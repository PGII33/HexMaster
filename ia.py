""" IA file """
# pylint: disable=line-too-long
# IA V2 - Architecture basée sur le scoring d'actions


from typing import List, Tuple, Union  # Optional
from dataclasses import dataclass
from unites import Unite
from utils_pos import hex_distance, est_adjacent, est_a_portee, get_positions_adjacentes

# Imports directs du module competences
from competences import (
    est_competence_active, utiliser_competence_active, comp_portee,
    comp_attaque, cooldowns, comp_cib_allie,
    comp_cib_vide, com_cib_ennemi
)

# Constantes et paramètres
MODE_PRINT = True  # Activer/désactiver les impressions de debug
MIN_SCORE = 0  # Score minimum pour une action valide

SC_DMG = 20  # Score de base pour un point d'attaque
SC_PV = 20           # Score par point de vie
SC_PM = 8           # Score par point de mouvement
SC_BOU = 15  # Valeur fixe du bouclier
SC_PORT = 4  # Score par point de portée
SC_ATT = 20  # Score de base pour une attaque (nombre d'attaques)
SC_SOIN = 50  # Score par point de vie soigné

SC_ACTIF = 2000 # Score de base pour une action de compétence active
SC_PASSIF = 500  # Score de base pour une action passive

# ===============================
# STRUCTURES DE DONNÉES
# ===============================


@dataclass
class MovementAction:
    """Action de déplacement vers une nouvelle position"""
    unite: 'Unite'
    nouvelle_position: Tuple[int, int]

    def __str__(self):
        return f"Move {self.unite.get_nom()} to {self.nouvelle_position}"


@dataclass
class AttackAction:
    """Action d'attaque contre une cible"""
    unite: 'Unite'
    cible: 'Unite'

    def __str__(self):
        return f"{self.unite.get_nom()} attacks {self.cible.get_nom()}"


@dataclass
class ActiveSkillAction:
    """Action de compétence active"""
    unite: 'Unite'
    nom_competence: str
    cible_ou_position: Union['Unite', Tuple[int, int], None]

    def __str__(self):
        if isinstance(self.cible_ou_position, tuple):
            return f"{self.unite.get_nom()} uses {self.nom_competence} on position {self.cible_ou_position}"
        elif self.cible_ou_position is None:
            return f"{self.unite.get_nom()} uses {self.nom_competence}"
        else:
            return f"{self.unite.get_nom()} uses {self.nom_competence} on {self.cible_ou_position.get_nom()}"

Action = Union[MovementAction, AttackAction, ActiveSkillAction]


def calculer_bonus_force_relative(unite, ennemi_adjacent) -> float:
    """Calcule le bonus/malus basé sur la force relative entre notre unité et un ennemi adjacent"""
    force_unite = sc_stat(unite)
    force_ennemi = sc_stat(ennemi_adjacent)

    # Éviter la division par zéro
    if force_ennemi == 0:
        return 15.0  # Bonus maximum si l'ennemi est très faible

    ratio = force_unite / force_ennemi

    # Système de bonus/malus basé sur le ratio de force
    if ratio >= 1.5:
        # Notre unité est beaucoup plus forte (150%+) - TRÈS ENCOURAGÉ
        return 15.0
    elif ratio >= 1.2:
        # Notre unité est moyennement plus forte (120-149%) - BIEN ENCOURAGÉ
        return 10.0
    elif ratio >= 0.8:
        # Forces similaires (80-119%) - ENCOURAGEMENT MODÉRÉ
        return 5.0
    elif ratio >= 0.5:
        # Notre unité est plus faible (50-79%) - PEU ENCOURAGÉ
        return 2.0
    else:
        # Notre unité est beaucoup plus faible (<50%) - TRÈS PEU ENCOURAGÉ
        return 0.5

# ===============================
# UTILITAIRES POUR COMPÉTENCES ACTIVES
# ===============================


def unite_peut_utiliser_competence(unite, nom_competence) -> bool:
    """Vérifie si une unité peut utiliser sa compétence active"""
    # Vérifier que l'unité a cette compétence
    if not unite.has_competence():
        return False

    # Vérifier que c'est une compétence active
    if not est_competence_active(nom_competence):
        return False

    # Vérifier si la compétence nécessite une attaque disponible
    if nom_competence in comp_attaque:
        if unite.get_attaque_restantes() <= 0:
            return False

    # Vérifier le cooldown si applicable
    if unite.get_cooldown_actuel() != 0:
        return False

    return True


