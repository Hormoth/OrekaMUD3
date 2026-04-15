"""
GMCP (Generic Mud Communication Protocol) for OrekaMUD3.
Sends structured JSON data to clients that support it.

Two transport modes:
  1. Telnet — IAC SB 201 <payload> IAC SE  (standard GMCP subnegotiation)
  2. WebSocket — text frame prefixed with "GMCP:" e.g.
       GMCP:Char.Vitals {"hp":45,"hp_max":50,...}

Used by Veil Client for visual panels, and by MudLet/TinTin++ for scripting.
"""

import json
import logging

logger = logging.getLogger("OrekaMUD.GMCP")

# Telnet bytes
IAC = 255   # Interpret As Command
SB = 250    # Subnegotiation Begin
SE = 240    # Subnegotiation End
WILL = 251
WONT = 252
DO = 253
DONT = 254
GMCP_OPT = 201  # GMCP option code


# ---------------------------------------------------------------------------
# GMCPHandler — per-connection handler (telnet transport)
# ---------------------------------------------------------------------------

class GMCPHandler:
    """Manages GMCP state for a single telnet player connection."""

    def __init__(self, writer):
        self.writer = writer
        self.enabled = False
        self.supported_packages = set()

    def negotiate(self):
        """Send WILL GMCP to advertise support. Call on connection."""
        try:
            raw = bytes([IAC, WILL, GMCP_OPT])
            if hasattr(self.writer, '_transport') and self.writer._transport:
                self.writer._transport.write(raw)
            self.enabled = True
        except Exception:
            self.enabled = False

    def handle_do(self):
        """Client responded DO GMCP — they support it."""
        self.enabled = True

    def handle_dont(self):
        """Client responded DONT GMCP — they don't support it."""
        self.enabled = False

    def handle_subnegotiation(self, data):
        """Handle incoming GMCP data from client (e.g., package list)."""
        try:
            text = data.decode('utf-8', errors='replace')
            if text.startswith('Core.Supports.Set'):
                payload = text[len('Core.Supports.Set'):].strip()
                packages = json.loads(payload)
                for pkg in packages:
                    name = pkg.split()[0] if ' ' in pkg else pkg
                    self.supported_packages.add(name)
            elif text.startswith('Core.Hello'):
                pass
        except Exception:
            pass

    # -- low-level emit --

    def emit(self, package, data):
        """Send a GMCP data package over telnet subnegotiation."""
        if not self.enabled:
            return
        try:
            payload = f"{package} {json.dumps(data, separators=(',', ':'))}"
            payload_bytes = payload.encode('utf-8')
            raw = bytes([IAC, SB, GMCP_OPT]) + payload_bytes + bytes([IAC, SE])
            if hasattr(self.writer, '_transport') and self.writer._transport:
                self.writer._transport.write(raw)
        except Exception:
            pass

    # -- high-level emitters (shared logic, delegated to _emit_* helpers) --

    def emit_vitals(self, character):
        self.emit("Char.Vitals", _build_vitals(character))

    def emit_status(self, character):
        self.emit("Char.Status", _build_status(character))

    def emit_factions(self, character):
        self.emit("Char.Factions", _build_factions(character))

    def emit_deity(self, character, at_shrine=False, shrine_name=None):
        self.emit("Char.Deity", _build_deity(character, at_shrine, shrine_name))

    def emit_room(self, room, character=None):
        self.emit("Room.Info", _build_room(room))

    def emit_room_mobs(self, room):
        self.emit("Room.Mobs", _build_room_mobs(room))

    def emit_kin_sense(self, detections, room_modifier="normal", range_ft=60):
        self.emit("Char.KinSense", _build_kin_sense(detections, room_modifier, range_ft))

    def emit_quest(self, character):
        self.emit("Char.Quest", _build_quest(character))


# ---------------------------------------------------------------------------
# WebSocketGMCPHandler — per-connection handler (WebSocket transport)
# ---------------------------------------------------------------------------

