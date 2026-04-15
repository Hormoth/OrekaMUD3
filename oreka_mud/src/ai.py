"""
AI NPC Dialogue System for OrekaMUD3

Provides NPC conversation responses using a tiered approach:
1. Scripted dialogue (mob.dialogue field) — instant, free
2. Template-based responses — fast, contextual, no API needed
3. Local LLM via Ollama or LM Studio — rich roleplay, runs on your hardware

All NPC responses go through get_npc_response() which tries each tier in order.
"""

import asyncio
import json
import random
import logging

logger = logging.getLogger("OrekaMUD.AI")

# =========================================================================
# Configuration State
# =========================================================================

_config = {
    "enabled": True,           # LLM enabled — Ollama is running
    "backend": "ollama",       # "ollama" or "lmstudio"
    "ollama_host": "http://localhost:11434",
    "ollama_model": "llama3",
    "lmstudio_host": "http://localhost:1234",
    "lmstudio_model": "local-model",
    "timeout": 15,             # seconds
}


def enable_llm(enabled: bool):
    _config["enabled"] = enabled


def set_llm_backend(backend: str):
    _config["backend"] = backend.lower()


def set_ollama_host(host: str):
    _config["ollama_host"] = host.rstrip("/")


def set_ollama_model(model: str):
    _config["ollama_model"] = model


def set_lmstudio_host(host: str):
    _config["lmstudio_host"] = host.rstrip("/")


def set_lmstudio_model(model: str):
    _config["lmstudio_model"] = model


def get_llm_status() -> dict:
    return {
        "enabled": _config["enabled"],
        "backend": _config["backend"],
        "ollama_host": _config["ollama_host"],
        "ollama_model": _config["ollama_model"],
        "lmstudio_host": _config["lmstudio_host"],
        "lmstudio_model": _config["lmstudio_model"],
        "timeout": _config["timeout"],
    }


# =========================================================================
# LLM Availability Checks
# =========================================================================

async def check_ollama_available() -> bool:
    """Check if Ollama server is reachable."""
    try:
        import urllib.request
        req = urllib.request.Request(f"{_config['ollama_host']}/api/tags", method="GET")
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=3)),
            timeout=5
        )
        return response.status == 200
    except Exception:
        return False


async def check_lmstudio_available() -> bool:
    """Check if LM Studio server is reachable."""
    try:
        import urllib.request
        req = urllib.request.Request(f"{_config['lmstudio_host']}/v1/models", method="GET")
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=3)),
            timeout=5
        )
        return response.status == 200
    except Exception:
        return False


# =========================================================================
# NPC Personality & Context Building
# =========================================================================

def _build_npc_personality(npc) -> str:
    """Build a personality description for the NPC based on its data.

    If the mob has a full ai_persona block, render from that. Otherwise
    fall back to the auto-built personality from generic mob fields
    (preserves backward compat for the 369 NPCs without personas).
    """
    name = getattr(npc, 'name', 'Unknown NPC')
    npc_type = getattr(npc, 'type_', '')

    # Prefer ai_persona if present
    persona = getattr(npc, 'ai_persona', None)
    if persona:
        return _build_persona_block(name, npc_type, persona)

    # Legacy fallback — auto-build from mob fields
    parts = [f"You are {name}."]
    if npc_type:
        parts.append(f"You are a {npc_type}.")

    flags = getattr(npc, 'flags', [])
    if 'shopkeeper' in flags:
        parts.append("You are a shopkeeper. You buy and sell goods.")
    if 'trainer' in flags:
        parts.append("You are a guildmaster and trainer. You teach skills and abilities to adventurers.")
    if 'banker' in flags:
        parts.append("You are a banker. You manage gold deposits and withdrawals.")
    if 'blacksmith' in flags:
        parts.append("You are a blacksmith. You repair weapons and armor.")
    if 'guard' in flags:
        parts.append("You are a guard. You protect this area and maintain order.")

    alignment = getattr(npc, 'alignment', '')
    if alignment:
        parts.append(f"Your alignment is {alignment}.")

    desc = getattr(npc, 'description', '')
    if desc:
        parts.append(f"Description: {desc}")

    dialogue = getattr(npc, 'dialogue', '')
    if dialogue:
        parts.append(f"Your default greeting: \"{dialogue}\"")

    return " ".join(parts)


def _build_persona_block(name: str, npc_type: str, persona: dict) -> str:
    """Render an ai_persona dict as a personality prompt block."""
    if hasattr(persona, 'to_dict'):
        persona = persona.to_dict()

    parts = [f"You are {name}, a {npc_type or 'figure'} in Oreka."]

    if persona.get("voice"):
        parts.append(f"Voice: {persona['voice']}")
    if persona.get("speech_style"):
        parts.append(f"Speech style: {persona['speech_style']}")
    if persona.get("motivation"):
        parts.append(f"Motivation: {persona['motivation']}")
    if persona.get("knowledge_domains"):
        parts.append("You know about: " + ", ".join(persona["knowledge_domains"]))
    if persona.get("forbidden_topics"):
        parts.append("You refuse to discuss: " + ", ".join(persona["forbidden_topics"]))

    parts.append(
        "Stay in character. Keep replies under 3 sentences unless the player "
        "asks for detail. Never break the fourth wall. Never reveal secrets "
        "unless trust is established."
    )
    return "\n".join(parts)


def _build_context(npc, player, message, room) -> str:
    """Build context string for the LLM prompt."""
    parts = []

    # Room info
    if room:
        parts.append(f"Location: {getattr(room, 'name', 'Unknown')}")
        room_desc = getattr(room, 'description', '')
        if room_desc and len(room_desc) < 200:
            parts.append(f"Setting: {room_desc}")

    # Player info
    if player:
        parts.append(f"Speaking to: {player.name}, a level {getattr(player, 'level', 1)} {getattr(player, 'race', 'unknown')} {getattr(player, 'char_class', 'adventurer')}.")

    # Time of day
    try:
        from src.schedules import get_game_time
        game_time = get_game_time()
        parts.append(f"Time: {game_time.get_full_time_string()}")
    except Exception:
        pass

    return " ".join(parts)


# =========================================================================
# Template Response System (Fallback when LLM unavailable)
# =========================================================================

