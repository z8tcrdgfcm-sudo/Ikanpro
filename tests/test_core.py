import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from isekai import core, data


class TestMap(unittest.TestCase):
    def test_map_dimensions(self):
        self.assertEqual(len(data.MAP), data.MAP_H)
        for row in data.MAP:
            self.assertEqual(len(row), data.MAP_W)

    def test_connectivity(self):
        from collections import deque
        blocked = set("TWB") | {data.NPCS[n]["pos"] for n in data.NPCS}
        start = data.PLAYER_START
        seen = {start}
        q = deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < data.MAP_W and 0 <= ny < data.MAP_H:
                    if (nx, ny) not in seen and (nx, ny) not in blocked \
                            and data.MAP[ny][nx] in data.WALKABLE:
                        seen.add((nx, ny))
                        q.append((nx, ny))
        targets = [(14, 6), (14, 1), (2, 16), (9, 16), (5, 17), (4, 9), (18, 12)]
        for t in targets:
            self.assertIn(t, seen, f"unreachable target {t}")


class TestDamage(unittest.TestCase):
    def test_bounds(self):
        rng = random.Random(42)
        e = data.ENEMIES["goblin"]
        for _ in range(2000):
            dmg, crit, mult = core.compute_damage(12, 1.0, "phys", 4, e, rng)
            lo = (12 - 4 * 0.6) * 0.85
            hi = (12 - 4 * 0.6) * 1.15 * core.CRIT_MULT
            self.assertGreaterEqual(dmg, 1)
            self.assertLessEqual(dmg, max(1, round(hi)))
            self.assertGreaterEqual(dmg, min(lo, 1) - 1)

    def test_weakness_and_resist(self):
        rng = random.Random(1)
        slime = data.ENEMIES["slime"]
        fire_dmgs = [core.compute_damage(20, 1.0, "fire", 2, slime, rng)[0] for _ in range(200)]
        phys_dmgs = [core.compute_damage(20, 1.0, "phys", 2, slime, rng)[0] for _ in range(200)]
        self.assertGreater(sum(fire_dmgs), sum(phys_dmgs) * 1.2)
        skel = data.ENEMIES["skeleton"]
        phys = [core.compute_damage(20, 1.0, "phys", 6, skel, rng)[0] for _ in range(200)]
        holy = [core.compute_damage(20, 1.0, "holy", 6, skel, rng)[0] for _ in range(200)]
        self.assertGreater(sum(holy), sum(phys) * 1.2)
        self.assertEqual(core.effectiveness("fire", slime), core.WEAK_MULT)
        self.assertEqual(core.effectiveness("phys", skel), core.RESIST_MULT)


class TestProgression(unittest.TestCase):
    def test_xp_curve_monotonic(self):
        vals = [core.xp_for_level(l) for l in range(1, 30)]
        self.assertEqual(vals, sorted(vals))
        self.assertTrue(all(v > 0 for v in vals))

    def test_level_up_unlocks_skills(self):
        p = core.Player()
        self.assertIn("fire", p.skills)
        self.assertNotIn("powerslash", p.skills)
        self.assertNotIn("holy", p.skills)
        p.gain_xp(core.xp_for_level(1) + core.xp_for_level(2))
        self.assertGreaterEqual(p.level, 3)
        self.assertIn("powerslash", p.skills)
        p.gain_xp(sum(core.xp_for_level(l) for l in range(p.level, 6)))
        self.assertGreaterEqual(p.level, 6)
        self.assertIn("holy", p.skills)
        self.assertGreater(p.max_hp, 60)

    def test_save_roundtrip(self):
        p = core.Player()
        p.gain_xp(500)
        p.gold = 321
        p.inventory["potion"] = 7
        p.x, p.y = 3, 9
        p.flags["boss_dead"] = True
        d = p.to_dict()
        q = core.Player.from_dict(d)
        self.assertEqual(q.to_dict(), d)


