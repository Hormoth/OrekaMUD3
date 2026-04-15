"""
AI Chat Session System for OrekaMUD3.

Manages chat sessions where a player enters an AI-driven conversation with an NPC.
The player appears as a Shadow Presence in the NPC's room while chatting.
Real-world events (speech, combat, room events) inject into the AI context.
"""

import asyncio
import json
import os
import time
import uuid
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, List

logger = logging.getLogger("OrekaMUD.ChatSession")

CHAT_SESSIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'chat_sessions')
NPC_MEMORIES_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'npc_memories')

# ANSI colors
PURPLE = "\033[1;35m"
DIM_YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
WHITE = "\033[1;37m"
RESET = "\033[0m"


CHAT_STATES = {
    "IDLE", "ENTERING", "ACTIVE",
    "EXITING_CLEAN", "MATERIALIZING", "EXITING_FORCED",
    "EXITING_PATIENCE", "EXITING_PANIC",
}


@dataclass
class ChatSession:
    """Active AI chat session between a player and an NPC."""
    session_id: str
    player_name: str
    player_level: int
    player_class: str
    player_race: str
    player_deity: Optional[str]
    player_factions: dict
    npc_vnum: int
    npc_name: str
    npc_type: Optional[str]
    anchor_room_vnum: int
    anchor_room_name: str
    anchor_region: str
    started_at: float
    last_active: float
    conversation_history: list = field(default_factory=list)
    world_events_injected: list = field(default_factory=list)
    game_actions_executed: list = field(default_factory=list)
    materialized: bool = False
    ended: bool = False
    scenario: Optional[str] = None
    _summary: Optional[str] = None  # Compressed summary of older conversation

    # State machine (Phase 5)
    state: str = "IDLE"  # one of CHAT_STATES
    state_transitions: list = field(default_factory=list)  # list of {from, to, at, reason}
    exit_reason: Optional[str] = None  # final reason chat ended

    def transition_to(self, new_state: str, reason: str = ""):
        """Move session to a new state with audit trail."""
        if new_state not in CHAT_STATES:
            return False
        prior = self.state
        self.state = new_state
        self.state_transitions.append({
            "from": prior, "to": new_state,
            "at": time.time(), "reason": reason,
        })
        return True

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to conversation history."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
        }
        entry.update(kwargs)
        self.conversation_history.append(entry)
        self.last_active = time.time()

    def add_world_event(self, text: str):
        """Inject a world event into the conversation context."""
        event = {
            "text": text,
            "timestamp": time.time(),
        }
        self.world_events_injected.append(event)
        # Also add to conversation history as a system message
        self.conversation_history.append({
            "role": "system",
            "content": f"[WORLD EVENT] {text}",
            "timestamp": time.time(),
        })
        self.last_active = time.time()

    def get_recent_world_events(self, limit: int = 5) -> list:
        """Get the most recent world events."""
        return self.world_events_injected[-limit:]

    def get_messages_for_llm(self, max_messages: int = 20) -> list:
        """Get conversation history formatted for LLM API.
        Uses a sliding window to prevent context overflow."""
        messages = []
        for entry in self.conversation_history[-max_messages:]:
            role = entry["role"]
            content = entry["content"]
            if role == "system":
                messages.append({"role": "system", "content": content})
            elif role == "user":
                messages.append({"role": "user", "content": content})
            elif role == "assistant":
                messages.append({"role": "assistant", "content": content})
        return messages


def _get_region_for_vnum(vnum: int) -> str:
    """Map room vnum to region name."""
    regions = {
        (0, 4000): "Chapel",
        (4000, 5000): "Custos do Aeternos",
        (5000, 6000): "Kinsweave",
        (6000, 7000): "Tidebloom Reach",
        (7000, 8000): "Eternal Steppe",
        (8000, 9000): "Infinite Desert",
        (9000, 10000): "Deepwater Marches",
        (10000, 11000): "Twin Rivers",
        (11200, 13000): "Gatefall Reach",
        (13000, 13100): "Chainless Legion",
    }
    for (lo, hi), name in regions.items():
        if lo <= vnum < hi:
            return name
    return "Unknown"


