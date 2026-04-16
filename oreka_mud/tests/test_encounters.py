"""Tests for the regional random-encounter system."""

from __future__ import annotations

import os
import sys
import time
import pytest

# Make ``src.*`` imports work whether tests are run from the repo root
# or from ``oreka_mud/``.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import encounters as enc  # noqa: E402


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------

class FakeRoom:
    def __init__(self, vnum, flags=None, exits=None):
        self.vnum = vnum
        self.flags = list(flags or [])
        self.exits = dict(exits or {})
        self.mobs = []
        self.players = []


class FakePlayer:
    def __init__(self, name, room, level=5):
        self.name = name
        self.room = room
        self.level = level
        self.is_ai = False
        room.players.append(self)


class FakeWorld:
    def __init__(self, rooms):
        self.rooms = {r.vnum: r for r in rooms}
        self.mobs = {}
        self.players = []


def make_corridor(n=8, region_vnums=None, base_vnum=1000, flags=("forest",)):
    """Build a chain of n rooms connected east<->west."""
    rooms = []
    for i in range(n):
        v = base_vnum + i
        r = FakeRoom(v, flags=flags)
        rooms.append(r)
    for i, r in enumerate(rooms):
        if i > 0:
            r.exits["west"] = rooms[i - 1].vnum
        if i < len(rooms) - 1:
            r.exits["east"] = rooms[i + 1].vnum
    if region_vnums is not None:
        region_vnums.update(r.vnum for r in rooms)
    return rooms


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

class TestEligibility:
    def test_safe_room_excluded(self):
        assert not enc.is_eligible_room(FakeRoom(1, flags=["safe", "forest"]))

    def test_indoor_excluded(self):
        assert not enc.is_eligible_room(FakeRoom(1, flags=["indoor"]))

    def test_shop_excluded(self):
        assert not enc.is_eligible_room(FakeRoom(1, flags=["shop"]))

    def test_inn_tavern_excluded(self):
        assert not enc.is_eligible_room(FakeRoom(1, flags=["tavern"]))
        assert not enc.is_eligible_room(FakeRoom(1, flags=["inn"]))

    def test_wilderness_eligible(self):
        assert enc.is_eligible_room(FakeRoom(1, flags=["forest", "dangerous"]))
        assert enc.is_eligible_room(FakeRoom(1, flags=["plains"]))
        assert enc.is_eligible_room(FakeRoom(1, flags=["desert"]))


# ---------------------------------------------------------------------------
# Pathfinding
# ---------------------------------------------------------------------------

class TestPathfinding:
    def test_bfs_two_rooms_apart(self):
        rooms = make_corridor(5)
        world = FakeWorld(rooms)
        path = enc.bfs_path(world, rooms[0].vnum, rooms[2].vnum)
        assert path == [rooms[0].vnum, rooms[1].vnum, rooms[2].vnum]

    def test_bfs_no_path(self):
        # Two disconnected rooms
        a = FakeRoom(1)
        b = FakeRoom(2)
        world = FakeWorld([a, b])
        assert enc.bfs_path(world, 1, 2) is None

    def test_find_spawn_room_two_away(self):
        region_vnums = set()
        rooms = make_corridor(7, region_vnums)
        world = FakeWorld(rooms)
        # Target sits at index 3; we want a spawn 2 rooms away.
        target_vnum = rooms[3].vnum
        spawn = enc.find_spawn_room(world, target_vnum, region_vnums)
        assert spawn in {rooms[1].vnum, rooms[5].vnum}

    def test_find_spawn_room_skips_excluded(self):
        region_vnums = set()
        rooms = make_corridor(7, region_vnums, flags=("forest",))
        # Make both 2-away rooms unsafe (`safe` flag) -> should fall back
        # to distance-1 or distance+1.
        rooms[1].flags = ["safe"]
        rooms[5].flags = ["safe"]
        world = FakeWorld(rooms)
        spawn = enc.find_spawn_room(world, rooms[3].vnum, region_vnums)
        # Distance-1 (rooms[2] or rooms[4]) or distance+1 (rooms[0] or rooms[6])
        assert spawn in {rooms[0].vnum, rooms[2].vnum,
                         rooms[4].vnum, rooms[6].vnum}


