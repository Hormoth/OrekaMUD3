"""Standalone NPC chat server.

A lightweight WebSocket endpoint (port 8767) that lets anyone connect
directly to an NPC conversation without going through the full MUD
login flow.  Opens ``oreka_npc_chat.html`` in a browser, pick an NPC
from the dropdown, type, get AI responses.

Uses the same ``ai.get_npc_response()`` pipeline as the in-game
``talk`` command, so NPC personas, room ambience, and the character
dossier all apply.

Runs as an ``asyncio.create_task`` inside main.py alongside the
other background servers.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("OrekaMUD.NPCChat")

NPC_CHAT_PORT = 8767
NPC_CHAT_HOST = "0.0.0.0"


# ---------------------------------------------------------------------------
# Ghost player — minimal Character-like object for AI prompt context
# ---------------------------------------------------------------------------

class GhostPlayer:
    """A lightweight stand-in for a real Character, carrying just enough
    attributes for ``ai.get_npc_response()`` and the dossier builder
    to work without crashing on missing fields."""

    def __init__(self, name: str = "Visitor"):
        self.name = name
        self.level = 5
        self.race = "Eruskan Human"
        self.char_class = "Adventurer"
        self.hp = 30
        self.max_hp = 30
        self.ac = 12
        self.is_ai = False
        self.is_immortal = False
        self.reputation = {}
        self.rescued_captives = []
        self.pending_rescue_rewards = []
        self.revealed_quests = []
        self.completed_hidden_quests = []
        self.rooms_visited = set()
        self.kill_count = 0
        self.craft_count = 0
        self.remort_count = 0
        self.elemental_affinity = None
        self.alignment = "Neutral"
        self.deity = None
        self.title = "Visitor"
        self.room = None
        self.inventory = []
        self.equipment = {}
        self.rp_sheet = None
        self.quest_log = None
        self.xp = 0
        self.gold = 0
        self.feats = []
        self.skills = {}
        self.str_score = 10
        self.dex_score = 10
        self.con_score = 10
        self.int_score = 10
        self.wis_score = 10
        self.cha_score = 10
        self.writer = None
        self.afk = False
        self.active_chat_session = None

    def get_prompt(self):
        return "> "


# ---------------------------------------------------------------------------
# Session state per connected client
# ---------------------------------------------------------------------------

class ChatClientSession:
    def __init__(self, ws):
        self.ws = ws
        self.npc = None
        self.room = None
        self.player = GhostPlayer()  # replaced with real Character on auth
        self.authenticated = False
        self.history: list = []  # [(role, text), ...]


# ---------------------------------------------------------------------------
# Character loading from disk (same as MUD login, but read-only)
# ---------------------------------------------------------------------------

def _load_character(username: str, password: str, world) -> Optional[Any]:
    """Load a real Character from disk, verify password.
    Returns the Character object or None on failure."""
    import os, hashlib, json as _json
    players_dir = os.path.join(os.path.dirname(__file__), "..", "data", "players")
    player_file = os.path.join(players_dir, f"{username}.json")
    if not os.path.exists(player_file):
        return None
    try:
        with open(player_file, "r", encoding="utf-8") as f:
            data = _json.load(f)
    except Exception:
        return None
    # Verify password
    stored_hash = data.get("hashed_password")
    if stored_hash is None:
        return None
    attempt_hash = hashlib.sha256(password.encode()).hexdigest()
    if attempt_hash != stored_hash:
        return None
    # Build the Character
    try:
        from src.character import Character
        char = Character.from_dict(data)
        # Set their room from the world for AI context
        room_vnum = data.get("room_vnum")
        if room_vnum and world:
            char.room = world.rooms.get(room_vnum)
        return char
    except Exception as e:
        logger.warning("NPC Chat: failed to load character %s: %s", username, e)
        return None


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

_world = None


def _list_chat_npcs(world) -> list:
    """Return a list of NPCs available for chat."""
    npcs = []
    seen_names = set()
    for vnum, mob in world.mobs.items():
        if not getattr(mob, "alive", True):
            continue
        flags = {str(f).lower() for f in getattr(mob, "flags", []) or []}
        # Include: quest_givers, family_reps, named NPCs with dialogue or persona
        if not (flags & {"quest_giver", "family_rep", "shopkeeper",
                          "innkeeper", "trainer", "priest", "guard"}):
            # Also include any mob with an ai_persona or dialogue
            if not getattr(mob, "ai_persona", None) and \
               not getattr(mob, "dialogue", None):
                continue
        name = getattr(mob, "name", "?")
        if name in seen_names:
            continue
        seen_names.add(name)
        room = None
        room_name = "unknown"
        room_vnum = getattr(mob, "room_vnum", None)
        if room_vnum is None:
            # Find room by scanning
            for r in world.rooms.values():
                if mob in r.mobs:
                    room = r
                    room_vnum = r.vnum
                    room_name = r.name
                    break
        else:
            room = world.rooms.get(room_vnum)
            room_name = room.name if room else "unknown"
        npcs.append({
            "vnum": vnum,
            "name": name,
            "room_vnum": room_vnum,
            "room_name": room_name,
            "cr": getattr(mob, "cr", None),
        })
    # Sort by name
    npcs.sort(key=lambda n: n["name"])
    return npcs


async def _handle_client(ws, world):
    session = ChatClientSession(ws)
    try:
        # Send welcome with NPC list
        npcs = _list_chat_npcs(world)
        await ws.send(json.dumps({
            "type": "welcome",
            "npcs": npcs,
            "message": (f"Welcome to Oreka NPC Chat. {len(npcs)} NPCs available. "
                        "Log in with your character for the full experience, "
                        "or chat as a guest."),
        }))

        async for raw in ws:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            msg_type = msg.get("type")

            # --- Authentication (optional but recommended) ----------------
            if msg_type == "auth":
                username = (msg.get("username") or "").strip()
                password = (msg.get("password") or "").strip()
                if not username or not password:
                    await ws.send(json.dumps({
                        "type": "auth_result",
                        "success": False,
                        "message": "Username and password required.",
                    }))
                    continue
                char = _load_character(username, password, world)
                if char is None:
                    await ws.send(json.dumps({
                        "type": "auth_result",
                        "success": False,
                        "message": "Login failed. Check username/password.",
                    }))
                    continue
                session.player = char
                session.authenticated = True
                # Build a quick dossier summary for the welcome
                try:
                    from src.character_dossier import build_dossier
                    d = build_dossier(char)
                    tags = d.get("tags", [])[:3]
                    tag_str = ", ".join(tags) if tags else "newcomer"
                except Exception:
                    tag_str = ""
                await ws.send(json.dumps({
                    "type": "auth_result",
                    "success": True,
                    "character_name": char.name,
                    "level": getattr(char, "level", 1),
                    "race": getattr(char, "race", "?"),
                    "char_class": getattr(char, "char_class", "?"),
                    "tags": tag_str,
                    "message": (f"Logged in as {char.name}, level "
                                f"{getattr(char, 'level', 1)} "
                                f"{getattr(char, 'race', '?')} "
                                f"{getattr(char, 'char_class', '?')}. "
                                f"NPCs will recognize you."),
                }))

            # --- Start chat with a specific NPC ---------------------------
            elif msg_type == "start":
                npc_vnum = msg.get("npc_vnum")
                # Guest name fallback
                if not session.authenticated:
                    guest_name = (msg.get("player_name") or "Visitor").strip()
                    session.player.name = guest_name

                mob = world.mobs.get(npc_vnum)
                if mob is None:
                    await ws.send(json.dumps({
                        "type": "error",
                        "message": f"NPC vnum {npc_vnum} not found.",
                    }))
                    continue

                session.npc = mob
                # Find the NPC's room for context
                for r in world.rooms.values():
                    if mob in r.mobs:
                        session.room = r
                        if not session.authenticated:
                            session.player.room = r
                        break

                session.history = []
                npc_name = getattr(mob, "name", "NPC")
                auth_note = (f" (chatting as {session.player.name})"
                             if session.authenticated else
                             " (guest mode — log in for the full experience)")
                await ws.send(json.dumps({
                    "type": "started",
                    "npc_name": npc_name,
                    "npc_description": getattr(mob, "description", ""),
                    "room_name": session.room.name if session.room else "unknown",
                    "auth_note": auth_note,
                }))

            # --- Send a message to the NPC --------------------------------
            elif msg_type == "message":
                if session.npc is None:
                    await ws.send(json.dumps({
                        "type": "error",
                        "message": "No NPC selected. Send a 'start' message first.",
                    }))
                    continue

                text = (msg.get("text") or "").strip()
                if not text:
                    continue

                # Unified prompt pipeline — same function the MUD uses
                try:
                    from src.prompt_pipeline import (
                        build_npc_prompt, extract_and_save_memory
                    )
                    from src.ai import _call_ollama, _config

                    system_prompt, user_prompt = build_npc_prompt(
                        npc=session.npc,
                        player=session.player,
                        message=text,
                        room=session.room,
                        conversation_history=session.history,
                        mode="chat",
                    )
                    if _config["enabled"]:
                        response = await _call_ollama(user_prompt,
                                                       system_prompt)
                        if response:
                            response = response.strip().strip('"').strip("'")
                            if len(response) > 500:
                                response = response[:497] + "..."
                        else:
                            response = "(The NPC says nothing.)"
                    else:
                        response = "(AI is currently disabled.)"
                except Exception as e:
                    # Fallback to old direct path
                    try:
                        from src import ai
                        response = await ai.get_npc_response(
                            npc=session.npc,
                            player=session.player,
                            message=text,
                            room=session.room,
                            use_llm=True,
                        )
                    except Exception:
                        response = f"(AI error: {e})"

                session.history.append(("player", text))
                session.history.append(("npc", response))

                # Save NPC memory every 5 exchanges
                if len(session.history) % 10 == 0:
                    try:
                        extract_and_save_memory(session.npc,
                                                 session.player,
                                                 session.history)
                    except Exception:
                        pass

                npc_name = getattr(session.npc, "name", "NPC")
                await ws.send(json.dumps({
                    "type": "response",
                    "npc_name": npc_name,
                    "text": response,
                }))

    except Exception as e:
        logger.debug("NPC chat client error: %s", e)


async def start_npc_chat_server(world):
    """Start the standalone NPC chat WebSocket server."""
    global _world
    _world = world
    try:
        import websockets
    except ImportError:
        logger.warning("NPC Chat: websockets not installed, server not started")
        return

    async def handler(ws):
        await _handle_client(ws, world)

    logger.info("NPC Chat: starting on ws://%s:%d",
                NPC_CHAT_HOST, NPC_CHAT_PORT)
    async with websockets.serve(handler, NPC_CHAT_HOST, NPC_CHAT_PORT,
                                ping_interval=30, ping_timeout=10):
        await asyncio.Future()  # run forever
