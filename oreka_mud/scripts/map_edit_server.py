"""
Map Edit Server — local HTTP backend for maps/editor.html.

Runs on 127.0.0.1:8401 only (no remote access). Exposes CRUD for area
JSONs and per-area layout-position overrides. Every write to a canonical
area file creates a timestamped .mapedit_bak.<ts> backup first and
preserves the most recent 10.

Endpoints:
  GET  /api/areas                                — list all areas
  GET  /api/areas/<name>                         — full area JSON + layout overrides
  POST /api/areas/<name>/layout                  — save per-room positions
  POST /api/areas/<name>/room                    — create new room (auto-vnum)
  PATCH /api/areas/<name>/room/<vnum>            — update room fields (name/description/flags)
  DELETE /api/areas/<name>/room/<vnum>           — delete room + strip dangling exits
  PUT  /api/areas/<name>/room/<vnum>/exit        — upsert exit (dir, target_vnum)
  DELETE /api/areas/<name>/room/<vnum>/exit/<dir> — remove exit
  POST /api/areas/<name>/rebuild                 — regenerate map HTML for one area
  POST /api/areas/rebuild_all                    — regenerate index + all area maps

Run:  python scripts/map_edit_server.py
"""

import json
import os
import sys
import re
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
AREAS_DIR = os.path.normpath(os.path.join(HERE, "..", "data", "areas"))
LAYOUTS_DIR = os.path.normpath(os.path.join(HERE, "..", "data", "area_layouts"))

PORT = 8401
BACKUPS_TO_KEEP = 10

_LOCK = threading.Lock()


def _ensure_dirs():
    os.makedirs(LAYOUTS_DIR, exist_ok=True)


def _list_areas():
    files = sorted(f for f in os.listdir(AREAS_DIR)
                   if f.endswith(".json") and ".bak" not in f)
    out = []
    for fn in files:
        name = os.path.splitext(fn)[0]
        try:
            d = json.load(open(os.path.join(AREAS_DIR, fn), encoding="utf-8"))
            rooms = d if isinstance(d, list) else d.get("rooms", [])
            out.append({"name": name, "room_count": len(rooms)})
        except Exception:
            continue
    return out


def _load_area(name):
    path = os.path.join(AREAS_DIR, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _backup_and_save_area(name, data):
    path = os.path.join(AREAS_DIR, f"{name}.json")
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup = f"{path}.mapedit_bak.{ts}"
    if os.path.exists(path):
        import shutil
        shutil.copy2(path, backup)
        # prune old backups
        pattern = re.compile(rf"^{re.escape(name)}\.json\.mapedit_bak\.")
        backups = sorted(
            (os.path.join(AREAS_DIR, f) for f in os.listdir(AREAS_DIR) if pattern.match(f)),
            key=os.path.getmtime,
        )
        for old in backups[:-BACKUPS_TO_KEEP]:
            try:
                os.remove(old)
            except Exception:
                pass
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _load_layout(name):
    path = os.path.join(LAYOUTS_DIR, f"{name}.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_layout(name, data):
    _ensure_dirs()
    path = os.path.join(LAYOUTS_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _rooms_list(data):
    return data if isinstance(data, list) else data.get("rooms", [])


def _as_list(data):
    """Normalize to the list-of-rooms shape used by the area files on disk."""
    return data if isinstance(data, list) else data.get("rooms", [])


def _find_room(rooms, vnum):
    for i, r in enumerate(rooms):
        if r.get("vnum") == vnum:
            return i, r
    return None, None


def _next_vnum(name, rooms):
    # Find next free integer in the area's observed range.
    if not rooms:
        return 1000
    vnums = sorted(r.get("vnum", 0) for r in rooms if r.get("vnum") is not None)
    lo, hi = vnums[0], vnums[-1]
    taken = set(vnums)
    for v in range(lo, hi + 200):
        if v not in taken:
            return v
    return hi + 1


# ----- Handlers ----------------------------------------------------------

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[map_edit] {self.address_string()} - {fmt % args}\n")

    def _json(self, status, body):
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self._json(200, {"ok": True})

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def _route(self):
        path = urlparse(self.path).path.strip("/")
        parts = path.split("/")
        return parts

    def do_GET(self):
        parts = self._route()
        try:
            if parts == ["api", "areas"]:
                return self._json(200, {"areas": _list_areas()})
            if len(parts) == 3 and parts[:2] == ["api", "areas"]:
                name = parts[2]
                data = _load_area(name)
                if data is None:
                    return self._json(404, {"error": f"area {name} not found"})
                layout = _load_layout(name)
                return self._json(200, {"name": name, "rooms": _rooms_list(data), "layout": layout})
            return self._json(404, {"error": "unknown route"})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def do_POST(self):
        parts = self._route()
        try:
            body = self._read_body()
            if len(parts) == 4 and parts[:2] == ["api", "areas"] and parts[3] == "layout":
                name = parts[2]
                with _LOCK:
                    current = _load_layout(name)
                    current.update(body.get("positions", {}))
                    _save_layout(name, current)
                return self._json(200, {"ok": True, "saved": len(current)})

            if len(parts) == 4 and parts[:2] == ["api", "areas"] and parts[3] == "room":
                name = parts[2]
                with _LOCK:
                    data = _load_area(name)
                    if data is None:
                        return self._json(404, {"error": f"area {name} not found"})
                    rooms = _as_list(data)
                    new_vnum = body.get("vnum") or _next_vnum(name, rooms)
                    if any(r.get("vnum") == new_vnum for r in rooms):
                        return self._json(409, {"error": f"vnum {new_vnum} already exists"})
                    new_room = {
                        "vnum": new_vnum,
                        "name": body.get("name") or "Unnamed Room",
                        "description": body.get("description") or "",
                        "exits": body.get("exits") or {},
                        "flags": body.get("flags") or [],
                    }
                    rooms.append(new_room)
                    if isinstance(data, dict):
                        data["rooms"] = rooms
                    _backup_and_save_area(name, rooms if isinstance(_load_area(name), list) else data)
                return self._json(201, {"ok": True, "room": new_room})

            if len(parts) == 4 and parts[:2] == ["api", "areas"] and parts[3] == "rebuild":
                name = parts[2]
                import subprocess
                r = subprocess.run([sys.executable, os.path.join(HERE, "build_area_maps.py")],
                                   cwd=os.path.join(HERE, ".."), capture_output=True, text=True, timeout=60)
                return self._json(200, {"ok": r.returncode == 0,
                                        "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]})

            if parts == ["api", "areas", "rebuild_all"]:
                import subprocess
                r = subprocess.run([sys.executable, os.path.join(HERE, "build_area_maps.py")],
                                   cwd=os.path.join(HERE, ".."), capture_output=True, text=True, timeout=120)
                return self._json(200, {"ok": r.returncode == 0,
                                        "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]})

            return self._json(404, {"error": "unknown route"})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def do_PATCH(self):
        parts = self._route()
        try:
            body = self._read_body()
            # /api/areas/<name>/room/<vnum>
            if len(parts) == 5 and parts[:2] == ["api", "areas"] and parts[3] == "room":
                name = parts[2]; vnum = int(parts[4])
                with _LOCK:
                    data = _load_area(name)
                    if data is None:
                        return self._json(404, {"error": f"area {name} not found"})
                    rooms = _as_list(data)
                    idx, room = _find_room(rooms, vnum)
                    if room is None:
                        return self._json(404, {"error": f"room {vnum} not found"})
                    for field in ("name", "description"):
                        if field in body:
                            room[field] = body[field]
                    if "flags" in body:
                        room["flags"] = list(body["flags"])
                    rooms[idx] = room
                    if isinstance(data, dict):
                        data["rooms"] = rooms
                    _backup_and_save_area(name, rooms if isinstance(_load_area(name), list) else data)
                return self._json(200, {"ok": True, "room": room})
            return self._json(404, {"error": "unknown route"})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def do_PUT(self):
        parts = self._route()
        try:
            body = self._read_body()
            # /api/areas/<name>/room/<vnum>/exit
            if len(parts) == 6 and parts[:2] == ["api", "areas"] and parts[3] == "room" and parts[5] == "exit":
                name = parts[2]; vnum = int(parts[4])
                direction = str(body.get("direction", "")).lower()
                target = body.get("target")
                if not direction or target is None:
                    return self._json(400, {"error": "direction and target required"})
                with _LOCK:
                    data = _load_area(name)
                    if data is None:
                        return self._json(404, {"error": f"area {name} not found"})
                    rooms = _as_list(data)
                    idx, room = _find_room(rooms, vnum)
                    if room is None:
                        return self._json(404, {"error": f"room {vnum} not found"})
                    exits = room.get("exits") or {}
                    exits[direction] = int(target)
                    room["exits"] = exits
                    rooms[idx] = room
                    if isinstance(data, dict):
                        data["rooms"] = rooms
                    _backup_and_save_area(name, rooms if isinstance(_load_area(name), list) else data)
                return self._json(200, {"ok": True, "exit": {direction: int(target)}})
            return self._json(404, {"error": "unknown route"})
        except Exception as e:
            return self._json(500, {"error": str(e)})

    def do_DELETE(self):
        parts = self._route()
        try:
            # /api/areas/<name>/room/<vnum>
            if len(parts) == 5 and parts[:2] == ["api", "areas"] and parts[3] == "room":
                name = parts[2]; vnum = int(parts[4])
                with _LOCK:
                    data = _load_area(name)
                    if data is None:
                        return self._json(404, {"error": f"area {name} not found"})
                    rooms = _as_list(data)
                    rooms = [r for r in rooms if r.get("vnum") != vnum]
                    # strip dangling exits in this area (exits to this vnum elsewhere stay; editor can detect)
                    for r in rooms:
                        r["exits"] = {d: t for d, t in (r.get("exits") or {}).items() if t != vnum}
                    if isinstance(data, dict):
                        data["rooms"] = rooms
                    _backup_and_save_area(name, rooms if isinstance(_load_area(name), list) else data)
                return self._json(200, {"ok": True, "deleted": vnum})

            # /api/areas/<name>/room/<vnum>/exit/<direction>
            if len(parts) == 7 and parts[:2] == ["api", "areas"] and parts[3] == "room" and parts[5] == "exit":
                name = parts[2]; vnum = int(parts[4]); direction = parts[6].lower()
                with _LOCK:
                    data = _load_area(name)
                    if data is None:
                        return self._json(404, {"error": f"area {name} not found"})
                    rooms = _as_list(data)
                    idx, room = _find_room(rooms, vnum)
                    if room is None:
                        return self._json(404, {"error": f"room {vnum} not found"})
                    exits = room.get("exits") or {}
                    exits.pop(direction, None)
                    room["exits"] = exits
                    rooms[idx] = room
                    if isinstance(data, dict):
                        data["rooms"] = rooms
                    _backup_and_save_area(name, rooms if isinstance(_load_area(name), list) else data)
                return self._json(200, {"ok": True, "removed": direction})
            return self._json(404, {"error": "unknown route"})
        except Exception as e:
            return self._json(500, {"error": str(e)})


def main():
    _ensure_dirs()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Map Edit Server listening on http://127.0.0.1:{PORT}")
    print(f"Areas dir: {AREAS_DIR}")
    print(f"Layouts dir: {LAYOUTS_DIR}")
    print("Open maps/editor.html in a browser. Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")


if __name__ == "__main__":
    main()
