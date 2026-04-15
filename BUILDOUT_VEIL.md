# Veil — Arc Tracking Admin & DM Agent Integration

**Target agent:** Claude Code (or similar CLI coding agent) working inside the Veil repo (gateway + client + ai + electron).
**Goal:** Surface the MUD's new arc tracking system to DMs and admins through Veil — without exposing any of it to players. Give the DM Agent the arc context it needs to make smarter world-event decisions. Add a minimal admin UI for managing modules and inspecting player arc sheets.

**Rule for the agent:** Do the sections in order. Each section has acceptance criteria. This document is the counterpart to `BUILDOUT_ARC_MODULE.md` in the `oreka_mud` repo — do not start Veil work until at least Sections 1–4 of that document are complete, because the gateway endpoints here proxy MUD-side endpoints that must exist first.

---

## 0. Context (read this first)

The MUD has just shipped the arc tracking system (`BUILDOUT_ARC_MODULE.md`). Every character now has a hidden set of `ArcSheet` objects tracking what they've learned, who they've met, where they've been, and what choices they've made per arc. NPCs react to this state via `arc_reactions` in their `ai_persona`. The data is intentionally invisible to players — the felt experience comes from NPC dialogue, not a UI panel.

Veil's job in this system is **DM-facing**, not player-facing. Specifically:

- **Expose arc sheets to human DMs** through an admin panel, gated by the existing admin/immortal role in JWT claims.
- **Surface module management** so DMs can see which modules are loaded, what arcs exist, which NPCs belong to which modules.
- **Feed arc context to the DM Agent** so its 5-minute decision loop can consider arc progression when choosing world events.
- **Add nothing to player-facing UI.** No quest journal panel. No "what you've learned" tab. No arc indicator on the character sheet. Players experience arcs through NPC dialogue only.

Design decisions already locked in the MUD doc — reaffirmed here:

- **Player UI is untouched.** Even Pro and Ultimate tier players see no arc indicator.
- **Cloud fallback to Claude API is permitted** for arc-aware NPC conversations. The AI Router already supports this; no changes required unless tier policy needs tightening.
- **DM Agent is free to read arc state** when deciding whether to trigger world events. That's new integration work in this doc.

**Do not touch:**

- The player-facing character sheet panel, the Kin-Sense visualizer, combat feed, crafting UI, deity panel, analytics — none of these gain arc awareness.
- The subscription gate logic. Arc admin features are gated by admin role, not subscription tier.
- The existing DM Agent decision logic. Extend only — preserve the 5-minute loop, the safety rails, the manual override.

---

## 1. Gateway: arc admin routes

Extend `gateway/main.py` (or split into `gateway/routes/arc.py` if route count justifies it).

### 1.1 Route list

All routes require admin-role JWT. Return 403 for non-admin callers.

```
GET  /api/arc/sheet/{player_name}              — proxy to MUD MCP: full arc dump
GET  /api/arc/sheet/{player_name}/{arc_id}     — proxy: single arc detail
GET  /api/arc/module/{module_slug}             — proxy: module manifest + arc templates + NPCs
GET  /api/arc/modules                          — proxy: list all loaded modules
POST /api/arc/force-check                      — proxy: admin override checklist item
POST /api/arc/force-status                     — proxy: admin override arc status
GET  /api/arc/stats                            — proxy: aggregate arc stats
GET  /api/arc/audit                            — read the MUD's arc_overrides.jsonl
```

### 1.2 Proxy implementation

These are thin HTTP proxies to the MUD's MCP bridge at port 8001. Pattern:

```python
@app.get("/api/arc/sheet/{player_name}")
async def arc_sheet(player_name: str, user=Depends(require_admin)):
    resp = await mcp_client.get(f"/arc/sheet/{player_name}")
    return resp.json()
```

### 1.3 Rate limiting

- Read routes: 60 req/min per admin user (generous — DMs click around).
- Force-* routes: 20 req/min per admin user (rarer, deliberate actions).
- `/api/arc/audit`: 10 req/min (cheaper to just open once).

### 1.4 Audit logging

Every force-* call gets logged to the gateway's audit log **in addition to** the MUD's audit log, with the calling admin's user_id captured. Cross-reference enables attributing overrides to specific human admins.