class WebSocketGMCPHandler:
    """Manages GMCP state for a single WebSocket player connection.

    Sends GMCP as plain text frames:  ``GMCP:<package> <json>``
    """

    def __init__(self, websocket):
        self.websocket = websocket
        self.enabled = True  # Always enabled for WS — no negotiation needed
        self.supported_packages = set()
        self._send_queue = []  # Buffer if needed

    # -- low-level emit --

    def emit(self, package, data):
        """Send a GMCP package as a prefixed text frame over WebSocket."""
        if not self.enabled:
            return
        try:
            payload = json.dumps(data, separators=(',', ':'))
            message = f"GMCP:{package} {payload}"
            # Use the async send via the event loop
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                asyncio.ensure_future(self._async_send(message), loop=loop)
            except RuntimeError:
                # No running loop; queue the message
                self._send_queue.append(message)
        except Exception as e:
            logger.debug(f"GMCP WS emit error: {e}")

    async def _async_send(self, message):
        """Send a message over the WebSocket connection."""
        try:
            await self.websocket.send(message)
        except Exception:
            self.enabled = False

    def handle_client_message(self, text):
        """Handle incoming GMCP message from WebSocket client.

        WebSocket clients send: ``GMCP:<package> <json>``
        """
        if not text.startswith("GMCP:"):
            return False  # Not a GMCP message
        try:
            rest = text[5:]  # Strip "GMCP:"
            space = rest.find(' ')
            if space == -1:
                package = rest
                payload = {}
            else:
                package = rest[:space]
                payload = json.loads(rest[space + 1:])

            if package == 'Core.Supports.Set':
                if isinstance(payload, list):
                    for pkg in payload:
                        name = pkg.split()[0] if ' ' in pkg else pkg
                        self.supported_packages.add(name)
            elif package == 'Core.Hello':
                pass
            return True
        except Exception:
            return True  # Was GMCP but malformed — still consumed

    # -- high-level emitters --

    def emit_vitals(self, character):
        self.emit("Char.Vitals", _build_vitals(character))

    def emit_status(self, character):
        self.emit("Char.Status", _build_status(character))

    def emit_factions(self, character):
        self.emit("Char.Factions", _build_factions(character))

    def emit_deity(self, character, at_shrine=False, shrine_name=None):
        self.emit("Char.Deity", _build_deity(character, at_shrine, shrine_name))

    def emit_room(self, room, character=None):
        self.emit("Room.Info", _build_room(room))

    def emit_room_mobs(self, room):
        self.emit("Room.Mobs", _build_room_mobs(room))

    def emit_kin_sense(self, detections, room_modifier="normal", range_ft=60):
        self.emit("Char.KinSense", _build_kin_sense(detections, room_modifier, range_ft))

    def emit_quest(self, character):
        self.emit("Char.Quest", _build_quest(character))


# ---------------------------------------------------------------------------
# Shared data-building helpers (transport-agnostic)
# ---------------------------------------------------------------------------

def _build_vitals(character):
    """Build Char.Vitals payload."""
    from src.character import XP_TABLE
    tnl = max(0, XP_TABLE.get(character.level + 1, 0) - getattr(character, 'xp', 0))
    return {
        "hp": character.hp,
        "hp_max": character.max_hp,
        "ac": character.ac,
        "mv": getattr(character, 'move', 100),
        "mv_max": getattr(character, 'max_move', 100),
        "gold": getattr(character, 'gold', 0),
        "tnl": tnl,
        "level": character.level,
    }


def _build_status(character):
    """Build Char.Status payload — active conditions and basic info."""
    conditions = list(getattr(character, 'conditions', set()))
    conditions += list(getattr(character, 'active_conditions', {}).keys())
    divine = getattr(character, 'divine_buffs', {})
    if divine and divine.get('duration', 0) > 0:
        conditions.append("Blessed")

    spells = {}
    spd = getattr(character, 'spells_per_day', {})
    for lvl, remaining in spd.items():
        spells[str(lvl)] = remaining

    return {
        "conditions": conditions,
        "spells": spells,
        "level": character.level,
        "class": getattr(character, 'char_class', 'Unknown'),
        "race": getattr(character, 'race', 'Unknown'),
    }


