# --- Helpers cohérents avec le système axial (q, r) ---

def est_adjacent_pos(a, b):
    """Vrai si a et b sont deux hex adjacents (mêmes 6 directions que Unite.est_adjacente)."""
    dq = b[0] - a[0]
    dr = b[1] - a[1]
    return (dq, dr) in {(1,0), (-1,0), (0,1), (0,-1), (1,-1), (-1,1)}

def hex_distance(a, b):
    """Distance hex (axiale) standard."""
    dq = a[0] - b[0]
    dr = a[1] - b[1]
    return (abs(dq) + abs(dr) + abs(dq + dr)) // 2

def est_a_portee_pos(pos1, pos2, portee):
    dq = pos1[0] - pos2[0]
    dr = pos1[1] - pos2[1]
    dist = max(abs(dq), abs(dr), abs((pos1[0]+pos1[1])-(pos2[0]+pos2[1])))
    return dist <= portee

def get_unites_adjacentes(pos, unites):
    """Retourne les unités adjacentes à une position."""
    return [u for u in unites if u.vivant and est_adjacent_pos(pos, u.pos)]

def get_unites_a_portee(pos, unites, portee):
    """Retourne les unités à portée d'une position."""
    return [u for u in unites if u.vivant and est_a_portee_pos(pos, u.pos, portee)]

def evaluer_utilite_competence(unite, competence, cible, tous_unites):
    """Évalue l'utilité d'utiliser une compétence sur une cible (score 0-100)."""
    if not cible or not cible.vivant:
        return 0
    
    score = 0
    
    if competence == "soin":
        if cible.equipe == unite.equipe:  # Allié
            pv_manquants = cible.pv_max - cible.pv
            if pv_manquants > 0:
                # Plus l'allié est blessé, plus c'est urgent
                score = min(pv_manquants * 20, 80)
                # Bonus si l'allié est puissant (tier élevé)
                score += cible.tier * 5
                # Bonus si l'allié est en danger (PV très bas)
                if cible.pv <= 2:
                    score += 30
        return score
    
    elif competence == "bénédiction":
        if cible.equipe == unite.equipe:  # Allié
            # Priorité aux unités offensives
            score = cible.dmg * 10 + cible.tier * 5
            # Bonus si l'allié peut attaquer ce tour
            if cible.attaque_restantes > 0:
                score += 20
            # Bonus si l'allié a des ennemis à portée
            ennemis_a_portee = [u for u in tous_unites 
                              if u.vivant and u.equipe != cible.equipe 
                              and est_a_portee_pos(cible.pos, u.pos, cible.portee)]
            if ennemis_a_portee:
                score += 30
        return score
    
    return 0

def peut_utiliser_competence_active(unite, competence, tous_unites):
    """Vérifie si l'unité peut utiliser sa compétence active."""
    from competences import est_competence_active
    
    if not hasattr(unite, 'comp') or unite.comp != competence:
        return False
    
    if not est_competence_active(competence):
        return False
        
    if unite.attaque_restantes <= 0:
        return False
        
    return True

def trouver_meilleure_cible_competence(unite, competence, tous_unites):
    """Trouve la meilleure cible pour une compétence active."""
    from competences import peut_cibler_allie, peut_cibler_ennemi
    
    cibles_potentielles = []
    
    # Déterminer la portée à utiliser pour cette compétence
    if competence == "soin":
        portee_competence = 99  # Portée illimitée pour le soin
    else:
        portee_competence = unite.portee  # Portée normale pour les autres compétences
    
    # Collecter les cibles possibles
    for cible in tous_unites:
        if not cible.vivant or cible == unite:
            continue
            
        # Vérifier si on peut cibler cette unité
        if cible.equipe == unite.equipe and peut_cibler_allie(competence):
            # C'est un allié et on peut cibler les alliés
            if est_a_portee_pos(unite.pos, cible.pos, portee_competence):
                cibles_potentielles.append(cible)
        elif cible.equipe != unite.equipe and peut_cibler_ennemi(competence):
            # C'est un ennemi et on peut cibler les ennemis
            if est_a_portee_pos(unite.pos, cible.pos, portee_competence):
                cibles_potentielles.append(cible)
    
    if not cibles_potentielles:
        return None
    
    # Évaluer chaque cible et retourner la meilleure
    meilleure_cible = None
    meilleur_score = 0
    
    for cible in cibles_potentielles:
        score = evaluer_utilite_competence(unite, competence, cible, tous_unites)
        if score > meilleur_score:
            meilleur_score = score
            meilleure_cible = cible
    
    return meilleure_cible if meilleur_score > 30 else None  # Seuil minimum d'utilité