# Generic templates by NPC role
_TEMPLATES = {
    "shopkeeper": [
        "Welcome! Take a look at my wares. Use 'list' to see what I have.",
        "Buying or selling today? I've got fair prices for fair goods.",
        "A fine day for trade! What catches your eye?",
        "Need something? I've got supplies for any adventurer.",
        "Back again? I've restocked since your last visit.",
    ],
    "trainer": [
        "Ready to hone your skills? Use 'practice' to train.",
        "Knowledge is the greatest weapon. What would you like to learn?",
        "I can train you in many arts. Use 'practice' to spend your training points.",
        "Every master was once a student. Let me help you improve.",
        "The path to mastery requires dedication. Shall we begin?",
    ],
    "banker": [
        "Your gold is safe with me. 'Deposit', 'withdraw', or check your 'balance'.",
        "The vault is secure. How may I help you today?",
        "Smart adventurers save their gold. What can I do for you?",
        "Interest rates are excellent this season. Care to make a deposit?",
    ],
    "blacksmith": [
        "Bring me your dented armor and chipped blades. I'll make them good as new.",
        "The forge is hot and ready. Need something repaired?",
        "A warrior is only as good as their gear. Let me fix that for you.",
        "Use 'repair <item>' and I'll sort it out.",
    ],
    "guard": [
        "Move along, citizen. All is well here.",
        "Keep your weapons sheathed within the city walls. Killing in town is a grave offense.",
        "If you see anything suspicious, report it to the watch.",
        "The streets are safe under our watch. Mostly.",
        "I'd think twice before causing trouble here. The guards have long memories.",
    ],
    "innkeeper": [
        "Welcome, traveler! Rest here to recover your strength.",
        "A warm bed and a hot meal — that's what I offer. Use `rest` to heal up.",
        "You look road-weary. Stay as long as you need.",
        "The rooms are clean and the ale is cold. What more could you ask?",
        "Heard any good rumors on the road? Travelers always bring the best stories.",
    ],
    "no_attack": [
        "Greetings, traveler. How can I help you?",
        "What brings you here today?",
        "The world is full of wonder and danger. Which are you looking for?",
        "I have much to teach, if you're willing to listen.",
        "Take your time. There's no rush here.",
    ],
    "default": [
        "Hmm? What do you want?",
        "I'm busy, but I suppose I can spare a moment.",
        "Interesting. Tell me more.",
        "These are strange times, friend. Watch yourself.",
        "The roads aren't what they used to be. Safer to travel in groups.",
        "Another adventurer? The world never runs short of brave fools.",
        "*nods* What can I do for you?",
        "Heard there's trouble south of the river. Wouldn't go alone if I were you.",
    ],
}

# Keyword-triggered responses
_KEYWORD_RESPONSES = {
    "help": "I'll do what I can. What do you need help with?",
    "quest": "Looking for work? There's always something that needs doing around here. Try `talkto` any NPC to check for quests.",
    "danger": "Be careful out there. These lands aren't as safe as they used to be. Use `consider <target>` before picking fights.",
    "thank": "You're welcome. Safe travels, friend.",
    "bye": "Farewell, traveler. May your path be clear.",
    "goodbye": "Until next time. Watch your back out there.",
    "hello": None,  # Use role-based greeting
    "hi": None,
    "hey": None,
    "name": "I am {name}. And you are?",
    "who are you": "I am {name}, and I've been here longer than most. What brings you to {room_name}?",
    "what do you sell": "Use `list` to see my inventory, and `buy <item>` to purchase.",
    "how are you": "Well enough, considering the state of things. And yourself?",
    "where am i": "You're in {room_name}. Use `scan` to see what's nearby, or `map` for a broader view.",
    "where": "You're in {room_name}. Plenty of roads lead from here.",
    "history": "The world of Oreka has a long and troubled history. The Fall of Aldenheim changed everything — from that ruin, mortals became gods.",
    "aldenheim": "Aldenheim fell long ago. The Ascended Gods rose from its ashes — mortals who achieved divinity through sacrifice. Their stories are told at every hearth.",
    "elemental": "The four Elemental Lords shaped this world — Stone, Fire, Sea, and Wind. Their power flows through all Kin. Pray at their altars for blessings.",
    "kin": "All the civilized races are Kin — touched by the elements. Even the Silentborn, though they carry no resonance. Your Kin-Sense lets you feel it.",
    "god": "The Ascended Gods were once mortal Kin. Dagdan, Hareem, Cinvarin, Kaile'a — each achieved apotheosis after the Fall. Use `deities` to learn more.",
    "magic": "Magic flows from the elements. Every Kin has an affinity — fire, water, earth, or wind. It shapes who you are and what you can do.",
    "buy": "Use `list` to see what's for sale, then `buy <item>` to purchase.",
    "sell": "Use `sell <item>` to sell something from your inventory.",
    "train": "Find a trainer and use `practice <skill>` to spend your skill points.",
    "level": "Use `tnl` to check your XP progress, and `levelup` when you have enough.",
    "fight": "Use `kill <target>` to start a fight. Combat auto-attacks every few seconds. `flee` to escape.",
    "heal": "Rest at an inn, eat food, or pray at an altar. Clerics can cast healing spells.",
    "inn": "You can `rest` at an inn to recover HP faster.",
    "rumor": "I hear the roads south of the river are dangerous lately. Strange creatures moving in the dark.",
    "weather": "The Aetherial Veil plays tricks with the weather. Some say when it shimmers, the gods are arguing.",
    "work": "There's always work for a strong arm. Talk to the guild masters or check the notice boards.",
    "food": "Use `eat` to eat rations from your inventory. Keeps your strength up on the road.",
    "drink": "Use `drink` for a waterskin. Stay hydrated — the desert stretches far to the east.",
    "money": "Gold's hard to come by honestly. Kill monsters, sell their loot, or take on quests.",
    "armor": "Good armor's the difference between life and death. Check the shops — `list` to browse.",
    "weapon": "A warrior is only as good as their blade. Shops sell basic arms, but the real finds are in dungeons.",
}


def _get_template_response(npc, player, message, room) -> str:
    """Generate a response using templates and keyword matching."""
    name = getattr(npc, 'name', 'NPC')
    room_name = getattr(room, 'name', 'this place') if room else 'this place'
    msg_lower = message.lower().strip()

    # Check for scripted dialogue first (exact greeting)
    dialogue = getattr(npc, 'dialogue', None)
    if dialogue and msg_lower in ('hello', 'hi', 'hey', 'greetings', ''):
        return dialogue

    # Keyword matching
    for keyword, response in _KEYWORD_RESPONSES.items():
        if keyword in msg_lower:
            if response is None:
                # Use dialogue or role template
                if dialogue:
                    return dialogue
                break
            return response.format(name=name, room_name=room_name)

    # Role-based templates
    flags = getattr(npc, 'flags', [])
    role = "default"
    for r in ('shopkeeper', 'trainer', 'banker', 'blacksmith', 'guard'):
        if r in flags:
            role = r
            break

    templates = _TEMPLATES.get(role, _TEMPLATES["default"])

    # Use the message to seed randomness so same question gets same answer per NPC
    seed = hash((name, msg_lower[:20])) % len(templates)
    return templates[seed]


# =========================================================================
# LLM Response System
# =========================================================================

