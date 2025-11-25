""" Compétences des unités."""
#pylint: disable=line-too-long
#pylint: disable=import-outside-toplevel
#pylint: disable=unnecessary-dunder-call
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
    if DO_PRINT:
        print("Sangsue :", degats_infliges, "PV récupérés")
    self.set_pv(self.get_pv() + degats_infliges)


def zombification(self, cible):
    """Transforme l'unite morte en zombie sous le contrôle du joueur de l'attaquant"""
    if DO_PRINT:
        print("Zombification effectuée sur :", cible.get_name())
    if not cible.is_vivant() and cible.get_nom() != "Zombie":
        cible.__class__ = self.__class__
        cible.__init__(self.get_equipe(), cible.get_pos())
        cible.pm = 0
        cible.attaque_restantes = 0


def tas_d_os(self):
    """Transforme l'unité morte en tas d'os."""
    from unites_liste import Tas_D_Os
    # Transformation en tas d'os : c'est une nouvelle unité is_vivant()e
    self.__class__ = Tas_D_Os
    self.__init__(self.get_equipe(), self.get_pos())
    # Le tas d'os est is_vivant() avec 1 PV (défini dans Tas_D_Os.__init__)


def cases_fantomatiques(unite, toutes_unites, q_range=None, r_range=None):
    """Retourne toutes les cases accessibles en traversant les unités (traverser une unité ne coûte pas de PM, s'arrêter sur une case vide coûte 1 PM par case vide)."""
    from collections import deque

    # Limites par défaut si non spécifiées
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)

    accessibles = {}
    file = deque([(unite.get_pos(), 0)])
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    vus = dict()  # (q, r): cout minimal
    occupees = {u.get_pos() for u in toutes_unites if u.is_vivant() and u != unite}
    while file:
        (q, r), cout = file.popleft()
        if cout > unite.get_pm():
            continue
        if (q, r) in vus and cout >= vus[(q, r)]:
            continue
        vus[(q, r)] = cout
        if (q, r) != unite.get_pos() and (q, r) not in occupees:
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


def necromancie(self, toutes_unites, plateau, q_range=None, r_range=None):
    """Invoque un Squelette sur une case adjacente vide à chaque tour."""
    from unites_liste import Squelette

    # Limites par défaut si non spécifiées
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)

    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    random.shuffle(directions)  # Pour varier les positions d'invocation
    q, r = self.get_pos()
    for dq, dr in directions:
        new_pos = (q+dq, r+dr)
        new_q, new_r = new_pos

        # VÉRIFIER QUE LA POSITION EST DANS LA GRILLE
        if new_q not in q_range or new_r not in r_range:
            continue

        if plateau.est_case_vide(new_pos, toutes_unites):
            toutes_unites.append(Squelette(self.get_equipe(), new_pos))
            break


def invocation(self, toutes_unites, plateau, q_range=None, r_range=None):
    """Invoque deux unité Morts-Vivants de tier 1 ou 2 sur une case adjacente vide à chaque tour."""
    from unites_liste import Goule, Squelette, Spectre, Zombie, Vampire

    # Limites par défaut si non spécifiées
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)

    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    random.shuffle(directions)  # Pour varier les positions d'invocation
    q, r = self.get_pos()
    candidates = [Goule, Squelette, Spectre, Zombie, Vampire]
    random.shuffle(candidates)
    for _ in range(2):
        for dq, dr in directions:
            new_pos = (q+dq, r+dr)
            new_q, new_r = new_pos

            # VÉRIFIER QUE LA POSITION EST DANS LA GRILLE
            if new_q not in q_range or new_r not in r_range:
                continue

            if plateau.est_case_vide(new_pos, toutes_unites):
                unite_class = random.choice(candidates)
                toutes_unites.append(unite_class(self.get_equipe(), new_pos))
                break

# ========== COMPÉTENCES RELIGIEUX ==========


def soin(self, cible):
    """Soigne la cible de 5 points de vie."""
    if cible.get_equipe() == self.get_equipe() and cible.is_vivant():
        cible.set_pv(min(cible.get_pv() + 5, cible.get_pv_max()))
        return True
    return False


