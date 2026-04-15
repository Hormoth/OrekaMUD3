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

    # Inject into shadow presences (world bleed for AI chat)
    try:
        from src.shadow_presence import shadow_manager
        if scope == "room":
            try:
                shadow_manager.broadcast_event(int(target), message)
            except (ValueError, TypeError):
                pass
        elif scope == "global":
            for shadow in shadow_manager.get_all().values():
                shadow.inject_room_event(message)
        elif scope == "region":
            # Regional events reach shadows in that region
            vrange = region_ranges.get(target.lower()) if target else None
            if vrange:
                for shadow in shadow_manager.get_all().values():
                    if vrange[0] <= shadow.room_vnum < vrange[1]:
                        shadow.inject_room_event(message)
    except Exception:
        pass

    # Apply mechanical effects if any
    if mechanical_effects:
        await _apply_event_effects(world, mechanical_effects, scope, target)

    logger.info(f"World event ({scope}/{target}): reached {len(players_reached)} players")
    return players_reached


async def _apply_event_effects(world, effects: dict, scope: str, target: str):
    """Apply mechanical changes from a world event."""
    # Weather change
    if "weather" in effects:
        try:
            from src.weather import get_weather_manager
            wm = get_weather_manager()
            new_weather = effects["weather"]
            if scope == "region" and target:
                region = target.lower().replace(" ", "_")
                wm.region_weather[region] = new_weather
                await wm._notify_weather_change(world, region, "clear", new_weather)
            elif scope == "global":
                for region in wm.region_weather:
                    wm.region_weather[region] = new_weather
                    await wm._notify_weather_change(world, region, "clear", new_weather)
        except Exception:
            pass

    # Mob surge — spawn additional mobs
    if "mob_surge" in effects:
        try:
            from src.spawning import get_spawn_manager
            sm = get_spawn_manager()
            surge = effects["mob_surge"]
            mob_vnum = surge.get("mob_vnum")
            count = surge.get("count", 3)
            target_vnum = surge.get("room_vnum") or (int(target) if scope == "room" else None)
            if mob_vnum and target_vnum:
                room = world.rooms.get(int(target_vnum))
                if room:
                    from src.mob import Mob
                    # Get mob template from spawn manager or world mobs
                    mob_template = None
                    sp = sm.spawn_points.get(mob_vnum)
                    if sp:
                        mob_template = sp.mob_template
                    elif mob_vnum in world.mobs:
                        mob_template = world.mobs[mob_vnum].to_dict()
                    if mob_template:
                        import copy
                        for _ in range(count):
                            data = {k: v for k, v in copy.deepcopy(mob_template).items() if k != 'room_vnum'}
                            mob = Mob(**data)
                            mob.alive = True
                            room.mobs.append(mob)
        except Exception:
            pass

    # Shrine bonus — temporarily boost shrine effects
    if "shrine_bonus" in effects:
        try:
            bonus = effects["shrine_bonus"]
            multiplier = bonus.get("multiplier", 2.0)
            duration = bonus.get("duration", 300)  # seconds
            # Apply as a temporary buff to all players at shrines in scope
            for player in world.players:
                if not hasattr(player, 'room') or not player.room:
                    continue
                room_flags = getattr(player.room, 'flags', []) or []
                if 'shrine' not in room_flags and 'altar' not in room_flags:
                    continue
                if not hasattr(player, 'active_buffs'):
                    player.active_buffs = {}
                player.active_buffs['shrine_bonus'] = {
                    'value': multiplier,
                    'duration': int(duration / 6),  # convert seconds to rounds
                    'spell': 'World Event',
                    'effect': f'Shrine power x{multiplier}',
                }
                if hasattr(player, '_writer'):
                    try:
                        player._writer.write(
                            f"\n\033[1;33m[Shrine]\033[0m The shrine pulses with amplified power!\n"
                        )
                    except Exception:
                        pass
        except Exception:
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