def utiliser_competence_immediate(unite, tous_unites):
    """Utilise les compétences qui ne nécessitent pas de cible (comme explosion sacrée)."""
    if not hasattr(unite, 'comp') or unite.attaque_restantes <= 0:
        return False
    
    competence = unite.comp
    
    if competence == "explosion sacrée":
        # Vérifie s'il y a des ennemis adjacents
        ennemis_adjacents = [u for u in tous_unites 
                           if u.vivant and u.equipe != unite.equipe 
                           and est_adjacent_pos(unite.pos, u.pos)]
        
        if ennemis_adjacents:
            # Évalue si c'est rentable
            degats_totaux = sum(min(unite.pv, ennemi.pv) for ennemi in ennemis_adjacents)
            # Se sacrifier vaut le coup si on peut faire beaucoup de dégâts
            if degats_totaux >= unite.pv and len(ennemis_adjacents) >= 2:
                unite.utiliser_competence(None, tous_unites)
                return True
    
    elif competence == "bouclier de la foi":
        # Vérifie s'il y a des alliés adjacents qui peuvent bénéficier du bouclier
        allies_adjacents = [u for u in tous_unites 
                           if u.vivant and u.equipe == unite.equipe 
                           and est_adjacent_pos(unite.pos, u.pos)]
        
        if allies_adjacents:
            # Utilise si au moins un allié n'a pas de bouclier ou est en danger
            for allie in allies_adjacents:
                if (not hasattr(allie, 'bouclier') or allie.bouclier == 0) and allie.pv <= 3:
                    unite.utiliser_competence(None, tous_unites)
                    return True
    
    elif competence == "aura sacrée":
        # Utilise si des alliés adjacents peuvent attaquer
        allies_adjacents = [u for u in tous_unites 
                           if u.vivant and u.equipe == unite.equipe 
                           and est_adjacent_pos(unite.pos, u.pos) 
                           and u.attaque_restantes > 0]
        
        if allies_adjacents:
            unite.utiliser_competence(None, tous_unites)
            return True
    
    elif competence == "nécromancie":
        # Essaie d'invoquer un squelette sur une position stratégique
        directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
        for dq, dr in directions:
            pos_cible = (unite.pos[0] + dq, unite.pos[1] + dr)
            # Vérifie si la position est libre et utile
            if not any(u.pos == pos_cible and u.vivant for u in tous_unites):
                # Position libre, essaie d'invoquer
                unite.utiliser_competence(None, tous_unites)
                return True
    
    elif competence == "invocation":
        # Logique similaire à nécromancie mais plus sélective
        directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
        for dq, dr in directions:
            pos_cible = (unite.pos[0] + dq, unite.pos[1] + dr)
            if not any(u.pos == pos_cible and u.vivant for u in tous_unites):
                unite.utiliser_competence(None, tous_unites)
                return True
    
    return False

# --- IA cible faible avec compétences ---

