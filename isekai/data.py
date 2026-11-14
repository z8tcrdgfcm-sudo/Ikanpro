import os
from pathlib import Path

TILE = 32
MAP_W = 30
MAP_H = 20
WIDTH = MAP_W * TILE
HEIGHT = MAP_H * TILE

PLAYER_START = (7, 18)
HERO_NAME = "Ren"

ENCOUNTER_CHANCE = 0.12
BOSS_ID = "demonlord"
SAVE_FILE = str(Path(__file__).resolve().parent.parent / "save.json")

ZONE_OF_TILE = {"G": "meadow", "F": "dungeon"}

WALKABLE = set(".Gf=FEIXSs")


def _build_map():
    g = [["." for _ in range(MAP_W)] for _ in range(MAP_H)]

    def rect(x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[y][x] = ch

    def vline(x, y0, y1, ch):
        for y in range(y0, y1 + 1):
            g[y][x] = ch

    for x in range(MAP_W):
        g[0][x] = "T"
    for y in range(MAP_H):
        g[y][0] = "T"
        g[y][MAP_W - 1] = "T"

    rect(9, 1, 20, 6, "T")
    rect(10, 1, 19, 5, "F")
    g[1][14] = "X"
    g[6][14] = "E"

    rect(3, 8, 6, 10, "G")
    rect(6, 11, 9, 13, "G")
    rect(17, 8, 20, 10, "G")
    rect(16, 12, 19, 14, "G")

    rect(24, 8, 28, 13, "W")

    vline(14, 7, 18, "=")
    rect(1, 15, 12, 19, "=")

    rect(2, 15, 3, 15, "B")
    g[16][2] = "S"
    rect(9, 15, 10, 15, "B")
    g[16][9] = "I"
    rect(6, 15, 7, 15, "B")
    g[17][5] = "s"

    for x, y in [(3, 7), (11, 7), (18, 7), (26, 7), (2, 9), (12, 12),
                 (22, 11), (5, 13), (21, 15), (13, 9), (25, 16), (8, 12)]:
        if g[y][x] == ".":
            g[y][x] = "f"

    for x, y in [(1, 8), (2, 12), (12, 14), (22, 14), (23, 7), (27, 7),
                 (1, 13), (13, 11), (21, 13), (28, 16), (4, 7), (19, 13)]:
        if g[y][x] == ".":
            g[y][x] = "T"

    return ["".join(row) for row in g]


MAP = _build_map()

NPCS = {
    "shopkeeper": {"pos": (4, 16), "sprite": "shopkeeper", "dialog": "shopkeeper", "opens_shop": True},
    "priestess": {"pos": (8, 17), "sprite": "priestess", "dialog": "priestess"},
    "villager": {"pos": (6, 18), "sprite": "villager", "dialog": "villager"},
}

ENEMIES = {
    "slime": {
        "name": "Slime", "hp": 30, "atk": 6, "def": 2, "spd": 4,
        "xp": 12, "gold": 8, "sprite": "slime", "scale": 4,
        "weak": ["fire"], "resist": [],
        "moves": [{"name": "Tackle", "power": 1.0, "element": "phys", "w": 3},
                  {"name": "Goo Spit", "power": 1.15, "element": "water", "w": 1}],
    },
    "goblin": {
        "name": "Goblin", "hp": 42, "atk": 9, "def": 4, "spd": 6,
        "xp": 18, "gold": 14, "sprite": "goblin", "scale": 4,
        "weak": [], "resist": [],
        "moves": [{"name": "Shank", "power": 1.1, "element": "phys", "w": 3},
                  {"name": "Wild Stab", "power": 1.45, "element": "phys", "w": 1}],
    },
    "wolf": {
        "name": "Dire Wolf", "hp": 38, "atk": 11, "def": 3, "spd": 10,
        "xp": 20, "gold": 10, "sprite": "wolf", "scale": 4,
        "weak": ["ice"], "resist": [],
        "moves": [{"name": "Bite", "power": 1.05, "element": "phys", "w": 3},
                  {"name": "Rending Claws", "power": 1.5, "element": "phys", "w": 1}],
    },
    "skeleton": {
        "name": "Skeleton", "hp": 50, "atk": 12, "def": 6, "spd": 5,
        "xp": 26, "gold": 18, "sprite": "skeleton", "scale": 4,
        "weak": ["holy"], "resist": ["phys"],
        "moves": [{"name": "Bone Swing", "power": 1.2, "element": "phys", "w": 3},
                  {"name": "Rattle", "power": 1.0, "element": "dark", "w": 2}],
    },
    "orc": {
        "name": "Orc Brute", "hp": 70, "atk": 15, "def": 8, "spd": 4,
        "xp": 34, "gold": 26, "sprite": "orc", "scale": 4,
        "weak": [], "resist": ["phys"],
        "moves": [{"name": "Club Smash", "power": 1.35, "element": "phys", "w": 3},
                  {"name": "Heavy Blow", "power": 1.7, "element": "phys", "w": 1}],
    },
    "darkmage": {
        "name": "Dark Mage", "hp": 46, "atk": 16, "def": 4, "spd": 8,
        "xp": 36, "gold": 30, "sprite": "mage", "scale": 4,
        "weak": ["holy"], "resist": ["dark"],
        "moves": [{"name": "Dark Bolt", "power": 1.5, "element": "dark", "w": 3},
                  {"name": "Drain", "power": 0.9, "element": "dark", "w": 2, "heal": True}],
    },
    "demonlord": {
        "name": "Demon Lord Vexaris", "hp": 260, "atk": 24, "def": 12, "spd": 10,
        "xp": 300, "gold": 500, "sprite": "demon", "scale": 4,
        "weak": ["holy"], "resist": ["fire", "ice", "phys"],
        "moves": [{"name": "Doom Slash", "power": 1.7, "element": "phys", "w": 3},
                  {"name": "Dark Flare", "power": 1.6, "element": "fire", "w": 2},
                  {"name": "Nightmare", "power": 2.2, "element": "dark", "w": 1},
                  {"name": "Dark Mend", "power": 0.0, "element": "dark", "w": 2, "heal": 45}],
    },
}

ENCOUNTER_TABLES = {
    "meadow": [("slime", 50), ("goblin", 30), ("wolf", 20)],
    "dungeon": [("goblin", 20), ("wolf", 15), ("skeleton", 25), ("orc", 25), ("darkmage", 15)],
}

SKILLS = {
    "strike": {"name": "Strike", "mp": 0, "power": 1.0, "element": "phys", "min_level": 1,
               "desc": "A reliable sword strike."},
    "fire": {"name": "Fireball", "mp": 6, "power": 1.8, "element": "fire", "min_level": 1,
             "desc": "Hurl a ball of flame. Slimes fear it."},
    "ice": {"name": "Ice Shard", "mp": 5, "power": 1.5, "element": "ice", "min_level": 1,
            "desc": "A shard of ice. Wolves hate it."},
    "heal": {"name": "Heal", "mp": 8, "power": 0, "element": "holy", "min_level": 1,
             "heal": 35, "heal_per_lvl": 5, "desc": "Restore HP."},
    "drain": {"name": "Drain", "mp": 7, "power": 1.1, "element": "dark", "min_level": 2,
              "drain": True, "desc": "Damage the foe and siphon HP."},
    "powerslash": {"name": "Power Slash", "mp": 10, "power": 2.6, "element": "phys", "min_level": 3,
                   "desc": "A devastating overhead blow."},
    "megafire": {"name": "Mega Fire", "mp": 16, "power": 3.2, "element": "fire", "min_level": 5,
                 "desc": "Inferno. Burns almost everything."},
    "holy": {"name": "Holy Light", "mp": 14, "power": 3.0, "element": "holy", "min_level": 6,
             "desc": "Sacred light. The undead and demons fear it."},
}

SKILL_ORDER = ["strike", "fire", "ice", "heal", "drain", "powerslash", "megafire", "holy"]

ITEMS = {
    "potion": {"name": "Potion", "price": 30, "heal": 50, "desc": "Restores 50 HP.", "battle": True},
    "ether": {"name": "Ether", "price": 45, "mp": 25, "desc": "Restores 25 MP.", "battle": True},
    "elixir": {"name": "Elixir", "price": 150, "full": True, "desc": "Fully restores HP and MP.", "battle": True},
    "phoenix": {"name": "Phoenix Down", "price": 120, "revive": True,
                "desc": "Auto-revives you at 50% HP if you fall.", "battle": False},
}

WEAPONS = [
    ("Wooden Sword", 0, 0),
    ("Bronze Sword", 4, 80),
    ("Iron Sword", 8, 200),
    ("Steel Sword", 13, 450),
    ("Mythril Sword", 19, 900),
    ("Dragon Blade", 28, 1800),
]

ARMORS = [
    ("Traveler's Clothes", 0, 0),
    ("Leather Armor", 3, 70),
    ("Chainmail", 6, 180),
    ("Plate Armor", 10, 420),
    ("Dragon Mail", 16, 950),
]

SHOP_STOCK = ["potion", "ether", "elixir", "phoenix"]
SHOP_GEAR = ["weapon", "armor"]

INN_COST = 20

DIALOGS = {
    "intro": [
        "???: ...Hey. Hey! Can you hear me?!",
        "A blinding light fills your vision.",
        "Goddess Lunaria: Welcome, brave soul... to the world of AETHERIA!",
        "Goddess Lunaria: You were pulled from another world by a strange magic.",
        "Goddess Lunaria: The Demon Lord VEXARIS has awakened in the dungeon to the north.",
        "Goddess Lunaria: Take this sword, hero. Grow strong. Save Aetheria!",
        "Goddess Lunaria: Move with WASD or the arrow keys. Press E to talk.",
        "Goddess Lunaria: Beware the tall grass... monsters love to hide there.",
    ],
    "sign": [
        "Town notice board:",
        "Monsters roam the tall grass north of town. Adventurers wanted!",
        "The dungeon lies far north, past the meadow. Bring potions!",
    ],
    "shopkeeper": [
        "Shopkeeper: Welcome to the Emporium!",
        "Shopkeeper: Step on the golden door, or talk to me, to browse my wares.",
        "Shopkeeper: Better gear means a longer life. Potions save lives!",
    ],
    "priestess": [
        "Priestess: I serve Goddess Lunaria. The inn will restore you for 20 gold.",
        "Priestess: The Demon Lord fears holy magic. Keep your MP topped up!",
    ],
    "villager": [
        "Villager: They say the Demon Lord was once a hero of this world...",
        "Villager: Slimes are weak to fire. Wolves fear ice. Skeleton bones shrug off blades!",
        "Villager: Press ESC for your status and to save. Good luck, hero!",
    ],
    "boss_pre": [
        "Demon Lord Vexaris: So... another 'hero' crawls into my lair.",
        "Demon Lord Vexaris: I swallowed this world's hope long ago. Yours is next!",
    ],
    "boss_post": [
        "Demon Lord Vexaris: Impossible... my power...",
        "The Demon Lord dissolves into black mist.",
    ],
    "ending": [
        "Goddess Lunaria: You did it, hero! Vexaris is destroyed!",
        "Goddess Lunaria: Aetheria is at peace... for now.",
        "Goddess Lunaria: Stay as long as you like. This world could use a hero.",
        "THE END — thanks for playing!",
        "(Choose NEW JOURNEY+ on the title screen for a harder adventure.)",
    ],
    "gameover": [
        "Goddess Lunaria: ...Don't give up, hero. I'll pull you back from the brink.",
        "You awaken in town. (You lost some gold.)",
    ],
    "inn_choice": {
        "lines": ["Sleep at the inn and fully restore HP/MP? (20 gold)"],
        "choices": ["Yes", "No"],
    },
    "inn_no_gold": ["Not enough gold, traveler."],
    "inn_healed": ["You slept soundly. HP and MP fully restored!"],
    "no_potions": ["You have nothing usable right now."],
}
