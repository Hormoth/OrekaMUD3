"""Build the Custos Undercity and Muddywake starter zones.

Appends 30 undercity rooms + 16 river-adventure rooms to
``data/areas/CustosDoAeternos.json``, adds 23 new mob spawns to
``data/mobs.json``, wires outbound exits on 7 existing Custos rooms,
and registers 5 new starter-tier items in ``data/items.json``.

Idempotent: running twice detects existing entries by vnum and no-ops.

Run:
    python scripts/build_custos_starter_zones.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ---------------------------------------------------------------------------
# Zone A: The Custos Undercity (vnums 4200-4229)
# ---------------------------------------------------------------------------

UNDERCITY_ROOMS: List[Dict[str, Any]] = [
    # --- Upper Sewers (4200-4207) -----------------------------------------
    {
        "vnum": 4200,
        "name": "Under the Deepwell Tavern",
        "description": (
            "The old service well beneath the Deepwell Tavern opens into a low "
            "stone chamber that smells of spilled beer turned sour and wet rot. "
            "An iron ladder climbs back up to the tavern floor overhead, its "
            "lowest rungs orange with rust. Fragments of broken crockery litter "
            "the packed-earth floor, and a curved tunnel leads east along the "
            "old drain line."
        ),
        "exits": {"up": 4012, "east": 4201},
        "flags": ["indoor", "dangerous", "underground", "sewer"],
    },
    {
        "vnum": 4201,
        "name": "Sewer Main -- Market Branch",
        "description": (
            "This broad brick-lined passage carries the runoff from the market "
            "district above. A trickle of grey water runs along a central "
            "channel, and the air is thick with the smell of rotting vegetables "
            "and old blood from the butchers' stalls. Side drains open east "
            "and south; a collapsed section blocks the way further west."
        ),
        "exits": {"west": 4200, "east": 4202, "south": 4203},
        "flags": ["indoor", "dangerous", "underground", "sewer"],
    },
    {
        "vnum": 4202,
        "name": "Sewer Grate -- Sludge Pool",
        "description": (
            "The brick vault opens over a pool of slow-moving sludge fed by "
            "three lesser drains. Pale streamers of mold hang from the ceiling "
            "and trail into the water. An iron grate above admits a single "
            "pencil of daylight -- it illuminates very little. The pool can be "
            "waded across, but the footing is treacherous."
        ),
        "exits": {"west": 4201, "east": 4204, "down": 4203},
        "flags": ["indoor", "dangerous", "underground", "sewer", "water"],
    },
    {
        "vnum": 4203,
        "name": "The Rat's Den",
        "description": (
            "What was once a collapsed cellar has become a warren. Piles of "
            "shredded burlap, gnawed bone, and stolen trinkets ring the walls, "
            "and the floor is a carpet of matted fur and droppings. The "
            "occupants scatter and regroup as intruders enter, their red eyes "
            "glinting in the torchlight."
        ),
        "exits": {"north": 4201, "up": 4202, "east": 4207},
        "flags": ["indoor", "dangerous", "underground", "sewer"],
    },
    {
        "vnum": 4204,
        "name": "Collapsed Drain",
        "description": (
            "A cave-in years ago brought the far wall down into the sewer, and "
            "the resulting slope of broken brick and mud has never been cleared. "
            "A chill draft rises through the gap, smelling of wet stone and "
            "something older -- the mineral scent of deeper tunnels. A rough "
            "scramble down the rubble leads into the old cisterns."
        ),
        "exits": {"west": 4202, "down": 4208, "east": 4205},
        "flags": ["indoor", "dangerous", "underground", "sewer"],
    },
    {
        "vnum": 4205,
        "name": "Canal Grate Chamber",
        "description": (
            "A heavy iron grate above pours a steady silver curtain of canal "
            "water into this small stone chamber, which drains through a vent "
            "on the far wall. The noise is a constant hiss. A rusted ladder "
            "climbs up through the grate to the Pekakarlik Canal Walk overhead; "
            "a passage leads north into older, drier brickwork."
        ),
        "exits": {"up": 4152, "west": 4204, "north": 4206},
        "flags": ["indoor", "dangerous", "underground", "sewer", "water"],
    },
    {
        "vnum": 4206,
        "name": "The Stirge Nest",
        "description": (
            "The brick ceiling here is crazed with cracks, and mossy growths "
            "hang from them in long curtains. Small leathery shapes cling to "
            "the vault overhead, their proboscises twitching at the scent of "
            "warm blood. The smell of ammonia is overpowering."
        ),
        "exits": {"south": 4205, "east": 4207},
        "flags": ["indoor", "dangerous", "underground", "sewer"],
    },
    {
        "vnum": 4207,
        "name": "The Alpha's Midden",
        "description": (
            "The sewer widens into a crude throne-chamber for something very "
            "large and very aggressive. Piled against the walls are the remains "
            "of dozens of meals: chewed leather boots, split bones, a broken "
            "shortsword still clutched in a gnawed hand. The master of this "
            "place is clearly in residence, and clearly not pleased."
        ),
        "exits": {"west": 4206, "south": 4203},
        "flags": ["indoor", "dangerous", "underground", "sewer"],
    },

    # --- Old Cisterns (4208-4214) -----------------------------------------
    {
        "vnum": 4208,
        "name": "Cistern Overflow",
        "description": (
            "The sewer brickwork abruptly gives way to much older stonework -- "
            "great rough-hewn blocks laid without mortar, slick with centuries "
            "of wet. This is one of the old Custos cisterns, built before the "
            "city reached its current size. Water laps softly somewhere ahead."
        ),
        "exits": {"up": 4204, "south": 4209, "east": 4211},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4209,
        "name": "Flooded Cistern",
        "description": (
            "Black water fills most of this circular chamber to knee depth, "
            "still as glass. Bloated shapes stir beneath the surface as you "
            "step in -- the dead of older centuries, preserved cold and wet "
            "and hungry. Something in this water remembers that it was once a "
            "person, and is furious about what it has become."
        ),
        "exits": {"north": 4208, "east": 4212},
        "flags": ["indoor", "dangerous", "underground", "water"],
    },
    {
        "vnum": 4210,
        "name": "Under the Safe House",
        "description": (
            "A rotten trapdoor overhead opens into a stone-lined cell no larger "
            "than a closet. A stub of candle on an iron shelf has been lit "
            "recently; beside it is a note in a crabbed hand that reads 'Lie "
            "still until dawn.' The cell opens west into older, colder stone."
        ),
        "exits": {"up": 4142, "west": 4211},
        "flags": ["indoor", "underground"],
    },
    {
        "vnum": 4211,
        "name": "The Broken Arch",
        "description": (
            "A grand arch once stood here, connecting the cisterns to "
            "something older still. Today it is reduced to a jagged semicircle "
            "of broken stone around a dark opening. A skeletal figure sits "
            "propped beside the arch in the pose of a bored sentry, and it has "
            "been sitting there a very long time. As you approach, it stands."
        ),
        "exits": {"west": 4208, "east": 4210, "down": 4212},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4212,
        "name": "Fetid Pool",
        "description": (
            "A dead cistern. The water here has been still so long that it has "
            "grown a skin of reddish-brown mold, and the smell rising from it "
            "is a clinging, sickly sweetness that coats the tongue. The mold "
            "is cold -- unnaturally so -- and draws warmth from everything "
            "that comes near."
        ),
        "exits": {"up": 4211, "west": 4209, "south": 4213},
        "flags": ["indoor", "dangerous", "underground", "water"],
    },
    {
        "vnum": 4213,
        "name": "The Necromancer's Scratch",
        "description": (
            "Someone once practiced dark arts in this low-ceilinged cell, and "
            "the walls still show their work: scratched sigils in long repeating "
            "spirals, some rubbed smooth by centuries of passing bodies. The "
            "stone floor is dark with old blood. The present tenant eats what "
            "wanders in, and has been doing so for a long time."
        ),
        "exits": {"north": 4212, "south": 4214},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4214,
        "name": "Drowned Stair",
        "description": (
            "A stone staircase descends into standing water; its lower steps "
            "vanish into blackness. The water is colder than any in the cisterns "
            "above, and the echoes that come back sound like they travel a "
            "long way. A dry upper landing connects east to Pekakarlik work -- "
            "tighter cut stone, different craft entirely."
        ),
        "exits": {"north": 4213, "east": 4215},
        "flags": ["indoor", "dangerous", "underground", "water"],
    },

    # --- Pekakarlik Maintenance Tunnels (4215-4222) -----------------------
    {
        "vnum": 4215,
        "name": "The Vault Breach",
        "description": (
            "A section of the Donation Vault's north wall has collapsed inward, "
            "revealing a tunnel dressed in the distinctive close-cut stonework "
            "of Pekakarlik work -- blocks fitted so tightly that no mortar was "
            "needed. The passage predates the vault above by centuries. Faint "
            "hammering sounds in the distance, from something that does not "
            "sleep."
        ),
        "exits": {"west": 4161, "east": 4216, "up": 4214},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4216,
        "name": "Tunnel Junction",
        "description": (
            "The Pekakarlik tunnel forks here into three branches, each marked "
            "by a carved rune in the corner of the jamb. Scratched over the "
            "runes in more recent charcoal are the crude tally-marks of "
            "kobold scouts, and a faint reek of lamp oil and unwashed fur "
            "drifts from the east branch."
        ),
        "exits": {"west": 4215, "north": 4218, "east": 4217, "south": 4219},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4217,
        "name": "Kobold Warren -- East",
        "description": (
            "The Pekakarlik passage has been crudely expanded sideways to "
            "accommodate a squatter colony. Cook-fire ash blackens the ceiling, "
            "bundles of filthy blankets line the walls, and small yellow-eyed "
            "figures chitter and scramble for weapons at the sight of intruders. "
            "The floor is slick with spilled grease."
        ),
        "exits": {"west": 4216, "north": 4218},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4218,
        "name": "Kobold Warren -- West",
        "description": (
            "A smaller chamber filled with the Warren's stores of stolen goods: "
            "tavern knives, dropped coin-purses cut open and drained, a "
            "half-finished wooden fetish of Tiamat carved with more enthusiasm "
            "than skill. The lone occupant crouches between the piles, "
            "guarding his hoard with furious little squeals."
        ),
        "exits": {"south": 4216, "south_duplicate": None, "east": 4217},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4219,
        "name": "The Quarry Shaft",
        "description": (
            "The Pekakarlik tunnel widens here into a true quarry-shaft, its "
            "walls shaped into patient terraces that climb beyond the reach of "
            "any torch. A low crust of dust covers everything. At the base of "
            "the shaft, a lump of patient earth resolves itself -- as you "
            "watch -- into a shape with arms and attention."
        ),
        "exits": {"north": 4216, "east": 4221, "south": 4220},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4220,
        "name": "The Postern Shaft",
        "description": (
            "A knotted rope of the finest dwarven silk drops from a shaft in "
            "the ceiling -- the thieves' route down from Dodger's Gate. "
            "Shallow-cut handholds flank the rope for those who distrust "
            "knotted silk. The shaft rises into a lightless square far above; "
            "a low passage leads west into the maintenance tunnels proper."
        ),
        "exits": {"up": 4144, "north": 4219, "west": 4222},
        "flags": ["indoor", "underground"],
    },
    {
        "vnum": 4221,
        "name": "Hall of the Quarry-Golem",
        "description": (
            "A dressed-stone hall with columns shaped like kneeling figures. "
            "One column has moved since the hall was built: the sixth from the "
            "door stands closer to the center than the others, and its shaped "
            "arms hang at slightly different angles. The dust on its shoulders "
            "looks freshly disturbed."
        ),
        "exits": {"west": 4219, "east": 4223},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4222,
        "name": "Forge-Ward Passage",
        "description": (
            "A narrow maintenance passage with a low vaulted ceiling, its walls "
            "scorched black by the Pekakarlik foundries it once served. The "
            "heat is long gone; what remains is cold soot and the smell of old "
            "iron. Thick grey webs span the corners -- something patient lives "
            "here, and is not pleased to share."
        ),
        "exits": {"east": 4220, "north": 4221, "south": 4223},
        "flags": ["indoor", "dangerous", "underground"],
    },

    # --- The Old Vault (4223-4229) ----------------------------------------
    {
        "vnum": 4223,
        "name": "The Outer Vault Hall",
        "description": (
            "A grand hall of careful Pekakarlik stonework, lit only by a "
            "faint phosphoric glow from runes set into the capstones. The "
            "columns here are shaped like axe-heads pointing downward -- the "
            "old clan-seal of the tunnel-stewards. At the far end, a stone "
            "doorway has been sealed and then forced open again. Webs thick "
            "as cord sway in the still air."
        ),
        "exits": {"west": 4222, "north": 4221, "east": 4224, "south": 4225},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4224,
        "name": "Pekakarlik Archive Chamber",
        "description": (
            "A long gallery lined with slate tablets set into the walls, each "
            "incised in the block-script the Pekakarlik used for maintenance "
            "records. The tablets detail pump-schedules, cistern depths, and "
            "the genealogies of the minor stewards who kept the undercity "
            "running. None of it is secret, but all of it is centuries old."
        ),
        "exits": {"west": 4223, "south": 4227},
        "flags": ["indoor", "underground"],
    },
    {
        "vnum": 4225,
        "name": "The Gel-Cube Chamber",
        "description": (
            "A square room whose floor is worn glassy-smooth in a perfect "
            "track along the walls -- something large and slow has been "
            "patrolling this chamber for a very long time. Bones lie in three "
            "tidy heaps in the corners, their marrow scooped clean. The air "
            "tastes faintly of acid."
        ),
        "exits": {"north": 4223, "east": 4226},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4226,
        "name": "The Tinker's Workshop",
        "description": (
            "A small study that has not been swept since its owner died. A "
            "workbench holds tools laid out neat, each in its outline of "
            "accumulated dust. The craftsman's successor still fusses about "
            "the shop -- a small leathery creature with bat-like wings, which "
            "eyes you with something between resentment and recognition."
        ),
        "exits": {"west": 4225, "east": 4227},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4227,
        "name": "The Treasure Cache",
        "description": (
            "A small strongroom, its door long since forced. Most of what was "
            "here has been taken over the centuries, but the thieves in their "
            "haste left items that were too heavy, too ugly, or too carefully "
            "locked. A Pekakarlik strongbox sits in the corner, its hinges "
            "stubborn with rust but still workable. The air smells of iron "
            "and old leather."
        ),
        "exits": {"north": 4224, "west": 4226, "east": 4228},
        "flags": ["indoor", "underground"],
    },
    {
        "vnum": 4228,
        "name": "The Tunnel-Warden's Hall",
        "description": (
            "A broad stone hall built for ceremony, with a dais at the far end "
            "and a stone chair carved in the shape of an overturned anvil. "
            "Seated on the chair is the Warden: a Pekakarlik kept alive far "
            "past his time by the slow magic of the runes around him. His "
            "eyes open as you enter, and they are the eyes of something that "
            "has forgotten it ever was kind."
        ),
        "exits": {"west": 4227, "south": 4229},
        "flags": ["indoor", "dangerous", "underground"],
    },
    {
        "vnum": 4229,
        "name": "Deep Pipe Terminus",
        "description": (
            "A dead-end chamber where three great stone pipes debouche into a "
            "pool of dark, motionless water. The water is deeper than it "
            "appears; divers have vanished here, and not come back. Something "
            "about the sound of dripping in this place feels more like a "
            "conversation than an accident."
        ),
        "exits": {"north": 4228},
        "flags": ["indoor", "dangerous", "underground", "water"],
    },
]


# ---------------------------------------------------------------------------
# Zone B: The Muddywake (vnums 4300-4315)
# ---------------------------------------------------------------------------

MUDDYWAKE_ROOMS: List[Dict[str, Any]] = [
    {
        "vnum": 4300,
        "name": "Shrine Skiff Landing",
        "description": (
            "The priests of Semyon keep a flat-bottomed skiff tied at the "
            "eastern quay of the Dockside Shrine. A gravel path leads up from "
            "the water to the shrine's side door. The current here curls "
            "strangely against the bank, as if something upstream is bending "
            "the river's will. The priestess says she will pay for answers."
        ),
        "exits": {"north": 4021, "east": 4301},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4301,
        "name": "Reed Shallows -- Eastern Flats",
        "description": (
            "The Great River slows here into a maze of reed-choked channels "
            "where the dredgers never reach. The water is tea-colored with "
            "tannin and barely knee-deep, but the mud beneath it is soft and "
            "treacherous. Small dark shapes glide through the reeds, and "
            "bubbles rise where larger things wait."
        ),
        "exits": {"west": 4300, "east": 4302, "north": 4303},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4302,
        "name": "Muddywake Bend",
        "description": (
            "The river swings into a slow bend here, leaving a wide crescent "
            "of wet mudflat before it. A fallen willow half-bridges the water, "
            "its trailing branches thick with skulking green things. The stench "
            "is that of a healthy swamp -- rich, alive, and actively rotting "
            "in three different directions at once."
        ),
        "exits": {"west": 4301, "east": 4308},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4303,
        "name": "Reed-Hidden Sandbar",
        "description": (
            "Tall reeds screen a narrow sandbar from the shore, creating a "
            "natural blind. The sand is tracked with webbed footprints, all "
            "coming in, none going out. A pile of fish-bones, picked very "
            "clean, sits at the water's edge -- and a few of the bones are "
            "not fish."
        ),
        "exits": {"south": 4301, "north": 4304},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4304,
        "name": "Half-Sunken Shrine Approach",
        "description": (
            "The reeds thin as the ground rises, revealing the tops of three "
            "weathered stone pillars that once flanked a shrine-path. The "
            "shrine itself lies north, mostly submerged now where the river "
            "has broken through its old foundations. A carving of Semyon's "
            "river-crown still faces downstream in silent benediction."
        ),
        "exits": {"south": 4303, "north": 4305},
        "flags": ["outdoor", "water"],
    },
    {
        "vnum": 4305,
        "name": "Sunken Shrine -- Steps",
        "description": (
            "Mossy stone steps descend into clear shallow water where once "
            "they climbed to the shrine porch. The river has claimed the lower "
            "third of the building. A slim figure sits on the submerged middle "
            "step, combing out her long green hair, and her smile at your "
            "approach is not entirely reassuring."
        ),
        "exits": {"south": 4304, "north": 4306},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4306,
        "name": "Sunken Shrine -- Inner Porch",
        "description": (
            "The interior of the old shrine is dim and half-flooded, lit only "
            "by light filtering through broken roof-tiles. River-worn floor-"
            "mosaics show Semyon in her aspect as Lady of the Shallows. Where "
            "the tiles are missing, the water is deep and very cold -- it "
            "gets colder further in."
        ),
        "exits": {"south": 4305, "north": 4307},
        "flags": ["indoor", "water", "dangerous"],
    },
    {
        "vnum": 4307,
        "name": "Sunken Shrine -- Altar Chamber",
        "description": (
            "The shrine's altar is still standing, though the idol that once "
            "rested on it has fallen and cracked. The water is chest-deep here "
            "and moves gently in patterns that have nothing to do with the "
            "river current outside. A small pale creature circles the altar "
            "like a swimmer doing patient laps."
        ),
        "exits": {"south": 4306},
        "flags": ["indoor", "water", "dangerous"],
    },
    {
        "vnum": 4308,
        "name": "The Old Weir Approach",
        "description": (
            "The river widens into a shallow plate where the old weir once "
            "regulated flow. The weir itself is broken in two places, but its "
            "surviving stones form a natural crossing to an islet of higher "
            "ground. The water boils suspiciously around one of the gaps -- "
            "something is lodged there."
        ),
        "exits": {"west": 4302, "east": 4309, "south": 4310},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4309,
        "name": "Stone Weir Passage",
        "description": (
            "A narrow walk along the surviving weir stones, wet and slippery. "
            "To either side the river drops into pools deep enough to hide a "
            "wagon. Something large has been digging -- or living -- beneath "
            "the stones on the north side; there are drag-marks in the silt "
            "where the current is weakest."
        ),
        "exits": {"west": 4308, "east": 4311},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4310,
        "name": "Weir Channel",
        "description": (
            "A secondary channel below the broken weir carries most of the "
            "current when the river is high. A merfolk warrior waits here with "
            "a bone-tipped spear, watching the crossing with the hostile "
            "patience of a toll-keeper who has decided the toll will be blood. "
            "The water swirls dark behind him."
        ),
        "exits": {"north": 4308, "east": 4311},
        "flags": ["outdoor", "water", "dangerous"],
    },
    {
        "vnum": 4311,
        "name": "Flooded Grotto Mouth",
        "description": (
            "The river forms a quiet pool at the foot of a limestone bluff "
            "whose face has been opened by erosion into a dark cavern mouth. "
            "The air coming out is cold and smells of minerals and deep water. "
            "A soft, almost musical sound echoes from within -- the voice of "
            "something old and patient speaking in the language of currents."
        ),
        "exits": {"west": 4309, "south_from_weir": 4310, "east": 4312},
        "flags": ["outdoor", "water", "dangerous", "underground"],
    },
    {
        "vnum": 4312,
        "name": "Lantern Pool",
        "description": (
            "The grotto opens into a broad water-chamber lit by a single shaft "
            "of daylight that falls through a crack far above. The pool is "
            "fifteen feet across and fathoms deep. The walls are slick with "
            "carbonate and webbed with root-systems of whatever grows on the "
            "bluff above. The singing is louder here."
        ),
        "exits": {"west": 4311, "east": 4313, "north": 4314},
        "flags": ["indoor", "water", "dangerous", "underground"],
    },
    {
        "vnum": 4313,
        "name": "Grotto -- The Deep Chamber",
        "description": (
            "The grotto ends in a domed chamber whose pool is deeper than its "
            "diameter -- the water drops straight down into the river's old "
            "bed. The surface of the pool is not still; it is shaping itself "
            "into a broad, humanoid figure of moving water whose attention has "
            "just turned fully upon you. This is what is angry."
        ),
        "exits": {"west": 4312},
        "flags": ["indoor", "water", "dangerous", "underground"],
    },
    {
        "vnum": 4314,
        "name": "Grotto -- Side Cache",
        "description": (
            "A narrow side-gallery dry enough to kneel in. Whoever last came "
            "here stashed their takings carefully under a ledge -- a small "
            "leather satchel, perhaps the work of a diver from long ago who "
            "never came back up. The satchel's contents have weathered the "
            "years better than the satchel itself."
        ),
        "exits": {"south": 4312},
        "flags": ["indoor", "underground"],
    },
    {
        "vnum": 4315,
        "name": "Upriver Gate",
        "description": (
            "A small stone landing marks the east-bank approach the River-"
            "Gate guards use when they patrol downriver. The path from the "
            "city's East River Gate comes in along the top of the bank. The "
            "Muddywake lies west; the river flats of Kinsweave lie east."
        ),
        "exits": {"west": 4308, "north_gate": 4024},
        "flags": ["outdoor", "water"],
    },
]


# Fix a typo/hack: some of the above used placeholder non-standard direction
# keys ("south_duplicate", "south_from_weir", "north_gate") to keep exits
# distinct while drafting; strip them before emit (they were authoring
# scaffolds, not real directions).
_SCAFFOLD_KEYS = {"south_duplicate", "south_from_weir", "north_gate"}

def _clean_exits(rooms: List[Dict[str, Any]]) -> None:
    for r in rooms:
        for k in list(r.get("exits", {}).keys()):
            if k in _SCAFFOLD_KEYS or r["exits"][k] is None:
                del r["exits"][k]


# ---------------------------------------------------------------------------
# Outbound exits to wire from existing Custos rooms into the new zones
# ---------------------------------------------------------------------------

# (existing_vnum, direction, target_vnum)
NEW_CUSTOS_EXITS = [
    (4012, "down",  4200),  # Deepwell Tavern -> Under the Deepwell Tavern
    (4152, "down",  4205),  # Pekakarlik Canal Walk -> Canal Grate Chamber
    (4142, "down",  4210),  # Safe House -> Under the Safe House
    (4161, "east",  4215),  # Donation Vault -> The Vault Breach
    (4144, "down",  4220),  # Dodger's Gate Postern -> The Postern Shaft
    (4021, "south", 4300),  # Dockside Shrine of Semyon -> Shrine Skiff Landing
                            # (east is taken; south is the water-ward door)
    (4024, "north", 4315),  # East River Gate -> Upriver Gate
]


# ---------------------------------------------------------------------------
# New items (vnums 700-704) -- "ok but not great" starter gear
# ---------------------------------------------------------------------------

NEW_ITEMS: List[Dict[str, Any]] = [
    {
        "vnum": 700,
        "name": "Masterwork Shortsword",
        "item_type": "weapon",
        "weight": 2,
        "value": 310,
        "description": (
            "A well-balanced shortsword with a blued steel blade and a "
            "leather-wrapped grip. The workmanship grants a +1 bonus to "
            "attack rolls."
        ),
        "damage": [1, 6, 0],
        "properties": ["martial", "masterwork"],
    },
    {
        "vnum": 701,
        "name": "Masterwork Studded Leather",
        "item_type": "armor",
        "weight": 20,
        "value": 175,
        "description": (
            "Supple leather armor reinforced with closely-spaced iron studs. "
            "The exacting fit reduces its armor check penalty and allows "
            "freer movement."
        ),
        "ac_bonus": 3,
        "properties": ["medium", "masterwork"],
    },
    {
        "vnum": 702,
        "name": "Pekakarlik Signet Ring",
        "item_type": "ring",
        "weight": 0,
        "value": 50,
        "description": (
            "A ring of dull grey stone polished smooth, its face carved with "
            "the overturned-anvil mark of the Pekakarlik tunnel-stewards. It "
            "is not magical, but Pekakarlik who see it worn tend to notice."
        ),
        "properties": ["ring", "flavor"],
    },
    {
        "vnum": 703,
        "name": "Waterward Amulet",
        "item_type": "amulet",
        "weight": 0.1,
        "value": 300,
        "description": (
            "A carved river-pearl hung on a silver chain, blessed at a shrine "
            "of Semyon. Grants resistance 5 against cold damage."
        ),
        "properties": ["amulet", "minor_magic"],
    },
    {
        "vnum": 704,
        "name": "Shrine Pendant of Semyon",
        "item_type": "amulet",
        "weight": 0.1,
        "value": 200,
        "description": (
            "A small bronze pendant stamped with Semyon's river-crown. Grants "
            "a +1 sacred bonus on Will saves made against water-elemental "
            "effects."
        ),
        "properties": ["amulet", "minor_magic"],
    },
]


# ---------------------------------------------------------------------------
# New mob spawns (vnums 3500-3522) -- 23 spawns across both zones
# ---------------------------------------------------------------------------

def _make_mob(vnum, name, level, hp, ac, dmg, room_vnum, type_, cr,
              loot=None, attacks=None, flags=None, desc=""):
    """Build a minimally-complete mob dict matching the existing schema."""
    hpd = hp if isinstance(hp, list) else [hp, 8, 0]
    damd = dmg if isinstance(dmg, list) else [1, dmg, 0]
    return {
        "vnum": vnum,
        "name": name,
        "level": level,
        "hp_dice": hpd,
        "ac": ac,
        "damage_dice": damd,
        "flags": flags or [],
        "room_vnum": room_vnum,
        "type_": type_,
        "alignment": "Neutral",
        "ability_scores": {"Str": 10, "Dex": 12, "Con": 11,
                           "Int": 3,  "Wis": 10, "Cha": 4},
        "initiative": 1,
        "speed": {"land": 30},
        "attacks": attacks or [{"type": "bite", "bonus": level,
                                "damage": f"{damd[0]}d{damd[1]}+{damd[2]}"}],
        "special_attacks": [],
        "special_qualities": [],
        "feats": [],
        "skills": {},
        "saves": {"Fort": level // 2 + 1, "Ref": 1, "Will": 0},
        "environment": "Underground",
        "organization": "solitary",
        "cr": cr,
        "advancement": "-",
        "description": desc,
        "loot_table": loot or [],
    }

# Loot tables: existing items from items.json we know exist
COIN_POUCH = [{"vnum": 2,   "chance": 0.25}]       # dagger drops for low tier
DAGGER_DROP = [{"vnum": 2,  "chance": 0.30}]
SHORTSWORD_DROP = [{"vnum": 5, "chance": 0.20}]
LEATHER_DROP = [{"vnum": 102, "chance": 0.25}]     # leather armor vnum guess
CLUB_DROP = [{"vnum": 1,   "chance": 0.40}]
POTION_DROP = [{"vnum": 301,"chance": 0.15}]       # cure light wounds
TORCH_DROP = [{"vnum": 203,"chance": 0.50}]
# New item drops
MW_SHORTSWORD = [{"vnum": 700, "chance": 0.50}]
MW_ARMOR     = [{"vnum": 701, "chance": 0.45}]
SIGNET_RING  = [{"vnum": 702, "chance": 0.35}]
WARDAMULET   = [{"vnum": 703, "chance": 0.60}]
SHRINE_PEND  = [{"vnum": 704, "chance": 0.55}]


NEW_MOBS: List[Dict[str, Any]] = [
    # Undercity -- Upper Sewers
    _make_mob(3500, "Giant Rat", 1, [1,8,1], 14, [1,3,0], 4203, "Animal", 0.33,
              loot=TORCH_DROP + COIN_POUCH, flags=["animal","hostile"],
              desc="A bloated, scabrous rat the size of a small dog, with yellow incisors stained from generations of garbage."),
    _make_mob(3501, "Giant Rat", 1, [1,8,1], 14, [1,3,0], 4203, "Animal", 0.33,
              loot=[], flags=["animal","hostile"],
              desc="A matted specimen, its fur plastered with filth and its pink tail still bleeding from its last skirmish."),
    _make_mob(3502, "Stirge", 1, [1,10,0], 16, [1,3,0], 4206, "Magical Beast", 0.5,
              loot=[], flags=["hostile"],
              attacks=[{"type":"piercing proboscis","bonus":7,"damage":"1d3"}],
              desc="A leathery flyer with a needle-pointed beak, dripping with half-digested blood."),
    _make_mob(3503, "Monstrous Spider", 2, [2,8,2], 14, [1,4,0], 4222, "Vermin", 1,
              loot=DAGGER_DROP, flags=["hostile"],
              attacks=[{"type":"venomous bite","bonus":2,"damage":"1d4+poison"}],
              desc="A dog-sized black spider whose abdomen is striped with wet red."),
    _make_mob(3504, "Dire Rat Alpha", 2, [3,8,6], 15, [1,6,2], 4207, "Animal", 1,
              loot=DAGGER_DROP + COIN_POUCH + POTION_DROP, flags=["animal","hostile","boss"],
              attacks=[{"type":"savage bite","bonus":4,"damage":"1d6+2"}],
              desc="A rat larger than a wolf, its eyes intelligent, its jaws broad enough to sever a wrist."),

    # Undercity -- Old Cisterns
    _make_mob(3505, "Cistern Zombie", 2, [2,12,3], 11, [1,6,1], 4209, "Undead", 0.5,
              loot=LEATHER_DROP, flags=["undead","hostile"],
              attacks=[{"type":"slam","bonus":2,"damage":"1d6+1"}],
              desc="A bloated corpse, river-water streaming from its mouth and nostrils, eyes white and sightless."),
    _make_mob(3506, "Cistern Zombie", 2, [2,12,3], 11, [1,6,1], 4209, "Undead", 0.5,
              loot=[], flags=["undead","hostile"],
              desc="Another waterlogged cadaver, its movements slow and purposeful despite the damage."),
    _make_mob(3507, "Arch Skeleton", 1, [1,12,0], 13, [1,6,0], 4211, "Undead", 0.33,
              loot=CLUB_DROP, flags=["undead","hostile"],
              attacks=[{"type":"rusted blade","bonus":1,"damage":"1d6"}],
              desc="A skeleton in the rotted remnants of sentry livery, still gripping a pitted sword."),
    _make_mob(3508, "Arch Skeleton", 1, [1,12,0], 13, [1,6,0], 4211, "Undead", 0.33,
              loot=[], flags=["undead","hostile"],
              desc="Another sentry long dead at his post, reanimated by something that has no name anymore."),
    _make_mob(3509, "Starveling Ghoul", 2, [2,12,0], 14, [1,6,0], 4213, "Undead", 1,
              loot=DAGGER_DROP + POTION_DROP + WARDAMULET, flags=["undead","hostile"],
              attacks=[{"type":"claws","bonus":3,"damage":"1d3+1 plus paralysis"}],
              desc="A twisted figure with skin pulled taut over bones, its hunger so old it has forgotten food."),

    # Undercity -- Pekakarlik Tunnels
    _make_mob(3510, "Kobold Raider", 1, [1,8,0], 15, [1,4,0], 4217, "Humanoid", 0.25,
              loot=CLUB_DROP, flags=["hostile"],
              attacks=[{"type":"short spear","bonus":1,"damage":"1d6-1"}],
              desc="A small scaly humanoid in filthy leathers, yipping and brandishing a spear."),
    _make_mob(3511, "Kobold Raider", 1, [1,8,0], 15, [1,4,0], 4217, "Humanoid", 0.25,
              loot=[], flags=["hostile"],
              desc="Another kobold, its crest-scales dyed an alarming red with human blood."),
    _make_mob(3512, "Kobold Hoarder", 1, [1,8,0], 15, [1,4,0], 4218, "Humanoid", 0.25,
              loot=COIN_POUCH + POTION_DROP, flags=["hostile"],
              desc="A kobold crouched over a pile of stolen trinkets, squealing indignantly."),
    _make_mob(3513, "Small Earth Elemental", 2, [2,8,4], 17, [1,4,1], 4219, "Elemental", 1,
              loot=SIGNET_RING, flags=["hostile"],
              attacks=[{"type":"slam","bonus":4,"damage":"1d4+2"}],
              desc="A humanoid shape of packed dirt and gravel, dislocated from its quarry and deeply confused."),
    _make_mob(3514, "Quarry-Golem Shard", 3, [3,10,6], 17, [1,8,2], 4221, "Construct", 3,
              loot=MW_ARMOR, flags=["hostile","construct"],
              attacks=[{"type":"stone fist","bonus":5,"damage":"1d8+3"}],
              desc="A column-sized fragment of Pekakarlik stonework brought to angry motion, its kneeling-figure shape half-broken."),
    _make_mob(3515, "Cellar Spider", 1, [1,8,1], 14, [1,4,0], 4222, "Vermin", 0.5,
              loot=TORCH_DROP, flags=["hostile"],
              attacks=[{"type":"venomous bite","bonus":2,"damage":"1d4"}],
              desc="A lean grey-brown spider with long trembling legs, its web thick enough to snare unwary feet."),

    # Undercity -- The Old Vault
    _make_mob(3516, "Gelatinous Cube", 3, [4,10,16], 3, [1,6,0], 4225, "Ooze", 3,
              loot=MW_SHORTSWORD + DAGGER_DROP + POTION_DROP, flags=["hostile","ooze"],
              attacks=[{"type":"slam","bonus":2,"damage":"1d6 plus paralysis"}],
              desc="A near-transparent cube of faintly glowing jelly, ten feet on a side, full of half-dissolved reminders of earlier visitors."),
    _make_mob(3517, "Homunculus", 1, [2,10,0], 14, [1,4,0], 4226, "Construct", 1,
              loot=[{"vnum":303,"chance":0.3}], flags=["hostile","construct"],
              attacks=[{"type":"bite","bonus":2,"damage":"1d4 plus sleep"}],
              desc="A small leathery creature the size of a cat, with bat-wings and a miniature human face carved in resentful lines."),
    _make_mob(3518, "Pekakarlik Tunnel-Warden", 5, [5,10,15], 18, [1,10,3], 4228, "Humanoid", 3,
              loot=MW_SHORTSWORD + MW_ARMOR + SIGNET_RING + POTION_DROP,
              flags=["hostile","boss"],
              attacks=[{"type":"warhammer","bonus":8,"damage":"1d10+4"}],
              desc="A Pekakarlik dwarf of immense age, his beard gone the color of iron filings, his eyes the flat grey of old stone."),

    # Muddywake -- Reed Shallows
    _make_mob(3519, "Giant Leech", 1, [1,8,1], 13, [1,4,0], 4301, "Vermin", 0.5,
              loot=[], flags=["hostile"],
              attacks=[{"type":"bite","bonus":1,"damage":"1d4 plus blood drain"}],
              desc="A mottled black worm as long as a forearm, pulsing as it fastens to its prey."),
    _make_mob(3520, "Giant Frog", 2, [2,8,2], 12, [1,4,0], 4302, "Animal", 1,
              loot=TORCH_DROP, flags=["animal","hostile"],
              attacks=[{"type":"tongue/bite","bonus":2,"damage":"1d4"}],
              desc="A bullfrog the size of a pony, throat ballooning in mating-cry or threat."),
    _make_mob(3521, "Merfolk Scout", 1, [1,8,1], 14, [1,6,0], 4303, "Humanoid", 0.5,
              loot=SHORTSWORD_DROP, flags=["hostile"],
              attacks=[{"type":"short spear","bonus":1,"damage":"1d6"}],
              desc="A slim merfolk with pale green scales, peering from the reeds with a bone spear ready."),

    # Muddywake -- Sunken Shrine branch
    _make_mob(3522, "Nixie", 2, [2,6,0], 14, [1,4,0], 4305, "Fey", 1,
              loot=SHRINE_PEND, flags=["hostile"],
              attacks=[{"type":"dagger","bonus":2,"damage":"1d4"}],
              desc="A delicate figure with webbed fingers and silver-green hair, her smile edged with predator's teeth."),
    _make_mob(3523, "Water Mephit", 3, [3,8,3], 16, [1,3,0], 4307, "Outsider", 3,
              loot=POTION_DROP + WARDAMULET, flags=["hostile","outsider"],
              attacks=[{"type":"claws","bonus":4,"damage":"1d3"}],
              desc="A small turquoise-scaled imp with gill-fringes, dripping river-water wherever it moves."),

    # Muddywake -- Weir
    _make_mob(3524, "River-Borne Ankheg", 3, [3,10,6], 18, [2,6,3], 4309, "Magical Beast", 3,
              loot=MW_ARMOR, flags=["hostile"],
              attacks=[{"type":"mandible","bonus":6,"damage":"2d6+3"}],
              desc="A chitinous predator washed down from Kinsweave floodplains, miserable in the water and furious about it."),
    _make_mob(3525, "Merfolk Hunter", 2, [2,8,4], 15, [1,8,1], 4310, "Humanoid", 2,
              loot=SHORTSWORD_DROP + COIN_POUCH, flags=["hostile"],
              attacks=[{"type":"trident","bonus":3,"damage":"1d8+1"}],
              desc="A weather-hardened merfolk warrior with deep-sea scars, guarding the crossing with bared teeth."),

    # Muddywake -- Boss
    _make_mob(3526, "Medium Water Elemental", 3, [3,8,6], 16, [1,6,1], 4313, "Elemental", 3,
              loot=MW_SHORTSWORD + SHRINE_PEND + WARDAMULET + POTION_DROP,
              flags=["hostile","boss","elemental"],
              attacks=[{"type":"slam","bonus":4,"damage":"1d6+1"},
                       {"type":"drench","bonus":4,"damage":"1d6 cold"}],
              desc="A humanoid pillar of moving water, its surface rippling with the faces of things that have drowned in its reach."),
]


# ---------------------------------------------------------------------------
# Merge logic -- idempotent writes
# ---------------------------------------------------------------------------

def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _atomic_write(path: str, obj) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def merge_rooms_into_area():
    path = os.path.join(DATA, "areas", "CustosDoAeternos.json")
    rooms = _read_json(path)
    existing = {r.get("vnum") for r in rooms}
    added = 0

    # Append new rooms (idempotent by vnum)
    for new_room in UNDERCITY_ROOMS + MUDDYWAKE_ROOMS:
        if new_room["vnum"] in existing:
            continue
        rooms.append(new_room)
        existing.add(new_room["vnum"])
        added += 1

    # Wire new outbound exits on existing Custos rooms
    wired = 0
    by_vnum = {r["vnum"]: r for r in rooms}
    for src_v, direction, dest_v in NEW_CUSTOS_EXITS:
        r = by_vnum.get(src_v)
        if r is None:
            print(f"  WARN: source room {src_v} not found for exit")
            continue
        exits = r.setdefault("exits", {})
        if exits.get(direction) == dest_v:
            continue
        if direction in exits and exits[direction] != dest_v:
            print(f"  WARN: room {src_v} already has '{direction}' exit to "
                  f"{exits[direction]}; not overwriting.")
            continue
        exits[direction] = dest_v
        wired += 1

    _atomic_write(path, rooms)
    print(f"  Custos area: +{added} rooms, +{wired} new outbound exits "
          f"(total rooms now {len(rooms)})")


def merge_mobs():
    path = os.path.join(DATA, "mobs.json")
    mobs = _read_json(path)
    existing = {m.get("vnum") for m in mobs}
    added = 0
    for m in NEW_MOBS:
        if m["vnum"] in existing:
            continue
        mobs.append(m)
        added += 1
    _atomic_write(path, mobs)
    print(f"  mobs.json: +{added} new mob spawns (total now {len(mobs)})")


def merge_items():
    path = os.path.join(DATA, "items.json")
    items = _read_json(path)
    if isinstance(items, list):
        existing = {it.get("vnum") for it in items}
        added = 0
        for it in NEW_ITEMS:
            if it["vnum"] in existing:
                continue
            items.append(it)
            added += 1
        _atomic_write(path, items)
        print(f"  items.json: +{added} new items (total now {len(items)})")
    else:
        print("  items.json: unexpected dict form, skipping item merge")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    # Scrub authoring scaffolds
    _clean_exits(UNDERCITY_ROOMS)
    _clean_exits(MUDDYWAKE_ROOMS)

    print("Building Custos starter zones:")
    merge_rooms_into_area()
    merge_mobs()
    merge_items()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
