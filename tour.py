""" Module gérant le tour des équipes dans le jeu."""
def reset_actions_tour(jeu):
    """ Réinitialise les actions des unités au début du tour. """
    for u in jeu.unites:
        if u.get_equipe() == jeu.tour and u.get_vivant():
            u.reset_actions()
            u.debut_tour(jeu.unites, jeu, jeu.q_range, jeu.r_range)
