"""Tests for the rpsheet command (Phase 3)."""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _make_char():
    from src.character import Character
    from src.room import Room
    from src.ai_schemas.pc_sheet import PcSheet
    room = Room(vnum=1, name="x", description="x", exits={}, flags=[])
    char = Character(
        name="Hormoth", title=None, race="Taraf-Imro Human", level=3,
        hp=10, max_hp=10, ac=10, room=room,
    )
    # Override save to no-op so tests don't write to disk
    char.save = lambda: None
    return char


def _parser():
    from src.commands import CommandParser
    p = CommandParser.__new__(CommandParser)
    p.world = MagicMock()
    return p


class TestRpsheetView(unittest.TestCase):
    def test_view_empty_sheet(self):
        char = _make_char()
        result = _parser().cmd_rpsheet(char, "")
        self.assertIn("Hormoth", result)
        self.assertIn("they/them", result)
        self.assertIn("(set with: rpsheet bio", result)


class TestRpsheetBio(unittest.TestCase):
    def test_set_bio(self):
        char = _make_char()
        _parser().cmd_rpsheet(char, "bio I am a scribe from Custos.")
        self.assertEqual(char.rp_sheet.bio, "I am a scribe from Custos.")

    def test_view_existing_bio(self):
        char = _make_char()
        char.rp_sheet.bio = "Existing bio."
        result = _parser().cmd_rpsheet(char, "bio")
        self.assertIn("Existing bio.", result)

    def test_bio_too_long_rejected(self):
        char = _make_char()
        result = _parser().cmd_rpsheet(char, "bio " + "X" * 600)
        self.assertIn("500 characters or less", result)
        self.assertEqual(char.rp_sheet.bio, "")


class TestRpsheetGoals(unittest.TestCase):
    def test_add_goal(self):
        char = _make_char()
        _parser().cmd_rpsheet(char, "goal add find the missing ledger")
        self.assertIn("find the missing ledger", char.rp_sheet.goals)

    def test_remove_goal(self):
        char = _make_char()
        char.rp_sheet.goals = ["one", "two", "three"]
        _parser().cmd_rpsheet(char, "goal remove 2")
        self.assertEqual(char.rp_sheet.goals, ["one", "three"])

    def test_max_10_goals(self):
        char = _make_char()
        char.rp_sheet.goals = [f"goal {i}" for i in range(10)]
        result = _parser().cmd_rpsheet(char, "goal add eleventh")
        self.assertIn("maximum 10 goals", result)
        self.assertEqual(len(char.rp_sheet.goals), 10)


class TestRpsheetQuirks(unittest.TestCase):
    def test_add_quirk(self):
        char = _make_char()
        _parser().cmd_rpsheet(char, "quirk add always carries ink")
        self.assertIn("always carries ink", char.rp_sheet.quirks)

    def test_max_5_quirks(self):
        char = _make_char()
        char.rp_sheet.quirks = [f"q{i}" for i in range(5)]
        result = _parser().cmd_rpsheet(char, "quirk add another")
        self.assertIn("maximum 5 quirks", result)


class TestRpsheetVisibility(unittest.TestCase):
    def test_hide(self):
        char = _make_char()
        _parser().cmd_rpsheet(char, "hide")
        self.assertFalse(char.rp_sheet.sheet_visible_in_prompts)

    def test_show(self):
        char = _make_char()
        char.rp_sheet.sheet_visible_in_prompts = False
        _parser().cmd_rpsheet(char, "show")
        self.assertTrue(char.rp_sheet.sheet_visible_in_prompts)


class TestRpsheetClear(unittest.TestCase):
    def test_clear_bio(self):
        char = _make_char()
        char.rp_sheet.bio = "x"
        _parser().cmd_rpsheet(char, "clear bio")
        self.assertEqual(char.rp_sheet.bio, "")

    def test_clear_goals(self):
        char = _make_char()
        char.rp_sheet.goals = ["a", "b"]
        _parser().cmd_rpsheet(char, "clear goals")
        self.assertEqual(char.rp_sheet.goals, [])

    def test_clear_unknown_field(self):
        char = _make_char()
        result = _parser().cmd_rpsheet(char, "clear bogus")
        self.assertIn("Unknown field", result)


class TestRpsheetPersistence(unittest.TestCase):
    def test_round_trip_through_character_save_load(self):
        from src.character import Character
        char = _make_char()
        char.rp_sheet.bio = "A scribe."
        char.rp_sheet.goals = ["find the ledger"]
        char.rp_sheet.quirks = ["winces at thunder"]

        d = char.to_dict()
        char2 = Character.from_dict(d)
        self.assertEqual(char2.rp_sheet.bio, "A scribe.")
        self.assertEqual(char2.rp_sheet.goals, ["find the ledger"])
        self.assertEqual(char2.rp_sheet.quirks, ["winces at thunder"])

    def test_old_save_without_rp_sheet_loads(self):
        from src.character import Character
        char = _make_char()
        d = char.to_dict()
        del d["rp_sheet"]
        char2 = Character.from_dict(d)
        # Should have a fresh empty PcSheet
        self.assertIsNotNone(char2.rp_sheet)
        self.assertEqual(char2.rp_sheet.bio, "")


if __name__ == "__main__":
    unittest.main()
