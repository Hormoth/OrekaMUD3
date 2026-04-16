"""Phase 6: sprinkle captives across non-Deceiver wilderness rooms.

Scans ``data/mobs.json`` for rooms that already contain hostile mobs
(the natural "captors") in the seven main regions, excluding the
authored Deceiver zones and the existing Custos/exemplar placements,
then adds bound captive NPCs to a random sample of them.

Captives get:
  - Random template (scout/farmer/merchant/child/scholar)
  - Random family from the region's pool (falls back to any family)
  - Random rescue_type weighted per captives.RESCUE_TYPE_WEIGHTS
  - family_fate rolled at rescue time (not baked in here)

Vnums 4321-4349 are reserved for the 25 scattered captives.

Idempotent by vnum.  Run:
    python scripts/scatter_wilderness_captives.py
"""

from __future__ import annotations

import json
import os
import random
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..")))


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Deceiver-zone vnum ranges and Custos placements to EXCLUDE
EXCLUDED_RANGES: List[Tuple[int, int]] = [
    (4200, 4321),    # Custos Undercity + Muddywake + family NPCs + exemplars
    (5308, 5345),    # Kinsweave Deceiver zones (Highridge + Andrio)
    (6251, 6282),    # Tidebloom Deceiver zones (Raider Camp + Enclave)
    (7246, 7283),    # Eternal Steppe Deceiver zones (Burnt Hollows + Second Breath)
    (8264, 8295),    # Infinite Desert Deceiver zones
    (9360, 9399),    # Deepwater Deceiver zones
    (10307, 10340),  # Twin Rivers Deceiver zones
    (12250, 12291),  # Gatefall Deceiver zones
]

# Region vnum ranges (must match the encounter-table build)
REGION_VNUMS = {
    "kinsweave":       (5000, 5999),
    "eternalsteppe":   (7000, 7999),
    "infinitedesert":  (8000, 8999),
    "gatefall":        (12000, 12999),
    "deepwater":       (9000, 9999),
    "tidebloom":       (6000, 6999),
    "twinrivers":      (10000, 10999),
}

# How many to place per region
PLACEMENTS_PER_REGION = {
    "kinsweave":       4,
    "eternalsteppe":   4,
    "infinitedesert":  4,
    "gatefall":        3,
    "deepwater":       4,
    "tidebloom":       3,
    "twinrivers":      3,
}

# Non-combat / non-hostile flags -- a mob bearing any of these is not a "captor"
SKIP_FLAGS = {
    "no_attack", "shopkeeper", "innkeeper", "trainer", "priest",
    "guard", "quest_giver", "nonaggressive", "family_rep",
    "captive",
}

# Vnum allocation base -- leaves 5316-5320 as the exemplars and uses
# fresh vnums for scattered captives.
SCATTER_VNUM_BASE = 4321


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _in_excluded_range(vnum: int) -> bool:
    return any(lo <= vnum <= hi for lo, hi in EXCLUDED_RANGES)


def _region_of(vnum: int) -> str:
    for region, (lo, hi) in REGION_VNUMS.items():
        if lo <= vnum <= hi:
            return region
    return ""


# ---------------------------------------------------------------------------
# Build the captive record
# ---------------------------------------------------------------------------

