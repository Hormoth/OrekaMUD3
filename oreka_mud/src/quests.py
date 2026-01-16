# quests.py
"""
D&D 3.5 Quest System for OrekaMUD

This module implements a comprehensive quest system including:
- Multiple quest types (kill, collect, deliver, escort, explore, talk)
- Quest objectives with progress tracking
- Quest rewards (XP, gold, items, reputation)
- Quest prerequisites (level, quests, reputation, items)
- Quest chains and branching
- NPC quest givers
- Quest states and lifecycle
"""

import random
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class QuestState(Enum):
    """Quest lifecycle states."""
    UNAVAILABLE = "unavailable"  # Prerequisites not met
    AVAILABLE = "available"      # Can be accepted
    ACTIVE = "active"            # Currently in progress
    COMPLETE = "complete"        # Objectives done, awaiting turn-in
    TURNED_IN = "turned_in"      # Rewards claimed
    FAILED = "failed"            # Quest failed (time limit, wrong choice, etc.)
    ABANDONED = "abandoned"      # Player dropped the quest


class ObjectiveType(Enum):
    """Types of quest objectives."""
    KILL = "kill"                # Kill X of mob type
    COLLECT = "collect"          # Collect X items
    DELIVER = "deliver"          # Deliver item to NPC
    ESCORT = "escort"            # Escort NPC to location
    EXPLORE = "explore"          # Visit a location
    TALK = "talk"                # Talk to an NPC
    USE = "use"                  # Use an item/object
    DEFEND = "defend"            # Protect something for time
    SKILL_CHECK = "skill_check"  # Pass a skill check
    CHOICE = "choice"            # Make a choice (branching)


