# IA V2 - Architecture basée sur le scoring d'actions
# Option B: Calcul prédictif sans modification d'état

from typing import List, Tuple, Union, Optional
from dataclasses import dataclass
from unites import Unite
import math

# ===============================
# STRUCTURES DE DONNÉES
# ===============================

@dataclass
class MovementAction:
    """Action de déplacement vers une nouvelle position"""
    unite: 'Unite'
    nouvelle_position: Tuple[int, int]
    
    def __str__(self):
        return f"Move {self.unite.nom} to {self.nouvelle_position}"

@dataclass
class AttackAction:
    """Action d'attaque contre une cible"""
    unite: 'Unite'
    cible: 'Unite'
    
    def __str__(self):
        return f"{self.unite.nom} attacks {self.cible.nom}"

@dataclass
class ActiveSkillAction:
    """Action de compétence active (désactivée pour l'instant)"""
    unite: 'Unite'
    cible_ou_position: Union['Unite', Tuple[int, int], None]
    
    def __str__(self):
        return f"{self.unite.nom} uses skill on {self.cible_ou_position}"

Action = Union[MovementAction, AttackAction, ActiveSkillAction]

# ===============================
# UTILITAIRES GÉOMÉTRIQUES
# ===============================

def hex_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calcule la distance hexagonale entre deux positions"""
    q1, r1 = pos1
    q2, r2 = pos2
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

def est_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """Vérifie si deux positions sont adjacentes"""
    return hex_distance(pos1, pos2) == 1

def est_a_portee(pos_attaquant: Tuple[int, int], pos_cible: Tuple[int, int], portee: int) -> bool:
    """Vérifie si une cible est à portée d'attaque"""
    return hex_distance(pos_attaquant, pos_cible) <= portee

def get_unites_adjacentes(position: Tuple[int, int], unites: List['Unite']) -> List['Unite']:
    """Retourne les unités adjacentes à une position donnée"""
    return [u for u in unites if u.vivant and est_adjacent(position, u.pos)]

def get_unites_a_portee(position: Tuple[int, int], unites: List['Unite'], portee: int) -> List['Unite']:
    """Retourne les unités à portée d'une position donnée"""
    return [u for u in unites if u.vivant and est_a_portee(position, u.pos, portee)]

