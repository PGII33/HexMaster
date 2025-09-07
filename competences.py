def sangsue(self, degats_infliges):
    """Le vampire récupère autant de PV que de dégâts réellement infligés."""
    self.pv = min(self.pv + degats_infliges, self.pv_max)

def zombification(self, cible):
    """Transforme l'unite morte en zombie sous le contrôle du joueur de l'attaquant"""
    from unites import Zombie_BASE
    if not cible.vivant and cible.nom != "Zombie":        
        # Transformer la cible en Zombie_BASE
        cible.__class__ = Zombie_BASE
        cible.__init__(self.equipe, cible.pos)
        cible.pm = 0
        cible.attaque_restantes = 0
        cible.comp = "zombification"
        cible.attaque_restantes = 0

def tas_d_os(self):
    from unites import Tas_D_Os
    if not self.vivant:
        self.__class__ = Tas_D_Os
        self.__init__(self.equipe, self.pos)
        self.vivant = False  # Important: garder l'état mort après transformation

def cases_fantomatiques(unite, toutes_unites, q_range=None, r_range=None):
    """Retourne toutes les cases accessibles en traversant les unités (traverser une unité ne coûte pas de PM, s'arrêter sur une case vide coûte 1 PM par case vide)."""
    from collections import deque
    
    # Limites par défaut si non spécifiées
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)
        
    accessibles = {}
    file = deque([(unite.pos, 0)])
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    vus = dict()  # (q, r): cout minimal
    occupees = {u.pos for u in toutes_unites if u.vivant and u != unite}
    while file:
        (q, r), cout = file.popleft()
        if cout > unite.pm:
            continue
        if (q, r) in vus and cout >= vus[(q, r)]:
            continue
        vus[(q, r)] = cout
        if (q, r) != unite.pos and (q, r) not in occupees:
            accessibles[(q, r)] = cout
        for dq, dr in directions:
            new_pos = (q+dq, r+dr)
            new_q, new_r = new_pos
            
            # VÉRIFIER QUE LA NOUVELLE POSITION EST DANS LA GRILLE
            if new_q not in q_range or new_r not in r_range:
                continue
                
            if new_pos in occupees:
                file.appendleft((new_pos, cout))  # traverser une unité = 0 PM
            else:
                file.append((new_pos, cout+1))   # case vide = +1 PM
    return accessibles

def nécromancie(self, toutes_unites, plateau, q_range=None, r_range=None):
    """Invoque un Squelette sur une case adjacente vide à chaque tour."""
    from unites import Squelette
    
    # Limites par défaut si non spécifiées
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)
    
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    for dq, dr in directions:
        new_pos = (q+dq, r+dr)
        new_q, new_r = new_pos
        
        # VÉRIFIER QUE LA POSITION EST DANS LA GRILLE
        if new_q not in q_range or new_r not in r_range:
            continue
            
        if plateau.est_case_vide(new_pos, toutes_unites):
            toutes_unites.append(Squelette(self.equipe, new_pos))
            break

def invocation(self, toutes_unites, plateau, q_range=None, r_range=None):
    """Invoque une unité Morts-Vivants de tier 1 ou 2 sur une case adjacente vide à chaque tour."""
    from unites import Goule, Squelette, Spectre, Zombie, Vampire
    import random
    
    # Limites par défaut si non spécifiées
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)
    
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    candidates = [Goule, Squelette, Spectre, Zombie, Vampire]
    random.shuffle(candidates)
    for i in range (2):
        for dq, dr in directions:
            new_pos = (q+dq, r+dr)
            new_q, new_r = new_pos
            
            # VÉRIFIER QUE LA POSITION EST DANS LA GRILLE
            if new_q not in q_range or new_r not in r_range:
                continue
                
            if plateau.est_case_vide(new_pos, toutes_unites):
                UniteClass = random.choice(candidates)
                toutes_unites.append(UniteClass(self.equipe, new_pos))
                break

# ========== COMPÉTENCES RELIGIEUX ==========

def soin(self, cible):
    """Soigne la cible de 5 points de vie."""
    if cible.equipe == self.equipe and cible.vivant:
        cible.pv = min(cible.pv + 5, cible.pv_max)
        return True
    return False

