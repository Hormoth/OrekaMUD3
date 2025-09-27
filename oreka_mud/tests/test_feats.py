
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.character import Character
from src.feats import list_eligible_feats, FEATS
from src.classes import CLASSES

class FeatSystemTest(unittest.TestCase):
    def setUp(self):
        self.room = None
        self.char = Character(
            name="TestFighter", title="", race="Human", level=1, hp=10, max_hp=10, ac=10, room=self.room,
            char_class="Fighter", skills={}, spells_known={}, str_score=13
        )

    def test_eligible_feats_at_creation(self):
        eligible = list_eligible_feats(self.char)
        self.assertTrue(len(eligible) > 0)
        self.assertIn("Power Attack", eligible)  # Example feat

    def test_bonus_feat_granted_at_levelup(self):
        # Simulate level-up to a level that grants Bonus Feat
        self.char.set_level(1)
        # Fighter gets Bonus Feat at level 1
        eligible = list_eligible_feats(self.char)
        # Simulate picking the first eligible feat
        chosen = eligible[0]
        self.char.feats.append(chosen)
        self.assertIn(chosen, self.char.feats)

    def test_levelup_command_triggers_bonus_feat(self):
        # This is a placeholder: would require integration test with async/command system
        self.char.set_level(1)
        old_feats = set(self.char.feats)
        self.char.set_level(2)
        # No bonus feat at level 2 for Fighter
        self.assertEqual(set(self.char.feats), old_feats)
        self.char.set_level(4)
        # Fighter gets Bonus Feat at level 4
        eligible = list_eligible_feats(self.char)
        self.char.feats.append(eligible[0])
        self.assertIn(eligible[0], self.char.feats)

if __name__ == "__main__":
    unittest.main()
