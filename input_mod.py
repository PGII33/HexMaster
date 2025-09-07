import pygame
from layout import hex_to_pixel
from tour import reset_actions_tour
import competences as co

def handle_click(jeu, mx, my):
    # clic bouton fin de tour - TOUJOURS ACCESSIBLE
    if hasattr(jeu, 'btn_fin_tour') and jeu.btn_fin_tour.collidepoint(mx, my):
        jeu.changer_tour()
        return

    # Gérer le mode de sélection de compétence
    if hasattr(jeu, 'mode_selection_competence') and jeu.mode_selection_competence:
        _handle_competence_target_selection(jeu, mx, my)
        return

    # clic sur le bouton de compétence active
    if (hasattr(jeu, 'competence_btn_rect') and jeu.competence_btn_rect and 
        jeu.competence_btn_rect.collidepoint(mx, my) and jeu.selection and 
        jeu.selection.equipe == jeu.tour):
        
        print(f"🔵 CLIC SUR BOUTON COMPETENCE: {jeu.selection.get_competence()}")
        
        # Vérifier que la compétence est utilisable (pas en cooldown et pas déjà utilisée)
        cooldown_restant = getattr(jeu.selection, 'cooldown_actuel', 0)
        competence_utilisee = getattr(jeu.selection, 'competence_utilisee_ce_tour', False)
        
        # Compétences qui ne nécessitent pas d'attaque restante
        competences_sans_attaque = ["soin"]
        comp_name = jeu.selection.get_competence()
        attaque_necessaire = comp_name not in competences_sans_attaque
        
        if (jeu.selection.a_competence_active() and 
            (not attaque_necessaire or jeu.selection.attaque_restantes > 0) and 
            cooldown_restant == 0 and not competence_utilisee):
            
            print(f"🟢 ACTIVATION: {comp_name}")
            
            # Compétences qui ne nécessitent pas de cible
            if comp_name == "explosion sacrée":
                print(f"   Explosion sacrée directe")
                jeu.selection.utiliser_competence(None, jeu.unites)
                jeu.deplacement_possibles = jeu.selection.cases_accessibles(jeu.unites, jeu.q_range, jeu.r_range)
                return
            
            # Compétences qui nécessitent une cible
            elif comp_name in ["soin", "bénédiction", "cristalisation"]:
                print(f"🔸 DEBUG: Activation {comp_name} pour {jeu.selection.nom}")
                print(f"   - Mode sélection: {getattr(jeu, 'mode_selection_competence', False)}")
                print(f"   - Attaques restantes: {jeu.selection.attaque_restantes}")
                print(f"   - Cooldown: {getattr(jeu.selection, 'cooldown_actuel', 0)}")
                print(f"   - Compétence utilisée: {getattr(jeu.selection, 'competence_utilisee_ce_tour', False)}")
                
                print(f"   Mode sélection activé pour {comp_name}")
                # Entrer en mode sélection de cible
                jeu.mode_selection_competence = True
                jeu.competence_en_cours = comp_name
                jeu.unite_utilisant_competence = jeu.selection  # Stocker l'unité
                jeu.cibles_possibles = _get_valid_targets(jeu, comp_name, jeu.selection)
                print(f"   {len(jeu.cibles_possibles)} cibles disponibles")
                if jeu.cibles_possibles:
                    print(f"   Première cible: {jeu.cibles_possibles[0]}")
                return
        else:
            print(f"🔴 CONDITIONS NON REMPLIES")
            if not jeu.selection.a_competence_active():
                print(f"   - Pas de compétence active")
            if attaque_necessaire and jeu.selection.attaque_restantes <= 0:
                print(f"   - Pas d'attaque restante")
            if cooldown_restant > 0:
                print(f"   - En cooldown ({cooldown_restant} tours)")
            if competence_utilisee:
                print(f"   - Déjà utilisée ce tour")
        
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
                    jeu.selection.attaquer(u, jeu.unites)
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

