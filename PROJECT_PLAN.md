# OrekaMUD3 — Implementation Plan

**Created:** 2026-04-13
**Scope:** Execute BUILDOUT.md, BUILDOUT_ARC_MODULE.md, and BUILDOUT_VEIL.md in dependency order.

This plan combines all three planning briefs into a single execution sequence. The briefs authored their sections independently, but in practice they share a foundation (`ai_persona`) and must be interleaved.

---

## Combined Dependency Graph

```
                    ┌─────────────────────────────┐
                    │  PHASE 1: Foundation        │
                    │  - 4 schemas (BUILDOUT §1)  │
                    │  - ArcSheet (ARCS §1)       │
                    │  - ai_persona arc ext       │
                    │    (ARCS §2 + expression)   │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │  PHASE 2: Engine Wiring     │
                    │  - Prompt builders          │
                    │    (BUILDOUT §2)            │
                    │  - check_arc_item action    │
                    │    (ARCS §3)                │
                    │  - Arc context block        │
                    │    (ARCS §4)                │
                    └──────────────┬──────────────┘
                                   ▼
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
┌───────────────────┐  ┌───────────────────┐  ┌──────────────────────┐
│ PHASE 3: Tools    │  │ PHASE 4: Modules  │  │ PHASE 5: Shadow Chat │
│ - rpsheet (B§3)   │  │ - Module loader   │  │   Game (BUILDOUT §5) │
│ - @arc (A§6)      │  │   (ARCS §5)       │  │ - State machine      │
│ - Migration (A§7) │  │ - Quiet Graft     │  │ - 6 mechanics        │
│                   │  │   scaffold        │  │ - 8 exemplar personas│
└─────────┬─────────┘  └─────────┬─────────┘  └──────────┬───────────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────────┐
                    │  PHASE 6: Veil Admin        │
                    │  (different repo)           │
                    │  - Gateway routes           │
                    │  - DM Arc Panel UI          │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │  PHASE 7: Content & Polish  │
                    │  - 42 more personas         │
                    │  - DM Agent integration     │
                    │  - Module mgmt UI           │
                    │  - Electron parity          │
                    │  - Quality checks           │
                    │  - Author "Quiet Graft"     │
                    └─────────────────────────────┘
```

---

## Phase 1 — Foundation Schemas

**Goal:** All schemas exist, validate cleanly, save/load round-trip works. Zero player-visible change. No engine wiring yet — that's Phase 2.

### Tasks

| # | Source | What | Files Created |
|---|--------|------|---------------|
| 1.1 | BUILDOUT §1.1 | `AiPersona` + `FactionAttitude` + vocabularies + `validate_persona()` + `persona_stub_from_mob()` | `src/ai_schemas/__init__.py`, `src/ai_schemas/ai_persona.py` |
| 1.2 | BUILDOUT §1.2 | `PcSheet` + `RecentEvent` + `summarize_for_prompt()` + engine-hook helpers | `src/ai_schemas/pc_sheet.py` |
| 1.3 | BUILDOUT §1.3 | `RoomAmbience` dataclass | `src/ai_schemas/room_ambience.py` |
| 1.4 | BUILDOUT §1.4 | `build_environment_context()` aggregator | `src/ai_schemas/environment_context.py` |
| 1.5 | ARCS §1 | `ArcSheet` + `ChecklistItem` + `validate_arc_sheet()` + Character integration | `src/ai_schemas/arc_sheet.py`, modify `src/character.py` |
| 1.6 | ARCS §2.2 | Expression evaluator (no `eval`, hand-rolled parser) | `src/ai_schemas/arc_expression.py` |
| 1.7 | ARCS §2.1 | Extend `AiPersona` with `arcs_known` + `arc_reactions` + `ArcReaction` | modify `src/ai_schemas/ai_persona.py` |
| 1.8 | All | Unit tests | `tests/test_ai_schemas.py`, `tests/test_arc_sheet.py`, `tests/test_arc_expression.py` |
| 1.9 | BUILDOUT §1 | Mob loader calls `validate_persona()`, logs warnings (not fatal) | modify `src/world.py` or wherever mobs load |

### Acceptance criteria

- All schemas importable
- All validators reject malformed input with specific error strings
- `Character.arc_sheets` round-trips through save/load with no data loss
- Old character files (no `arc_sheets` field) load to empty dict
- Expression parser handles `==`, `!=`, `>=`, `<=`, `>`, `<`, `AND`, `OR`, `NOT`, parens
- 298 existing tests still pass + new tests pass
- No player-visible behavior change