def peut_cibler_pour_competence(unite_cible, nom_competence) -> bool:
    """
    Vérifie si une unité peut être ciblée par une compétence spécifique,
    en tenant compte des buffs non-stackables déjà présents.
    """
    if not unite_cible or not unite_cible.is_vivant():
        return False
    # Vérifications spécifiques par compétence pour les buffs non-stackables
    if nom_competence == "bénédiction":
        # Ne peut pas bénir une unité qui a déjà la bénédiction
        if unite_cible.has_buff('ba_benediction'):
            return False

    elif nom_competence == "commandement":
        # Ne peut pas commander une unité qui a déjà le commandement
        if unite_cible.has_buff('ba_commandement'):
            return False

    elif nom_competence == "soin":
        # Ne peut pas soigner une unité en pleine santé
        if unite_cible.get_pv() >= unite_cible.get_pv_max():
            return False

    # D'autres vérifications pourraient être ajoutées ici pour d'autres compétences

    return True


def obtenir_cibles_competence(unite, nom_competence, toutes_unites) -> List[Union['Unite', Tuple[int, int]]]:
    """Retourne toutes les cibles possibles pour une compétence active, en excluant les cibles déjà buffées"""
    cibles = []
    portee_comp = comp_portee.get(nom_competence, -1)
    if portee_comp == -1:
        raise ValueError(f"Portée non définie pour la compétence {nom_competence}")

    # Pour tir précis, ajouter la portée de base de l'unité
    if nom_competence == "tir précis":
        portee_comp += unite.get_portee()

    # Cibles alliées
    if nom_competence in comp_cib_allie:
        allies = [u for u in toutes_unites if u.is_vivant() and u.get_equipe() ==
                  unite.get_equipe()]
        for allie in allies:
            if (hex_distance(unite.get_pos(), allie.get_pos()) <= portee_comp and
                    peut_cibler_pour_competence(allie, nom_competence)):
                cibles.append(allie)

    # Cibles ennemies
    if nom_competence in com_cib_ennemi:
        ennemis = [
            u for u in toutes_unites if u.is_vivant() and u.get_equipe() != unite.get_equipe()]
        for ennemi in ennemis:
            if hex_distance(unite.get_pos(), ennemi.get_pos()) <= portee_comp:
                cibles.append(ennemi)

    # Cases vides (dans un rayon autour de l'unité)
    if nom_competence in comp_cib_vide:
        q_unite, r_unite = unite.get_pos()
        for dq in range(-portee_comp, portee_comp + 1):
            for dr in range(-portee_comp, portee_comp + 1):
                if abs(dq) + abs(dr) + abs(-dq-dr) <= portee_comp * 2:  # Distance hexagonale
                    position = (q_unite + dq, r_unite + dr)

                    # Vérifier que la position est dans les limites du plateau
                    q, r = position
                    if -1 <= q <= 6 and -1 <= r <= 6:  # Ajuster selon votre plateau
                        # Vérifier que la case est vide
                        case_occupee = any(
                            u.get_pos() == position and u.is_vivant() for u in toutes_unites)
                        if not case_occupee and position != unite.get_pos():
                            cibles.append(position)

    return cibles


def evaluer_competence_soin(unite, cible_allie) -> float:
    """Évalue l'intérêt d'utiliser la compétence soin sur un allié"""
    if cible_allie.get_equipe() != unite.get_equipe():
        return 0.0

    # Plus l'allié est blessé, plus le soin a de la valeur
    pv_manquants = cible_allie.get_pv_max() - cible_allie.get_pv()
    if pv_manquants <= 0:
        return 0.0  # Allié déjà pleine santé

    # Base : valeur proportionnelle aux PV manquants
    score = min(3, pv_manquants) * SC_SOIN

    # Bonus si l'allié est important (stats élevées)
    force_allie = sc_stat(cible_allie)
    score += force_allie * 0.02  # 2% de la force comme bonus

    # Bonus si l'allié est en danger critique
    if cible_allie.get_pv() <= 10:
        score += 30  # Bonus de sauvetage

    return score + SC_ACTIF


def evaluer_competence_benediction(unite, cible_allie) -> float:
    """Évalue l'intérêt d'utiliser la compétence bénédiction sur un allié"""
    if cible_allie.get_equipe() != unite.get_equipe():
        return 0.0

    # Éviter de bénir plusieurs fois la même unité
    if cible_allie.has_buff('ba_benediction'):
        return 0.0

    # Plus l'allié est fort, plus la bénédiction a de la valeur
    force_allie = sc_stat(cible_allie)

    # Bonus basé sur les stats offensives (attaque et portée)
    # +2 dmg vaut plus sur une unité qui frappe fort
    bonus_attaque = cible_allie.get_attaque_totale() * 5
    bonus_bouclier = 15  # Valeur fixe du bouclier

    # Bonus si l'allié a encore des attaques disponibles
    if cible_allie.get_attaque_restantes() > 0:
        bonus_attaque *= 2  # Double valeur si peut encore attaquer

    return bonus_attaque + bonus_bouclier + force_allie * 0.01 + SC_ACTIF


