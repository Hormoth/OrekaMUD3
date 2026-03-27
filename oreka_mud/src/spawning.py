"""Mob spawning and respawn management system."""

import time
import copy
import random
from typing import Dict, List, Optional, Tuple, Any

# Default respawn time in seconds (5 minutes)
DEFAULT_RESPAWN_TIME = 300

# Boss mobs take longer to respawn (15 minutes)
BOSS_RESPAWN_TIME = 900

# Unique/quest mobs don't respawn
NO_RESPAWN_FLAGS = {'unique', 'quest', 'no_respawn'}


class SpawnPoint:
    """Represents a single spawn point for a mob."""

    def __init__(self, mob_template: dict, room_vnum: int, respawn_time: int = None):
        """
        Initialize a spawn point.

        Args:
            mob_template: The full mob data dict from mobs.json
            room_vnum: The room where this mob spawns
            respawn_time: Override respawn time in seconds (None = use default)
        """
        self.mob_template = mob_template
        self.room_vnum = room_vnum
        self.vnum = mob_template.get('vnum')
        self.name = mob_template.get('name', 'Unknown')

        # Determine respawn time
        flags = set(f.lower() for f in mob_template.get('flags', []))
        if flags & NO_RESPAWN_FLAGS:
            self.respawn_time = None  # Never respawns
        elif 'boss' in flags:
            self.respawn_time = respawn_time or BOSS_RESPAWN_TIME
        else:
            self.respawn_time = respawn_time or DEFAULT_RESPAWN_TIME

        # Track the current mob instance (None if dead/not spawned)
        self.current_mob = None
        self.death_time = None
        self.spawn_count = 0  # Track how many times this mob has spawned

    def is_alive(self) -> bool:
        """Check if the current mob instance is alive."""
        if self.current_mob is None:
            return False
        return getattr(self.current_mob, 'alive', False) and getattr(self.current_mob, 'hp', 0) > 0

    def can_respawn(self) -> bool:
        """Check if this spawn point can respawn."""
        if self.respawn_time is None:
            return False  # Never respawns
        if self.is_alive():
            return False  # Already alive
        if self.death_time is None:
            return True  # Never spawned yet

        elapsed = time.time() - self.death_time
        return elapsed >= self.respawn_time

    def time_until_respawn(self) -> Optional[float]:
        """Get seconds until respawn, or None if can't respawn."""
        if self.respawn_time is None:
            return None
        if self.is_alive():
            return None
        if self.death_time is None:
            return 0  # Can spawn immediately

        elapsed = time.time() - self.death_time
        remaining = self.respawn_time - elapsed
        return max(0, remaining)

    def mark_dead(self):
        """Mark the current mob as dead and record death time."""
        self.death_time = time.time()
        self.current_mob = None

    def spawn(self, world) -> Optional[Any]:
        """
        Spawn a new mob instance at this spawn point.

        Args:
            world: The OrekaWorld instance

        Returns:
            The newly spawned Mob instance, or None if spawn failed
        """
        from src.mob import Mob

        if not self.can_respawn() and self.is_alive():
            return None

        room = world.rooms.get(self.room_vnum)
        if room is None:
            return None

        # Create a new mob instance from template
        mob_data = {k: v for k, v in self.mob_template.items() if k != 'room_vnum'}

        # Store hp_dice for potential re-rolling
        hp_dice = mob_data.get('hp_dice', [1, 8, 0])
        mob_data['hp_dice'] = hp_dice

        new_mob = Mob(**mob_data)
        new_mob.room_vnum = self.room_vnum

        # Reset combat state
        new_mob.alive = True
        new_mob.conditions = set()
        new_mob.active_conditions = {}

        # Add to world and room
        world.mobs[new_mob.vnum] = new_mob
        room.mobs.append(new_mob)

        # Update spawn point tracking
        self.current_mob = new_mob
        self.death_time = None
        self.spawn_count += 1

        return new_mob


