import os

# D&D 3.5e Cleric reference data
CLERIC_SKILLS = [
    "Concentration", "Craft (any)", "Diplomacy", "Heal",
    "Knowledge (arcana)", "Knowledge (religion)", "Profession (any)", "Spellcraft"
]
CLERIC_DOMAINS = [
    "Air", "Chaos", "Death", "Earth", "Evil", "Fire", "Good", "Healing", "Knowledge",
    "Law", "Luck", "Magic", "Plant", "Protection", "Strength", "Sun", "Travel", "Trickery", "War", "Water"
]
CLERIC_FEATURES = [
    "Divine Spellcasting", "Turn/Rebuke Undead", "Spontaneous Cure/Inflict",
    "Domain Spells", "Channel Energy (optional)", "Deity & Alignment Restrictions"
]
CLERIC_FEATS = [
    "Extra Turning", "Improved Turning", "Divine Metamagic", "Augment Healing",
    "Empower Spell", "Quicken Spell", "Spell Focus", "Combat Casting"
]
CLERIC_SPELLS = [
    "Cure Light Wounds", "Bless", "Shield of Faith", "Detect Magic", "Divine Favor",
    "Hold Person", "Prayer", "Dispel Magic", "Cure Serious Wounds", "Flame Strike",
    "Raise Dead", "Greater Command", "Holy Smite", "Righteous Might", "Mass Cure Light Wounds",
    "Blade Barrier", "Resurrection", "Earthquake", "Gate"
]
CLERIC_PROGRESSION = [
    "1: Divine Spellcasting, Turn/Rebuke Undead, Domains, Spontaneous Cure/Inflict",
    "2: New spell levels, domain spells",
    "3: Bonus feat",
    "6: Bonus feat",
    "9: Bonus feat",
    "12: Bonus feat",
    "15: Bonus feat",
    "18: Bonus feat"
]

def update_classes_file(classes_path):
    cleric_entry = f'''
CLASSES["Cleric"] = {{
    "name": "Cleric",
    "class_skills": {CLERIC_SKILLS},
    "save_progression": {{"fort": "good", "ref": "poor", "will": "good"}},
    "attack_progression": "medium",
    "spellcasting": {{
        "type": "prepared",
        "start_level": 1,
        "max_level": 9,
        "domains": {CLERIC_DOMAINS},
        "spells": {CLERIC_SPELLS}
    }},
    "features": {CLERIC_FEATURES},
    "feats": {CLERIC_FEATS},
    "progression": {CLERIC_PROGRESSION}
}}
'''
    with open(classes_path, "a", encoding="utf-8") as f:
        f.write("\n" + cleric_entry)
    print("CLASSES['Cleric'] updated with full D&D 3.5e features.")

def update_commands_file(commands_path):
    help_text = f'''
    def cmd_help(self, character, *args):
        topic = " ".join(args).strip().lower()
        if topic == "cleric":
            return (
                "Cleric (D&D 3.5e OGL)\\n"
                "\\n"
                "Class Skills:\\n"
                "  {", ".join(CLERIC_SKILLS)}\\n"
                "\\n"
                "Domains:\\n"
                "  {", ".join(CLERIC_DOMAINS)}\\n"
                "\\n"
                "Common Feats:\\n"
                "  {", ".join(CLERIC_FEATS)}\\n"
                "\\n"
                "Common Spells:\\n"
                "  {", ".join(CLERIC_SPELLS)}\\n"
                "\\n"
                "Class Features:\\n"
                "  {", ".join(CLERIC_FEATURES)}\\n"
                "\\n"
                "Progression Table:\\n"
                "  {chr(10).join(CLERIC_PROGRESSION)}\\n"
                "\\n"
                "Special: Clerics must choose a deity and alignment. Some spells are restricted by alignment.\\n"
                "Turn Undead allows you to repel or destroy undead creatures.\\n"
                "Domains grant special powers and extra spells.\\n"
            )
        # ...existing help logic...
    '''
    with open(commands_path, "a", encoding="utf-8") as f:
        f.write("\n" + help_text)
    print("Cleric help topic updated in CommandParser.")

if __name__ == "__main__":
    update_classes_file("oreka_mud/src/classes.py")
    update_commands_file("oreka_mud/src/commands.py")
    print("Cleric class and help topic updated.")