def evaluer_competence_commandement(unite, cible_allie) -> float:
    """Évalue l'intérêt d'utiliser la compétence commandement sur un allié"""
    if cible_allie.get_equipe() != unite.get_equipe():
        return 0.0

    # Éviter de commander plusieurs fois la même unité
    if hasattr(cible_allie, 'ba_commandement'):
        return 0.0

    # Commandement donne +attaque du roi et +1 attaque supplémentaire
    attaque_roi = unite.get_attaque_totale()

    # Plus l'allié est offensif, plus le commandement a de la valeur
    score = attaque_roi * 8  # Valeur du bonus d'attaque
    score += 25  # Valeur de l'attaque supplémentaire

    # Bonus si l'allié a une bonne portée (peut toucher plus d'ennemis)
    if cible_allie.get_portee():
        score += cible_allie.get_portee() * 5

    # Bonus si l'allié est en position d'attaquer
    if cible_allie.get_attaque_restantes() and cible_allie.get_attaque_restantes() > 0:
        score *= 1.5  # 50% de bonus si peut déjà attaquer

    return score


def evaluer_competence_tir_precis(unite, cible_ennemi, toutes_unites) -> float:
    """Évalue l'intérêt d'utiliser tir précis sur un ennemi"""
    if cible_ennemi.get_equipe() or cible_ennemi.get_equipe() == unite.get_equipe():
        return 0.0

    # Score de base similaire à une attaque normale mais avec bonus dégâts
    score_attaque_base = sc_attaque(unite, cible_ennemi, toutes_unites)

    # Tir précis fait 1.5x dégâts, donc 50% de bonus
    bonus_degats = score_attaque_base * 0.5

    # Bonus pour la portée étendue (peut toucher des cibles normalement hors de portée)
    distance = hex_distance(unite.get_pos(), cible_ennemi.get_pos())
    portee_normale = getattr(unite, 'portee', 1)
    portee_etendue = portee_normale + comp_portee.get('tir précis', 1)

    if distance > portee_etendue:
        bonus_degats += 20  # Bonus pour atteindre une cible éloignée

    return score_attaque_base + bonus_degats


def evaluer_competence_case_vide(unite, nom_competence, position, toutes_unites) -> float:
    """Évalue l'intérêt d'utiliser une compétence sur une case vide"""
    score = 0.0

    if nom_competence == "cristalisation":
        # Évaluer l'intérêt de placer un cristal
        # Bonus pour position défensive (près des alliés)
        allies_proches = [u for u in toutes_unites
                          if u.is_vivant() and u.get_equipe() == unite.get_equipe() and hex_distance(position, u.get_pos()) <= 2]
        score += len(allies_proches) * 10

        # Bonus pour contrôle territorial
        q, r = position
        if 1 <= q <= 5 and 1 <= r <= 5:
            score += 15  # Position centrale

    elif nom_competence == "pluie de flèches":
        # Évaluer l'AOE
        positions_affectees = [position] + get_positions_adjacentes(position)
        ennemis_touches = 0
        allies_touches = 0

        for pos in positions_affectees:
            for u in toutes_unites:
                if u.get_pos() == pos and u.is_vivant():
                    if u.get_equipe() != unite.get_equipe():
                        ennemis_touches += 1
                        score += sc_stat(u) * 0.1  # 10% de la force ennemie
                    else:
                        allies_touches += 1
                        score -= sc_stat(u) * 0.15  # Malus pour friendly fire

        # Bonus pour multi-hit
        if ennemis_touches >= 2:
            score += 30

        # Malus rédhibitoire si trop d'alliés touchés
        if allies_touches >= ennemis_touches and allies_touches > 0:
            score = 0

    elif nom_competence == "monture libéré":
        # Évaluer l'intérêt de la transformation + placement de cheval
        score_position = sc_case_base(unite, position, toutes_unites)
        score += score_position

        # Bonus pour créer une unité supplémentaire (cheval)
        score += 40

    return score

# ===============================
# FONCTIONS DE DEBUG
# ===============================