def start_session(character, npc, room) -> ChatSession:
    """Create a new chat session and Shadow Presence.

    Args:
        character: The Character entering chat mode
        npc: The Mob being talked to
        room: The Room where the NPC is located

    Returns:
        ChatSession object
    """
    from src.shadow_presence import shadow_manager
    from src.character import State

    session_id = str(uuid.uuid4())[:12]
    region = _get_region_for_vnum(room.vnum)

    session = ChatSession(
        session_id=session_id,
        player_name=character.name,
        player_level=getattr(character, 'level', 1),
        player_class=getattr(character, 'char_class', 'Adventurer'),
        player_race=getattr(character, 'race', 'Unknown'),
        player_deity=getattr(character, 'deity', None),
        player_factions=dict(getattr(character, 'reputation', {})),
        npc_vnum=getattr(npc, 'vnum', 0),
        npc_name=getattr(npc, 'name', 'Unknown'),
        npc_type=getattr(npc, 'npc_type', None),
        anchor_room_vnum=room.vnum,
        anchor_room_name=getattr(room, 'name', 'Unknown'),
        anchor_region=region,
        started_at=time.time(),
        last_active=time.time(),
    )

    # State machine: IDLE -> ENTERING
    session.transition_to("ENTERING", reason="chat_command")

    # Create Shadow Presence
    shadow = shadow_manager.create_for_telnet(
        character, npc, room.vnum, session_id=session_id
    )

    # Link session and shadow to character
    character.active_chat_session = session
    character.chat_shadow = shadow
    character.state = State.CHATTING

    # Load NPC memory for this player
    npc_memory = load_npc_memory(npc.vnum, character.name)

    # Build opening narration
    opening = _build_opening(npc, room, npc_memory)
    session.add_message("assistant", opening)

    # Broadcast entry ritual to physical room AND NPC room
    _broadcast_entry_ritual(character, npc, room)

    # State machine: ENTERING -> ACTIVE
    session.transition_to("ACTIVE", reason="entry_complete")

    logger.info(f"Chat session started: {character.name} with {npc.name} "
                f"(session {session_id})")

    return session


def _broadcast_entry_ritual(character, npc, npc_room):
    """Tell other players in both rooms that a dream is forming."""
    try:
        from src.chat import send_to_player
    except Exception:
        return

    # NPC room: a shadow drifts in
    if npc_room and getattr(npc_room, 'players', None):
        for p in list(npc_room.players):
            if p is character:
                continue
            send_to_player(
                p,
                f"\033[0;35mA shadow of {character.name} drifts into view "
                f"beside {getattr(npc, 'name', 'the figure')}, half-real, half-dream.\033[0m"
            )

    # Physical room (the player's body): eyes go distant
    body_room = getattr(character, 'room', None)
    if body_room and body_room is not npc_room and getattr(body_room, 'players', None):
        for p in list(body_room.players):
            if p is character:
                continue
            send_to_player(
                p,
                f"\033[0;35m{character.name}'s eyes go distant. A faint echo "
                f"rises from them — they are dreaming.\033[0m"
            )


def end_session(session: ChatSession, character, farewell: str = None,
                exit_state: str = "EXITING_CLEAN", reason: str = ""):
    """End a chat session gracefully or otherwise.

    Args:
        session: The active ChatSession
        character: The Character leaving chat mode
        farewell: Optional NPC farewell line (rendered to player)
        exit_state: One of EXITING_CLEAN, MATERIALIZING, EXITING_FORCED,
                    EXITING_PATIENCE, EXITING_PANIC.
        reason: short string for audit log.
    """
    from src.shadow_presence import shadow_manager
    from src.character import State

    if exit_state not in CHAT_STATES:
        exit_state = "EXITING_CLEAN"

    session.transition_to(exit_state, reason=reason or exit_state)
    session.ended = True
    session.exit_reason = reason or exit_state

    # Remove Shadow Presence (unless materialize handled this elsewhere)
    if exit_state != "MATERIALIZING":
        shadow_manager.remove(character.name)
    character.chat_shadow = None
    character.active_chat_session = None
    character.state = State.EXPLORING

    # Render farewell to player
    writer = getattr(character, '_writer', None)
    if writer:
        try:
            if farewell:
                writer.write(f"\n  \033[1;36m{session.npc_name} says: \"{farewell}\"\033[0m\n")
            if exit_state == "EXITING_CLEAN":
                writer.write("  \033[0;35m~ You return from the dreamlight.\033[0m\n")
            elif exit_state == "EXITING_FORCED":
                writer.write("  \033[0;31m~ The dream snaps. You are pulled back into your body.\033[0m\n")
            elif exit_state == "EXITING_PATIENCE":
                writer.write("  \033[0;33m~ The conversation drifts to silence. You return to your body.\033[0m\n")
            elif exit_state == "EXITING_PANIC":
                writer.write("  \033[1;31m~ Something pulls at your body. The dream shatters!\033[0m\n")
        except Exception:
            pass

    # Save session log
    _save_session_log(session)

    # Extract and save NPC memory
    _extract_and_save_memory(session)

    logger.info(f"Chat session ended: {session.player_name} with {session.npc_name} "
                f"(session {session.session_id}, exit={exit_state}, reason={reason})")


