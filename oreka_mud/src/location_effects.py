"""
Location Effects System for OrekaMUD3.
Handles room-based environmental mechanics: Kin-sense modifiers, elemental resonance,
environmental hazards, rune-circles, and sanctuaries.
"""
import random
import time


class LocationEffectsManager:
    """Processes room effects on player entry, exit, and periodic ticks."""

    def __init__(self):
        self.hazard_timers = {}  # {(player_name, room_vnum): last_tick_time}

    def on_room_enter(self, character, room):
        """Called when a player enters a room. Returns list of messages to show."""
        effects = getattr(room, 'effects', None) or []
        messages = []

        for effect in effects:
            etype = effect.get("type", "")

            if etype == "kin_sense_modifier":
                msg = self._handle_kin_sense_enter(character, effect)
                if msg:
                    messages.append(msg)

            elif etype == "elemental_resonance":
                msg = self._handle_resonance_enter(character, effect)
                if msg:
                    messages.append(msg)

            elif etype == "hazard":
                msg = self._handle_hazard_enter(character, effect, room)
                if msg:
                    messages.append(msg)

            elif etype == "rune_circle":
                msg = self._handle_rune_circle_enter(character, effect)
                if msg:
                    messages.append(msg)

            elif etype == "sanctuary":
                msg = self._handle_sanctuary_enter(character, effect)
                if msg:
                    messages.append(msg)

        return messages

    def on_room_exit(self, character, room):
        """Called when player leaves a room. Clean up timers."""
        key = (character.name, room.vnum)
        self.hazard_timers.pop(key, None)

    # === KIN-SENSE MODIFIERS ===

    def _handle_kin_sense_enter(self, character, effect):
        mode = effect.get("mode", "normal")
        msg = effect.get("message", "")

        if mode == "dead":
            return f"\033[1;35m[Kin-Sense] {msg or 'Your Kin-sense goes utterly silent. The resonance is dead here.'}\033[0m"
        elif mode == "flickering":
            return f"\033[0;35m[Kin-Sense] {msg or 'Your Kin-sense flickers unreliably, like a candle in wind.'}\033[0m"
        elif mode == "amplified":
            return f"\033[1;36m[Kin-Sense] {msg or 'Your Kin-sense sharpens. Every presence rings clear.'}\033[0m"
        elif mode == "suppressed":
            return f"\033[0;33m[Kin-Sense] {msg or 'Your Kin-sense feels muffled, as if heard through thick stone.'}\033[0m"
        return None

    def get_kin_sense_modifier(self, room):
        """Returns (mode, dc) for Kin-sense checks in this room.
        Called by kin_sense.py before detection rolls.
        Returns: ('normal', 0) | ('dead', 0) | ('flickering', dc) | ('amplified', 0) | ('suppressed', 0)
        """
        effects = getattr(room, 'effects', None) or []
        for effect in effects:
            if effect.get("type") == "kin_sense_modifier":
                mode = effect.get("mode", "normal")
                dc = effect.get("dc", 0)
                return (mode, dc)

        # Also check room flags for legacy support
        flags = getattr(room, 'flags', [])
        if 'kin_sense_dead' in flags or 'false_silence' in flags:
            return ('dead', 0)

        return ('normal', 0)

    # === ELEMENTAL RESONANCE ===

    def _handle_resonance_enter(self, character, effect):
        element = effect.get("element", "")
        bonus = effect.get("bonus", 0)
        msg = effect.get("message", "")

        if msg:
            return f"\033[0;36m{msg}\033[0m"

        element_feel = {
            "fire": "heat radiating from the stone",
            "water": "cool moisture in the air",
            "earth": "a deep, grounded vibration",
            "wind": "a constant gentle breeze"
        }
        feel = element_feel.get(element, f"{element} energy")
        return f"\033[0;36mYou sense {feel}. The {element} element is strong here.\033[0m"

    def get_elemental_resonance(self, room):
        """Returns (element, bonus) for spell casting in this room.
        Called by spells.py during casting.
        Returns: (None, 0) or ('fire', 2) etc.
        """
        effects = getattr(room, 'effects', None) or []
        for effect in effects:
            if effect.get("type") == "elemental_resonance":
                return (effect.get("element"), effect.get("bonus", 1))
        return (None, 0)

    # === ENVIRONMENTAL HAZARDS ===

    def _handle_hazard_enter(self, character, effect, room):
        msg = effect.get("message", "You feel the environment pressing against you.")
        return f"\033[1;31m[Warning] {msg}\033[0m"

    def tick_hazards(self, world):
        """Called periodically. Process hazard damage for players in hazard rooms.
        Returns list of (player, message) tuples."""
        notifications = []
        now = time.time()

        for player in world.players:
            if not hasattr(player, 'room') or not player.room:
                continue

            effects = getattr(player.room, 'effects', None) or []
            for effect in effects:
                if effect.get("type") != "hazard":
                    continue

                interval = effect.get("interval", 300)
                key = (player.name, player.room.vnum)
                last_tick = self.hazard_timers.get(key, 0)

                if now - last_tick < interval:
                    continue

                self.hazard_timers[key] = now

                # Make save
                save_type = effect.get("save", "fort")
                dc = effect.get("dc", 14)
                damage_str = effect.get("damage", "1d6")
                damage_type = effect.get("damage_type", "fire")
                resist_element = effect.get("resist_element", damage_type)

                # Calculate save bonus
                save_mod = 0
                if save_type == "fort":
                    save_mod = getattr(player, 'fort_save', 0) or (getattr(player, 'con_score', 10) - 10) // 2
                elif save_type == "reflex":
                    save_mod = getattr(player, 'ref_save', 0) or (getattr(player, 'dex_score', 10) - 10) // 2
                elif save_type == "will":
                    save_mod = getattr(player, 'will_save', 0) or (getattr(player, 'wis_score', 10) - 10) // 2

                roll = random.randint(1, 20) + save_mod

                if roll >= dc:
                    msg = f"\033[0;33m[Hazard] You endure the {damage_type} hazard. (Save: {roll} vs DC {dc})\033[0m"
                    notifications.append((player, msg))
                else:
                    # Roll damage
                    damage = self._roll_dice(damage_str)

                    # Check resistance
                    elem_affinity = getattr(player, 'elemental_affinity', '')
                    if elem_affinity and resist_element:
                        # Matching elemental affinity grants natural resistance
                        element_map = {"earth": "acid", "fire": "fire", "water": "cold", "wind": "electricity"}
                        if element_map.get(elem_affinity) == damage_type:
                            damage = max(0, damage - 5)

                    # Check divine buffs for resistance
                    divine = getattr(player, 'divine_buffs', {})
                    resist = divine.get('resist', {})
                    if damage_type in resist:
                        damage = max(0, damage - resist[damage_type])

                    if damage > 0 and hasattr(player, 'hp'):
                        player.hp -= damage
                        msg = f"\033[1;31m[Hazard] The {damage_type} hazard burns you for {damage} damage! (Save: {roll} vs DC {dc})\033[0m"
                    else:
                        msg = f"\033[0;33m[Hazard] Your resistance absorbs the {damage_type} hazard.\033[0m"
                    notifications.append((player, msg))

        return notifications

    # === RUNE CIRCLES ===

    def _handle_rune_circle_enter(self, character, effect):
        state = effect.get("state", "dormant")
        attunement = effect.get("attunement", "unknown")

        state_desc = {
            "active": "pulses with warm amber light",
            "dormant": "lies dim and silent, its runes barely visible",
            "damaged": "flickers erratically, cracked stone leaking residual energy",
            "sealed": "is dark and cold, deliberately sealed by ancient hands"
        }
        desc = state_desc.get(state, "hums with faint energy")
        return f"\033[1;33mA Giant-era rune-circle {desc}. ({attunement.title()} attunement)\033[0m"

    def interact_rune_circle(self, character, room, action="study"):
        """Handle study/activate/repair commands on rune-circles.
        Returns message string."""
        effects = getattr(room, 'effects', None) or []
        circle = None
        for e in effects:
            if e.get("type") == "rune_circle":
                circle = e
                break

        if not circle:
            return "There is no rune-circle here."

        state = circle.get("state", "dormant")
        attunement = circle.get("attunement", "unknown")
        study_dc = circle.get("study_dc", 20)
        activate_dc = circle.get("activate_dc", 15)
        power = circle.get("power", "unknown")

        if action == "study":
            # Knowledge Arcana check
            skill_mod = 0
            skills = getattr(character, 'skills', {})
            if isinstance(skills, dict):
                skill_mod = skills.get('Knowledge (arcana)', skills.get('knowledge_arcana', 0))
            int_mod = (getattr(character, 'int_score', 10) - 10) // 2
            roll = random.randint(1, 20) + skill_mod + int_mod

            if roll >= study_dc:
                lines = [f"\033[1;33mYou study the rune-circle carefully.\033[0m"]
                lines.append(f"  State: {state.title()}")
                lines.append(f"  Attunement: {attunement.title()} element")
                lines.append(f"  Power: {power.replace('_', ' ').title()}")
                if state == "active":
                    lines.append(f"  \033[0;32mThis circle is functional and can be activated.\033[0m")
                elif state == "damaged":
                    lines.append(f"  \033[0;31mThis circle is damaged but could be repaired.\033[0m")
                elif state == "sealed":
                    lines.append(f"  \033[0;31mThis circle has been deliberately sealed. Breaking the seal would be... unwise.\033[0m")
                return "\n".join(lines)
            else:
                return f"You study the rune-circle but cannot decipher its purpose. (Check: {roll} vs DC {study_dc})"

        elif action == "activate":
            if state == "dormant" or state == "damaged":
                return f"The rune-circle is {state}. It cannot be activated in this state."
            if state == "sealed":
                return "The circle is sealed. Something powerful holds it shut."

            # Use Magic Device or matching affinity check
            affinity = getattr(character, 'elemental_affinity', '')
            bonus = 4 if affinity == attunement else 0
            cha_mod = (getattr(character, 'cha_score', 10) - 10) // 2
            roll = random.randint(1, 20) + cha_mod + bonus

            if roll >= activate_dc:
                result = self._activate_rune_circle(character, circle, room)
                return result
            else:
                return f"You reach for the circle's power but cannot grasp it. (Check: {roll} vs DC {activate_dc})"

        elif action == "repair":
            if state != "damaged":
                return f"The rune-circle is {state} — {'it does not need repair' if state == 'active' else 'it cannot be repaired in this state'}."

            # Craft check
            skill_mod = 0
            skills = getattr(character, 'skills', {})
            if isinstance(skills, dict):
                skill_mod = skills.get('Craft (stonemasonry)', skills.get('craft_stonemasonry', 0))
            int_mod = (getattr(character, 'int_score', 10) - 10) // 2
            roll = random.randint(1, 20) + skill_mod + int_mod
            repair_dc = study_dc + 5  # Harder than studying

            if roll >= repair_dc:
                circle["state"] = "active"
                return f"\033[1;32mYou carefully mend the cracked runes. The circle flares to life, amber light pulsing steadily!\033[0m"
            else:
                return f"Your repair attempt fails. The runes resist your efforts. (Check: {roll} vs DC {repair_dc})"

        return "Usage: study | activate | repair"

    def _activate_rune_circle(self, character, circle, room):
        """Process rune-circle activation based on its power type."""
        power = circle.get("power", "unknown")
        attunement = circle.get("attunement", "unknown")

        if power == "heal":
            heal = random.randint(10, 30)
            if hasattr(character, 'hp') and hasattr(character, 'max_hp'):
                actual = min(heal, character.max_hp - character.hp)
                character.hp = min(character.hp + heal, character.max_hp)
                return f"\033[1;32mThe rune-circle pulses. Warm {attunement} energy flows through you, healing {actual} HP!\033[0m"

        elif power == "amplify":
            # Grant temporary elemental bonus
            if not hasattr(character, 'divine_buffs'):
                character.divine_buffs = {}
            element_energy = {"earth": "acid", "fire": "fire", "water": "cold", "wind": "electricity"}
            energy = element_energy.get(attunement, "force")
            character.divine_buffs = {
                "deity": f"Rune-Circle ({attunement.title()})",
                "stat_bonus": {},
                "duration": 50,
                "resist": {energy: 10}
            }
            return f"\033[1;36mThe rune-circle blazes! {attunement.title()} energy saturates you. Resistance to {energy} granted for 50 rounds!\033[0m"

        elif power == "ward":
            return f"\033[1;33mThe rune-circle activates a ward. A shimmering barrier of {attunement} energy surrounds the area.\033[0m"

        elif power == "teleport":
            # List connected rune-circles (future: actual teleportation)
            return f"\033[1;35mThe rune-circle hums with teleportation energy. You sense distant circles connected to this one.\033[0m\n  (Windstone teleportation network — use 'activate' at any active Windstone to travel.)"

        elif power == "weather":
            return f"\033[1;36mThe rune-circle stabilizes the weather around it. Winds calm, clouds part, the air steadies.\033[0m"

        return f"\033[1;33mThe rune-circle activates with a pulse of {attunement} light, but you're unsure of its effect.\033[0m"

    # === SANCTUARY ===

    def _handle_sanctuary_enter(self, character, effect):
        deity = effect.get("deity", "")
        msg = effect.get("message", "")
        if msg:
            return f"\033[0;33m{msg}\033[0m"
        if deity:
            return f"\033[0;33mYou feel the presence of {deity} in this sacred place.\033[0m"
        return f"\033[0;33mThis is hallowed ground. Rest comes easier here.\033[0m"

    def get_sanctuary_bonus(self, room, character=None):
        """Returns (healing_bonus, rest_multiplier) for resting in this room."""
        effects = getattr(room, 'effects', None) or []
        for effect in effects:
            if effect.get("type") == "sanctuary":
                hb = effect.get("healing_bonus", 0)
                rm = effect.get("rest_multiplier", 1.0)
                deity = effect.get("deity", "")
                # Bonus if character worships this deity
                if character and deity and hasattr(character, 'deity'):
                    if character.deity and deity.lower() in character.deity.lower():
                        hb += 2
                        rm += 0.5
                return (hb, rm)
        return (0, 1.0)

    # === UTILITY ===

    def _roll_dice(self, dice_str):
        import re
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', str(dice_str))
        if not match:
            return 0
        num = int(match.group(1))
        size = int(match.group(2))
        bonus = int(match.group(3) or 0)
        return max(0, sum(random.randint(1, size) for _ in range(num)) + bonus)


# Singleton
_location_effects = None

def get_location_effects():
    global _location_effects
    if _location_effects is None:
        _location_effects = LocationEffectsManager()
    return _location_effects
