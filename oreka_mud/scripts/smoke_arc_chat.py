#!/usr/bin/env python3
"""Smoke test arc state persistence through chat actions.

Simulates a 5-step arc-aware conversation:
  1. Player has untouched arc sheet
  2. NPC emits check_arc_item action
  3. Engine flips state
  4. Player saves character; reloads
  5. New session sees the updated state in the prompt

Does not call the LLM — feeds synthetic action lists directly into
execute_chat_actions to verify wiring.

Exit code 0 = pass.
"""
import asyncio
import os
import sys
import tempfile
from unittest.mock import MagicMock

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


def main():
    from src.ai import execute_chat_actions, _build_arc_context_block
    from src.ai_schemas.arc_sheet import ArcSheet, ChecklistItem
    from src.character import Character
    from src.room import Room

    print("Step 1: Build a player with an untouched arc sheet")
    room = Room(vnum=1000, name="Test", description="x", exits={}, flags=[])
    char = Character(
        name="TestPlayer", title=None, race="Human", level=1,
        hp=100, max_hp=100, ac=10, room=room,
    )
    char.save = lambda: None
    arc = ArcSheet(
        arc_id="quiet_graft", title="The Quiet Graft",
        checklist=[
            ChecklistItem(id="met_maeren", category="npc_met"),
            ChecklistItem(id="met_vaerix", category="npc_met"),
        ],
    )
    char.arc_sheets["quiet_graft"] = arc
    print(f"  initial state: arc.status={arc.status}, met_maeren={arc.get_item('met_maeren').state}")
    assert arc.status == "untouched"
    assert arc.get_item("met_maeren").state == "unchecked"

    print("\nStep 2: NPC emits check_arc_item action")
    # Set up an NPC with arcs_known
    mob = MagicMock()
    mob.vnum = 9010
    mob.name = "Test NPC"
    mob.alive = True
    mob.ai_persona = {"arcs_known": ["quiet_graft"]}
    room.mobs.append(mob)
    session = MagicMock()
    session.npc_vnum = 9010
    session.npc_name = "Test NPC"

    actions = [{
        "type": "check_arc_item",
        "arc_id": "quiet_graft",
        "item_id": "met_maeren",
        "detail": {"trust": "warm", "topic": "the road"},
    }]
    asyncio.run(execute_chat_actions(actions, char, session))

    print("\nStep 3: Verify state flipped")
    item = char.get_checklist_item("quiet_graft", "met_maeren")
    print(f"  met_maeren.state={item.state}")
    print(f"  met_maeren.detail={item.detail}")
    print(f"  arc.status={arc.status}")
    assert item.state == "detailed", f"Expected detailed, got {item.state}"
    assert item.detail.get("trust") == "warm"
    assert arc.status == "aware", f"Expected aware, got {arc.status}"

    print("\nStep 4: Round-trip through save/load")
    char_dict = char.to_dict()
    char2 = Character.from_dict(char_dict)
    item2 = char2.get_checklist_item("quiet_graft", "met_maeren")
    print(f"  reloaded met_maeren.state={item2.state}")
    print(f"  reloaded arc.status={char2.get_arc('quiet_graft').status}")
    assert item2.state == "detailed"
    assert item2.detail.get("trust") == "warm"
    assert char2.get_arc("quiet_graft").status == "aware"

    print("\nStep 5: New conversation prompt reflects the state")
    persona = {
        "arcs_known": ["quiet_graft"],
        "arc_reactions": [
            {
                "when": "met_maeren.detail.trust == warm",
                "flavor": "Reference her warmth.",
                "loudness": "subtle",
            }
        ],
    }
    block = _build_arc_context_block(persona, char2)
    print(f"  arc context block:\n{block}")
    assert "Quiet Graft" in block, "Block should reference the arc"
    assert "Reference her warmth" in block, "Block should include matching flavor"

    print("\n[OK] Arc state persistence smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