def explosion_sacree(self, toutes_unites, cible_attaquee=None):
    """Se sacrifie en attaquant pour infliger ses points de vie en dégâts à la cible uniquement."""
    degats = self.get_pv()  # Utilise ses PV actuels comme dégâts

    # Infliger des dégâts uniquement à la cible directe si c'est un ennemi
    if cible_attaquee and cible_attaquee.get_equipe() != self.get_equipe() and cible_attaquee.is_vivant():
        # Appliquer la protection si applicable
        protection(cible_attaquee, degats, toutes_unites)

        # Vérifier si la cible ou les protecteurs meurent
        for unite in toutes_unites:
            if unite.get_pv() <= 0 and unite.is_vivant():
                unite.mourir(toutes_unites)

    # Marquer pour mourir après l'animation (ne pas mourir immédiatement)
    self.explosion_sacree_pending = True


def bouclier_de_la_foi(self, toutes_unites):
    """Applique 1 bouclier sur les unités alliées adjacentes."""
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = self.get_pos()

    for unite in toutes_unites:
        if unite.get_equipe() == self.get_equipe() and unite != self and unite.is_vivant():
            unite_q, unite_r = unite.get_pos()
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Ajouter un bouclier temporaire
                    unite.set_bouclier(unite.get_bouclier() + 1)
                    break


def benediction(self, cible):
    """Augmente l'attaque de 2 et applique 1 bouclier à la cible."""
    if cible.get_equipe() == self.get_equipe() and cible.is_vivant():
        # Ajouter un buff permanent
        if not hasattr(cible, 'ba_benediction'):
            cible.ba_benediction = 2
            print (f"✨ Bénédiction appliquée à {cible.get_nom()} (+2 attaque)")
            print(f"A été bénis ? {hasattr(cible, 'ba_benediction')}")
            cible.set_bouclier(cible.get_bouclier() + 1)
        return True
    return False


def lumiere_vengeresse(self, cible):
    """Regagne son attaque lorsqu'il tue un Mort-Vivant."""
    if cible.get_faction() != "Morts-Vivants":
        return
    self.set_attaque_restantes(self.get_attaque_restantes() + 1)
    # Flag pour indiquer que cette unité devrait continuer à agir
    if not hasattr(self, 'lumiere_vengeresse'):
        self.lumiere_vengeresse = True


def aura_sacree(self, toutes_unites):
    """Bonus de dégâts pour tout les alliés adjacents."""
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = self.get_pos()

    for unite in toutes_unites:
        if unite.get_equipe() == self.get_equipe() and unite != self and unite.is_vivant():
            unite_q, unite_r = unite.get_pos()
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Bonus permanent tant que l'ArchAnge est is_vivant()
                    if not hasattr(unite, 'ba_aura_sacree'):
                        unite.ba_aura_sacree = 3
                    break

# ========== COMPÉTENCES ROYAUME ==========


def pluie_de_fleches(self, cible_pos, toutes_unites):
    """Attaque AOE sur la case cible et toutes les cases adjacentes."""
    # Vérifier que la case cible est à portée (jusqu'à 3 cases)
    q_self, r_self = self.get_pos()
    q_cible, r_cible = cible_pos
    distance = max(abs(q_self - q_cible), abs(r_self - r_cible),
                   abs((q_self + r_self) - (q_cible + r_cible)))

    if distance > 3:
        return False

    # Cases affectées : la case cible + ses adjacentes
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    cases_affectees = [cible_pos]  # Case cible

    # Ajouter les cases adjacentes à la cible
    for dq, dr in directions:
        case_adjacente = (q_cible + dq, r_cible + dr)
        cases_affectees.append(case_adjacente)

    # Attaquer TOUTES les unités dans les cases affectées (y compris les alliés)
    unites_touchees = []
    for unite in toutes_unites:
        if unite.get_pos() in cases_affectees and unite.is_vivant():  # Touche tout sauf l'archer lui-même
            # Appliquer la protection si applicable
            protection(unite, self.get_dmg(), toutes_unites)
            unites_touchees.append(unite)

    # Vérifier les morts après tous les dégâts
    # Copie pour éviter les problèmes de modification pendant l'itération
    for unite in toutes_unites[:]:
        if unite.get_pv() <= 0 and unite.is_vivant():
            unite.mourir(toutes_unites)

    return len(unites_touchees) > 0


