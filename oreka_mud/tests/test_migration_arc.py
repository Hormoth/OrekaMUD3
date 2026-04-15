"""Tests for arc_sheets migration (Phase 3)."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.migrations.arc_sheets import (
    migrate_character_arc_sheets,
    migrate_player_file,
    migrate_all_offline_players,
    migrate_online_player,
)


REGISTERED_ARCS = [
    {
        "arc_id": "quiet_graft",
        "title": "The Quiet Graft",
        "checklist": [
            {"id": "met_maeren", "label": "Met Maeren", "category": "npc_met"},
            {"id": "met_vaerix", "label": "Met Vaerix", "category": "npc_met"},
        ],
    }
]


class TestMigrateCharacterArcSheets(unittest.TestCase):
    def test_old_save_no_arc_sheets_field(self):
        """Old save loads and gains all registered arcs as untouched."""
        char_data = {"name": "Test"}
        result = migrate_character_arc_sheets(char_data, REGISTERED_ARCS)
        self.assertIn("arc_sheets", result)
        self.assertIn("quiet_graft", result["arc_sheets"])
        sheet = result["arc_sheets"]["quiet_graft"]
        self.assertEqual(sheet["status"], "untouched")
        self.assertEqual(len(sheet["checklist"]), 2)
        for ci in sheet["checklist"]:
            self.assertEqual(ci["state"], "unchecked")

    def test_partial_arc_sheets(self):
        """Character with some arcs gains missing ones without disturbing existing."""
        char_data = {
            "arc_sheets": {
                "another_arc": {
                    "arc_id": "another_arc",
                    "title": "Another",
                    "status": "active",
                    "checklist": [],
                }
            }
        }
        result = migrate_character_arc_sheets(char_data, REGISTERED_ARCS)
        self.assertIn("quiet_graft", result["arc_sheets"])
        # Other arc unchanged
        self.assertEqual(result["arc_sheets"]["another_arc"]["status"], "active")

    def test_new_checklist_item_added(self):
        """Character with outdated checklist gains new items as unchecked."""
        char_data = {
            "arc_sheets": {
                "quiet_graft": {
                    "arc_id": "quiet_graft",
                    "title": "The Quiet Graft",
                    "status": "aware",
                    "checklist": [
                        {"id": "met_maeren", "category": "npc_met", "state": "checked"},
                    ],
                }
            }
        }
        result = migrate_character_arc_sheets(char_data, REGISTERED_ARCS)
        items = result["arc_sheets"]["quiet_graft"]["checklist"]
        self.assertEqual(len(items), 2)  # Original + new
        # Original retained checked state
        original = next(ci for ci in items if ci["id"] == "met_maeren")
        self.assertEqual(original["state"], "checked")
        # New item added as unchecked
        new = next(ci for ci in items if ci["id"] == "met_vaerix")
        self.assertEqual(new["state"], "unchecked")

    def test_orphaned_items_preserved(self):
        """Items removed from template are kept with orphaned: true."""
        char_data = {
            "arc_sheets": {
                "quiet_graft": {
                    "arc_id": "quiet_graft",
                    "title": "The Quiet Graft",
                    "status": "active",
                    "checklist": [
                        {"id": "met_maeren", "category": "npc_met", "state": "checked"},
                        {"id": "removed_item", "category": "fact_learned", "state": "checked"},
                    ],
                }
            }
        }
        result = migrate_character_arc_sheets(char_data, REGISTERED_ARCS)
        items = result["arc_sheets"]["quiet_graft"]["checklist"]
        # Removed item still present, marked orphaned
        orphan = next(ci for ci in items if ci["id"] == "removed_item")
        self.assertTrue(orphan.get("orphaned"))
        # Active state preserved
        self.assertEqual(orphan["state"], "checked")

    def test_no_change_when_already_synced(self):
        """Re-running migration with no template changes is a no-op."""
        char_data = {"name": "Test"}
        result1 = migrate_character_arc_sheets(char_data, REGISTERED_ARCS)
        snapshot1 = json.dumps(result1["arc_sheets"], sort_keys=True)
        result2 = migrate_character_arc_sheets(result1, REGISTERED_ARCS)
        snapshot2 = json.dumps(result2["arc_sheets"], sort_keys=True)
        self.assertEqual(snapshot1, snapshot2)


class TestMigratePlayerFile(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "test_player.json")

    def tearDown(self):
        # Clean up tmpdir
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_writes_backup_before_mutation(self):
        with open(self.path, "w") as f:
            json.dump({"name": "Test"}, f)

        changed = migrate_player_file(self.path, REGISTERED_ARCS, backup=True)
        self.assertTrue(changed)

        # Backup file exists
        backups = [f for f in os.listdir(self.tmpdir) if ".backup." in f]
        self.assertEqual(len(backups), 1)

    def test_no_change_no_backup(self):
        # Pre-populated with full migration
        char_data = {"name": "Test"}
        char_data = migrate_character_arc_sheets(char_data, REGISTERED_ARCS)
        with open(self.path, "w") as f:
            json.dump(char_data, f)

        changed = migrate_player_file(self.path, REGISTERED_ARCS, backup=True)
        self.assertFalse(changed)

        backups = [f for f in os.listdir(self.tmpdir) if ".backup." in f]
        self.assertEqual(len(backups), 0)

    def test_missing_file_returns_false(self):
        result = migrate_player_file(
            os.path.join(self.tmpdir, "nonexistent.json"),
            REGISTERED_ARCS,
        )
        self.assertFalse(result)


class TestMigrateAllOfflinePlayers(unittest.TestCase):
    def test_processes_directory(self):
        tmpdir = tempfile.mkdtemp()
        try:
            # Create three player files, one already migrated
            for name in ("alice", "bob", "carol"):
                with open(os.path.join(tmpdir, f"{name}.json"), "w") as f:
                    json.dump({"name": name}, f)
            # Pre-migrate one
            migrate_player_file(
                os.path.join(tmpdir, "carol.json"), REGISTERED_ARCS, backup=False
            )
            stats = migrate_all_offline_players(tmpdir, REGISTERED_ARCS)
            # Should migrate alice + bob (carol already done)
            self.assertEqual(stats["migrated"], 2)
            self.assertEqual(stats["skipped"], 1)
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_skips_backup_files(self):
        tmpdir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tmpdir, "alice.json"), "w") as f:
                json.dump({"name": "alice"}, f)
            with open(os.path.join(tmpdir, "alice.json.backup.20260101_000000"), "w") as f:
                json.dump({"name": "alice_backup"}, f)
            stats = migrate_all_offline_players(tmpdir, REGISTERED_ARCS)
            # Backup file should NOT be touched
            self.assertEqual(stats["migrated"], 1)
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestMigrateOnlinePlayer(unittest.TestCase):
    def test_appends_new_arcs_to_live_character(self):
        from src.character import Character
        from src.room import Room
        room = Room(vnum=1, name="x", description="x", exits={}, flags=[])
        char = Character(
            name="Test", title=None, race="Human", level=1,
            hp=10, max_hp=10, ac=10, room=room,
        )
        # No arcs initially
        self.assertEqual(char.arc_sheets, {})

        changed = migrate_online_player(char, REGISTERED_ARCS)
        self.assertTrue(changed)
        self.assertIn("quiet_graft", char.arc_sheets)
        self.assertEqual(len(char.arc_sheets["quiet_graft"].checklist), 2)

    def test_no_change_returns_false(self):
        from src.character import Character
        from src.room import Room
        room = Room(vnum=1, name="x", description="x", exits={}, flags=[])
        char = Character(
            name="Test", title=None, race="Human", level=1,
            hp=10, max_hp=10, ac=10, room=room,
        )
        migrate_online_player(char, REGISTERED_ARCS)
        # Run again — no change
        result = migrate_online_player(char, REGISTERED_ARCS)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
