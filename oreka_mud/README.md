# OrekaMUD3

A D&D 3.5 OGL multi-user dungeon set in the world of Oreka, built from scratch in Python with async telnet and WebSocket support.

**33,000+ lines of code | 1,624 rooms | 373 mobs | 321 commands | 88 feats | 82 spells | 60 crafting recipes | 13 deities | 10 factions | 300 automated tests**

## Quick Start

```bash
cd oreka_mud
pip install telnetlib3 websockets
python main.py
```

Connect via telnet: `telnet localhost 4000` or any MUD client (MudLet, TinTin++, etc.) on port 4000.

Connect via browser: Open `veil_client.html` (WebSocket on port 8765).

Public server: `telnet 47.188.185.168 4000`

---

## The World of Oreka

Oreka is a continent shaped by four Elemental Lords -- Stone, Fire, Sea, and Wind. Two parallel Giant's Teeth mountain ranges flank an equatorial desert corridor, dividing civilization into northern and southern hemispheres.

### Regions

| Region | Location | Character | Key Cities |
|--------|----------|-----------|------------|
| **Twin Rivers** | Northwest | Densest population, river trade, canopy cities | Custos do Aeternos (25K), Liraveth (22K), Aerithal (15K), Greenford (8.5K), Stoneharbor (6.8K) |
| **Kinsweave** | North-center | Highland quarries, haunted ruins, pilgrimage | Stonefall, Rivertop, Highridge, Lakeshore, Lakewell + 6 ruins |
| **Tidebloom Reach** | Northeast | Tidal farming, Mithril Chains, lake trade | Branmill Cove, Velathenor, Tiravel, Myruvane, Darnavar + 4 ruins |
| **Infinite Desert** | Equatorial belt | Pilgrim roads, oasis cities, volcanic forges | Kharazhad (20K), Dunewell, Solhaven, Ashgarin Fold, Sandsong |
| **Eternal Steppe** | South-center | Horse breeding, cavalry, nomadic camps | Tavranek (6K) + 8 semi-permanent camps |
| **Gatefall Reach** | Southeast | Frontier, Silence Breach, Wind-Riders | Hillwatch, Silkenbough, Glimmerholt, Brayholt, Redtrail, Briarshade |
| **Deepwater Marches** | Southwest | Dense jungle, Warg settlements, intelligence trade | Titan's Rest (28K), Tidewell, Canopy Hold, Thornwall, Murtavah Root |

### World Stats

- **1,624 rooms** across 13 area files
- **373 mobs** (276 hostile, 85 friendly NPCs, 5 tutorial)
- **238 bestiary creatures** (D&D 3.5 compatible template library)
- **88 items** with 12 special material types
- **83 active location effects** (Kin-sense modifiers, elemental resonance, hazards, rune-circles, sanctuaries)
- **100% room connectivity** verified by AI bot explorer
- **6 wilderness corridors** connecting regions through mountain passes and desert roads

---

## Races (20)

### Playable Kin Races
| Race | Element | Kin-Sense | Size |
|------|---------|-----------|------|
| Hasura Elf | Wind | Harmonic | Medium |
| Kovaka Elf | Wind | Harmonic | Medium |
| Pasua Elf | Wind | Harmonic | Medium |
| Na'wasua Elf | Wind | Harmonic | Medium |
| Visetri Dwarf | Earth | Harmonic | Medium |
| Pekakarlik Dwarf | Water | Harmonic | Small |
| Rarozhki Dwarf | Fire | Harmonic | Medium |
| Halfling | Water | Harmonic | Small |
| Orean Human | Earth | Harmonic | Medium |
| Taraf-Imro Human | Fire | Harmonic | Medium |
| Eruskan Human | Water | Harmonic | Medium |
| Mytroan Human | Wind | Harmonic | Medium |
| Half-Giant | All | Harmonic | Large |
| Silentborn | None | Null | Medium |
| Farborn Human | None | None (invisible) | Medium |

### NPC Races
| Race | Kin-Sense | Notes |
|------|-----------|-------|
| Half-Domnathar | Harmonic (cracked) | Domnathar-touched, discordant resonance |
| Warg | Breach Static | Sapient wolf-warriors, freed servitors |
| Goblin | Breach Static | Freed servitors, diverse tribal societies |
| Hobgoblin | Breach Static | Disciplined military, Deceiver remnants |
| Tanuki | Wild Static | Raccoon-folk shapeshifters, trickster-artisans |

---

## Classes (12)

Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Wizard, Magi

