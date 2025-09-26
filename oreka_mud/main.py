import asyncio
import logging
from src.world import OrekaWorld
from src.commands import CommandParser
from src.character import Character
import hashlib
import json
import getpass
from src.classes import CLASSES
from src.feats import FEATS
from src.spells import SPELLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrekaMUD")


# Structured deity data for Elemental Lords and Ascended Gods
DEITIES = [
    {
        "name": "Dagdan, The United Sun",
        "type": "Ascended God",
        "alignment": "Lawful Good",
        "domains": ["Good", "Strength", "Magic"],
        "lore": "The immortal champion who united the tribes and brought the light of knowledge and strength to all peoples."
    },
    # Elemental Lords (examples, you can expand)
    {
        "name": "Aureon",
        "title": "The Sunlord",
        "type": "Elemental Lord",
        "alignment": "Lawful Good",
        "domains": ["Sun", "Law", "Knowledge"],
        "lore": "Original Lord of the Sun, order, and wisdom."
    },
    {
        "name": "Nerath",
        "title": "The Deep Current",
        "type": "Elemental Lord",
        "alignment": "Neutral",
        "domains": ["Sea", "Change", "Luck"],
        "lore": "Primal god of the sea, tides, and fate."
    },
    {
        "name": "Vulkar",
        "title": "The Forgefire",
        "type": "Elemental Lord",
        "alignment": "Neutral Good",
        "domains": ["Forge", "Fire", "Earth"],
        "lore": "Smith of the world, master of fire and stone."
    },
    {
        "name": "Lirael",
        "title": "The Moonweaver",
        "type": "Elemental Lord",
        "alignment": "Chaotic Good",
        "domains": ["Moon", "Magic", "Fate"],
        "lore": "Mistress of the moon, magic, and destiny."
    },
    # Ascended Gods
    {
        "name": "Cinvarin, the Five Witnesses (The Fivefold Flame)",
        "type": "Ascended God",
        "alignment": "Neutral Good",
        "domains": ["Community", "Fire", "Earth", "Air", "Water"],
        "lore": "Five druids merged at the Lament to end the Deceivers and rose as one god of unity and the four elements."
    },
    {
        "name": "Hareem, The Golden Rose",
        "type": "Ascended God",
        "alignment": "Chaotic Good",
        "domains": ["Good", "Charm", "Community", "Retribution"],
        "lore": "Bard-saint who sacrificed herself to slay the Twelve Kings that abandoned the dwarves, enshrining mercy for Kin and justice for traitors."
    },
    {
        "name": "Tarvek Wen, Doombringer",
        "type": "Ascended God",
        "alignment": "Lawful Good",
        "domains": ["Law", "Good", "Protection", "Justice"],
        "lore": "Shield and sword of the helpless; patron of oaths kept under fire and liberation from tyrants."
    },
    {
        "name": "Ludus Galerius, Stone’s Hand",
        "type": "Ascended God",
        "alignment": "Neutral Good",
        "domains": ["Earth", "Endurance", "Travel", "Protection"],
        "lore": "Way-maker of deserts and ruins; patron of wardens, guides, and any who swear to defend oases and lifelines across the sands."
    },
    {
        "name": "Apela Kelsoe, Windrider",
        "type": "Ascended God",
        "alignment": "Chaotic Good",
        "domains": ["Air", "Travel", "Liberation", "Luck"],
        "lore": "Sky-borne pathfinder whose favor rides in free winds, bold voyages, and leaps of faith."
    },
    {
        "name": "Kaile’a, Mistress of Waves",
        "type": "Ascended God",
        "alignment": "Neutral Good",
        "domains": ["Water", "Travel", "Luck", "Community"],
        "lore": "Beloved mariner-saint of riverfolk and coast towns; her tide binds trade, kinship, and safe harbors."
    },
    # Atheist/None
    {
        "name": "None/Atheist",
        "type": "None",
        "alignment": "Any",
        "domains": [],
        "lore": "No patron deity."
    }
]

ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil"
]

STARTING_EQUIPMENT = {
    "Barbarian": ["Greataxe", "Hide Armor", "Explorer's Pack"],
    "Rogue": ["Shortsword", "Leather Armor", "Thieves' Tools"],
    "Ranger": ["Longbow", "Studded Leather Armor", "Explorer's Pack"],
    "Wizard": ["Quarterstaff", "Spellbook", "Component Pouch"],
    "Sorcerer": ["Dagger", "Light Crossbow", "Component Pouch"],
    # Add more as needed
}

