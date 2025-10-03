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
        # Apply Damage Reduction (DR) if present
        dr = getattr(target, 'damage_reduction', 0)
        if dr > 0:
            damage = max(0, damage - dr)
        target.hp = max(0, target.hp - damage)
        if target.hp == 0:
            target.alive = False
            # Award XP if attacker is a player and target is a monster with CR
            xp_award = 0
            cr = getattr(target, 'cr', None)
            loot_msg = ""
            # --- D&D 3.5 Generic Loot Table (simplified) ---
            # By CR: (gp, chance for item)
            loot_table = [
                # (min_cr, max_cr, gold_dice, item_chance, item_type)
                (0, 1, (1, 6, 0), 0.05, 'mundane'),
                (2, 4, (2, 8, 0), 0.10, 'mundane'),
                (5, 10, (4, 10, 0), 0.20, 'minor_magic'),
                (11, 16, (8, 10, 0), 0.30, 'medium_magic'),
                (17, 100, (12, 10, 0), 0.50, 'major_magic'),
            ]
            # Try to parse CR as float
            try:
                cr_val = float(cr)
            except Exception:
                cr_val = 0
            # Find loot tier
            for min_cr, max_cr, gold_dice, item_chance, item_type in loot_table:
                if min_cr <= cr_val <= max_cr:
                    # Gold drop
                    gold = sum(random.randint(1, gold_dice[1]) for _ in range(gold_dice[0])) + gold_dice[2]
                    loot_msg += f"\nLoot: {gold} gp."
                    # Item drop
                    if random.random() < item_chance:
                        from oreka_mud.src import items as itemdb
                        # Determine item type for drop
                        if item_type == 'mundane':
                            item = itemdb.get_random_item(magical=False)
                        elif item_type == 'minor_magic' or item_type == 'medium_magic' or item_type == 'major_magic':
                            item = itemdb.get_random_item(magical=True)
                        else:
                            item = itemdb.get_random_item()
                        if item:
                            if hasattr(target, 'room') and target.room:
                                target.room.items.append(item)
                                loot_msg += f" {item.name} drops to the ground!"
                    break
            if cr is not None and hasattr(attacker, 'xp'):
                # D&D 3.5 XP table for 1 character (party of 1)
                xp_table = {
                    -4: 75, -3: 100, -2: 150, -1: 200, 0: 300, 1: 450, 2: 600, 3: 900, 4: 1200
                }
                level = getattr(attacker, 'level', 1)
                diff = int(round(cr_val - level))
                if diff < -4:
                    diff = -4
                if diff > 4:
                    diff = 4
                xp_award = xp_table.get(diff, 0)
                attacker.xp = getattr(attacker, 'xp', 0) + xp_award
                if hasattr(attacker, 'save'):
                    attacker.save()
                return f"{attacker.name} kills {target.name}! You gain {xp_award} XP.{loot_msg}"
            return f"{attacker.name} kills {target.name}!{loot_msg}"
        return f"{attacker.name} hits {target.name} for {damage} damage!"
    return "Miss!"
