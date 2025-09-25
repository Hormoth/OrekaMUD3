from enum import Enum
from src.combat import attack

class State(Enum):
    EXPLORING = 1
    COMBAT = 2

class Character:
    def __init__(self, name, title, race, level, hp, max_hp, ac, room, is_immortal=False, elemental_affinity=None,
                 str_score=10, dex_score=10, con_score=10, int_score=10, wis_score=10, cha_score=10,
                 mana=100, max_mana=100, move=100, max_move=100):
        self.name = name
        self.title = title
        self.race = race
        self.level = level
        self.hp = hp
        self.max_hp = max_hp
        self.ac = ac
        self.room = room
        self.quests = []
        self.state = State.EXPLORING
        self.is_ai = False
        self.is_immortal = is_immortal
        self.elemental_affinity = elemental_affinity
        self.str_score = str_score
        self.dex_score = dex_score
        self.con_score = con_score
        self.int_score = int_score
        self.wis_score = wis_score
        self.cha_score = cha_score
        self.mana = mana
        self.max_mana = max_mana
        self.move = move
        self.max_move = max_move
        self.xp = 0  # Current experience points
        self.show_all = False
        self.prompt = "%n%s (%RACE): AC %a HP %h/%H EXP %x>" if is_immortal else "%n%s: AC %a HP %h/%H EXP %x>"
        self.full_prompt = "%n%s (%RACE): AC %a HP %h/%H EXP %x Mana %m/%M Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>" if is_immortal else "%n%s: AC %a HP %h/%H EXP %x Mana %m/%M Move %v/%V Str %s Dex %d Con %c Int %i Wis %w Cha %c%s>"

    def get_prompt(self):
        title_str = f" {self.title}" if self.title else ""
        str_mod = (self.str_score - 10) // 2
        dex_mod = (self.dex_score - 10) // 2
        con_mod = (self.con_score - 10) // 2
        int_mod = (self.int_score - 10) // 2
        wis_mod = (self.wis_score - 10) // 2
        cha_mod = (self.cha_score - 10) // 2
        xp_to_next = max(0, {1: 1000, 2: 3000, 3: 6000, 4: 10000, 5: 15000, 6: 21000, 7: 28000, 60: 0}.get(self.level + 1, 0) - self.xp)
        if self.show_all:
            return self.full_prompt.replace("%n", self.name).replace("%s", title_str).replace("%a", str(self.ac)).replace("%h", str(self.hp)).replace("%H", str(self.max_hp)).replace("%x", str(xp_to_next)).replace("%m", str(self.mana)).replace("%M", str(self.max_mana)).replace("%v", str(self.move)).replace("%V", str(self.max_move)).replace("%s", f"{self.str_score} ({str_mod:+})").replace("%d", f"{self.dex_score} ({dex_mod:+})").replace("%c", f"{self.con_score} ({con_mod:+})").replace("%i", f"{self.int_score} ({int_mod:+})").replace("%w", f"{self.wis_score} ({wis_mod:+})").replace("%c", f"{self.cha_score} ({cha_mod:+})").replace("%RACE", self.race or "Unknown").replace("%s", " [Immortal]" if self.is_immortal else "")
        return self.prompt.replace("%n", self.name).replace("%s", title_str).replace("%a", str(self.ac)).replace("%h", str(self.hp)).replace("%H", str(self.max_hp)).replace("%x", str(xp_to_next)).replace("%RACE", self.race or "Unknown").replace("%s", " [Immortal]" if self.is_immortal else "")
    
    def toggle_stats(self):
        self.show_all = not self.show_all
        return f"Stats display {'enabled' if self.show_all else 'disabled'}.\n{self.get_prompt()}"

    async def ai_decide(self, world):
        if self.state == State.COMBAT:
            for mob in self.room.mobs:
                if mob.alive and self.hp > self.max_hp * 0.2:
                    return attack(self, mob)
                elif self.hp <= self.max_hp * 0.2:
                    self.state = State.EXPLORING
                    return "You flee from combat!"
        if self.quests and self.room.vnum == self.quests[0]["location"]:
            self.quests.clear()
            self.xp += 1000
            return "Quest completed: Starweave Ritual! +1000 XP"
        return self.get_prompt()
