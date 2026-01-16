# skills.py
"""
D&D 3.5 Skills System for OrekaMUD

This module implements the complete D&D 3.5 skill check system including:
- All core skills with ability modifiers
- Trained-only skill enforcement
- Armor check penalties
- Take 10 / Take 20 mechanics
- Opposed skill checks
- Synergy bonuses
- Feat and condition integration
"""

import random
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.character import Character
    from src.mob import Mob


@dataclass
class Skill:
    """Represents a D&D 3.5 skill."""
    name: str
    key_ability: str  # Str, Dex, Con, Int, Wis, Cha
    trained_only: bool = False
    armor_check_penalty: bool = False
    description: str = ""
    synergies: Dict[str, int] = None  # skill_name: bonus when 5+ ranks

    def __post_init__(self):
        if self.synergies is None:
            self.synergies = {}


# =============================================================================
# All D&D 3.5 Skills
# =============================================================================

SKILLS: Dict[str, Skill] = {
    # Strength-based
    "Climb": Skill(
        "Climb", "Str",
        armor_check_penalty=True,
        description="Scale walls, cliffs, and other steep surfaces."
    ),
    "Jump": Skill(
        "Jump", "Str",
        armor_check_penalty=True,
        description="Leap horizontal or vertical distances.",
        synergies={"Tumble": 2}  # 5+ ranks in Tumble gives +2 to Jump
    ),
    "Swim": Skill(
        "Swim", "Str",
        armor_check_penalty=True,  # Double penalty
        description="Move through water without drowning."
    ),

    # Dexterity-based
    "Balance": Skill(
        "Balance", "Dex",
        armor_check_penalty=True,
        description="Keep footing on narrow or slippery surfaces.",
        synergies={"Tumble": 2}
    ),
    "Escape Artist": Skill(
        "Escape Artist", "Dex",
        armor_check_penalty=True,
        description="Slip free of bonds, grapples, or tight spaces.",
        synergies={"Use Rope": 2}
    ),
    "Hide": Skill(
        "Hide", "Dex",
        armor_check_penalty=True,
        description="Conceal yourself from notice."
    ),
    "Move Silently": Skill(
        "Move Silently", "Dex",
        armor_check_penalty=True,
        description="Move without being heard."
    ),
    "Open Lock": Skill(
        "Open Lock", "Dex",
        trained_only=True,
        description="Pick locks and bypass mechanical security."
    ),
    "Ride": Skill(
        "Ride", "Dex",
        description="Control a mount in combat and difficult terrain.",
        synergies={"Handle Animal": 2}
    ),
    "Sleight of Hand": Skill(
        "Sleight of Hand", "Dex",
        trained_only=True,
        armor_check_penalty=True,
        description="Pick pockets, palm objects, and perform legerdemain."
    ),
    "Tumble": Skill(
        "Tumble", "Dex",
        trained_only=True,
        armor_check_penalty=True,
        description="Roll, flip, and tumble to avoid damage or move through threatened areas.",
        synergies={"Balance": 2, "Jump": 2}
    ),
    "Use Rope": Skill(
        "Use Rope", "Dex",
        description="Tie knots, secure bindings, and handle ropes.",
        synergies={"Climb": 2, "Escape Artist": 2}
    ),

    # Constitution-based
    "Concentration": Skill(
        "Concentration", "Con",
        description="Maintain focus while distracted, especially during spellcasting."
    ),

    # Intelligence-based
    "Appraise": Skill(
        "Appraise", "Int",
        description="Estimate the value of items and treasure."
    ),
    "Craft (any)": Skill(
        "Craft (any)", "Int",
        description="Create items using raw materials and tools."
    ),
    "Decipher Script": Skill(
        "Decipher Script", "Int",
        trained_only=True,
        description="Read ancient, foreign, or coded texts."
    ),
    "Disable Device": Skill(
        "Disable Device", "Int",
        trained_only=True,
        description="Disarm traps and sabotage mechanisms."
    ),
    "Forgery": Skill(
        "Forgery", "Int",
        description="Create fake documents and detect forgeries."
    ),
    "Knowledge (arcana)": Skill(
        "Knowledge (arcana)", "Int",
        trained_only=True,
        description="Ancient mysteries, magic traditions, arcane symbols."
    ),
    "Knowledge (architecture and engineering)": Skill(
        "Knowledge (architecture and engineering)", "Int",
        trained_only=True,
        description="Buildings, aqueducts, bridges, fortifications."
    ),
    "Knowledge (dungeoneering)": Skill(
        "Knowledge (dungeoneering)", "Int",
        trained_only=True,
        description="Aberrations, caverns, oozes, spelunking."
    ),
    "Knowledge (geography)": Skill(
        "Knowledge (geography)", "Int",
        trained_only=True,
        description="Lands, terrain, climate, people."
    ),
    "Knowledge (history)": Skill(
        "Knowledge (history)", "Int",
        trained_only=True,
        description="Royalty, wars, colonies, migrations, founding of cities."
    ),
    "Knowledge (local)": Skill(
        "Knowledge (local)", "Int",
        trained_only=True,
        description="Legends, personalities, inhabitants, laws, customs."
    ),
    "Knowledge (nature)": Skill(
        "Knowledge (nature)", "Int",
        trained_only=True,
        description="Animals, fey, giants, monstrous humanoids, plants, seasons, weather.",
        synergies={"Survival": 2}
    ),
    "Knowledge (nobility and royalty)": Skill(
        "Knowledge (nobility and royalty)", "Int",
        trained_only=True,
        description="Lineages, heraldry, family trees, mottoes, personalities."
    ),
    "Knowledge (religion)": Skill(
        "Knowledge (religion)", "Int",
        trained_only=True,
        description="Gods and goddesses, mythic history, ecclesiastic tradition, holy symbols."
    ),
    "Knowledge (the planes)": Skill(
        "Knowledge (the planes)", "Int",
        trained_only=True,
        description="Inner and Outer Planes, Astral, Ethereal, outsiders, planar magic.",
        synergies={"Survival": 2}  # On other planes
    ),
    "Search": Skill(
        "Search", "Int",
        description="Find hidden doors, traps, and concealed objects.",
        synergies={"Survival": 2}  # Following tracks
    ),
    "Spellcraft": Skill(
        "Spellcraft", "Int",
        trained_only=True,
        description="Identify spells, craft magic items, decipher scrolls.",
        synergies={"Use Magic Device": 2}
    ),

    # Wisdom-based
    "Heal": Skill(
        "Heal", "Wis",
        description="Provide first aid, treat wounds, and cure diseases."
    ),
    "Listen": Skill(
        "Listen", "Wis",
        description="Hear approaching enemies, eavesdrop, detect hidden creatures."
    ),
    "Profession (any)": Skill(
        "Profession (any)", "Wis",
        trained_only=True,
        description="Practice a trade and earn a living."
    ),
    "Sense Motive": Skill(
        "Sense Motive", "Wis",
        description="Detect lies, gauge trustworthiness, get a hunch.",
        synergies={"Diplomacy": 2}
    ),
    "Spot": Skill(
        "Spot", "Wis",
        description="Notice creatures lurking, see through disguises, spot hidden objects."
    ),
    "Survival": Skill(
        "Survival", "Wis",
        description="Navigate wilderness, track creatures, avoid hazards.",
        synergies={"Knowledge (nature)": 2}
    ),

    # Charisma-based
    "Bluff": Skill(
        "Bluff", "Cha",
        description="Deceive others, create diversions, feint in combat.",
        synergies={"Diplomacy": 2, "Intimidate": 2, "Sleight of Hand": 2, "Disguise": 2}
    ),
    "Diplomacy": Skill(
        "Diplomacy", "Cha",
        description="Negotiate, persuade, and change attitudes.",
        synergies={"Bluff": 2, "Knowledge (nobility and royalty)": 2, "Sense Motive": 2}
    ),
    "Disguise": Skill(
        "Disguise", "Cha",
        description="Change your appearance to look like another person."
    ),
    "Gather Information": Skill(
        "Gather Information", "Cha",
        description="Learn rumors, find contacts, and locate people or things.",
        synergies={"Knowledge (local)": 2}
    ),
    "Handle Animal": Skill(
        "Handle Animal", "Cha",
        trained_only=True,
        description="Train animals, teach tricks, and command animal companions.",
        synergies={"Ride": 2}
    ),
    "Intimidate": Skill(
        "Intimidate", "Cha",
        description="Cow opponents, influence through threats.",
        synergies={"Bluff": 2}
    ),
    "Perform (any)": Skill(
        "Perform (any)", "Cha",
        description="Entertain audiences with music, dance, acting, or oratory."
    ),
    "Use Magic Device": Skill(
        "Use Magic Device", "Cha",
        trained_only=True,
        description="Activate magic items as if you had the required class features or spells."
    ),
}


