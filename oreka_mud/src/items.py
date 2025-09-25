class Item:
    def __init__(self, vnum, name, item_type, weight, value, stats=None):
        self.vnum = vnum
        self.name = name
        self.item_type = item_type
        self.weight = weight
        self.value = value
        self.stats = stats or {}
