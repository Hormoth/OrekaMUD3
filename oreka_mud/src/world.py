import json
from src.room import Room
from src.mob import Mob

class OrekaWorld:
    def __init__(self):
        self.rooms = {}
        self.mobs = {}
        self.players = []
        self.quests = {
            1: {"id": 1, "name": "Starweave Ritual", "description": "Perform the Starweave in Guild Street.", "location": 3001}
        }

    def load_data(self):
        import json
        # Load rooms from JSON
        with open("data/rooms.json", "r") as f:
            rooms_data = json.load(f)
        for room_data in rooms_data:
            room = Room(**room_data)
            self.rooms[room.vnum] = room

        # Load mobs from JSON
        with open("data/mobs.json", "r") as f:
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
