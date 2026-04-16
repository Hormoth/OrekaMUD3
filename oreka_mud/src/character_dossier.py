"""Character dossier — dual-purpose: player journal + AI context.

Two views of the same underlying data:

    render_journal(character) -> str
        Player-facing command output. Narrative-flavored summary of
        their adventure history: rescues, factions, exploration,
        combat, quests. The character reads their own diary.

    build_dossier(character) -> dict
        System-facing structured summary for AI persona injection.
        NPCs and the DM Agent read this to understand who they're
        dealing with: "Honored with Far Riders, rescued 8 captives
        including a VIP, survived a Burnt Trail, explored 40% of
        the world."

Both draw from the same character fields; neither creates new data.
"""

from __future__ import annotations

import time
from collections import Counter
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Total rooms in the world (approximate; used for exploration %)
TOTAL_WORLD_ROOMS = 1926

# Region vnum ranges for exploration breakdown
REGION_RANGES = {
    "Kinsweave":       (5000, 5999),
    "Tidebloom Reach": (6000, 6999),
    "Eternal Steppe":  (7000, 7999),
    "Infinite Desert": (8000, 8999),
    "Deepwater":       (9000, 9999),
    "Twin Rivers":     (10000, 10999),
    "Gatefall Reach":  (12000, 12999),
    "Custos":          (4000, 4999),
    "Chainless":       (13000, 13999),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _standing_label(rep: int) -> str:
    if rep < -500:   return "Hated"
    if rep < -100:   return "Hostile"
    if rep < 0:      return "Unfriendly"
    if rep < 100:    return "Neutral"
    if rep < 300:    return "Friendly"
    if rep < 600:    return "Honored"
    if rep < 1000:   return "Allied"
    return "Revered"


def _faction_name(faction_id: str) -> str:
    try:
        from src.factions import get_faction_manager
        fm = get_faction_manager()
        data = fm.get_faction(faction_id) or {}
        return data.get("name", faction_id)
    except Exception:
        return faction_id


def _exploration_stats(character) -> Dict[str, Any]:
    visited = getattr(character, "rooms_visited", set()) or set()
    total = len(visited)
    pct = round(total / max(TOTAL_WORLD_ROOMS, 1) * 100, 1)
    by_region: Dict[str, int] = {}
    for vnum in visited:
        for region, (lo, hi) in REGION_RANGES.items():
            if lo <= vnum <= hi:
                by_region[region] = by_region.get(region, 0) + 1
                break
    return {"total": total, "pct": pct, "by_region": by_region}


def _rescue_stats(character) -> Dict[str, Any]:
    records = getattr(character, "rescued_captives", []) or []
    total = len(records)
    by_type = Counter(r.get("type", "unknown") for r in records)
    families = set(r.get("family_id") for r in records if r.get("family_id"))
    total_gold = sum(r.get("gold", 0) for r in records)
    return {
        "total": total,
        "by_type": dict(by_type),
        "unique_families": len(families),
        "total_gold_earned": total_gold,
        "has_leader_rescue": by_type.get("leader", 0) > 0,
        "has_memoriam": by_type.get("memoriam", 0) > 0 or
                        by_type.get("quiet_tragedy", 0) > 0,
        "has_self_rescue": by_type.get("self_rescue", 0) > 0,
    }


def _quest_stats(character) -> Dict[str, Any]:
    revealed = getattr(character, "revealed_quests", []) or []
    completed = getattr(character, "completed_hidden_quests", []) or []
    # Filter out appointment-half-reveals
    real_revealed = [q for q in revealed if not q.startswith("_appt_")]
    return {
        "revealed": len(real_revealed),
        "completed": len(completed),
        "open": len(set(real_revealed) - set(completed)),
    }


def _faction_stats(character) -> List[Dict[str, Any]]:
    rep_map = getattr(character, "reputation", {}) or {}
    out = []
    for fid, val in sorted(rep_map.items(), key=lambda x: -abs(x[1])):
        out.append({
            "id": fid,
            "name": _faction_name(fid),
            "rep": val,
            "standing": _standing_label(val),
        })
    return out


def _behavioral_tags(character, rescue: Dict, exploration: Dict,
                     factions: List) -> List[str]:
    """Derive qualitative tags from quantitative data.  Used by the AI
    dossier to give NPCs a quick read on the character's personality."""
    tags: List[str] = []
    if rescue["total"] >= 10:
        tags.append("prolific rescuer")
    elif rescue["total"] >= 3:
        tags.append("experienced rescuer")
    if rescue["has_leader_rescue"]:
        tags.append("VIP rescuer")
    if rescue["has_memoriam"]:
        tags.append("has carried grief")
    if exploration["pct"] >= 50:
        tags.append("world-walker")
    elif exploration["pct"] >= 20:
        tags.append("seasoned traveler")
    elif exploration["pct"] < 5:
        tags.append("newcomer")
    kill_count = int(getattr(character, "kill_count", 0))
    if kill_count >= 100:
        tags.append("veteran combatant")
    elif kill_count >= 30:
        tags.append("blooded fighter")
    # Faction alignment tags
    for f in factions:
        if f["standing"] in ("Allied", "Revered"):
            tags.append(f"deep ally of {f['name']}")
        elif f["standing"] == "Hated":
            tags.append(f"enemy of {f['name']}")
    if getattr(character, "remort_count", 0) > 0:
        tags.append("reborn")
    return tags


# ---------------------------------------------------------------------------
# Player-facing: the journal command
# ---------------------------------------------------------------------------

def render_journal(character) -> str:
    """Render the player's adventure journal as narrative-flavored ASCII."""
    rescue = _rescue_stats(character)
    exploration = _exploration_stats(character)
    quests = _quest_stats(character)
    factions = _faction_stats(character)
    tags = _behavioral_tags(character, rescue, exploration, factions)

    W = 74
    R = "\033[0m"
    C = "\033[1;36m"  # cyan headers
    G = "\033[1;33m"  # gold numbers
    D = "\033[0;37m"  # dim text

    top = f"{C}+{'=' * W}+{R}"
    sep = f"{C}+{'-' * W}+{R}"

    lines = [top]
    name = getattr(character, "name", "Adventurer")
    level = int(getattr(character, "level", 1))
    race = getattr(character, "race", "Unknown")
    cls = getattr(character, "char_class", "Adventurer")
    lines.append(f"{C}|{R}  {G}THE JOURNAL OF {name.upper()}{R}")
    lines.append(f"{C}|{R}  {D}Level {level} {race} {cls}{R}")
    lines.append(sep)

    # --- Rescues ---
    lines.append(f"{C}|{R}  {C}RESCUES{R}")
    if rescue["total"] == 0:
        lines.append(f"{C}|{R}    {D}No captives rescued yet.{R}")
    else:
        lines.append(f"{C}|{R}    Captives freed: {G}{rescue['total']}{R}"
                     f"  ({rescue['unique_families']} distinct families)")
        lines.append(f"{C}|{R}    Gold earned from rescues: {G}{rescue['total_gold_earned']}{R}")
        if rescue["by_type"]:
            type_parts = [f"{t}: {n}" for t, n in rescue["by_type"].items()]
            lines.append(f"{C}|{R}    By type: {', '.join(type_parts)}")
        if rescue["has_leader_rescue"]:
            lines.append(f"{C}|{R}    {G}* Rescued a VIP captive{R}")
        if rescue["has_memoriam"]:
            lines.append(f"{C}|{R}    {D}* Carried word of the dead home{R}")
    lines.append(sep)

    # --- Factions ---
    lines.append(f"{C}|{R}  {C}FACTION STANDINGS{R}")
    if not factions:
        lines.append(f"{C}|{R}    {D}No notable standings.{R}")
    else:
        for f in factions[:8]:
            color = "\033[0;32m" if f["rep"] > 0 else "\033[0;31m" if f["rep"] < 0 else D
            lines.append(f"{C}|{R}    {f['name']:35s} "
                         f"{color}{f['standing']:12s} ({f['rep']:+d}){R}")
    lines.append(sep)

    # --- Exploration ---
    lines.append(f"{C}|{R}  {C}EXPLORATION{R}")
    lines.append(f"{C}|{R}    Rooms visited: {G}{exploration['total']}{R}"
                 f" / {TOTAL_WORLD_ROOMS}"
                 f"  ({G}{exploration['pct']}%{R} of the world)")
    if exploration["by_region"]:
        for region, count in sorted(exploration["by_region"].items(),
                                     key=lambda x: -x[1])[:5]:
            lines.append(f"{C}|{R}      {region:20s} {G}{count}{R} rooms")
    lines.append(sep)

    # --- Combat ---
    lines.append(f"{C}|{R}  {C}COMBAT{R}")
    kill_count = int(getattr(character, "kill_count", 0))
    lines.append(f"{C}|{R}    Kills: {G}{kill_count}{R}")
    remort = int(getattr(character, "remort_count", 0))
    if remort > 0:
        lines.append(f"{C}|{R}    Remorts: {G}{remort}{R}")
    lines.append(sep)

    # --- Quests ---
    lines.append(f"{C}|{R}  {C}HIDDEN QUESTS{R}")
    if quests["revealed"] == 0:
        lines.append(f"{C}|{R}    {D}No hidden quests revealed yet.{R}")
    else:
        lines.append(f"{C}|{R}    Revealed: {G}{quests['revealed']}{R}"
                     f"  Completed: {G}{quests['completed']}{R}"
                     f"  Open: {G}{quests['open']}{R}")
    lines.append(sep)

    # --- Character tags ---
    if tags:
        lines.append(f"{C}|{R}  {C}KNOWN AS{R}")
        lines.append(f"{C}|{R}    {', '.join(tags)}")
        lines.append(sep)

    # --- Crafting ---
    craft_count = int(getattr(character, "craft_count", 0))
    if craft_count > 0:
        lines.append(f"{C}|{R}  {C}CRAFTING{R}")
        lines.append(f"{C}|{R}    Items crafted: {G}{craft_count}{R}")
        lines.append(sep)

    lines.append(top)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# System-facing: AI / NPC / DM Agent dossier
# ---------------------------------------------------------------------------

def build_dossier(character) -> Dict[str, Any]:
    """Build a structured dossier for AI context injection.

    Returns a dict suitable for JSON serialization and prompt injection:

        {
            "name": "Hormoth",
            "level": 12,
            "race": "Eruskan Human",
            "class": "Ranger",
            "tags": ["prolific rescuer", "world-walker", "deep ally of Far Riders"],
            "factions": [
                {"name": "Far Riders", "standing": "Allied", "rep": 650},
                ...
            ],
            "rescues": {"total": 8, "by_type": {...}, "has_leader_rescue": true},
            "exploration": {"pct": 34.2, "total": 660},
            "quests": {"revealed": 5, "completed": 2, "open": 3},
            "kill_count": 87,
            "remort_count": 0,
            "summary": "A level-12 Eruskan Human Ranger known as a prolific
                        rescuer and deep ally of the Far Riders. Has explored
                        34% of the world and completed 2 hidden quests."
        }

    The ``summary`` field is a one-paragraph plain-English description
    suitable for direct injection into an NPC prompt as context.
    """
    rescue = _rescue_stats(character)
    exploration = _exploration_stats(character)
    quests = _quest_stats(character)
    factions = _faction_stats(character)
    tags = _behavioral_tags(character, rescue, exploration, factions)

    name = getattr(character, "name", "Unknown")
    level = int(getattr(character, "level", 1))
    race = getattr(character, "race", "Unknown")
    cls = getattr(character, "char_class", "Adventurer")
    kill_count = int(getattr(character, "kill_count", 0))
    remort = int(getattr(character, "remort_count", 0))

    # Build one-paragraph summary for prompt injection
    parts = [f"A level-{level} {race} {cls}"]
    if tags:
        parts.append(f"known as {', '.join(tags[:3])}")
    if rescue["total"] > 0:
        parts.append(f"who has rescued {rescue['total']} captives "
                     f"across {rescue['unique_families']} families")
    if exploration["pct"] >= 10:
        parts.append(f"and explored {exploration['pct']}% of the world")
    if quests["completed"] > 0:
        parts.append(f"completing {quests['completed']} hidden quests")
    # Faction highlights
    top_positive = [f for f in factions if f["rep"] > 100][:2]
    top_negative = [f for f in factions if f["rep"] < -100][:1]
    if top_positive:
        fac_str = " and ".join(f["name"] for f in top_positive)
        parts.append(f"deeply trusted by {fac_str}")
    if top_negative:
        parts.append(f"hostile to {top_negative[0]['name']}")
    summary = ". ".join(parts) + "."

    return {
        "name": name,
        "level": level,
        "race": race,
        "class": cls,
        "tags": tags,
        "factions": factions,
        "rescues": rescue,
        "exploration": {
            "pct": exploration["pct"],
            "total": exploration["total"],
        },
        "quests": quests,
        "kill_count": kill_count,
        "remort_count": remort,
        "summary": summary,
    }


def build_dossier_prompt_block(character) -> str:
    """Return a text block suitable for direct injection into an NPC
    chat prompt.  Compact, ~100-200 tokens, covers the essentials an
    NPC would know or intuit about the character.
    """
    d = build_dossier(character)
    lines = [
        f"[Character Dossier for {d['name']}]",
        d["summary"],
    ]
    if d["factions"]:
        fac_lines = [f"  {f['name']}: {f['standing']} ({f['rep']:+d})"
                     for f in d["factions"][:5]]
        lines.append("Faction standings: " + "; ".join(
            f"{f['name']}={f['standing']}" for f in d["factions"][:5]
        ))
    if d["rescues"]["total"] > 0:
        lines.append(f"Captives rescued: {d['rescues']['total']} "
                     f"({d['rescues']['unique_families']} families)")
    if d["tags"]:
        lines.append(f"Reputation: {', '.join(d['tags'][:4])}")
    return "\n".join(lines)
