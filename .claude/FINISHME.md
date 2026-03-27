# OrekaMUD

> *A D&D 3.5 OGL multi-user dungeon set in the world of Oreka.*

**Live server:** `telnet 47.188.185.168 4000`  
**Veil Client:** `play.orekamud.com` (see `../veil/README.md`)  
**Engine:** Python 3.13, async telnet, port 4000

---

## What This Repository Is

OrekaMUD is the game server. It is complete and running. The Veil Client connects to it. This README documents what exists, what needs to be added to support Veil, and exactly where in the codebase every addition goes.

**Do not rebuild anything already listed under "What Exists."**

---

## Quick Start

```bash
cd oreka_mud
python main.py
```

Connect via telnet:
```bash
telnet localhost 4000
telnet 47.188.185.168 4000
```

Connect via Veil Client (once built):
```
https://play.orekamud.com
```

---

## What Exists — Do Not Rebuild

Everything in this section is complete and tested. The Veil Client uses it as-is.

### World

| Asset | Count | Status |
|---|---|---|
| Rooms | 1,615 | Complete — 100% connectivity verified by AI bot |
| Area files | 12 | Complete |
| Regions | 7 | Complete |
| Wilderness corridors | 6 | Complete |

### Creatures

| Asset | Count | Status |
|---|---|---|
| Mobs total | 366 | Complete |
| Hostile mobs | 276 | Complete |
| Friendly NPCs | 85 | Complete |
| Tutorial mobs | 5 | Complete |
| Bestiary templates | 238 | Complete |

### Character Systems

| System | File | Status |
|---|---|---|
| 15 playable races | `src/races.py` | Complete |
| 12 classes with full 3.5 progression | `src/classes.py` | Complete |
| 88 feats with prerequisites | `src/feats.py` | Complete |
| Full D&D 3.5 combat engine | `src/combat.py` | Complete |
| Spell system with elemental integration | `src/spells.py` | Complete |
| Kin-sense detection (9 categories) | `src/kin_sense.py` | Complete |
| Faction and reputation system (10 factions) | `src/factions.py` | Complete |
| Deity and prayer system (13 deities) | `src/religion.py` | Complete |
| Special materials (12 types) | `src/items.py` | Complete |
| Crafting system (32 recipes, 7 skills) | `src/crafting.py` | Complete |
| Quest system | `src/quests.py` | Complete |
| Status conditions | `src/conditions.py` | Complete |
| Party system | `src/party.py` | Complete |
| Location effects (83 active) | `src/location_effects.py` | Complete |
| Wandering gods | `src/wandering_gods.py` | Complete |
| Mob schedules | `src/schedules.py` | Complete |
| Spawning and respawn | `src/spawning.py` | Complete |
| NPC Dialogue system | `src/chat.py` | Complete |

### Player Commands (~200 total)

All commands exist. See the full command list at the bottom of this file.

### Admin Commands

| Command | Purpose |
|---|---|
| `@botrun [max] [nofight]` | AI bot explorer for world verification |
| `@deity create/link/unlink/shrine/list` | Deity management |
| `@mobadd / @mobedit` | Mob management |
| `@itemadd / @itemedit` | Item management |
| `@dig / @desc / @exit / @flag` | Room management |

### Infrastructure

| Component | Detail |
|---|---|
| Networking | `telnetlib3` async telnet |
| Storage | JSON files per player in `data/players/` |
| Area data | JSON files in `data/areas/` (12 files) |
| World map | Interactive HTML at port 8080 |
| Tick system | 7 background tick functions |
| Log system | Player activity logging |

---

## What Needs to Be Added — Veil Support

Everything in this section is new work. Nothing here exists yet. Each item shows the file it goes into and exactly what it needs to do.

---

### ADDITION 1 — GMCP Output
**Priority: CRITICAL — blocks all Phase 2 Veil panels**

**New file:** `src/gmcp.py`

GMCP (Generic Mud Communication Protocol) sends structured JSON data alongside the text stream. The Veil Client's visual panels — character sheet, Kin-sense visualizer, deity panel, faction bars — are all driven by GMCP. Without it, those panels cannot function.

**What to build:**

GMCP telnet option negotiation:
```python
# On client connect, advertise GMCP support
GMCP_IAC = bytes([255])   # IAC
GMCP_WILL = bytes([251])  # WILL
GMCP_OPT = bytes([201])   # GMCP option code
# Send: IAC WILL GMCP
```

Seven data packages to emit:

