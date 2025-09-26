"""
D&D 3.5 Class Definitions for OrekaMUD
This file defines the core classes, their features, and progression tables.
"""

# Armor Proficiency and Class Feature Limits (OrekaMUD / D&D 3.5)
#
# Barbarian: Light, Medium. No Fast Movement/Rage in Medium/Heavy armor.
# Rogue: Light. Evasion and similar features only in Light armor.
# Ranger: Light, Medium. Combat Style only in Light armor.
# Wizard: None. Arcane spell failure in any armor.
# Sorcerer: None. Arcane spell failure in any armor.
#
# | Class      | Armor Proficiency         | Class Feature Limits                |
# |------------|--------------------------|-------------------------------------|
# | Barbarian  | Light, Medium            | No Fast Movement/Rage in Med/Heavy  |
# | Rogue      | Light                    | Evasion, etc. only in Light         |
# | Ranger     | Light, Medium            | Combat Style only in Light          |
# | Wizard     | None                     | Arcane spell failure in any armor   |
# | Sorcerer   | None                     | Arcane spell failure in any armor   |
#
# If you want to enforce these limits in code (e.g., block abilities or warn players), let the dev team know!

CLASSES = {
    "Barbarian": {
        "alignment": "Any nonlawful",
        "hit_die": 12,
        "skill_points": 4,
        "class_skills": [
            "Climb", "Craft (any)", "Handle Animal", "Intimidate", "Jump", "Listen", "Ride", "Survival", "Swim"
        ],
        "bab_progression": "full",
        "save_progression": {"fort": "good", "ref": "poor", "will": "poor"},
        "spellcasting": None,
        "features": {
            1: ["Fast Movement", "Illiteracy", "Rage 1/day"],
            2: ["Uncanny Dodge"],
            3: ["Trap Sense +1"],
            4: ["Rage 2/day"],
            5: ["Improved Uncanny Dodge"],
            6: ["Trap Sense +2"],
            7: ["Damage Reduction 1/-"],
            8: ["Rage 3/day"],
            9: ["Trap Sense +3"],
            10: ["Damage Reduction 2/-"],
            11: ["Greater Rage"],
            12: ["Rage 4/day", "Trap Sense +4"],
            13: ["Damage Reduction 3/-"],
            14: ["Indomitable Will"],
            15: ["Trap Sense +5"],
            16: ["Damage Reduction 4/-", "Rage 5/day"],
            17: ["Tireless Rage"],
            18: ["Trap Sense +6"],
            19: ["Damage Reduction 5/-"],
            20: ["Mighty Rage", "Rage 6/day"]
        }
    },
    "Rogue": {
        "alignment": "Any",
        "hit_die": 6,
        "skill_points": 8,
        "class_skills": [
            "Appraise", "Balance", "Bluff", "Climb", "Craft (any)", "Decipher Script", "Diplomacy", "Disable Device", "Disguise", "Escape Artist", "Forgery", "Gather Information", "Hide", "Intimidate", "Jump", "Knowledge (local)", "Listen", "Move Silently", "Open Lock", "Perform (any)", "Profession (any)", "Search", "Sense Motive", "Sleight of Hand", "Spot", "Swim", "Tumble", "Use Magic Device"
        ],
        "bab_progression": "3/4",
        "save_progression": {"fort": "poor", "ref": "good", "will": "poor"},
        "spellcasting": None,
        "features": {
            1: ["Sneak Attack +1d6", "Trapfinding"],
            2: ["Evasion"],
            3: ["Trap Sense +1"],
            4: ["Uncanny Dodge"],
            5: ["Sneak Attack +3d6"],
            8: ["Improved Uncanny Dodge"],
            10: ["Special Ability"],
            20: ["Sneak Attack +10d6"]
        }
    },
    "Ranger": {
        "alignment": "Any",
        "hit_die": 8,
        "skill_points": 6,
        "class_skills": [
            "Climb", "Concentration", "Craft (any)", "Handle Animal", "Heal", "Hide", "Jump",
            "Knowledge (dungeoneering)", "Knowledge (geography)", "Knowledge (nature)", "Listen", "Move Silently",
            "Profession (any)", "Ride", "Search", "Spot", "Survival", "Swim", "Use Rope"
        ],
        "bab_progression": "full",
        "save_progression": {"fort": "good", "ref": "good", "will": "poor"},
        "spellcasting": {
            "type": "divine",
            "start_level": 4,
            "spells_per_day": [
                [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0],
                [1,0,0,0], [1,0,0,0], [1,0,0,0], [1,0,0,0], [1,1,0,0],
                [1,1,0,0], [1,1,1,0], [1,1,1,0], [2,1,1,0], [2,1,1,1],
                [2,2,1,1], [2,2,2,1], [3,2,2,1], [3,3,2,2], [3,3,3,3]
            ]
        },
        "features": {
            1: ["1st Favored Enemy", "Track", "Wild Empathy"],
            2: ["Combat Style"],
            3: ["Endurance"],
            4: ["Animal Companion"],
            5: ["2nd Favored Enemy"],
            6: ["Improved Combat Style"],
            7: ["Woodland Stride"],
            8: ["Swift Tracker"],
            9: ["Evasion"],
            10: ["3rd Favored Enemy"],
            11: ["Combat Style Mastery"],
            13: ["Camouflage"],
            15: ["4th Favored Enemy"],
            17: ["Hide in Plain Sight"],
            20: ["5th Favored Enemy"]
        }
    },
    "Wizard": {
        "alignment": "Any",
        "hit_die": 4,
        "skill_points": 2,
        "class_skills": [
            "Concentration", "Craft (any)", "Decipher Script", "Knowledge (all)", "Profession (any)", "Spellcraft"
        ],
        "bab_progression": "1/2",
        "save_progression": {"fort": "poor", "ref": "poor", "will": "good"},
        "spellcasting": {
            "type": "arcane",
            "start_level": 1,
            "spells_per_day": [
                [3,1,0,0,0,0,0,0,0,0], [4,2,0,0,0,0,0,0,0,0], [4,2,1,0,0,0,0,0,0,0], [4,3,2,0,0,0,0,0,0,0],
                [4,3,2,1,0,0,0,0,0,0], [4,3,3,2,0,0,0,0,0,0], [4,4,3,2,1,0,0,0,0,0], [4,4,3,3,2,0,0,0,0,0],
                [4,4,4,3,2,1,0,0,0,0], [4,4,4,3,3,2,0,0,0,0], [4,4,4,4,3,2,1,0,0,0], [4,4,4,4,3,3,2,0,0,0],
                [4,4,4,4,4,3,2,1,0,0], [4,4,4,4,4,3,3,2,0,0], [4,4,4,4,4,4,3,2,1,0], [4,4,4,4,4,4,3,3,2,0],
                [4,4,4,4,4,4,4,3,2,1], [4,4,4,4,4,4,4,3,3,2], [4,4,4,4,4,4,4,4,3,2], [4,4,4,4,4,4,4,4,4,4]
            ]
        },
        "features": {
            1: ["Summon Familiar", "Scribe Scroll"],
            5: ["Bonus Feat"],
            10: ["Bonus Feat"],
            15: ["Bonus Feat"],
            20: ["Bonus Feat"]
        }
    },
    "Sorcerer": {
        "alignment": "Any",
        "hit_die": 4,
        "skill_points": 2,
        "class_skills": [
            "Bluff", "Concentration", "Craft (any)", "Knowledge (arcana)", "Profession (any)", "Spellcraft"
        ],
        "bab_progression": "1/2",
        "save_progression": {"fort": "poor", "ref": "poor", "will": "good"},
        "spellcasting": {
            "type": "arcane",
            "start_level": 1,
            "spells_per_day": [
                [5,3,0,0,0,0,0,0,0,0], [6,4,0,0,0,0,0,0,0,0], [6,5,0,0,0,0,0,0,0,0], [6,6,2,0,0,0,0,0,0,0],
                [6,6,3,0,0,0,0,0,0,0], [6,6,3,1,0,0,0,0,0,0], [6,6,4,2,0,0,0,0,0,0], [6,6,4,2,1,0,0,0,0,0],
                [6,6,4,3,2,0,0,0,0,0], [6,6,4,3,2,1,0,0,0,0], [6,6,4,3,3,2,0,0,0,0], [6,6,4,3,3,2,1,0,0,0],
                [6,6,4,3,3,2,1,1,0,0], [6,6,4,3,3,2,1,1,1,0], [6,6,4,3,3,2,1,1,1,1], [6,6,4,3,3,2,1,1,1,1],
                [6,6,4,3,3,2,1,1,1,1], [6,6,4,3,3,2,1,1,1,1], [6,6,4,3,3,2,1,1,1,1], [6,6,4,3,3,2,1,1,1,1]
            ]
        },
        "features": {
            1: ["Summon Familiar"],
            7: ["Bonus Feat"],
            14: ["Bonus Feat"],
            20: ["Bonus Feat"]
        }
    }
}
