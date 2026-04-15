#!/usr/bin/env python3
"""Validate every ai_persona block in the project.

Sources scanned:
  - data/mobs.json (placed mobs)
  - data/modules/*/personas/*.json (module persona files)

Exit code 0 = all valid, 1 = errors found.
"""
import json
import os
import sys
import glob

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


def main():
    from src.ai_schemas import validate_persona

    total_personas = 0
    total_errors = 0
    failed_sources = []

    # ---- mobs.json ----
    mobs_path = os.path.join(parent_dir, "data", "mobs.json")
    if os.path.exists(mobs_path):
        with open(mobs_path, "r", encoding="utf-8") as f:
            mobs = json.load(f)
        for m in mobs:
            persona = m.get("ai_persona")
            if not persona:
                continue
            total_personas += 1
            errors = validate_persona(persona)
            if errors:
                total_errors += len(errors)
                failed_sources.append(
                    f"mobs.json vnum {m.get('vnum')} ({m.get('name', '?')}):\n  "
                    + "\n  ".join(errors)
                )

    # ---- module personas ----
    modules_dir = os.path.join(parent_dir, "data", "modules")
    if os.path.isdir(modules_dir):
        for persona_file in glob.glob(os.path.join(modules_dir, "*", "personas", "*.json")):
            try:
                with open(persona_file, "r", encoding="utf-8") as f:
                    persona = json.load(f)
            except Exception as e:
                failed_sources.append(f"{persona_file}: failed to parse: {e}")
                total_errors += 1
                continue
            total_personas += 1
            errors = validate_persona(persona)
            if errors:
                total_errors += len(errors)
                rel = os.path.relpath(persona_file, parent_dir)
                failed_sources.append(f"{rel}:\n  " + "\n  ".join(errors))

    # ---- Report ----
    print(f"Validated {total_personas} personas, {total_errors} error(s).")
    if failed_sources:
        print()
        for src in failed_sources:
            print(f"[X] {src}")
            print()
        return 1
    print("[OK] All personas pass validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
