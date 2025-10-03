import asyncio

# Global session tracking for all connected users
ACTIVE_SESSIONS = {}  # username: (writer, last_activity)
import telnetlib3
import time
import logging
from .src.world import OrekaWorld
from .src.commands import CommandParser
from .src.character import Character
import json
import getpass
from .src.classes import CLASSES
from .src.feats import FEATS
from .src.spells import SPELLS

import telnetlib3
import unicodedata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrekaMUD")

# Patch telnetlib3 to use utf-8 encoding for all writers
telnetlib3.server_base.DEFAULT_ENCODING = 'utf-8'

def ascii_safe(text):
    if not isinstance(text, str):
        return text
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

import types
def wrap_writer(writer):
    orig_write = writer.write
    def safe_write(s):
        return orig_write(ascii_safe(s))
    writer.write = safe_write
    return writer

DEITIES = [
    {
        "name": "Dagdan, The United Sun",
        "type": "Ascended God",
        "alignment": "Lawful Good",
        "domains": ["Good", "Strength", "Magic"],
        "lore": "The immortal champion who united the tribes and brought the light of knowledge and strength to all peoples.",
    },
    {
        "name": "Aureon",
        "title": "The Sunlord",
        "type": "Elemental Lord",
        "alignment": "Lawful Good",
        "domains": ["Sun", "Law", "Knowledge"],
        "lore": "Original Lord of the Sun, order, and wisdom.",
    },
    {
        "name": "Nerath",
        "title": "The Deep Current",
        "type": "Elemental Lord",
        "alignment": "Neutral",
        "domains": ["Sea", "Change", "Luck"],
        "lore": "Primal god of the sea, tides, and fate.",
    },
    {
        "name": "Vulkar",
        "title": "The Forgefire",
        "type": "Elemental Lord",
        "alignment": "Neutral Good",
        "domains": ["Forge", "Fire", "Earth"],
        "lore": "Smith of the world, master of fire and stone.",
    },
    {
        "name": "Lirael",
        "title": "The Moonweaver",
        "type": "Elemental Lord",
        "alignment": "Chaotic Good",
        "domains": ["Moon", "Magic", "Fate"],
        "lore": "Mistress of the moon, magic, and destiny.",
    },
    {
        "name": "Cinvarin, the Five Witnesses (The Fivefold Flame)",
        "type": "Ascended God",
        "alignment": "Neutral Good",
        "domains": ["Community", "Fire", "Earth", "Air", "Water"],
        "lore": "Five druids merged at the Lament to end the Deceivers and rose as one god of unity and the four elements.",
    },
    {
        "name": "Hareem, The Golden Rose",
        "type": "Ascended God",
        "alignment": "Chaotic Good",
        "domains": ["Good", "Charm", "Community", "Retribution"],
        "lore": "Bard-saint who sacrificed herself to slay the Twelve Kings that abandoned the dwarves, enshrining mercy for Kin and justice for traitors.",
    },
    {
        "name": "Tarvek Wen, Doombringer",
        "type": "Ascended God",
        "alignment": "Lawful Good",
        "domains": ["Law", "Good", "Protection", "Justice"],
        "lore": "Shield and sword of the helpless; patron of oaths kept under fire and liberation from tyrants.",
    },
    {
    "name": "Ludus Galerius, Stone's Hand",
        "type": "Ascended God",
        "alignment": "Neutral Good",
        "domains": ["Earth", "Endurance", "Travel", "Protection"],
        "lore": "Way-maker of deserts and ruins; patron of wardens, guides, and any who swear to defend oases and lifelines across the sands.",
    },
    {
        "name": "Apela Kelsoe, Windrider",
        "type": "Ascended God",
        "alignment": "Chaotic Good",
        "domains": ["Air", "Travel", "Liberation", "Luck"],
        "lore": "Sky-borne pathfinder whose favor rides in free winds, bold voyages, and leaps of faith.",
    },
    {
    "name": "Kailea, Mistress of Waves",
        "type": "Ascended God",
        "alignment": "Neutral Good",
        "domains": ["Water", "Travel", "Luck", "Community"],
        "lore": "Beloved mariner-saint of riverfolk and coast towns; her tide binds trade, kinship, and safe harbors.",
    },
    {
        "name": "None/Atheist",
        "type": "None",
        "alignment": "Any",
        "domains": [],
        "lore": "No patron deity.",
    },
]

