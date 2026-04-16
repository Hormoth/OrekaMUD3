"""Unified prompt pipeline for NPC conversations.

ONE function assembles the prompt for BOTH the MUD ``talk``/``chat``
commands AND the standalone NPC chat room.  Both entry points call
``build_npc_prompt()`` and get back an identical prompt structure.
Both write to the same memory files.  No drift.

Prompt assembly order (position matters — see AI Dungeon research):

    1.  NPC identity (name, description, type)
    2.  NPC persona (if enriched persona exists: activity, mood,
        relationships, quirks, opinions, emotional needs, secrets)
    3.  Example dialogues (teaches voice)
    4.  Room ambience
    5.  Player dossier (reputation, rescues, tags)
    6.  NPC memory of this player (cross-session)
    7.  Lorebook entries (keyword-triggered, only relevant lore)
    8.  Conversation history (last 8-10 turns)
    9.  Rules (no brackets, first person, no meta)
    10. Author's Note (tone/style — positioned NEAR END for max influence)
    11. Player's message
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("OrekaMUD.PromptPipeline")


# ---------------------------------------------------------------------------
# NPC memory I/O (persistent cross-session memory per NPC per player)
# ---------------------------------------------------------------------------

_MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "data",
                           "npc_memories")


def _memory_path(npc_vnum: int, player_name: str) -> str:
    npc_dir = os.path.join(_MEMORY_DIR, str(npc_vnum))
    os.makedirs(npc_dir, exist_ok=True)
    safe_name = "".join(c for c in player_name if c.isalnum() or c in "._-")
    return os.path.join(npc_dir, f"{safe_name}.json")


def load_npc_memory(npc_vnum: int, player_name: str) -> List[str]:
    """Load persistent facts this NPC remembers about this player."""
    path = _memory_path(npc_vnum, player_name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("facts", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_npc_memory(npc_vnum: int, player_name: str,
                    facts: List[str]) -> None:
    """Save persistent facts.  Keeps the last 20 facts."""
    path = _memory_path(npc_vnum, player_name)
    facts = facts[-20:]  # cap
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"player": player_name, "facts": facts,
                       "updated": time.time()}, f, indent=2)
    except Exception as e:
        logger.debug("NPC memory save failed: %s", e)


# ---------------------------------------------------------------------------
# Enriched persona loader
# ---------------------------------------------------------------------------

_PERSONA_PATH = os.path.join(os.path.dirname(__file__), "..", "data",
                             "npc_personas.json")
_personas: Optional[Dict[str, Any]] = None


def _load_personas() -> Dict[str, Any]:
    global _personas
    if _personas is not None:
        return _personas
    try:
        with open(_PERSONA_PATH, "r", encoding="utf-8") as f:
            _personas = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _personas = {}
    return _personas


def get_enriched_persona(npc) -> Optional[Dict[str, Any]]:
    """Look up an enriched persona by mob vnum or name."""
    personas = _load_personas()
    vnum = getattr(npc, "vnum", None)
    name = getattr(npc, "name", "")

    # Try by vnum first
    if vnum is not None:
        for pid, pdata in personas.items():
            if pdata.get("mob_vnum") == vnum:
                return pdata

    # Fallback: fuzzy name match
    name_lower = name.lower()
    for pid, pdata in personas.items():
        if pdata.get("name", "").lower() in name_lower or \
           name_lower in pdata.get("name", "").lower():
            return pdata

    return None


# ---------------------------------------------------------------------------
# The unified prompt builder
# ---------------------------------------------------------------------------

def build_npc_prompt(
    npc,
    player,
    message: str,
    room=None,
    conversation_history: Optional[List[Tuple[str, str]]] = None,
    mode: str = "talk",
) -> Tuple[str, str]:
    """Assemble the full (system_prompt, user_message) pair for an NPC
    conversation turn.

    Returns (system_prompt, user_prompt) ready to pass to the LLM.
    Both MUD talk/chat and the standalone chat room call this.
    """
    parts: List[str] = []

    npc_name = getattr(npc, "name", "NPC")
    npc_vnum = getattr(npc, "vnum", 0)
    npc_type = getattr(npc, "npc_type", None) or getattr(npc, "type_", "")
    player_name = getattr(player, "name", "Visitor")

    # Try to load enriched persona
    persona = get_enriched_persona(npc)

    # ── 1. NPC IDENTITY ──────────────────────────────────────────────
    if persona:
        parts.append(f"You are {persona.get('name', npc_name)}.")
        if persona.get("short_description"):
            parts.append(persona["short_description"])
    else:
        parts.append(f"You are {npc_name}, a {npc_type or 'figure'} in Oreka.")
        desc = getattr(npc, "description", "")
        if desc:
            parts.append(desc[:300])

    # ── 2. ENRICHED PERSONA FIELDS ───────────────────────────────────
    if persona:
        if persona.get("current_activity"):
            parts.append(f"\nRIGHT NOW: {persona['current_activity']}")
        if persona.get("mood"):
            parts.append(f"MOOD: {persona['mood']}")
        if persona.get("relationships"):
            rel_lines = []
            for r in persona["relationships"][:5]:
                rel_lines.append(f"  {r['name']}: {r['feeling']}")
            parts.append("PEOPLE YOU KNOW:\n" + "\n".join(rel_lines))
        if persona.get("verbal_quirks"):
            parts.append("YOUR SPEECH HABITS: " +
                         "; ".join(persona["verbal_quirks"][:5]))
        if persona.get("opinions"):
            parts.append("YOUR OPINIONS: " +
                         "; ".join(persona["opinions"][:4]))
        if persona.get("emotional_needs"):
            parts.append(f"WHAT YOU WANT (but won't ask): {persona['emotional_needs']}")

        # Secrets gated by player reputation
        if persona.get("secrets"):
            player_rep = getattr(player, "reputation", {}) or {}
            # Determine trust level from rep with NPC's faction
            # (simplified: check if any faction rep > threshold)
            max_rep = max(player_rep.values()) if player_rep else 0
            for secret in persona["secrets"]:
                threshold_map = {"friendly": 100, "honored": 300,
                                 "allied": 600, "revered": 1000}
                req = threshold_map.get(secret.get("trust", "allied"), 600)
                if max_rep >= req:
                    parts.append(f"SECRET (you may reveal if trust is right): "
                                 f"{secret['secret']}")
    else:
        # Fallback: use existing ai_persona if available
        ai_persona = getattr(npc, "ai_persona", None)
        if ai_persona:
            if isinstance(ai_persona, dict):
                for k in ("voice", "speech_style", "motivation",
                           "knowledge_domains"):
                    v = ai_persona.get(k)
                    if v:
                        parts.append(f"{k}: {v}")

    # ── 3. EXAMPLE DIALOGUES ─────────────────────────────────────────
    if persona and persona.get("definition_examples"):
        parts.append("\nEXAMPLES OF HOW YOU SPEAK:")
        for ex in persona["definition_examples"][:5]:
            user_line = ex.get("user", "")
            char_line = ex.get("char", "")
            parts.append(f"Player: \"{user_line}\"")
            parts.append(f"{npc_name}: \"{char_line}\"")

    # ── 4. ROOM AMBIENCE ─────────────────────────────────────────────
    if room:
        room_name = getattr(room, "name", "")
        ambience = getattr(room, "ambience", None)
        if ambience:
            amb = ambience.to_dict() if hasattr(ambience, "to_dict") else ambience
            amb_parts = [f"LOCATION: {room_name}"]
            if amb.get("mood"):
                amb_parts.append(f"Atmosphere: {amb['mood']}")
            for field in ("sounds", "smells"):
                vals = amb.get(field) or []
                if vals:
                    amb_parts.append(f"{field}: {', '.join(vals[:3])}")
            parts.append("\n".join(amb_parts))
        elif room_name:
            parts.append(f"LOCATION: {room_name}")

    # ── 5. PLAYER DOSSIER ────────────────────────────────────────────
    try:
        from src.character_dossier import build_dossier_prompt_block
        dossier = build_dossier_prompt_block(player)
        if dossier:
            parts.append(f"\n{dossier}")
    except Exception:
        # Minimal fallback
        parts.append(f"\nPLAYER: {player_name}, level "
                     f"{getattr(player, 'level', '?')} "
                     f"{getattr(player, 'race', '?')}")

    # ── 6. NPC MEMORY OF THIS PLAYER ─────────────────────────────────
    facts = load_npc_memory(npc_vnum, player_name)
    if facts:
        parts.append(f"\nWHAT YOU REMEMBER ABOUT {player_name.upper()}:")
        for fact in facts[-5:]:
            parts.append(f"  - {fact}")

    # ── 7. LOREBOOK (keyword-triggered lore) ─────────────────────────
    # Scan both the current message and recent history for keywords
    lore_scan_text = message
    if conversation_history:
        recent = conversation_history[-6:]
        lore_scan_text += " " + " ".join(
            f"{role}: {text}" for role, text in recent
        )
    try:
        from src.lorebook import build_lore_block
        lore_block = build_lore_block(lore_scan_text, max_total_tokens=800)
        if lore_block:
            parts.append(lore_block)
    except Exception as e:
        logger.debug("Lorebook injection failed: %s", e)

    # ── 8. CONVERSATION HISTORY ──────────────────────────────────────
    if conversation_history:
        recent = conversation_history[-10:]
        if recent:
            parts.append("\nRECENT CONVERSATION:")
            for role, text in recent:
                speaker = player_name if role == "player" else npc_name
                parts.append(f"  {speaker}: \"{text}\"")

    # ── 9. RULES ─────────────────────────────────────────────────────
    parts.append("\nRULES:")
    parts.append("- Stay in character. Always speak in first person as yourself.")
    parts.append("- Never narrate your own actions in third person.")
    parts.append("- Never include bracketed stage directions, DM notes, or meta-commentary.")
    parts.append("- No asterisks for actions. No markdown formatting.")
    parts.append("- Never mention: AI, language model, game, hit points, dice, stats, NPC.")
    if mode == "talk":
        parts.append("- Respond in 1-3 sentences unless the player asks for detail.")
    else:
        parts.append("- Respond in 2-4 sentences unless the player asks for detail.")

    # ── 10. AUTHOR'S NOTE (positioned NEAR END for max influence) ────
    if persona and persona.get("authors_note"):
        parts.append(f"\n[Author's Note: {persona['authors_note']}]")

    system_prompt = "\n".join(parts)

    # ── 11. PLAYER'S MESSAGE ─────────────────────────────────────────
    user_prompt = f"{player_name}: {message}"

    return system_prompt, user_prompt


# ---------------------------------------------------------------------------
# Post-conversation memory extraction
# ---------------------------------------------------------------------------

def extract_and_save_memory(npc, player, conversation_history: List[Tuple[str, str]]) -> None:
    """After a conversation ends (or periodically), extract key facts
    the NPC learned about the player and persist them.

    Simple heuristic: save the last 3 player messages as "things the
    player mentioned."  A future version could use LLM summarization.
    """
    if not conversation_history:
        return
    npc_vnum = getattr(npc, "vnum", 0)
    player_name = getattr(player, "name", "Visitor")

    existing = load_npc_memory(npc_vnum, player_name)

    # Extract player messages from recent history
    player_msgs = [text for role, text in conversation_history
                   if role == "player" and len(text) > 10]
    # Keep last 3 as new facts
    new_facts = [f"Said: \"{msg[:100]}\"" for msg in player_msgs[-3:]]
    if new_facts:
        timestamp = time.strftime("%Y-%m-%d")
        new_facts = [f"[{timestamp}] {f}" for f in new_facts]
        combined = existing + new_facts
        save_npc_memory(npc_vnum, player_name, combined)