async def handle_client(reader, writer, world, parser):
    logger.info("New client connected")
    writer.write(b"Welcome to Oreka MUD!\n")
    writer.write(b"Do you have an existing character? (y/n): ")
    resp = (await reader.read(10)).decode().strip().lower()
    import hashlib
    import os
    if resp == 'y':
        writer.write(b"Enter your character name: ")
        username = (await reader.read(100)).decode().strip()
        writer.write(b"Enter your password: ")
        password = (await reader.read(100)).decode().strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # Special case: Dagdan immortal login
        if username.lower() == "dagdan":
            expected_hash = hashlib.sha256("Purple#5186".encode()).hexdigest()
            if hashed_password != expected_hash:
                logger.warning(f"Invalid password attempt for Dagdan")
                writer.write(b"Invalid password! Connection closed.\n")
                writer.close()
                return
            character = Character(
                name="Dagdan",
                title="The United Sun",
                race="Half-Giant",
                level=60,
                hp=600,
                max_hp=600,
                ac=30,
                room=world.rooms[1000],
                is_immortal=True,
                elemental_affinity="Fire",
                str_score=30,
                dex_score=16,
                con_score=20,
                int_score=18,
                wis_score=20,
                cha_score=22,
                mana=200,
                max_mana=200,
                move=150,
                max_move=150,
                alignment="Lawful Good",
                deity="Aureon (Sun, Law, Knowledge)"
            )
            character.is_ai = False
            # Store writer/reader for async commands
            character.writer = writer
            character.reader = reader
            world.players.append(character)
            character.room.players.append(character)
            # Do not announce Dagdan on startup
            # Initial room display and game loop
            RED_BOLD = '\033[1;31m'
            WHITE = '\033[37m'
            RESET = '\033[0m'
            def format_room_output(room, look_result, exits, prompt, add_space=False):
                space = "\n" if add_space else ""
                return (f"{space}{RED_BOLD}{room.name}{RESET}\n"
                        f"{WHITE}{look_result}\nExits [{', '.join(exits)}]\n{prompt} {RESET}")
            look_result = parser.cmd_look(character, "")
            writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt()).encode())
            last_room_vnum = character.room.vnum
            save_path = f"data/{character.name.lower()}.json"
            while True:
                data = await reader.read(100)
                if not data:
                    break
                command = data.decode().strip().split(maxsplit=1)
                cmd = command[0].lower()
                args = command[1] if len(command) > 1 else ""
                add_space = False
                prev_room_vnum = character.room.vnum
                if cmd in parser.commands:
                    result = parser.commands[cmd](character, args)
                    if cmd == "look":
                        writer.write(format_room_output(character.room, result, character.room.exits.keys(), character.get_prompt()).encode())
                    else:
                        writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}".encode())
                elif cmd in ["south", "east", "west"]:
                    result = parser.cmd_move(character, cmd)
                    add_space = character.room.vnum != prev_room_vnum
                    if "move" in result:
                        look_result = parser.cmd_look(character, "")
                        writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt(), add_space=add_space).encode())
                    else:
                        writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}".encode())
                else:
                    writer.write(f"{WHITE}Unknown command.\n{character.get_prompt()} {RESET}".encode())
                await writer.drain()
                if getattr(character, 'is_ai', False):
                    ai_result = await character.ai_decide(world)
                    add_space = character.room.vnum != prev_room_vnum
                    if "move" in ai_result:
                        look_result = parser.cmd_look(character, "")
                        writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt(), add_space=add_space).encode())
                    else:
                        writer.write(f"{WHITE}{ai_result}\n{character.get_prompt()} {RESET}".encode())
                    await writer.drain()
            # Save character on disconnect
            world.players.remove(character)
            character.room.players.remove(character)
            try:
                with open(save_path, "w") as f:
                    json.dump(character.to_dict(), f, indent=2)
                logger.info(f"Saved character {character.name} to {save_path}")
            except Exception as e:
                logger.error(f"Failed to save character {character.name}: {e}")
            logger.info(f"Character {character.name} disconnected")
            writer.close()
            return
        elif username.lower() == "hareem":
            expected_hash = hashlib.sha256("Bulldog3".encode()).hexdigest()
            if hashed_password != expected_hash:
                logger.warning(f"Invalid password attempt for Hareem")
                writer.write(b"Invalid password! Connection closed.\n")
                writer.close()
                return
            character = Character(
                name="Hareem",
                title="The Golden Rose",
                race="Human",
                level=60,
                hp=600,
                max_hp=600,
                ac=30,
                room=world.rooms[1000],
                is_immortal=True,
                str_score=18,
                dex_score=20,
                con_score=18,
                int_score=22,
                wis_score=28,
                cha_score=30,
                mana=300,
                max_mana=300,
                move=200,
                max_move=200,
                alignment="Chaotic Good",
                deity="Hareem, The Golden Rose",
                feats=["Leadership", "Skill Focus (Perform)", "Skill Focus (Diplomacy)", "Epic Reputation"],
                domains=["Good", "Charm", "Community", "Retribution"]
            )
            character.is_ai = False
            character.writer = writer
            character.reader = reader
            world.players.append(character)
            character.room.players.append(character)
            RED_BOLD = '\033[1;31m'
            WHITE = '\033[37m'
            RESET = '\033[0m'
            def format_room_output(room, look_result, exits, prompt, add_space=False):
                space = "\n" if add_space else ""
                return (f"{space}{RED_BOLD}{room.name}{RESET}\n"
                        f"{WHITE}{look_result}\nExits [{', '.join(exits)}]\n{prompt} {RESET}")
            look_result = parser.cmd_look(character, "")
            writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt()).encode())
            last_room_vnum = character.room.vnum
            save_path = f"data/{character.name.lower()}.json"
            while True:
                data = await reader.read(100)
                if not data:
                    break
                command = data.decode().strip().split(maxsplit=1)
                cmd = command[0].lower()
                args = command[1] if len(command) > 1 else ""
                add_space = False
                prev_room_vnum = character.room.vnum
                if cmd in parser.commands:
                    result = parser.commands[cmd](character, args)
                    if cmd == "look":
                        writer.write(format_room_output(character.room, result, character.room.exits.keys(), character.get_prompt()).encode())
                    else:
                        writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}".encode())
                elif cmd in ["south", "east", "west"]:
                    result = parser.cmd_move(character, cmd)
                    add_space = character.room.vnum != prev_room_vnum
                    if "move" in result:
                        look_result = parser.cmd_look(character, "")
                        writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt(), add_space=add_space).encode())
                    else:
                        writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}".encode())
                else:
                    writer.write(f"{WHITE}Unknown command.\n{character.get_prompt()} {RESET}".encode())
                await writer.drain()
                if getattr(character, 'is_ai', False):
                    ai_result = await character.ai_decide(world)
                    add_space = character.room.vnum != prev_room_vnum
                    if "move" in ai_result:
                        look_result = parser.cmd_look(character, "")
                        writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt(), add_space=add_space).encode())
                    else:
                        writer.write(f"{WHITE}{ai_result}\n{character.get_prompt()} {RESET}".encode())
                    await writer.drain()
            world.players.remove(character)
            character.room.players.remove(character)
            try:
                with open(save_path, "w") as f:
                    json.dump(character.to_dict(), f, indent=2)
                logger.info(f"Saved character {character.name} to {save_path}")
            except Exception as e:
                logger.error(f"Failed to save character {character.name}: {e}")
            logger.info(f"Character {character.name} disconnected")
            writer.close()
            return
        else:
            save_path = f"data/{username.lower()}.json"
            if not os.path.exists(save_path):
                writer.write(b"Character not found. Disconnecting.\n")
                writer.close()
                return
            try:
                with open(save_path, "r") as f:
                    char_data = json.load(f)
                if char_data.get("hashed_password") != hashed_password:
                    writer.write(b"Incorrect password. Disconnecting.\n")
                    writer.close()
                    return
                # Load character from file
                character = Character.from_dict(char_data, world)
                # Place in correct room
                if hasattr(character, 'room') and character.room:
                    if character.room not in world.rooms.values():
                        character.room = world.rooms[1000]
                else:
                    character.room = world.rooms[1000]
                # Continue to game loop below
            except Exception as e:
                writer.write(b"Failed to load character. Disconnecting.\n")
                writer.close()
                return
    else:
        # New character creation flow
        writer.write(b"Enter your email: ")
        email_data = await reader.read(100)
        email = email_data.decode().strip()
        writer.write(b"Enter your character name: ")
        username_data = await reader.read(100)
        username = username_data.decode().strip()
        writer.write(b"Enter password: ")
        password = (await reader.read(100)).decode().strip()
        writer.write(b"Confirm password: ")
        confirm = (await reader.read(100)).decode().strip()
        if password != confirm:
            writer.write(b"Passwords do not match. Try again.\n")
            return await handle_client(reader, writer, world, parser)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Stat rolling: 4d6 drop lowest, six times, allow up to 3 re-rolls
        import random
        def roll_stat():
            rolls = [random.randint(1,6) for _ in range(4)]
            return sum(sorted(rolls)[1:])
        stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        rerolls = 3
        while True:
            stats = [roll_stat() for _ in range(6)]
            stat_dict = dict(zip(stat_names, stats))
            writer.write(b"\nYour rolled stats (4d6 drop lowest):\n")
            for name in stat_names:
                writer.write(f"  {name}: {stat_dict[name]}\n".encode())
            if rerolls == 0:
                writer.write(b"No re-rolls remaining. These stats will be used.\n")
                break
            writer.write(f"You have {rerolls} re-roll(s) left. Re-roll stats? (y/n): ".encode())
            resp = (await reader.read(10)).decode().strip().lower()
            if resp == 'y':
                rerolls -= 1
                continue
            else:
                break

        # Race selection (allow number or name)
        races = character_creation_prompt(writer)
        race_choice_data = await reader.read(100)
        race_choice_raw = race_choice_data.decode().strip()
        chosen_race = None
        try:
            race_choice = int(race_choice_raw)
            if 1 <= race_choice <= len(races):
                chosen_race = races[race_choice-1][0]
        except Exception:
            # Try to match by name (case-insensitive, partial)
            for race, desc in races:
                if race_choice_raw.lower() in race.lower():
                    chosen_race = race
                    break
        if not chosen_race:
            chosen_race = races[0][0]

        # Class selection (all classes in CLASSES)
        class_names = list(CLASSES.keys())
        writer.write(b"\nChoose your class (type the number or name):\n")
        for i, cname in enumerate(class_names, 1):
            writer.write(f"  {i}. {cname}\n".encode())
        writer.write(b"Enter choice: ")
        class_choice_data = await reader.read(100)
        class_choice_raw = class_choice_data.decode().strip()
        chosen_class = None
        try:
            class_choice = int(class_choice_raw)
            if 1 <= class_choice <= len(class_names):
                chosen_class = class_names[class_choice-1]
        except Exception:
            # Try to match by name (case-insensitive, partial)
            for cname in class_names:
                if class_choice_raw.lower() in cname.lower():
                    chosen_class = cname
                    break
        if not chosen_class:
            chosen_class = class_names[0]

        # Assign stats to variables for skill point calculation
        str_score = stat_dict["STR"]
        dex_score = stat_dict["DEX"]
        con_score = stat_dict["CON"]
        int_score = stat_dict["INT"]
        wis_score = stat_dict["WIS"]
        cha_score = stat_dict["CHA"]

        # Pass int_score and chosen_race to prompt_skills via frame
        import inspect
        frame = inspect.currentframe()
        frame.f_locals['int_score'] = int_score
        frame.f_locals['chosen_race'] = chosen_race
        skills = await prompt_skills(writer, reader, chosen_class)
        spells = await prompt_spells(writer, reader, chosen_class)
        # Prompt for alignment and deity
        alignment = await prompt_alignment(writer, reader)
        deity = await prompt_deity(writer, reader)
        # Prompt for domains if class grants them (e.g., Cleric)
        domains = []
        if chosen_class == "Cleric":
            from src.spells import DOMAIN_DATA
            domain_names = list(DOMAIN_DATA.keys())
            writer.write(b"\nChoose two domains for your Cleric (comma separated numbers):\n")
            for i, d in enumerate(domain_names, 1):
                writer.write(f"  {i}. {d} - {DOMAIN_DATA[d]['power']}\n".encode())
            writer.write(b"Enter choices: ")
            domain_choices = (await reader.read(100)).decode().strip().split(",")
            for c in domain_choices:
                try:
                    idx = int(c.strip()) - 1
                    if 0 <= idx < len(domain_names):
                        domains.append(domain_names[idx])
                except Exception:
                    continue
            domains = domains[:2]
        # Use a temp Character to filter eligible feats (now with domains)
        start_room = world.rooms[1000]
        temp_char = Character(username, None, chosen_race, 1, 10, 10, 10, start_room, char_class=chosen_class, skills=skills, spells_known=spells, alignment=alignment, deity=deity, domains=domains)
        feats = await prompt_feats(writer, reader, character=temp_char)
        # Confirm character summary (add domains and stats)
        equipment = get_starting_equipment(chosen_class)
        summary = build_character_sheet(
            username, chosen_race, chosen_class, alignment, deity, domains, skills, spells, feats, equipment,
            stats=stat_dict
        )
        if not await confirm_character(writer, reader, summary):
            writer.write(b"Restarting character creation...\n")
            return await handle_client(reader, writer, world, parser)
        # Convert spells list to dict by level for compatibility with cmd_spells
        from src.spells import SPELLS
        spells_by_level = {}
        for spell_name in spells:
            spell_obj = next((s for s in SPELLS if s["name"] == spell_name), None)
            if spell_obj:
                for cls, lvl in spell_obj.get("level", {}).items():
                    if cls == chosen_class:
                        spells_by_level.setdefault(lvl, []).append(spell_name)
        # fallback: if no levels found, put all at level 1
        if not spells_by_level and spells:
            spells_by_level[1] = spells

        character = Character(
            username, None, chosen_race, 1, 10, 10, 10, start_room,
            char_class=chosen_class, skills=skills, spells_known=spells_by_level, feats=feats,
            alignment=alignment, deity=deity, domains=domains,
            str_score=str_score, dex_score=dex_score, con_score=con_score,
            int_score=int_score, wis_score=wis_score, cha_score=cha_score
        )
        character.hashed_password = hashed_password
    # Special case: Dagdan (immortal/AI)
    if username.lower() == "dagdan":
        writer.write(b"Enter password: ")
        password_data = await reader.read(100)
        password = password_data.decode().strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        expected_hash = hashlib.sha256("Purple#5186".encode()).hexdigest()
        if hashed_password != expected_hash:
            logger.warning(f"Invalid password attempt for Dagdan")
            writer.write(b"Invalid password! Connection closed.\n")
            writer.close()
            return
        # Dagdan is always Lawful Good, worships Aureon, and is not AI
        character = Character(
            name="Dagdan",
            title="The United Sun",
            race="Half-Giant",
            level=60,
            hp=600,
            max_hp=600,
            ac=30,
            room=start_room,
            is_immortal=True,
            elemental_affinity="Fire",
            str_score=30,
            dex_score=16,
            con_score=20,
            int_score=18,
            wis_score=20,
            cha_score=22,
            mana=200,
            max_mana=200,
            move=150,
            max_move=150,
            alignment="Lawful Good",
            deity="Aureon (Sun, Law, Knowledge)"
        )
        character.is_ai = False
    # Special case: Hareem (immortal)
    elif username.lower() == "hareem":
        writer.write(b"Enter password: ")
        password_data = await reader.read(100)
        password = password_data.decode().strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        expected_hash = hashlib.sha256("Bulldog3".encode()).hexdigest()
        if hashed_password != expected_hash:
            logger.warning(f"Invalid password attempt for Hareem")
            writer.write(b"Invalid password! Connection closed.\n")
            writer.close()
            return
        character = Character(
            name="Hareem",
            title="The Golden Rose",
            race="Human",
            level=60,
            hp=600,
            max_hp=600,
            ac=30,
            room=start_room,
            is_immortal=True,
            str_score=18,
            dex_score=20,
            con_score=18,
            int_score=22,
            wis_score=28,
            cha_score=30,
            mana=300,
            max_mana=300,
            move=200,
            max_move=200,
            alignment="Chaotic Good",
            deity="Hareem, The Golden Rose",
            feats=["Leadership", "Skill Focus (Perform)", "Skill Focus (Diplomacy)", "Epic Reputation"],
            domains=["Good", "Charm", "Community", "Retribution"]
        )
        character.is_ai = False

    # AI player setup (if needed)
    if hasattr(character, 'is_ai') and character.is_ai:
        if not getattr(character, 'alignment', None):
            character.alignment = "True Neutral"
        if not getattr(character, 'deity', None):
            character.deity = "None/Atheist"

    # Store writer/reader for async commands (like levelup Bonus Feat prompt)
    character.writer = writer
    character.reader = reader
    world.players.append(character)
    character.room.players.append(character)
    # Do not announce Dagdan on startup
    if character.name.lower() != "dagdan":
        logger.info(f"Character {character.name} logged in")

    # ANSI color codes
    RED_BOLD = '\033[1;31m'
    WHITE = '\033[37m'
    RESET = '\033[0m'

    def format_room_output(room, look_result, exits, prompt, add_space=False):
        space = "\n" if add_space else ""
        return (f"{space}{RED_BOLD}{room.name}{RESET}\n"
                f"{WHITE}{look_result}\nExits [{', '.join(exits)}]\n{prompt} {RESET}")

    # Initial room display
    look_result = parser.cmd_look(character, "")
    writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt()).encode())
    last_room_vnum = character.room.vnum
    save_path = f"data/{character.name.lower()}.json"
    while True:
        data = await reader.read(100)
        if not data:
            break
        command = data.decode().strip().split(maxsplit=1)
        cmd = command[0].lower()
        args = command[1] if len(command) > 1 else ""

        add_space = False
        prev_room_vnum = character.room.vnum

        if cmd in parser.commands:
            result = parser.commands[cmd](character, args)
            if cmd == "look":
                writer.write(format_room_output(character.room, result, character.room.exits.keys(), character.get_prompt()).encode())
            else:
                writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}".encode())
        elif cmd in ["south", "east", "west"]:
            result = parser.cmd_move(character, cmd)
            # Check if room changed
            add_space = character.room.vnum != prev_room_vnum
            if "move" in result:
                look_result = parser.cmd_look(character, "")
                writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt(), add_space=add_space).encode())
            else:
                writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}".encode())
        else:
            writer.write(f"{WHITE}Unknown command.\n{character.get_prompt()} {RESET}".encode())

        await writer.drain()

        if getattr(character, 'is_ai', False):
            ai_result = await character.ai_decide(world)
            # Check if room changed for AI
            add_space = character.room.vnum != prev_room_vnum
            if "move" in ai_result:
                look_result = parser.cmd_look(character, "")
                writer.write(format_room_output(character.room, look_result, character.room.exits.keys(), character.get_prompt(), add_space=add_space).encode())
            else:
                writer.write(f"{WHITE}{ai_result}\n{character.get_prompt()} {RESET}".encode())
            await writer.drain()

    # Save character on disconnect
    world.players.remove(character)
    character.room.players.remove(character)
    try:
        with open(save_path, "w") as f:
            json.dump(character.to_dict(), f, indent=2)
        logger.info(f"Saved character {character.name} to {save_path}")
    except Exception as e:
        logger.error(f"Failed to save character {character.name}: {e}")
    logger.info(f"Character {character.name} disconnected")
    writer.close()

