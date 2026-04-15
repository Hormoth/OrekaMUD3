"""
Kin-Sense System for OrekaMUD3

The most important metaphysical concept in Oreka. A supernatural sixth sense
shared by all Kin that identifies "who belongs." Operates within 60ft (one room),
passes through barriers up to 5ft thick, and cannot be suppressed except by
the Deceiver's Feat, False Silence, or worked Domnathar metal.

NOT magic. Cannot be dispelled or suppressed by anti-magic.

Resonance Categories:
  harmonic     - Warm presence; race and element readable (all Kin)
  wild_static  - Present, alive, fundamentally different (Tanuki, Oreka-native beasts)
  warm_static  - Faint background noise (simple animals, insects, plants)
  breach_static - Alien, unsettling wrong note (Goblins, Wargs, Hobgoblins, Orcs, Ogres)
  null         - A wound; absence that hurts (Silentborn, Severed, Oath-Broken)
  void         - Deliberate predatory wrongness (Domnathar, true Deceivers)
  none         - Simply absent, like furniture (Undead, Constructs, Farborn, Deceiver's Feat)
  raw_static   - Overwhelming, painful at close range (pure elementals)
"""

import random

# Racial Kin-sense bonuses (for detection checks)
RACIAL_KIN_SENSE_BONUS = {
    "Half-Giant": 4,
    "Hasura Elf": 2, "Kovaka Elf": 2, "Pasua Elf": 2, "Na'wasua Elf": 2,
    "Visetri Dwarf": 2, "Pekakarlik Dwarf": 2, "Rarozhki Dwarf": 2,
    "Halfling": 1,
    "Orean Human": 0, "Taraf-Imro Human": 0, "Eruskan Human": 0, "Mytroan Human": 0,
    "Farborn Human": -99,  # Cannot use Kin-sense
    "Half-Domnathar": 0,
    "Silentborn": 0,
}

# Race -> elemental affinity mapping
RACE_ELEMENT = {
    "Half-Giant": "all",
    "Hasura Elf": "wind", "Kovaka Elf": "wind", "Pasua Elf": "wind", "Na'wasua Elf": "wind",
    "Visetri Dwarf": "earth", "Pekakarlik Dwarf": "water", "Rarozhki Dwarf": "fire",
    "Halfling": "water",
    "Orean Human": "earth", "Taraf-Imro Human": "fire", "Eruskan Human": "water", "Mytroan Human": "wind",
    "Farborn Human": None,
    "Half-Domnathar": None,
    "Silentborn": None,
}

# Element -> energy type
ELEMENT_ENERGY = {
    "earth": "acid",
    "fire": "fire",
    "water": "cold",
    "wind": "electricity",
}

# Descriptive text for elements when sensed
ELEMENT_FEEL = {
    "earth": "deep and steady, like river-smoothed stone",
    "fire": "warm and restless, like embers under ash",
    "water": "cool and flowing, like a stream in shade",
    "wind": "bright and sharp, like windchimes in a gust",
    "all": "vast and layered, all four elements in concert",
}

# How resonance categories feel
RESONANCE_FEEL = {
    "harmonic": None,  # Uses race/element-specific text
    "wild_static": "a warm presence, alive but fundamentally different — like a breeze from an unexpected direction",
    "warm_static": "a faint background hum, barely noticeable",
    "breach_static": "an unsettling wrongness — a note that doesn't belong in the harmony",
    "null": "a wound in the resonance — an absence that aches to perceive",
    "void": "deliberate, predatory silence — a gap shaped like a person where something should be",
    "none": None,  # Simply not detected
    "raw_static": "overwhelming elemental force — painful and blinding at this range",
    "echo": "a presence that feels both near and far, like a voice heard through water",
}

# Kin race names for readout
KIN_RACE_NAMES = {
    "Hasura Elf": "elven", "Kovaka Elf": "elven", "Pasua Elf": "elven", "Na'wasua Elf": "elven",
    "Visetri Dwarf": "dwarven", "Pekakarlik Dwarf": "dwarven", "Rarozhki Dwarf": "dwarven",
    "Halfling": "halfling", "Half-Giant": "half-giant",
    "Orean Human": "human", "Taraf-Imro Human": "human", "Eruskan Human": "human", "Mytroan Human": "human",
}


