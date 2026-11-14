import random

import pygame

from . import data

SKIN = (255, 217, 179)
SKIN_SH = (224, 168, 120)
EYE = (30, 30, 45)
MOUTH = (180, 90, 90)
HAIR_SILVER = (205, 215, 240)
HAIR_SILVER_SH = (140, 155, 195)
COAT = (58, 111, 216)
COAT_SH = (39, 73, 143)
SCARF = (232, 69, 69)
TRIM = (240, 240, 245)
PANTS = (58, 58, 74)
BOOTS = (90, 58, 34)
BLADE = (225, 232, 245)
GUARD = (230, 190, 80)
GRIP = (120, 80, 40)

HERO_PAL = {
    "H": HAIR_SILVER, "h": HAIR_SILVER_SH, "S": SKIN, "s": SKIN_SH, "E": EYE,
    "M": MOUTH, "C": COAT, "c": COAT_SH, "R": SCARF, "W": TRIM, "P": PANTS,
    "B": BOOTS, "Y": GUARD, "G": GRIP,
}

HERO = [
    "..H..H..H..H....",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    ".HHHHHHHHHHHHHH.",
    ".HHSSSSSSSSSSHH.",
    ".HSSSSSSSSSSSSH.",
    ".HSSESSSSSSESH..",
    ".HSSSSMMSSSSSH..",
    "..RRRRRRRRRRRR..",
    "..RWCCCCCCCCWR..",
    "..CCCCCCCCCCCC..",
    ".SCCCCCCCCCCCCS.",
    "..cccccccccccc..",
    "...PPPPPPPPPP...",
    "...PPP..PPP.....",
    "...BBB..BBB.....",
]

HERO_BACK = [
    "..H..H..H..H....",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    ".HHHHHHHHHHH.W..",
    ".HHHHHHHHHHHHWW.",
    ".hhhhhhhhhhhhWW.",
    ".HHHHHHHHHHHHWW.",
    ".HHHHHHHHHHHHWW.",
    "..RRRRRRRRRRWW..",
    "..RWCCCCCCCCWY..",
    "..CCCCCCCCCCCY..",
    ".SCCCCCCCCCCCCG.",
    "..cccccccccccc..",
    "...PPPPPPPPPP...",
    "...PPP..PPP.....",
    "...BBB..BBB.....",
]

SLIME_PAL = {"S": (94, 200, 255), "s": (60, 150, 220), "W": (220, 245, 255), "E": (20, 40, 80), "M": (20, 60, 110)}
SLIME = [
    "................",
    "................",
    "................",
    ".....SSSSSS.....",
    "...SSSSSSSSSS...",
    "..SSWSSSSSSSSS..",
    ".SSSSSSSSSSSSSS.",
    ".SSESSSSSSSESSS.",
    ".SSSSSSSSSSSSSS.",
    ".SSSMMMMMMSSSS..",
    "..SSSSSSSSSSSS..",
    "..SSSSSSSSSSSS..",
    "...SSSSSSSSSS...",
    "..ssSSSSSSSSss..",
    ".ssSSSSSSSSSSss.",
    "..ssssssssssss..",
]

GOBLIN_PAL = {"G": (90, 180, 70), "g": (60, 140, 50), "E": (230, 50, 50), "W": (240, 240, 220), "T": (240, 240, 220), "L": (150, 90, 40), "D": (170, 170, 180)}
GOBLIN = [
    "................",
    "..G........G....",
    ".GGG......GGG...",
    ".GGGGGGGGGGGG...",
    "GGGGGGGGGGGGGG..",
    "GGGGGGGGGGGGGGG.",
    "GgEESSSSSSSEGg..",
    "GgSSSSSSSSSSGg..",
    ".GgWWSSSSWWGg...",
    ".GGTTTTTTTTGG...",
    "..GGGGGGGGGG....",
    "..LLLLLLLLLL.D..",
    "..LLLLLLLLLLDD..",
    "...LL....LL.....",
    "...GG....GG.....",
    "..ggg....ggg....",
]

