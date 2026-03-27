#!/usr/bin/env python3
"""Parse Oreka_All_Monster_Entries.docx into mobs_bestiary.json."""

import json
import os
import re
import sys

import docx
from docx.table import Table
from docx.text.paragraph import Paragraph


# ─── Helpers ────────────────────────────────────────────────────────────

def normalize_dashes(text: str) -> str:
    """Replace en-dash, em-dash, and similar with hyphen for numeric parsing."""
    return text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2012", "-")


def parse_int(s: str) -> int:
    """Parse an integer from a string, handling +/- prefixes and dashes."""
    s = normalize_dashes(s).strip().lstrip("+")
    if not s or s == "\u2014" or s == "-":
        return 0
    return int(s)


def parse_cr(val: str):
    """Parse Challenge Rating, handling fractions and compound values."""
    val = normalize_dashes(val).strip()
    # Compound: "½ (individual); 3 (hunting band of 6)" -> take first number
    # Also: "1 (Medium); 2 (Large)" -> take first
    if ";" in val:
        val = val.split(";")[0].strip()
    # Remove parenthetical
    val = re.sub(r"\s*\(.*?\)", "", val).strip()
    # Unicode fraction
    if "\u00bd" in val:  # ½
        return 0.5
    if "\u2153" in val:  # ⅓
        return 0.33
    if "\u00bc" in val:  # ¼
        return 0.25
    # Textual fractions
    if "/" in val:
        parts = val.split("/")
        try:
            return round(int(parts[0]) / int(parts[1]), 2)
        except (ValueError, ZeroDivisionError):
            pass
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return val  # fallback: store raw


def parse_hp_dice(val: str):
    """Parse hit dice like '8d8+32 (68 hp)' -> [8, 8, 32]."""
    val = normalize_dashes(val).strip()
    m = re.match(r"(\d+)d(\d+)\s*([+-]\s*\d+)?", val)
    if not m:
        return [1, 8, 0]
    n = int(m.group(1))
    d = int(m.group(2))
    bonus = 0
    if m.group(3):
        bonus = int(m.group(3).replace(" ", ""))
    return [n, d, bonus]


def parse_initiative(val: str) -> int:
    val = normalize_dashes(val).strip()
    m = re.match(r"([+-]?\d+)", val)
    return int(m.group(1)) if m else 0


def parse_speed(val: str) -> dict:
    """Parse speed like '30 ft. (6 squares), climb 15 ft.' -> {land: 30, climb: 15}."""
    speed = {}
    val = normalize_dashes(val).strip()
    # Match patterns: "30 ft." at start (land), "climb 15 ft.", "fly 60 ft.", etc.
    # First, check for leading number (land speed)
    m = re.match(r"(\d+)\s*ft\.", val)
    if m:
        speed["land"] = int(m.group(1))
    # Named speeds
    for match in re.finditer(r"(burrow|climb|fly|swim)\s+(\d+)\s*ft\.", val, re.IGNORECASE):
        speed[match.group(1).lower()] = int(match.group(2))
    if not speed:
        speed["land"] = 30  # fallback
    return speed


def parse_ac(val: str) -> int:
    """Extract first integer from AC string."""
    val = normalize_dashes(val).strip()
    m = re.match(r"(\d+)", val)
    return int(m.group(1)) if m else 10


def parse_single_attack(text: str) -> dict:
    """Parse a single attack like 'Claw +8 melee (1d6+6)' or 'Bite +4 ranged (1d4-1 plus poison)'.
    Returns {"type": ..., "bonus": ..., "damage": ...}."""
    text = normalize_dashes(text).strip()
    # Pattern: <name> +/-N melee/ranged [touch] (<damage>)
    m = re.match(
        r"(?:\d+\s+)?(.+?)\s+([+-]?\d+)\s+(?:melee|ranged)(?:\s+touch)?\s*\(([^)]+)\)",
        text, re.IGNORECASE
    )
    if m:
        name = m.group(1).strip().lower()
        # Clean up prefixes like "Tiny", "Small", etc.
        name = re.sub(r"^(tiny|small|medium|large|huge|gargantuan|colossal)\s+", "", name, flags=re.IGNORECASE)
        bonus = int(m.group(2))
        damage_str = m.group(3).strip()
        return {"type": name, "bonus": bonus, "damage": damage_str}
    return None