**`Char.Vitals`** — emit after every game tick and after every combat round:
```json
{
  "hp": 45, "hp_max": 50,
  "ac": 17,
  "mv": 88, "mv_max": 100,
  "gold": 150,
  "tnl": 450
}
```

**`Char.Status`** — emit when conditions or spell slots change:
```json
{
  "conditions": ["Blessed", "Hasted"],
  "spells": {"0": [3, 3], "1": [2, 2], "2": [1, 1]},
  "level": 8,
  "class": "Cleric",
  "race": "Visetri Dwarf"
}
```

**`Char.Factions`** — emit when any faction rep changes:
```json
{
  "Circle of Deeproot": 240,
  "Golden Roses": -50,
  "Far Riders": 120,
  "Sand Wardens": 0,
  "Trade Houses": 80,
  "The Unstrung": -200,
  "Silent Concord": 0,
  "Chainless Legion": 0,
  "Gatefall Remnant": 60,
  "Brotherhood of Steppe": 30
}
```

**`Char.Deity`** — emit on shrine enter/exit and buff change:
```json
{
  "patron": "Harreem",
  "at_shrine": true,
  "shrine_name": "Shrine of Harreem",
  "active_buffs": ["Harreem's Clarity"],
  "patron_region": true
}
```

**`Room.Info`** — emit on every room change:
```json
{
  "vnum": 1001,
  "name": "Central Altar",
  "region": "twin_rivers",
  "exits": ["north", "south", "east", "west"],
  "effects": ["sanctuary"],
  "terrain": "indoor"
}
```

**`Char.KinSense`** — emit when Kin-sense detections change:
```json
{
  "detections": [
    {"name": "Torven", "resonance": "harmonic", "strength": "normal"},
    {"name": "Jessie", "resonance": "echo", "strength": "faint"},
    {"name": "Unknown", "resonance": "breach_static", "strength": "strong"}
  ],
  "room_modifier": "amplified",
  "range_ft": 90
}
```

**`Char.Quest`** — emit when quest state changes:
```json
{
  "active": [
    {"id": "river_trade", "name": "The River Road", "npc": "Merchant Galen"}
  ],
  "completed": ["chapel_tour"],
  "available": ["deeproot_patrol"]
}
```

**Where to call emit from (hooks into existing code):**

```python
# In src/character.py — after any stat change:
await gmcp.emit(player, "Char.Vitals", player.vitals_dict())

# In src/combat.py — end of each combat round:
await gmcp.emit(player, "Char.Vitals", player.vitals_dict())

# In src/conditions.py — after apply/remove condition:
await gmcp.emit(player, "Char.Status", player.status_dict())

# In src/factions.py — after rep change:
await gmcp.emit(player, "Char.Factions", player.faction_dict())

# In src/religion.py — after shrine enter/exit or buff change:
await gmcp.emit(player, "Char.Deity", player.deity_dict())

# In src/room.py — in move() after player changes rooms:
await gmcp.emit(player, "Room.Info", room.info_dict())

# In src/kin_sense.py — after detection scan:
await gmcp.emit(player, "Char.KinSense", kin_results)

# In src/quests.py — after quest state changes:
await gmcp.emit(player, "Char.Quest", player.quest_dict())
```

---

### ADDITION 2 — WebSocket Server
**Priority: CRITICAL — blocks all Veil access**

**New file:** `src/websocket_server.py`

The WebSocket server runs alongside the telnet server. Veil connects via WebSocket; legacy MUD clients connect via telnet. Both are served simultaneously from the same Python process.

```python
import asyncio
import websockets

async def ws_handler(websocket):
    """
    Accept a WebSocket connection from Veil.
    Spawn a telnet connection to the MUD on port 4000.
    Proxy bytes bidirectionally.
    """
    reader, writer = await asyncio.open_connection('127.0.0.1', 4000)

    async def client_to_mud():
        async for message in websocket:
            writer.write(message.encode() + b'\r\n')
            await writer.drain()

    async def mud_to_client():
        while True:
            data = await reader.read(4096)
            if not data:
                break
            await websocket.send(data.decode('utf-8', errors='replace'))

    await asyncio.gather(client_to_mud(), mud_to_client())

async def start_ws_server():
    async with websockets.serve(ws_handler, '0.0.0.0', 8765):
        await asyncio.Future()  # run forever
```

**Hook into `main.py`:**
```python
# In main.py — start alongside telnet server:
await asyncio.gather(
    start_telnet_server(),
    start_ws_server(),        # ADD THIS
    start_world_map_server(),
    run_ticks(),
)
```

