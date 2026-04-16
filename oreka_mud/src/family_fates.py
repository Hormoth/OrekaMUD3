"""Family fate variants for captive-token deliveries.

Every rescued captive gets a family_fate rolled at rescue time.  When
the player eventually presents the token to the family NPC, the fate
determines what happens:

    honest_pay    -- default; standard payout from on_token_delivered
    burnt_trail   -- family home is burnt; hidden message warns of
                     ambush; 2-minute escape window or 3 waves spawn
    quiet_tragedy -- family is dead when you arrive; grief beat only

The fate roll happens once per rescue (stored on the token's
``family_fate`` attribute) so the same token always produces the same
experience when delivered.  First-time-delivery-per-family only --
subsequent deliveries always use honest_pay.

This module runs its own lightweight tick loop to manage burnt-trail
timers and wave spawning.  See ``tick_fate_manager(world)`` below.
"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("OrekaMUD.Fates")


# ---------------------------------------------------------------------------
# Fate rolling
# ---------------------------------------------------------------------------

# Probability weights for each fate.  Tokens from leader rescues skew
# toward honest_pay (VIPs travel with escorts); token_bearer/homesick
# use the standard distribution.
FATE_WEIGHTS = {
    "honest_pay":    60,
    "burnt_trail":   20,
    "quiet_tragedy": 20,
}


def roll_family_fate(rescue_type: str = "token_bearer") -> str:
    """Pick a fate for a newly-minted token.  Returns a fate name."""
    weights = dict(FATE_WEIGHTS)
    if rescue_type == "leader":
        # Leaders almost always pay out cleanly (someone was watching out
        # for their family too)
        weights = {"honest_pay": 85, "burnt_trail": 10, "quiet_tragedy": 5}
    elif rescue_type == "dinner":
        # Dinner-type captives never reach token delivery, but if they
        # did, skew toward tragedy
        weights = {"honest_pay": 20, "burnt_trail": 30, "quiet_tragedy": 50}

    total = sum(weights.values())
    pick = random.uniform(0, total)
    cum = 0
    for fate, w in weights.items():
        cum += w
        if pick <= cum:
            return fate
    return "honest_pay"


# ---------------------------------------------------------------------------
# Trail state (for burnt_trail fate)
# ---------------------------------------------------------------------------

BURNT_TRAIL_GRACE_SECONDS = 120   # player has 2 minutes to leave town
BURNT_TRAIL_WAVE_GAP_SECONDS = 30  # between waves
BURNT_TRAIL_WAVES = 3


@dataclass
class TrailState:
    """Live state for an active burnt-trail scene."""
    character_name: str
    family_id: str
    home_vnum: int
    started_at: float
    examined_hint: bool = False
    warned_player: bool = False
    waves_spawned: int = 0
    last_wave_time: float = 0.0
    wave_mobs: List[Any] = field(default_factory=list)
    resolved: bool = False  # True if player escaped OR survived all waves


# ---------------------------------------------------------------------------
# The manager
# ---------------------------------------------------------------------------

class FamilyFateManager:
    def __init__(self):
        # Keyed by (character_name, family_id) so a single character can
        # have multiple simultaneous trails (one per family visited).
        self.active_trails: Dict[Tuple[str, str], TrailState] = {}
        # Home-room override text keyed by room_vnum when a trail is live
        self.room_overrides: Dict[int, Dict[str, Any]] = {}

    # -- Delivery-time dispatch ------------------------------------------

    def on_delivery_attempt(self, character, token, npc, room, family) -> Optional[str]:
        """Called from ``captives.on_token_delivered`` BEFORE the normal
        payout logic runs.  Returns a message to replace the payout, or
        None to fall through to honest_pay.
        """
        fate = getattr(token, "family_fate", None) or "honest_pay"
        handler = _FATE_HANDLERS.get(fate)
        if handler is None:
            return None  # honest_pay (or unknown) -> fall through
        try:
            return handler(self, character, token, npc, room, family)
        except Exception as e:
            logger.exception("fate handler %s failed: %s", fate, e)
            return None  # graceful fallback to honest_pay

    # -- Tick -----------------------------------------------------------

    def tick(self, world) -> List[str]:
        """Periodic tick -- advances any active burnt-trail scenes.
        Called from main.py's async loop every ~30 seconds.
        """
        messages: List[str] = []
        now = time.time()
        completed: List[Tuple[str, str]] = []

        for key, trail in list(self.active_trails.items()):
            if trail.resolved:
                completed.append(key)
                continue

            # Find the character
            character = self._find_character(world, trail.character_name)
            if character is None:
                completed.append(key)
                continue

            # Has the player left the home room area?
            cur_room = getattr(character, "room", None)
            cur_vnum = getattr(cur_room, "vnum", None) if cur_room else None
            home = world.rooms.get(trail.home_vnum)
            same_area = self._rooms_in_same_area(world, cur_vnum,
                                                 trail.home_vnum)

            elapsed = now - trail.started_at

            # Escape condition: left the home town/area during the grace window
            if elapsed <= BURNT_TRAIL_GRACE_SECONDS and not same_area:
                trail.resolved = True
                completed.append(key)
                try:
                    from src.chat import send_to_player
                    send_to_player(character,
                        "\033[1;32mYou put distance between yourself and the "
                        "burnt house. The sense of being watched fades.\033[0m\n"
                        "\033[2;37m(You survived the Burnt Trail. The family's "
                        "representatives will seek you out later with word "
                        "of what really happened.)\033[0m")
                    # Schedule a deferred "survivor" reward on next home visit
                    if not hasattr(character, "pending_rescue_rewards"):
                        character.pending_rescue_rewards = []
                    character.pending_rescue_rewards.append({
                        "family_id":    trail.family_id,
                        "rescued_at":   now,
                        "survivor":     True,
                    })
                except Exception:
                    pass
                continue

            # Grace period expired -- time to spawn waves
            if elapsed > BURNT_TRAIL_GRACE_SECONDS:
                if trail.waves_spawned < BURNT_TRAIL_WAVES:
                    # Check if previous wave is cleared
                    prev_wave_alive = any(
                        getattr(m, "alive", True)
                        and getattr(m, "hp", 0) > 0
                        for m in trail.wave_mobs
                    )
                    if prev_wave_alive and trail.waves_spawned > 0:
                        continue  # wait for player to clear before next wave
                    if now - trail.last_wave_time < BURNT_TRAIL_WAVE_GAP_SECONDS \
                       and trail.waves_spawned > 0:
                        continue
                    # Spawn the next wave in the home room
                    self._spawn_ambush_wave(world, trail)
                    trail.waves_spawned += 1
                    trail.last_wave_time = now
                    messages.append(
                        f"[Burnt Trail] Wave {trail.waves_spawned}/"
                        f"{BURNT_TRAIL_WAVES} arrives in room {trail.home_vnum} "
                        f"for {trail.character_name}")
                elif not any(getattr(m, "alive", True) and getattr(m, "hp", 0) > 0
                              for m in trail.wave_mobs):
                    # All 3 waves cleared
                    trail.resolved = True
                    completed.append(key)
                    try:
                        from src.chat import send_to_player
                        send_to_player(character,
                            "\033[1;33mYou stand over the last of the "
                            "ambushers. The burnt ruin is quiet at last.\033[0m\n"
                            "\033[2;37m(Survived the Burnt Trail. The family's "
                            "true fate -- and who struck them -- is a story "
                            "worth seeking out.)\033[0m")
                        # Heavy faction rep for surviving + modest gold
                        self._grant_burnt_survivor_reward(character,
                                                           trail.family_id)
                    except Exception as e:
                        logger.debug("burnt survivor reward failed: %s", e)

        for key in completed:
            self.active_trails.pop(key, None)
        return messages

    # -- Helpers --------------------------------------------------------

    def _find_character(self, world, name):
        for p in getattr(world, "players", []) or []:
            if getattr(p, "name", None) == name:
                return p
        return None

    def _rooms_in_same_area(self, world, a_vnum, b_vnum) -> bool:
        if a_vnum is None or b_vnum is None:
            return False
        # Rough heuristic: "same area" = vnum within 100 of home
        return abs(int(a_vnum) - int(b_vnum)) <= 100

    def _spawn_ambush_wave(self, world, trail: TrailState) -> None:
        """Spawn 2-3 hostile mobs in the home room as the next wave.

        Before spawning, checks for patron-faction intervention -- a
        player with enough rep in the region can have a faction patrol
        disrupt the ambush wave entirely.  Only the FIRST wave gets the
        patronage check; once combat is active, the waves keep coming.
        """
        room = world.rooms.get(trail.home_vnum)
        if room is None:
            return
        try:
            from src.encounters import get_encounter_manager, _instantiate_mob
            mgr = get_encounter_manager()
            character = self._find_character(world, trail.character_name)
            apl = int(getattr(character, "level", 5)) if character else 5
            # Pick creatures appropriate to the region of this family
            from src.captives import get_data
            family = get_data().get_family(trail.family_id)
            region = family.get("region", "twinrivers") if family else "twinrivers"

            # Patron intervention check (only on wave 1)
            if trail.waves_spawned == 0 and character is not None:
                try:
                    from src.patronage import (check_intervention,
                                                on_intervention_used)
                    intervention = check_intervention(character, region)
                except Exception:
                    intervention = None
                if intervention is not None and intervention.cancels_encounter:
                    # Patron cuts the ambush off before it starts
                    try:
                        from src.chat import send_to_player
                        send_to_player(character, intervention.player_message)
                        on_intervention_used(character, intervention)
                    except Exception:
                        pass
                    # Mark trail as resolved favorably + grant survivor reward
                    trail.resolved = True
                    try:
                        self._grant_burnt_survivor_reward(character,
                                                           trail.family_id)
                    except Exception:
                        pass
                    return

            wave_size = random.choice([2, 3])
            for _ in range(wave_size):
                creature = mgr.pick_creature(region, apl)
                if creature is None:
                    continue
                mob = _instantiate_mob(creature, trail.home_vnum)
                world.mobs[mob.vnum] = mob
                room.mobs.append(mob)
                trail.wave_mobs.append(mob)
            # Notify the character
            if character is not None:
                try:
                    from src.chat import send_to_player
                    send_to_player(character,
                        f"\033[1;31mWave {trail.waves_spawned + 1} falls on "
                        f"you -- {wave_size} figures step in through the "
                        f"broken doorway, blades drawn.\033[0m")
                except Exception:
                    pass
        except Exception as e:
            logger.exception("wave spawn failed: %s", e)

    def _grant_burnt_survivor_reward(self, character, family_id):
        """After surviving all 3 waves, grant a modest survivor reward."""
        from src.captives import get_data, _reward_item_for_level, _grant_item
        family = get_data().get_family(family_id)
        if family is None:
            return
        low, high = family.get("reward_gold_range", [20, 60])
        gold = random.randint(low * 2, high * 2)
        character.gold = getattr(character, "gold", 0) + gold
        # Bump faction rep substantially
        fid = family.get("faction_id")
        if fid:
            try:
                from src.factions import get_faction_manager
                fm = get_faction_manager()
                fm.modify_reputation(character, fid, 40,
                                     reason=f"survived an ambush meant for "
                                            f"{family['family_name']}")
            except Exception:
                pass
        # Bonus item
        try:
            item_vnum = _reward_item_for_level(family,
                                                min(20, getattr(character, "level", 5) + 3))
            if item_vnum is not None:
                _grant_item(character, item_vnum)
        except Exception:
            pass
        try:
            from src.chat import send_to_player
            send_to_player(character,
                f"\033[1;33m{gold} gold from the corpses. "
                f"Bloody work done.\033[0m")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Fate handlers
# ---------------------------------------------------------------------------

def _fate_burnt_trail(mgr: FamilyFateManager, character, token, npc,
                      room, family) -> str:
    """The Burnt Trail: family home is a ruin; hidden message warns; timer starts."""
    home_vnum = family.get("home_room_vnum")
    key = (getattr(character, "name", "?"), family["id"])
    if key in mgr.active_trails:
        # Player already has this trail active; re-presenting token does nothing
        return ("\033[2;37mThe house is silent. Your token goes unacknowledged.\033[0m")

    # Remove the "NPC is here" illusion for this scene: the family NPC
    # is narratively absent.  We don't actually remove the mob from the
    # room (other players might be using it); we just override the
    # narration for this character.
    trail = TrailState(
        character_name=getattr(character, "name", "?"),
        family_id=family["id"],
        home_vnum=home_vnum,
        started_at=time.time(),
    )
    mgr.active_trails[key] = trail

    # Register the hidden-content cue on the room for the `examine` command
    mgr.room_overrides.setdefault(home_vnum, {})["burnt_hint"] = {
        "object": random.choice(["loose floorboard", "cracked vase",
                                  "pried-open panel", "discolored hearth-stone"]),
        "character_name": getattr(character, "name", "?"),
        "family_id": family["id"],
    }

    # Narrative beat
    fam_name = family.get("family_name", "the family")
    town = family.get("home_town", "the town")
    return (
        f"\033[1;31mThe door to the family home is charred half-off its hinges.\033[0m\n"
        f"\033[0;37mInside, {fam_name}'s hearth-room is a ruin -- soot on the walls, "
        f"the long-table burnt through at one end, the wooden floor scorched in the "
        f"unmistakable overlapping patterns of Dómnathar sorcery.\n"
        f"\n"
        f"No one is here. No bodies, either. Whoever lived here is either fled or taken.\n"
        f"\n"
        f"Your token feels suddenly heavy in your hand.\033[0m\n"
        f"\033[2;37m(Something in this room wants to be found. Try 'examine' on likely "
        f"features. You have about two minutes before whoever did this comes back.)\033[0m"
    )


def _fate_quiet_tragedy(mgr: FamilyFateManager, character, token, npc,
                        room, family) -> str:
    """Family is dead when you arrive.  No combat, just grief + small
    sympathy reward."""
    # Apply small sympathy reward (half gold, no item)
    low, high = family.get("reward_gold_range", [20, 60])
    gold = int(random.randint(low, high) * 0.5)
    character.gold = getattr(character, "gold", 0) + gold

    # Record the rescue
    if not hasattr(character, "rescued_captives"):
        character.rescued_captives = []
    character.rescued_captives.append({
        "family_id":   family["id"],
        "family_name": family.get("family_name"),
        "gold":        gold,
        "type":        "quiet_tragedy",
        "timestamp":   time.time(),
    })

    # Modest faction rep
    fid = family.get("faction_id")
    fac_msg = ""
    if fid:
        try:
            from src.factions import get_faction_manager
            fm = get_faction_manager()
            result = fm.modify_reputation(character, fid, 10,
                                          reason=f"brought grief's news to {family['family_name']}")
            if isinstance(result, tuple) and result:
                fac_msg = "\n" + str(result[-1])
        except Exception:
            pass

    fam_name = family.get("family_name", "the family")
    town = family.get("home_town", "the town")
    rep_name = family.get("representative_npc", "a neighbor")
    return (
        f"\033[1;31mYou find the house dark and the door unbarred.\033[0m\n"
        f"\033[0;37mInside, the hearth is cold. {rep_name} sits at the table "
        f"with hands folded, eyes red. They look up as you enter. They do "
        f"not rise.\n"
        f"\n"
        f"\"You brought news of one lost. I have to give you news back.\"\n"
        f"\n"
        f"{rep_name} pauses. \"They caught {fam_name} three nights ago. "
        f"The ones who took your captive -- they came for everyone else "
        f"too. Only I was out.\"\033[0m\n"
        f"\033[1;33m{rep_name} presses {gold} gold into your palm -- all "
        f"they have left.\033[0m\n"
        f"\033[2;37m\"Thank you for bringing news. At the end, they'd have "
        f"wanted to know someone was trying.\"\033[0m"
        + fac_msg
    )


_FATE_HANDLERS = {
    "burnt_trail":   _fate_burnt_trail,
    "quiet_tragedy": _fate_quiet_tragedy,
    # honest_pay is intentionally not registered -- it falls through
}


# ---------------------------------------------------------------------------
# Examine command support
# ---------------------------------------------------------------------------

def reveal_hidden_content(character, room) -> Optional[str]:
    """Called by the ``examine`` command.  If the character has an
    active burnt-trail in this room, reveal the hidden message.
    Returns the reveal message, or None if no hidden content here.
    """
    mgr = get_fate_manager()
    room_vnum = getattr(room, "vnum", None)
    if room_vnum is None:
        return None
    overrides = mgr.room_overrides.get(room_vnum, {})
    hint = overrides.get("burnt_hint")
    if hint is None:
        return None
    if hint.get("character_name") != getattr(character, "name", "?"):
        return None  # another player's trail

    family_id = hint.get("family_id")
    key = (character.name, family_id)
    trail = mgr.active_trails.get(key)
    if trail is None or trail.resolved:
        return None
    trail.examined_hint = True
    trail.warned_player = True

    obj = hint.get("object", "loose floorboard")
    fam_name = "your captive's family"
    try:
        from src.captives import get_data
        fam = get_data().get_family(family_id)
        if fam:
            fam_name = fam.get("family_name", fam_name)
    except Exception:
        pass

    return (
        f"\033[1;33mYou pry open the {obj}. Inside, wrapped in oilcloth, is a "
        f"folded scrap of parchment.\033[0m\n"
        f"\033[0;37mThe writing is hurried, the ink smudged:\n"
        f"\n"
        f"\"If you come, don't stop. Leave town by sundown. Trust no one "
        f"here who says they are {fam_name}. They've watched this house "
        f"since the burning -- they will be back tonight.\"\n"
        f"\n"
        f"The ink is still damp.\033[0m\n"
        f"\033[1;31m(Get out of town. Now.)\033[0m"
    )


# ---------------------------------------------------------------------------
# Singleton accessor + tick coroutine
# ---------------------------------------------------------------------------

_mgr: Optional[FamilyFateManager] = None


def get_fate_manager() -> FamilyFateManager:
    global _mgr
    if _mgr is None:
        _mgr = FamilyFateManager()
    return _mgr


async def family_fate_tick(world):
    """Background tick to advance burnt-trail timers/waves."""
    import asyncio
    mgr = get_fate_manager()
    while True:
        try:
            await asyncio.sleep(15)
            messages = mgr.tick(world)
            for m in messages:
                logger.info("Fates: %s", m)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("family_fate_tick error: %s", e)
