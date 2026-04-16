
from enum import Enum
import random
from src.classes import CLASSES
from src.spells import get_spells_for_class
from src import conditions as cond

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

XP_TABLE = {
    1: 0, 2: 1000, 3: 3000, 4: 6000, 5: 10000, 6: 15000, 7: 21000,
    8: 28000, 9: 36000, 10: 45000, 11: 55000, 12: 66000, 13: 78000,
    14: 91000, 15: 105000, 16: 120000, 17: 136000, 18: 153000,
    19: 171000, 20: 190000
}

class State(Enum):
    EXPLORING = 1
    COMBAT = 2
    CHATTING = 3


class HealthStatus(Enum):
    """D&D 3.5 health states"""
    HEALTHY = "healthy"       # HP > 0
    DISABLED = "disabled"     # HP == 0, can take single action
    DYING = "dying"           # HP -1 to -9, unconscious, losing HP
    DEAD = "dead"             # HP <= -10
    STABLE = "stable"         # Dying but stabilized


# D&D 3.5 Equipment Slots
EQUIPMENT_SLOTS = [
    "head",       # Helm, hat, circlet
    "face",       # Goggles, mask, lenses
    "neck",       # Amulet, necklace, periapt
    "shoulders",  # Cloak, cape, mantle
    "body",       # Armor, robe
    "torso",      # Vest, shirt (under armor)
    "arms",       # Bracers, armbands
    "hands",      # Gloves, gauntlets
    "ring_left",  # Ring
    "ring_right", # Ring
    "waist",      # Belt
    "feet",       # Boots, shoes
    "main_hand",  # Weapon
    "off_hand",   # Shield, second weapon, or empty
]


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
        self.quest_log = None  # Will be initialized with QuestLog when needed
        self.reputation = {}  # {faction_name: reputation_value}
        self.titles = []  # List of earned titles
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
        self.active_conditions = {}  # {condition_name: rounds_remaining} for duration tracking
        self.feats = feats if feats is not None else []  # Accept feats from constructor or default to empty list
        self.domains = domains if domains is not None else []  # List of domain names (e.g., ["War", "Sun"])

        # Apply Toughness feat bonus at creation time (only when feats passed explicitly; from_dict sets feats after init)
        if feats is not None and 'Toughness' in self.feats:
            self.max_hp += 3
            self.hp = min(self.hp + 3, self.max_hp)

        # Equipment system
        self.equipment = {slot: None for slot in EQUIPMENT_SLOTS}
        self.gold = 0  # Currency

        # Dying/stabilization tracking
        self.is_stable = False  # True if dying but stabilized

        # Spell slot tracking
        self.spells_used = {}  # {spell_level: count_used_today}

        # Damage dice for unarmed attacks
        self.damage_dice = [1, 3, 0]  # 1d3 unarmed by default
        self.domain_powers = {}  # domain_name -> granted power description or callable
        self.domain_spells = {}  # spell_level -> set of domain spell names
        self.is_builder = is_builder

        # Auto-attack and action queue system
        self.auto_attack_enabled = True  # Auto-attack is on by default
        self.combat_target = None  # Current combat target (mob or player)
        self.queued_action = None  # (action_type, action_name, args) - replaces next auto-attack
        # action_type: 'spell', 'skill', 'feat', 'maneuver', 'item'

        self.color_enabled = True
        self.email = None
        self.resistances = {}    # {"fire": 10, "cold": 5}
        self.immunities = []     # ["poison", "disease"]
        self.build_mode = False
        self.hashed_password = None

        # Power Attack and Combat Expertise toggle amounts
        self.power_attack_amt = 0
        self.combat_expertise_amt = 0

        # --- New system fields (Phase 1-4 + Batch A/B) ---
        # Phase 1
        self.chosen_path = None      # Magi path: Seer/Keeper/Voice
        self.wimpy = 0               # Auto-flee HP% threshold (0-50)
        self.bank_gold = 0           # Gold stored in bank

        # Phase 2
        self.hidden = False          # Stealth: currently hiding
        self.hide_check = 0          # Stealth: last Hide check result
        self.sneaking = False        # Stealth: sneak mode active
        self.class_levels = {}       # Multiclass: {class_name: level}

        # Phase 3 (session-only — NOT persisted)
        self.party = None            # Party object
        self.following = None        # Player we're following

        # Phase 4
        self.achievements = []       # List of earned achievement IDs
        self.kill_count = 0
        self.craft_count = 0
        self.rooms_visited = set()   # Set of visited room vnums
        self.hunger = 100            # 100 = full, 0 = starving
        self.thirst = 100            # 100 = hydrated, 0 = dehydrated
        self.survival_mode = False   # Toggle hunger/thirst mechanics
        self.guild_name = None       # Guild membership
        self.guild_rank = None       # Rank within guild

        # Session-only fields
        self.mount = None
        self.mounted = False
        self.companion = None
        self.light_source = None
        self.flying = False          # System 30: Flying (session-only)
        self.speaking_language = "Common"   # System 28: active speaking language (session-only)
        self.known_languages = ["Common"]   # System 28: known languages (session-only)

        # Batch A/B
        self.auto_loot = False
        self.auto_gold = False
        self.aliases = {}            # Custom command aliases
        self.practice_points = 0     # Skill points (D&D 3.5: spent on skills at level-up)
        self.trained_abilities = {}  # {ability: times_trained}
        self.brief_mode = False      # Short room descriptions
        self.compact_mode = False    # Reduce blank lines
        self.auto_exit = True        # Show exits on move
        self.familiar_type = None    # System 26: Familiar type (persisted)

        # System 36: Remort / Prestige
        self.remort_count = 0        # Number of times character has remoorted
        self.remort_pending = False  # Confirmation flag (session-only)

        # Narrative progression
        self.narrative_progress = []  # List of completed chapter IDs

        # Arc tracking (BUILDOUT_ARC_MODULE) — hidden from player
        self.arc_sheets = {}  # arc_id (str) -> ArcSheet

        # PC roleplay sheet (player-authored via rpsheet command)
        try:
            from src.ai_schemas.pc_sheet import PcSheet
            self.rp_sheet = PcSheet()
        except ImportError:
            self.rp_sheet = None

        # System 39: Ignore / Block (persisted)
        self.ignored_players = []    # List of player names to ignore

        # System 40: AFK Status (session-only, NOT persisted)
        self.afk = False             # AFK toggle
        self.afk_message = ""        # Optional AFK message

        # AI Chat session (session-only, NOT persisted)
        self.active_chat_session = None  # ChatSession object when in CHATTING state
        self.chat_shadow = None          # ShadowPresence created for this chat

        # Body position (session-only, NOT persisted)
        self.position = "standing"   # standing/sitting/kneeling/resting/sleeping

        # Auto-sacrifice toggle (persisted)
        self.auto_sac = False

        # System 42: Duel (session-only, NOT persisted)
        self._in_duel = False
        self._duel_challenger = None

        # Class ability tracking (session-only, NOT persisted)
        self._rage_uses = 0
        self._inspire_uses = 0
        self._turn_uses = 0
        self._wildshape_uses = 0
        self._smite_active = False
        self._lay_on_hands_pool = 0
        self._flurry_active = False
        self._original_stats = None  # For wild shape revert

        # Persisted class ability data
        self.favored_enemies = []

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
        if self.char_class in ("Wizard", "Sorcerer", "Bard", "Cleric", "Paladin", "Ranger", "Magi"):
            spells = get_spells_for_class(self.char_class, self.class_level)
            # Handle both old dict format and new Spell dataclass format
            result = {}
            for spell in spells:
                if hasattr(spell, 'name'):
                    # New Spell dataclass
                    result[spell.name] = spell.name
                elif isinstance(spell, dict):
                    # Old dict format
                    result[spell["name"]] = spell
            return result
        return {}

    def _auto_spells_per_day(self):
        """Auto-populate spells per day for spellcasting classes (placeholder logic)."""
        if self.char_class in ("Wizard", "Sorcerer", "Bard", "Cleric", "Paladin", "Ranger", "Magi"):
            spells = get_spells_for_class(self.char_class, self.class_level)
            per_day = {}
            for spell in spells:
                # Handle both old dict format and new Spell dataclass format
                if hasattr(spell, 'level'):
                    # New Spell dataclass
                    lvl = spell.level.get(self.char_class, 0)
                elif isinstance(spell, dict):
                    # Old dict format
                    lvl = spell["level"][self.char_class]
                else:
                    continue
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
    def _apply_innate_elemental_resistance(self):
        """Apply innate elemental resistance based on racial elemental affinity.
        Oreka lore: all Kin carry elemental resonance granting minor resistance.
        earth=acid resist 2, fire=fire resist 2, water=cold resist 2, wind=electricity resist 2.
        """
        affinity = getattr(self, 'elemental_affinity', None)
        if not affinity:
            return
        element_to_energy = {"earth": "acid", "fire": "fire", "water": "cold", "wind": "electricity"}
        energy = element_to_energy.get(affinity)
        if energy:
            # Set innate resistance (don't overwrite if player already has higher)
            current = self.resistances.get(energy, 0)
            if current < 2:
                self.resistances[energy] = 2

    def to_dict(self):
        # Serialize equipment
        equipment_dict = {}
        for slot, item in self.equipment.items():
            if item:
                equipment_dict[slot] = item.to_dict()
            else:
                equipment_dict[slot] = None

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
            "spells_used": getattr(self, 'spells_used', {}),
            "hp": self.hp,
            "max_hp": self.max_hp,
            "ac": self.ac,
            "room_vnum": self.room.vnum if self.room else None,
            "quests": self.quests,
            "quest_log": self.quest_log.to_dict() if self.quest_log else None,
            "reputation": getattr(self, 'reputation', {}),
            "titles": getattr(self, 'titles', []),
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
            "equipment": equipment_dict,
            "gold": getattr(self, 'gold', 0),
            "feats": getattr(self, 'feats', []),
            "skills": getattr(self, 'skills', {}),
            "domains": getattr(self, 'domains', []),
            "alignment": getattr(self, 'alignment', None),
            "deity": getattr(self, 'deity', None),
            "is_builder": getattr(self, 'is_builder', False),
            "is_stable": getattr(self, 'is_stable', False),
            "conditions": list(getattr(self, 'conditions', set())),
            "active_conditions": getattr(self, 'active_conditions', {}),
            "auto_attack_enabled": getattr(self, 'auto_attack_enabled', True),
            "color_enabled": getattr(self, 'color_enabled', True),
            "email": getattr(self, 'email', None),
            "resistances": getattr(self, 'resistances', {}),
            "immunities": getattr(self, 'immunities', []),
            "build_mode": getattr(self, 'build_mode', False),
            "hashed_password": getattr(self, 'hashed_password', None),
            "power_attack_amt": getattr(self, 'power_attack_amt', 0),
            "combat_expertise_amt": getattr(self, 'combat_expertise_amt', 0),
            "active_buffs": getattr(self, 'active_buffs', {}),
            "temp_str_bonus": getattr(self, 'temp_str_bonus', 0),
            "temp_dex_bonus": getattr(self, 'temp_dex_bonus', 0),
            "temp_con_bonus": getattr(self, 'temp_con_bonus', 0),
            "temp_ac_bonus": getattr(self, 'temp_ac_bonus', 0),
            "temp_attack_bonus": getattr(self, 'temp_attack_bonus', 0),
            "temp_save_bonus": getattr(self, 'temp_save_bonus', 0),
            # New system fields
            "chosen_path": getattr(self, 'chosen_path', None),
            "wimpy": getattr(self, 'wimpy', 0),
            "bank_gold": getattr(self, 'bank_gold', 0),
            "hidden": getattr(self, 'hidden', False),
            "hide_check": getattr(self, 'hide_check', 0),
            "sneaking": getattr(self, 'sneaking', False),
            "class_levels": getattr(self, 'class_levels', {}),
            "achievements": getattr(self, 'achievements', []),
            "kill_count": getattr(self, 'kill_count', 0),
            "craft_count": getattr(self, 'craft_count', 0),
            "rooms_visited": list(getattr(self, 'rooms_visited', set())),
            "hunger": getattr(self, 'hunger', 100),
            "thirst": getattr(self, 'thirst', 100),
            "survival_mode": getattr(self, 'survival_mode', False),
            "guild_name": getattr(self, 'guild_name', None),
            "guild_rank": getattr(self, 'guild_rank', None),
            "auto_loot": getattr(self, 'auto_loot', False),
            "auto_gold": getattr(self, 'auto_gold', False),
            "aliases": getattr(self, 'aliases', {}),
            "practice_points": getattr(self, 'practice_points', 0),
            "quest_points": getattr(self, 'quest_points', 0),
            "trained_abilities": getattr(self, 'trained_abilities', {}),
            "brief_mode": getattr(self, 'brief_mode', False),
            "compact_mode": getattr(self, 'compact_mode', False),
            "auto_exit": getattr(self, 'auto_exit', True),
            "familiar_type": getattr(self, 'familiar_type', None),
            # System 36: Remort
            "remort_count": getattr(self, 'remort_count', 0),
            # System 39: Ignore / Block
            "ignored_players": getattr(self, 'ignored_players', []),
            # Class abilities (persisted)
            "favored_enemies": getattr(self, 'favored_enemies', []),
            # Auto-sacrifice
            "auto_sac": getattr(self, 'auto_sac', False),
            "pending_feats": getattr(self, '_pending_feat_selection', None),
            # Narrative progress
            "narrative_progress": getattr(self, 'narrative_progress', []),
            # Arc tracking (hidden from player; serialized for persistence)
            "arc_sheets": {
                arc_id: (sheet.to_dict() if hasattr(sheet, 'to_dict') else sheet)
                for arc_id, sheet in (getattr(self, 'arc_sheets', {}) or {}).items()
            },
            # PC roleplay sheet (player-authored via rpsheet command)
            "rp_sheet": (
                self.rp_sheet.to_dict()
                if getattr(self, 'rp_sheet', None) and hasattr(self.rp_sheet, 'to_dict')
                else None
            ),
            # Captive rescue system persistence
            "rescued_captives": getattr(self, 'rescued_captives', []),
            "pending_rescue_rewards": getattr(self, 'pending_rescue_rewards', []),
            # Reputation-gated quest reveal persistence
            "revealed_quests": getattr(self, 'revealed_quests', []),
            "completed_hidden_quests": getattr(self, 'completed_hidden_quests', []),
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
        char.spells_used = data.get("spells_used", {})
        char.quests = data.get("quests", [])
        # Load quest log from saved data
        quest_log_data = data.get("quest_log")
        if quest_log_data:
            from src.quests import QuestLog
            char.quest_log = QuestLog.from_dict(quest_log_data)
            char.quest_log.owner = char  # Set owner for GMCP emission
        else:
            char.quest_log = None
        char.reputation = data.get("reputation", {})
        char.titles = data.get("titles", [])
        char.state = State[data.get("state", "EXPLORING")]
        char.is_ai = data.get("is_ai", False)
        char.xp = data.get("xp", 0)
        char.show_all = data.get("show_all", False)
        char.alignment = data.get("alignment")
        char.deity = data.get("deity")
        char.is_builder = data.get("is_builder", False)

        # Load new fields
        char.gold = data.get("gold", 0)
        char.feats = data.get("feats", [])
        char.skills = data.get("skills", {})
        char.domains = data.get("domains", [])
        char.is_stable = data.get("is_stable", False)
        char.conditions = set(data.get("conditions", []))
        char.active_conditions = data.get("active_conditions", {})
        char.auto_attack_enabled = data.get("auto_attack_enabled", True)
        char.color_enabled = data.get("color_enabled", True)
        char.email = data.get("email", None)
        char.resistances = data.get("resistances", {})
        # Apply innate elemental resistance from racial affinity
        char._apply_innate_elemental_resistance()
        char.immunities = data.get("immunities", [])
        char.build_mode = data.get("build_mode", False)
        char.hashed_password = data.get("hashed_password", None)
        char.power_attack_amt = data.get("power_attack_amt", 0)
        char.combat_expertise_amt = data.get("combat_expertise_amt", 0)
        char.active_buffs = data.get("active_buffs", {})
        char.temp_str_bonus = data.get("temp_str_bonus", 0)
        char.temp_dex_bonus = data.get("temp_dex_bonus", 0)
        char.temp_con_bonus = data.get("temp_con_bonus", 0)
        char.temp_ac_bonus = data.get("temp_ac_bonus", 0)
        char.temp_attack_bonus = data.get("temp_attack_bonus", 0)
        char.temp_save_bonus = data.get("temp_save_bonus", 0)
        # New system fields
        char.chosen_path = data.get("chosen_path", None)
        char.wimpy = data.get("wimpy", 0)
        char.bank_gold = data.get("bank_gold", 0)
        char.hidden = data.get("hidden", False)
        char.hide_check = data.get("hide_check", 0)
        char.sneaking = data.get("sneaking", False)
        char.class_levels = data.get("class_levels", {})
        char.achievements = data.get("achievements", [])
        char.kill_count = data.get("kill_count", 0)
        char.craft_count = data.get("craft_count", 0)
        char.rooms_visited = set(data.get("rooms_visited", []))
        char.hunger = data.get("hunger", 100)
        char.thirst = data.get("thirst", 100)
        char.survival_mode = data.get("survival_mode", False)
        char.guild_name = data.get("guild_name", None)
        char.guild_rank = data.get("guild_rank", None)
        char.auto_loot = data.get("auto_loot", False)
        char.auto_gold = data.get("auto_gold", False)
        char.aliases = data.get("aliases", {})
        char.practice_points = data.get("practice_points", 0)
        char.quest_points = data.get("quest_points", 0)
        char.trained_abilities = data.get("trained_abilities", {})
        char.brief_mode = data.get("brief_mode", False)
        char.compact_mode = data.get("compact_mode", False)
        char.auto_exit = data.get("auto_exit", True)
        char.familiar_type = data.get("familiar_type", None)
        # System 36: Remort
        char.remort_count = data.get("remort_count", 0)
        # System 39: Ignore / Block
        char.ignored_players = data.get("ignored_players", [])
        # Class abilities (persisted)
        char.favored_enemies = data.get("favored_enemies", [])
        # Auto-sacrifice
        char.auto_sac = data.get("auto_sac", False)
        char._pending_feat_selection = data.get("pending_feats", None)
        # Narrative progress
        char.narrative_progress = data.get("narrative_progress", [])

        # Arc sheets (hidden from player)
        char.arc_sheets = {}
        try:
            from src.ai_schemas.arc_sheet import ArcSheet
            for arc_id, sheet_data in (data.get("arc_sheets", {}) or {}).items():
                if isinstance(sheet_data, ArcSheet):
                    char.arc_sheets[arc_id] = sheet_data
                elif isinstance(sheet_data, dict):
                    char.arc_sheets[arc_id] = ArcSheet.from_dict(sheet_data)
        except ImportError:
            pass  # Schemas not yet loadable — ignore

        # PC roleplay sheet
        try:
            from src.ai_schemas.pc_sheet import PcSheet
            rp_data = data.get("rp_sheet")
            if isinstance(rp_data, dict):
                char.rp_sheet = PcSheet.from_dict(rp_data)
            elif isinstance(rp_data, PcSheet):
                char.rp_sheet = rp_data
            else:
                char.rp_sheet = PcSheet()
        except ImportError:
            char.rp_sheet = None

        # Captive rescue system persistence
        char.rescued_captives = data.get("rescued_captives", [])
        char.pending_rescue_rewards = data.get("pending_rescue_rewards", [])
        # Reputation-gated quest reveal persistence
        char.revealed_quests = data.get("revealed_quests", [])
        char.completed_hidden_quests = data.get("completed_hidden_quests", [])

        # Load equipment
        equipment_data = data.get("equipment", {})
        if equipment_data:
            for slot, item_data in equipment_data.items():
                if item_data:
                    char.equipment[slot] = Item.from_dict(item_data)
                else:
                    char.equipment[slot] = None

        return char

    # =========================================================================
    # Arc sheet accessors (BUILDOUT_ARC_MODULE §1.3)
    # =========================================================================

    def get_arc(self, arc_id):
        """Return the ArcSheet for this arc_id, or None if not registered."""
        return (getattr(self, 'arc_sheets', None) or {}).get(arc_id)

    def get_checklist_item(self, arc_id, item_id):
        """Return the ChecklistItem, or None."""
        arc = self.get_arc(arc_id)
        if not arc:
            return None
        return arc.get_item(item_id)

    def check_arc_item(self, arc_id, item_id, detail=None, now=None):
        """Flip a checklist item to checked (or detailed if detail provided).

        Returns True if state changed, False otherwise. Updates timestamps
        and auto-promotes arc.status from 'untouched' to 'aware' on first flip.
        """
        import time as _time
        arc = self.get_arc(arc_id)
        if not arc:
            return False
        item = arc.get_item(item_id)
        if not item:
            return False

        ts = now if now is not None else _time.time()
        prior_state = item.state
        new_state = "detailed" if detail else "checked"

        # Determine if this counts as an actual change
        if detail:
            # Detailed update is always considered a change if detail differs OR was unchecked
            if prior_state == "detailed" and dict(item.detail) == dict(detail):
                return False
        else:
            if prior_state == "checked":
                return False

        item.state = new_state
        if detail:
            item.detail = dict(detail)
        if item.first_changed_at is None:
            item.first_changed_at = ts
        item.last_changed_at = ts

        arc.last_activity_at = ts
        if arc.status == "untouched":
            arc.status = "aware"
            arc.entered_at = ts

        return True

    def touched_arcs(self):
        """Return list of arc_ids where any checklist item has progress."""
        arcs = getattr(self, 'arc_sheets', None) or {}
        return [
            arc_id for arc_id, sheet in arcs.items()
            if hasattr(sheet, 'has_any_progress') and sheet.has_any_progress()
        ]

    def set_arc_status(self, arc_id, status, resolution=None, now=None):
        """Set the arc's status. Returns True if changed."""
        import time as _time
        arc = self.get_arc(arc_id)
        if not arc:
            return False
        from src.ai_schemas.arc_sheet import ARC_STATUSES
        if status not in ARC_STATUSES:
            return False
        if arc.status == status and (resolution is None or arc.resolution == resolution):
            return False
        arc.status = status
        if resolution is not None:
            arc.resolution = resolution
        ts = now if now is not None else _time.time()
        arc.last_activity_at = ts
        if arc.entered_at is None and status != "untouched":
            arc.entered_at = ts
        return True

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

        # Domain bonus slots: Clerics with domains get +1 slot per domain per spell level.
        # One domain slot per spell level is the D&D 3.5 rule (not per domain count).
        if self.char_class == "Cleric" and self.domains:
            max_lvl = self.get_max_spell_level()
            for lvl in range(1, max_lvl + 1):
                self.spells_per_day[lvl] = self.spells_per_day.get(lvl, 0) + 1

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

    # =========================================================================
    # Auto-attack and Action Queue System
    # =========================================================================
    def queue_action(self, action_type, action_name, args=""):
        """Queue an action to replace the next auto-attack.

        Args:
            action_type: 'spell', 'skill', 'feat', 'maneuver', or 'item'
            action_name: Name of the spell/skill/feat/maneuver/item
            args: Additional arguments (e.g., target name)
        """
        self.queued_action = (action_type, action_name, args)

    def clear_queue(self):
        """Clear the queued action."""
        self.queued_action = None

    def has_queued_action(self):
        """Check if there's a queued action."""
        return self.queued_action is not None

    def get_queued_action(self):
        """Get and clear the queued action (consume it)."""
        action = self.queued_action
        self.queued_action = None
        return action

    def set_combat_target(self, target):
        """Set the current combat target for auto-attack."""
        self.combat_target = target

    def clear_combat_target(self):
        """Clear the combat target."""
        self.combat_target = None

    def toggle_auto_attack(self):
        """Toggle auto-attack on/off."""
        self.auto_attack_enabled = not self.auto_attack_enabled
        return self.auto_attack_enabled

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

        # Feat selection is handled by cmd_levelup / cmd_feat_select

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
        # Armor check penalty — derive from equipped body armor
        armor_penalty = 0
        if hasattr(self, 'equipment'):
            body_armor = self.equipment.get('body')
            if body_armor:
                # Common ACP values by armor type
                acp_table = {
                    'padded': 0, 'leather': 0, 'studded leather': -1,
                    'chain shirt': -2, 'hide': -3, 'scale mail': -4,
                    'chainmail': -5, 'breastplate': -4, 'splint mail': -7,
                    'banded mail': -6, 'half-plate': -7, 'full plate': -6,
                }
                armor_name = getattr(body_armor, 'name', '').lower()
                for key, acp in acp_table.items():
                    if key in armor_name:
                        armor_penalty = abs(acp)
                        break
                # Fallback: heavier armor = higher penalty based on AC bonus
                if armor_penalty == 0 and getattr(body_armor, 'ac_bonus', 0) > 3:
                    armor_penalty = getattr(body_armor, 'ac_bonus', 0) - 2
            shield = self.equipment.get('off_hand')
            if shield and getattr(shield, 'item_type', '').lower() == 'shield':
                armor_penalty += 1  # Shields add -1 to -2 ACP
        penalty = armor_penalty if skill in armor_check_skills else 0
        roll = random.randint(1, 20)
        ability_mod = ability_mods.get(skill, 0)
        # Fallback: Craft (*) and Knowledge (*) use INT, Profession (*) uses WIS, Perform (*) uses CHA
        if ability_mod == 0:
            if skill.startswith("Craft ("):
                ability_mod = (self.int_score - 10) // 2
            elif skill.startswith("Knowledge ("):
                ability_mod = (self.int_score - 10) // 2
            elif skill.startswith("Profession ("):
                ability_mod = (self.wis_score - 10) // 2
            elif skill.startswith("Perform ("):
                ability_mod = (self.cha_score - 10) // 2
        # Apply feat bonuses to skill checks (Skill Focus, Acrobatic, etc.)
        feat_bonus = 0
        from src.feats import FEATS
        for feat_name in getattr(self, 'feats', []):
            feat = FEATS.get(feat_name)
            if feat and feat.effect:
                feat_bonus = feat.apply(self, skill=skill, value=feat_bonus)
        return roll + skill_val + ability_mod + bonus - penalty + feat_bonus

    def get_prompt(self):
        # Colors
        R = "\033[0m"       # Reset
        RED = "\033[1;31m"
        GRN = "\033[0;32m"
        YEL = "\033[1;33m"
        CYN = "\033[1;36m"
        WHT = "\033[1;37m"
        DIM = "\033[0;90m"
        MAG = "\033[0;35m"
        BRED = "\033[0;31m"

        # HP with color based on percentage
        hp_pct = (self.hp / self.max_hp * 100) if self.max_hp > 0 else 0
        if hp_pct >= 75:
            hp_color = GRN
        elif hp_pct >= 40:
            hp_color = YEL
        else:
            hp_color = RED
        hp_str = f"{hp_color}HP:{self.hp}/{self.max_hp}{R}"

        # AC
        ac_str = f"{CYN}AC:{self.ac}{R}"

        # Move
        mv_str = f"{WHT}MV:{self.move}/{self.max_move}{R}"

        # Gold
        gold = getattr(self, 'gold', 0)
        gold_str = f"{YEL}Gold:{gold}{R}"

        # XP to next level
        xp_to_next = max(0, XP_TABLE.get(self.level + 1, 0) - self.xp)
        xp_str = f"{DIM}TNL:{xp_to_next}{R}"

        # Spells (for casters)
        spell_str = ""
        spells_per_day = getattr(self, 'spells_per_day', {})
        if spells_per_day and any(v > 0 for v in spells_per_day.values()):
            slots = []
            for lvl in sorted(spells_per_day.keys()):
                remaining = spells_per_day[lvl]
                if remaining > 0 or lvl == 0:
                    slots.append(f"L{lvl}:{remaining}")
            if slots:
                spell_str = f" {MAG}SP:[{'/'.join(slots)}]{R}"

        # Conditions
        cond_str = ""
        conditions = getattr(self, 'conditions', set())
        active = getattr(self, 'active_conditions', {})
        all_conds = list(conditions) + list(active.keys())
        # Also check divine buffs
        divine = getattr(self, 'divine_buffs', {})
        if divine and divine.get('duration', 0) > 0:
            all_conds.append("Blessed")
        if all_conds:
            cond_str = f" {BRED}[{','.join(all_conds[:3])}]{R}"

        # Room name (short)
        room_name = ""
        if hasattr(self, 'room') and self.room:
            rn = self.room.name
            if len(rn) > 25:
                rn = rn[:22] + "..."
            room_name = f" {DIM}{rn}{R}"

        # Exits line in yellow
        exits_str = ""
        if hasattr(self, 'room') and self.room and hasattr(self.room, 'exits'):
            exit_names = list(self.room.exits.keys())
            if exit_names:
                exits_str = f"{YEL}[Exits: {', '.join(exit_names)}]{R}\n"

        # Build prompt — exits in yellow above the stat line
        return f"\n{exits_str}{hp_str} {ac_str} {mv_str} {gold_str} {xp_str}{spell_str}{cond_str}\n> \n"
    
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
        # GMCP: notify client of condition change
        try:
            from src.gmcp import emit_status
            emit_status(self)
        except Exception:
            pass

    def remove_condition(self, condition):
        """Remove a status condition."""
        self.conditions.discard(condition)
        # GMCP: notify client of condition change
        try:
            from src.gmcp import emit_status
            emit_status(self)
        except Exception:
            pass

    def has_condition(self, condition):
        """Check if the character has a given condition."""
        return condition in self.conditions or condition in self.active_conditions

    def get_condition_modifier(self, modifier_type: str) -> int:
        """
        Get total modifier from all conditions for a given type.
        Uses the conditions module to calculate cumulative penalties/bonuses.

        modifier_type can be: 'attack_penalty', 'ac_penalty', 'save_penalty',
        'damage_penalty', 'initiative_penalty', etc.
        """
        return cond.calculate_condition_modifiers(self, modifier_type)

    def can_act(self) -> bool:
        """Check if character can take actions based on conditions."""
        if not self.is_conscious:
            return False
        return cond.can_act(self)

    def can_move(self) -> bool:
        """Check if character can move based on conditions."""
        if not self.is_conscious:
            return False
        return cond.can_move(self)

    def can_cast(self) -> bool:
        """Check if character can cast spells based on conditions."""
        if not self.is_conscious:
            return False
        return cond.can_cast_spells(self)

    def has_condition_effect(self, effect_key: str) -> bool:
        """Check if any active condition has a specific effect."""
        return cond.has_effect(self, effect_key)

    def loses_dex_to_ac(self) -> bool:
        """Check if character loses Dex bonus to AC from conditions."""
        return cond.has_effect(self, 'loses_dex_to_ac')

    def get_speed_multiplier(self) -> float:
        """Get speed multiplier from conditions (e.g., exhausted = 0.5)."""
        # Check for speed_multiplier in conditions
        multiplier = 1.0
        all_conditions = self.conditions | set(self.active_conditions.keys())
        for cond_name in all_conditions:
            condition = cond.get_condition(cond_name)
            if condition and 'speed_multiplier' in condition.effects:
                multiplier = min(multiplier, condition.effects['speed_multiplier'])
        return multiplier

    def list_conditions(self) -> list:
        """Return list of active condition names with descriptions."""
        result = []
        all_conditions = self.conditions | set(self.active_conditions.keys())
        for cond_name in sorted(all_conditions):
            condition = cond.get_condition(cond_name)
            if condition:
                duration = self.active_conditions.get(cond_name)
                if duration:
                    result.append(f"{condition.name} ({duration} rounds)")
                else:
                    result.append(condition.name)
            else:
                result.append(cond_name)
        return result

    def describe_conditions(self) -> str:
        """Get formatted description of all active conditions."""
        conditions_list = self.list_conditions()
        if not conditions_list:
            return "No active conditions."
        return "Active conditions: " + ", ".join(conditions_list)

    # =========================================================================
    # D&D 3.5 Health Status System
    # =========================================================================

    @property
    def health_status(self) -> HealthStatus:
        """
        Determine character's health status based on HP.
        D&D 3.5 rules: 0 = disabled, -1 to -9 = dying, -10 or less = dead
        """
        if self.hp > 0:
            return HealthStatus.HEALTHY
        elif self.hp == 0:
            return HealthStatus.DISABLED
        elif self.hp > -10:
            if self.is_stable:
                return HealthStatus.STABLE
            return HealthStatus.DYING
        else:
            return HealthStatus.DEAD

    @property
    def is_conscious(self) -> bool:
        """Check if character is conscious (can take actions)"""
        status = self.health_status
        return status in (HealthStatus.HEALTHY, HealthStatus.DISABLED)

    @property
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.health_status != HealthStatus.DEAD

    def stabilization_check(self) -> tuple:
        """
        Make a stabilization check when dying.
        D&D 3.5: 10% chance to stabilize each round.
        Returns (stabilized: bool, message: str)
        """
        if self.health_status not in (HealthStatus.DYING,):
            return False, ""

        roll = random.randint(1, 100)
        if roll <= 10:
            self.is_stable = True
            return True, f"{self.name} stabilizes at {self.hp} HP!"
        else:
            # Lose 1 HP
            self.hp -= 1
            if self.hp <= -10:
                return False, f"{self.name} bleeds out and dies!"
            return False, f"{self.name} continues bleeding ({self.hp} HP)..."

    def take_damage(self, amount: int) -> str:
        """
        Take damage and return status message.
        Handles transition to dying/dead states.
        """
        old_hp = self.hp
        self.hp -= amount

        # If was stable and took damage, no longer stable
        if self.is_stable and amount > 0:
            self.is_stable = False

        status = self.health_status
        msg = f"{self.name} takes {amount} damage! ({old_hp} -> {self.hp} HP)"

        if status == HealthStatus.DISABLED:
            msg += f"\n{self.name} is disabled (0 HP)!"
        elif status == HealthStatus.DYING:
            msg += f"\n{self.name} is dying!"
        elif status == HealthStatus.DEAD:
            msg += f"\n{self.name} has died!"

        # Shadow Chat Game world bleed: notify the dream
        if amount > 0 and getattr(self, 'state', None) and self.state.name == 'CHATTING':
            session = getattr(self, 'active_chat_session', None)
            if session:
                session.add_world_event(
                    f"{self.name}'s body takes {amount} damage in the waking world!"
                )
                # Catastrophic damage ends the chat
                if status == HealthStatus.DEAD:
                    try:
                        from src.chat_session import force_end_body_death
                        force_end_body_death(session, self)
                    except Exception:
                        pass

        return msg

    def heal(self, amount: int) -> str:
        """Heal damage and return status message."""
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)

        # If healed above 0, no longer dying/stable
        if self.hp > 0:
            self.is_stable = False

        return f"{self.name} heals {amount} HP! ({old_hp} -> {self.hp} HP)"

    # =========================================================================
    # Condition Duration System
    # =========================================================================

    def add_timed_condition(self, condition: str, duration: int = None):
        """
        Add a condition with optional duration in rounds.
        If duration is None, condition is permanent until removed.
        """
        self.conditions.add(condition)
        if duration is not None:
            self.active_conditions[condition] = duration

    def tick_conditions(self) -> list:
        """
        Called each combat round to decrement condition durations.
        Returns list of expired condition names.
        """
        expired = []
        to_remove = []

        for condition, duration in self.active_conditions.items():
            if duration is not None:
                new_duration = duration - 1
                if new_duration <= 0:
                    expired.append(condition)
                    to_remove.append(condition)
                else:
                    self.active_conditions[condition] = new_duration

        # Remove expired conditions
        for condition in to_remove:
            del self.active_conditions[condition]
            self.conditions.discard(condition)

        return expired

    # =========================================================================
    # Equipment System
    # =========================================================================

    def get_equipment_slot_for_item(self, item) -> str:
        """Determine which slot an item should go in based on its type."""
        slot_mapping = {
            'weapon': 'main_hand',
            'shield': 'off_hand',
            'light': 'off_hand',
            'armor': 'body',
            'helm': 'head',
            'helmet': 'head',
            'hat': 'head',
            'circlet': 'head',
            'goggles': 'face',
            'mask': 'face',
            'amulet': 'neck',
            'necklace': 'neck',
            'periapt': 'neck',
            'cloak': 'shoulders',
            'cape': 'shoulders',
            'mantle': 'shoulders',
            'robe': 'body',
            'vest': 'torso',
            'shirt': 'torso',
            'bracers': 'arms',
            'armband': 'arms',
            'gloves': 'hands',
            'gauntlets': 'hands',
            'ring': 'ring_left',  # Default to left, can specify right
            'belt': 'waist',
            'boots': 'feet',
            'shoes': 'feet',
        }

        item_type = (getattr(item, 'item_type', '') or '').lower()
        item_slot = (getattr(item, 'slot', '') or '').lower()

        # First check if item has explicit slot
        if item_slot and item_slot in EQUIPMENT_SLOTS:
            return item_slot

        # Check item type
        if item_type in slot_mapping:
            return slot_mapping[item_type]

        # Check item name for hints
        item_name = getattr(item, 'name', '').lower()
        for keyword, slot in slot_mapping.items():
            if keyword in item_name:
                return slot

        return None  # Can't be equipped

    def equip_item(self, item, slot: str = None) -> tuple:
        """
        Equip an item to the appropriate slot.
        Returns (success: bool, message: str, unequipped_item or None)
        """
        # Determine slot
        if slot is None:
            slot = self.get_equipment_slot_for_item(item)

        if slot is None:
            return False, f"You cannot equip {item.name}.", None

        if slot not in EQUIPMENT_SLOTS:
            return False, f"Invalid equipment slot: {slot}", None

        # Handle ring slots
        if slot == 'ring_left' and self.equipment.get('ring_left'):
            if not self.equipment.get('ring_right'):
                slot = 'ring_right'

        # Check if item is in inventory
        if item not in self.inventory:
            return False, f"You don't have {item.name} in your inventory.", None

        # Unequip current item in slot if any
        unequipped = None
        if self.equipment.get(slot):
            unequipped = self.equipment[slot]
            self.inventory.append(unequipped)

        # Equip new item
        self.equipment[slot] = item
        self.inventory.remove(item)

        # Recalculate AC
        self._recalculate_ac()

        # Apply stat bonuses from equipped item
        _stat_bonus_attr_map = {
            'str': 'temp_str_bonus', 'dex': 'temp_dex_bonus', 'con': 'temp_con_bonus',
            'int': 'temp_int_bonus', 'wis': 'temp_wis_bonus', 'cha': 'temp_cha_bonus',
            'attack': 'temp_attack_bonus', 'damage': 'temp_damage_bonus',
            'save': 'temp_save_bonus',
        }
        bonuses = getattr(item, 'stat_bonuses', {})
        for stat, value in bonuses.items():
            attr = _stat_bonus_attr_map.get(stat.lower())
            if attr:
                setattr(self, attr, getattr(self, attr, 0) + value)

        # Reverse bonuses from unequipped item
        if unequipped:
            old_bonuses = getattr(unequipped, 'stat_bonuses', {})
            for stat, value in old_bonuses.items():
                attr = _stat_bonus_attr_map.get(stat.lower())
                if attr:
                    setattr(self, attr, getattr(self, attr, 0) - value)

        msg = f"You equip {item.name}."
        if unequipped:
            msg += f" (Removed {unequipped.name})"

        return True, msg, unequipped

    def unequip_item(self, slot: str) -> tuple:
        """
        Unequip item from a slot.
        Returns (success: bool, message: str, unequipped_item or None)
        """
        if slot not in EQUIPMENT_SLOTS:
            return False, f"Invalid slot: {slot}", None

        item = self.equipment.get(slot)
        if not item:
            return False, f"Nothing equipped in {slot}.", None

        self.equipment[slot] = None
        self.inventory.append(item)

        # Recalculate AC
        self._recalculate_ac()

        # Reverse stat bonuses from unequipped item
        _stat_bonus_attr_map = {
            'str': 'temp_str_bonus', 'dex': 'temp_dex_bonus', 'con': 'temp_con_bonus',
            'int': 'temp_int_bonus', 'wis': 'temp_wis_bonus', 'cha': 'temp_cha_bonus',
            'attack': 'temp_attack_bonus', 'damage': 'temp_damage_bonus',
            'save': 'temp_save_bonus',
        }
        bonuses = getattr(item, 'stat_bonuses', {})
        for stat, value in bonuses.items():
            attr = _stat_bonus_attr_map.get(stat.lower())
            if attr:
                setattr(self, attr, getattr(self, attr, 0) - value)

        return True, f"You remove {item.name}.", item

    def _recalculate_ac(self):
        """Recalculate AC based on equipped items and Dex."""
        base_ac = 10
        dex_mod = (self.dex_score - 10) // 2
        max_dex = 99  # Default no limit

        armor_bonus = 0
        shield_bonus = 0
        natural_bonus = 0
        deflection_bonus = 0
        dodge_bonus = 0

        # Check body armor
        armor = self.equipment.get('body')
        if armor:
            armor_bonus = getattr(armor, 'ac_bonus', 0)
            max_dex = min(max_dex, getattr(armor, 'max_dex_bonus', 99))

        # Check shield
        shield = self.equipment.get('off_hand')
        if shield and getattr(shield, 'item_type', '').lower() == 'shield':
            shield_bonus = getattr(shield, 'ac_bonus', 0)

        # Check other equipment for bonuses
        for slot, item in self.equipment.items():
            if item and slot not in ('body', 'off_hand'):
                bonuses = getattr(item, 'stat_bonuses', {})
                if 'natural_armor' in bonuses:
                    natural_bonus = max(natural_bonus, bonuses['natural_armor'])
                if 'deflection' in bonuses:
                    deflection_bonus = max(deflection_bonus, bonuses['deflection'])
                if 'dodge' in bonuses:
                    dodge_bonus += bonuses['dodge']  # Dodge stacks

        # Apply max dex from armor
        effective_dex = min(dex_mod, max_dex)

        self.ac = base_ac + armor_bonus + shield_bonus + natural_bonus + deflection_bonus + dodge_bonus + effective_dex

    def get_equipped_weapon(self):
        """Get the currently equipped weapon, or None for unarmed."""
        return self.equipment.get('main_hand')

    # =========================================================================
    # Rest and Recovery
    # =========================================================================

    def rest(self, hours: int = 8) -> str:
        """
        Rest for a period of time.
        8 hours = full rest (full HP recovery, spell slots restored)
        1 hour = short rest (regain some HP)
        """
        messages = []

        if hours >= 8:
            # Long rest - full recovery
            old_hp = self.hp
            self.hp = self.max_hp
            messages.append(f"After a full night's rest, you recover fully. ({old_hp} -> {self.max_hp} HP)")

            # Restore spell slots
            if self.spells_per_day:
                self.spells_used = {}
                messages.append("Your spell slots have been restored.")

            # Clear temporary conditions
            temp_conditions = ['fatigued', 'shaken']
            for cond in temp_conditions:
                if cond in self.conditions:
                    self.conditions.discard(cond)
                    messages.append(f"You are no longer {cond}.")

            # Stabilize if dying
            if self.health_status == HealthStatus.DYING:
                self.is_stable = True
                messages.append("You have stabilized.")

        else:
            # Short rest - recover some HP
            con_mod = (self.con_score - 10) // 2
            recovery = max(1, self.level + con_mod)
            old_hp = self.hp
            self.hp = min(self.hp + recovery, self.max_hp)
            messages.append(f"After a short rest, you recover {self.hp - old_hp} HP. ({old_hp} -> {self.hp} HP)")

        return "\n".join(messages)

    # =========================================================================
    # Feat Support
    # =========================================================================

    def has_feat(self, feat_name: str) -> bool:
        """Check if character has a feat (case-insensitive, partial match)."""
        feat_lower = feat_name.lower()
        for f in self.feats:
            if feat_lower in f.lower():
                return True
        return False

    # =========================================================================
    # Combat Maneuvers
    # =========================================================================

    def disarm(self, target):
        """Attempt to disarm an opponent. Uses D&D 3.5 rules."""
        from src import maneuvers
        return maneuvers.disarm(self, target)

    def trip(self, target):
        """Attempt to trip an opponent. Uses D&D 3.5 rules."""
        from src import maneuvers
        return maneuvers.trip(self, target)

    def bull_rush(self, target):
        """Attempt to bull rush an opponent. Uses D&D 3.5 rules."""
        from src import maneuvers
        return maneuvers.bull_rush(self, target)

    def grapple(self, target):
        """Attempt to grapple an opponent. Uses D&D 3.5 rules."""
        from src import maneuvers
        return maneuvers.grapple(self, target)

    def overrun(self, target):
        """Attempt to overrun an opponent. Uses D&D 3.5 rules."""
        from src import maneuvers
        return maneuvers.overrun(self, target)

    def sunder(self, target):
        """Attempt to sunder an opponent's weapon. Uses D&D 3.5 rules."""
        from src import maneuvers
        return maneuvers.sunder(self, target)

    def whirlwind_attack(self, targets):
        """Attack all adjacent enemies once. Requires Whirlwind Attack feat."""
        from src import maneuvers
        return maneuvers.whirlwind_attack(self, targets)

    def spring_attack(self, target, move_before=10, move_after=10):
        """Move, attack, and continue moving. Requires Spring Attack feat."""
        from src import maneuvers
        return maneuvers.spring_attack(self, target, move_before, move_after)

    def stunning_fist(self, target):
        """Attempt to stun an opponent. Requires Stunning Fist feat."""
        from src import maneuvers
        return maneuvers.stunning_fist(self, target)

    def feint(self, target):
        """Attempt to feint in combat. Uses Bluff vs Sense Motive."""
        from src import maneuvers
        return maneuvers.feint(self, target)

    def grapple_damage(self, target):
        """Deal damage while grappling."""
        from src import maneuvers
        return maneuvers.grapple_action_damage(self, target)

    def grapple_pin(self, target):
        """Attempt to pin a grappled opponent."""
        from src import maneuvers
        return maneuvers.grapple_action_pin(self, target)

    def grapple_escape(self, grappler):
        """Attempt to escape from a grapple."""
        from src import maneuvers
        return maneuvers.grapple_action_escape(self, grappler)

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

    # =========================================================================
    # Encumbrance System
    # =========================================================================

    def get_carry_weight(self):
        """Sum of weight for all inventory items."""
        return sum(getattr(item, 'weight', 0) for item in self.inventory)

    def get_max_carry(self):
        """Max carry weight: STR * 10 (simplified D&D 3.5 light load for medium creatures)."""
        return self.str_score * 10
