"""
Chat Context Builder for OrekaMUD3.
Builds the AI prompt context for chat sessions, manages NPC memory,
and executes game actions from AI responses.
"""

import json
import os
import time
import logging
from typing import Optional

logger = logging.getLogger("OrekaMUD.ChatContext")

MEMORIES_DIR = os.path.join("data", "npc_memories")
os.makedirs(MEMORIES_DIR, exist_ok=True)


# =========================================================================
# NPC Memory System
# =========================================================================

def load_npc_memory(npc_vnum: int, player_name: str) -> list:
    """Load NPC's memories of a specific player. Returns top 5 by importance."""
    filepath = _memory_path(npc_vnum, player_name)
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        memories = data.get("memories", [])
        # Sort by importance descending, return top 5
        memories.sort(key=lambda m: m.get("importance", 0), reverse=True)
        return memories[:5]
    except Exception as e:
        logger.error(f"Failed to load NPC memory: {e}")
        return []


def save_npc_memory(npc_vnum: int, player_name: str, memory_text: str,
                    importance: float = 0.3, session_id: str = ""):
    """Save a memory for an NPC about a player."""
    filepath = _memory_path(npc_vnum, player_name)

    # Load existing
    data = {"npc_vnum": npc_vnum, "player_name": player_name,
            "memories": [], "last_interaction": 0, "total_sessions": 0}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except Exception:
            pass

    # Append new memory
    data["memories"].append({
        "text": memory_text,
        "importance": importance,
        "session_id": session_id,
        "created_at": time.time(),
    })
    data["last_interaction"] = time.time()

    # Keep only top 20 memories by importance
    data["memories"].sort(key=lambda m: m.get("importance", 0), reverse=True)
    data["memories"] = data["memories"][:20]

    # Ensure directory exists
    npc_dir = os.path.join(MEMORIES_DIR, str(npc_vnum))
    os.makedirs(npc_dir, exist_ok=True)

    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save NPC memory: {e}")


def _memory_path(npc_vnum: int, player_name: str) -> str:
    return os.path.join(MEMORIES_DIR, str(npc_vnum), f"{player_name}.json")


def calculate_importance(response: dict) -> float:
    """Score importance of an AI response for memory storage."""
    score = 0.3  # Base

    # Game actions increase importance
    actions = response.get("game_actions", [])
    score += min(len(actions) * 0.2, 0.6)

    # Key terms increase importance
    memory_text = response.get("remember", "") or ""
    key_terms = ["quest", "deity", "faction", "secret", "alliance",
                 "enemy", "betrayal", "oath", "promise", "war"]
    term_hits = sum(1 for t in key_terms if t in memory_text.lower())
    score += min(term_hits * 0.05, 0.3)

    # Longer memories are slightly more important
    word_count = len(memory_text.split())
    if word_count > 20:
        score += 0.1
    elif word_count > 10:
        score += 0.05

    return min(score, 1.0)


# =========================================================================
# Context Builder
# =========================================================================

