# OREKA MONSTER MANUAL — ENTRY CONSTRUCTION GUIDE
## Complete Instructions for Building D&D 3.5e-Compatible Bestiary Entries

*This document captures all conventions, formulas, worldbuilding rules, and process developed across 104+ entries for the Oreka Monster Manual project. Use this as a reference when building new entries in any chat session.*

---

# PART 1: STAT BLOCK CONSTRUCTION

## The 24-Field Stat Block

Every entry uses these 24 fields in this exact order. Do not rearrange.

| # | Field | Description |
|---|---|---|
| 1 | **Creature Name** | Bold, large, top of entry |
| 2 | **Size/Type** | Including subtypes in parentheses |
| 3 | **Hit Dice** | Dice expression with average hp in parentheses |
| 4 | **Initiative** | Modifier (Dex mod + feats) |
| 5 | **Speed** | All movement modes with flight maneuverability |
| 6 | **Armor Class** | Full, touch, flat-footed with full modifier breakdown |
| 7 | **Base Attack/Grapple** | BAB from HD and type / Grapple modifier |
| 8 | **Attack** | Single best attack, full modifier and damage |
| 9 | **Full Attack** | All attacks available in a full-attack action |
| 10 | **Space/Reach** | Area occupied and striking distance |
| 11 | **Special Attacks** | Named offensive abilities |
| 12 | **Special Qualities** | Passive/defensive abilities (include elemental resonance here) |
| 13 | **Saves** | Fort/Ref/Will with modifiers |
| 14 | **Abilities** | All six: Str, Dex, Con, Int, Wis, Cha |
| 15 | **Skills** | With total modifiers |
| 16 | **Feats** | Listed by name |
| 17 | **Elemental Affinity** | Associated Elemental Lord(s) or None — OREKA-SPECIFIC |
| 18 | **Environment** | Habitat with Oreka region names and landmarks |
| 19 | **Organization** | How many appear together |
| 20 | **Challenge Rating** | Difficulty for a standard 4-person party |
| 21 | **Treasure** | Standard, double standard, none, etc. |
| 22 | **Alignment** | Usual alignment |
| 23 | **Advancement** | HD ranges for larger versions |
| 24 | **Level Adjustment** | For playable creatures, or — |

---

## CR Benchmark Table

Use this table to validate that a creature's stats land within the expected range for its Challenge Rating. The CR is typically assigned first (based on the creature's role, mythological weight, and intended encounter tier), then stats are built to fit.

| CR | HP | AC | Atk Bonus | Dmg/Round | Good Save | Poor Save |
|---|---|---|---|---|---|---|
| 1/4 | 4–8 | 11–13 | +0 to +2 | 2–4 | 1–3 | 0 |
| 1/2 | 6–12 | 12–14 | +1 to +3 | 3–6 | 2–3 | 0–1 |
| 1 | 10–20 | 13–15 | +2 to +4 | 5–8 | 3–4 | 0–1 |
| 2 | 18–30 | 14–16 | +3 to +6 | 7–12 | 4–5 | 1–2 |
| 3 | 25–40 | 15–17 | +5 to +7 | 10–15 | 5–6 | 1–2 |
| 4 | 32–50 | 16–18 | +6 to +9 | 12–18 | 5–7 | 2–3 |
| 5 | 40–65 | 17–19 | +8 to +10 | 15–25 | 6–8 | 2–3 |
| 6 | 50–75 | 18–20 | +9 to +12 | 18–28 | 7–8 | 3–4 |
| 7 | 60–90 | 19–21 | +10 to +13 | 20–35 | 7–9 | 3–5 |
| 8 | 70–105 | 20–22 | +12 to +15 | 25–40 | 8–10 | 3–5 |
| 9 | 85–120 | 21–23 | +13 to +16 | 28–45 | 8–11 | 4–6 |
| 10 | 100–135 | 22–25 | +14 to +17 | 30–50 | 9–12 | 4–6 |
| 11 | 115–155 | 23–26 | +15 to +19 | 35–55 | 10–13 | 5–7 |
| 12 | 130–170 | 25–27 | +17 to +20 | 40–60 | 11–14 | 5–7 |
| 13 | 150–185 | 27–29 | +18 to +22 | 45–65 | 12–15 | 6–8 |
| 14 | 165–200 | 28–30 | +20 to +23 | 50–70 | 13–16 | 6–8 |
| 15 | 185–225 | 29–32 | +22 to +25 | 55–80 | 14–17 | 7–9 |
| 16 | 200–250 | 30–33 | +23 to +26 | 60–85 | 15–17 | 7–9 |
| 17 | 225–275 | 31–34 | +24 to +27 | 65–95 | 15–18 | 8–10 |
| 18 | 250–300 | 32–35 | +26 to +28 | 70–100 | 16–19 | 8–10 |
| 19 | 275–325 | 33–36 | +27 to +29 | 75–110 | 17–19 | 9–11 |
| 20 | 300–370 | 34–38 | +28 to +31 | 80–120 | 17–20 | 9–12 |