def debug_afficher_scores_cases(unite, toutes_unites, q_range, r_range, avec_influence=True):
    """Affiche les scores de toutes les cases du plateau pour une unité donnée"""
    type_score = "avec influence" if avec_influence else "score de base"
    print(
        f"\n=== SCORES DES CASES ({type_score}) pour {unite.get_nom()} (équipe {unite.get_equipe()}) ===")

    # Calculer les scores pour toutes les cases du plateau
    scores_plateau = {}

    for q in q_range:
        for r in r_range:
            position = (q, r)
            # Vérifier que la case n'est pas occupée
            case_occupee = any(
                u.pos == position and u.vivant for u in toutes_unites)
            if not case_occupee:
                if avec_influence:
                    score = sc_case(unite, position, toutes_unites)
                else:
                    score = sc_case_base(unite, position, toutes_unites)
                scores_plateau[position] = score

    # Trier par score décroissant
    cases_triees = sorted(scores_plateau.items(),
                          key=lambda x: x[1], reverse=True)

    # Afficher les meilleures cases
    print("Top 10 des meilleures cases:")
    for i, ((q, r), score) in enumerate(cases_triees[:10]):
        print(f"  {i+1}. Case ({q}, {r}): {score:.1f} points")

    # Afficher les pires cases
    if len(cases_triees) > 10:
        print("\nTop 5 des pires cases:")
        for i, ((q, r), score) in enumerate(cases_triees[-5:]):
            print(f"  {i+1}. Case ({q}, {r}): {score:.1f} points")

    print("=" * 50)

# ===============================
# FONCTIONS DE SCORING
# ===============================


def sc_stat(unite) -> float:
    """Score basé sur les statistiques actuelles de l'unité"""
    score = 0.0

    # Facteurs offensifs
    score += unite.get_attaque_totale() * SC_DMG  # score pour les dégâts
    score += unite.get_portee() * SC_PORT  # score pour la portée
    score += max(unite.get_attaque_restantes(),
                 unite.get_attaque_max()) * SC_ATT  # score pour les attaques

    # Facteurs défensifs
    score += unite.get_pv() * SC_PV  # score pour les PV
    score += unite.get_bouclier() * SC_BOU  # score pour le bouclier

    # Facteurs de mobilité
    score += unite.get_pm() * SC_PM  # score pour les PM

    # Facteurs de compétences
    score_competences = sc_comp(unite)
    score += score_competences

    return score


def sc_comp(unite) -> float:
    """Score basé sur les compétences de l'unité """
    # Pour l'instant, retourne 0 car on ne gère pas les compétences
    if unite.get_competence() == "explosion sacrée":
        return unite.get_pv() * SC_DMG  # Puissant en fonction des pv actuels
    return 0.0


