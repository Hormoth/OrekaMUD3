"""
D&D 3.5 Edition Combat System for OrekaMUD3

This module implements a real-time adapted combat system based on D&D 3.5 rules:
- Initiative system with d20 + Dex mod + feats
- Action economy (standard, move, swift, free, full-round)
- Saving throws (Fortitude, Reflex, Will)
- Attacks of opportunity
- Flanking bonuses
- Combat rounds (6-second ticks adapted for MUD play)
"""

import random
import asyncio
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING

from src import conditions as cond
from src import feats as feat_module
from src import quests as quest_module

if TYPE_CHECKING:
    from src.character import Character
    from src.mob import Mob
    from src.room import Room


class ActionType(Enum):
    """D&D 3.5 action types"""
    STANDARD = "standard"      # Attack, cast spell, use ability
    MOVE = "move"              # Move, draw weapon, stand up
    SWIFT = "swift"            # Quick abilities
    FREE = "free"              # Speaking, drop item
    FULL_ROUND = "full_round"  # Full attack, charge, run
    IMMEDIATE = "immediate"    # Reaction (uses swift action)


class SaveType(Enum):
    """D&D 3.5 saving throw types"""
    FORTITUDE = "Fort"
    REFLEX = "Ref"
    WILL = "Will"


class CombatantState:
    """Tracks a single combatant's state within a combat instance"""

    def __init__(self, combatant, initiative_roll: int):
        self.combatant = combatant
        self.initiative_roll = initiative_roll
        self.actions_used = {
            ActionType.STANDARD: False,
            ActionType.MOVE: False,
            ActionType.SWIFT: False,
        }
        self.free_actions_taken = 0
        self.aoo_taken = 0
        self.has_acted_this_round = False
        self.is_flat_footed = True  # Until first action
        self.position = 0  # Abstract position for flanking

    def reset_actions(self):
        """Reset actions at start of new round"""
        self.actions_used = {
            ActionType.STANDARD: False,
            ActionType.MOVE: False,
            ActionType.SWIFT: False,
        }
        self.free_actions_taken = 0
        self.aoo_taken = 0
        self.has_acted_this_round = False

    def can_take_action(self, action_type: ActionType) -> bool:
        """Check if combatant can take specified action type"""
        if action_type == ActionType.FREE:
            return self.free_actions_taken < 5  # Reasonable limit
        if action_type == ActionType.FULL_ROUND:
            return not self.actions_used[ActionType.STANDARD] and not self.actions_used[ActionType.MOVE]
        if action_type == ActionType.IMMEDIATE:
            return not self.actions_used[ActionType.SWIFT]
        return not self.actions_used.get(action_type, True)

    def use_action(self, action_type: ActionType):
        """Mark an action type as used"""
        if action_type == ActionType.FREE:
            self.free_actions_taken += 1
        elif action_type == ActionType.FULL_ROUND:
            self.actions_used[ActionType.STANDARD] = True
            self.actions_used[ActionType.MOVE] = True
        elif action_type == ActionType.IMMEDIATE:
            self.actions_used[ActionType.SWIFT] = True
        else:
            self.actions_used[action_type] = True
        self.has_acted_this_round = True
        self.is_flat_footed = False

    def get_max_aoo(self) -> int:
        """Get maximum attacks of opportunity per round"""
        # Use feat module to calculate AoO count (Combat Reflexes, etc.)
        return feat_module.get_aoo_count(self.combatant)

    def can_take_aoo(self) -> bool:
        """Check if combatant can take an attack of opportunity"""
        return self.aoo_taken < self.get_max_aoo()


