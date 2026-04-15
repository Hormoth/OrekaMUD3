"""
AiPersona — canonical NPC character sheet for LLM prompts.

Authored on mobs.json (or in module persona files). The prompt assembler
reads from this if present; otherwise it falls back to building a
personality string from generic mob fields.

Includes the arc tracking extension (arcs_known + arc_reactions) so that
NPCs can react to per-character arc state without engine code changes.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Vocabularies — kept small, concrete, high-signal
# ---------------------------------------------------------------------------

SPEECH_STYLES = {
    "formal", "casual", "cryptic", "clipped", "reverent", "boisterous",
    "wary", "scholarly", "flirtatious", "soldierly", "archaic", "silentborn",
}

EMOTION_STATES = {
    "neutral", "warm", "guarded", "amused", "reverent", "grim", "curious",
    "irritated", "grieving", "defensive", "joyful", "frightened",
    "conspiratorial", "bored", "watchful",
}

MODEL_TIERS = {"premium", "standard", "fast"}

LOUDNESS_LEVELS = {"natural", "loud", "subtle"}

SECRET_TRUST_THRESHOLDS = {"casual", "warm", "trusted", "allied"}

FACTION_BASELINES = {"loyal", "friendly", "neutral", "wary", "hostile"}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FactionAttitude:
    """How an NPC feels about a specific faction by default."""
    faction_id: str
    baseline: str = "neutral"   # one of FACTION_BASELINES
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "FactionAttitude":
        return FactionAttitude(
            faction_id=data.get("faction_id", ""),
            baseline=data.get("baseline", "neutral"),
            notes=data.get("notes", ""),
        )


@dataclass
class ArcReaction:
    """Conditional flavor injected into the LLM prompt when an arc condition matches."""
    when: str                       # boolean expression — see arc_expression module
    flavor: str                     # natural-language cue for the LLM
    loudness: str = "natural"       # one of LOUDNESS_LEVELS

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "ArcReaction":
        return ArcReaction(
            when=data.get("when", ""),
            flavor=data.get("flavor", ""),
            loudness=data.get("loudness", "natural"),
        )


@dataclass
class AiPersona:
    """Full NPC character sheet for LLM-tier dialogue."""

    # --- Identity ---
    voice: str = ""                 # 1-2 sentences on HOW they speak
    motivation: str = ""            # 1 sentence on what drives them
    speech_style: str = "casual"    # see SPEECH_STYLES
    opening_line: str = ""          # greeting when chat begins
    farewell_line: str = ""         # goodbye when chat ends

    # --- Knowledge ---
    knowledge_domains: list = field(default_factory=list)
    forbidden_topics: list = field(default_factory=list)
    lore_tags: list = field(default_factory=list)
    secrets: list = field(default_factory=list)   # "trust_threshold:text" format

    # --- Relationships ---
    faction_attitudes: list = field(default_factory=list)   # list[FactionAttitude]
    relationship_hooks: list = field(default_factory=list)  # short references to other NPCs

    # --- Filtering / routing ---
    chat_eligible: bool = True
    model_tier: str = "standard"    # premium | standard | fast
    default_emotion: str = "neutral"

    # --- Arc tracking (extension from BUILDOUT_ARC_MODULE) ---
    arcs_known: list = field(default_factory=list)          # arc_ids the NPC knows about
    arc_reactions: list = field(default_factory=list)       # list[ArcReaction]

    def to_dict(self) -> dict:
        return {
            "voice": self.voice,
            "motivation": self.motivation,
            "speech_style": self.speech_style,
            "opening_line": self.opening_line,
            "farewell_line": self.farewell_line,
            "knowledge_domains": list(self.knowledge_domains),
            "forbidden_topics": list(self.forbidden_topics),
            "lore_tags": list(self.lore_tags),
            "secrets": list(self.secrets),
            "faction_attitudes": [
                fa.to_dict() if isinstance(fa, FactionAttitude) else fa
                for fa in self.faction_attitudes
            ],
            "relationship_hooks": list(self.relationship_hooks),
            "chat_eligible": self.chat_eligible,
            "model_tier": self.model_tier,
            "default_emotion": self.default_emotion,
            "arcs_known": list(self.arcs_known),
            "arc_reactions": [
                ar.to_dict() if isinstance(ar, ArcReaction) else ar
                for ar in self.arc_reactions
            ],
        }

    @staticmethod
    def from_dict(data: dict) -> "AiPersona":
        if not isinstance(data, dict):
            return AiPersona()

        # Normalize faction_attitudes to FactionAttitude objects
        fa_list = []
        for fa in data.get("faction_attitudes", []) or []:
            if isinstance(fa, FactionAttitude):
                fa_list.append(fa)
            elif isinstance(fa, dict):
                fa_list.append(FactionAttitude.from_dict(fa))

        # Normalize arc_reactions to ArcReaction objects
        ar_list = []
        for ar in data.get("arc_reactions", []) or []:
            if isinstance(ar, ArcReaction):
                ar_list.append(ar)
            elif isinstance(ar, dict):
                ar_list.append(ArcReaction.from_dict(ar))

        return AiPersona(
            voice=data.get("voice", ""),
            motivation=data.get("motivation", ""),
            speech_style=data.get("speech_style", "casual"),
            opening_line=data.get("opening_line", ""),
            farewell_line=data.get("farewell_line", ""),
            knowledge_domains=list(data.get("knowledge_domains", []) or []),
            forbidden_topics=list(data.get("forbidden_topics", []) or []),
            lore_tags=list(data.get("lore_tags", []) or []),
            secrets=list(data.get("secrets", []) or []),
            faction_attitudes=fa_list,
            relationship_hooks=list(data.get("relationship_hooks", []) or []),
            chat_eligible=bool(data.get("chat_eligible", True)),
            model_tier=data.get("model_tier", "standard"),
            default_emotion=data.get("default_emotion", "neutral"),
            arcs_known=list(data.get("arcs_known", []) or []),
            arc_reactions=ar_list,
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate_secret(secret: str) -> Optional[str]:
    """Return error string or None if valid."""
    if not isinstance(secret, str):
        return "secret must be a string"
    if ":" not in secret:
        return f"secret missing 'threshold:' prefix: {secret!r}"
    threshold, text = secret.split(":", 1)
    threshold = threshold.strip()
    if threshold not in SECRET_TRUST_THRESHOLDS:
        return f"secret threshold {threshold!r} not in {sorted(SECRET_TRUST_THRESHOLDS)}"
    if not text.strip():
        return f"secret has no body text: {secret!r}"
    return None


def validate_persona(data) -> list:
    """Return list of error strings; empty list means valid.

    Accepts either a dict or an AiPersona instance.
    """
    errors = []

    if isinstance(data, AiPersona):
        d = data.to_dict()
    elif isinstance(data, dict):
        d = data
    else:
        return [f"persona must be dict or AiPersona, got {type(data).__name__}"]

    # speech_style must be in vocabulary (allow empty for hand-editing flag)
    style = d.get("speech_style", "casual")
    if style and style not in SPEECH_STYLES:
        errors.append(
            f"speech_style {style!r} not in {sorted(SPEECH_STYLES)}"
        )

    # model_tier must be in vocabulary
    tier = d.get("model_tier", "standard")
    if tier not in MODEL_TIERS:
        errors.append(f"model_tier {tier!r} not in {sorted(MODEL_TIERS)}")

    # default_emotion must be in vocabulary
    emotion = d.get("default_emotion", "neutral")
    if emotion not in EMOTION_STATES:
        errors.append(f"default_emotion {emotion!r} not in {sorted(EMOTION_STATES)}")

    # secrets must follow "threshold:text" format
    for i, secret in enumerate(d.get("secrets", []) or []):
        err = _validate_secret(secret)
        if err:
            errors.append(f"secrets[{i}]: {err}")

    # faction_attitudes must have valid baselines
    for i, fa in enumerate(d.get("faction_attitudes", []) or []):
        fa_data = fa.to_dict() if isinstance(fa, FactionAttitude) else fa
        if not isinstance(fa_data, dict):
            errors.append(f"faction_attitudes[{i}] must be dict, got {type(fa_data).__name__}")
            continue
        if not fa_data.get("faction_id"):
            errors.append(f"faction_attitudes[{i}] missing faction_id")
        baseline = fa_data.get("baseline", "neutral")
        if baseline not in FACTION_BASELINES:
            errors.append(
                f"faction_attitudes[{i}] baseline {baseline!r} not in {sorted(FACTION_BASELINES)}"
            )

    # arcs_known entries must be non-empty strings
    for i, arc_id in enumerate(d.get("arcs_known", []) or []):
        if not isinstance(arc_id, str) or not arc_id.strip():
            errors.append(f"arcs_known[{i}] must be a non-empty string")

    # arc_reactions: validate loudness + expression syntax
    # Lazy import to avoid circular import at module load
    try:
        from src.ai_schemas.arc_expression import validate_expression
        have_expr_validator = True
    except ImportError:
        have_expr_validator = False

    for i, ar in enumerate(d.get("arc_reactions", []) or []):
        ar_data = ar.to_dict() if isinstance(ar, ArcReaction) else ar
        if not isinstance(ar_data, dict):
            errors.append(f"arc_reactions[{i}] must be dict, got {type(ar_data).__name__}")
            continue
        when = ar_data.get("when", "")
        if not isinstance(when, str) or not when.strip():
            errors.append(f"arc_reactions[{i}] 'when' expression is empty")
        elif have_expr_validator:
            expr_errors = validate_expression(when)
            for e in expr_errors:
                errors.append(f"arc_reactions[{i}] when: {e}")
        flavor = ar_data.get("flavor", "")
        if not isinstance(flavor, str) or not flavor.strip():
            errors.append(f"arc_reactions[{i}] 'flavor' is empty")
        loudness = ar_data.get("loudness", "natural")
        if loudness not in LOUDNESS_LEVELS:
            errors.append(
                f"arc_reactions[{i}] loudness {loudness!r} not in {sorted(LOUDNESS_LEVELS)}"
            )

    return errors


# ---------------------------------------------------------------------------
# Stub generation (for bulk backfill scripts)
# ---------------------------------------------------------------------------

def persona_stub_from_mob(mob: dict) -> dict:
    """Produce a TODO-filled stub persona from a bare mob dict.

    Used by scripts/backfill_personas.py to generate per-NPC files for
    later hand-authoring. Infers speech_style and model_tier from flags
    and alignment per the rules in BUILDOUT.md §1.1.

    NEVER generates final personas — these are starting points for humans.
    """
    flags = set(f.lower() for f in (mob.get("flags") or []))
    alignment = (mob.get("alignment") or "").lower()
    npc_type = (mob.get("type_") or mob.get("type") or "").lower()

    # Default
    speech_style = "casual"
    model_tier = "fast"

    # Apply rules in order from highest-priority to lowest
    if flags & {"priest", "deity_avatar", "lore_keeper"}:
        speech_style = "reverent"
        model_tier = "premium"
    elif flags & {"guard", "soldier", "watch"}:
        speech_style = "soldierly"
        model_tier = "fast"
    elif "innkeeper" in flags:
        speech_style = "boisterous"
        model_tier = "standard"
    elif flags & {"shopkeeper", "merchant", "banker"}:
        speech_style = "casual"
        model_tier = "standard"
    elif flags & {"faction_leader", "boss"}:
        speech_style = ""           # explicit blank for human authoring
        model_tier = "premium"
    elif "evil" in alignment:
        speech_style = "wary"

    name = mob.get("name", "Unknown NPC")
    description = mob.get("description", "")[:200] if mob.get("description") else ""
    existing_dialogue = mob.get("dialogue", "")

    return {
        "vnum": mob.get("vnum"),
        "name": name,
        "_TODO": "Fill in voice, motivation, opening_line, farewell_line, knowledge_domains, secrets.",
        "voice": "",
        "motivation": "",
        "speech_style": speech_style,
        "opening_line": existing_dialogue or "",
        "farewell_line": "",
        "knowledge_domains": [],
        "forbidden_topics": [],
        "lore_tags": [],
        "secrets": [],
        "faction_attitudes": [],
        "relationship_hooks": [],
        "chat_eligible": True,
        "model_tier": model_tier,
        "default_emotion": "neutral",
        "arcs_known": [],
        "arc_reactions": [],
        "_source_description": description,
    }
