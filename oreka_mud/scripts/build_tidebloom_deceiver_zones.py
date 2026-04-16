"""Build the Tidebloom Reach Deceiver zones.

  * Zone T1 -- Ashen Hollows Raider Camp (14 rooms, 6251-6264)
    Goblin squatters in the Foxfen ruins led by a charismatic Gate-
    refugee bandit-lord (using the Half-Dómnathar Broker stat line),
    with two Dark Dwarves as muscle.  Levels 3-6.

  * Zone T2 -- The Refugee Enclave of Kin Tharonnath (18 rooms,
    6265-6282)
    The headline moral-dilemma zone. An above-ground village of
    Half-Dómnathar and Silentborn refugees (peaceful; no mob spawns
    in the visible village) conceals a hidden understage where a
    Dómnathar Remnant-Officer is corrupting the enclave and feeding
    intel to the Spur Tower.  Players who fight their way through
    the understage get combat; players who investigate diplomatically
    get a quest chain.  Levels 6-9.

Idempotent. Run:
    python scripts/build_tidebloom_deceiver_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ===========================================================================
# Zone T1 -- Ashen Hollows Raider Camp  (14 rooms, 6251-6264)
# ===========================================================================

RAIDER_CAMP_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 6251,
        "name": "Ashen Hollows -- Raider Camp Perimeter",
        "description": (
            "A wider section of the Foxfen ruins where goblin squatters "
            "have thrown up a crude stockade of salvaged beams and "
            "canvas between two fire-blackened Elven columns. Smoke "
            "rises from cook-fires within; a watchman's crow calls "
            "from somewhere above. The path curves in toward the "
            "camp's heart."
        ),
        "exits": {"west": 6222, "east": 6252, "south": 6253},
        "flags": ["outdoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6252,
        "name": "Ashen Hollows -- Watchers' Rest",
        "description": (
            "A two-tiered platform cobbled together from Elven wood "
            "that did not burn, lashed with new rope. Two human "
            "cultists in charred red sashes sit cross-legged on the "
            "upper tier, watching the approaches while sharing a "
            "water-skin. Their sleeves bear the Flamewarg sun-and-"
            "bar marks."
        ),
        "exits": {"west": 6251, "south": 6253},
        "flags": ["outdoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6253,
        "name": "Ashen Hollows -- Cook-Fire",
        "description": (
            "The camp's central firepit, fed by scavenged Elven "
            "timbers that still bear the burn-scars of the original "
            "Dómnathar sorcery. A great iron pot simmers with a "
            "stew the goblins consider excellent and most humans "
            "would decline. A goblin shaman squats beside the fire, "
            "reading omens in the rising smoke."
        ),
        "exits": {"north": 6251, "east": 6254, "south": 6255,
                  "west": 6256},
        "flags": ["outdoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6254,
        "name": "Ashen Hollows -- Relic Tent",
        "description": (
            "A canvas tent kept deliberately shadowed inside. At the "
            "rear, on a low table covered with a velvet cloth, rest "
            "the camp's most valuable takings: a rack of scorched "
            "Elven harps, a dented silver bracelet, a glass sphere "
            "shot through with black veins. This last is a fragment "
            "of Sylvara's Shadow Orb -- worth far more than the "
            "raiders know. A kobold trapsmith stands watch beside it."
        ),
        "exits": {"west": 6253, "south": 6258},
        "flags": ["indoor", "dangerous", "trapped", "raider_camp"],
    },
    {
        "vnum": 6255,
        "name": "Ashen Hollows -- The Captain's Tent",
        "description": (
            "The largest tent in the camp, floored with layered rugs "
            "salvaged from the burnt cities. A desk of good wood holds "
            "a bandit-lord's working papers: tally-sheets of stolen "
            "goods, a half-written letter to a 'respected buyer in "
            "the Marches.' At the desk sits the Captain himself, a "
            "handsome man with unusually elongated ears he explains "
            "as a Westerlin birth-trait. He is not Westerlin. He is "
            "not, quite, human."
        ),
        "exits": {"north": 6253, "west": 6256, "east": 6257},
        "flags": ["indoor", "dangerous", "raider_camp", "boss_room"],
    },
    {
        "vnum": 6256,
        "name": "Ashen Hollows -- Dark Dwarf Lodge",
        "description": (
            "A stout tent, its canvas doubled against cold, pitched "
            "a little apart from the goblin tents. Two Dark Dwarves "
            "lodge here: the Captain's prized heavy muscle. A small "
            "portable forge sits cold in one corner; a wooden rack "
            "holds their armor and axes."
        ),
        "exits": {"east": 6253, "north": 6255, "south": 6259},
        "flags": ["indoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6257,
        "name": "Ashen Hollows -- Slave Pen",
        "description": (
            "A crude enclosure of lashed timber where the camp keeps "
            "its occasional captives. Currently two: a Pasua scout "
            "with a splinted arm, and a Twin Rivers trader whose "
            "caravan was taken last month. A Silentborn guards the "
            "pen, posing as a human mercenary -- an act she has been "
            "maintaining for the Captain's benefit for six months."
        ),
        "exits": {"west": 6255, "south": 6260},
        "flags": ["outdoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6258,
        "name": "Ashen Hollows -- Storeroom",
        "description": (
            "A canvas-roofed lean-to built against a surviving wall-"
            "section of an Elven storehouse. The camp's supplies are "
            "stacked neatly: ration-crates, water-barrels, oil-jars, "
            "and a locked strongbox containing the Captain's "
            "emergency coin. A hobgoblin sergeant sits at a camp-"
            "stool, reading the manifest-ledger by lantern light."
        ),
        "exits": {"north": 6254, "west": 6261, "east": 6259},
        "flags": ["indoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6259,
        "name": "Ashen Hollows -- Smuggler's Cut",
        "description": (
            "A narrow path cut through the brush behind the camp, "
            "leading down to a hidden dock on a concealed arm of "
            "Foxfen's old canal. The Captain's goods leave the camp "
            "here, on flat-bottomed boats bound for the Marches. "
            "Currently the dock is empty; the next shipment is "
            "two nights away."
        ),
        "exits": {"north": 6256, "west": 6258, "south": 6260},
        "flags": ["outdoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6260,
        "name": "Ashen Hollows -- Trade Tent",
        "description": (
            "A canvas pavilion where the Captain conducts business "
            "with visiting buyers. A low table, two chairs, a folded "
            "cloth for displaying goods. A locked chest contains "
            "sample-pieces. The pavilion is empty now; the last "
            "negotiation concluded yesterday evening and the Captain "
            "is still tallying the profit."
        ),
        "exits": {"north": 6257, "west": 6261, "east": 6262},
        "flags": ["indoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6261,
        "name": "Ashen Hollows -- Cultist's Tent",
        "description": (
            "A low tent the Flamewarg cultists use for their evening "
            "prayers. A crude altar holds a crossed-out-sun symbol "
            "and a sputtering candle. Sleeping rolls are arranged "
            "around the altar in a precise circle. The air smells "
            "of old incense and newer lamp-oil."
        ),
        "exits": {"east": 6258, "south": 6260},
        "flags": ["indoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6262,
        "name": "Ashen Hollows -- Scout Bunker",
        "description": (
            "A half-dug bunker in the ruin's outer margin, concealed "
            "by brush and draped with old Elven canvas. The bunker's "
            "single goblin scout watches the south approach through "
            "a slit-window. The view commands a long stretch of the "
            "Foxfen path."
        ),
        "exits": {"west": 6260, "south": 6263},
        "flags": ["outdoor", "dangerous", "raider_camp"],
    },
    {
        "vnum": 6263,
        "name": "Ashen Hollows -- Relic Stash",
        "description": (
            "A concealed pit beneath the scout bunker's floor, "
            "accessible only by lifting a canvas rug and prying up "
            "two loose boards. Inside, wrapped in oilcloth, are the "
            "items the Captain has not yet declared to his partners: "
            "four silver bracelets, a sealed jar of elven perfume, "
            "and the clean half of Aerith's Flute."
        ),
        "exits": {"north": 6262, "east": 6264},
        "flags": ["indoor", "dangerous", "trapped", "raider_camp"],
    },
    {
        "vnum": 6264,
        "name": "Ashen Hollows -- Escape Path",
        "description": (
            "A narrow trail slipping away south from the relic stash, "
            "through the densest part of the old-Elf tree-fall. Hard "
            "to follow without knowing the way. This is the Captain's "
            "personal exit, memorized rather than mapped. It emerges, "
            "eventually, on the road to the Marches."
        ),
        "exits": {"west": 6263},
        "flags": ["outdoor", "dangerous"],
    },
]


# ===========================================================================
# Zone T2 -- The Refugee Enclave of Kin Tharonnath  (18 rooms, 6265-6282)
# ===========================================================================
# Above ground = peaceful village (no hostile mobs).
# Hidden understage = combat + moral weight.

ENCLAVE_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 6265,
        "name": "Kin Tharonnath -- Hidden Approach",
        "description": (
            "North of the Tomb of Kings approach, the forest thickens "
            "until the canopy almost closes overhead. An unmarked "
            "path -- hardly a path, really -- winds through the "
            "undergrowth. A careful watcher will notice that the "
            "nearby trees have been subtly pruned to conceal the "
            "line-of-sight from the main road."
        ),
        "exits": {"south": 6207, "north": 6266},
        "flags": ["outdoor", "forest"],
    },
    {
        "vnum": 6266,
        "name": "Kin Tharonnath -- Enclave Gate",
        "description": (
            "A modest gate of woven sapling-wood stands in a clearing "
            "where the forest path ends. Two figures in plain homespun "
            "sit on a log bench: an older Half-Dómnathar man who "
            "smiles at visitors with genuine, if wary, warmth, and a "
            "young Silentborn woman who looks up from her mending. "
            "Neither is armed. The welcome is real."
        ),
        "exits": {"south": 6265, "north": 6267},
        "flags": ["outdoor", "safe", "camp"],
    },
    {
        "vnum": 6267,
        "name": "Kin Tharonnath -- Village Square",
        "description": (
            "A small square paved with flat river-stones. A communal "
            "well at the center; wooden benches around the periphery. "
            "Half-Dómnathar villagers go about their business -- "
            "carrying water, hanging laundry, calling to children. "
            "Their eyes, in the shade, catch the light at a "
            "faintly-wrong angle. No one is hostile. No one has been "
            "hostile, to a stranger, in three generations."
        ),
        "exits": {"south": 6266, "east": 6268, "north": 6269,
                  "west": 6270},
        "flags": ["outdoor", "safe", "camp"],
    },
    {
        "vnum": 6268,
        "name": "Kin Tharonnath -- Elder's Hall",
        "description": (
            "A longhouse of salvaged timber where the village's "
            "elders gather for council. Low benches, a central hearth "
            "now cold, and a carved wooden chair at the hall's head "
            "bearing an empty iron circle worked into its back. The "
            "hall is empty at the moment. The village elder is not "
            "here."
        ),
        "exits": {"west": 6267, "north": 6275},
        "flags": ["indoor", "safe", "camp"],
    },
    {
        "vnum": 6269,
        "name": "Kin Tharonnath -- Common Kitchen",
        "description": (
            "A long open-sided kitchen where the village's meals are "
            "prepared communally. Two older Half-Dómnathar women "
            "chop root vegetables at a long table, speaking quietly "
            "about weather and grandchildren. The smell of bread and "
            "onions is excellent."
        ),
        "exits": {"south": 6267, "east": 6268, "west": 6271},
        "flags": ["outdoor", "safe", "camp"],
    },
    {
        "vnum": 6270,
        "name": "Kin Tharonnath -- Half-Dómnathar Quarters",
        "description": (
            "A row of modest cottages where the village's Half-"
            "Dómnathar families live. Kitchen-gardens at each front "
            "door; chickens pecking in the lane; a child's wooden toy "
            "left on a doorstep. The cottages are well-kept and "
            "warm-looking. Normal life happens here."
        ),
        "exits": {"east": 6267, "south": 6272},
        "flags": ["outdoor", "safe", "camp"],
    },
    {
        "vnum": 6271,
        "name": "Kin Tharonnath -- Silentborn Farmers' Huts",
        "description": (
            "A smaller cluster of huts, simpler in construction, "
            "where the village's Silentborn farmers live. A few are "
            "tending small vegetable-plots; others repair fishing-"
            "nets on a stretched frame. They are quieter than their "
            "Half-Dómnathar neighbors. They have not forgotten what "
            "was done to their grandmothers."
        ),
        "exits": {"east": 6269, "south": 6273},
        "flags": ["outdoor", "safe", "camp"],
    },
    {
        "vnum": 6272,
        "name": "Kin Tharonnath -- Dark Dwarf Forge",
        "description": (
            "A modest forge at the village's edge, tended by the "
            "enclave's two Dark Dwarves. The forge is cold today; "
            "the smiths are at the water-barrel, sharing a meal. "
            "They nod at visitors without hostility, but without "
            "particular welcome either."
        ),
        "exits": {"north": 6270, "east": 6273},
        "flags": ["outdoor", "safe", "camp"],
    },
    {
        "vnum": 6273,
        "name": "Kin Tharonnath -- Shrine of the Fallen",
        "description": (
            "A small open shrine of polished stone bearing names in "
            "three scripts -- the enclave's dead, across four "
            "generations. Half-Dómnathar, Silentborn, and the "
            "handful of Kin who have chosen over the years to live "
            "here and be buried here. A candle burns beneath each "
            "name. No one tends the shrine; it tends itself."
        ),
        "exits": {"north": 6271, "west": 6272, "south": 6274},
        "flags": ["outdoor", "safe", "camp"],
    },
    {
        "vnum": 6274,
        "name": "Kin Tharonnath -- Storehouse",
        "description": (
            "A log-built storehouse containing the enclave's "
            "communal reserves: sacks of grain, barrels of salted "
            "fish, bundles of dried herbs. A ledger on a peg "
            "records what has been drawn and by whom. The "
            "bookkeeping is honest. The quartermaster is not "
            "here."
        ),
        "exits": {"north": 6273},
        "flags": ["indoor", "safe", "camp"],
    },
    {
        "vnum": 6275,
        "name": "Kin Tharonnath -- Hidden Understage",
        "description": (
            "A concealed trapdoor behind the Elder's chair in the "
            "Elder's Hall drops into a stone-lined chamber below "
            "the village. The lamps here are brass, carefully shaded. "
            "A desk against the wall holds a neat stack of "
            "dispatches in Dómnathar script -- receipts of "
            "correspondence that the village's elder has been "
            "maintaining with the Spur Tower for twenty-two years."
        ),
        "exits": {"up": 6268, "north": 6276, "east": 6277,
                  "west": 6279},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 6276,
        "name": "Kin Tharonnath -- The Officer's Chamber",
        "description": (
            "A private chamber more richly appointed than the hall "
            "above would suggest: good rugs, a writing-desk of "
            "dark wood, a weapon-stand holding a Dómnathar-forged "
            "longsword. At the desk sits the village's Elder -- or "
            "rather, the man who has played the role of Elder for "
            "twenty-two years. He is Dómnathar. He has been "
            "infiltrating this village since the grandfathers of the "
            "current villagers were children."
        ),
        "exits": {"south": 6275, "east": 6278},
        "flags": ["indoor", "dangerous", "underground", "boss_room"],
    },
    {
        "vnum": 6277,
        "name": "Kin Tharonnath -- Loyalist Barracks",
        "description": (
            "A small barracks beside the Officer's chamber, "
            "housing the three Silentborn who know about the "
            "understage and have chosen to side with the Officer. "
            "Their cots are neat, their weapons are oiled, and the "
            "three are currently on duty: two watch the corridor, "
            "a third tends a small work-forge in the corner."
        ),
        "exits": {"west": 6275, "south": 6278},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 6278,
        "name": "Kin Tharonnath -- The Void Conduit",
        "description": (
            "A stone chamber whose walls are inlaid with silence-"
            "runes. In the center, a basin of absolutely still black "
            "water -- a scrying-pool connected directly to the Spur "
            "Tower's Void Chamber. Through this pool the Officer "
            "reports weekly. Beside the pool stands his "
            "enforcer-priest, in blackened leather, waiting for "
            "today's communion."
        ),
        "exits": {"north": 6276, "west": 6277},
        "flags": ["indoor", "dangerous", "underground", "silence_zone"],
    },
    {
        "vnum": 6279,
        "name": "Kin Tharonnath -- Memory Archive",
        "description": (
            "A small study lined with shelves of carefully-bound "
            "record-books. Each book contains the village's "
            "genealogy for a decade -- the true lineages, as the "
            "Officer knows them, with names of informants marked in "
            "red and with blood-ties to Spur Tower agents traced "
            "back to the founding generation. A Silentborn researcher "
            "sits at a desk, updating the current year's record."
        ),
        "exits": {"east": 6275, "south": 6280},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 6280,
        "name": "Kin Tharonnath -- Escape Burrow",
        "description": (
            "A narrow tunnel dug from the understage outward, "
            "toward a concealed exit somewhere in the deep Tidewoods. "
            "The tunnel is braced with fresh-cut timbers and "
            "maintained well. The Officer has used it twice in "
            "twenty-two years. He does not expect to need it again, "
            "but one prepares."
        ),
        "exits": {"north": 6279, "east": 6282},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 6281,
        "name": "Kin Tharonnath -- Children's House",
        "description": (
            "A larger cottage above-ground where the village's "
            "children sleep during the day-and-night teaching-cycle "
            "by which the enclave educates its young. Several "
            "half-dozen children of various ages sit at low tables "
            "with slate-boards, learning letters. They look up "
            "when strangers enter, shy, curious. None of them know "
            "what their grandfather does in the understage."
        ),
        "exits": {"south": 6267},
        "flags": ["indoor", "safe", "camp"],
    },
    {
        "vnum": 6282,
        "name": "Kin Tharonnath -- Deep Forest Path",
        "description": (
            "The escape burrow emerges in a thicket far from the "
            "village clearing. The Tidewoods stretch away in all "
            "directions. A careful walker could vanish into this "
            "forest and never be found; the Officer has relied on "
            "this fact through three small crises over the years. "
            "Today the path is quiet."
        ),
        "exits": {"west": 6280},
        "flags": ["outdoor", "forest"],
    },
]


# ===========================================================================
# Outbound exits from existing rooms
# ===========================================================================

NEW_EXITS = [
    (6222, "east", 6251),  # Foxfen Northern Ruins -> Raider Camp Perimeter
    (6207, "north", 6265), # Tomb of Kings Outer Precinct -> Enclave approach
]


# ===========================================================================
# Mob spawns (vnums 4100-4119)
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
LT_FIRECLOAK  = [{"vnum": 706, "chance": 0.35}]
LT_VOIDHAMMER = [{"vnum": 707, "chance": 0.45}]
LT_TABLET     = [{"vnum": 708, "chance": 0.55}]
LT_DARKIRON_L = [{"vnum": 709, "chance": 0.45}]
LT_COLLAR     = [{"vnum": 710, "chance": 0.55}]
LT_VOIDROD    = [{"vnum": 711, "chance": 0.75}]


SPAWN_SPEC = [
    # --- Raider Camp (4100-4109) -----------------------------------------
    (4100, "Flamewarg Cult Initiate (Sorcerer 3, Human)", 6252,
            LT_FIRECLOAK + LT_DARKIRON_D),
    (4101, "Flamewarg Cult Initiate (Sorcerer 3, Human)", 6252,
            LT_FIRECLOAK + LT_POTION),
    (4102, "Goblin Shaman (Adept 3)",                6253,
            LT_POTION + LT_FIRECLOAK),
    (4103, "Kobold Trapsmith (Rogue 3)",             6254,
            LT_DARKIRON_D + LT_POTION + LT_SIGNET),
    (4104, "Half-Dómnathar Broker (Bard 5 / Rogue 2)", 6255,
            LT_MW_SWORD + LT_TABLET + LT_WARDAMUL + LT_SIGNET,
            ),
    (4105, "Dark Dwarf Warrior (Fighter 3)",         6256,
            LT_DARKIRON_L + LT_MW_ARMOR),
    (4106, "Dark Dwarf Warrior (Fighter 3)",         6256,
            LT_DARKIRON_L),
    (4107, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 6257,
            LT_MW_SWORD + LT_COLLAR),
    (4108, "Hobgoblin Sergeant (Fighter 2)",         6258,
            LT_MW_ARMOR + LT_COINS),
    (4109, "Hobgoblin Tunnel-Warden (Fighter 3 / Ranger 1)", 6259,
            LT_MW_SWORD + LT_MW_ARMOR + LT_DARKIRON_L),

    # --- Enclave Hidden Understage (4110-4115) ---------------------------
    # Above-ground village is peaceful -- NO mob spawns there.
    (4110, "Dómnathar Remnant-Officer (Fighter 7)",  6276,
            LT_MW_SWORD + LT_VOIDHAMMER + LT_MW_ARMOR + LT_TABLET + LT_COLLAR + LT_VOIDROD),
    (4111, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 6277,
            LT_MW_SWORD + LT_DARKIRON_L),
    (4112, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 6277,
            LT_MW_ARMOR + LT_COLLAR),
    (4113, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 6277,
            LT_DARKIRON_L),
    (4114, "Half-Dómnathar Battle-Priest (Cleric 7)", 6278,
            LT_VOIDHAMMER + LT_COLLAR + LT_TABLET),
    (4115, "Silentborn Researcher (Wizard 4)",       6279,
            LT_POTION + LT_TABLET),
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
    path = os.path.join(DATA, "areas", "TidebloomReach.json")
    rooms = _read(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0
    for r in RAIDER_CAMP_ROOMS + ENCLAVE_ROOMS:
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
    print(f"  TidebloomReach.json: +{added} rooms, +{wired} exits (total {len(rooms)})")


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
    print("Building Tidebloom Reach Deceiver zones:")
    merge_rooms()
    merge_mobs()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
