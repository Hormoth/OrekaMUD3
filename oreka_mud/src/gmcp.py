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

    def emit_status(self, character, added=None, removed=None):
        self.emit("Char.Status", _build_status(character, added=added, removed=removed))

    def emit_faction(self, faction_name, reputation, change=0):
        self.emit("Char.Factions", _build_faction(faction_name, reputation, change))

    def emit_factions(self, character):
        """Emit the full faction set as one message per faction (initial refresh)."""
        rep = getattr(character, 'reputation', {})
        for name, value in rep.items():
            self.emit_faction(name, value, change=0)

    def emit_deity(self, character, at_shrine=False, shrine_name=None, patron_nearby=False):
        self.emit("Char.Deity", _build_deity(character, at_shrine, shrine_name, patron_nearby))

    def emit_room(self, room, character=None):
        self.emit("Room.Info", _build_room(room))

    def emit_room_mobs(self, room, character=None):
        self.emit("Room.Mobs", _build_room_mobs(room, character))

    def emit_kin_sense(self, presences, room_modifier=None, range_ft=60):
        self.emit("Char.KinSense", _build_kin_sense(presences, room_modifier, range_ft))

    def emit_quest(self, character):
        self.emit("Char.Quest", _build_quest(character))

    def emit_inventory(self, character):
        self.emit("Char.Inventory", _build_inventory(character))


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

    def emit_status(self, character, added=None, removed=None):
        self.emit("Char.Status", _build_status(character, added=added, removed=removed))

    def emit_faction(self, faction_name, reputation, change=0):
        self.emit("Char.Factions", _build_faction(faction_name, reputation, change))

    def emit_factions(self, character):
        """Emit the full faction set as one message per faction (initial refresh)."""
        rep = getattr(character, 'reputation', {})
        for name, value in rep.items():
            self.emit_faction(name, value, change=0)

    def emit_deity(self, character, at_shrine=False, shrine_name=None, patron_nearby=False):
        self.emit("Char.Deity", _build_deity(character, at_shrine, shrine_name, patron_nearby))

    def emit_room(self, room, character=None):
        self.emit("Room.Info", _build_room(room))

    def emit_room_mobs(self, room, character=None):
        self.emit("Room.Mobs", _build_room_mobs(room, character))

    def emit_kin_sense(self, presences, room_modifier=None, range_ft=60):
        self.emit("Char.KinSense", _build_kin_sense(presences, room_modifier, range_ft))

    def emit_quest(self, character):
        self.emit("Char.Quest", _build_quest(character))

    def emit_inventory(self, character):
        self.emit("Char.Inventory", _build_inventory(character))


# ---------------------------------------------------------------------------
# Shared data-building helpers (transport-agnostic)
# ---------------------------------------------------------------------------

def _build_vitals(character):
    """Build Char.Vitals payload per docs/GMCP_SPEC.md."""
    from src.character import XP_TABLE
    xp_tnl = max(0, XP_TABLE.get(character.level + 1, 0) - getattr(character, 'xp', 0))
    spell_slots = {}
    for lvl, remaining in getattr(character, 'spells_per_day', {}).items():
        spell_slots[str(lvl)] = remaining
    return {
        "hp": character.hp,
        "hp_max": character.max_hp,
        "mv": getattr(character, 'move', 100),
        "mv_max": getattr(character, 'max_move', 100),
        "ac": character.ac,
        "gold": getattr(character, 'gold', 0),
        "xp_tnl": xp_tnl,
        "spell_slots": spell_slots,
    }


def _build_status(character, added=None, removed=None):
    """Build Char.Status payload per docs/GMCP_SPEC.md.

    ``added`` and ``removed`` are optional condition-name strings used by
    event-driven callers to signal exactly one transition; callers that
    lack delta info (initial emit, periodic refresh) pass None.
    """
    conditions = list(getattr(character, 'conditions', set()))
    conditions += list(getattr(character, 'active_conditions', {}).keys())
    divine = getattr(character, 'divine_buffs', {})
    if divine and divine.get('duration', 0) > 0:
        conditions.append("Blessed")
    return {
        "conditions": conditions,
        "added": added,
        "removed": removed,
    }


_FACTION_TIER_BANDS = (
    (600, "allied"),
    (300, "friendly"),
    (100, "respected"),
    (-100, "neutral"),
    (-300, "unfriendly"),
    (-500, "hostile"),
)


def _faction_tier(reputation):
    for threshold, label in _FACTION_TIER_BANDS:
        if reputation >= threshold:
            return label
    return "reviled"


def _build_faction(faction_name, reputation, change=0):
    """Build a per-faction Char.Factions payload per docs/GMCP_SPEC.md."""
    return {
        "faction": faction_name,
        "reputation": reputation,
        "tier": _faction_tier(reputation),
        "change": change,
    }