def cible_faible(unite, ennemis, unites):
    """IA améliorée qui utilise intelligemment les compétences actives."""
    
    action_effectuee = None
    
    # Phase 1: Essayer d'utiliser des compétences immédiates (sans cible)
    if utiliser_competence_immediate(unite, unites):
        action_effectuee = "competence"
    
    # Phase 2: Essayer d'utiliser des compétences actives sur des cibles
    if hasattr(unite, 'comp') and unite.attaque_restantes > 0:
        meilleure_cible = trouver_meilleure_cible_competence(unite, unite.comp, unites)
        if meilleure_cible:
            unite.utiliser_competence(meilleure_cible, unites)
            if action_effectuee is None:
                action_effectuee = "competence"
            else:
                action_effectuee = "competence_multiple"
    
    # Phase 3: Logique d'attaque classique (seulement si on a encore des attaques)
    if unite.attaque_restantes > 0:
        # 0) Filtre
        cibles = [e for e in ennemis if e.vivant]
        if not cibles:
            return action_effectuee
        
        cible = min(cibles, key=lambda x: x.pv)

        # 1) Cases atteignables (inclure la position actuelle)
        accessibles = unite.cases_accessibles(unites)
        accessibles = dict(accessibles)  # copie défensive
        accessibles.setdefault(unite.pos, 0)

        # 2) Peut-on atteindre ET attaquer la cible ce tour-ci ?
        adj_to_target = [pos for pos in accessibles if est_a_portee_pos(pos, cible.pos, unite.portee)]
        if adj_to_target and unite.attaque_restantes > 0:
            # Choix: coût minimal puis (optionnel) distance au centre de la cible (toujours 1 si adjacent)
            best_pos = min(adj_to_target, key=lambda p: (accessibles[p], hex_distance(p, cible.pos)))
            cout = accessibles[best_pos]
            if cout > 0:
                unite.pos = best_pos
                unite.pm -= cout
            # Une seule attaque
            unite.attaquer(cible)
            if action_effectuee is None:
                return "attaque"
            else:
                return "competence_et_attaque"

        # 3) Sinon, opportunisme: une autre cible attaquable depuis une case atteignable (y compris sans bouger)
        meilleure_option = None  # (cout, pv_ennemi, pos, enn)
        meilleur_score = None    # (cout, pv_ennemi) pour la comparaison
        
        for pos, cout in accessibles.items():
            # Si plus de PM que le coût nécessaire
            if cout > unite.pm:
                continue
            for enn in cibles:
                if est_a_portee_pos(pos, enn.pos, unite.portee):
                    score = (cout, enn.pv)  # Seulement les critères de comparaison
                    if (meilleur_score is None) or (score < meilleur_score):
                        meilleur_score = score
                        meilleure_option = (cout, enn.pv, pos, enn)

        if (meilleure_option is not None) and unite.attaque_restantes > 0:
            cout, _, pos, enn = meilleure_option
            if pos != unite.pos:
                unite.pos = pos
                unite.pm -= cout
            unite.attaquer(enn)
            if action_effectuee is None:
                return "attaque"
            else:
                return "competence_et_attaque"

        # 4) Sinon, avancer vers la cible principale (sans attaquer)
        if accessibles and unite.pm > 0:
            # Choisir la case qui réduit le plus la distance hex; tie-breaker sur coût
            best_move = min(accessibles.keys(), key=lambda p: (hex_distance(p, cible.pos), accessibles[p]))
            if best_move != unite.pos and accessibles[best_move] <= unite.pm:
                unite.pos = best_move
                unite.pm -= accessibles[best_move]
                if action_effectuee is None:
                    return "deplacement"
                else:
                    return "competence_et_deplacement"

    return action_effectuee