def explosion_sacrée(self, toutes_unites, cible_attaquee=None):
    """Se sacrifie en attaquant pour infliger ses points de vie en dégâts à la cible uniquement."""
    degats = self.pv  # Utilise ses PV actuels comme dégâts
    
    # Infliger des dégâts uniquement à la cible directe si c'est un ennemi
    if cible_attaquee and cible_attaquee.equipe != self.equipe and cible_attaquee.vivant:
        cible_attaquee.subir_degats(degats)
        if cible_attaquee.pv <= 0:
            cible_attaquee.mourir(toutes_unites)
    
    # Marquer pour mourir après l'animation (ne pas mourir immédiatement)
    self.explosion_sacree_pending = True

def bouclier_de_la_foi(self, toutes_unites):
    """2 Bouclier sur les unités autour de soi."""
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    
    for unite in toutes_unites:
        if unite.equipe == self.equipe and unite != self and unite.vivant:
            unite_q, unite_r = unite.pos
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Ajouter un bouclier temporaire
                    if not hasattr(unite, 'bouclier'):
                        unite.bouclier = 0
                    unite.bouclier += 1
                    break

def bénédiction(self, cible):
    """Augmente l'attaque et la défense de la cible."""
    if cible.equipe == self.equipe and cible.vivant:
        # Ajouter un buff permanent
        if not hasattr(cible, 'buff_bénédiction'):
            cible.buff_bénédiction = True
            cible.dmg += 2
            if not hasattr(cible, 'bouclier'):
                cible.bouclier = 0
            cible.bouclier += 1
        return True
    return False

def cristalisation(self, cible_pos, toutes_unites):
    """Crée un Cristal sur une case adjacente à 1 de portée."""
    from unites import Cristal
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    
    # Vérifier si la cible est adjacente
    for dq, dr in directions:
        if (q+dq, r+dr) == cible_pos:
            # Vérifier que la case est vide
            case_libre = True
            for unite in toutes_unites:
                if unite.pos == cible_pos and unite.vivant:
                    case_libre = False
                    break
            
            if case_libre:
                cristal = Cristal(self.equipe, cible_pos)
                toutes_unites.append(cristal)
                return True
    
    return False

def lumière_vengeresse(self, cible):
    """Regagne son attaque lorsqu'il tue un Mort-Vivant."""
    if not cible.vivant and cible.faction == "Morts-Vivants":
        # Regagner une attaque
        self.attaque_restantes += 1

def aura_sacrée(self, toutes_unites):
    """Bonus de dégâts pour tout les alliés adjacents."""
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    
    for unite in toutes_unites:
        if unite.equipe == self.equipe and unite != self and unite.vivant:
            unite_q, unite_r = unite.pos
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Bonus permanent tant que l'ArchAnge est vivant
                    if not hasattr(unite, 'aura_sacrée_bonus'):
                        unite.aura_sacrée_bonus = True
                        unite.dmg += 3
                    break

# ========== COMPÉTENCES ÉLÉMENTAIRES ==========

def enracinement(self):
    """Si l'unité n'a pas bougé en fin de tour, régénère 2 PV."""
    # L'enracinement se déclenche si l'unité n'a pas dépensé de PM (pas bougé)
    if self.pm == self.mv:  # N'a pas bougé (PM restants = MV max)
        if self.pv + 2 <= self.pv_max:
            self.pv += 2
        else:
            self.pv = self.pv_max

def vague_apaisante(self, toutes_unites):
    """Soigne les unités alliées adjacentes de 2 PV (comme bouclier de la foi mais avec soin)."""
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    
    for unite in toutes_unites:
        if unite.equipe == self.equipe and unite != self and unite.vivant:
            unite_q, unite_r = unite.pos
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Soigner l'unité adjacente
                    if unite.pv + 2 <= unite.pv_max:
                        unite.pv += 2
                    else:
                        unite.pv = unite.pv_max
                    break

def renaissance(self, toutes_unites):
    """80% de chance de revenir à la vie avec tous ses PV."""
    import random
    
    # La renaissance se déclenche quand l'unité est sur le point de mourir (PV <= 0)
    if self.vivant and self.pv <= 0 and random.random() < 0.8:  # 80% de chance
        self.pv = self.pv_max
        # Réinitialiser les actions pour le tour suivant
        self.pm = self.mv
        self.attaque_restantes = self.attaque_max
        return True  # Indique que la renaissance a eu lieu
    
    return False

