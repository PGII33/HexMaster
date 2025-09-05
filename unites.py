from collections import deque
import animations
import competences as co

# Callback global pour gérer les kills (sera défini par le jeu si besoin)
_kill_callback = None

def set_kill_callback(callback):
    """Définit le callback à appeler quand une unité est tuée."""
    global _kill_callback
    _kill_callback = callback

def clear_kill_callback():
    """Supprime le callback de kill."""
    global _kill_callback
    _kill_callback = None

class Unite:
    def __init__(self, equipe, pos, pv, dmg, mv, tier, nom, faction, prix=None, comp=None, portee=1, pv_max=None, attaque_max=1):
        self.equipe = equipe
        self.pos = pos
        self.pv = pv
        self.pv_max = pv_max if pv_max is not None else pv
        self.dmg = dmg
        self.mv = mv
        self.pm = self.mv
        self.tier = tier
        self.nom = nom
        self.faction = faction
        self.portee = portee
        self.attaque_max = attaque_max
        self.attaque_restantes = attaque_max
        # prix selon le nouveau système : Tier 1=20, Tier 2=80, Tier 3=200, Tier 4=non achetable
        if prix is not None:
            self.prix = prix
        else:
            if tier == 1:
                self.prix = 20
            elif tier == 2:
                self.prix = 80
            elif tier == 3:
                self.prix = 200
            elif tier == 4:
                self.prix = -1  # Non achetable (bloqué)
            else:
                self.prix = tier * 5  # Fallback pour autres tiers
        # comp doit être le nom de la compétence (string) ou None/""
        self.comp = comp or ""
        self.vivant = True
        self.anim = None

    # ---------- Getters ----------
    def get_nom(self): return self.nom
    def get_pv(self): return self.pv
    def get_dmg(self): return self.dmg
    def get_mv(self): return self.mv
    def get_tier(self): return self.tier
    def get_prix(self): return "Bloqué" if self.prix < 0 else self.prix
    def get_name(self): return self.nom
    def get_faction(self): return self.faction
    def get_competence(self): return self.comp
    def get_portee(self): return self.portee
    def get_pv_max(self): return self.pv_max

    # ---------- Logique ----------
    def reset_actions(self):
        self.attaque_restantes = self.attaque_max
        self.pm = self.mv

    # ---------- Déplacements ----------
    def est_adjacente(self, autre):
        q1, r1 = self.pos
        q2, r2 = autre.pos
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,-1), (-1,1)]
        return any((q1+dx, r1+dy) == (q2, r2) for dx, dy in directions)

    def cases_accessibles(self, toutes_unites, q_range=None, r_range=None):
        if self.pm <= 0:
            return {}

        # Limites par défaut si non spécifiées
        if q_range is None:
            q_range = range(-1, 7)
        if r_range is None:
            r_range = range(-1, 7)

        if self.comp == "fantomatique":
            return co.cases_fantomatiques(self, toutes_unites, q_range, r_range)

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
                new_q, new_r = new_pos
                
                # VÉRIFIER QUE LA NOUVELLE POSITION EST DANS LA GRILLE
                if new_q not in q_range or new_r not in r_range:
                    continue
                    
                new_cout = cout + 1
                if new_pos in occupees:
                    continue
                if new_pos == self.pos:
                    continue
                if new_pos not in accessibles or new_cout < accessibles[new_pos]:
                    accessibles[new_pos] = new_cout
                    file.append((new_pos, new_cout))
        return accessibles

    def est_a_portee(self, autre):
        """Vrai si l'unité 'autre' est à portée d'attaque."""
        q1, r1 = self.pos
        q2, r2 = autre.pos
        distance = max(abs(q1 - q2), abs(r1 - r2), abs((q1 + r1) - (q2 + r2)))
        return distance <= self.portee

    # ---------- Combat ----------
    def subir_degats(self, degats):
        """Subit des dégâts en tenant compte du bouclier."""
        if not hasattr(self, 'bouclier'):
            self.bouclier = 0
        
        # Le bouclier absorbe d'abord les dégâts
        if self.bouclier > 0:
            if degats <= self.bouclier:
                # Le bouclier absorbe tous les dégâts
                self.bouclier -= degats
                return
            else:
                # Le bouclier absorbe une partie, le reste va aux PV
                degats -= self.bouclier
                self.bouclier = 0
        
        # Les dégâts restants vont aux PV
        self.pv -= degats
    
    def attaquer(self, autre):
        """Applique l'animation et les dégâts séparément."""
        if self.attaque_restantes > 0 and self.est_a_portee(autre) and autre.vivant:
            # Compétences avant l'attaque
            if self.comp == "sangsue":
                co.sangsue(self)

            # Animation
            self.anim = animations.Animation("attack", 250, self, cible=autre)
            
            # Gestion spéciale pour explosion sacrée
            if self.comp == "explosion sacrée":
                # Le Fanatique inflige ses PV en dégâts et se sacrifie
                co.explosion_sacrée(self, [], autre)  # Passer la cible
                # Ne pas faire l'attaque normale, l'explosion sacrée remplace tout
            else:
                # Attaque normale
                autre.subir_degats(self.dmg)
                cible_tuée = False
                if autre.pv <= 0:
                    autre.mourir([])  # Utiliser la nouvelle méthode mourir
                    cible_tuée = True
                
                # Compétences après l'attaque normale
                if self.comp == "zombification":
                    co.zombification(self, autre)
                elif self.comp == "lumière vengeresse" and cible_tuée:
                    co.lumière_vengeresse(self, autre)
            
            self.attaque_restantes -= 1

    def mourir(self, toutes_unites):
        """Gère la mort de l'unité et les compétences déclenchées.
        Retourne True si l'unité était vivante et est maintenant morte."""
        if self.vivant:
            self.vivant = False
            
            # Appeler le callback de kill si défini (pour le mode hexarene)
            global _kill_callback
            if _kill_callback:
                _kill_callback(self)
            
            # Compétences déclenchées à la mort (sauf explosion sacrée qui est gérée dans attaquer)
            if self.comp == "tas d'os":
                co.tas_d_os(self)
            
            return True  # Unité effectivement tuée
        return False  # Unité déjà morte

    def debut_tour(self, toutes_unites, plateau, q_range=None, r_range=None):
        """À appeler au début du tour de l'unité pour déclencher les compétences passives."""
        if self.comp == "nécromancie":
            co.nécromancie(self, toutes_unites, plateau, q_range, r_range)
        elif self.comp == "invocation":
            co.invocation(self, toutes_unites, plateau, q_range, r_range)
        elif self.comp == "bouclier de la foi":
            co.bouclier_de_la_foi(self, toutes_unites)
        elif self.comp == "aura sacrée":
            co.aura_sacrée(self, toutes_unites)
        # Ajoute ici d'autres compétences passives si besoin
    
    def a_competence_active(self):
        """Retourne True si l'unité a une compétence active utilisable."""
        if not self.comp:
            return False
        return co.est_competence_active(self.comp)
    
    def utiliser_competence(self, cible=None, toutes_unites=None):
        """Utilise la compétence active de l'unité."""
        if self.a_competence_active() and self.attaque_restantes > 0:
            success = co.utiliser_competence_active(self, self.comp, cible, toutes_unites)
            if success:
                self.attaque_restantes -= 1
            return success
        return False


