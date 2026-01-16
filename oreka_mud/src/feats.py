# feats.py
"""
D&D 3.5 OGL Feats system for OrekaMUD
This module defines all feats, their descriptions, prerequisites, and effects.
"""

from typing import Dict, List, Optional, Callable, Any, Tuple


class Feat:
    """
    Represents a D&D 3.5 feat with prerequisites and effects.

    Effects can be:
    - Passive bonuses (skill, save, AC, attack, damage, HP, initiative)
    - Active abilities (triggered in combat)
    - Special rules modifications
    """
    def __init__(
        self,
        name: str,
        description: str,
        prerequisites: List[Dict] = None,
        effect: Callable = None,
        feat_type: str = "general",
        is_bonus: bool = False,
        is_fighter_bonus: bool = False,
        stackable: bool = False,
    ):
        self.name = name
        self.description = description
        self.prerequisites = prerequisites or []
        self.effect = effect
        self.feat_type = feat_type  # general, combat, metamagic, item_creation, etc.
        self.is_bonus = is_bonus  # Can be taken as a bonus feat
        self.is_fighter_bonus = is_fighter_bonus  # Fighter bonus feat
        self.stackable = stackable  # Can be taken multiple times

    def apply(self, user, context: str = None, **kwargs):
        """
        Apply the feat's effect.

        Args:
            user: The character/mob using the feat
            context: What the feat is being applied to (skill, attack, damage, etc.)
            **kwargs: Additional context (skill name, save type, etc.)

        Returns:
            Modified value or result
        """
        if self.effect:
            return self.effect(user, context=context, **kwargs)
        return kwargs.get('value', 0)


# =============================================================================
# Prerequisite Checking
# =============================================================================

def meets_prereq(character, prereq: Dict) -> bool:
    """
    Check if a character meets a single prerequisite dict.
    Supported keys: 'level', 'bab', 'ability', 'feat', 'class_feature', 'skill', 'race', 'class', 'caster_level'.
    """
    if 'level' in prereq:
        if getattr(character, 'level', 1) < prereq['level']:
            return False

    if 'bab' in prereq:
        bab = getattr(character, 'bab', None)
        if bab is None:
            cl = getattr(character, 'char_class', '').lower()
            lvl = getattr(character, 'level', 1)
            if cl in ('fighter', 'barbarian', 'paladin', 'ranger'):
                bab = lvl
            elif cl in ('wizard', 'sorcerer'):
                bab = lvl // 2
            else:
                bab = (lvl * 3) // 4
        if bab < prereq['bab']:
            return False

    if 'ability' in prereq:
        ab, val = prereq['ability']
        if getattr(character, f'{ab.lower()}_score', 10) < val:
            return False

    if 'feat' in prereq:
        feats = getattr(character, 'feats', [])
        required = prereq['feat']
        # Handle partial matches for feats like "Weapon Focus (longsword)"
        found = False
        for f in feats:
            if required.lower() in f.lower():
                found = True
                break
        if not found:
            return False

    if 'class_feature' in prereq:
        if prereq['class_feature'] not in getattr(character, 'class_features', []):
            return False

    if 'skill' in prereq:
        sk, val = prereq['skill']
        if getattr(character, 'skills', {}).get(sk, 0) < val:
            return False

    if 'race' in prereq:
        if getattr(character, 'race', '').lower() != prereq['race'].lower():
            return False

    if 'class' in prereq:
        if getattr(character, 'char_class', '').lower() != prereq['class'].lower():
            return False

    if 'caster_level' in prereq:
        caster_level = getattr(character, 'caster_level', 0)
        if caster_level < prereq['caster_level']:
            return False

    return True


def is_eligible_for_feat(character, feat) -> bool:
    """Return True if character meets all prerequisites for the feat."""
    if isinstance(feat, str):
        feat = FEATS.get(feat)
    if not feat:
        return False
    for prereq in feat.prerequisites:
        if not meets_prereq(character, prereq):
            return False
    return True


def list_eligible_feats(character, only_bonus: bool = False, only_fighter: bool = False) -> List[str]:
    """Return a list of feat names the character is eligible to select."""
    eligible = []
    for fname, feat in FEATS.items():
        if only_bonus and not feat.is_bonus:
            continue
        if only_fighter and not feat.is_fighter_bonus:
            continue
        if fname in getattr(character, 'feats', []):
            if not feat.stackable:
                continue
        if is_eligible_for_feat(character, feat):
            eligible.append(fname)
    return eligible


def get_feat(name: str) -> Optional[Feat]:
    """Get a feat by name."""
    return FEATS.get(name)


# =============================================================================
# Feat Effect Functions
# =============================================================================

# --- Skill Bonus Feats ---

def effect_alertness(user, context=None, **kwargs):
    """Alertness: +2 to Listen and Spot checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Listen', 'Spot'):
        return value + 2
    return value


def effect_acrobatic(user, context=None, **kwargs):
    """Acrobatic: +2 to Jump and Tumble checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Jump', 'Tumble'):
        return value + 2
    return value


def effect_agile(user, context=None, **kwargs):
    """Agile: +2 to Balance and Escape Artist checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Balance', 'Escape Artist'):
        return value + 2
    return value


def effect_animal_affinity(user, context=None, **kwargs):
    """Animal Affinity: +2 to Handle Animal and Ride checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Handle Animal', 'Ride'):
        return value + 2
    return value


def effect_athletic(user, context=None, **kwargs):
    """Athletic: +2 to Climb and Swim checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Climb', 'Swim'):
        return value + 2
    return value


def effect_deceitful(user, context=None, **kwargs):
    """Deceitful: +2 to Disguise and Forgery checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Disguise', 'Forgery'):
        return value + 2
    return value


