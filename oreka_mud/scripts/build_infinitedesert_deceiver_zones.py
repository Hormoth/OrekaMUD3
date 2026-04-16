"""Build the Infinite Desert Deceiver zones.

  * Zone I1 -- Dust-Cache Warren (12 rooms, vnums 8264-8275)
    Kobold scavengers digging up buried Deceiver equipment beneath the
    Glass Wastes. A Dark Dwarf scavenger-lord runs the operation, a
    confused Sand Wraith has been accidentally released, and two
    Pekakarlik refugees have been captured and forced to translate the
    runes. Level band 2-5.  Extends the 1-room 8244 placeholder.

  * Zone I2 -- Fusion-Cell Outpost (20 rooms, vnums 8276-8295)
    A Half-Dómnathar research station buried under a fused-glass slab
    in the Glass Wastes, trying to re-create the Deceiver fusion magic
    that melted the glass in the first place. A captive human
    arcanist from beyond the Gate is being used as a caster-battery.
    Level band 11-14, boss: Half-Dómnathar Research-Sorcerer CR 12.

Idempotent. Run:
    python scripts/build_infinitedesert_deceiver_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ===========================================================================
# Zone I1 -- Dust-Cache Warren  (12 rooms, 8264-8275)
# ===========================================================================

DUSTCACHE_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 8264,
        "name": "Dust-Cache Warren -- Upper Vault",
        "description": (
            "A broken-open antechamber beneath the Buried Deceiver "
            "Cache above. Kobold workers have widened the original "
            "breach into a crude vaulted room propped with scavenged "
            "timber. Sand drifts in through cracks in the sealed "
            "ceiling, and the air is thick with dust and lamp-smoke. "
            "A Pekakarlik-script rune half-visible on a wall has been "
            "partially erased by a careless scraper."
        ),
        "exits": {"up": 8244, "east": 8265},
        "flags": ["indoor", "dangerous", "underground", "dust_cache"],
    },
    {
        "vnum": 8265,
        "name": "Dust-Cache Warren -- Main Shaft",
        "description": (
            "The central shaft of the warren descends steeply from the "
            "upper vault, its floor a long slope of loose sand and "
            "broken Pekakarlik stonework. A rope-and-pulley hauling "
            "system at the top lifts ore-sacks to the surface. The "
            "shaft branches into work-tunnels to north, east, and "
            "south."
        ),
        "exits": {"west": 8264, "north": 8266, "east": 8267,
                  "south": 8268, "down": 8269},
        "flags": ["indoor", "dangerous", "underground", "dust_cache"],
    },
    {
        "vnum": 8266,
        "name": "Dust-Cache Warren -- Kobold Work Gang",
        "description": (
            "A wider chamber where the warren's kobold laborers sift "
            "through loose sand for Deceiver-era trinkets. Three "
            "kobolds -- two scouts and a trapsmith -- work the sieves "
            "while chanting a low repetitive work-song. Every recovered "
            "item goes into a wicker basket which the trapsmith then "
            "catalogues with meticulous care."
        ),
        "exits": {"south": 8265, "east": 8270},
        "flags": ["indoor", "dangerous", "underground", "dust_cache"],
    },
    {
        "vnum": 8267,
        "name": "Dust-Cache Warren -- The Sand Wraith's Cell",
        "description": (
            "A chamber the kobolds accidentally opened three weeks ago "
            "and have since sealed off with timber and canvas. Inside, "
            "something ancient and very thirsty paces in an irregular "
            "circle. The air here is dry beyond reason -- it pulls "
            "moisture from the lungs on every breath. The Sand Wraith "
            "was buried alive. She has not forgiven anyone for it."
        ),
        "exits": {"west": 8265, "south": 8268},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "dust_cache"],
    },
    {
        "vnum": 8268,
        "name": "Dust-Cache Warren -- Translators' Chamber",
        "description": (
            "A small carved-out cell with a writing-bench and lamp, "
            "occupied by two Pekakarlik dwarves. Their chains are "
            "short enough that they cannot reach the door. They are "
            "here to read the Deceiver runes on recovered items, and "
            "they are terrified. One of them, seeing Kin, risks "
            "everything and raises a finger to her lips."
        ),
        "exits": {"north": 8265, "east": 8267},
        "flags": ["indoor", "underground", "dust_cache"],
    },
    {
        "vnum": 8269,
        "name": "Dust-Cache Warren -- The Scavenger's Vault",
        "description": (
            "A dressed-stone chamber at the bottom of the main shaft, "
            "lit by multiple oil-lamps. The floor is covered in a "
            "carefully-arranged sorting of recovered artifacts: rack "
            "of Deceiver daggers, shelf of cipher-tablets, a velvet "
            "tray holding a dozen rings. A dour dwarf in fine lamellar "
            "sits at a writing-desk, updating a ledger."
        ),
        "exits": {"up": 8265, "east": 8271, "south": 8272},
        "flags": ["indoor", "dangerous", "underground", "dust_cache"],
    },
    {
        "vnum": 8270,
        "name": "Dust-Cache Warren -- Trap-Diggers' Workshop",
        "description": (
            "A workshop where the warren's more skilled kobolds work "
            "on genuine trap-craft rather than mere sifting. Benches "
            "hold small brass mechanisms, glass phials of various "
            "poisons, and a few pristine Deceiver-era devices the "
            "kobolds are trying to reverse-engineer with uneven "
            "success."
        ),
        "exits": {"west": 8266, "south": 8271},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "dust_cache"],
    },
    {
        "vnum": 8271,
        "name": "Dust-Cache Warren -- Scavenger-Lord's Chamber",
        "description": (
            "The Dark Dwarf's private quarters, appointed in "
            "surprisingly good taste: a proper bed, a shelf of books "
            "stolen from Kinsweave libraries, a small brass samovar. "
            "He sits in a padded chair, reading, with a war-axe across "
            "his knees. A Dark Dwarf warrior guards the door. The "
            "Scavenger-Lord looks up, unsurprised and faintly annoyed."
        ),
        "exits": {"west": 8269, "north": 8270},
        "flags": ["indoor", "dangerous", "underground", "dust_cache"],
    },
    {
        "vnum": 8272,
        "name": "Dust-Cache Warren -- Deeper Dig Site",
        "description": (
            "The active excavation, where the warren's workers are "
            "still breaking through to whatever the Pekakarlik runes "
            "indicate lies deeper. A rough ramp descends into a "
            "chamber only partly excavated. An ore-cart rails setup "
            "has been abandoned mid-installation."
        ),
        "exits": {"north": 8269, "east": 8273, "down": 8274},
        "flags": ["indoor", "dangerous", "underground", "dust_cache"],
    },
    {
        "vnum": 8273,
        "name": "Dust-Cache Warren -- Abandoned Machine Room",
        "description": (
            "A chamber the kobolds have cleared but not yet fully "
            "catalogued. Rows of strange metal apparatus stand in the "
            "sand, half-buried. Some of them are still warm to the "
            "touch despite centuries of burial. The Pekakarlik "
            "translators refused to read the inscriptions here, and "
            "were beaten for their refusal."
        ),
        "exits": {"west": 8272},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "dust_cache"],
    },
    {
        "vnum": 8274,
        "name": "Dust-Cache Warren -- Hidden Storeroom",
        "description": (
            "A concealed strongroom the Scavenger-Lord keeps for the "
            "items he has not yet declared to the warren's official "
            "ledger. A locked iron chest sits in the middle of the "
            "room; behind it, leaning against the wall, is a "
            "Deceiver-era staff whose head is a perfectly smooth "
            "sphere of black glass."
        ),
        "exits": {"up": 8272, "south": 8275},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "dust_cache"],
    },
    {
        "vnum": 8275,
        "name": "Dust-Cache Warren -- Bolt-Hole",
        "description": (
            "A narrow tunnel leading away to the south, cut by the "
            "Scavenger-Lord's personal work-gang in secret. It "
            "emerges, supposedly, somewhere in the dunes several miles "
            "from the warren. He has never used it; the tunnel is "
            "maintained but unused, as a safety measure he hopes "
            "never to need."
        ),
        "exits": {"north": 8274},
        "flags": ["indoor", "dangerous", "underground"],
    },
]


# ===========================================================================
# Zone I2 -- Fusion-Cell Outpost  (20 rooms, 8276-8295)
# ===========================================================================

FUSIONCELL_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 8276,
        "name": "Fusion-Cell -- Surface Hatch",
        "description": (
            "Beneath a fused-glass slab indistinguishable from the "
            "surrounding Glass Wastes, a concealed hatch opens into "
            "a small surface blind: a canvas-roofed tent-space holding "
            "a desk, a weapon-stand, and a ledger-book. The tent is "
            "not visible from even a few paces away. The outpost's "
            "discretion is, above all else, absolute."
        ),
        "exits": {"up": 8242, "north": 8277, "down": 8278},
        "flags": ["indoor", "dangerous", "outpost"],
    },
    {
        "vnum": 8277,
        "name": "Fusion-Cell -- Surface Guards' Post",
        "description": (
            "A small observation-chamber behind the surface hatch, "
            "with a narrow slit-window looking out across the Glass "
            "Wastes. Two Silentborn in neutral traveling-clothes "
            "stand watch by the window, weapons low and hands ready. "
            "The watch-rotation is on a stone slate on the wall."
        ),
        "exits": {"south": 8276},
        "flags": ["indoor", "dangerous", "outpost"],
    },
    {
        "vnum": 8278,
        "name": "Fusion-Cell -- Descent Corridor",
        "description": (
            "A long staircase of polished black stone descends steeply "
            "from the surface hatch. Runes inlaid in silver along the "
            "stair-walls shed a faint, cold illumination. The air "
            "grows warmer as one descends, not cooler -- the fusion "
            "furnace is running."
        ),
        "exits": {"up": 8276, "down": 8279},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8279,
        "name": "Fusion-Cell -- Upper Lab Hall",
        "description": (
            "The central hall of the upper lab, a long arched chamber "
            "whose floor is a single polished slab and whose walls are "
            "lined with glass-fronted cabinets full of neatly-labeled "
            "samples. Silentborn researchers in spotless white aprons "
            "move between stations with purposeful quiet."
        ),
        "exits": {"up": 8278, "north": 8280, "east": 8281,
                  "south": 8283, "west": 8287},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8280,
        "name": "Fusion-Cell -- Materials Storage",
        "description": (
            "A locked chamber full of crates of fused-glass samples, "
            "each labeled with its extraction-date and coordinates. "
            "A Dark Dwarf warrior stands guard in the corner, polishing "
            "her waraxe. She looks up at intruders with unconcealed "
            "professional interest: a break in the boredom."
        ),
        "exits": {"south": 8279, "east": 8281},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8281,
        "name": "Fusion-Cell -- Fusion Furnace Access",
        "description": (
            "An iron-and-stone corridor whose walls are hot to the "
            "touch. The corridor slopes gently downward toward the "
            "primary fusion chamber. Thick bundles of silver cable "
            "run along the ceiling, connecting the furnace to apparatus "
            "elsewhere in the complex. The air tastes like lightning."
        ),
        "exits": {"west": 8279, "north": 8280, "south": 8282,
                  "east": 8289},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8282,
        "name": "Fusion-Cell -- The Primary Fusion Chamber",
        "description": (
            "A domed chamber whose floor is a ring-shaped furnace, "
            "currently active, its interior glowing a deep and "
            "unreasonable violet. Safely suspended above the ring on "
            "an iron gallery, a Half-Dómnathar in scholar's robes "
            "directs the work with calm, absorbed concentration. "
            "Two Silentborn assistants stand at the gallery rail, "
            "reading from an open notebook."
        ),
        "exits": {"north": 8281, "west": 8291, "east": 8284},
        "flags": ["indoor", "dangerous", "underground", "outpost",
                  "boss_room"],
    },
    {
        "vnum": 8283,
        "name": "Fusion-Cell -- Researchers' Quarters",
        "description": (
            "A row of narrow cells for the outpost's Silentborn "
            "researchers. Each cell contains a cot, a small shelf, "
            "and a reading-light. Several of the cells are currently "
            "occupied by off-duty staff asleep or studying. The "
            "quarters are spartan, but the outpost is proud of them."
        ),
        "exits": {"north": 8279, "east": 8284},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8284,
        "name": "Fusion-Cell -- Containment Cell",
        "description": (
            "A reinforced glass-fronted cell contains a prisoner. "
            "She is a human woman of middle years in worn traveling-"
            "robes, shackled at wrist and ankle to a stone block that "
            "cannot be moved. Her hands are blistered where she has "
            "been forced to cast spells she did not want to cast. She "
            "watches you without hope, which is itself a terrible "
            "thing to see."
        ),
        "exits": {"west": 8283, "north": 8282, "south": 8285},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8285,
        "name": "Fusion-Cell -- Void-Smith's Forge",
        "description": (
            "A cold forge where a Dark Dwarf smith shapes iron into "
            "containment-vessels, suppressor-irons, and the housings "
            "of the fusion-chamber's consumable cells. The anvil runs "
            "with perpetual frost despite the forge's banked coals. "
            "She works quickly and well."
        ),
        "exits": {"north": 8284, "east": 8286},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8286,
        "name": "Fusion-Cell -- Construct Guard Post",
        "description": (
            "A square chamber whose only occupant stands in the center. "
            "Eight feet tall, obsidian-bodied, breathing no breath. A "
            "Void-Construct, on sentinel duty. The air around it is "
            "cold. The runes inlaid into the chamber's floor prevent "
            "any non-authorized entry from passing into the lower "
            "complex; the Construct enforces the prohibition."
        ),
        "exits": {"west": 8285, "north": 8289, "south": 8290},
        "flags": ["indoor", "dangerous", "underground", "outpost",
                  "silence_zone"],
    },
    {
        "vnum": 8287,
        "name": "Fusion-Cell -- Records Library",
        "description": (
            "A long narrow room lined with metal filing-cabinets and "
            "a central work-table. The cabinets contain the outpost's "
            "research logs: five years of attempts to reproduce the "
            "Glass Wastes' fusion-event. The conclusions are, so far, "
            "incomplete. A Silentborn researcher stands at the table, "
            "cross-referencing two volumes."
        ),
        "exits": {"east": 8279, "north": 8288},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8288,
        "name": "Fusion-Cell -- Observation Platform",
        "description": (
            "A small viewing-gallery set above the primary fusion "
            "chamber's outer ring. The floor here is glass-panelled, "
            "allowing visitors to observe the furnace from above. "
            "Brass-and-ivory opera-glasses rest on a shelf. A ledger "
            "bound to the railing records observations in exquisitely "
            "neat script."
        ),
        "exits": {"south": 8287},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8289,
        "name": "Fusion-Cell -- Secondary Furnace",
        "description": (
            "A smaller furnace-chamber currently banked and cooling. "
            "Its purpose is preliminary heating of materials before "
            "they are introduced to the primary. The chamber is empty "
            "of staff; a maintenance-gang apparently finished here "
            "hours ago. Warmth radiates from the walls."
        ),
        "exits": {"west": 8281, "south": 8286},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8290,
        "name": "Fusion-Cell -- Experimental Cold Lab",
        "description": (
            "An extremely cold chamber where the researchers work on "
            "preservation and storage of fusion-reaction by-products. "
            "The walls are lined with sealed glass cases holding "
            "substances that should not be possible to stabilize. "
            "Breath frosts. Fingers stiffen. The precise temperature "
            "is maintained by Pekakarlik cold-stones of unusual power."
        ),
        "exits": {"north": 8286, "east": 8291},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8291,
        "name": "Fusion-Cell -- The Mother-Core",
        "description": (
            "The outpost's most sensitive chamber. At its center, "
            "suspended in a ring of silver holders above a pit of "
            "absolutely black water, hangs a small rough sphere of "
            "material that is neither stone nor metal nor glass. It "
            "is, the researchers believe, a fragment of the original "
            "Deceiver fusion-event. The air here is not quite right. "
            "It does not take breath willingly."
        ),
        "exits": {"east": 8282, "west": 8290, "south": 8292},
        "flags": ["indoor", "dangerous", "underground", "outpost",
                  "silence_zone"],
    },
    {
        "vnum": 8292,
        "name": "Fusion-Cell -- Escape Shaft Access",
        "description": (
            "A concealed chamber behind a pivoting section of wall. "
            "A shaft descends sharply here -- the outpost's planned "
            "evacuation route if the fusion-chamber destabilizes. "
            "The researchers talk about this shaft very rarely and "
            "always in low voices."
        ),
        "exits": {"north": 8291, "down": 8293},
        "flags": ["indoor", "dangerous", "underground", "outpost"],
    },
    {
        "vnum": 8293,
        "name": "Fusion-Cell -- Deep Escape Shaft",
        "description": (
            "A long vertical shaft, braced with iron rungs. It "
            "descends through solid sandstone for what feels like a "
            "very long time, and eventually emerges into a natural "
            "cavern whose entrance-tunnels have never been mapped by "
            "the outpost's surveyors. Somewhere below is a larger "
            "cavern system."
        ),
        "exits": {"up": 8292, "down": 8294},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 8294,
        "name": "Fusion-Cell -- Sealed Cavern",
        "description": (
            "The shaft terminates in a natural limestone cavern whose "
            "far walls disappear into darkness. The air is cooler "
            "than the outpost above and smells of old stone and "
            "faint sulfur. A rough stone door -- dressed by Kin "
            "hands generations ago -- is set into the far wall, "
            "sealed with Pekakarlik runes still glowing faintly."
        ),
        "exits": {"up": 8293, "north": 8295},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 8295,
        "name": "Fusion-Cell -- Ancient Cache",
        "description": (
            "A small chamber beyond the sealed door, where the "
            "Pekakarlik once hid a cache of items against the "
            "Deceivers' return. A rack of old dwarven gear, a wrapped "
            "bundle of scrolls, and a small stone chest rest "
            "undisturbed. These have been here for three hundred "
            "years. They are the outpost's researchers' great secret "
            "hope: that when they find this cache, they will "
            "understand what the Pekakarlik hid from the Deceivers, "
            "and why."
        ),
        "exits": {"south": 8294},
        "flags": ["indoor", "dangerous", "trapped", "underground"],
    },
]


# ===========================================================================
# Outbound exits from existing rooms
# ===========================================================================

NEW_EXITS = [
    (8244, "down", 8264),  # Buried Deceiver Cache -> Dust-Cache Upper Vault
    (8242, "down", 8276),  # Ancient Battleground -> Fusion-Cell Surface Hatch
]


# ===========================================================================
# Mob spawns (vnums 3900-3920)
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
LT_TABLET     = [{"vnum": 708, "chance": 0.60}]
LT_DARKIRON_L = [{"vnum": 709, "chance": 0.45}]
LT_COLLAR     = [{"vnum": 710, "chance": 0.55}]
LT_VOIDROD    = [{"vnum": 711, "chance": 0.75}]


SPAWN_SPEC = [
    # --- Dust-Cache Warren (3900-3908) ------------------------------------
    (3900, "Kobold Scout (Sorcerer 1)",              8266, LT_TORCH + LT_COINS),
    (3901, "Kobold Scout (Sorcerer 1)",              8266, LT_TORCH),
    (3902, "Kobold Trapsmith (Rogue 3)",             8266, LT_DARKIRON_D + LT_POTION + LT_SIGNET),
    (3903, "Sand Wraith",                            8267,
            LT_WARDAMUL + LT_SIGNET + LT_POTION),
    (3904, "Kobold Cultist (Cleric 2)",              8270, LT_POTION + LT_FIRECLOAK),
    (3905, "Kobold Scout (Sorcerer 1)",              8270, LT_COINS),
    (3906, "Dark Dwarf Scavenger-Lord (Rogue 4)",    8271,
            LT_MW_SWORD + LT_DARKIRON_L + LT_TABLET + LT_SIGNET),
    (3907, "Dark Dwarf Warrior (Fighter 3)",         8271,
            LT_DARKIRON_L + LT_MW_ARMOR),
    (3908, "Kobold Sorcerer (Sorcerer 3)",           8273,
            LT_DARKIRON_D + LT_POTION + LT_FIRECLOAK),

    # --- Fusion-Cell Outpost (3909-3920) ---------------------------------
    (3909, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 8277,
            LT_MW_SWORD + LT_COLLAR),
    (3910, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 8277,
            LT_MW_ARMOR + LT_COLLAR),
    (3911, "Silentborn Researcher (Wizard 4)",       8279,
            LT_POTION + LT_TABLET),
    (3912, "Dark Dwarf Warrior (Fighter 3)",         8280,
            LT_MW_ARMOR + LT_DARKIRON_L),
    (3913, "Half-Dómnathar Research-Sorcerer (Wizard 10)", 8282,
            LT_VOIDHAMMER + LT_VOIDROD + LT_COLLAR + LT_TABLET + LT_WARDAMUL),
    (3914, "Silentborn Researcher (Wizard 4)",       8282,
            LT_POTION + LT_COLLAR),
    (3915, "Silentborn Researcher (Wizard 4)",       8282,
            LT_TABLET),
    (3916, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 8283,
            LT_MW_SWORD),
    (3917, "Dark Dwarf Void-Smith (Expert 7 / Wizard 1)", 8285,
            LT_COLLAR + LT_DARKIRON_L + LT_TABLET),
    (3918, "Dómnathar Void-Construct",               8286, []),
    (3919, "Silentborn Researcher (Wizard 4)",       8287,
            LT_TABLET + LT_POTION),
    (3920, "Dómnathar Sorcerer (Sorcerer 8)",        8291,
            LT_VOIDHAMMER + LT_COLLAR + LT_WARDAMUL + LT_TABLET),
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
    path = os.path.join(DATA, "areas", "InfiniteDesert.json")
    rooms = _read(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0
    for r in DUSTCACHE_ROOMS + FUSIONCELL_ROOMS:
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
    print(f"  InfiniteDesert.json: +{added} rooms, +{wired} exits "
          f"(total {len(rooms)})")


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
    print("Building Infinite Desert Deceiver zones:")
    merge_rooms()
    merge_mobs()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
