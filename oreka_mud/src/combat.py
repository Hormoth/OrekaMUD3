import random

def attack(attacker, target, power_attack_amt=0):
    # Use attack method from Mob or Character, which now applies all feat logic
    if hasattr(attacker, 'attack'):
        return attacker.attack(target, power_attack_amt=power_attack_amt)
    # fallback: old logic
    roll = random.randint(1, 20)
    bab = (attacker.level * 3) // 4
    if roll == 1:
        return "Miss!"
    if roll == 20 or roll + bab >= getattr(target, 'ac', 10):
        damage = random.randint(1, 8) + 2
        target.hp = max(0, target.hp - damage)
        if target.hp == 0:
            target.alive = False
            return f"{attacker.name} kills {target.name}!"
        return f"{attacker.name} hits {target.name} for {damage} damage!"
    return "Miss!"
