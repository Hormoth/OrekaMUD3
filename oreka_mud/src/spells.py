# D&D 3.5 Domain data: domain_name -> {"power": str, "spells": {level: spell_name}}
DOMAIN_DATA = {
    "Air": {
        "power": "Turn/rebuke earth creatures, +1 caster level with [Air] spells.",
        "spells": {
            1: "Obscuring Mist",
            2: "Wind Wall",
            3: "Gaseous Form",
            4: "Air Walk",
            5: "Control Winds",
            6: "Chain Lightning",
            7: "Control Weather",
            8: "Whirlwind",
            9: "Elemental Swarm (air only)"
        }
    },
    "Animal": {
        "power": "Knowledge (nature) as class skill, speak with animals 1/day.",
        "spells": {
            1: "Calm Animals",
            2: "Hold Animal",
            3: "Dominate Animal",
            4: "Summon Nature’s Ally IV",
            5: "Commune with Nature",
            6: "Antilife Shell",
            7: "Animal Shapes",
            8: "Summon Nature’s Ally VIII",
            9: "Shapechange"
        }
    },
    "Chaos": {
        "power": "Cast chaos spells at +1 caster level.",
        "spells": {
            1: "Protection from Law",
            2: "Shatter",
            3: "Magic Circle against Law",
            4: "Chaos Hammer",
            5: "Dispel Law",
            6: "Animate Objects",
            7: "Word of Chaos",
            8: "Cloak of Chaos",
            9: "Summon Monster IX (chaotic only)"
        }
    },
    "Death": {
        "power": "Rebuke/command undead, Death Touch (slay living, limited uses).",
        "spells": {
            1: "Cause Fear",
            2: "Death Knell",
            3: "Animate Dead",
            4: "Death Ward",
            5: "Slay Living",
            6: "Create Undead",
            7: "Destruction",
            8: "Create Greater Undead",
            9: "Wail of the Banshee"
        }
    },
    # ... Add all other domains as needed ...
}
# spells.py
"""
Central D&D 3.5 spell data for OrekaMUD.
Contains spell definitions, class/level mapping, and descriptions.
"""

# Example spell structure:
# {
#   "name": "Magic Missile",
#   "level": {"Wizard": 1, "Sorcerer": 1},
#   "school": "Evocation",
#   "description": "A missile of magical energy darts forth...",
#   "components": ["V", "S"],
#   "casting_time": "1 action",
#   "range": "100 ft. + 10 ft./level",
#   "target": "Up to five creatures",
#   "duration": "Instantaneous",
#   "saving_throw": "None",
#   "spell_resistance": "Yes"
# }

SPELLS = [
    {
        "name": "Magic Missile",
        "level": {"Wizard": 1, "Sorcerer": 1},
        "school": "Evocation",
        "description": "A missile of magical energy darts forth from your fingertip and strikes its target, dealing 1d4+1 force damage. Additional missiles at higher levels.",
        "components": ["V", "S"],
        "casting_time": "1 action",
        "range": "100 ft. + 10 ft./level",
        "target": "Up to five creatures",
        "duration": "Instantaneous",
        "saving_throw": "None",
        "spell_resistance": "Yes"
    },
    {
        "name": "Cure Light Wounds",
        "level": {"Cleric": 1, "Bard": 1, "Paladin": 1, "Ranger": 2},
        "school": "Conjuration (Healing)",
        "description": "Heals 1d8 +1/level (max +5) hit points.",
        "components": ["V", "S"],
        "casting_time": "1 action",
        "range": "Touch",
        "target": "Creature touched",
        "duration": "Instantaneous",
        "saving_throw": "Will half (harmless)",
        "spell_resistance": "Yes (harmless)"
    },
    {
        "name": "Fireball",
        "level": {"Wizard": 3, "Sorcerer": 3},
        "school": "Evocation [Fire]",
        "description": "A fireball detonates with a low roar, dealing 1d6 fire damage per caster level (max 10d6) in a 20-ft.-radius spread.",
        "components": ["V", "S", "M"],
        "casting_time": "1 action",
        "range": "Long (400 ft. + 40 ft./level)",
        "area": "20-ft.-radius spread",
        "duration": "Instantaneous",
        "saving_throw": "Reflex half",
        "spell_resistance": "Yes"
    },
    # ... Add more spells as needed ...
]

# Helper: Map class to spells by level
def get_spells_for_class(cls_name, level):
    """Return list of spells available to a class at a given level."""
    return [spell for spell in SPELLS if cls_name in spell["level"] and spell["level"][cls_name] <= level]

# Helper: Map spell name to spell data
def get_spell_by_name(name):
    for spell in SPELLS:
        if spell["name"].lower() == name.lower():
            return spell
    return None
