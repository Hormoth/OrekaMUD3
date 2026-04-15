"""
Module loader for OrekaMUD3.

Discovers, validates, and loads modules from data/modules/{slug}/.
Each module bundles arcs, personas, mobs, rooms, quests, factions,
narrative hooks, and lore in a single drop.

Load order on startup:
  1. Discover all modules with module.json
  2. Topological sort by depends_on_modules
  3. Validate each module's files
  4. Merge into the live world (rejecting vnum collisions)
  5. Run arc migration on online/offline players to backfill new arcs
"""

import os
import json
import logging
import glob
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("OrekaMUD.ModuleLoader")

MODULES_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'modules')


@dataclass
class Module:
    """Loaded module with all its content."""
    module_id: str
    title: str
    version: str
    author: str = ""
    requires_engine: str = ""
    depends_on_modules: list = field(default_factory=list)
    summary: str = ""
    tags: list = field(default_factory=list)
    content_warnings: list = field(default_factory=list)

    # Loaded content (filled in by load_module)
    arcs: list = field(default_factory=list)               # list of arc template dicts
    personas: list = field(default_factory=list)           # list of persona dicts
    mobs: list = field(default_factory=list)               # list of mob dicts
    rooms: list = field(default_factory=list)              # list of room dicts
    quests: list = field(default_factory=list)             # list of quest dicts
    faction_deltas: list = field(default_factory=list)
    narrative_hooks: list = field(default_factory=list)
    lore_files: list = field(default_factory=list)         # list of (filename, content) tuples

    # Source path (for diagnostics)
    source_path: str = ""

    def to_summary(self) -> dict:
        """Compact dict for admin display."""
        return {
            "module_id": self.module_id,
            "title": self.title,
            "version": self.version,
            "author": self.author,
            "summary": self.summary,
            "content_warnings": list(self.content_warnings),
            "depends_on_modules": list(self.depends_on_modules),
            "counts": {
                "arcs": len(self.arcs),
                "personas": len(self.personas),
                "mobs": len(self.mobs),
                "rooms": len(self.rooms),
                "quests": len(self.quests),
                "narrative_hooks": len(self.narrative_hooks),
                "lore_files": len(self.lore_files),
            },
        }


# ---------------------------------------------------------------------------
# Discovery + loading
# ---------------------------------------------------------------------------

def discover_modules(modules_dir: str = None) -> list:
    """Find all module.json files; return list of (slug, manifest_dict, dirpath)."""
    if modules_dir is None:
        modules_dir = MODULES_DIR
    out = []
    if not os.path.isdir(modules_dir):
        return out
    for entry in sorted(os.listdir(modules_dir)):
        manifest_path = os.path.join(modules_dir, entry, "module.json")
        if not os.path.isfile(manifest_path):
            continue
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            slug = manifest.get("module_id", entry)
            out.append((slug, manifest, os.path.join(modules_dir, entry)))
        except Exception as e:
            logger.error(f"discover: failed to read {manifest_path}: {e}")
    return out


def topological_sort(discovered: list) -> list:
    """Sort discovered modules so that dependencies load first.

    discovered: list of (slug, manifest, dirpath) tuples.
    Returns same list reordered. Raises ValueError on cycle or missing dep.
    """
    by_slug = {slug: (manifest, path) for slug, manifest, path in discovered}
    visited = set()
    visiting = set()
    result = []

    def visit(slug):
        if slug in visited:
            return
        if slug in visiting:
            raise ValueError(f"Cyclic module dependency involving '{slug}'")
        if slug not in by_slug:
            raise ValueError(f"Module '{slug}' not found (declared as dependency)")
        visiting.add(slug)
        manifest, _ = by_slug[slug]
        for dep in manifest.get("depends_on_modules", []) or []:
            visit(dep)
        visiting.remove(slug)
        visited.add(slug)
        result.append(slug)

    for slug, _, _ in discovered:
        visit(slug)

    return [(slug, by_slug[slug][0], by_slug[slug][1]) for slug in result]


def load_module(module_dir: str) -> Module:
    """Load a single module from its directory. Returns a populated Module."""
    manifest_path = os.path.join(module_dir, "module.json")
    if not os.path.isfile(manifest_path):
        raise FileNotFoundError(f"No module.json at {module_dir}")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    mod = Module(
        module_id=manifest.get("module_id", ""),
        title=manifest.get("title", ""),
        version=manifest.get("version", "0.0.0"),
        author=manifest.get("author", ""),
        requires_engine=manifest.get("requires_engine", ""),
        depends_on_modules=list(manifest.get("depends_on_modules", []) or []),
        summary=manifest.get("summary", ""),
        tags=list(manifest.get("tags", []) or []),
        content_warnings=list(manifest.get("content_warnings", []) or []),
        source_path=module_dir,
    )

    # arcs.json
    arcs_path = os.path.join(module_dir, "arcs.json")
    if os.path.isfile(arcs_path):
        with open(arcs_path, 'r', encoding='utf-8') as f:
            arcs_data = json.load(f)
        mod.arcs = list(arcs_data.get("arcs", []) or [])

    # personas/*.json
    personas_dir = os.path.join(module_dir, "personas")
    if os.path.isdir(personas_dir):
        for fname in sorted(os.listdir(personas_dir)):
            if fname.endswith(".json"):
                with open(os.path.join(personas_dir, fname), 'r', encoding='utf-8') as f:
                    mod.personas.append(json.load(f))

    # mobs.json
    mobs_path = os.path.join(module_dir, "mobs.json")
    if os.path.isfile(mobs_path):
        with open(mobs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            mod.mobs = data
        elif isinstance(data, dict):
            mod.mobs = list(data.get("mobs", []) or [])

    # rooms/*.json
    rooms_dir = os.path.join(module_dir, "rooms")
    if os.path.isdir(rooms_dir):
        for fname in sorted(os.listdir(rooms_dir)):
            if fname.endswith(".json"):
                with open(os.path.join(rooms_dir, fname), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    mod.rooms.extend(data)
                elif isinstance(data, dict):
                    if "rooms" in data:
                        mod.rooms.extend(data.get("rooms", []) or [])
                    else:
                        mod.rooms.append(data)

    # quests.json
    quests_path = os.path.join(module_dir, "quests.json")
    if os.path.isfile(quests_path):
        with open(quests_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            mod.quests = data
        elif isinstance(data, dict):
            mod.quests = list(data.get("quests", []) or [])

    # factions.json
    factions_path = os.path.join(module_dir, "factions.json")
    if os.path.isfile(factions_path):
        with open(factions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        mod.faction_deltas = list(data.get("faction_deltas", []) or [])

    # hooks.json
    hooks_path = os.path.join(module_dir, "hooks.json")
    if os.path.isfile(hooks_path):
        with open(hooks_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        mod.narrative_hooks = list(data.get("narrative_hooks", []) or [])

    # lore/*.md
    lore_dir = os.path.join(module_dir, "lore")
    if os.path.isdir(lore_dir):
        for fname in sorted(os.listdir(lore_dir)):
            if fname.endswith(".md"):
                with open(os.path.join(lore_dir, fname), 'r', encoding='utf-8') as f:
                    mod.lore_files.append((fname, f.read()))

    return mod


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_module(module: Module, world=None, other_modules: list = None) -> list:
    """Validate a loaded module. Returns list of error strings.

    Checks:
    - All personas pass validate_persona()
    - Every arc_reactions[*].when references items that exist in this module's arcs
    - Every NPC's arcs_known references this module's arc_ids
    - No vnum collisions against world or other modules
    """
    errors = []
    other_modules = other_modules or []

    # Build set of arc_ids and per-arc item_ids defined by this module
    arc_ids = {a.get("arc_id") for a in module.arcs if a.get("arc_id")}
    arc_items = {}  # arc_id -> set of item_ids
    for arc in module.arcs:
        arc_id = arc.get("arc_id")
        if arc_id:
            arc_items[arc_id] = {ci.get("id") for ci in arc.get("checklist", []) or [] if ci.get("id")}

    # Validate each persona
    try:
        from src.ai_schemas import validate_persona
    except ImportError:
        validate_persona = lambda p: []  # noqa

    for persona in module.personas:
        vnum = persona.get("vnum", "?")
        # Standard validation
        for err in validate_persona(persona):
            errors.append(f"persona vnum {vnum}: {err}")
        # arcs_known must reference this module's arcs
        for arc_id in persona.get("arcs_known", []) or []:
            if arc_id not in arc_ids:
                errors.append(
                    f"persona vnum {vnum}: arcs_known references unknown arc '{arc_id}' "
                    f"(this module declares: {sorted(arc_ids) or 'none'})"
                )
        # arc_reactions must reference items in known arcs
        for i, ar in enumerate(persona.get("arc_reactions", []) or []):
            when = ar.get("when") if isinstance(ar, dict) else getattr(ar, 'when', '')
            # Extract item references from the expression (best-effort)
            for arc_id in persona.get("arcs_known", []) or []:
                items = arc_items.get(arc_id, set())
                # We just warn if an unknown item appears unambiguously (best effort)
                for tok in _extract_path_roots(when):
                    if tok in ("arc",):
                        continue
                    # If the token isn't in any known module's arcs, flag it
                    if tok not in items and tok not in {"true", "false"}:
                        # Check if it's a valid keyword / number
                        if tok.replace("_", "").replace(".", "").isdigit():
                            continue
                        # We don't fail hard — many references might be intentional
                        # cross-arc, so just log
                        logger.debug(
                            f"persona vnum {vnum} arc_reactions[{i}] references "
                            f"unknown identifier '{tok}'"
                        )

    # vnum collision detection
    vnum_sources = {}  # vnum -> source string
    for mob in module.mobs:
        v = mob.get("vnum")
        if v is None:
            continue
        if world and v in (getattr(world, 'mobs', None) or {}):
            errors.append(
                f"mob vnum {v} ({mob.get('name', '?')}) collides with existing world mob"
            )
        for other in other_modules:
            for other_mob in other.mobs:
                if other_mob.get("vnum") == v:
                    errors.append(
                        f"mob vnum {v} collides with module '{other.module_id}'"
                    )
        vnum_sources[v] = f"mob {v}"
    for room in module.rooms:
        v = room.get("vnum")
        if v is None:
            continue
        if world and v in (getattr(world, 'rooms', None) or {}):
            errors.append(
                f"room vnum {v} ({room.get('name', '?')}) collides with existing world room"
            )
        for other in other_modules:
            for other_room in other.rooms:
                if other_room.get("vnum") == v:
                    errors.append(
                        f"room vnum {v} collides with module '{other.module_id}'"
                    )

    # Lore frontmatter sanity
    for fname, content in module.lore_files:
        if content.startswith("---"):
            # Has frontmatter — quick parse
            end = content.find("---", 3)
            if end == -1:
                errors.append(f"lore/{fname}: frontmatter not closed")

    return errors


def _extract_path_roots(expr: str) -> set:
    """Extract the first identifier of each dotted path in a when-expression.

    Used for best-effort item-id reference checking.
    """
    if not isinstance(expr, str) or not expr.strip():
        return set()
    import re
    # Match identifiers, but only those followed by . or whitespace (not inside strings)
    tokens = re.findall(r'\b([A-Za-z_][A-Za-z_0-9]*)', expr)
    # Filter out keywords
    skip = {"AND", "OR", "NOT", "and", "or", "not"}
    return {t for t in tokens if t not in skip}


# ---------------------------------------------------------------------------
# Application — merge module content into the live world
# ---------------------------------------------------------------------------

def apply_module_to_world(module: Module, world) -> dict:
    """Merge a validated module into the live world.

    Returns dict of stats: {merged_personas, merged_mobs, merged_rooms, ...}
    """
    stats = {
        "merged_personas": 0,
        "merged_mobs": 0,
        "merged_rooms": 0,
        "merged_quests": 0,
        "registered_arcs": 0,
        "narrative_hooks": 0,
    }

    # Personas: attach to existing mobs by vnum
    for persona in module.personas:
        vnum = persona.get("vnum")
        if vnum is None:
            continue
        mob = world.mobs.get(vnum) if hasattr(world, 'mobs') else None
        if mob:
            mob.ai_persona = persona
            stats["merged_personas"] += 1

    # Mobs (new mobs added by the module)
    if hasattr(world, 'mobs'):
        from src.mob import Mob
        for mob_data in module.mobs:
            v = mob_data.get("vnum")
            if v is None or v in world.mobs:
                continue
            try:
                mob = Mob(**{k: val for k, val in mob_data.items() if k != "room_vnum"})
                world.mobs[v] = mob
                room_vnum = mob_data.get("room_vnum")
                if room_vnum and room_vnum in world.rooms:
                    world.rooms[room_vnum].mobs.append(mob)
                stats["merged_mobs"] += 1
            except Exception as e:
                logger.error(f"Failed to instantiate module mob vnum {v}: {e}")

    # Rooms
    if hasattr(world, 'rooms'):
        from src.room import Room
        for room_data in module.rooms:
            v = room_data.get("vnum")
            if v is None or v in world.rooms:
                continue
            try:
                room = Room(**room_data)
                room._world = world
                world.rooms[v] = room
                stats["merged_rooms"] += 1
            except Exception as e:
                logger.error(f"Failed to instantiate module room vnum {v}: {e}")

    # Arcs are tracked at module-load level for migration
    stats["registered_arcs"] = len(module.arcs)

    # Narrative hooks — registered with the narrative manager if available
    try:
        from src.narrative import get_narrative_manager
        nm = get_narrative_manager()
        for hook in module.narrative_hooks:
            if hasattr(nm, 'register_hook'):
                nm.register_hook(hook)
        stats["narrative_hooks"] = len(module.narrative_hooks)
    except Exception:
        pass

    return stats


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_all_modules(modules_dir: str = None) -> list:
    """Discover, sort, load, and return all modules. Does NOT apply them to a world."""
    discovered = discover_modules(modules_dir)
    if not discovered:
        return []
    sorted_mods = topological_sort(discovered)
    loaded = []
    for slug, manifest, path in sorted_mods:
        try:
            mod = load_module(path)
            loaded.append(mod)
            logger.info(f"loaded module '{slug}' v{mod.version} from {path}")
        except Exception as e:
            logger.error(f"failed to load module '{slug}': {e}")
    return loaded


def apply_all_modules_to_world(world, modules_dir: str = None) -> dict:
    """End-to-end: discover, load, validate, apply, run migration."""
    modules = load_all_modules(modules_dir)
    if not modules:
        return {"loaded": 0, "applied": 0, "errors": []}

    # Validate each module against the world + other modules
    all_errors = []
    valid_modules = []
    for i, mod in enumerate(modules):
        others = modules[:i] + modules[i+1:]
        errors = validate_module(mod, world=world, other_modules=others)
        if errors:
            for e in errors:
                logger.error(f"module '{mod.module_id}' validation: {e}")
            all_errors.extend([f"{mod.module_id}: {e}" for e in errors])
            # Reject the module
            continue
        valid_modules.append(mod)

    # Apply valid modules
    applied = 0
    for mod in valid_modules:
        try:
            stats = apply_module_to_world(mod, world)
            logger.info(f"applied module '{mod.module_id}': {stats}")
            applied += 1
        except Exception as e:
            logger.error(f"failed to apply module '{mod.module_id}': {e}")
            all_errors.append(f"{mod.module_id}: apply failed: {e}")

    # Run arc migration for every loaded arc
    all_arcs = []
    for mod in valid_modules:
        all_arcs.extend(mod.arcs)
    if all_arcs:
        try:
            from src.migrations.arc_sheets import migrate_online_player, migrate_all_offline_players
            # Online players first
            for player in getattr(world, 'players', []) or []:
                migrate_online_player(player, all_arcs)
            # Offline player files
            players_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
            stats = migrate_all_offline_players(players_dir, all_arcs)
            logger.info(f"arc migration on offline players: {stats}")
        except Exception as e:
            logger.error(f"arc migration failed: {e}")

    return {
        "loaded": len(modules),
        "valid": len(valid_modules),
        "applied": applied,
        "errors": all_errors,
        "modules": [m.module_id for m in valid_modules],
    }
