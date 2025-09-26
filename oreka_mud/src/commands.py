from src.combat import attack
from src.character import State

class CommandParser:
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
            # --- Build commands (restricted to immortals) ---
            "build": self.cmd_build,
            "dig": self.cmd_dig,
            "setdesc": self.cmd_setdesc,
            "setexit": self.cmd_setexit,
            "setmob": self.cmd_setmob,
            "setitem": self.cmd_setitem,
            "setflag": self.cmd_setflag,
            "setname": self.cmd_setname,
            "setvnum": self.cmd_setvnum,
            "setarea": self.cmd_setarea,
            "setroom": self.cmd_setroom,
            "setreset": self.cmd_setreset,
            "setdoor": self.cmd_setdoor,
            "setowner": self.cmd_setowner,
            "setzone": self.cmd_setzone,
            "setweather": self.cmd_setweather,
            "setlight": self.cmd_setlight,
            "setterrain": self.cmd_setterrain,
            "setnote": self.cmd_setnote,
            "sethelp": self.cmd_sethelp,
            "setcolor": self.cmd_setcolor,
            "setprompt": self.cmd_setprompt,
            "settitle": self.cmd_settitle,
            "setrace": self.cmd_setrace,
            "setclass": self.cmd_setclass,
            "setdeity": self.cmd_setdeity,
            "setalignment": self.cmd_setalignment,
            "setlevel": self.cmd_setlevel,
            "sethp": self.cmd_sethp,
            "setmana": self.cmd_setmana,
            "setmove": self.cmd_setmove,
            "setac": self.cmd_setac,
            "setstr": self.cmd_setstr,
            "setdex": self.cmd_setdex,
            "setcon": self.cmd_setcon,
            "setint": self.cmd_setint,
            "setwis": self.cmd_setwis,
            "setcha": self.cmd_setcha,
            "setxp": self.cmd_setxp,
            "setgold": self.cmd_setgold,
            "setfeats": self.cmd_setfeats,
            "setskills": self.cmd_setskills,
            "setspells": self.cmd_setspells,
            "setinventory": self.cmd_setinventory,
            "setequipment": self.cmd_setequipment,
            "setresist": self.cmd_setresist,
            "setimmune": self.cmd_setimmune,
            "setaffinity": self.cmd_setaffinity,
            "setai": self.cmd_setai,
            "setimmortal": self.cmd_setimmortal,
            "setpassword": self.cmd_setpassword,
            "setemail": self.cmd_setemail
        }

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
        # Section 1: Identity
        lines = [
            "+" + "-"*40 + "+",
            f"| Name: {character.name:<15} Level: {character.level:<3}  |",
            f"| Title: {character.title or '':<32} |",
            f"| Race: {character.race:<15} Class: {getattr(character, 'char_class', 'Adventurer'):<12} |",
        ]
        # Class details
        if hasattr(character, 'get_class_data'):
            class_data = character.get_class_data()
            lines.append(f"| Class Alignment: {class_data.get('alignment', '-'):<27} |")
            lines.append(f"| Hit Die: d{class_data.get('hit_die', '-')}  Skill/Level: {class_data.get('skill_points', '-')}  |")
            lines.append(f"| BAB: {class_data.get('bab_progression', '-'):>6}  Saves: {class_data.get('save_progression', '-')} |")
        lines.append("+" + "-"*40 + "+")

        # Section 2: Roleplay/Meta
        lines.append(f"| Alignment: {getattr(character, 'alignment', 'Unaligned'):<15} Deity: {getattr(character, 'deity', 'None'):<18}|")
        lines.append(f"| Size: {getattr(character, 'size', 'Medium'):<8} Speed: {getattr(character, 'speed', character.move):<4} ft.   Immortal: {'Yes' if character.is_immortal else 'No':<3} |")
        lines.append(f"| Elemental Affinity: {character.elemental_affinity or 'None':<22}|")
        lines.append("+" + "-"*40 + "+")

        # Section 3: Combat
        lines.append(f"| HP: {character.hp:>3}/{character.max_hp:<3}  Mana: {character.mana:>3}/{character.max_mana:<3}  AC: {character.ac:<2}  |")
        lines.append(f"| Touch AC: {getattr(character, 'touch_ac', character.ac):<2}  Flat-Footed AC: {getattr(character, 'flat_ac', character.ac):<2}  |")
        lines.append(f"| BAB: {getattr(character, 'bab', (character.level * 3) // 4):<2}  Grapple: {getattr(character, 'grapple', (character.level * 3) // 4 + (character.str_score - 10) // 2):<2} |")

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
        lines.append(f"| Fort: {fort:<2}  Ref: {ref:<2}  Will: {will:<2} |")
        lines.append("+" + "-"*40 + "+")

        # Section 4: Stats
        lines.append(f"| STR: {character.str_score:<2}  DEX: {character.dex_score:<2}  CON: {character.con_score:<2}  INT: {character.int_score:<2}  WIS: {character.wis_score:<2}  CHA: {character.cha_score:<2} |")
        lines.append("+" + "-"*40 + "+")

        # Section 5: XP, Resistances, Immunities
        lines.append(f"| XP: {character.xp:<8} |")
        lines.append(f"| Resistances: {', '.join(getattr(character, 'resistances', [])) or 'None':<28}|")
        lines.append(f"| Immunities: {', '.join(getattr(character, 'immunities', [])) or 'None':<29}|")
        lines.append("+" + "-"*40 + "+")

        # Section 6: Active Effects
        effects = getattr(character, 'active_effects', [])
        if effects:
            lines.append("| Active Conditions/Status Effects:         |")
            for effect in effects:
                lines.append(f"| - {effect:<36}|")
            lines.append("+" + "-"*40 + "+")

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
                "  %m = Mana, %M = Max Mana, %v = Move, %V = Max Move,\n"
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
        return character.room.description

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
                character.room.players.remove(character)
                character.room = self.world.rooms[new_vnum]
                character.room.players.append(character)
                return f"You move {direction} to {character.room.name}."
        return "No exit that way!"

    def cmd_exits(self, character, args):
        return ", ".join(character.room.exits.keys())

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
    def cmd_appraise(self, character, args):
        result = character.skill_check("Appraise")
        return f"You appraise the item. Skill check result: {result}"

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