def get_element_for_race(race):
    """Get the elemental affinity for a race."""
    return RACE_ELEMENT.get(race)


def get_racial_bonus(race):
    """Get the Kin-sense racial bonus for detection checks."""
    return RACIAL_KIN_SENSE_BONUS.get(race, 0)


def get_wis_mod(entity):
    """Get Wisdom modifier for an entity."""
    if hasattr(entity, 'wis_score'):
        return (entity.wis_score - 10) // 2
    if hasattr(entity, 'ability_scores'):
        return (entity.ability_scores.get("Wis", 10) - 10) // 2
    return 0


def get_resonance(entity):
    """Get the kin-sense resonance category for an entity.
    Returns (category, element, race_name)."""
    # Players
    if hasattr(entity, 'xp'):
        race = getattr(entity, 'race', '')
        # Check for Deceiver's Feat active
        if getattr(entity, 'deceivers_feat_active', False):
            return ("none", None, None)
        if race == "Farborn Human":
            return ("none", None, None)
        if race == "Silentborn":
            return ("null", None, None)
        if race == "Half-Domnathar":
            element = getattr(entity, 'elemental_affinity', None)
            return ("harmonic", element, "half-domnathar")  # "cracked" harmonic
        element = get_element_for_race(race)
        race_name = KIN_RACE_NAMES.get(race, "unknown")
        return ("harmonic", element, race_name)

    # Mobs — check for kin_sense_category field first
    cat = getattr(entity, 'kin_sense_category', None)
    if cat:
        element = getattr(entity, 'elemental_affinity', None)
        race_name = getattr(entity, 'kin_sense_race', None)
        return (cat, element, race_name)

    # Infer from mob type
    type_ = getattr(entity, 'type_', '').lower()
    flags = [f.lower() for f in getattr(entity, 'flags', [])]

    if 'domnathar' in type_ or 'domnathar' in ' '.join(flags):
        return ("void", None, None)
    if type_ == 'construct' or 'construct' in type_:
        return ("none", None, None)
    if type_ == 'undead' or 'undead' in type_:
        return ("none", None, None)
    if type_ == 'elemental':
        element = getattr(entity, 'elemental_affinity', None)
        return ("raw_static", element, None)
    if type_ == 'humanoid':
        # Check for shopkeeper/named NPCs — treat as Kin
        element = getattr(entity, 'elemental_affinity', None)
        return ("harmonic", element, "kin")
    if type_ in ('animal', 'magical beast', 'vermin'):
        return ("wild_static", None, None)
    if type_ == 'fey':
        return ("wild_static", None, None)
    if type_ in ('plant', 'ooze'):
        return ("warm_static", None, None)
    if any(f in flags for f in ('goblin', 'orc', 'hobgoblin', 'ogre', 'warg')):
        return ("breach_static", None, None)

    # Default: wild static for animals, warm static for everything else
    if type_ == 'animal':
        return ("wild_static", None, None)
    return ("warm_static", None, None)


def _describe_harmonic(entity, element, race_name, viewer, viewer_element, familiar):
    """Generate description for a harmonic (Kin) resonance."""
    if familiar:
        # Recognized individual
        name = getattr(entity, 'name', 'someone')
        if element and element in ELEMENT_FEEL:
            return f"the familiar presence of {name} — {ELEMENT_FEEL[element]}"
        return f"the familiar presence of {name}"

    # Unknown Kin — read race + element
    parts = []
    if race_name:
        if race_name == "half-domnathar":
            parts.append("a discordant, cracked resonance — Kin, but wrong")
        else:
            parts.append(f"a {race_name} presence")
    else:
        parts.append("a Kin presence")

    if element and element in ELEMENT_FEEL:
        parts.append(ELEMENT_FEEL[element])

    return ", ".join(parts)


def _count_by_category(entities, viewer):
    """Group entities by resonance category for summary."""
    counts = {}
    for entity in entities:
        if entity is viewer:
            continue
        cat, element, race_name = get_resonance(entity)
        if cat == "none":
            continue  # Not detected
        key = (cat, element, race_name)
        counts[key] = counts.get(key, 0) + 1
    return counts