def build_chat_context(player, npc, session) -> dict:
    """
    Build the full AI context payload for a chat session.
    Returns {system: str, messages: list, world_events: list}
    """
    persona = getattr(npc, 'ai_persona', None) or {}

    # Build system prompt layers
    system_parts = []

    # Layer 1: NPC Identity
    npc_name = getattr(npc, 'name', 'Unknown')
    system_parts.append(f"You are {npc_name}, an NPC in the world of Oreka.")

    # Voice / personality
    if persona.get("voice"):
        system_parts.append(f"\nIDENTITY:\n{persona['voice']}")
    else:
        system_parts.append(f"\nIDENTITY:\n{_build_default_personality(npc)}")

    # Motivation
    if persona.get("motivation"):
        system_parts.append(f"Motivation: {persona['motivation']}")

    # Knowledge domains
    if persona.get("knowledge_domains"):
        domains = ", ".join(persona["knowledge_domains"])
        system_parts.append(f"Knowledge: {domains}")

    # Speech style
    if persona.get("speech_style"):
        system_parts.append(f"Speech style: {persona['speech_style']}")

    # Layer 2: World Context
    system_parts.append(f"\nWORLD CONTEXT:")
    system_parts.append(f"Region: {session.anchor_region}")
    system_parts.append(f"Room: {session.anchor_room_name}")
    try:
        from src.schedules import get_game_time
        game_time = get_game_time()
        system_parts.append(f"Time: {game_time.get_full_time_string()}")
    except Exception:
        pass

    # Room effects
    room = None
    try:
        from src.world import get_world
        world = get_world()
        room = world.rooms.get(session.anchor_room_vnum)
        if room and getattr(room, 'effects', None):
            effects = ", ".join(str(e) for e in room.effects)
            system_parts.append(f"Active room effects: {effects}")
    except Exception:
        pass

    # Layer 3: Player Context
    system_parts.append(f"\nPLAYER CONTEXT:")
    system_parts.append(f"Name: {session.player_name}")
    system_parts.append(f"Race: {session.player_race}")
    system_parts.append(f"Class: {session.player_class}, Level {session.player_level}")
    if session.player_deity:
        system_parts.append(f"Deity: {session.player_deity}")

    # Faction standings relevant to this NPC
    npc_faction = getattr(npc, 'faction', None) or persona.get("faction")
    if session.player_factions:
        relevant = {}
        faction_attitudes = persona.get("faction_attitudes", {})
        for faction, rep in session.player_factions.items():
            if faction in faction_attitudes or faction == npc_faction:
                relevant[faction] = rep
        if relevant:
            faction_lines = [f"  {f}: {r}" for f, r in relevant.items()]
            system_parts.append("Faction standings:\n" + "\n".join(faction_lines))

    # Layer 4: NPC Memory
    memories = load_npc_memory(npc.vnum if hasattr(npc, 'vnum') else 0,
                               session.player_name)
    if memories:
        memory_lines = [m["text"] for m in memories]
        system_parts.append(f"\nNPC MEMORY OF THIS PLAYER:\n" +
                            "\n".join(f"- {m}" for m in memory_lines))
    else:
        system_parts.append("\nNPC MEMORY OF THIS PLAYER:\nNo prior interaction.")

    # Layer 5: Forbidden topics
    forbidden = persona.get("forbidden_topics", [])
    if forbidden:
        system_parts.append(f"\nForbidden topics: {', '.join(forbidden)}")

    # Layer 5b: YOUR QUESTS — the closed set this NPC may actually offer.
    # Prevents hallucinated quests and "go see the quest hall" referrals.
    quest_roster = _build_quest_roster(player, npc)
    session._quest_roster_ids = {q["quest_id"] for q in quest_roster}
    if quest_roster:
        lines = [f"- id={q['quest_id']} | {q['title']}: {q['hook']}" for q in quest_roster]
        system_parts.append(
            "\nYOUR QUESTS (the ONLY quests you may offer this player):\n"
            + "\n".join(lines)
        )
    else:
        system_parts.append(
            "\nYOUR QUESTS: YOU HAVE NO QUESTS TO OFFER THIS PLAYER.\n"
            "If they ask for work, say so plainly in character. "
            "Do NOT invent a quest. Do NOT direct them to a quest hall, "
            "quest desk, quest master, or quest board — none exist."
        )

    # Layer 5c: KNOWN PEOPLE — real NPCs in this NPC's room and adjacent rooms.
    # The NPC may only refer the player to people on this list.
    known_people = _build_known_people(npc, player)
    if known_people:
        lines = [f"- {p['name']} — {p['role']}" for p in known_people]
        system_parts.append(
            "\nKNOWN PEOPLE (real individuals nearby — only refer the "
            "player to names on this list):\n" + "\n".join(lines)
        )

    # Layer 6: Rules
    system_parts.append(f"""
RULES:
- Stay in character. Never mention being an AI, a game, hit points, dice, or stats.
- Speak as {npc_name} would speak.
- Respond in 2-4 sentences unless the player asks something requiring detail.
- You may trigger game actions by including them in your JSON response.
- If world events are injected, react to them naturally as your character would.
- ONLY offer quests listed in YOUR QUESTS above. If the list is empty or no
  quest fits, refuse plainly — do NOT invent a quest or a quest-giver.
- There is NO quest hall, quest desk, quest master, quest board, or adventurer
  guild administrator in this world. Never direct the player to one.
- Only name or refer the player to people listed under KNOWN PEOPLE, or to
  canonical named figures you already know from the world's lore. Never
  invent an NPC name on the spot.
- If you don't know something, say you don't know — don't fabricate.

RESPONSE FORMAT (JSON):
{{"dialogue": "Your in-character speech", "game_actions": [], "emotion_state": "neutral", "remember": null}}

Valid game_actions types: modify_reputation, grant_quest, give_item, take_item, set_condition, send_message
For grant_quest, quest_id MUST be one of the ids listed under YOUR QUESTS.
Valid emotion_state values: neutral, happy, angry, sad, afraid, suspicious, reverent, excited, troubled""")

    system = "\n".join(system_parts)

    # Build message history
    messages = []
    for entry in session.get_conversation_messages(limit=20):
        role = entry.get("role", "user")
        content = entry.get("content", "")
        if role in ("user", "assistant", "system"):
            messages.append({"role": role, "content": content})

    # Include recent world events in context
    world_events = session.get_recent_world_events(limit=5)

    return {
        "system": system,
        "messages": messages,
        "world_events": world_events,
    }


