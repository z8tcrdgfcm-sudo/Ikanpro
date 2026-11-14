import random

from . import data

WEAK_MULT = 1.5
RESIST_MULT = 0.6
CRIT_CHANCE = 0.08
CRIT_MULT = 1.6


def xp_for_level(level):
    return int(20 * (level ** 1.5)) + 10


def effectiveness(element, enemy_data):
    if element in enemy_data.get("weak", []):
        return WEAK_MULT
    if element in enemy_data.get("resist", []):
        return RESIST_MULT
    return 1.0


def compute_damage(atk, power, element, target_def, enemy_data, rng):
    base = atk * power - target_def * 0.6
    variance = rng.uniform(0.85, 1.15)
    crit = rng.random() < CRIT_CHANCE
    mult = effectiveness(element, enemy_data)
    dmg = max(1, int(round(base * variance * mult * (CRIT_MULT if crit else 1.0))))
    return dmg, crit, mult


class Player:
    def __init__(self, new_game_plus=False):
        self.level = 1
        self.xp = 0
        self.max_hp = 60
        self.hp = 60
        self.max_mp = 20
        self.mp = 20
        self.atk = 12
        self.defense = 6
        self.spd = 8
        self.gold = 50
        self.weapon = 0
        self.armor = 0
        self.inventory = {"potion": 3, "ether": 1}
        self.skills = ["strike", "fire", "ice", "heal"]
        self.x, self.y = data.PLAYER_START
        self.flags = {}
        self.new_game_plus = new_game_plus
        if new_game_plus:
            self.level = 8
            self.max_hp = 60 + 9 * 7
            self.hp = self.max_hp
            self.max_mp = 20 + 3 * 7
            self.mp = self.max_mp
            self.atk = 12 + 3 * 7
            self.defense = 6 + 2 * 7
            self.spd = 8 + 7
            self.xp = 0
            self.skills = [s for s in data.SKILL_ORDER
                           if data.SKILLS[s]["min_level"] <= self.level]

    def eff_atk(self):
        return self.atk + data.WEAPONS[self.weapon][1]

    def eff_def(self):
        return self.defense + data.ARMORS[self.armor][1]

    def xp_next(self):
        return xp_for_level(self.level)

    def known_skills(self):
        return [s for s in data.SKILL_ORDER if s in self.skills]

    def can_cast(self, sid):
        return sid in self.skills and data.SKILLS[sid]["mp"] <= self.mp

    def heal_amount(self, sid):
        sk = data.SKILLS[sid]
        return sk.get("heal", 0) + sk.get("heal_per_lvl", 0) * self.level

    def gain_xp(self, amount):
        self.xp += amount
        levels = []
        while self.xp >= self.xp_next():
            self.xp -= self.xp_next()
            self.level += 1
            levels.append(self.level)
            self.max_hp += 9
            self.max_mp += 3
            self.atk += 3
            self.defense += 2
            self.spd += 1
            self.hp = min(self.max_hp, self.hp + 15)
            self.mp = min(self.max_mp, self.mp + 5)
            for sid, sk in data.SKILLS.items():
                if sk["min_level"] == self.level and sid not in self.skills:
                    self.skills.append(sid)
        return levels

    def full_restore(self):
        self.hp = self.max_hp
        self.mp = self.max_mp

    def to_dict(self):
        return {
            "level": self.level, "xp": self.xp, "max_hp": self.max_hp, "hp": self.hp,
            "max_mp": self.max_mp, "mp": self.mp, "atk": self.atk, "defense": self.defense,
            "spd": self.spd, "gold": self.gold, "weapon": self.weapon, "armor": self.armor,
            "inventory": dict(self.inventory), "skills": list(self.skills),
            "x": self.x, "y": self.y, "flags": dict(self.flags),
            "new_game_plus": self.new_game_plus,
        }

    @classmethod
    def from_dict(cls, d):
        p = cls(new_game_plus=d.get("new_game_plus", False))
        for k in ("level", "xp", "max_hp", "hp", "max_mp", "mp", "atk", "defense",
                  "spd", "gold", "weapon", "armor", "x", "y"):
            setattr(p, k, d[k])
        p.inventory = dict(d["inventory"])
        p.skills = list(d["skills"])
        p.flags = dict(d.get("flags", {}))
        return p


class Enemy:
    def __init__(self, enemy_id, new_game_plus=False):
        e = data.ENEMIES[enemy_id]
        self.id = enemy_id
        self.data = e
        mult = 1.6 if new_game_plus else 1.0
        self.name = e["name"]
        self.max_hp = int(e["hp"] * mult)
        self.hp = self.max_hp
        self.atk = int(e["atk"] * mult)
        self.defense = int(e["def"] * mult)
        self.spd = e["spd"]
        self.xp = e["xp"]
        self.gold = e["gold"]
        self.sprite = e["sprite"]
        self.scale = e["scale"]

    def choose_move(self, rng):
        if self.id == data.BOSS_ID and self.hp < self.max_hp * 0.35 and rng.random() < 0.35:
            for m in self.data["moves"]:
                if m.get("heal") and m["power"] == 0:
                    return m
        moves = self.data["moves"]
        weights = [m.get("w", 1) for m in moves]
        return rng.choices(moves, weights=weights, k=1)[0]


class Battle:
    def __init__(self, player, enemy_id, rng, boss=False):
        self.player = player
        self.enemy = Enemy(enemy_id, new_game_plus=player.new_game_plus)
        self.rng = rng
        self.boss = boss
        self.over = False
        self.result = None
        self.defending = False
        self.round = 0

    def _player_damage_enemy(self, power, element, label):
        dmg, crit, mult = compute_damage(self.player.eff_atk(), power, element,
                                         self.enemy.defense, self.enemy.data, self.rng)
        self.enemy.hp = max(0, self.enemy.hp - dmg)
        return {"type": "hit", "target": "enemy", "dmg": dmg, "crit": crit,
                "mult": mult, "element": element, "label": label}

    def _enemy_damage_player(self, move):
        power = move["power"]
        if self.defending:
            power *= 0.5
        dmg, crit, mult = compute_damage(self.enemy.atk, power, move["element"],
                                         self.player.eff_def(), {"weak": [], "resist": []},
                                         self.rng)
        self.player.hp = max(0, self.player.hp - dmg)
        ev = {"type": "hit", "target": "player", "dmg": dmg, "crit": crit,
              "mult": mult, "element": move["element"], "label": move["name"]}
        if self.player.hp <= 0 and self.player.inventory.get("phoenix", 0) > 0:
            self.player.inventory["phoenix"] -= 1
            self.player.hp = self.player.max_hp // 2
            ev["phoenix"] = True
        return ev

    def player_action(self, cmd, arg=None):
        if self.over:
            return []
        events = []
        self.round += 1
        self.defending = False

        if cmd == "defend":
            self.defending = True
            events.append({"type": "msg", "text": f"{data.HERO_NAME} braces for impact!"})
        elif cmd == "flee":
            if self.boss:
                events.append({"type": "msg", "text": "There is no escape from this battle!"})
            else:
                chance = 0.55 + 0.05 * (self.player.spd - self.enemy.spd)
                if self.rng.random() < min(0.95, chance):
                    self.over = True
                    self.result = "fled"
                    events.append({"type": "fled"})
                    return events
                events.append({"type": "msg", "text": "Couldn't escape!"})
        elif cmd == "attack":
            events.append({"type": "msg", "text": f"{data.HERO_NAME} attacks!"})
            events.append(self._player_damage_enemy(1.0, "phys", "Attack"))
        elif cmd == "skill":
            sk = data.SKILLS[arg]
            if arg not in self.player.skills or sk["mp"] > self.player.mp:
                events.append({"type": "msg", "text": "Can't use that now."})
            else:
                self.player.mp -= sk["mp"]
                events.append({"type": "msg", "text": f"{data.HERO_NAME} casts {sk['name']}!"})
                if sk.get("heal"):
                    amt = min(self.player.max_hp - self.player.hp,
                              self.player.heal_amount(arg))
                    self.player.hp += amt
                    events.append({"type": "heal", "target": "player", "amount": amt})
                else:
                    ev = self._player_damage_enemy(sk["power"], sk["element"], sk["name"])
                    if sk.get("drain") and ev["dmg"] > 0:
                        healed = ev["dmg"] // 2
                        self.player.hp = min(self.player.max_hp, self.player.hp + healed)
                        ev["drained"] = healed
                    events.append(ev)
        elif cmd == "item":
            item = data.ITEMS[arg]
            if self.player.inventory.get(arg, 0) <= 0:
                events.append({"type": "msg", "text": f"No {item['name']} left!"})
            elif not item.get("battle", True):
                events.append({"type": "msg", "text": "Can't use that in battle."})
            else:
                self.player.inventory[arg] -= 1
                events.append({"type": "msg", "text": f"{data.HERO_NAME} uses {item['name']}!"})
                if item.get("full"):
                    self.player.hp = self.player.max_hp
                    self.player.mp = self.player.max_mp
                    events.append({"type": "heal", "target": "player", "amount": self.player.max_hp})
                    events.append({"type": "mp", "target": "player", "amount": self.player.max_mp})
                elif item.get("heal"):
                    amt = min(self.player.max_hp - self.player.hp, item["heal"])
                    self.player.hp += amt
                    events.append({"type": "heal", "target": "player", "amount": amt})
                elif item.get("mp"):
                    amt = min(self.player.max_mp - self.player.mp, item["mp"])
                    self.player.mp += amt
                    events.append({"type": "mp", "target": "player", "amount": amt})

        if self.enemy.hp <= 0 and not self.over:
            self.over = True
            self.result = "win"
            levels = self.player.gain_xp(self.enemy.xp)
            self.player.gold += self.enemy.gold
            events.append({"type": "faint", "target": "enemy"})
            events.append({"type": "win", "xp": self.enemy.xp, "gold": self.enemy.gold,
                           "levels": levels})
            return events

        if not self.over:
            move = self.enemy.choose_move(self.rng)
            events.append({"type": "msg", "text": f"{self.enemy.name} uses {move['name']}!"})
            if move.get("heal") and move["power"] == 0:
                amt = min(self.enemy.max_hp - self.enemy.hp, move["heal"])
                self.enemy.hp += amt
                events.append({"type": "heal", "target": "enemy", "amount": amt})
            else:
                ev = self._enemy_damage_player(move)
                if move.get("heal") and ev["dmg"] > 0:
                    self.enemy.hp = min(self.enemy.max_hp, self.enemy.hp + ev["dmg"] // 2)
                    ev["drained"] = ev["dmg"] // 2
                events.append(ev)

        if self.player.hp <= 0 and not self.over:
            self.over = True
            self.result = "lose"
            events.append({"type": "faint", "target": "player"})
            events.append({"type": "lose"})

        return events


def pick_encounter(zone, rng):
    table = data.ENCOUNTER_TABLES[zone]
    ids = [e for e, _ in table]
    weights = [w for _, w in table]
    return rng.choices(ids, weights=weights, k=1)[0]


def auto_battle(player, enemy_id, rng, max_rounds=200):
    b = Battle(player, enemy_id, rng)
    rounds = 0
    while not b.over and rounds < max_rounds:
        if b.player.mp >= data.SKILLS["fire"]["mp"] and b.rng.random() < 0.5:
            b.player_action("skill", "fire")
        else:
            b.player_action("attack")
        rounds += 1
    return b