# =============================================================================
# Skill Check Difficulty Classes
# =============================================================================

DC_EXAMPLES = {
    # General DCs
    "very_easy": 5,
    "easy": 10,
    "average": 15,
    "tough": 20,
    "challenging": 25,
    "heroic": 30,
    "nearly_impossible": 40,

    # Climb DCs
    "climb_rope": 0,
    "climb_knotted_rope": 5,
    "climb_wall_ledges": 10,
    "climb_uneven_surface": 15,
    "climb_rough_surface": 20,
    "climb_overhang": 25,
    "climb_perfectly_smooth": 30,

    # Jump DCs (horizontal = DC per 5 ft, vertical = DC per 1 ft)
    "jump_5ft_running": 5,
    "jump_10ft_running": 10,
    "jump_15ft_running": 15,
    "jump_20ft_running": 20,
    "jump_1ft_vertical": 4,
    "jump_2ft_vertical": 8,
    "jump_3ft_vertical": 12,

    # Balance DCs
    "balance_wide_surface": 0,
    "balance_1ft_surface": 10,
    "balance_6in_surface": 15,
    "balance_2in_surface": 20,

    # Tumble DCs
    "tumble_threat_area": 15,
    "tumble_attack_soft_fall": 15,
    "tumble_through_enemy": 25,

    # Disable Device / Open Lock
    "simple_lock": 20,
    "average_lock": 25,
    "good_lock": 30,
    "amazing_lock": 40,
    "simple_trap": 10,
    "tricky_trap": 20,
    "difficult_trap": 25,

    # Hide DCs (opposed by Spot)
    "hide_no_cover": -999,  # Cannot hide
    "hide_concealment": 0,  # Opposed check only
    "hide_moving": -5,  # Penalty
    "hide_running": -20,  # Penalty
    "hide_sniping": -20,  # Penalty

    # Survival DCs
    "track_soft_ground": 10,
    "track_firm_ground": 15,
    "track_hard_ground": 20,
    "track_outdoors": 15,
    "survive_wild": 10,
    "survive_severe_weather": 15,
}


