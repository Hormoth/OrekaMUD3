# OrekaMUD3 — A D&D 3.5 Edition MUD Built for the Modern Era

## What Is It?

OrekaMUD3 is a fully playable Multi-User Dungeon that implements the D&D 3.5 Edition ruleset from the ground up in Python. Players connect via telnet, WebSocket (Veil Client), or any GMCP-compatible MUD client. They create characters using the complete 3.5 character creation process and play through a persistent 1,624-room world with real-time combat, spellcasting, equipment, quests, factions, religion, crafting, and AI-powered NPC dialogue.

It is not a fork of DikuMUD, CircleMUD, or any legacy codebase. Every line — 35,000+ across 42 source modules — was written from scratch with modern Python async architecture. The result is a MUD that plays like a tabletop D&D session — not a simplified approximation, but the actual rules.

---

## The Elevator Pitch

> **"What if you could play D&D 3.5 as a MUD — with real opposed rolls, iterative attacks, 88 feats, 82 spells, 6 metamagic types, 37 conditions, 10 combat maneuvers, 60 crafting recipes, 10 factions, 13 deities, dynamic weather, a 6-chapter story arc, player housing, a unique Kin-sense system, and NPCs that talk back using AI?"**

---

## Core Systems

### Character Creation — The Full D&D Experience

Character creation walks players through every step of building a 3.5 character:

