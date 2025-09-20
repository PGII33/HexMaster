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
    """Évalue l'utilité d'utiliser une compétence sur une cible (score entier positif)."""
    if not cible or not cible.vivant:
        return 0
    
    score = 0
    
    if competence == "soin":
        if cible.equipe == unite.equipe:  # Allié
            pv_manquants = cible.pv_max - cible.pv
            if pv_manquants > 0:
                # Base score selon les PV manquants
                score = min(pv_manquants * 15, 70)
                
                # Bonus si l'allié est puissant (tier élevé)
                score += cible.tier * 8
                
                # PRIORITÉ ABSOLUE si l'allié est critique (PV très bas)
                if cible.pv <= 2:
                    score += 60  # Score très élevé pour les alliés critiques
                elif cible.pv <= cible.pv_max // 2:  # À moins de 50% PV
                    score += 30  # Score élevé pour les alliés blessés
                
                # Bonus si l'allié a des compétences importantes
                if hasattr(cible, 'comp'):
                    competences_importantes = ["soin", "bénédiction", "commandement", "explosion sacrée"]
                    if cible.comp in competences_importantes:
                        score += 15
                
                # Bonus si l'allié peut encore agir (attaques ou mouvements restants)
                if hasattr(cible, 'attaque_restantes') and cible.attaque_restantes > 0:
                    score += 10
                if hasattr(cible, 'pm') and cible.pm > 0:
                    score += 5
                    
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
    
    elif competence == "pluie de flèches":
        # Évalue l'efficacité d'une attaque de zone
        if cible.equipe != unite.equipe:  # Ennemi (position de référence)
            score = 0
            # Compter les unités qui seraient touchées autour de cette position
            directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
            cases_affectees = [cible.pos]  # Position centrale
            
            # Ajouter les cases adjacentes
            for dq, dr in directions:
                case_adj = (cible.pos[0] + dq, cible.pos[1] + dr)
                cases_affectees.append(case_adj)
            
            # Calculer le score selon les unités touchées
            for case in cases_affectees:
                for u in tous_unites:
                    if u.pos == case and u.vivant:
                        if u.equipe != unite.equipe:  # Ennemi touché = bon
                            score += 35 + (u.tier * 5)
                            if u.pv <= unite.dmg:  # Peut être tué
                                score += 20
                        else:  # Allié touché = mauvais
                            score -= 25
        return score
    
    elif competence == "tir précis":
        if cible.equipe != unite.equipe:  # Ennemi
            # Priorité aux cibles importantes avec dégâts augmentés
            score = 40  # Score de base pour tir précis (dégâts x2)
            score += cible.tier * 8
            # Bonus si on peut tuer la cible d'un coup avec dégâts doublés
            if cible.pv <= unite.dmg * 2:
                score += 35
            # Malus si trop loin
            distance = hex_distance(unite.pos, cible.pos)
            score -= distance * 3
        return score
    
    elif competence == "commandement":
        if cible.equipe == unite.equipe:  # Allié
            # Donner +1 attaque à un allié qui peut l'utiliser
            score = 0
            if hasattr(cible, 'attaque_restantes'):
                # Bonus selon le potentiel offensif de l'allié
                score += cible.dmg * 8 + cible.tier * 6
                # Gros bonus si l'allié n'a plus d'attaques
                if cible.attaque_restantes == 0:
                    score += 40
                # Bonus si l'allié a des ennemis à portée
                ennemis_a_portee = [u for u in tous_unites 
                                  if u.vivant and u.equipe != cible.equipe 
                                  and est_a_portee_pos(cible.pos, u.pos, cible.portee)]
                score += len(ennemis_a_portee) * 15
        return score
    
    return 0