def _build_factions(character):
    """Build Char.Factions payload — all faction reputation values."""
    rep = getattr(character, 'reputation', {})
    return dict(rep)


def _build_deity(character, at_shrine=False, shrine_name=None):
    """Build Char.Deity payload — patron, shrine status, divine buffs."""
    divine = getattr(character, 'divine_buffs', {})
    buffs = []
    if divine and divine.get('duration', 0) > 0:
        buffs.append(divine.get('deity', 'Divine Blessing'))

    return {
        "patron": getattr(character, 'deity', None),
        "at_shrine": at_shrine,
        "shrine_name": shrine_name,
        "active_buffs": buffs,
    }


def _build_room(room):
    """Build Room.Info payload — room data for mapping and display."""
    effects = []
    for e in getattr(room, 'effects', []):
        effects.append(e.get('type', 'unknown') if isinstance(e, dict) else str(e))

    vnum = room.vnum
    if vnum < 4000:
        region = "chapel"
    elif vnum < 5000:
        region = "custos_do_aeternos"
    elif vnum < 6000:
        region = "kinsweave"
    elif vnum < 7000:
        region = "tidebloom_reach"
    elif vnum < 8000:
        region = "eternal_steppe"
    elif vnum < 9000:
        region = "infinite_desert"
    elif vnum < 10000:
        region = "deepwater_marches"
    elif vnum < 11000:
        region = "twin_rivers"
    elif vnum < 11200:
        region = "wilderness"
    elif vnum < 13000:
        region = "gatefall_reach"
    elif vnum < 13100:
        region = "chainless_legion"
    else:
        region = "deepwater_expansion"

    return {
        "vnum": vnum,
        "name": room.name,
        "description": getattr(room, 'description', ''),
        "region": region,
        "exits": list(room.exits.keys()),
        "effects": effects,
        "terrain": getattr(room, 'terrain', None),
        "area": region,
    }


def _build_room_mobs(room):
    """Build Room.Mobs payload — mobs in the room with health state."""
    mobs = []
    for mob in getattr(room, 'mobs', []):
        if not getattr(mob, 'alive', True):
            continue
        hp = getattr(mob, 'hp', 0)
        max_hp = getattr(mob, 'max_hp', 1)
        if max_hp <= 0:
            max_hp = 1
        pct = (hp / max_hp) * 100

        if pct >= 100:
            state = "unhurt"
        elif pct >= 75:
            state = "lightly wounded"
        elif pct >= 50:
            state = "wounded"
        elif pct >= 25:
            state = "badly wounded"
        elif pct > 0:
            state = "near death"
        else:
            state = "dead"

        mobs.append({
            "name": mob.name,
            "hp_state": state,
            "level": getattr(mob, 'level', 0),
            "vnum": getattr(mob, 'vnum', 0),
        })
    return {"mobs": mobs}


def _build_kin_sense(detections, room_modifier="normal", range_ft=60):
    """Build Char.KinSense payload."""
    return {
        "detections": detections,
        "room_modifier": room_modifier,
        "range_ft": range_ft,
    }


def _build_quest(character):
    """Build Char.Quest payload — active and completed quests."""
    active = []
    completed = []
    quest_log = getattr(character, 'quest_log', None)
    if quest_log and hasattr(quest_log, 'active_quests'):
        for qid, aq in quest_log.active_quests.items():
            entry = {"id": str(qid), "state": aq.state.value if hasattr(aq.state, 'value') else str(aq.state)}
            # Try to get quest name from the quest manager
            try:
                from src.quests import get_quest_manager
                qm = get_quest_manager()
                quest = qm.get_quest(qid)
                if quest:
                    entry["name"] = quest.name
            except Exception:
                pass
            active.append(entry)
    if quest_log and hasattr(quest_log, 'completed_quests'):
        completed = [str(qid) for qid in quest_log.completed_quests]

    return {
        "active": active,
        "completed": completed,
    }


