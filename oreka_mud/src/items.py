
class Item:
    def __init__(self, vnum, name, item_type, weight, value, description="", slot=None, magical=False, ac_bonus=0, stat_bonuses=None, damage=None, properties=None, stats=None):
        self.vnum = vnum
        self.name = name
        self.item_type = item_type  # e.g., weapon, armor, potion
        self.weight = weight
        self.value = value
        self.description = description
        self.slot = slot  # e.g., head, body, hand, etc.
        self.magical = magical
        self.ac_bonus = ac_bonus
        self.stat_bonuses = stat_bonuses or {}
        self.damage = damage  # e.g., (1, 8, 2) for 1d8+2
        self.properties = properties or []
        self.stats = stats or {}

    def to_dict(self):
        return {
            "vnum": self.vnum,
            "name": self.name,
            "item_type": self.item_type,
            "weight": self.weight,
            "value": self.value,
            "description": self.description,
            "slot": self.slot,
            "magical": self.magical,
            "ac_bonus": self.ac_bonus,
            "stat_bonuses": self.stat_bonuses,
            "damage": self.damage,
            "properties": self.properties,
            "stats": self.stats
        }

    @staticmethod
    def from_dict(data):
        return Item(**data)