def sc_position_competence(unite, position: Tuple[int, int], toutes_unites) -> float:
    """
    Évalue l'intérêt d'une position en fonction des compétences spécifiques de l'unité.
    Chaque unité privilégie les positions qui maximisent l'efficacité de ses compétences.
    """
    score = 0.0

    if not unite.get_competence():
        return score  # Pas de compétence active

    nom_competence = unite.get_competence()

    if not est_competence_active(nom_competence):
        return score  # Pas une compétence active

    # Calculer la portée de la compétence depuis cette position
    portee_comp = comp_portee.get(nom_competence, 1)
    if nom_competence == "tir précis":
        portee_comp += getattr(unite, 'portee', 1)

    # Évaluer les cibles accessibles depuis cette position
    if nom_competence == "soin":
        # Pour le soin : privilégier les positions qui permettent de soigner des alliés blessés
        allies = [u for u in toutes_unites if u.is_vivant() and u.get_equipe() ==
                  unite.get_equipe()]
        for allie in allies:
            if hex_distance(position, allie.get_pos()) <= portee_comp:
                pv_manquants = allie.get_pv_max() - allie.get_pv()
                if pv_manquants > 0:
                    # Score basé sur les PV manquants et l'importance de l'allié
                    # 25 points par PV manquant (max 125)
                    score_soin = min(5, pv_manquants) * 25
                    # 5% de la force de l'allié
                    score_soin += sc_stat(allie) * 0.05

                    # Bonus si l'allié est en danger critique
                    if allie.get_pv() <= 10:
                        score_soin += 50

                    score += score_soin

    elif nom_competence == "bénédiction":
        # Pour la bénédiction : privilégier les positions près d'alliés offensifs
        allies = [u for u in toutes_unites if u.is_vivant() and u.get_equipe() ==
                  unite.get_equipe() and u != unite]
        for allie in allies:
            if hex_distance(position, allie.get_pos()) <= portee_comp:
                # Éviter de bénir une unité déjà bénie
                if not hasattr(allie, 'buff_benediction'):
                    # Score basé sur le potentiel offensif de l'allié
                    score_benediction = allie.get_dmg() * 10  # Valoriser les unités qui frappent fort
                    if hasattr(allie, 'portee'):
                        score_benediction += allie.get_portee() * 8  # Bonus pour la portée
                    if hasattr(allie, 'attaque_restantes') and allie.attaque_restantes > 0:
                        score_benediction *= 1.5  # Bonus si peut encore attaquer

                    score += score_benediction

    elif nom_competence == "commandement":
        # Pour le commandement : privilégier les positions près d'alliés avec bon potentiel d'attaque
        allies = [u for u in toutes_unites if u.is_vivant() and u.get_equipe() ==
                  unite.get_equipe() and u != unite]
        for allie in allies:
            if hex_distance(position, allie.get_pos()) <= portee_comp:
                # Éviter de commander une unité déjà commandée
                if not hasattr(allie, 'ba_commandement'):
                    # Score basé sur le potentiel de dégâts de l'allié
                    score_cmd = unite.get_attaque_totale() * 15  # Valeur du bonus d'attaque accordé
                    score_cmd += 30  # Valeur de l'attaque supplémentaire

                    # Bonus pour les unités avec bonne portée
                    score_cmd += allie.get_portee() * 8

                    # Bonus si l'allié peut agir
                    if allie.get_attaque_restantes() > 0:
                        score_cmd *= 1.3

                    score += score_cmd

    elif nom_competence == "tir précis":
        # Pour tir précis : privilégier les positions qui permettent d'atteindre des ennemis prioritaires
        ennemis = [
            u for u in toutes_unites if u.is_vivant() and u.get_equipe() != unite.get_equipe()]
        for ennemi in ennemis:
            if hex_distance(position, ennemi.get_pos()) <= portee_comp:
                # Score similaire à sc_attaque mais avec bonus pour portée étendue
                # 80% du score d'attaque normal
                score_tir = sc_attaque(unite, ennemi, toutes_unites) * 0.8

                # Bonus spécial si cette position permet d'atteindre un ennemi hors portée normale
                portee_normale = unite.get_portee()
                if hex_distance(position, ennemi.get_pos()) > portee_normale:
                    score_tir += 25  # Bonus pour atteindre une cible éloignée

                score += score_tir

    elif nom_competence in ["cristalisation", "pluie de flèches", "monture libéré"]: # TODO: ne pas utiliser cette liste, utiliser une référence
        # Pour les compétences sur cases vides : privilégier les positions avec bonnes options de ciblage
        cases_ciblables = 0
        positions_interessantes = 0

        # Compter les cases vides ciblables depuis cette position
        q_pos, r_pos = position
        for dq in range(-portee_comp, portee_comp + 1):
            for dr in range(-portee_comp, portee_comp + 1):
                if abs(dq) + abs(dr) + abs(-dq-dr) <= portee_comp * 2:
                    pos_cible = (q_pos + dq, r_pos + dr)
                    q, r = pos_cible

                    if -1 <= q <= 6 and -1 <= r <= 6:  # Dans les limites
                        case_occupee = any(
                            u.get_pos() == pos_cible and u.is_vivant() for u in toutes_unites)
                        if not case_occupee and pos_cible != position:
                            cases_ciblables += 1

                            # Pour pluie de flèches, evaluer l'intérêt tactique de cette case
                            if nom_competence == "pluie de flèches":
                                # Compter les ennemis qui seraient touchés
                                positions_aoe = [pos_cible] + \
                                    get_positions_adjacentes(pos_cible)
                                ennemis_touches = sum(1 for pos in positions_aoe
                                                      for u in toutes_unites
                                                      if u.get_pos() == pos and u.is_vivant() and u.get_equipe() != unite.get_equipe())
                                if ennemis_touches >= 1:
                                    positions_interessantes += ennemis_touches * 10

        # Score basé sur la flexibilité de ciblage
        score += cases_ciblables * 2  # 2 points par case ciblable
        # Bonus pour les positions tactiquement intéressantes
        score += positions_interessantes

    return score


def sc_case_base(unite, position: Tuple[int, int], toutes_unites) -> float:
    """Score de base d'une position pour une unité donnée (sans influence adjacente)"""
    score = 0.0

    # Séparer alliés et ennemis
    allies = [u for u in toutes_unites if u.is_vivant() and u.get_equipe() ==
              unite.get_equipe() and u != unite]
    ennemis = [u for u in toutes_unites if u.is_vivant() and u.get_equipe() != unite.get_equipe()]

    # 1. Proximité des alliés (bonus modéré)
    allies_adjacents = [u for u in allies if est_adjacent(position, u.get_pos())]
    score += len(allies_adjacents) * 5  # 5 points par allié adjacent

    # Bonus pour être près des alliés sans être collé (distance 2)
    allies_proches = [u for u in allies if 1 <
                      hex_distance(position, u.get_pos()) <= 2]
    score += len(allies_proches) * 3  # 3 points par allié proche

    # 2. Analyse des ennemis adjacents basée sur la force relative
    ennemis_adjacents = [u for u in ennemis if est_adjacent(position, u.get_pos())]
    # bonus/malus selon la force relative des ennemis adjacents
    for ennemi in ennemis_adjacents:
        bonus_force = calculer_bonus_force_relative(unite, ennemi)
        score += bonus_force


    # 3. Contrôle territorial (bonus pour positions centrales)
    # Bonus pour être au centre du plateau (positions entre 2-4 en q et r)
    q, r = position
    if 1 <= q <= 5 and 1 <= r <= 5:
        score += 30  # Bonus pour position centrale

    # 4. Position défensive (éviter les bords si possible)
    if q == -1 or q == 6 or r == -1 or r == 6:
        score -= 20  # Malus pour position de bord

    # 5. NOUVEAU: Score spécialisé basé sur les compétences de l'unité
    score_competence = sc_position_competence(unite, position, toutes_unites)
    score += score_competence * 1.2  # Augmenter l'importance des compétences

    return score