@dataclass
class QuestObjective:
    """A single objective within a quest."""
    id: str
    objective_type: ObjectiveType
    description: str
    target: str = ""              # Mob type, item name, NPC name, room vnum, etc.
    required_count: int = 1       # How many needed
    current_count: int = 0        # Current progress
    optional: bool = False        # Is this objective optional?
    hidden: bool = False          # Hidden until discovered
    order: int = 0                # For sequential objectives (0 = any order)
    skill_name: str = ""          # For skill check objectives
    skill_dc: int = 15            # DC for skill check objectives

    @property
    def is_complete(self) -> bool:
        """Check if objective is complete."""
        return self.current_count >= self.required_count

    @property
    def progress_text(self) -> str:
        """Get progress display text."""
        if self.objective_type == ObjectiveType.EXPLORE:
            return "Complete" if self.is_complete else "Incomplete"
        elif self.objective_type == ObjectiveType.TALK:
            return "Complete" if self.is_complete else "Not yet spoken to"
        elif self.objective_type == ObjectiveType.CHOICE:
            return "Decision made" if self.is_complete else "Awaiting decision"
        else:
            return f"{self.current_count}/{self.required_count}"

    def to_dict(self) -> Dict:
        """Serialize objective to dict."""
        return {
            "id": self.id,
            "objective_type": self.objective_type.value,
            "description": self.description,
            "target": self.target,
            "required_count": self.required_count,
            "current_count": self.current_count,
            "optional": self.optional,
            "hidden": self.hidden,
            "order": self.order,
            "skill_name": self.skill_name,
            "skill_dc": self.skill_dc,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestObjective':
        """Deserialize objective from dict."""
        return cls(
            id=data["id"],
            objective_type=ObjectiveType(data["objective_type"]),
            description=data["description"],
            target=data.get("target", ""),
            required_count=data.get("required_count", 1),
            current_count=data.get("current_count", 0),
            optional=data.get("optional", False),
            hidden=data.get("hidden", False),
            order=data.get("order", 0),
            skill_name=data.get("skill_name", ""),
            skill_dc=data.get("skill_dc", 15),
        )


@dataclass
class QuestReward:
    """Rewards for completing a quest."""
    xp: int = 0
    gold: int = 0
    items: List[str] = field(default_factory=list)  # Item vnums or names
    reputation: Dict[str, int] = field(default_factory=dict)  # faction: amount
    unlock_quests: List[int] = field(default_factory=list)  # Quest IDs to unlock
    class_feature: str = ""       # Special class feature or ability
    title: str = ""               # Title to grant

    def to_dict(self) -> Dict:
        """Serialize reward to dict."""
        return {
            "xp": self.xp,
            "gold": self.gold,
            "items": self.items,
            "reputation": self.reputation,
            "unlock_quests": self.unlock_quests,
            "class_feature": self.class_feature,
            "title": self.title,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestReward':
        """Deserialize reward from dict."""
        return cls(
            xp=data.get("xp", 0),
            gold=data.get("gold", 0),
            items=data.get("items", []),
            reputation=data.get("reputation", {}),
            unlock_quests=data.get("unlock_quests", []),
            class_feature=data.get("class_feature", ""),
            title=data.get("title", ""),
        )


@dataclass
class QuestPrerequisite:
    """Prerequisites for accepting a quest."""
    min_level: int = 1
    max_level: int = 99
    required_quests: List[int] = field(default_factory=list)  # Quest IDs that must be complete
    required_class: str = ""      # Required class (empty = any)
    required_race: str = ""       # Required race (empty = any)
    required_alignment: str = ""  # Required alignment (empty = any)
    required_reputation: Dict[str, int] = field(default_factory=dict)  # faction: min_rep
    required_items: List[str] = field(default_factory=list)  # Must have these items
    required_skills: Dict[str, int] = field(default_factory=dict)  # skill: min_ranks

    def check(self, character, quest_log: 'QuestLog') -> Tuple[bool, str]:
        """
        Check if character meets prerequisites.
        Returns (passes: bool, reason: str)
        """
        # Level check
        level = getattr(character, 'level', 1)
        if level < self.min_level:
            return False, f"Requires level {self.min_level}"
        if level > self.max_level:
            return False, f"Maximum level {self.max_level}"

        # Quest completion check
        for quest_id in self.required_quests:
            if not quest_log.is_quest_complete(quest_id):
                return False, f"Requires completion of quest #{quest_id}"

        # Class check
        if self.required_class:
            char_class = getattr(character, 'char_class', '').lower()
            if char_class != self.required_class.lower():
                return False, f"Requires {self.required_class} class"

        # Race check
        if self.required_race:
            race = getattr(character, 'race', '').lower()
            if race != self.required_race.lower():
                return False, f"Requires {self.required_race} race"

        # Alignment check
        if self.required_alignment:
            alignment = getattr(character, 'alignment', '').lower()
            if alignment != self.required_alignment.lower():
                return False, f"Requires {self.required_alignment} alignment"

        # Reputation check
        reputation = getattr(character, 'reputation', {})
        for faction, min_rep in self.required_reputation.items():
            current_rep = reputation.get(faction, 0)
            if current_rep < min_rep:
                return False, f"Requires {min_rep} reputation with {faction}"

        # Item check
        inventory = getattr(character, 'inventory', [])
        inv_names = [item.name.lower() for item in inventory]
        for item_name in self.required_items:
            if item_name.lower() not in inv_names:
                return False, f"Requires item: {item_name}"

        # Skill check
        skills = getattr(character, 'skills', {})
        for skill_name, min_ranks in self.required_skills.items():
            if skills.get(skill_name, 0) < min_ranks:
                return False, f"Requires {min_ranks} ranks in {skill_name}"

        return True, "Prerequisites met"

    def to_dict(self) -> Dict:
        """Serialize prerequisite to dict."""
        return {
            "min_level": self.min_level,
            "max_level": self.max_level,
            "required_quests": self.required_quests,
            "required_class": self.required_class,
            "required_race": self.required_race,
            "required_alignment": self.required_alignment,
            "required_reputation": self.required_reputation,
            "required_items": self.required_items,
            "required_skills": self.required_skills,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestPrerequisite':
        """Deserialize prerequisite from dict."""
        return cls(
            min_level=data.get("min_level", 1),
            max_level=data.get("max_level", 99),
            required_quests=data.get("required_quests", []),
            required_class=data.get("required_class", ""),
            required_race=data.get("required_race", ""),
            required_alignment=data.get("required_alignment", ""),
            required_reputation=data.get("required_reputation", {}),
            required_items=data.get("required_items", []),
            required_skills=data.get("required_skills", {}),
        )


@dataclass
class Quest:
    """A complete quest definition."""
    id: int
    name: str
    description: str
    objectives: List[QuestObjective]
    rewards: QuestReward
    prerequisites: QuestPrerequisite = field(default_factory=QuestPrerequisite)

    # Quest metadata
    level: int = 1                # Suggested level
    category: str = "main"        # main, side, daily, repeatable
    giver_npc: str = ""           # NPC who gives the quest
    giver_room: int = 0           # Room vnum where quest starts
    turnin_npc: str = ""          # NPC to turn in to (empty = same as giver)
    turnin_room: int = 0          # Room vnum for turn-in

    # Quest behavior
    time_limit: int = 0           # Time limit in minutes (0 = no limit)
    repeatable: bool = False      # Can be done multiple times
    shareable: bool = True        # Can share with party
    abandonable: bool = True      # Can be abandoned
    auto_accept: bool = False     # Automatically accepted on trigger
    auto_complete: bool = False   # Automatically completes on objectives done

    # Story/dialogue
    accept_text: str = ""         # Text when accepting
    progress_text: str = ""       # Text when checking progress
    complete_text: str = ""       # Text when completing
    fail_text: str = ""           # Text when failing

    # Chain/branching
    chain_quest: int = 0          # Next quest in chain (0 = none)
    branch_quests: List[int] = field(default_factory=list)  # Alternative quests based on choices

    def get_objective(self, obj_id: str) -> Optional[QuestObjective]:
        """Get an objective by ID."""
        for obj in self.objectives:
            if obj.id == obj_id:
                return obj
        return None

    @property
    def all_objectives_complete(self) -> bool:
        """Check if all required objectives are complete."""
        for obj in self.objectives:
            if not obj.optional and not obj.is_complete:
                return False
        return True

    @property
    def visible_objectives(self) -> List[QuestObjective]:
        """Get list of visible (non-hidden) objectives."""
        return [obj for obj in self.objectives if not obj.hidden]

    def to_dict(self) -> Dict:
        """Serialize quest to dict."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "rewards": self.rewards.to_dict(),
            "prerequisites": self.prerequisites.to_dict(),
            "level": self.level,
            "category": self.category,
            "giver_npc": self.giver_npc,
            "giver_room": self.giver_room,
            "turnin_npc": self.turnin_npc,
            "turnin_room": self.turnin_room,
            "time_limit": self.time_limit,
            "repeatable": self.repeatable,
            "shareable": self.shareable,
            "abandonable": self.abandonable,
            "auto_accept": self.auto_accept,
            "auto_complete": self.auto_complete,
            "accept_text": self.accept_text,
            "progress_text": self.progress_text,
            "complete_text": self.complete_text,
            "fail_text": self.fail_text,
            "chain_quest": self.chain_quest,
            "branch_quests": self.branch_quests,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Quest':
        """Deserialize quest from dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            objectives=[QuestObjective.from_dict(o) for o in data.get("objectives", [])],
            rewards=QuestReward.from_dict(data.get("rewards", {})),
            prerequisites=QuestPrerequisite.from_dict(data.get("prerequisites", {})),
            level=data.get("level", 1),
            category=data.get("category", "main"),
            giver_npc=data.get("giver_npc", ""),
            giver_room=data.get("giver_room", 0),
            turnin_npc=data.get("turnin_npc", ""),
            turnin_room=data.get("turnin_room", 0),
            time_limit=data.get("time_limit", 0),
            repeatable=data.get("repeatable", False),
            shareable=data.get("shareable", True),
            abandonable=data.get("abandonable", True),
            auto_accept=data.get("auto_accept", False),
            auto_complete=data.get("auto_complete", False),
            accept_text=data.get("accept_text", ""),
            progress_text=data.get("progress_text", ""),
            complete_text=data.get("complete_text", ""),
            fail_text=data.get("fail_text", ""),
            chain_quest=data.get("chain_quest", 0),
            branch_quests=data.get("branch_quests", []),
        )


@dataclass
class ActiveQuest:
    """
    An instance of a quest in a player's quest log.
    Contains the quest reference and player-specific progress.
    """
    quest_id: int
    state: QuestState
    objectives: List[QuestObjective]  # Copy with player's progress
    start_time: float = 0.0           # When quest was accepted
    completion_time: float = 0.0      # When quest was completed

    def to_dict(self) -> Dict:
        """Serialize active quest to dict."""
        return {
            "quest_id": self.quest_id,
            "state": self.state.value,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "start_time": self.start_time,
            "completion_time": self.completion_time,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ActiveQuest':
        """Deserialize active quest from dict."""
        return cls(
            quest_id=data["quest_id"],
            state=QuestState(data["state"]),
            objectives=[QuestObjective.from_dict(o) for o in data.get("objectives", [])],
            start_time=data.get("start_time", 0.0),
            completion_time=data.get("completion_time", 0.0),
        )


class QuestLog:
    """
    Manages a player's quests.
    """

    def __init__(self):
        self.active_quests: Dict[int, ActiveQuest] = {}  # quest_id -> ActiveQuest
        self.completed_quests: Set[int] = set()          # Quest IDs completed
        self.failed_quests: Set[int] = set()             # Quest IDs failed
        self.abandoned_quests: Set[int] = set()          # Quest IDs abandoned

    def accept_quest(self, quest: Quest) -> Tuple[bool, str]:
        """Accept a new quest."""
        import time

        if quest.id in self.active_quests:
            return False, "Quest already active."

        if quest.id in self.completed_quests and not quest.repeatable:
            return False, "Quest already completed."

        # Create active quest with copy of objectives
        objectives = [
            QuestObjective(
                id=obj.id,
                objective_type=obj.objective_type,
                description=obj.description,
                target=obj.target,
                required_count=obj.required_count,
                current_count=0,  # Reset progress
                optional=obj.optional,
                hidden=obj.hidden,
                order=obj.order,
                skill_name=obj.skill_name,
                skill_dc=obj.skill_dc,
            )
            for obj in quest.objectives
        ]

        active_quest = ActiveQuest(
            quest_id=quest.id,
            state=QuestState.ACTIVE,
            objectives=objectives,
            start_time=time.time(),
        )

        self.active_quests[quest.id] = active_quest
        return True, f"Quest accepted: {quest.name}"

    def abandon_quest(self, quest_id: int) -> Tuple[bool, str]:
        """Abandon an active quest."""
        if quest_id not in self.active_quests:
            return False, "Quest not in your log."

        del self.active_quests[quest_id]
        self.abandoned_quests.add(quest_id)
        return True, "Quest abandoned."

    def complete_quest(self, quest_id: int) -> Tuple[bool, str]:
        """Mark a quest as complete (ready for turn-in)."""
        import time

        if quest_id not in self.active_quests:
            return False, "Quest not in your log."

        active_quest = self.active_quests[quest_id]
        active_quest.state = QuestState.COMPLETE
        active_quest.completion_time = time.time()
        return True, "Quest objectives complete!"

    def turn_in_quest(self, quest_id: int) -> Tuple[bool, str]:
        """Turn in a completed quest and claim rewards."""
        if quest_id not in self.active_quests:
            return False, "Quest not in your log."

        active_quest = self.active_quests[quest_id]
        if active_quest.state != QuestState.COMPLETE:
            return False, "Quest objectives not complete."

        # Move to completed
        del self.active_quests[quest_id]
        self.completed_quests.add(quest_id)
        return True, "Quest turned in!"

    def fail_quest(self, quest_id: int, reason: str = "") -> Tuple[bool, str]:
        """Mark a quest as failed."""
        if quest_id not in self.active_quests:
            return False, "Quest not in your log."

        del self.active_quests[quest_id]
        self.failed_quests.add(quest_id)
        return True, f"Quest failed{': ' + reason if reason else '.'}"

    def update_objective(
        self,
        quest_id: int,
        objective_id: str,
        progress: int = 1,
        set_value: bool = False
    ) -> Tuple[bool, str]:
        """
        Update progress on a quest objective.
        """
        if quest_id not in self.active_quests:
            return False, ""

        active_quest = self.active_quests[quest_id]
        if active_quest.state != QuestState.ACTIVE:
            return False, ""

        for obj in active_quest.objectives:
            if obj.id == objective_id:
                old_count = obj.current_count
                if set_value:
                    obj.current_count = min(progress, obj.required_count)
                else:
                    obj.current_count = min(obj.current_count + progress, obj.required_count)

                if obj.current_count > old_count:
                    msg = f"Quest progress: {obj.description} ({obj.progress_text})"
                    if obj.is_complete:
                        msg += " - COMPLETE!"
                    return True, msg

        return False, ""

    def check_objective_by_target(
        self,
        objective_type: ObjectiveType,
        target: str,
        progress: int = 1
    ) -> List[str]:
        """
        Check all active quests for matching objectives and update them.
        Returns list of progress messages.
        """
        messages = []
        target_lower = target.lower()

        for quest_id, active_quest in self.active_quests.items():
            if active_quest.state != QuestState.ACTIVE:
                continue

            for obj in active_quest.objectives:
                if obj.objective_type == objective_type and not obj.is_complete:
                    # Check if target matches
                    if obj.target.lower() in target_lower or target_lower in obj.target.lower():
                        updated, msg = self.update_objective(quest_id, obj.id, progress)
                        if updated:
                            messages.append(msg)

        return messages

    def get_active_quest(self, quest_id: int) -> Optional[ActiveQuest]:
        """Get an active quest by ID."""
        return self.active_quests.get(quest_id)

    def is_quest_complete(self, quest_id: int) -> bool:
        """Check if a quest has been completed (turned in)."""
        return quest_id in self.completed_quests

    def is_quest_active(self, quest_id: int) -> bool:
        """Check if a quest is currently active."""
        return quest_id in self.active_quests

    def get_quests_by_state(self, state: QuestState) -> List[ActiveQuest]:
        """Get all quests with a specific state."""
        return [q for q in self.active_quests.values() if q.state == state]

    def to_dict(self) -> Dict:
        """Serialize quest log to dict."""
        return {
            "active_quests": {
                str(qid): aq.to_dict()
                for qid, aq in self.active_quests.items()
            },
            "completed_quests": list(self.completed_quests),
            "failed_quests": list(self.failed_quests),
            "abandoned_quests": list(self.abandoned_quests),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'QuestLog':
        """Deserialize quest log from dict."""
        log = cls()
        for qid_str, aq_data in data.get("active_quests", {}).items():
            log.active_quests[int(qid_str)] = ActiveQuest.from_dict(aq_data)
        log.completed_quests = set(data.get("completed_quests", []))
        log.failed_quests = set(data.get("failed_quests", []))
        log.abandoned_quests = set(data.get("abandoned_quests", []))
        return log


class QuestManager:
    """
    Manages all quests in the game world.
    """

    def __init__(self):
        self.quests: Dict[int, Quest] = {}
        self.npc_quests: Dict[str, List[int]] = {}  # NPC name -> list of quest IDs

    def load_quests(self, filepath: str = None):
        """Load quests from JSON file."""
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'quests.json'
            )

        if not os.path.exists(filepath):
            self._create_default_quests()
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for quest_data in data.get("quests", []):
                    quest = Quest.from_dict(quest_data)
                    self.register_quest(quest)
        except Exception as e:
            print(f"Error loading quests: {e}")
            self._create_default_quests()

    def save_quests(self, filepath: str = None):
        """Save quests to JSON file."""
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'quests.json'
            )

        data = {
            "quests": [quest.to_dict() for quest in self.quests.values()]
        }

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _create_default_quests(self):
        """Create default starter quests."""
        # Quest 1: Starweave Ritual (existing quest)
        quest1 = Quest(
            id=1,
            name="Starweave Ritual",
            description="Travel to Guild Street and perform the ancient Starweave Ritual.",
            level=1,
            category="main",
            giver_npc="Elder Sage",
            giver_room=3001,
            objectives=[
                QuestObjective(
                    id="visit_guild",
                    objective_type=ObjectiveType.EXPLORE,
                    description="Travel to Guild Street",
                    target="3001",
                    required_count=1,
                )
            ],
            rewards=QuestReward(
                xp=1000,
                gold=50,
            ),
            accept_text="The Starweave Ritual must be performed at Guild Street. "
                       "Travel there and complete this sacred rite.",
            complete_text="You have completed the Starweave Ritual! "
                         "The stars shine brightly upon you.",
        )
        self.register_quest(quest1)

        # Quest 2: Rat Problem
        quest2 = Quest(
            id=2,
            name="The Rat Problem",
            description="Clear out the rats infesting the tavern cellar.",
            level=1,
            category="side",
            giver_npc="Innkeeper",
            giver_room=3002,
            objectives=[
                QuestObjective(
                    id="kill_rats",
                    objective_type=ObjectiveType.KILL,
                    description="Kill giant rats in the cellar",
                    target="giant rat",
                    required_count=5,
                )
            ],
            rewards=QuestReward(
                xp=500,
                gold=25,
                reputation={"Tavern": 10},
            ),
            accept_text="Those blasted rats have gotten into my cellar again! "
                       "Kill five of them and I'll make it worth your while.",
            complete_text="Thank the gods! The rats are gone! Here's your reward.",
        )
        self.register_quest(quest2)

        # Quest 3: Delivery Quest
        quest3 = Quest(
            id=3,
            name="Special Delivery",
            description="Deliver a package to the blacksmith.",
            level=1,
            category="side",
            giver_npc="Merchant",
            giver_room=3003,
            objectives=[
                QuestObjective(
                    id="get_package",
                    objective_type=ObjectiveType.COLLECT,
                    description="Receive the package from the Merchant",
                    target="merchant package",
                    required_count=1,
                    order=1,
                ),
                QuestObjective(
                    id="deliver_package",
                    objective_type=ObjectiveType.DELIVER,
                    description="Deliver the package to the Blacksmith",
                    target="blacksmith",
                    required_count=1,
                    order=2,
                ),
            ],
            rewards=QuestReward(
                xp=300,
                gold=15,
            ),
            accept_text="I need this package delivered to the blacksmith. "
                       "Can you help me out?",
            complete_text="Ah, my order arrived! Thanks for bringing it.",
        )
        self.register_quest(quest3)

        # Quest 4: Investigation quest with skill checks
        quest4 = Quest(
            id=4,
            name="The Missing Heirloom",
            description="Help find a noble's stolen family heirloom.",
            level=3,
            category="side",
            giver_npc="Noble Lady",
            giver_room=3004,
            prerequisites=QuestPrerequisite(min_level=3),
            objectives=[
                QuestObjective(
                    id="search_room",
                    objective_type=ObjectiveType.SKILL_CHECK,
                    description="Search the lady's chamber for clues",
                    skill_name="Search",
                    skill_dc=15,
                    required_count=1,
                    order=1,
                ),
                QuestObjective(
                    id="question_servants",
                    objective_type=ObjectiveType.TALK,
                    description="Question the servants",
                    target="servant",
                    required_count=3,
                    order=2,
                ),
                QuestObjective(
                    id="find_thief",
                    objective_type=ObjectiveType.EXPLORE,
                    description="Find the thief's hideout",
                    target="3010",
                    required_count=1,
                    order=3,
                    hidden=True,
                ),
                QuestObjective(
                    id="recover_heirloom",
                    objective_type=ObjectiveType.COLLECT,
                    description="Recover the stolen heirloom",
                    target="family heirloom",
                    required_count=1,
                    order=4,
                ),
            ],
            rewards=QuestReward(
                xp=800,
                gold=100,
                reputation={"Nobility": 25},
            ),
            accept_text="My grandmother's heirloom has been stolen! "
                       "Please, you must help me find it!",
            complete_text="You found it! I cannot thank you enough. "
                         "Please accept this reward.",
        )
        self.register_quest(quest4)

        # Quest 5: Kill quest chain part 1
        quest5 = Quest(
            id=5,
            name="Goblin Menace",
            description="The goblins have grown bold. Thin their numbers.",
            level=2,
            category="main",
            giver_npc="Guard Captain",
            giver_room=3005,
            prerequisites=QuestPrerequisite(min_level=2),
            chain_quest=6,
            objectives=[
                QuestObjective(
                    id="kill_goblins",
                    objective_type=ObjectiveType.KILL,
                    description="Slay goblins",
                    target="goblin",
                    required_count=10,
                )
            ],
            rewards=QuestReward(
                xp=600,
                gold=30,
                unlock_quests=[6],
            ),
            accept_text="Those green-skinned vermin are attacking travelers! "
                       "Kill at least ten of them.",
            complete_text="Good work, soldier. But I fear this is just the beginning...",
        )
        self.register_quest(quest5)

        # Quest 6: Chain quest part 2
        quest6 = Quest(
            id=6,
            name="The Goblin Chief",
            description="Find and defeat the goblin chieftain.",
            level=4,
            category="main",
            giver_npc="Guard Captain",
            giver_room=3005,
            prerequisites=QuestPrerequisite(
                min_level=4,
                required_quests=[5],
            ),
            objectives=[
                QuestObjective(
                    id="find_lair",
                    objective_type=ObjectiveType.EXPLORE,
                    description="Find the goblin lair",
                    target="3020",
                    required_count=1,
                    order=1,
                ),
                QuestObjective(
                    id="kill_chief",
                    objective_type=ObjectiveType.KILL,
                    description="Slay the Goblin Chieftain",
                    target="goblin chieftain",
                    required_count=1,
                    order=2,
                ),
            ],
            rewards=QuestReward(
                xp=1500,
                gold=150,
                items=["chieftain's blade"],
                title="Goblin Slayer",
            ),
            accept_text="The goblins have a chieftain organizing them. "
                       "Find their lair and end this threat!",
            complete_text="You've done it! The goblin threat is ended. "
                         "Take this blade as a trophy of your victory.",
        )
        self.register_quest(quest6)

    def register_quest(self, quest: Quest):
        """Register a quest in the manager."""
        self.quests[quest.id] = quest

        # Track NPC quest associations
        if quest.giver_npc:
            npc_name = quest.giver_npc.lower()
            if npc_name not in self.npc_quests:
                self.npc_quests[npc_name] = []
            if quest.id not in self.npc_quests[npc_name]:
                self.npc_quests[npc_name].append(quest.id)

    def get_quest(self, quest_id: int) -> Optional[Quest]:
        """Get a quest by ID."""
        return self.quests.get(quest_id)

    def get_quests_for_npc(self, npc_name: str) -> List[Quest]:
        """Get all quests available from an NPC."""
        npc_lower = npc_name.lower()
        quest_ids = self.npc_quests.get(npc_lower, [])
        return [self.quests[qid] for qid in quest_ids if qid in self.quests]

    def get_available_quests(
        self,
        character,
        quest_log: QuestLog,
        npc_name: str = None,
        room_vnum: int = None
    ) -> List[Quest]:
        """
        Get quests available to a character.
        Optionally filter by NPC or room.
        """
        available = []

        for quest in self.quests.values():
            # Skip if already active or completed (unless repeatable)
            if quest_log.is_quest_active(quest.id):
                continue
            if quest_log.is_quest_complete(quest.id) and not quest.repeatable:
                continue

            # Filter by NPC
            if npc_name and quest.giver_npc.lower() != npc_name.lower():
                continue

            # Filter by room
            if room_vnum and quest.giver_room != room_vnum:
                continue

            # Check prerequisites
            meets_prereqs, reason = quest.prerequisites.check(character, quest_log)
            if meets_prereqs:
                available.append(quest)

        return available

    def get_turnin_quests(
        self,
        quest_log: QuestLog,
        npc_name: str = None,
        room_vnum: int = None
    ) -> List[Tuple[Quest, ActiveQuest]]:
        """Get quests that can be turned in to an NPC."""
        turnable = []

        for quest_id, active_quest in quest_log.active_quests.items():
            if active_quest.state != QuestState.COMPLETE:
                continue

            quest = self.get_quest(quest_id)
            if not quest:
                continue

            # Check turn-in location
            turnin_npc = quest.turnin_npc or quest.giver_npc
            if npc_name and turnin_npc.lower() != npc_name.lower():
                continue

            turnin_room = quest.turnin_room or quest.giver_room
            if room_vnum and turnin_room != room_vnum:
                continue

            turnable.append((quest, active_quest))

        return turnable


# =============================================================================
# Quest Event Handlers
# =============================================================================

def on_mob_killed(character, mob, quest_log: QuestLog, quest_manager: QuestManager) -> List[str]:
    """
    Called when a mob is killed. Updates kill objectives.
    Returns list of quest progress messages.
    """
    mob_name = getattr(mob, 'name', '')
    messages = quest_log.check_objective_by_target(ObjectiveType.KILL, mob_name)

    # Check for quest completion
    for quest_id, active_quest in list(quest_log.active_quests.items()):
        if active_quest.state == QuestState.ACTIVE:
            all_complete = True
            for obj in active_quest.objectives:
                if not obj.optional and not obj.is_complete:
                    all_complete = False
                    break

            if all_complete:
                quest = quest_manager.get_quest(quest_id)
                if quest and quest.auto_complete:
                    quest_log.complete_quest(quest_id)
                    messages.append(f"Quest complete: {quest.name}!")
                else:
                    quest_log.complete_quest(quest_id)
                    messages.append(f"Quest objectives complete: {quest.name if quest else quest_id}. Return to turn in.")

    return messages


def on_item_collected(character, item, quest_log: QuestLog, quest_manager: QuestManager) -> List[str]:
    """
    Called when an item is collected. Updates collect objectives.
    Returns list of quest progress messages.
    """
    item_name = getattr(item, 'name', str(item))
    messages = quest_log.check_objective_by_target(ObjectiveType.COLLECT, item_name)

    # Check for quest completion
    for quest_id, active_quest in list(quest_log.active_quests.items()):
        if active_quest.state == QuestState.ACTIVE:
            all_complete = all(
                obj.is_complete for obj in active_quest.objectives if not obj.optional
            )
            if all_complete:
                quest = quest_manager.get_quest(quest_id)
                quest_log.complete_quest(quest_id)
                messages.append(f"Quest objectives complete: {quest.name if quest else quest_id}")

    return messages


def on_room_entered(character, room_vnum: int, quest_log: QuestLog, quest_manager: QuestManager) -> List[str]:
    """
    Called when entering a room. Updates explore objectives.
    Returns list of quest progress messages.
    """
    messages = quest_log.check_objective_by_target(ObjectiveType.EXPLORE, str(room_vnum))

    # Check for auto-accept quests in this room
    for quest in quest_manager.quests.values():
        if quest.auto_accept and quest.giver_room == room_vnum:
            if not quest_log.is_quest_active(quest.id) and not quest_log.is_quest_complete(quest.id):
                meets_prereqs, _ = quest.prerequisites.check(character, quest_log)
                if meets_prereqs:
                    success, msg = quest_log.accept_quest(quest)
                    if success:
                        messages.append(f"New quest discovered: {quest.name}")
                        if quest.accept_text:
                            messages.append(quest.accept_text)

    # Check for quest completion
    for quest_id, active_quest in list(quest_log.active_quests.items()):
        if active_quest.state == QuestState.ACTIVE:
            all_complete = all(
                obj.is_complete for obj in active_quest.objectives if not obj.optional
            )
            if all_complete:
                quest = quest_manager.get_quest(quest_id)
                quest_log.complete_quest(quest_id)
                messages.append(f"Quest objectives complete: {quest.name if quest else quest_id}")

    return messages


def on_npc_talked(character, npc_name: str, quest_log: QuestLog, quest_manager: QuestManager) -> List[str]:
    """
    Called when talking to an NPC. Updates talk objectives.
    Returns list of quest progress messages.
    """
    messages = quest_log.check_objective_by_target(ObjectiveType.TALK, npc_name)

    # Reveal hidden objectives if talk objectives complete
    for quest_id, active_quest in quest_log.active_quests.items():
        for obj in active_quest.objectives:
            if obj.objective_type == ObjectiveType.TALK and obj.is_complete:
                for next_obj in active_quest.objectives:
                    if next_obj.hidden and next_obj.order == obj.order + 1:
                        next_obj.hidden = False
                        messages.append(f"New objective revealed: {next_obj.description}")
                        break

    return messages


def on_item_delivered(character, item, npc_name: str, quest_log: QuestLog, quest_manager: QuestManager) -> List[str]:
    """
    Called when delivering an item to an NPC. Updates deliver objectives.
    Returns list of quest progress messages.
    """
    messages = quest_log.check_objective_by_target(ObjectiveType.DELIVER, npc_name)
    return messages


def apply_quest_rewards(character, quest: Quest, quest_log: QuestLog) -> List[str]:
    """
    Apply quest rewards to a character.
    Returns list of reward messages.
    """
    messages = []
    rewards = quest.rewards

    # XP reward
    if rewards.xp > 0:
        old_xp = getattr(character, 'xp', 0)
        character.xp = old_xp + rewards.xp
        messages.append(f"You gain {rewards.xp} experience points!")

        # Check for level up
        xp_thresholds = {
            1: 0, 2: 1000, 3: 3000, 4: 6000, 5: 10000,
            6: 15000, 7: 21000, 8: 28000, 9: 36000, 10: 45000,
        }
        current_level = getattr(character, 'level', 1)
        for level, threshold in sorted(xp_thresholds.items(), reverse=True):
            if character.xp >= threshold and level > current_level:
                character.level = level
                character.class_level = level
                messages.append(f"Level up! You are now level {level}!")
                break

    # Gold reward
    if rewards.gold > 0:
        old_gold = getattr(character, 'gold', 0)
        character.gold = old_gold + rewards.gold
        messages.append(f"You receive {rewards.gold} gold pieces!")

    # Item rewards
    for item_name in rewards.items:
        messages.append(f"You receive: {item_name}")

    # Reputation rewards
    reputation = getattr(character, 'reputation', {})
    for faction, amount in rewards.reputation.items():
        old_rep = reputation.get(faction, 0)
        reputation[faction] = old_rep + amount
        messages.append(f"Your reputation with {faction} increases by {amount}!")
    if rewards.reputation:
        character.reputation = reputation

    # Title reward
    if rewards.title:
        titles = getattr(character, 'titles', [])
        if rewards.title not in titles:
            titles.append(rewards.title)
            character.titles = titles
            messages.append(f"You earn the title: {rewards.title}!")

    # Unlock follow-up quests
    for unlock_id in rewards.unlock_quests:
        messages.append(f"New quest available: Quest #{unlock_id}")

    return messages
