# OrekaMUD3 — Arc Tracking & Module Format

**Target agent:** Claude Code (or similar CLI coding agent) working inside the `oreka_mud` repo.
**Goal:** Add a hidden per-character arc tracking system that lets NPCs react to what a player has learned and who they've met across the game — without the player seeing a quest journal UI. Ship the first module (The Quiet Graft) in the new module authoring format so that one authoring act populates NPCs, rooms, personas, quest chains, and arc reactions in a single drop.

**Rule for the agent:** Do the sections in order. Each section has acceptance criteria. Schema first, then persona extension, then action, then assembler, then module loader, then admin, then migration. The module format depends on all of the prior work.

---

## 0. Context (read this first)

The existing BUILDOUT.md ships the Shadow Chat Game and the four original schemas (`ai_persona`, `pc_sheet`, `room_ambience`, `environment_context`). It treats engine as correct and gaps as content-only. This document **adds a new schema** (`arc_sheet`) and **extends an existing one** (`ai_persona`), because arc tracking is new engine — not a content gap.

Design decisions already locked (do not relitigate):

- **Arc sheets are hidden from the player.** No journal UI. No "quest log" entry. Player-felt experience comes from what NPCs say, not from a panel. Admin/DM view only.
- **Every arc has a flat checklist.** No state graphs, no dependency trees. Items have states `unchecked | checked | detailed`. Categories: `npc_met`, `fact_learned`, `place_visited`, `choice_made`, `beat_fired`.
- **All arcs exist on every character from creation** (lazy population). New arcs get appended to existing character files on load via migration.
- **NPCs react via `arc_reactions`** — conditional flavor strings injected into the prompt, not hardcoded logic.
- **State transitions use structured actions.** The LLM emits `check_arc_item(arc_id, item_id)` (and optionally a detail blob) in its structured output; the engine flips the flag cleanly. No regex parsing of freeform text.
- **Revelation style is per-module authorial.** Loud ("Joe told me about you") vs subtle ("I hear you've been asking around") is a flavor-string choice, not a system setting.
- **Cloud fallback to Claude API is permitted** for arc-aware NPC conversations when Ollama is unhealthy or for premium-tier NPCs. This revises Design Principle #2. Free tier may still be hard-local; policy knob lives in `ai/router.py`.

**Do not touch:**

- Combat. Arc tracking never enters combat resolution.
- The three-tier dialogue system (scripted → template → LLM). Only the LLM tier reads arc sheets. Scripted and template tiers remain deterministic and cheap.
- Existing `ai_persona` fields. Extend only.
- The player-facing UI. Arc sheets never render to the player.

---

## 1. Add the arc sheet schema

Create `oreka_mud/src/ai_schemas/arc_sheet.py`.

### 1.1 Dataclasses

```python
from dataclasses import dataclass, field
from typing import Optional

CHECKLIST_CATEGORIES = {
    "npc_met",
    "fact_learned",
    "place_visited",
    "choice_made",
    "beat_fired",
}

CHECKLIST_STATES = {"unchecked", "checked", "detailed"}

@dataclass
class ChecklistItem:
    id: str                               # stable module-author id, e.g. "met_maeren"
    label: str                            # human-readable, shown in DM view only
    category: str                         # one of CHECKLIST_CATEGORIES
    state: str = "unchecked"              # one of CHECKLIST_STATES
    detail: dict = field(default_factory=dict)
                                          # free-form when state == "detailed":
                                          # {first_met_at, trust, context, topics, ...}
    first_changed_at: Optional[float] = None
    last_changed_at: Optional[float] = None

@dataclass
class ArcSheet:
    arc_id: str                           # "quiet_graft"
    title: str                            # "The Quiet Graft"
    status: str = "untouched"             # untouched | aware | active | advancing | resolved
    resolution: Optional[str] = None      # free-form ending id, e.g. "graft_took", "burned_down"
    checklist: list[ChecklistItem] = field(default_factory=list)
    entered_at: Optional[float] = None
    last_activity_at: Optional[float] = None
    flags: dict = field(default_factory=dict)
                                          # module-defined arbitrary flags
```

### 1.2 Validation

```python
def validate_arc_sheet(data: dict) -> list[str]:
    """Return list of error strings; empty list = valid."""
```

Required checks:
- `arc_id` is a non-empty string
- Every checklist item has valid `category` and `state`
- `state == "detailed"` implies non-empty `detail` dict
- No duplicate checklist item ids within the same arc

