import json
import os
import random
import re


class ReligionManager:
    def __init__(self):
        self.deities = {}
        self.load_deities()

    def load_deities(self):
        path = os.path.join("data", "deities.json")
        with open(path, "r", encoding="utf-8") as f:
            self.deities = json.load(f)

    def save_deities(self):
        path = os.path.join("data", "deities.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.deities, f, indent=2, ensure_ascii=False)

    def get_deity(self, deity_id):
        return self.deities.get(deity_id)

    def find_deity(self, query):
        """Fuzzy match deity by name or id."""
        q = query.lower().strip()
        for did, d in self.deities.items():
            if q in did or q in d.get("name", "").lower():
                return did, d
        return None, None

    def get_all_deities(self):
        return self.deities

    def get_deity_for_shrine(self, room):
        """Determine which deity a shrine/temple room belongs to."""
        vnum = room.vnum if hasattr(room, 'vnum') else room
        for did, d in self.deities.items():
            if vnum in d.get("shrine_vnums", []):
                return did, d
        # Check room name for hints
        if hasattr(room, 'name'):
            name = room.name.lower()
            for did, d in self.deities.items():
                dname = d.get("name", "").lower()
                # Check if deity name fragment appears in room name
                for part in dname.split(",")[0].split():
                    if len(part) > 3 and part.lower() in name:
                        return did, d
        return None, None

    def can_pray(self, character, room):
        """Check if character can pray in this room."""
        flags = getattr(room, 'flags', [])
        if 'altar' in flags or 'temple' in flags:
            return True, ""
        return False, "There is no shrine or altar here to pray at."

    def pray(self, character, room, world=None):
        """
        Pray at a shrine/altar. Returns (message, deity_player_to_notify).
        - Always gives mechanical buff
        - If deity is player-linked and online, returns their character for notification
        """
        can, reason = self.can_pray(character, room)
        if not can:
            return reason, None

        deity_id, deity = self.get_deity_for_shrine(room)

        if not deity:
            # Generic altar -- small generic buff
            if hasattr(character, 'hp') and hasattr(character, 'max_hp'):
                heal = min(random.randint(1, 6), character.max_hp - character.hp)
                character.hp = min(character.hp + heal, character.max_hp)
            return "You kneel and pray. A faint warmth touches you, though no particular presence answers.", None

        deity_name = deity.get("name", deity_id)
        dtype = deity.get("type", "ascended")

        # Apply prayer buff
        buff = deity.get("prayer_buff", {})
        buff_msg = self._apply_buff(character, buff, deity)

        # Build response message
        lines = []
        if dtype == "elemental_lord":
            lines.append(f"\n\033[1;36mYou kneel before the altar of {deity_name}.\033[0m")
            lines.append(f"The elemental resonance deepens. You feel the {deity.get('element', 'primal')} element acknowledge your presence.")
        else:
            lines.append(f"\n\033[1;33mYou kneel and pray to {deity_name}.\033[0m")
            if hasattr(character, 'deity') and character.deity and character.deity.lower() in deity_name.lower():
                lines.append("As a devoted follower, your prayer resonates strongly.")
            else:
                lines.append("Your prayer rises into the sacred silence.")

        if buff_msg:
            lines.append(buff_msg)

        # Check for player-linked deity
        notify_player = None
        player_name = deity.get("player_name")
        if player_name and world:
            for p in world.players:
                if p.name.lower() == player_name.lower():
                    notify_player = p
                    lines.append(f"\033[1;35mYou sense a divine presence stir in response.\033[0m")
                    break

        return "\n".join(lines), notify_player

    def _apply_buff(self, character, buff, deity):
        """Apply prayer buff to character. Returns description message."""
        if not buff:
            return ""

        btype = buff.get("type", "")
        desc = buff.get("description", "")

        messages = []

        if btype == "healing":
            amount_str = buff.get("amount", "1d6")
            if amount_str:
                heal = self._roll_dice(amount_str)
                if hasattr(character, 'hp') and hasattr(character, 'max_hp'):
                    actual_heal = min(heal, character.max_hp - character.hp)
                    character.hp = min(character.hp + heal, character.max_hp)
                    if actual_heal > 0:
                        messages.append(f"  \033[0;32mDivine energy heals you for {actual_heal} HP.\033[0m")

        # Apply stat bonuses
        stat_bonus = buff.get("stat_bonus", {})
        duration = buff.get("duration_rounds", 100)
        if stat_bonus:
            # Store as a temporary buff on character
            if not hasattr(character, 'divine_buffs'):
                character.divine_buffs = {}
            character.divine_buffs = {
                "deity": deity.get("name", "Unknown"),
                "stat_bonus": stat_bonus,
                "duration": duration,
                "resist": buff.get("resist", {})
            }
            bonus_parts = [f"+{v} {k}" for k, v in stat_bonus.items()]
            messages.append(f"  \033[0;36mBlessed: {', '.join(bonus_parts)} for {duration} rounds.\033[0m")

        # Apply resistance (when there are resists but no stat bonuses)
        resist = buff.get("resist", {})
        if resist and not stat_bonus:
            if not hasattr(character, 'divine_buffs'):
                character.divine_buffs = {}
            character.divine_buffs = {
                "deity": deity.get("name", "Unknown"),
                "stat_bonus": {},
                "duration": duration,
                "resist": resist
            }
            resist_parts = [f"{k} {v}" for k, v in resist.items()]
            messages.append(f"  \033[0;36mResistance granted: {', '.join(resist_parts)} for {duration} rounds.\033[0m")

        if desc and not messages:
            messages.append(f"  {desc}")

        return "\n".join(messages)

    def _roll_dice(self, dice_str):
        """Parse and roll dice like '2d8+5'."""
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', str(dice_str))
        if not match:
            return 0
        num = int(match.group(1))
        size = int(match.group(2))
        bonus = int(match.group(3) or 0)
        total = sum(random.randint(1, size) for _ in range(num)) + bonus
        return max(0, total)

    def notify_deity_player(self, deity_player, worshipper, prayer_text=""):
        """Send prayer notification to a player-linked deity."""
        msg = f"\n\033[1;35m[Divine] A prayer reaches you from {worshipper.name}"
        if hasattr(worshipper, 'room') and worshipper.room:
            msg += f" at {worshipper.room.name}"
        msg += f".\033[0m"
        if prayer_text:
            msg += f'\n\033[0;35m  "{prayer_text}"\033[0m'
        return msg

    # === DIVINE POWERS (for player-linked deities / admins) ===

    def divine_bless(self, deity_char, target_char):
        """Deity blesses a follower with a powerful buff."""
        # Heal to full
        if hasattr(target_char, 'hp') and hasattr(target_char, 'max_hp'):
            target_char.hp = target_char.max_hp
        # Grant divine buff
        target_char.divine_buffs = {
            "deity": deity_char.name,
            "stat_bonus": {"Str": 2, "Dex": 2, "Con": 2, "Wis": 2},
            "duration": 200,
            "resist": {}
        }
        return (
            f"\033[1;33m{deity_char.name}'s divine light washes over {target_char.name}!\033[0m\n"
            f"  Fully healed. +2 to all physical and mental attributes for 200 rounds."
        )

    def divine_smite(self, deity_char, target):
        """Deity strikes an enemy with divine damage."""
        damage = random.randint(20, 40)
        if hasattr(target, 'hp'):
            target.hp -= damage
        return (
            f"\033[1;31m{deity_char.name}'s divine wrath strikes {target.name} for {damage} damage!\033[0m"
        )

    def divine_manifest(self, deity_char, room):
        """Deity manifests visibly in a room."""
        return (
            f"\n\033[1;33m{'=' * 50}\033[0m\n"
            f"\033[1;33mThe air shimmers with golden light. {deity_char.name} manifests before you!\033[0m\n"
            f"\033[1;33m{'=' * 50}\033[0m"
        )

    def divine_speak(self, deity_char, message, world):
        """Deity speaks through all their shrines. Returns list of (player, message) to notify."""
        # Find this deity's entry
        deity_id = None
        for did, d in self.deities.items():
            pname = d.get("player_name", "")
            if pname and pname.lower() == deity_char.name.lower():
                deity_id = did
                break

        if not deity_id:
            return []

        deity = self.deities[deity_id]
        shrine_vnums = set(deity.get("shrine_vnums", []))

        notifications = []
        speak_msg = (
            f"\n\033[1;33mA divine voice echoes through the shrine:\033[0m\n"
            f'\033[1;37m  "{message}"\033[0m\n'
            f"\033[0;33m  \u2014 {deity.get('name', deity_char.name)}\033[0m"
        )

        for player in world.players:
            if hasattr(player, 'room') and player.room:
                if player.room.vnum in shrine_vnums:
                    notifications.append((player, speak_msg))

        return notifications

    def divine_grant_title(self, deity_char, target_char, title):
        """Deity grants a divine title to a follower."""
        if not hasattr(target_char, 'titles'):
            target_char.titles = []
        target_char.titles.append(title)
        target_char.title = title  # Set as active title
        return (
            f"\033[1;33m{deity_char.name} bestows upon {target_char.name} the title: {title}\033[0m"
        )

    # === ADMIN DEITY MANAGEMENT ===

    def create_deity(self, name, deity_type="ascended", alignment="Neutral",
                     domains=None, portfolio="", element=None, description=""):
        """Create a new deity (for ascension events). Returns deity_id."""
        # Generate ID from name
        deity_id = name.lower().replace(" ", "_").replace(",", "").replace("'", "")[:30]

        self.deities[deity_id] = {
            "name": name,
            "type": deity_type,
            "alignment": alignment,
            "domains": domains or [],
            "portfolio": portfolio,
            "favored_weapon": "None",
            "element": element,
            "player_name": None,
            "shrine_vnums": [],
            "prayer_buff": {
                "type": "healing",
                "amount": "1d8+1",
                "duration_rounds": 100,
                "stat_bonus": {},
                "resist": {},
                "description": "A faint divine warmth touches you."
            },
            "holy_symbol": "Unknown",
            "description": description or "A newly ascended deity."
        }
        self.save_deities()
        return deity_id

    def link_deity_to_player(self, deity_id, player_name):
        """Link a deity to a player account (for player-gods)."""
        if deity_id not in self.deities:
            return False, f"Deity '{deity_id}' not found."
        self.deities[deity_id]["player_name"] = player_name
        self.save_deities()
        return True, f"Deity '{self.deities[deity_id]['name']}' linked to player '{player_name}'."

    def unlink_deity(self, deity_id):
        """Remove player link from deity."""
        if deity_id not in self.deities:
            return False, f"Deity '{deity_id}' not found."
        self.deities[deity_id]["player_name"] = None
        self.save_deities()
        return True, f"Deity '{self.deities[deity_id]['name']}' unlinked."

    def add_shrine(self, deity_id, room_vnum):
        """Add a shrine room to a deity."""
        if deity_id not in self.deities:
            return False, f"Deity '{deity_id}' not found."
        shrines = self.deities[deity_id].setdefault("shrine_vnums", [])
        if room_vnum not in shrines:
            shrines.append(room_vnum)
            self.save_deities()
        return True, f"Room {room_vnum} added as shrine of {self.deities[deity_id]['name']}."

    def format_deity_list(self, character):
        """Format deity list for display."""
        lines = ["\n\033[1;33m=== Deities of Oreka ===\033[0m\n"]

        lines.append("\033[1;36mElemental Lords:\033[0m")
        for did, d in self.deities.items():
            if d.get("type") == "elemental_lord":
                marker = ""
                if hasattr(character, 'deity') and character.deity and character.deity.lower() in d.get("name", "").lower():
                    marker = " \033[1;33m<Your Patron>\033[0m"
                lines.append(f"  {d['name']} \u2014 {d.get('portfolio', '')}{marker}")

        lines.append(f"\n\033[1;33mAscended Gods:\033[0m")
        for did, d in self.deities.items():
            if d.get("type") == "ascended":
                marker = ""
                if hasattr(character, 'deity') and character.deity and character.deity.lower() in d.get("name", "").lower():
                    marker = " \033[1;33m<Your Patron>\033[0m"
                player_tag = ""
                if d.get("player_name"):
                    player_tag = " \033[0;35m(Living)\033[0m"
                lines.append(f"  {d['name']} \u2014 {d.get('portfolio', '')}{marker}{player_tag}")

        lines.append("")
        return "\n".join(lines)

    def format_deity_info(self, character, deity_id):
        """Format detailed deity info."""
        d = self.deities.get(deity_id)
        if not d:
            return "Unknown deity."

        lines = [f"\n\033[1;33m=== {d['name']} ===\033[0m"]
        lines.append(f"  Type: {d.get('type', 'unknown').replace('_', ' ').title()}")
        lines.append(f"  Alignment: {d.get('alignment', 'Unknown')}")
        lines.append(f"  Portfolio: {d.get('portfolio', 'Unknown')}")
        lines.append(f"  Domains: {', '.join(d.get('domains', []))}")
        if d.get('element'):
            lines.append(f"  Element: {d['element'].title()}")
        lines.append(f"  Favored Weapon: {d.get('favored_weapon', 'None')}")
        lines.append(f"  Holy Symbol: {d.get('holy_symbol', 'Unknown')}")
        lines.append(f"\n  {d.get('description', '')}")

        if d.get('player_name'):
            lines.append(f"\n  \033[0;35mThis deity walks among mortals.\033[0m")

        is_patron = hasattr(character, 'deity') and character.deity and character.deity.lower() in d.get("name", "").lower()
        if is_patron:
            lines.append(f"  \033[1;33mThis is your patron deity.\033[0m")

        shrines = d.get("shrine_vnums", [])
        if shrines:
            lines.append(f"  Known shrines: {len(shrines)} locations")

        lines.append("")
        return "\n".join(lines)


# Singleton
_religion_manager = None


def get_religion_manager():
    global _religion_manager
    if _religion_manager is None:
        _religion_manager = ReligionManager()
    return _religion_manager
