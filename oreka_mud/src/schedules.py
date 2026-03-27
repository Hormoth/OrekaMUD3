"""
NPC Schedule and Routine System for OrekaMUD3

This module implements dynamic NPC behaviors including:
- Game time system with day/night cycle
- NPC schedules with activities at different times
- Pathfinding for NPC movement between rooms
- Activity states that affect NPC behavior and dialogue
"""

import time
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import deque
from dataclasses import dataclass, field


# =============================================================================
# Game Time System
# =============================================================================

class TimeOfDay(Enum):
    """Periods of the game day."""
    DAWN = "dawn"           # 5:00 - 6:59
    MORNING = "morning"     # 7:00 - 11:59
    NOON = "noon"           # 12:00 - 12:59
    AFTERNOON = "afternoon" # 13:00 - 17:59
    EVENING = "evening"     # 18:00 - 20:59
    NIGHT = "night"         # 21:00 - 23:59
    MIDNIGHT = "midnight"   # 0:00 - 4:59


# Time period boundaries (hour ranges)
TIME_PERIODS = {
    TimeOfDay.MIDNIGHT: (0, 4),
    TimeOfDay.DAWN: (5, 6),
    TimeOfDay.MORNING: (7, 11),
    TimeOfDay.NOON: (12, 12),
    TimeOfDay.AFTERNOON: (13, 17),
    TimeOfDay.EVENING: (18, 20),
    TimeOfDay.NIGHT: (21, 23),
}


class GameTime:
    """
    Tracks in-game time with configurable speed.

    Default: 1 real minute = 1 game hour (24 real minutes = 1 game day)
    """

    # How many real seconds equal one game hour
    REAL_SECONDS_PER_GAME_HOUR = 60  # 1 minute = 1 hour

    def __init__(self, hour: int = 8, day: int = 1, month: int = 1, year: int = 1000):
        self.hour = hour  # 0-23
        self.day = day    # 1-30
        self.month = month  # 1-12
        self.year = year
        self._last_update = time.time()
        self._paused = False

        # Month names for flavor
        self.month_names = [
            "Deepwinter", "Icemelt", "Springseed", "Rainmoon",
            "Greengrass", "Summertide", "Highsun", "Harvestend",
            "Leaffall", "Frostfall", "Darknight", "Yearsend"
        ]

    def tick(self):
        """Update game time based on elapsed real time."""
        if self._paused:
            return

        now = time.time()
        elapsed = now - self._last_update

        # Calculate how many game hours have passed
        hours_passed = int(elapsed / self.REAL_SECONDS_PER_GAME_HOUR)

        if hours_passed > 0:
            self._last_update = now - (elapsed % self.REAL_SECONDS_PER_GAME_HOUR)
            self._advance_hours(hours_passed)

    def _advance_hours(self, hours: int):
        """Advance time by the given number of hours."""
        self.hour += hours

        while self.hour >= 24:
            self.hour -= 24
            self.day += 1

            if self.day > 30:
                self.day = 1
                self.month += 1

                if self.month > 12:
                    self.month = 1
                    self.year += 1

    def get_time_of_day(self) -> TimeOfDay:
        """Get the current period of day."""
        for period, (start, end) in TIME_PERIODS.items():
            if start <= self.hour <= end:
                return period
        return TimeOfDay.MIDNIGHT

    def is_daytime(self) -> bool:
        """Check if it's currently daytime (for visibility, etc.)."""
        return self.hour >= 6 and self.hour < 20

    def is_nighttime(self) -> bool:
        """Check if it's currently nighttime."""
        return not self.is_daytime()

    def get_time_string(self) -> str:
        """Get a formatted time string."""
        period = "AM" if self.hour < 12 else "PM"
        display_hour = self.hour if self.hour <= 12 else self.hour - 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:00 {period}"

    def get_full_time_string(self) -> str:
        """Get a detailed time and date string."""
        month_name = self.month_names[self.month - 1]
        time_of_day = self.get_time_of_day().value.capitalize()
        return f"{time_of_day}, {self.get_time_string()}, Day {self.day} of {month_name}, Year {self.year}"

    def get_description(self) -> str:
        """Get an atmospheric description of the current time."""
        tod = self.get_time_of_day()
        descriptions = {
            TimeOfDay.DAWN: "The first light of dawn breaks over the horizon, painting the sky in shades of pink and gold.",
            TimeOfDay.MORNING: "The morning sun shines brightly, and the day is full of promise.",
            TimeOfDay.NOON: "The sun stands directly overhead, casting short shadows.",
            TimeOfDay.AFTERNOON: "The afternoon sun hangs in the western sky, its warmth still strong.",
            TimeOfDay.EVENING: "The evening approaches as the sun sinks toward the horizon, bathing everything in amber light.",
            TimeOfDay.NIGHT: "Night has fallen. Stars begin to appear in the darkening sky.",
            TimeOfDay.MIDNIGHT: "Deep night envelops the land. The world sleeps under a canopy of stars.",
        }
        return descriptions.get(tod, "")

    def pause(self):
        """Pause time progression."""
        self._paused = True

    def resume(self):
        """Resume time progression."""
        self._paused = False
        self._last_update = time.time()

    def set_time(self, hour: int):
        """Set the current hour (for admin commands)."""
        self.hour = hour % 24
        self._last_update = time.time()