ALIGNMENTS = [
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "True Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil",
]

STARTING_EQUIPMENT = {
    "Barbarian": ["Greataxe", "Hide Armor", "Explorer's Pack"],
    "Rogue": ["Shortsword", "Leather Armor", "Thieves' Tools"],
    "Ranger": ["Longbow", "Studded Leather Armor", "Explorer's Pack"],
    "Wizard": ["Quarterstaff", "Spellbook", "Component Pouch"],
    "Sorcerer": ["Dagger", "Light Crossbow", "Component Pouch"],
}

async def handle_client(reader, writer, world, parser):
    logger.info("New client connected")
    writer = wrap_writer(writer)
    character = None
    writer.write("Welcome to Oreka MUD!\n")
    import os
    global ACTIVE_SESSIONS
    if "ACTIVE_SESSIONS" not in globals():
        ACTIVE_SESSIONS = {}

    while True:
        writer.write("Do you have an existing character? (y/n): ")
        resp = (await reader.read(10)).strip().lower()
        if resp == "y":
            writer.write("Enter your character name: ")
            username = (await reader.read(100)).strip()
            if not username:
                writer.write("No username entered. Try again.\n")
                continue
            if username in ACTIVE_SESSIONS:
                try:
                    ACTIVE_SESSIONS[username][0].write(
                        "Your account was logged in elsewhere. Disconnecting.\n"
                    )
                    ACTIVE_SESSIONS[username][0].close()
                except Exception:
                    pass
            ACTIVE_SESSIONS[username] = (writer, time.time())
            writer.write("Enter your password: ")
            password = (await reader.read(100)).strip()
            # Special case: Dagdan
            if username.lower() == "dagdan":
                if password != "Nero123":
                    logger.warning(f"Invalid password attempt for Dagdan")
                    writer.write("Invalid password! Connection closed.\n")
                    writer.close()
                    if (
                        username
                        and username in ACTIVE_SESSIONS
                        and ACTIVE_SESSIONS[username][0] is writer
                    ):
                        del ACTIVE_SESSIONS[username]
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
                    move=150,
                    max_move=150,
                    alignment="Lawful Good",
                    deity="Aureon (Sun, Law, Knowledge)",
                )
                character.is_ai = False
                break
            elif username.lower() == "hareem":
                if password != "Nero123":
                    logger.warning(f"Invalid password attempt for Hareem")
                    writer.write("Invalid password! Connection closed.\n")
                    writer.close()
                    if (
                        username
                        and username in ACTIVE_SESSIONS
                        and ACTIVE_SESSIONS[username][0] is writer
                    ):
                        del ACTIVE_SESSIONS[username]
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
                    move=200,
                    max_move=200,
                    alignment="Chaotic Good",
                    deity="Hareem, The Golden Rose",
                    feats=[
                        "Leadership",
                        "Skill Focus (Perform)",
                        "Skill Focus (Diplomacy)",
                        "Epic Reputation",
                    ],
                    domains=["Good", "Charm", "Community", "Retribution"],
                )
                character.is_ai = False
                break
            else:
                player_path = os.path.join(os.path.dirname(__file__), "data", "players", f"{username.lower()}.json")
                if not os.path.exists(player_path):
                    writer.write("No such character.\n")
                    continue
                with open(player_path, "r", encoding="utf-8") as f:
                    try:
                        pdata = json.load(f)
                    except json.JSONDecodeError:
                        writer.write("Player file is empty or corrupt. Please contact an admin or recreate your character.\n")
                        continue
                if isinstance(pdata, list):
                    pdata = pdata[0]
                # Use Character.from_dict for proper password checking
                character = Character.from_dict(pdata)
                if not character.check_password(password):
                    logger.warning(f"Invalid password attempt for {username}")
                    writer.write("Invalid password! Connection closed.\n")
                    writer.close()
                    if (
                        username
                        and username in ACTIVE_SESSIONS
                        and ACTIVE_SESSIONS[username][0] is writer
                    ):
                        del ACTIVE_SESSIONS[username]
                    return
                character.room = world.rooms.get(pdata.get("room_vnum", 1000), world.rooms[1000])
                break
        elif resp == "n":
            writer.write("Enter your desired character name: ")
            username = (await reader.read(100)).strip()
            if not username:
                writer.write("No username entered. Try again.\n")
                continue
            writer.write("Enter password: ")
            password = (await reader.read(100)).strip()
            writer.write("Confirm password: ")
            confirm = (await reader.read(100)).strip()
            if password != confirm:
                writer.write("Passwords do not match. Try again.\n")
                continue
            races = character_creation_prompt(writer)
            race_choice = (await reader.read(10)).strip()
            try:
                race_idx = int(race_choice) - 1
                chosen_race = races[race_idx][0] if 0 <= race_idx < len(races) else races[0][0]
            except Exception:
                chosen_race = races[0][0]
            import random
            def roll_stat():
                rolls = sorted([random.randint(1,6) for _ in range(4)], reverse=True)
                return sum(rolls[:3])
            stats = [roll_stat() for _ in range(6)]
            stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
            stat_dict = dict(zip(stat_names, stats))
            writer.write(f"Rolled stats: {', '.join(f'{n}: {v}' for n,v in stat_dict.items())}\n")
            chosen_class = await prompt_class(writer, reader)
            skills = await prompt_skills(writer, reader, chosen_class)
            domains = []
            if chosen_class == "Cleric":
                from .src.spells import DOMAIN_DATA
                domain_names = list(DOMAIN_DATA.keys())
                writer.write("\nChoose your first domain for your Cleric:\n")
                for i, d in enumerate(domain_names, 1):
                    writer.write(f"  {i}. {d} - {DOMAIN_DATA[d]['power']}\n")
                writer.write("Enter choice: ")
                first_choice = (await reader.read(100)).strip()
                try:
                    idx = int(first_choice) - 1
                    first_domain = domain_names[idx] if 0 <= idx < len(domain_names) else domain_names[0]
                except Exception:
                    first_domain = domain_names[0]
                domains.append(first_domain)
                remaining_domains = [d for d in domain_names if d != first_domain]
                writer.write("\nChoose your second domain for your Cleric:\n")
                for i, d in enumerate(remaining_domains, 1):
                    writer.write(f"  {i}. {d} - {DOMAIN_DATA[d]['power']}\n")
                writer.write("Enter choice: ")
                second_choice = (await reader.read(100)).strip()
                try:
                    idx = int(second_choice) - 1
                    second_domain = remaining_domains[idx] if 0 <= idx < len(remaining_domains) else remaining_domains[0]
                except Exception:
                    second_domain = remaining_domains[0]
                domains.append(second_domain)
            spells = await prompt_spells(writer, reader, chosen_class, domains)
            temp_char = Character(
                username, None, chosen_race, 1, 10, 10, 10, world.rooms[1000],
                char_class=chosen_class, skills=skills, spells_known=spells,
                alignment=None, deity=None, domains=domains,
                str_score=stat_dict["STR"], dex_score=stat_dict["DEX"], con_score=stat_dict["CON"],
                int_score=stat_dict["INT"], wis_score=stat_dict["WIS"], cha_score=stat_dict["CHA"]
            )
            feats = await prompt_feats(writer, reader, character=temp_char)
            deity = await prompt_deity(writer, reader)
            alignment = await prompt_alignment(writer, reader)
            equipment = get_starting_equipment(chosen_class)
            summary = build_character_sheet(
                username, chosen_race, chosen_class, alignment, deity, domains,
                skills, spells, feats, equipment, stats=stat_dict
            )
            if not await confirm_character(writer, reader, summary):
                writer.write("Restarting character creation...\n")
                continue
            player_path = os.path.join(os.path.dirname(__file__), "data", "players", f"{username.lower()}.json")
            # Create and save character using Character class (handles password hashing)
            character = Character(
                name=username,
                title=None,
                race=chosen_race,
                level=1,
                hp=10,
                max_hp=10,
                ac=10,
                room=world.rooms[1000],
                is_immortal=False,
                elemental_affinity=None,
                str_score=stat_dict["STR"],
                dex_score=stat_dict["DEX"],
                con_score=stat_dict["CON"],
                int_score=stat_dict["INT"],
                wis_score=stat_dict["WIS"],
                cha_score=stat_dict["CHA"],
                move=100,
                max_move=100,
                alignment=alignment,
                deity=deity,
                feats=feats,
                domains=domains,
                char_class=chosen_class,
                skills=skills,
                spells_known=spells,
                password=password,  # <-- Secure password handling!
            )
            character.is_ai = False
            character.save()
            break
        else:
            writer.write("Please enter 'y' or 'n'.\n")
            continue

    if character is None:
        writer.write("Login or character creation failed. Connection closed.\n")
        writer.close()
        return

    character.writer = writer
    character.reader = reader
    world.players.append(character)
    character.room.players.append(character)
    if character.name.lower() != "dagdan":
        logger.info(f"Character {character.name} logged in")

    RED_BOLD = "\033[1;31m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

    def format_room_output(room, look_result, exits, prompt, add_space=False):
        space = "\n" if add_space else ""
        return (
            f"{space}{RED_BOLD}{room.name}{RESET}\n"
            f"{WHITE}{look_result}\nExits [{', '.join(exits)}]\n{prompt} {RESET}"
        )

    look_result = parser.cmd_look(character, "")
    writer.write(
        format_room_output(
            character.room,
            look_result,
            character.room.exits.keys(),
            character.get_prompt(),
        )
    )
    last_room_vnum = character.room.vnum
    while True:
        data = await reader.read(100)
        if not data:
            break
        command = data.strip().split(maxsplit=1)
        cmd = command[0].lower()
        args = command[1] if len(command) > 1 else ""

        add_space = False
        prev_room_vnum = character.room.vnum

        if cmd in parser.commands:
            result = parser.commands[cmd](character, args)
            if cmd == "look":
                writer.write(
                    format_room_output(
                        character.room,
                        result,
                        character.room.exits.keys(),
                        character.get_prompt(),
                    )
                )
            else:
                writer.write(
                    f"{WHITE}{result}\n{character.get_prompt()} {RESET}"
                )
        elif cmd in ["south", "east", "west"]:
            result = parser.cmd_move(character, cmd)
            add_space = character.room.vnum != prev_room_vnum
            if "move" in result:
                look_result = parser.cmd_look(character, "")
                writer.write(
                    format_room_output(
                        character.room,
                        look_result,
                        character.room.exits.keys(),
                        character.get_prompt(),
                        add_space=add_space,
                    )
                )
            else:
                writer.write(
                    f"{WHITE}{result}\n{character.get_prompt()} {RESET}"
                )
        else:
            writer.write(
                f"{WHITE}Unknown command.\n{character.get_prompt()} {RESET}"
            )

        await writer.drain()

        if getattr(character, "is_ai", False):
            ai_result = await character.ai_decide(world)
            add_space = character.room.vnum != prev_room_vnum
            if "move" in ai_result:
                look_result = parser.cmd_look(character, "")
                writer.write(
                    format_room_output(
                        character.room,
                        look_result,
                        character.room.exits.keys(),
                        character.get_prompt(),
                        add_space=add_space,
                    )
                )
            else:
                writer.write(
                    f"{WHITE}{ai_result}\n{character.get_prompt()} {RESET}"
                )
            await writer.drain()

    world.players.remove(character)
    character.room.players.remove(character)
    try:
        character.save()
        logger.info(f"Saved character {character.name}")
    except Exception as e:
        logger.error(f"Failed to save character {character.name}: {e}")
    logger.info(f"Character {character.name} disconnected")
    writer.close()

