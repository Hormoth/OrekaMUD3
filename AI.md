# OrekaMUD3 AI System

OrekaMUD3 uses Large Language Models (LLMs) extensively for NPC dialogue, conversation memory, and dynamic roleplay. This document covers every place an LLM is invoked, how it's configured, and what each call costs.

---

## Table of Contents

1. [LLM Backends](#llm-backends)
2. [The Three-Tier Dialogue System](#the-three-tier-dialogue-system)
3. [Per-Feature LLM Usage](#per-feature-llm-usage)
4. [Model Tier Selection](#model-tier-selection)
5. [Memory Systems](#memory-systems)
6. [Context Building](#context-building)
7. [Cost & Performance](#cost--performance)
8. [Configuration](#configuration)

---

## LLM Backends

OrekaMUD3 supports two **local-only** LLM backends. No cloud APIs are used. No per-token costs. Everything runs on your hardware.

| Backend | URL Default | API Format | Best For |
|---------|-------------|------------|----------|
| **Ollama** | `http://localhost:11434` | Native `/api/generate` | Default. Single-binary, easy install. |
| **LM Studio** | `http://localhost:1234` | OpenAI-compatible `/v1/chat/completions` | GUI users, easy model swapping |

Configured in `oreka_mud/src/ai.py`:
```python
_config = {
    "enabled": True,
    "backend": "ollama",
    "ollama_host": "http://localhost:11434",
    "ollama_model": "llama3",
    "lmstudio_host": "http://localhost:1234",
    "lmstudio_model": "local-model",
    "timeout": 15,
}
```

Generation parameters:
- `temperature`: 0.8 (creative roleplay)
- `top_p`: 0.9
- `num_predict`/`max_tokens`: 150 (concise MUD output)

---

## The Three-Tier Dialogue System

Every NPC response goes through `get_npc_response()` in `src/ai.py:417`, which tries each tier in order:

### Tier 1: Scripted Dialogue (Instant, Free)

NPCs with a `dialogue` field in `mobs.json` return that text directly for greeting messages (`hello`, `hi`, `hey`, `greetings`).

**When used:** Simple greetings, deterministic NPC introductions  
**Cost:** Zero (in-memory string lookup)  
**Latency:** <1ms

### Tier 2: Template + Keyword Matching (Fast, Free)

If LLM is disabled or unavailable, falls through to `_get_template_response()` in `src/ai.py:283`:

- **30+ keyword triggers** (`help`, `quest`, `aldenheim`, `elemental`, `kin`, `god`, `magic`, `buy`, `sell`, etc.)
- **7 role-based template pools** (shopkeeper, trainer, banker, blacksmith, guard, innkeeper, no_attack, default)
- **Deterministic seeding** per (NPC name, message hash) — same NPC gives same answer to same question
- **Templates parameterize** with NPC name and room name

**When used:** LLM unavailable, generic NPCs, fallback for slow responses  
**Cost:** Zero (string substitution)  
**Latency:** <1ms

### Tier 3: LLM (Rich Roleplay, Local Compute)

When `_config["enabled"]` is `True` and the backend is reachable, calls `_get_llm_response()` in `src/ai.py:391`:

- Builds a personality prompt from NPC data (name, type, role flags, alignment, description, dialogue)
- Builds a context prompt (room name/description, player level/race/class, time of day)
- Sends to Ollama or LM Studio with 15-second timeout
- Falls back to Tier 2 on timeout or error

**When used:** All NPC interactions when LLM is online  
**Cost:** GPU/CPU compute (typically 1-5 seconds on a decent GPU)  
**Latency:** 1-5 seconds depending on model size

---

## Per-Feature LLM Usage

### 1. `talk <npc> <message>` — Single-shot NPC Conversation

**Function:** `cmd_talkto` in `commands.py`  
**Calls:** `get_npc_response(npc, player, message, room, use_llm=True)`  
**Tier:** Tries 1 → 3 → 2 in order  
**Memory:** None (stateless)

A single back-and-forth. The NPC receives the player's message with their personality and context, and returns one response. No history persists between `talk` invocations.

```
> talk mira hello
Mira the Shopkeeper says: "Welcome, traveler! Looking to buy or sell?"
```

---

### 2. `chat <npc>` — Full AI Conversation Mode

**Function:** Chat session lifecycle in `src/chat_session.py` and `src/ai.py:750` (`get_chat_response`)  
**Calls:** `get_chat_response(session, character)`  
**Tier:** LLM only (Tier 3) — uses structured JSON responses  
**Memory:** Persistent per (NPC vnum, player name)

Enters a dedicated conversation mode. The player drifts into a "dreamstate" and appears as a Shadow Presence visible to others via Kin-sense. The conversation maintains:

- **Full conversation history** (sliding window of last 20 messages)
- **Loaded NPC memory** (top 5 memories by importance from `data/npc_memories/<vnum>/<player>.json`)
- **Lore injection** (queries `data/lore.json` based on NPC's `lore_tags`)
- **World events** (speech and combat in the NPC's room inject as `[WORLD EVENT]` messages)
- **Game actions** (NPC can grant quests, modify reputation, give items, store memories)
- **Conversation summarization** when history grows long

Response uses **structured JSON** for parseable game actions:
```json
{
  "dialogue": "Your in-character speech...",
  "game_actions": [
    {"type": "modify_reputation", "faction": "circle_of_deeproot", "amount": 5}
  ],
  "emotion_state": "reverent",
  "remember": "This player asked about the Breach with genuine concern."
}
```

---

### 3. `rpsay <message>` — Local RP with NPC Reactions

**Function:** `cmd_rpsay` in `commands.py`  
**Calls:** `get_npc_response()` for each LLM-capable NPC in the room (60% chance per NPC)  
**Tier:** Tier 3 (LLM) preferred  
**Memory:** Room-level conversation buffer + per-NPC persistent memory

When a player uses `rpsay`, the message broadcasts to the room and all LLM-capable NPCs (with `dialogue`, `persona`, or friendly flags) may overhear and react.

**Targeted form:** `rpsay (guard) tell me about the patrols` — guarantees the named NPC responds.

Each NPC response prompt includes:
- The room's recent conversation buffer (last 8 exchanges, both player and NPC lines)
- The NPC's persistent memory of past `rpsay` exchanges with this player
- The NPC's last remark for continuity ("Your last remark was: ...")

NPCs can return `...` to stay silent if the topic isn't relevant. Untargeted NPCs have a 60% response rate; targeted NPCs always respond.

Memory is saved to `data/npc_memories/<vnum>/<player>.json` with importance 0.4 per exchange.

---

### 4. NPC Combat AI

**Function:** `get_combat_action_detailed()` in `src/ai.py:477`  
**Calls:** **None** — this is pure decision-tree logic, no LLM  
**Memory:** None

Despite living in `ai.py`, combat AI is **not LLM-driven**. It uses deterministic rules:
- Flee at < 20% HP (30% chance, unless boss/no_flee)
- Use special attacks 25% of the time
- Use combat maneuvers 20% if mob has the relevant feat
- Otherwise: attack lowest-HP player

This keeps combat fast and predictable. LLM cost would be unacceptable for round-by-round combat.

---

### 5. Shadow Presence Voice Lines

**Function:** `src/shadow_presence.py`  
**Calls:** Optional — uses LLM only if a chatting player's NPC speaks  
**Tier:** Inherits from chat session  
**Memory:** Within the active chat session

When a player is in `chat` mode, they appear as a "dreaming presence" in the NPC's room. Other players see them as an echo on Kin-sense. The NPC's voice (via the chat session's LLM) is occasionally broadcast to room observers.

---

### 6. World Event Bleed (DM Agent / MCP Bridge)

**Function:** `src/events.py` `broadcast_event()` and `src/mcp_bridge.py`  
**Calls:** Injects events into active chat sessions for LLM context  
**Tier:** N/A — events bleed into existing LLM calls  
**Memory:** Stored in chat session `world_events_injected`

External agents (a DM agent via MCP bridge on port 8001) can broadcast world events. These are pushed into all active chat sessions as `[WORLD EVENT]` system messages, so when the player's next turn fires the LLM, the NPC sees and reacts to them ("the volcano just erupted in Kharazhad").

---

## Model Tier Selection

`_select_model_tier()` in `src/ai.py:688` picks a model class based on NPC type:

| Tier | NPC Types | Model Recommendation |
|------|-----------|---------------------|
| **Premium** | `faction_leader`, `deity_avatar`, `lore_keeper`, `boss` | Larger model (8B-70B) — quest givers, story-critical NPCs |
| **Standard** | `merchant`, `trainer`, `quest`, `priest`, `banker` | Mid-size model (7B-13B) — most named NPCs |
| **Fast** | Everything else (guards, commoners) | Small model (3B-7B) — quick reactions |

Currently this returns a tier string — actual model swapping per-tier is configured by setting `ollama_model` per backend. Future enhancement: route premium NPCs to a different Ollama model.

---

## Memory Systems

### Persistent NPC Memory (per player)

Files: `oreka_mud/data/npc_memories/<npc_vnum>/<player_name>.json`

Schema:
```json
{
  "npc_vnum": 9304,
  "player_name": "Hormoth",
  "memories": [
    {
      "text": "[RP overheard] Hormoth said: \"...\" — I replied: \"...\"",
      "importance": 0.4,
      "session_id": "rpsay",
      "created_at": 1733512345.67
    }
  ],
  "last_interaction": 1733512345.67,
  "total_sessions": 3
}
```

Functions in `src/chat_context.py`:
- `load_npc_memory(npc_vnum, player_name)` — returns top 5 memories by importance
- `save_npc_memory(...)` — appends, sorts, keeps top 20
- `calculate_importance(response)` — scores 0.3 base + 0.2 per game action

### Room-Level RP Buffer

Module: `src/rp_context.py`

Per-room conversation buffer (deque, max 20 lines, 10-min expiry) holding:
- Player `rpsay` lines
- NPC AI reactions

Used to give NPCs continuity within an active scene without persisting forever.

### Chat Session History

Held in `ChatSession.conversation_history` — full transcript of an active `chat` mode conversation. Sliding window of last 20 messages sent to LLM. Older messages compressed into `_summary` field when history grows long.

Saved to `data/chat_sessions/<session_id>.json` on chat end for review.

---

## Context Building

### NPC Personality Prompt (`_build_npc_personality`)

Built from mob JSON data:
- `name`, `type_`, `flags` (mapped to role descriptions)
- `alignment`
- `description` (full text)
- `dialogue` (default greeting)

### Chat System Prompt (`_build_chat_system_prompt`)

Far richer than `talk` mode. Built from `ai_persona` field in mob data:
- `voice` — how the NPC speaks
- `motivation` — what drives them
- `speech_style` — formal/casual/cryptic
- `knowledge_domains` — what they know
- `forbidden_topics` — what they refuse to discuss
- `secrets` — only revealed when trust is earned
- `lore_tags` — pulls matching entries from `data/lore.json`

Plus dynamic context:
- World state (location, region, time of day)
- Player identity (name, race, class, level, deity, faction standings)
- NPC's memory of this player
- Recent world events
- Conversation summary if long

---

## Cost & Performance

### Latency by Feature

| Feature | LLM Calls | Typical Latency | Acceptable? |
|---------|-----------|----------------|-------------|
| `talk` (single shot) | 1 | 1-5s | Yes (player waits) |
| `chat` (per turn) | 1 | 1-5s | Yes (dedicated mode) |
| `rpsay` (room reactions) | 0-N (1 per responding NPC) | 1.5-3.5s + stagger | Yes (async, non-blocking) |
| Combat | 0 | <10ms | Yes (rules-only) |
| Movement | 0 | <10ms | Yes |

### Resource Usage

- **Ollama llama3 (8B)** on a modern GPU: ~2s per response, ~6GB VRAM
- **Smaller models (3B)**: ~500ms, ~3GB VRAM — good for `rpsay` reactions
- **CPU-only**: 5-15s per response — degrades MUD feel; consider Tier 2 fallback

### Failure Modes

LLM calls fail gracefully:
- **Timeout (15s)**: logs warning, falls back to template (Tier 2)
- **Backend unreachable**: silent fallback to Tier 2
- **Malformed JSON in chat mode**: regex extracts dialogue, defaults other fields
- **Empty response**: skipped (NPC stays silent in `rpsay`)

---

## Configuration

### Switching Backends

In `src/ai.py` or via a runtime command:
```python
from src.ai import set_llm_backend, set_ollama_model
set_llm_backend("lmstudio")  # or "ollama"
set_ollama_model("llama3:70b")  # use a bigger model
```

### Disabling LLM Entirely

```python
from src.ai import enable_llm
enable_llm(False)  # All NPC dialogue falls back to Tier 2 templates
```

The MUD remains fully playable without any LLM — templates and scripted dialogue cover all NPCs.

### Checking Status

```python
from src.ai import get_llm_status, check_ollama_available
status = get_llm_status()
available = await check_ollama_available()
```

---

## File Map

| File | Responsibility |
|------|---------------|
| `src/ai.py` | All LLM calls, template fallback, personality/context building |
| `src/chat_session.py` | Chat session lifecycle, persistence, world event injection |
| `src/chat_context.py` | NPC memory load/save, importance scoring |
| `src/rp_context.py` | Room-level RP buffer, rpsay memory helpers |
| `src/shadow_presence.py` | Dreaming presence visibility during chat |
| `src/events.py` | World event broadcast (used by MCP DM agent) |
| `src/mcp_bridge.py` | REST API on port 8001 for external DM agents |
| `data/lore.json` | 17 canonical lore entries injected by `lore_tags` |
| `data/npc_memories/` | Per-NPC, per-player persistent memory files |
| `data/chat_sessions/` | Saved transcripts of completed chat sessions |

---

## Summary

OrekaMUD3 uses LLMs **strategically** — only where roleplay quality matters, never where speed matters:

- **Combat, movement, mechanics**: zero LLM (rules-based)
- **Casual NPC chatter**: tiered (template fallback)
- **Deep conversations (`chat`)**: full LLM with persistent memory
- **Living world (`rpsay`)**: LLM with room buffer + persistent memory + targeting

Everything runs locally. No telemetry, no API keys, no per-message costs.
