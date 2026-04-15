"""
Narrative / Story Progression System for OrekaMUD3.

Manages the main story arc of Oreka, from a character's awakening through
the escalating Silence Breach crisis.  Each chapter has trigger conditions
(level, faction reputation, room entry, mob kill) and rewards (XP, titles).

Characters store completed chapter IDs in ``narrative_progress`` (a list).

Usage
-----
::

    from src.narrative import get_narrative_manager

    nm = get_narrative_manager()
    triggered = nm.on_level_up(character)
    for chapter, text in triggered:
        writer.write(text)
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("OrekaMUD.Narrative")

# ---------------------------------------------------------------------------
# Lore helpers
# ---------------------------------------------------------------------------

_lore_cache: Optional[Dict[str, str]] = None


def _load_lore() -> Dict[str, str]:
    """Load the lore.json reference data (cached after first call)."""
    global _lore_cache
    if _lore_cache is not None:
        return _lore_cache
    path = os.path.join("data", "lore.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            _lore_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.warning("Could not load lore.json: %s", exc)
        _lore_cache = {}
    return _lore_cache


# ---------------------------------------------------------------------------
# Region vnum ranges (mirrors events.py)
# ---------------------------------------------------------------------------

REGION_VNUM_RANGES: Dict[str, Tuple[int, int]] = {
    "chapel": (0, 4000),
    "custos_do_aeternos": (4000, 5000),
    "kinsweave": (5000, 6000),
    "tidebloom_reach": (6000, 7000),
    "eternal_steppe": (7000, 8000),
    "infinite_desert": (8000, 9000),
    "deepwater_marches": (9000, 10000),
    "twin_rivers": (10000, 11000),
    "shadeharmon_glade": (11000, 11200),
    "gatefall_reach": (11200, 13000),
    "chainless_legion": (13000, 13100),
}


def _room_region(room) -> Optional[str]:
    """Return the region key for *room*, or ``None``."""
    vnum = room.vnum if hasattr(room, "vnum") else None
    if vnum is None:
        return None
    for region, (lo, hi) in REGION_VNUM_RANGES.items():
        if lo <= vnum < hi:
            return region
    return None


# ---------------------------------------------------------------------------
# Story chapters
# ---------------------------------------------------------------------------

STORY_CHAPTERS: List[Dict[str, Any]] = [
    {
        "id": "awakening",
        "title": "The Awakening",
        "description": "You arrive in Oreka, sensing the elemental currents for the first time.",
        "trigger": {"type": "level", "value": 1},
        "narrative": (
            "The world hums with elemental resonance.  You feel the Kin-sense "
            "awaken within you -- a warmth at the edge of perception, telling "
            "you that you are not alone.  Stone beneath your feet pulses with "
            "the heartbeat of the Lord of Stone's ancient dream.  Wind carries "
            "whispers of a world far older than memory.  Your journey begins."
        ),
        "rewards": {"xp": 100},
    },
    {
        "id": "the_breach",
        "title": "Whispers of the Breach",
        "description": "Reports of a growing silence in the east reach your ears.",
        "trigger": {"type": "level", "value": 5},
        "narrative": (
            "Travelers speak of a spreading void in Gatefall Reach where "
            "Kin-sense falters and fades to nothing.  The frontier wardens "
            "call it the Silence Breach -- an absence that hurts, like a wound "
            "in the world itself.  Something is consuming the elemental "
            "resonance that binds all Kin together, and no one knows why."
        ),
        "rewards": {"xp": 500},
    },
    {
        "id": "faction_ties",
        "title": "Choosing Allegiances",
        "description": "The factions of Oreka seek your loyalty.",
        "trigger": {"type": "faction_rep", "faction": "any", "value": 100},
        "narrative": (
            "Your reputation precedes you.  Messengers arrive bearing sigils "
            "of the great factions -- the Trade Houses, the Sand Wardens, the "
            "Gatefall Remnant, and others.  Each offers purpose; each demands "
            "allegiance.  In Oreka, no one walks alone for long.  The question "
            "is not whether you will choose, but whom."
        ),
        "rewards": {"xp": 300},
    },
    {
        "id": "elemental_trials",
        "title": "The Elemental Trials",
        "description": "The Elemental Lords test those who would serve.",
        "trigger": {"type": "level", "value": 10},
        "narrative": (
            "The ground trembles, the wind whispers, the waters churn, and "
            "distant fires flare without fuel.  The Elemental Lords have taken "
            "notice of you.  In dreams you see the Lord of Stone, vast and "
            "silent, sleeping beneath the mountains.  The Lady of Fire stares "
            "through forge-flame.  The Lady of the Sea watches from the deep.  "
            "And somewhere beyond the horizon, the exiled Wind Lord stirs.  "
            "They are testing you."
        ),
        "rewards": {"xp": 1000, "title": "Elemental Aspirant"},
    },
    {
        "id": "silence_deepens",
        "title": "The Silence Deepens",
        "description": "The Breach grows.  Kin-sense fails near its borders.",
        "trigger": {"type": "level", "value": 15},
        "narrative": (
            "Where once elemental currents flowed, there is only emptiness.  "
            "The Breach has swallowed another frontier town.  Refugees stream "
            "westward with hollow eyes, speaking of a silence so total that "
            "even thought falters within it.  The Gatefall Remnant is "
            "overwhelmed.  The wardens call for champions.  Whatever is coming "
            "from beyond the Breach, it is not slowing down."
        ),
        "rewards": {"xp": 2000, "title": "Breach Warden"},
    },
    {
        "id": "lords_gambit",
        "title": "The Lords' Gambit",
        "description": "The Elemental Lords make their move.",
        "trigger": {"type": "level", "value": 20},
        "narrative": (
            "The Lord of Stone stirs in his slumber and the mountains crack.  "
            "The Lady of Fire rages, her forges burning white-hot beneath "
            "Kharazhad.  The Lady of the Sea retreats, pulling tides inward "
            "as if bracing for impact.  Across the world, Kin-sense blazes "
            "with raw elemental static -- painful, overwhelming.  The Lords "
            "are gathering their strength for something.  And in the silence "
            "of Gatefall Reach, something answers."
        ),
        "rewards": {"xp": 5000, "title": "Champion of Oreka"},
    },
]

# Room-triggered narrative fragments (region -> chapter prerequisites)
ROOM_NARRATIVE_TRIGGERS: Dict[str, Dict[str, Any]] = {
    "gatefall_reach": {
        "chapter": "breach_arrival",
        "title": "At the Edge of Silence",
        "requires": ["the_breach"],
        "narrative": (
            "You cross into Gatefall Reach and feel your Kin-sense dim, as "
            "though cotton has been pressed against that inner ear.  The air "
            "is colder here, and the elemental resonance that has been a "
            "constant companion since your awakening falters and stutters.  "
            "This is the frontier -- the edge of everything familiar."
        ),
        "rewards": {"xp": 200},
    },
    "infinite_desert": {
        "chapter": "glass_wastes_arrival",
        "title": "The Glass Wastes",
        "requires": ["awakening"],
        "narrative": (
            "Heat shimmers rise from volcanic glass that stretches to the "
            "horizon.  Your Kin-sense goes utterly silent -- not the creeping "
            "wrongness of the Breach, but a natural dead zone scoured clean "
            "by elemental fire.  The Sand Wardens call this the Glass Wastes.  "
            "Many enter.  Fewer leave."
        ),
        "rewards": {"xp": 150},
    },
    "kinsweave": {
        "chapter": "aldenheim_approach",
        "title": "Echoes of Aldenheim",
        "requires": ["awakening"],
        "narrative": (
            "Highland winds carry the faint resonance of something ancient -- "
            "an echo of the city that once stood here before House Buarath "
            "seized the EarthForge.  Ruins dot the hills, watched by Buarath "
            "sentinels who regard you with cold suspicion.  Three centuries of "
            "secrets lie buried in these stones."
        ),
        "rewards": {"xp": 150},
    },
    "deepwater_marches": {
        "chapter": "jungle_depths",
        "title": "Into the Marches",
        "requires": ["awakening"],
        "narrative": (
            "Dense jungle closes around you.  Kin-sense blooms with warm_static "
            "-- countless small lives, insects, plants, all humming at the edge "
            "of perception.  Somewhere deeper in, Warg settlements thrive: freed "
            "servitors who have built their own civilization far from Kin scrutiny."
        ),
        "rewards": {"xp": 150},
    },
}

# Kill-triggered narrative (mob template ID -> narrative)
KILL_NARRATIVE_TRIGGERS: Dict[str, Dict[str, Any]] = {
    "breach_creature": {
        "chapter": "first_breach_kill",
        "title": "The Silence Bleeds",
        "requires": ["the_breach"],
        "narrative": (
            "The creature falls and dissolves into nothing -- no corpse, no "
            "blood, only a fading absence.  Your Kin-sense recoils from the "
            "space where it was, as though the world itself is relieved.  "
            "These things are not alive in any way you understand.  They are "
            "holes in the world, wearing shapes."
        ),
        "rewards": {"xp": 250},
    },
}


# ---------------------------------------------------------------------------
# Chapter state helpers
# ---------------------------------------------------------------------------

def _get_progress(character) -> List[str]:
    """Return the character's narrative_progress list, creating it if absent."""
    if not hasattr(character, "narrative_progress"):
        character.narrative_progress = []
    return character.narrative_progress


def _has_chapter(character, chapter_id: str) -> bool:
    """Check whether *character* has completed a chapter."""
    return chapter_id in _get_progress(character)


def _complete_chapter(character, chapter_id: str) -> None:
    """Mark a chapter as complete on the character."""
    progress = _get_progress(character)
    if chapter_id not in progress:
        progress.append(chapter_id)


# ---------------------------------------------------------------------------
# Narrative Manager
# ---------------------------------------------------------------------------

class NarrativeManager:
    """
    Central controller for the Oreka story arc.

    Checks trigger conditions against character state and delivers cutscene
    text + rewards when a chapter activates.
    """

    def __init__(self):
        self.chapters: List[Dict[str, Any]] = list(STORY_CHAPTERS)
        self.room_triggers: Dict[str, Dict[str, Any]] = dict(ROOM_NARRATIVE_TRIGGERS)
        self.kill_triggers: Dict[str, Dict[str, Any]] = dict(KILL_NARRATIVE_TRIGGERS)
        self.lore: Dict[str, str] = _load_lore()
        logger.info(
            "NarrativeManager initialised: %d chapters, %d room triggers, "
            "%d kill triggers, %d lore entries",
            len(self.chapters),
            len(self.room_triggers),
            len(self.kill_triggers),
            len(self.lore),
        )

    # ------------------------------------------------------------------
    # Trigger checking
    # ------------------------------------------------------------------

    def _check_trigger(self, character, trigger: Dict[str, Any]) -> bool:
        """Evaluate a single trigger condition against *character*."""
        ttype = trigger.get("type")

        if ttype == "level":
            return getattr(character, "level", 0) >= trigger.get("value", 999)

        if ttype == "faction_rep":
            faction = trigger.get("faction", "any")
            threshold = trigger.get("value", 0)
            rep = getattr(character, "reputation", {})
            if faction == "any":
                return any(v >= threshold for v in rep.values())
            return rep.get(faction, 0) >= threshold

        if ttype == "quest_complete":
            quest_id = trigger.get("quest")
            quest_log = getattr(character, "quest_log", None)
            if quest_log is None:
                return False
            return any(
                q.get("id") == quest_id and q.get("state") == "turned_in"
                for q in (quest_log.to_dict() if hasattr(quest_log, "to_dict") else {}).get("quests", [])
            )

        if ttype == "room":
            room = getattr(character, "room", None)
            if room is None:
                return False
            target_vnum = trigger.get("vnum")
            if target_vnum is not None:
                return room.vnum == target_vnum
            target_region = trigger.get("region")
            if target_region is not None:
                return _room_region(room) == target_region
            return False

        if ttype == "kill":
            # Kill triggers checked via on_kill hook, not here
            return False

        logger.debug("Unknown trigger type: %s", ttype)
        return False

    def check_triggers(self, character) -> List[Dict[str, Any]]:
        """
        Evaluate all main-arc chapters against *character*.

        Returns a list of chapter dicts that have just become eligible
        (i.e., trigger met and not already completed).
        """
        newly_triggered: List[Dict[str, Any]] = []
        for chapter in self.chapters:
            cid = chapter["id"]
            if _has_chapter(character, cid):
                continue
            if self._check_trigger(character, chapter.get("trigger", {})):
                newly_triggered.append(chapter)
        return newly_triggered

    # ------------------------------------------------------------------
    # Chapter activation
    # ------------------------------------------------------------------

    def trigger_chapter(
        self, character, chapter: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Activate *chapter* for *character*.

        * Marks the chapter complete.
        * Awards rewards (XP, titles).
        * Returns ``(formatted_cutscene_text, rewards_dict)``.
        """
        cid = chapter["id"]
        if _has_chapter(character, cid):
            return ("", {})

        _complete_chapter(character, cid)

        rewards = dict(chapter.get("rewards", {}))
        self._apply_rewards(character, rewards)

        cutscene = self.format_cutscene(chapter["title"], chapter["narrative"])
        reward_lines = self._format_rewards(rewards)
        if reward_lines:
            cutscene += reward_lines

        logger.info(
            "Chapter '%s' triggered for %s",
            cid,
            getattr(character, "name", "?"),
        )
        return (cutscene, rewards)

    # ------------------------------------------------------------------
    # Reward application
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_rewards(character, rewards: Dict[str, Any]) -> None:
        """Apply reward dict to *character*."""
        xp = rewards.get("xp", 0)
        if xp and hasattr(character, "xp"):
            character.xp = getattr(character, "xp", 0) + xp

        title = rewards.get("title")
        if title:
            titles = getattr(character, "titles", [])
            if title not in titles:
                titles.append(title)
                character.titles = titles

        gold = rewards.get("gold", 0)
        if gold and hasattr(character, "gold"):
            character.gold = getattr(character, "gold", 0) + gold

    @staticmethod
    def _format_rewards(rewards: Dict[str, Any]) -> str:
        """Return a coloured summary of rewards earned."""
        parts: List[str] = []
        if rewards.get("xp"):
            parts.append(f"\033[1;33m+{rewards['xp']} XP\033[0m")
        if rewards.get("gold"):
            parts.append(f"\033[1;33m+{rewards['gold']} gold\033[0m")
        if rewards.get("title"):
            parts.append(f"\033[1;36mTitle earned: {rewards['title']}\033[0m")
        if not parts:
            return ""
        return "\n  ".join([""] + parts) + "\n"

    # ------------------------------------------------------------------
    # Progress / display
    # ------------------------------------------------------------------

    def get_progress(self, character) -> List[Dict[str, str]]:
        """
        Return a list of chapter status dicts for *character*.

        Each entry:
        ``{"id": ..., "title": ..., "description": ..., "status": ...}``

        ``status`` is one of ``"completed"``, ``"available"``, ``"locked"``.
        """
        progress = _get_progress(character)
        result: List[Dict[str, str]] = []
        for chapter in self.chapters:
            cid = chapter["id"]
            if cid in progress:
                status = "completed"
            elif self._check_trigger(character, chapter.get("trigger", {})):
                status = "available"
            else:
                status = "locked"
            result.append(
                {
                    "id": cid,
                    "title": chapter["title"],
                    "description": chapter["description"],
                    "status": status,
                }
            )
        # Include room-triggered chapters the character has completed
        for region, trigger_data in self.room_triggers.items():
            cid = trigger_data["chapter"]
            if cid in progress:
                result.append(
                    {
                        "id": cid,
                        "title": trigger_data["title"],
                        "description": trigger_data["narrative"][:80] + "...",
                        "status": "completed",
                    }
                )
        # Include kill-triggered chapters the character has completed
        for mob_key, trigger_data in self.kill_triggers.items():
            cid = trigger_data["chapter"]
            if cid in progress:
                result.append(
                    {
                        "id": cid,
                        "title": trigger_data["title"],
                        "description": trigger_data["narrative"][:80] + "...",
                        "status": "completed",
                    }
                )
        return result

    def get_current_chapter(self, character) -> Optional[Dict[str, Any]]:
        """
        Return the latest *available* main-arc chapter, or the most recently
        completed one if nothing new is available.
        """
        progress = _get_progress(character)
        latest_completed: Optional[Dict[str, Any]] = None
        for chapter in self.chapters:
            cid = chapter["id"]
            if cid in progress:
                latest_completed = chapter
            elif self._check_trigger(character, chapter.get("trigger", {})):
                return chapter
        return latest_completed

    def format_story(self, character) -> str:
        """
        Build a display-ready story progress string for the ``story``
        command, showing each chapter with coloured status indicators.
        """
        lines: List[str] = [
            "",
            "\033[1;35m" + "=" * 60 + "\033[0m",
            "\033[1;35m  The Story of Oreka\033[0m",
            "\033[1;35m" + "=" * 60 + "\033[0m",
            "",
        ]
        progress_list = self.get_progress(character)
        for entry in progress_list:
            status = entry["status"]
            if status == "completed":
                marker = "\033[1;32m[*]\033[0m"  # green check
            elif status == "available":
                marker = "\033[1;33m[!]\033[0m"  # yellow exclamation
            else:
                marker = "\033[1;30m[-]\033[0m"  # grey dash
            lines.append(f"  {marker} \033[1m{entry['title']}\033[0m")
            lines.append(f"      {entry['description']}")
            lines.append("")

        completed = sum(1 for e in progress_list if e["status"] == "completed")
        total = len(progress_list)
        lines.append(
            f"  \033[0;36mProgress: {completed}/{total} chapters\033[0m"
        )
        lines.append(
            "\033[1;35m" + "=" * 60 + "\033[0m\n"
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Cutscene formatting
    # ------------------------------------------------------------------

    @staticmethod
    def format_cutscene(title: str, text: str) -> str:
        """
        Wrap *title* and *text* in an ANSI-coloured cutscene box.
        """
        lines = [
            "\n\033[1;35m" + "=" * 60 + "\033[0m",
            f"\033[1;35m  {title}\033[0m",
            "\033[1;35m" + "=" * 60 + "\033[0m",
            "",
            f"\033[0;37m{text}\033[0m",
            "",
            "\033[1;35m" + "=" * 60 + "\033[0m\n",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Event hooks
    # ------------------------------------------------------------------

    def on_level_up(self, character) -> List[Tuple[Dict[str, Any], str]]:
        """
        Called when *character* gains a level.

        Returns a list of ``(chapter, cutscene_text)`` for every chapter
        that just triggered.
        """
        results: List[Tuple[Dict[str, Any], str]] = []
        for chapter in self.check_triggers(character):
            text, _rewards = self.trigger_chapter(character, chapter)
            if text:
                results.append((chapter, text))
        return results

    def on_enter_room(self, character, room) -> List[Tuple[Dict[str, Any], str]]:
        """
        Called when *character* enters *room*.

        Checks both main-arc room triggers and region-based narrative
        fragments.
        """
        results: List[Tuple[Dict[str, Any], str]] = []

        # Main-arc triggers that use room-type conditions
        for chapter in self.chapters:
            cid = chapter["id"]
            if _has_chapter(character, cid):
                continue
            trigger = chapter.get("trigger", {})
            if trigger.get("type") == "room":
                if self._check_trigger(character, trigger):
                    text, _rewards = self.trigger_chapter(character, chapter)
                    if text:
                        results.append((chapter, text))

        # Region-based narrative fragments
        region = _room_region(room)
        if region and region in self.room_triggers:
            trigger_data = self.room_triggers[region]
            cid = trigger_data["chapter"]
            if not _has_chapter(character, cid):
                # Check prerequisites
                requires = trigger_data.get("requires", [])
                if all(_has_chapter(character, req) for req in requires):
                    _complete_chapter(character, cid)
                    rewards = dict(trigger_data.get("rewards", {}))
                    self._apply_rewards(character, rewards)
                    text = self.format_cutscene(
                        trigger_data["title"], trigger_data["narrative"]
                    )
                    reward_text = self._format_rewards(rewards)
                    if reward_text:
                        text += reward_text
                    results.append((trigger_data, text))
                    logger.info(
                        "Room narrative '%s' triggered for %s in %s",
                        cid,
                        getattr(character, "name", "?"),
                        region,
                    )

        return results

    def on_kill(self, character, mob) -> List[Tuple[Dict[str, Any], str]]:
        """
        Called when *character* kills *mob*.

        Checks kill-triggered narrative fragments.
        """
        results: List[Tuple[Dict[str, Any], str]] = []

        # Match mob against kill triggers by template_id or name
        mob_template = getattr(mob, "template_id", None) or ""
        mob_name = getattr(mob, "name", "") or ""
        mob_keys = {mob_template.lower(), mob_name.lower()}

        for trigger_key, trigger_data in self.kill_triggers.items():
            if trigger_key.lower() not in mob_keys:
                continue
            cid = trigger_data["chapter"]
            if _has_chapter(character, cid):
                continue
            requires = trigger_data.get("requires", [])
            if not all(_has_chapter(character, req) for req in requires):
                continue

            _complete_chapter(character, cid)
            rewards = dict(trigger_data.get("rewards", {}))
            self._apply_rewards(character, rewards)
            text = self.format_cutscene(
                trigger_data["title"], trigger_data["narrative"]
            )
            reward_text = self._format_rewards(rewards)
            if reward_text:
                text += reward_text
            results.append((trigger_data, text))
            logger.info(
                "Kill narrative '%s' triggered for %s (killed %s)",
                cid,
                getattr(character, "name", "?"),
                mob_name,
            )

        return results

    def on_faction_change(
        self, character, faction: str, new_rep: int
    ) -> List[Tuple[Dict[str, Any], str]]:
        """
        Called when *character*'s reputation with *faction* changes.

        Re-evaluates faction_rep triggers on main-arc chapters.
        """
        results: List[Tuple[Dict[str, Any], str]] = []
        for chapter in self.chapters:
            cid = chapter["id"]
            if _has_chapter(character, cid):
                continue
            trigger = chapter.get("trigger", {})
            if trigger.get("type") != "faction_rep":
                continue
            if self._check_trigger(character, trigger):
                text, _rewards = self.trigger_chapter(character, chapter)
                if text:
                    results.append((chapter, text))
        return results

    # ------------------------------------------------------------------
    # Lore lookup
    # ------------------------------------------------------------------

    def get_lore(self, topic: str) -> Optional[str]:
        """
        Look up a lore entry by key or substring.

        Returns the lore text or ``None``.
        """
        topic_lower = topic.lower().strip()
        # Exact match first
        if topic_lower in self.lore:
            return self.lore[topic_lower]
        # Substring / partial match
        for key, text in self.lore.items():
            if topic_lower in key:
                return text
        return None

    def format_lore(self, topic: str) -> str:
        """Return formatted lore text for display, or a not-found message."""
        text = self.get_lore(topic)
        if text is None:
            return f"\033[0;33mNo lore found for '{topic}'.\033[0m"
        display_title = topic.replace("_", " ").title()
        return self.format_cutscene(f"Lore: {display_title}", text)


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_narrative_manager: Optional[NarrativeManager] = None


def get_narrative_manager() -> NarrativeManager:
    """Return the singleton NarrativeManager instance."""
    global _narrative_manager
    if _narrative_manager is None:
        _narrative_manager = NarrativeManager()
    return _narrative_manager