### Effort estimate
Substantial. Largest single phase. Maybe 1-2 work sessions.

---

## Phase 2 — Engine Wiring

**Goal:** Prompt builders read the new schemas. Existing 4 personas with `ai_persona` instantly look smarter. NPC chat starts using PC sheets and arc context.

### Tasks

| # | Source | What |
|---|--------|------|
| 2.1 | BUILDOUT §2.1 | Rewrite `_build_npc_personality()` — uses `ai_persona` if present, falls back to old behavior |
| 2.2 | BUILDOUT §2.2 | Rewrite `_build_chat_system_prompt()` — assembles 5 blocks (persona, PC sheet, room ambience, environment, memory) |
| 2.3 | BUILDOUT §2.2 | Implement `effective_trust()` and secrets filtering by trust threshold |
| 2.4 | BUILDOUT §2.3 | New `_build_rpsay_npc_prompt()` builder with room buffer + speaker PC sheet |
| 2.5 | ARCS §3.1-§3.2 | `check_arc_item` structured action — register, parse, execute, gate, fire `arc.item_checked` event |
| 2.6 | ARCS §3.3 | Companion action `set_arc_status` |
| 2.7 | ARCS §3.4 | Update prompt to document allowed actions for the LLM |
| 2.8 | ARCS §4.1 | Arc context block in chat system prompt — `relevant_arcs` selection, render with loudness guidance |
| 2.9 | ARCS §4.2 | Token budget enforcement on arc section (~800 tokens), salience ranking |
| 2.10 | All | Tests: `tests/test_prompt_builders.py`, `tests/test_arc_actions.py` |

### Acceptance criteria

- `talk` regression: NPCs without persona unchanged
- `chat` on Warden Kael (9010) uses full persona with trust-filtered secrets
- `rpsay` near guard+priest gives 0-2 reactions, stagger correct
- Malformed JSON response from LLM doesn't crash session — emits farewell
- `check_arc_item` only succeeds when NPC's `arcs_known` includes the arc
- First check on untouched arc auto-promotes status to `aware`
- Arc context block renders ~800 tokens, drops least-salient when over

---

## Phase 3 — Player & Admin Tools

**Goal:** Players can author their own RP sheet. Admins can inspect and override arc state. Existing characters get arc sheets via migration.

### Tasks

| # | Source | What |
|---|--------|------|
| 3.1 | BUILDOUT §3 | `rpsheet` command with all subcommands (bio, personality, goal add/remove, quirk add, pronouns, hide/show, clear) |
| 3.2 | BUILDOUT §3 | GMCP package `Char.RpSheet` for client integration |
| 3.3 | BUILDOUT §3 | Help entry `help rpsheet` |
| 3.4 | ARCS §6.1 | MCP Bridge endpoints: `GET /arc/sheet/...`, `GET /arc/module/...`, `POST /arc/force-check`, `POST /arc/force-status`, `GET /arc/stats` |
| 3.5 | ARCS §6.2 | In-game `@arc view/check/status/stats` commands using ui.py rendering |
| 3.6 | ARCS §7 | Migration function `migrate_character_arc_sheets()` |
| 3.7 | ARCS §7.2 | Migration runs: on character load, on module load (online players), on startup batch (offline files) |
| 3.8 | ARCS §7.3 | Backup files written before migration; orphan preservation |
| 3.9 | ARCS §6.1 | Audit log to `data/audit/arc_overrides.jsonl` |
| 3.10 | All | Tests: `tests/test_rpsheet.py`, `tests/test_migration_arc.py` |

### Acceptance criteria

- Players can run `rpsheet bio "I am terrified of fire"` and chat with a forge-priest who acknowledges it
- `@arc view hormoth` prints readable arc sheet summary
- Force-check via `@arc check ... ...` updates state and audit-logs
- Migration on old player file produces fresh untouched arcs without disturbing existing data
- Backup `.backup.{timestamp}` created before mutation
- All admin commands gated by `is_immortal`

---

## Phase 4 — Module System

**Goal:** Modules can be dropped into `data/modules/{slug}/` and loaded on startup. "The Quiet Graft" scaffold exists (empty but valid structure).

### Tasks