### CR Adjustment Principles

**Special abilities push effective CR up.** A creature with strong specials (save-or-die, flight, DR, SR, spell-like abilities, area effects) should have slightly lower raw combat numbers to compensate. Conversely, a "bag of hit points" with no specials can have higher raw stats for its CR.

**Rough adjustments:**
- Flight + ranged attack: +0 to +1 effective CR
- DR 5/something: +0 (minor); DR 10/something: +1
- SR 15+: +0.5 to +1 depending on CL
- Save-or-suck ability (paralysis, petrification, charm): +1 to +2 depending on save DC and effect severity
- Multiple save-or-suck abilities: +2 to +3
- Regeneration: +0.5 to +1
- At-will spell-like abilities: varies, judge by the strongest effect
- Area damage (breath weapon, burst): +1 if usable frequently

**The process:** Pick CR from roster → build HD and abilities to produce HP/AC/Atk in the benchmark range → add special abilities → check if specials push the effective CR above target → adjust raw stats down if needed.

---

## Creature Type Rules

### Hit Die by Type

| Type | HD | BAB | Good Saves | Skill Pts/HD |
|---|---|---|---|---|
| Aberration | d8 | 3/4 | Will | 2 |
| Animal | d8 | 3/4 | Fort, Ref | 2 |
| Construct | d10 | 3/4 | None | 2 |
| Dragon | d12 | Full | Fort, Ref, Will | 6 |
| Elemental | d8 | 3/4 | Ref (varies) | 2 |
| Fey | d6 | 1/2 | Ref, Will | 6 |
| Giant | d8 | 3/4 | Fort | 2 |
| Humanoid | d8 | 3/4 | Varies (usually Ref) | 2 |
| Magical Beast | d10 | Full | Fort, Ref | 2 |
| Monstrous Humanoid | d8 | Full | Ref, Will | 2 |
| Ooze | d10 | 3/4 | None | 2 |
| Outsider | d8 | Full | Fort, Ref, Will | 8 |
| Plant | d8 | 3/4 | Fort | 2 |
| Undead | d12 | 1/2 | Will | 4 |
| Vermin | d8 | 3/4 | Fort | 2 |

### Key Formulas

**BAB:**
- Full: = HD
- 3/4: = floor(HD × 3/4)
- 1/2: = floor(HD / 2)

**Saves:**
- Good: 2 + floor(HD / 2)
- Poor: floor(HD / 3)

**HP:** HD × ((die size + 1) / 2) + (HD × Con modifier)

**Feats:** 1 + floor((HD - 1) / 3) — i.e., one at 1st HD, then one more at 3rd, 6th, 9th, etc.

**Grapple:** BAB + Str mod + size mod (Fine –16, Diminutive –12, Tiny –8, Small –4, Medium +0, Large +4, Huge +8, Gargantuan +12, Colossal +16)

**AC size modifier:** Fine +8, Diminutive +4, Tiny +2, Small +1, Medium +0, Large –1, Huge –2, Gargantuan –4, Colossal –8

### Space/Reach by Size

