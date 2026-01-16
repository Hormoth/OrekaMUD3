from src.combat import attack
from src.character import State
from src import quests

class CommandParser:
    def cmd_progression(self, character, args):
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

    def cmd_talk(self, character, args):
        """Talk to the shopkeeper in the room for a greeting or info."""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        dialogue = getattr(shopkeeper, 'dialogue', None)
        if dialogue:
            return f"{shopkeeper.name} says: '{dialogue}'"
        # Default dialogue
        return f"{shopkeeper.name} says: 'Welcome! Type list to see my wares, buy <item> to purchase, sell <item> to sell, or appraise <item> for a price.'"
    def _find_shopkeeper(self, character):
        # Return the first shopkeeper mob in the room, or None
        for mob in getattr(character.room, 'mobs', []):
            if hasattr(mob, 'is_shopkeeper') and mob.is_shopkeeper():
                return mob
        return None

    def cmd_list(self, character, args):
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
        return f"You sell {item.name} for {price} gp."
    def cmd_components(self, character, args):
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
            from src.spells import SPELLS
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
    def cmd_saveplayer(self, character, args):
        """@saveplayer <name> | Force-save a player's data (admin only)."""
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        from src.character import Character
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
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        from src.character import Character
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
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        from src.character import Character
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
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @mobadd <name>"
        from src.mob import Mob
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
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @itemadd <name>"
        from src.items import Item
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
        return f"Item has no field '{field}'."
    def cmd_cast(self, character, args):
        """Casts a spell if prepared/known and slots are available, enforcing V/S and concentration."""
        from src.spells import get_spell_by_name
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

        # Execute the spell effect
        effect_result = self._execute_spell(character, spell_name, args, spell_level)

        # Add slot info
        slots_remaining = character.spells_per_day.get(spell_level, 0)
        return f"{effect_result}\nSlots left for level {spell_level}: {slots_remaining}"

    def _execute_spell(self, caster, spell_name, args, spell_level):
        """Execute the actual spell effect - damage, healing, buffs, conditions."""
        import random
        from src.spells import (
            get_spell, calculate_spell_damage, calculate_healing,
            calculate_spell_dc, calculate_caster_level, get_num_missiles,
            get_num_rays, SaveType, SpellEffectType, TargetType
        )
        from src import conditions as cond

        spell = get_spell(spell_name)
        if not spell:
            return f"You cast {spell_name}! (Effect not implemented)"

        char_class = getattr(caster, 'char_class', 'Wizard')
        caster_level = calculate_caster_level(caster, char_class)
        results = [f"You cast {spell.name}!"]

        # Determine target
        target = None
        target_name = args.split()[-1] if args and len(args.split()) > len(spell_name.split()) else None

        # For self-targeted spells
        if spell.target_type == TargetType.SELF:
            target = caster
        # For touch/single target spells, find target
        elif spell.target_type in (TargetType.TOUCH, TargetType.RANGED_TOUCH, TargetType.SINGLE):
            if target_name:
                # Look for target in room
                if hasattr(caster, 'room') and caster.room:
                    # Check mobs
                    for mob in getattr(caster.room, 'mobs', []):
                        if hasattr(mob, 'name') and mob.name.lower() == target_name.lower():
                            if hasattr(mob, 'alive') and mob.alive:
                                target = mob
                                break
                    # Check players
                    if not target:
                        for player in getattr(caster.room, 'players', []):
                            if hasattr(player, 'name') and player.name.lower() == target_name.lower():
                                target = player
                                break
            # Default to self for buffs/healing without target
            if not target and spell.effect_type in (SpellEffectType.BUFF, SpellEffectType.HEALING, SpellEffectType.PROTECTION):
                target = caster

        # Handle touch attacks
        if spell.target_type == TargetType.RANGED_TOUCH and target and target != caster:
            # Roll ranged touch attack
            attack_roll = random.randint(1, 20)
            attack_bonus = (getattr(caster, 'level', 1) // 2) + ((getattr(caster, 'dex_score', 10) - 10) // 2)
            total_attack = attack_roll + attack_bonus
            target_touch_ac = 10 + ((getattr(target, 'dex_score', 10) - 10) // 2)

            if attack_roll == 1 or (attack_roll != 20 and total_attack < target_touch_ac):
                results.append(f"Ranged touch attack misses {target.name}! ({total_attack} vs Touch AC {target_touch_ac})")
                return "\n".join(results)
            results.append(f"Ranged touch attack hits {target.name}! ({total_attack} vs Touch AC {target_touch_ac})")

        elif spell.target_type == TargetType.TOUCH and target and target != caster:
            # Touch attack (melee)
            attack_roll = random.randint(1, 20)
            attack_bonus = (getattr(caster, 'level', 1) // 2) + ((getattr(caster, 'str_score', 10) - 10) // 2)
            total_attack = attack_roll + attack_bonus
            target_touch_ac = 10 + ((getattr(target, 'dex_score', 10) - 10) // 2)

            # For healing/buff spells on allies, auto-hit
            if spell.effect_type not in (SpellEffectType.DAMAGE, SpellEffectType.CONDITION, SpellEffectType.DEBUFF):
                pass  # Auto-hit friendly spells
            elif attack_roll == 1 or (attack_roll != 20 and total_attack < target_touch_ac):
                results.append(f"Touch attack misses {target.name}! ({total_attack} vs Touch AC {target_touch_ac})")
                return "\n".join(results)
            else:
                results.append(f"Touch attack hits {target.name}!")

        # Calculate saving throw DC
        spell_dc = calculate_spell_dc(caster, spell, char_class)

        # Handle different spell effect types
        # =====================================================================
        # DAMAGE SPELLS
        # =====================================================================
        if spell.effect_type == SpellEffectType.DAMAGE and spell.damage_dice:
            targets_hit = []

            # Area spells hit multiple targets
            if spell.target_type in (TargetType.AREA_BURST, TargetType.AREA_CONE, TargetType.AREA_LINE, TargetType.AREA_SPREAD):
                if hasattr(caster, 'room') and caster.room:
                    # Hit all mobs in room
                    for mob in getattr(caster.room, 'mobs', []):
                        if hasattr(mob, 'alive') and mob.alive:
                            targets_hit.append(mob)
            elif target:
                targets_hit.append(target)

            if not targets_hit:
                results.append("No valid targets!")
                return "\n".join(results)

            # Special handling for Magic Missile (auto-hit, multiple missiles)
            if spell.name.lower() == "magic missile":
                num_missiles = get_num_missiles(caster_level)
                total_damage = 0
                for _ in range(num_missiles):
                    missile_dmg = random.randint(1, 4) + 1
                    total_damage += missile_dmg

                # Distribute damage (simplified: all at one target)
                for t in targets_hit[:1]:
                    # Check for Shield spell immunity
                    if hasattr(t, 'active_buffs') and t.active_buffs.get('immune_magic_missile'):
                        results.append(f"{t.name}'s Shield blocks the missiles!")
                        continue

                    t.hp = max(0, t.hp - total_damage)
                    results.append(f"{num_missiles} missiles strike {t.name} for {total_damage} force damage!")

                    if t.hp <= 0:
                        if hasattr(t, 'alive'):
                            t.alive = False
                        results.append(f"{t.name} is slain!")
                        # Quest trigger
                        if hasattr(caster, 'quest_log'):
                            mob_type = getattr(t, 'mob_type', t.name.lower())
                            quest_updates = quests.on_mob_killed(caster, mob_type)
                            for update in quest_updates:
                                results.append(f"[Quest] {update}")

            # Special handling for Scorching Ray (multiple rays)
            elif spell.name.lower() == "scorching ray":
                num_rays = get_num_rays(caster_level)
                for i, t in enumerate(targets_hit[:num_rays]):
                    damage, dice_str = calculate_spell_damage(caster, spell.damage_dice, char_class)
                    t.hp = max(0, t.hp - damage)
                    results.append(f"Ray {i+1} hits {t.name} for {damage} fire damage! ({dice_str})")

                    if t.hp <= 0:
                        if hasattr(t, 'alive'):
                            t.alive = False
                        results.append(f"{t.name} is slain!")

            # Standard damage spell
            else:
                damage, dice_str = calculate_spell_damage(caster, spell.damage_dice, char_class)

                for t in targets_hit:
                    final_damage = damage

                    # Saving throw
                    if spell.save_type != SaveType.NONE:
                        save_roll = random.randint(1, 20)
                        save_bonus = 0
                        if spell.save_type == SaveType.REFLEX:
                            save_bonus = ((getattr(t, 'dex_score', 10) - 10) // 2) + (getattr(t, 'level', 1) // 2)
                        elif spell.save_type == SaveType.FORTITUDE:
                            save_bonus = ((getattr(t, 'con_score', 10) - 10) // 2) + (getattr(t, 'level', 1) // 2)
                        elif spell.save_type == SaveType.WILL:
                            save_bonus = ((getattr(t, 'wis_score', 10) - 10) // 2) + (getattr(t, 'level', 1) // 2)

                        total_save = save_roll + save_bonus

                        if total_save >= spell_dc:
                            if spell.save_effect.value == "half":
                                final_damage = damage // 2
                                results.append(f"{t.name} makes save ({total_save} vs DC {spell_dc}) - half damage!")
                            elif spell.save_effect.value == "negates":
                                results.append(f"{t.name} makes save ({total_save} vs DC {spell_dc}) - no effect!")
                                continue
                        else:
                            results.append(f"{t.name} fails save ({total_save} vs DC {spell_dc})!")

                    t.hp = max(0, t.hp - final_damage)
                    damage_type = spell.damage_type or "magical"
                    results.append(f"{t.name} takes {final_damage} {damage_type} damage! ({dice_str})")

                    if t.hp <= 0:
                        if hasattr(t, 'alive'):
                            t.alive = False
                        results.append(f"{t.name} is slain!")
                        # Quest trigger
                        if hasattr(caster, 'quest_log'):
                            mob_type = getattr(t, 'mob_type', t.name.lower())
                            quest_updates = quests.on_mob_killed(caster, mob_type)
                            for update in quest_updates:
                                results.append(f"[Quest] {update}")

        # =====================================================================
        # HEALING SPELLS
        # =====================================================================
        elif spell.effect_type == SpellEffectType.HEALING and spell.healing_dice:
            if not target:
                target = caster

            healing, dice_str = calculate_healing(caster, spell.healing_dice, char_class)
            old_hp = target.hp
            target.hp = min(target.max_hp, target.hp + healing)
            actual_heal = target.hp - old_hp

            if target == caster:
                results.append(f"You heal yourself for {actual_heal} HP! ({dice_str}) [HP: {target.hp}/{target.max_hp}]")
            else:
                results.append(f"You heal {target.name} for {actual_heal} HP! ({dice_str}) [HP: {target.hp}/{target.max_hp}]")

        # =====================================================================
        # BUFF SPELLS
        # =====================================================================
        elif spell.effect_type == SpellEffectType.BUFF and spell.buff_effects:
            if not target:
                target = caster

            # Initialize active_buffs if needed
            if not hasattr(target, 'active_buffs'):
                target.active_buffs = {}

            # Apply buff effects
            buff_desc = []
            duration_rounds = spell.duration_rounds if spell.duration_rounds > 0 else caster_level * 10

            for buff_name, buff_value in spell.buff_effects.items():
                target.active_buffs[buff_name] = {
                    'value': buff_value,
                    'duration': duration_rounds,
                    'spell': spell.name
                }

                # Apply stat bonuses immediately
                if buff_name == 'str_bonus':
                    if not hasattr(target, 'temp_str_bonus'):
                        target.temp_str_bonus = 0
                    target.temp_str_bonus += buff_value
                    buff_desc.append(f"+{buff_value} Str")
                elif buff_name == 'dex_bonus':
                    if not hasattr(target, 'temp_dex_bonus'):
                        target.temp_dex_bonus = 0
                    target.temp_dex_bonus += buff_value
                    buff_desc.append(f"+{buff_value} Dex")
                elif buff_name == 'con_bonus':
                    if not hasattr(target, 'temp_con_bonus'):
                        target.temp_con_bonus = 0
                    target.temp_con_bonus += buff_value
                    buff_desc.append(f"+{buff_value} Con")
                elif buff_name == 'armor_bonus':
                    if not hasattr(target, 'temp_ac_bonus'):
                        target.temp_ac_bonus = 0
                    target.temp_ac_bonus += buff_value
                    buff_desc.append(f"+{buff_value} AC (armor)")
                elif buff_name == 'shield_bonus':
                    if not hasattr(target, 'temp_ac_bonus'):
                        target.temp_ac_bonus = 0
                    target.temp_ac_bonus += buff_value
                    buff_desc.append(f"+{buff_value} AC (shield)")
                elif buff_name == 'attack_bonus':
                    buff_desc.append(f"+{buff_value} attack")
                elif buff_name == 'save_bonus':
                    buff_desc.append(f"+{buff_value} saves")
                elif buff_name == 'invisible':
                    if hasattr(target, 'add_condition'):
                        target.add_condition('invisible')
                    buff_desc.append("Invisible")
                elif buff_name == 'fly_speed':
                    buff_desc.append(f"Fly {buff_value} ft.")
                elif buff_name == 'concealment':
                    buff_desc.append(f"{buff_value}% concealment")

            target_name = "yourself" if target == caster else target.name
            results.append(f"You enhance {target_name}: {', '.join(buff_desc)} for {duration_rounds} rounds!")

        # =====================================================================
        # CONDITION SPELLS (debuffs)
        # =====================================================================
        elif spell.effect_type == SpellEffectType.CONDITION and spell.condition_applied:
            if not target or target == caster:
                results.append("You need a target for this spell!")
                return "\n".join(results)

            # Saving throw
            saved = False
            if spell.save_type != SaveType.NONE:
                save_roll = random.randint(1, 20)
                save_bonus = 0
                if spell.save_type == SaveType.WILL:
                    save_bonus = ((getattr(target, 'wis_score', 10) - 10) // 2) + (getattr(target, 'level', 1) // 2)
                elif spell.save_type == SaveType.FORTITUDE:
                    save_bonus = ((getattr(target, 'con_score', 10) - 10) // 2) + (getattr(target, 'level', 1) // 2)
                elif spell.save_type == SaveType.REFLEX:
                    save_bonus = ((getattr(target, 'dex_score', 10) - 10) // 2) + (getattr(target, 'level', 1) // 2)

                total_save = save_roll + save_bonus

                if total_save >= spell_dc:
                    saved = True
                    if spell.save_effect.value == "negates":
                        results.append(f"{target.name} resists the spell! (Save {total_save} vs DC {spell_dc})")
                        return "\n".join(results)
                    elif spell.save_effect.value == "partial":
                        results.append(f"{target.name} partially resists! (Save {total_save} vs DC {spell_dc})")
                else:
                    results.append(f"{target.name} fails to resist! (Save {total_save} vs DC {spell_dc})")

            # Apply condition
            condition_name = spell.condition_applied
            duration = spell.condition_duration if spell.condition_duration > 0 else caster_level

            if hasattr(target, 'add_condition'):
                target.add_condition(condition_name)
            if hasattr(target, 'active_conditions'):
                target.active_conditions[condition_name] = duration

            condition_display = condition_name.replace('_', ' ').title()
            results.append(f"{target.name} is now {condition_display} for {duration} rounds!")

        # =====================================================================
        # PROTECTION SPELLS
        # =====================================================================
        elif spell.effect_type == SpellEffectType.PROTECTION:
            if not target:
                target = caster

            if not hasattr(target, 'active_buffs'):
                target.active_buffs = {}

            duration_rounds = spell.duration_rounds if spell.duration_rounds > 0 else caster_level * 10

            for buff_name, buff_value in spell.buff_effects.items():
                target.active_buffs[buff_name] = {
                    'value': buff_value,
                    'duration': duration_rounds,
                    'spell': spell.name
                }

            target_name = "yourself" if target == caster else target.name
            results.append(f"You protect {target_name} with {spell.name} for {duration_rounds} rounds!")

        # =====================================================================
        # UTILITY/OTHER SPELLS
        # =====================================================================
        else:
            results.append(spell.description)

        # Show remaining slots
        remaining = caster.spells_per_day.get(spell_level, 0)
        results.append(f"(Level {spell_level} slots remaining: {remaining})")

        return "\n".join(results)

    # ...existing code...
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
            "spellinfo": self.cmd_spellinfo,
            "spellbook": self.cmd_spellbook,
            "domains": self.cmd_domains,
            "prepare": self.cmd_prepare,
            "memorize": self.cmd_prepare,  # Alias
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
            # Equipment commands
            "wear": self.cmd_wear,
            "equip": self.cmd_wear,
            "remove": self.cmd_remove,
            "unequip": self.cmd_remove,
            "equipment": self.cmd_equipment,
            "eq": self.cmd_equipment,
            # Rest and recovery
            "rest": self.cmd_rest,
            "sleep": self.cmd_rest,
            # Status
            "conditions": self.cmd_conditions,
            "status": self.cmd_status,
            # Full attack
            "fullattack": self.cmd_fullattack,
            "fa": self.cmd_fullattack,
            # Admin condition commands
            "@addcondition": self.cmd_addcondition,
            "@removecondition": self.cmd_removecondition,
            "@listconditions": self.cmd_listconditions,
            # Combat maneuver commands
            "disarm": self.cmd_disarm,
            "trip": self.cmd_trip,
            "bullrush": self.cmd_bullrush,
            "grapple": self.cmd_grapple,
            "overrun": self.cmd_overrun,
            "sunder": self.cmd_sunder,
            "feint": self.cmd_feint,
            "whirlwind": self.cmd_whirlwind,
            "springattack": self.cmd_springattack,
            "stunningfist": self.cmd_stunningfist,
            "stun": self.cmd_stunningfist,
            "gdamage": self.cmd_grapple_damage,
            "gpin": self.cmd_grapple_pin,
            "gescape": self.cmd_grapple_escape,
        }

    # --- Builder Commands ---
    def cmd_dig(self, character, args):
        """@dig <direction> <room name> | Creates a new room in the given direction, linking it to the current room."""
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
        from src.room import Room
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

    def cmd_spellinfo(self, character, args):
        """Get detailed information about a specific spell."""
        from src.spells import describe_spell, get_spell
        if not args:
            return "Usage: spellinfo <spell name>"
        spell = get_spell(args)
        if not spell:
            return f"Unknown spell: {args}"
        return describe_spell(args)

    def cmd_spellbook(self, character, args):
        """List all spells available to your class organized by level."""
        from src.spells import get_spells_by_level, get_spell_count
        char_class = getattr(character, 'char_class', None)
        if not char_class:
            return "You have no class to learn spells from."

        # Check if class can cast spells
        from src.classes import CLASSES
        class_data = CLASSES.get(char_class, {})
        spellcasting = class_data.get('spellcasting')
        if not spellcasting:
            return f"{char_class}s do not cast spells."

        lines = [f"=== {char_class} Spellbook ==="]
        lines.append(f"Spellcasting: {spellcasting.get('type', 'Unknown').title()}")

        max_spell_level = min(9, (character.level + 1) // 2)  # Rough approximation

        for spell_level in range(0, max_spell_level + 1):
            spells = get_spells_by_level(char_class, spell_level)
            if spells:
                level_name = "Cantrips/Orisons" if spell_level == 0 else f"Level {spell_level}"
                lines.append(f"\n{level_name}:")
                for spell in spells:
                    lines.append(f"  {spell.name} - {spell.school.value}")

        lines.append(f"\nTotal spells in database: {get_spell_count()}")
        return "\n".join(lines)

    def cmd_domains(self, character, args):
        """Show domain spells and powers for divine casters."""
        from src.spells import get_domain_spells, get_domain_power, DOMAIN_DATA
        char_class = getattr(character, 'char_class', None)

        if char_class != "Cleric":
            return "Only Clerics have domains."

        domains = getattr(character, 'domains', [])
        if not domains:
            # Show available domains
            lines = ["You have not chosen your domains yet."]
            lines.append("\nAvailable Domains:")
            for domain_name in sorted(DOMAIN_DATA.keys()):
                power = get_domain_power(domain_name)
                lines.append(f"  {domain_name}: {power[:60]}...")
            return "\n".join(lines)

        lines = ["=== Your Domains ==="]
        for domain in domains:
            lines.append(f"\n--- {domain} Domain ---")
            power = get_domain_power(domain)
            lines.append(f"Granted Power: {power}")
            lines.append("Domain Spells:")
            domain_spells = get_domain_spells(domain)
            for level, spell_name in sorted(domain_spells.items()):
                lines.append(f"  {level}: {spell_name}")

        return "\n".join(lines)

    def cmd_prepare(self, character, args):
        """Prepare (memorize) a spell for prepared casters."""
        from src.spells import get_spell
        if not args:
            return "Usage: prepare <spell name>"

        # Check if character is a prepared caster
        char_class = getattr(character, 'char_class', None)
        spellcasting = character.get_spellcasting_info() if hasattr(character, 'get_spellcasting_info') else None

        if not spellcasting or spellcasting.get('type', '').lower() != 'prepared':
            # Wizards and Clerics are prepared, Sorcerers and Bards are spontaneous
            if char_class in ("Sorcerer", "Bard"):
                return f"As a {char_class}, you cast spells spontaneously and don't need to prepare them."
            elif char_class not in ("Wizard", "Cleric", "Druid", "Paladin", "Ranger"):
                return "You cannot prepare spells."

        spell = get_spell(args)
        if not spell:
            return f"Unknown spell: {args}"

        # Check if class can cast this spell
        if char_class not in spell.level:
            return f"{char_class}s cannot cast {spell.name}."

        spell_level = spell.level[char_class]

        # Initialize prepared_spells if needed
        if not hasattr(character, 'prepared_spells'):
            character.prepared_spells = {}
        if spell_level not in character.prepared_spells:
            character.prepared_spells[spell_level] = []

        # Check if we have slots available
        spells_per_day = getattr(character, 'spells_per_day', {})
        max_prepared = spells_per_day.get(spell_level, 0)
        current_prepared = len(character.prepared_spells.get(spell_level, []))

        if current_prepared >= max_prepared:
            return f"You cannot prepare any more level {spell_level} spells today. (Max: {max_prepared})"

        character.prepared_spells[spell_level].append(spell.name)
        return f"You prepare {spell.name} (level {spell_level}). Prepared: {current_prepared + 1}/{max_prepared}"

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
        bab = getattr(character, 'bab', (character.level * 3) // 4)
        grapple_mod = bab + (character.str_score - 10) // 2  # BAB + Str mod
        lines.append(pad_line(f" BAB: {bab:<2}  Grapple: {grapple_mod:<2}"))

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
        result = f"You pick up {item.name}."

        # Quest trigger for item collection
        if hasattr(character, 'quest_log'):
            item_type = getattr(item, 'item_type', item.name.lower())
            quest_updates = quests.on_item_collected(character, item_type)
            for update in quest_updates:
                result += f"\n[Quest] {update}"

        return result

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

    # =========================================================================
    # Chat and Communication Commands
    # =========================================================================
    def cmd_say(self, character, args):
        """Say something to everyone in the room."""
        if not args:
            return "Say what?"
        from src.chat import format_say, broadcast_to_room
        message = format_say(character, args)
        # Broadcast to others in room
        broadcast_to_room(character.room, message, exclude=character)
        # Return message to speaker
        return f"You say, '{args}'"

    def cmd_tell(self, character, args):
        """Send a private message to another player.
        Usage: tell <player> <message>
        """
        if not args:
            return "Tell whom what? Usage: tell <player> <message>"
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Tell them what? Usage: tell <player> <message>"

        target_name, message = parts
        from src.chat import find_player_by_name, send_tell
        recipient = find_player_by_name(self.world, target_name)

        if not recipient:
            # Try prefix match
            from src.chat import find_player_by_name_prefix
            recipient = find_player_by_name_prefix(self.world, target_name)

        if not recipient:
            return f"Player '{target_name}' not found."

        success, response = send_tell(character, recipient, message)
        return response

    def cmd_whisper(self, character, args):
        """Whisper to another player (alias for tell)."""
        return self.cmd_tell(character, args)

    def cmd_reply(self, character, args):
        """Reply to the last person who sent you a tell.
        Usage: reply <message>
        """
        if not args:
            return "Reply with what?"

        last_sender = getattr(character, 'last_tell_from', None)
        if not last_sender:
            return "No one has sent you a tell to reply to."

        from src.chat import find_player_by_name, send_tell
        recipient = find_player_by_name(self.world, last_sender)
        if not recipient:
            return f"{last_sender} is no longer online."

        success, response = send_tell(character, recipient, args)
        return response

    def cmd_emote(self, character, args):
        """Perform an emote/action visible to everyone in the room.
        Usage: emote <action>
        Example: emote waves hello
        Output: Playername waves hello
        """
        if not args:
            return "Emote what?"
        from src.chat import format_emote, broadcast_to_room
        message = format_emote(character, args)
        # Broadcast to others in room
        broadcast_to_room(character.room, message, exclude=character)
        # Return to actor
        return format_emote(character, args)

    def cmd_me(self, character, args):
        """Alias for emote."""
        return self.cmd_emote(character, args)

    def cmd_ooc(self, character, args):
        """Send an out-of-character message to everyone in the world.
        Usage: ooc <message>
        """
        if not args:
            return "OOC what?"
        from src.chat import format_ooc, broadcast_to_world
        message = format_ooc(character, args)
        # Broadcast to everyone except sender
        broadcast_to_world(self.world, message, exclude=character)
        # Return to sender
        return message

    def cmd_global(self, character, args):
        """Send a message to the global chat channel.
        Usage: global <message>
        """
        if not args:
            return "Say what globally?"
        from src.chat import format_global, broadcast_to_world
        message = format_global(character, args)
        # Broadcast to everyone except sender
        broadcast_to_world(self.world, message, exclude=character)
        # Return to sender
        return message

    def cmd_chat(self, character, args):
        """Alias for global chat."""
        return self.cmd_global(character, args)

    def cmd_shout(self, character, args):
        """Shout something that can be heard in nearby rooms.
        Usage: shout <message>
        """
        if not args:
            return "Shout what?"
        from src.chat import format_shout, broadcast_to_room
        message = format_shout(character, args)
        # Broadcast to current room (TODO: expand to nearby rooms)
        broadcast_to_room(character.room, message, exclude=character)
        # Return to shouter
        return f"You shout, '{args}'"

    def cmd_yell(self, character, args):
        """Alias for shout."""
        return self.cmd_shout(character, args)

    def cmd_who(self, character, args):
        """List all online players."""
        online = []
        for player in self.world.players:
            if getattr(player, 'is_ai', False):
                continue  # Skip AI players
            status = ""
            if getattr(player, 'is_immortal', False):
                status = " [IMM]"
            online.append(f"  {player.name} - {player.race} {player.char_class} Level {player.level}{status}")

        if not online:
            return "No players online."

        return f"Players Online ({len(online)}):\n" + "\n".join(online)

    def cmd_kill(self, character, args):
        # Check if character can act based on conditions
        if hasattr(character, 'can_act') and not character.can_act():
            return "You cannot act in your current condition!"

        # Check for cannot_attack effect (e.g., nauseated)
        if hasattr(character, 'has_condition_effect') and character.has_condition_effect('cannot_attack'):
            return "You cannot attack in your current condition!"

        target = next((m for m in character.room.mobs if m.name.lower() == args.lower() and m.alive), None)
        if target:
            # Initialize combat instance
            from src.combat import start_combat as init_combat
            combat = init_combat(character.room, character, target)

            character.state = State.COMBAT
            character.set_combat_target(target)  # Set auto-attack target

            # Build combat start message
            results = []
            results.append(combat.start_combat())
            results.append(attack(character, target))

            # Check if target died from first attack
            if target.hp <= 0:
                target.alive = False
                results.append(f"{target.name} has been slain!")
                # Quest trigger
                if hasattr(character, 'quest_log'):
                    mob_type = getattr(target, 'mob_type', target.name.lower())
                    quest_updates = quests.on_mob_killed(character, mob_type)
                    for update in quest_updates:
                        results.append(f"[Quest] {update}")
                # End combat if no enemies left
                should_end, end_msg = combat.check_combat_end()
                if should_end:
                    results.append(end_msg)
                    combat.end_combat()
                    character.clear_combat_target()
                    character.state = State.EXPLORING

            return "\n".join(results)
        return "No such target!"

    def cmd_flee(self, character, args):
        """Attempt to flee from combat."""
        import random
        from src.combat import get_combat, end_combat

        if character.state != State.COMBAT:
            return "You're not in combat!"

        # 50% base chance to flee, modified by Dex
        dex_mod = (getattr(character, 'dex_score', 10) - 10) // 2
        flee_chance = 50 + (dex_mod * 5)

        if random.randint(1, 100) <= flee_chance:
            # Success - pick a random exit and move
            if character.room.exits:
                direction = random.choice(list(character.room.exits.keys()))
                new_vnum = character.room.exits[direction]

                # Remove from combat
                combat = get_combat(character.room)
                if combat:
                    combat.remove_combatant(character)
                    # End combat if no players left
                    should_end, _ = combat.check_combat_end()
                    if should_end:
                        end_combat(character.room)

                character.state = State.EXPLORING
                character.clear_combat_target()
                character.clear_queue()

                # Move to new room
                if new_vnum in self.world.rooms:
                    character.room.players.remove(character)
                    character.room = self.world.rooms[new_vnum]
                    character.room.players.append(character)
                    return f"You flee {direction}!\nYou escape to {character.room.name}."

            return "You flee in panic but there's nowhere to go!"
        else:
            return "You try to flee but can't escape!"

    # =========================================================================
    # Auto-Attack and Action Queue Commands
    # =========================================================================
    def cmd_queue(self, character, args):
        """Queue an action to replace your next auto-attack.
        Usage: queue <spell|skill|feat|maneuver|item> <name> [target]
        Example: queue spell fireball
        Example: queue spell cure light wounds self
        Example: queue maneuver disarm goblin
        """
        if not args:
            return ("Usage: queue <type> <name> [target]\n"
                    "Types: spell, skill, feat, maneuver, item\n"
                    "Example: queue spell fireball\n"
                    "Example: queue maneuver trip goblin")

        parts = args.split(None, 2)  # Split into max 3 parts
        if len(parts) < 2:
            return "Usage: queue <type> <name> [target]"

        action_type = parts[0].lower()
        action_name = parts[1]
        action_args = parts[2] if len(parts) > 2 else ""

        valid_types = ['spell', 'skill', 'feat', 'maneuver', 'item']
        if action_type not in valid_types:
            return f"Invalid action type '{action_type}'. Valid types: {', '.join(valid_types)}"

        # Validate the action exists
        if action_type == 'spell':
            from src.spells import get_spell_by_name
            spell = get_spell_by_name(action_name)
            if not spell:
                return f"No such spell: {action_name}"
            # Check if known
            known = False
            for s in character.spells_known.values():
                if isinstance(s, dict) and s.get("name", "").lower() == action_name.lower():
                    known = True
                    break
                elif isinstance(s, str) and s.lower() == action_name.lower():
                    known = True
                    break
            if not known:
                return f"You don't know the spell: {action_name}"

        elif action_type == 'maneuver':
            from src import maneuvers
            valid_maneuvers = ['disarm', 'trip', 'bullrush', 'grapple', 'overrun', 'sunder', 'feint']
            if action_name.lower() not in valid_maneuvers:
                return f"Invalid maneuver '{action_name}'. Valid: {', '.join(valid_maneuvers)}"

        elif action_type == 'feat':
            # Check if character has the feat
            if action_name not in character.feats:
                return f"You don't have the feat: {action_name}"

        character.queue_action(action_type, action_name, action_args)
        return f"Queued {action_type}: {action_name}" + (f" (target: {action_args})" if action_args else "") + "\nThis will replace your next auto-attack."

    def cmd_q(self, character, args):
        """Shortcut for queue command."""
        return self.cmd_queue(character, args)

    def cmd_clearqueue(self, character, args):
        """Clear your queued action."""
        if character.has_queued_action():
            character.clear_queue()
            return "Queued action cleared."
        return "No action was queued."

    def cmd_cq(self, character, args):
        """Shortcut for clearqueue."""
        return self.cmd_clearqueue(character, args)

    def cmd_showqueue(self, character, args):
        """Show your currently queued action."""
        if character.has_queued_action():
            action_type, action_name, action_args = character.queued_action
            result = f"Queued: {action_type} - {action_name}"
            if action_args:
                result += f" (target: {action_args})"
            return result
        return "No action queued. You will auto-attack."

    def cmd_sq(self, character, args):
        """Shortcut for showqueue."""
        return self.cmd_showqueue(character, args)

    def cmd_autoattack(self, character, args):
        """Toggle auto-attack on or off."""
        enabled = character.toggle_auto_attack()
        if enabled:
            return "Auto-attack is now ON. You will automatically attack your target each round."
        else:
            return "Auto-attack is now OFF. You must manually attack each round."

    def cmd_aa(self, character, args):
        """Shortcut for autoattack toggle."""
        return self.cmd_autoattack(character, args)

    def cmd_target(self, character, args):
        """Set your auto-attack target without attacking.
        Usage: target <mob name>
        """
        if not args:
            if character.combat_target:
                target_name = getattr(character.combat_target, 'name', 'Unknown')
                return f"Current target: {target_name}"
            return "No target set. Usage: target <mob name>"

        target = next((m for m in character.room.mobs if m.name.lower() == args.lower() and m.alive), None)
        if target:
            character.set_combat_target(target)
            return f"Target set to: {target.name}"
        return "No such target!"

    def cmd_move(self, character, args):
        # Check if character can move based on conditions
        if hasattr(character, 'can_move') and not character.can_move():
            return "You cannot move in your current condition!"

        direction = args.lower()
        if direction in character.room.exits:
            new_vnum = character.room.exits[direction]
            if new_vnum in self.world.rooms:
                from src.chat import broadcast_to_room

                old_room = character.room
                new_room = self.world.rooms[new_vnum]

                # Announce departure to old room
                broadcast_to_room(old_room, f"{character.name} leaves {direction}.", exclude=character)

                # Move the character
                old_room.players.remove(character)
                character.room = new_room
                new_room.players.append(character)

                # Announce arrival to new room
                # Figure out opposite direction for "arrives from"
                opposites = {'north': 'south', 'south': 'north', 'east': 'west',
                            'west': 'east', 'up': 'below', 'down': 'above'}
                from_dir = opposites.get(direction, 'somewhere')
                broadcast_to_room(new_room, f"{character.name} arrives from the {from_dir}.", exclude=character)

                # Quest trigger for room entry
                result = f"You move {direction} to {character.room.name}."
                if hasattr(character, 'quest_log'):
                    room_vnum = str(new_vnum)
                    quest_updates = quests.on_room_entered(character, room_vnum)
                    for update in quest_updates:
                        result += f"\n[Quest] {update}"

                # Show room description and mobs after moving
                look_output = self.cmd_look(character, "")
                return f"{result}\n{look_output}"
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
        """Admin broadcast to all players."""
        if not character.is_immortal:
            return "Command restricted to immortals!"
        if not args:
            return "Broadcast what?"
        from src.chat import format_admin, broadcast_to_world
        message = format_admin(character, args)
        # Broadcast to everyone including sender
        broadcast_to_world(self.world, message, exclude=None)
        return "Broadcast sent."

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
        result = character.skill_check("Ride")
        return f"You attempt to ride. Skill check result: {result}"

    def cmd_search(self, character, args):
        result = character.skill_check("Search")
        return f"You search the area. Skill check result: {result}"

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
        from src.feats import FEATS
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

    def cmd_levelup(self, character, args):
        """
        Level up the character by 1 and trigger Bonus Feat selection if eligible.
        """
        import asyncio
        old_level = getattr(character, 'class_level', 1)
        new_level = old_level + 1
        character.set_level(new_level)
        # If running in async context, schedule bonus feat prompt
        try:
            loop = asyncio.get_event_loop()
            coro = character.check_levelup_bonus_feat(character.writer, character.reader)
            if loop.is_running():
                asyncio.ensure_future(coro)
            else:
                loop.run_until_complete(coro)
        except Exception:
            pass
        return f"You have reached level {new_level}!"

    # =========================================================================
    # Equipment Commands
    # =========================================================================

    def cmd_wear(self, character, args):
        """
        Equip an item from your inventory.
        Usage: wear <item name> [slot]
        """
        if not args:
            return "Wear what? Usage: wear <item name>"

        parts = args.split()
        item_name = parts[0].lower()
        slot = parts[1].lower() if len(parts) > 1 else None

        # Find item in inventory
        item = None
        for inv_item in character.inventory:
            if inv_item.name.lower().startswith(item_name) or item_name in inv_item.name.lower():
                item = inv_item
                break

        if not item:
            return f"You don't have '{args}' in your inventory."

        success, msg, unequipped = character.equip_item(item, slot)
        return msg

    def cmd_remove(self, character, args):
        """
        Remove an equipped item.
        Usage: remove <slot or item name>
        """
        if not args:
            return "Remove what? Usage: remove <slot or item name>"

        from src.character import EQUIPMENT_SLOTS
        arg = args.lower().strip()

        # Check if it's a slot name
        if arg in EQUIPMENT_SLOTS:
            success, msg, item = character.unequip_item(arg)
            return msg

        # Try to find by item name
        for slot, item in character.equipment.items():
            if item and (arg in item.name.lower() or item.name.lower().startswith(arg)):
                success, msg, removed = character.unequip_item(slot)
                return msg

        return f"You don't have '{args}' equipped."

    def cmd_equipment(self, character, args):
        """
        Display currently equipped items.
        Usage: equipment
        """
        from src.character import EQUIPMENT_SLOTS

        lines = ["=== Equipment ==="]

        slot_names = {
            "head": "Head",
            "face": "Face",
            "neck": "Neck",
            "shoulders": "Shoulders",
            "body": "Body/Armor",
            "torso": "Torso",
            "arms": "Arms",
            "hands": "Hands",
            "ring_left": "Ring (L)",
            "ring_right": "Ring (R)",
            "waist": "Waist",
            "feet": "Feet",
            "main_hand": "Main Hand",
            "off_hand": "Off Hand",
        }

        for slot in EQUIPMENT_SLOTS:
            item = character.equipment.get(slot)
            slot_display = slot_names.get(slot, slot.title())
            if item:
                ac_info = f" (AC +{item.ac_bonus})" if getattr(item, 'ac_bonus', 0) else ""
                dmg_info = ""
                if getattr(item, 'damage', None):
                    d = item.damage
                    dmg_info = f" ({d[0]}d{d[1]}+{d[2]})" if len(d) > 2 else f" ({d[0]}d{d[1]})"
                lines.append(f"  {slot_display:12}: {item.name}{ac_info}{dmg_info}")
            else:
                lines.append(f"  {slot_display:12}: -empty-")

        lines.append(f"\nAC: {character.ac}")
        lines.append(f"Gold: {getattr(character, 'gold', 0)} gp")

        return "\n".join(lines)

    # =========================================================================
    # Rest and Recovery Commands
    # =========================================================================

    def cmd_rest(self, character, args):
        """
        Rest to recover HP and spell slots.
        Usage: rest [short|long]
        - short: 1 hour rest, recover some HP
        - long: 8 hour rest, full recovery (default)

        You must be in a safe room to rest.
        """
        # Check for safe room
        room_flags = getattr(character.room, 'flags', [])
        if 'safe' not in room_flags and 'inn' not in room_flags and 'temple' not in room_flags:
            return "You cannot rest here. Find an inn or safe area."

        # Check for combat
        from src.combat import get_combat
        combat = get_combat(character.room)
        if combat and combat.is_active:
            return "You cannot rest while in combat!"

        # Determine rest type
        rest_type = args.lower().strip() if args else "long"

        if rest_type in ("short", "s", "1"):
            hours = 1
        else:  # Default to long rest
            hours = 8

        return character.rest(hours)

    # =========================================================================
    # Status and Condition Commands
    # =========================================================================

    def cmd_conditions(self, character, args):
        """
        Display current conditions affecting you.
        Usage: conditions
        """
        from src.conditions import describe_condition

        lines = ["=== Active Conditions ==="]

        if not character.conditions and not character.active_conditions:
            lines.append("  None")
            return "\n".join(lines)

        # Permanent conditions
        for cond in character.conditions:
            if cond not in character.active_conditions:
                desc = describe_condition(cond)
                lines.append(f"  {desc}")

        # Timed conditions
        for cond, duration in character.active_conditions.items():
            desc = describe_condition(cond)
            lines.append(f"  {desc} ({duration} rounds remaining)")

        return "\n".join(lines)

    def cmd_status(self, character, args):
        """
        Display detailed character status including health state.
        Usage: status
        """
        from src.character import HealthStatus

        lines = ["=== Character Status ==="]
        lines.append(f"Name: {character.name}")
        lines.append(f"Race: {character.race}")
        lines.append(f"Class: {character.char_class} Level {character.class_level}")
        lines.append("")

        # Health status
        status = character.health_status
        status_colors = {
            HealthStatus.HEALTHY: "Healthy",
            HealthStatus.DISABLED: "DISABLED (0 HP)",
            HealthStatus.DYING: "DYING!",
            HealthStatus.STABLE: "Stable (unconscious)",
            HealthStatus.DEAD: "DEAD",
        }
        lines.append(f"HP: {character.hp}/{character.max_hp}")
        lines.append(f"Status: {status_colors.get(status, 'Unknown')}")
        lines.append(f"AC: {character.ac}")
        lines.append("")

        # Ability scores
        lines.append("Abilities:")
        for stat in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
            score = getattr(character, f'{stat}_score', 10)
            mod = (score - 10) // 2
            lines.append(f"  {stat.upper()}: {score} ({mod:+d})")

        # Active conditions summary
        if character.conditions or character.active_conditions:
            lines.append("")
            lines.append("Conditions: " + ", ".join(character.conditions | set(character.active_conditions.keys())))

        return "\n".join(lines)

    # =========================================================================
    # Combat Commands
    # =========================================================================

    def cmd_fullattack(self, character, args):
        """
        Make a full attack (all iterative attacks based on BAB).
        Usage: fullattack <target>
        """
        from src.combat import attack as combat_attack

        if not args:
            return "Attack who? Usage: fullattack <target>"

        # Find target mob
        target = None
        target_name = args.lower()
        for mob in character.room.mobs:
            if mob.alive and target_name in mob.name.lower():
                target = mob
                break

        if not target:
            return f"You don't see '{args}' here."

        # Execute full attack
        return combat_attack(character, target, is_full_attack=True)

    # =========================================================================
    # Admin Condition Commands
    # =========================================================================

    def cmd_addcondition(self, character, args):
        """
        Add a condition to a target (admin command).
        Usage: @addcondition <target> <condition> [duration]
        Example: @addcondition goblin stunned 3
        """
        if not character.is_immortal:
            return "Command restricted to immortals!"

        from src import conditions as cond

        parts = args.split()
        if len(parts) < 2:
            return "Usage: @addcondition <target> <condition> [duration]"

        target_name = parts[0].lower()
        condition_name = parts[1].lower()
        duration = int(parts[2]) if len(parts) > 2 else None

        # Validate condition exists
        condition = cond.get_condition(condition_name)
        if not condition:
            valid_conditions = ", ".join(sorted(cond.get_condition_list()))
            return f"Unknown condition: {condition_name}\nValid conditions: {valid_conditions}"

        # Find target (player or mob)
        target = None
        for p in character.room.players:
            if p.name.lower() == target_name:
                target = p
                break
        if not target:
            for m in character.room.mobs:
                if m.name.lower() == target_name and m.alive:
                    target = m
                    break

        if not target:
            return f"No target named '{parts[0]}' found in this room."

        # Apply condition
        if hasattr(target, 'add_timed_condition'):
            target.add_timed_condition(condition_name, duration)
        else:
            target.conditions.add(condition_name)
            if duration:
                target.active_conditions[condition_name] = duration

        duration_msg = f" for {duration} rounds" if duration else " (permanent)"
        return f"Applied {condition.name} to {target.name}{duration_msg}."

    def cmd_removecondition(self, character, args):
        """
        Remove a condition from a target (admin command).
        Usage: @removecondition <target> <condition>
        Example: @removecondition goblin stunned
        """
        if not character.is_immortal:
            return "Command restricted to immortals!"

        parts = args.split()
        if len(parts) < 2:
            return "Usage: @removecondition <target> <condition>"

        target_name = parts[0].lower()
        condition_name = parts[1].lower()

        # Find target (player or mob)
        target = None
        for p in character.room.players:
            if p.name.lower() == target_name:
                target = p
                break
        if not target:
            for m in character.room.mobs:
                if m.name.lower() == target_name and m.alive:
                    target = m
                    break

        if not target:
            return f"No target named '{parts[0]}' found in this room."

        # Check if target has condition
        if not (condition_name in getattr(target, 'conditions', set()) or
                condition_name in getattr(target, 'active_conditions', {})):
            return f"{target.name} does not have the {condition_name} condition."

        # Remove condition
        if hasattr(target, 'remove_condition'):
            target.remove_condition(condition_name)
        else:
            target.conditions.discard(condition_name)

        if condition_name in getattr(target, 'active_conditions', {}):
            del target.active_conditions[condition_name]

        return f"Removed {condition_name} from {target.name}."

    def cmd_listconditions(self, character, args):
        """
        List all available conditions.
        Usage: @listconditions [category]
        Categories: physical, mental, other, combat, all
        """
        from src import conditions as cond

        category = args.lower() if args else "all"

        # Define categories
        physical = ['blinded', 'dazzled', 'deafened', 'entangled', 'exhausted', 'fatigued',
                   'grappled', 'helpless', 'paralyzed', 'petrified', 'pinned', 'prone', 'stunned']
        mental = ['confused', 'cowering', 'dazed', 'fascinated', 'frightened', 'nauseated',
                 'panicked', 'shaken']
        other = ['incorporeal', 'invisible', 'sickened', 'staggered', 'stable', 'unconscious']
        combat = ['flanked', 'flat_footed', 'silenced', 'bound', 'gagged']

        if category == "physical":
            conditions_to_show = physical
        elif category == "mental":
            conditions_to_show = mental
        elif category == "other":
            conditions_to_show = other
        elif category == "combat":
            conditions_to_show = combat
        else:
            conditions_to_show = cond.get_condition_list()

        lines = [f"=== Conditions ({category.title()}) ==="]
        for cond_name in sorted(conditions_to_show):
            condition = cond.get_condition(cond_name)
            if condition:
                lines.append(f"  {condition.name}: {condition.description[:60]}...")

        return "\n".join(lines)

    # =========================================================================
    # Combat Maneuver Commands
    # =========================================================================

    def _find_target(self, character, target_name):
        """Find a target mob in the room by name."""
        target_name = target_name.lower()
        for mob in character.room.mobs:
            if mob.alive and target_name in mob.name.lower():
                return mob
        return None

    def _check_can_act(self, character):
        """Check if character can take actions."""
        if hasattr(character, 'can_act') and not character.can_act():
            return "You cannot act in your current condition!"
        return None

    def cmd_disarm(self, character, args):
        """
        Attempt to disarm an opponent.
        Usage: disarm <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Disarm who? Usage: disarm <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.disarm(target)

    def cmd_trip(self, character, args):
        """
        Attempt to trip an opponent.
        Usage: trip <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Trip who? Usage: trip <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.trip(target)

    def cmd_bullrush(self, character, args):
        """
        Attempt to bull rush an opponent, pushing them back.
        Usage: bullrush <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Bull rush who? Usage: bullrush <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.bull_rush(target)

    def cmd_grapple(self, character, args):
        """
        Attempt to grapple an opponent.
        Usage: grapple <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Grapple who? Usage: grapple <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.grapple(target)

    def cmd_overrun(self, character, args):
        """
        Attempt to overrun an opponent, moving through their space.
        Usage: overrun <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Overrun who? Usage: overrun <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.overrun(target)

    def cmd_sunder(self, character, args):
        """
        Attempt to destroy an opponent's weapon.
        Usage: sunder <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Sunder whose weapon? Usage: sunder <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.sunder(target)

    def cmd_feint(self, character, args):
        """
        Feint in combat to deny opponent their Dex bonus to AC.
        Usage: feint <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Feint who? Usage: feint <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.feint(target)

    def cmd_whirlwind(self, character, args):
        """
        Attack all adjacent enemies at once. Requires Whirlwind Attack feat.
        Usage: whirlwind
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not character.has_feat("Whirlwind Attack"):
            return "You don't have the Whirlwind Attack feat!"

        # Get all alive mobs in room
        targets = [m for m in character.room.mobs if m.alive and m.hp > 0]
        if not targets:
            return "There are no enemies to attack!"

        return character.whirlwind_attack(targets)

    def cmd_springattack(self, character, args):
        """
        Move, attack, and continue moving. Requires Spring Attack feat.
        Usage: springattack <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not character.has_feat("Spring Attack"):
            return "You don't have the Spring Attack feat!"

        if not args:
            return "Spring attack who? Usage: springattack <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.spring_attack(target)

    def cmd_stunningfist(self, character, args):
        """
        Attempt to stun an opponent with an unarmed strike. Requires Stunning Fist feat.
        Usage: stunningfist <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not character.has_feat("Stunning Fist"):
            return "You don't have the Stunning Fist feat!"

        if not args:
            return "Stunning fist who? Usage: stunningfist <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        return character.stunning_fist(target)

    def cmd_grapple_damage(self, character, args):
        """
        Deal damage to a grappled opponent.
        Usage: gdamage <target>
        """
        if not character.has_condition('grappled'):
            return "You are not grappling anyone!"

        if not args:
            return "Damage who? Usage: gdamage <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        if not target.has_condition('grappled'):
            return f"{target.name} is not grappled!"

        return character.grapple_damage(target)

    def cmd_grapple_pin(self, character, args):
        """
        Attempt to pin a grappled opponent.
        Usage: gpin <target>
        """
        if not character.has_condition('grappled'):
            return "You are not grappling anyone!"

        if not args:
            return "Pin who? Usage: gpin <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        if not target.has_condition('grappled'):
            return f"{target.name} is not grappled!"

        return character.grapple_pin(target)

    def cmd_grapple_escape(self, character, args):
        """
        Attempt to escape from a grapple.
        Usage: gescape
        """
        if not character.has_condition('grappled'):
            return "You are not grappled!"

        # Find who is grappling us (any grappled mob in room)
        grappler = None
        for mob in character.room.mobs:
            if mob.alive and mob.has_condition('grappled'):
                grappler = mob
                break

        if not grappler:
            # Remove condition if no grappler found
            character.remove_condition('grappled')
            return "You are no longer grappled."

        return character.grapple_escape(grappler)

    # =========================================================================
    # Skill Check Commands
    # =========================================================================

    def cmd_check(self, character, args):
        """
        Perform a skill check.
        Usage: check <skill> [dc]
        Examples:
          check climb
          check climb 15
          check "knowledge arcana"
          check hide
        """
        from src import skills

        if not args:
            return "Check what? Usage: check <skill> [dc]\nType 'skills' to see available skills."

        parts = args.split()

        # Handle quoted skill names like "knowledge arcana"
        if args.startswith('"') or args.startswith("'"):
            # Find quoted skill name
            quote_char = args[0]
            end_quote = args.find(quote_char, 1)
            if end_quote > 0:
                skill_name = args[1:end_quote]
                rest = args[end_quote + 1:].strip().split()
            else:
                skill_name = args[1:]
                rest = []
        else:
            # Try to match a skill name (some have multiple words)
            skill_name = None
            for sname in skills.SKILLS.keys():
                if args.lower().startswith(sname.lower()):
                    skill_name = sname
                    rest = args[len(sname):].strip().split()
                    break

            if not skill_name:
                # Take first word as skill name
                skill_name = parts[0]
                rest = parts[1:]

        # Try to find skill
        skill = skills.SKILLS.get(skill_name)
        if not skill:
            # Try case-insensitive partial match
            for sname, s in skills.SKILLS.items():
                if skill_name.lower() in sname.lower():
                    skill_name = sname
                    skill = s
                    break

        if not skill:
            return f"Unknown skill: {skill_name}\nType 'skills' to see available skills."

        # Parse DC if provided
        dc = None
        if rest:
            try:
                dc = int(rest[0])
            except ValueError:
                pass

        # Perform the check
        success, total, desc = skills.skill_check(character, skill_name, dc=dc)

        return desc

    def cmd_take10(self, character, args):
        """
        Perform a skill check using Take 10 (no rolling).
        Usage: take10 <skill>
        Requires: No stress or distractions (not in combat)
        """
        from src import skills
        from src.combat import get_combat

        # Check for combat
        combat = get_combat(character.room)
        if combat and combat.is_active:
            return "You cannot take 10 while in combat!"

        if not args:
            return "Take 10 on what skill? Usage: take10 <skill>"

        skill_name = args.strip()

        # Try to find skill
        skill = skills.SKILLS.get(skill_name)
        if not skill:
            for sname in skills.SKILLS.keys():
                if skill_name.lower() in sname.lower():
                    skill_name = sname
                    skill = skills.SKILLS.get(sname)
                    break

        if not skill:
            return f"Unknown skill: {skill_name}"

        success, total, desc = skills.skill_check(character, skill_name, take_10=True)
        return desc

    def cmd_take20(self, character, args):
        """
        Perform a skill check using Take 20 (maximum effort, requires time).
        Usage: take20 <skill>
        Requires: No danger from failure, 20x normal time
        """
        from src import skills
        from src.combat import get_combat

        # Check for combat
        combat = get_combat(character.room)
        if combat and combat.is_active:
            return "You cannot take 20 while in combat!"

        if not args:
            return "Take 20 on what skill? Usage: take20 <skill>"

        skill_name = args.strip()

        # Try to find skill
        skill = skills.SKILLS.get(skill_name)
        if not skill:
            for sname in skills.SKILLS.keys():
                if skill_name.lower() in sname.lower():
                    skill_name = sname
                    skill = skills.SKILLS.get(sname)
                    break

        if not skill:
            return f"Unknown skill: {skill_name}"

        # Can't take 20 on skills with consequences for failure
        no_take_20 = ["Disable Device", "Open Lock", "Use Magic Device", "Tumble"]
        if skill_name in no_take_20:
            return f"You cannot take 20 on {skill_name} (failure has consequences)."

        success, total, desc = skills.skill_check(character, skill_name, take_20=True)
        return f"After careful effort (20x normal time):\n{desc}"

    def cmd_skilllist(self, character, args):
        """
        List all available skills.
        Usage: skills [ability]
        Examples:
          skills        - List all skills
          skills str    - List Strength-based skills
          skills trained - List trained-only skills
        """
        from src import skills

        ability_filter = args.lower() if args else None

        lines = ["=== Skills ==="]

        # Group by ability
        by_ability = {}
        for skill_name, skill in sorted(skills.SKILLS.items()):
            ability = skill.key_ability
            if ability not in by_ability:
                by_ability[ability] = []
            by_ability[ability].append(skill)

        ability_order = ["Str", "Dex", "Con", "Int", "Wis", "Cha"]

        for ability in ability_order:
            if ability_filter and ability_filter not in ability.lower() and ability_filter != "trained":
                continue

            skill_list = by_ability.get(ability, [])
            if not skill_list:
                continue

            lines.append(f"\n{ability}-based:")
            for skill in sorted(skill_list, key=lambda s: s.name):
                if ability_filter == "trained" and not skill.trained_only:
                    continue

                # Get character's ranks
                ranks = skills.get_skill_ranks(character, skill.name)
                total_mod, _ = skills.calculate_skill_modifier(character, skill.name)

                # Build skill info
                markers = []
                if skill.trained_only:
                    markers.append("T")
                if skill.armor_check_penalty:
                    markers.append("*")
                marker_str = f" [{','.join(markers)}]" if markers else ""

                # Class skill indicator
                is_class = skills.is_class_skill(character, skill.name)
                class_marker = "C" if is_class else "X"

                lines.append(f"  {skill.name:35} {class_marker} Ranks: {ranks:2} Mod: {total_mod:+3}{marker_str}")

        lines.append("\nLegend: T=Trained Only, *=Armor Check Penalty, C=Class Skill, X=Cross-Class")
        lines.append("Usage: check <skill> [dc] | take10 <skill> | take20 <skill>")

        return "\n".join(lines)

    def cmd_hide(self, character, args):
        """
        Attempt to hide from enemies.
        Usage: hide
        Opposed by: Spot checks from observers
        """
        from src import skills
        from src.combat import get_combat

        # Check if in combat
        combat = get_combat(character.room)
        if combat and combat.is_active:
            return "You cannot hide while in active combat!"

        # Check for cover/concealment (simplified)
        room = character.room
        has_cover = 'shadows' in getattr(room, 'flags', []) or \
                   'dark' in getattr(room, 'flags', []) or \
                   'forest' in getattr(room, 'flags', [])

        if not has_cover:
            return "You have nowhere to hide here. Find cover or concealment first."

        # Get observers (mobs in room)
        observers = [m for m in room.mobs if m.alive and m.hp > 0]

        if not observers:
            success, total, desc = skills.skill_check(character, "Hide")
            return f"{desc}\nYou successfully hide (no observers)."

        # Check against each observer
        results = [f"{character.name} attempts to hide..."]
        hidden_from_all = True

        for observer in observers:
            actor_wins, hider_total, spotter_total, desc = skills.opposed_skill_check(
                character, "Hide",
                observer, "Spot"
            )
            if actor_wins:
                results.append(f"  vs {observer.name}: HIDDEN (Hide {hider_total} vs Spot {spotter_total})")
            else:
                hidden_from_all = False
                results.append(f"  vs {observer.name}: SPOTTED! (Hide {hider_total} vs Spot {spotter_total})")

        if hidden_from_all:
            character.add_condition('hidden')
            results.append("You successfully hide from all observers!")
        else:
            results.append("You fail to hide from some observers.")

        return "\n".join(results)

    def cmd_sneak(self, character, args):
        """
        Move silently through the area.
        Usage: sneak
        Opposed by: Listen checks from nearby creatures
        """
        from src import skills

        # Get listeners (mobs in room)
        listeners = [m for m in character.room.mobs if m.alive and m.hp > 0]

        if not listeners:
            success, total, desc = skills.skill_check(character, "Move Silently")
            return f"{desc}\nYou move silently (no listeners)."

        # Check against each listener
        results = [f"{character.name} attempts to move silently..."]
        silent_to_all = True

        for listener in listeners:
            actor_wins, mover_total, listener_total, desc = skills.opposed_skill_check(
                character, "Move Silently",
                listener, "Listen"
            )
            if actor_wins:
                results.append(f"  vs {listener.name}: SILENT (Sneak {mover_total} vs Listen {listener_total})")
            else:
                silent_to_all = False
                results.append(f"  vs {listener.name}: HEARD! (Sneak {mover_total} vs Listen {listener_total})")

        if silent_to_all:
            results.append("You move silently past all listeners!")
        else:
            results.append("Some creatures hear you moving.")

        return "\n".join(results)

    def cmd_search(self, character, args):
        """
        Search the area for hidden objects or doors.
        Usage: search [dc]
        """
        from src import skills

        # Default DC for hidden things
        dc = 20
        if args:
            try:
                dc = int(args)
            except ValueError:
                pass

        success, total, desc = skills.skill_check(character, "Search", dc=dc)

        if success:
            # Check for hidden things in the room
            room = character.room
            found_items = []

            # Check for hidden exits
            for direction, exit_data in getattr(room, 'exits', {}).items():
                if isinstance(exit_data, dict) and exit_data.get('hidden'):
                    found_items.append(f"a hidden exit to the {direction}")

            # Check for hidden items
            for item in getattr(room, 'items', []):
                if getattr(item, 'hidden', False):
                    found_items.append(f"a hidden {item.name}")
                    item.hidden = False  # Reveal it

            if found_items:
                desc += f"\nYou find: {', '.join(found_items)}!"
            else:
                desc += "\nYou find nothing hidden."

        return desc

    def cmd_listen(self, character, args):
        """
        Listen for sounds in the area.
        Usage: listen [dc]
        """
        from src import skills

        dc = 15  # Default
        if args:
            try:
                dc = int(args)
            except ValueError:
                pass

        success, total, desc = skills.skill_check(character, "Listen", dc=dc)

        if success:
            # Check for things to hear
            room = character.room
            sounds = []

            # Adjacent room occupants
            for direction, exit_data in getattr(room, 'exits', {}).items():
                adj_vnum = exit_data if isinstance(exit_data, int) else exit_data.get('room')
                if adj_vnum:
                    # Would need world reference to check adjacent room
                    pass

            # Mobs in current room (hidden ones)
            for mob in room.mobs:
                if mob.alive and mob.has_condition('hidden'):
                    sounds.append(f"something moving nearby")
                    break

            if sounds:
                desc += f"\nYou hear: {', '.join(sounds)}"
            else:
                desc += "\nYou hear nothing unusual."

        return desc

    def cmd_spot(self, character, args):
        """
        Spot hidden creatures or objects.
        Usage: spot
        """
        from src import skills

        results = [f"{character.name} looks around carefully..."]

        # Check for hidden mobs
        hidden_found = []
        for mob in character.room.mobs:
            if mob.alive and mob.has_condition('hidden'):
                # Opposed check
                actor_wins, spotter_total, hider_total, desc = skills.opposed_skill_check(
                    character, "Spot",
                    mob, "Hide"
                )
                if actor_wins:
                    mob.remove_condition('hidden')
                    hidden_found.append(mob.name)
                    results.append(f"  You spot {mob.name}! (Spot {spotter_total} vs Hide {hider_total})")
                else:
                    results.append(f"  You sense something but can't locate it...")

        if not character.room.mobs or not any(m.has_condition('hidden') for m in character.room.mobs):
            success, total, desc = skills.skill_check(character, "Spot")
            results.append(desc)
            if success:
                results.append("You see nothing out of the ordinary.")

        return "\n".join(results)

    def cmd_climb(self, character, args):
        """
        Attempt to climb a surface.
        Usage: climb [dc]
        Default DCs: rope=0, ladder=5, knotted rope=5, wall with ledges=10, rough=20, smooth=25
        """
        from src import skills

        dc = 15  # Default
        if args:
            try:
                dc = int(args)
            except ValueError:
                # Try to parse surface type
                surfaces = {
                    "rope": 0, "ladder": 5, "knotted": 5,
                    "ledges": 10, "rough": 20, "smooth": 25, "overhang": 25
                }
                for surface, sdc in surfaces.items():
                    if surface in args.lower():
                        dc = sdc
                        break

        success, total, desc = skills.skill_check(character, "Climb", dc=dc)

        if success:
            desc += "\nYou climb successfully!"
        else:
            desc += "\nYou fail to climb and make no progress."
            # Optional: Check for falling (fail by 5+)
            if total < dc - 5:
                desc += " You slip and fall!"

        return desc

    def cmd_jump(self, character, args):
        """
        Attempt to jump a distance.
        Usage: jump <distance in feet>
        Running: DC = distance in feet (horizontal) or 4x feet (vertical)
        Standing: DC is doubled
        """
        from src import skills

        if not args:
            return "Jump how far? Usage: jump <distance> (e.g., 'jump 10' for 10 feet)"

        try:
            distance = int(args)
        except ValueError:
            return "Please specify distance in feet (e.g., 'jump 10')"

        # Assume running jump; DC = distance for horizontal
        dc = distance

        # Check movement
        is_running = getattr(character, 'is_running', False)
        if not is_running:
            dc *= 2  # Standing jump

        # Get current speed (affects max distance)
        base_speed = getattr(character, 'max_move', 30)
        speed_mod = (base_speed - 30) // 10 * 4  # +4 per 10 ft above 30

        success, total, desc = skills.skill_check(character, "Jump", dc=dc, modifier=speed_mod)

        if success:
            desc += f"\nYou successfully jump {distance} feet!"
        else:
            # Calculate actual distance jumped
            actual = max(0, total // (2 if not is_running else 1))
            desc += f"\nYou only manage to jump {actual} feet."

        return desc

    def cmd_tumble(self, character, args):
        """
        Tumble through a threatened area or to reduce falling damage.
        Usage: tumble [target]
        DC 15: Move through threatened area without AoO
        DC 25: Tumble through enemy's space
        """
        from src import skills

        # Check for trained only
        ranks = skills.get_skill_ranks(character, "Tumble")
        if ranks == 0:
            return "You cannot tumble untrained."

        dc = 15  # Default: avoid AoO
        through_enemy = False

        if args:
            target = self._find_target(character, args)
            if target:
                dc = 25
                through_enemy = True

        success, total, desc = skills.skill_check(character, "Tumble", dc=dc)

        if success:
            if through_enemy:
                desc += f"\nYou tumble through your opponent's space!"
            else:
                desc += "\nYou tumble safely through the threatened area!"
        else:
            desc += "\nYou stumble and provoke attacks of opportunity!"

        return desc

    def cmd_intimidate(self, character, args):
        """
        Attempt to demoralize an opponent.
        Usage: intimidate <target>
        On success: Target is shaken for 1+ rounds.
        """
        from src import skills

        if not args:
            return "Intimidate who? Usage: intimidate <target>"

        target = self._find_target(character, args)
        if not target:
            # Try players
            for p in character.room.players:
                if p != character and args.lower() in p.name.lower():
                    target = p
                    break

        if not target:
            return f"You don't see '{args}' here."

        success, total, desc = skills.check_intimidate(character, target)

        if success:
            # Apply shaken condition
            rounds = 1 + max(0, (total - (10 + target.level + skills.get_ability_mod(target, "Wis"))) // 5)
            target.add_timed_condition('shaken', rounds)

        return desc

    def cmd_diplomacy(self, character, args):
        """
        Attempt to improve an NPC's attitude.
        Usage: diplomacy <target>
        """
        from src import skills

        if not args:
            return "Negotiate with who? Usage: diplomacy <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        # Get current attitude (default to indifferent)
        current_attitude = getattr(target, 'attitude', 'indifferent')

        new_attitude, total, desc = skills.check_diplomacy(character, target, current_attitude)

        # Update target's attitude
        if hasattr(target, 'attitude'):
            target.attitude = new_attitude

        return desc

    def cmd_bluff(self, character, args):
        """
        Attempt to deceive someone or feint in combat.
        Usage: bluff <target>
        In combat: Feint to deny Dex bonus to AC
        Out of combat: Opposed by Sense Motive
        """
        from src import skills
        from src.combat import get_combat

        if not args:
            return "Bluff who? Usage: bluff <target>"

        target = self._find_target(character, args)
        if not target:
            for p in character.room.players:
                if p != character and args.lower() in p.name.lower():
                    target = p
                    break

        if not target:
            return f"You don't see '{args}' here."

        # In combat = feint
        combat = get_combat(character.room)
        if combat and combat.is_active:
            success, bluff_total, sm_total, desc = skills.check_bluff_feint(character, target)
            if success:
                # Mark target as flat-footed for next attack
                target.add_timed_condition('flat_footed', 1)
            return desc
        else:
            # Out of combat - opposed Bluff vs Sense Motive
            actor_wins, actor_total, target_total, desc = skills.opposed_skill_check(
                character, "Bluff",
                target, "Sense Motive"
            )
            if actor_wins:
                return f"{desc}\n{target.name} believes your bluff!"
            else:
                return f"{desc}\n{target.name} sees through your deception!"

    def cmd_sensemotive(self, character, args):
        """
        Try to determine if someone is lying or get a hunch about them.
        Usage: sensemotive <target>
        """
        from src import skills

        if not args:
            return "Sense the motives of who? Usage: sensemotive <target>"

        target = self._find_target(character, args)
        if not target:
            for p in character.room.players:
                if p != character and args.lower() in p.name.lower():
                    target = p
                    break

        if not target:
            return f"You don't see '{args}' here."

        # Opposed check vs Bluff (or fixed DC for hunch)
        bluff_ranks = skills.get_skill_ranks(target, "Bluff")

        if bluff_ranks > 0:
            actor_wins, actor_total, target_total, desc = skills.opposed_skill_check(
                character, "Sense Motive",
                target, "Bluff"
            )
            if actor_wins:
                return f"{desc}\nYou sense that {target.name} may be hiding something."
            else:
                return f"{desc}\nYou cannot read {target.name}'s intentions."
        else:
            # Hunch check (DC 20)
            success, total, desc = skills.skill_check(character, "Sense Motive", dc=20)
            if success:
                return f"{desc}\nYou get a hunch about {target.name}'s general attitude."
            else:
                return f"{desc}\nYou cannot get a read on {target.name}."

    def cmd_heal_skill(self, character, args):
        """
        Use the Heal skill for first aid or treating wounds.
        Usage: healskill <target> [type]
        Types: first_aid, treat_wounds, treat_poison, treat_disease
        """
        from src import skills

        if not args:
            return "Heal who? Usage: healskill <target> [type]"

        parts = args.split()
        target_name = parts[0]
        heal_type = parts[1] if len(parts) > 1 else "first_aid"

        # Find target
        target = None
        if target_name.lower() == "self" or target_name.lower() == character.name.lower():
            target = character
        else:
            target = self._find_target(character, target_name)
            if not target:
                for p in character.room.players:
                    if target_name.lower() in p.name.lower():
                        target = p
                        break

        if not target:
            return f"You don't see '{target_name}' here."

        # Determine DC
        dcs = {
            "first_aid": 15,        # Stabilize dying
            "treat_wounds": 15,     # Restore 1 HP (long-term care)
            "treat_poison": 15,     # Help save vs secondary damage
            "treat_disease": 15,    # Help save vs disease
            "aid_another": 10,      # Give +2 to next Heal check
        }

        dc = dcs.get(heal_type, 15)
        success, total, desc = skills.skill_check(character, "Heal", dc=dc)

        if success:
            if heal_type == "first_aid":
                if hasattr(target, 'health_status'):
                    from src.character import HealthStatus
                    if target.health_status in (HealthStatus.DYING,):
                        target.is_stable = True
                        desc += f"\n{target.name} is stabilized!"
                    else:
                        desc += f"\n{target.name} doesn't need first aid."
                else:
                    desc += f"\nYou tend to {target.name}'s wounds."
            elif heal_type == "treat_wounds":
                old_hp = target.hp
                target.hp = min(target.hp + 1, target.max_hp)
                desc += f"\nWith long-term care, {target.name} recovers 1 HP. ({old_hp} -> {target.hp})"
            else:
                desc += f"\nYou provide medical attention to {target.name}."
        else:
            desc += f"\nYour attempt to help fails."

        return desc

    # =========================================================================
    # Quest Commands
    # =========================================================================

    def _get_quest_log(self, character):
        """Get or create a QuestLog for the character."""
        from src.quests import QuestLog
        if not hasattr(character, 'quest_log') or character.quest_log is None:
            character.quest_log = QuestLog()
        return character.quest_log

    def _get_quest_manager(self):
        """Get or create the world's QuestManager."""
        from src.quests import QuestManager
        if not hasattr(self.world, 'quest_manager') or self.world.quest_manager is None:
            self.world.quest_manager = QuestManager()
            self.world.quest_manager.load_quests()
        return self.world.quest_manager

    def cmd_questlog(self, character, args):
        """
        Display your quest log.
        Usage: questlog [active|complete|all]
        """
        from src.quests import QuestState

        quest_log = self._get_quest_log(character)
        quest_manager = self._get_quest_manager()

        filter_type = args.lower() if args else "active"

        lines = ["=== Quest Log ==="]

        # Active quests
        if filter_type in ("active", "all"):
            active = [q for q in quest_log.active_quests.values()
                     if q.state in (QuestState.ACTIVE, QuestState.COMPLETE)]

            if active:
                lines.append("\nActive Quests:")
                for aq in active:
                    quest = quest_manager.get_quest(aq.quest_id)
                    if quest:
                        status = "[READY TO TURN IN]" if aq.state == QuestState.COMPLETE else ""
                        lines.append(f"  [{quest.id}] {quest.name} (Lv.{quest.level}) {status}")

                        # Show objectives
                        for obj in aq.objectives:
                            if not obj.hidden:
                                check = "[X]" if obj.is_complete else "[ ]"
                                opt = "(Optional)" if obj.optional else ""
                                lines.append(f"      {check} {obj.description} {obj.progress_text} {opt}")
            else:
                lines.append("\nNo active quests.")

        # Completed quests
        if filter_type in ("complete", "all"):
            if quest_log.completed_quests:
                lines.append("\nCompleted Quests:")
                for qid in sorted(quest_log.completed_quests):
                    quest = quest_manager.get_quest(qid)
                    if quest:
                        lines.append(f"  [{qid}] {quest.name}")
            elif filter_type == "complete":
                lines.append("\nNo completed quests.")

        lines.append("\nCommands: questlog | quest accept <id> | quest abandon <id> | quest turnin <id>")
        return "\n".join(lines)

    def cmd_quest_action(self, character, args):
        """
        Quest management command.
        Usage:
          quest list          - Show available quests
          quest info <id>     - Show quest details
          quest accept <id>   - Accept a quest
          quest abandon <id>  - Abandon a quest
          quest turnin <id>   - Turn in a completed quest
        """
        from src.quests import QuestState, apply_quest_rewards

        if not args:
            return self.cmd_questlog(character, "")

        parts = args.split()
        action = parts[0].lower()
        quest_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

        quest_log = self._get_quest_log(character)
        quest_manager = self._get_quest_manager()

        if action == "list":
            # Show available quests in this room or from nearby NPCs
            room_vnum = character.room.vnum if character.room else 0
            available = quest_manager.get_available_quests(character, quest_log, room_vnum=room_vnum)

            if not available:
                # Show all available quests
                available = quest_manager.get_available_quests(character, quest_log)

            if available:
                lines = ["=== Available Quests ==="]
                for quest in available:
                    lines.append(f"  [{quest.id}] {quest.name} (Lv.{quest.level}) - {quest.giver_npc}")
                    lines.append(f"      {quest.description[:60]}...")
                lines.append("\nUse 'quest accept <id>' to accept a quest.")
                return "\n".join(lines)
            else:
                return "No quests available at your level."

        elif action == "info":
            if quest_id is None:
                return "Usage: quest info <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            lines = [f"=== {quest.name} ==="]
            lines.append(f"Level: {quest.level} | Category: {quest.category.title()}")
            lines.append(f"Quest Giver: {quest.giver_npc}")
            lines.append(f"\n{quest.description}")

            lines.append("\nObjectives:")
            for obj in quest.objectives:
                if not obj.hidden:
                    opt = "(Optional)" if obj.optional else ""
                    lines.append(f"  - {obj.description} {opt}")

            lines.append("\nRewards:")
            if quest.rewards.xp:
                lines.append(f"  XP: {quest.rewards.xp}")
            if quest.rewards.gold:
                lines.append(f"  Gold: {quest.rewards.gold}")
            for item in quest.rewards.items:
                lines.append(f"  Item: {item}")
            if quest.rewards.title:
                lines.append(f"  Title: {quest.rewards.title}")
            for faction, rep in quest.rewards.reputation.items():
                lines.append(f"  Reputation: +{rep} with {faction}")

            # Check status
            if quest_log.is_quest_active(quest_id):
                lines.append("\nStatus: ACTIVE")
            elif quest_log.is_quest_complete(quest_id):
                lines.append("\nStatus: COMPLETED")
            else:
                meets, reason = quest.prerequisites.check(character, quest_log)
                if meets:
                    lines.append("\nStatus: Available - use 'quest accept' to start")
                else:
                    lines.append(f"\nStatus: Locked - {reason}")

            return "\n".join(lines)

        elif action == "accept":
            if quest_id is None:
                return "Usage: quest accept <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            # Check prerequisites
            meets, reason = quest.prerequisites.check(character, quest_log)
            if not meets:
                return f"Cannot accept quest: {reason}"

            success, msg = quest_log.accept_quest(quest)
            if success and quest.accept_text:
                msg += f"\n\n{quest.giver_npc} says: \"{quest.accept_text}\""
            return msg

        elif action == "abandon":
            if quest_id is None:
                return "Usage: quest abandon <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            if not quest.abandonable:
                return f"Quest '{quest.name}' cannot be abandoned."

            success, msg = quest_log.abandon_quest(quest_id)
            return msg

        elif action == "turnin":
            if quest_id is None:
                return "Usage: quest turnin <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            active_quest = quest_log.get_active_quest(quest_id)
            if not active_quest:
                return "You don't have this quest active."

            if active_quest.state != QuestState.COMPLETE:
                return "Quest objectives not complete yet."

            # Turn in and apply rewards
            success, msg = quest_log.turn_in_quest(quest_id)
            if success:
                lines = [msg]
                if quest.complete_text:
                    lines.append(f"\n{quest.giver_npc or 'Quest Giver'} says: \"{quest.complete_text}\"")

                # Apply rewards
                reward_msgs = apply_quest_rewards(character, quest, quest_log)
                lines.extend(reward_msgs)

                # Check for chain quest
                if quest.chain_quest:
                    next_quest = quest_manager.get_quest(quest.chain_quest)
                    if next_quest:
                        lines.append(f"\nNew quest available: {next_quest.name}")

                return "\n".join(lines)
            return msg

        else:
            return "Unknown quest action. Use: list, info, accept, abandon, turnin"

    def cmd_talkto(self, character, args):
        """
        Talk to an NPC to get quests or turn in completed ones.
        Usage: talkto <npc name>
        """
        from src.quests import QuestState, on_npc_talked, apply_quest_rewards

        if not args:
            return "Talk to who? Usage: talkto <npc name>"

        npc_name = args.lower()
        quest_log = self._get_quest_log(character)
        quest_manager = self._get_quest_manager()

        # Find NPC in room
        npc = None
        for mob in character.room.mobs:
            if mob.alive and npc_name in mob.name.lower():
                npc = mob
                break

        if not npc:
            return f"You don't see '{args}' here."

        lines = [f"You approach {npc.name}."]

        # Update quest talk objectives
        talk_msgs = on_npc_talked(character, npc.name, quest_log, quest_manager)
        lines.extend(talk_msgs)

        # Check for quests to turn in
        turnin_quests = quest_manager.get_turnin_quests(quest_log, npc_name=npc.name)
        for quest, active_quest in turnin_quests:
            lines.append(f"\n{npc.name} says: \"Ah, you've completed {quest.name}!\"")
            if quest.complete_text:
                lines.append(f"\"{quest.complete_text}\"")

            # Auto turn in
            success, msg = quest_log.turn_in_quest(quest.id)
            if success:
                reward_msgs = apply_quest_rewards(character, quest, quest_log)
                lines.extend(reward_msgs)

        # Check for available quests
        available = quest_manager.get_available_quests(character, quest_log, npc_name=npc.name)
        if available:
            lines.append(f"\n{npc.name} has quests available:")
            for quest in available:
                lines.append(f"  [{quest.id}] {quest.name} (Lv.{quest.level})")
            lines.append("Use 'quest accept <id>' to accept a quest.")

        # Show NPC dialogue if they have one
        if hasattr(npc, 'dialogue') and npc.dialogue:
            lines.append(f"\n{npc.name} says: \"{npc.dialogue}\"")
        elif not available and not turnin_quests:
            lines.append(f"\n{npc.name} has nothing to say right now.")

        return "\n".join(lines)

    def cmd_reputation(self, character, args):
        """
        Display your reputation with various factions.
        Usage: reputation
        """
        reputation = getattr(character, 'reputation', {})
        titles = getattr(character, 'titles', [])

        lines = ["=== Reputation & Titles ==="]

        if titles:
            lines.append("\nTitles:")
            for title in titles:
                lines.append(f"  {title}")

        if reputation:
            lines.append("\nFaction Standing:")

            # Reputation thresholds
            def rep_rank(value):
                if value >= 100:
                    return "Exalted"
                elif value >= 75:
                    return "Revered"
                elif value >= 50:
                    return "Honored"
                elif value >= 25:
                    return "Friendly"
                elif value >= 0:
                    return "Neutral"
                elif value >= -25:
                    return "Unfriendly"
                elif value >= -50:
                    return "Hostile"
                else:
                    return "Hated"

            for faction, value in sorted(reputation.items()):
                rank = rep_rank(value)
                lines.append(f"  {faction}: {value} ({rank})")
        else:
            lines.append("\nNo faction reputation yet.")

        return "\n".join(lines)
