"""
Tests for OrekaMUD3 new systems (Phase 1 and Phase 2).

Covers: consider, wimpy, scan, identify, track, bank, newbie channel,
rescue, character new fields, consumables (quaff/use), hide/sneak,
door system (open/close/lock/unlock/pick), weather, map, item charges,
and character hidden/sneaking serialization.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.character import Character, State
from src.commands import CommandParser
from src.room import Room
from src.mob import Mob
from src.items import Item


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_char(name="Hero", level=3, hp=30, max_hp=30, char_class="Fighter",
              room=None, skills=None):
    c = Character(
        name=name, title="", race="Human", level=level,
        hp=hp, max_hp=max_hp, ac=10, room=room,
        char_class=char_class, skills=skills or {}, spells_known={}
    )
    c.writer = None
    c.reader = None
    return c


def make_room(vnum=1, name="Test Room", exits=None, flags=None, weather=None):
    r = Room(vnum, name, "A test room.", exits or {}, flags or [],
             weather=weather)
    return r


def make_mob(vnum=5001, name="Goblin", level=1, cr=None):
    m = Mob(vnum, name, level, (1, 6, 0), 12, (1, 4, 0))
    if cr is not None:
        m.cr = cr
    return m


def make_item(vnum=1001, name="Iron Sword", item_type="weapon",
              stats=None, charges=None):
    return Item(vnum, name, item_type, weight=5, value=10,
                stats=stats or {}, charges=charges)


class FakeWorld:
    def __init__(self):
        self.players = []
        self.rooms = {}
        self.mobs = {}
        self.items = {}
        self.zones = []
        self.help_topics = {}
        self.area_meta = {}

    def save_rooms(self): pass
    def save_mobs(self): pass
    def save_items(self): pass
    def save_zones(self): pass
    def save_help_data(self): pass
    def save_area_meta(self): pass


# ===========================================================================
# Phase 1 Tests
# ===========================================================================

class TestConsiderCommand(unittest.TestCase):
    """Tests for cmd_consider (System 3)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(vnum=100)
        self.char = make_char(level=5, room=self.room)
        self.world.rooms[100] = self.room

    def _add_mob(self, cr):
        mob = make_mob(cr=cr)
        mob.alive = True
        self.room.mobs = [mob]
        return mob

    def test_consider_no_args(self):
        result = self.parser.cmd_consider(self.char, "")
        self.assertIn("Consider whom", result)

    def test_consider_mob_not_found(self):
        self.room.mobs = []
        result = self.parser.cmd_consider(self.char, "dragon")
        self.assertIn("don't see", result)

    def test_consider_easy_diff_plus_3(self):
        # char level 5, mob cr=2 → diff=3 → easy
        self._add_mob(cr=2)
        result = self.parser.cmd_consider(self.char, "goblin")
        self.assertIn("easy", result)

    def test_consider_even_match(self):
        # char level 5, mob cr=5 → diff=0 → even match
        self._add_mob(cr=5)
        result = self.parser.cmd_consider(self.char, "goblin")
        self.assertIn("even", result)

    def test_consider_dangerous(self):
        # char level 5, mob cr=7 → diff=-2 → dangerous
        self._add_mob(cr=7)
        result = self.parser.cmd_consider(self.char, "goblin")
        self.assertIn("dangerous", result)

    def test_consider_suicidal(self):
        # char level 1, mob cr=10 → diff=-9 → suicidal
        self.char.level = 1
        self._add_mob(cr=10)
        result = self.parser.cmd_consider(self.char, "goblin")
        self.assertIn("suicidal", result)

    def test_consider_trivial(self):
        # char level 10, mob cr=1 → diff=9 → trivial
        self.char.level = 10
        self._add_mob(cr=1)
        result = self.parser.cmd_consider(self.char, "goblin")
        self.assertIn("trivial", result)


