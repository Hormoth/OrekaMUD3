import asyncio
import logging
from src.world import OrekaWorld
from src.commands import CommandParser
from src.character import Character
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrekaMUD")

async def handle_client(reader, writer, world, parser):
    logger.info("New client connected")
    writer.write(b"Welcome to Oreka MUD!\nEnter name (Dagdan for immortal): ")
    name_data = await reader.read(100)
    name = name_data.decode().strip()
    
    start_room = world.rooms[1000]
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
            max_move=150
        )
    else:
        character = Character(name, None, "Hasura Elf", 5, 50, 100, 14, start_room,
                              str_score=12, dex_score=14, con_score=12, int_score=14, wis_score=12, cha_score=16,
                              mana=100, max_mana=100, move=100, max_move=100)
    
    world.players.append(character)
    character.room.players.append(character)
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

    world.players.remove(character)
    character.room.players.remove(character)
    logger.info(f"Character {character.name} disconnected")
    writer.close()

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
