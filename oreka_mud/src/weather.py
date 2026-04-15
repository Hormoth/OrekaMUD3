"""
Dynamic Weather Engine for OrekaMUD3.

Manages per-region weather that changes over time based on biome, season,
and weighted transition tables. Integrates with the game_time system and
broadcasts atmospheric messages to outdoor players when weather shifts.
"""

import logging
import random

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Region vnum ranges
# ---------------------------------------------------------------------------

REGION_RANGES = {
    "chapel":              (0, 4000),
    "custos_do_aeternos":  (4000, 5000),
    "kinsweave":           (5000, 6000),
    "tidebloom_reach":     (6000, 7000),
    "eternal_steppe":      (7000, 8000),
    "infinite_desert":     (8000, 9000),
    "deepwater_marches":   (9000, 10000),
    "twin_rivers":         (10000, 11000),
    "gatefall_reach":      (11200, 13000),
    "chainless_legion":    (13000, 13100),
}

# ---------------------------------------------------------------------------
# Weather types
# ---------------------------------------------------------------------------

WEATHER_TYPES = ["clear", "rain", "storm", "heat", "cold", "snow", "fog", "wind"]

# ---------------------------------------------------------------------------
# Weather transition messages
# ---------------------------------------------------------------------------

WEATHER_MESSAGES = {
    "rain":  "Dark clouds gather and rain begins to fall.",
    "storm": "Thunder rumbles as a fierce storm rolls in!",
    "clear": "The skies clear and the sun breaks through.",
    "heat":  "The air grows thick with oppressive heat.",
    "cold":  "A bitter chill settles over the land.",
    "snow":  "Snowflakes begin to drift down from grey skies.",
    "fog":   "A thick fog rolls in, obscuring your surroundings.",
    "wind":  "Strong winds begin to howl across the land.",
}

# ---------------------------------------------------------------------------
# Smooth transition table
# ---------------------------------------------------------------------------
# Each weather type maps to a dict of {target_weather: weight}.
# Transitions that skip intensity (e.g. clear -> storm) are omitted so
# weather changes feel natural.

WEATHER_TRANSITIONS = {
    "clear": {"clear": 40, "rain": 15, "fog": 15, "wind": 15, "heat": 10, "cold": 5},
    "rain":  {"rain": 30, "storm": 20, "clear": 20, "fog": 15, "cold": 10, "wind": 5},
    "storm": {"storm": 25, "rain": 35, "wind": 20, "clear": 10, "fog": 10},
    "heat":  {"heat": 40, "clear": 30, "wind": 15, "fog": 5, "storm": 10},
    "cold":  {"cold": 35, "clear": 20, "snow": 20, "wind": 15, "fog": 10},
    "snow":  {"snow": 35, "cold": 25, "clear": 15, "fog": 15, "wind": 10},
    "fog":   {"fog": 30, "clear": 25, "rain": 20, "wind": 15, "cold": 10},
    "wind":  {"wind": 30, "clear": 30, "rain": 15, "storm": 10, "cold": 10, "fog": 5},
}

# ---------------------------------------------------------------------------
# Biome modifiers per region
# ---------------------------------------------------------------------------
# Multiplier applied to transition weights. A value > 1 makes that weather
# more likely; a value of 0 forbids it entirely.