# =============================================================================
# Ability Modifier Helper
# =============================================================================

def get_ability_mod(entity, ability: str) -> int:
    """Get ability modifier for an entity."""
    ability_lower = ability.lower()
    attr_name = f"{ability_lower}_score"
    score = getattr(entity, attr_name, 10)
    return (score - 10) // 2


def get_ability_score(entity, ability: str) -> int:
    """Get raw ability score for an entity."""
    ability_lower = ability.lower()
    attr_name = f"{ability_lower}_score"
    return getattr(entity, attr_name, 10)


# =============================================================================
# Skill Check Functions
# =============================================================================

def get_skill_ranks(entity, skill_name: str) -> int:
    """Get the number of ranks an entity has in a skill."""
    skills = getattr(entity, 'skills', {})
    return skills.get(skill_name, 0)


def get_synergy_bonus(entity, skill_name: str) -> int:
    """
    Calculate synergy bonus for a skill.
    D&D 3.5: Having 5+ ranks in certain skills grants +2 to related skills.
    """
    bonus = 0
    skills = getattr(entity, 'skills', {})

    # Check each skill to see if it provides synergy to target skill
    for other_skill_name, ranks in skills.items():
        if ranks >= 5:
            other_skill = SKILLS.get(other_skill_name)
            if other_skill and skill_name in other_skill.synergies:
                bonus += other_skill.synergies[skill_name]

    return bonus


