import random
from .feats import get_feat

class Mob:
    def choose_dodge_target(self, combat_targets):
        """
        Dynamically select a Dodge target from current combatants.
        For player: prompt for selection. For AI: pick highest threat.
        """
        # For now, pick the first alive target (stub; expand for UI/AI logic)
        for t in combat_targets:
            if getattr(t, 'alive', True):
                self.set_dodge_target(getattr(t, 'vnum', None) or getattr(t, 'name', None))
                return t
        return None
    def to_dict(self):
        """Serialize mob for saving (exclude live state like conditions, alive, etc)."""
        return {
            "vnum": self.vnum,
            "name": self.name,
            "level": self.level,
            "hp_dice": getattr(self, 'hp_dice', [1, 8, 0]),
            "ac": self.ac,
            "damage_dice": self.damage_dice,
            "flags": self.flags,
            "type_": self.type_,
            "alignment": self.alignment,
            "ability_scores": self.ability_scores,
            "initiative": self.initiative,
            "speed": self.speed,
            "attacks": self.attacks,
            "special_attacks": self.special_attacks,
            "special_qualities": self.special_qualities,
            "feats": self.feats,
            "skills": self.skills,
            "saves": self.saves,
            "environment": self.environment,
            "organization": self.organization,
            "cr": self.cr,
            "advancement": self.advancement,
            "description": self.description,
            # Save room_vnum for placement
            "room_vnum": getattr(self, 'room_vnum', None)
        }
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
                 environment="", organization="", cr=None, advancement=None, description="",
                 shop_inventory=None, shop_type=None, buy_rate=1.0, sell_rate=1.0, dialogue=None, **kwargs):
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
        self.dodge_target = None  # For Dodge feat: vnum or name of target
        self.weapon_type = attacks[0]["type"] if attacks else None  # For Weapon Finesse/Focus
        self.aoo_count = 0  # Attacks of opportunity used this round
        self.power_attack_amt = 0  # Power Attack value for this round
        self.track_target = None  # For Track feat
        # Shopkeeper fields
        self.shop_inventory = shop_inventory or []  # List of item vnums
        self.shop_type = shop_type  # e.g., 'general', 'weapons', 'magic'
        self.buy_rate = buy_rate  # Multiplier for buying from player (e.g., 1.0 = 100% value)
        self.sell_rate = sell_rate  # Multiplier for selling to player (e.g., 1.0 = 100% value)
        self.dialogue = dialogue

    def is_shopkeeper(self):
        return 'shopkeeper' in (self.flags or []) or self.shop_inventory

    def get_shop_items(self):
        from .items import load_items_db
        db = load_items_db()
        return [db[vnum] for vnum in self.shop_inventory if vnum in db]

    def get_buy_price(self, item):
        # Price player pays to buy from shop
        return int(getattr(item, 'value', 0) * self.sell_rate)

    def get_sell_price(self, item):
        # Price shop pays to buy from player
        return int(getattr(item, 'value', 0) * self.buy_rate)

    def add_shop_item(self, item_vnum):
        if item_vnum not in self.shop_inventory:
            self.shop_inventory.append(item_vnum)

    def remove_shop_item(self, item_vnum):
        if item_vnum in self.shop_inventory:
            self.shop_inventory.remove(item_vnum)
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
        data = {
            "vnum": self.vnum,
            "name": self.name,
            "level": self.level,
            "hp_dice": getattr(self, 'hp_dice', [1, 8, 0]),
            "ac": self.ac,
            "damage_dice": self.damage_dice,
            "flags": self.flags,
            "type_": self.type_,
            "alignment": self.alignment,
            "ability_scores": self.ability_scores,
            "initiative": self.initiative,
            "speed": self.speed,
            "attacks": self.attacks,
            "special_attacks": self.special_attacks,
            "special_qualities": self.special_qualities,
            "feats": self.feats,
            "skills": self.skills,
            "saves": self.saves,
            "environment": self.environment,
            "organization": self.organization,
            "cr": self.cr,
            "advancement": self.advancement,
            "description": self.description,
            # Save room_vnum for placement
            "room_vnum": getattr(self, 'room_vnum', None)
        }
        # Shopkeeper fields
        if self.shop_inventory:
            data["shop_inventory"] = self.shop_inventory
        if self.shop_type:
            data["shop_type"] = self.shop_type
        if getattr(self, "buy_rate", None) is not None:
            data["buy_rate"] = self.buy_rate
        if getattr(self, "sell_rate", None) is not None:
            data["sell_rate"] = self.sell_rate
        if getattr(self, "dialogue", None):
            data["dialogue"] = self.dialogue
        return data
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
        # Base AC plus passive feat bonuses (Dodge, Mobility)
        ac = self.ac
        # Dodge: +1 AC vs chosen target (must be set via set_dodge_target or choose_dodge_target)
        if self.has_feat("Dodge") and attacker and (getattr(attacker, 'vnum', None) == self.dodge_target or getattr(attacker, 'name', None) == self.dodge_target):
            ac += 1
        # Mobility: +4 AC vs attacks of opportunity
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
    # (Removed duplicate __init__ definition. The above definition with shopkeeper fields and **kwargs is now the only one.)

    def add_condition(self, condition):
        self.conditions.add(condition)

    def remove_condition(self, condition):
        self.conditions.discard(condition)

    def has_condition(self, condition):
        return condition in self.conditions

    def attack(self, target, power_attack_amt=None, all_targets=None):
        # Attack logic with feat support (Power Attack, Weapon Finesse, Weapon Focus, Cleave, Great Cleave, Dodge, Combat Reflexes)
        roll = random.randint(1, 20)
        bab = (self.level * 3) // 4
        str_mod = (self.ability_scores.get("Str", 10) - 10) // 2
        dex_mod = (self.ability_scores.get("Dex", 10) - 10) // 2
        using_finesse = self.has_feat("Weapon Finesse") and self._is_finesse_weapon()
        stat_mod = dex_mod if using_finesse else str_mod
        attack_bonus = bab + stat_mod
        pa_amt = self.power_attack_amt if power_attack_amt is None else power_attack_amt
        if self.has_feat("Power Attack") and pa_amt > 0:
            attack_bonus -= pa_amt
        if self.has_feat("Weapon Focus"):
            for f in self.feats:
                if f.startswith("Weapon Focus"):
                    focus_type = f.split("(")[-1].rstrip(")")
                    if self.weapon_type and self.weapon_type in focus_type:
                        attack_bonus += 1
        ac = target.get_ac(attacker=self)
        if hasattr(target, 'is_flat_footed') and not target.is_flat_footed():
            pass
        if hasattr(target, 'is_immune_to_sneak_attack') and target.is_immune_to_sneak_attack(getattr(self, 'level', None)):
            sneak_attack = False
        else:
            sneak_attack = True
        # TODO: Add other feat/condition/skill modifiers
        if roll == 1:
            return "Miss!"
        if roll == 20 or roll + attack_bonus >= ac:
            damage = sum(random.randint(1, self.damage_dice[1]) for _ in range(self.damage_dice[0])) + self.damage_dice[2]
            if self.has_feat("Power Attack") and pa_amt > 0:
                damage += pa_amt
            if hasattr(target, 'apply_damage_reduction'):
                damage = target.apply_damage_reduction(damage)
            target.hp = max(0, target.hp - damage)
            result = f"{self.name} hits {target.name} for {damage} damage!"
            if target.hp == 0:
                target.alive = False
                result = f"{self.name} kills {target.name}!"
                # Cleave/Great Cleave logic
                if all_targets:
                    if self.has_feat("Great Cleave"):
                        # Great Cleave: keep attacking until no valid targets remain
                        remaining_targets = [t for t in all_targets if t is not target and getattr(t, 'alive', True)]
                        while remaining_targets:
                            next_target = remaining_targets.pop(0)
                            result += f" {self.name} great cleaves into {next_target.name}! "
                            result += self.attack(next_target, power_attack_amt=pa_amt, all_targets=[t for t in all_targets if t is not next_target and getattr(t, 'alive', True)])
                            # Update remaining_targets in case more are killed
                            remaining_targets = [t for t in all_targets if t is not target and getattr(t, 'alive', True)]
                    elif self.has_feat("Cleave"):
                        # Cleave: only one extra attack per kill
                        for t in all_targets:
                            if t is not target and getattr(t, 'alive', True):
                                result += f" {self.name} cleaves into {t.name}! "
                                result += self.attack(t, power_attack_amt=pa_amt, all_targets=None)
                                break
            return result
        return "Miss!"

    def _is_finesse_weapon(self):
        # Expanded check: treat all attacks with finesse weapon types as finesse weapons
        if not self.attacks:
            return False
        # Comprehensive D&D 3.5e finesse weapon list
        finesse_types = {
            "claw", "bite", "dagger", "rapier", "shortsword", "punch", "unarmed", "whip", "kukri", "spiked chain", "hand", "sickle", "light mace", "light hammer", "club", "nunchaku", "parrying dagger", "sap", "sai", "butterfly sword", "elven thinblade", "elven lightblade", "chain", "needle", "stiletto", "main-gauche", "jitte", "katana", "wakizashi"
        }
        # Check all attacks for finesse type
        for atk in self.attacks:
            if atk.get("type") in finesse_types:
                return True
        # Optionally, check for 'finesse' property in item/weapon data in future
        return False

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

    # Saving throw stubs for Trap Sense and Indomitable Will
    def saving_throw(self, save_type, dc, effect_type=None, is_trap=False):
        # Example: save_type = 'reflex', 'will', 'fortitude'
        bonus = 0
        if is_trap and hasattr(self, 'get_trap_sense_bonus'):
            bonus += self.get_trap_sense_bonus()
        if save_type == 'will' and hasattr(self, 'get_indomitable_will_bonus'):
            bonus += self.get_indomitable_will_bonus(effect_type)
        roll = random.randint(1, 20) + bonus
        return roll >= dc

# Weapon lists (abbreviated, expand as needed)
SIMPLE_WEAPONS = set([
    "club", "dagger", "heavy crossbow", "light crossbow", "quarterstaff", "shortspear", "spear", "mace", "sickle", "javelin", "morningstar", "sling", "staff", "light mace", "heavy mace", "dart", "greatclub", "handaxe", "light hammer", "light pick", "heavy pick", "scythe"
])
MARTIAL_WEAPONS = set([
    "longsword", "battleaxe", "warhammer", "scimitar", "falchion", "glaive", "greataxe", "greatsword", "halberd", "lance", "rapier", "sabre", "shortbow", "longbow", "trident", "whip", "flail", "heavy flail", "guisarme", "kukri", "net", "ranseur", "scimitar", "scythe", "sickle", "spiked chain"
])

# In attack() or equip logic, call self.is_weapon_proficient(weapon_name) and apply penalty or block if not.
    # Add more methods for special attacks, feats, skills, etc.