**Configuration:**
```
WS_PORT=8765  # add to config
```

---

### ADDITION 3 — Shadow Presence System
**Priority: HIGH — required for Veil Phase 3 AI chat**

**New file:** `src/shadow_presence.py`

When a player starts an AI NPC chat session in Veil, they appear as a dreaming presence inside the live MUD world. Real players can see them. What real players say enters the AI conversation. When ready, the chat player can materialize fully into the MUD.

**Full implementation:**

```python
import asyncio
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ShadowPresence:
    player_id: str
    player_name: str
    npc_id: int
    npc_name: str
    room_id: int
    conversation_history: list = field(default_factory=list)
    visible: bool = True
    materialized: bool = False

    def room_description(self) -> str:
        return (
            f"{self.player_name} stands nearby, lost in "
            f"quiet conversation with {self.npc_name}. "
            f"Their eyes are distant, as if looking at something "
            f"only they can see."
        )

    def kin_sense_entry(self) -> dict:
        """
        Shadow presences register on Kin-sense as Echo resonance.
        Faint strength — clearly different from a real player.
        """
        return {
            "name": self.player_name,
            "resonance": "echo",
            "strength": "faint",
            "description": "a presence that feels both near and far"
        }

    def inject_player_speech(self, speaker: str, text: str):
        """A MUD player speaks in the room — inject into AI context."""
        self.conversation_history.append({
            "role": "system",
            "content": (
                f"[WORLD EVENT] {speaker} says nearby: \"{text}\". "
                f"You and {self.npc_name} can hear this."
            )
        })

    def inject_combat(self, description: str):
        """Combat starts nearby — inject into AI context."""
        self.conversation_history.append({
            "role": "system",
            "content": (
                f"[WORLD EVENT] Nearby: {description}. "
                f"The sound of battle fills the air around you."
            )
        })

    def inject_room_event(self, event_text: str):
        """Generic world event — inject into AI context."""
        self.conversation_history.append({
            "role": "system",
            "content": f"[WORLD EVENT] {event_text}"
        })


class ShadowPresenceManager:
    """Global manager. One instance, lives in main.py."""

    def __init__(self):
        self.shadows: dict[str, ShadowPresence] = {}

    def create(self, player_id, player_name,
               npc_id, npc_name, room_id) -> ShadowPresence:
        shadow = ShadowPresence(
            player_id=player_id,
            player_name=player_name,
            npc_id=npc_id,
            npc_name=npc_name,
            room_id=room_id
        )
        self.shadows[player_id] = shadow
        asyncio.create_task(self._broadcast_arrival(shadow))
        return shadow

    async def _broadcast_arrival(self, shadow: ShadowPresence):
        from src.world import get_room
        room = get_room(shadow.room_id)
        msg = (
            f"\n{shadow.player_name} appears, stepping into the "
            f"space with a distant look in their eyes. They seem "
            f"to be conversing with {shadow.npc_name}.\n"
        )
        for player in room.players:
            await player.send(msg)

    def get_by_room(self, room_id: int) -> list[ShadowPresence]:
        return [s for s in self.shadows.values()
                if s.room_id == room_id]

    def broadcast_speech(self, room_id: int,
                         speaker: str, text: str):
        """Called by say command hook."""
        for shadow in self.get_by_room(room_id):
            shadow.inject_player_speech(speaker, text)

    def broadcast_combat(self, room_id: int, description: str):
        """Called by combat engine hook."""
        for shadow in self.get_by_room(room_id):
            shadow.inject_combat(description)

    def materialize(self, player_id: str) -> Optional[ShadowPresence]:
        """
        Player clicks Enter World in Veil.
        Returns shadow so login system can spawn them correctly.
        """
        shadow = self.shadows.get(player_id)
        if shadow:
            shadow.materialized = True
            asyncio.create_task(
                self._broadcast_materialization(shadow)
            )
        return shadow

    async def _broadcast_materialization(self, shadow: ShadowPresence):
        from src.world import get_room
        room = get_room(shadow.room_id)
        for player in room.players:
            await player.send(
                f"\n{shadow.player_name}'s eyes focus. "
                f"They are fully present.\n"
            )

    def remove(self, player_id: str):
        shadow = self.shadows.pop(player_id, None)
        if shadow:
            asyncio.create_task(self._broadcast_departure(shadow))

    async def _broadcast_departure(self, shadow: ShadowPresence):
        from src.world import get_room
        room = get_room(shadow.room_id)
        for player in room.players:
            await player.send(
                f"\n{shadow.player_name} fades from view.\n"
            )


# Global instance — import this everywhere that needs it
shadow_manager = ShadowPresenceManager()
```

