import asyncio

# Global session tracking for all connected users
ACTIVE_SESSIONS = {}  # username: (writer, last_activity)
import telnetlib3
import time
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
from src.spawning import get_spawn_manager
from src.wandering_gods import get_wandering_gods
from src.mcp_bridge import set_world as mcp_set_world, set_event_loop as mcp_set_loop, start_mcp_bridge_thread


import telnetlib3
import unicodedata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrekaMUD")

# Patch telnetlib3 to use utf-8 encoding for all writers
telnetlib3.server_base.DEFAULT_ENCODING = 'utf-8'

# Utility: Replace all non-ASCII characters with closest ASCII equivalents
def ascii_safe(text):
    if not isinstance(text, str):
        return text
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

# Patch writer.write to always send ASCII-safe output
import types
def wrap_writer(writer):
    orig_write = writer.write
    def safe_write(s):
        return orig_write(ascii_safe(s))
    writer.write = safe_write
    return writer


# Structured deity data for Elemental Lords and Ascended Gods
DEITIES = [
    {
        "name": "Dagdan, The United Sun",
        "type": "Ascended God",
        "alignment": "Lawful Good",
        "domains": ["Good", "Strength", "Magic"],
        "lore": "The immortal champion who united the tribes and brought the light of knowledge and strength to all peoples.",
    },
    # Elemental Lords (examples, you can expand)
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
    # Ascended Gods
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
    # Atheist/None
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
    "Barbarian":  ["Greataxe", "Handaxe", "Javelin", "Javelin", "Javelin", "Javelin", "Hide Armor", "Explorer's Pack", "Waterskin", "Rations", "Rations"],
    "Bard":       ["Rapier", "Leather Armor", "Lute", "Dagger", "Entertainer's Pack", "Waterskin", "Rations", "Rations"],
    "Cleric":     ["Mace", "Scale Mail", "Heavy Wooden Shield", "Holy Symbol", "Healer's Kit", "Waterskin", "Rations", "Rations"],
    "Druid":      ["Scimitar", "Leather Armor", "Heavy Wooden Shield", "Holly and Mistletoe", "Explorer's Pack", "Waterskin", "Rations", "Rations"],
    "Fighter":    ["Longsword", "Heavy Wooden Shield", "Chain Shirt", "Longbow", "Quiver of Arrows", "Dagger", "Adventurer's Pack", "Waterskin", "Rations", "Rations"],
    "Monk":       ["Quarterstaff", "Sling", "Sling Bullets", "Explorer's Pack", "Waterskin", "Rations", "Rations"],
    "Paladin":    ["Longsword", "Heavy Wooden Shield", "Scale Mail", "Holy Symbol", "Adventurer's Pack", "Waterskin", "Rations", "Rations"],
    "Ranger":     ["Longbow", "Quiver of Arrows", "Short Sword", "Short Sword", "Studded Leather Armor", "Explorer's Pack", "Waterskin", "Rations", "Rations"],
    "Rogue":      ["Short Sword", "Shortbow", "Quiver of Arrows", "Leather Armor", "Thieves' Tools", "Dagger", "Dagger", "Adventurer's Pack", "Waterskin", "Rations", "Rations"],
    "Wizard":     ["Quarterstaff", "Dagger", "Spellbook", "Component Pouch", "Scholar's Pack", "Waterskin", "Rations", "Rations"],
    "Sorcerer":   ["Light Crossbow", "Bolts", "Dagger", "Dagger", "Component Pouch", "Explorer's Pack", "Waterskin", "Rations", "Rations"],
    "Magi":       ["Quarterstaff", "Dagger", "Spellbook", "Component Pouch", "Scholar's Pack", "Waterskin", "Rations", "Rations"],
}


# Item templates for starting equipment (proper Item dicts for serialization)
ITEM_TEMPLATES = {
    "Longsword":        {"vnum": 50001, "name": "Longsword", "item_type": "weapon", "weight": 4, "value": 15, "damage": [1,8,0], "material": "steel", "slot": "main_hand", "description": "A sturdy steel longsword."},
    "Short Sword":      {"vnum": 50002, "name": "Short Sword", "item_type": "weapon", "weight": 2, "value": 10, "damage": [1,6,0], "material": "steel", "slot": "main_hand", "description": "A light steel short sword."},
    "Greataxe":         {"vnum": 50003, "name": "Greataxe", "item_type": "weapon", "weight": 12, "value": 20, "damage": [1,12,0], "material": "steel", "slot": "main_hand", "description": "A heavy greataxe."},
    "Handaxe":          {"vnum": 50004, "name": "Handaxe", "item_type": "weapon", "weight": 3, "value": 6, "damage": [1,6,0], "material": "steel", "slot": "main_hand", "description": "A small handaxe."},
    "Mace":             {"vnum": 50005, "name": "Mace", "item_type": "weapon", "weight": 8, "value": 12, "damage": [1,8,0], "material": "steel", "slot": "main_hand", "description": "A heavy steel mace."},
    "Rapier":           {"vnum": 50006, "name": "Rapier", "item_type": "weapon", "weight": 2, "value": 20, "damage": [1,6,0], "material": "steel", "slot": "main_hand", "description": "An elegant thrusting sword."},
    "Scimitar":         {"vnum": 50007, "name": "Scimitar", "item_type": "weapon", "weight": 4, "value": 15, "damage": [1,6,0], "material": "steel", "slot": "main_hand", "description": "A curved slashing blade."},
    "Quarterstaff":     {"vnum": 50008, "name": "Quarterstaff", "item_type": "weapon", "weight": 4, "value": 0, "damage": [1,6,0], "material": "wood", "slot": "main_hand", "description": "A simple wooden staff."},
    "Dagger":           {"vnum": 50009, "name": "Dagger", "item_type": "weapon", "weight": 1, "value": 2, "damage": [1,4,0], "material": "steel", "slot": "main_hand", "description": "A small steel dagger."},
    "Longbow":          {"vnum": 50010, "name": "Longbow", "item_type": "weapon", "weight": 3, "value": 75, "damage": [1,8,0], "material": "wood", "slot": "main_hand", "description": "A tall wooden longbow."},
    "Shortbow":         {"vnum": 50011, "name": "Shortbow", "item_type": "weapon", "weight": 2, "value": 30, "damage": [1,6,0], "material": "wood", "slot": "main_hand", "description": "A compact shortbow."},
    "Light Crossbow":   {"vnum": 50012, "name": "Light Crossbow", "item_type": "weapon", "weight": 4, "value": 35, "damage": [1,8,0], "material": "wood", "slot": "main_hand", "description": "A light crossbow."},
    "Sling":            {"vnum": 50013, "name": "Sling", "item_type": "weapon", "weight": 0, "value": 0, "damage": [1,4,0], "material": "leather", "slot": "main_hand", "description": "A simple leather sling."},
    "Javelin":          {"vnum": 50014, "name": "Javelin", "item_type": "weapon", "weight": 2, "value": 1, "damage": [1,6,0], "material": "wood", "description": "A throwing javelin."},
    "Chain Shirt":      {"vnum": 50020, "name": "Chain Shirt", "item_type": "armor", "weight": 25, "value": 100, "ac_bonus": 4, "material": "steel", "slot": "body", "description": "A shirt of interlocking steel rings."},
    "Leather Armor":    {"vnum": 50021, "name": "Leather Armor", "item_type": "armor", "weight": 15, "value": 10, "ac_bonus": 2, "material": "leather", "slot": "body", "description": "Cured leather armor."},
    "Studded Leather Armor": {"vnum": 50022, "name": "Studded Leather Armor", "item_type": "armor", "weight": 20, "value": 25, "ac_bonus": 3, "material": "leather", "slot": "body", "description": "Leather armor reinforced with metal studs."},
    "Hide Armor":       {"vnum": 50023, "name": "Hide Armor", "item_type": "armor", "weight": 25, "value": 15, "ac_bonus": 3, "material": "leather", "slot": "body", "description": "Armor made from thick animal hides."},
    "Scale Mail":       {"vnum": 50024, "name": "Scale Mail", "item_type": "armor", "weight": 30, "value": 50, "ac_bonus": 4, "material": "steel", "slot": "body", "description": "Armor of overlapping metal scales."},
    "Heavy Wooden Shield": {"vnum": 50030, "name": "Heavy Wooden Shield", "item_type": "shield", "weight": 10, "value": 7, "ac_bonus": 2, "material": "wood", "slot": "off_hand", "description": "A large wooden shield."},
    "Quiver of Arrows": {"vnum": 50040, "name": "Quiver of Arrows", "item_type": "ammunition", "weight": 3, "value": 1, "description": "A quiver with 20 arrows."},
    "Bolts":            {"vnum": 50041, "name": "Crossbow Bolts", "item_type": "ammunition", "weight": 1, "value": 1, "description": "A case of 20 crossbow bolts."},
    "Sling Bullets":    {"vnum": 50042, "name": "Sling Bullets", "item_type": "ammunition", "weight": 5, "value": 0, "description": "A pouch of 10 sling bullets."},
    "Adventurer's Pack": {"vnum": 50050, "name": "Adventurer's Pack", "item_type": "container", "weight": 5, "value": 15, "description": "Backpack, bedroll, flint & steel, torches, 50ft rope."},
    "Explorer's Pack":  {"vnum": 50051, "name": "Explorer's Pack", "item_type": "container", "weight": 5, "value": 10, "description": "Backpack, bedroll, torches, rations, waterskin."},
    "Scholar's Pack":   {"vnum": 50052, "name": "Scholar's Pack", "item_type": "container", "weight": 5, "value": 15, "description": "Backpack, ink, parchment, candles, small knife."},
    "Entertainer's Pack": {"vnum": 50053, "name": "Entertainer's Pack", "item_type": "container", "weight": 4, "value": 15, "description": "Backpack, costumes, candles, waterskin, rations."},
    "Waterskin":        {"vnum": 50060, "name": "Waterskin", "item_type": "drink", "weight": 4, "value": 1, "description": "A leather waterskin filled with water."},
    "Rations":          {"vnum": 50061, "name": "Trail Rations", "item_type": "food", "weight": 1, "value": 0.5, "description": "A day's worth of dried food."},
    "Thieves' Tools":   {"vnum": 50070, "name": "Thieves' Tools", "item_type": "tools", "weight": 1, "value": 30, "description": "Lockpicks, files, and a small mirror."},
    "Healer's Kit":     {"vnum": 50071, "name": "Healer's Kit", "item_type": "tools", "weight": 1, "value": 50, "description": "Bandages, salves, and splinting materials. 10 uses."},
    "Holy Symbol":      {"vnum": 50072, "name": "Holy Symbol", "item_type": "focus", "weight": 0, "value": 25, "description": "A silver holy symbol of your deity."},
    "Holly and Mistletoe": {"vnum": 50073, "name": "Holly and Mistletoe", "item_type": "focus", "weight": 0, "value": 0, "description": "A druidic focus of sacred plants."},
    "Spellbook":        {"vnum": 50074, "name": "Spellbook", "item_type": "focus", "weight": 3, "value": 15, "description": "A leather-bound book with blank pages for recording spells."},
    "Component Pouch":  {"vnum": 50075, "name": "Component Pouch", "item_type": "focus", "weight": 2, "value": 5, "description": "A belt pouch filled with spell components."},
    "Lute":             {"vnum": 50076, "name": "Lute", "item_type": "instrument", "weight": 3, "value": 5, "description": "A wooden lute, well-tuned."},
}

