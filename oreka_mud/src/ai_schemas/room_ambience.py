"""
RoomAmbience — optional rich atmosphere data for room JSON.

Most rooms keep their basic name/description/exits/flags. High-traffic
or chat-heavy rooms (Central Aetherial Altar, chapel rooms, Custos town,
Kharazhad forge, Gatefall frontier) get RoomAmbience attached for richer
LLM context.

When ambience is None, the prompt builder falls back to the room's plain
description.
"""

from dataclasses import dataclass, field, asdict


VALID_TIME_VARIANTS = {"dawn", "day", "dusk", "night"}


@dataclass
class RoomAmbience:
    """Atmospheric metadata for an LLM-aware room."""

    mood: str = ""                          # "tense", "reverent", "festive", "abandoned"
    sounds: list = field(default_factory=list)
    smells: list = field(default_factory=list)
    textures: list = field(default_factory=list)
    ambient_details: list = field(default_factory=list)
    # ambient_details: short atmospheric flavors, rotated through prompts

    npc_relevance: dict = field(default_factory=dict)
    # vnum (str) -> "why this NPC belongs here"

    events_history: list = field(default_factory=list)
    # last 5 notable events that happened here

    seasonal_variants: dict = field(default_factory=dict)
    # season_name -> description override

    time_variants: dict = field(default_factory=dict)
    # one of VALID_TIME_VARIANTS -> description override

    def to_dict(self) -> dict:
        return {
            "mood": self.mood,
            "sounds": list(self.sounds),
            "smells": list(self.smells),
            "textures": list(self.textures),
            "ambient_details": list(self.ambient_details),
            "npc_relevance": dict(self.npc_relevance),
            "events_history": list(self.events_history),
            "seasonal_variants": dict(self.seasonal_variants),
            "time_variants": dict(self.time_variants),
        }

    @staticmethod
    def from_dict(data: dict) -> "RoomAmbience":
        if not isinstance(data, dict):
            return RoomAmbience()
        return RoomAmbience(
            mood=data.get("mood", ""),
            sounds=list(data.get("sounds", []) or []),
            smells=list(data.get("smells", []) or []),
            textures=list(data.get("textures", []) or []),
            ambient_details=list(data.get("ambient_details", []) or []),
            npc_relevance=dict(data.get("npc_relevance", {}) or {}),
            events_history=list(data.get("events_history", []) or [])[-5:],
            seasonal_variants=dict(data.get("seasonal_variants", {}) or {}),
            time_variants=dict(data.get("time_variants", {}) or {}),
        )

    def is_empty(self) -> bool:
        return not any([
            self.mood.strip(),
            self.sounds, self.smells, self.textures,
            self.ambient_details, self.npc_relevance,
            self.events_history, self.seasonal_variants, self.time_variants,
        ])

    def push_event(self, event_text: str) -> None:
        """Add to events_history, keeping last 5."""
        if not event_text:
            return
        self.events_history.append(event_text)
        self.events_history = self.events_history[-5:]


def validate_ambience(data) -> list:
    """Return list of error strings; empty list means valid."""
    errors = []

    if isinstance(data, RoomAmbience):
        d = data.to_dict()
    elif isinstance(data, dict):
        d = data
    else:
        return [f"ambience must be dict or RoomAmbience, got {type(data).__name__}"]

    # time_variants keys must be valid phases
    for k in d.get("time_variants", {}) or {}:
        if k not in VALID_TIME_VARIANTS:
            errors.append(
                f"time_variants key {k!r} not in {sorted(VALID_TIME_VARIANTS)}"
            )

    # All list fields must be lists of strings
    for field_name in ("sounds", "smells", "textures", "ambient_details", "events_history"):
        val = d.get(field_name, [])
        if not isinstance(val, list):
            errors.append(f"{field_name} must be a list, got {type(val).__name__}")
            continue
        for i, item in enumerate(val):
            if not isinstance(item, str):
                errors.append(f"{field_name}[{i}] must be string, got {type(item).__name__}")

    return errors
