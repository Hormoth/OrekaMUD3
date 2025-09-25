from src.combat import attack

class CommandParser:
    def __init__(self, world):
        self.world = world
        self.commands = {
            "look": self.cmd_look,
            "say": self.cmd_say,
            "kill": self.cmd_kill,
            "north": self.cmd_move,
            "exits": self.cmd_exits,
            "quest": self.cmd_quest,
            "gecho": self.cmd_gecho,
            "who": self.cmd_who,
            "stats": self.cmd_stats
        }

    def cmd_look(self, character, args):
        return character.room.description

    def cmd_say(self, character, args):
        return f"{character.name} says, '{args}'"

    def cmd_kill(self, character, args):
        target = next((m for m in character.room.mobs if m.name.lower() == args.lower() and m.alive), None)
        if target:
            character.state = State.COMBAT
            return attack(character, target)
        return "No such target!"

    def cmd_move(self, character, args):
        direction = args.lower()
        if direction in character.room.exits:
            new_vnum = character.room.exits[direction]
            if new_vnum in self.world.rooms:
                character.room.players.remove(character)
                character.room = self.world.rooms[new_vnum]
                character.room.players.append(character)
                return f"You move {direction} to {character.room.name}."
        return "No exit that way!"

    def cmd_exits(self, character, args):
        return ", ".join(character.room.exits.keys())

    def cmd_quest(self, character, args):
        if args.lower() == "start" and 1 not in [q["id"] for q in character.quests]:
            character.quests.append(self.world.quests[1])
            return f"Quest started: {self.world.quests[1]['name']}"
        return "Quest status: " + (f"{character.quests[0]['name']}" if character.quests else "No active quests.")

    def cmd_gecho(self, character, args):
        if not character.is_immortal:
            return "Command restricted to immortals!"
        return f"[GLOBAL] {character.name} broadcasts: {args}"

    def cmd_who(self, character, args):
        return self.world.do_who()

    def cmd_stats(self, character, args):
        return character.toggle_stats()
