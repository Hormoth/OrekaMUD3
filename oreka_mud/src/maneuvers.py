"""
D&D 3.5 Edition Combat Maneuvers for OrekaMUD3

This module implements the core combat maneuvers from D&D 3.5:
- Disarm: Knock weapon from opponent's hand
- Trip: Knock opponent prone
- Bull Rush: Push opponent back
- Grapple: Grab and restrain opponent
- Overrun: Move through opponent's space
- Sunder: Destroy opponent's weapon/shield
- Feint: Bluff to deny Dex to AC
- Whirlwind Attack: Attack all adjacent enemies
- Spring Attack: Move-attack-move without AoO
- Stunning Fist: Stun opponent on hit
"""

import random
from typing import Optional, Tuple, List, Any


# =============================================================================
# Size Categories and Modifiers
# =============================================================================

SIZE_CATEGORIES = {
    "fine": -16,
    "diminutive": -12,
    "tiny": -8,
    "small": -4,
    "medium": 0,
    "large": 4,
    "huge": 8,
    "gargantuan": 12,
    "colossal": 16,
}


def get_size_modifier(entity) -> int:
    """Get size modifier for grapple/bull rush checks."""
    size = getattr(entity, 'size', 'medium').lower()
    return SIZE_CATEGORIES.get(size, 0)


def get_ability_mod(entity, ability: str) -> int:
    """Get ability modifier for an entity."""
    if hasattr(entity, 'ability_scores'):
        score = entity.ability_scores.get(ability, 10)
    elif hasattr(entity, f'{ability.lower()}_score'):
        score = getattr(entity, f'{ability.lower()}_score', 10)
    else:
        score = 10
    return (score - 10) // 2


def get_bab(entity) -> int:
    """Get base attack bonus."""
    level = getattr(entity, 'level', 1)
    if hasattr(entity, 'char_class'):
        from src.classes import CLASSES
        class_data = CLASSES.get(entity.char_class, {})
        bab_type = class_data.get('bab', 'medium')
        if bab_type == 'full':
            return level
        elif bab_type == 'medium':
            return (level * 3) // 4
        else:
            return level // 2
    return (level * 3) // 4


def get_skill_ranks(entity, skill: str) -> int:
    """Get skill ranks for an entity."""
    skills = getattr(entity, 'skills', {})
    return skills.get(skill, 0)


def has_feat(entity, feat_name: str) -> bool:
    """Check if entity has a feat."""
    if hasattr(entity, 'has_feat'):
        return entity.has_feat(feat_name)
    feats = getattr(entity, 'feats', [])
    for f in feats:
        if feat_name.lower() in f.lower():
            return True
    return False


def trigger_aoo(defender, attacker, reason: str) -> Optional[str]:
    """Trigger attack of opportunity if applicable."""
    from src.combat import trigger_aoo as combat_aoo
    return combat_aoo(defender, attacker, reason)


# =============================================================================
# Opposed Roll System
# =============================================================================

def opposed_roll(
    attacker,
    defender,
    attacker_stat: str,
    defender_stat: str,
    attacker_bonus: int = 0,
    defender_bonus: int = 0,
    attacker_size_matters: bool = False,
    defender_size_matters: bool = False,
) -> Tuple[bool, int, int, str]:
    """
    Make an opposed roll between attacker and defender.

    Returns: (attacker_wins, attacker_total, defender_total, description)
    """
    # Roll dice
    attacker_roll = random.randint(1, 20)
    defender_roll = random.randint(1, 20)

    # Get stat modifiers
    attacker_mod = get_ability_mod(attacker, attacker_stat)
    defender_mod = get_ability_mod(defender, defender_stat)

    # Add size modifiers if applicable
    attacker_size = get_size_modifier(attacker) if attacker_size_matters else 0
    defender_size = get_size_modifier(defender) if defender_size_matters else 0

    # Calculate totals
    attacker_total = attacker_roll + attacker_mod + attacker_bonus + attacker_size
    defender_total = defender_roll + defender_mod + defender_bonus + defender_size

    # Attacker wins ties
    attacker_wins = attacker_total >= defender_total

    desc = (f"{attacker.name}: d20({attacker_roll}) + {attacker_mod} + {attacker_bonus} = {attacker_total} vs "
            f"{defender.name}: d20({defender_roll}) + {defender_mod} + {defender_bonus} = {defender_total}")

    return attacker_wins, attacker_total, defender_total, desc