| Size | Space | Reach (Tall) | Reach (Long) |
|---|---|---|---|
| Tiny | 2½ ft. | 0 ft. | 0 ft. |
| Small | 5 ft. | 5 ft. | 5 ft. |
| Medium | 5 ft. | 5 ft. | 5 ft. |
| Large | 10 ft. | 10 ft. | 5 ft. |
| Huge | 15 ft. | 15 ft. | 10 ft. |
| Gargantuan | 20 ft. | 20 ft. | 15 ft. |
| Colossal | 30 ft. | 30 ft. | 20 ft. |

---

# PART 2: THE FIVE DESCRIPTIVE SECTIONS

After the stat block, every entry includes these five sections in this order.

## 1. Flavor Paragraph

**Convention developed:** Rather than the format guide's 2–4 sentence field-guide description, entries use a longer second-person vignette (1–2 paragraphs) that puts the reader IN the encounter. Present tense. Establishes visual appearance, threat level, and atmosphere.

**Example pattern:** "The [setting detail]. [What you see/hear/sense]. [The creature, described viscerally]. [One line that captures the creature's essential nature or the emotional response it provokes]."

## 2. Combat

How the creature fights. Must be specific enough that a DM can run the creature without improvising. Include:
- Preferred opening tactic
- Primary attack strategy
- Group behavior (if applicable)
- Retreat conditions
- Terrain preferences and how they affect tactics

## 3. Special Abilities

Every named Special Attack and Special Quality gets a full sub-entry. Format:

**Ability Name (Type):** Full mechanical description. Include range, area, duration, save type and DC, damage, and conditions. "The save DC is [Ability]-based."

- **(Ex) Extraordinary:** Non-magical, always active, not subject to SR or antimagic
- **(Su) Supernatural:** Magical but not spell-like, not subject to SR, suppressed in antimagic
- **(Sp) Spell-Like:** Functions like a spell, subject to SR and antimagic

**CRITICAL:** Kin-Sense Signature / Elemental Resonance is always described here using sensory language. This is the Oreka-specific element that makes every entry unique.

## 4. Society (called "History" in the format guide)

Cultural and historical context. Requirements:
- At least two Kin cultures named and their relationship to the creature described
- Specific Oreka locations, not generic terrain
- Connection to at least one major Oreka event or cultural tradition
- Practical details: how do Kin deal with this creature day-to-day?

## 5. Lore (Knowledge Checks)

Three tiers using the appropriate Knowledge skill:

| Creature Type | Knowledge Skill |
|---|---|
| Constructs, Dragons, Magical Beasts | Knowledge (arcana) |
| Aberrations, Oozes | Knowledge (dungeoneering) |
| Humanoids, sapient Non-Kin | Knowledge (local) |
| Animals, Fey, Giants, Monstrous Humanoids, Plants, Vermin | Knowledge (nature) |
| Undead | Knowledge (religion) |
| Elementals, Outsiders, Extraplanar | Knowledge (the planes) |

**DC tiers:**
- **DC 10 + CR:** Creature type, basic description, one key ability
- **DC 15 + CR:** Full abilities, vulnerabilities, behavioral patterns
- **DC 20 + CR:** Oreka-specific lore, cultural significance, Kin-sense details

---

# PART 3: OREKA WORLDBUILDING RULES

## The Elemental Framework

Oreka has four Elemental Lords:
- **Lord of Stone** (Earth)
- **Lady of Fire** (Fire)
- **Lady of the Sea** (Water)
- **Youngest Brother / Wind Lord** (Air)

Most creatures have an elemental affinity — one or two Lords whose domain they embody. Some have all four (Giant remnants). Some have none (Dómnathar, alien/breach creatures, non-Kin peoples).

### Dual Affinities

Many creatures have dual-element affinities. Describe what the intersection means:
- Fire/Earth = volcanic, forge-related, deep heat
- Water/Air = storm, waterfall, mist
- Earth/Water = marsh, river-bottom, growing things, root-water
- Fire/Air = lightning, desert wind, combustion
- Earth/Air = mountain wind, dust, erosion
- Fire/Water = steam, hot springs (rare)

