import unittest
from unittest.mock import MagicMock
from oreka_mud.src.commands import CommandParser
from oreka_mud.src.character import Character
from oreka_mud.src.room import Room

class TestBarbarianFastMovement(unittest.TestCase):
    def setUp(self):
        # Create a mock world with two rooms
        self.room1 = Room(vnum=1, name="Start Room", description="", exits={"north": 2}, flags=[])
        self.room2 = Room(vnum=2, name="Flagged Room", description="", exits={}, flags=[])
        self.world = MagicMock()
        self.world.rooms = {1: self.room1, 2: self.room2}
        self.cmd_parser = CommandParser(self.world)
        # Create a Barbarian character with Fast Movement
        self.barbarian = Character(
            name="Barb",
            title="Barbarian",
            race="Human",
            level=10,
            hp=100,
            max_hp=100,
            ac=15,
            room=self.room1,
            char_class="Barbarian"
        )
        self.barbarian.get_class_features = MagicMock(return_value=["Fast Movement"])
        self.room1.players = [self.barbarian]
        self.room2.players = []
        # Create a non-Barbarian character
        self.fighter = Character(
            name="Fighter",
            title="Fighter",
            race="Human",
            level=10,
            hp=100,
            max_hp=100,
            ac=15,
            room=self.room1,
            char_class="Fighter"
        )
        self.fighter.get_class_features = MagicMock(return_value=[])
    def test_barbarian_ignores_easy_flags(self):
        # Barbarians with Fast Movement should ignore 'difficult' flag
        self.room2.flags = ["difficult"]
        result = self.cmd_parser.cmd_move(self.barbarian, "north")
        self.assertIn("You move north", result)
        self.assertEqual(self.barbarian.room, self.room2)
    def test_barbarian_blocked_by_hard_flag(self):
        # Barbarians with Fast Movement should be blocked by 'deep_water'
        self.room2.flags = ["deep_water"]
        result = self.cmd_parser.cmd_move(self.barbarian, "north")
        self.assertIn("cannot move into", result)
        self.assertEqual(self.barbarian.room, self.room1)
    def test_non_barbarian_blocked_by_any_flag(self):
        # Non-barbarians should be blocked by any movement-impairing flag
        self.room2.flags = ["difficult"]
        result = self.cmd_parser.cmd_move(self.fighter, "north")
        self.assertIn("impeded by", result)
        self.assertEqual(self.fighter.room, self.room1)
    def test_barbarian_ignores_multiple_easy_flags(self):
        # Barbarians should ignore multiple easy flags
        self.room2.flags = ["difficult", "undergrowth"]
        result = self.cmd_parser.cmd_move(self.barbarian, "north")
        self.assertIn("You move north", result)
        self.assertEqual(self.barbarian.room, self.room2)
    def test_barbarian_blocked_by_multiple_flags(self):
        # If any hard flag is present, Barbarian is blocked
        self.room2.flags = ["difficult", "deep_water", "undergrowth"]
        result = self.cmd_parser.cmd_move(self.barbarian, "north")
        self.assertIn("cannot move into", result)
        self.assertEqual(self.barbarian.room, self.room1)

if __name__ == "__main__":
    unittest.main()
