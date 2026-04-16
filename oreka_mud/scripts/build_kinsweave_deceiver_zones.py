"""Build the Kinsweave Deceiver zones.

  * Zone K1 -- Highridge Lava-Tube Artifact Chamber (16 rooms, 5308-5323)
    A Half-Dómnathar artifact-keeper infiltrated Highridge a decade ago
    and is siphoning power from a buried Deceiver artifact in the
    city's lava-tubes. Entry via a disreputable stall in the
    Scorchmarket South. Level band 7-10, boss CR 8.

  * Zone K2 -- Andrio Giant Chamber Proper (22 rooms, 5324-5345)
    Extends the 1-room Andrio Giant Chamber stub (5286) into the full
    expedition: a Half-Dómnathar expedition commandeered the Giant
    undercroft and is digging toward a pre-War artifact buried by
    Giants even before the Deceivers' War. A Dread Wraith -- a Giant
    general who died defending the seal -- is the deep-chamber
    guardian. Level band 10-13.

Idempotent. Run:
    python scripts/build_kinsweave_deceiver_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ===========================================================================
# Zone K1 -- Highridge Lava-Tube Artifact Chamber  (16 rooms, 5308-5323)
# ===========================================================================

HIGHRIDGE_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 5308,
        "name": "Highridge Under-Market -- Hidden Cellar",
        "description": (
            "A cellar beneath the sketchiest stall in the Scorchmarket "
            "South, accessible through a trapdoor the stallkeeper "
            "prefers not to discuss. Crates of scorch-marked ceramics "
            "line the walls; one crate has been pushed aside to reveal "
            "a narrow stair cut into the volcanic rock below. A faint "
            "heat rises from the opening."
        ),
        "exits": {"up": 5109, "down": 5309},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5309,
        "name": "Highridge Under-Market -- Smuggler's Stair",
        "description": (
            "A steep spiral stair descends through solid basalt into "
            "the old lava-tube network beneath Highridge. The stair "
            "is of Pekakarlik cut; the rope handrail is newer and "
            "smells strongly of oiled hemp. Heat rises steadily from "
            "below."
        ),
        "exits": {"up": 5308, "down": 5310},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5310,
        "name": "Highridge Lava-Tube -- Upper Chamber",
        "description": (
            "The stair opens into a wider natural lava-tube whose "
            "walls curve like a smooth basalt throat. The air is "
            "sharply hot; the rock itself is warm to the touch. "
            "Torches are mounted at intervals, recently trimmed. The "
            "tube continues east and branches south."
        ),
        "exits": {"up": 5309, "east": 5311, "south": 5313},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5311,
        "name": "Highridge Lava-Tube -- Kobold Watch Post",
        "description": (
            "A wider section of the tube where the Artifact-Keeper's "
            "kobold accomplices maintain a watch. A brass gong hangs "
            "on a hook; a kobold in ritual face-paint sits on a stool "
            "with a ready crossbow. Its scales are ashy gray, and it "
            "bears the sigil of a tongue-of-flame burnt into its "
            "forearm."
        ),
        "exits": {"west": 5310, "east": 5312},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5312,
        "name": "Highridge Lava-Tube -- Flamewarg Den",
        "description": (
            "An alcove off the main tube that has filled with heat-"
            "loving vermin drawn by the artifact's warmth. A pair of "
            "wolf-sized beasts with faintly-glowing orange coats lie "
            "curled on stone ledges. They are the Flamewargs of "
            "Deceiver-era blood, and the Keeper tolerates their "
            "presence because they keep kin-scouts away."
        ),
        "exits": {"west": 5311, "south": 5314},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5313,
        "name": "Highridge Lava-Tube -- Cultist Dormitory",
        "description": (
            "A more hospitable chamber where the Keeper's kobold "
            "cultists sleep and eat. Bedrolls line the walls, a low "
            "fire burns in a central hearth, and a small shrine to "
            "no named god sits in the corner. A kobold cultist in a "
            "priest's stole serves watery tea to two kobold scouts."
        ),
        "exits": {"north": 5310, "east": 5314, "south": 5315},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5314,
        "name": "Highridge Lava-Tube -- The Keeper's Study",
        "description": (
            "A scholar's workshop built into a widening of the tube, "
            "with a heavy writing-desk, stacks of notebooks, and "
            "carefully-arranged glass apparatus on a stone bench. A "
            "Half-Dómnathar in forge-scholar's robes looks up from a "
            "book. Her faintly luminous eyes, normally hidden by the "
            "academic fiction she maintains above ground, catch the "
            "lamplight openly here."
        ),
        "exits": {"north": 5312, "south": 5315, "east": 5316,
                  "down": 5317},
        "flags": ["indoor", "dangerous", "underground", "hot",
                  "boss_room"],
    },
    {
        "vnum": 5315,
        "name": "Highridge Lava-Tube -- Sanctum Approach",
        "description": (
            "A short passage between the Keeper's study and the "
            "sanctum proper. Walls glisten with silver leaf laid in "
            "complex patterns -- arcane focusing inscriptions that "
            "channel the artifact's power to the Keeper's workings. "
            "The temperature rises noticeably as one walks the "
            "passage."
        ),
        "exits": {"north": 5313, "south": 5314},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5316,
        "name": "Highridge Lava-Tube -- Translation Chamber",
        "description": (
            "A small study fitted with scribe's tools. At the desk "
            "sits an Elf in plain robes, ankles unshackled but eyes "
            "weary. He has been translating Deceiver-era spell-scripts "
            "for the Keeper for six years. He raises his head at the "
            "interruption without obvious enthusiasm. His loyalties "
            "are uncertain."
        ),
        "exits": {"west": 5314},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5317,
        "name": "Highridge Lava-Tube -- Lower Passage",
        "description": (
            "A steep-descending passage hewn by Pekakarlik hands, "
            "now lit by the distant glow of the artifact chamber "
            "below. The walls radiate uncomfortable heat. A heat-"
            "shimmer blurs vision at the passage's far end."
        ),
        "exits": {"up": 5314, "down": 5318},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5318,
        "name": "Highridge Lava-Tube -- Deep Tube",
        "description": (
            "The natural lava-tube widens into a cavern-like chamber "
            "whose floor is cracked with thin veins of still-warm "
            "basalt. Ahead, the source of the heat: a doorway-arch "
            "of Pekakarlik cut, glowing faintly amber from within. "
            "Two Dark Dwarves stand before the arch, their armor "
            "warded against heat, their axes drawn."
        ),
        "exits": {"up": 5317, "north": 5319, "south": 5320},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5319,
        "name": "Highridge Lava-Tube -- The Artifact Chamber",
        "description": (
            "A round chamber whose walls are inscribed with Pekakarlik "
            "warding-sigils, most now cracked or dulled from centuries "
            "of slow failure. At the center, set into a pedestal of "
            "smooth black stone, is the artifact: a Deceiver-made "
            "prism that glows a steady amber from within. The "
            "Keeper's channeling-apparatus surrounds the pedestal. "
            "The air here is over 120 degrees and getting hotter."
        ),
        "exits": {"south": 5318},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "hot"],
    },
    {
        "vnum": 5320,
        "name": "Highridge Lava-Tube -- Dark Dwarf Barracks",
        "description": (
            "A side-chamber that the Keeper's Dark Dwarf guards use "
            "as a barracks and mess. Their armor hangs on pegs along "
            "one wall; a long trestle-table dominates the room. A "
            "small forge-stone in one corner is kept perpetually warm "
            "for maintaining the guards' gear."
        ),
        "exits": {"north": 5318, "east": 5321, "south": 5322},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5321,
        "name": "Highridge Lava-Tube -- Forge-Warded Vault",
        "description": (
            "A secondary strongroom, its door protected by Pekakarlik "
            "heat-wards repurposed by the Keeper. Inside are crates of "
            "rare forge-metals she has siphoned from Highridge's own "
            "foundries, bar by bar, over ten years of patient theft. "
            "The Taraf-Imro scholars believe the losses are normal "
            "wastage. They are not."
        ),
        "exits": {"west": 5320},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "hot"],
    },
    {
        "vnum": 5322,
        "name": "Highridge Lava-Tube -- Secondary Chamber",
        "description": (
            "A small natural cavern the Keeper uses for experiments "
            "she does not want the translation staff to observe. A "
            "circular work-table holds instruments of various "
            "provenance; the floor is scored with concentric channels "
            "for containing spilled reagents. The chamber has been "
            "used recently -- fresh scorch-marks crisscross the stone."
        ),
        "exits": {"north": 5320, "east": 5323},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
    {
        "vnum": 5323,
        "name": "Highridge Lava-Tube -- Escape Crevasse",
        "description": (
            "A natural crevasse leading off into the deep rock of the "
            "mountain. The Keeper can descend this crevasse in an "
            "emergency to eventually emerge on the far side of "
            "Highridge, miles from the city walls. She has rehearsed "
            "the descent three times in ten years. She has not yet "
            "had to use it."
        ),
        "exits": {"west": 5322},
        "flags": ["indoor", "dangerous", "underground", "hot"],
    },
]


# ===========================================================================
# Zone K2 -- Andrio Giant Chamber Proper  (22 rooms, 5324-5345)
# ===========================================================================
# The entry is the existing 5286 Giant Chamber (dead-end stub), now
# extended downward and outward.

ANDRIO_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 5324,
        "name": "Andrio Giant Chamber -- Expedition Antechamber",
        "description": (
            "The existing Giant antechamber has been thoroughly "
            "commandeered. Silentborn-made camp-cots line the walls; "
            "writing-desks have been set up between the colossal stone "
            "columns; a rope-and-pulley lift has been rigged from the "
            "ceiling to the floor for lowering heavy gear. The "
            "expedition's banner -- an empty iron circle -- hangs from "
            "the nearest column."
        ),
        "exits": {"up": 5286, "north": 5325, "east": 5326,
                  "south": 5327, "west": 5328},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5325,
        "name": "Andrio Giant Chamber -- Supply Station",
        "description": (
            "Crates, barrels, and sealed water-vessels stacked in a "
            "rough grid. A quartermaster's clipboard hangs on a peg; "
            "the inventory is rigorous. A Silentborn loyalist sits on "
            "a crate, polishing his longsword with thoughtful care. "
            "The supplies suggest the expedition plans to remain in "
            "the undercroft for months."
        ),
        "exits": {"south": 5324, "east": 5326},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5326,
        "name": "Andrio Giant Chamber -- Expedition Leader's Camp",
        "description": (
            "The expedition's command tent, pitched in the widest "
            "part of the antechamber. Maps of the Giant undercroft, "
            "annotated in three different hands, cover the central "
            "work-table. A powerfully-built Half-Dómnathar in traveling "
            "leathers stands at the table, one hand on the pommel of "
            "a greatsword, the other tracing a line across the map. "
            "He looks up without surprise. He has been expecting this."
        ),
        "exits": {"west": 5325, "south": 5324, "east": 5329},
        "flags": ["indoor", "dangerous", "underground", "boss_room"],
    },
    {
        "vnum": 5327,
        "name": "Andrio Giant Chamber -- Porters' Quarters",
        "description": (
            "A crude lean-to of canvas draped between two Giant "
            "columns, sheltering the expedition's goblin porter-"
            "gang. The goblins are not permitted to sit on the "
            "expedition's proper cots. They are, however, fed "
            "regularly -- a precaution against mutiny that the "
            "expedition's Silentborn officers insisted on."
        ),
        "exits": {"north": 5324, "east": 5328},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5328,
        "name": "Andrio Giant Chamber -- Guard Post",
        "description": (
            "A Silentborn guard-station controlling access to the "
            "deeper undercroft. A wooden barrier has been set up "
            "across the way west, with a rope-gate to admit "
            "authorized personnel. Two Silentborn stand the watch in "
            "rotating shifts; the current pair do not speak."
        ),
        "exits": {"east": 5324, "west": 5327, "north": 5329},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5329,
        "name": "Andrio Giant Chamber -- Descent Shaft",
        "description": (
            "A vertical shaft descends through the Giant-cut stone, "
            "lined with Pekakarlik iron rungs the expedition's Dark "
            "Dwarves have installed for safer climbing. The shaft was "
            "cut by the Giants themselves for access to the deeper "
            "undercroft. It is wider than a natural shaft would need "
            "to be, because Giants were larger than anyone currently "
            "living."
        ),
        "exits": {"south": 5328, "west": 5326, "down": 5330},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5330,
        "name": "Andrio Giant Chamber -- Giant Colonnade",
        "description": (
            "A vast hall whose columns are each the span of two grown "
            "people across their base, arranged in rows that suggest "
            "a temple or court of giants. The ceiling is lost in "
            "shadow far above. The hall has a ceremonial quality: "
            "somewhere at the far end, a processional dais for beings "
            "of enormous size is dimly visible."
        ),
        "exits": {"up": 5329, "north": 5331, "east": 5333,
                  "south": 5334},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5331,
        "name": "Andrio Giant Chamber -- Collapsed Section",
        "description": (
            "A portion of the colonnade where the ceiling has fallen "
            "in, a tumbled pile of dressed stone and broken columns. "
            "The expedition's Dark Dwarves have begun clearing a path "
            "around the fall. Their tools -- picks, braces, "
            "measuring-cords -- are neatly stacked at the work-site. "
            "No workers are currently present."
        ),
        "exits": {"south": 5330, "east": 5332},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 5332,
        "name": "Andrio Giant Chamber -- The Sand Wraith's Lair",
        "description": (
            "A side-chamber that the Dark Dwarves accidentally broke "
            "through two weeks ago. Inside, something ancient has "
            "awakened: a Sand Wraith of Deceiver-War vintage, "
            "desiccated centuries ago but now aware and hostile. The "
            "air here draws moisture from any lungs that breathe it. "
            "The Dark Dwarves have since sealed the chamber, but the "
            "seal is imperfect."
        ),
        "exits": {"west": 5331},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 5333,
        "name": "Andrio Giant Chamber -- Dark Dwarf Tunnel Camp",
        "description": (
            "A secondary work-camp for the expedition's Dark Dwarf "
            "tunnelers, off the main colonnade. Braces of dressed "
            "timber, iron wedges, and small steam-hammers rest in "
            "neat piles. Two Dark Dwarf warriors sit on the floor, "
            "sharing a meal of cold meat and harder bread."
        ),
        "exits": {"west": 5330, "south": 5335},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5334,
        "name": "Andrio Giant Chamber -- Pillar of Oaths",
        "description": (
            "A single smooth-cut pillar stands in the colonnade hall, "
            "its surface carved from base to vanishing-point with "
            "names in Giant-script. This is a memorial-column, each "
            "name a Giant who swore an oath and kept it. The "
            "expedition's translator is here somewhere along its "
            "height: the column lists the seven Giant defenders who "
            "buried the artifact players have come to retrieve."
        ),
        "exits": {"north": 5330},
        "flags": ["indoor", "underground"],
    },
    {
        "vnum": 5335,
        "name": "Andrio Giant Chamber -- Preparation Hall",
        "description": (
            "A secondary chamber the expedition uses for preparation-"
            "rituals before descending into the deeper vaults. A "
            "shallow pool of clean water; a folding-rack of ritual "
            "robes; a shelf of carefully-labeled oils and unguents. "
            "A Silentborn battle-priest stands at a worktable, laying "
            "out equipment for a coming ritual."
        ),
        "exits": {"north": 5333, "east": 5336},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5336,
        "name": "Andrio Giant Chamber -- Deeper Stair",
        "description": (
            "A long stair of Giant-scaled steps -- each riser knee-"
            "high to a human -- descends into the deeper vaults. The "
            "expedition has laid wooden step-ladders over the worst "
            "sections to make them passable. Torchlight below "
            "suggests the stair opens into another large chamber."
        ),
        "exits": {"west": 5335, "down": 5337},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5337,
        "name": "Andrio Giant Chamber -- Giant Archive",
        "description": (
            "A vaulted hall lined with slate tablets set into the "
            "walls. The tablets are Giant-sized; reading them is a "
            "physical challenge as well as a scholarly one. They "
            "record -- the expedition's translator has confirmed -- "
            "the Giants' ancient war with the Deceivers, and the "
            "burial-rite for the artifact buried in the deepest "
            "vault."
        ),
        "exits": {"up": 5336, "east": 5338},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5338,
        "name": "Andrio Giant Chamber -- Vault Approach",
        "description": (
            "A narrow passage compared to the Giant halls above, dug "
            "by the expedition's Dark Dwarves through a previously-"
            "unbreached section of stone. The walls show fresh tool-"
            "marks. The passage terminates ahead at a great stone "
            "door incised with Giant-script warnings that the "
            "translator refused to read aloud."
        ),
        "exits": {"west": 5337, "north": 5339},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 5339,
        "name": "Andrio Giant Chamber -- The Seal Chamber",
        "description": (
            "A circular hall whose floor bears a complex interlocking "
            "seal of seven overlapping sigils -- one for each of the "
            "Giant defenders named on the Pillar of Oaths. The seal "
            "has been partially breached: the expedition's dark-"
            "workings have burnt through three of the seven sigils. "
            "Four remain intact. Doing something about those four is "
            "the expedition's current objective."
        ),
        "exits": {"south": 5338, "east": 5340, "north": 5342},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 5340,
        "name": "Andrio Giant Chamber -- Sigil Study",
        "description": (
            "A small alcove off the Seal Chamber where the expedition's "
            "research team studies the remaining sigils. A portable "
            "desk holds detailed sketches, theories, and a small "
            "stack of Deceiver-era reagents purchased at considerable "
            "cost from Spur Tower quartermasters. The work is careful "
            "and slow."
        ),
        "exits": {"west": 5339, "east": 5341},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5341,
        "name": "Andrio Giant Chamber -- Researcher's Cell",
        "description": (
            "A small private cell for the Half-Dómnathar expedition-"
            "leader's personal use, spartanly furnished. A cot, a "
            "writing-desk, a weapon-stand. A locked document-case "
            "holds his private orders -- sealed under the House "
            "Leader's personal sign, a detail the expedition's rank-"
            "and-file do not know."
        ),
        "exits": {"west": 5340},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 5342,
        "name": "Andrio Giant Chamber -- The Dread Wraith's Hall",
        "description": (
            "Beyond a barricade of tumbled stone -- the four intact "
            "sigils still gleaming dimly -- lies a vast hall the "
            "expedition has not yet entered. At its center, dimly "
            "visible, a tall spectral figure stands vigil: a Giant "
            "general who died defending the seal, three millennia ago, "
            "and whose hatred for Dómnathar kind has only grown in "
            "death. Its voice, when it speaks, will drop the "
            "temperature of the air by twenty degrees."
        ),
        "exits": {"south": 5339, "north": 5343},
        "flags": ["indoor", "dangerous", "underground", "boss_room"],
    },
    {
        "vnum": 5343,
        "name": "Andrio Giant Chamber -- The Relic Vault",
        "description": (
            "Beyond the Dread Wraith's vigil lies the Giant-built "
            "vault proper. On a low pedestal of black stone rests the "
            "artifact: a small cube of dark metal, no larger than a "
            "clenched fist, carved on every face with Deceiver-era "
            "script. Even from across the chamber, its presence makes "
            "the teeth ache. Three millennia of Giant guard-magic "
            "have, just barely, held."
        ),
        "exits": {"south": 5342, "north": 5344},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 5344,
        "name": "Andrio Giant Chamber -- Beyond the Seal",
        "description": (
            "Past the Relic Vault, a low corridor leads into darkness "
            "the expedition has not mapped. A small stone door in the "
            "far wall bears a Giant-script inscription too worn to "
            "fully read. Beyond it, according to the Archive tablets, "
            "lies 'the rest of what they buried.' The expedition has "
            "not risked opening the door. Not yet."
        ),
        "exits": {"south": 5343},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 5345,
        "name": "Andrio Giant Chamber -- The Old King's Tomb",
        "description": (
            "A secondary vault off the Seal Chamber, built into "
            "Giant-cut alcoves in the wall, housing the sarcophagus "
            "of one of the Seven -- a Giant defender named on the "
            "Pillar of Oaths. His stone effigy shows him in full "
            "battle-harness, greatsword across his chest. His face "
            "is serene. The sarcophagus has been opened; his grave-"
            "goods have been taken."
        ),
        "exits": {"west": 5339},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
]


# ===========================================================================
# Outbound exits from existing rooms
# ===========================================================================

NEW_EXITS = [
    # Highridge Scorchmarket South Stalls -> Hidden Cellar
    (5109, "down", 5308),
    # Andrio Giant Chamber (existing stub) -> Expedition Antechamber
    (5286, "down", 5324),
]


# ===========================================================================
# Mob spawns (vnums 4000-4021)
# ===========================================================================

def _bestiary_lookup(name, bestiary):
    hits = [b for b in bestiary if b.get("name") == name]
    if not hits:
        raise KeyError(f"bestiary missing: {name}")
    return hits[0]


def _spawn(vnum, bestiary_name, room_vnum, *, bestiary,
           name_override=None, loot=None):
    src = _bestiary_lookup(bestiary_name, bestiary)
    new = {k: v for k, v in src.items() if k != "vnum"}
    new["vnum"] = vnum
    new["room_vnum"] = room_vnum
    if name_override:
        new["name"] = name_override
    if loot is not None:
        new["loot_table"] = loot
    return new


LT_COINS      = [{"vnum": 2,   "chance": 0.25}]
LT_TORCH      = [{"vnum": 203, "chance": 0.4}]
LT_POTION     = [{"vnum": 301, "chance": 0.2}]
LT_MW_SWORD   = [{"vnum": 700, "chance": 0.35}]
LT_MW_ARMOR   = [{"vnum": 701, "chance": 0.30}]
LT_SIGNET     = [{"vnum": 702, "chance": 0.30}]
LT_WARDAMUL   = [{"vnum": 703, "chance": 0.30}]
LT_DARKIRON_D = [{"vnum": 705, "chance": 0.35}]
LT_FIRECLOAK  = [{"vnum": 706, "chance": 0.50}]
LT_VOIDHAMMER = [{"vnum": 707, "chance": 0.45}]
LT_TABLET     = [{"vnum": 708, "chance": 0.50}]
LT_DARKIRON_L = [{"vnum": 709, "chance": 0.45}]
LT_COLLAR     = [{"vnum": 710, "chance": 0.55}]
LT_VOIDROD    = [{"vnum": 711, "chance": 0.70}]


SPAWN_SPEC = [
    # --- Highridge (4000-4009) -------------------------------------------
    (4000, "Kobold Scout (Sorcerer 1)",              5311,
            LT_TORCH + LT_FIRECLOAK),
    (4001, "Kobold Fire-Sorcerer (Sorcerer 5)",      5311,
            LT_FIRECLOAK + LT_MW_SWORD + LT_POTION),
    (4002, "Flamewarg Cult Initiate (Sorcerer 3, Human)", 5312,
            LT_FIRECLOAK + LT_DARKIRON_D),
    (4003, "Kobold Cultist (Cleric 2)",              5313,
            LT_FIRECLOAK + LT_POTION),
    (4004, "Kobold Scout (Sorcerer 1)",              5313, LT_COINS),
    (4005, "Kobold Scout (Sorcerer 1)",              5313, LT_TORCH),
    (4006, "Half-Dómnathar Artifact-Keeper (Wizard 6)", 5314,
            LT_VOIDHAMMER + LT_VOIDROD + LT_COLLAR + LT_TABLET + LT_WARDAMUL),
    (4007, "Dark Dwarf Fireforged (Fighter 5)",      5318,
            LT_DARKIRON_L + LT_MW_ARMOR + LT_FIRECLOAK),
    (4008, "Dark Dwarf Fireforged (Fighter 5)",      5318,
            LT_DARKIRON_L + LT_MW_ARMOR),
    (4009, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 5316,
            LT_MW_SWORD + LT_TABLET),

    # --- Andrio (4010-4021) ----------------------------------------------
    (4010, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 5325,
            LT_MW_ARMOR + LT_COLLAR),
    (4011, "Half-Dómnathar Expedition-Leader (Fighter 6 / Sorcerer 3)", 5326,
            LT_MW_SWORD + LT_VOIDHAMMER + LT_MW_ARMOR + LT_TABLET + LT_COLLAR),
    (4012, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 5326,
            LT_MW_SWORD + LT_DARKIRON_L),
    (4013, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 5326,
            LT_MW_ARMOR + LT_COLLAR),
    (4014, "Kobold Scout (Sorcerer 1)",              5327, LT_COINS),
    (4015, "Kobold Scout (Sorcerer 1)",              5327, LT_TORCH),
    (4016, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 5328,
            LT_MW_SWORD),
    (4017, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 5328,
            LT_DARKIRON_L),
    (4018, "Dark Dwarf Warrior (Fighter 3)",         5333,
            LT_DARKIRON_L + LT_MW_ARMOR),
    (4019, "Dark Dwarf Warrior (Fighter 3)",         5333,
            LT_DARKIRON_L),
    (4020, "Sand Wraith",                            5332,
            LT_WARDAMUL + LT_SIGNET),
    (4021, "Silentborn Battle-Priest (Cleric 5)",    5335,
            LT_VOIDHAMMER + LT_MW_ARMOR + LT_POTION),
    (4022, "Dread Wraith",                           5342,
            LT_VOIDROD + LT_WARDAMUL + LT_SIGNET + LT_MW_SWORD),
]


# ===========================================================================
# Merge
# ===========================================================================

def _read(p):
    with open(p,"r",encoding="utf-8") as f: return json.load(f)
def _write(p,o):
    tmp = p + ".tmp"
    with open(tmp,"w",encoding="utf-8") as f:
        json.dump(o, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def merge_rooms():
    path = os.path.join(DATA, "areas", "Kinsweave.json")
    rooms = _read(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0
    for r in HIGHRIDGE_ROOMS + ANDRIO_ROOMS:
        if r["vnum"] in existing: continue
        rooms.append(r); existing.add(r["vnum"]); added += 1
    by_vnum = {r["vnum"]: r for r in rooms}
    wired = 0
    for src_v, direction, dest_v in NEW_EXITS:
        r = by_vnum.get(src_v)
        if r is None: continue
        exits = r.setdefault("exits", {})
        if exits.get(direction) == dest_v: continue
        if direction in exits and exits[direction] != dest_v:
            print(f"  WARN: {src_v} already has '{direction}' to {exits[direction]}; skipping")
            continue
        exits[direction] = dest_v; wired += 1
    _write(path, rooms)
    print(f"  Kinsweave.json: +{added} rooms, +{wired} exits (total {len(rooms)})")


def merge_mobs():
    mobs_path = os.path.join(DATA, "mobs.json")
    bestiary = _read(os.path.join(DATA, "mobs_bestiary.json"))
    mobs = _read(mobs_path)
    existing = {m.get("vnum") for m in mobs}
    added = 0
    for vnum, best_name, room_vnum, loot in SPAWN_SPEC:
        if vnum in existing: continue
        try:
            mobs.append(_spawn(vnum, best_name, room_vnum,
                               bestiary=bestiary, loot=loot))
            added += 1
        except KeyError as e:
            print(f"  WARN: {e}")
    _write(mobs_path, mobs)
    print(f"  mobs.json: +{added} new spawns (total {len(mobs)})")


def main() -> int:
    print("Building Kinsweave Deceiver zones:")
    merge_rooms()
    merge_mobs()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
