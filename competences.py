import random

DO_PRINT = False

comp_portee = {
    "bénédiction": 3,
    "commandement": 2,
    "cristalisation": 1,
    "pluie de flèches": 3,
    "monture libéré": 1,
    "soin": 3,
    "tir précis": 1,  # Portée normale +1
}

def sangsue(self, degats_infliges):
    """Le vampire récupère autant de PV que de dégâts réellement infligés (peut dépasser PV max)."""
    if DO_PRINT : print("Sangsue :", degats_infliges, "PV récupérés")
    self.pv += degats_infliges

def zombification(self, cible):
    """Transforme l'unite morte en zombie sous le contrôle du joueur de l'attaquant"""
    if DO_PRINT : print("Zombification effectuée sur :", cible.get_name())
    if not cible.vivant and cible.nom != "Zombie":        
        cible.__class__ = self.__class__
        cible.__init__(self.equipe, cible.pos)
        cible.pm = 0
        cible.attaque_restantes = 0
    

def tas_d_os(self):
    """Transforme l'unité morte en tas d'os."""
    from unites import Tas_D_Os
    # Transformation en tas d'os : c'est une nouvelle unité vivante
    self.__class__ = Tas_D_Os
    self.__init__(self.equipe, self.pos)
    # Le tas d'os est vivant avec 1 PV (défini dans Tas_D_Os.__init__)

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
    random.shuffle(directions) # Pour varier les positions d'invocation
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
    """Invoque deux unité Morts-Vivants de tier 1 ou 2 sur une case adjacente vide à chaque tour."""
    from unites import Goule, Squelette, Spectre, Zombie, Vampire
    import random
    
    # Limites par défaut si non spécifiées
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)
    
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    random.shuffle(directions) # Pour varier les positions d'invocation
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
        # Appliquer la protection si applicable
        degats_infliges = protection(cible_attaquee, degats, toutes_unites)
        
        # Vérifier si la cible ou les protecteurs meurent
        for unite in toutes_unites:
            if unite.pv <= 0 and unite.vivant:
                unite.mourir(toutes_unites)
    
    # Marquer pour mourir après l'animation (ne pas mourir immédiatement)
    self.explosion_sacree_pending = True

def bouclier_de_la_foi(self, toutes_unites):
    """Applique 1 bouclier sur les unités alliées adjacentes."""
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    
    for unite in toutes_unites:
        if unite.equipe == self.equipe and unite != self and unite.vivant:
            unite_q, unite_r = unite.pos
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Ajouter un bouclier temporaire
                    unite.bouclier += 1
                    break

def bénédiction(self, cible):
    """Augmente l'attaque de 2 et applique 1 bouclier à la cible."""
    if cible.equipe == self.equipe and cible.vivant:
        # Ajouter un buff permanent
        if not hasattr(cible, 'buff_bénédiction'):
            cible.buff_bénédiction = True
            cible.ba_benediction = 2
            cible.bouclier += 1
        return True
    return False

def lumière_vengeresse(self, cible):
    """Regagne son attaque lorsqu'il tue un Mort-Vivant."""
    if cible.get_faction() != "Morts-Vivants":
        return
    self.attaque_restantes += 1
    # Flag pour indiquer que cette unité devrait continuer à agir
    self._lumiere_vengeresse_activee = True

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
                    if not hasattr(unite, 'ba_aura_sacree'):
                        unite.ba_aura_sacree = 3
                    break

# ========== COMPÉTENCES ROYAUME ==========

def pluie_de_fleches(self, cible_pos, toutes_unites):
    """Attaque AOE sur la case cible et toutes les cases adjacentes."""
    # Vérifier que la case cible est à portée (jusqu'à 3 cases)
    q_self, r_self = self.pos
    q_cible, r_cible = cible_pos
    distance = max(abs(q_self - q_cible), abs(r_self - r_cible), abs((q_self + r_self) - (q_cible + r_cible)))
    
    if distance > 3:
        return False
    
    # Cases affectées : la case cible + ses adjacentes
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    cases_affectees = [cible_pos]  # Case cible
    
    # Ajouter les cases adjacentes à la cible
    for dq, dr in directions:
        case_adjacente = (q_cible + dq, r_cible + dr)
        cases_affectees.append(case_adjacente)
    
    # Attaquer TOUTES les unités dans les cases affectées (y compris les alliés)
    unites_touchees = []
    for unite in toutes_unites:
        if unite.pos in cases_affectees and unite != self and unite.vivant:  # Touche tout sauf l'archer lui-même
            # Appliquer la protection si applicable
            degats_infliges = protection(unite, self.dmg, toutes_unites)
            unites_touchees.append(unite)
    
    # Vérifier les morts après tous les dégâts
    for unite in toutes_unites[:]:  # Copie pour éviter les problèmes de modification pendant l'itération
        if unite.pv <= 0 and unite.vivant:
            unite.mourir(toutes_unites)
    
    return len(unites_touchees) > 0

