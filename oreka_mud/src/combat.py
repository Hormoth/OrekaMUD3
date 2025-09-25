import random

def attack(attacker, target):
    roll = random.randint(1, 20)
    bab = (attacker.level * 3) // 4
    if roll == 1:
        return "Miss!"
    if roll == 20 or roll + bab >= target.ac:
        damage = random.randint(1, 8) + 2
        target.hp = max(0, target.hp - damage)
        if target.hp == 0:
            target.alive = False
            return f"{attacker.name} kills {target.name}!"
        return f"{attacker.name} hits {target.name} for {damage} damage!"
    return "Miss!"
