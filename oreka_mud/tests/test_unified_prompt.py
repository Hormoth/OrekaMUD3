"""Tests for the unified NPC prompt builder.

Verifies that talk, rpsay, and chat modes all produce prompts containing
the same enrichment blocks (PC sheet, room ambience, environment, arc
context, trust-filtered secrets, NPC memory).
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai import build_unified_npc_prompt, PROMPT_MODES
from src.ai_schemas import (
    AiPersona, ArcReaction, ArcSheet, ChecklistItem, PcSheet, RoomAmbience,
)


def _make_room(with_ambience=True):
    from src.room import Room
    room = Room(vnum=1000, name="Spur Tower", description="A scholar's redoubt.",
                exits={}, flags=[])
    if with_ambience:
        room.ambience = RoomAmbience(
            mood="watchful",
            sounds=["a distant chime"],
            smells=["wet stone"],
            ambient_details=["motes drift in the lamplight"],
        )
    return room


def _make_character(with_rp_sheet=True, with_arc=True):
    from src.character import Character
    room = _make_room()
    char = Character(
        name="Hormoth", title=None, race="Human", level=5,
        hp=100, max_hp=100, ac=10, room=room,
    )
    char.save = lambda: None
    if with_rp_sheet:
        char.rp_sheet = PcSheet(
            bio="A scribe from Custos who fears fire.",
            personality="Cautious, observant, slow to trust.",
            goals=["find the missing ledger"],
            quirks=["always carries ink"],
        )
    if with_arc:
        char.arc_sheets["quiet_graft"] = ArcSheet(
            arc_id="quiet_graft", title="The Quiet Graft", status="aware",
            checklist=[
                ChecklistItem(id="met_maeren", category="npc_met",
                              state="detailed", detail={"trust": "warm"}),
            ],
        )
    return char, room


def _make_npc(with_persona=True, with_arc=True):
    npc = MagicMock()
    npc.name = "Warden Kael Ridgeborn"
    npc.vnum = 9010
    npc.type_ = "Humanoid"
    npc.dialogue = "Walk watchful."
    npc.alive = True
    if with_persona:
        persona = {
            "voice": "Low and measured.",
            "motivation": "Keep the road open.",
            "speech_style": "clipped",
            "knowledge_domains": ["frontier"],
            "secrets": [
                "casual:I keep the road.",
                "warm:Three scouts lost last moon.",
                "trusted:The Breach spreads down, not east.",
                "allied:I was at Hillwatch the night it fell.",
            ],
            "lore_tags": ["gatefall_reach"],
        }
        if with_arc:
            persona["arcs_known"] = ["quiet_graft"]
            persona["arc_reactions"] = [
                {
                    "when": "met_maeren.detail.trust == warm",
                    "flavor": "Reference her warmth.",
                    "loudness": "subtle",
                }
            ]
        npc.ai_persona = persona
    else:
        npc.ai_persona = None
    return npc


class TestUnifiedBuilderAllModes(unittest.TestCase):
    """Verify all 3 modes produce the same enrichment blocks."""

    def setUp(self):
        self.char, self.room = _make_character()
        self.npc = _make_npc()
        # Place the NPC in the room (used by chat session resolver)
        self.room.mobs.append(self.npc)

    def _build(self, mode, **kwargs):
        return build_unified_npc_prompt(
            npc=self.npc,
            character=self.char,
            room=self.room,
            mode=mode,
            **kwargs,
        )

    def test_talk_includes_persona(self):
        prompt = self._build("talk")
        self.assertIn("Warden Kael", prompt)
        self.assertIn("Low and measured", prompt)
        self.assertIn("Keep the road open", prompt)

    def test_rpsay_includes_persona(self):
        prompt = self._build("rpsay", rp_room_buffer=["Hormoth: \"hello\""])
        self.assertIn("Warden Kael", prompt)
        self.assertIn("Low and measured", prompt)

    def test_chat_includes_persona(self):
        prompt = self._build("chat")
        self.assertIn("Warden Kael", prompt)
        self.assertIn("Low and measured", prompt)

    def test_all_modes_include_pc_sheet(self):
        for mode in ("talk", "rpsay", "chat"):
            prompt = self._build(mode)
            self.assertIn("scribe from Custos", prompt,
                          f"PC sheet missing in mode '{mode}'")
            self.assertIn("Cautious, observant", prompt,
                          f"PC personality missing in mode '{mode}'")

    def test_all_modes_include_room_ambience(self):
        for mode in ("talk", "rpsay", "chat"):
            prompt = self._build(mode)
            self.assertIn("ROOM AMBIENCE", prompt,
                          f"Room ambience missing in mode '{mode}'")
            self.assertIn("watchful", prompt,
                          f"Room mood missing in mode '{mode}'")
            self.assertIn("distant chime", prompt,
                          f"Room sounds missing in mode '{mode}'")

    def test_all_modes_include_arc_awareness(self):
        for mode in ("talk", "rpsay", "chat"):
            prompt = self._build(mode)
            self.assertIn("Arc Awareness", prompt,
                          f"Arc awareness missing in mode '{mode}'")
            self.assertIn("Reference her warmth", prompt,
                          f"Arc flavor missing in mode '{mode}'")

    def test_all_modes_filter_secrets_by_trust(self):
        # Default char has no faction rep & no memory → casual tier
        for mode in ("talk", "rpsay", "chat"):
            prompt = self._build(mode)
            # Casual secret should appear
            self.assertIn("I keep the road", prompt,
                          f"Casual secret missing in mode '{mode}'")
            # Higher-tier secrets should NOT appear at casual trust
            self.assertNotIn("Three scouts lost", prompt,
                             f"Warm secret leaked in mode '{mode}'")
            self.assertNotIn("Hillwatch", prompt,
                             f"Allied secret leaked in mode '{mode}'")


class TestModeSpecificDifferences(unittest.TestCase):
    def setUp(self):
        self.char, self.room = _make_character()
        self.npc = _make_npc()
        self.room.mobs.append(self.npc)

    def _build(self, mode, **kwargs):
        return build_unified_npc_prompt(
            npc=self.npc,
            character=self.char,
            room=self.room,
            mode=mode,
            **kwargs,
        )

    def test_chat_has_json_response_format(self):
        prompt = self._build("chat")
        self.assertIn("RESPONSE FORMAT", prompt)
        self.assertIn("dialogue", prompt)
        self.assertIn("game_actions", prompt)
        self.assertIn("emotion_state", prompt)

    def test_talk_has_no_json_format(self):
        prompt = self._build("talk")
        self.assertNotIn("RESPONSE FORMAT", prompt)
        self.assertIn("Speak naturally", prompt)

    def test_rpsay_has_silence_instruction(self):
        prompt = self._build("rpsay", rp_room_buffer=["x: y"])
        self.assertIn("not relevant", prompt.lower())
        self.assertIn("...", prompt)
        self.assertIn("OVERHEARD", prompt)

    def test_rpsay_includes_room_buffer(self):
        prompt = self._build("rpsay", rp_room_buffer=[
            'Alice: "hello"',
            'Bob: "what news"',
        ])
        self.assertIn("RECENT CONVERSATION", prompt)
        self.assertIn("Alice", prompt)
        self.assertIn("hello", prompt)

    def test_rpsay_includes_npc_last_remark(self):
        prompt = self._build("rpsay",
                             rp_room_buffer=[],
                             npc_last_remark="The road carries.")
        self.assertIn("Your last remark", prompt)
        self.assertIn("The road carries", prompt)


class TestBackwardCompat(unittest.TestCase):
    def test_npc_without_persona_still_works(self):
        from src.character import Character
        room = _make_room(with_ambience=False)
        char = Character(
            name="Test", title=None, race="Human", level=1,
            hp=10, max_hp=10, ac=10, room=room,
        )
        char.save = lambda: None
        npc = _make_npc(with_persona=False)
        npc.name = "Generic Guard"
        npc.flags = ["guard"]
        npc.alignment = "Lawful Neutral"
        npc.description = "A vigilant guard."
        npc.dialogue = "Move along."

        # Should not crash
        prompt = build_unified_npc_prompt(
            npc=npc, character=char, room=room, mode="talk",
        )
        self.assertIn("Generic Guard", prompt)
        # Legacy auto-build should kick in
        self.assertIn("guard", prompt.lower())

    def test_no_room_no_crash(self):
        from src.character import Character
        room = _make_room()
        char = Character(
            name="Test", title=None, race="Human", level=1,
            hp=10, max_hp=10, ac=10, room=room,
        )
        char.save = lambda: None
        npc = _make_npc()
        prompt = build_unified_npc_prompt(
            npc=npc, character=char, room=None, mode="talk",
        )
        # Should not crash and should still have core blocks
        self.assertIn("Warden Kael", prompt)

    def test_invalid_mode_falls_back_to_talk(self):
        char, room = _make_character()
        npc = _make_npc()
        prompt = build_unified_npc_prompt(
            npc=npc, character=char, room=room, mode="nonsense_mode",
        )
        # Should not crash; should produce a talk-style prompt
        self.assertNotIn("RESPONSE FORMAT", prompt)


if __name__ == "__main__":
    unittest.main()