def monture_libere(self, case_pos, toutes_unites):
    """Transforme le cavalier en guerrier et place un cheval sur sa position actuelle."""
    from unites import Guerrier, Cheval
    
    # Vérifier que la case est adjacente
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    case_adjacente = False
    
    for dq, dr in directions:
        if (q + dq, r + dr) == case_pos:
            case_adjacente = True
            break
    
    if not case_adjacente:
        return False
    
    # Vérifier que la case de destination est libre
    for unite in toutes_unites:
        if unite.pos == case_pos and unite.vivant:
            return False
    
    # Créer un cheval sur la position actuelle du cavalier
    cheval = Cheval(self.equipe, self.pos)
    toutes_unites.append(cheval)
    
    # Transformer le cavalier en guerrier à la nouvelle position
    self.pos = case_pos
    
    # Changer les stats pour devenir un guerrier (garder les PV actuels)
    pv_actuels = self.pv
    self.__class__ = Guerrier
    self.__init__(self.equipe, self.pos)
    self.pv = pv_actuels  # Conserver les PV du cavalier
    self.pm = 0  # Plus de mouvement après la transformation
    self.attaque_restantes = self.attaque_max  # Peut attaquer après transformation
    
    return True

def commandement(unite, cible, toutes_unites):
    """Augmente l'attaque d'un allié de l'attaque actuelle du roi, et +1 attaque supplémentaire."""
    from ia import hex_distance
    
    # Vérifier si c'est un allié
    if not isinstance(cible, (tuple, list)):
        # Si c'est une unité directement
        if cible.equipe != unite.equipe or not cible.vivant:
            return False
        
        # Vérifier la portée (2 cases)
        if hex_distance(unite.pos, cible.pos) > 2:
            return False
        
        # Appliquer les boosts
        cible.ba_commandement = unite.get_attaque_totale()

        # Donner +1 attaque supplémentaire
        cible.attaque_restantes += 1

        print(f"{unite.nom} commande {cible.nom} ! (+{unite.get_attaque_totale()} attaque, +1 attaque supplémentaire)")

        return True
    
    return False

def divertissement(self, toutes_unites):
    """S'il lui reste une attaque, marque toutes les unités adjacentes comme diverties (perdront 1 attaque au prochain tour)."""
    # Vérifier que l'unité a encore au moins une attaque
    if self.attaque_restantes <= 0:
        return
    
    # Trouver toutes les unités adjacentes (alliées et ennemies)
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = self.pos
    
    unites_diverties = []
    for dq, dr in directions:
        pos_adjacente = (q + dq, r + dr)
        
        # Chercher une unité à cette position (peu importe l'équipe)
        for unite in toutes_unites:
            if (unite.pos == pos_adjacente and 
                unite.vivant and 
                unite != self):  # Exclure le bouffon lui-même
                
                # Marquer l'unité comme divertie pour le prochain tour
                unite.diverti = True
                unites_diverties.append(unite)
                break  # Une seule unité par case
    
    if unites_diverties:
        print(f"{self.nom} divertit {len(unites_diverties)} unité(s) adjacente(s)!")

def manipulation(self, toutes_unites):
    """Toutes les unités avec 3PV ou moins passent dans votre camp tant qu'elles ont ≤4 PV."""
    unites_manipulees = []
    
    for unite in toutes_unites:
        if (unite.equipe != self.equipe and 
            unite.vivant and 
            unite.pv <= 3 and
            not hasattr(unite, 'manipulee_par')):  # Éviter la double manipulation
            
            # Marquer l'unité comme manipulée
            unite.equipe_originale = unite.equipe
            unite.equipe = self.equipe
            unite.manipulee_par = self  # Référence au marionettiste qui manipule
            
            # L'unité manipulée récupère ses actions
            unite.pm = unite.mv
            unite.attaque_restantes = unite.attaque_max
            
            unites_manipulees.append(unite)
            print(f"🎭 {unite.nom} ({unite.pv} PV) est manipulé par {self.nom}!")
    
    return unites_manipulees

