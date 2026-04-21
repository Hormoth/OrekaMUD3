# OrekaMUD3

> *A D&D 3.5 OGL multi-user dungeon set in the world of Oreka.*

OrekaMUD3 is the world engine behind **OrekaWorld** — a persistent text RPG with
1,624 hand-built rooms, a full D&D 3.5 OGL rules implementation, an integrated
AI conversation layer, and first-class support for a purpose-built browser
client (**Veil**, in a separate repo).

**Live server:** `telnet 47.188.185.168 4000`
**Browser play:** play.orekaworld.com (Phase 1 gateway)

---

## What lives in this workspace

This directory is the OrekaMUD3 **workspace**, not just the engine source. It
contains the game server, a companion storytelling tool, HTML artifacts used by
the browser client, design assets, and planning docs.

```
OrekaMUD3/
├── oreka_mud/                # ★ The MUD server itself (Python, 33k+ LOC)
│   ├── main.py               # Async telnet + WebSocket loop, login, char creation
│   ├── src/                  # 40+ modules: combat, spells, kin-sense, AI, GMCP, …
│   ├── data/                 # Area files, mobs, items, lore, deities, factions
│   ├── tests/                # 300 automated tests
│   ├── veil_client.html      # Built-in browser client (WebSocket, ANSI, GMCP)
│   ├── World Regions history/ # Lore source documents (world bible, monster entries)
│   └── README.md             # Engine-specific README (start here for code details)
│
├── oreka-scribe/             # Collaborative storytelling + quest-authoring tool
│   ├── SKILL.md              # Scribe agent instructions (/log, /riff, /quest modes)
│   ├── canon/                # Canon Bible snapshots + canon-index.md
│   ├── characters/           # NPC voice notes, persona sheets
│   ├── quests/               # Authored quest files
│   ├── sessions/             # Campaign session logs
│   └── threads/              # Ongoing story threads
│
├── data/                     # Persistent state (npc_memories/ etc.)
│
├── oreka_veil_portal.html    # Landing/portal page for OrekaWorld
├── oreka_character_sheet.html # Standalone character sheet viewer
├── oreka_world_map.html      # Interactive 1,624-room map (Canvas, pan/zoom)
├── oreka_world_map_data.js   # Map data payload
├── oreka_npc_chat.html       # Standalone AI NPC chat UI
├── oreka_design_system.css   # Shared visual language (colors, typography, tokens)
│
├── AI.md                     # AI layer design notes
├── BUILDOUT.md               # Top-level buildout spec
├── BUILDOUT_ARC_MODULE.md    # Arc module spec (admin tooling)
├── BUILDOUT_VEIL.md          # Veil integration spec
├── CLAUDE_DESKTOP_CONTEXT.md # Context for Claude Desktop sessions
├── DEVELOPMENT_STATUS.md     # Rolling status log
├── PROJECT_ANALYSIS.md       # Architecture/analysis write-up
├── PROJECT_PLAN.md           # Roadmap narrative
├── Road_map.json             # Machine-readable roadmap (systems + status)
├── SALES.md                  # Kickstarter / product positioning
│
└── *.log                     # Running-service logs (gateway, MUD, veil_client, cloudflared)
```

See **[oreka_mud/README.md](oreka_mud/README.md)** for the full engine
breakdown — regions, races, classes, combat, crafting, GMCP, commands.

---

## The world — at a glance

- **1,624 rooms** across 13 area files, 100% connectivity verified
- **7 regions**: Twin Rivers, Kinsweave, Tidebloom Reach, Infinite Desert,
  Eternal Steppe, Gatefall Reach, Deepwater Marches
- **20 races** (15 playable Kin + 5 NPC races), each with elemental resonance
- **12 classes**, full D&D 3.5 OGL (BAB, saves, spell slots, class features)
- **88 feats**, **82 spells**, **60 crafting recipes**, **37 conditions**
- **13 deities** — 4 Elemental Lords + 9 Ascended Gods, with prayer/shrine effects
- **10 factions** with reputation (-500 hostile to +600 allied)
- **373 mobs** + 238 bestiary templates, **300 automated tests**

The signature mechanic is **Kin-Sense** — a 60-ft elemental sixth sense with 9
resonance categories (harmonic, wild_static, breach_static, null, void, echo,
raw_static, warm_static, none). Room modifiers amplify, dampen, or invert
readings.

---

## Quick start — run the server

