"""
Scene state — Phase 2 of DM Player.

Per-player scene tracking. What the DM *thinks* is going on: current room,
active NPCs it has introduced, tone, pending foreshadowing beats (reserved
for Phase 10), last contact timestamp (used for "since we last spoke" recap).

Persisted to data/dm_scene_state/<player>.json. Separate from DMSession
so the conversation log can be trimmed without losing the scene the DM
has established.
"""

import json
import os
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

logger = logging.getLogger("OrekaMUD.DM.Scene")

SCENE_STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "dm_scene_state")

DEFAULT_TONE = "neutral"
VALID_TONES = {"neutral", "tense", "somber", "hopeful", "ominous",
               "comedic", "reverent", "triumphant", "mysterious", "melancholy"}


@dataclass
class SceneState:
    player_name: str
    scene_id: int = 0
    last_room_vnum: int = 0
    active_npcs: List[str] = field(default_factory=list)
    pending_beats: List[Dict] = field(default_factory=list)  # Phase 10 seeds
    tone: str = DEFAULT_TONE
    last_contact_ts: float = 0.0
    created_at: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SceneState":
        return cls(
            player_name=d["player_name"],
            scene_id=d.get("scene_id", 0),
            last_room_vnum=d.get("last_room_vnum", 0),
            active_npcs=d.get("active_npcs", []),
            pending_beats=d.get("pending_beats", []),
            tone=d.get("tone", DEFAULT_TONE),
            last_contact_ts=d.get("last_contact_ts", 0.0),
            created_at=d.get("created_at", time.time()),
        )


def _path(player_name: str) -> str:
    os.makedirs(SCENE_STATE_DIR, exist_ok=True)
    return os.path.join(SCENE_STATE_DIR, f"{player_name.lower()}.json")


def load_or_create(player_name: str) -> SceneState:
    path = _path(player_name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return SceneState.from_dict(json.load(f))
        except Exception as e:
            logger.warning(f"Could not load scene state for {player_name}: {e}. Fresh.")
    return SceneState(player_name=player_name, created_at=time.time())


def save(state: SceneState) -> None:
    try:
        with open(_path(state.player_name), "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save scene state for {state.player_name}: {e}")


def update_from_contact(state: SceneState, character, dm_response: str) -> None:
    """Mutate `state` after a DM exchange. Bumps scene_id on room change,
    extracts NPC names from the Voice's response, advances timestamps."""
    now = time.time()
    current_room = getattr(getattr(character, "room", None), "vnum", 0) or 0
    if current_room and current_room != state.last_room_vnum:
        state.scene_id += 1
        state.last_room_vnum = current_room
    state.last_contact_ts = now
    # Heuristic NPC extraction: grab Title-Case-followed-by-said / asks / replies / Title-Case-in-quotes-attribution
    import re
    names = set(state.active_npcs)
    # pattern: <Name> says/asks/replies/hisses/murmurs
    for m in re.finditer(r'\b([A-Z][a-zA-Z\-\']{2,}(?:\s+[A-Z][a-zA-Z\-\']{2,}){0,2})\b\s+(?:says|asks|replies|murmurs|mutters|hisses|whispers|growls|laughs)', dm_response):
        names.add(m.group(1))
    # pattern: "..." <Name> said
    for m in re.finditer(r'["\u201c][^"\u201d]+["\u201d]\s+([A-Z][a-zA-Z\-\']{2,}(?:\s+[A-Z][a-zA-Z\-\']{2,}){0,2})\s+(?:said|asked|replied)', dm_response):
        names.add(m.group(1))
    # cap list to keep it readable
    state.active_npcs = sorted(names)[-20:]


def recap_since_last(state: SceneState, player_name: str, max_events: int = 10) -> str:
    """Summarize what happened since the last DM contact. Returns a short
    string suitable for the DM's context block, or '' if nothing notable."""
    if state.last_contact_ts <= 0:
        return ""
    try:
        from src.event_log import get_recent_events
        events = get_recent_events(count=80, player=player_name)
    except Exception:
        return ""
    if not events:
        return ""
    since = [e for e in events if e.get("timestamp", 0) > state.last_contact_ts]
    if not since:
        return ""
    # Group by type and count
    from collections import Counter
    type_counts = Counter(e.get("type", "?") for e in since)
    # Format: "{count} kills, 2 new rooms explored, 1 quest turned in"
    parts = []
    for t, c in type_counts.most_common():
        parts.append(f"{c} {t.replace('_',' ')}")
    tail = since[-max_events:]
    detail_lines = []
    for e in tail:
        t = e.get("type", "?")
        d = e.get("data", {})
        summary = d.get("summary") or d.get("target") or d.get("room") or d.get("mob") or ""
        detail_lines.append(f"  - {t}: {summary}")
    return f"Since last contact: {', '.join(parts)}.\n" + "\n".join(detail_lines)
