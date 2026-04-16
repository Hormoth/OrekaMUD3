"""Build regional random-encounter tables from the bestiary.

Scans ``data/mobs_bestiary.json`` and classifies each creature into one or
more of the seven encounter regions based on its ``environment`` text and
generic terrain keywords.  Output is one JSON file per region under
``data/encounter_tables/``, plus a ``region_map.json`` recording which
room vnums belong to which region.

Run:
    python scripts/build_encounter_tables.py

The script is safe to re-run; it overwrites the generated files.
"""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Set


# ---------------------------------------------------------------------------
# Region definitions
# ---------------------------------------------------------------------------

# Each region maps to the area JSON file(s) that compose it.  Encounters
# only fire in rooms belonging to one of these regions.
REGION_AREAS: Dict[str, List[str]] = {
    "kinsweave":      ["Kinsweave.json"],
    "eternalsteppe":  ["EternalSteppe.json"],
    "infinitedesert": ["InfiniteDesert.json"],
    "gatefall":       ["GatefallReach.json"],
    "deepwater":      ["DeepwaterExpansion.json", "DeepwaterMarches.json"],
    "tidebloom":      ["TidebloomReach.json"],
    "twinrivers":     ["TwinRivers.json"],
}

# Keyword groups used to classify a bestiary creature into a region by its
# free-text ``environment`` description.  Lowercase, substring match.
REGION_KEYWORDS: Dict[str, List[str]] = {
    "kinsweave":      ["kinsweave", "mytro", "sand-buried", "buried city"],
    "eternalsteppe":  ["steppe", "eternal steppe", "mytroan", "pasua",
                       "tavranek", "zhoraven"],
    "infinitedesert": ["infinite desert", "desert", "pekakarlik", "dune",
                       "oasis", "sand wraith"],
    "gatefall":       ["gatefall", "vestri", "mountain", "mining",
                       "dwarf hold", "tunnel network"],
    "deepwater":      ["deepwater", "marches", "swamp", "marsh", "bog",
                       "wetland", "fen"],
    "tidebloom":      ["tidebloom", "coast", "shore", "tidepool", "kelp",
                       "salt-marsh", "shallows"],
    "twinrivers":     ["twin rivers", "great river", "eruskan", "river-gate",
                       "river-fork", "canal", "tributary", "river"],
}

