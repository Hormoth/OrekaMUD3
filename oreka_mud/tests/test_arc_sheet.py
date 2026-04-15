"""Tests for ArcSheet schema and Character integration."""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_schemas.arc_sheet import (
    ArcSheet, ChecklistItem,
    CHECKLIST_CATEGORIES, CHECKLIST_STATES, ARC_STATUSES,
    validate_arc_sheet, fresh_arc_from_template,
)


class TestChecklistItem(unittest.TestCase):
    def test_round_trip(self):
        ci = ChecklistItem(
            id="met_maeren",
            label="Met Maeren of the Long Road",
            category="npc_met",
            state="detailed",
            detail={"trust": "warm", "topics": ["ledger"]},
            first_changed_at=100.0,
            last_changed_at=200.0,
        )
        ci2 = ChecklistItem.from_dict(ci.to_dict())
        self.assertEqual(ci.to_dict(), ci2.to_dict())


class TestArcSheet(unittest.TestCase):
    def test_round_trip(self):
        arc = ArcSheet(
            arc_id="quiet_graft",
            title="The Quiet Graft",
            status="aware",
            checklist=[
                ChecklistItem(id="a", label="A", category="npc_met"),
                ChecklistItem(id="b", label="B", category="fact_learned", state="checked"),
            ],
            entered_at=100.0,
            flags={"key": "value"},
        )
        arc2 = ArcSheet.from_dict(arc.to_dict())
        self.assertEqual(arc.to_dict(), arc2.to_dict())

    def test_get_item(self):
        arc = ArcSheet(arc_id="x", checklist=[ChecklistItem(id="i1"), ChecklistItem(id="i2")])
        self.assertIsNotNone(arc.get_item("i1"))
        self.assertIsNone(arc.get_item("missing"))

    def test_has_any_progress(self):
        arc = ArcSheet(arc_id="x", checklist=[
            ChecklistItem(id="i1", state="unchecked"),
            ChecklistItem(id="i2", state="unchecked"),
        ])
        self.assertFalse(arc.has_any_progress())
        arc.checklist[0].state = "checked"
        self.assertTrue(arc.has_any_progress())

    def test_evaluation_context(self):
        arc = ArcSheet(arc_id="x", status="aware", flags={"k": "v"}, checklist=[
            ChecklistItem(id="met", state="checked", detail={"trust": "warm"}),
        ])
        ctx = arc.to_evaluation_context()
        self.assertEqual(ctx["met"]["state"], "checked")
        self.assertEqual(ctx["met"]["detail"]["trust"], "warm")
        self.assertEqual(ctx["arc"]["status"], "aware")
        self.assertEqual(ctx["arc"]["flags"]["k"], "v")


class TestValidateArcSheet(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_arc_sheet({"arc_id": "x"}), [])

    def test_missing_arc_id(self):
        errors = validate_arc_sheet({})
        self.assertTrue(any("arc_id" in e for e in errors))

    def test_bad_status(self):
        errors = validate_arc_sheet({"arc_id": "x", "status": "bogus"})
        self.assertTrue(any("status" in e for e in errors))

    def test_bad_category(self):
        errors = validate_arc_sheet({"arc_id": "x", "checklist": [
            {"id": "a", "category": "ennui"},
        ]})
        self.assertTrue(any("category" in e for e in errors))

    def test_bad_state(self):
        errors = validate_arc_sheet({"arc_id": "x", "checklist": [
            {"id": "a", "category": "npc_met", "state": "halfway"},
        ]})
        self.assertTrue(any("state" in e for e in errors))

    def test_detailed_requires_detail(self):
        errors = validate_arc_sheet({"arc_id": "x", "checklist": [
            {"id": "a", "category": "npc_met", "state": "detailed", "detail": {}},
        ]})
        self.assertTrue(any("detail" in e for e in errors))

    def test_duplicate_item_ids(self):
        errors = validate_arc_sheet({"arc_id": "x", "checklist": [
            {"id": "a", "category": "npc_met"},
            {"id": "a", "category": "fact_learned"},
        ]})
        self.assertTrue(any("duplicate" in e for e in errors))


class TestFreshArcFromTemplate(unittest.TestCase):
    def test_creates_unchecked_arc(self):
        template = {
            "arc_id": "x",
            "title": "X",
            "checklist": [
                {"id": "a", "label": "A", "category": "npc_met"},
                {"id": "b", "label": "B", "category": "fact_learned"},
            ],
        }
        arc = fresh_arc_from_template(template)
        self.assertEqual(arc.arc_id, "x")
        self.assertEqual(arc.status, "untouched")
        self.assertEqual(len(arc.checklist), 2)
        for ci in arc.checklist:
            self.assertEqual(ci.state, "unchecked")


# =========================================================================
# Character integration
# =========================================================================