# ---------------------------------------------------------------------------
# Manager: creature selection and spawning
# ---------------------------------------------------------------------------

class TestEncounterManager:
    def setup_method(self):
        # Use the real loaded tables -- they're fast to load and we want
        # to confirm the production data behaves.
        self.mgr = enc.EncounterManager()
        self.mgr.load()

    def test_tables_loaded_for_seven_regions(self):
        expected = {"kinsweave", "eternalsteppe", "infinitedesert",
                    "gatefall", "deepwater", "tidebloom", "twinrivers"}
        assert set(self.mgr.tables) == expected

    def test_pick_creature_within_apl_band(self):
        # APL 5 should yield something in CR 3-7 from gatefall.
        c = self.mgr.pick_creature("gatefall", apl=5)
        assert c is not None
        assert 3 <= float(c["cr"]) <= 7

    def test_pick_creature_low_apl_falls_back(self):
        # APL 1 -- band is 0-3.  Should always find something.
        for region in self.mgr.tables:
            assert self.mgr.pick_creature(region, apl=1) is not None

    def test_pick_creature_returns_none_above_table(self):
        # No CR 30 creatures exist anywhere.
        assert self.mgr.pick_creature("twinrivers", apl=30) is None

    def test_force_encounter_rejects_safe_room(self):
        # Build a fake target sitting in a safe room.
        # First, find a kinsweave vnum, then create a FakeRoom with safe flag.
        kw_vnum = next(iter(self.mgr.region_map["kinsweave"]))
        room = FakeRoom(kw_vnum, flags=["safe"])
        player = FakePlayer("Test", room)
        world = FakeWorld([room])
        ok, msg = self.mgr.force_encounter(world, "kinsweave", player)
        assert not ok
        assert "not in an encounter-eligible" in msg

    def test_force_encounter_rejects_wrong_region(self):
        # Player in a kinsweave room but we ask for gatefall.
        kw_vnum = next(iter(self.mgr.region_map["kinsweave"]))
        room = FakeRoom(kw_vnum, flags=["forest"])
        player = FakePlayer("Test", room)
        world = FakeWorld([room])
        ok, msg = self.mgr.force_encounter(world, "gatefall", player)
        assert not ok
        assert "not currently in gatefall" in msg


# ---------------------------------------------------------------------------
# Stalker behavior
# ---------------------------------------------------------------------------