- **20 unique races** — Not generic fantasy. Half-Giants, four elven subraces (Hasura, Kovaka, Pasua, Na'wasua), three dwarven clans (Visetri, Pekakarlik, Rarozhki), four human cultures (Orean, Taraf-Imro, Eruskan, Mytroan), Halflings, Silentborn, Half-Domnathar, Farborn Humans, and non-player races (Goblin, Hobgoblin, Warg, Tanuki). Each with unique ability mods, vision, proficiencies, elemental affinity, and Kin-sense category.
- **12 classes** — Barbarian, Bard, Cleric, Druid, Fighter, Magi, Monk, Paladin, Ranger, Rogue, Sorcerer, Wizard. Each with correct hit die, BAB progression, save progressions, skill points, class skills, and class features by level.
- **Magi class** — Original Oreka class with three paths (Seer, Keeper, Voice), each granting unique skill bonuses and elemental attunement abilities.
- **Racial stat modifiers applied at creation** — Hasura Elf gets +2 DEX, +2 INT, -2 CON. Half-Giant gets +4 STR, +2 CON, -2 DEX, -2 CHA. Racial speed sets movement points.
- **4d6-drop-lowest ability scores** — Rolled live during creation with racial adjustments shown.
- **38+ skills** with class/cross-class costs, rank limits, armor check penalties, and feat bonuses.
- **88 feats** with full prerequisite checking (level, BAB, ability scores, other feats). 70 have mechanical effects that auto-apply.
- **82 spells** across 8 schools, with prepared vs spontaneous casting, domain spells, component requirements, and spell resistance.
- **13 deities** with domain grants — 4 Elemental Lords, 8 Ascended Gods, plus atheism. 23+ cleric domains.
- **9 alignments** with class and deity restrictions enforced.

A player sits down, rolls stats, picks a race (sees modifiers applied), picks a class, allocates skill points, chooses feats and spells, selects a deity, and walks into the world. Just like sitting at a table.

### Combat — D&D 3.5, Not a Simplification

This is not "you hit the goblin for 5 damage." This is:

```
=== COMBAT BEGINS ===
Round 1
Initiative Order:
  >>> Aelthara: 18
      Goblin: 12

Aelthara's turn.
Aelthara hits Goblin for 7 damage! (d20(14) + 5 = 19 vs AC 13)
Aelthara (off-hand) hits Goblin for 4 damage!
```

Under the hood:

- **Initiative** — d20 + Dex mod + Improved Initiative feat bonus + condition modifiers.
- **Full action economy** — Standard, Move, Swift, Free, Full-Round, and Immediate actions. Maneuvers consume your standard action. Spells consume slots.
- **Attack rolls** — BAB (calculated from class `bab_progression`: full/3/4/1/2) + Str/Dex (Weapon Finesse) + feat bonuses (Weapon Focus, Greater Weapon Focus) + condition penalties + flanking + temporary buffs + size modifiers, vs AC calculated from armor + shield + Dex + dodge + deflection + natural armor + spell bonuses + size + condition penalties.
- **Iterative attacks** — At BAB +6 you get two attacks. At +11, three. At +16, four. Each at cumulative -5.
- **Dual wielding** — Off-hand attacks with Two-Weapon Fighting feat. Light weapons reduce penalty. Half STR to off-hand damage per 3.5 rules.
- **Critical hits** — Natural 20 threatens, confirmation roll required, x2 damage. Keen weapons threaten on 19-20.
- **Sneak Attack** — Rogues deal bonus d6s when flanking, attacking flat-footed targets, OR striking from hidden.
- **Power Attack / Combat Expertise** — Trade attack for damage or AC, toggled by the player.
- **Saving throws** — Fortitude, Reflex, Will. Base saves calculated from class progression (good = 2+level/2, poor = level/3) + ability mod + feat bonuses (Iron Will, Lightning Reflexes, Great Fortitude) + condition penalties + spell buffs + Paladin Divine Grace (CHA to all saves).
- **Damage Reduction** — Barbarian DR scales with level. Reduces incoming damage automatically.
- **Size modifiers** — Large creatures get -1 AC/attack, Small get +1. Derived from racial data.
- **Special weapon properties** — Keen (expanded crit range), Flaming/Frost/Shock (+1d6 elemental), Holy (+2d6 vs evil), Vorpal (instant kill on confirmed crit nat 20). Elemental resistance applied to bonus damage.
- **Concentration checks** — Casters hit during combat must pass Concentration (DC 10 + damage taken) or lose the spell.
- **Spell Resistance** — Casters roll d20 + caster level (+ Spell Penetration feats) vs target SR. Fail = spell fizzles.

### 13 Class Abilities — Every Class Plays Differently

| Class | Ability | How It Works |
|-------|---------|-------------|
| **Barbarian** | Rage | +4 STR/CON, +2 Will, -2 AC. Duration = 3+CON mod rounds. Fatigued after. |
| **Bard** | Inspire Courage | +1/+2/+3 morale to attack/damage for all allies in room. Scales at levels 8/14. |
| **Cleric** | Turn Undead | 2d6+CHA+level check vs undead HD. Turned = frightened. Destroyed if HD < level-4. |
| **Druid** | Wild Shape | Transform into Wolf (+2 DEX), Bear (+4 STR), or Eagle (+4 DEX, fly). Stores original stats. |
| **Monk** | Flurry of Blows | Extra attack at -2 penalty. Unarmed damage scales: 1d6 -> 1d8 -> 1d10 -> 2d6 -> 2d8 -> 2d10. |
| **Paladin** | Smite Evil | +CHA to attack, +level to damage vs evil. Lay on Hands heals level x CHA HP/day. Divine Grace adds CHA to all saves. |
| **Ranger** | Favored Enemy | +2 damage vs chosen creature types. Combat Style grants free archery or TWF feats. |
| **Rogue** | Evasion | Successful Reflex save = 0 damage (not half). Improved Evasion at level 10: failed save = half. Uncanny Dodge retains Dex to AC when flat-footed. |

### 10 Combat Maneuvers — All by the Book

Every D&D 3.5 special attack is implemented with correct opposed rolls:

| Maneuver | Mechanic |
|----------|----------|
| **Disarm** | Touch attack + opposed attack roll. Applies "disarmed" condition (-4 attacks, unarmed only). |
| **Trip** | Touch attack + opposed Str check (defender uses higher of Str/Dex). Size modifiers x4. |
| **Grapple** | Touch attack + opposed grapple check (BAB + Str + size). Unlocks gdamage/gpin/gescape. |
| **Bull Rush** | Opposed Str + size. Push back 5ft + 5ft per 5 margin. |
| **Overrun** | Opposed Str + size. Loser may be knocked prone. |
| **Sunder** | Opposed attack roll. Deals damage to opponent's weapon. |
| **Feint** | Bluff vs Sense Motive. Success denies Dex to AC. |
| **Whirlwind Attack** | Full-round: one attack against every adjacent enemy. |
| **Spring Attack** | Move-attack-move. Target gets no AoO. |
| **Stunning Fist** | Unarmed strike + Fort save or stunned 1 round. |

Plus **Charge** (+2 attack, -2 AC), **Total Defense** (+4 dodge AC, forfeit attacks), and **Fighting Defensively** (-4 attack, +2 dodge AC).

### Combat Stances and Options

| Command | Effect |
|---------|--------|
| `kill <target>` | Initiate combat, auto-attack each round |
| `queue spell <name>` | Cast a spell on your next turn instead of auto-attack |
| `queue maneuver <name>` | Execute a combat maneuver on your next turn |
| `fullattack` | Use all iterative attacks this round |
| `flurry` | Monk: extra attack at -2 penalty |
| `charge <target>` | +2 attack, -2 AC, must not have moved |
| `totaldefense` | +4 dodge AC, skip attacks |
| `defensive` | Toggle: -4 attack, +2 AC |
| `powerattack <amount>` | Trade attack bonus for damage |
| `combatexpertise <amount>` | Trade attack bonus for AC |
| `flee` | Escape combat (triggers AoO from all hostiles) |
| `wimpy <percent>` | Auto-flee when HP drops below threshold |

### 37 Status Conditions with Mechanical Effects

Not flavor text — actual mechanical modifiers:

- **Blinded**: -2 AC, loses Dex to AC, 50% miss chance, -4 Str/Dex checks
- **Grappled**: Cannot move, -4 Dex, -2 attacks, light weapons only
- **Stunned**: Cannot act, drops everything, -2 AC, loses Dex to AC
- **Prone**: -4 melee attacks, can't use ranged, +4 AC vs ranged, -4 AC vs melee
- **Disarmed**: -4 attacks, forced to fight unarmed (1d4 damage)
- **Frightened**: -2 attacks/saves/skills, must flee from source
- **Invisible**: +2 attack, attackers take -2, ignores Dex to AC
- **Poisoned**: -1 attack/saves, 1d4 damage per round, Fort DC 15 each round to end
- **Diseased**: -2 attack/saves, 3/4 speed
- **Charging**: -2 AC (from charge maneuver)
- ...and 27 more, all with duration tracking and automatic expiration.

Conditions stack. They modify attack rolls, AC, saves, damage, movement, and action availability — all calculated automatically.

### 82 Spells Across 8 Schools

Spellcasting follows 3.5 rules precisely:

- **Prepared casters** (Wizard, Cleric, Druid) prepare spells from their list, then cast from slots. Enforced in `cmd_cast`.
- **Spontaneous casters** (Sorcerer, Bard, Magi) cast any known spell using a slot of the right level.
- **Components enforced** — Verbal blocked by silence/gagged. Somatic blocked by paralysis/binding. Material components consumed from inventory.
- **Spell DCs** — 10 + spell level + casting stat modifier. Modified by Spell Focus feats.
- **Concentration checks** when casting after taking damage (DC 10 + damage taken).
- **Spell Resistance** — d20 + caster level vs SR. Spell Penetration/Greater Spell Penetration add +2/+4.
- **Domain spells** for Clerics — each domain grants bonus slots and a granted power. 23+ domains.
- **AoE spells** — Fireball, Lightning Bolt, Cone of Cold hit all enemies in the room.
- **Healing spells** — Cure Light/Moderate/Serious/Critical Wounds, Heal. Target self or allies.
- **Buff spells** — Bull's Strength, Mage Armor, Shield, Bless, etc. Duration tracking with automatic expiration and stat reversal.
- **Dispel Magic** — Caster level check vs each buff on the target. Success removes the effect.

### 88 Feats with Prerequisite Trees

The full 3.5 feat system — 70 with mechanical effects that auto-apply:

- **Combat chain**: Power Attack -> Cleave -> Great Cleave
- **Mobility chain**: Dodge -> Mobility -> Spring Attack -> Whirlwind Attack
- **Ranged chain**: Point Blank Shot -> Precise Shot -> Rapid Shot -> Manyshot
- **Two-Weapon chain**: TWF -> Improved TWF -> Greater TWF + Two-Weapon Defense
- **Maneuver feats**: Improved Grapple/Disarm/Trip/Bull Rush/Overrun/Sunder (+4 bonus, no AoO)
- **Save feats**: Iron Will, Lightning Reflexes, Great Fortitude (+2 to respective saves)
- **Skill feats**: 15+ skill bonus feats, Skill Focus (+3 to chosen skill)
- **Weapon feats**: Weapon Focus (+1 attack), Greater Weapon Focus (+2), Weapon Specialization (+2 damage), Greater Weapon Specialization (+4)
- **Toughness**: +3 HP applied at character creation
- **Item creation feats**: Brew Potion, Scribe Scroll, Craft Magic Arms and Armor, Craft Wand, etc.
- **Metamagic feats**: Empower Spell, Maximize Spell, Quicken Spell, Extend Spell, Silent Spell, Still Spell — all usable via `metamagic <type> <spell>` with correct slot-level increases per D&D 3.5 rules

Prerequisites are checked at selection time. A Fighter can't take Whirlwind Attack without Dex 13, Int 13, Combat Expertise, Dodge, Mobility, Spring Attack, and BAB +4.

---

## The Gameplay Loop

### Kill -> Corpse -> Loot -> XP -> Level -> Gear Up -> Repeat

1. **Find a mob** — `look` shows NPCs in the room. `scan` shows adjacent rooms. `consider goblin` gauges difficulty.
2. **Fight it** — `kill goblin` initiates combat with initiative rolls and auto-advancing rounds.
3. **Use tactics** — `queue spell magic missile`, `disarm goblin`, `charge goblin`, `flurry`, `flee` if things go badly.
4. **Mob dies** — Corpse appears with gold and possibly items, scaled by Challenge Rating.
5. **Loot it** — `loot` transfers gold and items. Or enable `autoloot` and `autogold` to skip this step.
6. **Earn XP** — Award scales with level difference vs CR (75-1200 XP per kill). `tnl` shows progress bar.
7. **Level up** — `levelup` when you hit the threshold. Roll hit die + CON mod for HP. Gain practice points for skills.
8. **Train** — Visit Guildmaster Thorin. `practice hide 2` to spend practice points. `train strength` to boost a stat.
9. **Gear up** — Visit Merchant Lyssa. `list`, `buy leather armor`, `wear leather armor`. Equipment bonuses apply automatically.
10. **Bank your gold** — Visit Banker Goldsworth. `deposit 500`. `balance` to check savings.
11. **Repair your gear** — Visit Smith Ironforge. `repair longsword`.
12. **Die sometimes** — HP drops below -10, you're dead. `respawn` at the chapel for 10% XP penalty.
13. **Rest** — `rest` in a safe room to recover HP and spell slots. Rest at an inn for full recovery on short rest.

Every step follows D&D 3.5 rules. XP tables (levels 1-20), loot tables, CR-based encounters, spell slot recovery on rest — all correct.

### Economy System

| Command | What It Does |
|---------|-------------|
| `buy <item>` | Purchase from shopkeeper |
| `sell <item>` | Sell to shopkeeper |
| `list` | See shop inventory and prices |
| `appraise <item>` | Check what it's worth |
| `deposit <amount>` | Bank gold with Banker NPC |
| `withdraw <amount>` | Withdraw from bank |
| `balance` | Check bank balance |
| `worth` | Show all wealth (gold + bank + inventory value) |
| `auction sell <item> <price>` | List item for auction (7-day timer) |
| `auction bid <#> <amount>` | Bid on auction item |
| `auction buyout <#>` | Buy at buyout price |
| `repair <item>` | Repair equipment at Blacksmith NPC |
| `craft <recipe>` | Craft items from materials (Craft skill check) |
| `enchant <item> <type> <value>` | Enchant weapons/armor (Spellcraft check, gold cost) |

### Death and Respawn

D&D 3.5 death rules:

| HP | Status | What Happens |
|----|--------|-------------|
| > 0 | Healthy | Normal play |
| = 0 | Disabled | Single action per round |
| -1 to -9 | Dying | Unconscious, lose 1 HP/round, 10% stabilization check |
| <= -10 | Dead | Must respawn |

Respawn teleports you to the chapel at 50% HP with a 10% XP penalty. Conditions cleared. Your corpse (and its loot) stays where you died — other players can see it.

---

## Social & Communication

### 9 Chat Channels

| Channel | Command | Scope |
|---------|---------|-------|
| Say | `say <msg>` | Room (with language garbling for unknown languages) |
| RP Say | `rpsay <msg>` | Room — LLM-capable NPCs overhear and may react in character |
| Tell | `tell <player> <msg>` | Private (with AFK auto-reply, ignore list) |
| Reply | `reply <msg>` | Reply to last tell |
| Shout | `shout <msg>` | Area-wide (BFS radius 3 rooms through open exits) |
| OOC | `ooc <msg>` | Global out-of-character |
| Newbie | `newbie <msg>` | Global helper channel |
| Party | `gtell <msg>` | Party members only |
| Guild | Guild chat via guild system | Guild members only |
| Emote | `emote <action>` | Room — custom actions |

### 60 Social Verbs

`bow`, `wave`, `laugh`, `cry`, `nod`, `shrug`, `grin`, `wink`, `hug`, `poke`, `slap`, `dance`, `cheer`, `clap`, `sigh`, `groan`, `yawn`, `cough`, `whistle`, `flex`, `curtsey`, `salute`, `pat`, `tickle`, `comfort`, `thank`, `apologize`, `agree`, `disagree`, `shiver`, `growl`, `snicker`, `giggle`, `gasp`, `blink`, `frown`, `smirk`, `scowl`, `ponder`, `pray`, `meditate`, `stretch`, `cringe`, `cackle`, `scream`, `roar`, `purr`, `snore`, `burp`, `hiccup`, `mumble`, `mutter`, `blush`, `taunt`, `high5`, `facepalm`, `eyeroll`, `thumbsup`, `shh`, `bonk`

Each supports targeting: `bow guard` sends different messages to you, the guard, and the room.

### Party System

| Command | Effect |
|---------|--------|
| `group invite <player>` | Invite to party |
| `follow <player>` | Follow (auto-move when leader moves) |
| `assist` | Join ally's combat, target their target |
| `rescue <ally>` | Redirect mob attacks to yourself |
| `gtell <msg>` | Party-only chat |
| `group` | Show party status (HP bars for all members) |

XP splits evenly among party members present in the room.

### Guild / Clan System

Persistent player organizations with:
- Guild creation (1000 gold), invite, accept, leave, kick
- Ranks: Leader, Officer, Member, Recruit (promote/demote)
- Guild bank (deposit/withdraw by officers+)
- Guild MOTD
- Guild who list

### Additional Social Features

- **Mail** — Send letters to offline players (requires mailbox room flag)
- **Bulletin Boards** — Post and read notes in board rooms
- **Duel** — Challenge another player to non-lethal PvP (`duel <player>`, `duel accept`)
- **Ignore/Block** — Silently drop tells from blocked players
- **AFK** — Toggle with optional message, auto-replies to tells
- **Finger** — Inspect player info (online or offline from saved data)
- **Leaderboards** — Top 10 by level, XP, kills, or gold
- **Achievements** — 9+ achievements (First Blood, Warrior, Slayer, Adventurer, Veteran, Hero, Wealthy, Artisan, Explorer) that award titles

---

## Quality of Life

### Navigation & Exploration

| Command | What It Does |
|---------|-------------|
| `look` | Room description, mobs, players, corpses, exits, Kin-sense |
| `scan` | See mobs/players in adjacent rooms |
| `map` | ASCII map of nearby rooms |
| `where` | Find players/mobs across all rooms |
| `areas` | List all zones with level ranges |
| `track <name>` | Survival check to find mob/player direction |
| `consider <mob>` | Gauge difficulty (trivial/easy/even/dangerous/deadly) |
| `speedwalk` | Chain directions: `sw nnnwws` moves north x3, west x2, south |
| `recall` | Teleport to starting room |

Speedwalk also works inline — type `nnnwws` directly and it auto-moves.

### Stealth System

| Command | Effect |
|---------|--------|
| `hide` | Hide check — become invisible to others |
| `sneak` | Toggle silent movement (Move Silently check on each move) |
| `search` | Search check for traps, hidden items |

Hidden players: others must beat your Hide check with their Spot to see you. Attacking from hidden grants sneak attack damage (Rogues get bonus d6s).

### Door & Trap System

| Command | Effect |
|---------|--------|
| `open/close <dir>` | Open or close doors |
| `lock/unlock <dir>` | Lock/unlock with key in inventory |
| `pick <dir>` | Open Lock skill check vs door DC |
| `search` | Search check to detect room traps |
| `disarmtrap` | Disable Device check to disarm detected trap |

Traps trigger automatically on entry if undetected. Detected traps can be avoided or disarmed.

### Container System

| Command | Effect |
|---------|--------|
| `put <item> <container>` | Put item in bag/backpack |
| `get <item> <container>` | Get item from container |
| `peek <container>` | Look inside a container |

Containers have capacity limits. Inventory shows container item counts.

### Consumables

| Command | Effect |
|---------|--------|
| `quaff <potion>` | Drink potion (heal, buff) |
| `read <scroll>` | Cast scroll spell (Spellcraft check) |
| `use <wand>` | Use wand charge (Use Magic Device check if not your class) |
| `eat <food>` | Restore hunger |
| `drink_water <item>` | Restore thirst |

### Resource Gathering

| Command | Requires | Produces |
|---------|----------|----------|
| `fish` | Water/fishing room | Fresh Fish (food) |
| `mine` | Mine/cave room | Iron Ore, Copper Ore, Gold Nugget |
| `gather` | Forest/garden room | Healing Herb, Leather Strip, Wood Plank |

### Player Customization

| Command | Effect |
|---------|--------|
| `config` | View/toggle all preferences (brief, compact, autoexit, color, autoloot, autogold, etc.) |
| `prompt <template>` | Custom prompt with tokens (%h HP, %a AC, %x XP, %g gold, etc.) |
| `alias <name> <expansion>` | Custom command shortcuts (persisted across sessions) |
| `title <text>` | Set your character title |
| `survivalmode` | Toggle hunger/thirst mechanics |

### Information Commands

| Command | Shows |
|---------|-------|
| `score` | Full character sheet |
| `affects` | Active buffs, conditions, equipment bonuses with durations |
| `examine <thing>` | Detailed inspection of mob, item, or equipment |
| `compare <item1> <item2>` | Side-by-side item comparison |
| `worth` | Gold on hand, bank gold, inventory value, total wealth |
| `tnl` | XP progress bar to next level |
| `who` | Online players with level, class, race, idle time |
| `finger <player>` | Player info (online or offline) |
| `achievements` | Achievement progress and earned titles |
| `time` | Current game time and date |
| `weather` | Current weather and gameplay effects (dynamic per region) |
| `weather forecast` | Predicted next weather for your region |
| `story` | Narrative progress and chapter status |
| `lore <topic>` | World lore entries (17 topics) |
| `metamagic list` | Available metamagic feats and their effects |

---

## Crafting & Enchanting

### Crafting System

60 recipes across 7 craft disciplines:

| Discipline | Recipes | Example Items |
|------------|---------|---------------|
| Weaponsmithing | 8 | Iron Dagger, Iron Longsword, Embersteel Blade, Volcanic Glass Dagger |
| Armorsmithing | 6 | Steel Shield, Chain Shirt, Embersteel Plate |
| Leatherworking | 4 | Leather Armor, Wind-silk Cloak, Cured Hide |
| Alchemy | 6 | Healing Potion, Amber-sap Elixir, Antitoxin |
| Weaving | 3 | Wind-silk Robes, Spell Component Pouch |
| Jewelrycrafting | 3 | Riverstone Amulet, Moonwhisper Ring |
| Runic Crafting | 2 | Rune-carved Focus, Warding Stone |

- DC checks with success, critical success, and critical failure mechanics
- Material requirements and gold costs per recipe
- Feat and caster level requirements for magical crafting
- Oreka-specific materials (Embersteel, Wind-silk, Riverstone, Volcanic Glass, Giant-bone, Moonwhisper Silver)
- Critical failure (DC-5): materials destroyed. Normal failure: materials preserved.

### Enchanting System

Spellcasters can enchant weapons and armor:

- `enchant longsword attack 2` — Add +2 attack bonus (Spellcraft DC 25, costs 2000 gold)
- Bonus types: attack, damage, ac, stat
- Maximum +5 enhancement
- Requires spellcaster class

### Item Sets

Equipping matching items grants set bonuses:

- **Iron Warrior** (Longsword + Dagger + Shield): 2 pieces = +1 attack, 3 pieces = +2 AC, +1 damage
- **Leather Scout** (Armor + Boots + Gloves): 2 pieces = +20 movement, 3 pieces = +2 Hide/Sneak

---

## Mount, Companion & Summon Systems

| System | Command | How It Works |
|--------|---------|-------------|
| **Mount** | `mount <creature>` | Ride check DC 5, faster movement, mob removed from room |
| **Companion** | `companion call <mob>` | Handle Animal DC 15, companion follows and fights alongside |
| **Summon** | `summon` | Spellcaster: create level-scaled companion (HP=level x 4, costs spell slot) |
| **Familiar** | `familiar <type>` | Wizard/Sorcerer: permanent companion (cat, rat, hawk, owl, snake, toad) with passive bonuses |

---

## AI-Powered NPCs

Every NPC can hold a conversation:

```
> talk mira hello
Mira the Shopkeeper says: "Welcome, traveler! Looking to buy, sell,
or appraise? My wares are the best in town."

> talk guard what is this place?
Stone Golem says: "This is the Quadrant of the Lord of Stone.
Ancient beyond your years, mortal."
```

The dialogue system uses a three-tier approach:

1. **Scripted dialogue** — Authored responses from mob data (instant, zero cost)
2. **Template-based keyword matching** — 280+ keyword-triggered responses with role-based templates (shopkeeper, trainer, banker, blacksmith, guard, innkeeper). Fast, no API cost. Deterministic seeding per NPC ensures consistent personality.
3. **Local LLM** via Ollama or LM Studio — Rich roleplay conversations for complex interactions. Personality built from mob data (name, type, flags, alignment, description). Context-aware: NPCs know their location, the time of day, their schedule, and the player's level.

No cloud API required. No per-token costs. Runs entirely on local hardware.

### Combat AI

Mobs fight intelligently, not randomly:

- **Flee logic** — 30% chance to flee when below 20% HP (unless boss or no_flee flag)
- **Target selection** — Prefer current target, or switch to lowest-HP player
- **Special attacks** — 25% chance to use special_attacks from mob data
- **Combat maneuvers** — Mobs with relevant feats use Trip, Disarm, Grapple, Bull Rush, or Sunder (20% chance)
- **Decision tree** — Full CombatAction class evaluates options each round

### AI Chat Game — Deep NPC Conversations

Beyond the `talk` command, the `chat` command enters a full AI conversation mode:

```
> chat elia

  ~ You feel yourself drift...

  The Central Altar hums with quiet warmth. Guide Priestess Elia
  looks up from her work as you approach.

  Elia says: "Ah. Another traveler steps through. Welcome to Oreka.
  I am Elia — I will not keep you long, but there are things you
  should know before you venture out."

[Chat: Guide Priestess Elia] > What are the Elemental Lords?

  Guide Priestess Elia [reverent] says:
  "Four primordial beings shaped this world — Stone, Fire, Sea, and
  Wind. Their resonance flows through all Kin. You feel it now, in
  your Kin-sense. That warmth is them."

[Chat: Guide Priestess Elia] > endchat

  Guide Priestess Elia says: "Walk carefully, traveler. The world
  remembers those who pay attention to it."
  ~ You return from the dreamlight.
```

- **NPC personas** — Each NPC has authored personality: voice, motivation, secrets, knowledge domains, speech style, forbidden topics, and faction attitudes
- **NPC memory** — NPCs remember past conversations with each player across sessions
- **Lore integration** — 17 canon lore entries injected into AI context based on NPC expertise
- **World bleed** — Real-world events (other players speaking, combat, world events) inject into the conversation as `[~WORLD~]` messages
- **Game actions** — NPCs can modify reputation, grant quests, give items, and store memories during conversation
- **Shadow Presence** — Chatting players appear as dreaming presences visible to others, registering as "echo" resonance on Kin-sense
- **Materialize** — Type `enter world` to step out of the dreamlight into the NPC's room as a full player
- **RP Say** — `rpsay` broadcasts speech in the room and LLM-capable NPCs overhear and may chime in. Guards might comment on threats, shopkeepers on trade talk, priests on blessings. Responses arrive 1-3 seconds later with natural staggering if multiple NPCs react.
- **Model tiers** — Premium models for faction leaders and lore keepers, standard for merchants, fast for guards
- **Conversation summarization** — Long conversations auto-compress to stay within context limits
- **Session logging** — Complete conversation history saved for review

---

## NPC Schedules and Living World

NPCs don't stand in one spot. They follow schedules:

- **Game time** runs at 60:1 (1 real minute = 1 game hour)
- **NPCs move** between rooms based on time of day (shopkeeper opens at dawn, guards patrol at night)
- **Activity descriptions** change with their schedule ("Mira is arranging her wares" vs "Mira is closing up shop")
- **Ambient room echoes** — Forests rustle, caves drip, towns murmur, waves lap. Random atmospheric messages every 60 seconds.
- **12 months** with names: Deepwinter, Icemelt, Springseed, Rainmoon, Greengrass, Summertide, Highsun, Harvestend, Leaffall, Frostfall, Darknight, Yearsend
- **Day/night affects** room lighting, visibility, and NPC behavior
- **Dynamic weather engine** — Weather changes per region every ~5 minutes based on biome and season. 8 weather types (clear, rain, storm, heat, cold, snow, fog, wind). Per-region biome weights (desert favors heat, marshes favor rain, steppe favors wind). Players see atmospheric broadcasts when weather changes. Mechanical effects in combat: rain/wind -2/-4 ranged attacks, storm -4 ranged and +4 concentration DC, fog -4 Spot. `weather forecast` shows what's coming.

---

## Quest System

Quests support 10 objective types:

| Type | Example |
|------|---------|
| Kill | "Slay 5 wolves in the forest" |
| Collect | "Gather 3 healing herbs" |
| Deliver | "Bring this letter to the guard captain" |
| Escort | "Protect the merchant to Market Street" |
| Explore | "Visit the Quadrant of Fire" |
| Talk | "Speak with the sage about the prophecy" |
| Use | "Light the beacon at the tower" |
| Defend | "Hold the gate for 5 rounds" |
| Skill Check | "Pick the lock on the chest (DC 15)" |
| Choice | "Side with the merchants or the thieves" |

Quests track progress, support optional/hidden objectives, chain together, and award XP, gold, items, and reputation.

---

## Kin-Sense — Oreka's Signature Mechanic

Every living being in Oreka resonates with elemental energy. All Kin share a supernatural sixth sense — **not magic**, cannot be dispelled or suppressed by anti-magic — that detects nearby presences as distinct resonance patterns:

| Resonance | Feel | Who |
|-----------|------|-----|
| **Harmonic** | Warm presence, race and element readable | All Kin races (Elves, Dwarves, Humans, Halflings, Half-Giants) |
| **Wild Static** | Present, alive, fundamentally different | Tanuki, Oreka-native beasts |
| **Warm Static** | Faint background noise | Simple animals, insects, plants |
| **Breach Static** | Alien, unsettling wrongness | Goblins, Wargs, Hobgoblins, Orcs, Ogres |
| **Null** | A wound; absence that hurts | Silentborn, Severed, Oath-Broken |
| **Void** | Deliberate predatory wrongness | Domnathar, true Deceivers |
| **None** | Simply absent — undetectable | Undead, Constructs, Farborn |
| **Raw Static** | Overwhelming elemental force | Pure elementals |

- **Base range**: 60 feet (one room), passes through barriers up to 5 feet thick
- **Racial detection bonuses**: Half-Giant +4, Elves/Dwarves +2, Halfling +1, Humans +0, Farborn -99 (cannot use)
- **Room modifiers**: Dead zones (Glass Wastes), flickering zones (Lament of Kings), amplified zones (Windstones)
- **Suppression methods**: Deceiver's Feat, False Silence, worked Domnathar metal
- **Elemental feel**: Earth = "deep and steady", Fire = "warm and restless", Water = "cool and flowing", Wind = "bright and sharp"

This isn't flavor text — it's a detection system with mechanical consequences. Silentborn are invisible to Kin-sense. Farborn can't use it at all. Dead zones silence it entirely. Amplified zones make every presence ring clear.

---

## Religion — Pray, Worship, Ascend

### 13 Deities

**4 Elemental Lords** (primordial, never player-controlled):
Lord of Stone (comatose), Lady of Fire, Lady of the Sea, Youngest Brother (Wind/exiled)

**9 Ascended Gods** (were mortals, can be player-linked):
Dagdan the United Sun, Hareem the Golden Rose, Kaile'a, Cinvarin the Five Witnesses, Semyon, Apela Kelsoe, Ludus Galerius, Gonmareck Ritler, The Hand Unanswered

### Prayer System
- Pray at shrines for deity-specific buffs (healing, stat bonuses, resistances)
- Patron deity's shrine gives stronger effects
- Each deity grants different mechanical benefits

### Player Ascension
Admins can create new deities (`@deity create`) and link them to player accounts (`@deity link`). Player-gods get:
- `divine bless` — Bless nearby followers
- `divine smite` — Strike enemies
- `divine manifest` — Appear visibly at a shrine
- `divine speak` — Echo voice through all shrines worldwide
- `divine grant` — Bestow titles on followers

### Wandering Gods
Invisible deity entities roam between their shrines. Your patron deity is visible to you. Others sensed via Wisdom checks. Elemental Lords felt as environmental surges.

---

## Factions & Reputation

10 factions with a reputation system ranging from -500 (hostile) to +600 (allied):

| Faction | Type | Description |
|---------|------|-------------|
| Circle of Deeproot | Joinable | Druid order monitoring elemental health |
| Golden Roses | Joinable | Law enforcement, Harreem cult monitors |
| Far Riders | Joinable | Mytrone/Pasua cavalry brotherhood |
| Sand Wardens | Joinable | Desert pilgrim/patrol order |
| Trade Houses | Joinable | Mercantile guilds of Twin Rivers |
| The Unstrung | Secret | 600-year-old criminal organization |
| Silent Concord | Race-locked | Silentborn organization with 5 Choirs |
| Chainless Legion | Race-locked | Farborn veterans |
| Gatefall Remnant | Reputation only | Survivors at Tomb of Kings |
| Brotherhood of Steppe | Reputation only | Mytrone cultural alliance |

- Joinable factions have 5 ranks with auto-promotion on reputation thresholds
- NPC shop prices modified by faction standing
- Territory hostility detection — enter hostile territory and guards react
- Reputation gains/losses from quest completion and player actions

---

## Special Materials

12 material types — 6 standard D&D and 6 unique to Oreka:

| Material | Element | Special Properties |
|----------|---------|-------------------|
| **Embersteel** | Fire | +1d4 fire on crit, fire resist 5 |
| **Wind-silk** | Wind | Quarter weight, +5 movement, -15% spell failure |
| **Riverstone** | Water | +1 CL water/cold spells as focus |
| **Moonwhisper Silver** | Wind | Silver DR bypass, no damage penalty, +1d4 cold vs fey/undead |
| **Volcanic Glass** | Fire | Expanded crit range, fragile |
| **Giant-bone** | Earth | +1 CL earth/acid as focus, +1 bludgeon damage |

Plus standard D&D: Adamantine, Darkwood, Mithral, Cold Iron, Alchemical Silver, Dragonhide. Material pricing tables affect crafted item values.

---

## 83 Location Effects

The world reacts to characters mechanically through 5 types of room effects:

| Effect Type | Count | Examples |
|-------------|-------|---------|
| Kin-sense modifier | 14 | Dead zones (Glass Wastes), flickering (Lament of Kings), amplified (Windstones) |
| Elemental resonance | 10 | Fire at Kharazhad forges (+1 CL fire spells), water at river shrines |
| Environmental hazard | 5 | Desert heat (DC 12 CON), volcanic gas (DC 14 poison), mountain cold |
| Rune-circle | 12 | Teleport, heal, amplify, ward, weather — study/activate/repair with Craft checks |
| Sanctuary | 14 | Deity-linked shrines with healing bonuses, rest bonuses, XP modifiers, PvP restrictions |

---

## Player Housing, Mail & Auction

### Player Housing — Full System

4 house types with scaling cost, rooms, and storage:

| Type | Cost | Rooms | Storage | Description |
|------|------|-------|---------|-------------|
| Cottage | 5,000 gp | 2 | 20 | A cozy stone cottage |
| Townhouse | 15,000 gp | 4 | 50 | A comfortable two-story townhouse |
| Manor | 50,000 gp | 8 | 100 | An impressive manor house |
| Guild Hall | 100,000 gp | 12 | 200 | A great hall fit for a guild |

**Furniture with mechanical effects:**

| Furniture | Cost | Effect |
|-----------|------|--------|
| Comfortable Bed | 100 gp | +25% HP on rest at home |
| Storage Chest | 200 gp | +10 storage slots each |
| Crafting Workbench | 500 gp | +2 to Craft checks at home |
| Prayer Altar | 1,000 gp | Prayer effects last longer |
| Bookshelf | 250 gp | +2 to Knowledge checks |
| Herb Garden | 600 gp | Produces 1 healing herb per day |
| Trophy Case | 300 gp | Display achievements and rare items |
| Fireplace | 400 gp | Comfort and light |

| Command | Function |
|---------|----------|
| `house buy <type>` | Purchase a house |
| `house sell` | Sell for 50% refund |
| `house visit <player>` | Visit another player's home |
| `furnish list` | Browse available furniture |
| `furnish buy <item>` | Buy and place furniture |
| `storage list` | View stored items |
| `storage store <item>` | Store inventory item |
| `storage take <item>` | Retrieve stored item |
| `home` | Teleport to your house |

Housing effects are mechanically active — crafting at your workbench adds +2 to skill checks, resting with a bed heals 25% extra HP.

### Mail System
- `sendmail <player> <subject> = <body>` — Send mail (1 gold, requires mailbox)
- `mail` — Check inbox
- `readmail <#>` — Read a letter

### Auction House
- `auction sell <item> <price> [buyout]` — List for 7 days
- `auction list` — Browse listings
- `auction bid <#> <amount>` — Place bid (outbid refunds returned)
- `auction buyout <#>` — Instant purchase
- `auction collect` — Collect won items/gold

---

## Narrative & Story Progression

### Main Story Arc — The Silence Breach

A 6-chapter narrative tracks the world's central conflict — the growing Silence Breach in Gatefall Reach:

| Chapter | Trigger | Title Earned |
|---------|---------|-------------|
| The Awakening | Level 1 | — |
| Whispers of the Breach | Level 5 | — |
| Choosing Allegiances | Faction rep 100+ | — |
| The Elemental Trials | Level 10 | Elemental Aspirant |
| The Silence Deepens | Level 15 | Breach Warden |
| The Lords' Gambit | Level 20 | Champion of Oreka |

Chapters trigger automatically on level-up, room entry, mob kills, and faction reputation changes. Each delivers an ANSI-rendered cutscene with narrative text and rewards (XP, titles).

**Narrative hooks fire from real gameplay:**
- Enter Gatefall Reach and sense the Breach
- Kill creatures near the Silence and trigger story fragments
- Level up through the story's power thresholds
- Earn faction reputation and unlock allegiance chapters

### Lore System

17 canonical lore entries accessible via `lore <topic>`:
- Elemental Lords, Ascended Gods, Kin-Sense mechanics
- Aldenheim, EarthForge, House Buarath
- Regional histories (Twin Rivers, Infinite Desert, Deepwater Marches, Gatefall Reach, Kinsweave)
- Factions (Sand Wardens, Trade Houses, The Unstrung, Silent Concord)
- The Silence Breach and its spreading void

`story` shows your narrative progress. `story <chapter_id>` replays a completed chapter's cutscene.

---

## Metamagic System

Spellcasters with metamagic feats can modify their spells per D&D 3.5 rules:

| Metamagic | Feat Required | Slot Increase | Effect |
|-----------|--------------|---------------|--------|
| `metamagic empower <spell>` | Empower Spell | +2 levels | +50% variable numeric effects (damage/healing) |
| `metamagic maximize <spell>` | Maximize Spell | +3 levels | Maximize all variable effects |
| `metamagic quicken <spell>` | Quicken Spell | +4 levels | Cast as swift action |
| `metamagic extend <spell>` | Extend Spell | +1 level | Double spell duration |
| `metamagic silent <spell>` | Silent Spell | +1 level | No verbal component |
| `metamagic still <spell>` | Still Spell | +1 level | No somatic component |

Prepare metamagic, then cast — the spell uses a higher-level slot. `metamagic list` shows available options and which feats you have.

---

## Area Reset System

Rooms periodically reset to their default state:
- Items, doors, and containers restored on configurable timers
- Rooms with players in combat are skipped
- Players in affected rooms see a notification
- Admin controls: `@resets status`, `@resets force <area>`, `@resets interval <area> <seconds>`
- Default 15-minute reset cycle for tutorial areas

---

## Account Management

| Command | Function |
|---------|----------|
| `changepassword <old> <new>` | Change your password |
| `deletechar <password> CONFIRM` | Permanently delete character (safe rename, not true delete) |

---

## End-Game Content

### Remort System
At level 20, players can `remort`:
- Reset to level 1 with +1 to ALL ability scores permanently
- +10 max HP permanently
- Keep all skills, feats, equipment, gold, achievements
- Earn "Reborn" title
- Track remort count for prestige

### Achievements (9+)
| Achievement | Trigger | Title Earned |
|-------------|---------|-------------|
| First Blood | 1 kill | Blooded |
| Warrior | 10 kills | Warrior |
| Slayer | 100 kills | Slayer |
| Adventurer | Level 5 | Adventurer |
| Veteran | Level 10 | Veteran |
| Hero | Level 20 | Hero |
| Wealthy | 1000 gold | the Wealthy |
| Artisan | Craft 1 item | Artisan |
| Explorer | Visit 50 rooms | Explorer |

---

## The World of Oreka

### 1,624 Rooms Across 7 Regions

Oreka isn't a generic fantasy setting. It's a continent shaped by four Elemental Lords, divided by the Giant's Teeth mountain ranges and an equatorial desert corridor.

| Region | Location | Rooms | Character | Key Cities |
|--------|----------|-------|-----------|------------|
| **Twin Rivers** | Northwest | 338 | Densest population, river trade, canopy cities | Custos do Aeternos (25K), Liraveth (22K), Aerithal (15K) |
| **Kinsweave** | North-center | 167 | Highland quarries, haunted ruins, pilgrimage | Stonefall, Rivertop, Highridge + 6 ruins |
| **Tidebloom Reach** | Northeast | 225 | Tidal farming, Mithril Chains, lake trade | Branmill Cove, Velathenor, Tiravel + 4 ruins |
| **Infinite Desert** | Equatorial | 149 | Pilgrim roads, oasis cities, volcanic forges | Kharazhad (20K), Dunewell, Solhaven |
| **Eternal Steppe** | South-center | 161 | Horse breeding, cavalry, nomadic camps | Tavranek (6K) + 8 semi-permanent camps |
| **Gatefall Reach** | Southeast | 193 | Frontier, Silence Breach, Wind-Riders | Hillwatch, Silkenbough, Glimmerholt |
| **Deepwater Marches** | Southwest | 240 | Dense jungle, Warg settlements, intelligence trade | Titan's Rest (28K), Canopy Hold, Thornwall |

Plus: Chapel tutorial (25 rooms), Chainless Legion (80 rooms), ShadeharmonGlade (8 rooms), Wilderness Connectors (38 rooms).

### Original Cosmology

- **Four Elemental Lords** — The Lord of Stone (comatose), The Lady of Fire (active), The Lady of the Sea (active), The Youngest Brother/Wind Lord (exiled)
- **Nine Ascended Gods** — Mortals who achieved apotheosis after the Fall of Aldenheim
- **Elemental affinities** — Every Kin race aligns with a primal element (Fire, Water, Earth, Wind, or All-Element Concord for Half-Giants)
- **Kin-sense** — Supernatural awareness system unique to Oreka
- **373 placed mobs** — Guards, merchants, quest-givers, wandering beasts, and bosses
- **238 bestiary templates** — D&D 3.5 compatible creature library for expansion

### Starting Area

Room 1000 (Central Aetherial Altar) provides immediate access to:

- **Guildmaster Thorin** — Train skills and abilities
- **Banker Goldsworth** — Deposit and withdraw gold
- **Smith Ironforge** — Repair equipment
- **Merchant Lyssa** — Buy and sell gear (weapons, armor, tools, potions)
- **Mailbox** — Send and receive mail
- **Bulletin Board** — Community posts

The world is designed for expansion — rooms are JSON files, mobs are JSON entries, items are JSON records. Adding content requires no code changes.

---

## Builder Tools

Complete online creation (OLC) system for building the world without touching code:

| Command | Function |
|---------|----------|
| `@dig <dir> <name>` | Create new room with auto-linking |
| `@desc <text>` | Set room description |
| `@exit <dir> <vnum>` | Create/modify exits |
| `@setdoor <dir> <prop> <val>` | Set door properties (locked, hidden, key) |
| `@setroom <field> <val>` | Edit room flags, terrain, weather |
| `@setlight <level>` | Set room lighting |
| `@mobadd <vnum> <name>` | Create new mob template |
| `@mobedit <vnum> <field> <val>` | Edit mob properties |
| `@itemadd <vnum> <name>` | Create new item template |
| `@itemedit <vnum> <field> <val>` | Edit item properties |
| `@setmob <field> <val>` | Configure mob placement |
| `@setrespawn <vnum> <time>` | Configure respawn timing |
| `@sethelp <topic>` | Add/edit help entries |

Plus 20+ admin `@set*` commands for modifying player stats, equipment, spells, feats, and more.

### Bug Reporting

Players can submit feedback directly:
- `bug <description>` — Report a bug
- `typo <description>` — Report a typo
- `idea <description>` — Suggest a feature

All saved to `data/feedback.json` with timestamp, reporter, and room context.

---

## Veil Client — Play in Your Browser

OrekaMUD3 ships with the **Veil Client**, a built-in HTML/WebSocket client that runs in any modern browser:

- **No download required** — Open `veil_client.html` or connect to the WebSocket endpoint
- **WebSocket server** on port 8765 — Bidirectional proxy to the telnet game server
- **ANSI color rendering** — Full color support matching terminal MUD clients
- **GMCP integration** — Real-time character vitals, room info, quest state, and Kin-sense data pushed to the client
- **Keep-alive** — 30-second ping/pong heartbeat for stable connections
- **Dual transport** — Players on telnet and WebSocket play in the same world simultaneously

### GMCP Protocol Support

Full Generic MUD Communication Protocol implementation for rich client integration:

| GMCP Package | Data Sent |
|--------------|-----------|
| `Char.Vitals` | HP, AC, movement, gold, TNL, level |
| `Char.Status` | Conditions, spell slots per day, class, race |
| `Char.Factions` | All faction reputation values |
| `Char.Deity` | Patron deity, shrine status, active buffs |
| `Char.KinSense` | Elemental detections with range and room modifiers |
| `Char.Quest` | Active quests with state, completed quest list |
| `Room.Info` | Vnum, name, description, region, exits, effects, terrain |
| `Room.Mobs` | Living mobs with health state (unhurt/wounded/near death) |

Works with MudLet, TinTin++, Veil Client, and any GMCP-compatible client.

---

## Technical Details

| Spec | Value |
|------|-------|
| Language | Python 3.13 |
| Architecture | Async I/O (asyncio + telnetlib3) |
| Protocols | Telnet (port 4000) + WebSocket (port 8765) + GMCP |
| Client | Veil Client (built-in HTML/WebSocket), MudLet, TinTin++ |
| Data format | JSON (rooms, mobs, items, spells, quests, events) |
| Character persistence | Atomic JSON saves with timestamped backups |
| AI backend | Ollama / LM Studio (local, no cloud API) |
| Test suite | 298 automated tests (pytest) across 12 test files |
| Commands | 340+ registered commands |
| Source modules | 42 Python files + main.py |
| Codebase size | ~35,000+ lines |
| Dependencies | telnetlib3, websockets, ollama (optional) |

---

## By the Numbers

| System | Count |
|--------|-------|
| Lines of code | 35,000+ across 42 source modules |
| Registered commands | 340+ |
| World rooms | 1,624 across 13 areas |
| Placed mobs | 373 (276 hostile, 85 friendly, 5 tutorial) |
| Bestiary templates | 238 (D&D 3.5 compatible creature library) |
| Items | 88 |
| Races | 20 (15 playable + 5 creature races) |
| Classes | 12 (including custom Magi with 3 paths) |
| Feats | 88 (70 with mechanical effects) |
| Spells | 82 across 8 schools |
| Skills | 38+ with full ability mod mapping |
| Conditions | 37 with mechanical modifiers |
| Combat maneuvers | 10 + charge/defense stances |
| Class abilities | 13 unique commands |
| Crafting recipes | 60 across 7 disciplines |
| Special materials | 12 (6 standard D&D + 6 Oreka-exclusive) |
| Factions | 10 (5 joinable, 1 secret, 2 race-locked, 2 reputation-only) |
| Deities | 13 (4 Elemental Lords + 9 Ascended Gods) |
| Location effects | 83 active room effects (5 types) |
| Social verbs | 60 |
| Equipment slots | 14 |
| Cleric domains | 23+ |
| Help entries | 90+ |
| Achievements | 9+ |
| Chat channels | 10 (including RP Say with NPC AI reactions) |
| GMCP packages | 12 real-time data streams (8 game + 4 chat) |
| Metamagic types | 6 (Empower, Maximize, Quicken, Extend, Silent, Still) |
| Story chapters | 6 main arc + room/kill narrative fragments |
| House types | 4 (cottage, townhouse, manor, guild hall) |
| Furniture items | 8 with mechanical effects |
| Lore entries | 17 canonical world lore topics |
| Weather types | 8 dynamic per-region (clear, rain, storm, heat, cold, snow, fog, wind) |
| Automated tests | 298 across 12 test files |

---

## What's Ready Today

### Core Engine
- Full character creation (20 races with stat mods, 12 classes, 88 feats, 82 spells, 38 skills, 13 deities, 9 alignments)
- Complete D&D 3.5 combat (initiative, action economy, 10 maneuvers, dual wield, ranged, sneak attack, charge, defense stances, AoO on flee, concentration checks, spell resistance, damage reduction, weapon properties, size modifiers)
- 13 class abilities (Rage, Inspire, Turn Undead, Wild Shape, Flurry, Smite, Lay on Hands, Divine Grace, Favored Enemy, Evasion, Uncanny Dodge, Combat Style)
- Combat AI (flee logic, target selection, special attacks, maneuver usage)
- Equipment system (14 slots, AC recalculation, stat bonuses auto-applied, material durability, item repair)
- Corpse and loot system (CR-scaled drops, decay timers, auto-loot/auto-gold)

### World
- 1,624 rooms across 13 area files, 7 distinct regions with unique identity
- 373 placed mobs (276 hostile, 85 friendly NPCs, 5 tutorial)
- 238 bestiary creature templates (D&D 3.5 compatible, ready for placement)
- 88 items with 12 special material types (6 Oreka-exclusive)
- 83 active location effects (Kin-sense modifiers, elemental resonance, hazards, rune-circles, sanctuaries)
- 100% room connectivity verified by AI bot explorer
- 6 wilderness corridors connecting regions through mountain passes and desert roads

### Systems
- Spellcasting (prepared/spontaneous, components consumed, saves, SR, buffs, healing, AoE, dispel, 23+ domains)
- Crafting (60 recipes across 7 disciplines, skill checks, material consumption, Oreka-specific recipes)
- Enchanting (weapons/armor, +1 to +5, Spellcraft check)
- Religion (13 deities, prayer at shrines, patron buffs, player ascension to godhood, wandering deity entities)
- Factions (10 factions with reputation -500 to +600, 5 joinable with ranks, shop price modifiers, territory hostility)
- Kin-sense (unique sixth sense, 9 resonance categories, room modifiers, racial detection bonuses)
- Quest system (10 objective types, progress tracking, chain quests, rewards)
- Shop system (buy/sell/appraise with auto-restock) + bank + auction house
- Death/respawn (D&D dying rules, chapel respawn, XP penalty)
- Rest and recovery (long/short rest, inn bonus, spell slot restoration)

### Multiplayer & Social
- PvP combat + formal duel system (non-lethal)
- Party system (group, follow, assist, rescue, XP split)
- Guild/clan system (create, ranks, bank, MOTD)
- Chat system (say with language garbling, tell with AFK/ignore, whisper, reply, shout, OOC, newbie, emote, 60 socials)
- Mail, bulletin boards, auction house
- Leaderboards, finger/whois, language system

### AI & Dialogue
- Three-tier NPC dialogue (scripted, 280+ keyword templates, local LLM via Ollama/LM Studio)
- AI NPC personality system with role-based responses (shopkeeper, trainer, banker, blacksmith, guard, innkeeper)
- NPC schedules (day/night cycle, room movement, activity descriptions, ambient echoes)
- Combat AI with decision trees (flee, target switching, maneuvers, special attacks)

### Client Support
- Telnet on port 4000 (MudLet, TinTin++, any MUD client)
- WebSocket on port 8765 (Veil Client, custom integrations)
- GMCP protocol (12 data packages: vitals, status, factions, deity, kin-sense, quests, room info, mobs + 4 chat packages)
- Built-in Veil Client (HTML/WebSocket, plays in any browser, no download)
- Interactive world map viewer (HTML/Canvas, all 1,624 rooms visualized)

### Quality of Life
- Stealth (hide, sneak, search, spot opposition)
- Doors and traps (lock/unlock/pick, trap detection/disarm/trigger)
- Containers (put/get/peek with capacity)
- Mount, companion, summon, and familiar systems
- Player housing (4 types, 8 furniture items with mechanical bonuses, persistent storage)
- Achievements with title rewards (auto-granted on kill, level, craft, explore)
- Remort system at level 20
- Hunger/thirst with survival mode
- Light sources (torches/lanterns illuminate dark rooms)
- Fishing, mining, gathering (resource nodes by room flag)
- Gambling, encumbrance, body positions
- Speedwalk, aliases, custom prompts, config toggles
- Account management (password change, character deletion)
- 90+ help entries, bug/typo/idea reporting
- Mob respawn (configurable timers, boss/unique/quest flags)
- Area resets (configurable room/item/door restoration on timers)
- Event logging (player actions, combat, deaths, quests, economy)
- 340+ commands, 298 automated tests, complete builder/admin OLC toolset
- Character persistence with atomic saves and backup rollback

### Dynamic Systems
- Dynamic weather engine (8 types, per-region biome weights, seasonal modifiers, combat integration)
- Narrative engine (6-chapter story arc, room/kill/level/faction triggers, cutscene rendering)
- Area reset system (configurable timers, admin controls, combat-safe)
- Metamagic casting (6 types with D&D 3.5 slot-level rules)
- ANSI UI rendering library (progress bars, score cards, combat prompts)
- World event system (weather changes, mob surges, shrine bonuses via DM/MCP bridge)

## What It Needs

- **Quest content** — The quest system is fully built (10 objective types, chains, rewards). It needs authored quest chains filling the 1,624-room world.
- **More bestiary placement** — 238 creature templates in the bestiary library await room assignments across the regions.
- **Continued world polish** — The 7 regions are built and connected. Flavor text, hidden areas, and regional storylines deepen the experience.

The engine is complete. Every system is built, wired, and tested. The world is built. It needs stories to tell.

---

## Get Started

```bash
# Install dependencies
pip install telnetlib3 websockets

# Optional: Install Ollama for AI NPC dialogue
# https://ollama.ai

# Start the server
cd oreka_mud
python main.py

# Connect via telnet
telnet localhost 4000

# Or open the Veil Client in your browser
# veil_client.html (connects via WebSocket on port 8765)
```

Create a character. Kill something. Loot the corpse. Buy a sword. Cast a spell. Pray at a shrine. Join a faction. Craft an Embersteel blade. Talk to an NPC. Die and respawn. Group up with friends. Join a guild. Duel a rival. Enchant your weapon. Remort at level 20. It all works.