def monture_libere(self, case_pos, toutes_unites):
    """Transforme le cavalier en guerrier et place un cheval sur sa position actuelle."""
    from unites_liste import Guerrier, Cheval

    # Vérifier que la case est adjacente
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = self.get_pos()
    case_adjacente = False

    for dq, dr in directions:
        if (q + dq, r + dr) == case_pos:
            case_adjacente = True
            break

    if not case_adjacente:
        return False

    # Vérifier que la case de destination est libre
    for unite in toutes_unites:
        if unite.get_pos() == case_pos and unite.is_vivant():
            return False

    # Créer un cheval sur la position actuelle du cavalier
    cheval = Cheval(self.get_equipe(), self.get_pos())
    toutes_unites.append(cheval)

    # Transformer le cavalier en guerrier à la nouvelle position
    self.set_pos(case_pos)

    # Changer les stats pour devenir un guerrier (garder les PV actuels)
    pv_actuels = self.get_pv()
    self.__class__ = Guerrier
    self.__init__(self.get_equipe(), self.get_pos())
    self.set_pv(pv_actuels)  # Conserver les PV du cavalier
    self.pm = 0  # Plus de mouvement après la transformation
    self.attaque_restantes = self.attaque_max  # Peut attaquer après transformation

    return True


def commandement(unite, cible):
    """Augmente l'attaque d'un allié de l'attaque actuelle du roi, et +1 attaque supplémentaire."""
    from ia import hex_distance
    # Vérifier si c'est un allié
    if not isinstance(cible, (tuple, list)):
        # Si c'est une unité directement
        if cible.get_equipe() != unite.get_equipe() or not cible.is_vivant():
            return False

        if hasattr(cible, 'ba_commandement'):
            return False  # Ne peut pas bénéficier de commandement plusieurs fois

        # Vérifier la portée (2 cases)
        if hex_distance(unite.get_pos(), cible.get_pos()) > comp_portee["commandement"]:
            return False

        # Appliquer les boosts
        cible.ba_commandement = unite.get_attaque_totale()
        cible.attaque_restantes += 1

        print(f"{unite.get_nom()} commande {cible.get_nom()} ! (+{unite.get_attaque_totale()} attaque, +1 attaque supplémentaire)")

        return True

    return False


def divertissement(self, toutes_unites):
    """S'il lui reste une attaque, marque toutes les unités adjacentes comme diverties (perdront 1 attaque au prochain tour)."""
    # Vérifier que l'unité a encore au moins une attaque
    if self.attaque_restantes <= 0:
        return

    # Trouver toutes les unités adjacentes (alliées et ennemies)
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = self.get_pos()

    unites_diverties = []
    for dq, dr in directions:
        pos_adjacente = (q + dq, r + dr)

        # Chercher une unité à cette position (peu importe l'équipe)
        for unite in toutes_unites:
            if (unite.get_pos() == pos_adjacente and
                unite.is_vivant() and
                    unite != self):  # Exclure le bouffon lui-même

                # Marquer l'unité comme divertie pour le prochain tour
                unite.diverti = True
                unites_diverties.append(unite)
                break  # Une seule unité par case

    if unites_diverties:
        print(f"{self.get_nom()} divertit {len(unites_diverties)} unité(s) adjacente(s)!")


def manipulation(self, toutes_unites):
    """Toutes les unités avec 3PV ou moins passent dans votre camp tant qu'elles ont ≤4 PV."""
    unites_manipulees = []

    for unite in toutes_unites:
        if (unite.get_equipe() != self.get_equipe() and
            unite.is_vivant() and
            unite.get_pv() <= 3 and
                not hasattr(unite, 'manipulee_par')):  # Éviter la double manipulation

            # Marquer l'unité comme manipulée
            unite.equipe_originale = unite.get_equipe()
            unite.set_equipe(self.get_equipe())
            unite.manipulee_par = self  # Référence au marionettiste qui manipule

            # L'unité manipulée récupère ses actions
            unite.pm = unite.mv
            unite.attaque_restantes = unite.attaque_max

            unites_manipulees.append(unite)
            print(f"🎭 {unite.get_nom()} ({unite.get_pv()} PV) est manipulé par {self.get_nom()}!")

    return unites_manipulees