# Generic terrain keywords -> region affinity, used when a creature's
# environment field doesn't name a region directly but does name a biome
# that maps to one (e.g. "temperate forest" -> twinrivers/gatefall edges).
TERRAIN_AFFINITY: Dict[str, List[str]] = {
    "forest":      ["twinrivers", "gatefall", "tidebloom"],
    "plains":      ["eternalsteppe", "kinsweave"],
    "grassland":   ["eternalsteppe"],
    "mountain":    ["gatefall"],
    "hills":       ["gatefall", "twinrivers"],
    "swamp":       ["deepwater"],
    "marsh":       ["deepwater"],
    "underground": ["gatefall", "kinsweave", "infinitedesert"],
    "cave":        ["gatefall", "kinsweave"],
    "river":       ["twinrivers", "deepwater"],
    "lake":        ["twinrivers", "deepwater"],
    "coast":       ["tidebloom"],
    "ocean":       ["tidebloom"],
    "ruin":        ["kinsweave", "infinitedesert"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CR_FRACTION_RE = re.compile(r"^(\d+)\s*/\s*(\d+)")
_CR_NUMERIC_RE = re.compile(r"^(\d+(?:\.\d+)?)")


def parse_cr(raw) -> float | None:
    """Parse a CR field into a float.  Returns None for unparseable values."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip()
    m = _CR_FRACTION_RE.match(s)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = _CR_NUMERIC_RE.match(s)
    if m:
        return float(m.group(1))
    return None


def classify_creature(env_text: str) -> Set[str]:
    """Return the set of region keys this creature belongs to."""
    text = (env_text or "").lower()
    if not text:
        return set()

    matched: Set[str] = set()

    # Direct regional keyword hits
    for region, keywords in REGION_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matched.add(region)
                break

    # Terrain affinity fallback (only if no direct hit)
    if not matched:
        for terrain, regions in TERRAIN_AFFINITY.items():
            if terrain in text:
                matched.update(regions)

    return matched


def cr_bucket(cr: float) -> str:
    """Bucket CR into a string key for table lookup.

    Sub-CR-1 creatures are bucketed together as ``"0"``; integer CRs above
    that are stored as their integer string.  Half-CRs round down so a
    CR 1/2 lands in bucket 0 with the other low-tier creatures.
    """
    if cr < 1:
        return "0"
    return str(int(cr))


# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------

def build_region_map(data_dir: str) -> Dict[str, List[int]]:
    """Walk each region's area files and collect their room vnums."""
    region_map: Dict[str, List[int]] = {}
    areas_dir = os.path.join(data_dir, "areas")

    for region, files in REGION_AREAS.items():
        vnums: List[int] = []
        for fn in files:
            path = os.path.join(areas_dir, fn)
            if not os.path.exists(path):
                print(f"  WARN: missing area file {fn}")
                continue
            with open(path, "r", encoding="utf-8") as f:
                area = json.load(f)
            rooms = area if isinstance(area, list) else area.get("rooms", [])
            if isinstance(rooms, dict):
                rooms = list(rooms.values())
            for r in rooms:
                v = r.get("vnum")
                if v is not None:
                    vnums.append(int(v))
        region_map[region] = sorted(set(vnums))
        print(f"  {region:18s} {len(region_map[region]):>4} rooms")

    return region_map


def build_tables(data_dir: str) -> Dict[str, Dict[str, list]]:
    """Build per-region encounter tables from the bestiary.

    Returns ``{region: {cr_bucket: [creature_dict, ...]}}``.  Each
    creature_dict carries the minimal fields needed to spawn a Mob at
    runtime (name, vnum hint, CR, hp_dice, etc.).
    """
    bestiary_path = os.path.join(data_dir, "mobs_bestiary.json")
    with open(bestiary_path, "r", encoding="utf-8") as f:
        bestiary = json.load(f)

    tables: Dict[str, Dict[str, list]] = {r: defaultdict(list)
                                          for r in REGION_AREAS}
    skipped_no_region = 0
    skipped_no_cr = 0

    for entry in bestiary:
        if not isinstance(entry, dict):
            continue
        cr = parse_cr(entry.get("cr") or entry.get("CR"))
        if cr is None:
            skipped_no_cr += 1
            continue
        regions = classify_creature(entry.get("environment", ""))
        if not regions:
            skipped_no_region += 1
            continue

        bucket = cr_bucket(cr)
        # Strip down to the fields we actually need at spawn time.
        slim = {
            "name":            entry.get("name"),
            "vnum":            entry.get("vnum"),
            "cr":              cr,
            "level":           entry.get("level", max(1, int(cr))),
            "hp_dice":         entry.get("hp_dice", [max(1, int(cr)), 8, 0]),
            "ac":              entry.get("ac", 10 + int(cr)),
            "damage_dice":     entry.get("damage_dice", [1, 6, 0]),
            "flags":           entry.get("flags", []),
            "type_":           entry.get("type_", "humanoid"),
            "alignment":       entry.get("alignment", "neutral"),
            "ability_scores":  entry.get("ability_scores"),
            "speed":           entry.get("speed", 30),
            "attacks":         entry.get("attacks", []),
            "special_attacks": entry.get("special_attacks", []),
            "special_qualities": entry.get("special_qualities", []),
            "feats":           entry.get("feats", []),
            "skills":          entry.get("skills", {}),
            "saves":           entry.get("saves", {}),
            "environment":     entry.get("environment", ""),
            "organization":    entry.get("organization", "solitary"),
            "description":     entry.get("description", ""),
        }
        for region in regions:
            tables[region][bucket].append(slim)

    # Report
    print(f"\n  Skipped (no parseable CR):  {skipped_no_cr}")
    print(f"  Skipped (no region match):  {skipped_no_region}")
    print()
    for region in REGION_AREAS:
        buckets = tables[region]
        total = sum(len(v) for v in buckets.values())
        bucket_summary = ", ".join(
            f"CR{k}={len(buckets[k])}" for k in sorted(buckets, key=lambda x: int(x))
        )
        print(f"  {region:18s} {total:>4} entries  ({bucket_summary})")

    return {r: dict(b) for r, b in tables.items()}


def write_outputs(data_dir: str,
                  region_map: Dict[str, List[int]],
                  tables: Dict[str, Dict[str, list]]) -> None:
    out_dir = os.path.join(data_dir, "encounter_tables")
    os.makedirs(out_dir, exist_ok=True)

    region_map_path = os.path.join(out_dir, "region_map.json")
    with open(region_map_path, "w", encoding="utf-8") as f:
        json.dump(region_map, f, indent=2)
    print(f"\n  Wrote {region_map_path}")

    for region, buckets in tables.items():
        path = os.path.join(out_dir, f"{region}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"region": region, "buckets": buckets}, f, indent=2)
        print(f"  Wrote {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.normpath(os.path.join(here, "..", "data"))
    if not os.path.isdir(data_dir):
        print(f"Data directory not found: {data_dir}")
        return 1

    print("Region -> rooms")
    region_map = build_region_map(data_dir)

    print("\nClassifying bestiary creatures...")
    tables = build_tables(data_dir)

    print("\nWriting outputs...")
    write_outputs(data_dir, region_map, tables)
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