WOLF_PAL = {"F": (150, 155, 165), "f": (110, 115, 130), "W": (235, 235, 240), "E": (255, 200, 60), "N": (25, 25, 30), "T": (110, 115, 130)}
WOLF = [
    "................",
    "....FF..........",
    "...FFFF..FF.....",
    "..FFFFFFFF......",
    ".FFFFFFFFFFF....",
    ".FFFEFFFFFFFF...",
    "FFFFFFFFFFFWW...",
    "FFFFFFFFFFFFN...",
    ".FFFFFFFFFFFFf..",
    "..FFFFFFFFF.....",
    "T.FFFFFFFFFFFF..",
    "TTFFFFFFFFFFFFF.",
    "FFFFFFFFFFFF....",
    "FF...FF...FF....",
    "FF....FF....FF..",
    "ff....ff....ff..",
]

SKELETON_PAL = {"B": (235, 230, 215), "b": (190, 185, 170), "E": (25, 25, 35)}
SKELETON = [
    "................",
    "....BBBBBB......",
    "...BBBBBBBB.....",
    "..BBEBBBBBEB....",
    "..BBBBBBBBBB....",
    "...BBBBBBBB.....",
    "....BB..BB......",
    "..BBBBBBBBBB....",
    ".BbBbBbBbBbBb...",
    ".BbBbBbBbBbBb...",
    "..BBBBBBBBBB....",
    "...BB....BB.....",
    "...BB....BB.....",
    "...BB....BB.....",
    "...BB....BB.....",
    "..bbb....bbb....",
]

ORC_PAL = {"G": (70, 160, 60), "g": (45, 120, 40), "E": (255, 220, 60), "T": (240, 240, 220), "W": (240, 240, 220), "A": (120, 120, 135)}
ORC = [
    "................",
    "..GG........GG..",
    ".GGGGGGGGGGGG...",
    "GGGGGGGGGGGGGG..",
    "GgGGGGGGGGGGGg..",
    "GEESSSSSSSSEEG..",
    "GGSSSSSSSSSSGG..",
    "GGTWWSSSSWWTG...",
    ".GAAAAAAAAAG....",
    ".AAAAAAAAAAAA...",
    "GAAAAAAAAAAAAA..",
    "GgAAAAAAAAAAGg..",
    "..AAAAAAAAAA....",
    "...GGGGGGGG.....",
    "...GG....GG.....",
    "..ggg....ggg....",
]

MAGE_PAL = {"R": (110, 70, 170), "r": (80, 50, 130), "H": (110, 70, 170), "Y": (255, 210, 80), "S": SKIN, "E": EYE, "M": MOUTH, "B": (120, 80, 40), "O": (255, 120, 220)}
MAGE = [
    ".......HH.......",
    "......HHHH......",
    ".....HHHHHH.....",
    "....HHHHHHHH....",
    "...HHYYYYYYHH...",
    "..HHHHHHHHHHHH..",
    "...SSSSSSSS.....",
    "...SESSSSES.....",
    "....SSSSSS......",
    "...RRRRRRRR.....",
    "..RRRRRRRRRR....",
    ".RRRRRRRRRRRRO..",
    "..RRRRRRRRRRB...",
    "..RrRRRRRRrRB...",
    "...RRRRRRRRRB...",
    "...rrrrrrrrrb...",
]

