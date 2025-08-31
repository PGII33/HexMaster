# stratégie simple: cible la cible la plus faible, approche et attaque si adjacent

def cible_faible(unite, ennemis, unites):
    cibles = [e for e in ennemis if e.vivant]
    if not cibles:
        return None
    cible = min(cibles, key=lambda x: x.pv)
    if unite.est_adjacente(cible) and not unite.a_attaque:
        unite.attaquer(cible)
        return "attaque"
    if unite.pm > 0:
        q, r = unite.pos
        cq, cr = cible.pos
        dq, dr = cq - q, cr - r
        step = (0, 0)
        # simple pas axial (garde comportement précédent)
        if abs(dq) > abs(dr):
            step = (1 if dq > 0 else -1, 0)
        else:
            step = (0, 1 if dr > 0 else -1)
        new_pos = (q+step[0], r+step[1])
        occupee = any(u.pos == new_pos and u.vivant for u in unites)
        if not occupee:
            unite.pos = new_pos
            unite.pm -= 1
            return "deplacement"
    return None