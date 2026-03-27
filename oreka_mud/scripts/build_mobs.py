#!/usr/bin/env python
"""Build the massive mob placement file for OrekaMUD3."""
import json
import copy
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load bestiary
with open('oreka_mud/data/mobs_bestiary.json', 'r', encoding='utf-8') as f:
    bestiary = json.load(f)
bestiary_by_vnum = {m['vnum']: m for m in bestiary}

# Load current mobs
with open('oreka_mud/data/mobs.json', 'r', encoding='utf-8') as f:
    current_mobs = json.load(f)

# Load all area rooms
areas_list = [
    'Chapel', 'TwinRivers', 'CustosDoAeternos', 'Kinsweave',
    'TidebloomReach', 'EternalSteppe', 'InfiniteDesert',
    'DeepwaterMarches', 'GatefallReach', 'WildernessConnectors'
]
all_room_vnums = set()
room_lookup = {}
for area in areas_list:
    with open(f'oreka_mud/data/areas/{area}.json', 'r', encoding='utf-8') as f:
        rooms = json.load(f)
    for r in rooms:
        all_room_vnums.add(r['vnum'])
        room_lookup[r['vnum']] = {
            'area': area,
            'name': r['name'],
            'flags': r.get('flags', [])
        }

new_mobs = []
next_dup_vnum = 20001


def place_bestiary_mob(vnum, room_vnum):
    """Place a bestiary creature in a room (using original vnum)."""
    if room_vnum not in all_room_vnums:
        print(f"WARNING: room {room_vnum} does not exist for bestiary {vnum}")
        return None
    if vnum not in bestiary_by_vnum:
        print(f"WARNING: bestiary vnum {vnum} not found")
        return None
    mob = copy.deepcopy(bestiary_by_vnum[vnum])
    mob['room_vnum'] = room_vnum
    return mob


def place_bestiary_dup(vnum, room_vnum):
    """Place a DUPLICATE of a bestiary creature (new vnum)."""
    global next_dup_vnum
    if room_vnum not in all_room_vnums:
        print(f"WARNING: room {room_vnum} does not exist for dup of {vnum}")
        return None
    if vnum not in bestiary_by_vnum:
        print(f"WARNING: bestiary vnum {vnum} not found")
        return None
    mob = copy.deepcopy(bestiary_by_vnum[vnum])
    mob['vnum'] = next_dup_vnum
    mob['room_vnum'] = room_vnum
    next_dup_vnum += 1
    return mob


def add_mob(mob):
    if mob is not None:
        new_mobs.append(mob)


