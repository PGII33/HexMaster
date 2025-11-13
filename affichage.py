import math
import pygame
from layout import hex_to_pixel
from animations import dessiner_unite_animee
from const import BLANC, NOIR, GRIS, VERT, ROUGE, VERT_VIE, BLEU_BOUCLIER, ROUGE_DMG_TOTAL, JAUNE_CIBLE
from const import D_AIDES
import competences as co
from utils_pos import est_a_portee

DO_PRINT = True


def dessiner(jeu):
    # Debug mode sélection
    if hasattr(jeu, 'mode_selection_competence') and jeu.mode_selection_competence and DO_PRINT:
        print(
            f"🎯 MODE SELECTION ACTIF: {jeu.competence_en_cours}, cibles: {len(jeu.cibles_possibles) if hasattr(jeu, 'cibles_possibles') else 0}")
        if hasattr(jeu, 'cibles_possibles'):
            print(f"   Cibles: {jeu.cibles_possibles}")

    jeu.screen.fill(BLANC)

    # Vérifier que les attributs de layout existent
    if not hasattr(jeu, 'largeur') or not hasattr(jeu, 'top_h'):
        # Recalculer le layout si les attributs manquent
        from layout import recalculer_layout
        recalculer_layout(jeu)

    # bandeau
    bandeau = pygame.Rect(0, 0, jeu.largeur, jeu.top_h)
    pygame.draw.rect(jeu.screen, (200, 200, 250), bandeau)

    # Affichage du tour selon le mode
    if getattr(jeu, 'versus_mode', False):
        if jeu.tour == "joueur":
            tour_text = "Tour du Joueur 1"
        elif jeu.tour == "joueur2":
            tour_text = "Tour du Joueur 2"
        else:
            tour_text = f"Tour du {jeu.tour}"
    else:
        tour_text = f"Tour du {jeu.tour}"

    # Affichage spécial si en mode sélection de compétence
    if hasattr(jeu, 'mode_selection_competence') and jeu.mode_selection_competence:
        tour_text = f"Sélectionnez une cible pour {jeu.competence_en_cours}"

    txt_tour = jeu.font_big.render(tour_text, True, NOIR)
    jeu.screen.blit(txt_tour, (jeu.largeur // 2 - txt_tour.get_width() // 2,
                               jeu.top_h // 2 - txt_tour.get_height() // 2))

    # separateur panneau lateral
    pygame.draw.line(jeu.screen, GRIS,
                     (jeu.largeur - jeu.sidebar_w, jeu.top_h),
                     (jeu.largeur - jeu.sidebar_w, jeu.hauteur), width=2)

    # grille - dessiner en deux passes pour assurer que le bleu soit au dessus
    # Première passe : hexagones gris
    for q in jeu.q_range:
        for r in jeu.r_range:
            if (q, r) not in jeu.deplacement_possibles:
                dessiner_hex(jeu, q, r, GRIS, max(
                    1, int(jeu.taille_hex * 0.05)))

    # Deuxième passe : hexagones bleus des déplacements possibles
    for q in jeu.q_range:
        for r in jeu.r_range:
            if (q, r) in jeu.deplacement_possibles:
                cout = jeu.deplacement_possibles[(q, r)]
                couleur = (50, 120, 255)  # Bleu uniforme
                epaisseur = max(2, int(jeu.taille_hex * 0.08))
                dessiner_hex(jeu, q, r, couleur, epaisseur)
                # Afficher le coût de déplacement
                cx, cy = hex_to_pixel(jeu, q, r)
                txtc = jeu.font_small.render(str(cout), True, (255, 255, 255))
                jeu.screen.blit(txtc, (cx - txtc.get_width() //
                                2, cy - txtc.get_height()//2))

            # Affichage des compétences (indépendant des mouvements)
            if (hasattr(jeu, 'mode_selection_competence') and jeu.mode_selection_competence and
                    hasattr(jeu, 'cibles_possibles') and (q, r) in jeu.cibles_possibles):
                # Afficher les cases ciblables par les compétences (ex: cristalisation)
                cx, cy = hex_to_pixel(jeu, q, r)

                # Dessiner un hexagone vert semi-transparent de la même taille
                points = []
                for i in range(6):
                    # Décalage de 30° pour avoir une arête au nord
                    angle = math.pi / 3 * i + math.pi / 6
                    px = cx + jeu.taille_hex * 0.9 * math.cos(angle)
                    py = cy + jeu.taille_hex * 0.9 * math.sin(angle)
                    points.append((px, py))

                # Créer une surface temporaire pour la transparence
                temp_surface = pygame.Surface(
                    (jeu.taille_hex * 2, jeu.taille_hex * 2), pygame.SRCALPHA)
                pygame.draw.polygon(temp_surface, (0, 255, 100, 120),
                                    [(p[0] - cx + jeu.taille_hex, p[1] - cy + jeu.taille_hex) for p in points])
                jeu.screen.blit(
                    temp_surface, (cx - jeu.taille_hex, cy - jeu.taille_hex))

                # Dessiner une forme de cristal spécifique pour la cristalisation
                if hasattr(jeu, 'competence_en_cours') and jeu.competence_en_cours == "cristalisation":
                    # Forme de cristal (losange avec des facettes)
                    cristal_size = 16
                    # Losange principal
                    points_cristal = [
                        (cx, cy - cristal_size),      # Haut
                        (cx + cristal_size//2, cy),    # Droite
                        (cx, cy + cristal_size),      # Bas
                        (cx - cristal_size//2, cy)     # Gauche
                    ]
                    pygame.draw.polygon(
                        jeu.screen, (255, 255, 255), points_cristal)
                    pygame.draw.polygon(
                        jeu.screen, (100, 255, 255), points_cristal, 2)

                    # Petites facettes internes pour effet cristal
                    facette_size = cristal_size // 3
                    pygame.draw.line(jeu.screen, (200, 255, 255),
                                     (cx - facette_size, cy - facette_size),
                                     (cx + facette_size, cy + facette_size), 2)
                    pygame.draw.line(jeu.screen, (200, 255, 255),
                                     (cx - facette_size, cy + facette_size),
                                     (cx + facette_size, cy - facette_size), 2)
                else:
                    # Pour autres compétences, simple croix
                    pygame.draw.circle(
                        jeu.screen, (255, 255, 255), (cx, cy), 12)
                    pygame.draw.circle(jeu.screen, (0, 255, 0), (cx, cy), 10)
                    pygame.draw.line(jeu.screen, (255, 255, 255),
                                     (cx-6, cy), (cx+6, cy), 3)
                    pygame.draw.line(jeu.screen, (255, 255, 255),
                                     (cx, cy-6), (cx, cy+6), 3)

    # unités
    for u in jeu.unites:
        # Afficher seulement les unités vivantes
        if not u.vivant:
            continue
        x, y = hex_to_pixel(jeu, u.pos[0], u.pos[1])

        # Couleurs selon l'équipe
        if u.equipe == 'joueur':
            color = VERT
        elif u.equipe == 'joueur2':
            color = (50, 50, 200)  # Bleu pour joueur 2
        else:
            color = ROUGE  # Rouge pour IA/ennemi

        # utilise la fonction d'animation
        x, y = dessiner_unite_animee(jeu, u, x, y, color)

        # Affichage vie (cercle vert et nombre de PV à gauche)
        if D_AIDES["PV"]:
            vie_txt = jeu.font_small.render(f"{u.get_pv()}", True, VERT_VIE)
            jeu.screen.blit(vie_txt, (x - jeu.unit_radius - 5 -
                            vie_txt.get_width(), y - jeu.unit_radius - 5))

        # Affichage du bouclier si présent
        if u.get_bouclier() > 0 and D_AIDES["BOUCLIER"]:
            # Dessiner un cercle bleu autour de l'unité pour le bouclier
            pygame.draw.circle(jeu.screen, BLEU_BOUCLIER,
                               (x, y), jeu.unit_radius + 8, 4)
            # Afficher le nombre de points de bouclier à droite
            bouclier_txt = jeu.font_small.render(
                f"{u.get_bouclier()}", True, BLEU_BOUCLIER)
            jeu.screen.blit(
                bouclier_txt, (x + jeu.unit_radius + 5, y - jeu.unit_radius - 5))

        # Affichage des dégâts totaux (rouge)
        if D_AIDES["DMG"]:
            dmg_tot_txt = jeu.font_small.render(
                f"{u.get_attaque_totale()}", True, ROUGE_DMG_TOTAL)
            jeu.screen.blit(dmg_tot_txt, (x - jeu.unit_radius -
                            5 - dmg_tot_txt.get_width(), y + jeu.unit_radius - 5))

        # Indicateur de cible possible pour compétence (unités)
        if (hasattr(jeu, 'mode_selection_competence') and
                jeu.mode_selection_competence and
                hasattr(jeu, 'cibles_possibles') and
                (u in jeu.cibles_possibles or u.pos in jeu.cibles_possibles)):
            # Cercle jaune pulsant plus visible
            pygame.draw.circle(jeu.screen, (255, 255, 0),
                               (x, y), jeu.unit_radius + 15, 6)
            pygame.draw.circle(jeu.screen, (255, 255, 100),
                               (x, y), jeu.unit_radius + 8, 3)

            # Ajouter un indicateur de soin (croix rouge)
            if jeu.competence_en_cours == "soin":
                # Croix de soin
                pygame.draw.line(jeu.screen, (255, 255, 255),
                                 (x-8, y), (x+8, y), 4)
                pygame.draw.line(jeu.screen, (255, 255, 255),
                                 (x, y-8), (x, y+8), 4)
                pygame.draw.line(jeu.screen, (255, 0, 0),
                                 (x-6, y), (x+6, y), 2)
                pygame.draw.line(jeu.screen, (255, 0, 0),
                                 (x, y-6), (x, y+6), 2)

        name_txt = jeu.font_small.render(u.get_nom(), True, NOIR)
        jeu.screen.blit(name_txt, (x - name_txt.get_width() //
                        2, y - jeu.unit_radius - name_txt.get_height() - 2))
        if jeu.selection == u:
            pygame.draw.circle(jeu.screen, color, (x, y), int(
                jeu.unit_radius * 1.25), width=max(2, int(jeu.taille_hex * 0.08)))

    # Indicateurs d'attaque (seulement si pas en mode sélection de compétence)
    if (jeu.selection and jeu.selection.equipe == jeu.tour and jeu.selection.attaque_restantes > 0 and
            not (hasattr(jeu, 'mode_selection_competence') and jeu.mode_selection_competence)):
        for u in jeu.unites:
            # Vérifier si c'est un ennemi selon le mode
            is_enemy = False
            if getattr(jeu, 'versus_mode', False):
                # Mode versus : joueur vs joueur2
                is_enemy = (jeu.selection.equipe == "joueur" and u.equipe == "joueur2") or \
                    (jeu.selection.equipe == "joueur2" and u.equipe == "joueur")
            else:
                # Mode normal : joueur vs ennemi
                is_enemy = u.equipe != jeu.selection.equipe
            if (
                u.vivant
                and is_enemy
                and est_a_portee(jeu.selection.pos, u.pos, jeu.selection.get_portee())
            ):
                # Dessiner un cercle rouge autour de u
                x, y = hex_to_pixel(jeu, u.pos[0], u.pos[1])
                pygame.draw.circle(jeu.screen, (220, 30, 30),
                                   (x, y), jeu.unit_radius+4, 3)

    # panneau info
    if jeu.selection:
        u = jeu.selection
        pygame.draw.rect(jeu.screen, (225, 225, 225),
                         jeu.info_panel, border_radius=8)
        lignes = [
            f"Nom: {u.get_nom()}",
            f"Faction: {u.get_faction()}",
            f"PV: {u.get_pv()}/{u.get_pv_max()}",
            f"Bouclier: {u.get_bouclier()}",
            f"DMG: {u.get_attaque_totale()}",
            f"Portée: {u.get_portee()}",
            f"Attaques restantes: {u.get_attaque_restantes()}/{u.get_attaque_max()}",
            f"PM restants: {u.pm}/{u.mv}",
            f"Equipe: {u.equipe}",
        ]

        if u.comp:
            lignes.append(f"Compétence: {u.comp}")
            # Ajouter l'information de cooldown si la compétence est active
            if hasattr(u, 'a_competence_active') and u.a_competence_active():
                cooldown_restant = getattr(u, 'cooldown_actuel', 0)

                if cooldown_restant > 0:
                    tours_text = "tour" if cooldown_restant == 1 else "tours"
                    lignes.append(f"Cooldown: {cooldown_restant} {tours_text}")
                else:
                    lignes.append(f"Compétence prête")

        for i, l in enumerate(lignes):
            color_text = NOIR
            txt = jeu.font_norm.render(l, True, color_text)
            jeu.screen.blit(txt, (jeu.info_panel.x + 10,
                            jeu.info_panel.y + 10 + i * (txt.get_height() + 4)))

        # Bouton pour compétence active si disponible (et pas en mode sélection)
        # Compétences qui ne nécessitent pas d'attaque restante
        attaque_necessaire = getattr(u, 'comp', '') in co.comp_attaque
        if (u.possede_competence_active() and
            (not attaque_necessaire or u.attaque_restantes > 0) and
                u.equipe == jeu.tour and not (hasattr(jeu, 'mode_selection_competence') and jeu.mode_selection_competence)):

            btn_y = jeu.info_panel.y + 10 + \
                len(lignes) * (jeu.font_norm.get_height() + 4) + 10
            btn_rect = pygame.Rect(jeu.info_panel.x + 10,
                                   btn_y, jeu.sidebar_w - 40, 30)

            # Vérifier le cooldown et l'utilisation de la compétence
            cooldown_restant = getattr(u, 'cooldown_actuel', 0)

            # Couleur du bouton selon la disponibilité
            if cooldown_restant == 0:
                btn_color = (100, 200, 100)  # Vert si utilisable
                text_color = NOIR
                btn_text = f"Utiliser {u.get_competence()}"
                if DO_PRINT:
                    print(
                        f"🟢 BOUTON COMPETENCE AFFICHE: {u.get_competence()} pour {u.nom}")
            else:
                # Gris si en cooldown ou déjà utilisée
                btn_color = (150, 150, 150)
                text_color = (100, 100, 100)

                # Toujours afficher "utilisé, dispo dans X tours" quand utilisée
                if cooldown_restant > 0:
                    tours_text = "tour" if cooldown_restant == 1 else "tours"
                    btn_text = f"{u.get_competence()} (utilisée, dispo dans {cooldown_restant} {tours_text})"
                else:
                    # Cooldown 0 = disponible au prochain tour
                    btn_text = f"{u.get_competence()} (utilisée, dispo dans 1 tour)"

            pygame.draw.rect(jeu.screen, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(jeu.screen, NOIR, btn_rect,
                             width=2, border_radius=5)

            btn_text_surface = jeu.font_small.render(
                btn_text, True, text_color)
            text_x = btn_rect.centerx - btn_text_surface.get_width() // 2
            text_y = btn_rect.centery - btn_text_surface.get_height() // 2
            jeu.screen.blit(btn_text_surface, (text_x, text_y))

            # Stocker le rectangle pour la détection de clic seulement si utilisable
            if cooldown_restant == 0:
                jeu.competence_btn_rect = btn_rect
                if DO_PRINT:
                    print(f"🟢 BOUTON CLIQUABLE DEFINI: {btn_rect}")
            else:
                jeu.competence_btn_rect = None
                if DO_PRINT:
                    print(f"🔴 BOUTON NON CLIQUABLE: {u.get_competence()}")
        else:
            jeu.competence_btn_rect = None

    # bouton fin de tour
    pygame.draw.rect(jeu.screen, (100, 100, 250),
                     jeu.btn_fin_tour, border_radius=8)
    txt_btn = jeu.font_norm.render("Fin de tour", True, (255, 255, 255))
    jeu.screen.blit(txt_btn, (jeu.btn_fin_tour.centerx - txt_btn.get_width() // 2,
                              jeu.btn_fin_tour.centery - txt_btn.get_height() // 2))

    # bouton abandonner
    if hasattr(jeu, 'btn_abandonner'):
        pygame.draw.rect(jeu.screen, (200, 50, 50),
                         jeu.btn_abandonner, border_radius=8)
        txt_abandon = jeu.font_norm.render("Abandonner", True, (255, 255, 255))
        jeu.screen.blit(txt_abandon, (jeu.btn_abandonner.centerx - txt_abandon.get_width() // 2,
                                      jeu.btn_abandonner.centery - txt_abandon.get_height() // 2))

    # Menu de fin de combat (affiché par-dessus tout le reste)
    dessiner_menu_fin_combat(jeu)


def dessiner_hex(jeu, q, r, couleur, largeur=1):
    x, y = hex_to_pixel(jeu, q, r)
    pts = []
    for i in range(6):
        ang = math.pi / 3 * i + math.pi / 6
        px = x + jeu.taille_hex * math.cos(ang)
        py = y + jeu.taille_hex * math.sin(ang)
        pts.append((px, py))
    pygame.draw.polygon(jeu.screen, couleur, pts, largeur)


def dessiner_menu_fin_combat(jeu):
    """Dessine le menu de fin de combat avec les résultats et récompenses"""
    if not hasattr(jeu, 'show_end_menu') or not jeu.show_end_menu:
        return

    # Overlay semi-transparent
    overlay = pygame.Surface((jeu.largeur, jeu.hauteur))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    jeu.screen.blit(overlay, (0, 0))

    # Fenêtre principale du menu
    menu_width = 500
    menu_height = 400
    menu_x = (jeu.largeur - menu_width) // 2
    menu_y = (jeu.hauteur - menu_height) // 2

    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    pygame.draw.rect(jeu.screen, (250, 250, 250), menu_rect, border_radius=15)
    pygame.draw.rect(jeu.screen, (100, 100, 100),
                     menu_rect, width=3, border_radius=15)

    # Titre du menu
    titre = jeu.get_titre_fin_combat()
    couleur_titre = (50, 150, 50) if jeu.victoire else (200, 50, 50)
    txt_titre = jeu.font_big.render(titre, True, couleur_titre)
    titre_y = menu_y + 30
    jeu.screen.blit(
        txt_titre, (menu_x + (menu_width - txt_titre.get_width()) // 2, titre_y))

    # Section récompenses (seulement si victoire et qu'il y a des récompenses)
    if jeu.victoire and (jeu.recompenses['pa'] > 0 or jeu.recompenses['cp'] > 0 or jeu.recompenses['unites']):
        recomp_y = titre_y + 60
        txt_recomp = jeu.font_norm.render("Récompenses :", True, NOIR)
        jeu.screen.blit(txt_recomp, (menu_x + 50, recomp_y))

        current_y = recomp_y + 40

        # PA (seulement si > 0)
        if jeu.recompenses['pa'] > 0:
            txt_pa = jeu.font_norm.render(
                f"PA : +{jeu.recompenses['pa']}", True, (0, 100, 200))
            jeu.screen.blit(txt_pa, (menu_x + 70, current_y))
            current_y += 30

        # CP (seulement si > 0)
        if jeu.recompenses['cp'] > 0:
            txt_cp = jeu.font_norm.render(
                f"CP : +{jeu.recompenses['cp']}", True, (200, 100, 0))
            jeu.screen.blit(txt_cp, (menu_x + 70, current_y))
            current_y += 30

        # Nouvelles unités
        if jeu.recompenses['unites']:
            for i, unite in enumerate(jeu.recompenses['unites']):
                txt_unite = jeu.font_norm.render(
                    f"Nouvelle unité : {unite}", True, (100, 150, 100))
                jeu.screen.blit(txt_unite, (menu_x + 70, current_y + i * 25))
    elif not jeu.victoire:
        # Message de défaite sans récompenses
        defaite_y = titre_y + 80
        txt_defaite = jeu.font_norm.render(
            "Aucune récompense accordée", True, (150, 150, 150))
        jeu.screen.blit(txt_defaite, (menu_x + (menu_width -
                        txt_defaite.get_width()) // 2, defaite_y))

    # Bouton Retour au menu principal
    btn_width = 200
    btn_height = 50
    btn_x = menu_x + (menu_width - btn_width) // 2
    btn_y = menu_y + menu_height - 80

    jeu.btn_retour_menu = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
    pygame.draw.rect(jeu.screen, (100, 150, 200),
                     jeu.btn_retour_menu, border_radius=8)

    txt_btn = jeu.font_norm.render("Menu Principal", True, BLANC)
    jeu.screen.blit(txt_btn, (jeu.btn_retour_menu.centerx - txt_btn.get_width() // 2,
                              jeu.btn_retour_menu.centery - txt_btn.get_height() // 2))
