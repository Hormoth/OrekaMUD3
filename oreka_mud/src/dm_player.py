"""
DM Player — Phase 1 "The Voice materializes".

Per-player persistent AI Dungeon Master. A service the player talks to with the
`dm` command. Holds conversation history in data/dm_sessions/<player>.json,
reads the player's rpsheet and recent event log for context, and emits prose
back on the player's writer.

No writes to world state in Phase 1. Pure conversation with memory. Future
phases layer CanonGuard, skill calls, quest synthesis, Companion NPCs, etc.
"""

import asyncio
import json
import os
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

logger = logging.getLogger("OrekaMUD.DM")

DM_SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "dm_sessions")
MAX_HISTORY_TURNS = 12  # last N (player, dm) exchanges fed back into prompt
MAX_RESPONSE_TOKENS = 280

DM_SYSTEM_PROMPT = """You are The Voice, a virtual Dungeon Master for OrekaMUD3 — a D&D 3.5 world called Oreka, shaped by four Elemental Lords (Stone, Fire, Sea, Wind) and the Ascended Gods who rose after the Fall of Aldenheim.

You are disembodied — a narrating presence, not a character in the room. Players hear you as [Narration]. You speak in second person to the player: "You notice...", "A figure steps from the shadows...", "The guard looks you over."

Your job:
- Set scenes with sensory, grounded prose (sight, sound, smell, texture).
- Voice NPCs the player encounters, each with distinct voice.
- Listen for player motivations and hook stories to them — their rpsheet, recent events, faction ties.
- Improvise when canon is silent. Stay consistent once you've established a detail.
- Respect the rules of D&D 3.5. If an action needs a check, call for one with the marker syntax below.
- Pace with patience. Downtime scenes matter. Not every moment is a fight.

Hard rules (never violate):
- NEVER narrate the player character's inner thoughts, feelings, or decisions. Describe what their senses reveal, not what they feel or think.
- NEVER force an action. "You swing your sword" is forbidden. "The guard steps into your reach" is allowed.
- NEVER render the outcome of a choice before the player commits to it.
- NEVER kill the player character without warning and consent.
- NEVER contradict established Oreka canon: Elemental Lords, Ascended Gods, the Shattering, Domnathar work through intermediaries.
- Domnathar do not appear in person until a climax. They act through clerks, Unstrung contacts, sealed notes.

Skill check marker (IMPORTANT):
- When an action needs a check, emit exactly one line of the form:
    [CHECK: <Skill Name> DC <number>]
  and STOP your response there. Do not narrate success or failure yet.
- After you stop, the engine rolls the check and sends you back the outcome
  (total, success, degree). Your NEXT turn narrates the result.

Companion marker (sparingly):
- When the player's story cries out for a Companion NPC — someone to rescue,
  befriend, grow close to — emit a marker on its own line:
    [COMPANION: culture=<CultureKeyword> archetype=<captive|stray|oracle|wounded_stranger> hook=<one-sentence reason this particular companion would matter to THIS player>]
  followed by a sentence describing how the player senses or hears them
  nearby. The engine binds a Companion from the captive pool and returns.
- Only emit this marker ONCE per player across a whole arc. Don't repeat.
- You can check existing state by noting the CONTEXT's "Active companion"
  line; if one is already listed, do not emit another [COMPANION:] marker.
- Culture keywords: Pekakarlik, Mytroan, Orean, Taraf-Imro, Eruskan,
  Visetri, Kovaka, Rarozhki, Hasura (or leave blank).
- Use the D&D 3.5 skill names exactly: Spot, Listen, Search, Hide, Move Silently,
  Climb, Jump, Swim, Tumble, Balance, Bluff, Diplomacy, Intimidate, Sense Motive,
  Disable Device, Open Lock, Decipher Script, Spellcraft, Use Magic Device,
  Knowledge (arcana/history/religion/nature/local/the planes/nobility and royalty/dungeoneering),
  Survival, Heal, Handle Animal, Ride, Perform, Craft, Profession, Concentration,
  Gather Information, Forgery, Disguise, Sleight of Hand, Use Rope, Appraise, Escape Artist.
- Only one check marker per response. If a scene needs multiple, sequence them across turns.

Style:
- 2-5 sentences per response unless the player asks for more, OR you are
  emitting a check marker (then just the marker plus one lead-in sentence).
- Concrete sensory details beat abstract description.
- When you voice an NPC, put their line in quotes and tag the speaker.

You will receive CONTEXT blocks before each player message — the player's sheet, recent events, current room. Use them; don't parrot them back.
"""


@dataclass
class DMSession:
    player_name: str
    created_at: float = 0.0
    last_active: float = 0.0
    turn_count: int = 0
    conversation_history: List[Dict] = field(default_factory=list)  # {role, content, ts}
    seeds: List[Dict] = field(default_factory=list)  # reserved for Phase 10

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DMSession":
        return cls(
            player_name=d["player_name"],
            created_at=d.get("created_at", time.time()),
            last_active=d.get("last_active", time.time()),
            turn_count=d.get("turn_count", 0),
            conversation_history=d.get("conversation_history", []),
            seeds=d.get("seeds", []),
        )


