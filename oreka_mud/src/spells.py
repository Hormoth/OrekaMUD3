"""
D&D 3.5 Edition Spell System for OrekaMUD3

This module implements a comprehensive spell system including:
- All spell schools and subschools
- Spells for levels 0-9
- Spell effects (damage, healing, buffs, conditions)
- Saving throws and spell resistance
- Component requirements (V, S, M, F, XP)
- Metamagic support
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random


# =============================================================================
# Spell Schools and Subschools
# =============================================================================

class SpellSchool(Enum):
    """D&D 3.5 spell schools"""
    ABJURATION = "Abjuration"
    CONJURATION = "Conjuration"
    DIVINATION = "Divination"
    ENCHANTMENT = "Enchantment"
    EVOCATION = "Evocation"
    ILLUSION = "Illusion"
    NECROMANCY = "Necromancy"
    TRANSMUTATION = "Transmutation"
    UNIVERSAL = "Universal"


class ConjurationSubschool(Enum):
    CALLING = "Calling"
    CREATION = "Creation"
    HEALING = "Healing"
    SUMMONING = "Summoning"
    TELEPORTATION = "Teleportation"


class EnchantmentSubschool(Enum):
    CHARM = "Charm"
    COMPULSION = "Compulsion"


class IllusionSubschool(Enum):
    FIGMENT = "Figment"
    GLAMER = "Glamer"
    PATTERN = "Pattern"
    PHANTASM = "Phantasm"
    SHADOW = "Shadow"


# =============================================================================
# Spell Descriptors
# =============================================================================

class SpellDescriptor(Enum):
    """Spell descriptors that affect how spells interact with the world"""
    ACID = "Acid"
    AIR = "Air"
    CHAOTIC = "Chaotic"
    COLD = "Cold"
    DARKNESS = "Darkness"
    DEATH = "Death"
    EARTH = "Earth"
    ELECTRICITY = "Electricity"
    EVIL = "Evil"
    FEAR = "Fear"
    FIRE = "Fire"
    FORCE = "Force"
    GOOD = "Good"
    LANGUAGE_DEPENDENT = "Language-Dependent"
    LAWFUL = "Lawful"
    LIGHT = "Light"
    MIND_AFFECTING = "Mind-Affecting"
    SONIC = "Sonic"
    WATER = "Water"


# =============================================================================
# Spell Effect Types
# =============================================================================

class SpellEffectType(Enum):
    """Types of spell effects"""
    DAMAGE = "damage"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"
    CONDITION = "condition"
    SUMMON = "summon"
    UTILITY = "utility"
    MOVEMENT = "movement"
    DETECTION = "detection"
    CREATION = "creation"
    DISPEL = "dispel"
    PROTECTION = "protection"


class SaveType(Enum):
    """Saving throw types"""
    NONE = "None"
    FORTITUDE = "Fortitude"
    REFLEX = "Reflex"
    WILL = "Will"


class SaveEffect(Enum):
    """What happens on a successful save"""
    NONE = "none"
    NEGATES = "negates"
    HALF = "half"
    PARTIAL = "partial"
    DISBELIEF = "disbelief"
    HARMLESS = "harmless"


class TargetType(Enum):
    """Spell targeting types"""
    SELF = "self"
    TOUCH = "touch"
    RANGED_TOUCH = "ranged_touch"
    SINGLE = "single"
    MULTIPLE = "multiple"
    AREA_BURST = "area_burst"
    AREA_CONE = "area_cone"
    AREA_LINE = "area_line"
    AREA_SPREAD = "area_spread"
    AREA_EMANATION = "area_emanation"


# =============================================================================
# Spell Data Structure
# =============================================================================

@dataclass
class Spell:
    """Represents a D&D 3.5 spell"""
    name: str
    school: SpellSchool
    level: Dict[str, int]  # {class_name: spell_level}
    description: str

    # Components
    verbal: bool = True
    somatic: bool = True
    material: Optional[str] = None  # Material component description
    focus: Optional[str] = None  # Focus component description
    xp_cost: int = 0  # XP cost if any

    # Casting
    casting_time: str = "1 standard action"
    range_type: str = "Close"  # Close, Medium, Long, Personal, Touch, Unlimited
    range_feet: Optional[int] = None  # Override for specific range

    # Target/Area
    target_type: TargetType = TargetType.SINGLE
    area_size: Optional[int] = None  # Radius in feet for area spells

    # Duration
    duration: str = "Instantaneous"
    duration_rounds: int = 0  # 0 for instantaneous/permanent
    concentration: bool = False
    dismissible: bool = False

    # Saving throw
    save_type: SaveType = SaveType.NONE
    save_effect: SaveEffect = SaveEffect.NONE

    # Spell resistance
    spell_resistance: bool = True

    # Effects
    effect_type: SpellEffectType = SpellEffectType.UTILITY
    damage_dice: Optional[str] = None  # e.g., "1d4+1", "1d6/level max 10d6"
    damage_type: Optional[str] = None  # e.g., "fire", "force", "negative"
    healing_dice: Optional[str] = None  # e.g., "1d8+1/level max +5"
    condition_applied: Optional[str] = None  # Condition to apply
    condition_duration: int = 0  # Rounds the condition lasts
    buff_effects: Dict[str, Any] = field(default_factory=dict)

    # Subschool and descriptors
    subschool: Optional[str] = None
    descriptors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "school": self.school.value,
            "level": self.level,
            "description": self.description,
            "verbal": self.verbal,
            "somatic": self.somatic,
            "material": self.material,
            "focus": self.focus,
            "xp_cost": self.xp_cost,
            "casting_time": self.casting_time,
            "range_type": self.range_type,
            "target_type": self.target_type.value,
            "duration": self.duration,
            "save_type": self.save_type.value,
            "save_effect": self.save_effect.value,
            "spell_resistance": self.spell_resistance,
            "effect_type": self.effect_type.value,
            "damage_dice": self.damage_dice,
            "healing_dice": self.healing_dice,
            "condition_applied": self.condition_applied,
            "descriptors": self.descriptors,
        }

    def get_components(self) -> List[str]:
        """Get list of component abbreviations"""
        components = []
        if self.verbal:
            components.append("V")
        if self.somatic:
            components.append("S")
        if self.material:
            components.append("M")
        if self.focus:
            components.append("F")
        if self.xp_cost > 0:
            components.append("XP")
        return components


# =============================================================================
# D&D 3.5 Spell Database
# =============================================================================

SPELLS: Dict[str, Spell] = {}

def register_spell(spell: Spell):
    """Register a spell in the database"""
    SPELLS[spell.name.lower()] = spell


# =============================================================================
# Level 0 Cantrips/Orisons
# =============================================================================

register_spell(Spell(
    name="Acid Splash",
    school=SpellSchool.CONJURATION,
    subschool="Creation",
    level={"Wizard": 0, "Sorcerer": 0},
    description="You fire a small orb of acid at the target, dealing 1d3 acid damage.",
    target_type=TargetType.RANGED_TOUCH,
    range_type="Close",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d3",
    damage_type="acid",
    save_type=SaveType.NONE,
    descriptors=["Acid"],
))

register_spell(Spell(
    name="Daze",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 0, "Sorcerer": 0, "Bard": 0},
    description="A humanoid creature of 4 HD or less loses its next action.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="dazed",
    condition_duration=1,
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Detect Magic",
    school=SpellSchool.DIVINATION,
    level={"Wizard": 0, "Sorcerer": 0, "Bard": 0, "Cleric": 0, "Druid": 0},
    description="You detect magical auras. The amount of information revealed depends on how long you study.",
    target_type=TargetType.AREA_CONE,
    area_size=60,
    range_type="Personal",
    duration="Concentration, up to 1 min./level",
    concentration=True,
    effect_type=SpellEffectType.DETECTION,
    save_type=SaveType.NONE,
    spell_resistance=False,
))

register_spell(Spell(
    name="Guidance",
    school=SpellSchool.DIVINATION,
    level={"Cleric": 0, "Druid": 0},
    description="The subject gets a +1 competence bonus on a single attack roll, saving throw, or skill check.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 minute or until discharged",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"competence_bonus": 1},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Light",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 0, "Sorcerer": 0, "Bard": 0, "Cleric": 0, "Druid": 0},
    description="Object shines like a torch, providing bright light in a 20-foot radius.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="10 min./level",
    duration_rounds=100,
    effect_type=SpellEffectType.UTILITY,
    save_type=SaveType.NONE,
    descriptors=["Light"],
))

register_spell(Spell(
    name="Mage Hand",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 0, "Sorcerer": 0, "Bard": 0},
    description="You point your finger at an object and can lift it and move it at will from a distance.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    duration="Concentration",
    concentration=True,
    effect_type=SpellEffectType.UTILITY,
    save_type=SaveType.NONE,
    spell_resistance=False,
))

register_spell(Spell(
    name="Prestidigitation",
    school=SpellSchool.UNIVERSAL,
    level={"Wizard": 0, "Sorcerer": 0, "Bard": 0},
    description="Prestidigitations are minor tricks that novice spellcasters use for practice.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    duration="1 hour",
    effect_type=SpellEffectType.UTILITY,
    save_type=SaveType.NONE,
    spell_resistance=False,
))

register_spell(Spell(
    name="Ray of Frost",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 0, "Sorcerer": 0},
    description="A ray of freezing air and ice projects from your pointing finger, dealing 1d3 cold damage.",
    target_type=TargetType.RANGED_TOUCH,
    range_type="Close",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d3",
    damage_type="cold",
    save_type=SaveType.NONE,
    descriptors=["Cold"],
))

register_spell(Spell(
    name="Resistance",
    school=SpellSchool.ABJURATION,
    level={"Wizard": 0, "Sorcerer": 0, "Bard": 0, "Cleric": 0, "Druid": 0, "Paladin": 1},
    description="Subject gains +1 on saving throws.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 minute",
    duration_rounds=10,
    effect_type=SpellEffectType.BUFF,
    buff_effects={"save_bonus": 1},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Virtue",
    school=SpellSchool.TRANSMUTATION,
    level={"Cleric": 0, "Druid": 0, "Paladin": 1},
    description="Subject gains 1 temporary hit point.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min.",
    duration_rounds=10,
    effect_type=SpellEffectType.BUFF,
    buff_effects={"temp_hp": 1},
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.HARMLESS,
))

# =============================================================================
# Level 1 Spells
# =============================================================================

register_spell(Spell(
    name="Magic Missile",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 1, "Sorcerer": 1},
    description="A missile of magical energy darts forth and strikes its target, dealing 1d4+1 force damage. "
                "You gain additional missiles at higher levels (one at 3rd, 5th, 7th, and 9th).",
    target_type=TargetType.SINGLE,
    range_type="Medium",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d4+1",
    damage_type="force",
    save_type=SaveType.NONE,
    spell_resistance=True,
    descriptors=["Force"],
))

register_spell(Spell(
    name="Burning Hands",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 1, "Sorcerer": 1},
    description="A cone of searing flame shoots from your fingertips, dealing 1d4 fire damage per caster level (max 5d4).",
    target_type=TargetType.AREA_CONE,
    area_size=15,
    range_type="Personal",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d4/level max 5d4",
    damage_type="fire",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    descriptors=["Fire"],
))

register_spell(Spell(
    name="Charm Person",
    school=SpellSchool.ENCHANTMENT,
    subschool="Charm",
    level={"Wizard": 1, "Sorcerer": 1, "Bard": 1},
    description="This charm makes a humanoid creature regard you as its trusted friend and ally.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    duration="1 hour/level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="charmed",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Color Spray",
    school=SpellSchool.ILLUSION,
    subschool="Pattern",
    level={"Wizard": 1, "Sorcerer": 1},
    description="A vivid cone of clashing colors springs forth, causing creatures to become stunned, blinded, or unconscious.",
    target_type=TargetType.AREA_CONE,
    area_size=15,
    range_type="Personal",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="stunned",
    condition_duration=1,
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Cure Light Wounds",
    school=SpellSchool.CONJURATION,
    subschool="Healing",
    level={"Cleric": 1, "Bard": 1, "Druid": 1, "Paladin": 1, "Ranger": 2},
    description="When laying your hand upon a living creature, you channel positive energy that cures 1d8+1/level (max +5) hit points.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.HEALING,
    healing_dice="1d8+1/level max +5",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HALF,  # Only for undead
    spell_resistance=True,
))

register_spell(Spell(
    name="Inflict Light Wounds",
    school=SpellSchool.NECROMANCY,
    level={"Cleric": 1},
    description="When laying your hand upon a creature, you channel negative energy that deals 1d8+1/level (max +5) damage.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d8+1/level max +5",
    damage_type="negative",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HALF,
))

register_spell(Spell(
    name="Mage Armor",
    school=SpellSchool.CONJURATION,
    subschool="Creation",
    level={"Wizard": 1, "Sorcerer": 1},
    description="An invisible but tangible field of force surrounds the subject, providing a +4 armor bonus to AC.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 hour/level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"armor_bonus": 4},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
    descriptors=["Force"],
))

register_spell(Spell(
    name="Shield",
    school=SpellSchool.ABJURATION,
    level={"Wizard": 1, "Sorcerer": 1},
    description="Shield creates an invisible, tower-shield-sized mobile disk of force that provides a +4 shield bonus to AC.",
    target_type=TargetType.SELF,
    range_type="Personal",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"shield_bonus": 4, "immune_magic_missile": True},
    descriptors=["Force"],
))

register_spell(Spell(
    name="Sleep",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 1, "Sorcerer": 1, "Bard": 1},
    description="A sleep spell causes a magical slumber to come upon 4 HD of creatures.",
    target_type=TargetType.AREA_BURST,
    area_size=10,
    range_type="Medium",
    duration="1 min./level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="unconscious",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Shocking Grasp",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 1, "Sorcerer": 1},
    description="Your successful melee touch attack deals 1d6 electricity damage per caster level (max 5d6). +3 attack vs metal armor.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 5d6",
    damage_type="electricity",
    save_type=SaveType.NONE,
    descriptors=["Electricity"],
))

register_spell(Spell(
    name="Bless",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Cleric": 1, "Paladin": 1},
    description="Bless fills your allies with courage, granting +1 morale bonus on attack rolls and saves vs fear.",
    target_type=TargetType.AREA_BURST,
    area_size=50,
    range_type="Close",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"attack_bonus": 1, "save_vs_fear": 1},
    save_type=SaveType.NONE,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Cause Fear",
    school=SpellSchool.NECROMANCY,
    level={"Wizard": 1, "Sorcerer": 1, "Bard": 1, "Cleric": 1},
    description="The affected creature becomes frightened. If it has 6 or more HD, it becomes shaken instead.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    duration="1d4 rounds or 1 round",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="frightened",
    condition_duration=4,
    save_type=SaveType.WILL,
    save_effect=SaveEffect.PARTIAL,
    descriptors=["Fear", "Mind-Affecting"],
))

register_spell(Spell(
    name="Entangle",
    school=SpellSchool.TRANSMUTATION,
    level={"Druid": 1, "Ranger": 1},
    description="Grasses, weeds, and plants entangle creatures in the area, making them entangled.",
    target_type=TargetType.AREA_SPREAD,
    area_size=40,
    range_type="Long",
    duration="1 min./level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="entangled",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.PARTIAL,
))

register_spell(Spell(
    name="Grease",
    school=SpellSchool.CONJURATION,
    subschool="Creation",
    level={"Wizard": 1, "Sorcerer": 1, "Bard": 1},
    description="A grease spell covers a solid surface with a slippery layer of grease. Creatures must save or fall prone.",
    target_type=TargetType.AREA_SPREAD,
    area_size=10,
    range_type="Close",
    duration="1 round/level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="prone",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.NEGATES,
))

register_spell(Spell(
    name="Protection from Evil",
    school=SpellSchool.ABJURATION,
    level={"Cleric": 1, "Wizard": 1, "Sorcerer": 1, "Paladin": 1},
    description="+2 deflection bonus to AC and +2 resistance bonus on saves vs evil creatures. Blocks mental control.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.PROTECTION,
    buff_effects={"deflection_ac_vs_evil": 2, "save_vs_evil": 2},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
    descriptors=["Good"],
))

register_spell(Spell(
    name="True Strike",
    school=SpellSchool.DIVINATION,
    level={"Wizard": 1, "Sorcerer": 1},
    description="You gain a +20 insight bonus on your next single attack roll.",
    target_type=TargetType.SELF,
    range_type="Personal",
    duration="See text",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"next_attack_bonus": 20},
))

# =============================================================================
# Level 2 Spells
# =============================================================================

register_spell(Spell(
    name="Scorching Ray",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 2, "Sorcerer": 2},
    description="You blast your enemies with fiery rays. You may fire one ray, plus one additional ray for every "
                "four levels beyond 3rd (max three rays at 11th). Each ray deals 4d6 fire damage.",
    target_type=TargetType.RANGED_TOUCH,
    range_type="Close",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="4d6",
    damage_type="fire",
    save_type=SaveType.NONE,
    descriptors=["Fire"],
))

register_spell(Spell(
    name="Acid Arrow",
    school=SpellSchool.CONJURATION,
    subschool="Creation",
    level={"Wizard": 2, "Sorcerer": 2},
    description="A magical arrow of acid springs from your hand and speeds to its target. Deals 2d4 acid damage "
                "with no splash damage. For every three caster levels, the acid deals an additional 2d4 damage in the following round.",
    target_type=TargetType.RANGED_TOUCH,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="2d4",
    damage_type="acid",
    save_type=SaveType.NONE,
    descriptors=["Acid"],
))

register_spell(Spell(
    name="Bull's Strength",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 2, "Sorcerer": 2, "Cleric": 2, "Druid": 2, "Paladin": 2},
    description="The subject becomes stronger, gaining a +4 enhancement bonus to Strength.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"str_bonus": 4},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Cat's Grace",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 2, "Sorcerer": 2, "Bard": 2, "Druid": 2, "Ranger": 2},
    description="The subject becomes more agile, gaining a +4 enhancement bonus to Dexterity.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"dex_bonus": 4},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Bear's Endurance",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 2, "Sorcerer": 2, "Cleric": 2, "Druid": 2, "Ranger": 2},
    description="The subject becomes hardier, gaining a +4 enhancement bonus to Constitution.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"con_bonus": 4},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Cure Moderate Wounds",
    school=SpellSchool.CONJURATION,
    subschool="Healing",
    level={"Cleric": 2, "Bard": 2, "Druid": 3, "Paladin": 3, "Ranger": 3},
    description="Cures 2d8+1/level (max +10) hit points.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.HEALING,
    healing_dice="2d8+1/level max +10",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HALF,
))

register_spell(Spell(
    name="Hold Person",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 3, "Sorcerer": 3, "Bard": 2, "Cleric": 2},
    description="The subject becomes paralyzed and freezes in place. It is aware but cannot take any actions.",
    target_type=TargetType.SINGLE,
    range_type="Medium",
    duration="1 round/level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="paralyzed",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Invisibility",
    school=SpellSchool.ILLUSION,
    subschool="Glamer",
    level={"Wizard": 2, "Sorcerer": 2, "Bard": 2},
    description="The creature or object touched becomes invisible. If the recipient attacks, the spell ends.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"invisible": True},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Mirror Image",
    school=SpellSchool.ILLUSION,
    subschool="Figment",
    level={"Wizard": 2, "Sorcerer": 2, "Bard": 2},
    description="Several illusory duplicates of you pop into being, making it difficult for enemies to know which target to attack.",
    target_type=TargetType.SELF,
    range_type="Personal",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"mirror_images": "1d4+1"},
))

register_spell(Spell(
    name="Web",
    school=SpellSchool.CONJURATION,
    subschool="Creation",
    level={"Wizard": 2, "Sorcerer": 2},
    description="Web creates a many-layered mass of strong, sticky strands that trap those caught in it.",
    target_type=TargetType.AREA_SPREAD,
    area_size=20,
    range_type="Medium",
    duration="10 min./level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="entangled",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.NEGATES,
))

register_spell(Spell(
    name="Blur",
    school=SpellSchool.ILLUSION,
    subschool="Glamer",
    level={"Wizard": 2, "Sorcerer": 2, "Bard": 2},
    description="The subject's outline appears blurred, granting concealment (20% miss chance).",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"concealment": 20},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Darkness",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 2, "Sorcerer": 2, "Bard": 2, "Cleric": 2},
    description="This spell causes an object to radiate shadowy illumination out to a 20-foot radius.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="10 min./level",
    effect_type=SpellEffectType.UTILITY,
    descriptors=["Darkness"],
))

# =============================================================================
# Level 3 Spells
# =============================================================================

register_spell(Spell(
    name="Fireball",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 3, "Sorcerer": 3},
    description="A fireball detonates with a low roar, dealing 1d6 fire damage per caster level (max 10d6) "
                "in a 20-ft.-radius spread.",
    target_type=TargetType.AREA_SPREAD,
    area_size=20,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 10d6",
    damage_type="fire",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    material="A tiny ball of bat guano and sulfur",
    descriptors=["Fire"],
))

register_spell(Spell(
    name="Lightning Bolt",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 3, "Sorcerer": 3},
    description="You release a powerful stroke of electrical energy that deals 1d6 electricity damage per caster level (max 10d6).",
    target_type=TargetType.AREA_LINE,
    area_size=120,
    range_type="Personal",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 10d6",
    damage_type="electricity",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    descriptors=["Electricity"],
))

register_spell(Spell(
    name="Dispel Magic",
    school=SpellSchool.ABJURATION,
    level={"Wizard": 3, "Sorcerer": 3, "Bard": 3, "Cleric": 3, "Druid": 4, "Paladin": 3},
    description="You can use dispel magic to end ongoing spells that have been cast on a creature or object.",
    target_type=TargetType.SINGLE,
    range_type="Medium",
    effect_type=SpellEffectType.DISPEL,
    save_type=SaveType.NONE,
))

register_spell(Spell(
    name="Fly",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 3, "Sorcerer": 3},
    description="The subject can fly at a speed of 60 feet (or 40 feet if wearing medium or heavy armor).",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"fly_speed": 60},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Haste",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 3, "Sorcerer": 3, "Bard": 3},
    description="One creature per level moves and acts more quickly. +1 attack, +1 AC, +1 Reflex, +30 ft. speed, extra attack.",
    target_type=TargetType.MULTIPLE,
    range_type="Close",
    duration="1 round/level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"attack_bonus": 1, "ac_bonus": 1, "reflex_bonus": 1, "speed_bonus": 30, "extra_attack": True},
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Slow",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 3, "Sorcerer": 3, "Bard": 3},
    description="Affected creatures can only take a single move or standard action each turn. -1 AC, -1 attack, -1 Reflex.",
    target_type=TargetType.MULTIPLE,
    range_type="Close",
    duration="1 round/level",
    effect_type=SpellEffectType.DEBUFF,
    buff_effects={"attack_penalty": 1, "ac_penalty": 1, "reflex_penalty": 1},
    condition_applied="staggered",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
))

register_spell(Spell(
    name="Cure Serious Wounds",
    school=SpellSchool.CONJURATION,
    subschool="Healing",
    level={"Cleric": 3, "Bard": 3, "Druid": 4, "Paladin": 4, "Ranger": 4},
    description="Cures 3d8+1/level (max +15) hit points.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.HEALING,
    healing_dice="3d8+1/level max +15",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HALF,
))

register_spell(Spell(
    name="Stinking Cloud",
    school=SpellSchool.CONJURATION,
    subschool="Creation",
    level={"Wizard": 3, "Sorcerer": 3},
    description="Stinking Cloud creates a bank of fog like that created by fog cloud, except that the vapors are nauseating.",
    target_type=TargetType.AREA_SPREAD,
    area_size=20,
    range_type="Medium",
    duration="1 round/level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="nauseated",
    condition_duration=1,
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.NEGATES,
))

register_spell(Spell(
    name="Vampiric Touch",
    school=SpellSchool.NECROMANCY,
    level={"Wizard": 3, "Sorcerer": 3},
    description="Your touch deals 1d6 damage per two caster levels (max 10d6). You gain temporary HP equal to the damage dealt.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/2 levels max 10d6",
    damage_type="negative",
    save_type=SaveType.NONE,
))

register_spell(Spell(
    name="Protection from Energy",
    school=SpellSchool.ABJURATION,
    level={"Wizard": 3, "Sorcerer": 3, "Cleric": 3, "Druid": 3, "Ranger": 2},
    description="Grants temporary immunity to specified energy type until spell absorbs 12 points per caster level (max 120).",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="10 min./level or until discharged",
    effect_type=SpellEffectType.PROTECTION,
    buff_effects={"energy_absorption": 120},
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.HARMLESS,
))

# =============================================================================
# Level 4 Spells
# =============================================================================

register_spell(Spell(
    name="Ice Storm",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 4, "Sorcerer": 4, "Druid": 4},
    description="Great hailstones pound creatures dealing 3d6 bludgeoning damage and 2d6 cold damage.",
    target_type=TargetType.AREA_BURST,
    area_size=20,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="5d6",
    damage_type="cold",
    save_type=SaveType.NONE,
    descriptors=["Cold"],
))

register_spell(Spell(
    name="Stoneskin",
    school=SpellSchool.ABJURATION,
    level={"Wizard": 4, "Sorcerer": 4, "Druid": 5},
    description="Grants DR 10/adamantine, absorbing up to 10 damage per caster level (max 150).",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="10 min./level or until discharged",
    effect_type=SpellEffectType.PROTECTION,
    buff_effects={"dr": "10/adamantine", "dr_max": 150},
    material="Granite and diamond dust worth 250 gp",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Dimension Door",
    school=SpellSchool.CONJURATION,
    subschool="Teleportation",
    level={"Wizard": 4, "Sorcerer": 4, "Bard": 4},
    description="You instantly transfer yourself from your current location to any other spot within range.",
    target_type=TargetType.SELF,
    range_type="Long",
    effect_type=SpellEffectType.MOVEMENT,
    save_type=SaveType.NONE,
    spell_resistance=False,
))

register_spell(Spell(
    name="Cure Critical Wounds",
    school=SpellSchool.CONJURATION,
    subschool="Healing",
    level={"Cleric": 4, "Bard": 4, "Druid": 5},
    description="Cures 4d8+1/level (max +20) hit points.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.HEALING,
    healing_dice="4d8+1/level max +20",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HALF,
))

register_spell(Spell(
    name="Greater Invisibility",
    school=SpellSchool.ILLUSION,
    subschool="Glamer",
    level={"Wizard": 4, "Sorcerer": 4, "Bard": 4},
    description="This spell functions like invisibility, except that it doesn't end if the subject attacks.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 round/level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"invisible": True, "greater": True},
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Confusion",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 4, "Sorcerer": 4, "Bard": 3},
    description="Creatures affected by this spell behave randomly for the duration.",
    target_type=TargetType.AREA_BURST,
    area_size=15,
    range_type="Medium",
    duration="1 round/level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="confused",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Fear",
    school=SpellSchool.NECROMANCY,
    level={"Wizard": 4, "Sorcerer": 4, "Bard": 3},
    description="An invisible cone of terror causes each living creature to become panicked.",
    target_type=TargetType.AREA_CONE,
    area_size=30,
    range_type="Personal",
    duration="1 round/level or 1 round",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="panicked",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.PARTIAL,
    descriptors=["Fear", "Mind-Affecting"],
))

register_spell(Spell(
    name="Enervation",
    school=SpellSchool.NECROMANCY,
    level={"Wizard": 4, "Sorcerer": 4},
    description="You point your finger and utter the incantation, releasing a ray of negative energy. "
                "Subject gains 1d4 negative levels.",
    target_type=TargetType.RANGED_TOUCH,
    range_type="Close",
    effect_type=SpellEffectType.DEBUFF,
    buff_effects={"negative_levels": "1d4"},
    save_type=SaveType.NONE,
))

# =============================================================================
# Level 5 Spells
# =============================================================================

register_spell(Spell(
    name="Cone of Cold",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 5, "Sorcerer": 5},
    description="Cone of cold creates an area of extreme cold, dealing 1d6 cold damage per caster level (max 15d6).",
    target_type=TargetType.AREA_CONE,
    area_size=60,
    range_type="Personal",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 15d6",
    damage_type="cold",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    descriptors=["Cold"],
))

register_spell(Spell(
    name="Cloudkill",
    school=SpellSchool.CONJURATION,
    subschool="Creation",
    level={"Wizard": 5, "Sorcerer": 5},
    description="This spell generates a bank of yellowish-green fog. Living creatures of 3 HD or less are killed; "
                "4-6 HD creatures must save or die.",
    target_type=TargetType.AREA_SPREAD,
    area_size=20,
    range_type="Medium",
    duration="1 min./level",
    effect_type=SpellEffectType.DAMAGE,
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.PARTIAL,
))

register_spell(Spell(
    name="Hold Monster",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 5, "Sorcerer": 5, "Bard": 4},
    description="This spell functions like hold person, except it affects any living creature.",
    target_type=TargetType.SINGLE,
    range_type="Medium",
    duration="1 round/level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="paralyzed",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Teleport",
    school=SpellSchool.CONJURATION,
    subschool="Teleportation",
    level={"Wizard": 5, "Sorcerer": 5},
    description="This spell instantly transports you to a designated destination up to 100 miles per caster level.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.MOVEMENT,
    save_type=SaveType.NONE,
    spell_resistance=False,
))

register_spell(Spell(
    name="Wall of Force",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 5, "Sorcerer": 5},
    description="An invisible wall of force springs into existence. It is immune to damage of all kinds.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    duration="1 round/level",
    effect_type=SpellEffectType.CREATION,
    save_type=SaveType.NONE,
    descriptors=["Force"],
))

register_spell(Spell(
    name="Heal",
    school=SpellSchool.CONJURATION,
    subschool="Healing",
    level={"Cleric": 6, "Druid": 7},
    description="Heal enables you to channel positive energy into a creature to wipe away injury and afflictions. "
                "It cures 10 hit points per caster level (max 150).",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    effect_type=SpellEffectType.HEALING,
    healing_dice="10/level max 150",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HALF,
))

register_spell(Spell(
    name="Dominate Person",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 5, "Sorcerer": 5, "Bard": 4},
    description="You can control the actions of any humanoid creature. You and the subject have a telepathic link.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    duration="1 day/level",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="dominated",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Mind-Affecting"],
))

# =============================================================================
# Level 6 Spells
# =============================================================================

register_spell(Spell(
    name="Chain Lightning",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 6, "Sorcerer": 6},
    description="This spell creates an electrical discharge that begins as a single stroke and arcs to other targets. "
                "Primary target takes 1d6/level (max 20d6), secondary targets take half.",
    target_type=TargetType.SINGLE,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 20d6",
    damage_type="electricity",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    descriptors=["Electricity"],
))

register_spell(Spell(
    name="Disintegrate",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 6, "Sorcerer": 6},
    description="A thin, green ray springs from your pointing finger. You must make a ranged touch attack. "
                "On a hit, the target takes 2d6 damage per caster level (max 40d6).",
    target_type=TargetType.RANGED_TOUCH,
    range_type="Medium",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="2d6/level max 40d6",
    damage_type="force",
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.PARTIAL,
    descriptors=["Force"],
))

register_spell(Spell(
    name="True Seeing",
    school=SpellSchool.DIVINATION,
    level={"Wizard": 6, "Sorcerer": 6, "Cleric": 5, "Druid": 7},
    description="You confer on the subject the ability to see all things as they actually are.",
    target_type=TargetType.TOUCH,
    range_type="Touch",
    duration="1 min./level",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"true_seeing": True},
    material="Ointment worth 250 gp",
    save_type=SaveType.WILL,
    save_effect=SaveEffect.HARMLESS,
))

register_spell(Spell(
    name="Greater Dispel Magic",
    school=SpellSchool.ABJURATION,
    level={"Wizard": 6, "Sorcerer": 6, "Bard": 5, "Cleric": 6, "Druid": 6},
    description="This spell functions like dispel magic, except that the maximum caster level bonus is +20 instead of +10.",
    target_type=TargetType.SINGLE,
    range_type="Medium",
    effect_type=SpellEffectType.DISPEL,
    save_type=SaveType.NONE,
))

register_spell(Spell(
    name="Flesh to Stone",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 6, "Sorcerer": 6},
    description="The subject, along with all its carried gear, turns into a mindless, inert statue.",
    target_type=TargetType.SINGLE,
    range_type="Medium",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="petrified",
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.NEGATES,
))

# =============================================================================
# Level 7 Spells
# =============================================================================

register_spell(Spell(
    name="Delayed Blast Fireball",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 7, "Sorcerer": 7},
    description="This spell functions like fireball, except that it is more powerful and can detonate up to 5 rounds later. "
                "Deals 1d6 fire damage per caster level (max 20d6).",
    target_type=TargetType.AREA_SPREAD,
    area_size=20,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 20d6",
    damage_type="fire",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    descriptors=["Fire"],
))

register_spell(Spell(
    name="Finger of Death",
    school=SpellSchool.NECROMANCY,
    level={"Wizard": 7, "Sorcerer": 7, "Druid": 8},
    description="You can slay any one living creature within range. The target must make a Fortitude save or die.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="3d6+1/level",
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.PARTIAL,
    descriptors=["Death"],
))

register_spell(Spell(
    name="Power Word Blind",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 7, "Sorcerer": 7},
    description="You utter a single word of power that causes one creature with 200 HP or less to become blinded.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="blinded",
    save_type=SaveType.NONE,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Spell Turning",
    school=SpellSchool.ABJURATION,
    level={"Wizard": 7, "Sorcerer": 7},
    description="Spells and spell-like abilities targeted on you are turned back upon the original caster.",
    target_type=TargetType.SELF,
    range_type="Personal",
    duration="Until expended or 10 min./level",
    effect_type=SpellEffectType.PROTECTION,
    buff_effects={"spell_turning": True},
))

# =============================================================================
# Level 8 Spells
# =============================================================================

register_spell(Spell(
    name="Polar Ray",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 8, "Sorcerer": 8},
    description="A blue-white ray of freezing air and ice springs from your hand. Deals 1d6 cold damage per caster level (max 25d6).",
    target_type=TargetType.RANGED_TOUCH,
    range_type="Close",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 25d6",
    damage_type="cold",
    save_type=SaveType.NONE,
    descriptors=["Cold"],
))

register_spell(Spell(
    name="Power Word Stun",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 8, "Sorcerer": 8},
    description="You utter a single word of power that instantly causes one creature with 150 HP or less to become stunned.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    effect_type=SpellEffectType.CONDITION,
    condition_applied="stunned",
    condition_duration=4,
    save_type=SaveType.NONE,
    descriptors=["Mind-Affecting"],
))

register_spell(Spell(
    name="Sunburst",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 8, "Sorcerer": 8, "Druid": 8},
    description="Sunburst causes a globe of searing radiance to explode, dealing 6d6 damage to all creatures in the area.",
    target_type=TargetType.AREA_BURST,
    area_size=80,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="6d6",
    damage_type="light",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    descriptors=["Light"],
))

register_spell(Spell(
    name="Horrid Wilting",
    school=SpellSchool.NECROMANCY,
    level={"Wizard": 8, "Sorcerer": 8},
    description="This spell evaporates moisture from the bodies of living creatures, dealing 1d6 damage per caster level (max 20d6).",
    target_type=TargetType.MULTIPLE,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="1d6/level max 20d6",
    damage_type="negative",
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.HALF,
))

# =============================================================================
# Level 9 Spells
# =============================================================================

register_spell(Spell(
    name="Meteor Swarm",
    school=SpellSchool.EVOCATION,
    level={"Wizard": 9, "Sorcerer": 9},
    description="Meteor swarm is a very powerful and spectacular spell. Four 2-foot-diameter spheres spring from your hand. "
                "Each deals 2d6 bludgeoning damage plus 6d6 fire damage.",
    target_type=TargetType.AREA_BURST,
    area_size=40,
    range_type="Long",
    effect_type=SpellEffectType.DAMAGE,
    damage_dice="24d6",
    damage_type="fire",
    save_type=SaveType.REFLEX,
    save_effect=SaveEffect.HALF,
    descriptors=["Fire"],
))

register_spell(Spell(
    name="Power Word Kill",
    school=SpellSchool.ENCHANTMENT,
    subschool="Compulsion",
    level={"Wizard": 9, "Sorcerer": 9},
    description="You utter a single word of power that instantly kills one creature with 100 HP or less.",
    target_type=TargetType.SINGLE,
    range_type="Close",
    effect_type=SpellEffectType.DAMAGE,
    save_type=SaveType.NONE,
    descriptors=["Death", "Mind-Affecting"],
))

register_spell(Spell(
    name="Wish",
    school=SpellSchool.UNIVERSAL,
    level={"Wizard": 9, "Sorcerer": 9},
    description="Wish is the mightiest spell a wizard or sorcerer can cast. It can alter reality to your will.",
    target_type=TargetType.SINGLE,
    range_type="Unlimited",
    effect_type=SpellEffectType.UTILITY,
    xp_cost=5000,
    save_type=SaveType.NONE,
))

register_spell(Spell(
    name="Time Stop",
    school=SpellSchool.TRANSMUTATION,
    level={"Wizard": 9, "Sorcerer": 9},
    description="You seem to move with unimaginable speed. You gain 1d4+1 rounds of apparent time to act.",
    target_type=TargetType.SELF,
    range_type="Personal",
    duration="1d4+1 rounds (apparent time)",
    effect_type=SpellEffectType.BUFF,
    buff_effects={"time_stop": True},
))

register_spell(Spell(
    name="Wail of the Banshee",
    school=SpellSchool.NECROMANCY,
    level={"Wizard": 9, "Sorcerer": 9},
    description="You emit a terrible scream that kills creatures that hear it (except yourself). One creature per caster level dies.",
    target_type=TargetType.AREA_SPREAD,
    area_size=40,
    range_type="Close",
    effect_type=SpellEffectType.DAMAGE,
    save_type=SaveType.FORTITUDE,
    save_effect=SaveEffect.NEGATES,
    descriptors=["Death", "Sonic"],
))

register_spell(Spell(
    name="Gate",
    school=SpellSchool.CONJURATION,
    subschool="Calling",
    level={"Wizard": 9, "Sorcerer": 9, "Cleric": 9},
    description="You connect your plane with a random point on another plane and summon a powerful extraplanar creature.",
    target_type=TargetType.SINGLE,
    range_type="Medium",
    effect_type=SpellEffectType.SUMMON,
    xp_cost=1000,
    save_type=SaveType.NONE,
))


# =============================================================================
# D&D 3.5 Domain Data
# =============================================================================

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
            9: "Elemental Swarm"
        }
    },
    "Animal": {
        "power": "Knowledge (nature) as class skill, speak with animals 1/day.",
        "spells": {
            1: "Calm Animals",
            2: "Hold Animal",
            3: "Dominate Animal",
            4: "Summon Nature's Ally IV",
            5: "Commune with Nature",
            6: "Antilife Shell",
            7: "Animal Shapes",
            8: "Summon Nature's Ally VIII",
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
            9: "Summon Monster IX"
        }
    },
    "Death": {
        "power": "Rebuke/command undead, Death Touch 1/day.",
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
    "Destruction": {
        "power": "Smite 1/day (+4 attack, +level damage).",
        "spells": {
            1: "Inflict Light Wounds",
            2: "Shatter",
            3: "Contagion",
            4: "Inflict Critical Wounds",
            5: "Inflict Light Wounds, Mass",
            6: "Harm",
            7: "Disintegrate",
            8: "Earthquake",
            9: "Implosion"
        }
    },
    "Earth": {
        "power": "Turn/rebuke air creatures, +1 caster level with [Earth] spells.",
        "spells": {
            1: "Magic Stone",
            2: "Soften Earth and Stone",
            3: "Stone Shape",
            4: "Spike Stones",
            5: "Wall of Stone",
            6: "Stoneskin",
            7: "Earthquake",
            8: "Iron Body",
            9: "Elemental Swarm"
        }
    },
    "Evil": {
        "power": "Cast evil spells at +1 caster level.",
        "spells": {
            1: "Protection from Good",
            2: "Desecrate",
            3: "Magic Circle against Good",
            4: "Unholy Blight",
            5: "Dispel Good",
            6: "Create Undead",
            7: "Blasphemy",
            8: "Unholy Aura",
            9: "Summon Monster IX"
        }
    },
    "Fire": {
        "power": "Turn/rebuke water creatures, +1 caster level with [Fire] spells.",
        "spells": {
            1: "Burning Hands",
            2: "Produce Flame",
            3: "Resist Energy",
            4: "Wall of Fire",
            5: "Fire Shield",
            6: "Fire Seeds",
            7: "Fire Storm",
            8: "Incendiary Cloud",
            9: "Elemental Swarm"
        }
    },
    "Good": {
        "power": "Cast good spells at +1 caster level.",
        "spells": {
            1: "Protection from Evil",
            2: "Aid",
            3: "Magic Circle against Evil",
            4: "Holy Smite",
            5: "Dispel Evil",
            6: "Blade Barrier",
            7: "Holy Word",
            8: "Holy Aura",
            9: "Summon Monster IX"
        }
    },
    "Healing": {
        "power": "Cast healing spells at +1 caster level.",
        "spells": {
            1: "Cure Light Wounds",
            2: "Cure Moderate Wounds",
            3: "Cure Serious Wounds",
            4: "Cure Critical Wounds",
            5: "Cure Light Wounds, Mass",
            6: "Heal",
            7: "Regenerate",
            8: "Cure Critical Wounds, Mass",
            9: "Heal, Mass"
        }
    },
    "Knowledge": {
        "power": "All Knowledge skills are class skills, cast divinations at +1 caster level.",
        "spells": {
            1: "Detect Secret Doors",
            2: "Detect Thoughts",
            3: "Clairaudience/Clairvoyance",
            4: "Divination",
            5: "True Seeing",
            6: "Find the Path",
            7: "Legend Lore",
            8: "Discern Location",
            9: "Foresight"
        }
    },
    "Law": {
        "power": "Cast law spells at +1 caster level.",
        "spells": {
            1: "Protection from Chaos",
            2: "Calm Emotions",
            3: "Magic Circle against Chaos",
            4: "Order's Wrath",
            5: "Dispel Chaos",
            6: "Hold Monster",
            7: "Dictum",
            8: "Shield of Law",
            9: "Summon Monster IX"
        }
    },
    "Luck": {
        "power": "Reroll one roll per day.",
        "spells": {
            1: "Entropic Shield",
            2: "Aid",
            3: "Protection from Energy",
            4: "Freedom of Movement",
            5: "Break Enchantment",
            6: "Mislead",
            7: "Spell Turning",
            8: "Moment of Prescience",
            9: "Miracle"
        }
    },
    "Magic": {
        "power": "Use spell completion and spell trigger items as a wizard of half your cleric level.",
        "spells": {
            1: "Magic Aura",
            2: "Identify",
            3: "Dispel Magic",
            4: "Imbue with Spell Ability",
            5: "Spell Resistance",
            6: "Antimagic Field",
            7: "Spell Turning",
            8: "Protection from Spells",
            9: "Mage's Disjunction"
        }
    },
    "Plant": {
        "power": "Rebuke/command plant creatures, Knowledge (nature) as class skill.",
        "spells": {
            1: "Entangle",
            2: "Barkskin",
            3: "Plant Growth",
            4: "Command Plants",
            5: "Wall of Thorns",
            6: "Repel Wood",
            7: "Animate Plants",
            8: "Control Plants",
            9: "Shambler"
        }
    },
    "Protection": {
        "power": "Generate protective ward granting +level resistance bonus on next save.",
        "spells": {
            1: "Sanctuary",
            2: "Shield Other",
            3: "Protection from Energy",
            4: "Spell Immunity",
            5: "Spell Resistance",
            6: "Antimagic Field",
            7: "Repulsion",
            8: "Mind Blank",
            9: "Prismatic Sphere"
        }
    },
    "Strength": {
        "power": "Feat of Strength: +level enhancement bonus to Str for 1 round, 1/day.",
        "spells": {
            1: "Enlarge Person",
            2: "Bull's Strength",
            3: "Magic Vestment",
            4: "Spell Immunity",
            5: "Righteous Might",
            6: "Stoneskin",
            7: "Grasping Hand",
            8: "Clenched Fist",
            9: "Crushing Hand"
        }
    },
    "Sun": {
        "power": "Greater turning 1/day.",
        "spells": {
            1: "Endure Elements",
            2: "Heat Metal",
            3: "Searing Light",
            4: "Fire Shield",
            5: "Flame Strike",
            6: "Fire Seeds",
            7: "Sunbeam",
            8: "Sunburst",
            9: "Prismatic Sphere"
        }
    },
    "Travel": {
        "power": "Survival as class skill, freedom of movement 1 round/level per day.",
        "spells": {
            1: "Longstrider",
            2: "Locate Object",
            3: "Fly",
            4: "Dimension Door",
            5: "Teleport",
            6: "Find the Path",
            7: "Greater Teleport",
            8: "Phase Door",
            9: "Astral Projection"
        }
    },
    "Trickery": {
        "power": "Bluff, Disguise, Hide as class skills.",
        "spells": {
            1: "Disguise Self",
            2: "Invisibility",
            3: "Nondetection",
            4: "Confusion",
            5: "False Vision",
            6: "Mislead",
            7: "Screen",
            8: "Polymorph Any Object",
            9: "Time Stop"
        }
    },
    "War": {
        "power": "Free Martial Weapon Proficiency and Weapon Focus with deity's favored weapon.",
        "spells": {
            1: "Magic Weapon",
            2: "Spiritual Weapon",
            3: "Magic Vestment",
            4: "Divine Power",
            5: "Flame Strike",
            6: "Blade Barrier",
            7: "Power Word Blind",
            8: "Power Word Stun",
            9: "Power Word Kill"
        }
    },
    "Water": {
        "power": "Turn/rebuke fire creatures, +1 caster level with [Water] spells.",
        "spells": {
            1: "Obscuring Mist",
            2: "Fog Cloud",
            3: "Water Breathing",
            4: "Control Water",
            5: "Ice Storm",
            6: "Cone of Cold",
            7: "Acid Fog",
            8: "Horrid Wilting",
            9: "Elemental Swarm"
        }
    },
}


# =============================================================================
# Spell Helper Functions
# =============================================================================

def get_spell(name: str) -> Optional[Spell]:
    """Get a spell by name (case-insensitive)."""
    return SPELLS.get(name.lower())


def get_spell_by_name(name: str) -> Optional[Dict]:
    """Get a spell by name, returning dict format for compatibility."""
    spell = get_spell(name)
    if spell:
        return {
            "name": spell.name,
            "level": spell.level,
            "school": f"{spell.school.value}" + (f" ({spell.subschool})" if spell.subschool else ""),
            "description": spell.description,
            "components": spell.get_components(),
            "casting_time": spell.casting_time,
            "range": spell.range_type,
            "target": spell.target_type.value,
            "duration": spell.duration,
            "saving_throw": f"{spell.save_type.value} {spell.save_effect.value}" if spell.save_type != SaveType.NONE else "None",
            "spell_resistance": "Yes" if spell.spell_resistance else "No",
        }
    return None


def get_spells_for_class(class_name: str, max_level: int = 9) -> List[Spell]:
    """Get all spells available to a class up to a given spell level."""
    result = []
    for spell in SPELLS.values():
        if class_name in spell.level and spell.level[class_name] <= max_level:
            result.append(spell)
    return sorted(result, key=lambda s: (s.level.get(class_name, 99), s.name))


def get_spells_by_level(class_name: str, spell_level: int) -> List[Spell]:
    """Get all spells available to a class at a specific spell level."""
    result = []
    for spell in SPELLS.values():
        if class_name in spell.level and spell.level[class_name] == spell_level:
            result.append(spell)
    return sorted(result, key=lambda s: s.name)


def get_spells_by_school(school: SpellSchool) -> List[Spell]:
    """Get all spells of a specific school."""
    return [s for s in SPELLS.values() if s.school == school]


def get_domain_spells(domain_name: str) -> Dict[int, str]:
    """Get spells for a specific domain."""
    domain = DOMAIN_DATA.get(domain_name, {})
    return domain.get("spells", {})


def get_domain_power(domain_name: str) -> str:
    """Get the granted power for a specific domain."""
    domain = DOMAIN_DATA.get(domain_name, {})
    return domain.get("power", "")


# =============================================================================
# Spell Calculation Functions
# =============================================================================

def calculate_spell_dc(caster, spell: Spell, class_name: str) -> int:
    """Calculate the saving throw DC for a spell."""
    base_dc = 10
    spell_level = spell.level.get(class_name, 0)

    # Get casting ability modifier
    casting_ability = get_casting_ability(class_name)
    ability_mod = get_ability_modifier(caster, casting_ability)

    # Check for Spell Focus feat
    spell_focus_bonus = 0
    if hasattr(caster, 'has_feat'):
        if caster.has_feat("Spell Focus") and hasattr(caster, 'spell_focus_school'):
            if caster.spell_focus_school == spell.school.value:
                spell_focus_bonus = 1
        if caster.has_feat("Greater Spell Focus") and hasattr(caster, 'spell_focus_school'):
            if caster.spell_focus_school == spell.school.value:
                spell_focus_bonus = 2

    return base_dc + spell_level + ability_mod + spell_focus_bonus


def get_casting_ability(class_name: str) -> str:
    """Get the ability score used for casting by class."""
    casting_abilities = {
        "Wizard": "int",
        "Sorcerer": "cha",
        "Bard": "cha",
        "Cleric": "wis",
        "Druid": "wis",
        "Paladin": "wis",
        "Ranger": "wis",
    }
    return casting_abilities.get(class_name, "int")


def get_ability_modifier(entity, ability: str) -> int:
    """Get ability modifier for spell DCs."""
    ability_map = {
        "str": "str_score",
        "dex": "dex_score",
        "con": "con_score",
        "int": "int_score",
        "wis": "wis_score",
        "cha": "cha_score",
    }
    score_attr = ability_map.get(ability.lower(), "int_score")
    score = getattr(entity, score_attr, 10)
    return (score - 10) // 2


def calculate_caster_level(caster, class_name: str, spell=None) -> int:
    """Calculate effective caster level, including elemental affinity and room resonance bonuses.

    Oreka Elemental Rules:
    - Matching element (caster affinity matches spell damage type): +1 caster level
    - Opposing element (fire vs cold, earth vs electricity): -1 caster level
    - Room elemental resonance matching caster's affinity: additional +1
    """
    base_level = getattr(caster, 'level', 1)

    # Half-casters (Paladin, Ranger) have caster level = class level - 3
    if class_name in ("Paladin", "Ranger"):
        base_level = max(1, base_level - 3)

    # --- Elemental Affinity Bonus/Penalty ---
    affinity = getattr(caster, 'elemental_affinity', None)
    if affinity and spell:
        # Map affinity to energy type
        element_to_energy = {"earth": "acid", "fire": "fire", "water": "cold", "wind": "electricity"}
        caster_energy = element_to_energy.get(affinity)

        # Get spell's damage type from spell dict or Spell object
        spell_damage_type = None
        if isinstance(spell, dict):
            spell_damage_type = spell.get("damage_type", "")
            descriptors = spell.get("descriptors", [])
        else:
            spell_damage_type = getattr(spell, 'damage_type', '') or ''
            descriptors = getattr(spell, 'descriptors', []) or []

        # Also check descriptors for element match
        if not spell_damage_type:
            descriptor_map = {"Acid": "acid", "Fire": "fire", "Cold": "cold", "Electricity": "electricity"}
            for d in descriptors:
                if d in descriptor_map:
                    spell_damage_type = descriptor_map[d]
                    break

        if caster_energy and spell_damage_type:
            # Matching element: +1
            if caster_energy == spell_damage_type:
                base_level += 1
            # Opposing elements: fire<>cold, earth(acid)<>electricity(wind)
            opposites = {"fire": "cold", "cold": "fire", "acid": "electricity", "electricity": "acid"}
            if opposites.get(caster_energy) == spell_damage_type:
                base_level -= 1

    # --- Room Elemental Resonance Bonus ---
    room = getattr(caster, 'room', None)
    if room and affinity:
        try:
            from src.location_effects import get_location_effects
            le = get_location_effects()
            room_element, room_bonus = le.get_elemental_resonance(room)
            if room_element and room_element == affinity:
                base_level += room_bonus
        except Exception:
            pass

    return max(1, base_level)


def calculate_spell_damage(caster, damage_dice: str, class_name: str = None) -> Tuple[int, str]:
    """
    Calculate spell damage based on damage dice string.

    Returns (damage, description)
    """
    import re

    caster_level = calculate_caster_level(caster, class_name or getattr(caster, 'char_class', 'Wizard'))

    # Parse damage string like "1d4+1", "1d6/level max 10d6", "1d8+1/level max +5"
    damage = 0

    # Check for "per level" patterns
    level_match = re.search(r'(\d+)d(\d+)/level\s*max\s*(\d+)d\d+', damage_dice)
    if level_match:
        dice_per_level = int(level_match.group(1))
        die_size = int(level_match.group(2))
        max_dice = int(level_match.group(3))

        num_dice = min(dice_per_level * caster_level, max_dice)
        damage = sum(random.randint(1, die_size) for _ in range(num_dice))
        return damage, f"{num_dice}d{die_size}"

    # Check for "+X/level max +Y" pattern (like healing spells)
    level_bonus_match = re.search(r'(\d+)d(\d+)\+(\d+)/level\s*max\s*\+(\d+)', damage_dice)
    if level_bonus_match:
        num_dice = int(level_bonus_match.group(1))
        die_size = int(level_bonus_match.group(2))
        bonus_per_level = int(level_bonus_match.group(3))
        max_bonus = int(level_bonus_match.group(4))

        dice_damage = sum(random.randint(1, die_size) for _ in range(num_dice))
        level_bonus = min(bonus_per_level * caster_level, max_bonus)
        damage = dice_damage + level_bonus
        return damage, f"{num_dice}d{die_size}+{level_bonus}"

    # Check for "/2 levels" pattern (like vampiric touch)
    half_level_match = re.search(r'(\d+)d(\d+)/2 levels\s*max\s*(\d+)d\d+', damage_dice)
    if half_level_match:
        dice_per_2_levels = int(half_level_match.group(1))
        die_size = int(half_level_match.group(2))
        max_dice = int(half_level_match.group(3))

        num_dice = min(dice_per_2_levels * (caster_level // 2), max_dice)
        damage = sum(random.randint(1, die_size) for _ in range(num_dice))
        return damage, f"{num_dice}d{die_size}"

    # Check for flat "/level max X" pattern (like Heal)
    flat_level_match = re.search(r'(\d+)/level\s*max\s*(\d+)', damage_dice)
    if flat_level_match:
        hp_per_level = int(flat_level_match.group(1))
        max_hp = int(flat_level_match.group(2))

        damage = min(hp_per_level * caster_level, max_hp)
        return damage, f"{damage}"

    # Simple dice pattern like "1d4+1" or "4d6"
    simple_match = re.match(r'(\d+)d(\d+)(?:\+(\d+))?', damage_dice)
    if simple_match:
        num_dice = int(simple_match.group(1))
        die_size = int(simple_match.group(2))
        bonus = int(simple_match.group(3)) if simple_match.group(3) else 0

        damage = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus
        return damage, f"{num_dice}d{die_size}" + (f"+{bonus}" if bonus else "")

    return 0, damage_dice


def calculate_healing(caster, healing_dice: str, class_name: str = None) -> Tuple[int, str]:
    """Calculate healing amount based on healing dice string."""
    return calculate_spell_damage(caster, healing_dice, class_name)


def get_num_missiles(caster_level: int) -> int:
    """Calculate number of magic missiles based on caster level."""
    # 1 missile at 1st-2nd, 2 at 3rd-4th, 3 at 5th-6th, 4 at 7th-8th, 5 at 9th+
    return min(5, (caster_level + 1) // 2)


def get_num_rays(caster_level: int) -> int:
    """Calculate number of scorching rays based on caster level."""
    # 1 ray at 3rd, 2 at 7th, 3 at 11th+
    if caster_level >= 11:
        return 3
    elif caster_level >= 7:
        return 2
    return 1


# =============================================================================
# Spell Range Calculations
# =============================================================================

def get_spell_range(spell: Spell, caster_level: int) -> int:
    """Calculate actual range in feet based on range type and caster level."""
    range_type = spell.range_type.lower()

    if spell.range_feet:
        return spell.range_feet

    if range_type == "personal" or range_type == "self":
        return 0
    elif range_type == "touch":
        return 5  # Adjacent square
    elif range_type == "close":
        return 25 + (caster_level // 2) * 5  # 25 ft. + 5 ft./2 levels
    elif range_type == "medium":
        return 100 + caster_level * 10  # 100 ft. + 10 ft./level
    elif range_type == "long":
        return 400 + caster_level * 40  # 400 ft. + 40 ft./level
    elif range_type == "unlimited":
        return 99999

    return 30  # Default


# =============================================================================
# Spell List Functions
# =============================================================================

def get_all_spell_names() -> List[str]:
    """Get a list of all spell names."""
    return sorted([s.name for s in SPELLS.values()])


def get_spell_count() -> int:
    """Get total number of spells in database."""
    return len(SPELLS)


def describe_spell(name: str) -> str:
    """Get a formatted description of a spell."""
    spell = get_spell(name)
    if not spell:
        return f"Unknown spell: {name}"

    lines = [
        f"=== {spell.name} ===",
        f"School: {spell.school.value}" + (f" ({spell.subschool})" if spell.subschool else ""),
        f"Level: {', '.join(f'{cls} {lvl}' for cls, lvl in spell.level.items())}",
        f"Components: {', '.join(spell.get_components())}",
        f"Casting Time: {spell.casting_time}",
        f"Range: {spell.range_type}",
        f"Duration: {spell.duration}",
    ]

    if spell.save_type != SaveType.NONE:
        lines.append(f"Saving Throw: {spell.save_type.value} {spell.save_effect.value}")
    else:
        lines.append("Saving Throw: None")

    lines.append(f"Spell Resistance: {'Yes' if spell.spell_resistance else 'No'}")
    lines.append("")
    lines.append(spell.description)

    if spell.material:
        lines.append(f"\nMaterial Component: {spell.material}")

    return "\n".join(lines)
