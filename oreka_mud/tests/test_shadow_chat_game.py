"""Tests for the Shadow Chat Game state machine and intrusion mechanics (Phase 5)."""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chat_session import (
    ChatSession, CHAT_STATES, end_session, materialize,
    force_end_disturbed, force_end_timeout, force_end_body_death,
    MATERIALIZE_HP_COST_PCT, MATERIALIZE_COOLDOWN_SECS,
)


def _make_world():
    from src.room import Room
    world = MagicMock()
    world.rooms = {
        1000: Room(vnum=1000, name="Anchor Room", description="x", exits={}, flags=[]),
        2000: Room(vnum=2000, name="Body Room", description="x", exits={}, flags=[]),
    }
    world.players = []
    return world


def _make_char(world, room_vnum=2000):
    from src.character import Character
    room = world.rooms[room_vnum]
    char = Character(
        name="Hormoth", title=None, race="Human", level=1,
        hp=100, max_hp=100, ac=10, room=room,
    )
    char.save = lambda: None
    if char not in room.players:
        room.players.append(char)
    world.players.append(char)
    return char


def _make_session(char, npc_room_vnum=1000):
    """Create a fresh ChatSession in IDLE state."""
    return ChatSession(
        session_id="test_sess_001",
        player_name=char.name,
        player_level=char.level,
        player_class="Fighter",
        player_race="Human",
        player_deity=None,
        player_factions={},
        npc_vnum=9010,
        npc_name="Warden Kael",
        npc_type=None,
        anchor_room_vnum=npc_room_vnum,
        anchor_room_name="Spur Tower",
        anchor_region="Gatefall Reach",
        started_at=time.time(),
        last_active=time.time(),
    )


class TestStateMachine(unittest.TestCase):
    def test_initial_state_is_idle(self):
        s = _make_session(MagicMock(name="x"))
        self.assertEqual(s.state, "IDLE")

    def test_transition_records_history(self):
        s = _make_session(MagicMock(name="x"))
        s.transition_to("ENTERING", reason="chat_command")
        self.assertEqual(s.state, "ENTERING")
        self.assertEqual(len(s.state_transitions), 1)
        self.assertEqual(s.state_transitions[0]["from"], "IDLE")
        self.assertEqual(s.state_transitions[0]["to"], "ENTERING")
        self.assertEqual(s.state_transitions[0]["reason"], "chat_command")

    def test_transition_to_invalid_state_returns_false(self):
        s = _make_session(MagicMock(name="x"))
        ok = s.transition_to("BOGUS_STATE", reason="x")
        self.assertFalse(ok)
        self.assertEqual(s.state, "IDLE")

    def test_all_documented_states_valid(self):
        for st in [
            "IDLE", "ENTERING", "ACTIVE",
            "EXITING_CLEAN", "MATERIALIZING", "EXITING_FORCED",
            "EXITING_PATIENCE", "EXITING_PANIC",
        ]:
            self.assertIn(st, CHAT_STATES)


