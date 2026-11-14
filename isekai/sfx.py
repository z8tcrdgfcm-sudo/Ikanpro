import array
import math

import pygame

enabled = True
_mixer_ok = False
_cache = {}


def init():
    global _mixer_ok
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 1, 512)
        _mixer_ok = True
    except Exception:
        _mixer_ok = False


def toggle():
    global enabled
    enabled = not enabled
    return enabled


def _tone(dur, fn, vol=0.22):
    n = int(44100 * dur)
    buf = array.array("h")
    for i in range(n):
        t = i / 44100.0
        env = 1.0 - (t / dur) * 0.6
        v = fn(t) * vol * env
        buf.append(int(max(-1.0, min(1.0, v)) * 32767))
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _note(freq, dur, vol=0.22, wave="sin"):
    def fn(t, f=freq, d=dur, v=vol, w=wave):
        if w == "square":
            return v * (1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0)
        return v * math.sin(2 * math.pi * f * t)
    return fn


def _seq(notes, gap=0.09, vol=0.22, wave="sin"):
    total = gap * len(notes)

    def fn(t):
        for i, (f, d) in enumerate(notes):
            start = i * gap
            if start <= t < start + d:
                tt = t - start
                env = 1.0 - (tt / d) * 0.5
                if wave == "square":
                    v = 1.0 if math.sin(2 * math.pi * f * tt) >= 0 else -1.0
                else:
                    v = math.sin(2 * math.pi * f * tt)
                return v * vol * env
        return 0.0
    return fn, total


def _build(name):
    if name == "blip":
        return _tone(0.07, _note(760, 0.07, wave="square"))
    if name == "confirm":
        return _tone(0.18, _seq([(660, 0.07), (990, 0.1)], 0.07, wave="square")[0])
    if name == "cancel":
        return _tone(0.14, _seq([(520, 0.06), (330, 0.08)], 0.06, wave="square")[0])
    if name == "slash":
        def fn(t):
            return math.sin(2 * math.pi * (300 + 2600 * t) * t) * (1 - t / 0.18)
        return _tone(0.18, fn, vol=0.3)
    if name == "fire":
        def fn(t):
            f = 180 + 900 * (t / 0.35)
            return math.sin(2 * math.pi * f * t) * 0.7 + math.sin(2 * math.pi * f * 2.01 * t) * 0.3
        return _tone(0.35, fn, vol=0.25)
    if name == "ice":
        def fn(t):
            return math.sin(2 * math.pi * (1400 - 700 * t) * t) * (0.6 + 0.4 * math.sin(2 * math.pi * 30 * t))
        return _tone(0.3, fn, vol=0.2)
    if name == "holy":
        return _tone(0.5, _seq([(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.24)], 0.1, vol=0.2)[0])
    if name == "dark":
        def fn(t):
            return math.sin(2 * math.pi * (220 - 140 * t) * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 13 * t))
        return _tone(0.35, fn, vol=0.28)
    if name == "heal":
        return _tone(0.4, _seq([(523, 0.1), (659, 0.1), (784, 0.2)], 0.09, vol=0.2)[0])
    if name == "hurt":
        return _tone(0.22, _seq([(180, 0.1), (110, 0.12)], 0.1, vol=0.3, wave="square")[0])
    if name == "levelup":
        return _tone(0.6, _seq([(523, 0.09), (659, 0.09), (784, 0.09), (1047, 0.09), (1319, 0.2)], 0.09, vol=0.22)[0])
    if name == "win":
        return _tone(0.9, _seq([(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.3), (784, 0.1), (1047, 0.35)], 0.12, vol=0.22)[0])
    if name == "lose":
        return _tone(1.0, _seq([(392, 0.2), (330, 0.2), (262, 0.2), (196, 0.4)], 0.2, vol=0.24, wave="square")[0])
    if name == "coin":
        return _tone(0.25, _seq([(988, 0.07), (1319, 0.18)], 0.07, wave="square")[0])
    if name == "door":
        return _tone(0.25, _seq([(300, 0.1), (220, 0.15)], 0.1, vol=0.2, wave="square")[0])
    if name == "encounter":
        return _tone(0.4, _seq([(220, 0.1), (220, 0.1), (440, 0.2)], 0.1, vol=0.3, wave="square")[0])
    if name == "step":
        return _tone(0.03, _note(200, 0.03, vol=0.05))
    return _tone(0.1, _note(440, 0.1))


def play(name):
    if not enabled or not _mixer_ok:
        return
    try:
        if name not in _cache:
            _cache[name] = _build(name)
        _cache[name].play()
    except Exception:
        pass