def make_npc(vnum, name, level, room_vnum, flags, alignment='Neutral Good',
             hp_dice=None, ac=12, dialogue=None, shop_inventory=None,
             shop_type=None, description=''):
    if room_vnum not in all_room_vnums:
        print(f"WARNING: room {room_vnum} does not exist for NPC {name}")
        return None
    if hp_dice is None:
        hp_dice = [level, 8, level * 2]
    npc = {
        'vnum': vnum,
        'name': name,
        'level': level,
        'hp_dice': hp_dice,
        'ac': ac,
        'damage_dice': [1, 4, 0],
        'flags': flags,
        'room_vnum': room_vnum,
        'type_': 'Humanoid',
        'alignment': alignment,
        'ability_scores': {
            'Str': 12, 'Dex': 12, 'Con': 12,
            'Int': 12, 'Wis': 12, 'Cha': 12
        },
        'initiative': 1,
        'speed': {'land': 30},
        'attacks': [{'type': 'fist', 'bonus': level, 'damage': '1d4'}],
        'special_attacks': [],
        'special_qualities': [],
        'feats': [],
        'skills': {},
        'saves': {
            'Fort': level // 2 + 1,
            'Ref': level // 3 + 1,
            'Will': level // 3 + 1
        },
        'environment': 'Town',
        'organization': 'Solitary',
        'cr': max(1, level // 2),
        'advancement': 'By character class',
        'description': description
    }
    if dialogue:
        npc['dialogue'] = dialogue
    if shop_inventory:
        npc['shop_inventory'] = shop_inventory
        npc['shop_type'] = shop_type or 'general'
        npc['buy_rate'] = 0.5
        npc['sell_rate'] = 1.2
    return npc


# ============================================================
# STEP 1: RELOCATE EXISTING 22 MOBS
# ============================================================

# Stone Golem (2001) -> Custos Crystal Spire Ground Floor
existing = copy.deepcopy(current_mobs[0])
existing['room_vnum'] = 4111
add_mob(existing)

# Water Elemental (2002) -> Custos Riverbank Landing
existing = copy.deepcopy(current_mobs[1])
existing['room_vnum'] = 4004
add_mob(existing)

# Mira the Shopkeeper (3000) -> Custos Central Market Square
existing = copy.deepcopy(current_mobs[2])
existing['room_vnum'] = 4062
add_mob(existing)

# Skip duplicate Water Elemental (index 3)

# Gentle Deer (2003) -> Twin Rivers Windweave Forest Road
existing = copy.deepcopy(current_mobs[4])
existing['room_vnum'] = 10435
add_mob(existing)

# Ape (2101) -> Deepwater Marches jungle
existing = copy.deepcopy(current_mobs[5])
existing['room_vnum'] = 9402
add_mob(existing)

# Baboon (2102) -> Deepwater Marches
existing = copy.deepcopy(current_mobs[6])
existing['room_vnum'] = 9409
add_mob(existing)

# Badger (2103) -> Twin Rivers wilderness
existing = copy.deepcopy(current_mobs[7])
existing['room_vnum'] = 10417
add_mob(existing)

# Bat (2104) -> Kinsweave ruins
existing = copy.deepcopy(current_mobs[8])
existing['room_vnum'] = 5200
add_mob(existing)

# Black Bear (2105) -> Twin Rivers forest
existing = copy.deepcopy(current_mobs[9])
existing['room_vnum'] = 10434
add_mob(existing)

# Brown Bear (2106) -> WildernessConnectors Giant's Teeth
existing = copy.deepcopy(current_mobs[10])
existing['room_vnum'] = 11012
add_mob(existing)

# Polar Bear (2107) -> Gatefall The Gap
existing = copy.deepcopy(current_mobs[11])
existing['room_vnum'] = 12200
add_mob(existing)

# Bison (2108) -> Eternal Steppe grassland
existing = copy.deepcopy(current_mobs[12])
existing['room_vnum'] = 7201
add_mob(existing)

# Boar (2109) -> Twin Rivers forest
existing = copy.deepcopy(current_mobs[13])
existing['room_vnum'] = 10430
add_mob(existing)

# Camel (2110) -> Infinite Desert road
existing = copy.deepcopy(current_mobs[14])
existing['room_vnum'] = 8301
add_mob(existing)

# Cat (2111) -> Custos city
existing = copy.deepcopy(current_mobs[15])
existing['room_vnum'] = 4136
add_mob(existing)

# Goble Test (2200) -> Chapel Dodger Street
existing = copy.deepcopy(current_mobs[16])
existing['room_vnum'] = 3012
add_mob(existing)

# Wolf (2300) -> Twin Rivers wilderness
existing = copy.deepcopy(current_mobs[17])
existing['room_vnum'] = 10421
add_mob(existing)

# Guildmaster Thorin (9001) -> Custos Adventurers' Guild
existing = copy.deepcopy(current_mobs[18])
existing['room_vnum'] = 4080
add_mob(existing)

# Banker Goldsworth (9002) -> Custos Trade House
existing = copy.deepcopy(current_mobs[19])
existing['room_vnum'] = 4065
add_mob(existing)

# Smith Ironforge (9003) -> Custos Weaponsmith's Hall
existing = copy.deepcopy(current_mobs[20])
existing['room_vnum'] = 4099
add_mob(existing)

# Merchant Lyssa (9004) -> Custos Golden Bazaar
existing = copy.deepcopy(current_mobs[21])
existing['room_vnum'] = 4063
add_mob(existing)

# ============================================================
# STEP 2: BESTIARY CREATURE PLACEMENTS
# ============================================================

# --- ETERNAL STEPPE (CR 2-6) ---
add_mob(place_bestiary_mob(10001, 7201))  # Abatwa -> Central Steppe Stretch
add_mob(place_bestiary_dup(10001, 7049))  # Abatwa -> Kavarn's Drift Outer Grass

add_mob(place_bestiary_mob(10004, 7208))  # Air Elemental Small -> Central Open Steppe
add_mob(place_bestiary_dup(10004, 10433))  # Air Elemental Small -> Singing Ridges Wind Lord's Terrace

add_mob(place_bestiary_mob(10005, 7228))  # Air Elemental Medium -> Varkhon Rise Central Ridge

add_mob(place_bestiary_mob(10012, 7202))  # Ankheg -> Wind Road Southern Passage
add_mob(place_bestiary_dup(10012, 7209))  # Ankheg -> Wind Road Southwest Approach

add_mob(place_bestiary_mob(10013, 7244))  # Annis Hag -> Steppe Eastern Transition Zone

add_mob(place_bestiary_mob(10020, 7203))  # Blink Dog -> Wind Road Eastern Margin
add_mob(place_bestiary_dup(10020, 7204))  # Blink Dog -> Wind Road Western Margin

add_mob(place_bestiary_mob(10026, 7059))  # Almas -> Zhoraven Ring Outer Perimeter
add_mob(place_bestiary_dup(10026, 7042))  # Almas -> Kavarn's Drift Perimeter Watch

add_mob(place_bestiary_mob(10040, 7207))  # Cockatrice -> Approach to Battlefield
add_mob(place_bestiary_dup(10040, 7071))  # Cockatrice -> Sylrek Camp Perimeter

add_mob(place_bestiary_mob(10032, 7241))  # Centaur -> Crescent Forest Northern Shieldwood
add_mob(place_bestiary_dup(10032, 7245))  # Centaur -> Steppe Northwestern Margin

add_mob(place_bestiary_mob(10060, 7226))  # Dire Lion -> Varkhon Rise Southern Approach

add_mob(place_bestiary_mob(10062, 7080))  # Dire Wolf -> Orthek's Stand Perimeter South
add_mob(place_bestiary_dup(10062, 7077))  # Dire Wolf -> Orthek's Stand Mountain Watch

add_mob(place_bestiary_mob(10073, 7205))  # Gnoll -> Wind Road Eastern Junction
add_mob(place_bestiary_dup(10073, 7206))  # Gnoll -> Wind Road Western Junction

add_mob(place_bestiary_mob(10075, 7219))  # Gorgon -> Dark Dawn Dead Zone Center

add_mob(place_bestiary_mob(10093, 7213))  # Impundulu -> Dark Dawn Central Zone

add_mob(place_bestiary_mob(10118, 7231))  # Manticore -> Varkhon Rise Western Slope

add_mob(place_bestiary_mob(10151, 7229))  # Pegasus -> Varkhon Rise Northern Summit

add_mob(place_bestiary_mob(10190, 7218))  # Skinwalker -> Dark Dawn Gilded Company Stand

add_mob(place_bestiary_mob(10196, 7233))  # Storm Wisp -> Varkhon Rise Southern Pass
add_mob(place_bestiary_dup(10196, 7227))  # Storm Wisp -> Varkhon Rise First Hill

add_mob(place_bestiary_mob(10231, 7090))  # Worg -> Veyla Crossing Outer Camp

add_mob(place_bestiary_mob(10230, 7242))  # Wolf -> Crescent Forest Shieldwood Interior
add_mob(place_bestiary_dup(10230, 7243))  # Wolf -> Crescent Forest Southern Shieldwood

add_mob(place_bestiary_mob(10229, 7225))  # Winter Wolf -> Burnt Hollows

add_mob(place_bestiary_mob(10206, 7049))  # Tokoloshe -> Kavarn's outer (already has abatwa dup, that's fine)

add_mob(place_bestiary_mob(10234, 7211))  # Yer-Sub -> Dark Dawn Western Edge

add_mob(place_bestiary_mob(10161, 7232))  # Poludnitsa -> Kavarn's Drift Northern Pastures

add_mob(place_bestiary_mob(10204, 7224))  # Thunderbird -> Dark Dawn Hawk Rider Position (boss)

# Dark Dawn Battlefield undead
add_mob(place_bestiary_mob(10189, 7212))  # Skeleton -> Dark Dawn Northern Perimeter
add_mob(place_bestiary_dup(10189, 7215))  # Skeleton -> Dark Dawn Southern Zone

add_mob(place_bestiary_mob(10238, 7214))  # Zombie -> Dark Dawn Eastern Flank
add_mob(place_bestiary_dup(10238, 7222))  # Zombie -> Dark Dawn Brotherhood Advance Line

add_mob(place_bestiary_mob(10227, 7216))  # Wight -> Dark Dawn Warg Kill Zone

# --- KINSWEAVE (CR 2-5) ---
add_mob(place_bestiary_mob(10010, 5202))  # Allip -> Mytro Ruins King's Ground
add_mob(place_bestiary_dup(10010, 5224))  # Allip -> Kalite Ruins King's Hall

add_mob(place_bestiary_mob(10016, 5305))  # Banshee -> Pryee Ruins Great Hall
add_mob(place_bestiary_dup(10016, 5282))  # Banshee -> Andrio Ruins Orean Quarter

add_mob(place_bestiary_mob(10014, 5430))  # Aranea -> Road to Mytro Ruins

add_mob(place_bestiary_mob(10179, 5203))  # Sand Wraith -> Mytro Ruins Eastern Sand
add_mob(place_bestiary_dup(10179, 5205))  # Sand Wraith -> Mytro Ruins Deepest Sand
add_mob(place_bestiary_dup(10179, 5263))  # Sand Wraith -> Thrush Ruins King's Forge

add_mob(place_bestiary_mob(10126, 5304))  # Mohrg -> Pryee Ruins Citadel Interior

add_mob(place_bestiary_mob(10129, 5286))  # Mummy -> Andrio Ruins Giant Chamber

add_mob(place_bestiary_mob(10183, 5222))  # Shadow -> Kalite Ruins Market Square
add_mob(place_bestiary_dup(10183, 5242))  # Shadow -> Hylen Ruins Central Ground

add_mob(place_bestiary_mob(10198, 5262))  # Svartalfar Shade -> Thrush Ruins Cold Smelter

add_mob(place_bestiary_mob(10127, 5240))  # Monstrous Spider -> Hylen Ruins Plain Approach
add_mob(place_bestiary_dup(10127, 5301))  # Monstrous Spider -> Pryee Ruins Outer Wall

add_mob(place_bestiary_mob(10232, 5264))  # Wraith -> Thrush Ruins Residential Quarter

add_mob(place_bestiary_mob(10053, 5040))  # Dryad -> Earthcircle Grove Entrance

add_mob(place_bestiary_dup(10189, 5201))  # Skeleton -> Mytro Ruins Market Ground
add_mob(place_bestiary_dup(10189, 5281))  # Skeleton -> Andrio Ruins Main Valley

add_mob(place_bestiary_dup(10238, 5221))  # Zombie -> Kalite Ruins Silted Docks
add_mob(place_bestiary_dup(10238, 5241))  # Zombie -> Hylen Ruins Outer Perimeter

add_mob(place_bestiary_mob(10052, 5442))  # Dread Wraith -> Lament of Kings (boss)

add_mob(place_bestiary_mob(10066, 5441))  # Earth Elemental Large -> Lament of Kings Blasted Plain

# --- TIDEBLOOM REACH (CR 2-5) ---
add_mob(place_bestiary_mob(10051, 6200))  # Draugr -> Hillmeet Charred Gateway
add_mob(place_bestiary_dup(10051, 6206))  # Draugr -> Hillmeet Tomb of Kings Approach

add_mob(place_bestiary_mob(10077, 6245))  # Green Hag -> Mossgrove Drowned Approach

add_mob(place_bestiary_mob(10092, 6246))  # Hydra -> Mossgrove Submerged Market

add_mob(place_bestiary_mob(10063, 6307))  # Each-Uisge -> Tidewoods Deep Forest Crossing

add_mob(place_bestiary_mob(10029, 6312))  # Assassin Vine -> Tidewoods Canopy Watch
add_mob(place_bestiary_dup(10029, 6325))  # Assassin Vine -> Tidewoods Western Patrol

add_mob(place_bestiary_mob(10139, 6249))  # Nuckelavee -> Mossgrove Eastern Shore (boss)

add_mob(place_bestiary_mob(10033, 6327))  # Changeling -> Tidewoods Intermediate Forest

add_mob(place_bestiary_mob(10070, 6326))  # Ettercap -> Tidewoods Northern Mist Zone

add_mob(place_bestiary_mob(10150, 6302))  # Owlbear -> Tidewoods Western Trail

add_mob(place_bestiary_mob(10184, 6330))  # Shambling Mound -> Tidewoods Northfade Margin

add_mob(place_bestiary_dup(10196, 6203))  # Storm Wisp -> Hillmeet Storm Wisp Warren

add_mob(place_bestiary_mob(10162, 6230))  # Ponaturi -> Whistlebank Silted Harbor
add_mob(place_bestiary_dup(10162, 6247))  # Ponaturi -> Mossgrove Partially Submerged Docks

add_mob(place_bestiary_dup(10189, 6201))  # Skeleton -> Hillmeet Fallen Canopy
add_mob(place_bestiary_dup(10189, 6232))  # Skeleton -> Whistlebank Market Quarter
add_mob(place_bestiary_dup(10189, 6215))  # Skeleton -> Foxfen Vine-Strangled Gate

add_mob(place_bestiary_dup(10238, 6234))  # Zombie -> Whistlebank Residential Ruins
add_mob(place_bestiary_dup(10238, 6217))  # Zombie -> Foxfen Ogre-Burned Grove

add_mob(place_bestiary_mob(10134, 6301))  # Nang Tani -> Tidewoods Northern Trail

add_mob(place_bestiary_mob(10192, 6309))  # Spider Eater -> Tidewoods Forest Road North

add_mob(place_bestiary_mob(10080, 6095))  # Grig -> Tiravel Forest Floor

add_mob(place_bestiary_mob(10103, 6305))  # Kodama -> Tidewoods Mist Edge

add_mob(place_bestiary_mob(10137, 6329))  # Nixie -> Kailian Shore Chain-Field View

add_mob(place_bestiary_mob(10160, 6311))  # Pixie -> Tidewoods Tiravel Forest Road South

add_mob(place_bestiary_mob(10213, 6313))  # Unicorn -> Tidewoods Myruvane-Tiravel Path

add_mob(place_bestiary_mob(10219, 6164))  # Water Elemental Medium -> Darnavar Mossgrove Shore

add_mob(place_bestiary_mob(10049, 6315))  # Dragon Turtle -> Kailian Shore South

add_mob(place_bestiary_mob(10024, 6316))  # Bunyip -> Kailian Shore Forest Road

add_mob(place_bestiary_mob(10097, 6328))  # Kappa -> Tidewoods Northern Shore Trail

add_mob(place_bestiary_mob(10084, 6314))  # Hakuturi -> Tidewoods Tiravel East Trail

add_mob(place_bestiary_mob(10205, 6304))  # Tipua -> Stonewind Plains Western Edge

add_mob(place_bestiary_mob(10140, 6094))  # Nymph -> Tiravel Starlit Glade

add_mob(place_bestiary_mob(10100, 6322))  # Kitsune -> Sundrift Veil Forest Margin

add_mob(place_bestiary_mob(10109, 6323))  # Leshy -> Sundrift Veil Trade Road (boss)

# --- INFINITE DESERT (CR 3-8) ---
add_mob(place_bestiary_mob(10011, 8205))  # Androsphinx -> Giant Oasis-City Processional (boss)

add_mob(place_bestiary_mob(10028, 8300))  # Amphisbaena -> Desert Road Kharazhad Junction
add_mob(place_bestiary_dup(10028, 8307))  # Amphisbaena -> Desert Road Long Flat

add_mob(place_bestiary_mob(10017, 8220))  # Basilisk -> Sunken Thrones Outer Desert
add_mob(place_bestiary_dup(10017, 8200))  # Basilisk -> Giant Oasis-City Outer Ring

add_mob(place_bestiary_mob(10018, 8346))  # Behir -> Great River Gorge Upper Rim

add_mob(place_bestiary_mob(10023, 8241))  # Bulette -> Glass Wastes Deep Glass Field

add_mob(place_bestiary_mob(10055, 8302))  # Dust Mephit -> Desert Road East Caravan
add_mob(place_bestiary_dup(10055, 8310))  # Dust Mephit -> Desert Road Ruin Outlook

add_mob(place_bestiary_mob(10083, 8242))  # Gynosphinx -> Glass Wastes Ancient Battleground

add_mob(place_bestiary_mob(10086, 8260))  # Hieracosphinx -> Tharok's Pillar Outer

add_mob(place_bestiary_mob(10107, 8203))  # Lamia -> Giant Oasis-City Western Residential

add_mob(place_bestiary_dup(10179, 8221))  # Sand Wraith -> Sunken Thrones Approach
add_mob(place_bestiary_dup(10179, 8222))  # Sand Wraith -> Sunken Thrones Northern

add_mob(place_bestiary_mob(10144, 8308))  # Olgoi-Khorkhoi -> Desert Road Glass Wastes Bypass

add_mob(place_bestiary_mob(10170, 8240))  # Remorhaz -> Glass Wastes Iridescent Flats

add_mob(place_bestiary_mob(10165, 8243))  # Purple Worm -> Glass Wastes Glass Sinkhole (boss)

add_mob(place_bestiary_mob(10106, 8223))  # Lamassu -> Sunken Thrones The Four Thrones

add_mob(place_bestiary_mob(10121, 8209))  # Medusa -> Giant Oasis-City Underground Archive

add_mob(place_bestiary_mob(10178, 8304))  # Salt Mephit -> Desert Road Southern Approach

add_mob(place_bestiary_mob(10130, 8201))  # Mushussu -> Giant Oasis-City Eastern Gate

add_mob(place_bestiary_dup(10129, 8224))  # Mummy -> Sunken Thrones Vault Approach

add_mob(place_bestiary_dup(10189, 8202))  # Skeleton -> Giant Oasis-City Northern Approach

add_mob(place_bestiary_dup(10238, 8206))  # Zombie -> Giant Oasis-City Hall of Waters

add_mob(place_bestiary_mob(10215, 8227))  # Vampire Spawn -> Sunken Thrones Sealed Vault

add_mob(place_bestiary_mob(10152, 8244))  # Peri -> Glass Wastes Buried Deceiver Cache

add_mob(place_bestiary_mob(10091, 8208))  # Humbaba -> Giant Oasis-City Treasure Vault (boss)

# Scorchspires / Volcanic
add_mob(place_bestiary_mob(10035, 8335))  # Cherufe -> Scorchspires Upper Vent (boss)
add_mob(place_bestiary_mob(10068, 8332))  # Ember Drake -> Scorchspires Emberfang Ridge
add_mob(place_bestiary_dup(10068, 8334))  # Ember Drake -> Scorchspires Volcanic Flow
add_mob(place_bestiary_mob(10114, 8331))  # Magma Mephit -> Scorchspires Western Approach
add_mob(place_bestiary_mob(10115, 11001))  # Magmin -> Scorchspire Mountain Road
add_mob(place_bestiary_mob(10203, 11002))  # Thoqqua -> Emberfang Pass
add_mob(place_bestiary_mob(10064, 11000))  # Earth Elemental Small -> Scorchspire Foothills
add_mob(place_bestiary_mob(10041, 11003))  # Criosphinx -> Volcanic Ridge Trail
add_mob(place_bestiary_mob(10176, 8050))  # Salamander -> Ember Vault First Antechamber
add_mob(place_bestiary_mob(10163, 8333))  # Popobawa -> Scorchspires Rarozhki Watch
add_mob(place_bestiary_mob(10169, 11005))  # Rast -> Scorchspire Junction
add_mob(place_bestiary_mob(10050, 11004))  # Dragonne -> Kharazhad Outer Approach

# Great River Gorge
add_mob(place_bestiary_mob(10217, 8349))  # Vodyanoy -> Gorge River Level North
add_mob(place_bestiary_mob(10158, 8350))  # Piasa -> Gorge Western Rim Road (boss)
add_mob(place_bestiary_mob(10157, 8348))  # Phi Tai Hong -> Gorge River Terrace
add_mob(place_bestiary_mob(10034, 8358))  # Charun -> Gorge Canyon Pool
add_mob(place_bestiary_mob(10043, 8347))  # Culsans -> Gorge Descent Path
add_mob(place_bestiary_mob(10099, 8354))  # Kinnari -> Gorge Sea Falls Overlook
add_mob(place_bestiary_mob(10174, 8093))  # Rust Monster -> Dunewell Tunnel Works
add_mob(place_bestiary_mob(10124, 8097))  # Minotaur -> Dunewell Under-River Tunnels
add_mob(place_bestiary_mob(10173, 8051))  # Roper -> Ember Vault Giant Forge (boss)
add_mob(place_bestiary_mob(10111, 8052))  # Lindworm -> Ember Vault Metal Repository (boss)
add_mob(place_bestiary_mob(10237, 8053))  # Zmey Gorynych -> Ember Vault Sealed Chamber (boss)

# --- DEEPWATER MARCHES (CR 4-8) ---
add_mob(place_bestiary_mob(10003, 9401))  # Adze -> Ash Trail North Track
add_mob(place_bestiary_mob(10002, 9342))  # Aboleth -> Drowned Piers Rune-Circle Core (boss)

add_mob(place_bestiary_mob(10022, 9350))  # Bugbear -> Ashcrown Warren Jungle Approach
add_mob(place_bestiary_dup(10022, 9355))  # Bugbear -> Ashcrown Warren Hobgoblin Post

add_mob(place_bestiary_mob(10074, 9353))  # Goblin -> Ashcrown Warren Goblin Occupation
add_mob(place_bestiary_dup(10074, 9356))  # Goblin -> Ashcrown Warren Lower Tunnel
add_mob(place_bestiary_dup(10074, 9411))  # Goblin -> Ash Trail Free Goblin Camp

add_mob(place_bestiary_mob(10072, 9416))  # Girallon -> Ash Trail Deepwood Interior

add_mob(place_bestiary_mob(10057, 9419))  # Dire Ape -> Ash Trail Canopy Bridge

add_mob(place_bestiary_mob(10085, 9425))  # Harpy -> Apelian Shore Mangrove Labyrinth

add_mob(place_bestiary_mob(10105, 9404))  # Krasue -> Ash Trail Flamewarg Margin

add_mob(place_bestiary_mob(10119, 9408))  # Mapinguari -> Ash Trail Ruined Waystation

add_mob(place_bestiary_mob(10155, 9403))  # Phi Krahang -> Ash Trail South Track

add_mob(place_bestiary_mob(10156, 9412))  # Phi Pop -> Ash Trail Flamewarg Fire-Site

add_mob(place_bestiary_mob(10186, 9215))  # Shocker Lizard -> Tidewell Lake Shore Path
add_mob(place_bestiary_dup(10186, 9421))  # Shocker Lizard -> Apelian Shore Tidewell Beach

add_mob(place_bestiary_mob(10194, 9406))  # Stirge -> Ash Trail River Crossing
add_mob(place_bestiary_dup(10194, 9413))  # Stirge -> Ash Trail Northern Junction

add_mob(place_bestiary_mob(10228, 9418))  # Will-O'-Wisp -> Ash Trail Water Serpent Crossing

add_mob(place_bestiary_mob(10181, 9422))  # Sea Cat -> Apelian Shore Pearl-Diving

add_mob(place_bestiary_mob(10182, 9424))  # Sea Hag -> Apelian Shore Western Shoals

add_mob(place_bestiary_mob(10069, 9423))  # Encantado -> Apelian Shore North Shore Reed Beds

add_mob(place_bestiary_mob(10128, 9405))  # Mud Menders -> Ash Trail Canopy Hold Approach

add_mob(place_bestiary_mob(10200, 9409))  # Tendriculos -> Ash Trail Deepwood Crossing

add_mob(place_bestiary_mob(10209, 9300))  # Troll -> The Spur Peninsula Approach

add_mob(place_bestiary_mob(10112, 9337))  # Locathah -> Drowned Piers Main Pier

add_mob(place_bestiary_mob(10122, 9335))  # Merfolk -> Drowned Piers Shore Approach

add_mob(place_bestiary_mob(10037, 9339))  # Chuul -> Drowned Piers South Pier (boss)

add_mob(place_bestiary_mob(10110, 9428))  # Leviathan-Shard -> Apelian Shore Headland

add_mob(place_bestiary_mob(10116, 9434))  # Mamlambo -> Apelian Shore Water Serpent Obs.

add_mob(place_bestiary_mob(10133, 9205))  # Nak -> Tidewell Lower Dock

add_mob(place_bestiary_mob(10095, 9344))  # Inkanyamba -> Drowned Piers Eel Nursery (boss)

add_mob(place_bestiary_mob(10135, 9283))  # Nasnas -> Murtavah Root Veil Grove

add_mob(place_bestiary_mob(10185, 9275))  # Shedim -> Thornwall Scent-Post Ring

add_mob(place_bestiary_mob(10120, 9269))  # Mazzikin -> Thornwall Outer Warg Dens

add_mob(place_bestiary_mob(10101, 9271))  # Klatterkin -> Thornwall South Trap Field

add_mob(place_bestiary_mob(10056, 9354))  # Dybbuk -> Ashcrown Warren Sealed Section

add_mob(place_bestiary_mob(10166, 9286))  # Qareen -> Murtavah Root East Jungle

add_mob(place_bestiary_mob(10187, 9277))  # Si'Lat -> Murtavah Root Jungle Approach

add_mob(place_bestiary_mob(10168, 9320))  # Rakshasa -> Deceiver's Refuge Edge (boss)

add_mob(place_bestiary_mob(10214, 9414))  # Uthikoloshe -> Ash Trail Wargbond Scout Post

add_mob(place_bestiary_mob(10201, 9249))  # Tengu -> Canopy Hold Deepwatch Spire

add_mob(place_bestiary_mob(10147, 9426))  # Ooze Mephit -> Apelian Shore Eastern Shoals

add_mob(place_bestiary_mob(10220, 9338))  # Water Elemental Large -> Drowned Piers Pier Junction

add_mob(place_bestiary_mob(10202, 9357))  # Tepegoz -> Ashcrown Warren Sealed Deep (boss)

add_mob(place_bestiary_mob(10197, 9358))  # Supay -> Ashcrown Warren Collapsed Section (boss)

add_mob(place_bestiary_mob(10061, 9420))  # Dire Tiger -> Ash Trail South Track Junction

add_mob(place_bestiary_mob(10146, 9417))  # Oni -> Ash Trail Giant Ruin Marker

add_mob(place_bestiary_mob(10208, 9351))  # Troglodyte -> Ashcrown Warren Outer Burrow

add_mob(place_bestiary_mob(10081, 9352))  # Grimlock -> Ashcrown Warren Upper Tunnel

# --- GATEFALL REACH (CR 3-7) ---
add_mob(place_bestiary_mob(10021, 12249))  # Bodak -> Silence Breach Inner Perimeter

add_mob(place_bestiary_mob(10153, 12239))  # Phase Spider -> Crescent Forest Spider Web Gallery

add_mob(place_bestiary_mob(10096, 12237))  # Jorogumo -> Crescent Forest Southern Deep

add_mob(place_bestiary_mob(10030, 12243))  # Cadi Kusu -> Scar Road Northern End

add_mob(place_bestiary_mob(10117, 12248))  # Manananggal -> Silence Breach Outer Perimeter

add_mob(place_bestiary_mob(10191, 12244))  # Spectre -> Scar Road Ambush Hollow

add_mob(place_bestiary_dup(10227, 12245))  # Wight -> Tomb of Kings Colonnade North
add_mob(place_bestiary_dup(10227, 12247))  # Wight -> Tomb of Kings Colonnade South

add_mob(place_bestiary_mob(10059, 12234))  # Dire Boar -> Gatefall Forest Transition

add_mob(place_bestiary_mob(10226, 12246))  # Wendigo -> Tomb of Kings Colonnade Central (boss)

add_mob(place_bestiary_mob(10054, 12225))  # Dullahan -> Warden's Ridge Road Southern

add_mob(place_bestiary_mob(10164, 12235))  # Puca -> Crescent Forest Northern Path

add_mob(place_bestiary_mob(10148, 12233))  # Orc -> Gatefall Grasslands Southern Road

add_mob(place_bestiary_mob(10088, 12201))  # Hippogriff -> The Gap Narrows

add_mob(place_bestiary_mob(10042, 12236))  # Cu Sith -> Crescent Forest Central Path

add_mob(place_bestiary_mob(10235, 12238))  # Yuki-Onna -> Crescent Forest Briarshade Approach

add_mob(place_bestiary_mob(10098, 12249))  # Karakoncolos -> Silence Breach Inner (with Bodak)

add_mob(place_bestiary_mob(10087, 12026))  # Goreham Brute -> Hillwatch Gap Road Overlook

add_mob(place_bestiary_mob(10113, 12202))  # Maero -> The Gap Central Passage

add_mob(place_bestiary_dup(10040, 12232))  # Cockatrice -> Gatefall Grasslands East-West

add_mob(place_bestiary_dup(10233, 12230))  # Wyvern -> Gatefall Grasslands Western Road

add_mob(place_bestiary_dup(10150, 12235))  # Owlbear -> Crescent Forest Northern Path

# --- TWIN RIVERS (CR 1-3) ---
add_mob(place_bestiary_dup(10014, 10437))  # Aranea -> Windweave Forest Eastern Deep

add_mob(place_bestiary_mob(10015, 10450))  # Bakeneko -> Shadeharm Glade Edge of Twilight

add_mob(place_bestiary_mob(10044, 10071))  # Darkmantle -> Stoneharbor Mine Gallery

add_mob(place_bestiary_mob(10108, 10035))  # Lasa -> Forkmeet Riverbank South
add_mob(place_bestiary_dup(10108, 10076))  # Lasa -> Stoneharbor River Walk

add_mob(place_bestiary_mob(10090, 10431))  # Huldra -> Singing Ridges Crystal Hollow

add_mob(place_bestiary_dup(10127, 10451))  # Monstrous Spider -> Shadeharm Sealed Path

add_mob(place_bestiary_mob(10180, 10432))  # Satyr -> Singing Ridges Eastern Ridge

add_mob(place_bestiary_dup(10080, 10436))  # Grig -> Windweave Canopy Base Camp

add_mob(place_bestiary_dup(10137, 10411))  # Nixie -> Highwater River Road The Narrows

add_mob(place_bestiary_dup(10103, 10435))  # Kodama -> Windweave Forest Deep Forest

add_mob(place_bestiary_mob(10171, 10043))  # River Serpent -> Forkmeet Highwater Road East

add_mob(place_bestiary_mob(10207, 10418))  # Treant -> Riverwind Heights Druidic Overlook (boss)

add_mob(place_bestiary_mob(10210, 10214))  # Tsukumogami -> Liraveth Tanuki Quarter

add_mob(place_bestiary_mob(10236, 10215))  # Zashiki-Warashi -> Liraveth Tanuki Workshop

add_mob(place_bestiary_mob(10138, 10503))  # Noppera-Bo -> Windweave Canopy Descent

add_mob(place_bestiary_mob(10224, 10400))  # Water Mephit -> Great River Road South of Custos

add_mob(place_bestiary_mob(10172, 10443))  # Roc -> Mountain Approaches Eagle's Perch (boss)

add_mob(place_bestiary_mob(10039, 10441))  # Cloud Giant -> Mountain Approaches Volcanic Shelf (boss)

add_mob(place_bestiary_mob(10188, 10442))  # Simurgh -> Mountain Approaches High Pass (boss)

# --- CUSTOS DO AETERNOS (CR 1-3, city area) ---
add_mob(place_bestiary_mob(10149, 4023))  # Otyugh -> Smuggler's Dock

add_mob(place_bestiary_mob(10048, 4140))  # Doppelganger -> Rat Run

add_mob(place_bestiary_mob(10123, 4036))  # Mimic -> The Reliquary

add_mob(place_bestiary_mob(10047, 4103))  # Domovoi -> Blacksmith's Row

# --- WILDERNESS CONNECTORS (CR 3-6) ---
add_mob(place_bestiary_mob(10079, 11011))  # Griffon -> Giant's Teeth Approach
add_mob(place_bestiary_dup(10079, 11013))  # Griffon -> Canyon Rim Road

add_mob(place_bestiary_mob(10036, 11131))  # Chimera -> Northern Giant's Teeth Foothills

add_mob(place_bestiary_mob(10071, 11014))  # Ettin -> Great River Gorge Northern Rim

add_mob(place_bestiary_mob(10159, 11102))  # Pishtaco -> Hillwatch Pass Summit

add_mob(place_bestiary_mob(10046, 11015))  # Derro -> Gorge Descent

add_mob(place_bestiary_mob(10142, 11081))  # Ogre -> Southern Hills Road
add_mob(place_bestiary_dup(10142, 11082))  # Ogre -> Jungle Margin

add_mob(place_bestiary_dup(10209, 11132))  # Troll -> Northern Giant's Teeth Sea Falls Pass

add_mob(place_bestiary_mob(10065, 11051))  # Earth Elemental Medium -> Stonewind Plains

add_mob(place_bestiary_mob(10218, 11010))  # Water Elemental Small -> Great River South Road

add_mob(place_bestiary_mob(10233, 11130))  # Wyvern -> Southern Highlands Road

add_mob(place_bestiary_mob(10102, 11014))  # Kobold -> GRG Northern Rim (with Ettin)

add_mob(place_bestiary_mob(10195, 11133))  # Stone Giant -> Inner Mountain Descent

add_mob(place_bestiary_mob(10143, 11103))  # Ogre Mage -> Hillwatch Pass Northern Descent

add_mob(place_bestiary_mob(10027, 11135))  # Amaru -> Gorge Rim Eastern Junction (boss)

add_mob(place_bestiary_mob(10058, 11134))  # Dire Bear -> GRG Eastern Rim Approach

add_mob(place_bestiary_mob(10078, 8054))  # Grick -> Ember Vault Guard Garrison

add_mob(place_bestiary_mob(10038, 5306))  # Cloaker -> Pryee Ruins Lava Tube Upper
add_mob(place_bestiary_mob(10076, 5307))  # Gray Ooze -> Pryee Ruins Lava Tube Deep
add_mob(place_bestiary_mob(10141, 5223))  # Ochre Jelly -> Kalite Ruins Hidden Silt Cache
add_mob(place_bestiary_mob(10019, 5285))  # Black Pudding -> Andrio Ruins Giant Ruin Access
add_mob(place_bestiary_mob(10177, 8053))  # Salamander Noble -> Ember Vault Sealed Chamber
# Oops, 8053 already has Zmey. Use a different room.
# Remove last and use 8051 -> already has Roper. Let's use Kharazhad forge area
# Actually let me just skip duplicate placement. We have enough.

# ============================================================
# STEP 3: NPC PLACEMENTS
# ============================================================

npc_vnum = 9010

# Named NPCs from lore
add_mob(make_npc(npc_vnum, 'Warden Kael Ridgeborn', 8, 12009,
    ['no_attack', 'quest_giver'], 'Lawful Good', [8, 10, 16], 18,
    'Warden Kael surveys the frontier with sharp eyes. "The Gap is quiet today, but the Breach never sleeps. What brings you to Hillwatch?"',
    description='A weathered Mytroan ranger in dappled green and brown, his keen gaze sweeping the frontier horizon. A longbow and twin short swords are never far from his hands.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Elder Aelwyn Rootsong', 10, 12035,
    ['no_attack', 'quest_giver'], 'Neutral Good', [10, 6, 20], 14,
    'Elder Aelwyn plucks a soft chord on her harp. "The trees sing of distant troubles, traveler. Perhaps you can help ease their worry."',
    description='A serene Pasua elf bard with silver-streaked hair, her fingers resting lightly on a harp of living wood. Her voice carries the memory of centuries.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Speaker Maren Firebraid', 7, 12058,
    ['no_attack', 'quest_giver'], 'Neutral', [7, 8, 14], 15,
    'Speaker Maren tends the amber forge-flame. "Glimmerholt stands because we tend both fire and forest. What do you seek here?"',
    description='A sturdy Mytroan druid with flame-red braids, wearing amber-studded leather. Her presence radiates the warmth of a well-tended hearth.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Headman Torven Grassmane', 6, 12081,
    ['no_attack', 'quest_giver'], 'Chaotic Good', [6, 12, 12], 15,
    'Torven laughs heartily. "Welcome to Brayholt! If you can ride and fight, there\'s always work on the frontier."',
    description='A broad-shouldered Mytroan barbarian with wind-tangled hair and a booming laugh. Scars crisscross his arms from years of frontier skirmishing.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Captain Sera Dawnwatch', 7, 12109,
    ['no_attack', 'quest_giver'], 'Lawful Good', [7, 10, 14], 18,
    'Captain Sera checks her patrol map. "The Red Trail is our lifeline. Keep your eyes open and your blade sharp out there."',
    description='A disciplined Mytroan fighter in polished chain mail, her red-dyed patrol cloak marking her as Redtrail\'s commander.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Druid Lirael Thornveil', 9, 12140,
    ['no_attack', 'quest_giver'], 'Neutral Good', [9, 8, 18], 16,
    'Lirael traces a rune in the air. "The thorns guard us, but they whisper of darkness creeping closer. Will you listen?"',
    description='A willowy Pasua elf druid in robes of woven bark and living vines. Her eyes shimmer with the green light of deep forest magic.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Talia Wendrow', 5, 10010,
    ['no_attack', 'quest_giver'], 'Lawful Neutral', [5, 6, 10], 12,
    'Talia looks up from her ledger. "Greenford\'s mill never stops turning, and neither does the Reeve\'s work. How can I help?"',
    description='A practical human woman in a miller\'s apron, Greenford\'s Reeve. Her no-nonsense manner belies a keen mind for trade and justice.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Soren Raftbinder', 4, 10038,
    ['no_attack', 'quest_giver'], 'Neutral Good', [4, 8, 8], 14,
    'Soren lashes a rope tight. "The rivers run swift here. If you\'re heading downstream, watch for the narrows past Stoneharbor."',
    description='A lean human ranger with river-weathered hands, known for guiding rafts safely through the confluence currents.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Thargrim Ironvein', 6, 10065,
    ['no_attack', 'quest_giver'], 'Lawful Neutral', [6, 10, 12], 17,
    'Thargrim pounds his fist on the anvil. "Stoneharbor\'s ore runs deep and true. What brings you to the bluffs?"',
    description='A powerfully built Pekakarlik dwarf with soot-stained arms and a braided beard. As head of the Smelter\'s Guild, he commands respect throughout the river towns.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Veyra Skysong', 5, 10105,
    ['no_attack', 'quest_giver'], 'Neutral Good', [5, 8, 10], 14,
    'Veyra gazes at the sky. "The wind carries messages from the peaks. What news do you bring from below?"',
    description='A lithe Kovaka elf ranger with feathered tokens braided into her hair. She tends the Sky-Flame that guides travelers through mountain passes.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Aeloria Sapwhisper', 7, 10131,
    ['no_attack', 'quest_giver'], 'Neutral Good', [7, 8, 14], 14,
    'Aeloria presses her palm against the ancient oak. "Deeproot Grove speaks. The forest remembers what others forget."',
    description='A serene Hasura elf druid in moss-green robes, her fingers stained with tree-sap. She serves as keeper of the Circle of Deeproot Grove.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Sylvara Quillwind', 8, 10205,
    ['no_attack', 'quest_giver'], 'Neutral', [8, 4, 16], 13,
    'Sylvara adjusts her spectacles. "The Grand Library contains knowledge from three ages. What lore do you seek?"',
    description='An elderly Hasura elf wizard in ink-stained robes, surrounded by floating scrolls and quill-pens. Head Librarian of the Grand Library of Liraveth.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Voren Starlance', 6, 10253,
    ['no_attack', 'quest_giver'], 'Chaotic Good', [6, 4, 12], 13,
    'Voren studies a star chart. "The currents above and below are changing. Something stirs in the deep places."',
    description='A young Na\'wasua elf sorcerer with gravity-defying silver hair, his Navigation Hall filled with floating star charts and wind maps.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Liora Airsong', 6, 10294,
    ['no_attack', 'quest_giver'], 'Chaotic Good', [6, 6, 12], 12,
    'Liora strums her lute. "Every guild compact begins with a song and ends with a promise. What promise do you bring?"',
    description='A vivacious Pasua elf bard with wind-chime earrings, her lute always at hand. She manages the Guild Compact Hall of Sylarien.'))
npc_vnum += 1

# ============================================================
# GENERIC NPCs
# ============================================================
npc_vnum = 9100

# --- CUSTOS DO AETERNOS ---
add_mob(make_npc(npc_vnum, 'Custos City Guard', 4, 4008,
    ['guard', 'no_attack'], 'Lawful Neutral', [4, 10, 8], 16,
    'The guard nods curtly. "Keep the peace and you\'re welcome in Custos."',
    description='A city guard in polished mail, bearing the sigil of Custos do Aeternos.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Custos City Guard', 4, 4024,
    ['guard', 'no_attack'], 'Lawful Neutral', [4, 10, 8], 16,
    'The guard watches the river traffic. "Move along, citizen."',
    description='A city guard in polished mail, bearing the sigil of Custos do Aeternos.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Custos City Guard', 4, 4072,
    ['guard', 'no_attack'], 'Lawful Neutral', [4, 10, 8], 16,
    '"The market gate is open. Mind your purse."',
    description='A city guard in polished mail, bearing the sigil of Custos do Aeternos.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Custos City Guard', 4, 4108,
    ['guard', 'no_attack'], 'Lawful Neutral', [4, 10, 8], 16,
    '"The west gate stands firm. Safe travels."',
    description='A city guard in polished mail, bearing the sigil of Custos do Aeternos.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Custos North Gate Guard', 5, 4131,
    ['guard', 'no_attack'], 'Lawful Neutral', [5, 10, 10], 17,
    '"Oroas Gate is open from dawn to dusk. State your business."',
    description='A senior guard in reinforced chain, stationed at the main northern gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Provisioner Halwick', 3, 4070,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 11,
    '"Need supplies for the road? I\'ve got everything an adventurer needs."',
    shop_inventory=[1, 2, 3, 5, 101, 102],
    shop_type='general',
    description='A rotund halfling with a perpetual smile, his shop overflowing with adventuring supplies.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Enchantress Vaelith', 6, 4038,
    ['shopkeeper', 'no_attack'], 'Neutral', [6, 4, 12], 12,
    '"Arcane components and enchanted trinkets. Everything has a price, of course."',
    shop_inventory=[201, 203, 208],
    shop_type='magic',
    description='A Na\'wasua elf with shimmering robes, her eyes gleaming with arcane knowledge.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Innkeeper Bressal', 2, 4005,
    ['innkeeper', 'no_attack'], 'Neutral Good', [2, 6, 4], 10,
    '"Welcome to the Wavecrest Inn! Rest your weary bones and enjoy the river view."',
    description='A jovial man with a thick mustache, wiping down the bar of the riverside inn.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Innkeeper Tessara', 2, 4083,
    ['innkeeper', 'no_attack'], 'Neutral Good', [2, 6, 4], 10,
    '"The Guildsman\'s Rest has the softest beds in the guild quarter. Stay a while!"',
    description='A cheerful woman running the guild quarter\'s finest inn.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'High Priestess Miravel', 8, 4026,
    ['priest', 'no_attack'], 'Neutral Good', [8, 8, 16], 14,
    '"The Ascended watch over all. Seek their blessing, and find peace."',
    description='A dignified elf priestess in white and gold vestments, tending the Plaza of the Ascended.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Swordmaster Daven', 10, 4080,
    ['trainer', 'no_attack'], 'Lawful Neutral', [10, 10, 20], 18,
    '"Training never ends. Show me what you\'ve learned, and I\'ll show you what you haven\'t."',
    description='A scarred veteran with a practice sword always in hand, running drills at the Adventurers\' Guild.'))
npc_vnum += 1

# --- TWIN RIVERS ---
add_mob(make_npc(npc_vnum, 'Greenford Gate Guard', 3, 10000,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"Welcome to Greenford. The mill\'s always turning."',
    description='A local militia guard at Greenford\'s north gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Miller Jorik', 2, 10002,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [2, 6, 4], 10,
    '"Fresh flour and grain, straight from the mill!"',
    shop_inventory=[1, 2, 3],
    shop_type='general',
    description='A flour-dusted man tending Greenford\'s Great Mill.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Innkeeper Olwen', 2, 10018,
    ['innkeeper', 'no_attack'], 'Neutral Good', [2, 6, 4], 10,
    '"The Millstone Inn has hot stew and cold ale. What\'ll it be?"',
    description='A stout woman with flour on her apron, running the Millstone Inn.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Stoneharbor Gate Guard', 3, 10060,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"River Bluff Gate stands strong. Enter freely."',
    description='A dwarf militia guard at Stoneharbor\'s gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Smith Bolgar', 4, 10067,
    ['shopkeeper', 'no_attack'], 'Lawful Neutral', [4, 8, 8], 14,
    '"Finest forged steel on the river. See for yourself."',
    shop_inventory=[101, 102, 103],
    shop_type='weapons',
    description='A soot-blackened dwarf hammering away at Stoneharbor\'s Forge Row.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Highspire Gate Guard', 3, 10100,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"Mountain Gate is open. Watch the switchbacks."',
    description='A Kovaka elf guard at Highspire\'s mountain gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Alchemist Fenna', 4, 10108,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [4, 4, 8], 11,
    '"Potions, salves, and reagents! Everything an adventurer needs."',
    shop_inventory=[201, 203],
    shop_type='magic',
    description='A young elf woman surrounded by bubbling vials and herb bundles.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Wind-Silk Merchant Ivali', 3, 10211,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 11,
    '"Wind-silk is Liraveth\'s pride. Light as air, strong as memory."',
    shop_inventory=[301],
    shop_type='general',
    description='A Hasura elf merchant displaying bolts of shimmering wind-silk fabric.'))
npc_vnum += 1

# --- KINSWEAVE ---
add_mob(make_npc(npc_vnum, 'Stonefall Gate Guard', 3, 5000,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"Eastern Gate is secure. Welcome to Stonefall."',
    description='A Pekakarlik dwarf guard at Stonefall\'s eastern gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Stonefall Shopkeeper Grimnar', 3, 5011,
    ['shopkeeper', 'no_attack'], 'Neutral', [3, 6, 6], 12,
    '"Quarrymarket has the finest stone goods. What catches your eye?"',
    shop_inventory=[1, 2, 3, 101, 102],
    shop_type='general',
    description='A stout dwarf manning the Quarrymarket stalls with pride.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Innkeeper Dagna', 2, 5022,
    ['innkeeper', 'no_attack'], 'Neutral Good', [2, 6, 4], 10,
    '"The Greystone Inn welcomes all. Ale\'s fresh and beds are warm."',
    description='A cheery dwarf woman running the Greystone Inn.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Highridge Guard Captain', 5, 5111,
    ['guard', 'no_attack'], 'Lawful Neutral', [5, 10, 10], 17,
    '"Lavaflow Bastion stands firm. The frontier is secure."',
    description='A Rarozhki dwarf officer in heat-treated armor at the Lavaflow Bastion.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Forgemaster Azak', 5, 5122,
    ['shopkeeper', 'no_attack'], 'Lawful Neutral', [5, 8, 10], 15,
    '"The Emberforge burns hot. What shall I craft for you?"',
    shop_inventory=[101, 102, 103, 301],
    shop_type='weapons',
    description='A master smith tending the legendary Emberforge of Highridge.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Lakeshore Guard', 3, 5141,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"Lake Gate stands open. Welcome to Lakeshore."',
    description='A guard at Lakeshore\'s city gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Rivertop Dock Guard', 3, 5068,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"North Dock Gate. State your cargo."',
    description='A guard at Rivertop\'s dock gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Innkeeper Meryam', 2, 5078,
    ['innkeeper', 'no_attack'], 'Neutral Good', [2, 6, 4], 10,
    '"The Riverflow Inn! Best view on the river."',
    description='A friendly halfling innkeeper at the Riverflow Inn.'))
npc_vnum += 1

# --- TIDEBLOOM REACH ---
add_mob(make_npc(npc_vnum, 'Branmill Gate Guard', 3, 6032,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"North gate stands. Welcome to Branmill Cove."',
    description='A guard at Branmill Cove\'s north gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Merchant Piers', 3, 6017,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 11,
    '"Grain, fish, and sundries. All from the finest sources in the Reach."',
    shop_inventory=[1, 2, 3],
    shop_type='general',
    description='A weathered merchant at Branmill Cove\'s grain market.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Velathenor Gate Guard', 3, 6063,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"East gate. State your business in Velathenor."',
    description='A guard at Velathenor\'s east gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Innkeeper Darva', 2, 6073,
    ['innkeeper', 'no_attack'], 'Neutral Good', [2, 6, 4], 10,
    '"The Wavecrest Inn welcomes you! Ale\'s fresh."',
    description='A plump woman at the Wavecrest Inn.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Tiravel Gate Guard', 3, 6101,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"The east gate is open. Mind the forest paths."',
    description='An elf guard at Tiravel\'s east gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Myruvane Gate Guard', 3, 6128,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"North gate secure. Welcome to Myruvane."',
    description='An elf guard at Myruvane\'s north gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Darnavar Gate Guard', 3, 6156,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"East gate. Careful near the Mossgrove approach."',
    description='A guard at Darnavar\'s east gate.'))
npc_vnum += 1

# --- ETERNAL STEPPE ---
add_mob(make_npc(npc_vnum, 'Tavranek Gate Guard', 4, 7005,
    ['guard', 'no_attack'], 'Lawful Neutral', [4, 10, 8], 16,
    '"North Gate and Desert Road. Papers, please."',
    description='A Mytroan Far Rider guard at Tavranek\'s north gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Tavranek Gate Guard', 4, 7034,
    ['guard', 'no_attack'], 'Lawful Neutral', [4, 10, 8], 16,
    '"Western Gate. The steppe road is clear today."',
    description='A Mytroan Far Rider guard at Tavranek\'s western gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Horse Trader Yakhin', 4, 7011,
    ['shopkeeper', 'no_attack'], 'Neutral', [4, 6, 8], 12,
    '"Finest horses on the steppe! Come see my stock."',
    shop_inventory=[1, 2, 3],
    shop_type='general',
    description='A weathered Mytroan horse trader at the auction floor.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Steppe Healer Nashira', 5, 7030,
    ['priest', 'no_attack'], 'Neutral Good', [5, 8, 10], 12,
    '"The wind carries healing. Let me tend your wounds."',
    description='A Pasua elf herbalist and healer at Tavranek\'s Healer\'s Hall.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Teshen Halt Gate Guard', 4, 7093,
    ['guard', 'no_attack'], 'Lawful Neutral', [4, 10, 8], 16,
    '"Desert Gate. Fill your waterskins before you leave."',
    description='A Mytroan guard at Teshen Halt\'s desert gate.'))
npc_vnum += 1

# --- INFINITE DESERT ---
add_mob(make_npc(npc_vnum, 'Kharazhad Caldera Guard', 5, 8000,
    ['guard', 'no_attack'], 'Lawful Neutral', [5, 10, 10], 18,
    '"Caldera Gate stands. State your business in Kharazhad."',
    description='A Rarozhki dwarf guard in heat-forged armor at the caldera gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Merchant Ember-Eye', 4, 8002,
    ['shopkeeper', 'no_attack'], 'Neutral', [4, 6, 8], 12,
    '"Embersteel, fire-powder, and desert provisions. Name your need."',
    shop_inventory=[101, 102, 103, 1, 2],
    shop_type='general',
    description='A one-eyed Rarozhki merchant at Kharazhad\'s central market.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Forge-Priest Korrath', 7, 8004,
    ['priest', 'no_attack'], 'Lawful Neutral', [7, 8, 14], 15,
    '"The Lady of Fire watches over Kharazhad. Seek her blessing and be renewed."',
    description='A solemn Rarozhki priest at the Temple of the Lady of Fire.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Oasis Warden Jebril', 4, 8118,
    ['guard', 'no_attack'], 'Neutral Good', [4, 8, 8], 14,
    '"Solhaven\'s oasis is sacred. Drink freely but respect the water."',
    description='A Pekakarlik water-engineer who serves as Solhaven\'s warden.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Desert Provisioner Ashani', 3, 8110,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 11,
    '"Waterskins, dried food, and desert cloaks. You\'ll need them all out there."',
    shop_inventory=[1, 2, 3],
    shop_type='general',
    description='A sun-darkened woman selling desert survival supplies.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Dunewell Merchant Haskel', 3, 8090,
    ['shopkeeper', 'no_attack'], 'Neutral', [3, 6, 6], 11,
    '"Upper Cliff Market has the best prices on the gorge trade route."',
    shop_inventory=[1, 2, 3, 101],
    shop_type='general',
    description='A cliff-dwelling merchant at Dunewell\'s upper market.'))
npc_vnum += 1

# --- DEEPWATER MARCHES ---
add_mob(make_npc(npc_vnum, "Titan's Rest Gate Guard", 5, 9100,
    ['guard', 'no_attack'], 'Lawful Neutral', [5, 10, 10], 17,
    '"Ralven\'s Gate stands. The Gilded Company welcomes disciplined visitors."',
    description='A Gilded Company soldier in gleaming plate at Titan\'s Rest\'s main gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Bazaar Merchant Kolva', 3, 9102,
    ['shopkeeper', 'no_attack'], 'Neutral', [3, 6, 6], 11,
    '"Jungle provisions, exotic herbs, and Deepwater trade goods!"',
    shop_inventory=[1, 2, 3, 201],
    shop_type='general',
    description='A halfling trader at Titan\'s Rest\'s Bazaar.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Healer Aura', 5, 9124,
    ['priest', 'no_attack'], 'Neutral Good', [5, 8, 10], 12,
    '"Jungle fevers and venom bites. I\'ve seen it all. Let me help."',
    description='A healer attending the wounded at Titan\'s Rest.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Tidewell Stiltmarket Trader', 3, 9200,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 11,
    '"Reed-craft, lake fish, and Apelian pearls!"',
    shop_inventory=[1, 2],
    shop_type='general',
    description='A halfling merchant on Tidewell\'s stilt platforms.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Thornwall Warg-Bond Guard', 4, 9262,
    ['guard', 'no_attack'], 'Neutral', [4, 10, 8], 15,
    '"The Palisade stands. Friend or foe?"',
    description='A goblin warrior bonded with a war-warg, guarding Thornwall\'s gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Murtavah Root Merchant', 3, 9279,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 11,
    '"Rare herbs, jungle medicines, and spirit-crafted goods."',
    shop_inventory=[201, 203],
    shop_type='magic',
    description='An elderly halfling herbalist at the Outer Stall Ring.'))
npc_vnum += 1

# --- GATEFALL REACH ---
add_mob(make_npc(npc_vnum, 'Hillwatch Gate Guard', 4, 12000,
    ['guard', 'no_attack'], 'Lawful Good', [4, 10, 8], 17,
    '"Gap Road Gate. Welcome to the frontier."',
    description='A Mytroan ranger-guard at Hillwatch\'s main gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Hillwatch Provisioner', 3, 12002,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 12,
    '"Frontier supplies. You\'ll need good steel and warm cloaks out here."',
    shop_inventory=[1, 2, 3, 101, 102],
    shop_type='general',
    description='A frontier merchant selling supplies to patrol riders.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Brayholt Gate Guard', 3, 12080,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"Steppe Road Gate. Horses for sale at the fair grounds."',
    description='A Mytroan guard at Brayholt\'s steppe road gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Silkenbough Wind-Silk Trader', 3, 12032,
    ['shopkeeper', 'no_attack'], 'Neutral Good', [3, 6, 6], 11,
    '"Silkenbough wind-silk. The finest in the Reach."',
    shop_inventory=[301],
    shop_type='general',
    description='A Pasua elf merchant at the Wind-Silk Yards.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Redtrail Gate Guard', 4, 12106,
    ['guard', 'no_attack'], 'Lawful Good', [4, 10, 8], 16,
    '"North Gate. The Red Trail awaits."',
    description='A patrol rider guard at Redtrail Hollow\'s gate.'))
npc_vnum += 1

add_mob(make_npc(npc_vnum, 'Briarshade Gate Guard', 3, 12130,
    ['guard', 'no_attack'], 'Lawful Neutral', [3, 10, 6], 15,
    '"Thornwall Gate. The forest watches with us."',
    description='An elf guard at Briarshade\'s thornwall gate.'))
npc_vnum += 1

# --- CHAPEL ---
add_mob(make_npc(npc_vnum, 'Altar Keeper Solenne', 6, 1000,
    ['priest', 'no_attack'], 'Neutral Good', [6, 8, 12], 13,
    '"The four elements converge here. Seek balance, and you shall find strength."',
    description='A serene priestess who tends the Central Aetherial Altar, her robes shifting with elemental colors.'))
npc_vnum += 1

# ============================================================
# Remove last Salamander Noble that was placed in already-occupied room
# ============================================================
# Filter out the Salamander Noble (10177) at 8053 since Zmey is there
new_mobs = [m for m in new_mobs if not (m.get('vnum') == 10177 and m.get('room_vnum') == 8053)]

# ============================================================
# VALIDATE AND WRITE
# ============================================================

# Remove None entries
new_mobs = [m for m in new_mobs if m is not None]

# Verify all room_vnums exist
invalid = []
for m in new_mobs:
    if m['room_vnum'] not in all_room_vnums:
        invalid.append((m['vnum'], m['name'], m['room_vnum']))

if invalid:
    print(f'WARNING: {len(invalid)} mobs with invalid room_vnums:')
    for v, n, r in invalid:
        print(f'  {v}: {n} -> room {r}')

# Count by type
type_counts = {}
for m in new_mobs:
    t = 'NPC' if 'no_attack' in m.get('flags', []) else m.get('type_', 'Unknown')
    type_counts[t] = type_counts.get(t, 0) + 1

print(f'Total mobs: {len(new_mobs)}')
print('By category:')
for t, c in sorted(type_counts.items()):
    print(f'  {t}: {c}')

# Count by area
area_counts = {}
for m in new_mobs:
    rv = m['room_vnum']
    area = room_lookup.get(rv, {}).get('area', 'Unknown')
    area_counts[area] = area_counts.get(area, 0) + 1

print('\nBy area:')
for a, c in sorted(area_counts.items()):
    print(f'  {a}: {c}')

# Check room overcrowding
room_mob_counts = {}
for m in new_mobs:
    rv = m['room_vnum']
    room_mob_counts[rv] = room_mob_counts.get(rv, 0) + 1

overcrowded = {rv: cnt for rv, cnt in room_mob_counts.items() if cnt > 3}
if overcrowded:
    print(f'\nWARNING: {len(overcrowded)} rooms with >3 mobs:')
    for rv, cnt in sorted(overcrowded.items()):
        info = room_lookup.get(rv, {})
        print(f'  Room {rv} ({info.get("name", "?")}): {cnt} mobs')

# Write
with open('oreka_mud/data/mobs.json', 'w', encoding='utf-8') as f:
    json.dump(new_mobs, f, indent=2, ensure_ascii=False)

print('\nWrote mobs.json successfully!')
