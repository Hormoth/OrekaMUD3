"""Area reset system for OrekaMUD3.

Periodically restores rooms to their default state: replenishes items,
resets door states, and refills containers.  Mob respawning is handled
separately by src.spawning.SpawnManager.

Reset configuration lives in data/area_resets.json.  If the file is
missing a minimal default covering the Chapel tutorial area is created
on first load.
"""

import copy
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("OrekaMUD.AreaResets")

# Default reset interval in seconds (15 minutes)
DEFAULT_RESET_INTERVAL = 900

# ANSI-formatted message sent to players when their room resets
RESET_MESSAGE = (
    "\033[1;33m[Area Reset]\033[0m "
    "You notice the area returning to its natural state.\n"
)

# Path helpers ---------------------------------------------------------------

def _data_dir() -> str:
    """Return the absolute path to the data/ directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))


def _config_path() -> str:
    """Return the absolute path to data/area_resets.json."""
    return os.path.join(_data_dir(), "area_resets.json")


# Default configuration ------------------------------------------------------

def _default_config() -> dict:
    """Return a minimal default reset configuration for the Chapel area."""
    return {
        "areas": {
            "chapel": {
                "reset_interval": DEFAULT_RESET_INTERVAL,
                "rooms": {
                    "1000": {
                        "items": [],
                        "doors": {},
                        "containers": {}
                    }
                }
            }
        }
    }


# ---------------------------------------------------------------------------
# ResetManager
# ---------------------------------------------------------------------------

class ResetManager:
    """Manages periodic area resets — item replenishment, door states, and
    container contents."""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        # area_name -> timestamp of last successful reset
        self.last_reset: Dict[str, float] = {}
        self.enabled: bool = True
        self.load_resets()

    # -- Configuration -------------------------------------------------------

    def load_resets(self) -> None:
        """Load (or create) reset configuration from *data/area_resets.json*."""
        path = _config_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                logger.info("Loaded area reset config from %s", path)
            except Exception as exc:
                logger.error("Failed to load area_resets.json: %s", exc)
                self.config = _default_config()
        else:
            self.config = _default_config()
            self._save_config()
            logger.info("Created default area_resets.json at %s", path)

        # Initialise last_reset timestamps so that areas don't all fire at
        # once on first boot — stagger them by pretending they just reset.
        now = time.time()
        for area_name in self.config.get("areas", {}):
            if area_name not in self.last_reset:
                self.last_reset[area_name] = now

    def _save_config(self) -> None:
        """Persist the current configuration to disk."""
        path = _config_path()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as exc:
            logger.error("Failed to save area_resets.json: %s", exc)

    # -- Tick entry point ----------------------------------------------------

    def check_resets(self, world) -> List[str]:
        """Called every game tick.  Check which areas are due for a reset and
        execute them.

        Returns a list of log-level status messages (not sent to players).
        """
        if not self.enabled:
            return []

        now = time.time()
        messages: List[str] = []
        areas = self.config.get("areas", {})

        for area_name, area_cfg in areas.items():
            interval = area_cfg.get("reset_interval", DEFAULT_RESET_INTERVAL)
            last = self.last_reset.get(area_name, 0)

            if now - last >= interval:
                result = self.reset_area(world, area_name)
                if result:
                    messages.append(result)

        return messages

    # -- Full area reset -----------------------------------------------------

    def reset_area(self, world, area_name: str) -> Optional[str]:
        """Reset every room defined under *area_name* in the config.

        Skips rooms where any player is in combat (State.COMBAT).
        Notifies players in affected rooms.

        Returns a short log string, or ``None`` if nothing happened.
        """
        areas = self.config.get("areas", {})
        area_cfg = areas.get(area_name)
        if area_cfg is None:
            return None

        rooms_cfg = area_cfg.get("rooms", {})
        if not rooms_cfg:
            self.last_reset[area_name] = time.time()
            return None

        rooms_reset = 0
        rooms_skipped = 0

        for vnum_str, room_cfg in rooms_cfg.items():
            try:
                vnum = int(vnum_str)
            except (ValueError, TypeError):
                logger.warning("Invalid vnum '%s' in area '%s'", vnum_str, area_name)
                continue

            room = world.rooms.get(vnum)
            if room is None:
                continue

            # Safety: skip rooms where a player is in combat
            if self._room_has_combat(room):
                rooms_skipped += 1
                continue

            # Perform the actual reset steps
            changed = False

            default_items = room_cfg.get("items")
            if default_items is not None:
                changed |= self.reset_room_items(world, vnum, default_items)

            default_doors = room_cfg.get("doors")
            if default_doors is not None:
                changed |= self.reset_doors(world, vnum, default_doors)

            default_containers = room_cfg.get("containers")
            if default_containers is not None:
                changed |= self.reset_containers(world, vnum, default_containers)

            if changed:
                rooms_reset += 1
                self._notify_players(room)

        self.last_reset[area_name] = time.time()

        if rooms_reset or rooms_skipped:
            msg = (
                f"Area '{area_name}' reset: {rooms_reset} room(s) restored"
                f"{f', {rooms_skipped} skipped (combat)' if rooms_skipped else ''}."
            )
            logger.info(msg)
            return msg

        return None

    # -- Item reset ----------------------------------------------------------

    def reset_room_items(self, world, vnum: int, default_items: list) -> bool:
        """Restore the default item list for a room.

        *default_items* is a list of dicts, each with at least ``vnum`` (int)
        and ``name`` (str).  Items are only added if the room does not already
        contain an item with that vnum — this avoids duplication while still
        allowing players to pick items up and have them re-appear on reset.

        Returns ``True`` if the room was modified.
        """
        room = world.rooms.get(vnum)
        if room is None:
            return False

        if not default_items:
            return False

        # Build set of item vnums currently on the ground
        existing_vnums = set()
        for item in room.items:
            iv = getattr(item, "vnum", None)
            if iv is not None:
                existing_vnums.add(iv)

        changed = False
        for item_def in default_items:
            item_vnum = item_def.get("vnum")
            if item_vnum is None:
                continue

            if item_vnum in existing_vnums:
                continue  # already present — nothing to do

            # Try to create a proper Item object from the items database
            item_obj = self._create_item(item_vnum)
            if item_obj is not None:
                room.items.append(item_obj)
                changed = True
            else:
                logger.warning(
                    "Reset: could not create item vnum %s for room %s",
                    item_vnum, vnum,
                )

        return changed

    # -- Door reset ----------------------------------------------------------

    def reset_doors(self, world, vnum: int, default_doors: dict) -> bool:
        """Reset door / exit states for a room.

        *default_doors* maps direction strings to a dict of properties::

            {"north": {"closed": false, "locked": false}}

        The room's ``exits`` dict may store exit data as an int (target vnum)
        or as a dict with ``to``, ``closed``, ``locked`` keys.  We only modify
        dict-style exits; plain int exits have no door to reset.

        Returns ``True`` if anything changed.
        """
        room = world.rooms.get(vnum)
        if room is None:
            return False

        changed = False
        for direction, door_state in default_doors.items():
            exit_data = room.exits.get(direction)
            if exit_data is None:
                continue

            # Only dict-style exits can carry door state
            if isinstance(exit_data, dict):
                for key in ("closed", "locked"):
                    if key in door_state and exit_data.get(key) != door_state[key]:
                        exit_data[key] = door_state[key]
                        changed = True
            elif isinstance(exit_data, int):
                # Convert to dict-style exit if door defaults require it
                needs_door = door_state.get("closed", False) or door_state.get("locked", False)
                if needs_door:
                    room.exits[direction] = {
                        "to": exit_data,
                        "closed": door_state.get("closed", False),
                        "locked": door_state.get("locked", False),
                    }
                    changed = True

        return changed

    # -- Container reset -----------------------------------------------------

    def reset_containers(self, world, vnum: int, default_containers: dict) -> bool:
        """Refill containers in a room to their default contents.

        *default_containers* maps a container vnum (as string) to a list of
        item dicts that should be inside it::

            {"200": [{"vnum": 101, "name": "Healing Potion"}]}

        Returns ``True`` if anything changed.
        """
        room = world.rooms.get(vnum)
        if room is None:
            return False

        changed = False
        for container_vnum_str, desired_contents in default_containers.items():
            try:
                container_vnum = int(container_vnum_str)
            except (ValueError, TypeError):
                continue

            # Find the container in the room's item list
            container = None
            for item in room.items:
                if getattr(item, "vnum", None) == container_vnum:
                    if getattr(item, "capacity", 0) > 0:
                        container = item
                        break

            if container is None:
                continue

            # Build set of vnums already inside
            contents = getattr(container, "contents", None)
            if contents is None:
                container.contents = []
                contents = container.contents

            existing_vnums = {
                getattr(ci, "vnum", None) for ci in contents
            }

            for ci_def in desired_contents:
                ci_vnum = ci_def.get("vnum")
                if ci_vnum is None or ci_vnum in existing_vnums:
                    continue

                if len(contents) >= container.capacity:
                    break  # container full

                ci_obj = self._create_item(ci_vnum)
                if ci_obj is not None:
                    contents.append(ci_obj)
                    changed = True

        return changed

    # -- Helpers -------------------------------------------------------------

    @staticmethod
    def _create_item(item_vnum: int):
        """Create a fresh Item instance from the global items database.

        Returns an Item object or ``None`` if the vnum is not found.
        """
        try:
            from src.items import get_item_by_vnum
            template = get_item_by_vnum(item_vnum)
            if template is None:
                return None
            # Deep-copy so each placed item is an independent instance
            return copy.deepcopy(template)
        except Exception as exc:
            logger.error("Failed to create item vnum %s: %s", item_vnum, exc)
            return None

    @staticmethod
    def _room_has_combat(room) -> bool:
        """Return True if any player in *room* is currently in combat."""
        try:
            from src.character import State
            for player in room.players:
                if getattr(player, "state", None) is State.COMBAT:
                    return True
        except ImportError:
            pass
        return False

    @staticmethod
    def _notify_players(room) -> None:
        """Send the reset notification to every player in *room*."""
        for player in room.players:
            writer = getattr(player, "_writer", None)
            if writer is not None:
                try:
                    writer.write(RESET_MESSAGE)
                except Exception:
                    pass

    # -- Admin / diagnostic --------------------------------------------------

    def get_status(self) -> str:
        """Return a human-readable status summary."""
        now = time.time()
        lines = ["Area Reset Manager Status:", f"  Enabled: {self.enabled}"]
        areas = self.config.get("areas", {})
        lines.append(f"  Configured areas: {len(areas)}")

        for area_name, area_cfg in areas.items():
            interval = area_cfg.get("reset_interval", DEFAULT_RESET_INTERVAL)
            last = self.last_reset.get(area_name, 0)
            elapsed = now - last
            remaining = max(0, interval - elapsed)
            room_count = len(area_cfg.get("rooms", {}))
            lines.append(
                f"  [{area_name}] interval={interval}s, "
                f"rooms={room_count}, "
                f"next reset in {remaining:.0f}s"
            )

        return "\n".join(lines)

    def force_reset(self, world, area_name: str) -> str:
        """Immediately reset an area regardless of timer.

        Returns a status message.
        """
        areas = self.config.get("areas", {})
        if area_name not in areas:
            return f"Unknown area: '{area_name}'."

        result = self.reset_area(world, area_name)
        return result or f"Area '{area_name}' reset (no changes needed)."

    def set_interval(self, area_name: str, seconds: int) -> str:
        """Change the reset interval for an area and persist it.

        Returns a status message.
        """
        areas = self.config.get("areas", {})
        if area_name not in areas:
            return f"Unknown area: '{area_name}'."

        areas[area_name]["reset_interval"] = seconds
        self._save_config()
        minutes = seconds / 60
        return f"Area '{area_name}' reset interval set to {minutes:.1f} minutes."

    def add_area(self, area_name: str, interval: int = DEFAULT_RESET_INTERVAL) -> str:
        """Register a new area for resets.

        Returns a status message.
        """
        areas = self.config.setdefault("areas", {})
        if area_name in areas:
            return f"Area '{area_name}' already registered."

        areas[area_name] = {
            "reset_interval": interval,
            "rooms": {}
        }
        self.last_reset[area_name] = time.time()
        self._save_config()
        return f"Area '{area_name}' registered with {interval}s reset interval."

    def add_room_reset(self, area_name: str, vnum: int,
                       items: Optional[list] = None,
                       doors: Optional[dict] = None,
                       containers: Optional[dict] = None) -> str:
        """Add or update a room's reset data within an area.

        Returns a status message.
        """
        areas = self.config.get("areas", {})
        area_cfg = areas.get(area_name)
        if area_cfg is None:
            return f"Unknown area: '{area_name}'."

        rooms = area_cfg.setdefault("rooms", {})
        vnum_str = str(vnum)
        room_cfg = rooms.setdefault(vnum_str, {})

        if items is not None:
            room_cfg["items"] = items
        if doors is not None:
            room_cfg["doors"] = doors
        if containers is not None:
            room_cfg["containers"] = containers

        self._save_config()
        return f"Room {vnum} reset data updated in area '{area_name}'."


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_reset_manager: Optional[ResetManager] = None


def get_reset_manager() -> ResetManager:
    """Return the global ResetManager singleton, creating it on first call."""
    global _reset_manager
    if _reset_manager is None:
        _reset_manager = ResetManager()
    return _reset_manager