def opposed_attack_roll(attacker, defender, attacker_bonus: int = 0, defender_bonus: int = 0) -> Tuple[bool, int, int, str]:
    """
    Opposed attack roll (for Disarm, Sunder).
    Uses BAB + Str mod + size modifier.
    """
    attacker_roll = random.randint(1, 20)
    defender_roll = random.randint(1, 20)

    attacker_bab = get_bab(attacker)
    defender_bab = get_bab(defender)

    attacker_str = get_ability_mod(attacker, "Str")
    defender_str = get_ability_mod(defender, "Str")

    attacker_size = get_size_modifier(attacker)
    defender_size = get_size_modifier(defender)

    attacker_total = attacker_roll + attacker_bab + attacker_str + attacker_size + attacker_bonus
    defender_total = defender_roll + defender_bab + defender_str + defender_size + defender_bonus

    attacker_wins = attacker_total >= defender_total

    desc = (f"Opposed Attack: {attacker.name} ({attacker_total}) vs {defender.name} ({defender_total})")

    return attacker_wins, attacker_total, defender_total, desc


def melee_touch_attack(attacker, defender) -> Tuple[bool, int, int, str]:
    """
    Make a melee touch attack.
    Returns: (hit, attack_roll, touch_ac, description)
    """
    roll = random.randint(1, 20)

    bab = get_bab(attacker)
    str_mod = get_ability_mod(attacker, "Str")

    # Touch AC = 10 + size mod + Dex mod + deflection
    base_ac = 10
    dex_mod = get_ability_mod(defender, "Dex")
    size_mod = -get_size_modifier(defender)  # Negative because smaller = harder to hit
    touch_ac = base_ac + dex_mod + size_mod

    attack_total = roll + bab + str_mod

    # Natural 1 always misses, natural 20 always hits
    if roll == 1:
        hit = False
    elif roll == 20:
        hit = True
    else:
        hit = attack_total >= touch_ac

    desc = f"Touch Attack: d20({roll}) + {bab} + {str_mod} = {attack_total} vs Touch AC {touch_ac}"

    return hit, attack_total, touch_ac, desc


# =============================================================================
# Combat Maneuvers
# =============================================================================

def disarm(attacker, defender, attacker_bonus: int = 0) -> str:
    """
    Attempt to disarm an opponent.

    D&D 3.5 Rules:
    1. Melee touch attack to grab weapon
    2. Opposed attack roll (BAB + Str + size)
    3. If attacker wins by 10+, weapon flies 10 feet away
    4. Improved Disarm: +4 bonus, no AoO
    """
    results = []

    # Check for Improved Disarm (no AoO)
    has_improved = has_feat(attacker, "Improved Disarm")
    if has_improved:
        attacker_bonus += 4
    else:
        # Trigger AoO from defender
        aoo_result = trigger_aoo(defender, attacker, "disarm attempt")
        if aoo_result:
            results.append(aoo_result)

    # Step 1: Melee touch attack
    hit, attack_roll, touch_ac, touch_desc = melee_touch_attack(attacker, defender)
    results.append(touch_desc)

    if not hit:
        results.append(f"{attacker.name} fails to grab {defender.name}'s weapon!")
        return "\n".join(results)

    results.append(f"{attacker.name} grabs {defender.name}'s weapon!")

    # Step 2: Opposed attack roll
    # Two-handed weapon: +4 to defender
    # Light weapon: -4 to defender
    defender_bonus = 0  # Could add weapon size modifiers

    wins, atk_total, def_total, opposed_desc = opposed_attack_roll(
        attacker, defender, attacker_bonus, defender_bonus
    )
    results.append(opposed_desc)

    if wins:
        margin = atk_total - def_total
        if margin >= 10:
            results.append(f"{attacker.name} DISARMS {defender.name}! The weapon flies 10 feet away!")
        else:
            results.append(f"{attacker.name} DISARMS {defender.name}! The weapon falls at their feet.")

        # Apply disarmed effect
        if hasattr(defender, 'add_condition'):
            defender.add_condition('disarmed')
    else:
        results.append(f"{defender.name} holds onto their weapon!")
        # Defender can attempt to disarm attacker
        results.append(f"{defender.name} can now attempt to disarm {attacker.name}!")

    return "\n".join(results)


