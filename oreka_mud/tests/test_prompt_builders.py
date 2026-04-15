"""Tests for the rewritten prompt builders (Phase 2)."""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai import (
    _build_npc_personality, _build_persona_block, _build_arc_context_block,
    effective_trust, _filter_secrets_by_trust, _build_chat_system_prompt,
)
from src.ai_schemas import (
    AiPersona, ArcReaction, FactionAttitude, ArcSheet, ChecklistItem,
)


# =========================================================================
# _build_npc_personality
# =========================================================================

class TestNpcPersonalityFallback(unittest.TestCase):
    """Backward compat: NPCs without ai_persona use auto-build."""

    def test_no_persona_uses_legacy_auto_build(self):
        npc = MagicMock()
        npc.name = "Town Guard"
        npc.type_ = "Humanoid"
        npc.flags = ["guard"]
        npc.alignment = "Lawful Neutral"
        npc.description = "A vigilant city guard."
        npc.dialogue = "Move along."
        npc.ai_persona = None

        result = _build_npc_personality(npc)
        self.assertIn("Town Guard", result)
        self.assertIn("guard", result.lower())
        self.assertIn("Lawful Neutral", result)
        self.assertIn("vigilant", result)

    def test_with_persona_uses_new_format(self):
        npc = MagicMock()
        npc.name = "Warden Kael"
        npc.type_ = "Humanoid"
        npc.ai_persona = {
            "voice": "Low and measured.",
            "motivation": "Keep the road open.",
            "speech_style": "clipped",
            "knowledge_domains": ["frontier", "wind_riders"],
            "forbidden_topics": ["his_daughter"],
        }

        result = _build_npc_personality(npc)
        self.assertIn("Warden Kael", result)
        self.assertIn("Low and measured", result)
        self.assertIn("Keep the road open", result)
        self.assertIn("clipped", result)
        self.assertIn("frontier", result)
        self.assertIn("his_daughter", result)
        # Should contain rules text
        self.assertIn("Stay in character", result)


# =========================================================================
# effective_trust
# =========================================================================

class TestEffectiveTrust(unittest.TestCase):
    def _make_char(self, reputation=None):
        char = MagicMock()
        char.reputation = reputation or {}
        return char

    def test_no_persona_returns_casual(self):
        char = self._make_char()
        self.assertEqual(effective_trust(None, char, {}), "casual")

    def test_empty_persona_returns_casual(self):
        char = self._make_char()
        self.assertEqual(effective_trust({}, char, {}), "casual")

    def test_allied_baseline_with_high_rep(self):
        persona = {"faction_attitudes": [
            {"faction_id": "gatefall", "baseline": "allied"}
        ]}
        char = self._make_char({"gatefall": 200})
        self.assertEqual(effective_trust(persona, char, {}), "allied")

    def test_friendly_baseline_with_neutral_rep(self):
        persona = {"faction_attitudes": [
            {"faction_id": "x", "baseline": "friendly"}
        ]}
        char = self._make_char({"x": 50})
        self.assertEqual(effective_trust(persona, char, {}), "warm")

    def test_hostile_overrides_all(self):
        persona = {"faction_attitudes": [
            {"faction_id": "a", "baseline": "allied"},
            {"faction_id": "b", "baseline": "hostile"},
        ]}
        char = self._make_char({"a": 200, "b": 50})
        self.assertEqual(effective_trust(persona, char, {}), "casual")

    def test_session_count_promotes_tier(self):
        persona = {}
        char = self._make_char()
        memory = {"sessions": 30}  # 3 tier promotions
        self.assertEqual(effective_trust(persona, char, memory), "allied")

    def test_clamps_to_max(self):
        persona = {}
        char = self._make_char()
        memory = {"sessions": 1000}
        self.assertEqual(effective_trust(persona, char, memory), "allied")


# =========================================================================
# _filter_secrets_by_trust
# =========================================================================

