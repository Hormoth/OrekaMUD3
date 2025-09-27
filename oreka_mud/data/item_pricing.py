# OrekaMUD3 Item Pricing Formulae
# Fastest access: Python functions and dictionaries

COMPLEXITY_MULTIPLIERS = {
    'simple': 1,
    'standard': 2,
    'intermediate': 5,
    'advanced': 10,
    'masterwork': 10,  # Use advanced multiplier, plus flat surcharge
}

MASTERWORK_SURCHARGE = 300  # gp, flat surcharge for masterwork items


def calculate_item_cost(material_value, complexity, is_masterwork=False):
    """
    Calculate the cost of an item based on material value, complexity, and masterwork status.
    material_value: float (in gp, sum of all main materials)
    complexity: str (one of 'simple', 'standard', 'intermediate', 'advanced', 'masterwork')
    is_masterwork: bool (if True, applies masterwork rules)
    Returns: float (cost in gp)
    """
    multiplier = COMPLEXITY_MULTIPLIERS.get(complexity, 1)
    cost = material_value * multiplier
    if is_masterwork or complexity == 'masterwork':
        cost = (material_value * COMPLEXITY_MULTIPLIERS['masterwork']) + MASTERWORK_SURCHARGE
    return cost

# Example usage:
# from oreka_mud.data.material_prices import MATERIAL_PRICES
# iron_sword_cost = calculate_item_cost(MATERIAL_PRICES['iron'], 'standard')
# masterwork_sword_cost = calculate_item_cost(MATERIAL_PRICES['iron'], 'masterwork', is_masterwork=True)
