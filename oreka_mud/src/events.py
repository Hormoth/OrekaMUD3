"""
World Events System for OrekaMUD3.
Broadcasts narrative events to players. Called by DM Agent via MCP Bridge.
"""
import logging

logger = logging.getLogger("OrekaMUD.Events")


async def broadcast_event(world, scope: str, target: str, message: str,
                          mechanical_effects: dict = None):
    """
    Broadcast a world event to players.

    scope: "room" | "region" | "global"
    target: room vnum (str/int), region name, or "all"
    message: narrative text sent to players
    mechanical_effects: optional dict of game mechanics to apply

    Returns list of player names reached.
    """
    players_reached = []

    formatted_msg = f"\n\033[1;33m[World Event]\033[0m {message}\n"

    if scope == "room":
        try:
            vnum = int(target)
            room = world.rooms.get(vnum)
            if room:
                for player in room.players:
                    if hasattr(player, '_writer'):
                        try:
                            player._writer.write(formatted_msg)
                        except Exception:
                            pass
                    players_reached.append(getattr(player, 'name', '?'))
        except (ValueError, TypeError):
            pass

    elif scope == "region":
        # Map region names to vnum ranges
        region_ranges = {
            "chapel": (0, 4000),
            "custos_do_aeternos": (4000, 5000),
            "kinsweave": (5000, 6000),
            "tidebloom_reach": (6000, 7000),
            "eternal_steppe": (7000, 8000),
            "infinite_desert": (8000, 9000),
            "deepwater_marches": (9000, 10000),
            "twin_rivers": (10000, 11000),
            "gatefall_reach": (11200, 13000),
            "chainless_legion": (13000, 13100),
        }
        vrange = region_ranges.get(target.lower())
        if vrange:
            for player in world.players:
                if hasattr(player, 'room') and player.room:
                    if vrange[0] <= player.room.vnum < vrange[1]:
                        if hasattr(player, '_writer'):
                            try:
                                player._writer.write(formatted_msg)
                            except Exception:
                                pass
                        players_reached.append(getattr(player, 'name', '?'))

    elif scope == "global":
        for player in world.players:
            if hasattr(player, '_writer'):
                try:
                    player._writer.write(formatted_msg)
                except Exception:
                    pass
            players_reached.append(getattr(player, 'name', '?'))

    # Apply mechanical effects if any
    if mechanical_effects:
        await _apply_event_effects(world, mechanical_effects, scope, target)

    logger.info(f"World event ({scope}/{target}): reached {len(players_reached)} players")
    return players_reached


async def _apply_event_effects(world, effects: dict, scope: str, target: str):
    """Apply mechanical changes from a world event."""
    # Weather change
    if "weather" in effects:
        # Future: apply weather to rooms in scope
        pass

    # Mob surge — spawn additional mobs
    if "mob_surge" in effects:
        # Future: spawn temporary mobs in target area
        pass

    # Shrine bonus — temporarily boost shrine effects
    if "shrine_bonus" in effects:
        # Future: modify sanctuary effects temporarily
        pass

    # Faction rep change for all players in area
    if "faction_rep" in effects:
        faction = effects["faction_rep"].get("faction")
        amount = effects["faction_rep"].get("amount", 0)
        if faction:
            try:
                from src.factions import get_faction_manager
                fm = get_faction_manager()
                for player in world.players:
                    if hasattr(player, 'room') and player.room:
                        fm.modify_reputation(player, faction, amount, "World event")
            except Exception:
                pass