class SpawnManager:
    """Manages all mob spawn points in the world."""

    def __init__(self):
        self.spawn_points: Dict[int, SpawnPoint] = {}  # vnum -> SpawnPoint
        self.respawn_messages: List[str] = []  # Messages to broadcast
        self.enabled = True

    def initialize_from_mobs_data(self, mobs_data: List[dict]):
        """
        Initialize spawn points from the mobs.json data.

        Args:
            mobs_data: List of mob dicts from mobs.json
        """
        seen_vnums = set()
        for mob_data in mobs_data:
            vnum = mob_data.get('vnum')
            room_vnum = mob_data.get('room_vnum')

            if vnum is None or room_vnum is None:
                continue

            # Handle duplicate vnums (same mob type in different rooms)
            # Use a composite key or just track the first occurrence
            if vnum in seen_vnums:
                # Create unique key for duplicate spawns
                spawn_key = vnum * 10000 + room_vnum
            else:
                spawn_key = vnum
                seen_vnums.add(vnum)

            self.spawn_points[spawn_key] = SpawnPoint(mob_data, room_vnum)

    def link_existing_mobs(self, world):
        """
        Link existing mobs in the world to their spawn points.
        Call this after world.load_data() to connect loaded mobs to spawn tracking.

        Args:
            world: The OrekaWorld instance
        """
        for vnum, mob in world.mobs.items():
            if vnum in self.spawn_points:
                self.spawn_points[vnum].current_mob = mob
            else:
                # Try composite key
                room_vnum = getattr(mob, 'room_vnum', None)
                if room_vnum:
                    spawn_key = vnum * 10000 + room_vnum
                    if spawn_key in self.spawn_points:
                        self.spawn_points[spawn_key].current_mob = mob

    def on_mob_death(self, mob, room=None):
        """
        Called when a mob dies. Records death time for respawn tracking.

        Args:
            mob: The Mob instance that died
            room: The room where it died (optional, for cleanup)
        """
        vnum = getattr(mob, 'vnum', None)
        if vnum is None:
            return

        # Find the spawn point
        spawn_point = self.spawn_points.get(vnum)
        if spawn_point is None:
            # Try composite key
            room_vnum = getattr(mob, 'room_vnum', None) or (room.vnum if room else None)
            if room_vnum:
                spawn_key = vnum * 10000 + room_vnum
                spawn_point = self.spawn_points.get(spawn_key)

        if spawn_point:
            spawn_point.mark_dead()

            # Remove from room's mob list
            if room:
                if mob in room.mobs:
                    room.mobs.remove(mob)

    def tick(self, world) -> List[str]:
        """
        Check for mobs that need to respawn and spawn them.
        Call this periodically (e.g., every 30 seconds or every game tick).

        Args:
            world: The OrekaWorld instance

        Returns:
            List of respawn messages for broadcasting
        """
        if not self.enabled:
            return []

        messages = []

        for spawn_key, spawn_point in self.spawn_points.items():
            if spawn_point.can_respawn():
                new_mob = spawn_point.spawn(world)
                if new_mob:
                    room = world.rooms.get(spawn_point.room_vnum)
                    room_name = room.name if room else "somewhere"
                    messages.append(f"[Respawn] {new_mob.name} appears in {room_name}.")

        return messages

    def force_respawn(self, vnum: int, world) -> Tuple[bool, str]:
        """
        Force a specific mob to respawn immediately.

        Args:
            vnum: The mob vnum to respawn
            world: The OrekaWorld instance

        Returns:
            (success, message) tuple
        """
        spawn_point = self.spawn_points.get(vnum)
        if spawn_point is None:
            return False, f"No spawn point found for vnum {vnum}."

        if spawn_point.is_alive():
            return False, f"{spawn_point.name} is still alive."

        # Clear death time to allow immediate respawn
        spawn_point.death_time = None
        new_mob = spawn_point.spawn(world)

        if new_mob:
            room = world.rooms.get(spawn_point.room_vnum)
            room_name = room.name if room else "somewhere"
            return True, f"{new_mob.name} has been respawned in {room_name}."
        else:
            return False, f"Failed to respawn mob vnum {vnum}."

    def force_respawn_all(self, world) -> Tuple[int, List[str]]:
        """
        Force all dead mobs to respawn immediately.

        Args:
            world: The OrekaWorld instance

        Returns:
            (count, messages) tuple
        """
        count = 0
        messages = []

        for spawn_key, spawn_point in self.spawn_points.items():
            if not spawn_point.is_alive() and spawn_point.respawn_time is not None:
                spawn_point.death_time = None
                new_mob = spawn_point.spawn(world)
                if new_mob:
                    count += 1
                    room = world.rooms.get(spawn_point.room_vnum)
                    room_name = room.name if room else "somewhere"
                    messages.append(f"  {new_mob.name} in {room_name}")

        return count, messages

    def set_respawn_time(self, vnum: int, seconds: int) -> Tuple[bool, str]:
        """
        Set custom respawn time for a specific mob.

        Args:
            vnum: The mob vnum
            seconds: Respawn time in seconds (0 = disable respawn)

        Returns:
            (success, message) tuple
        """
        spawn_point = self.spawn_points.get(vnum)
        if spawn_point is None:
            return False, f"No spawn point found for vnum {vnum}."

        if seconds <= 0:
            spawn_point.respawn_time = None
            return True, f"{spawn_point.name} will no longer respawn."
        else:
            spawn_point.respawn_time = seconds
            minutes = seconds / 60
            return True, f"{spawn_point.name} respawn time set to {minutes:.1f} minutes."

    def get_status(self) -> str:
        """Get a summary of spawn point status."""
        alive = 0
        dead = 0
        no_respawn = 0

        for sp in self.spawn_points.values():
            if sp.respawn_time is None:
                no_respawn += 1
            elif sp.is_alive():
                alive += 1
            else:
                dead += 1

        status = f"Spawn Manager Status:\n"
        status += f"  Enabled: {self.enabled}\n"
        status += f"  Total spawn points: {len(self.spawn_points)}\n"
        status += f"  Alive: {alive}\n"
        status += f"  Dead (pending respawn): {dead}\n"
        status += f"  No respawn: {no_respawn}\n"
        status += f"  Default respawn time: {DEFAULT_RESPAWN_TIME}s ({DEFAULT_RESPAWN_TIME/60:.1f} min)\n"
        status += f"  Boss respawn time: {BOSS_RESPAWN_TIME}s ({BOSS_RESPAWN_TIME/60:.1f} min)"

        return status

    def get_pending_respawns(self) -> List[Tuple[str, int, float]]:
        """
        Get list of mobs pending respawn with time remaining.

        Returns:
            List of (mob_name, vnum, seconds_remaining) tuples
        """
        pending = []

        for spawn_key, sp in self.spawn_points.items():
            if not sp.is_alive() and sp.respawn_time is not None:
                remaining = sp.time_until_respawn()
                if remaining is not None:
                    pending.append((sp.name, sp.vnum, remaining))

        # Sort by time remaining
        pending.sort(key=lambda x: x[2])
        return pending


# Global spawn manager instance
spawn_manager = SpawnManager()


def get_spawn_manager() -> SpawnManager:
    """Get the global spawn manager instance."""
    return spawn_manager


def initialize_spawning(mobs_data: List[dict], world):
    """
    Initialize the spawn system with mob data.

    Args:
        mobs_data: List of mob dicts from mobs.json
        world: The OrekaWorld instance
    """
    spawn_manager.initialize_from_mobs_data(mobs_data)
    spawn_manager.link_existing_mobs(world)
