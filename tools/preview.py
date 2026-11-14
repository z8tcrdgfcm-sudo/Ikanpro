import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from isekai import data, pix

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "preview")


def main():
    pygame.init()
    pygame.display.set_mode((data.WIDTH, data.HEIGHT))

    sheet = pygame.Surface((16 * 5 * 4, 16 * 5 * 4))
    sheet.fill((30, 32, 50))
    names = list(pix.SPRITES.keys())
    cell = 16 * 4
    for i, name in enumerate(names):
        s = pix.sprite(name, 4)
        x = (i % 5) * cell
        y = (i // 5) * cell
        sheet.blit(s, (x + (cell - s.get_width()) // 2, y + (cell - s.get_height()) // 2))
        pygame.draw.rect(sheet, (90, 90, 120), (x, y, cell - 1, cell - 1), 1)
    pygame.image.save(sheet, os.path.join(OUT, "sprites.png"))

    world = pygame.Surface((data.WIDTH, data.HEIGHT))
    for y in range(data.MAP_H):
        for x in range(data.MAP_W):
            world.blit(pix.tile(data.MAP[y][x], seed=x * 31 + y * 7, tick=0), (x * data.TILE, y * data.TILE))
    for npc in data.NPCS.values():
        x, y = npc["pos"]
        world.blit(pix.sprite(npc["sprite"], 2), (x * data.TILE, y * data.TILE - 8))
    hx, hy = data.PLAYER_START
    world.blit(pix.sprite("hero", 2), (hx * data.TILE, hy * data.TILE - 8))
    pygame.image.save(world, os.path.join(OUT, "map.png"))

    tiles = pygame.Surface((32 * 14, 32 * 2))
    tiles.fill((30, 32, 50))
    for i, ch in enumerate(".GfT W=BSIFEXs"):
        if ch == " ":
            continue
        tiles.blit(pix.tile(ch, seed=3, tick=0), ((i % 14) * 32, (i // 14) * 32))
    pygame.image.save(tiles, os.path.join(OUT, "tiles.png"))
    print("preview written to", OUT)


if __name__ == "__main__":
    main()