def verifier_conditions_manipulation(toutes_unites):
    """Vérifie les conditions de manipulation en continu et libère les unités si nécessaire."""
    unites_a_liberer = []

    for unite in toutes_unites:
        if hasattr(unite, 'manipulee_par') and unite.is_vivant():
            marionettiste = unite.manipulee_par

            # Condition 1: Le marionettiste est mort
            if not marionettiste.is_vivant():
                unites_a_liberer.append(unite)
                print(
                    f"🎭 {unite.get_nom()} retrouve son libre arbitre car {marionettiste.get_nom()} est mort!")

            # Condition 2: L'unité a maintenant plus de 4 PV
            elif unite.get_pv() > 4:
                unites_a_liberer.append(unite)
                print(
                    f"🎭 {unite.get_nom()} ({unite.get_pv()} PV) retrouve son libre arbitre car elle a plus de 4 PV!")

    # Libérer les unités qui ne remplissent plus les conditions
    for unite in unites_a_liberer:
        liberer_unite_manipulee(unite)


def liberer_unite_manipulee(unite):
    """Libère une unité manipulée et nettoie ses attributs."""
    if hasattr(unite, 'equipe_originale'):
        unite.set_equipe(unite.equipe_originale)
        delattr(unite, 'equipe_originale')
    if hasattr(unite, 'manipulee_par'):
        delattr(unite, 'manipulee_par')


def liberer_toutes_unites_manipulees_par(marionettiste, toutes_unites):
    """Libère toutes les unités manipulées par un marionettiste spécifique."""
    for unite in toutes_unites:
        if (hasattr(unite, 'manipulee_par') and
                unite.manipulee_par == marionettiste):
            liberer_unite_manipulee(unite)
            print(f"🎭 {unite.get_nom()} est libérée car {marionettiste.get_nom()} est mort!")


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
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = cible_originale.get_pos()

    # 1. Trouver tous les protecteurs connectés (BFS)
    protecteurs = set()
    visited = set()
    queue = []
    # Démarre par les protecteurs adjacents à la cible
    for dq, dr in directions:
        pos_adj = (q + dq, r + dr)
        for unite in toutes_unites:
            if (unite.get_competence() == "protection" and unite.get_pos() == pos_adj and unite.is_vivant() and unite.get_equipe() == cible_originale.get_equipe()):
                protecteurs.add(unite)
                queue.append(unite)
                visited.add(unite)
                break
    # Étendre à tous les protecteurs connectés (adjacents entre eux)
    while queue:
        current = queue.pop(0)
        cq, cr = current.get_pos()
        for dq, dr in directions:
            pos_adj = (cq + dq, cr + dr)
            for unite in toutes_unites:
                if (unite.get_pos() == pos_adj and unite.is_vivant()
                    and unite.get_equipe() == cible_originale.get_equipe()
                    and unite.get_competence() == "protection"):
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
        print(
            f" {cible_originale.get_nom()} a armure de pierre: {degats} → {degats_apres_armure_cible} dégâts")

    # ÉTAPE 2: Répartir les dégâts pour équilibrer les PV restants
    n = len(protecteurs)
    pv_initiaux = [p.get_pv() for p in protecteurs]
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
    print(f" {n} protecteurs protègent {cible_originale.get_nom()} ! Dégâts répartis pour équilibrer les PV :")
    total_inflige = 0
    for i, protecteur in enumerate(protecteurs):
        print(
            f"  {protecteur.get_nom()} subit {parts[i]} dégâts (PV initiaux: {pv_initiaux[i]} → finaux: {pv_initiaux[i]-parts[i]})")
        total_inflige += protecteur.subir_degats(parts[i])
        if protecteur.get_pv() <= 0 and protecteur.is_vivant():
            protecteur.mourir(toutes_unites)
        # Dégâts non absorbés par ce protecteur
        degats_a_rediriger += max(0, parts[i] - (pv_initiaux[i]))

    # ÉTAPE 3: Si des dégâts restent, la cible originale les subit
    if degats_a_rediriger > 0:
        print(f"  {cible_originale.get_nom()} subit {degats_a_rediriger} dégâts restants (aucun protecteur n'a pu les absorber)")
        total_inflige += cible_originale.subir_degats(degats_a_rediriger)
        if cible_originale.get_pv() <= 0 and cible_originale.is_vivant():
            cible_originale.mourir(toutes_unites)
    return total_inflige