def peut_utiliser_competence_active(unite, competence, tous_unites):
    """Vérifie si l'unité peut utiliser sa compétence active."""
    from competences import est_competence_active
    
    if not hasattr(unite, 'comp') or unite.comp != competence:
        return False
    
    if not est_competence_active(competence):
        return False
    
    # Vérifier le cooldown
    if hasattr(unite, 'cooldown_actuel') and unite.cooldown_actuel > 0:
        return False
    
    # Compétences qui ne nécessitent pas d'attaque restante
    competences_sans_attaque = ["soin", "pluie de flèches", "commandement"]
    if unite.comp not in competences_sans_attaque and unite.attaque_restantes <= 0:
        return False
    
    return True

def trouver_meilleure_cible_competence(unite, competence, tous_unites):
    """Trouve la meilleure cible pour une compétence active."""
    from competences import peut_cibler_allie, peut_cibler_ennemi, peut_cibler_case_vide
    
    cibles_potentielles = []
    
    # Déterminer la portée à utiliser pour cette compétence
    if competence == "soin":
        portee_competence = 99  # Portée illimitée pour le soin
    else:
        portee_competence = unite.portee  # Portée normale pour les autres compétences
    
    # Gestion spéciale pour les compétences de zone (comme pluie de flèches)
    if peut_cibler_case_vide(competence) and competence == "pluie de flèches":
        # Pour pluie de flèches, on évalue les positions centrées sur les ennemis
        ennemis = [u for u in tous_unites if u.vivant and u.equipe != unite.equipe]
        for ennemi in ennemis:
            if est_a_portee_pos(unite.pos, ennemi.pos, portee_competence):
                cibles_potentielles.append(ennemi)  # Utiliser l'ennemi comme référence de position
    else:
        # Logique normale pour les autres compétences
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
    
    # Seuil adaptatif selon la compétence
    seuil_minimum = 30  # Seuil par défaut
    if competence == "soin":
        seuil_minimum = 15  # Seuil plus bas pour permettre plus de soins
    elif competence == "bénédiction":
        seuil_minimum = 25  # Seuil modéré pour bénédiction
    
    return meilleure_cible if meilleur_score > seuil_minimum else None

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
    if hasattr(unite, 'comp') and peut_utiliser_competence_active(unite, unite.comp, unites):
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
            unite.attaquer(cible, unites)
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
            unite.attaquer(enn, unites)
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
    if hasattr(unite, 'comp') and peut_utiliser_competence_active(unite, unite.comp, unites):
        competence = unite.comp
        # Soigner un allié critique en priorité (logique assouplie)
        if competence == "soin":
            meilleure_cible = trouver_meilleure_cible_competence(unite, competence, unites)
            if meilleure_cible:
                unite.utiliser_competence(meilleure_cible, unites)
                return "competence_soin"
        # Bénédiction : ne pas buff une unité déjà buffée, et comparer à l'intérêt d'attaquer
        elif competence == "bénédiction":
            # Filtrer les alliés non buffés
            allies_non_buffes = [u for u in unites if u.vivant and u.equipe == unite.equipe and not getattr(u, 'buff_bénédiction', False)]
            meilleure_cible = None
            print(allies_non_buffes.__len__)
            meilleur_score = 0
            for cible in allies_non_buffes:
                score = evaluer_utilite_competence(unite, competence, cible, unites)
                if score > meilleur_score:
                    meilleur_score = score
                    meilleure_cible = cible
            # Calculer l'intérêt d'attaquer
            score_attaque = 0
            if unite.attaque_restantes > 0:
                # On prend la meilleure cible ennemie
                ennemis_vivants = [e for e in ennemis if e.vivant]
                if ennemis_vivants:
                    score_attaque = max(_evaluer_cible(unite, e, unites, [a for a in unites if a.vivant and a.equipe == unite.equipe and a != unite]) for e in ennemis_vivants)
            # Si le buff est plus intéressant que l'attaque, on buff
            print(meilleure_cible, score_attaque, meilleur_score)
            if meilleure_cible and meilleur_score > score_attaque:
                unite.utiliser_competence(meilleure_cible, unites)
                return "competence_benediction"
            # Si aucune cible à bénir, passer à l'attaque normale
            elif not allies_non_buffes:
                pass  # Permet à l'IA de continuer et d'attaquer comme une unité classique
        # Commandement : donner une attaque supplémentaire
        elif competence == "commandement":
            meilleure_cible = trouver_meilleure_cible_competence(unite, competence, unites)
            if meilleure_cible:
                unite.utiliser_competence(meilleure_cible, unites)
                return "competence_commandement"
        # Attaques spéciales à cooldown
        elif competence in ["pluie de flèches", "tir précis"]:
            meilleure_cible = trouver_meilleure_cible_competence(unite, competence, unites)
            if meilleure_cible:
                unite.utiliser_competence(meilleure_cible, unites)
                return f"competence_{competence.replace(' ', '_')}"
    
    # Phase 3: Utiliser compétences immédiates si pertinent
    if utiliser_competence_immediate(unite, unites):
        return "competence_immediate"
    
    # Phase 4: Stratégie d'attaque adaptative
    return _strategie_attaque_adaptative(unite, ennemis_vivants, unites, allies)