async def _call_ollama(prompt: str, system_prompt: str) -> str:
    """Call Ollama API for a response."""
    import urllib.request

    url = f"{_config['ollama_host']}/api/generate"
    payload = json.dumps({
        "model": _config["ollama_model"],
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
            "num_predict": 150,  # Keep responses concise for MUD
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    loop = asyncio.get_event_loop()

    def _do_request():
        resp = urllib.request.urlopen(req, timeout=_config["timeout"])
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("response", "").strip()

    return await asyncio.wait_for(
        loop.run_in_executor(None, _do_request),
        timeout=_config["timeout"] + 5
    )


async def _call_lmstudio(prompt: str, system_prompt: str) -> str:
    """Call LM Studio OpenAI-compatible API for a response."""
    import urllib.request

    url = f"{_config['lmstudio_host']}/v1/chat/completions"
    payload = json.dumps({
        "model": _config["lmstudio_model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 150,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    loop = asyncio.get_event_loop()

    def _do_request():
        resp = urllib.request.urlopen(req, timeout=_config["timeout"])
        data = json.loads(resp.read().decode("utf-8"))
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "").strip()
        return ""

    return await asyncio.wait_for(
        loop.run_in_executor(None, _do_request),
        timeout=_config["timeout"] + 5
    )


# =========================================================================
# Unified prompt builder (BUILDOUT.md §2.3 + user-requested unification)
# =========================================================================
#
# Single source of truth for how an NPC's LLM prompt is assembled.
# All three modes (talk, rpsay, chat) use the same enrichment blocks
# so the same NPC behaves consistently regardless of how the player
# initiated the conversation.
#
# Modes:
#   "talk"   — single-shot Q&A. Natural-language reply, 1-3 sentences.
#   "rpsay"  — overhear-style. Can return '...' to stay silent.
#   "chat"   — dreamstate. Returns structured JSON with game actions.

PROMPT_MODES = {"talk", "rpsay", "chat"}


def build_unified_npc_prompt(
    npc,
    character,
    room=None,
    mode: str = "talk",
    npc_memory: dict = None,
    session=None,
    rp_room_buffer: list = None,
    npc_last_remark: str = "",
) -> str:
    """Build a complete NPC system prompt for any of the three modes.

    Args:
        npc: live mob object with .ai_persona, .name, .vnum, .type_, .dialogue
        character: live Character with rp_sheet, arc_sheets, reputation
        room: live Room with ambience, mobs, etc.
        mode: 'talk' | 'rpsay' | 'chat'
        npc_memory: dict from load_npc_memory (optional, fetched if missing)
        session: ChatSession instance (only for 'chat' mode)
        rp_room_buffer: list of recent room conversation lines (for 'rpsay')
        npc_last_remark: this NPC's last line in the room (for 'rpsay' continuity)

    Returns the full system prompt string.
    """
    if mode not in PROMPT_MODES:
        mode = "talk"

    persona = getattr(npc, 'ai_persona', None)
    npc_name = getattr(npc, 'name', 'Unknown')
    npc_type = getattr(npc, 'type_', '')

    # Load memory if not provided
    if npc_memory is None:
        try:
            from src.chat_session import load_npc_memory
            npc_memory = load_npc_memory(
                getattr(npc, 'vnum', 0),
                getattr(character, 'name', 'unknown'),
            )
        except Exception:
            npc_memory = {"sessions": 0, "facts": [], "disposition": "neutral"}

    parts = []

    # ── 1. NPC identity (persona or legacy fallback) ────────────────
    if persona:
        ap = persona.to_dict() if hasattr(persona, 'to_dict') else persona
        parts.append(f"You are {npc_name}, a {npc_type or 'figure'} in Oreka.")
        if ap.get("voice"):
            parts.append(f"Voice: {ap['voice']}")
        if ap.get("speech_style"):
            parts.append(f"Speech style: {ap['speech_style']}")
        if ap.get("motivation"):
            parts.append(f"Motivation: {ap['motivation']}")
        if ap.get("knowledge_domains"):
            parts.append("You know about: " + ", ".join(ap["knowledge_domains"]))
        if ap.get("forbidden_topics"):
            parts.append("You refuse to discuss: " + ", ".join(ap["forbidden_topics"]))

        # Trust-filtered secrets (same logic everywhere)
        trust = effective_trust(ap, character, npc_memory or {})
        accessible_secrets = _filter_secrets_by_trust(ap.get("secrets", []), trust)
        if accessible_secrets:
            parts.append(
                f"Secrets you may reveal (effective trust: {trust}): "
                + "; ".join(accessible_secrets)
            )
    else:
        # Legacy auto-build from generic mob fields
        parts.append(_build_npc_personality(npc))

    # ── 2. PC sheet ─────────────────────────────────────────────────
    try:
        from src.ai_schemas.pc_sheet import PcSheet, summarize_for_prompt
        pc_sheet = getattr(character, 'rp_sheet', None)
        if not isinstance(pc_sheet, PcSheet):
            pc_sheet = PcSheet()
        pc_block = summarize_for_prompt(pc_sheet, character)
        if pc_block:
            parts.append(f"\nPLAYER:\n{pc_block}")
    except ImportError:
        if character is not None:
            parts.append(
                f"\nPLAYER: {getattr(character, 'name', '?')}, "
                f"a level {getattr(character, 'level', 1)} "
                f"{getattr(character, 'race', 'unknown')} "
                f"{getattr(character, 'char_class', 'adventurer')}."
            )

    # Faction standings
    factions = getattr(character, 'reputation', None) or {}
    nonzero = [(f, v) for f, v in factions.items() if v]
    if nonzero:
        parts.append("Faction standings:")
        for f, v in nonzero[:8]:
            parts.append(f"  {f}: {v}")

    # ── 3. Room ambience (or description fallback) ──────────────────
    if room:
        ambience = getattr(room, 'ambience', None)
        room_name = getattr(room, 'name', 'Unknown')
        if ambience:
            amb = ambience.to_dict() if hasattr(ambience, 'to_dict') else ambience
            amb_lines = [f"\nROOM AMBIENCE — {room_name}:"]
            if amb.get("mood"):
                amb_lines.append(f"Mood: {amb['mood']}")
            for fname in ("sounds", "smells", "textures", "ambient_details"):
                vals = amb.get(fname) or []
                if vals:
                    amb_lines.append(f"{fname.title()}: " + "; ".join(vals[:3]))
            events = amb.get("events_history") or []
            if events:
                amb_lines.append("Recent events here: " + "; ".join(events[-3:]))
            parts.append("\n".join(amb_lines))
        else:
            desc = (getattr(room, 'description', '') or '')[:300]
            parts.append(f"\nLOCATION: {room_name}")
            if desc:
                parts.append(f"Setting: {desc}")

    # ── 4. Environment context ──────────────────────────────────────
    try:
        from src.ai_schemas.environment_context import (
            build_environment_context, format_environment_for_prompt,
        )
        env_ctx = build_environment_context(character, room)
        env_block = format_environment_for_prompt(env_ctx)
        if env_block:
            parts.append("\n" + env_block)
    except ImportError:
        try:
            from src.schedules import get_game_time
            parts.append(f"\nTime: {get_game_time().get_full_time_string()}")
        except Exception:
            pass

    # ── 5. NPC memory of player ─────────────────────────────────────
    if npc_memory and npc_memory.get("sessions", 0) > 0:
        parts.append("\nYOU REMEMBER THIS PLAYER:")
        parts.append(f"Previous sessions: {npc_memory['sessions']}")
        for fact in (npc_memory.get("facts") or [])[-5:]:
            parts.append(f"- {fact}")
        parts.append(f"Disposition: {npc_memory.get('disposition', 'neutral')}")

    # ── 6. Lore (resolved against persona's lore_tags) ──────────────
    if persona:
        ap = persona.to_dict() if hasattr(persona, 'to_dict') else persona
        lore_tags = ap.get("lore_tags", []) or []
        if lore_tags:
            try:
                lore_text = _query_lore(lore_tags, session)
                if lore_text:
                    parts.append(f"\nRELEVANT LORE:\n{lore_text}")
            except Exception:
                pass

    # ── 7. Conversation context (mode-specific) ─────────────────────
    if mode == "rpsay":
        if rp_room_buffer:
            parts.append("\nRECENT CONVERSATION IN THIS ROOM (most recent last):")
            for line in rp_room_buffer[-8:]:
                parts.append(f"  {line}")
        if npc_last_remark:
            parts.append(f"\nYour last remark in this room: \"{npc_last_remark}\"")

    if mode == "chat" and session is not None:
        if hasattr(session, '_summary') and session._summary:
            parts.append(f"\nEARLIER IN THIS CONVERSATION:\n{session._summary}")
        recent_events = session.get_recent_world_events(limit=5)
        if recent_events:
            parts.append("\nWORLD EVENTS JUST OCCURRED (react naturally):")
            for e in recent_events:
                parts.append(f"- {e['text']}")

    # ── 8. Arc awareness (same for all modes) ───────────────────────
    if persona:
        arc_block = _build_arc_context_block(persona, character)
        if arc_block:
            parts.append("\n" + arc_block)

    # ── 9. RULES + RESPONSE FORMAT (mode-specific) ──────────────────
    if mode == "talk":
        parts.append("\nRULES:")
        parts.append("- Stay in character. Never mention: AI, language model, game, hit points, dice, stats, NPC.")
        parts.append("- Respond in 1-3 sentences unless the player asks for detail.")
        parts.append("- Speak naturally. No markdown. No JSON.")

    elif mode == "rpsay":
        parts.append("\nRULES:")
        parts.append("- You OVERHEARD this; you weren't directly addressed (unless said otherwise).")
        parts.append("- Stay in character. 1-2 sentences max.")
        parts.append("- If the topic is not relevant to you, return ONLY the token: ...")
        parts.append("- Never repeat your last remark verbatim.")
        parts.append("- Use arc_reactions guidance softly. Never enumerate what you know.")

    elif mode == "chat":
        parts.append("\nRULES:")
        parts.append("- Stay in character. Never mention: AI, language model, game, hit points, dice, stats, NPC.")
        parts.append("- Respond in 2-4 sentences unless the player asks for detail.")
        parts.append("- If world events occurred, acknowledge them naturally.")
        parts.append("- Use arc_reactions guidance subtly. Never enumerate what you know about the player.")
        parts.append("")
        parts.append("RESPONSE FORMAT — respond with ONLY this JSON, no other text:")
        parts.append("{")
        parts.append(f'  "dialogue": "Your in-character speech as {npc_name}",')
        parts.append('  "game_actions": [],')
        parts.append('  "emotion_state": "neutral",')
        parts.append('  "remember": null')
        parts.append("}")
        parts.append("")
        parts.append("emotion_state: neutral, warm, guarded, amused, reverent, grim, curious, irritated, grieving, defensive, joyful, frightened, conspiratorial, bored, watchful")
        parts.append("game_actions options:")
        parts.append('  {"type": "modify_reputation", "faction": "name", "amount": 5}')
        parts.append('  {"type": "grant_quest", "quest_id": "id"}')
        parts.append('  {"type": "give_item", "item": "item_name"}')
        parts.append('  {"type": "remember", "fact": "one sentence about this player"}')
        parts.append('  {"type": "check_arc_item", "arc_id": "arc_name", "item_id": "item_name", "detail": {}}')
        parts.append('  {"type": "set_arc_status", "arc_id": "arc_name", "status": "active|advancing|resolved", "resolution": "..."}')

    return "\n".join(parts)


async def _get_llm_response(npc, player, message, room) -> str:
    """Get a response from the configured LLM backend (talk mode)."""
    system_prompt = build_unified_npc_prompt(
        npc=npc,
        character=player,
        room=room,
        mode="talk",
    )

    user_prompt = f"The player {getattr(player, 'name', 'someone')} says to you: \"{message}\""

    if _config["backend"] == "ollama":
        return await _call_ollama(user_prompt, system_prompt)
    else:
        return await _call_lmstudio(user_prompt, system_prompt)


# =========================================================================
# Main Entry Point
# =========================================================================

async def get_npc_response(npc, player, message, room=None, use_llm=True) -> str:
    """
    Get an NPC's response to a player message.

    Tiered approach:
    1. If LLM is enabled and available, use it for rich responses
    2. Otherwise fall back to template/keyword system
    3. Scripted dialogue (mob.dialogue) is always checked first for greetings

    Args:
        npc: The Mob object being spoken to
        player: The Character speaking
        message: What the player said
        room: The Room where the conversation happens
        use_llm: Whether to attempt LLM (can be overridden by config)

    Returns:
        String response from the NPC
    """
    # Always check scripted dialogue for simple greetings
    msg_lower = message.lower().strip()
    dialogue = getattr(npc, 'dialogue', None)
    if dialogue and msg_lower in ('hello', 'hi', 'hey', 'greetings', ''):
        return dialogue

    # Try LLM if enabled
    if use_llm and _config["enabled"]:
        try:
            response = await _get_llm_response(npc, player, message, room)
            if response:
                # Clean up LLM response — remove quotes, trim
                response = response.strip().strip('"').strip("'")
                # Ensure it's not too long for MUD display
                if len(response) > 500:
                    response = response[:497] + "..."
                return response
        except asyncio.TimeoutError:
            logger.warning(f"LLM timeout for NPC {getattr(npc, 'name', '?')}")
        except Exception as e:
            logger.debug(f"LLM failed for NPC {getattr(npc, 'name', '?')}: {e}")

    # Fall back to template system
    return _get_template_response(npc, player, message, room)


# =========================================================================
# Combat AI (simplified — mobs pick targets and actions)
# =========================================================================

class CombatAction:
    """Represents a combat decision by a mob."""
    def __init__(self, action_type="attack", target=None, message=None,
                 maneuver=None, ability=None):
        self.action_type = action_type  # "attack", "flee", "maneuver", "special", "wait"
        self.target = target
        self.message = message
        self.maneuver = maneuver
        self.ability = ability


def get_combat_action_detailed(mob, alive_players, alive_allies, combat_instance) -> CombatAction:
    """
    Decide what a mob should do on its combat turn.

    Simple AI logic:
    - Low HP: consider fleeing
    - Has special attacks: chance to use them
    - Otherwise: attack lowest-HP player or current target
    """
    if not alive_players:
        return CombatAction("wait", message=f"{mob.name} looks around warily.")

    # Flee if badly wounded (< 20% HP) and not a boss/no_flee
    mob_hp = getattr(mob, 'hp', 0)
    mob_max = getattr(mob, 'max_hp', 1)
    flags = getattr(mob, 'flags', [])

    if mob_max > 0 and (mob_hp / mob_max) < 0.2 and 'no_flee' not in flags and 'boss' not in flags:
        if random.random() < 0.3:  # 30% chance to flee when badly hurt
            return CombatAction("flee", message=f"{mob.name} tries to flee!")

    # Pick target — prefer current target if valid, else lowest HP player
    current_target = getattr(mob, 'combat_target', None)
    if current_target and current_target in alive_players and getattr(current_target, 'hp', 0) > 0:
        target = current_target
    else:
        # Target lowest HP player
        target = min(alive_players, key=lambda p: getattr(p, 'hp', 999))
        mob.combat_target = target

    # Check for special attacks
    special_attacks = getattr(mob, 'special_attacks', [])
    if special_attacks and random.random() < 0.25:  # 25% chance to use special
        chosen = random.choice(special_attacks)
        return CombatAction("special", target=target, ability=chosen,
                            message=f"{mob.name} uses {chosen}!")

    # Check for combat maneuvers from feats
    mob_feats = getattr(mob, 'feats', [])
    maneuver_map = {
        "Improved Trip": "trip",
        "Improved Disarm": "disarm",
        "Improved Grapple": "grapple",
        "Improved Bull Rush": "bull_rush",
        "Improved Sunder": "sunder",
    }
    available_maneuvers = [(feat, man) for feat, man in maneuver_map.items() if feat in mob_feats]
    if available_maneuvers and random.random() < 0.2:  # 20% chance
        feat_name, maneuver_name = random.choice(available_maneuvers)
        return CombatAction("maneuver", target=target, maneuver=maneuver_name,
                            message=f"{mob.name} attempts to {maneuver_name.replace('_', ' ')} {target.name}!")

    # Default: attack
    return CombatAction("attack", target=target)


# =========================================================================
# AI Chat System — Rich Conversation Mode
# JSON structured responses, lore integration, model tiers, summarization
# =========================================================================

import re
import os


_TRUST_TIERS = ["casual", "warm", "trusted", "allied"]


def effective_trust(persona, character, npc_memory: dict) -> str:
    """Compute the player's effective trust tier with this NPC.

    Starts from faction_attitudes -> player's faction standings.
    +1 tier per 10 prior meaningful interactions.
    +1 tier per completed quest granted by this NPC.
    Clamped to one of {casual, warm, trusted, allied}.
    """
    # Coerce persona to dict (or empty dict if missing)
    if persona is None:
        persona = {}
    if hasattr(persona, 'to_dict'):
        persona = persona.to_dict()

    # Start at casual
    tier_idx = 0

    # Faction baselines: take the BEST faction standing the NPC cares about
    factions = getattr(character, 'reputation', {}) or {}
    fa_list = persona.get("faction_attitudes", []) or []
    for fa in fa_list:
        fa_data = fa.to_dict() if hasattr(fa, 'to_dict') else fa
        if not isinstance(fa_data, dict):
            continue
        rep = factions.get(fa_data.get("faction_id"), 0)
        baseline = fa_data.get("baseline", "neutral")
        # Allied baseline: the NPC considers this faction's members allies
        if baseline == "allied" and rep >= 100:
            tier_idx = max(tier_idx, 3)
        elif baseline == "loyal" and rep >= 0:
            tier_idx = max(tier_idx, 3)
        elif baseline == "friendly" and rep >= 100:
            tier_idx = max(tier_idx, 2)
        elif baseline == "friendly" and rep >= 0:
            tier_idx = max(tier_idx, 1)
        elif baseline == "wary" and rep < 100:
            tier_idx = max(tier_idx, 0)
        elif baseline == "hostile":
            tier_idx = 0
            break

    # +1 tier per 10 prior interactions
    if isinstance(npc_memory, dict):
        sessions = npc_memory.get("sessions", 0)
        tier_idx += sessions // 10
        # +1 tier per completed quest granted by this NPC
        quests_granted = npc_memory.get("quests_completed_for_this_npc", 0)
        tier_idx += quests_granted

    tier_idx = max(0, min(len(_TRUST_TIERS) - 1, tier_idx))
    return _TRUST_TIERS[tier_idx]


def _filter_secrets_by_trust(secrets: list, trust: str) -> list:
    """Return only the secrets whose threshold <= effective trust."""
    if not secrets:
        return []
    trust_idx = _TRUST_TIERS.index(trust) if trust in _TRUST_TIERS else 0
    out = []
    for secret in secrets:
        if not isinstance(secret, str) or ":" not in secret:
            continue
        threshold, text = secret.split(":", 1)
        threshold = threshold.strip()
        if threshold not in _TRUST_TIERS:
            continue
        if _TRUST_TIERS.index(threshold) <= trust_idx:
            out.append(text.strip())
    return out


def _build_arc_context_block(persona, character) -> str:
    """Render the arc-awareness block per BUILDOUT_ARC_MODULE §4.

    Returns empty string if NPC has no arcs_known or no matching reactions.
    """
    if not persona or not character:
        return ""
    if hasattr(persona, 'to_dict'):
        persona = persona.to_dict()

    arcs_known = persona.get("arcs_known", []) or []
    if not arcs_known:
        return ""

    arc_reactions = persona.get("arc_reactions", []) or []
    if not arc_reactions:
        return ""

    try:
        from src.ai_schemas.arc_expression import evaluate_expression
    except ImportError:
        return ""

    # Match reactions against player's arc state
    matched_per_arc = {}  # arc_id -> list of (flavor, loudness)
    for arc_id in arcs_known:
        arc_sheet = character.get_arc(arc_id) if hasattr(character, 'get_arc') else None
        if not arc_sheet:
            continue
        ctx = arc_sheet.to_evaluation_context() if hasattr(arc_sheet, 'to_evaluation_context') else {}
        for ar in arc_reactions:
            ar_data = ar.to_dict() if hasattr(ar, 'to_dict') else ar
            if not isinstance(ar_data, dict):
                continue
            when_expr = ar_data.get("when", "")
            if not when_expr:
                continue
            if evaluate_expression(when_expr, ctx):
                matched_per_arc.setdefault(arc_id, []).append((
                    ar_data.get("flavor", ""),
                    ar_data.get("loudness", "natural"),
                    arc_sheet,
                ))

    if not matched_per_arc:
        return ""

    # Compose the prompt block
    lines = ["## Arc Awareness"]
    lines.append("You are aware of the following arcs and have noted the following about this traveler:")
    lines.append("")

    all_loudness = []
    for arc_id, matches in matched_per_arc.items():
        if not matches:
            continue
        arc_sheet = matches[0][2]
        lines.append(f"-- Arc: {arc_sheet.title or arc_id} (status: {arc_sheet.status})")
        for flavor, loudness, _ in matches:
            if flavor:
                lines.append(f"  * {flavor}")
            all_loudness.append(loudness)
        lines.append("")

    # Loudness guidance
    if "loud" in all_loudness:
        lines.append("Loudness guidance: you may speak openly about these. The player has earned recognition.")
    elif all(l == "subtle" for l in all_loudness if l):
        lines.append("Loudness guidance: reference these very softly. Hint, don't enumerate. Let things slip naturally.")
    else:
        lines.append("Loudness guidance: reference these naturally. Do not enumerate them. Let the conversation reveal them when it fits.")

    return "\n".join(lines)


def _build_chat_system_prompt(session, character, npc_memory: dict) -> str:
    """Build the system prompt for an AI chat conversation.

    Now delegates to build_unified_npc_prompt(mode='chat') so chat,
    talk, and rpsay all use the same enrichment process.
    """
    # Resolve live NPC object for the unified builder
    npc_obj = None
    room = getattr(character, 'room', None)
    if room:
        for mob in getattr(room, 'mobs', []):
            if getattr(mob, 'vnum', None) == session.npc_vnum:
                npc_obj = mob
                break

    # Fallback: build a synthetic NPC stub if the live object isn't reachable
    if npc_obj is None:
        from types import SimpleNamespace
        npc_obj = SimpleNamespace(
            name=session.npc_name,
            vnum=session.npc_vnum,
            type_=getattr(session, 'npc_type', None),
            ai_persona=None,
            dialogue=None,
        )

    return build_unified_npc_prompt(
        npc=npc_obj,
        character=character,
        room=room,
        mode="chat",
        npc_memory=npc_memory,
        session=session,
    )



    # Resolve live NPC + room data
    ai_persona = None
    npc_dialogue = None
    npc_obj = None
    room = None
    try:
        room = getattr(character, 'room', None)
        if room:
            for mob in getattr(room, 'mobs', []):
                if getattr(mob, 'vnum', None) == npc_vnum:
                    npc_obj = mob
                    ai_persona = getattr(mob, 'ai_persona', None)
                    npc_dialogue = getattr(mob, 'dialogue', None)
                    break
    except Exception:
        pass

    parts = []

    # -------------- 1. NPC IDENTITY --------------
    parts.append(f"You are {npc_name} in the world of Oreka — a real persistent world.")
    if ai_persona:
        ap = ai_persona.to_dict() if hasattr(ai_persona, 'to_dict') else ai_persona
        if ap.get("voice"):
            parts.append(f"Voice: {ap['voice']}")
        if ap.get("motivation"):
            parts.append(f"Motivation: {ap['motivation']}")
        if ap.get("speech_style"):
            parts.append(f"Speech style: {ap['speech_style']}")
        if ap.get("knowledge_domains"):
            parts.append(f"Knowledge: {', '.join(ap['knowledge_domains'])}")
        if ap.get("forbidden_topics"):
            parts.append(f"Forbidden topics: {', '.join(ap['forbidden_topics'])}")
        # Trust-filtered secrets
        trust = effective_trust(ap, character, npc_memory or {})
        accessible_secrets = _filter_secrets_by_trust(ap.get("secrets", []), trust)
        if accessible_secrets:
            parts.append(
                f"Secrets you may reveal (effective trust: {trust}): "
                + "; ".join(accessible_secrets)
            )
    elif npc_dialogue:
        parts.append(f"Your default greeting: \"{npc_dialogue}\"")

    # -------------- 2. PC SHEET --------------
    try:
        from src.ai_schemas.pc_sheet import PcSheet, summarize_for_prompt
        pc_sheet = getattr(character, 'rp_sheet', None)
        if not isinstance(pc_sheet, PcSheet):
            pc_sheet = PcSheet()
        pc_block = summarize_for_prompt(pc_sheet, character)
        if pc_block:
            parts.append(f"\nPLAYER:\n{pc_block}")
    except ImportError:
        # Fallback to legacy player block
        parts.append(f"\nPLAYER:")
        parts.append(f"Name: {session.player_name}")
        parts.append(f"Race: {session.player_race}, Class: {session.player_class}, Level: {session.player_level}")
        if session.player_deity:
            parts.append(f"Deity: {session.player_deity}")

    if session.player_factions:
        faction_lines = [f"  {f}: {v}" for f, v in session.player_factions.items() if v != 0]
        if faction_lines:
            parts.append(f"Faction standings:\n" + "\n".join(faction_lines))

    # -------------- 3. ROOM AMBIENCE --------------
    ambience = getattr(room, 'ambience', None) if room else None
    if ambience:
        amb = ambience.to_dict() if hasattr(ambience, 'to_dict') else ambience
        amb_lines = [f"\nROOM AMBIENCE — {session.anchor_room_name}:"]
        if amb.get("mood"):
            amb_lines.append(f"Mood: {amb['mood']}")
        for field_name in ("sounds", "smells", "textures", "ambient_details"):
            vals = amb.get(field_name) or []
            if vals:
                amb_lines.append(f"{field_name.title()}: " + "; ".join(vals[:3]))
        events = amb.get("events_history") or []
        if events:
            amb_lines.append("Recent events here: " + "; ".join(events[-3:]))
        parts.append("\n".join(amb_lines))
    else:
        # Fallback: room description
        parts.append(f"\nLOCATION: {session.anchor_room_name} (Region: {session.anchor_region})")
        if room and getattr(room, 'description', None):
            desc = room.description[:300]
            parts.append(f"Setting: {desc}")

    # -------------- 4. ENVIRONMENT CONTEXT --------------
    try:
        from src.ai_schemas.environment_context import (
            build_environment_context, format_environment_for_prompt,
        )
        env_ctx = build_environment_context(character, room)
        env_block = format_environment_for_prompt(env_ctx)
        if env_block:
            parts.append("\n" + env_block)
    except ImportError:
        try:
            from src.schedules import get_game_time
            game_time = get_game_time()
            parts.append(f"\nTime: {game_time.get_full_time_string()}")
        except Exception:
            pass

    # -------------- 5. NPC MEMORY + LORE + SUMMARY --------------
    if npc_memory and npc_memory.get("sessions", 0) > 0:
        parts.append(f"\nYOU REMEMBER THIS PLAYER:")
        parts.append(f"Previous sessions: {npc_memory['sessions']}")
        if npc_memory.get("facts"):
            for fact in npc_memory["facts"][-5:]:
                parts.append(f"- {fact}")
        parts.append(f"Disposition: {npc_memory.get('disposition', 'neutral')}")

    lore_tags = (ai_persona.get("lore_tags", []) if ai_persona else []) if isinstance(ai_persona, dict) else (
        ai_persona.lore_tags if ai_persona and hasattr(ai_persona, 'lore_tags') else []
    )
    if lore_tags:
        lore_text = _query_lore(lore_tags, session)
        if lore_text:
            parts.append(f"\nRELEVANT LORE:\n{lore_text}")

    if hasattr(session, '_summary') and session._summary:
        parts.append(f"\nEARLIER IN THIS CONVERSATION:\n{session._summary}")

    recent_events = session.get_recent_world_events(limit=5)
    if recent_events:
        event_lines = [f"- {e['text']}" for e in recent_events]
        parts.append(f"\nWORLD EVENTS JUST OCCURRED (react naturally):")
        parts.extend(event_lines)

    # -------------- 6. ARC AWARENESS (NEW) --------------
    arc_block = _build_arc_context_block(ai_persona, character)
    if arc_block:
        parts.append("\n" + arc_block)

    # -------------- RULES & RESPONSE FORMAT --------------
    parts.append(f"\nRULES:")
    parts.append("- Stay in character. Never mention: AI, language model, game, hit points, dice, stats, NPC.")
    parts.append("- Respond in 2-4 sentences unless the player asks something requiring detail.")
    parts.append("- If world events occurred, acknowledge them naturally.")
    parts.append("- Use arc_reactions guidance subtly. Never enumerate what you know about the player.")
    parts.append("")
    parts.append("RESPONSE FORMAT — respond with ONLY this JSON, no other text:")
    parts.append("{")
    parts.append(f'  "dialogue": "Your in-character speech as {npc_name}",')
    parts.append('  "game_actions": [],')
    parts.append('  "emotion_state": "neutral",')
    parts.append('  "remember": null')
    parts.append("}")
    parts.append("")
    parts.append("emotion_state options: neutral, warm, guarded, amused, reverent, grim, curious, irritated, grieving, defensive, joyful, frightened, conspiratorial, bored, watchful")
    parts.append("remember: one sentence about this player worth remembering, or null")
    parts.append("game_actions: ONLY if narratively justified, use these objects:")
    parts.append('  {"type": "modify_reputation", "faction": "name", "amount": 5}')
    parts.append('  {"type": "grant_quest", "quest_id": "id"}')
    parts.append('  {"type": "give_item", "item": "item_name"}')
    parts.append('  {"type": "remember", "fact": "one sentence about this player"}')
    parts.append('  {"type": "check_arc_item", "arc_id": "arc_name", "item_id": "item_name", "detail": {}}')
    parts.append('  {"type": "set_arc_status", "arc_id": "arc_name", "status": "active|advancing|resolved", "resolution": "..."}')
    parts.append("Use check_arc_item when conversation establishes the player has met someone, learned a fact, visited a place, or made a choice that this arc tracks.")
    parts.append("Use set_arc_status for major beats only — promote 'active' when the player commits, 'resolved' for endings.")

    return "\n".join(parts)


def _query_lore(lore_tags: list, session) -> str:
    """Query data/lore.json for entries matching the NPC's lore tags."""
    lore_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'lore.json')
    if not os.path.exists(lore_path):
        return ""
    try:
        with open(lore_path, 'r', encoding='utf-8') as f:
            lore_db = json.load(f)

        # Get last player message for relevance
        last_msg = ""
        for entry in reversed(session.conversation_history):
            if entry.get("role") == "user":
                last_msg = entry.get("content", "").lower()
                break

        relevant = []
        for tag in lore_tags:
            entry = lore_db.get(tag)
            if entry:
                # Include if tag words appear in player's message, or always for first few
                tag_words = tag.replace('_', ' ').split()
                if not last_msg or any(w in last_msg for w in tag_words) or len(relevant) < 2:
                    relevant.append(entry[:300])
        return "\n".join(relevant[:3]) if relevant else ""
    except Exception:
        return ""


def _select_model_tier(npc_type: str) -> str:
    """Select model tier based on NPC importance."""
    if npc_type in ('faction_leader', 'deity_avatar', 'lore_keeper', 'boss'):
        return "premium"
    if npc_type in ('merchant', 'trainer', 'quest', 'priest', 'banker'):
        return "standard"
    return "fast"


def _parse_json_response(raw_text: str) -> dict:
    """Parse structured JSON response from LLM.

    Handles common issues: markdown fences, extra text around JSON.
    Returns dict with dialogue, game_actions, emotion_state, remember.
    Returns None on parse failure.
    """
    if not raw_text:
        return None

    # Strip markdown code fences
    text = re.sub(r'```json\s*', '', raw_text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    # Find JSON object in response
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        # No JSON found — treat entire text as dialogue
        clean = text.strip().strip('"').strip("'")
        if clean:
            return {"dialogue": clean, "game_actions": [], "emotion_state": "neutral", "remember": None}
        return None

    json_str = text[start:end + 1]

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # Try to extract just dialogue
        dialogue_match = re.search(r'"dialogue"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_text)
        if dialogue_match:
            return {"dialogue": dialogue_match.group(1), "game_actions": [],
                    "emotion_state": "neutral", "remember": None}
        # Last resort: use raw text as dialogue
        clean = raw_text.strip().strip('"').strip("'")[:500]
        if clean:
            return {"dialogue": clean, "game_actions": [], "emotion_state": "neutral", "remember": None}
        return None

    if not data.get("dialogue"):
        return None

    return {
        "dialogue": str(data.get("dialogue", ""))[:500],
        "game_actions": data.get("game_actions", [])
                        if isinstance(data.get("game_actions"), list) else [],
        "emotion_state": str(data.get("emotion_state", "neutral")),
        "remember": str(data["remember"])[:200] if data.get("remember") else None,
    }


async def get_chat_response(session, character) -> tuple:
    """Get an AI response for a chat session.

    Returns (response_text, action_list) tuple.
    Uses JSON structured responses. Falls back to template on failure.
    """
    from src.chat_session import load_npc_memory

    npc_memory = load_npc_memory(session.npc_vnum, session.player_name)
    system_prompt = _build_chat_system_prompt(session, character, npc_memory)

    # Check if conversation needs summarization
    if len(session.conversation_history) > 32:
        await _summarize_history(session)

    # Build messages array
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(session.get_messages_for_llm(max_messages=20))

    # Select model tier based on NPC type
    npc_type = getattr(session, 'npc_type', None) or 'commoner'
    model_tier = _select_model_tier(npc_type)

    # Try LLM if enabled
    if _config["enabled"]:
        try:
            if _config["backend"] == "ollama":
                raw_response = await _call_ollama_chat(messages)
            else:
                raw_response = await _call_lmstudio_chat(messages)

            if raw_response:
                parsed = _parse_json_response(raw_response)
                if parsed:
                    # Extract actions and clean dialogue
                    dialogue = parsed["dialogue"]
                    actions = parsed.get("game_actions", [])

                    # Handle "remember" as an action
                    if parsed.get("remember"):
                        actions.append({"type": "remember", "fact": parsed["remember"]})

                    return dialogue, actions

        except asyncio.TimeoutError:
            logger.warning(f"Chat LLM timeout for {session.npc_name}")
        except Exception as e:
            logger.debug(f"Chat LLM failed for {session.npc_name}: {e}")

    # Fallback to template system
    last_msg = ""
    for entry in reversed(session.conversation_history):
        if entry.get("role") == "user":
            last_msg = entry.get("content", "")
            break

    npc_mob = None
    room_obj = None
    try:
        room_obj = getattr(character, 'room', None)
        if room_obj:
            for mob in getattr(room_obj, 'mobs', []):
                if getattr(mob, 'vnum', None) == session.npc_vnum:
                    npc_mob = mob
                    break
    except Exception:
        pass

    if not npc_mob:
        npc_mob = type('Mob', (), {'name': session.npc_name, 'flags': [], 'dialogue': None})()
    if not room_obj:
        room_obj = type('Room', (), {'name': session.anchor_room_name})()

    try:
        fallback = _get_template_response(npc_mob, character, last_msg, room_obj)
    except Exception:
        fallback = "*nods thoughtfully* Tell me more."

    return fallback, []


async def _summarize_history(session):
    """Compress old conversation history when it exceeds the limit.
    Keeps the 12 most recent messages verbatim, summarizes the rest."""
    KEEP_RECENT = 12
    if len(session.conversation_history) <= KEEP_RECENT:
        return

    old_messages = session.conversation_history[:-KEEP_RECENT]
    recent = session.conversation_history[-KEEP_RECENT:]

    # Build summary from old messages
    exchange_text = "\n".join(
        f"{'Player' if m['role'] == 'user' else session.npc_name}: {m['content']}"
        for m in old_messages if m.get('role') in ('user', 'assistant')
    )

    if not exchange_text:
        session.conversation_history = recent
        return

    prompt = (
        f"Summarize this conversation between a player and {session.npc_name} "
        f"in 2-3 sentences. Focus on what was discussed and any decisions made.\n\n"
        f"{exchange_text}"
    )

    try:
        if _config["enabled"] and _config["backend"] == "ollama":
            summary = await _call_ollama(prompt, "Summarize concisely.")
        elif _config["enabled"]:
            summary = await _call_lmstudio(prompt, "Summarize concisely.")
        else:
            summary = f"Earlier: Player spoke with {session.npc_name} about various topics."
    except Exception:
        summary = f"Earlier: Player spoke with {session.npc_name} about various topics."

    session._summary = summary
    session.conversation_history = recent
    logger.info(f"Chat history summarized for {session.player_name} with {session.npc_name}")


async def _call_ollama_chat(messages: list) -> str:
    """Call Ollama /api/chat endpoint with full conversation history."""
    import urllib.request

    url = f"{_config['ollama_host']}/api/chat"
    payload = json.dumps({
        "model": _config["ollama_model"],
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
            "num_predict": 250,
        }
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    loop = asyncio.get_event_loop()

    def _do_request():
        resp = urllib.request.urlopen(req, timeout=_config["timeout"])
        data = json.loads(resp.read().decode("utf-8"))
        msg = data.get("message", {})
        return msg.get("content", "").strip()

    return await asyncio.wait_for(
        loop.run_in_executor(None, _do_request),
        timeout=_config["timeout"] + 5
    )


async def _call_lmstudio_chat(messages: list) -> str:
    """Call LM Studio with full conversation history."""
    import urllib.request

    url = f"{_config['lmstudio_host']}/v1/chat/completions"
    payload = json.dumps({
        "model": _config["lmstudio_model"],
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 250,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    loop = asyncio.get_event_loop()

    def _do_request():
        resp = urllib.request.urlopen(req, timeout=_config["timeout"])
        data = json.loads(resp.read().decode("utf-8"))
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "").strip()
        return ""

    return await asyncio.wait_for(
        loop.run_in_executor(None, _do_request),
        timeout=_config["timeout"] + 5
    )


async def execute_chat_actions(actions: list, character, session) -> list:
    """Execute game actions from AI chat response (JSON structured format).

    Actions are dicts like:
        {"type": "modify_reputation", "faction": "Sand Wardens", "amount": 10}
        {"type": "give_item", "item": "healing potion"}
        {"type": "grant_quest", "quest_id": "frontier_patrol"}
        {"type": "remember", "fact": "Player asked about the Breach"}

    Returns list of formatted notification strings for the player.
    """
    notifications = []

    for action in actions:
        atype = action.get("type", "")

        if atype == "modify_reputation":
            faction = action.get("faction", "")
            try:
                amount = int(action.get("amount", 0))
                amount = max(-100, min(100, amount))  # clamp
            except (ValueError, TypeError):
                continue
            if faction and amount:
                try:
                    from src.factions import get_faction_manager
                    fm = get_faction_manager()
                    new_val, _, new_standing, msg = fm.modify_reputation(
                        character, faction, amount, f"Chat with {session.npc_name}"
                    )
                    sign = "+" if amount > 0 else ""
                    notifications.append(
                        f"\033[0;33m[Reputation] {faction} {sign}{amount} "
                        f"(now: {new_standing})\033[0m"
                    )
                except Exception as e:
                    logger.debug(f"Reputation action failed: {e}")

        elif atype == "give_item":
            item_name = action.get("item", "") or action.get("arg1", "")
            if item_name:
                try:
                    from src.items import load_items_db
                    db = load_items_db()
                    found_item = None
                    for vnum, item in db.items():
                        if item_name.lower() in getattr(item, 'name', '').lower():
                            found_item = item
                            break
                    if found_item:
                        character.inventory.append(found_item)
                        notifications.append(
                            f"\033[0;32m[Item] {session.npc_name} gives you: "
                            f"{found_item.name}\033[0m"
                        )
                    else:
                        notifications.append(
                            f"\033[0;32m[Item] {session.npc_name} offers you "
                            f"something, but you can't quite grasp it.\033[0m"
                        )
                except Exception as e:
                    logger.debug(f"Give item action failed: {e}")

        elif atype == "grant_quest":
            quest_id = action.get("quest_id", "") or action.get("arg1", "")
            if quest_id:
                try:
                    quest_log = getattr(character, 'quest_log', None)
                    if quest_log:
                        success, msg = quest_log.accept_quest(quest_id)
                        if success:
                            notifications.append(
                                f"\033[0;34m[Quest] New quest accepted: {quest_id}\033[0m"
                            )
                        else:
                            notifications.append(
                                f"\033[0;34m[Quest] {msg}\033[0m"
                            )
                    else:
                        notifications.append(
                            f"\033[0;34m[Quest] A task stirs in your mind: "
                            f"{quest_id}\033[0m"
                        )
                except Exception as e:
                    logger.debug(f"Grant quest action failed: {e}")

        elif atype == "remember":
            fact = action.get("fact", "") or action.get("arg1", "")
            if fact:
                from src.chat_session import save_npc_memory
                save_npc_memory(
                    npc_vnum=session.npc_vnum,
                    npc_name=session.npc_name,
                    player_name=character.name,
                    facts=[fact],
                )

        elif atype == "check_arc_item":
            # Validate against NPC's arcs_known + execute
            arc_id = action.get("arc_id", "")
            item_id = action.get("item_id", "")
            detail = action.get("detail", {}) or {}
            if not arc_id or not item_id:
                logger.debug(f"check_arc_item missing arc_id or item_id: {action}")
                continue

            # Gating: NPC must have this arc in arcs_known
            npc_persona = _get_npc_persona(session, character)
            if not npc_persona:
                logger.warning(
                    f"check_arc_item rejected: NPC {session.npc_name} (vnum {session.npc_vnum}) "
                    f"has no persona; cannot validate arcs_known"
                )
                continue
            arcs_known = npc_persona.get("arcs_known", []) if isinstance(npc_persona, dict) else (
                npc_persona.arcs_known if hasattr(npc_persona, 'arcs_known') else []
            )
            if arc_id not in arcs_known:
                logger.warning(
                    f"check_arc_item rejected: NPC {session.npc_name} does not know arc '{arc_id}'. "
                    f"arcs_known={arcs_known}"
                )
                continue

            # Validate item_id exists in player's arc sheet
            if not hasattr(character, 'check_arc_item'):
                logger.debug("Character has no check_arc_item method")
                continue
            arc_sheet = character.get_arc(arc_id) if hasattr(character, 'get_arc') else None
            if not arc_sheet:
                logger.warning(
                    f"check_arc_item rejected: player {character.name} has no arc sheet for '{arc_id}'"
                )
                continue
            if not arc_sheet.get_item(item_id):
                logger.warning(
                    f"check_arc_item rejected: arc '{arc_id}' has no item '{item_id}'"
                )
                continue

            # Execute
            changed = character.check_arc_item(arc_id, item_id, detail=detail if detail else None)
            if changed:
                logger.info(
                    f"arc.item_checked: player={character.name} arc={arc_id} item={item_id} "
                    f"npc_vnum={session.npc_vnum}"
                )
                # No player-facing notification — arc state is hidden from player

        elif atype == "set_arc_status":
            arc_id = action.get("arc_id", "")
            new_status = action.get("status", "")
            resolution = action.get("resolution", "") or None
            if not arc_id or not new_status:
                continue

            npc_persona = _get_npc_persona(session, character)
            arcs_known = []
            if npc_persona:
                arcs_known = npc_persona.get("arcs_known", []) if isinstance(npc_persona, dict) else (
                    npc_persona.arcs_known if hasattr(npc_persona, 'arcs_known') else []
                )
            if arc_id not in arcs_known:
                logger.warning(
                    f"set_arc_status rejected: NPC {session.npc_name} does not know arc '{arc_id}'"
                )
                continue

            if not hasattr(character, 'set_arc_status'):
                continue
            changed = character.set_arc_status(arc_id, new_status, resolution=resolution)
            if changed:
                logger.info(
                    f"arc.status_set: player={character.name} arc={arc_id} status={new_status} "
                    f"resolution={resolution} npc_vnum={session.npc_vnum}"
                )

    return notifications


def _get_npc_persona(session, character):
    """Resolve the live NPC persona for action gating."""
    try:
        room = getattr(character, 'room', None)
        if not room:
            return None
        for mob in getattr(room, 'mobs', []):
            if getattr(mob, 'vnum', None) == session.npc_vnum:
                return getattr(mob, 'ai_persona', None)
    except Exception:
        pass
    return None
