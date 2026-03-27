"""Tests for combat maneuvers integration, corpse/loot system, and shop wiring."""

import unittest
import importlib.util
import os
import sys
import time

# Ensure the project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def import_from_path(module_name, rel_path):
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', rel_path))
    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conditions_mod = import_from_path('conditions', 'src/conditions.py')
maneuvers_mod = import_from_path('maneuvers', 'src/maneuvers.py')
items_mod = import_from_path('items', 'src/items.py')
room_mod = import_from_path('room', 'src/room.py')
combat_mod = import_from_path('combat', 'src/combat.py')


class DummyEntity:
    """Minimal entity for maneuver tests."""
    def __init__(self, name="Dummy", level=3, hp=20, ac=12):
        self.name = name
        self.level = level
        self.hp = hp
        self.max_hp = hp
        self.ac = ac
        self.alive = True
        self.conditions = set()
        self.active_conditions = {}
        self.ability_scores = {"Str": 14, "Dex": 12, "Con": 12, "Int": 10, "Wis": 10, "Cha": 10}
        self.feats = []
        self.skills = {}
        self.damage_dice = [1, 6, 2]
        self.size = "medium"
        self.attacks = [{"type": "sword", "bonus": 3, "damage": "1d6+2"}]
        self.weapon_type = "sword"
        self.aoo_count = 0
        self.power_attack_amt = 0
        self.saves = {"Fort": 3, "Ref": 2, "Will": 1}
        self.dodge_target = None

    def add_condition(self, condition):
        self.conditions.add(condition)

    def remove_condition(self, condition):
        self.conditions.discard(condition)
        self.active_conditions.pop(condition, None)

    def has_condition(self, condition):
        return condition in self.conditions or condition in self.active_conditions

    def has_feat(self, feat_name):
        for f in self.feats:
            if feat_name.lower() in f.lower():
                return True
        return False

    def get_ac(self, attacker=None, vs_aop=False):
        return self.ac

    def get_save(self, save):
        return self.saves.get(save, 0)

    def get_initiative(self):
        return 0

    def get_speed(self, mode="land"):
        return 30

    def reset_aoo(self):
        self.aoo_count = 0


# =========================================================================
# Phase 1: Conditions
# =========================================================================

class TestManeuverConditions(unittest.TestCase):
    def test_disarmed_condition_exists(self):
        cond = conditions_mod.get_condition('disarmed')
        self.assertIsNotNone(cond)
        self.assertEqual(cond.name, "Disarmed")
        self.assertEqual(cond.effects.get('attack_penalty'), 4)
        self.assertTrue(cond.effects.get('cannot_use_weapon'))

    def test_pushed_condition_exists(self):
        cond = conditions_mod.get_condition('pushed')
        self.assertIsNotNone(cond)
        self.assertEqual(cond.name, "Pushed")
        self.assertEqual(cond.effects, {})

    def test_disarmed_has_effect(self):
        entity = DummyEntity()
        entity.add_condition('disarmed')
        self.assertTrue(conditions_mod.has_effect(entity, 'cannot_use_weapon'))
        self.assertEqual(conditions_mod.calculate_condition_modifiers(entity, 'attack_penalty'), 4)


# =========================================================================
# Phase 1: Maneuvers apply conditions
# =========================================================================

class TestManeuverEffects(unittest.TestCase):
    def test_disarm_applies_condition(self):
        attacker = DummyEntity("Attacker")
        defender = DummyEntity("Defender")
        # Run disarm many times — at least one should succeed and apply 'disarmed'
        for _ in range(50):
            defender.conditions.clear()
            maneuvers_mod.disarm(attacker, defender)
            if 'disarmed' in defender.conditions:
                break
        # With 50 tries, at least one should succeed (probability very high)
        self.assertIn('disarmed', defender.conditions)

    def test_trip_applies_prone(self):
        attacker = DummyEntity("Attacker")
        defender = DummyEntity("Defender")
        for _ in range(50):
            defender.conditions.clear()
            maneuvers_mod.trip(attacker, defender)
            if 'prone' in defender.conditions:
                break
        self.assertIn('prone', defender.conditions)

    def test_grapple_applies_grappled(self):
        attacker = DummyEntity("Attacker")
        defender = DummyEntity("Defender")
        for _ in range(50):
            attacker.conditions.clear()
            defender.conditions.clear()
            maneuvers_mod.grapple(attacker, defender)
            if 'grappled' in defender.conditions:
                break
        self.assertIn('grappled', defender.conditions)
        self.assertIn('grappled', attacker.conditions)

    def test_bull_rush_applies_pushed(self):
        attacker = DummyEntity("Attacker")
        defender = DummyEntity("Defender")
        for _ in range(50):
            defender.conditions.clear()
            maneuvers_mod.bull_rush(attacker, defender)
            if 'pushed' in defender.conditions:
                break
        self.assertIn('pushed', defender.conditions)