---

### ADDITION 4 — Hooks Into Existing Commands
**Priority: HIGH — required for shadow presence to work**

These are small edits to existing files. Nothing is rewritten — lines are added.

**`src/commands.py` — hook the `say` command:**
```python
# Find the existing cmd_say function and add after the existing broadcast:
async def cmd_say(player, args):
    text = " ".join(args)
    room = get_room(player.room_id)

    # Existing: broadcast to MUD players
    for p in room.players:
        if p != player:
            await p.send(f"{player.name} says: \"{text}\"\n")
    await player.send(f"You say: \"{text}\"\n")

    # ADD: inject into any shadow presences in this room
    from src.shadow_presence import shadow_manager
    shadow_manager.broadcast_speech(room.vnum, player.name, text)
```

**`src/room.py` — hook the `look` command to show shadow presences:**
```python
# Find the function that builds the occupants list for look output
# Add shadow presences alongside regular players:

def get_occupants_string(room) -> str:
    from src.shadow_presence import shadow_manager
    lines = []

    # Existing: real players
    for player in room.players:
        lines.append(f"{player.name} is here.")

    # ADD: shadow presences
    for shadow in shadow_manager.get_by_room(room.vnum):
        lines.append(shadow.room_description())

    return "\n".join(lines)
```

**`src/kin_sense.py` — hook Kin-sense to include shadow presences:**
```python
# Find the function that builds Kin-sense detections
# Add after the existing detection loop:

def get_detections(room, viewer) -> list:
    from src.shadow_presence import shadow_manager
    detections = []

    # Existing: real players and mobs
    for player in room.players:
        if player != viewer:
            detections.append({
                "name": player.name,
                "resonance": player.resonance_type,
                "strength": "normal"
            })

    # ADD: shadow presences as echo resonance
    for shadow in shadow_manager.get_by_room(room.vnum):
        detections.append(shadow.kin_sense_entry())

    return detections
```

**`src/combat.py` — hook combat to notify shadow presences:**
```python
# Find the function that announces combat start to the room
# Add after the existing room broadcast:

async def broadcast_combat_start(room, attacker, target):
    # Existing: send to all players in room
    msg = f"{attacker.name} attacks {target.name}!"
    for player in room.players:
        await player.send(msg)

    # ADD: inject into shadow presences
    from src.shadow_presence import shadow_manager
    shadow_manager.broadcast_combat(
        room.vnum,
        f"{attacker.name} attacks {target.name}"
    )
```

---

### ADDITION 5 — Materialization Handler
**Priority: HIGH — required for shadow presence to work**

**In `main.py` or `src/character.py` — handle players entering from Veil chat:**

```python
async def handle_veil_materialize(player_id: str, websocket):
    """
    Called when a Veil chat player clicks 'Enter World'.
    Spawns them at the correct room with conversation context intact.
    """
    from src.shadow_presence import shadow_manager

    shadow = shadow_manager.materialize(player_id)
    if not shadow:
        await websocket.send("ERROR: No active shadow presence found.")
        return

    # Load or create the player character
    player = await load_or_create_player(player_id)

    # Spawn at the room where the shadow was
    player.room_id = shadow.room_id

    # Attach conversation context to player session
    # (the Veil gateway handles passing this to the AI layer)
    player.session_data["materialized_from"] = {
        "npc_id": shadow.npc_id,
        "npc_name": shadow.npc_name,
        "conversation_history": shadow.conversation_history
    }

    # Remove shadow — player is now fully present
    shadow_manager.remove(player_id)

    # Normal login flow from here
    await player_login(player, websocket)
```

---

### ADDITION 6 — MCP Server Integration
**Priority: MEDIUM — required for AI DM agent and AI NPC system**

**New file:** `src/mcp_bridge.py`

The MCP server (in the Veil repo at `veil/mcp/server.py`) needs to read live game state from OrekaMUD. Rather than the MCP server importing OrekaMUD modules directly, the MUD exposes a lightweight internal API that the MCP server calls.