All follow D&D 3.5 OGL rules with full:
- Hit dice, BAB progression, save progression
- Class skill lists
- Spell slots and preparation (prepared vs spontaneous casters)
- Class features and bonus feats
- Starting equipment packages per class
- Starting gold per class

---

## Core Systems

### Kin-Sense
The signature mechanic of Oreka. All Kin share an elemental sixth sense that detects nearby presences.

- **9 resonance categories**: harmonic, wild_static, warm_static, breach_static, null, void, echo, none, raw_static
- **60 ft base range**, modified by room effects
- **Room modifiers**: Dead zones (Silence Breach), flickering zones (Dark Dawn), amplified zones (Windstones)
- Races determine resonance type; Farborn are invisible, Domnathar register as void

### Elemental Attunement
Every race carries elemental resonance affecting magic and combat.

- **Matching element spell**: +1 caster level (fire caster + fireball = stronger)
- **Opposing element**: -1 caster level (fire caster + ice storm = weaker)
- **Room resonance stacking**: +1 to +2 additional in matching elemental zones
- **Innate resistance**: All characters resist their element's energy type (fire affinity = fire resist 2)

### Combat
Full D&D 3.5 combat system:
- Auto-attack with configurable behavior
- Attack rolls, AC, damage, critical hits
- Combat maneuvers: disarm, trip, bull rush, grapple, overrun, sunder, feint
- Full attack actions with iterative attacks
- Power Attack, Combat Expertise toggles
- Sneak Attack for Rogues
- 37 conditions with mechanical effects: prone, stunned, blinded, poisoned, etc.
- Elemental weapon damage (flaming, frost, shock)
- Spawn/respawn system with timers (5 min regular, 15 min boss)
- **Combat AI**: Mobs flee at low HP, select optimal targets, use combat maneuvers from feats, trigger special attacks

### AI Chat Game
Full AI conversation system with any eligible NPC. Players enter a narrative chat mode with structured JSON responses from the LLM.