def get_armor_check_penalty(entity) -> int:
    """Get the total armor check penalty from equipped armor and shield."""
    penalty = getattr(entity, 'armor_check_penalty', 0)

    # Check equipped items
    equipment = getattr(entity, 'equipment', {})

    body_armor = equipment.get('body')
    if body_armor:
        penalty += getattr(body_armor, 'armor_check_penalty', 0)

    shield = equipment.get('off_hand')
    if shield and getattr(shield, 'item_type', '').lower() == 'shield':
        penalty += getattr(shield, 'armor_check_penalty', 0)

    return penalty


def get_size_modifier(entity, skill_name: str) -> int:
    """
    Get size modifier for certain skills.
    Hide: +4 Small, +8 Tiny, -4 Large, -8 Huge
    Grapple: opposite
    """
    size = getattr(entity, 'size', 'medium').lower()

    size_mods = {
        'fine': {'hide': 16, 'grapple': -16},
        'diminutive': {'hide': 12, 'grapple': -12},
        'tiny': {'hide': 8, 'grapple': -8},
        'small': {'hide': 4, 'grapple': -4},
        'medium': {'hide': 0, 'grapple': 0},
        'large': {'hide': -4, 'grapple': 4},
        'huge': {'hide': -8, 'grapple': 8},
        'gargantuan': {'hide': -12, 'grapple': 12},
        'colossal': {'hide': -16, 'grapple': 16},
    }

    skill_lower = skill_name.lower()
    if skill_lower == 'hide':
        return size_mods.get(size, {}).get('hide', 0)

    return 0


def get_feat_bonus(entity, skill_name: str) -> int:
    """Get feat bonuses for a skill using the feats module."""
    try:
        from src import feats as feat_module
        return feat_module.get_skill_feat_bonus(entity, skill_name)
    except ImportError:
        return 0


def get_condition_modifier(entity, skill_name: str) -> int:
    """Get condition modifiers for skill checks."""
    try:
        from src import conditions as cond

        penalty = 0

        # Get all active conditions
        conditions = getattr(entity, 'conditions', set())
        active = getattr(entity, 'active_conditions', {})
        all_conditions = conditions | set(active.keys())

        for cond_name in all_conditions:
            condition = cond.get_condition(cond_name)
            if not condition:
                continue

            # Check for skill_penalty_all (applies to all skills)
            if 'skill_penalty_all' in condition.effects:
                penalty += condition.effects['skill_penalty_all']

            # Check for specific skill_penalty dict
            if 'skill_penalty' in condition.effects:
                skill_penalties = condition.effects['skill_penalty']
                if isinstance(skill_penalties, dict):
                    # Check for exact skill match
                    if skill_name in skill_penalties:
                        penalty += skill_penalties[skill_name]
                    # Check for partial match (e.g., "Spot" in "Spot check")
                    for skill_key, pen_val in skill_penalties.items():
                        if skill_key.lower() in skill_name.lower():
                            penalty += pen_val
                            break

            # Check for reaction_skill_penalty (for Dex-based skills in certain situations)
            if 'reaction_skill_penalty' in condition.effects:
                skill = SKILLS.get(skill_name)
                if skill and skill.key_ability == 'Dex':
                    penalty += condition.effects['reaction_skill_penalty']

        # Check for Dex-based skill penalties from other conditions
        skill = SKILLS.get(skill_name)
        if skill and skill.key_ability == 'Dex':
            penalty += cond.calculate_condition_modifiers(entity, 'dex_skill_penalty')

        # Check for Str-based skill penalties
        if skill and skill.key_ability == 'Str':
            penalty += cond.calculate_condition_modifiers(entity, 'str_skill_penalty')

        return -penalty  # Return as negative since penalties reduce the check
    except ImportError:
        return 0