def character_creation_prompt(writer):
    races = [
        ("Giant", "First People: Born of all four elements; ancient stewards and builders."),
        ("Half-Giant", "Forged lineages: Rare hybrids with Giant essence; bridge peoples."),
        ("Hasura Elf", "Treetop artisans/scholars, airy grace and craft."),
        ("Kovaka Elf", "Earth-revering wardens and hunters."),
        ("Pasua Elf", "Wind-song storytellers and travelers."),
        ("Na'wasua Elf", "Mist-veiled mystics of star and twilight."),
        ("Vestri Dwarf", "Stone-working traditions (river/stone ties)."),
        ("Pekakarlik Dwarf", "River-trade and watercraft specialists."),
        ("Rarozhki Dwarf", "Volcanic-forge masters (embersteel, etc.)."),
        ("Halfling", "Sea/water-touched wanderers and festival-folk."),
        ("Orian Human", "Stone-favored keepers and founders."),
        ("Taraf-Imro Human", "Fire-bound warriors and smiths."),
        ("Eruskan Human", "Water-tied seafarers of the great rivers/sea."),
        ("Mytroan Human", "Wind-leaning desert/steppe folk; swift arts of air.")
    ]
    writer.write(b"\nChoose your race (type the number):\n")
    for i, (race, desc) in enumerate(races, 1):
        writer.write(f"  {i}. {race} - {desc}\n".encode())
    writer.write(b"Enter choice: ")
    return races

