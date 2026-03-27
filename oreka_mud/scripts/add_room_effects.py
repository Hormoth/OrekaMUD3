#!/usr/bin/env python
"""Add room effects to area JSON files.

This script adds kin-sense modifiers, elemental resonance, environmental hazards,
rune-circles, and sanctuary effects to specific rooms across the OrekaMUD3 area files.
"""

import json
import os

AREAS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "areas")

# ──────────────────────────────────────────────
# Effects mapping: vnum -> list of effect dicts
# ──────────────────────────────────────────────

EFFECTS: dict[int, list[dict]] = {}


def add(vnum: int, effect: dict):
    EFFECTS.setdefault(vnum, []).append(effect)


# ═══════════════════════════════════════════════
# Kin-Sense Dead Zones
# ═══════════════════════════════════════════════

# InfiniteDesert.json
add(8240, {"type": "kin_sense_modifier", "mode": "dead",
           "message": "Your Kin-sense dies completely. The fused glass swallows all resonance."})
add(8241, {"type": "kin_sense_modifier", "mode": "dead",
           "message": "Absolute silence in your Kin-sense. Nothing lives here in any elemental sense."})
add(8242, {"type": "kin_sense_modifier", "mode": "dead",
           "message": "Your Kin-sense is dead. The Deceiver army's march fused the sand and burned out all resonance."})
add(8244, {"type": "kin_sense_modifier", "mode": "dead",
           "message": "Your Kin-sense goes completely dark. Something here actively suppresses it."})

# ═══════════════════════════════════════════════
# Kin-Sense Flickering Zones
# ═══════════════════════════════════════════════

# Kinsweave.json
add(5441, {"type": "kin_sense_modifier", "mode": "flickering", "dc": 16,
           "message": "Your Kin-sense stutters. The resonance of thousands who died in anguish bleeds through the soil."})
add(5442, {"type": "kin_sense_modifier", "mode": "flickering", "dc": 16,
           "message": "Your Kin-sense flickers erratically. The wound in the world's fabric is strongest here."})
add(5443, {"type": "kin_sense_modifier", "mode": "flickering", "dc": 16,
           "message": "Your Kin-sense wavers. Grief resonates through the earth itself."})

# EternalSteppe.json
add(7213, {"type": "kin_sense_modifier", "mode": "flickering", "dc": 16,
           "message": "Your Kin-sense flickers dangerously. The central dead zone of Dark Dawn still pulses."})
add(7214, {"type": "kin_sense_modifier", "mode": "flickering", "dc": 16,
           "message": "Your Kin-sense is unstable here. Dark Dawn's echo has not faded."})

# ═══════════════════════════════════════════════
# Kin-Sense Amplified Zones
# ═══════════════════════════════════════════════

# EternalSteppe.json
add(7236, {"type": "kin_sense_modifier", "mode": "amplified",
           "message": "Your Kin-sense sharpens dramatically. The Windstone's rune-circle amplifies every resonance."})
add(7237, {"type": "kin_sense_modifier", "mode": "amplified",
           "message": "Your Kin-sense rings clear as a bell. Giant-era magic amplifies your perception."})
add(7000, {"type": "kin_sense_modifier", "mode": "amplified",
           "message": "Your Kin-sense is crystal clear here. The Great Windstone amplifies all resonance."})

# GatefallReach.json
add(12010, {"type": "kin_sense_modifier", "mode": "amplified",
            "message": "The Vigil Stone sharpens your Kin-sense. Every presence within the garrison rings clear."})
add(12086, {"type": "kin_sense_modifier", "mode": "amplified",
            "message": "The Windstone amplifies your Kin-sense, extending your awareness across the grassland."})

# ═══════════════════════════════════════════════
# Elemental Resonance Zones
# ═══════════════════════════════════════════════

# InfiniteDesert.json
add(8004, {"type": "elemental_resonance", "element": "fire", "bonus": 2,
           "message": "The eternal flame radiates fire-element power. Spellcasters attuned to fire feel their power surge."})
add(8006, {"type": "elemental_resonance", "element": "fire", "bonus": 1,
           "message": "Heat from the magma vents saturates the air with fire resonance."})
