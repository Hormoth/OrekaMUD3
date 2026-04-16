"""Build the Deepwater Marches Deceiver zones.

Extends two partially-built zones in ``data/areas/DeepwaterMarches.json``:

  * Zone D1 -- Ashcrown Warren (+9 rooms, vnums 9360-9368)
    9 scaffolded rooms already exist (9350-9358). This adds 9 more to
    reach the full 18-room zone, including the Half-Dómnathar Broker's
    salon and the enslaved human informant.  Level band 5-8.

  * Zone D2 -- The Spur Tower Interior (+31 rooms, vnums 9369-9399)
    3 placeholder rooms already exist (9305, 9306, 9307 as floors 1-3).
    This adds 31 rooms to build out all 5 floors: Guard Barracks,
    Archive, Breeding Lab, Command, and the Void Chamber + Throne
    where the CR 17 House Leader waits.  Level band 16-19.

Also adds ~29 mob spawns and 3 themed items.

Idempotent by vnum. Run:
    python scripts/build_deepwater_deceiver_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ===========================================================================
# Zone D1 -- Ashcrown Warren extension (9 new rooms)
# ===========================================================================
# Existing rooms:
#   9350 Jungle Approach / 9351 Outer Burrow Entrance / 9352 Upper Tunnel
#   9353 Goblin Occupation / 9354 Sealed Section / 9355 Hobgoblin Patrol
#   9356 Lower Tunnel (Goblin Access) / 9357 Sealed Deep Level
#   9358 Collapsed Section

ASHCROWN_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 9360,
        "name": "Ashcrown Warren -- Common Market",
        "description": (
            "A wider chamber at the heart of the warren, where the "
            "goblins run a crude market for whatever their raiders bring "
            "home. A trestle-table doubles as a butcher's block and a "
            "display rack. A hobgoblin 'tribute collector' in Shattered "
            "Host colors sits at the far end, ticking off goods on a "
            "slate. He is ignored as a visitor who never quite leaves."
        ),
        "exits": {"west": 9356, "north": 9361, "east": 9363,
                  "south": 9364},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9361,
        "name": "Ashcrown Warren -- The Broker's Salon",
        "description": (
            "A room that does not belong in a goblin warren. The walls "
            "are hung with good tapestries, the floor is laid with "
            "layered rugs, and a small iron-bound writing-desk sits "
            "under a lacquered reading-lamp. A Half-Dómnathar broker "
            "in traveling silks sits behind the desk, turning over a "
            "ledger. Two Silentborn attendants stand behind her, "
            "watching."
        ),
        "exits": {"south": 9360, "east": 9362},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9362,
        "name": "Ashcrown Warren -- Kitchen (Captive Quarters)",
        "description": (
            "A smoke-stained kitchen where the broker's meals are "
            "prepared and the warren's stew-pot simmers. The cook is "
            "a weary human woman with a slave-collar of dark iron; she "
            "speaks only in whispers and only when she is sure no "
            "goblin is listening. She may have information worth more "
            "than any silver in this warren."
        ),
        "exits": {"west": 9361, "south": 9363},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9363,
        "name": "Ashcrown Warren -- Goblin Shaman's Shrine",
        "description": (
            "A crudely-built shrine to a god whose carving is so rough "
            "it could be almost anything. The goblin shaman has hung "
            "crossed-out-sun banners above the altar -- the mark of the "
            "Flamewarg faith. He burns scraps of hair and paper to read "
            "the futures of his own clan, which have recently been very "
            "cloudy."
        ),
        "exits": {"west": 9360, "north": 9362, "south": 9365},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9364,
        "name": "Ashcrown Warren -- Flamewarg Pen",
        "description": (
            "A stinking kennel where the warren's single Flamewarg "
            "is kept between raids. The beast is a wolf-sized creature "
            "whose coat glows faintly orange at the roots, a descendant "
            "of the war-wolves the Deceivers brought through the "
            "Breach. It watches visitors with very old, very alert eyes."
        ),
        "exits": {"north": 9360, "east": 9365},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9365,
        "name": "Ashcrown Warren -- Tribute Storeroom",
        "description": (
            "A locked strongroom where the warren's take is sorted into "
            "barrels and crates for transport to the Spur Tower. Two "
            "hobgoblins lounge by the door, eating travel-bread from a "
            "cloth and bored enough to welcome an interruption. Behind "
            "them, the goods are labeled in ink: 'FOR THE SPUR,' 'FOR "
            "THE MARKET,' and 'FOR THE FIRE.'"
        ),
        "exits": {"north": 9363, "west": 9364, "east": 9366},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9366,
        "name": "Ashcrown Warren -- Slave Pen",
        "description": (
            "A low-ceilinged chamber with iron-barred cells along two "
            "walls. Four captives are currently held: a Pasua scout "
            "with a crude splint on her arm, two human travelers who "
            "do not yet understand what has happened to them, and a "
            "silent figure in a cloak whose face is not clearly human. "
            "Rescue is possible, but the goblins will give chase."
        ),
        "exits": {"west": 9365, "east": 9367},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9367,
        "name": "Ashcrown Warren -- Smuggling Chamber",
        "description": (
            "A small side-vault built into the wall of the tribute "
            "storeroom, accessed only through a narrow passage. Inside, "
            "carefully wrapped in oiled silk, are the items the broker "
            "does not want the Spur Tower to know she has kept: a rack "
            "of Deceiver spell-foci, three sealed letters in her own "
            "hand, and a small jeweled pectoral of unknown provenance."
        ),
        "exits": {"west": 9366, "south": 9368},
        "flags": ["indoor", "dangerous", "underground", "goblin_warren"],
    },
    {
        "vnum": 9368,
        "name": "Ashcrown Warren -- Deep Escape Tunnel",
        "description": (
            "A long downward-sloping passage cut by Pekakarlik hands "
            "centuries ago, re-opened by goblin work-gangs at the "
            "broker's direction. Somewhere far along this tunnel, it "
            "connects to the deep approaches of the Spur Tower. The "
            "broker uses it to move contraband. The occasional skeleton "
            "in the side-alcoves suggests she also uses it to move "
            "problems."
        ),
        "exits": {"north": 9367},
        "flags": ["indoor", "dangerous", "underground"],
    },
]


# ===========================================================================
# Zone D2 -- Spur Tower Interior (31 new rooms across 5 floors)
# ===========================================================================
# Existing: 9305 Tower First, 9306 Tower Second, 9307 Tower Upper (stubs)
# New 9369-9399 fill out the five floors.

SPUR_ROOMS: List[Dict[str, Any]] = [
    # --- Floor 1 (Guard Barracks): 9305 + 9369-9373 ----------------------
    {
        "vnum": 9369,
        "name": "Spur Tower -- Guard Common",
        "description": (
            "A common hall off the tower entry, dominated by a long "
            "trestle-table and a rack of pole-weapons. Hobgoblin "
            "standers-to-watch eat and rest here between shifts. The "
            "discipline is perfect; the mood is quiet and tense. "
            "No one laughs in the Spur."
        ),
        "exits": {"west": 9305, "north": 9370, "east": 9371,
                  "south": 9373},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9370,
        "name": "Spur Tower -- Guard Barracks",
        "description": (
            "Two rows of straw-stuffed pallets line the walls of this "
            "long dormitory. The floor is polished smooth by centuries "
            "of bootsteps. A small shrine-niche at one end holds a "
            "featureless black stone -- the House's god, whose name "
            "the garrison refuses to speak aloud."
        ),
        "exits": {"south": 9369, "east": 9371},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9371,
        "name": "Spur Tower -- Officers' Mess",
        "description": (
            "A smaller dining-room for the tower's ranking hobgoblins "
            "and infiltrators. A Dómnathar officer in traveling leathers "
            "sits at the head of the table, reading a field-report by "
            "lamplight. He looks up as you enter; his eyes catch the "
            "lamp at a slightly wrong angle. He has been killing Kin "
            "scouts for three hundred years and is pleased by the "
            "prospect of more."
        ),
        "exits": {"west": 9369, "south": 9370, "east": 9372},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9372,
        "name": "Spur Tower -- Outer Armory",
        "description": (
            "Racks and racks of dark-iron weapons, neatly oiled and "
            "labeled. A locked cage in the back holds a half-dozen "
            "enchanted longswords and a single suit of rune-etched "
            "plate the garrison's officers rotate through as the "
            "active Champion. A weapon-smith's workbench shows a "
            "repair in progress."
        ),
        "exits": {"west": 9371, "south": 9373},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9373,
        "name": "Spur Tower -- Interrogation Cell",
        "description": (
            "A windowless room with a single iron chair at its center, "
            "bolted to the floor. Tools of unpleasant specificity hang "
            "on hooks along one wall. A Silentborn loyalist polishes "
            "a set of small silver picks at a side-table with the "
            "patience of an artisan who does not expect to be "
            "interrupted today."
        ),
        "exits": {"north": 9369, "east": 9372},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },

    # --- Floor 2 (Archive): 9306 + 9374-9378 -----------------------------
    {
        "vnum": 9374,
        "name": "Spur Tower -- Archive Hall",
        "description": (
            "A grand library-hall whose shelves climb thirty feet to a "
            "vaulted ceiling lit by slow-burning oil-lamps in recessed "
            "niches. The books are bound in dark leather, each spine "
            "bearing a small silver sigil that glows faintly in the "
            "presence of unauthorized readers. Several sigils are "
            "flickering."
        ),
        "exits": {"west": 9306, "north": 9375, "east": 9376,
                  "south": 9378},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9375,
        "name": "Spur Tower -- Scribes' Room",
        "description": (
            "A long workroom filled with slanted writing-desks where "
            "Silentborn scribes copy captured Kin texts and transliterate "
            "them into Dómnathar script. The ink-pots are elaborate; "
            "the pens are quills plucked from birds that do not "
            "exist in the Kin's taxonomies."
        ),
        "exits": {"south": 9374, "east": 9376},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9376,
        "name": "Spur Tower -- Lore-Keeper's Study",
        "description": (
            "A private study whose walls are shelved floor-to-ceiling in "
            "leather-bound codices. A Dark Dwarf of great age sits "
            "cross-legged on a mat at the center, a book open in her "
            "lap though her eyes are milky with cataracts. Her memory "
            "supplies what her eyes no longer can. She is the living "
            "archive of three centuries of Shattered Host lineages."
        ),
        "exits": {"west": 9374, "north": 9375, "south": 9377},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9377,
        "name": "Spur Tower -- Cipher Room",
        "description": (
            "A small office devoted to codebreaking and cipher-work. "
            "A table in the middle is piled high with Kin military "
            "dispatches in various stages of translation. Silver "
            "decoder-rings hang on pegs along one wall. Whoever reads "
            "these knows far more about Kin plans than the Kin would "
            "prefer."
        ),
        "exits": {"north": 9376, "south": 9378},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9378,
        "name": "Spur Tower -- Forbidden Texts",
        "description": (
            "A locked vault behind a stone door with three bronze keys "
            "set into its face. Inside, held upright in crystal cases, "
            "are the Archive's most sensitive volumes: the breeding-"
            "program logs, the genealogy of every Silentborn ever "
            "produced, and a single black-bound diary in the "
            "personal hand of the House Leader."
        ),
        "exits": {"north": 9374, "east": 9377},
        "flags": ["indoor", "dangerous", "trapped", "fortress",
                  "tower_spur"],
    },

    # --- Floor 3 (Breeding Lab): 9307 + 9379-9383 ------------------------
    {
        "vnum": 9379,
        "name": "Spur Tower -- Lab Corridor",
        "description": (
            "A long clinical corridor lined with doors that do not "
            "speak their function. The floor is tiled in white stone "
            "that shows every stain. Somewhere along this corridor "
            "something is gently weeping, and no one is coming."
        ),
        "exits": {"west": 9307, "north": 9380, "east": 9381,
                  "south": 9383},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9380,
        "name": "Spur Tower -- Researcher's Workshop",
        "description": (
            "A long counter-room whose surfaces are covered with glass "
            "apparatus, ceramic beakers, leather-bound notebooks, and "
            "rows of specimen-jars arranged by contents rather than "
            "size. A Silentborn researcher in spotless aprons bends "
            "over a microscope; she is good at her work and takes "
            "nothing personally."
        ),
        "exits": {"south": 9379, "east": 9381},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9381,
        "name": "Spur Tower -- Incubation Chamber",
        "description": (
            "A warm, humid chamber lined with rows of heated cabinets "
            "each holding a delicate glass vessel. Inside each vessel, "
            "suspended in amber-colored solution, is a small shape the "
            "size of a thumb. They move. A Half-Dómnathar priest in "
            "hooded vestments tends the vessels with a doctor's gentle "
            "patience."
        ),
        "exits": {"west": 9379, "north": 9380, "east": 9382},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur"],
    },
    {
        "vnum": 9382,
        "name": "Spur Tower -- Cold Storage",
        "description": (
            "A chamber kept bitterly cold by old Pekakarlik cold-stones "
            "set into the walls. Stacked on shelves are sealed glass "
            "caskets, each containing a Silentborn infant in stasis. "
            "There are perhaps forty. They are catalogued by date of "
            "extraction from the incubator. The oldest is eleven years "
            "stored; the youngest is this past spring."
        ),
        "exits": {"west": 9381, "south": 9383},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "horror"],
    },
    {
        "vnum": 9383,
        "name": "Spur Tower -- Test Subject Holding",
        "description": (
            "A secure ward for the Mother-Superior's long-running "
            "projects. Behind iron-barred cells, a dozen Silentborn of "
            "various ages wait in silence. Some are fully adult, still "
            "here because the Mother-Superior has not yet decided what "
            "to do with them. The Mother-Superior herself stands at the "
            "center of the ward, reviewing a clipboard."
        ),
        "exits": {"north": 9379, "west": 9382},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "horror"],
    },

    # --- Floor 4 (Command): 9384-9389 ------------------------------------
    {
        "vnum": 9384,
        "name": "Spur Tower -- Command Stair Landing",
        "description": (
            "A modest landing at the top of the stair that climbs from "
            "the breeding-floor below. The walls here are the first "
            "bare stone the tower shows; the painted plaster of the "
            "lower levels has been replaced with plain dressed "
            "basalt, a deliberate austerity that signals seriousness "
            "of purpose."
        ),
        "exits": {"down": 9307, "north": 9385, "east": 9386,
                  "west": 9388, "up": 9390},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "command"],
    },
    {
        "vnum": 9385,
        "name": "Spur Tower -- Officers' Hall",
        "description": (
            "The command floor's shared office: a long chamber with "
            "individual writing-desks along the walls, each assigned "
            "to a Half-Dómnathar officer of rank. Most sit empty at "
            "this hour; two are occupied by scholarly-looking figures "
            "who look up at intruders with polite, professional "
            "interest that does not extend to mercy."
        ),
        "exits": {"south": 9384, "east": 9386},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "command"],
    },
    {
        "vnum": 9386,
        "name": "Spur Tower -- Void-Sorcerer's Study",
        "description": (
            "A circular chamber whose walls are shelved with grimoires "
            "and whose floor is inlaid with a complex silver diagram "
            "-- an astrolabe rendered in spellwork. A Dómnathar "
            "sorceress sits at the diagram's heart, one slender finger "
            "tracing a pattern that illuminates points she touches. "
            "She turns her head without surprise at your arrival."
        ),
        "exits": {"west": 9384, "south": 9385, "east": 9387},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "command"],
    },
    {
        "vnum": 9387,
        "name": "Spur Tower -- Captive Scholar's Cell",
        "description": (
            "A comfortable room with a bed, writing-desk, and shelf of "
            "hand-copied reference texts. At the desk sits an Elf in "
            "worn but clean scholar's robes. His ankles bear iron "
            "shackles with a longer-than-normal chain; he has lived "
            "here for eleven years. His captors think he is tame. He "
            "is not, quite."
        ),
        "exits": {"west": 9386},
        "flags": ["indoor", "fortress", "tower_spur", "command"],
    },
    {
        "vnum": 9388,
        "name": "Spur Tower -- Guard Post",
        "description": (
            "A short corridor-chamber whose only decoration is the "
            "creature standing silent guard at its far end. An eight-"
            "foot construct of dark obsidian holds the position of "
            "parade-rest, unmoving, unbreathing. The air around it is "
            "cold. It will move when it has a reason."
        ),
        "exits": {"east": 9384, "north": 9389},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "command"],
    },
    {
        "vnum": 9389,
        "name": "Spur Tower -- Ante-Throne",
        "description": (
            "A narrow hall of featureless black stone that serves as "
            "the approach to the command floor's greater chamber above. "
            "The hall is kept deliberately empty -- no chair, no "
            "decoration, no relief. Whoever walks this hall is meant to "
            "feel both the plainness of it and their own footfalls "
            "echoing."
        ),
        "exits": {"south": 9388, "up": 9391},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "command"],
    },

    # --- Floor 5 (The Void Chamber): 9390-9399 ---------------------------
    {
        "vnum": 9390,
        "name": "Spur Tower -- Throne Stair Approach",
        "description": (
            "The top of the narrow stair from the Command floor opens "
            "into a short columned approach. Each column is carved with "
            "a different line of Dómnathar script -- histories, oaths, "
            "curses -- so closely cut that the columns themselves seem "
            "to be speaking in a whisper just below the threshold of "
            "hearing."
        ),
        "exits": {"down": 9384, "north": 9391},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "throne"],
    },
    {
        "vnum": 9391,
        "name": "Spur Tower -- Silence Corridor",
        "description": (
            "A long corridor whose walls are inlaid with unfamiliar runes "
            "that absorb sound. Visitors' footfalls stop echoing after "
            "three paces; whispered words do not travel. A Dark Dwarf "
            "lore-keeper, milky-eyed and ancient, stands as the "
            "corridor's warden. An obsidian Void-Construct waits at the "
            "far end beside the throne doors. Neither speaks."
        ),
        "exits": {"south": 9390, "north": 9392},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "throne", "silence_zone"],
    },
    {
        "vnum": 9392,
        "name": "Spur Tower -- The Audience Chamber",
        "description": (
            "The throne hall is larger than any other room in the tower "
            "and also the quietest. At its far end rises a low dais of "
            "black basalt, and on the dais a stone seat without "
            "ornament. Seated on the seat is a tall figure of great "
            "and terrible age, whose eyes catch the lamplight with the "
            "faint yellow of something submerged. He does not stand as "
            "intruders approach. His name is not spoken, even by his "
            "servants. He has been here four hundred and eighty-seven "
            "years, and he has been expecting this day."
        ),
        "exits": {"south": 9391, "east": 9393, "west": 9394,
                  "up": 9396},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "throne", "boss_room"],
    },
    {
        "vnum": 9393,
        "name": "Spur Tower -- Sanctum of the Void",
        "description": (
            "A small private chamber adjacent to the throne, whose "
            "single feature is a basin of impossibly still black water "
            "set on a plinth. The basin does not ripple even when "
            "approached. The House Leader uses it for scrying and for "
            "silence. Dropping anything into the water results in a "
            "perfectly soundless disappearance."
        ),
        "exits": {"west": 9392},
        "flags": ["indoor", "dangerous", "fortress", "tower_spur",
                  "throne"],
    },
    {
        "vnum": 9394,
        "name": "Spur Tower -- Vault Approach",
        "description": (
            "A heavy iron-bound door marks the entrance to the tower's "
            "private vault. The door is worked in dark iron and bears "
            "three locks, each of a different Dómnathar guild-make. "
            "Two small runes worked into the jamb will discharge upon "
            "forced entry, producing effects that vary -- the guards "
            "pool bets on which on-duty scholar's skin they will flay "
            "off."
        ),
        "exits": {"east": 9392, "west": 9395},
        "flags": ["indoor", "dangerous", "trapped", "fortress",
                  "tower_spur"],
    },
    {
        "vnum": 9395,
        "name": "Spur Tower -- The House Vault",
        "description": (
            "A cold stone vault whose shelves hold the House's small "
            "treasures: the personal items the House Leader has kept "
            "through the centuries. A rack of pre-invasion weapons, a "
            "small chest of House-sigil rings, a sealed coffer of "
            "coinage from before the Kin knew such things, and in a "
            "crystal case on a velvet plinth, an ancient book whose "
            "title is in no living language."
        ),
        "exits": {"east": 9394},
        "flags": ["indoor", "fortress", "tower_spur"],
    },
    {
        "vnum": 9396,
        "name": "Spur Tower -- Upper Observation",
        "description": (
            "A narrow chamber with a single window -- the tower's only "
            "external window on this height -- looking out across the "
            "jungle canopy toward the far shore of the Apelian Sea. "
            "A brass-and-ivory spyglass on a stand is pointed at "
            "nothing in particular, but has been recently used: the "
            "dust on its footplate is disturbed."
        ),
        "exits": {"down": 9392, "east": 9397},
        "flags": ["indoor", "fortress", "tower_spur"],
    },
    {
        "vnum": 9397,
        "name": "Spur Tower -- Hidden Alcove",
        "description": (
            "A small alcove behind a pivot-panel in the observation "
            "chamber, large enough for a single person to stand in "
            "comfortably. Inside is a jeweled box containing three "
            "letters in the House Leader's hand, addressed to three "
            "Dómnathar captains whose locations are not otherwise "
            "recorded. This is the last piece of information any Kin "
            "intelligence officer has ever wanted."
        ),
        "exits": {"west": 9396},
        "flags": ["indoor", "fortress", "tower_spur"],
    },
    {
        "vnum": 9398,
        "name": "Spur Tower -- Descent Shaft",
        "description": (
            "A narrow shaft cut straight down through the tower's core, "
            "braced by iron rungs, and leading into darkness far below "
            "the rock-base of the Spur. The descent goes deeper than "
            "any map in the Kin's possession. This is the House "
            "Leader's private route to the greater tunnels of the "
            "Shattered Host."
        ),
        "exits": {"north": 9396, "down": 9399},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 9399,
        "name": "Spur Tower -- The Void Terminus",
        "description": (
            "The bottom of the descent shaft opens into a chamber whose "
            "floor is an unpolished pool of absolutely black water. "
            "Stones dropped in make no sound; there is no splash. A "
            "passage continues beyond, leading to places that have not "
            "been mapped by anyone living. This is a dead-end for "
            "today. It will not remain one."
        ),
        "exits": {"up": 9398},
        "flags": ["indoor", "dangerous", "underground", "silence_zone"],
    },
]


# ===========================================================================
# Outbound exits from existing rooms into the new zones
# ===========================================================================

NEW_EXITS = [
    # Ashcrown: 9356 Lower Tunnel -> new common market
    # (room 9356 currently: {up: 9352, east: 9357})
    (9356, "south", 9360),

    # Spur Tower: existing stub floors get lateral exits to new rooms
    # 9305 Tower First Level currently: {down: 9304, up: 9306}
    (9305, "east", 9369),
    # 9306 Tower Second Level currently: {down: 9305, up: 9307}
    (9306, "east", 9374),
    # 9307 Tower Upper Level currently: {down: 9306}
    (9307, "east", 9379),
    (9307, "up",   9384),
]


# ===========================================================================
# New themed items (vnums 709-711)
# ===========================================================================

NEW_ITEMS: List[Dict[str, Any]] = [
    {
        "vnum": 709,
        "name": "Dark-Iron Longsword",
        "item_type": "weapon",
        "weight": 4,
        "value": 315,
        "description": (
            "A longsword forged in Deceiver foundries from dark iron. "
            "The blade is blacker than night steel and takes an edge "
            "beautifully. Masterwork: +1 to attack."
        ),
        "damage": [1, 8, 0],
        "properties": ["martial", "masterwork"],
    },
    {
        "vnum": 710,
        "name": "Suppressor-Iron Collar",
        "item_type": "wondrous",
        "weight": 2,
        "value": 4000,
        "description": (
            "A collar of dark iron worked with runes not of Kin script. "
            "When worn, the wearer registers as dead to Kin-sense -- "
            "the same effect the Dómnathar use to hide captives from "
            "search-magic. Neutral in alignment, dangerous in intent."
        ),
        "slot": "neck",
        "properties": ["wondrous", "magical"],
    },
    {
        "vnum": 711,
        "name": "Void-Rod of the Silent Host",
        "item_type": "wondrous",
        "weight": 3,
        "value": 12000,
        "description": (
            "A smooth black rod of unknown material, warm to the touch. "
            "3/day the bearer may cast Silence (DC 15) centered on a "
            "target within 60 ft. 1/day the bearer may cast Dispel "
            "Magic at caster level 12."
        ),
        "properties": ["wondrous", "magical", "charged"],
    },
]


# ===========================================================================
# Mob spawns (vnums 3700-3729)
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


# Loot shortcuts
LT_COINS      = [{"vnum": 2,   "chance": 0.25}]
LT_POTION     = [{"vnum": 301, "chance": 0.2}]
LT_MW_SWORD   = [{"vnum": 700, "chance": 0.25}]
LT_MW_ARMOR   = [{"vnum": 701, "chance": 0.25}]
LT_SIGNET     = [{"vnum": 702, "chance": 0.3}]
LT_WARDAMUL   = [{"vnum": 703, "chance": 0.3}]
LT_DARKIRON_D = [{"vnum": 705, "chance": 0.35}]
LT_FIRECLOAK  = [{"vnum": 706, "chance": 0.35}]
LT_VOIDHAMMER = [{"vnum": 707, "chance": 0.45}]
LT_TABLET     = [{"vnum": 708, "chance": 0.60}]
LT_DARKIRON_L = [{"vnum": 709, "chance": 0.50}]
LT_COLLAR     = [{"vnum": 710, "chance": 0.60}]
LT_VOIDROD    = [{"vnum": 711, "chance": 1.00}]  # House Leader drops it


SPAWN_SPEC = [
    # --- Ashcrown Warren (vnums 3700-3708) -------------------------------
    (3700, "Goblin Shaman (Adept 3)",                  9363,
            LT_POTION + LT_SIGNET),
    (3701, "Hobgoblin Sergeant (Fighter 2)",           9365,
            LT_MW_ARMOR + LT_DARKIRON_L + LT_COINS),
    (3702, "Hobgoblin Sergeant (Fighter 2)",           9360,
            LT_MW_ARMOR + LT_COINS),
    (3703, "Flamewarg Cult Initiate (Sorcerer 3, Human)", 9364,
            LT_FIRECLOAK + LT_POTION),
    (3704, "Half-Dómnathar Broker (Bard 5 / Rogue 2)", 9361,
            LT_MW_SWORD + LT_TABLET + LT_WARDAMUL + LT_POTION),
    (3705, "Silentborn Loyalist (Warrior 3 / Rogue 1)",9361,
            LT_MW_ARMOR + LT_DARKIRON_L),
    (3706, "Silentborn Loyalist (Warrior 3 / Rogue 1)",9361,
            LT_DARKIRON_L + LT_COINS),
    (3707, "Silentborn Loyalist (Warrior 3 / Rogue 1)",9366,
            LT_COINS),
    (3708, "Silentborn Loyalist (Warrior 3 / Rogue 1)",9353,
            LT_MW_SWORD),

    # --- Spur Tower Interior: Floor 1 (3709-3712) ------------------------
    (3709, "Hobgoblin Sergeant (Fighter 2)",           9370,
            LT_MW_ARMOR + LT_DARKIRON_L),
    (3710, "Hobgoblin Tunnel-Warden (Fighter 3 / Ranger 1)", 9372,
            LT_MW_SWORD + LT_MW_ARMOR),
    (3711, "Dómnathar Infiltrator (Rogue 6 / Fighter 2)", 9371,
            LT_MW_SWORD + LT_VOIDHAMMER + LT_TABLET),
    (3712, "Silentborn Loyalist (Warrior 3 / Rogue 1)",9373,
            LT_DARKIRON_L + LT_COLLAR),

    # --- Spur Tower Interior: Floor 2 (3713-3716) ------------------------
    (3713, "Silentborn Researcher (Wizard 4)",         9375,
            LT_POTION + LT_TABLET),
    (3714, "Dark Dwarf Lore-Keeper (Cleric 9)",        9376,
            LT_VOIDHAMMER + LT_TABLET + LT_SIGNET),
    (3715, "Silentborn Researcher (Wizard 4)",         9377,
            LT_TABLET),
    (3716, "Silentborn Researcher (Wizard 4)",         9378,
            LT_POTION),

    # --- Spur Tower Interior: Floor 3 (3717-3720) ------------------------
    (3717, "Silentborn Researcher (Wizard 4)",         9380,
            LT_POTION + LT_MW_ARMOR),
    (3718, "Half-Dómnathar Battle-Priest (Cleric 7)",  9381,
            LT_VOIDHAMMER + LT_MW_ARMOR + LT_COLLAR),
    (3719, "Silentborn Researcher (Wizard 4)",         9382,
            LT_POTION),
    (3720, "Half-Dómnathar Mother-Superior (Cleric 8)",9383,
            LT_VOIDHAMMER + LT_WARDAMUL + LT_COLLAR + LT_TABLET),

    # --- Spur Tower Interior: Floor 4 Command (3721-3724) ---------------
    (3721, "Half-Dómnathar Battle-Priest (Cleric 7)",  9385,
            LT_VOIDHAMMER + LT_POTION),
    (3722, "Dómnathar Void-Sorcerer (Sorcerer 12)",    9386,
            LT_VOIDHAMMER + LT_COLLAR + LT_TABLET + LT_POTION),
    (3723, "Dómnathar Void-Construct",                 9388, []),

    # --- Spur Tower Interior: Floor 5 Throne (3724-3726) ----------------
    (3724, "Dark Dwarf Lore-Keeper (Cleric 9)",        9391,
            LT_VOIDHAMMER + LT_TABLET + LT_COLLAR),
    (3725, "Dómnathar Void-Construct",                 9391, []),
    (3726, "Dómnathar House Leader (Sorcerer 15 / Fighter 2)", 9392,
            LT_VOIDHAMMER + LT_VOIDROD + LT_COLLAR + LT_TABLET
            + LT_DARKIRON_L + LT_MW_ARMOR),
]


# ===========================================================================
# Merge logic
# ===========================================================================

def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def merge_rooms():
    path = os.path.join(DATA, "areas", "DeepwaterMarches.json")
    rooms = _read(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0
    for r in ASHCROWN_ROOMS + SPUR_ROOMS:
        if r["vnum"] in existing:
            continue
        rooms.append(r)
        existing.add(r["vnum"])
        added += 1

    # Wire outbound exits
    wired = 0
    by_vnum = {r["vnum"]: r for r in rooms}
    for src_v, direction, dest_v in NEW_EXITS:
        r = by_vnum.get(src_v)
        if r is None:
            print(f"  WARN: missing source room {src_v}")
            continue
        exits = r.setdefault("exits", {})
        if exits.get(direction) == dest_v:
            continue
        if direction in exits and exits[direction] != dest_v:
            print(f"  WARN: {src_v} already has '{direction}' to "
                  f"{exits[direction]}; skipping")
            continue
        exits[direction] = dest_v
        wired += 1

    _write(path, rooms)
    print(f"  DeepwaterMarches.json: +{added} rooms, +{wired} exits "
          f"(total now {len(rooms)})")


def merge_items():
    path = os.path.join(DATA, "items.json")
    items = _read(path)
    existing = {it.get("vnum") for it in items}
    added = 0
    for it in NEW_ITEMS:
        if it["vnum"] in existing:
            continue
        items.append(it)
        added += 1
    _write(path, items)
    print(f"  items.json: +{added} new items (total now {len(items)})")


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
            spawn = _spawn(vnum, best_name, room_vnum,
                           bestiary=bestiary, loot=loot)
        except KeyError as e:
            print(f"  WARN: {e}")
            continue
        mobs.append(spawn)
        added += 1
    _write(mobs_path, mobs)
    print(f"  mobs.json: +{added} new spawns (total now {len(mobs)})")


def main() -> int:
    print("Building Deepwater Marches Deceiver zones:")
    merge_rooms()
    merge_items()
    merge_mobs()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