def effect_deft_hands(user, context=None, **kwargs):
    """Deft Hands: +2 to Sleight of Hand and Use Rope checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Sleight of Hand', 'Use Rope'):
        return value + 2
    return value


def effect_diligent(user, context=None, **kwargs):
    """Diligent: +2 to Appraise and Decipher Script checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Appraise', 'Decipher Script'):
        return value + 2
    return value


def effect_investigator(user, context=None, **kwargs):
    """Investigator: +2 to Gather Information and Search checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Gather Information', 'Search'):
        return value + 2
    return value


def effect_magical_aptitude(user, context=None, **kwargs):
    """Magical Aptitude: +2 to Spellcraft and Use Magic Device checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Spellcraft', 'Use Magic Device'):
        return value + 2
    return value


def effect_negotiator(user, context=None, **kwargs):
    """Negotiator: +2 to Diplomacy and Sense Motive checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Diplomacy', 'Sense Motive'):
        return value + 2
    return value


def effect_nimble_fingers(user, context=None, **kwargs):
    """Nimble Fingers: +2 to Disable Device and Open Lock checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Disable Device', 'Open Lock'):
        return value + 2
    return value


def effect_persuasive(user, context=None, **kwargs):
    """Persuasive: +2 to Bluff and Intimidate checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Bluff', 'Intimidate'):
        return value + 2
    return value


def effect_self_sufficient(user, context=None, **kwargs):
    """Self-Sufficient: +2 to Heal and Survival checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Heal', 'Survival'):
        return value + 2
    return value


def effect_stealthy(user, context=None, **kwargs):
    """Stealthy: +2 to Hide and Move Silently checks."""
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill' and skill in ('Hide', 'Move Silently'):
        return value + 2
    return value


def effect_skill_focus(user, context=None, **kwargs):
    """Skill Focus: +3 to chosen skill checks."""
    # Skill Focus is taken for a specific skill, stored as "Skill Focus (Perception)"
    skill = kwargs.get('skill')
    value = kwargs.get('value', 0)
    if context == 'skill':
        # Check if user has Skill Focus for this skill
        for feat in getattr(user, 'feats', []):
            if feat.startswith('Skill Focus') and skill and skill.lower() in feat.lower():
                return value + 3
    return value


# --- Save Bonus Feats ---

def effect_iron_will(user, context=None, **kwargs):
    """Iron Will: +2 to Will saves."""
    save_type = kwargs.get('save_type')
    value = kwargs.get('value', 0)
    if context == 'save' and save_type == 'Will':
        return value + 2
    return value


def effect_lightning_reflexes(user, context=None, **kwargs):
    """Lightning Reflexes: +2 to Reflex saves."""
    save_type = kwargs.get('save_type')
    value = kwargs.get('value', 0)
    if context == 'save' and save_type == 'Reflex':
        return value + 2
    return value


def effect_great_fortitude(user, context=None, **kwargs):
    """Great Fortitude: +2 to Fortitude saves."""
    save_type = kwargs.get('save_type')
    value = kwargs.get('value', 0)
    if context == 'save' and save_type == 'Fortitude':
        return value + 2
    return value


# --- HP/Toughness Feats ---

def effect_toughness(user, context=None, **kwargs):
    """Toughness: +3 hit points."""
    value = kwargs.get('value', 0)
    if context == 'hp':
        return value + 3
    return value


# --- Initiative Feats ---

def effect_improved_initiative(user, context=None, **kwargs):
    """Improved Initiative: +4 to initiative checks."""
    value = kwargs.get('value', 0)
    if context == 'initiative':
        return value + 4
    return value


# --- Combat Feats ---

def effect_weapon_focus(user, context=None, **kwargs):
    """Weapon Focus: +1 to attack rolls with chosen weapon."""
    value = kwargs.get('value', 0)
    weapon = kwargs.get('weapon')
    if context == 'attack':
        for feat in getattr(user, 'feats', []):
            if feat.startswith('Weapon Focus'):
                if weapon and weapon.lower() in feat.lower():
                    return value + 1
                # Generic weapon focus for current weapon
                if not weapon:
                    return value + 1
    return value


def effect_greater_weapon_focus(user, context=None, **kwargs):
    """Greater Weapon Focus: +1 to attack rolls (stacks with Weapon Focus)."""
    value = kwargs.get('value', 0)
    weapon = kwargs.get('weapon')
    if context == 'attack':
        for feat in getattr(user, 'feats', []):
            if feat.startswith('Greater Weapon Focus'):
                if weapon and weapon.lower() in feat.lower():
                    return value + 1
                if not weapon:
                    return value + 1
    return value


def effect_weapon_specialization(user, context=None, **kwargs):
    """Weapon Specialization: +2 to damage rolls with chosen weapon."""
    value = kwargs.get('value', 0)
    weapon = kwargs.get('weapon')
    if context == 'damage':
        for feat in getattr(user, 'feats', []):
            if feat.startswith('Weapon Specialization'):
                if weapon and weapon.lower() in feat.lower():
                    return value + 2
                if not weapon:
                    return value + 2
    return value


def effect_greater_weapon_specialization(user, context=None, **kwargs):
    """Greater Weapon Specialization: +2 to damage (stacks with Weapon Spec)."""
    value = kwargs.get('value', 0)
    weapon = kwargs.get('weapon')
    if context == 'damage':
        for feat in getattr(user, 'feats', []):
            if feat.startswith('Greater Weapon Specialization'):
                if weapon and weapon.lower() in feat.lower():
                    return value + 2
                if not weapon:
                    return value + 2
    return value


def effect_point_blank_shot(user, context=None, **kwargs):
    """Point Blank Shot: +1 attack and damage with ranged weapons within 30 ft."""
    value = kwargs.get('value', 0)
    is_ranged = kwargs.get('is_ranged', False)
    distance = kwargs.get('distance', 0)
    if is_ranged and distance <= 30:
        if context in ('attack', 'damage'):
            return value + 1
    return value


