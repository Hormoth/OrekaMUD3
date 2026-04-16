"""Live-map event broker and server.

Runs a dedicated WebSocket server on ``MAP_WS_PORT`` that pushes a
periodic snapshot of the seven tracked overlays to every subscribed
viewer:

    1. Player positions + HP
    2. Active combat rooms
    3. Active stalkers (from the encounter system)
    4. Chat / Shadow-Presence sessions
    5. Wandering gods
    6. Weather + time of day
    7. Error log (pushed immediately via a logging handler)

The snapshot is rebuilt from in-memory world state every
``SNAPSHOT_INTERVAL`` seconds (default 2) and broadcast to all
subscribers.  Error events are forwarded on a separate message type
as they happen.

Admin auth (v1): a single shared token configured via the
``OREKA_MAP_TOKEN`` environment variable.  The viewer must send it as
the first message after connecting.  If unset, a default token is
generated and logged at startup -- admins grab it from the log.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import time
from collections import deque
from typing import Any, Dict, List, Set

logger = logging.getLogger("OrekaMUD.Map")


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAP_WS_PORT = int(os.environ.get("OREKA_MAP_WS_PORT", "8766"))
MAP_WS_HOST = os.environ.get("OREKA_MAP_WS_HOST", "0.0.0.0")
SNAPSHOT_INTERVAL = 2.0          # seconds between full snapshots
ERROR_RING_SIZE = 100            # retained recent errors
AUTH_TIMEOUT = 10.0              # seconds to send auth before disconnect


# ---------------------------------------------------------------------------
# The broker
# ---------------------------------------------------------------------------

class MapEventBroker:
    """Tracks subscribed viewers and broadcasts snapshots / events to them."""

    def __init__(self) -> None:
        self.subscribers: Set[Any] = set()
        self.recent_errors: deque = deque(maxlen=ERROR_RING_SIZE)
        # Shared admin token.  Preference: env > generated random.
        self.token = os.environ.get("OREKA_MAP_TOKEN")
        if not self.token:
            self.token = secrets.token_urlsafe(16)
            logger.warning(
                "Map WS: no OREKA_MAP_TOKEN set, generated one: %s",
                self.token,
            )
        else:
            logger.info("Map WS: using OREKA_MAP_TOKEN from environment")

    async def subscribe(self, ws) -> None:
        self.subscribers.add(ws)
        logger.info("Map WS: subscriber connected (%d total)",
                    len(self.subscribers))

    async def unsubscribe(self, ws) -> None:
        self.subscribers.discard(ws)
        logger.info("Map WS: subscriber disconnected (%d total)",
                    len(self.subscribers))

    async def broadcast(self, payload: dict) -> None:
        if not self.subscribers:
            return
        message = json.dumps(payload, default=str)
        dead: List[Any] = []
        for ws in list(self.subscribers):
            try:
                await ws.send(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.subscribers.discard(ws)

    def record_error(self, record: logging.LogRecord) -> dict:
        entry = {
            "type":      "error",
            "timestamp": time.time(),
            "level":     record.levelname,
            "source":    record.name,
            "message":   record.getMessage(),
        }
        self.recent_errors.append(entry)
        return entry


_broker: MapEventBroker | None = None


def get_broker() -> MapEventBroker:
    global _broker
    if _broker is None:
        _broker = MapEventBroker()
    return _broker


# ---------------------------------------------------------------------------
# Logging bridge -- captures ERROR/WARNING and pushes to viewers
# ---------------------------------------------------------------------------

class MapLogHandler(logging.Handler):
    """Forward ERROR/WARNING log records to map subscribers."""

    def __init__(self, broker: MapEventBroker) -> None:
        super().__init__(level=logging.WARNING)
        self.broker = broker

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = self.broker.record_error(record)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self.broker.broadcast(entry))
        except Exception:
            pass  # never propagate logging errors


def install_log_handler() -> None:
    broker = get_broker()
    root = logging.getLogger()
    handler = MapLogHandler(broker)
    # Keep a simple formatter to avoid duplicate handler registration on reloads
    for h in root.handlers:
        if isinstance(h, MapLogHandler):
            return
    root.addHandler(handler)


# ---------------------------------------------------------------------------
# Snapshot builder -- reads in-memory world state
# ---------------------------------------------------------------------------

def _safe_hp(p) -> Dict[str, int]:
    hp = getattr(p, "hp", None)
    max_hp = getattr(p, "max_hp", None)
    if hp is None or max_hp is None or max_hp <= 0:
        return {"hp": 0, "max_hp": 0}
    return {"hp": int(hp), "max_hp": int(max_hp)}


def _is_in_combat(player, combats: Dict[int, Any]) -> bool:
    room = getattr(player, "room", None)
    if room is None:
        return False
    combat = combats.get(room.vnum)
    if combat is None:
        return False
    return player in combat.combatants


def build_snapshot(world) -> Dict[str, Any]:
    """Compose the full live-view payload from current server state."""
    snapshot: Dict[str, Any] = {
        "type":      "snapshot",
        "timestamp": time.time(),
    }

    # --- time of day + weather ------------------------------------------
    try:
        from src.schedules import get_game_time
        gt = get_game_time()
        snapshot["time_of_day"] = {
            "hour":        int(getattr(gt, "hour", 0)),
            "is_daytime":  bool(getattr(gt, "is_daytime", lambda: True)()),
            "is_nighttime": bool(getattr(gt, "is_nighttime",
                                         lambda: False)()),
        }
    except Exception:
        snapshot["time_of_day"] = {"hour": 0, "is_daytime": True,
                                    "is_nighttime": False}

    try:
        from src.weather import get_weather_manager
        wm = get_weather_manager()
        snapshot["weather"] = dict(getattr(wm, "region_weather", {}) or {})
    except Exception:
        snapshot["weather"] = {}

    # --- combat rooms ---------------------------------------------------
    try:
        from src.combat import _active_combats as combats
    except Exception:
        combats = {}
    snapshot["combat_rooms"] = sorted(int(v) for v in combats.keys())

    # --- players -------------------------------------------------------
    players_out: List[Dict[str, Any]] = []
    for p in getattr(world, "players", []) or []:
        if getattr(p, "is_ai", False):
            continue
        room = getattr(p, "room", None)
        if room is None:
            continue
        vitals = _safe_hp(p)
        players_out.append({
            "name":       getattr(p, "name", "?"),
            "level":      int(getattr(p, "level", 1)),
            "room_vnum":  int(getattr(room, "vnum", 0)),
            "hp":         vitals["hp"],
            "max_hp":     vitals["max_hp"],
            "in_combat":  _is_in_combat(p, combats),
            "in_chat":    bool(getattr(p, "active_chat_session", None)),
            "afk":        bool(getattr(p, "afk", False)),
        })
    snapshot["players"] = players_out

    # --- stalkers ------------------------------------------------------
    stalkers_out: List[Dict[str, Any]] = []
    try:
        from src.encounters import get_encounter_manager
        mgr = get_encounter_manager()
        for s in getattr(mgr, "active", []) or []:
            target = getattr(s, "target", None)
            target_room = getattr(target, "room", None) if target else None
            stalkers_out.append({
                "name":            getattr(s.mob, "name", "stalker"),
                "cr":              getattr(s.mob, "cr", None),
                "room_vnum":       int(getattr(s.mob, "room_vnum", 0)),
                "target":          getattr(target, "name", "?"),
                "target_room":     int(getattr(target_room, "vnum", 0))
                                    if target_room else None,
                "region":          getattr(s, "region", "?"),
                "engaged":         bool(getattr(s, "engaged", False)),
                "warnings_sent":   int(getattr(s, "warnings_sent", 0)),
            })
    except Exception:
        pass
    snapshot["stalkers"] = stalkers_out

    # --- chat sessions -------------------------------------------------
    chat_out: List[Dict[str, Any]] = []
    for p in getattr(world, "players", []) or []:
        if getattr(p, "is_ai", False):
            continue
        session = getattr(p, "active_chat_session", None)
        if session is None:
            continue
        npc = getattr(session, "npc", None)
        npc_name = getattr(npc, "name", "?") if npc else "?"
        room = getattr(p, "room", None)
        chat_out.append({
            "player":    getattr(p, "name", "?"),
            "npc":       npc_name,
            "room_vnum": int(getattr(room, "vnum", 0)) if room else None,
            "state":     getattr(session, "state", "active"),
        })
    snapshot["chat_sessions"] = chat_out

    # --- wandering gods ------------------------------------------------
    gods_out: List[Dict[str, Any]] = []
    try:
        from src.wandering_gods import get_wandering_gods
        wg = get_wandering_gods()
        gods = getattr(wg, "wanderers", None) or getattr(wg, "_wanderers",
                                                          None) or {}
        if isinstance(gods, dict):
            god_iter = gods.values()
        else:
            god_iter = list(gods)
        for g in god_iter:
            gods_out.append({
                "name":       getattr(g, "name", None) or
                              getattr(g, "deity_name", "?"),
                "room_vnum":  int(getattr(g, "current_vnum", 0) or 0),
            })
    except Exception:
        pass
    snapshot["gods"] = gods_out

    # --- recent errors (last 10) ---------------------------------------
    broker = get_broker()
    snapshot["recent_errors"] = list(broker.recent_errors)[-10:]

    return snapshot


# ---------------------------------------------------------------------------
# Periodic broadcaster task
# ---------------------------------------------------------------------------

async def snapshot_broadcast_loop(world) -> None:
    """Build and push a snapshot every SNAPSHOT_INTERVAL seconds."""
    broker = get_broker()
    while True:
        try:
            await asyncio.sleep(SNAPSHOT_INTERVAL)
            if not broker.subscribers:
                continue  # no viewers -- skip the work
            snap = build_snapshot(world)
            await broker.broadcast(snap)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("Map WS snapshot error: %s", e)


# ---------------------------------------------------------------------------
# WebSocket handler + server
# ---------------------------------------------------------------------------

async def _handle_client(ws, world) -> None:
    broker = get_broker()
    try:
        # First message must be: {"type": "auth", "token": "..."}
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=AUTH_TIMEOUT)
        except asyncio.TimeoutError:
            await ws.close(code=4001, reason="auth timeout")
            return
        try:
            payload = json.loads(raw)
        except Exception:
            await ws.close(code=4002, reason="invalid auth json")
            return
        if payload.get("type") != "auth" or \
           payload.get("token") != broker.token:
            await ws.close(code=4003, reason="auth failed")
            return

        # Accepted.  Send a hello + initial snapshot, then register.
        await ws.send(json.dumps({"type": "hello",
                                  "interval": SNAPSHOT_INTERVAL}))
        try:
            await ws.send(json.dumps(build_snapshot(world), default=str))
        except Exception:
            pass
        await broker.subscribe(ws)

        # Hold the connection open; we don't expect further messages for v1.
        try:
            async for _ in ws:
                pass  # ignore incoming messages
        except Exception:
            pass
    finally:
        await broker.unsubscribe(ws)


async def start_map_ws_server(world) -> None:
    """Start the map WebSocket server.  Called from main.py."""
    import websockets

    async def handler(ws):
        await _handle_client(ws, world)

    logger.info("Map WS: starting on ws://%s:%d (subscribe with auth token)",
                MAP_WS_HOST, MAP_WS_PORT)
    async with websockets.serve(handler, MAP_WS_HOST, MAP_WS_PORT,
                                ping_interval=30, ping_timeout=10):
        await asyncio.Future()  # run forever
