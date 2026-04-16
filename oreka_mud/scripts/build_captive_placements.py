"""Place 15 family-representative NPCs in their home rooms + 6 exemplar
captives in Deceiver zones, and register captive-family linkage on them.

After running, the captive loop works end-to-end with real NPCs:

    player kills captors → frees captive → receives token
    → travels to named town → `present <token>` → family NPC pays out

Idempotent by vnum. Run:
    python scripts/build_captive_placements.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


# ---------------------------------------------------------------------------
# 15 family representative NPCs -- vnums 4300-4314
# ---------------------------------------------------------------------------

def _family_npc(vnum: int, name: str, room_vnum: int,
                description: str, faction_id: str) -> Dict[str, Any]:
    return {
        "vnum": vnum,
        "name": name,
        "level": 6,
        "hp_dice": [6, 8, 18],
        "ac": 14,
        "damage_dice": [1, 6, 1],
        "flags": ["nonaggressive", "quest_giver", "family_rep"],
        "type_": "Humanoid",
        "alignment": "Neutral Good",
        "ability_scores": {
            "Str": 12, "Dex": 11, "Con": 13,
            "Int": 13, "Wis": 14, "Cha": 13
        },
        "initiative": 0,
        "speed": {"land": 30},
        "attacks": [{"type": "quarterstaff", "bonus": 4,
                     "damage": "1d6+1"}],
        "special_attacks": [],
        "special_qualities": [],
        "feats": [],
        "skills": {"Diplomacy": 8, "Sense Motive": 7},
        "saves": {"Fort": 4, "Ref": 2, "Will": 5},
        "environment": f"{faction_id} representative",
        "organization": "solitary",
        "cr": 3,
        "advancement": "-",
        "description": description,
        "room_vnum": room_vnum,
        "loot_table": []
    }


FAMILY_NPCS: List[Dict[str, Any]] = [
    _family_npc(4300, "Matriarch Vessla Ridgeborn", 7006,
                "A lean Mytroan woman with silver-streaked braids and the "
                "upright bearing of a lifelong horse-master. Her eyes "
                "miss nothing; her silences say more than her words.",
                "far_riders"),
    _family_npc(4301, "Clan-Speaker Morrek Gharoz", 8003,
                "A broad-shouldered Pekakarlik dwarf with a beard threaded "
                "with small iron tally-rings, one for each clan oath kept. "
                "He moves slowly and speaks with deliberate weight.",
                "sand_wardens"),
    _family_npc(4302, "Grandfather Sarn Oathbond", 12109,
                "An old hill-rider whose hands bear the calluses of fifty "
                "years of reins. He sits more than he stands now, but his "
                "voice still carries across the Hollow.",
                "far_riders"),
    _family_npc(4303, "Factor Iralia Vaelun", 10220,
                "A sharp-eyed Eruskan woman in merchant's fine wool, a "
                "cedar scroll-tube at her belt. House Vaelun has traded "
                "the river for three generations under her line.",
                "trade_houses"),
    _family_npc(4304, "Archivist Calren Vos", 4049,
                "A bookish Eruskan in scholar's robes, his thumbs "
                "permanently stained dark from a lifetime of ink. He "
                "speaks quietly and remembers everything.",
                "trade_houses"),
    _family_npc(4305, "Shieldfather Harn Kovaka", 6075,
                "An imposing Pasua warrior with a weathered staff of "
                "black-oak propped beside his chair. The Kovaka "
                "Shieldhearth has stood five generations in Velathenor.",
                "circle_of_deeproot"),
    _family_npc(4306, "Elder Naerin Silverleaf", 9245,
                "A Pasua elder in simple robes of undyed linen, her hair "
                "bound in the two-strand knot of Canopy Hold's senior "
                "speakers. She rarely raises her voice and never needs to.",
                "circle_of_deeproot"),
    _family_npc(4307, "Forge-Mother Kharaz Fireforge", 5108,
                "A stout Taraf-Imro dwarf woman whose arms are scarred "
                "with old burns from a lifetime at the forge. She wears "
                "a smith's leather apron even in council.",
                "brotherhood_of_steppe"),
    _family_npc(4308, "Keeper Sunwend Dalan", 7110,
                "A tall Mytroan man with sun-dark skin and the braided "
                "beard of a hold-keeper. He keeps a tally-string at his "
                "belt with small knots for every rider sent out.",
                "brotherhood_of_steppe"),
    _family_npc(4309, "Guildmaster Henna Briarshade", 12143,
                "A brisk, businesslike Eruskan woman in practical working "
                "clothes, her hands quick and her accounting sharper. She "
                "runs the Briarshade trade-circle with iron fairness.",
                "trade_houses"),
    _family_npc(4310, "Captain Vaerd of the Chainless", 13005,
                "A scarred Farborn veteran in plain sea-traveler's clothes, "
                "the double-chain sigil of the Chainless Legion tattooed "
                "across his knuckles. He speaks like a man accustomed to "
                "command.",
                "chainless_legion"),
    _family_npc(4311, "Concord Agent Sevren", 4139,
                "A quiet figure in dark traveling clothes, unremarkable at "
                "a glance. Close inspection reveals faintly luminous "
                "yellow-green eyes and deliberately-rounded ears. He is "
                "Half-Dómnathar, and he is not apologizing for it.",
                "silent_concord"),
    _family_npc(4312, "Warden-Elder Morun", 12245,
                "An ancient Mytroan in a cloak of Tomb-weave, his eyes "
                "milky with age but his hearing perfect. He keeps watch "
                "over the colonnade approaches to the Tomb.",
                "gatefall_remnant"),
    _family_npc(4313, "Circle-Speaker Lirien Thorn-Ear", 6117,
                "A Pasua with the elongated, thorn-scarred ears of her "
                "particular Tidebloom circle. She speaks softly and "
                "laughs rarely, but when she does, the whole Hollow "
                "hears it.",
                "circle_of_deeproot"),
    _family_npc(4314, "Firemother Zhareni", 8125,
                "A dark-skinned Rarozhki dwarf whose robes smell "
                "permanently of volcanic ash. The Ashgarin Fold's oldest "
                "living Firemother, she knows every fold-kin by name.",
                "sand_wardens"),
]


# ---------------------------------------------------------------------------
# 6 exemplar captives placed in existing Deceiver zones
# ---------------------------------------------------------------------------

def _captive(vnum: int, name: str, room_vnum: int, description: str,
             family_id: str, template_id: str,
             captor_type: str,
             rescue_type: str = "token_bearer") -> Dict[str, Any]:
    return {
        "vnum": vnum,
        "name": name,
        "level": 2,
        "hp_dice": [2, 8, 4],
        "ac": 10,
        "damage_dice": [1, 3, 0],
        "flags": ["captive", "nonaggressive", "quest_giver"],
        "type_": "Humanoid",
        "alignment": "Neutral Good",
        "ability_scores": {
            "Str": 10, "Dex": 10, "Con": 11,
            "Int": 11, "Wis": 11, "Cha": 10
        },
        "initiative": 0,
        "speed": {"land": 30},
        "attacks": [],
        "special_attacks": [],
        "special_qualities": [],
        "feats": [],
        "skills": {},
        "saves": {"Fort": 1, "Ref": 0, "Will": 1},
        "environment": f"Captive of {captor_type}",
        "organization": "solitary captive",
        "cr": None,
        "advancement": "-",
        "description": description,
        "room_vnum": room_vnum,
        "loot_table": [],
        "captive_family": family_id,
        "captive_template": template_id,
        "captive_captor_type": captor_type,
        "captive_state": "bound",
        "rescue_type": rescue_type
    }


EXEMPLAR_CAPTIVES: List[Dict[str, Any]] = [
    _captive(4315,
             "The chained Pekakarlik translator",
             8268,
             "A stocky Pekakarlik dwarf with a short silver beard and a "
             "heavy iron collar clamped around her neck. Her wrists are "
             "scabbed and her fingers are stained with reagent-ink. When "
             "she sees you are not a kobold, her shoulders sag in "
             "exhausted relief.",
             "pekakarlik_gharoz", "scholar", "kobold scavengers",
             rescue_type="homesick"),
    _captive(4316,
             "The bound Wind-Rider scout",
             12258,
             "A young Pasua woman with her braid cut ragged at the scalp "
             "-- kobold work, done to humiliate. Her arms are tied behind "
             "her back. She stiffens when you enter; when she recognizes "
             "you are not a captor, her eyes fill with a fierce, "
             "desperate hope.",
             "ridgeborn_kin", "scout", "Scald-Tongue kobolds",
             rescue_type="quest_giver"),
    _captive(4317,
             "The caged Mytroan herder",
             6257,
             "A wiry middle-aged Mytroan man in the plain working clothes "
             "of a steppe herder, bound in the raider camp's iron cage. "
             "His lip is split and one eye is swollen shut. He has been "
             "expecting rescue but hoping for it less each day.",
             "tidebloom_myruvane", "farmer", "goblin raiders",
             rescue_type="token_bearer"),
    _captive(4318,
             "The captive Elf scholar",
             9387,
             "An Elf in worn but clean scholar's robes, his ankles shackled "
             "with a chain long enough to reach his desk and his bed but "
             "not the door. He has been here eleven years. He lowers his "
             "book carefully and waits, unsure whether to trust this.",
             "custos_scholar", "scholar", "Dómnathar of the Spur Tower",
             rescue_type="leader"),
    _captive(4319,
             "The cage-bound steppe herder",
             7253,
             "A young Mytroan in a Flamewarg-cultist's cage, his "
             "wrists chafed raw from the lashings. The cult keeps him for "
             "the next pyre. He watches you with the calm resignation of "
             "someone who had given up hope an hour before you arrived.",
             "steppe_dalan", "farmer", "Flamewarg cultists",
             rescue_type="self_rescue"),
    _captive(4320,
             "The captive arcanist",
             8284,
             "A human woman of middle years in the worn robes of a "
             "traveling mage, her hands red-raw from being forced to "
             "cast again and again. She is shackled to a stone block "
             "that cannot be moved. Her eyes meet yours without hope, "
             "which is itself a terrible thing to see.",
             "custos_scholar", "scholar", "Half-Dómnathar researchers",
             rescue_type="quest_giver"),
]


# ---------------------------------------------------------------------------
# Merge into mobs.json
# ---------------------------------------------------------------------------

def main() -> int:
    path = os.path.join(DATA, "mobs.json")
    with open(path, "r", encoding="utf-8") as f:
        mobs = json.load(f)
    existing = {m.get("vnum") for m in mobs}

    added_families = 0
    for npc in FAMILY_NPCS:
        if npc["vnum"] in existing:
            continue
        mobs.append(npc)
        existing.add(npc["vnum"])
        added_families += 1

    added_captives = 0
    for cap in EXEMPLAR_CAPTIVES:
        if cap["vnum"] in existing:
            continue
        mobs.append(cap)
        existing.add(cap["vnum"])
        added_captives += 1

    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(mobs, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

    print(f"Placements:")
    print(f"  +{added_families} family representative NPCs")
    print(f"  +{added_captives} exemplar captives in Deceiver zones")
    print(f"  mobs.json now has {len(mobs)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
