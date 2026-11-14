from collections import deque

import pygame

from . import core, data, pix, sfx, ui

PANEL_Y = 430

ELEMENT_SFX = {"fire": "fire", "ice": "ice", "holy": "holy", "dark": "dark", "phys": "slash", "water": "ice"}
ELEMENT_COLOR = {"fire": (255, 140, 60), "ice": (140, 220, 255), "holy": (255, 240, 160),
                 "dark": (190, 110, 255), "phys": (245, 245, 250), "water": (110, 170, 255)}


class Floater:
    def __init__(self, text, x, y, color, size=28):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.ttl = 1.1

    def update(self, dt):
        self.ttl -= dt
        self.y -= dt * 40

    def render(self, surf):
        ui.draw_text(surf, self.text, (int(self.x), int(self.y)), self.size, self.color)


class BattleScene:
    def __init__(self, game, enemy_id, zone, boss=False):
        self.game = game
        self.battle = core.Battle(game.player, enemy_id, game.rng, boss=boss)
        self.zone = zone
        self.boss = boss
        self.enemy = self.battle.enemy
        self.state = "cmd"
        self.cmd_menu = ui.Menu(["Attack", "Skills", "Item", "Defend", "Flee"], 600, PANEL_Y + 70, 26, 8)
        self.skill_menu = None
        self.item_menu = None
        self.events = deque()
        self.floaters = []
        self.shake = 0
        self.enemy_flash = 0
        self.player_flash = 0
        self.log = f"A wild {self.enemy.name} appears!"
        self.anim_t = 0
        self.over_shown = False
        self.rewards = None
        self.done = False
        self.enemy_surf = pix.sprite(self.enemy.sprite, self.enemy.scale)
        self.hero_surf = pix.sprite("hero_back", 4)
        self.bg = self._make_bg()
        sfx.play("encounter")

    def _make_bg(self):
        s = pygame.Surface((data.WIDTH, PANEL_Y))
        if self.zone == "dungeon":
            for y in range(PANEL_Y):
                t = y / PANEL_Y
                s.fill((int(30 - 10 * t), int(26 - 8 * t), int(44 - 12 * t)), (0, y, data.WIDTH, 1))
            for tx in (140, 820):
                pygame.draw.circle(s, (120, 60, 160, 60), (tx, 90), 46)
                pygame.draw.circle(s, (200, 120, 255), (tx, 90), 22)
                pygame.draw.rect(s, (90, 60, 40), (tx - 4, 110, 8, 60))
            pygame.draw.rect(s, (52, 48, 70), (0, PANEL_Y - 60, data.WIDTH, 60))
        else:
            for y in range(PANEL_Y):
                t = y / PANEL_Y
                r = int(135 + (210 - 135) * t)
                g = int(206 + (240 - 206) * t)
                b = int(250 + (170 - 250) * t)
                s.fill((r, g, b), (0, y, data.WIDTH, 1))
            pygame.draw.circle(s, (120, 200, 110), (140, PANEL_Y - 40), 120)
            pygame.draw.circle(s, (110, 195, 100), (830, PANEL_Y - 30), 140)
            pygame.draw.rect(s, (96, 180, 84), (0, PANEL_Y - 70, data.WIDTH, 70))
            pygame.draw.ellipse(s, (120, 205, 100), (250, PANEL_Y - 90, 460, 60))
        return s

    def _enemy_pos(self):
        return (620, 250)

    def _player_pos(self):
        return (230, 330)

    def submit(self, cmd, arg=None):
        evs = self.battle.player_action(cmd, arg)
        self.events.extend(evs)
        self.state = "anim"
        self.anim_t = 0.0

    def _apply_event(self, ev):
        t = ev["type"]
        if t == "msg":
            self.log = ev["text"]
        elif t == "hit":
            if ev["target"] == "enemy":
                self.enemy_flash = 0.18
                col = ELEMENT_COLOR.get(ev.get("element"), (245, 245, 250))
                label = f"-{ev['dmg']}"
                if ev["crit"]:
                    label = f"CRIT -{ev['dmg']}"
                if ev.get("mult", 1.0) > 1.0 and not ev["crit"]:
                    label += "!"
                self.floaters.append(Floater(label, *self._enemy_pos(), col, 30 if ev["crit"] else 26))
                self.shake = 10
                sfx.play(ELEMENT_SFX.get(ev.get("element"), "slash"))
            else:
                self.player_flash = 0.18
                label = f"-{ev['dmg']}"
                if ev["crit"]:
                    label = f"CRIT -{ev['dmg']}"
                self.floaters.append(Floater(label, *self._player_pos(), (255, 90, 90), 30 if ev["crit"] else 26))
                self.shake = 8
                sfx.play("hurt")
                if ev.get("phoenix"):
                    self.floaters.append(Floater("PHOENIX DOWN!", self._player_pos()[0], self._player_pos()[1] - 60, (255, 160, 60), 26))
                    self.log = "The Phoenix Down revives you!"
            if ev.get("drained"):
                tgt = self._player_pos() if ev["target"] == "enemy" else self._enemy_pos()
                self.floaters.append(Floater(f"+{ev['drained']}", tgt[0], tgt[1] - 40, (120, 255, 140), 22))
        elif t == "heal":
            tgt = self._player_pos() if ev["target"] == "player" else self._enemy_pos()
            self.floaters.append(Floater(f"+{ev['amount']}", tgt[0], tgt[1] - 40, (120, 255, 140), 26))
            sfx.play("heal")
        elif t == "mp":
            self.floaters.append(Floater(f"+{ev['amount']} MP", *self._player_pos(), (110, 160, 255), 24))
            sfx.play("heal")
        elif t == "faint":
            if ev["target"] == "enemy":
                self.log = f"{self.enemy.name} fainted!"
                sfx.play("win")
            else:
                self.log = f"{data.HERO_NAME} fainted..."
                sfx.play("lose")
        elif t == "win":
            self.rewards = ev
            sfx.play("win")
            if ev["levels"]:
                sfx.play("levelup")
        elif t == "lose":
            sfx.play("lose")
        elif t == "fled":
            self.log = "Got away safely!"
            sfx.play("door")

    def handle_key(self, key):
        if self.done:
            return
        if self.state == "over":
            if key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE, pygame.K_z):
                sfx.play("confirm")
                self.done = True
                self.game.on_battle_end(self.battle.result, self.battle)
            return
        if self.state == "anim":
            while self.events:
                self._apply_event(self.events.popleft())
            return
        if self.state == "cmd":
            r = self.cmd_menu.handle_key(key)
            if r == "back":
                return
            if r is None:
                return
            if r == 0:
                self.submit("attack")
            elif r == 1:
                self.state = "skill"
                skills = self.game.player.known_skills()
                self.skill_menu = ui.Menu(
                    [f"{data.SKILLS[s]['name']}  ({data.SKILLS[s]['mp']} MP)" for s in skills],
                    600, PANEL_Y + 40, 24, 6)
                self.skill_menu.ids = skills
                self.skill_menu.disabled = {i for i, s in enumerate(skills)
                                            if not self.game.player.can_cast(s)}
            elif r == 2:
                self.state = "item"
                inv = self.game.player.inventory
                ids = [k for k in data.ITEMS if inv.get(k, 0) > 0 and data.ITEMS[k].get("battle", True)]
                if not ids:
                    self.log = "No usable items!"
                    sfx.play("cancel")
                    return
                self.item_menu = ui.Menu([f"{data.ITEMS[k]['name']} x{inv[k]}" for k in ids],
                                         600, PANEL_Y + 40, 24, 6)
                self.item_menu.ids = ids
            elif r == 3:
                self.submit("defend")
            elif r == 4:
                self.submit("flee")
        elif self.state == "skill":
            r = self.skill_menu.handle_key(key)
            if r == "back":
                self.state = "cmd"
                return
            if r is None:
                return
            self.submit("skill", self.skill_menu.ids[r])
            self.state = "cmd"
        elif self.state == "item":
            r = self.item_menu.handle_key(key)
            if r == "back":
                self.state = "cmd"
                return
            if r is None:
                return
            self.submit("item", self.item_menu.ids[r])
            self.state = "cmd"

    def update(self, dt):
        self.shake = max(0.0, self.shake - dt * 40)
        self.enemy_flash = max(0.0, self.enemy_flash - dt)
        self.player_flash = max(0.0, self.player_flash - dt)
        for f in self.floaters:
            f.update(dt)
        self.floaters = [f for f in self.floaters if f.ttl > 0]
        if self.state == "anim":
            self.anim_t += dt
            if self.anim_t > 0.45:
                self.anim_t = 0.0
                if self.events:
                    self._apply_event(self.events.popleft())
                else:
                    if self.battle.over:
                        self.state = "over"
                        if self.battle.result == "fled":
                            self.done = True
                            self.game.on_battle_end("fled", self.battle)
                    else:
                        self.state = "cmd"

    def render(self, surf):
        ox, oy = (int((self.shake * 0.5) * (1 if (int(self.shake * 10) % 2 == 0) else -1)), 0) if self.shake > 0 else (0, 0)
        surf.blit(self.bg, (ox, oy))

        ex, ey = self._enemy_pos()
        if self.enemy.hp > 0:
            bob = int(abs(pygame.time.get_ticks() / 300) % 2) * 3
            es = self.enemy_surf
            if self.enemy_flash > 0:
                es = es.copy()
                es.fill((255, 255, 255, 140))
            surf.blit(es, (ex - es.get_width() // 2 + ox, ey - es.get_height() + bob + oy))
            ui.draw_text(surf, self.enemy.name, (ex - 90 + ox, ey - es.get_height() - 44 + oy), 26, (255, 220, 100))
            ui.bar(surf, (ex - 90 + ox, ey - es.get_height() - 20 + oy, 180, 12),
                   self.enemy.hp / self.enemy.max_hp, ui.HP_LOW if self.enemy.hp < self.enemy.max_hp * 0.3 else ui.HP)

        px, py = self._player_pos()
        hs = self.hero_surf
        if self.player_flash > 0:
            hs = hs.copy()
            hs.fill((255, 80, 80), special_flags=pygame.BLEND_RGB_MULT)
        if self.battle.player.hp > 0:
            surf.blit(hs, (px - hs.get_width() // 2 + ox, py - hs.get_height() + oy))
        else:
            rot = pygame.transform.rotate(hs, -70)
            surf.blit(rot, (px - rot.get_width() // 2 + ox, py - rot.get_height() + oy))

        for f in self.floaters:
            f.render(surf)

        ui.panel(surf, (0, PANEL_Y, data.WIDTH, data.HEIGHT - PANEL_Y))
        pygame.draw.line(surf, (250, 220, 120), (0, PANEL_Y), (data.WIDTH, PANEL_Y), 2)
        p = self.game.player
        ui.draw_text(surf, f"{data.HERO_NAME}   LV {p.level}", (24, PANEL_Y + 14), 26)
        ui.draw_text(surf, "HP", (24, PANEL_Y + 48), 20, ui.TEXT_DIM)
        ui.bar(surf, (58, PANEL_Y + 48, 220, 16), p.hp / p.max_hp, ui.HP_LOW if p.hp < p.max_hp * 0.3 else ui.HP)
        ui.draw_text(surf, f"{p.hp}/{p.max_hp}", (286, PANEL_Y + 47), 18)
        ui.draw_text(surf, "MP", (24, PANEL_Y + 74), 20, ui.TEXT_DIM)
        ui.bar(surf, (58, PANEL_Y + 74, 220, 16), p.mp / p.max_mp, ui.MP)
        ui.draw_text(surf, f"{p.mp}/{p.max_mp}", (286, PANEL_Y + 73), 18)
        ui.draw_text(surf, "XP", (24, PANEL_Y + 100), 20, ui.TEXT_DIM)
        ui.bar(surf, (58, PANEL_Y + 100, 220, 12), p.xp / p.xp_next(), ui.XP)
        ui.draw_text(surf, self.log, (24, PANEL_Y + 126), 20, ui.TEXT_DIM)

        if self.state == "cmd":
            self.cmd_menu.render(surf)
            ui.draw_text(surf, "Choose a command", (600, PANEL_Y + 40), 22, ui.TEXT_DIM)
        elif self.state == "skill":
            self.skill_menu.render(surf)
            sel = self.skill_menu.sel
            if sel < len(self.skill_menu.ids):
                sid = self.skill_menu.ids[sel]
                ui.draw_text(surf, data.SKILLS[sid]["desc"], (600, PANEL_Y + 40), 18, ui.TEXT_DIM)
        elif self.state == "item":
            self.item_menu.render(surf)

        if self.state == "over" and self.battle.over:
            r = self.battle.result
            if r == "win" and self.rewards:
                ui.panel(surf, (330, 120, 380, 220))
                ui.draw_text(surf, "VICTORY!", (520, 140), 36, (255, 220, 100), align="center")
                ui.draw_text(surf, f"+{self.rewards['xp']} XP", (370, 190), 26)
                ui.draw_text(surf, f"+{self.rewards['gold']} G", (370, 224), 26, (255, 220, 100))
                if self.rewards["levels"]:
                    lv = ", ".join(str(l) for l in self.rewards["levels"])
                    ui.draw_text(surf, f"LEVEL UP! Now LV {p.level} ({lv})", (370, 258), 22, (120, 255, 140))
                    news = [data.SKILLS[s]["name"] for s in p.skills
                            if data.SKILLS[s]["min_level"] in self.rewards["levels"]]
                    if news:
                        ui.draw_text(surf, f"New skill: {', '.join(news)}", (370, 288), 20, (160, 200, 255))
                ui.draw_text(surf, "Press E to continue", (520, 316), 20, ui.TEXT_DIM, align="center")
            elif r == "lose":
                ui.panel(surf, (330, 120, 380, 160))
                ui.draw_text(surf, "DEFEATED...", (520, 170), 36, (255, 90, 90), align="center")
                ui.draw_text(surf, "Press E to continue", (520, 230), 20, ui.TEXT_DIM, align="center")