def _strategie_attaque_adaptative(unite, ennemis, unites, allies):
    """Stratégie d'attaque qui s'adapte à la situation tactique."""
    
    # PHASE DÉFENSIVE AVANCÉE : Vérifier si une stratégie défensive est prioritaire
    if should_use_golem_blocking(unite, ennemis, allies):
        accessibles = unite.cases_accessibles(unites)
        accessibles = dict(accessibles)
        accessibles.setdefault(unite.pos, 0)
        
        position_blocage = find_optimal_blocking_position(unite, ennemis, allies, accessibles)
        if position_blocage and position_blocage != unite.pos:
            cout = accessibles[position_blocage]
            if cout <= unite.pm:
                unite.pos = position_blocage
                unite.pm -= cout
                return "blocage_defensif"
    
    # PHASE TACTIQUE PASSIVE : Appliquer des stratégies spécialisées selon les passifs
    result_tactique = apply_advanced_passive_tactics(unite, ennemis, allies, unites)
    if result_tactique:
        return result_tactique
    
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
            unite.attaquer(cible_prioritaire, unites)
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
                unite.attaquer(cible, unites)
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
    
    # --- BONUS SPÉCIAUX BASÉS SUR LES PASSIFS OFFENSIFS ---
    
    # LUMIÈRE VENGERESSE contre les morts-vivants
    if (hasattr(unite, 'comp') and unite.comp == "lumière vengeresse" and 
        hasattr(ennemi, 'faction') and ennemi.faction == "Morts-Vivants"):
        # Gros bonus pour cibler les morts-vivants car cela donne une attaque supplémentaire
        score += 30
        # Bonus encore plus gros si on peut les tuer d'un coup (attaque gratuite)
        if ennemi.pv <= unite.dmg:
            score += 50
    
    # RAGE - Prioriser les ennemis qu'on peut enchaîner pour accumuler rage
    if hasattr(unite, 'comp') and unite.comp == "rage":
        # Bonus si on peut tuer l'ennemi (rage s'accumule)
        if ennemi.pv <= unite.dmg:
            score += 25
            # Bonus supplémentaire si il y a d'autres ennemis à portée après
            autres_ennemis_proches = [e for e in unites 
                                     if (e.vivant and e.equipe != unite.equipe 
                                         and e != ennemi 
                                         and hex_distance(ennemi.pos, e.pos) <= 2)]
            score += len(autres_ennemis_proches) * 10
    
    # SANGSUE - Prioriser les combats soutenus contre ennemis durables
    if hasattr(unite, 'comp') and unite.comp == "sangsue":
        # Bonus si l'ennemi a beaucoup de PV (plus de sustain)
        if ennemi.pv > unite.pv:
            score += 20
        # Bonus si on peut faire des dégâts élevés
        score += min(unite.dmg, ennemi.pv) * 5
    
    # REGARD MORTEL - Prioriser les ennemis tier 2 ou moins
    if hasattr(unite, 'comp') and unite.comp == "regard mortel":
        if ennemi.tier <= 2:
            score += 60  # Très haute priorité pour insta-kill
            # Bonus encore plus important si l'ennemi a beaucoup de PV
            if ennemi.pv > unite.dmg:
                score += 40  # Économise beaucoup d'attaques
    
    # TIR PRÉCIS - Évaluer avec dégâts doublés
    if hasattr(unite, 'comp') and unite.comp == "tir précis":
        if hasattr(unite, 'cooldown_actuel') and unite.cooldown_actuel == 0:
            # Simuler les dégâts avec tir précis (x1.5 selon la description)
            degats_tir_precis = int(unite.dmg * 1.5)
            if ennemi.pv <= degats_tir_precis:
                score += 35  # Peut tuer avec tir précis
            score += 15  # Bonus général pour tir précis
    
    # --- ADAPTATION AUX PASSIFS ENNEMIS ---
    
    if hasattr(ennemi, 'comp'):
        # VOL ennemi - Moins prioritaire car première attaque sera ignorée
        if ennemi.comp == "vol":
            score -= 20
        
        # ARMURE DE PIERRE ennemie - Moins efficace si nos dégâts sont faibles
        elif ennemi.comp == "armure de pierre":
            if unite.dmg <= 4:
                score -= 25  # Dégâts fortement réduits
            elif unite.dmg <= 6:
                score -= 15  # Dégâts modérément réduits
        
        # RENAISSANCE ennemie - Risque de revival
        elif ennemi.comp == "renaissance":
            score -= 15  # 80% de revenir à la vie
        
        # MANIPULATION ennemie - Priorité si on a ≤4 PV
        elif ennemi.comp == "manipulation":
            if unite.pv <= 4:
                score += 40  # Priorité absolue pour éviter d'être manipulé
        
        # COMBUSTION DIFFÉRÉE ennemie - Danger à long terme
        elif ennemi.comp == "combustion différée":
            score += 25  # Éliminer rapidement
        
        # VENIN INCAPACITANT ennemi - Réduire mobilité
        elif ennemi.comp == "venin incapacitant":
            # Prioritaire si notre unité dépend du mouvement
            if unite.pm > 1:  # Unité mobile
                score += 20
        
        # SÉDITION VENIMEUSE - Danger pour nos alliés adjacents
        elif ennemi.comp == "sédition venimeuse":
            allies_adjacents_a_nous = [a for a in allies if est_adjacent_pos(unite.pos, a.pos)]
            if allies_adjacents_a_nous:
                score += 15  # Éviter qu'on attaque nos alliés
    
    return max(0, score)


