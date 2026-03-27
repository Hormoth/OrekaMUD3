"""Tests for the NPC schedule and routine system."""

import unittest
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.schedules import (
    GameTime,
    TimeOfDay,
    ActivityType,
    ScheduleEntry,
    NPCSchedule,
    ScheduleManager,
    find_path,
    create_shopkeeper_schedule,
    create_guard_schedule,
)
from src.room import Room


class MockWorld:
    """Mock world for testing."""
    def __init__(self):
        self.rooms = {}
        self.mobs = {}


class MockMob:
    """Mock mob for testing."""
    def __init__(self, vnum, name, room_vnum=None):
        self.vnum = vnum
        self.name = name
        self.room_vnum = room_vnum
        self.alive = True


class TestGameTime(unittest.TestCase):
    """Test the GameTime class."""

    def test_initial_time(self):
        """Test default time initialization."""
        gt = GameTime()
        self.assertEqual(gt.hour, 8)
        self.assertEqual(gt.day, 1)
        self.assertEqual(gt.month, 1)
        self.assertEqual(gt.year, 1000)

    def test_custom_initial_time(self):
        """Test custom time initialization."""
        gt = GameTime(hour=14, day=15, month=6, year=1500)
        self.assertEqual(gt.hour, 14)
        self.assertEqual(gt.day, 15)
        self.assertEqual(gt.month, 6)
        self.assertEqual(gt.year, 1500)

    def test_time_of_day_dawn(self):
        """Test dawn time period."""
        gt = GameTime(hour=5)
        self.assertEqual(gt.get_time_of_day(), TimeOfDay.DAWN)

        gt = GameTime(hour=6)
        self.assertEqual(gt.get_time_of_day(), TimeOfDay.DAWN)

    def test_time_of_day_morning(self):
        """Test morning time period."""
        gt = GameTime(hour=7)
        self.assertEqual(gt.get_time_of_day(), TimeOfDay.MORNING)

        gt = GameTime(hour=11)
        self.assertEqual(gt.get_time_of_day(), TimeOfDay.MORNING)

    def test_time_of_day_noon(self):
        """Test noon time period."""
        gt = GameTime(hour=12)
        self.assertEqual(gt.get_time_of_day(), TimeOfDay.NOON)

    def test_time_of_day_night(self):
        """Test night time period."""
        gt = GameTime(hour=22)
        self.assertEqual(gt.get_time_of_day(), TimeOfDay.NIGHT)

    def test_time_of_day_midnight(self):
        """Test midnight time period."""
        gt = GameTime(hour=2)
        self.assertEqual(gt.get_time_of_day(), TimeOfDay.MIDNIGHT)

    def test_is_daytime(self):
        """Test daytime check."""
        gt = GameTime(hour=12)
        self.assertTrue(gt.is_daytime())

        gt = GameTime(hour=22)
        self.assertFalse(gt.is_daytime())

    def test_is_nighttime(self):
        """Test nighttime check."""
        gt = GameTime(hour=22)
        self.assertTrue(gt.is_nighttime())

        gt = GameTime(hour=12)
        self.assertFalse(gt.is_nighttime())

    def test_set_time(self):
        """Test setting time directly."""
        gt = GameTime(hour=8)
        gt.set_time(14)
        self.assertEqual(gt.hour, 14)

    def test_get_time_string(self):
        """Test time string formatting."""
        gt = GameTime(hour=8)
        self.assertEqual(gt.get_time_string(), "8:00 AM")

        gt = GameTime(hour=14)
        self.assertEqual(gt.get_time_string(), "2:00 PM")

        gt = GameTime(hour=0)
        self.assertEqual(gt.get_time_string(), "12:00 AM")

    def test_pause_resume(self):
        """Test pausing and resuming time."""
        gt = GameTime(hour=8)
        gt.pause()
        self.assertTrue(gt._paused)

        gt.resume()
        self.assertFalse(gt._paused)