class TestWimpyCommand(unittest.TestCase):
    """Tests for cmd_wimpy (System 4)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.char = make_char()

    def test_wimpy_default_zero(self):
        self.assertEqual(self.char.wimpy, 0)

    def test_wimpy_no_args_when_disabled(self):
        result = self.parser.cmd_wimpy(self.char, "")
        self.assertIn("disabled", result)

    def test_wimpy_set_valid(self):
        result = self.parser.cmd_wimpy(self.char, "25")
        self.assertEqual(self.char.wimpy, 25)
        self.assertIn("25", result)

    def test_wimpy_disable_with_zero(self):
        self.char.wimpy = 25
        result = self.parser.cmd_wimpy(self.char, "0")
        self.assertEqual(self.char.wimpy, 0)
        self.assertIn("disabled", result)

    def test_wimpy_above_50_rejected(self):
        result = self.parser.cmd_wimpy(self.char, "51")
        self.assertIn("between 0 and 50", result)
        self.assertEqual(self.char.wimpy, 0)

    def test_wimpy_negative_rejected(self):
        result = self.parser.cmd_wimpy(self.char, "-1")
        self.assertIn("between 0 and 50", result)

    def test_wimpy_invalid_string(self):
        result = self.parser.cmd_wimpy(self.char, "lots")
        self.assertIn("wimpy", result.lower())

    def test_wimpy_status_when_set(self):
        self.char.wimpy = 30
        result = self.parser.cmd_wimpy(self.char, "")
        self.assertIn("30", result)

    def test_wimpy_round_trip_to_dict_from_dict(self):
        self.char.wimpy = 40
        d = self.char.to_dict()
        self.assertEqual(d["wimpy"], 40)
        char2 = Character.from_dict(d)
        self.assertEqual(char2.wimpy, 40)


class TestScanCommand(unittest.TestCase):
    """Tests for cmd_scan (System 5)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(vnum=200, exits={"north": 201})
        self.north_room = make_room(vnum=201, name="North Hall")
        self.world.rooms[200] = self.room
        self.world.rooms[201] = self.north_room
        self.char = make_char(room=self.room)

    def test_scan_no_exits(self):
        self.room.exits = {}
        result = self.parser.cmd_scan(self.char, "")
        self.assertIn("no exits", result)

    def test_scan_empty_adjacent_room(self):
        result = self.parser.cmd_scan(self.char, "")
        self.assertIn("north", result)
        self.assertIn("nothing", result)

    def test_scan_shows_mob_in_adjacent_room(self):
        mob = make_mob(name="Skeleton")
        mob.alive = True
        self.north_room.mobs.append(mob)
        result = self.parser.cmd_scan(self.char, "")
        self.assertIn("Skeleton", result)
        self.assertIn("north", result)

    def test_scan_shows_player_in_adjacent_room(self):
        other = make_char(name="Alice", room=self.north_room)
        self.north_room.players.append(other)
        result = self.parser.cmd_scan(self.char, "")
        self.assertIn("Alice", result)

    def test_scan_dead_mob_not_shown(self):
        mob = make_mob(name="DeadGoblin")
        mob.alive = False
        self.north_room.mobs.append(mob)
        result = self.parser.cmd_scan(self.char, "")
        self.assertNotIn("DeadGoblin", result)