# ========== COMPÉTENCES ÉLÉMENTAIRES ==========


def enracinement(self):
    """Si l'unité n'a pas bougé en fin de tour, régénère 2 PV."""
    # L'enracinement se déclenche si l'unité n'a pas dépensé de PM (pas bougé)
    if self.get_pm() == self.get_mv():  # N'a pas bougé (PM restants = MV max)
        if self.get_pv() + 2 <= self.get_pv_max():
            self.set_pv(self.get_pv() + 2)
        else:
            self.set_pv(self.get_pv_max())


def vague_apaisante(self, toutes_unites):
    """Soigne les unités alliées adjacentes de 2 PV (comme bouclier de la foi mais avec soin)."""
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = self.get_pos()

    for unite in toutes_unites:
        if unite.get_equipe() == self.get_equipe() and unite != self and unite.is_vivant():
            unite_q, unite_r = unite.get_pos()
            for dq, dr in directions:
                if (q+dq, r+dr) == (unite_q, unite_r):
                    # Soigner l'unité adjacente
                    if unite.get_pv() + 2 <= unite.get_pv_max():
                        unite.set_pv(unite.get_pv() + 2)
                    else:
                        unite.set_pv(unite.get_pv_max())
                    break


def cristalisation(self, cible_pos, toutes_unites):
    """Crée un Cristal sur une case adjacente à 1 de portée."""
    from unites_liste import Cristal
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = self.get_pos()

    # Vérifier si la cible est adjacente
    for dq, dr in directions:
        if (q+dq, r+dr) == cible_pos:
            # Vérifier que la case est vide
            case_libre = True
            for unite in toutes_unites:
                if unite.get_pos() == cible_pos and unite.is_vivant():
                    case_libre = False
                    break

            if case_libre:
                cristal = Cristal(self.get_equipe(), cible_pos)
                toutes_unites.append(cristal)
                return True

    return False


def renaissance(self):
    """80% de chance de revenir à la vie avec tous ses PV."""

    # La renaissance se déclenche quand l'unité est sur le point de mourir (PV <= 0)
    if self.is_vivant() and self.get_pv() <= 0 and random.random() < 0.8:  # 80% de chance
        print("Renaissance de", self.get_nom(), "!")
        self.set_pv(self.get_pv_max())
        # Réinitialiser les actions pour le tour suivant
        self.set_pm(self.get_mv())
        self.set_attaque_restantes(self.get_attaque_max())
        return True  # Indique que la renaissance a eu lieu

    return False


def armure_de_pierre(degats_recus):
    """Réduit tous les dégâts reçus de 2 points (minimum 0)."""
    return max(0, degats_recus - 2)


def combustion_differee(attaquant, cible):
    """Marque la cible pour mourir dans 3 tours."""
    if not hasattr(cible, 'combustion_differee'):
        cible.combustion_differee = 3
        cible.combustion_attaquant = attaquant.get_equipe()
        print(
            f"🔥 {cible.get_nom()} est marqué par la combustion différée! Mort dans 3 tours.")


def gerer_combustion_differee(unite, toutes_unites):
    """Vérifie et applique la combustion différée en fin de tour ennemi."""
    if hasattr(unite, 'combustion_tours_restants') and unite.combustion_tours_restants > 0:
        unite.combustion_tours_restants -= 1
        print(
            f"🔥 {unite.get_nom()} - Combustion: {unite.combustion_tours_restants} tours restants")

        if unite.combustion_tours_restants == 0:
            print(f"💥 {unite.get_nom()} succombe à la combustion différée!")
            unite.set_pv(0)
            unite.mourir(toutes_unites)
            # Nettoyer l'effet
            if hasattr(unite, 'combustion_tours_restants'):
                delattr(unite, 'combustion_tours_restants')
            if hasattr(unite, 'combustion_attaquant'):
                delattr(unite, 'combustion_attaquant')


def regard_mortel(attaquant, cible):
    """Renvoie 0 si la cible est de tier 2 ou moins, sinon renvoie les dégâts normaux."""
    if cible.tier <= 2 and cible.get_equipe() != attaquant.get_equipe() and cible.is_vivant():
        print(
            f"{attaquant.get_nom()} utilise son regard mortel sur {cible.get_nom()} (tier {cible.tier})!")
        print(f"{cible.get_nom()} succombe au regard mortel!")
        cible.set_pv(0)  # Tue la cible immédiatement
        return 0
    return attaquant.dmg  # Dégâts normaux si la cible est de tier > 2