class TestScheduleEntry(unittest.TestCase):
    """Test the ScheduleEntry class."""

    def test_is_active_normal_range(self):
        """Test activity check for normal hour range."""
        entry = ScheduleEntry(
            start_hour=9, end_hour=17,
            activity=ActivityType.WORKING,
            location=1000
        )

        self.assertTrue(entry.is_active_at(9))
        self.assertTrue(entry.is_active_at(12))
        self.assertTrue(entry.is_active_at(17))
        self.assertFalse(entry.is_active_at(8))
        self.assertFalse(entry.is_active_at(18))

    def test_is_active_midnight_wrap(self):
        """Test activity check for hours wrapping around midnight."""
        entry = ScheduleEntry(
            start_hour=22, end_hour=6,
            activity=ActivityType.SLEEPING,
            location=1000
        )

        self.assertTrue(entry.is_active_at(22))
        self.assertTrue(entry.is_active_at(0))
        self.assertTrue(entry.is_active_at(3))
        self.assertTrue(entry.is_active_at(6))
        self.assertFalse(entry.is_active_at(12))
        self.assertFalse(entry.is_active_at(20))


class TestNPCSchedule(unittest.TestCase):
    """Test the NPCSchedule class."""

    def setUp(self):
        self.schedule = NPCSchedule(
            npc_vnum=3000,
            home_location=1000,
            entries=[
                ScheduleEntry(0, 5, ActivityType.SLEEPING, 1000),
                ScheduleEntry(7, 17, ActivityType.WORKING, 1001),
                ScheduleEntry(18, 21, ActivityType.EATING, 1002),
                ScheduleEntry(22, 23, ActivityType.RESTING, 1000),
            ]
        )

    def test_get_current_entry(self):
        """Test getting the current schedule entry."""
        entry = self.schedule.get_current_entry(12)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.activity, ActivityType.WORKING)

        entry = self.schedule.get_current_entry(3)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.activity, ActivityType.SLEEPING)

    def test_get_current_entry_gap(self):
        """Test getting entry during schedule gap."""
        entry = self.schedule.get_current_entry(6)
        self.assertIsNone(entry)

    def test_get_current_location(self):
        """Test getting current location."""
        loc = self.schedule.get_current_location(12)
        self.assertEqual(loc, 1001)  # At work

        loc = self.schedule.get_current_location(3)
        self.assertEqual(loc, 1000)  # At home sleeping

        loc = self.schedule.get_current_location(6)
        self.assertEqual(loc, 1000)  # Gap, returns home

    def test_get_current_activity(self):
        """Test getting current activity."""
        activity = self.schedule.get_current_activity(12)
        self.assertEqual(activity, ActivityType.WORKING)

        activity = self.schedule.get_current_activity(6)
        self.assertEqual(activity, ActivityType.IDLE)  # Gap


class TestPathfinding(unittest.TestCase):
    """Test the pathfinding system."""

    def setUp(self):
        """Create a simple connected room network."""
        self.rooms = {}

        # Create rooms: 1 - 2 - 3
        #                   |
        #                   4
        self.rooms[1] = Room(vnum=1, name="Room 1", description="", exits={"east": 2}, flags=[])
        self.rooms[2] = Room(vnum=2, name="Room 2", description="", exits={"west": 1, "east": 3, "south": 4}, flags=[])
        self.rooms[3] = Room(vnum=3, name="Room 3", description="", exits={"west": 2}, flags=[])
        self.rooms[4] = Room(vnum=4, name="Room 4", description="", exits={"north": 2}, flags=[])

    def test_find_path_adjacent(self):
        """Test finding path to adjacent room."""
        path = find_path(1, 2, self.rooms)
        self.assertEqual(path, [2])

    def test_find_path_multiple_steps(self):
        """Test finding path requiring multiple steps."""
        path = find_path(1, 3, self.rooms)
        self.assertEqual(path, [2, 3])

    def test_find_path_branch(self):
        """Test finding path with branching."""
        path = find_path(1, 4, self.rooms)
        self.assertEqual(path, [2, 4])

    def test_find_path_same_room(self):
        """Test finding path to same room."""
        path = find_path(1, 1, self.rooms)
        self.assertEqual(path, [])

    def test_find_path_no_path(self):
        """Test when no path exists."""
        # Add a disconnected room
        self.rooms[5] = Room(vnum=5, name="Room 5", description="", exits={}, flags=[])
        path = find_path(1, 5, self.rooms)
        self.assertIsNone(path)

    def test_find_path_invalid_room(self):
        """Test with invalid room vnum."""
        path = find_path(1, 999, self.rooms)
        self.assertIsNone(path)


