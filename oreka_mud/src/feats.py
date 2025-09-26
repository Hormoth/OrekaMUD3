# feats.py
"""
D&D 3.5 OGL Feats system for OrekaMUD
This module defines all feats, their descriptions, prerequisites, and effect stubs.
"""


class Feat:
    def __init__(self, name, description, prerequisites=None, effect=None):
        self.name = name
        self.description = description
        self.prerequisites = prerequisites or []  # List of prerequisite dicts
        self.effect = effect  # Callable or None

    def apply(self, user, *args, **kwargs):
        if self.effect:
            return self.effect(user, *args, **kwargs)
        return None

def meets_prereq(character, prereq):
    """
    Check if a character meets a single prerequisite dict.
    Supported keys: 'level', 'bab', 'ability', 'feat', 'class_feature', 'skill', 'race', 'class'.
    """
    if 'level' in prereq:
        if getattr(character, 'level', 1) < prereq['level']:
            return False
    if 'bab' in prereq:
        # Assume BAB = level for fighters, 3/4 for most, 1/2 for wizards
        bab = getattr(character, 'bab', None)
        if bab is None:
            cl = getattr(character, 'char_class', '').lower()
            lvl = getattr(character, 'level', 1)
            if cl in ('fighter', 'barbarian', 'paladin', 'ranger'): bab = lvl
            elif cl in ('wizard', 'sorcerer'): bab = lvl // 2
            else: bab = (lvl * 3) // 4
        if bab < prereq['bab']:
            return False
    if 'ability' in prereq:
        # e.g. {'ability': ('Dex', 13)}
        ab, val = prereq['ability']
        if getattr(character, f'{ab.lower()}_score', 10) < val:
            return False
    if 'feat' in prereq:
        if prereq['feat'] not in getattr(character, 'feats', []):
            return False
    if 'class_feature' in prereq:
        if prereq['class_feature'] not in getattr(character, 'class_features', []):
            return False
    if 'skill' in prereq:
        # e.g. {'skill': ('Tumble', 5)}
        sk, val = prereq['skill']
        if getattr(character, 'skills', {}).get(sk, 0) < val:
            return False
    if 'race' in prereq:
        if getattr(character, 'race', '').lower() != prereq['race'].lower():
            return False
    if 'class' in prereq:
        if getattr(character, 'char_class', '').lower() != prereq['class'].lower():
            return False
    return True

def is_eligible_for_feat(character, feat):
    """Return True if character meets all prerequisites for the feat (by name or Feat object)."""
    from src.feats import FEATS
    if isinstance(feat, str):
        feat = FEATS.get(feat)
    if not feat:
        return False
    for prereq in feat.prerequisites:
        if not meets_prereq(character, prereq):
            return False
    return True

def list_eligible_feats(character, only_bonus=False):
    """Return a list of feat names the character is eligible to select (optionally only bonus feats)."""
    from src.feats import FEATS
    eligible = []
    for fname, feat in FEATS.items():
        if only_bonus and not getattr(feat, 'is_bonus', False):
            continue
        if fname in getattr(character, 'feats', []):
            continue  # Already has
        if is_eligible_for_feat(character, feat):
            eligible.append(fname)
    return eligible



# --- D&D 3.5 Feats with Prerequisites (sample, expand as needed) ---
FEATS = {
    "Power Attack": Feat(
        "Power Attack",
        "Trade attack bonus for damage (up to BAB).",
        prerequisites=[{'ability': ('Str', 13)}],
        effect=None
    ),
    "Cleave": Feat(
        "Cleave",
        "Extra melee attack if mob drops a foe.",
        prerequisites=[{'feat': 'Power Attack'}],
        effect=None
    ),
    "Great Cleave": Feat(
        "Great Cleave",
        "No limit on number of Cleave attacks per round.",
        prerequisites=[{'feat': 'Cleave'}, {'bab': 4}],
        effect=None
    ),
    "Dodge": Feat(
        "Dodge",
        "+1 dodge bonus to AC against one opponent.",
        prerequisites=[{'ability': ('Dex', 13)}],
        effect=None
    ),
    "Mobility": Feat(
        "Mobility",
        "+4 AC against attacks of opportunity caused by movement.",
        prerequisites=[{'feat': 'Dodge'}],
        effect=None
    ),
    "Spring Attack": Feat(
        "Spring Attack",
        "Move-attack-move, no AoO from target.",
        prerequisites=[{'feat': 'Dodge'}, {'feat': 'Mobility'}, {'bab': 4}],
        effect=None
    ),
    "Weapon Finesse": Feat(
        "Weapon Finesse",
        "Use Dex instead of Str for attack rolls with light weapons.",
        prerequisites=[{'bab': 1}],
        effect=None
    ),
    "Toughness": Feat(
        "Toughness",
        "+3 hit points.",
        prerequisites=[],
        effect=lambda user, value=0: value + 3
    ),
    "Improved Initiative": Feat(
        "Improved Initiative",
        "+4 bonus on initiative checks.",
        prerequisites=[],
        effect=lambda user, value=0: value + 4
    ),
    "Alertness": Feat(
        "Alertness",
        "+2 bonus on Listen and Spot checks.",
        prerequisites=[],
        effect=lambda user, skill=None, value=0: value + 2 if skill in ("Listen", "Spot") else value
    ),
    # ...add all other feats with prerequisites here...
}

def get_feat(name):
    return FEATS.get(name)
