
import os
import json
from src.room import Room
from src.mob import Mob

class OrekaWorld:
    def save_items(self):
        """Save all items to data/items.json."""
        import os, json
        if not hasattr(self, 'items'):
            return
        items_file = os.path.join("data", "items.json")
        items_data = [item.to_dict() for item in self.items.values()]
        with open(items_file, "w", encoding="utf-8") as f:
            json.dump(items_data, f, indent=2)
    def save_mobs(self):
        """Save all mobs to data/mobs.json."""
        import os, json
        mobs_file = os.path.join("data", "mobs.json")
        mobs_data = []
        for mob in self.mobs.values():
            d = mob.to_dict()
            # Try to find the room vnum for this mob
            for room in self.rooms.values():
                if mob in room.mobs:
                    d["room_vnum"] = room.vnum
                    break
            mobs_data.append(d)
        with open(mobs_file, "w", encoding="utf-8") as f:
            json.dump(mobs_data, f, indent=2)
    def save_rooms(self):
        """Save all rooms to their area JSON files in data/areas/ (grouped by file if possible)."""
        import os, json
        # Group rooms by area file (assume all in one file for now: Chapel.json or similar)
        area_dir = os.path.join("data", "areas")
        # For now, save all rooms to Chapel.json (expand logic for multi-area later)
        area_file = os.path.join(area_dir, "Chapel.json")
        rooms_data = [room.to_dict() for room in self.rooms.values()]
        with open(area_file, "w", encoding="utf-8") as f:
            json.dump(rooms_data, f, indent=2)
    def __init__(self):
        self.rooms = {}
        self.mobs = {}
        self.players = []
        self.quests = {
            1: {"id": 1, "name": "Starweave Ritual", "description": "Perform the Starweave in Guild Street.", "location": 3001}
        }

    def load_data(self):
        # Load all area JSON files from data/areas
        area_dir = os.path.join("data", "areas")
        for filename in os.listdir(area_dir):
            if filename.endswith(".json"):
                with open(os.path.join(area_dir, filename), "r") as f:
                    try:
                        data = json.load(f)
                        # Support both list-of-rooms and {"rooms": [...]} formats
                        if isinstance(data, dict) and "rooms" in data:
                            rooms_data = data["rooms"]
                        else:
                            rooms_data = data
                        for room_data in rooms_data:
                            room = Room(**room_data)
                            self.rooms[room.vnum] = room
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")

        # Load mobs from JSON
        with open(os.path.join("data", "mobs.json"), "r") as f:
            mobs_data = json.load(f)
        for mob_data in mobs_data:
            mob = Mob(**{k: v for k, v in mob_data.items() if k != "room_vnum"})
            self.mobs[mob.vnum] = mob
            room_vnum = mob_data.get("room_vnum")
            if room_vnum in self.rooms:
                self.rooms[room_vnum].mobs.append(mob)

    def do_who(self):
        output = "Players Online:\n"
        for player in self.players:
            race_abbr = player.race[:3] if player.race else "Unk"
            class_abbr = "Clr" if player.is_immortal else "Brd"  # Simplified
            title = f" {player.title}" if player.title else ""
            output += f"[Lvl {player.level:2} {race_abbr} {class_abbr}] {player.name}{title} ({player.race or 'Unknown'})"
            if player.elemental_affinity:
                output += f" [{player.elemental_affinity}]"
            if player.is_immortal:
                output += " [Immortal]"
            output += "\n"
        return output