def character_creation_prompt(writer):
    races = [
        (
            "Giant",
            "First People: Born of all four elements; ancient stewards and builders.",
        ),
        (
            "Half-Giant",
            "Forged lineages: Rare hybrids with Giant essence; bridge peoples.",
        ),
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
        ("Mytroan Human", "Wind-leaning desert/steppe folk; swift arts of air."),
    ]
    writer.write("\nChoose your race (type the number):\n")
    for i, (race, desc) in enumerate(races, 1):
        writer.write(f"  {i}. {race} - {desc}\n")
    writer.write("Enter choice: ")
    return races

async def prompt_class(writer, reader):
    class_names = list(CLASSES.keys())
    writer.write("\nChoose your class (type the number):\n")
    for i, cname in enumerate(class_names, 1):
        writer.write(f"  {i}. {cname}\n")
    writer.write("Enter choice: ")
    class_choice_data = await reader.read(10)
    class_choice_raw = class_choice_data.strip()
    try:
        class_choice = int(class_choice_raw)
        if 1 <= class_choice <= len(class_names):
            chosen_class = class_names[class_choice - 1]
        else:
            chosen_class = class_names[0]
    except Exception:
        chosen_class = class_names[0]
    return chosen_class

async def prompt_skills(writer, reader, chosen_class):
    class_skills = CLASSES[chosen_class]["class_skills"]
    all_skills = set(class_skills)
    for cdata in CLASSES.values():
        all_skills.update(cdata.get("class_skills", []))
    all_skills = sorted(all_skills)
    def skill_base_name(skill):
        if skill.startswith("Craft ("):
            return "Craft (any)"
        if skill.startswith("Profession ("):
            return "Profession (any)"
        if skill.startswith("Perform ("):
            return "Perform (any)"
        return skill
    cross_class_skills = [s for s in all_skills if skill_base_name(s) not in class_skills]
    skills = {s: 0 for s in all_skills}
    import json
    import os
    craft_skills_set = set()
    materials_path = os.path.join(os.path.dirname(__file__), '../data/materials.json')
    try:
        with open(materials_path, 'r', encoding='utf-8') as f:
            materials = json.load(f)
        for mat in materials:
            for skill in mat.get('crafting_skills', []):
                craft_skills_set.add(skill)
    except Exception:
        craft_skills_set = set()
    if craft_skills_set:
        writer.write("\nAvailable crafting skills in this world:\n")
        for skill in sorted(craft_skills_set):
            writer.write(f"  Craft ({skill.capitalize()})\n")
        writer.write("\n")
    writer.write("Skill Rank Limits:\n")
    writer.write("- Class skills: max rank = character level + 3\n")
    writer.write("- Cross-class skills: max rank = (character level + 3) / 2\n")
    writer.write("- Cross-class skills cost 2 points per rank.\n\n")
    import inspect
    frame = inspect.currentframe().f_back
    int_score = frame.f_locals.get("int_score", 10)
    chosen_race = frame.f_locals.get("chosen_race", "")
    int_mod = (int_score - 10) // 2
    base = CLASSES[chosen_class]["skill_points"]
    skill_points = max((base + int_mod), 1) * 4
    if "Human" in chosen_race:
        skill_points += 4
    spent = 0
    writer.write(f"\nYou have {skill_points} skill points to spend.\n")
    def show_skills():
        writer.write("\nCurrent skills:\n")
        for s in all_skills:
            is_cross = skill_base_name(s) not in class_skills
            mark = "*" if is_cross else " "
            writer.write(f"{mark} {s}: {skills[s]}\n")
        writer.write("* = cross-class skill (costs 2 points per rank, max rank = (level+3)/2)\n")
        writer.write(f"Points remaining: {skill_points - spent}\n")
    show_skills()
    max_rank_class = 1 + 3
    max_rank_cross = (1 + 3) // 2
    while spent < skill_points:
        writer.write("Type 'add <number> <skill>' to allocate, or 'help <skill>' for info.\n")
        cmd = (await reader.read(100)).strip()
        if cmd.lower().startswith("help "):
            skill_name = cmd[5:].strip()
            writer.write(f"Info about {skill_name}: (description here)\n")
            continue
        if cmd.lower().startswith("add "):
            try:
                parts = cmd.split()
                num = int(parts[1])
                skill = " ".join(parts[2:])
                if skill not in all_skills:
                    writer.write("Invalid skill name.\n")
                    continue
                is_cross = skill_base_name(skill) not in class_skills
                current = skills[skill]
                if is_cross:
                    max_rank = max_rank_cross
                    cost = num * 2
                else:
                    max_rank = max_rank_class
                    cost = num
                if num < 0:
                    writer.write("Cannot add negative points.\n")
                    continue
                if current + num > max_rank:
                    writer.write(f"Cannot exceed max rank ({max_rank}) for this skill.\n")
                    continue
                if spent + cost > skill_points:
                    writer.write("Not enough points remaining.\n")
                    continue
                skills[skill] += num
                spent += cost
                show_skills()
            except Exception:
                writer.write("Invalid command format. Use: add <number> <skill>\n")
            continue
        writer.write("Unknown command. Use 'add <number> <skill>' or 'help <skill>'.\n")
    return {k: v for k, v in skills.items() if v > 0}