```python
# src/mcp_bridge.py
# Internal REST API for MCP server to query game state
# Runs on port 8001 — not publicly exposed, local network only

from fastapi import FastAPI
from src.world import get_room as world_get_room
from src.character import load_player
from src.mob import get_npc
from src.factions import get_standings
from src.shadow_presence import shadow_manager

app = FastAPI()

@app.get("/room/{room_id}")
async def get_room(room_id: int):
    room = world_get_room(room_id)
    shadows = shadow_manager.get_by_room(room_id)
    return {
        "vnum": room.vnum,
        "name": room.name,
        "description": room.description,
        "region": room.region,
        "exits": list(room.exits.keys()),
        "players": [p.name for p in room.players],
        "npcs": [n.name for n in room.npcs],
        "effects": [e.name for e in room.effects],
        "shadows": [s.player_name for s in shadows]
    }

@app.get("/player/{player_name}")
async def get_player(player_name: str):
    player = load_player(player_name)
    return player.to_dict()

@app.get("/npc/{npc_id}")
async def get_npc_data(npc_id: int):
    npc = get_npc(npc_id)
    return npc.to_dict()

@app.get("/world/state")
async def get_world_state():
    from src.world import WORLD
    return {
        "player_count": len(WORLD.online_players),
        "regions": WORLD.region_summaries(),
    }

@app.post("/player/{player_name}/message")
async def send_message(player_name: str, body: dict):
    from src.world import get_online_player
    player = get_online_player(player_name)
    if player:
        await player.send(body["message"] + "\n")
        return {"status": "delivered"}
    return {"status": "player_offline"}

@app.post("/world/event")
async def trigger_event(body: dict):
    from src.events import broadcast_event
    await broadcast_event(
        scope=body["scope"],
        target=body["target"],
        message=body["description"]
    )
    return {"status": "triggered"}

@app.post("/player/{player_name}/reputation")
async def modify_rep(player_name: str, body: dict):
    player = load_player(player_name)
    player.factions[body["faction"]] += body["amount"]
    player.save()
    return {"status": "updated",
            "new_value": player.factions[body["faction"]]}
```

**Start alongside the MUD:**
```python
# In main.py:
import uvicorn
from src.mcp_bridge import app as mcp_bridge_app

async def start_mcp_bridge():
    config = uvicorn.Config(
        mcp_bridge_app,
        host="127.0.0.1",  # local only
        port=8001,
        log_level="warning"
    )
    server = uvicorn.Server(config)
    await server.serve()

# Add to asyncio.gather in main():
await asyncio.gather(
    start_telnet_server(),
    start_ws_server(),
    start_mcp_bridge(),     # ADD THIS
    start_world_map_server(),
    run_ticks(),
)
```

---

### ADDITION 7 — Player Events Log
**Priority: MEDIUM — required for DM Agent to watch the world**

**New file:** `src/event_log.py`

The DM Agent reads a rolling log of significant player events to decide when to trigger world events, faction responses, and story beats.

```python
import asyncio
import json
from datetime import datetime
from pathlib import Path

EVENT_LOG_FILE = Path("data/events/player_events.jsonl")
EVENT_LOG_FILE.parent.mkdir(exist_ok=True)

async def log_event(player_name: str, event_type: str,
                    event_data: dict, room_id: int = None,
                    region: str = None):
    """
    Log a significant player action.
    Called from the relevant system after the action happens.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "player": player_name,
        "type": event_type,
        "data": event_data,
        "room_id": room_id,
        "region": region
    }
    with open(EVENT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**Hook into existing systems:**

```python
# After player levels up in src/character.py:
await log_event(player.name, "level_up",
    {"new_level": player.level, "class": player.char_class},
    room_id=player.room_id, region=player.region)

# After mob death in src/combat.py:
await log_event(player.name, "mob_kill",
    {"mob": mob.name, "cr": mob.cr},
    room_id=player.room_id, region=player.region)

# After faction rep threshold crossed in src/factions.py:
await log_event(player.name, "faction_threshold",
    {"faction": faction, "standing": new_standing,
     "old": old_value, "new": new_value})

# After quest complete in src/quests.py:
await log_event(player.name, "quest_complete",
    {"quest": quest_id, "quest_name": quest_name},
    room_id=player.room_id, region=player.region)

# After player ascends as deity in src/religion.py:
await log_event(player.name, "deity_ascension",
    {"deity_name": deity_name},
    region=player.region)
```

---

### ADDITION 8 — `to_dict()` Methods
**Priority: MEDIUM — required for MCP bridge and GMCP output**

Several existing classes need serialization methods. Add these to the existing class definitions:

**`src/character.py` — Player class:**
```python
def vitals_dict(self) -> dict:
    return {
        "hp": self.hp, "hp_max": self.max_hp,
        "ac": self.ac,
        "mv": self.mv, "mv_max": self.max_mv,
        "gold": self.gold, "tnl": self.tnl
    }

