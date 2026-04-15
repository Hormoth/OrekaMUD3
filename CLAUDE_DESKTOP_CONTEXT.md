# OrekaMUD3 — Claude Desktop Context

**Purpose:** Single-file context bundle for Claude Desktop. Upload this as Project Knowledge and Claude can discuss any aspect of the MUD accurately without needing the full codebase.

**Last updated:** 2026-04-13
**Project root:** `C:\data\workspace\OrekaMUD3`

---

## Table of Contents

1. [Project Snapshot](#1-project-snapshot)
2. [Architecture Overview](#2-architecture-overview)
3. [The World of Oreka](#3-the-world-of-oreka)
4. [Game Mechanics (D&D 3.5)](#4-game-mechanics-dd-35)
5. [AI / LLM System](#5-ai--llm-system)
6. [Client Access](#6-client-access)
7. [Data Layer](#7-data-layer)
8. [Command Reference](#8-command-reference)
9. [Current State & Recent Changes](#9-current-state--recent-changes)
10. [Planned Work](#10-planned-work)
11. [Design Principles](#11-design-principles)
12. [How to Help Me](#12-how-to-help-me)

---

## 1. Project Snapshot

| Metric | Value |
|--------|-------|
| **What it is** | A fully playable Multi-User Dungeon implementing D&D 3.5 Edition |
| **Language** | Python 3.13 (async, asyncio) |
| **Lines of code** | ~35,000 across 42 source modules |
| **Tests** | 298 automated (pytest) |
| **Commands** | 340+ registered |
| **World rooms** | 1,624 across 13 areas / 7 regions |
| **Placed mobs** | 373 + 238 bestiary templates |
| **NPCs with full AI persona** | 4 of 373 (gap — see §10) |
| **Clients supported** | Telnet (port 4000), Veil WebSocket (port 8765), Mudlet, TinTin++ |
| **LLM backends** | Ollama, LM Studio (local only, no cloud) |
| **Status** | Production-playable; continuous content expansion |

Public server (if running): `telnet 47.188.185.168 4000`

---

## 2. Architecture Overview

### Servers (running concurrently under a single asyncio event loop)

| Port | Protocol | Purpose |
|------|----------|---------|
| 4000 | Telnet (raw asyncio TCP with GMCP) | Primary MUD interface |
| 8765 | WebSocket | Veil Client proxy, has pre-auth wizard |
| 8001 | HTTP/REST | MCP Bridge — exposes game state to external agents |

### Source layout (`oreka_mud/src/`)

**Core engine:**
- `main.py` — server entry, login flow, connection handling, tick loop
- `commands.py` — ~14K lines, 340+ commands all registered on `CommandParser`
- `character.py` — `Character` class, serialization, stat system
- `combat.py` — D&D 3.5 combat engine, initiative, action economy
- `spells.py` — 82 spells, 8 schools, 23 domains
- `feats.py` — 88 feats with prerequisite trees
- `skills.py` — 40+ skills with synergies
- `classes.py` — 12 classes with full progression tables
- `races.py` — 20 races (15 playable + 5 creature)
- `conditions.py` — 37 conditions with mechanical effects
- `maneuvers.py` — 10 combat maneuvers

**Systems:**
- `quests.py` — 10 objective types, chains, rewards
- `crafting.py` — 60 recipes across 7 disciplines
- `factions.py` — 10 factions, reputation -500 to +600
- `religion.py` — 13 deities, prayer, player ascension
- `kin_sense.py` — elemental 6th-sense detection
- `location_effects.py` — 83 room effects
- `spawning.py` — mob respawn manager
- `schedules.py` — NPC behavior schedules + game time
- `weather.py` — dynamic per-region weather engine
- `area_resets.py` — timed room restoration
- `housing.py` — player homes + furniture with effects
- `narrative.py` — 6-chapter story arc
- `wandering_gods.py` — invisible deity entities

**AI / dialogue:**
- `ai.py` — tiered dialogue (scripted → templates → LLM), both Ollama and LM Studio
- `chat_session.py` — dreamstate chat lifecycle
- `chat_context.py` — NPC memory persistence
- `rp_context.py` — room-level RP conversation buffer
- `shadow_presence.py` — dreaming player visibility
- `veil_auth.py` — Veil Client whitelist + mode gating

**Networking / protocol:**
- `websocket_server.py` — WebSocket proxy with pre-auth wizard + GMCP extraction
- `gmcp.py` — Generic MUD Communication Protocol (12 packages)
- `mcp_bridge.py` — REST API for external agents (port 8001)
- `events.py` — world event broadcasting

**Utility:**
- `items.py`, `mob.py`, `room.py`, `world.py` — core data classes
- `party.py` — group system
- `chat.py` — channels (say, tell, shout with BFS, ooc, etc.)
- `event_log.py` — persistent event log
- `ui.py` — ANSI rendering helpers (progress bars, score cards)

### Key architectural decisions

1. **JSON-driven data** — rooms, mobs, items, quests, recipes, deities, factions all in JSON. No code recompile to add content.
2. **Single source of truth for characters** — `data/players/<name>.json` via atomic writes with backups. Same file whether logged in via MUD or Chat.
3. **Tiered dialogue** — scripted (free) → template (free) → LLM (local compute). Never touches combat.
4. **Local LLM only** — Ollama/LM Studio. No cloud APIs, no per-token costs.
5. **Async everything** — telnet, WebSocket, LLM calls, tick functions all coroutines.

---

## 3. The World of Oreka

### Cosmology

- **4 Elemental Lords** (primordial): Lord of Stone (comatose), Lady of Fire, Lady of the Sea, Youngest Brother / Wind Lord (exiled)
- **9 Ascended Gods** (mortal → divine): Dagdan, Hareem, Tarvek Wen, Ludus Galerius, Apela Kelsoe, Kaile'a, Cinvarin, Semyon, The Hand Unanswered
- **Every Kin race has elemental affinity**: Fire, Water, Earth, Wind, or All-Element Concord
- **Kin-sense**: supernatural sixth sense shared by all Kin — *not magic*, cannot be dispelled

### 7 Regions (1,624 rooms)

| Region | Population | Character | Key Cities |
|--------|-----------|-----------|------------|
| Twin Rivers | Densest | Canopy cities, river trade | Custos do Aeternos (25K), Liraveth (22K), Aerithal (15K) |
| Kinsweave | Sparse | Highland quarries, haunted ruins | Stonefall, Rivertop, Highridge |
| Tidebloom Reach | Medium | Tidal farming, Mithril Chains | Branmill Cove, Velathenor, Tiravel |
| Infinite Desert | Equatorial | Pilgrim roads, volcanic forges | Kharazhad (20K), Dunewell, Solhaven |
| Eternal Steppe | Nomadic | Cavalry brotherhood | Tavranek (6K) + 8 camps |
| Gatefall Reach | Frontier | Silence Breach, Wind-Riders | Hillwatch, Silkenbough, Glimmerholt |
| Deepwater Marches | Jungle | Warg settlements, intelligence trade | Titan's Rest (28K), Canopy Hold, Thornwall |

Plus: Chapel tutorial (25), Chainless Legion (80), ShadeharmonGlade (8), Wilderness Connectors (38).

### The Silence Breach (central narrative)

A growing void in Gatefall Reach where Kin-sense fails. Spreading *down*, not east (secret known only to high-trust NPCs like Warden Kael). 6-chapter main story arc tracks its progression with level-triggered narrative beats.

### 20 Races (15 playable)

- **Elves**: Hasura (Wind), Kovaka (Wind), Pasua (Wind), Na'wasua (Wind)
- **Dwarves**: Visetri (Earth), Pekakarlik (Water), Rarozhki (Fire)
- **Humans**: Orean (Earth), Taraf-Imro (Fire), Eruskan (Water), Mytroan (Wind)
- **Others**: Half-Giant (All), Halfling (Water), Silentborn (None/Null), Farborn Human (None)
- **NPC only**: Half-Domnathar, Warg, Goblin, Hobgoblin, Tanuki

### 10 Factions

| Faction | Type | Role |
|---------|------|------|
| Circle of Deeproot | Joinable | Druid order |
| Golden Roses | Joinable | Law enforcement, Hareem cult |
| Far Riders | Joinable | Cavalry brotherhood |
| Sand Wardens | Joinable | Desert pilgrims/patrols |
| Trade Houses | Joinable | Mercantile guilds |
| The Unstrung | Secret | 600-year-old criminal org |
| Silent Concord | Race-locked | Silentborn organization |
| Chainless Legion | Race-locked | Farborn veterans |
| Gatefall Remnant | Rep only | Survivors of Tomb of Kings |
| Brotherhood of Steppe | Rep only | Mytrone cultural alliance |

---

## 4. Game Mechanics (D&D 3.5)

### Character creation
4d6-drop-lowest stats, racial mods applied live, skill point allocation, feat selection with prereq checking, spell selection, deity/domain choice for Clerics, Magi path selection (Seer/Keeper/Voice).

### Combat (not a simplification — the actual rules)
- d20 + Dex + Improved Initiative feat
- Full action economy: Standard, Move, Swift, Free, Full-Round, Immediate
- BAB-based iterative attacks (+6 → 2 attacks, +11 → 3, +16 → 4)
- Power Attack, Combat Expertise toggles
- Crits with confirmation rolls, Keen (19-20), Vorpal (instant kill)
- Sneak Attack from flanking OR flat-footed OR hidden
- Saving throws (Fort/Ref/Will) with class progression
- Damage Reduction (Barbarian)
- Size modifiers
- Weapon properties (flaming, frost, shock, holy, vorpal)
- Concentration checks (DC 10 + damage)
- Spell Resistance with penetration feats
- 10 combat maneuvers all correctly implemented
- Combat AI (deterministic — flee, target selection, maneuver use)

### Class abilities (all 12 working)
Rage, Inspire Courage, Turn Undead, Wild Shape, Flurry, Smite Evil, Lay on Hands, Divine Grace, Favored Enemy, Evasion, Uncanny Dodge, Combat Style.

### Spellcasting (82 spells, 8 schools, 23 domains)
Prepared vs spontaneous, component enforcement (V/S/M/F/XP), AoE, healing, buffs with duration tracking, dispel, Metamagic (Empower, Maximize, Quicken, Extend, Silent, Still — correct slot-level rules).

### 37 Conditions
All with mechanical modifiers: Blinded (-2 AC, 50% miss), Grappled (no move, -4 Dex), Stunned (no act, drops items), Prone (-4 melee, +4 AC vs ranged), Disarmed (-4, unarmed only), etc. Stack and auto-expire.

### Economy
Shops, banking, auction house (7-day listings), crafting with skill checks and Oreka-exclusive materials (Embersteel, Wind-silk, Riverstone, Moonwhisper Silver, Volcanic Glass, Giant-bone), enchanting up to +5, item sets with set bonuses.

### Death & Respawn
D&D dying rules: 0 HP disabled, -1 to -9 dying + losing 1/round, <= -10 dead. Stabilization check 10%/round. Respawn at chapel with 10% XP penalty. Corpse stays where you died.

---

## 5. AI / LLM System

See `AI.md` for full detail. Key points for discussion:

### Three-tier dialogue cascade (`src/ai.py:417` — `get_npc_response`)

1. **Scripted dialogue** — mob.dialogue field, instant, free
2. **Template + keyword matching** — 30+ keywords, 7 role templates, deterministic seeding
3. **LLM (Ollama or LM Studio)** — rich roleplay, 15s timeout, falls back to tier 2 on failure

### Where LLMs are used

| Feature | LLM calls | Memory |
|---------|-----------|--------|
| `talk <npc> <msg>` | 1 per invocation | None (stateless) |
| `chat <npc>` | 1 per turn | Persistent per (NPC, player) — structured JSON responses with game actions |
| `rpsay <msg>` | 0–N (60% chance per eligible NPC in room) | Room buffer + per-NPC memory |
| Combat AI | **Never** — deterministic rules only | — |

### Memory systems

- **Persistent**: `data/npc_memories/<vnum>/<player>.json` — top 5 by importance, 0.3 base + 0.2 per game action
- **Room-level RP buffer**: `src/rp_context.py` — deque(20), 10-min expiry
- **Chat session history**: sliding window of 20 + rolling summary for long sessions

### Context that already goes into LLM prompts

NPC: name, type, flags-mapped role, alignment, description, dialogue. If `ai_persona` present (only 4 NPCs): voice, motivation, speech_style, knowledge_domains, forbidden_topics, secrets (trust-gated), faction_attitudes, lore_tags → data/lore.json.

Player: name, level, race, class, deity, faction standings.

World: room name, description (if short), time of day.

**Chat mode adds**: full ai_persona, world events injected as `[WORLD EVENT]`, conversation summary, trust-gated secrets, structured JSON response format.

### Critical gap

369 of 373 mobs don't have `ai_persona` fields. That's why most NPC chat feels generic. See BUILDOUT.md §4 for the backfill plan.

### MCP Bridge (NOT an LLM client)

Despite the name, `src/mcp_bridge.py` is a REST API on port 8001 that exposes game state **to** external agents. The MUD itself talks to LLMs via plain `urllib.request` HTTP — no MCP, no Anthropic SDK, no agent framework.

---

## 6. Client Access

### Telnet (port 4000)
Direct MUD access. Mudlet, TinTin++, any MUD client. Full login flow with SHA256 password check.

### Veil WebSocket (port 8765 → pre-auth wizard → telnet)

Since the recent buildout, the Veil Client has its own gate:

```
╔══════════════════════════════════════════════════════════════╗
║                    V E I L   C L I E N T                     ║
║              Step through the Veil. Oreka waits.             ║
╚══════════════════════════════════════════════════════════════╝

  Do you have an existing character? (y/n):
  Username: _
  Password: _

  [+] Welcome back, {name}.

  Choose your path:
    1. Walk OrekaMUD       — Full game
    2. Enter the Dream     — AI Chat with an NPC

  >
```

- Whitelist: `data/veil_whitelist.json` — explicit users OR any existing char (configurable)
- Mode 1 (MUD): auto-login, normal play
- Mode 2 (Chat): auto-login, then auto-runs `chat <npc>` — player drops straight into dreamstate
- **Unified character** — same player JSON file. A Chat-first user who gains quests/items via NPC game actions can later log in via MUD and continue normally.

### Admin command: `@veil`
`@veil list/add/remove/signup/openchars/npcs` — manage whitelist in-game.

### MCP Bridge (port 8001, localhost only)
REST endpoints:
- `GET /world/state`, `GET /room/<vnum>`, `GET /player/<name>`, `GET /npc/<vnum>`, `GET /events/recent`, `GET /shadows`
- `POST /player/<name>/message`

### GMCP (over telnet or WebSocket)
12 packages: Char.Vitals, Char.Status, Char.Factions, Char.Deity, Char.KinSense, Char.Quest, Room.Info, Room.Mobs, Chat.Started, Chat.WorldEvent, Chat.Ended, Chat.Materialized.

---

## 7. Data Layer

All under `oreka_mud/data/`:

### World content
- `areas/*.json` — 14 area files with rooms
- `mobs.json` — 373 placed mobs
- `mobs_bestiary.json` — 238 creature templates
- `items.json` — 98 items + crafting materials
- `recipes.json` — 60 crafting recipes
- `special_materials.json`, `material_prices.json`
- `treasure.json`, `traps.json`

### Game systems
- `deities.json` — 13 deities
- `guilds.json` — 10 factions with ranks
- `creature_types.json`
- `zones.json`, `areas_meta.json`
- `lore.json` — 17 canonical lore entries (injected by NPC lore_tags)
- `help.json` — 90+ help topics
- `achievements.json` — 9+ achievements
- `magi_spells.json`

### Persistence
- `players/<name>.json` — character saves with atomic writes + timestamped backups
- `npc_memories/<vnum>/<player>.json` — per-NPC memory
- `chat_sessions/<session_id>.json` — saved chat transcripts
- `mail/<player>.json` — mailbox
- `boards/<room_vnum>.json` — bulletin boards
- `auctions.json`, `housing.json`, `area_resets.json`, `veil_whitelist.json`
- `events/` — event log

---

## 8. Command Reference

340+ commands. Major categories:

### Movement
`n/s/e/w/u/d`, `exits`, `scan`, `map`, `where`, `speedwalk`, `recall`, `home`, `track`, `consider`

### Character
`score`, `stats`, `skills`, `skilllist`, `feats`, `helpfeats`, `spells`, `spellbook`, `domains`, `affects`, `conditions`, `inventory/i`, `equipment/eq`, `worth`, `tnl/xp`, `progression`, `achievements`, `story`, `lore`, `faction`, `finger`

### Combat
`kill`, `flee`, `fullattack`, `charge`, `totaldefense`, `defensive`, `powerattack`, `combatexpertise`, `disarm`, `trip`, `grapple`, `bullrush`, `overrun`, `sunder`, `feint`, `whirlwind`, `springattack`, `stunningfist`, `queue`, `autoattack`, `target`, `wimpy`

### Class abilities
`rage`, `inspire`, `turn`, `wildshape`, `flurry`, `smite`, `layonhands`, `favoredenemy`

### Spellcasting
`cast`, `prepare/memorize`, `metamagic` (empower, maximize, quicken, extend, silent, still), `components`

### Skills (40+ commands, one per skill)
`hide`, `sneak`, `search`, `openlock`, `disarmtrap`, `tumble`, `climb`, `jump`, `swim`, `listen`, `spot`, `diplomacy`, `bluff`, `intimidate`, `sensemotive`, `appraise`, `knowledge`, `concentration`, `spellcraft`, etc.

### Items & Economy
`get/drop`, `put`, `peek`, `wear/remove`, `list/buy/sell`, `craft`, `recipes`, `scribe`, `brew`, `enchant`, `itemsets`, `compare`, `repair`, `repairall`, `identify`, `examine`, `quaff/drink`, `read`, `use`, `give`, `deposit/withdraw`, `balance`, `auction`, `storage`

### Social
`say`, `tell/reply`, `whisper`, `shout/yell` (BFS radius 3), `ooc/global`, `newbie`, `emote/me`, `rpsay/rp` (with NPC reactions), `60 socials` (bow, wave, laugh, etc.), `who`, `whois/finger`, `afk`, `ignore/block`, `duel`

### Group
`group`, `follow/unfollow`, `assist`, `rescue`, `gtell`

### Guild
`guild create/invite/join/leave/kick/promote/demote`, `clan`

### Communication (AI)
`talk <npc> <msg>` — single-shot
`chat <npc>` — enter dream mode
`rpsay [(npc)] <msg>` — LLM-capable NPCs may react, persistent memory
`endchat`, `enter world`, `chatstatus`

### World systems
`weather`, `weather forecast`, `pray`, `worship`, `deities`, `divine` (bless/smite/manifest/speak/grant), `sense` (kin-sense), `study/activate/repair` (rune-circles), `chapel`

### Housing
`house buy/sell/visit`, `furnish list/buy/remove`, `storage list/store/take`, `home`, `buyroom`, `setdesc`

### Quests
`quest`, `questlog`, `talkto`

### Mail / Boards / Auction
`mail`, `sendmail`, `readmail`, `board`, `post`, `readnote`, `auction list/sell/bid/buyout/collect`

### Survival
`eat`, `drink_water`, `survivalmode`, `rest`, `sleep/wake`, `sit/stand/kneel`, `holdbreath`, `fly/land`, `light/extinguish`

### Travel
`mount/dismount`, `ride`, `swim`, `climb`, `jump`

### Gathering
`fish`, `mine`, `gather`

### Customization
`config/toggle`, `prompt`, `alias`, `title`, `autoloot`, `autogold`, `autosac`, `briefmode`, `compactmode`, `autoexit`

### Utility
`help`, `time`, `who`, `areas/zones`, `leaderboard/top/rankings`, `reputation`, `remort`, `achievements`, `bug/typo/idea`, `changepassword`, `deletechar`

### Admin (requires `is_immortal`)
`@dig`, `@desc`, `@exit`, `@flag`, `@mobadd/edit`, `@itemadd/edit`, `@set*` (30+ field setters), `@resets`, `@veil`, `@backup/restore/save`, `@botrun`, `@admin_deity`, `@gecho`

---

## 9. Current State & Recent Changes

### Production-playable, actively polished
Recent sessions added:
- Dynamic weather engine (8 types, per-region biomes, seasonal)
- Area reset system (configurable timers, combat-safe)
- Full player housing (4 types × 8 furniture with mechanical effects)
- 6-chapter narrative arc with level/room/kill/faction triggers
- Metamagic casting (6 types with D&D slot-level rules)
- `rpsay` with room-level buffer + persistent NPC memory + NPC targeting `rpsay (guard) msg`
- Veil pre-auth wizard with whitelist + MUD/Chat mode selection
- Weather modifiers applied to combat (ranged penalties)
- Narrative hooks wired to room entry, kills, level-ups, faction changes
- Achievement grants on kill/level/craft/exploration events
- Housing effects: +2 craft at workbench, +25% HP on rest with bed
- UI rendering module (ANSI progress bars, score cards, combat prompts)
- 3,966 unicode characters in data files fixed (em dashes, smart quotes, replacement chars)
- GMCP JSON packet leak in WebSocket output fixed (split-packet buffering)
- NPC greeting truncation fixed (`"I..."` no longer becomes `"I."`)
- `broadcast_to_area` BFS traversal works (room._world back-ref set on load)

### Test suite
298 automated tests across 12 files. All passing. One known pre-existing test failure (`test_levelup_command` — not caused by recent work).

---

## 10. Planned Work

Three planning briefs live at the project root — upload alongside this file for full context:

- **`BUILDOUT.md`** — Original LLM buildout: NPC personas, PC sheets, room ambience, environment context, Shadow Chat Game (state machine, eavesdrop/disturb/materialize)
- **`BUILDOUT_ARC_MODULE.md`** — Arc tracking & module format (MUD-side): hidden per-character arc sheets, NPC arc reactions with expression evaluator, structured `check_arc_item` action, module loader, "The Quiet Graft" first module
- **`BUILDOUT_VEIL.md`** — Veil-side arc admin: DM-only Arc Panel (player lookup / module browser / stats dashboard), gateway proxy routes, DM Agent arc-aware decisions (`nudge_arc`, `propagate_resolution`), Electron parity. Depends on MUD §§1-6 of BUILDOUT_ARCS being complete first.

Summary of original BUILDOUT.md:

### The core gap
- **4 of 373** mobs have full `ai_persona` schemas
- **0** PCs have roleplay sheets for LLM injection
- **0** rooms have ambience metadata (mood, sounds, smells, events_history)
- **0** environment context aggregation (weather/politics/events into prompts)

### The 9-section roadmap

1. **Four schemas** — `ai_persona`, `pc_sheet`, `room_ambience`, `environment_context` under `src/ai_schemas/`
2. **Rewrite prompt builders** — use rich data when available, backward-compatible
3. **`rpsheet` command** — players author their own bio/personality/goals/quirks
4. **Backfill ~50 priority NPCs** — faction leaders, deity priests, city stewards, lore keepers, named shopkeepers (hand-authored, not LLM-generated)
5. **The Shadow Chat Game** — state machine formalization, witness/intrusion (eavesdrop/disturb), materialization with HP cost, 5 exit paths, admin endpoints
6. **Content quality checks** — persona validator, prompt length audit, smoke chat test
7. **Out of scope** — no cloud LLM, no LLM-generated personas, no voice/image, no LLM in combat

### Explicit non-goals
- Cloud LLM backends (Anthropic, OpenAI) — stay local only
- Machine-generated personas — hand-authored only
- LLM-driven combat decisions — deterministic forever

---

## 11. Design Principles

These are load-bearing. When Claude Desktop suggests changes, they should respect these:

1. **D&D 3.5 is the actual rule system, not a skin.** If a combat suggestion doesn't match 3.5, it's wrong.
2. **Local LLM only.** No cloud APIs, no per-token costs, no telemetry.
3. **Tiered dialogue stays cheap.** Cheap NPCs get cheap templates. LLM is opt-in per NPC via `chat_eligible`.
4. **Combat is deterministic.** LLMs are for roleplay, not decisions that should be fast and reproducible.
5. **Data layer is JSON.** Adding content should never require code changes.
6. **Single character across modes.** MUD and Chat share the same player file — quest progress carries over either direction.
7. **Respect the setting.** Oreka is not generic fantasy. Elemental Lords, Ascended Gods, Kin-sense, Silence Breach — these are load-bearing worldbuilding, not flavor.
8. **Hand-authored content beats generated content.** 50 great personas > 500 mediocre ones.
9. **Backward compatibility on character files.** Existing characters must load after any schema change (with migration if needed).
10. **Async everything.** No blocking I/O on the main event loop.

---

## 12. How to Help Me

### Good use cases for Claude Desktop

- **Design discussions**: "Should I add a `mood` field to rooms? What are the trade-offs?"
- **Writing personas**: "Draft an ai_persona for Captain Vess of the Golden Roses based on the existing Kael exemplar style."
- **Lore authoring**: "Write a lore entry about the Fall of Aldenheim in the style of existing lore.json entries."
- **Code review**: "Here's my new `cmd_rpsheet` — does it follow the existing command patterns?"
- **Quest design**: "Design a 3-stage quest that takes the player from Custos to Gatefall and connects to the Silence Breach arc."
- **Bug investigation**: "The Veil Client shows duplicate room descriptions. Here's the websocket_server.py. Where's the issue?"
- **Feature planning**: "I want to add a dueling tournament system. Break it into phases that respect the Design Principles."

### Bad use cases

- Generating 50 ai_persona files at once — the point is hand-authored quality
- Suggesting cloud LLM integration — explicitly out of scope
- Suggesting non-D&D 3.5 combat changes
- Refactoring working systems for "cleaner code" without a real bug

### When answering, prefer

- **Concrete over abstract**: reference specific files, line numbers, existing patterns
- **Small diffs over big rewrites**
- **Respect existing vocabulary**: `ai_persona`, `PcSheet`, `RoomAmbience`, `chat_eligible`, `rpsay`, etc.
- **Cite the relevant Design Principle** when making trade-off calls

---

## Quick Facts for Reference

- **Starting room**: vnum 1000 (Central Aetherial Altar) — Chapel tutorial
- **Respawn room**: same as starting
- **Max level**: 20 (then `remort` for +1 all stats, +10 HP, reset to 1)
- **XP table**: levels 1-20, 0 → 190,000
- **Combat round**: 6 seconds (D&D 3.5 adapted)
- **Game time**: 60:1 ratio (1 real minute = 1 game hour)
- **Chat timeout**: 30 minutes idle
- **Mob respawn**: 5 min default, 15 min for bosses, never for unique/quest
- **Area reset**: 15 min default
- **Weather tick**: ~5 minutes per region
- **Auction listing**: 7 days
- **Character file backup**: on every save

---

**End of context bundle.** Upload to Claude Desktop Project Knowledge for full-context discussions about OrekaMUD3.