async def prompt_spells(writer, reader, chosen_class, domains=None):
    from .src.spells import DOMAIN_DATA
    spell_list = [
        s
        for s in SPELLS
        if chosen_class in s["level"] and s["level"][chosen_class] == 1
    ]
    if domains and chosen_class == "Cleric":
        for domain in domains:
            domain_spell = DOMAIN_DATA.get(domain, {}).get("spells", {}).get(1)
            if domain_spell:
                spell_obj = next((s for s in SPELLS if s["name"] == domain_spell), None)
                if spell_obj:
                    spell_list.append(spell_obj)
    if not spell_list:
        return []
    writer.write("\nChoose your starting spells (comma separated numbers):\n")
    for i, spell in enumerate(spell_list, 1):
        writer.write(f"  {i}. {spell['name']} - {spell['description']}\n")
    writer.write("Enter choices: ")
    choices = (await reader.read(100)).strip().split(",")
    chosen = []
    for c in choices:
        try:
            idx = int(c.strip()) - 1
            if 0 <= idx < len(spell_list):
                chosen.append(spell_list[idx]["name"])
        except Exception:
            continue
    return chosen

from .src.feats import list_eligible_feats

async def prompt_feats(writer, reader, character=None, allow_multiple=False):
    if character:
        eligible_feats = list_eligible_feats(character)
    else:
        eligible_feats = list(FEATS.keys())
    if not eligible_feats:
        writer.write("No eligible feats available.\n")
        return []
    writer.write("\nChoose your feat(s):\n")
    for i, fname in enumerate(eligible_feats, 1):
        writer.write(f"  {i}. {fname} - {FEATS[fname].description}\n")
    if allow_multiple:
        writer.write("Enter numbers separated by commas: ")
        feat_choice_data = await reader.read(100)
        choices = feat_choice_data.strip().split(",")
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
        writer.write("Enter choice: ")
        feat_choice_data = await reader.read(10)
        try:
            feat_choice = int(feat_choice_data.strip())
            if 1 <= feat_choice <= len(eligible_feats):
                chosen_feat = eligible_feats[feat_choice - 1]
            else:
                chosen_feat = eligible_feats[0]
        except Exception:
            chosen_feat = eligible_feats[0]
        return [chosen_feat]

