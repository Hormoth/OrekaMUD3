"""Categorize all 209 help topics into logical groups and write
a help_categories.json index file that the help command reads."""
import json

CATEGORIES = {
    "Getting Started": {
        "description": "New to Oreka? Start here.",
        "topics": [
            "look", "score", "stats", "exits", "north", "south", "east", "west",
            "up", "down", "config", "prompt", "areas", "map", "who", "time",
            "weather", "help", "death", "respawn", "rest", "xp", "tnl",
            "levelup", "progression",
        ]
    },
    "Movement & Travel": {
        "description": "Getting around the world.",
        "topics": [
            "north", "south", "east", "west", "up", "down", "look", "scan",
            "exits", "speedwalk", "recall", "follow", "unfollow", "mount",
            "dismount", "ride", "fly", "land", "climb", "swim", "jump",
            "kneel", "sit", "stand", "wake", "where", "areas", "map",
        ]
    },
    "Combat": {
        "description": "Fighting, maneuvers, and staying alive.",
        "topics": [
            "kill", "flee", "assist", "rescue", "autoattack", "fullattack",
            "charge", "powerattack", "combatexpertise", "totaldefense",
            "fightdef", "target", "queue", "conditions", "ac", "bullrush",
            "disarm", "feint", "grapple", "gpin", "gescape", "gdamage",
            "overrun", "sunder", "trip", "flurry", "springattack",
            "stunningfist", "whirlwind", "smite", "layonhands", "rage",
            "withdraw", "consider", "duel", "corpses", "loot", "wimpy",
        ]
    },
    "Magic & Spells": {
        "description": "Casting, preparing, and understanding magic.",
        "topics": [
            "cast", "spells", "spellinfo", "spellbook", "prepare",
            "components", "domains", "dispel", "quaff", "turn",
            "summon", "familiar", "companion", "wildshape", "spellcraft",
            "identify",
        ]
    },
    "Skills": {
        "description": "D&D 3.5 skill checks and trained abilities.",
        "topics": [
            "skills", "skilllist", "skillcheck", "take10", "take20",
            "balance", "bluff", "climb", "concentration", "decipher",
            "diplomacy", "disable", "disguise", "escape", "forgery",
            "gatherinfo", "handle", "heal", "hide", "intimidate",
            "jump", "knowledge", "listen", "movesilently", "openlock",
            "perform", "profession", "ride", "sensemotive", "sleight",
            "spellcraft", "spot", "survival", "swim", "tumble",
            "usemagic", "userope",
        ]
    },
    "Items & Equipment": {
        "description": "Gear, inventory, and item management.",
        "topics": [
            "inventory", "equipment", "get", "take", "drop", "put",
            "wear", "remove", "compare", "examine", "appraise",
            "buy", "sell", "list", "shop", "shops", "give", "loot",
            "autoloot", "autogold", "autosac", "light", "extinguish",
            "drink_water", "eat", "use", "worth", "gold", "deposit",
            "itemsets",
        ]
    },
    "Communication": {
        "description": "Talking to players and NPCs.",
        "topics": [
            "say", "tell", "reply", "shout", "ooc", "global", "emote",
            "talk", "talkto", "board", "post", "readnote", "mail",
            "sendmail", "readmail", "guild", "group", "chat",
        ]
    },
    "Character & Progress": {
        "description": "Your character sheet, feats, factions, and journal.",
        "topics": [
            "score", "stats", "affects", "helpfeats", "favoredenemy",
            "achievements", "reputation", "title", "kinsense",
            "remort", "progression", "levelup", "xp", "tnl",
            "sense", "journal", "faction", "hidden",
        ]
    },
    "Crafting & Professions": {
        "description": "Making and repairing things.",
        "topics": [
            "craft", "recipes", "enchant", "repair", "components",
            "mine", "fish", "gather", "profession",
        ]
    },
    "Quests & Rescue": {
        "description": "Quests, captive rescue, and hidden missions.",
        "topics": [
            "quest", "questlog", "unbind", "present", "hidden",
        ]
    },
    "Social & Settings": {
        "description": "Player interaction and preferences.",
        "topics": [
            "who", "finger", "ignore", "afk", "alias", "config",
            "prompt", "survivalmode", "leaderboard", "auction",
            "gamble", "inspire",
        ]
    },
    "Doors & Locks": {
        "description": "Opening, closing, locking, and picking.",
        "topics": [
            "open", "close", "lock", "unlock", "pick", "peek",
        ]
    },
    "Admin Commands": {
        "description": "Immortal and builder commands.",
        "topics": [
            "@backup", "@restore", "@save",
        ]
    },
}

# Write the categories index
with open("data/help_categories.json", "w", encoding="utf-8") as f:
    json.dump(CATEGORIES, f, indent=2, ensure_ascii=False)

# Stats
total_categorized = set()
for cat, data in CATEGORIES.items():
    total_categorized.update(data["topics"])

with open("data/help.json", "r", encoding="utf-8") as f:
    all_topics = set(json.load(f).keys())

uncategorized = all_topics - total_categorized
print(f"Categories: {len(CATEGORIES)}")
print(f"Topics categorized: {len(total_categorized)}")
print(f"Total help topics: {len(all_topics)}")
print(f"Uncategorized: {len(uncategorized)}")
if uncategorized:
    print(f"  {sorted(uncategorized)}")