def rage(attaquant):
    """Augmente l'attaque de 1 par attaque (accumulation permanente)."""
    # Initialise le compteur de rage s'il n'existe pas
    if not hasattr(attaquant, 'ba_rage'):
        attaquant.ba_rage = 0

    # Augmente le stack de rage
    attaquant.ba_rage += 1
    print(f"{attaquant.get_nom()} entre en RAGE ! Attaque +{attaquant.ba_rage} (Total: {attaquant.get_attaque_totale()})")


def vol(defenseur, degats):
    """Ignore la première attaque subie (retourne les dégâts après réduction)."""
    # Initialise le compteur de vol s'il n'existe pas
    if not hasattr(defenseur, 'vol_utilise'):
        defenseur.vol_utilise = False

    # Si c'est la première attaque, l'ignorer
    if not defenseur.vol_utilise:
        defenseur.vol_utilise = True
        print(f"{defenseur.get_nom()} utilise VOL ! La première attaque est ignorée.")
        return 0  # Aucun dégât subi

    # Les attaques suivantes passent normalement
    return degats


def venin_incapacitant(attaquant, cible):
    """Empêche la cible de se déplacer au prochain tour."""
    if cible.is_vivant() and cible.get_equipe() != attaquant.get_equipe():
        # Marquer la cible comme empoisonnée (ne peut pas bouger au prochain tour)
        cible.venin_incapacite = True
        print(
            f"{attaquant.get_nom()} empoisonne {cible.get_nom()} ! Elle ne pourra pas se déplacer au prochain tour.")
        return True
    return False


def sedition_venimeuse(attaquant, cible, toutes_unites):
    """La créature attaquée attaque une autre créature ennemie adjacente s'il y en a une."""
    if not cible.is_vivant() or cible.get_equipe() == attaquant.get_equipe():
        return False

    # Trouver les créatures alliées adjacentes à la cible
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = cible.get_pos()

    cibles_possibles = []
    for dq, dr in directions:
        pos_adjacente = (q + dq, r + dr)

        # Chercher une unité alliée de la cible à cette position
        for unite in toutes_unites:
            if (unite.get_pos() == pos_adjacente and
                unite.is_vivant() and
                unite.get_equipe() == cible.get_equipe() and  # Allié de la cible
                    unite != cible):  # Pas la cible elle-même

                cibles_possibles.append(unite)
                break  # Une seule unité par case

    if cibles_possibles:
        # Choisir la première cible disponible
        cible_seduite = cibles_possibles[0]
        print(
            f"🐍✨ {attaquant.get_nom()} séduit {cible.get_nom()} ! {cible.get_nom()} attaque {cible_seduite.get_nom()} !")

        # La cible attaque la créature séduite (mais sans déclencher ses propres compétences)
        if cible.est_a_portee(cible_seduite):
            # Calculer les dégâts de la cible
            degats = cible.get_attaque_totale()
            cible_seduite.subir_degats(degats)

            # Gestion de la mort si nécessaire
            if cible_seduite.get_pv() <= 0:
                cible_seduite.mourir(toutes_unites)

            return True

    return False


def tir_precis(attaquant, cible, toutes_unites):
    """Tir précis : Attaque avec dégâts x1.5 à portée étendue (portée +1)."""
    if not cible or not cible.is_vivant():
        return False

    # Vérifier que la cible est ennemie
    if cible.get_equipe() == attaquant.get_equipe():
        return False

    # Calculer la distance
    q1, r1 = attaquant.get_pos()
    q2, r2 = cible.get_pos()
    distance = max(abs(q1 - q2), abs(r1 - r2), abs((q1 + r1) - (q2 + r2)))

    # Vérifier la portée étendue (portée normale + 1)
    portee_etendue = attaquant.portee + comp_portee.get(attaquant.comp, 0)
    print(portee_etendue)
    if distance > portee_etendue:
        print(f"{cible.get_nom()} est trop loin pour le tir précis (distance {distance}, portée max {portee_etendue})")
        return False

    # Tir précis activé : dégâts x1.5
    degats_base = attaquant.get_attaque_totale()
    degats_precis = int(degats_base * 1.5)

    print(f"{attaquant.get_nom()} utilise TIR PRÉCIS ! Dégâts augmentés à {degats_precis} !")

    # Appliquer les dégâts avec protection
    attaquant.appliquer_degats_avec_protection(
        cible, degats_precis, toutes_unites)

    # Gestion de la mort
    if cible.get_pv() <= 0:
        cible.mourir(toutes_unites)

    return True