# =============================================================================
# Activity System
# =============================================================================

class ActivityType(Enum):
    """Types of activities NPCs can perform."""
    IDLE = "idle"               # Standing around, default
    WORKING = "working"         # At their job, doing work
    TRAVELING = "traveling"     # Moving between locations
    RESTING = "resting"         # At home, relaxing
    SLEEPING = "sleeping"       # Asleep (won't respond)
    EATING = "eating"           # At tavern or home, eating
    PATROLLING = "patrolling"   # Moving through a patrol route
    SOCIALIZING = "socializing" # Chatting with others
    PRAYING = "praying"         # At temple, religious activity
    TRAINING = "training"       # Practicing combat or skills


# Activity descriptions for "look" command
ACTIVITY_DESCRIPTIONS = {
    ActivityType.IDLE: "{name} is standing here.",
    ActivityType.WORKING: "{name} is hard at work.",
    ActivityType.TRAVELING: "{name} is passing through.",
    ActivityType.RESTING: "{name} is relaxing.",
    ActivityType.SLEEPING: "{name} is fast asleep.",
    ActivityType.EATING: "{name} is having a meal.",
    ActivityType.PATROLLING: "{name} is on patrol, watching alertly.",
    ActivityType.SOCIALIZING: "{name} is chatting with others.",
    ActivityType.PRAYING: "{name} is deep in prayer.",
    ActivityType.TRAINING: "{name} is practicing their skills.",
}

# Activities where NPCs won't respond to conversation
NON_RESPONSIVE_ACTIVITIES = {ActivityType.SLEEPING}

# Activities that can be interrupted
INTERRUPTIBLE_ACTIVITIES = {
    ActivityType.IDLE, ActivityType.RESTING, ActivityType.SOCIALIZING,
    ActivityType.EATING
}


@dataclass
class ScheduleEntry:
    """A single entry in an NPC's schedule."""
    start_hour: int           # Hour this activity starts (0-23)
    end_hour: int             # Hour this activity ends (0-23)
    activity: ActivityType    # What they're doing
    location: int             # Room vnum where this happens
    description: str = ""     # Optional custom description
    patrol_route: List[int] = field(default_factory=list)  # For patrolling: list of room vnums

    def is_active_at(self, hour: int) -> bool:
        """Check if this entry is active at the given hour."""
        if self.start_hour <= self.end_hour:
            return self.start_hour <= hour <= self.end_hour
        else:
            # Wraps around midnight (e.g., 22:00 - 6:00)
            return hour >= self.start_hour or hour <= self.end_hour


@dataclass
class NPCSchedule:
    """Complete schedule for an NPC."""
    npc_vnum: int
    home_location: int                    # Default location when no schedule entry
    entries: List[ScheduleEntry] = field(default_factory=list)
    enabled: bool = True

    def get_current_entry(self, hour: int) -> Optional[ScheduleEntry]:
        """Get the schedule entry for the current hour."""
        for entry in self.entries:
            if entry.is_active_at(hour):
                return entry
        return None

    def get_current_location(self, hour: int) -> int:
        """Get where the NPC should be at this hour."""
        entry = self.get_current_entry(hour)
        if entry:
            return entry.location
        return self.home_location

    def get_current_activity(self, hour: int) -> ActivityType:
        """Get what the NPC should be doing at this hour."""
        entry = self.get_current_entry(hour)
        if entry:
            return entry.activity
        return ActivityType.IDLE


# =============================================================================
# Pathfinding
# =============================================================================

