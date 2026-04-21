"""
Companions — Phase 5 of DM Player.

A Companion is a persistent NPC tied to a specific player through the DM
Player's story. The Companion exists as a mob in the world (we reuse the
captive roster at vnums 4315-4345 by default) and has a per-player
relationship state machine: Met → Trust → Bond → Devotion → {Sacrifice,
Loss, Union}.

The DM Player can:
  - introduce(): pick a candidate from the captive pool (or any mob vnum)
                 and bind them to the player as their Companion.
  - advance_bond(): move the state machine forward by one step.
  - adjust_affinity(): fine-grained +/- nudge (5 per step; Yellow risk).
  - retire(): Sacrifice, Loss, or Union — closes the arc.

Companion records persist at data/companions/<player>.json.

This module does NOT spawn new mobs. Spawn + placement is handled by the
existing mob system; Companions are recorded against already-existing
mob vnums. This keeps Phase 5 simple and canon-safe.
"""

import json
import os
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

logger = logging.getLogger("OrekaMUD.DM.Companions")

COMPANIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "companions")

# Relationship states. Forward progress is one-step; retirement states are terminal.
STATES = ["met", "trust", "bond", "devotion", "sacrifice", "loss", "union"]
ADVANCING = ["met", "trust", "bond", "devotion"]
TERMINAL = ["sacrifice", "loss", "union"]

# Affinity points per advance. Phase 12 will add consent-gated romance path.
AFFINITY_STEP = 5
AFFINITY_MAX = 100


@dataclass
class Companion:
    player_name: str
    mob_vnum: int
    mob_name: str
    archetype: str        # "captive", "stray", "wounded_stranger", "oracle", etc.
    state: str = "met"    # from STATES
    affinity: int = 10    # 0-100
    shared_scenes: int = 0
    introduced_at: float = 0.0
    last_interaction: float = 0.0
    romance_consent: bool = False   # Phase 12 gate, set via rpsheet later
    backstory_hook: str = ""        # one-sentence why this companion matters to THIS player
    notes: List[str] = field(default_factory=list)  # DM running notes

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Companion":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class CompanionRoster:
    player_name: str
    companions: List[Companion] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"player_name": self.player_name,
                "companions": [c.to_dict() for c in self.companions]}

    @classmethod
    def from_dict(cls, d: dict) -> "CompanionRoster":
        return cls(
            player_name=d["player_name"],
            companions=[Companion.from_dict(c) for c in d.get("companions", [])],
        )


def _path(player_name: str) -> str:
    os.makedirs(COMPANIONS_DIR, exist_ok=True)
    return os.path.join(COMPANIONS_DIR, f"{player_name.lower()}.json")


