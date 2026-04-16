"""Build the Twin Rivers Deceiver zones (the final region).

  * Zone W1 -- Gorge-Bridge Infiltrator Cell (14 rooms, 10307-10320)
    A Half-Dómnathar Broker running a long-embedded smuggling cell
    beneath Liraveth's Western Bridge Head, moving Deceiver artifacts
    upriver from the Deepwater Marches to Twin Rivers sympathizers.
    Levels 5-8.

  * Zone W2 -- Unstrung Philosophers' Refuge (20 rooms, 10321-10340)
    The ideologue-cult headquarters concealed in the Riverwind Heights.
    Not formally Dómnathar, but philosophically aligned and
    functionally supplying the Spur Tower with trained assassins.
    Levels 9-12, boss CR 10.

Idempotent. Run:
    python scripts/build_twinrivers_deceiver_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ===========================================================================
# Zone W1 -- Gorge-Bridge Infiltrator Cell  (14 rooms, 10307-10320)
# ===========================================================================

INFILTRATOR_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 10307,
        "name": "Bridge Cellar -- Stone Stair",
        "description": (
            "A stone stair descends beneath Liraveth's Western Bridge "
            "Head, past the normal cellar-level of the river-house "
            "above and into the old flood-vaults the river-factor "
            "claims are abandoned. They are not abandoned. The stair "
            "ends in a warm, well-lit antechamber whose stone has been "
            "recently re-pointed."
        ),
        "exits": {"up": 10222, "north": 10308, "east": 10309},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10308,
        "name": "Infiltrator Cell -- Smuggler's Vault",
        "description": (
            "A long vaulted chamber stacked with sealed crates marked "
            "for various buyers up and down the river. The inventory "
            "is impressive: Deceiver spell-foci in padded velvet; a "
            "wrapped bundle of Silentborn-made suppressor-collars; "
            "several sealed scroll-cases. Two hobgoblin 'caravan "
            "guards' lounge by the door, reading aloud from a ledger."
        ),
        "exits": {"south": 10307, "east": 10311},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10309,
        "name": "Infiltrator Cell -- Merchant Facade",
        "description": (
            "A front-office appointed as any reputable Eruskan "
            "river-factor's cellar-office would be: a writing-desk, "
            "shelves of ledger-books, a low stool for supplicants. "
            "Three Silentborn in merchant dress stand at the desk, "
            "reviewing papers with the quiet competence of people "
            "who have been at this work for years."
        ),
        "exits": {"west": 10307, "north": 10311, "east": 10312,
                  "south": 10310},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10310,
        "name": "Infiltrator Cell -- Porter's Quarters",
        "description": (
            "A low-ceilinged bunk-room for the cell's goblin porters "
            "-- the workers who actually move the crates up and down "
            "river at night. Simple bedrolls, a shared chest, a "
            "cluttered pegboard of duty-schedules. The goblins here "
            "are paid fairly, which is unusual enough that they are "
            "fiercely loyal."
        ),
        "exits": {"north": 10309, "east": 10318},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10311,
        "name": "Infiltrator Cell -- River Dock Access",
        "description": (
            "A concealed passage leading from the smuggler's vault "
            "out to a hidden dock beneath the bridge-head. Goods "
            "move through this passage by the cart-load, twice per "
            "week, by night. A small iron grate opens onto the river "
            "at the passage's far end."
        ),
        "exits": {"west": 10308, "south": 10309, "east": 10319},
        "flags": ["indoor", "dangerous", "underground", "water"],
    },
    {
        "vnum": 10312,
        "name": "Infiltrator Cell -- Ledger Room",
        "description": (
            "A proper accounting-office: high desks, tall stools, "
            "banks of pigeon-holes holding invoices and receipts. "
            "The cell's actual inventory is tracked here, in plain "
            "Kin-script, behind a veneer of ordinary river-trade "
            "paperwork. To a random inspector, everything would "
            "check out."
        ),
        "exits": {"west": 10309, "east": 10313, "south": 10318},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10313,
        "name": "Infiltrator Cell -- The Broker's Office",
        "description": (
            "A private office of good furniture and better taste. The "
            "desk is dark walnut; the rug is imported; the brandy on "
            "the sideboard is a Westerlin vintage of some note. At "
            "the desk sits a handsome, immaculately-dressed figure "
            "the Liraveth mercantile community knows as Madam Cerran "
            "the River-Factor. Her ears, if you look closely, are "
            "very slightly more pointed than a full Eruskan's."
        ),
        "exits": {"west": 10312, "north": 10314, "east": 10315,
                  "south": 10316},
        "flags": ["indoor", "dangerous", "underground", "boss_room"],
    },
    {
        "vnum": 10314,
        "name": "Infiltrator Cell -- Advisor's Room",
        "description": (
            "A smaller private chamber used by the Broker's personal "
            "advisor -- an elderly Elf whose accent is from nowhere "
            "living Kin would recognize. He was smuggled through "
            "the Silence Breach as a young man, has served the "
            "Shattered Host for decades, and handles the coded "
            "correspondence with Dómnathar cells east of the river."
        ),
        "exits": {"south": 10313},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10315,
        "name": "Infiltrator Cell -- Strongbox Vault",
        "description": (
            "A small reinforced room the Broker uses to store the "
            "cell's liquid reserves: three locked iron-bound strong-"
            "boxes holding Kin coinage, Dómnathar trade-bars of pure "
            "silver, and a fourth box containing emergency travel-"
            "papers in four different names."
        ),
        "exits": {"west": 10313},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 10316,
        "name": "Infiltrator Cell -- Hidden Cache",
        "description": (
            "A concealed alcove behind a pivot-panel in the Broker's "
            "office. Inside, wrapped in oilcloth, are the items the "
            "Broker does not declare even to the Spur Tower: a "
            "bundle of letters in her own hand (copies of reports "
            "she has made), a sheaf of coded names, and a small "
            "Deceiver-era device of unknown purpose."
        ),
        "exits": {"north": 10313, "east": 10317},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 10317,
        "name": "Infiltrator Cell -- Upriver Gate",
        "description": (
            "A small iron-gated alcove leading to a concealed "
            "staircase up to a hidden exit somewhere in Liraveth's "
            "storage-quarter. The gate is unlocked by a mechanism "
            "operated from the Broker's desk. She uses this exit "
            "when she wishes to move through the city without being "
            "observed."
        ),
        "exits": {"west": 10316},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10318,
        "name": "Infiltrator Cell -- Guard Post",
        "description": (
            "A modest sentry-post at the junction of the porters' "
            "quarters and the ledger room. A Silentborn in neutral "
            "traveling-clothes sits at a small table, reading a "
            "thin volume on Kin etiquette. His short-sword leans "
            "against the wall beside him, close enough to reach."
        ),
        "exits": {"north": 10312, "west": 10310},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 10319,
        "name": "Infiltrator Cell -- Contraband Store",
        "description": (
            "A smaller strongroom holding the cell's most sensitive "
            "contraband: two unopened Deceiver-era crystal reliquaries, "
            "a rolled tapestry bearing the Shattered Host sigil, and "
            "a sealed clay jar whose contents no one in the cell has "
            "opened because the Broker has not yet told them what is "
            "inside."
        ),
        "exits": {"west": 10311, "east": 10320},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
    {
        "vnum": 10320,
        "name": "Infiltrator Cell -- Escape Trapdoor",
        "description": (
            "A trapdoor in the floor of the contraband store opens "
            "onto a narrow sloping passage that emerges -- eventually "
            "-- in a stand of reeds on the far side of the Great "
            "River. It is the Broker's final insurance. It has not "
            "been used."
        ),
        "exits": {"west": 10319},
        "flags": ["indoor", "dangerous", "underground"],
    },
]


# ===========================================================================
# Zone W2 -- Unstrung Philosophers' Refuge  (20 rooms, 10321-10340)
# ===========================================================================

UNSTRUNG_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 10321,
        "name": "Unstrung Refuge -- Hidden Path",
        "description": (
            "The Druidic Overlook's western edge conceals a narrow "
            "trail descending along the cliff-face, visible only to "
            "someone who knows precisely where to look. The trail "
            "ends at a carved stone threshold into the hillside -- "
            "an entrance disguised as a natural cave-mouth."
        ),
        "exits": {"east": 10418, "west": 10322},
        "flags": ["outdoor", "dangerous"],
    },
    {
        "vnum": 10322,
        "name": "Unstrung Refuge -- Greeting Hall",
        "description": (
            "Past the stone threshold, a welcoming hall opens out, "
            "polished stone floor and whitewashed walls hung with "
            "modest tapestries of Hareem's rose-in-sword. Two "
            "acolytes in undyed robes stand at the welcome-desk, "
            "their sleeves bearing the small cut-string sigil. "
            "Their greeting, to unannounced visitors, is polite but "
            "firm: 'Your purpose, friend?'"
        ),
        "exits": {"east": 10321, "north": 10323, "south": 10325,
                  "west": 10331},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10323,
        "name": "Unstrung Refuge -- Philosophy Classroom",
        "description": (
            "A long hall with rows of low reading-desks facing a "
            "raised dais. Currently empty; the morning lecture "
            "concluded an hour ago. Slate boards on the walls bear "
            "the lecture's outline -- a reading of Hareem's Cut-"
            "String doctrine interleaved with references to the "
            "Deceiver's Feat. The two are presented as philosophically "
            "identical."
        ),
        "exits": {"south": 10322, "north": 10324, "east": 10327},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10324,
        "name": "Unstrung Refuge -- Meditation Chamber",
        "description": (
            "A circular room with cushions around the walls and a "
            "small brazier in the center, currently burning a light "
            "incense of frankincense and something harder to name. "
            "A Half-Dómnathar priest in blackened leather kneels in "
            "meditation -- or appears to. His breathing is measured. "
            "His eyes are open."
        ),
        "exits": {"south": 10323, "east": 10326},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10325,
        "name": "Unstrung Refuge -- Practice Ring",
        "description": (
            "A sand-floored circle sunk below the surrounding "
            "floor-level for easier observation. Racked along the "
            "walls are practice-weapons: wooden swords, padded "
            "daggers, weighted sparring-rods. Two young cultists "
            "currently spar in the ring, their instructor calling "
            "corrections from the ringside."
        ),
        "exits": {"north": 10322, "east": 10333, "south": 10334},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10326,
        "name": "Unstrung Refuge -- Scribe's Hall",
        "description": (
            "A long narrow room where the Refuge's scribes copy out "
            "doctrinal texts for distribution to the congregation in "
            "town. High writing-desks, small reading-lamps, careful "
            "pots of black and red ink. Several works in progress "
            "are laid out on the desks; their contents, read closely, "
            "blur the line between Hareem's scriptures and "
            "Dómnathar propaganda."
        ),
        "exits": {"west": 10324, "south": 10327, "east": 10331},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10327,
        "name": "Unstrung Refuge -- The Philosopher's Study",
        "description": (
            "The Philosopher-in-Residence's private study. Walls of "
            "bound books; a reading-table piled with Dómnathar and "
            "Kin texts in equal proportion; a low divan for "
            "favored students; a silver decanter of excellent wine. "
            "At the table, the Philosopher himself looks up with the "
            "warm, practiced smile of a teacher recognizing the "
            "potential for a promising new student."
        ),
        "exits": {"west": 10323, "north": 10326, "south": 10328},
        "flags": ["indoor", "dangerous", "cult", "boss_room"],
    },
    {
        "vnum": 10328,
        "name": "Unstrung Refuge -- Favored Student's Chamber",
        "description": (
            "A comfortable small cell adjoining the Philosopher's "
            "study, reserved for the student he currently finds "
            "most promising. Simple bedding, a writing-desk, a "
            "bookshelf with the student's own copies of the core "
            "texts. Currently occupied by a Silentborn student -- "
            "quiet, attentive, deeply loyal."
        ),
        "exits": {"north": 10327, "east": 10329},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10329,
        "name": "Unstrung Refuge -- Second Student's Chamber",
        "description": (
            "A second small cell, mirror of the first, occupied by "
            "another advanced student. This one is also Silentborn. "
            "The Philosopher's best students are always Silentborn. "
            "The congregation in town does not know this, but one "
            "day, they will."
        ),
        "exits": {"west": 10328, "south": 10330},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10330,
        "name": "Unstrung Refuge -- Masters' Table",
        "description": (
            "A small dining-hall where the Refuge's teachers and "
            "ranking students take meals together. The table is set "
            "for six but currently empty. The provisions, laid out "
            "on a sideboard, are excellent: good bread, strong "
            "cheese, a handsome roast. The cooking is done by "
            "servants who know better than to ask questions."
        ),
        "exits": {"north": 10329, "east": 10332},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10331,
        "name": "Unstrung Refuge -- Library of Doctrine",
        "description": (
            "The Refuge's main library: three walls of shelving "
            "floor-to-ceiling, the fourth a tall arched window "
            "looking east over the Riverwind Heights. A reading "
            "table; a globe; a rack of reading-lamps. The library "
            "is quiet. The collection is uncommonly good, especially "
            "its shelf of Dómnathar-era philosophical texts."
        ),
        "exits": {"east": 10322, "west": 10326, "south": 10337},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10332,
        "name": "Unstrung Refuge -- Guest Suite",
        "description": (
            "A large guest-suite currently occupied by a Dark Dwarf "
            "dignitary visiting from the Marches to discuss weapons-"
            "sales arrangements. His quarters are spartan by dwarven "
            "standards but surprisingly well-appointed by Kin ones: "
            "a fine writing-desk, a half-read book on his cot, a "
            "standing weapons-rack holding a work-axe of unusual "
            "craftsmanship."
        ),
        "exits": {"west": 10330, "south": 10334},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10333,
        "name": "Unstrung Refuge -- Training Hall of Shadow",
        "description": (
            "A larger room than the practice ring, lit only by narrow "
            "skylights that cast bars of dim light across the floor. "
            "The hall is used to train the Refuge's advanced "
            "students in the more discrete arts. A Silentborn "
            "assassin stands in the deepest shadow along the east "
            "wall, running through a forms-drill with a real blade."
        ),
        "exits": {"west": 10325, "south": 10336},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10334,
        "name": "Unstrung Refuge -- Shrine of the Feat",
        "description": (
            "A small shrine set within the main building, ostensibly "
            "to Hareem of the Cut-String, whose rose-and-sword "
            "emblem hangs above the altar. Below the emblem, however, "
            "engraved into the altar-stone itself, is a second "
            "symbol: an iron circle, empty. Whoever kneels here "
            "prays to both faiths simultaneously."
        ),
        "exits": {"north": 10325, "east": 10332, "south": 10335},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10335,
        "name": "Unstrung Refuge -- Ritual Chamber",
        "description": (
            "A stone-walled room reserved for the Refuge's more "
            "intimate rituals. A carved stone basin at the center "
            "holds water that is uncomfortably still. A human in "
            "cultist robes tends the basin, her face scarred with "
            "Flamewarg burns. She is the only full human in "
            "attendance today, and she is the least loyal to any "
            "Kin authority of anyone in the building."
        ),
        "exits": {"north": 10334, "east": 10336},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10336,
        "name": "Unstrung Refuge -- Weapons Cache",
        "description": (
            "A locked strongroom holding the Refuge's 'discrete' "
            "armament -- the weapons the students use in the Hall "
            "of Shadow and, eventually, in the field. Racks of "
            "dark-iron knives, crossbows with enclosed triggers, "
            "poisoned bolts in labeled cases. The locks are "
            "excellent."
        ),
        "exits": {"north": 10333, "west": 10335},
        "flags": ["indoor", "dangerous", "trapped", "cult"],
    },
    {
        "vnum": 10337,
        "name": "Unstrung Refuge -- Hidden Archive",
        "description": (
            "A concealed library behind a pivot-shelf in the main "
            "library. Where the public collection holds Hareem's "
            "scriptures with subtle Dómnathar interpolations, this "
            "archive holds the raw Dómnathar source-texts, in the "
            "original script, together with the Refuge's complete "
            "correspondence with the Spur Tower."
        ),
        "exits": {"north": 10331, "east": 10338},
        "flags": ["indoor", "dangerous", "trapped", "cult"],
    },
    {
        "vnum": 10338,
        "name": "Unstrung Refuge -- Conclave Hall",
        "description": (
            "A small round hall with seven carved chairs in a circle. "
            "The Refuge's ranking members gather here once per year "
            "to decide doctrine and operations. The chairs are "
            "numbered, each by the rank of its occupant. The First "
            "Chair is larger than the others and belongs to the "
            "Philosopher-in-Residence."
        ),
        "exits": {"west": 10337, "south": 10339},
        "flags": ["indoor", "dangerous", "cult"],
    },
    {
        "vnum": 10339,
        "name": "Unstrung Refuge -- Deep Meditation Cells",
        "description": (
            "A row of small individual cells for students undergoing "
            "extended meditation-retreats. Each cell contains only a "
            "mat, a small brass lamp, and a wall-shelf for a single "
            "book. Three cells are currently occupied by silent "
            "students; the rest are empty and dim."
        ),
        "exits": {"north": 10338, "south": 10340},
        "flags": ["indoor", "cult"],
    },
    {
        "vnum": 10340,
        "name": "Unstrung Refuge -- Escape Ladder",
        "description": (
            "A concealed iron ladder climbs from the bottom of the "
            "meditation cells up through solid rock to an exit "
            "somewhere high on the Riverwind Heights cliff-face. "
            "The ladder is well-maintained and the upper hatch "
            "opens readily. The Philosopher has climbed this ladder "
            "three times in his career: once as practice, twice in "
            "earnest."
        ),
        "exits": {"north": 10339},
        "flags": ["indoor", "dangerous"],
    },
]


# ===========================================================================
# Outbound exits from existing rooms
# ===========================================================================

NEW_EXITS = [
    (10222, "down", 10307),  # Liraveth Western Bridge Head -> Cellar
    (10418, "west", 10321),  # Druidic Overlook -> Hidden Path
]


# ===========================================================================
# Mob spawns (vnums 4200-4221)
# ===========================================================================

def _bestiary_lookup(name, bestiary):
    hits = [b for b in bestiary if b.get("name") == name]
    if not hits: raise KeyError(f"bestiary missing: {name}")
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
LT_POTION     = [{"vnum": 301, "chance": 0.2}]
LT_MW_SWORD   = [{"vnum": 700, "chance": 0.35}]
LT_MW_ARMOR   = [{"vnum": 701, "chance": 0.30}]
LT_SIGNET     = [{"vnum": 702, "chance": 0.30}]
LT_WARDAMUL   = [{"vnum": 703, "chance": 0.30}]
LT_DARKIRON_D = [{"vnum": 705, "chance": 0.35}]
LT_FIRECLOAK  = [{"vnum": 706, "chance": 0.35}]
LT_VOIDHAMMER = [{"vnum": 707, "chance": 0.45}]
LT_TABLET     = [{"vnum": 708, "chance": 0.55}]
LT_DARKIRON_L = [{"vnum": 709, "chance": 0.45}]
LT_COLLAR     = [{"vnum": 710, "chance": 0.55}]
LT_VOIDROD    = [{"vnum": 711, "chance": 0.70}]


SPAWN_SPEC = [
    # --- Gorge-Bridge Infiltrator Cell (4200-4209) -----------------------
    (4200, "Hobgoblin Sergeant (Fighter 2)",           10308,
            LT_MW_ARMOR + LT_DARKIRON_L),
    (4201, "Hobgoblin Sergeant (Fighter 2)",           10308,
            LT_MW_ARMOR + LT_COINS),
    (4202, "Silentborn Loyalist (Warrior 3 / Rogue 1)",10309,
            LT_MW_SWORD + LT_COLLAR),
    (4203, "Silentborn Loyalist (Warrior 3 / Rogue 1)",10309,
            LT_MW_SWORD + LT_TABLET),
    (4204, "Silentborn Loyalist (Warrior 3 / Rogue 1)",10309,
            LT_MW_ARMOR),
    (4205, "Half-Dómnathar Broker (Bard 5 / Rogue 2)", 10313,
            LT_MW_SWORD + LT_VOIDHAMMER + LT_TABLET + LT_SIGNET + LT_COINS),
    (4206, "Dómnathar Infiltrator (Rogue 6 / Fighter 2)", 10314,
            LT_MW_SWORD + LT_COLLAR + LT_TABLET + LT_WARDAMUL),
    (4207, "Silentborn Loyalist (Warrior 3 / Rogue 1)",10318,
            LT_MW_SWORD + LT_COINS),
    (4208, "Flamewarg Cult Initiate (Sorcerer 3, Human)",10310,
            LT_FIRECLOAK + LT_POTION),

    # --- Unstrung Refuge (4209-4221) -------------------------------------
    (4209, "Flamewarg Cult Initiate (Sorcerer 3, Human)",10322,
            LT_FIRECLOAK + LT_POTION),
    (4210, "Flamewarg Cult Initiate (Sorcerer 3, Human)",10322,
            LT_FIRECLOAK + LT_DARKIRON_D),
    (4211, "Half-Dómnathar Battle-Priest (Cleric 7)", 10324,
            LT_VOIDHAMMER + LT_MW_ARMOR + LT_POTION),
    (4212, "Half-Dómnathar Philosopher (Bard 8)",    10327,
            LT_MW_SWORD + LT_VOIDROD + LT_COLLAR + LT_TABLET + LT_WARDAMUL),
    (4213, "Silentborn Loyalist (Warrior 3 / Rogue 1)",10328,
            LT_MW_SWORD + LT_COLLAR),
    (4214, "Silentborn Loyalist (Warrior 3 / Rogue 1)",10329,
            LT_MW_ARMOR + LT_COLLAR),
    (4215, "Dark Dwarf Fireforged (Fighter 5)",      10332,
            LT_DARKIRON_L + LT_MW_ARMOR + LT_FIRECLOAK),
    (4216, "Silentborn Assassin (Rogue 5 / Assassin 2)",10333,
            LT_MW_SWORD + LT_POTION + LT_COLLAR + LT_TABLET),
    (4217, "Flamewarg Cult Initiate (Sorcerer 3, Human)",10335,
            LT_FIRECLOAK + LT_POTION + LT_SIGNET),
    (4218, "Silentborn Researcher (Wizard 4)",       10336,
            LT_POTION + LT_TABLET),
    (4219, "Silentborn Researcher (Wizard 4)",       10337,
            LT_TABLET + LT_POTION),
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
    path = os.path.join(DATA, "areas", "TwinRivers.json")
    rooms = _read(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0
    for r in INFILTRATOR_ROOMS + UNSTRUNG_ROOMS:
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
    print(f"  TwinRivers.json: +{added} rooms, +{wired} exits (total {len(rooms)})")


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
    print("Building Twin Rivers Deceiver zones:")
    merge_rooms()
    merge_mobs()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