def get_kin_sense_readout(character, room):
    """Generate the Kin-sense readout for a character entering a room.

    Returns a string to display, or empty string if nothing notable.
    """
    race = getattr(character, 'race', '')

    # Farborn cannot use Kin-sense
    if race == "Farborn Human":
        return ""

    # Check if Deceiver's Feat is active (bidirectional blindness)
    if getattr(character, 'deceivers_feat_active', False):
        return ""

    viewer_element = get_element_for_race(race)

    # Gather all entities in the room (mobs + other players + shadow presences)
    entities = []
    for mob in getattr(room, 'mobs', []):
        if getattr(mob, 'alive', True) and getattr(mob, 'hp', 1) > 0:
            entities.append(mob)
    for player in getattr(room, 'players', []):
        if player is not character and getattr(player, 'hp', 1) > 0:
            entities.append(player)

    # Shadow presences register as "echo" resonance
    shadows = []
    try:
        from src.shadow_presence import shadow_manager
        shadows = shadow_manager.get_by_room(getattr(room, 'vnum', -1))
    except Exception:
        pass

    if not entities and not shadows:
        return ""

    # Check for room-level suppression (False Silence zone, Domnathar metal)
    room_flags = [f.lower() for f in getattr(room, 'flags', [])]
    if 'false_silence' in room_flags or 'kin_sense_dead' in room_flags:
        return "\033[1;35m[Kin-Sense]\033[0m Nothing. Your soul reaches out and finds only silence."

    # Categorize everyone in the room
    counts = _count_by_category(entities, character)

    if not counts:
        return ""

    # Check for special/dangerous resonances first
    lines = []
    has_void = False
    has_null = False
    has_raw = False
    has_breach = False
    harmonic_count = 0
    harmonic_elements = set()

    for (cat, element, race_name), count in counts.items():
        if cat == "void":
            has_void = True
        elif cat == "null":
            has_null = True
        elif cat == "raw_static":
            has_raw = True
        elif cat == "breach_static":
            has_breach = True
        elif cat == "harmonic":
            harmonic_count += count
            if element:
                harmonic_elements.add(element)

    # Build the readout
    PURPLE = "\033[1;35m"
    RESET = "\033[0m"
    prefix = f"{PURPLE}[Kin-Sense]{RESET} "

    # Void — always detected, no check needed
    if has_void:
        lines.append("A predatory absence — Absolute Silence. Something is here that should not be.")

    # Raw static — painful
    if has_raw:
        lines.append("Overwhelming elemental force pulses nearby — raw and blinding.")

    # Null resonance
    if has_null:
        lines.append("A wound in the harmony — something absent where presence should be.")

    # Breach static
    if has_breach:
        breach_count = sum(c for (cat, _, _), c in counts.items() if cat == "breach_static")
        if breach_count == 1:
            lines.append("An unsettling dissonance — a wrong note in the harmony. Not Kin.")
        else:
            lines.append(f"Unsettling dissonance — {breach_count} alien presences, wrong notes in the harmony.")

    # Harmonic (Kin) — the common case
    if harmonic_count > 0:
        if harmonic_count >= 10:
            # The Hum — crowded Kin area
            if harmonic_elements:
                dominant = max(harmonic_elements, key=lambda e: sum(
                    c for (cat, el, _), c in counts.items() if cat == "harmonic" and el == e
                ))
                if viewer_element and viewer_element == dominant:
                    lines.append(f"The Hum — a warm, familiar resonance. Many Kin, mostly your own element.")
                else:
                    lines.append(f"The Hum — many Kin nearby, predominantly {ELEMENT_FEEL.get(dominant, dominant)}.")
            else:
                lines.append("The Hum — many Kin nearby, their resonance blending into a warm chorus.")
        elif harmonic_count >= 4:
            # Several Kin
            elem_desc = []
            for elem in harmonic_elements:
                elem_count = sum(c for (cat, el, _), c in counts.items() if cat == "harmonic" and el == elem)
                if elem_count > 0:
                    elem_desc.append(f"{ELEMENT_FEEL.get(elem, elem)}")
            if elem_desc:
                lines.append(f"Several Kin presences — " + "; ".join(elem_desc[:3]) + ".")
            else:
                lines.append("Several Kin presences nearby.")
        else:
            # Individual Kin — describe each
            for (cat, element, race_name), count in counts.items():
                if cat != "harmonic":
                    continue
                if count == 1:
                    # Find the specific entity
                    for entity in entities:
                        ecat, eelem, ername = get_resonance(entity)
                        if ecat == "harmonic" and eelem == element and ername == race_name:
                            familiar = _is_familiar(character, entity)
                            desc = _describe_harmonic(entity, element, race_name, character, viewer_element, familiar)
                            lines.append(desc.capitalize() + ".")
                            break
                else:
                    race_desc = race_name if race_name else "Kin"
                    elem_desc = f", {ELEMENT_FEEL.get(element, '')}" if element else ""
                    lines.append(f"{count} {race_desc} presences{elem_desc}.")

    # Wild static (animals, Tanuki, fey)
    wild_count = sum(c for (cat, _, _), c in counts.items() if cat == "wild_static")
    if wild_count > 0:
        if wild_count == 1:
            lines.append("A wild presence — alive but not Kin.")
        else:
            lines.append(f"{wild_count} wild presences — alive but not Kin.")

    # Echo resonance (shadow presences — dreaming players in AI chat)
    if shadows:
        for shadow in shadows:
            # Don't report your own shadow
            if shadow.player_name == getattr(character, 'name', ''):
                continue
            lines.append(
                f"An echo — {RESONANCE_FEEL.get('echo', 'a presence both near and far')}."
            )

    if not lines:
        return ""

    # GMCP: emit structured kin-sense data for the client
    try:
        from src.gmcp import emit_kin_sense as _gmcp_kin
        detections = []
        for (cat, element, race_name), count in counts.items():
            detections.append({
                "resonance": cat,
                "element": element,
                "race": race_name,
                "count": count,
            })
        # Include shadow presences as echo resonance
        for shadow in shadows:
            if shadow.player_name != getattr(character, 'name', ''):
                detections.append({
                    "resonance": "echo",
                    "element": None,
                    "race": None,
                    "count": 1,
                    "name": shadow.player_name,
                    "is_shadow": True,
                })
        room_mod = "suppressed" if ('false_silence' in room_flags or 'kin_sense_dead' in room_flags) else "normal"
        _gmcp_kin(character, detections, room_modifier=room_mod, range_ft=60)
    except Exception:
        pass

    return prefix + " ".join(lines)


