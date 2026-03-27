from src.combat import attack
from src.character import State
from src import quests
from src.spawning import get_spawn_manager
from src.schedules import get_game_time, get_schedule_manager, ActivityType

VALID_RACES = [
    # True Kin (Elemental Framework)
    "Half-Giant",
    "Hasura Elf", "Kovaka Elf", "Pasua Elf", "Na'wasua Elf",
    "Visetri Dwarf", "Pekakarlik Dwarf", "Rarozhki Dwarf",
    "Halfling",
    "Orean Human", "Taraf-Imro Human", "Eruskan Human", "Mytroan Human",
    # Outsider-origin (possible via Farborn or Domnathar crossing)
    "Half-Domnathar", "Farborn Human",
    # Silentborn (Kin + Deceiver heritage)
    "Silentborn",
]
VALID_CLASSES = ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Magi", "Monk",
                 "Paladin", "Ranger", "Rogue", "Sorcerer", "Wizard"]
VALID_ALIGNMENTS = ["Lawful Good", "Neutral Good", "Chaotic Good",
                    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
                    "Lawful Evil", "Neutral Evil", "Chaotic Evil"]
VALID_AFFINITIES = ["Air", "Earth", "Fire", "Water"]
VALID_LIGHT_LEVELS = ["bright", "normal", "dim", "dark", "magical"]
VALID_DAMAGE_TYPES = ["fire", "cold", "acid", "electricity", "sonic", "force", "negative", "positive"]


def _resolve_exit(exit_data):
    """Return the integer vnum from an exit that may be int or dict format."""
    if isinstance(exit_data, dict):
        return exit_data["room"]
    return exit_data


SOCIALS = {
    "bow": {
        "self_no_target": "You bow gracefully.",
        "room_no_target": "{name} bows gracefully.",
        "self_targeted": "You bow before {target}.",
        "room_targeted": "{name} bows before {target}.",
        "victim": "{name} bows before you.",
    },
    "wave": {
        "self_no_target": "You wave cheerfully.",
        "room_no_target": "{name} waves cheerfully.",
        "self_targeted": "You wave at {target}.",
        "room_targeted": "{name} waves at {target}.",
        "victim": "{name} waves at you.",
    },
    "laugh": {
        "self_no_target": "You laugh out loud.",
        "room_no_target": "{name} laughs out loud.",
        "self_targeted": "You laugh at {target}.",
        "room_targeted": "{name} laughs at {target}.",
        "victim": "{name} laughs at you.",
    },
    "cry": {
        "self_no_target": "You burst into tears.",
        "room_no_target": "{name} bursts into tears.",
        "self_targeted": "You cry on {target}'s shoulder.",
        "room_targeted": "{name} cries on {target}'s shoulder.",
        "victim": "{name} cries on your shoulder.",
    },
    "nod": {
        "self_no_target": "You nod solemnly.",
        "room_no_target": "{name} nods solemnly.",
        "self_targeted": "You nod at {target}.",
        "room_targeted": "{name} nods at {target}.",
        "victim": "{name} nods at you.",
    },
    "shrug": {
        "self_no_target": "You shrug indifferently.",
        "room_no_target": "{name} shrugs indifferently.",
        "self_targeted": "You shrug at {target}.",
        "room_targeted": "{name} shrugs at {target}.",
        "victim": "{name} shrugs at you.",
    },
    "grin": {
        "self_no_target": "You grin wickedly.",
        "room_no_target": "{name} grins wickedly.",
        "self_targeted": "You grin at {target}.",
        "room_targeted": "{name} grins at {target}.",
        "victim": "{name} grins at you.",
    },
    "wink": {
        "self_no_target": "You wink suggestively.",
        "room_no_target": "{name} winks suggestively.",
        "self_targeted": "You wink at {target}.",
        "room_targeted": "{name} winks at {target}.",
        "victim": "{name} winks at you.",
    },
    "hug": {
        "self_no_target": "You hug yourself for comfort.",
        "room_no_target": "{name} hugs themselves for comfort.",
        "self_targeted": "You hug {target} warmly.",
        "room_targeted": "{name} hugs {target} warmly.",
        "victim": "{name} hugs you warmly.",
    },
    "poke": {
        "self_no_target": "You poke yourself in the eye.",
        "room_no_target": "{name} pokes themselves in the eye.",
        "self_targeted": "You poke {target} in the ribs.",
        "room_targeted": "{name} pokes {target} in the ribs.",
        "victim": "{name} pokes you in the ribs.",
    },
    "slap": {
        "self_no_target": "You slap your forehead.",
        "room_no_target": "{name} slaps their forehead.",
        "self_targeted": "You slap {target} across the face.",
        "room_targeted": "{name} slaps {target} across the face.",
        "victim": "{name} slaps you across the face.",
    },
    "dance": {
        "self_no_target": "You break into a wild dance.",
        "room_no_target": "{name} breaks into a wild dance.",
        "self_targeted": "You dance with {target}.",
        "room_targeted": "{name} dances with {target}.",
        "victim": "{name} dances with you.",
    },
    "cheer": {
        "self_no_target": "You cheer enthusiastically.",
        "room_no_target": "{name} cheers enthusiastically.",
        "self_targeted": "You cheer for {target}.",
        "room_targeted": "{name} cheers for {target}.",
        "victim": "{name} cheers for you.",
    },
    "clap": {
        "self_no_target": "You clap your hands together.",
        "room_no_target": "{name} claps their hands together.",
        "self_targeted": "You clap for {target}.",
        "room_targeted": "{name} claps for {target}.",
        "victim": "{name} claps for you.",
    },
    "sigh": {
        "self_no_target": "You sigh deeply.",
        "room_no_target": "{name} sighs deeply.",
        "self_targeted": "You sigh at {target}.",
        "room_targeted": "{name} sighs at {target}.",
        "victim": "{name} sighs at you.",
    },
    "groan": {
        "self_no_target": "You groan miserably.",
        "room_no_target": "{name} groans miserably.",
        "self_targeted": "You groan at {target}.",
        "room_targeted": "{name} groans at {target}.",
        "victim": "{name} groans at you.",
    },
    "yawn": {
        "self_no_target": "You yawn tiredly.",
        "room_no_target": "{name} yawns tiredly.",
        "self_targeted": "You yawn in {target}'s face.",
        "room_targeted": "{name} yawns in {target}'s face.",
        "victim": "{name} yawns in your face.",
    },
    "cough": {
        "self_no_target": "You cough loudly.",
        "room_no_target": "{name} coughs loudly.",
        "self_targeted": "You cough at {target}.",
        "room_targeted": "{name} coughs at {target}.",
        "victim": "{name} coughs at you.",
    },
    "whistle": {
        "self_no_target": "You whistle a tune.",
        "room_no_target": "{name} whistles a tune.",
        "self_targeted": "You whistle at {target}.",
        "room_targeted": "{name} whistles at {target}.",
        "victim": "{name} whistles at you.",
    },
    "flex": {
        "self_no_target": "You flex your muscles impressively.",
        "room_no_target": "{name} flexes their muscles impressively.",
        "self_targeted": "You flex your muscles at {target}.",
        "room_targeted": "{name} flexes their muscles at {target}.",
        "victim": "{name} flexes their muscles at you.",
    },
    "curtsey": {
        "self_no_target": "You curtsey gracefully.",
        "room_no_target": "{name} curtseys gracefully.",
        "self_targeted": "You curtsey before {target}.",
        "room_targeted": "{name} curtseys before {target}.",
        "victim": "{name} curtseys before you.",
    },
    "salute": {
        "self_no_target": "You salute sharply.",
        "room_no_target": "{name} salutes sharply.",
        "self_targeted": "You salute {target}.",
        "room_targeted": "{name} salutes {target}.",
        "victim": "{name} salutes you.",
    },
    "pat": {
        "self_no_target": "You pat yourself on the back.",
        "room_no_target": "{name} pats themselves on the back.",
        "self_targeted": "You pat {target} on the head.",
        "room_targeted": "{name} pats {target} on the head.",
        "victim": "{name} pats you on the head.",
    },
    "tickle": {
        "self_no_target": "You tickle yourself.",
        "room_no_target": "{name} tickles themselves.",
        "self_targeted": "You tickle {target} mercilessly.",
        "room_targeted": "{name} tickles {target} mercilessly.",
        "victim": "{name} tickles you mercilessly.",
    },
    "comfort": {
        "self_no_target": "You look around for someone to comfort.",
        "room_no_target": "{name} looks around for someone to comfort.",
        "self_targeted": "You comfort {target} gently.",
        "room_targeted": "{name} comforts {target} gently.",
        "victim": "{name} comforts you gently.",
    },
    "thank": {
        "self_no_target": "You thank everyone around you.",
        "room_no_target": "{name} thanks everyone around them.",
        "self_targeted": "You thank {target} sincerely.",
        "room_targeted": "{name} thanks {target} sincerely.",
        "victim": "{name} thanks you sincerely.",
    },
    "apologize": {
        "self_no_target": "You apologize to no one in particular.",
        "room_no_target": "{name} apologizes to no one in particular.",
        "self_targeted": "You apologize to {target}.",
        "room_targeted": "{name} apologizes to {target}.",
        "victim": "{name} apologizes to you.",
    },
    "agree": {
        "self_no_target": "You nod in agreement.",
        "room_no_target": "{name} nods in agreement.",
        "self_targeted": "You agree with {target}.",
        "room_targeted": "{name} agrees with {target}.",
        "victim": "{name} agrees with you.",
    },
    "disagree": {
        "self_no_target": "You shake your head in disagreement.",
        "room_no_target": "{name} shakes their head in disagreement.",
        "self_targeted": "You disagree with {target}.",
        "room_targeted": "{name} disagrees with {target}.",
        "victim": "{name} disagrees with you.",
    },
    "shiver": {
        "self_no_target": "You shiver with cold.",
        "room_no_target": "{name} shivers with cold.",
        "self_targeted": "You shiver next to {target}.",
        "room_targeted": "{name} shivers next to {target}.",
        "victim": "{name} shivers next to you.",
    },
    "growl": {
        "self_no_target": "You growl menacingly.",
        "room_no_target": "{name} growls menacingly.",
        "self_targeted": "You growl at {target}.",
        "room_targeted": "{name} growls at {target}.",
        "victim": "{name} growls at you.",
    },
    "snicker": {
        "self_no_target": "You snicker under your breath.",
        "room_no_target": "{name} snickers under their breath.",
        "self_targeted": "You snicker at {target}.",
        "room_targeted": "{name} snickers at {target}.",
        "victim": "{name} snickers at you.",
    },
    "giggle": {
        "self_no_target": "You giggle uncontrollably.",
        "room_no_target": "{name} giggles uncontrollably.",
        "self_targeted": "You giggle at {target}.",
        "room_targeted": "{name} giggles at {target}.",
        "victim": "{name} giggles at you.",
    },
    "gasp": {
        "self_no_target": "You gasp in surprise.",
        "room_no_target": "{name} gasps in surprise.",
        "self_targeted": "You gasp at {target}.",
        "room_targeted": "{name} gasps at {target}.",
        "victim": "{name} gasps at you.",
    },
    "blink": {
        "self_no_target": "You blink in confusion.",
        "room_no_target": "{name} blinks in confusion.",
        "self_targeted": "You blink at {target}.",
        "room_targeted": "{name} blinks at {target}.",
        "victim": "{name} blinks at you.",
    },
    "frown": {
        "self_no_target": "You frown thoughtfully.",
        "room_no_target": "{name} frowns thoughtfully.",
        "self_targeted": "You frown at {target}.",
        "room_targeted": "{name} frowns at {target}.",
        "victim": "{name} frowns at you.",
    },
    "smirk": {
        "self_no_target": "You smirk knowingly.",
        "room_no_target": "{name} smirks knowingly.",
        "self_targeted": "You smirk at {target}.",
        "room_targeted": "{name} smirks at {target}.",
        "victim": "{name} smirks at you.",
    },
    "scowl": {
        "self_no_target": "You scowl darkly.",
        "room_no_target": "{name} scowls darkly.",
        "self_targeted": "You scowl at {target}.",
        "room_targeted": "{name} scowls at {target}.",
        "victim": "{name} scowls at you.",
    },
    "ponder": {
        "self_no_target": "You ponder the mysteries of the universe.",
        "room_no_target": "{name} ponders the mysteries of the universe.",
        "self_targeted": "You ponder what to do about {target}.",
        "room_targeted": "{name} ponders what to do about {target}.",
        "victim": "{name} ponders what to do about you.",
    },
    "pray": {
        "self_no_target": "You kneel in prayer.",
        "room_no_target": "{name} kneels in prayer.",
        "self_targeted": "You pray for {target}.",
        "room_targeted": "{name} prays for {target}.",
        "victim": "{name} prays for you.",
    },
    "meditate": {
        "self_no_target": "You sit and meditate peacefully.",
        "room_no_target": "{name} sits and meditates peacefully.",
        "self_targeted": "You meditate alongside {target}.",
        "room_targeted": "{name} meditates alongside {target}.",
        "victim": "{name} meditates alongside you.",
    },
    "stretch": {
        "self_no_target": "You stretch languidly.",
        "room_no_target": "{name} stretches languidly.",
        "self_targeted": "You stretch in front of {target}.",
        "room_targeted": "{name} stretches in front of {target}.",
        "victim": "{name} stretches in front of you.",
    },
    "cringe": {
        "self_no_target": "You cringe in fear.",
        "room_no_target": "{name} cringes in fear.",
        "self_targeted": "You cringe away from {target}.",
        "room_targeted": "{name} cringes away from {target}.",
        "victim": "{name} cringes away from you.",
    },
    "cackle": {
        "self_no_target": "You cackle with mad glee.",
        "room_no_target": "{name} cackles with mad glee.",
        "self_targeted": "You cackle at {target}.",
        "room_targeted": "{name} cackles at {target}.",
        "victim": "{name} cackles at you.",
    },
    "scream": {
        "self_no_target": "You let out a blood-curdling scream.",
        "room_no_target": "{name} lets out a blood-curdling scream.",
        "self_targeted": "You scream at {target}.",
        "room_targeted": "{name} screams at {target}.",
        "victim": "{name} screams at you.",
    },
    "roar": {
        "self_no_target": "You roar with ferocity.",
        "room_no_target": "{name} roars with ferocity.",
        "self_targeted": "You roar at {target}.",
        "room_targeted": "{name} roars at {target}.",
        "victim": "{name} roars at you.",
    },
    "purr": {
        "self_no_target": "You purr contentedly.",
        "room_no_target": "{name} purrs contentedly.",
        "self_targeted": "You purr at {target}.",
        "room_targeted": "{name} purrs at {target}.",
        "victim": "{name} purrs at you.",
    },
    "snore": {
        "self_no_target": "You snore loudly.",
        "room_no_target": "{name} snores loudly.",
        "self_targeted": "You snore at {target}.",
        "room_targeted": "{name} snores at {target}.",
        "victim": "{name} snores at you.",
    },
    "burp": {
        "self_no_target": "You burp loudly and without shame.",
        "room_no_target": "{name} burps loudly and without shame.",
        "self_targeted": "You burp in {target}'s general direction.",
        "room_targeted": "{name} burps in {target}'s general direction.",
        "victim": "{name} burps in your general direction.",
    },
    "hiccup": {
        "self_no_target": "You hiccup embarrassingly.",
        "room_no_target": "{name} hiccups embarrassingly.",
        "self_targeted": "You hiccup at {target}.",
        "room_targeted": "{name} hiccups at {target}.",
        "victim": "{name} hiccups at you.",
    },
    "mumble": {
        "self_no_target": "You mumble something incomprehensible.",
        "room_no_target": "{name} mumbles something incomprehensible.",
        "self_targeted": "You mumble at {target}.",
        "room_targeted": "{name} mumbles at {target}.",
        "victim": "{name} mumbles at you.",
    },
    "mutter": {
        "self_no_target": "You mutter darkly under your breath.",
        "room_no_target": "{name} mutters darkly under their breath.",
        "self_targeted": "You mutter darkly at {target}.",
        "room_targeted": "{name} mutters darkly at {target}.",
        "victim": "{name} mutters darkly at you.",
    },
    "blush": {
        "self_no_target": "You blush a deep crimson.",
        "room_no_target": "{name} blushes a deep crimson.",
        "self_targeted": "You blush at {target}.",
        "room_targeted": "{name} blushes at {target}.",
        "victim": "{name} blushes at you.",
    },
    "taunt": {
        "self_no_target": "You taunt the air around you.",
        "room_no_target": "{name} taunts the air around them.",
        "self_targeted": "You taunt {target} mercilessly.",
        "room_targeted": "{name} taunts {target} mercilessly.",
        "victim": "{name} taunts you mercilessly.",
    },
    "high5": {
        "self_no_target": "You raise your hand for a high five but no one obliges.",
        "room_no_target": "{name} raises their hand for a high five but no one obliges.",
        "self_targeted": "You give {target} an enthusiastic high five!",
        "room_targeted": "{name} gives {target} an enthusiastic high five!",
        "victim": "{name} gives you an enthusiastic high five!",
    },
    "facepalm": {
        "self_no_target": "You facepalm in exasperation.",
        "room_no_target": "{name} facepalms in exasperation.",
        "self_targeted": "You facepalm at {target}'s antics.",
        "room_targeted": "{name} facepalms at {target}'s antics.",
        "victim": "{name} facepalms at your antics.",
    },
    "eyeroll": {
        "self_no_target": "You roll your eyes dramatically.",
        "room_no_target": "{name} rolls their eyes dramatically.",
        "self_targeted": "You roll your eyes at {target}.",
        "room_targeted": "{name} rolls their eyes at {target}.",
        "victim": "{name} rolls their eyes at you.",
    },
    "thumbsup": {
        "self_no_target": "You give a thumbs up to nobody in particular.",
        "room_no_target": "{name} gives a thumbs up to nobody in particular.",
        "self_targeted": "You give {target} a thumbs up.",
        "room_targeted": "{name} gives {target} a thumbs up.",
        "victim": "{name} gives you a thumbs up.",
    },
    "shh": {
        "self_no_target": "You raise a finger to your lips and shush everyone.",
        "room_no_target": "{name} raises a finger to their lips and shushes everyone.",
        "self_targeted": "You shush {target}.",
        "room_targeted": "{name} shushes {target}.",
        "victim": "{name} shushes you.",
    },
    "bonk": {
        "self_no_target": "You bonk yourself on the head.",
        "room_no_target": "{name} bonks themselves on the head.",
        "self_targeted": "You bonk {target} on the head.",
        "room_targeted": "{name} bonks {target} on the head.",
        "victim": "{name} bonks you on the head.",
    },
}


class CommandParser:
    def cmd_progression(self, character, args):
        """Show the D&D 3.5e advancement chart for feats, skill ranks, and ability increases."""
        lines = [
            "D&D 3.5e Character Advancement Chart:",
            "",
            "| Level | Feat? | Ability Score? | Max Class Skill | Max Cross-Class Skill |",
            "|-------|-------|----------------|-----------------|----------------------|",
        ]
        for lvl in range(1, 21):
            feat = "Yes" if lvl == 1 or lvl in (3, 6, 9, 12, 15, 18) else ""
            ability = "Yes" if lvl in (4, 8, 12, 16, 20) else ""
            max_class = lvl + 3
            max_cross = (lvl + 3) / 2
            lines.append(f"| {lvl:<5} | {feat:<5} | {ability:<14} | {max_class:<15} | {max_cross:<20} |")
        lines.append("")
        lines.append("- Feats: 1st, 3rd, 6th, 9th, 12th, 15th, 18th level.")
        lines.append("- Ability Score: 4th, 8th, 12th, 16th, 20th level.")
        lines.append("- Max Class Skill Rank: level + 3")
        lines.append("- Max Cross-Class Skill Rank: (level + 3) / 2")
        return "\n".join(lines)
    def cmd_appraise(self, character, args):
        """Appraise the value of an item in your inventory or in the shopkeeper's stock."""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        if not args:
            return "Appraise what? Usage: appraise <item name>"
        # Check player's inventory first
        item = next((i for i in character.inventory if i.name.lower() == args.lower()), None)
        if item:
            price = shopkeeper.get_sell_price(item)
            return f"{shopkeeper.name} says: 'I can offer you {price} gp for your {item.name}." + (" It's in fine condition!'" if getattr(item, 'hp', None) == getattr(item, 'max_hp', None) else " It's a bit worn, but I'll take it.'")
        # Check shopkeeper's stock
        items = shopkeeper.get_shop_items()
        item = next((i for i in items if i.name.lower() == args.lower()), None)
        if item:
            price = shopkeeper.get_buy_price(item)
            return f"{shopkeeper.name} says: 'That {item.name} will cost you {price} gp.'"
        return f"{shopkeeper.name} says: 'I don't see any {args} here.'"

    async def cmd_talk(self, character, args):
        """
        Talk to an NPC in the room. Uses AI for roleplay responses.
        Usage: talk <npc name> <message>
               talk <npc name>  (for a greeting)

        Examples:
            talk guard hello
            talk merchant what do you have for sale?
            talk sage tell me about dragons
        """
        if not args:
            # List NPCs in the room
            mobs = [m for m in getattr(character.room, 'mobs', []) if getattr(m, 'alive', True)]
            if not mobs:
                return "There's no one here to talk to."
            npc_names = [m.name for m in mobs]
            return f"You can talk to: {', '.join(npc_names)}\nUsage: talk <name> <message>"

        parts = args.split(None, 1)
        npc_name = parts[0].lower()
        message = parts[1] if len(parts) > 1 else "hello"

        # Find the NPC
        npc = None
        for mob in getattr(character.room, 'mobs', []):
            if getattr(mob, 'alive', True) and npc_name in mob.name.lower():
                npc = mob
                break

        if not npc:
            return f"You don't see '{parts[0]}' here."

        # Use AI system for response
        from src import ai
        try:
            response = await ai.get_npc_response(
                npc=npc,
                player=character,
                message=message,
                room=character.room,
                use_llm=True
            )
            return f"{npc.name} says: \"{response}\""
        except Exception as e:
            # Fallback to simple response if AI fails
            return f"{npc.name} looks at you but doesn't respond."
    def _find_shopkeeper(self, character):
        # Return the first shopkeeper mob in the room, or None
        for mob in getattr(character.room, 'mobs', []):
            if hasattr(mob, 'is_shopkeeper') and mob.is_shopkeeper():
                return mob
        return None

    def cmd_list(self, character, args):
        """List items for sale from the shopkeeper in the room."""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        items = shopkeeper.get_shop_items()
        if not items:
            return f"{shopkeeper.name} has nothing for sale."
        lines = [f"{shopkeeper.name} offers the following items:"]
        for item in items:
            price = shopkeeper.get_buy_price(item)
            lines.append(f"- {item.name} (Price: {price} gp)")
        return "\n".join(lines)

    def cmd_buy(self, character, args):
        """Buy an item from the shopkeeper in the room. Usage: buy <item name>"""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        if not args:
            return "Buy what? Usage: buy <item name>"
        # Auto-restock if shop is empty
        if not shopkeeper.shop_inventory and hasattr(shopkeeper, 'restock_shop'):
            shopkeeper.restock_shop()
        items = shopkeeper.get_shop_items()
        item = next((i for i in items if i.name.lower() == args.lower()), None)
        if not item:
            return f"{shopkeeper.name} does not have {args}."
        price = shopkeeper.get_buy_price(item)
        if getattr(character, 'gold', 0) < price:
            return f"You cannot afford {item.name}. (Price: {price} gp)"
        character.gold -= price
        character.inventory.append(item)
        shopkeeper.remove_shop_item(item.vnum)
        return f"You buy {item.name} for {price} gp."

    def cmd_sell(self, character, args):
        """Sell an item to the shopkeeper in the room. Usage: sell <item name>"""
        shopkeeper = self._find_shopkeeper(character)
        if not shopkeeper:
            return "There is no shopkeeper here."
        if not args:
            return "Sell what? Usage: sell <item name>"
        item = next((i for i in character.inventory if i.name.lower() == args.lower()), None)
        if not item:
            return f"You do not have {args}."
        price = shopkeeper.get_sell_price(item)
        character.gold = getattr(character, 'gold', 0) + price
        character.inventory.remove(item)
        shopkeeper.add_shop_item(item.vnum)
        return f"You sell {item.name} for {price} gp."
    def cmd_components(self, character, args):
        """
        Show all raw materials, spell components, and reagents available in the game.
        Usage: components
        """
        import os, json
        lines = ["Raw Materials, Spell Components, and Reagents:"]
        # Load raw materials
        raw_path = os.path.join(os.path.dirname(__file__), '../data/items_raw_materials.json')
        try:
            with open(raw_path, 'r', encoding='utf-8') as f:
                raw_materials = json.load(f)
            lines.append("\nRaw Materials:")
            for item in raw_materials:
                lines.append(f"- {item['name']}: {item.get('description','')}")
        except Exception as e:
            lines.append(f"(Could not load raw materials: {e})")

        # Load spell components from spells.py (if any)
        try:
            from src.spells import SPELLS
            component_set = set()
            material_set = set()
            for spell in SPELLS:
                for comp in spell.get('components', []):
                    if comp not in ('V', 'S', 'F', 'DF'):
                        component_set.add(comp)
                # Try to extract material components from description (optional)
                desc = spell.get('description', '')
                for mat in ["bat guano", "sulfur", "pearl", "amber", "resin", "charcoal", "saltpeter", "mercury", "mandrake root", "dragon blood"]:
                    if mat in desc.lower():
                        material_set.add(mat)
            if component_set or material_set:
                lines.append("\nSpell Components:")
                for comp in sorted(component_set):
                    lines.append(f"- {comp}")
                for mat in sorted(material_set):
                    lines.append(f"- {mat.title()}")
        except Exception as e:
            lines.append(f"(Could not load spell components: {e})")

        # List all unique materials from material_prices.json
        try:
            mat_path = os.path.join(os.path.dirname(__file__), '../data/material_prices.json')
            with open(mat_path, 'r', encoding='utf-8') as f:
                mat_data = json.load(f)
            lines.append("\nAll Known Materials:")
            for mat in sorted(mat_data.keys()):
                lines.append(f"- {mat.title()}")
        except Exception as e:
            lines.append(f"(Could not load material list: {e})")

        return "\n".join(lines)
    def cmd_saveplayer(self, character, args):
        """@saveplayer <name> | Force-save a player's data (admin only)."""
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        from src.character import Character
        name = args.strip()
        if not name:
            return "Usage: @saveplayer <name>"
        try:
            # This assumes the player is loaded in memory; otherwise, load from file
            for player in self.world.players:
                if player.name.lower() == name.lower():
                    player.save()
                    return f"Player {name} saved."
            # Not in memory: try to load and save
            import os, json
            player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
            filename = os.path.join(player_dir, f"{name.lower()}.json")
            if not os.path.exists(filename):
                return f"Player file for {name} not found."
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            char = Character.from_dict(data)
            char.save()
            return f"Player {name} saved (from file)."
        except Exception as e:
            import logging
            logging.error(f"Error saving player {name}: {e}")
            return f"Error saving player {name}: {e}"

    def cmd_backupplayer(self, character, args):
        """@backupplayer <name> | Create a backup of a player's data (admin only)."""
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        from src.character import Character
        name = args.strip()
        if not name:
            return "Usage: @backupplayer <name>"
        try:
            # Just call save, which now always creates a backup
            for player in self.world.players:
                if player.name.lower() == name.lower():
                    player.save()
                    return f"Backup created for {name}."
            # Not in memory: try to load and save
            import os, json
            player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
            filename = os.path.join(player_dir, f"{name.lower()}.json")
            if not os.path.exists(filename):
                return f"Player file for {name} not found."
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            char = Character.from_dict(data)
            char.save()
            return f"Backup created for {name} (from file)."
        except Exception as e:
            import logging
            logging.error(f"Error backing up player {name}: {e}")
            return f"Error backing up player {name}: {e}"

    def cmd_restoreplayer(self, character, args):
        """@restoreplayer <name> [timestamp] | Restore a player's data from backup (admin only)."""
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."
        from src.character import Character
        parts = args.strip().split()
        if not parts:
            return "Usage: @restoreplayer <name> [timestamp]"
        name = parts[0]
        timestamp = parts[1] if len(parts) > 1 else None
        try:
            path = Character.rollback(name, timestamp)
            return f"Player {name} restored from backup: {path}"
        except Exception as e:
            import logging
            logging.error(f"Error restoring player {name}: {e}")
            return f"Error restoring player {name}: {e}"
    def cmd_admin_deity(self, character, args):
        """Admin deity management.
        Usage: @deity create <name>         — Create a new Ascended God
               @deity link <id> <player>    — Link deity to a player account
               @deity unlink <id>           — Remove player link
               @deity shrine <id> <vnum>    — Add a shrine room to a deity
               @deity list                  — List all deity IDs"""
        if not getattr(character, 'is_immortal', False):
            return "Only immortals can manage deities."
        from src.religion import get_religion_manager
        rm = get_religion_manager()

        if not args:
            return "Usage: @deity [create|link|unlink|shrine|list]"

        parts = args.strip().split()
        subcmd = parts[0].lower()

        if subcmd == "list":
            lines = ["Deity IDs:"]
            for did, d in rm.get_all_deities().items():
                plink = f" -> {d['player_name']}" if d.get('player_name') else ""
                lines.append(f"  {did}: {d['name']}{plink}")
            return "\n".join(lines)

        elif subcmd == "create":
            name = " ".join(parts[1:]) if len(parts) > 1 else ""
            if not name:
                return "Usage: @deity create <deity name>"
            did = rm.create_deity(name)
            return f"Created new deity '{name}' with id '{did}'. Use @deity link to connect to a player."

        elif subcmd == "link":
            if len(parts) < 3:
                return "Usage: @deity link <deity_id> <player_name>"
            ok, msg = rm.link_deity_to_player(parts[1], parts[2])
            return msg

        elif subcmd == "unlink":
            if len(parts) < 2:
                return "Usage: @deity unlink <deity_id>"
            ok, msg = rm.unlink_deity(parts[1])
            return msg

        elif subcmd == "shrine":
            if len(parts) < 3:
                return "Usage: @deity shrine <deity_id> <room_vnum>"
            try:
                vnum = int(parts[2])
            except ValueError:
                return "Room vnum must be a number."
            ok, msg = rm.add_shrine(parts[1], vnum)
            return msg

        return "Usage: @deity [create|link|unlink|shrine|list]"

    def cmd_mobadd(self, character, args):
        """@mobadd <name> | Creates a new mob in the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @mobadd <name>"
        from src.mob import Mob
        # Find an unused vnum
        max_vnum = max(self.world.mobs.keys(), default=1000)
        new_vnum = max_vnum + 1
        name = args.strip()
        # Basic mob template
        mob = Mob(new_vnum, name, 1, (1, 6, 0), 10, (1, 4, 0))
        self.world.mobs[new_vnum] = mob
        character.room.mobs.append(mob)
        self.world.save_mobs()
        return f"Mob '{name}' created in this room (vnum {new_vnum})."

    def cmd_mobedit(self, character, args):
        """@mobedit <vnum> <field> <value> | Edits a mob's property."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @mobedit <vnum> <field> <value>"
        try:
            vnum = int(parts[0])
        except ValueError:
            return "Vnum must be a number."
        field, value = parts[1], parts[2]
        mob = self.world.mobs.get(vnum)
        if not mob:
            return f"No mob with vnum {vnum}."
        # Basic fields only for now
        if hasattr(mob, field):
            # Try to cast to int if possible
            try:
                val = int(value)
            except ValueError:
                val = value
            setattr(mob, field, val)
            self.world.save_mobs()
            return f"Mob {vnum} field '{field}' set to {val}."
        return f"Mob has no field '{field}'."

    def cmd_itemadd(self, character, args):
        """@itemadd <name> | Creates a new item in the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @itemadd <name>"
        from src.items import Item
        # Find an unused vnum
        if hasattr(self.world, 'items'):
            max_vnum = max(self.world.items.keys(), default=1000)
        else:
            if not hasattr(self.world, 'items'):
                self.world.items = {}
            max_vnum = 1000
        new_vnum = max_vnum + 1
        name = args.strip()
        # Basic item template
        item = Item(new_vnum, name, "misc", 1, 0, description=f"A {name}.")
        self.world.items[new_vnum] = item
        character.room.items.append(item)
        self.world.save_items()
        return f"Item '{name}' created in this room (vnum {new_vnum})."

    def cmd_itemedit(self, character, args):
        """@itemedit <vnum> <field> <value> | Edits an item's property."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @itemedit <vnum> <field> <value>"
        try:
            vnum = int(parts[0])
        except ValueError:
            return "Vnum must be a number."
        field, value = parts[1], parts[2]
        item = None
        if hasattr(self.world, 'items'):
            item = self.world.items.get(vnum)
        if not item:
            return f"No item with vnum {vnum}."
        if hasattr(item, field):
            try:
                val = int(value)
            except ValueError:
                val = value
            setattr(item, field, val)
            self.world.save_items()
            return f"Item {vnum} field '{field}' set to {val}."
        return f"Item has no field '{field}'."

    def cmd_botrun(self, character, args):
        """@botrun [max_rooms] [nofight] | Run the AI bot explorer (admin only)."""
        if not getattr(character, 'is_immortal', False):
            return "Only immortals can run the bot."
        from src.ai_player import run_bot_exploration

        parts = args.split() if args else []
        max_rooms = None
        fight = True
        for p in parts:
            if p.isdigit():
                max_rooms = int(p)
            elif p.lower() == "nofight":
                fight = False

        max_rooms = max_rooms or len(self.world.rooms)
        text, report = run_bot_exploration(self.world, self, max_rooms=max_rooms, max_time=120, fight=fight)
        return text

    def cmd_cast(self, character, args):
        """Casts a spell if prepared/known and slots are available, enforcing V/S and concentration."""
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check
        from src.spells import get_spell_by_name
        if not args:
            return "Cast what spell? Usage: cast <spell name>"
        spell_name = args.strip()
        spell = get_spell_by_name(spell_name)
        if not spell:
            return f"No such spell: {spell_name}"
        # Check if character has the spell prepared/known
        known = False
        # Prepared casters: Wizard, Cleric, Druid, Paladin, Ranger must use cmd_prepare first.
        # Spontaneous casters: Sorcerer, Bard, Magi cast from spells_known directly.
        PREPARED_CASTERS = {"Wizard", "Cleric", "Druid", "Paladin", "Ranger"}
        SPONTANEOUS_CASTERS = {"Sorcerer", "Bard", "Magi"}
        char_class = getattr(character, 'char_class', '')
        is_prepared = char_class in PREPARED_CASTERS
        if is_prepared:
            prepared = getattr(character, 'prepared_spells', {})
            for lvl, spells in prepared.items():
                if any(s.lower() == spell_name.lower() for s in spells):
                    known = True
                    break
            # Fallback: if prepared_spells not used yet, check spells_known for backward compat
            if not known:
                for s in character.spells_known.values():
                    if isinstance(s, dict):
                        if s.get("name", "").lower() == spell_name.lower():
                            known = True
                            break
                    elif isinstance(s, str):
                        if s.lower() == spell_name.lower():
                            known = True
                            break
        else:
            # Spontaneous casters use spells_known directly
            for s in character.spells_known.values():
                if isinstance(s, dict):
                    if s.get("name", "").lower() == spell_name.lower():
                        known = True
                        break
                elif isinstance(s, str):
                    if s.lower() == spell_name.lower():
                        known = True
                        break
        # Check for domain spells (Cleric only)
        if not known and character.char_class == "Cleric":
            # Check if the spell is a domain spell available at this level
            available_domains = character.get_available_domain_spells() if hasattr(character, 'get_available_domain_spells') else {}
            for lvl, spells in available_domains.items():
                if any(s.lower() == spell_name.lower() for s in spells):
                    known = True
                    break
        if not known:
            return f"You do not have {spell_name} prepared or known."
        # Find spell level for this class
        spell_level = spell["level"].get(character.char_class)
        if spell_level is None:
            return f"Your class cannot cast {spell_name}."
        # Check slots
        slots = character.spells_per_day.get(spell_level, 0)
        if slots < 1:
            return f"No spell slots remaining for level {spell_level}."
        # Enforce V/S components
        components = spell.get("components", [])
        if "V" in components and not character.can_cast_verbal():
            return "You cannot cast this spell: you are unable to speak!"
        if "S" in components and not character.can_cast_somatic():
            return "You cannot cast this spell: you are unable to move!"
        # Concentration check if interrupted (e.g., hit in combat)
        if character.was_interrupted():
            conc_result = character.skill_check("Concentration")
            # DC 10 + spell level (simplified)
            dc = 10 + spell_level
            if isinstance(conc_result, str):
                return f"Spell fails: {conc_result}"
            if conc_result < dc:
                character.clear_interrupted()
                return f"You fail to concentrate and lose the spell! (Needed {dc}, rolled {conc_result})"
            character.clear_interrupted()
        # Material component check
        material_component = spell.get("material")
        if material_component:
            inventory = getattr(character, 'inventory', [])
            component_item = None
            for item in inventory:
                item_name = getattr(item, 'name', '') if hasattr(item, 'name') else str(item)
                if item_name.lower() in material_component.lower() or material_component.lower() in item_name.lower():
                    component_item = item
                    break
            if not component_item:
                return f"You lack the material component: {material_component}"
            # Consume the component
            character.inventory.remove(component_item)

        # Alignment/Deity restrictions (for divine casters)
        # Check for alignment tags in spell['school'] or spell.get('alignment')
        alignment = getattr(character, 'alignment', None)
        deity = getattr(character, 'deity', None)
        # Only enforce for Cleric, Paladin, Druid (expand as needed)
        if character.char_class in ("Cleric", "Paladin", "Druid"):
            school = spell.get("school", "")
            # Alignment tag check (e.g., [Evil], [Good], [Lawful], [Chaotic])
            import re
            align_tags = re.findall(r'\[(.*?)\]', school)
            for tag in align_tags:
                tag = tag.lower()
                if tag == "evil" and (not alignment or "evil" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Evil] spells."
                if tag == "good" and (not alignment or "good" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Good] spells."
                if tag == "lawful" and (not alignment or "lawful" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Lawful] spells."
                if tag == "chaotic" and (not alignment or "chaotic" not in alignment.lower()):
                    return "Your alignment prevents you from casting [Chaotic] spells."
            # Deity restriction (if spell has 'deity' key)
            spell_deity = spell.get("deity")
            if spell_deity and (not deity or deity.lower() != spell_deity.lower()):
                return f"Only followers of {spell_deity} may cast this spell."
        # Deduct slot
        character.spells_per_day[spell_level] -= 1
        # Remove from prepared if prepared caster and prepared_spells is in use
        if is_prepared and hasattr(character, 'prepared_spells'):
            for lvl, spells in character.prepared_spells.items():
                if spell_name in spells:
                    character.prepared_spells[lvl].remove(spell_name)
                    break

        # Execute the spell effect
        effect_result = self._execute_spell(character, spell_name, args, spell_level)

        # Add slot info
        slots_remaining = character.spells_per_day.get(spell_level, 0)
        return f"{effect_result}\nSlots left for level {spell_level}: {slots_remaining}"

    def _execute_spell(self, caster, spell_name, args, spell_level):
        """Execute the actual spell effect - damage, healing, buffs, conditions."""
        import random
        from src.spells import (
            get_spell, calculate_spell_damage, calculate_healing,
            calculate_spell_dc, calculate_caster_level, get_num_missiles,
            get_num_rays, SaveType, SpellEffectType, TargetType
        )
        from src import conditions as cond

        spell = get_spell(spell_name)
        if not spell:
            return f"You cast {spell_name}! (Effect not implemented)"

        char_class = getattr(caster, 'char_class', 'Wizard')
        caster_level = calculate_caster_level(caster, char_class, spell=spell)
        results = [f"You cast {spell.name}!"]

        # Report elemental affinity bonus if active
        base_cl = getattr(caster, 'level', 1)
        if char_class in ("Paladin", "Ranger"):
            base_cl = max(1, base_cl - 3)
        cl_diff = caster_level - base_cl
        if cl_diff > 0:
            results.append(f"\033[0;36m[Elemental resonance: +{cl_diff} caster level]\033[0m")
        elif cl_diff < 0:
            results.append(f"\033[0;31m[Opposing element: {cl_diff} caster level]\033[0m")

        # Determine target
        target = None
        target_name = args.split()[-1] if args and len(args.split()) > len(spell_name.split()) else None

        # For self-targeted spells
        if spell.target_type == TargetType.SELF:
            target = caster
        # For touch/single target spells, find target
        elif spell.target_type in (TargetType.TOUCH, TargetType.RANGED_TOUCH, TargetType.SINGLE):
            if target_name:
                # Look for target in room
                if hasattr(caster, 'room') and caster.room:
                    # Check mobs
                    for mob in getattr(caster.room, 'mobs', []):
                        if hasattr(mob, 'name') and mob.name.lower() == target_name.lower():
                            if hasattr(mob, 'alive') and mob.alive:
                                target = mob
                                break
                    # Check players
                    if not target:
                        for player in getattr(caster.room, 'players', []):
                            if hasattr(player, 'name') and player.name.lower() == target_name.lower():
                                target = player
                                break
            # Default to self for buffs/healing without target
            if not target and spell.effect_type in (SpellEffectType.BUFF, SpellEffectType.HEALING, SpellEffectType.PROTECTION):
                target = caster

        # Handle touch attacks
        if spell.target_type == TargetType.RANGED_TOUCH and target and target != caster:
            # Roll ranged touch attack
            attack_roll = random.randint(1, 20)
            attack_bonus = (getattr(caster, 'level', 1) // 2) + ((getattr(caster, 'dex_score', 10) - 10) // 2)
            total_attack = attack_roll + attack_bonus
            target_touch_ac = 10 + ((getattr(target, 'dex_score', 10) - 10) // 2)

            if attack_roll == 1 or (attack_roll != 20 and total_attack < target_touch_ac):
                results.append(f"Ranged touch attack misses {target.name}! ({total_attack} vs Touch AC {target_touch_ac})")
                return "\n".join(results)
            results.append(f"Ranged touch attack hits {target.name}! ({total_attack} vs Touch AC {target_touch_ac})")

        elif spell.target_type == TargetType.TOUCH and target and target != caster:
            # Touch attack (melee)
            attack_roll = random.randint(1, 20)
            attack_bonus = (getattr(caster, 'level', 1) // 2) + ((getattr(caster, 'str_score', 10) - 10) // 2)
            total_attack = attack_roll + attack_bonus
            target_touch_ac = 10 + ((getattr(target, 'dex_score', 10) - 10) // 2)

            # For healing/buff spells on allies, auto-hit
            if spell.effect_type not in (SpellEffectType.DAMAGE, SpellEffectType.CONDITION, SpellEffectType.DEBUFF):
                pass  # Auto-hit friendly spells
            elif attack_roll == 1 or (attack_roll != 20 and total_attack < target_touch_ac):
                results.append(f"Touch attack misses {target.name}! ({total_attack} vs Touch AC {target_touch_ac})")
                return "\n".join(results)
            else:
                results.append(f"Touch attack hits {target.name}!")

        # Calculate saving throw DC
        spell_dc = calculate_spell_dc(caster, spell, char_class)

        # Spell Resistance check (only for spells that allow SR, and only vs valid single targets)
        if spell.spell_resistance and target and target != caster:
            sr_value = getattr(target, 'spell_resistance', 0)
            if sr_value > 0:
                sr_roll = random.randint(1, 20) + caster_level
                # Spell Penetration feats
                feats = getattr(caster, 'feats', [])
                if 'Greater Spell Penetration' in feats:
                    sr_roll += 4
                elif 'Spell Penetration' in feats:
                    sr_roll += 2
                if sr_roll < sr_value:
                    results.append(
                        f"The spell fails to penetrate {target.name}'s spell resistance! "
                        f"({sr_roll} vs SR {sr_value})"
                    )
                    return "\n".join(results)

        # Handle different spell effect types
        # =====================================================================
        # DAMAGE SPELLS
        # =====================================================================
        if spell.effect_type == SpellEffectType.DAMAGE and spell.damage_dice:
            targets_hit = []

            # Area spells hit multiple targets
            if spell.target_type in (TargetType.AREA_BURST, TargetType.AREA_CONE, TargetType.AREA_LINE, TargetType.AREA_SPREAD):
                if hasattr(caster, 'room') and caster.room:
                    # Hit all mobs in room
                    for mob in getattr(caster.room, 'mobs', []):
                        if hasattr(mob, 'alive') and mob.alive:
                            targets_hit.append(mob)
            elif target:
                targets_hit.append(target)

            if not targets_hit:
                results.append("No valid targets!")
                return "\n".join(results)

            # Special handling for Magic Missile (auto-hit, multiple missiles)
            if spell.name.lower() == "magic missile":
                num_missiles = get_num_missiles(caster_level)
                total_damage = 0
                for _ in range(num_missiles):
                    missile_dmg = random.randint(1, 4) + 1
                    total_damage += missile_dmg

                # Distribute damage (simplified: all at one target)
                for t in targets_hit[:1]:
                    # Check for Shield spell immunity
                    if hasattr(t, 'active_buffs') and t.active_buffs.get('immune_magic_missile'):
                        results.append(f"{t.name}'s Shield blocks the missiles!")
                        continue

                    t.hp = max(0, t.hp - total_damage)
                    results.append(f"{num_missiles} missiles strike {t.name} for {total_damage} force damage!")

                    if t.hp <= 0:
                        if hasattr(t, 'alive'):
                            t.alive = False
                        results.append(f"{t.name} is slain!")
                        # Quest trigger
                        if hasattr(caster, 'quest_log'):
                            mob_type = getattr(t, 'mob_type', t.name.lower())
                            try:
                                quest_updates = quests.on_mob_killed(caster, mob_type, caster.quest_log if hasattr(caster, 'quest_log') else None, quests.get_quest_manager() if hasattr(quests, 'get_quest_manager') else None)
                            except Exception:
                                quest_updates = []
                            for update in quest_updates:
                                results.append(f"[Quest] {update}")

            # Special handling for Scorching Ray (multiple rays)
            elif spell.name.lower() == "scorching ray":
                num_rays = get_num_rays(caster_level)
                for i, t in enumerate(targets_hit[:num_rays]):
                    damage, dice_str = calculate_spell_damage(caster, spell.damage_dice, char_class)
                    t.hp = max(0, t.hp - damage)
                    results.append(f"Ray {i+1} hits {t.name} for {damage} fire damage! ({dice_str})")

                    if t.hp <= 0:
                        if hasattr(t, 'alive'):
                            t.alive = False
                        results.append(f"{t.name} is slain!")

            # Standard damage spell
            else:
                damage, dice_str = calculate_spell_damage(caster, spell.damage_dice, char_class)

                for t in targets_hit:
                    final_damage = damage

                    # Saving throw
                    if spell.save_type != SaveType.NONE:
                        save_roll = random.randint(1, 20)
                        save_bonus = 0
                        if spell.save_type == SaveType.REFLEX:
                            save_bonus = ((getattr(t, 'dex_score', 10) - 10) // 2) + (getattr(t, 'level', 1) // 2)
                        elif spell.save_type == SaveType.FORTITUDE:
                            save_bonus = ((getattr(t, 'con_score', 10) - 10) // 2) + (getattr(t, 'level', 1) // 2)
                        elif spell.save_type == SaveType.WILL:
                            save_bonus = ((getattr(t, 'wis_score', 10) - 10) // 2) + (getattr(t, 'level', 1) // 2)

                        total_save = save_roll + save_bonus

                        if total_save >= spell_dc:
                            if spell.save_effect.value == "half":
                                final_damage = damage // 2
                                results.append(f"{t.name} makes save ({total_save} vs DC {spell_dc}) - half damage!")
                                # Fix 45: Evasion (Rogue level 2+) — no damage on successful Reflex save
                                if (spell.save_type == SaveType.REFLEX
                                        and getattr(t, 'char_class', '') == "Rogue"
                                        and getattr(t, 'class_level', getattr(t, 'level', 0)) >= 2):
                                    final_damage = 0
                                    results.append(f"{t.name}'s Evasion negates all damage!")
                            elif spell.save_effect.value == "negates":
                                results.append(f"{t.name} makes save ({total_save} vs DC {spell_dc}) - no effect!")
                                continue
                        else:
                            results.append(f"{t.name} fails save ({total_save} vs DC {spell_dc})!")
                            # Fix 45: Improved Evasion (Rogue level 10+) — half damage on failed Reflex save
                            if (spell.save_type == SaveType.REFLEX
                                    and getattr(t, 'char_class', '') == "Rogue"
                                    and getattr(t, 'class_level', getattr(t, 'level', 0)) >= 10):
                                final_damage = final_damage // 2
                                results.append(f"{t.name}'s Improved Evasion halves damage!")

                    t.hp = max(0, t.hp - final_damage)
                    damage_type = spell.damage_type or "magical"
                    results.append(f"{t.name} takes {final_damage} {damage_type} damage! ({dice_str})")

                    if t.hp <= 0:
                        if hasattr(t, 'alive'):
                            t.alive = False
                        results.append(f"{t.name} is slain!")
                        # Quest trigger
                        if hasattr(caster, 'quest_log'):
                            mob_type = getattr(t, 'mob_type', t.name.lower())
                            try:
                                quest_updates = quests.on_mob_killed(caster, mob_type, caster.quest_log if hasattr(caster, 'quest_log') else None, quests.get_quest_manager() if hasattr(quests, 'get_quest_manager') else None)
                            except Exception:
                                quest_updates = []
                            for update in quest_updates:
                                results.append(f"[Quest] {update}")

        # =====================================================================
        # HEALING SPELLS
        # =====================================================================
        elif spell.effect_type == SpellEffectType.HEALING and spell.healing_dice:
            if not target:
                target = caster

            healing, dice_str = calculate_healing(caster, spell.healing_dice, char_class)
            old_hp = target.hp
            target.hp = min(target.max_hp, target.hp + healing)
            actual_heal = target.hp - old_hp

            if target == caster:
                results.append(f"You heal yourself for {actual_heal} HP! ({dice_str}) [HP: {target.hp}/{target.max_hp}]")
            else:
                results.append(f"You heal {target.name} for {actual_heal} HP! ({dice_str}) [HP: {target.hp}/{target.max_hp}]")

        # =====================================================================
        # BUFF SPELLS
        # =====================================================================
        elif spell.effect_type == SpellEffectType.BUFF and spell.buff_effects:
            if not target:
                target = caster

            # Initialize active_buffs if needed
            if not hasattr(target, 'active_buffs'):
                target.active_buffs = {}

            # Apply buff effects
            buff_desc = []
            duration_rounds = spell.duration_rounds if spell.duration_rounds > 0 else caster_level * 10

            for buff_name, buff_value in spell.buff_effects.items():
                target.active_buffs[buff_name] = {
                    'value': buff_value,
                    'duration': duration_rounds,
                    'spell': spell.name
                }

                # Apply stat bonuses immediately
                if buff_name == 'str_bonus':
                    if not hasattr(target, 'temp_str_bonus'):
                        target.temp_str_bonus = 0
                    target.temp_str_bonus += buff_value
                    buff_desc.append(f"+{buff_value} Str")
                elif buff_name == 'dex_bonus':
                    if not hasattr(target, 'temp_dex_bonus'):
                        target.temp_dex_bonus = 0
                    target.temp_dex_bonus += buff_value
                    buff_desc.append(f"+{buff_value} Dex")
                elif buff_name == 'con_bonus':
                    if not hasattr(target, 'temp_con_bonus'):
                        target.temp_con_bonus = 0
                    target.temp_con_bonus += buff_value
                    buff_desc.append(f"+{buff_value} Con")
                elif buff_name == 'armor_bonus':
                    if not hasattr(target, 'temp_ac_bonus'):
                        target.temp_ac_bonus = 0
                    target.temp_ac_bonus += buff_value
                    buff_desc.append(f"+{buff_value} AC (armor)")
                elif buff_name == 'shield_bonus':
                    if not hasattr(target, 'temp_ac_bonus'):
                        target.temp_ac_bonus = 0
                    target.temp_ac_bonus += buff_value
                    buff_desc.append(f"+{buff_value} AC (shield)")
                elif buff_name == 'attack_bonus':
                    if not hasattr(target, 'temp_attack_bonus'):
                        target.temp_attack_bonus = 0
                    target.temp_attack_bonus += buff_value
                    buff_desc.append(f"+{buff_value} attack")
                elif buff_name == 'save_bonus':
                    if not hasattr(target, 'temp_save_bonus'):
                        target.temp_save_bonus = 0
                    target.temp_save_bonus += buff_value
                    buff_desc.append(f"+{buff_value} saves")
                elif buff_name == 'invisible':
                    if hasattr(target, 'add_condition'):
                        target.add_condition('invisible')
                    buff_desc.append("Invisible")
                elif buff_name == 'fly_speed':
                    buff_desc.append(f"Fly {buff_value} ft.")
                elif buff_name == 'concealment':
                    buff_desc.append(f"{buff_value}% concealment")

            target_name = "yourself" if target == caster else target.name
            results.append(f"You enhance {target_name}: {', '.join(buff_desc)} for {duration_rounds} rounds!")

        # =====================================================================
        # CONDITION SPELLS (debuffs)
        # =====================================================================
        elif spell.effect_type == SpellEffectType.CONDITION and spell.condition_applied:
            if not target or target == caster:
                results.append("You need a target for this spell!")
                return "\n".join(results)

            # Saving throw
            saved = False
            if spell.save_type != SaveType.NONE:
                save_roll = random.randint(1, 20)
                save_bonus = 0
                if spell.save_type == SaveType.WILL:
                    save_bonus = ((getattr(target, 'wis_score', 10) - 10) // 2) + (getattr(target, 'level', 1) // 2)
                elif spell.save_type == SaveType.FORTITUDE:
                    save_bonus = ((getattr(target, 'con_score', 10) - 10) // 2) + (getattr(target, 'level', 1) // 2)
                elif spell.save_type == SaveType.REFLEX:
                    save_bonus = ((getattr(target, 'dex_score', 10) - 10) // 2) + (getattr(target, 'level', 1) // 2)

                total_save = save_roll + save_bonus

                if total_save >= spell_dc:
                    saved = True
                    if spell.save_effect.value == "negates":
                        results.append(f"{target.name} resists the spell! (Save {total_save} vs DC {spell_dc})")
                        return "\n".join(results)
                    elif spell.save_effect.value == "partial":
                        results.append(f"{target.name} partially resists! (Save {total_save} vs DC {spell_dc})")
                else:
                    results.append(f"{target.name} fails to resist! (Save {total_save} vs DC {spell_dc})")

            # Apply condition
            condition_name = spell.condition_applied
            duration = spell.condition_duration if spell.condition_duration > 0 else caster_level

            if hasattr(target, 'add_condition'):
                target.add_condition(condition_name)
            if hasattr(target, 'active_conditions'):
                target.active_conditions[condition_name] = duration

            condition_display = condition_name.replace('_', ' ').title()
            results.append(f"{target.name} is now {condition_display} for {duration} rounds!")

        # =====================================================================
        # PROTECTION SPELLS
        # =====================================================================
        elif spell.effect_type == SpellEffectType.PROTECTION:
            if not target:
                target = caster

            if not hasattr(target, 'active_buffs'):
                target.active_buffs = {}

            duration_rounds = spell.duration_rounds if spell.duration_rounds > 0 else caster_level * 10

            for buff_name, buff_value in spell.buff_effects.items():
                target.active_buffs[buff_name] = {
                    'value': buff_value,
                    'duration': duration_rounds,
                    'spell': spell.name
                }

            target_name = "yourself" if target == caster else target.name
            results.append(f"You protect {target_name} with {spell.name} for {duration_rounds} rounds!")

        # =====================================================================
        # DISPEL SPELLS
        # =====================================================================
        elif spell.effect_type == SpellEffectType.DISPEL:
            if not target:
                results.append("You need a target to dispel!")
                return "\n".join(results)

            active_buffs = getattr(target, 'active_buffs', {})
            if not active_buffs:
                results.append(f"{target.name} has no active magical effects to dispel.")
            else:
                dispelled = []
                still_active = {}
                for buff_name, buff_data in list(active_buffs.items()):
                    buff_caster_level = buff_data.get('caster_level', 10) if isinstance(buff_data, dict) else 10
                    dispel_roll = random.randint(1, 20) + caster_level
                    dispel_dc = 11 + buff_caster_level
                    if dispel_roll >= dispel_dc:
                        # Dispel succeeded — reverse stat effects
                        if isinstance(buff_data, dict):
                            buff_val = buff_data.get('value', 0)
                            if buff_name == 'str_bonus':
                                target.temp_str_bonus = max(0, getattr(target, 'temp_str_bonus', 0) - buff_val)
                            elif buff_name == 'dex_bonus':
                                target.temp_dex_bonus = max(0, getattr(target, 'temp_dex_bonus', 0) - buff_val)
                            elif buff_name == 'con_bonus':
                                target.temp_con_bonus = max(0, getattr(target, 'temp_con_bonus', 0) - buff_val)
                            elif buff_name in ('armor_bonus', 'shield_bonus'):
                                target.temp_ac_bonus = max(0, getattr(target, 'temp_ac_bonus', 0) - buff_val)
                            elif buff_name == 'attack_bonus':
                                target.temp_attack_bonus = max(0, getattr(target, 'temp_attack_bonus', 0) - buff_val)
                            elif buff_name == 'save_bonus':
                                target.temp_save_bonus = max(0, getattr(target, 'temp_save_bonus', 0) - buff_val)
                            elif buff_name == 'invisible':
                                if hasattr(target, 'remove_condition'):
                                    target.remove_condition('invisible')
                        dispelled.append(buff_name.replace('_', ' ').title())
                    else:
                        still_active[buff_name] = buff_data
                target.active_buffs = still_active
                if dispelled:
                    results.append(f"Dispelled from {target.name}: {', '.join(dispelled)}!")
                else:
                    results.append(f"Failed to dispel any effects from {target.name}.")

        # =====================================================================
        # UTILITY/OTHER SPELLS
        # =====================================================================
        else:
            results.append(spell.description)

        # Show remaining slots
        remaining = caster.spells_per_day.get(spell_level, 0)
        results.append(f"(Level {spell_level} slots remaining: {remaining})")

        return "\n".join(results)

    # ...existing code...
    def __init__(self, world):
        self.world = world
        self.commands = {
            "look": self.cmd_look,
            "l": self.cmd_look,
            "say": self.cmd_say,
            "kill": self.cmd_kill,
            "north": self.cmd_move,
            "exits": self.cmd_exits,
            "quest": self.cmd_quest,
            "gecho": self.cmd_gecho,
            "who": self.cmd_who,
            "stats": self.cmd_stats,
            "get": self.cmd_get,
            "take": self.cmd_get,
            "drop": self.cmd_drop,
            "inventory": self.cmd_inventory,
            "inv": self.cmd_inventory,
            "i": self.cmd_inventory,
            "help": self.cmd_help,
            "score": self.cmd_score,
            "skills": self.cmd_skills,
            "spells": self.cmd_spells,
            "cast": self.cmd_cast,
            "spellinfo": self.cmd_spellinfo,
            "spellbook": self.cmd_spellbook,
            "domains": self.cmd_domains,
            "prepare": self.cmd_prepare,
            "memorize": self.cmd_prepare,  # Alias
            "companion": self.cmd_companion,
            "quest": self.cmd_questpage,
            "levelup": self.cmd_levelup,
            "recall": self.cmd_recall,
            "@dig": self.cmd_dig,
            "@desc": self.cmd_desc,
            "@exit": self.cmd_exit,
            "@flag": self.cmd_flag,
            "@deity": self.cmd_admin_deity,
            "@mobadd": self.cmd_mobadd,
            "@mobedit": self.cmd_mobedit,
            "@itemadd": self.cmd_itemadd,
            "@itemedit": self.cmd_itemedit,
            "components": self.cmd_components,
            # Equipment commands
            "wear": self.cmd_wear,
            "equip": self.cmd_wear,
            "remove": self.cmd_remove,
            "unequip": self.cmd_remove,
            "equipment": self.cmd_equipment,
            "eq": self.cmd_equipment,
            # Rest and recovery
            "rest": self.cmd_rest,
            "sleep": self.cmd_rest,
            # Status
            "conditions": self.cmd_conditions,
            "status": self.cmd_status,
            # Full attack
            "fullattack": self.cmd_fullattack,
            "fa": self.cmd_fullattack,
            # Admin condition commands
            "@addcondition": self.cmd_addcondition,
            "@removecondition": self.cmd_removecondition,
            "@listconditions": self.cmd_listconditions,
            # Combat maneuver commands
            "disarm": self.cmd_disarm,
            "trip": self.cmd_trip,
            "bullrush": self.cmd_bullrush,
            "grapple": self.cmd_grapple,
            "overrun": self.cmd_overrun,
            "sunder": self.cmd_sunder,
            "feint": self.cmd_feint,
            "whirlwind": self.cmd_whirlwind,
            "springattack": self.cmd_springattack,
            "stunningfist": self.cmd_stunningfist,
            "stun": self.cmd_stunningfist,
            "gdamage": self.cmd_grapple_damage,
            "gpin": self.cmd_grapple_pin,
            "gescape": self.cmd_grapple_escape,
            # NPC interaction (AI-powered)
            "talk": self.cmd_talk,
            "ask": self.cmd_talk,
            "converse": self.cmd_talk,
            # AI configuration commands (admin)
            "@ai": self.cmd_ai_config,
            "@aimodel": self.cmd_ai_model,
            "@aistatus": self.cmd_ai_status,
            # Respawn commands (admin)
            "@respawn": self.cmd_respawn,
            "@respawnall": self.cmd_respawnall,
            "@respawnstatus": self.cmd_respawnstatus,
            "@setrespawn": self.cmd_setrespawn,
            # Time and schedule commands
            "time": self.cmd_time,
            "@settime": self.cmd_settime,
            "@schedule": self.cmd_schedule,
            "@movenpc": self.cmd_movenpc,
            # Player death/respawn
            "respawn": self.cmd_player_respawn,
            # Combat: flee, queue, auto-attack, target
            "flee": self.cmd_flee,
            "queue": self.cmd_queue,
            "q": self.cmd_queue,
            "clearqueue": self.cmd_clearqueue,
            "cq": self.cmd_clearqueue,
            "showqueue": self.cmd_showqueue,
            "sq": self.cmd_showqueue,
            "autoattack": self.cmd_autoattack,
            "aa": self.cmd_autoattack,
            "target": self.cmd_target,
            # Kin-sense
            "sense": self.cmd_sense,
            "kinsense": self.cmd_sense,
            # Corpse looting
            "loot": self.cmd_loot,
            # Shop commands
            "buy": self.cmd_buy,
            "sell": self.cmd_sell,
            "list": self.cmd_list,
            "shop": self.cmd_list,
            "appraise": self.cmd_appraise,
            # Economy / interaction
            "give": self.cmd_give,
            # Combat stance toggles
            "powerattack": self.cmd_powerattack,
            "combatexpertise": self.cmd_combatexpertise,
            # Fix 39-41: Charge, Total Defense, Fighting Defensively
            "charge": self.cmd_charge,
            "totaldefense": self.cmd_totaldefense,
            "td": self.cmd_totaldefense,
            "fightdef": self.cmd_fightdef,
            "defensive": self.cmd_fightdef,
            # Immortal setter commands
            "@sethp": self.cmd_sethp,
            "@setmove": self.cmd_setmove,
            "@setac": self.cmd_setac,
            "@setlevel": self.cmd_setlevel,
            "@setxp": self.cmd_setxp,
            "@setgold": self.cmd_setgold,
            "@setstr": self.cmd_setstr,
            "@setdex": self.cmd_setdex,
            "@setcon": self.cmd_setcon,
            "@setint": self.cmd_setint,
            "@setwis": self.cmd_setwis,
            "@setcha": self.cmd_setcha,
            "@setrace": self.cmd_setrace,
            "@setclass": self.cmd_setclass,
            "@setalignment": self.cmd_setalignment,
            "@setdeity": self.cmd_setdeity,
            "@settitle": self.cmd_settitle,
            "@setaffinity": self.cmd_setaffinity,
            "@setimmortal": self.cmd_setimmortal,
            "@setai": self.cmd_setai,
            "@setfeat": self.cmd_setfeat,
            "@setskill": self.cmd_setskill,
            "@setname": self.cmd_setname,
            "@setterrain": self.cmd_setterrain,
            "@setweather": self.cmd_setweather,
            # New immortal/builder commands
            "@setmob": self.cmd_setmob,
            "@setitem": self.cmd_setitem,
            "@setreset": self.cmd_setreset,
            "@setspells": self.cmd_setspells,
            "@setinventory": self.cmd_setinventory,
            "@setequipment": self.cmd_setequipment,
            "@setprompt": self.cmd_setprompt,
            "@setpassword": self.cmd_setpassword,
            "@setdoor": self.cmd_setdoor,
            "@setroom": self.cmd_setroom,
            "@setlight": self.cmd_setlight,
            "@setnote": self.cmd_setnote,
            "@setowner": self.cmd_setowner,
            "@setcolor": self.cmd_setcolor,
            "@setemail": self.cmd_setemail,
            "@setresist": self.cmd_setresist,
            "@setimmune": self.cmd_setimmune,
            "@build": self.cmd_build,
            "@setarea": self.cmd_setarea,
            "@setzone": self.cmd_setzone,
            "@sethelp": self.cmd_sethelp,
            "@setvnum": self.cmd_setvnum,
            # Bank / Storage commands
            "deposit": self.cmd_deposit,
            "withdraw": self.cmd_withdraw,
            # Newbie channel
            "newbie": self.cmd_newbie,
            # Rescue
            "rescue": self.cmd_rescue,
            # Consider (System 3)
            "consider": self.cmd_consider,
            "con": self.cmd_consider,
            # Wimpy (System 4)
            "wimpy": self.cmd_wimpy,
            # Scan (System 5)
            "scan": self.cmd_scan,
            # Identify (System 8)
            "identify": self.cmd_identify,
            "id": self.cmd_identify,
            # Track (System 9)
            "track": self.cmd_track,
            # Door system (Phase 2)
            "open": self.cmd_open,
            "close": self.cmd_close,
            "lock": self.cmd_lock,
            "unlock": self.cmd_unlock,
            "pick": self.cmd_pick,
            # Hide/Sneak system (System 16)
            "hide": self.cmd_hide,
            "sneak": self.cmd_sneak,
            # Consumable items (Systems 13-15: Potions / Scrolls / Wands)
            "quaff": self.cmd_quaff,
            "drink": self.cmd_quaff,
            "use": self.cmd_use,
            "read": self.cmd_read_scroll,
            # Weather (System 19)
            "weather": self.cmd_weather,
            # Map (System 20)
            "map": self.cmd_map,
            # Party / Group system (Phase 3)
            "group": self.cmd_group,
            "follow": self.cmd_follow,
            "unfollow": self.cmd_unfollow,
            "assist": self.cmd_assist,
            "gtell": self.cmd_gtell,
            # Crafting (Phase 3)
            "craft": self.cmd_craft,
            "recipes": self.cmd_recipes,
            # Mount system (System 27)
            "mount": self.cmd_mount,
            "dismount": self.cmd_dismount,
            # Fishing / Mining / Gathering (System 28)
            "fish": self.cmd_fish,
            "mine": self.cmd_mine,
            "gather": self.cmd_gather,
            # Achievements (System 30)
            "achievements": self.cmd_achievements,
            "achieve": self.cmd_achievements,
            # Hunger / Thirst (System 31)
            "eat": self.cmd_eat,
            "drink_water": self.cmd_drink_water,
            "survivalmode": self.cmd_survivalmode,
            # Player Housing (System 32)
            "buyroom": self.cmd_buyroom,
            "setdesc": self.cmd_setdesc,
            "home": self.cmd_home,
            # Mail system (System 24)
            "mail": self.cmd_mail,
            "sendmail": self.cmd_sendmail,
            "readmail": self.cmd_readmail,
            # Bulletin Boards (System 25)
            "board": self.cmd_board,
            "post": self.cmd_post,
            "readnote": self.cmd_readnote,
            "note": self.cmd_readnote,
            # Auction House (System 26)
            "auction": self.cmd_auction,
            "auc": self.cmd_auction,
            # Factions / Reputation
            "faction": self.cmd_faction,
            "factions": self.cmd_faction,
            # Rune-circle interaction
            "study": self.cmd_study,
            "activate": self.cmd_activate,
            "repair": self.cmd_repair,
            # Religion / Deities
            "pray": self.cmd_pray,
            "worship": self.cmd_worship,
            "deities": self.cmd_deities,
            "divine": self.cmd_divine,
            # Emotes / Socials
            "emote": self.cmd_emote,
            "me": self.cmd_emote,
            # Speedwalk (System 9)
            "speedwalk": self.cmd_speedwalk,
            "sw": self.cmd_speedwalk,
            "walk": self.cmd_speedwalk,
            # Alias system (System 10)
            "alias": self.cmd_alias,
            # Container system (System 2)
            "put": self.cmd_put,
            "peek": self.cmd_peek,
            # Where command (System 4)
            "where": self.cmd_where,
            # Auto-loot / Auto-gold (System 5)
            "autoloot": self.cmd_autoloot,
            "autogold": self.cmd_autogold,
            # Light Sources (System 6)
            "light": self.cmd_light,
            "extinguish": self.cmd_extinguish,
            # Cure (System 8)
            "cure": self.cmd_cure,
            # XP / TNL (System 21)
            "tnl": self.cmd_tnl,
            "xp": self.cmd_tnl,
            # Guild / Clan system (System 24)
            "guild": self.cmd_guild,
            "clan": self.cmd_guild,
            # Traps (System 25)
            "search": self.cmd_search,
            "disarmtrap": self.cmd_disarmtrap,
            # System 12: Ranged Combat
            "shoot": self.cmd_shoot,
            "fire": self.cmd_shoot,
            # System 13: Practice / Train
            "practice": self.cmd_practice,
            "prac": self.cmd_practice,
            "train": self.cmd_train,
            # System 15: Config / Toggle
            "config": self.cmd_config,
            "toggle": self.cmd_config,
            # System 16: Areas / Zone List
            "areas": self.cmd_areas,
            "zones": self.cmd_areas,
            # System 17: Prompt Customization
            "prompt": self.cmd_prompt,
            # System 18: Item Repair
            "repair": self.cmd_repair,
            "fix": self.cmd_repair,
            "repairall": self.cmd_repairall,
            # System 26: Summoning / Familiars
            "summon": self.cmd_summon,
            "familiar": self.cmd_familiar,
            # System 28: Language System
            "speak": self.cmd_speak,
            "languages": self.cmd_languages,
            "lang": self.cmd_languages,
            # System 29: Swimming / Drowning
            "holdbreath": self.cmd_hold_breath,
            # System 30: Flying
            "fly": self.cmd_fly,
            "land": self.cmd_land,
            # System 32: Gambling
            "gamble": self.cmd_gamble,
            "bet": self.cmd_gamble,
            # System 33: Enchanting
            "enchant": self.cmd_enchant,
            # System 34: Item Sets
            "itemsets": self.cmd_itemsets,
            "sets": self.cmd_itemsets,
            # System 35: Reputation
            "reputation": self.cmd_reputation,
            "rep": self.cmd_reputation,
            # System 36: Remort
            "remort": self.cmd_remort,
            # System 38: Bug / Typo / Idea
            "bug": self.cmd_bug,
            "typo": self.cmd_typo,
            "idea": self.cmd_idea,
            # System 39: Ignore / Block
            "ignore": self.cmd_ignore,
            "block": self.cmd_ignore,
            # System 40: AFK Status
            "afk": self.cmd_afk,
            # System 41: Finger / Whois
            "finger": self.cmd_finger,
            "whois": self.cmd_finger,
            # System 42: Duel
            "duel": self.cmd_duel,
            "challenge": self.cmd_duel,
            # System 43: Leaderboards
            "leaderboard": self.cmd_leaderboard,
            "top": self.cmd_leaderboard,
            "rankings": self.cmd_leaderboard,
            # Class ability commands
            "rage": self.cmd_rage,
            "inspire": self.cmd_inspire,
            "turn": self.cmd_turn,
            "turnundead": self.cmd_turn,
            "wildshape": self.cmd_wildshape,
            "flurry": self.cmd_flurry,
            "smite": self.cmd_smite,
            "layonhands": self.cmd_layonhands,
            "loh": self.cmd_layonhands,
            "favoredenemy": self.cmd_favoredenemy,
            "fe": self.cmd_favoredenemy,
            # Communication commands
            "tell": self.cmd_tell,
            "whisper": self.cmd_whisper,
            "reply": self.cmd_reply,
            "shout": self.cmd_shout,
            "yell": self.cmd_shout,
            "ooc": self.cmd_ooc,
            "global": self.cmd_ooc,
            "chat": self.cmd_ooc,
            # Examine / Inspect
            "examine": self.cmd_examine,
            "exam": self.cmd_examine,
            "inspect": self.cmd_examine,
            # Affects / Buffs
            "affects": self.cmd_affects,
            "buffs": self.cmd_affects,
            # Compare
            "compare": self.cmd_compare,
            "comp": self.cmd_compare,
            # Worth / Wealth
            "worth": self.cmd_worth,
            "wealth": self.cmd_worth,
            # Body positions
            "sit": self.cmd_sit,
            "stand": self.cmd_stand,
            "kneel": self.cmd_kneel,
            # Wake
            "wake": self.cmd_wake,
            # Autosac
            "autosac": self.cmd_autosac,
            # Player title
            "title": self.cmd_title,
            # Progression chart
            "progression": self.cmd_progression,
            # Skill commands
            "balance": self.cmd_balance,
            "bluff": self.cmd_bluff,
            "climb": self.cmd_climb,
            "concentration": self.cmd_concentration,
            "decipher": self.cmd_decipher,
            "diplomacy": self.cmd_diplomacy,
            "disable": self.cmd_disable,
            "disguise": self.cmd_disguise,
            "escape": self.cmd_escape,
            "forgery": self.cmd_forgery,
            "handle": self.cmd_handle,
            "heal": self.cmd_heal,
            "intimidate": self.cmd_intimidate,
            "jump": self.cmd_jump,
            "knowledge": self.cmd_knowledge,
            "listen": self.cmd_listen,
            "movesilently": self.cmd_movesilently,
            "openlock": self.cmd_openlock,
            "perform": self.cmd_perform,
            "profession": self.cmd_profession,
            "ride": self.cmd_ride,
            "sensemotive": self.cmd_sensemotive,
            "sleight": self.cmd_sleight,
            "spellcraft": self.cmd_spellcraft,
            "spot": self.cmd_spot,
            "survival": self.cmd_survival,
            "swim": self.cmd_swim,
            "tumble": self.cmd_tumble,
            "usemagic": self.cmd_usemagic,
            "userope": self.cmd_userope,
            # Skill utility commands
            "gatherinfo": self.cmd_gatherinfo,
            "take10": self.cmd_take10,
            "take20": self.cmd_take20,
            "skilllist": self.cmd_skilllist,
            "helpfeats": self.cmd_help_feats,
            # Quest log
            "questlog": self.cmd_questlog,
            # NPC dialogue
            "talkto": self.cmd_talkto,
            # Admin player data commands
            "@backup": self.cmd_backupplayer,
            "@restore": self.cmd_restoreplayer,
            "@save": self.cmd_saveplayer,
            "@botrun": self.cmd_botrun,
        }
        # Register all social verbs dynamically
        for _verb in SOCIALS:
            self.commands[_verb] = lambda char, args, v=_verb: self.cmd_social(char, args, verb=v)

    # --- Speedwalk (System 9) ---
    def cmd_speedwalk(self, character, args):
        """speedwalk <directions> | Execute a sequence of moves, e.g. 'speedwalk nnnwws'."""
        direction_chars = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'u': 'up', 'd': 'down'}
        sequence = args.strip().lower()
        if not sequence:
            return "Usage: speedwalk <directions> (e.g. speedwalk nnnwws)"
        if not all(c in direction_chars for c in sequence):
            return "Speedwalk only accepts direction letters: n s e w u d"
        results = []
        for char in sequence:
            direction = direction_chars[char]
            result = self.cmd_move(character, direction)
            if "no exit" in result.lower() or "closed" in result.lower() or "locked" in result.lower():
                results.append(f"Stopped: {result}")
                break
            results.append(f"You move {direction} to {character.room.name}.")
        return "\n".join(results)

    # --- Alias System (System 10) ---
    def cmd_alias(self, character, args):
        """alias [name [expansion]] | List, set, or remove command aliases."""
        if not hasattr(character, 'aliases'):
            character.aliases = {}
        args = args.strip()
        if not args:
            # List all aliases
            if not character.aliases:
                return "You have no aliases defined."
            lines = ["Your aliases:"]
            for name, expansion in sorted(character.aliases.items()):
                lines.append(f"  {name} -> {expansion}")
            return "\n".join(lines)
        parts = args.split(maxsplit=1)
        name = parts[0].lower()
        if len(parts) == 1:
            # Delete alias
            if name in character.aliases:
                del character.aliases[name]
                return f"Alias '{name}' removed."
            else:
                return f"No alias named '{name}'."
        # Set alias
        expansion = parts[1]
        # Prevent aliasing over existing commands
        if name in self.commands:
            return f"Cannot alias '{name}': that is an existing command."
        if len(character.aliases) >= 20 and name not in character.aliases:
            return "You have reached the maximum of 20 aliases."
        character.aliases[name] = expansion
        return f"Alias '{name}' set to '{expansion}'."

    # --- Builder Commands ---
    def cmd_dig(self, character, args):
        """@dig <direction> <room name> | Creates a new room in the given direction, linking it to the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 1)
        if not parts or len(parts) < 2:
            return "Usage: @dig <direction> <room name>"
        direction, name = parts[0].lower(), parts[1].strip()
        # Find an unused vnum
        max_vnum = max(self.world.rooms.keys(), default=1000)
        new_vnum = max_vnum + 1
        # Create new room
        from src.room import Room
        new_room = Room(new_vnum, name, f"This is {name}.", {{}}, [], [])
        self.world.rooms[new_vnum] = new_room
        # Link exits
        character.room.exits[direction] = new_vnum
        # Add reverse exit
        reverse = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
        rev_dir = reverse.get(direction, None)
        if rev_dir:
            new_room.exits[rev_dir] = character.room.vnum
        self.world.save_rooms()
        return f"Room '{name}' created to the {direction} (vnum {new_vnum})."

    def cmd_desc(self, character, args):
        """@desc <new description> | Sets the description of the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @desc <new description>"
        character.room.description = args.strip()
        self.world.save_rooms()
        return "Room description updated."

    def cmd_exit(self, character, args):
        """@exit <direction> <vnum> | Creates or changes an exit in the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 1)
        if not parts or len(parts) < 2:
            return "Usage: @exit <direction> <vnum>"
        direction, vnum_str = parts[0].lower(), parts[1].strip()
        try:
            vnum = int(vnum_str)
        except ValueError:
            return "Vnum must be a number."
        if vnum not in self.world.rooms:
            return f"No room with vnum {vnum}."
        character.room.exits[direction] = vnum
        self.world.save_rooms()
        return f"Exit '{direction}' set to room {vnum}."

    def cmd_flag(self, character, args):
        """@flag <flag> [on|off] | Sets or clears a flag on the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split()
        if not parts:
            return "Usage: @flag <flag> [on|off]"
        flag = parts[0].lower()
        action = parts[1].lower() if len(parts) > 1 else "on"
        if action == "on":
            if flag not in character.room.flags:
                character.room.flags.append(flag)
            self.world.save_rooms()
            return f"Flag '{flag}' set on this room."
        elif action == "off":
            if flag in character.room.flags:
                character.room.flags.remove(flag)
            self.world.save_rooms()
            return f"Flag '{flag}' removed from this room."
        else:
            return "Usage: @flag <flag> [on|off]"

    def cmd_recall(self, character, args):
        """Teleports the player to the center room of the chapel (Central Aetherial Altar)."""
        death_check = self._check_incapacitated(character)
        if death_check:
            return "You are dead! Use 'respawn' instead of recall."
        center_vnum = 1000
        if center_vnum not in self.world.rooms:
            return "Recall failed: Chapel center room not found."
        # Remove from current room
        if character in character.room.players:
            character.room.players.remove(character)
        # Move to center room
        character.room = self.world.rooms[center_vnum]
        character.room.players.append(character)
        return f"You are enveloped in shimmering light and find yourself at the {character.room.name}."

    # --- Immortal/Builder command helpers ---
    def _immortal_only(self, character):
        if not getattr(character, 'is_immortal', False):
            return "Command restricted to immortals!"
        return None

    def _find_player_by_name(self, name):
        for player in self.world.players:
            if player.name.lower() == name.lower():
                return player
        return None

    def _set_numeric_stat(self, character, args, attr, min_val, max_val, label):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split()
        if len(parts) < 2:
            return f"Usage: @set{label.lower()} <player> <value>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        try:
            value = int(parts[1])
        except ValueError:
            return f"{label} must be a number."
        if value < min_val or value > max_val:
            return f"{label} must be between {min_val} and {max_val}."
        setattr(target, attr, value)
        return f"{target.name}'s {label} set to {value}."

    def _set_string_field(self, character, args, attr, valid_values, label):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 1)
        if len(parts) < 2:
            return f"Usage: @set{label.lower()} <player> <value>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        value = parts[1].strip()
        if valid_values is not None:
            matched = next((v for v in valid_values if v.lower() == value.lower()), None)
            if not matched:
                return f"Invalid {label}. Valid: {', '.join(valid_values)}"
            value = matched
        setattr(target, attr, value)
        return f"{target.name}'s {label} set to {value}."

    def _set_boolean_flag(self, character, args, attr, label):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split()
        if len(parts) < 2:
            return f"Usage: @set{label.lower()} <player> [on|off]"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        toggle = parts[1].lower()
        if toggle not in ("on", "off"):
            return "Value must be 'on' or 'off'."
        setattr(target, attr, toggle == "on")
        return f"{target.name}'s {label} set to {toggle}."

    # --- Immortal Setter Commands: Numeric Stats ---
    def cmd_sethp(self, character, args):
        return self._set_numeric_stat(character, args, "hp", -10, 9999, "HP")

    def cmd_setmove(self, character, args):
        return self._set_numeric_stat(character, args, "move", 0, 9999, "Move")

    def cmd_setac(self, character, args):
        return self._set_numeric_stat(character, args, "ac", -20, 99, "AC")

    def cmd_setxp(self, character, args):
        return self._set_numeric_stat(character, args, "xp", 0, 999999, "XP")

    def cmd_setgold(self, character, args):
        return self._set_numeric_stat(character, args, "gold", 0, 999999, "Gold")

    def cmd_setstr(self, character, args):
        return self._set_numeric_stat(character, args, "str_score", 1, 50, "Str")

    def cmd_setdex(self, character, args):
        return self._set_numeric_stat(character, args, "dex_score", 1, 50, "Dex")

    def cmd_setcon(self, character, args):
        return self._set_numeric_stat(character, args, "con_score", 1, 50, "Con")

    def cmd_setint(self, character, args):
        return self._set_numeric_stat(character, args, "int_score", 1, 50, "Int")

    def cmd_setwis(self, character, args):
        return self._set_numeric_stat(character, args, "wis_score", 1, 50, "Wis")

    def cmd_setcha(self, character, args):
        return self._set_numeric_stat(character, args, "cha_score", 1, 50, "Cha")

    def cmd_setlevel(self, character, args):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split()
        if len(parts) < 2:
            return "Usage: @setlevel <player> <value>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        try:
            value = int(parts[1])
        except ValueError:
            return "Level must be a number."
        if value < 1 or value > 20:
            return "Level must be between 1 and 20."
        target.set_level(value)
        target.level = value
        return f"{target.name}'s Level set to {value}."

    # --- Immortal Setter Commands: String Identity ---
    def cmd_setrace(self, character, args):
        return self._set_string_field(character, args, "race", VALID_RACES, "Race")

    def cmd_setclass(self, character, args):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Usage: @setclass <player> <class>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        value = parts[1].strip()
        matched = next((v for v in VALID_CLASSES if v.lower() == value.lower()), None)
        if not matched:
            return f"Invalid Class. Valid: {', '.join(VALID_CLASSES)}"
        target.set_class(matched)
        return f"{target.name}'s Class set to {matched}."

    def cmd_setalignment(self, character, args):
        return self._set_string_field(character, args, "alignment", VALID_ALIGNMENTS, "Alignment")

    def cmd_setdeity(self, character, args):
        return self._set_string_field(character, args, "deity", None, "Deity")

    def cmd_settitle(self, character, args):
        return self._set_string_field(character, args, "title", None, "Title")

    def cmd_setaffinity(self, character, args):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Usage: @setaffinity <player> <affinity>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        value = parts[1].strip()
        if value.lower() == "none":
            target.elemental_affinity = None
            return f"{target.name}'s Affinity set to None."
        matched = next((v for v in VALID_AFFINITIES if v.lower() == value.lower()), None)
        if not matched:
            return f"Invalid Affinity. Valid: {', '.join(VALID_AFFINITIES)}, None"
        target.elemental_affinity = matched
        return f"{target.name}'s Affinity set to {matched}."

    # --- Immortal Setter Commands: Boolean Toggles ---
    def cmd_setimmortal(self, character, args):
        return self._set_boolean_flag(character, args, "is_immortal", "Immortal")

    def cmd_setai(self, character, args):
        return self._set_boolean_flag(character, args, "is_ai", "AI")

    # --- Immortal Setter Commands: List/Dict Modifiers ---
    def cmd_setfeat(self, character, args):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @setfeat <player> add|remove <feat>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        action = parts[1].lower()
        feat_name = parts[2].strip()
        if action == "add":
            if not hasattr(target, 'feats'):
                target.feats = []
            target.feats.append(feat_name)
            return f"Feat '{feat_name}' added to {target.name}."
        elif action == "remove":
            if not hasattr(target, 'feats'):
                return f"{target.name} has no feats."
            match = next((f for f in target.feats if f.lower() == feat_name.lower()), None)
            if not match:
                return f"{target.name} does not have feat '{feat_name}'."
            target.feats.remove(match)
            return f"Feat '{match}' removed from {target.name}."
        else:
            return "Usage: @setfeat <player> add|remove <feat>"

    def cmd_setskill(self, character, args):
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split()
        if len(parts) < 3:
            return "Usage: @setskill <player> <skill_name> <rank>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        try:
            rank = int(parts[-1])
        except ValueError:
            return "Rank must be a number."
        skill_name = " ".join(parts[1:-1])
        if not hasattr(target, 'skills') or target.skills is None:
            target.skills = {}
        if rank == 0:
            target.skills.pop(skill_name, None)
            return f"Skill '{skill_name}' removed from {target.name}."
        target.skills[skill_name] = rank
        return f"{target.name}'s skill '{skill_name}' set to rank {rank}."

    # --- Builder Room Commands ---
    def cmd_setname(self, character, args):
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setname <new name>"
        character.room.name = args.strip()
        self.world.save_rooms()
        return f"Room name set to '{character.room.name}'."

    def cmd_setterrain(self, character, args):
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setterrain <type>"
        character.room.terrain = args.strip()
        self.world.save_rooms()
        return f"Room terrain set to '{character.room.terrain}'."

    def cmd_setweather(self, character, args):
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setweather <type>"
        character.room.weather = args.strip()
        self.world.save_rooms()
        return f"Room weather set to '{character.room.weather}'."

    # =========================================================================
    # New Immortal/Builder Commands (Phase 3)
    # =========================================================================

    def cmd_setmob(self, character, args):
        """@setmob <vnum> <field> <value> | Edit a mob template."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @setmob <vnum> <field> <value>"
        try:
            vnum = int(parts[0])
        except ValueError:
            return "Vnum must be a number."
        mob = self.world.mobs.get(vnum)
        if not mob:
            return f"No mob with vnum {vnum}."
        field, value = parts[1].lower(), parts[2]
        valid_fields = ["name", "level", "ac", "cr", "type_", "alignment", "description", "flags"]
        if field not in valid_fields:
            return f"Invalid field '{field}'. Valid: {', '.join(valid_fields)}"
        if field in ("level", "ac"):
            try:
                value = int(value)
            except ValueError:
                return f"{field} must be a number."
        elif field == "cr":
            try:
                value = float(value)
            except ValueError:
                return "CR must be a number."
        elif field == "flags":
            value = [f.strip() for f in value.split(",")]
        setattr(mob, field, value)
        self.world.save_mobs()
        return f"Mob {vnum} '{mob.name}' field '{field}' updated."

    def cmd_setitem(self, character, args):
        """@setitem <vnum> <field> <value> | Edit an item template."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @setitem <vnum> <field> <value>"
        try:
            vnum = int(parts[0])
        except ValueError:
            return "Vnum must be a number."
        if not hasattr(self.world, 'items'):
            self.world.items = {}
        item = self.world.items.get(vnum)
        if not item:
            return f"No item with vnum {vnum}."
        field, value = parts[1].lower(), parts[2]
        valid_fields = ["name", "item_type", "weight", "value", "description", "slot", "magical", "ac_bonus", "material"]
        if field not in valid_fields:
            return f"Invalid field '{field}'. Valid: {', '.join(valid_fields)}"
        if field in ("weight", "value", "ac_bonus"):
            try:
                value = int(value)
            except ValueError:
                return f"{field} must be a number."
        elif field == "magical":
            value = value.lower() in ("true", "yes", "on", "1")
        setattr(item, field, value)
        self.world.save_items()
        return f"Item {vnum} '{item.name}' field '{field}' updated."

    def cmd_setreset(self, character, args):
        """@setreset <vnum> <seconds|off> | Set respawn timer for a mob."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split()
        if len(parts) < 2:
            return "Usage: @setreset <vnum> <seconds|off>"
        try:
            vnum = int(parts[0])
        except ValueError:
            return "Vnum must be a number."
        if vnum not in self.world.mobs:
            return f"No mob with vnum {vnum}."
        if parts[1].lower() == "off":
            get_spawn_manager().set_respawn_time(vnum, 0)
            return f"Respawn disabled for mob {vnum}."
        try:
            seconds = int(parts[1])
        except ValueError:
            return "Seconds must be a number or 'off'."
        get_spawn_manager().set_respawn_time(vnum, seconds)
        return f"Respawn timer for mob {vnum} set to {seconds}s."

    def cmd_setspells(self, character, args):
        """@setspells <player> add|remove <spell> | Modify a player's spells known."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @setspells <player> add|remove <spell>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        action = parts[1].lower()
        spell_name = parts[2].strip()
        from src.spells import get_spell
        spell = get_spell(spell_name)
        if not spell:
            return f"No such spell: '{spell_name}'."
        if action == "add":
            spell_level = str(spell.level)
            if spell_level not in target.spells_known:
                target.spells_known[spell_level] = []
            if spell.name not in target.spells_known[spell_level]:
                target.spells_known[spell_level].append(spell.name)
            return f"Spell '{spell.name}' added to {target.name}'s spells known (level {spell_level})."
        elif action == "remove":
            for lvl, spells in target.spells_known.items():
                match = next((s for s in spells if s.lower() == spell_name.lower()), None)
                if match:
                    spells.remove(match)
                    return f"Spell '{match}' removed from {target.name}'s spells known."
            return f"{target.name} does not know spell '{spell_name}'."
        return "Usage: @setspells <player> add|remove <spell>"

    def cmd_setinventory(self, character, args):
        """@setinventory <player> add|remove <vnum_or_name> | Modify a player's inventory."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @setinventory <player> add|remove <vnum_or_name>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        action = parts[1].lower()
        identifier = parts[2].strip()
        if action == "add":
            from src.items import get_item_by_vnum, Item
            try:
                vnum = int(identifier)
                template = get_item_by_vnum(vnum)
            except ValueError:
                template = None
            if not template:
                return f"No item template found for '{identifier}'."
            new_item = Item.from_dict(template.to_dict())
            target.inventory.append(new_item)
            return f"Item '{new_item.name}' added to {target.name}'s inventory."
        elif action == "remove":
            match = next((i for i in target.inventory if i.name.lower() == identifier.lower()), None)
            if not match:
                return f"{target.name} does not have '{identifier}' in inventory."
            target.inventory.remove(match)
            return f"Item '{match.name}' removed from {target.name}'s inventory."
        return "Usage: @setinventory <player> add|remove <vnum_or_name>"

    def cmd_setequipment(self, character, args):
        """@setequipment <player> <slot> <vnum|none> | Set a player's equipment slot."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split()
        if len(parts) < 3:
            return "Usage: @setequipment <player> <slot> <vnum|none>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        from src.character import EQUIPMENT_SLOTS
        slot = parts[1].lower()
        if slot not in EQUIPMENT_SLOTS:
            return f"Invalid slot '{slot}'. Valid: {', '.join(EQUIPMENT_SLOTS)}"
        value = parts[2].lower()
        if value == "none":
            target.equipment[slot] = None
            return f"{target.name}'s {slot} slot cleared."
        try:
            vnum = int(value)
        except ValueError:
            return "Value must be a vnum (number) or 'none'."
        from src.items import get_item_by_vnum, Item
        template = get_item_by_vnum(vnum)
        if not template:
            return f"No item template with vnum {vnum}."
        new_item = Item.from_dict(template.to_dict())
        target.equipment[slot] = new_item
        return f"{target.name}'s {slot} slot set to '{new_item.name}'."

    def cmd_setprompt(self, character, args):
        """@setprompt <player> <template> | Set a player's prompt template."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Usage: @setprompt <player> <template>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        target.set_prompt(parts[1])
        return f"{target.name}'s prompt set to: {parts[1]}"

    def cmd_setpassword(self, character, args):
        """@setpassword <player> <new_password> | Set a player's password."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Usage: @setpassword <player> <new_password>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        import hashlib
        hashed = hashlib.sha256(parts[1].encode()).hexdigest()
        target.hashed_password = hashed
        target.save()
        return f"{target.name}'s password has been updated."

    def cmd_setdoor(self, character, args):
        """@setdoor <direction> <property> <value> | Set door properties on an exit."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split()
        if len(parts) < 3:
            return "Usage: @setdoor <direction> <property> <value>"
        direction = parts[0].lower()
        prop = parts[1].lower()
        value = parts[2].lower()
        if direction not in character.room.exits:
            return f"No exit '{direction}' in this room."
        valid_props = ["hidden", "locked", "key_vnum"]
        if prop not in valid_props:
            return f"Invalid property '{prop}'. Valid: {', '.join(valid_props)}"
        # Convert simple int exit to dict format if needed
        exit_data = character.room.exits[direction]
        if not isinstance(exit_data, dict):
            exit_data = {"room": exit_data}
            character.room.exits[direction] = exit_data
        if prop in ("hidden", "locked"):
            if value not in ("on", "off"):
                return f"Value for '{prop}' must be 'on' or 'off'."
            exit_data[prop] = (value == "on")
        elif prop == "key_vnum":
            try:
                exit_data["key_vnum"] = int(value)
            except ValueError:
                return "key_vnum must be a number."
        self.world.save_rooms()
        return f"Exit '{direction}' property '{prop}' set to {value}."

    def cmd_setroom(self, character, args):
        """@setroom <field> <value> | Edit the current room's properties."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setroom <field> <value>"
        parts = args.split(None, 1)
        field = parts[0].lower()
        value = parts[1] if len(parts) > 1 else ""
        if field == "description":
            if not value:
                return "Usage: @setroom description <text>"
            character.room.description = value
            self.world.save_rooms()
            return "Room description updated."
        elif field == "flags":
            flag_parts = value.split()
            if len(flag_parts) < 2 or flag_parts[0].lower() not in ("add", "remove"):
                return "Usage: @setroom flags add|remove <flag>"
            action = flag_parts[0].lower()
            flag = flag_parts[1].lower()
            if action == "add":
                if flag not in character.room.flags:
                    character.room.flags.append(flag)
                self.world.save_rooms()
                return f"Flag '{flag}' added to room."
            else:
                if flag in character.room.flags:
                    character.room.flags.remove(flag)
                self.world.save_rooms()
                return f"Flag '{flag}' removed from room."
        return f"Invalid field '{field}'. Valid: description, flags"

    def cmd_setlight(self, character, args):
        """@setlight <level> | Set the light level of the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setlight <level>"
        level = args.strip().lower()
        if level not in VALID_LIGHT_LEVELS:
            return f"Invalid light level. Valid: {', '.join(VALID_LIGHT_LEVELS)}"
        character.room.light = level
        self.world.save_rooms()
        return f"Room light level set to '{level}'."

    def cmd_setnote(self, character, args):
        """@setnote <text> | Set builder notes for the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setnote <text>"
        character.room.builder_notes = args.strip()
        self.world.save_rooms()
        return "Builder notes set for this room."

    def cmd_setowner(self, character, args):
        """@setowner <player_name> | Set the owner of the current room."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setowner <player_name>"
        character.room.owner = args.strip()
        self.world.save_rooms()
        return f"Room owner set to '{args.strip()}'."

    def cmd_setcolor(self, character, args):
        """@setcolor <player> on|off | Toggle color for a player."""
        return self._set_boolean_flag(character, args, "color_enabled", "Color")

    def cmd_setemail(self, character, args):
        """@setemail <player> <email> | Set a player's email."""
        return self._set_string_field(character, args, "email", None, "Email")

    def cmd_setresist(self, character, args):
        """@setresist <player> <type> <value> | Set a player's damage resistance."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split()
        if len(parts) < 3:
            return "Usage: @setresist <player> <type> <value>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        dmg_type = parts[1].lower()
        if dmg_type not in VALID_DAMAGE_TYPES:
            return f"Invalid damage type '{dmg_type}'. Valid: {', '.join(VALID_DAMAGE_TYPES)}"
        try:
            value = int(parts[2])
        except ValueError:
            return "Value must be a number."
        if not hasattr(target, 'resistances'):
            target.resistances = {}
        if value == 0:
            target.resistances.pop(dmg_type, None)
            return f"{target.name}'s {dmg_type} resistance removed."
        target.resistances[dmg_type] = value
        return f"{target.name}'s {dmg_type} resistance set to {value}."

    def cmd_setimmune(self, character, args):
        """@setimmune <player> add|remove <type> | Modify a player's immunities."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @setimmune <player> add|remove <type>"
        target = self._find_player_by_name(parts[0])
        if not target:
            return f"Player '{parts[0]}' not found."
        action = parts[1].lower()
        dmg_type = parts[2].strip().lower()
        if dmg_type not in VALID_DAMAGE_TYPES:
            return f"Invalid damage type '{dmg_type}'. Valid: {', '.join(VALID_DAMAGE_TYPES)}"
        if not hasattr(target, 'immunities'):
            target.immunities = []
        if action == "add":
            if dmg_type not in target.immunities:
                target.immunities.append(dmg_type)
            return f"{target.name} is now immune to {dmg_type}."
        elif action == "remove":
            if dmg_type in target.immunities:
                target.immunities.remove(dmg_type)
                return f"{target.name}'s {dmg_type} immunity removed."
            return f"{target.name} is not immune to {dmg_type}."
        return "Usage: @setimmune <player> add|remove <type>"

    def cmd_build(self, character, args):
        """@build [on|off] | Toggle build mode."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not hasattr(character, 'build_mode'):
            character.build_mode = False
        if not args.strip():
            character.build_mode = not character.build_mode
        elif args.strip().lower() == "on":
            character.build_mode = True
        elif args.strip().lower() == "off":
            character.build_mode = False
        else:
            return "Usage: @build [on|off]"
        status = "ON" if character.build_mode else "OFF"
        return f"Build mode is now {status}."

    def cmd_setarea(self, character, args):
        """@setarea <field> <value> | Set area metadata for the current room's area."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Usage: @setarea <field> <value>"
        field = parts[0].lower()
        value = parts[1].strip()
        valid_fields = ["name", "level_range", "author", "description"]
        if field not in valid_fields:
            return f"Invalid field '{field}'. Valid: {', '.join(valid_fields)}"
        area_key = getattr(character.room, 'area_file', None) or "default"
        if area_key not in self.world.area_meta:
            self.world.area_meta[area_key] = {}
        self.world.area_meta[area_key][field] = value
        self.world.save_area_meta()
        return f"Area '{area_key}' field '{field}' set to '{value}'."

    def cmd_setzone(self, character, args):
        """@setzone <start_vnum> <end_vnum> <name> | Define a vnum zone."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 2)
        if len(parts) < 3:
            return "Usage: @setzone <start_vnum> <end_vnum> <name>"
        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError:
            return "Start and end vnums must be numbers."
        if start > end:
            return "Start vnum must be less than or equal to end vnum."
        name = parts[2].strip()
        self.world.zones.append({"name": name, "vnum_start": start, "vnum_end": end})
        self.world.save_zones()
        return f"Zone '{name}' created (vnums {start}-{end})."

    def cmd_sethelp(self, character, args):
        """@sethelp <topic> <text> | Create or update a help topic."""
        check = self._immortal_only(character)
        if check:
            return check
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Usage: @sethelp <topic> <text>"
        topic = parts[0].lower()
        text = parts[1].strip()
        self.world.help_topics[topic] = text
        self.world.save_help_data()
        return f"Help topic '{topic}' saved."

    def cmd_setvnum(self, character, args):
        """@setvnum <new_vnum> | Change the current room's vnum."""
        if not getattr(character, 'is_builder', False):
            return "Permission denied: You are not a builder."
        if not args.strip():
            return "Usage: @setvnum <new_vnum>"
        try:
            new_vnum = int(args.strip())
        except ValueError:
            return "Vnum must be a number."
        if new_vnum in self.world.rooms:
            return f"Room with vnum {new_vnum} already exists."
        old_vnum = character.room.vnum
        room = character.room
        # Update the rooms dict
        del self.world.rooms[old_vnum]
        room.vnum = new_vnum
        self.world.rooms[new_vnum] = room
        # Update all exits in other rooms that point to old_vnum
        for r in self.world.rooms.values():
            for direction, exit_data in list(r.exits.items()):
                if isinstance(exit_data, dict):
                    if exit_data.get("room") == old_vnum:
                        exit_data["room"] = new_vnum
                elif exit_data == old_vnum:
                    r.exits[direction] = new_vnum
        # Update mob room_vnum references
        for mob in self.world.mobs.values():
            if getattr(mob, 'room_vnum', None) == old_vnum:
                mob.room_vnum = new_vnum
        self.world.save_rooms()
        self.world.save_mobs()
        return f"Room vnum changed from {old_vnum} to {new_vnum}."

    def cmd_spells(self, character, args):
        lines = ["Spells Known and Spells Per Day:"]
        spellcasting = character.get_spellcasting_info() if hasattr(character, 'get_spellcasting_info') else None
        if spellcasting:
            lines.append(f"Spellcasting Type: {spellcasting.get('type','-')}, Starts at Level: {spellcasting.get('start_level','-')}")
        # Spells known: dict of level -> list of spell names
        spells_known = getattr(character, 'spells_known', {})
        if spells_known:
            lines.append("Spells Known:")
            for lvl in sorted(spells_known.keys()):
                spell_list = spells_known[lvl]
                lines.append(f"  Level {lvl}: {', '.join(spell_list) if spell_list else 'None'}")
        else:
            lines.append("Spells Known: None")
        # Spells per day: dict of level -> int
        spells_per_day = getattr(character, 'spells_per_day', {})
        if spells_per_day:
            lines.append("Spells Per Day:")
            for lvl in sorted(spells_per_day.keys()):
                lines.append(f"  Level {lvl}: {spells_per_day[lvl]}")
        else:
            lines.append("Spells Per Day: None")
        return "\n".join(lines)

    def cmd_spellinfo(self, character, args):
        """Get detailed information about a specific spell."""
        from src.spells import describe_spell, get_spell
        if not args:
            return "Usage: spellinfo <spell name>"
        spell = get_spell(args)
        if not spell:
            return f"Unknown spell: {args}"
        return describe_spell(args)

    def cmd_spellbook(self, character, args):
        """List all spells available to your class organized by level."""
        from src.spells import get_spells_by_level, get_spell_count
        char_class = getattr(character, 'char_class', None)
        if not char_class:
            return "You have no class to learn spells from."

        # Check if class can cast spells
        from src.classes import CLASSES
        class_data = CLASSES.get(char_class, {})
        spellcasting = class_data.get('spellcasting')
        if not spellcasting:
            return f"{char_class}s do not cast spells."

        lines = [f"=== {char_class} Spellbook ==="]
        lines.append(f"Spellcasting: {spellcasting.get('type', 'Unknown').title()}")

        max_spell_level = min(9, (character.level + 1) // 2)  # Rough approximation

        for spell_level in range(0, max_spell_level + 1):
            spells = get_spells_by_level(char_class, spell_level)
            if spells:
                level_name = "Cantrips/Orisons" if spell_level == 0 else f"Level {spell_level}"
                lines.append(f"\n{level_name}:")
                for spell in spells:
                    lines.append(f"  {spell.name} - {spell.school.value}")

        lines.append(f"\nTotal spells in database: {get_spell_count()}")
        return "\n".join(lines)

    def cmd_domains(self, character, args):
        """Show domain spells and powers for divine casters."""
        from src.spells import get_domain_spells, get_domain_power, DOMAIN_DATA
        char_class = getattr(character, 'char_class', None)

        if char_class != "Cleric":
            return "Only Clerics have domains."

        domains = getattr(character, 'domains', [])
        if not domains:
            # Show available domains
            lines = ["You have not chosen your domains yet."]
            lines.append("\nAvailable Domains:")
            for domain_name in sorted(DOMAIN_DATA.keys()):
                power = get_domain_power(domain_name)
                lines.append(f"  {domain_name}: {power[:60]}...")
            return "\n".join(lines)

        lines = ["=== Your Domains ==="]
        for domain in domains:
            lines.append(f"\n--- {domain} Domain ---")
            power = get_domain_power(domain)
            lines.append(f"Granted Power: {power}")
            lines.append("Domain Spells:")
            domain_spells = get_domain_spells(domain)
            for level, spell_name in sorted(domain_spells.items()):
                lines.append(f"  {level}: {spell_name}")

        return "\n".join(lines)

    def cmd_prepare(self, character, args):
        """Prepare (memorize) a spell for prepared casters."""
        from src.spells import get_spell
        if not args:
            return "Usage: prepare <spell name>"

        # Check if character is a prepared caster
        char_class = getattr(character, 'char_class', None)
        spellcasting = character.get_spellcasting_info() if hasattr(character, 'get_spellcasting_info') else None

        if not spellcasting or spellcasting.get('type', '').lower() != 'prepared':
            # Wizards and Clerics are prepared, Sorcerers and Bards are spontaneous
            if char_class in ("Sorcerer", "Bard"):
                return f"As a {char_class}, you cast spells spontaneously and don't need to prepare them."
            elif char_class not in ("Wizard", "Cleric", "Druid", "Paladin", "Ranger"):
                return "You cannot prepare spells."

        spell = get_spell(args)
        if not spell:
            return f"Unknown spell: {args}"

        # Check if class can cast this spell
        if char_class not in spell.level:
            return f"{char_class}s cannot cast {spell.name}."

        spell_level = spell.level[char_class]

        # Initialize prepared_spells if needed
        if not hasattr(character, 'prepared_spells'):
            character.prepared_spells = {}
        if spell_level not in character.prepared_spells:
            character.prepared_spells[spell_level] = []

        # Check if we have slots available
        spells_per_day = getattr(character, 'spells_per_day', {})
        max_prepared = spells_per_day.get(spell_level, 0)
        current_prepared = len(character.prepared_spells.get(spell_level, []))

        if current_prepared >= max_prepared:
            return f"You cannot prepare any more level {spell_level} spells today. (Max: {max_prepared})"

        character.prepared_spells[spell_level].append(spell.name)
        return f"You prepare {spell.name} (level {spell_level}). Prepared: {current_prepared + 1}/{max_prepared}"

    def cmd_skills(self, character, args):
        lines = ["Skills, Feats, and Class Features:"]
        # Skills
        skills = getattr(character, 'skills', {})
        if hasattr(character, 'get_class_skills'):
            class_skills = character.get_class_skills()
            lines.append(f"Class Skills: {', '.join(class_skills) if class_skills else 'None'}")
        if skills:
            lines.append("Skills:")
            for skill, value in skills.items():
                lines.append(f"  {skill}: {value}")
        else:
            lines.append("Skills: None")
        # Feats
        feats = getattr(character, 'feats', [])
        if feats:
            lines.append("Feats:")
            for feat in feats:
                lines.append(f"  {feat}")
        else:
            lines.append("Feats: None")
        # Class Features
        if hasattr(character, 'get_class_features'):
            features = character.get_class_features()
            if features:
                lines.append("Class Features:")
                for feature in features:
                    lines.append(f"  {feature}")
            else:
                lines.append("Class Features: None")
        return "\n".join(lines)

    def cmd_score(self, character, args):
        W = 78  # inner width between the | borders
        bar = "+" + "-" * W + "+"

        def row(text):
            """Fixed-width row — truncate or pad to exactly W chars."""
            t = text[:W]
            return "|" + t + " " * (W - len(t)) + "|"

        # Helper to truncate strings
        def t(s, n):
            s = str(s or '')
            return s[:n]

        lines = []
        lines.append(bar)
        lines.append(row(f" Name: {t(character.name, 18):<18}  Level: {character.level:<3}  Title: {t(character.title, 26):<26}"))
        lines.append(row(f" Race: {t(character.race, 18):<18}  Class: {t(getattr(character, 'char_class', 'Adventurer'), 18):<18}"))
        lines.append(bar)

        alignment = t(getattr(character, 'alignment', 'Unaligned'), 18)
        deity = t(getattr(character, 'deity', 'None'), 30)
        lines.append(row(f" Alignment: {alignment:<18}  Deity: {deity:<30}"))
        elem = t(character.elemental_affinity or 'None', 10)
        size = t(getattr(character, 'size', 'Medium'), 8)
        # Show racial speed (from race data), not move points
        _race_speed = 30
        try:
            from src.races import RACES
            _rdata = RACES.get(character.race, {})
            _race_speed = _rdata.get('speed', 30)
        except Exception:
            pass
        speed = str(_race_speed)
        imm = 'Yes' if character.is_immortal else 'No'
        lines.append(row(f" Size: {size:<8}  Speed: {speed:<4} ft  Immortal: {imm:<3}  Element: {elem:<10}"))
        lines.append(bar)

        # Combat
        hp_str = f"{character.hp}/{character.max_hp}"
        tac = getattr(character, 'touch_ac', character.ac)
        fac = getattr(character, 'flat_ac', character.ac)
        lines.append(row(f" HP: {hp_str:<8}  AC: {character.ac:<3}  Touch: {tac:<3}  Flat: {fac:<3}"))
        bab = getattr(character, 'bab', (character.level * 3) // 4)
        grapple = bab + (character.str_score - 10) // 2
        lines.append(row(f" BAB: {bab:<3}  Grapple: {grapple:<3}"))

        def calc_save(save_type):
            class_data = character.get_class_data()
            prog = class_data.get('save_progression', {}).get(save_type, 'poor')
            lvl = getattr(character, 'class_level', character.level)
            base = (2 + lvl // 2) if prog == 'good' else (lvl // 3)
            mod_attr = {'fort': 'con_score', 'ref': 'dex_score', 'will': 'wis_score'}
            mod = (getattr(character, mod_attr[save_type], 10) - 10) // 2
            return base + mod

        fort, ref, will = calc_save('fort'), calc_save('ref'), calc_save('will')
        lines.append(row(f" Saves — Fort: {fort:<3}  Ref: {ref:<3}  Will: {will:<3}"))
        lines.append(bar)

        # Stats
        lines.append(row(f" STR: {character.str_score:<4} DEX: {character.dex_score:<4} CON: {character.con_score:<4} INT: {character.int_score:<4} WIS: {character.wis_score:<4} CHA: {character.cha_score:<4}"))
        lines.append(bar)

        # XP, Gold
        gold = getattr(character, 'gold', 0)
        lines.append(row(f" XP: {character.xp:<10}  Gold: {gold:<10} gp"))

        # Resistances
        resists = getattr(character, 'resistances', {})
        if isinstance(resists, dict) and resists:
            res_str = ', '.join(f"{k} {v}" for k, v in resists.items())
        elif isinstance(resists, list) and resists:
            res_str = ', '.join(str(r) for r in resists)
        else:
            res_str = 'None'
        lines.append(row(f" Resistances: {t(res_str, 60):<60}"))

        immun = getattr(character, 'immunities', [])
        imm_str = ', '.join(str(i) for i in immun) if immun else 'None'
        lines.append(row(f" Immunities:  {t(imm_str, 60):<60}"))
        lines.append(bar)

        # Guild/Faction
        guild = getattr(character, 'guild_name', None)
        if guild:
            rank = getattr(character, 'guild_rank', '')
            lines.append(row(f" Faction: {t(guild, 25):<25}  Rank: {t(rank, 20):<20}"))
            lines.append(bar)

        # Active conditions
        effects = getattr(character, 'active_effects', [])
        if effects:
            lines.append(row(f" Conditions: {t(', '.join(str(e) for e in effects), 62):<62}"))
            lines.append(bar)

        return "\n".join(lines)

    def cmd_companion(self, character, args):
        """Manage your animal companion.
        Usage: companion              - show companion status
               companion call <name>  - call a companion mob from the room
               companion dismiss      - release your current companion
               companion attack <target> - order companion to attack a target
               companion stay        - companion stays in place
               companion follow      - companion follows you
        """
        companion = getattr(character, 'companion', None)

        if not args:
            # Show companion status
            if not companion:
                return "You have no companion."
            lines = [f"Companion: {companion.name}"]
            lines.append(f"  HP: {getattr(companion, 'hp', '?')}/{getattr(companion, 'max_hp', '?')}")
            following = getattr(companion, '_companion_following', True)
            lines.append(f"  Status: {'following' if following else 'staying'}")
            return "\n".join(lines)

        parts = args.split(None, 1)
        sub = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        if sub == "call":
            if not rest:
                return "Call which companion? Usage: companion call <mob name>"
            # Check Handle Animal skill (trained-only, DC 15)
            result = character.skill_check("Handle Animal")
            if isinstance(result, str):
                return f"You lack the training to call a companion. ({result})"
            # Find a mob with 'companion' flag in the room
            target_name = rest.lower()
            found = None
            for mob in getattr(character.room, 'mobs', []):
                if getattr(mob, 'alive', True) and target_name in mob.name.lower():
                    if 'companion' in getattr(mob, 'flags', []):
                        found = mob
                        break
            if not found:
                return f"You don't see a suitable companion named '{rest}' here."
            if result < 15:
                return f"You fail to bond with {found.name}. (Handle Animal check: {result} vs DC 15)"
            # Dismiss previous companion first
            if companion:
                character.room.mobs.append(companion)
            character.companion = found
            found._companion_following = True
            character.room.mobs.remove(found)
            return f"You bond with {found.name}. They will now follow you."

        elif sub == "dismiss":
            if not companion:
                return "You have no companion to dismiss."
            character.room.mobs.append(companion)
            character.companion = None
            return f"You release {companion.name}. They wander off."

        elif sub == "attack":
            if not companion:
                return "You have no companion."
            if not rest:
                return "Attack what? Usage: companion attack <target>"
            # Find target in room
            target_name = rest.lower()
            target = None
            for mob in getattr(character.room, 'mobs', []):
                if getattr(mob, 'alive', True) and target_name in mob.name.lower():
                    target = mob
                    break
            if not target:
                return f"You don't see '{rest}' here."
            # Set companion's combat target (mob object duck-typed)
            companion._companion_target = target
            return f"{companion.name} lunges at {target.name}!"

        elif sub in ("stay", "follow"):
            if not companion:
                return "You have no companion."
            companion._companion_following = (sub == "follow")
            return f"{companion.name} will now {'follow you' if sub == 'follow' else 'stay here'}."

        return "Usage: companion [call <name>|dismiss|attack <target>|stay|follow]"

    def cmd_questpage(self, character, args):
        lines = ["Quest Log and Reputation:"]
        # Reputation/Standing
        rep = getattr(character, 'reputation', {})
        if rep:
            lines.append("Reputation/Standing:")
            for faction, value in rep.items():
                lines.append(f"  {faction}: {value}")
        else:
            lines.append("Reputation/Standing: None")
        # Quest log
        quests = getattr(character, 'quest_log', [])
        if quests:
            lines.append("Quest Log:")
            for quest in quests:
                lines.append(f"  {quest}")
        else:
            lines.append("Quest Log: None")
        return "\n".join(lines)

    def cmd_help(self, character, args):
        topic = args.strip().lower() if args else None

        # Check data-driven help topics first
        if topic and hasattr(self, 'world') and self.world and hasattr(self.world, 'help_topics'):
            if topic in self.world.help_topics:
                return self.world.help_topics[topic]

        if topic == "prompt":
            return (
                "Prompt Customization:\n"
                "You can change your prompt using the 'setprompt' command.\n"
                "Example: setprompt AC %a HP %h/%H EXP %x>\n"
                "Available prompt codes:\n"
                "  %a = AC, %h = HP, %H = Max HP, %x = XP to next level, %RACE = your race,\n"
                "  %v = Move, %V = Max Move,\n"
                "  %s = Str, %d = Dex, %c = Con, %i = Int, %w = Wis, %c = Cha, %s = [Immortal] if immortal.\n"
                "Type 'setprompt <your prompt>' to change it."
            )

        if topic in ("combat", "maneuvers", "maneuver"):
            return (
                "Combat Maneuvers (D&D 3.5 Edition):\n"
                "\n"
                "Basic Combat:\n"
                "  kill <target>      - Attack a mob or player (starts combat)\n"
                "  attack <target>    - Same as kill\n"
                "  flee               - Attempt to escape combat\n"
                "\n"
                "Combat Maneuvers:\n"
                "  disarm <target>    - Knock weapon from opponent's hand\n"
                "  trip <target>      - Knock opponent prone (-4 to attacks)\n"
                "  bullrush <target>  - Push opponent back\n"
                "  grapple <target>   - Grab and restrain opponent\n"
                "  overrun <target>   - Move through opponent's space\n"
                "  sunder <target>    - Damage opponent's weapon\n"
                "  feint <target>     - Bluff to deny Dex bonus to AC\n"
                "\n"
                "Special Attacks (require feats):\n"
                "  whirlwind          - Attack all adjacent enemies (req: Whirlwind Attack)\n"
                "  springattack <t>   - Move-attack-move (req: Spring Attack)\n"
                "  stunningfist <t>   - Stun opponent (req: Stunning Fist)\n"
                "\n"
                "Grapple Actions (while grappled):\n"
                "  gdamage <target>   - Deal damage to grappled foe\n"
                "  gpin <target>      - Pin a grappled opponent\n"
                "  gescape            - Escape from a grapple\n"
                "\n"
                "Action Queue:\n"
                "  queue <action>     - Queue a spell/maneuver for your next turn\n"
                "  showqueue          - Show queued actions\n"
                "  clearqueue         - Clear action queue\n"
                "  autoattack [on/off]- Toggle auto-attack\n"
                "\n"
                "Tips:\n"
                "  - Improved feats (Improved Disarm, Improved Trip, etc.) give +4 bonus\n"
                "    and prevent attacks of opportunity.\n"
                "  - Maneuvers work on both mobs and players (PvP).\n"
                "  - Use 'help feats' to see all available feats."
            )

        if topic == "chat":
            return (
                "Chat Commands:\n"
                "\n"
                "  say <message>      - Speak to everyone in the room\n"
                "  tell <player> <msg>- Private message to a player\n"
                "  whisper <p> <msg>  - Same as tell\n"
                "  reply <message>    - Reply to last tell received\n"
                "  ooc <message>      - Out-of-character chat (room)\n"
                "  global <message>   - World-wide chat\n"
                "  chat <message>     - Same as global\n"
                "  shout <message>    - Area broadcast\n"
                "  yell <message>     - Same as shout\n"
                "  emote <action>     - Roleplay action (e.g., 'emote waves')\n"
                "  me <action>        - Same as emote\n"
                "  who                - List online players"
            )

        if topic == "movement":
            return (
                "Movement Commands:\n"
                "\n"
                "  north (n)          - Move north\n"
                "  south (s)          - Move south\n"
                "  east (e)           - Move east\n"
                "  west (w)           - Move west\n"
                "  up (u)             - Move up\n"
                "  down (d)           - Move down\n"
                "  exits              - Show available exits\n"
                "  recall             - Teleport to the chapel center\n"
                "  look               - Look around the room"
            )

        # Default: list all commands with topic hints
        cmds = sorted(c for c in self.commands.keys() if not c.startswith("@"))
        help_text = "Available commands: " + ", ".join(cmds)
        help_text += "\n\nHelp topics:"
        help_text += "\n  General:    combat, movement, chat, prompt, feats, death, conditions, ac, xp"
        help_text += "\n  Combat:     kill, flee, target, autoattack, queue, fullattack, powerattack, combatexpertise"
        help_text += "\n  Maneuvers:  disarm, trip, bullrush, grapple, overrun, sunder, feint"
        help_text += "\n              whirlwind, springattack, stunningfist, gdamage, gpin, gescape"
        help_text += "\n  Magic:      cast, spells, spellinfo, spellbook, prepare, domains, components"
        help_text += "\n  Items:      inventory, equipment, wear, remove, get, drop, loot, corpses"
        help_text += "\n  Economy:    shops, buy, sell, list, appraise, give, gold"
        help_text += "\n  Character:  score, stats, skills, rest, respawn, levelup, progression"
        help_text += "\n  Social:     say, tell, reply, emote, global, shout, ooc, who, talk, quest, time"
        help_text += "\nType 'help <topic>' for more info."
        return help_text

    def cmd_get(self, character, args):
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check
        if not args:
            return "Get what?"

        # Support "get <item> <container>" or "get <item> in <container>"
        parts = args.split()
        container_name = None
        if len(parts) >= 3 and parts[1].lower() == "in":
            item_name = parts[0].lower()
            container_name = " ".join(parts[2:]).lower()
        elif len(parts) >= 2:
            item_name = parts[0].lower()
            container_name = " ".join(parts[1:]).lower()
        else:
            item_name = args.lower()

        # If container name given, look in a container in inventory
        if container_name:
            container = next(
                (i for i in character.inventory
                 if i.name.lower() == container_name and i.capacity > 0 and i.contents is not None),
                None
            )
            if container:
                item = next((i for i in container.contents if i.name.lower() == item_name), None)
                if not item:
                    return f"No {item_name} in {container.name}."
                container.contents.remove(item)
                character.inventory.append(item)
                result = f"You take {item.name} from {container.name}."
                if hasattr(character, 'quest_log') and character.quest_log:
                    try:
                        item_type = getattr(item, 'item_type', item.name.lower())
                        quest_updates = quests.on_item_collected(character, item_type, character.quest_log, quests.get_quest_manager() if hasattr(quests, 'get_quest_manager') else None)
                        for update in quest_updates:
                            result += f"\n[Quest] {update}"
                    except Exception:
                        pass
                return result
            # No matching container found — fall through to room search with full args
            item_name = args.lower()

        # Default: get item from room
        item = next((i for i in character.room.items if i.name.lower() == item_name), None)
        if not item:
            return f"No {args} here."
        # Encumbrance check
        if hasattr(character, 'get_carry_weight') and hasattr(character, 'get_max_carry'):
            item_weight = getattr(item, 'weight', 0)
            if character.get_carry_weight() + item_weight > character.get_max_carry():
                return "You can't carry that much weight!"
        character.room.items.remove(item)
        character.inventory.append(item)
        result = f"You pick up {item.name}."

        # Quest trigger for item collection
        if hasattr(character, 'quest_log'):
            if hasattr(character, 'quest_log') and character.quest_log:
                try:
                    item_type = getattr(item, 'item_type', item.name.lower())
                    quest_updates = quests.on_item_collected(character, item_type, character.quest_log, quests.get_quest_manager() if hasattr(quests, 'get_quest_manager') else None)
                    for update in quest_updates:
                        result += f"\n[Quest] {update}"
                except Exception:
                    pass

        return result

    def cmd_drop(self, character, args):
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check
        # Find item in inventory by name
        if not args:
            return "Drop what?"
        item = next((i for i in character.inventory if i.name.lower() == args.lower()), None)
        if not item:
            return f"You don't have {args}."
        character.inventory.remove(item)
        character.room.items.append(item)
        return f"You drop {item.name}."

    def cmd_inventory(self, character, args):
        total_weight = sum(getattr(item, 'weight', 0) for item in character.inventory)
        # D&D 3.5 encumbrance thresholds (simplified):
        light = character.str_score * 5
        medium = character.str_score * 10
        heavy = character.str_score * 15
        if total_weight <= light:
            enc = "Light"
        elif total_weight <= medium:
            enc = "Medium"
        elif total_weight <= heavy:
            enc = "Heavy"
        else:
            enc = "Overloaded!"
        lines = [f"You are carrying ({total_weight} lbs): Encumbrance: {enc}"]
        if not character.inventory:
            lines.append("  (nothing)")
        else:
            for item in character.inventory:
                line = f"- {item.name} (wt {item.weight})"
                if item.capacity > 0 and item.contents is not None:
                    line += f" [container, {len(item.contents)}/{item.capacity}]"
                lines.append(line)
        return "\n".join(lines)

    def cmd_put(self, character, args):
        """Put an item into a container in your inventory.
        Usage: put <item> <container>  or  put <item> in <container>
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check
        if not args:
            return "Usage: put <item> <container>"

        parts = args.split()
        # Support "put all in bag", "put all bag", "put sword in bag", "put sword bag"
        if len(parts) >= 2 and parts[0].lower() == "all":
            # put all <container> or put all in <container>
            if parts[1].lower() == "in" and len(parts) >= 3:
                container_name = " ".join(parts[2:]).lower()
            else:
                container_name = " ".join(parts[1:]).lower()
            container = next(
                (i for i in character.inventory
                 if container_name in i.name.lower() and i.capacity > 0 and i.contents is not None),
                None
            )
            if not container:
                return f"You don't have a container named '{container_name}'."
            results = []
            for item in list(character.inventory):
                if item is container:
                    continue
                if len(container.contents) >= container.capacity:
                    results.append(f"{container.name} is full.")
                    break
                character.inventory.remove(item)
                container.contents.append(item)
                results.append(f"You put {item.name} into {container.name}.")
            return "\n".join(results) if results else "Nothing to put away."

        if len(parts) >= 3 and parts[1].lower() == "in":
            item_name = parts[0].lower()
            container_name = " ".join(parts[2:]).lower()
        elif len(parts) >= 2:
            item_name = parts[0].lower()
            container_name = " ".join(parts[1:]).lower()
        else:
            return "Usage: put <item> <container> or put all <container>"

        item = next((i for i in character.inventory if item_name in i.name.lower()), None)
        if not item:
            return f"You don't have '{item_name}'."

        container = next(
            (i for i in character.inventory
             if container_name in i.name.lower() and i.capacity > 0 and i.contents is not None),
            None
        )
        if not container:
            return f"You don't have a container named '{container_name}'."
        if item is container:
            return "You can't put a container inside itself."
        if len(container.contents) >= container.capacity:
            return f"{container.name} is full (capacity {container.capacity})."

        character.inventory.remove(item)
        container.contents.append(item)
        return f"You put {item.name} into {container.name}."

    def cmd_peek(self, character, args):
        """Look inside a container in your inventory.
        Usage: peek <container>
        """
        if not args:
            return "Peek into what?"
        container = next(
            (i for i in character.inventory
             if i.name.lower() == args.lower() and i.capacity > 0 and i.contents is not None),
            None
        )
        if not container:
            return f"You don't have a container named {args}."
        if not container.contents:
            return f"{container.name} is empty."
        lines = [f"{container.name} contains ({len(container.contents)}/{container.capacity}):"]
        for item in container.contents:
            lines.append(f"  - {item.name}")
        return "\n".join(lines)

    def cmd_where(self, character, args):
        """Show where players or mobs are in the world.
        Usage: where           - list all players with their rooms
               where <name>    - find mob/player matching name
        """
        results = []
        if not args:
            # List all non-AI players
            for player in self.world.players:
                if getattr(player, 'is_ai', False):
                    continue
                room = getattr(player, 'room', None)
                room_name = room.name if room else "Unknown"
                room_vnum = room.vnum if room else "?"
                results.append(f"  {player.name} - {room_name} ({room_vnum})")
            if not results:
                return "No players online."
            return f"Players in the World ({len(results)}):\n" + "\n".join(results[:20])
        else:
            # Search all rooms for matching mob or player
            search = args.lower()
            count = 0
            for room in self.world.rooms.values():
                for mob in getattr(room, 'mobs', []):
                    if search in mob.name.lower() and getattr(mob, 'alive', True):
                        results.append(f"  {mob.name} - {room.name} ({room.vnum})")
                        count += 1
                        if count >= 20:
                            break
                for player in getattr(room, 'players', []):
                    if search in player.name.lower():
                        results.append(f"  {player.name} - {room.name} ({room.vnum})")
                        count += 1
                if count >= 20:
                    break
            if not results:
                return f"No '{args}' found in the world."
            header = f"Matches for '{args}':"
            if count >= 20:
                header += " (showing first 20)"
            return header + "\n" + "\n".join(results)

    def cmd_autoloot(self, character, args):
        """Toggle automatic looting of items from corpses.
        Usage: autoloot
        """
        character.auto_loot = not getattr(character, 'auto_loot', False)
        state = "ON" if character.auto_loot else "OFF"
        return f"Auto-loot is now {state}."

    def cmd_autogold(self, character, args):
        """Toggle automatic collection of gold from corpses.
        Usage: autogold
        """
        character.auto_gold = not getattr(character, 'auto_gold', False)
        state = "ON" if character.auto_gold else "OFF"
        return f"Auto-gold is now {state}."

    def cmd_look(self, character, args):
        # Look at a specific target (mob, player, item)
        if args and args.strip():
            target_name = args.strip().lower()

            # Check mobs in room
            for mob in character.room.mobs:
                if hasattr(mob, 'alive') and not mob.alive:
                    continue
                if target_name in mob.name.lower():
                    lines = [f"\033[1;33m{mob.name}\033[0m"]
                    if hasattr(mob, 'description') and mob.description:
                        lines.append(mob.description[:500])
                    else:
                        lines.append(f"You see {mob.name}.")
                    # Show basic info
                    mtype = getattr(mob, 'type_', 'Unknown')
                    cr = getattr(mob, 'cr', '?')
                    align = getattr(mob, 'alignment', 'Unknown')
                    lines.append(f"  Type: {mtype}  CR: {cr}  Alignment: {align}")
                    if hasattr(mob, 'hp') and hasattr(mob, 'max_hp'):
                        hp_pct = (mob.hp / mob.max_hp * 100) if mob.max_hp > 0 else 0
                        if hp_pct >= 100:
                            condition = "is in perfect health"
                        elif hp_pct >= 75:
                            condition = "has a few scratches"
                        elif hp_pct >= 50:
                            condition = "has some wounds"
                        elif hp_pct >= 25:
                            condition = "is badly wounded"
                        else:
                            condition = "is near death"
                        lines.append(f"  {mob.name} {condition}.")
                    return "\n".join(lines)

            # Check players in room
            for other in character.room.players:
                if other is character:
                    continue
                if target_name in other.name.lower():
                    lines = [f"\033[1;36m{other.name}\033[0m"]
                    lines.append(f"  Race: {other.race}  Class: {getattr(other, 'char_class', '?')}  Level: {other.level}")
                    if hasattr(other, 'title') and other.title:
                        lines.append(f"  Title: {other.title}")
                    return "\n".join(lines)

            # Check items in inventory
            for item in getattr(character, 'inventory', []):
                item_name = getattr(item, 'name', str(item))
                if target_name in item_name.lower():
                    lines = [f"\033[1;32m{item_name}\033[0m"]
                    if hasattr(item, 'description') and item.description:
                        lines.append(item.description)
                    if hasattr(item, 'item_type'):
                        lines.append(f"  Type: {item.item_type}")
                    if hasattr(item, 'damage') and item.damage:
                        lines.append(f"  Damage: {item.damage[0]}d{item.damage[1]}+{item.damage[2]}")
                    if hasattr(item, 'ac_bonus') and item.ac_bonus:
                        lines.append(f"  AC bonus: +{item.ac_bonus}")
                    if hasattr(item, 'material') and item.material:
                        lines.append(f"  Material: {item.material}")
                    if hasattr(item, 'weight'):
                        lines.append(f"  Weight: {item.weight} lbs  Value: {getattr(item, 'value', 0)} gp")
                    return "\n".join(lines)

            # Check items on ground
            for item in getattr(character.room, 'items', []):
                item_name = getattr(item, 'name', str(item))
                if target_name in item_name.lower():
                    lines = [f"\033[1;32m{item_name}\033[0m (on ground)"]
                    if hasattr(item, 'description') and item.description:
                        lines.append(item.description)
                    return "\n".join(lines)

            return f"You don't see '{args.strip()}' here."

        desc = character.room.description
        # Add time-based atmospheric description
        game_time = get_game_time()
        if game_time.is_nighttime():
            desc += "\n\nThe area is dimly lit by starlight."

        # List mobs in the room with activity descriptions
        schedule_manager = get_schedule_manager()
        mob_lines = []
        for mob in character.room.mobs:
            if hasattr(mob, 'alive') and not mob.alive:
                continue
            # Use schedule-based activity description if available
            mob_vnum = getattr(mob, 'vnum', None)
            if mob_vnum and mob_vnum in schedule_manager.schedules:
                activity_desc = schedule_manager.get_activity_description(mob)
                mob_lines.append(activity_desc)
            else:
                mob_lines.append(f"{mob.name} is here.")
        if mob_lines:
            desc += "\n\n" + "\n".join(mob_lines)

        # Show corpses
        corpse_lines = []
        for corpse in getattr(character.room, 'corpses', []):
            corpse_lines.append(f"The corpse of {corpse.mob_name} lies here.")
        if corpse_lines:
            desc += "\n\n" + "\n".join(corpse_lines)

        # Show other players in the room (accounting for hidden players)
        player_lines = []
        for other in character.room.players:
            if other is character:
                continue
            if getattr(other, 'hidden', False):
                # Viewer must beat the hider's hide_check with a Spot check
                spot = character.skill_check("Spot")
                if isinstance(spot, int) and spot >= other.hide_check:
                    player_lines.append(f"{other.name} is hiding here (you spot them!).")
                # else: hidden and not spotted — don't show them
            else:
                player_lines.append(f"{other.name} is here.")
        if player_lines:
            desc += "\n\n" + "\n".join(player_lines)

        # Wandering gods presence
        try:
            from src.wandering_gods import get_wandering_gods
            wg = get_wandering_gods()
            god_msgs = wg.get_room_presence_messages(character, character.room.vnum)
            if god_msgs:
                desc += "\n\n" + "\n".join(god_msgs)
        except Exception:
            pass

        # Kin-sense (shown at end of look)
        from src.kin_sense import get_kin_sense_readout
        kin_sense = get_kin_sense_readout(character, character.room)
        if kin_sense:
            desc += "\n\n" + kin_sense

        return desc

    # =========================================================================
    # Chat and Communication Commands
    # =========================================================================
    def cmd_say(self, character, args):
        """Say something to everyone in the room."""
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check
        if not args:
            return "Say what?"
        from src.chat import broadcast_to_room, send_to_player

        # System 28: Language filtering
        active_lang = getattr(character, 'speaking_language', 'Common')
        lang_tag = f" [{active_lang}]" if active_lang != "Common" else ""

        def _garble(text):
            """Return a garbled version of the text (same length, scrambled)."""
            import random
            vowels = "aeiou"
            consonants = "bcdfghjklmnpqrstvwxyz"
            result_chars = []
            for ch in text:
                if ch.isalpha():
                    pool = vowels if ch.lower() in vowels else consonants
                    replacement = random.choice(pool)
                    result_chars.append(replacement.upper() if ch.isupper() else replacement)
                else:
                    result_chars.append(ch)
            return "".join(result_chars)

        # Broadcast to others in room with language filtering
        for listener in list(getattr(character.room, 'players', [])):
            if listener is character:
                continue
            listener_langs = self._get_known_languages(listener)
            if active_lang in listener_langs:
                msg = f"{character.name} says{lang_tag}, '{args}'"
            else:
                garbled = _garble(args)
                msg = (f"{character.name} says something in {active_lang}, "
                       f"'{garbled}'")
            send_to_player(listener, msg)

        # Return message to speaker
        if active_lang != "Common":
            return f"You say in {active_lang}, '{args}'"
        return f"You say, '{args}'"

    def cmd_tell(self, character, args):
        """Send a private message to another player.
        Usage: tell <player> <message>
        """
        if not args:
            return "Tell whom what? Usage: tell <player> <message>"
        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Tell them what? Usage: tell <player> <message>"

        target_name, message = parts
        from src.chat import find_player_by_name, send_tell
        recipient = find_player_by_name(self.world, target_name)

        if not recipient:
            # Try prefix match
            from src.chat import find_player_by_name_prefix
            recipient = find_player_by_name_prefix(self.world, target_name)

        if not recipient:
            return f"Player '{target_name}' not found."

        success, response = send_tell(character, recipient, message)
        return response

    def cmd_whisper(self, character, args):
        """Whisper to another player (alias for tell)."""
        return self.cmd_tell(character, args)

    def cmd_reply(self, character, args):
        """Reply to the last person who sent you a tell.
        Usage: reply <message>
        """
        if not args:
            return "Reply with what?"

        last_sender = getattr(character, 'last_tell_from', None)
        if not last_sender:
            return "No one has sent you a tell to reply to."

        from src.chat import find_player_by_name, send_tell
        recipient = find_player_by_name(self.world, last_sender)
        if not recipient:
            return f"{last_sender} is no longer online."

        success, response = send_tell(character, recipient, args)
        return response

    def cmd_social(self, character, args, verb=None):
        """Execute a social/emote verb."""
        if verb not in SOCIALS:
            return f"Unknown social: {verb}"
        social = SOCIALS[verb]
        # Check for target
        target = None
        if args:
            target_name = args.strip().lower()
            # Search room players
            for p in character.room.players:
                if p.name.lower() == target_name or p.name.lower().startswith(target_name):
                    if p != character:
                        target = p
                        break
            # Search room mobs if no player found
            if not target:
                for m in getattr(character.room, 'mobs', []):
                    if m.name.lower().startswith(target_name) and getattr(m, 'alive', True):
                        target = m
                        break

        from src.chat import broadcast_to_room, send_to_player
        if target:
            msg = social["room_targeted"].format(name=character.name, target=target.name)
            broadcast_to_room(character.room, msg, exclude=character)
            if hasattr(target, 'writer') and target != character:
                victim_msg = social["victim"].format(name=character.name)
                send_to_player(target, victim_msg)
            return social["self_targeted"].format(target=target.name)
        else:
            msg = social["room_no_target"].format(name=character.name)
            broadcast_to_room(character.room, msg, exclude=character)
            return social["self_no_target"]

    def cmd_emote(self, character, args):
        """Perform an emote/action visible to everyone in the room.
        Usage: emote <action>
        Example: emote waves hello
        Output: Playername waves hello
        """
        if not args:
            return "Emote what?"
        from src.chat import format_emote, broadcast_to_room
        message = format_emote(character, args)
        # Broadcast to others in room
        broadcast_to_room(character.room, message, exclude=character)
        # Return to actor
        return format_emote(character, args)

    def cmd_me(self, character, args):
        """Alias for emote."""
        return self.cmd_emote(character, args)

    def cmd_ooc(self, character, args):
        """Send an out-of-character message to everyone in the world.
        Usage: ooc <message>
        """
        if not args:
            return "OOC what?"
        from src.chat import format_ooc, broadcast_to_world
        message = format_ooc(character, args)
        # Broadcast to everyone except sender
        broadcast_to_world(self.world, message, exclude=character)
        # Return to sender
        return message

    def cmd_global(self, character, args):
        """Send a message to the global chat channel.
        Usage: global <message>
        """
        if not args:
            return "Say what globally?"
        from src.chat import format_global, broadcast_to_world
        message = format_global(character, args)
        # Broadcast to everyone except sender
        broadcast_to_world(self.world, message, exclude=character)
        # Return to sender
        return message

    def cmd_chat(self, character, args):
        """Alias for global chat."""
        return self.cmd_global(character, args)

    def cmd_shout(self, character, args):
        """Shout something that can be heard in nearby rooms.
        Usage: shout <message>
        """
        if not args:
            return "Shout what?"
        from src.chat import format_shout, broadcast_to_room
        message = format_shout(character, args)
        # Broadcast to current room (TODO: expand to nearby rooms)
        broadcast_to_room(character.room, message, exclude=character)
        # Return to shouter
        return f"You shout, '{args}'"

    def cmd_yell(self, character, args):
        """Alias for shout."""
        return self.cmd_shout(character, args)

    def cmd_who(self, character, args):
        """List all online players.
        Usage: who [level_min-level_max]
        Example: who 5-10
        """
        import time as _time
        # Parse optional level range filter: "who 5-10"
        level_min = None
        level_max = None
        args = (args or "").strip()
        if args:
            import re as _re
            m = _re.match(r'^(\d+)(?:-(\d+))?$', args)
            if m:
                level_min = int(m.group(1))
                level_max = int(m.group(2)) if m.group(2) else level_min
            # Non-numeric args are silently ignored (could be name filter extension)

        # Pull ACTIVE_SESSIONS for idle time calculation
        try:
            from main import ACTIVE_SESSIONS
        except ImportError:
            ACTIVE_SESSIONS = {}

        now = _time.time()
        lines = []
        count = 0
        for player in self.world.players:
            if getattr(player, 'is_ai', False):
                continue
            # Level range filter
            if level_min is not None and not (level_min <= player.level <= level_max):
                continue
            count += 1

            # Build status tags
            tags = []
            if getattr(player, 'is_immortal', False):
                tags.append("[IMM]")
            if getattr(player, 'afk', False):
                tags.append("[AFK]")

            # Idle time
            session_entry = ACTIVE_SESSIONS.get(player.name)
            if session_entry:
                idle_secs = int(now - session_entry[1])
                if idle_secs >= 3600:
                    idle_str = f"[Idle {idle_secs // 3600}h{(idle_secs % 3600) // 60}m]"
                elif idle_secs >= 60:
                    idle_str = f"[Idle {idle_secs // 60}m]"
                else:
                    idle_str = ""
                if idle_str:
                    tags.append(idle_str)

            # Format: [Lv## Class    ] Name Title (Race)
            level_str = str(player.level).zfill(2)
            class_name = (player.char_class or "Unknown")[:8]
            bracket = f"[Lv{level_str} {class_name:<8}]"
            name_part = player.name
            title_part = getattr(player, 'title', None) or ""
            race_part = f"({player.race})" if player.race else ""
            tag_str = " ".join(tags)
            right_side = " ".join(filter(None, [name_part, title_part, race_part, tag_str]))
            lines.append(f"  {bracket} {right_side}")

        if not lines:
            if level_min is not None:
                return f"No players online in level range {level_min}-{level_max}."
            return "No players online."

        header = "Players Online:"
        if level_min is not None:
            header = f"Players Online (levels {level_min}-{level_max}):"
        footer = f"{count} player{'s' if count != 1 else ''} online."
        return header + "\n" + "\n".join(lines) + "\n" + footer

    def cmd_kill(self, character, args):
        """Attack a mob or player.
        Usage: kill <target>
        """
        if not args:
            return "Kill whom?"

        # Check if dead/incapacitated
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        # Check if character can act based on conditions
        if hasattr(character, 'can_act') and not character.can_act():
            return "You cannot act in your current condition!"

        # Check for cannot_attack effect (e.g., nauseated)
        if hasattr(character, 'has_condition_effect') and character.has_condition_effect('cannot_attack'):
            return "You cannot attack in your current condition!"

        # Must be standing to fight
        if getattr(character, 'position', 'standing') != 'standing':
            return "You need to stand up first!"

        target = None
        is_pvp = False

        # First check mobs
        target = next((m for m in character.room.mobs if m.name.lower() == args.lower() and m.alive), None)

        # If no mob found, check players (PvP)
        if not target:
            for player in character.room.players:
                if player.name.lower() == args.lower():
                    # Can't attack yourself
                    if player == character:
                        return "You can't attack yourself!"
                    # Can't attack dead players
                    if getattr(player, 'hp', 0) <= 0:
                        return f"{player.name} is already dead!"
                    target = player
                    is_pvp = True
                    break

        if not target:
            return "No such target!"

        # Initialize combat instance
        from src.combat import start_combat as init_combat
        from src.chat import broadcast_to_room

        combat = init_combat(character.room, character, target)

        character.state = State.COMBAT
        character.set_combat_target(target)

        # If PvP, put the other player in combat too
        if is_pvp:
            target.state = State.COMBAT
            if not getattr(target, 'combat_target', None):
                target.set_combat_target(character)  # Auto-target attacker

        # Build combat start message
        results = []
        combat_start_msg = combat.start_combat()
        results.append(combat_start_msg)

        # Announce PvP to room
        if is_pvp:
            broadcast_to_room(character.room,
                f"\033[1;31m*** {character.name} attacks {target.name}! ***\033[0m",
                exclude=character)

        # Sneak attack: if attacker was hidden, apply sneak attack bonus and break stealth
        if getattr(character, 'hidden', False):
            results.append("You attack from the shadows!")
            character.hidden = False
            if getattr(character, 'char_class', '') == "Rogue":
                import math
                sneak_dice = max(1, math.ceil(character.level / 2))
                sneak_dmg = sum(__import__('random').randint(1, 6) for _ in range(sneak_dice))
                results.append(f"Sneak attack! +{sneak_dmg} damage ({sneak_dice}d6).")
                target.hp -= sneak_dmg

        # Execute first attack
        attack_result = attack(character, target)
        results.append(attack_result)

        # Check if target died from first attack
        if target.hp <= 0:
            if is_pvp:
                # Player death
                results.append(f"\033[1;31m{target.name} has been defeated by {character.name}!\033[0m")
                broadcast_to_room(character.room,
                    f"\033[1;31m*** {target.name} has been defeated by {character.name}! ***\033[0m",
                    exclude=character)
                # Don't set alive=False for players, just leave them at 0 HP
                # They can be healed or will need to respawn
                target.state = State.EXPLORING
                target.clear_combat_target()
            else:
                # Mob death
                target.alive = False
                results.append(f"{target.name} has been slain!")
                # Quest trigger
                if hasattr(character, 'quest_log'):
                    try:
                        mob_type = getattr(target, 'mob_type', target.name.lower())
                        quest_updates = quests.on_mob_killed(character, mob_type, character.quest_log if hasattr(character, 'quest_log') else None, quests.get_quest_manager() if hasattr(quests, 'get_quest_manager') else None)
                        for update in quest_updates:
                            results.append(f"[Quest] {update}")
                    except Exception:
                        pass

            # End combat if no enemies left
            should_end, end_msg = combat.check_combat_end()
            if should_end:
                results.append(end_msg)
                combat.end_combat()
                character.clear_combat_target()
                character.state = State.EXPLORING

        return "\n".join(results)

    def cmd_flee(self, character, args):
        """Attempt to flee from combat."""
        import random
        from src.combat import get_combat, end_combat, trigger_aoo

        if character.state != State.COMBAT:
            return "You're not in combat!"

        # System 20: Trigger Attacks of Opportunity from hostile mobs before fleeing
        flee_messages = []
        combat = get_combat(character.room)
        if combat:
            for state in list(combat.initiative_order):
                mob_combatant = state.combatant
                # Only non-player combatants (mobs) trigger AoO on flee
                if not hasattr(mob_combatant, 'xp') and getattr(mob_combatant, 'hp', 0) > 0 and getattr(mob_combatant, 'alive', True):
                    aoo_result = trigger_aoo(mob_combatant, character, "flee")
                    if aoo_result:
                        flee_messages.append(aoo_result)

        # 50% base chance to flee, modified by Dex
        dex_mod = (getattr(character, 'dex_score', 10) - 10) // 2
        flee_chance = 50 + (dex_mod * 5)

        if random.randint(1, 100) <= flee_chance:
            # Success - pick a random exit and move
            if character.room.exits:
                direction = random.choice(list(character.room.exits.keys()))
                new_vnum = _resolve_exit(character.room.exits[direction])

                # Remove from combat
                combat = get_combat(character.room)
                if combat:
                    combat.remove_combatant(character)
                    # End combat if no players left
                    should_end, _ = combat.check_combat_end()
                    if should_end:
                        end_combat(character.room)

                character.state = State.EXPLORING
                character.clear_combat_target()
                character.clear_queue()

                # Move to new room
                if new_vnum in self.world.rooms:
                    character.room.players.remove(character)
                    character.room = self.world.rooms[new_vnum]
                    character.room.players.append(character)
                    flee_result = f"You flee {direction}!\nYou escape to {character.room.name}."
                    if flee_messages:
                        return "\n".join(flee_messages) + "\n" + flee_result
                    return flee_result

            flee_result = "You flee in panic but there's nowhere to go!"
        else:
            flee_result = "You try to flee but can't escape!"

        if flee_messages:
            return "\n".join(flee_messages) + "\n" + flee_result
        return flee_result

    # =========================================================================
    # Auto-Attack and Action Queue Commands
    # =========================================================================
    def cmd_queue(self, character, args):
        """Queue an action to replace your next auto-attack.
        Usage: queue <spell|skill|feat|maneuver|item> <name> [target]
        Example: queue spell fireball
        Example: queue spell cure light wounds self
        Example: queue maneuver disarm goblin
        """
        if not args:
            return ("Usage: queue <type> <name> [target]\n"
                    "Types: spell, skill, feat, maneuver, item\n"
                    "Example: queue spell fireball\n"
                    "Example: queue maneuver trip goblin")

        parts = args.split(None, 2)  # Split into max 3 parts
        if len(parts) < 2:
            return "Usage: queue <type> <name> [target]"

        action_type = parts[0].lower()
        action_name = parts[1]
        action_args = parts[2] if len(parts) > 2 else ""

        valid_types = ['spell', 'skill', 'feat', 'maneuver', 'item']
        if action_type not in valid_types:
            return f"Invalid action type '{action_type}'. Valid types: {', '.join(valid_types)}"

        # Validate the action exists
        if action_type == 'spell':
            from src.spells import get_spell_by_name
            spell = get_spell_by_name(action_name)
            if not spell:
                return f"No such spell: {action_name}"
            # Check if known
            known = False
            for s in character.spells_known.values():
                if isinstance(s, dict) and s.get("name", "").lower() == action_name.lower():
                    known = True
                    break
                elif isinstance(s, str) and s.lower() == action_name.lower():
                    known = True
                    break
            if not known:
                return f"You don't know the spell: {action_name}"

        elif action_type == 'maneuver':
            from src import maneuvers
            valid_maneuvers = ['disarm', 'trip', 'bullrush', 'grapple', 'overrun', 'sunder', 'feint']
            if action_name.lower() not in valid_maneuvers:
                return f"Invalid maneuver '{action_name}'. Valid: {', '.join(valid_maneuvers)}"

        elif action_type == 'feat':
            # Check if character has the feat
            if action_name not in character.feats:
                return f"You don't have the feat: {action_name}"

        character.queue_action(action_type, action_name, action_args)
        return f"Queued {action_type}: {action_name}" + (f" (target: {action_args})" if action_args else "") + "\nThis will replace your next auto-attack."

    def cmd_q(self, character, args):
        """Shortcut for queue command."""
        return self.cmd_queue(character, args)

    def cmd_clearqueue(self, character, args):
        """Clear your queued action."""
        if character.has_queued_action():
            character.clear_queue()
            return "Queued action cleared."
        return "No action was queued."

    def cmd_cq(self, character, args):
        """Shortcut for clearqueue."""
        return self.cmd_clearqueue(character, args)

    def cmd_showqueue(self, character, args):
        """Show your currently queued action."""
        if character.has_queued_action():
            action_type, action_name, action_args = character.queued_action
            result = f"Queued: {action_type} - {action_name}"
            if action_args:
                result += f" (target: {action_args})"
            return result
        return "No action queued. You will auto-attack."

    def cmd_sq(self, character, args):
        """Shortcut for showqueue."""
        return self.cmd_showqueue(character, args)

    def cmd_autoattack(self, character, args):
        """Toggle auto-attack on or off."""
        enabled = character.toggle_auto_attack()
        if enabled:
            return "Auto-attack is now ON. You will automatically attack your target each round."
        else:
            return "Auto-attack is now OFF. You must manually attack each round."

    def cmd_aa(self, character, args):
        """Shortcut for autoattack toggle."""
        return self.cmd_autoattack(character, args)

    def cmd_target(self, character, args):
        """Set your auto-attack target without attacking.
        Usage: target <mob name>
        """
        if not args:
            if character.combat_target:
                target_name = getattr(character.combat_target, 'name', 'Unknown')
                return f"Current target: {target_name}"
            return "No target set. Usage: target <mob name>"

        target = next((m for m in character.room.mobs if m.name.lower() == args.lower() and m.alive), None)
        if target:
            character.set_combat_target(target)
            return f"Target set to: {target.name}"
        return "No such target!"

    def cmd_open(self, character, args):
        """Open a door in the given direction."""
        if not args:
            return "Open which direction?"
        direction = args.strip().lower()
        if direction not in character.room.exits:
            return f"There is no door to the {direction}."
        exit_data = character.room.exits[direction]
        if not isinstance(exit_data, dict) or not exit_data.get("door"):
            return f"There is no door to the {direction}."
        if not exit_data.get("closed"):
            return "The door is already open."
        if exit_data.get("locked"):
            return "The door is locked."
        exit_data["closed"] = False
        return f"You open the door to the {direction}."

    def cmd_close(self, character, args):
        """Close a door in the given direction."""
        if not args:
            return "Close which direction?"
        direction = args.strip().lower()
        if direction not in character.room.exits:
            return "There is no door that way."
        exit_data = character.room.exits[direction]
        if not isinstance(exit_data, dict) or not exit_data.get("door"):
            return "There is no door that way."
        if exit_data.get("closed"):
            return "The door is already closed."
        exit_data["closed"] = True
        return "You close the door."

    def cmd_unlock(self, character, args):
        """Unlock a door in the given direction using a key from inventory."""
        if not args:
            return "Unlock which direction?"
        direction = args.strip().lower()
        if direction not in character.room.exits:
            return "There is no door that way."
        exit_data = character.room.exits[direction]
        if not isinstance(exit_data, dict) or not exit_data.get("door"):
            return "There is no door that way."
        if not exit_data.get("locked"):
            return "The door is not locked."
        key_vnum = exit_data.get("key_vnum")
        key = next((item for item in character.inventory if item.vnum == key_vnum), None)
        if not key:
            return "You don't have the right key."
        exit_data["locked"] = False
        return f"You unlock the door with {key.name}."

    def cmd_lock(self, character, args):
        """Lock a door in the given direction using a key from inventory."""
        if not args:
            return "Lock which direction?"
        direction = args.strip().lower()
        if direction not in character.room.exits:
            return "There is no door that way."
        exit_data = character.room.exits[direction]
        if not isinstance(exit_data, dict) or not exit_data.get("door"):
            return "There is no door that way."
        if exit_data.get("locked"):
            return "The door is already locked."
        key_vnum = exit_data.get("key_vnum")
        key = next((item for item in character.inventory if item.vnum == key_vnum), None)
        if not key:
            return "You don't have the right key."
        exit_data["locked"] = True
        return f"You lock the door with {key.name}."

    def cmd_pick(self, character, args):
        """Pick the lock on a door in the given direction (Open Lock skill check)."""
        if not args:
            return "Pick the lock on which direction?"
        direction = args.strip().lower()
        if direction not in character.room.exits:
            return "There is no door that way."
        exit_data = character.room.exits[direction]
        if not isinstance(exit_data, dict) or not exit_data.get("door"):
            return "There is no door that way."
        if not exit_data.get("locked"):
            return "The door is not locked."
        pick_dc = exit_data.get("pick_dc", 20)
        result = character.skill_check("Open Lock")
        if isinstance(result, str):
            return result
        if result >= pick_dc:
            exit_data["locked"] = False
            return "You pick the lock!"
        return "You fail to pick the lock."

    def cmd_move(self, character, args):
        # Check if dead/incapacitated
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check
        # Check if character can move based on conditions
        if hasattr(character, 'can_move') and not character.can_move():
            return "You cannot move in your current condition!"
        # Must be standing to move
        if getattr(character, 'position', 'standing') != 'standing':
            return "You need to stand up first!"

        # When mounted, movement is faster (mount carries the rider)
        # Move cost is halved when mounted (mount's speed applies)
        _mounted = getattr(character, 'mounted', False)

        direction = args.lower()
        if direction in character.room.exits:
            exit_data = character.room.exits[direction]
            # Door check: block movement through closed or locked doors
            if isinstance(exit_data, dict) and exit_data.get("door"):
                if exit_data.get("locked"):
                    return "The door is locked."
                if exit_data.get("closed"):
                    return "The door is closed."
            new_vnum = _resolve_exit(exit_data)
            if new_vnum in self.world.rooms:
                from src.chat import broadcast_to_room

                old_room = character.room
                new_room = self.world.rooms[new_vnum]

                # Announce departure to old room
                broadcast_to_room(old_room, f"{character.name} leaves {direction}.", exclude=character)

                # Move the character
                old_room.players.remove(character)
                character.room = new_room
                new_room.players.append(character)

                # Announce arrival to new room
                # Figure out opposite direction for "arrives from"
                opposites = {'north': 'south', 'south': 'north', 'east': 'west',
                            'west': 'east', 'up': 'below', 'down': 'above'}
                from_dir = opposites.get(direction, 'somewhere')
                broadcast_to_room(new_room, f"{character.name} arrives from the {from_dir}.", exclude=character)

                # Aerial room check (System 30: Flying)
                if "aerial" in getattr(new_room, 'flags', []):
                    if not getattr(character, 'flying', False):
                        # Can't enter aerial room without flying
                        new_room.players.remove(character)
                        character.room = old_room
                        old_room.players.append(character)
                        broadcast_to_room(new_room, f"{character.name} turns back.", exclude=character)
                        broadcast_to_room(old_room, f"{character.name} returns, unable to fly.", exclude=character)
                        return "You cannot enter an aerial area without the ability to fly!"

                # Trap check: trigger or safely bypass trap in new room
                result = f"You move {direction} to {character.room.name}."

                # Flying bonus: +2 dodge vs pit traps (note in result)
                if getattr(character, 'flying', False):
                    result += "\n[Flying: +2 dodge bonus, immune to pit traps]"

                if "trapped" in getattr(new_room, 'flags', []):
                    detected = getattr(new_room, '_detected_traps', set())
                    if character.name in detected:
                        result += "\nYou carefully avoid the trap."
                    else:
                        trap_msg = self._trigger_trap(character, new_room)
                        result += f"\n{trap_msg}"

                # Quest trigger for room entry
                if hasattr(character, 'quest_log') and character.quest_log:
                    try:
                        room_vnum = str(new_vnum)
                        quest_updates = quests.on_room_entered(character, room_vnum, character.quest_log, quests.get_quest_manager() if hasattr(quests, 'get_quest_manager') else None)
                        for update in quest_updates:
                            result += f"\n[Quest] {update}"
                    except Exception:
                        pass  # Quest system not fully initialized

                # System 29: Underwater / Drowning mechanics
                result = self._handle_underwater_move(character, new_room, result)

                # Hide/Sneak: check if movement breaks stealth
                if getattr(character, 'hidden', False):
                    if getattr(character, 'sneaking', False):
                        stealth = character.skill_check("Move Silently")
                        if isinstance(stealth, str) or stealth < 10:
                            character.hidden = False
                            result += "\nYour stealth is broken!"
                        else:
                            result += "\nYou move silently."
                    else:
                        character.hidden = False

                # Move followers who were in the old room
                for player in list(self.world.players):
                    if getattr(player, 'following', None) is character and player.room is old_room:
                        old_room.players.remove(player)
                        player.room = new_room
                        new_room.players.append(player)
                        from src.chat import send_to_player as _stp
                        _stp(player, f"You follow {character.name} {direction}.")

                # If mounted, note faster travel; mount moves with the rider
                if _mounted and getattr(character, 'mount', None):
                    result += f"\n{character.mount.name} carries you swiftly."

                # Move companion with character if following
                companion = getattr(character, 'companion', None)
                if companion and getattr(companion, '_companion_following', True):
                    result += f"\n{companion.name} follows you {direction}."

                # Location effects on room entry
                try:
                    from src.location_effects import get_location_effects
                    le = get_location_effects()
                    le.on_room_exit(character, old_room)
                    effect_msgs = le.on_room_enter(character, new_room)
                    for emsg in effect_msgs:
                        result += f"\n{emsg}"
                except Exception:
                    pass

                # Show room description and mobs after moving
                look_output = self.cmd_look(character, "")
                return f"{result}\n{look_output}"
        return "No exit that way!"

    def cmd_exits(self, character, args):
        # Only show exits that are connected to existing rooms
        connected_exits = []
        for direction, exit_data in character.room.exits.items():
            # Skip hidden exits for non-builders
            if isinstance(exit_data, dict) and exit_data.get("hidden") and not getattr(character, 'is_builder', False):
                continue
            vnum = _resolve_exit(exit_data)
            if vnum in self.world.rooms:
                connected_exits.append(direction)
        if connected_exits:
            return "Exits: " + ", ".join(connected_exits)
        else:
            return "No visible exits."

    def cmd_quest(self, character, args):
        if args.lower() == "start" and 1 not in [q["id"] for q in character.quests]:
            character.quests.append(self.world.quests[1])
            return f"Quest started: {self.world.quests[1]['name']}"
        return "Quest status: " + (f"{character.quests[0]['name']}" if character.quests else "No active quests.")

    def cmd_gecho(self, character, args):
        """Admin broadcast to all players."""
        if not character.is_immortal:
            return "Command restricted to immortals!"
        if not args:
            return "Broadcast what?"
        from src.chat import format_admin, broadcast_to_world
        message = format_admin(character, args)
        # Broadcast to everyone including sender
        broadcast_to_world(self.world, message, exclude=None)
        return "Broadcast sent."

    def cmd_stats(self, character, args):
        return character.toggle_stats()

    # --- D&D 3.5 Skill Command Stubs ---

    def cmd_balance(self, character, args):
        banker = self._find_banker(character)
        if banker:
            return f"{banker.name} tells you, 'You have {character.bank_gold} gold pieces in your account.'"
        result = character.skill_check("Balance")
        return f"You attempt to keep your balance. Skill check result: {result}"

    def cmd_bluff(self, character, args):
        result = character.skill_check("Bluff")
        return f"You attempt to bluff. Skill check result: {result}"

    def cmd_climb(self, character, args):
        result = character.skill_check("Climb")
        return f"You attempt to climb. Skill check result: {result}"

    def cmd_concentration(self, character, args):
        result = character.skill_check("Concentration")
        return f"You focus your concentration. Skill check result: {result}"

    def cmd_decipher(self, character, args):
        result = character.skill_check("Decipher Script")
        return f"You attempt to decipher the script. Skill check result: {result}"

    def cmd_diplomacy(self, character, args):
        result = character.skill_check("Diplomacy")
        return f"You attempt diplomacy. Skill check result: {result}"

    def cmd_disable(self, character, args):
        result = character.skill_check("Disable Device")
        return f"You attempt to disable the device. Skill check result: {result}"

    def cmd_disguise(self, character, args):
        result = character.skill_check("Disguise")
        return f"You attempt to disguise yourself. Skill check result: {result}"

    def cmd_escape(self, character, args):
        result = character.skill_check("Escape Artist")
        return f"You attempt to escape. Skill check result: {result}"

    def cmd_forgery(self, character, args):
        result = character.skill_check("Forgery")
        return f"You attempt to forge a document. Skill check result: {result}"

    def cmd_gatherinfo(self, character, args):
        result = character.skill_check("Gather Information")
        return f"You attempt to gather information. Skill check result: {result}"

    def cmd_gather(self, character, args):
        """Gather herbs and natural materials from the environment.
        Requires being in a forest, garden, or field room.
        Uses Survival (DC 8). Has a 60-second cooldown.
        """
        import time
        import random
        from src.items import Item

        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        # Check room flags
        room_flags = getattr(character.room, 'flags', [])
        terrain_types = ['forest', 'garden', 'field']
        terrain = next((f for f in terrain_types if f in room_flags), None)
        if not terrain:
            return "There is nothing to gather here. You need to be in a forest, garden, or field."

        # Cooldown check (60 seconds)
        now = time.time()
        last = getattr(character, '_last_gather', 0)
        if now - last < 60:
            remaining = int(60 - (now - last))
            return f"You need to wait {remaining} more seconds before gathering again."
        character._last_gather = now

        # Survival check DC 8
        result = character.skill_check("Survival")
        if isinstance(result, str):
            return result
        if result < 8:
            return "You don't find anything useful."

        # Determine yield by terrain
        if terrain == 'forest':
            options = [
                ("Healing Herb", 96001),
                ("Wood Plank", 96002),
                ("Leather Strip", 96003),
            ]
        elif terrain == 'garden':
            options = [
                ("Healing Herb", 96001),
                ("Rare Herb", 96004),
                ("Healing Herb", 96001),
            ]
        else:  # field
            options = [
                ("Leather Strip", 96003),
                ("Wood Plank", 96002),
                ("Wild Herb", 96005),
            ]

        chosen_name, base_vnum = random.choice(options)
        vnum = base_vnum
        item = Item(vnum=vnum, name=chosen_name, item_type="material", weight=1, value=2,
                    description=f"A {chosen_name.lower()} gathered from the {terrain}.")
        character.inventory.append(item)
        return f"You forage the {terrain} and find a {chosen_name}."

    def cmd_fish(self, character, args):
        """Fish in bodies of water.
        Requires being in a water or fishing room.
        Uses Survival (DC 10). Has a 30-second cooldown.
        """
        import time
        import random
        from src.items import Item

        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        # Check room flags
        room_flags = getattr(character.room, 'flags', [])
        if 'water' not in room_flags and 'fishing' not in room_flags:
            return "There is no suitable water for fishing here."

        # Cooldown check (30 seconds)
        now = time.time()
        last = getattr(character, '_last_fish', 0)
        if now - last < 30:
            remaining = int(30 - (now - last))
            return f"You need to wait {remaining} more seconds before fishing again."
        character._last_fish = now

        # Survival check DC 10
        result = character.skill_check("Survival")
        if isinstance(result, str):
            return result
        if result < 10:
            return "You fail to catch anything."

        # Create a fish item with a unique vnum in the 95000 range
        fish_vnum = 95000 + random.randint(0, 999)
        fish = Item(vnum=fish_vnum, name="Fresh Fish", item_type="food", weight=1, value=1,
                    description="A freshly caught fish.")
        character.inventory.append(fish)
        return "You cast your line and pull out a Fresh Fish!"

    def cmd_mine(self, character, args):
        """Mine for ore and minerals.
        Requires being in a mine or cave room.
        Uses Craft(mining) or Survival (DC 12). Has a 60-second cooldown.
        """
        import time
        import random
        from src.items import Item

        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        # Check room flags
        room_flags = getattr(character.room, 'flags', [])
        if 'mine' not in room_flags and 'cave' not in room_flags:
            return "There is nothing to mine here. You need to be in a mine or cave."

        # Cooldown check (60 seconds)
        now = time.time()
        last = getattr(character, '_last_mine', 0)
        if now - last < 60:
            remaining = int(60 - (now - last))
            return f"You need to wait {remaining} more seconds before mining again."
        character._last_mine = now

        # Craft(mining) or Survival check DC 12
        craft_result = character.skill_check("Craft (any)")
        survival_result = character.skill_check("Survival")
        # Use the better of the two (if craft_result is a string it means untrained, skip it)
        result = craft_result if not isinstance(craft_result, str) else None
        surv = survival_result if not isinstance(survival_result, str) else None
        if result is None and surv is None:
            return "You lack the skill to mine effectively."
        best = max(r for r in [result, surv] if r is not None)
        if best < 12:
            return "You fail to find any ore."

        # Determine ore type by random roll
        roll = random.randint(1, 100)
        if roll <= 60:
            ore_name, ore_vnum, ore_value = "Iron Ore", 97001, 5
        elif roll <= 90:
            ore_name, ore_vnum, ore_value = "Copper Ore", 97002, 8
        else:
            ore_name, ore_vnum, ore_value = "Gold Nugget", 97003, 30

        ore = Item(vnum=ore_vnum, name=ore_name, item_type="material", weight=3, value=ore_value,
                   description=f"A chunk of {ore_name.lower()} chipped from the rock.")
        character.inventory.append(ore)
        return f"You strike the rock and extract some {ore_name}!"

    def cmd_mount(self, character, args):
        """Mount a rideable creature in the room.
        Usage: mount <mob name>
        The mob must have the 'mountable' flag. Requires a Ride check (DC 5).
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        if getattr(character, 'mounted', False):
            return f"You are already mounted on {character.mount.name}."

        if not args:
            return "Mount what? Usage: mount <mob name>"

        target_name = args.lower()
        found = None
        for mob in getattr(character.room, 'mobs', []):
            if getattr(mob, 'alive', True) and target_name in mob.name.lower():
                if 'mountable' in getattr(mob, 'flags', []):
                    found = mob
                    break

        if not found:
            return f"You don't see a mountable creature named '{args}' here."

        # Ride check DC 5
        result = character.skill_check("Ride")
        if isinstance(result, str):
            return f"You don't know how to ride. ({result})"
        if result < 5:
            return f"You fail to mount {found.name}. (Ride check: {result} vs DC 5)"

        character.mount = found
        character.mounted = True
        character.room.mobs.remove(found)
        return f"You mount {found.name}."

    def cmd_dismount(self, character, args):
        """Dismount your current mount.
        Usage: dismount
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        if not getattr(character, 'mounted', False) or not getattr(character, 'mount', None):
            return "You are not mounted."

        mount = character.mount
        character.room.mobs.append(mount)
        character.mount = None
        character.mounted = False
        return "You dismount."

    def cmd_handle(self, character, args):
        result = character.skill_check("Handle Animal")
        return f"You attempt to handle the animal. Skill check result: {result}"

    def cmd_heal(self, character, args):
        result = character.skill_check("Heal")
        return f"You attempt to heal. Skill check result: {result}"

    def cmd_hide(self, character, args):
        """Attempt to hide from observers. Can't be used in active combat."""
        if character.state == State.COMBAT:
            return "You can't hide while in combat!"
        result = character.skill_check("Hide")
        if isinstance(result, str):
            return result
        character.hidden = True
        character.hide_check = result
        return f"You attempt to hide... (Hide check: {result})"

    def cmd_sneak(self, character, args):
        """Toggle sneaking mode for silent movement."""
        character.sneaking = not character.sneaking
        if character.sneaking:
            return "You begin moving stealthily."
        return "You stop sneaking."

    def cmd_intimidate(self, character, args):
        result = character.skill_check("Intimidate")
        return f"You attempt to intimidate. Skill check result: {result}"

    def cmd_jump(self, character, args):
        result = character.skill_check("Jump")
        return f"You attempt to jump. Skill check result: {result}"

    def cmd_knowledge(self, character, args):
        # args should specify the knowledge type
        skill = f"Knowledge ({args.strip().lower()})" if args else "Knowledge (arcana)"
        result = character.skill_check(skill.title())
        return f"You recall knowledge about {args or 'arcana'}. Skill check result: {result}"

    def cmd_listen(self, character, args):
        result = character.skill_check("Listen")
        return f"You attempt to listen carefully. Skill check result: {result}"

    def cmd_movesilently(self, character, args):
        result = character.skill_check("Move Silently")
        return f"You attempt to move silently. Skill check result: {result}"

    def cmd_openlock(self, character, args):
        result = character.skill_check("Open Lock")
        return f"You attempt to open the lock. Skill check result: {result}"

    def cmd_perform(self, character, args):
        result = character.skill_check("Perform (any)")
        return f"You attempt to perform. Skill check result: {result}"

    def cmd_profession(self, character, args):
        result = character.skill_check("Profession (any)")
        return f"You attempt to use your profession. Skill check result: {result}"

    def cmd_ride(self, character, args):
        result = character.skill_check("Ride")
        return f"You attempt to ride. Skill check result: {result}"

    # cmd_search is defined below as the trap-aware version (overrides this location)

    def cmd_sensemotive(self, character, args):
        result = character.skill_check("Sense Motive")
        return f"You attempt to sense motive. Skill check result: {result}"

    def cmd_sleight(self, character, args):
        result = character.skill_check("Sleight of Hand")
        return f"You attempt sleight of hand. Skill check result: {result}"

    def cmd_spellcraft(self, character, args):
        result = character.skill_check("Spellcraft")
        return f"You attempt to identify magic. Skill check result: {result}"

    def cmd_spot(self, character, args):
        result = character.skill_check("Spot")
        return f"You attempt to spot something. Skill check result: {result}"

    def cmd_survival(self, character, args):
        result = character.skill_check("Survival")
        return f"You attempt to survive in the wild. Skill check result: {result}"

    def cmd_swim(self, character, args):
        result = character.skill_check("Swim")
        return f"You attempt to swim. Skill check result: {result}"

    def cmd_tumble(self, character, args):
        result = character.skill_check("Tumble")
        return f"You attempt to tumble. Skill check result: {result}"

    def cmd_usemagic(self, character, args):
        result = character.skill_check("Use Magic Device")
        return f"You attempt to use a magic device. Skill check result: {result}"

    def cmd_userope(self, character, args):
        result = character.skill_check("Use Rope")
        return f"You attempt to use a rope. Skill check result: {result}"

    def cmd_help_feats(self, character, args):
        """
        Show all feats, their type (passive/active), description, and usage if active.
        Usage: help feats [<feat name>]
        """
        from src.feats import FEATS
        lines = []
        if args:
            name = args.strip().lower()
            # Try to find the feat by name (case-insensitive, partial match allowed)
            for feat_key, feat in FEATS.items():
                if name in feat_key.lower():
                    lines.append(f"{feat.name}:")
                    lines.append(f"  Description: {feat.description}")
                    # Determine passive/active
                    if feat.effect is None:
                        lines.append("  Type: Passive (always on or handled automatically)")
                        lines.append("  Usage: This feat is always in effect or handled by the system.")
                    else:
                        # Heuristic: if effect expects a target, it's active
                        import inspect
                        params = inspect.signature(feat.effect).parameters
                        if any(p in params for p in ("target", "targets")):
                            lines.append("  Type: Active (requires a command or action)")
                            # Suggest usage based on feat name
                            if "disarm" in feat.name.lower():
                                lines.append("  Usage: Use the 'disarm <target>' command in combat.")
                            elif "trip" in feat.name.lower():
                                lines.append("  Usage: Use the 'trip <target>' command in combat.")
                            elif "bull rush" in feat.name.lower():
                                lines.append("  Usage: Use the 'bullrush <target>' command in combat.")
                            elif "grapple" in feat.name.lower():
                                lines.append("  Usage: Use the 'grapple <target>' command in combat.")
                            elif "overrun" in feat.name.lower():
                                lines.append("  Usage: Use the 'overrun <target>' command in combat.")
                            elif "sunder" in feat.name.lower():
                                lines.append("  Usage: Use the 'sunder <target>' command in combat.")
                            elif "whirlwind" in feat.name.lower():
                                lines.append("  Usage: Use the 'whirlwind' command in combat.")
                            elif "spring attack" in feat.name.lower():
                                lines.append("  Usage: Use the 'springattack <target>' command in combat.")
                            elif "stunning fist" in feat.name.lower():
                                lines.append("  Usage: Use the 'stunningfist <target>' command in combat.")
                            elif "feint" in feat.name.lower():
                                lines.append("  Usage: Use the 'feint <target>' command in combat.")
                            else:
                                lines.append("  Usage: This feat is used via a special command or action in combat.")
                        else:
                            lines.append("  Type: Passive (always on or handled automatically)")
                            lines.append("  Usage: This feat is always in effect or handled by the system.")
                    return "\n".join(lines)
            return "No such feat found. Type 'help feats' to see all feats."
        # No args: list all feats
        lines.append("Feats List:")
        for feat in sorted(FEATS.values(), key=lambda f: f.name):
            if feat.effect is None:
                ftype = "Passive"
            else:
                import inspect
                params = inspect.signature(feat.effect).parameters
                if any(p in params for p in ("target", "targets")):
                    ftype = "Active"
                else:
                    ftype = "Passive"
            lines.append(f"- {feat.name}: {ftype} - {feat.description}")
        lines.append("\nType 'help feats <feat name>' for details on a specific feat.")
        return "\n".join(lines)

    def cmd_levelup(self, character, args):
        """
        Level up the character by 1 and trigger Bonus Feat selection if eligible.
        """
        import asyncio
        import random
        old_level = getattr(character, 'class_level', 1)
        new_level = old_level + 1
        character.set_level(new_level)
        # TODO: Multiclass - prompt for class change
        # If running in async context, schedule bonus feat prompt
        try:
            # Use get_running_loop() to avoid deprecation warning in Python 3.10+
            loop = asyncio.get_running_loop()
            coro = character.check_levelup_bonus_feat(character.writer, character.reader)
            asyncio.ensure_future(coro)
        except RuntimeError:
            # No running loop - we're likely in a sync test context
            pass
        except Exception:
            pass

        # System 13: Award practice points on level-up
        from src.classes import CLASSES
        from src.combat import get_ability_mod
        class_data = CLASSES.get(getattr(character, 'char_class', ''), {})
        skill_points_per_level = class_data.get('skill_points', 2)
        int_mod = get_ability_mod(character, 'Int')
        points_gained = max(1, skill_points_per_level + int_mod)
        character.practice_points = getattr(character, 'practice_points', 0) + points_gained

        # System 22: HP Roll on level-up
        hit_die_raw = class_data.get('hit_die', 6)
        # Support both integer (e.g. 10) and string (e.g. "d10") hit_die formats
        if isinstance(hit_die_raw, str):
            try:
                die_size = int(hit_die_raw.lstrip('d'))
            except (ValueError, AttributeError):
                die_size = 6
        else:
            die_size = int(hit_die_raw)
        die_string = f"d{die_size}"
        con_mod = (getattr(character, 'con_score', 10) - 10) // 2
        hp_roll = random.randint(1, die_size)
        hp_gained = max(1, hp_roll + con_mod)
        character.max_hp += hp_gained
        character.hp += hp_gained
        hp_msg = f"You roll {die_string}{con_mod:+} for HP: +{hp_gained} HP! (Max HP: {character.max_hp})"

        return f"You have reached level {new_level}!\n{hp_msg}\nYou gained {points_gained} practice points."

    def cmd_tnl(self, character, args):
        """Show XP progress toward the next level (TNL = To Next Level).
        Usage: tnl / xp
        """
        from src.character import XP_TABLE
        current_level = getattr(character, 'level', 1)
        current_xp = getattr(character, 'xp', 0)
        next_level = current_level + 1
        xp_for_next = XP_TABLE.get(next_level, None)

        lines = ["=== Experience Progress ==="]
        lines.append(f"  Level: {current_level}")
        lines.append(f"  XP:    {current_xp}")

        if xp_for_next is None:
            lines.append("  You are at maximum level!")
            return "\n".join(lines)

        xp_this_level = XP_TABLE.get(current_level, 0)
        xp_range = xp_for_next - xp_this_level
        xp_earned = current_xp - xp_this_level
        xp_remaining = max(0, xp_for_next - current_xp)

        if xp_range > 0:
            pct = min(100, int((xp_earned / xp_range) * 100))
        else:
            pct = 100

        # Build progress bar (20 chars wide)
        filled = int(pct / 5)
        bar = "\u2588" * filled + "\u2591" * (20 - filled)
        lines.append(f"  Next:  {xp_for_next} XP (Level {next_level})")
        lines.append(f"  [{bar}] {pct}%")
        lines.append(f"  TNL:   {xp_remaining} XP remaining")
        return "\n".join(lines)

    # =========================================================================
    # System 12: Ranged Combat
    # =========================================================================

    def cmd_shoot(self, character, args):
        """Fire a ranged weapon at a target.
        Usage: shoot <target> / fire <target>
        """
        import random
        from src.combat import (
            calculate_attack_bonus, calculate_ac, get_ability_mod,
            start_combat, get_combat,
        )

        if not args:
            return "Shoot at whom? Usage: shoot <target>"

        # Check main-hand weapon is ranged
        weapon = character.equipment.get('main_hand') if hasattr(character, 'equipment') else None
        if not weapon:
            return "You need a ranged weapon equipped to shoot."

        item_type = getattr(weapon, 'item_type', '').lower()
        weapon_name_lower = getattr(weapon, 'name', '').lower()
        is_ranged = (
            item_type in ('bow', 'crossbow', 'ranged')
            or 'bow' in weapon_name_lower
            or 'crossbow' in weapon_name_lower
            or 'sling' in weapon_name_lower
        )
        if not is_ranged:
            return f"Your {weapon.name} is not a ranged weapon."

        target_name = args.strip().lower()
        target = None
        target_room = character.room
        in_same_room = False

        # Search current room first
        if character.room:
            for mob in character.room.mobs:
                if mob.name.lower().startswith(target_name) or target_name in mob.name.lower():
                    if getattr(mob, 'alive', True) and getattr(mob, 'hp', 1) > 0:
                        target = mob
                        target_room = character.room
                        in_same_room = True
                        break
            if not target:
                for player in character.room.players:
                    if player is not character and (
                        player.name.lower().startswith(target_name)
                        or target_name in player.name.lower()
                    ):
                        target = player
                        target_room = character.room
                        in_same_room = True
                        break

        # Search adjacent rooms (1 room away) if not found
        if not target and character.room and getattr(character.room, 'exits', None):
            for direction, exit_data in character.room.exits.items():
                adj_vnum = _resolve_exit(exit_data)
                adj_room = self.world.rooms.get(adj_vnum)
                if not adj_room:
                    continue
                for mob in adj_room.mobs:
                    if mob.name.lower().startswith(target_name) or target_name in mob.name.lower():
                        if getattr(mob, 'alive', True) and getattr(mob, 'hp', 1) > 0:
                            target = mob
                            target_room = adj_room
                            break
                if target:
                    break

        if not target:
            return f"No target '{args}' found here or in adjacent rooms."

        # Find ammo in inventory
        ammo = None
        for item in character.inventory:
            itype = getattr(item, 'item_type', '').lower()
            iname = getattr(item, 'name', '').lower()
            if itype in ('ammunition', 'arrow', 'bolt') or 'arrow' in iname or 'bolt' in iname:
                ammo = item
                break

        if not ammo:
            return "You have no ammunition (arrows or bolts) to fire."

        # Consume 1 ammo
        character.inventory.remove(ammo)

        # Ranged attacks use DEX instead of STR for the attack roll
        dex_mod = get_ability_mod(character, 'Dex')
        str_mod = get_ability_mod(character, 'Str')
        base_bonus = calculate_attack_bonus(character, target)
        attack_bonus = base_bonus - str_mod + dex_mod

        # Point Blank Shot: +1 attack and +1 damage in same room
        pbs_attack = 0
        pbs_damage = 0
        if in_same_room and hasattr(character, 'has_feat') and character.has_feat("Point Blank Shot"):
            pbs_attack = 1
            pbs_damage = 1
        attack_bonus += pbs_attack

        roll = random.randint(1, 20)
        ac = calculate_ac(target, character)

        if roll == 1:
            return f"You fire at {target.name} — MISS (fumble)! (1 {ammo.name} used)"

        is_crit = False
        if roll == 20:
            confirm = random.randint(1, 20)
            if confirm + attack_bonus >= ac:
                is_crit = True

        if roll == 20 or roll + attack_bonus >= ac:
            dmg_dice = getattr(weapon, 'damage', None)
            if dmg_dice:
                damage = sum(random.randint(1, dmg_dice[1]) for _ in range(dmg_dice[0]))
                if len(dmg_dice) > 2:
                    damage += dmg_dice[2]
            else:
                damage = random.randint(1, 6)

            damage += pbs_damage
            damage = max(1, damage)

            if is_crit:
                damage *= 2

            target.hp = max(0, target.hp - damage)
            crit_msg = " CRITICAL HIT!" if is_crit else ""
            loc_msg = "" if in_same_room else " (across the room)"
            result = (
                f"You fire at {target.name}{loc_msg} and hit for {damage} damage!"
                f"{crit_msg} (1 {ammo.name} used)"
            )

            if target.hp <= 0:
                if hasattr(target, 'alive'):
                    target.alive = False
                result += f"\n{target.name} has been slain!"
                from src.combat import award_xp, generate_loot
                xp = award_xp(character, target)
                if xp:
                    result += f" (+{xp} XP)"
                loot_msg = generate_loot(character, target, target_room)
                if loot_msg:
                    result += f"\n{loot_msg}"
            else:
                if in_same_room:
                    combat = get_combat(character.room)
                    if not combat:
                        start_combat(character.room, character, target)
                    character.set_combat_target(target)

            return result
        else:
            return (
                f"You fire at {target.name} — MISS "
                f"({roll}+{attack_bonus}={roll + attack_bonus} vs AC {ac}). "
                f"(1 {ammo.name} used)"
            )

    # =========================================================================
    # System 24: Guild / Clan
    # =========================================================================

    def _load_guilds(self):
        """Load guilds from data/guilds.json."""
        import os
        import json
        guild_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'guilds.json')
        try:
            with open(guild_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_guilds(self, guilds):
        """Save guilds dict to data/guilds.json atomically."""
        import os
        import json
        guild_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'guilds.json')
        tmp_path = guild_path + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(guilds, f, indent=2)
        os.replace(tmp_path, guild_path)

    def cmd_guild(self, character, args):
        """Guild / Clan system commands.
        Usage: guild [info|create|invite|accept|leave|kick|promote|demote|bank|motd|disband|who]
        """
        guild_ranks = ["Recruit", "Member", "Officer", "Leader"]
        args = (args or "").strip()
        parts = args.split(None, 1)
        subcmd = parts[0].lower() if parts else "info"
        sub_args = parts[1] if len(parts) > 1 else ""

        guilds = self._load_guilds()
        char_name = character.name
        char_guild = getattr(character, 'guild_name', None)
        char_rank = getattr(character, 'guild_rank', None)

        if subcmd in ("info", ""):
            if not char_guild or char_guild not in guilds:
                return "You are not a member of any guild.\nUse 'guild create <name>' to found one."
            g = guilds[char_guild]
            lines = [f"=== Guild: {g['name']} ==="]
            lines.append(f"  Leader: {g['leader']}")
            lines.append(f"  Members: {len(g['members'])}")
            for mname, mrank in sorted(g['members'].items()):
                lines.append(f"    {mname}: {mrank}")
            lines.append(f"  Bank Gold: {g.get('bank_gold', 0)} gp")
            if g.get('motd'):
                lines.append(f"  MOTD: {g['motd']}")
            return "\n".join(lines)

        elif subcmd == "create":
            if not sub_args:
                return "Usage: guild create <name>"
            if char_guild:
                return f"You are already a member of {char_guild}. Leave first."
            guild_name = sub_args.strip()
            if guild_name in guilds:
                return f"A guild named '{guild_name}' already exists."
            cost = 1000
            if getattr(character, 'gold', 0) < cost:
                return (f"You need {cost} gold to found a guild. "
                        f"You have {getattr(character, 'gold', 0)} gp.")
            character.gold -= cost
            guilds[guild_name] = {
                "name": guild_name,
                "leader": char_name,
                "members": {char_name: "Leader"},
                "bank_gold": 0,
                "motd": "",
            }
            character.guild_name = guild_name
            character.guild_rank = "Leader"
            self._save_guilds(guilds)
            if hasattr(character, 'save'):
                character.save()
            return f"You have founded the guild '{guild_name}'! ({cost} gp deducted)"

        elif subcmd == "invite":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            if char_rank not in ("Leader", "Officer"):
                return "Only Leaders and Officers can invite players."
            if not sub_args:
                return "Usage: guild invite <player>"
            target = self._find_player_by_name(sub_args.strip())
            if not target:
                return f"Player '{sub_args}' is not online."
            if getattr(target, 'guild_name', None):
                return f"{target.name} is already in a guild."
            target.guild_invite = char_guild
            return f"You invite {target.name} to join {char_guild}. They must type 'guild accept' to join."

        elif subcmd == "accept":
            invite = getattr(character, 'guild_invite', None)
            if not invite or invite not in guilds:
                return "You have no pending guild invitation."
            if char_guild:
                return f"You are already in {char_guild}. Leave first."
            g = guilds[invite]
            g['members'][char_name] = "Recruit"
            character.guild_name = invite
            character.guild_rank = "Recruit"
            character.guild_invite = None
            self._save_guilds(guilds)
            if hasattr(character, 'save'):
                character.save()
            return f"You have joined {invite} as a Recruit!"

        elif subcmd == "leave":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            g = guilds[char_guild]
            if char_rank == "Leader" and len(g['members']) > 1:
                return "You must promote another member to Leader before leaving."
            g['members'].pop(char_name, None)
            if not g['members']:
                del guilds[char_guild]
            character.guild_name = None
            character.guild_rank = None
            self._save_guilds(guilds)
            if hasattr(character, 'save'):
                character.save()
            return f"You have left {char_guild}."

        elif subcmd == "kick":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            if char_rank not in ("Leader", "Officer"):
                return "Only Leaders and Officers can kick members."
            if not sub_args:
                return "Usage: guild kick <player>"
            target_name = sub_args.strip()
            g = guilds[char_guild]
            if target_name not in g['members']:
                return f"{target_name} is not in your guild."
            if g['members'][target_name] == "Leader":
                return "You cannot kick the guild leader."
            g['members'].pop(target_name)
            target = self._find_player_by_name(target_name)
            if target:
                target.guild_name = None
                target.guild_rank = None
            self._save_guilds(guilds)
            return f"{target_name} has been kicked from {char_guild}."

        elif subcmd == "promote":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            if char_rank != "Leader":
                return "Only the Leader can promote members."
            if not sub_args:
                return "Usage: guild promote <player>"
            target_name = sub_args.strip()
            g = guilds[char_guild]
            if target_name not in g['members']:
                return f"{target_name} is not in your guild."
            current_rank = g['members'][target_name]
            idx = guild_ranks.index(current_rank) if current_rank in guild_ranks else 0
            if idx >= len(guild_ranks) - 1:
                return f"{target_name} is already at the highest rank."
            new_rank = guild_ranks[idx + 1]
            if new_rank == "Leader":
                g['members'][char_name] = "Officer"
                character.guild_rank = "Officer"
            g['members'][target_name] = new_rank
            target = self._find_player_by_name(target_name)
            if target:
                target.guild_rank = new_rank
            self._save_guilds(guilds)
            return f"{target_name} has been promoted to {new_rank}."

        elif subcmd == "demote":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            if char_rank != "Leader":
                return "Only the Leader can demote members."
            if not sub_args:
                return "Usage: guild demote <player>"
            target_name = sub_args.strip()
            g = guilds[char_guild]
            if target_name not in g['members']:
                return f"{target_name} is not in your guild."
            current_rank = g['members'][target_name]
            idx = guild_ranks.index(current_rank) if current_rank in guild_ranks else 0
            if idx <= 0:
                return f"{target_name} is already at the lowest rank."
            new_rank = guild_ranks[idx - 1]
            g['members'][target_name] = new_rank
            target = self._find_player_by_name(target_name)
            if target:
                target.guild_rank = new_rank
            self._save_guilds(guilds)
            return f"{target_name} has been demoted to {new_rank}."

        elif subcmd == "bank":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            g = guilds[char_guild]
            bank_parts = sub_args.split(None, 1)
            if not bank_parts or not bank_parts[0]:
                return (f"Guild bank holds {g.get('bank_gold', 0)} gp.\n"
                        "Usage: guild bank deposit <amount> / guild bank withdraw <amount>")
            bank_action = bank_parts[0].lower()
            bank_amount_str = bank_parts[1] if len(bank_parts) > 1 else ""
            try:
                amount = int(bank_amount_str)
                if amount <= 0:
                    raise ValueError("amount must be positive")
            except (ValueError, TypeError):
                return "Usage: guild bank deposit/withdraw <amount>"
            if bank_action == "deposit":
                if getattr(character, 'gold', 0) < amount:
                    return f"You only have {getattr(character, 'gold', 0)} gp."
                character.gold -= amount
                g['bank_gold'] = g.get('bank_gold', 0) + amount
                self._save_guilds(guilds)
                return f"Deposited {amount} gp to the guild bank. Bank total: {g['bank_gold']} gp."
            elif bank_action == "withdraw":
                if char_rank not in ("Leader", "Officer"):
                    return "Only Leaders and Officers can withdraw from the guild bank."
                if g.get('bank_gold', 0) < amount:
                    return f"The guild bank only holds {g.get('bank_gold', 0)} gp."
                g['bank_gold'] -= amount
                character.gold = getattr(character, 'gold', 0) + amount
                self._save_guilds(guilds)
                return f"Withdrew {amount} gp from the guild bank. Bank total: {g['bank_gold']} gp."
            else:
                return "Usage: guild bank deposit/withdraw <amount>"

        elif subcmd == "motd":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            if char_rank != "Leader":
                return "Only the Leader can set the message of the day."
            guilds[char_guild]['motd'] = sub_args.strip()
            self._save_guilds(guilds)
            return f"Guild MOTD set to: {sub_args.strip()}"

        elif subcmd == "disband":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            if char_rank != "Leader":
                return "Only the Leader can disband the guild."
            for player in self.world.players:
                if getattr(player, 'guild_name', None) == char_guild:
                    player.guild_name = None
                    player.guild_rank = None
            del guilds[char_guild]
            self._save_guilds(guilds)
            return f"You have disbanded {char_guild}."

        elif subcmd == "who":
            if not char_guild or char_guild not in guilds:
                return "You are not in a guild."
            g = guilds[char_guild]
            online_members = []
            for player in self.world.players:
                if getattr(player, 'guild_name', None) == char_guild:
                    rank = g['members'].get(player.name, "Member")
                    online_members.append(f"  {player.name} [{rank}]")
            if not online_members:
                return f"No members of {char_guild} are currently online."
            lines = [f"=== {char_guild} - Online Members ==="]
            lines.extend(online_members)
            return "\n".join(lines)

        else:
            return ("Guild commands: info, create <name>, invite <player>, accept, leave,\n"
                    "  kick <player>, promote <player>, demote <player>,\n"
                    "  bank deposit/withdraw <amount>, motd <msg>, disband, who")

    # =========================================================================
    # System 13: Practice / Train at Guildmaster
    # =========================================================================

    def _find_trainer(self, character):
        """Return the first trainer NPC (mob with 'trainer' in flags) in the room."""
        if not character.room:
            return None
        for mob in character.room.mobs:
            flags = getattr(mob, 'flags', []) or []
            if 'trainer' in flags:
                return mob
        return None

    def cmd_practice(self, character, args):
        """Practice skills with a trainer NPC.
        Usage: practice
               practice <skill> [amount]
        """
        from src.classes import CLASSES

        trainer = self._find_trainer(character)
        if not trainer:
            return "You need to find a guildmaster or trainer to practice skills."

        practice_points = getattr(character, 'practice_points', 0)

        if not args:
            lines = [
                f"{trainer.name} says: 'You have {practice_points} practice points available.'",
                "Your skills:",
            ]
            if character.skills:
                for skill_name, rank in sorted(character.skills.items()):
                    lines.append(f"  {skill_name}: {rank}")
            else:
                lines.append("  (no skills learned yet)")
            return "\n".join(lines)

        parts = args.strip().split()
        if len(parts) > 1 and parts[-1].isdigit():
            skill_name_parts = parts[:-1]
            amount_str = parts[-1]
        else:
            skill_name_parts = parts
            amount_str = "1"

        try:
            amount = max(1, int(amount_str))
        except ValueError:
            amount = 1

        skill_name = " ".join(skill_name_parts)

        all_skills = [
            "Appraise", "Balance", "Bluff", "Climb", "Concentration", "Craft (any)",
            "Decipher Script", "Diplomacy", "Disable Device", "Disguise", "Escape Artist",
            "Forgery", "Gather Information", "Handle Animal", "Heal", "Hide", "Intimidate",
            "Jump", "Knowledge (arcana)", "Knowledge (dungeoneering)", "Knowledge (geography)",
            "Knowledge (history)", "Knowledge (local)", "Knowledge (nature)",
            "Knowledge (nobility and royalty)", "Knowledge (religion)", "Knowledge (the planes)",
            "Listen", "Move Silently", "Open Lock", "Perform (any)", "Profession (any)",
            "Ride", "Search", "Sense Motive", "Sleight of Hand", "Spellcraft", "Spot",
            "Survival", "Swim", "Tumble", "Use Magic Device", "Use Rope",
        ]
        matched_skill = None
        skill_name_lower = skill_name.lower()
        for s in all_skills:
            if s.lower() == skill_name_lower or s.lower().startswith(skill_name_lower):
                matched_skill = s
                break
        if not matched_skill:
            for s in character.skills:
                if s.lower() == skill_name_lower or s.lower().startswith(skill_name_lower):
                    matched_skill = s
                    break

        if not matched_skill:
            return f"Unknown skill '{skill_name}'. Type 'practice' to see your skills."

        level = getattr(character, 'class_level', getattr(character, 'level', 1))
        class_data = CLASSES.get(getattr(character, 'char_class', ''), {})
        class_skills = class_data.get('class_skills', [])

        is_class_skill = matched_skill in class_skills
        max_ranks = level + 3 if is_class_skill else (level + 3) // 2
        cost_per_rank = 1 if is_class_skill else 2

        current_rank = character.skills.get(matched_skill, 0)

        if current_rank >= max_ranks:
            return (
                f"You have already maxed {matched_skill} "
                f"({'class' if is_class_skill else 'cross-class'} skill, max {max_ranks})."
            )

        ranks_available = max_ranks - current_rank
        ranks_to_buy = min(amount, ranks_available)
        total_cost = ranks_to_buy * cost_per_rank

        if practice_points < total_cost:
            affordable = practice_points // cost_per_rank
            if affordable <= 0:
                return (
                    f"You need {cost_per_rank} practice point(s) to practice {matched_skill}. "
                    f"You have {practice_points}."
                )
            ranks_to_buy = affordable
            total_cost = ranks_to_buy * cost_per_rank

        character.skills[matched_skill] = current_rank + ranks_to_buy
        character.practice_points = practice_points - total_cost
        new_rank = character.skills[matched_skill]
        cross_msg = " (cross-class, costs 2 pts/rank)" if not is_class_skill else ""
        return (
            f"You practice {matched_skill}{cross_msg}.\n"
            f"  Rank: {current_rank} -> {new_rank} (max {max_ranks})\n"
            f"  Practice points remaining: {character.practice_points}"
        )

    def cmd_train(self, character, args):
        """Train an ability score with a trainer NPC.
        Usage: train <ability>
        Costs 500 gp x current score. Each ability trainable once per 5 levels.
        """
        trainer = self._find_trainer(character)
        if not trainer:
            return "You need to find a guildmaster or trainer to train your abilities."

        if not args:
            return "\n".join([
                f"{trainer.name} says: 'I can train your body and mind. "
                "Specify an ability: str, dex, con, int, wis, cha.'",
                "Cost: 500 gp x current ability score.",
                "Limit: each ability once per 5 character levels.",
            ])

        ability_map = {
            'str': 'str_score', 'strength': 'str_score',
            'dex': 'dex_score', 'dexterity': 'dex_score',
            'con': 'con_score', 'constitution': 'con_score',
            'int': 'int_score', 'intelligence': 'int_score',
            'wis': 'wis_score', 'wisdom': 'wis_score',
            'cha': 'cha_score', 'charisma': 'cha_score',
        }
        ability_key = args.strip().lower()
        attr_name = ability_map.get(ability_key)
        if not attr_name:
            return f"Unknown ability '{args}'. Use: str, dex, con, int, wis, cha."

        ability_display = ability_key.capitalize()
        current_score = getattr(character, attr_name, 10)
        gold = getattr(character, 'gold', 0)
        cost = 500 * current_score
        level = getattr(character, 'level', getattr(character, 'class_level', 1))

        if not hasattr(character, 'trained_abilities'):
            character.trained_abilities = {}

        last_trained = character.trained_abilities.get(attr_name, 0)
        if last_trained > 0 and level - last_trained < 5:
            next_allowed = last_trained + 5
            return (
                f"You cannot train {ability_display} again yet. "
                f"You may retrain it at level {next_allowed} (currently level {level})."
            )

        if gold < cost:
            return (
                f"Training {ability_display} from {current_score} costs {cost} gold. "
                f"You only have {gold} gold."
            )

        character.gold -= cost
        setattr(character, attr_name, current_score + 1)
        character.trained_abilities[attr_name] = level

        if attr_name == 'con_score':
            old_con_mod = (current_score - 10) // 2
            new_con_mod = ((current_score + 1) - 10) // 2
            hp_gain = new_con_mod - old_con_mod
            if hp_gain > 0:
                character.max_hp += hp_gain
                character.hp = min(character.hp + hp_gain, character.max_hp)

        if attr_name == 'dex_score':
            if hasattr(character, '_recalculate_ac'):
                character._recalculate_ac()

        return (
            f"{trainer.name} puts you through grueling training.\n"
            f"Your {ability_display} increases from {current_score} to {current_score + 1}!\n"
            f"You paid {cost} gold. Remaining gold: {character.gold}"
        )

    # =========================================================================
    # Equipment Commands
    # =========================================================================

    def cmd_wear(self, character, args):
        """
        Equip an item from your inventory.
        Usage: wear <item name> [slot]
               wear all  — equip all equippable items
        """
        if not args:
            return "Wear what? Usage: wear <item name> or wear all"

        if args.strip().lower() == "all":
            results = []
            equippable_types = {"weapon", "armor", "shield", "ring", "helmet", "boots", "gloves", "cloak", "belt", "amulet"}
            for item in list(character.inventory):
                if hasattr(item, 'item_type') and item.item_type in equippable_types:
                    success, msg, _ = character.equip_item(item)
                    results.append(msg)
                elif hasattr(item, 'slot') and item.slot:
                    success, msg, _ = character.equip_item(item)
                    results.append(msg)
            return "\n".join(results) if results else "Nothing in your inventory can be equipped."

        parts = args.split()
        item_name = parts[0].lower()
        slot = parts[1].lower() if len(parts) > 1 else None

        # Find item in inventory — match full multi-word names
        item = None
        full_name = args.lower().strip()
        for inv_item in character.inventory:
            if full_name in inv_item.name.lower() or inv_item.name.lower().startswith(full_name):
                item = inv_item
                break
        if not item:
            # Try first word only
            for inv_item in character.inventory:
                if inv_item.name.lower().startswith(item_name) or item_name in inv_item.name.lower():
                    item = inv_item
                    break

        if not item:
            return f"You don't have '{args}' in your inventory."

        success, msg, unequipped = character.equip_item(item, slot)
        return msg

    def cmd_remove(self, character, args):
        """
        Remove an equipped item.
        Usage: remove <slot or item name>
               remove all  — unequip everything
        """
        if not args:
            return "Remove what? Usage: remove <slot or item name> or remove all"

        from src.character import EQUIPMENT_SLOTS
        arg = args.lower().strip()

        if arg == "all":
            results = []
            for slot, item in list(character.equipment.items()):
                if item:
                    success, msg, removed = character.unequip_item(slot)
                    results.append(msg)
            return "\n".join(results) if results else "You have nothing equipped."

        # Check if it's a slot name
        if arg in EQUIPMENT_SLOTS:
            success, msg, item = character.unequip_item(arg)
            return msg

        # Try to find by item name
        for slot, item in character.equipment.items():
            if item and (arg in item.name.lower() or item.name.lower().startswith(arg)):
                success, msg, removed = character.unequip_item(slot)
                return msg

        return f"You don't have '{args}' equipped."

    def cmd_equipment(self, character, args):
        """
        Display currently equipped items.
        Usage: equipment
        """
        from src.character import EQUIPMENT_SLOTS

        lines = ["=== Equipment ==="]

        slot_names = {
            "head": "Head",
            "face": "Face",
            "neck": "Neck",
            "shoulders": "Shoulders",
            "body": "Body/Armor",
            "torso": "Torso",
            "arms": "Arms",
            "hands": "Hands",
            "ring_left": "Ring (L)",
            "ring_right": "Ring (R)",
            "waist": "Waist",
            "feet": "Feet",
            "main_hand": "Main Hand",
            "off_hand": "Off Hand",
        }

        for slot in EQUIPMENT_SLOTS:
            item = character.equipment.get(slot)
            slot_display = slot_names.get(slot, slot.title())
            if item:
                ac_info = f" (AC +{item.ac_bonus})" if getattr(item, 'ac_bonus', 0) else ""
                dmg_info = ""
                if getattr(item, 'damage', None):
                    d = item.damage
                    dmg_info = f" ({d[0]}d{d[1]}+{d[2]})" if len(d) > 2 else f" ({d[0]}d{d[1]})"
                lines.append(f"  {slot_display:12}: {item.name}{ac_info}{dmg_info}")
            else:
                lines.append(f"  {slot_display:12}: -empty-")

        lines.append(f"\nAC: {character.ac}")
        lines.append(f"Gold: {getattr(character, 'gold', 0)} gp")

        return "\n".join(lines)

    # =========================================================================
    # Rest and Recovery Commands
    # =========================================================================

    def cmd_rest(self, character, args):
        """
        Rest to recover HP and spell slots.
        Usage: rest [short|long]
        - short: 1 hour rest, recover some HP
        - long: 8 hour rest, full recovery (default)

        You must be in a safe room to rest.
        """
        # Check for safe room
        room_flags = getattr(character.room, 'flags', [])
        if 'safe' not in room_flags and 'inn' not in room_flags and 'temple' not in room_flags:
            return "You cannot rest here. Find an inn or safe area."

        # Check for combat
        from src.combat import get_combat
        combat = get_combat(character.room)
        if combat and combat.is_active:
            return "You cannot rest while in combat!"

        # Determine rest type
        rest_type = args.lower().strip() if args else "long"

        if rest_type in ("short", "s", "1"):
            hours = 1
        else:  # Default to long rest
            hours = 8

        # Inn/tavern bonus: short rest grants full recovery
        room_flags = getattr(character.room, 'flags', [])
        if hours == 1 and ('inn' in room_flags or 'tavern' in room_flags):
            result = character.rest(8)  # Full recovery
            return "The comfortable inn allows you to rest fully.\n" + result

        return character.rest(hours)

    # =========================================================================
    # Status and Condition Commands
    # =========================================================================

    def cmd_sense(self, character, args):
        """Actively focus your Kin-sense to read the room or a specific target.
        Usage: sense          - Read all presences in the room
               sense <target> - Focus on a specific entity
        """
        from src.kin_sense import get_kin_sense_readout, get_resonance, get_racial_bonus, get_wis_mod, ELEMENT_FEEL, RESONANCE_FEEL, _is_familiar, _describe_harmonic, get_element_for_race

        race = getattr(character, 'race', '')
        if race == "Farborn Human":
            return "You have no Kin-sense. The resonance of Oreka is silent to you."
        if getattr(character, 'deceivers_feat_active', False):
            return "Your Kin-sense is suppressed while the Deceiver's Feat is active. You are blind to resonance."

        if not args:
            # Full room readout
            readout = get_kin_sense_readout(character, character.room)
            if readout:
                return readout
            return "\033[1;35m[Kin-Sense]\033[0m The room is empty of notable resonance."

        # Focus on specific target
        target_name = args.strip().lower()
        target = None
        for mob in getattr(character.room, 'mobs', []):
            if getattr(mob, 'alive', True) and target_name in mob.name.lower():
                target = mob
                break
        if not target:
            for player in getattr(character.room, 'players', []):
                if player is not character and target_name in player.name.lower():
                    target = player
                    break
        if not target:
            return f"You don't see '{args}' here."

        cat, element, race_name = get_resonance(target)
        PURPLE = "\033[1;35m"
        RESET = "\033[0m"
        prefix = f"{PURPLE}[Kin-Sense]{RESET} "

        if cat == "none":
            return prefix + f"{target.name} does not register on your Kin-sense at all — absent, like furniture."
        if cat == "void":
            return prefix + f"{target.name} radiates Absolute Silence — a deliberate, predatory void where a soul should be. Domnathar."
        if cat == "null":
            return prefix + f"{target.name} is a wound in the harmony — an aching absence. Silentborn or Severed."
        if cat == "raw_static":
            elem_desc = f" The elemental force feels {ELEMENT_FEEL.get(element, 'primal')}." if element else ""
            return prefix + f"{target.name} radiates overwhelming elemental power. Painful to perceive directly.{elem_desc}"
        if cat == "breach_static":
            return prefix + f"{target.name} registers as Breach Static — alien, unsettling, a wrong note. Not native to Oreka's harmony."
        if cat == "wild_static":
            return prefix + f"{target.name} registers as Wild Static — alive, present, but fundamentally not Kin."
        if cat == "warm_static":
            return prefix + f"{target.name} is barely perceptible — faint background warmth."
        if cat == "harmonic":
            viewer_element = get_element_for_race(race)
            familiar = _is_familiar(character, target)
            desc = _describe_harmonic(target, element, race_name, character, viewer_element, familiar)
            return prefix + desc.capitalize()

        return prefix + f"You sense {target.name}, but the resonance is unclear."

    def cmd_conditions(self, character, args):
        """
        Display current conditions affecting you.
        Usage: conditions
        """
        from src.conditions import describe_condition

        lines = ["=== Active Conditions ==="]

        if not character.conditions and not character.active_conditions:
            lines.append("  None")
            return "\n".join(lines)

        # Permanent conditions
        for cond in character.conditions:
            if cond not in character.active_conditions:
                desc = describe_condition(cond)
                lines.append(f"  {desc}")

        # Timed conditions
        for cond, duration in character.active_conditions.items():
            desc = describe_condition(cond)
            lines.append(f"  {desc} ({duration} rounds remaining)")

        return "\n".join(lines)

    def cmd_status(self, character, args):
        """
        Display detailed character status including health state.
        Usage: status
        """
        from src.character import HealthStatus

        lines = ["=== Character Status ==="]
        lines.append(f"Name: {character.name}")
        lines.append(f"Race: {character.race}")
        lines.append(f"Class: {character.char_class} Level {character.class_level}")
        lines.append("")

        # Health status
        status = character.health_status
        status_colors = {
            HealthStatus.HEALTHY: "Healthy",
            HealthStatus.DISABLED: "DISABLED (0 HP)",
            HealthStatus.DYING: "DYING!",
            HealthStatus.STABLE: "Stable (unconscious)",
            HealthStatus.DEAD: "DEAD",
        }
        lines.append(f"HP: {character.hp}/{character.max_hp}")
        lines.append(f"Status: {status_colors.get(status, 'Unknown')}")
        lines.append(f"AC: {character.ac}")
        lines.append("")

        # Ability scores
        lines.append("Abilities:")
        for stat in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
            score = getattr(character, f'{stat}_score', 10)
            mod = (score - 10) // 2
            lines.append(f"  {stat.upper()}: {score} ({mod:+d})")

        # Active conditions summary
        if character.conditions or character.active_conditions:
            lines.append("")
            lines.append("Conditions: " + ", ".join(character.conditions | set(character.active_conditions.keys())))

        return "\n".join(lines)

    # =========================================================================
    # Combat Commands
    # =========================================================================

    def cmd_fullattack(self, character, args):
        """
        Make a full attack (all iterative attacks based on BAB).
        Usage: fullattack <target>
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check
        from src.combat import attack as combat_attack

        if not args:
            return "Attack who? Usage: fullattack <target>"

        # Find target mob
        target = None
        target_name = args.lower()
        for mob in character.room.mobs:
            if mob.alive and target_name in mob.name.lower():
                target = mob
                break

        if not target:
            return f"You don't see '{args}' here."

        # Execute full attack
        return combat_attack(character, target, is_full_attack=True)

    # =========================================================================
    # Fix 39: Charge Command
    # =========================================================================

    def cmd_charge(self, character, args):
        """Charge at a target: +2 to attack, -2 to AC until next turn.
        Usage: charge <target>
        """
        from src.character import State
        from src.combat import attack as combat_attack, start_combat as init_combat

        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        if hasattr(character, 'can_act') and not character.can_act():
            return "You cannot act in your current condition!"

        # Need a target
        target_name = (args or "").strip()
        if not target_name and hasattr(character, 'combat_target') and character.combat_target:
            target = character.combat_target
        else:
            if not target_name:
                return "Charge whom? Usage: charge <target>"
            target = None
            for mob in character.room.mobs:
                if mob.alive and target_name.lower() in mob.name.lower():
                    target = mob
                    break
            if not target:
                for player in character.room.players:
                    if player.name.lower() == target_name.lower() and player != character:
                        target = player
                        break

        if not target:
            return f"You don't see '{target_name}' here."

        # Apply charge effect: +2 attack (temp), -2 AC (charging condition)
        character._charging = True
        if not hasattr(character, 'temp_attack_bonus'):
            character.temp_attack_bonus = 0
        character.temp_attack_bonus += 2

        # Mark -2 AC via a simple flag checked in calculate_ac
        if not hasattr(character, 'active_conditions'):
            character.active_conditions = {}
        character.active_conditions['charging'] = 1  # lasts 1 round

        # Enter combat if not already
        combat = init_combat(character.room, character, target)
        character.state = State.COMBAT
        character.set_combat_target(target)

        results = [f"You charge {target.name}! (+2 attack, -2 AC this round)"]
        result = combat_attack(character, target)
        results.append(result)

        # Check target death
        if hasattr(target, 'hp') and target.hp <= 0:
            if hasattr(target, 'alive'):
                target.alive = False
            results.append(f"{target.name} has been slain!")

        return "\n".join(results)

    # =========================================================================
    # Fix 40: Total Defense Command
    # =========================================================================

    def cmd_totaldefense(self, character, args):
        """Take the Total Defense action: forfeit attacks, gain +4 dodge to AC.
        Usage: totaldefense
        """
        from src.character import State

        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        if character.state != State.COMBAT:
            return "You must be in combat to use Total Defense."

        character._total_defense = True
        return ("You adopt a total defensive stance! "
                "You forfeit your attacks this round but gain +4 dodge bonus to AC.")

    # =========================================================================
    # Fix 41: Fighting Defensively Command
    # =========================================================================

    def cmd_fightdef(self, character, args):
        """Toggle fighting defensively: -4 to attacks, +2 dodge bonus to AC.
        Usage: fightdef
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        current = getattr(character, '_fighting_defensively', False)
        character._fighting_defensively = not current

        if character._fighting_defensively:
            return ("Fighting defensively activated. "
                    "(-4 to attacks, +2 dodge bonus to AC)")
        else:
            return "Fighting defensively deactivated."

    # =========================================================================
    # Admin Condition Commands
    # =========================================================================

    def cmd_addcondition(self, character, args):
        """
        Add a condition to a target (admin command).
        Usage: @addcondition <target> <condition> [duration]
        Example: @addcondition goblin stunned 3
        """
        if not character.is_immortal:
            return "Command restricted to immortals!"

        from src import conditions as cond

        parts = args.split()
        if len(parts) < 2:
            return "Usage: @addcondition <target> <condition> [duration]"

        target_name = parts[0].lower()
        condition_name = parts[1].lower()
        duration = int(parts[2]) if len(parts) > 2 else None

        # Validate condition exists
        condition = cond.get_condition(condition_name)
        if not condition:
            valid_conditions = ", ".join(sorted(cond.get_condition_list()))
            return f"Unknown condition: {condition_name}\nValid conditions: {valid_conditions}"

        # Find target (player or mob)
        target = None
        for p in character.room.players:
            if p.name.lower() == target_name:
                target = p
                break
        if not target:
            for m in character.room.mobs:
                if m.name.lower() == target_name and m.alive:
                    target = m
                    break

        if not target:
            return f"No target named '{parts[0]}' found in this room."

        # Apply condition
        if hasattr(target, 'add_timed_condition'):
            target.add_timed_condition(condition_name, duration)
        else:
            target.conditions.add(condition_name)
            if duration:
                target.active_conditions[condition_name] = duration

        duration_msg = f" for {duration} rounds" if duration else " (permanent)"
        return f"Applied {condition.name} to {target.name}{duration_msg}."

    def cmd_removecondition(self, character, args):
        """
        Remove a condition from a target (admin command).
        Usage: @removecondition <target> <condition>
        Example: @removecondition goblin stunned
        """
        if not character.is_immortal:
            return "Command restricted to immortals!"

        parts = args.split()
        if len(parts) < 2:
            return "Usage: @removecondition <target> <condition>"

        target_name = parts[0].lower()
        condition_name = parts[1].lower()

        # Find target (player or mob)
        target = None
        for p in character.room.players:
            if p.name.lower() == target_name:
                target = p
                break
        if not target:
            for m in character.room.mobs:
                if m.name.lower() == target_name and m.alive:
                    target = m
                    break

        if not target:
            return f"No target named '{parts[0]}' found in this room."

        # Check if target has condition
        if not (condition_name in getattr(target, 'conditions', set()) or
                condition_name in getattr(target, 'active_conditions', {})):
            return f"{target.name} does not have the {condition_name} condition."

        # Remove condition
        if hasattr(target, 'remove_condition'):
            target.remove_condition(condition_name)
        else:
            target.conditions.discard(condition_name)

        if condition_name in getattr(target, 'active_conditions', {}):
            del target.active_conditions[condition_name]

        return f"Removed {condition_name} from {target.name}."

    def cmd_listconditions(self, character, args):
        """
        List all available conditions.
        Usage: @listconditions [category]
        Categories: physical, mental, other, combat, all
        """
        from src import conditions as cond

        category = args.lower() if args else "all"

        # Define categories
        physical = ['blinded', 'dazzled', 'deafened', 'entangled', 'exhausted', 'fatigued',
                   'grappled', 'helpless', 'paralyzed', 'petrified', 'pinned', 'prone', 'stunned']
        mental = ['confused', 'cowering', 'dazed', 'fascinated', 'frightened', 'nauseated',
                 'panicked', 'shaken']
        other = ['incorporeal', 'invisible', 'sickened', 'staggered', 'stable', 'unconscious']
        combat = ['flanked', 'flat_footed', 'silenced', 'bound', 'gagged']

        if category == "physical":
            conditions_to_show = physical
        elif category == "mental":
            conditions_to_show = mental
        elif category == "other":
            conditions_to_show = other
        elif category == "combat":
            conditions_to_show = combat
        else:
            conditions_to_show = cond.get_condition_list()

        lines = [f"=== Conditions ({category.title()}) ==="]
        for cond_name in sorted(conditions_to_show):
            condition = cond.get_condition(cond_name)
            if condition:
                lines.append(f"  {condition.name}: {condition.description[:60]}...")

        return "\n".join(lines)

    # =========================================================================
    # Combat Maneuver Commands
    # =========================================================================

    def _find_target(self, character, target_name):
        """Find a target mob or player in the room by name.

        Searches mobs first, then players (for PvP). Excludes the character
        performing the search and dead targets.
        """
        target_name = target_name.lower()

        # First check mobs
        for mob in character.room.mobs:
            if mob.alive and target_name in mob.name.lower():
                return mob

        # Then check players (PvP)
        for player in getattr(character.room, 'players', []):
            if player == character:
                continue  # Can't target yourself
            if player.name.lower() == target_name or target_name in player.name.lower():
                # Check if player is alive
                if getattr(player, 'hp', 0) > 0:
                    return player

        return None

    def _check_can_act(self, character):
        """Check if character can take actions."""
        if hasattr(character, 'can_act') and not character.can_act():
            return "You cannot act in your current condition!"
        return None

    def _ensure_combat(self, character, target):
        """Ensure character and target are in combat. Returns combat instance."""
        from src.combat import get_combat, start_combat as init_combat
        from src.chat import broadcast_to_room
        combat = get_combat(character.room)
        if not combat:
            combat = init_combat(character.room, character, target)
            character.state = State.COMBAT
            character.set_combat_target(target)
            if hasattr(target, 'state'):
                target.state = State.COMBAT
        else:
            combat.add_combatant(character)
            combat.add_combatant(target)
            if character.state != State.COMBAT:
                character.state = State.COMBAT
                character.set_combat_target(target)
        return combat

    def cmd_disarm(self, character, args):
        """
        Attempt to disarm an opponent.
        Usage: disarm <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Disarm who? Usage: disarm <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.disarm(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_trip(self, character, args):
        """
        Attempt to trip an opponent.
        Usage: trip <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Trip who? Usage: trip <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.trip(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_bullrush(self, character, args):
        """
        Attempt to bull rush an opponent, pushing them back.
        Usage: bullrush <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Bull rush who? Usage: bullrush <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.bull_rush(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_grapple(self, character, args):
        """
        Attempt to grapple an opponent.
        Usage: grapple <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Grapple who? Usage: grapple <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.grapple(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_overrun(self, character, args):
        """
        Attempt to overrun an opponent, moving through their space.
        Usage: overrun <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Overrun who? Usage: overrun <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.overrun(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_sunder(self, character, args):
        """
        Attempt to destroy an opponent's weapon.
        Usage: sunder <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Sunder whose weapon? Usage: sunder <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.sunder(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_feint(self, character, args):
        """
        Feint in combat to deny opponent their Dex bonus to AC.
        Usage: feint <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not args:
            return "Feint who? Usage: feint <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.feint(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_whirlwind(self, character, args):
        """
        Attack all adjacent enemies at once. Requires Whirlwind Attack feat.
        Usage: whirlwind
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not character.has_feat("Whirlwind Attack"):
            return "You don't have the Whirlwind Attack feat!"

        # Get all alive mobs in room
        targets = [m for m in character.room.mobs if m.alive and m.hp > 0]
        if not targets:
            return "There are no enemies to attack!"

        # Ensure combat with first target
        self._ensure_combat(character, targets[0])
        from src.chat import broadcast_to_room
        result = character.whirlwind_attack(targets)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_springattack(self, character, args):
        """
        Move, attack, and continue moving. Requires Spring Attack feat.
        Usage: springattack <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not character.has_feat("Spring Attack"):
            return "You don't have the Spring Attack feat!"

        if not args:
            return "Spring attack who? Usage: springattack <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.spring_attack(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_stunningfist(self, character, args):
        """
        Attempt to stun an opponent with an unarmed strike. Requires Stunning Fist feat.
        Usage: stunningfist <target>
        """
        error = self._check_can_act(character)
        if error:
            return error

        if not character.has_feat("Stunning Fist"):
            return "You don't have the Stunning Fist feat!"

        if not args:
            return "Stunning fist who? Usage: stunningfist <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        self._ensure_combat(character, target)
        from src.chat import broadcast_to_room
        result = character.stunning_fist(target)
        broadcast_to_room(character.room, result, exclude=character)
        return result

    def cmd_grapple_damage(self, character, args):
        """
        Deal damage to a grappled opponent.
        Usage: gdamage <target>
        """
        if not character.has_condition('grappled'):
            return "You are not grappling anyone!"

        if not args:
            return "Damage who? Usage: gdamage <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        if not target.has_condition('grappled'):
            return f"{target.name} is not grappled!"

        return character.grapple_damage(target)

    def cmd_grapple_pin(self, character, args):
        """
        Attempt to pin a grappled opponent.
        Usage: gpin <target>
        """
        if not character.has_condition('grappled'):
            return "You are not grappling anyone!"

        if not args:
            return "Pin who? Usage: gpin <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        if not target.has_condition('grappled'):
            return f"{target.name} is not grappled!"

        return character.grapple_pin(target)

    def cmd_grapple_escape(self, character, args):
        """
        Attempt to escape from a grapple.
        Usage: gescape
        """
        if not character.has_condition('grappled'):
            return "You are not grappled!"

        # Find who is grappling us (check mobs and players)
        grappler = None

        # Check mobs first
        for mob in character.room.mobs:
            if mob.alive and mob.has_condition('grappled'):
                grappler = mob
                break

        # Check players if no mob grappler found (PvP)
        if not grappler:
            for player in getattr(character.room, 'players', []):
                if player != character and player.has_condition('grappled'):
                    if getattr(player, 'hp', 0) > 0:
                        grappler = player
                        break

        if not grappler:
            # Remove condition if no grappler found
            character.remove_condition('grappled')
            return "You are no longer grappled."

        return character.grapple_escape(grappler)

    # =========================================================================
    # Skill Check Commands
    # =========================================================================

    def cmd_check(self, character, args):
        """
        Perform a skill check.
        Usage: check <skill> [dc]
        Examples:
          check climb
          check climb 15
          check "knowledge arcana"
          check hide
        """
        from src import skills

        if not args:
            return "Check what? Usage: check <skill> [dc]\nType 'skills' to see available skills."

        parts = args.split()

        # Handle quoted skill names like "knowledge arcana"
        if args.startswith('"') or args.startswith("'"):
            # Find quoted skill name
            quote_char = args[0]
            end_quote = args.find(quote_char, 1)
            if end_quote > 0:
                skill_name = args[1:end_quote]
                rest = args[end_quote + 1:].strip().split()
            else:
                skill_name = args[1:]
                rest = []
        else:
            # Try to match a skill name (some have multiple words)
            skill_name = None
            for sname in skills.SKILLS.keys():
                if args.lower().startswith(sname.lower()):
                    skill_name = sname
                    rest = args[len(sname):].strip().split()
                    break

            if not skill_name:
                # Take first word as skill name
                skill_name = parts[0]
                rest = parts[1:]

        # Try to find skill
        skill = skills.SKILLS.get(skill_name)
        if not skill:
            # Try case-insensitive partial match
            for sname, s in skills.SKILLS.items():
                if skill_name.lower() in sname.lower():
                    skill_name = sname
                    skill = s
                    break

        if not skill:
            return f"Unknown skill: {skill_name}\nType 'skills' to see available skills."

        # Parse DC if provided
        dc = None
        if rest:
            try:
                dc = int(rest[0])
            except ValueError:
                pass

        # Perform the check
        success, total, desc = skills.skill_check(character, skill_name, dc=dc)

        return desc

    def cmd_take10(self, character, args):
        """
        Perform a skill check using Take 10 (no rolling).
        Usage: take10 <skill>
        Requires: No stress or distractions (not in combat)
        """
        from src import skills
        from src.combat import get_combat

        # Check for combat
        combat = get_combat(character.room)
        if combat and combat.is_active:
            return "You cannot take 10 while in combat!"

        if not args:
            return "Take 10 on what skill? Usage: take10 <skill>"

        skill_name = args.strip()

        # Try to find skill
        skill = skills.SKILLS.get(skill_name)
        if not skill:
            for sname in skills.SKILLS.keys():
                if skill_name.lower() in sname.lower():
                    skill_name = sname
                    skill = skills.SKILLS.get(sname)
                    break

        if not skill:
            return f"Unknown skill: {skill_name}"

        success, total, desc = skills.skill_check(character, skill_name, take_10=True)
        return desc

    def cmd_take20(self, character, args):
        """
        Perform a skill check using Take 20 (maximum effort, requires time).
        Usage: take20 <skill>
        Requires: No danger from failure, 20x normal time
        """
        from src import skills
        from src.combat import get_combat

        # Check for combat
        combat = get_combat(character.room)
        if combat and combat.is_active:
            return "You cannot take 20 while in combat!"

        if not args:
            return "Take 20 on what skill? Usage: take20 <skill>"

        skill_name = args.strip()

        # Try to find skill
        skill = skills.SKILLS.get(skill_name)
        if not skill:
            for sname in skills.SKILLS.keys():
                if skill_name.lower() in sname.lower():
                    skill_name = sname
                    skill = skills.SKILLS.get(sname)
                    break

        if not skill:
            return f"Unknown skill: {skill_name}"

        # Can't take 20 on skills with consequences for failure
        no_take_20 = ["Disable Device", "Open Lock", "Use Magic Device", "Tumble"]
        if skill_name in no_take_20:
            return f"You cannot take 20 on {skill_name} (failure has consequences)."

        success, total, desc = skills.skill_check(character, skill_name, take_20=True)
        return f"After careful effort (20x normal time):\n{desc}"

    def cmd_skilllist(self, character, args):
        """
        List all available skills.
        Usage: skills [ability]
        Examples:
          skills        - List all skills
          skills str    - List Strength-based skills
          skills trained - List trained-only skills
        """
        from src import skills

        ability_filter = args.lower() if args else None

        lines = ["=== Skills ==="]

        # Group by ability
        by_ability = {}
        for skill_name, skill in sorted(skills.SKILLS.items()):
            ability = skill.key_ability
            if ability not in by_ability:
                by_ability[ability] = []
            by_ability[ability].append(skill)

        ability_order = ["Str", "Dex", "Con", "Int", "Wis", "Cha"]

        for ability in ability_order:
            if ability_filter and ability_filter not in ability.lower() and ability_filter != "trained":
                continue

            skill_list = by_ability.get(ability, [])
            if not skill_list:
                continue

            lines.append(f"\n{ability}-based:")
            for skill in sorted(skill_list, key=lambda s: s.name):
                if ability_filter == "trained" and not skill.trained_only:
                    continue

                # Get character's ranks
                ranks = skills.get_skill_ranks(character, skill.name)
                total_mod, _ = skills.calculate_skill_modifier(character, skill.name)

                # Build skill info
                markers = []
                if skill.trained_only:
                    markers.append("T")
                if skill.armor_check_penalty:
                    markers.append("*")
                marker_str = f" [{','.join(markers)}]" if markers else ""

                # Class skill indicator
                is_class = skills.is_class_skill(character, skill.name)
                class_marker = "C" if is_class else "X"

                lines.append(f"  {skill.name:35} {class_marker} Ranks: {ranks:2} Mod: {total_mod:+3}{marker_str}")

        lines.append("\nLegend: T=Trained Only, *=Armor Check Penalty, C=Class Skill, X=Cross-Class")
        lines.append("Usage: check <skill> [dc] | take10 <skill> | take20 <skill>")

        return "\n".join(lines)

    def cmd_search(self, character, args):
        """
        Search the area for hidden objects, doors, and traps.
        Usage: search
        """
        import random
        room = character.room

        # Check for a trap in this room
        if "trapped" in getattr(room, 'flags', []):
            trap_data = getattr(room, '_trap_data', None)
            search_dc = trap_data.get('search_dc', 20) if trap_data else 20
            roll = random.randint(1, 20)
            # Search uses Intelligence modifier
            int_mod = (getattr(character, 'int_score', 10) - 10) // 2
            ranks = 0
            if hasattr(character, 'skill_ranks') and isinstance(character.skill_ranks, dict):
                ranks = character.skill_ranks.get('Search', 0)
            total = roll + int_mod + ranks
            if total >= search_dc:
                trap_name = trap_data.get('name', 'trap') if trap_data else 'trap'
                if not hasattr(room, '_detected_traps'):
                    room._detected_traps = set()
                room._detected_traps.add(character.name)
                return f"You notice a {trap_name}! (Search {total} vs DC {search_dc})"
            else:
                return "You don't find anything unusual."

        # Check for hidden things in the room
        found_items = []

        # Check for hidden exits
        for direction, exit_data in getattr(room, 'exits', {}).items():
            if isinstance(exit_data, dict) and exit_data.get('hidden'):
                found_items.append(f"a hidden exit to the {direction}")

        # Check for hidden items
        for item in getattr(room, 'items', []):
            if getattr(item, 'hidden', False):
                found_items.append(f"a hidden {item.name}")
                item.hidden = False  # Reveal it

        if found_items:
            return f"You search carefully and find: {', '.join(found_items)}!"
        return "You don't find anything unusual."

    def cmd_disarmtrap(self, character, args):
        """
        Attempt to disarm a detected trap in the current room.
        Usage: disarmtrap
        """
        import random
        room = character.room

        if "trapped" not in getattr(room, 'flags', []):
            return "There is no trap here."

        detected = getattr(room, '_detected_traps', set())
        if character.name not in detected:
            return "You haven't detected a trap here. Use 'search' first."

        trap_data = getattr(room, '_trap_data', None)
        disable_dc = trap_data.get('disable_dc', 20) if trap_data else 20

        # Disable Device check (Intelligence-based)
        roll = random.randint(1, 20)
        int_mod = (getattr(character, 'int_score', 10) - 10) // 2
        ranks = 0
        if hasattr(character, 'skill_ranks') and isinstance(character.skill_ranks, dict):
            ranks = character.skill_ranks.get('Disable Device', 0)
        total = roll + int_mod + ranks

        if total >= disable_dc:
            # Success: disarm the trap
            room.flags.remove("trapped")
            room._detected_traps.discard(character.name)
            trap_name = trap_data.get('name', 'trap') if trap_data else 'trap'
            return f"You carefully disarm the {trap_name}. (Disable Device {total} vs DC {disable_dc})"
        elif total <= disable_dc - 5:
            # Failed by 5+: trigger the trap!
            trigger_msg = self._trigger_trap(character, room)
            return (
                f"You fumble the disarm attempt and trigger the trap!"
                f" (Disable Device {total} vs DC {disable_dc})\n{trigger_msg}"
            )
        else:
            return f"You fail to disarm the trap. (Disable Device {total} vs DC {disable_dc})"

    def _trigger_trap(self, character, room):
        """
        Trigger a trap in the given room, applying damage and conditions.
        Returns a description string of what happened.
        """
        import random
        import os
        import json
        from src.combat import roll_saving_throw, SaveType

        # Load trap data stored on the room, or pick a random trap
        trap_data = getattr(room, '_trap_data', None)
        if trap_data is None:
            traps_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 'data', 'traps.json'
            )
            try:
                with open(traps_path, 'r') as f:
                    all_traps = json.load(f)
                trap_data = random.choice(all_traps)
            except (FileNotFoundError, ValueError):
                character.take_damage(random.randint(1, 6))
                return f"{character.name} triggers a hidden trap and takes damage!"

        trap_name = trap_data.get('name', 'trap')
        damage_str = trap_data.get('damage', '1d6')
        damage_type = trap_data.get('damage_type', 'physical')
        save_type_str = trap_data.get('save_type')
        save_dc = trap_data.get('save_dc')
        has_poison = 'poison' in trap_data

        messages = [f"*** {trap_name} TRIGGERED! ***"]

        # Handle special/non-numeric damage types
        if damage_str in ('drowning', 'poison', 'none', 'special') or damage_str is None:
            if has_poison:
                poison_info = trap_data.get('poison', {})
                if hasattr(character, 'add_condition'):
                    character.add_condition('poisoned')
                messages.append(
                    f"{character.name} is exposed to {poison_info.get('name', 'poison')}!"
                )
            elif damage_str == 'drowning':
                messages.append("Water begins flooding the room. Escape quickly!")
        else:
            # Parse damage dice string, e.g. "2d6", "1d4+1", "4d6", "1"
            damage_dealt = 0
            try:
                ds = str(damage_str).strip()
                if 'd' in ds:
                    parts = ds.split('d', 1)
                    num_dice = int(parts[0]) if parts[0] else 1
                    rest = parts[1]
                    if '+' in rest:
                        die_size, bonus = rest.split('+', 1)
                        damage_dealt = (
                            sum(random.randint(1, int(die_size)) for _ in range(num_dice))
                            + int(bonus)
                        )
                    elif '-' in rest:
                        die_size, penalty = rest.split('-', 1)
                        damage_dealt = max(
                            0,
                            sum(random.randint(1, int(die_size)) for _ in range(num_dice))
                            - int(penalty)
                        )
                    else:
                        damage_dealt = sum(
                            random.randint(1, int(rest)) for _ in range(num_dice)
                        )
                else:
                    damage_dealt = int(ds)
            except (ValueError, IndexError):
                damage_dealt = random.randint(1, 6)

            # Saving throw for half damage (Reflex) if applicable
            saved = False
            if save_type_str and save_dc:
                save_type_map = {
                    'reflex': SaveType.REFLEX,
                    'fortitude': SaveType.FORTITUDE,
                    'will': SaveType.WILL,
                }
                save_enum = save_type_map.get(str(save_type_str).lower())
                if save_enum:
                    success, save_total, save_desc = roll_saving_throw(
                        character, save_enum, save_dc
                    )
                    messages.append(save_desc)
                    if success:
                        damage_dealt = damage_dealt // 2
                        saved = True

            # Apply damage
            if damage_dealt > 0:
                dmg_msg = character.take_damage(damage_dealt)
                messages.append(dmg_msg)
                half_note = " (half damage from successful save)" if saved else ""
                messages.append(f"({damage_dealt} {damage_type} damage{half_note})")

            # Apply poison if trap has one
            if has_poison:
                poison_info = trap_data.get('poison', {})
                poison_save_dc = poison_info.get('save_dc', 13)
                fort_success, _, fort_desc = roll_saving_throw(
                    character, SaveType.FORTITUDE, poison_save_dc
                )
                messages.append(fort_desc)
                if not fort_success:
                    if hasattr(character, 'add_condition'):
                        character.add_condition('poisoned')
                    messages.append(
                        f"{character.name} is poisoned by {poison_info.get('name', 'poison')}!"
                    )

        # One-shot trap: remove "trapped" flag after triggering for manual/repair reset
        reset_type = trap_data.get('reset', 'manual')
        if reset_type in ('manual', 'repair'):
            if "trapped" in getattr(room, 'flags', []):
                room.flags.remove("trapped")
            if hasattr(room, '_detected_traps'):
                room._detected_traps.clear()

        return "\n".join(messages)

    def cmd_listen(self, character, args):
        """
        Listen for sounds in the area.
        Usage: listen [dc]
        """
        from src import skills

        dc = 15  # Default
        if args:
            try:
                dc = int(args)
            except ValueError:
                pass

        success, total, desc = skills.skill_check(character, "Listen", dc=dc)

        if success:
            # Check for things to hear
            room = character.room
            sounds = []

            # Adjacent room occupants
            for direction, exit_data in getattr(room, 'exits', {}).items():
                adj_vnum = exit_data if isinstance(exit_data, int) else exit_data.get('room')
                if adj_vnum:
                    # Would need world reference to check adjacent room
                    pass

            # Mobs in current room (hidden ones)
            for mob in room.mobs:
                if mob.alive and mob.has_condition('hidden'):
                    sounds.append(f"something moving nearby")
                    break

            if sounds:
                desc += f"\nYou hear: {', '.join(sounds)}"
            else:
                desc += "\nYou hear nothing unusual."

        return desc

    def cmd_spot(self, character, args):
        """
        Spot hidden creatures or objects.
        Usage: spot
        """
        from src import skills

        results = [f"{character.name} looks around carefully..."]

        # Check for hidden mobs
        hidden_found = []
        for mob in character.room.mobs:
            if mob.alive and mob.has_condition('hidden'):
                # Opposed check
                actor_wins, spotter_total, hider_total, desc = skills.opposed_skill_check(
                    character, "Spot",
                    mob, "Hide"
                )
                if actor_wins:
                    mob.remove_condition('hidden')
                    hidden_found.append(mob.name)
                    results.append(f"  You spot {mob.name}! (Spot {spotter_total} vs Hide {hider_total})")
                else:
                    results.append(f"  You sense something but can't locate it...")

        if not character.room.mobs or not any(m.has_condition('hidden') for m in character.room.mobs):
            success, total, desc = skills.skill_check(character, "Spot")
            results.append(desc)
            if success:
                results.append("You see nothing out of the ordinary.")

        return "\n".join(results)

    def cmd_climb(self, character, args):
        """
        Attempt to climb a surface.
        Usage: climb [dc]
        Default DCs: rope=0, ladder=5, knotted rope=5, wall with ledges=10, rough=20, smooth=25
        """
        from src import skills

        dc = 15  # Default
        if args:
            try:
                dc = int(args)
            except ValueError:
                # Try to parse surface type
                surfaces = {
                    "rope": 0, "ladder": 5, "knotted": 5,
                    "ledges": 10, "rough": 20, "smooth": 25, "overhang": 25
                }
                for surface, sdc in surfaces.items():
                    if surface in args.lower():
                        dc = sdc
                        break

        success, total, desc = skills.skill_check(character, "Climb", dc=dc)

        if success:
            desc += "\nYou climb successfully!"
        else:
            desc += "\nYou fail to climb and make no progress."
            # Optional: Check for falling (fail by 5+)
            if total < dc - 5:
                desc += " You slip and fall!"

        return desc

    def cmd_jump(self, character, args):
        """
        Attempt to jump a distance.
        Usage: jump <distance in feet>
        Running: DC = distance in feet (horizontal) or 4x feet (vertical)
        Standing: DC is doubled
        """
        from src import skills

        if not args:
            return "Jump how far? Usage: jump <distance> (e.g., 'jump 10' for 10 feet)"

        try:
            distance = int(args)
        except ValueError:
            return "Please specify distance in feet (e.g., 'jump 10')"

        # Assume running jump; DC = distance for horizontal
        dc = distance

        # Check movement
        is_running = getattr(character, 'is_running', False)
        if not is_running:
            dc *= 2  # Standing jump

        # Get current speed (affects max distance)
        base_speed = getattr(character, 'max_move', 30)
        speed_mod = (base_speed - 30) // 10 * 4  # +4 per 10 ft above 30

        success, total, desc = skills.skill_check(character, "Jump", dc=dc, modifier=speed_mod)

        if success:
            desc += f"\nYou successfully jump {distance} feet!"
        else:
            # Calculate actual distance jumped
            actual = max(0, total // (2 if not is_running else 1))
            desc += f"\nYou only manage to jump {actual} feet."

        return desc

    def cmd_tumble(self, character, args):
        """
        Tumble through a threatened area or to reduce falling damage.
        Usage: tumble [target]
        DC 15: Move through threatened area without AoO
        DC 25: Tumble through enemy's space
        """
        from src import skills

        # Check for trained only
        ranks = skills.get_skill_ranks(character, "Tumble")
        if ranks == 0:
            return "You cannot tumble untrained."

        dc = 15  # Default: avoid AoO
        through_enemy = False

        if args:
            target = self._find_target(character, args)
            if target:
                dc = 25
                through_enemy = True

        success, total, desc = skills.skill_check(character, "Tumble", dc=dc)

        if success:
            if through_enemy:
                desc += f"\nYou tumble through your opponent's space!"
            else:
                desc += "\nYou tumble safely through the threatened area!"
        else:
            desc += "\nYou stumble and provoke attacks of opportunity!"

        return desc

    def cmd_intimidate(self, character, args):
        """
        Attempt to demoralize an opponent.
        Usage: intimidate <target>
        On success: Target is shaken for 1+ rounds.
        """
        from src import skills

        if not args:
            return "Intimidate who? Usage: intimidate <target>"

        target = self._find_target(character, args)
        if not target:
            # Try players
            for p in character.room.players:
                if p != character and args.lower() in p.name.lower():
                    target = p
                    break

        if not target:
            return f"You don't see '{args}' here."

        success, total, desc = skills.check_intimidate(character, target)

        if success:
            # Apply shaken condition
            rounds = 1 + max(0, (total - (10 + target.level + skills.get_ability_mod(target, "Wis"))) // 5)
            target.add_timed_condition('shaken', rounds)

        return desc

    def cmd_diplomacy(self, character, args):
        """
        Attempt to improve an NPC's attitude.
        Usage: diplomacy <target>
        """
        from src import skills

        if not args:
            return "Negotiate with who? Usage: diplomacy <target>"

        target = self._find_target(character, args)
        if not target:
            return f"You don't see '{args}' here."

        # Get current attitude (default to indifferent)
        current_attitude = getattr(target, 'attitude', 'indifferent')

        new_attitude, total, desc = skills.check_diplomacy(character, target, current_attitude)

        # Update target's attitude
        if hasattr(target, 'attitude'):
            target.attitude = new_attitude

        return desc

    def cmd_bluff(self, character, args):
        """
        Attempt to deceive someone or feint in combat.
        Usage: bluff <target>
        In combat: Feint to deny Dex bonus to AC
        Out of combat: Opposed by Sense Motive
        """
        from src import skills
        from src.combat import get_combat

        if not args:
            return "Bluff who? Usage: bluff <target>"

        target = self._find_target(character, args)
        if not target:
            for p in character.room.players:
                if p != character and args.lower() in p.name.lower():
                    target = p
                    break

        if not target:
            return f"You don't see '{args}' here."

        # In combat = feint
        combat = get_combat(character.room)
        if combat and combat.is_active:
            success, bluff_total, sm_total, desc = skills.check_bluff_feint(character, target)
            if success:
                # Mark target as flat-footed for next attack
                target.add_timed_condition('flat_footed', 1)
            return desc
        else:
            # Out of combat - opposed Bluff vs Sense Motive
            actor_wins, actor_total, target_total, desc = skills.opposed_skill_check(
                character, "Bluff",
                target, "Sense Motive"
            )
            if actor_wins:
                return f"{desc}\n{target.name} believes your bluff!"
            else:
                return f"{desc}\n{target.name} sees through your deception!"

    def cmd_sensemotive(self, character, args):
        """
        Try to determine if someone is lying or get a hunch about them.
        Usage: sensemotive <target>
        """
        from src import skills

        if not args:
            return "Sense the motives of who? Usage: sensemotive <target>"

        target = self._find_target(character, args)
        if not target:
            for p in character.room.players:
                if p != character and args.lower() in p.name.lower():
                    target = p
                    break

        if not target:
            return f"You don't see '{args}' here."

        # Opposed check vs Bluff (or fixed DC for hunch)
        bluff_ranks = skills.get_skill_ranks(target, "Bluff")

        if bluff_ranks > 0:
            actor_wins, actor_total, target_total, desc = skills.opposed_skill_check(
                character, "Sense Motive",
                target, "Bluff"
            )
            if actor_wins:
                return f"{desc}\nYou sense that {target.name} may be hiding something."
            else:
                return f"{desc}\nYou cannot read {target.name}'s intentions."
        else:
            # Hunch check (DC 20)
            success, total, desc = skills.skill_check(character, "Sense Motive", dc=20)
            if success:
                return f"{desc}\nYou get a hunch about {target.name}'s general attitude."
            else:
                return f"{desc}\nYou cannot get a read on {target.name}."

    def cmd_heal_skill(self, character, args):
        """
        Use the Heal skill for first aid or treating wounds.
        Usage: healskill <target> [type]
        Types: first_aid, treat_wounds, treat_poison, treat_disease
        """
        from src import skills

        if not args:
            return "Heal who? Usage: healskill <target> [type]"

        parts = args.split()
        target_name = parts[0]
        heal_type = parts[1] if len(parts) > 1 else "first_aid"

        # Find target
        target = None
        if target_name.lower() == "self" or target_name.lower() == character.name.lower():
            target = character
        else:
            target = self._find_target(character, target_name)
            if not target:
                for p in character.room.players:
                    if target_name.lower() in p.name.lower():
                        target = p
                        break

        if not target:
            return f"You don't see '{target_name}' here."

        # Determine DC
        dcs = {
            "first_aid": 15,        # Stabilize dying
            "treat_wounds": 15,     # Restore 1 HP (long-term care)
            "treat_poison": 15,     # Help save vs secondary damage
            "treat_disease": 15,    # Help save vs disease
            "aid_another": 10,      # Give +2 to next Heal check
        }

        dc = dcs.get(heal_type, 15)
        success, total, desc = skills.skill_check(character, "Heal", dc=dc)

        if success:
            if heal_type == "first_aid":
                if hasattr(target, 'health_status'):
                    from src.character import HealthStatus
                    if target.health_status in (HealthStatus.DYING,):
                        target.is_stable = True
                        desc += f"\n{target.name} is stabilized!"
                    else:
                        desc += f"\n{target.name} doesn't need first aid."
                else:
                    desc += f"\nYou tend to {target.name}'s wounds."
            elif heal_type == "treat_wounds":
                old_hp = target.hp
                target.hp = min(target.hp + 1, target.max_hp)
                desc += f"\nWith long-term care, {target.name} recovers 1 HP. ({old_hp} -> {target.hp})"
            else:
                desc += f"\nYou provide medical attention to {target.name}."
        else:
            desc += f"\nYour attempt to help fails."

        return desc

    # =========================================================================
    # Quest Commands
    # =========================================================================

    def _get_quest_log(self, character):
        """Get or create a QuestLog for the character."""
        from src.quests import QuestLog
        if not hasattr(character, 'quest_log') or character.quest_log is None:
            character.quest_log = QuestLog()
        return character.quest_log

    def _get_quest_manager(self):
        """Get or create the world's QuestManager."""
        from src.quests import QuestManager
        if not hasattr(self.world, 'quest_manager') or self.world.quest_manager is None:
            self.world.quest_manager = QuestManager()
            self.world.quest_manager.load_quests()
        return self.world.quest_manager

    def cmd_questlog(self, character, args):
        """
        Display your quest log.
        Usage: questlog [active|complete|all]
        """
        from src.quests import QuestState

        quest_log = self._get_quest_log(character)
        quest_manager = self._get_quest_manager()

        filter_type = args.lower() if args else "active"

        lines = ["=== Quest Log ==="]

        # Active quests
        if filter_type in ("active", "all"):
            active = [q for q in quest_log.active_quests.values()
                     if q.state in (QuestState.ACTIVE, QuestState.COMPLETE)]

            if active:
                lines.append("\nActive Quests:")
                for aq in active:
                    quest = quest_manager.get_quest(aq.quest_id)
                    if quest:
                        status = "[READY TO TURN IN]" if aq.state == QuestState.COMPLETE else ""
                        lines.append(f"  [{quest.id}] {quest.name} (Lv.{quest.level}) {status}")

                        # Show objectives
                        for obj in aq.objectives:
                            if not obj.hidden:
                                check = "[X]" if obj.is_complete else "[ ]"
                                opt = "(Optional)" if obj.optional else ""
                                lines.append(f"      {check} {obj.description} {obj.progress_text} {opt}")
            else:
                lines.append("\nNo active quests.")

        # Completed quests
        if filter_type in ("complete", "all"):
            if quest_log.completed_quests:
                lines.append("\nCompleted Quests:")
                for qid in sorted(quest_log.completed_quests):
                    quest = quest_manager.get_quest(qid)
                    if quest:
                        lines.append(f"  [{qid}] {quest.name}")
            elif filter_type == "complete":
                lines.append("\nNo completed quests.")

        lines.append("\nCommands: questlog | quest accept <id> | quest abandon <id> | quest turnin <id>")
        return "\n".join(lines)

    def cmd_quest_action(self, character, args):
        """
        Quest management command.
        Usage:
          quest list          - Show available quests
          quest info <id>     - Show quest details
          quest accept <id>   - Accept a quest
          quest abandon <id>  - Abandon a quest
          quest turnin <id>   - Turn in a completed quest
        """
        from src.quests import QuestState, apply_quest_rewards

        if not args:
            return self.cmd_questlog(character, "")

        parts = args.split()
        action = parts[0].lower()
        quest_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

        quest_log = self._get_quest_log(character)
        quest_manager = self._get_quest_manager()

        if action == "list":
            # Show available quests in this room or from nearby NPCs
            room_vnum = character.room.vnum if character.room else 0
            available = quest_manager.get_available_quests(character, quest_log, room_vnum=room_vnum)

            if not available:
                # Show all available quests
                available = quest_manager.get_available_quests(character, quest_log)

            if available:
                lines = ["=== Available Quests ==="]
                for quest in available:
                    lines.append(f"  [{quest.id}] {quest.name} (Lv.{quest.level}) - {quest.giver_npc}")
                    lines.append(f"      {quest.description[:60]}...")
                lines.append("\nUse 'quest accept <id>' to accept a quest.")
                return "\n".join(lines)
            else:
                return "No quests available at your level."

        elif action == "info":
            if quest_id is None:
                return "Usage: quest info <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            lines = [f"=== {quest.name} ==="]
            lines.append(f"Level: {quest.level} | Category: {quest.category.title()}")
            lines.append(f"Quest Giver: {quest.giver_npc}")
            lines.append(f"\n{quest.description}")

            lines.append("\nObjectives:")
            for obj in quest.objectives:
                if not obj.hidden:
                    opt = "(Optional)" if obj.optional else ""
                    lines.append(f"  - {obj.description} {opt}")

            lines.append("\nRewards:")
            if quest.rewards.xp:
                lines.append(f"  XP: {quest.rewards.xp}")
            if quest.rewards.gold:
                lines.append(f"  Gold: {quest.rewards.gold}")
            for item in quest.rewards.items:
                lines.append(f"  Item: {item}")
            if quest.rewards.title:
                lines.append(f"  Title: {quest.rewards.title}")
            for faction, rep in quest.rewards.reputation.items():
                lines.append(f"  Reputation: +{rep} with {faction}")

            # Check status
            if quest_log.is_quest_active(quest_id):
                lines.append("\nStatus: ACTIVE")
            elif quest_log.is_quest_complete(quest_id):
                lines.append("\nStatus: COMPLETED")
            else:
                meets, reason = quest.prerequisites.check(character, quest_log)
                if meets:
                    lines.append("\nStatus: Available - use 'quest accept' to start")
                else:
                    lines.append(f"\nStatus: Locked - {reason}")

            return "\n".join(lines)

        elif action == "accept":
            if quest_id is None:
                return "Usage: quest accept <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            # Check prerequisites
            meets, reason = quest.prerequisites.check(character, quest_log)
            if not meets:
                return f"Cannot accept quest: {reason}"

            success, msg = quest_log.accept_quest(quest)
            if success and quest.accept_text:
                msg += f"\n\n{quest.giver_npc} says: \"{quest.accept_text}\""
            return msg

        elif action == "abandon":
            if quest_id is None:
                return "Usage: quest abandon <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            if not quest.abandonable:
                return f"Quest '{quest.name}' cannot be abandoned."

            success, msg = quest_log.abandon_quest(quest_id)
            return msg

        elif action == "turnin":
            if quest_id is None:
                return "Usage: quest turnin <id>"

            quest = quest_manager.get_quest(quest_id)
            if not quest:
                return f"Quest #{quest_id} not found."

            active_quest = quest_log.get_active_quest(quest_id)
            if not active_quest:
                return "You don't have this quest active."

            if active_quest.state != QuestState.COMPLETE:
                return "Quest objectives not complete yet."

            # Turn in and apply rewards
            success, msg = quest_log.turn_in_quest(quest_id)
            if success:
                lines = [msg]
                if quest.complete_text:
                    lines.append(f"\n{quest.giver_npc or 'Quest Giver'} says: \"{quest.complete_text}\"")

                # Apply rewards
                reward_msgs = apply_quest_rewards(character, quest, quest_log)
                lines.extend(reward_msgs)

                # Check for chain quest
                if quest.chain_quest:
                    next_quest = quest_manager.get_quest(quest.chain_quest)
                    if next_quest:
                        lines.append(f"\nNew quest available: {next_quest.name}")

                return "\n".join(lines)
            return msg

        else:
            return "Unknown quest action. Use: list, info, accept, abandon, turnin"

    def cmd_talkto(self, character, args):
        """
        Talk to an NPC to get quests or turn in completed ones.
        Usage: talkto <npc name>
        """
        from src.quests import QuestState, on_npc_talked, apply_quest_rewards

        if not args:
            return "Talk to who? Usage: talkto <npc name>"

        npc_name = args.lower()
        quest_log = self._get_quest_log(character)
        quest_manager = self._get_quest_manager()

        # Find NPC in room
        npc = None
        for mob in character.room.mobs:
            if mob.alive and npc_name in mob.name.lower():
                npc = mob
                break

        if not npc:
            return f"You don't see '{args}' here."

        lines = [f"You approach {npc.name}."]

        # Update quest talk objectives
        talk_msgs = on_npc_talked(character, npc.name, quest_log, quest_manager)
        lines.extend(talk_msgs)

        # Check for quests to turn in
        turnin_quests = quest_manager.get_turnin_quests(quest_log, npc_name=npc.name)
        for quest, active_quest in turnin_quests:
            lines.append(f"\n{npc.name} says: \"Ah, you've completed {quest.name}!\"")
            if quest.complete_text:
                lines.append(f"\"{quest.complete_text}\"")

            # Auto turn in
            success, msg = quest_log.turn_in_quest(quest.id)
            if success:
                reward_msgs = apply_quest_rewards(character, quest, quest_log)
                lines.extend(reward_msgs)

        # Check for available quests
        available = quest_manager.get_available_quests(character, quest_log, npc_name=npc.name)
        if available:
            lines.append(f"\n{npc.name} has quests available:")
            for quest in available:
                lines.append(f"  [{quest.id}] {quest.name} (Lv.{quest.level})")
            lines.append("Use 'quest accept <id>' to accept a quest.")

        # Show NPC dialogue if they have one
        if hasattr(npc, 'dialogue') and npc.dialogue:
            lines.append(f"\n{npc.name} says: \"{npc.dialogue}\"")
        elif not available and not turnin_quests:
            lines.append(f"\n{npc.name} has nothing to say right now.")

        return "\n".join(lines)

    def cmd_reputation(self, character, args):
        """
        Display your reputation with various factions.
        Usage: reputation
        """
        reputation = getattr(character, 'reputation', {})
        titles = getattr(character, 'titles', [])

        lines = ["=== Reputation & Titles ==="]

        if titles:
            lines.append("\nTitles:")
            for title in titles:
                lines.append(f"  {title}")

        if reputation:
            lines.append("\nFaction Standing:")

            # Reputation thresholds
            def rep_rank(value):
                if value >= 100:
                    return "Exalted"
                elif value >= 75:
                    return "Revered"
                elif value >= 50:
                    return "Honored"
                elif value >= 25:
                    return "Friendly"
                elif value >= 0:
                    return "Neutral"
                elif value >= -25:
                    return "Unfriendly"
                elif value >= -50:
                    return "Hostile"
                else:
                    return "Hated"

            for faction, value in sorted(reputation.items()):
                rank = rep_rank(value)
                lines.append(f"  {faction}: {value} ({rank})")
        else:
            lines.append("\nNo faction reputation yet.")

        return "\n".join(lines)

    # =========================================================================
    # AI Configuration Commands (Admin)
    # =========================================================================

    def cmd_ai_config(self, character, args):
        """
        Configure AI settings for NPC roleplay.
        Usage: @ai <setting> <value>

        Settings:
            enable/disable  - Enable or disable LLM responses
            backend <name>  - Set backend: ollama, lmstudio
            ollama <host>   - Set Ollama host URL
            lmstudio <host> - Set LM Studio host URL

        Examples:
            @ai enable
            @ai disable
            @ai backend ollama
            @ai backend lmstudio
            @ai ollama http://localhost:11434
            @ai lmstudio http://192.168.1.100:1234
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        from src import ai

        if not args:
            return self.cmd_ai_status(character, "")

        parts = args.split(None, 1)
        setting = parts[0].lower()
        value = parts[1] if len(parts) > 1 else ""

        if setting == "enable":
            ai.enable_llm(True)
            return "AI LLM responses enabled."
        elif setting == "disable":
            ai.enable_llm(False)
            return "AI LLM responses disabled. NPCs will use templates only."
        elif setting == "backend":
            if value.lower() in ("ollama", "lmstudio"):
                ai.set_llm_backend(value)
                return f"AI backend set to: {value}"
            return "Invalid backend. Options: ollama, lmstudio"
        elif setting == "ollama":
            if value:
                ai.set_ollama_host(value)
                return f"Ollama host set to: {value}"
            return "Usage: @ai ollama <host url>"
        elif setting == "lmstudio":
            if value:
                ai.set_lmstudio_host(value)
                return f"LM Studio host set to: {value}"
            return "Usage: @ai lmstudio <host url>"
        else:
            return "Unknown setting. Type '@ai' for help."

    def cmd_ai_model(self, character, args):
        """
        Set the AI model to use.
        Usage: @aimodel <backend> <model_name>

        Examples:
            @aimodel ollama llama3.2
            @aimodel ollama mistral
            @aimodel lmstudio local-model
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        from src import ai

        if not args:
            status = ai.get_llm_status()
            return f"Current models:\n  Ollama: {status['ollama_model']}\n  LM Studio: {status['lmstudio_model']}"

        parts = args.split(None, 1)
        if len(parts) < 2:
            return "Usage: @aimodel <backend> <model_name>"

        backend = parts[0].lower()
        model = parts[1]

        if backend == "ollama":
            ai.set_ollama_model(model)
            return f"Ollama model set to: {model}"
        elif backend == "lmstudio":
            ai.set_lmstudio_model(model)
            return f"LM Studio model set to: {model}"
        else:
            return "Unknown backend. Options: ollama, lmstudio"

    async def cmd_ai_status(self, character, args):
        """
        Show current AI configuration and status.
        Usage: @aistatus
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        from src import ai

        status = ai.get_llm_status()

        lines = [
            "AI System Status:",
            f"  LLM Enabled: {status['enabled']}",
            f"  Primary Backend: {status['backend']}",
            "",
            "Ollama Configuration:",
            f"  Host: {status['ollama_host']}",
            f"  Model: {status['ollama_model']}",
        ]

        # Check Ollama availability
        ollama_available = await ai.check_ollama_available()
        lines.append(f"  Available: {'Yes' if ollama_available else 'No'}")

        lines.extend([
            "",
            "LM Studio Configuration:",
            f"  Host: {status['lmstudio_host']}",
            f"  Model: {status['lmstudio_model']}",
        ])

        # Check LM Studio availability
        lmstudio_available = await ai.check_lmstudio_available()
        lines.append(f"  Available: {'Yes' if lmstudio_available else 'No'}")

        lines.extend([
            "",
            f"Timeout: {status['timeout']} seconds",
            "",
            "Commands:",
            "  talk <npc> <message> - Talk to an NPC",
            "  @ai <setting> <value> - Configure AI",
            "  @aimodel <backend> <model> - Set model",
        ])

        return "\n".join(lines)

    # =========================================================================
    # Respawn Management Commands (Admin)
    # =========================================================================

    def cmd_respawn(self, character, args):
        """
        Force respawn a specific mob by vnum.
        Usage: @respawn <vnum>
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        if not args:
            return "Usage: @respawn <mob_vnum>"

        try:
            vnum = int(args.strip())
        except ValueError:
            return "Invalid vnum. Must be a number."

        spawn_manager = get_spawn_manager()
        success, message = spawn_manager.force_respawn(vnum, self.world)
        return message

    def cmd_respawnall(self, character, args):
        """
        Force respawn all dead mobs immediately.
        Usage: @respawnall
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        spawn_manager = get_spawn_manager()
        count, messages = spawn_manager.force_respawn_all(self.world)

        if count == 0:
            return "No mobs need to respawn."

        output = [f"Respawned {count} mobs:"]
        output.extend(messages[:20])  # Limit output
        if len(messages) > 20:
            output.append(f"  ... and {len(messages) - 20} more")

        return "\n".join(output)

    def cmd_respawnstatus(self, character, args):
        """
        Show respawn system status and pending respawns.
        Usage: @respawnstatus [pending]
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        spawn_manager = get_spawn_manager()

        if args and args.strip().lower() == "pending":
            # Show detailed pending respawns
            pending = spawn_manager.get_pending_respawns()
            if not pending:
                return "No mobs pending respawn."

            lines = ["Pending Respawns:"]
            for name, vnum, remaining in pending[:25]:
                minutes = remaining / 60
                lines.append(f"  {name} (vnum {vnum}): {minutes:.1f} min remaining")
            if len(pending) > 25:
                lines.append(f"  ... and {len(pending) - 25} more")

            return "\n".join(lines)
        else:
            # Show general status
            return spawn_manager.get_status()

    def cmd_setrespawn(self, character, args):
        """
        Set the respawn time for a specific mob.
        Usage: @setrespawn <vnum> <seconds>
        Example: @setrespawn 2001 600  (set Stone Golem to 10 minute respawn)
        Use 0 to disable respawning for a mob.
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        parts = args.split() if args else []
        if len(parts) != 2:
            return "Usage: @setrespawn <mob_vnum> <seconds>\nUse 0 to disable respawn."

        try:
            vnum = int(parts[0])
            seconds = int(parts[1])
        except ValueError:
            return "Invalid arguments. Both vnum and seconds must be numbers."

        spawn_manager = get_spawn_manager()
        success, message = spawn_manager.set_respawn_time(vnum, seconds)
        return message

    # =========================================================================
    # Time and Schedule Commands
    # =========================================================================

    def cmd_time(self, character, args):
        """
        Show the current in-game time and date.
        Usage: time
        """
        game_time = get_game_time()
        lines = [
            game_time.get_full_time_string(),
            "",
            game_time.get_description(),
        ]
        return "\n".join(lines)

    def cmd_settime(self, character, args):
        """
        Set the current game hour (admin only).
        Usage: @settime <hour>
        Example: @settime 12  (set to noon)
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        if not args:
            return "Usage: @settime <hour> (0-23)"

        try:
            hour = int(args.strip())
            if not 0 <= hour <= 23:
                return "Hour must be between 0 and 23."
        except ValueError:
            return "Invalid hour. Must be a number 0-23."

        game_time = get_game_time()
        game_time.set_time(hour)
        return f"Game time set to {game_time.get_full_time_string()}"

    def cmd_schedule(self, character, args):
        """
        View or manage NPC schedules (admin only).
        Usage: @schedule <npc_vnum>       - View an NPC's schedule
               @schedule list             - List all registered schedules
               @schedule enable <vnum>    - Enable an NPC's schedule
               @schedule disable <vnum>   - Disable an NPC's schedule
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        schedule_manager = get_schedule_manager()
        game_time = get_game_time()

        if not args:
            return ("Usage:\n"
                    "  @schedule <npc_vnum>     - View NPC's schedule\n"
                    "  @schedule list           - List all schedules\n"
                    "  @schedule enable <vnum>  - Enable schedule\n"
                    "  @schedule disable <vnum> - Disable schedule")

        parts = args.split()
        cmd = parts[0].lower()

        if cmd == "list":
            if not schedule_manager.schedules:
                return "No NPC schedules registered."

            lines = ["Registered NPC Schedules:", ""]
            for vnum, schedule in schedule_manager.schedules.items():
                npc = self.world.mobs.get(vnum)
                npc_name = npc.name if npc else f"Unknown (vnum {vnum})"
                status = "enabled" if schedule.enabled else "disabled"
                activity = schedule_manager.get_npc_activity(vnum)
                lines.append(f"  {npc_name} (vnum {vnum}): {status}, currently {activity.value}")

            return "\n".join(lines)

        elif cmd == "enable" and len(parts) > 1:
            try:
                vnum = int(parts[1])
            except ValueError:
                return "Invalid vnum."

            if vnum not in schedule_manager.schedules:
                return f"No schedule found for vnum {vnum}."

            schedule_manager.schedules[vnum].enabled = True
            return f"Schedule for vnum {vnum} enabled."

        elif cmd == "disable" and len(parts) > 1:
            try:
                vnum = int(parts[1])
            except ValueError:
                return "Invalid vnum."

            if vnum not in schedule_manager.schedules:
                return f"No schedule found for vnum {vnum}."

            schedule_manager.schedules[vnum].enabled = False
            return f"Schedule for vnum {vnum} disabled."

        else:
            # Assume it's a vnum to view
            try:
                vnum = int(cmd)
            except ValueError:
                return "Invalid command or vnum."

            return schedule_manager.get_schedule_status(vnum, game_time)

    def cmd_movenpc(self, character, args):
        """
        Force move an NPC to a specific room (admin only).
        Usage: @movenpc <npc_vnum> <room_vnum>
        """
        if not getattr(character, 'is_immortal', False):
            return "Permission denied: You are not an admin."

        parts = args.split() if args else []
        if len(parts) != 2:
            return "Usage: @movenpc <npc_vnum> <room_vnum>"

        try:
            npc_vnum = int(parts[0])
            room_vnum = int(parts[1])
        except ValueError:
            return "Invalid arguments. Both must be numbers."

        schedule_manager = get_schedule_manager()
        success, message = schedule_manager.force_move_npc(npc_vnum, room_vnum, self.world)
        return message

    # =========================================================================
    # Death Check Helper
    # =========================================================================

    def _check_incapacitated(self, character):
        """Return an error message if the character is incapacitated, else None."""
        if getattr(character, 'hp', 1) <= 0:
            from src.character import HealthStatus
            status = getattr(character, 'health_status', None)
            if status and status != HealthStatus.HEALTHY:
                return "You are incapacitated! Type 'respawn' to return to the chapel."
        return None

    # =========================================================================
    # Player Respawn Command
    # =========================================================================

    def cmd_player_respawn(self, character, args):
        """Respawn at the chapel after death.
        Usage: respawn
        Only usable when your HP is 0 or below (disabled/dying/dead).
        Restores 50% HP but applies a 25% XP penalty for current level.
        """
        if character.hp > 0:
            return "You are not dead! No need to respawn."

        chapel_vnum = 1000
        if chapel_vnum not in self.world.rooms:
            return "Respawn failed: Chapel room not found."

        # Apply 25% XP penalty for current level
        xp_table = {1: 0, 2: 1000, 3: 3000, 4: 6000, 5: 10000, 6: 15000,
                     7: 21000, 8: 28000, 9: 36000, 10: 45000}
        current_level_xp = xp_table.get(character.level, (character.level - 1) * 5000)
        next_level_xp = xp_table.get(character.level + 1, character.level * 5000)
        level_xp_range = next_level_xp - current_level_xp
        xp_penalty = level_xp_range // 4
        character.xp = max(current_level_xp, character.xp - xp_penalty)

        # Remove from current room
        if character in character.room.players:
            character.room.players.remove(character)

        # Broadcast departure
        from src.chat import broadcast_to_room
        broadcast_to_room(character.room, f"{character.name}'s body fades away in a shimmer of light.", exclude=character)

        # Move to chapel
        character.room = self.world.rooms[chapel_vnum]
        character.room.players.append(character)

        # Restore HP to 50% of max
        character.hp = max(1, character.max_hp // 2)
        character.is_stable = False

        # Clear combat state
        character.state = State.EXPLORING
        if hasattr(character, 'clear_combat_target'):
            character.clear_combat_target()
        if hasattr(character, 'clear_queue'):
            character.clear_queue()

        # Clear conditions
        character.conditions.clear()
        character.active_conditions.clear()

        # Broadcast arrival
        broadcast_to_room(character.room, f"{character.name} materializes at the chapel in a flash of light.", exclude=character)

        return (f"You awaken at the Chapel of the Aetherial Altar.\n"
                f"HP restored to {character.hp}/{character.max_hp}.\n"
                f"XP penalty: -{xp_penalty} XP.")

    # =========================================================================
    # Loot Command
    # =========================================================================

    def cmd_loot(self, character, args):
        """Loot gold and items from a corpse.
        Usage: loot [corpse name]
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        corpses = getattr(character.room, 'corpses', [])
        if not corpses:
            return "There are no corpses here to loot."

        # Find matching corpse (first one, or by name)
        corpse = None
        if args:
            for c in corpses:
                if args.lower() in c.mob_name.lower():
                    corpse = c
                    break
            if not corpse:
                return f"No corpse matching '{args}' here."
        else:
            corpse = corpses[0]

        results = []

        # Loot gold
        if corpse.gold > 0:
            character.gold = getattr(character, 'gold', 0) + corpse.gold
            results.append(f"You loot {corpse.gold} gp from the corpse of {corpse.mob_name}.")
            corpse.gold = 0

        # Loot items
        for item in corpse.items[:]:
            character.inventory.append(item)
            results.append(f"You loot {item.name} from the corpse of {corpse.mob_name}.")
        corpse.items.clear()

        # Remove empty corpse (auto-sac or default cleanup)
        if corpse.is_empty:
            if getattr(character, 'auto_sac', False):
                corpses.remove(corpse)
                results.append("The corpse crumbles to dust.")
            else:
                corpses.remove(corpse)
                results.append(f"The corpse of {corpse.mob_name} crumbles to dust.")

        if not results:
            return f"The corpse of {corpse.mob_name} has nothing left to loot."

        return "\n".join(results)

    # =========================================================================
    # Give Command (triggers DELIVER quest objectives)
    # =========================================================================

    def cmd_give(self, character, args):
        """Give an item or gold to an NPC or player.
        Usage: give <item> <target>
               give <amount> gold <target>
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        if not args:
            return "Give what to whom? Usage: give <item> <target> or give <amount> gold <target>"

        # Check for gold transfer: give <amount> gold <target>
        gold_parts = args.split()
        if len(gold_parts) >= 3 and gold_parts[1].lower() == "gold":
            try:
                amount = int(gold_parts[0])
            except ValueError:
                return "Invalid amount. Usage: give <amount> gold <target>"
            if amount <= 0:
                return "Amount must be positive."
            target_name = " ".join(gold_parts[2:])
            if getattr(character, 'gold', 0) < amount:
                return f"You don't have {amount} gp."
            # Find target
            target = None
            for player in getattr(character.room, 'players', []):
                if player != character and player.name.lower() == target_name.lower():
                    target = player
                    break
            if not target:
                for mob in getattr(character.room, 'mobs', []):
                    if hasattr(mob, 'name') and mob.name.lower() == target_name.lower():
                        if getattr(mob, 'alive', True):
                            target = mob
                            break
            if not target:
                return f"You don't see '{target_name}' here."
            character.gold -= amount
            if hasattr(target, 'gold'):
                target.gold = getattr(target, 'gold', 0) + amount
            from src.chat import broadcast_to_room
            broadcast_to_room(character.room, f"{character.name} gives {amount} gp to {target.name}.", exclude=character)
            return f"You give {amount} gp to {target.name}."

        parts = args.rsplit(None, 1)
        if len(parts) < 2:
            return "Usage: give <item> <target>"

        item_name, target_name = parts

        # Find item in inventory
        item = next((i for i in character.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            return f"You don't have '{item_name}'."

        # Find target - check mobs first, then players
        target = None
        for mob in getattr(character.room, 'mobs', []):
            if hasattr(mob, 'name') and mob.name.lower() == target_name.lower():
                if getattr(mob, 'alive', True):
                    target = mob
                    break

        if not target:
            for player in getattr(character.room, 'players', []):
                if player != character and player.name.lower() == target_name.lower():
                    target = player
                    break

        if not target:
            return f"You don't see '{target_name}' here."

        # Transfer item
        character.inventory.remove(item)
        if hasattr(target, 'inventory'):
            target.inventory.append(item)

        result = f"You give {item.name} to {target.name}."

        # Quest trigger for DELIVER objectives
        if getattr(character, 'quest_log', None):
            item_type = getattr(item, 'item_type', item.name.lower())
            npc_name = getattr(target, 'name', '')
            try:
                quest_updates = character.quest_log.check_objective_by_target(
                    quests.ObjectiveType.DELIVER, npc_name
                )
                for update in quest_updates:
                    result += f"\n[Quest] {update}"
            except Exception:
                pass

        return result

    # =========================================================================
    # Power Attack Toggle
    # =========================================================================

    def cmd_powerattack(self, character, args):
        """Toggle Power Attack: trade attack bonus for damage.
        Usage: powerattack <0-BAB>  or  powerattack off
        Requires the Power Attack feat.
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        feats = getattr(character, 'feats', [])
        if "Power Attack" not in feats:
            return "You don't have the Power Attack feat."

        if not args or args.strip().lower() == 'off':
            character.power_attack_amt = 0
            return "Power Attack disabled."

        try:
            amount = int(args.strip())
        except ValueError:
            return "Usage: powerattack <number> or powerattack off"

        bab = getattr(character, 'bab', (character.level * 3) // 4)
        if amount < 0 or amount > bab:
            return f"Power Attack amount must be between 0 and your BAB ({bab})."

        character.power_attack_amt = amount
        if amount == 0:
            return "Power Attack disabled."
        return f"Power Attack set to {amount}. (-{amount} attack, +{amount} damage)"

    # =========================================================================
    # Combat Expertise Toggle
    # =========================================================================

    def cmd_combatexpertise(self, character, args):
        """Toggle Combat Expertise: trade attack bonus for AC.
        Usage: combatexpertise <0-5>  or  combatexpertise off
        Requires the Combat Expertise feat.
        """
        death_check = self._check_incapacitated(character)
        if death_check:
            return death_check

        feats = getattr(character, 'feats', [])
        if "Combat Expertise" not in feats:
            return "You don't have the Combat Expertise feat."

        if not args or args.strip().lower() == 'off':
            character.combat_expertise_amt = 0
            return "Combat Expertise disabled."

        try:
            amount = int(args.strip())
        except ValueError:
            return "Usage: combatexpertise <number> or combatexpertise off"

        bab = getattr(character, 'bab', (character.level * 3) // 4)
        max_amount = min(5, bab)
        if amount < 0 or amount > max_amount:
            return f"Combat Expertise amount must be between 0 and {max_amount}."

        character.combat_expertise_amt = amount
        if amount == 0:
            return "Combat Expertise disabled."
        return f"Combat Expertise set to {amount}. (-{amount} attack, +{amount} dodge AC)"

    # --- Bank / Storage Commands ---

    def _find_banker(self, character):
        """Return the first banker mob in the room, or None."""
        for mob in getattr(character.room, 'mobs', []):
            if hasattr(mob, 'flags') and 'banker' in mob.flags:
                return mob
        return None

    def cmd_deposit(self, character, args):
        """Deposit gold into the bank. Usage: deposit <amount>"""
        banker = self._find_banker(character)
        if not banker:
            return "There is no banker here."
        if not args:
            return "Deposit how much gold? Usage: deposit <amount>"
        try:
            amount = int(args.strip())
        except ValueError:
            return "Please specify a valid number. Usage: deposit <amount>"
        if amount <= 0:
            return "You must deposit a positive amount of gold."
        if character.gold < amount:
            return f"You only have {character.gold} gold pieces."
        character.gold -= amount
        character.bank_gold += amount
        return (f"{banker.name} takes your coins and records the transaction.\n"
                f"You deposit {amount} gold. Balance: {character.bank_gold} gp. "
                f"On hand: {character.gold} gp.")

    def cmd_withdraw(self, character, args):
        """Withdraw gold from the bank. Usage: withdraw <amount>"""
        banker = self._find_banker(character)
        if not banker:
            return "There is no banker here."
        if not args:
            return "Withdraw how much gold? Usage: withdraw <amount>"
        try:
            amount = int(args.strip())
        except ValueError:
            return "Please specify a valid number. Usage: withdraw <amount>"
        if amount <= 0:
            return "You must withdraw a positive amount of gold."
        if character.bank_gold < amount:
            return f"You only have {character.bank_gold} gold pieces in your account."
        character.bank_gold -= amount
        character.gold += amount
        return (f"{banker.name} counts out the coins and hands them to you.\n"
                f"You withdraw {amount} gold. Balance: {character.bank_gold} gp. "
                f"On hand: {character.gold} gp.")

    # --- Newbie Channel ---

    def cmd_newbie(self, character, args):
        """Broadcast a message on the newbie channel. Usage: newbie <message>"""
        if not args:
            return "Newbie what?"
        from src.chat import format_newbie, broadcast_to_world
        formatted = format_newbie(character, args)
        broadcast_to_world(self.world, formatted, exclude=character)
        bold_green = '\033[1;32m'
        reset = '\033[0m'
        return f"{bold_green}[Newbie] You: {args}{reset}"

    # --- Rescue Command ---

    def cmd_rescue(self, character, args):
        """Redirect mobs targeting an ally to target you instead. Usage: rescue <player>"""
        from src.character import State
        if character.state != State.COMBAT:
            return "You must be in combat to rescue someone."
        if not args:
            return "Rescue whom? Usage: rescue <player name>"
        target_name = args.strip().lower()
        ally = next(
            (p for p in getattr(character.room, 'players', [])
             if p.name.lower() == target_name and p != character),
            None
        )
        if not ally:
            return f"You don't see '{args}' here to rescue."
        from src.combat import get_combat
        combat = get_combat(character.room)
        if not combat:
            return "There is no active combat here."
        redirected = 0
        for state in combat.initiative_order:
            combatant = state.combatant
            # Only redirect mobs (mobs lack an 'xp' attribute on the character class)
            if hasattr(combatant, 'xp'):
                continue
            if getattr(combatant, 'combat_target', None) == ally:
                combatant.combat_target = character
                redirected += 1
        if redirected == 0:
            return f"No enemies were targeting {ally.name}."
        return (f"You leap to {ally.name}'s defense, drawing the attention of "
                f"{redirected} {'enemy' if redirected == 1 else 'enemies'}!")

    # =========================================================================
    # Consider Command (System 3)
    # =========================================================================

    def cmd_consider(self, character, args):
        """Consider a mob to gauge how dangerous it is compared to you.
        Usage: consider <mob name>
        """
        if not args:
            return "Consider whom? Usage: consider <mob name>"

        target_name = args.strip().lower()
        target = None
        for mob in getattr(character.room, 'mobs', []):
            if getattr(mob, 'alive', True) and target_name in mob.name.lower():
                target = mob
                break

        if not target:
            return f"You don't see '{args.strip()}' here."

        diff = character.level - getattr(target, 'cr', getattr(target, 'level', 1))

        if diff <= -4:
            assessment = "\033[1;31msuicidal! You would surely die.\033[0m"
        elif diff <= -1:
            assessment = "\033[0;31mdangerous — it has the upper hand.\033[0m"
        elif diff == 0:
            assessment = "\033[0;33man even match.\033[0m"
        elif diff <= 3:
            assessment = "\033[0;32measy — you have the advantage.\033[0m"
        else:
            assessment = "\033[1;32mtrivial. Hardly worth the effort.\033[0m"

        return f"You consider {target.name}. It looks like {assessment}"

    # =========================================================================
    # Wimpy Command (System 4)
    # =========================================================================

    def cmd_wimpy(self, character, args):
        """Set auto-flee HP threshold percentage (0-50). 0 disables wimpy.
        Usage: wimpy [0-50]
        """
        if not args:
            wimpy = getattr(character, 'wimpy', 0)
            if wimpy == 0:
                return "Wimpy is currently disabled. Use 'wimpy <1-50>' to enable auto-flee."
            return f"You will automatically flee when your HP drops to {wimpy}% or below."

        try:
            value = int(args.strip())
        except ValueError:
            return "Usage: wimpy <0-50>  (0 disables wimpy)"

        if value < 0 or value > 50:
            return "Wimpy must be between 0 and 50."

        character.wimpy = value
        if value == 0:
            return "Wimpy disabled. You will fight to the bitter end."
        return f"Wimpy set to {value}%. You will automatically flee when your HP drops to {value}% or below."

    # =========================================================================
    # Scan Command (System 5)
    # =========================================================================

    def cmd_scan(self, character, args):
        """Scan adjacent rooms for mobs and players.
        Usage: scan
        """
        exits = getattr(character.room, 'exits', {})
        if not exits:
            return "You see no exits to scan."

        lines = ["You scan your surroundings:"]
        for direction, exit_data in exits.items():
            vnum = _resolve_exit(exit_data)
            adjacent = self.world.rooms.get(vnum)
            if adjacent is None:
                continue

            occupants = []
            for mob in getattr(adjacent, 'mobs', []):
                if getattr(mob, 'alive', True):
                    occupants.append(mob.name)
            for player in getattr(adjacent, 'players', []):
                occupants.append(player.name)

            if occupants:
                lines.append(f"  Looking {direction}: {', '.join(occupants)}")
            else:
                lines.append(f"  Looking {direction}: nothing")

        if len(lines) == 1:
            return "You scan around but see nothing of interest nearby."
        return "\n".join(lines)

    # =========================================================================
    # Identify Command (System 8)
    # =========================================================================

    def cmd_identify(self, character, args):
        """Identify a magical item using Spellcraft (DC 15).
        Usage: identify <item name>
        """
        if not args:
            return "Identify what? Usage: identify <item name>"

        item_name = args.strip().lower()
        item = None
        for i in character.inventory:
            if item_name in i.name.lower():
                item = i
                break

        if not item:
            return f"You don't have '{args.strip()}' in your inventory."

        result = character.skill_check("Spellcraft")
        if isinstance(result, str):
            # Trained-only failure message returned by skill_check
            return result

        if result < 15:
            return "You study the item carefully, but fail to identify it."

        # Build identification output
        lines = [f"\033[1;36mYou successfully identify: {item.name}\033[0m"]
        item_type = getattr(item, 'item_type', None)
        if item_type:
            lines.append(f"  Type: {item_type}")
        magical = getattr(item, 'magical', False)
        lines.append(f"  Magical: {'Yes' if magical else 'No'}")
        value = getattr(item, 'value', 0)
        lines.append(f"  Value: {value} gp")
        damage = getattr(item, 'damage', None)
        if damage:
            lines.append(f"  Damage: {damage}")
        ac_bonus = getattr(item, 'ac_bonus', None)
        if ac_bonus:
            lines.append(f"  AC Bonus: +{ac_bonus}")
        stat_bonuses = getattr(item, 'stat_bonuses', None)
        if stat_bonuses:
            lines.append(f"  Stat Bonuses: {stat_bonuses}")
        properties = getattr(item, 'properties', None)
        if properties:
            lines.append(f"  Properties: {properties}")
        stats = getattr(item, 'stats', None)
        if stats:
            lines.append(f"  Stats: {stats}")
        return "\n".join(lines)

    # =========================================================================
    # Track Command (System 9)
    # =========================================================================

    def cmd_track(self, character, args):
        """Track a creature or player through adjacent rooms.
        Requires the Track feat and a Survival check (DC 15).
        Usage: track <name>
        """
        if not args:
            return "Track whom? Usage: track <name>"

        if not character.has_feat("Track"):
            return "You need the Track feat to use this ability."

        result = character.skill_check("Survival")
        if isinstance(result, str):
            return result

        if result < 15:
            return "You search for tracks but fail to find any trail."

        target_name = args.strip().lower()
        exits = getattr(character.room, 'exits', {})
        found_direction = None

        for direction, exit_data in exits.items():
            vnum = _resolve_exit(exit_data)
            adjacent = self.world.rooms.get(vnum)
            if adjacent is None:
                continue
            for mob in getattr(adjacent, 'mobs', []):
                if target_name in mob.name.lower() and getattr(mob, 'alive', True):
                    found_direction = direction
                    break
            if not found_direction:
                for player in getattr(adjacent, 'players', []):
                    if target_name in player.name.lower():
                        found_direction = direction
                        break
            if found_direction:
                break

        if not found_direction:
            return f"You carefully study the ground but find no tracks for '{args.strip()}'."

        return (f"\033[0;32mYou pick up the trail of {args.strip()} "
                f"heading {found_direction}.\033[0m")

    # =========================================================================
    # Consumable Commands (Systems 13-15: Potions / Scrolls / Wands)
    # =========================================================================

    def cmd_quaff(self, character, args):
        """Drink a potion from your inventory.
        Usage: quaff <potion name>  (aliases: drink)
        """
        if not args:
            return "Quaff what? Usage: quaff <potion name>"

        # Find potion in inventory by name (case-insensitive, partial match)
        item = None
        target_name = args.strip().lower()
        for i in character.inventory:
            if target_name in i.name.lower():
                item = i
                break

        if not item:
            return f"You don't have '{args.strip()}' in your inventory."

        if item.item_type != "potion":
            return f"{item.name} is not a potion."

        messages = [f"You uncork and drink {item.name}."]

        # Apply healing
        healing = item.stats.get("healing", 0)
        if healing:
            old_hp = character.hp
            character.hp = min(character.max_hp, character.hp + healing)
            actual_heal = character.hp - old_hp
            messages.append(f"You are healed for {actual_heal} HP! [HP: {character.hp}/{character.max_hp}]")

        # Apply buff effect if present
        spell_name = item.stats.get("spell")
        if spell_name:
            duration = item.stats.get("duration", 10)
            if not hasattr(character, "active_buffs"):
                character.active_buffs = {}
            character.active_buffs[spell_name] = {
                "value": item.stats.get("spell_value", 1),
                "duration": duration,
                "spell": spell_name
            }
            messages.append(f"You feel the magic of {spell_name} wash over you! ({duration} rounds)")

        # Consume the potion
        character.inventory.remove(item)

        return "\n".join(messages)

    def cmd_read_scroll(self, character, args):
        """Read a magical scroll from your inventory.
        Usage: read <scroll name>
        """
        if not args:
            return "Read what? Usage: read <scroll name>"

        # Find scroll in inventory by name (case-insensitive, partial match)
        item = None
        target_name = args.strip().lower()
        for i in character.inventory:
            if target_name in i.name.lower():
                item = i
                break

        if not item:
            return f"You don't have '{args.strip()}' in your inventory."

        if item.item_type != "scroll":
            return f"{item.name} is not a scroll."

        # Spellcraft check DC 15 + spell_level
        spell_level = item.stats.get("spell_level", 1)
        dc = 15 + spell_level

        result = character.skill_check("Spellcraft")

        # Consume scroll regardless of outcome
        character.inventory.remove(item)

        if isinstance(result, str):
            # Trained-only failure: character cannot use the scroll
            return "The scroll crumbles to dust! You failed to decipher it."

        if result < dc:
            return "The scroll crumbles to dust! You failed to decipher it."

        # Success: apply stored spell effect
        messages = [f"You read {item.name} aloud, releasing its magic!"]

        healing = item.stats.get("healing", 0)
        if healing:
            old_hp = character.hp
            character.hp = min(character.max_hp, character.hp + healing)
            actual_heal = character.hp - old_hp
            messages.append(f"You are healed for {actual_heal} HP! [HP: {character.hp}/{character.max_hp}]")

        damage = item.stats.get("damage", 0)
        if damage:
            # Apply damage to current combat target if any, else notify
            target = getattr(character, "target", None)
            if target and getattr(target, "alive", True):
                target.hp = max(0, target.hp - damage)
                messages.append(f"The scroll's magic strikes {target.name} for {damage} damage!")
            else:
                messages.append("The scroll's magic discharges harmlessly (no valid target).")

        spell_name = item.stats.get("spell")
        if spell_name and not healing and not damage:
            duration = item.stats.get("duration", 10)
            if not hasattr(character, "active_buffs"):
                character.active_buffs = {}
            character.active_buffs[spell_name] = {
                "value": item.stats.get("spell_value", 1),
                "duration": duration,
                "spell": spell_name
            }
            messages.append(f"You feel the magic of {spell_name} wash over you! ({duration} rounds)")

        return "\n".join(messages)

    def cmd_use(self, character, args):
        """Use an item from your inventory.
        Usage: use <item name>
        Dispatches to the appropriate handler based on item type.
        """
        if not args:
            return "Use what? Usage: use <item name>"

        # Find item in inventory by name (case-insensitive, partial match)
        item = None
        target_name = args.strip().lower()
        for i in character.inventory:
            if target_name in i.name.lower():
                item = i
                break

        if not item:
            return f"You don't have '{args.strip()}' in your inventory."

        if item.item_type == "potion":
            return self.cmd_quaff(character, args)

        if item.item_type == "scroll":
            return self.cmd_read_scroll(character, args)

        if item.item_type == "wand":
            charges = getattr(item, "charges", None)
            if charges is None or charges <= 0:
                return f"{item.name} has no charges remaining."

            # Use Magic Device check if character's class is not in the wand's class list
            class_list = item.stats.get("class_list", [])
            char_class = getattr(character, "char_class", "")
            requires_umd = char_class not in class_list

            if requires_umd:
                umd_result = character.skill_check("Use Magic Device")
                if isinstance(umd_result, str):
                    return f"You wave {item.name} but can't activate it. (Use Magic Device untrained)"
                if umd_result < 20:
                    return (f"You fail to activate {item.name}. "
                            f"(Use Magic Device DC 20, you rolled {umd_result})")

            # Decrement charges and apply spell effect
            item.charges -= 1
            messages = [f"You activate {item.name}! ({item.charges} charges remaining)"]

            healing = item.stats.get("healing", 0)
            if healing:
                old_hp = character.hp
                character.hp = min(character.max_hp, character.hp + healing)
                actual_heal = character.hp - old_hp
                messages.append(f"You are healed for {actual_heal} HP! [HP: {character.hp}/{character.max_hp}]")

            damage = item.stats.get("damage", 0)
            if damage:
                target = getattr(character, "target", None)
                if target and getattr(target, "alive", True):
                    target.hp = max(0, target.hp - damage)
                    messages.append(f"The wand's magic strikes {target.name} for {damage} damage!")
                else:
                    messages.append("The wand's magic discharges harmlessly (no valid target).")

            spell_name = item.stats.get("spell")
            if spell_name and not healing and not damage:
                duration = item.stats.get("duration", 10)
                if not hasattr(character, "active_buffs"):
                    character.active_buffs = {}
                character.active_buffs[spell_name] = {
                    "value": item.stats.get("spell_value", 1),
                    "duration": duration,
                    "spell": spell_name
                }
                messages.append(f"You feel the magic of {spell_name} wash over you! ({duration} rounds)")

            # Remove wand if depleted
            if item.charges == 0:
                character.inventory.remove(item)
                messages.append(f"{item.name} crumbles to dust \u2014 its magic is spent.")

            return "\n".join(messages)

        return f"You can't figure out how to use {item.name}."

    # =========================================================================
    # System 18: Day/Night Gameplay Effects
    # =========================================================================

    def _get_effective_light(self, room):
        """Return the effective light level for a room, adjusted for time of day.
        Also considers active light sources carried by players in the room.
        """
        LIGHT_LEVELS = ("dark", "dim", "normal", "bright")

        base = room.light if room.light else "normal"
        # Indoor rooms are unaffected by day/night cycle
        if "indoor" in getattr(room, 'flags', []):
            # Still apply light source boost for indoor rooms
            for p in getattr(room, 'players', []):
                if getattr(p, 'light_source', None):
                    # A lit light source raises the effective level to at least "normal"
                    if base in LIGHT_LEVELS and LIGHT_LEVELS.index(base) < LIGHT_LEVELS.index("normal"):
                        base = "normal"
                    break
            return base
        game_time = get_game_time()
        if game_time.is_nighttime():
            if base in ("normal", "bright", None):
                base = "dim"
            elif base == "dim":
                base = "dark"
        # Light source override: any player in room with a light source raises floor to "normal"
        for p in getattr(room, 'players', []):
            if getattr(p, 'light_source', None):
                if base in LIGHT_LEVELS and LIGHT_LEVELS.index(base) < LIGHT_LEVELS.index("normal"):
                    base = "normal"
                break
        return base

    # =========================================================================
    # System 19: Weather Effects
    # =========================================================================

    def cmd_weather(self, character, args):
        """
        Show current weather conditions and their mechanical effects.
        Usage: weather
        """
        room = character.room
        game_time = get_game_time()

        if "indoor" in getattr(room, 'flags', []):
            return "You are indoors. You can't see the weather."

        weather = getattr(room, 'weather', None)
        lines = []

        if weather is None or weather == "clear":
            lines.append("The skies are clear.")
        elif weather == "rain":
            lines.append("Rain falls steadily. (-2 ranged attacks, -4 Spot)")
        elif weather == "storm":
            lines.append("A fierce storm rages! (half movement, concentration DC +4)")
        elif weather == "heat":
            lines.append("The heat is oppressive. (fire spells +1 CL)")
        elif weather == "cold":
            lines.append("A bitter cold grips the land. (cold spells +1 CL)")
        elif weather == "snow":
            lines.append("Snow blankets the area. (-2 movement, +2 Hide in snow)")
        else:
            lines.append(f"The weather is: {weather}.")

        lines.append(f"Current time: {game_time.get_full_time_string()}")
        return "\n".join(lines)

    def get_weather_modifier(self, room, modifier_type):
        """
        Return an integer modifier for the given modifier_type based on room weather.

        modifier_type options: "ranged_attack", "spot", "movement_speed",
                               "concentration_dc", "fire_cl", "cold_cl", "hide"
        Returns 0 if no weather or the room is indoor.
        """
        if "indoor" in getattr(room, 'flags', []):
            return 0

        weather = getattr(room, 'weather', None)
        if not weather or weather == "clear":
            return 0

        modifiers = {
            "rain":  {"ranged_attack": -2, "spot": -4},
            "storm": {"movement_speed": -50, "concentration_dc": 4},
            "heat":  {"fire_cl": 1},
            "cold":  {"cold_cl": 1},
            "snow":  {"movement_speed": -2, "hide": 2},
        }

        weather_mods = modifiers.get(weather, {})
        return weather_mods.get(modifier_type, 0)

    # =========================================================================
    # System 20: Map Display
    # =========================================================================

    def cmd_map(self, character, args):
        """
        Display a simple ASCII map of immediate exits from the current room.
        Usage: map
        """
        room = character.room
        exits = getattr(room, 'exits', {})

        def room_label(vnum, current=False):
            r = self.world.rooms.get(vnum)
            if r is None:
                return "[??????]"
            abbrev = r.name[:8]
            if current:
                return f"[*{abbrev[:6]}*]"
            return f"[{abbrev:<6}]"

        north_vnum = _resolve_exit(exits["north"]) if "north" in exits else None
        south_vnum = _resolve_exit(exits["south"]) if "south" in exits else None
        east_vnum  = _resolve_exit(exits["east"])  if "east"  in exits else None
        west_vnum  = _resolve_exit(exits["west"])  if "west"  in exits else None
        up_vnum    = _resolve_exit(exits["up"])    if "up"    in exits else None
        down_vnum  = _resolve_exit(exits["down"])  if "down"  in exits else None

        current_label = room_label(room.vnum, current=True)
        lines = []

        # Up
        if up_vnum is not None:
            lines.append(f"              {room_label(up_vnum)} (up)")

        # North row
        north_label = room_label(north_vnum) if north_vnum is not None else "        "
        lines.append(f"         {north_label}")
        lines.append("              |")

        # West - current - east row
        west_label = room_label(west_vnum) if west_vnum is not None else "        "
        east_label = room_label(east_vnum) if east_vnum is not None else "        "
        lines.append(f"{west_label}--{current_label}--{east_label}")

        # South row
        lines.append("              |")
        south_label = room_label(south_vnum) if south_vnum is not None else "        "
        lines.append(f"         {south_label}")

        # Down
        if down_vnum is not None:
            lines.append(f"              {room_label(down_vnum)} (down)")

        # Extra exits (non-cardinal)
        extra = [d for d in exits if d not in ("north", "south", "east", "west", "up", "down")]
        if extra:
            extra_parts = []
            for d in extra:
                v = _resolve_exit(exits[d])
                extra_parts.append(f"{d}: {room_label(v)}")
            lines.append("Other exits: " + ", ".join(extra_parts))

        return "\n".join(lines)

    # =========================================================================
    # Party / Group system (Phase 3)
    # =========================================================================

    def cmd_group(self, character, args):
        """Manage your party. Usage: group | group invite <name> | group leave | group disband | group kick <name>"""
        from src.party import Party
        from src.chat import send_to_player

        sub = args.strip().lower() if args else ""

        if not sub:
            # Show party status
            if not getattr(character, 'party', None):
                return "You are not in a group."
            return character.party.get_status()

        parts = sub.split(None, 1)
        action = parts[0]
        target_name = parts[1].strip() if len(parts) > 1 else ""

        if action == "invite":
            if not target_name:
                return "Invite whom? Usage: group invite <name>"
            # Find the target player in the world
            target = next(
                (p for p in self.world.players if p.name.lower() == target_name.lower()),
                None
            )
            if not target:
                return f"No player named '{target_name}' is online."
            if target is character:
                return "You cannot invite yourself."
            # Create a party if this character doesn't have one
            if not getattr(character, 'party', None):
                character.party = Party(character)
            party = character.party
            if party.is_member(target):
                return f"{target.name} is already in your party."
            party.invite(target.name)
            send_to_player(target,
                f"\033[32m{character.name} invites you to join their party. "
                f"Type 'follow {character.name}' to accept.\033[0m")
            return f"You invite {target.name} to join your party."

        if action == "leave":
            party = getattr(character, 'party', None)
            if not party:
                return "You are not in a group."
            party.remove_member(character)
            character.party = None
            character.following = None
            if not party.members:
                party.disband()
            else:
                # Notify remaining members
                for member in party.members:
                    send_to_player(member, f"\033[32m{character.name} has left the party.\033[0m")
            return "You leave the party."

        if action == "disband":
            party = getattr(character, 'party', None)
            if not party:
                return "You are not in a group."
            if party.leader is not character:
                return "Only the party leader can disband the group."
            members = list(party.members)
            party.disband()
            for member in members:
                if member is not character:
                    send_to_player(member, "\033[32mThe party has been disbanded.\033[0m")
            return "You disband the party."

        if action == "kick":
            if not target_name:
                return "Kick whom? Usage: group kick <name>"
            party = getattr(character, 'party', None)
            if not party:
                return "You are not in a group."
            if party.leader is not character:
                return "Only the party leader can kick members."
            target = next(
                (m for m in party.members if m.name.lower() == target_name.lower()),
                None
            )
            if not target:
                return f"'{target_name}' is not in your party."
            if target is character:
                return "You cannot kick yourself. Use 'group disband' to end the party."
            party.remove_member(target)
            target.party = None
            target.following = None
            send_to_player(target, "\033[32mYou have been removed from the party.\033[0m")
            for member in party.members:
                send_to_player(member, f"\033[32m{target.name} has been removed from the party.\033[0m")
            return f"You remove {target.name} from the party."

        return "Unknown group command. Usage: group | group invite <name> | group leave | group disband | group kick <name>"

    def cmd_follow(self, character, args):
        """Begin following a player in the same room. Usage: follow <name>"""
        from src.party import Party
        from src.chat import send_to_player

        if not args:
            return "Follow whom? Usage: follow <name>"
        target_name = args.strip().lower()
        target = next(
            (p for p in getattr(character.room, 'players', [])
             if p.name.lower() == target_name and p is not character),
            None
        )
        if not target:
            return f"You don't see '{args.strip()}' here."

        character.following = target

        # Auto-join party if there is a pending invite
        target_party = getattr(target, 'party', None)
        if target_party and character.name in target_party.pending_invites:
            if getattr(character, 'party', None) and character.party is not target_party:
                # Leave old party first
                old_party = character.party
                old_party.remove_member(character)
                if not old_party.members:
                    old_party.disband()
            target_party.add_member(character)
            character.party = target_party
            # Notify party members
            for member in target_party.members:
                if member is not character:
                    send_to_player(member, f"\033[32m{character.name} has joined the party.\033[0m")
            return f"You begin following {target.name} and join their party."

        return f"You begin following {target.name}."

    def cmd_unfollow(self, character, args):
        """Stop following and leave your party. Usage: unfollow"""
        from src.chat import send_to_player

        character.following = None
        party = getattr(character, 'party', None)
        if party:
            party.remove_member(character)
            character.party = None
            if not party.members:
                party.disband()
            else:
                for member in party.members:
                    send_to_player(member, f"\033[32m{character.name} has left the party.\033[0m")
        return "You stop following."

    def cmd_assist(self, character, args):
        """Join a party member's combat and target their target. Usage: assist <name>"""
        from src.combat import get_combat, start_combat
        from src.chat import send_to_player

        party = getattr(character, 'party', None)
        if not party:
            return "You must be in a party to assist someone."

        if not args:
            return "Assist whom? Usage: assist <name>"
        target_name = args.strip().lower()

        # Find the party member in the same room
        ally = next(
            (m for m in party.members
             if m.name.lower() == target_name.lower()
             and m is not character
             and m.room is character.room),
            None
        )
        if not ally:
            return f"No party member named '{args.strip()}' is here."

        from src.character import State
        if ally.state != State.COMBAT:
            return f"{ally.name} is not in combat."

        combat_target = getattr(ally, 'combat_target', None)
        if not combat_target:
            return f"{ally.name} has no current target."

        # Join the combat targeting the ally's target
        combat = get_combat(character.room)
        if combat:
            combat.add_combatant(character)
        else:
            start_combat(character.room, character, combat_target)

        character.combat_target = combat_target
        character.state = State.COMBAT

        send_to_player(ally, f"\033[32m{character.name} assists you!\033[0m")
        return f"You assist {ally.name}, attacking {combat_target.name}!"

    def cmd_gtell(self, character, args):
        """Send a message to all party members. Usage: gtell <message>"""
        from src.chat import send_to_player

        party = getattr(character, 'party', None)
        if not party:
            return "You are not in a group."
        if not args:
            return "Say what to your party?"

        message = args.strip()
        formatted = f"\033[32m[Party] {character.name}: {message}\033[0m"
        for member in party.members:
            if member is not character:
                send_to_player(member, formatted)
        return formatted

    # =========================================================================
    # Phase 3: Crafting System
    # =========================================================================

    def cmd_craft(self, character, args):
        """
        Craft an item using materials in your inventory.
        Usage: craft <recipe name>
        Use 'recipes' to see available recipes.
        """
        import src.crafting as crafting

        if not args or not args.strip():
            return "Craft what? Use 'recipes' to see available recipes."

        recipe_name = args.strip()
        recipe = crafting.find_recipe(recipe_name)
        if recipe is None:
            return f"No recipe found for '{recipe_name}'. Use 'recipes' to see available recipes."

        has_all, missing = crafting.check_materials(character, recipe)
        if not has_all:
            lines = ["You are missing materials:"]
            for m in missing:
                lines.append(f"  - {m}")
            return "\n".join(lines)

        success, message, item = crafting.craft_item(character, recipe)

        if success:
            crafting.consume_materials(character, recipe)
            character.inventory.append(item)
            character.craft_count = getattr(character, 'craft_count', 0) + 1
            return message
        else:
            # Critical failure: result < dc - 5, materials are lost
            dc = recipe["dc"]
            # Re-check: craft_item already returned the message; determine if critical
            # We detect critical by the message text (materials ruined)
            if "ruined" in message:
                crafting.consume_materials(character, recipe)
            return message

    def cmd_recipes(self, character, args):
        """
        List all available crafting recipes with required materials and DC.
        Usage: recipes
        """
        import src.crafting as crafting

        recipes = crafting.load_recipes()
        if not recipes:
            return "No recipes are available."

        lines = ["Available Crafting Recipes:", "-" * 40]
        for recipe in recipes:
            mats = ", ".join(
                f"{m['name']} x{m['qty']}" for m in recipe["materials"]
            )
            lines.append(
                f"  {recipe['name']:<20} Skill: {recipe['skill']:<28} DC: {recipe['dc']:<4} Materials: {mats}"
            )
        lines.append("-" * 40)
        lines.append("Use: craft <recipe name>")
        return "\n".join(lines)


    # =========================================================================
    # Phase 4: Achievement System (System 30)
    # =========================================================================

    def _load_achievements(self):
        """Load achievement definitions from data/achievements.json."""
        import os, json
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'achievements.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def check_achievements(self, character):
        """
        Check all achievements against current character stats.
        Awards any newly-met achievements and appends the associated title.
        Returns a list of award messages (may be empty).
        Call this after kills, level-ups, crafting, or gold changes.
        """
        try:
            achievements = self._load_achievements()
        except Exception:
            return []

        earned = getattr(character, 'achievements', [])
        messages = []

        for ach in achievements:
            if ach['id'] in earned:
                continue

            trigger = ach['trigger']
            threshold = ach['threshold']

            if trigger == 'kill_count':
                value = getattr(character, 'kill_count', 0)
            elif trigger == 'level':
                value = getattr(character, 'level', 1)
            elif trigger == 'gold':
                value = getattr(character, 'gold', 0)
            elif trigger == 'craft_count':
                value = getattr(character, 'craft_count', 0)
            elif trigger == 'rooms_visited':
                value = len(getattr(character, 'rooms_visited', set()))
            else:
                continue

            if value >= threshold:
                character.achievements.append(ach['id'])
                title = ach.get('title')
                if title and title not in getattr(character, 'titles', []):
                    character.titles.append(title)
                messages.append(
                    f"\033[33m*** Achievement Unlocked: {ach['name']} — {ach['description']}!"
                    f" (Title awarded: {title}) ***\033[0m"
                )

        return messages

    def cmd_faction(self, character, args):
        """
        Faction and reputation system.
        Usage: faction              — List all factions and your standing
               faction info <name>  — Detailed info on a faction
               faction join <name>  — Join a faction (if eligible)
               faction leave        — Leave your current faction
        """
        from src.factions import get_faction_manager
        fm = get_faction_manager()

        if not args:
            return fm.format_faction_list(character)

        parts = args.strip().split(None, 1)
        subcmd = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""

        if subcmd == "list":
            return fm.format_faction_list(character)

        elif subcmd == "info":
            if not subargs:
                return "Usage: faction info <faction name>"
            # Fuzzy match faction by name
            query = subargs.lower()
            for fid, faction in fm.get_all_factions().items():
                if query in faction.get("name", "").lower() or query in fid:
                    return fm.format_faction_info(character, fid)
            return f"No faction matching '{subargs}' found."

        elif subcmd == "join":
            if not subargs:
                return "Usage: faction join <faction name>"
            query = subargs.lower()
            for fid, faction in fm.get_all_factions().items():
                if query in faction.get("name", "").lower() or query in fid:
                    return fm.join_faction(character, fid)
            return f"No faction matching '{subargs}' found."

        elif subcmd == "leave":
            return fm.leave_faction(character)

        else:
            # Try treating the whole args as a faction name for info
            query = args.strip().lower()
            for fid, faction in fm.get_all_factions().items():
                if query in faction.get("name", "").lower() or query in fid:
                    return fm.format_faction_info(character, fid)
            return "Usage: faction [list|info <name>|join <name>|leave]"

    def cmd_study(self, character, args):
        """Study a rune-circle in the current room. Usage: study"""
        from src.location_effects import get_location_effects
        return get_location_effects().interact_rune_circle(character, character.room, "study")

    def cmd_activate(self, character, args):
        """Activate a rune-circle in the current room. Usage: activate"""
        from src.location_effects import get_location_effects
        return get_location_effects().interact_rune_circle(character, character.room, "activate")

    def cmd_repair(self, character, args):
        """Repair a damaged rune-circle. Usage: repair"""
        from src.location_effects import get_location_effects
        return get_location_effects().interact_rune_circle(character, character.room, "repair")

    def cmd_pray(self, character, args):
        """Pray at a shrine or altar for a divine blessing.
        Usage: pray [optional prayer text]"""
        from src.religion import get_religion_manager
        rm = get_religion_manager()
        msg, deity_player = rm.pray(character, character.room, self.world)
        # If a player-deity is online, notify them
        if deity_player and hasattr(deity_player, '_writer'):
            prayer_text = args.strip() if args else ""
            notify = rm.notify_deity_player(deity_player, character, prayer_text)
            try:
                deity_player._writer.write(notify + "\n")
            except Exception:
                pass
        return msg

    def cmd_worship(self, character, args):
        """View info about a deity. Usage: worship <deity name>"""
        from src.religion import get_religion_manager
        rm = get_religion_manager()
        if not args:
            if character.deity:
                did, d = rm.find_deity(character.deity)
                if did:
                    return rm.format_deity_info(character, did)
            return "Usage: worship <deity name>  (or just 'deities' to list all)"
        did, d = rm.find_deity(args.strip())
        if did:
            return rm.format_deity_info(character, did)
        return f"No deity matching '{args.strip()}' found. Try 'deities' to see the list."

    def cmd_deities(self, character, args):
        """List all deities of Oreka. Usage: deities"""
        from src.religion import get_religion_manager
        rm = get_religion_manager()
        return rm.format_deity_list(character)

    def cmd_divine(self, character, args):
        """Divine powers for player-linked deities (admin/ascended players).
        Usage: divine bless <player>  — Heal and buff a follower
               divine smite <target>  — Strike with divine damage
               divine manifest        — Appear with divine presence
               divine speak <message> — Speak through all your shrines
               divine grant <player> <title> — Bestow a divine title
        Admin: @deity create <name>   — Create a new deity
               @deity link <id> <player> — Link deity to player account
               @deity unlink <id>     — Remove player link
               @deity shrine <id> <vnum> — Add shrine room"""
        from src.religion import get_religion_manager
        rm = get_religion_manager()

        if not args:
            return "Usage: divine [bless|smite|manifest|speak|grant]"

        parts = args.strip().split(None, 1)
        subcmd = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""

        # Check if this player is a linked deity or immortal
        is_deity = False
        for did, d in rm.get_all_deities().items():
            if d.get("player_name", "").lower() == character.name.lower():
                is_deity = True
                break

        if not is_deity and not getattr(character, 'is_immortal', False):
            return "You do not possess divine power."

        if subcmd == "bless":
            target = self._find_player_in_room(character, subargs)
            if not target:
                return f"No one named '{subargs}' is here."
            msg = rm.divine_bless(character, target)
            # Notify target
            if hasattr(target, '_writer'):
                try:
                    target._writer.write(msg + "\n")
                except Exception:
                    pass
            return msg

        elif subcmd == "smite":
            # Check mobs and players in room
            target = None
            for mob in character.room.mobs:
                if subargs.lower() in mob.name.lower():
                    target = mob
                    break
            if not target:
                target = self._find_player_in_room(character, subargs)
            if not target:
                return f"No target named '{subargs}' found here."
            msg = rm.divine_smite(character, target)
            return msg

        elif subcmd == "manifest":
            msg = rm.divine_manifest(character, character.room)
            # Broadcast to room
            for p in character.room.players:
                if p != character and hasattr(p, '_writer'):
                    try:
                        p._writer.write(msg + "\n")
                    except Exception:
                        pass
            return msg

        elif subcmd == "speak":
            if not subargs:
                return "Usage: divine speak <message>"
            notifications = rm.divine_speak(character, subargs, self.world)
            for player, nmsg in notifications:
                if hasattr(player, '_writer'):
                    try:
                        player._writer.write(nmsg + "\n")
                    except Exception:
                        pass
            return f"Your voice echoes through {len(notifications)} shrine(s)."

        elif subcmd == "grant":
            gparts = subargs.split(None, 1)
            if len(gparts) < 2:
                return "Usage: divine grant <player> <title>"
            target = self._find_player_in_room(character, gparts[0])
            if not target:
                return f"No one named '{gparts[0]}' is here."
            msg = rm.divine_grant_title(character, target, gparts[1])
            if hasattr(target, '_writer'):
                try:
                    target._writer.write(msg + "\n")
                except Exception:
                    pass
            return msg

        else:
            return "Usage: divine [bless|smite|manifest|speak|grant]"

    def _find_player_in_room(self, character, name):
        """Find a player in the same room by name."""
        if not name:
            return None
        for p in character.room.players:
            if p != character and p.name.lower() == name.strip().lower():
                return p
        return None

    def cmd_achievements(self, character, args):
        """
        Show all achievements and your progress toward them.
        Completed achievements are marked [X]; incomplete show current/threshold.
        Usage: achievements
        """
        try:
            achievements = self._load_achievements()
        except Exception:
            return "Achievement data unavailable."

        earned = getattr(character, 'achievements', [])
        lines = ["Your Achievements:", "-" * 50]

        for ach in achievements:
            trigger = ach['trigger']
            threshold = ach['threshold']

            if trigger == 'kill_count':
                value = getattr(character, 'kill_count', 0)
            elif trigger == 'level':
                value = getattr(character, 'level', 1)
            elif trigger == 'gold':
                value = getattr(character, 'gold', 0)
            elif trigger == 'craft_count':
                value = getattr(character, 'craft_count', 0)
            elif trigger == 'rooms_visited':
                value = len(getattr(character, 'rooms_visited', set()))
            else:
                value = 0

            if ach['id'] in earned:
                marker = "[X]"
                detail = f"{ach['name']} - {ach['description']}"
            else:
                marker = "[ ]"
                detail = f"{ach['name']} - {ach['description']} ({value}/{threshold})"

            lines.append(f"  {marker} {detail}")

        lines.append("-" * 50)
        lines.append(f"Completed: {len(earned)}/{len(achievements)}")
        return "\n".join(lines)

    # =========================================================================
    # Phase 4: Hunger / Thirst System (System 31)
    # =========================================================================

    def cmd_eat(self, character, args):
        """
        Eat a food item from your inventory to restore hunger.
        Usage: eat <food item name>
               eat  (eats first food item found)
        """
        if args and args.strip():
            food = next(
                (i for i in character.inventory
                 if getattr(i, 'item_type', '') == 'food'
                 and i.name.lower() == args.strip().lower()),
                None
            )
            if food is None:
                return f"You don't have any food called '{args.strip()}'."
        else:
            food = next(
                (i for i in character.inventory
                 if getattr(i, 'item_type', '') == 'food'),
                None
            )
            if food is None:
                return "You have no food to eat."

        nourishment = getattr(food, 'stats', {}).get('nourishment', 25)
        old_hunger = character.hunger
        character.hunger = min(100, character.hunger + nourishment)
        character.inventory.remove(food)
        return f"You eat the {food.name}. (Hunger: {old_hunger} -> {character.hunger})"

    def cmd_drink_water(self, character, args):
        """
        Drink a beverage from your inventory to restore thirst.
        Usage: drink_water <drink item name>
               drink_water  (drinks first drink item found)
        """
        if args and args.strip():
            drink = next(
                (i for i in character.inventory
                 if getattr(i, 'item_type', '') == 'drink'
                 and i.name.lower() == args.strip().lower()),
                None
            )
            if drink is None:
                return f"You don't have any drink called '{args.strip()}'."
        else:
            drink = next(
                (i for i in character.inventory
                 if getattr(i, 'item_type', '') == 'drink'),
                None
            )
            if drink is None:
                return "You have nothing to drink."

        hydration = getattr(drink, 'stats', {}).get('hydration', 25)
        old_thirst = character.thirst
        character.thirst = min(100, character.thirst + hydration)
        character.inventory.remove(drink)
        return f"You drink the {drink.name}. (Thirst: {old_thirst} -> {character.thirst})"

    def cmd_survivalmode(self, character, args):
        """
        Toggle survival mode (enables hunger and thirst mechanics).
        Usage: survivalmode
        """
        character.survival_mode = not getattr(character, 'survival_mode', False)
        state = "enabled" if character.survival_mode else "disabled"
        return f"Survival mode {state}."

    # =========================================================================
    # Phase 4: Player Housing (System 32)
    # =========================================================================

    def cmd_buyroom(self, character, args):
        """
        Purchase the current room as your home.
        The room must have the 'housing' or 'realestate' flag and be unowned.
        Cost: 500 gold.
        Usage: buyroom
        """
        room = character.room
        if room is None:
            return "You are not in a room."

        flags = getattr(room, 'flags', []) or []
        if not any(f in flags for f in ('housing', 'realestate')):
            return "This room is not available for purchase."

        if getattr(room, 'owner', None) is not None:
            return "This room is already owned by someone else."

        cost = 500
        if character.gold < cost:
            return (
                f"You need {cost} gold to purchase this room. "
                f"(You have {character.gold} gold)"
            )

        character.gold -= cost
        room.owner = character.name
        return f"You purchase this room for {cost} gold! It is now your home."

    def cmd_setdesc(self, character, args):
        """
        Set a custom description for your owned room.
        Usage: setdesc <new description>
        """
        room = character.room
        if room is None:
            return "You are not in a room."

        if getattr(room, 'owner', None) != character.name:
            return "You do not own this room."

        if not args or not args.strip():
            return "Usage: setdesc <new description>"

        room.description = args.strip()
        return "Room description updated."

    def cmd_home(self, character, args):
        """
        Teleport to your owned home room.
        Usage: home
        """
        owned_room = None
        for room in self.world.rooms.values():
            if getattr(room, 'owner', None) == character.name:
                owned_room = room
                break

        if owned_room is None:
            return "You don't own a home."

        character.room = owned_room
        return f"You return home to {owned_room.name}."


    # =========================================================================
    # Phase 4 System 24: Mail System
    # =========================================================================

    def _mail_path(self, player_name):
        """Return absolute path to a player's mail file."""
        import os
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'mail')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.abspath(os.path.join(data_dir, f"{player_name.lower()}.json"))

    def _load_mail(self, player_name):
        """Load mail list for player; return empty list if no file."""
        import json, os
        path = self._mail_path(player_name)
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_mail(self, player_name, mail_list):
        """Persist mail list for player."""
        import json
        path = self._mail_path(player_name)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(mail_list, f, indent=2)

    def cmd_mail(self, character, args):
        """List your mail. Must be at a mailbox. Usage: mail"""
        if 'mailbox' not in getattr(character.room, 'flags', []):
            return "You need to be at a mailbox to read mail."
        mail_list = self._load_mail(character.name)
        if not mail_list:
            return "Your mailbox is empty."
        unread = sum(1 for m in mail_list if not m.get('read', False))
        lines = [f"Mailbox for {character.name} ({unread} unread, {len(mail_list)} total):"]
        lines.append(f"{'#':<4} {'From':<20} {'Subject':<35} Status")
        lines.append("-" * 65)
        for idx, entry in enumerate(mail_list, 1):
            status = "" if entry.get('read', False) else "[UNREAD]"
            lines.append(f"{idx:<4} {entry.get('from', '?'):<20} {entry.get('subject', ''):<35} {status}")
        lines.append("Use 'readmail <number>' to read a message.")
        return "\n".join(lines)

    def cmd_sendmail(self, character, args):
        """Send mail to a player. Usage: sendmail <player> <subject> = <body>"""
        if 'mailbox' not in getattr(character.room, 'flags', []):
            return "You need to be at a mailbox to send mail."
        if not args or '=' not in args:
            return "Usage: sendmail <player> <subject> = <body>"
        pre, body = args.split('=', 1)
        body = body.strip()
        pre_parts = pre.strip().split(None, 1)
        if len(pre_parts) < 2:
            return "Usage: sendmail <player> <subject> = <body>"
        recipient = pre_parts[0].strip()
        subject = pre_parts[1].strip()
        if not recipient or not subject or not body:
            return "Usage: sendmail <player> <subject> = <body>"
        if getattr(character, 'gold', 0) < 1:
            return "You need at least 1 gold coin to send mail."
        character.gold -= 1
        from datetime import datetime, timezone
        mail_list = self._load_mail(recipient)
        mail_list.append({
            "from": character.name,
            "subject": subject,
            "body": body,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False
        })
        self._save_mail(recipient, mail_list)
        return f"Mail sent to {recipient}. (1 gold charged)"

    def cmd_readmail(self, character, args):
        """Read a specific mail message. Usage: readmail <number>"""
        if 'mailbox' not in getattr(character.room, 'flags', []):
            return "You need to be at a mailbox to read mail."
        if not args or not args.strip().isdigit():
            return "Usage: readmail <number>"
        index = int(args.strip()) - 1
        mail_list = self._load_mail(character.name)
        if index < 0 or index >= len(mail_list):
            return f"No message number {args.strip()}. You have {len(mail_list)} message(s)."
        entry = mail_list[index]
        entry['read'] = True
        self._save_mail(character.name, mail_list)
        lines = [
            f"Message #{index + 1}",
            f"From   : {entry.get('from', '?')}",
            f"Subject: {entry.get('subject', '')}",
            f"Date   : {entry.get('timestamp', '')}",
            "-" * 50,
            entry.get('body', ''),
        ]
        return "\n".join(lines)

    # =========================================================================
    # Phase 4 System 25: Bulletin Boards
    # =========================================================================

    def _board_path(self, room_vnum):
        """Return absolute path to a room's board file."""
        import os
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'boards')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.abspath(os.path.join(data_dir, f"{room_vnum}.json"))

    def _load_board(self, room_vnum):
        """Load board posts for a room; return empty list if no file."""
        import json, os
        path = self._board_path(room_vnum)
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_board(self, room_vnum, posts):
        """Persist board posts for a room."""
        import json
        path = self._board_path(room_vnum)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2)

    def cmd_board(self, character, args):
        """List posts on the bulletin board in this room. Usage: board"""
        if 'board' not in getattr(character.room, 'flags', []):
            return "There is no bulletin board here."
        posts = self._load_board(character.room.vnum)
        if not posts:
            return "The bulletin board is empty."
        recent = list(reversed(posts))[:10]
        lines = [f"Bulletin Board ({len(posts)} post(s) total):"]
        lines.append(f"{'#':<4} {'Author':<20} {'Title':<40} Date")
        lines.append("-" * 75)
        for display_idx, post in enumerate(recent, 1):
            ts = post.get('timestamp', '')[:10]
            lines.append(f"{display_idx:<4} {post.get('author', '?'):<20} {post.get('title', ''):<40} {ts}")
        lines.append("Use 'readnote <number>' to read a post.")
        return "\n".join(lines)

    def cmd_post(self, character, args):
        """Post a note to the bulletin board. Usage: post <title> = <body>"""
        if 'board' not in getattr(character.room, 'flags', []):
            return "There is no bulletin board here."
        if not args or '=' not in args:
            return "Usage: post <title> = <body>"
        title_part, body = args.split('=', 1)
        title = title_part.strip()
        body = body.strip()
        if not title or not body:
            return "Usage: post <title> = <body>"
        from datetime import datetime, timezone
        posts = self._load_board(character.room.vnum)
        posts.append({
            "author": character.name,
            "title": title,
            "body": body,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self._save_board(character.room.vnum, posts)
        return f"You post a note titled '{title}' to the bulletin board."

    def cmd_readnote(self, character, args):
        """Read a post from the bulletin board. Usage: readnote <number>"""
        if 'board' not in getattr(character.room, 'flags', []):
            return "There is no bulletin board here."
        if not args or not args.strip().isdigit():
            return "Usage: readnote <number>"
        index = int(args.strip()) - 1
        posts = self._load_board(character.room.vnum)
        recent = list(reversed(posts))[:10]
        if index < 0 or index >= len(recent):
            return f"No post number {args.strip()}. The board shows {len(recent)} post(s)."
        post = recent[index]
        lines = [
            f"Post #{index + 1}",
            f"Author : {post.get('author', '?')}",
            f"Title  : {post.get('title', '')}",
            f"Date   : {post.get('timestamp', '')}",
            "-" * 50,
            post.get('body', ''),
        ]
        return "\n".join(lines)

    # =========================================================================
    # Phase 4 System 26: Auction House
    # =========================================================================

    def _auctions_path(self):
        """Return absolute path to the auctions data file."""
        import os
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        return os.path.abspath(os.path.join(data_dir, 'auctions.json'))

    def _load_auctions(self):
        """Load auctions list; return empty list if no file."""
        import json, os
        path = self._auctions_path()
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_auctions(self, auctions):
        """Persist auctions list."""
        import json
        path = self._auctions_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(auctions, f, indent=2)

    def _active_auctions(self, auctions):
        """Return only auctions that have not yet expired."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        result = []
        for a in auctions:
            try:
                expires = datetime.fromisoformat(a['expires'])
                if expires > now:
                    result.append(a)
            except Exception:
                pass
        return result

    def cmd_auction(self, character, args):
        """
        Auction house commands.
        Usage: auction list
               auction sell <item name> <min_bid> [buyout]
               auction bid <number> <amount>
               auction buyout <number>
               auction collect
        """
        from datetime import datetime, timezone, timedelta
        from src.items import Item

        parts = args.strip().split(None, 1) if args else []
        subcmd = parts[0].lower() if parts else 'list'
        rest = parts[1] if len(parts) > 1 else ''

        auctions = self._load_auctions()
        active = self._active_auctions(auctions)

        # --- list ---
        if subcmd == 'list':
            if not active:
                return "The auction house has no active listings."
            lines = ["Auction House - Active Listings:"]
            lines.append(f"{'#':<4} {'Seller':<16} {'Item':<28} {'Min':>7} {'Bid':>7} {'Buyout':>8} Expires")
            lines.append("-" * 80)
            for idx, a in enumerate(active, 1):
                buyout_str = str(a.get('buyout') or '-')
                expires = a.get('expires', '')[:10]
                lines.append(
                    f"{idx:<4} {a['seller']:<16} {a['item'].get('name', '?'):<28} "
                    f"{a['min_bid']:>7} {a['current_bid']:>7} {buyout_str:>8} {expires}"
                )
            return "\n".join(lines)

        # --- sell ---
        elif subcmd == 'sell':
            sell_parts = rest.split()
            if len(sell_parts) < 2:
                return "Usage: auction sell <item name> <min_bid> [buyout]"
            try:
                buyout = None
                if len(sell_parts) >= 3:
                    try:
                        buyout = int(sell_parts[-1])
                        min_bid = int(sell_parts[-2])
                        item_name = ' '.join(sell_parts[:-2])
                    except ValueError:
                        min_bid = int(sell_parts[-1])
                        item_name = ' '.join(sell_parts[:-1])
                        buyout = None
                else:
                    min_bid = int(sell_parts[-1])
                    item_name = ' '.join(sell_parts[:-1])
            except ValueError:
                return "Usage: auction sell <item name> <min_bid> [buyout]"
            if min_bid <= 0:
                return "Minimum bid must be at least 1 gold."
            if buyout is not None and buyout <= min_bid:
                return "Buyout price must be greater than the minimum bid."
            item = next(
                (i for i in character.inventory if i.name.lower() == item_name.lower()),
                None
            )
            if not item:
                return f"You don't have '{item_name}' in your inventory."
            character.inventory.remove(item)
            expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
            auctions.append({
                "seller": character.name,
                "item": item.to_dict(),
                "min_bid": min_bid,
                "current_bid": 0,
                "bidder": None,
                "buyout": buyout,
                "expires": expires
            })
            self._save_auctions(auctions)
            buyout_msg = f" (buyout: {buyout} gp)" if buyout is not None else ""
            return f"You list {item.name} on the auction house. Min bid: {min_bid} gp{buyout_msg}. Expires in 7 days."

        # --- bid ---
        elif subcmd == 'bid':
            bid_parts = rest.split()
            if len(bid_parts) < 2:
                return "Usage: auction bid <number> <amount>"
            try:
                auc_num = int(bid_parts[0])
                amount = int(bid_parts[1])
            except ValueError:
                return "Usage: auction bid <number> <amount>"
            if auc_num < 1 or auc_num > len(active):
                return "Invalid auction number. Use 'auction list' to see listings."
            auc = active[auc_num - 1]
            if auc['seller'] == character.name:
                return "You cannot bid on your own auction."
            min_required = max(auc['min_bid'], auc['current_bid'] + 1)
            if amount < min_required:
                return f"Your bid must be at least {min_required} gp. Current bid: {auc['current_bid']} gp."
            if getattr(character, 'gold', 0) < amount:
                return f"You don't have enough gold. (Need {amount} gp, have {character.gold} gp)"
            prev_bidder_name = auc.get('bidder')
            if prev_bidder_name:
                prev_amount = auc['current_bid']
                for p in getattr(self.world, 'players', []):
                    if p.name == prev_bidder_name:
                        p.gold = getattr(p, 'gold', 0) + prev_amount
                        from src.chat import send_to_player
                        send_to_player(p, f"Your bid on {auc['item'].get('name', '?')} was outbid. {prev_amount} gp returned.")
                        break
            character.gold -= amount
            auc['current_bid'] = amount
            auc['bidder'] = character.name
            self._save_auctions(auctions)
            return f"You bid {amount} gp on {auc['item'].get('name', '?')}."

        # --- buyout ---
        elif subcmd == 'buyout':
            if not rest.strip().isdigit():
                return "Usage: auction buyout <number>"
            auc_num = int(rest.strip())
            if auc_num < 1 or auc_num > len(active):
                return "Invalid auction number. Use 'auction list' to see listings."
            auc = active[auc_num - 1]
            if auc['seller'] == character.name:
                return "You cannot buyout your own auction."
            if auc.get('buyout') is None:
                return "This auction has no buyout price."
            buyout_price = auc['buyout']
            if getattr(character, 'gold', 0) < buyout_price:
                return f"You don't have enough gold. (Need {buyout_price} gp, have {character.gold} gp)"
            prev_bidder_name = auc.get('bidder')
            if prev_bidder_name and prev_bidder_name != character.name:
                prev_amount = auc['current_bid']
                for p in getattr(self.world, 'players', []):
                    if p.name == prev_bidder_name:
                        p.gold = getattr(p, 'gold', 0) + prev_amount
                        from src.chat import send_to_player
                        send_to_player(p, f"The auction for {auc['item'].get('name', '?')} ended via buyout. {prev_amount} gp returned.")
                        break
            character.gold -= buyout_price
            item = Item.from_dict(auc['item'])
            character.inventory.append(item)
            for p in getattr(self.world, 'players', []):
                if p.name == auc['seller']:
                    p.gold = getattr(p, 'gold', 0) + buyout_price
                    from src.chat import send_to_player
                    send_to_player(p, f"Your auction for {item.name} sold via buyout for {buyout_price} gp.")
                    break
            auctions.remove(auc)
            self._save_auctions(auctions)
            return f"You buy {item.name} for {buyout_price} gp."

        # --- collect ---
        elif subcmd == 'collect':
            now = datetime.now(timezone.utc)
            collected_items = []
            remaining = []
            for auc in auctions:
                try:
                    expires = datetime.fromisoformat(auc['expires'])
                except Exception:
                    remaining.append(auc)
                    continue
                if expires <= now:
                    if auc.get('bidder') == character.name:
                        item = Item.from_dict(auc['item'])
                        character.inventory.append(item)
                        collected_items.append(item.name)
                        for p in getattr(self.world, 'players', []):
                            if p.name == auc['seller']:
                                p.gold = getattr(p, 'gold', 0) + auc['current_bid']
                                from src.chat import send_to_player
                                send_to_player(p, f"Your auction for {item.name} sold for {auc['current_bid']} gp.")
                                break
                    elif auc.get('seller') == character.name and not auc.get('bidder'):
                        item = Item.from_dict(auc['item'])
                        character.inventory.append(item)
                        collected_items.append(f"{item.name} (unsold, returned)")
                    else:
                        remaining.append(auc)
                        continue
                else:
                    remaining.append(auc)
            self._save_auctions(remaining)
            if not collected_items:
                return "Nothing to collect from the auction house."
            lines = ["Collected from auction house:"]
            for name in collected_items:
                lines.append(f"  - {name}")
            return "\n".join(lines)

        else:
            return "Usage: auction [list|sell|bid|buyout|collect]"

    # =========================================================================
    # System 6: Light Sources
    # =========================================================================

    def cmd_light(self, character, args):
        """Light a torch, lantern, or other light source from inventory.
        Usage: light [item name]
        """
        light_types = ("torch", "lantern", "light")
        light_keywords = ("torch", "lantern")

        target_name = args.strip().lower() if args else ""

        # Search inventory for a matching light source
        found = None
        for item in character.inventory:
            itype = getattr(item, 'item_type', '').lower()
            iname = getattr(item, 'name', '').lower()

            type_match = itype in light_types
            name_match = any(kw in iname for kw in light_keywords)

            if type_match or name_match:
                if not target_name or target_name in iname:
                    found = item
                    break

        if not found:
            return "You have nothing to light."

        character.light_source = found
        return f"You light {found.name}."

    def cmd_extinguish(self, character, args):
        """Extinguish a held light source.
        Usage: extinguish
        """
        source = getattr(character, 'light_source', None)
        if not source:
            return "You have no light source to extinguish."

        name = getattr(source, 'name', 'the light source')
        character.light_source = None
        return f"You extinguish {name}."

    # =========================================================================
    # System 8: Cure Command (Poison / Disease)
    # =========================================================================

    def cmd_cure(self, character, args):
        """Attempt to cure poison or disease on yourself or another.
        Usage: cure [target]
        Heal skill DC 15 for poison, DC 20 for disease.
        """
        target_name = args.strip().lower() if args else ""

        # Resolve target: default to self
        target = character
        if target_name:
            # Check room players first
            for p in getattr(character.room, 'players', []):
                if p.name.lower() == target_name:
                    target = p
                    break
            else:
                # Check room mobs
                for m in getattr(character.room, 'mobs', []):
                    if m.name.lower() == target_name or target_name in m.name.lower():
                        target = m
                        break

        results = []

        # Attempt cure poison (Heal DC 15)
        if hasattr(target, 'has_condition') and target.has_condition('poisoned'):
            heal_roll = character.skill_check('Heal')
            if isinstance(heal_roll, int) and heal_roll >= 15:
                if hasattr(target, 'remove_condition'):
                    target.remove_condition('poisoned')
                if hasattr(target, 'active_conditions'):
                    target.active_conditions.pop('poisoned', None)
                if target is character:
                    results.append("You successfully cure your own poison!")
                else:
                    results.append(f"You successfully cure the poison afflicting {target.name}!")
            else:
                if target is character:
                    results.append("You fail to cure your own poison.")
                else:
                    results.append(f"You fail to cure the poison afflicting {target.name}.")

        # Attempt cure disease (Heal DC 20)
        if hasattr(target, 'has_condition') and target.has_condition('diseased'):
            heal_roll = character.skill_check('Heal')
            if isinstance(heal_roll, int) and heal_roll >= 20:
                if hasattr(target, 'remove_condition'):
                    target.remove_condition('diseased')
                if hasattr(target, 'active_conditions'):
                    target.active_conditions.pop('diseased', None)
                if target is character:
                    results.append("You successfully cure your own disease!")
                else:
                    results.append(f"You successfully cure the disease afflicting {target.name}!")
            else:
                if target is character:
                    results.append("You fail to cure your own disease.")
                else:
                    results.append(f"You fail to cure the disease afflicting {target.name}.")

        if not results:
            if target is character:
                return "You are not poisoned or diseased."
            else:
                return f"{target.name} is not poisoned or diseased."

        return "\n".join(results)

    # -------------------------------------------------------------------------
    # System 15: Config / Toggle Command
    # -------------------------------------------------------------------------

    def cmd_config(self, character, args):
        """Show or toggle player configuration settings.
        Usage: config              - show all settings
               config <setting>   - toggle a setting
        Settings: brief, compact, autoexit, color, autoloot, autogold,
                  survivalmode, autoattack
        """
        SETTINGS = {
            "brief":        ("brief_mode",          False, "Short room descriptions"),
            "compact":      ("compact_mode",         False, "Reduce blank lines"),
            "autoexit":     ("auto_exit",            True,  "Show exits automatically"),
            "color":        ("color_enabled",        True,  "ANSI color output"),
            "autoloot":     ("auto_loot",            False, "Auto-loot corpses"),
            "autogold":     ("auto_gold",            False, "Auto-collect gold"),
            "survivalmode": ("survival_mode",        False, "Hunger/thirst mechanics"),
            "autoattack":   ("auto_attack_enabled",  True,  "Auto-attack in combat"),
        }

        args = (args or "").strip().lower()

        if not args:
            lines = ["Current configuration settings:", ""]
            lines.append(f"  {'Setting':<14} {'Value':<6} Description")
            lines.append(f"  {'-'*14} {'-'*6} {'-'*30}")
            for name, (attr, default, desc) in SETTINGS.items():
                value = getattr(character, attr, default)
                val_str = "ON" if value else "OFF"
                lines.append(f"  {name:<14} {val_str:<6} {desc}")
            lines.append("")
            lines.append("Use 'config <setting>' to toggle.")
            return "\n".join(lines)

        if args not in SETTINGS:
            names = ", ".join(sorted(SETTINGS.keys()))
            return f"Unknown setting '{args}'. Valid settings: {names}"

        attr, default, desc = SETTINGS[args]
        current = getattr(character, attr, default)
        new_val = not current
        setattr(character, attr, new_val)
        state = "ON" if new_val else "OFF"
        return f"{desc} ({args}) is now {state}."

    # -------------------------------------------------------------------------
    # System 16: Areas / Zone List
    # -------------------------------------------------------------------------

    def cmd_areas(self, character, args):
        """List all known areas/zones.
        Usage: areas
        """
        import json as _json
        import os as _os

        meta_path = _os.path.join(_os.path.dirname(__file__), '..', 'data', 'areas_meta.json')
        areas = {}
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                areas = _json.load(f)
        except (FileNotFoundError, _json.JSONDecodeError):
            areas = {}

        lines = ["Areas and Zones:", ""]

        if areas:
            lines.append(f"  {'Level':<9} {'Area Name':<30} {'Builder':<15} Status")
            lines.append(f"  {'-'*9} {'-'*30} {'-'*15} {'-'*10}")
            for area_name, meta in sorted(areas.items()):
                if isinstance(meta, dict):
                    min_lv = meta.get('min_level', meta.get('min_lv', '?'))
                    max_lv = meta.get('max_level', meta.get('max_lv', '?'))
                    builder = meta.get('builder', meta.get('author', 'Unknown'))
                    status = meta.get('status', 'Open')
                    lv_range = f"[{min_lv}-{max_lv}]"
                    lines.append(f"  {lv_range:<9} {area_name:<30} {str(builder):<15} {status}")
                else:
                    lines.append(f"  {'[?-?]':<9} {area_name:<30} {'Unknown':<15} Open")
        else:
            seen = set()
            for room in self.world.rooms.values():
                af = getattr(room, 'area_file', None)
                if af and af not in seen:
                    seen.add(af)
                    area_display = _os.path.splitext(_os.path.basename(af))[0]
                    lines.append(f"  [?-?]     {area_display}")
            if not seen:
                lines.append("  No area information available.")

        lines.append("")
        if areas:
            total = len(areas)
        else:
            seen_files = {getattr(r, 'area_file', None)
                          for r in self.world.rooms.values()
                          if getattr(r, 'area_file', None)}
            total = len(seen_files)
        lines.append(f"{total} area(s) known.")
        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # System 17: Prompt Customization
    # -------------------------------------------------------------------------

    def cmd_prompt(self, character, args):
        """View or customize your prompt string.
        Usage: prompt                   - show current prompt and available tokens
               prompt default           - reset to default prompt
               prompt <template>        - set prompt to template
        Tokens: %h(hp) %H(max_hp) %a(ac) %x(xp_to_next) %v(move) %V(max_move)
                %g(gold) %RACE %CLASS %LEVEL %s(immortal tag)
        """
        DEFAULT_PROMPT = "AC %a HP %h/%H [%RACE] >"

        TOKENS = [
            ("%h",     "Current HP"),
            ("%H",     "Max HP"),
            ("%a",     "Armor Class"),
            ("%x",     "XP needed for next level"),
            ("%v",     "Current move points"),
            ("%V",     "Max move points"),
            ("%g",     "Gold carried"),
            ("%RACE",  "Character race"),
            ("%CLASS", "Character class"),
            ("%LEVEL", "Character level"),
            ("%s",     "Immortal tag (if applicable)"),
        ]

        args = (args or "").strip()

        if not args:
            lines = ["Current prompt:", f"  {character.prompt}", "",
                     "Available tokens:"]
            for token, desc in TOKENS:
                lines.append(f"  {token:<8} {desc}")
            lines.append("")
            lines.append("Usage: prompt <template>  |  prompt default")
            return "\n".join(lines)

        if args.lower() == "default":
            character.set_prompt(DEFAULT_PROMPT)
            return f"Prompt reset to default: {DEFAULT_PROMPT}"

        character.set_prompt(args)
        return f"Prompt set to: {args}"

    # -------------------------------------------------------------------------
    # System 18: Item Repair
    # -------------------------------------------------------------------------

    def _find_blacksmith(self, character):
        """Return the first alive mob in the character's room with 'blacksmith' in flags."""
        if not character.room:
            return None
        for mob in character.room.mobs:
            if not getattr(mob, 'alive', True):
                continue
            flags = getattr(mob, 'flags', None) or []
            if 'blacksmith' in flags:
                return mob
        return None

    def _find_item_for_repair(self, character, name):
        """Find item by name in inventory or equipment."""
        name_lower = name.lower()
        for item in character.inventory:
            if name_lower in item.name.lower():
                return item
        for slot, item in character.equipment.items():
            if item and name_lower in item.name.lower():
                return item
        return None

    def cmd_repair(self, character, args):
        """Repair a damaged item at a blacksmith.
        Usage: repair <item name>
        """
        blacksmith = self._find_blacksmith(character)
        if not blacksmith:
            return "There is no blacksmith here to repair your equipment."

        args = (args or "").strip()
        if not args:
            return "Repair which item? Usage: repair <item name>"

        item = self._find_item_for_repair(character, args)
        if not item:
            return f"You don't have '{args}' in your inventory or equipment."

        item_hp = getattr(item, 'hp', None)
        item_max_hp = getattr(item, 'max_hp', None)
        if item_hp is None or item_max_hp is None:
            return f"{item.name} cannot be repaired."

        if item_hp >= item_max_hp:
            return f"{item.name} doesn't need repair."

        missing = item_max_hp - item_hp
        cost = max(1, (getattr(item, 'value', 0) or 0) // 10) * missing
        gold = getattr(character, 'gold', 0)

        if gold < cost:
            return (f"Repairing {item.name} ({item_hp}/{item_max_hp} HP, "
                    f"missing {missing} points) would cost {cost} gold, "
                    f"but you only have {gold} gold.")

        item.hp = item_max_hp
        character.gold -= cost
        return (f"{blacksmith.name} repairs your {item.name} to full condition. "
                f"Cost: {cost} gold. (Remaining gold: {character.gold})")

    def cmd_repairall(self, character, args):
        """Repair all equipped items that need repair at a blacksmith.
        Usage: repairall
        """
        blacksmith = self._find_blacksmith(character)
        if not blacksmith:
            return "There is no blacksmith here to repair your equipment."

        total_cost = 0
        repaired = []

        for slot, item in character.equipment.items():
            if not item:
                continue
            item_hp = getattr(item, 'hp', None)
            item_max_hp = getattr(item, 'max_hp', None)
            if item_hp is None or item_max_hp is None:
                continue
            if item_hp >= item_max_hp:
                continue
            missing = item_max_hp - item_hp
            cost = max(1, (getattr(item, 'value', 0) or 0) // 10) * missing
            total_cost += cost
            repaired.append((item, cost, missing))

        if not repaired:
            return "All your equipped items are in perfect condition."

        gold = getattr(character, 'gold', 0)
        if gold < total_cost:
            item_list = "\n".join(
                f"  {it.name}: {cost} gold ({miss} HP missing)"
                for it, cost, miss in repaired
            )
            return (f"Repairing all damaged equipment would cost {total_cost} gold, "
                    f"but you only have {gold} gold.\n"
                    f"Damaged items:\n{item_list}")

        lines = [f"{blacksmith.name} repairs your equipment:"]
        for item, cost, missing in repaired:
            item.hp = item.max_hp
            lines.append(f"  {item.name}: restored {missing} HP ({cost} gold)")

        character.gold -= total_cost
        lines.append(f"Total cost: {total_cost} gold. (Remaining gold: {character.gold})")
        return "\n".join(lines)

    # =========================================================================
    # System 26: Summoning / Familiars
    # =========================================================================

    def cmd_summon(self, character, args):
        """Summon a temporary creature companion.
        Usage: summon [creature type]
        Requires a spellcasting class (Wizard, Sorcerer, Cleric, Druid, Magi).
        """
        import random
        SPELLCASTER_CLASSES = {"Wizard", "Sorcerer", "Cleric", "Druid", "Magi"}
        if character.char_class not in SPELLCASTER_CLASSES:
            return "Only spellcasters (Wizard, Sorcerer, Cleric, Druid, Magi) can summon creatures."

        # Deduct a spell slot (use level 1 slot by default)
        spells_used = getattr(character, 'spells_used', {})
        spells_per_day = getattr(character, 'spells_per_day', {})
        slot_level = 1
        # Find the lowest available slot
        for lvl in sorted(spells_per_day.keys()):
            used = spells_used.get(lvl, 0)
            available = spells_per_day.get(lvl, 0)
            if used < available:
                slot_level = lvl
                break
        else:
            # No slots found from spells_per_day — check if character has any slots at all
            if spells_per_day:
                return "You have no spell slots remaining to summon a creature."

        # Mark slot as used
        character.spells_used[slot_level] = spells_used.get(slot_level, 0) + 1

        # Build companion stats scaled to caster level
        lvl = character.level
        companion_hp = lvl * 4
        companion_ac = 10 + lvl // 2
        companion_damage = [1, 4 + lvl // 3, 0]

        creature_name = (args.strip() or "summoned creature").capitalize()

        from src.mob import Mob
        companion = Mob(
            vnum=-1,
            name=creature_name,
            level=lvl,
            hp_dice=[companion_hp, 1, 0],  # hp_dice computes: sum(randint(1,1) for _ in range(hp)) + 0 = hp
            ac=companion_ac,
            damage_dice=companion_damage,
            flags=["companion"],
            type_="Summoned",
            alignment="True Neutral",
        )
        # Force HP to exact value rather than rolled
        companion.hp = companion_hp
        companion.max_hp = companion_hp
        companion._companion_following = True

        character.companion = companion
        return (f"You channel magical energy and summon a {creature_name}!\n"
                f"{creature_name}: HP {companion.hp}, AC {companion.ac}, "
                f"Dmg 1d{companion_damage[1]} (level {lvl} summoned creature).")

    def cmd_familiar(self, character, args):
        """Bond with a permanent familiar (Wizard/Sorcerer only).
        Usage: familiar <type>
        Types: cat, rat, hawk, owl, snake, toad
        """
        if character.char_class not in ("Wizard", "Sorcerer"):
            return "Only Wizards and Sorcerers may bond with a familiar."

        if getattr(character, 'familiar_type', None):
            return "You already have a familiar."

        FAMILIAR_TYPES = {
            "cat":   ("cat",   "Move Silently", 3),
            "rat":   ("rat",   "Fort saves",    2),
            "hawk":  ("hawk",  "Spot",          3),
            "owl":   ("owl",   "Listen",        3),
            "snake": ("snake", "Bluff",         3),
            "toad":  ("toad",  "HP",            3),
        }

        chosen = (args.strip().lower() if args else "")
        if chosen not in FAMILIAR_TYPES:
            type_list = ", ".join(FAMILIAR_TYPES.keys())
            return f"Choose a familiar type: {type_list}"

        familiar_name, bonus_stat, bonus_val = FAMILIAR_TYPES[chosen]
        character.familiar_type = chosen

        # Apply the passive bonus
        if bonus_stat == "HP":
            character.max_hp += bonus_val
            character.hp = min(character.hp + bonus_val, character.max_hp)
            bonus_msg = f"+{bonus_val} max HP"
        elif bonus_stat == "Fort saves":
            # Store as a temp save bonus (fort)
            character.temp_save_bonus = getattr(character, 'temp_save_bonus', 0) + bonus_val
            bonus_msg = f"+{bonus_val} to Fortitude saves"
        else:
            # Skill bonus — add to skills dict
            current = character.skills.get(bonus_stat, 0)
            character.skills[bonus_stat] = current + bonus_val
            bonus_msg = f"+{bonus_val} to {bonus_stat}"

        return (f"You complete the familiar bonding ritual. A {familiar_name} "
                f"becomes your permanent companion!\nFamiliar bonus: {bonus_msg}.")

    # =========================================================================
    # System 28: Language System
    # =========================================================================

    def _get_known_languages(self, character):
        """Return the full set of languages a character knows."""
        from src.races import get_race
        known = set(getattr(character, 'known_languages', ["Common"]))
        race_data = get_race(character.race or "")
        if race_data:
            for lang in race_data.get("languages_auto", []):
                known.add(lang)
        return known

    def cmd_speak(self, character, args):
        """Set your active speaking language.
        Usage: speak <language>
        """
        if not args:
            current = getattr(character, 'speaking_language', 'Common')
            return f"You are currently speaking {current}. Usage: speak <language>"

        language = args.strip().title()
        known = self._get_known_languages(character)

        if language not in known:
            lang_list = ", ".join(sorted(known))
            return (f"You do not know the language '{language}'.\n"
                    f"Languages you know: {lang_list}")

        character.speaking_language = language
        return f"You will now speak in {language}."

    def cmd_languages(self, character, args):
        """List all languages you know and your currently active language.
        Usage: languages
        """
        from src.races import get_race
        known = self._get_known_languages(character)
        current = getattr(character, 'speaking_language', 'Common')

        lines = ["Languages you know:"]
        for lang in sorted(known):
            marker = " (active)" if lang == current else ""
            lines.append(f"  {lang}{marker}")

        race_data = get_race(character.race or "")
        if race_data:
            bonus_langs = race_data.get("languages_bonus", [])
            if bonus_langs:
                lines.append(f"\nBonus languages available to learn: {', '.join(bonus_langs)}")

        return "\n".join(lines)

    # =========================================================================
    # System 29: Swimming / Drowning (helper + hold breath command)
    # =========================================================================

    def _handle_underwater_move(self, character, new_room, result):
        """Handle underwater movement mechanics. Returns updated result string."""
        import random
        is_underwater = "underwater" in getattr(new_room, 'flags', [])

        if is_underwater:
            # Initialize breath tracker
            if not hasattr(character, '_breath') or character._breath is None:
                character._breath = 10

            # Swim check DC 10
            swim_result = character.skill_check("Swim")
            if isinstance(swim_result, str) or swim_result < 10:
                damage = random.randint(1, 6)
                character.hp -= damage
                result += f"\nYou struggle in the water! ({damage} damage)"
            else:
                result += "\nYou swim through the water."

            # Decrement breath
            character._breath -= 1
            if character._breath <= 0:
                character._breath = 0
                damage = random.randint(1, 6)
                character.hp -= damage
                result += f"\nYou are drowning! ({damage} damage)"
            else:
                result += f"\n[Breath: {character._breath} rounds remaining]"
        else:
            # Left underwater — reset breath
            if getattr(character, '_breath', None) is not None and character._breath < 10:
                character._breath = None
                result += "\nYou surface and gasp for air!"

        return result

    def cmd_hold_breath(self, character, args):
        """Extend your breath underwater with a Constitution check.
        Usage: holdbreath
        """
        import random
        if not hasattr(character, '_breath') or character._breath is None:
            return "You are not underwater."

        con_mod = (character.con_score - 10) // 2
        roll = random.randint(1, 20)
        total = roll + con_mod
        dc = 15

        if total >= dc:
            character._breath += 2
            return (f"You control your breathing. (CON check: {total} vs DC {dc})\n"
                    f"Breath extended by 2 rounds. [{character._breath} rounds remaining]")
        else:
            return (f"You fail to control your breathing. (CON check: {total} vs DC {dc})\n"
                    f"[Breath: {character._breath} rounds remaining]")

    # =========================================================================
    # System 30: Flying
    # =========================================================================

    def cmd_fly(self, character, args):
        """Take to the air if you have a fly ability.
        Usage: fly
        Requires a fly spell buff, racial fly ability, or flying item.
        """
        if getattr(character, 'flying', False):
            return "You are already flying."

        # Check for fly ability: spell buff, racial, or item
        has_fly = False

        # Check active buffs for a fly spell
        active_buffs = getattr(character, 'active_buffs', {})
        if any('fly' in str(k).lower() for k in active_buffs):
            has_fly = True

        # Check racial fly ability
        from src.races import get_race
        race_data = get_race(character.race or "")
        if race_data:
            for special in race_data.get("special", []):
                if 'fly' in special.lower():
                    has_fly = True
                    break

        # Check equipped items for fly ability
        for slot, item in character.equipment.items():
            if item:
                bonuses = getattr(item, 'stat_bonuses', {})
                if 'fly' in bonuses or 'flying' in bonuses:
                    has_fly = True
                    break
                item_name = getattr(item, 'name', '').lower()
                if 'wings' in item_name or 'fly' in item_name:
                    has_fly = True
                    break

        if not has_fly:
            return ("You do not have the ability to fly. You need a fly spell, "
                    "racial fly ability, or a flying item.")

        character.flying = True
        return "You take to the air!"

    def cmd_land(self, character, args):
        """Land and stop flying.
        Usage: land
        """
        if not getattr(character, 'flying', False):
            return "You are not flying."

        character.flying = False
        return "You land gracefully."


# =========================================================================
# System 34: Item Sets data (module-level)
# =========================================================================

ITEM_SETS = {
    "Iron Warrior": {
        "items": ["Iron Longsword", "Iron Dagger", "Steel Shield"],
        "bonuses": {2: {"attack_bonus": 1}, 3: {"ac_bonus": 2, "damage_bonus": 1}}
    },
    "Leather Scout": {
        "items": ["Leather Armor", "Leather Boots", "Leather Gloves"],
        "bonuses": {2: {"move_bonus": 20}, 3: {"hide_bonus": 2, "sneak_bonus": 2}}
    }
}


# =========================================================================
# Append Systems 32-36 methods to CommandParser
# =========================================================================

def _cmd_gamble(self, character, args):
    """Dice gambling mini-game.
    Usage: gamble dice <amount>
           gamble coinflip <amount>
    Must be in a room with 'tavern' or 'casino' in its flags, name, or description.
    """
    import random
    room = character.room
    room_flags = getattr(room, 'flags', []) if room else []
    if isinstance(room_flags, str):
        room_flags = [room_flags]
    room_flags_lower = [str(f).lower() for f in room_flags]
    room_name = getattr(room, 'name', '').lower() if room else ''
    room_desc = getattr(room, 'description', '').lower() if room else ''
    in_gambling_venue = (
        any('tavern' in f or 'casino' in f for f in room_flags_lower)
        or 'tavern' in room_name or 'casino' in room_name
        or 'tavern' in room_desc or 'casino' in room_desc
    )
    if not in_gambling_venue:
        return "You need to be in a tavern or casino to gamble."

    parts = args.strip().split()
    if len(parts) < 2:
        return ("Usage: gamble dice <amount> | gamble coinflip <amount>\n"
                "  dice: Roll 2d6. 7+ wins double, 12 wins triple, 2-6 loses.\n"
                "  coinflip: 50/50 chance to double or lose your bet.")

    subcommand = parts[0].lower()
    try:
        amount = int(parts[1])
    except ValueError:
        return "Bet amount must be a number."

    if amount <= 0:
        return "You must bet a positive amount of gold."
    if getattr(character, 'gold', 0) < amount:
        return f"You don't have enough gold. (You have {character.gold} gold)"

    if subcommand == "dice":
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        total = die1 + die2
        roll_str = f"You roll the dice: {die1} + {die2} = {total}."
        if total == 12:
            winnings = amount * 2  # net gain (triple payout = original + 2x profit)
            character.gold += winnings
            return (f"{roll_str}\nBoxcars! Triple winnings! You gain {winnings} gold. "
                    f"(Gold: {character.gold})")
        elif total >= 7:
            character.gold += amount
            return (f"{roll_str}\nYou win! You gain {amount} gold. "
                    f"(Gold: {character.gold})")
        else:
            character.gold -= amount
            return (f"{roll_str}\nYou lose your bet of {amount} gold. "
                    f"(Gold: {character.gold})")

    elif subcommand == "coinflip":
        result = random.choice(["heads", "tails"])
        player_call = "heads"  # player always calls heads
        if result == player_call:
            character.gold += amount
            return (f"The coin lands on {result}. You win! +{amount} gold. "
                    f"(Gold: {character.gold})")
        else:
            character.gold -= amount
            return (f"The coin lands on {result}. You lose! -{amount} gold. "
                    f"(Gold: {character.gold})")
    else:
        return "Unknown gambling game. Try: gamble dice <amount> or gamble coinflip <amount>"


_SPELLCASTER_CLASSES = {"Bard", "Cleric", "Druid", "Magi", "Paladin", "Ranger", "Sorcerer", "Wizard"}


def _cmd_enchant(self, character, args):
    """Enchant an item with a magical bonus.
    Usage: enchant <item> <bonus_type> <value>
    bonus_type: attack, damage, ac, stat
    Requires a spellcaster class and a Spellcraft check.
    Costs value * 1000 gold. Maximum enchantment: +5.
    """
    char_class = getattr(character, 'char_class', '')
    if char_class not in _SPELLCASTER_CLASSES:
        return "You must be a spellcaster to enchant items."

    parts = args.strip().split()
    if len(parts) < 3:
        return "Usage: enchant <item name> <bonus_type> <value>\n  bonus_type: attack, damage, ac, stat"

    try:
        value = int(parts[-1])
        bonus_type = parts[-2].lower()
        item_name = " ".join(parts[:-2])
    except (ValueError, IndexError):
        return "Usage: enchant <item name> <bonus_type> <value>"

    if value < 1 or value > 5:
        return "Enchantment bonus must be between 1 and 5."

    valid_bonus_types = {"attack", "damage", "ac", "stat"}
    if bonus_type not in valid_bonus_types:
        return f"Invalid bonus type '{bonus_type}'. Choose: attack, damage, ac, stat"

    # Find item in inventory or equipped
    item = next((i for i in character.inventory if i.name.lower() == item_name.lower()), None)
    if not item:
        for slot, eq_item in character.equipment.items():
            if eq_item and eq_item.name.lower() == item_name.lower():
                item = eq_item
                break
    if not item:
        return f"You don't have '{item_name}'."

    item_type = getattr(item, 'item_type', '').lower()
    if item_type not in ('weapon', 'armor', 'shield'):
        return f"{item.name} must be a weapon or armor to be enchanted."

    cost = value * 1000
    if getattr(character, 'gold', 0) < cost:
        return (f"Enchanting {item.name} with +{value} {bonus_type} costs {cost} gold, "
                f"but you only have {character.gold} gold.")

    # Spellcraft check: DC 15 + (value * 5)
    dc = 15 + (value * 5)
    spellcraft_result = character.skill_check("Spellcraft")
    if isinstance(spellcraft_result, str):
        return f"You cannot enchant items: {spellcraft_result}"
    if spellcraft_result < dc:
        fail_cost = cost // 2
        character.gold -= fail_cost
        return (f"Your enchantment ritual fails! Spellcraft check: {spellcraft_result} vs DC {dc}. "
                f"You lose {fail_cost} gold in wasted materials. (Gold: {character.gold})")

    character.gold -= cost
    if not hasattr(item, 'stat_bonuses') or item.stat_bonuses is None:
        item.stat_bonuses = {}

    if bonus_type == "ac":
        item.ac_bonus = getattr(item, 'ac_bonus', 0) + value
        result_desc = f"+{value} AC bonus"
    elif bonus_type == "attack":
        item.stat_bonuses['attack_bonus'] = item.stat_bonuses.get('attack_bonus', 0) + value
        result_desc = f"+{value} attack bonus"
    elif bonus_type == "damage":
        item.stat_bonuses['damage_bonus'] = item.stat_bonuses.get('damage_bonus', 0) + value
        result_desc = f"+{value} damage bonus"
    else:  # stat
        item.stat_bonuses['enhancement'] = item.stat_bonuses.get('enhancement', 0) + value
        result_desc = f"+{value} enhancement bonus to stats"

    item.magical = True
    return (f"You successfully enchant {item.name} with {result_desc}! "
            f"(Spellcraft: {spellcraft_result} vs DC {dc}, Cost: {cost} gold, "
            f"Gold remaining: {character.gold})")


def _cmd_itemsets(self, character, args):
    """Show all item sets and which pieces the character has equipped.
    Usage: itemsets
    """
    equipped_names = set()
    for slot, item in character.equipment.items():
        if item:
            equipped_names.add(item.name)
    inventory_names = {i.name for i in character.inventory}

    lines = ["Item Sets:"]
    for set_name, set_data in ITEM_SETS.items():
        set_items = set_data["items"]
        bonuses = set_data["bonuses"]
        equipped_count = sum(1 for i in set_items if i in equipped_names)
        lines.append(f"\n{set_name} ({equipped_count}/{len(set_items)} equipped):")
        for item_name in set_items:
            if item_name in equipped_names:
                lines.append(f"  [x] {item_name}")
            elif item_name in inventory_names:
                lines.append(f"  [ ] {item_name} (in inventory)")
            else:
                lines.append(f"  [ ] {item_name}")
        lines.append("  Bonuses:")
        for count, bonus_dict in sorted(bonuses.items()):
            bonus_strs = [f"+{v} {k.replace('_', ' ')}" for k, v in bonus_dict.items()]
            active = " (ACTIVE)" if equipped_count >= count else ""
            lines.append(f"    {count} pieces: {', '.join(bonus_strs)}{active}")
    return "\n".join(lines)


def _check_set_bonuses(self, character):
    """Recalculate and apply/remove set bonuses based on currently equipped items.
    Call this after equip/unequip operations.
    Returns a list of status messages about bonuses gained/lost.
    """
    equipped_names = set()
    for slot, item in character.equipment.items():
        if item:
            equipped_names.add(item.name)

    messages = []
    if not hasattr(character, '_active_set_bonuses'):
        character._active_set_bonuses = {}

    for set_name, set_data in ITEM_SETS.items():
        set_items = set_data["items"]
        bonuses = set_data["bonuses"]
        equipped_count = sum(1 for i in set_items if i in equipped_names)

        active_tier = 0
        for count in sorted(bonuses.keys()):
            if equipped_count >= count:
                active_tier = count

        prev_tier = character._active_set_bonuses.get(set_name, 0)
        if active_tier == prev_tier:
            continue

        # Remove old bonuses
        if prev_tier > 0:
            old_bonus = bonuses.get(prev_tier, {})
            for key, val in old_bonus.items():
                if key == 'ac_bonus':
                    character.ac = max(0, character.ac - val)
                elif key == 'move_bonus':
                    character.max_move = max(0, character.max_move - val)
                    character.move = min(character.move, character.max_move)
            messages.append(f"Set bonus '{set_name}' ({prev_tier}-piece) removed.")

        # Apply new bonuses
        if active_tier > 0:
            new_bonus = bonuses.get(active_tier, {})
            for key, val in new_bonus.items():
                if key == 'ac_bonus':
                    character.ac += val
                elif key == 'move_bonus':
                    character.max_move += val
            messages.append(
                f"Set bonus '{set_name}' ({active_tier}-piece) activated: "
                + ", ".join(f"+{v} {k.replace('_', ' ')}" for k, v in new_bonus.items())
            )

        character._active_set_bonuses[set_name] = active_tier

    return messages


def _cmd_reputation(self, character, args):
    """Show all faction reputations and standings.
    Usage: reputation
    """
    rep = getattr(character, 'reputation', {})
    if not rep:
        return "You have no notable reputation with any faction."

    def standing_label(value):
        if value <= -100:
            return "Hostile"
        elif value < -25:
            return "Unfriendly"
        elif value < 25:
            return "Neutral"
        elif value < 100:
            return "Friendly"
        elif value < 200:
            return "Honored"
        else:
            return "Revered"

    lines = ["Faction Reputations:"]
    for faction, value in sorted(rep.items()):
        label = standing_label(value)
        lines.append(f"  {faction}: {value:+d} ({label})")
    return "\n".join(lines)


def _apply_reputation_decay(players):
    """Decay all faction reputation values by 1 point toward 0.
    Call this every 300 seconds (5 minutes) from the game tick loop.
    Positive rep decreases by 1, negative rep increases by 1, never crosses 0.
    """
    for player in players:
        rep = getattr(player, 'reputation', {})
        for faction in list(rep.keys()):
            val = rep[faction]
            if val > 0:
                rep[faction] = val - 1
            elif val < 0:
                rep[faction] = val + 1


def _cmd_remort(self, character, args):
    """Reset character to level 1 with permanent bonuses (requires level 20).
    Usage: remort
         remort confirm  -- to proceed after seeing the warning
    """
    args = (args or "").strip().lower()

    if getattr(character, 'level', 1) < 20:
        return f"You must be level 20 to remort. (Current level: {character.level})"

    if args != "confirm":
        character.remort_pending = True
        remort_count = getattr(character, 'remort_count', 0)
        return (f"Remort will reset you to level 1 with permanent bonuses:\n"
                f"  +1 to ALL ability scores\n"
                f"  +10 permanent maximum HP\n"
                f"  Title: 'Reborn'\n"
                f"  Your skills, feats, equipment, gold, and achievements are kept.\n"
                f"  This will be your remort #{remort_count + 1}.\n"
                f"Type 'remort confirm' to proceed.")

    remort_count = getattr(character, 'remort_count', 0)

    # Reset level and XP
    character.level = 1
    character.class_level = 1
    character.xp = 0

    # Reset max HP: base for level 1 + CON mod + 10 per total remort (including this one)
    con_mod = (character.con_score - 10) // 2
    base_max_hp = 10 + con_mod
    character.max_hp = base_max_hp + ((remort_count + 1) * 10)
    character.hp = min(character.hp, character.max_hp)

    # Permanent +1 to all ability scores
    character.str_score += 1
    character.dex_score += 1
    character.con_score += 1
    character.int_score += 1
    character.wis_score += 1
    character.cha_score += 1

    # Grant "Reborn" title
    if not hasattr(character, 'titles') or character.titles is None:
        character.titles = []
    if "Reborn" not in character.titles:
        character.titles.append("Reborn")
    character.title = "Reborn"

    character.remort_count = remort_count + 1
    character.remort_pending = False

    return (f"You have been Reborn! You return to level 1 with the wisdom of your past life.\n"
            f"  All ability scores increased by 1.\n"
            f"  Maximum HP is now {character.max_hp}.\n"
            f"  Title 'Reborn' granted. Remort count: {character.remort_count}.\n"
            f"  Your skills, feats, equipment, and gold remain.")


# Bind all new methods to CommandParser
CommandParser.cmd_gamble = _cmd_gamble
CommandParser.cmd_enchant = _cmd_enchant
CommandParser.cmd_itemsets = _cmd_itemsets
CommandParser._check_set_bonuses = _check_set_bonuses
CommandParser.cmd_reputation = _cmd_reputation
CommandParser.cmd_remort = _cmd_remort
CommandParser.apply_reputation_decay = staticmethod(_apply_reputation_decay)


# =============================================================================
# System 38: Bug / Typo / Idea Commands
# =============================================================================

def _submit_feedback(self, character, feedback_type, args):
    """Shared helper for bug, typo, idea commands."""
    import os, json
    from datetime import datetime, timezone

    args = (args or "").strip()
    if not args:
        return "Usage: %s <description>" % feedback_type

    feedback_path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'feedback.json'
    )

    # Load existing entries
    try:
        with open(feedback_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        if not isinstance(entries, list):
            entries = []
    except (FileNotFoundError, json.JSONDecodeError):
        entries = []

    entry = {
        "type": feedback_type,
        "reporter": character.name,
        "room": character.room.vnum if character.room else None,
        "text": args,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)

    # Atomic write
    tmp_path = feedback_path + ".tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2)
    os.replace(tmp_path, feedback_path)

    labels = {"bug": "Bug report", "typo": "Typo report", "idea": "Idea"}
    label = labels.get(feedback_type, "Feedback")
    return "%s submitted. Thank you!" % label


def cmd_bug(self, character, args):
    """Report a bug. Usage: bug <description>"""
    return self._submit_feedback(character, "bug", args)


def cmd_typo(self, character, args):
    """Report a typo. Usage: typo <description>"""
    return self._submit_feedback(character, "typo", args)


def cmd_idea(self, character, args):
    """Submit an idea or suggestion. Usage: idea <description>"""
    return self._submit_feedback(character, "idea", args)


CommandParser._submit_feedback = _submit_feedback
CommandParser.cmd_bug = cmd_bug
CommandParser.cmd_typo = cmd_typo
CommandParser.cmd_idea = cmd_idea


# =============================================================================
# System 39: Ignore / Block
# =============================================================================

def cmd_ignore(self, character, args):
    """Manage your ignore list.
    Usage: ignore            - list ignored players
           ignore <name>     - toggle ignore on/off for <name>
    """
    if not hasattr(character, 'ignored_players'):
        character.ignored_players = []

    args = (args or "").strip()

    if not args:
        if not character.ignored_players:
            return "Your ignore list is empty."
        lines = ["Players you are ignoring:"]
        for name in character.ignored_players:
            lines.append("  %s" % name)
        return "\n".join(lines)

    target_name = args.split()[0]

    # Toggle: if already ignored, remove; otherwise add
    lower_list = [n.lower() for n in character.ignored_players]
    if target_name.lower() in lower_list:
        character.ignored_players = [
            n for n in character.ignored_players
            if n.lower() != target_name.lower()
        ]
        return "%s has been removed from your ignore list." % target_name
    else:
        character.ignored_players.append(target_name)
        return "%s has been added to your ignore list." % target_name


CommandParser.cmd_ignore = cmd_ignore


# =============================================================================
# System 40: AFK Status
# =============================================================================

def cmd_afk(self, character, args):
    """Toggle AFK status.
    Usage: afk              - toggle AFK on/off
           afk <message>   - go AFK with a custom message
    """
    if not hasattr(character, 'afk'):
        character.afk = False
    if not hasattr(character, 'afk_message'):
        character.afk_message = ""

    args = (args or "").strip()

    if character.afk:
        # Turn AFK off
        character.afk = False
        character.afk_message = ""
        return "You are no longer AFK."
    else:
        # Turn AFK on
        character.afk = True
        character.afk_message = args
        if args:
            return "You are now AFK. (%s)" % args
        return "You are now AFK."


CommandParser.cmd_afk = cmd_afk


# =============================================================================
# System 41: Finger / Whois
# =============================================================================

def cmd_finger(self, character, args):
    """Show information about a player.
    Usage: finger <player name>
    """
    import os, json

    args = (args or "").strip()
    if not args:
        return "Finger whom? Usage: finger <player name>"

    target_name = args.split()[0]

    # Try to find the player online first
    target = None
    if self.world and hasattr(self.world, 'players'):
        for p in self.world.players:
            if p.name.lower() == target_name.lower():
                target = p
                break

    if target:
        room_name = target.room.name if target.room else "Unknown"
        room_vnum = target.room.vnum if target.room else "?"
        lines = [
            "[ Online ]  %s" % target.name,
            "  Race    : %s" % getattr(target, 'race', 'Unknown'),
            "  Class   : %s" % getattr(target, 'char_class', 'Unknown'),
            "  Level   : %s" % target.level,
            "  Title   : %s" % (getattr(target, 'title', '') or '(none)'),
            "  Guild   : %s" % (getattr(target, 'guild_name', None) or '(none)'),
            "  Location: %s (#%s)" % (room_name, room_vnum),
        ]
        if getattr(target, 'afk', False):
            afk_msg = getattr(target, 'afk_message', '')
            lines.append("  AFK     : %s" % (afk_msg or 'Yes'))
        return "\n".join(lines)

    # Try loading from player file
    player_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'players')
    filename = os.path.join(player_dir, "%s.json" % target_name.lower())
    if not os.path.exists(filename):
        return "No player named '%s' found." % target_name

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return "Could not load data for '%s'." % target_name

    lines = [
        "[ Offline ] %s" % data.get('name', target_name),
        "  Race    : %s" % data.get('race', 'Unknown'),
        "  Class   : %s" % data.get('char_class', 'Unknown'),
        "  Level   : %s" % data.get('level', '?'),
        "  Title   : %s" % (data.get('title', None) or '(none)'),
        "  Guild   : %s" % (data.get('guild_name', None) or '(none)'),
        "  Last seen: (offline)",
    ]
    return "\n".join(lines)


CommandParser.cmd_finger = cmd_finger


# =============================================================================
# System 42: Duel System
# =============================================================================

def cmd_duel(self, character, args):
    """Challenge another player to a duel, or accept/decline a challenge.
    Usage: duel <player>     - challenge a player in the room
           duel accept       - accept a pending duel challenge
           duel decline      - decline a pending duel challenge
    """
    from src.combat import start_combat

    args = (args or "").strip().lower()

    if not args:
        return "Usage: duel <player> | duel accept | duel decline"

    # Accept a challenge
    if args == "accept":
        challenger_name = getattr(character, '_duel_challenger', None)
        if not challenger_name:
            return "You have no pending duel challenge."

        # Find the challenger in the room
        challenger = None
        if character.room:
            for p in character.room.players:
                if p.name.lower() == challenger_name.lower():
                    challenger = p
                    break

        if not challenger:
            character._duel_challenger = None
            return "%s is no longer here." % challenger_name

        # Start the duel
        character._in_duel = True
        challenger._in_duel = True
        character._duel_challenger = None

        from src.chat import broadcast_to_room
        start_combat(character.room, challenger, character)
        challenger.combat_target = character
        character.combat_target = challenger

        room_msg = "%s and %s square off in a duel!" % (challenger.name, character.name)
        broadcast_to_room(character.room, room_msg, exclude=None)
        return "You accept %s's duel challenge! En garde!" % challenger.name

    # Decline a challenge
    if args == "decline":
        challenger_name = getattr(character, '_duel_challenger', None)
        if not challenger_name:
            return "You have no pending duel challenge."
        character._duel_challenger = None

        if self.world and hasattr(self.world, 'players'):
            from src.chat import send_to_player
            for p in self.world.players:
                if p.name.lower() == challenger_name.lower():
                    send_to_player(
                        p,
                        "%s has declined your duel challenge." % character.name
                    )
                    break
        return "You decline the duel challenge from %s." % challenger_name

    # Challenge another player
    target_name = args
    if not character.room:
        return "You must be in a room to issue a duel challenge."

    target = None
    for p in character.room.players:
        if p.name.lower() == target_name and p != character:
            target = p
            break

    if not target:
        return "%s is not in the room." % args.capitalize()

    if getattr(target, '_in_duel', False):
        return "%s is already in a duel." % target.name

    # Store pending challenge on target
    target._duel_challenger = character.name

    from src.chat import send_to_player
    send_to_player(
        target,
        "%s challenges you to a duel! "
        "Type 'duel accept' to accept or 'duel decline' to refuse." % character.name
    )
    return "You challenge %s to a duel!" % target.name


CommandParser.cmd_duel = cmd_duel


# =============================================================================
# System 43: Leaderboards
# =============================================================================

def cmd_leaderboard(self, character, args):
    """Show the top 10 players by various criteria.
    Usage: leaderboard [level|xp|kills|gold]
    Default: sort by level.
    """
    import os, json

    args = (args or "").strip().lower()
    criteria = args if args in ("level", "xp", "kills", "gold") else "level"

    player_dir = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'players'
    )
    if not os.path.isdir(player_dir):
        return "No player data found."

    records = []
    for filename in os.listdir(player_dir):
        if not filename.endswith('.json') or '.bak.' in filename:
            continue
        filepath = os.path.join(player_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            records.append({
                "name": data.get("name", filename),
                "level": data.get("level", 1),
                "char_class": data.get("char_class", "Unknown"),
                "xp": data.get("xp", 0),
                "kills": data.get("kill_count", 0),
                "gold": data.get("gold", 0),
            })
        except Exception:
            continue

    if not records:
        return "No players found."

    key_map = {
        "level": "level",
        "xp": "xp",
        "kills": "kills",
        "gold": "gold",
    }
    sort_key = key_map[criteria]
    records.sort(key=lambda r: r[sort_key], reverse=True)
    top = records[:10]

    label_map = {
        "level": "Level",
        "xp": "Experience",
        "kills": "Kills",
        "gold": "Gold",
    }
    header = "Top Players by %s:" % label_map[criteria]
    lines = [header, "-" * 40]
    for rank, rec in enumerate(top, 1):
        value = rec[sort_key]
        lines.append(
            "#%-3d %-16s - Level %d (%s) | %s: %s"
            % (rank, rec['name'], rec['level'], rec['char_class'],
               label_map[criteria], value)
        )
    return "\n".join(lines)


CommandParser.cmd_leaderboard = cmd_leaderboard


# =============================================================================
# Class Ability Commands
# =============================================================================

def cmd_rage(self, character, args):
    """Barbarian Rage: enter a battle rage granting STR/CON bonuses.
    Usage: rage
    """
    import random as _rng
    if character.char_class != "Barbarian":
        return "Only Barbarians can rage."
    if character.has_condition('fatigued') or character.has_condition('exhausted'):
        return "You are too fatigued to rage."
    if character.has_condition('raging'):
        return "You are already raging!"

    # Calculate uses per day: 1 + 1 per 4 levels above 1st
    max_uses = 1 + max(0, (character.class_level - 1) // 4)
    if not hasattr(character, '_rage_uses'):
        character._rage_uses = 0
    if character._rage_uses >= max_uses:
        return f"You have no rage uses remaining today (used {character._rage_uses}/{max_uses})."

    con_mod = (character.con_score - 10) // 2
    duration = 3 + con_mod

    # Apply bonuses
    if not hasattr(character, 'temp_str_bonus'):
        character.temp_str_bonus = 0
    if not hasattr(character, 'temp_con_bonus'):
        character.temp_con_bonus = 0
    if not hasattr(character, 'temp_ac_bonus'):
        character.temp_ac_bonus = 0
    if not hasattr(character, 'temp_save_bonus'):
        character.temp_save_bonus = 0

    character.temp_str_bonus = getattr(character, 'temp_str_bonus', 0) + 4
    character.temp_con_bonus = getattr(character, 'temp_con_bonus', 0) + 4
    character.temp_ac_bonus = getattr(character, 'temp_ac_bonus', 0) - 2
    character.temp_save_bonus = getattr(character, 'temp_save_bonus', 0) + 2  # Will saves

    character.add_timed_condition('raging', duration)
    character._rage_uses += 1
    character._rage_duration = duration  # remember for fatigue

    return (f"You fly into a RAGE! (+4 STR, +4 CON, +2 Will saves, -2 AC)\n"
            f"Rage lasts {duration} rounds. ({character._rage_uses}/{max_uses} uses today)")


CommandParser.cmd_rage = cmd_rage


def cmd_inspire(self, character, args):
    """Bard Inspire Courage: inspire allies in the room.
    Usage: inspire
    """
    if character.char_class != "Bard":
        return "Only Bards can use Inspire Courage."

    max_uses = max(1, character.class_level // 2)
    if not hasattr(character, '_inspire_uses'):
        character._inspire_uses = 0
    if character._inspire_uses >= max_uses:
        return f"No Inspire Courage uses remaining today ({character._inspire_uses}/{max_uses})."

    cha_mod = (character.cha_score - 10) // 2
    duration = 5 + cha_mod

    # Determine bonus based on Bard level
    bonus = 1
    if character.class_level >= 14:
        bonus = 3
    elif character.class_level >= 8:
        bonus = 2

    # Apply buff to self and all allies in room
    affected = []
    targets = list(getattr(character.room, 'players', []))
    for ally in targets:
        if not hasattr(ally, 'active_buffs'):
            ally.active_buffs = {}
        ally.active_buffs['inspire_attack'] = bonus
        ally.active_buffs['inspire_damage'] = bonus
        ally.add_timed_condition('inspired', duration)
        affected.append(ally.name)

    character._inspire_uses += 1

    names = ", ".join(affected) if affected else "no one"
    return (f"You begin a rousing performance! All allies gain +{bonus} to attack and damage.\n"
            f"Affects: {names} for {duration} rounds. ({character._inspire_uses}/{max_uses} uses today)")


CommandParser.cmd_inspire = cmd_inspire


def cmd_turn(self, character, args):
    """Cleric Turn Undead: attempt to turn or destroy undead in the room.
    Usage: turn  or  turnundead
    """
    import random as _rng
    if character.char_class != "Cleric":
        return "Only Clerics can turn undead."

    cha_mod = (character.cha_score - 10) // 2
    max_uses = 3 + cha_mod
    if max_uses < 1:
        max_uses = 1
    if not hasattr(character, '_turn_uses'):
        character._turn_uses = 0
    if character._turn_uses >= max_uses:
        return f"No Turn Undead uses remaining today ({character._turn_uses}/{max_uses})."

    # Find undead in room
    undead = [m for m in character.room.mobs
              if m.alive and 'undead' in getattr(m, 'type_', '').lower()]
    if not undead:
        return "There are no undead here to turn."

    # Turning check: d20 + CHA mod determines max HD affected
    turning_check = _rng.randint(1, 20) + cha_mod
    # Turning damage: 2d6 + cleric level + CHA mod = total HD turned
    turning_damage = sum(_rng.randint(1, 6) for _ in range(2)) + character.class_level + cha_mod

    character._turn_uses += 1
    results = [f"You brandish your holy symbol! (Turn check: {turning_check}, HD pool: {turning_damage})"]

    hd_spent = 0
    for mob in undead:
        mob_hd = getattr(mob, 'hd', getattr(mob, 'level', 1))
        if hd_spent + mob_hd > turning_damage:
            break
        if mob_hd > turning_check:
            results.append(f"{mob.name} resists the turning!")
            continue
        hd_spent += mob_hd
        # Destroy if cleric level >= mob HD + 4
        if character.class_level >= mob_hd + 4:
            mob.hp = 0
            mob.alive = False
            results.append(f"{mob.name} is DESTROYED by your holy power!")
        else:
            mob.add_timed_condition('frightened', 10)
            results.append(f"{mob.name} is turned and flees in terror!")

    results.append(f"({character._turn_uses}/{max_uses} uses today)")
    return "\n".join(results)


CommandParser.cmd_turn = cmd_turn


def cmd_wildshape(self, character, args):
    """Druid Wild Shape: transform into an animal form.
    Usage: wildshape <wolf|bear|eagle>  or  wildshape revert
    """
    if character.char_class != "Druid":
        return "Only Druids can use Wild Shape."
    if character.class_level < 5:
        return "You must be at least level 5 to use Wild Shape."

    max_uses = 1 + character.class_level // 4
    if not hasattr(character, '_wildshape_uses'):
        character._wildshape_uses = 0

    args = (args or "").strip().lower()

    # Revert
    if args == "revert":
        if not character.has_condition('wildshaped'):
            return "You are not in a wild shape form."
        original = getattr(character, '_original_stats', None)
        if original:
            character.str_score = original['str']
            character.dex_score = original['dex']
            character.con_score = original['con']
            character._original_stats = None
        character.remove_condition('wildshaped')
        character._wildshape_form = None
        return "You revert to your natural form."

    if character.has_condition('wildshaped'):
        form = getattr(character, '_wildshape_form', 'an animal')
        return f"You are already in {form} form. Use 'wildshape revert' first."

    if character._wildshape_uses >= max_uses:
        return f"No Wild Shape uses remaining today ({character._wildshape_uses}/{max_uses})."

    FORMS = {
        "wolf":  {"str": +0, "dex": +2, "con": +0, "desc": "a swift wolf",   "note": "speed bonus, bite 1d6+STR"},
        "bear":  {"str": +4, "dex": -2, "con": +2, "desc": "a powerful bear","note": "claw 1d8+STR"},
        "eagle": {"str": -2, "dex": +4, "con": +0, "desc": "a keen eagle",   "note": "fly ability, talons 1d4+DEX"},
    }

    if args not in FORMS:
        form_list = ", ".join(FORMS.keys())
        return f"Unknown form. Choose: {form_list}\nOr 'wildshape revert' to return to normal."

    form = FORMS[args]
    # Save original stats
    character._original_stats = {
        'str': character.str_score,
        'dex': character.dex_score,
        'con': character.con_score,
    }
    # Apply stat changes
    character.str_score += form['str']
    character.dex_score += form['dex']
    character.con_score += form['con']
    character.add_timed_condition('wildshaped', 9999)  # effectively permanent until reverted
    character._wildshape_form = form['desc']
    character._wildshape_uses += 1

    return (f"You transform into {form['desc']}! ({form['note']})\n"
            f"STR {form['str']:+d}, DEX {form['dex']:+d}, CON {form['con']:+d}. "
            f"Use 'wildshape revert' to return. ({character._wildshape_uses}/{max_uses} uses today)")


CommandParser.cmd_wildshape = cmd_wildshape


def cmd_flurry(self, character, args):
    """Monk Flurry of Blows: make an extra attack this round at -2 to all attacks.
    Usage: flurry
    Must be in combat. Activates on your next attack.
    """
    if character.char_class != "Monk":
        return "Only Monks can use Flurry of Blows."
    if character.state.name != "COMBAT":
        return "You must be in combat to use Flurry of Blows."
    if not character.combat_target:
        return "You have no combat target."
    if getattr(character, '_flurry_active', False):
        return "Flurry of Blows is already active."

    character._flurry_active = True
    return "You prepare a Flurry of Blows! (-2 to all attacks, +1 extra attack this round.)"


CommandParser.cmd_flurry = cmd_flurry


def cmd_smite(self, character, args):
    """Paladin Smite Evil: smite an evil target (+CHA to attack, +level to damage).
    Usage: smite
    Must be in combat with a target of evil alignment.
    """
    if character.char_class != "Paladin":
        return "Only Paladins can smite evil."
    if character.state.name != "COMBAT" or not character.combat_target:
        return "You must be in combat to smite."

    # Check daily uses: 1 + 1 per 5 levels
    max_uses = 1 + character.class_level // 5
    if not hasattr(character, '_smite_uses'):
        character._smite_uses = 0
    if character._smite_uses >= max_uses:
        return f"No Smite Evil uses remaining today ({character._smite_uses}/{max_uses})."

    target = character.combat_target
    target_alignment = getattr(target, 'alignment', '') or ''
    if 'evil' not in target_alignment.lower():
        # Wasted use per D&D 3.5 rules
        character._smite_uses += 1
        return (f"{target.name} does not appear to be evil — smite wasted! "
                f"({character._smite_uses}/{max_uses} uses today)")

    if getattr(character, '_smite_active', False):
        return "Smite Evil is already active for your next attack."

    cha_mod = (character.cha_score - 10) // 2
    character._smite_active = True
    character._smite_uses += 1
    return (f"You call upon divine power to smite {target.name}! "
            f"(+{cha_mod} attack, +{character.class_level} damage on next hit)\n"
            f"({character._smite_uses}/{max_uses} uses today)")


CommandParser.cmd_smite = cmd_smite


def cmd_layonhands(self, character, args):
    """Paladin Lay on Hands: heal yourself or an ally.
    Usage: layonhands         - heals self
           layonhands <name>  - heals target ally in room
    Heals Paladin level x CHA modifier HP per day (pool).
    """
    if character.char_class != "Paladin":
        return "Only Paladins can use Lay on Hands."

    cha_mod = max(1, (character.cha_score - 10) // 2)
    max_pool = character.class_level * cha_mod
    if not hasattr(character, '_lay_on_hands_pool'):
        character._lay_on_hands_pool = 0

    # Determine target
    args = (args or "").strip()
    if not args or args.lower() in ("self", character.name.lower()):
        target = character
    else:
        target = None
        for p in character.room.players:
            if p.name.lower() == args.lower() and p != character:
                target = p
                break
        if not target:
            return f"You don't see '{args}' here to heal."

    # Calculate heal amount (remaining pool)
    used = character._lay_on_hands_pool
    remaining = max_pool - used
    if remaining <= 0:
        return f"Your Lay on Hands pool is exhausted for today ({used}/{max_pool} HP used)."

    heal_amount = min(remaining, target.max_hp - target.hp)
    if heal_amount <= 0:
        return f"{target.name} is already at full health."

    target.hp = min(target.max_hp, target.hp + heal_amount)
    character._lay_on_hands_pool += heal_amount

    used_after = character._lay_on_hands_pool
    if target == character:
        return (f"You channel divine energy to heal yourself for {heal_amount} HP! "
                f"({target.hp}/{target.max_hp} HP)\n"
                f"Pool: {used_after}/{max_pool} HP used today.")
    else:
        return (f"You channel divine energy into {target.name}, healing {heal_amount} HP! "
                f"({target.hp}/{target.max_hp} HP)\n"
                f"Pool: {used_after}/{max_pool} HP used today.")


CommandParser.cmd_layonhands = cmd_layonhands


def cmd_favoredenemy(self, character, args):
    """Ranger Favored Enemy: list or set favored enemy types.
    Usage: favoredenemy           - list current favored enemies
           favoredenemy <type>    - add a favored enemy type
    Ranger gains a favored enemy at levels 1, 5, 10, 15, 20.
    Grants +2 damage vs that creature type.
    """
    if character.char_class != "Ranger":
        return "Only Rangers can have favored enemies."

    if not hasattr(character, 'favored_enemies'):
        character.favored_enemies = []

    # Max number of favored enemies based on level
    max_fe = 1
    for threshold in (5, 10, 15, 20):
        if character.class_level >= threshold:
            max_fe += 1

    args = (args or "").strip()
    if not args:
        if not character.favored_enemies:
            return (f"You have no favored enemies yet.\n"
                    f"You may have up to {max_fe} favored {'enemy' if max_fe == 1 else 'enemies'} at your level.")
        fe_list = "\n".join(f"  - {fe}" for fe in character.favored_enemies)
        return (f"Your favored enemies ({len(character.favored_enemies)}/{max_fe}):\n{fe_list}\n"
                f"(+2 damage against each type)")

    # Add a favored enemy
    if len(character.favored_enemies) >= max_fe:
        return (f"You already have the maximum number of favored enemies ({max_fe}) "
                f"for your level ({character.class_level}).")

    enemy_type = args.strip().title()
    if enemy_type.lower() in [fe.lower() for fe in character.favored_enemies]:
        return f"{enemy_type} is already one of your favored enemies."

    character.favored_enemies.append(enemy_type)
    return (f"You designate {enemy_type} as a favored enemy! "
            f"(+2 damage vs {enemy_type}) "
            f"[{len(character.favored_enemies)}/{max_fe}]")


CommandParser.cmd_favoredenemy = cmd_favoredenemy


# =========================================================================
# Fix 4: Examine command
# =========================================================================

def cmd_examine(self, character, args):
    """Examine something in detail: a mob, item, or piece of equipment.
    Usage: examine <target>
    """
    if not args:
        return "Examine what?"

    target_name = args.strip().lower()
    lines = []

    # Check mobs in room
    for mob in getattr(character.room, 'mobs', []):
        if getattr(mob, 'alive', True) and target_name in mob.name.lower():
            lines.append(f"=== {mob.name} ===")
            lines.append(mob.description or "You see nothing special.")
            lines.append(f"Level: {mob.level}")
            # HP status
            hp_pct = mob.hp / max(mob.max_hp, 1)
            if hp_pct >= 0.75:
                hp_status = "healthy"
            elif hp_pct >= 0.5:
                hp_status = "injured"
            elif hp_pct >= 0.25:
                hp_status = "badly wounded"
            else:
                hp_status = "near death"
            lines.append(f"Condition: {hp_status}")
            # Equipment (mob attacks as proxy)
            if mob.attacks:
                lines.append("Attacks:")
                for atk in mob.attacks:
                    lines.append(f"  {atk.get('type', 'attack')} +{atk.get('bonus', 0)} ({atk.get('damage', '?')})")
            return "\n".join(lines)

    # Check inventory
    for item in character.inventory:
        if target_name in item.name.lower():
            return _format_item_examine(item)

    # Check room items
    for item in getattr(character.room, 'items', []):
        if target_name in item.name.lower():
            return _format_item_examine(item)

    # Check equipment
    for slot, item in getattr(character, 'equipment', {}).items():
        if item and target_name in item.name.lower():
            return _format_item_examine(item, equipped_slot=slot)

    return f"You don't see '{args}' here."


def _format_item_examine(item, equipped_slot=None):
    """Format detailed item examination output."""
    lines = [f"=== {item.name} ==="]
    if item.description:
        lines.append(item.description)
    lines.append(f"Type: {item.item_type}")
    lines.append(f"Weight: {item.weight} lbs")
    lines.append(f"Value: {item.value} gp")
    if item.damage:
        d = item.damage
        lines.append(f"Damage: {d[0]}d{d[1]}{'+' + str(d[2]) if d[2] else ''}")
    if item.ac_bonus:
        lines.append(f"AC Bonus: +{item.ac_bonus}")
    if item.magical:
        lines.append("This item is magical.")
    if item.properties:
        lines.append(f"Properties: {', '.join(item.properties)}")
    if item.stat_bonuses:
        bonus_parts = [f"+{v} {k}" for k, v in item.stat_bonuses.items()]
        lines.append(f"Stat Bonuses: {', '.join(bonus_parts)}")
    if item.material:
        lines.append(f"Material: {item.material}")
    if equipped_slot:
        lines.append(f"(Equipped: {equipped_slot})")
    return "\n".join(lines)


CommandParser.cmd_examine = cmd_examine


# =========================================================================
# Fix 5: Affects command
# =========================================================================

def cmd_affects(self, character, args):
    """Show all active conditions, buffs, and equipment bonuses.
    Usage: affects
    """
    lines = []

    # Active conditions with duration
    cond_lines = []
    all_conditions = getattr(character, 'conditions', set()) | set(getattr(character, 'active_conditions', {}).keys())
    for cond_name in sorted(all_conditions):
        duration = character.active_conditions.get(cond_name)
        if duration:
            cond_lines.append(f"  {cond_name.title()} ({duration} rounds remaining)")
        else:
            cond_lines.append(f"  {cond_name.title()}")
    if cond_lines:
        lines.append("Active Conditions:")
        lines.extend(cond_lines)
    else:
        lines.append("Active Conditions: None")

    # Active buffs with duration
    buff_lines = []
    active_buffs = getattr(character, 'active_buffs', {})
    for buff_name, buff_data in active_buffs.items():
        if isinstance(buff_data, dict):
            dur = buff_data.get('duration', '?')
            effect = buff_data.get('effect', '')
            buff_lines.append(f"  {buff_name}: {effect} ({dur} rounds remaining)")
        else:
            buff_lines.append(f"  {buff_name}: {buff_data} rounds remaining")
    if buff_lines:
        lines.append("Active Buffs:")
        lines.extend(buff_lines)
    else:
        lines.append("Active Buffs: None")

    # Equipment stat bonuses
    eq_lines = []
    _bonus_names = {
        'temp_str_bonus': 'STR', 'temp_dex_bonus': 'DEX', 'temp_con_bonus': 'CON',
        'temp_attack_bonus': 'Attack', 'temp_save_bonus': 'Save', 'temp_ac_bonus': 'AC',
    }
    for attr, label in _bonus_names.items():
        val = getattr(character, attr, 0)
        if val != 0:
            # Find which equipment provides this
            source = "equipment"
            for slot, item in getattr(character, 'equipment', {}).items():
                if item:
                    bonuses = getattr(item, 'stat_bonuses', {})
                    for k, v in bonuses.items():
                        if k.lower() in attr.lower() and v != 0:
                            source = f"from {item.name}"
                            break
            eq_lines.append(f"  {'+' if val > 0 else ''}{val} {label} ({source})")
    if eq_lines:
        lines.append("Equipment Bonuses:")
        lines.extend(eq_lines)
    else:
        lines.append("Equipment Bonuses: None")

    return "\n".join(lines)


CommandParser.cmd_affects = cmd_affects


# =========================================================================
# Fix 6: Compare command
# =========================================================================

def cmd_compare(self, character, args):
    """Compare two items in your inventory.
    Usage: compare <item1> <item2>
    """
    if not args:
        return "Compare what? Usage: compare <item1> <item2>"

    parts = args.strip().split()
    if len(parts) < 2:
        return "Compare what with what? Usage: compare <item1> <item2>"

    name1 = parts[0].lower()
    name2 = parts[1].lower()

    item1 = next((i for i in character.inventory if name1 in i.name.lower()), None)
    item2 = next((i for i in character.inventory if name2 in i.name.lower() and i != item1), None)

    if not item1:
        return f"You don't have '{parts[0]}' in your inventory."
    if not item2:
        return f"You don't have '{parts[1]}' in your inventory."

    lines = [f"Comparing: {item1.name} vs {item2.name}", "-" * 40]
    lines.append(f"{'':15} {'Item 1':>12} {'Item 2':>12}")
    lines.append(f"{'Type:':<15} {item1.item_type:>12} {item2.item_type:>12}")
    lines.append(f"{'Weight:':<15} {item1.weight:>12} {item2.weight:>12}")
    lines.append(f"{'Value:':<15} {item1.value:>12} {item2.value:>12}")

    # Damage comparison (weapons)
    if item1.damage or item2.damage:
        d1 = f"{item1.damage[0]}d{item1.damage[1]}+{item1.damage[2]}" if item1.damage else "N/A"
        d2 = f"{item2.damage[0]}d{item2.damage[1]}+{item2.damage[2]}" if item2.damage else "N/A"
        marker = ""
        if item1.damage and item2.damage:
            avg1 = item1.damage[0] * (item1.damage[1] + 1) / 2 + item1.damage[2]
            avg2 = item2.damage[0] * (item2.damage[1] + 1) / 2 + item2.damage[2]
            if avg1 > avg2:
                marker = " <-- better"
            elif avg2 > avg1:
                marker = "             <-- better"
        lines.append(f"{'Damage:':<15} {d1:>12} {d2:>12}{marker}")

    # AC comparison (armor)
    if item1.ac_bonus or item2.ac_bonus:
        ac1 = item1.ac_bonus or 0
        ac2 = item2.ac_bonus or 0
        marker = ""
        if ac1 > ac2:
            marker = " <-- better"
        elif ac2 > ac1:
            marker = "             <-- better"
        lines.append(f"{'AC Bonus:':<15} {'+' + str(ac1):>12} {'+' + str(ac2):>12}{marker}")

    # Stat bonuses
    all_stats = set(list(item1.stat_bonuses.keys()) + list(item2.stat_bonuses.keys()))
    for stat in sorted(all_stats):
        v1 = item1.stat_bonuses.get(stat, 0)
        v2 = item2.stat_bonuses.get(stat, 0)
        lines.append(f"  {stat + ':':<13} {'+' + str(v1):>12} {'+' + str(v2):>12}")

    return "\n".join(lines)


CommandParser.cmd_compare = cmd_compare


# =========================================================================
# Fix 7: Worth command
# =========================================================================

def cmd_worth(self, character, args):
    """Show your financial status.
    Usage: worth
    """
    gold = getattr(character, 'gold', 0)
    bank = getattr(character, 'bank_gold', 0)
    inv_value = sum(getattr(item, 'value', 0) for item in character.inventory)
    total = gold + bank + inv_value

    lines = [
        f"You are carrying {gold} gold pieces.",
        f"You have {bank} gold in the bank.",
        f"Inventory value: {inv_value} gold.",
        f"Total wealth: {total} gold.",
    ]
    return "\n".join(lines)


CommandParser.cmd_worth = cmd_worth


# =========================================================================
# Fix 8: Body position commands (sit/stand/kneel)
# =========================================================================

def cmd_sit(self, character, args):
    """Sit down.
    Usage: sit
    """
    pos = getattr(character, 'position', 'standing')
    if pos == 'sitting':
        return "You are already sitting."
    if pos != 'standing':
        return f"You need to stand up first! (You are {pos}.)"
    character.position = 'sitting'
    return "You sit down."


def cmd_stand(self, character, args):
    """Stand up.
    Usage: stand
    """
    pos = getattr(character, 'position', 'standing')
    if pos == 'standing':
        return "You are already standing."
    character.position = 'standing'
    return "You stand up."


def cmd_kneel(self, character, args):
    """Kneel down.
    Usage: kneel
    """
    pos = getattr(character, 'position', 'standing')
    if pos == 'kneeling':
        return "You are already kneeling."
    if pos != 'standing':
        return f"You need to stand up first! (You are {pos}.)"
    character.position = 'kneeling'
    return "You kneel."


CommandParser.cmd_sit = cmd_sit
CommandParser.cmd_stand = cmd_stand
CommandParser.cmd_kneel = cmd_kneel


# =========================================================================
# Fix 9: Wake command
# =========================================================================

def cmd_wake(self, character, args):
    """Wake up and stand.
    Usage: wake
    """
    pos = getattr(character, 'position', 'standing')
    if pos == 'standing':
        return "You are already awake."
    if pos in ('sleeping', 'resting'):
        character.position = 'standing'
        return "You wake and stand up."
    # For other positions (sitting, kneeling), also stand
    character.position = 'standing'
    return "You stand up."


CommandParser.cmd_wake = cmd_wake


# =========================================================================
# Fix 10: Autosac toggle
# =========================================================================

def cmd_autosac(self, character, args):
    """Toggle auto-sacrifice of empty corpses after looting.
    Usage: autosac
    """
    character.auto_sac = not getattr(character, 'auto_sac', False)
    state = "enabled" if character.auto_sac else "disabled"
    return f"Auto-sacrifice {state}."


CommandParser.cmd_autosac = cmd_autosac


# =========================================================================
# Fix 11: Player title command
# =========================================================================

def cmd_title(self, character, args):
    """Set your character's title.
    Usage: title <new title>
           title clear
    Max 40 characters, alphanumeric and spaces only.
    """
    import re
    if not args:
        current = getattr(character, 'title', None)
        if current:
            return f"Your current title is: {current}"
        return "You have no title set. Usage: title <new title>"

    if args.strip().lower() == "clear":
        character.title = None
        return "Your title has been cleared."

    new_title = args.strip()
    if len(new_title) > 40:
        return "Title must be 40 characters or less."
    if not re.match(r'^[a-zA-Z0-9 ]+$', new_title):
        return "Title may only contain letters, numbers, and spaces."

    character.title = new_title
    return f"Your title is now: {new_title}"


CommandParser.cmd_title = cmd_title
