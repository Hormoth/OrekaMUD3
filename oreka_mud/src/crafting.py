import json
import os
import random

# Load recipes from data file
RECIPES = None

def load_recipes():
    global RECIPES
    if RECIPES is not None:
        return RECIPES
    path = os.path.join(os.path.dirname(__file__), '../data/recipes.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            RECIPES = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        RECIPES = get_default_recipes()
    return RECIPES

def get_default_recipes():
    """Default recipes if no data file exists."""
    return [
        {
            "name": "Iron Dagger",
            "skill": "Craft (weaponsmithing)",
            "dc": 12,
            "materials": [{"name": "iron ingot", "qty": 1}],
            "result_vnum": None,
            "result_item": {
                "name": "Iron Dagger",
                "item_type": "weapon",
                "weight": 1,
                "value": 2,
                "damage": [1, 4, 0],
                "material": "iron",
                "description": "A simple iron dagger."
            },
            "time": 1
        },
        {
            "name": "Leather Armor",
            "skill": "Craft (leatherworking)",
            "dc": 12,
            "materials": [{"name": "leather hide", "qty": 2}],
            "result_item": {
                "name": "Leather Armor",
                "item_type": "armor",
                "weight": 15,
                "value": 10,
                "ac_bonus": 2,
                "material": "leather",
                "description": "Armor crafted from leather."
            },
            "time": 2
        },
        {
            "name": "Healing Potion",
            "skill": "Craft (alchemy)",
            "dc": 15,
            "required_feat": "Brew Potion",
            "required_caster_level": 3,
            "materials": [{"name": "healing herb", "qty": 2}, {"name": "glass vial", "qty": 1}],
            "result_item": {
                "name": "Healing Potion",
                "item_type": "potion",
                "weight": 0.5,
                "value": 50,
                "stats": {"healing": 8},
                "description": "A potion that heals 1d8 HP."
            },
            "time": 1
        },
        {
            "name": "Iron Longsword",
            "skill": "Craft (weaponsmithing)",
            "dc": 15,
            "materials": [{"name": "iron ingot", "qty": 2}, {"name": "leather strip", "qty": 1}],
            "result_item": {
                "name": "Iron Longsword",
                "item_type": "weapon",
                "weight": 4,
                "value": 15,
                "damage": [1, 8, 0],
                "material": "iron",
                "description": "A sturdy iron longsword."
            },
            "time": 2
        },
        {
            "name": "Steel Shield",
            "skill": "Craft (armorsmithing)",
            "dc": 15,
            "materials": [{"name": "steel ingot", "qty": 2}, {"name": "leather strip", "qty": 1}],
            "result_item": {
                "name": "Steel Shield",
                "item_type": "shield",
                "weight": 6,
                "value": 9,
                "ac_bonus": 1,
                "material": "steel",
                "description": "A round steel shield."
            },
            "time": 2
        }
    ]


def find_recipe(name):
    """Find recipe by name (case-insensitive, partial match)."""
    recipes = load_recipes()
    name_lower = name.lower()
    for recipe in recipes:
        if recipe["name"].lower() == name_lower:
            return recipe
    for recipe in recipes:
        if name_lower in recipe["name"].lower():
            return recipe
    return None


def check_materials(character, recipe):
    """Check if character has all required materials. Returns (has_all, missing_list)."""
    missing = []
    for mat in recipe["materials"]:
        count = sum(1 for item in character.inventory
                    if item.name.lower() == mat["name"].lower())
        if count < mat["qty"]:
            missing.append(f"{mat['name']} x{mat['qty']} (have {count})")
    return len(missing) == 0, missing


def consume_materials(character, recipe):
    """Remove crafting materials from inventory."""
    for mat in recipe["materials"]:
        removed = 0
        to_remove = []
        for item in character.inventory:
            if item.name.lower() == mat["name"].lower() and removed < mat["qty"]:
                to_remove.append(item)
                removed += 1
        for item in to_remove:
            character.inventory.remove(item)


def craft_item(character, recipe, bonus=0):
    """Attempt to craft an item. Returns (success, message, item_or_none).
    D&D 3.5 rules: magical items require Item Creation feats.
    bonus: additional skill check bonus (e.g. from housing workbench)
    """
    from src.items import Item

    # Check feat requirements for magical recipes
    required_feat = recipe.get("required_feat")
    if required_feat:
        feats = getattr(character, 'feats', [])
        if required_feat not in feats:
            return False, f"You need the '{required_feat}' feat to craft this.", None

    # Check caster level requirement
    required_cl = recipe.get("required_caster_level", 0)
    if required_cl > 0:
        caster_level = getattr(character, 'class_level', 1)
        if caster_level < required_cl:
            return False, f"You need caster level {required_cl} to craft this. You are level {caster_level}.", None

    # Check required spell (for scrolls, potions, wands)
    required_spell = recipe.get("required_spell")
    if required_spell:
        spells_known = getattr(character, 'spells_known', {})
        if required_spell not in spells_known and required_spell.lower() not in [s.lower() for s in spells_known]:
            return False, f"You need to know the spell '{required_spell}' to craft this.", None

    # Check gold cost
    gold_cost = recipe.get("gold_cost", 0)
    if gold_cost > 0:
        if getattr(character, 'gold', 0) < gold_cost:
            return False, f"You need {gold_cost} gold to craft this. You have {getattr(character, 'gold', 0)}.", None

    # Skill check
    skill_name = recipe["skill"]
    dc = recipe["dc"]
    result = character.skill_check(skill_name)
    # Apply crafting bonus (e.g. from housing workbench)
    if bonus and not isinstance(result, str):
        result += bonus

    # Handle untrained
    if isinstance(result, str):
        return False, f"You lack the {skill_name} skill.", None

    if result >= dc:
        # Deduct gold cost on success
        if gold_cost > 0:
            character.gold = getattr(character, 'gold', 0) - gold_cost

        # Use result_vnum if specified, otherwise create from result_item
        result_vnum = recipe.get("result_vnum")
        if result_vnum:
            from src.items import get_item_by_vnum
            item = get_item_by_vnum(result_vnum)
            if not item:
                item_data = recipe.get("result_item", {}).copy()
                item_data["vnum"] = result_vnum
                item = Item.from_dict(item_data)
        else:
            item_data = recipe.get("result_item", {}).copy()
            item_data["vnum"] = 90000 + random.randint(0, 9999)
            item = Item.from_dict(item_data)

        gold_msg = f", Cost: {gold_cost} gp" if gold_cost > 0 else ""
        return True, f"Success! You craft {item.name}. (Check: {result} vs DC {dc}{gold_msg})", item
    elif result < dc - 5:
        # Critical failure - materials AND half gold lost
        if gold_cost > 0:
            lost = gold_cost // 2
            character.gold = getattr(character, 'gold', 0) - lost
            return False, f"Critical failure! Materials ruined, {lost} gold lost. (Check: {result} vs DC {dc})", None
        return False, f"Critical failure! The materials are ruined. (Check: {result} vs DC {dc})", None
    else:
        # Normal failure - materials preserved
        return False, f"You fail to craft the item. Materials preserved. (Check: {result} vs DC {dc})", None
