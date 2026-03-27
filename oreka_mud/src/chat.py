"""
Chat and Message Broadcasting System for OrekaMUD3

Provides functions to broadcast messages to:
- All players in a room (say, emote)
- All players in the world (global, OOC)
- Specific players (tell, whisper)
- Guild members (guild chat)
"""

# ANSI color codes for chat channels
COLORS = {
    'say': '\033[37m',       # White
    'tell': '\033[35m',      # Magenta
    'whisper': '\033[35m',   # Magenta
    'ooc': '\033[36m',       # Cyan
    'global': '\033[33m',    # Yellow
    'guild': '\033[32m',     # Green
    'emote': '\033[33m',     # Yellow
    'shout': '\033[1;33m',   # Bold Yellow
    'admin': '\033[1;31m',   # Bold Red
    'reset': '\033[0m',      # Reset
}


def get_player_writer(player):
    """Get the writer object for a player if they have one."""
    return getattr(player, 'writer', None)


def send_to_player(player, message):
    """Send a message to a specific player."""
    writer = get_player_writer(player)
    if writer:
        try:
            # Include their prompt after the message
            prompt = player.get_prompt() if hasattr(player, 'get_prompt') else '> '
            writer.write(f"\n{message}\n{prompt} {COLORS['reset']}")
        except Exception:
            pass  # Player may have disconnected


def broadcast_to_room(room, message, exclude=None, include_prompt=True):
    """
    Broadcast a message to all players in a room.

    Args:
        room: The room object
        message: The message to send
        exclude: Player to exclude (usually the sender)
        include_prompt: Whether to include the player's prompt after message
    """
    if not room or not hasattr(room, 'players'):
        return

    for player in room.players:
        if exclude and player == exclude:
            continue
        send_to_player(player, message)


def broadcast_to_world(world, message, exclude=None):
    """
    Broadcast a message to all players in the world.

    Args:
        world: The world object containing all players
        message: The message to send
        exclude: Player to exclude (usually the sender)
    """
    if not world or not hasattr(world, 'players'):
        return

    for player in world.players:
        if exclude and player == exclude:
            continue
        # Skip AI players
        if getattr(player, 'is_ai', False):
            continue
        send_to_player(player, message)


def broadcast_to_area(room, message, exclude=None, radius=3):
    """
    Broadcast a message to players in nearby rooms (for shout).
    This is a simplified version - just broadcasts to current room.
    A full implementation would traverse exits up to 'radius' rooms away.
    """
    # For now, just broadcast to current room
    # TODO: Implement multi-room radius broadcasting
    broadcast_to_room(room, message, exclude)


def send_tell(sender, recipient, message):
    """
    Send a private message from one player to another.

    Args:
        sender: The player sending the message
        recipient: The player receiving the message
        message: The message content

    Returns:
        Tuple of (success, response_message)
    """
    if not recipient:
        return False, "Player not found."

    if recipient == sender:
        return False, "Talking to yourself?"

    # Check if recipient is AI
    if getattr(recipient, 'is_ai', False):
        return False, f"{recipient.name} cannot receive tells."

    # Check if recipient has the sender on ignore (System 39)
    ignored = getattr(recipient, 'ignored_players', [])
    if sender.name.lower() in [n.lower() for n in ignored]:
        # Silently succeed from sender's perspective; recipient doesn't see it
        return True, f"{COLORS['tell']}[Tell] You -> {recipient.name}: {message}{COLORS['reset']}"

    writer = get_player_writer(recipient)
    if not writer:
        return False, f"{recipient.name} is not connected."

    # Format and send the message
    formatted = f"{COLORS['tell']}[Tell] {sender.name} -> you: {message}{COLORS['reset']}"
    send_to_player(recipient, formatted)

    # Store last tell sender for 'reply' command
    recipient.last_tell_from = sender.name

    # System 40: AFK auto-reply
    if getattr(recipient, 'afk', False):
        afk_msg = getattr(recipient, 'afk_message', '')
        reply_text = f"{recipient.name} is AFK."
        if afk_msg:
            reply_text += f" ({afk_msg})"
        afk_formatted = f"{COLORS['tell']}[Tell] {recipient.name} is AFK: {afk_msg or 'Away from keyboard.'}{COLORS['reset']}"
        send_to_player(sender, afk_formatted)

    return True, f"{COLORS['tell']}[Tell] You -> {recipient.name}: {message}{COLORS['reset']}"


def format_say(speaker, message):
    """Format a say message for display."""
    return f"{COLORS['say']}{speaker.name} says, '{message}'{COLORS['reset']}"


def format_emote(actor, action):
    """Format an emote message for display."""
    # Handle actions that start with 's or similar
    if action.startswith("'"):
        return f"{COLORS['emote']}{actor.name}{action}{COLORS['reset']}"
    return f"{COLORS['emote']}{actor.name} {action}{COLORS['reset']}"


def format_ooc(speaker, message):
    """Format an OOC message for display."""
    return f"{COLORS['ooc']}[OOC] {speaker.name}: {message}{COLORS['reset']}"


def format_global(speaker, message):
    """Format a global chat message for display."""
    return f"{COLORS['global']}[Global] {speaker.name}: {message}{COLORS['reset']}"


def format_shout(speaker, message):
    """Format a shout message for display."""
    return f"{COLORS['shout']}{speaker.name} shouts, '{message}'{COLORS['reset']}"


def format_guild(speaker, guild_name, message):
    """Format a guild chat message for display."""
    return f"{COLORS['guild']}[{guild_name}] {speaker.name}: {message}{COLORS['reset']}"


def format_admin(speaker, message):
    """Format an admin broadcast message."""
    return f"{COLORS['admin']}[ADMIN] {speaker.name}: {message}{COLORS['reset']}"


def format_newbie(speaker, message):
    """Format a newbie channel message."""
    return f"\033[1;32m[Newbie] {speaker.name}: {message}{COLORS['reset']}"


# Helper to find a player by name
def find_player_by_name(world, name):
    """
    Find a player in the world by name (case-insensitive).

    Args:
        world: The world object
        name: Player name to search for

    Returns:
        Player object or None
    """
    if not world or not hasattr(world, 'players'):
        return None

    name_lower = name.lower()
    for player in world.players:
        if player.name.lower() == name_lower:
            return player
    return None


def find_player_by_name_prefix(world, prefix):
    """
    Find a player by name prefix (for partial matching).

    Args:
        world: The world object
        prefix: Beginning of player name

    Returns:
        Player object or None (returns first match)
    """
    if not world or not hasattr(world, 'players'):
        return None

    prefix_lower = prefix.lower()
    for player in world.players:
        if player.name.lower().startswith(prefix_lower):
            return player
    return None