def ia_tactique_avancee(unite, ennemis, unites):
    """IA avancée avec stratégies tactiques complexes."""
    
    # Phase 1: Analyse de la situation
    allies = [u for u in unites if u.vivant and u.equipe == unite.equipe and u != unite]
    ennemis_vivants = [e for e in ennemis if e.vivant]
    
    if not ennemis_vivants:
        return None
    
    # Phase 2: Compétences de support prioritaires
    if hasattr(unite, 'comp') and unite.attaque_restantes > 0:
        competence = unite.comp
        
        # Soigner un allié critique en priorité
        if competence == "soin":
            allie_critique = None
            for allie in allies:
                if allie.pv <= 2 and est_a_portee_pos(unite.pos, allie.pos, unite.portee):
                    if allie_critique is None or allie.pv < allie_critique.pv:
                        allie_critique = allie
            
            if allie_critique:
                unite.utiliser_competence(allie_critique, unites)
                return "competence_urgente"
        
        # Bénédiction sur l'allié le plus offensif qui peut attaquer
        elif competence == "bénédiction":
            meilleur_allie = None
            meilleur_potentiel = 0
            
            for allie in allies:
                if (est_a_portee_pos(unite.pos, allie.pos, unite.portee) and 
                    allie.attaque_restantes > 0):
                    # Calcule le potentiel offensif
                    ennemis_accessibles = [e for e in ennemis_vivants 
                                         if est_a_portee_pos(allie.pos, e.pos, allie.portee)]
                    potentiel = allie.dmg * len(ennemis_accessibles) + allie.tier * 5
                    
                    if potentiel > meilleur_potentiel:
                        meilleur_potentiel = potentiel
                        meilleur_allie = allie
            
            if meilleur_allie and meilleur_potentiel > 15:
                unite.utiliser_competence(meilleur_allie, unites)
                return "competence_support"
    
    # Phase 3: Utiliser compétences immédiates si pertinent
    if utiliser_competence_immediate(unite, unites):
        return "competence_immediate"
    
    # Phase 4: Stratégie d'attaque adaptative
    return _strategie_attaque_adaptative(unite, ennemis_vivants, unites, allies)


def _strategie_attaque_adaptative(unite, ennemis, unites, allies):
    """Stratégie d'attaque qui s'adapte à la situation tactique."""
    
    # Évaluer les cibles selon plusieurs critères
    meilleures_cibles = []
    
    for ennemi in ennemis:
        score = _evaluer_cible(unite, ennemi, unites, allies)
        if score > 0:
            meilleures_cibles.append((score, ennemi))
    
    if not meilleures_cibles:
        return None
    
    # Trier par score décroissant (utiliser seulement le score)
    meilleures_cibles.sort(key=lambda x: x[0], reverse=True)
    cible_prioritaire = meilleures_cibles[0][1]
    
    # Tenter d'attaquer la cible prioritaire
    accessibles = unite.cases_accessibles(unites)
    accessibles = dict(accessibles)
    accessibles.setdefault(unite.pos, 0)
    
    # Positions d'attaque possibles
    positions_attaque = [pos for pos in accessibles 
                        if est_a_portee_pos(pos, cible_prioritaire.pos, unite.portee)]
    
    if positions_attaque and unite.attaque_restantes > 0:
        # Choisir la meilleure position d'attaque
        meilleure_pos = _choisir_meilleure_position_attaque(
            positions_attaque, accessibles, cible_prioritaire, unites, unite)
        
        cout = accessibles[meilleure_pos]
        if cout <= unite.pm:
            if meilleure_pos != unite.pos:
                unite.pos = meilleure_pos
                unite.pm -= cout
            unite.attaquer(cible_prioritaire)
            return "attaque_tactique"
    
    # Attaque d'opportunité sur n'importe quelle cible
    for _, cible in meilleures_cibles:
        positions_attaque = [pos for pos in accessibles 
                           if est_a_portee_pos(pos, cible.pos, unite.portee)]
        
        if positions_attaque and unite.attaque_restantes > 0:
            meilleure_pos = min(positions_attaque, 
                              key=lambda p: (accessibles[p], hex_distance(p, cible.pos)))
            cout = accessibles[meilleure_pos]
            
            if cout <= unite.pm:
                if meilleure_pos != unite.pos:
                    unite.pos = meilleure_pos
                    unite.pm -= cout
                unite.attaquer(cible)
                return "attaque_opportunite"
    
    # Mouvement tactique
    if unite.pm > 0 and accessibles:
        nouvelle_pos = _choisir_mouvement_tactique(unite, ennemis, allies, accessibles)
        if nouvelle_pos and nouvelle_pos != unite.pos:
            cout = accessibles[nouvelle_pos]
            if cout <= unite.pm:
                unite.pos = nouvelle_pos
                unite.pm -= cout
                return "mouvement_tactique"
    
    return None


