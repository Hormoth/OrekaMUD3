"""Tests for the mob spawning and respawn system."""

import unittest
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.spawning import (
    SpawnPoint,
    SpawnManager,
    DEFAULT_RESPAWN_TIME,
    BOSS_RESPAWN_TIME,
    NO_RESPAWN_FLAGS,
)
from src.mob import Mob
from src.room import Room


class MockWorld:
    """Mock world for testing."""
    def __init__(self):
        self.rooms = {}
        self.mobs = {}


class TestSpawnPoint(unittest.TestCase):
    """Test the SpawnPoint class."""

    def setUp(self):
        self.mob_template = {
            "vnum": 2001,
            "name": "Test Goblin",
            "level": 2,
            "hp_dice": [2, 6, 2],
            "ac": 13,
            "damage_dice": [1, 4, 1],
            "flags": [],
            "type_": "Humanoid",
            "alignment": "Neutral Evil",
            "ability_scores": {"Str": 11, "Dex": 13, "Con": 12, "Int": 10, "Wis": 9, "Cha": 6},
            "initiative": 1,
            "speed": {"land": 30},
            "attacks": [{"type": "club", "bonus": 2, "damage": "1d6+1"}],
            "special_attacks": [],
            "special_qualities": [],
            "feats": [],
            "skills": {},
            "saves": {"Fort": 3, "Ref": 2, "Will": 0},
            "environment": "Any",
            "organization": "Solitary",
            "cr": 1,
            "advancement": "By character class",
            "description": "A test goblin for spawning tests."
        }

    def test_spawn_point_creation(self):
        """Test creating a spawn point."""
        sp = SpawnPoint(self.mob_template, room_vnum=1000)

        self.assertEqual(sp.vnum, 2001)
        self.assertEqual(sp.name, "Test Goblin")
        self.assertEqual(sp.room_vnum, 1000)
        self.assertEqual(sp.respawn_time, DEFAULT_RESPAWN_TIME)
        self.assertIsNone(sp.current_mob)
        self.assertIsNone(sp.death_time)
        self.assertEqual(sp.spawn_count, 0)

    def test_spawn_point_boss_respawn_time(self):
        """Test that boss mobs have longer respawn times."""
        boss_template = self.mob_template.copy()
        boss_template["flags"] = ["boss"]

        sp = SpawnPoint(boss_template, room_vnum=1000)
        self.assertEqual(sp.respawn_time, BOSS_RESPAWN_TIME)

    def test_spawn_point_no_respawn_unique(self):
        """Test that unique mobs don't respawn."""
        unique_template = self.mob_template.copy()
        unique_template["flags"] = ["unique"]

        sp = SpawnPoint(unique_template, room_vnum=1000)
        self.assertIsNone(sp.respawn_time)

    def test_spawn_point_no_respawn_quest(self):
        """Test that quest mobs don't respawn."""
        quest_template = self.mob_template.copy()
        quest_template["flags"] = ["quest"]

        sp = SpawnPoint(quest_template, room_vnum=1000)
        self.assertIsNone(sp.respawn_time)

    def test_spawn_point_custom_respawn_time(self):
        """Test setting custom respawn time."""
        sp = SpawnPoint(self.mob_template, room_vnum=1000, respawn_time=120)
        self.assertEqual(sp.respawn_time, 120)

    def test_is_alive_no_mob(self):
        """Test is_alive when no mob exists."""
        sp = SpawnPoint(self.mob_template, room_vnum=1000)
        self.assertFalse(sp.is_alive())

    def test_can_respawn_never_spawned(self):
        """Test that spawn points can respawn if never spawned."""
        sp = SpawnPoint(self.mob_template, room_vnum=1000)
        self.assertTrue(sp.can_respawn())

    def test_can_respawn_unique(self):
        """Test that unique mobs cannot respawn."""
        unique_template = self.mob_template.copy()
        unique_template["flags"] = ["unique"]

        sp = SpawnPoint(unique_template, room_vnum=1000)
        self.assertFalse(sp.can_respawn())

    def test_mark_dead(self):
        """Test marking a mob as dead."""
        sp = SpawnPoint(self.mob_template, room_vnum=1000)

        # Simulate having a mob
        mock_mob = type('MockMob', (), {'alive': True, 'hp': 10})()
        sp.current_mob = mock_mob

        sp.mark_dead()

        self.assertIsNone(sp.current_mob)
        self.assertIsNotNone(sp.death_time)

    def test_time_until_respawn(self):
        """Test calculating time until respawn."""
        sp = SpawnPoint(self.mob_template, room_vnum=1000)

        # Never spawned - can respawn immediately
        self.assertEqual(sp.time_until_respawn(), 0)

        # Mark dead
        sp.mark_dead()

        # Should be close to full respawn time
        remaining = sp.time_until_respawn()
        self.assertIsNotNone(remaining)
        self.assertLessEqual(remaining, DEFAULT_RESPAWN_TIME)
        self.assertGreater(remaining, DEFAULT_RESPAWN_TIME - 1)

    def test_spawn(self):
        """Test spawning a new mob."""
        sp = SpawnPoint(self.mob_template, room_vnum=1000)

        # Create a mock world with the room
        world = MockWorld()
        world.rooms[1000] = Room(
            vnum=1000, name="Test Room", description="A test room.",
            exits={}, flags=[]
        )

        # Spawn the mob
        new_mob = sp.spawn(world)

        self.assertIsNotNone(new_mob)
        self.assertIsInstance(new_mob, Mob)
        self.assertEqual(new_mob.name, "Test Goblin")
        self.assertTrue(new_mob.alive)
        self.assertEqual(sp.spawn_count, 1)
        self.assertIn(new_mob, world.rooms[1000].mobs)
        self.assertIn(new_mob.vnum, world.mobs)