def trip(attacker, defender, attacker_bonus: int = 0) -> str:
    """
    Attempt to trip an opponent.

    D&D 3.5 Rules:
    1. Melee touch attack
    2. Opposed Str or Dex check (defender uses higher)
    3. Size modifier applies (x4)
    4. If defender wins, they can try to trip attacker
    5. Improved Trip: +4 bonus, no AoO, free attack on success
    """
    results = []

    has_improved = has_feat(attacker, "Improved Trip")
    if has_improved:
        attacker_bonus += 4
    else:
        aoo_result = trigger_aoo(defender, attacker, "trip attempt")
        if aoo_result:
            results.append(aoo_result)

    # Step 1: Melee touch attack
    hit, attack_roll, touch_ac, touch_desc = melee_touch_attack(attacker, defender)
    results.append(touch_desc)

    if not hit:
        results.append(f"{attacker.name} fails to grab {defender.name}!")
        return "\n".join(results)

    # Step 2: Opposed Str check (defender can use Dex if higher)
    attacker_str = get_ability_mod(attacker, "Str")
    defender_str = get_ability_mod(defender, "Str")
    defender_dex = get_ability_mod(defender, "Dex")

    # Defender uses higher of Str or Dex
    defender_mod = max(defender_str, defender_dex)
    defender_stat = "Str" if defender_str >= defender_dex else "Dex"

    # Size modifiers (x4 for trip)
    attacker_size = get_size_modifier(attacker) * 4
    defender_size = get_size_modifier(defender) * 4

    attacker_roll = random.randint(1, 20)
    defender_roll = random.randint(1, 20)

    attacker_total = attacker_roll + attacker_str + attacker_size + attacker_bonus
    defender_total = defender_roll + defender_mod + defender_size

    results.append(f"Trip: {attacker.name} ({attacker_total}) vs {defender.name} ({defender_total})")

    if attacker_total >= defender_total:
        results.append(f"{attacker.name} TRIPS {defender.name}! They fall prone!")

        if hasattr(defender, 'add_condition'):
            defender.add_condition('prone')

        # Improved Trip grants free attack
        if has_improved:
            results.append(f"{attacker.name} makes a free attack!")
            from src.combat import attack as combat_attack
            attack_result = combat_attack(attacker, defender)
            results.append(attack_result)
    else:
        results.append(f"{defender.name} resists the trip!")
        # Defender can try to trip attacker
        results.append(f"{defender.name} attempts to counter-trip {attacker.name}!")

        counter_roll = random.randint(1, 20)
        counter_total = counter_roll + defender_mod + defender_size

        if counter_total > attacker_total:
            results.append(f"{defender.name} COUNTER-TRIPS {attacker.name}!")
            if hasattr(attacker, 'add_condition'):
                attacker.add_condition('prone')
        else:
            results.append(f"{attacker.name} stays on their feet.")

    return "\n".join(results)