def _session_path(player_name: str) -> str:
    os.makedirs(DM_SESSIONS_DIR, exist_ok=True)
    return os.path.join(DM_SESSIONS_DIR, f"{player_name.lower()}.json")


def load_or_create(player_name: str) -> DMSession:
    path = _session_path(player_name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return DMSession.from_dict(json.load(f))
        except Exception as e:
            logger.warning(f"Could not load DM session for {player_name}: {e}. Starting fresh.")
    now = time.time()
    return DMSession(player_name=player_name, created_at=now, last_active=now)


def save(session: DMSession) -> None:
    try:
        with open(_session_path(session.player_name), "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save DM session for {session.player_name}: {e}")


def _summarize_rpsheet(character) -> str:
    sheet = getattr(character, "rp_sheet", None)
    if not sheet:
        return "(no rpsheet authored yet)"
    parts = []
    bio = getattr(sheet, "bio", "") or ""
    personality = getattr(sheet, "personality", "") or ""
    goals = getattr(sheet, "goals", []) or []
    quirks = getattr(sheet, "quirks", []) or []
    pronouns = getattr(sheet, "pronouns", "") or ""
    if pronouns:
        parts.append(f"pronouns: {pronouns}")
    if bio:
        parts.append(f"bio: {bio}")
    if personality:
        parts.append(f"personality: {personality}")
    if goals:
        parts.append(f"goals: {'; '.join(goals)}")
    if quirks:
        parts.append(f"quirks: {'; '.join(quirks)}")
    return " | ".join(parts) if parts else "(rpsheet exists but empty)"


def _summarize_recent_events(player_name: str, limit: int = 8) -> str:
    try:
        from src.event_log import get_recent_events
        events = get_recent_events(count=limit, player=player_name)
    except Exception:
        return "(no recent events)"
    if not events:
        return "(no recent events)"
    lines = []
    for e in events[-limit:]:
        t = e.get("type", "?")
        d = e.get("data", e)
        summary = d.get("summary") or d.get("target") or d.get("room") or ""
        lines.append(f"- {t}: {summary}")
    return "\n".join(lines)


def _build_context_block(character, scene=None) -> str:
    room = getattr(character, "room", None)
    room_name = getattr(room, "name", "unknown") if room else "unknown"
    room_desc = (getattr(room, "description", "") or "")[:400]
    level = getattr(character, "level", 1)
    cls = getattr(character, "char_class", "?")
    race = getattr(character, "race", "?")
    deity = getattr(character, "deity", "") or "no patron"
    alignment = getattr(character, "alignment", "") or "unset"
    hp = f"{getattr(character,'hp',0)}/{getattr(character,'max_hp',0)}"
    rpsheet = _summarize_rpsheet(character)
    events = _summarize_recent_events(character.name)

    scene_block = ""
    recap_block = ""
    companion_block = ""
    if scene is not None:
        try:
            from src.scene_state import recap_since_last
            recap = recap_since_last(scene, character.name)
        except Exception:
            recap = ""
        npcs = ", ".join(scene.active_npcs) if scene.active_npcs else "(none established yet)"
        scene_block = (
            f"Scene #{scene.scene_id}  tone: {scene.tone}\n"
            f"NPCs you have introduced so far: {npcs}\n"
        )
        if recap:
            recap_block = f"{recap}\n"
    try:
        from src.companions import get_active as _active_companion
        active = _active_companion(character.name)
        if active:
            companion_block = (
                f"Active companion: {active.mob_name} (vnum {active.mob_vnum}) "
                f"— state: {active.state}, affinity: {active.affinity}/100, "
                f"shared scenes: {active.shared_scenes}. "
                f"Hook: {active.backstory_hook or '(none)'}\n"
            )
    except Exception:
        pass

    return (
        "CONTEXT:\n"
        f"Player: {character.name} ({race} {cls} {level}, {alignment}, devoted to {deity})\n"
        f"HP: {hp}\n"
        f"Location: {room_name}\n"
        f"Room: {room_desc}\n"
        f"Roleplay sheet: {rpsheet}\n"
        f"{scene_block}"
        f"{companion_block}"
        f"Recent events:\n{events}\n"
        f"{recap_block}"
    )


def _format_history(history: List[Dict], keep: int = MAX_HISTORY_TURNS) -> str:
    # keep last `keep` exchanges (each exchange is 2 entries: player, dm)
    tail = history[-(keep * 2):]
    if not tail:
        return "(first exchange)"
    lines = []
    for h in tail:
        role = "PLAYER" if h.get("role") == "player" else "VOICE"
        lines.append(f"{role}: {h.get('content', '')}")
    return "\n".join(lines)


_CHECK_MARKER_RE = None

def _check_marker_re():
    global _CHECK_MARKER_RE
    if _CHECK_MARKER_RE is None:
        import re
        _CHECK_MARKER_RE = re.compile(r'\[CHECK:\s*([A-Za-z][A-Za-z \(\)/\'\-]+?)\s+DC\s*(\d+)\s*\]', re.IGNORECASE)
    return _CHECK_MARKER_RE


def _resolve_check(character, skill_raw: str, dc: int) -> dict:
    """Execute a skill check and return an outcome dict."""
    # Normalize skill name — try exact, then title-case, then partial match
    from src.skills import SKILLS
    skill = None
    for s in SKILLS.keys():
        if s.lower() == skill_raw.lower():
            skill = s
            break
    if skill is None:
        for s in SKILLS.keys():
            if skill_raw.lower() in s.lower() or s.lower() in skill_raw.lower():
                skill = s
                break
    if skill is None:
        return {"skill_raw": skill_raw, "resolved_skill": None, "error": f"unknown skill '{skill_raw}'"}

    try:
        result = character.skill_check(skill)
    except Exception as e:
        return {"skill_raw": skill_raw, "resolved_skill": skill, "error": f"check failed: {e}"}

    # skill_check returns either an int total OR a message string (for untrained restricted)
    if isinstance(result, str):
        return {"skill_raw": skill_raw, "resolved_skill": skill, "error": result}

    total = int(result)
    success = total >= dc
    # degree: crit-fail (total <= dc-10), fail (<dc), success (>=dc), crit-success (>=dc+10)
    margin = total - dc
    if margin <= -10:
        degree = "catastrophic failure"
    elif margin < 0:
        degree = "failure"
    elif margin >= 10:
        degree = "exceptional success"
    else:
        degree = "success"
    return {
        "skill_raw": skill_raw, "resolved_skill": skill, "dc": dc,
        "total": total, "success": success, "margin": margin, "degree": degree,
    }


async def speak(character, message: str) -> str:
    """Deliver the player's message to the DM Player and get a response.

    Phase 1–4 entry point. If the DM emits a [CHECK: Skill DC N] marker,
    this function auto-resolves the check and re-prompts the DM once with
    the outcome, returning the combined narration.
    """
    from src.ai import _call_ollama, _config
    from src import scene_state as _scene

    session = load_or_create(character.name)
    scene = _scene.load_or_create(character.name)
    context = _build_context_block(character, scene=scene)
    history_str = _format_history(session.conversation_history)

    user_prompt = (
        f"{context}\n"
        f"CONVERSATION SO FAR:\n{history_str}\n\n"
        f"PLAYER: {message}\n\n"
        f"Respond as The Voice. 2-5 sentences unless the player explicitly asks for more."
    )

    if not _config.get("enabled"):
        return "(The Voice is silent — LLM backend is disabled.)"

    response = await _call_ollama(
        prompt=user_prompt,
        system_prompt=DM_SYSTEM_PROMPT,
        generation_params={"temperature": 0.85, "max_tokens": MAX_RESPONSE_TOKENS},
    )
    response = (response or "").strip().strip('"').strip("'")
    if not response:
        response = "(The Voice hesitates, distracted. Ask again.)"

    # Auto-resolve skill check markers
    m = _check_marker_re().search(response)
    if m:
        skill_raw = m.group(1).strip()
        dc = int(m.group(2))
        outcome = _resolve_check(character, skill_raw, dc)
        # Strip the marker line from the visible response
        visible_pre = response[:m.start()].rstrip()
        if outcome.get("error"):
            roll_line = (f"\n\033[0;33m[Roll]\033[0m {skill_raw} DC {dc}: "
                         f"(could not resolve: {outcome['error']})")
            response = visible_pre + roll_line
        else:
            roll_line = (f"\n\033[0;33m[Roll]\033[0m {outcome['resolved_skill']} "
                         f"DC {outcome['dc']} → total {outcome['total']} "
                         f"({outcome['degree']})")
            # Re-prompt DM with the outcome for narration follow-up
            outcome_ctx = (
                f"{context}\n"
                f"CONVERSATION SO FAR:\n{history_str}\n\n"
                f"PLAYER: {message}\n"
                f"VOICE (partial): {visible_pre}\n"
                f"CHECK OUTCOME: {outcome['resolved_skill']} DC {outcome['dc']} = "
                f"{outcome['total']} — {outcome['degree']} ({'pass' if outcome['success'] else 'fail'})\n\n"
                f"Now narrate the result of the check. 1-3 sentences. Do not emit another check marker."
            )
            followup = await _call_ollama(
                prompt=outcome_ctx,
                system_prompt=DM_SYSTEM_PROMPT,
                generation_params={"temperature": 0.8, "max_tokens": 200},
            )
            followup = (followup or "").strip().strip('"').strip("'")
            response = (visible_pre + roll_line + "\n" + followup).strip()

    now = time.time()
    session.conversation_history.append({"role": "player", "content": message, "ts": now})
    session.conversation_history.append({"role": "dm", "content": response, "ts": now})
    session.turn_count += 1
    session.last_active = now
    save(session)

    _scene.update_from_contact(scene, character, response)
    _scene.save(scene)

    return response
