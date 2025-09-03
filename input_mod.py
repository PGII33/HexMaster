import pygame
from layout import hex_to_pixel
from tour import reset_actions_tour

def handle_click(jeu, mx, my):
    # clic bouton fin de tour - TOUJOURS ACCESSIBLE
    if hasattr(jeu, 'btn_fin_tour') and jeu.btn_fin_tour.collidepoint(mx, my):
        jeu.changer_tour()
        return

    # clic sur une unité ?
    for u in jeu.unites:
        if not u.vivant:
            continue
        x, y = hex_to_pixel(jeu, u.pos[0], u.pos[1])
        if (mx-x)**2 + (my-y)**2 <= (jeu.unit_radius)**2:
            # Vérifier si c'est l'unité du joueur courant
            if u.equipe == jeu.tour:
                # Sélection/désélection de ses propres unités
                if jeu.selection == u:
                    jeu.selection = None
                    jeu.deplacement_possibles = {}
                else:
                    jeu.selection = u
                    jeu.deplacement_possibles = u.cases_accessibles(jeu.unites, jeu.q_range, jeu.r_range)
            else:
                # Clic sur une unité adverse
                if (
                    jeu.selection
                    and jeu.selection.attaque_restantes > 0
                    and jeu.selection.equipe == jeu.tour
                    and _are_enemies(jeu.selection.equipe, u.equipe, getattr(jeu, 'versus_mode', False))
                    and jeu.selection.est_a_portee(u)
                ):
                    # Attaquer l'unité adverse
                    jeu.selection.attaquer(u)
                    # Met à jour les cases accessibles après l'attaque
                    jeu.deplacement_possibles = jeu.selection.cases_accessibles(jeu.unites, jeu.q_range, jeu.r_range)
                else:
                    # Simplement sélectionner l'unité adverse pour voir ses stats
                    jeu.selection = u
                    jeu.deplacement_possibles = {}
                return

    # clic sur une case accessible ?
    if jeu.selection and jeu.deplacement_possibles and jeu.selection.equipe == jeu.tour:
        for case, cout in jeu.deplacement_possibles.items():
            q, r = case
            # VÉRIFIER QUE LA CASE EST DANS LA GRILLE VALIDE
            if q not in jeu.q_range or r not in jeu.r_range:
                continue
                
            cx, cy = hex_to_pixel(jeu, q, r)
            if (mx-cx)**2 + (my-cy)**2 <= (jeu.unit_radius)**2:
                occupee = any(x.pos == case and x.vivant for x in jeu.unites)
                if not occupee and jeu.selection.pm >= cout:
                    jeu.selection.pos = case
                    jeu.selection.pm -= cout
                    # Met à jour les cases accessibles après déplacement
                    jeu.deplacement_possibles = jeu.selection.cases_accessibles(jeu.unites, jeu.q_range, jeu.r_range)
                else:
                    jeu.deplacement_possibles = {}
                return

def _are_enemies(equipe1, equipe2, versus_mode):
    """Détermine si deux équipes sont ennemies selon le mode de jeu"""
    if versus_mode:
        # En mode versus : joueur vs joueur2
        return (equipe1 == "joueur" and equipe2 == "joueur2") or (equipe1 == "joueur2" and equipe2 == "joueur")
    else:
        # Mode normal : joueur vs ennemi
        return (equipe1 == "joueur" and equipe2 == "ennemi") or (equipe1 == "ennemi" and equipe2 == "joueur")