DEMON_PAL = {"D": (140, 30, 50), "d": (95, 18, 34), "c": (95, 18, 34), "H": (230, 225, 210), "E": (255, 230, 60), "M": (60, 10, 20), "T": (240, 240, 220), "W": (60, 20, 40), "C": (230, 225, 210)}
DEMON = [
    "....HH............HH....",
    "...HHHH..........HHHH...",
    "..HHHHHH........HHHHHH..",
    "..HHHDDDDDDDDDDDDHHH....",
    ".HHHDDDDDDDDDDDDDDHHH...",
    ".HDDDDDDDDDDDDDDDDDDH...",
    "WDDDDDDDDDDDDDDDDDDDDW..",
    "WWDDDEEDDDDDDDDEEDDDWW..",
    "WWWDDDDDMMMMMMDDDDDWWW..",
    ".WWDDDDDTTTTTTDDDDDWW...",
    ".WWWDDDDDDDDDDDDDDWWW...",
    "WWWWDDDDDDDDDDDDDDWWWW..",
    "WWWWWDDDDDDDDDDDDWWWWW..",
    ".WWWWDDDDDDDDDDDDWWWW...",
    "..WWWDDDDDDDDDDDDWWW....",
    "...WWDDDDDDDDDDDDWW.....",
    "....WWDDDDDDDDDDWW......",
    ".....DDDDDDDDDDDD.......",
    "......DDDDDDDDDD........",
    "......DDcDDDDcDD........",
    "......DDD....DDD........",
    ".....DDD......DDD.......",
    ".....DDD......DDD.......",
    "....CCC........CCC......",
]

SHOPKEEPER_PAL = {"H": (120, 80, 40), "S": SKIN, "E": EYE, "M": MOUTH, "C": (200, 90, 60), "A": (235, 235, 240), "P": PANTS, "B": BOOTS}
SHOPKEEPER = [
    ".....HHHHHH.....",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    ".HHSSSSSSSSSSHH.",
    ".HSSSSSSSSSSSSH.",
    ".HSSESSSSSSESH..",
    ".HSSSSMMSSSSSH..",
    "..CCCCCCCCCC....",
    ".CAAAAAAAAAAC...",
    ".CAAAAAAAAAAC...",
    ".SAAAAAAAAAAAS..",
    "..AAAAAAAAAA....",
    "..PPPPPPPPPP....",
    "..PPP....PPP....",
    "..PPP....PPP....",
    "..BBB....BBB....",
]

PRIESTESS_PAL = {"W": (240, 240, 250), "w": (200, 200, 220), "H": (240, 220, 140), "S": SKIN, "E": EYE, "M": MOUTH}
PRIESTESS = [
    "....HHHHHHHH....",
    "..HHHHHHHHHHHH..",
    ".WHHHHHHHHHHHHW.",
    ".WHSSSSSSSSSSHW.",
    ".WHSESSSSSSESHW.",
    ".WHSSSSMMSSSSHW.",
    "..WWSSSSSSWW....",
    "..WWWWWWWW......",
    ".WWWWWWWWWWWW...",
    ".WWWWWWWWWWWW...",
    ".WwWWWWWWWWwWW..",
    "..WWWWWWWWWW....",
    "..WWWWWWWWWW....",
    "..WWWWWWWWWW....",
    "..WWW....WWW....",
    "..www....www....",
]

VILLAGER_PAL = {"Y": (230, 200, 110), "H": (90, 60, 30), "S": SKIN, "E": EYE, "M": MOUTH, "C": (150, 110, 70), "P": (90, 70, 50), "B": BOOTS}
VILLAGER = [
    "....YYYYYYYY....",
    "..YYYYYYYYYYYY..",
    "..HHHHHHHHHHHH..",
    ".HHSSSSSSSSSSHH.",
    ".HSSSSSSSSSSSSH.",
    ".HSSESSSSSSESH..",
    ".HSSSSMMSSSSSH..",
    "..CCCCCCCCCC....",
    ".CCCCCCCCCCCC...",
    ".SCCCCCCCCCCS...",
    "..CCCCCCCCCC....",
    "..CCCCCCCCCC....",
    "..PPPPPPPPPP....",
    "..PPP....PPP....",
    "..PPP....PPP....",
    "..BBB....BBB....",
]