async def prompt_username_password(writer, reader):
    writer.write(b"Enter your email: ")
    email_data = await reader.read(100)
    email = email_data.decode().strip()
    writer.write(b"Enter your username: ")
    username_data = await reader.read(100)
    username = username_data.decode().strip()
    writer.write(b"Enter password: ")
    password = (await reader.read(100)).decode().strip()
    writer.write(b"Confirm password: ")
    confirm = (await reader.read(100)).decode().strip()
    if password != confirm:
        writer.write(b"Passwords do not match. Try again.\n")
        return await prompt_username_password(writer, reader)
    import hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return username, hashed_password

async def prompt_class(writer, reader):
    class_names = list(CLASSES.keys())
    writer.write(b"\nChoose your class (type the number):\n")
    for i, cname in enumerate(class_names, 1):
        writer.write(f"  {i}. {cname}\n".encode())
    writer.write(b"Enter choice: ")
    class_choice_data = await reader.read(10)
    try:
        class_choice = int(class_choice_data.decode().strip())
        if 1 <= class_choice <= len(class_names):
            chosen_class = class_names[class_choice-1]
        else:
            chosen_class = class_names[0]
    except Exception:
        chosen_class = class_names[0]
    return chosen_class

async def prompt_skills(writer, reader, chosen_class):
    class_skills = CLASSES[chosen_class]["class_skills"]
    # Get int_score and chosen_race from the call stack (globals in main.py)
    import inspect
    frame = inspect.currentframe().f_back
    int_score = frame.f_locals.get('int_score', 10)
    chosen_race = frame.f_locals.get('chosen_race', '')
    int_mod = (int_score - 10) // 2
    base = CLASSES[chosen_class]["skill_points"]
    skill_points = max((base + int_mod), 1) * 4  # 1st level: base + Int mod, min 1, times 4
    if 'Human' in chosen_race:
        skill_points += 4
    skills = {s: 0 for s in class_skills}
    spent = 0
    writer.write(f"\nYou have {skill_points} skill points to spend.\n".encode())
    def show_skills():
        writer.write(b"\nCurrent skills:\n")
        for s in class_skills:
            writer.write(f"  {s}: {skills[s]}\n".encode())
        writer.write(f"Points remaining: {skill_points - spent}\n".encode())
    show_skills()
    while spent < skill_points:
        writer.write(b"Type 'add <number> <skill>' to allocate, or 'help <skill>' for info.\n")
        cmd = (await reader.read(100)).decode().strip()
        if cmd.lower().startswith("help "):
            skill_name = cmd[5:].strip()
            # For now, just echo the skill name; you can expand with real info
            writer.write(f"Info about {skill_name}: (description here)\n".encode())
            continue
        if cmd.lower().startswith("add "):
            try:
                parts = cmd.split()
                num = int(parts[1])
                skill = " ".join(parts[2:])
                if skill not in class_skills:
                    writer.write(b"Invalid skill name.\n")
                    continue
                if num < 0:
                    writer.write(b"Cannot add negative points.\n")
                    continue
                if spent + num > skill_points:
                    writer.write(b"Not enough points remaining.\n")
                    continue
                skills[skill] += num
                spent += num
                show_skills()
            except Exception:
                writer.write(b"Invalid command format. Use: add <number> <skill>\n")
            continue
        writer.write(b"Unknown command. Use 'add <number> <skill>' or 'help <skill>'.\n")
    return skills

