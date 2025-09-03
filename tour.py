def reset_actions_tour(jeu):
    for u in jeu.unites:
        if u.equipe == jeu.tour and u.vivant:
            u.reset_actions()
            if hasattr(u, 'debut_tour'):
                u.debut_tour(jeu.unites, jeu, jeu.q_range, jeu.r_range)