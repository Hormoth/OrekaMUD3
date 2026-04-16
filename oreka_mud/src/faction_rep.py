"""Faction-reputation hooks + visual faction sheet renderer.

Two jobs:

1. ``on_mob_killed_rep`` — called from the combat hook when a PC kills a
   mob.  Reads the mob's ``flags`` to decide which factions gain or lose
   reputation and by how much, and applies the changes via the existing
   FactionManager (which already handles GMCP + narrative triggers).

2. ``render_faction_sheet`` — produces the readable ASCII faction sheet
   shown by the ``faction`` / ``factions`` / ``rep`` / ``reputation``
   commands, with a visual bar for each faction showing position from
   Hated to Loved.

The reputation thresholds used for labels and bar positioning mirror the
per-faction thresholds in ``guilds.json`` (Hostile -500, Unfriendly
-100, Neutral 0, Friendly 100, Honored 300, Allied 600).
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


# ---------------------------------------------------------------------------
# CR -> reputation amount tables (sign applied per-faction)
# ---------------------------------------------------------------------------

def _cr_tier(cr) -> str:
    try:
        c = float(cr) if cr is not None else 0.0
    except Exception:
        c = 0.0
    if c < 1:    return "trash"
    if c <= 2:   return "minion"
    if c <= 5:   return "soldier"
    if c <= 9:   return "elite"
    if c <= 14:  return "lieutenant"
    return "boss"


# (positive_delta, negative_delta) per CR tier
CR_DELTAS: Dict[str, Tuple[int, int]] = {
    "trash":      (1, 2),
    "minion":     (2, 5),
    "soldier":    (5, 10),
    "elite":      (10, 20),
    "lieutenant": (25, 50),
    "boss":       (100, 200),
}


# ---------------------------------------------------------------------------
# Mob-flag -> faction reputation rules
# ---------------------------------------------------------------------------
# Each rule emits a list of (faction_id, scale_sign, strength_multiplier)
# tuples.  scale_sign is +1 for gain, -1 for loss; multiplier scales the
# CR delta (1.0 = full, 0.5 = half).  Multiple rules can stack per mob.

FACTION_RULES: Dict[str, List[Tuple[str, int, float]]] = {
    # Core Dómnathar enemies -- killing them strongly shifts player
    # toward "enemies of the Shattered Host" alignment.
    "domnathar": [
        ("shattered_host",   -1, 1.0),
        ("gatefall_remnant", +1, 1.0),
        ("far_riders",       +1, 0.5),
        ("silent_concord",   +1, 0.3),
    ],
    "silentborn": [
        ("shattered_host",   -1, 0.8),
        ("silent_concord",   +1, 0.8),  # Silent Concord is pro-Silentborn
        ("gatefall_remnant", +1, 0.4),
    ],
    "half_domnathar": [
        ("shattered_host",   -1, 0.6),
        ("gatefall_remnant", +1, 0.5),
    ],
    "dark_dwarf": [
        ("shattered_host",   -1, 0.5),
        ("gatefall_remnant", +1, 0.4),
    ],
    "hobgoblin": [
        ("shattered_host",   -1, 0.4),
        ("far_riders",       +1, 0.2),
    ],
    "kobold": [
        ("shattered_host",   -1, 0.2),
    ],
    "goblin": [
        ("shattered_host",   -1, 0.2),
    ],
    # Flamewarg cult is its own faction -- killing cultists boosts
    # Golden Roses (law enforcement) and decrements the cult.
    "cultist": [
        ("flamewarg_cults",  -1, 1.0),
        ("golden_roses",     +1, 0.8),
    ],
    "flamewarg": [
        ("flamewarg_cults",  -1, 0.5),
    ],
    # Unstrung criminal order -- killing their cultists boosts Golden Roses
    "unstrung": [
        ("the_unstrung",     -1, 1.0),
        ("golden_roses",     +1, 0.8),
    ],
}


def _rep_deltas_for_mob(mob) -> List[Tuple[str, int, str]]:
    """Compute per-faction rep deltas for a killed mob.

    Returns a list of (faction_id, delta, reason) tuples.
    """
    flags = {str(f).lower() for f in (getattr(mob, "flags", []) or [])}
    tier = _cr_tier(getattr(mob, "cr", None))
    pos_base, neg_base = CR_DELTAS[tier]

    applied: Dict[str, Tuple[int, str]] = {}
    mob_name = getattr(mob, "name", "creature") or "creature"
    for flag in flags:
        rules = FACTION_RULES.get(flag)
        if not rules:
            continue
        for faction_id, sign, mult in rules:
            base = pos_base if sign > 0 else neg_base
            delta = int(round(sign * base * mult))
            if delta == 0:
                continue
            # Accumulate across flags (a mob with both "domnathar" and
            # "boss" flags takes the larger magnitude).
            prev = applied.get(faction_id)
            if prev is None or abs(delta) > abs(prev[0]):
                applied[faction_id] = (delta, f"slew {mob_name}")

    return [(fid, delta, reason)
            for fid, (delta, reason) in applied.items()]


# ---------------------------------------------------------------------------
# Combat hook -- called from combat.py when a mob dies to a PC
# ---------------------------------------------------------------------------

def on_mob_killed_rep(attacker, mob) -> List[str]:
    """Apply faction rep changes when ``attacker`` kills ``mob``.

    Returns a list of human-readable messages (one per faction).  Safe
    to call with any attacker/mob -- AI-controlled attackers and
    boss-less flags are no-ops.
    """
    if getattr(attacker, "is_ai", False):
        return []
    if not hasattr(attacker, "reputation"):
        attacker.reputation = {}

    deltas = _rep_deltas_for_mob(mob)
    if not deltas:
        return []

    try:
        from src.factions import get_faction_manager
        fm = get_faction_manager()
    except Exception:
        fm = None

    messages: List[str] = []
    for faction_id, delta, reason in deltas:
        if fm is not None:
            try:
                result = fm.modify_reputation(attacker, faction_id, delta,
                                              reason=reason)
                # modify_reputation returns a tuple; last element is the
                # message.  Only surface the "standing changed" line to
                # keep the combat log tidy.
                if isinstance(result, tuple) and result:
                    last = result[-1]
                    if isinstance(last, str) and "now" in last.lower():
                        messages.append(last)
                continue
            except Exception:
                pass  # fall through to manual update
        # Fallback: raw dict update
        cur = attacker.reputation.get(faction_id, 0)
        attacker.reputation[faction_id] = cur + delta

    return messages


# ---------------------------------------------------------------------------
# Visual faction sheet renderer
# ---------------------------------------------------------------------------

# Standing label thresholds -- matches the per-faction bands in
# guilds.json (hostile -500, unfriendly -100, neutral 0, friendly 100,
# honored 300, allied 600) with "Hated" and "Revered" added as outer
# extremes.
STANDING_THRESHOLDS: List[Tuple[int, str, str]] = [
    (-999999, "Hated",      "\033[1;31m"),  # floor -- anything below -500
    (-500,    "Hostile",    "\033[0;31m"),  # -500 to -101
    (-100,    "Unfriendly", "\033[0;33m"),  # -100 to -1
    (0,       "Neutral",    "\033[0;37m"),  # 0 to 99
    (100,     "Friendly",   "\033[0;36m"),  # 100 to 299
    (300,     "Honored",    "\033[0;32m"),  # 300 to 599
    (600,     "Allied",     "\033[1;32m"),  # 600 to 999
    (1000,    "Revered",    "\033[1;36m"),  # 1000+
]
_RESET = "\033[0m"


def _standing(rep: int) -> Tuple[str, str]:
    """Return (label, ansi_color) for a given rep value."""
    label, color = "Hated", STANDING_THRESHOLDS[0][2]
    for threshold, lbl, clr in STANDING_THRESHOLDS:
        if rep >= threshold:
            label, color = lbl, clr
    return label, color


# Bar parameters
BAR_WIDTH = 40
BAR_MIN = -500
BAR_MAX = 600


def _render_bar(rep: int) -> str:
    """Render a 40-char bar with a ● marker at the rep's position."""
    span = BAR_MAX - BAR_MIN
    clamped = max(BAR_MIN, min(BAR_MAX, rep))
    pos = int(round((clamped - BAR_MIN) / span * (BAR_WIDTH - 1)))
    # Find the "neutral" position for the mid-divider
    mid = int(round((0 - BAR_MIN) / span * (BAR_WIDTH - 1)))

    chars = []
    for i in range(BAR_WIDTH):
        if i == pos:
            chars.append("\033[1;37m\u25CF\033[0m")  # ● bright white
        elif i == mid:
            chars.append("\033[0;90m|\033[0m")  # dim | at neutral
        elif i < mid:
            # negative side -- red shades, heavier if further left
            chars.append("\033[0;31m-\033[0m")
        else:
            # positive side -- green shades
            chars.append("\033[0;32m=\033[0m")
    return "".join(chars)


