# OrekaMUD3 — LLM Buildout & Shadow Chat Game

**Target agent:** Claude Code (or similar CLI coding agent) working inside the `oreka_mud` repo.
**Goal:** Close the gap between the richly-designed LLM prompt builders and the nearly-empty data they consume. Ship the Shadow Chat Game as a first-class feature.

**Rule for the agent:** Do the sections in order. Each section has acceptance criteria. Do not skip schemas to get to the fun parts — the Chat Game depends on them.

---

## 0. Context (read this first)

The engine is complete. The diagnostic found:

- **NPCs:** Only 4 of 373 have `ai_persona` fields (vnums 3000, 9004, 9010, 9200). The other 369 fall back to auto-built personality from `name / type_ / flags / alignment / description / dialogue`. That's why most chat feels generic.
- **PCs:** The LLM sees a single line: `"Speaking to: Hormoth, a level 3 Taraf-Imro Human Fighter."` No backstory, goals, recent events.
- **Rooms:** Only `name / description / exits / flags`. No `mood`, `ambient_details`, `events_history`, `npc_relevance`.
- **Environment:** Only time of day is injected. No weather, season, regional politics, active world events.
- **Prompt builders know how to use rich data — the data just doesn't exist.**

The fix is **content + schema**, not engine work. The engine is right.

**Do not touch:**
- Combat AI (`get_combat_action_detailed` in `src/ai.py`). It's deterministic and should stay that way.
- The tier system (scripted → template → LLM). It's correct.
- The Ollama/LM Studio backends. Correct choice for local.

---

## 1. Add the four schemas

Create a new package: `oreka_mud/src/ai_schemas/`.

### 1.1 `src/ai_schemas/ai_persona.py`

Canonical NPC character sheet. Authored fields on `mobs.json`:

```python
@dataclass
class FactionAttitude:
    faction_id: str                   # "circle_of_deeproot"
    baseline: str                     # loyal | friendly | neutral | wary | hostile
    notes: str = ""

@dataclass
class AiPersona:
    # Identity
    voice: str                        # 1–2 sentences on HOW they speak
    motivation: str                   # 1 sentence on what drives them
    speech_style: str                 # see SPEECH_STYLES vocabulary
    opening_line: str                 # greeting when chat begins
    farewell_line: str                # goodbye when chat ends

    # Knowledge
    knowledge_domains: list[str]      # topics they speak to with authority
    forbidden_topics: list[str]       # topics they refuse/deflect
    lore_tags: list[str]              # keys into data/lore.json
    secrets: list[str]                # "trust_threshold:text" — revealed at threshold

    # Relationships
    faction_attitudes: list[FactionAttitude]
    relationship_hooks: list[str]     # "Warden Kael — old comrade, disagrees on Breach strategy"

    # Filtering / routing
    chat_eligible: bool = True        # False = chat <npc> refuses (mute beasts)
    model_tier: str = "standard"      # premium | standard | fast
    default_emotion: str = "neutral"
```

**SPEECH_STYLES vocabulary** (keep small, concrete, high-signal):
`formal, casual, cryptic, clipped, reverent, boisterous, wary, scholarly, flirtatious, soldierly, archaic, silentborn`

**EMOTION_STATES vocabulary:**
`neutral, warm, guarded, amused, reverent, grim, curious, irritated, grieving, defensive, joyful, frightened, conspiratorial, bored, watchful`

**Secret format:** `"trust_threshold:text"` where threshold ∈ `{casual, warm, trusted, allied}`. The chat session computes effective trust from `faction_attitudes` + past interaction count + quest completions, then filters secrets whose threshold is met.

**Add a `validate_persona(dict) -> list[str]` function** that checks required fields, vocabulary membership, and secret prefix format. Call it on load.

**Add `persona_stub_from_mob(mob: dict) -> dict`** — produces a TODO-filled stub from an existing bare mob, used by the bulk backfill script. Infer `speech_style` and `model_tier` from `flags` + `alignment` via these rules:

- `priest | deity_avatar | lore_keeper` → `reverent`, `premium`
- `guard | soldier | watch` → `soldierly`, `fast`
- `innkeeper` → `boisterous`, `standard`
- `shopkeeper | merchant | banker` → `casual`, `standard`
- `faction_leader | boss` → keep style blank for human editing, `premium`
- alignment contains `evil` → default style `wary`
- else → `casual`, `fast`