def verifier_conditions_manipulation(toutes_unites):
    """Vérifie les conditions de manipulation en continu et libère les unités si nécessaire."""
    unites_a_liberer = []
    
    for unite in toutes_unites:
        if hasattr(unite, 'manipulee_par') and unite.vivant:
            marionettiste = unite.manipulee_par
            
            # Condition 1: Le marionettiste est mort
            if not marionettiste.vivant:
                unites_a_liberer.append(unite)
                print(f"🎭 {unite.nom} retrouve son libre arbitre car {marionettiste.nom} est mort!")
            
            # Condition 2: L'unité a maintenant plus de 4 PV
            elif unite.pv > 4:
                unites_a_liberer.append(unite)
                print(f"🎭 {unite.nom} ({unite.pv} PV) retrouve son libre arbitre car elle a plus de 4 PV!")
    
    # Libérer les unités qui ne remplissent plus les conditions
    for unite in unites_a_liberer:
        liberer_unite_manipulee(unite)

def liberer_unite_manipulee(unite):
    """Libère une unité manipulée et nettoie ses attributs."""
    if hasattr(unite, 'equipe_originale'):
        unite.equipe = unite.equipe_originale
        delattr(unite, 'equipe_originale')
    if hasattr(unite, 'manipulee_par'):
        delattr(unite, 'manipulee_par')

def liberer_toutes_unites_manipulees_par(marionettiste, toutes_unites):
    """Libère toutes les unités manipulées par un marionettiste spécifique."""
    for unite in toutes_unites:
        if (hasattr(unite, 'manipulee_par') and 
            unite.manipulee_par == marionettiste):
            liberer_unite_manipulee(unite)
            print(f"🎭 {unite.nom} est libérée car {marionettiste.nom} est mort!")

def gerer_fin_manipulation(toutes_unites):
    """Fonction de compatibilité - maintenant appelle verifier_conditions_manipulation."""
    verifier_conditions_manipulation(toutes_unites)

def protection(cible_originale, degats, toutes_unites):
    """
    Gère la redirection des dégâts vers les protecteurs adjacents.
    1. Applique d'abord l'armure de pierre de la cible originale (si elle en a)
    2. Partage les dégâts réduits entre les protecteurs
    3. Chaque protecteur applique ses propres défenses
    Retourne les dégâts totaux effectivement infligés.
    """
    # Trouver tous les protecteurs connectés (adjacents à la cible ou entre eux)
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = cible_originale.pos
    
    # 1. Trouver tous les protecteurs connectés (BFS)
    protecteurs = set()
    visited = set()
    queue = []
    # Démarre par les protecteurs adjacents à la cible
    for dq, dr in directions:
        pos_adj = (q + dq, r + dr)
        for unite in toutes_unites:
            if (unite.comp == "protection" and unite.pos == pos_adj and unite.vivant and unite.equipe == cible_originale.equipe):
                protecteurs.add(unite)
                queue.append(unite)
                visited.add(unite)
                break
    # Étendre à tous les protecteurs connectés (adjacents entre eux)
    while queue:
        current = queue.pop(0)
        cq, cr = current.pos
        for dq, dr in directions:
            pos_adj = (cq + dq, cr + dr)
            for unite in toutes_unites:
                if (unite.pos == pos_adj and unite.vivant and unite.equipe == cible_originale.equipe and unite.comp == "protection"):
                    if unite not in visited:
                        protecteurs.add(unite)
                        queue.append(unite)
                        visited.add(unite)
    protecteurs = list(protecteurs)
    
    if not protecteurs:
        # Pas de protection, la cible subit tous les dégâts normalement
        return cible_originale.subir_degats(degats)
    
    # ÉTAPE 1: Appliquer l'armure de pierre de la cible originale si elle en a
    degats_apres_armure_cible = degats
    if cible_originale.comp == "armure de pierre":
        degats_apres_armure_cible = max(0, degats - 2)
        print(f" {cible_originale.nom} a armure de pierre: {degats} → {degats_apres_armure_cible} dégâts")
    
    # ÉTAPE 2: Répartir les dégâts pour équilibrer les PV restants
    n = len(protecteurs)
    pv_initiaux = [p.pv for p in protecteurs]
    degats_restants = degats_apres_armure_cible
    parts = [0] * n
    # On va donner les dégâts un par un à celui qui a le plus de PV restant
    pv_apres = pv_initiaux[:]
    degats_a_rediriger = 0
    while degats_restants > 0:
        # Trouver l'indice du protecteur avec le plus de PV actuel
        idx = pv_apres.index(max(pv_apres))
        parts[idx] += 1
        pv_apres[idx] -= 1
        degats_restants -= 1
    print(f" {n} protecteurs protègent {cible_originale.nom} ! Dégâts répartis pour équilibrer les PV :")
    total_inflige = 0
    for i, protecteur in enumerate(protecteurs):
        print(f"  {protecteur.nom} subit {parts[i]} dégâts (PV initiaux: {pv_initiaux[i]} → finaux: {pv_initiaux[i]-parts[i]})")
        total_inflige += protecteur.subir_degats(parts[i])
        if protecteur.pv <= 0 and protecteur.vivant:
            protecteur.mourir(toutes_unites)
        degats_a_rediriger += max(0, parts[i] - (pv_initiaux[i]))  # Dégâts non absorbés par ce protecteur
    
    # ÉTAPE 3: Si des dégâts restent, la cible originale les subit
    if degats_a_rediriger > 0:
        print(f"  {cible_originale.nom} subit {degats_a_rediriger} dégâts restants (aucun protecteur n'a pu les absorber)")
        total_inflige += cible_originale.subir_degats(degats_a_rediriger)
        if cible_originale.pv <= 0 and cible_originale.vivant:
            cible_originale.mourir(toutes_unites)
    return total_inflige

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

