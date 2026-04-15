"""
Faction & Reputation System for OrekaMUD3.

Manages faction membership, reputation tracking, rank progression,
shop discounts, and territory hostility checks. Faction data is loaded
from data/guilds.json. Characters store reputation as a dict of
faction_id -> int and guild membership as guild_name / guild_rank.
"""

import json
import os

# Reputation standing thresholds (default, overridden per-faction)
DEFAULT_THRESHOLDS = {
    "hostile": -500,
    "unfriendly": -100,
    "neutral": 0,
    "friendly": 100,
    "honored": 300,
    "allied": 600
}


class FactionManager:
    def __init__(self):
        self.factions = {}
        self.load_factions()

    def load_factions(self):
        """Load faction data from guilds.json"""
        path = os.path.join("data", "guilds.json")
        with open(path, "r", encoding="utf-8") as f:
            self.factions = json.load(f)

    def get_faction(self, faction_id):
        """Get faction data by ID"""
        return self.factions.get(faction_id)

    def get_all_factions(self):
        """Return all factions"""
        return self.factions

    def get_reputation(self, character, faction_id):
        """Get player's reputation with a faction"""
        return character.reputation.get(faction_id, 0)

    def modify_reputation(self, character, faction_id, amount, reason=""):
        """Change reputation. Returns (new_value, old_standing, new_standing, message)"""
        # Get current
        old_rep = character.reputation.get(faction_id, 0)
        old_standing = self.get_standing_name(character, faction_id)

        # Modify
        new_rep = old_rep + amount
        character.reputation[faction_id] = new_rep
        new_standing = self.get_standing_name(character, faction_id)

        # Build message
        faction = self.factions.get(faction_id, {})
        fname = faction.get("name", faction_id)
        direction = "increased" if amount > 0 else "decreased"
        msg = f"Your reputation with {fname} has {direction} by {abs(amount)}."
        if reason:
            msg += f" ({reason})"
        if old_standing != new_standing:
            msg += f"\nYou are now {new_standing} with {fname}!"

        # Update guild rank if member
        if character.guild_name == faction_id:
            self._update_rank(character, faction_id)

        # GMCP: notify client of faction reputation change
        try:
            from src.gmcp import emit_factions
            emit_factions(character)
        except Exception:
            pass

        # Narrative faction change hook
        try:
            from src.narrative import get_narrative_manager
            nm = get_narrative_manager()
            narr_triggered = nm.on_faction_change(character, faction_id, new_rep)
            if narr_triggered:
                _w = getattr(character, '_writer', None) or getattr(character, 'writer', None)
                if _w:
                    for chapter in narr_triggered:
                        text, rewards = nm.trigger_chapter(character, chapter)
                        try:
                            _w.write(text + "\n")
                            if rewards and "xp" in rewards:
                                character.xp = getattr(character, 'xp', 0) + rewards["xp"]
                                _w.write(f"Gained {rewards['xp']} XP!\n")
                            if rewards and "title" in rewards:
                                if not hasattr(character, 'titles'):
                                    character.titles = []
                                if rewards["title"] not in character.titles:
                                    character.titles.append(rewards["title"])
                                _w.write(f"Earned title: {rewards['title']}\n")
                        except Exception:
                            pass
        except Exception:
            pass

        return (new_rep, old_standing, new_standing, msg)

    def get_standing_name(self, character, faction_id):
        """Get standing name (hostile/unfriendly/neutral/friendly/honored/allied)"""
        rep = self.get_reputation(character, faction_id)
        faction = self.factions.get(faction_id, {})
        thresholds = faction.get("reputation_thresholds", DEFAULT_THRESHOLDS)

        # Check from highest to lowest
        if rep >= thresholds.get("allied", 600):
            return "Allied"
        elif rep >= thresholds.get("honored", 300):
            return "Honored"
        elif rep >= thresholds.get("friendly", 100):
            return "Friendly"
        elif rep >= thresholds.get("neutral", 0):
            return "Neutral"
        elif rep >= thresholds.get("unfriendly", -100):
            return "Unfriendly"
        else:
            return "Hostile"

    def can_join(self, character, faction_id):
        """Check if character meets join requirements. Returns (bool, reason_string)"""
        faction = self.factions.get(faction_id)
        if not faction:
            return (False, "Unknown faction.")

        ftype = faction.get("type", "reputation_only")
        if ftype == "reputation_only":
            return (False, f"The {faction['name']} cannot be formally joined.")
        if ftype == "secret":
            return (False, f"You don't know how to join the {faction['name']}.")

        if character.guild_name:
            return (False, f"You are already a member of {character.guild_name}. Leave first.")

        reqs = faction.get("join_requirements", {})

        # Race check
        allowed_races = reqs.get("races")
        if allowed_races and character.race not in allowed_races:
            return (False, f"The {faction['name']} does not accept your race.")

        # Class check
        allowed_classes = reqs.get("classes")
        if allowed_classes and character.char_class not in allowed_classes:
            return (False, f"The {faction['name']} does not accept your class.")

        # Reputation check
        min_rep = reqs.get("min_reputation", 0)
        current_rep = self.get_reputation(character, faction_id)
        if current_rep < min_rep:
            return (False, f"You need at least {min_rep} reputation to join. You have {current_rep}.")

        return (True, "")

    def join_faction(self, character, faction_id):
        """Join a faction. Returns message string."""
        can, reason = self.can_join(character, faction_id)
        if not can:
            return reason

        faction = self.factions.get(faction_id)
        character.guild_name = faction_id
        ranks = faction.get("ranks", [])
        if ranks:
            character.guild_rank = ranks[0].get("title", "Member")
        else:
            character.guild_rank = "Member"

        # Set minimum reputation if not already there
        if self.get_reputation(character, faction_id) < 0:
            character.reputation[faction_id] = 0

        return f"You have joined the {faction['name']} as a {character.guild_rank}!"

    def leave_faction(self, character):
        """Leave current faction. Returns message."""
        if not character.guild_name:
            return "You are not a member of any faction."

        faction = self.factions.get(character.guild_name, {})
        fname = faction.get("name", character.guild_name)

        # Reputation penalty for leaving
        self.modify_reputation(character, character.guild_name, -50, "Left the faction")

        character.guild_name = None
        character.guild_rank = None
        return f"You have left the {fname}. Your reputation has suffered."

    def _update_rank(self, character, faction_id):
        """Update guild rank based on current reputation."""
        faction = self.factions.get(faction_id)
        if not faction:
            return
        rep = self.get_reputation(character, faction_id)
        ranks = faction.get("ranks", [])

        # Find highest rank player qualifies for
        best_rank = None
        for r in ranks:
            if rep >= r.get("min_reputation", 0):
                best_rank = r.get("title")

        if best_rank and best_rank != character.guild_rank:
            old_rank = character.guild_rank
            character.guild_rank = best_rank
            # Return promotion message (caller should display)

    def get_rank_title(self, character, faction_id):
        """Get the rank title for a character in a faction (even if not a member)."""
        if character.guild_name == faction_id:
            return character.guild_rank
        return None

    def get_shop_modifier(self, character, faction_id):
        """Get shop price modifier based on reputation. Returns multiplier (1.0 = normal)."""
        standing = self.get_standing_name(character, faction_id)
        faction = self.factions.get(faction_id, {})
        base_discount = faction.get("shop_discount", 0.05)

        modifiers = {
            "Hostile": 1.5,       # 50% markup
            "Unfriendly": 1.2,    # 20% markup
            "Neutral": 1.0,       # Normal
            "Friendly": 1.0 - base_discount,
            "Honored": 1.0 - base_discount * 2,
            "Allied": 1.0 - base_discount * 3,
        }
        return modifiers.get(standing, 1.0)

    def is_territory(self, room_vnum, faction_id):
        """Check if a room is in a faction's territory."""
        faction = self.factions.get(faction_id, {})
        return room_vnum in faction.get("territory_vnums", [])

    def check_territory_hostility(self, character, room_vnum):
        """Check if character is hostile in any faction's territory. Returns list of hostile factions."""
        hostile = []
        for fid, faction in self.factions.items():
            if room_vnum in faction.get("territory_vnums", []):
                standing = self.get_standing_name(character, fid)
                if standing == "Hostile":
                    hostile.append(faction.get("name", fid))
        return hostile

    def format_faction_list(self, character):
        """Format the faction list display for a character."""
        lines = ["\n=== Factions of Oreka ===\n"]
        for fid, faction in self.factions.items():
            name = faction.get("name", fid)
            standing = self.get_standing_name(character, fid)
            rep = self.get_reputation(character, fid)
            ftype = faction.get("type", "unknown")

            # Color code standing
            color = {
                "Hostile": "\033[1;31m",
                "Unfriendly": "\033[0;31m",
                "Neutral": "\033[0;37m",
                "Friendly": "\033[0;32m",
                "Honored": "\033[1;32m",
                "Allied": "\033[1;36m",
            }.get(standing, "\033[0m")

            member_tag = ""
            if character.guild_name == fid:
                member_tag = f" \033[1;33m[{character.guild_rank}]\033[0m"

            type_tag = ""
            if ftype == "secret":
                if rep == 0 and character.guild_name != fid:
                    continue  # Don't show secret factions with no interaction
                type_tag = " \033[0;35m(Secret)\033[0m"
            elif ftype == "race_locked":
                type_tag = " \033[0;33m(Restricted)\033[0m"

            lines.append(f"  {color}{name}\033[0m — {standing} ({rep:+d}){member_tag}{type_tag}")

        lines.append("")
        return "\n".join(lines)

    def format_faction_info(self, character, faction_id):
        """Format detailed faction info."""
        faction = self.factions.get(faction_id)
        if not faction:
            return "Unknown faction."

        name = faction.get("name", faction_id)
        desc = faction.get("description", "No description.")
        leader = faction.get("leader", "Unknown")
        standing = self.get_standing_name(character, faction_id)
        rep = self.get_reputation(character, faction_id)
        ftype = faction.get("type", "unknown")

        lines = [f"\n=== {name} ==="]
        lines.append(f"  {desc}")
        lines.append(f"  Leader: {leader}")
        lines.append(f"  Your standing: {standing} ({rep:+d})")

        if character.guild_name == faction_id:
            lines.append(f"  Your rank: {character.guild_rank}")

        # Show ranks
        ranks = faction.get("ranks", [])
        if ranks:
            lines.append("  Ranks:")
            for r in ranks:
                marker = " <-- You" if character.guild_rank == r.get("title") else ""
                lines.append(f"    {r['title']} (rep {r['min_reputation']}+){marker}")

        # Show join info
        if ftype == "joinable":
            can, reason = self.can_join(character, faction_id)
            if character.guild_name == faction_id:
                lines.append("  Status: You are a member.")
            elif can:
                lines.append("  Status: You are eligible to join! Use 'faction join'.")
            else:
                lines.append(f"  Status: {reason}")
        elif ftype == "secret":
            lines.append("  This faction operates in shadow.")
        elif ftype == "race_locked":
            reqs = faction.get("join_requirements", {})
            races = reqs.get("races", [])
            if races:
                lines.append(f"  Restricted to: {', '.join(races)}")
        elif ftype == "reputation_only":
            lines.append("  This faction cannot be formally joined. Earn standing through actions.")

        lines.append("")
        return "\n".join(lines)


# Singleton
_faction_manager = None


def get_faction_manager():
    global _faction_manager
    if _faction_manager is None:
        _faction_manager = FactionManager()
    return _faction_manager
