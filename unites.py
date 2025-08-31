from collections import deque

class Unite:
    def __init__(self, equipe, pos, nom, pv, dmg, mv, tier):
        self.nom = nom
        self.equipe = equipe
        self.pos = pos
        self.pv = pv
        self.dmg = dmg
        self.mv = mv
        self.pm = self.mv
        self.tier = tier
        self.vivant = True
        self.a_attaque = False

    def reset_actions(self):
        self.a_attaque = False
        self.pm = self.mv

    def est_adjacente(self, autre):
        q1, r1 = self.pos
        q2, r2 = autre.pos
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,-1), (-1,1)]
        return any((q1+dx, r1+dy) == (q2, r2) for dx, dy in directions)

    def cases_accessibles(self, toutes_unites):
        # retourne dict {(q,r): coût} en PM pour atteindre la case (coût = distance en pas)
        if self.pm <= 0:
            return {}

        accessibles = {}
        file = deque([(self.pos, 0)])

        directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
        occupees = {u.pos for u in toutes_unites if u.vivant and u != self}

        while file:
            (q, r), cout = file.popleft()
            if cout >= self.pm:
                continue
            for dq, dr in directions:
                new_pos = (q+dq, r+dr)
                new_cout = cout + 1
                if new_pos in occupees:
                    continue
                if new_pos == self.pos:
                    continue
                if new_pos not in accessibles or new_cout < accessibles[new_pos]:
                    accessibles[new_pos] = new_cout
                    file.append((new_pos, new_cout))
        return accessibles

    def attaquer(self, autre):
        if not self.a_attaque and self.est_adjacente(autre) and autre.vivant:
            autre.pv -= self.dmg
            self.a_attaque = True
            if autre.pv <= 0:
                autre.vivant = False

class Squelette(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, "Squelette", pv=3, dmg=5, mv=2, tier=1)

class Goule(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, "Goule", pv=10, dmg=2, mv=1, tier=1)

class Vampire(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, "Vampire", pv=12, dmg=3, mv=2, tier=2)