"""
ArcSheet — hidden per-character arc tracking.

Each character carries one ArcSheet per registered arc. Items in the
checklist are flipped by NPC chat actions (check_arc_item) when the
LLM determines a beat has been hit. Players never see this — it's
DM-scope only. Felt experience comes from NPCs reacting via
arc_reactions in their ai_persona.
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Vocabularies
# ---------------------------------------------------------------------------

CHECKLIST_CATEGORIES = {
    "npc_met",
    "fact_learned",
    "place_visited",
    "choice_made",
    "beat_fired",
}

CHECKLIST_STATES = {"unchecked", "checked", "detailed"}

ARC_STATUSES = {"untouched", "aware", "active", "advancing", "resolved"}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ChecklistItem:
    """A single trackable beat within an arc."""
    id: str                                    # stable module-author id
    label: str = ""                            # human-readable, DM view only
    category: str = "fact_learned"             # one of CHECKLIST_CATEGORIES
    state: str = "unchecked"                   # one of CHECKLIST_STATES
    detail: dict = field(default_factory=dict) # free-form when state == "detailed"
    first_changed_at: Optional[float] = None
    last_changed_at: Optional[float] = None
    orphaned: bool = False                     # True if removed from module template

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "category": self.category,
            "state": self.state,
            "detail": dict(self.detail),
            "first_changed_at": self.first_changed_at,
            "last_changed_at": self.last_changed_at,
            "orphaned": self.orphaned,
        }

    @staticmethod
    def from_dict(data: dict) -> "ChecklistItem":
        return ChecklistItem(
            id=data.get("id", ""),
            label=data.get("label", ""),
            category=data.get("category", "fact_learned"),
            state=data.get("state", "unchecked"),
            detail=dict(data.get("detail", {}) or {}),
            first_changed_at=data.get("first_changed_at"),
            last_changed_at=data.get("last_changed_at"),
            orphaned=bool(data.get("orphaned", False)),
        )


@dataclass
class ArcSheet:
    """Per-character tracking sheet for one arc."""
    arc_id: str                                # module-author id, e.g. "quiet_graft"
    title: str = ""                            # human-readable
    status: str = "untouched"                  # one of ARC_STATUSES
    resolution: Optional[str] = None           # free-form id when status == "resolved"
    checklist: list = field(default_factory=list)   # list[ChecklistItem]
    entered_at: Optional[float] = None
    last_activity_at: Optional[float] = None
    flags: dict = field(default_factory=dict)  # module-defined arbitrary flags

    def to_dict(self) -> dict:
        return {
            "arc_id": self.arc_id,
            "title": self.title,
            "status": self.status,
            "resolution": self.resolution,
            "checklist": [
                ci.to_dict() if isinstance(ci, ChecklistItem) else ci
                for ci in self.checklist
            ],
            "entered_at": self.entered_at,
            "last_activity_at": self.last_activity_at,
            "flags": dict(self.flags),
        }

    @staticmethod
    def from_dict(data: dict) -> "ArcSheet":
        if not isinstance(data, dict):
            return ArcSheet(arc_id="")
        items = []
        for ci in data.get("checklist", []) or []:
            if isinstance(ci, ChecklistItem):
                items.append(ci)
            elif isinstance(ci, dict):
                items.append(ChecklistItem.from_dict(ci))
        return ArcSheet(
            arc_id=data.get("arc_id", ""),
            title=data.get("title", ""),
            status=data.get("status", "untouched"),
            resolution=data.get("resolution"),
            checklist=items,
            entered_at=data.get("entered_at"),
            last_activity_at=data.get("last_activity_at"),
            flags=dict(data.get("flags", {}) or {}),
        )

    # ----- Accessors -----

    def get_item(self, item_id: str) -> Optional[ChecklistItem]:
        for ci in self.checklist:
            if ci.id == item_id:
                return ci
        return None

    def has_any_progress(self) -> bool:
        """True if any checklist item is in a non-unchecked state."""
        return any(ci.state != "unchecked" for ci in self.checklist)

    def to_evaluation_context(self) -> dict:
        """Build the dict used by arc_expression evaluator.

        Layout:
            {
                "<item_id>": {"state": "...", "detail": {...}},
                "arc": {"status": "...", "flags": {...}},
            }
        """
        ctx = {}
        for ci in self.checklist:
            ctx[ci.id] = {
                "state": ci.state,
                "detail": dict(ci.detail),
            }
        ctx["arc"] = {
            "status": self.status,
            "flags": dict(self.flags),
        }
        return ctx


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_arc_sheet(data) -> list:
    """Return list of error strings; empty list means valid."""
    errors = []

    if isinstance(data, ArcSheet):
        d = data.to_dict()
    elif isinstance(data, dict):
        d = data
    else:
        return [f"arc sheet must be dict or ArcSheet, got {type(data).__name__}"]

    arc_id = d.get("arc_id", "")
    if not isinstance(arc_id, str) or not arc_id.strip():
        errors.append("arc_id must be a non-empty string")

    status = d.get("status", "untouched")
    if status not in ARC_STATUSES:
        errors.append(f"status {status!r} not in {sorted(ARC_STATUSES)}")

    seen_ids = set()
    for i, ci in enumerate(d.get("checklist", []) or []):
        ci_data = ci.to_dict() if isinstance(ci, ChecklistItem) else ci
        if not isinstance(ci_data, dict):
            errors.append(f"checklist[{i}] must be dict, got {type(ci_data).__name__}")
            continue
        item_id = ci_data.get("id", "")
        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"checklist[{i}] missing id")
            continue
        if item_id in seen_ids:
            errors.append(f"checklist[{i}] duplicate id {item_id!r}")
            continue
        seen_ids.add(item_id)

        category = ci_data.get("category", "fact_learned")
        if category not in CHECKLIST_CATEGORIES:
            errors.append(
                f"checklist[{i}] ({item_id}) category {category!r} not in {sorted(CHECKLIST_CATEGORIES)}"
            )

        state = ci_data.get("state", "unchecked")
        if state not in CHECKLIST_STATES:
            errors.append(
                f"checklist[{i}] ({item_id}) state {state!r} not in {sorted(CHECKLIST_STATES)}"
            )

        if state == "detailed":
            detail = ci_data.get("detail")
            if not isinstance(detail, dict) or not detail:
                errors.append(
                    f"checklist[{i}] ({item_id}) state is 'detailed' but detail is empty"
                )

    return errors


# ---------------------------------------------------------------------------
# Template helpers
# ---------------------------------------------------------------------------

def fresh_arc_from_template(arc_template: dict) -> ArcSheet:
    """Build a blank, all-unchecked ArcSheet from a module's arc definition.

    Template format (from data/modules/{slug}/arcs.json):
        {
            "arc_id": "quiet_graft",
            "title": "The Quiet Graft",
            "checklist": [
                {"id": "met_maeren", "label": "...", "category": "npc_met"},
                ...
            ]
        }
    """
    items = []
    for ci_template in arc_template.get("checklist", []) or []:
        items.append(ChecklistItem(
            id=ci_template.get("id", ""),
            label=ci_template.get("label", ""),
            category=ci_template.get("category", "fact_learned"),
            state="unchecked",
        ))
    return ArcSheet(
        arc_id=arc_template.get("arc_id", ""),
        title=arc_template.get("title", ""),
        status="untouched",
        checklist=items,
    )
