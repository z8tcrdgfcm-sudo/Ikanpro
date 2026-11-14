import pygame

from . import core, data, pix, sfx, ui

MOVE_TIME = 0.13

DIR_KEYS = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
}


class Overworld:
    def __init__(self, game):
        self.game = game
        p = game.player
        self.tx, self.ty = p.x, p.y
        self.x = self.tx * data.TILE
        self.y = self.ty * data.TILE - 8
        self.dir = (0, 1)
        self.moving = False
        self.mfrom = (0, 0)
        self.mto = (0, 0)
        self.mt = 0.0
        self.bob = 0.0
        self.tick = 0
        self.hint = "WASD/Arrows: move   E: talk   ESC: menu"

    def npc_at(self, x, y):
        for nid, n in data.NPCS.items():
            if n["pos"] == (x, y):
                return nid, n
        return None, None

    def walkable(self, x, y):
        if not (0 <= x < data.MAP_W and 0 <= y < data.MAP_H):
            return False
        if data.MAP[y][x] not in data.WALKABLE:
            return False
        if self.npc_at(x, y)[0]:
            return False
        return True

    def try_start_move(self, d):
        nx, ny = self.tx + d[0], self.ty + d[1]
        if self.walkable(nx, ny):
            self.dir = d
            self.moving = True
            self.mt = 0.0
            self.mfrom = (self.x, self.y)
            self.mto = (nx * data.TILE, ny * data.TILE - 8)
            self.tx, self.ty = nx, ny
            sfx.play("step")
            return True
        self.dir = d
        return False

    def on_enter_tile(self):
        ch = data.MAP[self.ty][self.tx]
        g = self.game
        p = g.player
        p.x, p.y = self.tx, self.ty
        if ch in data.ZONE_OF_TILE and g.rng.random() < data.ENCOUNTER_CHANCE:
            g.start_battle(data.ZONE_OF_TILE[ch])
            return
        if ch == "X" and not p.flags.get("boss_dead"):
            g.set_dialog(data.DIALOGS["boss_pre"],
                         on_done=lambda: g.start_battle("dungeon", boss=True))
            return
        if ch == "S":
            g.open_shop()
            return
        if ch == "I":
            g.inn()
            return

    def interact(self):
        fx, fy = self.tx + self.dir[0], self.ty + self.dir[1]
        nid, n = self.npc_at(fx, fy)
        if nid:
            if n.get("opens_shop"):
                self.game.open_shop()
            else:
                self.game.set_dialog(data.DIALOGS[n["dialog"]])
            return
        if 0 <= fx < data.MAP_W and 0 <= fy < data.MAP_H and data.MAP[fy][fx] == "s":
            self.game.set_dialog(data.DIALOGS["sign"])

    def handle_key(self, key):
        if key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
            if not self.moving:
                self.interact()

    def update(self, dt, keys):
        self.tick += dt
        self.bob += dt
        if self.moving:
            self.mt += dt
            t = min(1.0, self.mt / MOVE_TIME)
            self.x = self.mfrom[0] + (self.mto[0] - self.mfrom[0]) * t
            self.y = self.mfrom[1] + (self.mto[1] - self.mfrom[1]) * t
            if t >= 1.0:
                self.moving = False
                self.x, self.y = self.mto
                self.on_enter_tile()
                return
        if not self.moving:
            for key, d in DIR_KEYS.items():
                if keys[key]:
                    self.try_start_move(d)
                    break

    def render(self, surf):
        for y in range(data.MAP_H):
            for x in range(data.MAP_W):
                surf.blit(pix.tile(data.MAP[y][x], seed=x * 31 + y * 7,
                                   tick=int(self.tick * 10)), (x * data.TILE, y * data.TILE))
        for npc in data.NPCS.values():
            nx, ny = npc["pos"]
            bob = int(abs(self.bob * 3) % 2)
            surf.blit(pix.sprite(npc["sprite"], 2), (nx * data.TILE, ny * data.TILE - 8 - bob))
        bob = int(abs(self.bob * 6) % 3) if self.moving else 0
        spr = pix.sprite("hero", 2)
        if self.dir[0] < 0:
            spr = pygame.transform.flip(spr, True, False)
        surf.blit(spr, (int(self.x), int(self.y) - bob))

        p = self.game.player
        ui.panel(surf, (8, 8, 300, 96))
        ui.draw_text(surf, f"{data.HERO_NAME}  LV {p.level}", (20, 16), 24)
        ui.draw_text(surf, "HP", (20, 44), 20, ui.TEXT_DIM)
        ui.bar(surf, (52, 44, 180, 14), p.hp / p.max_hp, ui.HP_LOW if p.hp < p.max_hp * 0.3 else ui.HP)
        ui.draw_text(surf, f"{p.hp}/{p.max_hp}", (238, 42), 18)
        ui.draw_text(surf, "MP", (20, 66), 20, ui.TEXT_DIM)
        ui.bar(surf, (52, 66, 180, 14), p.mp / p.max_mp, ui.MP)
        ui.draw_text(surf, f"{p.mp}/{p.max_mp}", (238, 64), 18)
        ui.draw_text(surf, f"Gold: {p.gold} G", (20, 86), 20, (255, 220, 100))

        ui.panel(surf, (8, data.HEIGHT - 34, 620, 26), bg=(10, 12, 24, 200), edge=(90, 90, 120))
        ui.draw_text(surf, self.hint, (18, data.HEIGHT - 30), 18, ui.TEXT_DIM)