def find_path(start_vnum: int, end_vnum: int, rooms: Dict[int, Any]) -> Optional[List[int]]:
    """
    Find a path between two rooms using BFS.

    Args:
        start_vnum: Starting room vnum
        end_vnum: Destination room vnum
        rooms: Dict of room vnum -> Room objects

    Returns:
        List of room vnums representing the path (excluding start, including end),
        or None if no path exists.
    """
    if start_vnum == end_vnum:
        return []

    if start_vnum not in rooms or end_vnum not in rooms:
        return None

    # BFS
    queue = deque([(start_vnum, [])])
    visited: Set[int] = {start_vnum}

    while queue:
        current, path = queue.popleft()
        current_room = rooms.get(current)

        if not current_room:
            continue

        # Check all exits
        exits = getattr(current_room, 'exits', {})
        for direction, next_vnum in exits.items():
            if next_vnum == end_vnum:
                return path + [next_vnum]

            if next_vnum not in visited and next_vnum in rooms:
                visited.add(next_vnum)
                queue.append((next_vnum, path + [next_vnum]))

    return None  # No path found


# =============================================================================
# Schedule Manager
# =============================================================================

class ScheduleManager:
    """Manages all NPC schedules and movements."""

    def __init__(self):
        self.schedules: Dict[int, NPCSchedule] = {}  # npc_vnum -> NPCSchedule
        self.npc_states: Dict[int, dict] = {}  # npc_vnum -> current state
        self.enabled = True
        self.movement_messages: List[Tuple[int, str]] = []  # (room_vnum, message)

    def register_schedule(self, schedule: NPCSchedule):
        """Register a schedule for an NPC."""
        self.schedules[schedule.npc_vnum] = schedule
        self.npc_states[schedule.npc_vnum] = {
            'current_activity': ActivityType.IDLE,
            'current_path': [],
            'patrol_index': 0,
            'last_location': schedule.home_location,
        }

    def get_npc_activity(self, npc_vnum: int) -> ActivityType:
        """Get the current activity for an NPC."""
        state = self.npc_states.get(npc_vnum)
        if state:
            return state.get('current_activity', ActivityType.IDLE)
        return ActivityType.IDLE

    def get_activity_description(self, npc) -> str:
        """Get a description of what the NPC is currently doing."""
        activity = self.get_npc_activity(npc.vnum)
        template = ACTIVITY_DESCRIPTIONS.get(activity, "{name} is here.")
        return template.format(name=npc.name)

    def is_npc_responsive(self, npc_vnum: int) -> bool:
        """Check if NPC will respond to conversation."""
        activity = self.get_npc_activity(npc_vnum)
        return activity not in NON_RESPONSIVE_ACTIVITIES

    def get_activity_context(self, npc_vnum: int) -> str:
        """Get context string for AI roleplay about current activity."""
        state = self.npc_states.get(npc_vnum)
        if not state:
            return ""

        activity = state.get('current_activity', ActivityType.IDLE)

        contexts = {
            ActivityType.IDLE: "You are currently idle, with no pressing tasks.",
            ActivityType.WORKING: "You are busy with your work duties right now.",
            ActivityType.TRAVELING: "You are on your way somewhere and can't stay long.",
            ActivityType.RESTING: "You are taking a well-deserved rest.",
            ActivityType.SLEEPING: "You are asleep and cannot be disturbed.",
            ActivityType.EATING: "You are enjoying a meal.",
            ActivityType.PATROLLING: "You are on patrol duty and must remain vigilant.",
            ActivityType.SOCIALIZING: "You are relaxing and chatting with others.",
            ActivityType.PRAYING: "You are in the middle of your prayers.",
            ActivityType.TRAINING: "You are in the middle of training exercises.",
        }

        return contexts.get(activity, "")

    def tick(self, game_time: GameTime, world) -> List[Tuple[int, str]]:
        """
        Update all NPC schedules based on current game time.

        Args:
            game_time: Current game time
            world: The OrekaWorld instance

        Returns:
            List of (room_vnum, message) tuples for movement notifications
        """
        if not self.enabled:
            return []

        messages = []
        current_hour = game_time.hour

        for npc_vnum, schedule in self.schedules.items():
            if not schedule.enabled:
                continue

            # Find the NPC in the world
            npc = world.mobs.get(npc_vnum)
            if not npc or not getattr(npc, 'alive', True):
                continue

            state = self.npc_states.get(npc_vnum, {})

            # Get where they should be
            target_location = schedule.get_current_location(current_hour)
            target_activity = schedule.get_current_activity(current_hour)

            # Find current location
            current_location = self._find_npc_location(npc, world)

            if current_location is None:
                continue

            # Handle patrolling
            entry = schedule.get_current_entry(current_hour)
            if entry and entry.activity == ActivityType.PATROLLING and entry.patrol_route:
                # Advance patrol
                patrol_index = state.get('patrol_index', 0)
                target_location = entry.patrol_route[patrol_index % len(entry.patrol_route)]

                if current_location == target_location:
                    # Move to next patrol point
                    state['patrol_index'] = (patrol_index + 1) % len(entry.patrol_route)
                    target_location = entry.patrol_route[state['patrol_index']]

            # Check if NPC needs to move
            if current_location != target_location:
                # Get or compute path
                current_path = state.get('current_path', [])

                if not current_path or (current_path and current_path[-1] != target_location):
                    # Need new path
                    current_path = find_path(current_location, target_location, world.rooms)
                    state['current_path'] = current_path if current_path else []

                if current_path:
                    # Move one step
                    next_room_vnum = current_path.pop(0)
                    state['current_path'] = current_path

                    move_msg = self._move_npc(npc, current_location, next_room_vnum, world)
                    if move_msg:
                        messages.extend(move_msg)

                    state['current_activity'] = ActivityType.TRAVELING
                else:
                    # Can't reach destination, stay put
                    state['current_activity'] = target_activity
            else:
                # At destination
                state['current_path'] = []
                state['current_activity'] = target_activity

            state['last_location'] = current_location
            self.npc_states[npc_vnum] = state

        return messages

    def _find_npc_location(self, npc, world) -> Optional[int]:
        """Find which room an NPC is currently in."""
        for room_vnum, room in world.rooms.items():
            if npc in room.mobs:
                return room_vnum
        return getattr(npc, 'room_vnum', None)

    def _move_npc(self, npc, from_vnum: int, to_vnum: int, world) -> List[Tuple[int, str]]:
        """
        Move an NPC from one room to another.

        Returns list of (room_vnum, message) for notifications.
        """
        messages = []

        from_room = world.rooms.get(from_vnum)
        to_room = world.rooms.get(to_vnum)

        if not from_room or not to_room:
            return messages

        # Find exit direction
        direction = None
        for dir_name, dest_vnum in from_room.exits.items():
            if dest_vnum == to_vnum:
                direction = dir_name
                break

        # Remove from old room
        if npc in from_room.mobs:
            from_room.mobs.remove(npc)
            leave_msg = f"{npc.name} leaves {direction}." if direction else f"{npc.name} leaves."
            messages.append((from_vnum, leave_msg))

        # Add to new room
        if npc not in to_room.mobs:
            to_room.mobs.append(npc)

            # Find arrival direction
            arrive_dir = None
            opposite = {
                'north': 'south', 'south': 'north',
                'east': 'west', 'west': 'east',
                'up': 'below', 'down': 'above',
                'northeast': 'southwest', 'southwest': 'northeast',
                'northwest': 'southeast', 'southeast': 'northwest',
            }
            if direction:
                arrive_dir = opposite.get(direction, direction)

            arrive_msg = f"{npc.name} arrives from the {arrive_dir}." if arrive_dir else f"{npc.name} arrives."
            messages.append((to_vnum, arrive_msg))

        # Update NPC's room reference
        npc.room_vnum = to_vnum

        return messages

    def force_move_npc(self, npc_vnum: int, room_vnum: int, world) -> Tuple[bool, str]:
        """Force an NPC to a specific room immediately."""
        npc = world.mobs.get(npc_vnum)
        if not npc:
            return False, f"NPC vnum {npc_vnum} not found."

        target_room = world.rooms.get(room_vnum)
        if not target_room:
            return False, f"Room vnum {room_vnum} not found."

        # Remove from current room
        for room in world.rooms.values():
            if npc in room.mobs:
                room.mobs.remove(npc)
                break

        # Add to target room
        target_room.mobs.append(npc)
        npc.room_vnum = room_vnum

        # Clear path
        if npc_vnum in self.npc_states:
            self.npc_states[npc_vnum]['current_path'] = []

        return True, f"{npc.name} has been moved to {target_room.name}."

    def get_schedule_status(self, npc_vnum: int, game_time: GameTime) -> str:
        """Get detailed status of an NPC's schedule."""
        schedule = self.schedules.get(npc_vnum)
        if not schedule:
            return f"No schedule registered for vnum {npc_vnum}."

        state = self.npc_states.get(npc_vnum, {})
        current_entry = schedule.get_current_entry(game_time.hour)

        lines = [
            f"Schedule for NPC vnum {npc_vnum}:",
            f"  Enabled: {schedule.enabled}",
            f"  Home location: {schedule.home_location}",
            f"  Current activity: {state.get('current_activity', ActivityType.IDLE).value}",
            f"  Current path: {state.get('current_path', [])}",
            "",
            "Schedule entries:",
        ]

        for i, entry in enumerate(schedule.entries):
            active = " <-- CURRENT" if entry == current_entry else ""
            lines.append(f"  {i+1}. {entry.start_hour:02d}:00-{entry.end_hour:02d}:00 "
                        f"{entry.activity.value} @ room {entry.location}{active}")
            if entry.patrol_route:
                lines.append(f"      Patrol: {entry.patrol_route}")

        return "\n".join(lines)