### Primordial Creatures

Some creatures predate the separation of elemental domains. Their affinity is described as "primordial" — raw, undivided elemental force. Examples: Grootslang (Fire/Earth primordial), Huallallo (Fire/Earth primordial), Indrik (Fire/Earth ancient).

## Kin-Sense Categories

Every creature registers differently on Kin-sense. Use these categories:

| Category | Resonance Description |
|---|---|
| **Normal Kin** | Warm, distinct, identifiable by element |
| **Elemental Spirits** | Intense version of their element, overwhelming at close range |
| **Non-Kin (Wargs, Goblins)** | Wild static — present but unreadable, like a radio between stations |
| **Dómnathar** | Absolute void — absence where a living being should register; OR "False Silence" — artificially generated dead zone |
| **Undead (Oreka-native)** | Distorted, agonizing versions of original Kin-sense signature |
| **Giant Remnants** | All four elements in harmony — overwhelmingly powerful |
| **Alien/Breach** | No reading, or a reading that feels fundamentally wrong |
| **Fey** | Detectable but with a specific fey "flavor" — often mutable, playful, or unsettling |
| **Corrupted** | Recognizable elemental signature but twisted — warmth gone predatory, water gone stagnant |

**Always describe resonance using sensory language** — what does it feel like, sound like, taste like? Give a detection DC where appropriate. Describe how specific Kin cultures perceive it.

## The Kin Peoples

### The Seven Kin Cultures

| Culture | Race | Region | Specialty |
|---|---|---|---|
| **Vestri** | Dwarves | Giant's Teeth mountains | Mining, engineering, Stoneguard military |
| **Rarozhki** | Dwarves | Scorchspires | Volcanic smithing, fire-craft |
| **Pekakarlik** | Dwarves | Desert/coast | Trade caravans, ruin exploration, sea-falls |
| **Orean** | Humans | Giant's Teeth foothills | Farming, herding, volcano mythology |
| **Eruskan** | Humans | Great River cities | River-trade, bard traditions, urban culture |
| **Mytroan** | Humans | Eternal Steppe | Mounted nomads, steppe-riders |
| **Hasura** | Elves | Great Forests (canopy) | Canopy-dwelling, Dómnathar border defense |
| **Pasua** | Elves | Great Forests (ground) | Forest-floor scouts, rangers |
| **Kovaka** | Elves | Coastal/island forests | Sustainable forestry, seafaring |
| **Na'wasua** | Elves | Apelian Sea | Sea-elves, deep-water diving, ocean trade |
| **Taraf-Imro** | Humans | Southern mountains | Warriors, volcanic regions, distinct culture |

### Non-Kin Peoples

| People | Type | Notes |
|---|---|---|
| **Wargs** | Intelligent wolves | Harmony (species-specific awareness), deep steppe, pack culture |
| **Goblins** | Goblinoids | Wild static on Kin-sense, "chattering" (–2 detection penalty), free and Dómnathar-aligned populations, Warg-goblin symbiosis |
| **Tanuki** | Shapeshifting raccoon-dogs | Trickster-folk, communal, joyful, maintain groves |

### The Dómnathar (Deceivers)

Extraplanar creatures with eleven Great Houses tied to Abyss Circle patrons. They:
- Register as void/absence on Kin-sense
- Generate "False Silence" fields that suppress all Kin-sense in an area
- Operate through underground tunnel networks
- Created the Brutes (see below) as war-weapons
- Are the primary antagonist faction of Oreka

### The Brutes (NOT Giants)

Dómnathar-manufactured war-creatures that LOOK like giants but are artificial. All are feral — no longer under Dómnathar control. Only Hrokk reproduce reliably.

| Brute Name | Based On | CR | Notes |
|---|---|---|---|
| **Hrokk** | Ettin | 6 | Most common, self-sustaining, two-headed |
| **Goreham** | Hill Giant | 7 | Damage-absorber, dumb, most encountered near settlements |
| **Maero** | ??? | 6-7 | In Kovaka territory — still a Brute |
| **Charjaw** | Fire Giant | 10 | Fire-adapted |
| **Fogwrack** | Cloud Giant | 11 | Mountain summits, mockery of Giant grace |
| **Frost Giant** | Frost Giant | 9 | Needs a name still — not yet reached in alphabet |

