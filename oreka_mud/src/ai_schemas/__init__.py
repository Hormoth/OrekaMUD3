"""
AI prompt schemas for OrekaMUD3.

These dataclasses define the canonical shape of data injected into LLM
prompts for NPC dialogue. They are content schemas, not engine schemas —
the engine reads them but doesn't change them.

Modules:
    ai_persona       — NPC character sheets (voice, motivation, secrets, arcs)
    pc_sheet         — Player roleplay sheets (bio, goals, recent events)
    room_ambience    — Optional rich room atmosphere (mood, sounds, smells)
    environment_context — Live world-state aggregator (weather, season, events)
    arc_sheet        — Per-character hidden arc tracking (DM-only)
    arc_expression   — Boolean expression evaluator for arc_reactions[*].when
"""

from src.ai_schemas.ai_persona import (
    AiPersona, ArcReaction, FactionAttitude,
    SPEECH_STYLES, EMOTION_STATES, MODEL_TIERS, LOUDNESS_LEVELS,
    SECRET_TRUST_THRESHOLDS,
    validate_persona, persona_stub_from_mob,
)
from src.ai_schemas.pc_sheet import (
    PcSheet, RecentEvent,
    EVENT_CATEGORIES,
    record_event, record_notable_kill, summarize_for_prompt,
)
from src.ai_schemas.room_ambience import (
    RoomAmbience,
    validate_ambience,
)
from src.ai_schemas.environment_context import (
    build_environment_context,
)
from src.ai_schemas.arc_sheet import (
    ArcSheet, ChecklistItem,
    CHECKLIST_CATEGORIES, CHECKLIST_STATES, ARC_STATUSES,
    validate_arc_sheet, fresh_arc_from_template,
)
from src.ai_schemas.arc_expression import (
    parse_expression, evaluate_expression, validate_expression,
    ArcExpressionError,
)

__all__ = [
    # ai_persona
    "AiPersona", "ArcReaction", "FactionAttitude",
    "SPEECH_STYLES", "EMOTION_STATES", "MODEL_TIERS", "LOUDNESS_LEVELS",
    "SECRET_TRUST_THRESHOLDS",
    "validate_persona", "persona_stub_from_mob",
    # pc_sheet
    "PcSheet", "RecentEvent", "EVENT_CATEGORIES",
    "record_event", "record_notable_kill", "summarize_for_prompt",
    # room_ambience
    "RoomAmbience", "validate_ambience",
    # environment_context
    "build_environment_context",
    # arc_sheet
    "ArcSheet", "ChecklistItem",
    "CHECKLIST_CATEGORIES", "CHECKLIST_STATES", "ARC_STATUSES",
    "validate_arc_sheet", "fresh_arc_from_template",
    # arc_expression
    "parse_expression", "evaluate_expression", "validate_expression",
    "ArcExpressionError",
]
