import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.character import Character
from src.commands import CommandParser

class SpellcastingTest(unittest.TestCase):
    def setUp(self):
        self.world = None  # Mock or minimal world if needed
        self.cmd = CommandParser(self.world)
        self.char = Character(
            name="TestMage", title="", race="Human", level=3, hp=10, max_hp=10, ac=10, room=None,
            char_class="Wizard"
        )

    def test_cast_known_spell(self):
        # Should know Magic Missile at level 3
        result = self.cmd.cmd_cast(self.char, "Magic Missile")
        self.assertIn("You cast Magic Missile", result)
        self.assertIn("Slots left for level 1", result)

    def test_cast_unknown_spell(self):
        result = self.cmd.cmd_cast(self.char, "Cure Light Wounds")
        self.assertIn("do not know the spell", result)

    def test_cast_no_slots(self):
        # Exhaust all level 1 slots
        self.char.spells_per_day[1] = 0
        result = self.cmd.cmd_cast(self.char, "Magic Missile")
        self.assertIn("No spell slots remaining", result)

    def test_cast_invalid_spell(self):
        result = self.cmd.cmd_cast(self.char, "Nonexistent Spell")
        self.assertIn("No such spell", result)

if __name__ == "__main__":
    unittest.main()