class TestIdentifyCommand(unittest.TestCase):
    """Tests for cmd_identify (System 8)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.char = make_char(skills={"Spellcraft": 15})
        self.char.int_score = 14  # +2 int mod
        self.potion = make_item(name="Potion of Healing", item_type="potion")
        self.char.inventory.append(self.potion)

    def test_identify_no_args(self):
        result = self.parser.cmd_identify(self.char, "")
        self.assertIn("Identify what", result)

    def test_identify_item_not_in_inventory(self):
        result = self.parser.cmd_identify(self.char, "dragon tooth")
        self.assertIn("don't have", result)

    def test_identify_success_shows_item_name(self):
        import unittest.mock as mock
        # Force skill check to succeed by patching random.randint
        with mock.patch("random.randint", return_value=15):
            result = self.parser.cmd_identify(self.char, "potion")
        self.assertIn("Potion of Healing", result)

    def test_identify_failure_message(self):
        import unittest.mock as mock
        # Force skill check to fail (roll=1, skill=15, int=+2 → 1+15+2=18, but we want < 15)
        # With skill=0, no spellcraft trained, it returns a string (untrained error)
        no_spell_char = make_char(skills={})
        no_spell_char.inventory.append(self.potion)
        result = self.parser.cmd_identify(no_spell_char, "potion")
        # Either "untrained" message or "fail to identify" — both are valid
        self.assertTrue(
            "untrained" in result.lower() or "fail" in result.lower(),
            f"Expected failure message, got: {result}"
        )

    def test_identify_shows_magical_field(self):
        import unittest.mock as mock
        magical_item = make_item(name="Magic Sword", item_type="weapon")
        magical_item.magical = True
        self.char.inventory.append(magical_item)
        with mock.patch("random.randint", return_value=18):
            result = self.parser.cmd_identify(self.char, "magic sword")
        self.assertIn("Magical", result)


class TestTrackCommand(unittest.TestCase):
    """Tests for cmd_track (System 9)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(vnum=300, exits={"south": 301})
        self.south_room = make_room(vnum=301, name="Forest Path")
        self.world.rooms[300] = self.room
        self.world.rooms[301] = self.south_room
        self.char = make_char(level=3, room=self.room, skills={"Survival": 10})
        self.char.feats.append("Track")

    def test_track_no_args(self):
        result = self.parser.cmd_track(self.char, "")
        self.assertIn("Track whom", result)

    def test_track_requires_track_feat(self):
        self.char.feats = []
        result = self.parser.cmd_track(self.char, "goblin")
        self.assertIn("Track feat", result)

    def test_track_success_finds_mob(self):
        import unittest.mock as mock
        mob = make_mob(name="Orc Scout")
        mob.alive = True
        self.south_room.mobs.append(mob)
        with mock.patch("random.randint", return_value=18):
            result = self.parser.cmd_track(self.char, "orc")
        self.assertIn("south", result)
        self.assertIn("orc", result.lower())

    def test_track_fail_skill_check(self):
        import unittest.mock as mock
        mob = make_mob(name="Troll")
        mob.alive = True
        self.south_room.mobs.append(mob)
        with mock.patch("random.randint", return_value=1):
            result = self.parser.cmd_track(self.char, "troll")
        self.assertIn("fail", result.lower())

    def test_track_target_not_found_in_adjacents(self):
        import unittest.mock as mock
        self.south_room.mobs = []
        with mock.patch("random.randint", return_value=20):
            result = self.parser.cmd_track(self.char, "dragon")
        self.assertIn("no tracks", result.lower())


class TestBankSystem(unittest.TestCase):
    """Tests for deposit/withdraw/balance with banker mob."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(vnum=400)
        self.banker = make_mob(name="Banker Gregor", vnum=9001)
        self.banker.flags = ["banker"]
        self.room.mobs.append(self.banker)
        self.char = make_char(room=self.room)
        self.char.gold = 500
        self.char.bank_gold = 100

    def test_deposit_no_banker(self):
        self.room.mobs = []
        result = self.parser.cmd_deposit(self.char, "100")
        self.assertIn("no banker", result.lower())

    def test_deposit_no_args(self):
        result = self.parser.cmd_deposit(self.char, "")
        self.assertIn("Deposit how much", result)

    def test_deposit_valid_amount(self):
        result = self.parser.cmd_deposit(self.char, "200")
        self.assertEqual(self.char.gold, 300)
        self.assertEqual(self.char.bank_gold, 300)
        self.assertIn("200", result)

    def test_deposit_insufficient_gold(self):
        result = self.parser.cmd_deposit(self.char, "1000")
        self.assertIn("only have", result)
        self.assertEqual(self.char.gold, 500)

    def test_deposit_zero_rejected(self):
        result = self.parser.cmd_deposit(self.char, "0")
        self.assertIn("positive", result)

    def test_withdraw_no_banker(self):
        self.room.mobs = []
        result = self.parser.cmd_withdraw(self.char, "50")
        self.assertIn("no banker", result.lower())

    def test_withdraw_valid_amount(self):
        result = self.parser.cmd_withdraw(self.char, "50")
        self.assertEqual(self.char.bank_gold, 50)
        self.assertEqual(self.char.gold, 550)

    def test_withdraw_insufficient_bank_gold(self):
        result = self.parser.cmd_withdraw(self.char, "500")
        self.assertIn("only have", result)

    def test_balance_with_banker(self):
        result = self.parser.cmd_balance(self.char, "")
        self.assertIn("100", result)

    def test_bank_gold_default_zero(self):
        char2 = make_char()
        self.assertEqual(char2.bank_gold, 0)


class TestNewbieChannel(unittest.TestCase):
    """Tests for cmd_newbie."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.char = make_char()

    def test_newbie_no_args(self):
        result = self.parser.cmd_newbie(self.char, "")
        self.assertIn("Newbie what", result)

    def test_newbie_with_message(self):
        import unittest.mock as mock
        with mock.patch("src.chat.broadcast_to_world"), \
             mock.patch("src.chat.format_newbie", return_value="[Newbie] Hero: hello"):
            result = self.parser.cmd_newbie(self.char, "hello")
        self.assertIn("Newbie", result)
        self.assertIn("hello", result)


