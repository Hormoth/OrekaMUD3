import random
from .feats import get_feat

class Mob:
    # --- Combat Maneuver/Skill Methods for Feats ---
    def disarm(self, target):
        # Improved Disarm: +4 bonus, no AoO
        bonus = 0
        if self.has_feat("Improved Disarm"):
            bonus += 4
            # No AoO for this action
        # TODO: Implement opposed roll logic
        return f"{self.name} attempts to disarm {target.name} (bonus: {bonus})"

    def trip(self, target):
        # Improved Trip: +4 bonus, no AoO
        bonus = 0
        if self.has_feat("Improved Trip"):
            bonus += 4
            # No AoO for this action
        # TODO: Implement opposed roll logic
        return f"{self.name} attempts to trip {target.name} (bonus: {bonus})"

    def bull_rush(self, target):
        # Improved Bull Rush: +4 bonus, no AoO
        bonus = 0
        if self.has_feat("Improved Bull Rush"):
            bonus += 4
            # No AoO for this action
        # TODO: Implement opposed roll logic
        return f"{self.name} attempts to bull rush {target.name} (bonus: {bonus})"

    def grapple(self, target):
        # Improved Grapple: +4 bonus, no AoO
        bonus = 0
        if self.has_feat("Improved Grapple"):
            bonus += 4
            # No AoO for this action
        # TODO: Implement opposed roll logic
        return f"{self.name} attempts to grapple {target.name} (bonus: {bonus})"

    def overrun(self, target):
        # Improved Overrun: +4 bonus, no AoO
        bonus = 0
        if self.has_feat("Improved Overrun"):
            bonus += 4
            # No AoO for this action
        # TODO: Implement opposed roll logic
        return f"{self.name} attempts to overrun {target.name} (bonus: {bonus})"

    def sunder(self, target):
        # Improved Sunder: +4 bonus, no AoO
        bonus = 0
        if self.has_feat("Improved Sunder"):
            bonus += 4
            # No AoO for this action
        # TODO: Implement opposed roll logic
        return f"{self.name} attempts to sunder {target.name}'s weapon (bonus: {bonus})"

    def whirlwind_attack(self, targets):
        # Whirlwind Attack: attack all adjacent enemies once
        if not self.has_feat("Whirlwind Attack"):
            return "You do not have the Whirlwind Attack feat."
        # TODO: Implement attack logic for all targets
        return f"{self.name} makes a Whirlwind Attack!"

    def spring_attack(self, target):
        # Spring Attack: move-attack-move, no AoO from target
        if not self.has_feat("Spring Attack"):
            return "You do not have the Spring Attack feat."
        # TODO: Implement move-attack-move logic
        return f"{self.name} performs a Spring Attack on {target.name}!"

    def stunning_fist(self, target):
        # Stunning Fist: attempt to stun target
        if not self.has_feat("Stunning Fist"):
            return "You do not have the Stunning Fist feat."
        # TODO: Implement attack and Fort save logic
        return f"{self.name} attempts a Stunning Fist on {target.name}!"

    def feint(self, target):
        # Improved Feint: feint as a move action
        bonus = 0
        if self.has_feat("Improved Feint"):
            # Feint as move action (handled in action system)
            pass
        # TODO: Implement opposed Bluff vs Sense Motive
        return f"{self.name} attempts to feint {target.name}!"
    def __init__(self, vnum, name, level, hp_dice, ac, damage_dice, flags=None, 
                 type_="", alignment="", ability_scores=None, initiative=0, speed=None, attacks=None, 
                 special_attacks=None, special_qualities=None, feats=None, skills=None, saves=None, 
                 environment="", organization="", cr=None, advancement=None, description=""):
        # ...existing code...
        self.dodge_target = None  # For Dodge feat: vnum or name of target
        self.weapon_type = attacks[0]["type"] if attacks else None  # For Weapon Finesse/Focus
        self.aoo_count = 0  # Attacks of opportunity used this round
        self.power_attack_amt = 0  # Power Attack value for this round
        self.track_target = None  # For Track feat
    def set_dodge_target(self, target):
        self.dodge_target = target

    def set_power_attack(self, amount):
        # Set Power Attack value for this round (AI or player)
        if self.has_feat("Power Attack"):
            bab = (self.level * 3) // 4
            self.power_attack_amt = max(0, min(amount, bab))
        else:
            self.power_attack_amt = 0

    def reset_aoo(self):
        self.aoo_count = 0

    def can_aoo(self):
        # Combat Reflexes: extra AoOs per round equal to Dex mod
        max_aoo = 1
        if self.has_feat("Combat Reflexes"):
            dex_mod = (self.ability_scores.get("Dex", 10) - 10) // 2
            max_aoo += max(0, dex_mod)
        return self.aoo_count < max_aoo

    def use_aoo(self):
        self.aoo_count += 1

    def set_track_target(self, target):
        self.track_target = target
    def get_hp(self):
        # Base HP plus passive feat bonuses (e.g., Toughness)
        hp = self.max_hp
        from .feats import get_feat
        if self.has_feat("Toughness"):
            hp = get_feat("Toughness").apply(self, value=hp)
        return hp

    def get_skill(self, skill):
        # Base skill plus passive feat bonuses
        value = self.skills.get(skill, 0)
        from .feats import FEATS
        # Always check Acrobatic, Agile, Alertness for their skills
        for feat_name in self.feats:
            feat = FEATS.get(feat_name)
            if feat and feat.effect:
                value = feat.apply(self, skill=skill, value=value)
        # Passive check for Acrobatic, Agile, Alertness even if not in feats (for futureproofing)
        for passive in ("Acrobatic", "Agile", "Alertness"):
            if passive in self.feats:
                feat = FEATS.get(passive)
                if feat and feat.effect:
                    value = feat.apply(self, skill=skill, value=value)
        return value

    def get_save(self, save):
        # Base save plus passive feat bonuses
        value = self.saves.get(save, 0)
        from .feats import FEATS
        for feat_name in self.feats:
            feat = FEATS.get(feat_name)
            if feat and feat.effect:
                value = feat.apply(self, save=save, value=value)
        return value

    def get_ac(self, vs_aop=False, attacker=None):
        # Base AC plus passive feat bonuses (e.g., Dodge, Mobility)
        ac = self.ac
        # Dodge: +1 AC vs chosen target
        if self.has_feat("Dodge") and attacker and (getattr(attacker, 'vnum', None) == self.dodge_target or getattr(attacker, 'name', None) == self.dodge_target):
            ac += 1
        if vs_aop and self.has_feat("Mobility"):
            ac += 4
        return ac

    def get_initiative(self):
        # Initiative plus Improved Initiative
        value = self.initiative
        if self.has_feat("Improved Initiative"):
            from .feats import get_feat
            value = get_feat("Improved Initiative").apply(self, value=value)
        return value

    def get_speed(self, mode="land"):
        # Speed plus Run feat
        base = self.speed.get(mode, 0)
        if self.has_feat("Run") and mode == "land":
            return int(base * 1.25)  # x5 instead of x4 (approximate)
        return base
    def __init__(self, vnum, name, level, hp_dice, ac, damage_dice, flags=None, 
                 type_="", alignment="", ability_scores=None, initiative=0, speed=None, attacks=None, 
                 special_attacks=None, special_qualities=None, feats=None, skills=None, saves=None, 
                 environment="", organization="", cr=None, advancement=None, description=""):
        self.vnum = vnum
        self.name = name
        self.level = level
        self.hp = sum(random.randint(1, hp_dice[1]) for _ in range(hp_dice[0])) + hp_dice[2]
        self.max_hp = self.hp
        self.ac = ac
        self.damage_dice = damage_dice
        self.flags = flags or []
        self.type_ = type_  # e.g., 'Animal', 'Magical Beast'
        self.alignment = alignment
        self.ability_scores = ability_scores or {"Str":10, "Dex":10, "Con":10, "Int":2, "Wis":10, "Cha":6}
        self.initiative = initiative
        self.speed = speed or {"land": 30}
        self.attacks = attacks or []  # List of dicts: {"type": "claw", "bonus": 5, "damage": "1d6+3"}
        self.special_attacks = special_attacks or []
        self.special_qualities = special_qualities or []
        self.feats = feats or []
        self.skills = skills or {}
        self.saves = saves or {"Fort": 0, "Ref": 0, "Will": 0}
        self.environment = environment
        self.organization = organization
        self.cr = cr
        self.advancement = advancement
        self.description = description
        self.alive = True
        self.conditions = set()

    def add_condition(self, condition):
        self.conditions.add(condition)

    def remove_condition(self, condition):
        self.conditions.discard(condition)

    def has_condition(self, condition):
        return condition in self.conditions

    def attack(self, target, power_attack_amt=None, all_targets=None):
        # Attack logic with feat support (Power Attack, Weapon Finesse, Weapon Focus, Cleave, Dodge, Combat Reflexes)
        roll = random.randint(1, 20)
        bab = (self.level * 3) // 4
        # Weapon Finesse: use Dex instead of Str for attack bonus if using a finesse weapon
        str_mod = (self.ability_scores.get("Str", 10) - 10) // 2
        dex_mod = (self.ability_scores.get("Dex", 10) - 10) // 2
        using_finesse = self.has_feat("Weapon Finesse") and self._is_finesse_weapon()
        stat_mod = dex_mod if using_finesse else str_mod
        attack_bonus = bab + stat_mod
        # Power Attack: trade attack for damage
        pa_amt = self.power_attack_amt if power_attack_amt is None else power_attack_amt
        if self.has_feat("Power Attack") and pa_amt > 0:
            attack_bonus -= pa_amt
        # Weapon Focus: +1 to attack with specified weapon
        if self.has_feat("Weapon Focus"):
            for f in self.feats:
                if f.startswith("Weapon Focus"):
                    focus_type = f.split("(")[-1].rstrip(")")
                    if self.weapon_type and self.weapon_type in focus_type:
                        attack_bonus += 1
        # Dodge: target may have +1 AC if dodging this mob
        ac = target.get_ac(attacker=self)
        # TODO: Add other feat/condition/skill modifiers
        if roll == 1:
            return "Miss!"
        if roll == 20 or roll + attack_bonus >= ac:
            # Power Attack: add to damage
            damage = sum(random.randint(1, self.damage_dice[1]) for _ in range(self.damage_dice[0])) + self.damage_dice[2]
            if self.has_feat("Power Attack") and pa_amt > 0:
                damage += pa_amt
            target.hp = max(0, target.hp - damage)
            result = f"{self.name} hits {target.name} for {damage} damage!"
            if target.hp == 0:
                target.alive = False
                result = f"{self.name} kills {target.name}!"
                # Cleave: grant extra attack if available
                if self.has_feat("Cleave") and all_targets:
                    # Find another adjacent target (not self or dead)
                    for t in all_targets:
                        if t is not target and getattr(t, 'alive', True):
                            result += f" {self.name} cleaves into {t.name}! "
                            result += self.attack(t, power_attack_amt=pa_amt, all_targets=all_targets)
                            break
            return result
        return "Miss!"

    def _is_finesse_weapon(self):
        # Simple check: treat 'claw', 'bite', 'dagger', etc. as finesse weapons
        if not self.attacks:
            return False
        finesse_types = ["claw", "bite", "dagger", "rapier", "shortsword"]
        return self.attacks[0]["type"] in finesse_types

    def has_feat(self, feat_name):
        """Return True if mob has the named feat (case-insensitive, partial match allowed for Weapon Focus etc)."""
        for f in self.feats:
            if feat_name.lower() in f.lower():
                return True
        return False

    def is_weapon_proficient(self, weapon_name_or_type):
        # D&D 3.5 core proficiencies by class
        # weapon_name_or_type: string, e.g. 'longsword', 'club', 'rapier', 'martial', 'simple'
        class_name = getattr(self, 'char_class', None) or getattr(self, 'class_', None) or getattr(self, 'class', None)
        if not class_name:
            return False
        class_name = class_name.lower()
        # Normalize weapon type
        w = weapon_name_or_type.lower()
        # Barbarian, Ranger: all simple and martial
        if class_name in ("barbarian", "ranger"):
            return w in ("simple", "martial") or w in SIMPLE_WEAPONS or w in MARTIAL_WEAPONS
        # Rogue: all simple, hand crossbow, rapier, sap, shortbow, short sword
        if class_name == "rogue":
            return w in SIMPLE_WEAPONS or w in ("hand crossbow", "rapier", "sap", "shortbow", "short sword")
        # Wizard, Sorcerer: club, dagger, heavy crossbow, light crossbow, quarterstaff
        if class_name in ("wizard", "sorcerer"):
            return w in ("club", "dagger", "heavy crossbow", "light crossbow", "quarterstaff")
        return False

# Weapon lists (abbreviated, expand as needed)
SIMPLE_WEAPONS = set([
    "club", "dagger", "heavy crossbow", "light crossbow", "quarterstaff", "shortspear", "spear", "mace", "sickle", "javelin", "morningstar", "sling", "staff", "light mace", "heavy mace", "dart", "greatclub", "handaxe", "light hammer", "light pick", "heavy pick", "scythe"
])
MARTIAL_WEAPONS = set([
    "longsword", "battleaxe", "warhammer", "scimitar", "falchion", "glaive", "greataxe", "greatsword", "halberd", "lance", "rapier", "sabre", "shortbow", "longbow", "trident", "whip", "flail", "heavy flail", "guisarme", "kukri", "net", "ranseur", "scimitar", "scythe", "sickle", "spiked chain"
])

# In attack() or equip logic, call self.is_weapon_proficient(weapon_name) and apply penalty or block if not.
    # Add more methods for special attacks, feats, skills, etc.