def get_positions_adjacentes(position: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Retourne les 6 positions hexagonales adjacentes à une position donnée"""
    q, r = position
    # Les 6 directions hexagonales
    directions = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1)
    ]
    return [(q + dq, r + dr) for dq, dr in directions]

def evaluer_force_unite(unite) -> float:
    """Évalue la force combattante d'une unité basée sur ses statistiques"""
    force = 0.0
    
    # Facteurs offensifs
    force += unite.dmg * 10  # Dégâts sont très importants
    if hasattr(unite, 'portee'):
        force += unite.portee * 8  # Portée donne un avantage tactique
    if hasattr(unite, 'attaque_restantes'):
        force += unite.attaque_restantes * 12  # Capacité d'attaque restante
    
    # Facteurs défensifs
    force += unite.pv * 3  # Points de vie actuels
    if hasattr(unite, 'bouclier'):
        force += unite.bouclier * 5  # Bouclier vaut plus que les PV
    
    # Facteurs de mobilité
    if hasattr(unite, 'pm'):
        force += unite.pm * 2  # Mobilité a un impact modéré
    
    # NOUVEAU: Facteurs liés aux compétences
    score_competences = sc_comp(unite)
    force += score_competences * 0.5  # 50% du score de compétences ajouté à la force (réduit pour équilibrage)
    
    return force

def calculer_bonus_force_relative(unite, ennemi_adjacent) -> float:
    """Calcule le bonus/malus basé sur la force relative entre notre unité et un ennemi adjacent"""
    force_unite = evaluer_force_unite(unite)
    force_ennemi = evaluer_force_unite(ennemi_adjacent)
    
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
# FONCTIONS DE DEBUG
# ===============================

def debug_afficher_scores_cases(unite, toutes_unites, q_range, r_range, avec_influence=True):
    """Affiche les scores de toutes les cases du plateau pour une unité donnée"""
    type_score = "avec influence" if avec_influence else "score de base"
    print(f"\n=== SCORES DES CASES ({type_score}) pour {unite.nom} (équipe {unite.equipe}) ===")
    
    # Calculer les scores pour toutes les cases du plateau
    scores_plateau = {}
    
    for q in q_range:
        for r in r_range:
            position = (q, r)
            # Vérifier que la case n'est pas occupée
            case_occupee = any(u.pos == position and u.vivant for u in toutes_unites)
            if not case_occupee:
                if avec_influence:
                    score = sc_case(unite, position, toutes_unites)
                else:
                    score = sc_case_base(unite, position, toutes_unites)
                scores_plateau[position] = score
    
    # Trier par score décroissant
    cases_triees = sorted(scores_plateau.items(), key=lambda x: x[1], reverse=True)
    
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
    
    # Score basé sur les pv actuels
    score += unite.pv * 3  # 3 points par PV
    
    # Score basé sur les attaques disponibles
    if hasattr(unite, 'attaque_restantes'):
        score += unite.attaque_restantes * 15  # 15 points par attaque dispo
    
    # Score basé sur les points de mouvement
    if hasattr(unite, 'pm'):
        score += unite.pm * 8  # 8 points par PM
    
    # Score basé sur les dégâts
    score += unite.dmg * 5  # 5 points par point de dégât
    
    # Score basé sur le bouclier
    if hasattr(unite, 'bouclier'):
        score += unite.bouclier * 2  # 2 points par point de bouclier
    
    # Score basé sur la portée
    if hasattr(unite, 'portee'):
        score += unite.portee * 4  # 4 points par point de portée
    
    return score

def sc_comp(unite) -> float:
    """Score basé sur les compétences de l'unité (désactivé pour l'instant)"""
    # Pour l'instant, retourne 0 car on ne gère pas les compétences
    if hasattr(unite, 'competences'):
        if unite.competences == "explosion sacrée":
            return unite.get_pv() * 15  # Puissant en fonction des pv actuels
    return 0.0

def sc_case_base(unite, position: Tuple[int, int], toutes_unites) -> float:
    """Score de base d'une position pour une unité donnée (sans influence adjacente)"""
    score = 0.0
    
    # Séparer alliés et ennemis
    allies = [u for u in toutes_unites if u.vivant and u.equipe == unite.equipe and u != unite]
    ennemis = [u for u in toutes_unites if u.vivant and u.equipe != unite.equipe]
    
    # 1. Proximité des alliés (bonus modéré)
    allies_adjacents = [u for u in allies if est_adjacent(position, u.pos)]
    score += len(allies_adjacents) * 5  # 5 points par allié adjacent
    
    # Bonus pour être près des alliés sans être collé (distance 2)
    allies_proches = [u for u in allies if 1 < hex_distance(position, u.pos) <= 2]
    score += len(allies_proches) * 3  # 3 points par allié proche
    
    # 2. Analyse des ennemis adjacents basée sur la force relative
    ennemis_adjacents = [u for u in ennemis if est_adjacent(position, u.pos)]
    
    # Nouveau système : bonus/malus selon la force relative des ennemis adjacents
    for ennemi in ennemis_adjacents:
        bonus_force = calculer_bonus_force_relative(unite, ennemi)
        score += bonus_force  # Ajouter le bonus (positif si favorable, faible si défavorable)
    
    # Malus réduit pour les ennemis à portée mais pas adjacents (comportement existant)
    ennemis_menaçants = [u for u in ennemis 
                        if est_a_portee(u.pos, position, getattr(u, 'portee', 1)) 
                        and not est_adjacent(position, u.pos)]  # Éviter double comptage
    score -= len(ennemis_menaçants) * 1  # Malus de 1 point par ennemi menaçant non-adjacent
    
    # 3. Contrôle territorial (bonus pour positions centrales)
    # Bonus pour être au centre du plateau (positions entre 2-4 en q et r)
    q, r = position
    if 1 <= q <= 5 and 1 <= r <= 5:
        score += 3  # Bonus pour position centrale
    
    # 4. Position défensive (éviter les bords si possible)
    if q == -1 or q == 6 or r == -1 or r == 6:
        score -= 2  # Malus pour position de bord
    
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
        case_occupee = any(u.pos == pos_adj and u.vivant for u in toutes_unites)
        if not case_occupee:
            # Calculer le score de base de la case adjacente et en prendre 20%
            score_adj = sc_case_base(unite, pos_adj, toutes_unites)
            influence_adjacente += score_adj * 0.2
    
    return score_base + influence_adjacente

def sc_attaque(unite, cible, toutes_unites) -> float:
    """Score pour attaquer une cible donnée"""
    score = 0.0
    
    # 1. Facilité de kill (priorité aux ennemis faibles)
    pv_ratio = cible.pv / cible.pv_max if cible.pv_max > 0 else 0
    score += (1 - pv_ratio) * 50  # 0-50 points (plus de points si faible) - AUGMENTÉ
    
    # Bonus spécial si on peut tuer d'un coup
    if cible.pv <= unite.dmg:
        score += 100  # Très gros bonus pour un kill garanti - DOUBLÉ
    
    # 2. Score de l'unité ennemie (utilise sc_stat inversé)
    score_ennemi = sc_stat(cible)
    score += score_ennemi * 0.5  # 50% du score ennemi en bonus - AUGMENTÉ
    
    # 3. Menace immédiate (priorité aux ennemis qui menacent nos alliés)
    allies = [u for u in toutes_unites if u.vivant and u.equipe == unite.equipe and u != unite]
    allies_menaces = [a for a in allies 
                     if est_a_portee(cible.pos, a.pos, getattr(cible, 'portee', 1))]
    score += len(allies_menaces) * 25  # 25 points par allié menacé - AUGMENTÉ
    
    # 4. Difficulté d'accès (malus selon la distance)
    distance = hex_distance(unite.pos, cible.pos)
    portee_unite = getattr(unite, 'portee', 1)
    
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
    """Génère toutes les actions possibles pour une unité"""
    actions = []
    
    # 1. Actions de mouvement (seulement vers cases intéressantes)
    if hasattr(unite, 'pm') and unite.pm > 0:
        cases_accessibles = unite.cases_accessibles(toutes_unites)
        cases_interessantes = filtrer_cases_par_score(unite, cases_accessibles, toutes_unites)
        
        for position, cout in cases_interessantes:
            if cout <= unite.pm and position != unite.pos:
                # Vérifier que la nouvelle position est strictement meilleure
                score_actuel = sc_case(unite, unite.pos, toutes_unites)
                score_nouveau = sc_case(unite, position, toutes_unites)
                if score_nouveau > score_actuel:
                    actions.append(MovementAction(unite, position))
    
    # 2. Actions d'attaque
    if hasattr(unite, 'attaque_restantes') and unite.attaque_restantes > 0:
        ennemis = [u for u in toutes_unites if u.vivant and u.equipe != unite.equipe]
        portee = getattr(unite, 'portee', 1)
        
        for ennemi in ennemis:
            if est_a_portee(unite.pos, ennemi.pos, portee):
                actions.append(AttackAction(unite, ennemi))
    
    # 3. Actions de compétence active (désactivées pour l'instant)
    # TODO: Implémenter plus tard
    
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
    w1, w2, w3 = 4.0, 0.8, 1.5  # comp:2, case:0.8, stat:1
    
    unite = action.unite
    
    if isinstance(action, MovementAction):
        # Pour un mouvement, évaluer la nouvelle position
        score_comp = sc_comp(unite)
        score_case = sc_case(unite, action.nouvelle_position, toutes_unites)
        score_stat = sc_stat(unite)
        
    elif isinstance(action, AttackAction):
        # Pour une attaque, ajouter le score d'attaque au score de compétence
        score_comp = sc_comp(unite) + sc_attaque(unite, action.cible, toutes_unites)
        score_case = sc_case(unite, unite.pos, toutes_unites)  # Position actuelle
        score_stat = sc_stat(unite)
        
    elif isinstance(action, ActiveSkillAction):
        # Compétences désactivées pour l'instant
        return 0.0
        
    else:
        return 0.0
    
    score_final = w1 * score_comp + w2 * score_case + w3 * score_stat
    return score_final

# ===============================
# MOTEUR IA PRINCIPAL
# ===============================

def tour_ia(toutes_unites: List['Unite']) -> bool:
    """
    Exécute un tour complet de l'IA
    Retourne True si au moins une action a été effectuée, False sinon
    """
    action_effectuee = False
    
    while True:
        # 1. Générer toutes les actions possibles pour toutes les unités ennemies
        unites_ennemies = [u for u in toutes_unites if u.vivant and u.equipe == "ennemi"]
        
        if not unites_ennemies:
            break  # Plus d'unités ennemies
        
        actions_possibles = []
        for unite in unites_ennemies:
            # Vérifier que l'unité peut encore agir
            peut_agir = False
            if hasattr(unite, 'attaque_restantes') and unite.attaque_restantes > 0:
                peut_agir = True
            if hasattr(unite, 'pm') and unite.pm > 0:
                peut_agir = True
            
            if peut_agir:
                actions_unite = generer_actions_unite(unite, toutes_unites)
                actions_possibles.extend(actions_unite)
        
        if not actions_possibles:
            break  # Aucune action possible
        
        # 2. Scorer chaque action
        actions_scorees = []
        for action in actions_possibles:
            score = evaluer_action_complete(action, toutes_unites)
            # Seuil plus agressif : accepter même les actions avec score négatif modéré
            if score > -20:  # Seuil agressif au lieu de 0
                actions_scorees.append((action, score))
        
        # 3. Si aucune action positive, arrêter le tour
        if not actions_scorees:
            break
        
        # 4. Exécuter la meilleure action
        meilleure_action, meilleur_score = max(actions_scorees, key=lambda x: x[1])
        
        print(f"IA: {meilleure_action} (score: {meilleur_score:.1f})")
        
        # Exécuter l'action
        if isinstance(meilleure_action, MovementAction):
            executer_mouvement(meilleure_action)
        elif isinstance(meilleure_action, AttackAction):
            executer_attaque(meilleure_action, toutes_unites)
        
        action_effectuee = True
        
        # 5. Continuer avec les autres actions possibles
        # (Le recalcul se fait automatiquement au prochain tour de boucle)
    
    return action_effectuee

# ===============================
# EXÉCUTION D'ACTIONS
# ===============================

def executer_mouvement(action: MovementAction):
    """Exécute une action de mouvement"""
    unite = action.unite
    nouvelle_pos = action.nouvelle_position
    
    # Calculer le coût du mouvement
    cases_accessibles = unite.cases_accessibles([])  # Simplified pour l'exemple
    cout = cases_accessibles.get(nouvelle_pos, 0)
    
    # Déplacer l'unité
    unite.pos = nouvelle_pos
    if hasattr(unite, 'pm'):
        unite.pm = max(0, unite.pm - cout)

def executer_attaque(action: AttackAction, toutes_unites: List['Unite']):
    """Exécute une action d'attaque"""
    unite = action.unite
    cible = action.cible
    
    # Utiliser la méthode d'attaque existante de l'unité
    unite.attaquer(cible, toutes_unites)

# ===============================
# INTERFACE AVEC LE JEU EXISTANT
# ===============================

def ia_tactique_avancee(unite, ennemis, toutes_unites):
    """
    Interface avec l'ancien système d'IA
    Cette fonction sera appelée pour chaque unité individuellement par le système existant
    """
    # Utiliser notre nouveau système pour une unité spécifique
    actions = generer_actions_unite(unite, toutes_unites)
    if not actions:
        return None
    
    # Scorer et choisir la meilleure action
    actions_scorees = [(action, evaluer_action_complete(action, toutes_unites)) 
                      for action in actions]
    actions_positives = [(action, score) for action, score in actions_scorees if score > 0]
    
    if not actions_positives:
        return None
    
    meilleure_action, score = max(actions_positives, key=lambda x: x[1])
    
    print(f"IA: {meilleure_action} (score: {score:.1f})")
    
    # Exécuter l'action
    if isinstance(meilleure_action, MovementAction):
        executer_mouvement(meilleure_action)
        return "movement"
    elif isinstance(meilleure_action, AttackAction):
        executer_attaque(meilleure_action, toutes_unites)
        return "attack"
    
    return None

def ia_nouvelle_version(unite, ennemis, toutes_unites):
    """Alias pour compatibility"""
    return ia_tactique_avancee(unite, ennemis, toutes_unites)

# ===============================
# COMPATIBILITÉ AVEC ANCIEN SYSTÈME
# ===============================

# Fonction d'IA alternative pour tests
def cible_faible(unite, ennemis, unites):
    """IA simple qui cible toujours l'ennemi le plus faible"""
    return ia_tactique_avancee(unite, ennemis, unites)