def effect_precise_shot(user, context=None, **kwargs):
    """Precise Shot: No penalty for shooting into melee."""
    # This is handled in combat calculations
    value = kwargs.get('value', 0)
    return value


def effect_rapid_shot(user, context=None, **kwargs):
    """Rapid Shot: Extra ranged attack at -2 penalty."""
    # This modifies the number of attacks, handled in combat
    value = kwargs.get('value', 0)
    return value


def effect_manyshot(user, context=None, **kwargs):
    """Manyshot: Fire multiple arrows as a standard action."""
    value = kwargs.get('value', 0)
    return value


def effect_deadly_aim(user, context=None, **kwargs):
    """Deadly Aim: Trade attack for damage with ranged weapons."""
    # Similar to Power Attack but for ranged
    value = kwargs.get('value', 0)
    return value


def effect_two_weapon_fighting(user, context=None, **kwargs):
    """Two-Weapon Fighting: Reduce two-weapon penalties."""
    value = kwargs.get('value', 0)
    if context == 'twf_penalty':
        # Reduce penalty from -6/-10 to -4/-4 (or -2/-2 with light off-hand)
        return value + 2
    return value


def effect_improved_two_weapon_fighting(user, context=None, **kwargs):
    """Improved Two-Weapon Fighting: Extra off-hand attack at -5."""
    value = kwargs.get('value', 0)
    return value


def effect_greater_two_weapon_fighting(user, context=None, **kwargs):
    """Greater Two-Weapon Fighting: Third off-hand attack at -10."""
    value = kwargs.get('value', 0)
    return value


def effect_combat_expertise(user, context=None, **kwargs):
    """Combat Expertise: Trade attack bonus for AC (up to BAB, max 5)."""
    value = kwargs.get('value', 0)
    combat_expertise_amt = getattr(user, 'combat_expertise_amt', 0)
    if context == 'attack':
        return value - combat_expertise_amt
    elif context == 'ac':
        return value + combat_expertise_amt
    return value


def effect_improved_critical(user, context=None, **kwargs):
    """Improved Critical: Double threat range with chosen weapon."""
    value = kwargs.get('value', 0)
    if context == 'threat_range':
        return value * 2
    return value


def effect_power_attack(user, context=None, **kwargs):
    """Power Attack: Trade attack bonus for damage."""
    value = kwargs.get('value', 0)
    power_attack_amt = getattr(user, 'power_attack_amt', 0)
    if context == 'attack':
        return value - power_attack_amt
    elif context == 'damage':
        # Two-handed weapons get 2x bonus
        is_two_handed = kwargs.get('is_two_handed', False)
        multiplier = 2 if is_two_handed else 1
        return value + (power_attack_amt * multiplier)
    return value


# --- Defense Feats ---

def effect_dodge(user, context=None, **kwargs):
    """Dodge: +1 dodge bonus to AC against one opponent."""
    value = kwargs.get('value', 0)
    attacker = kwargs.get('attacker')
    if context == 'ac' and attacker:
        dodge_target = getattr(user, 'dodge_target', None)
        if dodge_target and (
            getattr(attacker, 'vnum', None) == dodge_target or
            getattr(attacker, 'name', None) == dodge_target
        ):
            return value + 1
    return value


def effect_mobility(user, context=None, **kwargs):
    """Mobility: +4 AC against attacks of opportunity from movement."""
    value = kwargs.get('value', 0)
    if context == 'ac' and kwargs.get('is_aoo', False):
        return value + 4
    return value


def effect_combat_reflexes(user, context=None, **kwargs):
    """Combat Reflexes: Extra AoO equal to Dex modifier."""
    value = kwargs.get('value', 0)
    if context == 'aoo_count':
        dex_mod = (getattr(user, 'dex_score', 10) - 10) // 2
        return max(1, 1 + dex_mod)
    return value


def effect_deflect_arrows(user, context=None, **kwargs):
    """Deflect Arrows: Deflect one ranged attack per round."""
    value = kwargs.get('value', 0)
    return value


def effect_snatch_arrows(user, context=None, **kwargs):
    """Snatch Arrows: Catch deflected arrows and throw them back."""
    value = kwargs.get('value', 0)
    return value


# --- Special Combat Feats ---

def effect_improved_grapple(user, context=None, **kwargs):
    """Improved Grapple: +4 to grapple checks, no AoO."""
    value = kwargs.get('value', 0)
    if context == 'grapple':
        return value + 4
    return value


def effect_improved_disarm(user, context=None, **kwargs):
    """Improved Disarm: +4 to disarm attempts, no AoO."""
    value = kwargs.get('value', 0)
    if context == 'disarm':
        return value + 4
    return value


def effect_improved_trip(user, context=None, **kwargs):
    """Improved Trip: +4 to trip attempts, no AoO, free attack on success."""
    value = kwargs.get('value', 0)
    if context == 'trip':
        return value + 4
    return value


def effect_improved_bull_rush(user, context=None, **kwargs):
    """Improved Bull Rush: +4 to bull rush attempts, no AoO."""
    value = kwargs.get('value', 0)
    if context == 'bull_rush':
        return value + 4
    return value


def effect_improved_overrun(user, context=None, **kwargs):
    """Improved Overrun: +4 to overrun attempts, target can't avoid."""
    value = kwargs.get('value', 0)
    if context == 'overrun':
        return value + 4
    return value


def effect_improved_sunder(user, context=None, **kwargs):
    """Improved Sunder: +4 to sunder attempts, no AoO."""
    value = kwargs.get('value', 0)
    if context == 'sunder':
        return value + 4
    return value


def effect_improved_feint(user, context=None, **kwargs):
    """Improved Feint: Feint as a move action instead of standard."""
    value = kwargs.get('value', 0)
    return value