# =============================================================================
# Default Schedules
# =============================================================================

def create_shopkeeper_schedule(npc_vnum: int, shop_room: int, home_room: int) -> NPCSchedule:
    """Create a typical shopkeeper schedule."""
    return NPCSchedule(
        npc_vnum=npc_vnum,
        home_location=home_room,
        entries=[
            # Sleep at home
            ScheduleEntry(0, 5, ActivityType.SLEEPING, home_room),
            # Wake up, travel to shop
            ScheduleEntry(6, 6, ActivityType.TRAVELING, shop_room),
            # Work at shop
            ScheduleEntry(7, 18, ActivityType.WORKING, shop_room),
            # Evening - socialize or eat
            ScheduleEntry(19, 21, ActivityType.EATING, shop_room),  # Could be tavern
            # Head home
            ScheduleEntry(22, 23, ActivityType.RESTING, home_room),
        ]
    )


def create_guard_schedule(npc_vnum: int, patrol_route: List[int], barracks: int) -> NPCSchedule:
    """Create a typical guard patrol schedule."""
    return NPCSchedule(
        npc_vnum=npc_vnum,
        home_location=barracks,
        entries=[
            # Night shift patrol
            ScheduleEntry(0, 5, ActivityType.PATROLLING, patrol_route[0],
                         patrol_route=patrol_route),
            # Rest at barracks
            ScheduleEntry(6, 13, ActivityType.SLEEPING, barracks),
            # Afternoon training
            ScheduleEntry(14, 16, ActivityType.TRAINING, barracks),
            # Evening patrol
            ScheduleEntry(17, 23, ActivityType.PATROLLING, patrol_route[0],
                         patrol_route=patrol_route),
        ]
    )