class TestRescueCommand(unittest.TestCase):
    """Tests for cmd_rescue."""

    def setUp(self):
        from src.combat import CombatInstance, CombatantState, _active_combats
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(vnum=500)
        self.world.rooms[500] = self.room

        self.rescuer = make_char(name="Knight", room=self.room)
        self.ally = make_char(name="Wizard", room=self.room)
        self.room.players = [self.rescuer, self.ally]

        self.rescuer.state = State.COMBAT
        self.ally.state = State.COMBAT

        # Build a real CombatInstance
        self.combat = CombatInstance(self.room)
        mob = make_mob(name="Troll", vnum=6001)
        mob.combat_target = self.ally
        mob.alive = True
        self.room.mobs = [mob]

        from src.combat import CombatantState
        import random
        mob_state = CombatantState(mob, random.randint(1, 20))
        self.combat.initiative_order.append(mob_state)
        _active_combats[self.room.vnum] = self.combat

    def tearDown(self):
        from src.combat import _active_combats
        _active_combats.clear()

    def test_rescue_not_in_combat(self):
        self.rescuer.state = State.EXPLORING
        result = self.parser.cmd_rescue(self.rescuer, "Wizard")
        self.assertIn("must be in combat", result)

    def test_rescue_no_args(self):
        result = self.parser.cmd_rescue(self.rescuer, "")
        self.assertIn("rescue whom", result.lower())

    def test_rescue_target_not_in_room(self):
        result = self.parser.cmd_rescue(self.rescuer, "Barbarian")
        self.assertIn("don't see", result)

    def test_rescue_redirects_mob_target(self):
        mob = self.room.mobs[0]
        result = self.parser.cmd_rescue(self.rescuer, "Wizard")
        self.assertEqual(mob.combat_target, self.rescuer)
        self.assertIn("defense", result)

    def test_rescue_no_mobs_targeting_ally(self):
        # Make mob target someone else
        mob = self.room.mobs[0]
        mob.combat_target = self.rescuer  # already targeting rescuer
        result = self.parser.cmd_rescue(self.rescuer, "Wizard")
        self.assertIn("No enemies were targeting", result)