# Dictionnaire des compétences (nom -> description)
COMPETENCES = {
    # Morts-Vivants
    "aura sacrée": "Augmente définitivement les DMG de +3 pour tous les alliés adjacents tant que l'unité est en vie. (Non stackable)",
    "armure de pierre": "Réduit tous les dégâts reçus de 2 points (minimum 0).",
    "bénédiction": "Augmente définitivement l'attaque de +2 et donne 1 bouclier à un allié. (Non stackable, portée : 3).",
    "bouclier de la foi": "Donne 1 point de bouclier à tous les alliés adjacents. (Chaque tour)",
    "combustion différée": "L'unité touchée meurt automatiquement au bout de 3 tours ennemis.",
    "commandement": "Donne +3 DMG temporaire et +1 attaque supplémentaire temporaire à un allié. (Non stackable, Portée : 2)",
    "cristalisation": "Crée un cristal de 10PV sur une case adjacente sélectionnée.",
    "divertissement": "S'il reste au moins une attaque en fin de tour à l'unité, toutes les unités adjacentes perdent une attaque au tour suivant.",
    "enracinement": "Régénère 2 PV en fin de tour si l'unité n'a pas bougé.",
    "explosion sacrée": "Se sacrifie pour infliger ses PV actuels en dégâts à la cible attaquée.",
    "fantomatique": "Permet de passer au travers des unités (ne coûte pas de PM).",
    "invocation": "Invoque aléatoirement deux unité Morts-Vivants (tier 1-2) sur une case adjacente libre chaque tour.",
    "lumière vengeresse": "L'unité regagne 1 attaque quand elle tue une unité de la faction Mort-Vivant.",
    "manipulation": "Toutes les unités ennemies avec 4 PV ou moins rejoignent votre équipe tant qu'elles ont 3 PV ou moins.",
    "monture libéré": "L'unité se transforme en Guerrier sur une case adjacente libre et crée un Cheval allié sur sa position d'origine.",
    "nécromancie": "Invoque un Squelette sur une case adjacente libre chaque tour.",
    "rage": "L'unité gagne +1 DMG après chaque attaque effectuée. (Stackable)",
    "regard mortel": "Tue instantanément les unités ennemies de tier 2 ou moins touchées.",
    "renaissance": "L'unité a 80% de chance de revenir à la vie avec tous ses PV quand elle meurt.",
    "pluie de flèches": "L'unité inflige des dégâts à la cible et toutes les unités adjacentes. (Portée : 3, Rechargement : 1 tour)",
    "protection": "Les unités subissent les dégâts à la place des alliés adjacents les dégats s'équilibrent pour que chaque protecteur aient le même nombre de poits de vie.",
    "sangsue": "L'unité gagné des PV égaux aux dégâts infligés (peut dépasser le maximum).",
    "sédition venimeuse": "L'unité attaquée est forcée d'attaquer un allié adjacent si possible.",
    "soin": "Soigne un allié de 5 PV. (Portée : 2)",
    "tas d'os": "À la mort de l'unité, se transforme en Tas d'Os.",
    "tir précis": "L'unité attaque à portée +1 avec dmg x1.5. (Rechargement : 1 tour)",
    "vague apaisante": "Soigne tous les alliés adjacents de 2 PV chaque tour.",
    "venin incapacitant": "L'unité touchée ne peut pas se déplacer au tour suivant.",
    "vol": "Ignore complètement la première attaque subie.",
    "zombification": "Transforme l'unité ennemie tuée en zombie allié (de).",
}