def _handle_competence_target_selection(jeu, mx, my):
    """Gère la sélection de cible pour une compétence active."""
    # Vérifier que nous avons une unité qui utilise la compétence
    if not hasattr(jeu, 'unite_utilisant_competence') or jeu.unite_utilisant_competence is None:
        # Annuler le mode sélection si pas d'unité
        jeu.mode_selection_competence = False
        jeu.competence_en_cours = None
        jeu.cibles_possibles = []
        return
    
    # Clic sur une unité pour la cibler
    for u in jeu.unites:
        if not u.vivant:
            continue
        x, y = hex_to_pixel(jeu, u.pos[0], u.pos[1])
        if (mx-x)**2 + (my-y)**2 <= (jeu.unit_radius)**2:
            if u in jeu.cibles_possibles:
                # Utiliser la compétence sur cette cible
                success = jeu.unite_utilisant_competence.utiliser_competence(u, jeu.unites)
                if success:
                    # Sortir du mode sélection
                    jeu.mode_selection_competence = False
                    jeu.competence_en_cours = None
                    jeu.cibles_possibles = []
                    jeu.unite_utilisant_competence = None
                    # Mettre à jour l'affichage si l'unité est encore sélectionnée
                    if jeu.selection == jeu.unite_utilisant_competence:
                        jeu.deplacement_possibles = jeu.selection.cases_accessibles(jeu.unites, jeu.q_range, jeu.r_range)
                return
    
    # Vérifier les clics sur des cases vides (pour cristalisation)
    for cible_pos in jeu.cibles_possibles:
        if isinstance(cible_pos, tuple):  # C'est une position de case vide
            q, r = cible_pos
            x, y = hex_to_pixel(jeu, q, r)
            # Vérifier si le clic est dans cette case hexagonale
            if (mx-x)**2 + (my-y)**2 <= (jeu.taille_hex)**2:
                print(f"🟢 CLIC SUR CASE VIDE: {cible_pos}")
                # Utiliser la compétence sur cette position
                success = jeu.unite_utilisant_competence.utiliser_competence(cible_pos, jeu.unites)
                if success:
                    print(f"🟢 COMPETENCE UTILISEE SUR CASE VIDE")
                    # Sortir du mode sélection
                    jeu.mode_selection_competence = False
                    jeu.competence_en_cours = None
                    jeu.cibles_possibles = []
                    jeu.unite_utilisant_competence = None
                    # Mettre à jour l'affichage
                    if jeu.selection:
                        jeu.deplacement_possibles = jeu.selection.cases_accessibles(jeu.unites, jeu.q_range, jeu.r_range)
                else:
                    print(f"🔴 ECHEC COMPETENCE SUR CASE VIDE")
                return
    
    # Clic ailleurs = annuler la sélection de compétence
    jeu.mode_selection_competence = False
    jeu.competence_en_cours = None
    jeu.cibles_possibles = []
    jeu.unite_utilisant_competence = None

def _get_valid_targets(jeu, comp_name, unite_source):
    """Retourne la liste des cibles valides pour une compétence."""
    valid_targets = []
    
    if co.peut_cibler_allie(comp_name):
        # Peut cibler les alliés
        for u in jeu.unites:
            if u.vivant and u.equipe == unite_source.equipe:
                valid_targets.append(u)
    
    if co.peut_cibler_ennemi(comp_name):
        # Peut cibler les ennemis
        for u in jeu.unites:
            if u.vivant and _are_enemies(unite_source.equipe, u.equipe, getattr(jeu, 'versus_mode', False)):
                valid_targets.append(u)
    
    if co.peut_cibler_case_vide(comp_name):
        # Peut cibler des cases vides adjacentes (pour cristalisation)
        print(f"   🔸 DEBUG: Recherche cases vides pour {comp_name}")
        print(f"   Position source: {unite_source.pos}")
        directions = [(-1,0), (1,0), (0,1), (0,-1), (1,-1), (-1,1)]
        q, r = unite_source.pos
        print(f"   Coordonnées source: q={q}, r={r}")
        
        for dq, dr in directions:
            case_pos = (q+dq, r+dr)
            case_q, case_r = case_pos
            print(f"   Vérification case: {case_pos}")
            # Vérifier que la case est dans les limites du jeu
            if (case_q in jeu.q_range and case_r in jeu.r_range):
                print(f"     - Dans les limites ✓")
                # Vérifier que la case est vide
                case_libre = True
                for u in jeu.unites:
                    if u.pos == case_pos and u.vivant:
                        case_libre = False
                        print(f"     - Occupée par {u.nom} ✗")
                        break
                
                if case_libre:
                    # Ajouter la position comme cible valide
                    valid_targets.append(case_pos)
                    print(f"     - Case vide trouvée ✓: {case_pos}")
                else:
                    print(f"     - Case occupée ✗")
            else:
                print(f"     - Hors limites ✗ (q_range: {jeu.q_range}, r_range: {jeu.r_range})")
    
    return valid_targets

def _are_enemies(equipe1, equipe2, versus_mode):
    """Détermine si deux équipes sont ennemies selon le mode de jeu"""
    if versus_mode:
        # En mode versus : joueur vs joueur2
        return (equipe1 == "joueur" and equipe2 == "joueur2") or (equipe1 == "joueur2" and equipe2 == "joueur")
    else:
        # Mode normal : joueur vs ennemi
        return (equipe1 == "joueur" and equipe2 == "ennemi") or (equipe1 == "ennemi" and equipe2 == "joueur")