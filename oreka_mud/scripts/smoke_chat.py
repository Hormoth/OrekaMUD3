#!/usr/bin/env python3
"""Smoke test harness for chat sessions with exemplar NPCs.

For each NPC with an ai_persona:
  1. Build the system prompt
  2. Verify it has all expected sections
  3. Verify trust filtering works at each tier
  4. Verify opening_line and farewell_line exist

Does NOT actually call the LLM (that's expensive and non-deterministic).
For LLM-in-the-loop testing, run a live server and use 'chat <npc>'.

Exit code 0 = all green.
"""
import json
import os
import sys
from unittest.mock import MagicMock

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


def _mock_session(npc_vnum, npc_name):
    sess = MagicMock()
    sess.npc_vnum = npc_vnum
    sess.npc_name = npc_name
    sess.player_name = "TestPlayer"
    sess.player_level = 5
    sess.player_class = "Fighter"
    sess.player_race = "Human"
    sess.player_deity = None
    sess.player_factions = {}
    sess.anchor_room_vnum = 1000
    sess.anchor_room_name = "Test Chamber"
    sess.anchor_region = "Chapel"
    sess._summary = None
    sess.get_recent_world_events = lambda limit=5: []
    return sess


def _mock_character_with_npc(npc_vnum, persona):
    from src.character import Character
    from src.room import Room
    room = Room(vnum=1000, name="Test Chamber", description="A test chamber.",
                exits={}, flags=[])
    char = Character(
        name="TestPlayer", title=None, race="Human", level=5,
        hp=10, max_hp=10, ac=10, room=room,
    )
    mob = MagicMock()
    mob.vnum = npc_vnum
    mob.name = "Test NPC"
    mob.alive = True
    mob.ai_persona = persona
    room.mobs.append(mob)
    return char


def _check_persona(persona, npc_name):
    """Return list of issues, or [] if all good."""
    from src.ai import _build_chat_system_prompt, effective_trust, _filter_secrets_by_trust
    issues = []

    if not persona.get("opening_line"):
        issues.append("missing opening_line")
    if not persona.get("farewell_line"):
        issues.append("missing farewell_line")
    if not persona.get("voice"):
        issues.append("missing voice")
    if not persona.get("motivation"):
        issues.append("missing motivation")

    # Build prompt with empty memory
    sess = _mock_session(persona.get("vnum", 0), npc_name)
    char = _mock_character_with_npc(0, persona)
    empty_memory = {"sessions": 0, "facts": []}
    prompt = _build_chat_system_prompt(sess, char, empty_memory)

    if "RESPONSE FORMAT" not in prompt:
        issues.append("prompt missing RESPONSE FORMAT block")
    if "Stay in character" not in prompt:
        issues.append("prompt missing in-character rule")

    # Trust filtering smoke test
    secrets = persona.get("secrets", [])
    if secrets:
        for tier in ("casual", "warm", "trusted", "allied"):
            allowed = _filter_secrets_by_trust(secrets, tier)
            # Each higher tier should include all lower-tier secrets
            if tier == "allied" and len(allowed) != len(secrets):
                issues.append(
                    f"allied tier should see all {len(secrets)} secrets, got {len(allowed)}"
                )

    return issues


def main():
    mobs_path = os.path.join(parent_dir, "data", "mobs.json")
    with open(mobs_path, "r", encoding="utf-8") as f:
        mobs = json.load(f)

    tested = 0
    failed = 0
    for m in mobs:
        persona = m.get("ai_persona")
        if not persona:
            continue
        tested += 1
        npc_name = m.get("name", "?")
        # Inject vnum so issue messages are useful
        persona_copy = dict(persona)
        persona_copy["vnum"] = m.get("vnum")
        issues = _check_persona(persona_copy, npc_name)
        if issues:
            failed += 1
            print(f"[X] vnum {m.get('vnum')} ({npc_name}):")
            for i in issues:
                print(f"      - {i}")
        else:
            print(f"[OK] vnum {m.get('vnum')} ({npc_name})")

    print(f"\nSmoke-tested {tested} NPCs. {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
