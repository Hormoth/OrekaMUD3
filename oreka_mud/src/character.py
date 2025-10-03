import random



from enum import Enum
# from oreka_mud.src.combat import attack  # Removed unused import
from oreka_mud.src.classes import CLASSES
from oreka_mud.src.spells import get_spells_for_class

COLOR_TAGS = {
    "@RESET@": "\033[0m",
    "@BOLD@": "\033[1m",
    "@RED@": "\033[31m",
    "@GREEN@": "\033[32m",
    "@YELLOW@": "\033[33m",
    "@BLUE@": "\033[34m",
    "@CYAN@": "\033[36m",
    # Add more as needed
}

def apply_color_tags(text):
    for tag, code in COLOR_TAGS.items():
        text = text.replace(tag, code)
    return text

class State(Enum):
    EXPLORING = 1
    COMBAT = 2

class Character:
    SKILL_ABILITY = {
        "Climb": "str_score",
        "Survival": "wis_score",
        "Handle Animal": "cha_score",
        "Intimidate": "cha_score",
        "Jump": "str_score",
        "Listen": "wis_score",
        "Ride": "dex_score",
        "Swim": "str_score",
        "Balance": "dex_score",
        "Spellcraft": "int_score",
        "Diplomacy": "cha_score",
        "Sense Motive": "wis_score",
        "Use Rope": "dex_score",
        "Escape Artist": "dex_score",
        "Search": "int_score",
        # ...add more as needed...
    }
    SKILL_SYNERGY = {
        "Bluff": ["Diplomacy"],
        "Tumble": ["Balance"],
        "Handle Animal": ["Ride"],
        "Knowledge (arcana)": ["Spellcraft"],
        "Escape Artist": ["Use Rope"],
        "Search": ["Survival"],
        "Diplomacy": ["Sense Motive"],
        # ...add more as needed...
    }
    SKILL_UNTRAINED = {
        "Climb": True,
        "Survival": True,
        "Handle Animal": False,
        "Intimidate": True,
        "Jump": True,
        "Listen": True,
        "Ride": True,
        "Swim": True,
        "Balance": True,
        "Spellcraft": False,
        "Diplomacy": True,
        "Sense Motive": True,
        "Use Rope": True,
        "Escape Artist": True,
        "Search": True,
        # ...add more as needed...
    }

    def __init__(self, name, title, race, level, hp, max_hp, ac, room, is_immortal=False, elemental_affinity=None,
                 str_score=10, dex_score=10, con_score=10, int_score=10, wis_score=10, cha_score=10,
                 move=100, max_move=100, inventory=None, skills=None,
                 char_class="Adventurer", class_level=None, class_features=None, spells_known=None, spells_per_day=None,
                 alignment=None, deity=None, feats=None, domains=None, is_builder=False, password=None):
        self.name = name
        self.title = title
        self.race = race
        self.level = level
        self.hp = hp
        self.max_hp = max_hp
        self.ac = ac
        self.room = room
        self.quests = []
        self.state = State.EXPLORING
        self.is_ai = False
        self.is_immortal = is_immortal
        self.elemental_affinity = elemental_affinity
        self.str_score = str_score
        self.dex_score = dex_score
        self.con_score = con_score
        self.int_score = int_score
        self.wis_score = wis_score
        self.cha_score = cha_score
        self.move = move
        self.max_move = max_move
        self.xp = 0  # Current experience points
        self.show_all = False
        self.inventory = inventory or []  # List of Item objects
        self.skills = skills or {}
        self.char_class = char_class
        self.class_level = class_level if class_level is not None else level
        self.class_features = class_features if class_features is not None else []
        self.spells_known = spells_known if spells_known is not None else self._auto_spells_known()
        self.spells_per_day = spells_per_day if spells_per_day is not None else self._auto_spells_per_day()
        self.alignment = alignment
        self.deity = deity
        self.feats = feats if feats is not None else []
        self.domains = domains if domains is not None else []
        self.domain_powers = {}
        self.domain_spells = {}
        self.is_builder = is_builder
        self.password = password
        self._init_domains()
        # Barbarian mechanics
        self.raging = False  # Barbarian rage state
        self.fast_movement = False  # Barbarian fast movement state
        self.damage_reduction = 0  # Barbarian DR
        self.trap_sense = 0  # Barbarian trap sense bonus
        self.uncanny_dodge = False  # Barbarian uncanny dodge state
        self.rages_used_today = 0  # Barbarian rages used today
        self.fatigued = False  # Fatigue state after rage
        self.illiterate = (self.char_class.lower() == "barbarian")
        self.conditions = set()
        self.prompt = "AC %a HP %h/%H [%RACE] >"  # Default prompt
        self.full_prompt = "(%RACE): AC %a HP %h/%H EXP %x Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>" if self.is_immortal else "AC %a HP %h/%H EXP %x Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>"
    # ...all your other methods, properly indented as shown above...
    # For example:
    def get_equipped_armor_type(self):
        for item in self.inventory:
            if getattr(item, 'item_type', None) == 'armor' and getattr(item, 'slot', None) == 'body':
                armor_type = item.stats.get('armor_type', 'light') if hasattr(item, 'stats') else 'light'
                return armor_type
        return 'none'

    # Continue with all other methods as you have them, indented inside the class.

    def get_rages_per_day(self):
        """Return number of rages per day based on level."""
        if self.char_class.lower() != "barbarian":
            return 0
        lvl = self.class_level
        if lvl >= 20:
            return 6
        elif lvl >= 16:
            return 5
        elif lvl >= 12:
            return 4
        elif lvl >= 8:
            return 3
        elif lvl >= 4:
            return 2
        else:
            return 1

    def has_greater_rage(self):
        return self.char_class.lower() == "barbarian" and self.class_level >= 11

    def has_tireless_rage(self):
        return self.char_class.lower() == "barbarian" and self.class_level >= 17

    def has_mighty_rage(self):
        return self.char_class.lower() == "barbarian" and self.class_level >= 20

    def activate_rage(self):
        """Activate Barbarian Rage with upgrades and per-day limits."""
        if self.char_class.lower() != "barbarian":
            return "You are not a Barbarian."
        armor_type = self.get_equipped_armor_type()
        if armor_type in ('medium', 'heavy'):
            return "You cannot rage while wearing medium or heavy armor."
        if self.raging:
            return "You are already raging!"
        if self.rages_used_today >= self.get_rages_per_day():
            return f"You have used all your rages for today ({self.get_rages_per_day()})."
        # Determine rage bonuses
        str_bonus = 4
        con_bonus = 4
        ac_penalty = 2
        if self.has_greater_rage():
            str_bonus = 6
            con_bonus = 6
            ac_penalty = 2
        if self.has_mighty_rage():
            str_bonus = 8
            con_bonus = 8
            ac_penalty = 2
        self.raging = True
        self.str_score += str_bonus
        self.con_score += con_bonus
        self.ac -= ac_penalty
        self.max_hp += con_bonus * self.level // 2
        self.hp += con_bonus * self.level // 2
        self.rages_used_today += 1
        self.fatigued = False
        return f"You fly into a rage! (+{str_bonus} Str, +{con_bonus} Con, -{ac_penalty} AC, +HP)"

    def deactivate_rage(self):
        """Deactivate Barbarian Rage and apply fatigue if needed."""
        if not self.raging:
            return "You are not raging."
        # Determine rage bonuses
        str_bonus = 4
        con_bonus = 4
        ac_penalty = 2
        if self.has_greater_rage():
            str_bonus = 6
            con_bonus = 6
            ac_penalty = 2
        if self.has_mighty_rage():
            str_bonus = 8
            con_bonus = 8
            ac_penalty = 2
        self.raging = False
        self.str_score -= str_bonus
        self.con_score -= con_bonus
        self.ac += ac_penalty
        self.max_hp -= con_bonus * self.level // 2
        self.hp = min(self.hp, self.max_hp)
        # Apply fatigue unless Tireless Rage
        if not self.has_tireless_rage():
            self.fatigued = True
            return "You calm down and become fatigued after rage."
        else:
            self.fatigued = False
            return "You calm down and feel no fatigue (Tireless Rage)."

    def rest(self):
        """Rest to reset rages used and remove fatigue."""
        self.rages_used_today = 0
        self.fatigued = False
        return "You rest and recover your strength."

    def update_barbarian_features(self):
        """Update Barbarian features based on level."""
        if self.char_class.lower() != "barbarian":
            return
        armor_type = self.get_equipped_armor_type()
        self.fast_movement = self.class_level >= 1 and armor_type == 'light'
        # Fast Movement also increases initiative by 1
        if self.fast_movement:
            self.initiative_bonus = getattr(self, 'initiative_bonus', 0) + 1
        else:
            self.initiative_bonus = getattr(self, 'initiative_bonus', 0)
    def get_initiative(self):
        # Returns initiative modifier including Fast Movement bonus
        base = (self.dex_score - 10) // 2
        bonus = getattr(self, 'initiative_bonus', 0)
        return base + bonus
    # Damage Reduction, Trap Sense, and Uncanny Dodge are updated in update_barbarian_features

    def get_damage_reduction(self):
        return self.damage_reduction if self.char_class.lower() == "barbarian" else 0

    def get_trap_sense(self):
        return self.trap_sense if self.char_class.lower() == "barbarian" else 0

    def has_uncanny_dodge(self):
        return self.char_class.lower() == "barbarian" and self.class_level >= 2

    def has_improved_uncanny_dodge(self):
        return self.char_class.lower() == "barbarian" and self.class_level >= 5

    def is_flat_footed(self):
        # If Uncanny Dodge, cannot be caught flat-footed except by rogues 4+ levels higher
        if self.has_uncanny_dodge():
            return False
        # ...existing flat-footed logic...
        return True

    def is_immune_to_sneak_attack(self, attacker_level=None):
        # If Improved Uncanny Dodge, immune to sneak attack except by rogues 4+ levels higher
        if self.has_improved_uncanny_dodge():
            if attacker_level is not None and attacker_level >= self.class_level + 4:
                return False
            return True
        return False

    def apply_damage_reduction(self, damage):
        # Subtract DR from incoming physical damage
        dr = self.get_damage_reduction()
        return max(0, damage - dr)

    def get_trap_sense_bonus(self):
        # Bonus to Reflex saves and AC vs traps
        return self.trap_sense if self.char_class.lower() == "barbarian" else 0

    def get_indomitable_will_bonus(self, effect_type=None):
        # Bonus on Will saves vs enchantments
        if self.char_class.lower() == "barbarian" and self.class_level >= 14 and effect_type == "enchantment":
            return 4
        return 0
    def save(self):
        import os, json, shutil, glob, datetime
        player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
        os.makedirs(player_dir, exist_ok=True)
        filename = os.path.join(player_dir, f"{self.name.lower()}.json")
        # Remove old backups
        for old in glob.glob(os.path.join(player_dir, f"{self.name.lower()}.*.bak.json")):
            os.remove(old)
        # Create new backup if file exists
        if os.path.exists(filename):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = os.path.join(player_dir, f"{self.name.lower()}.{timestamp}.bak.json")
            shutil.copy2(filename, backup_name)
        # Atomic save
        tmpfile = filename + ".tmp"
        with open(tmpfile, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        os.replace(tmpfile, filename)

    @classmethod
    def rollback(cls, name, timestamp=None):
        """Restore a player file from the most recent or specified backup."""
        import os, shutil, glob
        player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
        base = os.path.join(player_dir, f"{name.lower()}.json")
        pattern = os.path.join(player_dir, f"{name.lower()}.*.bak.json")
        backups = sorted(glob.glob(pattern), reverse=True)
        if not backups:
            raise FileNotFoundError(f"No backups found for {name}.")
        if timestamp:
            match = [b for b in backups if timestamp in b]
            if not match:
                raise FileNotFoundError(f"No backup for {name} with timestamp {timestamp}.")
            backup = match[0]
        else:
            backup = backups[0]
        shutil.copy2(backup, base)
        return base
    def prepare_spells(self, new_prepared):
        """
        Set the character's prepared spells (for classes that prepare spells).
        Only allowed during rest or explicit preparation phase.
        """
        # new_prepared: dict of level -> list of spell names
        self.prepared_spells = new_prepared
        # Optionally reset spells_per_day to max for each level
        for lvl in self.spells_per_day:
            self.spells_per_day[lvl] = len(new_prepared.get(lvl, []))

    def can_cast_verbal(self):
        # Returns False if character is silenced, gagged, etc.
        return not (self.has_condition('silenced') or self.has_condition('gagged'))

    def can_cast_somatic(self):
        # Returns False if character is paralyzed, bound, or both hands full
        return not (self.has_condition('paralyzed') or self.has_condition('bound'))

    def was_interrupted(self):
        # Returns True if the character was hit this round while casting
        return getattr(self, 'interrupted', False)

    def clear_interrupted(self):
        self.interrupted = False

    def set_interrupted(self):
        self.interrupted = True

    async def grant_bonus_feat(self, writer, reader):
        """
        Grant a bonus feat to the character (for level-up or class feature).
        Prompts the user for eligible feats.
        """
        from oreka_mud.src.feats import list_eligible_feats
        eligible = list_eligible_feats(self)
        if not eligible:
            return None
        writer.write(b"\nYou may select a Bonus Feat!\n")
        for i, fname in enumerate(eligible, 1):
            writer.write(f"  {i}. {fname}\n".encode())
        writer.write(b"Enter choice: ")
        data = await reader.read(10)
        try:
            idx = int(data.decode().strip())
            if 1 <= idx <= len(eligible):
                chosen = eligible[idx-1]
            else:
                chosen = eligible[0]
        except Exception:
            chosen = eligible[0]
        if not hasattr(self, 'feats'):
            self.feats = []
        self.feats.append(chosen)
        return chosen

    async def check_levelup_bonus_feat(self, writer, reader):
        """
        Check if this level grants a Bonus Feat and prompt the user if so.
        """
        class_data = self.get_class_data()
        features = class_data.get("features", {})
        for lvl, feats in features.items():
            if lvl == self.class_level and any("Bonus Feat" in f for f in feats):
                return await self.grant_bonus_feat(writer, reader)
        return None
    def get_skill(self, skill):
        value = self.skills.get(skill, 0) if hasattr(self, 'skills') else 0
        from oreka_mud.src.feats import FEATS
        # Always check Acrobatic, Agile, Alertness for their skills
        for feat_name in getattr(self, 'feats', []):
            feat = FEATS.get(feat_name)
            if feat and feat.effect:
                value = feat.apply(self, skill=skill, value=value)
        # Passive check for Acrobatic, Agile, Alertness even if not in feats (for futureproofing)
        for passive in ("Acrobatic", "Agile", "Alertness"):
            if passive in getattr(self, 'feats', []):
                feat = FEATS.get(passive)
                if feat and feat.effect:
                    value = feat.apply(self, skill=skill, value=value)
        return value

    def get_save(self, save):
        value = self.saves.get(save, 0) if hasattr(self, 'saves') else 0
        from oreka_mud.src.feats import FEATS
        for feat_name in getattr(self, 'feats', []):
            feat = FEATS.get(feat_name)
            if feat and feat.effect:
                value = feat.apply(self, save=save, value=value)
        return value
    def _auto_spells_known(self):
        """Auto-populate spells known for spellcasting classes."""
        if self.char_class in ("Wizard", "Sorcerer", "Bard", "Cleric", "Paladin", "Ranger"):
            spells = get_spells_for_class(self.char_class, self.class_level)
            return {spell["name"]: spell for spell in spells}
        return {}

    def _auto_spells_per_day(self):
        """Auto-populate spells per day for spellcasting classes (placeholder logic)."""
        if self.char_class in ("Wizard", "Sorcerer", "Bard", "Cleric", "Paladin", "Ranger"):
            spells = get_spells_for_class(self.char_class, self.class_level)
            per_day = {}
            for spell in spells:
                lvl = spell["level"][self.char_class]
                per_day[lvl] = per_day.get(lvl, 0) + 1
            return {lvl: 1 for lvl in per_day}
        return {}
    def get_class_data(self):
        return CLASSES.get(self.char_class, {})

    def get_class_skills(self):
        class_data = self.get_class_data()
        return class_data.get("class_skills", [])

def get_class_features(self):
    class_data = self.get_class_data()
    features = []
    for lvl in sorted(class_data.get("features", {})):
        if self.class_level >= lvl:
            features.extend(class_data["features"][lvl])
    return features

def get_spellcasting_info(self):
    class_data = self.get_class_data()
    return class_data.get("spellcasting", None)

def to_dict(self):
    return {
        "name": self.name,
        "hashed_password": getattr(self, "hashed_password", None),  # Always save hash!
        "title": self.title,
        "race": self.race,
        "level": self.level,
        "char_class": self.char_class,
        "class_level": self.class_level,
        "class_features": self.class_features,
        "spells_known": getattr(self, 'spells_known', {}),
        "spells_per_day": getattr(self, 'spells_per_day', {}),
        "hp": self.hp,
        "max_hp": self.max_hp,
        "ac": self.ac,
        "room_vnum": self.room.vnum if self.room else None,
        "quests": self.quests,
        "state": self.state.name if hasattr(self.state, 'name') else self.state,
        "is_ai": self.is_ai,
        "is_immortal": self.is_immortal,
        "elemental_affinity": self.elemental_affinity,
        "str_score": self.str_score,
        "dex_score": self.dex_score,
        "con_score": self.con_score,
        "int_score": self.int_score,
        "wis_score": self.wis_score,
        "cha_score": self.cha_score,
        "move": self.move,
        "max_move": self.max_move,
        "xp": self.xp,
        "show_all": self.show_all,
        "inventory": [item.to_dict() for item in self.inventory],
        "alignment": getattr(self, 'alignment', None),
        "deity": getattr(self, 'deity', None),
        "is_builder": getattr(self, 'is_builder', False),
    }

@staticmethod
def from_dict(data):
    import os
    import time
    from oreka_mud.src.items import Item
    lock_acquired = False
    lock_path = None
    if hasattr(data, '_file_path'):
        lock_path = data._file_path + '.lock'
        for _ in range(20):  # Try for up to 2 seconds
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                lock_acquired = True
                break
            except FileExistsError:
                time.sleep(0.1)
    char = None
    try:
        char = Character(
            name=data["name"],
            title=data.get("title"),
            race=data.get("race"),
            level=data.get("level", 1),
            hp=data.get("hp", 10),
            max_hp=data.get("max_hp", 10),
            ac=data.get("ac", 10),
            room=None,
            is_immortal=data.get("is_immortal", False),
            elemental_affinity=data.get("elemental_affinity"),
            str_score=data.get("str_score", 10),
            dex_score=data.get("dex_score", 10),
            con_score=data.get("con_score", 10),
            int_score=data.get("int_score", 10),
            wis_score=data.get("wis_score", 10),
            cha_score=data.get("cha_score", 10),
            move=data.get("move", 100),
            max_move=data.get("max_move", 100),
            inventory=[Item.from_dict(i) for i in data.get("inventory", [])],
            is_builder=data.get("is_builder", False)
        )
        char.hashed_password = data.get("hashed_password")  # <-- Load hash!
        char.char_class = data.get("char_class", "Adventurer")
        char.class_level = data.get("class_level", data.get("level", 1))
        char.class_features = data.get("class_features", [])
        char.spells_known = data.get("spells_known", {})
        char.spells_per_day = data.get("spells_per_day", {})
        char.quests = data.get("quests", [])
        char.state = State[data.get("state", "EXPLORING")]
        char.is_ai = data.get("is_ai", False)
        char.xp = data.get("xp", 0)
        char.show_all = data.get("show_all", False)
        char.alignment = data.get("alignment")
        char.deity = data.get("deity")
        char.is_builder = data.get("is_builder", False)
        char._init_domains()
    finally:
        if lock_acquired and lock_path:
            try:
                os.remove(lock_path)
            except Exception:
                pass
    return char

def _init_domains(self):
    """Initialize domain powers and domain spells for this character."""
    # Import a DOMAIN_DATA dict: domain_name -> {"powers": str/callable, "spells": {level: spell_name}}
    try:
        from oreka_mud.src.spells import DOMAIN_DATA
    except ImportError:
        DOMAIN_DATA = {}
    for domain in self.domains:
        data = DOMAIN_DATA.get(domain)
        if not data:
            continue
        self.domain_powers[domain] = data.get("power")
        for lvl, spell in data.get("spells", {}).items():
            if lvl not in self.domain_spells:
                self.domain_spells[lvl] = set()
            self.domain_spells[lvl].add(spell)

def get_available_domain_spells(self):
    """Return a dict of spell_level -> set of domain spells available at current spellcasting level."""
    # Only include domain spells for levels the character can cast
    available = {}
    max_spell_level = self.get_max_spell_level()
    for lvl, spells in self.domain_spells.items():
        if int(lvl) <= max_spell_level:
            available[lvl] = spells
    return available

def get_max_spell_level(self):
    """Return the highest spell level the character can cast (based on class_level and class)."""
    # This is a placeholder; real logic should use class spell progression tables
    # For Cleric: 1st at 1, 2nd at 3, 3rd at 5, 4th at 7, 5th at 9, 6th at 11, 7th at 13, 8th at 15, 9th at 17
    if self.char_class == "Cleric":
        return min(9, (self.class_level + 1) // 2)
    # Add other classes as needed
    return 0

def set_class(self, new_class):
    self.char_class = new_class
    self.class_features = self.get_class_features()
    self.spells_known = self._auto_spells_known()
    self.spells_per_day = self._auto_spells_per_day()

    def set_level(self, new_level):
        self.class_level = new_level
        self.class_features = self.get_class_features()
        self.spells_known = self._auto_spells_known()
        self.spells_per_day = self._auto_spells_per_day()
        self.prompt = "(%RACE): AC %a HP %h/%H EXP %x>" if self.is_immortal else "AC %a HP %h/%H EXP %x>"
        self.full_prompt = "(%RACE): AC %a HP %h/%H EXP %x Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>" if self.is_immortal else "AC %a HP %h/%H EXP %x Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>"

        # D&D 3.5e: Grant general feat at 1, 3, 6, 9, 12, 15, 18
        if new_level in (1, 3, 6, 9, 12, 15, 18):
            if hasattr(self, 'grant_general_feat'):
                # If async context, schedule prompt, else just append placeholder
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    coro = self.grant_general_feat(self.writer, self.reader)
                    if loop.is_running():
                        asyncio.ensure_future(coro)
                    else:
                        loop.run_until_complete(coro)
                except Exception:
                    self.feats.append("General Feat (choose)")
            else:
                self.feats.append("General Feat (choose)")

        # D&D 3.5e: Ability score increase at 4, 8, 12, 16, 20
        if new_level in (4, 8, 12, 16, 20):
            if hasattr(self, 'grant_ability_increase'):
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    coro = self.grant_ability_increase(self.writer, self.reader)
                    if loop.is_running():
                        asyncio.ensure_future(coro)
                    else:
                        loop.run_until_complete(coro)
                except Exception:
                    self.feats.append("Ability Score Increase (choose)")
            else:
                self.feats.append("Ability Score Increase (choose)")

        # Notify player of new class features gained at this level (Barbarian)
        from oreka_mud.src.classes import CLASSES
        if self.char_class == "Barbarian":
            class_data = CLASSES.get("Barbarian", {})
            features = class_data.get("features", {})
            gained = features.get(new_level, [])
            if gained:
                msg = f"\nCongratulations! As a Barbarian, you have gained the following at level {new_level}:\n  - " + "\n  - ".join(gained) + "\n"
                if hasattr(self, "writer") and self.writer:
                    try:
                        self.writer.write(msg.encode())
                    except Exception:
                        print(msg)
                else:
                    print(msg)

        # Notify player of new class features gained at this level (Bard)
        if self.char_class == "Bard":
            class_data = CLASSES.get("Bard", {})
            features = class_data.get("features", {})
            gained = features.get(new_level, [])
            if gained:
                msg = f"\nCongratulations! As a Bard, you have gained the following at level {new_level}:\n  - " + "\n  - ".join(gained) + "\n"
                if hasattr(self, "writer") and self.writer:
                    try:
                        self.writer.write(msg.encode())
                    except Exception:
                        print(msg)
                else:
                    print(msg)

        # D&D 3.5e: Grant general feat at 1, 3, 6, 9, 12, 15, 18
        if new_level in (1, 3, 6, 9, 12, 15, 18):
            if hasattr(self, 'grant_general_feat'):
                # If async context, schedule prompt, else just append placeholder
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    coro = self.grant_general_feat(self.writer, self.reader)
                    if loop.is_running():
                        asyncio.ensure_future(coro)
                    else:
                        loop.run_until_complete(coro)
                except Exception:
                    # Fallback: just append placeholder
                    self.feats.append("General Feat (choose)")
            else:
                self.feats.append("General Feat (choose)")

        # D&D 3.5e: Ability score increase at 4, 8, 12, 16, 20
        if new_level in (4, 8, 12, 16, 20):
            if hasattr(self, 'grant_ability_increase'):
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    coro = self.grant_ability_increase(self.writer, self.reader)
                    if loop.is_running():
                        asyncio.ensure_future(coro)
                    else:
                        loop.run_until_complete(coro)
                except Exception:
                    self.feats.append("Ability Score Increase (choose)")
            else:
                self.feats.append("Ability Score Increase (choose)")

        # Report ability scores on level up
        if hasattr(self, 'writer') and self.writer:
            msg = (
                f"\nYou have reached level {new_level}!\n"
                f"Current Ability Scores:\n"
                f"  Strength:     {self.str_score}\n"
                f"  Dexterity:    {self.dex_score}\n"
                f"  Constitution: {self.con_score}\n"
                f"  Intelligence: {self.int_score}\n"
                f"  Wisdom:       {self.wis_score}\n"
                f"  Charisma:     {self.cha_score}\n"
            )
            self.writer.write(msg.encode())

        # Notify player of new class features gained at this level (Barbarian)
        from oreka_mud.src.classes import CLASSES
        if self.char_class == "Barbarian":
            class_data = CLASSES.get("Barbarian", {})
            features = class_data.get("features", {})
            gained = features.get(new_level, [])
            if gained:
                msg = f"\nCongratulations! As a Barbarian, you have gained the following at level {new_level}:\n  - " + "\n  - ".join(gained) + "\n"
                if hasattr(self, "writer") and self.writer:
                    try:
                        self.writer.write(msg.encode())
                    except Exception:
                        print(msg)
                else:
                    print(msg)

            # Notify player of new class features gained at this level (Bard)
            if self.char_class == "Bard":
                class_data = CLASSES.get("Bard", {})
                features = class_data.get("features", {})
                gained = features.get(new_level, [])
                if gained:
                    msg = f"\nCongratulations! As a Bard, you have gained the following at level {new_level}:\n  - " + "\n  - ".join(gained) + "\n"
                    if hasattr(self, "writer") and self.writer:
                        try:
                            self.writer.write(msg.encode())
                        except Exception:
                            print(msg)
                    else:
                        print(msg)
        
        # Removed unreachable nested skill_check function.

    def add_condition(self, condition):
        """Add a status condition (e.g., 'prone', 'flanking', 'shaken')."""
        self.conditions.add(condition)

    def remove_condition(self, condition):
        """Remove a status condition."""
        self.conditions.discard(condition)

    def has_condition(self, condition):
        """Check if the character has a given condition."""
        return condition in self.conditions

    def render_prompt(self):
        prompt = self.prompt
        prompt = prompt.replace("%a", str(self.ac))
        prompt = prompt.replace("%h", str(self.hp))
        prompt = prompt.replace("%H", str(self.max_hp))
        prompt = prompt.replace("%RACE", self.race or "Unknown")
        # Add more codes as needed
        return prompt

    def get_prompt(self):
        """Return the current prompt string for the character."""
        return self.render_prompt()

    def set_prompt(self, new_prompt):
        self.prompt = new_prompt

    def learn_literacy(self):
        self.illiterate = False

    def can_read(self, file_type=None):
        """Return True if character can read. Barbarians can always read help files."""
        if not self.illiterate:
            return True
        if file_type == "help":
            return True
        return False

    def is_fatigued(self):
        return getattr(self, 'fatigued', False)

    def apply_fatigue_penalties(self):
        """Apply fatigue penalties: -2 Str/Dex, block running/charging."""
        if self.is_fatigued():
            self.str_score = max(1, self.str_score - 2)
            self.dex_score = max(1, self.dex_score - 2)
            self.can_run = False
            self.can_charge = False
        else:
            # Restore running/charging ability if not fatigued
            self.can_run = True
            self.can_charge = True

    def get_max_skill_rank(self, skill):
        # Class skills: level + 3; cross-class: (level + 3) / 2
        class_skills = getattr(self, 'class_skills', [])
        if skill in class_skills:
            return self.class_level + 3
        return (self.class_level + 3) // 2

    def skill_cost(self, skill):
        # Class skill: 1 point/rank; cross-class: 2 points/rank
        class_skills = getattr(self, 'class_skills', [])
        return 1 if skill in class_skills else 2

    def skill_check(self, skill, dc=15):
        # Untrained use check
        if not self.SKILL_UNTRAINED.get(skill, True) and self.skills.get(skill, 0) < 1:
            return "You cannot use this skill untrained."
        ranks = self.skills.get(skill, 0)
        ability_mod = getattr(self, self.SKILL_ABILITY.get(skill, "int_score"), 0)
        # Synergy bonuses
        synergy_bonus = 0
        for synergy_skill, targets in self.SKILL_SYNERGY.items():
            if ranks >= 5 and skill in targets:
                synergy_bonus += 2
        # Check if any other skills grant synergy to this skill
        for s, r in self.skills.items():
            if r >= 5:
                for target in self.SKILL_SYNERGY.get(s, []):
                    if target == skill:
                        synergy_bonus += 2
        # Feat, racial, magic, condition modifiers (stub)
        feat_bonus = 0  # TODO: Add feat/race/magic/condition bonuses
        roll = random.randint(1, 20)
        total = roll + ranks + (ability_mod - 10) // 2 + synergy_bonus + feat_bonus
        result = f"Skill check: d20({roll}) + ranks({ranks}) + ability({(ability_mod - 10) // 2}) + synergy({synergy_bonus}) + feat({feat_bonus}) = {total}"
        if total >= dc:
            return result + f"\nSuccess! (DC {dc})"
        else:
            return result + f"\nFailure. (DC {dc})"

    def get_class_skills(self):
        if self.char_class == "Cleric":
            return CLASSES["Cleric"]["class_skills"]
        # ...other classes...