SPRITES = {
    "hero": (HERO, HERO_PAL),
    "hero_back": (HERO_BACK, HERO_PAL),
    "slime": (SLIME, SLIME_PAL),
    "goblin": (GOBLIN, GOBLIN_PAL),
    "wolf": (WOLF, WOLF_PAL),
    "skeleton": (SKELETON, SKELETON_PAL),
    "orc": (ORC, ORC_PAL),
    "mage": (MAGE, MAGE_PAL),
    "demon": (DEMON, DEMON_PAL),
    "shopkeeper": (SHOPKEEPER, SHOPKEEPER_PAL),
    "priestess": (PRIESTESS, PRIESTESS_PAL),
    "villager": (VILLAGER, VILLAGER_PAL),
}

for _name, (_rows, _pal) in SPRITES.items():
    _w = len(_rows[0])
    assert all(len(r) == _w for r in _rows), f"sprite {_name} not rectangular"

_sprite_cache = {}


def sprite(name, scale=1):
    key = (name, scale)
    if key not in _sprite_cache:
        rows, pal = SPRITES[name]
        h, w = len(rows), len(rows[0])
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                c = pal.get(ch)
                if c is not None:
                    s.set_at((x, y), (*c, 255))
        if scale != 1:
            s = pygame.transform.scale(s, (w * scale, h * scale))
        _sprite_cache[key] = s
    return _sprite_cache[key]


TILE_COLORS = {
    "grass": (105, 194, 90),
    "grass_dark": (77, 163, 68),
    "grass_light": (138, 217, 119),
    "path": (205, 180, 130),
    "path_dark": (170, 145, 100),
    "water": (70, 130, 220),
    "water_light": (120, 180, 245),
    "water_dark": (45, 95, 175),
    "trunk": (110, 72, 40),
    "leaf": (46, 139, 60),
    "leaf_dark": (34, 110, 48),
    "leaf_light": (86, 180, 90),
    "wall": (220, 200, 160),
    "roof": (170, 70, 60),
    "roof_green": (70, 140, 90),
    "window": (90, 60, 40),
    "door_gold": (230, 180, 60),
    "door_blue": (80, 120, 220),
    "dfloor": (45, 42, 58),
    "dfloor_dark": (30, 28, 40),
    "glow": (150, 80, 200),
    "boss_red": (200, 40, 60),
}

_tile_cache = {}


def _grass_base(s, seed):
    c = TILE_COLORS
    s.fill(c["grass"])
    rng = random.Random(seed)
    for _ in range(16):
        x, y = rng.randrange(32), rng.randrange(32)
        s.set_at((x, y), c["grass_dark"] if rng.random() < 0.7 else c["grass_light"])
    for _ in range(4):
        x, y = rng.randrange(30), rng.randrange(30)
        s.fill(c["grass_dark"], (x, y, 2, 1))