### Acceptance — Section 1

- [ ] All routes registered and responding.
- [ ] Non-admin JWT returns 403 on every route.
- [ ] Proxy correctly forwards query params and request bodies.
- [ ] Rate limiting enforced and returns 429 cleanly.
- [ ] Gateway audit log includes admin user_id for force-* calls.
- [ ] Tests in `gateway/tests/test_arc_routes.py` cover: admin success, non-admin 403, proxy forwarding, rate limit trigger.

---

## 2. Client: DM arc panel

Create `client/src/admin/ArcPanel.js`. Registered in the admin section of the panel manager, hidden from non-admin users entirely.

### 2.1 Panel structure

Three modes, switchable by tab:

**Mode A — Player lookup:**
- Search input for player name (autocomplete against online + recently-offline)
- On select, load `/api/arc/sheet/{player_name}`
- Render as a collapsed list of arcs; click an arc to expand its checklist
- Each checklist item shows: label, category icon, state badge (unchecked/checked/detailed), last-changed timestamp, detail blob (if present)
- Right-click an item → context menu → "Force check" / "Force uncheck" / "Edit detail"
- Right-click an arc → context menu → "Set status"

**Mode B — Module browser:**
- List of all loaded modules from `/api/arc/modules`
- Click a module to see its manifest, arc templates, and NPC roster
- NPC roster rows: vnum, name, `arcs_known`, count of `arc_reactions`
- Click an NPC row → open their full persona in a read-only modal

**Mode C — Stats dashboard:**
- Load `/api/arc/stats` on entry
- Per-arc rows: title, # players untouched, # aware, # active, # advancing, # resolved (with resolution breakdown)
- Click-through from any row to a filtered player list
- Timeline chart: checklist-item flips per day over the last 30 days

### 2.2 Styling

Reuse the existing admin CSS conventions. Prefix all new classes `arc-` to avoid collision. Follow the DM Agent panel's visual language since it's a sibling admin tool.

### 2.3 Panel gating

- Panel registration in `client/src/layout/PanelManager.js` includes an `admin_only: true` flag.
- On layout load, non-admin users never see the panel in the panel list, nor can they add it via settings.
- JWT claim `is_admin` drives visibility. If claim is missing or false, panel doesn't render.

### 2.4 Keyboard shortcuts

- `Ctrl+Shift+A` opens/focuses the Arc Panel (admin only)
- Within the panel: `/` focuses search, `Esc` closes modals, `r` refreshes current view

### Acceptance — Section 2

- [ ] Panel renders for admin users and is absent for non-admin users.
- [ ] All three modes (Player lookup, Module browser, Stats dashboard) render and load data.
- [ ] Force check/uncheck, set status, edit detail all work and update UI immediately.
- [ ] Module browser accurately reflects loaded modules.
- [ ] Stats dashboard renders charts without crashing on zero-data edge cases.
- [ ] Tests in `client/tests/test_arc_panel.js` cover: rendering, admin gating, mode switching, force-action flow with mocked gateway.

---

## 3. DM Agent: arc-aware decisions

Modify `ai/dm_agent.py` to include arc state in its decision context.

### 3.1 New context source

In the DM Agent's 5-minute loop, when building the world-state snapshot, add an arc summary section:

```python
arc_context = {
    "arcs_by_activity": [
        {"arc_id": "quiet_graft", "active_players": 12, "advancing_players": 3, "last_flip": 1745000000.0},
        # ... per arc ...
    ],
    "stalled_arcs": [
        # arcs with active players whose last_flip is > 48 real hours ago
    ],
    "recent_resolutions": [
        {"arc_id": "...", "player": "...", "resolution": "...", "when": ...},
    ],
}
```

### 3.2 Decision enhancements

The DM Agent's existing decision logic selects among event types. Extend to consider:

- **Stalled arcs**: If players are stuck on an arc (no flips in 48h), the DM Agent may trigger a nudge event — an NPC migration, a piece of world news that references the arc, a rumor seeded into a tavern's rpsay feed. New MCP tool: `nudge_arc(arc_id, event_template_id)`.
- **Recent resolutions**: If a player recently resolved an arc loudly (say, killed Vaerix), the DM Agent may propagate consequences — downstream factions react, related NPCs update their emotional state, the Spur Tower scholar quarter loses a Records Adjutant. New MCP tool: `propagate_resolution(arc_id, resolution, radius)`.
- **Activity clustering**: If multiple players are all `active` on the same arc simultaneously, the DM Agent avoids nudging — they're creating their own activity, don't disturb.

### 3.3 Safety rails

- `nudge_arc` rate-limited to once per arc per real day across all players.
- `propagate_resolution` rate-limited to once per resolution event (idempotent).
- Human admin can disable DM Agent arc awareness entirely via a config flag `DM_AGENT_ARC_AWARE=false`.
- All arc-driven decisions are logged to the DM Agent decision log with reasoning strings — human-readable explanations of why the Agent chose each action.

### 3.4 New MCP tools

Add to `mcp/server.py` (Veil side) and request the MUD side to expose the corresponding executor endpoints:

```
nudge_arc(arc_id: str, event_template_id: str, radius: str = "regional")
propagate_resolution(arc_id: str, resolution: str, radius: str = "regional")
read_arc_stats()                                 — aggregate stats read
read_arc_activity_by_player(player_name: str)    — single-player arc activity summary
```

The first two are write-permission tools and go through the existing admin permission layer. The latter two are read-only.

### Acceptance — Section 3

- [ ] DM Agent 5-minute loop includes arc context in its snapshot.
- [ ] Stalled-arc detection correctly flags arcs with no recent flips.
- [ ] `nudge_arc` and `propagate_resolution` tools are wired and rate-limited.
- [ ] Config flag `DM_AGENT_ARC_AWARE=false` disables arc influence without disabling the Agent.
- [ ] Decision log entries include reasoning strings referencing specific arcs and players.
- [ ] Tests in `ai/tests/test_dm_agent_arc.py` cover: arc context injection, stalled detection, rate-limit enforcement, disabled-flag respect.

---

## 4. Module management admin UI

Minimal for now. Shipping modules is still primarily a file-drop operation (`data/modules/{slug}/` on the MUD server), but DMs should be able to see what's loaded and trigger a reload.

### 4.1 Endpoints

```
GET  /api/arc/modules                         — already exists from Section 1
POST /api/arc/modules/reload                  — admin: trigger MUD-side module reload
POST /api/arc/modules/{slug}/validate         — admin: run validate_module.py remotely
```

### 4.2 UI additions to ArcPanel Module browser mode

- "Reload modules" button — calls `POST /api/arc/modules/reload`, shows spinner, confirms with result summary
- Per-module "Validate" button — calls `POST /api/arc/modules/{slug}/validate`, shows validation errors inline if any
- Per-module metadata display: version, author, content warnings (surface the `content_warnings` field from manifest prominently)

### 4.3 Out of scope for this phase

- No in-browser module editing. Modules are authored externally, uploaded as files.
- No module upload UI. Admins SCP / rsync modules to the MUD server.
- No module marketplace (Phase 3.12 from original Veil buildout; stays deferred).

### Acceptance — Section 4

- [ ] Reload button triggers MUD-side reload and returns success/failure.
- [ ] Validate button surfaces errors inline, formatted readably.
- [ ] Module metadata renders accurately.
- [ ] Content warnings display prominently on module detail view.
- [ ] Non-admin users cannot call any of these endpoints.

---

## 5. Electron desktop parity

The Electron app needs parity with the browser client. Since the admin panel is a client-side React/Vue component, it inherits automatically. Check:

### 5.1 Verification tasks

- [ ] Launch Electron build as admin user, verify Arc Panel renders identically to browser.
- [ ] Verify keyboard shortcut `Ctrl+Shift+A` works on Windows, Mac, Linux builds (may need OS-specific shortcut config).
- [ ] Verify admin-only system tray menu item: "Open Arc Panel" as a quick jump.
- [ ] Verify OS notifications fire when DM Agent logs a significant arc decision (configurable, default on for admins).

### 5.2 No new code expected

If the panel renders correctly in the browser build and uses no browser-only APIs, Electron should just work. Flag any divergence discovered during verification as a bug, not a feature.