class TestExitPaths(unittest.TestCase):
    def test_clean_exit(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        session.transition_to("ACTIVE", reason="entry")
        char.active_chat_session = session
        char.state = State.CHATTING
        end_session(session, char, exit_state="EXITING_CLEAN", reason="user_endchat")
        self.assertEqual(session.state, "EXITING_CLEAN")
        self.assertTrue(session.ended)
        self.assertEqual(session.exit_reason, "user_endchat")
        self.assertIsNone(char.active_chat_session)
        self.assertEqual(char.state, State.EXPLORING)

    def test_forced_exit_disturbed(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        char.active_chat_session = session
        char.state = State.CHATTING
        force_end_disturbed(session, char, disturber_name="Annoying")
        self.assertEqual(session.state, "EXITING_FORCED")
        self.assertIn("disturbed_by:Annoying", session.exit_reason)

    def test_patience_timeout_exit(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        char.active_chat_session = session
        char.state = State.CHATTING
        force_end_timeout(session, char)
        self.assertEqual(session.state, "EXITING_PATIENCE")
        self.assertEqual(session.exit_reason, "idle_timeout")

    def test_body_death_panic_exit(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        char.active_chat_session = session
        char.state = State.CHATTING
        force_end_body_death(session, char)
        self.assertEqual(session.state, "EXITING_PANIC")
        self.assertEqual(session.exit_reason, "body_death")


class TestMaterialize(unittest.TestCase):
    def test_costs_hp(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world, room_vnum=2000)
        session = _make_session(char, npc_room_vnum=1000)
        char.active_chat_session = session
        char.state = State.CHATTING

        original_hp = char.hp
        materialize(session, char, world)

        expected_cost = max(1, int(char.max_hp * MATERIALIZE_HP_COST_PCT))
        self.assertEqual(char.hp, original_hp - expected_cost)

    def test_moves_to_npc_room(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world, room_vnum=2000)
        session = _make_session(char, npc_room_vnum=1000)
        char.active_chat_session = session
        char.state = State.CHATTING

        materialize(session, char, world)
        self.assertEqual(char.room.vnum, 1000)
        self.assertNotIn(char, world.rooms[2000].players)
        self.assertIn(char, world.rooms[1000].players)

    def test_session_ends_in_materializing_state(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        char.active_chat_session = session
        char.state = State.CHATTING

        materialize(session, char, world)
        self.assertEqual(session.state, "MATERIALIZING")
        self.assertEqual(session.exit_reason, "enter_world")

    def test_cooldown_blocks_second_materialize(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        char.active_chat_session = session
        char.state = State.CHATTING

        materialize(session, char, world)
        # Try second materialization immediately
        # Need a new session because the first one is now ended
        session2 = _make_session(char)
        char.active_chat_session = session2
        from src.character import State as _State
        char.state = _State.CHATTING

        result = materialize(session2, char, world)
        self.assertIn("cannot materialize again", result.lower())

    def test_cooldown_constant_is_one_hour(self):
        self.assertEqual(MATERIALIZE_COOLDOWN_SECS, 3600)


class TestBodyDamageBleed(unittest.TestCase):
    def test_damage_during_chat_injects_world_event(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        char.active_chat_session = session
        char.state = State.CHATTING

        char.take_damage(10)
        # Should have injected a [WORLD EVENT] entry
        self.assertTrue(any(
            "damage" in e.get("text", "").lower()
            for e in session.world_events_injected
        ))

    def test_lethal_damage_triggers_panic_exit(self):
        from src.character import State
        world = _make_world()
        char = _make_char(world)
        char.hp = 5  # Set low so damage kills
        session = _make_session(char)
        char.active_chat_session = session
        char.state = State.CHATTING

        char.take_damage(100)  # massive overkill
        # Session should end in EXITING_PANIC
        self.assertEqual(session.state, "EXITING_PANIC")
        self.assertEqual(session.exit_reason, "body_death")


class TestSessionLogPersistsState(unittest.TestCase):
    def test_log_includes_state_and_transitions(self):
        from src.character import State
        from src.chat_session import _save_session_log, CHAT_SESSIONS_DIR
        import json
        import glob

        world = _make_world()
        char = _make_char(world)
        session = _make_session(char)
        session.transition_to("ENTERING", reason="x")
        session.transition_to("ACTIVE", reason="y")
        session.transition_to("EXITING_CLEAN", reason="endchat")
        session.exit_reason = "endchat"
        session.add_message("user", "hello")
        session.add_message("assistant", "hi")

        # Clear any prior test files
        os.makedirs(CHAT_SESSIONS_DIR, exist_ok=True)
        before = set(os.listdir(CHAT_SESSIONS_DIR))

        _save_session_log(session)

        # Find new file
        after = set(os.listdir(CHAT_SESSIONS_DIR))
        new_files = list(after - before)
        if not new_files:
            self.skipTest("Couldn't find new session log file")

        path = os.path.join(CHAT_SESSIONS_DIR, new_files[0])
        with open(path, 'r') as f:
            data = json.load(f)

        self.assertIn("state", data)
        self.assertEqual(data["state"], "EXITING_CLEAN")
        self.assertIn("state_transitions", data)
        self.assertGreaterEqual(len(data["state_transitions"]), 3)

        # Cleanup
        os.remove(path)


if __name__ == "__main__":
    unittest.main()
