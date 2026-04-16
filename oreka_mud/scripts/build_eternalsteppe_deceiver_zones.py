"""Build the Eternal Steppe Deceiver zones.

  * Zone E1 -- Burnt Hollows Collapsed Fort (16 rooms, vnums 7246-7261)
    Extends the 1-room Burnt Hollows Entrance (7225) into a proper
    Flamewarg-cult compound in the collapsed Deceiver burrow-forts.
    Level band 4-7.  (Also repoints a broken exit: 7225's `down`
    currently leads to Varkhon Rise -- clearly an authoring error,
    since Varkhon is an open road. I repoint `down` into the new
    sub-level.)

  * Zone E2 -- The Second Breath Hideout (22 rooms, vnums 7262-7283)
    A Silentborn loyalist compound concealed in the Dark Dawn
    Battlefield dead zone (where Kin-sense dies). Above-ground tents
    plus a below-ground cold-storage horror, culminating in a Void
    Chamber. Level band 8-11, boss: Half-Dómnathar Mother-Superior
    (CR 9).

Idempotent. Run:
    python scripts/build_eternalsteppe_deceiver_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ===========================================================================
# Zone E1 -- Burnt Hollows Collapsed Fort  (16 rooms, 7246-7261)
# ===========================================================================

BURNT_HOLLOWS_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 7246,
        "name": "Burnt Hollows -- Upper Tunnel",
        "description": (
            "A jagged descent from the steppe above opens into a "
            "scorched tunnel of hand-cut stone, its walls blackened by "
            "fires that have been out for generations. The floor is "
            "uneven where the burrow-fort collapsed long ago; new "
            "timber braces hold the ceiling up where recent workmen "
            "have shored the worst passages. The air smells of old "
            "smoke and new lamp-oil."
        ),
        "exits": {"up": 7225, "north": 7247, "east": 7248},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7247,
        "name": "Burnt Hollows -- Collapsed Chamber",
        "description": (
            "A great chamber whose ceiling is half-fallen, buttressed "
            "now by a forest of stripped tree-trunks braced into the "
            "rubble. Loose earth sifts down in occasional small falls. "
            "The collapsed portion is said to hold the bodies of the "
            "garrison that once manned this place, pressed into the "
            "stone like flowers in a book."
        ),
        "exits": {"south": 7246, "east": 7249, "north": 7254},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "burnt_hollows"],
    },
    {
        "vnum": 7248,
        "name": "Burnt Hollows -- Goblin Barracks",
        "description": (
            "A crude barracks for the cult's goblin rank-and-file: "
            "bedding of scavenged cloaks, a central firepit ringed with "
            "blackened stones, and racks of stolen spears and shortbows. "
            "The goblins here wear red face-paint in the shape of a "
            "crossed-out sun -- the Flamewarg Cult's mark."
        ),
        "exits": {"west": 7246, "north": 7249, "east": 7255},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7249,
        "name": "Burnt Hollows -- Pyre Chamber",
        "description": (
            "A domed chamber whose floor is a wide pit filled with old "
            "ash and newer ember. A raised stone walkway rings the pit. "
            "Black smoke-stains climb the walls above the walkway, "
            "recording many fires. The cult burns its dead here, and "
            "keeps the ashes for sorcery."
        ),
        "exits": {"west": 7247, "south": 7248, "east": 7250,
                  "north": 7251},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7250,
        "name": "Burnt Hollows -- War-Warg Pens",
        "description": (
            "Iron-barred pens along both walls hold warg-sized beasts "
            "whose coats glow faint orange at the roots -- Flamewargs, "
            "the cult's prized mounts. The pens are kept hot by "
            "peat-fires; the floor is strewn with gnawed bones. "
            "Mercifully, the pens are currently full and locked."
        ),
        "exits": {"west": 7249, "north": 7252},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7251,
        "name": "Burnt Hollows -- Cult-Hall",
        "description": (
            "The largest chamber in the burrow-fort, deliberately kept "
            "cold and dim. Low stone benches ring three walls; a raised "
            "dais holds a rough-hewn altar piled with offerings. A "
            "tall figure in ember-stitched robes stands on the dais, "
            "her face lit from below by a low-burning brass brazier. "
            "Three human cultists flank her, their sleeves charred "
            "in the pattern of initiates."
        ),
        "exits": {"south": 7249, "east": 7252, "west": 7253,
                  "north": 7256},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7252,
        "name": "Burnt Hollows -- The Ancestor's Altar",
        "description": (
            "A small side-chamber where the cult-leader's most private "
            "relic is kept: the skull of her Mytroan great-grandfather, "
            "killed at Dark Dawn, mounted on a short iron pike and "
            "decorated with his own teeth re-sewn into his jaw. She "
            "calls on him for guidance. He, apparently, answers."
        ),
        "exits": {"west": 7251, "south": 7250},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7253,
        "name": "Burnt Hollows -- Captive Ring",
        "description": (
            "An iron-barred pen built into the side of the Cult-Hall, "
            "with a narrow viewing-slit cut into the wall above so that "
            "sermons can be delivered to the captives before they are "
            "pyre'd. Three prisoners sit hunched against the back wall: "
            "two steppe-nomads and a Mytroan herder, all bound, all "
            "silent."
        ),
        "exits": {"east": 7251, "south": 7254},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7254,
        "name": "Burnt Hollows -- Goblin Sub-Warren",
        "description": (
            "A warren of small burrow-chambers cut sideways into the "
            "fortress's main corridor, shared by the cult's goblin "
            "servants. The ceilings are too low for a full-height adult "
            "to stand comfortably. The smell of unwashed goblin is "
            "pungent but familiar."
        ),
        "exits": {"south": 7247, "north": 7253, "east": 7255},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7255,
        "name": "Burnt Hollows -- Hobgoblin Post",
        "description": (
            "A neatly-kept sentry post at the junction of the goblin "
            "barracks and the sub-warren. A hobgoblin in Shattered Host "
            "colors sits at a small table, reviewing a duty-roster. He "
            "is here on loan from the Spur Tower, and his quiet "
            "efficiency is a silent rebuke to the cult's disorder."
        ),
        "exits": {"west": 7248, "south": 7254, "north": 7256},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7256,
        "name": "Burnt Hollows -- Deep Forge",
        "description": (
            "An old Deceiver-era forge, its bellows rotted but its "
            "anvil still sound. The cult uses it for small work: "
            "arrowheads, hook-spikes, caltrops. A rack of half-finished "
            "cult-daggers -- crossed-out-sun motifs etched into their "
            "pommels -- rests against one wall."
        ),
        "exits": {"south": 7251, "north": 7255, "east": 7257},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7257,
        "name": "Burnt Hollows -- Cult Archive",
        "description": (
            "A low-ceilinged vault kept dry by carefully-maintained "
            "air-channels. Shelves hold bundles of scrolls and clay "
            "tablets recording the cult-leader's genealogy, her "
            "visions, and the dreams of her predecessors. Most of it "
            "is badly-written; some of it is uncomfortably prophetic."
        ),
        "exits": {"west": 7256, "north": 7258},
        "flags": ["indoor", "dangerous", "underground", "burnt_hollows"],
    },
    {
        "vnum": 7258,
        "name": "Burnt Hollows -- Treasure Vault",
        "description": (
            "The cult's small strongroom, holding the offerings the "
            "cult-leader has not yet burned: a sack of stolen coin, a "
            "chest of battered jewelry, and a locked case containing a "
            "single Deceiver-era dagger whose blade, even in the lamp-"
            "light, refuses to reflect anything."
        ),
        "exits": {"south": 7257, "east": 7259},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "burnt_hollows"],
    },
    {
        "vnum": 7259,
        "name": "Burnt Hollows -- Tunnel to Dark Dawn",
        "description": (
            "A long, low passage sloping gently downward and northward. "
            "The cult is aware that the Dark Dawn Battlefield lies "
            "somewhere beyond the tunnel's end; they do not pretend to "
            "know what else lies there. The tunnel has been abandoned "
            "for decades. Bones, small and old, are piled against the "
            "walls."
        ),
        "exits": {"west": 7258, "north": 7260},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 7260,
        "name": "Burnt Hollows -- Collapsed Stair",
        "description": (
            "A steep, narrow stair was cut here in Deceiver times, "
            "climbing from the deep-tunnel up to the steppe surface. "
            "The stair collapsed during the post-War retreat and is "
            "now a slope of loose rubble. A person with good "
            "footing might climb out of here, onto the steppe far "
            "beyond any road."
        ),
        "exits": {"south": 7259, "down": 7261},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 7261,
        "name": "Burnt Hollows -- Escape Bolt",
        "description": (
            "A single small cell carved into living stone at the very "
            "bottom of the collapsed stair. A leather bag of dried meat "
            "and a sealed clay jar of water sit on a shelf: the cult-"
            "leader's personal cache against the day she must flee. She "
            "has used it three times in her life, and returned to find "
            "it undisturbed each time."
        ),
        "exits": {"up": 7260},
        "flags": ["indoor", "dangerous", "underground"],
    },
]


# ===========================================================================
# Zone E2 -- The Second Breath Hideout  (22 rooms, 7262-7283)
# ===========================================================================
# Entry: from Dark Dawn Battlefield Central Zone (7213), `down`.
# Layout: tents above ground, Void-Smith's forge and cold-storage
# below ground, and a Void Chamber beyond the cold-storage.

SECOND_BREATH_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 7262,
        "name": "Second Breath -- Camp Edge",
        "description": (
            "A sunken hollow in the Dark Dawn Battlefield where the "
            "ground has been hollowed out and carefully bermed to hide "
            "the camp from the grass-line. Dome-tents of oiled canvas "
            "stand in a rough circle. The silence here is absolute: "
            "Kin-sense does not return even the faint whisper of one's "
            "own pulse."
        ),
        "exits": {"up": 7213, "north": 7263, "east": 7267,
                  "south": 7268, "west": 7264},
        "flags": ["dangerous", "camp", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7263,
        "name": "Second Breath -- Perimeter Tents",
        "description": (
            "A pair of small canvas tents set at the camp's outer ring. "
            "The bedding is neat, the weapons are oiled, the personal "
            "effects are spartan. A lantern burns outside each tent's "
            "flap, turned low. Two figures sit just inside the nearest "
            "tent, watching the approach, their eyes catching the "
            "lantern-light at an odd angle."
        ),
        "exits": {"south": 7262, "east": 7266, "north": 7265},
        "flags": ["dangerous", "camp", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7264,
        "name": "Second Breath -- Command Tent",
        "description": (
            "A larger tent at the camp's western edge, its sides "
            "painted with an iron-circle sigil. Inside, a field-desk "
            "holds a sand-map of the surrounding dead zone and a neat "
            "stack of dispatches in Dómnathar script. A tall slender "
            "figure reads by a hooded lamp and does not look up "
            "immediately."
        ),
        "exits": {"east": 7262},
        "flags": ["dangerous", "camp", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7265,
        "name": "Second Breath -- The Mother-Superior's Tent",
        "description": (
            "A stately canvas pavilion at the camp's heart, larger "
            "than the others, floored with overlapping rugs. Low-burning "
            "brass lamps cast pools of warm light. At a writing-desk "
            "sits a stern matriarch with grey-streaked hair coiled "
            "beneath a circle of iron. She has been expecting this "
            "interruption for several years; she is pleased it is "
            "finally here."
        ),
        "exits": {"south": 7263, "east": 7269},
        "flags": ["dangerous", "camp", "silence_zone", "boss_room",
                  "second_breath"],
    },
    {
        "vnum": 7266,
        "name": "Second Breath -- Medicine Tent",
        "description": (
            "A smaller tent hung with drying-lines of herbs and "
            "bandages. A stone-topped work-table holds the tools of "
            "the camp's physician-priest -- surgical instruments, "
            "suture-thread, vials of strange unguents. The priest "
            "himself, in blackened leather, is mid-stitch on a "
            "Silentborn whose shoulder has been recently opened."
        ),
        "exits": {"west": 7263, "south": 7267},
        "flags": ["dangerous", "camp", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7267,
        "name": "Second Breath -- Scout Bunker",
        "description": (
            "A half-buried canvas bunker from which the camp's scouts "
            "track the dead zone's shifting boundaries. Maps of the "
            "battlefield in various stages of accuracy are pinned to "
            "the canvas walls. A few pieces of captured Kin gear -- a "
            "Pasua scarf, a Wind-Rider stirrup -- hang from pegs as "
            "trophies."
        ),
        "exits": {"west": 7262, "north": 7266},
        "flags": ["dangerous", "camp", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7268,
        "name": "Second Breath -- Supply Cache",
        "description": (
            "A deep pit-tent stocked with food-barrels, water-skins, "
            "and neatly-rolled reserves of canvas for new tents. A "
            "separate locked chest contains the camp's emergency "
            "reserve: coin, travel-papers in several Kin languages, "
            "and suppressor-iron collars for evacuating the children "
            "in the cold-storage below."
        ),
        "exits": {"north": 7262, "east": 7269},
        "flags": ["dangerous", "camp", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7269,
        "name": "Second Breath -- Hidden Stair",
        "description": (
            "A camouflaged trapdoor under the Mother-Superior's rug "
            "opens onto a stone stair descending sharply into the "
            "earth. The stone is old Pekakarlik work -- the stair "
            "predates the dead zone. The camp was built here "
            "specifically to guard what lies below."
        ),
        "exits": {"west": 7265, "down": 7270, "up": 7268},
        "flags": ["indoor", "dangerous", "underground", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7270,
        "name": "Second Breath -- Understage Hall",
        "description": (
            "A stone antechamber at the bottom of the stair, lit by "
            "brass-and-crystal lamps set into the walls. The work is "
            "old and precise. A corridor leads east toward the forge; "
            "another leads north toward the quarters and the cold-"
            "storage. The air is cool and still."
        ),
        "exits": {"up": 7269, "east": 7271, "north": 7273,
                  "south": 7278},
        "flags": ["indoor", "dangerous", "underground", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7271,
        "name": "Second Breath -- Void-Smith's Forge",
        "description": (
            "A forge-chamber whose anvil runs with a perpetual rime of "
            "frost despite the banked coals. A Dark Dwarf smith works "
            "here, inking the inner surface of an iron collar with a "
            "brass stylus, her beard threaded with silver wire. She is "
            "making suppressor-irons to fit the next cold-storage "
            "evacuation."
        ),
        "exits": {"west": 7270, "south": 7272},
        "flags": ["indoor", "dangerous", "underground",
                  "second_breath"],
    },
    {
        "vnum": 7272,
        "name": "Second Breath -- Suppressor-Iron Workroom",
        "description": (
            "A small fitting-room beside the forge, hung with "
            "completed collars of various sizes, from infant to adult. "
            "Each is precisely labeled in Dómnathar script with the "
            "Silentborn they are intended for. The inventory has "
            "recently grown."
        ),
        "exits": {"north": 7271},
        "flags": ["indoor", "dangerous", "underground",
                  "second_breath"],
    },
    {
        "vnum": 7273,
        "name": "Second Breath -- Silentborn Quarters",
        "description": (
            "A row of private rooms for the camp's ranking Silentborn. "
            "The decoration is understated and personal: a pressed "
            "flower in a frame, a small sand-garden, a bookcase of "
            "well-read volumes in Kin script. These are people who "
            "have lived quietly here for decades."
        ),
        "exits": {"south": 7270, "east": 7274, "north": 7275},
        "flags": ["indoor", "dangerous", "underground",
                  "second_breath"],
    },
    {
        "vnum": 7274,
        "name": "Second Breath -- Loyalist Barracks",
        "description": (
            "A dormitory for the camp's Silentborn warriors. The bunks "
            "are neat, the weapon-racks are orderly. Sleeping rolls "
            "are double-stacked because the barracks houses more "
            "troopers than it was designed for. A whiteboard at one "
            "end bears the current watch-roster in chalk."
        ),
        "exits": {"west": 7273, "north": 7276},
        "flags": ["indoor", "dangerous", "underground",
                  "second_breath"],
    },
    {
        "vnum": 7275,
        "name": "Second Breath -- Cold Storage Corridor",
        "description": (
            "A descent-corridor whose temperature drops sharply as one "
            "walks it. Old Pekakarlik cold-stones are set into the "
            "walls at intervals, their faces rimed with frost. The "
            "corridor's far end is a heavy iron-bound door with no "
            "obvious lock-mechanism."
        ),
        "exits": {"south": 7273, "north": 7276, "east": 7277},
        "flags": ["indoor", "dangerous", "underground",
                  "second_breath"],
    },
    {
        "vnum": 7276,
        "name": "Second Breath -- Cold Storage Chamber",
        "description": (
            "A bitterly cold stone chamber lined with shelving, and on "
            "the shelves are sealed glass caskets. Twelve, this "
            "morning. Inside each casket, suspended in amber-colored "
            "solution, a Silentborn infant sleeps a sleep that is not "
            "natural. Each casket bears a small brass plaque with a "
            "date and a number. The cold is the only sound."
        ),
        "exits": {"south": 7274, "east": 7275},
        "flags": ["indoor", "dangerous", "underground", "horror",
                  "second_breath"],
    },
    {
        "vnum": 7277,
        "name": "Second Breath -- Assassin's Rest",
        "description": (
            "A small private cell claimed by the camp's resident "
            "Silentborn assassin, who takes his work home with him. "
            "The walls are bare stone; a single bedroll, a weapon-"
            "stand of five knives and no swords, a small altar to "
            "nothing in particular. The assassin himself is here now, "
            "oiling a blade."
        ),
        "exits": {"west": 7275},
        "flags": ["indoor", "dangerous", "underground",
                  "second_breath"],
    },
    {
        "vnum": 7278,
        "name": "Second Breath -- Void Chamber Approach",
        "description": (
            "A narrow corridor whose walls are inlaid with silence-"
            "runes. Sound drops away step by step as one walks it. At "
            "the corridor's end, a pair of Dómnathar-worked doors of "
            "dark iron stand partially open. The light beyond is "
            "strange -- not dim, but oddly wavelength-shifted."
        ),
        "exits": {"north": 7270, "south": 7279},
        "flags": ["indoor", "dangerous", "underground", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7279,
        "name": "Second Breath -- The Void Chamber",
        "description": (
            "A circular room whose floor is a shallow pool of "
            "absolutely black water held within a silver rim. A "
            "Dómnathar sorceress stands at the pool's far edge, her "
            "hand resting on the silver rim. The water does not ripple "
            "when she moves. She is scrying the Spur Tower; the "
            "Mother-Superior reports weekly through this pool."
        ),
        "exits": {"north": 7278, "south": 7280, "east": 7281,
                  "west": 7282},
        "flags": ["indoor", "dangerous", "underground", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7280,
        "name": "Second Breath -- Memorial Alcove",
        "description": (
            "A small niche off the Void Chamber whose only feature is "
            "a shelf bearing seven small iron circles, each inscribed "
            "with a Dómnathar name. These are the camp's dead -- the "
            "agents who were caught and did not come back. The shelf "
            "has room for many more."
        ),
        "exits": {"north": 7279},
        "flags": ["indoor", "underground", "silence_zone",
                  "second_breath"],
    },
    {
        "vnum": 7281,
        "name": "Second Breath -- Records Cache",
        "description": (
            "A locked alcove containing the camp's most sensitive "
            "records: the lineage-charts of every Silentborn it has "
            "produced, the signed loyalty-oaths, and a ledger of "
            "informants distributed across the Kin lands. If these "
            "records were ever to escape, the Kin intelligence services "
            "would have an unlooked-for season of bloody bureaucracy."
        ),
        "exits": {"west": 7279},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "second_breath"],
    },
    {
        "vnum": 7282,
        "name": "Second Breath -- Escape Tunnel",
        "description": (
            "A narrow stone-cut passage leading away from the Void "
            "Chamber. The tunnel descends, eventually to depths the "
            "camp's scouts have not fully mapped. This is the Mother-"
            "Superior's personal exit, and she has used it only once, "
            "twenty years ago, when a Kin patrol came unexpectedly "
            "close to the camp."
        ),
        "exits": {"east": 7279, "down": 7283},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 7283,
        "name": "Second Breath -- Dead-Zone Terminus",
        "description": (
            "The escape tunnel ends in a small chamber whose walls are "
            "inlaid with unfamiliar iron sigils. The silence here is "
            "total; no sound can be made to travel. A small stone door "
            "in the far wall waits, unopened in the camp's memory. "
            "Beyond it, according to the Mother-Superior's notes, "
            "lies the deeper tunnel-network the Shattered Host has "
            "been building under the Steppe for three centuries."
        ),
        "exits": {"up": 7282},
        "flags": ["indoor", "dangerous", "underground", "silence_zone"],
    },
]


# ===========================================================================
# Outbound exits from existing rooms
# ===========================================================================

NEW_EXITS = [
    # Burnt Hollows: repoint 7225's broken `down` -> new zone entry
    (7225, "down", 7246),

    # Second Breath: concealed descent from Dark Dawn Central Zone
    (7213, "down", 7262),
]


# ===========================================================================
# Mob spawns (vnums 3800-3824) -- clone from bestiary
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
LT_POTION     = [{"vnum": 301, "chance": 0.2}]
LT_MW_SWORD   = [{"vnum": 700, "chance": 0.35}]
LT_MW_ARMOR   = [{"vnum": 701, "chance": 0.30}]
LT_WARDAMUL   = [{"vnum": 703, "chance": 0.30}]
LT_DARKIRON_D = [{"vnum": 705, "chance": 0.35}]
LT_FIRECLOAK  = [{"vnum": 706, "chance": 0.35}]
LT_VOIDHAMMER = [{"vnum": 707, "chance": 0.45}]
LT_TABLET     = [{"vnum": 708, "chance": 0.55}]
LT_DARKIRON_L = [{"vnum": 709, "chance": 0.45}]
LT_COLLAR     = [{"vnum": 710, "chance": 0.60}]
LT_VOIDROD    = [{"vnum": 711, "chance": 0.80}]


SPAWN_SPEC = [
    # --- Burnt Hollows (3800-3810) ---------------------------------------
    (3800, "Goblin Shaman (Adept 3)",                7249,
            LT_POTION + LT_FIRECLOAK),
    (3801, "Hobgoblin Sergeant (Fighter 2)",         7255,
            LT_MW_ARMOR + LT_DARKIRON_L + LT_TABLET),
    (3802, "Flamewarg Cult Initiate (Sorcerer 3, Human)", 7251,
            LT_FIRECLOAK + LT_POTION + LT_DARKIRON_D),
    (3803, "Flamewarg Cult Initiate (Sorcerer 3, Human)", 7251,
            LT_FIRECLOAK + LT_POTION),
    (3804, "Flamewarg Cult Initiate (Sorcerer 3, Human)", 7251,
            LT_COINS + LT_FIRECLOAK),
    (3805, "Half-Dómnathar Cult-Leader (Sorcerer 6)", 7251,
            LT_MW_SWORD + LT_VOIDHAMMER + LT_FIRECLOAK + LT_TABLET + LT_POTION),
    (3806, "Kobold Fire-Sorcerer (Sorcerer 5)",      7256,
            LT_FIRECLOAK + LT_POTION),
    (3807, "Kobold Cultist (Cleric 2)",              7249,
            LT_POTION + LT_FIRECLOAK),
    (3808, "Hobgoblin Tunnel-Warden (Fighter 3 / Ranger 1)", 7259,
            LT_MW_SWORD + LT_MW_ARMOR),
    (3809, "Dark Dwarf Warrior (Fighter 3)",         7258,
            LT_DARKIRON_L + LT_MW_ARMOR),
    (3810, "Dark Dwarf Scavenger-Lord (Rogue 4)",    7258,
            LT_MW_SWORD + LT_DARKIRON_D + LT_TABLET),

    # --- Second Breath Hideout (3811-3824) -------------------------------
    (3811, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 7263,
            LT_DARKIRON_L + LT_COLLAR),
    (3812, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 7263,
            LT_MW_ARMOR + LT_COLLAR),
    (3813, "Dómnathar Infiltrator (Rogue 6 / Fighter 2)", 7264,
            LT_MW_SWORD + LT_VOIDHAMMER + LT_TABLET),
    (3814, "Half-Dómnathar Mother-Superior (Cleric 8)", 7265,
            LT_VOIDHAMMER + LT_VOIDROD + LT_COLLAR + LT_WARDAMUL + LT_TABLET),
    (3815, "Silentborn Battle-Priest (Cleric 5)",    7266,
            LT_VOIDHAMMER + LT_MW_ARMOR + LT_POTION),
    (3816, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 7267,
            LT_MW_SWORD + LT_COINS),
    (3817, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 7268,
            LT_COLLAR + LT_MW_ARMOR),
    (3818, "Dark Dwarf Void-Smith (Expert 7 / Wizard 1)", 7271,
            LT_COLLAR + LT_DARKIRON_L + LT_TABLET),
    (3819, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 7273,
            LT_DARKIRON_L),
    (3820, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 7274,
            LT_MW_SWORD + LT_COLLAR),
    (3821, "Silentborn Loyalist (Warrior 3 / Rogue 1)", 7274,
            LT_MW_ARMOR + LT_POTION),
    (3822, "Silentborn Researcher (Wizard 4)",       7276,
            LT_POTION + LT_TABLET),
    (3823, "Silentborn Assassin (Rogue 5 / Assassin 2)", 7277,
            LT_MW_SWORD + LT_POTION + LT_TABLET + LT_COLLAR),
    (3824, "Dómnathar Sorcerer (Sorcerer 8)",        7279,
            LT_VOIDHAMMER + LT_COLLAR + LT_TABLET + LT_WARDAMUL),
]


# ===========================================================================
# Merge logic
# ===========================================================================

def _read(p):
    with open(p, "r", encoding="utf-8") as f: return json.load(f)
def _write(p, o):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(o, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def merge_rooms():
    path = os.path.join(DATA, "areas", "EternalSteppe.json")
    rooms = _read(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0
    for r in BURNT_HOLLOWS_ROOMS + SECOND_BREATH_ROOMS:
        if r["vnum"] in existing:
            continue
        rooms.append(r)
        existing.add(r["vnum"])
        added += 1

    by_vnum = {r["vnum"]: r for r in rooms}
    wired = 0
    for src_v, direction, dest_v in NEW_EXITS:
        r = by_vnum.get(src_v)
        if r is None: continue
        exits = r.setdefault("exits", {})
        # For E-Steppe we WANT to overwrite 7225's broken `down` exit.
        # Explicitly allow overwrite for the two known rewires.
        if exits.get(direction) == dest_v:
            continue
        exits[direction] = dest_v
        wired += 1

    _write(path, rooms)
    print(f"  EternalSteppe.json: +{added} rooms, {wired} exits rewired "
          f"(total {len(rooms)})")


def merge_mobs():
    mobs_path = os.path.join(DATA, "mobs.json")
    bestiary = _read(os.path.join(DATA, "mobs_bestiary.json"))
    mobs = _read(mobs_path)
    existing = {m.get("vnum") for m in mobs}
    added = 0
    for vnum, best_name, room_vnum, loot in SPAWN_SPEC:
        if vnum in existing:
            continue
        try:
            mobs.append(_spawn(vnum, best_name, room_vnum,
                               bestiary=bestiary, loot=loot))
            added += 1
        except KeyError as e:
            print(f"  WARN: {e}")
    _write(mobs_path, mobs)
    print(f"  mobs.json: +{added} new spawns (total {len(mobs)})")


def main() -> int:
    print("Building Eternal Steppe Deceiver zones:")
    merge_rooms()
    merge_mobs()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