# =========================================================================
# Anti-hallucination helpers
# =========================================================================

# Phrases an AI NPC must never use — none of these exist in the world.
FORBIDDEN_REFERRAL_PATTERNS = (
    "quest hall", "quest desk", "quest master", "quest board",
    "adventurer's guild", "adventurers guild", "adventurer guild",
    "guild hall front desk", "quest giver at the",
)


def _build_quest_roster(player, npc) -> list:
    """Return the closed set of quests this NPC may offer this player now.

    Merges hidden quests (from hidden_quests.json, rep-gated) with regular
    quests (from QuestManager, prerequisite/level-gated). Each entry has
    ``quest_id``, ``title``, ``hook`` — the minimum the LLM needs to
    describe the hook in character.
    """
    roster = []
    seen = set()

    try:
        from src.quest_reveal import check_for_reveals
        for q in check_for_reveals(player, npc):
            qid = str(q.get("id", "")).strip()
            if not qid or qid in seen:
                continue
            seen.add(qid)
            roster.append({
                "quest_id": qid,
                "title": q.get("title", qid.replace("_", " ").title()),
                "hook": q.get("hook", ""),
            })
    except Exception as e:
        logger.debug(f"hidden quest roster failed: {e}")

    try:
        from src.quests import get_quest_manager
        qm = get_quest_manager()
        quest_log = getattr(player, 'quest_log', None)
        if quest_log:
            for q in qm.get_available_quests(player, quest_log,
                                             npc_name=getattr(npc, 'name', '')):
                qid = str(q.id)
                if qid in seen:
                    continue
                seen.add(qid)
                roster.append({
                    "quest_id": qid,
                    "title": q.name,
                    "hook": q.description[:180] if q.description else "",
                })
    except Exception as e:
        logger.debug(f"regular quest roster failed: {e}")

    return roster


def _build_known_people(npc, player) -> list:
    """Return a short list of real NPCs in the same room and adjacent rooms.

    The LLM must only refer the player to people on this list — stops the
    "go see the quest hall front desk" hallucinations. Capped at 30 to
    keep the prompt compact.
    """
    room = getattr(npc, 'room', None) or getattr(player, 'room', None)
    if room is None:
        return []

    world = getattr(room, '_world', None)
    seen = set()
    people = []

    def _add(mob, here=False):
        name = getattr(mob, 'name', '')
        if not name or name in seen or mob is npc:
            return
        seen.add(name)
        flags = getattr(mob, 'flags', []) or []
        role_bits = []
        for flag in ('shopkeeper', 'trainer', 'banker', 'blacksmith',
                     'guard', 'innkeeper', 'quest_giver', 'family_rep'):
            if flag in flags:
                role_bits.append(flag.replace('_', ' '))
        npc_type = getattr(mob, 'type_', '') or ''
        if npc_type and npc_type not in role_bits:
            role_bits.insert(0, npc_type)
        if not role_bits:
            role_bits.append("resident")
        location = "here" if here else "nearby"
        people.append({"name": name, "role": f"{', '.join(role_bits)} — {location}"})

    for mob in getattr(room, 'mobs', []):
        if getattr(mob, 'alive', True):
            _add(mob, here=True)

    if world is not None:
        for direction, target in getattr(room, 'exits', {}).items():
            if len(people) >= 30:
                break
            target_vnum = target if isinstance(target, int) else getattr(target, 'vnum', None)
            if target_vnum is None:
                continue
            adj = world.rooms.get(target_vnum)
            if not adj:
                continue
            for mob in getattr(adj, 'mobs', []):
                if len(people) >= 30:
                    break
                if getattr(mob, 'alive', True):
                    _add(mob, here=False)

    return people[:30]