REGION_BIOME = {
    "chapel": {
        # Temperate urban area -- no extreme modifiers
        "clear": 1.2, "rain": 1.0, "storm": 0.8, "heat": 0.8,
        "cold": 0.8, "snow": 0.6, "fog": 1.0, "wind": 0.8,
    },
    "custos_do_aeternos": {
        # Ancient stronghold, high-altitude sheltered valley
        "clear": 1.0, "rain": 0.9, "storm": 0.7, "heat": 0.6,
        "cold": 1.2, "snow": 1.0, "fog": 1.3, "wind": 1.0,
    },
    "kinsweave": {
        # Highland -- favors cold, fog
        "clear": 0.8, "rain": 1.0, "storm": 0.8, "heat": 0.4,
        "cold": 1.5, "snow": 1.3, "fog": 1.5, "wind": 1.2,
    },
    "tidebloom_reach": {
        # Coastal -- favors rain, fog
        "clear": 0.9, "rain": 1.5, "storm": 1.2, "heat": 0.7,
        "cold": 0.6, "snow": 0.3, "fog": 1.5, "wind": 1.3,
    },
    "eternal_steppe": {
        # Open grassland -- favors wind, clear; cold in winter
        "clear": 1.3, "rain": 0.8, "storm": 0.9, "heat": 1.0,
        "cold": 1.2, "snow": 0.8, "fog": 0.5, "wind": 1.8,
    },
    "infinite_desert": {
        # Desert -- favors heat, clear; never snow
        "clear": 1.5, "rain": 0.3, "storm": 0.4, "heat": 2.0,
        "cold": 0.3, "snow": 0.0, "fog": 0.2, "wind": 1.3,
    },
    "deepwater_marches": {
        # Wetland -- favors rain, fog; rarely cold
        "clear": 0.7, "rain": 1.8, "storm": 1.2, "heat": 0.8,
        "cold": 0.3, "snow": 0.1, "fog": 1.8, "wind": 0.7,
    },
    "twin_rivers": {
        # Riverland -- moderate, slightly wet
        "clear": 1.0, "rain": 1.3, "storm": 1.0, "heat": 0.9,
        "cold": 0.7, "snow": 0.5, "fog": 1.3, "wind": 0.8,
    },
    "gatefall_reach": {
        # Mountainous frontier -- variable, windy
        "clear": 1.0, "rain": 1.0, "storm": 1.2, "heat": 0.5,
        "cold": 1.3, "snow": 1.2, "fog": 1.0, "wind": 1.4,
    },
    "chainless_legion": {
        # Militant encampment, arid badlands
        "clear": 1.3, "rain": 0.6, "storm": 0.8, "heat": 1.5,
        "cold": 0.7, "snow": 0.1, "fog": 0.5, "wind": 1.2,
    },
}

# ---------------------------------------------------------------------------
# Season weights (multipliers applied on top of biome)
# ---------------------------------------------------------------------------
# Seasons are derived from GameTime.month:
#   Winter: months 1-2  (Deepwinter, Icemelt)
#   Spring: months 3-5  (Springseed, Rainmoon, Greengrass)
#   Summer: months 6-8  (Summertide, Highsun, Harvestend)
#   Autumn: months 9-12 (Leaffall, Frostfall, Darknight, Yearsend)

SEASON_WEIGHTS = {
    "winter": {
        "clear": 0.7, "rain": 0.8, "storm": 0.6, "heat": 0.1,
        "cold": 2.0, "snow": 2.0, "fog": 1.2, "wind": 1.3,
    },
    "spring": {
        "clear": 1.0, "rain": 1.5, "storm": 1.2, "heat": 0.6,
        "cold": 0.5, "snow": 0.3, "fog": 1.3, "wind": 1.0,
    },
    "summer": {
        "clear": 1.3, "rain": 0.7, "storm": 1.0, "heat": 1.8,
        "cold": 0.1, "snow": 0.0, "fog": 0.6, "wind": 0.8,
    },
    "autumn": {
        "clear": 0.9, "rain": 1.2, "storm": 1.0, "heat": 0.4,
        "cold": 1.3, "snow": 0.8, "fog": 1.5, "wind": 1.2,
    },
}


def _get_season(month: int) -> str:
    """Return the season name for a given game month (1-12)."""
    if month <= 2:
        return "winter"
    elif month <= 5:
        return "spring"
    elif month <= 8:
        return "summer"
    else:
        return "autumn"


# ---------------------------------------------------------------------------
# WeatherManager
# ---------------------------------------------------------------------------

