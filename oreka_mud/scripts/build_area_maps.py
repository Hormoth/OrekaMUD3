"""
Build static HTML/SVG maps for every area in data/areas/.

Usage:
    python scripts/build_area_maps.py

Output:
    maps/areas/<AreaName>.html   — one grid map per area file
    maps/index.html              — links to all area maps

Layout strategy:
    - Start at the numerically-lowest-vnum room of the area, place at (0,0).
    - BFS outward; direction deltas:
        north → (0, -1)    south → (0, +1)
        east  → (+1, 0)    west  → (-1, 0)
        (other exits like up/down/in/out/forge/etc. are drawn as labeled
         arrows outside the grid — they don't contribute to 2D position).
    - Resolve conflicts: if a cell is already taken, the arriving room is
      nudged outward along the arrival direction until free.
    - Unreachable rooms from the start are placed in a fallback row below.

Each room renders as a square with vnum and a truncated name. Hovering
shows the description. Lines connect N/S/E/W edges. Non-directional exits
show as small labels inside the square.
"""

import json
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
AREAS_DIR = os.path.normpath(os.path.join(HERE, "..", "data", "areas"))
OUT_DIR = os.path.normpath(os.path.join(REPO_ROOT, "maps", "areas"))
INDEX_PATH = os.path.normpath(os.path.join(REPO_ROOT, "maps", "index.html"))

CELL = 120  # pixel size per room square
GAP = 28    # gap between cells
CARD = CELL + GAP

GRID_DIRS = {
    "north": (0, -1), "south": (0, 1),
    "east":  (1, 0),  "west":  (-1, 0),
    "northeast": (1, -1), "northwest": (-1, -1),
    "southeast": (1, 1),  "southwest": (-1, 1),
    "n":  (0, -1), "s":  (0, 1),
    "e":  (1, 0),  "w":  (-1, 0),
    "ne": (1, -1), "nw": (-1, -1),
    "se": (1, 1),  "sw": (-1, 1),
}

OFF_GRID_DIRS = {"up", "u", "down", "d", "in", "out", "enter", "exit"}


def _load_area(path: str):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    rooms = d if isinstance(d, list) else d.get("rooms", [])
    by_vnum = {}
    for r in rooms:
        v = r.get("vnum")
        if v is None:
            continue
        by_vnum[v] = r
    return by_vnum


def _layout(rooms_by_vnum: dict):
    """Return (positions, off_grid_exits, orphans).

    positions: {vnum: (gx, gy)}
    off_grid_exits: {vnum: [(dirname, target_vnum), ...]}
    orphans: vnums not reachable from the chosen start; laid out row below.
    """
    if not rooms_by_vnum:
        return {}, {}, []

    # Prefer a temple/altar/hub-flagged room as the BFS root so radial
    # areas like the chapel lay out as a wagon wheel (hub at center,
    # cardinal quadrants as spokes, their own diagonal exits extending).
    hub_flags = {"altar", "temple", "hub"}
    hub_candidates = [
        v for v, r in rooms_by_vnum.items()
        if hub_flags & set(r.get("flags") or [])
    ]
    start = min(hub_candidates) if hub_candidates else min(rooms_by_vnum.keys())
    positions = {start: (0, 0)}
    taken = {(0, 0): start}
    off_grid_exits = {}
    warped_edges = set()
    queue = deque([start])

    while queue:
        vnum = queue.popleft()
        room = rooms_by_vnum[vnum]
        exits = room.get("exits") or {}
        off = []
        for dname, target in exits.items():
            try:
                tvnum = int(target)
            except (TypeError, ValueError):
                continue
            if tvnum not in rooms_by_vnum:
                continue
            key = dname.lower()
            if key in GRID_DIRS:
                dx, dy = GRID_DIRS[key]
                gx, gy = positions[vnum]
                nx, ny = gx + dx, gy + dy
                if tvnum in positions:
                    continue
                shoved = False
                while (nx, ny) in taken:
                    nx += dx or 1
                    ny += dy or 0
                    shoved = True
                positions[tvnum] = (nx, ny)
                taken[(nx, ny)] = tvnum
                if shoved:
                    warped_edges.add((min(vnum, tvnum), max(vnum, tvnum)))
                queue.append(tvnum)
            else:
                off.append((key, tvnum))
        if off:
            off_grid_exits[vnum] = off

    orphans = [v for v in rooms_by_vnum if v not in positions]
    if orphans:
        # place orphans in a row below the lowest grid row
        max_y = max((y for (_, y) in positions.values()), default=0)
        sx = min((x for (x, _) in positions.values()), default=0)
        for i, v in enumerate(sorted(orphans)):
            positions[v] = (sx + i, max_y + 2)

    return positions, off_grid_exits, orphans, warped_edges