def renaissance(self, toutes_unites):
    """80% de chance de revenir à la vie avec tous ses PV."""
    
    # La renaissance se déclenche quand l'unité est sur le point de mourir (PV <= 0)
    if self.vivant and self.pv <= 0 and random.random() < 0.8:  # 80% de chance
        print("Renaissance de", self.nom, "!")
        self.pv = self.pv_max
        # Réinitialiser les actions pour le tour suivant
        self.pm = self.mv
        self.attaque_restantes = self.attaque_max
        return True  # Indique que la renaissance a eu lieu
    
    return False

def armure_de_pierre(degats_recus):
    """Réduit tous les dégâts reçus de 2 points (minimum 0)."""
    return max(0, degats_recus - 2)

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

def regard_mortel(attaquant, cible):
    """Renvoie 0 si la cible est de tier 2 ou moins, sinon renvoie les dégâts normaux."""
    if cible.tier <= 2 and cible.equipe != attaquant.equipe and cible.vivant:
        print(f"{attaquant.nom} utilise son regard mortel sur {cible.nom} (tier {cible.tier})!")
        print(f"{cible.nom} succombe au regard mortel!")
        cible.pv = 0  # Tue la cible immédiatement
        return 0
    return attaquant.dmg  # Dégâts normaux si la cible est de tier > 2

def rage(attaquant):
    """Augmente l'attaque de 1 par attaque (accumulation permanente)."""
    # Initialise le compteur de rage s'il n'existe pas
    if not hasattr(attaquant, 'ba_rage'):
        attaquant.ba_rage = 0
    
    # Augmente le stack de rage
    attaquant.ba_rage += 1
    print(f"{attaquant.nom} entre en RAGE ! Attaque +{attaquant.ba_rage} (Total: {attaquant.get_attaque_totale()})")

def vol(defenseur, degats):
    """Ignore la première attaque subie (retourne les dégâts après réduction)."""
    # Initialise le compteur de vol s'il n'existe pas
    if not hasattr(defenseur, 'vol_utilise'):
        defenseur.vol_utilise = False
    
    # Si c'est la première attaque, l'ignorer
    if not defenseur.vol_utilise:
        defenseur.vol_utilise = True
        print(f"{defenseur.nom} utilise VOL ! La première attaque est ignorée.")
        return 0  # Aucun dégât subi
    
    # Les attaques suivantes passent normalement
    return degats

def venin_incapacitant(attaquant, cible):
    """Empêche la cible de se déplacer au prochain tour."""
    if cible.vivant and cible.equipe != attaquant.equipe:
        # Marquer la cible comme empoisonnée (ne peut pas bouger au prochain tour)
        cible.venin_incapacite = True
        print(f"{attaquant.nom} empoisonne {cible.nom} ! Elle ne pourra pas se déplacer au prochain tour.")
        return True
    return False