# ---------- Sous-classes d'unités ----------

# Morts-Vivants

class Tas_D_Os(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Tas d'Os", pv=1, dmg=0, mv=0, tier=0, faction="Morts-Vivants", attaque_max=0)

class Goule(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Goule", pv=10, dmg=2, mv=1, tier=1, faction="Morts-Vivants")

class Squelette(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Squelette", pv=3, dmg=5, mv=2, tier=1, comp="tas d'os", faction="Morts-Vivants")

class Spectre(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Spectre", pv=6, dmg=4, mv=1, tier=1, comp="fantomatique", faction="Morts-Vivants")

class Zombie_BASE(Unite):
    """ Pour crée les zombies zombifiés """
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Zombie", pv=8, dmg=4, mv=1, tier=2, faction="Morts-Vivants")

class Zombie(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Zombie", pv=8, dmg=4, mv=1, tier=2, comp="zombification", faction="Morts-Vivants")

class Vampire(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Vampire", pv=12, dmg=3, mv=2, tier=2, comp="sangsue", faction="Morts-Vivants")

class Liche(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Liche", pv=7, dmg=1, mv=2, tier=3, comp="nécromancie", faction="Morts-Vivants")

class Archliche(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Archliche", pv=10, dmg=2, mv=2, tier=4, comp="invocation", faction="Morts-Vivants")


# Religieux

class Missionnaire(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Missionnaire", pv=8, dmg=3, mv=2, tier=1, faction="Religieux")

class Clerc(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Clerc", pv=6, dmg=2, mv=1, tier=1, faction="Religieux", comp="soin")

class Fanatique(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Fanatique", pv=8, dmg=0, mv=2, tier=1, faction="Religieux", comp="explosion sacrée")

class Esprit_Saint(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Esprit Saint", pv=10, dmg=3, mv=2, tier=2, faction="Religieux", comp="bouclier de la foi")

class Paladin(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Paladin", pv=15, dmg=4, mv=2, tier=2, faction="Religieux", comp="bénédiction")

class Ange(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Ange", pv=12, dmg=5, mv=2, tier=3, faction="Religieux", comp="lumière vengeresse", portee=2)

class ArchAnge(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="ArchAnge", pv=18, dmg=6, mv=3, tier=4, faction="Religieux", comp="aura sacrée", portee=2)


# Liste des classes utilisables
CLASSES_UNITES = [
    # Morts-Vivants
    Goule, Squelette, Spectre, Vampire, Zombie, Liche, Archliche,
    # Religieux
    Missionnaire, Clerc, Fanatique, Esprit_Saint, Paladin, Ange, ArchAnge
]