class TestCharacterArcIntegration(unittest.TestCase):
    def _make_char(self):
        from src.character import Character
        from src.room import Room
        room = Room(vnum=1, name="x", description="x", exits={}, flags=[])
        return Character(
            name="Test", title=None, race="Human", level=1,
            hp=10, max_hp=10, ac=10, room=room,
        )

    def test_arc_sheets_initialized_empty(self):
        char = self._make_char()
        self.assertEqual(char.arc_sheets, {})

    def test_get_arc_returns_none_when_missing(self):
        char = self._make_char()
        self.assertIsNone(char.get_arc("nonexistent"))

    def test_check_arc_item_returns_false_when_arc_missing(self):
        char = self._make_char()
        self.assertFalse(char.check_arc_item("missing", "x"))

    def test_check_arc_item_flips_state(self):
        char = self._make_char()
        arc = ArcSheet(arc_id="quiet_graft", title="x", checklist=[
            ChecklistItem(id="met_maeren", category="npc_met"),
        ])
        char.arc_sheets["quiet_graft"] = arc

        result = char.check_arc_item("quiet_graft", "met_maeren")
        self.assertTrue(result)
        self.assertEqual(arc.get_item("met_maeren").state, "checked")
        # Status auto-promoted
        self.assertEqual(arc.status, "aware")
        # Timestamps set
        self.assertIsNotNone(arc.get_item("met_maeren").first_changed_at)
        self.assertIsNotNone(arc.last_activity_at)

    def test_check_arc_item_with_detail(self):
        char = self._make_char()
        arc = ArcSheet(arc_id="x", checklist=[ChecklistItem(id="a", category="npc_met")])
        char.arc_sheets["x"] = arc

        char.check_arc_item("x", "a", detail={"trust": "warm"})
        item = arc.get_item("a")
        self.assertEqual(item.state, "detailed")
        self.assertEqual(item.detail["trust"], "warm")

    def test_check_arc_item_no_change_returns_false(self):
        char = self._make_char()
        arc = ArcSheet(arc_id="x", checklist=[
            ChecklistItem(id="a", category="npc_met", state="checked"),
        ])
        char.arc_sheets["x"] = arc
        # Already checked; no detail provided
        result = char.check_arc_item("x", "a")
        self.assertFalse(result)

    def test_touched_arcs(self):
        char = self._make_char()
        arc1 = ArcSheet(arc_id="a", checklist=[ChecklistItem(id="x")])
        arc2 = ArcSheet(arc_id="b", checklist=[
            ChecklistItem(id="x", state="checked"),
        ])
        char.arc_sheets["a"] = arc1
        char.arc_sheets["b"] = arc2

        touched = char.touched_arcs()
        self.assertNotIn("a", touched)
        self.assertIn("b", touched)

    def test_set_arc_status(self):
        char = self._make_char()
        arc = ArcSheet(arc_id="x")
        char.arc_sheets["x"] = arc

        result = char.set_arc_status("x", "active")
        self.assertTrue(result)
        self.assertEqual(arc.status, "active")
        self.assertIsNotNone(arc.entered_at)

    def test_set_arc_status_invalid(self):
        char = self._make_char()
        arc = ArcSheet(arc_id="x")
        char.arc_sheets["x"] = arc
        self.assertFalse(char.set_arc_status("x", "fake_status"))

    def test_set_arc_status_no_change(self):
        char = self._make_char()
        arc = ArcSheet(arc_id="x", status="active")
        char.arc_sheets["x"] = arc
        self.assertFalse(char.set_arc_status("x", "active"))

    def test_set_arc_status_resolution(self):
        char = self._make_char()
        arc = ArcSheet(arc_id="x", status="active")
        char.arc_sheets["x"] = arc
        char.set_arc_status("x", "resolved", resolution="graft_took")
        self.assertEqual(arc.status, "resolved")
        self.assertEqual(arc.resolution, "graft_took")


class TestCharacterArcSerialization(unittest.TestCase):
    def _make_char_with_arcs(self):
        from src.character import Character
        from src.room import Room
        room = Room(vnum=1, name="x", description="x", exits={}, flags=[])
        char = Character(
            name="Test", title=None, race="Human", level=1,
            hp=10, max_hp=10, ac=10, room=room,
        )
        char.arc_sheets = {
            "quiet_graft": ArcSheet(
                arc_id="quiet_graft", title="The Quiet Graft", status="aware",
                checklist=[ChecklistItem(id="met_maeren", state="checked")],
            )
        }
        return char

    def test_serialize_arc_sheets(self):
        char = self._make_char_with_arcs()
        d = char.to_dict()
        self.assertIn("arc_sheets", d)
        self.assertIn("quiet_graft", d["arc_sheets"])
        self.assertEqual(d["arc_sheets"]["quiet_graft"]["status"], "aware")

    def test_round_trip_through_save_load(self):
        from src.character import Character
        char = self._make_char_with_arcs()
        d = char.to_dict()

        char2 = Character.from_dict(d)
        self.assertIn("quiet_graft", char2.arc_sheets)
        arc = char2.arc_sheets["quiet_graft"]
        self.assertEqual(arc.status, "aware")
        self.assertEqual(arc.get_item("met_maeren").state, "checked")

    def test_old_save_without_arc_sheets_loads(self):
        from src.character import Character
        # Simulate an old save by removing arc_sheets from dict
        char = self._make_char_with_arcs()
        d = char.to_dict()
        del d["arc_sheets"]

        char2 = Character.from_dict(d)
        self.assertEqual(char2.arc_sheets, {})


if __name__ == "__main__":
    unittest.main()