| # | Source | What |
|---|--------|------|
| 4.1 | ARCS §5.1 | Module directory layout convention |
| 4.2 | ARCS §5.2 | `module.json` manifest schema + validator |
| 4.3 | ARCS §5.3 | `arcs.json` schema for arc templates with checklists |
| 4.4 | ARCS §5.4 | Persona file schema in `personas/` |
| 4.5 | ARCS §5.5 | `src/module_loader.py` — discover, dependency-sort, load, merge, register |
| 4.6 | ARCS §5.5 | vnum collision detection — refuse startup with clear error |
| 4.7 | ARCS §5.6 | `scripts/validate_module.py <slug>` — runs all checks |
| 4.8 | ARCS §5 | Scaffold `data/modules/quiet_graft/` with empty-but-valid files |
| 4.9 | All | Tests: `tests/test_module_loader.py` (incl. dependency ordering, vnum collision) |

### Acceptance criteria

- `python scripts/validate_module.py quiet_graft` passes (empty scaffold)
- Module loader integrates with main.py startup
- Two-module dependency test passes
- vnum collision triggers clean refusal with helpful error

---

## Phase 5 — Shadow Chat Game

**Goal:** The headline feature ships. Chat sessions become a real game with state machine, intrusion mechanics, materialization. 8 NPCs are demo-ready.

### Tasks

| # | Source | What |
|---|--------|------|
| 5.1 | BUILDOUT §5.3 | Formalize state machine on `ChatSession` (IDLE → ENTERING → ACTIVE → 5 exit paths) |
| 5.2 | BUILDOUT §5.2.1 | Entry ritual broadcasts (physical room + NPC room) |
| 5.3 | BUILDOUT §5.2.2 | NPC game actions: `modify_reputation`, `grant_quest`, `give_item`, `remember`, `summon_world_event`, `offer_trust`, `bless`, `mark_player` (with rate limits) |
| 5.4 | BUILDOUT §5.2.3 | `eavesdrop <player>` command (Listen vs Will opposed) |
| 5.5 | BUILDOUT §5.2.3 | `disturb <player>` command (force-end + trust penalty) |
| 5.6 | BUILDOUT §5.2.4 | World bleed: weather, room speech, combat, body damage |
| 5.7 | BUILDOUT §5.2.5 | `enter world` materialization (10% HP cost, 1hr cooldown, broadcast) |
| 5.8 | BUILDOUT §5.2.6 | All 5 exit states (clean, materialize, disturbed, timeout, body-death) |
| 5.9 | BUILDOUT §5.4 | Chat UX touches (emotion brackets, dim gray world events, trust upgrade highlights) |
| 5.10 | BUILDOUT §5.5 | Admin endpoints `/chat/active`, `/chat/{id}`, `/chat/{id}/inject`, `/chat/{id}/force-end` |
| 5.11 | BUILDOUT §4 partial | Hand-author 8 exemplar personas (4 existing + 4 new — first batch from priority list) |
| 5.12 | All | Tests: `tests/test_shadow_chat_game.py` |

### Acceptance criteria

- All 5 exit paths tested
- Shadow Presence renders to both rooms
- `eavesdrop` opposed check works with redaction
- `disturb` ends session and applies trust penalty
- `enter world` materializes with 10% HP cost
- Weather change during active chat produces `[WORLD EVENT]` line
- Chat sessions persist with state transitions
- 8 personas validated and produce distinctive opening/farewell lines

---

## Phase 6 — Veil Admin (Different Repo)

**Goal:** DMs can inspect and override arc state from the Veil Client. Player-facing UI unchanged.

**Note:** This phase requires switching to the `C:\data\workspace\VeilClient` repo. Will need explicit user confirmation before starting.

### Tasks

| # | Source | What |
|---|--------|------|
| 6.1 | VEIL §1 | Gateway proxy routes `/api/arc/*` (admin-gated) |
| 6.2 | VEIL §1 | Rate limiting: 60/min reads, 20/min force-*, 10/min audit |
| 6.3 | VEIL §1 | Gateway-side audit logging with admin user_id |
| 6.4 | VEIL §2 | `client/src/admin/ArcPanel.js` with 3 modes (Player lookup / Module browser / Stats) |
| 6.5 | VEIL §2.3 | `admin_only: true` flag in PanelManager |
| 6.6 | VEIL §2.4 | Keyboard shortcuts: `Ctrl+Shift+A` panel, `/`, `Esc`, `r` |
| 6.7 | VEIL §2 | Right-click context menus for force actions |
| 6.8 | VEIL §2 | Stats dashboard with timeline chart |
| 6.9 | All | Tests: `gateway/tests/test_arc_routes.py`, `client/tests/test_arc_panel.js` |

### Acceptance criteria

