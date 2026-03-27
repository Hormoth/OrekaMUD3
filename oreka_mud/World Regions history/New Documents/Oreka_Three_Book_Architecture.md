# OREKA: ECHOES OF THE ELEMENTAL DAWN
## Three-Book Publication Architecture
### Complete File Organization, Table of Contents & Content Gap Analysis

**Prepared from:** All project files as of March 2026  
**Canon Reference:** Canon Bible v2.81  
**Scope:** 251 creatures · 7 regional guides · 4,278-line races compendium · 1,642-line Canon Bible · 15,618-line bestiary

---

## ORGANIZATIONAL PRINCIPLES

### The Three-Layer Rule
Every piece of content in Oreka belongs to one of three audiences:

| Audience | Book | Rule |
|---|---|---|
| Players only | Races of Oreka (Book 2) | No DM secrets. No hidden lore. No mechanical spoilers. |
| DM only | Dungeon Master's Guide (Book 3) | Full truth. Plots. Hidden status of Elemental Lords. |
| Both | Split: player version in Book 2, DM version in Book 3 | Always clearly labeled at the content level. |

The Monster Manual (Book 1) is the exception — it is DM-facing by default, but the Introduction, Paragon lore, and Kin-Sense entries that explain creature behavior are player-safe flavor.

### Source File Classification
| File | Primary Destination | Notes |
|---|---|---|
| `Oreka_Canon_Bible_v2_81.docx` | Split across all three | Master reference; individual sections go to different books |
| `MonsterEntries_v4.docx` | Book 1 | The core A-Z bestiary (15,618 lines) |
| `Oreka_Batch1` through `Batch19` (38 files) | Book 1 | Individual batch entries — these are the same content as MonsterEntries_v4 organized differently; reconcile before final print |
| `Monstermanuallayout.docx` | Book 1 Front Matter | Existing TOC with 251-creature roster |
| `Oreka_Monster_Manual_Introduction__1_.docx` | Book 1 Front Matter | Introduction, Paragons, Natural Animals/Magical Beasts |
| `Oreka_Monster_Manual_Introduction__2_.docx` | Book 1 Front Matter | Second draft / extended version of same introduction |
| `Oreka_Bestiary_Master_Roster.docx` | Book 1 Appendix | Indexed roster, CR list, source key |
| `Domnathar_Bestiary.docx` | Book 1 Chapter (Dómnathar section) | Buarath Mutate Family + all House creatures |
| `The_Duty_Bound_Creature_Template.docx` | Book 1 Templates Chapter | Acquired template for Kin |
| `The_Flesh_Forged_Creature_Template.docx` | Book 1 Templates Chapter | Acquired template for humanoids |
| `Oreka_Monster_Entry_Construction_Guide.md` | Book 1 Appendix (internal) | DM reference/authoring guide; publish as appendix |
| `Races_of_Oreka_Complete_Compendium__1_.pdf` | Book 2 (primary) + Book 3 (DM sections) | Chapter 1 races fully written; Chapters 2-7 partially placeholder |
| `Cleric_Domain_Spell_List_Clean.docx` | Book 2 + Book 3 | Spell reference; player domains in Races book, full list in DMG |
| `Oreka_Base_ClassesNew.pdf` | Book 2 | Base classes adapted for Oreka |
| `Oreka_Glossary.docx` | All three books (split by book) | Full glossary; each book gets its relevant terms |
| `Oreka_Pronunciation_Master__1_.docx` | All three books (split) | Each book gets its own section of this master list |
| `Gatefall_Reach_Regional_Guide_v3.docx` | Book 3 (primary) + Book 2 (player extract) | Full DM guide; player-facing geography sections go into Book 2 |
| `EternalSteppe_v4.docx` | Book 3 (primary) + Book 2 (player extract) | Same split |
| `DeepwaterMarches_v4.docx` | Book 3 (primary) + Book 2 (player extract) | Same split |
| `InfiniteDesert_v4.docx` | Book 3 (primary) + Book 2 (player extract) | Same split |
| `Tidebloom_v4.docx` | Book 3 (primary) + Book 2 (player extract) | Same split |
| `Kinsweave_v4.docx` | Book 3 (primary) + Book 2 (player extract) | Same split |
| `TwinRivers_Regional_Guide_v3__1_.docx` | Book 3 (primary) + Book 2 (player extract) | Same split |
| `Canon_Bible_Player_DM_Audit_v1.md` | Internal reference only | Governs all splitting decisions; do not publish |
| `Regional_Guides_Player_DM_Audit_v1.md` | Internal reference only | Same |
| `Oreka_Canon_Bible_v2_2.docx` | Superseded | Earlier version; reconcile differences with v2.81 before discarding |

---
---

# BOOK 1: OREKA MONSTER MANUAL

**Subtitle:** *Creatures of the Elemental Dawn*  
**Audience:** Dungeon Masters primarily; Introduction and Paragon sections are player-safe flavor  
**Total Creatures:** 251 (4 Oreka Original · 108 Mythological · 139 OGL 3.5e)

---

## TABLE OF CONTENTS — BOOK 1

### FRONT MATTER
- Title Page / Legal Page (OGL v1.0a declaration)
- Foreword: *The World That Made These Things*
- Introduction: *From Harmony, Danger* [SOURCE: `Oreka_Monster_Manual_Introduction__2_.docx`]
  - Natural Animals
  - Magical Beasts
  - Paragons and the Harmonic Cycle
  - On Monsters and the World That Made Them
- How to Read an Entry: Stat Block Breakdown [SOURCE: `Oreka_Monster_Entry_Construction_Guide.md` §Part 1, reformatted for readers]
- Creature Types and Subtypes in Oreka [SOURCE: Canon Bible §9 "Creature Categories"]
- Kin-Sense and the Harmony: What It Means for Encounters [SOURCE: Canon Bible §3, condensed for DMs]
- Elemental Affinity at a Glance [SOURCE: Canon Bible §2, condensed]

---

### CHAPTER 1: MONSTER FEATS AND SPELLS
[SOURCE: `Monstermanuallayout.docx` Chapter 1 listing; mechanics to be drawn from `Races_of_Oreka_Complete_Compendium.pdf` elemental feat section and Canon Bible §2]

- Monster Feats
  - Core Combat Feats (10 feats)
  - Elemental Affinity Feats (4 feats — one per element)
- Dómnathar Signature Spells (6 spells)
  - *Design note: These spells should appear here AND in Book 3's Dómnathar chapter for DM reference*

**⚠ MISSING CONTENT — CHAPTER 1:**
- Full text of the 10 core monster feats has not been written. The TOC names them but the entries do not exist in any provided file.
- Full text of the 4 Elemental Affinity feats exists as player feats in `Races_of_Oreka_Complete_Compendium.pdf` but must be adapted for monster use.
- Full text of the 6 Dómnathar Signature Spells does not appear in any file. The Canon Bible names their existence; the actual spell stat blocks are missing.
- **Gap type:** Mechanical content. Requires writing 10 feat entries, 4 feat adaptations, and 6 spell stat blocks in D&D 3.5e format.

