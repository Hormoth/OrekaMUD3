#!/usr/bin/env python3
"""Audit chat system prompt lengths.

Builds the chat system prompt for every NPC with an ai_persona using
mock player + room data, and reports the token estimate. Fails if any
single prompt exceeds 2500 tokens or arc section exceeds 800 tokens.

Token estimate uses 4 chars/token heuristic — close enough for budgeting.

Usage:
  python scripts/audit_prompt_lengths.py
  python scripts/audit_prompt_lengths.py --arc-section
"""
import json
import os
import sys
from unittest.mock import MagicMock

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


CHARS_PER_TOKEN = 4
PROMPT_BUDGET_TOKENS = 2500
ARC_SECTION_BUDGET_TOKENS = 800


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


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
    """Build a minimal character + room with the NPC inside."""
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


def main():
    from src.ai import _build_chat_system_prompt, _build_arc_context_block

    arc_only = "--arc-section" in sys.argv

    mobs_path = os.path.join(parent_dir, "data", "mobs.json")
    with open(mobs_path, "r", encoding="utf-8") as f:
        mobs = json.load(f)

    audited = 0
    over_budget = []
    arc_over_budget = []

    for m in mobs:
        persona = m.get("ai_persona")
        if not persona:
            continue
        audited += 1
        npc_vnum = m.get("vnum", 0)
        npc_name = m.get("name", "?")

        char = _mock_character_with_npc(npc_vnum, persona)
        sess = _mock_session(npc_vnum, npc_name)
        empty_memory = {"sessions": 0, "facts": []}

        try:
            full_prompt = _build_chat_system_prompt(sess, char, empty_memory)
        except Exception as e:
            over_budget.append((npc_vnum, npc_name, f"build failed: {e}"))
            continue

        full_tokens = estimate_tokens(full_prompt)
        arc_block = _build_arc_context_block(persona, char)
        arc_tokens = estimate_tokens(arc_block) if arc_block else 0

        if not arc_only:
            print(f"  vnum {npc_vnum:>5} ({npc_name[:35]:<35}) "
                  f"full: {full_tokens:>4}t  arc: {arc_tokens:>3}t")

        if full_tokens > PROMPT_BUDGET_TOKENS:
            over_budget.append((npc_vnum, npc_name, full_tokens))
        if arc_tokens > ARC_SECTION_BUDGET_TOKENS:
            arc_over_budget.append((npc_vnum, npc_name, arc_tokens))

    print(f"\nAudited {audited} personas.")
    print(f"  Full prompt budget: {PROMPT_BUDGET_TOKENS} tokens")
    print(f"  Arc section budget: {ARC_SECTION_BUDGET_TOKENS} tokens")

    rc = 0
    if over_budget:
        print(f"\n[X] {len(over_budget)} prompts over budget:")
        for vnum, name, tokens in over_budget:
            print(f"  vnum {vnum} ({name}): {tokens} tokens")
        rc = 1
    if arc_over_budget:
        print(f"\n[X] {len(arc_over_budget)} arc sections over budget:")
        for vnum, name, tokens in arc_over_budget:
            print(f"  vnum {vnum} ({name}): {tokens} tokens")
        rc = 1
    if rc == 0:
        print("[OK] All prompts within budget.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
