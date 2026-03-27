import json
import os

ITEMS_DB = None

def load_items_db():
    global ITEMS_DB
    if ITEMS_DB is not None:
        return ITEMS_DB
    path = os.path.join(os.path.dirname(__file__), '../data/items.json')
    path = os.path.abspath(path)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    ITEMS_DB = {item['vnum']: Item.from_dict(item) for item in data}
    return ITEMS_DB

def get_item_by_vnum(vnum):
    db = load_items_db()
    return db.get(vnum)

def get_random_item(item_type=None, magical=None):
    db = load_items_db()
    items = list(db.values())
    if item_type:
        items = [i for i in items if i.item_type == item_type]
    if magical is not None:
        items = [i for i in items if i.magical == magical]
    if not items:
        return None
    import random
    return random.choice(items)

class Item:
    def __init__(self, vnum, name, item_type, weight, value, description="", slot=None, magical=False, ac_bonus=0, stat_bonuses=None, damage=None, properties=None, stats=None, hp=None, max_hp=None, material=None, complexity=None, charges=None, capacity=0, contents=None):
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
        self.material = material
        self.complexity = complexity
        self.charges = charges  # For wands — None means not a charged item
        self.capacity = capacity  # Container capacity (0 = not a container)
        self.contents = contents if contents is not None else ([] if capacity > 0 else None)
        # HP system
        base_hp = self._base_hp_for_material(material)
        multiplier = self._complexity_multiplier(complexity)
        self.max_hp = max_hp if max_hp is not None else int(base_hp * multiplier)
        self.hp = hp if hp is not None else self.max_hp

    def _base_hp_for_material(self, material):
        # Example values; expand as needed
        base_hp_table = {
            'iron': 20, 'steel': 30, 'wood': 10, 'leather': 8, 'stone': 40, 'mithral': 40, 'adamantine': 60,
            'copper': 15, 'bronze': 18, 'bone': 8, 'chitin': 12, 'darkwood': 20, 'dragonhide': 50,
            'embersteel': 45, 'wind-silk': 12, 'riverstone': 35, 'moonwhisper silver': 25,
            'volcanic glass': 15, 'giant-bone': 50
        }
        if material is None:
            return 10
        return base_hp_table.get(material, 10)

    def _complexity_multiplier(self, complexity):
        table = {'simple': 1, 'standard': 1.5, 'intermediate': 2, 'advanced': 3, 'masterwork': 4}
        if complexity is None:
            return 1
        return table.get(complexity, 1)

    def erode(self, amount=1):
        self.hp = max(0, self.hp - amount)
        return self.hp

    def to_dict(self):
        d = {
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
            "stats": self.stats,
            "material": self.material,
            "complexity": self.complexity,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "charges": self.charges,
            "capacity": self.capacity,
            "contents": [item.to_dict() for item in self.contents] if self.contents is not None else None,
        }
        return d

    @staticmethod
    def from_dict(data):
        # Handle contents recursively
        raw_contents = data.pop("contents", None)
        item = Item(**data)
        if raw_contents is not None and isinstance(raw_contents, list) and item.capacity > 0:
            item.contents = [Item.from_dict(c) for c in raw_contents]
        return item


class Corpse:
    """A corpse left behind when a mob dies. Contains loot for players to collect."""

    def __init__(self, mob_name, items=None, gold=0, decay_time=300):
        self.mob_name = mob_name
        self.items = items or []
        self.gold = gold
        self.decay_time = decay_time  # seconds until decay
        self._created_at = None  # Set by caller (time.time())

    @property
    def is_decayed(self):
        if self._created_at is None:
            return False
        import time
        return (time.time() - self._created_at) >= self.decay_time

    @property
    def is_empty(self):
        return self.gold <= 0 and not self.items