add(8028, {"type": "elemental_resonance", "element": "fire", "bonus": 2,
           "message": "Raw volcanic fire energy pours from the vents."})

# TwinRivers.json
add(10016, {"type": "elemental_resonance", "element": "water", "bonus": 1,
            "message": "Pekakarlik water-engineering fills this space with cool water resonance."})
add(10065, {"type": "elemental_resonance", "element": "fire", "bonus": 1,
            "message": "The forge-fires carry strong fire-element resonance."})

# Kinsweave.json
add(5042, {"type": "elemental_resonance", "element": "earth", "bonus": 2,
           "message": "The earth element pulses strongly through this ancient shrine."})
add(5076, {"type": "elemental_resonance", "element": "water", "bonus": 1,
           "message": "The Great River's water resonance fills this shrine."})
add(5124, {"type": "elemental_resonance", "element": "fire", "bonus": 2,
           "message": "Volcanic heat from the Scorchspires feeds this shrine with fire energy."})

# WildernessConnectors.json
add(11002, {"type": "elemental_resonance", "element": "fire", "bonus": 1,
            "message": "Volcanic heat seeps from the rock. Fire energy is tangible."})
add(11003, {"type": "elemental_resonance", "element": "fire", "bonus": 2,
            "message": "Lava vents below radiate intense fire resonance."})

# ═══════════════════════════════════════════════
# Environmental Hazards
# ═══════════════════════════════════════════════

# InfiniteDesert.json
add(8307, {"type": "hazard", "damage_type": "fire", "save": "fort", "dc": 12,
           "damage": "1d4", "interval": 300, "resist_element": "fire",
           "message": "The desert sun beats down mercilessly. Without protection, the heat will kill."})
add(8309, {"type": "hazard", "damage_type": "fire", "save": "fort", "dc": 10,
           "damage": "1d4", "interval": 300, "resist_element": "fire",
           "message": "The desert sun beats down mercilessly. Without protection, the heat will kill."})
add(8028, {"type": "hazard", "damage_type": "fire", "save": "fort", "dc": 14,
           "damage": "1d6", "interval": 180, "resist_element": "fire",
           "message": "Volcanic gases and extreme heat fill this chamber."})

# WildernessConnectors.json
add(11102, {"type": "hazard", "damage_type": "cold", "save": "fort", "dc": 12,
            "damage": "1d4", "interval": 300, "resist_element": "wind",
            "message": "Wind howls through the exposed summit, cutting through clothing."})
add(11105, {"type": "hazard", "damage_type": "fire", "save": "fort", "dc": 13,
            "damage": "1d4", "interval": 300, "resist_element": "fire",
            "message": "The open desert offers no shelter from the punishing sun."})

# ═══════════════════════════════════════════════
# Rune-Circles
# ═══════════════════════════════════════════════

# EternalSteppe.json
add(7236, {"type": "rune_circle", "state": "active", "attunement": "earth",
           "power": "teleport", "study_dc": 18, "activate_dc": 15})
add(7237, {"type": "rune_circle", "state": "active", "attunement": "wind",
           "power": "weather", "study_dc": 18, "activate_dc": 15})
add(7239, {"type": "rune_circle", "state": "active", "attunement": "wind",
           "power": "teleport", "study_dc": 18, "activate_dc": 15})

# InfiniteDesert.json
add(8040, {"type": "rune_circle", "state": "active", "attunement": "fire",
           "power": "amplify", "study_dc": 20, "activate_dc": 18})
add(8112, {"type": "rune_circle", "state": "active", "attunement": "earth",
           "power": "heal", "study_dc": 16, "activate_dc": 12})
add(8261, {"type": "rune_circle", "state": "active", "attunement": "earth",
           "power": "teleport", "study_dc": 22, "activate_dc": 20})

# GatefallReach.json
add(12074, {"type": "rune_circle", "state": "dormant", "attunement": "earth",
            "power": "ward", "study_dc": 18, "activate_dc": 16})
add(12135, {"type": "rune_circle", "state": "active", "attunement": "wind",
            "power": "heal", "study_dc": 16, "activate_dc": 14})
add(12136, {"type": "rune_circle", "state": "damaged", "attunement": "wind",
            "power": "amplify", "study_dc": 20, "activate_dc": 18})