def status_dict(self) -> dict:
    return {
        "conditions": [c.name for c in self.conditions],
        "spells": self.spell_slots,
        "level": self.level,
        "class": self.char_class,
        "race": self.race
    }

def faction_dict(self) -> dict:
    return dict(self.factions)

def deity_dict(self) -> dict:
    return {
        "patron": self.deity,
        "at_shrine": self.at_shrine,
        "shrine_name": getattr(self, 'current_shrine', None),
        "active_buffs": [b.name for b in self.deity_buffs],
        "patron_region": self.deity_in_region
    }

def quest_dict(self) -> dict:
    return {
        "active": [q.to_dict() for q in self.active_quests],
        "completed": list(self.completed_quests),
        "available": self.get_available_quests()
    }

def to_dict(self) -> dict:
    """Full character sheet for MCP API."""
    return {
        "name": self.name,
        "race": self.race,
        "class": self.char_class,
        "level": self.level,
        "alignment": self.alignment,
        "deity": self.deity,
        "vitals": self.vitals_dict(),
        "stats": {
            "str": self.strength, "dex": self.dexterity,
            "con": self.constitution, "int": self.intelligence,
            "wis": self.wisdom, "cha": self.charisma
        },
        "factions": self.faction_dict(),
        "quests": self.quest_dict(),
        "room_id": self.room_id,
        "region": self.region,
        "equipment": [e.name for e in self.equipped.values() if e],
        "conditions": [c.name for c in self.conditions]
    }
```

**`src/room.py` — Room class:**
```python
def info_dict(self) -> dict:
    return {
        "vnum": self.vnum,
        "name": self.name,
        "region": self.region,
        "exits": list(self.exits.keys()),
        "effects": [e.name for e in self.effects],
        "terrain": self.terrain_type
    }

def to_dict(self) -> dict:
    """Full room data for MCP API."""
    from src.shadow_presence import shadow_manager
    return {
        "vnum": self.vnum,
        "name": self.name,
        "description": self.description,
        "region": self.region,
        "exits": list(self.exits.keys()),
        "players": [p.name for p in self.players],
        "npcs": [n.name for n in self.npcs],
        "effects": [e.name for e in self.effects],
        "terrain": self.terrain_type,
        "shadows": [
            s.player_name
            for s in shadow_manager.get_by_room(self.vnum)
        ]
    }
```

**`src/mob.py` — Mob/NPC class:**
```python
def to_dict(self) -> dict:
    return {
        "id": self.vnum,
        "name": self.name,
        "race": self.race,
        "level": self.level,
        "faction": self.faction,
        "deity": getattr(self, 'deity', None),
        "room_id": self.room_id,
        "region": self.region,
        "alignment": self.alignment,
        "npc_type": self.npc_type,
        "friendly": self.friendly
    }
```

---

### ADDITION 9 — World Events System
**Priority: MEDIUM — required for DM Agent triggers**

**New file:** `src/events.py`

```python
import asyncio
from src.world import WORLD

async def broadcast_event(scope: str, target: str,
                          message: str,
                          mechanical_effects: dict = None):
    """
    Broadcast a world event to players.
    Called by DM Agent via MCP bridge.

    scope: "room" | "region" | "global"
    target: room vnum, region name, or "all"
    message: narrative text sent to players
    mechanical_effects: optional dict of game mechanics to apply
    """
    players_reached = []

    if scope == "room":
        room = WORLD.get_room(int(target))
        if room:
            for player in room.players:
                await player.send(f"\n{message}\n")
                players_reached.append(player.name)

    elif scope == "region":
        for player in WORLD.online_players.values():
            if player.region == target:
                await player.send(f"\n{message}\n")
                players_reached.append(player.name)

    elif scope == "global":
        for player in WORLD.online_players.values():
            await player.send(f"\n{message}\n")
            players_reached.append(player.name)

    # Apply mechanical effects if any
    if mechanical_effects:
        await apply_event_effects(
            mechanical_effects, scope, target
        )

    return players_reached

async def apply_event_effects(effects: dict,
                               scope: str, target: str):
    """Apply mechanical changes from a world event."""
    if "mob_surge" in effects:
        # Spawn additional mobs in target area
        pass
    if "weather" in effects:
        # Apply weather effects to region
        pass
    if "shrine_bonus" in effects:
        # Temporarily boost shrine effects
        pass
