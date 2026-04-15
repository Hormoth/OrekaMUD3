"""
Veil Client authentication and access control.

Manages who can connect via the Veil WebSocket terminal and what mode
they're allowed to use. Characters are unified across MUD and Chat modes —
a player who logs in via Chat builds the same character file as a MUD player.
"""

import os
import json
import hashlib
import logging

logger = logging.getLogger("OrekaMUD.VeilAuth")

WHITELIST_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'veil_whitelist.json')
PLAYERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')


def _default_whitelist():
    return {
        "users": [],
        "allow_all_existing_chars": True,
        "open_signup": True,
        "chat_eligible_npcs": [3000, 9004, 9010, 9200],
        "default_chat_npc": 9200,
        "max_concurrent_users": 50,
    }


def load_whitelist() -> dict:
    """Load the Veil whitelist, creating a default if missing."""
    if not os.path.exists(WHITELIST_PATH):
        wl = _default_whitelist()
        save_whitelist(wl)
        return wl
    try:
        with open(WHITELIST_PATH, 'r', encoding='utf-8') as f:
            wl = json.load(f)
        # Fill in any missing keys with defaults
        defaults = _default_whitelist()
        for k, v in defaults.items():
            wl.setdefault(k, v)
        return wl
    except Exception as e:
        logger.error(f"Failed to load Veil whitelist: {e}")
        return _default_whitelist()


def save_whitelist(wl: dict):
    """Persist the Veil whitelist to disk."""
    try:
        with open(WHITELIST_PATH, 'w', encoding='utf-8') as f:
            json.dump(wl, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save Veil whitelist: {e}")


def is_allowed(username: str) -> tuple[bool, str]:
    """Check if a username is allowed to use the Veil Client.

    Returns (allowed, reason).
    """
    if not username:
        return False, "Username required."
    username = username.lower().strip()
    wl = load_whitelist()

    # Explicit whitelist
    if username in [u.lower() for u in wl.get("users", [])]:
        return True, "On whitelist."

    # Allow all existing characters
    if wl.get("allow_all_existing_chars", False):
        player_path = os.path.join(PLAYERS_DIR, f"{username}.json")
        if os.path.exists(player_path):
            return True, "Existing character — Veil access permitted."

    return False, "Veil access denied. Contact an administrator."


def can_signup() -> bool:
    """Check if new character creation via Veil is allowed."""
    wl = load_whitelist()
    return wl.get("open_signup", False)


def add_user(username: str) -> tuple[bool, str]:
    """Add a username to the explicit Veil whitelist."""
    username = username.strip()
    if not username:
        return False, "Username required."
    wl = load_whitelist()
    users = wl.get("users", [])
    if username.lower() in [u.lower() for u in users]:
        return False, f"{username} is already on the Veil whitelist."
    users.append(username)
    wl["users"] = users
    save_whitelist(wl)
    return True, f"{username} added to Veil whitelist."


def remove_user(username: str) -> tuple[bool, str]:
    """Remove a username from the Veil whitelist."""
    username = username.strip()
    if not username:
        return False, "Username required."
    wl = load_whitelist()
    users = wl.get("users", [])
    matching = [u for u in users if u.lower() == username.lower()]
    if not matching:
        return False, f"{username} is not on the Veil whitelist."
    for m in matching:
        users.remove(m)
    wl["users"] = users
    save_whitelist(wl)
    return True, f"{username} removed from Veil whitelist."


def set_config(key: str, value) -> tuple[bool, str]:
    """Set a config key on the whitelist (allow_all_existing_chars, open_signup, etc.)."""
    wl = load_whitelist()
    if key not in wl and key not in _default_whitelist():
        return False, f"Unknown config key '{key}'."
    wl[key] = value
    save_whitelist(wl)
    return True, f"Set {key} = {value}."


def list_config() -> dict:
    """Return the current whitelist configuration."""
    return load_whitelist()


# =========================================================================
# Password validation (mirrors main.py login flow)
# =========================================================================

def validate_password(username: str, password: str) -> tuple[bool, str]:
    """Validate a username/password pair against the player file.

    Returns (valid, reason). Mirrors the special cases in main.py for
    Dagdan and Hareem (hardcoded password 'Nero123').
    """
    if not username or not password:
        return False, "Username and password required."
    username = username.lower().strip()

    # Special cases for immortal accounts
    if username in ("dagdan", "hareem"):
        expected = hashlib.sha256("Nero123".encode()).hexdigest()
        actual = hashlib.sha256(password.encode()).hexdigest()
        if actual == expected:
            return True, "Authenticated (immortal)."
        return False, "Invalid password."

    # Regular players: load player file
    player_path = os.path.join(PLAYERS_DIR, f"{username}.json")
    if not os.path.exists(player_path):
        return False, "No such character."

    try:
        with open(player_path, 'r', encoding='utf-8') as f:
            pdata = json.load(f)
        if isinstance(pdata, list):
            pdata = pdata[0]
    except Exception as e:
        logger.error(f"Failed to load player file for {username}: {e}")
        return False, "Player file corrupt or missing."

    expected_hash = pdata.get("hashed_password")
    if not expected_hash:
        return False, "Character has no password set."

    actual_hash = hashlib.sha256(password.encode()).hexdigest()
    if actual_hash != expected_hash:
        return False, "Invalid password."

    return True, "Authenticated."


def character_exists(username: str) -> bool:
    """Check if a character file exists for this username."""
    if not username:
        return False
    username = username.lower().strip()
    if username in ("dagdan", "hareem"):
        return True
    player_path = os.path.join(PLAYERS_DIR, f"{username}.json")
    return os.path.exists(player_path)


# =========================================================================
# Chat NPC discovery
# =========================================================================

def list_chat_npcs(world=None) -> list[dict]:
    """Return a list of chat-eligible NPCs for the mode menu.

    If world is provided, returns live NPC data from the world.
    Otherwise loads names from data/mobs.json.
    """
    wl = load_whitelist()
    npc_vnums = wl.get("chat_eligible_npcs", [])

    npcs = []
    if world:
        for vnum in npc_vnums:
            mob = world.mobs.get(vnum)
            if mob and getattr(mob, 'alive', True):
                room = getattr(mob, 'room_vnum', None)
                room_name = "?"
                if room and room in world.rooms:
                    room_name = world.rooms[room].name
                npcs.append({
                    "vnum": vnum,
                    "name": mob.name,
                    "room": room_name,
                    "type": getattr(mob, 'type_', 'Unknown'),
                })
        return npcs

    # Fallback: load names from mobs.json
    mobs_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mobs.json')
    try:
        with open(mobs_path, 'r', encoding='utf-8') as f:
            mobs_data = json.load(f)
        by_vnum = {m['vnum']: m for m in mobs_data if 'vnum' in m}
        for vnum in npc_vnums:
            mob = by_vnum.get(vnum)
            if mob:
                npcs.append({
                    "vnum": vnum,
                    "name": mob.get("name", f"NPC #{vnum}"),
                    "room": None,
                    "type": mob.get("type_", "Unknown"),
                })
    except Exception as e:
        logger.error(f"Failed to load NPCs from mobs.json: {e}")
        return [{"vnum": v, "name": f"NPC #{v}", "room": None, "type": "?"} for v in npc_vnums]
    return npcs


def get_default_chat_npc() -> int:
    """Return the default NPC vnum for chat mode."""
    wl = load_whitelist()
    return wl.get("default_chat_npc", 9200)