def create_innkeeper_schedule(npc_vnum: int, tavern_room: int, private_room: int) -> NPCSchedule:
    """Create a typical innkeeper schedule."""
    return NPCSchedule(
        npc_vnum=npc_vnum,
        home_location=tavern_room,
        entries=[
            # Late night - cleaning/closing
            ScheduleEntry(0, 2, ActivityType.WORKING, tavern_room),
            # Sleep
            ScheduleEntry(3, 9, ActivityType.SLEEPING, private_room),
            # Morning prep
            ScheduleEntry(10, 11, ActivityType.WORKING, tavern_room),
            # Lunch service
            ScheduleEntry(12, 14, ActivityType.WORKING, tavern_room),
            # Afternoon break
            ScheduleEntry(15, 16, ActivityType.RESTING, private_room),
            # Evening service (busy time)
            ScheduleEntry(17, 23, ActivityType.WORKING, tavern_room),
        ]
    )


# =============================================================================
# Global Instance
# =============================================================================

# Global game time instance
game_time = GameTime()

# Global schedule manager instance
schedule_manager = ScheduleManager()


def get_game_time() -> GameTime:
    """Get the global game time instance."""
    return game_time


def get_schedule_manager() -> ScheduleManager:
    """Get the global schedule manager instance."""
    return schedule_manager


def initialize_schedules(world):
    """
    Initialize NPC schedules based on world data.
    This can be called after world.load_data() to set up default schedules.
    """
    # Example: Set up Mira the Shopkeeper (vnum 3000)
    # She works in room 1000 (The Chapel) and lives there too for now
    if 3000 in world.mobs:
        mira_schedule = NPCSchedule(
            npc_vnum=3000,
            home_location=1000,
            entries=[
                ScheduleEntry(0, 5, ActivityType.SLEEPING, 1000,
                             description="Mira sleeps behind her counter."),
                ScheduleEntry(6, 6, ActivityType.IDLE, 1000,
                             description="Mira yawns and prepares for the day."),
                ScheduleEntry(7, 19, ActivityType.WORKING, 1000,
                             description="Mira tends her shop, ready for customers."),
                ScheduleEntry(20, 21, ActivityType.EATING, 1000,
                             description="Mira enjoys a simple meal."),
                ScheduleEntry(22, 23, ActivityType.RESTING, 1000,
                             description="Mira relaxes after a long day."),
            ]
        )
        schedule_manager.register_schedule(mira_schedule)
