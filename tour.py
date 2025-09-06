def reset_actions_tour(jeu):
    for u in jeu.unites:
        if u.equipe == jeu.tour and u.vivant:
            u.reset_actions()
            
            # Réinitialiser les compteurs de protection IA
            if hasattr(u, '_ia_tentatives_tour'):
                u._ia_tentatives_tour = 0
            if hasattr(u, '_derniere_position'):
                u._derniere_position = u.pos
            
            if hasattr(u, 'debut_tour'):
                u.debut_tour(jeu.unites, jeu, jeu.q_range, jeu.r_range)