def _build_deity(character, at_shrine=False, shrine_name=None, patron_nearby=False):
    """Build Char.Deity payload per docs/GMCP_SPEC.md."""
    divine = getattr(character, 'divine_buffs', {})
    buffs = []
    if divine and divine.get('duration', 0) > 0:
        buffs.append({
            "name": divine.get('deity', 'Divine Blessing'),
            "duration": int(divine.get('duration', 0)),
        })
    return {
        "patron": getattr(character, 'deity', None),
        "at_shrine": at_shrine,
        "shrine_name": shrine_name,
        "patron_nearby": patron_nearby,
        "buffs": buffs,
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

    exits_map = {}
    for direction, target in getattr(room, 'exits', {}).items():
        if isinstance(target, int):
            exits_map[direction] = target
        else:
            exits_map[direction] = getattr(target, 'vnum', None)

    return {
        "vnum": vnum,
        "name": room.name,
        "description": getattr(room, 'description', ''),
        "area": region,
        "region": region,
        "exits": exits_map,
        "flags": list(getattr(room, 'flags', []) or []),
        "effects": effects,
        "terrain": getattr(room, 'terrain', None),
    }


_NONHOSTILE_FLAGS = {
    'no_attack', 'shopkeeper', 'trainer', 'banker', 'blacksmith',
    'guard', 'innkeeper', 'quest', 'friendly',
}


def _is_hostile(mob):
    if getattr(mob, 'hostile', False):
        return True
    flags = set(getattr(mob, 'flags', []) or [])
    return not (flags & _NONHOSTILE_FLAGS)


def _mob_summary(mob):
    hp = getattr(mob, 'hp', 0)
    max_hp = getattr(mob, 'max_hp', 1) or 1
    return {
        "name": mob.name,
        "hostile": _is_hostile(mob),
        "cr": getattr(mob, 'cr', getattr(mob, 'level', 0)),
        "hp_percent": int(round((hp / max_hp) * 100)),
        "vnum": getattr(mob, 'vnum', 0),
    }


def _build_room_mobs(room, character=None):
    """Build Room.Mobs payload per docs/GMCP_SPEC.md.

    Includes combat state derived from ``character.combat_target`` when
    the character is engaged with a mob in this room.
    """
    mobs = []
    for mob in getattr(room, 'mobs', []):
        if not getattr(mob, 'alive', True):
            continue
        mobs.append(_mob_summary(mob))

    target_mob = getattr(character, 'combat_target', None) if character else None
    in_combat = False
    target_payload = None
    if target_mob and getattr(target_mob, 'alive', True):
        in_combat = True
        hp = getattr(target_mob, 'hp', 0)
        max_hp = getattr(target_mob, 'max_hp', 1) or 1
        target_conditions = list(getattr(target_mob, 'conditions', set()))
        target_conditions += list(getattr(target_mob, 'active_conditions', {}).keys())
        target_payload = {
            "name": target_mob.name,
            "hp_percent": int(round((hp / max_hp) * 100)),
            "conditions": target_conditions,
        }

    return {
        "in_combat": in_combat,
        "target": target_payload,
        "mobs": mobs,
    }


def _build_kin_sense(presences, room_modifier=None, range_ft=60):
    """Build Char.KinSense payload per docs/GMCP_SPEC.md.

    ``presences`` is a list of per-entity dicts:
    ``{name, resonance, distance, bearing, type}``. Callers with only
    aggregated counts should expand before calling (see kin_sense.py).
    """
    return {
        "range_ft": range_ft,
        "modifier": room_modifier if room_modifier and room_modifier != "normal" else None,
        "presences": list(presences or []),
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


def _build_inventory(character):
    """Build Char.Inventory payload — items carried and equipped."""
    items = []
    for item in getattr(character, 'inventory', []):
        entry = {"name": getattr(item, 'name', str(item)), "quantity": 1}
        flags = []
        for flag in ('glowing', 'humming', 'invisible', 'magic', 'evil', 'anti_evil',
                     'anti_good', 'anti_neutral', 'cursed', 'blessed'):
            if getattr(item, flag, False):
                flags.append(flag)
        if flags:
            entry["flags"] = flags
        if hasattr(item, 'item_type'):
            entry["type"] = item.item_type
        items.append(entry)

    equipped = {}
    for slot, item in getattr(character, 'equipment', {}).items():
        if item:
            equipped[slot] = getattr(item, 'name', str(item))

    return {
        "items": items,
        "equipped": equipped,
        "gold": getattr(character, 'gold', 0),
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
        _last_emit_state.pop(name, None)


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
    elif package == "Char.Inventory":
        handler.emit_inventory(character)


def emit_vitals(character):
    """Emit Char.Vitals for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_vitals(character)


def emit_status(character, added=None, removed=None):
    """Emit Char.Status for a character if they have a GMCP handler.

    ``added`` / ``removed`` name the single condition that changed in this
    event (spec-aligned delta). Callers without delta info pass None.
    """
    handler = get_handler(character)
    if handler:
        handler.emit_status(character, added=added, removed=removed)


def emit_faction(character, faction_name, reputation, change=0):
    """Emit a single-faction Char.Factions update per spec."""
    handler = get_handler(character)
    if handler:
        handler.emit_faction(faction_name, reputation, change)


def emit_factions(character):
    """Emit one Char.Factions message per faction (initial refresh)."""
    handler = get_handler(character)
    if handler:
        handler.emit_factions(character)


def emit_deity(character, at_shrine=False, shrine_name=None, patron_nearby=False):
    """Emit Char.Deity for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_deity(character, at_shrine, shrine_name, patron_nearby)


def emit_room(character, room=None):
    """Emit Room.Info for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        r = room or getattr(character, 'room', None)
        if r:
            handler.emit_room(r, character)


def emit_room_mobs(character, room=None):
    """Emit Room.Mobs for a character if they have a GMCP handler.

    Combat state derives from ``character.combat_target``.
    """
    handler = get_handler(character)
    if handler:
        r = room or getattr(character, 'room', None)
        if r:
            handler.emit_room_mobs(r, character)


def emit_kin_sense(character, presences, room_modifier=None, range_ft=60):
    """Emit Char.KinSense for a character if they have a GMCP handler.

    ``presences`` is per-spec: list of ``{name, resonance, distance, bearing, type}``.
    """
    handler = get_handler(character)
    if handler:
        handler.emit_kin_sense(presences, room_modifier, range_ft)


def emit_quest(character):
    """Emit Char.Quest for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_quest(character)


def emit_inventory(character):
    """Emit Char.Inventory for a character if they have a GMCP handler."""
    handler = get_handler(character)
    if handler:
        handler.emit_inventory(character)


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


# ---------------------------------------------------------------------------
# Central tick emitter — fires delta-aware state snapshots every N seconds
# ---------------------------------------------------------------------------

# Per-character state cache to gate redundant emits.
_last_emit_state = {}  # {character_name: {"vitals": {...}, "conditions": set, "room_vnum": int}}


def _tick_emit_for(character):
    """Emit any state-delta GMCP packages for one character.

    Caches last-emitted vitals fingerprint, condition set, and room vnum
    so redundant per-tick packets are suppressed.
    """
    handler = get_handler(character)
    if not handler:
        return
    name = getattr(character, 'name', None)
    if not name:
        return
    prev = _last_emit_state.setdefault(name, {})

    vitals = _build_vitals(character)
    vitals_fp = (
        vitals["hp"], vitals["hp_max"], vitals["mv"], vitals["mv_max"],
        vitals["ac"], vitals["gold"], vitals["xp_tnl"],
        tuple(sorted(vitals["spell_slots"].items())),
    )
    if prev.get("vitals_fp") != vitals_fp:
        handler.emit("Char.Vitals", vitals)
        prev["vitals_fp"] = vitals_fp

    current_conditions = set(getattr(character, 'conditions', set()))
    current_conditions |= set(getattr(character, 'active_conditions', {}).keys())
    divine = getattr(character, 'divine_buffs', {})
    if divine and divine.get('duration', 0) > 0:
        current_conditions.add("Blessed")
    prev_conditions = prev.get("conditions", set())
    if current_conditions != prev_conditions:
        added = next(iter(current_conditions - prev_conditions), None)
        removed = next(iter(prev_conditions - current_conditions), None)
        handler.emit_status(character, added=added, removed=removed)
        prev["conditions"] = current_conditions

    room = getattr(character, 'room', None)
    if room is not None:
        target = getattr(character, 'combat_target', None)
        target_alive = bool(target and getattr(target, 'alive', True))
        mob_fp = tuple(
            (getattr(m, 'name', ''), getattr(m, 'hp', 0), getattr(m, 'alive', True))
            for m in getattr(room, 'mobs', [])
            if getattr(m, 'alive', True)
        )
        combat_fp = (
            target_alive,
            getattr(target, 'name', None) if target_alive else None,
            getattr(target, 'hp', None) if target_alive else None,
        )
        new_fp = (mob_fp, combat_fp)
        if prev.get("room_mobs_fp") != new_fp:
            handler.emit_room_mobs(room, character)
            prev["room_mobs_fp"] = new_fp


def tick_all(world):
    """Central GMCP tick — emit deltas for every connected character.

    Call on a 2-second loop from main.py. Safe to call when no handlers
    are registered (no-op).
    """
    if not _handlers:
        return
    players = getattr(world, 'players', None) or []
    for character in players:
        if getattr(character, 'name', None) in _handlers:
            try:
                _tick_emit_for(character)
            except Exception as e:
                logger.debug(f"GMCP tick error for {character.name}: {e}")


def clear_cache(character):
    """Clear per-character delta cache on disconnect or on forced refresh."""
    name = getattr(character, 'name', None)
    if name:
        _last_emit_state.pop(name, None)
