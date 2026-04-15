"""
Environment context aggregator for LLM prompts.

Pulls live world state from existing systems (weather engine, narrative
engine, game time, location effects, MCP bridge) into a single dict that
the prompt assembler injects into chat system prompts.

This is plumbing — it doesn't store anything. Every call recomputes from
the live world.
"""

import logging
from typing import Optional

logger = logging.getLogger("OrekaMUD.EnvironmentContext")


# ---------------------------------------------------------------------------
# Region politics — lightweight per-region tension descriptors.
# Authored content; could move to data/regions.json later.
# ---------------------------------------------------------------------------

REGION_POLITICS = {
    "twin_rivers": "Trade Houses jockey for river-route control; Custos do Aeternos remains the de-facto capital.",
    "kinsweave": "Quarry disputes simmer between Stonefall and Highridge; old Eke Concordant runes still settle some.",
    "tidebloom_reach": "Mithril Chains engineering syndicate quietly underwrites the lake economy.",
    "infinite_desert": "Sand Wardens and pilgrim caravans coexist under the Lady of Fire's tacit blessing.",
    "eternal_steppe": "Far Riders ride; the Mytrone Brotherhood's cultural grip tightens after each successful raid.",
    "gatefall_reach": "Frontier crumbling. Wind-Riders thin. The Silence Breach grows in a direction the Council will not name.",
    "deepwater_marches": "Warg settlements + jungle intelligence trade run by the Trade Houses' less-respectable cousins.",
    "chapel": "Aetherial Veil active. All four Lords' shrines maintained.",
    "chainless_legion": "Farborn veterans hold the cliffs. Old grievances kept on a tight leash.",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_environment_context(character, room) -> dict:
    """Aggregate live world state into a single dict for LLM prompt injection.

    Pulls from existing systems where possible, returns safe defaults where
    a system isn't available. Never raises — environment context is best-effort.
    """
    ctx = {
        "time_of_day": _safe_call(_get_time_of_day),
        "season": _safe_call(_get_season),
        "weather": _safe_call(_get_weather, room),
        "weather_forecast": _safe_call(_get_weather_forecast, room),
        "region": _safe_call(_get_region, room),
        "region_politics": "",
        "active_world_events": _safe_call(_get_active_world_events, room),
        "nearby_shrine_status": _safe_call(_get_nearby_shrine, room),
        "story_chapter": _safe_call(_get_current_chapter, character),
    }

    # Fill in region politics from the static map
    region = ctx.get("region")
    if region:
        ctx["region_politics"] = REGION_POLITICS.get(region.lower(), "")

    return ctx


def format_environment_for_prompt(ctx: dict) -> str:
    """Render the environment context dict as a prompt-friendly text block."""
    if not ctx:
        return ""

    lines = ["WORLD STATE:"]

    if ctx.get("time_of_day"):
        time_str = ctx["time_of_day"]
        if ctx.get("season"):
            time_str = f"{time_str}, {ctx['season']}"
        lines.append(f"Time: {time_str}")

    if ctx.get("region"):
        region_label = ctx["region"].replace("_", " ").title()
        lines.append(f"Region: {region_label}")

    if ctx.get("weather") and ctx["weather"] != "clear":
        wline = f"Weather: {ctx['weather']}"
        if ctx.get("weather_forecast"):
            wline += f" (likely shifting to {ctx['weather_forecast']})"
        lines.append(wline)

    if ctx.get("region_politics"):
        lines.append(f"Politics: {ctx['region_politics']}")

    if ctx.get("active_world_events"):
        events = ctx["active_world_events"]
        if isinstance(events, list) and events:
            lines.append("Recent world events:")
            for e in events[:3]:
                lines.append(f"  - {e}")

    if ctx.get("nearby_shrine_status"):
        lines.append(f"Nearby shrine: {ctx['nearby_shrine_status']}")

    if ctx.get("story_chapter"):
        lines.append(f"Player's story chapter: {ctx['story_chapter']}")

    if len(lines) == 1:
        return ""   # nothing to show
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal probes — each one is wrapped in _safe_call to never raise.
# ---------------------------------------------------------------------------

def _safe_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.debug(f"environment probe {fn.__name__} failed: {e}")
        return None


def _get_time_of_day() -> Optional[str]:
    from src.schedules import get_game_time
    gt = get_game_time()
    # Prefer a structured phase if available; fall back to full string
    phase = getattr(gt, "phase", None)
    if phase:
        return phase
    full = getattr(gt, "get_full_time_string", None)
    if callable(full):
        return full()
    return None


def _get_season() -> Optional[str]:
    from src.schedules import get_game_time
    gt = get_game_time()
    season = getattr(gt, "season", None) or getattr(gt, "month_name", None)
    return season


def _get_weather(room) -> Optional[str]:
    if room is None:
        return None
    # Try dynamic weather engine first
    try:
        from src.weather import get_weather_manager
        wm = get_weather_manager()
        return wm.get_weather(room.vnum)
    except Exception:
        pass
    return getattr(room, "weather", None)


def _get_weather_forecast(room) -> Optional[str]:
    if room is None:
        return None
    try:
        from src.weather import get_weather_manager
        wm = get_weather_manager()
        region = wm.get_region(room.vnum)
        if region:
            forecast = wm.get_forecast(region)
            if isinstance(forecast, dict):
                return forecast.get("likely_next")
    except Exception:
        pass
    return None


def _get_region(room) -> Optional[str]:
    if room is None:
        return None
    explicit = getattr(room, "region", None)
    if explicit:
        return explicit
    try:
        from src.weather import get_weather_manager
        wm = get_weather_manager()
        return wm.get_region(room.vnum)
    except Exception:
        return None


def _get_active_world_events(room) -> Optional[list]:
    """Best-effort — pull from event log if available."""
    try:
        from src.event_log import get_recent_events
        events = get_recent_events(count=3, event_type="world_event")
        if events:
            return [e.get("text", "") if isinstance(e, dict) else str(e) for e in events]
    except Exception:
        pass
    return []


def _get_nearby_shrine(room) -> Optional[str]:
    if room is None:
        return None
    flags = getattr(room, "flags", []) or []
    if "shrine" in flags or "altar" in flags:
        return getattr(room, "name", "an unnamed shrine")
    return None


def _get_current_chapter(character) -> Optional[str]:
    if character is None:
        return None
    progress = getattr(character, "narrative_progress", None) or []
    if not progress:
        return "untouched"
    return progress[-1]