def effect_stunning_fist(user, context=None, **kwargs):
    """Stunning Fist: Stun opponent on hit (Fort save)."""
    value = kwargs.get('value', 0)
    return value


def effect_blind_fight(user, context=None, **kwargs):
    """Blind-Fight: Reroll miss chance for concealment, no AC loss vs invisible."""
    value = kwargs.get('value', 0)
    if context == 'miss_chance':
        # Halve miss chance from concealment
        return value // 2
    return value


def effect_whirlwind_attack(user, context=None, **kwargs):
    """Whirlwind Attack: Attack all adjacent foes."""
    value = kwargs.get('value', 0)
    return value


def effect_spring_attack(user, context=None, **kwargs):
    """Spring Attack: Move-attack-move, no AoO from target."""
    value = kwargs.get('value', 0)
    return value


def effect_cleave(user, context=None, **kwargs):
    """Cleave: Extra attack if you drop a foe."""
    value = kwargs.get('value', 0)
    return value


def effect_great_cleave(user, context=None, **kwargs):
    """Great Cleave: Unlimited cleave attacks per round."""
    value = kwargs.get('value', 0)
    return value


# --- Metamagic Feats ---

def effect_empower_spell(user, context=None, **kwargs):
    """Empower Spell: Increase variable numeric effects by 50%."""
    value = kwargs.get('value', 0)
    if context == 'spell_damage':
        return int(value * 1.5)
    return value


def effect_maximize_spell(user, context=None, **kwargs):
    """Maximize Spell: Maximize all variable numeric effects."""
    value = kwargs.get('value', 0)
    dice = kwargs.get('dice')
    if context == 'spell_damage' and dice:
        # dice = (num, size, bonus)
        num, size, bonus = dice
        return num * size + bonus
    return value


def effect_quicken_spell(user, context=None, **kwargs):
    """Quicken Spell: Cast spell as a swift action."""
    value = kwargs.get('value', 0)
    return value


def effect_silent_spell(user, context=None, **kwargs):
    """Silent Spell: Cast spell without verbal components."""
    value = kwargs.get('value', 0)
    return value


def effect_still_spell(user, context=None, **kwargs):
    """Still Spell: Cast spell without somatic components."""
    value = kwargs.get('value', 0)
    return value


def effect_extend_spell(user, context=None, **kwargs):
    """Extend Spell: Double spell duration."""
    value = kwargs.get('value', 0)
    if context == 'spell_duration':
        return value * 2
    return value


def effect_widen_spell(user, context=None, **kwargs):
    """Widen Spell: Double spell area."""
    value = kwargs.get('value', 0)
    if context == 'spell_area':
        return value * 2
    return value


def effect_heighten_spell(user, context=None, **kwargs):
    """Heighten Spell: Cast spell at higher level."""
    value = kwargs.get('value', 0)
    return value


# --- Misc Feats ---

def effect_run(user, context=None, **kwargs):
    """Run: Run at 5x speed instead of 4x, +4 to Jump when running."""
    value = kwargs.get('value', 0)
    if context == 'run_multiplier':
        return 5
    if context == 'skill' and kwargs.get('skill') == 'Jump' and kwargs.get('is_running'):
        return value + 4
    return value


def effect_endurance(user, context=None, **kwargs):
    """Endurance: +4 to checks to avoid nonlethal damage from environmental hazards."""
    value = kwargs.get('value', 0)
    if context == 'endurance_check':
        return value + 4
    return value


def effect_diehard(user, context=None, **kwargs):
    """Diehard: Automatically stabilize when dying, can act while disabled."""
    value = kwargs.get('value', 0)
    return value


def effect_track(user, context=None, **kwargs):
    """Track: Use Survival to follow tracks."""
    value = kwargs.get('value', 0)
    return value


def effect_natural_spell(user, context=None, **kwargs):
    """Natural Spell: Cast spells while in wild shape."""
    value = kwargs.get('value', 0)
    return value


def effect_mounted_combat(user, context=None, **kwargs):
    """Mounted Combat: Negate hit on mount with Ride check."""
    value = kwargs.get('value', 0)
    return value


def effect_ride_by_attack(user, context=None, **kwargs):
    """Ride-By Attack: Move before and after mounted charge."""
    value = kwargs.get('value', 0)
    return value


def effect_spirited_charge(user, context=None, **kwargs):
    """Spirited Charge: Double damage on mounted charge (triple with lance)."""
    value = kwargs.get('value', 0)
    if context == 'damage' and kwargs.get('is_charge') and kwargs.get('is_mounted'):
        weapon = kwargs.get('weapon', '')
        if 'lance' in weapon.lower():
            return value * 3
        return value * 2
    return value


def effect_trample(user, context=None, **kwargs):
    """Trample: Mount can deal damage when overrunning."""
    value = kwargs.get('value', 0)
    return value


# =============================================================================
# The FEATS Dictionary
# =============================================================================

