"""
Wandering Townsfolk System for OrekaMUD3.
Spawns ambient NPCs that wander between town rooms, adding life to the world.
These are non-combat, non-interactive flavor NPCs.
"""
import random
import time
import logging

logger = logging.getLogger("OrekaMUD.Townsfolk")


class Townsfolk:
    """A wandering ambient NPC."""

    def __init__(self, name, description, home_vnum, wander_range=None):
        self.name = name
        self.description = description
        self.home_vnum = home_vnum
        self.current_vnum = home_vnum
        self.wander_range = wander_range or []  # List of vnums this NPC can visit
        self.last_move = time.time()
        self.move_interval = random.randint(120, 360)  # 2-6 minutes
        self.sayings = []  # Ambient things they might say

    def tick(self, world):
        """Maybe move to a neighboring room. Returns (old_vnum, new_vnum) or None."""
        now = time.time()
        if now - self.last_move < self.move_interval:
            return None

        self.last_move = now
        self.move_interval = random.randint(120, 360)

        if not self.current_vnum or self.current_vnum not in world.rooms:
            return None

        current_room = world.rooms[self.current_vnum]
        # Pick a random connected room that's in our wander range (or any town room)
        exits = list(current_room.exits.values())
        valid_exits = []
        for exit_data in exits:
            vnum = exit_data if isinstance(exit_data, int) else exit_data.get('room', exit_data)
            if isinstance(vnum, int) and vnum in world.rooms:
                dest_room = world.rooms[vnum]
                dest_flags = getattr(dest_room, 'flags', [])
                # Only wander to town/safe/street rooms
                if self.wander_range:
                    if vnum in self.wander_range:
                        valid_exits.append(vnum)
                elif any(f in dest_flags for f in ('safe', 'street', 'market', 'town')):
                    valid_exits.append(vnum)
                # Also accept rooms in the 3000-4999 range (town rooms)
                elif 3000 <= vnum <= 4999:
                    valid_exits.append(vnum)

        if not valid_exits:
            return None

        # 50% chance to actually move (some ticks they stay put)
        if random.random() > 0.5:
            return None

        old_vnum = self.current_vnum
        new_vnum = random.choice(valid_exits)
        self.current_vnum = new_vnum
        return (old_vnum, new_vnum)

    def get_ambient_message(self):
        """Random ambient message when in a room with players."""
        if self.sayings and random.random() < 0.15:  # 15% chance per tick
            return f"{self.name} {random.choice(self.sayings)}"
        return None


# Pre-defined townsfolk
TOWNSFOLK_TEMPLATES = [
    {
        "name": "a weary merchant",
        "description": "A tired-looking merchant hauling a pack of wares.",
        "sayings": [
            "mutters about the price of grain.",
            "adjusts the straps on a heavy pack.",
            "glances at you and nods in greeting.",
            "counts coins quietly.",
        ],
    },
    {
        "name": "a Pekakarlik fisherman",
        "description": "A stout dwarf with salt-crusted boots and a net over one shoulder.",
        "sayings": [
            "hums a river shanty.",
            "says, 'The fish aren't biting today.'",
            "wrings water from a weathered cap.",
            "glances toward the river with a sigh.",
        ],
    },
    {
        "name": "a Hasura scholar",
        "description": "A tall elf with ink-stained fingers, absorbed in a scroll.",
        "sayings": [
            "mutters something about ancient runes.",
            "scribbles a note in a leather journal.",
            "looks up briefly, then returns to reading.",
            "says, 'Fascinating... simply fascinating.'",
        ],
    },
    {
        "name": "a street urchin",
        "description": "A quick-eyed child darting between the crowds.",
        "sayings": [
            "darts past you with a grin.",
            "whistles a tuneless melody.",
            "eyes your coin purse for a moment, then looks away.",
            "kicks a pebble down the street.",
        ],
    },
    {
        "name": "a Visetri mason",
        "description": "A broad-shouldered dwarf covered in stone dust.",
        "sayings": [
            "brushes stone dust from thick arms.",
            "says, 'Good stone here. Solid foundations.'",
            "examines a nearby wall with professional interest.",
            "nods approvingly at the craftsmanship around.",
        ],
    },
    {
        "name": "a traveling bard",
        "description": "A Pasua elf with a lute slung across their back.",
        "sayings": [
            "strums a few notes on a well-worn lute.",
            "hums a melody about the Fall of Aldenheim.",
            "says, 'Have you heard the ballad of Cinvarin?'",
            "taps a rhythm on the cobblestones with one foot.",
        ],
    },
    {
        "name": "an off-duty guard",
        "description": "A guard out of uniform, enjoying a rare day of rest.",
        "sayings": [
            "stretches and yawns.",
            "says, 'Don't cause any trouble, now.'",
            "keeps one hand near a concealed blade out of habit.",
            "nods curtly as you pass.",
        ],
    },
    {
        "name": "a priestess of Kaile'a",
        "description": "A serene woman in flowing blue robes.",
        "sayings": [
            "whispers a prayer to the Mistress of Waves.",
            "sprinkles water from a small vial onto the ground.",
            "says, 'May the tides carry you safely.'",
            "gazes toward the river with peaceful eyes.",
        ],
    },
]


class TownsfolkManager:
    """Manages all wandering townsfolk in the world."""

    def __init__(self):
        self.townsfolk = []
        self.initialized = False

    def initialize(self, world):
        """Spawn townsfolk in various town rooms."""
        if self.initialized:
            return

        # Pick random starting rooms from town areas (3000-4200 range)
        town_vnums = [v for v in world.rooms if 3000 <= v <= 4200]
        if not town_vnums:
            return

        for template in TOWNSFOLK_TEMPLATES:
            start_vnum = random.choice(town_vnums)
            npc = Townsfolk(
                name=template["name"],
                description=template["description"],
                home_vnum=start_vnum,
            )
            npc.sayings = template.get("sayings", [])
            npc.current_vnum = start_vnum
            self.townsfolk.append(npc)

        self.initialized = True
        logger.info(f"Spawned {len(self.townsfolk)} wandering townsfolk")

    def tick(self, world):
        """Move townsfolk and generate ambient messages. Returns list of (vnum, message)."""
        messages = []
        for npc in self.townsfolk:
            movement = npc.tick(world)
            if movement:
                old_vnum, new_vnum = movement
                # Departure message
                if old_vnum in world.rooms:
                    messages.append((old_vnum, f"{npc.name.capitalize()} wanders off."))
                # Arrival message
                if new_vnum in world.rooms:
                    messages.append((new_vnum, f"{npc.name.capitalize()} arrives."))

            # Ambient sayings
            if npc.current_vnum:
                ambient = npc.get_ambient_message()
                if ambient:
                    messages.append((npc.current_vnum, ambient))

        return messages

    def get_townsfolk_in_room(self, vnum):
        """Get list of townsfolk currently in a room."""
        return [npc for npc in self.townsfolk if npc.current_vnum == vnum]


# Singleton
_manager = None


def get_townsfolk_manager():
    global _manager
    if _manager is None:
        _manager = TownsfolkManager()
    return _manager