def _choisir_meilleure_position_attaque(positions, accessibles, cible, unites, unite):
    """Choisit la meilleure position pour attaquer une cible."""
    if not positions:
        return unite.pos
    
    # Séparer alliés et ennemis
    ennemis = [u for u in unites if u.vivant and u.equipe != unite.equipe]
    allies = [u for u in unites if u.vivant and u.equipe == unite.equipe and u != unite]
    
    meilleure_pos = None
    meilleur_score = float('-inf')
    
    for pos in positions:
        score = 0
        
        # Préférer les positions avec un coût minimal
        score -= accessibles[pos] * 10
        
        # ÉVALUATION DÉFENSIVE AVANCÉE basée sur les passifs
        score_defensif = evaluate_defensive_passive(unite, pos, ennemis, allies)
        score += score_defensif
        
        # Éviter d'être adjacent à trop d'ennemis (sauf si on a des passifs défensifs)
        ennemis_adjacents = [u for u in unites 
                           if (u.vivant and u.equipe != unite.equipe and u != cible
                               and est_adjacent_pos(pos, u.pos))]
        
        # Modifier le malus selon les capacités défensives
        malus_ennemis = len(ennemis_adjacents) * 20
        if hasattr(unite, 'comp'):
            if unite.comp == "armure de pierre":
                # Réduire le malus pour armure de pierre contre ennemis faibles
                ennemis_faibles = [e for e in ennemis_adjacents if e.dmg <= 4]
                malus_ennemis -= len(ennemis_faibles) * 15  # Moins peur des faibles
            elif unite.comp == "vol":
                # Réduire le malus si vol peut nous protéger
                if len(ennemis_adjacents) == 1:  # Une seule attaque = vol optimal
                    malus_ennemis //= 2
        
        score -= malus_ennemis
        
        # Préférer les positions près des alliés (soutien)
        allies_adjacents = [u for u in unites 
                          if (u.vivant and u.equipe == unite.equipe and u != unite
                              and est_adjacent_pos(pos, u.pos))]
        
        bonus_allies = len(allies_adjacents) * 5
        # Bonus spécial pour protection
        if hasattr(unite, 'comp') and unite.comp == "protection":
            # Protection valorise d'être près des alliés fragiles
            allies_fragiles = [a for a in allies_adjacents if a.pv <= 5]
            bonus_allies += len(allies_fragiles) * 15
        
        score += bonus_allies
        
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