def calculate_skill_modifier(entity, skill_name: str) -> Tuple[int, Dict[str, int]]:
    """
    Calculate total skill modifier including all bonuses and penalties.

    Returns:
        Tuple of (total_modifier, breakdown_dict)
    """
    skill = SKILLS.get(skill_name)
    if not skill:
        # Try to find a matching skill (for subtypes like "Knowledge (history)")
        for sname, s in SKILLS.items():
            if skill_name.lower().startswith(sname.lower().split('(')[0].strip()):
                skill = s
                break

    if not skill:
        return 0, {"error": f"Unknown skill: {skill_name}"}

    breakdown = {}

    # Skill ranks
    ranks = get_skill_ranks(entity, skill_name)
    breakdown['ranks'] = ranks

    # Ability modifier
    ability_mod = get_ability_mod(entity, skill.key_ability)
    breakdown[f'{skill.key_ability}_mod'] = ability_mod

    # Synergy bonus
    synergy = get_synergy_bonus(entity, skill_name)
    if synergy:
        breakdown['synergy'] = synergy

    # Armor check penalty (if applicable)
    acp = 0
    if skill.armor_check_penalty:
        acp = get_armor_check_penalty(entity)
        # Swim has double armor check penalty
        if skill_name == "Swim":
            acp *= 2
        if acp:
            breakdown['armor_check'] = -acp

    # Size modifier
    size_mod = get_size_modifier(entity, skill_name)
    if size_mod:
        breakdown['size'] = size_mod

    # Feat bonus
    feat_bonus = get_feat_bonus(entity, skill_name)
    if feat_bonus:
        breakdown['feats'] = feat_bonus

    # Condition modifiers
    condition_mod = get_condition_modifier(entity, skill_name)
    if condition_mod:
        breakdown['conditions'] = condition_mod

    # Calculate total
    total = ranks + ability_mod + synergy - acp + size_mod + feat_bonus + condition_mod

    return total, breakdown


