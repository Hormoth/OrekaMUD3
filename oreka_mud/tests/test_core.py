
import unittest
import importlib.util
import os

def import_from_path(module_name, rel_path):
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', rel_path))
    spec = importlib.util.spec_from_file_location(module_name, abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


character_mod = import_from_path('character', 'src/character.py')
combat_mod = import_from_path('combat', 'src/combat.py')
feats_mod = import_from_path('feats', 'src/feats.py')
spells_mod = import_from_path('spells', 'src/spells.py')
world_mod = import_from_path('world', 'src/world.py')

Character = character_mod.Character
attack = combat_mod.attack
Feat = feats_mod.Feat
meets_prereq = feats_mod.meets_prereq
DOMAIN_DATA = spells_mod.DOMAIN_DATA
OrekaWorld = world_mod.OrekaWorld

class TestCharacter(unittest.TestCase):
    def test_character_creation(self):
        c = Character('Test', 'Hero', 'Human', 1, 10, 10, 10, None)
        self.assertEqual(c.name, 'Test')
        self.assertEqual(c.level, 1)
        self.assertEqual(c.hp, 10)
        self.assertFalse(c.is_immortal)

class TestCombat(unittest.TestCase):
    class Dummy:
        def __init__(self):
            self.level = 1
            self.ac = 10
            self.hp = 10
            self.alive = True
    def test_attack(self):
        attacker = self.Dummy()
        target = self.Dummy()
        result = attack(attacker, target)
        self.assertIn(result, ["Miss!", None])

class TestFeats(unittest.TestCase):
    def test_meets_prereq_level(self):
        c = Character('Test', 'Hero', 'Human', 5, 10, 10, 10, None)
        self.assertTrue(meets_prereq(c, {'level': 3}))
        self.assertFalse(meets_prereq(c, {'level': 10}))

class TestSpells(unittest.TestCase):
    def test_domain_data(self):
        self.assertIn('Air', DOMAIN_DATA)
        self.assertIn(1, DOMAIN_DATA['Air']['spells'])

class TestWorld(unittest.TestCase):
    def test_world_init(self):
        w = OrekaWorld()
        self.assertIsInstance(w.rooms, dict)
        self.assertIsInstance(w.mobs, dict)
        self.assertIsInstance(w.players, list)

if __name__ == '__main__':
    unittest.main()