# ---------------------------------------------------------------------------
# Handler Registry — maps character name -> handler (telnet or WS)
# ---------------------------------------------------------------------------

_handlers = {}  # {character_name: GMCPHandler | WebSocketGMCPHandler}


def get_handler(character):
    """Get GMCP handler for a character (telnet or WebSocket)."""
    name = getattr(character, 'name', None)
    if name and name in _handlers:
        return _handlers[name]
    return None


def register_handler(character, writer):
    """Register a telnet GMCP handler for a new connection."""
    handler = GMCPHandler(writer)
    handler.negotiate()
    _handlers[character.name] = handler
    return handler


def register_ws_handler(character, websocket):
    """Register a WebSocket GMCP handler for a new connection."""
    handler = WebSocketGMCPHandler(websocket)
    _handlers[character.name] = handler
    return handler


def unregister_handler(character):
    """Remove handler on disconnect."""
    name = getattr(character, 'name', None)
    if name:
        _handlers.pop(name, None)


# ---------------------------------------------------------------------------
# Convenience functions — emit from anywhere with just a character reference
# ---------------------------------------------------------------------------

def emit(character, package, data=None):
    """Convenience: emit a GMCP package for a character.

    If ``data`` is provided, it is sent directly as the package payload.
    Otherwise, the appropriate builder is called based on the package name.
    """
    handler = get_handler(character)
    if not handler:
        return

    if data is not None:
        handler.emit(package, data)
    elif package == "Char.Vitals":
        handler.emit_vitals(character)
    elif package == "Char.Status":
        handler.emit_status(character)
    elif package == "Char.Factions":
        handler.emit_factions(character)
    elif package == "Char.Deity":
        handler.emit_deity(character)
    elif package == "Char.Quest":
        handler.emit_quest(character)


def emit_vitals(character):
    """Emit Char.Vitals for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_vitals(character)


def emit_status(character):
    """Emit Char.Status for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_status(character)


def emit_factions(character):
    """Emit Char.Factions for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_factions(character)


def emit_deity(character, at_shrine=False, shrine_name=None):
    """Emit Char.Deity for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_deity(character, at_shrine, shrine_name)


def emit_room(character, room=None):
    """Emit Room.Info for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        r = room or getattr(character, 'room', None)
        if r:
            handler.emit_room(r, character)


def emit_room_mobs(character, room=None):
    """Emit Room.Mobs for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        r = room or getattr(character, 'room', None)
        if r:
            handler.emit_room_mobs(r)


def emit_kin_sense(character, detections, room_modifier="normal", range_ft=60):
    """Emit Char.KinSense for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_kin_sense(detections, room_modifier, range_ft)


def emit_quest(character):
    """Emit Char.Quest for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_quest(character)


# ---------------------------------------------------------------------------
# Chat System GMCP Packages
# ---------------------------------------------------------------------------

def emit_chat_start(character, npc_name, npc_vnum, room_vnum, scenario=None):
    """Emit Chat.Started when a player enters AI chat mode."""
    handler = get_handler(character)
    if handler:
        data = {
            "npc_name": npc_name,
            "npc_vnum": npc_vnum,
            "room_vnum": room_vnum,
        }
        if scenario:
            data["scenario"] = scenario
        handler.emit("Chat.Started", data)


def emit_chat_world_event(character, text):
    """Emit Chat.WorldEvent when a world event injects into the chat."""
    handler = get_handler(character)
    if handler:
        handler.emit("Chat.WorldEvent", {"text": text})


def emit_chat_end(character, session_id=None, reason="endchat"):
    """Emit Chat.Ended when a chat session ends."""
    handler = get_handler(character)
    if handler:
        data = {"reason": reason}
        if session_id:
            data["session_id"] = session_id
        handler.emit("Chat.Ended", data)


def emit_chat_materialized(character, room_vnum, room_name):
    """Emit Chat.Materialized when a shadow presence becomes a real player."""
    handler = get_handler(character)
    if handler:
        handler.emit("Chat.Materialized", {
            "room_vnum": room_vnum,
            "room_name": room_name,
        })
