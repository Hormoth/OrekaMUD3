# Task: Rebind OrekaMUD and Agamemnon servers to 127.0.0.1

## Context
Network listeners currently bind to `0.0.0.0` (all interfaces). They need to bind to `127.0.0.1` (localhost only). Access will be via Cloudflare Tunnel or RDP — no LAN access needed.

## Scope
Two projects:
- `C:\data\workspace\OrekaMUD3\oreka_mud` (the MUD)
- `C:\data\workspace\Agamenmnon\ai_orchestrator_cli` (Agamemnon AI + Veil gateway)

Do NOT touch `C:\data\workspace\VeilClient`.

---

## Part 1: OrekaMUD

### Current state
Running `python main.py` from `C:\data\workspace\OrekaMUD3\oreka_mud` produces:
- `Starting Oreka MUD server on 0.0.0.0:4000 (raw asyncio TCP)`
- `NPC Chat: starting on ws://0.0.0.0:8767`
- `Map WS: starting on ws://0.0.0.0:8766`
- `WebSocket server started on 0.0.0.0:8765`

MCP Bridge on `127.0.0.1:8001` is already correct — leave alone.

### What to do
1. Search the entire `C:\data\workspace\OrekaMUD3\oreka_mud` tree for `0.0.0.0` in `.py`, `.json`, `.yaml`, `.yml`, `.toml`, `.env`, `.ini`, `.cfg`.
2. Change every `0.0.0.0` → `127.0.0.1` for ports 4000, 8765, 8766, 8767.
3. If bind addresses come from env vars or config files, update the config, not just the code default.

---

## Part 2: Agamemnon (and Veil gateway)

### Current state
Two services in `C:\data\workspace\Agamenmnon\ai_orchestrator_cli`:

**Veil FastAPI gateway** — started with: