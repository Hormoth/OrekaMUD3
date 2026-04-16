"""Append Deceiver-aligned creatures to the bestiary.

Adds 36 new entries covering Kobolds (caster-heavy as requested),
Goblins, Hobgoblins, Flamewarg Cultists, Dark Dwarves, Silentborn,
Half-Dómnathar, and full-blooded Dómnathar (including pre-invasion
House Leaders). All entries carry region keywords in the
``environment`` field so ``build_encounter_tables.py`` picks them up
automatically when re-run.

Idempotent by vnum. Run:
    python scripts/build_deceiver_bestiary.py
    python scripts/build_encounter_tables.py   # regenerate tables
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ---------------------------------------------------------------------------
# Signature ability / flavor helpers
# ---------------------------------------------------------------------------

KIN_SENSE_SILENCE = (
    "Kin-Sense Silence (Ex): undetectable by Kin-sense; registers as "
    "no-signature at all, as if dead. DC 25 Will save or relevant "
    "class-level check to overcome."
)

VOID_RESONANCE = (
    "Void Resonance (Su): on a confirmed hit with any spell, target "
    "must save or take 1 point of Wisdom drain as reality feels wrong."
)

DARKVISION_60 = "Darkvision 60 ft."
DARKVISION_120 = "Darkvision 120 ft."
LOWLIGHT = "Low-light vision"


# ---------------------------------------------------------------------------
# Helper: build a full bestiary entry dict
# ---------------------------------------------------------------------------

def make(vnum: int, name: str, *,
         cr: float, level: int,
         hp_dice: List[int], ac: int,
         dmg_dice: List[int],
         type_: str = "Humanoid",
         alignment: str = "Neutral Evil",
         env: str = "",
         org: str = "solitary",
         abilities: Optional[Dict[str, int]] = None,
         init: int = 1,
         speed: Optional[Dict[str, int]] = None,
         attacks: Optional[List[dict]] = None,
         spec_atk: Optional[List[str]] = None,
         spec_qual: Optional[List[str]] = None,
         feats: Optional[List[str]] = None,
         skills: Optional[Dict[str, int]] = None,
         saves: Optional[Dict[str, int]] = None,
         flags: Optional[List[str]] = None,
         advancement: str = "-",
         desc: str = "") -> Dict[str, Any]:
    return {
        "vnum": vnum,
        "name": name,
        "level": level,
        "hp_dice": hp_dice,
        "ac": ac,
        "damage_dice": dmg_dice,
        "flags": flags or [],
        "room_vnum": None,
        "type_": type_,
        "alignment": alignment,
        "ability_scores": abilities or {
            "Str": 10, "Dex": 12, "Con": 11,
            "Int": 10, "Wis": 10, "Cha": 10,
        },
        "initiative": init,
        "speed": speed or {"land": 30},
        "attacks": attacks or [],
        "special_attacks": spec_atk or [],
        "special_qualities": spec_qual or [],
        "feats": feats or [],
        "skills": skills or {},
        "saves": saves or {"Fort": 1, "Ref": 1, "Will": 0},
        "environment": env,
        "organization": org,
        "cr": cr,
        "advancement": advancement,
        "description": desc,
    }


# Environment strings that trigger the region classifier correctly.
ENV_GATEFALL_UNDERGROUND = (
    "Gatefall Reach (Silence Breach tunnel networks and Dómnathar "
    "burrow-forts beneath the southeastern foothills); underground"
)
ENV_DEEPWATER_TUNNELS = (
    "Deepwater Marches (Ashcrown Warren burrow-forts, Spur Tower "
    "outer tunnels); underground jungle"
)
ENV_DUAL_GATEFALL_DEEPWATER = (
    "Gatefall Reach and Deepwater Marches (Dómnathar-linked "
    "underground sites, Silence Breach Zones, Ashcrown Warren)"
)
ENV_ETERNAL_STEPPE_BURROW = (
    "Eternal Steppe (Burnt Hollows collapsed burrow-forts, Dark Dawn "
    "Battlefield dead zones); underground"
)
ENV_INFINITE_DESERT_SITES = (
    "Infinite Desert (Glass Wastes fusion cells, buried Deceiver "
    "caches, Dust-Cache warrens); underground"
)
ENV_KINSWEAVE_RUINS = (
    "Kinsweave Ruins (buried Deceiver artifact chambers in the Six "
    "Kings' ruins: Mytro, Kalite, Hylen, Thrush, Andrio, Pryee; "
    "Highridge lava-tubes); underground"
)
ENV_TIDEBLOOM_HIDDEN = (
    "Tidebloom Reach (Ashen Hollows raider camps, hidden Dómnathar "
    "refugee enclaves near the Tomb of Kings); forest"
)
ENV_TWINRIVERS_CELLS = (
    "Twin Rivers (Gorge-Bridge infiltrator cells, Unstrung "
    "Philosophers' hidden refuges in the Riverwind Heights)"
)
ENV_ANY_DECEIVER = (
    "Gatefall Reach, Deepwater Marches, Infinite Desert Glass Wastes, "
    "Eternal Steppe Burnt Hollows, and any active Dómnathar site; "
    "underground"
)


# ---------------------------------------------------------------------------
# KOBOLDS (heavy caster presence, as requested) -- vnums 10300-10307
# ---------------------------------------------------------------------------

KOBOLDS: List[Dict[str, Any]] = [
    make(10300, "Kobold Scout (Sorcerer 1)",
         cr=1, level=2, hp_dice=[2, 4, 2], ac=15, dmg_dice=[1, 4, 0],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_DUAL_GATEFALL_DEEPWATER,
         org="gang (2-4) or raid (5-12 plus 1 sorcerer)",
         abilities={"Str": 8, "Dex": 15, "Con": 10, "Int": 10,
                    "Wis": 9, "Cha": 13},
         init=2, speed={"land": 30},
         attacks=[{"type": "shortspear", "bonus": 2, "damage": "1d4-1"},
                  {"type": "light crossbow", "bonus": 3, "damage": "1d6"}],
         spec_atk=["Magic Missile (1/day, 1d4+1)"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Spells known: 0th -- acid splash, ray of frost, "
                    "resistance; 1st -- magic missile"],
         feats=["Alertness"],
         skills={"Hide": 6, "Listen": 2, "Move Silently": 3,
                 "Spellcraft": 2, "Spot": 2},
         saves={"Fort": 0, "Ref": 3, "Will": 2},
         flags=["kobold", "hostile", "caster"],
         desc=("A crest-scaled kobold with a focused, calculating stare. "
               "Dust-stained sleeves conceal the sigil-ink on her arms "
               "where she has drawn her spell foci.")),

    make(10301, "Kobold Cultist (Cleric 2)",
         cr=2, level=3, hp_dice=[3, 8, 3], ac=16, dmg_dice=[1, 6, 0],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_KINSWEAVE_RUINS + "; also Gatefall and Deepwater",
         org="gang (2-6 plus 1 kobold sorcerer)",
         abilities={"Str": 9, "Dex": 14, "Con": 11, "Int": 10,
                    "Wis": 14, "Cha": 10},
         init=2, speed={"land": 30},
         attacks=[{"type": "morningstar", "bonus": 3, "damage": "1d6"}],
         spec_atk=["Inflict Light Wounds (1d8+2, 3/day)",
                   "Rebuke Undead 3/day"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Spells/day: 0th -- 4 (cure minor, detect magic); "
                    "1st -- 3 (bane, shield of faith, inflict light wounds)"],
         feats=["Combat Casting", "Weapon Focus (morningstar)"],
         skills={"Concentration": 6, "Knowledge (religion)": 4,
                 "Listen": 3, "Spellcraft": 4, "Spot": 3},
         saves={"Fort": 3, "Ref": 2, "Will": 5},
         flags=["kobold", "hostile", "caster"],
         desc=("A stooped kobold in scorched temple-robes, a small silver "
               "ampoule of Dómnathar Void-Oil hung at her neck. She tends "
               "the warren's sick and the warren's dead with equal patience.")),

    make(10302, "Kobold Sorcerer (Sorcerer 3)",
         cr=3, level=4, hp_dice=[4, 4, 4], ac=15, dmg_dice=[1, 4, 0],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_DUAL_GATEFALL_DEEPWATER,
         org="band (1 sorcerer plus 4-8 kobold scouts)",
         abilities={"Str": 8, "Dex": 15, "Con": 10, "Int": 11,
                    "Wis": 10, "Cha": 16},
         init=2, speed={"land": 30},
         attacks=[{"type": "dagger", "bonus": 1, "damage": "1d3-1"}],
         spec_atk=["Burning Hands 3/day (2d4)",
                   "Magic Missile 4/day (2 missiles)",
                   "Mage Armor 4/day"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Spells/day: 0th -- 6; 1st -- 6; 2nd -- 4",
                    "Spells known include: magic missile, mage armor, "
                    "burning hands, scorching ray, invisibility"],
         feats=["Combat Casting", "Spell Focus (evocation)"],
         skills={"Concentration": 7, "Knowledge (arcana)": 4,
                 "Listen": 2, "Spellcraft": 5, "Spot": 2},
         saves={"Fort": 1, "Ref": 3, "Will": 3},
         flags=["kobold", "hostile", "caster"],
         desc=("A kobold whose scales have faded to ash-grey from long hours "
               "near ritual-flame. His eyes are bright yellow and his claws "
               "are stained with different colors of dried reagent.")),

    make(10303, "Kobold Trapsmith (Rogue 3)",
         cr=3, level=4, hp_dice=[4, 6, 0], ac=17, dmg_dice=[1, 6, 1],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_DUAL_GATEFALL_DEEPWATER + "; also Kinsweave ruins",
         org="band (1 trapsmith plus 2-4 scouts)",
         abilities={"Str": 10, "Dex": 16, "Con": 10, "Int": 14,
                    "Wis": 10, "Cha": 8},
         init=3, speed={"land": 30},
         attacks=[{"type": "short sword", "bonus": 5,
                   "damage": "1d6+1 plus poison"}],
         spec_atk=["Sneak Attack +2d6",
                   "Poisoned blade (DC 14, 1d4 Dex/1d4 Dex)"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Trapfinding", "Evasion", "Trap sense +1"],
         feats=["Weapon Finesse", "Stealthy"],
         skills={"Craft (trapmaking)": 9, "Disable Device": 10,
                 "Hide": 12, "Move Silently": 12, "Search": 8,
                 "Spot": 4},
         saves={"Fort": 1, "Ref": 6, "Will": 1},
         flags=["kobold", "hostile", "rogue"],
         desc=("A wiry kobold with a brass belt of loops full of iron "
               "teeth, caltrops, dart-needles, and glass phials. He "
               "smiles with very small very even teeth.")),

    make(10304, "Kobold Wizard (Wizard 4)",
         cr=4, level=5, hp_dice=[5, 4, 5], ac=14, dmg_dice=[1, 4, 0],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_KINSWEAVE_RUINS + "; also Gatefall, Deepwater",
         org="circle (1 wizard plus 2 apprentice-sorcerers)",
         abilities={"Str": 7, "Dex": 15, "Con": 11, "Int": 16,
                    "Wis": 12, "Cha": 10},
         init=2, speed={"land": 30},
         attacks=[{"type": "quarterstaff", "bonus": 1, "damage": "1d6-2"}],
         spec_atk=["Fireball 1/day (5d6)", "Scorching Ray 1/day (4d6)",
                   "Magic Missile 3/day (3 missiles)",
                   "Summon Monster II 1/day"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Spells/day: 0th -- 5; 1st -- 5; 2nd -- 4; 3rd -- 2",
                    "Specialization: Evocation (opposed: Enchantment, "
                    "Illusion)", "Familiar (Tiny Viper)"],
         feats=["Scribe Scroll", "Spell Focus (evocation)",
                "Combat Casting"],
         skills={"Concentration": 9, "Decipher Script": 6,
                 "Knowledge (arcana)": 11, "Knowledge (history)": 5,
                 "Spellcraft": 13},
         saves={"Fort": 2, "Ref": 3, "Will": 5},
         flags=["kobold", "hostile", "caster"],
         desc=("An elder kobold in a high-collared robe sewn with brass "
               "reading-lenses. She has catalogued and copied more "
               "Deceiver scrolls than any living Kin scholar; she simply "
               "does not share.")),

    make(10305, "Kobold Fire-Sorcerer (Sorcerer 5)",
         cr=5, level=6, hp_dice=[6, 4, 6], ac=15, dmg_dice=[1, 4, 0],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_KINSWEAVE_RUINS + "; also Pryee lava-tubes specifically",
         org="solitary or lieutenant (with 1 kobold wizard and 6 scouts)",
         abilities={"Str": 8, "Dex": 16, "Con": 11, "Int": 12,
                    "Wis": 10, "Cha": 18},
         init=3, speed={"land": 30},
         attacks=[{"type": "dagger +1", "bonus": 3, "damage": "1d3"}],
         spec_atk=["Fireball 2/day (5d6)",
                   "Scorching Ray at will (4d6)",
                   "Burning Hands 5/day",
                   "Flame Blade (melee touch 1d8+3, 6 rounds)"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Spells/day: 0th -- 6; 1st -- 7; 2nd -- 6; 3rd -- 4",
                    "Draconic heritage (Red Dragon): fire subtype, "
                    "resistance 5 to fire"],
         feats=["Spell Focus (evocation)", "Greater Spell Focus (evocation)",
                "Empower Spell", "Combat Casting"],
         skills={"Bluff": 10, "Concentration": 9,
                 "Knowledge (arcana)": 5, "Spellcraft": 9},
         saves={"Fort": 2, "Ref": 4, "Will": 4},
         flags=["kobold", "hostile", "caster", "boss"],
         desc=("A scarred kobold whose left hand has fused into a claw of "
               "living flame. He calls himself Ashkarr, claims descent "
               "from a red dragon, and is disliked even by the other "
               "kobolds for his arrogance.")),

    make(10306, "Kobold Dragon-Priest (Cleric 5)",
         cr=5, level=6, hp_dice=[6, 8, 6], ac=19, dmg_dice=[1, 8, 0],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_ANY_DECEIVER,
         org="solitary or leader (with 6-10 kobolds and 1 trapsmith)",
         abilities={"Str": 10, "Dex": 14, "Con": 12, "Int": 11,
                    "Wis": 17, "Cha": 12},
         init=2, speed={"land": 20},
         attacks=[{"type": "heavy mace +1", "bonus": 5, "damage": "1d8+1"}],
         spec_atk=["Inflict Serious Wounds 1/day (3d8+5)",
                   "Cause Fear 3/day", "Rebuke Undead 4/day"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Spells/day: 0th -- 5; 1st -- 5; 2nd -- 4; 3rd -- 3",
                    "Domains: Fire (fire resistance 10), Law",
                    "Turn or rebuke dragons 1/day"],
         feats=["Combat Casting", "Spell Penetration",
                "Weapon Focus (heavy mace)"],
         skills={"Concentration": 9, "Diplomacy": 6,
                 "Knowledge (religion)": 7, "Spellcraft": 6},
         saves={"Fort": 5, "Ref": 3, "Will": 7},
         flags=["kobold", "hostile", "caster", "boss"],
         desc=("An old kobold priestess, scale-crest gone white, who "
               "serves the red dragon her clan believes to sleep beneath "
               "Pryee. Her robes smell of kerosene and incense.")),

    make(10307, "Kobold Sorcerer-Chief (Sorcerer 7)",
         cr=7, level=8, hp_dice=[8, 4, 8], ac=17, dmg_dice=[1, 4, 0],
         type_="Humanoid (Reptilian)", alignment="Lawful Evil",
         env=ENV_KINSWEAVE_RUINS + "; Gatefall major warrens",
         org="warren-leader (with 1 kobold wizard, 1 dragon-priest, "
             "2 trapsmiths, 12-20 lesser kobolds)",
         abilities={"Str": 10, "Dex": 16, "Con": 12, "Int": 13,
                    "Wis": 12, "Cha": 19},
         init=3, speed={"land": 30},
         attacks=[{"type": "dagger +1", "bonus": 5, "damage": "1d3+1"}],
         spec_atk=["Fireball 2/day (7d6)",
                   "Lightning Bolt 1/day (7d6)",
                   "Dispel Magic 2/day",
                   "Suggestion 2/day (DC 17)"],
         spec_qual=[DARKVISION_60, "Light sensitivity",
                    "Spells/day: 0th -- 6; 1st -- 7; 2nd -- 7; "
                    "3rd -- 7; 4th -- 5",
                    "Draconic heritage (Red Dragon): fire subtype",
                    "Familiar (pseudodragon)"],
         feats=["Spell Focus (evocation)",
                "Greater Spell Focus (evocation)",
                "Empower Spell", "Maximize Spell", "Combat Casting"],
         skills={"Bluff": 14, "Concentration": 12, "Diplomacy": 6,
                 "Intimidate": 14, "Knowledge (arcana)": 11,
                 "Spellcraft": 13},
         saves={"Fort": 3, "Ref": 5, "Will": 6},
         flags=["kobold", "hostile", "caster", "boss"],
         desc=("A kobold of truly unusual stature for her kind -- nearly "
               "four feet tall -- with a cape of overlapping metal scales "
               "scavenged from a dragon her grandmother killed. She has "
               "held the warren for thirty years and intends to hold it "
               "for thirty more.")),
]


# ---------------------------------------------------------------------------
# GOBLINS & HOBGOBLINS & FLAMEWARG CULTISTS -- vnums 10308-10312
# ---------------------------------------------------------------------------

GOBLINOIDS: List[Dict[str, Any]] = [
    make(10308, "Goblin Shaman (Adept 3)",
         cr=2, level=4, hp_dice=[4, 6, 4], ac=15, dmg_dice=[1, 6, 0],
         type_="Humanoid (Goblinoid)", alignment="Neutral Evil",
         env=ENV_DEEPWATER_TUNNELS + "; Ashen Hollows raider camps",
         org="solitary or pack leader (with 4-8 goblins)",
         abilities={"Str": 10, "Dex": 13, "Con": 12, "Int": 10,
                    "Wis": 14, "Cha": 11},
         init=1, speed={"land": 30},
         attacks=[{"type": "morningstar", "bonus": 3, "damage": "1d6"}],
         spec_atk=["Cause Fear 1/day", "Burning Hands 1/day (1d4)"],
         spec_qual=[DARKVISION_60,
                    "Spells/day: 0th -- 3 (cure minor, detect magic, "
                    "ghost sound); 1st -- 2 (cause fear, burning hands); "
                    "2nd -- 1 (invisibility)"],
         feats=["Combat Casting", "Weapon Focus (morningstar)"],
         skills={"Concentration": 4, "Hide": 4, "Listen": 5,
                 "Spellcraft": 3, "Spot": 5},
         saves={"Fort": 2, "Ref": 2, "Will": 5},
         flags=["goblin", "hostile", "caster"],
         desc=("A wizened goblin with tattoos of crossed-out suns -- the "
               "mark of the Flamewarg faith. He reads the future in the "
               "smoke of burnt hair.")),

    make(10309, "Hobgoblin Sergeant (Fighter 2)",
         cr=3, level=3, hp_dice=[3, 10, 6], ac=18, dmg_dice=[1, 8, 2],
         type_="Humanoid (Goblinoid)", alignment="Lawful Evil",
         env=ENV_DUAL_GATEFALL_DEEPWATER + "; Burnt Hollows",
         org="unit (1 sergeant plus 6-10 hobgoblins)",
         abilities={"Str": 15, "Dex": 13, "Con": 14, "Int": 10,
                    "Wis": 10, "Cha": 9},
         init=1, speed={"land": 30},
         attacks=[{"type": "longsword", "bonus": 6, "damage": "1d8+2"},
                  {"type": "shortbow", "bonus": 4, "damage": "1d6"}],
         spec_atk=["Power Attack", "Cleave"],
         spec_qual=[DARKVISION_60,
                    "Discipline: adjacent hobgoblins gain +1 morale to "
                    "attack and save vs fear"],
         feats=["Power Attack", "Cleave", "Weapon Focus (longsword)",
                "Improved Initiative"],
         skills={"Climb": 4, "Intimidate": 4, "Listen": 2,
                 "Move Silently": 4, "Spot": 2},
         saves={"Fort": 5, "Ref": 1, "Will": 1},
         flags=["hobgoblin", "hostile"],
         desc=("A hobgoblin in well-kept Dómnathar-issue chain and red "
               "tabard. He salutes crisply, speaks rarely, and breaks "
               "men who speak out of turn.")),

    make(10310, "Hobgoblin Tunnel-Warden (Fighter 3 / Ranger 1)",
         cr=4, level=4, hp_dice=[4, 10, 8], ac=19, dmg_dice=[1, 8, 3],
         type_="Humanoid (Goblinoid)", alignment="Lawful Evil",
         env=ENV_GATEFALL_UNDERGROUND,
         org="patrol (1 warden plus 4-6 hobgoblins and 2 war-wargs)",
         abilities={"Str": 17, "Dex": 14, "Con": 14, "Int": 10,
                    "Wis": 12, "Cha": 9},
         init=2, speed={"land": 30},
         attacks=[{"type": "longsword +1", "bonus": 8, "damage": "1d8+4"},
                  {"type": "composite longbow +1", "bonus": 7,
                   "damage": "1d8+4"}],
         spec_atk=["Power Attack", "Cleave", "Favored Enemy (Humanoids)"],
         spec_qual=[DARKVISION_60,
                    "Wild Empathy", "Track feat",
                    "Knows every turn and side-passage of his patrol circuit"],
         feats=["Power Attack", "Cleave", "Weapon Focus (longsword)",
                "Track", "Endurance"],
         skills={"Hide": 5, "Listen": 6, "Move Silently": 7,
                 "Spot": 6, "Survival": 7},
         saves={"Fort": 7, "Ref": 3, "Will": 2},
         flags=["hobgoblin", "hostile"],
         desc=("A veteran hobgoblin with a deep scar from jaw to temple "
               "and the gait of a man whose back has been broken and "
               "reset. He knows the tunnels better than any map.")),

    make(10311, "Hobgoblin Captain (Fighter 5)",
         cr=6, level=5, hp_dice=[5, 10, 10], ac=21, dmg_dice=[1, 8, 4],
         type_="Humanoid (Goblinoid)", alignment="Lawful Evil",
         env=ENV_DUAL_GATEFALL_DEEPWATER,
         org="company-leader (with 2 sergeants, 12-20 hobgoblins, "
             "4 war-wargs)",
         abilities={"Str": 17, "Dex": 14, "Con": 16, "Int": 11,
                    "Wis": 12, "Cha": 12},
         init=2, speed={"land": 30},
         attacks=[{"type": "greatsword +1", "bonus": 10,
                   "damage": "2d6+7"}],
         spec_atk=["Power Attack", "Cleave", "Great Cleave",
                   "Tactical orders (grant allies +2 initiative)"],
         spec_qual=[DARKVISION_60,
                    "Field Promotion: when the Captain takes a standard "
                    "action to issue a command, all hobgoblins within "
                    "30 ft gain +1 to hit for 1 round"],
         feats=["Power Attack", "Cleave", "Great Cleave",
                "Weapon Focus (greatsword)",
                "Weapon Specialization (greatsword)",
                "Improved Initiative"],
         skills={"Climb": 8, "Intimidate": 9, "Listen": 4,
                 "Move Silently": 6, "Ride": 6, "Spot": 4},
         saves={"Fort": 7, "Ref": 3, "Will": 3},
         flags=["hobgoblin", "hostile", "boss"],
         desc=("A hobgoblin captain in articulated plate, wearing an "
               "iron lamellar sash of rank worked with the seven "
               "broken-chain marks of the Shattered Host.")),

    make(10312, "Flamewarg Cult Initiate (Sorcerer 3, Human)",
         cr=3, level=3, hp_dice=[3, 4, 6], ac=14, dmg_dice=[1, 6, 0],
         type_="Humanoid (Human)", alignment="Chaotic Evil",
         env=(ENV_ETERNAL_STEPPE_BURROW + "; Gatefall Scar Road; "
              "occasional Infinite Desert oasis raid camps"),
         org="cell (2-4 cultists plus 1 flamewarg and 2 goblins)",
         abilities={"Str": 10, "Dex": 13, "Con": 14, "Int": 10,
                    "Wis": 10, "Cha": 15},
         init=1, speed={"land": 30},
         attacks=[{"type": "burning quarterstaff", "bonus": 1,
                   "damage": "1d6+1d4 fire"}],
         spec_atk=["Burning Hands 4/day (2d4)",
                   "Produce Flame at will (1d6+3)",
                   "Ritual self-immolation (healing others at cost of caster)"],
         spec_qual=["Fire resistance 5",
                    "Spells/day: 0th -- 6; 1st -- 6",
                    "Cult marks visible on the forearms -- crossed-out "
                    "suns in burn-scars"],
         feats=["Combat Casting", "Toughness"],
         skills={"Bluff": 8, "Concentration": 8, "Knowledge (religion)": 4,
                 "Spellcraft": 4},
         saves={"Fort": 3, "Ref": 2, "Will": 3},
         flags=["human", "hostile", "caster", "cultist"],
         desc=("A lean human woman with charred sleeves and a half-healed "
               "burn on her cheek in the shape of a hand. She believes "
               "the Deceivers will return, and she will be rewarded.")),
]


# ---------------------------------------------------------------------------
# DARK DWARVES -- vnums 10313-10317
# ---------------------------------------------------------------------------

DARK_DWARVES: List[Dict[str, Any]] = [
    make(10313, "Dark Dwarf Scavenger-Lord (Rogue 4)",
         cr=4, level=5, hp_dice=[5, 6, 10], ac=17, dmg_dice=[1, 6, 2],
         type_="Humanoid (Dwarf)", alignment="Neutral Evil",
         env=ENV_INFINITE_DESERT_SITES + "; Kinsweave ruin edges",
         org="solitary or leader (with 2-4 kobolds and captured slaves)",
         abilities={"Str": 14, "Dex": 16, "Con": 14, "Int": 13,
                    "Wis": 11, "Cha": 10},
         init=3, speed={"land": 20},
         attacks=[{"type": "short sword", "bonus": 6, "damage": "1d6+2"},
                  {"type": "hand crossbow", "bonus": 6, "damage": "1d4"}],
         spec_atk=["Sneak Attack +2d6",
                   "Poisoned bolts (DC 12, 1d2 Con/1d2 Con)"],
         spec_qual=[DARKVISION_120,
                    "Stonecunning", "Trapfinding", "Evasion",
                    "Void-touch: +2 vs mind-affecting effects",
                    "Trap sense +1"],
         feats=["Weapon Finesse", "Two-Weapon Fighting", "Alertness"],
         skills={"Appraise": 9, "Disable Device": 11, "Hide": 11,
                 "Move Silently": 11, "Search": 9, "Spot": 8},
         saves={"Fort": 3, "Ref": 7, "Will": 2},
         flags=["dwarf", "dark_dwarf", "hostile", "rogue"],
         desc=("A dwarf whose skin has gone the color of wet slate from "
               "long years in the Deceiver tunnels. His beard is braided "
               "with small brass rings, each one taken from a Kin scout "
               "who did not come home.")),

    make(10314, "Dark Dwarf Warrior (Fighter 3)",
         cr=4, level=3, hp_dice=[3, 10, 9], ac=19, dmg_dice=[1, 8, 3],
         type_="Humanoid (Dwarf)", alignment="Lawful Evil",
         env=ENV_ANY_DECEIVER,
         org="squad (2-4 warriors plus 1 fireforged)",
         abilities={"Str": 17, "Dex": 12, "Con": 16, "Int": 10,
                    "Wis": 11, "Cha": 8},
         init=1, speed={"land": 20},
         attacks=[{"type": "dwarven waraxe", "bonus": 7,
                   "damage": "1d10+4"}],
         spec_atk=["Power Attack", "+1 vs goblinoids and orcs"],
         spec_qual=[DARKVISION_120, "Stonecunning",
                    "Void-touch: +2 vs mind-affecting effects",
                    "+4 vs giant-type, +2 saves vs poison/spells"],
         feats=["Power Attack", "Cleave", "Weapon Focus (waraxe)"],
         skills={"Appraise": 2, "Craft (weapons)": 5,
                 "Intimidate": 3, "Listen": 2, "Spot": 2},
         saves={"Fort": 6, "Ref": 2, "Will": 1},
         flags=["dwarf", "dark_dwarf", "hostile"],
         desc=("A broad, scarred dwarf in iron plate darkened with lamp-"
               "black. The Deceivers' War left his clan underground; four "
               "generations later, this is what the clan has become.")),

    make(10315, "Dark Dwarf Fireforged (Fighter 5)",
         cr=6, level=5, hp_dice=[5, 10, 15], ac=21, dmg_dice=[1, 10, 4],
         type_="Humanoid (Dwarf)", alignment="Lawful Evil",
         env=ENV_KINSWEAVE_RUINS + "; Infinite Desert forge-sites",
         org="elite (1 fireforged plus 3-4 dark dwarf warriors)",
         abilities={"Str": 18, "Dex": 12, "Con": 16, "Int": 11,
                    "Wis": 12, "Cha": 9},
         init=1, speed={"land": 20},
         attacks=[{"type": "flaming dwarven waraxe +1", "bonus": 10,
                   "damage": "1d10+5 plus 1d6 fire"}],
         spec_atk=["Power Attack", "Cleave", "Fire Mastery (reroll 1s "
                   "on fire damage)"],
         spec_qual=[DARKVISION_120, "Stonecunning",
                    "Fire resistance 10", "Void-touch",
                    "Forge-Blessed: +2 saves vs heat/fire effects"],
         feats=["Power Attack", "Cleave", "Weapon Focus (waraxe)",
                "Weapon Specialization (waraxe)", "Great Cleave"],
         skills={"Craft (weaponsmithing)": 10,
                 "Intimidate": 4, "Listen": 3, "Spot": 3},
         saves={"Fort": 8, "Ref": 2, "Will": 2},
         flags=["dwarf", "dark_dwarf", "hostile", "boss"],
         desc=("A dwarf whose right arm is scarred to the shoulder from "
               "forge-fire he stood in as part of his vow. His axe still "
               "smokes faintly from the heat of the chamber where it "
               "was quenched.")),

    make(10316, "Dark Dwarf Void-Smith (Expert 7 / Wizard 1)",
         cr=8, level=8, hp_dice=[8, 6, 16], ac=16, dmg_dice=[1, 6, 1],
         type_="Humanoid (Dwarf)", alignment="Lawful Evil",
         env=ENV_ANY_DECEIVER,
         org="solitary (with 2-3 warrior guards)",
         abilities={"Str": 12, "Dex": 13, "Con": 15, "Int": 18,
                    "Wis": 14, "Cha": 10},
         init=1, speed={"land": 20},
         attacks=[{"type": "+1 smith's hammer", "bonus": 5,
                   "damage": "1d6+2"}],
         spec_atk=["Craft Construct (partial)",
                   "Fabricate 1/day",
                   "Shield 4/day",
                   "Magic Weapon (self-cast) 2/day"],
         spec_qual=[DARKVISION_120, "Stonecunning",
                    "Spells/day: 0th -- 3; 1st -- 2",
                    "Void-forging: can craft items that suppress "
                    "Kin-sense in a 5-ft radius"],
         feats=["Craft Wondrous Item", "Craft Arms and Armor",
                "Skill Focus (Craft - weaponsmithing)", "Scribe Scroll"],
         skills={"Appraise": 15, "Concentration": 9,
                 "Craft (armorsmithing)": 18, "Craft (weaponsmithing)": 18,
                 "Knowledge (arcana)": 12, "Spellcraft": 10},
         saves={"Fort": 6, "Ref": 3, "Will": 8},
         flags=["dwarf", "dark_dwarf", "hostile", "caster", "crafter"],
         desc=("A dwarf smith whose beard is threaded with silver wire "
               "and whose leather apron is embroidered with runes in "
               "a script not of this world. She makes the suppressor-"
               "irons that hide the Silentborn from Kin-sense.")),

    make(10317, "Dark Dwarf Lore-Keeper (Cleric 9)",
         cr=11, level=9, hp_dice=[9, 8, 18], ac=22, dmg_dice=[1, 8, 2],
         type_="Humanoid (Dwarf)", alignment="Lawful Evil",
         env=("Deepwater Marches (Spur Tower archive levels); "
              "Infinite Desert buried forge-vaults"),
         org="solitary (in the heart of a major Dómnathar site)",
         abilities={"Str": 14, "Dex": 11, "Con": 16, "Int": 14,
                    "Wis": 19, "Cha": 13},
         init=0, speed={"land": 20},
         attacks=[{"type": "heavy mace +2", "bonus": 11,
                   "damage": "1d8+4"}],
         spec_atk=["Rebuke Undead 5/day",
                   "Inflict Critical Wounds (4d8+9)",
                   "Flame Strike 1/day (9d6)",
                   "Summon Monster V 2/day"],
         spec_qual=[DARKVISION_120, "Stonecunning", "Void-touch",
                    "Spells/day: 0th -- 6; 1st -- 6+1; 2nd -- 5+1; "
                    "3rd -- 5+1; 4th -- 4+1; 5th -- 2+1",
                    "Domains: Knowledge, Fire"],
         feats=["Combat Casting", "Scribe Scroll", "Spell Penetration",
                "Greater Spell Penetration", "Craft Wondrous Item"],
         skills={"Concentration": 15, "Knowledge (arcana)": 14,
                 "Knowledge (history)": 14, "Knowledge (religion)": 14,
                 "Spellcraft": 14},
         saves={"Fort": 9, "Ref": 3, "Will": 11},
         flags=["dwarf", "dark_dwarf", "hostile", "caster", "boss"],
         desc=("An ancient dwarf with milky eyes and a perfect memory. She "
               "is the living archive of the Shattered Host's remaining "
               "lineages, and she is the reason the Dómnathar remnants "
               "still know who they are.")),
]


# ---------------------------------------------------------------------------
# SILENTBORN -- vnums 10318-10321
# ---------------------------------------------------------------------------

SILENTBORN: List[Dict[str, Any]] = [
    make(10318, "Silentborn Loyalist (Warrior 3 / Rogue 1)",
         cr=4, level=4, hp_dice=[4, 8, 8], ac=16, dmg_dice=[1, 8, 2],
         type_="Humanoid (Silentborn)", alignment="Lawful Evil",
         env=(ENV_ETERNAL_STEPPE_BURROW + "; Deepwater Spur Tower; "
              "Tidebloom hidden enclaves"),
         org="squad (3-6 loyalists plus 1 silentborn assassin)",
         abilities={"Str": 15, "Dex": 15, "Con": 13, "Int": 11,
                    "Wis": 10, "Cha": 8},
         init=2, speed={"land": 30},
         attacks=[{"type": "longsword", "bonus": 6, "damage": "1d8+2"}],
         spec_atk=["Sneak Attack +1d6"],
         spec_qual=[KIN_SENSE_SILENCE,
                    "Appears fully Kin at casual observation (Spot DC 20 "
                    "to spot the faint luminosity in their eyes)",
                    "Trapfinding"],
         feats=["Weapon Focus (longsword)", "Dodge", "Improved Initiative"],
         skills={"Bluff": 5, "Disguise": 5, "Hide": 6,
                 "Move Silently": 6, "Spot": 4},
         saves={"Fort": 4, "Ref": 5, "Will": 1},
         flags=["silentborn", "hostile", "kin_silent"],
         desc=("A figure who would pass for human -- unless you stared at "
               "her eyes in dim light and caught the faint luminous "
               "yellow-green behind the pupils. She was born in the "
               "Dómnathar breeding program and never raised to any other.")),

    make(10319, "Silentborn Researcher (Wizard 4)",
         cr=5, level=4, hp_dice=[4, 4, 4], ac=14, dmg_dice=[1, 4, 0],
         type_="Humanoid (Silentborn)", alignment="Lawful Evil",
         env="Deepwater Marches Spur Tower breeding-lab; Eternal Steppe "
             "Second Breath Hideout; Infinite Desert Fusion-Cell Outpost",
         org="solitary (in a laboratory, with 2 loyalist guards)",
         abilities={"Str": 9, "Dex": 14, "Con": 11, "Int": 18,
                    "Wis": 13, "Cha": 10},
         init=2, speed={"land": 30},
         attacks=[{"type": "dagger", "bonus": 1, "damage": "1d4-1"}],
         spec_atk=["Scorching Ray (4d6)", "Magic Missile (3 missiles)",
                   "Summon Monster II"],
         spec_qual=[KIN_SENSE_SILENCE, DARKVISION_60,
                    "Spells/day: 0th -- 4; 1st -- 4; 2nd -- 3",
                    "Specialization: Conjuration"],
         feats=["Scribe Scroll", "Combat Casting", "Skill Focus (Knowledge -- arcana)"],
         skills={"Concentration": 7, "Decipher Script": 10,
                 "Knowledge (arcana)": 13, "Spellcraft": 13},
         saves={"Fort": 1, "Ref": 3, "Will": 5},
         flags=["silentborn", "hostile", "caster", "kin_silent"],
         desc=("A slim figure with half-moon lenses, bent over a book "
               "written in two alphabets at once. She is the third "
               "Silentborn generation and has never set foot above ground.")),

    make(10320, "Silentborn Battle-Priest (Cleric 5)",
         cr=6, level=5, hp_dice=[5, 8, 10], ac=20, dmg_dice=[1, 8, 2],
         type_="Humanoid (Silentborn)", alignment="Lawful Evil",
         env=ENV_ETERNAL_STEPPE_BURROW + "; Deepwater Spur Tower",
         org="solitary (with 4-6 loyalists)",
         abilities={"Str": 14, "Dex": 12, "Con": 14, "Int": 11,
                    "Wis": 16, "Cha": 13},
         init=1, speed={"land": 20},
         attacks=[{"type": "heavy flail +1", "bonus": 8,
                   "damage": "1d10+3"}],
         spec_atk=["Inflict Serious Wounds 1/day",
                   "Silence 1/day", "Rebuke Undead 4/day",
                   "Searing Light 2/day"],
         spec_qual=[KIN_SENSE_SILENCE,
                    "Spells/day: 0th -- 5; 1st -- 4+1; 2nd -- 3+1; 3rd -- 2+1",
                    "Domains: Death, Trickery"],
         feats=["Combat Casting", "Weapon Focus (heavy flail)",
                "Power Attack"],
         skills={"Bluff": 6, "Concentration": 10,
                 "Knowledge (religion)": 6, "Spellcraft": 6},
         saves={"Fort": 6, "Ref": 2, "Will": 7},
         flags=["silentborn", "hostile", "caster", "kin_silent", "boss"],
         desc=("A Silentborn priestess in brass-bossed black leather, "
               "who serves no god known to the Kin. Her holy symbol is a "
               "closed circle with nothing inside.")),

    make(10321, "Silentborn Assassin (Rogue 5 / Assassin 2)",
         cr=7, level=7, hp_dice=[7, 6, 14], ac=19, dmg_dice=[1, 6, 2],
         type_="Humanoid (Silentborn)", alignment="Neutral Evil",
         env=(ENV_TIDEBLOOM_HIDDEN + "; Twin Rivers infiltration cells; "
              "any urban Dómnathar operation"),
         org="solitary",
         abilities={"Str": 12, "Dex": 18, "Con": 13, "Int": 14,
                    "Wis": 12, "Cha": 11},
         init=4, speed={"land": 30},
         attacks=[{"type": "poisoned kukri +2", "bonus": 10,
                   "damage": "1d4+3 plus poison (DC 15, 1d6 Con/1d6 Con)"}],
         spec_atk=["Sneak Attack +4d6",
                   "Death Attack (DC 15, paralyze or kill on 3-round study)"],
         spec_qual=[KIN_SENSE_SILENCE,
                    "Poison use (cannot poison self)",
                    "Spells/day: 1st -- 2 (disguise self, jump)",
                    "Evasion", "Uncanny Dodge"],
         feats=["Weapon Finesse", "Two-Weapon Fighting", "Combat Expertise",
                "Improved Initiative", "Dodge"],
         skills={"Bluff": 10, "Disguise": 10, "Hide": 16,
                 "Move Silently": 16, "Open Lock": 12, "Spot": 11},
         saves={"Fort": 4, "Ref": 10, "Will": 4},
         flags=["silentborn", "hostile", "kin_silent", "boss"],
         desc=("A killer the Spur Tower sends when subtlety is essential. "
               "He has been knifed, hanged, and drowned by three "
               "different Kin city-watches and all three reported him "
               "dead and buried. He was not.")),
]


# ---------------------------------------------------------------------------
# HALF-DÓMNATHAR -- vnums 10322-10329
# ---------------------------------------------------------------------------

HALF_DOMNATHAR: List[Dict[str, Any]] = [
    make(10322, "Half-Dómnathar Broker (Bard 5 / Rogue 2)",
         cr=7, level=7, hp_dice=[7, 6, 7], ac=17, dmg_dice=[1, 6, 1],
         type_="Humanoid", alignment="Lawful Evil",
         env=(ENV_TWINRIVERS_CELLS + "; Deepwater Ashcrown Warren "
              "as an embedded broker"),
         org="solitary (with 2-4 silentborn attendants)",
         abilities={"Str": 10, "Dex": 15, "Con": 12, "Int": 15,
                    "Wis": 12, "Cha": 18},
         init=2, speed={"land": 30},
         attacks=[{"type": "rapier +1", "bonus": 7, "damage": "1d6+1"}],
         spec_atk=["Sneak Attack +1d6", "Bardic Music 5/day",
                   "Suggestion (via music, DC 16)"],
         spec_qual=["Faintly luminous eyes in low light",
                    "Spells/day: 0th -- 3; 1st -- 3; 2nd -- 2",
                    "Bardic Knowledge +9", "Trapfinding", "Evasion",
                    "+2 racial to Bluff and Diplomacy"],
         feats=["Weapon Finesse", "Persuasive", "Negotiator",
                "Skill Focus (Diplomacy)"],
         skills={"Appraise": 9, "Bluff": 16, "Diplomacy": 18,
                 "Gather Information": 14, "Perform (oratory)": 12,
                 "Sense Motive": 10},
         saves={"Fort": 3, "Ref": 8, "Will": 5},
         flags=["half_domnathar", "hostile", "boss"],
         desc=("A handsome, neatly-dressed figure with slightly elongated "
               "ears who passes for human at any social distance. She has "
               "a perfect smile and a perfect memory for names.")),

    make(10323, "Half-Dómnathar Cult-Leader (Sorcerer 6)",
         cr=7, level=6, hp_dice=[6, 4, 6], ac=15, dmg_dice=[1, 4, 0],
         type_="Humanoid", alignment="Chaotic Evil",
         env=(ENV_ETERNAL_STEPPE_BURROW + "; scattered Flamewarg "
              "cell-leaders across Infinite Desert"),
         org="solitary (with 6-10 flamewarg cultists)",
         abilities={"Str": 10, "Dex": 14, "Con": 12, "Int": 13,
                    "Wis": 11, "Cha": 19},
         init=2, speed={"land": 30},
         attacks=[{"type": "flaming scimitar +1", "bonus": 4,
                   "damage": "1d6+1 plus 1d6 fire"}],
         spec_atk=["Fireball 2/day (6d6)",
                   "Scorching Ray at will",
                   "Flaming Sphere 3/day",
                   "Charm Person (DC 16) 3/day"],
         spec_qual=["Faintly luminous eyes in low light",
                    "Fire resistance 5 (heritage)",
                    "Spells/day: 0th -- 6; 1st -- 7; 2nd -- 6; 3rd -- 4",
                    "+2 racial to Bluff"],
         feats=["Spell Focus (evocation)", "Combat Casting",
                "Silent Spell"],
         skills={"Bluff": 15, "Concentration": 10, "Diplomacy": 7,
                 "Intimidate": 8, "Spellcraft": 10},
         saves={"Fort": 3, "Ref": 4, "Will": 5},
         flags=["half_domnathar", "hostile", "caster", "cultist", "boss"],
         desc=("A tall figure in ember-stitched robes, her voice warm "
               "enough to win a crowd and her eyes hot enough to burn "
               "dissenters out of it. Her grandfather was a Dómnathar "
               "captain.")),

    make(10324, "Half-Dómnathar Artifact-Keeper (Wizard 6)",
         cr=8, level=6, hp_dice=[6, 4, 6], ac=15, dmg_dice=[1, 6, 0],
         type_="Humanoid", alignment="Neutral Evil",
         env="Kinsweave (Highridge lava-tube artifact chambers; buried "
             "artifact sites across the Six Kings' ruins)",
         org="solitary (with 2-3 dark dwarf fireforged)",
         abilities={"Str": 10, "Dex": 13, "Con": 12, "Int": 18,
                    "Wis": 13, "Cha": 12},
         init=1, speed={"land": 30},
         attacks=[{"type": "staff of fire", "bonus": 4,
                   "damage": "1d6 plus charges (3 charges/day burning hands)"}],
         spec_atk=["Fireball 2/day (6d6)", "Scorching Ray 3/day",
                   "Dispel Magic 2/day", "Haste (self) 1/day"],
         spec_qual=["Faintly luminous eyes",
                    "Spells/day: 0th -- 5; 1st -- 6; 2nd -- 5; 3rd -- 4",
                    "Specialization: Transmutation",
                    "+3 Kn (arcana) for artifact identification"],
         feats=["Scribe Scroll", "Craft Wondrous Item",
                "Spell Focus (evocation)", "Spell Focus (transmutation)"],
         skills={"Appraise": 10, "Concentration": 10,
                 "Decipher Script": 13, "Disguise": 5,
                 "Knowledge (arcana)": 16, "Knowledge (history)": 14,
                 "Spellcraft": 16},
         saves={"Fort": 3, "Ref": 3, "Will": 6},
         flags=["half_domnathar", "hostile", "caster", "boss"],
         desc=("A scholar who passes in Kinsweave society as a visiting "
               "Taraf-Imro forge-adept. She has done so for twelve years "
               "and her cover has never been questioned.")),

    make(10325, "Half-Dómnathar Battle-Priest (Cleric 7)",
         cr=9, level=7, hp_dice=[7, 8, 14], ac=21, dmg_dice=[1, 8, 2],
         type_="Humanoid", alignment="Lawful Evil",
         env="Deepwater Marches (Spur Tower command levels); Gatefall "
             "Fortress of Dorrach-Vel",
         org="solitary (with 4-6 silentborn loyalists)",
         abilities={"Str": 15, "Dex": 12, "Con": 14, "Int": 12,
                    "Wis": 17, "Cha": 13},
         init=1, speed={"land": 20},
         attacks=[{"type": "warhammer +2", "bonus": 10,
                   "damage": "1d8+4"}],
         spec_atk=["Inflict Serious Wounds 2/day (3d8+7)",
                   "Flame Strike 1/day (7d6)",
                   "Searing Light 3/day",
                   "Rebuke Undead 6/day"],
         spec_qual=["Faintly luminous eyes",
                    "Spells/day: 0th -- 6; 1st -- 5+1; 2nd -- 4+1; "
                    "3rd -- 3+1; 4th -- 2+1",
                    "Domains: War, Destruction"],
         feats=["Combat Casting", "Power Attack",
                "Weapon Focus (warhammer)", "Spell Penetration"],
         skills={"Concentration": 12, "Knowledge (religion)": 11,
                 "Spellcraft": 11},
         saves={"Fort": 7, "Ref": 3, "Will": 9},
         flags=["half_domnathar", "hostile", "caster", "boss"],
         desc=("A Half-Dómnathar in blackened full plate, the chapter-"
               "priest of the Spur Tower's war-temple. His prayers call "
               "on an absence rather than a presence.")),

    make(10326, "Half-Dómnathar Mother-Superior (Cleric 8)",
         cr=9, level=8, hp_dice=[8, 8, 8], ac=19, dmg_dice=[1, 6, 1],
         type_="Humanoid", alignment="Lawful Evil",
         env="Eternal Steppe (Second Breath Hideout); Deepwater Spur Tower",
         org="solitary (with 6-8 silentborn and 2-3 dark dwarf attendants)",
         abilities={"Str": 11, "Dex": 12, "Con": 13, "Int": 15,
                    "Wis": 19, "Cha": 16},
         init=1, speed={"land": 30},
         attacks=[{"type": "mace of silence +1", "bonus": 7,
                   "damage": "1d6+1 plus silence for 1 round"}],
         spec_atk=["Summon Monster IV 2/day",
                   "Hold Person 2/day (DC 17)",
                   "Silence 2/day",
                   "Dispel Magic 2/day"],
         spec_qual=["Faintly luminous eyes",
                    "Spells/day: 0th -- 6; 1st -- 5+1; 2nd -- 5+1; "
                    "3rd -- 4+1; 4th -- 3+1; 5th -- 2+1",
                    "Domains: Knowledge, Protection"],
         feats=["Combat Casting", "Skill Focus (Heal)", "Leadership",
                "Craft Wondrous Item"],
         skills={"Concentration": 12, "Diplomacy": 14, "Heal": 15,
                 "Knowledge (arcana)": 10, "Knowledge (religion)": 15,
                 "Sense Motive": 15, "Spellcraft": 13},
         saves={"Fort": 7, "Ref": 3, "Will": 11},
         flags=["half_domnathar", "hostile", "caster", "boss"],
         desc=("A stern matriarch with grey-streaked hair coiled under a "
               "circle of iron. She rebuilds the breeding program the "
               "Kin thought they burned, and she tells herself the "
               "children will one day thank her.")),

    make(10327, "Half-Dómnathar Philosopher (Bard 8)",
         cr=10, level=8, hp_dice=[8, 6, 8], ac=18, dmg_dice=[1, 6, 1],
         type_="Humanoid", alignment="Neutral Evil",
         env="Twin Rivers (Unstrung Philosophers' Refuge in Riverwind Heights)",
         org="solitary (teaching a class of 4-8 Unstrung cultists)",
         abilities={"Str": 10, "Dex": 14, "Con": 13, "Int": 16,
                    "Wis": 13, "Cha": 20},
         init=2, speed={"land": 30},
         attacks=[{"type": "rapier +2", "bonus": 9, "damage": "1d6+2"}],
         spec_atk=["Bardic Music 8/day",
                   "Charm Person (DC 16, 3/day)",
                   "Suggestion (DC 17, 2/day)",
                   "Dominate Person (DC 19, 1/day)"],
         spec_qual=["Faintly luminous eyes",
                    "Spells/day: 0th -- 3; 1st -- 4; 2nd -- 4; 3rd -- 3",
                    "Bardic Knowledge +14",
                    "Lore Mastery: any Kn roll vs DC 20 is free info"],
         feats=["Persuasive", "Negotiator", "Skill Focus (Diplomacy)",
                "Silent Spell"],
         skills={"Bluff": 18, "Decipher Script": 12, "Diplomacy": 20,
                 "Gather Information": 16, "Knowledge (arcana)": 14,
                 "Knowledge (history)": 14, "Perform (oratory)": 18,
                 "Sense Motive": 14, "Spellcraft": 14},
         saves={"Fort": 3, "Ref": 8, "Will": 8},
         flags=["half_domnathar", "hostile", "caster", "boss"],
         desc=("A speaker whose voice most people would listen to "
               "regardless of content. He teaches the Deceiver's Feat "
               "as philosophy -- 'the power others would prefer you "
               "did not have' -- and his students do not always "
               "know whose feet they are sitting at.")),

    make(10328, "Half-Dómnathar Expedition-Leader (Fighter 6 / Sorcerer 3)",
         cr=11, level=9, hp_dice=[9, 8, 18], ac=21, dmg_dice=[1, 10, 4],
         type_="Humanoid", alignment="Lawful Evil",
         env="Kinsweave (Andrio Giant Chamber expedition camp)",
         org="solitary (with 4 silentborn, 3 dark dwarves, 8 goblin porters)",
         abilities={"Str": 18, "Dex": 13, "Con": 15, "Int": 13,
                    "Wis": 12, "Cha": 15},
         init=1, speed={"land": 30},
         attacks=[{"type": "greatsword +1", "bonus": 14,
                   "damage": "2d6+7"}],
         spec_atk=["Power Attack", "Cleave", "Great Cleave",
                   "Burning Hands 4/day (3d4)",
                   "Magic Missile 5/day (2 missiles)",
                   "Shield 4/day"],
         spec_qual=["Faintly luminous eyes",
                    "Spells/day: 0th -- 6; 1st -- 6",
                    "+2 racial bonus to Diplomacy/Bluff",
                    "Fire resistance 5"],
         feats=["Power Attack", "Cleave", "Great Cleave",
                "Weapon Focus (greatsword)",
                "Weapon Specialization (greatsword)",
                "Combat Casting", "Leadership"],
         skills={"Bluff": 8, "Climb": 11, "Diplomacy": 6,
                 "Intimidate": 13, "Knowledge (history)": 6,
                 "Spellcraft": 5},
         saves={"Fort": 8, "Ref": 4, "Will": 6},
         flags=["half_domnathar", "hostile", "caster", "boss"],
         desc=("A powerfully-built Half-Dómnathar with a sword-scar across "
               "his chin and the bearing of a man who has buried his "
               "subordinates. He leads the Andrio expedition with a "
               "commander's touch and a scholar's patience.")),

    make(10329, "Half-Dómnathar Research-Sorcerer (Wizard 10)",
         cr=12, level=10, hp_dice=[10, 4, 10], ac=17, dmg_dice=[1, 4, 0],
         type_="Humanoid", alignment="Lawful Evil",
         env="Infinite Desert (Fusion-Cell Outpost under the Glass Wastes)",
         org="solitary (with 4 silentborn researchers and 2 dark dwarf smiths)",
         abilities={"Str": 9, "Dex": 13, "Con": 13, "Int": 20,
                    "Wis": 14, "Cha": 14},
         init=1, speed={"land": 30},
         attacks=[{"type": "staff of dismissal +1", "bonus": 4,
                   "damage": "1d6"}],
         spec_atk=["Fireball 3/day (10d6)",
                   "Cone of Cold 1/day (10d6)",
                   "Dimension Door 2/day",
                   "Wall of Fire 1/day",
                   "Summon Monster V 2/day"],
         spec_qual=["Faintly luminous eyes",
                    "Spells/day: 0th -- 4; 1st -- 5+1; 2nd -- 5+1; "
                    "3rd -- 4+1; 4th -- 4+1; 5th -- 3+1",
                    "Specialization: Evocation (opposed: Necromancy, "
                    "Enchantment)"],
         feats=["Scribe Scroll", "Craft Wondrous Item", "Craft Rod",
                "Spell Focus (evocation)",
                "Greater Spell Focus (evocation)",
                "Empower Spell", "Maximize Spell"],
         skills={"Concentration": 14, "Decipher Script": 18,
                 "Knowledge (arcana)": 18, "Knowledge (history)": 15,
                 "Knowledge (the planes)": 15, "Spellcraft": 22},
         saves={"Fort": 4, "Ref": 4, "Will": 9},
         flags=["half_domnathar", "hostile", "caster", "boss"],
         desc=("A researcher with burn-scars crossing his hands and wrists, "
               "devoted to re-creating the Deceiver fusion-magic that "
               "melted the glass of the Wastes. He is brilliant, reserved, "
               "and patient. Give him five more years and he will "
               "succeed.")),
]


# ---------------------------------------------------------------------------
# DÓMNATHAR PROPER -- vnums 10330-10335
# ---------------------------------------------------------------------------

DOMNATHAR: List[Dict[str, Any]] = [
    make(10330, "Dómnathar Infiltrator (Rogue 6 / Fighter 2)",
         cr=8, level=8, hp_dice=[8, 6, 8], ac=18, dmg_dice=[1, 6, 2],
         type_="Humanoid (Dómnathar)", alignment="Lawful Evil",
         env=("Gatefall Reach (Silence Breach approaches, Fortress of "
              "Dorrach-Vel command); Deepwater Spur Tower outer"),
         org="solitary",
         abilities={"Str": 14, "Dex": 18, "Con": 13, "Int": 15,
                    "Wis": 13, "Cha": 14},
         init=4, speed={"land": 30},
         attacks=[{"type": "+2 short sword", "bonus": 11,
                   "damage": "1d6+4"},
                  {"type": "+1 dagger (off-hand)", "bonus": 9,
                   "damage": "1d4+2"}],
         spec_atk=["Sneak Attack +3d6",
                   "Poison use (DC 14, 1d4 Con/1d4 Con)"],
         spec_qual=[KIN_SENSE_SILENCE, DARKVISION_120,
                    "Trapfinding", "Evasion", "Uncanny Dodge",
                    "Trap sense +2",
                    "Light sensitivity (dazzled in bright sunlight)"],
         feats=["Weapon Finesse", "Two-Weapon Fighting",
                "Improved Two-Weapon Fighting", "Improved Initiative",
                "Dodge", "Mobility"],
         skills={"Bluff": 13, "Diplomacy": 5, "Disguise": 13,
                 "Hide": 15, "Move Silently": 15,
                 "Open Lock": 11, "Spot": 12},
         saves={"Fort": 5, "Ref": 10, "Will": 4},
         flags=["domnathar", "hostile", "kin_silent", "boss"],
         desc=("A tall, slender figure with skin the color of wet slate "
               "and eyes that catch the torchlight at an odd angle. His "
               "ears are so pointed they look sculpted. He has been "
               "killing Kin officers since the War and has not aged a day.")),

    make(10331, "Dómnathar Remnant-Officer (Fighter 7)",
         cr=9, level=7, hp_dice=[7, 10, 14], ac=22, dmg_dice=[1, 10, 4],
         type_="Humanoid (Dómnathar)", alignment="Lawful Evil",
         env=ENV_TIDEBLOOM_HIDDEN + "; Deepwater Spur Tower",
         org="solitary or enclave-leader (with 6-8 half-domnathar)",
         abilities={"Str": 18, "Dex": 14, "Con": 16, "Int": 13,
                    "Wis": 12, "Cha": 13},
         init=2, speed={"land": 30},
         attacks=[{"type": "+2 longsword", "bonus": 13,
                   "damage": "1d8+6"}],
         spec_atk=["Power Attack", "Cleave", "Great Cleave"],
         spec_qual=[KIN_SENSE_SILENCE, DARKVISION_120,
                    "Light sensitivity"],
         feats=["Power Attack", "Cleave", "Great Cleave",
                "Weapon Focus (longsword)",
                "Weapon Specialization (longsword)",
                "Greater Weapon Focus (longsword)",
                "Improved Initiative"],
         skills={"Climb": 10, "Diplomacy": 5, "Intimidate": 9,
                 "Listen": 6, "Sense Motive": 6, "Spot": 6},
         saves={"Fort": 8, "Ref": 4, "Will": 3},
         flags=["domnathar", "hostile", "kin_silent", "boss"],
         desc=("A Dómnathar officer who has hidden among Kin for three "
               "hundred years. His insignia-of-rank is a small iron "
               "disc worn inside the cheek so that no Kin will ever see "
               "it.")),

    make(10332, "Dómnathar Sorcerer (Sorcerer 8)",
         cr=10, level=8, hp_dice=[8, 4, 16], ac=18, dmg_dice=[1, 4, 0],
         type_="Humanoid (Dómnathar)", alignment="Lawful Evil",
         env="Deepwater Spur Tower; Gatefall deep tunnels",
         org="solitary",
         abilities={"Str": 10, "Dex": 14, "Con": 14, "Int": 15,
                    "Wis": 13, "Cha": 20},
         init=2, speed={"land": 30},
         attacks=[{"type": "+2 quarterstaff", "bonus": 6,
                   "damage": "1d6+2"}],
         spec_atk=["Fireball 3/day (8d6)",
                   "Lightning Bolt 2/day (8d6)",
                   "Haste 2/day", "Hold Person 3/day (DC 17)",
                   "Dispel Magic 3/day"],
         spec_qual=[KIN_SENSE_SILENCE, DARKVISION_120, VOID_RESONANCE,
                    "Light sensitivity",
                    "Spells/day: 0th -- 6; 1st -- 7; 2nd -- 7; "
                    "3rd -- 7; 4th -- 5"],
         feats=["Spell Focus (evocation)", "Greater Spell Focus (evocation)",
                "Empower Spell", "Combat Casting",
                "Silent Spell"],
         skills={"Bluff": 16, "Concentration": 13, "Diplomacy": 8,
                 "Intimidate": 12, "Knowledge (arcana)": 13,
                 "Spellcraft": 13},
         saves={"Fort": 4, "Ref": 4, "Will": 7},
         flags=["domnathar", "hostile", "caster", "kin_silent", "boss"],
         desc=("A Dómnathar caster whose spell-focus is a small blank "
               "glass sphere she carries on a silver chain. When she "
               "casts, the sphere fills with black smoke for a moment "
               "and then clears.")),

    make(10333, "Dómnathar Void-Construct",
         cr=11, level=10, hp_dice=[10, 10, 30], ac=24, dmg_dice=[2, 6, 5],
         type_="Construct", alignment="Always Neutral",
         env="Deepwater Spur Tower (command levels); Gatefall deep; "
             "Infinite Desert Fusion-Cell",
         org="solitary (as guard-construct)",
         abilities={"Str": 22, "Dex": 10, "Con": None,
                    "Int": None, "Wis": 11, "Cha": 1},
         init=0, speed={"land": 30},
         attacks=[{"type": "slam (×2)", "bonus": 15,
                   "damage": "2d6+6 plus 1d6 cold"}],
         spec_atk=["Cold slam (bypasses fire resistance)",
                   "Silence aura (30 ft, DC 15 Will or silenced)"],
         spec_qual=["Construct traits (immune mind-affecting, "
                    "fortification 50%, no Con)",
                    KIN_SENSE_SILENCE,
                    "Damage reduction 5/adamantine",
                    "Spell resistance 19",
                    "Magic immunity (except cold and acid)",
                    DARKVISION_120],
         feats=["Power Attack", "Cleave", "Improved Bull Rush"],
         skills={},
         saves={"Fort": 3, "Ref": 3, "Will": 4},
         flags=["construct", "domnathar", "hostile", "boss"],
         desc=("A man-shaped husk of grey-veined obsidian, eight feet "
               "tall, built around a core of absolutely empty air "
               "where most creatures would have breath. It moves in "
               "total silence even when it runs.")),

    make(10334, "Dómnathar Void-Sorcerer (Sorcerer 12)",
         cr=14, level=12, hp_dice=[12, 4, 24], ac=20, dmg_dice=[1, 4, 0],
         type_="Humanoid (Dómnathar)", alignment="Lawful Evil",
         env="Deepwater Spur Tower Void Chamber",
         org="solitary (with 1 void-construct and 4 silentborn guards)",
         abilities={"Str": 10, "Dex": 14, "Con": 14, "Int": 16,
                    "Wis": 14, "Cha": 22},
         init=2, speed={"land": 30},
         attacks=[{"type": "+3 quarterstaff of silence", "bonus": 9,
                   "damage": "1d6+3 plus silence on target 1 round"}],
         spec_atk=["Meteor Swarm 1/day (24d6 scattered)",
                   "Disintegrate 2/day (DC 22)",
                   "Greater Dispel Magic 3/day",
                   "Wall of Force 2/day",
                   "Dominate Person 2/day (DC 19)"],
         spec_qual=[KIN_SENSE_SILENCE, DARKVISION_120, VOID_RESONANCE,
                    "Light sensitivity",
                    "Spells/day: 0th -- 6; 1st -- 7; 2nd -- 7; "
                    "3rd -- 7; 4th -- 7; 5th -- 6; 6th -- 4",
                    "Aura of Silence: 10-ft radius of Silence spell, "
                    "will (DC 20)"],
         feats=["Spell Focus (evocation)",
                "Greater Spell Focus (evocation)",
                "Spell Focus (enchantment)",
                "Empower Spell", "Maximize Spell", "Silent Spell",
                "Combat Casting"],
         skills={"Bluff": 20, "Concentration": 17, "Diplomacy": 12,
                 "Intimidate": 16, "Knowledge (arcana)": 18,
                 "Knowledge (the planes)": 15, "Spellcraft": 20},
         saves={"Fort": 6, "Ref": 6, "Will": 10},
         flags=["domnathar", "hostile", "caster", "kin_silent", "boss"],
         desc=("A Dómnathar sorceress whose skin has the faint sheen of "
               "something submerged, whose eyes glow a muted yellow-green "
               "in any light less than noon-sun. Her voice is "
               "surprisingly kind.")),

    make(10335, "Dómnathar House Leader (Sorcerer 15 / Fighter 2)",
         cr=17, level=17, hp_dice=[17, 4, 51], ac=25, dmg_dice=[1, 8, 4],
         type_="Humanoid (Dómnathar)", alignment="Lawful Evil",
         env="Deepwater Marches (Spur Tower throne level)",
         org="unique (the last living pre-invasion House Leader)",
         abilities={"Str": 16, "Dex": 16, "Con": 18, "Int": 18,
                    "Wis": 16, "Cha": 24},
         init=3, speed={"land": 30},
         attacks=[{"type": "+3 longsword of void-edge", "bonus": 17,
                   "damage": "1d8+7 plus 1d6 Wis drain"}],
         spec_atk=["Time Stop 1/day",
                   "Meteor Swarm 2/day (24d6)",
                   "Gate 1/day", "Power Word Stun 1/day",
                   "Dominate Person 3/day (DC 20)",
                   "Horrid Wilting 1/day (DC 23, 17d6)"],
         spec_qual=[KIN_SENSE_SILENCE, DARKVISION_120, VOID_RESONANCE,
                    "Light sensitivity",
                    "Spells/day: 0th -- 6; 1st -- 8; 2nd -- 8; 3rd -- 8; "
                    "4th -- 7; 5th -- 7; 6th -- 7; 7th -- 6; 8th -- 3",
                    "Master of House: all Dómnathar within 60 ft gain "
                    "+2 morale to attack, save, and skill checks",
                    "Pre-Invasion Blessing: heals 10 HP per round as long "
                    "as the Spur Tower's Void Chamber is intact",
                    "Spell resistance 23"],
         feats=["Power Attack", "Cleave", "Weapon Focus (longsword)",
                "Spell Focus (evocation)",
                "Greater Spell Focus (evocation)",
                "Empower Spell", "Maximize Spell", "Quicken Spell",
                "Silent Spell", "Still Spell",
                "Craft Staff", "Craft Wondrous Item",
                "Spell Penetration", "Greater Spell Penetration"],
         skills={"Bluff": 27, "Concentration": 24, "Diplomacy": 18,
                 "Intimidate": 22, "Knowledge (arcana)": 24,
                 "Knowledge (history)": 20,
                 "Knowledge (the planes)": 20, "Spellcraft": 24,
                 "Spot": 20},
         saves={"Fort": 12, "Ref": 10, "Will": 15},
         flags=["domnathar", "hostile", "caster", "kin_silent",
                "boss", "legendary"],
         desc=("He is four hundred and eighty-seven years old and has not "
               "changed in four hundred of them. He remembers the "
               "Scattering the way most Kin remember last summer. He was "
               "a general once; he remains a general now. His name is "
               "not spoken by his servants, and he does not remember "
               "what his mother called him.")),
]


# ---------------------------------------------------------------------------
# Merge & write
# ---------------------------------------------------------------------------

ALL_NEW = KOBOLDS + GOBLINOIDS + DARK_DWARVES + SILENTBORN + HALF_DOMNATHAR + DOMNATHAR


def main() -> int:
    path = os.path.join(DATA, "mobs_bestiary.json")
    with open(path, "r", encoding="utf-8") as f:
        bestiary = json.load(f)
    existing = {b.get("vnum") for b in bestiary}

    added = 0
    by_group = {}
    for entry in ALL_NEW:
        if entry["vnum"] in existing:
            continue
        bestiary.append(entry)
        added += 1
        grp = entry["name"].split()[0]
        by_group[grp] = by_group.get(grp, 0) + 1

    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(bestiary, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

    print(f"Added {added} new bestiary entries (total now {len(bestiary)}).")
    for grp, n in sorted(by_group.items()):
        print(f"  {grp:20s} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