async def prompt_spells(writer, reader, chosen_class, domains=None):
    from src.spells import DOMAIN_DATA
    spell_list = [s for s in SPELLS if chosen_class in s["level"] and s["level"][chosen_class] == 1]
    # Add domain spells for 1st level if domains are provided
    if domains and chosen_class == "Cleric":
        for domain in domains:
            domain_spell = DOMAIN_DATA.get(domain, {}).get("spells", {}).get(1)
            if domain_spell:
                # Find the spell object by name
                spell_obj = next((s for s in SPELLS if s["name"] == domain_spell), None)
                if spell_obj:
                    spell_list.append(spell_obj)
    if not spell_list:
        return []
    writer.write(b"\nChoose your starting spells (comma separated numbers):\n")
    for i, spell in enumerate(spell_list, 1):
        writer.write(f"  {i}. {spell['name']} - {spell['description']}\n".encode())
    writer.write(b"Enter choices: ")
    choices = (await reader.read(100)).decode().strip().split(",")
    chosen = []
    for c in choices:
        try:
            idx = int(c.strip()) - 1
            if 0 <= idx < len(spell_list):
                chosen.append(spell_list[idx]["name"])
        except Exception:
            continue
    return chosen


from src.feats import list_eligible_feats

async def prompt_feats(writer, reader, character=None, allow_multiple=False):
    """
    Prompt the user to select one or more eligible feats. If character is None, show all feats.
    """
    if character:
        eligible_feats = list_eligible_feats(character)
    else:
        eligible_feats = list(FEATS.keys())
    if not eligible_feats:
        writer.write(b"No eligible feats available.\n")
        return []
    writer.write(b"\nChoose your feat(s):\n")
    for i, fname in enumerate(eligible_feats, 1):
        writer.write(f"  {i}. {fname} - {FEATS[fname].description}\n".encode())
    if allow_multiple:
        writer.write(b"Enter numbers separated by commas: ")
        feat_choice_data = await reader.read(100)
        choices = feat_choice_data.decode().strip().split(",")
        chosen = []
        for c in choices:
            try:
                idx = int(c.strip()) - 1
                if 0 <= idx < len(eligible_feats):
                    chosen.append(eligible_feats[idx])
            except Exception:
                continue
        return chosen
    else:
        writer.write(b"Enter choice: ")
        feat_choice_data = await reader.read(10)
        try:
            feat_choice = int(feat_choice_data.decode().strip())
            if 1 <= feat_choice <= len(eligible_feats):
                chosen_feat = eligible_feats[feat_choice-1]
            else:
                chosen_feat = eligible_feats[0]
        except Exception:
            chosen_feat = eligible_feats[0]
        return [chosen_feat]