# --- GESTION AVANCÉE DES PASSIFS ---

def evaluate_defensive_passive(unite, position, ennemis, allies):
    """Évalue l'efficacité défensive d'une unité avec ses passifs à une position donnée."""
    if not hasattr(unite, 'comp') or not unite.comp:
        return 0
    
    score = 0
    competence = unite.comp
    
    # ARMURE DE PIERRE - Excellent tank contre multiples faibles attaquants
    if competence == "armure de pierre":
        ennemis_adjacents = [e for e in ennemis if est_adjacent_pos(position, e.pos)]
        for ennemi in ennemis_adjacents:
            # Plus l'attaque ennemie est faible, plus l'armure de pierre est efficace
            if ennemi.dmg <= 4:  # Réduction significative
                score += 30
            elif ennemi.dmg <= 6:  # Réduction modérée
                score += 15
            else:  # Réduction minimale mais utile
                score += 5
        # Bonus pour chaque ennemi supplémentaire (tank AoE)
        score += len(ennemis_adjacents) * 10
    
    # VOL - Ignore la première attaque, excellent contre gros dégâts uniques
    elif competence == "vol":
        # Identifier l'ennemi le plus menaçant à portée
        ennemis_dangereux = [e for e in ennemis 
                           if est_a_portee_pos(position, e.pos, e.portee) 
                           and e.dmg >= 5]
        if ennemis_dangereux:
            # Plus l'attaque est forte, plus vol est précieux
            max_degats = max(e.dmg for e in ennemis_dangereux)
            score += max_degats * 8  # Plus les dégâts sont élevés, mieux c'est
            # Bonus si l'unité peut survivre après avoir volé une grosse attaque
            if unite.pv > max_degats:
                score += 25
    
    # PROTECTION - Protège les alliés adjacents
    elif competence == "protection":
        allies_adjacents = [a for a in allies if est_adjacent_pos(position, a.pos)]
        for allie in allies_adjacents:
            # Priorité aux alliés fragiles et importants
            if allie.pv <= 3:
                score += 40  # Protéger les alliés critiques
            elif allie.pv <= 5:
                score += 25  # Protéger les alliés blessés
            else:
                score += 10  # Protection générale
            
            # Bonus si l'allié a une compétence importante
            if hasattr(allie, 'comp') and allie.comp in ["soin", "bénédiction", "commandement"]:
                score += 20
        
        # Évaluer les menaces sur les alliés protégés
        for allie in allies_adjacents:
            ennemis_menaçants = [e for e in ennemis 
                               if est_a_portee_pos(allie.pos, e.pos, e.portee)]
            score += len(ennemis_menaçants) * 15
    
    return score