def _make_captive(vnum: int, room_vnum: int, template_id: str,
                  family_id: str, rescue_type: str,
                  captor_type: str) -> Dict:
    # Persona flavor
    name = random.choice([
        "the tied-up traveler",
        "the bound captive",
        "the gagged prisoner",
        "the chained farmer",
        "the shackled scout",
        "the roped-up villager",
    ])
    desc_starts = [
        "A weary figure roped to a post, face bruised, eyes uncertain.",
        "A slumped form in travel-stained clothes, wrists cut raw by binding rope.",
        "A prisoner gagged and tied, who goes rigid at the sound of strangers entering.",
        "A bloodied captive propped against the wall, semi-conscious.",
        "A quiet figure whose bindings are recent and whose eyes have seen things.",
    ]
    desc = random.choice(desc_starts) + \
        " Their clothing suggests they come from somewhere nearby."
    return {
        "vnum": vnum,
        "name": name,
        "level": 1,
        "hp_dice": [1, 8, 2],
        "ac": 10,
        "damage_dice": [1, 3, 0],
        "flags": ["captive", "nonaggressive", "quest_giver"],
        "type_": "Humanoid",
        "alignment": "Neutral Good",
        "ability_scores": {"Str": 9, "Dex": 10, "Con": 10,
                            "Int": 11, "Wis": 11, "Cha": 10},
        "initiative": 0,
        "speed": {"land": 30},
        "attacks": [],
        "special_attacks": [],
        "special_qualities": [],
        "feats": [],
        "skills": {},
        "saves": {"Fort": 0, "Ref": 0, "Will": 1},
        "environment": f"Captive of {captor_type}",
        "organization": "solitary captive",
        "cr": None,
        "advancement": "-",
        "description": desc,
        "room_vnum": room_vnum,
        "loot_table": [],
        "captive_family": family_id,
        "captive_template": template_id,
        "captive_captor_type": captor_type,
        "captive_state": "bound",
        "rescue_type": rescue_type,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    random.seed()  # fresh randomness each run

    path = os.path.join(DATA, "mobs.json")
    with open(path, "r", encoding="utf-8") as f:
        mobs = json.load(f)

    # Find captor-rooms per region
    hostile_rooms: Dict[str, List[int]] = defaultdict(list)
    # Track what hostile types are in each room (for captor_type flavor)
    room_captor_type: Dict[int, str] = {}
    for m in mobs:
        v = m.get("room_vnum")
        if v is None or _in_excluded_range(v):
            continue
        flags = {str(f).lower() for f in m.get("flags", []) or []}
        if flags & SKIP_FLAGS:
            continue
        region = _region_of(v)
        if not region:
            continue
        if v not in room_captor_type:
            hostile_rooms[region].append(v)
            # Pick a captor-type label from the mob's name/type
            type_ = m.get("type_", "")
            mname = m.get("name", "")
            room_captor_type[v] = f"{mname} group"

    # Load captives module for rescue-type rolling and family picking
    from src.captives import _roll_rescue_type, get_data as captives_data
    cd = captives_data()

    # Existing vnums in mobs.json to avoid collision
    existing_vnums = {m.get("vnum") for m in mobs}

    placements = []
    next_vnum = SCATTER_VNUM_BASE
    for region, rooms in hostile_rooms.items():
        n = PLACEMENTS_PER_REGION.get(region, 0)
        if n == 0 or not rooms:
            continue
        chosen = random.sample(rooms, min(n, len(rooms)))

        regional_families = cd.get_family_for_region(region)
        if not regional_families:
            # Fallback: any family
            regional_families = list(cd.families.values())
        if not regional_families:
            continue

        for room_vnum in chosen:
            # Skip if this vnum is already in use (idempotent)
            while next_vnum in existing_vnums:
                next_vnum += 1
            family = random.choice(regional_families)
            template = random.choice(list(cd.templates.keys())
                                      or ["scout"])
            rescue_type = _roll_rescue_type()
            captor_type = room_captor_type.get(room_vnum, f"{region} hostiles")

            captive = _make_captive(next_vnum, room_vnum, template,
                                     family["id"], rescue_type,
                                     captor_type)
            mobs.append(captive)
            existing_vnums.add(next_vnum)
            placements.append((next_vnum, region, room_vnum,
                               family["id"], template, rescue_type))
            next_vnum += 1

    # Write back
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(mobs, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

    print(f"Scattered {len(placements)} captives across wilderness rooms.\n")
    by_region = defaultdict(int)
    by_type = defaultdict(int)
    for vnum, region, room, fam, tmpl, rtype in placements:
        by_region[region] += 1
        by_type[rtype] += 1
    print("By region:")
    for r, n in sorted(by_region.items()):
        print(f"  {r:18s} {n}")
    print("\nBy rescue type:")
    for t, n in sorted(by_type.items()):
        print(f"  {t:15s} {n}")
    print(f"\nmobs.json now has {len(mobs)} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