async def prompt_deity(writer, reader):
    writer.write(b"\nChoose your deity (type the number):\n")
    for i, d in enumerate(DEITIES, 1):
        domains = f"Domains: {', '.join(d['domains'])}" if d['domains'] else ""
        writer.write(f"  {i}. {d['name']} [{d['alignment']}] {domains}\n     {d['lore']}\n".encode())
    writer.write(b"Enter choice: ")
    data = await reader.read(10)
    try:
        idx = int(data.decode().strip())
        if 1 <= idx <= len(DEITIES):
            return DEITIES[idx-1]['name']
    except Exception:
        pass
    return DEITIES[0]['name']


async def prompt_alignment(writer, reader):
    writer.write(b"\nChoose your alignment (type the number):\n")
    for i, a in enumerate(ALIGNMENTS, 1):
        writer.write(f"  {i}. {a}\n".encode())
    writer.write(b"Enter choice (or 'r' to roll randomly): ")
    data = await reader.read(10)
    val = data.decode().strip().lower()
    if val == 'r':
        import random
        return random.choice(ALIGNMENTS)
    try:
        idx = int(val)
        if 1 <= idx <= len(ALIGNMENTS):
            return ALIGNMENTS[idx-1]
    except Exception:
        pass
    return ALIGNMENTS[0]

