import asyncio
import logging
from src.world import OrekaWorld
from src.commands import CommandParser
from src.character import Character
import hashlib
import getpass
from src.classes import CLASSES
from src.feats import FEATS
from src.spells import SPELLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrekaMUD")

DEITIES = [
    "Aureon (Sun, Law, Knowledge)",
    "Nerath (Sea, Change, Luck)",
    "Vulkar (Forge, Fire, Earth)",
    "Lirael (Moon, Magic, Fate)",
    "Druun (Stone, Endurance, Oaths)",
    "Syris (Wind, Travel, Song)",
    "None/Atheist"
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
    writer.write(b"Welcome to Oreka MUD!\nEnter your name: ")
    name_data = await reader.read(100)
    name = name_data.decode().strip()
    
    import os, json
    start_room = world.rooms[1000]
    save_dir = os.path.join("data", "players")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{name.lower()}.json")
    character = None
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            char_data = json.load(f)
        character = Character.from_dict(char_data)
        # Assign room object
        room_vnum = char_data.get("room_vnum", 1000)
        character.room = world.rooms.get(room_vnum, start_room)
    else:
        username, hashed_password = await prompt_username_password(writer, reader)
        races = character_creation_prompt(writer)
        race_choice_data = await reader.read(10)
        try:
            race_choice = int(race_choice_data.decode().strip())
            if 1 <= race_choice <= len(races):
                chosen_race = races[race_choice-1][0]
            else:
                chosen_race = "Hasura Elf"
        except Exception:
            chosen_race = "Hasura Elf"
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
        skills = await prompt_skills(writer, reader, chosen_class)
        spells = await prompt_spells(writer, reader, chosen_class)
        # Prompt for alignment and deity
        alignment = await prompt_alignment(writer, reader)
        deity = await prompt_deity(writer, reader)
        # Use a temp Character to filter eligible feats
        temp_char = Character(username, None, chosen_race, 1, 10, 10, 10, start_room, char_class=chosen_class, skills=skills, spells_known=spells, alignment=alignment, deity=deity)
        feats = await prompt_feats(writer, reader, character=temp_char)
        # Confirm character summary
        equipment = get_starting_equipment(chosen_class)
        summary = f"Name: {username}\nRace: {chosen_race}\nClass: {chosen_class}\nAlignment: {alignment}\nDeity: {deity}\nSkills: {skills}\nSpells: {spells}\nFeats: {feats}\nEquipment: {equipment}"
        if not await confirm_character(writer, reader, summary):
            writer.write(b"Restarting character creation...\n")
            return await handle_client(reader, writer, world, parser)
        # Create new character
        character = Character(username, None, chosen_race, 1, 10, 10, 10, start_room, char_class=chosen_class, skills=skills, spells_known=spells, feats=feats, alignment=alignment, deity=deity)
        character.hashed_password = hashed_password
    # Special case: Dagdan (immortal/AI)
    if name.lower() == "dagdan":
        writer.write(b"Enter password: ")
        password_data = await reader.read(100)
        password = password_data.decode().strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        expected_hash = hashlib.sha256("Purple#5186".encode()).hexdigest()
        if hashed_password != expected_hash:
            logger.warning(f"Invalid password attempt for {name}")
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
    # AI player setup (if needed)
    if hasattr(character, 'is_ai') and character.is_ai:
        # AI should have valid alignment and deity
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

        if character.is_ai:
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
    writer.write(b"Enter username: ")
    username = (await reader.read(100)).decode().strip()
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
    skill_points = CLASSES[chosen_class]["skill_points"] + 4  # 1st level bonus
    skills = {s: 0 for s in class_skills}
    writer.write(f"\nYou have {skill_points} skill points to spend.\n".encode())
    for s in class_skills:
        writer.write(f"{s}: ".encode())
        val = (await reader.read(10)).decode().strip()
        try:
            v = int(val)
        except Exception:
            v = 0
        skills[s] = v
    if sum(skills.values()) > skill_points:
        writer.write(b"You spent too many points. Try again.\n")
        return await prompt_skills(writer, reader, chosen_class)
    return skills

async def prompt_spells(writer, reader, chosen_class):
    # Only for spellcasters
    spell_list = [s for s in SPELLS if chosen_class in s["level"] and s["level"][chosen_class] == 1]
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
        writer.write(f"  {i}. {d}\n".encode())
    writer.write(b"Enter choice: ")
    data = await reader.read(10)
    try:
        idx = int(data.decode().strip())
        if 1 <= idx <= len(DEITIES):
            return DEITIES[idx-1]
    except Exception:
        pass
    return DEITIES[0]


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


async def confirm_character(writer, reader, summary):
    writer.write(b"\nCharacter Summary:\n")
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
    
    ai_character = Character("Aelthara", None, "Eruskan Human", 7, 60, 120, 16, world.rooms[1000],
                            str_score=12, dex_score=14, con_score=12, int_score=14, wis_score=12, cha_score=16,
                            mana=100, max_mana=100, move=100, max_move=100)
    ai_character.is_ai = True
    ai_character.quests.append(world.quests[1])
    world.players.append(ai_character)
    world.rooms[1000].players.append(ai_character)
    
    logger.info("Starting Oreka MUD server on localhost:4000")
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, world, parser), "localhost", 4000
    )
    asyncio.create_task(log_players(world))
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