class WeatherManager:
    """
    Manages dynamic per-region weather, ticking every update cycle.

    Weather is determined by weighted random transitions influenced by the
    region's biome and the current season.
    """

    # How many ticks (each ~30 real seconds) between weather update checks.
    # 10 ticks = ~5 game-minutes of real time (300 seconds).
    TICKS_BETWEEN_UPDATES = 10

    def __init__(self):
        # Current weather per region
        self.region_weather: dict[str, str] = {}
        # Countdown ticks until next weather evaluation per region
        self._transition_timers: dict[str, int] = {}
        # Previous weather for change detection
        self._previous_weather: dict[str, str] = {}

        # Initialize every region to clear skies
        for region in REGION_RANGES:
            self.region_weather[region] = "clear"
            self._transition_timers[region] = self.TICKS_BETWEEN_UPDATES
            self._previous_weather[region] = "clear"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_region(self, vnum: int) -> str | None:
        """Return the region name a vnum belongs to, or None."""
        for region, (vmin, vmax) in REGION_RANGES.items():
            if vmin <= vnum < vmax:
                return region
        return None

    def get_weather(self, vnum: int) -> str:
        """Return the current weather string for the region a vnum is in."""
        region = self.get_region(vnum)
        if region is None:
            return "clear"
        return self.region_weather.get(region, "clear")

    def get_forecast(self, region: str) -> dict:
        """
        Return a dict with current weather and the most likely next weather.

        Keys:
          - current: str
          - likely_next: str
          - ticks_remaining: int  (ticks until next evaluation)
        """
        current = self.region_weather.get(region, "clear")
        # Determine what the most likely transition would be (without season
        # or biome -- just raw transition table) for a simple forecast.
        transitions = WEATHER_TRANSITIONS.get(current, {"clear": 1})
        likely_next = max(transitions, key=transitions.get)
        return {
            "current": current,
            "likely_next": likely_next,
            "ticks_remaining": self._transition_timers.get(region, 0),
        }

    async def update(self, world) -> None:
        """
        Called each tick (~30 seconds). Counts down per-region timers and
        rolls for weather transitions when the timer expires.

        When weather changes, broadcasts a notification to all outdoor
        players in the affected region.
        """
        # Resolve season from game time
        season = "summer"  # fallback
        try:
            from src.schedules import get_game_time
            game_time = get_game_time()
            season = _get_season(game_time.month)
        except Exception:
            pass

        for region in REGION_RANGES:
            self._transition_timers[region] -= 1

            if self._transition_timers[region] > 0:
                continue

            # Reset timer with a little jitter (8-12 ticks)
            self._transition_timers[region] = self.TICKS_BETWEEN_UPDATES + random.randint(-2, 2)

            old_weather = self.region_weather[region]
            new_weather = self._roll_transition(region, old_weather, season)
            self.region_weather[region] = new_weather

            if new_weather != old_weather:
                self._previous_weather[region] = old_weather
                logger.info(
                    "Weather in %s changed: %s -> %s (season=%s)",
                    region, old_weather, new_weather, season,
                )
                await self._notify_weather_change(world, region, old_weather, new_weather)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _roll_transition(self, region: str, current_weather: str, season: str) -> str:
        """
        Pick the next weather state using weighted random selection.

        The final weight for each candidate is:
            base_transition_weight * biome_modifier * season_modifier

        Candidates with a resulting weight <= 0 are excluded.
        """
        base_transitions = WEATHER_TRANSITIONS.get(current_weather, {"clear": 1})
        biome = REGION_BIOME.get(region, {})
        season_mods = SEASON_WEIGHTS.get(season, {})

        candidates: list[str] = []
        weights: list[float] = []

        for weather, base_weight in base_transitions.items():
            biome_mod = biome.get(weather, 1.0)
            season_mod = season_mods.get(weather, 1.0)
            final_weight = base_weight * biome_mod * season_mod

            if final_weight > 0:
                candidates.append(weather)
                weights.append(final_weight)

        if not candidates:
            return "clear"

        return random.choices(candidates, weights=weights, k=1)[0]

    async def _notify_weather_change(self, world, region: str, old_weather: str, new_weather: str) -> None:
        """Broadcast a weather-change message to outdoor players in the region."""
        vmin, vmax = REGION_RANGES[region]
        msg_text = WEATHER_MESSAGES.get(
            new_weather,
            f"The weather changes to {new_weather}.",
        )
        msg = f"\n\033[1;33m[Weather]\033[0m {msg_text}\n"

        for player in world.players:
            if hasattr(player, 'room') and player.room:
                if vmin <= player.room.vnum < vmax:
                    if 'indoor' not in getattr(player.room, 'flags', []):
                        if hasattr(player, '_writer'):
                            try:
                                player._writer.write(msg)
                            except Exception:
                                pass

        # Shadow Chat Game world bleed: notify dreaming players whose
        # bodies are in this region so the NPC can react to the weather.
        try:
            from src.shadow_presence import shadow_manager
            for shadow in shadow_manager.get_all().values():
                player = getattr(shadow, 'character_ref', None)
                if not player:
                    continue
                body_room = getattr(player, 'room', None)
                if not body_room:
                    continue
                if vmin <= body_room.vnum < vmax:
                    shadow.inject_room_event(
                        f"The weather in {region.replace('_', ' ').title()} "
                        f"shifts: {msg_text}"
                    )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_weather_manager: WeatherManager | None = None


def get_weather_manager() -> WeatherManager:
    """Return the global WeatherManager singleton, creating it if needed."""
    global _weather_manager
    if _weather_manager is None:
        _weather_manager = WeatherManager()
    return _weather_manager
