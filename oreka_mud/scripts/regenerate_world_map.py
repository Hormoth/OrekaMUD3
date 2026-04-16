"""Regenerate the world map data file.

Scans every area JSON under ``data/areas/`` and emits
``../oreka_world_map_data.js`` (at the repo root, alongside
``oreka_world_map.html``) as a single ``const ROOM_DATA = {...};``
line the viewer HTML expects.

Room descriptions are truncated to ~200 chars for map-viewer tooltip
readability (matches the existing file's convention).  Exits that
point to non-existent rooms are dropped.

Run:
    python scripts/regenerate_world_map.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict


HERE = os.path.dirname(os.path.abspath(__file__))
DATA_AREAS = os.path.normpath(os.path.join(HERE, "..", "data", "areas"))
OUT_PATH = os.path.normpath(
    os.path.join(HERE, "..", "..", "oreka_world_map_data.js")
)

# Description truncation -- matches the existing file's convention
DESC_TRUNC = 200


def truncate(s: str, n: int = DESC_TRUNC) -> str:
    if s is None:
        return ""
    s = str(s)
    if len(s) <= n:
        return s
    return s[:n]


def scan_areas() -> Dict[int, Dict[str, Any]]:
    """Walk every area file and produce {vnum: room_dict}."""
    rooms: Dict[int, Dict[str, Any]] = {}
    for fn in sorted(os.listdir(DATA_AREAS)):
        if not fn.endswith(".json"):
            continue
        area = fn[:-5]  # strip .json
        path = os.path.join(DATA_AREAS, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  WARN: could not read {fn}: {e}")
            continue

        room_list = data if isinstance(data, list) else data.get("rooms", [])
        if isinstance(room_list, dict):
            room_list = list(room_list.values())

        for r in room_list:
            v = r.get("vnum")
            if v is None:
                continue
            # Drop non-integer exit values (occasional string sentinels)
            exits_clean = {}
            for direction, dest in (r.get("exits") or {}).items():
                if isinstance(dest, int):
                    exits_clean[direction] = dest
            rooms[int(v)] = {
                "vnum":  int(v),
                "name":  r.get("name", ""),
                "desc":  truncate(r.get("description", "")),
                "area":  area,
                "flags": list(r.get("flags", []) or []),
                "exits": exits_clean,
            }
    return rooms


def prune_dangling_exits(rooms: Dict[int, Dict[str, Any]]) -> int:
    """Remove exits that point to vnums not loaded from any area."""
    pruned = 0
    vnums = set(rooms.keys())
    for r in rooms.values():
        for direction in list(r["exits"].keys()):
            if r["exits"][direction] not in vnums:
                del r["exits"][direction]
                pruned += 1
    return pruned


def emit(rooms: Dict[int, Dict[str, Any]]) -> None:
    """Write the ROOM_DATA constant to the output JS file."""
    # The viewer keys by stringified vnum, matching the existing file
    payload = {str(v): r for v, r in sorted(rooms.items())}
    js = "const ROOM_DATA = " + json.dumps(payload, ensure_ascii=True) + ";\n"
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(js)
    os.replace(tmp, OUT_PATH)


def main() -> int:
    print("Regenerating world map data:")
    rooms = scan_areas()
    print(f"  scanned {len(rooms)} rooms across "
          f"{len({r['area'] for r in rooms.values()})} area files")
    pruned = prune_dangling_exits(rooms)
    if pruned:
        print(f"  pruned {pruned} exits pointing to non-existent rooms")

    # Per-area breakdown
    from collections import Counter
    by_area = Counter(r["area"] for r in rooms.values())
    for area, n in sorted(by_area.items()):
        print(f"    {area:25s} {n:>4}")

    emit(rooms)
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"  wrote {OUT_PATH} ({size_kb:.1f} KB)")
    print()
    print("To view: open `oreka_world_map.html` in a browser.")
    print("On Windows: `start oreka_world_map.html` from the repo root.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
