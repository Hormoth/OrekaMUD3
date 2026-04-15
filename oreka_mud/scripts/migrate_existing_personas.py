"""Migrate the 4 pre-existing ai_persona blocks to match the new schema:
- speech_style: free-form -> nearest vocab term
- secrets: missing threshold -> add 'casual:' prefix as default tier
- faction_attitudes: {} dict -> [] list
- baseline: 'allied' (not in vocab) -> 'loyal'
"""
import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)


# Map free-form descriptions to vocab terms based on substring match
SPEECH_STYLE_MAP = [
    ("warm", "casual"),         # warm/patient/encouraging -> casual
    ("scholar", "scholarly"),
    ("crackle", "boisterous"),
    ("clipped", "clipped"),
    ("low, even", "reverent"),
    ("slow", "reverent"),
    ("cryptic", "cryptic"),
    ("formal", "formal"),
    ("soldier", "soldierly"),
    ("flirt", "flirtatious"),
    ("archaic", "archaic"),
    ("silent", "silentborn"),
    ("traveler", "casual"),     # uses 'traveler' as address -> casual
    ("simple", "casual"),
    ("short sentences", "clipped"),
]


def normalize_speech_style(raw):
    if not isinstance(raw, str):
        return "casual"
    raw_lower = raw.lower()
    # If already exactly a vocab term, keep
    from src.ai_schemas.ai_persona import SPEECH_STYLES
    if raw in SPEECH_STYLES:
        return raw
    # Substring match
    for needle, vocab in SPEECH_STYLE_MAP:
        if needle in raw_lower:
            return vocab
    return "casual"  # safe default


def normalize_secret(raw):
    """Add 'casual:' prefix if no threshold present."""
    if not isinstance(raw, str):
        return None
    if ":" in raw:
        threshold = raw.split(":", 1)[0].strip()
        if threshold in ("casual", "warm", "trusted", "allied"):
            return raw  # already has valid prefix
    return f"casual:{raw}"


def normalize_faction_attitudes(raw):
    """Convert {} dict to [] list. If dict has entries, convert to list."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        # Convert dict entries to list of FactionAttitude dicts
        result = []
        for fid, val in raw.items():
            if isinstance(val, str):
                # Map common values to baseline vocab
                baseline = val.lower() if val.lower() in ("loyal", "friendly", "neutral", "wary", "hostile") else "neutral"
                result.append({"faction_id": fid, "baseline": baseline, "notes": ""})
            elif isinstance(val, dict):
                baseline = val.get("baseline", "neutral")
                if baseline == "allied":
                    baseline = "loyal"
                result.append({
                    "faction_id": fid,
                    "baseline": baseline if baseline in ("loyal", "friendly", "neutral", "wary", "hostile") else "neutral",
                    "notes": val.get("notes", ""),
                })
        return result
    return []


def normalize_baseline(baseline):
    """Map 'allied' -> 'loyal' (since 'allied' is a trust tier not a baseline)."""
    if baseline == "allied":
        return "loyal"
    valid = {"loyal", "friendly", "neutral", "wary", "hostile"}
    return baseline if baseline in valid else "neutral"


def migrate_persona(persona):
    """Mutate a persona dict to be schema-compliant."""
    # speech_style
    if "speech_style" in persona:
        persona["speech_style"] = normalize_speech_style(persona["speech_style"])

    # secrets
    if "secrets" in persona:
        new_secrets = []
        for s in persona["secrets"]:
            ns = normalize_secret(s)
            if ns:
                new_secrets.append(ns)
        persona["secrets"] = new_secrets

    # faction_attitudes
    if "faction_attitudes" in persona:
        attitudes = normalize_faction_attitudes(persona["faction_attitudes"])
        # Also normalize baselines if list of dicts
        for fa in attitudes:
            if isinstance(fa, dict):
                fa["baseline"] = normalize_baseline(fa.get("baseline", "neutral"))
        persona["faction_attitudes"] = attitudes

    return persona


def main():
    mobs_path = os.path.join(parent_dir, "data", "mobs.json")
    with open(mobs_path, "r", encoding="utf-8") as f:
        mobs = json.load(f)

    migrated = 0
    for m in mobs:
        persona = m.get("ai_persona")
        if persona:
            migrate_persona(persona)
            migrated += 1

    with open(mobs_path, "w", encoding="utf-8") as f:
        json.dump(mobs, f, indent=2, ensure_ascii=False)

    print(f"Migrated {migrated} personas.")

    # Validate
    from src.ai_schemas import validate_persona
    total_errors = 0
    for m in mobs:
        persona = m.get("ai_persona")
        if persona:
            errors = validate_persona(persona)
            if errors:
                print(f"  [X] vnum {m.get('vnum')} ({m.get('name')}):")
                for e in errors:
                    print(f"       {e}")
                total_errors += len(errors)
            else:
                print(f"  [OK] vnum {m.get('vnum')} ({m.get('name')})")

    print(f"\nTotal validation errors: {total_errors}")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