def make_starting_items(equipment_names):
    """Convert equipment name list to list of Item dicts for serialization."""
    items = []
    vnum_counter = 60000  # unique vnums for dupes
    for name in equipment_names:
        template = ITEM_TEMPLATES.get(name)
        if template:
            item = dict(template)
            item["vnum"] = vnum_counter
            vnum_counter += 1
            items.append(item)
        else:
            # Generic item for anything not in templates
            items.append({"vnum": vnum_counter, "name": name, "item_type": "misc", "weight": 1, "value": 0, "description": name})
            vnum_counter += 1
    return items


async def handle_client(reader, writer, world, parser):
    logger.info("New client connected")
    # Only wrap if it's a telnetlib3 writer (legacy), skip for our TelnetWriter
    if not isinstance(writer, object) or not hasattr(writer, '_writer'):
        writer = wrap_writer(writer)
    character = None
    # Display MOTD
    try:
        import os as _os
        _motd_path = _os.path.join(_os.path.dirname(__file__), 'data', 'motd.txt')
        with open(_motd_path, 'r', encoding='utf-8') as _f:
            writer.write(_f.read() + "\n")
    except Exception:
        writer.write("Welcome to Oreka MUD!\n")
    if hasattr(writer, 'drain'):
        await writer.drain()
    import hashlib
    import os
    global ACTIVE_SESSIONS
    if "ACTIVE_SESSIONS" not in globals():
        ACTIVE_SESSIONS = {}  # username: (writer, last_activity)

    # Main login/creation loop
    while True:
        writer.write("Do you have an existing character? (y/n): ")
        if hasattr(writer, 'drain'):
            await writer.drain()
        resp = (await reader.readline()).strip().lower()
        if not resp:
            continue
        if resp == "y":
            writer.write("Enter your character name: ")
            username = (await reader.readline()).strip()
            if not username:
                writer.write("No username entered. Try again.\n")
                continue
            if len(username) > 20 or len(username) < 2 or not username.replace('_', '').replace('-', '').isalnum():
                writer.write("Invalid name. Use 2-20 alphanumeric characters.\n")
                continue
            # Duplicate login handling
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
            password = (await reader.readline()).strip()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            # Special case: Dagdan
            if username.lower() == "dagdan":
                expected_hash = hashlib.sha256("Nero123".encode()).hexdigest()
                if hashed_password != expected_hash:
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
                # ...proceed to Dagdan game loop...
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
            # Special case: Hareem
            elif username.lower() == "hareem":
                expected_hash = hashlib.sha256("Nero123".encode()).hexdigest()
                if hashed_password != expected_hash:
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
                # ...proceed to Hareem game loop...
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
                    # mana removed
                    # max_mana removed
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
            # All other characters: check player file
            else:
                player_path = os.path.join(os.path.dirname(__file__), "data", "players", f"{username.lower()}.json")
                import json
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
                expected_hash = pdata.get("hashed_password")
                if not expected_hash or hashed_password != expected_hash:
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
                # Load character using from_dict (handles all fields including inventory, equipment, etc.)
                character = Character.from_dict(pdata, world=world)
                character.room = world.rooms.get(pdata.get("room_vnum", 1000), world.rooms[1000])
                break
        elif resp == "n":
            # New character creation flow
            writer.write("Enter your desired character name (3-20 letters): ")
            username = (await reader.readline()).strip()
            if not username or len(username) < 3:
                writer.write("Name must be at least 3 characters. Try again.\n")
                continue
            if len(username) > 20:
                writer.write("Name must be 20 characters or less. Try again.\n")
                continue
            if not username.isalpha():
                writer.write("Name must contain only letters. Try again.\n")
                continue
            username = username.capitalize()
            # Check if name already taken
            player_path_check = os.path.join(os.path.dirname(__file__), "data", "players", f"{username.lower()}.json")
            if os.path.exists(player_path_check):
                writer.write(f"The name '{username}' is already taken. Try again.\n")
                continue
            # Password prompt
            writer.write("Enter password: ")
            password = (await reader.readline()).strip()
            if not password or len(password) < 4:
                writer.write("Password must be at least 4 characters. Try again.\n")
                continue
            writer.write("Confirm password: ")
            confirm = (await reader.readline()).strip()
            if password != confirm:
                writer.write("Passwords do not match. Try again.\n")
                continue
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            # Race
            races = character_creation_prompt(writer)
            race_choice = (await reader.read(100)).strip()
            chosen_race = None
            # Try number first
            try:
                race_idx = int(race_choice) - 1
                if 0 <= race_idx < len(races):
                    chosen_race = races[race_idx][0]
            except ValueError:
                pass
            # Try text match (case-insensitive, partial)
            if not chosen_race and race_choice:
                query = race_choice.lower()
                for rname, _ in races:
                    if query in rname.lower():
                        chosen_race = rname
                        break
            # If still nothing, ask again
            while not chosen_race:
                writer.write(f"'{race_choice}' not recognized. Enter a number (1-{len(races)}) or race name: ")
                race_choice = (await reader.read(100)).strip()
                try:
                    race_idx = int(race_choice) - 1
                    if 0 <= race_idx < len(races):
                        chosen_race = races[race_idx][0]
                except ValueError:
                    pass
                if not chosen_race and race_choice:
                    query = race_choice.lower()
                    for rname, _ in races:
                        if query in rname.lower():
                            chosen_race = rname
                            break
            # Roll stats (simple 4d6 drop lowest, 6 times)
            import random
            def roll_stat():
                rolls = sorted([random.randint(1,6) for _ in range(4)], reverse=True)
                return sum(rolls[:3])
            stats = [roll_stat() for _ in range(6)]
            stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
            stat_dict = dict(zip(stat_names, stats))
            # Apply racial stat mods
            from src.races import get_race
            _race_data = get_race(chosen_race)
            if _race_data:
                _ability_mods = _race_data.get('ability_mods', {})
                if _ability_mods:
                    _mod_parts = []
                    for _stat_abbr, _mod_val in _ability_mods.items():
                        _full_name = {"Str": "STR", "Dex": "DEX", "Con": "CON", "Int": "INT", "Wis": "WIS", "Cha": "CHA"}.get(_stat_abbr, _stat_abbr.upper())
                        if _full_name in stat_dict:
                            stat_dict[_full_name] += _mod_val
                            _mod_parts.append(f"{_full_name} {_mod_val:+d}")
                    if _mod_parts:
                        writer.write(f"Racial modifiers ({chosen_race}): {', '.join(_mod_parts)}\n")
                # Set move/max_move from racial speed
                _racial_speed = _race_data.get('speed', 30)
                _racial_move = (_racial_speed * 10) // 3
            else:
                _racial_move = 100
            writer.write(f"Rolled stats: {', '.join(f'{n}: {v}' for n,v in stat_dict.items())}\n")
            # Class
            chosen_class = await prompt_class(writer, reader)
            # Magi chosen path selection
            chosen_path = None
            if chosen_class == "Magi":
                writer.write("\nChoose your Magi Path:\n")
                writer.write("  1. Seer - Divination & foresight (+2 Spellcraft, +2 Knowledge(arcana))\n")
                writer.write("  2. Keeper - Knowledge & preservation (+2 Concentration, +2 Knowledge(history))\n")
                writer.write("  3. Voice - Communication & charm (+2 Diplomacy, +2 Perform(any))\n")
                writer.write("Enter choice: ")
                _path_choice = (await reader.read(10)).strip()
                _paths = {"1": "Seer", "2": "Keeper", "3": "Voice"}
                chosen_path = _paths.get(_path_choice, "Seer")
                writer.write(f"You have chosen the path of the {chosen_path}.\n")
            # Skills
            skills = await prompt_skills(writer, reader, chosen_class)
            # Apply Magi path skill bonuses
            if chosen_path == "Seer":
                skills["Spellcraft"] = skills.get("Spellcraft", 0) + 2
                skills["Knowledge (arcana)"] = skills.get("Knowledge (arcana)", 0) + 2
            elif chosen_path == "Keeper":
                skills["Concentration"] = skills.get("Concentration", 0) + 2
                skills["Knowledge (history)"] = skills.get("Knowledge (history)", 0) + 2
            elif chosen_path == "Voice":
                skills["Diplomacy"] = skills.get("Diplomacy", 0) + 2
                skills["Perform (any)"] = skills.get("Perform (any)", 0) + 2
            # Deity (pick FIRST — determines domains for Clerics)
            deity = await prompt_deity(writer, reader)
            # Alignment
            alignment = await prompt_alignment(writer, reader)
            # Domains (if Cleric — filtered by deity's domains)
            domains = []
            if chosen_class == "Cleric":
                from src.spells import DOMAIN_DATA
                # Get deity's allowed domains from deities.json
                deity_domains = []
                try:
                    from src.religion import get_religion_manager
                    rm = get_religion_manager()
                    did, ddata = rm.find_deity(deity)
                    if ddata:
                        deity_domains = ddata.get("domains", [])
                except Exception:
                    pass
                # If deity has specific domains, only show those. Otherwise show all.
                if deity_domains:
                    available_domains = [d for d in deity_domains if d in DOMAIN_DATA]
                    if len(available_domains) < 2:
                        # Deity has fewer than 2 recognized domains — supplement with all
                        available_domains = list(DOMAIN_DATA.keys())
                else:
                    available_domains = list(DOMAIN_DATA.keys())
                writer.write(f"\nYour deity {deity} grants access to these domains:\n")
                writer.write("Choose your first domain:\n")
                for i, d in enumerate(available_domains, 1):
                    writer.write(f"  {i}. {d} - {DOMAIN_DATA[d]['power']}\n")
                writer.write("Enter choice: ")
                first_choice = (await reader.readline()).strip()
                try:
                    idx = int(first_choice) - 1
                    first_domain = available_domains[idx] if 0 <= idx < len(available_domains) else available_domains[0]
                except Exception:
                    # Try text match
                    first_domain = available_domains[0]
                    for d in available_domains:
                        if first_choice.lower() in d.lower():
                            first_domain = d
                            break
                domains.append(first_domain)
                remaining = [d for d in available_domains if d != first_domain]
                writer.write(f"\nChosen: {first_domain}. Now choose your second domain:\n")
                for i, d in enumerate(remaining, 1):
                    writer.write(f"  {i}. {d} - {DOMAIN_DATA[d]['power']}\n")
                writer.write("Enter choice: ")
                second_choice = (await reader.readline()).strip()
                try:
                    idx = int(second_choice) - 1
                    second_domain = remaining[idx] if 0 <= idx < len(remaining) else remaining[0]
                except Exception:
                    second_domain = remaining[0]
                    for d in remaining:
                        if second_choice.lower() in d.lower():
                            second_domain = d
                            break
                domains.append(second_domain)
                writer.write(f"Domains chosen: {', '.join(domains)}\n")
            # Spells
            spells = await prompt_spells(writer, reader, chosen_class, domains)
            # Feats
            temp_char = Character(
                username, None, chosen_race, 1, 10, 10, 10, world.rooms[1000],
                char_class=chosen_class, skills=skills, spells_known=spells,
                alignment=alignment, deity=deity, domains=domains,
                str_score=stat_dict["STR"], dex_score=stat_dict["DEX"], con_score=stat_dict["CON"],
                int_score=stat_dict["INT"], wis_score=stat_dict["WIS"], cha_score=stat_dict["CHA"]
            )
            feats = await prompt_feats(writer, reader, character=temp_char)
            # Equipment
            equipment = get_starting_equipment(chosen_class)
            # Summary
            summary = build_character_sheet(
                username, chosen_race, chosen_class, alignment, deity, domains,
                skills, spells, feats, equipment, stats=stat_dict
            )
            if not await confirm_character(writer, reader, summary):
                writer.write("Restarting character creation...\n")
                continue
            # Save new character to file
            import json
            player_path = os.path.join(os.path.dirname(__file__), "data", "players", f"{username.lower()}.json")
            pdata = {
                "name": username,
                "title": None,
                "race": chosen_race,
                "level": 1,
                "char_class": chosen_class,
                "class_level": 1,
                "class_features": [],
                "spells_known": spells,
                "spells_per_day": {},
                "hp": 10,
                "max_hp": 10,
                "ac": 10,
                "room_vnum": 1000,
                "quests": [],
                "state": "EXPLORING",
                "is_ai": False,
                "is_immortal": False,
                "elemental_affinity": _race_data.get('elemental_affinity') if _race_data else None,
                "str_score": stat_dict["STR"],
                "dex_score": stat_dict["DEX"],
                "con_score": stat_dict["CON"],
                "int_score": stat_dict["INT"],
                "wis_score": stat_dict["WIS"],
                "cha_score": stat_dict["CHA"],
                "move": _racial_move,
                "max_move": _racial_move,
                "xp": 0,
                "show_all": False,
                "inventory": make_starting_items(equipment),
                "gold": {"Fighter": 150, "Barbarian": 80, "Rogue": 140, "Bard": 120, "Cleric": 100, "Druid": 60, "Monk": 20, "Paladin": 120, "Ranger": 100, "Wizard": 80, "Sorcerer": 80, "Magi": 80}.get(chosen_class, 100),
                "alignment": alignment,
                "deity": deity,
                "domains": domains,
                "hashed_password": hashed_password,
                "skills": skills,
                "feats": feats,
                "chosen_path": chosen_path,
            }
            with open(player_path, "w", encoding="utf-8") as f:
                json.dump(pdata, f, indent=2)
            # Actually create the character object
            # Calculate L1 HP: max hit die + con mod
            _hit_die = int(str(CLASSES.get(chosen_class, {}).get('hit_die', 8)).replace('d',''))
            _con_mod = (stat_dict["CON"] - 10) // 2
            _start_hp = max(1, _hit_die + _con_mod)
            character = Character(
                name=username,
                title=None,
                race=chosen_race,
                level=1,
                hp=_start_hp,
                max_hp=_start_hp,
                ac=10,
                room=world.rooms[1000],
                is_immortal=False,
                elemental_affinity=_race_data.get('elemental_affinity') if _race_data else None,
                str_score=stat_dict["STR"],
                dex_score=stat_dict["DEX"],
                con_score=stat_dict["CON"],
                int_score=stat_dict["INT"],
                wis_score=stat_dict["WIS"],
                cha_score=stat_dict["CHA"],
                move=_racial_move,
                max_move=_racial_move,
                alignment=alignment,
                deity=deity,
                feats=feats,
                domains=domains,
                char_class=chosen_class,
                skills=skills,
                spells_known=spells,
            )
            character.is_ai = False
            character.chosen_path = chosen_path
            # Give starting equipment and gold
            from src.items import Item
            for item_dict in make_starting_items(equipment):
                try:
                    item = Item(**item_dict)
                    character.inventory.append(item)
                except Exception:
                    pass
            starting_gold = {"Fighter": 150, "Barbarian": 80, "Rogue": 140, "Bard": 120, "Cleric": 100, "Druid": 60, "Monk": 20, "Paladin": 120, "Ranger": 100, "Wizard": 80, "Sorcerer": 80, "Magi": 80}.get(chosen_class, 100)
            character.gold = starting_gold
            break
        else:
            writer.write("Please enter 'y' or 'n'.\n")
            continue

    # If character is not set, abort
    if character is None:
        writer.write("Login or character creation failed. Connection closed.\n")
        writer.close()
        return
    # ...existing code continues here...
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
            username,
            None,
            chosen_race,
            1,
            10,
            10,
            10,
            start_room,
            char_class=chosen_class,
            skills=skills,
            spells_known=spells_by_level,
            feats=feats,
            alignment=alignment,
            deity=deity,
            domains=domains,
            str_score=str_score,
            dex_score=dex_score,
            con_score=con_score,
            int_score=int_score,
            wis_score=wis_score,
            cha_score=cha_score,
        )
        character.hashed_password = hashed_password

    # Special case: Dagdan (immortal/AI)
    if username.lower() == "dagdan":
        writer.write(b"Enter password: ")
        password_data = await reader.read(100)
        password = password_data.strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        expected_hash = hashlib.sha256("Nero123".encode()).hexdigest()
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
            move=150,
            max_move=150,
            alignment="Lawful Good",
            deity="Aureon (Sun, Law, Knowledge)",
        )
        character.is_ai = False

    # Special case: Hareem (immortal)
    elif username.lower() == "hareem":
        writer.write(b"Enter password: ")
        password_data = await reader.read(100)
        password = password_data.strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        expected_hash = hashlib.sha256("Nero123".encode()).hexdigest()
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
            # mana removed
            # max_mana removed
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

    # AI player setup (if needed)
    if hasattr(character, "is_ai") and character.is_ai:
        if not getattr(character, "alignment", None):
            character.alignment = "True Neutral"
        if not getattr(character, "deity", None):
            character.deity = "None/Atheist"

    # Store writer/reader for async commands (like levelup Bonus Feat prompt)
    character.writer = writer
    character.reader = reader
    world.players.append(character)
    world.players_by_name[character.name.lower()] = character
    character.room.players.append(character)
    # Do not announce Dagdan on startup
    if character.name.lower() != "dagdan":
        logger.info(f"Character {character.name} logged in")

    # ANSI color codes
    RED_BOLD = "\033[1;31m"
    WHITE = "\033[37m"
    CYAN = "\033[1;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    DIM = "\033[0;90m"
    RESET = "\033[0m"

    def format_room_output(room, look_result, exits, prompt, add_space=False):
        space = "\n" if add_space else ""
        # cmd_look now includes the room name as a heading, so just pass through
        result = f"{space}{WHITE}{look_result}{RESET}\n"
        result += f"\n{prompt}"
        return result

    # Register GMCP handler for this connection
    try:
        from src.gmcp import register_handler as gmcp_register
        gmcp_handler = gmcp_register(character, writer)
        gmcp_handler.emit_vitals(character)
        gmcp_handler.emit_status(character)
        gmcp_handler.emit_room(character.room, character)
    except Exception as e:
        logger.debug(f"GMCP registration: {e}")

    # Log login event
    try:
        from src.event_log import log_event
        log_event(character.name, "login", {"class": getattr(character, 'char_class', '?'), "level": character.level}, room_vnum=character.room.vnum)
    except Exception:
        pass

    # Notify shadow presences in this room that a player logged in
    try:
        from src.shadow_presence import shadow_manager
        shadow_manager.broadcast_event(
            character.room.vnum,
            f"{character.name} has entered the world nearby."
        )
    except Exception:
        pass

    # Initial room display
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
    COMBAT_TICK_RATE = 4  # seconds between auto-attack rounds
    _cmd_times = []  # Rate limiting: timestamps of recent commands
    _CMD_RATE_LIMIT = 8  # max commands per second
    while True:
        try:
            # In combat: use timeout so combat auto-ticks even without input
            from src.character import State as _State
            from src.combat import get_combat as _get_combat
            in_combat = (character.state == _State.COMBAT
                         and _get_combat(character.room)
                         and _get_combat(character.room).is_active)
            if in_combat:
                try:
                    data = await asyncio.wait_for(reader.readline(), timeout=COMBAT_TICK_RATE)
                except asyncio.TimeoutError:
                    # No input — auto-tick combat
                    combat = _get_combat(character.room)
                    if combat and combat.is_active:
                        combat_messages = []
                        should_end, end_msg = combat.check_combat_end()
                        if should_end:
                            combat_messages.append(end_msg)
                            combat.end_combat()
                            character.clear_combat_target()
                            character.state = _State.EXPLORING
                        else:
                            turn_msg = combat.advance_turn()
                            if turn_msg:
                                combat_messages.append(turn_msg)
                            current = combat.get_current_combatant()
                            if current:
                                turn_result = combat.execute_turn(current.combatant, parser)
                                combat_messages.append(turn_result)
                                should_end, end_msg = combat.check_combat_end()
                                if should_end:
                                    combat_messages.append(end_msg)
                                    combat.end_combat()
                                    character.clear_combat_target()
                                    character.state = _State.EXPLORING
                        if combat_messages:
                            writer.write(f"{WHITE}" + "\n".join(combat_messages) + f"\n{character.get_prompt()} {RESET}")
                            await writer.drain()
                    continue
            elif character.state == _State.CHATTING and character.active_chat_session:
                # Chat mode: route input to AI conversation
                _chat_session = character.active_chat_session
                _chat_prompt = f"\033[1;35m[Chat: {_chat_session.npc_name}]\033[0m > "
                try:
                    data = await reader.readline()
                except Exception:
                    break
                if not data:
                    break
                text = data.strip()
                if not text:
                    writer.write(_chat_prompt)
                    await writer.drain()
                    continue
                text_lower = text.lower()
                # Escape commands
                if text_lower in ("endchat", "/quit", "/end", "/exit"):
                    result = parser.cmd_endchat(character, "")
                    writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}")
                    await writer.drain()
                    continue
                if text_lower in ("enter world", "enterworld", "/enter"):
                    result = parser.cmd_enter_world(character, "")
                    writer.write(f"{WHITE}{result}\n{character.get_prompt()} {RESET}")
                    await writer.drain()
                    continue
                # Route to AI chat
                from src.chat_session import process_player_input as _chat_input
                _NPC_COLOR = "\033[0;36m"
                try:
                    response = await _chat_input(_chat_session, character, text)
                    writer.write(f"\n{_NPC_COLOR}{response}{RESET}\n\n{_chat_prompt}")
                except Exception as _chat_err:
                    writer.write(f"\n{_chat_session.npc_name} seems distracted.\n\n{_chat_prompt}")
                await writer.drain()
                continue
            else:
                data = await reader.readline()
            if not data:
                break
            data = data.strip()
            if not data:
                writer.write(f"{character.get_prompt()} ")
                await writer.drain()
                continue

            # Rate limiting — prevent command floods
            _now = time.time()
            _cmd_times = [t for t in _cmd_times if t > _now - 1.0]
            if len(_cmd_times) >= _CMD_RATE_LIMIT:
                writer.write(f"Slow down! ({_CMD_RATE_LIMIT} commands/sec max)\n{character.get_prompt()} ")
                await writer.drain()
                continue
            _cmd_times.append(_now)

            command = data.split(maxsplit=1)
            cmd = command[0].lower()
            args = command[1] if len(command) > 1 else ""

            # Quit / logout
            if cmd in ("quit", "logout"):
                writer.write("\033[1;33mSaving your character...\033[0m\n")
                try:
                    from src.chat import broadcast_to_room
                    broadcast_to_room(character.room, f"{character.name} has left the world.", exclude=character)
                except Exception:
                    pass
                try:
                    from src.gmcp import unregister_handler as gmcp_unreg
                    gmcp_unreg(character)
                except Exception:
                    pass
                try:
                    from src.event_log import log_event
                    log_event(character.name, "logout", {}, room_vnum=character.room.vnum)
                except Exception:
                    pass
                writer.write("\033[1;33mFarewell, adventurer. Until next time.\033[0m\n")
                await writer.drain()
                break

            # Alias expansion
            if hasattr(character, 'aliases') and cmd in getattr(character, 'aliases', {}):
                _expanded = character.aliases[cmd]
                if args:
                    _expanded = _expanded + " " + args
                _parts = _expanded.strip().split(maxsplit=1)
                cmd = _parts[0].lower()
                args = _parts[1] if len(_parts) > 1 else ""

            # Speedwalk detection (e.g., "nnnwws") — exclude diagonal shortcuts
            _dir_chars = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'u': 'up', 'd': 'down'}
            _diagonal_shortcuts = {"ne", "nw", "se", "sw"}
            if len(cmd) > 1 and cmd not in _diagonal_shortcuts and all(c in _dir_chars for c in cmd) and cmd not in parser.commands:
                _sw_results = []
                for _ch in cmd:
                    _dir = _dir_chars[_ch]
                    _res = parser.cmd_move(character, _dir)
                    if "no exit" in _res.lower() or "closed" in _res.lower() or "locked" in _res.lower() or "cannot" in _res.lower():
                        _sw_results.append(f"Stopped: {_res}")
                        break
                    _sw_results.append(f"You move {_dir} to {character.room.name}.")
                writer.write(f"{WHITE}" + "\n".join(_sw_results) + f"\n{character.get_prompt()} {RESET}")
                await writer.drain()
                continue

            add_space = False
            prev_room_vnum = character.room.vnum

            # Check if cmd is a room exit direction (for special exits like "in", "guild", "northeast")
            is_room_exit = hasattr(character, 'room') and character.room and cmd in character.room.exits

            # Prefix matching: if cmd isn't an exact match, find commands that start with it
            resolved_cmd = cmd
            if cmd not in parser.commands and len(cmd) >= 2 and not is_room_exit:
                matches = [c for c in parser.commands if c.startswith(cmd)]
                if len(matches) == 1:
                    resolved_cmd = matches[0]
                elif len(matches) > 1 and len(matches) <= 5:
                    writer.write(
                        f"{WHITE}Did you mean: {', '.join(sorted(matches))}?\n"
                        f"{character.get_prompt()} {RESET}"
                    )
                    await writer.drain()
                    continue

            if resolved_cmd in parser.commands and not is_room_exit:
                result = parser.commands[resolved_cmd](character, args)
                # Handle async commands
                if asyncio.iscoroutine(result):
                    result = await result
                if result is None:
                    result = ""
                if resolved_cmd in ("look", "l"):
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
            elif cmd in ["north", "south", "east", "west", "up", "down", "n", "s", "e", "w", "u", "d",
                         "northeast", "northwest", "southeast", "southwest", "ne", "nw", "se", "sw"] or is_room_exit:
                # Map shortcuts to full direction names
                direction_map = {"n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down",
                                 "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest"}
                direction = direction_map.get(cmd, cmd)
                result = parser.cmd_move(character, direction)
                if result is None:
                    result = ""
                # Check if room changed — cmd_move already includes look output
                add_space = character.room.vnum != prev_room_vnum
                if add_space:
                    writer.write(
                        format_room_output(
                            character.room,
                            result,
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

            # GMCP: emit vitals after every command
            try:
                from src.gmcp import get_handler as gmcp_get
                gh = gmcp_get(character)
                if gh:
                    gh.emit_vitals(character)
                    gh.emit_inventory(character)
                    # Emit room on movement
                    if character.room.vnum != prev_room_vnum:
                        gh.emit_room(character.room, character)
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Error processing command: {e}")
            import traceback
            traceback.print_exc()
            try:
                writer.write(f"\n[Error: {e}]\n{character.get_prompt()} ")
                await writer.drain()
            except Exception:
                break

        # Combat auto-advance is handled by the timeout loop above

        if getattr(character, "is_ai", False):
            ai_result = await character.ai_decide(world)
            # Check if room changed for AI
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

    # Save character on disconnect
    world.players.remove(character)
    world.players_by_name.pop(character.name.lower(), None)
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
        ("Hasura Elf", "Treetop artisans and scholars of the canopy cities. Wind-attuned."),
        ("Kovaka Elf", "Stonebound warriors and mountain wardens. Wind-attuned."),
        ("Pasua Elf", "Storytellers and diplomats, charm in every word. Wind-attuned."),
        ("Na'wasua Elf", "Stargazing mystics of twilight and divination. Wind-attuned."),
        ("Visetri Dwarf", "Traditional stone-workers and builders. Earth-attuned."),
        ("Pekakarlik Dwarf", "River engineers and watercraft masters. Water-attuned."),
        ("Rarozhki Dwarf", "Volcanic-forge masters, embersteel smiths. Fire-attuned."),
        ("Halfling", "Water-touched wanderers, lucky and sure-footed. Water-attuned."),
        ("Orean Human", "Stone-favored founders and keepers. Earth-attuned."),
        ("Taraf-Imro Human", "Fire-bound warriors and smiths. Fire-attuned."),
        ("Eruskan Human", "Seafarers and river traders. Water-attuned."),
        ("Mytroan Human", "Steppe riders and wind-runners. Wind-attuned."),
        ("Half-Giant", "Rare hybrids with Giant essence. All elements."),
        ("Silentborn", "Kin-Domnathar hybrids. Null resonance."),
        ("Farborn Human", "From beyond Oreka. Invisible to Kin-sense."),
    ]
    writer.write("\nChoose your race (type the number):\n")
    for i, (race, desc) in enumerate(races, 1):
        writer.write(f"  {i}. {race} - {desc}\n")
    writer.write("Enter choice: ")
    return races


async def prompt_username_password(writer, reader):
    writer.write("Enter your email: ")
    email = (await reader.read(100)).strip()
    writer.write("Enter your username: ")
    username = (await reader.read(100)).strip()
    writer.write("Enter password: ")
    password = (await reader.read(100)).strip()
    writer.write("Confirm password: ")
    confirm = (await reader.read(100)).strip()
    if password != confirm:
        writer.write("Passwords do not match. Try again.\n")
        return await prompt_username_password(writer, reader)
    import hashlib

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return username, hashed_password


async def prompt_class(writer, reader):
    class_names = list(CLASSES.keys())
    writer.write("\nChoose your class (type the number):\n")
    for i, cname in enumerate(class_names, 1):
        writer.write(f"  {i}. {cname}\n")
    writer.write("Enter choice: ")
    chosen_class = None
    while not chosen_class:
        raw = (await reader.read(100)).strip()
        # Try number
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(class_names):
                chosen_class = class_names[idx]
        except ValueError:
            pass
        # Try text match
        if not chosen_class and raw:
            query = raw.lower()
            for cname in class_names:
                if query in cname.lower():
                    chosen_class = cname
                    break
        if not chosen_class:
            writer.write(f"'{raw}' not recognized. Enter a number or class name: ")
    return chosen_class


async def prompt_skills(writer, reader, chosen_class):
    class_skills = CLASSES[chosen_class]["class_skills"]
    # Build the full skill list (all skills in the game)
    all_skills = set(class_skills)
    for cdata in CLASSES.values():
        all_skills.update(cdata.get("class_skills", []))
    all_skills = sorted(all_skills)
    # For Craft/Profession/Perform, treat each (any) as a group
    def skill_base_name(skill):
        if skill.startswith("Craft ("):
            return "Craft (any)"
        if skill.startswith("Profession ("):
            return "Profession (any)"
        if skill.startswith("Perform ("):
            return "Perform (any)"
        return skill
    # Mark cross-class skills
    cross_class_skills = [s for s in all_skills if skill_base_name(s) not in class_skills]
    # Initialize all skills to 0 for display and allocation
    skills = {s: 0 for s in all_skills}

    # Show all current complete craft skills (from materials.json)
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

    # Add skill rank limit info
    writer.write("Skill Rank Limits:\n")
    writer.write("- Class skills: max rank = character level + 3\n")
    writer.write("- Cross-class skills: max rank = (character level + 3) / 2\n")
    writer.write("- Cross-class skills cost 2 points per rank.\n\n")
    # Get int_score and chosen_race from the call stack (globals in main.py)
    import inspect

    frame = inspect.currentframe().f_back
    int_score = frame.f_locals.get("int_score", 10)
    chosen_race = frame.f_locals.get("chosen_race", "")
    int_mod = (int_score - 10) // 2
    base = CLASSES[chosen_class]["skill_points"]
    skill_points = max((base + int_mod), 1) * 4  # 1st level: base + Int mod, min 1, times 4
    if "Human" in chosen_race:
        skill_points += 4
    spent = 0
    writer.write(f"\nYou have {skill_points} skill points to spend.\n")

    def show_skills():
        # Split into class skills and cross-class, display side by side
        class_list = sorted([s for s in all_skills if skill_base_name(s) in class_skills])
        cross_list = sorted([s for s in all_skills if skill_base_name(s) not in class_skills])
        col_width = 28

        writer.write("\n  CLASS SKILLS (1 pt/rank)          | CROSS-CLASS SKILLS (2 pts/rank)\n")
        writer.write("  " + "-" * 34 + "+" + "-" * 38 + "\n")

        max_rows = max(len(class_list), len(cross_list))
        for i in range(max_rows):
            left = ""
            right = ""
            if i < len(class_list):
                s = class_list[i]
                left = f"  {s}: {skills[s]}"
            if i < len(cross_list):
                s = cross_list[i]
                right = f"  *{s}: {skills[s]}"
            writer.write(f"{left:<35}| {right}\n")

        writer.write(f"  Points remaining: {skill_points - spent}\n")

    show_skills()
    max_rank_class = 1 + 3  # 1st level
    max_rank_cross = (1 + 3) // 2
    # Build case-insensitive lookup for skill names
    skill_lookup = {s.lower(): s for s in all_skills}

    while spent < skill_points:
        writer.write("Type 'add <number> <skill>', 'done' to finish, or 'help <skill>'.\n")
        cmd = (await reader.read(100)).strip()
        if not cmd:
            continue
        if cmd.lower() == "done":
            break
        if cmd.lower().startswith("help "):
            skill_name = cmd[5:].strip()
            writer.write(f"Info about {skill_name}: (description here)\n")
            continue
        if cmd.lower().startswith("add "):
            try:
                parts = cmd.split()
                num = int(parts[1])
                skill_input = " ".join(parts[2:])
                # Case-insensitive skill match
                skill = skill_lookup.get(skill_input.lower())
                if skill is None:
                    # Try partial match
                    matches = [s for key, s in skill_lookup.items() if skill_input.lower() in key]
                    if len(matches) == 1:
                        skill = matches[0]
                    else:
                        writer.write(f"Unknown skill '{skill_input}'.")
                        if matches:
                            writer.write(f" Did you mean: {', '.join(matches[:5])}?")
                        writer.write("\n")
                        continue
                is_cross = skill_base_name(skill) not in class_skills
                # Enforce max rank
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
        if cmd.lower() == "show":
            show_skills()
            continue
        writer.write("Unknown command. Use 'add <number> <skill>', 'done', or 'help <skill>'.\n")

    if spent >= skill_points:
        writer.write("\nAll skill points spent!\n")
    else:
        writer.write(f"\nYou have {skill_points - spent} unspent skill points (can allocate later with 'train').\n")
    writer.write("Skill allocation complete. Moving on...\n")
    return {k: v for k, v in skills.items() if v > 0}


async def prompt_spells(writer, reader, chosen_class, domains=None):
    from src.spells import DOMAIN_DATA

    # SPELLS is a dict {name: Spell}, iterate values
    spell_list = []
    for spell_obj in SPELLS.values():
        level_dict = getattr(spell_obj, 'level', {}) if hasattr(spell_obj, 'level') else {}
        if isinstance(level_dict, dict) and chosen_class in level_dict and level_dict[chosen_class] == 1:
            spell_list.append(spell_obj)
    # Add domain spells for 1st level if domains are provided
    if domains and chosen_class == "Cleric":
        for domain in domains:
            domain_spell = DOMAIN_DATA.get(domain, {}).get("spells", {}).get(1)
            if domain_spell and domain_spell in SPELLS:
                spell_list.append(SPELLS[domain_spell])
    if not spell_list:
        writer.write(f"\n{chosen_class} has no spells to choose at level 1.\n")
        return []
    writer.write("\nChoose your starting spells (comma separated numbers):\n")
    for i, spell in enumerate(spell_list, 1):
        sname = getattr(spell, 'name', str(spell))
        sdesc = getattr(spell, 'description', '')[:80]
        writer.write(f"  {i}. {sname} - {sdesc}\n")
    writer.write("Enter choices (or 'none'): ")
    raw = (await reader.read(100)).strip()
    if raw.lower() == 'none' or not raw:
        return []
    choices = raw.split(",")
    chosen = []
    for c in choices:
        try:
            idx = int(c.strip()) - 1
            if 0 <= idx < len(spell_list):
                sname = getattr(spell_list[idx], 'name', str(spell_list[idx]))
                chosen.append(sname)
        except Exception:
            continue
    return chosen


from src.feats import list_eligible_feats


async def prompt_feats(writer, reader, character=None, allow_multiple=False):
    """
    Prompt the user to select one or more eligible feats, grouped by category.
    Type 'info <number>' or 'info <name>' for details.
    """
    if character:
        eligible_feats = list_eligible_feats(character)
    else:
        eligible_feats = list(FEATS.keys())

    # Filter out metamagic/item creation feats for non-casters
    if character:
        NON_CASTER_CLASSES = {"Fighter", "Barbarian", "Rogue", "Monk"}
        if getattr(character, 'char_class', '') in NON_CASTER_CLASSES:
            eligible_feats = [f for f in eligible_feats
                              if getattr(FEATS.get(f), 'feat_type', 'general') not in ('metamagic', 'item_creation')]

    if not eligible_feats:
        writer.write("No eligible feats available.\n")
        return []

    # Group by feat_type
    by_type = {}
    for fname in eligible_feats:
        ftype = getattr(FEATS.get(fname), 'feat_type', 'general') or 'general'
        by_type.setdefault(ftype.title(), []).append(fname)

    # Build numbered list preserving order
    numbered = []
    def show_feats():
        writer.write("\n=== Eligible Feats ===\n")
        numbered.clear()
        for category in sorted(by_type.keys()):
            feats_in_cat = by_type[category]
            writer.write(f"\n  [{category}]\n")
            # Display in 2 columns
            col_width = 35
            for row_start in range(0, len(feats_in_cat), 2):
                line = "  "
                for col in range(2):
                    idx = row_start + col
                    if idx < len(feats_in_cat):
                        num = len(numbered) + 1
                        numbered.append(feats_in_cat[idx])
                        entry = f"{num:3}. {feats_in_cat[idx]}"
                        line += entry.ljust(col_width)
                writer.write(line.rstrip() + "\n")
        writer.write(f"\n{len(numbered)} feats available. Type 'info <#>' for details.\n")

    # Determine how many feats to pick
    num_feats = 1
    if character:
        # Fighters get bonus feat at L1
        if getattr(character, 'char_class', '') == 'Fighter':
            num_feats = 2
        # Humans get bonus feat at L1
        if 'Human' in getattr(character, 'race', ''):
            num_feats += 1
    writer.write(f"\nYou may choose {num_feats} feat(s) this level.\n")
    show_feats()

    # Build case-insensitive lookup
    feat_lookup = {f.lower(): f for f in eligible_feats}
    chosen_feats = []

    while len(chosen_feats) < num_feats:
        remaining = num_feats - len(chosen_feats)
        writer.write(f"[{remaining} feat(s) remaining] Enter number, name, or 'info <#>': ")
        raw = (await reader.read(200)).strip()
        if not raw:
            continue

        # Info command
        if raw.lower() == "info":
            writer.write("Usage: info <number> or info <feat name>\n")
            continue
        if raw.lower().startswith("info "):
            query = raw[5:].strip()
            target = None
            try:
                idx = int(query) - 1
                if 0 <= idx < len(numbered):
                    target = numbered[idx]
            except ValueError:
                target = feat_lookup.get(query.lower())
                if not target:
                    matches = [f for k, f in feat_lookup.items() if query.lower() in k]
                    target = matches[0] if len(matches) == 1 else None
            if target and target in FEATS:
                f = FEATS[target]
                writer.write(f"\n  {target} [{getattr(f, 'feat_type', 'general')}]\n")
                writer.write(f"  {f.description}\n")
                prereqs = getattr(f, 'prerequisites', None)
                if prereqs:
                    writer.write(f"  Prereqs: {prereqs}\n")
                writer.write("\n")
            else:
                writer.write(f"Unknown feat '{query}'. Use a number or exact name.\n")
            continue

        if raw.lower() == "list":
            show_feats()
            continue

        # Try to resolve the selection
        selected = None
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(numbered):
                selected = numbered[idx]
        except ValueError:
            match = feat_lookup.get(raw.lower())
            if not match:
                matches = [f for k, f in feat_lookup.items() if raw.lower() in k]
                match = matches[0] if len(matches) == 1 else None
            selected = match

        if selected:
            if selected in chosen_feats:
                writer.write(f"You already picked {selected}. Choose a different feat.\n")
            else:
                chosen_feats.append(selected)
                writer.write(f"  Feat {len(chosen_feats)}/{num_feats}: {selected}\n")
        else:
            writer.write(f"'{raw}' not recognized. Enter a number, name, or 'info <#>'.\n")

    writer.write(f"Feats chosen: {', '.join(chosen_feats)}\n")
    return chosen_feats


async def prompt_deity(writer, reader):
    writer.write("\nChoose your patron deity:\n")
    for i, d in enumerate(DEITIES, 1):
        writer.write(f"  {i:2}. {d['name']}\n")
    writer.write(f"\nType 'info <#>' for details, or enter a number to choose.\n")
    while True:
        writer.write("Deity choice: ")
        raw = (await reader.read(100)).strip()
        if not raw:
            continue
        # Info command
        if raw.lower().startswith("info "):
            try:
                idx = int(raw[5:].strip()) - 1
                if 0 <= idx < len(DEITIES):
                    d = DEITIES[idx]
                    domains = ', '.join(d.get('domains', [])) or 'None'
                    writer.write(f"\n  {d['name']} [{d['alignment']}]\n")
                    writer.write(f"  Domains: {domains}\n")
                    writer.write(f"  {d.get('lore', '')}\n\n")
                else:
                    writer.write("Invalid number.\n")
            except ValueError:
                writer.write("Usage: info <number>\n")
            continue
        # Selection
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(DEITIES):
                writer.write(f"Selected: {DEITIES[idx]['name']}\n")
                return DEITIES[idx]["name"]
        except ValueError:
            # Text match
            query = raw.lower()
            for d in DEITIES:
                if query in d['name'].lower():
                    writer.write(f"Selected: {d['name']}\n")
                    return d['name']
        writer.write(f"'{raw}' not recognized. Enter a number or 'info <#>'.\n")


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
    # This function builds a pretty character sheet for confirmation
    lines = []
    from src.races import RACES as _RACES
    W = 78
    bar = "+" + "-" * W + "+"
    def row(text):
        t = text[:W]
        return "|" + t + " " * (W - len(t)) + "|"
    def tr(s, n):
        return str(s or '')[:n]

    class_data = CLASSES.get(chosen_class, {})
    race_data = _RACES.get(chosen_race, {})
    race_speed = race_data.get('speed', 30)
    race_elem = race_data.get('elemental_affinity', 'None') or 'None'
    race_size = race_data.get('size', 'Medium')
    hit_die = class_data.get('hit_die', 'd8')
    str_mod = (stats.get("STR", 10) - 10) // 2 if stats else 0
    grapple = str_mod

    # Saves
    fort = ref = will = 0
    if stats:
        def calc_save(save_type):
            prog = class_data.get("save_progression", {}).get(save_type, "poor")
            base = 2 if prog == "good" else 0
            mod_map = {"fort": "CON", "ref": "DEX", "will": "WIS"}
            return base + (stats.get(mod_map[save_type], 10) - 10) // 2
        fort, ref, will = calc_save("fort"), calc_save("ref"), calc_save("will")

    # HP = hit die max + con mod
    con_mod = (stats.get("CON", 10) - 10) // 2 if stats else 0
    hp = int(str(hit_die).replace('d','')) + con_mod
    hp = max(1, hp)

    lines = []
    lines.append(bar)
    lines.append(row(f" Name: {tr(username,18):<18}  Level: 1    Class: {tr(chosen_class,18):<18}"))
    lines.append(row(f" Race: {tr(chosen_race,18):<18}  Alignment: {tr(alignment,18):<18}"))
    lines.append(bar)
    lines.append(row(f" Deity: {tr(deity,30):<30}  Element: {tr(race_elem,10):<10}"))
    lines.append(row(f" Size: {tr(race_size,8):<8}  Speed: {race_speed:<4} ft  Hit Die: {hit_die}"))
    lines.append(bar)
    if stats:
        lines.append(row(f" STR: {stats.get('STR',10):<4} DEX: {stats.get('DEX',10):<4} CON: {stats.get('CON',10):<4} INT: {stats.get('INT',10):<4} WIS: {stats.get('WIS',10):<4} CHA: {stats.get('CHA',10):<4}"))
    lines.append(row(f" HP: {hp:<4}  AC: 10  Fort: {fort:<3} Ref: {ref:<3} Will: {will:<3}"))
    lines.append(bar)
    lines.append(row(f" Feats: {tr(', '.join(feats), 68):<68}"))
    lines.append(row(f" Equipment: {tr(', '.join(equipment), 64):<64}"))
    gold = {"Fighter": 150, "Barbarian": 80, "Rogue": 140, "Bard": 120, "Cleric": 100, "Druid": 60, "Monk": 20, "Paladin": 120, "Ranger": 100, "Wizard": 80, "Sorcerer": 80, "Magi": 80}.get(chosen_class, 100)
    lines.append(row(f" Gold: {gold} gp"))
    lines.append(bar)
    return "\n".join(lines)


async def confirm_character(writer, reader, summary):
    writer.write("\n")
    writer.write(summary + "\n")
    writer.write("Confirm character? (y/n): ")
    data = await reader.read(10)
    return data.strip().lower() == "y"


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


async def hunger_thirst_tick(world):
    """Periodic tick to drain hunger/thirst for players in survival mode."""
    while True:
        await asyncio.sleep(60)
        try:
            for player in world.players:
                if not getattr(player, 'survival_mode', False):
                    continue
                if getattr(player, 'is_ai', False):
                    continue
                player.hunger = max(0, getattr(player, 'hunger', 100) - 1)
                player.thirst = max(0, getattr(player, 'thirst', 100) - 2)
                _w = getattr(player, 'writer', None)
                if not _w:
                    continue
                try:
                    if player.hunger == 25:
                        _w.write("\nYou are very hungry!\n")
                    elif player.hunger == 0:
                        _w.write("\nYou are starving! Find food soon!\n")
                        # Add fatigued condition from starvation
                        if not player.has_condition('fatigued'):
                            player.add_condition('fatigued')
                            _w.write("You are fatigued from hunger.\n")
                    elif player.hunger > 0 and player.has_condition('fatigued'):
                        # Check if fatigue was from hunger (remove it when fed)
                        # Only remove if thirst isn't also causing it
                        if getattr(player, 'thirst', 100) > 0:
                            player.remove_condition('fatigued')
                            _w.write("You no longer feel fatigued.\n")

                    if player.thirst == 25:
                        _w.write("\nYou are very thirsty!\n")
                    elif player.thirst == 0:
                        _w.write("\nYou are dehydrated! Find water!\n")
                        # Add exhausted condition from dehydration
                        if not player.has_condition('exhausted'):
                            player.add_condition('exhausted')
                            _w.write("You are exhausted from dehydration.\n")
                    elif player.thirst > 0 and player.has_condition('exhausted'):
                        player.remove_condition('exhausted')
                        _w.write("You no longer feel exhausted.\n")
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error in hunger/thirst tick: {e}")


async def schedule_tick(world):
    """Periodic tick to advance game time and process NPC schedules."""
    from src.schedules import get_game_time, get_schedule_manager
    game_time = get_game_time()
    sched_mgr = get_schedule_manager()
    while True:
        await asyncio.sleep(30)  # Tick every 30 seconds
        try:
            game_time.tick()
            messages = sched_mgr.tick(game_time, world)
            # Broadcast movement messages to rooms
            for room_vnum, msg in messages:
                room = world.rooms.get(room_vnum)
                if room:
                    for p in getattr(room, 'players', []):
                        _pw = getattr(p, 'writer', None)
                        if _pw and not getattr(p, 'is_ai', False):
                            try:
                                _pw.write(f"\n{msg}\n")
                            except Exception:
                                pass
        except Exception as e:
            logger.error(f"Error in schedule tick: {e}")


async def location_effects_tick(world):
    """Periodically process environmental hazards in rooms."""
    from src.location_effects import get_location_effects
    le = get_location_effects()
    while True:
        try:
            await asyncio.sleep(60)
            notifications = le.tick_hazards(world)
            for player, msg in notifications:
                if hasattr(player, '_writer'):
                    try:
                        player._writer.write(msg + "\n")
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"Error in location effects tick: {e}")