async def prompt_deity(writer, reader):
    writer.write("\nChoose your deity (type the number):\n")
    for i, d in enumerate(DEITIES, 1):
        domains = f"Domains: {', '.join(d['domains'])}" if d["domains"] else ""
        writer.write(
            f"  {i}. {d['name']} [{d['alignment']}] {domains}\n     {d['lore']}\n"
        )
    writer.write("Enter choice: ")
    data = await reader.read(10)
    try:
        idx = int(data.strip())
        if 1 <= idx <= len(DEITIES):
            return DEITIES[idx - 1]["name"]
    except Exception:
        pass
    return DEITIES[0]["name"]

async def prompt_alignment(writer, reader):
    writer.write("\nChoose your alignment (type the number):\n")
    for i, a in enumerate(ALIGNMENTS, 1):
        writer.write(f"  {i}. {a}\n")
    writer.write("Enter choice (or 'r' to roll randomly): ")
    data = await reader.read(10)
    val = data.strip().lower()
    if val == "r":
        import random
        return random.choice(ALIGNMENTS)
    try:
        idx = int(val)
        if 1 <= idx <= len(ALIGNMENTS):
            return ALIGNMENTS[idx - 1]
    except Exception:
        pass
    return ALIGNMENTS[0]

def get_starting_equipment(chosen_class):
    return STARTING_EQUIPMENT.get(chosen_class, ["Club", "Traveler's Clothes"])