def armure_de_pierre(degats_recus):
    """Réduit tous les dégâts reçus de 2 points (minimum 0)."""
    degats_reduits = max(0, degats_recus - 2)
    return degats_reduits

def combustion_differee(attaquant, cible):
    """Marque la cible pour mourir dans 3 tours."""
    if not hasattr(cible, 'combustion_tours_restants'):
        cible.combustion_tours_restants = 3
        cible.combustion_attaquant = attaquant.equipe
        print(f"🔥 {cible.nom} est marqué par la combustion différée! Mort dans 3 tours.")
    
def gerer_combustion_differee(unite, toutes_unites):
    """Vérifie et applique la combustion différée en fin de tour ennemi."""
    if hasattr(unite, 'combustion_tours_restants') and unite.combustion_tours_restants > 0:
        unite.combustion_tours_restants -= 1
        print(f"🔥 {unite.nom} - Combustion: {unite.combustion_tours_restants} tours restants")
        
        if unite.combustion_tours_restants == 0:
            print(f"💥 {unite.nom} succombe à la combustion différée!")
            unite.pv = 0
            unite.mourir(toutes_unites)
            # Nettoyer l'effet
            if hasattr(unite, 'combustion_tours_restants'):
                delattr(unite, 'combustion_tours_restants')
            if hasattr(unite, 'combustion_attaquant'):
                delattr(unite, 'combustion_attaquant')

# Fonction utilitaire pour déterminer si une compétence est active
def est_competence_active(nom_competence):
    """Retourne True si la compétence nécessite une cible."""
    competences_actives = ["soin", "bénédiction", "cristalisation"]
    return nom_competence in competences_actives

def peut_cibler_allie(nom_competence):
    """Retourne True si la compétence peut cibler des alliés."""
    competences_alliés = ["soin", "bénédiction"]
    return nom_competence in competences_alliés

def peut_cibler_ennemi(nom_competence):
    """Retourne True si la compétence peut cibler des ennemis."""
    competences_ennemis = []
    return nom_competence in competences_ennemis

def peut_cibler_case_vide(nom_competence):
    """Retourne True si la compétence peut cibler des cases vides."""
    competences_cases = ["cristalisation"]
    return nom_competence in competences_cases

def utiliser_competence_active(unite, nom_competence, cible, toutes_unites=None):
    """Utilise une compétence active sur une cible."""
    if nom_competence == "soin":
        return soin(unite, cible)
    elif nom_competence == "bénédiction":
        return bénédiction(unite, cible)
    elif nom_competence == "cristalisation":
        return cristalisation(unite, cible, toutes_unites)
    return False


# Dictionnaire des compétences (nom -> description)
COMPETENCES = {
    # Morts-Vivants
    "sangsue": "Augmente sa vie du nombre de dégâts infligés.",
    "zombification": "Transforme l'unite ennemie tuée en zombie",
    "tas d'os": "À la mort, un tas d'os d'1PV apparaît sur la cellule.",
    "fantomatique": "Se déplace au travers des unites gratuitement.",
    "nécromancie": "Crée un squelette sur une case adjacente (chaque tour).",
    "invocation": "Invoque une unité de tier 1 ou 2 des Morts-Vivants sur une case adjacente (chaque tour).",
    
    # Religieux
    "soin": "Soigne un allié de 5 points de vie.",
    "explosion sacrée": "Se sacrifie en attaquant pour infliger ses points de vie en dégâts à la cible et aux ennemis adjacents.",
    "bouclier de la foi": "2 Bouclier sur les unités alliées autour de soi (chaque tour).",
    "bénédiction": "Augmente l'attaque et donne 1 bouclier à un allié.",
    "lumière vengeresse": "Regagne son attaque lorsqu'il tue un Mort-Vivant (passif).",
    "aura sacrée": "Bonus de dégâts pour tout les alliés adjacents (chaque tour).",
    
    # Élémentaires
    "enracinement": "Si l'unité n'a pas bougé en fin de tour, régénère 2 PV.",
    "vague apaisante": "Soigne les unités alliées adjacentes de 2 PV (chaque tour).",
    "renaissance": "80% de chance de revenir à la vie avec tous ses PV à la mort.",
    "armure de pierre": "Réduit tous les dégâts reçus de 2 points (minimum 0).",
    "combustion différée": "Les cibles touchées meurent au bout de 3 tours ennemis.",
}
