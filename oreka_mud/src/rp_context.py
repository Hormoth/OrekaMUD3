"""
RP Conversation Context for OrekaMUD3.

Manages room-level RP conversation buffers and per-NPC rpsay memory.
When players use 'rpsay', the conversation history is tracked per room
so NPCs can build on what was said. NPC memories of rpsay conversations
are persisted using the existing npc_memories system.
"""

import time
import logging
from collections import defaultdict, deque

logger = logging.getLogger("OrekaMUD.RPContext")

# Max lines to keep in a room's RP buffer
MAX_BUFFER_SIZE = 20
# How long before a room buffer expires (seconds) — 10 minutes
BUFFER_EXPIRY = 600


class RPExchange:
    """A single line in an RP conversation."""
    __slots__ = ('speaker', 'text', 'timestamp', 'is_npc')

    def __init__(self, speaker: str, text: str, is_npc: bool = False):
        self.speaker = speaker
        self.text = text
        self.timestamp = time.time()
        self.is_npc = is_npc

    def format(self):
        tag = "[NPC]" if self.is_npc else "[Player]"
        return f"{tag} {self.speaker}: {self.text}"


class RoomRPBuffer:
    """Conversation buffer for a single room."""

    def __init__(self):
        self.exchanges: deque = deque(maxlen=MAX_BUFFER_SIZE)
        self.last_activity: float = 0

    def add(self, speaker: str, text: str, is_npc: bool = False):
        self.exchanges.append(RPExchange(speaker, text, is_npc))
        self.last_activity = time.time()

    def is_expired(self) -> bool:
        return time.time() - self.last_activity > BUFFER_EXPIRY

    def get_context(self, limit: int = 10) -> str:
        """Return formatted conversation context for AI prompts."""
        if self.is_expired():
            self.exchanges.clear()
            return ""
        recent = list(self.exchanges)[-limit:]
        if not recent:
            return ""
        lines = ["[Recent RP conversation in this room:]"]
        for ex in recent:
            lines.append(ex.format())
        return "\n".join(lines)

    def get_npc_last_line(self, npc_name: str) -> str:
        """Get the last thing a specific NPC said."""
        for ex in reversed(self.exchanges):
            if ex.is_npc and ex.speaker.lower() == npc_name.lower():
                return ex.text
        return ""

    def clear_if_expired(self):
        if self.is_expired():
            self.exchanges.clear()


class RPContextManager:
    """Manages RP conversation buffers for all rooms."""

    def __init__(self):
        self._buffers: dict = {}  # room_vnum -> RoomRPBuffer

    def get_buffer(self, room_vnum: int) -> RoomRPBuffer:
        if room_vnum not in self._buffers:
            self._buffers[room_vnum] = RoomRPBuffer()
        buf = self._buffers[room_vnum]
        buf.clear_if_expired()
        return buf

    def add_player_line(self, room_vnum: int, player_name: str, text: str):
        buf = self.get_buffer(room_vnum)
        buf.add(player_name, text, is_npc=False)

    def add_npc_line(self, room_vnum: int, npc_name: str, text: str):
        buf = self.get_buffer(room_vnum)
        buf.add(npc_name, text, is_npc=True)

    def get_context(self, room_vnum: int, limit: int = 10) -> str:
        buf = self.get_buffer(room_vnum)
        return buf.get_context(limit)

    def get_npc_last_line(self, room_vnum: int, npc_name: str) -> str:
        buf = self.get_buffer(room_vnum)
        return buf.get_npc_last_line(npc_name)

    def cleanup(self):
        """Remove expired buffers to free memory."""
        expired = [vnum for vnum, buf in self._buffers.items() if buf.is_expired()]
        for vnum in expired:
            del self._buffers[vnum]


# Singleton
_rp_context_manager = None


def get_rp_context() -> RPContextManager:
    global _rp_context_manager
    if _rp_context_manager is None:
        _rp_context_manager = RPContextManager()
    return _rp_context_manager


def save_rpsay_memory(npc, player_name: str, player_said: str, npc_said: str):
    """Persist an rpsay exchange to the NPC's memory of this player."""
    try:
        from src.chat_context import save_npc_memory
        npc_vnum = getattr(npc, 'vnum', 0)
        memory_text = f"[RP overheard] {player_name} said: \"{player_said}\" — I replied: \"{npc_said}\""
        save_npc_memory(npc_vnum, player_name, memory_text, importance=0.4, session_id="rpsay")
    except Exception as e:
        logger.debug(f"Failed to save rpsay memory: {e}")


def load_rpsay_memories(npc, player_name: str) -> str:
    """Load NPC's memories of rpsay conversations with a player."""
    try:
        from src.chat_context import load_npc_memory
        npc_vnum = getattr(npc, 'vnum', 0)
        memories = load_npc_memory(npc_vnum, player_name)
        rp_memories = [m for m in memories if m.get("text", "").startswith("[RP overheard]")]
        if not rp_memories:
            return ""
        lines = ["[Your past RP exchanges with this player:]"]
        for m in rp_memories[:3]:
            lines.append(m["text"])
        return "\n".join(lines)
    except Exception:
        return ""