async def wandering_gods_tick(world):
    """Move gods between shrines and notify nearby players."""
    wg = get_wandering_gods()
    wg.initialize()
    while True:
        try:
            await asyncio.sleep(60)
            movements = wg.tick(world)
            # Notify players in rooms where gods arrive/depart
            for god, old_vnum, new_vnum in movements:
                # Notify players in the new room
                if new_vnum in world.rooms:
                    for player in world.rooms[new_vnum].players:
                        msg = god.get_presence_message(player)
                        if msg and hasattr(player, '_writer'):
                            try:
                                player._writer.write(f"\n{msg}\n")
                            except Exception:
                                pass
        except Exception as e:
            logger.error(f"Error in wandering gods tick: {e}")


async def chat_despawn_tick(world):
    """Auto-despawn stale chat sessions (30 min inactive)."""
    while True:
        try:
            await asyncio.sleep(60)  # Check every 60 seconds
            from src.shadow_presence import shadow_manager
            from src.chat_session import force_end_timeout
            stale = shadow_manager.get_stale(timeout_seconds=1800)
            for shadow in stale:
                if shadow.is_telnet and shadow.character_ref:
                    char = shadow.character_ref
                    if getattr(char, 'active_chat_session', None):
                        force_end_timeout(char.active_chat_session, char)
                else:
                    shadow_manager.remove(shadow.player_id)
        except Exception as e:
            logger.error(f"Error in chat despawn tick: {e}")