# Chapel.json
add(1000, {"type": "rune_circle", "state": "active", "attunement": "all",
           "power": "heal", "study_dc": 15, "activate_dc": 10})

# TwinRivers.json
add(10131, {"type": "rune_circle", "state": "active", "attunement": "earth",
            "power": "heal", "study_dc": 16, "activate_dc": 12})
add(10433, {"type": "rune_circle", "state": "dormant", "attunement": "wind",
            "power": "amplify", "study_dc": 22, "activate_dc": 20})

# ═══════════════════════════════════════════════
# Sanctuaries
# ═══════════════════════════════════════════════

# CustosDoAeternos.json
add(4007, {"type": "sanctuary", "deity": "Kaile'a", "healing_bonus": 3, "rest_multiplier": 2.0})
add(4027, {"type": "sanctuary", "deity": "Cinvarin", "healing_bonus": 2, "rest_multiplier": 1.5})
add(4029, {"type": "sanctuary", "deity": "Kaile'a", "healing_bonus": 4, "rest_multiplier": 2.0})
add(4030, {"type": "sanctuary", "deity": "Semyon", "healing_bonus": 3, "rest_multiplier": 2.0})
add(4031, {"type": "sanctuary", "deity": "Ludus Galerius", "healing_bonus": 2, "rest_multiplier": 1.5})
add(4032, {"type": "sanctuary", "deity": "Gonmareck Ritler", "healing_bonus": 2, "rest_multiplier": 1.5})

# Kinsweave.json
add(5009, {"type": "sanctuary", "deity": "Ludus Galerius", "healing_bonus": 2, "rest_multiplier": 1.5})
add(5042, {"type": "sanctuary", "deity": "Lord of Stone", "healing_bonus": 2, "rest_multiplier": 1.5})
add(5076, {"type": "sanctuary", "deity": "Kaile'a", "healing_bonus": 2, "rest_multiplier": 1.5})
add(5124, {"type": "sanctuary", "deity": "Lady of Fire", "healing_bonus": 2, "rest_multiplier": 1.5})
add(5146, {"type": "sanctuary", "deity": "Kaile'a", "healing_bonus": 2, "rest_multiplier": 1.5})

# InfiniteDesert.json
add(8004, {"type": "sanctuary", "deity": "Lady of Fire", "healing_bonus": 3, "rest_multiplier": 2.0})
add(8112, {"type": "sanctuary", "deity": "Lord of Stone", "healing_bonus": 2, "rest_multiplier": 1.5})
add(8115, {"type": "sanctuary", "deity": "Lord of Stone", "healing_bonus": 2, "rest_multiplier": 1.5})


# ═══════════════════════════════════════════════
# Main script
# ═══════════════════════════════════════════════

def main():
    # Collect which vnums belong to which file (for reporting)
    all_vnums_needed = set(EFFECTS.keys())
    vnums_found = set()
    total_effects_added = 0
    files_modified = []

    for filename in sorted(os.listdir(AREAS_DIR)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(AREAS_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            rooms = json.load(f)

        modified = False
        file_changes = []

        for room in rooms:
            vnum = room["vnum"]
            if vnum in EFFECTS:
                vnums_found.add(vnum)
                existing = room.get("effects", [])
                new_effects = EFFECTS[vnum]
                room["effects"] = existing + new_effects
                modified = True
                count = len(new_effects)
                total_effects_added += count
                types = ", ".join(e["type"] for e in new_effects)
                file_changes.append(f"  vnum {vnum} ({room['name']}): +{count} effect(s) [{types}]")

        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(rooms, f, indent=2, ensure_ascii=False)
            files_modified.append(filename)
            print(f"\n{filename}:")
            for line in file_changes:
                print(line)

    # Report
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files modified: {len(files_modified)}")
    print(f"  Rooms updated: {len(vnums_found)}")
    print(f"  Total effects added: {total_effects_added}")

    missing = all_vnums_needed - vnums_found
    if missing:
        print(f"\n  WARNING - vnums not found in any file: {sorted(missing)}")
    else:
        print(f"  All {len(all_vnums_needed)} target vnums found and updated.")


if __name__ == "__main__":
    main()
