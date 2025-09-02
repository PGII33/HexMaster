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

# --- IA cible faible corrigée ---

def cible_faible(unite, ennemis, unites):
    # 0) Filtre
    cibles = [e for e in ennemis if e.vivant]
    if not cibles:
        return None

    cible = min(cibles, key=lambda x: x.pv)

    # 1) Cases atteignables (inclure la position actuelle)
    accessibles = unite.cases_accessibles(unites)
    accessibles = dict(accessibles)  # copie défensive
    accessibles.setdefault(unite.pos, 0)

    # 2) Peut-on atteindre ET attaquer la cible ce tour-ci ?
    adj_to_target = [pos for pos in accessibles if est_adjacent_pos(pos, cible.pos)]
    if adj_to_target and not unite.a_attaque:
        # Choix: coût minimal puis (optionnel) distance au centre de la cible (toujours 1 si adjacent)
        best_pos = min(adj_to_target, key=lambda p: (accessibles[p], hex_distance(p, cible.pos)))
        cout = accessibles[best_pos]
        if cout > 0:
            unite.pos = best_pos
            unite.pm -= cout
        # Une seule attaque
        unite.attaquer(cible)
        return "attaque"

    # 3) Sinon, opportunisme: une autre cible attaquable depuis une case atteignable (y compris sans bouger)
    meilleure_option = None  # (cout, pv_ennemi, pos, enn)
    meilleur_score = None    # (cout, pv_ennemi) pour la comparaison
    
    for pos, cout in accessibles.items():
        # Si plus de PM que le coût nécessaire
        if cout > unite.pm:
            continue
        for enn in cibles:
            if est_adjacent_pos(pos, enn.pos):
                score = (cout, enn.pv)  # Seulement les critères de comparaison
                if (meilleur_score is None) or (score < meilleur_score):
                    meilleur_score = score
                    meilleure_option = (cout, enn.pv, pos, enn)

    if (meilleure_option is not None) and not unite.a_attaque:
        cout, _, pos, enn = meilleure_option
        if pos != unite.pos:
            unite.pos = pos
            unite.pm -= cout
        unite.attaquer(enn)
        return "attaque"

    # 4) Sinon, avancer vers la cible principale (sans attaquer)
    if accessibles and unite.pm > 0:
        # Choisir la case qui réduit le plus la distance hex; tie-breaker sur coût
        best_move = min(accessibles.keys(), key=lambda p: (hex_distance(p, cible.pos), accessibles[p]))
        if best_move != unite.pos and accessibles[best_move] <= unite.pm:
            unite.pos = best_move
            unite.pm -= accessibles[best_move]
            return "deplacement"

    return None