def get_starting_equipment(chosen_class):
    return STARTING_EQUIPMENT.get(chosen_class, ["Club", "Traveler's Clothes"])

def build_character_sheet(username, chosen_race, chosen_class, alignment, deity, domains, skills, spells, feats, equipment, stats=None):
    # This function builds a pretty character sheet for confirmation
    lines = []
    lines.append("+" + "-"*56 + "+")
    lines.append("|{:^56s}|".format("Character Summary"))
    lines.append("+" + "-"*56 + "+")
    lines.append(f"| Name: {username:<15} Race: {chosen_race:<15} Class: {chosen_class:<15}|")
    lines.append(f"| Alignment: {alignment:<15} Deity: {deity:<23}|")
    if domains:
        lines.append(f"| Domains: {', '.join(domains):<50}|")
    if stats:
        stat_line = ' '.join(f"{k}: {v}" for k, v in stats.items())
        lines.append(f"| Stats: {stat_line:<50}|")
        # Add D&D 3.5 saves to the summary
        # Calculate saves using class progression and ability mods
        class_data = CLASSES.get(chosen_class, {})
        def calc_save(save_type):
            prog = class_data.get('save_progression', {}).get(save_type, 'poor')
            lvl = 1  # Always level 1 at creation
            if prog == 'good':
                base = 2 + (lvl // 2)
            else:
                base = lvl // 3
            if save_type == 'fort':
                mod = (stats.get('CON', 10) - 10) // 2
            elif save_type == 'ref':
                mod = (stats.get('DEX', 10) - 10) // 2
            else:
                mod = (stats.get('WIS', 10) - 10) // 2
            return base + mod
        fort = calc_save('fort')
        ref = calc_save('ref')
        will = calc_save('will')
        lines.append(f"| Saves: Fortitude {fort}  Reflex {ref}  Will {will:<28}|")
    lines.append("+" + "-"*56 + "+")
    lines.append(f"| Skills: {', '.join(f'{k} {v}' for k,v in skills.items())[:50]:<50}|")
    lines.append(f"| Spells: {', '.join(spells)[:50]:<50}|")
    lines.append(f"| Feats: {', '.join(feats)[:50]:<50}|")
    lines.append(f"| Equipment: {', '.join(equipment)[:50]:<50}|")
    lines.append("+" + "-"*56 + "+")
    return "\n".join(lines)

async def confirm_character(writer, reader, summary):
    writer.write(b"\n")
    writer.write(summary.encode() + b"\n")
    writer.write(b"Confirm character? (y/n): ")
    data = await reader.read(10)
    return data.decode().strip().lower() == 'y'

# In handle_client, after all prompts:
# deity = await prompt_deity(writer, reader)
# alignment = await prompt_alignment(writer, reader)
# equipment = get_starting_equipment(chosen_class)
# summary = f"Name: {username}\nRace: {chosen_race}\nClass: {chosen_class}\nAlignment: {alignment}\nDeity: {deity}\nSkills: {skills}\nSpells: {spells}\nFeats: {feats}\nEquipment: {equipment}"
# if not await confirm_character(writer, reader, summary):
#     ...restart creation...
# else:
#     ...create and save character...

async def log_players(world):
    while True:
        logger.info(f"Active players: {[p.name for p in world.players]}")
        await asyncio.sleep(60)

async def main():

    world = OrekaWorld()
    world.load_data()
    parser = CommandParser(world)

    # --- Spawn a level 1 monster from mobs.json in all chapel.json rooms ---
    import os
    import random
    from src.mob import Mob
    import json as _json
    # Load all level 1 monsters from mobs.json
    mobs_path = os.path.join(os.path.dirname(__file__), "data", "mobs.json")
    with open(mobs_path, "r") as f:
        all_mobs = _json.load(f)
    level1_mobs = [m for m in all_mobs if m.get("level", 0) == 1]
    if not level1_mobs:
        raise Exception("No level 1 monsters found in mobs.json!")
    # Find chapel.json rooms (by area or filename in room data)
    chapel_rooms = [room for room in world.rooms.values() if getattr(room, 'area', '').lower() == 'chapel' or getattr(room, 'filename', '').lower() == 'chapel.json']
    if not chapel_rooms:
        # Fallback: try to match by vnum range if known (e.g., 2000-2099)
        chapel_rooms = [room for room in world.rooms.values() if 2000 <= getattr(room, 'vnum', 0) < 2100]
    for room in chapel_rooms:
        mob_data = random.choice(level1_mobs)
        # Use Mob.from_dict if available, else fallback to Mob constructor
        mob = None
        if hasattr(Mob, 'from_dict'):
            mob = Mob.from_dict(mob_data, world)
            mob.room = room
        else:
            mob = Mob(
                vnum=mob_data.get("vnum", 0),
                name=mob_data.get("name", "Level 1 Monster"),
                level=mob_data.get("level", 1),
                hp_dice=mob_data.get("hp_dice", [1,6,0]),
                ac=mob_data.get("ac", 10),
                damage_dice=mob_data.get("damage_dice", [1,2,0]),
                flags=mob_data.get("flags", []),
                type_=mob_data.get("type_", ""),
                alignment=mob_data.get("alignment", "Neutral"),
                ability_scores=mob_data.get("ability_scores", {}),
                initiative=mob_data.get("initiative", 0),
                speed=mob_data.get("speed", {}),
                attacks=mob_data.get("attacks", []),
                special_attacks=mob_data.get("special_attacks", []),
                special_qualities=mob_data.get("special_qualities", []),
                feats=mob_data.get("feats", []),
                skills=mob_data.get("skills", {}),
                saves=mob_data.get("saves", {}),
                environment=mob_data.get("environment", ""),
                organization=mob_data.get("organization", ""),
                cr=mob_data.get("cr", None),
                advancement=mob_data.get("advancement", None),
                description=mob_data.get("description", "A level 1 monster.")
            )
        mob.room = room
        if not hasattr(room, 'mobs'):
            room.mobs = []
        room.mobs.append(mob)

    ai_character = Character("Aelthara", None, "Eruskan Human", 7, 60, 120, 16, world.rooms[1000],
                            str_score=12, dex_score=14, con_score=12, int_score=14, wis_score=12, cha_score=16,
                            mana=100, max_mana=100, move=100, max_move=100)
    ai_character.is_ai = True
    ai_character.quests.append(world.quests[1])
    world.players.append(ai_character)
    world.rooms[1000].players.append(ai_character)

    # Immortal Character: Hareem, The Golden Rose
    hareem = Character(
        name="Hareem",
        title="The Golden Rose",
        race="Human",
        level=60,
        hp=600,
        max_hp=600,
        ac=30,
        room=world.rooms[1000],
        is_immortal=True,
        str_score=18,
        dex_score=20,
        con_score=18,
        int_score=22,
        wis_score=28,
        cha_score=30,
        mana=300,
        max_mana=300,
        move=200,
        max_move=200,
        alignment="Chaotic Good",
        deity="Hareem, The Golden Rose",
        feats=["Leadership", "Skill Focus (Perform)", "Skill Focus (Diplomacy)", "Epic Reputation"],
        domains=["Good", "Charm", "Community", "Retribution"]
    )
    hareem.is_ai = False
    world.players.append(hareem)
    world.rooms[1000].players.append(hareem)

    logger.info("Starting Oreka MUD server on localhost:4000")
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, world, parser), "localhost", 4000
    )
    asyncio.create_task(log_players(world))
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
