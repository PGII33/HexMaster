def reset_actions_tour(jeu):
    for u in jeu.unites:
        if u.equipe == jeu.tour and u.vivant:
            u.reset_actions()