### Acceptance — Section 5

- [ ] Browser and Electron builds produce identical Arc Panel output.
- [ ] Platform-specific shortcut conflicts resolved.
- [ ] Tray menu item present for admin users.
- [ ] OS notification test case fires and dismisses correctly.

---

## 6. Content quality checks

Before merging:

1. **Route regression** — existing gateway routes unaffected. Run full gateway test suite.
2. **Panel regression** — non-admin users see no Arc Panel anywhere. Manual QA with a non-admin JWT.
3. **DM Agent regression** — with `DM_AGENT_ARC_AWARE=false`, decisions are identical to pre-arc baseline. Verify by running the Agent's decision-log replay tool.
4. **End-to-end smoke test** — `scripts/smoke_arc_admin.py`:
   - Logs in as admin
   - Opens Arc Panel
   - Looks up a seeded test player
   - Force-checks a checklist item
   - Verifies change persists on MUD side
   - Views module browser, triggers a validate call
   - Closes panel
5. **Audit log verification** — every force-* action appears in both gateway and MUD audit logs with matching user/player correlation.

---

## 7. Out of scope (explicitly do not do)

- Do not build a player-facing arc view. Not in any tier. Not ever.
- Do not let non-admin users see arc state on other players via any endpoint.
- Do not add arc indicators to the character sheet, Kin-Sense visualizer, combat feed, or any other player panel.
- Do not implement a module marketplace or in-browser module editor. Those are separate projects.
- Do not expose arc state via GMCP. GMCP is player-scope; arc sheets are DM-scope.
- Do not let the DM Agent make decisions that materially harm a player's arc progress without human admin review. The Agent nudges; it does not block.

---

## 8. Milestone ordering

1. **Gateway routes (Section 1)** — unblocks all UI work.
2. **Arc Panel client (Section 2)** — DM tooling lights up.
3. **DM Agent integration (Section 3)** — parallel work, depends on Section 1 for read tools, independent of Section 2.
4. **Module management UI (Section 4)** — final polish layer on the Arc Panel.
5. **Electron parity (Section 5)** — verification, not new code.
6. **Content quality checks (Section 6)** — shippable.

Sections 2 and 3 can be built in parallel by separate contributors once Section 1 is green.

---

## 9. File manifest when complete

```
gateway/
├── routes/
│   └── arc.py                            # NEW (or block in main.py)
└── tests/
    └── test_arc_routes.py                # NEW

client/
├── src/
│   ├── admin/
│   │   └── ArcPanel.js                   # NEW
│   └── layout/
│       └── PanelManager.js               # MODIFIED — admin_only flag
├── styles/
│   └── admin/
│       └── arc-panel.css                 # NEW
└── tests/
    └── test_arc_panel.js                 # NEW

ai/
├── dm_agent.py                           # MODIFIED — arc context + new decisions
└── tests/
    └── test_dm_agent_arc.py              # NEW

mcp/
└── server.py                             # MODIFIED — nudge_arc, propagate_resolution tools

desktop/
└── (no code changes — verification only)

scripts/
└── smoke_arc_admin.py                    # NEW
```

---

## 10. Coordination with `BUILDOUT_ARC_MODULE.md`

This document depends on the MUD-side buildout. Sequencing:

| Veil Section | Depends on MUD Section(s) |
|--------------|--------------------------|
| 1 (Gateway routes) | MUD §6 (admin endpoints) must exist |
| 2 (Arc Panel) | MUD §6 + Veil §1 |
| 3 (DM Agent integration) | MUD §6 + Veil §1 |
| 4 (Module management) | MUD §5 (module loader) + MUD §6 |
| 5 (Electron) | Veil §2 |

The minimum viable milestone across both documents is: MUD §§1–6 complete + Veil §§1–2 complete. That produces a working arc-tracking system with DM inspection and manual override. Everything beyond that — DM Agent integration, module management UI, Electron verification, content authoring — is additive.

---

**End of brief.** Each section's acceptance criteria must be green before the next section starts. Player-facing UI is out of scope forever on this feature — if a reviewer finds arc state leaking to a non-admin view, treat it as a critical bug.