async def townsfolk_tick(world):
    """Move wandering townsfolk and send ambient messages to nearby players."""
    from src.townsfolk import get_townsfolk_manager
    mgr = get_townsfolk_manager()
    mgr.initialize(world)
    while True:
        try:
            await asyncio.sleep(30)  # Check every 30 seconds
            messages = mgr.tick(world)
            for vnum, msg in messages:
                if vnum in world.rooms:
                    for player in world.rooms[vnum].players:
                        if hasattr(player, '_writer'):
                            try:
                                player._writer.write(f"\n\033[0;90m{msg}\033[0m\n")
                            except Exception:
                                pass
        except Exception as e:
            logger.error(f"Error in townsfolk tick: {e}")


async def spawn_respawn_tick(world):
    """Periodically check for dead mobs and respawn them."""
    spawn_mgr = get_spawn_manager()
    if not spawn_mgr.spawn_points:
        # Initialize from current mobs data
        import json as _json
        try:
            with open("data/mobs.json", encoding="utf-8") as _f:
                mobs_data = _json.load(_f)
            spawn_mgr.initialize_from_mobs_data(mobs_data)
            spawn_mgr.link_existing_mobs(world)
            logger.info(f"SpawnManager initialized with {len(spawn_mgr.spawn_points)} spawn points")
        except Exception as e:
            logger.error(f"Failed to initialize SpawnManager: {e}")
            return
    while True:
        try:
            await asyncio.sleep(30)
            messages = spawn_mgr.tick(world)
            for msg in messages:
                logger.info(f"Spawn: {msg}")
        except Exception as e:
            logger.error(f"Error in spawn tick: {e}")