class TestStalker:
    def test_solo_player_pursued_while_moving(self):
        """A lone player is attacked while running -- stalker keeps closing."""
        mgr = enc.EncounterManager()
        mgr._loaded = True

        rooms = make_corridor(5)
        world = FakeWorld(rooms)
        target = FakePlayer("Solo", rooms[0])
        world.players.append(target)

        # Spawn a fake mob at rooms[2] -- 2 away from target.
        from src.mob import Mob
        mob = Mob(vnum=999001, name="Stalker Wolf", level=2,
                  hp_dice=(2, 8, 0), ac=14, damage_dice=(1, 6, 1))
        mob.room_vnum = rooms[2].vnum
        rooms[2].mobs.append(mob)
        world.mobs[mob.vnum] = mob

        s = enc.Stalker(mob, "kinsweave", target, [target])
        mgr.active = [s]

        # First tick: solo, mob should advance toward target.
        mgr.tick_stalkers(world)
        assert mob.room_vnum == rooms[1].vnum  # advanced one step

        # Move target to rooms[1] (player running) -- mob still closes.
        rooms[0].players.remove(target)
        target.room = rooms[1]
        rooms[1].players.append(target)

        mgr.tick_stalkers(world)
        # Solo player: mob should have engaged regardless of movement.
        assert s.engaged

    def test_party_pauses_when_moving(self):
        """A multi-player party that moves causes the stalker to wait."""
        mgr = enc.EncounterManager()
        mgr._loaded = True

        rooms = make_corridor(5)
        world = FakeWorld(rooms)
        a = FakePlayer("A", rooms[0])
        b = FakePlayer("B", rooms[0])
        world.players.extend([a, b])

        from src.mob import Mob
        mob = Mob(vnum=999002, name="Stalker Wolf", level=2,
                  hp_dice=(2, 8, 0), ac=14, damage_dice=(1, 6, 1))
        mob.room_vnum = rooms[2].vnum
        rooms[2].mobs.append(mob)
        world.mobs[mob.vnum] = mob

        s = enc.Stalker(mob, "kinsweave", a, [a, b])
        mgr.active = [s]

        # Move the party (target leader) before first tick.
        rooms[0].players.remove(a)
        a.room = rooms[1]
        rooms[1].players.append(a)

        # First tick: party moved -> mob should hold ground.
        mgr.tick_stalkers(world)
        assert mob.room_vnum == rooms[2].vnum  # did NOT advance

        # Second tick with party stationary: mob advances.
        mgr.tick_stalkers(world)
        assert mob.room_vnum == rooms[1].vnum

    def test_engagement_starts_combat(self):
        """When a stalker enters the target's room it auto-initiates combat."""
        from src.combat import get_combat, end_combat
        from src.mob import Mob

        mgr = enc.EncounterManager()
        mgr._loaded = True

        # 3-room corridor so the stalker is 1 room away and closes to 0.
        rooms = make_corridor(3)
        world = FakeWorld(rooms)
        target = FakePlayer("Hero", rooms[0])
        world.players.append(target)

        # Give player minimum fields combat needs (ability scores, hp, etc.)
        # The combat system reads ability_scores on entities -- for our fake
        # player we rely on Character behavior via getattr fallbacks.  A
        # bare FakePlayer with level/name is enough for start_combat to
        # roll initiative and register both combatants.
        target.ability_scores = {"Str": 10, "Dex": 12, "Con": 10,
                                 "Int": 10, "Wis": 10, "Cha": 10}
        target.hp = 20
        target.max_hp = 20
        target.alive = True

        mob = Mob(vnum=999010, name="Stalker Wolf", level=2,
                  hp_dice=(2, 8, 0), ac=14, damage_dice=(1, 6, 1))
        mob.room_vnum = rooms[1].vnum  # 1 room away
        rooms[1].mobs.append(mob)
        world.mobs[mob.vnum] = mob

        # Clear any lingering combat in these test rooms
        for r in rooms:
            try:
                end_combat(r)
            except Exception:
                pass

        s = enc.Stalker(mob, "kinsweave", target, [target])
        mgr.active = [s]

        try:
            mgr.tick_stalkers(world)
            # Solo target, 1 room away -> stalker advances into rooms[0]
            # and engages, kicking off combat.
            assert s.engaged is True
            combat = get_combat(rooms[0])
            assert combat is not None
            assert combat.is_active
            assert mob in combat.combatants
            assert target in combat.combatants
        finally:
            # Clean up so we don't leak combat state into other tests.
            try:
                end_combat(rooms[0])
            except Exception:
                pass

    def test_stalker_expires_after_lifetime(self):
        mgr = enc.EncounterManager()
        mgr._loaded = True
        rooms = make_corridor(5)
        world = FakeWorld(rooms)
        target = FakePlayer("Slow", rooms[0])
        world.players.append(target)

        from src.mob import Mob
        mob = Mob(vnum=999003, name="Stalker", level=1,
                  hp_dice=(1, 8, 0), ac=10, damage_dice=(1, 4, 0))
        # Park mob far away so it can't reach target quickly.
        mob.room_vnum = rooms[4].vnum
        rooms[4].mobs.append(mob)
        world.mobs[mob.vnum] = mob

        s = enc.Stalker(mob, "kinsweave", target, [target])
        s.spawned_at = time.time() - (enc.STALKER_MAX_LIFETIME_SECS + 1)
        mgr.active = [s]

        msgs = mgr.tick_stalkers(world)
        # Mob despawned, message emitted, stalker dropped.
        assert any("loses the trail" in m for m in msgs)
        assert mob.vnum not in world.mobs
        assert mgr.active == []