def scrub_forbidden_referrals(text: str) -> tuple:
    """Return (scrubbed_text, found_phrases). Strips sentences containing
    forbidden quest-hall referrals — these never exist in the world.
    Called after AI dialogue generation as a safety net.
    """
    if not text:
        return text, []
    lowered = text.lower()
    hits = [p for p in FORBIDDEN_REFERRAL_PATTERNS if p in lowered]
    if not hits:
        return text, []

    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    kept = []
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(p in s_lower for p in FORBIDDEN_REFERRAL_PATTERNS):
            continue
        kept.append(sentence)
    scrubbed = " ".join(kept).strip()
    if not scrubbed:
        scrubbed = "I don't have work for you right now."
    return scrubbed, hits


def _build_default_personality(npc) -> str:
    """Build a default personality from mob fields when ai_persona is absent."""
    parts = []
    npc_type = getattr(npc, 'type_', '')
    if npc_type:
        parts.append(f"You are a {npc_type}.")
    flags = getattr(npc, 'flags', []) or []
    if 'shopkeeper' in flags:
        parts.append("You are a shopkeeper who buys and sells goods.")
    if 'guard' in flags:
        parts.append("You are a guard who protects this area.")
    if 'trainer' in flags:
        parts.append("You train adventurers in combat skills.")
    alignment = getattr(npc, 'alignment', '')
    if alignment:
        parts.append(f"Your alignment is {alignment}.")
    desc = getattr(npc, 'description', '')
    if desc:
        parts.append(f"Description: {desc[:200]}")
    dialogue = getattr(npc, 'dialogue', '')
    if dialogue:
        parts.append(f"Your typical greeting: \"{dialogue}\"")
    return " ".join(parts) if parts else "You are a resident of Oreka."


# =========================================================================
# Game Action Executor
# =========================================================================

async def execute_game_actions(player, npc, actions: list, session) -> list:
    """
    Execute game actions from an AI NPC response.
    Returns list of result messages to show the player.
    """
    results = []

    for action in actions:
        action_type = action.get("type", "")
        try:
            if action_type == "modify_reputation":
                msg = await _handle_reputation(player, action)
                if msg:
                    results.append(msg)

            elif action_type == "grant_quest":
                msg = _handle_quest_grant(player, action, session=session)
                if msg:
                    results.append(msg)

            elif action_type == "give_item":
                msg = _handle_give_item(player, npc, action)
                if msg:
                    results.append(msg)

            elif action_type == "take_item":
                msg = _handle_take_item(player, action)
                if msg:
                    results.append(msg)

            elif action_type == "set_condition":
                msg = _handle_set_condition(player, action)
                if msg:
                    results.append(msg)

            elif action_type == "send_message":
                msg = _handle_send_message(player, action)
                if msg:
                    results.append(msg)

            else:
                logger.warning(f"Unknown game action type: {action_type}")
                continue

            # Log to session
            session.add_game_action(action)

        except Exception as e:
            logger.error(f"Failed to execute game action {action_type}: {e}")

    return results


async def _handle_reputation(player, action: dict) -> str:
    """Modify player's faction reputation."""
    faction = action.get("faction", "")
    amount = action.get("amount", 0)
    if not faction or not amount:
        return ""

    # Clamp amount
    amount = max(-100, min(100, amount))

    try:
        from src.factions import get_faction_manager
        fm = get_faction_manager()
        fm.modify_reputation(player, faction, amount, "NPC conversation")
        sign = "+" if amount > 0 else ""
        return (f"\033[1;33m[Action]\033[0m The {faction} will hear of this. "
                f"(Reputation {sign}{amount}: {faction})")
    except Exception as e:
        logger.error(f"Reputation change failed: {e}")
        # Fallback: modify directly
        if hasattr(player, 'reputation'):
            current = player.reputation.get(faction, 0)
            player.reputation[faction] = current + amount
            sign = "+" if amount > 0 else ""
            return (f"\033[1;33m[Action]\033[0m (Reputation {sign}{amount}: {faction})")
    return ""