async def encounter_tick(world):
    """Roll regional random encounters and advance active stalkers."""
    from src.encounters import get_encounter_manager
    from src.schedules import get_game_time
    mgr = get_encounter_manager()
    game_time = get_game_time()
    while True:
        try:
            await asyncio.sleep(30)
            messages = mgr.tick(world, game_time)
            for msg in messages:
                logger.info(f"Encounter: {msg}")
        except Exception as e:
            logger.error(f"Error in encounter tick: {e}")


async def ambient_echo_tick(world):
    """Send ambient room echoes to players periodically."""
    import random as _rnd
    AMBIENT_MESSAGES = {
        'forest': [
            "Leaves rustle in the wind.",
            "A bird calls from somewhere in the canopy.",
            "Sunlight filters through the branches above.",
        ],
        'cave': [
            "Water drips from the ceiling.",
            "A faint echo reverberates through the cavern.",
            "You hear stones shifting somewhere in the darkness.",
        ],
        'safe': [
            "You hear the distant murmur of conversation.",
            "A merchant calls out to passersby.",
        ],
        'town': [
            "You hear the distant murmur of conversation.",
            "The smell of fresh bread wafts from a nearby bakery.",
        ],
        'water': [
            "Waves lap gently against the shore.",
            "The sound of flowing water fills the air.",
        ],
        'mountain': [
            "A cold wind whistles through the peaks.",
            "Loose pebbles tumble down the slope.",
        ],
    }
    while True:
        await asyncio.sleep(60)
        try:
            # Collect rooms with players
            visited_rooms = set()
            for player in world.players:
                if getattr(player, 'is_ai', False):
                    continue
                room = getattr(player, 'room', None)
                if room and room.vnum not in visited_rooms:
                    visited_rooms.add(room.vnum)
                    # 10% chance for ambient echo
                    if _rnd.random() < 0.10:
                        flags = getattr(room, 'flags', [])
                        terrain = getattr(room, 'terrain', '')
                        # Determine message pool from terrain or flags
                        msg_pool = None
                        for key in AMBIENT_MESSAGES:
                            if key in flags or key == terrain:
                                msg_pool = AMBIENT_MESSAGES[key]
                                break
                        if msg_pool:
                            msg = _rnd.choice(msg_pool)
                            for p in room.players:
                                _pw = getattr(p, 'writer', None)
                                if _pw and not getattr(p, 'is_ai', False):
                                    try:
                                        _pw.write(f"\n{msg}\n")
                                    except Exception:
                                        pass
        except Exception as e:
            logger.error(f"Error in ambient echo tick: {e}")


