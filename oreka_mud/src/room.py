class Room:
    def __init__(self, vnum, name, description, exits, flags):
        self.vnum = vnum
        self.name = name
        self.description = description
        self.exits = exits
        self.flags = flags
        self.mobs = []
        self.players = []