---

### CHAPTER 2: MONSTERS A TO Z
[SOURCE: `MonsterEntries_v4.docx` — primary source, 15,618 lines; `Oreka_Batch1` through `Batch19` — batch drafts of same content]

**RECONCILIATION NOTE:** `MonsterEntries_v4.docx` and the Batch files appear to contain the same entries developed at different stages. Before final layout, these must be reconciled: use the most recent, complete version of each entry. The Batch files may contain entries not yet incorporated into MonsterEntries_v4; audit both sources per creature.

#### A (16 entries)
Abatwa · Aboleth · Adze · Air Elemental · Al Karisi · Albaharï · Allip · Almas · Amaru · Amphisbaena · Androsphinx · Ankheg · Annis Hag · Aranea · Asanbosam · Assassin Vine  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch1_Abatwa_to_Aranea.md`; `Oreka_Batch3_AlKarisi_to_AssassinVine.md`]

#### B (15 entries)
Bahamut (Myth) · Bakeneko · Banshee · Basilisk · Behir · Black Dragon · Black Pudding · Blink Dog · Blue Dragon · Bodak · Brass Dragon · Bronze Dragon · Bugbear · Bulette · Bunyip  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch2a_Bakeneko_to_BlinkDog.md`; `Oreka_Batch2b_Bodak_to_Bunyip.md`]

#### C (15 entries)
Cadı Kuşu · Ccoa · Centaur · Changeling · Charun · Cherufe · Chimera · Chuul · Cloaker · Cloud Giant · Cockatrice · Copper Dragon · Criosphinx · Cù Sìth · Culsans  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch4a_CadiKusu_to_Cherufe.md`; `Oreka_Batch4b_Chimera_to_Criosphinx.md`; `Oreka_Batch4c_CuSith_and_Culsans.md`]

#### D (19 entries)
Darkmantle · Delver · Derro · Dire Ape · Dire Bear · Dire Boar · Dire Lion · Dire Tiger · Dire Wolf · Domovoi · Doppelganger · Dragon Turtle · Dragonne · Draugr · Dread Wraith · Dryad · Dullahan · Dust Mephit · Dybbuk  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch5a_Darkmantle_to_DragonTurtle.md`; `Oreka_Batch5b_Dragonne_to_DustMephit.md`; `Oreka_Batch5c_Dybbuk_and_DireAnimals.md`]

#### E (6 entries)
Each-Uisge · Earth Elemental · Ember Drake · Encantado · Ettercap · Ettin  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch6_EachUisge_to_Ettin.md`]

#### F (7 entries)
Fear Gorta · Fire Elemental · Fire Giant · Fire Mephit · Firebird · Fossegrim · Frost Giant  
[SOURCE: `MonsterEntries_v4.docx`]

**⚠ MISSING CONTENT — F ENTRIES:**
No dedicated batch file for F entries was found. Confirm these entries exist in `MonsterEntries_v4.docx`. Fear Gorta, Firebird, and Fossegrim are mythological; confirm Oreka placement and elemental affinity.

#### G (21 entries)
Gallu · Gargoyle · Garuda · Gelatinous Cube · Ghast · Ghoul · Ghūl · Girallon · Gnoll · Goblin · Gorgon · Gray Ooze · Green Hag · Grick · Griffon · Grig · Grimlock · Grootslang · Gynosphinx  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch7b_Girallon_to_Grick.md`; `Oreka_Batch7c_Griffon_to_Gynosphinx.md`]

**⚠ NOTE:** The Bestiary Master Roster TOC shows 21 G entries but lists only 19 names with two blanks (shown as "·" gaps in the TOC). Confirm Goblin and one other entry are present in final files.

#### H (9 entries)
Hakuturi · Harpy · Hieracosphinx · Hill Giant · Hippogriff · Huallallo · Huldra · Humbaba · Hydra  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch8a_Hakuturi_to_Hippogriff.md`; `Oreka_Batch8b_Huallallo_to_Hydra.md`]

#### I (3 entries)
Impundulu · Indrik · Inkanyamba  
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch9a_Impundulu_to_Jorogumo.md`]

**⚠ NOTE:** TOC shows I ends at Inkanyamba but the batch file is titled "Impundulu_to_Jorogumo" — confirm whether Jorogumo is under J.

#### J–K (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch9b_Kappa_to_Klatterkin.md`; `Oreka_Batch9c_Kobold_to_Krasue.md`]

**⚠ MISSING CONTENT:** No J section is listed in the master TOC. Jorogumo (Japanese mythological water spider) appears in the Batch9a filename. Confirm whether Jorogumo is included and under what letter it is filed.

#### L (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch10a_Lamassu_to_Locathah.md`]

#### M (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch10b_Maero_to_Mushussu.md`]

#### N (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch11a_Nack_to_Nasnas.md`; `Oreka_Batch11b_Nidhoggrkin_to_Nymph.md`]

#### O (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch12a_OchreJelly_to_Oni.md`; `Oreka_Batch12b_OozeMephit_to_Owlbear.md`]

#### P (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch13a_Pegasus_to_PhiPop.md`; `Oreka_Batch13b_PhiTaiHong_to_Ponaturi.md`; `Oreka_Batch13c_Popobawa_to_PurpleWorm.md`; `Oreka_Batch13d_Qareen_to_Qilin.md`]

**⚠ NOTE:** Batch13d is titled Qareen_to_Qilin (Q entries) but is grouped in the P-range batch files. Confirm file naming is correct and Q entries are accounted for.

#### Q (entries per Bestiary Roster)
[SOURCE: `Oreka_Batch13d_Qareen_to_Qilin.md`]

#### R (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch14a_Rakshasa_to_Roc.md`; `Oreka_Batch14b_Roper_to_RustMonster.md`]

#### S (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch15a_Sahmeran_to_SandWraith.md`; `Oreka_Batch15b_Satyr_to_ShamblingMound.md`; `Oreka_Batch16a_Shedim_to_Skinwalker.md`; `Oreka_Batch16b_Spectre_to_StormWisp.md`; `Oreka_Batch16c_Supay_to_SvartalfarShade.md`]

**⚠ NOTE:** Sand Wraith has a dedicated entry in Batch15a. This entry must be cross-checked against the Sand Wraith canon ruling in the Canon Bible (Sand Wraiths = mal-aligned grief spirits of Kin crossing back due to missing Elemental Lords — NOT Giant spirits). Confirm the entry reflects this.

#### T (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch17a_Taniwha_to_Thunderbird.md`; `Oreka_Batch17b_Tipua_to_Troll.md`; `Oreka_Batch17c_Tsukumogami_to_Tuchulcha.md`; `Oreka_Batch17d_Ugallu_to_Uthikoloshe.md`]

**⚠ NOTE:** Batch17d is titled Ugallu_to_Uthikoloshe (U entries) but grouped in the T batch files. Confirm all U entries are accounted for.

#### U (entries per Bestiary Roster)
[SOURCE: `Oreka_Batch17d_Ugallu_to_Uthikoloshe.md`]