def build_character_sheet(
    username,
    chosen_race,
    chosen_class,
    alignment,
    deity,
    domains,
    skills,
    spells,
    feats,
    equipment,
    stats=None,
):
    lines = []
    lines.append("+" + "-" * 60 + "+")
    lines.append(f"| Name: {username:<20} Level: 1    Title: {'':<25}|")
    lines.append(f"| Race: {chosen_race:<18} Class: {chosen_class:<12}|")
    class_data = CLASSES.get(chosen_class, {})
    class_alignment = class_data.get('alignment', 'Any')
    hit_die = class_data.get('hit_die', 'd8')
    skill_per_level = class_data.get('skill_points', 2)
    bab_prog = class_data.get('bab', '3/4')
    save_prog = class_data.get('save_progression', {'fort': 'poor', 'ref': 'poor', 'will': 'poor'})
    lines.append(f"| Class Alignment: {class_alignment} |")
    lines.append(f"| Hit Die: {hit_die}  Skill/Level: {skill_per_level}  BAB:    {bab_prog}  Saves: {save_prog} |")
    lines.append("+" + "-" * 60 + "+")
    lines.append(f"| Alignment: {alignment:<15} Deity: {deity:<30}|")
    lines.append(f"| Size: Medium     Speed: 100  ft.   Immortal: No    Elemental Affinity: None           |")
    lines.append("+" + "-" * 60 + "+")
    lines.append(f"| HP:  10/10   AC: 10  Touch AC: 10  Flat-Footed AC: 10  |")
    lines.append(f"| BAB: 0   Grapple: 2   |")
    if stats:
        def calc_save(save_type):
            prog = class_data.get("save_progression", {}).get(save_type, "poor")
            lvl = 1
            if prog == "good":
                base = 2 + (lvl // 2)
            else:
                base = lvl // 3
            if save_type == "fort":
                mod = (stats.get("CON", 10) - 10) // 2
            elif save_type == "ref":
                mod = (stats.get("DEX", 10) - 10) // 2
            else:
                mod = (stats.get("WIS", 10) - 10) // 2
            return base + mod
        fort = calc_save("fort")
        ref = calc_save("ref")
        will = calc_save("will")
        lines.append(f"| Fort: {fort:<2}  Ref: {ref:<2}  Will: {will:<2}  |")
    lines.append("+" + "-" * 60 + "+")
    if stats:
        stat_line = "  ".join(f"{k}: {v}" for k, v in stats.items())
        lines.append(f"| {stat_line} |")
        lines.append("+" + "-" * 60 + "+")
    lines.append(f"| XP: 0            |")
    lines.append(f"| Resistances: None                                         |")
    lines.append(f"| Immunities: None                                         |")
    lines.append("+" + "-" * 60 + "+")
    lines.append(f"AC 10 HP 10/10 [{chosen_race}] > ")
    return "\n".join(lines)

async def confirm_character(writer, reader, summary):
    writer.write("\n")
    writer.write(summary + "\n")
    writer.write("Confirm character? (y/n): ")
    data = await reader.read(10)
    return data.strip().lower() == "y"

async def log_players(world):
    while True:
        logger.info(f"Active players: {[p.name for p in world.players]}")
        await asyncio.sleep(60)

async def main():
    world = OrekaWorld()
    world.load_data()
    parser = CommandParser(world)

    ai_character = Character(
        "Aelthara",
        None,
        "Eruskan Human",
        7,
        60,
        120,
        16,
        world.rooms[1000],
        str_score=12,
        dex_score=14,
        con_score=12,
        int_score=14,
        wis_score=12,
        cha_score=16,
        move=100,
        max_move=100,
    )
    ai_character.is_ai = True
    ai_character.quests.append(world.quests[1])
    world.players.append(ai_character)
    world.rooms[1000].players.append(ai_character)

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
        move=200,
        max_move=200,
        alignment="Chaotic Good",
        deity="Hareem, The Golden Rose",
        feats=[
            "Leadership",
            "Skill Focus (Perform)",
            "Skill Focus (Diplomacy)",
            "Epic Reputation",
        ],
        domains=["Good", "Charm", "Community", "Retribution"],
    )
    hareem.is_ai = False
    world.players.append(hareem)
    world.rooms[1000].players.append(hareem)

    logger.info("Starting Oreka MUD server on localhost:4000 (telnetlib3)")

    async def telnet_shell(reader, writer):
        await handle_client(reader, writer, world, parser)

    server = await telnetlib3.create_server(port=4000, shell=telnet_shell)
    asyncio.create_task(log_players(world))
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())