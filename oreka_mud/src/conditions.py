"""
D&D 3.5 Edition Conditions System for OrekaMUD3

This module defines all standard D&D 3.5 conditions and their effects.
Each condition has mechanical effects that are applied during combat calculations.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Callable, Any


@dataclass
class Condition:
    """Represents a D&D 3.5 condition with its effects."""
    name: str
    description: str
    effects: Dict[str, Any]
    # Optional: function to call when condition is applied/removed
    on_apply: Optional[Callable] = None
    on_remove: Optional[Callable] = None
    on_round_start: Optional[Callable] = None  # Called each round


# D&D 3.5 Core Conditions
CONDITIONS: Dict[str, Condition] = {
    # =========================================================================
    # Physical Conditions
    # =========================================================================
    "blinded": Condition(
        name="Blinded",
        description="Cannot see. -2 AC, loses Dex bonus to AC, -4 on Strength/Dex checks, "
                    "opponents have 50% concealment, -4 on Search and Spot checks.",
        effects={
            "ac_penalty": 2,
            "loses_dex_to_ac": True,
            "attack_penalty": 2,  # Can't see target
            "miss_chance": 50,
            "skill_penalty": {"Search": 4, "Spot": 4},
            "str_check_penalty": 4,
            "dex_check_penalty": 4,
        }
    ),

    "dazzled": Condition(
        name="Dazzled",
        description="Unable to see well because of overstimulation. -1 on attack rolls, "
                    "Search, and Spot checks.",
        effects={
            "attack_penalty": 1,
            "skill_penalty": {"Search": 1, "Spot": 1},
        }
    ),

    "deafened": Condition(
        name="Deafened",
        description="Cannot hear. -4 on initiative, automatically fails Listen checks, "
                    "20% spell failure for spells with verbal components.",
        effects={
            "initiative_penalty": 4,
            "auto_fail_listen": True,
            "spell_failure": 20,
        }
    ),

    "entangled": Condition(
        name="Entangled",
        description="Ensnared. -2 on attack rolls, -4 on Dex. Cannot run or charge. "
                    "Concentration check DC 15 + spell level to cast spells.",
        effects={
            "attack_penalty": 2,
            "dex_penalty": 4,
            "cannot_run": True,
            "cannot_charge": True,
            "concentration_dc_bonus": 15,
        }
    ),

    "exhausted": Condition(
        name="Exhausted",
        description="Extremely fatigued. -6 to Str and Dex, move at half speed. "
                    "One hour of rest reduces to fatigued.",
        effects={
            "str_penalty": 6,
            "dex_penalty": 6,
            "speed_multiplier": 0.5,
        }
    ),

    "fatigued": Condition(
        name="Fatigued",
        description="Tired. -2 to Str and Dex, cannot run or charge. "
                    "8 hours rest removes condition.",
        effects={
            "str_penalty": 2,
            "dex_penalty": 2,
            "cannot_run": True,
            "cannot_charge": True,
        }
    ),

    "grappled": Condition(
        name="Grappled",
        description="Wrestling with opponent. Cannot move, -4 to Dex. "
                    "Can only attack with light weapons, unarmed, or natural weapons. "
                    "-2 on all attack rolls (included in grapple checks).",
        effects={
            "cannot_move": True,
            "dex_penalty": 4,
            "attack_penalty": 2,
            "limited_weapons": True,
        }
    ),

    "helpless": Condition(
        name="Helpless",
        description="Paralyzed, held, bound, sleeping, unconscious, or otherwise immobile. "
                    "Dex 0 (-5 modifier). Melee attackers get +4 bonus. "
                    "Can be coup de graced.",
        effects={
            "dex_score": 0,
            "melee_attack_bonus_against": 4,
            "can_be_coup_de_grace": True,
        }
    ),

    "paralyzed": Condition(
        name="Paralyzed",
        description="Frozen in place, unable to move or act. "
                    "Str and Dex effectively 0. Helpless.",
        effects={
            "cannot_act": True,
            "cannot_move": True,
            "str_score": 0,
            "dex_score": 0,
            "is_helpless": True,
        }
    ),

    "petrified": Condition(
        name="Petrified",
        description="Turned to stone. Unconscious. If broken, cannot be restored.",
        effects={
            "is_stone": True,
            "cannot_act": True,
            "cannot_move": True,
            "unconscious": True,
        }
    ),

    "pinned": Condition(
        name="Pinned",
        description="Held immobile (not helpless) in grapple. "
                    "Loses Dex bonus, -4 AC vs other attackers.",
        effects={
            "cannot_move": True,
            "loses_dex_to_ac": True,
            "ac_penalty_vs_others": 4,
        }
    ),

    "prone": Condition(
        name="Prone",
        description="Lying on ground. -4 on melee attack rolls, cannot use ranged weapons. "
                    "+4 AC vs ranged, -4 AC vs melee.",
        effects={
            "melee_attack_penalty": 4,
            "cannot_ranged": True,
            "ranged_ac_bonus": 4,
            "melee_ac_penalty": 4,
        }
    ),

    "stunned": Condition(
        name="Stunned",
        description="Reeling and unable to act. Drops everything held, cannot take actions, "
                    "-2 AC, loses Dex bonus to AC.",
        effects={
            "cannot_act": True,
            "drops_items": True,
            "ac_penalty": 2,
            "loses_dex_to_ac": True,
        }
    ),

    # =========================================================================
    # Mental/Fear Conditions
    # =========================================================================
    "confused": Condition(
        name="Confused",
        description="Unable to determine actions. Each round, roll d100: "
                    "01-10 attack caster, 11-20 act normally, 21-50 babble, "
                    "51-70 flee, 71-100 attack nearest creature.",
        effects={
            "random_action": True,
            "confusion_table": True,
        }
    ),

    "cowering": Condition(
        name="Cowering",
        description="Frozen in fear, loses Dex bonus to AC, "
                    "-2 to AC, cannot take actions.",
        effects={
            "cannot_act": True,
            "ac_penalty": 2,
            "loses_dex_to_ac": True,
        }
    ),

    "dazed": Condition(
        name="Dazed",
        description="Unable to act normally. Cannot take actions, no penalty to AC.",
        effects={
            "cannot_act": True,
        }
    ),

    "fascinated": Condition(
        name="Fascinated",
        description="Entranced. -4 on skill checks made as reactions (Spot, Listen). "
                    "Potential threats allow new save, obvious threats break fascination.",
        effects={
            "reaction_skill_penalty": 4,
            "break_on_threat": True,
        }
    ),

    "frightened": Condition(
        name="Frightened",
        description="Afraid and must flee. -2 on attack rolls, saving throws, "
                    "skill checks, and ability checks. Must flee from source of fear.",
        effects={
            "attack_penalty": 2,
            "save_penalty": 2,
            "skill_penalty_all": 2,
            "ability_check_penalty": 2,
            "must_flee": True,
        }
    ),

    "nauseated": Condition(
        name="Nauseated",
        description="Stomach churning. Cannot attack, cast spells, concentrate, "
                    "or do anything else requiring attention. Can only move.",
        effects={
            "cannot_attack": True,
            "cannot_cast": True,
            "cannot_concentrate": True,
            "move_only": True,
        }
    ),

    "panicked": Condition(
        name="Panicked",
        description="Overwhelmed with fear. Must flee, drop held items, "
                    "-2 on saving throws, skill checks, ability checks. "
                    "If cornered, cowers.",
        effects={
            "must_flee": True,
            "drops_items": True,
            "save_penalty": 2,
            "skill_penalty_all": 2,
            "ability_check_penalty": 2,
            "cower_if_cornered": True,
        }
    ),

    "shaken": Condition(
        name="Shaken",
        description="Mildly afraid. -2 on attack rolls, saving throws, "
                    "skill checks, and ability checks.",
        effects={
            "attack_penalty": 2,
            "save_penalty": 2,
            "skill_penalty_all": 2,
            "ability_check_penalty": 2,
        }
    ),

    # =========================================================================
    # Other Conditions
    # =========================================================================
    "incorporeal": Condition(
        name="Incorporeal",
        description="No physical body. Immune to non-magical attacks. "
                    "50% chance to ignore force effects and magical attacks.",
        effects={
            "immune_nonmagical": True,
            "miss_chance_magic": 50,
        }
    ),

    "invisible": Condition(
        name="Invisible",
        description="Cannot be seen. +2 on attack rolls against sighted opponents. "
                    "Opponents have -2 to hit. Ignores foe's Dex bonus to AC.",
        effects={
            "attack_bonus": 2,
            "attackers_penalty": 2,
            "ignore_dex_to_ac": True,
            "total_concealment": True,
        }
    ),

    "sickened": Condition(
        name="Sickened",
        description="Mildly ill. -2 on attack rolls, weapon damage, "
                    "saving throws, skill checks, and ability checks.",
        effects={
            "attack_penalty": 2,
            "damage_penalty": 2,
            "save_penalty": 2,
            "skill_penalty_all": 2,
            "ability_check_penalty": 2,
        }
    ),

    "staggered": Condition(
        name="Staggered",
        description="So badly hurt can barely act. Can only take a single "
                    "standard or move action each round (not both).",
        effects={
            "single_action_only": True,
        }
    ),

    "stable": Condition(
        name="Stable",
        description="Dying but no longer losing HP. Still unconscious at negative HP.",
        effects={
            "no_bleed": True,
            "unconscious": True,
        }
    ),

    "unconscious": Condition(
        name="Unconscious",
        description="Not awake. Cannot perceive or act. Helpless.",
        effects={
            "cannot_act": True,
            "cannot_perceive": True,
            "is_helpless": True,
        }
    ),

    # =========================================================================
    # Combat-Specific Conditions (used for tracking)
    # =========================================================================
    "flanked": Condition(
        name="Flanked",
        description="Being attacked from opposite sides. "
                    "Attackers get +2 to hit, can sneak attack.",
        effects={
            "flanking_bonus_against": 2,
            "can_be_sneak_attacked": True,
        }
    ),

    "flat_footed": Condition(
        name="Flat-Footed",
        description="Not yet acted in combat. Loses Dex bonus to AC, "
                    "can be sneak attacked.",
        effects={
            "loses_dex_to_ac": True,
            "can_be_sneak_attacked": True,
        }
    ),

    "silenced": Condition(
        name="Silenced",
        description="Cannot speak or make verbal sounds. "
                    "Cannot cast spells with verbal components.",
        effects={
            "cannot_speak": True,
            "cannot_verbal_component": True,
        }
    ),

    "bound": Condition(
        name="Bound",
        description="Tied up or restrained. Cannot move hands freely. "
                    "Cannot cast spells with somatic components.",
        effects={
            "cannot_move_hands": True,
            "cannot_somatic_component": True,
        }
    ),

    "gagged": Condition(
        name="Gagged",
        description="Mouth covered or blocked. Cannot speak or use verbal components.",
        effects={
            "cannot_speak": True,
            "cannot_verbal_component": True,
        }
    ),

    "disarmed": Condition(
        name="Disarmed",
        description="Weapon knocked from hands. Must use unarmed attacks or retrieve weapon.",
        effects={
            "cannot_use_weapon": True,
            "attack_penalty": 4,
        }
    ),

    "pushed": Condition(
        name="Pushed",
        description="Forced back by a bull rush or similar effect.",
        effects={}
    ),

    "poisoned": Condition(
        name="Poisoned",
        description="Poisoned - taking periodic damage. -1 on attack rolls and saving throws.",
        effects={
            "attack_penalty": 1,
            "save_penalty": 1,
        }
    ),

    "diseased": Condition(
        name="Diseased",
        description="Diseased - weakened by illness. -2 on attack rolls and saving throws, move at 3/4 speed.",
        effects={
            "attack_penalty": 2,
            "save_penalty": 2,
            "speed_multiplier": 0.75,
        }
    ),

    "charging": Condition(
        name="Charging",
        description="Charging - +2 attack bonus, but -2 penalty to AC until next turn.",
        effects={
            "ac_penalty": 2,
        }
    ),
}


def get_condition(name: str) -> Optional[Condition]:
    """Get a condition by name (case-insensitive)."""
    return CONDITIONS.get(name.lower())


def get_effect_value(condition_name: str, effect_key: str, default=None):
    """Get a specific effect value from a condition."""
    condition = get_condition(condition_name)
    if condition:
        return condition.effects.get(effect_key, default)
    return default


def calculate_condition_modifiers(entity, modifier_type: str) -> int:
    """
    Calculate total modifier from all conditions for a given type.

    modifier_type can be:
    - 'attack_penalty'
    - 'ac_penalty'
    - 'save_penalty'
    - 'damage_penalty'
    - etc.
    """
    total = 0
    conditions = getattr(entity, 'conditions', set())
    active = getattr(entity, 'active_conditions', {})

    all_conditions = conditions | set(active.keys())

    for cond_name in all_conditions:
        condition = get_condition(cond_name)
        if condition and modifier_type in condition.effects:
            value = condition.effects[modifier_type]
            if isinstance(value, (int, float)):
                total += value

    return total


def has_effect(entity, effect_key: str) -> bool:
    """Check if entity has any condition with specified effect."""
    conditions = getattr(entity, 'conditions', set())
    active = getattr(entity, 'active_conditions', {})

    all_conditions = conditions | set(active.keys())

    for cond_name in all_conditions:
        condition = get_condition(cond_name)
        if condition and effect_key in condition.effects:
            if condition.effects[effect_key]:
                return True
    return False


def can_act(entity) -> bool:
    """Check if entity can take actions based on conditions."""
    return not has_effect(entity, 'cannot_act')


def can_move(entity) -> bool:
    """Check if entity can move based on conditions."""
    return not has_effect(entity, 'cannot_move')


def can_cast_spells(entity) -> bool:
    """Check if entity can cast spells based on conditions."""
    if has_effect(entity, 'cannot_cast'):
        return False
    if has_effect(entity, 'cannot_act'):
        return False
    return True


def get_condition_list() -> list:
    """Get list of all condition names."""
    return list(CONDITIONS.keys())


def describe_condition(name: str) -> str:
    """Get the description of a condition."""
    condition = get_condition(name)
    if condition:
        return f"{condition.name}: {condition.description}"
    return f"Unknown condition: {name}"
