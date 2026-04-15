"""Tests for the check_arc_item and set_arc_status structured actions (Phase 2)."""

import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai import execute_chat_actions
from src.ai_schemas.arc_sheet import ArcSheet, ChecklistItem


def _make_session(npc_vnum=9010, npc_name="Warden Kael"):
    session = MagicMock()
    session.npc_vnum = npc_vnum
    session.npc_name = npc_name
    return session


def _make_char_with_persona_and_arc(arcs_known=None, arc_id="quiet_graft", item_id="met_maeren"):
    """Build a character with a persona-equipped NPC in their room and an arc sheet."""
    from src.character import Character
    from src.room import Room
    room = Room(vnum=1, name="x", description="x", exits={}, flags=[])
    char = Character(
        name="Test", title=None, race="Human", level=1,
        hp=10, max_hp=10, ac=10, room=room,
    )

    # Set up arc sheet
    char.arc_sheets[arc_id] = ArcSheet(
        arc_id=arc_id, title="Test Arc",
        checklist=[ChecklistItem(id=item_id, category="npc_met")],
    )

    # Add a mob with persona to the room
    mob = MagicMock()
    mob.vnum = 9010
    mob.name = "Warden Kael"
    mob.alive = True
    mob.ai_persona = {"arcs_known": arcs_known if arcs_known is not None else [arc_id]}
    room.mobs.append(mob)

    return char


class TestCheckArcItemAction(unittest.TestCase):
    def _run_actions(self, actions, character, session):
        """Helper to run execute_chat_actions in a sync test."""
        return asyncio.run(execute_chat_actions(actions, character, session))

    def test_happy_path(self):
        char = _make_char_with_persona_and_arc()
        session = _make_session()
        actions = [{
            "type": "check_arc_item",
            "arc_id": "quiet_graft",
            "item_id": "met_maeren",
        }]

        self._run_actions(actions, char, session)

        item = char.get_checklist_item("quiet_graft", "met_maeren")
        self.assertEqual(item.state, "checked")
        # Status auto-promoted
        self.assertEqual(char.get_arc("quiet_graft").status, "aware")

    def test_with_detail(self):
        char = _make_char_with_persona_and_arc()
        session = _make_session()
        actions = [{
            "type": "check_arc_item",
            "arc_id": "quiet_graft",
            "item_id": "met_maeren",
            "detail": {"trust": "warm", "topic": "the road"},
        }]

        self._run_actions(actions, char, session)

        item = char.get_checklist_item("quiet_graft", "met_maeren")
        self.assertEqual(item.state, "detailed")
        self.assertEqual(item.detail["trust"], "warm")
        self.assertEqual(item.detail["topic"], "the road")

    def test_rejected_when_arc_not_in_arcs_known(self):
        char = _make_char_with_persona_and_arc(arcs_known=[])  # NPC knows no arcs
        session = _make_session()
        actions = [{
            "type": "check_arc_item",
            "arc_id": "quiet_graft",
            "item_id": "met_maeren",
        }]

        self._run_actions(actions, char, session)

        # Item should NOT have flipped
        item = char.get_checklist_item("quiet_graft", "met_maeren")
        self.assertEqual(item.state, "unchecked")

    def test_rejected_when_item_id_doesnt_exist(self):
        char = _make_char_with_persona_and_arc()
        session = _make_session()
        actions = [{
            "type": "check_arc_item",
            "arc_id": "quiet_graft",
            "item_id": "nonexistent_item",
        }]

        self._run_actions(actions, char, session)

        # Original item still unchecked
        item = char.get_checklist_item("quiet_graft", "met_maeren")
        self.assertEqual(item.state, "unchecked")

    def test_rejected_when_arc_id_doesnt_exist(self):
        char = _make_char_with_persona_and_arc()
        session = _make_session()
        actions = [{
            "type": "check_arc_item",
            "arc_id": "nonexistent_arc",
            "item_id": "x",
        }]

        # Should not crash
        self._run_actions(actions, char, session)
        # Existing arc unaffected
        item = char.get_checklist_item("quiet_graft", "met_maeren")
        self.assertEqual(item.state, "unchecked")

    def test_missing_args(self):
        char = _make_char_with_persona_and_arc()
        session = _make_session()
        actions = [{"type": "check_arc_item"}]  # No arc_id or item_id
        self._run_actions(actions, char, session)
        item = char.get_checklist_item("quiet_graft", "met_maeren")
        self.assertEqual(item.state, "unchecked")


class TestSetArcStatusAction(unittest.TestCase):
    def _run_actions(self, actions, character, session):
        return asyncio.run(execute_chat_actions(actions, character, session))

    def test_set_to_active(self):
        char = _make_char_with_persona_and_arc()
        session = _make_session()
        actions = [{
            "type": "set_arc_status",
            "arc_id": "quiet_graft",
            "status": "active",
        }]
        self._run_actions(actions, char, session)
        self.assertEqual(char.get_arc("quiet_graft").status, "active")

    def test_set_to_resolved_with_resolution(self):
        char = _make_char_with_persona_and_arc()
        session = _make_session()
        actions = [{
            "type": "set_arc_status",
            "arc_id": "quiet_graft",
            "status": "resolved",
            "resolution": "graft_took",
        }]
        self._run_actions(actions, char, session)
        arc = char.get_arc("quiet_graft")
        self.assertEqual(arc.status, "resolved")
        self.assertEqual(arc.resolution, "graft_took")

    def test_rejected_for_unknown_arc(self):
        char = _make_char_with_persona_and_arc(arcs_known=[])
        session = _make_session()
        actions = [{
            "type": "set_arc_status",
            "arc_id": "quiet_graft",
            "status": "active",
        }]
        self._run_actions(actions, char, session)
        # Status unchanged
        self.assertEqual(char.get_arc("quiet_graft").status, "untouched")


if __name__ == "__main__":
    unittest.main()