def skill_check(
    entity,
    skill_name: str,
    dc: int = None,
    modifier: int = 0,
    take_10: bool = False,
    take_20: bool = False,
    circumstance_bonus: int = 0
) -> Tuple[bool, int, str]:
    """
    Perform a skill check.

    Args:
        entity: The character or mob making the check
        skill_name: Name of the skill to check
        dc: Difficulty class (None for just returning the roll total)
        modifier: Additional situational modifier
        take_10: Use 10 instead of rolling (requires no stress)
        take_20: Use 20 instead of rolling (requires time and no failure consequences)
        circumstance_bonus: Bonus from good circumstances

    Returns:
        Tuple of (success, total, description)
    """
    skill = SKILLS.get(skill_name)
    if not skill:
        # Try partial match
        for sname, s in SKILLS.items():
            if skill_name.lower() in sname.lower():
                skill = s
                skill_name = sname
                break

    if not skill:
        return False, 0, f"Unknown skill: {skill_name}"

    # Check trained-only restriction
    ranks = get_skill_ranks(entity, skill_name)
    if skill.trained_only and ranks == 0:
        return False, 0, f"You cannot use {skill_name} untrained."

    # Get skill modifier
    total_mod, breakdown = calculate_skill_modifier(entity, skill_name)

    # Determine the roll
    if take_20:
        roll = 20
        roll_str = "Take 20"
    elif take_10:
        roll = 10
        roll_str = "Take 10"
    else:
        roll = random.randint(1, 20)
        roll_str = f"d20({roll})"

    # Calculate total
    total = roll + total_mod + modifier + circumstance_bonus

    # Build description
    mod_parts = []
    for key, val in breakdown.items():
        if key != 'error' and val != 0:
            mod_parts.append(f"{key}: {val:+d}")

    if modifier:
        mod_parts.append(f"situational: {modifier:+d}")
    if circumstance_bonus:
        mod_parts.append(f"circumstance: {circumstance_bonus:+d}")

    mod_str = ", ".join(mod_parts) if mod_parts else "no modifiers"

    entity_name = getattr(entity, 'name', 'Unknown')

    if dc is not None:
        success = total >= dc
        result = "SUCCESS" if success else "FAILURE"
        desc = f"{entity_name} {skill_name} check: {roll_str} + {total_mod} = {total} vs DC {dc} - {result}"
        if mod_parts:
            desc += f"\n  ({mod_str})"
        return success, total, desc
    else:
        desc = f"{entity_name} {skill_name} check: {roll_str} + {total_mod} = {total}"
        if mod_parts:
            desc += f"\n  ({mod_str})"
        return True, total, desc


def opposed_skill_check(
    actor,
    actor_skill: str,
    target,
    target_skill: str,
    actor_modifier: int = 0,
    target_modifier: int = 0
) -> Tuple[bool, int, int, str]:
    """
    Perform an opposed skill check between two entities.

    Args:
        actor: The initiating entity
        actor_skill: Skill the actor uses
        target: The opposing entity
        target_skill: Skill the target uses
        actor_modifier: Situational bonus for actor
        target_modifier: Situational bonus for target

    Returns:
        Tuple of (actor_wins, actor_total, target_total, description)
    """
    # Actor's check
    actor_success, actor_total, actor_desc = skill_check(
        actor, actor_skill, modifier=actor_modifier
    )

    # Target's check
    target_success, target_total, target_desc = skill_check(
        target, target_skill, modifier=target_modifier
    )

    # Determine winner (actor wins ties)
    actor_wins = actor_total >= target_total

    actor_name = getattr(actor, 'name', 'Actor')
    target_name = getattr(target, 'name', 'Target')

    result = actor_name if actor_wins else target_name
    desc = (
        f"Opposed check: {actor_name} ({actor_skill}) vs {target_name} ({target_skill})\n"
        f"  {actor_name}: {actor_total}\n"
        f"  {target_name}: {target_total}\n"
        f"  Winner: {result}"
    )

    return actor_wins, actor_total, target_total, desc


# =============================================================================
# Specific Skill Check Functions
# =============================================================================

def check_hide(hider, spotter=None, modifier: int = 0) -> Tuple[bool, int, str]:
    """
    Perform a Hide check, optionally opposed by Spot.
    """
    # Get movement modifier
    is_moving = getattr(hider, 'is_moving', False)
    is_running = getattr(hider, 'is_running', False)

    move_mod = 0
    if is_running:
        move_mod = -20
    elif is_moving:
        move_mod = -5

    if spotter:
        return opposed_skill_check(
            hider, "Hide",
            spotter, "Spot",
            actor_modifier=modifier + move_mod
        )[:3] + (f"Hide vs Spot check",)
    else:
        return skill_check(hider, "Hide", modifier=modifier + move_mod)


def check_move_silently(mover, listener=None, modifier: int = 0) -> Tuple[bool, int, str]:
    """
    Perform a Move Silently check, optionally opposed by Listen.
    """
    if listener:
        return opposed_skill_check(
            mover, "Move Silently",
            listener, "Listen",
            actor_modifier=modifier
        )[:3] + (f"Move Silently vs Listen check",)
    else:
        return skill_check(mover, "Move Silently", modifier=modifier)