class TestCharacterNewFields(unittest.TestCase):
    """Tests for chosen_path, bank_gold, wimpy, hidden, sneaking round-trips."""

    def _make_data(self, **overrides):
        base = {"name": "Test", "title": "", "race": "Human", "level": 1,
                "hp": 10, "max_hp": 10, "ac": 10}
        base.update(overrides)
        return base

    def test_chosen_path_default_none(self):
        char = make_char()
        self.assertIsNone(char.chosen_path)

    def test_chosen_path_serializes(self):
        char = make_char()
        char.chosen_path = "Seer"
        d = char.to_dict()
        self.assertEqual(d["chosen_path"], "Seer")

    def test_chosen_path_deserializes(self):
        data = self._make_data(chosen_path="Keeper")
        char = Character.from_dict(data)
        self.assertEqual(char.chosen_path, "Keeper")

    def test_bank_gold_serializes(self):
        char = make_char()
        char.bank_gold = 250
        d = char.to_dict()
        self.assertEqual(d["bank_gold"], 250)

    def test_bank_gold_deserializes(self):
        data = self._make_data(bank_gold=300)
        char = Character.from_dict(data)
        self.assertEqual(char.bank_gold, 300)

    def test_wimpy_serializes_and_deserializes(self):
        char = make_char()
        char.wimpy = 20
        d = char.to_dict()
        char2 = Character.from_dict(d)
        self.assertEqual(char2.wimpy, 20)

    def test_hidden_default_false(self):
        char = make_char()
        self.assertFalse(char.hidden)

    def test_hidden_serializes(self):
        char = make_char()
        char.hidden = True
        char.hide_check = 18
        d = char.to_dict()
        self.assertTrue(d["hidden"])
        self.assertEqual(d["hide_check"], 18)

    def test_hidden_deserializes(self):
        data = self._make_data(hidden=True, hide_check=14)
        char = Character.from_dict(data)
        self.assertTrue(char.hidden)
        self.assertEqual(char.hide_check, 14)

    def test_sneaking_default_false(self):
        char = make_char()
        self.assertFalse(char.sneaking)

    def test_sneaking_serializes(self):
        char = make_char()
        char.sneaking = True
        d = char.to_dict()
        self.assertTrue(d["sneaking"])

    def test_sneaking_deserializes(self):
        data = self._make_data(sneaking=True)
        char = Character.from_dict(data)
        self.assertTrue(char.sneaking)

    def test_backward_compat_missing_new_fields(self):
        """from_dict with no new fields uses safe defaults."""
        data = self._make_data()
        char = Character.from_dict(data)
        self.assertIsNone(char.chosen_path)
        self.assertEqual(char.bank_gold, 0)
        self.assertEqual(char.wimpy, 0)
        self.assertFalse(char.hidden)
        self.assertFalse(char.sneaking)


# ===========================================================================
# Phase 2 Tests
# ===========================================================================

