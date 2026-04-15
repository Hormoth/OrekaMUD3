"""
Player Housing System for OrekaMUD3.

Allows players to purchase, furnish, and manage houses.
Houses provide storage, passive bonuses from furniture, and social visiting.
"""

import json
import os
from datetime import datetime

from src.items import Item


# ---------------------------------------------------------------------------
# Purchasable house types
# ---------------------------------------------------------------------------

HOUSE_TYPES = {
    "cottage": {
        "name": "Small Cottage",
        "cost": 5000,
        "rooms": 2,
        "storage": 20,
        "description": "A cozy stone cottage.",
    },
    "townhouse": {
        "name": "Townhouse",
        "cost": 15000,
        "rooms": 4,
        "storage": 50,
        "description": "A comfortable two-story townhouse.",
    },
    "manor": {
        "name": "Grand Manor",
        "cost": 50000,
        "rooms": 8,
        "storage": 100,
        "description": "An impressive manor house.",
    },
    "guild_hall": {
        "name": "Guild Hall",
        "cost": 100000,
        "rooms": 12,
        "storage": 200,
        "description": "A great hall fit for a guild.",
    },
}

# ---------------------------------------------------------------------------
# Purchasable furniture
# ---------------------------------------------------------------------------

FURNITURE = {
    "bed": {
        "name": "Comfortable Bed",
        "cost": 100,
        "effect": "rest_bonus",
        "description": "A soft feather bed. Resting here heals faster.",
    },
    "chest": {
        "name": "Storage Chest",
        "cost": 200,
        "effect": "storage_10",
        "description": "A reinforced chest. Adds 10 storage slots.",
    },
    "workbench": {
        "name": "Crafting Workbench",
        "cost": 500,
        "effect": "craft_bonus",
        "description": "A sturdy workbench. +2 to Craft checks.",
    },
    "altar": {
        "name": "Prayer Altar",
        "cost": 1000,
        "effect": "prayer_bonus",
        "description": "A sacred altar. Prayer effects last longer.",
    },
    "trophy_case": {
        "name": "Trophy Case",
        "cost": 300,
        "effect": "display",
        "description": "Display your achievements and rare items.",
    },
    "bookshelf": {
        "name": "Bookshelf",
        "cost": 250,
        "effect": "knowledge_bonus",
        "description": "A tall bookshelf. +2 to Knowledge checks here.",
    },
    "fireplace": {
        "name": "Fireplace",
        "cost": 400,
        "effect": "warmth",
        "description": "A stone fireplace. Provides comfort and light.",
    },
    "garden": {
        "name": "Herb Garden",
        "cost": 600,
        "effect": "herb_source",
        "description": "A small garden. Produces 1 healing herb per day.",
    },
}


# ---------------------------------------------------------------------------
# HousingManager
# ---------------------------------------------------------------------------