def check_bluff_feint(bluffer, target) -> Tuple[bool, int, int, str]:
    """
    Perform a Bluff check to feint in combat (opposed by Sense Motive or BAB + Wis).
    """
    # Target uses Sense Motive or BAB + Wis mod (whichever is higher)
    sense_motive_mod, _ = calculate_skill_modifier(target, "Sense Motive")

    bab = getattr(target, 'bab', None)
    if bab is None:
        level = getattr(target, 'level', 1)
        bab = (level * 3) // 4
    wis_mod = get_ability_mod(target, "Wis")
    combat_sense = bab + wis_mod

    # Use higher of the two
    if combat_sense > sense_motive_mod:
        target_skill = "Combat Sense (BAB + Wis)"
        target_mod = combat_sense
    else:
        target_skill = "Sense Motive"
        target_mod = sense_motive_mod

    # Bluffer's check
    success, bluff_total, bluff_desc = skill_check(bluffer, "Bluff")

    # Target's check
    target_roll = random.randint(1, 20)
    target_total = target_roll + target_mod

    actor_wins = bluff_total >= target_total

    bluffer_name = getattr(bluffer, 'name', 'Bluffer')
    target_name = getattr(target, 'name', 'Target')

    result = "feint succeeds" if actor_wins else "feint fails"
    desc = (
        f"{bluffer_name} attempts to feint {target_name}!\n"
        f"  Bluff: {bluff_total} vs {target_skill}: {target_total}\n"
        f"  Result: {result.upper()}"
    )

    if actor_wins:
        desc += f"\n  {target_name} is denied Dex bonus to AC against next attack!"

    return actor_wins, bluff_total, target_total, desc


def check_diplomacy(diplomat, target, current_attitude: str = "indifferent") -> Tuple[str, int, str]:
    """
    Perform a Diplomacy check to change an NPC's attitude.

    Attitudes: hostile, unfriendly, indifferent, friendly, helpful
    """
    attitude_order = ["hostile", "unfriendly", "indifferent", "friendly", "helpful"]

    # DC based on starting attitude
    attitude_dcs = {
        "hostile": 25,
        "unfriendly": 20,
        "indifferent": 15,
        "friendly": 10,
        "helpful": 0  # Already helpful
    }

    base_dc = attitude_dcs.get(current_attitude, 15)

    success, total, desc = skill_check(diplomat, "Diplomacy", dc=base_dc)

    diplomat_name = getattr(diplomat, 'name', 'Diplomat')
    target_name = getattr(target, 'name', 'Target')

    # Determine new attitude
    current_idx = attitude_order.index(current_attitude) if current_attitude in attitude_order else 2

    if success:
        # Improve by 1 step (2 steps if beat DC by 5+)
        steps = 1
        if total >= base_dc + 5:
            steps = 2
        new_idx = min(current_idx + steps, len(attitude_order) - 1)
    else:
        # Fail by 5+: attitude worsens
        if total < base_dc - 5:
            new_idx = max(current_idx - 1, 0)
        else:
            new_idx = current_idx

    new_attitude = attitude_order[new_idx]

    result_desc = (
        f"{diplomat_name} attempts to persuade {target_name}.\n"
        f"  {desc}\n"
        f"  Attitude: {current_attitude} -> {new_attitude}"
    )

    return new_attitude, total, result_desc