def bull_rush(attacker, defender, attacker_bonus: int = 0) -> str:
    """
    Attempt to push an opponent back.

    D&D 3.5 Rules:
    1. Move into defender's space (provokes AoO)
    2. Opposed Str check with size modifiers
    3. If attacker wins, push defender back 5 feet + 5 per 5 points margin
    4. Improved Bull Rush: +4 bonus, no AoO
    """
    results = []

    has_improved = has_feat(attacker, "Improved Bull Rush")
    if has_improved:
        attacker_bonus += 4
    else:
        aoo_result = trigger_aoo(defender, attacker, "bull rush")
        if aoo_result:
            results.append(aoo_result)

    # Opposed Str check with size modifiers
    wins, atk_total, def_total, desc = opposed_roll(
        attacker, defender, "Str", "Str",
        attacker_bonus, 0,
        attacker_size_matters=True,
        defender_size_matters=True
    )
    results.append(f"Bull Rush: {desc}")

    if wins:
        margin = atk_total - def_total
        distance = 5 + (margin // 5) * 5
        results.append(f"{attacker.name} BULL RUSHES {defender.name} back {distance} feet!")

        # Could implement actual position tracking here
        if hasattr(defender, 'add_condition'):
            defender.add_condition('pushed')
    else:
        results.append(f"{defender.name} holds their ground!")
        # Failed bull rush - attacker moves back
        results.append(f"{attacker.name} is pushed back 5 feet!")

    return "\n".join(results)


def grapple(attacker, defender, attacker_bonus: int = 0) -> str:
    """
    Attempt to grapple an opponent.

    D&D 3.5 Rules:
    1. Melee touch attack (provokes AoO)
    2. Opposed grapple check (BAB + Str mod + size mod)
    3. If attacker wins, both are grappled
    4. Improved Grapple: +4 bonus, no AoO
    """
    results = []

    has_improved = has_feat(attacker, "Improved Grapple")
    if has_improved:
        attacker_bonus += 4
    else:
        aoo_result = trigger_aoo(defender, attacker, "grapple attempt")
        if aoo_result:
            results.append(aoo_result)
            # Check if attacker was killed by AoO
            if hasattr(attacker, 'hp') and attacker.hp <= 0:
                results.append(f"{attacker.name} is killed before completing the grapple!")
                return "\n".join(results)

    # Step 1: Melee touch attack
    hit, attack_roll, touch_ac, touch_desc = melee_touch_attack(attacker, defender)
    results.append(touch_desc)

    if not hit:
        results.append(f"{attacker.name} fails to grab {defender.name}!")
        return "\n".join(results)

    # Step 2: Grapple check (BAB + Str + size)
    attacker_roll = random.randint(1, 20)
    defender_roll = random.randint(1, 20)

    attacker_grapple = (attacker_roll + get_bab(attacker) +
                        get_ability_mod(attacker, "Str") +
                        get_size_modifier(attacker) + attacker_bonus)
    defender_grapple = (defender_roll + get_bab(defender) +
                        get_ability_mod(defender, "Str") +
                        get_size_modifier(defender))

    results.append(f"Grapple: {attacker.name} ({attacker_grapple}) vs {defender.name} ({defender_grapple})")

    if attacker_grapple >= defender_grapple:
        results.append(f"{attacker.name} GRAPPLES {defender.name}!")

        # Both are now grappled
        if hasattr(attacker, 'add_condition'):
            attacker.add_condition('grappled')
        if hasattr(defender, 'add_condition'):
            defender.add_condition('grappled')
    else:
        results.append(f"{defender.name} escapes the grapple attempt!")

    return "\n".join(results)


def overrun(attacker, defender, attacker_bonus: int = 0) -> str:
    """
    Attempt to move through an opponent's space.

    D&D 3.5 Rules:
    1. Move into defender's space
    2. Defender can avoid (step aside) or block
    3. If block, opposed Str check with size modifiers
    4. If attacker wins, defender is prone and attacker continues
    5. If defender wins, attacker stops and may be knocked prone
    6. Improved Overrun: +4 bonus, defender can't avoid
    """
    results = []

    has_improved = has_feat(attacker, "Improved Overrun")
    if has_improved:
        attacker_bonus += 4
        results.append(f"{defender.name} cannot avoid the overrun!")
    else:
        # Defender can choose to avoid
        # For now, assume defender blocks (AI could choose)
        results.append(f"{defender.name} attempts to block!")

    # Opposed Str check with size modifiers
    wins, atk_total, def_total, desc = opposed_roll(
        attacker, defender, "Str", "Str",
        attacker_bonus, 0,
        attacker_size_matters=True,
        defender_size_matters=True
    )
    results.append(f"Overrun: {desc}")

    if wins:
        results.append(f"{attacker.name} OVERRUNS {defender.name}! They are knocked prone!")
        if hasattr(defender, 'add_condition'):
            defender.add_condition('prone')
    else:
        results.append(f"{defender.name} stops {attacker.name}'s advance!")
        # Check if attacker is knocked prone (defender wins by 5+)
        if def_total - atk_total >= 5:
            results.append(f"{attacker.name} is knocked prone!")
            if hasattr(attacker, 'add_condition'):
                attacker.add_condition('prone')

    return "\n".join(results)


def sunder(attacker, defender, attacker_bonus: int = 0) -> str:
    """
    Attempt to destroy an opponent's weapon or shield.

    D&D 3.5 Rules:
    1. Attack the item (provokes AoO)
    2. Opposed attack roll
    3. If attacker wins, deal damage to item
    4. Improved Sunder: +4 bonus, no AoO
    """
    results = []

    has_improved = has_feat(attacker, "Improved Sunder")
    if has_improved:
        attacker_bonus += 4
    else:
        aoo_result = trigger_aoo(defender, attacker, "sunder attempt")
        if aoo_result:
            results.append(aoo_result)

    # Opposed attack roll
    wins, atk_total, def_total, desc = opposed_attack_roll(
        attacker, defender, attacker_bonus, 0
    )
    results.append(f"Sunder: {desc}")

    if wins:
        # Calculate damage to weapon
        damage_dice = getattr(attacker, 'damage_dice', [1, 6, 0])
        damage = sum(random.randint(1, damage_dice[1]) for _ in range(damage_dice[0])) + damage_dice[2]
        str_mod = get_ability_mod(attacker, "Str")
        damage += str_mod

        results.append(f"{attacker.name} SUNDERS {defender.name}'s weapon for {damage} damage!")

        # Apply damage to weapon (if item HP tracking exists)
        # For now, just report damage
        results.append(f"The weapon takes {damage} points of damage!")
    else:
        results.append(f"{defender.name} protects their weapon!")

    return "\n".join(results)


def feint(attacker, defender, attacker_bonus: int = 0) -> str:
    """
    Attempt to feint in combat.

    D&D 3.5 Rules:
    1. Opposed Bluff vs Sense Motive
    2. If successful, defender loses Dex to AC for attacker's next attack
    3. Improved Feint: Use as move action instead of standard
    """
    results = []

    has_improved = has_feat(attacker, "Improved Feint")
    if has_improved:
        results.append(f"{attacker.name} feints as a move action!")

    # Get skill modifiers
    attacker_bluff = get_skill_ranks(attacker, "Bluff")
    defender_sense = get_skill_ranks(defender, "Sense Motive")

    # Add Cha mod to Bluff, Wis mod to Sense Motive
    attacker_cha = get_ability_mod(attacker, "Cha")
    defender_wis = get_ability_mod(defender, "Wis")

    attacker_roll = random.randint(1, 20)
    defender_roll = random.randint(1, 20)

    attacker_total = attacker_roll + attacker_bluff + attacker_cha + attacker_bonus
    defender_total = defender_roll + defender_sense + defender_wis

    results.append(f"Feint: {attacker.name} Bluff ({attacker_total}) vs {defender.name} Sense Motive ({defender_total})")

    if attacker_total >= defender_total:
        results.append(f"{attacker.name} FEINTS {defender.name}! They lose Dex to AC for the next attack!")

        # Apply feinted condition (loses Dex to AC)
        if hasattr(defender, 'add_condition'):
            defender.add_condition('flat_footed')
    else:
        results.append(f"{defender.name} sees through the feint!")

    return "\n".join(results)


def whirlwind_attack(attacker, targets: List[Any]) -> str:
    """
    Attack all adjacent enemies at once.

    D&D 3.5 Rules:
    - Full-round action
    - One attack at highest BAB against each adjacent enemy
    - Requires: Dex 13, Int 13, Combat Expertise, Dodge, Mobility, Spring Attack, BAB +4
    """
    results = []

    if not has_feat(attacker, "Whirlwind Attack"):
        return f"{attacker.name} does not have the Whirlwind Attack feat!"

    if not targets:
        return f"No targets for {attacker.name}'s Whirlwind Attack!"

    results.append(f"{attacker.name} spins, attacking all nearby enemies!")

    from src.combat import attack as combat_attack

    for target in targets:
        if target is not attacker and getattr(target, 'alive', True):
            if hasattr(target, 'hp') and target.hp > 0:
                result = combat_attack(attacker, target)
                results.append(f"  vs {target.name}: {result}")

    return "\n".join(results)


def spring_attack(attacker, target, move_before: int = 10, move_after: int = 10) -> str:
    """
    Move, attack, and continue moving.

    D&D 3.5 Rules:
    - Move up to your speed
    - Make a single attack at any point during movement
    - Continue movement after attack
    - Target doesn't get AoO for this attack
    - Other enemies can still get AoO for movement
    """
    results = []

    if not has_feat(attacker, "Spring Attack"):
        return f"{attacker.name} does not have the Spring Attack feat!"

    results.append(f"{attacker.name} dashes forward {move_before} feet!")

    # Attack (no AoO from target)
    from src.combat import attack as combat_attack
    attack_result = combat_attack(attacker, target)
    results.append(f"{attacker.name} strikes: {attack_result}")

    results.append(f"{attacker.name} continues moving {move_after} feet!")

    return "\n".join(results)


def stunning_fist(attacker, defender) -> str:
    """
    Attempt to stun an opponent with an unarmed strike.

    D&D 3.5 Rules:
    - Declare before attack roll
    - If attack hits, defender makes Fort save (DC 10 + 1/2 level + Wis mod)
    - Failure: Stunned for 1 round
    - Uses per day: 1 per 4 levels (minimum 1)
    """
    results = []

    if not has_feat(attacker, "Stunning Fist"):
        return f"{attacker.name} does not have the Stunning Fist feat!"

    results.append(f"{attacker.name} attempts a Stunning Fist!")

    # Make attack roll
    from src.combat import attack as combat_attack, calculate_attack_bonus, calculate_ac

    roll = random.randint(1, 20)
    attack_bonus = calculate_attack_bonus(attacker, defender)
    ac = calculate_ac(defender, attacker)

    if roll == 1:
        results.append(f"Attack: MISS (natural 1)")
        return "\n".join(results)

    if roll == 20 or roll + attack_bonus >= ac:
        # Hit - calculate damage
        damage_dice = getattr(attacker, 'damage_dice', [1, 6, 0])
        damage = sum(random.randint(1, damage_dice[1]) for _ in range(damage_dice[0])) + damage_dice[2]
        str_mod = get_ability_mod(attacker, "Str")
        damage = max(1, damage + str_mod)

        defender.hp = max(0, defender.hp - damage)
        results.append(f"Attack: HIT for {damage} damage!")

        # Fort save
        level = getattr(attacker, 'level', 1)
        wis_mod = get_ability_mod(attacker, "Wis")
        dc = 10 + (level // 2) + wis_mod

        from src.combat import roll_saving_throw, SaveType
        success, save_total, save_desc = roll_saving_throw(defender, SaveType.FORTITUDE, dc)
        results.append(save_desc)

        if not success:
            results.append(f"{defender.name} is STUNNED for 1 round!")
            if hasattr(defender, 'add_timed_condition'):
                defender.add_timed_condition('stunned', 1)
            elif hasattr(defender, 'add_condition'):
                defender.add_condition('stunned')
        else:
            results.append(f"{defender.name} resists the stunning blow!")

        # Check for death
        if defender.hp <= 0:
            if hasattr(defender, 'alive'):
                defender.alive = False
            results.append(f"{defender.name} is slain!")
    else:
        results.append(f"Attack: MISS ({roll}+{attack_bonus}={roll+attack_bonus} vs AC {ac})")

    return "\n".join(results)


# =============================================================================
# Grapple Actions (for ongoing grapples)
# =============================================================================

def grapple_action_damage(attacker, defender) -> str:
    """Deal unarmed or light weapon damage while grappling."""
    damage_dice = getattr(attacker, 'damage_dice', [1, 3, 0])
    damage = sum(random.randint(1, damage_dice[1]) for _ in range(damage_dice[0])) + damage_dice[2]
    str_mod = get_ability_mod(attacker, "Str")
    damage = max(1, damage + str_mod)

    defender.hp = max(0, defender.hp - damage)

    result = f"{attacker.name} deals {damage} damage to {defender.name} in the grapple!"
    if defender.hp <= 0:
        if hasattr(defender, 'alive'):
            defender.alive = False
        result += f" {defender.name} is slain!"

    return result


def grapple_action_pin(attacker, defender) -> str:
    """Attempt to pin a grappled opponent."""
    attacker_roll = random.randint(1, 20)
    defender_roll = random.randint(1, 20)

    attacker_grapple = (attacker_roll + get_bab(attacker) +
                        get_ability_mod(attacker, "Str") +
                        get_size_modifier(attacker))
    defender_grapple = (defender_roll + get_bab(defender) +
                        get_ability_mod(defender, "Str") +
                        get_size_modifier(defender))

    if attacker_grapple >= defender_grapple:
        if hasattr(defender, 'add_condition'):
            defender.add_condition('pinned')
        return f"{attacker.name} PINS {defender.name}!"
    else:
        return f"{defender.name} resists being pinned!"


def grapple_action_escape(attacker, defender) -> str:
    """Attempt to escape a grapple."""
    # Can use grapple check OR Escape Artist check
    attacker_roll = random.randint(1, 20)
    defender_roll = random.randint(1, 20)

    # Try grapple check
    attacker_grapple = (attacker_roll + get_bab(attacker) +
                        get_ability_mod(attacker, "Str") +
                        get_size_modifier(attacker))
    defender_grapple = (defender_roll + get_bab(defender) +
                        get_ability_mod(defender, "Str") +
                        get_size_modifier(defender))

    if attacker_grapple >= defender_grapple:
        if hasattr(attacker, 'remove_condition'):
            attacker.remove_condition('grappled')
        if hasattr(defender, 'remove_condition'):
            defender.remove_condition('grappled')
        return f"{attacker.name} ESCAPES the grapple!"
    else:
        return f"{attacker.name} fails to escape!"
