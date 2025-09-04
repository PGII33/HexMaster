def sangsue(self):
    """Le vampire récupère autant de PV que de dégâts infligés."""
    self.pv = min(self.pv + self.dmg, self.pv_max)

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

def explosion_sacrée(self, toutes_unites):
    """Se sacrifie pour infliger ses points de vie en dégâts aux ennemis adjacents."""
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    degats = self.pv
    
    # Infliger des dégâts aux unités adjacentes ennemies
    for unite in toutes_unites:
        if unite.equipe != self.equipe and unite.vivant:
            unite_q, unite_r = unite.pos
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    unite.pv -= degats
                    if unite.pv <= 0:
                        unite.vivant = False
                    break
    
    # Se sacrifier
    self.vivant = False
    self.pv = 0

def bouclier_de_la_foi(self, toutes_unites):
    """2 Shield sur les unités autour de soi."""
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    
    for unite in toutes_unites:
        if unite.equipe == self.equipe and unite != self and unite.vivant:
            unite_q, unite_r = unite.pos
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Ajouter un bouclier temporaire
                    if not hasattr(unite, 'shield'):
                        unite.shield = 0
                    unite.shield += 2
                    break

def bénédiction(self, cible):
    """Augmente l'attaque et la défense de la cible."""
    if cible.equipe == self.equipe and cible.vivant:
        # Ajouter un buff permanent
        if not hasattr(cible, 'buff_bénédiction'):
            cible.buff_bénédiction = True
            cible.dmg += 2
            if not hasattr(cible, 'shield'):
                cible.shield = 0
            cible.shield += 1
        return True
    return False

def lumière_vengeresse(self, cible):
    """Regagne son attaque lorsqu'il tue un Mort-Vivant."""
    if not cible.vivant and cible.faction == "Morts-Vivants":
        # Regagner une attaque
        self.attaque_restantes = min(self.attaque_restantes + 1, self.attaque_max)

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

# Fonction utilitaire pour déterminer si une compétence est active
def est_competence_active(nom_competence):
    """Retourne True si la compétence nécessite une cible."""
    competences_actives = ["soin", "bénédiction"]  # Retiré "explosion sacrée" et "lumière vengeresse"
    return nom_competence in competences_actives

def peut_cibler_allie(nom_competence):
    """Retourne True si la compétence peut cibler des alliés."""
    competences_alliés = ["soin", "bénédiction"]
    return nom_competence in competences_alliés

def peut_cibler_ennemi(nom_competence):
    """Retourne True si la compétence peut cibler des ennemis."""
    competences_ennemis = []  # Retiré "explosion sacrée"
    return nom_competence in competences_ennemis

def utiliser_competence_active(unite, nom_competence, cible, toutes_unites=None):
    """Utilise une compétence active sur une cible."""
    if nom_competence == "soin":
        return soin(unite, cible)
    elif nom_competence == "bénédiction":
        return bénédiction(unite, cible)
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
    "explosion sacrée": "Se sacrifie pour infliger ses points de vie en dégâts aux ennemis adjacents (à la mort).",
    "bouclier de la foi": "2 Shield sur les unités alliées autour de soi (chaque tour).",
    "bénédiction": "Augmente l'attaque et donne 1 shield à un allié.",
    "lumière vengeresse": "Regagne son attaque lorsqu'il tue un Mort-Vivant (passif).",
    "aura sacrée": "Bonus de dégâts pour tout les alliés adjacents (chaque tour).",
}
