"""
MCP Bridge — Internal REST API for OrekaMUD3.
Allows the Veil MCP server to read game state and trigger events.
Runs on port 8001, bound to 127.0.0.1 (local only).
"""
import asyncio
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logger = logging.getLogger("OrekaMUD.MCPBridge")

# Reference to the world object — set by main.py on startup
_world = None
_event_loop = None
MCP_PORT = 8001


def set_event_loop(loop):
    """Store the main async event loop for cross-thread coroutine scheduling."""
    global _event_loop
    _event_loop = loop


def set_world(world):
    """Called by main.py to give the bridge access to the world."""
    global _world
    _world = world


class MCPRequestHandler(BaseHTTPRequestHandler):
    """Handle REST API requests from the MCP server."""

    def log_message(self, format, *args):
        """Suppress default HTTP logging — use our logger instead."""
        logger.debug(f"MCP Bridge: {format % args}")

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))

    def _read_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        return {}

    def do_GET(self):
        global _world
        if not _world:
            self._send_json({"error": "World not initialized"}, 503)
            return

        path = self.path.strip('/')
        parts = path.split('/')

        # GET /world/state
        if path == "world/state":
            self._send_json({
                "player_count": len(_world.players),
                "room_count": len(_world.rooms),
                "mob_count": len(_world.mobs),
                "players": [p.name for p in _world.players if not getattr(p, 'is_ai', False)]
            })
            return

        # GET /room/<vnum>
        if len(parts) == 2 and parts[0] == "room":
            try:
                vnum = int(parts[1])
                room = _world.rooms.get(vnum)
                if not room:
                    self._send_json({"error": f"Room {vnum} not found"}, 404)
                    return

                from src.shadow_presence import shadow_manager
                shadows = shadow_manager.get_by_room(vnum)

                self._send_json({
                    "vnum": room.vnum,
                    "name": room.name,
                    "description": room.description[:500] if room.description else "",
                    "exits": list(room.exits.keys()),
                    "flags": getattr(room, 'flags', []),
                    "effects": getattr(room, 'effects', []),
                    "players": [p.name for p in room.players],
                    "mobs": [m.name for m in room.mobs if hasattr(m, 'alive') and m.alive],
                    "shadows": [s.player_name for s in shadows]
                })
                return
            except ValueError:
                self._send_json({"error": "Invalid room vnum"}, 400)
                return

        # GET /player/<name>
        if len(parts) == 2 and parts[0] == "player":
            name = parts[1]
            player = None
            for p in _world.players:
                if p.name.lower() == name.lower():
                    player = p
                    break

            if not player:
                self._send_json({"error": f"Player {name} not found or offline"}, 404)
                return

            self._send_json({
                "name": player.name,
                "race": getattr(player, 'race', '?'),
                "class": getattr(player, 'char_class', '?'),
                "level": getattr(player, 'level', 1),
                "hp": getattr(player, 'hp', 0),
                "max_hp": getattr(player, 'max_hp', 0),
                "ac": getattr(player, 'ac', 10),
                "gold": getattr(player, 'gold', 0),
                "room_vnum": player.room.vnum if hasattr(player, 'room') and player.room else None,
                "deity": getattr(player, 'deity', None),
                "alignment": getattr(player, 'alignment', None),
                "elemental_affinity": getattr(player, 'elemental_affinity', None),
                "reputation": dict(getattr(player, 'reputation', {})),
                "guild": getattr(player, 'guild_name', None),
                "guild_rank": getattr(player, 'guild_rank', None),
            })
            return

        # GET /npc/<vnum>
        if len(parts) == 2 and parts[0] == "npc":
            try:
                vnum = int(parts[1])
                mob = _world.mobs.get(vnum)
                if not mob:
                    self._send_json({"error": f"NPC {vnum} not found"}, 404)
                    return
                self._send_json({
                    "vnum": mob.vnum,
                    "name": mob.name,
                    "level": getattr(mob, 'level', 1),
                    "type": getattr(mob, 'type_', 'Unknown'),
                    "cr": getattr(mob, 'cr', 0),
                    "alignment": getattr(mob, 'alignment', 'Unknown'),
                    "alive": getattr(mob, 'alive', True),
                    "description": getattr(mob, 'description', '')[:500],
                    "flags": getattr(mob, 'flags', []),
                })
                return
            except ValueError:
                self._send_json({"error": "Invalid NPC vnum"}, 400)
                return

        # GET /events/recent[?count=N&type=X&player=X&region=X]
        if parts[0] == "events" and (len(parts) == 1 or parts[1] == "recent"):
            from src.event_log import get_recent_events
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            count = int(params.get('count', [100])[0])
            event_type = params.get('type', [None])[0]
            player = params.get('player', [None])[0]
            region = params.get('region', [None])[0]
            events = get_recent_events(count=count, event_type=event_type, player=player, region=region)
            self._send_json({"events": events, "count": len(events)})
            return

        # GET /shadows
        if path == "shadows":
            from src.shadow_presence import shadow_manager
            shadows = shadow_manager.get_all()
            self._send_json({
                "shadows": [{
                    "player_id": s.player_id,
                    "player_name": s.player_name,
                    "npc_name": s.npc_name,
                    "room_vnum": s.room_vnum,
                    "materialized": s.materialized,
                } for s in shadows.values()]
            })
            return

        # GET /chat/active — list active chat sessions
        if path == "chat/active":
            sessions = []
            for player in _world.players:
                cs = getattr(player, 'active_chat_session', None)
                if cs and not getattr(cs, 'ended', False):
                    sessions.append({
                        "session_id": cs.session_id,
                        "player": cs.player_name,
                        "npc_vnum": cs.npc_vnum,
                        "npc_name": cs.npc_name,
                        "anchor_room_vnum": cs.anchor_room_vnum,
                        "anchor_room_name": cs.anchor_room_name,
                        "anchor_region": cs.anchor_region,
                        "started_at": cs.started_at,
                        "last_active": cs.last_active,
                        "state": getattr(cs, 'state', 'ACTIVE'),
                        "messages_count": len(cs.conversation_history),
                    })
            self._send_json({"sessions": sessions, "count": len(sessions)})
            return

        # GET /chat/<session_id>
        if len(parts) == 2 and parts[0] == "chat":
            sid = parts[1]
            for player in _world.players:
                cs = getattr(player, 'active_chat_session', None)
                if cs and cs.session_id == sid:
                    self._send_json({
                        "session_id": cs.session_id,
                        "player": cs.player_name,
                        "npc_name": cs.npc_name,
                        "npc_vnum": cs.npc_vnum,
                        "anchor_room_vnum": cs.anchor_room_vnum,
                        "anchor_room_name": cs.anchor_room_name,
                        "started_at": cs.started_at,
                        "last_active": cs.last_active,
                        "state": getattr(cs, 'state', 'ACTIVE'),
                        "state_transitions": getattr(cs, 'state_transitions', []),
                        "conversation_history": cs.conversation_history,
                        "world_events_injected": cs.world_events_injected,
                        "game_actions_executed": cs.game_actions_executed,
                    })
                    return
            self._send_json({"error": f"chat session '{sid}' not found"}, 404)
            return

        # GET /arc/sheet/<player_name>[/<arc_id>]
        if len(parts) >= 3 and parts[0] == "arc" and parts[1] == "sheet":
            name = parts[2]
            arc_id = parts[3] if len(parts) >= 4 else None
            target = None
            for p in _world.players:
                if p.name.lower() == name.lower():
                    target = p
                    break
            if not target:
                self._send_json({"error": f"player '{name}' not found online"}, 404)
                return
            arcs = getattr(target, 'arc_sheets', {}) or {}
            if arc_id:
                sheet = arcs.get(arc_id)
                if not sheet:
                    self._send_json({"error": f"player has no arc '{arc_id}'"}, 404)
                    return
                self._send_json(sheet.to_dict() if hasattr(sheet, 'to_dict') else sheet)
            else:
                self._send_json({
                    "player": target.name,
                    "arcs": {
                        aid: (s.to_dict() if hasattr(s, 'to_dict') else s)
                        for aid, s in arcs.items()
                    },
                })
            return

        # GET /arc/stats — aggregate stats
        if path == "arc/stats":
            stats = {}
            for player in _world.players:
                for arc_id, sheet in (getattr(player, 'arc_sheets', None) or {}).items():
                    entry = stats.setdefault(arc_id, {
                        "title": getattr(sheet, 'title', arc_id),
                        "untouched": 0, "aware": 0, "active": 0,
                        "advancing": 0, "resolved": 0, "total": 0,
                    })
                    entry["total"] += 1
                    status = getattr(sheet, 'status', 'untouched')
                    if status in entry:
                        entry[status] += 1
            self._send_json({"arcs": stats})
            return

        self._send_json({"error": "Unknown endpoint", "path": path}, 404)

    def do_POST(self):
        global _world
        if not _world:
            self._send_json({"error": "World not initialized"}, 503)
            return

        path = self.path.strip('/')
        parts = path.split('/')
        body = self._read_body()

        # POST /player/<name>/message
        if len(parts) == 3 and parts[0] == "player" and parts[2] == "message":
            name = parts[1]
            message = body.get("message", "")
            for player in _world.players:
                if player.name.lower() == name.lower():
                    if hasattr(player, '_writer'):
                        try:
                            player._writer.write(f"\n{message}\n")
                        except Exception:
                            pass
                    self._send_json({"status": "delivered"})
                    return
            self._send_json({"status": "player_offline"}, 404)
            return

        # POST /world/event
        if path == "world/event":
            scope = body.get("scope", "global")
            target = body.get("target", "all")
            message = body.get("message", body.get("description", ""))
            effects = body.get("mechanical_effects")

            # Run async broadcast in the main event loop (stored reference)
            from src.events import broadcast_event
            try:
                loop = _event_loop
                if loop is None:
                    self._send_json({"status": "error", "error": "Event loop not initialized"}, 503)
                    return
                future = asyncio.run_coroutine_threadsafe(
                    broadcast_event(_world, scope, target, message, effects), loop
                )
                reached = future.result(timeout=5)
                self._send_json({"status": "triggered", "players_reached": len(reached)})
            except Exception as e:
                self._send_json({"status": "error", "error": str(e)}, 500)
            return

        # POST /player/<name>/reputation
        if len(parts) == 3 and parts[0] == "player" and parts[2] == "reputation":
            name = parts[1]
            faction = body.get("faction")
            amount = body.get("amount", 0)

            for player in _world.players:
                if player.name.lower() == name.lower():
                    try:
                        from src.factions import get_faction_manager
                        fm = get_faction_manager()
                        new_val, _, new_standing, msg = fm.modify_reputation(player, faction, amount, "MCP Bridge")
                        self._send_json({"status": "updated", "new_value": new_val, "standing": new_standing})
                    except Exception as e:
                        self._send_json({"status": "error", "error": str(e)}, 500)
                    return
            self._send_json({"status": "player_offline"}, 404)
            return

        # POST /shadow/create
        if path == "shadow/create":
            from src.shadow_presence import shadow_manager
            shadow = shadow_manager.create(
                player_id=body.get("player_id"),
                player_name=body.get("player_name"),
                npc_id=body.get("npc_id", 0),
                npc_name=body.get("npc_name", "Unknown"),
                room_vnum=body.get("room_vnum", 1000)
            )
            self._send_json({"status": "created", "player_name": shadow.player_name, "room_vnum": shadow.room_vnum})
            return

        # POST /shadow/materialize
        if path == "shadow/materialize":
            from src.shadow_presence import shadow_manager
            shadow = shadow_manager.materialize(body.get("player_id"))
            if shadow:
                self._send_json({"status": "materialized", "room_vnum": shadow.room_vnum})
            else:
                self._send_json({"status": "not_found"}, 404)
            return

        # POST /shadow/remove
        if path == "shadow/remove":
            from src.shadow_presence import shadow_manager
            shadow = shadow_manager.remove(body.get("player_id"))
            self._send_json({"status": "removed" if shadow else "not_found"})
            return

        self._send_json({"error": "Unknown endpoint"}, 404)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def start_mcp_bridge_thread():
    """Start the MCP Bridge HTTP server in a background thread."""
    def run_server():
        server = HTTPServer(('127.0.0.1', MCP_PORT), MCPRequestHandler)
        logger.info(f"MCP Bridge started on 127.0.0.1:{MCP_PORT}")
        server.serve_forever()

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread
