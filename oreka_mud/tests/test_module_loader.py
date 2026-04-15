"""Tests for the module loader (Phase 4)."""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.module_loader import (
    discover_modules, topological_sort, load_module,
    validate_module, apply_module_to_world, load_all_modules,
    Module,
)


def _make_minimal_module(tmpdir: str, slug: str, manifest_extras: dict = None):
    """Create a minimal valid module on disk and return its path."""
    mod_dir = os.path.join(tmpdir, slug)
    os.makedirs(mod_dir, exist_ok=True)
    manifest = {
        "module_id": slug,
        "title": slug.title(),
        "version": "0.1.0",
        "author": "Test",
        "depends_on_modules": [],
    }
    if manifest_extras:
        manifest.update(manifest_extras)
    with open(os.path.join(mod_dir, "module.json"), "w") as f:
        json.dump(manifest, f)
    return mod_dir


def _add_arcs(mod_dir: str, arcs: list):
    with open(os.path.join(mod_dir, "arcs.json"), "w") as f:
        json.dump({"arcs": arcs}, f)


class TestDiscovery(unittest.TestCase):
    def test_discovers_modules(self):
        tmpdir = tempfile.mkdtemp()
        try:
            _make_minimal_module(tmpdir, "alpha")
            _make_minimal_module(tmpdir, "beta")
            results = discover_modules(tmpdir)
            slugs = [r[0] for r in results]
            self.assertIn("alpha", slugs)
            self.assertIn("beta", slugs)
        finally:
            import shutil; shutil.rmtree(tmpdir, ignore_errors=True)

    def test_skips_dirs_without_manifest(self):
        tmpdir = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmpdir, "no_manifest"))
            _make_minimal_module(tmpdir, "valid")
            results = discover_modules(tmpdir)
            slugs = [r[0] for r in results]
            self.assertNotIn("no_manifest", slugs)
            self.assertIn("valid", slugs)
        finally:
            import shutil; shutil.rmtree(tmpdir, ignore_errors=True)


class TestTopologicalSort(unittest.TestCase):
    def test_simple_dep_order(self):
        # B depends on A; result should be [A, B]
        manifests = [
            ("a", {"module_id": "a", "depends_on_modules": []}, "/a"),
            ("b", {"module_id": "b", "depends_on_modules": ["a"]}, "/b"),
        ]
        sorted_mods = topological_sort(manifests)
        slugs = [s[0] for s in sorted_mods]
        self.assertEqual(slugs, ["a", "b"])

    def test_reverse_input_still_sorted(self):
        # Same as above but input order reversed
        manifests = [
            ("b", {"module_id": "b", "depends_on_modules": ["a"]}, "/b"),
            ("a", {"module_id": "a", "depends_on_modules": []}, "/a"),
        ]
        sorted_mods = topological_sort(manifests)
        slugs = [s[0] for s in sorted_mods]
        self.assertEqual(slugs, ["a", "b"])

    def test_cycle_raises(self):
        manifests = [
            ("a", {"module_id": "a", "depends_on_modules": ["b"]}, "/a"),
            ("b", {"module_id": "b", "depends_on_modules": ["a"]}, "/b"),
        ]
        with self.assertRaises(ValueError):
            topological_sort(manifests)

    def test_missing_dep_raises(self):
        manifests = [
            ("a", {"module_id": "a", "depends_on_modules": ["nonexistent"]}, "/a"),
        ]
        with self.assertRaises(ValueError):
            topological_sort(manifests)


class TestLoadModule(unittest.TestCase):
    def test_loads_minimal(self):
        tmpdir = tempfile.mkdtemp()
        try:
            mod_dir = _make_minimal_module(tmpdir, "test")
            mod = load_module(mod_dir)
            self.assertEqual(mod.module_id, "test")
            self.assertEqual(mod.version, "0.1.0")
            self.assertEqual(mod.arcs, [])
        finally:
            import shutil; shutil.rmtree(tmpdir, ignore_errors=True)

    def test_loads_arcs(self):
        tmpdir = tempfile.mkdtemp()
        try:
            mod_dir = _make_minimal_module(tmpdir, "test")
            _add_arcs(mod_dir, [
                {"arc_id": "a", "title": "A", "checklist": [
                    {"id": "x", "label": "X", "category": "npc_met"}
                ]}
            ])
            mod = load_module(mod_dir)
            self.assertEqual(len(mod.arcs), 1)
            self.assertEqual(mod.arcs[0]["arc_id"], "a")
        finally:
            import shutil; shutil.rmtree(tmpdir, ignore_errors=True)

    def test_loads_personas(self):
        tmpdir = tempfile.mkdtemp()
        try:
            mod_dir = _make_minimal_module(tmpdir, "test")
            personas_dir = os.path.join(mod_dir, "personas")
            os.makedirs(personas_dir)
            with open(os.path.join(personas_dir, "9000_test.json"), "w") as f:
                json.dump({"vnum": 9000, "voice": "x"}, f)
            mod = load_module(mod_dir)
            self.assertEqual(len(mod.personas), 1)
            self.assertEqual(mod.personas[0]["vnum"], 9000)
        finally:
            import shutil; shutil.rmtree(tmpdir, ignore_errors=True)