def sedition_venimeuse(attaquant, cible, toutes_unites):
    """La créature attaquée attaque une autre créature ennemie adjacente s'il y en a une."""
    if not cible.vivant or cible.equipe == attaquant.equipe:
        return False
    
    # Trouver les créatures alliées adjacentes à la cible
    directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
    q, r = cible.pos
    
    cibles_possibles = []
    for dq, dr in directions:
        pos_adjacente = (q + dq, r + dr)
        
        # Chercher une unité alliée de la cible à cette position
        for unite in toutes_unites:
            if (unite.pos == pos_adjacente and 
                unite.vivant and 
                unite.equipe == cible.equipe and  # Allié de la cible
                unite != cible):  # Pas la cible elle-même
                
                cibles_possibles.append(unite)
                break  # Une seule unité par case
    
    if cibles_possibles:
        # Choisir la première cible disponible
        cible_seduite = cibles_possibles[0]
        print(f"🐍✨ {attaquant.nom} séduit {cible.nom} ! {cible.nom} attaque {cible_seduite.nom} !")
        
        # La cible attaque la créature séduite (mais sans déclencher ses propres compétences)
        if cible.est_a_portee(cible_seduite):
            # Calculer les dégâts de la cible
            degats = cible.get_attaque_totale()
            degats_infliges = cible_seduite.subir_degats(degats)
            
            # Gestion de la mort si nécessaire
            if cible_seduite.pv <= 0:
                cible_seduite.mourir(toutes_unites)
            
            return True
    
    return False

def tir_precis(attaquant, cible, toutes_unites):
    """Tir précis : Attaque avec dégâts x1.5 à portée étendue (portée +1)."""
    if not cible or not cible.vivant:
        return False
    
    # Vérifier que la cible est ennemie
    if cible.equipe == attaquant.equipe:
        return False
    
    # Calculer la distance
    q1, r1 = attaquant.pos
    q2, r2 = cible.pos
    distance = max(abs(q1 - q2), abs(r1 - r2), abs((q1 + r1) - (q2 + r2)))
    
    # Vérifier la portée étendue (portée normale + 1)
    portee_etendue = attaquant.portee + comp_portee.get(attaquant.comp, 0)
    print(portee_etendue)
    if distance > portee_etendue:
        print(f"{cible.nom} est trop loin pour le tir précis (distance {distance}, portée max {portee_etendue})")
        return False
    
    # Tir précis activé : dégâts x1.5
    degats_base = attaquant.get_attaque_totale()
    degats_precis = int(degats_base * 1.5)
    
    print(f"{attaquant.nom} utilise TIR PRÉCIS ! Dégâts augmentés à {degats_precis} !")
    
    # Appliquer les dégâts avec protection
    degats_infliges = attaquant.appliquer_degats_avec_protection(cible, degats_precis, toutes_unites)
    
    # Gestion de la mort
    if cible.pv <= 0:
        cible.mourir(toutes_unites)
    
    return True


# Dictionnaire des compétences (nom -> description)
COMPETENCES = {
    # Morts-Vivants
    "sangsue": "Récupère des PV égaux aux dégâts infligés (peut dépasser le maximum).",
    "zombification": "Transforme l'unité ennemie tuée en zombie allié.",
    "tas d'os": "À la mort, se transforme en Tas d'Os de 1 PV.",
    "fantomatique": "Traverse les unités gratuitement (0 PM pour traverser, 1 PM par case vide).",
    "nécromancie": "Invoque un Squelette sur une case adjacente libre chaque tour.",
    "invocation": "Invoque aléatoirement une unité Morts-Vivants (tier 1-2) sur une case adjacente libre chaque tour.",
    
    # Religieux
    "soin": "Soigne un allié de 5 PV (maximum PV max de la cible).",
    "explosion sacrée": "Se sacrifie pour infliger ses PV actuels en dégâts à la cible attaquée uniquement.",
    "bouclier de la foi": "Donne 1 point de bouclier à tous les alliés adjacents chaque tour.",
    "bénédiction": "Augmente définitivement l'attaque de +2 et donne 1 bouclier à un allié.",
    "lumière vengeresse": "Regagne 1 attaque et peut continuer d'agir quand il tue un Mort-Vivant.",
    "aura sacrée": "Augmente définitivement l'attaque de +3 pour tous les alliés adjacents tant qu'il vit.",
    
    # Élémentaires
    "enracinement": "Régénère 2 PV en fin de tour si l'unité n'a pas bougé.",
    "vague apaisante": "Soigne tous les alliés adjacents de 2 PV chaque tour.",
    "renaissance": "80% de chance de revenir à la vie avec tous ses PV quand elle meurt.",
    "armure de pierre": "Réduit tous les dégâts reçus de 2 points (minimum 0).",
    "combustion différée": "L'unité touchée meurt automatiquement au bout de 3 tours ennemis.",
    
    # Royaume - Compétences actives
    "pluie de flèches": "Attaque de zone (portée 3) : inflige des dégâts à la cible et toutes les cases adjacentes, y compris aux alliés. Utilisable tous les 2 tours.",
    "monture libéré": "Se transforme en Guerrier à une case adjacente libre et crée un Cheval allié à sa position d'origine.",
    "commandement": "Donne +3 attaque temporaire et +1 attaque supplémentaire à un allié (portée 2). N'utilise pas d'attaque.",
    "divertissement": "Si il reste des attaques en fin de tour, toutes les unités adjacentes perdent 1 attaque au tour suivant.",
    "protection": "Subit les dégâts à la place des alliés adjacents (le protecteur le plus résistant prend tous les dégâts).",
    "manipulation": "Toutes les unités ennemies avec ≤4 PV rejoignent temporairement votre camp tant qu'elles ont ≤4 PV.",
    
    # Chimères - Compétences actives/passives
    "regard mortel": "Tue instantanément les unités ennemies de tier ≤2 touchées.",
    "rage": "Gagne définitivement +1 attaque après chaque attaque effectuée.",
    "vol": "Ignore complètement la première attaque subie.",
    "tir précis": "Attaque à portée +1 avec dégâts x1.5. Utilisable tous les 2 tours.",
    "venin incapacitant": "L'unité touchée ne peut pas se déplacer au tour suivant.",
    "sédition venimeuse": "L'unité attaquée est forcée d'attaquer un allié adjacent si possible.",
}