### 1.3 Character integration

Extend `Character` in `src/character.py`:

- Add `self.arc_sheets: dict[str, ArcSheet]` — keyed by arc_id
- Serialize/deserialize in the existing JSON save/load path
- Backward-compat: missing `arc_sheets` field loads as empty dict

**Accessor methods on Character:**

```python
def get_arc(self, arc_id: str) -> Optional[ArcSheet]: ...
def get_checklist_item(self, arc_id: str, item_id: str) -> Optional[ChecklistItem]: ...
def check_arc_item(
    self,
    arc_id: str,
    item_id: str,
    detail: Optional[dict] = None,
    now: Optional[float] = None,
) -> bool:
    """Flip state to checked (or detailed if detail provided). Return True if state changed."""
def touched_arcs(self) -> list[str]:
    """Return arc_ids with any checklist item state != 'unchecked'."""
```

### Acceptance — Section 1

- [ ] `src/ai_schemas/arc_sheet.py` exists with dataclasses and validator.
- [ ] `Character` serializes `arc_sheets` through an atomic save/load round trip without data loss.
- [ ] `Character` loads an old save (no `arc_sheets` field) and produces an empty dict.
- [ ] `check_arc_item()` updates `first_changed_at`, `last_changed_at`, `last_activity_at` correctly.
- [ ] Unit tests in `tests/test_arc_sheet.py` cover: validator pass/fail cases, serialize round trip, `check_arc_item` state transition, duplicate-id rejection.

---

## 2. Extend AiPersona with arc awareness

Modify `src/ai_schemas/ai_persona.py`.

### 2.1 New fields

```python
@dataclass
class ArcReaction:
    when: str                             # condition expression, see 2.2
    flavor: str                           # natural-language cue for the LLM prompt
    loudness: str = "natural"             # natural | loud | subtle — authorial guidance

@dataclass
class AiPersona:
    # ... all existing fields unchanged ...
    arcs_known: list[str] = field(default_factory=list)
                                          # arc_ids this NPC is aware of at all
    arc_reactions: list[ArcReaction] = field(default_factory=list)
                                          # evaluated against player's arc sheets
```

### 2.2 Condition expression syntax

Keep simple. A condition is a boolean expression over flat paths. Supported operators: `==`, `!=`, `>=`, `<=`, `>`, `<`, `AND`, `OR`, `NOT`, parentheses.

Supported left-hand paths:
- `<item_id>.state` → one of `unchecked | checked | detailed`
- `<item_id>.detail.<key>` → free-form value lookup (string compare)
- `arc.status` → the arc's own status field
- `arc.flags.<key>` → arc-level flag lookup

Examples:
```
met_maeren.state == checked AND met_maeren.detail.trust == warm
learned_shrine_touch.state == checked
met_joe.state == unchecked AND arc.status != resolved
```

Implement as a small evaluator in `src/ai_schemas/arc_expression.py`. **No `eval()`.** Parse to a tree, evaluate against a context dict built from the player's arc sheet for this arc.

### 2.3 Validation extension

Extend `validate_persona()`:
- Every `arcs_known` entry is a non-empty string
- Every `ArcReaction.when` parses cleanly under the expression grammar
- Every `ArcReaction.loudness` is in `{natural, loud, subtle}`

### 2.4 Stub helper update

Extend `persona_stub_from_mob()`:
- Default `arcs_known` to `[]`
- Default `arc_reactions` to `[]`
- No inference rules — these are always hand-authored

### Acceptance — Section 2

- [ ] `AiPersona` loads with backward compatibility (missing `arcs_known`/`arc_reactions` → empty lists).
- [ ] Expression parser handles all operators with correct precedence.
- [ ] Unit tests in `tests/test_arc_expression.py` cover: simple comparisons, AND/OR combinations, NOT, parentheses, path resolution to missing items (returns false, no crash), malformed expression rejection in validator.
- [ ] `validate_persona()` rejects a persona with a malformed `arc_reactions[*].when`.

---

## 3. The `check_arc_item` structured action

Modify `src/chat_session.py` and the chat action executor.

### 3.1 Allowed action registration

Add to the `allowed_actions` vocabulary:

```
check_arc_item(arc_id: str, item_id: str, detail: dict = {})
```