def render_faction_sheet(character) -> str:
    """Render the full faction sheet for ``character`` as ASCII+ANSI."""
    rep_map: Dict[str, int] = dict(getattr(character, "reputation", {}) or {})

    # Pull faction metadata
    try:
        from src.factions import get_faction_manager
        fm = get_faction_manager()
        all_factions = fm.get_all_factions()
    except Exception:
        all_factions = {}

    # Compose the sorted list: include every faction the player has any
    # reputation with, plus every "joinable" faction (so new players see
    # all options at Neutral).
    shown: List[str] = []
    seen: set = set()
    # First: factions the player has any non-zero rep with, sorted by rep desc
    for fid, val in sorted(rep_map.items(), key=lambda x: -x[1]):
        shown.append(fid)
        seen.add(fid)
    # Then: joinable factions the player doesn't have rep with
    for fid, data in all_factions.items():
        if fid in seen:
            continue
        if (data or {}).get("type") == "joinable":
            shown.append(fid)
            seen.add(fid)
    # Finally: enemy factions the player hasn't encountered yet
    for fid, data in all_factions.items():
        if fid in seen:
            continue
        if (data or {}).get("type") == "enemy":
            shown.append(fid)

    W = 74
    top    = "\033[1;36m" + "+" + "=" * W + "+" + _RESET
    sep    = "\033[0;36m" + "+" + "-" * W + "+" + _RESET
    title  = "\033[1;36m|\033[0m" + " " * 22 + \
             "\033[1;37mFACTION STANDINGS\033[0m" + " " * 35 + \
             "\033[1;36m|" + _RESET
    lines: List[str] = [top, title, top]

    if not shown:
        lines.append("\033[0;36m|\033[0m  (no factions loaded)"
                     + " " * (W - 22) + "\033[0;36m|" + _RESET)
        lines.append(top)
        return "\n".join(lines)

    def pad(text: str, n: int, align: str = "left") -> str:
        """Pad/truncate visible text to exactly n cols (ANSI-aware)."""
        import re
        visible = re.sub(r"\033\[[0-9;]*m", "", text)
        pad_len = max(0, n - len(visible))
        if align == "right":
            return " " * pad_len + text
        if align == "center":
            left = pad_len // 2
            right = pad_len - left
            return " " * left + text + " " * right
        return text + " " * pad_len

    for fid in shown:
        data = all_factions.get(fid, {})
        name = data.get("name", fid)
        ftype = data.get("type", "neutral")
        rep = rep_map.get(fid, 0)
        label, color = _standing(rep)
        # Tag enemy factions so players understand orientation
        if ftype == "enemy":
            name_tag = f"{name} \033[0;31m[enemy]\033[0m"
        elif ftype == "joinable":
            name_tag = f"{name} \033[0;36m[joinable]\033[0m"
        else:
            name_tag = name
        header = f"  {name_tag}"
        right  = f"{color}{label}\033[0m ({rep:+d})"
        # Layout: left-padded header, right-aligned standing label
        line1 = "\033[0;36m|\033[0m " + pad(header, W - 22) + pad(right, 20, "right") + " \033[0;36m|" + _RESET
        bar = _render_bar(rep)
        line2 = ("\033[0;36m|\033[0m    \033[0;90mHated\033[0m " + bar
                 + " \033[0;90mLoved\033[0m" + " " * (W - 58)
                 + "\033[0;36m|" + _RESET)
        lines.append(line1)
        lines.append(line2)
        lines.append(sep)

    # Replace the last separator with the bottom top-bar
    if lines[-1] == sep:
        lines[-1] = top

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Score-sheet helper -- short summary of top 3 standings
# ---------------------------------------------------------------------------

def render_standings_summary(character, limit: int = 3) -> List[str]:
    """Return up to ``limit`` one-line summaries of the character's most
    extreme standings (most honored + most hostile), for inclusion in
    the score sheet.  Output is plain text, no ANSI."""
    rep_map = getattr(character, "reputation", {}) or {}
    if not rep_map:
        return []
    try:
        from src.factions import get_faction_manager
        fm = get_faction_manager()
        factions = fm.get_all_factions()
    except Exception:
        factions = {}

    # Highest absolute value first -- surfaces both strong positive and strong negative
    top = sorted(rep_map.items(), key=lambda x: -abs(x[1]))[:limit]
    out: List[str] = []
    for fid, val in top:
        fdata = factions.get(fid, {})
        name = fdata.get("name", fid)
        label, _ = _standing(val)
        out.append(f" {name}: {label} ({val:+d})")
    return out