# Définition des cooldowns par compétence (en tours d'attente)
cooldowns = {
    # Compétences actives - 1 = utilisable chaque tour, 2 = un tour d'attente, etc.
    "soin": 1,  # Utilisable chaque tour
    "bénédiction": 1,  # Un tour d'attente entre utilisations
    "tir précis": 2,  # Un tours d'attente entre utilisations (utilisable 1 tour sur 2)
    "pluie de flèches": 2,  # Un tours d'attente entre utilisations (utilisable 1 tour sur 2)
    "Commandement": 1,
}

# Comp actives
competences_actives = ["soin", "bénédiction", "cristalisation", "pluie de flèches", "monture libéré", "commandement", "tir précis"]

# Comp qui nécessitent une attaque
comp_attaque = ["tir précis", "pluie de flèches"]

# Comp qui nécessitent une cible
comp_nec_cible = ["soin", "bénédiction", "cristalisation", "pluie de flèches",  "monture libéré", "commandement", "tir précis"]

# Comp qui nécessitent une cible ennemie
com_cib_ennemi = ["tir précis"]

# Comp qui nécessitent une cible alliée
comp_cib_allie = ["soin", "bénédiction", "commandement"]

# Comp qui fonctionne sur du vide
comp_cib_vide = ["cristalisation", "pluie de flèches", "monture libéré"]

# Fonction utilitaire pour déterminer si une compétence est active
def est_competence_active(nom_competence):
    """Retourne True si la compétence nécessite une cible."""
    return nom_competence in competences_actives

def peut_cibler_allie(nom_competence):
    """Retourne True si la compétence peut cibler des alliés."""
    return nom_competence in comp_cib_allie

def peut_cibler_ennemi(nom_competence):
    """Retourne True si la compétence peut cibler des ennemis."""
    return nom_competence in com_cib_ennemi

def peut_cibler_case_vide(nom_competence):
    """Retourne True si la compétence peut cibler des cases vides."""
    return nom_competence in comp_cib_vide

def utiliser_competence_active(unite, nom_competence, cible, toutes_unites=None):
    """Utilise une compétence active sur une cible."""
    if nom_competence == "soin":
        return soin(unite, cible)
    elif nom_competence == "bénédiction":
        return bénédiction(unite, cible)
    elif nom_competence == "cristalisation":
        return cristalisation(unite, cible, toutes_unites)
    elif nom_competence == "pluie de flèches":
        # Gérer le cas où cible est déjà une position (tuple) ou un objet avec .pos
        if isinstance(cible, tuple):
            return pluie_de_fleches(unite, cible, toutes_unites)
        else:
            return pluie_de_fleches(unite, cible.pos if cible else None, toutes_unites)
    elif nom_competence == "monture libéré":
        return monture_libere(unite, cible, toutes_unites)
    elif nom_competence == "commandement":
        return commandement(unite, cible, toutes_unites)
    elif nom_competence == "tir précis":
        return tir_precis(unite, cible, toutes_unites)
    return False