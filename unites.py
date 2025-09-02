from collections import deque
import animations
import competences as co

class Unite:
    def __init__(self, equipe, pos, pv, dmg, mv, tier, nom, prix=None, comp=None):
        self.equipe = equipe
        self.pos = pos
        self.pv = pv
        self.dmg = dmg
        self.mv = mv
        self.pm = self.mv
        self.tier = tier
        self.nom = nom
        # prix par défaut = tier * 5 ; si prix < 0 => "Bloqué"
        self.prix = prix if prix is not None else (tier * 5)
        # comp doit être le nom de la compétence (string) ou None/""
        self.comp = comp or ""
        self.vivant = True
        self.a_attaque = False
        self.anim = None

    # ---------- Getters ----------
    def get_nom(self): return self.nom
    def get_pv(self): return self.pv
    def get_dmg(self): return self.dmg
    def get_mv(self): return self.mv
    def get_tier(self): return self.tier
    def get_prix(self): return "Bloqué" if self.prix < 0 else self.prix
    def get_competence(self): return self.comp

    # ---------- Logique ----------
    def reset_actions(self):
        self.a_attaque = False
        self.pm = self.mv

    # ---------- Déplacements ----------
    def est_adjacente(self, autre):
        q1, r1 = self.pos
        q2, r2 = autre.pos
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,-1), (-1,1)]
        return any((q1+dx, r1+dy) == (q2, r2) for dx, dy in directions)

    def cases_accessibles(self, toutes_unites):
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

    # ---------- Combat ----------
    def attaquer(self, autre):
        """Applique l'animation et les dégâts séparément."""
        if not self.a_attaque and self.est_adjacente(autre) and autre.vivant:
            
            # Compétences avant l'attaque
            if self.comp == "sangsue":
                co.sangsue(self)

            # Animation
            self.anim = animations.Animation("attack", 250, self, cible=autre)
            
            autre.pv -= self.dmg
            if autre.pv <= 0:
                autre.vivant = False
                
                # Compétences après la mort de la cible
                if self.comp == "zombification":
                    co.zombification(self, autre)

            self.a_attaque = True


# ---------- Sous-classes d’unités ----------
class Squelette(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Squelette", pv=3, dmg=5, mv=2, tier=1)


class Goule(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Goule", pv=10, dmg=2, mv=1, tier=1)


class Vampire(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Vampire", pv=12, dmg=3, mv=2, tier=2, comp="sangsue")

class Zombie(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, pv=8, dmg=4, mv=1, tier=2, nom="Zombie", comp="zombification")

# Liste des classes utilisables
CLASSES_UNITES = [Squelette, Goule, Vampire, Zombie]