def _is_familiar(character, entity):
    """Check if character recognizes this entity's Kin-sense signature.
    Recognized like a voice — those you know personally."""
    # Players always recognize other players they've met
    if hasattr(entity, 'xp'):
        return True
    # Named NPCs the character has interacted with
    # For now: shopkeepers and quest-givers are recognized
    if hasattr(entity, 'is_shopkeeper') and entity.is_shopkeeper():
        return True
    if 'quest' in getattr(entity, 'flags', []):
        return True
    return False


def kin_sense_check(character, target, dc):
    """Make a Kin-sense detection check.
    Used for detecting False Silence, hidden Deceivers, etc.
    Returns (success, roll_total, description)."""
    race = getattr(character, 'race', '')
    racial_bonus = get_racial_bonus(race)
    wis_mod = get_wis_mod(character)

    roll = random.randint(1, 20)
    total = roll + wis_mod + racial_bonus

    success = total >= dc
    desc = f"Kin-Sense check: d20({roll}) + WIS({wis_mod}) + racial({racial_bonus}) = {total} vs DC {dc}"

    return success, total, desc


def passive_kin_sense(character):
    """Calculate passive Kin-sense score (like passive Perception).
    Used for automatic detection with -10 penalty."""
    race = getattr(character, 'race', '')
    racial_bonus = get_racial_bonus(race)
    wis_mod = get_wis_mod(character)
    return 10 + wis_mod + racial_bonus  # d20 average of 10, minus the -10 passive penalty = net 0