#### V (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch18a_VampireSpawn_to_Vodyanoy.md`]

#### W (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch18b_WaterElemental_to_Wendigo.md`; `Oreka_Batch18c_Wight_to_Worg.md`; `Oreka_Batch18d_Wraith_to_Wyvern.md`]

#### Y–Z (entries per Bestiary Roster)
[SOURCE: `MonsterEntries_v4.docx`; `Oreka_Batch19_YerSub_to_Zombie.md`]

---

### CHAPTER 3: THE DÓMNATHAR BESTIARY
[SOURCE: `Domnathar_Bestiary.docx` — complete; Canon Bible §7 for lore context]

*Introductory note: Why these creatures register as silence on Kin-sense*

**Part One: The Buarath Mutate Family**
- Graftling (CR 1)
- [Further Buarath creatures from `Domnathar_Bestiary.docx`]

**Part Two: House Creatures**
*One section per Great House, each with introduction and unique creature(s)*
[SOURCE: Full content from `Domnathar_Bestiary.docx`]

**⚠ MISSING CONTENT — DÓMNATHAR BESTIARY:**
The `Domnathar_Bestiary.docx` intro mentions the Graftling explicitly but the file is 617 lines — not all entries have been verified as complete. A full audit of which House creatures exist vs. which are placeholders is needed. The Canon Bible lists 11 Great Houses (plus fallen House Konaeth = 12 total). Confirm each House has at least one creature entry.

---

### CHAPTER 4: TEMPLATES
[SOURCE: `The_Duty_Bound_Creature_Template.docx`; `The_Flesh_Forged_Creature_Template.docx`; Canon Bible §11]

**Established Templates:**
- The Duty-Bound (Acquired; any Kin) [SOURCE: `The_Duty_Bound_Creature_Template.docx` — fully written]
- The Flesh-Forged (Acquired; any humanoid) [SOURCE: `The_Flesh_Forged_Creature_Template.docx` — fully written]
- Elemental Infused [SOURCE: Canon Bible §11 — "Established Canon" subsection]

**Proposed Templates (Not Yet Finalized):**
[SOURCE: Canon Bible §11 "Proposed Templates"]

**⚠ MISSING CONTENT — TEMPLATES:**
Canon Bible §11 lists "Proposed Templates (Not Yet Finalized)" — these exist as design concepts but are not fully written. A decision is needed: include as appendix placeholders, develop fully, or cut for this edition. The Canon Bible language "not yet finalized" suggests these are author-pending items.

---

### APPENDIX A: BESTIARY MASTER ROSTER
[SOURCE: `Oreka_Bestiary_Master_Roster.docx` — complete 251-creature indexed table with Source, Type, CR, Region columns]

*Indexed roster with Challenge Rating quick-reference and regional distribution table*

---

### APPENDIX B: CREATURES BY REGION
*A secondary index cross-referencing creatures to the seven Oreka regions for encounter building*
[SOURCE: Environment field in each creature entry in `MonsterEntries_v4.docx`; also `Oreka_Bestiary_Master_Roster.docx` Region column]

---

### APPENDIX C: CREATURES BY CR
*Quick-reference table for encounter building*
[SOURCE: CR field in `Oreka_Bestiary_Master_Roster.docx`]

---

### APPENDIX D: MONSTER ENTRY CONSTRUCTION GUIDE
[SOURCE: `Oreka_Monster_Entry_Construction_Guide.md` — full document, reformatted for print]

*This appendix is for DMs who wish to create Oreka-compatible homebrew creatures. It explains the 24-field stat block, CR benchmarks, Kin-Sense signature design, and all eight canon rulings governing creature design.*

---

### APPENDIX E: PRONUNCIATION GUIDE (MONSTER MANUAL VOLUME)
[SOURCE: `Oreka_Pronunciation_Master__1_.docx` — extract creature and monster names only]

---

### BACK MATTER
- Open Game License v1.0a
- Index

---

## BOOK 1 — COMPLETE GAP ANALYSIS

| Gap | Why Needed | Content Type Required |
|---|---|---|
| Chapter 1 Monster Feats (10 feats) | Named in TOC but not written anywhere | Mechanical: feat stat blocks in 3.5e format |
| Chapter 1 Elemental Affinity Feats (monster version) | Player versions exist; monster adaptation missing | Mechanical: 4 adapted feat entries |
| Chapter 1 Dómnathar Signature Spells (6 spells) | Canon Bible names their existence; full stat blocks missing | Mechanical: spell stat blocks in 3.5e format |
| F entries confirmation | No dedicated batch file; entries should be in MonsterEntries_v4 | Audit/confirmation |
| G entries: 2 blank slots in TOC | Two creature names missing from TOC listing | Audit: identify the 2 unnamed G creatures |
| J entries / Jorogumo placement | Batch file name suggests it exists but TOC does not list it | Audit: confirm Jorogumo entry and letter placement |
| Dómnathar House creature audit | 12 Houses listed in Canon Bible; not confirmed all have creature entries | Audit + possible new creature writing (1 per House) |
| Proposed Templates finalization | 3–4 template concepts exist but are incomplete | Author ruling + mechanical completion |
| Bestiary Reconciliation (MonsterEntries_v4 vs. Batch files) | Two sets of content for same creature list; must establish canonical versions | Editorial: identify master copy per creature |
| Monsters for the Shrines / Veil zones | Canon mentions specific elemental zones; no dedicated creatures for shrine guardians | Optional: 4–8 new creature entries as "Guardian" category |

---
---

# BOOK 2: RACES OF OREKA
## *Races of the Elemental Dawn*

**Subtitle:** *A Player's Guide to the Peoples, Classes, and World of Oreka*  
**Audience:** Players. No DM secrets. No hidden lore. No true statuses.  
**Core Rule:** All "DM NOTE" content from the Canon Bible is stripped entirely from this book. Player-facing summaries replace it where context is needed.

---

## TABLE OF CONTENTS — BOOK 2

### FRONT MATTER
- Title Page / Legal
- How to Use This Book
- The World in Brief: A Player's Introduction to Oreka [SOURCE: Canon Bible §1 player sections per `Canon_Bible_Player_DM_Audit_v1.md`]
  - The Elemental Lords (player-safe: names, domains, "absent/asleep/active" status only)
  - The Summer Lands (player-safe: Kin go there, it exists, four Great Palaces)
  - The Ascended Gods (player-safe: full table minus apotheosis mechanics)
  - The Kin-Sense (full mechanical system — this is player-facing)

---

### PART ONE: THE KIN — RACES OF OREKA

*Chapter 1: The Order of Creation*
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 1 — fully written, ~3,000 lines]

**1.1 Giants — The Firstborn** *(Non-playable; presented for legacy context)*
- Origin & Mythology
- Physical Description  
- Legacy: What Giants Left Behind (ruins, Windstones, Tombs of Kings, sky-island engineering)
- Game Stats: presented as NPC/monster baseline only

