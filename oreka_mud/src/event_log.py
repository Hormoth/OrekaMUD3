"""
Player Event Logging for OrekaMUD3.
Logs significant player actions for the DM Agent to read.
Written as JSONL (one JSON object per line) for easy streaming.
"""
import json
import os
import time
from datetime import datetime
import logging

logger = logging.getLogger("OrekaMUD.EventLog")

EVENT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "events")
EVENT_LOG_FILE = os.path.join(EVENT_LOG_DIR, "player_events.jsonl")

# Ensure directory exists
os.makedirs(EVENT_LOG_DIR, exist_ok=True)


def log_event(player_name: str, event_type: str, event_data: dict,
              room_vnum: int = None, region: str = None):
    """
    Log a significant player action.

    event_type: "level_up", "mob_kill", "quest_complete", "faction_threshold",
                "deity_prayer", "deity_ascension", "player_death", "item_craft",
                "pvp_kill", "room_enter", "login", "logout"
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "player": player_name,
        "type": event_type,
        "data": event_data,
        "room_vnum": room_vnum,
        "region": region
    }

    try:
        with open(EVENT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write event log: {e}")


def get_recent_events(count: int = 100, event_type: str = None,
                      player: str = None, region: str = None) -> list:
    """Read recent events from the log, optionally filtered."""
    if not os.path.exists(EVENT_LOG_FILE):
        return []

    events = []
    try:
        with open(EVENT_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if event_type and entry.get("type") != event_type:
                        continue
                    if player and entry.get("player") != player:
                        continue
                    if region and entry.get("region") != region:
                        continue
                    events.append(entry)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.error(f"Failed to read event log: {e}")

    # Return most recent
    return events[-count:]


def clear_old_events(days: int = 30):
    """Remove events older than N days."""
    if not os.path.exists(EVENT_LOG_FILE):
        return 0

    cutoff = time.time() - (days * 86400)
    kept = []
    removed = 0

    try:
        with open(EVENT_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    ts = datetime.fromisoformat(entry["timestamp"]).timestamp()
                    if ts >= cutoff:
                        kept.append(line)
                    else:
                        removed += 1
                except Exception:
                    kept.append(line)

        with open(EVENT_LOG_FILE, "w", encoding="utf-8") as f:
            f.writelines(kept)
    except Exception as e:
        logger.error(f"Failed to clean event log: {e}")

    return removed
