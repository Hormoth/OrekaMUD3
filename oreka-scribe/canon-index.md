# Canon Index

Pointer file for the Oreka Scribe. Lists all canon documents and what each covers.
Read only what's relevant to the current session — don't load everything.

## Core Canon

| File | Location | Covers | DM Content? |
|------|----------|--------|-------------|
| Canon Bible (audit) | `World Regions history/New Documents/Canon_Bible_Player_DM_Audit_v1 (1).md` | Complete world canon: cosmology, Elemental Lords, Ascended Gods, races, factions, Kin-sense, Aldenheim, the Breach, history, apotheosis rules | Yes — marked per section |
| Three Book Architecture | `World Regions history/New Documents/Oreka_Three_Book_Architecture.md` | How canon is organized across Player Guide, DM Guide, Monster Manual | Yes |
| Lore entries | `oreka_mud/data/lore.json` | 17 canonical entries NPCs can reference (Aldenheim, EarthForge, Kin-Sense, Elemental Lords, etc.) | No |
| Deities | `oreka_mud/data/deities.json` | 13 deities with domains, alignment, lore | No |
| Factions | `oreka_mud/data/guilds.json` | 10 factions with ranks, rep thresholds, territories | No |

## Regional Guides

| File | Region | Key Content |
|------|--------|-------------|
| `World Regions history/New Documents/Regional_Guides_Player_DM_Audit_v1 (1).md` | All regions (audit) | Player/DM content split per region |
| Twin Rivers | (referenced in Canon Bible) | Custos do Aeternos, Liraveth, river trade, Trade Houses |
| `Kinsweave_v4.docx` | Kinsweave | Quarries, ruins, highland ecology, Stonefall, Rivertop, Highridge |
| `InfiniteDesert_v4.docx` | Infinite Desert | Pilgrim roads, Kharazhad, Sand Wardens, volcanic forges |
| `EternalSteppe_v4.docx` | Eternal Steppe | Far Riders, Tavranek, cavalry culture, Brotherhood |
| `GatefallReach_Regional_Guide_v3` | Gatefall Reach | Wind-Riders, Silence Breach, Hillwatch, frontier survival |
| `DeepwaterMarches_v4.docx` | Deepwater Marches | Warg settlements, jungle, intelligence trade, Titan's Rest |

## Creature Batches

19 batch files in `World Regions history/New Documents/Oreka_Batch*.md`
Each contains 5-15 creatures adapted for Oreka with ecology, behavior, encounter notes, and DM-only content.

| Batch | Notable Creatures |
|-------|-------------------|
| Batch 1 | Abatwa to Aranea |
| Batch 2a-b | Bakeneko to Bunyip |
| Batch 3 | Al-Karisi to Assassin Vine |
| ... (17 more) | See filenames for contents |

Also: `Oreka_Monster_Entry_Construction_Guide.md` — template for authoring new creatures.

## Other Reference

| File | Covers |
|------|--------|
| `oreka_mud/data/mobs.json` | 373 placed NPCs with stats, personas, dialogue |
| `oreka_mud/data/items.json` | 98 items with properties |
| `oreka_mud/data/recipes.json` | 60 crafting recipes |
| `oreka_mud/data/areas/*.json` | 1,624 rooms across 14 area files |
| `oreka_mud/data/modules/quiet_graft/` | The Quiet Graft module scaffold (arcs, personas, quest skeleton) |

## What's Not Canon (don't reference as authoritative)

- Session files in `oreka-scribe/sessions/` — these are works in progress
- Thread files — speculative until promoted to canon
- Draft quests — not live until moved to `quests/approved/`
- This index itself — it's a pointer, not content