**1.2 Elves — The Secondborn**
Four Subraces, each with full racial stats:
- Kovaka (Fire-aligned; pragmatic, mountain-border warriors)
- Na'wasua (Wind-aligned; sky-island dwellers, 20 floating islands)
- Pasua (Earth-aligned; forest nomads, Wind-Riders brotherhood)
- Hasura (Water-aligned; canopy city builders, sky-oak forest culture)
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 1; Canon Bible §4 player sections]

*Player note on the Great Shame:* The Elves' cultural wound is player-facing at the surface level (they know they failed in some way before the Shattering). The specific mechanics of what happened are public knowledge in-world.

**1.3 Dwarves — The Thirdborn**
Three Subraces, each with full racial stats:
- Visetri (Earth/Stone-aligned; wandering brotherhood, Mithril Legion)
- Rarozhki (Fire-aligned; forge-masters, Kharazhad, Stone Covenant)
- Pekakarlik (Water-aligned; river traders, guild city masters, Peravost)
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 1; Canon Bible §4 player sections]

**1.4 Halflings — The Fourthborn**
Core Halfling stats + note on known subraces
*(The four secret subraces remain DM-only; the player version acknowledges diversity without revealing the subraces)*
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 1; Canon Bible §4 player sections]

**1.5 Humans — The Fifthborn**
Four Subraces, each with full racial stats:
- Orean (Earth-aligned; fortress builders, mountain cultures)
- Eruskan (Water-aligned; river traders, coastal cities)
- Taraf-Imro (Fire-aligned; bardic tradition, Harreem's people)
- Mytroan (Wind-aligned; steppe riders, nomadic culture)
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 1; Canon Bible §4 player sections]

**1.6 Farborn — Humans But Not Kin**
- What Farborn are (player-safe: arrive from elsewhere, no Kin-sense, gaining attunement over generations)
- Physical description and social reception
- Racial stats (Farborn Human variant)
- The Gilded Standard Company as cultural context
[SOURCE: Canon Bible §4a player sections; `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 1]

*DM content stripped:* The Fifth House / soul-coloring mechanics; the transitional generation mechanics; the full truth of what "arriving from elsewhere" means cosmologically.

**1.7 Dómnathar — The Invaders**
*Player-facing entry only. Dómnathar are presented as the known enemy, not as a playable race.*
- What players know: extraplanar origin, house-based society, no elemental attunement
- Physical description visible to a soldier or scout
- Cultural behaviors visible in encounters
- Why they are not playable (in-world reasoning: cosmological incompatibility)
[SOURCE: Canon Bible §7 player-safe sections per Audit; `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 3 player sections]

*DM content stripped:* Dómnathar-Zhuan full detail; the accident; the apotheosis plot; the gate plot; House Buarath's soul-replacement operations; Silentborn experimental notes.

**1.8 Half-Kin and Farborn Children**
- Canon ruling on mixed heritage (Kin cannot produce half-breeds; Farborn can)
- Farborn-Kin children: what this looks like in play
[SOURCE: Canon Bible §4 "Canon Ruling: Mixed Heritage"; §4 "Hybrid Peoples"]

---

### PART TWO: DAILY LIFE AND CULTURE

*Chapter 2: How Kin Live*
[SOURCE: Canon Bible §4b–§4e, player sections per Audit]

**2.1 Death, the Accounting, and the Rebirth Cycle**
*Player-facing summary: Kin go to the Summer Lands, stand before guardians, can be reborn*
[SOURCE: Canon Bible §4b player sections; DM-only Three Aspects and soul-coloring mechanics are stripped]

**2.2 Coming of Age — Education and the Three Paths**
[SOURCE: Canon Bible §4d — fully player-facing]

**2.3 Religion in Daily Life**
- The Three Tiers of Orekan Religious Practice
- Shrines, Veils, and Solstice Gatherings
- The Ascended Gods in daily worship
[SOURCE: Canon Bible §4c — player sections per Audit]

**2.4 Trade, Currency, and the Giant Standard**
[SOURCE: Canon Bible §4e — fully player-facing]

**2.5 Kin-Sense in Daily Life**
*How Kin experience the world's resonance — practical daily effects (not broken/unusual zones)*
[SOURCE: Canon Bible §3 player sections; Regional Guide Kin-Sense sections extracted from all seven guides]

---

### PART THREE: HISTORY PLAYERS KNOW

*Chapter 3: The Shaping of the World*
[SOURCE: Canon Bible §5 player sections; Regional Guide History sections, player-facing per Audit]

**3.1 The Age of Giants** *(fully player-facing)*
**3.2 The Eke Concordant and the Three Keepers**
**3.3 The Shattering of Man** *(both versions — player knows the surface)*
**3.4 The Deceivers' War** *(public events only)*
  - The Silence Breach
  - The Siege of Aldenheim: Days 1–42 (surface fall) — Day 42 is fully public
  - The Five Druids and Cinvarin's ascension — fully public
  - The Lost Third and the Southern War — fully public
  - The Lament of Kings and Harreem — FULLY PUBLIC per canon ruling
**3.5 The Reckoning and its Aftermath**
**3.6 Three Hundred Years Later: The World Now**