class HousingManager:
    """Manages player-owned houses, furniture, and item storage."""

    def __init__(self):
        self.houses = {}  # player_name -> house dict
        self._load()

    # -- persistence --------------------------------------------------------

    def _data_path(self):
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data", "housing.json")
        )

    def _load(self):
        path = self._data_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.houses = data.get("houses", {})
            except (json.JSONDecodeError, IOError):
                self.houses = {}
        else:
            self.houses = {}

    def _save(self):
        path = self._data_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"houses": self.houses}, f, indent=2, ensure_ascii=False)

    # -- queries ------------------------------------------------------------

    def get_house(self, player_name):
        """Return the house record for *player_name*, or ``None``."""
        return self.houses.get(player_name)

    def _storage_capacity(self, house):
        """Compute total storage capacity (base + furniture bonuses)."""
        house_type = HOUSE_TYPES.get(house.get("type", ""), {})
        base = house_type.get("storage", 0)
        bonus = sum(
            10
            for fk in house.get("furniture", [])
            if FURNITURE.get(fk, {}).get("effect") == "storage_10"
        )
        return base + bonus

    # -- buying / selling ---------------------------------------------------

    def buy_house(self, character, house_type, location_vnum):
        """Purchase a house.  Deducts gold from the character.

        Returns a ``(success: bool, message: str)`` tuple.
        """
        if character.name in self.houses:
            return False, "You already own a house. Sell it first before buying a new one."

        ht = HOUSE_TYPES.get(house_type)
        if ht is None:
            valid = ", ".join(HOUSE_TYPES.keys())
            return False, f"Unknown house type '{house_type}'. Valid types: {valid}."

        cost = ht["cost"]
        if character.gold < cost:
            shortfall = cost - character.gold
            return False, (
                f"You need {cost} gold to purchase a {ht['name']}. "
                f"You are {shortfall} gold short."
            )

        character.gold -= cost
        self.houses[character.name] = {
            "type": house_type,
            "location_vnum": location_vnum,
            "furniture": [],
            "storage": [],
            "purchased": datetime.utcnow().isoformat(),
        }
        self._save()
        return True, (
            f"Congratulations! You purchased a {ht['name']} at location "
            f"{location_vnum} for {cost} gold."
        )

    def sell_house(self, character):
        """Sell the character's house for 50% of its purchase cost.

        Items in storage are returned to the character's inventory.
        Returns a ``(success: bool, message: str, returned_items: list)`` tuple.
        """
        house = self.houses.get(character.name)
        if house is None:
            return False, "You do not own a house.", []

        ht = HOUSE_TYPES.get(house["type"], {})
        refund = ht.get("cost", 0) // 2

        # Return stored items to inventory
        returned_items = []
        for item_data in house.get("storage", []):
            try:
                item = Item.from_dict(dict(item_data))
                if hasattr(character, "inventory"):
                    character.inventory.append(item)
                returned_items.append(item.name)
            except Exception:
                # If an item cannot be reconstituted, skip it gracefully
                returned_items.append(item_data.get("name", "unknown item"))

        character.gold += refund
        del self.houses[character.name]
        self._save()

        items_msg = ""
        if returned_items:
            items_msg = (
                f" {len(returned_items)} stored item(s) returned to your inventory: "
                + ", ".join(returned_items)
                + "."
            )

        return True, (
            f"You sold your {ht.get('name', 'house')} for {refund} gold.{items_msg}"
        ), returned_items

    # -- furniture ----------------------------------------------------------

    def add_furniture(self, character, furniture_key):
        """Buy and place a piece of furniture in the character's house.

        Returns ``(success, message)``.
        """
        house = self.houses.get(character.name)
        if house is None:
            return False, "You do not own a house."

        furn = FURNITURE.get(furniture_key)
        if furn is None:
            valid = ", ".join(FURNITURE.keys())
            return False, f"Unknown furniture '{furniture_key}'. Available: {valid}."

        if furniture_key in house.get("furniture", []):
            return False, f"You already have a {furn['name']} in your house."

        cost = furn["cost"]
        if character.gold < cost:
            shortfall = cost - character.gold
            return False, (
                f"A {furn['name']} costs {cost} gold. You are {shortfall} gold short."
            )

        character.gold -= cost
        house.setdefault("furniture", []).append(furniture_key)
        self._save()
        return True, (
            f"You purchased and placed a {furn['name']} in your house for {cost} gold. "
            f"{furn['description']}"
        )

    def remove_furniture(self, character, furniture_key):
        """Remove a piece of furniture (no refund).

        Returns ``(success, message)``.
        """
        house = self.houses.get(character.name)
        if house is None:
            return False, "You do not own a house."

        furniture_list = house.get("furniture", [])
        if furniture_key not in furniture_list:
            furn_name = FURNITURE.get(furniture_key, {}).get("name", furniture_key)
            return False, f"Your house does not have a {furn_name}."

        furniture_list.remove(furniture_key)
        self._save()
        furn_name = FURNITURE.get(furniture_key, {}).get("name", furniture_key)
        return True, f"You removed the {furn_name} from your house. (No refund.)"

    # -- item storage -------------------------------------------------------

    def store_item(self, character, item):
        """Store an Item in the character's house storage.

        Returns ``(success, message)``.
        """
        house = self.houses.get(character.name)
        if house is None:
            return False, "You do not own a house."

        capacity = self._storage_capacity(house)
        stored = house.get("storage", [])
        if len(stored) >= capacity:
            return False, (
                f"Your house storage is full ({len(stored)}/{capacity}). "
                "Consider buying a Storage Chest for more space."
            )

        item_data = item.to_dict() if hasattr(item, "to_dict") else {"name": str(item)}
        stored.append(item_data)
        house["storage"] = stored

        # Remove item from character inventory
        if hasattr(character, "inventory") and item in character.inventory:
            character.inventory.remove(item)

        self._save()
        return True, (
            f"You store {item.name} in your house. "
            f"({len(stored)}/{capacity} slots used)"
        )

    def retrieve_item(self, character, item_name):
        """Retrieve a stored item by name (case-insensitive prefix match).

        Returns ``(success, message)``.
        """
        house = self.houses.get(character.name)
        if house is None:
            return False, "You do not own a house."

        stored = house.get("storage", [])
        if not stored:
            return False, "Your house storage is empty."

        query = item_name.lower().strip()
        for i, item_data in enumerate(stored):
            name = item_data.get("name", "")
            if name.lower() == query or name.lower().startswith(query):
                stored.pop(i)
                try:
                    item = Item.from_dict(dict(item_data))
                except Exception:
                    return False, f"Failed to retrieve '{name}' -- item data corrupt."
                if hasattr(character, "inventory"):
                    character.inventory.append(item)
                self._save()
                capacity = self._storage_capacity(house)
                return True, (
                    f"You retrieve {item.name} from your house storage. "
                    f"({len(stored)}/{capacity} slots used)"
                )

        return False, f"No item matching '{item_name}' found in your storage."

    def list_storage(self, character):
        """Return a formatted listing of stored items.

        Returns ``(success, message)``.
        """
        house = self.houses.get(character.name)
        if house is None:
            return False, "You do not own a house."

        stored = house.get("storage", [])
        capacity = self._storage_capacity(house)
        if not stored:
            return True, f"Your house storage is empty. (0/{capacity} slots)"

        lines = [f"House Storage ({len(stored)}/{capacity} slots):"]
        for idx, item_data in enumerate(stored, 1):
            name = item_data.get("name", "Unknown")
            itype = item_data.get("item_type", "")
            value = item_data.get("value", 0)
            detail = f"  [{itype}]" if itype else ""
            detail += f"  ({value} gp)" if value else ""
            lines.append(f"  {idx}. {name}{detail}")
        return True, "\n".join(lines)

    # -- effects / bonuses --------------------------------------------------

    def get_house_effects(self, character):
        """Return a dict of active effects granted by the character's furniture.

        Keys are effect names (e.g. ``rest_bonus``, ``craft_bonus``).
        Values are ``True`` or a numeric bonus as appropriate.
        """
        house = self.houses.get(character.name)
        if house is None:
            return {}

        effects = {}
        for fk in house.get("furniture", []):
            furn = FURNITURE.get(fk)
            if furn is None:
                continue
            effect = furn["effect"]
            if effect == "rest_bonus":
                effects["rest_bonus"] = True
            elif effect == "storage_10":
                # Handled by _storage_capacity; not a gameplay effect per se
                effects["extra_storage"] = effects.get("extra_storage", 0) + 10
            elif effect == "craft_bonus":
                effects["craft_bonus"] = effects.get("craft_bonus", 0) + 2
            elif effect == "prayer_bonus":
                effects["prayer_bonus"] = True
            elif effect == "display":
                effects["display"] = True
            elif effect == "knowledge_bonus":
                effects["knowledge_bonus"] = effects.get("knowledge_bonus", 0) + 2
            elif effect == "warmth":
                effects["warmth"] = True
            elif effect == "herb_source":
                effects["herb_source"] = True
        return effects

    # -- display ------------------------------------------------------------

    def format_house_info(self, character):
        """Return a human-readable summary of the character's house.

        Returns ``(success, message)``.
        """
        house = self.houses.get(character.name)
        if house is None:
            return False, "You do not own a house."

        ht = HOUSE_TYPES.get(house["type"], {})
        capacity = self._storage_capacity(house)
        stored_count = len(house.get("storage", []))
        furniture_list = house.get("furniture", [])

        lines = [
            f"\033[1;33m=== {ht.get('name', 'House')} ===\033[0m",
            f"  {ht.get('description', '')}",
            f"  Location: Room {house.get('location_vnum', '?')}",
            f"  Rooms: {ht.get('rooms', '?')}",
            f"  Storage: {stored_count}/{capacity} slots",
            f"  Purchased: {house.get('purchased', 'unknown')}",
        ]

        if furniture_list:
            lines.append("  Furniture:")
            for fk in furniture_list:
                furn = FURNITURE.get(fk, {})
                lines.append(f"    - {furn.get('name', fk)}: {furn.get('description', '')}")
        else:
            lines.append("  Furniture: (none)")

        effects = self.get_house_effects(character)
        if effects:
            lines.append("  Active Effects:")
            for eff, val in effects.items():
                if isinstance(val, bool):
                    lines.append(f"    - {eff}")
                else:
                    lines.append(f"    - {eff}: +{val}")

        return True, "\n".join(lines)

    # -- visiting -----------------------------------------------------------

    def visit_house(self, character, owner_name):
        """Check if *character* can visit *owner_name*'s house.

        Returns ``(success, message, location_vnum | None)``.
        A player can visit any house that exists -- access control may be
        expanded later (locks, guest lists, etc.).
        """
        house = self.houses.get(owner_name)
        if house is None:
            return False, f"{owner_name} does not own a house.", None

        ht = HOUSE_TYPES.get(house["type"], {})
        vnum = house.get("location_vnum")
        return True, (
            f"You visit {owner_name}'s {ht.get('name', 'house')}."
        ), vnum


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_housing_manager = None


def get_housing_manager():
    """Return the global HousingManager instance, creating it on first call."""
    global _housing_manager
    if _housing_manager is None:
        _housing_manager = HousingManager()
    return _housing_manager