def parse_damage_dice(damage_str: str):
    """Extract primary damage dice from damage string like '1d6+4' or '2d6+4 plus slime'.
    Returns [N, D, B] list."""
    damage_str = normalize_dashes(damage_str).strip()
    m = re.match(r"(\d+)d(\d+)\s*([+-]\s*\d+)?", damage_str)
    if m:
        n = int(m.group(1))
        d = int(m.group(2))
        b = int(m.group(3).replace(" ", "")) if m.group(3) else 0
        return [n, d, b]
    # No dice (e.g. "0")
    return [0, 0, 0]


def parse_attacks(attack_val: str, full_attack_val: str):
    """Parse Attack and Full Attack fields into attacks list and primary damage_dice."""
    attacks = []
    seen = set()

    # Use Full Attack if available, else Attack
    source = full_attack_val if full_attack_val.strip() else attack_val
    source = normalize_dashes(source).strip()

    # Split on " and " but not inside parentheses
    # First, split on " and " outside parens
    parts = re.split(r"\s+and\s+", source)

    for part in parts:
        # Each part may have "or" alternatives - take each
        alternatives = re.split(r"\s+or\s+", part)
        for alt in alternatives:
            alt = alt.strip()
            # Handle "2 claws +8 melee (1d6+6)" -> count prefix
            count_match = re.match(r"(\d+)\s+(.+)", alt)
            count = 1
            attack_text = alt
            if count_match:
                count = int(count_match.group(1))
                attack_text = count_match.group(2)

            parsed = parse_single_attack(attack_text)
            if not parsed:
                # Try without count prefix
                parsed = parse_single_attack(alt)
            if parsed:
                key = (parsed["type"], parsed["bonus"])
                if key not in seen:
                    seen.add(key)
                    attacks.append(parsed)

    # Primary damage dice from first attack
    damage_dice = [1, 4, 0]
    if attacks:
        damage_dice = parse_damage_dice(attacks[0]["damage"])

    return attacks, damage_dice


def parse_saves(val: str) -> dict:
    """Parse saves like 'Fort +6, Ref +5, Will +2'."""
    val = normalize_dashes(val).strip()
    saves = {"Fort": 0, "Ref": 0, "Will": 0}
    for save_name in ("Fort", "Ref", "Will"):
        m = re.search(rf"{save_name}\s+([+-]?\d+)", val)
        if m:
            saves[save_name] = int(m.group(1))
        else:
            # Check for null/dash
            m2 = re.search(rf"{save_name}\s+(null|—|-)", val)
            if m2:
                saves[save_name] = None
    return saves


def parse_abilities(val: str) -> dict:
    """Parse abilities like 'Str 22, Dex 15, Con 14, Int 2, Wis 12, Cha 7'."""
    val = normalize_dashes(val).strip()
    abilities = {}
    for ability in ("Str", "Dex", "Con", "Int", "Wis", "Cha"):
        m = re.search(rf"{ability}\s+(\d+|—|-|null)", val)
        if m:
            v = m.group(1)
            if v in ("\u2014", "-", "null", "\u2013"):
                abilities[ability] = None
            else:
                abilities[ability] = int(v)
        else:
            abilities[ability] = 10  # fallback
    return abilities


def parse_skills(val: str) -> dict:
    """Parse skills like 'Climb +14, Listen +5, Move Silently +4, Spot +6'.
    Handle multi-word skills and parenthetical modifiers."""
    val = normalize_dashes(val).strip()
    if not val or val == "\u2014" or val == "-":
        return {}
    skills = {}
    # Match: skill name (letters/spaces) followed by +/-N, possibly followed by (modifier)
    for m in re.finditer(r"([A-Z][\w ]*?)\s+([+-]\d+)(?:\s*\([^)]*\))?", val):
        name = m.group(1).strip()
        bonus = int(m.group(2))
        if name and name not in skills:
            skills[name] = bonus
    return skills


def parse_comma_list(val: str) -> list:
    """Split on commas, strip, filter empties."""
    val = normalize_dashes(val).strip()
    if not val or val == "\u2014" or val == "-":
        return []
    return [item.strip() for item in val.split(",") if item.strip()]


