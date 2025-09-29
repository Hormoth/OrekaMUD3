
from enum import Enum
from src.combat import attack
from src.classes import CLASSES
from src.spells import get_spells_for_class

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
    def __init__(self, name, title, race, level, hp, max_hp, ac, room, is_immortal=False, elemental_affinity=None,
                 str_score=10, dex_score=10, con_score=10, int_score=10, wis_score=10, cha_score=10,
                 move=100, max_move=100, inventory=None, skills=None,
                 char_class="Adventurer", class_level=None, class_features=None, spells_known=None, spells_per_day=None,
                 alignment=None, deity=None, feats=None, domains=None, is_builder=False):
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
        # Always initialize prompt and full_prompt
        self.prompt = "AC %a HP %h/%H [%RACE] >"  # Default prompt
        self.full_prompt = "(%RACE): AC %a HP %h/%H EXP %x Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>" if self.is_immortal else "AC %a HP %h/%H EXP %x Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>"
        self.conditions = set()  # Track status effects/conditions (e.g., 'prone', 'flanking', 'shaken')
        self.feats = feats if feats is not None else []  # Accept feats from constructor or default to empty list
        self.domains = domains if domains is not None else []  # List of domain names (e.g., ["War", "Sun"])
        self.domain_powers = {}  # domain_name -> granted power description or callable
        self.domain_spells = {}  # spell_level -> set of domain spell names
        self.is_builder = is_builder
        self._init_domains()
    def save(self):
        """Save this character to a JSON file in data/players/ by name (lowercase), with backup."""
        import os, json, shutil, datetime
        player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
        os.makedirs(player_dir, exist_ok=True)
        filename = os.path.join(player_dir, f"{self.name.lower()}.json")
        # Backup existing file if it exists
        if os.path.exists(filename):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = os.path.join(player_dir, f"{self.name.lower()}.{timestamp}.bak.json")
            shutil.copy2(filename, backup_name)
        # Atomic save: write to temp, then move
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
        from src.feats import list_eligible_feats
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
        from src.feats import FEATS
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
        from src.feats import FEATS
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
    def from_dict(data, world=None):
        import os
        import time
        from src.items import Item
        # File locking: if loading from a file, try to acquire a lock
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
        try:
            char = Character(
                name=data["name"],
                title=data.get("title"),
                race=data.get("race"),
                level=data.get("level", 1),
                hp=data.get("hp", 10),
                max_hp=data.get("max_hp", 10),
                ac=data.get("ac", 10),
                room=None,  # Set after loading
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
        finally:
            if lock_acquired and lock_path:
                try:
                    os.remove(lock_path)
                except Exception:
                    pass

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
        return char

    def _init_domains(self):
        """Initialize domain powers and domain spells for this character."""
        # Import a DOMAIN_DATA dict: domain_name -> {"powers": str/callable, "spells": {level: spell_name}}
        try:
            from src.spells import DOMAIN_DATA
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
        old_level = getattr(self, 'class_level', 1)
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

    def skill_check(self, skill, bonus=0):
        import random
        # D&D 3.5: Skills that cannot be used untrained
        trained_only = {
            "Decipher Script", "Disable Device", "Handle Animal", "Knowledge (arcana)", "Knowledge (architecture and engineering)",
            "Knowledge (dungeoneering)", "Knowledge (geography)", "Knowledge (history)", "Knowledge (local)", "Knowledge (nature)",
            "Knowledge (nobility and royalty)", "Knowledge (religion)", "Knowledge (the planes)", "Profession (any)", "Sleight of Hand", "Spellcraft", "Tumble", "Use Magic Device"
        }
        # Skills with armor check penalty
        armor_check_skills = {
            "Balance", "Climb", "Escape Artist", "Hide", "Jump", "Move Silently", "Sleight of Hand", "Swim", "Tumble"
        }
        # Ability modifier mapping
        ability_mods = {
            "Appraise": (self.int_score - 10) // 2,
            "Balance": (self.dex_score - 10) // 2,
            "Bluff": (self.cha_score - 10) // 2,
            "Climb": (self.str_score - 10) // 2,
            "Concentration": (self.con_score - 10) // 2,
            "Craft (any)": (self.int_score - 10) // 2,
            "Decipher Script": (self.int_score - 10) // 2,
            "Diplomacy": (self.cha_score - 10) // 2,
            "Disable Device": (self.int_score - 10) // 2,
            "Disguise": (self.cha_score - 10) // 2,
            "Escape Artist": (self.dex_score - 10) // 2,
            "Forgery": (self.int_score - 10) // 2,
            "Gather Information": (self.cha_score - 10) // 2,
            "Handle Animal": (self.cha_score - 10) // 2,
            "Heal": (self.wis_score - 10) // 2,
            "Hide": (self.dex_score - 10) // 2,
            "Intimidate": (self.cha_score - 10) // 2,
            "Jump": (self.str_score - 10) // 2,
            "Knowledge (arcana)": (self.int_score - 10) // 2,
            "Knowledge (architecture and engineering)": (self.int_score - 10) // 2,
            "Knowledge (dungeoneering)": (self.int_score - 10) // 2,
            "Knowledge (geography)": (self.int_score - 10) // 2,
            "Knowledge (history)": (self.int_score - 10) // 2,
            "Knowledge (local)": (self.int_score - 10) // 2,
            "Knowledge (nature)": (self.int_score - 10) // 2,
            "Knowledge (nobility and royalty)": (self.int_score - 10) // 2,
            "Knowledge (religion)": (self.int_score - 10) // 2,
            "Knowledge (the planes)": (self.int_score - 10) // 2,
            "Listen": (self.wis_score - 10) // 2,
            "Move Silently": (self.dex_score - 10) // 2,
            "Open Lock": (self.dex_score - 10) // 2,
            "Perform (any)": (self.cha_score - 10) // 2,
            "Profession (any)": (self.wis_score - 10) // 2,
            "Ride": (self.dex_score - 10) // 2,
            "Search": (self.int_score - 10) // 2,
            "Sense Motive": (self.wis_score - 10) // 2,
            "Sleight of Hand": (self.dex_score - 10) // 2,
            "Spellcraft": (self.int_score - 10) // 2,
            "Spot": (self.wis_score - 10) // 2,
            "Survival": (self.wis_score - 10) // 2,
            "Swim": (self.str_score - 10) // 2,
            "Tumble": (self.dex_score - 10) // 2,
            "Use Magic Device": (self.cha_score - 10) // 2,
            "Use Rope": (self.dex_score - 10) // 2
        }
        # Enforce trained-only skills
        skill_val = self.skills.get(skill, 0)
        if skill in trained_only and skill_val == 0:
            return f"You cannot use {skill} untrained."
        # Armor check penalty (stub: assumes self.armor_check_penalty exists, else 0)
        armor_penalty = getattr(self, 'armor_check_penalty', 0)
        penalty = armor_penalty if skill in armor_check_skills else 0
        roll = random.randint(1, 20)
        ability_mod = ability_mods.get(skill, 0)
        # Cross-class skill logic (stub):
        # In a full implementation, check if skill is in self.get_class_skills(),
        # and enforce max ranks/costs accordingly.
        return roll + skill_val + ability_mod + bonus - penalty

    def get_prompt(self):
        str_mod = (self.str_score - 10) // 2
        dex_mod = (self.dex_score - 10) // 2
        con_mod = (self.con_score - 10) // 2
        int_mod = (self.int_score - 10) // 2
        wis_mod = (self.wis_score - 10) // 2
        cha_mod = (self.cha_score - 10) // 2
        xp_to_next = max(0, {1: 1000, 2: 3000, 3: 6000, 4: 10000, 5: 15000, 6: 21000, 7: 28000, 60: 0}.get(self.level + 1, 0) - self.xp)
        if self.show_all:
            return self.full_prompt.replace("%a", str(self.ac)).replace("%h", str(self.hp)).replace("%H", str(self.max_hp)).replace("%x", str(xp_to_next)).replace("%v", str(self.move)).replace("%V", str(self.max_move)).replace("%s", f"{self.str_score} ({str_mod:+})").replace("%d", f"{self.dex_score} ({dex_mod:+})").replace("%c", f"{self.con_score} ({con_mod:+})").replace("%i", f"{self.int_score} ({int_mod:+})").replace("%w", f"{self.wis_score} ({wis_mod:+})").replace("%c", f"{self.cha_score} ({cha_mod:+})").replace("%RACE", self.race or "Unknown").replace("%s", " [Immortal]" if self.is_immortal else "")
        return self.prompt.replace("%a", str(self.ac)).replace("%h", str(self.hp)).replace("%H", str(self.max_hp)).replace("%x", str(xp_to_next)).replace("%RACE", self.race or "Unknown").replace("%s", " [Immortal]" if self.is_immortal else "")
    
    def toggle_stats(self):
        self.show_all = not self.show_all
        return f"Stats display {'enabled' if self.show_all else 'disabled'}.\n{self.get_prompt()}"

    async def ai_decide(self, world):
        if self.state == State.COMBAT:
            for mob in self.room.mobs:
                if mob.alive and self.hp > self.max_hp * 0.2:
                    return attack(self, mob)
                elif self.hp <= self.max_hp * 0.2:
                    self.state = State.EXPLORING
                    return "You flee from combat!"
        if self.quests and self.room.vnum == self.quests[0]["location"]:
            self.quests.clear()
            self.xp += 1000
            return "Quest completed: Starweave Ritual! +1000 XP"
        return self.get_prompt()

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

    def set_prompt(self, new_prompt):
        self.prompt = new_prompt