- Non-admin JWT returns 403 on every arc route
- Panel renders for admins, completely absent for non-admins
- All 3 modes load data and render without crashing on edge cases
- Force-actions update UI immediately and persist to MUD
- Both gateway and MUD audit logs capture force-actions

---

## Phase 7 — Content & Polish (Ongoing)

**Goal:** Fill in the remaining content. Not a discrete phase — more like a rolling expansion.

### Subphases

**7a. Persona backfill (42 NPCs)**
- Create `scripts/backfill_personas.py` for stub generation
- Hand-author each NPC following the Warden Kael exemplar
- Priority groups: faction leaders (5), deity priests (9), city stewards (7), lore keepers (5), shopkeepers (8 minus 2 done), trainers (6), secret faction contacts (3), quest NPCs (4 minus 1 done)

**7b. Veil DM Agent integration (BUILDOUT_VEIL §3)**
- Inject arc context into 5-min decision loop
- Stalled-arc detection
- `nudge_arc` and `propagate_resolution` MCP tools (with rate limits + safety rails)
- `DM_AGENT_ARC_AWARE=false` config flag

**7c. Veil module management (BUILDOUT_VEIL §4)**
- Reload modules button
- Validate module button
- Surface content warnings prominently

**7d. Veil Electron parity (BUILDOUT_VEIL §5)**
- Verify Arc Panel renders identically in Electron
- OS-specific shortcut config
- Tray menu item
- OS notifications for DM Agent decisions

**7e. Quality checks (BUILDOUT §6 + ARCS §8 + VEIL §6)**
- `scripts/validate_personas.py` — zero errors
- `scripts/audit_prompt_lengths.py` — every chat prompt under 2500 tokens, arc section under 800
- `scripts/smoke_chat.py` — 10-turn chat with each exemplar
- `scripts/smoke_arc_chat.py` — arc-state persistence test
- `scripts/smoke_arc_admin.py` — end-to-end admin override flow

**7f. Author "The Quiet Graft" content**
- Following the Canon Bible
- Quest chains, NPC dialogue, room descriptions, lore chunks
- Arc reactions for every NPC who knows about the arc
- Three resolution paths

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| Schema changes break existing 298 tests | Run full suite after every section. Stop and investigate before continuing. |
| Veil and MUD repos drift apart | Keep BUILDOUT_VEIL coordination table current. Do MUD §1-6 first; Veil after. |
| Token budget overflow on arc-aware NPCs | Token audit script in Phase 7e catches it; salience ranking + drop logic in Phase 2 handles it at runtime. |
| Migration corrupts player files | Backup `.backup.{timestamp}` before any migration; never delete checklist items. |
| LLM emits malformed `check_arc_item` JSON | Action executor validates strictly; logs rejection; session continues normally. |
| vnum collision when loading new module | Module loader refuses startup with clear error pointing to colliding modules. |
| Arc state leaks to non-admin UI | Phase 7e has explicit player-facing regression test; treat any leak as critical bug. |

---

## Sequencing Decisions

### Per-section commits, not per-phase
Each section has its own acceptance criteria. Commit when section is green. Don't batch.

### Run tests after every section
`pytest oreka_mud/tests -q -k "not test_levelup"` — must show all green before next section starts. (test_levelup is a known pre-existing failure unrelated to this work.)

### Parallelization
Phase 3, 4, and 5 are independent of each other after Phase 2 is done. They could be done in parallel by separate contributors. With one agent, do them sequentially in the order: 3 → 4 → 5 (player tools first because they're shortest and lowest-risk).

### Stop conditions
- Test regression → stop, investigate
- Schema validator rejects authored content → stop, fix the content
- Player-facing change discovered in a Phase 1-3 section → stop, file as bug

---

## What I Need From You Before Starting

1. **Confirmation to proceed with Phase 1.** It's the longest phase but unblocks everything.
2. **Decision on `BUILDOUT_ARC_MODULE.md` vs `BUILDOUT_ARC_MODULE.md` naming.** The Veil brief references the latter. Quick rename or add a redirect note?
3. **Per-phase pause point or continuous?** I can stop after each phase for review, or run straight through with phase-end summaries.
4. **Test-failure tolerance.** 0 new failures tolerated, or some grace if I document them?

When confirmed, I start with Phase 1 — the four schemas + ArcSheet + ai_persona extension + expression evaluator + tests. Estimated to be the largest single push of the project.

---

## Tracking

Phase tasks are registered in the task tracker (#22-#28). Each phase's acceptance criteria becomes a sub-task as we hit it.
