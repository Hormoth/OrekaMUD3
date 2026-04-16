"""Captive rescue system.

A captive is an NPC placed in a hostile room.  When the player frees
the captive (defeats the captors in the room OR interacts with the
captive while no hostiles remain), the captive hands the player a
recognition-token and names a family.  Delivering the token to the
named family representative in a home-town room pays out.

This is the MVP: single captive type (token-bearer), single family
fate (honest pay).  The richer layers -- six captive types, six family
fates, reputation-patron intervention, reputation-gated quest reveal --
build on top of this by extending ``_on_token_delivered`` and
``_on_captive_rescued``.

Data lives in ``data/captives.json``.  Captive NPCs carry a
``captive_state`` attribute (string: "bound" / "freed" / "departed") and
a ``family_id`` attribute linking them to a family in that file.
"""

from __future__ import annotations

import json
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("OrekaMUD.Captives")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data",
                          "captives.json")


def _load_data() -> Dict[str, Any]:
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("captives.json load failed: %s", e)
        return {"families": {}, "templates": {}, "reward_pools": {}}


class CaptiveData:
    """Singleton holding the captive-system data loaded from disk."""

    def __init__(self):
        self._data = _load_data()

    @property
    def families(self) -> Dict[str, Dict[str, Any]]:
        return self._data.get("families", {})

    @property
    def templates(self) -> Dict[str, Dict[str, Any]]:
        return self._data.get("templates", {})

    @property
    def reward_pools(self) -> Dict[str, Dict[str, Any]]:
        return self._data.get("reward_pools", {})

    def reload(self) -> None:
        self._data = _load_data()

    def get_family(self, family_id: str) -> Optional[Dict[str, Any]]:
        return self.families.get(family_id)

    def get_family_for_region(self, region: str) -> List[Dict[str, Any]]:
        return [f for f in self.families.values()
                if f.get("region") == region]


_data: Optional[CaptiveData] = None


def get_data() -> CaptiveData:
    global _data
    if _data is None:
        _data = CaptiveData()
    return _data


# ---------------------------------------------------------------------------
# Token item vnum allocation
# ---------------------------------------------------------------------------
# Token items are generated on-the-fly, one per captive instance.  We
# allocate them from a reserved range (800-899) and store the token's
# family_id on the item so delivery can match.

_TOKEN_VNUM_BASE = 800
_next_token_vnum = _TOKEN_VNUM_BASE


def _allocate_token_vnum() -> int:
    global _next_token_vnum
    v = _next_token_vnum
    _next_token_vnum += 1
    if _next_token_vnum > 899:
        _next_token_vnum = _TOKEN_VNUM_BASE  # wrap; stale tokens overwritten
    return v


# Token flavor pool -- each captive generates a random physical token
_TOKEN_FLAVORS = [
    ("a silver signet ring", "A small silver ring bearing the family's crest."),
    ("a woven hair-band", "A braided hair-band of the family's signature colors."),
    ("a carved wooden charm", "A hand-carved wooden charm worn smooth from years of handling."),
    ("a clay seal-stone", "A small clay stone stamped with a family mark."),
    ("a bronze brooch", "A tarnished bronze brooch worked in the family's house-pattern."),
    ("a leather cord with a pendant", "A leather cord bearing a small pendant of personal meaning."),
    ("a folded scrap of embroidered cloth", "An embroidered scrap, clearly a piece cut from something larger."),
    ("a polished river stone", "A smooth stone whose shape a family would instantly recognize."),
]


# ---------------------------------------------------------------------------
# Captive creation
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Rescue types (Phase 2) -- each captive behaves differently when freed
# ---------------------------------------------------------------------------

# Valid rescue_type values and their weighted-random distribution when
# spawned procedurally (static exemplar captives get an explicit type).
RESCUE_TYPE_WEIGHTS = {
    "token_bearer": 35,   # default -- hands you a token, go home for pay
    "homesick":     20,   # no physical token, verbal/mental directions
    "quest_giver":  15,   # hands token + names a task to do first
    "self_rescue":  10,   # says thanks, walks off; reward deferred
    "leader":       10,   # VIP: triple gold + faction spike + unique drop
    "dinner":       10,   # variable: dying/plant/lost -- sometimes a trap
}


