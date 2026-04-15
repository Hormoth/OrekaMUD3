class Room:
    def __init__(self, vnum, name, description, exits, flags, items=None, terrain=None, weather=None,
                 light=None, builder_notes=None, owner=None, area_file=None, effects=None, **kwargs):
        self.vnum = vnum
        self.name = name
        self.description = description
        self.exits = exits
        self.flags = flags
        self.mobs = []
        self.players = []
        self.items = items or []  # List of Item objects
        self.corpses = []  # List of Corpse objects
        self.terrain = terrain
        self.weather = weather
        self.light = light
        self.builder_notes = builder_notes
        self.owner = owner
        self.area_file = area_file
        self.effects = effects or []  # Location effects: Kin-sense, hazards, rune-circles, etc.

        # Room ambience for LLM prompts (loaded from area JSON if present)
        self.ambience = None
        ambience_data = kwargs.get('ambience')
        if ambience_data and isinstance(ambience_data, dict):
            try:
                from src.ai_schemas.room_ambience import RoomAmbience
                self.ambience = RoomAmbience.from_dict(ambience_data)
            except ImportError:
                pass  # Schemas not loaded yet

    def to_dict(self):
        """Serialize room for saving (excluding live mobs/players)."""
        d = {
            "vnum": self.vnum,
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "flags": self.flags,
            # Items: store vnums if items are objects, or raw if already serializable
            "items": [item.vnum if hasattr(item, 'vnum') else item for item in self.items]
        }
        if self.terrain is not None:
            d["terrain"] = self.terrain
        if self.weather is not None:
            d["weather"] = self.weather
        if self.light is not None:
            d["light"] = self.light
        if self.builder_notes is not None:
            d["builder_notes"] = self.builder_notes
        if self.owner is not None:
            d["owner"] = self.owner
        if self.area_file is not None:
            d["area_file"] = self.area_file
        if self.effects:
            d["effects"] = self.effects
        return d

    def get_shadow_presences(self):
        """Get all shadow presences in this room."""
        try:
            from src.shadow_presence import shadow_manager
            return shadow_manager.get_by_room(self.vnum)
        except Exception:
            return []
