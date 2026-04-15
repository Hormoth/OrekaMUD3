"""Tests for the four core AI schemas: AiPersona, PcSheet, RoomAmbience, environment_context."""

import os
import sys
import time
import unittest

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_schemas import (
    AiPersona, ArcReaction, FactionAttitude,
    SPEECH_STYLES, EMOTION_STATES, MODEL_TIERS, LOUDNESS_LEVELS,
    validate_persona, persona_stub_from_mob,
    PcSheet, RecentEvent, record_event, record_notable_kill, summarize_for_prompt,
    RoomAmbience, validate_ambience,
    build_environment_context,
)


# =========================================================================
# AiPersona
# =========================================================================

class TestAiPersonaSerialization(unittest.TestCase):
    def test_empty_round_trip(self):
        p = AiPersona()
        d = p.to_dict()
        p2 = AiPersona.from_dict(d)
        self.assertEqual(p.to_dict(), p2.to_dict())

    def test_full_round_trip(self):
        p = AiPersona(
            voice="Low and measured.",
            motivation="Keep the road open.",
            speech_style="clipped",
            opening_line="You're new.",
            farewell_line="Walk watchful.",
            knowledge_domains=["frontier"],
            forbidden_topics=["his_daughter"],
            lore_tags=["gatefall_reach"],
            secrets=["warm:Three scouts lost.", "trusted:Spreading down, not east."],
            faction_attitudes=[FactionAttitude("gatefall_remnant", "allied", "kin")],
            relationship_hooks=["Captain Vess — respects, mistrusts."],
            chat_eligible=True,
            model_tier="premium",
            default_emotion="watchful",
            arcs_known=["quiet_graft"],
            arc_reactions=[
                ArcReaction("met_maeren.state == checked", "Reference her grief", "subtle"),
            ],
        )
        d = p.to_dict()
        p2 = AiPersona.from_dict(d)
        self.assertEqual(p.to_dict(), p2.to_dict())
        # Faction attitude survived
        self.assertEqual(len(p2.faction_attitudes), 1)
        self.assertEqual(p2.faction_attitudes[0].faction_id, "gatefall_remnant")
        # Arc reaction survived
        self.assertEqual(len(p2.arc_reactions), 1)
        self.assertEqual(p2.arc_reactions[0].loudness, "subtle")


class TestPersonaValidation(unittest.TestCase):
    def test_minimal_valid(self):
        self.assertEqual(validate_persona({}), [])

    def test_default_dataclass_valid(self):
        self.assertEqual(validate_persona(AiPersona()), [])

    def test_bad_speech_style(self):
        errors = validate_persona({"speech_style": "interpretive_dance"})
        self.assertTrue(any("speech_style" in e for e in errors))

    def test_bad_model_tier(self):
        errors = validate_persona({"model_tier": "ultra_premium"})
        self.assertTrue(any("model_tier" in e for e in errors))

    def test_bad_default_emotion(self):
        errors = validate_persona({"default_emotion": "ennui"})
        self.assertTrue(any("default_emotion" in e for e in errors))

    def test_secret_missing_prefix(self):
        errors = validate_persona({"secrets": ["just plain text"]})
        self.assertTrue(any("threshold" in e.lower() or "prefix" in e.lower() for e in errors))

    def test_secret_bad_threshold(self):
        errors = validate_persona({"secrets": ["maybe:something"]})
        self.assertTrue(any("threshold" in e.lower() for e in errors))

    def test_secret_empty_text(self):
        errors = validate_persona({"secrets": ["warm:"]})
        self.assertTrue(any("body text" in e for e in errors))

    def test_secret_valid(self):
        self.assertEqual(validate_persona({"secrets": [
            "casual:Knows the river road.",
            "warm:Lost three scouts.",
            "trusted:The Breach spreads down.",
            "allied:Was at Hillwatch.",
        ]}), [])

    def test_faction_attitude_missing_id(self):
        errors = validate_persona({"faction_attitudes": [{"baseline": "wary"}]})
        self.assertTrue(any("faction_id" in e for e in errors))

    def test_faction_attitude_bad_baseline(self):
        errors = validate_persona({"faction_attitudes": [
            {"faction_id": "x", "baseline": "smitten"}
        ]})
        self.assertTrue(any("baseline" in e for e in errors))

    def test_arc_reaction_empty_when(self):
        errors = validate_persona({"arc_reactions": [
            {"when": "", "flavor": "x", "loudness": "natural"}
        ]})
        self.assertTrue(any("when" in e for e in errors))

    def test_arc_reaction_bad_loudness(self):
        errors = validate_persona({"arc_reactions": [
            {"when": "x.state == checked", "flavor": "x", "loudness": "deafening"}
        ]})
        self.assertTrue(any("loudness" in e for e in errors))

    def test_arc_reaction_malformed_expression(self):
        errors = validate_persona({"arc_reactions": [
            {"when": "this is not valid syntax !!!", "flavor": "x", "loudness": "natural"}
        ]})
        # Expression validator should flag it
        self.assertTrue(any("when" in e for e in errors))

    def test_arcs_known_must_be_strings(self):
        errors = validate_persona({"arcs_known": ["", "valid_arc"]})
        self.assertTrue(any("arcs_known" in e for e in errors))