def _roll_rescue_type() -> str:
    import random as _r
    total = sum(RESCUE_TYPE_WEIGHTS.values())
    pick = _r.uniform(0, total)
    cum = 0
    for typ, w in RESCUE_TYPE_WEIGHTS.items():
        cum += w
        if pick <= cum:
            return typ
    return "token_bearer"


def make_captive(template_id: str, family_id: str, room_vnum: int,
                 captor_type: str = "unknown",
                 rescue_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Build a captive dict ready to be placed in a room.  Returns None
    if the template or family is invalid.

    The returned dict uses the same schema as other bestiary entries so
    it can drop cleanly into ``world.mobs`` and the room's mob list.
    """
    d = get_data()
    template = d.templates.get(template_id)
    family = d.get_family(family_id)
    if template is None or family is None:
        logger.warning("make_captive: missing template=%s or family=%s",
                       template_id, family_id)
        return None

    name_pool = template.get("name_pool", ["the captive"])
    hook_pool = template.get("hooks", ["abducted by unknown captors"])
    name = random.choice(name_pool).capitalize()
    hook = random.choice(hook_pool)
    desc = (template.get("description", "A bound captive.")
            + f" They were {hook}."
            + f" They mention the family name '{family.get('family_name')}' "
            + f"of {family.get('home_town')}.")

    # Captive mob stat-block (non-combatant; HP just to survive a few hits)
    vnum = _allocate_captive_vnum()
    rtype = rescue_type or _roll_rescue_type()
    captive = {
        "vnum":           vnum,
        "name":           name,
        "level":          1,
        "hp_dice":        [1, 8, 2],
        "ac":             10,
        "damage_dice":    [1, 3, 0],
        "flags":          ["captive", "nonaggressive", "quest_giver"],
        "type_":          "Humanoid",
        "alignment":      "Neutral Good",
        "ability_scores": {"Str": 9, "Dex": 10, "Con": 10,
                           "Int": 11, "Wis": 11, "Cha": 10},
        "initiative":     0,
        "speed":          {"land": 30},
        "attacks":        [],
        "special_attacks": [],
        "special_qualities": [],
        "feats":          [],
        "skills":         {},
        "saves":          {"Fort": 0, "Ref": 0, "Will": 1},
        "environment":    "Captive of " + captor_type,
        "organization":   "solitary captive",
        "cr":             None,
        "advancement":    "-",
        "description":    desc,
        "room_vnum":      room_vnum,
        "loot_table":     [],
        # Captive-specific state
        "captive_state":  "bound",
        "captive_template": template_id,
        "captive_family": family_id,
        "captive_captor_type": captor_type,
        "rescue_type":    rtype,
    }
    return captive


_CAPTIVE_VNUM_BASE = 800000
_next_captive_vnum = _CAPTIVE_VNUM_BASE


def _allocate_captive_vnum() -> int:
    global _next_captive_vnum
    v = _next_captive_vnum
    _next_captive_vnum += 1
    return v


# ---------------------------------------------------------------------------
# Rescue & token issuance
# ---------------------------------------------------------------------------

def is_captive(mob) -> bool:
    if mob is None:
        return False
    flags = {str(f).lower() for f in (getattr(mob, "flags", []) or [])}
    return "captive" in flags


def captors_still_present(room) -> bool:
    """Return True if the room still contains hostile mobs that are not
    themselves captives."""
    if room is None:
        return False
    for m in getattr(room, "mobs", []) or []:
        if is_captive(m):
            continue
        flags = {str(f).lower() for f in (getattr(m, "flags", []) or [])}
        if "hostile" in flags:
            return True
    return False


def on_captive_rescued(character, captive) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Called when a player frees a captive (captors have been cleared).
    Dispatches to a rescue-type-specific handler.

    Returns a (message, token_item_dict) tuple.  The caller should add
    the token to the character's inventory and narrate the message.
    token_item_dict may be None for types that don't issue physical
    tokens (homesick gives a "memory" token; self_rescue gives nothing
    immediately; dinner-plant actually starts combat).
    """
    state = getattr(captive, "captive_state", None)
    if state != "bound":
        return ("You find the captive, but they are no longer bound.", None)

    family_id = getattr(captive, "captive_family", None)
    d = get_data()
    family = d.get_family(family_id) if family_id else None
    if family is None:
        captive.captive_state = "freed"
        return ("You free the captive. They cannot say where they are "
                "from -- the abuse left them unable to name a place.",
                None)

    rtype = getattr(captive, "rescue_type", None) or "token_bearer"
    handler = _RESCUE_HANDLERS.get(rtype, _rescue_token_bearer)
    return handler(character, captive, family)


# --- rescue-type handlers --------------------------------------------------

def _make_token(family: Dict[str, Any], *, memory: bool = False,
                leader: bool = False, task: Optional[str] = None,
                rescue_type: str = "token_bearer") -> Dict[str, Any]:
    """Build a token item dict.  memory=True makes a verbal/mental token
    (no physical object).  leader=True flags the token for bonus payout.
    Also rolls a family_fate to embed on the token."""
    token_vnum = _allocate_token_vnum()
    if memory:
        flavor_name = f"the memory of {family['family_name']}"
        flavor_desc = ("You carry the memory of their home -- a place "
                       "you now know well enough to find.")
    else:
        flavor_name, flavor_desc = random.choice(_TOKEN_FLAVORS)
        flavor_name = f"{flavor_name} (token of {family['family_name']})"

    props = ["quest", "captive_token"]
    if memory:
        props.append("memory_token")
    if leader:
        props.append("leader_token")
    if task:
        props.append("task_token")

    # Roll the family fate that will play out at delivery time
    try:
        from src.family_fates import roll_family_fate
        family_fate = roll_family_fate(rescue_type)
    except Exception:
        family_fate = "honest_pay"

    token = {
        "vnum":          token_vnum,
        "name":          flavor_name,
        "item_type":     "gear" if not memory else "quest",
        "weight":        0.1 if not memory else 0,
        "value":         0,
        "description":   (f"{flavor_desc} Recognized by "
                          f"{family.get('representative_npc')} "
                          f"in {family.get('home_town')}."),
        "properties":    props,
        "captive_token": True,
        "family_id":     family["id"],
        "leader_bonus":  leader,
        "memory_only":   memory,
        "task_text":     task,
        "family_fate":   family_fate,
    }
    return token


def _rescue_token_bearer(character, captive, family) -> Tuple[str, Dict[str, Any]]:
    """Default MVP behavior: captive hands over a physical token + home directions."""
    token = _make_token(family, rescue_type="token_bearer")
    captive.captive_state = "freed"
    msg = (f"\033[1;33m{captive.name} presses {token['name']} into your hand.\033[0m\n"
           f"\033[0;37m\"Please... take this to \033[1;37m{family['representative_npc']}\033[0;37m\n"
           f"in \033[1;37m{family['home_town']}\033[0;37m. They'll know what it means.\"\033[0m")
    return msg, token


def _rescue_homesick(character, captive, family) -> Tuple[str, Dict[str, Any]]:
    """Captive has no physical item to give -- they share directions verbally.
    A memory-token is placed in inventory and `present` works on it the
    same as a physical token."""
    token = _make_token(family, memory=True, rescue_type="homesick")
    captive.captive_state = "freed"
    msg = (f"\033[0;37m{captive.name} grips your hand weakly, voice thin with exhaustion:\n"
           f"\"I have nothing to give you. But please -- find "
           f"\033[1;37m{family['representative_npc']}\033[0;37m in \033[1;37m"
           f"{family['home_town']}\033[0;37m. Tell them you met me. "
           f"Tell them I wanted to come home.\"\033[0m\n"
           f"\033[2;37m(You commit their family's name to memory.)\033[0m")
    return msg, token


def _rescue_quest_giver(character, captive, family) -> Tuple[str, Dict[str, Any]]:
    """Captive hands a token but asks you to complete a task first."""
    tasks = [
        "Before you go to my family -- find the bow I dropped when they took me. It should still be in this region somewhere.",
        "One of my fellow captives did not make it. Please carry word to their kin; I'll name them if you ask.",
        "My captors took something from me. If you find a marked pouch among their belongings, bring it to my family with this token.",
        "A companion of mine was separated from me when they took us. If you find them, guide them to my family too.",
    ]
    task = random.choice(tasks)
    token = _make_token(family, task=task, rescue_type="quest_giver")
    captive.captive_state = "freed"
    msg = (f"\033[1;33m{captive.name} presses {token['name']} into your hand.\033[0m\n"
           f"\033[0;37m\"Before you take this home -- {task}\n"
           f"My family is \033[1;37m{family['family_name']}\033[0;37m in "
           f"\033[1;37m{family['home_town']}\033[0;37m. Ask for "
           f"\033[1;37m{family['representative_npc']}\033[0;37m.\"\033[0m")
    return msg, token


def _rescue_self_rescue(character, captive, family) -> Tuple[str, None]:
    """Captive declines assistance and departs.  Family has a pending reward
    that triggers when the player next enters the family's home room."""
    # Record pending reward on character
    if not hasattr(character, "pending_rescue_rewards"):
        character.pending_rescue_rewards = []
    character.pending_rescue_rewards.append({
        "family_id":  family["id"],
        "rescued_at": time.time(),
    })
    captive.captive_state = "departed"
    msg = (f"\033[0;37m{captive.name} rubs their wrists where the bindings were, "
           f"then straightens.\n"
           f"\"Thank you. But I know my own way home -- and they'd worry if "
           f"I brought strangers. \033[1;37m{family['representative_npc']}\033[0;37m "
           f"will hear of this, and your name will be remembered in "
           f"\033[1;37m{family['home_town']}\033[0;37m.\"\n"
           f"They slip away into the shadows with surprising speed.\033[0m\n"
           f"\033[2;37m(A reward will be waiting for you next time you visit "
           f"{family['home_town']}.)\033[0m")
    return msg, None


def _rescue_leader(character, captive, family) -> Tuple[str, Dict[str, Any]]:
    """VIP rescue.  Bigger payout + faction rep + unique dialogue."""
    token = _make_token(family, leader=True, rescue_type="leader")
    captive.captive_state = "freed"
    msg = (f"\033[1;33m{captive.name} regards you with the calm, "
           f"measured attention of someone unused to being in your debt.\033[0m\n"
           f"\033[0;37m\"My life is worth something to people who matter. "
           f"Take this -- \033[1;37m{family['representative_npc']}\033[0;37m "
           f"of \033[1;37m{family['home_town']}\033[0;37m will understand "
           f"what it cost to lose me, and what it means to get me back.\"\033[0m\n"
           f"\033[2;37m(This captive seems unusually important.)\033[0m")
    return msg, token


def _rescue_dinner(character, captive, family) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Variable outcome: dying / plant / lost.

    dying: captive gives lore and dies; family can be told for sympathy reward.
    plant: captive turns hostile (infiltrator in disguise).
    lost : captive says thanks and wanders off.  No reward.
    """
    roll = random.random()
    if roll < 0.5:
        # Dying: captive dies after a brief speech. Character gets a
        # "memoriam" marker -- present to family for a small sympathy
        # payout (half-gold, no item).
        token = _make_token(family, memory=True)
        token["name"] = f"a lock of hair from {captive.name}"
        token["description"] = (f"Hair you kept after {captive.name} died "
                                f"in your arms. A token of remembrance to "
                                f"bring to {family.get('representative_npc')} "
                                f"in {family.get('home_town')}.")
        token["properties"].append("memoriam_token")
        token["leader_bonus"] = False
        # Remove captive from room
        captive.captive_state = "deceased"
        try:
            captive.hp = 0
            captive.alive = False
        except Exception:
            pass
        msg = (f"\033[0;37m{captive.name} sags against you as you cut "
               f"their bindings. They whisper:\n"
               f"\"Tell my family... tell \033[1;37m{family['representative_npc']}\033[0;37m... "
               f"I was thinking of them at the end...\"\n"
               f"They go still.\033[0m\n"
               f"\033[2;37m(You take a lock of their hair. Bring it to "
               f"{family['home_town']} if you have the time.)\033[0m")
        return msg, token
    elif roll < 0.8:
        # Plant: captive attacks or flees (for MVP, they flee)
        captive.captive_state = "fled"
        try:
            captive.flags = list(getattr(captive, "flags", []) or [])
            if "captive" in captive.flags:
                captive.flags.remove("captive")
            captive.flags.append("hostile")
        except Exception:
            pass
        msg = (f"\033[1;31mThe moment the bindings part, {captive.name}'s "
               f"face goes cold. They were never a captive at all.\033[0m\n"
               f"\033[0;33m\"A pity. You seemed competent.\"\033[0m\n"
               f"\033[0;37m{captive.name} vanishes into the shadows before "
               f"you can react.\033[0m\n"
               f"\033[2;37m(The captive was a plant -- a Dómnathar infiltrator "
               f"testing your identity. Watch yourself in this region.)\033[0m")
        return msg, None
    else:
        # Lost: captive thanks you and wanders away with no reward
        captive.captive_state = "departed"
        msg = (f"\033[0;37m{captive.name} blinks as if waking. They try "
               f"to speak, manage a weak laugh, then shrug helplessly.\n"
               f"\"I don't -- I don't know where I'm from. It's gone. "
               f"Thank you, stranger.\"\n"
               f"They walk off into the terrain, and do not look back.\033[0m\n"
               f"\033[2;37m(Not every rescue closes a story.)\033[0m")
        return msg, None


_RESCUE_HANDLERS = {
    "token_bearer": _rescue_token_bearer,
    "homesick":     _rescue_homesick,
    "quest_giver":  _rescue_quest_giver,
    "self_rescue":  _rescue_self_rescue,
    "leader":       _rescue_leader,
    "dinner":       _rescue_dinner,
}


# ---------------------------------------------------------------------------
# Token delivery
# ---------------------------------------------------------------------------

def is_captive_token(item) -> bool:
    if item is None:
        return False
    props = [str(p).lower() for p in (getattr(item, "properties", []) or [])]
    return "captive_token" in props or bool(getattr(item, "captive_token", False))


def _reward_item_for_level(family: Dict[str, Any], level: int) -> Optional[int]:
    """Pick a vnum from the family's reward pool appropriate to the PC's level."""
    pool_id = family.get("reward_item_pool") or "masterwork_mundane"
    d = get_data()
    pool = d.reward_pools.get(pool_id, {})
    if level <= 4:
        candidates = pool.get("levels_1_4", [])
    elif level <= 8:
        candidates = pool.get("levels_5_8", [])
    elif level <= 14:
        candidates = pool.get("levels_9_14", [])
    else:
        candidates = pool.get("levels_15_plus", [])
    if not candidates:
        return None
    return random.choice(candidates)


def on_token_delivered(character, token_item, npc) -> Optional[str]:
    """Called when a character presents a captive-token to a family NPC.

    Returns a payout narrative message, or None if the token isn't
    recognized by this NPC.  Scales payout by token properties:
        - leader_bonus = x3 gold, bonus item, +50 rep spike
        - memoriam     = half gold, no item, sympathy narrative
        - task_token   = normal + "the family mentions your task" beat
    """
    if not is_captive_token(token_item):
        return None
    family_id = getattr(token_item, "family_id", None)
    if family_id is None:
        return None
    d = get_data()
    family = d.get_family(family_id)
    if family is None:
        return None

    # Does this NPC represent the family?
    npc_name = getattr(npc, "name", "")
    rep_name = family.get("representative_npc", "")
    if rep_name and rep_name.lower() not in npc_name.lower() \
       and npc_name.lower() not in rep_name.lower():
        return None  # silent no-op so players can try elsewhere

    # Check if this token has a family fate that overrides the normal
    # payout (burnt_trail, quiet_tragedy, etc.).  First delivery only --
    # prior rescues skip the fate check so players don't get ambushed
    # repeatedly when they bring back multiple captives from the same family.
    if not hasattr(character, "rescued_captives"):
        character.rescued_captives = []
    _prior = sum(1 for r in character.rescued_captives
                 if r.get("family_id") == family_id)
    if _prior == 0:
        try:
            from src.family_fates import get_fate_manager
            fate_mgr = get_fate_manager()
            room = getattr(character, "room", None)
            fate_msg = fate_mgr.on_delivery_attempt(character, token_item,
                                                     npc, room, family)
            if fate_msg is not None:
                # Consume the token (caller handles inventory removal)
                return fate_msg
        except Exception as e:
            logger.debug("fate manager delivery check failed: %s", e)

    # Detect token flavor
    props = [str(p).lower() for p in (getattr(token_item, "properties", []) or [])]
    is_leader = bool(getattr(token_item, "leader_bonus", False)) or "leader_token" in props
    is_memoriam = "memoriam_token" in props
    is_task = "task_token" in props
    is_memory = "memory_token" in props and not is_memoriam

    # Apply diminishing returns: second+ delivery from same family pays half
    if not hasattr(character, "rescued_captives"):
        character.rescued_captives = []
    prior = sum(1 for r in character.rescued_captives
                if r.get("family_id") == family_id)
    multiplier = 1.0 if prior == 0 else 0.5

    # Gold payout, with type modifiers
    low, high = family.get("reward_gold_range", [20, 60])
    gold = random.randint(low, high) * multiplier
    if is_leader:
        gold *= 3
    elif is_memoriam:
        gold *= 0.5
    gold = int(gold)
    character.gold = getattr(character, "gold", 0) + gold

    # Item payout -- first rescue only, and not on memoriam tokens
    item_msg = ""
    if prior == 0 and not is_memoriam:
        # Leader tokens get bumped one tier higher
        effective_level = getattr(character, "level", 1)
        if is_leader:
            effective_level = min(20, effective_level + 4)
        item_vnum = _reward_item_for_level(family, effective_level)
        if item_vnum is not None:
            item_msg = _grant_item(character, item_vnum)

    # Faction rep bonus (leader = +50, memoriam = +5, normal = +20)
    faction_bonus_msg = ""
    fid = family.get("faction_id")
    if fid:
        try:
            from src.factions import get_faction_manager
            fm = get_faction_manager()
            if is_leader:
                rep_gain = 50
            elif is_memoriam:
                rep_gain = 5 if prior == 0 else 2
            else:
                rep_gain = 20 if prior == 0 else 5
            reason = (f"rescued a leader and returned them to {family['family_name']}"
                      if is_leader else
                      f"brought news of a lost kin to {family['family_name']}"
                      if is_memoriam else
                      f"returned a captive to {family['family_name']}")
            result = fm.modify_reputation(character, fid, rep_gain,
                                          reason=reason)
            if isinstance(result, tuple) and result:
                faction_bonus_msg = "\n" + str(result[-1])
        except Exception as e:
            logger.debug("Faction bonus failed: %s", e)

    # Track the rescue on the character's permanent record
    character.rescued_captives.append({
        "family_id": family_id,
        "family_name": family.get("family_name"),
        "gold": gold,
        "type": ("leader" if is_leader else
                 "memoriam" if is_memoriam else
                 "memory" if is_memory else
                 "task" if is_task else "standard"),
        "timestamp": time.time(),
    })

    # Narrate by type
    lines: List[str] = []
    if is_memoriam:
        lines += [
            f"\033[1;36m{npc_name} takes the lock of hair and closes "
            f"their eyes for a long moment.\033[0m",
            f"\033[0;37m\"You stayed with them. We won't forget that.\"\033[0m",
            f"\033[1;33m{npc_name} presses {gold} gold into your palm "
            f"and speaks a small blessing over you.\033[0m",
        ]
    elif is_leader:
        lines += [
            f"\033[1;36m{npc_name}'s face goes white, then -- relief -- "
            f"then a fierce, practical joy.\033[0m",
            f"\033[0;37m\"You have no idea what you have done for us. "
            f"No idea.\"\033[0m",
            f"\033[1;33m{npc_name} presses {gold} gold into your palm "
            f"and commits to further services your way.\033[0m",
        ]
    elif is_memory:
        lines += [
            f"\033[1;36m{npc_name} listens carefully, then breaks into a "
            f"slow, unguarded smile.\033[0m",
            f"\033[0;37m\"You've seen them. You carry their face. Thank "
            f"you for bringing us news.\"\033[0m",
            f"\033[1;33m{npc_name} presses {gold} gold into your palm.\033[0m",
        ]
    else:
        lines += [
            f"\033[1;36m{npc_name} takes the token in both hands and their "
            f"breath catches.\033[0m",
            f"\033[0;37m\"You brought them home. We owe you more than coin.\"\033[0m",
            f"\033[1;33m{npc_name} presses {gold} gold into your palm.\033[0m",
        ]

    if item_msg:
        lines.append(item_msg)

    if is_task:
        task_text = getattr(token_item, "task_text", None)
        if task_text:
            lines.append(f"\033[2;37m{npc_name} nods. \"We'll look into "
                         f"the matter they asked of you.\"\033[0m")

    if faction_bonus_msg:
        lines.append(faction_bonus_msg)

    if prior > 0:
        lines.append(f"\033[2;37m(You have now returned {prior + 1} captives "
                     f"to {family['family_name']}.)\033[0m")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-rescue deferred reward hook
# ---------------------------------------------------------------------------

def check_pending_rewards(character, npc) -> Optional[str]:
    """Called when a character interacts with (or enters a room with) a
    family NPC.  If the character has any pending self-rescue rewards
    for that NPC's family, pays them out and clears the pending entry.
    """
    pending = getattr(character, "pending_rescue_rewards", None)
    if not pending:
        return None

    d = get_data()
    npc_name = getattr(npc, "name", "")

    # Find a matching pending reward
    matched = None
    for idx, entry in enumerate(pending):
        family = d.get_family(entry.get("family_id"))
        if family is None:
            continue
        rep = family.get("representative_npc", "")
        if rep and (rep.lower() in npc_name.lower()
                    or npc_name.lower() in rep.lower()):
            matched = (idx, entry, family)
            break
    if matched is None:
        return None

    idx, entry, family = matched

    # Standard payout (first-time for this family)
    if not hasattr(character, "rescued_captives"):
        character.rescued_captives = []
    prior = sum(1 for r in character.rescued_captives
                if r.get("family_id") == family["id"])
    multiplier = 1.0 if prior == 0 else 0.5
    low, high = family.get("reward_gold_range", [20, 60])
    gold = int(random.randint(low, high) * multiplier)
    character.gold = getattr(character, "gold", 0) + gold

    item_msg = ""
    if prior == 0:
        item_vnum = _reward_item_for_level(family, getattr(character, "level", 1))
        if item_vnum is not None:
            item_msg = _grant_item(character, item_vnum)

    # Faction rep
    faction_msg = ""
    fid = family.get("faction_id")
    if fid:
        try:
            from src.factions import get_faction_manager
            fm = get_faction_manager()
            rep_gain = 20 if prior == 0 else 5
            result = fm.modify_reputation(character, fid, rep_gain,
                                          reason=f"the self-freed one reached {family['family_name']}")
            if isinstance(result, tuple) and result:
                faction_msg = "\n" + str(result[-1])
        except Exception as e:
            logger.debug("Pending-reward faction bonus failed: %s", e)

    # Pop the pending entry and record the rescue
    pending.pop(idx)
    character.rescued_captives.append({
        "family_id": family["id"],
        "family_name": family.get("family_name"),
        "gold": gold,
        "type": "self_rescue",
        "timestamp": time.time(),
    })

    lines = [
        f"\033[1;36m{npc_name} sees you enter and immediately stands.\033[0m",
        f"\033[0;37m\"You're the one. They got home two days ago and told "
        f"us everything. We've been watching the road for you.\"\033[0m",
        f"\033[1;33m{npc_name} presses {gold} gold into your palm.\033[0m",
    ]
    if item_msg:
        lines.append(item_msg)
    if faction_msg:
        lines.append(faction_msg)
    return "\n".join(lines)


def _grant_item(character, item_vnum: int) -> str:
    """Add an item to the character's inventory and narrate."""
    try:
        from src.items import get_item_manager
        im = get_item_manager()
        item = im.create_item(item_vnum)
    except Exception:
        item = None

    if item is None:
        # Fallback: read items.json directly
        try:
            import json as _j
            with open(os.path.join(os.path.dirname(__file__), "..",
                                    "data", "items.json"),
                      "r", encoding="utf-8") as f:
                items = _j.load(f)
            it_data = next((i for i in items if i.get("vnum") == item_vnum), None)
            if it_data is None:
                return ""
            from src.items import Item
            item = Item(**{k: v for k, v in it_data.items()
                          if k in ("vnum", "name", "item_type", "weight",
                                    "value", "description")})
        except Exception:
            return ""

    if not hasattr(character, "inventory"):
        character.inventory = []
    character.inventory.append(item)
    return (f"\033[1;32m{npc_name_from(character, item)}"
            f"{item.name}\033[0m has been added to your pack.")


def npc_name_from(character, item):
    # Stub for prose embedding if needed later
    return ""


# ---------------------------------------------------------------------------
# Admin / test helpers
# ---------------------------------------------------------------------------

def spawn_captive_in_room(world, room_vnum: int,
                          template_id: str = "scout",
                          family_id: Optional[str] = None,
                          captor_type: str = "testing",
                          rescue_type: Optional[str] = None) -> Tuple[bool, str]:
    """Admin utility: place a captive in a specific room."""
    room = world.rooms.get(room_vnum)
    if room is None:
        return False, f"Room {room_vnum} not found."

    d = get_data()
    if family_id is None:
        if not d.families:
            return False, "No families configured."
        family_id = random.choice(list(d.families.keys()))

    captive_data = make_captive(template_id, family_id, room_vnum,
                                 captor_type, rescue_type=rescue_type)
    if captive_data is None:
        return False, "Could not build captive (bad template or family?)."

    # Instantiate as a Mob
    try:
        from src.mob import Mob
    except Exception as e:
        return False, f"Mob import failed: {e}"

    mob_kwargs = {k: v for k, v in captive_data.items()
                  if k in ("vnum", "name", "level", "hp_dice", "ac",
                           "damage_dice", "flags", "type_", "alignment",
                           "environment", "organization", "cr",
                           "advancement", "description")}
    mob = Mob(**mob_kwargs)
    mob.room_vnum = room_vnum
    mob.alive = True
    # Attach captive-specific fields
    for k in ("captive_state", "captive_template",
              "captive_family", "captive_captor_type", "rescue_type"):
        setattr(mob, k, captive_data.get(k))
    # Ability scores + speed
    for k in ("ability_scores", "speed", "attacks",
              "special_attacks", "special_qualities",
              "feats", "skills", "saves"):
        if captive_data.get(k) is not None and not getattr(mob, k, None):
            try:
                setattr(mob, k, captive_data[k])
            except Exception:
                pass

    world.mobs[mob.vnum] = mob
    room.mobs.append(mob)
    return True, (f"Captive '{mob.name}' placed in room {room_vnum} "
                  f"(family={family_id}, template={template_id}, vnum={mob.vnum}).")


def apply_captive_state_on_load(world) -> int:
    """Walk every mob in the world and ensure any captive-flagged mob has
    its captive_state initialized to 'bound' if not already set.

    Called once after ``world.load_data()`` so static captives authored
    in mobs.json come online in the correct state.
    """
    fixed = 0
    for v, mob in getattr(world, "mobs", {}).items():
        if not is_captive(mob):
            continue
        if getattr(mob, "captive_family", None) is None:
            continue
        if getattr(mob, "captive_state", None) in (None, ""):
            mob.captive_state = "bound"
            fixed += 1
    if fixed:
        logger.info("Captives: initialized %d captive(s) to 'bound' state",
                    fixed)
    return fixed


def rescue_check(character, room) -> List[Tuple[Any, str, Dict[str, Any]]]:
    """Call every tick (or on any room interaction) to check if bound
    captives in ``room`` can now be freed because all hostiles are gone.

    Returns a list of (captive_mob, message, token_item_dict) for any
    captives just freed.  Caller is responsible for adding the tokens
    to inventory and narrating.
    """
    results: List[Tuple[Any, str, Dict[str, Any]]] = []
    if room is None or captors_still_present(room):
        return results

    for m in list(getattr(room, "mobs", []) or []):
        if not is_captive(m):
            continue
        if getattr(m, "captive_state", None) != "bound":
            continue
        msg, token = on_captive_rescued(character, m)
        if token is not None:
            results.append((m, msg, token))
        else:
            results.append((m, msg, {}))
    return results
