"""
CanonGuard — Phase 3 of DM Player.

Every mutation the DM Player proposes runs through gate() first. Classifies
into Green/Yellow/Orange/Red, enforces rate limits, writes an audit journal,
and queues Orange/Red as admin proposals. The DM Player can call gate() to
know whether to proceed, defer, or abort.

Risk classes:
  Green  — auto-apply, logged only. Narration, ambient flavor, scene-local
           state. No persistent world change.
  Yellow — auto-apply with rate limits + player-visible "improv" marker.
           Transient mob spawn (TTL), ad-hoc exit in transient zone,
           modest XP grant, companion affinity nudge.
  Orange — queued as admin proposal. Auto-applies after veto window if no
           admin objects. Writing to hidden_quests.json, killing a
           Companion, altering canon NPC persona, granting high-tier item,
           altering another player's arc sheet.
  Red    — admin signature required, never auto. Modifying canon rooms,
           retconning closed arcs, touching other-player sessions outside
           this scene, unlocking gated zones.

Future phases add: Veil admin panel (Phase 8), Scribe sync cross-check
(Phase 7), consequence cascade propagation (Phase 13).
"""

import json
import os
import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Tuple

logger = logging.getLogger("OrekaMUD.DM.Guard")

_BASE = os.path.join(os.path.dirname(__file__), "..", "data")
AUDIT_DIR = os.path.join(_BASE, "dm_audit")
PROPOSALS_DIR = os.path.join(_BASE, "dm_proposals")

# Auto-apply veto window for Orange actions (seconds). Admin can veto before
# this window elapses via a (future) admin command / Veil panel. In Phase 3
# no such veto interface exists yet, so Orange effectively still auto-applies
# after the delay — but the proposal file is written so admins can find it.
ORANGE_VETO_WINDOW = 120.0


# Action classification table. Unknown actions default to Orange (conservative).
GREEN_ACTIONS = {
    "narrate", "voice_npc", "set_tone", "whisper_aside", "ambient_injection",
    "ask_for_check", "rule_adjudication", "seed_plant", "seed_retire",
    "scene_detail", "read_rpsheet", "read_event_log", "read_arc",
    "recap", "group_check", "arc_check_green",
}
YELLOW_ACTIONS = {
    "spawn_transient_mob", "transient_exit", "room_condition_apply",
    "grant_small_xp", "companion_affinity_nudge", "foreshadow_harbinger",
    "twist_inject", "morale_check", "mob_force_action", "mob_buff_temp",
    "mob_debuff_temp", "grant_memento", "grant_scene_reward",
}
ORANGE_ACTIONS = {
    "materialize_quest", "spawn_companion", "kill_companion",
    "modify_ai_persona", "grant_item_tier_high", "alter_arc_other_player",
    "permanent_mob_buff", "permanent_mob_debuff", "advance_relationship_state",
    "cascade_event", "faction_rep_shift", "grant_xp_large", "add_quest_objective",
    "unlock_hidden_objective",
}
RED_ACTIONS = {
    "modify_canon_room", "retcon_closed_arc", "touch_other_session",
    "unlock_gated_zone", "delete_mob_permanent", "rename_canon_npc",
}

RISK_ORDER = ["green", "yellow", "orange", "red"]

# Per-player per-hour rate limits, by risk class.
_RATE_LIMITS = {
    "green":  120,
    "yellow": 20,
    "orange": 6,
    "red":    0,   # 0 = never auto; must go through admin
}

# In-memory action history: {player_name: [(ts, risk), ...]} rolling
_history: Dict[str, list] = {}


def _ensure_dirs() -> None:
    os.makedirs(AUDIT_DIR, exist_ok=True)
    os.makedirs(PROPOSALS_DIR, exist_ok=True)


def classify(action: str) -> str:
    if action in GREEN_ACTIONS:
        return "green"
    if action in YELLOW_ACTIONS:
        return "yellow"
    if action in ORANGE_ACTIONS:
        return "orange"
    if action in RED_ACTIONS:
        return "red"
    return "orange"  # conservative default


def _audit_path() -> str:
    _ensure_dirs()
    return os.path.join(AUDIT_DIR, f"{time.strftime('%Y%m%d')}.jsonl")


