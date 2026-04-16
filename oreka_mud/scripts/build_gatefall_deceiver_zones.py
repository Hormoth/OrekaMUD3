"""Build the Gatefall Reach Deceiver zones.

Appends two zones to ``data/areas/GatefallReach.json``:

  * Zone G1 -- The Scald-Tongue Warren (14 rooms, vnums 12250-12263)
    Kobold-heavy warren with a Dark Dwarf slave-driver as the nominal
    leader.  Level band 4-7.

  * Zone G2 -- The Fortress of Dorrach-Vel (28 rooms, vnums 12264-12291)
    Major Shattered Host garrison on 3 floors, commanded by a Dómnathar
    Infiltrator with a Half-Dómnathar Battle-Priest as second.  Level
    band 10-13.

Also:
  * Appends ~30 mob spawns to ``data/mobs.json`` using the new Deceiver
    bestiary creatures.
  * Adds 4 themed items (dark-iron dagger, kobold fire-cloak, void-
    touched warhammer, Dómnathar cipher-tablet) to ``data/items.json``.
  * Wires outbound exits from existing rooms 12249 (down) and 12244
    (east) into the new zones.

Idempotent by vnum.  Run:
    python scripts/build_gatefall_deceiver_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ===========================================================================
# Zone G1 -- The Scald-Tongue Warren  (vnums 12250-12263)
# ===========================================================================

SCALDTONGUE_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 12250,
        "name": "Scald-Tongue Warren -- Dead-Zone Entry",
        "description": (
            "A narrow stair cut into the rock descends from the Silence "
            "Breach's dead zone above into a close stone chamber lit by a "
            "greasy lantern. Kin-sense, absent above, is merely muffled "
            "here -- a difference kobold builders worked hard to achieve. "
            "Scratched into the jamb is a curling symbol in the shape of "
            "two crossed reptilian tongues -- the mark of the warren."
        ),
        "exits": {"up": 12249, "south": 12251},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12251,
        "name": "Scald-Tongue Warren -- Antechamber",
        "description": (
            "A low-ceilinged antechamber widens from the stair into the "
            "warren proper. Smoke-stained slate tablets hang on the walls "
            "and each bears a different kobold's name in spell-script, a "
            "hedge of warding-glyphs and small personal hexes. The air "
            "smells of kerosene, snake-musk, and simmering spellwork."
        ),
        "exits": {"north": 12250, "east": 12252, "south": 12253,
                  "west": 12254},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12252,
        "name": "Scald-Tongue Warren -- Trap Corridor",
        "description": (
            "The floor of this narrow corridor is a mosaic of pressure "
            "plates, razor-slots, and oil reservoirs. A small alcove to "
            "one side holds a bench of half-finished devices in brass and "
            "blued steel, each a different flavor of unpleasant surprise. "
            "The trapsmith does her best work here, and invites uninvited "
            "guests to appreciate the craft personally."
        ),
        "exits": {"west": 12251, "south": 12257},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "kobold_warren"],
    },
    {
        "vnum": 12253,
        "name": "Scald-Tongue Warren -- Common Hall",
        "description": (
            "A broader chamber where the warren's younger kobolds sleep "
            "in shared alcoves layered with stolen wool blankets and "
            "chewed leather scraps. A crude firepit burns at the center, "
            "ringed with flat stones for heating meals. Two scouts watch "
            "the corridor mouth with poorly-hidden spells readied."
        ),
        "exits": {"north": 12251, "east": 12258, "south": 12259},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12254,
        "name": "Scald-Tongue Warren -- Ritual Hall",
        "description": (
            "A circular room ringed with ash-stained prayer-mats around "
            "a low altar of black basalt. The altar's face bears a carving "
            "of a red dragon curled around an egg -- the warren's clan-"
            "mother myth made solid. The stone is warm to the touch and "
            "the smoke-smell is almost pleasant."
        ),
        "exits": {"east": 12251, "south": 12256},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12255,
        "name": "Scald-Tongue Warren -- Sorcerer's Study",
        "description": (
            "A working study lit by several oil-lamps of different shapes "
            "and ages, with a writing-desk piled high in parchment copied "
            "out in kobold claw-script. Dried reagents hang in bundles "
            "from pegs along one wall -- basilisk tongues, salamander "
            "skin, a pickled imp's heart. A silk bed-mat in the corner "
            "suggests the sorcerer sleeps here too, when he sleeps."
        ),
        "exits": {"north": 12256, "east": 12260, "south": 12261},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12256,
        "name": "Scald-Tongue Warren -- Nursery",
        "description": (
            "A round chamber kept deliberately warm by a banked peat-fire "
            "and lined with small nesting-pits filled with straw and worn "
            "velvet. A dozen mottled eggs rest in the pits, each about "
            "the size of a clenched fist, each marked with the sire's "
            "sigil in chalk. Nothing here is dangerous except by "
            "association."
        ),
        "exits": {"north": 12254, "south": 12255},
        "flags": ["indoor", "underground", "kobold_warren"],
    },
    {
        "vnum": 12257,
        "name": "Scald-Tongue Warren -- Wizard's Archive",
        "description": (
            "A long room lined with pigeon-holes cut into the stone, "
            "each filled with a tightly-rolled scroll sealed in red wax. "
            "The archivist's work-desk at the far end is scattered with "
            "glossaries, transliteration tables, and several Dómnathar-"
            "made reading-lenses on brass stands. The wizard herself is "
            "old, slow, and not at all weak."
        ),
        "exits": {"north": 12252, "west": 12260},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12258,
        "name": "Scald-Tongue Warren -- Kitchen & Slave Pen",
        "description": (
            "A smoky kitchen doubles as the warren's holding cell. A "
            "crude cage of iron bars welded by a smith of more enthusiasm "
            "than skill holds a single captive -- a Wind-Rider scout "
            "whose Pasua braid has been cut down to her skull. She "
            "watches without speaking. The cauldrons bubble."
        ),
        "exits": {"west": 12253, "south": 12259},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12259,
        "name": "Scald-Tongue Warren -- Supply Stores",
        "description": (
            "The warren's strongroom: barrels of salted meat, crates of "
            "scavenged weapons, and a neat stack of dark-iron helmets "
            "still bearing the Shattered Host's broken-chain stamp. Two "
            "Dark Dwarf warriors lean on their waraxes near the door, "
            "their beards oiled with something that smells of iron and "
            "burnt bone."
        ),
        "exits": {"north": 12253, "east": 12258, "west": 12262},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12260,
        "name": "Scald-Tongue Warren -- Champion's Hall",
        "description": (
            "A wider chamber shaped like a crude amphitheater, with tiers "
            "of stone benches cut into the walls. A circle of soot on the "
            "floor marks where the fire-sorcerer practices his art. "
            "Ashkarr the Bright-Clawed holds court here -- the warren's "
            "self-declared dragon-scion -- and is deeply offended by "
            "interruption."
        ),
        "exits": {"west": 12255, "east": 12257, "south": 12261},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12261,
        "name": "Scald-Tongue Warren -- Dragon-Priest's Sanctum",
        "description": (
            "A crypt-like chamber whose walls are hung with small effigies "
            "of a red dragon, carved from red sandstone and linen-wrapped "
            "for safekeeping. The sanctum's incense is sharp and "
            "metallic, like blood on a hot pan. A stone reliquary sits on "
            "a plinth at the center -- it is locked, and the lock is "
            "complicated."
        ),
        "exits": {"north": 12255, "east": 12260, "south": 12262},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12262,
        "name": "Scald-Tongue Warren -- Scavenger-Lord's Hall",
        "description": (
            "The warren's deepest and most comfortable chamber. A Dark "
            "Dwarf in fine lamellar sits on a chair of stolen Pekakarlik "
            "work, reading a ledger by the light of three separate oil-"
            "lamps. A kobold of unusual stature crouches on the back of "
            "the chair like a familiar, whispering into his ear in a "
            "dialect that is part Draconic and part something older. "
            "This is the master of the warren, and his whispering partner."
        ),
        "exits": {"east": 12259, "north": 12261, "south": 12263},
        "flags": ["indoor", "dangerous", "underground", "kobold_warren"],
    },
    {
        "vnum": 12263,
        "name": "Scald-Tongue Warren -- Strongroom",
        "description": (
            "A small locked room, its door reinforced in dark iron. "
            "Inside, the Scavenger-Lord keeps the warren's collected "
            "takings: a chest of mixed coinage, a rack of captured "
            "weapons, and a small locked box of Deceiver-make whose "
            "contents hum faintly when touched. The floor is trapped in "
            "at least two ways."
        ),
        "exits": {"north": 12262},
        "flags": ["indoor", "dangerous", "trapped", "underground",
                  "kobold_warren"],
    },
]


# ===========================================================================
# Zone G2 -- The Fortress of Dorrach-Vel  (vnums 12264-12291)
# ===========================================================================
# 3 floors: Outer Bastion (ground), Garrison (upper), Command (top)

FORTRESS_ROOMS: List[Dict[str, Any]] = [
    # ---- Ground Floor: Outer Bastion (12264-12273) ---------------------
    {
        "vnum": 12264,
        "name": "Dorrach-Vel -- The Hidden Gatehouse",
        "description": (
            "What looks from the Scar Road like an unremarkable rock "
            "outcropping is actually the fortress's outer gate, an iron-"
            "sheathed wooden door concealed behind a hinged stone facade. "
            "Murder-holes pierce the ceiling above the mat where visitors "
            "are expected to wait. A small plaque inside reads in "
            "hobgoblin script: 'State your business before breath is "
            "wasted on you.'"
        ),
        "exits": {"west": 12244, "east": 12265},
        "flags": ["indoor", "dangerous", "trapped", "fortress",
                  "hobgoblin_fort"],
    },
    {
        "vnum": 12265,
        "name": "Dorrach-Vel -- Outer Ward",
        "description": (
            "A small cobbled courtyard between the outer wall and the "
            "keep's first hall. Watch-braziers burn at each corner, and "
            "a whipping-post stands in the middle. The post has seen use "
            "recently; the cobbles around it are dark."
        ),
        "exits": {"west": 12264, "north": 12266, "east": 12268,
                  "south": 12269},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12266,
        "name": "Dorrach-Vel -- Guard Barracks",
        "description": (
            "Two long rows of wooden bunk-beds, neatly made. The walls "
            "are hung with a hobgoblin's personal gear on pegs -- helm, "
            "scabbard, belt, cup -- each set identical to the next. "
            "Discipline is visible in the way the boots are lined up at "
            "the foot of each bunk, every pair pointing the same way."
        ),
        "exits": {"south": 12265, "east": 12267},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12267,
        "name": "Dorrach-Vel -- War-Warg Kennels",
        "description": (
            "A dank, straw-floored chamber smelling of wet fur and "
            "musk. Iron-barred stalls along one wall hold massive "
            "wolves whose coats shimmer with the faint orange of "
            "banked embers -- War-Wargs bred from Flamewarg lines. "
            "They do not bark as intruders enter; they watch, and they "
            "remember."
        ),
        "exits": {"west": 12266, "south": 12268},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12268,
        "name": "Dorrach-Vel -- Armory",
        "description": (
            "Racks of identical longswords, greatswords, composite "
            "longbows, and quivers of black-fletched arrows line the "
            "walls. A smaller locked cage in the back holds the "
            "fortress's enchanted weapons -- a captain's privilege -- "
            "and a half-dozen dark-iron daggers rest in a velvet-lined "
            "tray labeled 'Requisition Only.'"
        ),
        "exits": {"west": 12265, "north": 12267, "south": 12270},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12269,
        "name": "Dorrach-Vel -- Drill Yard",
        "description": (
            "An open square of packed earth under a domed stone roof, "
            "lit by iron sconces. The floor is marked with lanes and "
            "circles for forms-practice. A Tunnel-Warden walks the perimeter "
            "slowly, correcting any hobgoblin who falters. Discipline is "
            "cold here, not cruel -- the cruelty is saved for intruders."
        ),
        "exits": {"north": 12265, "east": 12270, "south": 12272},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12270,
        "name": "Dorrach-Vel -- Mess Hall",
        "description": (
            "Long trestle tables run the length of this high-ceilinged "
            "hall. A bronze bell hangs over the doorway, and the cooks "
            "serve meals on a rigid schedule. The food is monotonous, "
            "calorie-dense, and surprisingly well-seasoned -- hobgoblin "
            "quartermasters take their work seriously."
        ),
        "exits": {"north": 12268, "west": 12269, "east": 12271},
        "flags": ["indoor", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12271,
        "name": "Dorrach-Vel -- Watchtower Base",
        "description": (
            "A cylindrical chamber whose center contains a spiral "
            "staircase of iron grating that climbs into shadow. The walls "
            "bear brass hooks where watch-cloaks hang, and a small desk "
            "holds the current watch-roster neatly inked in hobgoblin "
            "script. The tower goes up to the Garrison level."
        ),
        "exits": {"west": 12270, "up": 12274},
        "flags": ["indoor", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12272,
        "name": "Dorrach-Vel -- Sergeants' Quarters",
        "description": (
            "A smaller dormitory for the fortress's non-commissioned "
            "officers. Four private bunks instead of the common barracks' "
            "bunk-beds, a shared writing-desk, and a tray of worn iron "
            "sergeant's pins on a low shelf. Each pin bears a single "
            "notch for each year of service; the senior pin has nine."
        ),
        "exits": {"north": 12269, "east": 12273},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12273,
        "name": "Dorrach-Vel -- Inner Gate",
        "description": (
            "A heavy iron portcullis closes off the inner keep from the "
            "outer bastion. A gatehouse-alcove holds the winch mechanism "
            "and the pull-cord for the alarm-bell overhead. An iron-"
            "grated stair climbs past the portcullis into the upper "
            "floors of the keep."
        ),
        "exits": {"west": 12272, "up": 12274},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },

    # ---- Upper Floor: Garrison (12274-12283) ---------------------------
    {
        "vnum": 12274,
        "name": "Dorrach-Vel -- Upper Gate Hall",
        "description": (
            "A broad hallway at the top of the watchtower stair. Banners "
            "of the Shattered Host hang from the rafters -- seven "
            "overlapping iron-sigil chains on black field. Doors open to "
            "the east and west, and a narrow corridor leads north into "
            "the command section."
        ),
        "exits": {"down": 12271, "east": 12275, "west": 12277,
                  "north": 12276},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12275,
        "name": "Dorrach-Vel -- Officers' Quarters",
        "description": (
            "A row of private rooms for the fortress's ranking hobgoblins "
            "and its few Half-Dómnathar officers. The quarters are "
            "spartan but clean: a narrow bed, a writing-stand, a weapon-"
            "rack, and a single wall-hanging of some small heraldic "
            "emblem. The officers take their craft seriously."
        ),
        "exits": {"west": 12274, "north": 12278, "south": 12282},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12276,
        "name": "Dorrach-Vel -- Captain's Hall",
        "description": (
            "A paneled audience-chamber with a heavy oak desk at one end "
            "and a pair of chairs for petitioners at the other. The walls "
            "are hung with maps of the Gatefall foothills in various "
            "states of annotation. The Captain's articulated plate hangs "
            "on a mannequin behind his desk; the Captain himself sits at "
            "it, reading a report."
        ),
        "exits": {"south": 12274, "east": 12277},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12277,
        "name": "Dorrach-Vel -- Strategy Room",
        "description": (
            "A circular chamber with a great round table at its center, "
            "on which rests a detailed sand-model of the southeastern "
            "foothills with small carved markers for each of the "
            "Shattered Host's known garrisons. Several markers have been "
            "recently moved; a few have been overturned to indicate "
            "lost positions."
        ),
        "exits": {"east": 12274, "west": 12276, "north": 12279},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12278,
        "name": "Dorrach-Vel -- War-Temple of Silence",
        "description": (
            "A narrow chapel to a god that has no name, whose symbol is "
            "an empty iron circle hung on a chain. The walls are "
            "featureless black stone and the only light comes from three "
            "lamps set in the floor, directed upward. A battle-priest "
            "in blackened plate kneels at the rail, and his prayers "
            "echo strangely in the room."
        ),
        "exits": {"south": 12275, "east": 12281},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12279,
        "name": "Dorrach-Vel -- Void-Smith's Forge",
        "description": (
            "A low-ceilinged forge-chamber where the heat is cold "
            "rather than hot -- the anvil runs with a faint rime of "
            "frost even when the hammer strikes. A Dark Dwarf smith "
            "works at a iron-collar device, inking runes onto its inner "
            "face with a brass stylus. Suppressor-irons, the Kin call "
            "them. They hide Silentborn from detection."
        ),
        "exits": {"south": 12277, "east": 12280},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12280,
        "name": "Dorrach-Vel -- Punishment Cells",
        "description": (
            "A row of iron-barred cells, three of them, each narrow "
            "enough that a tall prisoner cannot fully lie down. One "
            "cell holds a hobgoblin private who spoke out of turn, "
            "waiting out his three-day sentence. The other two are "
            "empty but stained."
        ),
        "exits": {"west": 12279, "south": 12281},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12281,
        "name": "Dorrach-Vel -- Dark Dwarf Quarters",
        "description": (
            "A cluster of small rooms assigned to the fortress's Dark "
            "Dwarf specialists. The walls are hung with forge-craft "
            "tools, small heraldic banners of old clan-lines the "
            "Shattered Host has absorbed, and a single oil-lamp that "
            "never seems to go out. A Dark Dwarf warrior sits in the "
            "antechamber, cleaning his waraxe methodically."
        ),
        "exits": {"west": 12278, "north": 12280, "east": 12282},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12282,
        "name": "Dorrach-Vel -- Upper Ward",
        "description": (
            "A small enclosed courtyard open to the sky through a "
            "chimney-shaft. A single gnarled ash-tree grows in a stone "
            "planter at the center, the only living plant in the "
            "fortress. It is nourished, the hobgoblins joke, on blood."
        ),
        "exits": {"north": 12275, "west": 12281, "east": 12283},
        "flags": ["indoor", "fortress", "hobgoblin_fort"],
    },
    {
        "vnum": 12283,
        "name": "Dorrach-Vel -- Observatory",
        "description": (
            "A round stone chamber whose ceiling is a great cut-crystal "
            "lens pointing straight up through the fortress's bulk. A "
            "brass telescope on a gimbaled mount stands in the center. "
            "A narrow spiral stair climbs from a side-alcove into the "
            "command section above."
        ),
        "exits": {"west": 12282, "up": 12284},
        "flags": ["indoor", "dangerous", "fortress", "hobgoblin_fort"],
    },

    # ---- Top Floor: Command (12284-12291) ------------------------------
    {
        "vnum": 12284,
        "name": "Dorrach-Vel -- Command Staircase",
        "description": (
            "The top of the observatory's spiral stair opens into a "
            "short columned hall. The columns bear the seven-chain "
            "sigil inlaid in silver wire, and the floor is a single "
            "slab of polished black basalt. The air smells faintly of "
            "ozone -- the Command Staircase is kept warded."
        ),
        "exits": {"down": 12283, "east": 12285, "west": 12286,
                  "north": 12287},
        "flags": ["indoor", "dangerous", "fortress", "command"],
    },
    {
        "vnum": 12285,
        "name": "Dorrach-Vel -- Library & Archive",
        "description": (
            "A long gallery lined floor-to-ceiling with narrow-spined "
            "books in three alphabets. A librarian's lectern at the far "
            "end bears an open catalog. The collection is astonishingly "
            "complete, including copies of Kin texts the Kin themselves "
            "believe lost. The catalog is indexed by the names of the "
            "families the texts were stolen from."
        ),
        "exits": {"west": 12284, "south": 12286},
        "flags": ["indoor", "dangerous", "fortress", "command"],
    },
    {
        "vnum": 12286,
        "name": "Dorrach-Vel -- Infiltrator's Study",
        "description": (
            "A small private study. A writing-desk with perfect "
            "posture; a shelf of reference volumes in Silent Host "
            "script; a single sheathed sword on a stand by the window, "
            "its hilt of unfamiliar black metal. The Infiltrator's "
            "personal assassin waits in the shadow behind the door -- "
            "she is quiet enough that even a trained scout would miss "
            "her."
        ),
        "exits": {"east": 12284, "north": 12285, "south": 12287},
        "flags": ["indoor", "dangerous", "fortress", "command"],
    },
    {
        "vnum": 12287,
        "name": "Dorrach-Vel -- Audience Chamber",
        "description": (
            "A long room with a raised dais at the far end, above which "
            "hangs a simple black banner bearing no device. The floor is "
            "marked with concentric rings of inlaid silver, each smaller "
            "than the last, focused on the dais. Anyone kneeling at the "
            "innermost ring may speak; anyone beyond the outer ring is "
            "expected to have come armed, and to fight."
        ),
        "exits": {"south": 12284, "north": 12288},
        "flags": ["indoor", "dangerous", "fortress", "command"],
    },
    {
        "vnum": 12288,
        "name": "Dorrach-Vel -- The Infiltrator's Throne",
        "description": (
            "The fortress's command sanctum. A low stone throne sits on "
            "the dais, its back carved with the profile of a dragon "
            "tearing out the sun -- the old sigil of the Dómnathar "
            "infiltrator-school. On the throne, a tall and slender "
            "figure who has killed Kin officers for three hundred years "
            "looks up without surprise at the intruders. She has been "
            "expecting visitors."
        ),
        "exits": {"south": 12287, "east": 12289, "west": 12290},
        "flags": ["indoor", "dangerous", "fortress", "command"],
    },
    {
        "vnum": 12289,
        "name": "Dorrach-Vel -- Hidden Passage",
        "description": (
            "A narrow stone-cut passage concealed behind a section of "
            "wall in the Throne. Single-file; lit by a string of small "
            "oil-reservoirs that ignite themselves when a body passes. "
            "The passage descends steeply and vanishes into darkness -- "
            "the Infiltrator's private escape route, leading somewhere "
            "far beneath the Silence Breach approaches."
        ),
        "exits": {"west": 12288, "down": 12291},
        "flags": ["indoor", "dangerous", "fortress", "command"],
    },
    {
        "vnum": 12290,
        "name": "Dorrach-Vel -- Silence Chamber",
        "description": (
            "A small sealed room whose walls are inlaid with runes "
            "unlike any Kin script. The air within is utterly silent, "
            "as if sound has been amputated. A Dómnathar Void-Construct "
            "stands at parade-rest in the center of the room, its "
            "obsidian body reflecting no light. It does not move. When "
            "it moves, it will not make a sound."
        ),
        "exits": {"east": 12288},
        "flags": ["indoor", "dangerous", "fortress", "command",
                  "silence_zone"],
    },
    {
        "vnum": 12291,
        "name": "Dorrach-Vel -- Escape Tunnel",
        "description": (
            "A long descending passage that emerges, eventually, into "
            "the deep Silence Breach approach tunnels -- the "
            "Infiltrator's last insurance against defeat. The passage "
            "is kept in good repair and shows signs of recent use. "
            "Somewhere far below, through at least a mile of bored "
            "stone, it connects to the Shattered Host's greater "
            "tunnel network."
        ),
        "exits": {"up": 12289},
        "flags": ["indoor", "dangerous", "underground"],
    },
]


# ===========================================================================
# Outbound exits from existing rooms into the new zones
# ===========================================================================

NEW_EXITS = [
    # Silence Breach Inner Perimeter -> Scald-Tongue Warren entry
    (12249, "down", 12250),
    # Scar Road Ambush Hollow -> Fortress of Dorrach-Vel hidden gate
    (12244, "east", 12264),
]


# ===========================================================================
# New themed items (vnums 705-708)
# ===========================================================================

NEW_ITEMS: List[Dict[str, Any]] = [
    {
        "vnum": 705,
        "name": "Dark-Iron Dagger",
        "item_type": "weapon",
        "weight": 1,
        "value": 310,
        "description": (
            "A dwarven-forged dagger of iron smelted in a Deceiver-era "
            "foundry. The metal is blacker than ordinary iron and takes "
            "and keeps an edge superbly. Masterwork: +1 to attack."
        ),
        "damage": [1, 4, 0],
        "properties": ["simple", "masterwork"],
    },
    {
        "vnum": 706,
        "name": "Kobold Fire-Cloak",
        "item_type": "cloak",
        "weight": 1,
        "value": 200,
        "description": (
            "A shoulder-cloak of overlapping reddish kobold scales "
            "stitched on canvas backing. The scales are dense enough to "
            "shrug aside small fires; grants +1 circumstance bonus on "
            "saves against fire effects."
        ),
        "slot": "shoulders",
        "properties": ["cloak", "minor_magic"],
    },
    {
        "vnum": 707,
        "name": "Void-Touched Warhammer",
        "item_type": "weapon",
        "weight": 8,
        "value": 2310,
        "description": (
            "A +1 warhammer whose head is banded with bars of dark iron. "
            "In dim light, the iron seems to swallow illumination rather "
            "than reflect it. On a critical hit, target saves vs Will DC "
            "15 or is silenced for 1 round."
        ),
        "damage": [1, 8, 1],
        "properties": ["martial", "magical", "+1"],
    },
    {
        "vnum": 708,
        "name": "Dómnathar Cipher-Tablet",
        "item_type": "gear",
        "weight": 2,
        "value": 100,
        "description": (
            "A slate tablet engraved with Dómnathar rank-cipher, small "
            "enough to fit in a belt-pouch. Of no combat value; but "
            "Kin intelligence-officers will pay handsomely for a clean "
            "copy, and the Wind-Riders will extend faction credit to "
            "whoever brings one in."
        ),
        "properties": ["quest", "faction"],
    },
]


# ===========================================================================
# Mob spawns (vnums 3600-3634)  -- references to bestiary templates
# ===========================================================================

# We'll build full stat-block mobs (as mobs.json uses full inline stats,
# not bestiary vnum references).  Helper copies the base from the bestiary.

def _bestiary_lookup(name: str, bestiary: list) -> dict:
    hits = [b for b in bestiary if b.get("name") == name]
    if not hits:
        raise KeyError(f"bestiary missing: {name}")
    return hits[0]


def _spawn_from_bestiary(mob_vnum: int, bestiary_name: str, room_vnum: int,
                         *, bestiary, name_override=None, loot=None):
    """Clone a bestiary entry and pin it to a room."""
    src = _bestiary_lookup(bestiary_name, bestiary)
    new = {k: v for k, v in src.items() if k != "vnum"}
    new["vnum"] = mob_vnum
    new["room_vnum"] = room_vnum
    if name_override:
        new["name"] = name_override
    if loot is not None:
        new["loot_table"] = loot
    return new


# Loot tables (vnum -> drop chance)
LT_COINS      = [{"vnum": 2,   "chance": 0.25}]
LT_TORCH      = [{"vnum": 203, "chance": 0.4}]
LT_DAGGER     = [{"vnum": 2,   "chance": 0.25}]
LT_POTION     = [{"vnum": 301, "chance": 0.15}]
LT_MW_SWORD   = [{"vnum": 700, "chance": 0.35}]
LT_MW_ARMOR   = [{"vnum": 701, "chance": 0.30}]
LT_SIGNET     = [{"vnum": 702, "chance": 0.25}]
LT_WARDAMUL   = [{"vnum": 703, "chance": 0.35}]
LT_DARKIRON   = [{"vnum": 705, "chance": 0.40}]
LT_FIRECLOAK  = [{"vnum": 706, "chance": 0.50}]
LT_VOIDHAMMER = [{"vnum": 707, "chance": 0.80}]
LT_TABLET     = [{"vnum": 708, "chance": 0.75}]


# Specification: which bestiary creature goes in which room, with loot
SPAWN_SPEC = [
    # Scald-Tongue Warren
    (3600, "Kobold Scout (Sorcerer 1)",     12251, LT_DAGGER + LT_TORCH),
    (3601, "Kobold Scout (Sorcerer 1)",     12251, LT_COINS),
    (3602, "Kobold Trapsmith (Rogue 3)",    12252, LT_DAGGER + LT_POTION + LT_FIRECLOAK),
    (3603, "Kobold Scout (Sorcerer 1)",     12253, LT_TORCH),
    (3604, "Kobold Scout (Sorcerer 1)",     12253, LT_COINS),
    (3605, "Kobold Cultist (Cleric 2)",     12254, LT_POTION + LT_FIRECLOAK),
    (3606, "Kobold Sorcerer (Sorcerer 3)",  12255, LT_DAGGER + LT_POTION),
    (3607, "Kobold Scout (Sorcerer 1)",     12255, LT_COINS),
    (3608, "Kobold Wizard (Wizard 4)",      12257, LT_DAGGER + LT_POTION + LT_FIRECLOAK),
    (3609, "Kobold Scout (Sorcerer 1)",     12258, LT_COINS),
    (3610, "Dark Dwarf Warrior (Fighter 3)",12259, LT_MW_ARMOR + LT_DARKIRON),
    (3611, "Dark Dwarf Warrior (Fighter 3)",12259, LT_DARKIRON + LT_COINS),
    (3612, "Kobold Fire-Sorcerer (Sorcerer 5)", 12260,
            LT_MW_SWORD + LT_FIRECLOAK + LT_POTION),
    (3613, "Kobold Dragon-Priest (Cleric 5)", 12261,
            LT_MW_ARMOR + LT_POTION + LT_SIGNET),
    (3614, "Dark Dwarf Scavenger-Lord (Rogue 4)", 12262,
            LT_MW_SWORD + LT_MW_ARMOR + LT_DARKIRON + LT_SIGNET + LT_TABLET),
    (3615, "Kobold Sorcerer-Chief (Sorcerer 7)", 12262,
            LT_MW_SWORD + LT_POTION + LT_FIRECLOAK + LT_SIGNET),

    # Fortress of Dorrach-Vel -- Outer Bastion
    (3616, "Hobgoblin Sergeant (Fighter 2)", 12265, LT_MW_ARMOR + LT_COINS),
    (3617, "Hobgoblin Sergeant (Fighter 2)", 12266, LT_MW_ARMOR),
    (3618, "Hobgoblin Tunnel-Warden (Fighter 3 / Ranger 1)", 12269,
            LT_MW_SWORD + LT_MW_ARMOR + LT_POTION),

    # Upper Garrison
    (3619, "Hobgoblin Captain (Fighter 5)",  12276,
            LT_MW_SWORD + LT_MW_ARMOR + LT_DARKIRON + LT_TABLET),
    (3620, "Half-Dómnathar Battle-Priest (Cleric 7)", 12278,
            LT_VOIDHAMMER + LT_POTION + LT_WARDAMUL),
    (3621, "Dark Dwarf Void-Smith (Expert 7 / Wizard 1)", 12279,
            LT_DARKIRON + LT_MW_ARMOR + LT_TABLET),
    (3622, "Dark Dwarf Warrior (Fighter 3)", 12281,
            LT_DARKIRON + LT_MW_ARMOR),

    # Command
    (3623, "Silentborn Assassin (Rogue 5 / Assassin 2)", 12286,
            LT_MW_SWORD + LT_POTION + LT_TABLET),
    (3624, "Dómnathar Infiltrator (Rogue 6 / Fighter 2)", 12288,
            LT_MW_SWORD + LT_MW_ARMOR + LT_VOIDHAMMER + LT_TABLET + LT_WARDAMUL),
    (3625, "Dómnathar Void-Construct",       12290, []),
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
    path = os.path.join(DATA, "areas", "GatefallReach.json")
    rooms = _read(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0
    for r in SCALDTONGUE_ROOMS + FORTRESS_ROOMS:
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
    print(f"  GatefallReach.json: +{added} rooms, +{wired} exits "
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
    bestiary_path = os.path.join(DATA, "mobs_bestiary.json")
    mobs = _read(mobs_path)
    bestiary = _read(bestiary_path)
    existing = {m.get("vnum") for m in mobs}
    added = 0
    for mob_vnum, best_name, room_vnum, loot in SPAWN_SPEC:
        if mob_vnum in existing:
            continue
        try:
            spawn = _spawn_from_bestiary(mob_vnum, best_name, room_vnum,
                                         bestiary=bestiary, loot=loot)
        except KeyError as e:
            print(f"  WARN: {e}")
            continue
        mobs.append(spawn)
        added += 1
    _write(mobs_path, mobs)
    print(f"  mobs.json: +{added} new spawns (total now {len(mobs)})")


def main() -> int:
    print("Building Gatefall Reach Deceiver zones:")
    merge_rooms()
    merge_items()
    merge_mobs()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