**Key Brute traits:**
- Hollow Resonance on Kin-sense — artificial earth-attunement, recognizably fake
- "Dómnathar-Forged" special quality
- No new production — all existing Brutes are War-era remnants or their degraded offspring
- Population declining except Hrokk

## Key Oreka Locations

| Location | Description |
|---|---|
| **Giant's Teeth** | Major mountain range, former Giant homeland, Vestri mines |
| **Scorchspires** | Volcanic mountain range, Rarozhki territory |
| **Infinite Desert / Glass Wastes** | Giant ruins, sphinx territory, Pekakarlik caravans |
| **Great River** | Major waterway, Eruskan cities, lasa/fossegrim/etc. |
| **Eternal Steppe** | Open grassland, Mytroan riders, Warg packs |
| **Great Forests** | Multiple sub-regions: Hasura canopy, Pasua ground-level, Kovaka coast |
| **Deepwater Marches** | Halfling wetlands, fishing communities |
| **Tidebloom Reach** | Marshes, halfling territory |
| **Gatefall Reach** | Chain of waterfalls in Hasura territory |
| **Apelian Sea** | Major ocean, Na'wasua territory, kraken, deep-water creatures |
| **Kailian Sea** | Inland sea, Leviathan territory |
| **Kinsweave** | Border region, Dómnathar activity zone |

## Paragons

Paragons are exceptional immortal spirits chosen by the world itself to represent each animal subspecies. They are the "perfect version" of their kind. Reference Paragons in entries for natural animals when relevant, but they are separate from the standard bestiary entries.

## The Harmony

The animal equivalent of Kin-sense — species-specific awareness among animals. Wargs have it. Centaurs' horses have it. Reference it when describing how animals detect or react to creatures.

## The Lost Third

A mysterious faction located in Southwest Oreka and Gatefall Reach. Reference sparingly — this is an unfolding mystery in the setting.

---

# PART 4: ENTRY WRITING CONVENTIONS

## Flavor Paragraph Style

The project has evolved to use extended second-person vignettes rather than brief field-guide descriptions. The vignette puts the reader in an encounter scene. Pattern:

1. Set the scene (location, conditions)
2. Introduce the creature through sensory detail
3. Establish the threat or emotional response
4. One line that captures the creature's essential nature

**Length:** 1-2 paragraphs, roughly 80-150 words.

**Voice:** Second person present tense. "You see," "the air tastes of," "something is watching."

## Society Section Style

This is where the Oreka worldbuilding lives. Conventions:

- **Name specific Kin cultures** and describe their specific relationship (not generic "people fear it")
- **Include practical details** — how do communities actually deal with this creature? (Warning systems, counter-measures, seasonal patterns, trade goods, religious practices)
- **Population estimates** where appropriate ("fewer than a dozen," "perhaps sixty to eighty")
- **Inter-species relationships** — how does this creature relate to other creatures in the bestiary?
- **Unique cultural details** — named rituals, specific folk-wisdom, practical survival advice that Kin cultures have developed

## Lore Section Style

Three tiers, each building on the last:
- **Tier 1** (DC 10+CR): What a typical adventurer would know — type, basic appearance, one key danger
- **Tier 2** (DC 15+CR): What a knowledgeable person would know — full abilities, weaknesses, behavioral patterns, cultural countermeasures
- **Tier 3** (DC 20+CR): Expert knowledge — Oreka-specific lore, Kin-sense details, deep cultural significance, historical context

## Elemental Affinity Field Style

Don't just list the Lord(s). Add a brief evocative phrase:
- "Lord of Stone (Earth) / Lady of the Sea (Water) — the living forest; root-water and dark soil"
- "Youngest Brother (Air) — corrupted; the wind made cruel"
- "Lady of Fire (Fire) / Lord of Stone (Earth) — primordial; from an age when fire and earth were not yet separate"
- "None — the karakoncolos exists in the gap between elemental signatures"