class TestConsumablesQuaff(unittest.TestCase):
    """Tests for cmd_quaff (System 13)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.char = make_char(hp=5, max_hp=30)

    def test_quaff_no_args(self):
        result = self.parser.cmd_quaff(self.char, "")
        self.assertIn("Quaff what", result)

    def test_quaff_item_not_in_inventory(self):
        result = self.parser.cmd_quaff(self.char, "healing")
        self.assertIn("don't have", result)

    def test_quaff_non_potion_rejected(self):
        sword = make_item(name="Iron Sword", item_type="weapon")
        self.char.inventory.append(sword)
        result = self.parser.cmd_quaff(self.char, "iron sword")
        self.assertIn("not a potion", result)

    def test_quaff_heals_character(self):
        potion = make_item(name="Potion of Healing", item_type="potion",
                           stats={"healing": 8})
        self.char.inventory.append(potion)
        result = self.parser.cmd_quaff(self.char, "potion")
        self.assertGreater(self.char.hp, 5)
        self.assertIn("healed", result)

    def test_quaff_removes_potion_from_inventory(self):
        potion = make_item(name="Potion of Healing", item_type="potion",
                           stats={"healing": 5})
        self.char.inventory.append(potion)
        self.parser.cmd_quaff(self.char, "potion")
        self.assertNotIn(potion, self.char.inventory)

    def test_quaff_cannot_exceed_max_hp(self):
        self.char.hp = 28
        potion = make_item(name="Potion of Healing", item_type="potion",
                           stats={"healing": 100})
        self.char.inventory.append(potion)
        self.parser.cmd_quaff(self.char, "potion")
        self.assertEqual(self.char.hp, self.char.max_hp)

    def test_quaff_spell_buff_applied(self):
        potion = make_item(name="Potion of Haste", item_type="potion",
                           stats={"spell": "haste", "duration": 5})
        self.char.inventory.append(potion)
        self.parser.cmd_quaff(self.char, "haste")
        self.assertIn("haste", self.char.active_buffs)


class TestConsumablesUse(unittest.TestCase):
    """Tests for cmd_use dispatch (System 13-15)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.char = make_char(hp=10, max_hp=20)

    def test_use_no_args(self):
        result = self.parser.cmd_use(self.char, "")
        self.assertIn("Use what", result)

    def test_use_item_not_found(self):
        result = self.parser.cmd_use(self.char, "widget")
        self.assertIn("don't have", result)

    def test_use_potion_dispatches_to_quaff(self):
        potion = make_item(name="Cure Light Wounds", item_type="potion",
                           stats={"healing": 5})
        self.char.inventory.append(potion)
        result = self.parser.cmd_use(self.char, "cure light wounds")
        self.assertIn("drink", result.lower())

    def test_use_wand_with_charges_succeeds(self):
        wand = make_item(name="Wand of Fire", item_type="wand",
                         stats={"class_list": ["Wizard"], "healing": 0, "damage": 0,
                                "spell": "fireball"},
                         charges=5)
        self.char.char_class = "Wizard"
        self.char.inventory.append(wand)
        result = self.parser.cmd_use(self.char, "wand")
        self.assertEqual(wand.charges, 4)
        self.assertIn("activate", result.lower())

    def test_use_wand_no_charges(self):
        wand = make_item(name="Empty Wand", item_type="wand", charges=0)
        self.char.inventory.append(wand)
        result = self.parser.cmd_use(self.char, "empty wand")
        self.assertIn("no charges", result)

    def test_use_wand_depleted_removes_from_inventory(self):
        wand = make_item(name="Last Wand", item_type="wand",
                         stats={"class_list": ["Fighter"], "spell": "bless"},
                         charges=1)
        self.char.char_class = "Fighter"
        self.char.inventory.append(wand)
        self.parser.cmd_use(self.char, "last wand")
        self.assertNotIn(wand, self.char.inventory)

    def test_use_unknown_item_type(self):
        misc = make_item(name="Rock", item_type="misc")
        self.char.inventory.append(misc)
        result = self.parser.cmd_use(self.char, "rock")
        self.assertIn("can't figure out", result)


class TestItemChargesField(unittest.TestCase):
    """Tests for Item.charges serialization."""

    def test_item_charges_none_by_default(self):
        item = make_item()
        self.assertIsNone(item.charges)

    def test_item_charges_set_in_constructor(self):
        wand = make_item(name="Wand", item_type="wand", charges=10)
        self.assertEqual(wand.charges, 10)

    def test_item_charges_in_to_dict(self):
        wand = make_item(name="Wand", item_type="wand", charges=7)
        d = wand.to_dict()
        self.assertEqual(d["charges"], 7)

    def test_item_charges_none_in_to_dict(self):
        item = make_item()
        d = item.to_dict()
        self.assertIsNone(d["charges"])

    def test_item_charges_round_trip(self):
        wand = make_item(name="Wand", item_type="wand", charges=3)
        d = wand.to_dict()
        restored = Item.from_dict(d)
        self.assertEqual(restored.charges, 3)


