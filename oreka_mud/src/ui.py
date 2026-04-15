"""
Server-side UI rendering for OrekaMUD3.
Provides ANSI-formatted display helpers for character sheets, combat,
inventory, and other player-facing output.
"""


# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BRED = "\033[1;31m"
BGREEN = "\033[1;32m"
BYELLOW = "\033[1;33m"
BBLUE = "\033[1;34m"
BMAGENTA = "\033[1;35m"
BCYAN = "\033[1;36m"
BWHITE = "\033[1;37m"
DIM = "\033[2m"


def header(text, width=60, color=BYELLOW):
    """Render a centered header bar."""
    pad = max(0, width - len(text) - 4)
    left = pad // 2
    right = pad - left
    return f"{color}{'=' * left}[ {text} ]{'=' * right}{RESET}"


def divider(width=60, char="-", color=DIM):
    """Render a horizontal divider."""
    return f"{color}{char * width}{RESET}"


def bar(current, maximum, width=20, filled_char="=", empty_char="-",
        color_high=BGREEN, color_mid=BYELLOW, color_low=BRED):
    """Render a progress bar like [========------] 40/100."""
    if maximum <= 0:
        maximum = 1
    pct = current / maximum
    filled = int(pct * width)
    empty = width - filled

    if pct > 0.6:
        color = color_high
    elif pct > 0.3:
        color = color_mid
    else:
        color = color_low

    return f"{color}[{filled_char * filled}{empty_char * empty}]{RESET} {current}/{maximum}"


def hp_bar(current, maximum, width=20):
    """Render an HP bar."""
    return f"HP: {bar(current, maximum, width)}"


def move_bar(current, maximum, width=20):
    """Render a movement bar."""
    return f"MV: {bar(current, maximum, width, color_high=BCYAN, color_mid=BBLUE, color_low=BMAGENTA)}"


def xp_bar(current, next_level, width=20):
    """Render an XP progress bar to next level."""
    return f"XP: {bar(current, next_level, width, color_high=BMAGENTA, color_mid=BYELLOW, color_low=DIM)}"


def stat_line(label, value, modifier=None, width=12):
    """Render a stat line like 'STR: 16 (+3)'."""
    if modifier is not None:
        sign = "+" if modifier >= 0 else ""
        return f"  {label:<{width}} {BWHITE}{value:>3}{RESET} ({sign}{modifier})"
    return f"  {label:<{width}} {BWHITE}{value:>3}{RESET}"


def table_row(columns, widths, colors=None):
    """Render a table row with fixed-width columns."""
    parts = []
    for i, (col, w) in enumerate(zip(columns, widths)):
        c = colors[i] if colors and i < len(colors) else ""
        r = RESET if c else ""
        text = str(col)[:w]
        parts.append(f"{c}{text:<{w}}{r}")
    return " ".join(parts)


def format_item_short(item):
    """Short one-line item display."""
    name = getattr(item, 'name', '???')
    item_type = getattr(item, 'item_type', '')
    value = getattr(item, 'value', 0)

    type_color = {
        'weapon': BRED,
        'armor': BBLUE,
        'shield': BCYAN,
        'potion': BGREEN,
        'scroll': BMAGENTA,
        'wand': BYELLOW,
        'food': GREEN,
        'drink': CYAN,
    }.get(item_type, WHITE)

    return f"{type_color}{name}{RESET} ({item_type}) [{value}gp]"


def format_equipment_slot(slot_name, item):
    """Format an equipment slot display."""
    label = slot_name.replace("_", " ").title()
    if item:
        return f"  {CYAN}{label:<15}{RESET} {BWHITE}{item.name}{RESET}"
    return f"  {DIM}{label:<15} <empty>{RESET}"


def format_condition(name, duration=None):
    """Format a condition display."""
    if duration:
        return f"  {BYELLOW}{name.title()}{RESET} ({duration} rounds)"
    return f"  {BYELLOW}{name.title()}{RESET}"


def combat_prompt(character):
    """Generate a combat-ready prompt line."""
    hp_pct = character.hp / max(1, character.max_hp)
    if hp_pct > 0.6:
        hp_color = BGREEN
    elif hp_pct > 0.3:
        hp_color = BYELLOW
    else:
        hp_color = BRED

    target = getattr(character, 'combat_target', None)
    target_str = ""
    if target:
        target_hp_pct = getattr(target, 'hp', 0) / max(1, getattr(target, 'max_hp', 1))
        if target_hp_pct > 0.75:
            condition = "healthy"
        elif target_hp_pct > 0.5:
            condition = "hurt"
        elif target_hp_pct > 0.25:
            condition = "wounded"
        else:
            condition = "critical"
        target_str = f" | {BRED}{target.name}: {condition}{RESET}"

    return f"{hp_color}HP:{character.hp}/{character.max_hp}{RESET} AC:{character.ac}{target_str} > "


def format_score_card(character):
    """Format a full character score card display."""
    lines = []
    lines.append(header(f"{character.name} - {character.race} {character.char_class} {character.level}"))
    lines.append("")
    lines.append(hp_bar(character.hp, character.max_hp))
    lines.append(move_bar(getattr(character, 'move', 100), getattr(character, 'max_move', 100)))
    lines.append("")

    # Stats
    stats = [
        ("STR", character.str_score),
        ("DEX", character.dex_score),
        ("CON", character.con_score),
        ("INT", character.int_score),
        ("WIS", character.wis_score),
        ("CHA", character.cha_score),
    ]
    for label, val in stats:
        mod = (val - 10) // 2
        lines.append(stat_line(label, val, mod))

    lines.append("")
    lines.append(f"  {CYAN}Gold:{RESET} {getattr(character, 'gold', 0)} (Bank: {getattr(character, 'bank_gold', 0)})")
    lines.append(f"  {CYAN}XP:{RESET} {getattr(character, 'xp', 0)}")
    lines.append(f"  {CYAN}AC:{RESET} {character.ac}")

    alignment = getattr(character, 'alignment', None)
    if alignment:
        lines.append(f"  {CYAN}Alignment:{RESET} {alignment}")

    deity = getattr(character, 'deity', None)
    if deity:
        lines.append(f"  {CYAN}Deity:{RESET} {deity}")

    lines.append(divider())
    return "\n".join(lines)


def notification(text, category="info"):
    """Format a system notification."""
    colors = {
        "info": BCYAN,
        "warning": BYELLOW,
        "error": BRED,
        "success": BGREEN,
        "quest": BMAGENTA,
        "combat": BRED,
        "loot": BYELLOW,
        "xp": BGREEN,
    }
    color = colors.get(category, BWHITE)
    tag = category.upper()
    return f"{color}[{tag}]{RESET} {text}"