def journal(player_name: str, action: str, risk: str, args: dict,
            outcome: str, proposal_id: Optional[str] = None) -> None:
    entry = {
        "ts": time.time(),
        "player": player_name,
        "action": action,
        "risk": risk,
        "args": args,
        "outcome": outcome,
        "proposal_id": proposal_id,
    }
    try:
        with open(_audit_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to journal DM action {action}: {e}")


def _rate_ok(player_name: str, risk: str) -> bool:
    now = time.time()
    cutoff = now - 3600.0
    history = _history.setdefault(player_name, [])
    # prune
    history[:] = [(t, r) for (t, r) in history if t > cutoff]
    count = sum(1 for (_, r) in history if r == risk)
    limit = _RATE_LIMITS.get(risk, 0)
    return count < limit


def _record(player_name: str, risk: str) -> None:
    _history.setdefault(player_name, []).append((time.time(), risk))


def _proposal_path(proposal_id: str) -> str:
    _ensure_dirs()
    return os.path.join(PROPOSALS_DIR, f"{proposal_id}.json")


def _queue_proposal(player_name: str, action: str, args: dict, risk: str) -> str:
    pid = uuid.uuid4().hex[:12]
    body = {
        "proposal_id": pid,
        "created_at": time.time(),
        "auto_apply_at": time.time() + ORANGE_VETO_WINDOW if risk == "orange" else None,
        "player": player_name,
        "action": action,
        "risk": risk,
        "args": args,
        "status": "pending",
    }
    try:
        with open(_proposal_path(pid), "w", encoding="utf-8") as f:
            json.dump(body, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to queue proposal {pid}: {e}")
    return pid


@dataclass
class GateResult:
    allowed: bool
    risk: str
    reason: str
    proposal_id: Optional[str] = None
    defer_seconds: float = 0.0


def gate(player_name: str, action: str, args: Optional[dict] = None) -> GateResult:
    """Ask permission before executing a DM-originated mutation.

    Returns (allowed, risk, reason, proposal_id, defer_seconds). The DM Player
    should:
      - If allowed and defer_seconds == 0: execute the mutation, then call
        journal(..., outcome='applied').
      - If allowed and defer_seconds > 0 (Orange): queue via return value,
        schedule application after defer_seconds, journal 'queued'.
      - If not allowed: inform the player via narration ('something stops
        you from…'), journal 'blocked'.
    """
    args = args or {}
    risk = classify(action)

    if risk == "red":
        pid = _queue_proposal(player_name, action, args, risk)
        journal(player_name, action, risk, args, "blocked_red", pid)
        return GateResult(False, risk, "Red-tier action requires admin signature.", pid, 0.0)

    if not _rate_ok(player_name, risk):
        journal(player_name, action, risk, args, "blocked_rate_limit")
        return GateResult(False, risk,
                          f"{risk.title()} rate limit exceeded (per-hour). Try again later.",
                          None, 0.0)

    if risk == "orange":
        pid = _queue_proposal(player_name, action, args, risk)
        _record(player_name, risk)
        journal(player_name, action, risk, args, "queued_orange", pid)
        return GateResult(True, risk, "Queued; auto-applies after veto window.",
                          pid, ORANGE_VETO_WINDOW)

    # green or yellow: auto-allowed
    _record(player_name, risk)
    return GateResult(True, risk, "auto_allowed", None, 0.0)


def list_pending_proposals(include_applied: bool = False) -> list:
    """Admin helper: return current proposals."""
    _ensure_dirs()
    out = []
    for fn in sorted(os.listdir(PROPOSALS_DIR)):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(PROPOSALS_DIR, fn), "r", encoding="utf-8") as f:
                p = json.load(f)
            if p.get("status") != "pending" and not include_applied:
                continue
            out.append(p)
        except Exception:
            continue
    return out


def veto_proposal(proposal_id: str, admin_name: str, reason: str = "") -> bool:
    """Admin vetoes a pending proposal. Returns True if vetoed, False if
    not found or already resolved."""
    path = _proposal_path(proposal_id)
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            p = json.load(f)
        if p.get("status") != "pending":
            return False
        p["status"] = "vetoed"
        p["vetoed_by"] = admin_name
        p["vetoed_at"] = time.time()
        p["veto_reason"] = reason
        with open(path, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2, ensure_ascii=False)
        journal(p.get("player", "?"), p.get("action", "?"), p.get("risk", "?"),
                p.get("args", {}), f"vetoed_by:{admin_name}:{reason}", proposal_id)
        return True
    except Exception as e:
        logger.error(f"Failed to veto {proposal_id}: {e}")
        return False


def mark_applied(proposal_id: str) -> None:
    """Called once an Orange proposal's defer window has passed and it's
    actually executed. Updates the proposal file status."""
    path = _proposal_path(proposal_id)
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            p = json.load(f)
        if p.get("status") == "pending":
            p["status"] = "applied"
            p["applied_at"] = time.time()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(p, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to mark {proposal_id} applied: {e}")
