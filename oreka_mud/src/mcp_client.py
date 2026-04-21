"""
MCP Client — calls Veil MCP tools from inside the MUD.

Provides async methods for the MUD's AI systems to query:
  - Lore search (RAG via pgvector)
  - NPC memory recall
  - Room semantic search
  - NPC profile data
  - Player data enrichment

All calls go to the Veil Gateway API on localhost:8300, which has
the PostgreSQL + Ollama connections needed for these operations.
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger("OrekaMUD.MCPClient")

GATEWAY_URL = os.getenv("VEIL_GATEWAY_URL", "http://127.0.0.1:8300")

# Lazy-loaded httpx client
_client = None


def _get_client():
    """Lazy-init async HTTP client."""
    global _client
    if _client is None:
        try:
            import httpx
            _client = httpx.AsyncClient(
                base_url=GATEWAY_URL,
                timeout=30.0,
            )
        except ImportError:
            logger.warning("httpx not installed — MCP client disabled")
    return _client


async def search_lore(query: str, limit: int = 5, include_dm: bool = False) -> list[dict]:
    """Search lore chunks via pgvector semantic similarity.

    Returns list of { source, section, content, similarity }.
    Used by NPC conversations and DM agent for grounded responses.
    """
    client = _get_client()
    if not client:
        return []
    try:
        resp = await client.post("/api/mcp/search_lore", json={
            "query": query,
            "limit": limit,
            "include_dm": include_dm,
        })
        if resp.status_code == 200:
            return resp.json().get("results", [])
        logger.warning("search_lore failed (%d): %s", resp.status_code, resp.text[:200])
    except Exception as e:
        logger.warning("search_lore error: %s", e)
    return []


async def recall_npc_memories(npc_id: str, player_id: str,
                               query: str, limit: int = 5) -> list[dict]:
    """Recall NPC memories relevant to a conversation context.

    Returns list of { memory_text, importance, similarity }.
    Used by NPCConversation to maintain continuity across sessions.
    """
    client = _get_client()
    if not client:
        return []
    try:
        resp = await client.post("/api/mcp/recall_memories", json={
            "npc_id": npc_id,
            "player_id": player_id,
            "query": query,
            "limit": limit,
        })
        if resp.status_code == 200:
            return resp.json().get("memories", [])
    except Exception as e:
        logger.warning("recall_npc_memories error: %s", e)
    return []


async def store_npc_memory(npc_id: str, player_id: str,
                            memory_text: str, importance: float = 0.5) -> bool:
    """Store a new NPC memory after a conversation exchange.

    Called after meaningful NPC interactions to build long-term memory.
    """
    client = _get_client()
    if not client:
        return False
    try:
        resp = await client.post("/api/mcp/store_memory", json={
            "npc_id": npc_id,
            "player_id": player_id,
            "memory_text": memory_text,
            "importance": importance,
        })
        return resp.status_code == 200
    except Exception as e:
        logger.warning("store_npc_memory error: %s", e)
    return False


async def search_rooms(query: str, limit: int = 10) -> list[dict]:
    """Semantic search for rooms matching a description.

    Used by DM agent for finding thematically appropriate locations.
    """
    client = _get_client()
    if not client:
        return []
    try:
        resp = await client.post("/api/mcp/search_rooms", json={
            "query": query,
            "limit": limit,
        })
        if resp.status_code == 200:
            return resp.json().get("rooms", [])
    except Exception as e:
        logger.warning("search_rooms error: %s", e)
    return []


async def get_npc_profile(npc_vnum: int) -> Optional[dict]:
    """Get AI-ready NPC profile from the database.

    Returns personality, knowledge_topics, faction, alignment, etc.
    """
    client = _get_client()
    if not client:
        return None
    try:
        resp = await client.get(f"/api/mcp/npc/{npc_vnum}")
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        logger.warning("get_npc_profile error: %s", e)
    return None


async def log_player_event(player_name: str, event_type: str,
                            event_data: dict = None,
                            room_id: int = None, region: str = None) -> bool:
    """Log a player event for analytics and DM agent context.

    Event types: combat_start, combat_end, quest_complete, room_discover,
    npc_talk, death, level_up, faction_change, deity_prayer, etc.
    """
    client = _get_client()
    if not client:
        return False
    try:
        resp = await client.post("/api/mcp/log_event", json={
            "player_name": player_name,
            "event_type": event_type,
            "event_data": event_data or {},
            "room_id": room_id,
            "region": region,
        })
        return resp.status_code == 200
    except Exception as e:
        logger.warning("log_player_event error: %s", e)
    return False


async def get_recent_events(player_name: str = None, event_type: str = None,
                             region: str = None, limit: int = 20) -> list[dict]:
    """Get recent player events for DM agent narrative context."""
    client = _get_client()
    if not client:
        return []
    try:
        params = {"limit": limit}
        if player_name:
            params["player_name"] = player_name
        if event_type:
            params["event_type"] = event_type
        if region:
            params["region"] = region
        resp = await client.get("/api/mcp/events", params=params)
        if resp.status_code == 200:
            return resp.json().get("events", [])
    except Exception as e:
        logger.warning("get_recent_events error: %s", e)
    return []


async def close():
    """Clean up the HTTP client on shutdown."""
    global _client
    if _client:
        await _client.aclose()
        _client = None
