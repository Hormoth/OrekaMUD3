"""
Arc sheet migration for existing characters.

When new arcs are added (via module loading), every character — online and
offline — gets the new arc sheets appended to their save file. Existing
state is never touched. Items removed from a module's template are
preserved on the character with `orphaned: true` (DM-visible).
"""

import os
import json
import time
import shutil
import logging

logger = logging.getLogger("OrekaMUD.ArcMigration")


def migrate_character_arc_sheets(char_data: dict, registered_arcs: list) -> dict:
    """Mutate char_data dict to ensure it has every registered arc.

    Args:
        char_data: character dict (loaded from JSON, before Character.from_dict)
        registered_arcs: list of arc template dicts from module arcs.json files.
            Each must have: arc_id (str), title (str), checklist (list of dicts)

    Returns:
        The mutated char_data dict.

    Behavior:
        - Adds missing arc_sheets entries as fresh untouched sheets.
        - Adds new checklist items to existing arc sheets as unchecked.
        - Marks items present on the character but absent in the template as orphaned.
        - Never removes or downgrades existing non-unchecked state.
    """
    if not isinstance(char_data, dict):
        return char_data

    existing_arcs = char_data.setdefault("arc_sheets", {})

    for arc_template in registered_arcs:
        if not isinstance(arc_template, dict):
            continue
        arc_id = arc_template.get("arc_id")
        if not arc_id:
            continue
        title = arc_template.get("title", arc_id)
        template_items = arc_template.get("checklist", []) or []
        template_item_ids = {ci.get("id") for ci in template_items if ci.get("id")}

        if arc_id not in existing_arcs:
            # Fresh untouched arc sheet
            existing_arcs[arc_id] = {
                "arc_id": arc_id,
                "title": title,
                "status": "untouched",
                "resolution": None,
                "checklist": [
                    {
                        "id": ci.get("id"),
                        "label": ci.get("label", ""),
                        "category": ci.get("category", "fact_learned"),
                        "state": "unchecked",
                        "detail": {},
                        "first_changed_at": None,
                        "last_changed_at": None,
                        "orphaned": False,
                    }
                    for ci in template_items if ci.get("id")
                ],
                "entered_at": None,
                "last_activity_at": None,
                "flags": {},
            }
            logger.info(
                f"migrate: added new arc '{arc_id}' "
                f"({len(template_items)} items) to character"
            )
        else:
            # Existing sheet — append any new items, mark missing as orphaned
            sheet = existing_arcs[arc_id]
            sheet["title"] = title  # update title in case it changed
            existing_checklist = sheet.setdefault("checklist", [])
            existing_item_ids = {ci.get("id") for ci in existing_checklist if ci.get("id")}

            # Add new items as unchecked
            added = 0
            for ci in template_items:
                cid = ci.get("id")
                if not cid or cid in existing_item_ids:
                    continue
                existing_checklist.append({
                    "id": cid,
                    "label": ci.get("label", ""),
                    "category": ci.get("category", "fact_learned"),
                    "state": "unchecked",
                    "detail": {},
                    "first_changed_at": None,
                    "last_changed_at": None,
                    "orphaned": False,
                })
                added += 1
            if added:
                logger.info(
                    f"migrate: added {added} new checklist items to arc '{arc_id}'"
                )

            # Mark items as orphaned if no longer in template
            orphaned = 0
            for ci in existing_checklist:
                cid = ci.get("id")
                if cid and cid not in template_item_ids and not ci.get("orphaned"):
                    ci["orphaned"] = True
                    orphaned += 1
            if orphaned:
                logger.info(
                    f"migrate: marked {orphaned} items orphaned in arc '{arc_id}'"
                )

    return char_data


def migrate_player_file(player_path: str, registered_arcs: list, backup: bool = True) -> bool:
    """Run migration on an offline player JSON file. Returns True if file changed.

    Creates a .backup.<timestamp> copy before mutation when backup=True.
    """
    if not os.path.exists(player_path):
        return False

    try:
        with open(player_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"migrate: failed to load {player_path}: {e}")
        return False

    # Snapshot for diff detection
    before = json.dumps(data.get("arc_sheets", {}), sort_keys=True)
    data = migrate_character_arc_sheets(data, registered_arcs)
    after = json.dumps(data.get("arc_sheets", {}), sort_keys=True)

    if before == after:
        return False

    # Write backup
    if backup:
        ts = time.strftime("%Y%m%d_%H%M%S")
        backup_path = f"{player_path}.backup.{ts}"
        try:
            shutil.copy2(player_path, backup_path)
            logger.info(f"migrate: backup {backup_path}")
        except Exception as e:
            logger.error(f"migrate: backup failed for {player_path}: {e}")
            return False

    # Atomic write
    tmp_path = player_path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, player_path)
        logger.info(f"migrate: updated {player_path}")
        return True
    except Exception as e:
        logger.error(f"migrate: write failed for {player_path}: {e}")
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return False


def migrate_all_offline_players(players_dir: str, registered_arcs: list) -> dict:
    """Walk the players directory and migrate every .json file.

    Returns dict: {"migrated": n, "skipped": n, "errors": n}
    """
    stats = {"migrated": 0, "skipped": 0, "errors": 0}
    if not os.path.isdir(players_dir):
        return stats

    for filename in os.listdir(players_dir):
        if not filename.endswith(".json"):
            continue
        # Skip backups and deleted files
        if ".backup." in filename or filename.endswith(".bak.json") or filename.endswith(".deleted"):
            continue
        path = os.path.join(players_dir, filename)
        try:
            if migrate_player_file(path, registered_arcs):
                stats["migrated"] += 1
            else:
                stats["skipped"] += 1
        except Exception as e:
            logger.error(f"migrate: error on {filename}: {e}")
            stats["errors"] += 1

    return stats


def migrate_online_player(character, registered_arcs: list) -> bool:
    """Run migration on an online Character object's in-memory arc_sheets.

    Returns True if state changed.
    """
    from src.ai_schemas.arc_sheet import ArcSheet, ChecklistItem

    # Use the dict-level migration on a serialized snapshot
    snapshot = {
        "arc_sheets": {
            arc_id: (sheet.to_dict() if hasattr(sheet, 'to_dict') else sheet)
            for arc_id, sheet in (getattr(character, 'arc_sheets', {}) or {}).items()
        }
    }
    before = json.dumps(snapshot["arc_sheets"], sort_keys=True)
    snapshot = migrate_character_arc_sheets(snapshot, registered_arcs)
    after = json.dumps(snapshot["arc_sheets"], sort_keys=True)

    if before == after:
        return False

    # Reload arc_sheets from the migrated snapshot
    character.arc_sheets = {}
    for arc_id, sheet_data in snapshot["arc_sheets"].items():
        character.arc_sheets[arc_id] = ArcSheet.from_dict(sheet_data)

    return True
