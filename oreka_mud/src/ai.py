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
    "enabled": True,           # Whether LLM is enabled (falls back to templates if False)
    "backend": "ollama",       # "ollama" or "lmstudio"
    "ollama_host": "http://localhost:11434",
    "ollama_model": "llama3.2",
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
    """Build a personality description for the NPC based on its data."""
    parts = []

    name = getattr(npc, 'name', 'Unknown NPC')
    parts.append(f"You are {name}.")

    # Type/role
    npc_type = getattr(npc, 'type_', '')
    if npc_type:
        parts.append(f"You are a {npc_type}.")

    # Flags → role
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

    # Alignment
    alignment = getattr(npc, 'alignment', '')
    if alignment:
        parts.append(f"Your alignment is {alignment}.")

    # Description
    desc = getattr(npc, 'description', '')
    if desc:
        parts.append(f"Description: {desc}")

    # Dialogue hint
    dialogue = getattr(npc, 'dialogue', '')
    if dialogue:
        parts.append(f"Your default greeting: \"{dialogue}\"")

    return " ".join(parts)


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
        "Keep your weapons sheathed within the city walls.",
        "If you see anything suspicious, report it to the watch.",
        "The streets are safe under our watch. Mostly.",
    ],
    "default": [
        "Hmm? What do you want?",
        "I'm busy. Make it quick.",
        "Interesting. Tell me more.",
        "I see. And what would you have me do about it?",
        "You look like you could use some help.",
        "These are strange times, friend.",
    ],
}

# Keyword-triggered responses
_KEYWORD_RESPONSES = {
    "help": "I'll do what I can. What do you need help with?",
    "quest": "Looking for work? There's always something that needs doing around here.",
    "danger": "Be careful out there. These lands aren't as safe as they used to be.",
    "thank": "You're welcome. Safe travels.",
    "bye": "Farewell, traveler. May your path be clear.",
    "goodbye": "Until next time.",
    "hello": None,  # Use role-based greeting
    "hi": None,
    "hey": None,
    "name": "I am {name}. And you are?",
    "who are you": "I am {name}. What brings you here?",
    "what do you sell": "Use 'list' to see my inventory.",
    "how are you": "Well enough, considering. And yourself?",
    "where am I": "You're in {room_name}. Look around.",
    "history": "The world of Oreka has a long and troubled history. The Fall of Aldenheim changed everything.",
    "aldenheim": "Aldenheim fell long ago. The Ascended Gods rose from its ashes — mortals who achieved divinity through sacrifice.",
    "elemental": "The four Elemental Lords shaped this world — Stone, Fire, Sea, and Wind. Their power flows through all Kin.",
    "kin": "All the civilized races are Kin — touched by the elements. Even the Silentborn, though they carry no resonance.",
    "god": "The Ascended Gods were once mortal Kin. Cinvarin, Hareem, Tarvek Wen, and others achieved apotheosis after the Fall.",
    "magic": "Magic flows from the elements. Every Kin has an affinity — fire, water, earth, or wind. It shapes their power.",
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


async def _get_llm_response(npc, player, message, room) -> str:
    """Get a response from the configured LLM backend."""
    personality = _build_npc_personality(npc)
    context = _build_context(npc, player, message, room)

    system_prompt = (
        f"{personality}\n\n"
        f"You are an NPC in OrekaMUD, a D&D 3.5 text-based game set in the world of Oreka.\n"
        f"Stay in character. Respond in 1-3 sentences. Be concise — this is a MUD, not a novel.\n"
        f"Never break character. Never mention being an AI. Never use markdown or formatting.\n"
        f"Speak naturally as your character would. Use the world's lore when relevant.\n"
        f"{context}"
    )

    user_prompt = f"The player {player.name} says to you: \"{message}\""

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
