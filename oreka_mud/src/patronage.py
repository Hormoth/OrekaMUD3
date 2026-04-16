"""Reputation-patron intervention system.

Binds the faction sheet (faction_rep.py) to emergent gameplay outcomes
in encounters and ambushes.

When a player walks into a region, their reputation with that region's
patron factions changes what happens when trouble tries to find them.

    Hated          encounter chance 2.0x, dedicated hunters spawn
    Hostile        encounter chance 1.5x
    Unfriendly     encounter chance 1.25x
    Neutral        normal
    Friendly       15% chance a witness disrupts the encounter
    Honored        35% chance a patrol intervenes (encounter cancelled)
    Allied         60% chance of recognition let-go + 25% reverse ambush
    Revered        85% chance of passive avoidance (encounter skipped)

The module exposes two entry points:

    check_encounter_chance_multiplier(character, region) -> float
        Called by encounters.maybe_roll to scale the roll chance.

    check_intervention(character, region) -> Optional[Intervention]
        Called by encounters._spawn_for_party and by
        family_fates._spawn_ambush_wave *before* spawning threats.
        If it returns an Intervention, the caller cancels the threat
        and shows the intervention narrative to the player instead.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("OrekaMUD.Patronage")


# ---------------------------------------------------------------------------
# Region -> patron factions
# ---------------------------------------------------------------------------

REGION_PATRONS: Dict[str, List[str]] = {
    "eternalsteppe":  ["far_riders", "brotherhood_of_steppe"],
    "kinsweave":      ["brotherhood_of_steppe", "trade_houses"],
    "infinitedesert": ["sand_wardens"],
    "gatefall":       ["gatefall_remnant", "trade_houses"],
    "deepwater":      ["circle_of_deeproot"],
    "tidebloom":      ["circle_of_deeproot"],
    "twinrivers":     ["trade_houses"],
}


# Standing thresholds -- mirror faction_rep.STANDING_THRESHOLDS but
# collapsed to the labels we care about here.
def _standing_for(rep: int) -> str:
    if rep < -500:   return "hated"
    if rep < -100:   return "hostile"
    if rep < 0:      return "unfriendly"
    if rep < 100:    return "neutral"
    if rep < 300:    return "friendly"
    if rep < 600:    return "honored"
    if rep < 1000:   return "allied"
    return "revered"


# Intervention roll table -- (standing, intervention_type, chance).
# Tried in order; first successful roll wins.
INTERVENTION_TABLE = {
    "friendly":  [("witness", 0.15)],
    "honored":   [("patrol", 0.35), ("witness", 0.25)],
    "allied":    [("reverse_ambush", 0.25), ("recognition", 0.40),
                   ("patrol", 0.30), ("witness", 0.20)],
    "revered":   [("avoidance", 0.85), ("recognition", 0.50),
                   ("reverse_ambush", 0.30)],
}


# Chance multipliers for negative rep (applied per-encounter-roll)
NEGATIVE_REP_MULTIPLIERS = {
    "unfriendly": 1.25,
    "hostile":    1.5,
    "hated":      2.0,
}


# ---------------------------------------------------------------------------
# Intervention result
# ---------------------------------------------------------------------------

@dataclass
class Intervention:
    """Result of a patron-check: what intervention (if any) is applied."""
    type: str              # "avoidance", "recognition", "patrol",
                           # "reverse_ambush", "witness"
    faction_id: str
    faction_name: str
    player_message: str    # what the player sees
    cancels_encounter: bool = True   # if False, encounter still fires


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _faction_name(faction_id: str) -> str:
    try:
        from src.factions import get_faction_manager
        fm = get_faction_manager()
        data = fm.get_faction(faction_id) or {}
        return data.get("name", faction_id)
    except Exception:
        return faction_id


def _character_rep(character, faction_id: str) -> int:
    rep_map = getattr(character, "reputation", {}) or {}
    return int(rep_map.get(faction_id, 0))


# ---------------------------------------------------------------------------
# Public: encounter-chance multiplier (for negative rep)
# ---------------------------------------------------------------------------

def check_encounter_chance_multiplier(character, region: str) -> float:
    """Return a multiplier for the encounter-roll probability based on
    the character's reputation with the region's patron factions.
    Always >=1.0 when negative rep; 1.0 at neutral or positive (positive
    rep's benefits apply post-roll via ``check_intervention``)."""
    patrons = REGION_PATRONS.get(region, [])
    if not patrons:
        return 1.0
    worst_multiplier = 1.0
    for faction_id in patrons:
        rep = _character_rep(character, faction_id)
        standing = _standing_for(rep)
        mult = NEGATIVE_REP_MULTIPLIERS.get(standing, 1.0)
        if mult > worst_multiplier:
            worst_multiplier = mult
    return worst_multiplier


# ---------------------------------------------------------------------------
# Public: patron-check before spawning a threat
# ---------------------------------------------------------------------------

def check_intervention(character, region: str) -> Optional[Intervention]:
    """Check if a patron faction will intervene on the character's
    behalf *before* a threat is spawned.

    Iterates the region's patron factions in order, highest rep first,
    and attempts to roll an intervention.  Returns the first successful
    intervention, or None.
    """
    patrons = REGION_PATRONS.get(region, [])
    if not patrons:
        return None

    # Sort by rep descending so the most-trusted patron gets first chance
    patrons_sorted = sorted(
        patrons,
        key=lambda fid: _character_rep(character, fid),
        reverse=True,
    )

    for faction_id in patrons_sorted:
        rep = _character_rep(character, faction_id)
        standing = _standing_for(rep)
        if standing not in INTERVENTION_TABLE:
            continue  # unfriendly or lower -- no intervention
        for int_type, chance in INTERVENTION_TABLE[standing]:
            if random.random() < chance:
                return _build_intervention(int_type, faction_id, standing)
    return None


def _build_intervention(int_type: str, faction_id: str,
                        standing: str) -> Intervention:
    faction_name = _faction_name(faction_id)
    msgs = {
        "avoidance": (
            f"\033[2;37mSomewhere near, a {faction_name} rider notices "
            f"your passage and adjusts their patrol to shadow your road. "
            f"Whatever was stalking you has had second thoughts.\033[0m"
        ),
        "recognition": (
            f"\033[1;36mYou hear footsteps, then a pause. A gruff voice "
            f"calls from the brush: \"Leave them. That one brought "
            f"Rosin's girl home last spring.\"\n"
            f"The threat withdraws. The {faction_name} does not forget "
            f"debts.\033[0m"
        ),
        "patrol": (
            f"\033[1;33mRiders of the {faction_name} burst from the "
            f"trees, arrows nocked. They move with the practiced speed "
            f"of a patrol that has been tailing you for safety.\n"
            f"The stalking thing breaks and runs. The patrol captain "
            f"raises a gauntleted hand to you and vanishes back into "
            f"the trees.\033[0m"
        ),
        "reverse_ambush": (
            f"\033[1;32mThe ambusher never gets the chance to strike.\n"
            f"A {faction_name} strike-team was shadowing your route, "
            f"and the hunters were the ones walking into a trap. You "
            f"find the body a hundred yards down the path, quietly "
            f"done with.\033[0m"
        ),
        "witness": (
            f"\033[0;36mA traveler on the road spots you and shouts a "
            f"warning down the way. The stalker's approach loses the "
            f"element of surprise -- whatever it is, it will hunt you "
            f"cautiously now.\033[0m"
        ),
    }
    return Intervention(
        type=int_type,
        faction_id=faction_id,
        faction_name=faction_name,
        player_message=msgs.get(int_type, ""),
        # Witness doesn't cancel -- the encounter still fires, just less
        # surprising.  Everything else cancels the threat entirely.
        cancels_encounter=(int_type != "witness"),
    )


# ---------------------------------------------------------------------------
# Helper -- grant reputation for accepting help (informal sign of trust)
# ---------------------------------------------------------------------------

def on_intervention_used(character, intervention: Intervention) -> None:
    """Award a tiny amount of rep when an intervention fires.
    Encourages the faction-help loop to feel rewarding rather than
    consumptive."""
    if intervention is None or character is None:
        return
    try:
        from src.factions import get_faction_manager
        fm = get_faction_manager()
        gain = {"witness": 1, "avoidance": 0, "patrol": 3,
                "recognition": 2, "reverse_ambush": 5}.get(
                    intervention.type, 1)
        if gain > 0:
            fm.modify_reputation(
                character, intervention.faction_id, gain,
                reason=f"{intervention.faction_name} watched over you in the field")
    except Exception as e:
        logger.debug("intervention-use rep reward failed: %s", e)