class TestHideSneak(unittest.TestCase):
    """Tests for cmd_hide and cmd_sneak."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(vnum=600)
        self.char = make_char(room=self.room)
        self.char.state = State.EXPLORING

    def test_hide_sets_hidden_true(self):
        import unittest.mock as mock
        with mock.patch("random.randint", return_value=15):
            self.parser.cmd_hide(self.char, "")
        self.assertTrue(self.char.hidden)

    def test_hide_sets_hide_check_value(self):
        import unittest.mock as mock
        with mock.patch("random.randint", return_value=12):
            self.parser.cmd_hide(self.char, "")
        self.assertGreater(self.char.hide_check, 0)

    def test_hide_blocked_in_combat(self):
        self.char.state = State.COMBAT
        result = self.parser.cmd_hide(self.char, "")
        self.assertIn("combat", result.lower())
        self.assertFalse(self.char.hidden)

    def test_sneak_toggle_on(self):
        self.char.sneaking = False
        result = self.parser.cmd_sneak(self.char, "")
        self.assertTrue(self.char.sneaking)
        self.assertIn("stealthily", result.lower())

    def test_sneak_toggle_off(self):
        self.char.sneaking = True
        result = self.parser.cmd_sneak(self.char, "")
        self.assertFalse(self.char.sneaking)
        self.assertIn("stop sneaking", result.lower())


class TestDoorSystem(unittest.TestCase):
    """Tests for open/close/lock/unlock/pick door commands."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(
            vnum=700,
            exits={
                "north": {
                    "room": 701,
                    "door": True,
                    "closed": True,
                    "locked": False,
                    "key_vnum": 9000,
                    "pick_dc": 20
                }
            }
        )
        self.world.rooms[700] = self.room
        self.world.rooms[701] = make_room(vnum=701)
        self.char = make_char(room=self.room)

    def _add_key(self):
        key = make_item(vnum=9000, name="Iron Key", item_type="key")
        self.char.inventory.append(key)
        return key

    def test_open_door_success(self):
        result = self.parser.cmd_open(self.char, "north")
        self.assertFalse(self.room.exits["north"]["closed"])
        self.assertIn("open", result.lower())

    def test_open_door_no_direction(self):
        result = self.parser.cmd_open(self.char, "")
        self.assertIn("direction", result.lower())

    def test_open_already_open(self):
        self.room.exits["north"]["closed"] = False
        result = self.parser.cmd_open(self.char, "north")
        self.assertIn("already open", result)

    def test_open_locked_door_fails(self):
        self.room.exits["north"]["locked"] = True
        result = self.parser.cmd_open(self.char, "north")
        self.assertIn("locked", result)

    def test_close_door_success(self):
        self.room.exits["north"]["closed"] = False
        result = self.parser.cmd_close(self.char, "north")
        self.assertTrue(self.room.exits["north"]["closed"])
        self.assertIn("close", result.lower())

    def test_close_already_closed(self):
        result = self.parser.cmd_close(self.char, "north")
        self.assertIn("already closed", result)

    def test_unlock_with_key_success(self):
        self.room.exits["north"]["locked"] = True
        self._add_key()
        result = self.parser.cmd_unlock(self.char, "north")
        self.assertFalse(self.room.exits["north"]["locked"])
        self.assertIn("unlock", result.lower())

    def test_unlock_without_key_fails(self):
        self.room.exits["north"]["locked"] = True
        result = self.parser.cmd_unlock(self.char, "north")
        self.assertIn("key", result.lower())

    def test_unlock_not_locked(self):
        result = self.parser.cmd_unlock(self.char, "north")
        self.assertIn("not locked", result)

    def test_lock_with_key_success(self):
        self.room.exits["north"]["closed"] = False
        self.room.exits["north"]["locked"] = False
        self._add_key()
        result = self.parser.cmd_lock(self.char, "north")
        self.assertTrue(self.room.exits["north"]["locked"])

    def test_lock_already_locked(self):
        self.room.exits["north"]["locked"] = True
        self._add_key()
        result = self.parser.cmd_lock(self.char, "north")
        self.assertIn("already locked", result)

    def test_pick_success(self):
        import unittest.mock as mock
        self.room.exits["north"]["locked"] = True
        # Open Lock is not trained_only — patch random to exceed DC 20
        self.char.skills["Open Lock"] = 10
        with mock.patch("random.randint", return_value=15):
            result = self.parser.cmd_pick(self.char, "north")
        self.assertFalse(self.room.exits["north"]["locked"])
        self.assertIn("pick", result.lower())

    def test_pick_fail(self):
        import unittest.mock as mock
        self.room.exits["north"]["locked"] = True
        self.char.skills["Open Lock"] = 0
        with mock.patch("random.randint", return_value=1):
            result = self.parser.cmd_pick(self.char, "north")
        self.assertTrue(self.room.exits["north"]["locked"])
        self.assertIn("fail", result.lower())

    def test_pick_not_locked(self):
        result = self.parser.cmd_pick(self.char, "north")
        self.assertIn("not locked", result)

    def test_move_blocked_by_closed_door(self):
        self.room.exits["north"]["closed"] = True
        result = self.parser.cmd_move(self.char, "north")
        self.assertIn("closed", result)

    def test_move_blocked_by_locked_door(self):
        self.room.exits["north"]["locked"] = True
        result = self.parser.cmd_move(self.char, "north")
        self.assertIn("locked", result)