class TestSpawnManager(unittest.TestCase):
    """Test the SpawnManager class."""

    def setUp(self):
        self.mobs_data = [
            {
                "vnum": 2001,
                "name": "Test Goblin",
                "level": 2,
                "hp_dice": [2, 6, 2],
                "ac": 13,
                "damage_dice": [1, 4, 1],
                "flags": [],
                "room_vnum": 1000,
                "type_": "Humanoid",
                "alignment": "Neutral Evil",
                "ability_scores": {"Str": 11, "Dex": 13, "Con": 12, "Int": 10, "Wis": 9, "Cha": 6},
                "initiative": 1,
                "speed": {"land": 30},
                "attacks": [{"type": "club", "bonus": 2, "damage": "1d6+1"}],
                "special_attacks": [],
                "special_qualities": [],
                "feats": [],
                "skills": {},
                "saves": {"Fort": 3, "Ref": 2, "Will": 0},
                "environment": "Any",
                "organization": "Solitary",
                "cr": 1,
                "advancement": "By character class",
                "description": "A test goblin."
            },
            {
                "vnum": 2002,
                "name": "Test Boss",
                "level": 10,
                "hp_dice": [10, 10, 50],
                "ac": 20,
                "damage_dice": [2, 8, 5],
                "flags": ["boss"],
                "room_vnum": 1001,
                "type_": "Humanoid",
                "alignment": "Chaotic Evil",
                "ability_scores": {"Str": 18, "Dex": 14, "Con": 16, "Int": 12, "Wis": 10, "Cha": 14},
                "initiative": 2,
                "speed": {"land": 30},
                "attacks": [{"type": "sword", "bonus": 12, "damage": "2d8+5"}],
                "special_attacks": [],
                "special_qualities": [],
                "feats": [],
                "skills": {},
                "saves": {"Fort": 8, "Ref": 5, "Will": 3},
                "environment": "Any",
                "organization": "Solitary",
                "cr": 8,
                "advancement": "By character class",
                "description": "A test boss."
            }
        ]

        self.world = MockWorld()
        self.world.rooms[1000] = Room(
            vnum=1000, name="Test Room 1", description="Test room 1.",
            exits={}, flags=[]
        )
        self.world.rooms[1001] = Room(
            vnum=1001, name="Boss Room", description="The boss room.",
            exits={}, flags=[]
        )

    def test_initialize_from_mobs_data(self):
        """Test initializing spawn manager from mob data."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        self.assertEqual(len(manager.spawn_points), 2)
        self.assertIn(2001, manager.spawn_points)
        self.assertIn(2002, manager.spawn_points)

        # Check respawn times
        self.assertEqual(manager.spawn_points[2001].respawn_time, DEFAULT_RESPAWN_TIME)
        self.assertEqual(manager.spawn_points[2002].respawn_time, BOSS_RESPAWN_TIME)

    def test_on_mob_death(self):
        """Test tracking mob death."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        # Create a mock mob
        mock_mob = type('MockMob', (), {'vnum': 2001, 'room_vnum': 1000})()
        manager.spawn_points[2001].current_mob = mock_mob

        # Trigger death
        manager.on_mob_death(mock_mob)

        self.assertIsNone(manager.spawn_points[2001].current_mob)
        self.assertIsNotNone(manager.spawn_points[2001].death_time)

    def test_tick_respawns_mobs(self):
        """Test that tick respawns dead mobs when ready."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        # First, simulate that mobs were initially spawned and are alive
        mock_mob1 = type('MockMob', (), {'alive': True, 'hp': 10, 'vnum': 2001})()
        mock_mob2 = type('MockMob', (), {'alive': True, 'hp': 100, 'vnum': 2002})()
        manager.spawn_points[2001].current_mob = mock_mob1
        manager.spawn_points[2002].current_mob = mock_mob2

        # Now kill mob 2001 and set death time in the past
        manager.spawn_points[2001].current_mob = None
        manager.spawn_points[2001].death_time = time.time() - DEFAULT_RESPAWN_TIME - 1

        # Tick should respawn only mob 2001 (2002 is still alive)
        messages = manager.tick(self.world)

        self.assertEqual(len(messages), 1)
        self.assertIn("Test Goblin", messages[0])
        self.assertIsNotNone(manager.spawn_points[2001].current_mob)

    def test_force_respawn(self):
        """Test force respawning a specific mob."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        # Mark as dead
        manager.spawn_points[2001].mark_dead()

        # Force respawn
        success, message = manager.force_respawn(2001, self.world)

        self.assertTrue(success)
        self.assertIn("respawned", message.lower())
        self.assertIsNotNone(manager.spawn_points[2001].current_mob)

    def test_force_respawn_all(self):
        """Test force respawning all dead mobs."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        # Mark both as dead
        manager.spawn_points[2001].mark_dead()
        manager.spawn_points[2002].mark_dead()

        # Force respawn all
        count, messages = manager.force_respawn_all(self.world)

        self.assertEqual(count, 2)
        self.assertEqual(len(messages), 2)

    def test_set_respawn_time(self):
        """Test setting custom respawn time."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        # Set custom time
        success, message = manager.set_respawn_time(2001, 120)

        self.assertTrue(success)
        self.assertEqual(manager.spawn_points[2001].respawn_time, 120)

    def test_disable_respawn(self):
        """Test disabling respawn."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        # Disable respawn
        success, message = manager.set_respawn_time(2001, 0)

        self.assertTrue(success)
        self.assertIsNone(manager.spawn_points[2001].respawn_time)

    def test_get_pending_respawns(self):
        """Test getting list of pending respawns."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        # Simulate that mobs were initially spawned and are alive
        mock_mob1 = type('MockMob', (), {'alive': True, 'hp': 10, 'vnum': 2001})()
        mock_mob2 = type('MockMob', (), {'alive': True, 'hp': 100, 'vnum': 2002})()
        manager.spawn_points[2001].current_mob = mock_mob1
        manager.spawn_points[2002].current_mob = mock_mob2

        # Mark one as dead
        manager.spawn_points[2001].mark_dead()

        pending = manager.get_pending_respawns()

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0][0], "Test Goblin")
        self.assertEqual(pending[0][1], 2001)

    def test_get_status(self):
        """Test getting spawn manager status."""
        manager = SpawnManager()
        manager.initialize_from_mobs_data(self.mobs_data)

        status = manager.get_status()

        self.assertIn("Spawn Manager Status", status)
        self.assertIn("Total spawn points: 2", status)


if __name__ == "__main__":
    unittest.main()
