# Isekai Odyssey — Reborn in Aetheria

A classic anime-style Isekai JRPG in Python + Pygame: you get summoned to the world of
Aetheria, and the Demon Lord Vexaris is waking up in the dungeon to the north.
Explore the overworld, fight random encounters in the tall grass, level up, gear up
at the shop, and defeat the Demon Lord.

No art assets — every sprite, tile, and sound effect is generated procedurally in code.

## Run

```bash
pip install -r requirements.txt
python3 main.py
```

## Controls

| Key | Action |
| --- | --- |
| WASD / Arrow keys | Move |
| E / Enter / Space | Talk / interact / advance dialog / confirm |
| ESC | Menu (Status / Save / Quit to Title) |
| M | Toggle sound |

## How to play

- Walk into **tall grass** (or the **dungeon floor**) for random encounters.
- Battles are turn-based: Attack / Skills / Item / Defend / Flee.
- Elemental weaknesses matter: slimes fear **fire**, wolves fear **ice**,
  skeletons resist physical and fear **holy** light, the Demon Lord fears holy only.
- Step on the **golden door** (or talk to the shopkeeper) to buy potions, ethers,
  and better weapons/armor. The **blue door** is the inn (full heal for 20 G).
- Reach the **red magic circle** at the top of the dungeon for the boss fight.
- Progress auto-saves after battles and in the ESC menu. "Continue" resumes from the title screen.
- Beat the Demon Lord to unlock **New Journey+** (harder monsters, you keep your level).

## Project layout

```
main.py               entry point
isekai/
  data.py             map, enemies, skills, items, dialogs (pure data)
  core.py             battle engine, damage/XP/leveling, save model (pure logic)
  pix.py              procedural pixel-art sprites and tiles
  sfx.py              procedural sound effects (WebAudio-style synth via pygame.mixer)
  ui.py               dialog box, menus, HP/MP/XP bars
  overworld.py        tile map, movement, encounters, NPCs
  battle.py           turn-based battle scene
  game.py             state machine (title/overworld/battle/shop/menu/ending) + save/load
tests/
  test_core.py        unit tests for the game logic
  test_smoke.py       headless end-to-end playthrough (SDL dummy drivers)
tools/preview.py      renders sprite/tile preview sheets to preview/
```

## Tests

```bash
python3 -m unittest discover -s tests -v   # logic unit tests
python3 tests/test_smoke.py                 # headless full-game smoke test
python3 tools/preview.py                    # regenerate preview images
```

## Roadmap (making it better over time)

- Quests and story flags (NPC quest chains, town expansion)
- More areas: desert, volcano, sky islands, second dungeon
- Party members who join and fight alongside you
- Equipment with sprites shown in battle, status ailments (poison/burn)
- Boss phases and a proper battle soundtrack
- Replace procedural art with real pixel-art sheets (drop PNGs into `pix.py`)
- Gamepad support, difficulty options, achievements