# =========================================================================
# Phase 1: Disarmed forces unarmed damage
# =========================================================================

class TestDisarmedDamage(unittest.TestCase):
    def test_disarmed_forces_unarmed(self):
        """When disarmed (cannot_use_weapon), calculate_damage should use 1d4."""
        attacker = DummyEntity("Attacker")
        attacker.damage_dice = [2, 8, 5]  # Normally 2d8+5
        attacker.conditions.add('disarmed')
        # Run many times and check that damage never exceeds unarmed + str range
        # Unarmed: 1d4 + str_mod(2) + 0 power_attack = 3-6
        damages = []
        for _ in range(100):
            d = combat_mod.calculate_damage(attacker, is_crit=False)
            damages.append(d)
        # With unarmed 1d4+2, max damage is 6, min is 1 (clamped)
        # If weapon were used, 2d8+5+2 = min 9, so if any <= 6, disarm is working
        self.assertTrue(any(d <= 6 for d in damages), "Disarmed should produce unarmed-range damage")


# =========================================================================
# Phase 2: Corpse system
# =========================================================================

class TestCorpseSystem(unittest.TestCase):
    def test_corpse_creation(self):
        from src.items import Corpse
        corpse = Corpse("Goblin", items=[], gold=10)
        self.assertEqual(corpse.mob_name, "Goblin")
        self.assertEqual(corpse.gold, 10)
        self.assertFalse(corpse.is_empty)

    def test_corpse_empty(self):
        from src.items import Corpse
        corpse = Corpse("Goblin", items=[], gold=0)
        self.assertTrue(corpse.is_empty)

    def test_corpse_decay(self):
        from src.items import Corpse
        corpse = Corpse("Goblin", decay_time=1)
        corpse._created_at = time.time() - 2  # Created 2 seconds ago, decays in 1
        self.assertTrue(corpse.is_decayed)

    def test_corpse_not_decayed(self):
        from src.items import Corpse
        corpse = Corpse("Goblin", decay_time=300)
        corpse._created_at = time.time()
        self.assertFalse(corpse.is_decayed)

    def test_room_has_corpses_list(self):
        room = room_mod.Room(9999, "Test Room", "A test room.", {}, [])
        self.assertEqual(room.corpses, [])


# =========================================================================
# Phase 3: Shop registration
# =========================================================================

class TestShopRegistration(unittest.TestCase):
    def test_shop_commands_in_dispatch(self):
        """Verify buy/sell/list/appraise are registered in the dispatch table."""
        # We can't easily instantiate CommandParser without a world,
        # so just verify the methods exist on the class
        from src.commands import CommandParser
        self.assertTrue(hasattr(CommandParser, 'cmd_buy'))
        self.assertTrue(hasattr(CommandParser, 'cmd_sell'))
        self.assertTrue(hasattr(CommandParser, 'cmd_list'))
        self.assertTrue(hasattr(CommandParser, 'cmd_appraise'))
        self.assertTrue(hasattr(CommandParser, 'cmd_loot'))


# =========================================================================
# Phase 3: Mob restock
# =========================================================================

class TestMobRestock(unittest.TestCase):
    def test_restock_restores_inventory(self):
        from src.mob import Mob
        mob = Mob(
            vnum=9999, name="Test Shop", level=1,
            hp_dice=[1, 6, 0], ac=10, damage_dice=[1, 4, 0],
            shop_inventory=[1, 2, 3], shop_type="general"
        )
        self.assertEqual(mob.shop_inventory, [1, 2, 3])
        self.assertEqual(mob.base_shop_inventory, [1, 2, 3])
        # Remove an item
        mob.remove_shop_item(2)
        self.assertEqual(mob.shop_inventory, [1, 3])
        # Restock
        mob.restock_shop()
        self.assertEqual(mob.shop_inventory, [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