def _collect_edges(rooms_by_vnum: dict, positions: dict):
    """Return list of (a_vnum, b_vnum, direction_key_from_a) for grid edges.
    Only include A→B where both have grid positions."""
    edges = []
    seen = set()
    for vnum, r in rooms_by_vnum.items():
        if vnum not in positions:
            continue
        exits = r.get("exits") or {}
        for dname, target in exits.items():
            try:
                tvnum = int(target)
            except (TypeError, ValueError):
                continue
            if tvnum not in positions:
                continue
            key = dname.lower()
            if key not in GRID_DIRS:
                continue
            k = (min(vnum, tvnum), max(vnum, tvnum))
            if k in seen:
                continue
            seen.add(k)
            edges.append((vnum, tvnum, key))
    return edges


def _svg(rooms_by_vnum: dict, positions: dict, off_grid: dict, edges: list, area_name: str, warped_edges: set = None):
    warped_edges = warped_edges or set()
    if not positions:
        return "<p>No rooms.</p>"
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    def cell_xy(gx, gy):
        return ((gx - min_x) * CARD + GAP, (gy - min_y) * CARD + GAP)

    width = (max_x - min_x + 1) * CARD + GAP
    height = (max_y - min_y + 1) * CARD + GAP

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
             f'width="{width}" height="{height}" style="background:#0f1117;font-family:system-ui,sans-serif;">']

    # Edges (draw first so they go under cells)
    for a, b, dir_key in edges:
        ax, ay = cell_xy(*positions[a])
        bx, by = cell_xy(*positions[b])
        ax += CELL / 2; ay += CELL / 2
        bx += CELL / 2; by += CELL / 2
        pair = (min(a, b), max(a, b))
        if pair in warped_edges:
            stroke = "#b54a4a"
            dash = ' stroke-dasharray="6,4"'
        else:
            stroke = "#3e4a63"
            dash = ""
        parts.append(
            f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
            f'stroke="{stroke}" stroke-width="2"{dash} />'
        )

    # Rooms
    for vnum, (gx, gy) in sorted(positions.items()):
        room = rooms_by_vnum.get(vnum, {})
        name = (room.get("name") or f"vnum {vnum}").strip()
        desc = (room.get("description") or "").replace('"', '&quot;').replace('<', '&lt;')[:500]
        flags = room.get("flags") or []
        x, y = cell_xy(gx, gy)
        fill = "#1a1f2e"
        border = "#5b677f"
        if "safe" in flags or "temple" in flags or "altar" in flags:
            border = "#6cb38f"
        if "shop" in flags or "street" in flags:
            border = "#c79a5e"
        short_name = name if len(name) <= 22 else name[:20] + "…"
        parts.append(
            f'<g><title>vnum {vnum}\n{name}\n\n{desc}</title>'
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="8" ry="8" fill="{fill}" stroke="{border}" stroke-width="2" />'
            f'<text x="{x+CELL/2}" y="{y+18}" text-anchor="middle" '
            f'fill="#8aa0c2" font-size="11">vnum {vnum}</text>'
            f'<text x="{x+CELL/2}" y="{y+CELL/2+2}" text-anchor="middle" '
            f'fill="#d9dce6" font-size="12" font-weight="600">{short_name}</text>'
        )
        off = off_grid.get(vnum, [])
        if off:
            label = " ".join(f"{d}→{t}" for d, t in off[:3])
            parts.append(
                f'<text x="{x+CELL/2}" y="{y+CELL-8}" text-anchor="middle" '
                f'fill="#6a84a8" font-size="10">{label}</text>'
            )
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def _render_area_html(area_name: str, rooms_by_vnum: dict) -> str:
    positions, off_grid, orphans, warped = _layout(rooms_by_vnum)
    edges = _collect_edges(rooms_by_vnum, positions)
    svg = _svg(rooms_by_vnum, positions, off_grid, edges, area_name, warped_edges=warped)
    n_rooms = len(rooms_by_vnum)
    n_edges = len(edges)
    n_off = sum(len(v) for v in off_grid.values())
    n_orph = len(orphans)
    n_warped = len(warped)
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>{area_name} — OrekaMUD3 Area Map</title>
<style>
 body {{ background:#0b0d12; color:#d9dce6; font-family: system-ui, sans-serif; margin: 0; padding: 24px; }}
 header {{ margin-bottom: 16px; }}
 h1 {{ font-weight: 500; margin: 0 0 4px 0; }}
 .meta {{ color:#8593a8; font-size: 13px; }}
 a {{ color:#6cb38f; }}
 .map-wrap {{ overflow: auto; border:1px solid #2a3141; border-radius:8px; background:#0f1117; }}
 .legend span {{ margin-right: 14px; }}
 .warp {{ color:#d88080; }}
</style></head><body>
<header>
  <h1>{area_name}</h1>
  <div class="meta">{n_rooms} rooms · {n_edges} grid edges · {n_off} off-grid exits · {n_orph} orphans · <span class="warp">{n_warped} warped edges</span> ·
  <a href="../index.html">← back to map index</a></div>
  <div class="meta legend">
    <span>Hover a room for description.</span>
    <span>Border: <span style="color:#6cb38f;">green=safe/temple</span>, <span style="color:#c79a5e;">gold=shop/street</span></span>
    <span class="warp">red dashed edges = asymmetric or collision-shoved (map distortion)</span>
  </div>
</header>
<div class="map-wrap">{svg}</div>
</body></html>
"""


def _compute_interarea_graph(files: list):
    """Scan every area file; return:
       area_rooms[name] = {vnum: room}
       vnum_to_area[vnum] = area_name
       edges: {(A,B): count}  sorted canonically (A<B)
       directions: {(A,B): (unit_dx, unit_dy)} pointing from A to B in compass terms
    """
    area_rooms = {}
    vnum_to_area = {}
    for fname in files:
        name = os.path.splitext(fname)[0]
        try:
            rooms = _load_area(os.path.join(AREAS_DIR, fname))
        except Exception:
            continue
        area_rooms[name] = rooms
        for v in rooms:
            vnum_to_area[v] = name
    from collections import Counter
    edges = Counter()
    # directional accumulators per ordered pair A→B
    dir_acc = {}
    for name, rooms in area_rooms.items():
        for vnum, room in rooms.items():
            for dname, target in (room.get("exits") or {}).items():
                try:
                    tvnum = int(target)
                except (TypeError, ValueError):
                    continue
                other = vnum_to_area.get(tvnum)
                if not other or other == name:
                    continue
                a, b = sorted([name, other])
                edges[(a, b)] += 1
                dkey = dname.lower()
                if dkey in GRID_DIRS:
                    dx, dy = GRID_DIRS[dkey]
                    # orient the vector A→B (positive y down in screen coords)
                    if name == a:
                        dir_acc.setdefault((a, b), [0.0, 0.0])
                        dir_acc[(a, b)][0] += dx
                        dir_acc[(a, b)][1] += dy
                    else:
                        dir_acc.setdefault((a, b), [0.0, 0.0])
                        dir_acc[(a, b)][0] -= dx
                        dir_acc[(a, b)][1] -= dy
    # normalize to unit vectors; fall back to (0,0) when no directional data (e.g., only "in"/"out")
    directions = {}
    for pair, (sx, sy) in dir_acc.items():
        mag = (sx * sx + sy * sy) ** 0.5
        if mag < 1e-6:
            directions[pair] = (0.0, 0.0)
        else:
            directions[pair] = (sx / mag, sy / mag)
    return area_rooms, edges, directions


def _directional_layout(nodes: list, edges: dict, directions: dict,
                        w: int = 980, h: int = 660,
                        hub_areas: set = None) -> dict:
    """BFS layout that respects compass directions of inter-area exits.

    Pick a hub area (one that contains a temple/altar room) as the root
    and center it. If multiple candidates, the most-connected wins.
    Falls back to the most-connected overall if no hub area.

    Place each BFS neighbor offset from its parent by the (A→B) unit
    vector scaled by STEP pixels. Collisions push outward along the
    same axis. Isolated nodes go in a bottom row.
    """
    from collections import deque
    if not nodes:
        return {}
    hub_areas = hub_areas or set()
    STEP = 240  # px between adjacent area centers

    # degree for root pick
    deg = {n: 0 for n in nodes}
    for (a, b), c in edges.items():
        deg[a] = deg.get(a, 0) + c
        deg[b] = deg.get(b, 0) + c
    # Prefer hub areas as root
    connected = sorted([n for n in nodes if deg.get(n, 0) > 0],
                       key=lambda n: (0 if n in hub_areas else 1, -deg[n]))
    isolated = [n for n in nodes if deg.get(n, 0) == 0]

    # adjacency: neighbor → direction (A→B) scaled vector
    adj = {n: [] for n in nodes}
    for (a, b) in edges:
        dvec = directions.get((a, b), (0.0, 0.0))
        # if no direction data (only non-grid exits), use a weak default
        if dvec == (0.0, 0.0):
            dvec = (0.6, 0.2)  # slight east-south; caller may collide anyway
        adj[a].append((b, dvec[0], dvec[1]))
        adj[b].append((a, -dvec[0], -dvec[1]))

    pos = {}
    taken_cells = set()  # cells on a coarse grid, for collision check
    cell_size = STEP * 0.8

    def cell_of(x, y):
        return (round(x / cell_size), round(y / cell_size))

    def place(node, x, y):
        # shove outward if cell taken
        tries = 0
        while cell_of(x, y) in taken_cells and tries < 8:
            x += cell_size * 0.55
            y += cell_size * 0.45
            tries += 1
        pos[node] = (x, y)
        taken_cells.add(cell_of(x, y))

    cx, cy = w / 2, h / 2
    if connected:
        root = connected[0]
        place(root, cx, cy)
        queue = deque([root])
        while queue:
            cur = queue.popleft()
            for neigh, dx, dy in adj[cur]:
                if neigh in pos:
                    continue
                px, py = pos[cur]
                place(neigh, px + dx * STEP, py + dy * STEP)
                queue.append(neigh)
    # isolated nodes: arrange in a row at bottom
    if isolated:
        for i, n in enumerate(isolated):
            place(n, 100 + i * 180, h - 80)

    # center and clamp
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    if xs:
        dx_shift = cx - (min(xs) + max(xs)) / 2
        dy_shift = cy - (min(ys) + max(ys)) / 2
        pos = {n: (x + dx_shift, y + dy_shift) for n, (x, y) in pos.items()}
    # clamp inside canvas with padding
    pad = 90
    for n, (x, y) in list(pos.items()):
        pos[n] = (max(pad, min(w - pad, x)), max(pad, min(h - pad, y)))
    return pos


def _force_layout(nodes: list, edges: dict, iterations: int = 160, w: int = 900, h: int = 620):
    """Simple force-directed layout. Returns {node: (x, y)}."""
    import math, random
    random.seed(42)
    pos = {n: (random.uniform(0, w), random.uniform(0, h)) for n in nodes}
    # initial ring seed for stability
    import math as _m
    for i, n in enumerate(sorted(nodes)):
        ang = (i / max(1, len(nodes))) * 2 * _m.pi
        pos[n] = (w / 2 + _m.cos(ang) * w * 0.32, h / 2 + _m.sin(ang) * h * 0.32)
    # node degree for repulsion scaling
    degree = {n: 1 for n in nodes}
    for (a, b), c in edges.items():
        degree[a] = degree.get(a, 1) + 1
        degree[b] = degree.get(b, 1) + 1
    ideal = (w * h / max(1, len(nodes))) ** 0.5 * 0.6
    for it in range(iterations):
        disp = {n: [0.0, 0.0] for n in nodes}
        # repulsion
        arr = list(pos.items())
        for i in range(len(arr)):
            n1, (x1, y1) = arr[i]
            for j in range(i + 1, len(arr)):
                n2, (x2, y2) = arr[j]
                dx, dy = x1 - x2, y1 - y2
                d2 = dx * dx + dy * dy + 0.01
                d = d2 ** 0.5
                force = (ideal * ideal) / d
                ux, uy = dx / d, dy / d
                disp[n1][0] += ux * force
                disp[n1][1] += uy * force
                disp[n2][0] -= ux * force
                disp[n2][1] -= uy * force
        # attraction along edges, weight by log(count+1)
        import math
        for (a, b), c in edges.items():
            if a not in pos or b not in pos:
                continue
            xa, ya = pos[a]; xb, yb = pos[b]
            dx, dy = xa - xb, ya - yb
            d = (dx * dx + dy * dy) ** 0.5 + 0.01
            weight = math.log(c + 1)
            force = (d * d) / ideal * weight
            ux, uy = dx / d, dy / d
            disp[a][0] -= ux * force
            disp[a][1] -= uy * force
            disp[b][0] += ux * force
            disp[b][1] += uy * force
        # step
        temp = max(2.0, 40.0 * (1 - it / iterations))
        for n, (x, y) in pos.items():
            dx, dy = disp[n]
            mag = (dx * dx + dy * dy) ** 0.5 + 0.01
            mv = min(mag, temp)
            x2 = x + (dx / mag) * mv
            y2 = y + (dy / mag) * mv
            # keep within canvas with padding
            pad = 80
            x2 = max(pad, min(w - pad, x2))
            y2 = max(pad, min(h - pad, y2))
            pos[n] = (x2, y2)
    return pos


def _render_index(index_rows: list, area_rooms: dict, edges: dict,
                  directions: dict) -> str:
    nodes = [name for (name, _n) in index_rows]
    W, H = 980, 660
    # Areas that contain a temple/altar-flagged room are preferred hubs
    hub_areas = set()
    for name, rooms in area_rooms.items():
        for r in rooms.values():
            flags = set(r.get("flags") or [])
            if flags & {"altar", "temple", "hub"}:
                hub_areas.add(name)
                break
    pos = _directional_layout(nodes, edges, directions, W, H, hub_areas=hub_areas)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" style="background:#0f1117;border-radius:8px;">']
    # draw edges first, thickness by count
    import math
    max_c = max(edges.values()) if edges else 1
    for (a, b), c in sorted(edges.items()):
        if a not in pos or b not in pos:
            continue
        xa, ya = pos[a]; xb, yb = pos[b]
        width = 1 + math.log(c + 1) * 1.4
        stroke = "#3e4a63"
        svg.append(
            f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" '
            f'stroke="{stroke}" stroke-width="{width:.1f}" opacity="0.75"/>'
        )
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        svg.append(
            f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" '
            f'fill="#6a84a8" font-size="10" font-family="system-ui">{c}</text>'
        )
    # room count lookup
    count_map = dict(index_rows)
    # draw nodes
    for name, (x, y) in sorted(pos.items()):
        n_rooms = count_map.get(name, 0)
        # size by sqrt(rooms) so small areas don't get lost
        r = 28 + (n_rooms ** 0.5) * 2
        short = name
        if len(short) > 18:
            short = short[:17] + "…"
        svg.append(
            f'<g style="cursor:pointer" onclick="window.location.href=\'areas/{name}.html\'">'
            f'<title>{name} — {n_rooms} rooms</title>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#1a1f2e" '
            f'stroke="#6cb38f" stroke-width="2"/>'
            f'<text x="{x:.1f}" y="{y-4:.1f}" text-anchor="middle" '
            f'fill="#d9dce6" font-size="12" font-weight="600" font-family="system-ui">{short}</text>'
            f'<text x="{x:.1f}" y="{y+12:.1f}" text-anchor="middle" '
            f'fill="#8aa0c2" font-size="10" font-family="system-ui">{n_rooms} rooms</text>'
            f'</g>'
        )
    svg.append('</svg>')
    svg_str = "\n".join(svg)

    rows_html = "\n".join(
        f'<li><a href="areas/{name}.html">{name}</a> <span class="count">· {n} rooms</span></li>'
        for name, n in index_rows
    )

    n_edges = len(edges)
    total_crosslinks = sum(edges.values())

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>OrekaMUD3 Area Maps</title>
<style>
 body {{ background:#0b0d12; color:#d9dce6; font-family: system-ui, sans-serif; margin: 0; padding: 32px; max-width: 1100px; }}
 h1 {{ font-weight: 500; margin: 0 0 4px 0; }}
 h2 {{ font-weight: 500; font-size: 16px; color:#8593a8; margin: 24px 0 8px 0; }}
 .hint {{ color:#6a84a8; font-size: 13px; margin-bottom: 16px; }}
 ul {{ list-style: none; padding: 0; column-count: 2; column-gap: 24px; }}
 li {{ padding: 4px 0; font-size: 14px; break-inside: avoid; }}
 a {{ color:#6cb38f; text-decoration: none; }}
 a:hover {{ text-decoration: underline; }}
 .count {{ color:#6a84a8; font-size: 13px; }}
 .graph-wrap {{ border:1px solid #2a3141; border-radius:8px; }}
</style></head><body>
<h1>OrekaMUD3 Area Maps</h1>
<p class="hint">{len(index_rows)} areas · {n_edges} inter-area links · {total_crosslinks} cross-area exits total. Click a node to open its map. Line thickness and the number on each line = number of cross-area exits.</p>
<div class="graph-wrap">{svg_str}</div>
<h2>All areas (alphabetical)</h2>
<ul>
{rows_html}
</ul>
</body></html>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    index_rows = []
    files = sorted(f for f in os.listdir(AREAS_DIR)
                   if f.endswith(".json") and ".rest_bak." not in f
                   and ".bak" not in f)
    for fname in files:
        area_name = os.path.splitext(fname)[0]
        try:
            rooms = _load_area(os.path.join(AREAS_DIR, fname))
        except Exception as e:
            print(f"SKIP {fname}: {e}")
            continue
        html = _render_area_html(area_name, rooms)
        out_path = os.path.join(OUT_DIR, f"{area_name}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        index_rows.append((area_name, len(rooms)))
        print(f"wrote {out_path}  ({len(rooms)} rooms)")

    # Build the inter-area connection graph and render a visual index
    area_rooms, edges, directions = _compute_interarea_graph(files)
    html = _render_index(index_rows, area_rooms, edges, directions)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nwrote index: {INDEX_PATH}")
    print(f"Total areas: {len(index_rows)}  inter-area edges: {len(edges)}  "
          f"cross-area exit count: {sum(edges.values())}")


if __name__ == "__main__":
    main()