class TestPersonaStub(unittest.TestCase):
    def test_priest_stub(self):
        stub = persona_stub_from_mob({
            "vnum": 1, "name": "Sister Ilaine",
            "flags": ["priest"], "alignment": "Lawful Good",
        })
        self.assertEqual(stub["speech_style"], "reverent")
        self.assertEqual(stub["model_tier"], "premium")

    def test_guard_stub(self):
        stub = persona_stub_from_mob({
            "vnum": 2, "name": "City Guard",
            "flags": ["guard"], "alignment": "Lawful Neutral",
        })
        self.assertEqual(stub["speech_style"], "soldierly")
        self.assertEqual(stub["model_tier"], "fast")

    def test_innkeeper_stub(self):
        stub = persona_stub_from_mob({
            "vnum": 3, "name": "Innkeeper",
            "flags": ["innkeeper"], "alignment": "Neutral Good",
        })
        self.assertEqual(stub["speech_style"], "boisterous")
        self.assertEqual(stub["model_tier"], "standard")

    def test_shopkeeper_stub(self):
        stub = persona_stub_from_mob({
            "vnum": 4, "name": "Merchant",
            "flags": ["shopkeeper"],
        })
        self.assertEqual(stub["speech_style"], "casual")
        self.assertEqual(stub["model_tier"], "standard")

    def test_evil_alignment_stub(self):
        stub = persona_stub_from_mob({
            "vnum": 5, "name": "Bandit",
            "flags": [], "alignment": "Chaotic Evil",
        })
        self.assertEqual(stub["speech_style"], "wary")

    def test_default_stub(self):
        stub = persona_stub_from_mob({"vnum": 6, "name": "Random"})
        self.assertEqual(stub["speech_style"], "casual")
        self.assertEqual(stub["model_tier"], "fast")

    def test_faction_leader_blank_style(self):
        stub = persona_stub_from_mob({
            "vnum": 7, "name": "Leader",
            "flags": ["faction_leader"],
        })
        self.assertEqual(stub["speech_style"], "")  # blank for human authoring
        self.assertEqual(stub["model_tier"], "premium")


# =========================================================================
# PcSheet
# =========================================================================

class TestPcSheetSerialization(unittest.TestCase):
    def test_empty_round_trip(self):
        s = PcSheet()
        d = s.to_dict()
        s2 = PcSheet.from_dict(d)
        self.assertEqual(s.to_dict(), s2.to_dict())

    def test_full_round_trip(self):
        s = PcSheet(
            bio="A scribe from Custos.",
            personality="Cautious, observant.",
            goals=["find the missing ledger", "retire to the hills"],
            quirks=["always carries ink", "winces at thunder"],
            pronouns="she/her",
            recent_events=[
                RecentEvent("Killed a goblin.", time.time(), "combat", 1.5),
            ],
            titles_earned=["Blooded"],
            notable_kills=["Goblin Chieftain"],
            deaths=2, remorts=0,
            npc_relationships={"9010": "warm"},
        )
        d = s.to_dict()
        s2 = PcSheet.from_dict(d)
        self.assertEqual(s.to_dict(), s2.to_dict())

    def test_quirks_capped_at_5(self):
        s = PcSheet.from_dict({"quirks": ["a", "b", "c", "d", "e", "f", "g"]})
        self.assertEqual(len(s.quirks), 5)

    def test_recent_events_capped_at_10(self):
        events = [{"text": str(i), "timestamp": float(i)} for i in range(20)]
        s = PcSheet.from_dict({"recent_events": events})
        self.assertEqual(len(s.recent_events), 10)


class TestPcSheetHooks(unittest.TestCase):
    def test_record_event(self):
        s = PcSheet()
        record_event(s, "Killed a goblin.", "combat", 1.5)
        self.assertEqual(len(s.recent_events), 1)
        self.assertEqual(s.recent_events[0].text, "Killed a goblin.")

    def test_record_event_caps_at_10(self):
        s = PcSheet()
        for i in range(15):
            record_event(s, f"event {i}")
        self.assertEqual(len(s.recent_events), 10)

    def test_record_event_invalid_category_normalized(self):
        s = PcSheet()
        record_event(s, "x", "bogus_category")
        self.assertEqual(s.recent_events[0].category, "general")

    def test_record_notable_kill(self):
        s = PcSheet()
        record_notable_kill(s, "Goblin Chieftain")
        self.assertEqual(s.notable_kills, ["Goblin Chieftain"])

    def test_record_notable_kill_dedup(self):
        s = PcSheet()
        record_notable_kill(s, "Boss")
        record_notable_kill(s, "Boss")
        self.assertEqual(len(s.notable_kills), 1)