def evaluate_blocking_potential(unite, position, ennemis, allies):
    """Évalue le potentiel de blocage tactique d'une position."""
    if not hasattr(unite, 'comp') or unite.comp != "armure de pierre":
        return 0
    
    score = 0
    
    # Identifier les ennemis faibles que cette unité peut efficacement bloquer
    ennemis_bloquables = [e for e in ennemis if e.dmg <= 4]  # Dégâts faibles
    
    for ennemi in ennemis_bloquables:
        # Distance entre l'ennemi et les alliés les plus proches
        distance_min_allie = float('inf')
        for allie in allies:
            if allie != unite:
                dist = hex_distance(ennemi.pos, allie.pos)
                distance_min_allie = min(distance_min_allie, dist)
        
        # Si on peut s'interposer entre l'ennemi faible et nos alliés
        if distance_min_allie > 1:  # Il y a un chemin à bloquer
            distance_vers_ennemi = hex_distance(position, ennemi.pos)
            if distance_vers_ennemi <= 2:  # On peut se positionner
                # Plus l'ennemi est proche de nos alliés, plus c'est urgent
                score += max(0, 50 - distance_min_allie * 10)
                # Bonus si on bloque plusieurs ennemis faibles
                score += 20
    
    # Bonus pour contrôler des passages étroits ou positions clés
    ennemis_proches = [e for e in ennemis if hex_distance(position, e.pos) <= 2]
    allies_proches = [a for a in allies if hex_distance(position, a.pos) <= 2 and a != unite]
    
    # Position stratégique si on est entre beaucoup d'ennemis et d'alliés
    if len(ennemis_proches) >= 2 and len(allies_proches) >= 1:
        score += 30
    
    return score


def should_use_golem_blocking(unite, ennemis, allies):
    """Détermine si l'unité devrait utiliser une stratégie de blocage défensif."""
    if not hasattr(unite, 'comp') or unite.comp != "armure de pierre":
        return False
    
    # Compter les ennemis faibles qui peuvent être efficacement bloqués
    ennemis_faibles = [e for e in ennemis if e.vivant and e.dmg <= 4]
    
    # Compter les alliés fragiles qui bénéficieraient de la protection
    allies_fragiles = [a for a in allies if a.vivant and a.pv <= 5]
    
    # Utiliser le blocage si :
    # 1. Il y a au moins 2 ennemis faibles OU
    # 2. Il y a au moins 1 allié fragile et 1 ennemi faible
    return (len(ennemis_faibles) >= 2 or 
            (len(allies_fragiles) >= 1 and len(ennemis_faibles) >= 1))


def find_optimal_blocking_position(unite, ennemis, allies, accessibles):
    """Trouve la meilleure position pour une stratégie de blocage."""
    if not accessibles:
        return None
    
    meilleure_pos = None
    meilleur_score = 0
    
    for pos, cout in accessibles.items():
        if cout > unite.pm:
            continue
        
        # Score de blocage défensif
        score_defensif = evaluate_defensive_passive(unite, pos, ennemis, allies)
        score_blocage = evaluate_blocking_potential(unite, pos, ennemis, allies)
        
        score_total = score_defensif + score_blocage - (cout * 5)
        
        if score_total > meilleur_score:
            meilleur_score = score_total
            meilleure_pos = pos
    
    return meilleure_pos if meilleur_score > 30 else None


# --- STRATÉGIES TACTIQUES PASSIVES COMPLEXES ---

