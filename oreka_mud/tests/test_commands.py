import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.character import Character
from src.commands import CommandParser

class CommandIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.world = None
        self.parser = CommandParser(self.world)
        self.char = Character(
            name="TestFighter", title="", race="Human", level=1, hp=10, max_hp=10, ac=10, room=None,
            char_class="Fighter", skills={}, spells_known={}
        )
        self.char.writer = None  # Not used in sync test
        self.char.reader = None

    def test_levelup_command(self):
        old_level = self.char.class_level
        result = self.parser.cmd_levelup(self.char, "")
        self.assertIn("You have reached level", result)
        self.assertEqual(self.char.class_level, old_level + 1)

    def test_cmd_skills_lists_feats_and_features(self):
        self.char.feats.append("Toughness")
        result = self.parser.cmd_skills(self.char, "")
        self.assertIn("Toughness", result)
        self.assertIn("Class Features:", result)

    def test_cmd_score_includes_level_and_hp(self):
        result = self.parser.cmd_score(self.char, "")
        self.assertIn("Level:", result)
        self.assertIn(f"HP: {self.char.hp}/{self.char.max_hp}", result)

if __name__ == "__main__":
    unittest.main()