- `chat <npc>` — Enter AI chat mode with an NPC. All input routed to AI conversation.
- `endchat` — End session gracefully with NPC farewell
- `enter world` — Materialize from chat into the live world (moves player to NPC's room)
- **Shadow Presence**: Chatting players appear as dreaming presences in the NPC's room, visible to other players on `look` and Kin-sense (echo resonance)
- **World bleed**: Speech, combat, and world events in the room inject into the AI conversation as `[~WORLD~]` messages
- **NPC personas**: `ai_persona` field on mobs with voice, motivation, secrets, knowledge domains, speech style, faction attitudes, lore tags
- **NPC memory**: NPCs remember past conversations with each player (stored in `data/npc_memories/`)
- **Lore integration**: `data/lore.json` with 17 canon entries injected into AI context based on NPC's lore tags
- **Game actions**: AI can trigger reputation changes, quest grants, item gives, and memory storage
- **Conversation summarization**: Long conversations auto-compress older exchanges to stay within context limits
- **Model tier selection**: Premium (faction leaders, lore keepers), standard (merchants, trainers), fast (guards, commoners)
- **Session logs**: Complete conversation history saved to `data/chat_sessions/`
- **GMCP**: `Chat.Started`, `Chat.WorldEvent`, `Chat.Ended`, `Chat.Materialized` packages for Veil Client integration
- **30-minute auto-despawn**: Idle chat sessions cleaned up automatically

### Religion & Deities (13)
4 Elemental Lords + 9 Ascended Gods with mechanical effects.

**Elemental Lords** (primordial, never player-controlled):
- Lord of Stone, Lady of Fire, Lady of the Sea, Youngest Brother (Wind)

**Ascended Gods** (were mortals, can be player-linked):
- Dagdan, Harreem, Kaile'a, Cinvarin, Semyon, Apela Kelsoe, Ludus Galerius, Gonmareck Ritler, The Hand Unanswered

**Prayer system**: Pray at shrines for deity-specific buffs (healing, stat bonuses, resistances). Your patron deity's shrine gives stronger effects.

**Player ascension path**: Admins can create new deities (`@deity create`) and link them to player accounts (`@deity link`). Player-gods get: `divine bless`, `divine smite`, `divine manifest`, `divine speak` (echoes through all shrines), `divine grant` (bestow titles).

**Wandering gods**: Invisible deity entities roam between their shrines. Your patron deity is visible to you. Others sensed via Wisdom checks. Elemental Lords felt as environmental surges.

### Factions & Reputation (10)

| Faction | Type | Description |
|---------|------|-------------|
| Circle of Deeproot | Joinable | Druid order monitoring elemental health |
| Golden Roses | Joinable | Law enforcement, Harreem cult monitors |
| Far Riders | Joinable | Mytrone/Pasua cavalry brotherhood |
| Sand Wardens | Joinable | Desert pilgrim/patrol order |
| Trade Houses | Joinable | Mercantile guilds of Twin Rivers |
| The Unstrung | Secret | 600-year-old criminal org, Deceiver's Feat |
| Silent Concord | Race-locked | Silentborn organization, 5 Choirs |
| Chainless Legion | Race-locked | Farborn veterans |
| Gatefall Remnant | Reputation only | Survivors at Tomb of Kings |
| Brotherhood of Steppe | Reputation only | Mytrone cultural alliance |

- Reputation tracks standing with all 10 factions (-500 hostile to +600 allied)
- Joinable factions have 5 ranks with auto-promotion
- NPC shop prices modified by faction standing
- Territory hostility detection

### Location Effects (83 active room effects)

| Effect Type | Count | Examples |
|-------------|-------|---------|
| Kin-sense modifier | 14 | Dead zones (Glass Wastes), flickering (Lament of Kings), amplified (Windstones) |
| Elemental resonance | 10 | Fire at Kharazhad forges, water at river shrines |
| Environmental hazard | 5 | Desert heat (DC 12), volcanic gas (DC 14), mountain cold |
| Rune-circle | 12 | Teleport, heal, amplify, ward, weather — study/activate/repair |
| Sanctuary | 14 | Deity-linked shrines with healing and rest bonuses |

### Special Materials (12)

Standard D&D: Adamantine, Darkwood, Mithral, Cold Iron, Alchemical Silver, Dragonhide

Oreka-specific:
| Material | Element | Source | Special |
|----------|---------|--------|---------|
| Embersteel | Fire | Kharazhad | +1d4 fire on crit, fire resist 5 |
| Wind-silk | Wind | Canopy cities | Quarter weight, +5 move, -15% spell failure |
| Riverstone | Water | Great River | +1 CL water/cold spells as focus |
| Moonwhisper Silver | Wind | Hasura smiths | Silver DR bypass, no damage penalty, +1d4 cold vs fey/undead |
| Volcanic Glass | Fire | Scorchspires | Expanded crit range, fragile |
| Giant-bone | Earth | Ruins | +1 CL earth/acid as focus, +1 bludgeon damage |

### Crafting (60 recipes)

7 craft skills: Weaponsmithing (8), Armorsmithing (6), Leatherworking (4), Alchemy (6), Weaving (3), Jewelrycrafting (3), Runic Crafting (2)

- DC checks with success, critical success, and critical failure mechanics
- Material requirements and gold costs per recipe
- Feat and caster level requirements for magical crafting
- Includes Oreka-specific recipes: Embersteel weapons, Wind-silk cloaks, Amber-sap Elixir, Riverstone Amulets, Volcanic Glass daggers, Rune-carved focuses

---

## Character Creation

1. **Name** (3-20 letters)
2. **Race** (15 playable, text or number selection)
3. **Class** (12 classes, text or number)
4. **Stats** (4d6 drop lowest x6, racial modifiers applied)
5. **Skills** (class vs cross-class split display, 1pt vs 2pt cost)
6. **Deity** (13 deities, `info <#>` for details)
7. **Alignment** (9 options)
8. **Domains** (Cleric only, filtered by deity)
9. **Spells** (casters only, level 1 selection)
10. **Feats** (categorized by type, filtered by class/stats, multi-pick for Fighters/Humans)
11. **Confirmation** (full character sheet preview with equipment and gold)

Starting equipment is D&D 3.5 standard per class (weapons, armor, pack, supplies). Starting gold varies by class (20-150 gp).

---

## Tutorial (Chapel Area)

New players spawn in the Chapel, a 25-room tutorial zone:

- **Central Altar** — Guide Priestess Elia teaches basics (look, score, inventory, wear all)
- **North Quadrant** — Priest of Stone teaches movement (n/s/e/w, exits)
- **East Quadrant** — Priestess of Fire + Training Dummy (CR 0) teaches combat
- **South Quadrant** — Priestess of Sea teaches Kin-sense readouts
- **West Quadrant** — Priest of Wind teaches skills and interaction (pray, search, study)
- **District Streets** — Lead out to Custos do Aeternos and the wider world

---

## Commands

### Movement
`north/n`, `south/s`, `east/e`, `west/w`, `up/u`, `down/d`, `exits`, `scan`, `recall`, `speedwalk`

### Combat
`kill`, `flee`, `fullattack/fa`, `powerattack`, `combatexpertise`, `disarm`, `trip`, `grapple`, `bullrush`, `sunder`, `feint`

### Character
`score`, `stats`, `skills`, `inventory/i`, `equipment/eq`, `wear/wear all`, `remove/remove all`, `rest`, `levelup`, `conditions`

### Magic
`cast`, `spells`, `spellbook`, `spellinfo`, `prepare/memorize`, `domains`, `components`

### Items & Economy
`get`, `drop`, `put/put all`, `look <item>`, `look <mob>`, `list`, `buy`, `sell`, `appraise`, `craft`, `recipes`

### Religion
`pray`, `worship`, `deities`, `divine` (bless/smite/manifest/speak/grant)

### Factions
`faction`, `faction info <name>`, `faction join <name>`, `faction leave`

### Rune-Circles
`study`, `activate`, `repair`

### Social
`say`, `tell`, `yell`, `ooc`, `emote`, `who`, `where`, socials (bow, wave, nod, shrug, etc.)

### Admin
`@botrun [max_rooms] [nofight]`, `@deity create/link/unlink/shrine/list`, `@mobadd`, `@mobedit`, `@itemadd`, `@itemedit`, `@dig`, `@desc`, `@exit`, `@flag`

---

## Prompt

The prompt shows real-time character state with color coding:

```
HP:45/50 AC:17 MV:88/100 Gold:150 TNL:450 SP:[L0:3/L1:2] [Blessed]  Central Altar
>
```

- **HP** — Green (75%+), Yellow (40-74%), Red (below 40%)
- **AC** — Cyan
- **MV** — White (movement/stamina points)
- **Gold** — Yellow
- **TNL** — Grey (XP to next level)
- **SP** — Purple (spell slots per level, casters only)
- **Conditions** — Red (active effects)
- **Room** — Grey (current location)

---

## Veil Client — Browser-Based Play

OrekaMUD3 ships with the **Veil Client** (`veil_client.html`), a built-in HTML/WebSocket MUD client:

- **No download required** — Play in any modern browser
- **WebSocket server** on port 8765 with bidirectional telnet proxy
- **ANSI color rendering** — Full color support
- **GMCP integration** — Real-time data pushed to client
- **Keep-alive** — 30-second ping/pong heartbeat
- Telnet and WebSocket players share the same world simultaneously

### GMCP Protocol

Full Generic MUD Communication Protocol for rich client integration:

| Package | Data |
|---------|------|
| `Char.Vitals` | HP, AC, movement, gold, TNL, level |
| `Char.Status` | Conditions, spell slots, class, race |
| `Char.Factions` | All faction reputation values |
| `Char.Deity` | Patron deity, shrine status, active buffs |
| `Char.KinSense` | Elemental detections with range and room modifiers |
| `Char.Quest` | Active quests with state, completed quest list |
| `Room.Info` | Vnum, name, description, region, exits, effects, terrain |
| `Room.Mobs` | Living mobs with health state indicators |
| `Chat.Started` | NPC name/vnum, room, scenario (on chat session start) |
| `Chat.WorldEvent` | Injected world event text during chat |
| `Chat.Ended` | Session ID, reason (on chat session end) |
| `Chat.Materialized` | Room vnum/name (on shadow materialization) |

Works with MudLet, TinTin++, Veil Client, and any GMCP-compatible client.

---

## World Map Viewer

Interactive HTML/Canvas map at `http://localhost:8080/oreka_world_map.html`

- All 1,624 rooms visualized with region clustering
- Terrain topology layer (mountains, forests, rivers, desert, seas)
- Region labels with color coding
- Click rooms for details, exits, flags
- Pan/zoom navigation
- Toggle terrain on/off
- Search by room name or vnum
- Filter by region

---

## AI Bot Explorer

Built-in autonomous bot for testing and world verification.

```
@botrun              — Full exploration with combat
@botrun nofight      — Exploration only
@botrun 500          — Explore first 500 rooms
@botrun 100 nofight  — Explore 100 rooms, no fighting
```

Reports: room coverage, combat results by CR, deaths, dead ends, errors, region breakdown.

---

## Technical Architecture

### Server
- **Language**: Python 3.13+
- **Networking**: telnetlib3 (async telnet) + websockets (async WebSocket)
- **Ports**: 4000 (telnet, configurable) + 8765 (WebSocket/Veil Client)
- **Protocols**: Telnet + WebSocket + GMCP (Generic MUD Communication Protocol)
- **Codebase**: 33,000+ lines across 37 source modules + main.py

### Data Storage
- **Rooms**: JSON area files in `data/areas/` (13 files, 1,624 rooms)
- **Mobs**: `data/mobs.json` (373 entries) + `data/mobs_bestiary.json` (238 templates)
- **Players**: Individual JSON files in `data/players/`
- **Factions**: `data/guilds.json`
- **Deities**: `data/deities.json`
- **Materials**: `data/special_materials.json`
- **Recipes**: `data/recipes.json`
- **Achievements**: `data/achievements.json`
- **Events**: `data/events/player_events.jsonl` (JSONL event log)
- **Lore**: `data/lore.json` (17 canon entries for AI context)
- **Chat Sessions**: `data/chat_sessions/` (conversation logs)
- **NPC Memories**: `data/npc_memories/{npc_vnum}/` (per-player memory files)

### Source Modules
| File | Purpose |
|------|---------|
| `main.py` | Server, login, character creation, game loop, tick functions |
| `src/commands.py` | 321 player/admin/builder commands (13,128 lines) |
| `src/character.py` | Character class, stats, equipment, persistence |
| `src/combat.py` | D&D 3.5 combat engine |
| `src/spells.py` | 82 spells with elemental integration |
| `src/feats.py` | 88 feats with prerequisites |
| `src/items.py` | Item system with 12 special materials |
| `src/mob.py` | Mob/NPC class |
| `src/ai.py` | Three-tier NPC dialogue + Combat AI + AI Chat (JSON structured, lore, model tiers) |
| `src/chat_session.py` | AI chat session lifecycle, NPC memory, session logging |
| `src/room.py` | Room class with effects |
| `src/world.py` | World loader |
| `src/races.py` | 20 race definitions |
| `src/classes.py` | 12 class definitions |
| `src/kin_sense.py` | Kin-sense detection system |
| `src/factions.py` | Faction/reputation manager |
| `src/religion.py` | Deity/prayer system |
| `src/location_effects.py` | Room effects (hazards, rune-circles, etc.) |
| `src/wandering_gods.py` | Invisible deity entities |
| `src/spawning.py` | Mob spawn/respawn manager |
| `src/crafting.py` | Crafting system (60 recipes, 7 disciplines) |
| `src/quests.py` | Quest system (10 objective types) |
| `src/conditions.py` | 37 status conditions |
| `src/gmcp.py` | GMCP protocol (telnet + WebSocket, 12 data packages) |
| `src/websocket_server.py` | WebSocket server for Veil Client (port 8765) |
| `src/ai_player.py` | AI bot explorer |
| `src/party.py` | Party/group system |
| `src/schedules.py` | NPC behavior schedules |
| `src/chat.py` | Communication/broadcast |

### Tick Functions
| Tick | Interval | Purpose |
|------|----------|---------|
| `spawn_respawn_tick` | 30s | Respawn dead mobs |
| `location_effects_tick` | 60s | Process environmental hazards |
| `wandering_gods_tick` | 60s | Move deities between shrines |
| `hunger_thirst_tick` | 60s | Survival mechanics (if enabled) |
| `schedule_tick` | 30s | NPC behavior schedules |
| `ambient_echo_tick` | varies | Atmospheric room messages |
| `log_players` | periodic | Player activity logging |

---

## Lore Sources

| Document | Location |
|----------|----------|
| Complete World Lore | `World Regions history/World_of_Oreka_Complete_Lore.md` |
| Twin Rivers Guide | `World Regions history/Old Documents/TwinRivers_Regional_Guide_v3.docx` |
| Gatefall Reach Guide | `World Regions history/New Documents/GatefallReach_Regional_Guide_v3.txt` |
| Player/DM Audit | `World Regions history/New Documents/Regional_Guides_Player_DM_Audit_v1 (1).md` |
| Monster Entries | `World Regions history/New Documents/Oreka_Batch*.md` (19 batches) |
| Race Compendium | `World Regions history/Old Documents/Races_Compendium.txt` |
| World Map | `World Regions history/New Documents/Oreka_FullRegion_UniformDimensions.png` |

---

## License

D&D 3.5 mechanics under the Open Game License (OGL). Oreka world lore, setting, and original content are proprietary.