class TestSecretFiltering(unittest.TestCase):
    def setUp(self):
        self.secrets = [
            "casual:Knows the river road.",
            "warm:Lost three scouts last moon.",
            "trusted:The Breach spreads down, not east.",
            "allied:Was at Hillwatch the night it fell.",
        ]

    def test_casual_only_sees_casual(self):
        result = _filter_secrets_by_trust(self.secrets, "casual")
        self.assertEqual(len(result), 1)
        self.assertIn("river road", result[0])

    def test_warm_sees_two(self):
        result = _filter_secrets_by_trust(self.secrets, "warm")
        self.assertEqual(len(result), 2)

    def test_trusted_sees_three(self):
        result = _filter_secrets_by_trust(self.secrets, "trusted")
        self.assertEqual(len(result), 3)

    def test_allied_sees_all(self):
        result = _filter_secrets_by_trust(self.secrets, "allied")
        self.assertEqual(len(result), 4)

    def test_malformed_secrets_skipped(self):
        bad = ["no colon", "bad_threshold:text", "warm:valid"]
        result = _filter_secrets_by_trust(bad, "trusted")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "valid")


# =========================================================================
# _build_arc_context_block
# =========================================================================

class TestArcContextBlock(unittest.TestCase):
    def _make_char_with_arc(self, arc_status="aware", item_state="checked", item_detail=None):
        from src.character import Character
        from src.room import Room
        room = Room(vnum=1, name="x", description="x", exits={}, flags=[])
        char = Character(
            name="Test", title=None, race="Human", level=1,
            hp=10, max_hp=10, ac=10, room=room,
        )
        item = ChecklistItem(
            id="met_maeren", category="npc_met", state=item_state,
            detail=item_detail or {},
        )
        arc = ArcSheet(
            arc_id="quiet_graft", title="The Quiet Graft",
            status=arc_status, checklist=[item],
        )
        char.arc_sheets["quiet_graft"] = arc
        return char

    def test_no_persona_returns_empty(self):
        char = self._make_char_with_arc()
        self.assertEqual(_build_arc_context_block(None, char), "")

    def test_no_arcs_known_returns_empty(self):
        persona = {"arcs_known": [], "arc_reactions": []}
        char = self._make_char_with_arc()
        self.assertEqual(_build_arc_context_block(persona, char), "")

    def test_no_reactions_returns_empty(self):
        persona = {"arcs_known": ["quiet_graft"], "arc_reactions": []}
        char = self._make_char_with_arc()
        self.assertEqual(_build_arc_context_block(persona, char), "")

    def test_unmatched_reaction_returns_empty(self):
        persona = {
            "arcs_known": ["quiet_graft"],
            "arc_reactions": [
                {
                    "when": "met_maeren.detail.trust == warm",
                    "flavor": "Reference her grief.",
                    "loudness": "subtle",
                }
            ],
        }
        # Item is checked but no detail.trust set
        char = self._make_char_with_arc(item_state="checked")
        self.assertEqual(_build_arc_context_block(persona, char), "")

    def test_matched_reaction_renders_block(self):
        persona = {
            "arcs_known": ["quiet_graft"],
            "arc_reactions": [
                {
                    "when": "met_maeren.detail.trust == warm",
                    "flavor": "Reference her grief.",
                    "loudness": "subtle",
                }
            ],
        }
        char = self._make_char_with_arc(item_state="detailed", item_detail={"trust": "warm"})
        block = _build_arc_context_block(persona, char)
        self.assertIn("Arc Awareness", block)
        self.assertIn("Quiet Graft", block)
        self.assertIn("Reference her grief", block)
        self.assertIn("softly", block.lower())   # subtle loudness guidance

    def test_loud_loudness_guidance(self):
        persona = {
            "arcs_known": ["quiet_graft"],
            "arc_reactions": [
                {
                    "when": "met_maeren.state == checked",
                    "flavor": "She told us about you.",
                    "loudness": "loud",
                }
            ],
        }
        char = self._make_char_with_arc()
        block = _build_arc_context_block(persona, char)
        self.assertIn("openly", block.lower())

    def test_natural_loudness_guidance(self):
        persona = {
            "arcs_known": ["quiet_graft"],
            "arc_reactions": [
                {
                    "when": "met_maeren.state == checked",
                    "flavor": "Hint at it.",
                    "loudness": "natural",
                }
            ],
        }
        char = self._make_char_with_arc()
        block = _build_arc_context_block(persona, char)
        # natural guidance contains "naturally"
        self.assertIn("naturally", block.lower())


if __name__ == "__main__":
    unittest.main()