```bash
cd oreka_mud
pip install -r requirements.txt        # telnetlib3, websockets, …
python main.py
```

The server binds two ports:

| Port | Protocol | Purpose |
|------|----------|---------|
| 4000 | Telnet | Classic MUD clients (MudLet, TinTin++, raw telnet) |
| 8765 | WebSocket | Built-in browser client (`veil_client.html`) and Veil Client |

Connect any GMCP-aware client to port 4000 to receive the 12 GMCP packages —
`Char.Vitals`, `Char.Status`, `Char.Factions`, `Char.Deity`, `Char.KinSense`,
`Char.Quest`, `Room.Info`, `Room.Mobs`, and `Chat.Started / WorldEvent / Ended /
Materialized`.

---

## The AI chat layer

Any eligible NPC with an `ai_persona` field can be entered with `chat <npc>`:

- Structured JSON responses from an LLM (tier selected by NPC importance)
- Per-player **NPC memory** persisted in `oreka_mud/data/npc_memories/`
- **World bleed** — speech, combat, and events in the NPC's room inject into
  the conversation as `[~WORLD~]` messages
- **Shadow Presence** — chatting players appear as dreaming presences
  (echo resonance) to others via Kin-sense and `look`
- **Materialization** — `enter world` teleports the player to the NPC's room
- **Lore integration** — `data/lore.json` entries injected based on NPC tags
- 30-minute idle auto-despawn; session logs saved to `data/chat_sessions/`

See `oreka_mud/src/ai.py`, `src/chat_session.py`, and `src/npc_chat_server.py`.

---

## Oreka Scribe — the storytelling companion

`oreka-scribe/` is a **collaborative authoring tool** (used as a Claude skill).
It runs in two modes:

- **`/log`** — campaign log mode. The author narrates real session events;
  the Scribe listens, asks clarifying questions, and updates session files,
  character notes, and story threads without proposing what happens next.
- **`/riff`** — co-writer mode. Back-and-forth improvisation, with the Scribe
  voicing named NPCs and offering branching options tagged by arc type.

Outputs land in `oreka-scribe/sessions/`, `characters/`, `threads/`, and
eventually become MUD-ready quest files in `quests/`. See
[oreka-scribe/SKILL.md](oreka-scribe/SKILL.md) for the full agent spec.

---

## Related repos

| Repo | Role |
|------|------|
| **OrekaMUD3** (this repo) | The world engine, lore, AI layer, scribe |
| **[VeilClient](../VeilClient)** | The web + desktop client (play.orekaworld.com) |

Veil is the browser/desktop client shipping the gateway, panel system, GMCP
handler, subscription tiers, and Phase 3 AI features. OrekaMUD3 is the game
server Veil connects to.

---

## Running services (Dell R730)

| Service | Port | Notes |
|---------|------|-------|
| OrekaMUD (telnet) | 4000 | Public, `47.188.185.168` |
| OrekaMUD (WebSocket / GMCP) | 8765 | Browser client transport |
| HTTP static | 8080 | Hosts world map + portal HTML |

Logs for running services (`mud_server.log`, `gateway.log`, `veil_client.log`,
`http_server.log`, `cloudflared_oreka.log`) are written at the workspace root.

---

## Documentation index

| Document | Purpose |
|----------|---------|
| [oreka_mud/README.md](oreka_mud/README.md) | Engine reference (races/classes/combat/commands) |
| [oreka-scribe/SKILL.md](oreka-scribe/SKILL.md) | Scribe agent modes + story grammar |
| [BUILDOUT.md](BUILDOUT.md) | Workspace-wide buildout plan |
| [BUILDOUT_ARC_MODULE.md](BUILDOUT_ARC_MODULE.md) | Admin "Arc" module spec |
| [BUILDOUT_VEIL.md](BUILDOUT_VEIL.md) | Veil integration contract |
| [AI.md](AI.md) | AI layer architecture notes |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | Roadmap narrative |
| [Road_map.json](Road_map.json) | Machine-readable roadmap |
| [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) | Rolling status log |
| [SALES.md](SALES.md) | Kickstarter / product positioning |

---

## License

- **D&D 3.5 mechanics** — Open Game License v1.0a (OGL). See OGL attribution in
  the engine repo.
- **Oreka world content** — lore, setting, character/place names, deities,
  factions, original monsters, and in-game text are proprietary.
- **Code** — see the root `LICENSE` if present; otherwise treat as proprietary
  during the pre-Kickstarter phase.
