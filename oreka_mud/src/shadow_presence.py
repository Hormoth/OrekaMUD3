"""
Shadow Presence System for OrekaMUD3.
When a Veil player starts an AI NPC chat, they appear as a dreaming
presence in the live MUD world. Real players can see and interact with them.
"""
import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, List
import logging

logger = logging.getLogger("OrekaMUD.Shadow")


@dataclass
class ShadowPresence:
    """A player who exists in the world as a dreaming presence during AI chat."""
    player_id: str
    player_name: str
    npc_id: int
    npc_name: str
    room_vnum: int
    conversation_history: list = field(default_factory=list)
    visible: bool = True
    materialized: bool = False
    created_at: float = field(default_factory=time.time)

    def room_description(self) -> str:
        """How this shadow appears in room 'look' output."""
        return (
            f"{self.player_name} stands nearby, lost in "
            f"quiet conversation with {self.npc_name}. "
            f"Their eyes are distant, as if seeing something "
            f"only they can perceive."
        )

    def kin_sense_entry(self) -> dict:
        """Shadow presences register as 'echo' resonance on Kin-sense."""
        return {
            "name": self.player_name,
            "resonance": "echo",
            "strength": "faint",
            "description": "a presence that feels both near and far"
        }

    def inject_player_speech(self, speaker: str, text: str):
        """A real MUD player speaks in the room — inject into AI conversation context."""
        self.conversation_history.append({
            "role": "system",
            "content": (
                f"[WORLD EVENT] {speaker} says nearby: \"{text}\". "
                f"You and {self.npc_name} can both hear this."
            )
        })

    def inject_combat(self, description: str):
        """Combat starts nearby — inject into AI context."""
        self.conversation_history.append({
            "role": "system",
            "content": f"[WORLD EVENT] Nearby: {description}."
        })

    def inject_room_event(self, event_text: str):
        """Generic world event — inject into AI context."""
        self.conversation_history.append({
            "role": "system",
            "content": f"[WORLD EVENT] {event_text}"
        })


class ShadowPresenceManager:
    """Global manager for all shadow presences in the world."""

    def __init__(self):
        self.shadows = {}  # {player_id: ShadowPresence}

    def create(self, player_id: str, player_name: str,
               npc_id: int, npc_name: str, room_vnum: int) -> ShadowPresence:
        """Create a shadow presence when a Veil player starts AI chat."""
        shadow = ShadowPresence(
            player_id=player_id,
            player_name=player_name,
            npc_id=npc_id,
            npc_name=npc_name,
            room_vnum=room_vnum
        )
        self.shadows[player_id] = shadow
        logger.info(f"Shadow created: {player_name} at room {room_vnum} with {npc_name}")
        return shadow

    def get_by_room(self, room_vnum: int) -> List[ShadowPresence]:
        """Get all shadow presences in a specific room."""
        return [s for s in self.shadows.values() if s.room_vnum == room_vnum]

    def get_by_player(self, player_id: str) -> Optional[ShadowPresence]:
        """Get a specific player's shadow."""
        return self.shadows.get(player_id)

    def broadcast_speech(self, room_vnum: int, speaker: str, text: str):
        """Called when someone uses 'say' in a room with shadows."""
        for shadow in self.get_by_room(room_vnum):
            shadow.inject_player_speech(speaker, text)

    def broadcast_combat(self, room_vnum: int, description: str):
        """Called when combat occurs in a room with shadows."""
        for shadow in self.get_by_room(room_vnum):
            shadow.inject_combat(description)

    def broadcast_event(self, room_vnum: int, event_text: str):
        """Called for generic room events."""
        for shadow in self.get_by_room(room_vnum):
            shadow.inject_room_event(event_text)

    def materialize(self, player_id: str) -> Optional[ShadowPresence]:
        """Player clicks 'Enter World' in Veil — mark as materialized."""
        shadow = self.shadows.get(player_id)
        if shadow:
            shadow.materialized = True
            logger.info(f"Shadow materialized: {shadow.player_name}")
        return shadow

    def remove(self, player_id: str) -> Optional[ShadowPresence]:
        """Remove a shadow (player disconnected or materialized)."""
        shadow = self.shadows.pop(player_id, None)
        if shadow:
            logger.info(f"Shadow removed: {shadow.player_name}")
        return shadow

    def get_all(self) -> dict:
        """Get all active shadows."""
        return dict(self.shadows)


# Global singleton
shadow_manager = ShadowPresenceManager()
