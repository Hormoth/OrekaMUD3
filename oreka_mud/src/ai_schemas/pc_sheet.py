"""
PcSheet — player roleplay sheet attached to Character.

Combines player-authored fields (bio, personality, goals, quirks, pronouns)
with engine-authored fields (recent events, titles, notable kills, deaths).

Injected into NPC LLM prompts via summarize_for_prompt() so NPCs can react
to who the player actually is, not just their level/race/class.
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Optional


EVENT_CATEGORIES = {
    "combat", "quest", "social", "death", "discovery", "general",
}


@dataclass
class RecentEvent:
    """A noteworthy thing that recently happened to a PC."""
    text: str                       # natural-language one-liner
    timestamp: float = 0.0
    category: str = "general"       # one of EVENT_CATEGORIES
    weight: float = 1.0             # 0.0-2.0 — higher = more prominent in prompt

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "RecentEvent":
        return RecentEvent(
            text=data.get("text", ""),
            timestamp=float(data.get("timestamp", 0.0)),
            category=data.get("category", "general"),
            weight=float(data.get("weight", 1.0)),
        )


@dataclass
class PcSheet:
    """Roleplay sheet for a player character."""

    # --- Player-authored (set via rpsheet command) ---
    bio: str = ""                   # 1-3 sentences of background
    personality: str = ""           # 1-2 sentences of demeanor
    goals: list = field(default_factory=list)
    quirks: list = field(default_factory=list)   # max 5 observable tics
    pronouns: str = "they/them"

    # --- Engine-authored ---
    recent_events: list = field(default_factory=list)   # rolling window of 10
    titles_earned: list = field(default_factory=list)
    notable_kills: list = field(default_factory=list)   # last 5
    deaths: int = 0
    remorts: int = 0
    npc_relationships: dict = field(default_factory=dict)
    # vnum (str) -> "allied|trusted|warm|neutral|wary|hostile"

    # --- Privacy ---
    sheet_visible_in_prompts: bool = True

    def to_dict(self) -> dict:
        return {
            "bio": self.bio,
            "personality": self.personality,
            "goals": list(self.goals),
            "quirks": list(self.quirks),
            "pronouns": self.pronouns,
            "recent_events": [
                e.to_dict() if isinstance(e, RecentEvent) else e
                for e in self.recent_events
            ],
            "titles_earned": list(self.titles_earned),
            "notable_kills": list(self.notable_kills),
            "deaths": int(self.deaths),
            "remorts": int(self.remorts),
            "npc_relationships": dict(self.npc_relationships),
            "sheet_visible_in_prompts": bool(self.sheet_visible_in_prompts),
        }

    @staticmethod
    def from_dict(data: dict) -> "PcSheet":
        if not isinstance(data, dict):
            return PcSheet()

        events = []
        for e in data.get("recent_events", []) or []:
            if isinstance(e, RecentEvent):
                events.append(e)
            elif isinstance(e, dict):
                events.append(RecentEvent.from_dict(e))

        return PcSheet(
            bio=data.get("bio", ""),
            personality=data.get("personality", ""),
            goals=list(data.get("goals", []) or []),
            quirks=list(data.get("quirks", []) or [])[:5],   # enforce max 5
            pronouns=data.get("pronouns", "they/them"),
            recent_events=events[-10:],     # enforce rolling window of 10
            titles_earned=list(data.get("titles_earned", []) or []),
            notable_kills=list(data.get("notable_kills", []) or [])[-5:],   # last 5
            deaths=int(data.get("deaths", 0)),
            remorts=int(data.get("remorts", 0)),
            npc_relationships=dict(data.get("npc_relationships", {}) or {}),
            sheet_visible_in_prompts=bool(
                data.get("sheet_visible_in_prompts", True)
            ),
        )

    def is_empty(self) -> bool:
        """True if the sheet has no player-authored content."""
        return not any([
            self.bio.strip(),
            self.personality.strip(),
            self.goals,
            self.quirks,
        ])


# ---------------------------------------------------------------------------
# Engine hooks — call these from combat, quest completion, level-up, etc.
# ---------------------------------------------------------------------------

def record_event(
    sheet: PcSheet,
    text: str,
    category: str = "general",
    weight: float = 1.0,
    now: Optional[float] = None,
) -> None:
    """Append a recent event, keeping the rolling window of 10."""
    if not isinstance(sheet, PcSheet):
        return
    if category not in EVENT_CATEGORIES:
        category = "general"
    weight = max(0.0, min(2.0, float(weight)))
    sheet.recent_events.append(RecentEvent(
        text=text,
        timestamp=now if now is not None else time.time(),
        category=category,
        weight=weight,
    ))
    sheet.recent_events = sheet.recent_events[-10:]


def record_notable_kill(sheet: PcSheet, mob_name: str) -> None:
    """Track the player's last 5 boss/unique kills."""
    if not isinstance(sheet, PcSheet) or not mob_name:
        return
    if mob_name in sheet.notable_kills:
        return
    sheet.notable_kills.append(mob_name)
    sheet.notable_kills = sheet.notable_kills[-5:]