class CombatInstance:
    """
    Manages a combat encounter in a room.
    Tracks initiative order, rounds, and combat state.
    """

    ROUND_DURATION = 6  # seconds in D&D

    def __init__(self, room: 'Room'):
        self.room = room
        self.combatants: Dict[Any, CombatantState] = {}  # entity -> CombatantState
        self.initiative_order: List[CombatantState] = []
        self.round_number = 0
        self.current_turn_index = 0
        self.is_active = False
        self.combat_log: List[str] = []

    def add_combatant(self, entity) -> int:
        """Add a combatant and roll initiative. Returns initiative roll."""
        if entity in self.combatants:
            return self.combatants[entity].initiative_roll

        init_roll = roll_initiative(entity)
        state = CombatantState(entity, init_roll)
        self.combatants[entity] = state

        # Insert in initiative order
        self.initiative_order.append(state)
        self.initiative_order.sort(key=lambda x: (-x.initiative_roll, -get_ability_mod(x.combatant, "Dex")))

        # Set combat state on entity
        if hasattr(entity, 'state'):
            from src.character import State
            entity.state = State.COMBAT

        return init_roll

    def remove_combatant(self, entity):
        """Remove a combatant from combat"""
        if entity in self.combatants:
            state = self.combatants[entity]
            self.initiative_order.remove(state)
            del self.combatants[entity]

            # Reset combat state on entity
            if hasattr(entity, 'state'):
                from src.character import State
                entity.state = State.EXPLORING

    def start_combat(self) -> str:
        """Initialize combat and roll initiative for all combatants"""
        self.is_active = True
        self.round_number = 1
        self.current_turn_index = 0

        # Reset all combatants
        for state in self.combatants.values():
            state.reset_actions()
            state.is_flat_footed = True

        # Build initiative message
        lines = ["\n=== COMBAT BEGINS ===", f"Round {self.round_number}", "Initiative Order:"]
        for i, state in enumerate(self.initiative_order):
            marker = ">>>" if i == 0 else "   "
            lines.append(f"  {marker} {state.combatant.name}: {state.initiative_roll}")
        lines.append("")

        self.combat_log.append("\n".join(lines))
        return "\n".join(lines)

    def get_current_combatant(self) -> Optional[CombatantState]:
        """Get the combatant whose turn it is"""
        if not self.initiative_order:
            return None
        return self.initiative_order[self.current_turn_index % len(self.initiative_order)]

    def advance_turn(self) -> str:
        """Advance to next combatant's turn"""
        self.current_turn_index += 1

        # Check for new round
        if self.current_turn_index >= len(self.initiative_order):
            return self.new_round()

        current = self.get_current_combatant()
        if current:
            current.reset_actions()
            return f"\n{current.combatant.name}'s turn."
        return ""

    def new_round(self) -> str:
        """Start a new combat round"""
        self.round_number += 1
        self.current_turn_index = 0

        # Reset all combatants' actions
        for state in self.combatants.values():
            state.reset_actions()
            # Reset AoO tracking
            if hasattr(state.combatant, 'reset_aoo'):
                state.combatant.reset_aoo()

        # Tick conditions with durations
        condition_msgs = []
        for state in self.combatants.values():
            if hasattr(state.combatant, 'tick_conditions'):
                expired = state.combatant.tick_conditions()
                if expired:
                    condition_msgs.append(f"{state.combatant.name}: {', '.join(expired)} expired")

        current = self.get_current_combatant()
        msg = f"\n=== Round {self.round_number} ==="
        if condition_msgs:
            msg += "\n" + "\n".join(condition_msgs)
        if current:
            msg += f"\n{current.combatant.name}'s turn."
        return msg

    def check_combat_end(self) -> Tuple[bool, str]:
        """Check if combat should end. Returns (should_end, message)"""
        # Separate combatants into teams (players vs mobs)
        players = [s for s in self.initiative_order if hasattr(s.combatant, 'xp')]
        mobs = [s for s in self.initiative_order if not hasattr(s.combatant, 'xp')]

        # Filter to alive only
        alive_players = [s for s in players if getattr(s.combatant, 'hp', 0) > 0]
        alive_mobs = [s for s in mobs if getattr(s.combatant, 'alive', False) and getattr(s.combatant, 'hp', 0) > 0]

        if not alive_mobs:
            return True, "\n=== VICTORY! All enemies defeated! ==="
        if not alive_players:
            return True, "\n=== DEFEAT! All players have fallen! ==="

        return False, ""

    def end_combat(self):
        """End the combat encounter"""
        self.is_active = False
        for entity in list(self.combatants.keys()):
            if hasattr(entity, 'state'):
                from src.character import State
                entity.state = State.EXPLORING
        self.combatants.clear()
        self.initiative_order.clear()

    def is_flanking(self, attacker, defender) -> bool:
        """
        Check if attacker is flanking defender.
        In MUD adaptation: flanking if 2+ allies are attacking same target.
        """
        if not self.combatants:
            return False

        # Count allies also in combat with defender
        allies_attacking = 0
        for state in self.initiative_order:
            entity = state.combatant
            if entity is not attacker and entity is not defender:
                # Check if this entity is hostile to defender and friendly to attacker
                attacker_is_player = hasattr(attacker, 'xp')
                entity_is_player = hasattr(entity, 'xp')
                defender_is_player = hasattr(defender, 'xp')

                # Same team as attacker, different team from defender
                if attacker_is_player == entity_is_player and attacker_is_player != defender_is_player:
                    if getattr(entity, 'hp', 0) > 0 and getattr(entity, 'alive', True):
                        allies_attacking += 1

        return allies_attacking >= 1  # At least 2 total (attacker + 1 ally)


# Global combat instances by room
_active_combats: Dict[int, CombatInstance] = {}