def evaluate_manipulation_strategy(unite, ennemis, allies, accessibles):
    """Évalue l'opportunité d'utiliser une stratégie de manipulation."""
    if not hasattr(unite, 'comp') or unite.comp != "manipulation":
        return None, 0
    
    # Identifier les ennemis vulnérables à la manipulation (≤4 PV)
    cibles_manipulables = [e for e in ennemis if e.vivant and e.pv <= 4]
    
    if not cibles_manipulables:
        return None, 0
    
    meilleure_pos = None
    meilleur_score = 0
    
    for pos, cout in accessibles.items():
        if cout > unite.pm:
            continue
        
        score = 0
        
        # Compter combien d'ennemis seraient manipulés depuis cette position
        ennemis_manipules = []
        for ennemi in cibles_manipulables:
            # La manipulation affecte les unités avec ≤4 PV à la fin du tour
            # L'IA doit se positionner pour maximiser les unités affectées
            if hex_distance(pos, ennemi.pos) <= 3:  # Zone d'influence raisonnable
                ennemis_manipules.append(ennemi)
                score += ennemi.dmg * 15  # Valeur de l'ennemi manipulé
                score += ennemi.tier * 10
        
        # Bonus si on peut manipuler plusieurs ennemis
        if len(ennemis_manipules) >= 2:
            score += 30
        
        # Malus pour le coût du mouvement
        score -= cout * 8
        
        if score > meilleur_score:
            meilleur_score = score
            meilleure_pos = pos
    
    return meilleure_pos, meilleur_score


def evaluate_venin_incapacitant_strategy(unite, ennemis, allies, accessibles):
    """Évalue l'opportunité d'utiliser venin incapacitant tactiquement."""
    if not hasattr(unite, 'comp') or unite.comp != "venin incapacitant":
        return None, 0
    
    meilleure_pos = None
    meilleur_score = 0
    
    for pos, cout in accessibles.items():
        if cout > unite.pm:
            continue
        
        score = 0
        
        # Identifier les ennemis à portée qui bénéficieraient d'être immobilisés
        for ennemi in ennemis:
            if est_a_portee_pos(pos, ennemi.pos, unite.portee):
                # Plus l'ennemi est mobile, plus c'est utile de l'immobiliser
                if hasattr(ennemi, 'pm'):
                    score += ennemi.pm * 15
                
                # Bonus si l'ennemi menace des alliés qu'il ne pourra plus atteindre
                if ennemi.pm > 1:  # L'ennemi perdrait sa mobilité
                    allies_hors_portee = [a for a in allies 
                                         if (hex_distance(ennemi.pos, a.pos) > ennemi.portee 
                                             and hex_distance(ennemi.pos, a.pos) <= ennemi.portee + ennemi.pm)]
                    score += len(allies_hors_portee) * 20
                
                # Bonus si l'ennemi a des compétences de déplacement importantes
                if hasattr(ennemi, 'comp') and ennemi.comp in ["monture libéré", "fantomatique"]:
                    score += 25
        
        score -= cout * 5
        
        if score > meilleur_score:
            meilleur_score = score
            meilleure_pos = pos
    
    return meilleure_pos, meilleur_score


def evaluate_sedition_venimeuse_chaos(unite, ennemis, allies, accessibles):
    """Évalue l'opportunité de créer le chaos avec sédition venimeuse."""
    if not hasattr(unite, 'comp') or unite.comp != "sédition venimeuse":
        return None, 0
    
    meilleure_pos = None
    meilleur_score = 0
    
    for pos, cout in accessibles.items():
        if cout > unite.pm:
            continue
        
        score = 0
        
        # Chercher des ennemis qui ont d'autres ennemis adjacents
        for ennemi in ennemis:
            if est_a_portee_pos(pos, ennemi.pos, unite.portee):
                # Compter les ennemis adjacents à cette cible
                ennemis_adjacents = [e for e in ennemis 
                                   if e != ennemi and est_adjacent_pos(ennemi.pos, e.pos)]
                
                if ennemis_adjacents:
                    # Plus il y a d'ennemis adjacents, plus le chaos potentiel est grand
                    score += len(ennemis_adjacents) * 25
                    
                    # Bonus si les ennemis adjacents sont forts
                    for adj in ennemis_adjacents:
                        score += adj.dmg * 8
                        score += adj.tier * 5
                    
                    # Bonus spécial si on peut faire attaquer des unités importantes
                    unites_importantes = [e for e in ennemis_adjacents 
                                         if hasattr(e, 'comp') and e.comp in 
                                         ["soin", "bénédiction", "invocation", "commandement"]]
                    score += len(unites_importantes) * 30
        
        score -= cout * 5
        
        if score > meilleur_score:
            meilleur_score = score
            meilleure_pos = pos
    
    return meilleure_pos, meilleur_score