async def weather_tick(world):
    """Periodic tick to update dynamic weather per region."""
    from src.weather import get_weather_manager
    wm = get_weather_manager()
    while True:
        await asyncio.sleep(30)  # Check every 30 seconds (timer managed internally)
        try:
            await wm.update(world)
        except Exception as e:
            logger.error(f"Error in weather tick: {e}")


async def area_reset_tick(world):
    """Periodic tick to check and perform area resets."""
    from src.area_resets import get_reset_manager
    rm = get_reset_manager()
    while True:
        await asyncio.sleep(60)  # Check every 60 seconds
        try:
            await rm.check_resets(world)
        except Exception as e:
            logger.error(f"Error in area reset tick: {e}")


async def narrative_tick(world):
    """Periodic tick to check narrative triggers for online players."""
    from src.narrative import get_narrative_manager
    nm = get_narrative_manager()
    while True:
        await asyncio.sleep(120)  # Check every 2 minutes
        try:
            for player in world.players:
                if getattr(player, 'is_ai', False):
                    continue
                triggered = nm.check_triggers(player)
                for chapter in triggered:
                    text, rewards = nm.trigger_chapter(player, chapter)
                    _w = getattr(player, '_writer', None) or getattr(player, 'writer', None)
                    if _w:
                        try:
                            _w.write(text + "\n")
                            if rewards:
                                if "xp" in rewards:
                                    player.xp = getattr(player, 'xp', 0) + rewards["xp"]
                                    _w.write(f"Gained {rewards['xp']} XP!\n")
                                if "title" in rewards:
                                    if not hasattr(player, 'titles'):
                                        player.titles = []
                                    if rewards["title"] not in player.titles:
                                        player.titles.append(rewards["title"])
                                    _w.write(f"Earned title: {rewards['title']}\n")
                        except Exception:
                            pass
        except Exception as e:
            logger.error(f"Error in narrative tick: {e}")