```

---

## Complete File List After All Additions

### Existing Files (do not modify unless noted)

```
main.py                      # ADD: ws_server, mcp_bridge to gather()
src/character.py             # ADD: to_dict(), vitals_dict(), etc.
src/commands.py              # ADD: shadow_manager hook in cmd_say()
src/combat.py                # ADD: gmcp emit, shadow broadcast, event log
src/spells.py
src/feats.py
src/items.py
src/mob.py                   # ADD: to_dict()
src/room.py                  # ADD: to_dict(), info_dict(), shadow in look
src/world.py
src/races.py
src/classes.py
src/kin_sense.py             # ADD: shadow presences in detection
src/factions.py              # ADD: event log hook
src/religion.py              # ADD: gmcp emit, event log hook
src/location_effects.py
src/wandering_gods.py
src/spawning.py
src/crafting.py
src/quests.py                # ADD: event log hook, gmcp emit
src/conditions.py            # ADD: gmcp emit
src/ai_player.py
src/party.py
src/schedules.py
src/chat.py
```

### New Files to Create

```
src/gmcp.py                  # GMCP protocol output — Phase 2 blocker
src/websocket_server.py      # WebSocket bridge for Veil — Phase 1 blocker
src/shadow_presence.py       # Shadow presence system — Phase 3
src/mcp_bridge.py            # Internal API for MCP server — Phase 3
src/event_log.py             # Player event logging for DM Agent — Phase 3
src/events.py                # World event broadcast system — Phase 3
```

**Total new files: 6**  
**Total files with additions: 10**  
**Total files untouched: 14**

---

## How OrekaMUD Connects to Veil

```
Veil Browser Client
        │
        │ wss://play.orekamud.com/ws
        ▼
Veil Gateway (veil/gateway/main.py)
        │
        │ Raw bytes via WebSocket
        ▼
OrekaMUD WebSocket Server (src/websocket_server.py)
        │
        │ Telnet protocol internally
        ▼
OrekaMUD Engine (main.py → all src/ modules)
        │
        ├── GMCP data → Veil Client panels
        │   (character sheet, Kin-sense, map, deity, factions)
        │
        ├── Shadow Presence API ← Veil AI Layer
        │   (creates/removes shadows, injects events)
        │
        └── MCP Bridge (port 8001) ← Veil MCP Server
            (game state reads, world event writes,
             message delivery, reputation changes)
```

---

## Port Map

| Port | Service | Exposed |
|---|---|---|
| 4000 | MUD telnet | Public — legacy clients |
| 8080 | World map HTTP | Public |
| 8765 | WebSocket bridge | Public — via nginx at play.orekamud.com |
| 8001 | MCP bridge REST | Internal only — 127.0.0.1 |

---

## Environment Variables (New)

Add these alongside existing config:

```env
# WebSocket
WS_PORT=8765
WS_HOST=0.0.0.0

# MCP Bridge (internal)
MCP_BRIDGE_PORT=8001
MCP_BRIDGE_HOST=127.0.0.1

# Veil auth (for validating player tokens from Veil)
VEIL_JWT_SECRET=same_secret_as_veil_gateway

# Event log
EVENT_LOG_PATH=data/events/player_events.jsonl
EVENT_LOG_RETENTION_DAYS=30
```

---

## Testing Veil Integration

### Test 1 — WebSocket connects

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket bridge
wscat -c ws://localhost:8765

# You should see the OrekaMUD connection screen
# Type as normal — full MUD session over WebSocket
```

### Test 2 — GMCP emits correctly

```bash
# Connect via MUD client that supports GMCP (Mudlet)
# Enable GMCP in Mudlet → Settings → GMCP
# Open Mudlet's GMCP inspector
# Move rooms — verify Room.Info arrives
# Enter combat — verify Char.Vitals updates
# Change faction rep — verify Char.Factions updates
```

### Test 3 — Shadow presence appears in room

```bash
# Terminal 1: Log in as player A via telnet
telnet localhost 4000
# Log in, navigate to the Chapel (vnum 1)

# Simulate a shadow presence creation (admin command):
@shadow create Jessie Elia 1

# Player A types: look
# Should see: "Jessie stands nearby, lost in quiet
#              conversation with Elia."
```

### Test 4 — MCP bridge responds

```bash
# With MUD running, query the bridge directly:
curl http://localhost:8001/world/state
curl http://localhost:8001/room/1001
curl http://localhost:8001/player/YourCharacterName
```