def _evaluer_cible(unite, ennemi, unites, allies):
    """Évalue l'intérêt d'attaquer une cible ennemie (score 0-100)."""
    score = 0
    
    # Priorité aux ennemis faibles (faciles à tuer)
    score += max(0, 50 - ennemi.pv * 10)
    
    # Priorité aux ennemis dangereux (haut dégât)
    score += ennemi.dmg * 3
    
    # Bonus pour les ennemis de tier élevé
    score += ennemi.tier * 5
    
    # Malus si l'ennemi est loin
    distance = hex_distance(unite.pos, ennemi.pos)
    score -= distance * 2
    
    # Bonus si l'ennemi menace des alliés
    allies_menaces = [a for a in allies 
                     if est_a_portee_pos(ennemi.pos, a.pos, ennemi.portee)]
    score += len(allies_menaces) * 10
    
    # Bonus si l'ennemi a des compétences dangereuses
    if hasattr(ennemi, 'comp'):
        competences_dangereuses = ["explosion sacrée", "soin", "bénédiction", "invocation"]
        if ennemi.comp in competences_dangereuses:
            score += 15
    
    return max(0, score)


def _choisir_meilleure_position_attaque(positions, accessibles, cible, unites, unite):
    """Choisit la meilleure position pour attaquer une cible."""
    if not positions:
        return unite.pos
    
    meilleure_pos = None
    meilleur_score = float('-inf')
    
    for pos in positions:
        score = 0
        
        # Préférer les positions avec un coût minimal
        score -= accessibles[pos] * 10
        
        # Préférer les positions sûres (loin des ennemis)
        ennemis_adjacents = [u for u in unites 
                           if (u.vivant and u.equipe != unite.equipe and u != cible
                               and est_adjacent_pos(pos, u.pos))]
        score -= len(ennemis_adjacents) * 20
        
        # Préférer les positions près des alliés (soutien)
        allies_adjacents = [u for u in unites 
                          if (u.vivant and u.equipe == unite.equipe and u != unite
                              and est_adjacent_pos(pos, u.pos))]
        score += len(allies_adjacents) * 5
        
        if score > meilleur_score:
            meilleur_score = score
            meilleure_pos = pos
    
    return meilleure_pos or positions[0]


def _choisir_mouvement_tactique(unite, ennemis, allies, accessibles):
    """Choisit un mouvement tactique optimal."""
    if not accessibles:
        return None
    
    meilleure_pos = None
    meilleur_score = float('-inf')
    
    for pos, cout in accessibles.items():
        if cout > unite.pm or pos == unite.pos:
            continue
        
        score = 0
        
        # Se rapprocher de l'ennemi le plus faible
        ennemi_le_plus_faible = min(ennemis, key=lambda e: e.pv)
        distance_ennemi = hex_distance(pos, ennemi_le_plus_faible.pos)
        score -= distance_ennemi * 5
        
        # Éviter d'être adjacent à trop d'ennemis
        ennemis_adjacents = [e for e in ennemis if est_adjacent_pos(pos, e.pos)]
        score -= len(ennemis_adjacents) * 15
        
        # Rester près des alliés si possible
        allies_proches = [a for a in allies if hex_distance(pos, a.pos) <= 2]
        score += len(allies_proches) * 3
        
        # Coût du mouvement
        score -= cout * 2
        
        if score > meilleur_score:
            meilleur_score = score
            meilleure_pos = pos
    
    return meilleure_pos
