"""
GMCP (Generic Mud Communication Protocol) for OrekaMUD3.
Sends structured JSON data to clients that support it.
Used by Veil Client for visual panels, and by MudLet/TinTin++ for scripting.
"""
import json
import struct

# Telnet bytes
IAC = 255   # Interpret As Command
SB = 250    # Subnegotiation Begin
SE = 240    # Subnegotiation End
WILL = 251
WONT = 252
DO = 253
DONT = 254
GMCP_OPT = 201  # GMCP option code


class GMCPHandler:
    """Manages GMCP state for a single player connection."""

    def __init__(self, writer):
        self.writer = writer
        self.enabled = False
        self.supported_packages = set()

    def negotiate(self):
        """Send WILL GMCP to advertise support. Call on connection."""
        try:
            # Send raw bytes: IAC WILL GMCP
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
            # MudLet sends: Core.Supports.Set ["Char 1", "Room 1", ...]
            if text.startswith('Core.Supports.Set'):
                payload = text[len('Core.Supports.Set'):].strip()
                packages = json.loads(payload)
                for pkg in packages:
                    name = pkg.split()[0] if ' ' in pkg else pkg
                    self.supported_packages.add(name)
            elif text.startswith('Core.Hello'):
                # Client identification
                pass
        except Exception:
            pass

    def emit(self, package, data):
        """
        Send a GMCP data package to the client.
        package: e.g., "Char.Vitals", "Room.Info"
        data: dict that gets JSON-encoded
        """
        if not self.enabled:
            return

        try:
            payload = f"{package} {json.dumps(data, separators=(',', ':'))}"
            payload_bytes = payload.encode('utf-8')

            # IAC SB GMCP <payload> IAC SE
            raw = bytes([IAC, SB, GMCP_OPT]) + payload_bytes + bytes([IAC, SE])

            if hasattr(self.writer, '_transport') and self.writer._transport:
                self.writer._transport.write(raw)
        except Exception:
            pass

    def emit_vitals(self, character):
        """Emit Char.Vitals — HP, AC, MV, Gold, TNL."""
        from src.character import XP_TABLE
        tnl = max(0, XP_TABLE.get(character.level + 1, 0) - getattr(character, 'xp', 0))
        self.emit("Char.Vitals", {
            "hp": character.hp,
            "hp_max": character.max_hp,
            "ac": character.ac,
            "mv": getattr(character, 'move', 100),
            "mv_max": getattr(character, 'max_move', 100),
            "gold": getattr(character, 'gold', 0),
            "tnl": tnl
        })

    def emit_status(self, character):
        """Emit Char.Status — conditions, spell slots, level, class, race."""
        conditions = list(getattr(character, 'conditions', set()))
        conditions += list(getattr(character, 'active_conditions', {}).keys())
        divine = getattr(character, 'divine_buffs', {})
        if divine and divine.get('duration', 0) > 0:
            conditions.append("Blessed")

        spells = {}
        spd = getattr(character, 'spells_per_day', {})
        for lvl, remaining in spd.items():
            spells[str(lvl)] = remaining

        self.emit("Char.Status", {
            "conditions": conditions,
            "spells": spells,
            "level": character.level,
            "class": getattr(character, 'char_class', 'Unknown'),
            "race": getattr(character, 'race', 'Unknown')
        })

    def emit_factions(self, character):
        """Emit Char.Factions — all faction reputation values."""
        rep = getattr(character, 'reputation', {})
        self.emit("Char.Factions", dict(rep))

    def emit_deity(self, character, at_shrine=False, shrine_name=None):
        """Emit Char.Deity — patron, shrine status, buffs."""
        divine = getattr(character, 'divine_buffs', {})
        buffs = []
        if divine and divine.get('duration', 0) > 0:
            buffs.append(divine.get('deity', 'Divine Blessing'))

        self.emit("Char.Deity", {
            "patron": getattr(character, 'deity', None),
            "at_shrine": at_shrine,
            "shrine_name": shrine_name,
            "active_buffs": buffs
        })

    def emit_room(self, room, character=None):
        """Emit Room.Info — room data for mapping and display."""
        effects = []
        for e in getattr(room, 'effects', []):
            effects.append(e.get('type', 'unknown'))

        # Determine region from vnum
        vnum = room.vnum
        if vnum < 4000: region = "chapel"
        elif vnum < 5000: region = "custos_do_aeternos"
        elif vnum < 6000: region = "kinsweave"
        elif vnum < 7000: region = "tidebloom_reach"
        elif vnum < 8000: region = "eternal_steppe"
        elif vnum < 9000: region = "infinite_desert"
        elif vnum < 10000: region = "deepwater_marches"
        elif vnum < 11000: region = "twin_rivers"
        elif vnum < 11200: region = "wilderness"
        elif vnum < 13000: region = "gatefall_reach"
        elif vnum < 13100: region = "chainless_legion"
        else: region = "deepwater_expansion"

        self.emit("Room.Info", {
            "vnum": vnum,
            "name": room.name,
            "region": region,
            "exits": list(room.exits.keys()),
            "effects": effects,
            "terrain": getattr(room, 'terrain', None)
        })

    def emit_kin_sense(self, detections, room_modifier="normal", range_ft=60):
        """Emit Char.KinSense — detection results."""
        self.emit("Char.KinSense", {
            "detections": detections,
            "room_modifier": room_modifier,
            "range_ft": range_ft
        })

    def emit_quest(self, character):
        """Emit Char.Quest — quest state."""
        active = []
        completed = []
        quest_log = getattr(character, 'quest_log', None)
        if quest_log and hasattr(quest_log, 'active_quests'):
            for q in quest_log.active_quests:
                active.append({"id": str(q.id), "name": q.name})
        if quest_log and hasattr(quest_log, 'completed_quests'):
            completed = list(quest_log.completed_quests)

        self.emit("Char.Quest", {
            "active": active,
            "completed": completed
        })


# Store GMCP handlers per player
_handlers = {}  # {character_name: GMCPHandler}


def get_handler(character):
    """Get or create GMCP handler for a character."""
    name = getattr(character, 'name', None)
    if name and name in _handlers:
        return _handlers[name]
    return None


def register_handler(character, writer):
    """Register a GMCP handler for a new connection."""
    handler = GMCPHandler(writer)
    handler.negotiate()
    _handlers[character.name] = handler
    return handler


def unregister_handler(character):
    """Remove handler on disconnect."""
    name = getattr(character, 'name', None)
    if name:
        _handlers.pop(name, None)


def emit(character, package, data=None):
    """Convenience: emit a GMCP package for a character."""
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
    elif package == "Char.Quest":
        handler.emit_quest(character)
