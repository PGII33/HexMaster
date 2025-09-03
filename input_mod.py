import pygame
from layout import hex_to_pixel
from tour import reset_actions_tour

# handle_click: gère sélection d'unités / attaques / déplacements

def handle_click(jeu, mx, my):
    # clic bouton fin de tour
    if jeu.btn_fin_tour.collidepoint(mx, my):
        jeu.tour = 'ennemi' if jeu.tour == 'joueur' else 'joueur'
        jeu.selection = None
        jeu.deplacement_possibles = {}
        reset_actions_tour(jeu)
        return

    # clic sur une unité ?
    for u in jeu.unites:
        if not u.vivant:
            continue
        x,y = hex_to_pixel(jeu, u.pos[0], u.pos[1])
        if (mx-x)**2 + (my-y)**2 <= (jeu.unit_radius)**2:
            if u.equipe == jeu.tour:
                if jeu.selection == u:
                    jeu.selection = None
                    jeu.deplacement_possibles = {}
                else:
                    jeu.selection = u
                    jeu.deplacement_possibles = u.cases_accessibles(jeu.unites)
            else:
                # clic sur ennemi
                if (
                    jeu.selection
                    and jeu.selection.attaque_restantes > 0
                    and jeu.selection.equipe == jeu.tour
                    and u.equipe != jeu.tour
                    and jeu.selection.est_a_portee(u)
                ):
                    jeu.selection.attaquer(u)
                    # Met à jour les cases accessibles après l'attaque
                    jeu.deplacement_possibles = jeu.selection.cases_accessibles(jeu.unites)
                else:
                    jeu.selection = u
                    jeu.deplacement_possibles = {}
                return

    # clic sur une case accessible ?
    if jeu.selection and jeu.deplacement_possibles:
        for case, cout in jeu.deplacement_possibles.items():
            cx, cy = hex_to_pixel(jeu, case[0], case[1])
            if (mx-cx)**2 + (my-cy)**2 <= (jeu.unit_radius)**2:
                occupee = any(x.pos == case and x.vivant for x in jeu.unites)
                if not occupee and jeu.selection.pm >= cout:
                    jeu.selection.pos = case
                    jeu.selection.pm -= cout
                    # Met à jour les cases accessibles après déplacement
                    jeu.deplacement_possibles = jeu.selection.cases_accessibles(jeu.unites)
                else:
                    jeu.deplacement_possibles = {}
                return