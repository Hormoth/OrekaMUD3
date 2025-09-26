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
    "Bard": {
        "alignment": "Any nonlawful",
        "hit_die": 6,
        "skill_points": 6,
        "class_skills": [
            "Appraise", "Balance", "Bluff", "Climb", "Concentration", "Craft (any)", "Decipher Script", "Diplomacy", "Disguise", "Escape Artist", "Gather Information", "Hide", "Jump", "Knowledge (all)", "Listen", "Move Silently", "Perform (any)", "Profession (any)", "Sense Motive", "Sleight of Hand", "Speak Language", "Spellcraft", "Swim", "Tumble", "Use Magic Device"
        ],
        "bab_progression": "3/4",
        "save_progression": {"fort": "poor", "ref": "good", "will": "good"},
        "spellcasting": {
            "type": "arcane",
            "start_level": 1,
            "spells_per_day": [
                [2,0,0,0,0,0,0], [3,0,0,0,0,0,0], [3,1,0,0,0,0,0], [3,2,0,0,0,0,0], [3,3,1,0,0,0,0],
                [3,3,2,0,0,0,0], [3,3,2,1,0,0,0], [3,3,3,2,0,0,0], [3,3,3,2,1,0,0], [3,3,3,3,2,0,0],
                [3,3,3,3,2,1,0], [3,3,3,3,3,2,0], [3,3,3,3,3,2,1], [3,3,3,3,3,3,2], [4,3,3,3,3,3,2],
                [4,4,3,3,3,3,3], [4,4,4,3,3,3,3], [4,4,4,4,3,3,3], [4,4,4,4,4,3,3], [4,4,4,4,4,4,3]
            ]
        },
        "features": {
            1: ["Bardic Music", "Bardic Knowledge", "Countersong", "Fascinate", "Inspire Courage +1"],
            2: ["Inspire Competence"],
            6: ["Suggestion"],
            8: ["Inspire Courage +2"],
            9: ["Inspire Greatness"],
            12: ["Song of Freedom"],
            14: ["Inspire Courage +3"],
            15: ["Inspire Heroics"],
            18: ["Mass Suggestion"],
            20: ["Inspire Courage +4"]
        },
        "restrictions": {
            "armor": "Light armor only for spellcasting; arcane spell failure in medium/heavy armor or with shields.",
            "multiclass": "A bard who becomes lawful cannot progress as a bard but retains all abilities."
        }
    },
    "Cleric": {
        "alignment": "Within one step of deity's alignment; not neutral unless deity is neutral",
        "hit_die": 8,
        "skill_points": 2,
        "class_skills": [
            "Concentration", "Craft (any)", "Diplomacy", "Heal", "Knowledge (arcana)", "Knowledge (history)", "Knowledge (religion)", "Knowledge (the planes)", "Profession (any)", "Spellcraft"
        ],
        "bab_progression": "3/4",
        "save_progression": {"fort": "good", "ref": "poor", "will": "good"},
        "spellcasting": {
            "type": "divine",
            "start_level": 1,
            "spells_per_day": [
                [3,1,0,0,0,0,0,0,0,0], [4,2,0,0,0,0,0,0,0,0], [4,2,1,0,0,0,0,0,0,0], [5,3,2,0,0,0,0,0,0,0],
                [5,3,2,1,0,0,0,0,0,0], [5,3,3,2,0,0,0,0,0,0], [6,4,3,2,1,0,0,0,0,0], [6,4,3,3,2,0,0,0,0,0],
                [6,4,4,3,2,1,0,0,0,0], [6,4,4,3,3,2,0,0,0,0], [6,5,4,4,3,2,1,0,0,0], [6,5,4,4,3,3,2,0,0,0],
                [6,5,5,4,4,3,2,1,0,0], [6,5,5,4,4,3,3,2,0,0], [6,5,5,4,4,4,3,2,1,0], [6,5,5,4,4,4,3,3,2,0],
                [6,5,5,4,4,4,4,3,2,1], [6,5,5,4,4,4,4,3,3,2], [6,5,5,4,4,4,4,4,3,2], [6,5,5,4,4,4,4,4,4,4]
            ]
        },
        "features": {
            1: ["Turn or Rebuke Undead", "Domains (2)", "Aura"],
            5: ["Bonus Language: Celestial, Abyssal, Infernal"],
        },
        "restrictions": {
            "alignment": "Must be within one step of deity's alignment.",
            "deity": "Must select two domains from deity; domain restrictions apply.",
            "multiclass": "A cleric who grossly violates code loses all spells and class features until atonement."
        }
    },
    "Druid": {
        "alignment": "Neutral good, lawful neutral, neutral, chaotic neutral, or neutral evil",
        "hit_die": 8,
        "skill_points": 4,
        "class_skills": [
            "Concentration", "Craft (any)", "Diplomacy", "Handle Animal", "Heal", "Knowledge (nature)", "Listen", "Profession (any)", "Ride", "Spellcraft", "Spot", "Survival", "Swim"
        ],
        "bab_progression": "3/4",
        "save_progression": {"fort": "good", "ref": "poor", "will": "good"},
        "spellcasting": {
            "type": "divine",
            "start_level": 1,
            "spells_per_day": [
                [3,1,0,0,0,0,0,0,0,0], [4,2,0,0,0,0,0,0,0,0], [4,2,1,0,0,0,0,0,0,0], [5,3,2,0,0,0,0,0,0,0],
                [5,3,2,1,0,0,0,0,0,0], [5,3,3,2,0,0,0,0,0,0], [6,4,3,2,1,0,0,0,0,0], [6,4,3,3,2,0,0,0,0,0],
                [6,4,4,3,2,1,0,0,0,0], [6,4,4,3,3,2,0,0,0,0], [6,5,4,4,3,2,1,0,0,0], [6,5,4,4,3,3,2,0,0,0],
                [6,5,5,4,4,3,2,1,0,0], [6,5,5,4,4,3,3,2,0,0], [6,5,5,4,4,4,3,2,1,0], [6,5,5,4,4,4,3,3,2,0],
                [6,5,5,4,4,4,4,3,2,1], [6,5,5,4,4,4,4,3,3,2], [6,5,5,4,4,4,4,4,3,2], [6,5,5,4,4,4,4,4,4,4]
            ]
        },
        "features": {
            1: ["Animal Companion", "Nature Sense", "Wild Empathy"],
            2: ["Woodland Stride"],
            3: ["Trackless Step"],
            4: ["Resist Nature's Lure"],
            5: ["Wild Shape (1/day)"],
            6: ["Wild Shape (2/day)"],
            7: ["Wild Shape (3/day)"],
            8: ["Wild Shape (Large)"],
            9: ["Venom Immunity"],
            10: ["Wild Shape (4/day)"],
            11: ["Wild Shape (Tiny)"],
            12: ["Wild Shape (Plant)"],
            13: ["A Thousand Faces"],
            14: ["Wild Shape (5/day)"],
            15: ["Timeless Body", "Wild Shape (Huge)"],
            16: ["Wild Shape (Elemental 1/day)"],
            18: ["Wild Shape (6/day, Elemental 2/day)"],
            20: ["Wild Shape (Elemental 3/day, Huge Elemental)"]
        },
        "restrictions": {
            "armor": "Proficient with light/medium armor (nonmetal only) and wooden shields. Wearing prohibited armor/shields blocks spellcasting and class abilities.",
            "language": "Knows Druidic; forbidden to teach to non-druids.",
            "multiclass": "A druid who ceases to be neutral cannot progress as a druid but retains all abilities."
        }
    },
    "Fighter": {
        "alignment": "Any",
        "hit_die": 10,
        "skill_points": 2,
        "class_skills": [
            "Climb", "Craft (any)", "Handle Animal", "Intimidate", "Jump", "Ride", "Swim"
        ],
        "bab_progression": "full",
        "save_progression": {"fort": "good", "ref": "poor", "will": "poor"},
        "spellcasting": None,
        "features": {
            1: ["Bonus Feat"],
            2: ["Bonus Feat"],
            4: ["Bonus Feat"],
            6: ["Bonus Feat"],
            8: ["Bonus Feat"],
            10: ["Bonus Feat"],
            12: ["Bonus Feat"],
            14: ["Bonus Feat"],
            16: ["Bonus Feat"],
            18: ["Bonus Feat"],
            20: ["Bonus Feat"]
        },
        "restrictions": {}
    },
    "Monk": {
        "alignment": "Any lawful",
        "hit_die": 8,
        "skill_points": 4,
        "class_skills": [
            "Balance", "Climb", "Concentration", "Craft (any)", "Diplomacy", "Escape Artist", "Hide", "Jump", "Knowledge (arcana)", "Knowledge (religion)", "Listen", "Move Silently", "Perform (any)", "Profession (any)", "Sense Motive", "Spot", "Swim", "Tumble"
        ],
        "bab_progression": "3/4",
        "save_progression": {"fort": "good", "ref": "good", "will": "good"},
        "spellcasting": None,
        "features": {
            1: ["Bonus Feat", "Flurry of Blows", "Unarmed Strike"],
            2: ["Bonus Feat", "Evasion"],
            3: ["Still Mind"],
            4: ["Ki Strike (magic)", "Slow Fall 20 ft."],
            5: ["Purity of Body"],
            6: ["Bonus Feat", "Slow Fall 30 ft."],
            7: ["Wholeness of Body"],
            8: ["Slow Fall 40 ft."],
            9: ["Improved Evasion"],
            10: ["Ki Strike (lawful)", "Slow Fall 50 ft."],
            11: ["Diamond Body", "Greater Flurry"],
            12: ["Abundant Step", "Slow Fall 60 ft."],
            13: ["Diamond Soul"],
            14: ["Slow Fall 70 ft."],
            15: ["Quivering Palm"],
            16: ["Ki Strike (adamantine)", "Slow Fall 80 ft."],
            17: ["Timeless Body", "Tongue of the Sun and Moon"],
            18: ["Slow Fall 90 ft."],
            19: ["Empty Body"],
            20: ["Perfect Self", "Slow Fall any distance"]
        },
        "restrictions": {
            "armor": "Not proficient with any armor or shields.",
            "multiclass": "A monk who becomes nonlawful cannot progress as a monk but retains all abilities. If a monk multiclasses, she may never again raise her monk level."
        }
    },
    "Paladin": {
        "alignment": "Lawful good",
        "hit_die": 10,
        "skill_points": 2,
        "class_skills": [
            "Concentration", "Craft (any)", "Diplomacy", "Handle Animal", "Heal", "Knowledge (nobility and royalty)", "Knowledge (religion)", "Profession (any)", "Ride", "Sense Motive"
        ],
        "bab_progression": "full",
        "save_progression": {"fort": "good", "ref": "poor", "will": "good"},
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
            1: ["Aura of Good", "Detect Evil", "Smite Evil 1/day"],
            2: ["Divine Grace", "Lay on Hands"],
            3: ["Aura of Courage", "Divine Health"],
            4: ["Turn Undead"],
            5: ["Smite Evil 2/day", "Special Mount"],
            6: ["Remove Disease 1/week"],
            10: ["Smite Evil 3/day"],
            15: ["Remove Disease 4/week", "Smite Evil 4/day"],
            20: ["Smite Evil 5/day"]
        },
        "restrictions": {
            "alignment": "Must be lawful good. Loses all class abilities if commits evil act.",
            "code": "Must respect authority, act with honor, help those in need, punish evil.",
            "associates": "May not associate with evil characters or those who offend her code.",
            "multiclass": "A paladin who multiclasses may never again raise her paladin level."
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
