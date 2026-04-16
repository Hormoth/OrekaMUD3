"""Reputation-gated quest reveal.

When a player talks to an NPC whose faction they've reached a rep
threshold with, the NPC may reveal a hidden quest.  The framing of the
reveal depends on the quest's ``delivery_mode``:

    step_close  -- whispered in public (low threshold, immediate)
    follow_me   -- NPC walks you somewhere private before telling you
    private     -- names a specific room + time to meet
    later       -- appointment: come find me at hour X
    demand      -- high-rep delivery; blunt order, no niceties

Hidden quests live in ``data/hidden_quests.json``.  Each quest has:
    faction_id, min_rep, npc_match, delivery_mode, title, hook,
    location_hint, reward_gold_range, reward_rep_amount

Revealed state is stored on the character as ``character.revealed_quests``
(a list of quest IDs) so each quest is revealed exactly once per
character, and completion tracking can layer on top later.
"""

from __future__ import annotations

import json
import logging
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger("OrekaMUD.QuestReveal")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data",
                          "hidden_quests.json")


def _load_quests() -> List[Dict[str, Any]]:
    try:
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(data.get("quests", []) or [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("hidden_quests.json load failed: %s", e)
        return []


_quests: Optional[List[Dict[str, Any]]] = None


def get_quests() -> List[Dict[str, Any]]:
    global _quests
    if _quests is None:
        _quests = _load_quests()
    return _quests


def reload_quests() -> None:
    global _quests
    _quests = None


# ---------------------------------------------------------------------------
# Reveal check
# ---------------------------------------------------------------------------

def _character_rep(character, faction_id: str) -> int:
    rep_map = getattr(character, "reputation", {}) or {}
    return int(rep_map.get(faction_id, 0))


def _already_revealed(character, quest_id: str) -> bool:
    revealed = getattr(character, "revealed_quests", []) or []
    return quest_id in revealed


def _mark_revealed(character, quest_id: str) -> None:
    if not hasattr(character, "revealed_quests"):
        character.revealed_quests = []
    if quest_id not in character.revealed_quests:
        character.revealed_quests.append(quest_id)


def _npc_matches(quest: Dict[str, Any], npc) -> bool:
    """Quest.npc_match is a substring; empty string matches any NPC
    (used for generic faction-officer quests like "demand")."""
    pattern = (quest.get("npc_match") or "").strip().lower()
    if not pattern:
        # Must still be an NPC in the same faction.  Accept any family-
        # representative NPC (all 15 family reps are flagged "family_rep").
        flags = {str(f).lower() for f in getattr(npc, "flags", []) or []}
        return "family_rep" in flags or "quest_giver" in flags
    return pattern in (getattr(npc, "name", "") or "").lower()


def check_for_reveals(character, npc) -> List[Dict[str, Any]]:
    """Return a list of hidden quests this NPC is willing to reveal to
    this character right now (rep threshold met, not already revealed,
    NPC matches)."""
    out: List[Dict[str, Any]] = []
    for q in get_quests():
        if _already_revealed(character, q["id"]):
            continue
        if not _npc_matches(q, npc):
            continue
        rep = _character_rep(character, q["faction_id"])
        if rep < int(q.get("min_rep", 0)):
            continue
        out.append(q)
    return out


# ---------------------------------------------------------------------------
# Delivery-mode renderers
# ---------------------------------------------------------------------------

def _render_step_close(character, npc, quest: Dict[str, Any]) -> str:
    """A quiet whispered reveal in a public space."""
    return (
        f"\033[2;37m{npc.name} leans close as if adjusting a strap, "
        f"and speaks very quietly so only you hear:\033[0m\n"
        f"\033[0;36m\"{quest['hook']}\"\033[0m\n"
        f"\033[0;37m{npc.name} steps back and resumes speaking of "
        f"ordinary things. The hint is yours to follow or ignore.\033[0m\n"
        f"\033[2;37m(New hidden quest: \033[1;33m{quest['title']}\033[2;37m. "
        f"Location hint: {quest['location_hint']})\033[0m"
    )


def _render_follow_me(character, npc, quest: Dict[str, Any]) -> str:
    """NPC leads you to a private room before speaking."""
    return (
        f"\033[0;36m{npc.name} nods once, folds their hand over yours, "
        f"and murmurs: \"Walk with me.\"\033[0m\n"
        f"\033[2;37mYou follow them past the common room, past the shopkeepers, "
        f"to a quieter door. They close it behind you.\033[0m\n"
        f"\033[0;37m\"{quest['hook']}\"\033[0m\n"
        f"\033[2;37m(New hidden quest: \033[1;33m{quest['title']}\033[2;37m. "
        f"Location hint: {quest['location_hint']})\033[0m"
    )


def _render_private(character, npc, quest: Dict[str, Any]) -> str:
    """NPC names a specific room for a later private meeting."""
    return (
        f"\033[0;36m{npc.name} glances past your shoulder, lowers their voice:\n"
        f"\"Not here. My quarters, after everyone else has turned in. Come alone.\"\033[0m\n"
        f"\033[2;37mLater, in the agreed-upon quiet:\033[0m\n"
        f"\033[0;37m\"{quest['hook']}\"\033[0m\n"
        f"\033[2;37m(New hidden quest: \033[1;33m{quest['title']}\033[2;37m. "
        f"Location hint: {quest['location_hint']})\033[0m"
    )


def _render_later(character, npc, quest: Dict[str, Any]) -> str:
    """NPC defers to a specific future time."""
    hour = quest.get("appointment_hour", 2)
    ap_text = quest.get("appointment_text",
                          f"at the {hour:02d}th hour of the day")
    return (
        f"\033[0;36m{npc.name} studies you a long moment, then shakes their head.\n"
        f"\"Not here. Not now. Come find me {ap_text}. If you're serious "
        f"about this, you'll be there.\"\033[0m\n"
        f"\033[2;37m(Hidden quest \033[1;33m{quest['title']}\033[2;37m "
        f"will be revealed when you return at that hour.)\033[0m"
    )


def _render_demand(character, npc, quest: Dict[str, Any]) -> str:
    """High-rep: blunt order."""
    return (
        f"\033[1;31m{npc.name} sees you enter and does not rise. "
        f"They speak without preamble:\033[0m\n"
        f"\033[1;37m\"{quest['hook']}\"\033[0m\n"
        f"\033[0;37m{npc.name} does not wait for your agreement. They "
        f"expect compliance.\033[0m\n"
        f"\033[2;37m(New hidden quest: \033[1;33m{quest['title']}\033[2;37m. "
        f"Location hint: {quest['location_hint']})\033[0m"
    )


_RENDERERS = {
    "step_close": _render_step_close,
    "follow_me":  _render_follow_me,
    "private":    _render_private,
    "later":      _render_later,
    "demand":     _render_demand,
}


# ---------------------------------------------------------------------------
# Public: reveal dispatch
# ---------------------------------------------------------------------------

def attempt_reveals(character, npc) -> Optional[str]:
    """Called from the talk command (and talkto).  If this NPC is
    willing to reveal any hidden quests to this character, picks the
    HIGHEST-tier one available and fires its reveal.  Returns the
    narrative text, or None if nothing is revealed.

    Only one quest is revealed per interaction, so players unlock
    content gradually rather than getting flooded.
    """
    candidates = check_for_reveals(character, npc)
    if not candidates:
        return None

    # Prefer the highest-threshold quest we haven't yet seen -- that's
    # the one the NPC would be most nervous/relieved to finally share.
    candidates.sort(key=lambda q: int(q.get("min_rep", 0)), reverse=True)

    # For "later" delivery, check if we're at the appointment hour
    try:
        from src.schedules import get_game_time
        game_time = get_game_time()
        cur_hour = int(getattr(game_time, "hour", 0))
    except Exception:
        cur_hour = 0

    for quest in candidates:
        mode = quest.get("delivery_mode", "step_close")
        if mode == "later":
            ap_hour = int(quest.get("appointment_hour", 2))
            # If we haven't told the player about the appointment yet,
            # tell them now (mark half-revealed)
            half_key = f"_appt_{quest['id']}"
            if not _already_revealed(character, half_key):
                renderer = _RENDERERS["later"]
                _mark_revealed(character, half_key)
                return renderer(character, npc, quest)
            # Player has the appointment -- check if it's time
            if abs(cur_hour - ap_hour) > 1:
                continue  # not the right hour; keep searching
        renderer = _RENDERERS.get(mode, _render_step_close)
        _mark_revealed(character, quest["id"])
        return renderer(character, npc, quest)

    return None


# ---------------------------------------------------------------------------
# Completion stub (for future integration with quest system)
# ---------------------------------------------------------------------------

def complete_hidden_quest(character, quest_id: str, npc) -> Optional[str]:
    """Called when the player returns to the NPC having completed the
    task.  MVP: this is a stub -- requires the quest-tracking system
    to fully wire the "did player do X" check.  For now, it's player-
    driven: returning to the NPC after claiming completion pays out.
    """
    quest = next((q for q in get_quests() if q["id"] == quest_id), None)
    if quest is None:
        return None
    if not _already_revealed(character, quest_id):
        return None

    # Check for a completed-flag on the character
    completed = getattr(character, "completed_hidden_quests", [])
    if quest_id in completed:
        return None  # already paid

    # Apply reward
    low, high = quest.get("reward_gold_range", [50, 100])
    gold = random.randint(low, high)
    character.gold = getattr(character, "gold", 0) + gold

    rep_amount = int(quest.get("reward_rep_amount", 0))
    faction_msg = ""
    if rep_amount:
        try:
            from src.factions import get_faction_manager
            fm = get_faction_manager()
            result = fm.modify_reputation(
                character, quest["faction_id"], rep_amount,
                reason=f"completed '{quest['title']}'")
            if isinstance(result, tuple) and result:
                faction_msg = "\n" + str(result[-1])
        except Exception:
            pass

    if not hasattr(character, "completed_hidden_quests"):
        character.completed_hidden_quests = []
    character.completed_hidden_quests.append(quest_id)

    return (
        f"\033[1;36m{npc.name} listens to your report, nods slowly, "
        f"and reaches into their purse.\033[0m\n"
        f"\033[1;33m{npc.name} presses {gold} gold into your palm.\033[0m"
        + faction_msg
    )


# ---------------------------------------------------------------------------
# Status rendering for the character sheet
# ---------------------------------------------------------------------------

def render_hidden_quests(character) -> str:
    """Return a summary of revealed + completed hidden quests."""
    revealed = getattr(character, "revealed_quests", []) or []
    completed = getattr(character, "completed_hidden_quests", []) or []
    quests = get_quests()
    by_id = {q["id"]: q for q in quests}

    if not revealed and not completed:
        return "You have no hidden quests yet. Build reputation with factions."

    lines = ["\033[1;33m=== Hidden Quests ===\033[0m"]
    for qid in revealed:
        if qid.startswith("_appt_"):
            continue
        q = by_id.get(qid)
        if q is None:
            continue
        status = "\033[0;32m[COMPLETED]\033[0m" if qid in completed else "\033[0;33m[OPEN]\033[0m"
        lines.append(f"  {status} \033[1;37m{q['title']}\033[0m")
        lines.append(f"      {q['location_hint']}")
    return "\n".join(lines)