def sc_case(unite, position: Tuple[int, int], toutes_unites) -> float:
    """Score basé sur l'intérêt d'une position pour une unité donnée (avec influence adjacente)"""
    # Score de base de cette position
    score_base = sc_case_base(unite, position, toutes_unites)

    # Influence des cases adjacentes (20% de leur score de base)
    influence_adjacente = 0.0
    positions_adjacentes = get_positions_adjacentes(position)

    for pos_adj in positions_adjacentes:
        # Vérifier que la case adjacente n'est pas occupée par une unité
        case_occupee = any(
            u.get_pos() == pos_adj and u.is_vivant() for u in toutes_unites)
        if not case_occupee:
            # Calculer le score de base de la case adjacente et en prendre 20%
            score_adj = sc_case_base(unite, pos_adj, toutes_unites)
            influence_adjacente += score_adj * 0.2

    return score_base + influence_adjacente


def sc_attaque(unite, cible, toutes_unites) -> float:
    """Score pour attaquer une cible donnée"""
    score = 0.0

    # 1. Facilité de kill (priorité aux ennemis faibles)
    pv_ratio = cible.get_pv() / cible.get_pv_max() if cible.get_pv_max() > 0 else 0
    # 0-50 points (plus de points si faible) - AUGMENTÉ
    score += (1 - pv_ratio) * 50

    # Bonus spécial si on peut tuer d'un coup
    if cible.get_pv() <= unite.get_attaque_totale():
        score += 100  # Très gros bonus pour un kill garanti - DOUBLÉ

    # 2. Score de l'unité ennemie (utilise sc_stat inversé)
    score_ennemi = sc_stat(cible)
    score += score_ennemi * 0.5  # 50% du score ennemi en bonus - AUGMENTÉ

    # 3. Menace immédiate (priorité aux ennemis qui menacent nos alliés)
    allies = [u for u in toutes_unites if u.is_vivant() and u.get_equipe() ==
              unite.get_equipe() and u != unite]
    allies_menaces = [a for a in allies
                      if est_a_portee(cible.get_pos(), a.get_pos(), getattr(cible, 'portee', 1))]
    score += len(allies_menaces) * 25  # 25 points par allié menacé - AUGMENTÉ

    # 4. Difficulté d'accès (malus selon la distance)
    distance = hex_distance(unite.get_pos(), cible.get_pos())
    portee_unite = unite.get_portee()

    if distance <= portee_unite:
        # Cible déjà à portée = pas de malus
        pass
    else:
        # Malus selon la distance supplémentaire nécessaire
        distance_supplementaire = distance - portee_unite
        score -= distance_supplementaire * 5  # 5 points de malus par case

    return score

# ===============================
# GÉNÉRATION D'ACTIONS
# ===============================


def generer_actions_unite(unite, toutes_unites) -> List[Action]:
    """
    Génère toutes les actions possibles pour une unité, sans ordre de priorité.
    L'IA choisira la meilleure action parmi toutes les possibilités, 
    qu'il s'agisse d'un mouvement, d'une attaque, ou d'une compétence active.
    """
    actions = []

    # Actions de mouvement - Génère les mouvements vers des positions stratégiques
    if unite.get_pm() > 0:
        cases_accessibles = unite.cases_accessibles(toutes_unites)
        cases_interessantes = filtrer_cases_par_score(
            unite, cases_accessibles, toutes_unites)

        for position, cout in cases_interessantes:
            if cout <= unite.get_pm() and position != unite.get_pos():
                # Vérifier que la nouvelle position est strictement meilleure
                score_actuel = sc_case(unite, unite.get_pos(), toutes_unites)
                score_nouveau = sc_case(unite, position, toutes_unites)
                if score_nouveau > score_actuel:
                    actions.append(MovementAction(unite, position))

    # Actions d'attaque normale - Génère les attaques contre tous les ennemis à portée
    if unite.get_attaque_restantes() > 0:
        ennemis = [
            u for u in toutes_unites if u.is_vivant() and u.get_equipe() != unite.get_equipe()]
        portee = getattr(unite, 'portee', 1)

        for ennemi in ennemis:
            if est_a_portee(unite.get_pos(), ennemi.get_pos(), portee):
                actions.append(AttackAction(unite, ennemi))

    # Actions de compétence active - Génère les actions de compétences sur toutes les cibles valides
    if unite.get_competence():
        nom_competence = unite.get_competence()

        if unite_peut_utiliser_competence(unite, nom_competence):
            cibles_possibles = obtenir_cibles_competence(
                unite, nom_competence, toutes_unites)
            for cible in cibles_possibles:
                if nom_competence == "bénédiction":
                    print("oui je peut utiliser bénédiction")
                actions.append(ActiveSkillAction(unite, nom_competence, cible))

    if MODE_PRINT:
        for action in actions:
            print(f"Action générée pour {unite.get_nom()}: {action}")

    return actions


