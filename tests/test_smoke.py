import collections
import json
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from isekai import core, data
from isekai.game import Game

PREVIEW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "preview")
SAVE = data.SAVE_FILE


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def no_keys():
    return collections.defaultdict(lambda: False)


def pump_dialog(g, choice_key=pygame.K_RETURN):
    guard = 0
    while g.dialog is not None:
        g.update(1.0)
        if g.dialog is not None:
            g.handle_event(key(choice_key))
        guard += 1
        assert guard < 500, "dialog did not finish"


def pump_battle(g, use_skill=False):
    guard = 0
    while g.state == "battle":
        bs = g.battle_scene
        if bs.state == "cmd":
            if use_skill and g.player.can_cast("fire"):
                bs.submit("skill", "fire")
            else:
                bs.submit("attack")
        elif bs.state == "anim":
            bs.update(0.5)
        elif bs.state == "over":
            bs.handle_key(pygame.K_RETURN)
        g.update(1 / 60)
        guard += 1
        assert guard < 2000, "battle did not end"


def shot(g, name):
    pygame.image.save(g.screen, os.path.join(PREVIEW, name))


def main():
    if os.path.exists(SAVE):
        os.remove(SAVE)
    pygame.init()
    g = Game()
    assert g.state == "title"
    g.render()
    shot(g, "smoke_title.png")

    g.handle_event(key(pygame.K_RETURN))
    assert g.state == "overworld" and g.dialog is not None
    pump_dialog(g)
    assert g.dialog is None and g.state == "overworld"
    g.render()
    shot(g, "smoke_overworld.png")

    pressed = collections.defaultdict(lambda: False)
    orig = pygame.key.get_pressed
    pygame.key.get_pressed = lambda: pressed
    pressed[pygame.K_UP] = True
    start_y = g.player.y
    for _ in range(30):
        g.update(0.05)
    pygame.key.get_pressed = orig
    assert g.player.y < start_y, "player did not move up"

    g.start_battle("meadow")
    assert g.state == "battle"
    g.battle_scene.update(0.5)
    g.render()
    shot(g, "smoke_battle.png")
    gold_before = g.player.gold
    pump_battle(g, use_skill=True)
    assert g.state == "overworld", g.state
    assert g.player.gold >= gold_before

    g.open_shop()
    assert g.state == "shop"
    g.render()
    shot(g, "smoke_shop.png")
    potions_before = g.player.inventory.get("potion", 0)
    gold_before = g.player.gold
    g.shop.handle_key(pygame.K_RETURN)
    assert g.player.inventory.get("potion", 0) == potions_before + 1
    assert g.player.gold == gold_before - data.ITEMS["potion"]["price"]
    g.shop.handle_key(pygame.K_ESCAPE)
    assert g.state == "overworld"

    g.player.hp = 5
    g.inn()
    pump_dialog(g)
    assert g.player.hp == g.player.max_hp
    assert g.player.gold == gold_before - data.ITEMS["potion"]["price"] - data.INN_COST

    g.save()
    g2 = Game()
    g2.handle_event(key(pygame.K_DOWN))
    g2.handle_event(key(pygame.K_RETURN))
    assert g2.state == "overworld" and g2.player is not None
    assert g2.player.to_dict() == g.player.to_dict()

    g.player.atk = 999
    g.start_battle("dungeon", boss=True)
    pump_battle(g)
    assert g.player.flags.get("boss_dead") is True
    pump_dialog(g)
    pump_dialog(g)
    assert g.state == "title"
    assert any("Journey+" in i for i in g.title_items)

    g.handle_event(key(pygame.K_RETURN))
    assert g.state == "overworld"
    pump_dialog(g)
    g.player.atk = 1
    g.start_battle("dungeon", boss=True)
    bs = g.battle_scene
    guard = 0
    while g.state == "battle":
        if bs.state == "cmd":
            bs.submit("defend")
        elif bs.state == "anim":
            bs.update(0.5)
        elif bs.state == "over":
            bs.handle_key(pygame.K_RETURN)
        g.update(1 / 60)
        guard += 1
        assert guard < 2000
    assert g.state == "gameover"
    gold_before = g.player.gold
    pump_dialog(g)
    assert g.state == "overworld"
    assert g.player.hp == g.player.max_hp
    assert g.player.gold == int(gold_before * 0.7)
    assert (g.player.x, g.player.y) == data.PLAYER_START

    g.render()
    shot(g, "smoke_overworld2.png")
    print("SMOKE OK")


if __name__ == "__main__":
    main()