### Test 5 — Full Veil connection

```bash
# Start MUD server
python main.py

# Start Veil gateway (in veil repo)
cd ../veil && python gateway/main.py

# Open browser
open http://localhost:5173

# Click Play Now
# Verify: terminal renders, status bar shows HP/AC/MV
# Type: look
# Verify: room description appears correctly
```

---

## Tick System (Existing — for reference)

| Tick | Interval | Purpose |
|---|---|---|
| `spawn_respawn_tick` | 30s | Respawn dead mobs |
| `location_effects_tick` | 60s | Environmental hazards |
| `wandering_gods_tick` | 60s | Move deities between shrines |
| `hunger_thirst_tick` | 60s | Survival mechanics |
| `schedule_tick` | 30s | NPC behavior schedules |
| `ambient_echo_tick` | varies | Atmospheric room messages |
| `log_players` | periodic | Player activity logging |

Consider adding:

| Tick | Interval | Purpose |
|---|---|---|
| `gmcp_tick` | 5s | Push GMCP vitals even when nothing changes — keeps client panels alive |
| `event_log_flush` | 60s | Flush buffered event log entries to disk |

---

## World Stats (Current)

| Stat | Count |
|---|---|
| Rooms | 1,615 |
| Area files | 12 |
| Mobs | 366 |
| Bestiary creatures | 238 |
| Playable races | 15 |
| Classes | 12 |
| Feats | 88 |
| Deities | 13 |
| Factions | 10 |
| Crafting recipes | 32 |
| Room effects | 83 |
| Special materials | 12 |
| Rune-circle types | 12 |

---

## Data Files (Existing)

```
data/
├── areas/              # 12 JSON area files — 1,615 rooms
├── players/            # Per-player JSON files
├── mobs.json           # 366 mob definitions
├── mobs_bestiary.json  # 238 bestiary templates
├── guilds.json         # 10 faction definitions
├── deities.json        # 13 deity definitions
├── special_materials.json
├── recipes.json        # 32 crafting recipes
└── achievements.json
```

Add after Phase 3:
```
data/
└── events/
    └── player_events.jsonl   # Rolling event log for DM Agent
```

---

## Lore Files (For AI Indexing)

The Veil AI layer indexes these for RAG. They live in the lore directory alongside the MUD codebase.

```
World Regions history/
├── World_of_Oreka_Complete_Lore.md
├── TwinRivers_Regional_Guide_v4.docx
├── Kinsweave_v4.docx
├── EternalSteppe_v4.docx
├── GatefallReach_Regional_Guide_v3.docx
├── Tidebloom_v4.docx
├── DeepwaterMarches_v4.docx
└── InfiniteDesert_v4.docx
```

The Canon Bible DM-only sections are indexed separately with `is_dm_only=true` — these are only accessible to the DM Agent, not the player-facing AI assistant.

---

## Build Order (OrekaMUD side only)

```
Phase 1 support (needed before Kickstarter):
  Week 1    src/websocket_server.py
  Week 1    Hook ws_server into main.py gather()
  Week 2    Test: wscat connects, full MUD session over WebSocket

Phase 2 support (needed before Pro tier launch):
  Week 5    src/gmcp.py
  Week 5    Add to_dict() methods to character.py, room.py, mob.py
  Week 5    Hook GMCP emits into combat.py, conditions.py, religion.py,
             factions.py, quests.py, room.py
  Week 6    Test: Mudlet GMCP inspector shows all 7 data packages

Phase 3 support (needed before Ultimate tier):
  Week 17   src/shadow_presence.py
  Week 17   Hook say command in commands.py
  Week 17   Hook look command in room.py
  Week 17   Hook Kin-sense in kin_sense.py
  Week 17   Hook combat in combat.py
  Week 18   src/mcp_bridge.py — all endpoints
  Week 18   src/event_log.py — all hooks
  Week 18   src/events.py — broadcast system
  Week 18   Hook event log into combat.py, factions.py, quests.py, religion.py
  Week 18   Hook mcp_bridge into main.py gather()
  Week 19   Test: curl MCP bridge endpoints return correct data
  Week 19   Test: shadow presence appears in room for real players
  Week 19   Test: Enter World materializes player at correct room
```

---

## The Connection in One Sentence

OrekaMUD is the world. Veil is the door. The six new files and ten small hooks are the hinges that connect them.

---

*OrekaMUD — the world of Oreka, running.*  
*Connect: `telnet 47.188.185.168 4000`*