def load_or_create(player_name: str) -> CompanionRoster:
    path = _path(player_name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return CompanionRoster.from_dict(json.load(f))
        except Exception as e:
            logger.warning(f"Could not load companions for {player_name}: {e}. Fresh.")
    return CompanionRoster(player_name=player_name)


def save(roster: CompanionRoster) -> None:
    try:
        with open(_path(roster.player_name), "w", encoding="utf-8") as f:
            json.dump(roster.to_dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save companions for {roster.player_name}: {e}")


# ----- Candidate selection ------------------------------------------------

# The 31 named captives we authored live in vnums 4315-4345 with the
# 'captive' and 'quest_giver' flags. They're a natural Companion pool.
CAPTIVE_VNUM_RANGE = (4315, 4345)


def _load_captive_pool() -> List[dict]:
    """Return mob dicts from mobs.json that match the captive pool."""
    path = os.path.join(os.path.dirname(__file__), "..", "data", "mobs.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        logger.error(f"Cannot load mobs.json: {e}")
        return []
    rows = d if isinstance(d, list) else d.get("mobs", [])
    lo, hi = CAPTIVE_VNUM_RANGE
    pool = []
    for m in rows:
        v = m.get("vnum", 0)
        if lo <= v <= hi and "captive" in (m.get("flags") or []):
            pool.append(m)
    return pool


def _roster_vnums_globally() -> set:
    """Vnums already claimed by any player's roster — to avoid double-binding."""
    claimed = set()
    if not os.path.isdir(COMPANIONS_DIR):
        return claimed
    for fn in os.listdir(COMPANIONS_DIR):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(COMPANIONS_DIR, fn), "r", encoding="utf-8") as f:
                d = json.load(f)
            for c in d.get("companions", []):
                if c.get("state") not in TERMINAL:
                    claimed.add(c.get("mob_vnum"))
        except Exception:
            continue
    return claimed


def candidate_for(character, culture_hint: str = "") -> Optional[dict]:
    """Pick a captive that is not already bound to any active Companion.
    Optional culture_hint matches keywords in the mob name (Pekakarlik,
    Mytroan, Orean, Taraf-Imro, Eruskan, Visetri, Kovaka, Rarozhki, Hasura).
    """
    pool = _load_captive_pool()
    if not pool:
        return None
    claimed = _roster_vnums_globally()
    available = [m for m in pool if m.get("vnum") not in claimed]
    if not available:
        return None
    if culture_hint:
        culture_hint = culture_hint.lower()
        preferred = [m for m in available if culture_hint in m.get("name", "").lower()]
        if preferred:
            return preferred[0]
    return available[0]


# ----- DM-facing operations ----------------------------------------------

def introduce(player_name: str, character, archetype: str = "captive",
              backstory_hook: str = "", culture_hint: str = "",
              mob_vnum: Optional[int] = None) -> Optional[Companion]:
    """Bind a mob to the player as a Companion.

    If mob_vnum is given, use that exact mob. Otherwise pick from the
    captive pool, optionally biased by culture_hint.

    Returns the new Companion record, or None if no candidate exists
    (rare; means the pool is exhausted for this world).
    """
    roster = load_or_create(player_name)

    if any(c.state not in TERMINAL for c in roster.companions):
        # Phase 5 enforces one active Companion per player.
        logger.info(f"{player_name} already has an active Companion; not introducing.")
        return None

    chosen = None
    if mob_vnum is not None:
        pool = _load_captive_pool()
        for m in pool:
            if m.get("vnum") == mob_vnum:
                chosen = m
                break
    else:
        chosen = candidate_for(character, culture_hint=culture_hint)

    if not chosen:
        return None

    now = time.time()
    comp = Companion(
        player_name=player_name,
        mob_vnum=chosen["vnum"],
        mob_name=chosen.get("name", f"vnum {chosen['vnum']}"),
        archetype=archetype,
        state="met",
        affinity=10,
        introduced_at=now,
        last_interaction=now,
        backstory_hook=backstory_hook,
    )
    roster.companions.append(comp)
    save(roster)
    return comp


def get_active(player_name: str) -> Optional[Companion]:
    roster = load_or_create(player_name)
    for c in roster.companions:
        if c.state not in TERMINAL:
            return c
    return None


def advance_bond(player_name: str, reason: str = "") -> Optional[Companion]:
    """Move the active Companion one step forward in the state machine."""
    active = get_active(player_name)
    if not active:
        return None
    idx = ADVANCING.index(active.state) if active.state in ADVANCING else -1
    if idx < 0 or idx >= len(ADVANCING) - 1:
        return active
    active.state = ADVANCING[idx + 1]
    active.affinity = min(AFFINITY_MAX, active.affinity + AFFINITY_STEP)
    active.last_interaction = time.time()
    if reason:
        active.notes.append(f"[{time.strftime('%Y-%m-%d')}] advanced to {active.state}: {reason}")
    roster = load_or_create(player_name)
    for i, c in enumerate(roster.companions):
        if c.mob_vnum == active.mob_vnum and c.state not in TERMINAL:
            roster.companions[i] = active
            break
    save(roster)
    return active


def adjust_affinity(player_name: str, delta: int, reason: str = "") -> Optional[Companion]:
    """Fine-grained affinity nudge. +/- int. Does not change state."""
    active = get_active(player_name)
    if not active:
        return None
    active.affinity = max(0, min(AFFINITY_MAX, active.affinity + delta))
    active.last_interaction = time.time()
    if reason:
        active.notes.append(f"[{time.strftime('%Y-%m-%d')}] affinity {delta:+d} → {active.affinity}: {reason}")
    roster = load_or_create(player_name)
    for i, c in enumerate(roster.companions):
        if c.mob_vnum == active.mob_vnum and c.state not in TERMINAL:
            roster.companions[i] = active
            break
    save(roster)
    return active


def retire(player_name: str, resolution: str, reason: str = "") -> Optional[Companion]:
    """End the Companion's arc: 'sacrifice', 'loss', or 'union'."""
    if resolution not in TERMINAL:
        raise ValueError(f"resolution must be one of {TERMINAL}")
    active = get_active(player_name)
    if not active:
        return None
    active.state = resolution
    active.notes.append(f"[{time.strftime('%Y-%m-%d')}] retired as {resolution}: {reason}")
    active.last_interaction = time.time()
    roster = load_or_create(player_name)
    for i, c in enumerate(roster.companions):
        if c.mob_vnum == active.mob_vnum and c.state == resolution:
            roster.companions[i] = active
            break
        if c.mob_vnum == active.mob_vnum and c.state not in TERMINAL:
            roster.companions[i] = active
            break
    save(roster)
    return active
