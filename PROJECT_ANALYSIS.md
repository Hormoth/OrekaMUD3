# OrekaMUD3 Project Analysis

## Overview

OrekaMUD3 is a Python-based Multi-User Dungeon (MUD) that implements D&D 3.5 Edition mechanics. The project uses an asynchronous telnet server architecture with JSON-based data persistence.

---

## Project Structure

```
OrekaMUD3/
├── main.py                    # Server entry point
├── startup                    # Build script
├── Road_map.json              # Development roadmap
├── oreka_mud/
│   ├── main.py               # Main server logic
│   ├── src/                  # Core game modules
│   │   ├── character.py      # Character class & mechanics
│   │   ├── classes.py        # D&D 3.5 classes (12 classes)
│   │   ├── combat.py         # Combat system
│   │   ├── commands.py       # 80+ game commands
│   │   ├── feats.py          # Feat system
│   │   ├── items.py          # Item system
│   │   ├── mob.py            # NPC/Monster system
│   │   ├── quests.py         # Quest framework
│   │   ├── room.py           # Room class
│   │   ├── spells.py         # Spell & domain system
│   │   └── world.py          # World management
│   ├── data/
│   │   ├── areas/            # Room definitions (JSON)
│   │   │   └── Chapel.json   # Main starting area
│   │   ├── players/          # Player save files
│   │   ├── help/             # Help documentation
│   │   ├── socials/          # Social emotes
│   │   ├── items.json        # Item database (40+ items)
│   │   ├── mobs.json         # Monster database
│   │   └── materials.json    # Crafting materials
│   ├── config/
│   │   └── settings.json     # Server configuration
│   ├── utils/                # Utility modules
│   │   ├── database.py       # MongoDB utilities
│   │   ├── logging_utils.py  # Logging
│   │   └── api.py            # API utilities
│   └── tests/                # Unit tests
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3 |
| Server | telnetlib3 (async telnet) |
| Networking | asyncio |
| Storage | JSON files (MongoDB configured but unused) |
| Port | 4000 |

---

## Core Systems Implemented

### 1. Character System (`src/character.py`)

**Attributes:**
- Six ability scores (STR, DEX, CON, INT, WIS, CHA)
- HP, AC, Level, XP
- Skills dictionary with D&D 3.5 skill ranks
- Spells (known, per day, prepared)
- Feats with prerequisites
- Alignment and deity
- Elemental affinity

**Character States:** Exploring, Combat

### 2. Class System (`src/classes.py`)

12 D&D 3.5 Classes fully implemented:

| Class | Hit Die | BAB | Key Features |
|-------|---------|-----|--------------|
| Barbarian | d12 | Full | Rage, Fast Movement |
| Bard | d6 | 3/4 | Bardic Music, Arcane Spells |
| Cleric | d8 | 3/4 | Divine Spells, Turn Undead, Domains |
| Druid | d8 | 3/4 | Wild Shape, Animal Companion |
| Fighter | d10 | Full | Bonus Feats |
| Monk | d8 | 3/4 | Flurry of Blows, Unarmed Strike |
| Paladin | d10 | Full | Lay on Hands, Divine Spells |
| Ranger | d10 | Full | Favored Enemy, Two-Weapon |
| Rogue | d6 | 3/4 | Sneak Attack, Evasion |
| Sorcerer | d4 | 1/2 | Spontaneous Arcane |
| Wizard | d4 | 1/2 | Prepared Arcane, Spellbook |
| Warlock | d6 | 3/4 | Eldritch Blast |

### 3. Combat System (`src/combat.py`)

- D20 attack rolls with BAB modifiers
- Critical hits on natural 20
- Damage calculation with ability modifiers
- XP awards based on CR vs character level
- Loot system (gold and items by CR tier)
- Combat maneuvers (disarm, trip, grapple, etc.)

### 4. Spell System (`src/spells.py`)

**Features:**
- Spell components (Verbal, Somatic, Material)
- Spell levels by class
- Schools of magic with descriptors
- Divine domains with granted powers
- Spell preparation for Wizards/Clerics

**Domains Implemented:**
- Air, Animal, Chaos, Death, Destruction
- Earth, Evil, Fire, Good, Healing
- Knowledge, Law, Luck, Magic, Plant
- Protection, Strength, Sun, Travel
- Trickery, War, Water

### 5. Feat System (`src/feats.py`)

**Prerequisite Types:**
- Ability score minimums
- Base Attack Bonus requirements
- Other feats (chains)
- Skill ranks
- Class/race requirements

**Sample Feat Chains:**
- Power Attack → Cleave → Great Cleave
- Dodge → Mobility → Spring Attack
- Combat Expertise → Improved Disarm/Trip/Feint

### 6. Item System (`src/items.py`)

**Item Types:**
- Weapons (simple, martial, exotic)
- Armor (light, medium, heavy)
- Shields
- Potions, Scrolls, Wands
- Wondrous items, Rings, Amulets
- Mundane gear

**Materials System:**
- 30+ crafting materials
- Material properties affect durability
- Item HP and erosion tracking

### 7. Room/World System

**Room Properties:**
- vnum (unique identifier)
- Name and description
- Exits (direction → destination vnum)
- Flags (safe, altar, temple, etc.)
- Dynamic contents (mobs, players, items)

**Main Area: Chapel of the Elemental Lords**
- Central altar (vnum 1000)
- Four elemental quadrants (Stone, Fire, Water, Wind)
- 12+ connecting streets
- 8 meditation passages

---

## Races Available

1. Human
2. Half-Elf
3. Elf
4. Dwarf
5. Halfling
6. Gnome
7. Half-Orc
8. Tiefling
9. Aasimar
10. Eruskan (Human)
11. Half-Giant
12. Drow
13. Genasi (Elemental)
14. Dragonborn

---

## Commands Summary (80+)

**Movement:** north, south, east, west, look, exits, recall

**Combat:** kill, cast, flee

**Interaction:** say, talk, buy, sell, list, appraise

**Inventory:** get, drop, inventory, wear, remove

**Information:** score, stats, skills, spells, who, help, progression

**Skills:** 40+ skill commands (climb, hide, search, etc.)

**Builder (@prefix):** @dig, @desc, @exit, @flag, @mobadd, @itemadd

**Admin:** gecho, levelup, saveplayer, backupplayer

---

## What's Working

- Telnet server with async client handling
- Full character creation wizard
- 12 D&D 3.5 classes with mechanics
- Combat with XP and loot
- 40+ items in database
- Feat system with prerequisites
- Spell system with domains
- Skill system with point allocation
- Room navigation and building
- Player persistence (JSON)
- Builder commands for zone creation

---

## What's Missing/Incomplete

### High Priority (Core D&D 3.5 Feel)
- [ ] Death and respawn mechanics
- [ ] More monsters (need full bestiary)
- [ ] Encounter/spawn system
- [ ] Rest/healing mechanics
- [ ] More spells castable
- [ ] Equipment slots and wearing gear
- [ ] Initiative and turn-based combat
- [ ] Saving throws in combat
- [ ] Conditions and status effects application
- [ ] Level progression with class feature unlocks

### Medium Priority
- [ ] Economy/shop system integration
- [ ] Area reset/repopulation
- [ ] More areas and zones
- [ ] Quest system expansion
- [ ] NPC dialogue trees
- [ ] Combat log formatting

### Lower Priority (From Roadmap)
- [ ] Chat channels (global, guild, group)
- [ ] Help system content
- [ ] Guilds/clans
- [ ] Banking/auction house
- [ ] Player housing
- [ ] Web interface
- [ ] PvP system

---

## Key NPCs

### Immortals
- **Dagdan, The United Sun** - Level 60 Half-Giant (Admin)
- **Hareem, The Golden Rose** - Level 60 Human (Admin)

### Monsters
- **Stone Golem** (CR 11) - Immune to magic, DR 10/adamantine
- **Water Elemental** (CR 3) - Water mastery, drench

---

## Data File Locations

| Data Type | Location |
|-----------|----------|
| Players | `/data/players/*.json` |
| Rooms | `/data/areas/*.json` |
| Items | `/data/items.json` |
| Mobs | `/data/mobs.json` |
| Materials | `/data/materials.json` |
| Help | `/data/help/*.json` |
| Settings | `/config/settings.json` |

---

## Server Configuration

- **Port:** 4000
- **Protocol:** Telnet
- **Encoding:** UTF-8 with ASCII safety

---

## Development Notes

### Design Patterns Used
- Async event loop for concurrency
- Dictionary-based command dispatch
- JSON serialization for persistence
- D&D 3.5 OGL mechanics compliance

### Code Quality
- Well-organized module structure
- Consistent naming conventions
- Good separation of concerns
- Test framework present (needs expansion)

---

## Getting Started

1. Ensure Python 3 is installed
2. Install dependencies: `pip install telnetlib3`
3. Run server: `python oreka_mud/main.py`
4. Connect via telnet: `telnet localhost 4000`
5. Create character or login as existing player

---

## Next Steps for D&D 3.5 Enhancement

To make this feel like authentic D&D 3.5:

1. **Combat Enhancement**
   - Initiative system
   - Full action economy (standard/move/swift/free)
   - Attack of opportunity
   - Flanking and cover

2. **More Content**
   - Expand monster bestiary (CR 1-20)
   - More spell implementations
   - Additional feats
   - Magic items

3. **Game Flow**
   - Death/dying states (-1 to -9 HP)
   - Natural healing and rest
   - Condition tracking
   - Environmental hazards

4. **World Building**
   - Dungeon zones
   - Town areas with services
   - Wilderness regions
   - Random encounters