### 1.2 `src/ai_schemas/pc_sheet.py`

Player roleplay sheet attached to `Character`:

```python
@dataclass
class RecentEvent:
    text: str                         # "Killed my first Dómnathar scout in Silkenbough."
    timestamp: float
    category: str                     # combat | quest | social | death | discovery | general
    weight: float                     # 0.0–2.0 — prompt inclusion priority

@dataclass
class PcSheet:
    # Player-authored via `rpsheet` command
    bio: str = ""                     # 1–3 sentences of background
    personality: str = ""             # 1–2 sentences of demeanor
    goals: list[str] = []             # short and long term
    quirks: list[str] = []            # observable tics (max 5)
    pronouns: str = "they/them"

    # Engine-authored
    recent_events: list[RecentEvent]  # rolling window of 10
    titles_earned: list[str]          # from achievements
    notable_kills: list[str]          # bosses/unique mobs, last 5
    deaths: int = 0
    remorts: int = 0
    npc_relationships: dict[str, str] # vnum → allied|trusted|warm|neutral|wary|hostile

    # Privacy
    sheet_visible_in_prompts: bool = True
```

**Engine hooks to wire up:**

- On boss kill: `record_notable_kill(sheet, mob.name)` + `record_event(sheet, f"Killed {mob.name} in {room.name}.", "combat", weight=1.5)`
- On quest complete: `record_event(..., "quest", weight=1.3)`
- On death: `sheet.deaths += 1; record_event(..., "death", weight=1.8)`
- On remort: `sheet.remorts += 1`
- On achievement grant: `sheet.titles_earned.append(title)`

**`summarize_for_prompt(sheet, char, max_chars=600) -> str`** produces the block injected into NPC prompts. If sheet is empty/hidden, return the existing 1-liner for backwards compat. Rank recent events by `(recency × weight)` and keep top 3.

### 1.3 `src/ai_schemas/room_ambience.py`

Optional ambience block on room JSON:

```python
@dataclass
class RoomAmbience:
    mood: str = ""                    # "tense", "reverent", "festive", "abandoned"
    sounds: list[str] = []            # "distant hammer-ring from the forge below"
    smells: list[str] = []            # "wet stone and lamp oil"
    textures: list[str] = []          # "the floor hums faintly underfoot"
    ambient_details: list[str] = []   # 1-sentence atmospheric flavors, rotated in prompt
    npc_relevance: dict[str, str] = {} # vnum → "why this NPC belongs here"
    events_history: list[str] = []    # last 5 notable events that happened here
    seasonal_variants: dict[str, str] = {}  # season_name → description override
    time_variants: dict[str, str] = {}      # "dawn"|"day"|"dusk"|"night" → override
```

**Priority regions to author first** (high-traffic, chat-heavy):
1. Central Aetherial Altar (room 1000) — tutorial, must be rich
2. All chapel rooms — starting area
3. Custos do Aeternos town rooms — biggest city
4. Kharazhad forge rooms — distinctive setting
5. Gatefall Reach frontier rooms — story-critical for Chapter 2+

Lower-priority rooms keep `ambience = None` and the prompt builder falls back to `description`.

### 1.4 `src/ai_schemas/environment_context.py`

Not a schema per se — a context builder that aggregates live world state:

```python
def build_environment_context(char, room) -> dict:
    return {
        "time_of_day": get_game_time().phase,        # dawn|day|dusk|night
        "season": get_game_time().season,            # deepwinter|...|yearsend
        "weather": get_weather(room.region),         # current WeatherState
        "weather_forecast": get_forecast(room.region),
        "region": room.region,
        "region_politics": get_region_tensions(room.region),
        "active_world_events": get_active_events(scope=("global", room.region)),
        "nearby_shrine_status": get_nearby_shrine(room.vnum),
        "story_chapter": char.story.current_chapter,
    }
```

Most of this data already exists in your weather engine, narrative engine, and MCP bridge — it just isn't being plumbed into the LLM. This function is the plumbing.

### Acceptance — Section 1