def parse_size_from_type(size_type: str) -> str:
    """Extract size from Size/Type like 'Large Animal' -> 'Large'."""
    sizes = ["Fine", "Diminutive", "Tiny", "Small", "Medium", "Large",
             "Huge", "Gargantuan", "Colossal"]
    for size in sizes:
        if size_type.startswith(size):
            return size
    return "Medium"


def parse_type_from_size_type(size_type: str) -> str:
    """Extract type from Size/Type like 'Large Animal' -> 'Animal',
    'Huge Outsider (Aquatic, Extraplanar)' -> 'Outsider'."""
    # Remove size prefix
    sizes = ["Fine", "Diminutive", "Tiny", "Small", "Medium", "Large",
             "Huge", "Gargantuan", "Colossal"]
    rest = size_type
    for size in sizes:
        if rest.startswith(size + " "):
            rest = rest[len(size) + 1:]
            break
    # Remove subtypes in parentheses
    rest = re.sub(r"\s*\(.*?\)", "", rest).strip()
    return rest if rest else "Unknown"


# ─── Main Parser ────────────────────────────────────────────────────────

def parse_bestiary(docx_path: str):
    """Parse the bestiary docx and return list of mob dicts."""
    doc = docx.Document(docx_path)

    # Step 1: Walk body elements, map tables to headings, extract descriptions
    current_h1 = None
    current_h2 = None  # For Dire Animals sub-headings
    descriptions = {}  # heading -> description text
    heading_order = []  # ordered list of (name, table) tuples

    elements = []
    for elem in doc.element.body:
        tag = elem.tag.split("}")[-1]
        if tag == "p":
            elements.append(("p", Paragraph(elem, doc)))
        elif tag == "tbl":
            elements.append(("tbl", Table(elem, doc)))

    for i, (etype, eobj) in enumerate(elements):
        if etype == "p":
            style = eobj.style.name if eobj.style else ""
            text = eobj.text.strip()
            if style == "Heading 1" and text:
                current_h1 = text
                current_h2 = None
                # Capture next "First Paragraph" as description
                if current_h1 not in descriptions:
                    for j in range(i + 1, min(i + 5, len(elements))):
                        if elements[j][0] == "p":
                            pstyle = elements[j][1].style.name if elements[j][1].style else ""
                            if pstyle == "First Paragraph":
                                descriptions[current_h1] = elements[j][1].text.strip()
                                break
                            elif pstyle == "Heading 1":
                                break
            elif style == "Heading 2" and text:
                current_h2 = text
                # For Dire Animals sub-headings, capture description
                if current_h1 and current_h1.upper() == "DIRE ANIMALS":
                    key = current_h2
                    if key not in descriptions:
                        for j in range(i + 1, min(i + 5, len(elements))):
                            if elements[j][0] == "p":
                                pstyle = elements[j][1].style.name if elements[j][1].style else ""
                                if pstyle == "First Paragraph":
                                    descriptions[key] = elements[j][1].text.strip()
                                    break
                                elif pstyle in ("Heading 1", "Heading 2"):
                                    break

        elif etype == "tbl":
            tbl = eobj
            # Skip non-stat-block tables
            if not tbl.rows:
                continue
            first_cell = tbl.rows[0].cells[0].text.strip()
            if first_cell != "Field":
                continue

            # Determine the name for this table
            if current_h1 and current_h1.upper() == "DIRE ANIMALS" and current_h2:
                name = current_h2
            else:
                name = current_h1

            if name:
                heading_order.append((name, tbl))

    # Step 2: Parse each stat block table
    warnings = []
    mobs = []
    vnum = 10001
    # Track how many tables per heading for name disambiguation
    name_counts = {}
    for name, _ in heading_order:
        name_counts[name] = name_counts.get(name, 0) + 1

    # Second pass: track index per heading
    name_index = {}

    for name, tbl in heading_order:
        # Build field dict from table
        fields = {}
        for row in tbl.rows[1:]:  # skip header row
            field = row.cells[0].text.strip()
            value = row.cells[1].text.strip()
            fields[field] = value

        size_type = fields.get("Size/Type", "")
        size = parse_size_from_type(size_type)
        type_ = parse_type_from_size_type(size_type)

        # Determine mob name
        mob_name = name
        if name_counts.get(name, 1) > 1:
            # Multi-table monster: disambiguate with size
            idx = name_index.get(name, 0)
            name_index[name] = idx + 1
            mob_name = f"{name}, {size}"

        # Title-case the name
        mob_name = mob_name.title()

        # Parse fields
        hp_dice = parse_hp_dice(fields.get("Hit Dice", "1d8"))
        initiative = parse_initiative(fields.get("Initiative", "+0"))
        speed = parse_speed(fields.get("Speed", "30 ft."))
        ac = parse_ac(fields.get("Armor Class", "10"))

        attack_val = fields.get("Attack", "")
        full_attack_val = fields.get("Full Attack", "")
        attacks, damage_dice = parse_attacks(attack_val, full_attack_val)

        special_attacks = parse_comma_list(fields.get("Special Attacks", ""))
        special_qualities = parse_comma_list(fields.get("Special Qualities", ""))
        saves = parse_saves(fields.get("Saves", ""))
        abilities = parse_abilities(fields.get("Abilities", ""))
        skills = parse_skills(fields.get("Skills", ""))
        feats = parse_comma_list(fields.get("Feats", ""))
        cr = parse_cr(fields.get("Challenge Rating", fields.get("CR", "1")))
        alignment = fields.get("Alignment", "Neutral")
        environment = fields.get("Environment", "")
        organization = fields.get("Organization", "")
        advancement = fields.get("Advancement", "")

        # Flags
        flags = []
        elemental_affinity = fields.get("Elemental Affinity", "")
        if elemental_affinity:
            flags.append(f"elemental_affinity:{elemental_affinity}")

        # Description
        desc_key = name
        description = descriptions.get(desc_key, "")
        # Truncate long descriptions for the MUD
        if len(description) > 500:
            description = description[:497] + "..."

        # Level from HD count
        level = hp_dice[0]

        mob = {
            "vnum": vnum,
            "name": mob_name,
            "level": level,
            "hp_dice": hp_dice,
            "ac": ac,
            "damage_dice": damage_dice,
            "flags": flags,
            "room_vnum": None,
            "type_": type_,
            "alignment": alignment,
            "ability_scores": abilities,
            "initiative": initiative,
            "speed": speed,
            "attacks": attacks,
            "special_attacks": special_attacks,
            "special_qualities": special_qualities,
            "feats": feats,
            "skills": skills,
            "saves": saves,
            "environment": environment,
            "organization": organization,
            "cr": cr,
            "advancement": advancement,
            "description": description,
        }
        mobs.append(mob)
        vnum += 1

        # Warn on edge cases
        if not attacks:
            warnings.append(f"  WARNING: No attacks parsed for {mob_name} (vnum {mob['vnum']})")
        if not description:
            warnings.append(f"  WARNING: No description for {mob_name} (vnum {mob['vnum']})")

    return mobs, warnings


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)  # oreka_mud/
    docx_path = os.path.join(project_dir, "Oreka_All_Monster_Entries.docx")
    output_path = os.path.join(project_dir, "data", "mobs_bestiary.json")

    if not os.path.exists(docx_path):
        print(f"ERROR: {docx_path} not found")
        sys.exit(1)

    print(f"Parsing {docx_path}...")
    mobs, warnings = parse_bestiary(docx_path)

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mobs, f, indent=2, ensure_ascii=False)

    print(f"\nParsed {len(mobs)} mobs -> {output_path}")
    if warnings:
        print(f"\n{len(warnings)} warnings:")
        for w in warnings:
            print(w)
    else:
        print("No warnings.")

    # Summary stats
    types = {}
    for mob in mobs:
        t = mob["type_"]
        types[t] = types.get(t, 0) + 1
    print(f"\nTypes: {dict(sorted(types.items(), key=lambda x: -x[1]))}")
    cr_values = [mob["cr"] for mob in mobs if isinstance(mob["cr"], (int, float))]
    if cr_values:
        print(f"CR range: {min(cr_values)} - {max(cr_values)}")


if __name__ == "__main__":
    main()
