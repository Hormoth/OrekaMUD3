class Room:
    def __init__(self, vnum, name, description, exits, flags, items=None):
        self.vnum = vnum
        self.name = name
        self.description = description
        self.exits = exits
        self.flags = flags
        self.mobs = []
        self.players = []
        self.items = items or []  # List of Item objects

    def to_dict(self):
        """Serialize room for saving (excluding live mobs/players)."""
        return {
            "vnum": self.vnum,
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "flags": self.flags,
            # Items: store vnums if items are objects, or raw if already serializable
            "items": [item.vnum if hasattr(item, 'vnum') else item for item in self.items]
        }