# ---------------------------------------------------------------------------
# Prompt summarization
# ---------------------------------------------------------------------------

def summarize_for_prompt(
    sheet: PcSheet,
    character=None,
    max_chars: int = 600,
) -> str:
    """Produce the block of text injected into NPC LLM prompts.

    If sheet is empty or hidden, returns the legacy 1-liner from character data.
    Otherwise builds a structured summary with bio, personality, goals, quirks,
    and the top 3 most-salient recent events ranked by recency × weight.
    """
    # Backward-compat fallback
    if not isinstance(sheet, PcSheet) or sheet.is_empty() or not sheet.sheet_visible_in_prompts:
        if character is None:
            return ""
        name = getattr(character, "name", "Someone")
        level = getattr(character, "level", 1)
        race = getattr(character, "race", "unknown")
        char_class = getattr(character, "char_class", "adventurer")
        return f"Speaking to: {name}, a level {level} {race} {char_class}."

    name = getattr(character, "name", "the traveler") if character else "the traveler"
    parts = [f"Speaking to: {name} ({sheet.pronouns})."]

    if sheet.bio.strip():
        parts.append(f"Background: {sheet.bio.strip()}")
    if sheet.personality.strip():
        parts.append(f"Demeanor: {sheet.personality.strip()}")
    if sheet.goals:
        parts.append("Goals: " + "; ".join(sheet.goals[:3]))
    if sheet.quirks:
        parts.append("Quirks: " + ", ".join(sheet.quirks))
    if sheet.titles_earned:
        parts.append("Titles: " + ", ".join(sheet.titles_earned[-3:]))
    if sheet.notable_kills:
        parts.append("Notable kills: " + ", ".join(sheet.notable_kills[-3:]))
    if sheet.deaths > 0 or sheet.remorts > 0:
        stats = []
        if sheet.deaths:
            stats.append(f"{sheet.deaths} deaths")
        if sheet.remorts:
            stats.append(f"{sheet.remorts} remorts")
        parts.append("History: " + ", ".join(stats))

    # Top 3 recent events by recency × weight
    if sheet.recent_events:
        now = time.time()
        ranked = sorted(
            sheet.recent_events,
            key=lambda e: (
                # Recency factor: events fade over 30 days
                max(0.0, 1.0 - (now - e.timestamp) / (30 * 24 * 3600))
                * e.weight
            ),
            reverse=True,
        )
        top = [e.text for e in ranked[:3] if e.text]
        if top:
            parts.append("Recent: " + " ".join(top))

    summary = "\n".join(parts)
    if len(summary) > max_chars:
        summary = summary[: max_chars - 3] + "..."
    return summary