## Environment Field Style

Don't use generic terrain. Use specific Oreka locations with parenthetical detail:
- "Giant's Teeth Deep Shafts (the deepest mine-shafts and natural fissures — below Vestri mining depth)"
- "Apelian Shoals (the shallow coastal waters, tidal pools, and estuaries — particularly the Pekakarlik and Na'wasua coast)"
- "Kin-Sense Dead Zones (areas where elemental resonance has been drained — typically near Dómnathar surface-breach points)"

---

# PART 5: QUALITY CHECKLIST

Before finalizing any entry, verify:

- [ ] All 24 stat block fields present and in correct order
- [ ] Hit Dice use correct die type for creature type
- [ ] AC breakdown shows all modifiers and math adds up
- [ ] HP, AC, Atk, Damage fall within CR benchmark ranges
- [ ] Special abilities don't push effective CR above target (or raw stats adjusted down to compensate)
- [ ] Elemental Affinity identified with evocative phrase (or "None" with explanation)
- [ ] Save DCs stated with basis ability identified
- [ ] Flavor paragraph is second-person vignette, vivid and atmospheric
- [ ] Combat section specific enough for a DM to run without improvising
- [ ] Every Special Attack and Special Quality has full description with (Ex/Su/Sp) type
- [ ] Elemental Resonance / Kin-Sense described with sensory language and detection DC
- [ ] Society section names at least two Kin cultures with specific relationships
- [ ] Environment uses specific Oreka locations
- [ ] Lore provides three Knowledge check tiers at correct DCs
- [ ] Entry connects to at least one Oreka cultural tradition or historical event
- [ ] Feats count matches HD (1 + floor((HD-1)/3))
- [ ] BAB calculated correctly for creature type
- [ ] Saves calculated correctly (good vs. poor) plus ability modifiers

---

# PART 6: COMMON PATTERNS

## OGL Creatures (adapted from 3.5e SRD)

Start with the official SRD stat block. Keep the core mechanics. Add:
- Elemental Affinity (field 17)
- Oreka-specific Environment (field 18)
- Elemental Resonance as a Special Quality
- Society section connecting to Kin cultures
- Lore section with Knowledge check tiers

## Mythological Creatures (adapted from real-world myth)

Design from scratch using the myth as inspiration. The myth provides the concept; Oreka provides the context. Key questions:
- Which Kin culture is this creature most associated with?
- What elemental affinity fits its nature?
- How does it register on Kin-sense?
- What ecological/cultural niche does it fill?
- How do Kin communities actually deal with it?

## Brute Entries

All Brutes share these traits:
- **Type:** Giant (always)
- **Elemental Affinity:** "None — artificial earth-attunement, cosmetic only"
- **Special Quality: Dómnathar-Forged (Su)** — description of the Brute's manufactured origin, original purpose, current feral state, and declining population
- **Special Quality: Hollow Resonance (Su)** — description of the artificial Kin-sense signature, always recognizably fake but in a way specific to this Brute type
- **Society:** No true society — feral. Describe which Kin communities deal with them and how, military response protocols, and the Brute's relationship to other Brute types

## Fey Entries

Fey in Oreka tend to:
- Have damage reduction X/cold iron
- Have elemental resonance that feels distinctly "fey" — mutable, playful, or uncanny
- Be connected to specific natural features (a river, a tree, a waterfall)
- Have relationships with Kin cultures that are complicated — not purely hostile or friendly
- Have spell-like abilities rather than raw combat power

## Aquatic Entries

Aquatic creatures need:
- Swim speed
- Amphibious or water-dependent noted
- Consider how Na'wasua sea-elves interact with them
- Consider Pekakarlik coastal communities
- Consider Eruskan river-trade
- Consider halfling fishing communities (Deepwater Marches, Tidebloom)

---

*Document version: February 2026. Reflects conventions established across Batches 1–9c (104 entries). Update as new patterns emerge.*
