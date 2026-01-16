# OrekaMUD3 Development Status

A D&D 3.5 Edition MUD (Multi-User Dungeon) implementation in Python.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Implemented Systems](#implemented-systems)
3. [System Details](#system-details)
4. [Integration Status](#integration-status)
5. [Test Coverage](#test-coverage)
6. [Roadmap](#roadmap)
7. [Known Issues](#known-issues)

---

## Project Overview

**Total Codebase:** ~14,300 lines of Python
**Core Systems:** 10 major modules
**Commands:** 180+ player/admin commands
**Completion Status:** ~92% core mechanics

### Architecture
- **Server:** Async telnet server for multiplayer
- **Persistence:** JSON-based save/load with backups
- **Rules:** D&D 3.5 OGL compliance
- **Design:** Modular system separation

---

## Implemented Systems

| Module | Lines | Status | Description |
|--------|-------|--------|-------------|
| `commands.py` | 3,720 | Complete | 180+ commands (player, admin, builder) |
| `spells.py` | 2,090 | Complete | 60+ spells, 23 domains, full casting |
| `feats.py` | 1,577 | Complete | 100+ feats with prerequisites |
| `character.py` | 1,187 | Complete | Stats, equipment, conditions, auto-attack |
| `quests.py` | 1,132 | Complete | Quest system with objectives and rewards |
| `combat.py` | 1,189 | Complete | Initiative, attacks, auto-attack, action queue |
| `skills.py` | 982 | Complete | 40+ D&D 3.5 skills with synergies |
| `maneuvers.py` | 766 | Complete | Combat maneuvers (disarm, trip, grapple) |
| `conditions.py` | 484 | Complete | 20+ conditions with mechanical effects |
| `classes.py` | 384 | Complete | 11 classes with full progression |
| `items.py` | 99 | Basic | Item framework, needs expansion |
| `mob.py` | 414 | Partial | NPC/monster system |
| `room.py` | 22 | Minimal | Room structure |

---

## System Details

### Character System (`character.py`)
- Six ability scores (STR, DEX, CON, INT, WIS, CHA) with modifiers
- D&D 3.5 Health Status (Healthy, Disabled, Dying, Dead, Stable)
- 14 equipment slots with automatic AC recalculation
- Condition tracking with duration management
- Spell slots and preparation for casters
- Domain support for divine casters (Cleric)
- Skill ranks and synergy bonuses
- Feat integration
- JSON persistence with backup system
- **Auto-attack system** with combat target tracking
- **Action queue** for spells, skills, feats, maneuvers

### Combat System (`combat.py`)
- Initiative rolling (d20 + DEX + feat bonuses)
- Attack rolls with BAB calculation
- Critical hits on natural 20
- Saving throws (Fortitude, Reflex, Will)
- Action economy (Standard, Move, Swift, Full-round, Immediate)
- Combat instances per room with turn order
- Flanking detection
- Attacks of opportunity with feat support
- Quest kill triggers
- **Auto-attack** - Automatically attacks target each round
- **Action queue execution** - Queued spells/maneuvers replace auto-attack
- **Mob AI targeting** - Mobs auto-target random players

### Spell System (`spells.py`)
- **60+ spells** across levels 0-9
- **8 schools:** Abjuration, Conjuration, Divination, Enchantment, Evocation, Illusion, Necromancy, Transmutation
- **23 divine domains** with domain powers and spells
- **Spell effects:** Damage, healing, buffs, debuffs, conditions
- Saving throw mechanics with DC calculation
- Touch attacks and ranged touch attacks
- Special handling for Magic Missile and Scorching Ray
- Component enforcement (Verbal, Somatic, Material)
- Metamagic framework

### Feats System (`feats.py`)
- **100+ feats** across categories:
  - General (Alertness, Toughness, Iron Will)
  - Combat (Power Attack, Cleave, Dodge, Mobility)
  - Metamagic (Empower, Quicken, Maximize)
  - Item Creation (Brew Potion, Craft Wand)
- Prerequisite checking (level, BAB, ability scores, other feats)
- Feat chains (Power Attack -> Cleave -> Great Cleave)
- Automatic bonus application

### Quest System (`quests.py`)
- Quest states: Unavailable, Available, Active, Complete, Turned In, Failed
- **10 objective types:** Kill, Collect, Deliver, Escort, Explore, Talk, Use, Defend, Skill Check, Choice
- Progress tracking with counters
- Rewards: XP, gold, items, reputation
- Prerequisites (level, quest chains, reputation)
- Quest chains and branching paths
- Optional and hidden objectives

### Skills System (`skills.py`)
- **40+ D&D 3.5 skills** mapped to abilities
- Trained-only skill enforcement
- Armor check penalties
- Skill synergies (5+ ranks grants bonuses)
- Take 10 / Take 20 framework

### Maneuvers System (`maneuvers.py`)
- **Combat maneuvers:** Disarm, Trip, Bull Rush, Grapple, Overrun, Sunder, Feint
- **Special attacks:** Whirlwind Attack, Spring Attack, Stunning Fist
- CMB/CMD calculations with size modifiers
- Feat bonus integration

### Conditions System (`conditions.py`)
- **20+ conditions:** Blinded, Stunned, Paralyzed, Prone, Grappled, etc.
- Mechanical effects (AC penalty, attack penalty, speed reduction)
- Duration tracking in combat rounds
- Stacking rules enforcement

### Classes System (`classes.py`)
| Class | Hit Die | BAB | Good Saves |
|-------|---------|-----|------------|
| Barbarian | d12 | Full | Fort |
| Bard | d6 | 3/4 | Ref, Will |
| Cleric | d8 | 3/4 | Fort, Will |
| Druid | d8 | 3/4 | Fort, Will |
| Fighter | d10 | Full | Fort |
| Monk | d8 | 3/4 | All |
| Paladin | d10 | Full | Fort, Will |
| Ranger | d10 | Full | Fort, Ref |
| Rogue | d6 | 3/4 | Ref |
| Sorcerer | d4 | 1/2 | Will |
| Wizard | d4 | 1/2 | Will |

---

## Integration Status

### Fully Connected
| System A | System B | Integration |
|----------|----------|-------------|
| Combat | Character | Attack/damage uses stats, HP tracking |
| Combat | Conditions | Conditions apply penalties in combat |
| Spells | Combat | Spell casting applies damage/healing/conditions |
| Spells | Quests | Spell kills trigger quest objectives |
| Feats | Combat | Feat bonuses apply to attacks/damage |
| Skills | Commands | Skill checks work via commands |
| Quests | Character | Quest log tracked per character |
| Auto-Attack | Combat | Executes queued actions or auto-attacks each turn |
| Auto-Attack | Spells | Queued spells cast via action queue |
| Auto-Attack | Maneuvers | Queued maneuvers execute via action queue |

### Partially Connected
| System | Issue | Priority |
|--------|-------|----------|
| Conditions in Combat | Most conditions defined but not all automatically applied during combat | Medium |
| Maneuvers as Commands | Only `springattack` exposed; others need command wrappers | High |
| Feat Combat Bonuses | Some feat effects not fully integrated in attack resolution | Medium |
| Item Effects | Equipment AC works; magical effects limited | Medium |

### Not Connected
| System | Status | Priority |
|--------|--------|----------|
| AI/Mob Behavior | Framework only, no intelligent behavior | High |
| Events | Stub file, no implementation | Low |
| Narrative | Stub file, no implementation | Low |
| Housing/Guilds | Not implemented | Low |

---

## Test Coverage

### Current Tests (18 passing)
| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_core.py` | 5 | Character, Combat, Feats, Spells, World |
| `test_feats.py` | 3 | Feat eligibility, prerequisites |
| `test_spellcasting.py` | 4 | Spell casting, slots, validation |
| `test_commands.py` | 3 | Levelup, skills, score display |
| `test_combat.py` | 1 | Attack roll format |
| `test_quests.py` | 1 | Quest completion |
| `test_ai.py` | 1 | State transition |

### Testing Gaps
- No integration tests for full combat encounters
- No tests for condition application during combat
- Limited spell effect testing
- No quest progression tests
- No maneuver tests

---

## Roadmap

### Phase 1: Integration Completion (High Priority)
- [ ] Expose all combat maneuvers as commands (disarm, trip, grapple, etc.)
- [ ] Ensure all condition effects apply during combat resolution
- [ ] Complete feat bonus integration in attack/damage calculations
- [ ] Add more spell commands (memorize list, domain selection)

### Phase 2: Content Expansion (Medium Priority)
- [ ] Add more monsters/NPCs with varied abilities
- [ ] Create starter areas with room descriptions
- [ ] Expand item system with magical properties
- [ ] Add more quests with branching storylines

### Phase 3: AI & Behavior (Medium Priority)
- [ ] Implement intelligent mob AI (aggression, tactics)
- [ ] Add NPC dialogue trees
- [ ] Create patrol and respawn systems
- [ ] Add faction/reputation-based NPC reactions

### Phase 4: Advanced Features (Low Priority)
- [ ] Player housing system
- [ ] Guild/clan support
- [ ] Crafting system
- [ ] Weather and time-of-day effects
- [ ] Events and world scripting

### Phase 5: Testing & Polish
- [ ] Add integration tests for combat flow
- [ ] Add tests for spell effects
- [ ] Add tests for quest progression
- [ ] Performance optimization
- [ ] Documentation for builders

---

## Known Issues

1. **Deprecation Warning:** `asyncio.get_event_loop()` in commands.py:1906 - should use `asyncio.get_running_loop()` or create new loop explicitly

2. **Maneuver Commands:** Combat maneuvers (disarm, trip, etc.) are implemented in `maneuvers.py` but not exposed as player commands except for `springattack`

3. **Condition Auto-Application:** Some conditions (like from spells) are applied manually; need systematic application in combat loop

4. **Item System:** Basic framework exists but magical item effects are limited

5. **Test Coverage:** ~18 tests for 14K lines of code; needs significant expansion

---

## Quick Reference

### Running Tests
```bash
python -m pytest oreka_mud/tests/ -v
```

### Key Files
- `src/character.py` - Character class and stats
- `src/combat.py` - Combat resolution
- `src/commands.py` - All player commands
- `src/spells.py` - Spell definitions and casting
- `src/feats.py` - Feat definitions and prerequisites

### Command Categories
- **Movement:** north, south, east, west, up, down, recall
- **Combat:** kill, flee, cast, attack
- **Auto-Attack:** queue (q), showqueue (sq), clearqueue (cq), autoattack (aa), target
- **Inventory:** get, drop, inventory, wear, remove, equipment
- **Information:** score, skills, spells, help, who
- **Builder:** @dig, @desc, @exit, @mobadd, @itemadd
- **Admin:** gecho, levelup, saveplayer, force

### Auto-Attack Commands
| Command | Shortcut | Description |
|---------|----------|-------------|
| `queue <type> <name> [target]` | `q` | Queue spell/skill/feat/maneuver for next turn |
| `showqueue` | `sq` | Show currently queued action |
| `clearqueue` | `cq` | Clear the queued action |
| `autoattack` | `aa` | Toggle auto-attack on/off |
| `target <mob>` | - | Set auto-attack target without attacking |

**Queue Types:** spell, skill, feat, maneuver, item

**Examples:**
```
kill goblin              # Start combat, sets target
queue spell fireball     # Cast fireball next turn instead of attacking
queue maneuver trip goblin   # Trip attempt next turn
sq                       # Check what's queued
aa                       # Toggle auto-attack off
```

---

*Last Updated: January 2026*