FEATS: Dict[str, Feat] = {
    # --- Skill Feats ---
    "Acrobatic": Feat(
        "Acrobatic",
        "+2 bonus on Jump and Tumble checks.",
        prerequisites=[],
        effect=effect_acrobatic,
        feat_type="general"
    ),
    "Agile": Feat(
        "Agile",
        "+2 bonus on Balance and Escape Artist checks.",
        prerequisites=[],
        effect=effect_agile,
        feat_type="general"
    ),
    "Alertness": Feat(
        "Alertness",
        "+2 bonus on Listen and Spot checks.",
        prerequisites=[],
        effect=effect_alertness,
        feat_type="general"
    ),
    "Animal Affinity": Feat(
        "Animal Affinity",
        "+2 bonus on Handle Animal and Ride checks.",
        prerequisites=[],
        effect=effect_animal_affinity,
        feat_type="general"
    ),
    "Athletic": Feat(
        "Athletic",
        "+2 bonus on Climb and Swim checks.",
        prerequisites=[],
        effect=effect_athletic,
        feat_type="general"
    ),
    "Deceitful": Feat(
        "Deceitful",
        "+2 bonus on Disguise and Forgery checks.",
        prerequisites=[],
        effect=effect_deceitful,
        feat_type="general"
    ),
    "Deft Hands": Feat(
        "Deft Hands",
        "+2 bonus on Sleight of Hand and Use Rope checks.",
        prerequisites=[],
        effect=effect_deft_hands,
        feat_type="general"
    ),
    "Diligent": Feat(
        "Diligent",
        "+2 bonus on Appraise and Decipher Script checks.",
        prerequisites=[],
        effect=effect_diligent,
        feat_type="general"
    ),
    "Investigator": Feat(
        "Investigator",
        "+2 bonus on Gather Information and Search checks.",
        prerequisites=[],
        effect=effect_investigator,
        feat_type="general"
    ),
    "Magical Aptitude": Feat(
        "Magical Aptitude",
        "+2 bonus on Spellcraft and Use Magic Device checks.",
        prerequisites=[],
        effect=effect_magical_aptitude,
        feat_type="general"
    ),
    "Negotiator": Feat(
        "Negotiator",
        "+2 bonus on Diplomacy and Sense Motive checks.",
        prerequisites=[],
        effect=effect_negotiator,
        feat_type="general"
    ),
    "Nimble Fingers": Feat(
        "Nimble Fingers",
        "+2 bonus on Disable Device and Open Lock checks.",
        prerequisites=[],
        effect=effect_nimble_fingers,
        feat_type="general"
    ),
    "Persuasive": Feat(
        "Persuasive",
        "+2 bonus on Bluff and Intimidate checks.",
        prerequisites=[],
        effect=effect_persuasive,
        feat_type="general"
    ),
    "Self-Sufficient": Feat(
        "Self-Sufficient",
        "+2 bonus on Heal and Survival checks.",
        prerequisites=[],
        effect=effect_self_sufficient,
        feat_type="general"
    ),
    "Stealthy": Feat(
        "Stealthy",
        "+2 bonus on Hide and Move Silently checks.",
        prerequisites=[],
        effect=effect_stealthy,
        feat_type="general"
    ),
    "Skill Focus": Feat(
        "Skill Focus",
        "+3 bonus on checks with chosen skill.",
        prerequisites=[],
        effect=effect_skill_focus,
        feat_type="general",
        stackable=True  # Can take for different skills
    ),

    # --- Save Feats ---
    "Great Fortitude": Feat(
        "Great Fortitude",
        "+2 bonus on Fortitude saves.",
        prerequisites=[],
        effect=effect_great_fortitude,
        feat_type="general"
    ),
    "Iron Will": Feat(
        "Iron Will",
        "+2 bonus on Will saves.",
        prerequisites=[],
        effect=effect_iron_will,
        feat_type="general"
    ),
    "Lightning Reflexes": Feat(
        "Lightning Reflexes",
        "+2 bonus on Reflex saves.",
        prerequisites=[],
        effect=effect_lightning_reflexes,
        feat_type="general"
    ),

    # --- HP/Toughness ---
    "Toughness": Feat(
        "Toughness",
        "+3 hit points.",
        prerequisites=[],
        effect=effect_toughness,
        feat_type="general",
        stackable=True
    ),

    # --- Initiative ---
    "Improved Initiative": Feat(
        "Improved Initiative",
        "+4 bonus on initiative checks.",
        prerequisites=[],
        effect=effect_improved_initiative,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Combat Feats ---
    "Power Attack": Feat(
        "Power Attack",
        "Trade attack bonus for damage (up to BAB).",
        prerequisites=[{'ability': ('Str', 13)}],
        effect=effect_power_attack,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Cleave": Feat(
        "Cleave",
        "Extra melee attack if you drop a foe.",
        prerequisites=[{'ability': ('Str', 13)}, {'feat': 'Power Attack'}],
        effect=effect_cleave,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Great Cleave": Feat(
        "Great Cleave",
        "No limit on Cleave attacks per round.",
        prerequisites=[{'ability': ('Str', 13)}, {'feat': 'Cleave'}, {'bab': 4}],
        effect=effect_great_cleave,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Combat Expertise": Feat(
        "Combat Expertise",
        "Trade attack bonus for AC (up to 5).",
        prerequisites=[{'ability': ('Int', 13)}],
        effect=effect_combat_expertise,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Disarm": Feat(
        "Improved Disarm",
        "+4 to disarm, no AoO provoked.",
        prerequisites=[{'ability': ('Int', 13)}, {'feat': 'Combat Expertise'}],
        effect=effect_improved_disarm,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Trip": Feat(
        "Improved Trip",
        "+4 to trip, no AoO, free attack on success.",
        prerequisites=[{'ability': ('Int', 13)}, {'feat': 'Combat Expertise'}],
        effect=effect_improved_trip,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Feint": Feat(
        "Improved Feint",
        "Feint as a move action.",
        prerequisites=[{'ability': ('Int', 13)}, {'feat': 'Combat Expertise'}],
        effect=effect_improved_feint,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Whirlwind Attack": Feat(
        "Whirlwind Attack",
        "Attack all adjacent foes with one attack each.",
        prerequisites=[
            {'ability': ('Dex', 13)}, {'ability': ('Int', 13)},
            {'feat': 'Combat Expertise'}, {'feat': 'Dodge'},
            {'feat': 'Mobility'}, {'feat': 'Spring Attack'}, {'bab': 4}
        ],
        effect=effect_whirlwind_attack,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Defense/Dodge Chain ---
    "Dodge": Feat(
        "Dodge",
        "+1 dodge bonus to AC against one opponent.",
        prerequisites=[{'ability': ('Dex', 13)}],
        effect=effect_dodge,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Mobility": Feat(
        "Mobility",
        "+4 AC against attacks of opportunity from movement.",
        prerequisites=[{'ability': ('Dex', 13)}, {'feat': 'Dodge'}],
        effect=effect_mobility,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Spring Attack": Feat(
        "Spring Attack",
        "Move before and after attack, no AoO from target.",
        prerequisites=[{'ability': ('Dex', 13)}, {'feat': 'Dodge'}, {'feat': 'Mobility'}, {'bab': 4}],
        effect=effect_spring_attack,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Combat Reflexes ---
    "Combat Reflexes": Feat(
        "Combat Reflexes",
        "Extra attacks of opportunity equal to Dex modifier.",
        prerequisites=[],
        effect=effect_combat_reflexes,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Weapon Feats ---
    "Weapon Finesse": Feat(
        "Weapon Finesse",
        "Use Dex instead of Str for attack rolls with light weapons.",
        prerequisites=[{'bab': 1}],
        effect=None,  # Handled in attack calculations
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Weapon Focus": Feat(
        "Weapon Focus",
        "+1 to attack rolls with chosen weapon.",
        prerequisites=[{'bab': 1}],
        effect=effect_weapon_focus,
        feat_type="combat",
        is_fighter_bonus=True,
        stackable=True
    ),
    "Greater Weapon Focus": Feat(
        "Greater Weapon Focus",
        "+1 to attack rolls (stacks with Weapon Focus).",
        prerequisites=[{'feat': 'Weapon Focus'}, {'bab': 8}, {'class': 'Fighter'}],
        effect=effect_greater_weapon_focus,
        feat_type="combat",
        is_fighter_bonus=True,
        stackable=True
    ),
    "Weapon Specialization": Feat(
        "Weapon Specialization",
        "+2 to damage rolls with chosen weapon.",
        prerequisites=[{'feat': 'Weapon Focus'}, {'bab': 4}, {'class': 'Fighter'}],
        effect=effect_weapon_specialization,
        feat_type="combat",
        is_fighter_bonus=True,
        stackable=True
    ),
    "Greater Weapon Specialization": Feat(
        "Greater Weapon Specialization",
        "+2 to damage (stacks with Weapon Specialization).",
        prerequisites=[{'feat': 'Weapon Specialization'}, {'feat': 'Greater Weapon Focus'}, {'bab': 12}, {'class': 'Fighter'}],
        effect=effect_greater_weapon_specialization,
        feat_type="combat",
        is_fighter_bonus=True,
        stackable=True
    ),
    "Improved Critical": Feat(
        "Improved Critical",
        "Double threat range with chosen weapon.",
        prerequisites=[{'bab': 8}],
        effect=effect_improved_critical,
        feat_type="combat",
        is_fighter_bonus=True,
        stackable=True
    ),

    # --- Grapple/Bull Rush/etc ---
    "Improved Grapple": Feat(
        "Improved Grapple",
        "+4 to grapple checks, no AoO provoked.",
        prerequisites=[{'ability': ('Dex', 13)}, {'feat': 'Improved Unarmed Strike'}],
        effect=effect_improved_grapple,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Bull Rush": Feat(
        "Improved Bull Rush",
        "+4 to bull rush, no AoO provoked.",
        prerequisites=[{'ability': ('Str', 13)}, {'feat': 'Power Attack'}],
        effect=effect_improved_bull_rush,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Overrun": Feat(
        "Improved Overrun",
        "+4 to overrun, target can't avoid.",
        prerequisites=[{'ability': ('Str', 13)}, {'feat': 'Power Attack'}],
        effect=effect_improved_overrun,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Sunder": Feat(
        "Improved Sunder",
        "+4 to sunder, no AoO provoked.",
        prerequisites=[{'ability': ('Str', 13)}, {'feat': 'Power Attack'}],
        effect=effect_improved_sunder,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Unarmed Strike": Feat(
        "Improved Unarmed Strike",
        "Unarmed attacks deal lethal damage, no AoO provoked.",
        prerequisites=[],
        effect=None,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Stunning Fist": Feat(
        "Stunning Fist",
        "Stun opponent on unarmed hit (Fort save DC 10 + 1/2 level + Wis).",
        prerequisites=[{'ability': ('Dex', 13)}, {'ability': ('Wis', 13)}, {'feat': 'Improved Unarmed Strike'}, {'bab': 8}],
        effect=effect_stunning_fist,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Deflect Arrows": Feat(
        "Deflect Arrows",
        "Deflect one ranged attack per round.",
        prerequisites=[{'ability': ('Dex', 13)}, {'feat': 'Improved Unarmed Strike'}],
        effect=effect_deflect_arrows,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Snatch Arrows": Feat(
        "Snatch Arrows",
        "Catch deflected arrows and throw them back.",
        prerequisites=[{'ability': ('Dex', 15)}, {'feat': 'Deflect Arrows'}],
        effect=effect_snatch_arrows,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Ranged Combat ---
    "Point Blank Shot": Feat(
        "Point Blank Shot",
        "+1 attack and damage with ranged weapons within 30 feet.",
        prerequisites=[],
        effect=effect_point_blank_shot,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Precise Shot": Feat(
        "Precise Shot",
        "No penalty for shooting into melee.",
        prerequisites=[{'feat': 'Point Blank Shot'}],
        effect=effect_precise_shot,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Precise Shot": Feat(
        "Improved Precise Shot",
        "Ignore less than total cover/concealment.",
        prerequisites=[{'ability': ('Dex', 19)}, {'feat': 'Precise Shot'}, {'bab': 11}],
        effect=None,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Rapid Shot": Feat(
        "Rapid Shot",
        "Extra ranged attack at -2 penalty to all attacks.",
        prerequisites=[{'ability': ('Dex', 13)}, {'feat': 'Point Blank Shot'}],
        effect=effect_rapid_shot,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Manyshot": Feat(
        "Manyshot",
        "Fire multiple arrows as a standard action.",
        prerequisites=[{'ability': ('Dex', 17)}, {'feat': 'Rapid Shot'}, {'bab': 6}],
        effect=effect_manyshot,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Shot on the Run": Feat(
        "Shot on the Run",
        "Move before and after ranged attack.",
        prerequisites=[{'ability': ('Dex', 13)}, {'feat': 'Point Blank Shot'}, {'feat': 'Dodge'}, {'feat': 'Mobility'}, {'bab': 4}],
        effect=None,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Far Shot": Feat(
        "Far Shot",
        "Increase range increment by 50% (projectile) or 100% (thrown).",
        prerequisites=[{'feat': 'Point Blank Shot'}],
        effect=None,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Two-Weapon Fighting ---
    "Two-Weapon Fighting": Feat(
        "Two-Weapon Fighting",
        "Reduce two-weapon penalties.",
        prerequisites=[{'ability': ('Dex', 15)}],
        effect=effect_two_weapon_fighting,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Improved Two-Weapon Fighting": Feat(
        "Improved Two-Weapon Fighting",
        "Extra off-hand attack at -5 penalty.",
        prerequisites=[{'ability': ('Dex', 17)}, {'feat': 'Two-Weapon Fighting'}, {'bab': 6}],
        effect=effect_improved_two_weapon_fighting,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Greater Two-Weapon Fighting": Feat(
        "Greater Two-Weapon Fighting",
        "Third off-hand attack at -10 penalty.",
        prerequisites=[{'ability': ('Dex', 19)}, {'feat': 'Improved Two-Weapon Fighting'}, {'bab': 11}],
        effect=effect_greater_two_weapon_fighting,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Two-Weapon Defense": Feat(
        "Two-Weapon Defense",
        "+1 shield bonus to AC when wielding two weapons.",
        prerequisites=[{'feat': 'Two-Weapon Fighting'}],
        effect=None,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Blind-Fight ---
    "Blind-Fight": Feat(
        "Blind-Fight",
        "Reroll miss chance for concealment, keep Dex vs invisible.",
        prerequisites=[],
        effect=effect_blind_fight,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- Mounted Combat ---
    "Mounted Combat": Feat(
        "Mounted Combat",
        "Negate hit on mount with Ride check once per round.",
        prerequisites=[{'skill': ('Ride', 1)}],
        effect=effect_mounted_combat,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Mounted Archery": Feat(
        "Mounted Archery",
        "Halve penalty for ranged attacks while mounted.",
        prerequisites=[{'skill': ('Ride', 1)}, {'feat': 'Mounted Combat'}],
        effect=None,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Ride-By Attack": Feat(
        "Ride-By Attack",
        "Move before and after mounted charge.",
        prerequisites=[{'skill': ('Ride', 1)}, {'feat': 'Mounted Combat'}],
        effect=effect_ride_by_attack,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Spirited Charge": Feat(
        "Spirited Charge",
        "Double damage (triple with lance) on mounted charge.",
        prerequisites=[{'skill': ('Ride', 1)}, {'feat': 'Mounted Combat'}, {'feat': 'Ride-By Attack'}],
        effect=effect_spirited_charge,
        feat_type="combat",
        is_fighter_bonus=True
    ),
    "Trample": Feat(
        "Trample",
        "Mount can deal damage when overrunning.",
        prerequisites=[{'skill': ('Ride', 1)}, {'feat': 'Mounted Combat'}],
        effect=effect_trample,
        feat_type="combat",
        is_fighter_bonus=True
    ),

    # --- General/Misc ---
    "Run": Feat(
        "Run",
        "Run at 5x speed, +4 Jump when running.",
        prerequisites=[],
        effect=effect_run,
        feat_type="general"
    ),
    "Endurance": Feat(
        "Endurance",
        "+4 to Constitution checks for endurance, sleep in armor.",
        prerequisites=[],
        effect=effect_endurance,
        feat_type="general"
    ),
    "Diehard": Feat(
        "Diehard",
        "Automatically stabilize, act while disabled.",
        prerequisites=[{'feat': 'Endurance'}],
        effect=effect_diehard,
        feat_type="general"
    ),
    "Track": Feat(
        "Track",
        "Use Survival skill to follow tracks.",
        prerequisites=[],
        effect=effect_track,
        feat_type="general"
    ),

    # --- Metamagic Feats ---
    "Empower Spell": Feat(
        "Empower Spell",
        "Increase variable numeric effects by 50% (+2 spell level).",
        prerequisites=[],
        effect=effect_empower_spell,
        feat_type="metamagic"
    ),
    "Enlarge Spell": Feat(
        "Enlarge Spell",
        "Double spell range (+1 spell level).",
        prerequisites=[],
        effect=None,
        feat_type="metamagic"
    ),
    "Extend Spell": Feat(
        "Extend Spell",
        "Double spell duration (+1 spell level).",
        prerequisites=[],
        effect=effect_extend_spell,
        feat_type="metamagic"
    ),
    "Heighten Spell": Feat(
        "Heighten Spell",
        "Cast spell at higher level for higher save DC.",
        prerequisites=[],
        effect=effect_heighten_spell,
        feat_type="metamagic"
    ),
    "Maximize Spell": Feat(
        "Maximize Spell",
        "Maximize all variable numeric effects (+3 spell level).",
        prerequisites=[],
        effect=effect_maximize_spell,
        feat_type="metamagic"
    ),
    "Quicken Spell": Feat(
        "Quicken Spell",
        "Cast spell as swift action (+4 spell level).",
        prerequisites=[],
        effect=effect_quicken_spell,
        feat_type="metamagic"
    ),
    "Silent Spell": Feat(
        "Silent Spell",
        "Cast spell without verbal component (+1 spell level).",
        prerequisites=[],
        effect=effect_silent_spell,
        feat_type="metamagic"
    ),
    "Still Spell": Feat(
        "Still Spell",
        "Cast spell without somatic component (+1 spell level).",
        prerequisites=[],
        effect=effect_still_spell,
        feat_type="metamagic"
    ),
    "Widen Spell": Feat(
        "Widen Spell",
        "Double spell area (+3 spell level).",
        prerequisites=[],
        effect=effect_widen_spell,
        feat_type="metamagic"
    ),

    # --- Item Creation Feats ---
    "Brew Potion": Feat(
        "Brew Potion",
        "Create potions of spells up to 3rd level.",
        prerequisites=[{'caster_level': 3}],
        effect=None,
        feat_type="item_creation"
    ),
    "Craft Magic Arms and Armor": Feat(
        "Craft Magic Arms and Armor",
        "Create magic weapons, armor, and shields.",
        prerequisites=[{'caster_level': 5}],
        effect=None,
        feat_type="item_creation"
    ),
    "Craft Rod": Feat(
        "Craft Rod",
        "Create magic rods.",
        prerequisites=[{'caster_level': 9}],
        effect=None,
        feat_type="item_creation"
    ),
    "Craft Staff": Feat(
        "Craft Staff",
        "Create magic staves.",
        prerequisites=[{'caster_level': 12}],
        effect=None,
        feat_type="item_creation"
    ),
    "Craft Wand": Feat(
        "Craft Wand",
        "Create wands.",
        prerequisites=[{'caster_level': 5}],
        effect=None,
        feat_type="item_creation"
    ),
    "Craft Wondrous Item": Feat(
        "Craft Wondrous Item",
        "Create miscellaneous magic items.",
        prerequisites=[{'caster_level': 3}],
        effect=None,
        feat_type="item_creation"
    ),
    "Forge Ring": Feat(
        "Forge Ring",
        "Create magic rings.",
        prerequisites=[{'caster_level': 12}],
        effect=None,
        feat_type="item_creation"
    ),
    "Scribe Scroll": Feat(
        "Scribe Scroll",
        "Create scrolls of known spells.",
        prerequisites=[{'caster_level': 1}],
        effect=None,
        feat_type="item_creation"
    ),

    # --- Special ---
    "Natural Spell": Feat(
        "Natural Spell",
        "Cast spells while in wild shape.",
        prerequisites=[{'ability': ('Wis', 13)}, {'class_feature': 'Wild Shape'}],
        effect=effect_natural_spell,
        feat_type="general"
    ),
    "Extra Turning": Feat(
        "Extra Turning",
        "+4 turn/rebuke undead attempts per day.",
        prerequisites=[{'class_feature': 'Turn Undead'}],
        effect=None,
        feat_type="general",
        stackable=True
    ),
    "Improved Turning": Feat(
        "Improved Turning",
        "+1 effective level for turning undead.",
        prerequisites=[{'class_feature': 'Turn Undead'}],
        effect=None,
        feat_type="general"
    ),
}


# =============================================================================
# Feat Application Helpers
# =============================================================================

def apply_feat_bonuses(character, context: str, base_value: int = 0, **kwargs) -> int:
    """
    Apply all relevant feat bonuses to a value.

    Args:
        character: The character with feats
        context: What we're calculating (skill, save, attack, damage, ac, initiative, hp)
        base_value: The starting value
        **kwargs: Additional context (skill name, save type, weapon, etc.)

    Returns:
        Modified value with all applicable feat bonuses
    """
    value = base_value
    feats = getattr(character, 'feats', [])

    for feat_name in feats:
        # Handle feats with parameters like "Weapon Focus (longsword)"
        base_feat_name = feat_name.split('(')[0].strip()
        feat = FEATS.get(base_feat_name) or FEATS.get(feat_name)

        if feat and feat.effect:
            result = feat.apply(character, context=context, value=value, **kwargs)
            if isinstance(result, (int, float)):
                value = result

    return value


def get_skill_feat_bonus(character, skill_name: str) -> int:
    """Get total feat bonus for a skill."""
    return apply_feat_bonuses(character, 'skill', 0, skill=skill_name)


def get_save_feat_bonus(character, save_type: str) -> int:
    """Get total feat bonus for a saving throw."""
    return apply_feat_bonuses(character, 'save', 0, save_type=save_type)


def get_attack_feat_bonus(character, weapon: str = None) -> int:
    """Get total feat bonus for attack rolls."""
    return apply_feat_bonuses(character, 'attack', 0, weapon=weapon)


def get_damage_feat_bonus(character, weapon: str = None, is_two_handed: bool = False) -> int:
    """Get total feat bonus for damage rolls."""
    return apply_feat_bonuses(character, 'damage', 0, weapon=weapon, is_two_handed=is_two_handed)


def get_ac_feat_bonus(character, attacker=None, is_aoo: bool = False) -> int:
    """Get total feat bonus for AC."""
    return apply_feat_bonuses(character, 'ac', 0, attacker=attacker, is_aoo=is_aoo)


def get_initiative_feat_bonus(character) -> int:
    """Get total feat bonus for initiative."""
    return apply_feat_bonuses(character, 'initiative', 0)


def get_hp_feat_bonus(character) -> int:
    """Get total feat bonus for hit points."""
    return apply_feat_bonuses(character, 'hp', 0)


def get_aoo_count(character) -> int:
    """Get maximum attacks of opportunity per round."""
    base = 1
    if has_feat_by_name(character, 'Combat Reflexes'):
        dex_mod = (getattr(character, 'dex_score', 10) - 10) // 2
        return max(1, 1 + dex_mod)
    return base


def has_feat_by_name(character, feat_name: str) -> bool:
    """Check if character has a feat by name (handles parameterized feats)."""
    feats = getattr(character, 'feats', [])
    feat_lower = feat_name.lower()
    for f in feats:
        if feat_lower in f.lower():
            return True
    return False