def get_combat(room: 'Room') -> Optional[CombatInstance]:
    """Get active combat instance for a room"""
    return _active_combats.get(room.vnum)


def start_combat(room: 'Room', initiator, target) -> CombatInstance:
    """Start a new combat in a room or join existing combat"""
    combat = _active_combats.get(room.vnum)

    if not combat:
        combat = CombatInstance(room)
        _active_combats[room.vnum] = combat

    combat.add_combatant(initiator)
    combat.add_combatant(target)

    if not combat.is_active:
        combat.start_combat()

    return combat


def end_combat(room: 'Room'):
    """End combat in a room"""
    if room.vnum in _active_combats:
        _active_combats[room.vnum].end_combat()
        del _active_combats[room.vnum]


# =============================================================================
# Core Combat Functions
# =============================================================================

def get_ability_mod(entity, ability: str) -> int:
    """Get ability modifier for an entity"""
    if hasattr(entity, 'ability_scores'):
        score = entity.ability_scores.get(ability, 10)
    elif hasattr(entity, f'{ability.lower()}_score'):
        score = getattr(entity, f'{ability.lower()}_score', 10)
    else:
        score = 10
    return (score - 10) // 2


def roll_initiative(entity) -> int:
    """Roll initiative for an entity: d20 + Dex mod + bonuses"""
    roll = random.randint(1, 20)
    dex_mod = get_ability_mod(entity, "Dex")

    # Check for initiative bonuses
    bonus = 0
    if hasattr(entity, 'get_initiative'):
        # Mob method includes Improved Initiative
        return entity.get_initiative() + roll

    # Apply feat bonuses (Improved Initiative, etc.)
    feat_bonus = feat_module.get_initiative_feat_bonus(entity)
    bonus += feat_bonus

    # Apply condition penalties (e.g., deafened gives -4 initiative)
    condition_penalty = 0
    if hasattr(entity, 'get_condition_modifier'):
        condition_penalty = entity.get_condition_modifier('initiative_penalty')
    else:
        condition_penalty = cond.calculate_condition_modifiers(entity, 'initiative_penalty')

    return roll + dex_mod + bonus - condition_penalty


def roll_saving_throw(entity, save_type: SaveType, dc: int, modifiers: int = 0) -> Tuple[bool, int, str]:
    """
    Roll a saving throw.
    Returns (success, roll_total, description)
    """
    roll = random.randint(1, 20)

    # Get base save
    if hasattr(entity, 'get_save'):
        base_save = entity.get_save(save_type.value)
    elif hasattr(entity, 'saves'):
        base_save = entity.saves.get(save_type.value, 0)
    else:
        base_save = 0

    # Add ability modifier
    ability_map = {
        SaveType.FORTITUDE: "Con",
        SaveType.REFLEX: "Dex",
        SaveType.WILL: "Wis"
    }
    ability_mod = get_ability_mod(entity, ability_map[save_type])

    # Apply feat bonuses (Iron Will, Lightning Reflexes, Great Fortitude, etc.)
    feat_bonus = feat_module.get_save_feat_bonus(entity, save_type.value)

    # Get condition penalties using centralized conditions system
    condition_penalty = 0
    if hasattr(entity, 'get_condition_modifier'):
        condition_penalty = -entity.get_condition_modifier('save_penalty')
    else:
        condition_penalty = -cond.calculate_condition_modifiers(entity, 'save_penalty')

    total = roll + base_save + ability_mod + modifiers + condition_penalty + feat_bonus
    success = total >= dc

    result = "SUCCESS" if success else "FAILURE"
    desc = f"{entity.name} {save_type.value} save: d20({roll}) + {base_save} + {ability_mod} = {total} vs DC {dc} - {result}"

    return success, total, desc