def filtrer_cases_par_score(unite, cases_accessibles: dict, toutes_unites):
    """Filtre les cases accessibles pour ne garder que les plus intéressantes"""
    if not cases_accessibles:
        return []

    # Calculer le score de chaque case
    scores_cases = []
    for position, cout in cases_accessibles.items():
        score = sc_case(unite, position, toutes_unites)
        scores_cases.append((position, cout, score))

    # Trier par score décroissant
    scores_cases.sort(key=lambda x: x[2], reverse=True)

    # Garder au maximum les 5 meilleures cases ou 20% des cases disponibles
    nb_cases_max = max(3, min(5, len(scores_cases) // 5))
    meilleures_cases = scores_cases[:nb_cases_max]

    # Retourner sous format (position, cout)
    return [(pos, cout) for pos, cout, score in meilleures_cases]

# ===============================
# ÉVALUATION D'ACTIONS
# ===============================


def evaluer_action_complete(action: Action, toutes_unites) -> float:
    """Évalue le score complet d'une action (méthode prédictive)"""
    # Pondération agressive : favoriser les compétences/attaques
    w1, w2, w3 = 4.0, 0.8, 1.5  # comp:4, case:0.8, stat:1.5

    unite = action.unite

    if isinstance(action, MovementAction):
        # Pour un mouvement, évaluer la nouvelle position
        score_comp = sc_comp(unite)
        score_case = sc_case(unite, action.nouvelle_position, toutes_unites)
        score_stat = sc_stat(unite)

    elif isinstance(action, AttackAction):
        # Pour une attaque, ajouter le score d'attaque au score de compétence
        score_comp = sc_comp(unite) + sc_attaque(unite,
                                                 action.cible, toutes_unites)
        # Position actuelle
        score_case = sc_case(unite, unite.get_pos(), toutes_unites)
        score_stat = sc_stat(unite)

    elif isinstance(action, ActiveSkillAction):
        # Évaluation des compétences actives
        nom_comp = action.nom_competence
        cible = action.cible_ou_position

        score_comp = sc_comp(unite)  # Score de base de l'unité
        # Position actuelle
        score_case = sc_case(unite, unite.get_pos(), toutes_unites)
        score_stat = sc_stat(unite)

        # Évaluer la compétence spécifique
        score_competence = 0.0

        if isinstance(cible, tuple):
            # Cible = position (case vide)
            score_competence = evaluer_competence_case_vide(
                unite, nom_comp, cible, toutes_unites)
        elif cible is not None:
            # Cible = unité
            if nom_comp == "soin":
                score_competence = evaluer_competence_soin(unite, cible)
            elif nom_comp == "bénédiction":
                score_competence = evaluer_competence_benediction(unite, cible)
            elif nom_comp == "commandement":
                score_competence = evaluer_competence_commandement(
                    unite, cible)
            elif nom_comp == "tir précis":
                score_competence = evaluer_competence_tir_precis(
                    unite, cible, toutes_unites)

        # Ajouter le score de la compétence au score total
        score_comp += score_competence
    else:
        return 0.0

    score_final = w1 * score_comp + w2 * score_case + w3 * score_stat
    return score_final

# ===============================
# MOTEUR IA PRINCIPAL
# ===============================


def tour_ia(toutes_unites: List['Unite']) -> bool:
    """
    Exécute un tour complet de l'IA avec optimisation globale
    L'IA choisit toujours la meilleure action possible parmi toutes les unités,
    permettant les actions multiples (plusieurs mouvements, attaques, compétences)
    Retourne True si au moins une action a été effectuée, False sinon
    """
    action_effectuee = False

    while True:
        # 1. Générer toutes les actions possibles pour toutes les unités ennemies
        # Toutes les unités non-joueur
        unites_ennemies = [
            u for u in toutes_unites if u.vivant and u.equipe != 1]

        if not unites_ennemies:
            break  # Plus d'unités ennemies

        actions_possibles = []
        for unite in unites_ennemies:
            # Une unité peut agir si elle a des ressources disponibles (PM, attaques, compétences)
            peut_agir = False

            # Vérifier les mouvements disponibles
            if hasattr(unite, 'pm') and unite.get_pm() > 0:
                peut_agir = True

            # Vérifier les attaques disponibles
            if hasattr(unite, 'attaque_restantes') and unite.get_attaque_restantes() > 0:
                peut_agir = True

            # Vérifier les compétences actives disponibles
            if hasattr(unite, 'comp') and unite.get_competence():
                if unite_peut_utiliser_competence(unite, unite.get_competence()):
                    peut_agir = True

            # Générer toutes les actions possibles pour cette unité
            if peut_agir:
                actions_unite = generer_actions_unite(unite, toutes_unites)
                actions_possibles.extend(actions_unite)

        if not actions_possibles:
            break  # Aucune action possible pour aucune unité

        # 2. Scorer chaque action et choisir la meilleure globalement
        actions_scorees = []
        for action in actions_possibles:
            score = evaluer_action_complete(action, toutes_unites)
            # Seuil agressif : accepter même les actions avec score légèrement négatif
            if score > -20:
                actions_scorees.append((action, score))

        # 3. Si aucune action valide, arrêter le tour
        if not actions_scorees:
            break

        # 4. Choisir et exécuter la meilleure action globale (peu importe le type ou l'unité)
        meilleure_action, meilleur_score = max(
            actions_scorees, key=lambda x: x[1])

        if MODE_PRINT:
            print(f"IA: {meilleure_action} (score: {meilleur_score:.1f})")

        # Exécuter l'action choisie
        if isinstance(meilleure_action, MovementAction):
            executer_mouvement(meilleure_action)
        elif isinstance(meilleure_action, AttackAction):
            executer_attaque(meilleure_action, toutes_unites)
        elif isinstance(meilleure_action, ActiveSkillAction):
            executer_competence_active(meilleure_action, toutes_unites)

        action_effectuee = True

        # 5. Continuer la boucle pour réévaluer toutes les actions possibles
        # Cela permet les actions multiples : mouvements successifs, attaques multiples, etc.

    return action_effectuee

# ===============================
# EXÉCUTION D'ACTIONS
# ===============================


def executer_mouvement(action: MovementAction):
    """Exécute une action de mouvement"""
    unite = action.unite
    nouvelle_pos = action.nouvelle_position

    # Calculer le coût du mouvement
    cases_accessibles = unite.cases_accessibles(
        [])
    cout = cases_accessibles.get(nouvelle_pos, 0)

    # Déplacer l'unité
    unite.set_pos(nouvelle_pos)
    if hasattr(unite, 'pm'):
        unite.set_pm(max(0, unite.get_pm() - cout))


def executer_attaque(action: AttackAction, toutes_unites: List['Unite']):
    """Exécute une action d'attaque"""
    unite = action.unite
    cible = action.cible

    # Utiliser la méthode d'attaque existante de l'unité
    unite.attaquer(cible, toutes_unites)


def executer_competence_active(action: ActiveSkillAction, toutes_unites: List['Unite']):
    """Exécute une action de compétence active"""
    unite = action.unite
    nom_competence = action.nom_competence
    cible = action.cible_ou_position

    # Utiliser la fonction du module competences
    succes = utiliser_competence_active(
        unite, nom_competence, cible, toutes_unites)

    # Si la compétence nécessite une attaque, la consommer
    if nom_competence in comp_attaque and succes:
        if hasattr(unite, 'attaque_restantes'):
            unite.set_attaque_restantes(max(0, unite.get_attaque_restantes() - 1))

    # Appliquer le cooldown si applicable
    if nom_competence in cooldowns:
        setattr(unite, f'cooldown_{nom_competence}', cooldowns[nom_competence])

    return succes

# ===============================
# INTERFACE AVEC LE JEU EXISTANT
# ===============================


def ia_tactique_avancee(unite, toutes_unites):
    """
    Cette fonction sera appelée pour chaque unité individuellement par le système existant
    """
    # Utiliser notre nouveau système pour une unité spécifique
    actions = generer_actions_unite(unite, toutes_unites)
    if not actions:
        return None

    # Scorer et choisir la meilleure action
    actions_scorees = [(action, evaluer_action_complete(action, toutes_unites))
                       for action in actions]
    actions_positives = [(action, score)
                         for action, score in actions_scorees if score > 0]

    if not actions_positives:
        return None

    meilleure_action, score = max(actions_positives, key=lambda x: x[1])

    if MODE_PRINT:
        print(f"IA: {meilleure_action} (score: {score:.1f})")

    # Exécuter l'action
    if isinstance(meilleure_action, MovementAction):
        executer_mouvement(meilleure_action)
        return "movement"
    elif isinstance(meilleure_action, AttackAction):
        executer_attaque(meilleure_action, toutes_unites)
        return "attack"
    elif isinstance(meilleure_action, ActiveSkillAction):
        executer_competence_active(meilleure_action, toutes_unites)
        return "skill"

    return None
