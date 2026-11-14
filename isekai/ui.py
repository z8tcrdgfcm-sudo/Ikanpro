import pygame

from . import sfx

PANEL_BG = (18, 20, 38, 225)
PANEL_EDGE = (250, 220, 120)
TEXT = (245, 245, 250)
TEXT_DIM = (170, 170, 190)
HP = (80, 220, 100)
HP_LOW = (230, 70, 70)
MP = (80, 140, 255)
XP = (255, 210, 80)

_font_cache = {}


def font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


def draw_text(surf, text, pos, size=24, color=TEXT, outline=True, align="left"):
    f = font(size)
    img = f.render(text, True, color)
    x, y = pos
    if align == "center":
        x -= img.get_width() // 2
    elif align == "right":
        x -= img.get_width()
    if outline:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            o = f.render(text, True, (10, 10, 20))
            surf.blit(o, (x + dx, y + dy))
    surf.blit(img, (x, y))
    return img.get_width()


def panel(surf, rect, bg=PANEL_BG, edge=PANEL_EDGE, width=2):
    r = pygame.Rect(rect)
    pygame.draw.rect(surf, bg[:3], r, border_radius=8)
    pygame.draw.rect(surf, edge, r, width, border_radius=8)


def bar(surf, rect, frac, color, bg=(40, 42, 60)):
    r = pygame.Rect(rect)
    pygame.draw.rect(surf, bg, r, border_radius=3)
    frac = max(0.0, min(1.0, frac))
    if frac > 0:
        pygame.draw.rect(surf, color, (r.x + 2, r.y + 2, int((r.w - 4) * frac), r.h - 4), border_radius=2)
    pygame.draw.rect(surf, (10, 10, 20), r, 1, border_radius=3)


class Menu:
    def __init__(self, items, x, y, size=24, gap=6, color=TEXT, disabled=None):
        self.items = items
        self.x = x
        self.y = y
        self.size = size
        self.gap = gap
        self.sel = 0
        self.color = color
        self.disabled = disabled or set()

    def handle_key(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.sel = (self.sel - 1) % len(self.items)
            sfx.play("blip")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.sel = (self.sel + 1) % len(self.items)
            sfx.play("blip")
        elif key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
            if self.sel in self.disabled:
                sfx.play("cancel")
                return None
            sfx.play("confirm")
            return self.sel
        elif key in (pygame.K_ESCAPE, pygame.K_q):
            return "back"
        return None

    def render(self, surf):
        for i, item in enumerate(self.items):
            y = self.y + i * (self.size + self.gap)
            disabled = i in self.disabled
            color = (110, 110, 130) if disabled else self.color
            label = item if isinstance(item, str) else item[0]
            if i == self.sel and not disabled:
                draw_text(surf, ">", (self.x - 18, y), self.size, (255, 220, 100))
            draw_text(surf, label, (self.x, y), self.size, color)


class Dialog:
    def __init__(self, lines, choices=None, on_choice=None):
        self.lines = list(lines)
        self.choices = choices
        self.on_choice = on_choice
        self.idx = 0
        self.chars = 0
        self.done = False
        self.choice_sel = 0
        self.choosing = False
        self.finished = False

    @property
    def current(self):
        return self.lines[self.idx] if self.idx < len(self.lines) else ""

    def handle_key(self, key):
        if self.choosing:
            if key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                self.choice_sel = (self.choice_sel + 1) % len(self.choices)
                sfx.play("blip")
            elif key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                sfx.play("confirm")
                sel = self.choice_sel
                self.finished = True
                if self.on_choice:
                    self.on_choice(sel)
                return sel
            return None
        if key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE, pygame.K_z):
            if self.chars < len(self.current):
                self.chars = len(self.current)
            else:
                sfx.play("blip")
                self.idx += 1
                self.chars = 0
                if self.idx >= len(self.lines):
                    if self.choices:
                        self.choosing = True
                    else:
                        self.finished = True
                        self.done = True
        return None

    def update(self, dt):
        if not self.choosing and self.idx < len(self.lines):
            self.chars = min(len(self.current), self.chars + dt * 45)

    def render(self, surf, rect):
        panel(surf, rect)
        r = pygame.Rect(rect)
        text = self.current[: int(self.chars)]
        f = font(24)
        words = text.split(" ")
        lines = []
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if f.size(trial)[0] > r.w - 40:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        lines.append(cur)
        for i, ln in enumerate(lines[:3]):
            draw_text(surf, ln, (r.x + 20, r.y + 16 + i * 26), 24)
        if self.choosing:
            for i, ch in enumerate(self.choices):
                x = r.x + 40 + i * 140
                y = r.y + r.h - 40
                color = (255, 220, 100) if i == self.choice_sel else TEXT
                if i == self.choice_sel:
                    draw_text(surf, ">", (x - 16, y), 24, (255, 220, 100))
                draw_text(surf, ch, (x, y), 24, color)
        elif self.idx < len(self.lines) and self.chars >= len(self.current):
            draw_text(surf, "▼", (r.x + r.w - 32, r.y + r.h - 30), 20, (255, 220, 100))