def calculate_attack_bonus(attacker, target=None, is_aoo: bool = False) -> int:
    """Calculate total attack bonus"""
    # Base attack bonus
    if hasattr(attacker, 'level'):
        level = attacker.level
    else:
        level = 1

    # Determine BAB based on class or monster
    if hasattr(attacker, 'char_class'):
        from src.classes import CLASSES
        class_data = CLASSES.get(attacker.char_class, {})
        bab_type = class_data.get('bab', 'medium')
        if bab_type == 'full':
            bab = level
        elif bab_type == 'medium':
            bab = (level * 3) // 4
        else:  # poor
            bab = level // 2
    else:
        bab = (level * 3) // 4  # Default for monsters

    # Strength modifier (or Dex with Weapon Finesse)
    str_mod = get_ability_mod(attacker, "Str")
    dex_mod = get_ability_mod(attacker, "Dex")

    use_dex = False
    if hasattr(attacker, 'has_feat') and attacker.has_feat("Weapon Finesse"):
        if hasattr(attacker, '_is_finesse_weapon') and attacker._is_finesse_weapon():
            use_dex = True

    stat_mod = dex_mod if use_dex else str_mod

    # Power Attack penalty
    power_attack_penalty = getattr(attacker, 'power_attack_amt', 0)

    # Feat bonuses (Weapon Focus, Greater Weapon Focus, etc.)
    feat_bonus = feat_module.get_attack_feat_bonus(attacker, target)

    # Condition penalties using centralized conditions system
    condition_penalty = 0
    if hasattr(attacker, 'get_condition_modifier'):
        condition_penalty = -attacker.get_condition_modifier('attack_penalty')
        # Also check for melee-specific penalties (prone)
        condition_penalty -= attacker.get_condition_modifier('melee_attack_penalty')
    else:
        condition_penalty = -cond.calculate_condition_modifiers(attacker, 'attack_penalty')
        condition_penalty -= cond.calculate_condition_modifiers(attacker, 'melee_attack_penalty')

    # Condition bonuses (e.g., invisible gives +2 attack)
    condition_bonus = 0
    if hasattr(attacker, 'get_condition_modifier'):
        condition_bonus = attacker.get_condition_modifier('attack_bonus')
    else:
        condition_bonus = cond.calculate_condition_modifiers(attacker, 'attack_bonus')

    # Flanking bonus
    flanking_bonus = 0
    if target:
        room = getattr(attacker, 'room', None)
        if room:
            combat = get_combat(room)
            if combat and combat.is_flanking(attacker, target):
                flanking_bonus = 2

    return bab + stat_mod - power_attack_penalty + feat_bonus + condition_penalty + condition_bonus + flanking_bonus


def calculate_damage(attacker, is_crit: bool = False) -> int:
    """Calculate damage for an attack"""
    # Get damage dice
    if hasattr(attacker, 'damage_dice'):
        dice = attacker.damage_dice
        num_dice, die_size, bonus = dice[0], dice[1], dice[2] if len(dice) > 2 else 0
    else:
        # Default 1d4
        num_dice, die_size, bonus = 1, 4, 0

    # Roll damage
    damage = sum(random.randint(1, die_size) for _ in range(num_dice)) + bonus

    # Strength modifier to damage
    str_mod = get_ability_mod(attacker, "Str")
    damage += str_mod

    # Power Attack bonus
    power_attack_bonus = getattr(attacker, 'power_attack_amt', 0)
    damage += power_attack_bonus

    # Feat damage bonuses (Weapon Specialization, Greater Weapon Specialization, etc.)
    feat_damage = feat_module.get_damage_feat_bonus(attacker)
    damage += feat_damage

    # Condition damage penalties (e.g., sickened gives -2 damage)
    condition_penalty = 0
    if hasattr(attacker, 'get_condition_modifier'):
        condition_penalty = attacker.get_condition_modifier('damage_penalty')
    else:
        condition_penalty = cond.calculate_condition_modifiers(attacker, 'damage_penalty')
    damage -= condition_penalty

    # Critical hit multiplier (simplified: x2)
    if is_crit:
        damage *= 2

    return max(1, damage)  # Minimum 1 damage


def calculate_ac(defender, attacker=None, is_touch: bool = False, is_flat_footed: bool = False) -> int:
    """Calculate defender's AC against an attack"""
    base_ac = 10

    # Get armor bonus (not for touch attacks)
    armor_bonus = 0
    if not is_touch and hasattr(defender, 'ac'):
        armor_bonus = defender.ac - 10  # Assume ac includes armor

    # Dexterity modifier (not if flat-footed unless has Uncanny Dodge)
    dex_mod = get_ability_mod(defender, "Dex")

    # Check if loses Dex to AC from conditions (stunned, blinded, cowering, etc.)
    loses_dex = is_flat_footed
    if hasattr(defender, 'loses_dex_to_ac') and defender.loses_dex_to_ac():
        loses_dex = True
    elif cond.has_effect(defender, 'loses_dex_to_ac'):
        loses_dex = True

    # Check for helpless (Dex score of 0)
    if cond.has_effect(defender, 'dex_score'):
        dex_score_override = None
        for cond_name in getattr(defender, 'conditions', set()) | set(getattr(defender, 'active_conditions', {}).keys()):
            condition = cond.get_condition(cond_name)
            if condition and 'dex_score' in condition.effects:
                dex_score_override = condition.effects['dex_score']
                break
        if dex_score_override is not None:
            dex_mod = (dex_score_override - 10) // 2  # 0 gives -5

    if loses_dex:
        if hasattr(defender, 'has_feat') and defender.has_feat("Uncanny Dodge"):
            pass  # Keep Dex bonus
        else:
            dex_mod = 0

    # Dodge bonus (requires awareness of attacker)
    dodge_bonus = 0
    if attacker and hasattr(defender, 'get_ac'):
        # Use the entity's AC calculation if available
        return defender.get_ac(attacker=attacker)

    # Feat AC bonuses (Dodge, etc.) - only if not flat-footed
    feat_ac_bonus = 0
    if not loses_dex:
        feat_ac_bonus = feat_module.get_ac_feat_bonus(defender, attacker)

    # Condition AC penalties using centralized conditions system
    condition_penalty = 0
    if hasattr(defender, 'get_condition_modifier'):
        condition_penalty = defender.get_condition_modifier('ac_penalty')
        # Also check for melee-specific penalties (prone gives -4 vs melee)
        condition_penalty += defender.get_condition_modifier('melee_ac_penalty')
    else:
        condition_penalty = cond.calculate_condition_modifiers(defender, 'ac_penalty')
        condition_penalty += cond.calculate_condition_modifiers(defender, 'melee_ac_penalty')

    # Check for bonus against melee attackers when helpless
    melee_bonus_against = 0
    if cond.has_effect(defender, 'melee_attack_bonus_against'):
        # Attackers get bonus, so we subtract from defender's AC
        melee_bonus_against = cond.calculate_condition_modifiers(defender, 'melee_attack_bonus_against')

    return base_ac + armor_bonus + max(0, dex_mod) + dodge_bonus + feat_ac_bonus - condition_penalty - melee_bonus_against