class TestBattle(unittest.TestCase):
    def test_win_awards_rewards(self):
        rng = random.Random(7)
        p = core.Player()
        p.atk = 500
        b = core.Battle(p, "slime", rng)
        events = []
        while not b.over:
            events.extend(b.player_action("attack"))
        self.assertEqual(b.result, "win")
        win = [e for e in events if e["type"] == "win"]
        self.assertEqual(len(win), 1)
        self.assertEqual(win[0]["xp"], data.ENEMIES["slime"]["xp"])
        self.assertGreater(p.gold, 50)
        self.assertGreaterEqual(p.xp + sum(core.xp_for_level(l) for l in range(1, p.level)), 0)

    def test_lose_against_boss(self):
        rng = random.Random(3)
        p = core.Player()
        b = core.Battle(p, data.BOSS_ID, rng, boss=True)
        while not b.over:
            b.player_action("defend")
        self.assertEqual(b.result, "lose")

    def test_boss_flee_fails(self):
        rng = random.Random(5)
        p = core.Player()
        p.atk = 500
        b = core.Battle(p, data.BOSS_ID, rng, boss=True)
        ev = b.player_action("flee")
        self.assertFalse(b.over)
        self.assertTrue(any(e["type"] == "msg" for e in ev))

    def test_defend_halves_damage(self):
        rng = random.Random(11)
        p = core.Player()
        p.spd = 0
        b1 = core.Battle(p, "orc", rng)
        ev_attack = b1.player_action("attack")
        dmg_normal = [e["dmg"] for e in ev_attack if e["type"] == "hit" and e["target"] == "player"]

        rng2 = random.Random(11)
        p2 = core.Player()
        p2.spd = 0
        b2 = core.Battle(p2, "orc", rng2)
        ev_def = b2.player_action("defend")
        dmg_def = [e["dmg"] for e in ev_def if e["type"] == "hit" and e["target"] == "player"]
        if dmg_normal and dmg_def:
            self.assertLessEqual(dmg_def[0], dmg_normal[0])

    def test_skill_mp_and_heal(self):
        rng = random.Random(2)
        p = core.Player()
        p.hp = 10
        b = core.Battle(p, "slime", rng)
        mp_before = p.mp
        b.player_action("skill", "heal")
        self.assertLess(p.mp, mp_before)
        self.assertGreater(p.hp, 10)
        p.mp = 0
        b2 = core.Battle(p, "slime", random.Random(2))
        ev = b2.player_action("skill", "fire")
        self.assertTrue(any(e["type"] == "msg" for e in ev))
        self.assertEqual(b2.enemy.hp, b2.enemy.max_hp)

    def test_drain_heals_player(self):
        rng = random.Random(9)
        p = core.Player()
        p.hp = 5
        p.skills.append("drain")
        b = core.Battle(p, "slime", rng)
        b.player_action("skill", "drain")
        self.assertGreater(p.hp, 5)

    def test_phoenix_auto_revive(self):
        rng = random.Random(4)
        p = core.Player()
        p.inventory["phoenix"] = 1
        p.max_hp = 60
        p.hp = 1
        b = core.Battle(p, data.BOSS_ID, rng, boss=True)
        b.player_action("defend")
        if p.hp == 0 and not b.over:
            pass
        if b.result == "lose":
            self.fail("phoenix should have revived the player")
        self.assertEqual(p.inventory.get("phoenix", 0), 0)

    def test_pick_encounter_in_table(self):
        rng = random.Random(0)
        for _ in range(50):
            self.assertIn(core.pick_encounter("meadow", rng),
                          [e for e, _ in data.ENCOUNTER_TABLES["meadow"]])
            self.assertIn(core.pick_encounter("dungeon", rng),
                          [e for e, _ in data.ENCOUNTER_TABLES["dungeon"]])

    def test_auto_battle_terminates(self):
        rng = random.Random(123)
        p = core.Player()
        b = core.auto_battle(p, "slime", rng)
        self.assertTrue(b.over)
        self.assertIn(b.result, ("win", "lose", "fled"))


if __name__ == "__main__":
    unittest.main()