def check_intimidate(intimidator, target) -> Tuple[bool, int, str]:
    """
    Perform an Intimidate check to demoralize or coerce.
    DC = 10 + target's HD + target's Wis mod
    """
    hd = getattr(target, 'level', 1)
    wis_mod = get_ability_mod(target, "Wis")
    dc = 10 + hd + wis_mod

    success, total, desc = skill_check(intimidator, "Intimidate", dc=dc)

    intimidator_name = getattr(intimidator, 'name', 'Intimidator')
    target_name = getattr(target, 'name', 'Target')

    if success:
        result = f"{target_name} is shaken for 1 round (+1 per 5 points above DC)!"
        rounds = 1 + max(0, (total - dc) // 5)
        result = f"{target_name} is shaken for {rounds} round(s)!"
    else:
        result = f"{target_name} is not intimidated."

    full_desc = f"{intimidator_name} tries to intimidate {target_name}.\n  {desc}\n  {result}"

    return success, total, full_desc


def check_survival_track(tracker, dc: int = 15, modifier: int = 0) -> Tuple[bool, int, str]:
    """
    Perform a Survival check to track.

    Base DC depends on ground:
    - Very soft ground: DC 5
    - Soft ground: DC 10
    - Firm ground: DC 15
    - Hard ground: DC 20

    Modifiers:
    - Every 24 hours since trail was made: +1
    - Every hour of rain: +1
    - Fresh snow: +10
    - Poor visibility: +6
    - Tracked party has 3-5 creatures: -1
    - Tracked party has 6-10 creatures: -2
    - Tracked party has 11-25 creatures: -4
    """
    # Require Track feat
    has_track = False
    feats = getattr(tracker, 'feats', [])
    for f in feats:
        if 'track' in f.lower():
            has_track = True
            break

    # Rangers get Track for free at level 1
    char_class = getattr(tracker, 'char_class', '').lower()
    if char_class == 'ranger':
        has_track = True

    if not has_track:
        return False, 0, "You must have the Track feat to follow tracks using Survival."

    return skill_check(tracker, "Survival", dc=dc, modifier=modifier)


def check_concentration_damage(caster, damage_taken: int, spell_level: int = 1) -> Tuple[bool, int, str]:
    """
    Concentration check when taking damage while casting.
    DC = 10 + damage dealt + spell level
    """
    dc = 10 + damage_taken + spell_level
    return skill_check(caster, "Concentration", dc=dc)


def check_concentration_defensive(caster, spell_level: int = 1) -> Tuple[bool, int, str]:
    """
    Concentration check for casting defensively.
    DC = 15 + spell level
    """
    dc = 15 + spell_level
    return skill_check(caster, "Concentration", dc=dc)


# =============================================================================
# Skill List Helper
# =============================================================================

def get_all_skills() -> List[str]:
    """Return list of all skill names."""
    return list(SKILLS.keys())


def get_class_skills(char_class: str) -> List[str]:
    """Get the class skills for a given class."""
    try:
        from src.classes import CLASSES
        class_data = CLASSES.get(char_class, {})
        return class_data.get("class_skills", [])
    except ImportError:
        return []


def is_class_skill(entity, skill_name: str) -> bool:
    """Check if a skill is a class skill for the entity."""
    char_class = getattr(entity, 'char_class', None)
    if not char_class:
        return False

    class_skills = get_class_skills(char_class)

    # Check for exact match or Knowledge (all) / Craft (any) / etc.
    if skill_name in class_skills:
        return True

    # Check for Knowledge (all) granting all Knowledge skills
    if skill_name.startswith("Knowledge") and "Knowledge (all)" in class_skills:
        return True

    # Check for Craft (any) / Perform (any) / Profession (any)
    for generic in ["Craft (any)", "Perform (any)", "Profession (any)"]:
        if generic in class_skills:
            base = generic.replace(" (any)", "")
            if skill_name.startswith(base):
                return True

    return False


def get_max_ranks(entity, skill_name: str) -> int:
    """
    Get maximum skill ranks for an entity.
    Class skill: level + 3
    Cross-class skill: (level + 3) / 2
    """
    level = getattr(entity, 'level', 1)
    max_class = level + 3
    max_cross = (level + 3) // 2

    if is_class_skill(entity, skill_name):
        return max_class
    return max_cross