def trigger_aoo(defender, attacker, reason: str) -> Optional[str]:
    """
    Trigger attack of opportunity from defender against attacker.
    Returns attack result string or None if no AoO available.
    """
    # Check if defender can take AoO
    room = getattr(defender, 'room', None)
    if not room:
        return None

    combat = get_combat(room)
    if not combat:
        return None

    defender_state = combat.combatants.get(defender)
    if not defender_state or not defender_state.can_take_aoo():
        return None

    # Check if defender is capable of attacking
    if hasattr(defender, 'hp') and defender.hp <= 0:
        return None
    if hasattr(defender, 'alive') and not defender.alive:
        return None

    # Use centralized conditions system to check if defender can act
    if hasattr(defender, 'can_act') and not defender.can_act():
        return None
    elif cond.has_effect(defender, 'cannot_act'):
        return None

    # Check for feats that prevent AoO
    if hasattr(attacker, 'has_feat'):
        # Mobility gives +4 AC vs AoO from movement
        if reason == "movement" and attacker.has_feat("Mobility"):
            # Still triggers, but attacker gets +4 AC
            pass

    # Make the attack
    defender_state.aoo_taken += 1

    # Calculate attack
    roll = random.randint(1, 20)
    attack_bonus = calculate_attack_bonus(defender, attacker)

    # Mobility bonus for movement AoO
    ac_bonus = 0
    if reason == "movement" and hasattr(attacker, 'has_feat') and attacker.has_feat("Mobility"):
        ac_bonus = 4

    ac = calculate_ac(attacker, defender) + ac_bonus

    # Natural 1 always misses, natural 20 always hits
    if roll == 1:
        return f"[AoO] {defender.name} swings at {attacker.name} ({reason}) - MISS (natural 1)"

    is_crit = roll == 20
    if is_crit or roll + attack_bonus >= ac:
        damage = calculate_damage(defender, is_crit)
        attacker.hp = max(0, attacker.hp - damage)

        crit_msg = " CRITICAL HIT!" if is_crit else ""
        result = f"[AoO] {defender.name} strikes {attacker.name} ({reason}) for {damage} damage!{crit_msg}"

        if attacker.hp <= 0:
            if hasattr(attacker, 'alive'):
                attacker.alive = False
            result += f" {attacker.name} falls!"

        return result

    return f"[AoO] {defender.name} swings at {attacker.name} ({reason}) - MISS ({roll}+{attack_bonus}={roll+attack_bonus} vs AC {ac})"


# =============================================================================
# Main Attack Function
# =============================================================================