*DM content stripped from Chapter 3:*
- Days 42–142 underground war (Durak's full story)
- Lord of Wind's accidental exile (player text says "exiled" only)
- Stone Lord's comatose state from second gate
- Sundrift Veil relaunch capability
- Aetherial Veil weakening details

**3.7 The Oreka Calendar and Dating System**
[SOURCE: Canon Bible §5a — fully player-facing]

---

### PART FOUR: THE REGIONS

*Chapter 4: The Seven Regions — A Traveler's Overview*
[SOURCE: Player-facing sections extracted from all seven Regional Guides per `Regional_Guides_Player_DM_Audit_v1.md`]

*Design note: This chapter gives players the geography, culture, and general knowledge of each region. It is NOT the full regional guide — that is Book 3. This is the "what your character knows" version.*

**4.1 Gatefall Reach** — *Where the World Went Quiet*
- Geography and landmarks (player-safe)
- Cultural identity
- Major settlements (player-facing only)
- Kin-Sense in the Gatefall (daily life section only)

**4.2 Eternal Steppe** — *Where the Wind Remembers What Kings Forget*
- Geography and landmarks (player-safe)
- Mytroan culture deep-dive (this is their homeland)
- Major settlements: Tavranek, Windstone sites
- Kin-Sense on the Steppe

**4.3 Deepwater Marches** — *Where the Forest Meets the Sea*
- Geography (Apelian Sea, Deepwood, Verdant Shoals)
- Cultural identity
- Major settlements

**4.4 Infinite Desert** — *The Corridor Without End*
- Geography (the corridor between Giant's Teeth ranges, 49,800 miles)
- The Indorach and Warg communities
- Major settlements and oasis-cities

**4.5 Tidebloom Reach** — *Where the Sky-Islands Dream*
- Geography and the Sundrift Veil (player knows it exists, looks natural)
- Hasura canopy cities
- Major settlements including Hillmeet

**4.6 Kinsweave** — *The Weight of Empty Thrones*
- Geography (Giant's Teeth, Great River, Scorchspires)
- The Twelve Kingdoms and their ruins
- Living cities: Stonefall, Rivertop, Highridge, Lakeshore, Lakewell
- Kharazhad sidebar (public knowledge only)
- The Lament of Kings site

**4.7 Twin Rivers** — *Where Two Become One*
- Geography (Great River split at Peravost, convergence at Forkmeet)
- Peravost: City of Bridges
- Sylaraeth: The Veil City (player-facing: crystal spires, attunement crystals, minor flight, kaleidoscope light)
- Regional settlements

---

### PART FIVE: CLASSES AND ADVANCEMENT

*Chapter 5: Base Classes of Oreka*
[SOURCE: `Oreka_Base_ClassesNew.pdf` — fully written base classes; adapted for Oreka]

*All standard D&D 3.5e base classes are available. This chapter presents the Oreka-specific adaptations, flavor, and cultural context for each class.*

- Fighter (Kin cultural contexts: Mithril Legion fighters, Mytroan riders, Stoneharbor guards)
- Ranger (Mytroan outriders, Pasua wardens, Hasura canopy scouts)
- Rogue (Pekakarlik guild traders, Farborn infiltrators)
- Cleric (aligned to Elemental Lords or Ascended Gods — see Domain chapter)
- Druid (Cinvarin's legacy; the Five Witness tradition)
- Bard (Taraf-Imro tradition; Harreem's heritage)
- Wizard / Sorcerer (Magi Magic — the oldest tradition, see §5.7)
- [All remaining base classes with Oreka flavor text]

**5.1 Elemental Attunement Rules for Spellcasters**
[SOURCE: Canon Bible §2 "Elemental Attunement in Creatures" — player sections]

**5.2 Magi Magic — The Oldest Spellcasting Tradition**
[SOURCE: Canon Bible §15 — fully player-facing; Magi Magic is independent of the elemental framework and predates Kin civilization]

---

*Chapter 6: Prestige Classes*
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` Prestige Classes section — fully written]

**Part I: OGL-Adapted Prestige Classes** (15 classes)
- Arcane Archer (Hasura/Pasua Elf focus)
- Arcane Trickster (Pekakarlik/Halfling focus)
- [13 remaining OGL prestige classes, each with Oreka integration notes]

**Part II: Oreka-Original Prestige Classes**
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` Part II — confirm how many are fully written]

**⚠ MISSING CONTENT — PRESTIGE CLASSES:**
The Races compendium explicitly names "Oreka-original prestige classes: unique paths born from the setting's elemental magic." These include Starweaver, Stonewarden, Sky Artisan, and others mentioned in the Chapter 6 placeholder. The prestige class section in the provided PDF shows only the OGL-adapted classes as fully written. The Oreka-original prestige classes do not appear to be fully written in any file.
- **Gap type:** Original mechanical content. Requires: class name, requirements, 10-level progression table, 5–8 class features, and Oreka integration text per class.
- **Estimated scope:** 6–10 prestige classes at approximately 400–600 words each.

---

*Chapter 7: Cleric Domains*
[SOURCE: `Cleric_Domain_Spell_List_Clean.docx` — 1,823 lines, full domain list]

*All Oreka-available cleric domains with spell lists. Organized by Elemental Lord alignment and Ascended God portfolio.*

**Domain Index:**
Air · Animal · Artifice · Blackwater · Celerity · Celestial · Chaos · [continued — full list from `Cleric_Domain_Spell_List_Clean.docx`]

**Domains by Deity:**
- Elemental Lords: which domains each Lord grants
- Ascended Gods: domains by portfolio (Cinvarin, Harreem, Tarvek Wen, Ludus Galerius, Apela Kelsoe, Kaile'a, Gonmareck Ritler, Semyon, The Hand Unanswered, The Unnamed Warrior King)

**⚠ MISSING CONTENT — CLERIC DOMAINS:**
The domain spell list is cleaned and complete. However, no document assigns domains to specific Oreka deities. Each Elemental Lord and each Ascended God needs a defined domain list. This assignment does not exist in any current file.
- **Gap type:** Setting-specific rule assignment. Requires: 4 Elemental Lord domain lists + 10 Ascended God domain lists.

---

### PART SIX: FACTIONS AND ORGANIZATIONS

*Chapter 8: Who Kin Belong To*
[SOURCE: Canon Bible §8 player sections; `Races_of_Oreka_Complete_Compendium__1_.pdf` Chapter 7 (placeholder text exists)]

**8.1 The Eke Concordant** (historical; player-facing)
**8.2 The Mithril Legion** (Visetri wandering brotherhood — fully public)
**8.3 The Stone Covenant** (public knows it exists; connection to other Orders is DM-only)
**8.4 The Gilded Standard Company** (Farborn mercenaries; fully public)
**8.5 The Wind-Riders and Far Riders** (two halves of one brotherhood; player-facing)
**8.6 Trade Houses and Guild Structures** (player-facing economic factions)
**8.7 Regional Factions** (from Regional Guides, player-facing sections)

*DM content stripped:* Full Military Order three-way connection; Spur Tower location/purpose; Stone Covenant's full HQ reveal; House Buarath soul-replacement operations.

---

### BACK MATTER
- Glossary (player-facing terms only) [SOURCE: `Oreka_Glossary.docx` — extract player-safe entries; strip all DM NOTE content]
- Pronunciation Guide (player volume) [SOURCE: `Oreka_Pronunciation_Master__1_.docx` — peoples, places, and cultural terms only]
- Elemental Quick-Reference Card
- Character Creation Checklist (race + class + elemental affinity + cultural background)
- Index

---

## BOOK 2 — COMPLETE GAP ANALYSIS

| Gap | Why Needed | Content Type Required |
|---|---|---|
| Oreka-original prestige classes (6–10 classes) | Named in compendium but not written | Mechanical: full class progression, features, Oreka integration |
| Domain assignments per deity (14 deities) | Domain list exists; deity-domain mapping missing | Setting rule: 4 Elemental Lord + 10 Ascended God domain assignments |
| Halfling subrace player-facing note | 4 secret subraces exist; player text needs non-spoiler acknowledgment | Short lore: 1 paragraph acknowledging subrace diversity without revealing it |
| Farborn prestige class or racial feat chain | Farborn gain attunement over generations; no mechanical pathway provided | Optional: feat chain or prestige class for transitioning Farborn |
| Dómnathar player-facing entry (encounter-level knowledge) | Players need to recognize and react to Dómnathar in play | Player-safe creature/culture entry: visual appearance, known behaviors, encounter guidance |
| Character creation integration (race × class × elemental) | No single document synthesizes these choices | Utility: 1–2 page matrix or decision guide |
| Chapter 4 Region sections (player extracts from 7 guides) | Currently buried in full DM guides; player-safe version not isolated | Editorial: extract and rewrite player-facing sections from each Regional Guide |
| Kin-Sense daily life compendium | Scattered across 7 regional guides; no single player reference | Editorial: compile all 7 Kin-Sense daily life sections into one chapter |

---
---

# BOOK 3: OREKA DUNGEON MASTER'S GUIDE

**Subtitle:** *Secrets of the Elemental Dawn — A Complete Campaign Reference*  
**Audience:** Dungeon Masters only. Contains all DM-only content, full regional guides, hidden truths, campaign-level plots.  
**Core Rule:** This book contains the full, unredacted truth of every [DM] and [BOTH-DM] item from the Canon Bible and Regional Guide audits.

---

## TABLE OF CONTENTS — BOOK 3

### FRONT MATTER
- Title Page / Legal
- How to Use This Book
- The Three-Layer System: How to Manage Player-Facing vs. DM-Facing Information
- Quick Reference: What Players Know (summary of Book 2) vs. What the DM Knows (this book)

---

### PART ONE: THE TRUE WORLD

*Chapter 1: Cosmology — The Full Picture*
[SOURCE: Canon Bible §1 DM sections; Canon Bible §7 full]

**1.1 The Elemental Lords — True Status**
- Lord of Stone: comatose; caused by second assault gate (not the Silence Breach); Dómnathar unaware
- Lady of Fire: active; holding the Abyss Circle back; destroying first gate
- Lady of Water / Tempest: active; alongside Lady of Fire at the Breach
- Youngest Brother / Wind Lord: NOT exiled by choice — accidentally pulled from realm; actively seeking return; DM hook for Aetherial Veil weakening
- The Abyss Circle: no direct presence in Oreka while the door is held; "answering letters from a place they cannot reach"

**1.2 The Spirit Realm — Full Architecture**
- Single combined plane (not four separate)
- Four Great Palaces: anchor points, mini-elemental zones, self-sustaining
- Shrines as pinpricks; Veils as sustained overlaps
- What Fire and Tempest are actually doing at the Breach
- Dómnathar cosmological incompatibility (cannot interact with shrine/Veil infrastructure)

**1.3 The Ascended Gods — Hidden Truths**
- Apotheosis mechanics (full: four-element attunement, morally neutral, magnitude-driven)
- Harreem DM truth (patricide confirmed; full apotheosis event detail)
- Durak Stonewatch: unknown for 300 years after Day 142; worshippers know a version; full truth is secret
- The Unnamed Warrior King: why the alignment is "Disputed" and what that means for your campaign

**1.4 The Dómnathar Apotheosis Plot** *(DM-FACING ONLY)*
[SOURCE: Canon Bible §7 "The Dómnathar Apotheosis Plot"]

**1.5 The Dómnathar Gate Plot** *(DM-FACING ONLY)*
[SOURCE: Canon Bible §7 "The Dómnathar Gate Plot"]

**1.6 Dómnathar-Zhuan — The Full World**
[SOURCE: Canon Bible §7a through §7d — complete detail including the Accident, the Cut-Off, Three Hundred Years, the Eleven Great Houses full descriptions]

---

*Chapter 2: The Peoples — Hidden Layers*
[SOURCE: Canon Bible §4 DM sections; §4b DM sections; Audit rulings]

**2.1 The Three Aspects of Death** *(DM-only)*
- What actually happens when Kin die; the full accounting mechanics
- Soul-coloring: full mechanics (players see hint only: "carry something forward that cannot be named")

**2.2 The Farborn Fifth House** *(DM-only)*
- What the Fifth House is
- Why Farborn children are "different" in ways their parents cannot explain
- The transitional generation mechanics

**2.3 The Pekakarlik Split — Full Truth** *(DM-only)*
- The Aldenheim dispute
- Visetri delayed loyalty
- Why the estrangement runs deeper than players know

**2.4 The Four Halfling Subraces** *(DM-only)*
[SOURCE: Canon Bible §4 "The Four Halfling Subraces" — full detail]

**2.5 Sand Wraiths — Origin and Behavior** *(DM-depth)*
- Full origin: mal-aligned grief spirits of Kin crossing back due to missing Elemental Lords
- NOT Giant spirits (common misconception in-world)
- The Indorach connection: atheist dead become spirits, learn belief, then grieve missing Lords
- How to use Sand Wraiths as a campaign element

---

### PART TWO: HISTORY — THE FULL RECORD

*Chapter 3: The Complete Historical Record*
[SOURCE: Canon Bible §5 full; §14 "The Lost Third"; Regional Guide History sections, DM layers]

**3.1 The Siege of Aldenheim — Complete**
- Days 1–42: public record
- Day 42: Five Druids' rage; Cinvarin's ascension; simultaneous events
- Days 42–142: the underground war *(DM-only)*
  - Durak Stonewatch's full story
  - Day 142: Durak falls and ascends — unwitnessed, unknown for 300 years
- What the populace believes vs. what happened

**3.2 The Lost Third and the Southern War** *(Chapter 14 from Canon Bible)*
- The Reversal
- The March South
- The Running War (Wind-Riders / Far Riders — two halves of one brotherhood)
- The Gilded Company's Betrayal
- The Battle of Dark Dawn
- The Scatter: Two Fates
- The Aftermath

**3.3 The Lament of Kings — All Three Meanings**
- The druidic ritual
- The blasted plain
- Harreem's killing of the twelve kings (full account)
- How all three are simultaneously canonical
- The public confession that sparked the Stone Covenant, Lament festival, and rebuilt alliances

---

### PART THREE: THE SEVEN REGIONS — COMPLETE GUIDES

*Introduction: How to Use the Regional Guides*
- The 14-section template explained
- Campaign Integration sections (DM-only throughout)
- How to layer player-facing and DM-facing information at the table

---

*Chapter 4: Gatefall Reach — Full Regional Guide*
[SOURCE: `Gatefall_Reach_Regional_Guide_v3.docx` — complete; DM notes included]

Full 14-section structure:
1. Region Overview
2. Geography and Named Land Features
3. Regional History (full DM version)
4. Cultural Identity
5. Political Landscape
6. Religion and Belief
7. Elemental Influence and Kin-Sense (daily life + unusual zones in this section)
8. Major Settlements
9. Regional Power Centers
10. Trade and Travel
11. Factions and Organizations
12. Threats, Conflicts, and Current Situation
13. Adventure Hooks
14. Campaign Integration *(DM-only)*

**DM-ONLY CONTENT — GATEFALL REACH:**
- Gatefall Remnant's purpose at the Tomb of Kings (players see Remnant uses it as base; purpose is DM-only)
- Full Tomb of Kings contents and Giant-era secrets
- Silence Breach exact mechanics and current status

---

*Chapter 5: Eternal Steppe — Full Regional Guide*
[SOURCE: `EternalSteppe_v4.docx` — complete, v4]

Full 14-section structure (same as above)

**DM-ONLY CONTENT — ETERNAL STEPPE:**
- Burnt Hollows Dómnathar warrens: discovery through play; what is actually down there
- Windstone full rune-circle mechanics and reactivation potential
- Warg community elemental attunement timeline (300-year accumulation)

---

*Chapter 6: Deepwater Marches — Full Regional Guide*
[SOURCE: `DeepwaterMarches_v4.docx` — complete, v4]

Full 14-section structure

**DM-ONLY CONTENT — DEEPWATER MARCHES:**
- The Spur full detail (player sees: mysterious, avoid; DM knows: what it is and who controls it)
- Farborn Fifth House presence in the Marches
- Elven Great Shame full context for this region

---

*Chapter 7: Infinite Desert — Full Regional Guide*
[SOURCE: `InfiniteDesert_v4.docx` — complete, v4]

Full 14-section structure

**DM-ONLY CONTENT — INFINITE DESERT:**
- Indorach atheism → Sand Wraith pipeline (full mechanics)
- Dómnathar Lost Third remnants: location and current activity
- Desert Tomb of Kings: full contents
- The corridor's actual length (49,800 miles — players know it wraps the planet, not the exact measurement)

---

*Chapter 8: Tidebloom Reach — Full Regional Guide*
[SOURCE: `Tidebloom_v4.docx` — complete, v4]

Full 14-section structure

**DM-ONLY CONTENT — TIDEBLOOM:**
- Sundrift Veil relaunch capability: rune-circle dormant but intact; can relaunch (players see natural island)
- Tidebloom Tomb of Kings: exact location near Hillmeet; full contents
- Dómnathar refugees near Hillmeet: what they are actually doing
- Na'wasua hidden islands: players know 17; Na'wasua hide 3; DM knows the 3 hidden ones and why

---

*Chapter 9: Kinsweave — Full Regional Guide*
[SOURCE: `Kinsweave_v4.docx` — complete, v4]

Full 14-section structure

**DM-ONLY CONTENT — KINSWEAVE:**
- Kinsweave Tomb of Kings: exact location (large stage, back left corner of Lament of Kings grounds)
- Durak Stonewatch's full history and the underground war's physical footprint in Kinsweave
- Stone Covenant HQ at Kharazhad: full operational detail
- Thane Karveth Stonefire: 350–400+ years old; last living witness to Aldenheim; what he actually knows
- Mithril Legion / Mithril Chains shared-name red herring: full DM explanation

---

*Chapter 10: Twin Rivers — Full Regional Guide*
[SOURCE: `TwinRivers_Regional_Guide_v3__1_.docx` — complete, v3]

Full 14-section structure

**DM-ONLY CONTENT — TWIN RIVERS:**
- Aetherial Veil weakening: the Wind Lord connection; what the Unstrung are and their leverage
- Tomb of Kings under Stoneharbor: exact location; what the Pekakarlik may have found
- Lord of Stone comatose location: Twin Rivers region; how this affects the local elemental balance
- Sylaraeth Aetherial Veil as prototype: the blueprint for replication; DM implications
- Three canopy cities: what lives in the sky-oaks below them that drove the Hasura up

---

### PART FOUR: RUNNING THE CAMPAIGN

*Chapter 11: Factions in Depth*
[SOURCE: Canon Bible §8 full; Regional Guide faction sections DM layers]

**11.1 The Three Military Orders — Full Truth**
- Mithril Legion (public: Visetri wandering brotherhood)
- Steelward Host (mostly forgotten; extinct; what it was)
- Stone Covenant (public knows it exists; DM knows: HQ at Kharazhad, full connection to other two Orders)
- How the three connect: the full reveal sequence for a campaign
- Call signs: "We Stand for the Host" / "the stone remembers"

**11.2 Kharazhad — Full Operational Detail**
- Thane Karveth Stonefire full profile
- Forgekeeper Agama Stonefire full profile
- Sacred flame as pinprick to Palace of Flames: what this means in play
- Scorchspires Pact with Highridge: allies but rivals; full diplomatic situation

**11.3 Spur Tower** *(DM-FACING ONLY)*
- The Dómnathar hidden stronghold rebuilt over 300 years
- Current operational status
- How players might discover it

**11.4 The Abyss Circle — Nine Patrons**
[SOURCE: Canon Bible §7 "The Abyss Circle"]
- Full descriptions of all nine Patrons
- What they want, what they cannot do while the door is held
- How their priests function (answering prayers through a barrier)

**11.5 House Buarath — Soul Replacement Operations** *(DM-ONLY)*
[SOURCE: Canon Bible §7; Dómnathar Bestiary]
- Full mechanics of giving non-Kin spirits new bodies
- Recipients are unaware
- How to introduce this into a campaign

---

*Chapter 12: Encounter Design and the Elemental Ecology*
[SOURCE: Canon Bible §6; §9; §13; all Regional Guide Threats sections]

**12.1 The Three-Tier Bestiary System**
[SOURCE: Canon Bible §9 — full creature categories]

**12.2 Regional Encounter Tables**
*One table per region, organized by CR range*
[SOURCE: Derive from creature Environment fields in `MonsterEntries_v4.docx` + `Oreka_Bestiary_Master_Roster.docx`]

**12.3 The Elemental Ecology — How Creatures Relate to the Land**
[SOURCE: Canon Bible §6 Regional Environment Guide; §13 Design Philosophy]

**12.4 Dómnathar Encounter Design**
[SOURCE: Canon Bible §7 "Dómnathar Creature Design Principles"; Dómnathar Bestiary intro]

**12.5 Paragon Encounters**
*How to run a Paragon encounter; what it means narratively; how communities react*
[SOURCE: Monster Manual Introduction — Paragons section; repurposed for DM guidance]

---

*Chapter 13: Settlements — Full Reference*
[SOURCE: Canon Bible §17 "Settlements — Named Locations"; Regional Guide Major Settlements sections full DM versions]

*All named settlements with full DM profiles: population, leadership, secrets, hooks, current tensions*

**⚠ MISSING CONTENT — SETTLEMENTS:**
The `Races_of_Oreka_Complete_Compendium.pdf` Chapter 2 "Settlements of Oreka" is marked as a placeholder: "[Full settlement entries for Twin Rivers, Tidebloom, Kinweave, and Northwest Region. Every mayor, official, population, festival, history, and district. Complete texts, not summarized.]" This content does not exist in written form in any file. Only Canon Bible §17 and the Regional Guide settlement sections provide actual settlement data.
- **Gap type:** Major content gap. Requires: full settlement write-ups for all named locations. The Canon Bible §17 provides a skeleton; Regional Guides provide regional context. The "every mayor, official, population, festival, history, and district" version referenced in the Races compendium is not written.

---

*Chapter 14: Economy, Equipment, and Trade Routes*
[SOURCE: Canon Bible §16 full; §4e full; Regional Guide Trade and Travel sections from all seven guides]

**14.1 The Giant Standard (currency system)**
**14.2 The Four Pillars of Long-Distance Trade**
**14.3 Titanbreed Pricing** (8,000–15,000 gp — canonized)
**14.4 Regional Trade Specialties** (one per region from Regional Guides)
**14.5 The Great River Trade Network**
**14.6 Sea Falls Navigation** (halfling submersibles, seasonal tidal flow, chaotic interior)

---

*Chapter 15: Magic Systems*
[SOURCE: Canon Bible §15 "Magi Magic"; §2 "Elemental Attunement"; §3 Kin-Sense full rules; Regional Guide elemental sections]

**15.1 Magi Magic — Full Rules**
[SOURCE: Canon Bible §15; §15 "Critical Ruling: Magi Magic Independence"]

**15.2 Kin-Sense — Full Mechanical System**
[SOURCE: Canon Bible §3 complete — Detection DCs, Racial Bonuses, Tiered Success, Situational Modifiers, Special Cases, the Deceiver's Feat]

**15.3 Shrine and Veil Mechanics**
*How shrines and Veils function mechanically in play*

**15.4 Dómnathar Spell Design**
[SOURCE: Canon Bible §7 "Dómnathar Elemental Disconnection"; Monster Manual Chapter 1 Dómnathar Spells]

**⚠ MISSING CONTENT — SHRINE/VEIL MECHANICS:**
The Canon Bible extensively references Shrines and Veils as locations and cosmological concepts. No document provides actual mechanical rules for what a PC standing in or interacting with a Shrine or Veil experiences, what rolls are required, or what effects are produced.
- **Gap type:** Core mechanical system. Requires: Shrine interaction rules, Veil zone effects, and DM guidance on attunement crystal mechanics (referenced for Sylaraeth).

---

### PART FIVE: REFERENCE AND TOOLS

*Chapter 16: Classes for the DM — NPCs and Prestige*
[SOURCE: `Races_of_Oreka_Complete_Compendium__1_.pdf` prestige classes; Canon Bible §18 "Classes & Prestige Classes"]

*Full class reference for building NPC adversaries, Dómnathar agents, and faction leaders*

---

### BACK MATTER
- Appendix A: Open Questions and Author Flags [SOURCE: Canon Bible Appendix A "Remaining Open Questions"]
- Appendix B: Worldbuilding Gaps [SOURCE: Canon Bible Appendix B "Worldbuilding Gaps"]
- Appendix C: Production Checklist [SOURCE: Canon Bible Appendix C "RPG Production Gaps"]
- Appendix D: Canon Change Log [SOURCE: Canon Bible Appendix D "All Changes Applied"]
- Glossary (DM-complete, including all DM NOTE entries) [SOURCE: `Oreka_Glossary.docx` — full text including all DM-flagged definitions]
- Pronunciation Guide (DM volume — all terms) [SOURCE: `Oreka_Pronunciation_Master__1_.docx` — complete]
- Index

---

## BOOK 3 — COMPLETE GAP ANALYSIS

| Gap | Why Needed | Content Type Required |
|---|---|---|
| Full settlement write-ups (all named locations) | Races compendium placeholder promises "every mayor, official, population, festival, history, and district" — this does not exist | Major writing project: 20–40 settlement profiles at 500–1,500 words each |
| Shrine and Veil mechanical rules | Core location type throughout all 7 guides; no interaction mechanics written | Mechanical: DC tables, effect lists, attunement crystal rules |
| Regional encounter tables (7 regions × CR range) | No compiled encounter tables in any file | Editorial + mechanical: derive from creature Environment fields |
| Dómnathar Signature Spells (6) | Named in Monster Manual TOC; not written anywhere | Mechanical: 6 spell stat blocks |
| Abyss Circle patron profiles | Canon Bible §7 lists all 9 Patrons; full profiles not confirmed complete | Lore: 9 patron write-ups with portfolio, motivation, and campaign use |
| Sea Falls full description | Mentioned as a major feature (subterranean tunnel connecting two seas); no detailed write-up | Geography + encounter design: 500–800 words + encounter hooks |
| Ashgarin Fold development | "Exists on the map but needs development" (per working notes) | Lore + geography: full regional sub-area write-up |
| Stone Concordant vs. Stone Covenant naming resolution | Flagged as unresolved conflict in working notes | Author ruling needed; then find-and-replace across all documents |
| Three Military Orders full reveal sequence | DM guidance needed for how/when players learn the connection | Campaign structure: reveal flowchart and encounter triggers |
| Na'wasua three hidden islands | Flagged as DM-only; 17 known, 3 hidden; hidden ones not described | Lore: 3 island profiles with why they're hidden |

---
---

# CROSS-BOOK CONTENT APPEARING IN MULTIPLE VOLUMES

The following content must appear in more than one book, with appropriate versions for each audience:

| Content | Book 1 Version | Book 2 Version | Book 3 Version |
|---|---|---|---|
| Kin-Sense system | Front matter: DM encounter implications | Ch. 2.5: daily life, no broken zones | Ch. 15.2: full mechanical rules |
| Elemental Affinity | Per creature entry | Racial ability tables | Full ecology and campaign impact |
| Dómnathar | Bestiary + Templates | Player encounter knowledge only | Full: houses, plots, operations |
| Ascended Gods | Creature design notes (Harreem-linked creatures) | Player table: names, portfolios, followers | Full: apotheosis mechanics, hidden truths |
| Harreem / Lament of Kings | Sand Wraith origin context | Full history (fully public) | Theological implications for campaign |
| Magi Magic | Not in Monster Manual | Player rules (§5.2) | Full DM rules + NPC casters |
| Regional Ecology | Creature Environment fields | Traveler's overview (Ch. 4) | Full 7 Regional Guides |
| Glossary | Not in Monster Manual | Player-safe terms only | Complete with DM Notes |
| Pronunciation | Monster/creature names | Peoples and places | All terms |
| Prestige Classes | Not in Monster Manual | Player use | DM reference (NPC builds) |

---

# MASTER PRODUCTION PRIORITY LIST

### Tier 1 — Must Resolve Before Any Book Goes to Layout
1. Reconcile `MonsterEntries_v4.docx` vs. Batch files — establish one canonical version per creature
2. Resolve Stone Concordant vs. Stone Covenant naming conflict (author ruling needed)
3. Audit Dómnathar Bestiary for completeness (which Houses have entries; which are missing)
4. Confirm full creature count matches 251-creature roster (G entries gap; J/Jorogumo status)

### Tier 2 — Major Writing Gaps (Book Completion Blockers)
5. Write 10 Monster Feats + 4 Elemental Affinity Feats (monster version) — Book 1
6. Write 6 Dómnathar Signature Spells — Books 1 and 3
7. Write Oreka-original Prestige Classes (Starweaver, Stonewarden, Sky Artisan, etc.) — Book 2
8. Assign domains to 14 deities (4 Elemental Lords + 10 Ascended Gods) — Book 2
9. Write full settlement profiles for all named locations — Book 3
10. Write Shrine and Veil interaction mechanics — Book 3

### Tier 3 — Content Enrichment (Important but Not Blocking)
11. Develop Ashgarin Fold sub-region
12. Write Na'wasua three hidden islands
13. Build regional encounter tables (7 regions)
14. Complete Proposed Templates from Canon Bible §11
15. Write Abyss Circle patron profiles (9 patrons)
16. Develop Sea Falls full description

### Tier 4 — Editorial and Production
17. Extract player-facing sections from 7 Regional Guides for Book 2 Chapter 4
18. Compile Kin-Sense daily life sections from 7 guides into Book 2 Chapter 2.5
19. Split Glossary into three volume-specific editions
20. Split Pronunciation Guide into three volume-specific editions

---

*Document prepared March 2026. All file references are to project files as enumerated above. This document is an internal architectural reference and production guide — it is not intended for publication in any of the three books.*