Gating rules (enforced by the executor, not the prompt):
- NPC must have `arc_id` in its `arcs_known` — else the action is rejected with a log line.
- `item_id` must exist in the module's arc definition — else rejected.
- No rate limit for this action within a single session (NPCs can flip multiple items in one exchange when narratively appropriate).

### 3.2 Executor wiring

When the LLM emits a `check_arc_item` action block:

1. Validate the action against the rules above.
2. Call `character.check_arc_item(arc_id, item_id, detail, now=time.time())`.
3. If the item state actually changed (return value True), emit an internal event `arc.item_checked` with payload `{player_id, arc_id, item_id, prior_state, new_state, source_npc_vnum}`.
4. If the arc's `status` was `untouched` and an item flipped, promote status to `aware` automatically. (Higher statuses — `active`, `advancing`, `resolved` — are only set explicitly by the module via `set_arc_status` action, Section 3.3.)

### 3.3 Companion action: `set_arc_status`

Also add:
```
set_arc_status(arc_id: str, status: str, resolution: str = "")
```

Gating: NPC must have `arc_id` in `arcs_known`. `status` must be a valid enum value. `resolution` only meaningful when `status == "resolved"`.

Usage: a module's climactic NPC (Vaerix at the reckoning, say) emits `set_arc_status("quiet_graft", "resolved", "graft_took")` in their final structured output block.

### 3.4 Prompt documentation

The NPC Agent's system prompt must describe these actions to the LLM, including when to use them. Add a short allowed-actions reference block that lists signature + 1-line usage guidance for each action. Example guidance for `check_arc_item`:

> Call this when the conversation establishes that the player has met someone, learned a fact, visited a place, or made a choice that this arc tracks. Provide `detail` when the item's checklist category warrants it (e.g., `npc_met` with `trust`, `topics`). Do not call for trivia.

### Acceptance — Section 3

- [ ] `check_arc_item` action is parsed from LLM structured output and executed.
- [ ] Action rejections (invalid arc_id, invalid item_id, NPC not in `arcs_known`) are logged with full context.
- [ ] `arc.item_checked` event fires on genuine state changes only.
- [ ] First-time check on an untouched arc promotes status to `aware`.
- [ ] `set_arc_status` works for all valid status transitions.
- [ ] Tests in `tests/test_arc_actions.py` cover: happy path check, rejected check (wrong NPC), detailed check with detail blob, status promotion, explicit `set_arc_status` to resolved.

---

## 4. Prompt assembler extension

Modify `src/ai/npc_agent.py` (or the current prompt-building module) to inject arc state.

### 4.1 New assembler step

After the existing persona + PC sheet + room + environment sections, add an arc context section.

**Selection logic:**

1. Compute `relevant_arcs = intersect(npc.arcs_known, player.touched_arcs())`.
2. For arcs the player has not touched but the NPC knows about, include the arc only if the NPC has an `arc_reactions[*].when` clause that evaluates true (e.g., "met_joe.state == unchecked" — the NPC can open the arc).
3. For each relevant arc:
   - Compute the evaluation context dict from the player's `ArcSheet` for that arc.
   - Iterate `npc.arc_reactions`, evaluate each `when` expression against the context.
   - Collect matching `flavor` strings, tagged with loudness.

**Rendered prompt block format:**

```
## Arc Awareness
You are aware of the following arcs and have noted the following about this traveler:

— Arc: The Quiet Graft (status: aware)
  • The traveler has met Maeren of the Long Road and earned her warmth. You may reference her grief when it would feel natural.
  • The traveler does not yet know about the weighmaster at Dry Fork. If questions arise about the Unstrung, you may suggest the station.

Loudness guidance: reference these softly. Do not enumerate them. Let the conversation reveal them when it fits.
```

The loudness guidance line adapts based on the highest loudness among the matched reactions: if any is `loud`, guidance says "you may speak openly about these"; if all are `subtle`, guidance emphasizes indirection; mixed/natural is the default.

### 4.2 Token budget

The arc section gets a budget of ~800 tokens (per the overall 2500 target from BUILDOUT.md §6 item 2). If exceeded:

1. Rank reactions by salience: matched-on-checked > matched-on-unchecked, recent-activity > old, loud > natural > subtle (loud is more important to include because it's typically the "you've been marked" cue).
2. Drop lowest-salience reactions until under budget.
3. Log the drop event for later audit.

### 4.3 Prompt length audit update

Extend `scripts/audit_prompt_lengths.py` to measure the arc section specifically. Fail if any single NPC with arcs generates > 800 tokens of arc context.

### Acceptance — Section 4

- [ ] Arc context block renders in every LLM-tier NPC prompt where `relevant_arcs` is non-empty.
- [ ] No arc context block renders for NPCs with empty `arcs_known` (backward compat).
- [ ] Expression evaluation correctly filters reactions.
- [ ] Token budget enforced; drops logged.
- [ ] `scripts/smoke_chat.py` extended with a 3-turn arc-aware conversation test: player meets NPC A (checks `met_a`), then meets NPC B; NPC B's opening line acknowledges meeting NPC A.
- [ ] Prompt length audit passes with arc section enabled.

---

## 5. Module authoring format

Create `data/modules/` and the loader.

### 5.1 Module file layout

A module is a directory under `data/modules/{module_slug}/` containing:

```
data/modules/quiet_graft/
├── module.json                   # manifest
├── arcs.json                     # arc definitions (arc_id, title, checklist template)
├── personas/                     # one .json per NPC — extends existing ai_persona schema
│   ├── 9500_vaerix.json
│   ├── 9501_sarre.json
│   ├── 9502_maeren.json
│   ├── 9503_khadi.json
│   └── ... supporting NPCs ...
├── mobs.json                     # stat-block entries, vnum-keyed
├── rooms/                        # one .json per area
│   ├── spur_tower_scholar.json
│   ├── dry_fork_station.json
│   └── long_road_camp.json
├── quests.json                   # quest chain entries using existing quests.py schema
├── factions.json                 # faction hook deltas (reputation changes, new factions)
├── lore/                         # lore chunks for RAG indexing
│   └── *.md
└── hooks.json                    # narrative.py triggers (room entry, kill, level, faction)
```

### 5.2 `module.json` manifest

```json
{
  "module_id": "quiet_graft",
  "title": "The Quiet Graft",
  "version": "0.1.0",
  "author": "Jessie",
  "requires_engine": ">=3.5.0",
  "depends_on_modules": [],
  "summary": "A Dómnathar kingmaker cultivates a half-Farborn heir while the Unstrung quietly learn what he's shopping for.",
  "tags": ["conspiracy", "domnathar", "unstrung", "farborn"],
  "content_warnings": ["grief", "family-separation", "political-violence-implied"]
}
```

### 5.3 `arcs.json` format

```json
{
  "arcs": [
    {
      "arc_id": "quiet_graft",
      "title": "The Quiet Graft",
      "checklist": [
        {
          "id": "met_maeren",
          "label": "Met Maeren of the Long Road",
          "category": "npc_met"
        },
        {
          "id": "learned_maeren_shrine_touch",
          "label": "Learned Maeren can touch shrine infrastructure without ejection",
          "category": "fact_learned"
        },
        {
          "id": "met_vaerix",
          "label": "Met Vaerix Caelnorath",
          "category": "npc_met"
        },
        {
          "id": "visited_dry_fork",
          "label": "Visited Dry Fork Station",
          "category": "place_visited"
        },
        {
          "id": "chose_to_trust_khadi",
          "label": "Chose to trust Khadi's offer",
          "category": "choice_made"
        }
      ]
    }
  ]
}
```

Checklist items here are the **template** — when a new character is created (or migration runs), each character gets a fresh `ArcSheet` with all items in `unchecked` state.

### 5.4 Persona extension format

Persona files in a module's `personas/` directory follow the existing `ai_persona` schema plus the new `arcs_known` and `arc_reactions` fields. Example excerpt:

```json
{
  "vnum": 9500,
  "voice": "Measured, sardonic, unnervingly patient.",
  "motivation": "To build the heir who will eclipse the pre-invasion lords.",
  "speech_style": "scholarly",
  "opening_line": "Ah. Do sit. I have been meaning to speak with you.",
  "arcs_known": ["quiet_graft"],
  "arc_reactions": [
    {
      "when": "met_maeren.state == checked AND met_maeren.detail.trust == warm",
      "flavor": "The player has earned Maeren's warmth. You may probe gently for what she has said to them. Do not name her directly — refer to 'our mutual friend' or 'the woman at Spur Tower.'",
      "loudness": "subtle"
    },
    {
      "when": "met_khadi.state == checked",
      "flavor": "Show no recognition of Khadi's name; however, internally register the player as a potential liability and let your warmth cool by one notch.",
      "loudness": "subtle"
    }
  ],
  "allowed_actions": [
    "check_arc_item",
    "set_arc_status",
    "remember",
    "mark_player",
    "offer_trust"
  ]
}
```

### 5.5 Module loader

Create `src/module_loader.py`:

```python
def load_module(module_slug: str) -> Module: ...
def load_all_modules() -> list[Module]: ...
def apply_module_to_world(module: Module, world: World) -> None: ...
```

Load order on server startup:

1. Discover all `data/modules/*/module.json` files.
2. Sort by `depends_on_modules` dependency graph (topological).
3. For each module in order:
   - Validate all files (arc schema, persona schema, rooms, quests).
   - Merge personas into the live persona registry.
   - Merge rooms into the world (reject vnum collisions with clear error).
   - Merge mobs into the mob registry.
   - Merge quests into quest registry.
   - Register faction deltas.
   - Index lore chunks into pgvector (if running).
   - Register narrative hooks.
4. Run arc migration (Section 7) to backfill existing characters with new arcs.

### 5.6 Module validation

Create `scripts/validate_module.py <module_slug>`:

- All JSON parses cleanly.
- All personas pass `validate_persona()` with the extended rules.
- Every `arc_reactions[*].when` expression references items that exist in the module's arc definitions.
- Every NPC with `arcs_known` containing `arc_id X` only references checklist items from arc X in its reactions.
- No vnum collisions against the live world or other loaded modules.
- All lore chunks are valid markdown with frontmatter specifying `dm_only: true|false`.

### Acceptance — Section 5

- [ ] `data/modules/quiet_graft/` scaffolded with empty-but-valid files.
- [ ] `src/module_loader.py` loads it without error.
- [ ] `scripts/validate_module.py quiet_graft` passes.
- [ ] Dependency ordering works for a two-module test case (mock module B depends on mock module A).
- [ ] vnum collision is detected and the server refuses to start with a clear error message.

---

## 6. Admin observability

Extend the MCP bridge (`src/mcp_bridge.py`) with arc-aware endpoints.

### 6.1 New REST endpoints

```
GET  /arc/sheet/{player_name}              — full arc sheet dump for a player (DM view)
GET  /arc/sheet/{player_name}/{arc_id}     — single arc detail with checklist states
GET  /arc/module/{module_slug}             — module manifest + arc templates + persona list
POST /arc/force-check                      — admin override: check an item on a player's sheet
                                             body: {player, arc_id, item_id, detail?}
POST /arc/force-status                     — admin override: set arc status
                                             body: {player, arc_id, status, resolution?}
GET  /arc/stats                            — per-arc aggregate: how many players touched, resolved, etc.
```

All under the existing admin authentication. Audit log every force-* call.

### 6.2 In-game admin commands

Add to builder command set:

```
@arc view <player>                        — pretty-print player's arc sheets
@arc view <player> <arc_id>               — focused single-arc view
@arc check <player> <arc_id> <item_id>    — force a check (admin override)
@arc status <player> <arc_id> <status>    — force a status transition
@arc stats                                — aggregate stats for the current server
```

Output formatted with the existing `ui.py` rendering helpers.

### Acceptance — Section 6

- [ ] All endpoints respond correctly and enforce admin auth.
- [ ] `@arc view` in-game commands print readable output.
- [ ] Force-* calls are audit-logged to `data/audit/arc_overrides.jsonl`.
- [ ] `/arc/stats` aggregates correctly over a seeded test population.

---

## 7. Character migration

Existing player files predate arc sheets. On load, run migration.

### 7.1 Migration function

`src/migrations/arc_sheets.py`:

```python
def migrate_character_arc_sheets(char_data: dict, registered_arcs: list[dict]) -> dict:
    """
    Ensures the character has an ArcSheet for every registered arc.
    Adds missing arcs as fresh untouched sheets.
    Adds missing checklist items to existing sheets (authored after character was created).
    Never removes or modifies existing non-unchecked state.
    Returns the mutated char_data.
    """
```

### 7.2 When it runs

- On character load, before the Character dataclass is constructed
- When a new module is loaded into a running server, for every online player
- On server startup, as a batch job, for every offline player file (with backup)

### 7.3 Safety

- Create a backup of each character file before migration (`.backup.{timestamp}`)
- Never delete checklist items even if a module removes them from its arc definition — keep as orphaned items with `orphaned: true` flag (DM-visible)
- Log every migration action

### Acceptance — Section 7

- [ ] Old character file (no `arc_sheets` field) loads and gains all registered arcs as untouched.
- [ ] Character with partial `arc_sheets` gains missing arcs without disturbing existing ones.
- [ ] Character with outdated checklist (module added new items) gains new items as unchecked.
- [ ] Orphaned items from a removed-from-module checklist are preserved with `orphaned: true`.
- [ ] Backup files are written before mutation.
- [ ] Tests in `tests/test_migration_arc.py` cover all four cases.

---

## 8. Content quality checks

Before merging:

1. **Module validation pass** — `python scripts/validate_module.py quiet_graft` zero errors.
2. **Prompt length audit** — `python scripts/audit_prompt_lengths.py --arc-section` shows every arc-aware NPC prompt ≤ 2500 total tokens and ≤ 800 in arc section.
3. **Smoke arc-chat test** — `python scripts/smoke_arc_chat.py` runs a scripted 5-turn conversation that:
   - starts with `met_maeren` unchecked
   - ends with `met_maeren` checked via `check_arc_item` action from the LLM
   - persists the state to disk
   - verifies a subsequent NPC reads the new state correctly
4. **Regression** — all existing tests pass.

---

## 9. Out of scope (explicitly do not do)

- Do not build a player-facing quest journal. Arc sheets are hidden by design.
- Do not let `check_arc_item` affect combat, XP, or loot. Those run through separate quest system hooks.
- Do not attempt to auto-generate `arc_reactions` with the LLM. Hand-authored only.
- Do not pre-compute all reactions for all arcs on character load. Evaluate lazily per-conversation.
- Do not share arc sheets across characters of the same player. Each character has their own.
- Do not make arc state visible to other players. Nothing leaks to `look`, `finger`, `who`, or chat channels.

---

## 10. Milestone ordering

1. **Schemas (Section 1)** — no player-visible change, unblocks everything.
2. **AiPersona extension (Section 2)** — expression evaluator is self-contained and testable.
3. **Structured action (Section 3)** — wires the state transitions.
4. **Assembler extension (Section 4)** — NPCs start reading the state. Existing NPCs unaffected because `arcs_known` defaults to empty.
5. **Module loader (Section 5)** — format exists; Quiet Graft scaffolded but empty.
6. **Admin observability (Section 6)** — DM can inspect and override.
7. **Migration (Section 7)** — existing characters survive the new system.
8. **Content quality checks (Section 8)** — shippable.
9. **Author The Quiet Graft** — content authoring phase, separate effort, follows the Canon Bible.

---

## 11. File manifest when complete

```
oreka_mud/
├── src/
│   ├── ai_schemas/
│   │   ├── arc_sheet.py                  # NEW
│   │   ├── arc_expression.py             # NEW
│   │   └── ai_persona.py                 # MODIFIED — arcs_known, arc_reactions
│   ├── character.py                      # MODIFIED — arc_sheets dict + accessors
│   ├── chat_session.py                   # MODIFIED — check_arc_item action
│   ├── ai/
│   │   └── npc_agent.py                  # MODIFIED — arc context assembler
│   ├── module_loader.py                  # NEW
│   ├── mcp_bridge.py                     # MODIFIED — /arc/* endpoints
│   ├── commands.py                       # MODIFIED — @arc builder commands
│   └── migrations/
│       └── arc_sheets.py                 # NEW
├── data/
│   ├── modules/                          # NEW directory
│   │   └── quiet_graft/                  # NEW — scaffold, authored separately
│   │       ├── module.json
│   │       ├── arcs.json
│   │       ├── personas/
│   │       ├── mobs.json
│   │       ├── rooms/
│   │       ├── quests.json
│   │       ├── factions.json
│   │       ├── lore/
│   │       └── hooks.json
│   └── audit/
│       └── arc_overrides.jsonl           # NEW — created on first override
├── scripts/
│   ├── validate_module.py                # NEW
│   ├── smoke_arc_chat.py                 # NEW
│   └── audit_prompt_lengths.py           # MODIFIED — --arc-section flag
└── tests/
    ├── test_arc_sheet.py                 # NEW
    ├── test_arc_expression.py            # NEW
    ├── test_arc_actions.py               # NEW
    ├── test_module_loader.py             # NEW
    └── test_migration_arc.py             # NEW
```

---

**End of brief.** Each section's acceptance criteria must be green before the next section starts. Do not batch commits across sections — per-section review is the whole point.