def attack(attacker, target, power_attack_amt: int = 0, is_full_attack: bool = False) -> str:
    """
    Execute an attack against a target.

    Args:
        attacker: The attacking entity
        target: The target entity
        power_attack_amt: Amount to trade from attack for damage (Power Attack feat)
        is_full_attack: If True, make all iterative attacks

    Returns:
        String describing the attack result
    """
    results = []

    # Check if attacker can act based on conditions
    if hasattr(attacker, 'can_act') and not attacker.can_act():
        return f"{attacker.name} cannot act!"
    elif cond.has_effect(attacker, 'cannot_act'):
        return f"{attacker.name} cannot act!"

    # Check if attacker can attack (nauseated prevents attacks)
    if cond.has_effect(attacker, 'cannot_attack'):
        return f"{attacker.name} cannot attack!"

    # Set power attack amount
    if hasattr(attacker, 'set_power_attack'):
        attacker.set_power_attack(power_attack_amt)
    else:
        attacker.power_attack_amt = power_attack_amt

    # Get or start combat
    room = getattr(attacker, 'room', None) or getattr(target, 'room', None)
    if room:
        combat = get_combat(room)
        if not combat:
            combat = start_combat(room, attacker, target)
            results.append(combat.combat_log[-1] if combat.combat_log else "")
    else:
        combat = None

    # Check for flat-footed (first round, hasn't acted)
    is_flat_footed = False
    if combat:
        target_state = combat.combatants.get(target)
        if target_state and target_state.is_flat_footed:
            is_flat_footed = True

    # Check for flanking (for Sneak Attack)
    is_flanking = False
    if combat:
        is_flanking = combat.is_flanking(attacker, target)

    # Determine number of attacks
    num_attacks = 1
    if is_full_attack:
        # Calculate iterative attacks based on BAB
        bab = calculate_attack_bonus(attacker, target)
        num_attacks = max(1, (bab + 5) // 5)  # +6/+1 = 2 attacks, +11/+6/+1 = 3, etc.

    all_targets = list(room.mobs) + list(room.players) if room else [target]

    for attack_num in range(num_attacks):
        # Iterative attack penalty
        iterative_penalty = -5 * attack_num

        # Roll attack
        roll = random.randint(1, 20)
        attack_bonus = calculate_attack_bonus(attacker, target) + iterative_penalty
        ac = calculate_ac(target, attacker, is_flat_footed=is_flat_footed)

        # Natural 1 always misses
        if roll == 1:
            results.append(f"{attacker.name} attacks {target.name} - MISS (natural 1)")
            continue

        # Check for critical threat (natural 20)
        is_crit = False
        if roll == 20:
            # Confirm critical
            confirm_roll = random.randint(1, 20)
            if confirm_roll + attack_bonus >= ac:
                is_crit = True

        # Check hit
        if roll == 20 or roll + attack_bonus >= ac:
            damage = calculate_damage(attacker, is_crit)

            # Sneak Attack damage (Rogue)
            sneak_damage = 0
            if (is_flat_footed or is_flanking) and hasattr(attacker, 'char_class'):
                if attacker.char_class == "Rogue":
                    sneak_dice = (attacker.level + 1) // 2  # 1d6 per 2 levels
                    sneak_damage = sum(random.randint(1, 6) for _ in range(sneak_dice))
                    damage += sneak_damage

            target.hp = max(0, target.hp - damage)

            crit_msg = " CRITICAL HIT!" if is_crit else ""
            sneak_msg = f" (+{sneak_damage} sneak attack)" if sneak_damage else ""
            hit_msg = f"{attacker.name} hits {target.name} for {damage} damage!{crit_msg}{sneak_msg}"

            # Check for death
            if target.hp <= 0:
                if hasattr(target, 'alive'):
                    target.alive = False

                # Award XP
                xp_award = award_xp(attacker, target)
                loot_msg = generate_loot(target, room)

                hit_msg = f"{attacker.name} defeats {target.name}!"
                if xp_award:
                    hit_msg += f" (+{xp_award} XP)"
                if loot_msg:
                    hit_msg += f"\n{loot_msg}"

                # Quest trigger for mob kills
                if hasattr(attacker, 'quest_log'):
                    mob_type = getattr(target, 'mob_type', target.name.lower())
                    quest_updates = quest_module.on_mob_killed(attacker, mob_type)
                    for update in quest_updates:
                        hit_msg += f"\n[Quest] {update}"

                # Cleave feat
                if hasattr(attacker, 'has_feat') and attacker.has_feat("Cleave"):
                    cleave_target = find_cleave_target(attacker, target, all_targets)
                    if cleave_target:
                        hit_msg += f"\n{attacker.name} cleaves into {cleave_target.name}!"
                        cleave_result = attack(attacker, cleave_target, power_attack_amt)
                        hit_msg += f"\n{cleave_result}"

                        # Great Cleave: continue if kill
                        if hasattr(attacker, 'has_feat') and attacker.has_feat("Great Cleave"):
                            if cleave_target.hp <= 0:
                                next_target = find_cleave_target(attacker, cleave_target, all_targets)
                                if next_target:
                                    hit_msg += f"\n{attacker.name} continues cleaving into {next_target.name}!"
                                    hit_msg += f"\n{attack(attacker, next_target, power_attack_amt)}"

            results.append(hit_msg)

            # Check combat end
            if combat:
                ended, end_msg = combat.check_combat_end()
                if ended:
                    results.append(end_msg)
                    end_combat(room)
        else:
            results.append(f"{attacker.name} attacks {target.name} - MISS ({roll}+{attack_bonus}={roll+attack_bonus} vs AC {ac})")

    return "\n".join(results)


def find_cleave_target(attacker, killed_target, all_targets) -> Optional[Any]:
    """Find a valid target for Cleave"""
    for t in all_targets:
        if t is not killed_target and t is not attacker:
            if hasattr(t, 'alive') and t.alive and hasattr(t, 'hp') and t.hp > 0:
                # Check if hostile (player vs mob)
                attacker_is_player = hasattr(attacker, 'xp')
                target_is_player = hasattr(t, 'xp')
                if attacker_is_player != target_is_player:
                    return t
    return None


def award_xp(attacker, target) -> int:
    """Award XP for defeating a target"""
    if not hasattr(attacker, 'xp'):
        return 0

    cr = getattr(target, 'cr', None)
    if cr is None:
        return 0

    try:
        cr_val = float(cr)
    except:
        return 0

    level = getattr(attacker, 'level', 1)

    # D&D 3.5 XP table (single character)
    xp_table = {
        -4: 75, -3: 100, -2: 150, -1: 200, 0: 300,
        1: 450, 2: 600, 3: 900, 4: 1200
    }

    diff = int(round(cr_val - level))
    diff = max(-4, min(4, diff))

    xp_award = xp_table.get(diff, 0)
    attacker.xp += xp_award

    if hasattr(attacker, 'save'):
        attacker.save()

    return xp_award


def generate_loot(target, room) -> str:
    """Generate loot from a defeated target"""
    cr = getattr(target, 'cr', None)
    if cr is None:
        return ""

    try:
        cr_val = float(cr)
    except:
        return ""

    # Loot table by CR
    loot_table = [
        (0, 1, (1, 6, 0), 0.05, 'mundane'),
        (2, 4, (2, 8, 0), 0.10, 'mundane'),
        (5, 10, (4, 10, 0), 0.20, 'minor_magic'),
        (11, 16, (8, 10, 0), 0.30, 'medium_magic'),
        (17, 100, (12, 10, 0), 0.50, 'major_magic'),
    ]

    loot_msgs = []

    for min_cr, max_cr, gold_dice, item_chance, item_type in loot_table:
        if min_cr <= cr_val <= max_cr:
            # Gold drop
            gold = sum(random.randint(1, gold_dice[1]) for _ in range(gold_dice[0])) + gold_dice[2]
            loot_msgs.append(f"Loot: {gold} gp")

            # Item drop
            if random.random() < item_chance:
                try:
                    from src import items as itemdb
                    if item_type == 'mundane':
                        item = itemdb.get_random_item(magical=False)
                    else:
                        item = itemdb.get_random_item(magical=True)
                    if item and room:
                        room.items.append(item)
                        loot_msgs.append(f"{item.name} drops to the ground!")
                except:
                    pass
            break

    return " ".join(loot_msgs)


# =============================================================================
# Spell-Related Combat Functions
# =============================================================================

def spell_attack(caster, target, spell_data: dict) -> str:
    """
    Execute a spell attack.

    Args:
        caster: The spellcasting entity
        target: The target entity
        spell_data: Dictionary with spell properties

    Returns:
        String describing the spell result
    """
    # Check if caster can act
    if hasattr(caster, 'can_act') and not caster.can_act():
        return f"{caster.name} cannot act!"
    elif cond.has_effect(caster, 'cannot_act'):
        return f"{caster.name} cannot act!"

    # Check if caster can cast spells (nauseated, silenced, etc.)
    if hasattr(caster, 'can_cast') and not caster.can_cast():
        return f"{caster.name} cannot cast spells!"
    elif cond.has_effect(caster, 'cannot_cast'):
        return f"{caster.name} cannot cast spells!"

    # Check for spell components
    spell_components = spell_data.get('components', '')

    # Check verbal component (silenced, gagged)
    if 'V' in spell_components:
        if cond.has_effect(caster, 'cannot_verbal_component') or cond.has_effect(caster, 'cannot_speak'):
            return f"{caster.name} cannot speak to cast {spell_data.get('name', 'the spell')}!"

    # Check somatic component (bound, paralyzed)
    if 'S' in spell_components:
        if cond.has_effect(caster, 'cannot_somatic_component') or cond.has_effect(caster, 'cannot_move_hands'):
            return f"{caster.name} cannot perform somatic components!"

    spell_name = spell_data.get('name', 'Unknown Spell')

    # Check if spell requires attack roll (ray spells, touch spells)
    requires_attack = spell_data.get('requires_attack', False)
    is_touch = spell_data.get('is_touch', False)

    # Check saving throw
    save_type_str = spell_data.get('saving_throw', 'none')
    save_type = None
    if 'Reflex' in save_type_str:
        save_type = SaveType.REFLEX
    elif 'Will' in save_type_str:
        save_type = SaveType.WILL
    elif 'Fortitude' in save_type_str or 'Fort' in save_type_str:
        save_type = SaveType.FORTITUDE

    # Calculate spell DC
    spell_level = 1
    if 'level' in spell_data:
        for cls, lvl in spell_data['level'].items():
            if hasattr(caster, 'char_class') and caster.char_class == cls:
                spell_level = lvl
                break

    # DC = 10 + spell level + casting stat modifier
    if hasattr(caster, 'char_class'):
        casting_stat_map = {
            'Wizard': 'Int', 'Sorcerer': 'Cha', 'Bard': 'Cha',
            'Cleric': 'Wis', 'Druid': 'Wis', 'Paladin': 'Wis', 'Ranger': 'Wis'
        }
        casting_stat = casting_stat_map.get(caster.char_class, 'Int')
    else:
        casting_stat = 'Int'

    stat_mod = get_ability_mod(caster, casting_stat)
    dc = 10 + spell_level + stat_mod

    results = []

    # Attack roll if needed
    if requires_attack:
        roll = random.randint(1, 20)
        attack_bonus = calculate_attack_bonus(caster, target)
        ac = calculate_ac(target, caster, is_touch=is_touch)

        if roll == 1:
            return f"{caster.name} casts {spell_name} at {target.name} - MISS (natural 1)"
        if roll != 20 and roll + attack_bonus < ac:
            return f"{caster.name} casts {spell_name} at {target.name} - MISS"

    # Apply spell effect
    damage = 0
    if 'damage' in spell_data:
        damage_str = spell_data['damage']
        # Parse damage like "1d4+1 per level" or "5d6"
        damage = calculate_spell_damage(caster, damage_str)

    # Saving throw for half damage
    half_on_save = 'half' in save_type_str.lower() if save_type_str else False
    negates_on_save = 'negates' in save_type_str.lower() if save_type_str else False

    if save_type:
        success, roll_total, save_desc = roll_saving_throw(target, save_type, dc)
        results.append(save_desc)

        if success:
            if negates_on_save:
                return f"{caster.name} casts {spell_name}!\n{save_desc}\n{target.name} resists the spell!"
            elif half_on_save:
                damage = damage // 2
                results.append(f"{target.name} takes half damage!")

    # Apply damage
    if damage > 0:
        target.hp = max(0, target.hp - damage)
        results.append(f"{caster.name} casts {spell_name} on {target.name} for {damage} damage!")

        if target.hp <= 0:
            if hasattr(target, 'alive'):
                target.alive = False
            results.append(f"{target.name} is slain!")

            xp_award = award_xp(caster, target)
            if xp_award:
                results.append(f"(+{xp_award} XP)")

            # Quest trigger for mob kills (spell damage)
            if hasattr(caster, 'quest_log'):
                mob_type = getattr(target, 'mob_type', target.name.lower())
                quest_updates = quest_module.on_mob_killed(caster, mob_type)
                for update in quest_updates:
                    results.append(f"[Quest] {update}")

    # Apply conditions
    if 'applies_condition' in spell_data:
        condition = spell_data['applies_condition']
        duration = spell_data.get('duration_rounds', 1)
        if hasattr(target, 'add_condition'):
            target.add_condition(condition)
            if hasattr(target, 'active_conditions'):
                target.active_conditions[condition] = duration
            results.append(f"{target.name} is now {condition}!")

    return "\n".join(results)


def calculate_spell_damage(caster, damage_str: str) -> int:
    """Parse and calculate spell damage"""
    import re

    # Handle "XdY" format
    match = re.match(r'(\d+)d(\d+)', damage_str)
    if match:
        num_dice = int(match.group(1))
        die_size = int(match.group(2))

        # Check for "per level" or "per caster level"
        if 'per level' in damage_str.lower() or 'per caster level' in damage_str.lower():
            level = getattr(caster, 'level', 1)
            num_dice = num_dice * level

            # Check for cap
            cap_match = re.search(r'max(?:imum)?\s*(\d+)', damage_str.lower())
            if cap_match:
                max_dice = int(cap_match.group(1))
                num_dice = min(num_dice, max_dice)

        damage = sum(random.randint(1, die_size) for _ in range(num_dice))

        # Check for bonus
        bonus_match = re.search(r'\+(\d+)', damage_str)
        if bonus_match:
            damage += int(bonus_match.group(1))

        return damage

    return 0