class TestValidateModule(unittest.TestCase):
    def test_empty_module_valid(self):
        mod = Module(module_id="x", title="X", version="0.0.0")
        self.assertEqual(validate_module(mod), [])

    def test_persona_referencing_undeclared_arc(self):
        mod = Module(
            module_id="x", title="X", version="0.0.0",
            arcs=[{"arc_id": "real_arc", "checklist": []}],
            personas=[{"vnum": 1, "arcs_known": ["nonexistent_arc"]}],
        )
        errors = validate_module(mod)
        self.assertTrue(any("arcs_known references unknown arc" in e for e in errors))

    def test_vnum_collision_against_world(self):
        world = MagicMock()
        world.mobs = {100: object()}
        world.rooms = {}
        mod = Module(
            module_id="x", title="X", version="0.0.0",
            mobs=[{"vnum": 100, "name": "Test Mob"}],
        )
        errors = validate_module(mod, world=world)
        self.assertTrue(any("collides with existing world mob" in e for e in errors))

    def test_vnum_collision_between_modules(self):
        mod_a = Module(
            module_id="a", title="A", version="0.0.0",
            mobs=[{"vnum": 200, "name": "A's mob"}],
        )
        mod_b = Module(
            module_id="b", title="B", version="0.0.0",
            mobs=[{"vnum": 200, "name": "B's mob"}],
        )
        errors = validate_module(mod_b, other_modules=[mod_a])
        self.assertTrue(any("collides with module 'a'" in e for e in errors))

    def test_room_vnum_collision(self):
        world = MagicMock()
        world.mobs = {}
        world.rooms = {500: object()}
        mod = Module(
            module_id="x", title="X", version="0.0.0",
            rooms=[{"vnum": 500, "name": "test"}],
        )
        errors = validate_module(mod, world=world)
        self.assertTrue(any("collides with existing world room" in e for e in errors))


class TestQuietGraftScaffold(unittest.TestCase):
    """Verify the actual Quiet Graft scaffold loads and validates."""

    def test_loads(self):
        # Load from real project path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        modules_root = os.path.join(script_dir, "..", "data", "modules")
        if not os.path.isdir(os.path.join(modules_root, "quiet_graft")):
            self.skipTest("quiet_graft module not present")
        mod = load_module(os.path.join(modules_root, "quiet_graft"))
        self.assertEqual(mod.module_id, "quiet_graft")
        # Has at least the one arc
        self.assertGreaterEqual(len(mod.arcs), 1)

    def test_validates(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        modules_root = os.path.join(script_dir, "..", "data", "modules")
        if not os.path.isdir(os.path.join(modules_root, "quiet_graft")):
            self.skipTest("quiet_graft module not present")
        mod = load_module(os.path.join(modules_root, "quiet_graft"))
        errors = validate_module(mod)
        self.assertEqual(errors, [],
                         f"Quiet Graft scaffold should validate cleanly. Errors: {errors}")


class TestApplyModuleToWorld(unittest.TestCase):
    def test_applies_persona_to_existing_mob(self):
        mob = MagicMock()
        mob.vnum = 9999
        world = MagicMock()
        world.mobs = {9999: mob}
        world.rooms = {}

        mod = Module(
            module_id="x", title="X", version="0.0.0",
            personas=[{"vnum": 9999, "voice": "test voice"}],
        )
        stats = apply_module_to_world(mod, world)
        self.assertEqual(stats["merged_personas"], 1)
        self.assertEqual(mob.ai_persona["voice"], "test voice")


if __name__ == "__main__":
    unittest.main()