def _handle_quest_grant(player, action: dict, session=None) -> str:
    """Grant a quest to the player — whitelisted against the NPC's roster.

    Rejects any quest_id not in the roster built at context time, so a
    hallucinated grant action from the LLM becomes a no-op instead of
    corrupting the player's quest log.
    """
    quest_id = str(action.get("quest_id", "") or "").strip()
    if not quest_id:
        return ""

    allowed = getattr(session, "_quest_roster_ids", None) if session else None
    if allowed is not None and quest_id not in allowed:
        logger.warning(
            f"Rejected hallucinated grant_quest: quest_id={quest_id!r} "
            f"not in NPC's roster ({sorted(allowed)[:5]}...)"
        )
        return ""

    try:
        from src.quests import get_quest_manager
        qm = get_quest_manager()
        if qm.accept_quest(player, quest_id):
            return (f"\033[1;34m[Action]\033[0m A quest has been marked in your journal: "
                    f"{quest_id.replace('_', ' ').title()}")
    except Exception:
        pass
    return ""


def _handle_give_item(player, npc, action: dict) -> str:
    """NPC gives an item to the player."""
    item_name = action.get("item", "")
    if not item_name:
        return ""
    # Try to find and give a real item
    try:
        from src.items import load_items_db, Item
        db = load_items_db()
        # Search by name
        for vnum, item_data in db.items():
            if item_name.lower() in str(item_data).lower():
                item = Item(**item_data) if isinstance(item_data, dict) else item_data
                player.inventory.append(item)
                npc_name = getattr(npc, 'name', 'The NPC')
                return (f"\033[1;32m[Action]\033[0m {npc_name} presses "
                        f"{getattr(item, 'name', item_name)} into your hand. "
                        f"(Item received: {getattr(item, 'name', item_name)})")
    except Exception:
        pass
    npc_name = getattr(npc, 'name', 'The NPC')
    return (f"\033[1;32m[Action]\033[0m {npc_name} gives you {item_name}.")


def _handle_take_item(player, action: dict) -> str:
    """NPC takes an item from the player."""
    item_name = action.get("item", "")
    amount = action.get("amount", 1)
    if not item_name:
        return ""
    if item_name.lower() == "gold":
        if player.gold >= amount:
            player.gold -= amount
            return f"\033[1;33m[Action]\033[0m You hand over {amount} gold."
    # Try to remove from inventory
    for item in list(player.inventory):
        if item_name.lower() in getattr(item, 'name', '').lower():
            player.inventory.remove(item)
            return f"\033[1;33m[Action]\033[0m You hand over {getattr(item, 'name', item_name)}."
    return ""


def _handle_set_condition(player, action: dict) -> str:
    """Set a condition on the player."""
    condition = action.get("condition", "")
    if not condition:
        return ""
    duration = action.get("duration", 0)
    if duration:
        player.add_timed_condition(condition, duration)
    else:
        player.add_condition(condition)
    return f"\033[1;35m[Action]\033[0m You feel {condition}."


def _handle_send_message(player, action: dict) -> str:
    """Send a message to the player (divine whisper, faction notice, etc)."""
    text = action.get("text", "")
    source = action.get("source", "world")
    if not text:
        return ""
    color_map = {
        "deity": "\033[1;35m",
        "faction": "\033[1;33m",
        "world": "\033[1;36m",
    }
    color = color_map.get(source, "\033[0;37m")
    return f"{color}[{source.title()}]\033[0m {text}"


# =========================================================================
# AI Response Parser
# =========================================================================

def parse_ai_response(raw_text: str) -> dict:
    """
    Parse an AI response, handling both JSON and plain text.
    Returns dict with: dialogue, game_actions, emotion_state, remember
    """
    # Try to parse as JSON
    try:
        # Find JSON in the response (may be wrapped in text)
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(raw_text[start:end])
            return {
                "dialogue": data.get("dialogue", ""),
                "game_actions": data.get("game_actions", []),
                "emotion_state": data.get("emotion_state", "neutral"),
                "remember": data.get("remember"),
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Fallback: treat entire response as dialogue
    clean = raw_text.strip().strip('"').strip("'")
    if len(clean) > 500:
        clean = clean[:497] + "..."
    return {
        "dialogue": clean,
        "game_actions": [],
        "emotion_state": "neutral",
        "remember": None,
    }