class TestSummarizeForPrompt(unittest.TestCase):
    def _make_char(self, **overrides):
        class FakeChar:
            pass
        c = FakeChar()
        c.name = overrides.get("name", "Hormoth")
        c.level = overrides.get("level", 3)
        c.race = overrides.get("race", "Taraf-Imro Human")
        c.char_class = overrides.get("char_class", "Fighter")
        return c

    def test_empty_sheet_falls_back_to_legacy(self):
        s = PcSheet()
        char = self._make_char()
        result = summarize_for_prompt(s, char)
        self.assertIn("Hormoth", result)
        self.assertIn("level 3", result)
        self.assertIn("Fighter", result)

    def test_hidden_sheet_falls_back(self):
        s = PcSheet(bio="x", personality="y", sheet_visible_in_prompts=False)
        char = self._make_char()
        result = summarize_for_prompt(s, char)
        self.assertNotIn("x", result)
        self.assertIn("Hormoth", result)

    def test_filled_sheet_renders_blocks(self):
        s = PcSheet(
            bio="A scribe from Custos.",
            personality="Cautious.",
            goals=["find the ledger"],
            quirks=["carries ink"],
        )
        char = self._make_char()
        result = summarize_for_prompt(s, char)
        self.assertIn("scribe from Custos", result)
        self.assertIn("Cautious", result)
        self.assertIn("ledger", result)

    def test_max_chars_enforced(self):
        s = PcSheet(bio="X" * 1000)
        char = self._make_char()
        result = summarize_for_prompt(s, char, max_chars=100)
        self.assertLessEqual(len(result), 100)


# =========================================================================
# RoomAmbience
# =========================================================================

class TestRoomAmbience(unittest.TestCase):
    def test_empty_round_trip(self):
        a = RoomAmbience()
        self.assertEqual(RoomAmbience.from_dict(a.to_dict()).to_dict(), a.to_dict())

    def test_full_round_trip(self):
        a = RoomAmbience(
            mood="reverent",
            sounds=["a distant chime"],
            smells=["wet stone"],
            textures=["floor hums"],
            ambient_details=["motes drift"],
            npc_relevance={"9200": "Elia tends the altar"},
            events_history=["a pilgrim wept here"],
            seasonal_variants={"deepwinter": "snow drifts in"},
            time_variants={"night": "shadows pool"},
        )
        a2 = RoomAmbience.from_dict(a.to_dict())
        self.assertEqual(a.to_dict(), a2.to_dict())

    def test_events_history_capped_at_5(self):
        a = RoomAmbience.from_dict({"events_history": [str(i) for i in range(10)]})
        self.assertEqual(len(a.events_history), 5)

    def test_push_event(self):
        a = RoomAmbience()
        for i in range(7):
            a.push_event(f"event {i}")
        self.assertEqual(len(a.events_history), 5)
        self.assertEqual(a.events_history[-1], "event 6")

    def test_validate_valid(self):
        self.assertEqual(validate_ambience({}), [])

    def test_validate_bad_time_variant(self):
        errors = validate_ambience({"time_variants": {"midnight_express": "x"}})
        self.assertTrue(any("time_variants" in e for e in errors))

    def test_validate_bad_list_field(self):
        errors = validate_ambience({"sounds": "not a list"})
        self.assertTrue(any("sounds" in e for e in errors))


# =========================================================================
# environment_context
# =========================================================================

class TestEnvironmentContext(unittest.TestCase):
    def test_handles_no_room(self):
        ctx = build_environment_context(None, None)
        self.assertIsInstance(ctx, dict)
        self.assertIn("region", ctx)

    def test_returns_dict_with_keys(self):
        class FakeRoom:
            vnum = 1000
            flags = []
            weather = "clear"
            name = "Test Room"
        ctx = build_environment_context(None, FakeRoom())
        self.assertIn("time_of_day", ctx)
        self.assertIn("weather", ctx)
        self.assertIn("region", ctx)
        self.assertIn("region_politics", ctx)

    def test_never_raises_on_bad_input(self):
        # Pass garbage; should still return dict
        ctx = build_environment_context("nonsense", 42)
        self.assertIsInstance(ctx, dict)


if __name__ == "__main__":
    unittest.main()
