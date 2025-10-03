from oreka_mud.src.combat import attack
from oreka_mud.src.character import State

class CommandParser:
    def cmd_handleanimal(self, character, _):
        """Attempt a Handle Animal skill check."""
        result = character.skill_check("Handle Animal")
        return f"You attempt to handle an animal. Skill check result: {result}"

    def cmd_survival(self, character, _):
        """Attempt a Survival skill check."""
        result = character.skill_check("Survival")
        return f"You attempt to survive in the wild. Skill check result: {result}"

    def cmd_intimidate(self, character, _):
        """Attempt an Intimidate skill check."""
        result = character.skill_check("Intimidate")
        return f"You attempt to intimidate. Skill check result: {result}"

    def cmd_climb(self, character, _):
        result = character.skill_check("Climb")
        return f"You attempt to climb. Skill check result: {result}"

    def cmd_jump(self, character, _):
        result = character.skill_check("Jump")
        return f"You attempt to jump. Skill check result: {result}"

    def cmd_listen(self, character, _):
        result = character.skill_check("Listen")
        return f"You attempt to listen. Skill check result: {result}"

    def cmd_ride(self, character, _):
        result = character.skill_check("Ride")
        return f"You attempt to ride. Skill check result: {result}"
    def cmd_rage(self, character, args):
        """Activate Barbarian Rage."""
        # 'args' is not used, but included for interface consistency
        return character.activate_rage()

    def cmd_calm(self, character, args):
        """End Barbarian Rage."""
        # 'args' is not used, but included for interface consistency
        return character.deactivate_rage()

    def cmd_swim(self, character, _):
        result = character.skill_check("Swim")
        return f"You attempt to swim. Skill check result: {result}"

    def cmd_progression(self, _, __):
        """Show the D&D 3.5e advancement chart for feats, skill ranks, and ability increases."""
        lines = [
            "D&D 3.5e Character Advancement Chart:",
            "",
            "| Level | Feat? | Ability Score? | Max Class Skill | Max Cross-Class Skill |",
            "|-------|-------|----------------|-----------------|----------------------|",
        ]
        for lvl in range(1, 21):
            feat = "Yes" if lvl == 1 or lvl in (3, 6, 9, 12, 15, 18) else ""
            ability = "Yes" if lvl in (4, 8, 12, 16, 20) else ""
            max_class = lvl + 3
            max_cross = (lvl + 3) / 2
            lines.append(f"| {lvl:<5} | {feat:<5} | {ability:<14} | {max_class:<15} | {max_cross:<20} |")
        lines.append("")
        lines.append("- Feats: 1st, 3rd, 6th, 9th, 12th, 15th, 18th level.")
        lines.append("- Ability Score: 4th, 8th, 12th, 16th, 20th level.")
        lines.append("- Max Class Skill Rank: level + 3")
        lines.append("- Max Cross-Class Skill Rank: (level + 3) / 2")
        return "\n".join(lines)
    def cmd_appraise(self, character, args):
        """Appraise the value of an item in your inventory or in the shopkeeper's stock."""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        if not args:
            return "Appraise what? Usage: appraise <item name>"
        # Check player's inventory first
        item = next((i for i in character.inventory if i.name.lower() == args.lower()), None)
        if item:
            price = shopkeeper.get_sell_price(item)
            return f"{shopkeeper.name} says: 'I can offer you {price} gp for your {item.name}." + (" It's in fine condition!'" if getattr(item, 'hp', None) == getattr(item, 'max_hp', None) else " It's a bit worn, but I'll take it.'")
        # Check shopkeeper's stock
        items = shopkeeper.get_shop_items()
        item = next((i for i in items if i.name.lower() == args.lower()), None)
        if item:
            price = shopkeeper.get_buy_price(item)
            return f"{shopkeeper.name} says: 'That {item.name} will cost you {price} gp.'"
        return f"{shopkeeper.name} says: 'I don't see any {args} here.'"
    def cmd_talk(self, character, _):
        """Talk to the shopkeeper in the room for a greeting or info."""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        dialogue = getattr(shopkeeper, 'dialogue', None)
        if dialogue:
            return f"{shopkeeper.name} says: '{dialogue}'"
        # Default dialogue
        return f"{shopkeeper.name} says: 'Welcome! Type list to see my wares, buy <item> to purchase, sell <item> to sell, or appraise <item> for a price.'"
        return f"{shopkeeper.name} says: 'Welcome! Type list to see my wares, buy <item> to purchase, sell <item> to sell, or appraise <item> for a price.'"
    def _find_shopkeeper(self, character):
        # Return the first shopkeeper mob in the room, or None
        for mob in getattr(character.room, 'mobs', []):
            if hasattr(mob, 'is_shopkeeper') and mob.is_shopkeeper():
                return mob
        return None
    def cmd_list(self, character, _):
        """List items for sale from the shopkeeper in the room."""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        items = shopkeeper.get_shop_items()
        if not items:
            return f"{shopkeeper.name} has nothing for sale."
        lines = [f"{shopkeeper.name} offers the following items:"]
        for item in items:
            price = shopkeeper.get_buy_price(item)
            lines.append(f"- {item.name} (Price: {price} gp)")
        return "\n".join(lines)
        return "\n".join(lines)

    def cmd_buy(self, character, args):
        """Buy an item from the shopkeeper in the room. Usage: buy <item name>"""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        if not args:
            return "Buy what? Usage: buy <item name>"
        items = shopkeeper.get_shop_items()
        item = next((i for i in items if i.name.lower() == args.lower()), None)
        if not item:
            return f"{shopkeeper.name} does not have {args}."
        price = shopkeeper.get_buy_price(item)
        if getattr(character, 'gold', 0) < price:
            return f"You cannot afford {item.name}. (Price: {price} gp)"
        character.gold -= price
        character.inventory.append(item)
        shopkeeper.remove_shop_item(item.vnum)
        return f"You buy {item.name} for {price} gp."

    def cmd_sell(self, character, args):
        """Sell an item to the shopkeeper in the room. Usage: sell <item name>"""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        if not args:
            return "Sell what? Usage: sell <item name>"
        item = next((i for i in character.inventory if i.name.lower() == args.lower()), None)
        if not item:
            return f"You do not have {args}."
        price = shopkeeper.get_sell_price(item)
        character.gold = getattr(character, 'gold', 0) + price
        character.inventory.remove(item)
        shopkeeper.add_shop_item(item.vnum)
    def cmd_components(self, _, __):
        """
        Show all raw materials, spell components, and reagents available in the game.
        Usage: components
        """
        import os, json
        lines = ["Raw Materials, Spell Components, and Reagents:"]
        # Load raw materials
        raw_path = os.path.join(os.path.dirname(__file__), '../data/items_raw_materials.json')
        try:
            with open(raw_path, 'r', encoding='utf-8') as f:
                raw_materials = json.load(f)
            lines.append("\nRaw Materials:")
            for item in raw_materials:
                lines.append(f"- {item['name']}: {item.get('description','')}")
        except Exception as e:
            lines.append(f"(Could not load raw materials: {e})")

        # Load spell components from spells.py (if any)
        try:
            from oreka_mud.src.spells import SPELLS
            component_set = set()
            material_set = set()
            for spell in SPELLS:
                for comp in spell.get('components', []):
                    if comp not in ('V', 'S', 'F', 'DF'):
                        component_set.add(comp)
                # Try to extract material components from description (optional)
                desc = spell.get('description', '')
                for mat in ["bat guano", "sulfur", "pearl", "amber", "resin", "charcoal", "saltpeter", "mercury", "mandrake root", "dragon blood"]:
                    if mat in desc.lower():
                        material_set.add(mat)
            if component_set or material_set:
                lines.append("\nSpell Components:")
                for comp in sorted(component_set):
                    lines.append(f"- {comp}")
                for mat in sorted(material_set):
                    lines.append(f"- {mat.title()}")
        except Exception as e:
            lines.append(f"(Could not load spell components: {e})")

        # List all unique materials from material_prices.json
        try:
            mat_path = os.path.join(os.path.dirname(__file__), '../data/material_prices.json')
            with open(mat_path, 'r', encoding='utf-8') as f:
                mat_data = json.load(f)
            lines.append("\nAll Known Materials:")
            for mat in sorted(mat_data.keys()):
                lines.append(f"- {mat.title()}")
        except Exception as e:
            lines.append(f"(Could not load material list: {e})")

        return "\n".join(lines)
        return "\n".join(lines)
    def cmd_saveplayer(self, character, args):
        """@saveplayer <name> | Force-save a player's data (admin only)."""
        from oreka_mud.src.character import Character
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        name = args.strip()
        if not name:
            return "Usage: @saveplayer <name>"
        try:
            # This assumes the player is loaded in memory; otherwise, load from file
            for player in self.world.players:
                if player.name.lower() == name.lower():
                    player.save()
                    return f"Player {name} saved."
            # Not in memory: try to load and save
            import os, json
            player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
            filename = os.path.join(player_dir, f"{name.lower()}.json")
            if not os.path.exists(filename):
                return f"Player file for {name} not found."
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            char = Character.from_dict(data)
            char.save()
            return f"Player {name} saved (from file)."
        except Exception as e:
            import logging
            logging.error(f"Error saving player {name}: {e}")
            return f"Error saving player {name}: {e}"

    def cmd_backupplayer(self, character, args):
        """@backupplayer <name> | Create a backup of a player's data (admin only)."""
        from oreka_mud.src.character import Character
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        name = args.strip()
        if not name:
            return "Usage: @backupplayer <name>"
        try:
            # Just call save, which now always creates a backup
            for player in self.world.players:
                if player.name.lower() == name.lower():
                    player.save()
                    return f"Backup created for {name}."
            # Not in memory: try to load and save
            import os, json
            player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
            filename = os.path.join(player_dir, f"{name.lower()}.json")
            if not os.path.exists(filename):
                return f"Player file for {name} not found."
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            char = Character.from_dict(data)
            char.save()
            return f"Backup created for {name} (from file)."
        except Exception as e:
            import logging
            logging.error(f"Error backing up player {name}: {e}")
            return f"Error backing up player {name}: {e}"

    def cmd_restoreplayer(self, character, args):
        """@restoreplayer <name> [timestamp] | Restore a player's data from backup (admin only)."""
        from oreka_mud.src.character import Character
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        parts = args.strip().split()
        if not parts:
            return "Usage: @restoreplayer <name> [timestamp]"
        name = parts[0]
        timestamp = parts[1] if len(parts) > 1 else None
        try:
            path = Character.rollback(name, timestamp)
            return f"Player {name} restored from backup: {path}"
        except Exception as e:
            import logging
            logging.error(f"Error restoring player {name}: {e}")
            return f"Error restoring player {name}: {e}"
    def cmd_mobadd(self, character, args):
        """@mobadd <name> | Creates a new mob in the current room."""
        from oreka_mud.src.mob import Mob
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @mobadd <name>"
        # Find an unused vnum
        max_vnum = max(self.world.mobs.keys(), default=1000)
        new_vnum = max_vnum + 1
        name = args.strip()
        # Basic mob template
        mob = Mob(new_vnum, name, 1, (1, 6, 0), 10, (1, 4, 0))
        self.world.mobs[new_vnum] = mob
        character.room.mobs.append(mob)
        self.world.save_mobs()
        return f"Mob '{name}' created in this room (vnum {new_vnum})."

    def cmd_mobedit(self, character, args):
        """@mobedit <vnum> <field> <value> | Edits a mob's property."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @mobedit <vnum> <field> <value>"
        try:
            vnum = int(parts[0])
        except ValueError:
            return "Vnum must be a number."
        field, value = parts[1], parts[2]
        mob = self.world.mobs.get(vnum)
        if not mob:
            return f"No mob with vnum {vnum}."
        # Basic fields only for now
        if hasattr(mob, field):
            # Try to cast to int if possible
            try:
                val = int(value)
            except ValueError:
                val = value
            setattr(mob, field, val)
            self.world.save_mobs()
            return f"Mob {vnum} field '{field}' set to {val}."
        return f"Mob has no field '{field}'."

    def cmd_itemadd(self, character, args):
        """@itemadd <name> | Creates a new item in the current room."""
        from oreka_mud.src.items import Item
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @itemadd <name>"
        # Find an unused vnum
        if hasattr(self.world, 'items'):
            max_vnum = max(self.world.items.keys(), default=1000)
        else:
            if not hasattr(self.world, 'items'):
                self.world.items = {}
            max_vnum = 1000
        new_vnum = max_vnum + 1
        name = args.strip()
        # Basic item template
        item = Item(new_vnum, name, "misc", 1, 0, description=f"A {name}.")
        self.world.items[new_vnum] = item
        character.room.items.append(item)
        self.world.save_items()
        return f"Item '{name}' created in this room (vnum {new_vnum})."

    def cmd_itemedit(self, character, args):
        """@itemedit <vnum> <field> <value> | Edits an item's property."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @itemedit <vnum> <field> <value>"
        try:
            vnum = int(parts[0])
        except ValueError:
            return "Vnum must be a number."
        field, value = parts[1], parts[2]
        item = None
        if hasattr(self.world, 'items'):
            item = self.world.items.get(vnum)
        if not item:
            return f"No item with vnum {vnum}."
        if hasattr(item, field):
            try:
                val = int(value)
            except ValueError:
                val = value
            setattr(item, field, val)
            self.world.save_items()
            return f"Item {vnum} field '{field}' set to {val}."
    def cmd_cast(self, character, args):
        """Casts a spell if prepared/known and slots are available, enforcing V/S and concentration."""
        from oreka_mud.src.spells import get_spell_by_name
        if not args:
            return "Cast what spell? Usage: cast <spell name>"
        spell_name = args.strip()
        spell = get_spell_by_name(spell_name)
        if not spell:
            return f"No such spell: {spell_name}"
        # Check if character has the spell prepared/known
        known = False
        # For prepared casters, check prepared_spells; for spontaneous, check spells_known
        spellcasting = character.get_spellcasting_info() if hasattr(character, 'get_spellcasting_info') else None
        is_prepared = spellcasting and spellcasting.get('type', '').lower() == 'prepared'
        if is_prepared:
            prepared = getattr(character, 'prepared_spells', {})
            for lvl, spells in prepared.items():
                if any(s.lower() == spell_name.lower() for s in spells):
                    known = True
                    break
        else:
            for s in character.spells_known.values():
                if isinstance(s, dict):
                    if s.get("name", "").lower() == spell_name.lower():
                        known = True
                        break
                elif isinstance(s, str):
                    if s.lower() == spell_name.lower():
                        known = True
                        break
        # Check for domain spells (Cleric only)
        if not known and character.char_class == "Cleric":
            # Check if the spell is a domain spell available at this level
            available_domains = character.get_available_domain_spells() if hasattr(character, 'get_available_domain_spells') else {}
            for lvl, spells in available_domains.items():
                if any(s.lower() == spell_name.lower() for s in spells):
                    known = True
                    break
        if not known:
            return f"You do not have {spell_name} prepared or known."
        # Find spell level for this class
        spell_level = spell["level"].get(character.char_class)
        if spell_level is None:
            return f"Your class cannot cast {spell_name}."
        # Check slots
        slots = character.spells_per_day.get(spell_level, 0)
        if slots < 1:
            return f"No spell slots remaining for level {spell_level}."
        # Enforce V/S components
        components = spell.get("components", [])
        if "V" in components and not character.can_cast_verbal():
            return "You cannot cast this spell: you are unable to speak!"
        if "S" in components and not character.can_cast_somatic():
            return "You cannot cast this spell: you are unable to move!"
        # Concentration check if interrupted (e.g., hit in combat)
        if character.was_interrupted():
            conc_result = character.skill_check("Concentration")
            # DC 10 + spell level (simplified)
            dc = 10 + spell_level
            if isinstance(conc_result, str):
                return f"Spell fails: {conc_result}"
            if conc_result < dc:
                character.clear_interrupted()
                return f"You fail to concentrate and lose the spell! (Needed {dc}, rolled {conc_result})"
            character.clear_interrupted()
        # Alignment/Deity restrictions (for divine casters)
        # Check for alignment tags in spell['school'] or spell.get('alignment')
        alignment = getattr(character, 'alignment', None)
        deity = getattr(character, 'deity', None)
        # Only enforce for Cleric, Paladin, Druid (expand as needed)
        if character.char_class in ("Cleric", "Paladin", "Druid"):
            school = spell.get("school", "")
            # Alignment tag check (e.g., [Evil], [Good], [Lawful], [Chaotic])
            import re
            align_tags = re.findall(r'\[(.*?)\]', school)
            for tag in align_tags:
                tag = tag.lower()
                if tag == "evil" and (not alignment or "evil" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Evil] spells."
                if tag == "good" and (not alignment or "good" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Good] spells."
                if tag == "lawful" and (not alignment or "lawful" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Lawful] spells."
                if tag == "chaotic" and (not alignment or "chaotic" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Chaotic] spells."
            # Deity restriction (if spell has 'deity' key)
            spell_deity = spell.get("deity")
            if spell_deity and (not deity or deity.lower() != spell_deity.lower()):
                return f"Only followers of {spell_deity} may cast this spell."
        # Deduct slot
        character.spells_per_day[spell_level] -= 1
        # Remove from prepared if prepared caster
        if is_prepared:
            for lvl, spells in character.prepared_spells.items():
                if spell_name in spells:
                    character.prepared_spells[lvl].remove(spell_name)
                    break
        # Simulate spell effect (placeholder)
        return f"You cast {spell_name}! {spell['description']} (Slots left for level {spell_level}: {character.spells_per_day[spell_level]})"
    def __init__(self, world):
        self.world = world
        self.commands = {
            "look": self.cmd_look,
            "say": self.cmd_say,
            "kill": self.cmd_kill,
            "north": self.cmd_move,
            "exits": self.cmd_exits,
            "quest": self.cmd_quest,
            "gecho": self.cmd_gecho,
            "who": self.cmd_who,
            "stats": self.cmd_stats,
            "get": self.cmd_get,
            "take": self.cmd_get,
            "drop": self.cmd_drop,
            "inventory": self.cmd_inventory,
            "inv": self.cmd_inventory,
            "help": self.cmd_help,
            "score": self.cmd_score,
            "skills": self.cmd_skills,
            "spells": self.cmd_spells,
            "cast": self.cmd_cast,
            "companion": self.cmd_companion,
            "quest": self.cmd_questpage,
            "levelup": self.cmd_levelup,
            "recall": self.cmd_recall,
            "@dig": self.cmd_dig,
            "@desc": self.cmd_desc,
            "@exit": self.cmd_exit,
            "@flag": self.cmd_flag,
            "@mobadd": self.cmd_mobadd,
            "@mobedit": self.cmd_mobedit,
            "@itemadd": self.cmd_itemadd,
            "@itemedit": self.cmd_itemedit,
            "components": self.cmd_components,
            "rage": self.cmd_rage,
            "calm": self.cmd_calm,
        }

    # --- Builder Commands ---
    def cmd_dig(self, character, args):
        """@dig <direction> <room name> | Creates a new room in the given direction, linking it to the current room."""
        from oreka_mud.src.room import Room
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 1)
        if not parts or len(parts) < 2:
            return "Usage: @dig <direction> <room name>"
        direction, name = parts[0].lower(), parts[1].strip()
        # Find an unused vnum
        max_vnum = max(self.world.rooms.keys(), default=1000)
        new_vnum = max_vnum + 1
        # Create new room
        new_room = Room(new_vnum, name, f"This is {name}.", {{}}, [], [])
        self.world.rooms[new_vnum] = new_room
        # Link exits
        character.room.exits[direction] = new_vnum
        # Add reverse exit
        reverse = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
        rev_dir = reverse.get(direction, None)
        if rev_dir:
            new_room.exits[rev_dir] = character.room.vnum
        self.world.save_rooms()
        return f"Room '{name}' created to the {direction} (vnum {new_vnum})."

    def cmd_desc(self, character, args):
        """@desc <new description> | Sets the description of the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @desc <new description>"
        character.room.description = args.strip()
        self.world.save_rooms()
        return "Room description updated."

    def cmd_exit(self, character, args):
        """@exit <direction> <vnum> | Creates or changes an exit in the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 1)
        if not parts or len(parts) < 2:
            return "Usage: @exit <direction> <vnum>"
        direction, vnum_str = parts[0].lower(), parts[1].strip()
        try:
            vnum = int(vnum_str)
        except ValueError:
            return "Vnum must be a number."
        if vnum not in self.world.rooms:
            return f"No room with vnum {vnum}."
        character.room.exits[direction] = vnum
        self.world.save_rooms()
        return f"Exit '{direction}' set to room {vnum}."

    def cmd_flag(self, character, args):
        """@flag <flag> [on|off] | Sets or clears a flag on the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split()
        if not parts:
            return "Usage: @flag <flag> [on|off]"
        flag = parts[0].lower()
        action = parts[1].lower() if len(parts) > 1 else "on"
        if action == "on":
            if flag not in character.room.flags:
                character.room.flags.append(flag)
            self.world.save_rooms()
            return f"Flag '{flag}' set on this room."
        elif action == "off":
            if flag in character.room.flags:
                character.room.flags.remove(flag)
            self.world.save_rooms()
            return f"Flag '{flag}' removed from this room."
        else:
            return "Usage: @flag <flag> [on|off]"

    def cmd_recall(self, character, args):
        """Teleports the player to the center room of the chapel (Central Aetherial Altar)."""
        center_vnum = 1000
        if center_vnum not in self.world.rooms:
            return "Recall failed: Chapel center room not found."
        # Remove from current room
        if character in character.room.players:
            character.room.players.remove(character)
        # Move to center room
        character.room = self.world.rooms[center_vnum]
        character.room.players.append(character)
        return f"You are enveloped in shimmering light and find yourself at the {character.room.name}."

    # --- Build command stubs, all restricted to immortals ---
    def _immortal_only(self, character):
        if not getattr(character, 'is_immortal', False):
            return "Command restricted to immortals!"
        return None

    def cmd_build(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing build logic...
        return "[IMMORTAL] Build command executed."

    def cmd_dig(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing dig logic...
        return "[IMMORTAL] Dig command executed."

    def cmd_setdesc(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setdesc logic...
        return "[IMMORTAL] Setdesc command executed."

    def cmd_setexit(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setexit logic...
        return "[IMMORTAL] Setexit command executed."

    def cmd_setmob(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setmob logic...
        return "[IMMORTAL] Setmob command executed."

    def cmd_setitem(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setitem logic...
        return "[IMMORTAL] Setitem command executed."

    def cmd_setflag(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setflag logic...
        return "[IMMORTAL] Setflag command executed."

    def cmd_setname(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setname logic...
        return "[IMMORTAL] Setname command executed."

    def cmd_setvnum(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setvnum logic...
        return "[IMMORTAL] Setvnum command executed."

    def cmd_setarea(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setarea logic...
        return "[IMMORTAL] Setarea command executed."

    def cmd_setroom(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setroom logic...
        return "[IMMORTAL] Setroom command executed."

    def cmd_setreset(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setreset logic...
        return "[IMMORTAL] Setreset command executed."

    def cmd_setdoor(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setdoor logic...
        return "[IMMORTAL] Setdoor command executed."

    def cmd_setowner(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setowner logic...
        return "[IMMORTAL] Setowner command executed."

    def cmd_setzone(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setzone logic...
        return "[IMMORTAL] Setzone command executed."

    def cmd_setweather(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setweather logic...
        return "[IMMORTAL] Setweather command executed."

    def cmd_setlight(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setlight logic...
        return "[IMMORTAL] Setlight command executed."

    def cmd_setterrain(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setterrain logic...
        return "[IMMORTAL] Setterrain command executed."

    def cmd_setnote(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setnote logic...
        return "[IMMORTAL] Setnote command executed."

    def cmd_sethelp(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing sethelp logic...
        return "[IMMORTAL] Sethelp command executed."

    def cmd_setcolor(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setcolor logic...
        return "[IMMORTAL] Setcolor command executed."

    def cmd_setprompt(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setprompt logic...
        return "[IMMORTAL] Setprompt command executed."

    def cmd_settitle(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing settitle logic...
        return "[IMMORTAL] Settitle command executed."

    def cmd_setrace(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setrace logic...
        return "[IMMORTAL] Setrace command executed."

    def cmd_setclass(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setclass logic...
        return "[IMMORTAL] Setclass command executed."

    def cmd_setdeity(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setdeity logic...
        return "[IMMORTAL] Setdeity command executed."

    def cmd_setalignment(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setalignment logic...
        return "[IMMORTAL] Setalignment command executed."

    def cmd_setlevel(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setlevel logic...
        return "[IMMORTAL] Setlevel command executed."

    def cmd_sethp(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing sethp logic...
        return "[IMMORTAL] Sethp command executed."

    def cmd_setmana(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setmana logic...
        return "[IMMORTAL] Setmana command executed."

    def cmd_setmove(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setmove logic...
        return "[IMMORTAL] Setmove command executed."

    def cmd_setac(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setac logic...
        return "[IMMORTAL] Setac command executed."

    def cmd_setstr(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setstr logic...
        return "[IMMORTAL] Setstr command executed."

    def cmd_setdex(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setdex logic...
        return "[IMMORTAL] Setdex command executed."

    def cmd_setcon(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setcon logic...
        return "[IMMORTAL] Setcon command executed."

    def cmd_setint(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setint logic...
        return "[IMMORTAL] Setint command executed."

    def cmd_setwis(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setwis logic...
        return "[IMMORTAL] Setwis command executed."

    def cmd_setcha(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setcha logic...
        return "[IMMORTAL] Setcha command executed."

    def cmd_setxp(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setxp logic...
        return "[IMMORTAL] Setxp command executed."

    def cmd_setgold(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setgold logic...
        return "[IMMORTAL] Setgold command executed."

    def cmd_setfeats(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setfeats logic...
        return "[IMMORTAL] Setfeats command executed."

    def cmd_setskills(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setskills logic...
        return "[IMMORTAL] Setskills command executed."

    def cmd_setspells(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setspells logic...
        return "[IMMORTAL] Setspells command executed."

    def cmd_setinventory(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setinventory logic...
        return "[IMMORTAL] Setinventory command executed."

    def cmd_setequipment(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setequipment logic...
        return "[IMMORTAL] Setequipment command executed."

    def cmd_setresist(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setresist logic...
        return "[IMMORTAL] Setresist command executed."

    def cmd_setimmune(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setimmune logic...
        return "[IMMORTAL] Setimmune command executed."

    def cmd_setaffinity(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setaffinity logic...
        return "[IMMORTAL] Setaffinity command executed."

    def cmd_setai(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setai logic...
        return "[IMMORTAL] Setai command executed."

    def cmd_setimmortal(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setimmortal logic...
        return "[IMMORTAL] Setimmortal command executed."

    def cmd_setpassword(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setpassword logic...
        return "[IMMORTAL] Setpassword command executed."

    def cmd_setemail(self, character, args):
        check = self._immortal_only(character)
        if check: return check
        # ...existing setemail logic...
        return "[IMMORTAL] Setemail command executed."
    def cmd_spells(self, character, args):
        lines = ["Spells Known and Spells Per Day:"]
        spellcasting = character.get_spellcasting_info() if hasattr(character, 'get_spellcasting_info') else None
        if spellcasting:
            lines.append(f"Spellcasting Type: {spellcasting.get('type','-')}, Starts at Level: {spellcasting.get('start_level','-')}")
        # Spells known: dict of level -> list of spell names
        spells_known = getattr(character, 'spells_known', {})
        if spells_known:
            lines.append("Spells Known:")
            for lvl in sorted(spells_known.keys()):
                spell_list = spells_known[lvl]
                lines.append(f"  Level {lvl}: {', '.join(spell_list) if spell_list else 'None'}")
        else:
            lines.append("Spells Known: None")
        # Spells per day: dict of level -> int
        spells_per_day = getattr(character, 'spells_per_day', {})
        if spells_per_day:
            lines.append("Spells Per Day:")
            for lvl in sorted(spells_per_day.keys()):
                lines.append(f"  Level {lvl}: {spells_per_day[lvl]}")
        else:
            lines.append("Spells Per Day: None")
        return "\n".join(lines)

    def cmd_skills(self, character, args):
        lines = ["Skills, Feats, and Class Features:"]
        # Skills
        skills = getattr(character, 'skills', {})
        if hasattr(character, 'get_class_skills'):
            class_skills = character.get_class_skills()
            lines.append(f"Class Skills: {', '.join(class_skills) if class_skills else 'None'}")
        if skills:
            lines.append("Skills:")
            for skill, value in skills.items():
                lines.append(f"  {skill}: {value}")
        else:
            lines.append("Skills: None")
        # Feats
        feats = getattr(character, 'feats', [])
        if feats:
            lines.append("Feats:")
            for feat in feats:
                lines.append(f"  {feat}")
        else:
            lines.append("Feats: None")
        # Class Features
        if hasattr(character, 'get_class_features'):
            features = character.get_class_features()
            if features:
                lines.append("Class Features:")
                for feature in features:
                    lines.append(f"  {feature}")
            else:
                lines.append("Class Features: None")
        return "\n".join(lines)

    def cmd_score(self, character, args):
        width = 80
        def pad_line(content):
            # Pads content to width, with | at start and end
            return f"|{content}{' ' * (width - len(content))}|"

        lines = []
        lines.append("+" + "-"*width + "+")
        lines.append(pad_line(f" Name: {character.name:<20} Level: {character.level:<3}  Title: {str(character.title or '')[:30]:<30}"))
        lines.append(pad_line(f" Race: {str(character.race)[:20]:<20} Class: {str(getattr(character, 'char_class', 'Adventurer'))[:20]:<20}"))
        # Class details removed for player score output

        lines.append("+" + "-"*width + "+")

        # Section 2: Roleplay/Meta
        alignment = str(getattr(character, 'alignment', 'Unaligned') or 'Unaligned')
        deity = str(getattr(character, 'deity', 'None') or 'None')
        lines.append(pad_line(f" Alignment: {alignment:<20} Deity: {deity:<30}"))
        lines.append(pad_line(f" Size: {str(getattr(character, 'size', 'Medium')):<10} Speed: {str(getattr(character, 'speed', character.move)):<4} ft.   Immortal: {'Yes' if character.is_immortal else 'No':<3}   Elemental Affinity: {str(character.elemental_affinity or 'None'):<15}"))
        lines.append("+" + "-"*width + "+")

        # Section 3: Combat
        lines.append(pad_line(f" HP: {character.hp:>3}/{character.max_hp:<3}  AC: {character.ac:<2}  Touch AC: {getattr(character, 'touch_ac', character.ac):<2}  Flat-Footed AC: {getattr(character, 'flat_ac', character.ac):<2}"))
        lines.append(pad_line(f" BAB: {getattr(character, 'bab', (character.level * 3) // 4):<2}  Grapple: {getattr(character, 'grapple', (character.level * 3) // 4 + (character.str_score - 10) // 2):<2}"))

        # D&D 3.5 Save Calculation
        def calc_save(save_type):
            class_data = character.get_class_data()
            prog = class_data.get('save_progression', {}).get(save_type, 'poor')
            lvl = getattr(character, 'class_level', character.level)
            if prog == 'good':
                base = 2 + (lvl // 2)
            else:
                base = lvl // 3
            if save_type == 'fort':
                mod = (character.con_score - 10) // 2
            elif save_type == 'ref':
                mod = (character.dex_score - 10) // 2
            else:
                mod = (character.wis_score - 10) // 2
            return base + mod

        fort = calc_save('fort')
        ref = calc_save('ref')
        will = calc_save('will')
        lines.append(pad_line(f" Saves: Fortitude: {fort:<2}  Reflex: {ref:<2}  Will: {will:<2}"))
        lines.append("+" + "-"*width + "+")

        # Section 4: Stats
        lines.append(pad_line(f" STR: {character.str_score:<2}  DEX: {character.dex_score:<2}  CON: {character.con_score:<2}  INT: {character.int_score:<2}  WIS: {character.wis_score:<2}  CHA: {character.cha_score:<2}"))
        lines.append("+" + "-"*width + "+")

        # Section 5: XP, Resistances, Immunities
        lines.append(pad_line(f" XP: {character.xp:<12}"))
        lines.append(pad_line(f" Resistances: {', '.join(getattr(character, 'resistances', [])) or 'None'}"))
        lines.append(pad_line(f" Immunities: {', '.join(getattr(character, 'immunities', [])) or 'None'}"))
        lines.append("+" + "-"*width + "+")

        # Section 6: Active Effects
        effects = getattr(character, 'active_effects', [])
        if effects:
            effect_line = f" Active Conditions/Status Effects: {', '.join(str(e) for e in effects)}"
            lines.append(pad_line(effect_line))
            lines.append("+" + "-"*width + "+")

        return "\n".join(lines)

    def cmd_companion(self, character, args):
        lines = ["Companion(s):"]
        companions = getattr(character, 'companions', [])
        if not companions:
            lines.append("  None")
        else:
            for comp in companions:
                lines.append(f"- {comp}")
        return "\n".join(lines)

    def cmd_questpage(self, character, args):
        lines = ["Quest Log and Reputation:"]
        # Reputation/Standing
        rep = getattr(character, 'reputation', {})
        if rep:
            lines.append("Reputation/Standing:")
            for faction, value in rep.items():
                lines.append(f"  {faction}: {value}")
        else:
            lines.append("Reputation/Standing: None")
        # Quest log
        quests = getattr(character, 'quest_log', [])
        if quests:
            lines.append("Quest Log:")
            for quest in quests:
                lines.append(f"  {quest}")
        else:
            lines.append("Quest Log: None")
        return "\n".join(lines)

    def cmd_help(self, character, args):
        if args and args.strip().lower() == "prompt":
            return (
                "Prompt Customization:\n"
                "You can change your prompt using the 'setprompt' command.\n"
                "Example: setprompt AC %a HP %h/%H EXP %x>\n"
                "Available prompt codes:\n"
                "  %a = AC, %h = HP, %H = Max HP, %x = XP to next level, %RACE = your race,\n"
                "  %v = Move, %V = Max Move,\n"
                "  %s = Str, %d = Dex, %c = Con, %i = Int, %w = Wis, %c = Cha, %s = [Immortal] if immortal.\n"
                "Type 'setprompt <your prompt>' to change it."
            )
        cmds = sorted(self.commands.keys())
        help_text = "Available commands: " + ", ".join(cmds)
        help_text += "\nType 'help <topic>' for more info. For prompt customization, type 'help prompt'."
        return help_text

    def cmd_get(self, character, args):
        # Find item in room by name
        if not args:
            return "Get what?"
        item = next((i for i in character.room.items if i.name.lower() == args.lower()), None)
        if not item:
            return f"No {args} here."
        character.room.items.remove(item)
        character.inventory.append(item)
        return f"You pick up {item.name}."

    def cmd_drop(self, character, args):
        # Find item in inventory by name
        if not args:
            return "Drop what?"
        item = next((i for i in character.inventory if i.name.lower() == args.lower()), None)
        if not item:
            return f"You don't have {args}."
        character.inventory.remove(item)
        character.room.items.append(item)
        return f"You drop {item.name}."

    def cmd_inventory(self, character, args):
        total_weight = sum(getattr(item, 'weight', 0) for item in character.inventory)
        # D&D 3.5 encumbrance thresholds (simplified):
        light = character.str_score * 5
        medium = character.str_score * 10
        heavy = character.str_score * 15
        if total_weight <= light:
            enc = "Light"
        elif total_weight <= medium:
            enc = "Medium"
        elif total_weight <= heavy:
            enc = "Heavy"
        else:
            enc = "Overloaded!"
        lines = [f"You are carrying ({total_weight} lbs): Encumbrance: {enc}"]
        if not character.inventory:
            lines.append("  (nothing)")
        else:
            for item in character.inventory:
                lines.append(f"- {item.name} (wt {item.weight})")
        return "\n".join(lines)

    def cmd_look(self, character, args):
        desc = character.room.description
        # List mobs in the room
        mob_lines = []
        for mob in character.room.mobs:
            if hasattr(mob, 'alive') and not mob.alive:
                continue
            mob_lines.append(f"You see {mob.name} here.")
        if mob_lines:
            desc += "\n" + "\n".join(mob_lines)
        return desc

    def cmd_say(self, character, args):
        return f"{character.name} says, '{args}'"

    def cmd_kill(self, character, args):
        target = next((m for m in character.room.mobs if m.name.lower() == args.lower() and m.alive), None)
        if target:
            character.state = State.COMBAT
            return attack(character, target)
        return "No such target!"

    def cmd_move(self, character, args):
        direction = args.lower()
        if direction in character.room.exits:
            new_vnum = character.room.exits[direction]
            if new_vnum in self.world.rooms:
                next_room = self.world.rooms[new_vnum]
                fastmove_flags = {"difficult", "obstacle", "stairs", "slope", "undergrowth", "heavy_undergrowth", "water", "shallow_water", "ice", "sand", "elevation", "rough"}
                hard_flags = {"deep_water", "trap", "dark", "cover"}
                if character.char_class == "Barbarian" and "Fast Movement" in character.get_class_features():
                    for flag in next_room.flags:
                        if flag.lower() in hard_flags:
                            return f"You cannot move into {next_room.name} due to {flag.replace('_', ' ')}."
                    # Ignore fastmove_flags
                else:
                    for flag in next_room.flags:
                        if flag.lower() in hard_flags or flag.lower() in fastmove_flags:
                            return f"You are impeded by {flag.replace('_', ' ')} and cannot move that way."
                character.room.players.remove(character)
                character.room = next_room
                character.room.players.append(character)
                look_output = self.cmd_look(character, "")
                return f"You move {direction} to {character.room.name}.\n{look_output}"
        return "No exit that way!"

    def cmd_exits(self, character, args):
        # Only show exits that are connected to existing rooms
        connected_exits = []
        for direction, vnum in character.room.exits.items():
            if vnum in self.world.rooms:
                connected_exits.append(direction)
        if connected_exits:
            return "Exits: " + ", ".join(connected_exits)
        else:
            return "No visible exits."

    def cmd_quest(self, character, args):
        if args.lower() == "start" and 1 not in [q["id"] for q in character.quests]:
            character.quests.append(self.world.quests[1])
            return f"Quest started: {self.world.quests[1]['name']}"
        return "Quest status: " + (f"{character.quests[0]['name']}" if character.quests else "No active quests.")

    def cmd_gecho(self, character, args):
        if not character.is_immortal:
            return "Command restricted to immortals!"
        return f"[GLOBAL] {character.name} broadcasts: {args}"

    def cmd_who(self, character, args):
        return self.world.do_who()

    def cmd_stats(self, character, args):
        return character.toggle_stats()

    # --- D&D 3.5 Skill Command Stubs ---

    def cmd_balance(self, character, args):
        result = character.skill_check("Balance")
        return f"You attempt to keep your balance. Skill check result: {result}"

    def cmd_bluff(self, character, args):
        result = character.skill_check("Bluff")
        return f"You attempt to bluff. Skill check result: {result}"

    def cmd_climb(self, character, args):
        result = character.skill_check("Climb")
        return f"You attempt to climb. Skill check result: {result}"

    def cmd_concentration(self, character, args):
        result = character.skill_check("Concentration")
        return f"You focus your concentration. Skill check result: {result}"

    def cmd_decipher(self, character, args):
        result = character.skill_check("Decipher Script")
        return f"You attempt to decipher the script. Skill check result: {result}"

    def cmd_diplomacy(self, character, args):
        result = character.skill_check("Diplomacy")
        return f"You attempt diplomacy. Skill check result: {result}"

    def cmd_disable(self, character, args):
        result = character.skill_check("Disable Device")
        return f"You attempt to disable the device. Skill check result: {result}"

    def cmd_disguise(self, character, args):
        result = character.skill_check("Disguise")
        return f"You attempt to disguise yourself. Skill check result: {result}"

    def cmd_escape(self, character, args):
        result = character.skill_check("Escape Artist")
        return f"You attempt to escape. Skill check result: {result}"

    def cmd_forgery(self, character, args):
        result = character.skill_check("Forgery")
        return f"You attempt to forge a document. Skill check result: {result}"

    def cmd_gather(self, character, args):
        result = character.skill_check("Gather Information")
        return f"You attempt to gather information. Skill check result: {result}"

    def cmd_handle(self, character, args):
        result = character.skill_check("Handle Animal")
        return f"You attempt to handle the animal. Skill check result: {result}"

    def cmd_heal(self, character, args):
        result = character.skill_check("Heal")
        return f"You attempt to heal. Skill check result: {result}"

    def cmd_hide(self, character, args):
        result = character.skill_check("Hide")
        return f"You attempt to hide. Skill check result: {result}"

    def cmd_intimidate(self, character, args):
        result = character.skill_check("Intimidate")
        return f"You attempt to intimidate. Skill check result: {result}"

    def cmd_jump(self, character, args):
        result = character.skill_check("Jump")
        return f"You attempt to jump. Skill check result: {result}"

    def cmd_knowledge(self, character, args):
        # args should specify the knowledge type
        skill = f"Knowledge ({args.strip().lower()})" if args else "Knowledge (arcana)"
        result = character.skill_check(skill.title())
        return f"You recall knowledge about {args or 'arcana'}. Skill check result: {result}"

    def cmd_listen(self, character, args):
        result = character.skill_check("Listen")
        return f"You attempt to listen carefully. Skill check result: {result}"

    def cmd_movesilently(self, character, args):
        result = character.skill_check("Move Silently")
        return f"You attempt to move silently. Skill check result: {result}"

    def cmd_openlock(self, character, args):
        result = character.skill_check("Open Lock")
        return f"You attempt to open the lock. Skill check result: {result}"

    def cmd_perform(self, character, args):
        result = character.skill_check("Perform (any)")
        return f"You attempt to perform. Skill check result: {result}"

    def cmd_profession(self, character, args):
        result = character.skill_check("Profession (any)")
        return f"You attempt to use your profession. Skill check result: {result}"

    def cmd_ride(self, character, args):
           result = character.activate_rage()
           return result

    def cmd_search(self, character, args):
           result = character.deactivate_rage()
           return result

    def cmd_rest(self, character, args):
        """Rest to reset rages used and remove fatigue."""
        return character.rest()

    def cmd_sensemotive(self, character, args):
        result = character.skill_check("Sense Motive")
        return f"You attempt to sense motive. Skill check result: {result}"

    def cmd_sleight(self, character, args):
        result = character.skill_check("Sleight of Hand")
        return f"You attempt sleight of hand. Skill check result: {result}"

    def cmd_spellcraft(self, character, args):
        result = character.skill_check("Spellcraft")
        return f"You attempt to identify magic. Skill check result: {result}"

    def cmd_spot(self, character, args):
        result = character.skill_check("Spot")
        return f"You attempt to spot something. Skill check result: {result}"

    def cmd_survival(self, character, args):
        result = character.skill_check("Survival")
        return f"You attempt to survive in the wild. Skill check result: {result}"

    def cmd_swim(self, character, args):
        result = character.skill_check("Swim")
        return f"You attempt to swim. Skill check result: {result}"

    def cmd_tumble(self, character, args):
        result = character.skill_check("Tumble")
        return f"You attempt to tumble. Skill check result: {result}"

    def cmd_usemagic(self, character, args):
        result = character.skill_check("Use Magic Device")
        return f"You attempt to use a magic device. Skill check result: {result}"

    def cmd_userope(self, character, args):
        result = character.skill_check("Use Rope")
        return f"You attempt to use a rope. Skill check result: {result}"

    def cmd_help_feats(self, character, args):
        """
        Show all feats, their type (passive/active), description, and usage if active.
        Usage: help feats [<feat name>]
        """
        from oreka_mud.src.feats import FEATS
        lines = []
        if args:
            name = args.strip().lower()
            # Try to find the feat by name (case-insensitive, partial match allowed)
            for feat_key, feat in FEATS.items():
                if name in feat_key.lower():
                    lines.append(f"{feat.name}:")
                    lines.append(f"  Description: {feat.description}")
                    # Determine passive/active
                    if feat.effect is None:
                        lines.append("  Type: Passive (always on or handled automatically)")
                        lines.append("  Usage: This feat is always in effect or handled by the system.")
                    else:
                        # Heuristic: if effect expects a target, it's active
                        import inspect
                        params = inspect.signature(feat.effect).parameters
                        if any(p in params for p in ("target", "targets")):
                            lines.append("  Type: Active (requires a command or action)")
                            # Suggest usage based on feat name
                            if "disarm" in feat.name.lower():
                                lines.append("  Usage: Use the 'disarm <target>' command in combat.")
                            elif "trip" in feat.name.lower():
                                lines.append("  Usage: Use the 'trip <target>' command in combat.")
                            elif "bull rush" in feat.name.lower():
                                lines.append("  Usage: Use the 'bullrush <target>' command in combat.")
                            elif "grapple" in feat.name.lower():
                                lines.append("  Usage: Use the 'grapple <target>' command in combat.")
                            elif "overrun" in feat.name.lower():
                                lines.append("  Usage: Use the 'overrun <target>' command in combat.")
                            elif "sunder" in feat.name.lower():
                                lines.append("  Usage: Use the 'sunder <target>' command in combat.")
                            elif "whirlwind" in feat.name.lower():
                                lines.append("  Usage: Use the 'whirlwind' command in combat.")
                            elif "spring attack" in feat.name.lower():
                                lines.append("  Usage: Use the 'springattack <target>' command in combat.")
                            elif "stunning fist" in feat.name.lower():
                                lines.append("  Usage: Use the 'stunningfist <target>' command in combat.")
                            elif "feint" in feat.name.lower():
                                lines.append("  Usage: Use the 'feint <target>' command in combat.")
                            else:
                                lines.append("  Usage: This feat is used via a special command or action in combat.")
                        else:
                            lines.append("  Type: Passive (always on or handled automatically)")
                            lines.append("  Usage: This feat is always in effect or handled by the system.")
                    return "\n".join(lines)
            return "No such feat found. Type 'help feats' to see all feats."
        # No args: list all feats
        lines.append("Feats List:")
        for feat in sorted(FEATS.values(), key=lambda f: f.name):
            if feat.effect is None:
                ftype = "Passive"
            else:
                import inspect
                params = inspect.signature(feat.effect).parameters
                if any(p in params for p in ("target", "targets")):
                    ftype = "Active"
                else:
                    ftype = "Passive"
            lines.append(f"- {feat.name}: {ftype} - {feat.description}")
        lines.append("\nType 'help feats <feat name>' for details on a specific feat.")
        return "\n".join(lines)

    # (Removed duplicate cmd_help definition; keep only the previous implementation above.)

    def cmd_levelup(self, character, args):
        """
        Level up the character by 1 and trigger Bonus Feat selection if eligible.
        """
        import asyncio
        old_level = getattr(character, 'class_level', 1)
        new_level = old_level + 1
        character.set_level(new_level)
    def cmd_help(self, character, *args):
        """Show help for commands, classes, or topics."""
        topic = " ".join(args).strip().lower()
        if topic == "barbarian":
            return (
                "Barbarian (D&D 3.5e OGL)\n"
                "\n"
                "Class Skills:\n"
                "  Climb, Craft (any), Handle Animal, Intimidate, Jump, Listen, Ride, Survival, Swim\n"
                "\n"
                "Common Feats:\n"
                "  Power Attack, Cleave, Great Cleave, Toughness, Improved Initiative, Dodge, Mobility,\n"
                "  Spring Attack, Weapon Finesse, Alertness\n"
                "\n"
                "Class Features & Progression:\n"
                "  1: Fast Movement, Illiteracy, Rage 1/day\n"
                "  2: Uncanny Dodge\n"
                "  3: Trap Sense +1\n"
                "  4: Rage 2/day\n"
                "  5: Improved Uncanny Dodge\n"
                "  6: Trap Sense +2\n"
                "  7: Damage Reduction 1/-\n"
                "  8: Rage 3/day\n"
                "  9: Trap Sense +3\n"
                " 10: Damage Reduction 2/-\n"
                " 11: Greater Rage\n"
                " 12: Rage 4/day, Trap Sense +4\n"
                " 13: Damage Reduction 3/-\n"
                " 14: Indomitable Will\n"
                " 15: Trap Sense +5\n"
                " 16: Damage Reduction 4/-, Rage 5/day\n"
                " 17: Tireless Rage\n"
                " 18: Trap Sense +6\n"
                " 19: Damage Reduction 5/-\n"
                " 20: Mighty Rage, Rage 6/day\n"
                "\n"
                "Ability Score Increases: Levels 4, 8, 12, 16, 20\n"
                "General Feats: Levels 1, 3, 6, 9, 12, 15, 18\n"
                "\n"
                "Special: Barbarians are illiterate by default, but can learn literacy.\n"
                "Rage grants bonuses to Strength, Constitution, HP, and AC penalty. Upgrades at higher levels.\n"
                "Fast Movement increases speed and initiative, ignores most terrain penalties in light armor.\n"
                "Damage Reduction reduces incoming physical damage.\n"
                "Trap Sense grants bonuses to Reflex saves and trap detection.\n"
                "Uncanny Dodge prevents being caught flat-footed; Improved Uncanny Dodge grants immunity to sneak attacks.\n"
                "Indomitable Will grants bonus on Will saves vs enchantments.\n"
            )
        # ...existing help logic...



    

    def cmd_cast(self, character, args):
        """Cast a prepared or known spell."""
        return character.cast_spell(args.strip())

    def cmd_prepare(self, character, args):
        """Prepare a spell for the day."""
        parts = args.strip().split()
        if len(parts) < 2:
            return "Usage: prepare <spell name> <level>"
        spell_name, level = parts[0], int(parts[1])
        character.prepare_spell(spell_name, level)
        return f"Prepared {spell_name} at level {level}."

    def cmd_turn(self, character, args):
        """Turn or rebuke undead."""
        return character.turn_undead()

    def cmd_domain(self, character, args):
        """Show available domain spells."""
        domains = character.get_available_domain_spells()
        return f"Domain spells: {domains}"
    

   

def cmd_help(self, character, *args):
    topic = " ".join(args).strip().lower()
    if topic == "cleric":
        return (
            "Cleric (D&D 3.5e OGL)\n"
            "\n"
            "Class Skills:\n"
            "  Concentration, Craft (any), Diplomacy, Heal, Knowledge (arcana), Knowledge (religion), Profession (any), Spellcraft\n"
            "\n"
            "Domains:\n"
            "  Air, Chaos, Death, Earth, Evil, Fire, Good, Healing, Knowledge, Law, Luck, Magic, Plant, Protection, Strength, Sun, Travel, Trickery, War, Water\n"
            "\n"
            "Common Feats:\n"
            "  Extra Turning, Improved Turning, Divine Metamagic, Augment Healing, Empower Spell, Quicken Spell, Spell Focus, Combat Casting\n"
            "\n"
            "Common Spells:\n"
            "  Cure Light Wounds, Bless, Shield of Faith, Detect Magic, Divine Favor, Hold Person, Prayer, Dispel Magic, Cure Serious Wounds, Flame Strike, Raise Dead, Greater Command, Holy Smite, Righteous Might, Mass Cure Light Wounds, Blade Barrier, Resurrection, Earthquake, Gate\n"
            "\n"
            "Class Features:\n"
            "  Divine Spellcasting, Turn/Rebuke Undead, Spontaneous Cure/Inflict, Domain Spells, Channel Energy (optional), Deity & Alignment Restrictions\n"
            "\n"
            "Progression Table:\n"
            "  1: Divine Spellcasting, Turn/Rebuke Undead, Domains, Spontaneous Cure/Inflict\n"
            "  2: New spell levels, domain spells\n"
            "  3: Bonus feat\n"
            "  6: Bonus feat\n"
            "  9: Bonus feat\n"
            " 12: Bonus feat\n"
            " 15: Bonus feat\n"
            " 18: Bonus feat\n"
            "\n"
            "Special: Clerics must choose a deity and alignment. Some spells are restricted by alignment.\n"
            "Turn Undead allows you to repel or destroy undead creatures.\n"
            "Domains grant special powers and extra spells.\n"
        )
    # ...existing help logic...
    

    