"""
AI Player Bot for OrekaMUD3.
An autonomous player that explores the world, fights mobs, and reports findings.
Runs internally — no telnet connection needed.
"""
import random
import time
import json
from collections import deque


class AIPlayerBot:
    """Autonomous bot that plays the MUD and tracks everything."""

    def __init__(self, world, parser, name="BotExplorer", race="Orean Human", char_class="Fighter"):
        self.world = world
        self.parser = parser
        self.name = name

        # Create the character
        from src.character import Character
        start_room = world.rooms.get(1000, list(world.rooms.values())[0])
        self.character = Character(
            name=name, title="[AI Bot]", race=race, level=5,
            hp=50, max_hp=50, ac=16, room=start_room,
            is_immortal=False, elemental_affinity="earth",
            str_score=16, dex_score=14, con_score=14,
            int_score=12, wis_score=12, cha_score=10,
            move=100, max_move=100, char_class=char_class,
            alignment="True Neutral"
        )
        self.character.is_ai = True
        self.character.gold = 500
        self.character.feats = ["Power Attack", "Improved Initiative", "Toughness"]
        self.character.skills = {"Spot": 4, "Listen": 4, "Search": 4, "Survival": 4}

        # Add to world
        start_room.players.append(self.character)
        world.players.append(self.character)

        # Tracking
        self.rooms_visited = set()
        self.rooms_data = {}  # {vnum: {"name", "exits", "mobs", "flags", "effects"}}
        self.combat_log = []  # [{"mob", "cr", "result", "damage_taken", "room"}]
        self.error_log = []   # [{"command", "error", "room"}]
        self.death_log = []   # [{"mob", "room", "cr"}]
        self.item_log = []    # [{"item", "source", "room"}]
        self.move_count = 0
        self.kill_count = 0
        self.flee_count = 0
        self.start_time = None

        # Exploration state
        self.exploration_queue = deque()
        self.exploration_queue.append(start_room.vnum)
        self.parent_map = {}  # {vnum: (parent_vnum, direction)} for backtracking

    def run_exploration(self, max_rooms=None, max_time=60, fight=True):
        """
        Run BFS exploration of the world.
        max_rooms: stop after visiting this many rooms (None = all)
        max_time: stop after this many seconds
        fight: whether to engage mobs
        Returns: report dict
        """
        self.start_time = time.time()
        max_rooms = max_rooms or len(self.world.rooms)

        while self.exploration_queue and len(self.rooms_visited) < max_rooms:
            # Time check
            if time.time() - self.start_time > max_time:
                break

            target_vnum = self.exploration_queue.popleft()

            if target_vnum in self.rooms_visited:
                continue

            if target_vnum not in self.world.rooms:
                self.error_log.append({"command": "move", "error": f"Room {target_vnum} doesn't exist", "room": self.character.room.vnum})
                continue

            # Navigate to target room
            self._navigate_to(target_vnum)

            # Record room data
            self._record_room()

            # Fight mobs if enabled
            if fight:
                self._fight_room_mobs()

            # Heal if needed
            self._heal_if_needed()

            # Queue adjacent rooms
            room = self.character.room
            for direction, exit_data in room.exits.items():
                # Resolve exit vnum
                if isinstance(exit_data, dict):
                    next_vnum = exit_data.get("vnum", exit_data.get("target"))
                else:
                    next_vnum = exit_data

                if next_vnum and next_vnum not in self.rooms_visited:
                    self.exploration_queue.append(next_vnum)
                    if next_vnum not in self.parent_map:
                        self.parent_map[next_vnum] = (room.vnum, direction)

        return self.generate_report()

    def _navigate_to(self, target_vnum):
        """Move the bot to target room. Uses direct teleport for efficiency."""
        if self.character.room.vnum == target_vnum:
            self.rooms_visited.add(target_vnum)
            return

        # Direct move — remove from old room, add to new
        old_room = self.character.room
        if self.character in old_room.players:
            old_room.players.remove(self.character)

        new_room = self.world.rooms.get(target_vnum)
        if new_room:
            self.character.room = new_room
            new_room.players.append(self.character)
            self.rooms_visited.add(target_vnum)
            self.move_count += 1

    def _record_room(self):
        """Record data about current room."""
        room = self.character.room
        vnum = room.vnum

        mob_data = []
        for mob in room.mobs:
            if hasattr(mob, 'alive') and mob.alive:
                mob_data.append({
                    "name": mob.name,
                    "cr": getattr(mob, 'cr', '?'),
                    "type": getattr(mob, 'type_', '?'),
                    "level": getattr(mob, 'level', '?'),
                    "hp": getattr(mob, 'hp', '?'),
                    "flags": getattr(mob, 'flags', [])
                })

        self.rooms_data[vnum] = {
            "name": room.name,
            "exits": dict(room.exits),
            "exit_count": len(room.exits),
            "flags": getattr(room, 'flags', []),
            "effects": getattr(room, 'effects', []),
            "mobs": mob_data,
            "mob_count": len(mob_data),
            "has_shop": any('shop' in str(f).lower() for f in getattr(room, 'flags', [])),
            "has_safe": 'safe' in getattr(room, 'flags', []),
            "description_length": len(room.description) if room.description else 0,
        }

    def _fight_room_mobs(self):
        """Fight hostile mobs in the room if CR is appropriate."""
        room = self.character.room
        for mob in list(room.mobs):
            if not hasattr(mob, 'alive') or not mob.alive:
                continue

            # Skip friendly mobs
            flags = getattr(mob, 'flags', [])
            if any(f in flags for f in ['no_attack', 'trainer', 'shopkeeper', 'guard']):
                continue

            # Check CR — only fight if CR <= bot level + 2
            import re
            raw_cr = str(getattr(mob, 'cr', 0))
            match = re.match(r'[\d.]+', raw_cr)
            cr = float(match.group()) if match else 0

            if cr > self.character.level + 2:
                continue  # Too dangerous

            # Fight!
            mob_hp_before = mob.hp if hasattr(mob, 'hp') else 0
            bot_hp_before = self.character.hp

            # Simple combat simulation — don't use full combat system to avoid async issues
            rounds = 0
            while hasattr(mob, 'alive') and mob.alive and mob.hp > 0 and self.character.hp > 0:
                # Bot attacks
                attack_roll = random.randint(1, 20) + (self.character.str_score - 10) // 2
                if attack_roll >= getattr(mob, 'ac', 10):
                    damage = random.randint(1, 8) + (self.character.str_score - 10) // 2
                    mob.hp -= damage

                # Mob attacks back (if it has attacks)
                if mob.hp > 0 and getattr(mob, 'attacks', []):
                    mob_attack = random.randint(1, 20) + getattr(mob, 'level', 1)
                    if mob_attack >= self.character.ac:
                        mob_dmg_dice = getattr(mob, 'damage_dice', [1, 6, 0])
                        if isinstance(mob_dmg_dice, list) and len(mob_dmg_dice) >= 3:
                            mob_damage = sum(random.randint(1, mob_dmg_dice[1]) for _ in range(mob_dmg_dice[0])) + mob_dmg_dice[2]
                        else:
                            mob_damage = random.randint(1, 6)
                        self.character.hp -= mob_damage

                rounds += 1
                if rounds > 50:  # Safety valve
                    break

                # Flee if low HP
                if self.character.hp <= self.character.max_hp * 0.3:
                    self.flee_count += 1
                    self.combat_log.append({
                        "mob": mob.name, "cr": cr, "result": "fled",
                        "damage_taken": bot_hp_before - self.character.hp,
                        "room": room.vnum, "rounds": rounds
                    })
                    break

            if mob.hp <= 0:
                mob.alive = False
                self.kill_count += 1
                self.combat_log.append({
                    "mob": mob.name, "cr": cr, "result": "killed",
                    "damage_taken": bot_hp_before - self.character.hp,
                    "room": room.vnum, "rounds": rounds
                })

            if self.character.hp <= 0:
                self.death_log.append({
                    "mob": mob.name, "room": room.vnum, "cr": cr
                })
                # Resurrect bot
                self.character.hp = self.character.max_hp
                break

    def _heal_if_needed(self):
        """Heal bot between fights."""
        if self.character.hp < self.character.max_hp * 0.7:
            self.character.hp = self.character.max_hp

    def generate_report(self):
        """Generate comprehensive exploration report."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        total_rooms = len(self.world.rooms)

        # Region breakdown
        regions = {}
        for vnum, data in self.rooms_data.items():
            if vnum < 4000: region = "Chapel"
            elif vnum < 5000: region = "CustosDoAeternos"
            elif vnum < 6000: region = "Kinsweave"
            elif vnum < 7000: region = "TidebloomReach"
            elif vnum < 8000: region = "EternalSteppe"
            elif vnum < 9000: region = "InfiniteDesert"
            elif vnum < 10000: region = "DeepwaterMarches"
            elif vnum < 11000: region = "TwinRivers"
            elif vnum < 11200: region = "WildernessConnectors"
            elif vnum < 13000: region = "GatefallReach"
            elif vnum < 13100: region = "ChainlessLegion"
            else: region = "DeepwaterExpansion"

            if region not in regions:
                regions[region] = {"visited": 0, "mobs": 0, "shops": 0, "safe": 0, "effects": 0, "empty_desc": 0}
            regions[region]["visited"] += 1
            regions[region]["mobs"] += data["mob_count"]
            if data["has_shop"]: regions[region]["shops"] += 1
            if data["has_safe"]: regions[region]["safe"] += 1
            if data["effects"]: regions[region]["effects"] += 1
            if data["description_length"] == 0: regions[region]["empty_desc"] += 1

        # Dead-end rooms (1 exit only)
        dead_ends = [vnum for vnum, data in self.rooms_data.items() if data["exit_count"] <= 1]

        # Rooms with no description
        empty_rooms = [vnum for vnum, data in self.rooms_data.items() if data["description_length"] == 0]

        # Combat summary
        kills_by_cr = {}
        for combat in self.combat_log:
            cr = combat["cr"]
            result = combat["result"]
            kills_by_cr.setdefault(cr, {"killed": 0, "fled": 0})
            kills_by_cr[cr][result] = kills_by_cr[cr].get(result, 0) + 1

        # Dangerous rooms (where bot died)
        danger_rooms = [(d["room"], d["mob"], d["cr"]) for d in self.death_log]

        report = {
            "summary": {
                "bot_name": self.name,
                "elapsed_seconds": round(elapsed, 1),
                "rooms_visited": len(self.rooms_visited),
                "total_rooms": total_rooms,
                "coverage_pct": round(100 * len(self.rooms_visited) / total_rooms, 1) if total_rooms else 0,
                "moves": self.move_count,
                "kills": self.kill_count,
                "deaths": len(self.death_log),
                "flees": self.flee_count,
                "errors": len(self.error_log),
            },
            "regions": regions,
            "dead_ends": dead_ends[:20],  # First 20
            "dead_end_count": len(dead_ends),
            "empty_rooms": empty_rooms,
            "combat_by_cr": kills_by_cr,
            "deaths": danger_rooms,
            "errors": self.error_log[:20],
        }

        return report

    def format_report(self, report=None):
        """Format report as readable text."""
        if report is None:
            report = self.generate_report()

        s = report["summary"]
        lines = []
        lines.append("=" * 70)
        lines.append(f"  AI BOT EXPLORATION REPORT — {s['bot_name']}")
        lines.append("=" * 70)
        lines.append(f"  Time: {s['elapsed_seconds']}s")
        lines.append(f"  Rooms: {s['rooms_visited']} / {s['total_rooms']} ({s['coverage_pct']}% coverage)")
        lines.append(f"  Moves: {s['moves']}  Kills: {s['kills']}  Deaths: {s['deaths']}  Flees: {s['flees']}")
        lines.append(f"  Errors: {s['errors']}")
        lines.append("")

        lines.append("  REGION BREAKDOWN:")
        lines.append(f"  {'Region':<25} {'Visited':>7} {'Mobs':>5} {'Shops':>5} {'Safe':>5} {'Effects':>7}")
        lines.append("  " + "-" * 60)
        for region, data in sorted(report["regions"].items()):
            lines.append(f"  {region:<25} {data['visited']:>7} {data['mobs']:>5} {data['shops']:>5} {data['safe']:>5} {data['effects']:>7}")

        if report.get("combat_by_cr"):
            lines.append("")
            lines.append("  COMBAT BY CR:")
            for cr in sorted(report["combat_by_cr"].keys()):
                data = report["combat_by_cr"][cr]
                lines.append(f"    CR {cr}: {data.get('killed',0)} killed, {data.get('fled',0)} fled")

        if report.get("deaths"):
            lines.append("")
            lines.append("  DEATHS:")
            for room, mob, cr in report["deaths"]:
                rname = self.rooms_data.get(room, {}).get("name", "?")
                lines.append(f"    Room {room} ({rname}) — killed by {mob} (CR {cr})")

        if report.get("dead_end_count", 0) > 0:
            lines.append("")
            lines.append(f"  DEAD ENDS ({report['dead_end_count']} rooms with 1 or fewer exits):")
            for vnum in report["dead_ends"][:10]:
                rname = self.rooms_data.get(vnum, {}).get("name", "?")
                lines.append(f"    {vnum} — {rname}")
            if report["dead_end_count"] > 10:
                lines.append(f"    ... and {report['dead_end_count'] - 10} more")

        if report.get("empty_rooms"):
            lines.append("")
            lines.append(f"  ROOMS WITH NO DESCRIPTION ({len(report['empty_rooms'])}):")
            for vnum in report["empty_rooms"][:10]:
                lines.append(f"    {vnum}")

        if report.get("errors"):
            lines.append("")
            lines.append(f"  ERRORS ({len(report['errors'])}):")
            for err in report["errors"][:10]:
                lines.append(f"    [{err.get('room','?')}] {err.get('command','?')}: {err.get('error','?')}")

        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)

    def cleanup(self):
        """Remove bot from world."""
        if self.character in self.character.room.players:
            self.character.room.players.remove(self.character)
        if self.character in self.world.players:
            self.world.players.remove(self.character)


def run_bot_exploration(world, parser, max_rooms=None, max_time=60, fight=True):
    """Convenience function to run a bot and get the report."""
    bot = AIPlayerBot(world, parser)
    report = bot.run_exploration(max_rooms=max_rooms, max_time=max_time, fight=fight)
    text = bot.format_report(report)
    bot.cleanup()
    return text, report