async def main():
    world = OrekaWorld()
    world.load_data()

    # Initialize captive-rescue state on all statically-placed captives
    try:
        from src.captives import apply_captive_state_on_load
        apply_captive_state_on_load(world)
    except Exception as e:
        logger.warning(f"Captive state init failed: {e}")

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
    world.players_by_name[ai_character.name.lower()] = ai_character
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
    world.players_by_name[hareem.name.lower()] = hareem
    world.rooms[1000].players.append(hareem)

    logger.info("Starting Oreka MUD server on 127.0.0.1:4000 (raw asyncio TCP)")

    # =====================================================================
    # RAW TCP SERVER — replaces telnetlib3 for universal client compatibility
    # =====================================================================
    IAC, WILL, WONT, DO, DONT, SB, SE = 255, 251, 252, 253, 254, 250, 240
    GMCP_OPT = 201

    class TelnetReader:
        """Wraps asyncio.StreamReader with telnet-aware readline."""
        def __init__(self, stream_reader):
            self._reader = stream_reader
            self._buffer = ""

        async def readline(self):
            """Read until newline, stripping telnet IAC sequences."""
            while '\n' not in self._buffer:
                try:
                    raw = await asyncio.wait_for(self._reader.read(4096), timeout=300)
                except asyncio.TimeoutError:
                    return ""
                if not raw:
                    return ""
                # Strip telnet negotiation bytes
                clean = self._strip_iac(raw)
                self._buffer += clean.decode('utf-8', errors='replace')

            line, self._buffer = self._buffer.split('\n', 1)
            return line.strip('\r')

        async def read(self, n):
            """Read up to n chars, stripping telnet IAC."""
            while len(self._buffer) < n:
                try:
                    raw = await asyncio.wait_for(self._reader.read(4096), timeout=300)
                except asyncio.TimeoutError:
                    break
                if not raw:
                    break
                clean = self._strip_iac(raw)
                self._buffer += clean.decode('utf-8', errors='replace')
                if self._buffer:
                    break  # Got something, return it

            result = self._buffer[:n]
            self._buffer = self._buffer[n:]
            return result

        def _strip_iac(self, data):
            """Remove all telnet IAC negotiation sequences from raw bytes."""
            result = bytearray()
            i = 0
            while i < len(data):
                if data[i] == IAC and i + 1 < len(data):
                    cmd = data[i + 1]
                    if cmd in (WILL, WONT, DO, DONT):
                        i += 3  # IAC + cmd + option
                    elif cmd == SB:
                        # Skip subnegotiation until IAC SE
                        j = i + 2
                        while j < len(data) - 1:
                            if data[j] == IAC and data[j + 1] == SE:
                                j += 2
                                break
                            j += 1
                        i = j
                    elif cmd == IAC:
                        result.append(IAC)
                        i += 2
                    else:
                        i += 2
                else:
                    result.append(data[i])
                    i += 1
            return bytes(result)

    class TelnetWriter:
        """Wraps asyncio.StreamWriter with write/close/drain and _writer for GMCP."""
        def __init__(self, stream_writer):
            self._writer = stream_writer
            self._transport = stream_writer.transport if hasattr(stream_writer, 'transport') else None

        def write(self, text):
            """Send text to client."""
            if isinstance(text, str):
                text = text.encode('utf-8', errors='replace')
            try:
                self._writer.write(text)
            except Exception:
                pass

        async def drain(self):
            try:
                await self._writer.drain()
            except Exception:
                pass

        def close(self):
            try:
                self._writer.close()
            except Exception:
                pass

    async def tcp_client_handler(stream_reader, stream_writer):
        """Handle a raw TCP connection."""
        addr = stream_writer.get_extra_info('peername')
        logger.info(f"Connection from {addr}")

        reader = TelnetReader(stream_reader)
        writer = TelnetWriter(stream_writer)

        # Send minimal telnet negotiation (don't wait for response)
        try:
            stream_writer.write(bytes([IAC, WILL, GMCP_OPT]))  # Advertise GMCP
            await stream_writer.drain()
        except Exception:
            pass

        # Small delay to let client negotiate, then proceed regardless
        await asyncio.sleep(0.3)

        try:
            await handle_client(reader, writer, world, parser)
        except ConnectionError as e:
            logger.info(f"Client disconnected: {addr} - {e}")
        except Exception as e:
            logger.error(f"Client handler crashed for {addr}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up active chat session on disconnect
            try:
                if character and getattr(character, 'active_chat_session', None):
                    from src.chat_session import end_session as _end_chat
                    _end_chat(character.active_chat_session, character)
            except Exception:
                pass
            logger.info(f"Connection closed for {addr}")
            writer.close()

    server = await asyncio.start_server(tcp_client_handler, '127.0.0.1', 4000)

    # Start MCP Bridge (internal REST API on port 8001)
    mcp_set_world(world)
    mcp_set_loop(asyncio.get_running_loop())
    start_mcp_bridge_thread()

    # Load modules (arcs, personas, rooms, quests, hooks)
    try:
        from src.module_loader import apply_all_modules_to_world
        mod_result = apply_all_modules_to_world(world)
        logger.info(f"Module loader: {mod_result}")
    except Exception as e:
        logger.error(f"Module loading failed: {e}")

    # Start background ticks
    asyncio.create_task(log_players(world))
    asyncio.create_task(hunger_thirst_tick(world))
    asyncio.create_task(ambient_echo_tick(world))
    asyncio.create_task(schedule_tick(world))
    asyncio.create_task(spawn_respawn_tick(world))
    asyncio.create_task(wandering_gods_tick(world))
    asyncio.create_task(location_effects_tick(world))
    asyncio.create_task(townsfolk_tick(world))

    # Start chat session auto-despawn tick
    asyncio.create_task(chat_despawn_tick(world))

    # Start dynamic weather tick
    asyncio.create_task(weather_tick(world))

    # Start area reset tick
    asyncio.create_task(area_reset_tick(world))

    # Start narrative check tick
    asyncio.create_task(narrative_tick(world))

    # Start regional random-encounter tick
    asyncio.create_task(encounter_tick(world))

    # Start family-fate tick (burnt-trail timers, ambush waves, etc.)
    try:
        from src.family_fates import family_fate_tick
        asyncio.create_task(family_fate_tick(world))
    except Exception as e:
        logger.warning(f"Family fate tick not started: {e}")

    # Start WebSocket server (for Veil Client)
    # Keep a reference to prevent garbage collection of the task
    _ws_task = None
    try:
        from src.websocket_server import start_websocket_server
        _ws_task = asyncio.create_task(start_websocket_server())
    except Exception as e:
        logger.warning(f"WebSocket server not started: {e}")

    # Start standalone NPC chat server (port 8767)
    _npc_chat_task = None
    try:
        from src.npc_chat_server import start_npc_chat_server
        _npc_chat_task = asyncio.create_task(start_npc_chat_server(world))
    except Exception as e:
        logger.warning(f"NPC Chat server not started: {e}")

    # Start live-map WebSocket server + snapshot broadcaster
    _map_ws_task = None
    _map_snap_task = None
    try:
        from src.map_events import (start_map_ws_server,
                                    snapshot_broadcast_loop,
                                    install_log_handler)
        install_log_handler()
        _map_ws_task = asyncio.create_task(start_map_ws_server(world))
        _map_snap_task = asyncio.create_task(snapshot_broadcast_loop(world))
    except Exception as e:
        logger.warning(f"Map WS server not started: {e}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
