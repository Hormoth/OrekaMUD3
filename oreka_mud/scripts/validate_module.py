#!/usr/bin/env python3
"""Validate a module's content. Exit code 0 = valid, 1 = errors found.

Usage: python scripts/validate_module.py <module_slug>
       python scripts/validate_module.py --all
"""

import os
import sys

# Ensure the parent dir is on the path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


def validate_one(slug: str, modules_root: str) -> int:
    from src.module_loader import load_module, validate_module
    module_dir = os.path.join(modules_root, slug)
    if not os.path.isdir(module_dir):
        print(f"[X] No such module directory: {module_dir}")
        return 1
    try:
        mod = load_module(module_dir)
    except Exception as e:
        print(f"[X] Failed to load module: {e}")
        return 1
    errors = validate_module(mod)
    if errors:
        print(f"[X] {slug}: {len(errors)} error(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"[OK] {slug}: validated. "
          f"arcs={len(mod.arcs)} personas={len(mod.personas)} "
          f"mobs={len(mod.mobs)} rooms={len(mod.rooms)} "
          f"quests={len(mod.quests)} hooks={len(mod.narrative_hooks)} "
          f"lore_files={len(mod.lore_files)}")
    return 0


def main():
    modules_root = os.path.join(parent_dir, 'data', 'modules')
    args = sys.argv[1:]

    if not args:
        print("Usage: python scripts/validate_module.py <module_slug>")
        print("       python scripts/validate_module.py --all")
        return 2

    if args[0] == "--all":
        if not os.path.isdir(modules_root):
            print(f"[X] modules dir does not exist: {modules_root}")
            return 1
        slugs = sorted(d for d in os.listdir(modules_root)
                       if os.path.isdir(os.path.join(modules_root, d)))
        if not slugs:
            print("No modules found.")
            return 0
        rc = 0
        for slug in slugs:
            if validate_one(slug, modules_root) != 0:
                rc = 1
        return rc

    return validate_one(args[0], modules_root)


if __name__ == "__main__":
    sys.exit(main())