class TestWeatherCommand(unittest.TestCase):
    """Tests for cmd_weather (System 19)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)

    def _char_with_weather(self, weather, flags=None):
        room = make_room(vnum=800, weather=weather, flags=flags or [])
        char = make_char(room=room)
        return char

    def test_weather_clear(self):
        char = self._char_with_weather("clear")
        result = self.parser.cmd_weather(char, "")
        self.assertIn("clear", result.lower())

    def test_weather_rain(self):
        char = self._char_with_weather("rain")
        result = self.parser.cmd_weather(char, "")
        self.assertIn("Rain", result)

    def test_weather_storm(self):
        char = self._char_with_weather("storm")
        result = self.parser.cmd_weather(char, "")
        self.assertIn("storm", result.lower())

    def test_weather_heat(self):
        char = self._char_with_weather("heat")
        result = self.parser.cmd_weather(char, "")
        self.assertIn("heat", result.lower())

    def test_weather_cold(self):
        char = self._char_with_weather("cold")
        result = self.parser.cmd_weather(char, "")
        self.assertIn("cold", result.lower())

    def test_weather_snow(self):
        char = self._char_with_weather("snow")
        result = self.parser.cmd_weather(char, "")
        self.assertIn("Snow", result)

    def test_weather_indoors_blocked(self):
        char = self._char_with_weather("rain", flags=["indoor"])
        result = self.parser.cmd_weather(char, "")
        self.assertIn("indoors", result.lower())

    def test_weather_none_shows_clear(self):
        char = self._char_with_weather(None)
        result = self.parser.cmd_weather(char, "")
        self.assertIn("clear", result.lower())


class TestMapCommand(unittest.TestCase):
    """Tests for cmd_map (System 20)."""

    def setUp(self):
        self.world = FakeWorld()
        self.parser = CommandParser(self.world)
        self.room = make_room(vnum=900, name="Central Hall",
                              exits={"north": 901, "south": 902})
        self.north_room = make_room(vnum=901, name="North Gate")
        self.south_room = make_room(vnum=902, name="South Tower")
        self.world.rooms[900] = self.room
        self.world.rooms[901] = self.north_room
        self.world.rooms[902] = self.south_room
        self.char = make_char(room=self.room)

    def test_map_renders_current_room(self):
        result = self.parser.cmd_map(self.char, "")
        # Current room is marked with asterisks
        self.assertIn("*", result)

    def test_map_shows_north_exit(self):
        result = self.parser.cmd_map(self.char, "")
        self.assertIn("North", result)

    def test_map_shows_south_exit(self):
        result = self.parser.cmd_map(self.char, "")
        self.assertIn("South", result)

    def test_map_unknown_exit_room(self):
        # Exit to a vnum not in world.rooms
        self.room.exits["east"] = 999
        result = self.parser.cmd_map(self.char, "")
        self.assertIn("?", result)

    def test_map_no_exits_still_renders(self):
        self.room.exits = {}
        result = self.parser.cmd_map(self.char, "")
        # Should render a map frame without crashing
        self.assertIsInstance(result, str)

    def test_map_with_dict_exit(self):
        """Test map handles dict-format exit (door system)."""
        self.room.exits["north"] = {"room": 901, "door": True, "closed": True}
        result = self.parser.cmd_map(self.char, "")
        self.assertIn("North", result)


if __name__ == "__main__":
    unittest.main()