def evaluate_combustion_differee_timing(unite, ennemis, allies):
    """Évalue le timing optimal pour utiliser combustion différée."""
    if not hasattr(unite, 'comp') or unite.comp != "combustion différée":
        return 0
    
    score = 0
    
    # Priorité aux ennemis avec beaucoup de PV (ils ont 3 tours pour agir)
    for ennemi in ennemis:
        if est_a_portee_pos(unite.pos, ennemi.pos, unite.portee):
            # Plus l'ennemi a de PV, plus combustion différée est intéressante
            if ennemi.pv > unite.dmg * 2:
                score += 40  # Bon investissement sur une cible durable
            
            # Bonus si l'ennemi a des compétences dangereuses à long terme
            if hasattr(ennemi, 'comp'):
                competences_dangereuses = ["invocation", "nécromancie", "soin", "manipulation"]
                if ennemi.comp in competences_dangereuses:
                    score += 20  # L'éliminer à terme vaut le coup
            
            # Malus si l'ennemi peut être tué rapidement par d'autres moyens
            if ennemi.pv <= unite.dmg:
                score -= 25  # Mieux vaut le tuer tout de suite
    
    return score


def apply_advanced_passive_tactics(unite, ennemis, allies, unites):
    """Applique les stratégies tactiques avancées basées sur les passifs."""
    if not hasattr(unite, 'comp') or not unite.comp:
        return None
    
    accessibles = unite.cases_accessibles(unites)
    accessibles = dict(accessibles)
    accessibles.setdefault(unite.pos, 0)
    
    # Évaluer chaque stratégie passive
    strategies = []
    
    # Manipulation
    pos_manipulation, score_manipulation = evaluate_manipulation_strategy(
        unite, ennemis, allies, accessibles)
    if score_manipulation > 30:
        strategies.append(("manipulation", pos_manipulation, score_manipulation))
    
    # Venin incapacitant
    pos_venin, score_venin = evaluate_venin_incapacitant_strategy(
        unite, ennemis, allies, accessibles)
    if score_venin > 25:
        strategies.append(("venin_incapacitant", pos_venin, score_venin))
    
    # Sédition venimeuse
    pos_sedition, score_sedition = evaluate_sedition_venimeuse_chaos(
        unite, ennemis, allies, accessibles)
    if score_sedition > 35:
        strategies.append(("sedition_venimeuse", pos_sedition, score_sedition))
    
    # Combustion différée (évaluation pour prioriser les cibles)
    score_combustion = evaluate_combustion_differee_timing(unite, ennemis, allies)
    if score_combustion > 30:
        strategies.append(("combustion_differee", unite.pos, score_combustion))
    
    # Choisir la meilleure stratégie
    if strategies:
        strategies.sort(key=lambda x: x[2], reverse=True)
        meilleure_strategie, meilleure_pos, _ = strategies[0]
        
        # Appliquer la stratégie
        if meilleure_pos and meilleure_pos != unite.pos:
            cout = accessibles[meilleure_pos]
            if cout <= unite.pm:
                unite.pos = meilleure_pos
                unite.pm -= cout
                return f"tactique_{meilleure_strategie}"
    
    return None
