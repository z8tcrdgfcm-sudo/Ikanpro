import json
import os
import random

import pygame

from . import core, data, overworld, pix, sfx, ui
from .battle import BattleScene

TITLE_BG_SEED_TICK = 0


class Shop:
    def __init__(self, game):
        self.game = game
        self.rows = []
        for iid in data.SHOP_STOCK:
            it = data.ITEMS[iid]
            self.rows.append(("item", iid, f"{it['name']} - {it['desc']}", it["price"]))
        w = data.WEAPONS[game.player.weapon]
        if game.player.weapon + 1 < len(data.WEAPONS):
            nw = data.WEAPONS[game.player.weapon + 1]
            self.rows.append(("weapon", game.player.weapon + 1,
                              f"{nw[0]}  (+{nw[1]} ATK)", nw[2]))
        else:
            self.rows.append(("weapon", None, f"{w[0]} (max weapon)", None))
        a = data.ARMORS[game.player.armor]
        if game.player.armor + 1 < len(data.ARMORS):
            na = data.ARMORS[game.player.armor + 1]
            self.rows.append(("armor", game.player.armor + 1,
                              f"{na[0]}  (+{na[1]} DEF)", na[2]))
        else:
            self.rows.append(("armor", None, f"{a[0]} (max armor)", None))
        self.menu = ui.Menu([r[2] if r[3] is not None else r[2] + "  [owned]" for r in self.rows],
                            60, 150, 24, 8)
        self.menu.disabled = {i for i, r in enumerate(self.rows)
                              if r[3] is None or r[3] > game.player.gold}
        self.msg = "Welcome! What'll it be?"

    def handle_key(self, key):
        r = self.menu.handle_key(key)
        if r == "back":
            self.game.close_shop()
            return
        if r is None:
            return
        kind, arg, label, price = self.rows[r]
        p = self.game.player
        if price is None or price > p.gold:
            self.msg = "Can't afford that!"
            sfx.play("cancel")
            return
        p.gold -= price
        if kind == "item":
            p.inventory[arg] = p.inventory.get(arg, 0) + 1
            self.msg = f"Bought {data.ITEMS[arg]['name']}!"
        elif kind == "weapon":
            p.weapon = arg
            self.msg = f"Equipped {data.WEAPONS[arg][0]}! ATK {p.eff_atk()}"
        elif kind == "armor":
            p.armor = arg
            self.msg = f"Equipped {data.ARMORS[arg][0]}! DEF {p.eff_def()}"
        sfx.play("coin")
        self.menu.disabled = {i for i, rr in enumerate(self.rows)
                              if rr[3] is None or rr[3] > p.gold}

    def render(self, surf):
        surf.fill((24, 20, 36))
        pygame.draw.rect(surf, (60, 45, 80), (0, 0, data.WIDTH, 90))
        ui.draw_text(surf, "THE EMPORIUM", (data.WIDTH // 2, 24), 44, (255, 220, 100), align="center")
        ui.draw_text(surf, f"Gold: {self.game.player.gold} G", (data.WIDTH // 2, 62), 24, (255, 220, 100), align="center")
        self.menu.render(surf)
        for i, r in enumerate(self.rows):
            if r[3] is not None:
                ui.draw_text(surf, f"{r[3]} G", (820, 150 + i * 32), 22,
                             (110, 110, 130) if i in self.menu.disabled else (255, 220, 100))
        ui.panel(surf, (40, data.HEIGHT - 70, data.WIDTH - 80, 50), bg=(10, 12, 24, 220))
        ui.draw_text(surf, self.msg, (60, data.HEIGHT - 56), 22)
        ui.draw_text(surf, "E/Enter: buy   ESC: leave", (data.WIDTH - 320, data.HEIGHT - 56), 20, ui.TEXT_DIM)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((data.WIDTH, data.HEIGHT))
        pygame.display.set_caption("Isekai Odyssey — Reborn in Aetheria")
        self.clock = pygame.time.Clock()
        self.rng = random.Random()
        self.player = None
        self.state = "title"
        self.title_items = ["New Game", "Continue", "Quit"]
        self.title_sel = 0
        self.overworld = None
        self.battle_scene = None
        self.shop = None
        self.dialog = None
        self.dialog_done = None
        self.menu = None
        self.status_view = False
        self.tick = 0.0
        self.map_bg = None
        self.refresh_title_items()

    def refresh_title_items(self):
        items = ["New Game"]
        if os.path.exists(data.SAVE_FILE):
            items.append("Continue")
            try:
                with open(data.SAVE_FILE) as f:
                    if json.load(f).get("player", {}).get("flags", {}).get("boss_dead"):
                        items.append("New Journey+ (hard mode)")
            except Exception:
                pass
        items.append("Quit")
        self.title_items = items
        self.title_sel = min(self.title_sel, len(items) - 1)

    def new_game(self, ngplus=False):
        self.player = core.Player(new_game_plus=ngplus)
        self.overworld = overworld.Overworld(self)
        self.state = "overworld"
        self.set_dialog(data.DIALOGS["intro"])

    def continue_game(self):
        try:
            with open(data.SAVE_FILE) as f:
                d = json.load(f)
            self.player = core.Player.from_dict(d["player"])
        except Exception:
            self.new_game()
            return
        self.overworld = overworld.Overworld(self)
        self.state = "overworld"

    def save(self):
        if self.player is None:
            return
        with open(data.SAVE_FILE, "w") as f:
            json.dump({"player": self.player.to_dict()}, f, indent=1)

    def set_dialog(self, lines, choices=None, on_choice=None, on_done=None):
        if isinstance(lines, dict):
            self.dialog = ui.Dialog(lines["lines"], choices=lines.get("choices"),
                                    on_choice=on_choice)
        else:
            self.dialog = ui.Dialog(lines, choices=choices, on_choice=on_choice)
        self.dialog_done = on_done

    def start_battle(self, zone, boss=False):
        enemy_id = data.BOSS_ID if boss else core.pick_encounter(zone, self.rng)
        self.battle_scene = BattleScene(self, enemy_id, zone, boss=boss)
        self.state = "battle"

    def on_battle_end(self, result, battle):
        p = self.player
        if result == "win":
            self.save()
            if battle.boss:
                p.flags["boss_dead"] = True
                self.save()
                self.state = "overworld"
                self.set_dialog(data.DIALOGS["boss_post"],
                                on_done=lambda: self.set_dialog(
                                    data.DIALOGS["ending"],
                                    on_done=lambda: self.to_title()))
            else:
                self.state = "overworld"
        elif result == "fled":
            self.state = "overworld"
        else:
            self.state = "gameover"
            self.set_dialog(data.DIALOGS["gameover"], on_done=self.respawn)

    def respawn(self):
        p = self.player
        p.hp = p.max_hp
        p.mp = p.max_mp
        p.gold = int(p.gold * 0.7)
        p.x, p.y = data.PLAYER_START
        self.overworld = overworld.Overworld(self)
        self.state = "overworld"
        self.save()

    def to_title(self):
        self.save()
        self.state = "title"
        self.refresh_title_items()

    def open_shop(self):
        self.shop = Shop(self)
        self.state = "shop"
        sfx.play("door")

    def close_shop(self):
        self.shop = None
        self.state = "overworld"
        self.save()
        sfx.play("door")

    def inn(self):
        def on_choice(sel):
            p = self.player
            if sel == 0:
                if p.gold >= data.INN_COST:
                    p.gold -= data.INN_COST
                    p.full_restore()
                    self.set_dialog(data.DIALOGS["inn_healed"])
                    sfx.play("heal")
                else:
                    self.set_dialog(data.DIALOGS["inn_no_gold"])
            self.save()
        self.set_dialog(data.DIALOGS["inn_choice"], on_choice=on_choice)

    def open_menu(self):
        self.menu = ui.Menu(["Status", "Save", "Quit to Title"], data.WIDTH // 2 - 80, 260, 28, 12)
        self.state = "menu"

    def get_map_bg(self):
        if self.map_bg is None:
            s = pygame.Surface((data.WIDTH, data.HEIGHT))
            for y in range(data.MAP_H):
                for x in range(data.MAP_W):
                    s.blit(pix.tile(data.MAP[y][x], seed=x * 31 + y * 7, tick=0),
                           (x * data.TILE, y * data.TILE))
            self.map_bg = s
        return self.map_bg

    def handle_event(self, ev):
        if ev.type == pygame.QUIT:
            self.save()
            return False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_m:
                sfx.toggle()
                return True
            if self.state == "title":
                if ev.key in (pygame.K_UP, pygame.K_w):
                    self.title_sel = (self.title_sel - 1) % len(self.title_items)
                    sfx.play("blip")
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.title_sel = (self.title_sel + 1) % len(self.title_items)
                    sfx.play("blip")
                elif ev.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                    sfx.play("confirm")
                    choice = self.title_items[self.title_sel]
                    if choice == "New Game":
                        self.new_game()
                    elif choice == "Continue":
                        self.continue_game()
                    elif choice.startswith("New Journey+"):
                        self.new_game(ngplus=True)
                    else:
                        self.save()
                        return False
            elif self.state == "overworld":
                if self.dialog:
                    self.dialog.handle_key(ev.key)
                elif ev.key == pygame.K_ESCAPE:
                    self.open_menu()
                else:
                    self.overworld.handle_key(ev.key)
            elif self.state == "battle":
                self.battle_scene.handle_key(ev.key)
            elif self.state == "shop":
                self.shop.handle_key(ev.key)
            elif self.state == "menu":
                r = self.menu.handle_key(ev.key)
                if r == "back":
                    self.state = "overworld"
                elif r == 0:
                    self.status_view = True
                    self.state = "status"
                elif r == 1:
                    self.save()
                    self.state = "overworld"
                elif r == 2:
                    self.to_title()
            elif self.state == "status":
                if ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_e):
                    self.state = "menu"
            elif self.state == "gameover":
                if self.dialog:
                    self.dialog.handle_key(ev.key)
        return True

    def update(self, dt):
        self.tick += dt
        if self.state == "overworld":
            if self.dialog:
                self.dialog.update(dt)
                if self.dialog.finished:
                    d = self.dialog
                    self.dialog = None
                    if self.dialog_done:
                        cb, self.dialog_done = self.dialog_done, None
                        cb()
                    elif d.on_choice and d.choices is None:
                        pass
            else:
                self.overworld.update(dt, pygame.key.get_pressed())
        elif self.state == "battle":
            self.battle_scene.update(dt)
            if self.battle_scene.done and self.state == "battle":
                pass
        elif self.state == "gameover":
            if self.dialog:
                self.dialog.update(dt)
                if self.dialog.finished:
                    cb, self.dialog_done = self.dialog_done, None
                    self.dialog = None
                    if cb:
                        cb()

    def render(self):
        s = self.screen
        if self.state == "title":
            s.blit(self.get_map_bg(), (0, 0))
            overlay = pygame.Surface((data.WIDTH, data.HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 30, 170))
            s.blit(overlay, (0, 0))
            ui.draw_text(s, "ISEKAI ODYSSEY", (data.WIDTH // 2, 120), 84, (255, 220, 100), align="center")
            ui.draw_text(s, "— Reborn in Aetheria —", (data.WIDTH // 2, 200), 36, (200, 220, 255), align="center")
            spr = pix.sprite("hero", 6)
            s.blit(spr, (data.WIDTH // 2 - spr.get_width() // 2, 250))
            for i, item in enumerate(self.title_items):
                y = 470 + i * 44
                color = (255, 220, 100) if i == self.title_sel else ui.TEXT
                if i == self.title_sel:
                    ui.draw_text(s, ">", (data.WIDTH // 2 - 130, y), 32, (255, 220, 100))
                ui.draw_text(s, item, (data.WIDTH // 2 - 110, y), 32, color)
            if int(self.tick * 2) % 2 == 0:
                ui.draw_text(s, "M: sound on/off", (data.WIDTH // 2, data.HEIGHT - 40), 20, ui.TEXT_DIM, align="center")
        elif self.state in ("overworld", "menu", "status", "gameover"):
            self.overworld.render(s)
            if self.state == "gameover":
                overlay = pygame.Surface((data.WIDTH, data.HEIGHT), pygame.SRCALPHA)
                overlay.fill((60, 0, 10, 160))
                s.blit(overlay, (0, 0))
                ui.draw_text(s, "YOU HAVE FALLEN...", (data.WIDTH // 2, 200), 60, (255, 90, 90), align="center")
            if self.dialog:
                self.dialog.render(s, (40, data.HEIGHT - 170, data.WIDTH - 80, 130))
            if self.state == "menu":
                overlay = pygame.Surface((data.WIDTH, data.HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                s.blit(overlay, (0, 0))
                ui.panel(s, (data.WIDTH // 2 - 160, 220, 320, 220))
                ui.draw_text(s, "MENU", (data.WIDTH // 2, 235), 32, (255, 220, 100), align="center")
                self.menu.render(s)
            elif self.state == "status":
                p = self.player
                overlay = pygame.Surface((data.WIDTH, data.HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 140))
                s.blit(overlay, (0, 0))
                ui.panel(s, (200, 90, 560, 460))
                ui.draw_text(s, f"{data.HERO_NAME} — LV {p.level}", (220, 110), 32, (255, 220, 100))
                ui.draw_text(s, f"XP {p.xp}/{p.xp_next()}", (220, 150), 22)
                ui.draw_text(s, f"HP {p.hp}/{p.max_hp}   MP {p.mp}/{p.max_mp}", (220, 180), 22)
                ui.draw_text(s, f"ATK {p.eff_atk()} ({data.WEAPONS[p.weapon][0]})", (220, 210), 22)
                ui.draw_text(s, f"DEF {p.eff_def()} ({data.ARMORS[p.armor][0]})", (220, 240), 22)
                ui.draw_text(s, f"SPD {p.spd}   Gold {p.gold} G", (220, 270), 22)
                ui.draw_text(s, "Skills:", (220, 310), 22, (160, 200, 255))
                ui.draw_text(s, ", ".join(data.SKILLS[s]["name"] for s in p.known_skills()), (220, 338), 20)
                ui.draw_text(s, "Items:", (220, 378), 22, (160, 200, 255))
                inv = ", ".join(f"{data.ITEMS[k]['name']} x{v}" for k, v in p.inventory.items() if v > 0) or "none"
                ui.draw_text(s, inv, (220, 406), 20)
                ui.draw_text(s, "Press ESC to go back", (480, 510), 20, ui.TEXT_DIM, align="center")
        elif self.state == "battle":
            self.battle_scene.render(s)
        elif self.state == "shop":
            self.shop.render(s)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for ev in pygame.event.get():
                if not self.handle_event(ev):
                    running = False
            self.update(dt)
            self.render()
        pygame.quit()