def _draw_tile(ch, seed, tick):
    c = TILE_COLORS
    s = pygame.Surface((data.TILE, data.TILE))
    if ch in (".", "G", "f", "T", "s"):
        _grass_base(s, seed)
    if ch == "G":
        rng = random.Random(seed + 1)
        for _ in range(7):
            x = rng.randrange(4, 28)
            y = rng.randrange(10, 28)
            pygame.draw.line(s, (46, 125, 50), (x, y), (x + rng.choice((-2, 0, 2)), y - rng.randrange(6, 12)), 2)
            pygame.draw.line(s, (124, 217, 119), (x, y - 6), (x, y - 9), 1)
    elif ch == "f":
        rng = random.Random(seed + 2)
        for _ in range(3):
            x, y = rng.randrange(6, 26), rng.randrange(8, 24)
            petal = rng.choice([(255, 130, 180), (245, 245, 250), (255, 200, 90)])
            pygame.draw.line(s, (46, 125, 50), (x, y + 4), (x, y + 7), 1)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                s.set_at((x + dx, y + dy), petal)
            s.set_at((x, y), (255, 230, 90))
    elif ch == "T":
        pygame.draw.rect(s, c["trunk"], (13, 18, 6, 14))
        s.fill(c["trunk"], (14, 26, 4, 6))
        pygame.draw.circle(s, c["leaf_dark"], (16, 13), 11)
        pygame.draw.circle(s, c["leaf"], (16, 12), 9)
        pygame.draw.circle(s, c["leaf_light"], (12, 8), 4)
    elif ch == "W":
        s.fill(c["water"])
        off = (tick // 18) % 2
        for i, y in enumerate((6, 14, 22, 30)):
            yy = (y + off * 4) % 32
            pygame.draw.line(s, c["water_light"], (4 + i * 5, yy), (12 + i * 5, yy), 2)
        pygame.draw.line(s, c["water_dark"], (0, 31), (31, 31), 1)
    elif ch == "=":
        s.fill(c["path"])
        rng = random.Random(seed)
        for _ in range(12):
            s.set_at((rng.randrange(32), rng.randrange(32)), c["path_dark"])
    elif ch == "B":
        s.fill(c["roof"], (0, 0, 32, 10))
        pygame.draw.rect(s, c["roof"], (2, 8, 28, 6))
        s.fill(c["wall"], (2, 14, 28, 18))
        s.fill(c["window"], (8, 20, 6, 6))
        s.fill(c["window"], (18, 20, 6, 6))
        pygame.draw.rect(s, (60, 40, 30), (0, 0, 32, 32), 1)
    elif ch == "S":
        s.fill(c["roof"], (0, 0, 32, 8))
        for x in range(0, 32, 8):
            s.fill((232, 69, 69) if (x // 8) % 2 == 0 else (245, 245, 250), (x, 8, 8, 5))
        s.fill(c["wall"], (2, 13, 28, 19))
        s.fill(c["door_gold"], (11, 16, 10, 16))
        s.set_at((18, 24), (120, 90, 20))
        s.fill((255, 230, 120), (13, 6, 6, 4))
        pygame.draw.rect(s, (60, 40, 30), (0, 0, 32, 32), 1)
    elif ch == "I":
        s.fill(c["roof_green"], (0, 0, 32, 10))
        s.fill(c["wall"], (2, 14, 28, 18))
        s.fill(c["door_blue"], (11, 17, 10, 15))
        s.fill((245, 245, 250), (15, 4, 2, 6))
        s.fill((245, 245, 250), (13, 6, 6, 2))
        pygame.draw.rect(s, (60, 40, 30), (0, 0, 32, 32), 1)
    elif ch in ("F", "E", "X"):
        s.fill(c["dfloor"])
        rng = random.Random(seed)
        for _ in range(5):
            x, y = rng.randrange(28), rng.randrange(28)
            pygame.draw.line(s, c["dfloor_dark"], (x, y), (x + rng.randrange(3, 6), y + rng.randrange(-2, 3)), 1)
        if ch == "E":
            pygame.draw.rect(s, (20, 16, 28), (8, 4, 16, 28))
            pygame.draw.rect(s, c["glow"], (10, 8, 12, 24))
            pygame.draw.rect(s, (200, 140, 255), (13, 14, 6, 18))
        elif ch == "X":
            pygame.draw.circle(s, c["boss_red"], (16, 16), 11, 2)
            pygame.draw.circle(s, (255, 90, 110), (16, 16), 6, 1)
            s.set_at((16, 16), (255, 90, 110))
    elif ch == "s":
        s.fill(c["trunk"], (14, 16, 4, 16))
        pygame.draw.rect(s, (160, 120, 70), (6, 4, 20, 12))
        pygame.draw.rect(s, (90, 60, 30), (6, 4, 20, 12), 1)
        s.fill((60, 40, 20), (9, 8, 14, 1))
        s.fill((60, 40, 20), (9, 11, 10, 1))
    return s


def tile(ch, seed=0, tick=0):
    key = (ch, seed, tick if ch == "W" else 0)
    if key not in _tile_cache:
        _tile_cache[key] = _draw_tile(ch, seed, tick)
    return _tile_cache[key]