- [ ] Four files created under `src/ai_schemas/`.
- [ ] `validate_persona` catches missing fields, bad vocabulary, malformed secrets.
- [ ] `mobs.json` loader calls `validate_persona` on any mob with a persona and logs warnings (not fatal).
- [ ] Unit tests cover: valid persona, missing required field, bad speech_style, bad secret prefix.

---

## 2. Rewrite the prompt builders

Edit `src/ai.py`. Keep the function signatures so existing callers don't break.

### 2.1 `_build_npc_personality(mob)` — used by `talk` (Tier 3 single-shot)

Current: reads `name, type_, flags, alignment, description, dialogue`.

New: if `mob.get("ai_persona")` exists, build from that. Otherwise keep the existing auto-build. Prompt shape:

```
You are {name}, a {type_} in Oreka.
Voice: {persona.voice}
Speech style: {persona.speech_style}
Motivation: {persona.motivation}

You know about: {knowledge_domains}
You refuse to discuss: {forbidden_topics}

Stay in character. Keep replies under 3 sentences unless the player asks
for detail. Never break the fourth wall. Never reveal secrets unless
trust is established.
```

### 2.2 `_build_chat_system_prompt(session, character)` — used by `chat` mode

The big one. Must assemble five context blocks in this order:

1. **NPC persona block** — full `ai_persona` including lore_tags resolved against `data/lore.json`
2. **PC sheet block** — from `summarize_for_prompt(character.rp_sheet, character)`
3. **Room ambience block** — from `RoomAmbience` if present, else `room.description`
4. **Environment block** — from `build_environment_context`
5. **Memory block** — existing top-5 memories + rolling summary

**Secrets filtering:** Compute trust level before rendering:

```python
def effective_trust(npc_persona, character) -> str:
    # 1. Start from faction_attitudes → character's faction standings
    # 2. +1 tier per 10 prior meaningful interactions (from npc_memory)
    # 3. +1 tier per completed quest granted by this NPC
    # Clamp to {casual, warm, trusted, allied}
```

Only include secrets whose threshold ≤ effective_trust.

**Structured JSON response — keep the existing schema** but enforce it more strictly. Parse failures should strip code fences, then try a regex fallback to extract `dialogue`. If all fails, emit the farewell_line and end the session gracefully.

### 2.3 New builder: `_build_rpsay_npc_prompt(mob, room, speaker, message)`

`rpsay` currently reuses `get_npc_response` with a truncated prompt. Give it its own builder that adds:

- The room's recent conversation buffer (last 8 exchanges)
- The speaker's PC sheet (abbreviated)
- Explicit instruction: **"Return the single token `...` if the topic doesn't concern you."**
- The NPC's own last remark in this room for continuity

### Acceptance — Section 2

- [ ] `talk` still works on NPCs without personas (regression test).
- [ ] `chat` on Warden Kael (9010) uses his full persona including secrets filtered by trust.
- [ ] `rpsay` in a room with a guard and a priest generates 0–2 reactions, not always both.
- [ ] A malformed LLM JSON response does not crash the session — it ends with the farewell.

---

## 3. Add the `rpsheet` command

New file or add to `src/commands.py`:

```
rpsheet                        — view your sheet
rpsheet bio <text>             — set 1–3 sentence background
rpsheet personality <text>     — set demeanor
rpsheet goal add <text>        — add a goal
rpsheet goal remove <#>        — remove goal by number
rpsheet quirk add <text>       — add observable quirk (max 5)
rpsheet pronouns <text>
rpsheet hide                   — hide from NPC prompts
rpsheet show                   — show to NPC prompts (default)
rpsheet clear <field>          — wipe a specific field
```

Persist as part of the character JSON save. Add a migration that initializes an empty `PcSheet` on load for existing characters.

GMCP: add `Char.RpSheet` package pushing sheet on change so the Veil Client can render an RP panel.

### Acceptance — Section 3

- [ ] `rpsheet` command registered and documented in `help rpsheet`.
- [ ] Existing characters load without error (migration works).
- [ ] An LLM NPC's response demonstrably changes when a PC sets a bio (manual test: set "I am terrified of fire," then `talk` to a Kharazhad forge-priest and verify the NPC acknowledges it).

---

## 4. Backfill ~50 priority NPCs

Create `scripts/backfill_personas.py` that:

1. Loads `data/mobs.json`.
2. For each vnum in `PRIORITY_VNUMS` that lacks `ai_persona`, calls `persona_stub_from_mob` and writes the stub into a per-NPC file: `data/personas/{vnum}_{slug}.json`.
3. Prints a TODO checklist for the builder.

Then **author them by hand** using the exemplar below as a pattern. Do not ship TODO-filled stubs to production.

### Priority list (~50 NPCs)

- **Faction leaders (5):** heads of Circle of Deeproot, Golden Roses, Far Riders, Sand Wardens, Trade Houses
- **Deity priests (9):** one per Ascended God, at their main shrine
- **Chapel tutorial (3):** Guide Priestess Elia (✓), plus two helpers
- **City mayors/stewards (7):** one per major settlement (Custos, Liraveth, Kharazhad, Titan's Rest, Tavranek, Dunewell, Hillwatch)
- **Lore keepers (5):** Aldenheim scholar, Silence Breach researcher, Keeper-lineage historian, Mithril Chains engineer, Wind-Rider archivist
- **Named shopkeepers (8):** Mira (✓), Lyssa (✓), plus one signature merchant per region
- **Named trainers/guildmasters (6):** Thorin plus one per major class hub
- **Secret faction contacts (3):** one Unstrung, one Silent Concord Choir Mother, one Chainless Legion veteran
- **Quest NPCs (4):** Kael (✓) plus three more frontier/quest hubs

### Exemplar persona — use as a template

```json
{
  "vnum": 9010,
  "name": "Warden Kael Ridgeborn",
  "ai_persona": {
    "voice": "Low, even, measured. Never raises it. Pauses before hard questions like he's weighing the road for weight.",
    "motivation": "Keep the Gatefall road open for one more season. After that, let someone else decide.",
    "speech_style": "clipped",
    "opening_line": "You're new. Keep your voice down — the Breach carries. What do you need?",
    "farewell_line": "Walk watchful. The road doesn't forgive twice.",
    "knowledge_domains": [
      "gatefall_reach",
      "silence_breach",
      "wind_riders",
      "cavalry_tactics",
      "frontier_survival"
    ],
    "forbidden_topics": [
      "his_daughter",
      "the_night_at_hillwatch"
    ],
    "lore_tags": [
      "gatefall_reach",
      "silence_breach",
      "wind_riders"
    ],
    "secrets": [
      "warm:The Wind-Riders lost three scouts last moon. Command doesn't want it public.",
      "trusted:The Breach isn't spreading east like we told the Council. It's spreading down.",
      "allied:I was at Hillwatch the night it fell. I'm the reason the signal fires never lit."
    ],
    "faction_attitudes": [
      {"faction_id": "gatefall_remnant", "baseline": "allied", "notes": "Kin — his sister-in-law is among them."},
      {"faction_id": "golden_roses", "baseline": "wary", "notes": "Thinks they grandstand while the frontier bleeds."},
      {"faction_id": "the_unstrung", "baseline": "hostile", "notes": "Will alert the watch if they're named."}
    ],
    "relationship_hooks": [
      "Captain Vess of the Golden Roses — respects her, doesn't trust her mission.",
      "Scout Kaivos of the Far Riders — rode with him twenty years ago.",
      "Sister Ilaine (Hareem priest at Silkenbough) — owes her a debt he won't name."
    ],
    "chat_eligible": true,
    "model_tier": "premium",
    "default_emotion": "watchful"
  }
}
```

### Acceptance — Section 4

- [ ] `scripts/backfill_personas.py` runs and produces 46+ stub files.
- [ ] 8 exemplars are fully authored (not stubs).
- [ ] Validation passes on all authored personas.
- [ ] Smoke test: `chat` with each of the 8 exemplars produces opening_line, accepts 3 exchanges without crashing, and ends with farewell_line.

---

## 5. The Shadow Chat Game

This is the headline feature. Everything above is infrastructure for this.

### 5.1 Concept

When a player types `chat <npc>`, they drift into a **dreamstate** conversation with the NPC. While dreaming, their body remains in its physical room, visible to other players as a **Shadow Presence** — a dreaming echo that registers on Kin-sense as faint "echo" resonance. This is already partially built (`src/shadow_presence.py`). This section makes it a real game.

### 5.2 The six mechanics that make it a *game*, not just a chat

1. **Entry ritual** — `chat <npc>` fades the screen, the NPC's opening_line arrives, and the player is in. Other players in the player's physical room see `"Hormoth's eyes go distant. A faint echo rises from them — they are dreaming."` Other players in the NPC's room see `"A shadow of Hormoth drifts into view beside {npc_name}, half-real, half-dream."`

2. **NPC-driven game actions** — NPCs can, via structured JSON, modify the world during conversation. Authored per-NPC in `allowed_actions`:
   - `modify_reputation(faction, amount)` — max ±10 per chat
   - `grant_quest(quest_id)` — only if player qualifies
   - `give_item(vnum)` — only from NPC's `gift_pool`
   - `remember(text)` — store long-term memory with importance
   - `summon_world_event(event_id)` — premium NPCs only, rate-limited
   - `offer_trust(new_threshold)` — manually upgrade trust for this player
   - `bless(deity_id)` — priest NPCs only, applies a shrine buff
   - `mark_player(tag)` — adds a faction-visible tag (e.g. "witnessed_by_kael")

3. **Witness/intrusion mechanic** — While the PC is dreaming, another player can:
   - `look` at their body and see the shadow effect
   - Use `kin-sense` and perceive the echo at reduced clarity
   - `eavesdrop <player>` — if the eavesdropper succeeds at a Listen check vs the dreaming PC's Will save, they see the last 3 lines of the chat transcript (redacted — NPC name replaced with `"a distant voice"`)
   - `disturb <player>` — ends the chat session immediately, with a consequence: the NPC marks the disturbing player as `interrupted_my_counsel` and their next interaction starts at `wary`

4. **World bleed** — Events in the real world push into the chat as `[WORLD EVENT]` lines. Already partially implemented. Expand to:
   - Weather changes in the dreaming PC's physical region
   - Another player speaking in the NPC's physical room (`rpsay` bleeds through)
   - Combat nearby the NPC
   - The dreaming PC taking damage (triggers NPC concern line + session may auto-end)

5. **Materialization** — The player can type `enter world` during chat to step OUT of dream and INTO the NPC's physical room as a real, moving character. This is a **one-way teleport** with costs:
   - 10% of max HP (cost of manifesting)
   - 1 hour in-game cooldown before next chat
   - Broadcast to the NPC's room: `"The air shivers. {player} steps out of a shadow and into the room."`
   - All active dream sessions with other NPCs end immediately

6. **Exit states** — Chat ends in one of these ways:
   - `endchat` — clean exit, farewell_line, return to body
   - `enter world` — materialize (above)
   - Disturb/attack — forced end, trust penalty
   - Timeout — 10 min real-time idle, NPC gives a patience line and ends
   - Death of PC body — catastrophic end, NPC's last line is alarmed

### 5.3 Session state machine

```
IDLE
  │ chat <npc>
  ▼
ENTERING ──(fade, opening_line)──▶ ACTIVE
                                    │
                                    ├─ endchat ───▶ EXITING_CLEAN ──▶ IDLE
                                    ├─ enter world ─▶ MATERIALIZING ─▶ IDLE (physical)
                                    ├─ disturbed ──▶ EXITING_FORCED ─▶ IDLE (penalty)
                                    ├─ timeout ───▶ EXITING_PATIENCE ▶ IDLE
                                    └─ body_death ─▶ EXITING_PANIC ──▶ IDLE (unconscious)
```

Implement as a state enum on `ChatSession`. Each transition emits appropriate broadcasts.

### 5.4 Chat UX — rendering

Keep the dreamlight framing from the existing design:

```
  ~ You feel yourself drift...

  The Central Altar hums with quiet warmth. Guide Priestess Elia
  looks up from her work as you approach.

  Elia says: "Ah. Another traveler steps through. Welcome to Oreka."

[Chat: Guide Priestess Elia] > _
```

Add these small touches:
- NPC emotion displayed in brackets when it changes: `Elia [reverent] says: "..."`
- `[WORLD EVENT]` lines rendered in dim gray
- Trust upgrade moments rendered with a soft highlight: `~ You feel Elia's guard lower slightly. ~`
- The `[Chat: {npc}]` prompt token is stable so the player always knows whose dream they're in

### 5.5 Admin observability

The DM/MCP bridge should expose:

- `GET /chat/active` — list active chat sessions (player, npc, duration, trust)
- `GET /chat/{session_id}` — full transcript
- `POST /chat/{session_id}/inject` — inject a WORLD EVENT line into this specific chat
- `POST /chat/{session_id}/force-end` — kick the session cleanly

This lets a human DM or an external agent nudge conversations.

### Acceptance — Section 5

- [ ] State machine implemented with all 5 exit paths tested.
- [ ] Shadow Presence renders to physical-room observers AND to NPC-room observers.
- [ ] `eavesdrop` works with Listen vs Will opposed check.
- [ ] `disturb` ends the session and records the trust penalty.
- [ ] `enter world` materializes the PC and costs 10% HP.
- [ ] A weather change during an active chat produces a `[WORLD EVENT]` line.
- [ ] Chat sessions save to `data/chat_sessions/{session_id}.json` with full transcript and state transitions.
- [ ] Admin endpoints live under `/chat/` on the MCP bridge.

---

## 6. Content quality checks

Before merging, run these:

1. **Persona validation pass** — `python scripts/validate_personas.py` zero errors.
2. **Prompt length audit** — `python scripts/audit_prompt_lengths.py` shows every chat system prompt under 2500 tokens (else summarize more aggressively).
3. **Smoke conversation test** — `python scripts/smoke_chat.py` runs a scripted 10-turn chat with each of the 8 exemplar NPCs, asserting opening_line, 3 mid-exchanges without parse failure, farewell_line, and memory persisted to disk.
4. **Regression** — existing 298-test suite passes unchanged.

---

## 7. Out of scope (explicitly do not do)

- Do not add a cloud LLM backend. Local only.
- Do not generate `ai_persona` with the LLM. Hand-author the 50 priority NPCs. Machine generation produces generic personas and defeats the whole point.
- Do not add voice chat, image generation, or anything that isn't text.
- Do not replace the three-tier dialogue system. It's correct — cheap tiers for cheap NPCs.
- Do not give combat LLM-driven decisions. It's fast and deterministic on purpose.

---

## 8. Milestone ordering

1. Schemas (Section 1) — no player-visible change, unblocks everything.
2. Prompt builders (Section 2) — existing 4 personas instantly get better.
3. `rpsheet` command (Section 3) — players start filling in bios.
4. First 8 exemplar personas (Section 4 partial) — demo-ready for chat testing.
5. Shadow Chat Game (Section 5) — the headline feature ships.
6. Remaining 42 persona backfills (Section 4 full) — world fills in over a few weeks.
7. Content quality checks (Section 6) — shippable.

---

## 9. File manifest when complete

```
oreka_mud/
├── src/
│   ├── ai.py                              # MODIFIED — new prompt builders
│   ├── ai_schemas/                        # NEW
│   │   ├── __init__.py
│   │   ├── ai_persona.py
│   │   ├── pc_sheet.py
│   │   ├── room_ambience.py
│   │   └── environment_context.py
│   ├── character.py                       # MODIFIED — adds PcSheet
│   ├── chat_session.py                    # MODIFIED — state machine + 5 exits
│   ├── commands.py                        # MODIFIED — rpsheet, eavesdrop, disturb, enter world
│   ├── shadow_presence.py                 # MODIFIED — bidirectional room rendering
│   └── mcp_bridge.py                      # MODIFIED — /chat admin endpoints
├── data/
│   ├── personas/                          # NEW — 50 per-NPC persona files
│   │   └── {vnum}_{slug}.json
│   └── mobs.json                          # MODIFIED — references to personas/
├── scripts/
│   ├── backfill_personas.py               # NEW
│   ├── validate_personas.py               # NEW
│   ├── audit_prompt_lengths.py            # NEW
│   └── smoke_chat.py                      # NEW
└── tests/
    ├── test_ai_schemas.py                 # NEW
    ├── test_prompt_builders.py            # NEW
    ├── test_rpsheet.py                    # NEW
    └── test_shadow_chat_game.py           # NEW
```

---

**End of brief.** When each section's acceptance criteria are green, move to the next. Do not batch commits across sections — the review value is per-section.
