import random

class Mob:
    def __init__(self, vnum, name, level, hp_dice, ac, damage_dice, flags=None):
        self.vnum = vnum
        self.name = name
        self.level = level
        self.hp = sum(random.randint(1, hp_dice[1]) for _ in range(hp_dice[0])) + hp_dice[2]
        self.max_hp = self.hp
        self.ac = ac
        self.damage_dice = damage_dice
        self.flags = flags or []
        self.alive = True

    def attack(self, target):
        roll = random.randint(1, 20)
        bab = (self.level * 3) // 4
        if roll == 1:
            return "Miss!"
        if roll == 20 or roll + bab >= target.ac:
            damage = sum(random.randint(1, self.damage_dice[1]) for _ in range(self.damage_dice[0])) + self.damage_dice[2]
            target.hp = max(0, target.hp - damage)
            if target.hp == 0:
                target.alive = False
                return f"{self.name} kills {target.name}!"
            return f"{self.name} hits {target.name} for {damage} damage!"
        return "Miss!"
