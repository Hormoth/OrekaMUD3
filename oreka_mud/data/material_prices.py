# OrekaMUD3 Material Price List (D&D 3.5 inspired)
# All prices are per pound (lb) unless otherwise noted.

MATERIAL_PRICES = {
    # Metals & Alloys
    'iron': 0.1,  # 1 sp
    'steel': 0.2,  # 2 sp
    'copper': 0.5,  # 5 sp
    'brass': 0.5,  # 5 sp
    'bronze': 0.4,  # 4 sp
    'tin': 0.3,  # 3 sp
    'lead': 0.2,  # 2 sp
    'silver': 5.0,  # 5 gp
    'gold': 50.0,  # 50 gp
    'platinum': 500.0,  # 500 gp
    'mithral': 500.0,  # 500 gp
    'adamantine': 5000.0,  # 5,000 gp
    'electrum': 25.0,  # 25 gp
    'cold iron': 0.4,  # 4 sp

    # Woods (Common & Rare)
    'oak': 0.05,  # 5 cp
    'pine': 0.04,  # 4 cp
    'ash': 0.06,  # 6 cp
    'yew': 0.1,  # 1 sp
    'mahogany': 0.2,  # 2 sp
    'darkwood': 10.0,  # 10 gp
    'teak': 0.1,  # 1 sp
    'maple': 0.05,  # 5 cp
    'ebony': 0.5,  # 5 sp
    'bamboo': 0.02,  # 2 cp

    # Stones & Minerals
    'stone': 0.01,  # 1 cp
    'marble': 1.0,  # 1 gp
    'granite': 0.2,  # 2 sp
    'slate': 0.05,  # 5 cp
    'limestone': 0.02,  # 2 cp
    'obsidian': 0.1,  # 1 sp
    'alabaster': 0.1,  # 1 sp
    'quartz': 1.0,  # 1 gp
    'salt': 0.01,  # 1 cp
    'sulfur': 0.02,  # 2 cp
    'saltpeter': 0.1,  # 1 sp
    'coal': 0.01,  # 1 cp
    'chalk': 0.01,  # 1 cp/stick
    'flint': 0.01,  # 1 cp/piece
    'sand': 0.01,  # 1 cp
    'sandstone': 0.02,  # 2 cp
    'pumice': 0.02,  # 2 cp
    'amber': 10.0,  # 10 gp
    'jade': 100.0,  # 100 gp
    # Gems: use variable pricing

    # Animal & Monster Parts
    'leather': 0.2,  # 2 sp
    'wool': 0.1,  # 1 sp
    'feather': 0.01,  # 1 cp/each
    'animal hide': 0.1,  # 1 sp
    'bone': 0.01,  # 1 cp
    'horn': 0.02,  # 2 cp
    'ivory': 5.0,  # 5 gp
    'shell': 0.1,  # 1 sp
    'silk': 10.0,  # 10 gp
    'spider silk': 50.0,  # 50 gp
    'chitin': 0.2,  # 2 sp
    'sinew': 0.1,  # 1 sp
    'blood': 0.01,  # 1 cp/vial (beast)
    'dragon blood': 100.0,  # 100 gp/vial
    'scales': 0.1,  # 1 sp/lb (lizard, fish)
    'dragon scales': 100.0,  # 100 gp/lb
    'claws': 0.1,  # 1 sp/each (beast)
    'dragon claws': 50.0,  # 50 gp/each
    'hair': 0.01,  # 1 cp/lb
    'eggs': 10.0,  # 10 gp/each (giant, monster)
    'dragonhide': 500.0,  # 500 gp/lb
    'dragon bone': 200.0,  # 200 gp/lb
    'venom gland': 50.0,  # 50 gp/vial
    'monster eye': 100.0,  # 100 gp/each
    'monster heart': 10.0,  # 10 gp/each

    # Alchemical Reagents & Spell Components
    'bat guano': 0.01,  # 1 cp/lb
    'charcoal': 0.01,  # 1 cp/lb
    'clay': 0.01,  # 1 cp/lb
    'crystal': 1.0,  # 1 gp/each
    'fur': 0.1,  # 1 sp/lb
    'incense': 1.0,  # 1 gp/oz
    'mistletoe': 0.01,  # 1 cp/sprig
    'pearl': 100.0,  # 100 gp/each
    'phosphorus': 5.0,  # 5 gp/lb
    'powdered iron': 0.2,  # 2 sp/lb
    'powdered silver': 6.0,  # 6 gp/lb
    'resin': 0.02,  # 2 cp/lb
    'ruby dust': 100.0,  # 100 gp/oz
    'myrrh': 5.0,  # 5 gp/oz
    'frankincense': 5.0,  # 5 gp/oz
    'mercury': 1.0,  # 1 gp/lb
    'quicklime': 0.1,  # 1 sp/lb
    'bitumen': 0.01,  # 1 cp/lb
    'camphor': 1.0,  # 1 gp/oz
    'rare herb': 5.0,  # 5 gp/oz (average)
    'moss': 0.1,  # 1 sp/lb
    'bark': 0.01,  # 1 cp/lb
    'sap': 0.01,  # 1 cp/oz
    'flower': 0.01,  # 1 cp/each
    'seed': 0.01,  # 1 cp/each
    'root': 0.01,  # 1 cp/oz
    'mushroom': 0.01,  # 1 cp/each
    'ambergris': 50.0,  # 50 gp/oz
    'dragon's blood': 500.0,  # 500 gp/vial
    'bone ash': 0.1,  # 1 sp/lb
    'ash': 0.01,  # 1 cp/lb
    'perfume': 5.0,  # 5 gp/oz
    'tincture': 1.0,  # 1 gp/oz
    'distilled spirits': 0.2,  # 2 sp/bottle
    'indigo': 1.0,  # 1 gp/oz
    'saffron': 15.0,  # 15 gp/oz
    'ochre': 0.1,  # 1 sp/lb

    # Liquids & Extracts
    'water': 0.01,  # 1 cp/gallon
    'oil': 0.1,  # 1 sp/pint
    'wine': 0.2,  # 2 sp/bottle
    'ale': 0.04,  # 4 cp/mug
    'vinegar': 0.1,  # 1 sp/bottle
    'honey': 0.1,  # 1 sp/lb
    'milk': 0.02,  # 2 cp/pint

    # Other Trade Goods & Special Items
    'paper': 0.4,  # 4 sp/sheet
    'parchment': 0.2,  # 2 sp/sheet
    'canvas': 0.2,  # 2 sp/sq yd
    'burlap': 0.1,  # 1 sp/sq yd
    'cotton': 0.05,  # 5 cp/lb
    'hemp': 0.1,  # 1 sp/lb
    'plant oil': 0.1,  # 1 sp/pint
    'fat': 0.01,  # 1 cp/lb
    'lye': 0.01,  # 1 cp/lb
    'tallow': 0.01,  # 1 cp/lb
    'rope fiber': 0.05,  # 5 cp/lb
    'salt': 0.01,  # 1 cp/lb
    'spice': 5.0,  # 5 gp/lb (average)
    'grain': 0.01,  # 1 cp/lb
    'trade bar (iron)': 0.5,  # 5 gp/bar (10 lbs)
    'trade bar (silver)': 5.0,  # 50 gp/bar (10 lbs)
    'trade bar (gold)': 50.0,  # 500 gp/bar (10 lbs)
    'trade bar (platinum)': 500.0,  # 5,000 gp/bar (10 lbs)

    # Special Magic Item Materials
    'elemental essence': 500.0,  # 500 gp/vial
    'star metal': 5000.0,  # 5,000 gp/lb
    'ectoplasm': 100.0,  # 100 gp/vial
    'demon ichor': 250.0,  # 250 gp/vial
    'angel feather': 100.0,  # 100 gp/each
}