# liste des noms des compétences dans le jeu par rapport à dans le code
nom_competences = {
    "aura sacrée": "aura_sacree",
    "armure de pierre": "armure_de_pierre",
    "bénédiction": "benediction",
    "bouclier de la foi": "bouclier_de_la_foi",
    "combustion différée": "combustion_differee",
    "commandement": "commandement",
    "cristalisation": "cristalisation",
    "divertissement": "divertissement",
    "enracinement": "enracinement",
    "explosion sacrée": "explosion_sacree",
    "fantomatique": "fantomatique",
    "invocation": "invocation",
    "lumière vengeresse": "lumiere_vengeresse",
    "manipulation": "manipulation",
    "monture libéré": "monture_libere",
    "nécromancie": "necromancie",
    "rage": "rage",
    "regard mortel": "regard_mortel",
    "renaissance": "renaissance",
    "pluie de flèches": "pluie_de_fleches",
    "protection": "protection",
    "sangsue": "sangsue",
    "sédition venimeuse": "sedition_venimeuse",
    "soin": "soin",
    "tas d'os": "tas_d_os",
    "tir précis": "tir_precis",
    "vague apaisante": "vague_apaisante",
    "venin incapacitant": "venin_incapacitant",
    "vol": "vol",
    "zombification": "zombification"
}

# Définition des cooldowns par compétence (en tours d'attente)
cooldowns = {
    # Compétences actives - 1 = utilisable chaque tour, 2 = un tour d'attente, etc.
    "soin": 1,  # Utilisable chaque tour
    "bénédiction": 1,  # Un tour d'attente entre utilisations
    # Un tours d'attente entre utilisations (utilisable 1 tour sur 2)
    "tir précis": 2,
    # Un tours d'attente entre utilisations (utilisable 1 tour sur 2)
    "pluie de flèches": 2,
    "Commandement": 1,
}

buffs = {
    "ba_aura_sacree": 3,  # +3 DMG permanent
    "ba_benediction": 2,  # +2 DMG permanent
    "ba_commandement": 0,  # Variable, dépend de l'attaquant
    "ba_rage": 1,  # +1 DMG par stack
}

# Comp actives
competences_actives = ["soin", "bénédiction", "cristalisation",
                       "pluie de flèches", "monture libéré", "commandement", "tir précis"]

# Comp qui nécessitent une attaque
comp_attaque = ["tir précis", "pluie de flèches"]

# Comp qui nécessitent une cible
comp_nec_cible = ["soin", "bénédiction", "cristalisation",
                  "pluie de flèches",  "monture libéré", "commandement", "tir précis"]

# Comp qui nécessitent une cible ennemie
com_cib_ennemi = ["tir précis"]

# Comp qui nécessitent une cible alliée
comp_cib_allie = ["soin", "bénédiction", "commandement"]

# Comp qui fonctionne sur du vide
comp_cib_vide = ["cristalisation", "pluie de flèches", "monture libéré"]


def is_competence(nom_competence):
    """Retourne True si le nom correspond à une compétence."""
    return nom_competence in nom_competences


def get_cooldown(nom_competence):
    """Retourne le cooldown de la compétence (0 si passive ou inconnue)."""
    if not is_competence(nom_competence):
        raise ValueError(f"Compétence inconnue : {nom_competence}")
    cooldown = cooldowns.get(nom_competence, 0)
    if cooldown == -1:
        raise ValueError(f"Compétence inconnue : {nom_competence}")
    return cooldown


def get_buff(nom_buff):
    """Retourne l'existence d'un buff. Retourne -1 si inconnu."""
    buff = buffs.get(nom_buff, -1)
    if buff == -1:
        raise ValueError(f"Buff inconnu : {nom_buff}")
    return buff


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
        return benediction(unite, cible)
    elif nom_competence == "cristalisation":
        return cristalisation(unite, cible, toutes_unites)
    elif nom_competence == "pluie de flèches":
        # Gérer le cas où cible est déjà une position (tuple) ou un objet avec .get_pos()
        if isinstance(cible, tuple):
            return pluie_de_fleches(unite, cible, toutes_unites)
        else:
            return pluie_de_fleches(unite, cible.get_pos() if cible else None, toutes_unites)
    elif nom_competence == "monture libéré":
        return monture_libere(unite, cible, toutes_unites)
    elif nom_competence == "commandement":
        return commandement(unite, cible)
    elif nom_competence == "tir précis":
        return tir_precis(unite, cible, toutes_unites)
    return False