class TestScheduleManager(unittest.TestCase):
    """Test the ScheduleManager class."""

    def setUp(self):
        self.manager = ScheduleManager()
        self.world = MockWorld()

        # Create connected rooms
        self.world.rooms[1000] = Room(vnum=1000, name="Shop", description="", exits={"east": 1001}, flags=[])
        self.world.rooms[1001] = Room(vnum=1001, name="Home", description="", exits={"west": 1000}, flags=[])

        # Create a mob
        self.mob = MockMob(3000, "Test NPC", 1000)
        self.world.mobs[3000] = self.mob
        self.world.rooms[1000].mobs = [self.mob]
        self.world.rooms[1001].mobs = []

        # Create a schedule
        self.schedule = NPCSchedule(
            npc_vnum=3000,
            home_location=1001,
            entries=[
                ScheduleEntry(0, 6, ActivityType.SLEEPING, 1001),
                ScheduleEntry(7, 18, ActivityType.WORKING, 1000),
                ScheduleEntry(19, 23, ActivityType.RESTING, 1001),
            ]
        )

    def test_register_schedule(self):
        """Test registering a schedule."""
        self.manager.register_schedule(self.schedule)
        self.assertIn(3000, self.manager.schedules)
        self.assertIn(3000, self.manager.npc_states)

    def test_get_npc_activity(self):
        """Test getting NPC activity."""
        self.manager.register_schedule(self.schedule)

        # Default is IDLE until tick updates it
        activity = self.manager.get_npc_activity(3000)
        self.assertEqual(activity, ActivityType.IDLE)

    def test_is_npc_responsive(self):
        """Test NPC responsiveness check."""
        self.manager.register_schedule(self.schedule)

        # Default activity (IDLE) is responsive
        self.assertTrue(self.manager.is_npc_responsive(3000))

        # Set to sleeping
        self.manager.npc_states[3000]['current_activity'] = ActivityType.SLEEPING
        self.assertFalse(self.manager.is_npc_responsive(3000))

    def test_get_activity_description(self):
        """Test activity description generation."""
        self.manager.register_schedule(self.schedule)
        self.manager.npc_states[3000]['current_activity'] = ActivityType.WORKING

        desc = self.manager.get_activity_description(self.mob)
        self.assertIn("Test NPC", desc)
        self.assertIn("work", desc.lower())

    def test_tick_moves_npc(self):
        """Test that tick moves NPCs to correct location."""
        self.manager.register_schedule(self.schedule)

        # Set mob in wrong room (shop at 1000) during resting hours
        self.mob.room_vnum = 1000
        self.world.rooms[1000].mobs = [self.mob]
        self.world.rooms[1001].mobs = []

        # Create game time set to resting hours (20:00)
        game_time = GameTime(hour=20)

        # Run tick
        messages = self.manager.tick(game_time, self.world)

        # NPC should start moving toward home (1001)
        self.assertGreater(len(messages), 0)

    def test_force_move_npc(self):
        """Test force moving an NPC."""
        self.manager.register_schedule(self.schedule)

        success, msg = self.manager.force_move_npc(3000, 1001, self.world)

        self.assertTrue(success)
        self.assertIn(self.mob, self.world.rooms[1001].mobs)
        self.assertNotIn(self.mob, self.world.rooms[1000].mobs)


class TestScheduleTemplates(unittest.TestCase):
    """Test the schedule template functions."""

    def test_create_shopkeeper_schedule(self):
        """Test shopkeeper schedule creation."""
        schedule = create_shopkeeper_schedule(3000, shop_room=1000, home_room=1001)

        self.assertEqual(schedule.npc_vnum, 3000)
        self.assertEqual(schedule.home_location, 1001)
        self.assertGreater(len(schedule.entries), 0)

        # Should have working hours
        has_working = any(e.activity == ActivityType.WORKING for e in schedule.entries)
        self.assertTrue(has_working)

        # Should have sleeping
        has_sleeping = any(e.activity == ActivityType.SLEEPING for e in schedule.entries)
        self.assertTrue(has_sleeping)

    def test_create_guard_schedule(self):
        """Test guard patrol schedule creation."""
        patrol_route = [1000, 1001, 1002, 1003]
        schedule = create_guard_schedule(2001, patrol_route=patrol_route, barracks=1004)

        self.assertEqual(schedule.npc_vnum, 2001)
        self.assertEqual(schedule.home_location, 1004)

        # Should have patrolling
        patrol_entries = [e for e in schedule.entries if e.activity == ActivityType.PATROLLING]
        self.assertGreater(len(patrol_entries), 0)

        # Patrol entry should have the route
        self.assertEqual(patrol_entries[0].patrol_route, patrol_route)


if __name__ == "__main__":
    unittest.main()
