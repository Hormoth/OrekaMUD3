"""
Wandering Gods System for OrekaMUD3.
Ascended Gods exist as invisible entities that roam between their shrines.
- Your patron deity is visible to you
- Other gods sensed only via high Kin-sense / Wisdom
- Elemental Lords are never visible — felt as elemental surges
- Player-linked gods follow different rules (visible when manifested)
"""
import random
import time


class WanderingGod:
    """An invisible deity entity that moves between shrine rooms."""

    def __init__(self, deity_id, deity_data):
        self.deity_id = deity_id
        self.name = deity_data.get("name", deity_id)
        self.dtype = deity_data.get("type", "ascended")  # elemental_lord or ascended
        self.element = deity_data.get("element")
        self.shrine_vnums = deity_data.get("shrine_vnums", [])
        self.player_name = deity_data.get("player_name")
        self.current_vnum = self.shrine_vnums[0] if self.shrine_vnums else None
        self.last_move_time = time.time()
        self.move_interval = random.randint(300, 900)  # Move every 5-15 minutes
        self.manifested = False  # True if player-god used divine manifest

    def tick(self):
        """Move to a different shrine if interval elapsed."""
        if not self.shrine_vnums or len(self.shrine_vnums) < 2:
            return None  # Nowhere to go

        now = time.time()
        if now - self.last_move_time >= self.move_interval:
            self.last_move_time = now
            self.move_interval = random.randint(300, 900)
            self.manifested = False  # Unmanifest on move

            old_vnum = self.current_vnum
            available = [v for v in self.shrine_vnums if v != self.current_vnum]
            if available:
                self.current_vnum = random.choice(available)
            return (old_vnum, self.current_vnum)
        return None

    def is_visible_to(self, character):
        """Determine if this god is visible to a specific character."""
        # Player-linked god who manifested = visible to all
        if self.manifested and self.player_name:
            return True

        # Elemental Lords are NEVER visible — only felt
        if self.dtype == "elemental_lord":
            return False

        # Your patron deity = visible
        char_deity = getattr(character, 'deity', '') or ''
        if char_deity and char_deity.lower() in self.name.lower():
            return True

        # Farborn and Silentborn can never see gods
        race = getattr(character, 'race', '')
        if 'Farborn' in race or 'Silentborn' in race:
            return False

        return False

    def get_presence_message(self, character):
        """Get the message a character sees/senses for this god."""
        if self.is_visible_to(character):
            # Full visibility — patron deity
            element_desc = {
                "fire": "wreathed in flickering embers",
                "water": "shimmering with tidal light",
                "earth": "solid as mountain stone",
                "wind": "trailing wisps of cloud",
                "all": "radiant with all four elemental lights",
            }
            edesc = element_desc.get(self.element, "glowing with divine light")
            return f"\033[1;33m{self.name} is here, {edesc}. Your patron deity acknowledges your presence.\033[0m"

        # Elemental Lord — felt, not seen
        if self.dtype == "elemental_lord":
            element_feel = {
                "earth": "The ground vibrates with a deep, patient resonance — as if the stone itself is watching.",
                "fire": "An impossible warmth fills the air, carrying the scent of volcanic forge-fire.",
                "water": "The air grows cool and damp. You hear the distant sound of waves where no sea exists.",
                "wind": "A gentle breeze stirs from nowhere, carrying the faint sound of laughter.",
            }
            return f"\033[0;33m{element_feel.get(self.element, 'You sense an ancient elemental presence.')}\033[0m"

        # Ascended God — not your patron, but detectable with high Wisdom
        wis = getattr(character, 'wis_score', 10)
        if wis >= 16:
            return f"\033[0;35mYou sense a divine presence nearby — powerful but not meant for you.\033[0m"
        elif wis >= 12:
            return f"\033[0;90mA faint shimmer in your Kin-sense, like a distant bell.\033[0m"

        return None  # Below Wis 12 = can't sense it at all


class WanderingGodsManager:
    """Manages all wandering god entities."""

    def __init__(self):
        self.gods = {}  # {deity_id: WanderingGod}
        self.initialized = False

    def initialize(self):
        """Load deities and create wandering entities."""
        if self.initialized:
            return
        try:
            from src.religion import get_religion_manager
            rm = get_religion_manager()
            for deity_id, deity_data in rm.get_all_deities().items():
                shrines = deity_data.get("shrine_vnums", [])
                if shrines:  # Only create wanderers for gods with shrines
                    self.gods[deity_id] = WanderingGod(deity_id, deity_data)
            self.initialized = True
        except Exception as e:
            print(f"Error initializing wandering gods: {e}")

    def tick(self, world):
        """Move gods between shrines. Returns list of (god, old_vnum, new_vnum)."""
        if not self.initialized:
            self.initialize()

        movements = []
        for deity_id, god in self.gods.items():
            result = god.tick()
            if result:
                old_vnum, new_vnum = result
                movements.append((god, old_vnum, new_vnum))
        return movements

    def get_gods_in_room(self, room_vnum):
        """Get all gods currently in a room."""
        return [g for g in self.gods.values() if g.current_vnum == room_vnum]

    def get_room_presence_messages(self, character, room_vnum):
        """Get all divine presence messages for a character in a room."""
        messages = []
        for god in self.get_gods_in_room(room_vnum):
            msg = god.get_presence_message(character)
            if msg:
                messages.append(msg)
        return messages

    def get_god_by_deity_id(self, deity_id):
        """Get a specific wandering god."""
        return self.gods.get(deity_id)


# Singleton
_wandering_gods = None


def get_wandering_gods():
    global _wandering_gods
    if _wandering_gods is None:
        _wandering_gods = WanderingGodsManager()
    return _wandering_gods