# ---------------------------------------------------------------------------
# Materialization (Phase 5 §5.2.5)
# ---------------------------------------------------------------------------

MATERIALIZE_HP_COST_PCT = 0.10  # 10% of max HP
MATERIALIZE_COOLDOWN_SECS = 3600  # 1 hour


def materialize(session: ChatSession, character, world) -> str:
    """Player steps OUT of dream INTO the NPC's physical room.

    One-way teleport. Costs 10% max HP. Sets cooldown.
    Returns message string for the player.
    """
    from src.shadow_presence import shadow_manager
    from src.character import State

    # Check cooldown
    last_materialize = getattr(character, '_last_materialize_at', 0) or 0
    now = time.time()
    elapsed = now - last_materialize
    if elapsed < MATERIALIZE_COOLDOWN_SECS:
        wait = int((MATERIALIZE_COOLDOWN_SECS - elapsed) // 60) + 1
        return (f"\033[0;33mYou cannot materialize again so soon. "
                f"Wait about {wait} more minute(s).\033[0m")

    # Find target room
    target_room = world.rooms.get(session.anchor_room_vnum) if hasattr(world, 'rooms') else None
    if not target_room:
        return "\033[0;31mThe NPC's location is no longer reachable. Materialization fails.\033[0m"

    # Apply HP cost
    cost = max(1, int(character.max_hp * MATERIALIZE_HP_COST_PCT))
    character.hp = max(1, character.hp - cost)
    character._last_materialize_at = now

    # Move character to NPC's room
    old_room = getattr(character, 'room', None)
    if old_room and character in getattr(old_room, 'players', []):
        old_room.players.remove(character)
    character.room = target_room
    if character not in target_room.players:
        target_room.players.append(character)

    # Mark shadow as materialized then remove
    shadow = shadow_manager.shadows.get(character.name)
    if shadow:
        shadow.materialized = True
    shadow_manager.remove(character.name)

    # Broadcast to NPC room
    try:
        from src.chat import send_to_player
        for p in list(target_room.players):
            if p is character:
                continue
            send_to_player(
                p,
                f"\033[1;35mThe air shivers. {character.name} steps out of a "
                f"shadow and into the room.\033[0m"
            )
    except Exception:
        pass

    # End the session in MATERIALIZING state
    end_session(session, character, exit_state="MATERIALIZING", reason="enter_world")

    # End any other active dream sessions for this character (defensive)
    # (only one chat session is supported per char, so this is mainly for safety)

    return (f"\033[1;35m~ The dream solidifies. You step from the shadow into "
            f"{target_room.name}. ({cost} HP spent on the crossing.)\033[0m")


# ---------------------------------------------------------------------------
# Forced exits (Phase 5 §5.2.6)
# ---------------------------------------------------------------------------

def force_end_disturbed(session: ChatSession, character, disturber_name: str = "?"):
    """Another player disturbed the dreamer. End immediately with trust penalty."""
    npc_persona = _get_npc_persona_dict(session, character)
    farewell = "..."
    if npc_persona:
        farewell = npc_persona.get("farewell_line", "I... will speak with you another time.")

    end_session(
        session, character,
        farewell=farewell,
        exit_state="EXITING_FORCED",
        reason=f"disturbed_by:{disturber_name}",
    )

    # Trust penalty: mark the disturbing player as 'interrupted_my_counsel'
    try:
        from src.chat_context import save_npc_memory as save_mem
        save_mem(
            session.npc_vnum, disturber_name,
            f"[Disturbance] Interrupted my counsel with {character.name}.",
            importance=0.6, session_id="disturbed",
        )
    except Exception:
        pass


def force_end_timeout(session: ChatSession, character):
    """Real-time idle exceeded. NPC offers patience line and ends."""
    npc_persona = _get_npc_persona_dict(session, character)
    farewell = "Take your time. Find me again when you're ready."
    if npc_persona:
        farewell = npc_persona.get("farewell_line") or farewell

    end_session(
        session, character,
        farewell=farewell,
        exit_state="EXITING_PATIENCE",
        reason="idle_timeout",
    )


def force_end_body_death(session: ChatSession, character):
    """Player's body died while dreaming. NPC's last line is alarmed."""
    farewell = "Wait — what is happening? You're— "
    end_session(
        session, character,
        farewell=farewell,
        exit_state="EXITING_PANIC",
        reason="body_death",
    )


def _get_npc_persona_dict(session: ChatSession, character) -> dict:
    """Resolve the NPC's ai_persona dict (or None)."""
    try:
        room = getattr(character, 'room', None)
        if not room:
            return None
        for mob in getattr(room, 'mobs', []):
            if getattr(mob, 'vnum', None) == session.npc_vnum:
                p = getattr(mob, 'ai_persona', None)
                if p is None:
                    return None
                return p.to_dict() if hasattr(p, 'to_dict') else p
    except Exception:
        return None
    return None


async def process_player_input(session: ChatSession, character, text: str) -> str:
    """Process player input during chat mode.

    Routes the message through the AI system and returns the NPC response.
    Also handles game action execution.

    Args:
        session: Active ChatSession
        character: The Character
        text: Player's typed input

    Returns:
        Formatted NPC response string
    """
    from src import ai

    # Add player message to history
    session.add_message("user", text)

    # Update shadow activity
    from src.shadow_presence import shadow_manager
    shadow_manager.touch(character.name)

    # Get AI response
    try:
        response_text, actions = await ai.get_chat_response(
            session=session,
            character=character,
        )
    except asyncio.TimeoutError:
        return f"{session.npc_name} pauses, lost in thought..."
    except Exception as e:
        logger.error(f"Chat AI error: {e}")
        return f"{session.npc_name} seems distracted and doesn't respond."

    # Add NPC response to history
    session.add_message("assistant", response_text)

    # Execute game actions if any
    action_messages = []
    if actions:
        action_messages = await ai.execute_chat_actions(actions, character, session)
        for action in actions:
            session.game_actions_executed.append({
                "type": action.get("type", "unknown"),
                "data": action,
                "timestamp": time.time(),
            })

    # Format output
    output = f"{session.npc_name} says: \"{response_text}\""
    if action_messages:
        output += "\n" + "\n".join(action_messages)

    return output


# =========================================================================
# NPC Memory System
# =========================================================================

def load_npc_memory(npc_vnum: int, player_name: str) -> dict:
    """Load an NPC's memory of a specific player.

    Returns dict with keys: facts (list of strings), disposition, sessions, last_seen
    """
    path = os.path.join(NPC_MEMORIES_DIR, f"{npc_vnum}.json")
    if not os.path.exists(path):
        return {"facts": [], "disposition": "neutral", "sessions": 0, "last_seen": None}

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        memories = data.get("memories", {})
        player_mem = memories.get(player_name, {})
        return {
            "facts": player_mem.get("facts", []),
            "disposition": player_mem.get("disposition", "neutral"),
            "sessions": player_mem.get("sessions", 0),
            "last_seen": player_mem.get("last_seen"),
        }
    except Exception as e:
        logger.error(f"Failed to load NPC memory {npc_vnum}: {e}")
        return {"facts": [], "disposition": "neutral", "sessions": 0, "last_seen": None}


def save_npc_memory(npc_vnum: int, npc_name: str, player_name: str,
                    facts: list, disposition: str = "neutral"):
    """Save NPC memory about a player."""
    os.makedirs(NPC_MEMORIES_DIR, exist_ok=True)
    path = os.path.join(NPC_MEMORIES_DIR, f"{npc_vnum}.json")

    # Load existing
    data = {"npc_vnum": npc_vnum, "npc_name": npc_name, "memories": {}}
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            pass

    # Update player's entry
    memories = data.setdefault("memories", {})
    player_mem = memories.setdefault(player_name, {
        "facts": [],
        "disposition": "neutral",
        "sessions": 0,
    })
    # Merge new facts (deduplicate)
    existing = set(player_mem.get("facts", []))
    for fact in facts:
        if fact and fact not in existing:
            player_mem.setdefault("facts", []).append(fact)
            existing.add(fact)
    # Keep only last 10 facts
    player_mem["facts"] = player_mem["facts"][-10:]
    player_mem["disposition"] = disposition
    player_mem["sessions"] = player_mem.get("sessions", 0) + 1
    player_mem["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save NPC memory {npc_vnum}: {e}")


def _extract_and_save_memory(session: ChatSession):
    """Extract key facts from a chat session and save to NPC memory.
    Simple heuristic: save action-related facts and long player messages."""
    facts = []

    # Extract from game actions
    for action in session.game_actions_executed:
        atype = action.get("type", "")
        if atype == "modify_reputation":
            facts.append(f"Discussed faction matters ({action.get('data', {}).get('faction', '?')})")
        elif atype == "grant_quest":
            facts.append(f"Accepted quest: {action.get('data', {}).get('quest_id', '?')}")
        elif atype == "give_item":
            facts.append(f"Received an item")

    # Extract from conversation (player messages that are substantial)
    for entry in session.conversation_history:
        if entry.get("role") == "user" and len(entry.get("content", "")) > 40:
            # Summarize: take first 60 chars
            content = entry["content"][:60].strip()
            facts.append(f"Asked about: {content}")

    if facts:
        save_npc_memory(
            npc_vnum=session.npc_vnum,
            npc_name=session.npc_name,
            player_name=session.player_name,
            facts=facts[-5:],  # Max 5 facts per session
        )


def _save_session_log(session: ChatSession):
    """Save the complete session to a JSON log file."""
    os.makedirs(CHAT_SESSIONS_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{session.player_name}_{session.npc_name}_{timestamp}.json"
    # Sanitize filename
    filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
    path = os.path.join(CHAT_SESSIONS_DIR, filename)

    data = {
        "session_id": session.session_id,
        "player_name": session.player_name,
        "player_level": session.player_level,
        "player_class": session.player_class,
        "player_race": session.player_race,
        "npc_vnum": session.npc_vnum,
        "npc_name": session.npc_name,
        "anchor_room_vnum": session.anchor_room_vnum,
        "anchor_room_name": session.anchor_room_name,
        "anchor_region": session.anchor_region,
        "started_at": session.started_at,
        "ended_at": time.time(),
        "conversation_history": session.conversation_history,
        "world_events_injected": session.world_events_injected,
        "game_actions_executed": session.game_actions_executed,
        "materialized": session.materialized,
        "state": session.state,
        "state_transitions": session.state_transitions,
        "exit_reason": session.exit_reason,
    }

    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Session log saved: {path}")
    except Exception as e:
        logger.error(f"Failed to save session log: {e}")


def _build_opening(npc, room, npc_memory: dict) -> str:
    """Build the opening narration + NPC greeting for a chat session."""
    lines = []

    # Scene narration
    ai_persona = getattr(npc, 'ai_persona', None)
    if ai_persona and ai_persona.get("opening_line"):
        lines.append(ai_persona["opening_line"])
    elif getattr(npc, 'dialogue', None):
        lines.append(npc.dialogue)
    else:
        lines.append(f"\"Hmm? What brings you here, traveler?\"")

    # If NPC has memory of this player, add a recognition line
    if npc_memory.get("sessions", 0) > 0:
        lines.append(f"\"Ah, I remember you. Welcome back.\"")

    return " ".join(lines)
