"""
Races of Oreka -- D&D 3.5 Racial Definitions for OrekaMUD

Every playable race from the Races of Oreka Compendium is defined here
with full mechanical stats: ability modifiers, size, speed, vision,
proficiencies, elemental affinities, Kin-sense categories, and more.

Kin-Sense Categories
--------------------
  harmonic       - Attuned to the Kin (standard registration).
  wild_static    - Former Breach-born or wild creatures developing
                   harmonic resonance.
  breach_static  - Still carrying Breach resonance.
  null           - No resonance detected; Silentborn trait.
  void           - Anti-resonance (not currently playable).
  none           - Completely outside the Kin-sense spectrum (Farborn).
"""

# ---------------------------------------------------------------------------
# RACES dictionary
# ---------------------------------------------------------------------------

RACES = {
    # -------------------------------------------------------------------
    # ELVES
    # -------------------------------------------------------------------
    "Hasura Elf": {
        "name": "Hasura Elf",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Int": 2, "Con": -2},
        "vision": "Low-Light Vision",
        "languages_auto": ["Common", "Elven"],
        "languages_bonus": ["Draconic", "Gnoll", "Gnome", "Goblin", "Orc", "Sylvan"],
        "skill_bonuses": {"Listen": 2, "Search": 2, "Perform(wind instruments)": 2},
        "spell_like": [
            "Dancing lights 1/day",
            "Lightweave (prestidigitation 1/day, light effects only; +2 racial bonus on saves vs light spells)",
        ],
        "special": [
            "Immune to magical sleep effects",
            "+2 racial bonus on saves vs enchantment spells and effects",
        ],
        "elemental_affinity": "wind",
        "elemental_resistance": {},
        "weapon_proficiencies": ["longsword", "rapier", "longbow", "shortbow"],
        "armor_proficiencies": [],
        "immunities": ["magical sleep"],
        "favored_class": "Wizard",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Pasua Elf": {
        "name": "Pasua Elf",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Cha": 2, "Con": -2},
        "vision": "Low-Light Vision",
        "languages_auto": ["Common", "Elven"],
        "languages_bonus": ["Draconic", "Gnoll", "Gnome", "Goblin", "Orc", "Sylvan"],
        "skill_bonuses": {"Listen": 2, "Perform(wind instruments)": 2, "Diplomacy": 2},
        "spell_like": [
            "Charm person 1/day (DC 11 + Cha modifier)",
        ],
        "special": [
            "Immune to magical sleep effects",
            "+2 racial bonus on saves vs enchantment spells and effects",
        ],
        "elemental_affinity": "wind",
        "elemental_resistance": {},
        "weapon_proficiencies": ["longsword", "rapier", "longbow", "shortbow"],
        "armor_proficiencies": [],
        "immunities": ["magical sleep"],
        "favored_class": "Bard",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Na'wasua Elf": {
        "name": "Na'wasua Elf",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Wis": 2, "Con": -2},
        "vision": "Low-Light Vision",
        "languages_auto": ["Common", "Elven"],
        "languages_bonus": ["Draconic", "Gnoll", "Gnome", "Goblin", "Orc", "Sylvan"],
        "skill_bonuses": {"Listen": 2, "Search": 2, "Knowledge(arcana)": 2},
        "spell_like": [
            "Detect thoughts 1/day (DC 12 + Wis modifier)",
            "Starlit Vision: +2 Spot checks under starlight; guidance 1/day",
        ],
        "special": [
            "Immune to magical sleep effects",
            "+2 racial bonus on saves vs enchantment spells and effects",
            "Starlit Vision: +2 Spot under starlight, guidance 1/day",
        ],
        "elemental_affinity": "wind",
        "elemental_resistance": {},
        "weapon_proficiencies": ["longsword", "rapier", "longbow", "shortbow"],
        "armor_proficiencies": [],
        "immunities": ["magical sleep"],
        "favored_class": "Cleric",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Kovaka Elf": {
        "name": "Kovaka Elf",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Str": 2, "Con": 2, "Dex": -2},
        "vision": "Low-Light Vision",
        "languages_auto": ["Common", "Elven"],
        "languages_bonus": ["Draconic", "Gnoll", "Gnome", "Goblin", "Orc", "Sylvan"],
        "skill_bonuses": {"Listen": 2, "Survival": 2, "Craft(stone)": 2},
        "spell_like": [
            "Stone shape 1/day",
        ],
        "special": [
            "Immune to magical sleep effects",
            "+2 racial bonus on saves vs enchantment spells and effects",
            "Earth's Resilience: +2 saves vs earth effects, +1 natural armor bonus",
        ],
        "elemental_affinity": "wind",
        "elemental_resistance": {"acid": 5},
        "weapon_proficiencies": ["longsword", "rapier", "longbow", "shortbow"],
        "armor_proficiencies": ["light"],
        "immunities": ["magical sleep"],
        "favored_class": "Fighter",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },

    # -------------------------------------------------------------------
    # DWARVES
    # -------------------------------------------------------------------
    "Visetri Dwarf": {
        "name": "Visetri Dwarf",
        "size": "Medium",
        "speed": 20,
        "ability_mods": {"Con": 2, "Wis": 2, "Dex": -2},
        "vision": "Darkvision 60 ft.",
        "languages_auto": ["Common", "Dwarven"],
        "languages_bonus": ["Giant", "Gnome", "Goblin", "Orc", "Terran", "Undercommon"],
        "skill_bonuses": {"Appraise(metal/stone)": 2, "Craft(stone or metal)": 2},
        "spell_like": [
            "Stone shape 1/day",
        ],
        "special": [
            "Stability: +4 bonus on ability checks to resist bull rush or trip",
            "Stone's Memory: +2 racial bonus on Appraise checks related to stone or metal",
            "Speed not reduced by medium or heavy armor",
        ],
        "elemental_affinity": "earth",
        "elemental_resistance": {"acid": 5},
        "weapon_proficiencies": ["warhammer", "battleaxe", "heavy pick"],
        "armor_proficiencies": ["light", "medium", "heavy", "shields"],
        "immunities": [],
        "favored_class": "Fighter or Cleric",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Pekakarlik Dwarf": {
        "name": "Pekakarlik Dwarf",
        "size": "Small",
        "speed": 20,
        "ability_mods": {"Con": 2, "Dex": 2, "Cha": -2},
        "vision": "Darkvision 60 ft.",
        "languages_auto": ["Common", "Dwarven"],
        "languages_bonus": ["Aquan", "Giant", "Gnome", "Goblin", "Orc", "Undercommon"],
        "skill_bonuses": {"Swim": 2, "Craft(boats)": 2, "Profession(sailor)": 2},
        "spell_like": [
            "Create water 1/day",
        ],
        "special": [
            "Swim speed 20 ft.",
        ],
        "elemental_affinity": "water",
        "elemental_resistance": {"fire": 5},
        "weapon_proficiencies": ["warhammer", "battleaxe", "heavy pick"],
        "armor_proficiencies": ["light", "medium", "heavy", "shields"],
        "immunities": [],
        "favored_class": "Rogue",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Rarozhki Dwarf": {
        "name": "Rarozhki Dwarf",
        "size": "Medium",
        "speed": 20,
        "ability_mods": {"Str": 2, "Int": 2, "Dex": -1, "Cha": -1},
        "vision": "Darkvision 60 ft.",
        "languages_auto": ["Common", "Dwarven"],
        "languages_bonus": ["Giant", "Gnome", "Goblin", "Ignan", "Orc", "Undercommon"],
        "skill_bonuses": {
            "Craft(metal)": 2,
            "Knowledge(engineering)": 2,
            "Perception(stonework)": 2,
        },
        "spell_like": [
            "Heat metal 1/day",
        ],
        "special": [
            "Ember's Might: +1 racial bonus on attack rolls vs orcs and goblinoids",
            "Ember's Might: +2 racial bonus on saves vs fire effects",
            "Stability: +4 bonus on ability checks to resist bull rush or trip",
            "Speed not reduced by medium or heavy armor",
        ],
        "elemental_affinity": "fire",
        "elemental_resistance": {"fire": 10},
        "weapon_proficiencies": ["all simple", "all martial"],
        "armor_proficiencies": ["light", "medium", "heavy", "shields", "tower shields"],
        "immunities": [],
        "favored_class": "Fighter or Wizard",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },

    # -------------------------------------------------------------------
    # HALFLING
    # -------------------------------------------------------------------
    "Halfling": {
        "name": "Halfling",
        "size": "Small",
        "speed": 20,
        "ability_mods": {"Dex": 2, "Cha": 1, "Str": -1},
        "vision": "Normal",
        "languages_auto": ["Common", "Halfling"],
        "languages_bonus": ["Dwarven", "Elven", "Gnome", "Goblin", "Orc"],
        "skill_bonuses": {"Climb": 2, "Swim": 2, "Move Silently": 2},
        "spell_like": [
            "Create water 1/day",
        ],
        "special": [
            "Sea's Luck: +2 racial bonus on saves vs fear; +1 dodge bonus to AC when near water",
            "Halfling Agility: +1 racial bonus on all saving throws (stacks with Sea's Luck for +3 vs fear)",
            "Sure-Footed: move through natural difficult terrain at normal speed",
            "+1 racial bonus on attack rolls with thrown weapons and slings",
        ],
        "elemental_affinity": "water",
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple", "sling"],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Rogue",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },

    # -------------------------------------------------------------------
    # HUMANS
    # -------------------------------------------------------------------
    "Eruskan Human": {
        "name": "Eruskan Human",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Int": 2, "Dex": 1, "Wis": 1},
        "vision": "Normal",
        "languages_auto": ["Common", "Eruskan"],
        "languages_bonus": ["Aquan", "Dwarven", "Elven", "Halfling", "Sylvan"],
        "skill_bonuses": {"Swim": 2, "Profession(sailor)": 2, "Diplomacy": 2},
        "spell_like": [
            "Create water 1/day",
        ],
        "special": [
            "Water's Grace: +2 racial bonus on Swim (stacks with skill bonus); +1 dodge bonus to AC while in or on water",
            "Bonus feat at 1st level",
        ],
        "elemental_affinity": "water",
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple"],
        "armor_proficiencies": ["light"],
        "immunities": [],
        "favored_class": "Any",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Mytroan Human": {
        "name": "Mytroan Human",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Wis": 1, "Cha": 1},
        "vision": "Normal",
        "languages_auto": ["Common", "Mytroan"],
        "languages_bonus": ["Auran", "Dwarven", "Elven", "Halfling", "Sylvan"],
        "skill_bonuses": {"Ride": 2, "Survival": 2, "Handle Animal": 2},
        "spell_like": [
            "Feather fall 1/day",
        ],
        "special": [
            "Windrider's Grace: +2 racial bonus on Ride (stacks with skill bonus); +1 Reflex save in open terrain",
            "Bonus feat at 1st level",
        ],
        "elemental_affinity": "wind",
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple"],
        "armor_proficiencies": ["light"],
        "immunities": [],
        "favored_class": "Any",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Taraf-Imro Human": {
        "name": "Taraf-Imro Human",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Str": 2, "Con": 1, "Cha": 1},
        "vision": "Normal",
        "languages_auto": ["Common", "Taraf-Imro"],
        "languages_bonus": ["Dwarven", "Giant", "Goblin", "Ignan", "Orc"],
        "skill_bonuses": {"Intimidate": 2, "Craft(metal)": 2, "Climb": 2},
        "spell_like": [
            "Produce flame 1/day",
        ],
        "special": [
            "Fire's Fury: +2 damage with fire attacks and fire spells; +1 racial bonus on saves vs fire",
            "Bonus feat at 1st level",
        ],
        "elemental_affinity": "fire",
        "elemental_resistance": {"fire": 5},
        "weapon_proficiencies": ["all simple", "all martial"],
        "armor_proficiencies": ["light", "medium"],
        "immunities": [],
        "favored_class": "Any",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },
    "Orean Human": {
        "name": "Orean Human",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Con": 2, "Str": 1, "Wis": 1},
        "vision": "Normal",
        "languages_auto": ["Common", "Orean"],
        "languages_bonus": ["Dwarven", "Giant", "Gnome", "Halfling", "Terran"],
        "skill_bonuses": {"Craft(stone)": 2, "Knowledge(nature)": 2, "Profession(farmer)": 2},
        "spell_like": [
            "Stone shape 1/day",
        ],
        "special": [
            "Earth's Stability: +2 racial bonus on saves vs earth effects; +1 CMD vs bull rush",
            "Bonus feat at 1st level",
        ],
        "elemental_affinity": "earth",
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple"],
        "armor_proficiencies": ["light", "medium"],
        "immunities": [],
        "favored_class": "Any",
        "level_adjustment": 0,
        "kin_sense_category": "harmonic",
    },

    # -------------------------------------------------------------------
    # HALF-GIANT
    # -------------------------------------------------------------------
    "Half-Giant": {
        "name": "Half-Giant",
        "size": "Large",
        "speed": 30,
        "ability_mods": {"Str": 4, "Con": 2, "Dex": -2, "Cha": -2},
        "vision": "Low-Light Vision",
        "languages_auto": ["Common", "Giant"],
        "languages_bonus": ["Dwarven", "Gnome", "Goblin", "Orc", "Terran", "Ignan"],
        "skill_bonuses": {"Craft(stone)": 2, "Knowledge(nature)": 2},
        "spell_like": [
            "Stone shape OR produce flame 1/day (chosen each day at dawn)",
        ],
        "special": [
            "Large size: 10 ft. space, 10 ft. natural reach",
            "-1 size penalty to AC, -1 size penalty on attack rolls",
            "+4 size bonus on grapple checks",
            "Lifting and carrying limits x2 those of Medium characters",
        ],
        "elemental_affinity": "all",
        "elemental_resistance": {"fire": 5},
        "weapon_proficiencies": ["all simple", "all martial"],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Fighter",
        "level_adjustment": 1,
        "kin_sense_category": "harmonic",
    },

    # -------------------------------------------------------------------
    # SILENTBORN
    # -------------------------------------------------------------------
    "Silentborn": {
        "name": "Silentborn",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Wis": 2, "Dex": 2, "Cha": -2},
        "vision": "Darkvision 30 ft.",
        "languages_auto": ["Common"],
        "languages_bonus": ["Dwarven", "Elven", "Gnome", "Goblin", "Halfling", "Orc"],
        "skill_bonuses": {"Hide": 2, "Sense Motive": 2, "Spot": 2},
        "spell_like": [
            "Detect thoughts 1/day",
        ],
        "special": [
            "Silent Echo: 1/day gain +4 insight bonus on a single Spot, Listen, or Sense Motive check",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": [],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Rogue",
        "level_adjustment": 0,
        "kin_sense_category": "null",
    },

    # -------------------------------------------------------------------
    # HALF-DOMNATHAR
    # -------------------------------------------------------------------
    "Half-Domnathar": {
        "name": "Half-Domnathar",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Cha": -2},
        "vision": "Darkvision 60 ft.",
        "languages_auto": ["Common", "Undercommon"],
        "languages_bonus": ["Abyssal", "Draconic", "Dwarven", "Elven", "Goblin", "Infernal"],
        "skill_bonuses": {"Hide": 2, "Move Silently": 2, "Intimidate": 2},
        "spell_like": [],
        "special": [
            "Shadow Drills: +2 racial bonus on Hide, Move Silently, and Intimidate checks",
            "Light Sensitivity: dazzled in areas of bright sunlight or within a daylight spell",
            "Immune to magical sleep effects",
            "+2 racial bonus on saves vs enchantment spells and effects",
            "Treat hand crossbow and spiked chain as martial weapons",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple", "short sword", "hand crossbow"],
        "armor_proficiencies": [],
        "immunities": ["magical sleep"],
        "favored_class": "Rogue or Fighter",
        "level_adjustment": 1,
        "kin_sense_category": "harmonic",
    },

    # -------------------------------------------------------------------
    # FARBORN HUMAN
    # -------------------------------------------------------------------
    "Farborn Human": {
        "name": "Farborn Human",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {},  # +2 to one ability score of the player's choice
        "vision": "Normal",
        "languages_auto": ["Common"],
        "languages_bonus": ["any"],
        "skill_bonuses": {},
        "spell_like": [],
        "special": [
            "+2 to one ability score of the player's choice (applied during character creation)",
            "Bonus feat at 1st level",
            "4 extra skill points at 1st level, 1 extra skill point at each additional level",
            "No Kin-sense: undetectable by Kin-sense abilities",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple", "lance", "longbow"],
        "armor_proficiencies": ["light", "medium"],
        "immunities": [],
        "favored_class": "Any",
        "level_adjustment": 0,
        "kin_sense_category": "none",
    },

    # -------------------------------------------------------------------
    # GOBLIN
    # -------------------------------------------------------------------
    "Goblin": {
        "name": "Goblin",
        "size": "Small",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Str": -2, "Cha": -2},
        "vision": "Darkvision 60 ft.",
        "languages_auto": ["Common", "Goblin"],
        "languages_bonus": ["Draconic", "Elven", "Giant", "Gnoll", "Orc"],
        "skill_bonuses": {"Move Silently": 4, "Ride": 4},
        "spell_like": [],
        "special": [
            "Light Sensitivity: dazzled in areas of bright sunlight or within a daylight spell",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": [],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Rogue",
        "level_adjustment": 0,
        "kin_sense_category": "wild_static",
    },

    # -------------------------------------------------------------------
    # HOBGOBLIN
    # -------------------------------------------------------------------
    "Hobgoblin": {
        "name": "Hobgoblin",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Con": 2},
        "vision": "Darkvision 60 ft.",
        "languages_auto": ["Common", "Goblin"],
        "languages_bonus": ["Draconic", "Dwarven", "Giant", "Infernal", "Orc"],
        "skill_bonuses": {"Move Silently": 4},
        "spell_like": [],
        "special": [
            "Battle Hardened: +2 racial bonus on saves vs fear",
            "Command: adjacent hobgoblin allies gain +1 morale bonus on attack rolls and saves vs fear",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": [],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Fighter",
        "level_adjustment": 0,
        "kin_sense_category": "wild_static",
    },

    # -------------------------------------------------------------------
    # WARG
    # -------------------------------------------------------------------
    "Warg": {
        "name": "Warg",
        "size": "Medium",
        "speed": 50,
        "ability_mods": {"Str": 2, "Wis": 2, "Cha": -2},
        "vision": "Low-Light Vision",
        "languages_auto": ["Common", "Warg"],
        "languages_bonus": ["Goblin", "Gnoll", "Orc", "Sylvan"],
        "skill_bonuses": {},
        "spell_like": [],
        "special": [
            "Scent: can detect creatures by smell within 30 ft. (60 ft. upwind, 15 ft. downwind)",
            "Bite attack: 1d6 + Str modifier (natural weapon)",
            "Quadruped: +4 racial bonus on ability checks to resist bull rush and trip; x1.5 carrying capacity; cannot wield weapons or use items requiring hands",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": [],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Ranger or Druid",
        "level_adjustment": 0,
        "kin_sense_category": "wild_static",
    },

    # -------------------------------------------------------------------
    # TANUKI
    # -------------------------------------------------------------------
    "Tanuki": {
        "name": "Tanuki",
        "size": "Small",
        "speed": 20,
        "ability_mods": {"Cha": 2, "Dex": 2, "Str": -2},
        "vision": "Low-Light Vision",
        "languages_auto": ["Common", "Sylvan"],
        "languages_bonus": ["Dwarven", "Elven", "Gnome", "Goblin", "Halfling"],
        "skill_bonuses": {"Perform": 2, "Bluff": 2},
        "spell_like": [
            "Disguise self 1/day",
        ],
        "special": [
            "Spirit Brew: 1/day brew a small cup of sake; drinker must succeed on DC 12 Will save or answer one question truthfully",
            "Kin-adjacent: registers as warm/familiar to Kin-sense but is not truly harmonic",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": [],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Bard or Druid",
        "level_adjustment": 0,
        "kin_sense_category": "wild_static",
    },

    # -------------------------------------------------------------------
    # NPC / ENCOUNTER RACES (Non-Kin)
    # -------------------------------------------------------------------
    "Warg": {
        "name": "Warg",
        "size": "Large",
        "speed": 50,
        "ability_mods": {"Str": 4, "Dex": 2, "Con": 2, "Int": -2, "Cha": -2},
        "vision": "Low-Light, Scent",
        "languages_auto": ["Warg", "Common"],
        "languages_bonus": ["Goblin"],
        "skill_bonuses": {"Survival": 4, "Listen": 2, "Hide": 2},
        "spell_like": [],
        "special": [
            "Trip: free trip attempt on successful bite attack",
            "Scent: detect creatures within 30 feet by smell",
            "Pack Tactics: +2 attack when adjacent to ally warg",
            "Sapient: fully intelligent, not animals — freed servitors of the Deceivers",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": ["bite"],
        "armor_proficiencies": ["barding"],
        "immunities": [],
        "favored_class": "Ranger",
        "level_adjustment": 2,
        "kin_sense_category": "breach_static",
    },

    "Goblin": {
        "name": "Goblin",
        "size": "Small",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Str": -2, "Cha": -2},
        "vision": "Darkvision 60",
        "languages_auto": ["Goblin", "Common"],
        "languages_bonus": ["Warg", "Orc", "Draconic"],
        "skill_bonuses": {"Move Silently": 4, "Ride": 4, "Hide": 4},
        "spell_like": [],
        "special": [
            "Small size: +1 AC, +1 attack, +4 Hide, -4 grapple",
            "Freed Servitors: broke chains at Dark Dawn, diverse tribal societies",
            "Tunnel Dweller: no penalty for fighting in confined spaces",
            "Scavenger: +2 racial bonus on Craft (trapmaking) and Survival (foraging)",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple", "short sword", "shortbow"],
        "armor_proficiencies": ["light armor", "shields"],
        "immunities": [],
        "favored_class": "Rogue",
        "level_adjustment": 0,
        "kin_sense_category": "breach_static",
    },

    "Hobgoblin": {
        "name": "Hobgoblin",
        "size": "Medium",
        "speed": 30,
        "ability_mods": {"Dex": 2, "Con": 2},
        "vision": "Darkvision 60",
        "languages_auto": ["Goblin", "Common"],
        "languages_bonus": ["Draconic", "Infernal", "Giant"],
        "skill_bonuses": {"Move Silently": 4},
        "spell_like": [],
        "special": [
            "Disciplined: +2 racial bonus on saves vs fear and mind-affecting effects",
            "Deceiver Remnant: organized military hierarchy, Domnathar-aligned units still exist",
            "Tactical Coordination: +1 morale bonus to attack when in formation with 2+ hobgoblins",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": ["all martial", "all simple"],
        "armor_proficiencies": ["all armor", "shields"],
        "immunities": [],
        "favored_class": "Fighter",
        "level_adjustment": 1,
        "kin_sense_category": "breach_static",
    },

    "Tanuki": {
        "name": "Tanuki",
        "size": "Small",
        "speed": 25,
        "ability_mods": {"Cha": 4, "Dex": 2, "Str": -2},
        "vision": "Low-Light",
        "languages_auto": ["Sylvan", "Common"],
        "languages_bonus": ["Elven", "Gnome", "Halfling"],
        "skill_bonuses": {"Bluff": 4, "Disguise": 4, "Perform": 2, "Craft(any)": 2},
        "spell_like": [
            "Disguise Self at will",
            "Ghost Sound at will",
            "Prestidigitation 3/day",
        ],
        "special": [
            "Shapechanger: can assume Small or Medium humanoid form at will (as alter self)",
            "Oreka-native raccoon-folk: trickster-artisans, theatrical performers",
            "Wild Static: registers on Kin-sense as alive but non-Kin — never associated with Deceivers",
            "Forest Spirit Affinity: can communicate with forest spirits and fey creatures",
            "Illusion Mastery: +2 DC to saving throws against Tanuki illusion spells",
        ],
        "elemental_affinity": None,
        "elemental_resistance": {},
        "weapon_proficiencies": ["all simple"],
        "armor_proficiencies": [],
        "immunities": [],
        "favored_class": "Bard",
        "level_adjustment": 1,
        "kin_sense_category": "wild_static",
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_race(name: str) -> dict | None:
    """Look up a race by name (case-insensitive, partial-match friendly).

    Returns the race dict if found, or ``None`` if no match.

    Matching priority:
      1. Exact key match (case-insensitive).
      2. First key that *contains* the search string (case-insensitive).
    """
    lower = name.lower()

    # Exact match first
    for key, data in RACES.items():
        if key.lower() == lower:
            return data

    # Partial / substring match
    for key, data in RACES.items():
        if lower in key.lower():
            return data

    return None
