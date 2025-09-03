import math
import pygame
from layout import hex_to_pixel
from animations import dessiner_unite_animee

BLANC = (255,255,255)
NOIR = (0,0,0)
GRIS = (180,180,180)
VERT = (50,200,50)
ROUGE = (200,50,50)

def dessiner(jeu):
    jeu.screen.fill(BLANC)

    # bandeau
    bandeau = pygame.Rect(0, 0, jeu.largeur, jeu.top_h)
    pygame.draw.rect(jeu.screen, (200,200,250), bandeau)
    txt_tour = jeu.font_big.render(f"Tour du {jeu.tour}", True, NOIR)
    jeu.screen.blit(txt_tour, (jeu.largeur // 2 - txt_tour.get_width() // 2,
                                jeu.top_h // 2 - txt_tour.get_height() // 2))

    # separateur panneau lateral
    pygame.draw.line(jeu.screen, GRIS,
                     (jeu.largeur - jeu.sidebar_w, jeu.top_h),
                     (jeu.largeur - jeu.sidebar_w, jeu.hauteur), width=2)

    # grille
    for q in jeu.q_range:
        for r in jeu.r_range:
            if (q,r) in jeu.deplacement_possibles:
                cout = jeu.deplacement_possibles[(q,r)]
                intensite = max(70, 250 - cout * 40)
                couleur = (50,50,intensite)
                dessiner_hex(jeu, q, r, couleur, max(2, int(jeu.taille_hex * 0.08)))
                cx, cy = hex_to_pixel(jeu, q, r)
                txtc = jeu.font_small.render(str(cout), True, (255,255,255))
                jeu.screen.blit(txtc, (cx - txtc.get_width()//2, cy - txtc.get_height()//2))
            else:
                dessiner_hex(jeu, q, r, GRIS, max(1, int(jeu.taille_hex * 0.05)))

    # unités
    for u in jeu.unites:
        if not u.vivant:
            continue
        x,y = hex_to_pixel(jeu, u.pos[0], u.pos[1])
        color = VERT if u.equipe == 'joueur' else ROUGE

        # utilise la fonction d’animation
        x, y = dessiner_unite_animee(jeu, u, x, y, color)

        name_txt = jeu.font_small.render(u.get_nom(), True, NOIR)
        jeu.screen.blit(name_txt, (x - name_txt.get_width() // 2, y - jeu.unit_radius - name_txt.get_height() - 2))
        if jeu.selection == u:
            pygame.draw.circle(jeu.screen, color, (x,y), int(jeu.unit_radius * 1.25), width=max(2, int(jeu.taille_hex * 0.08)))

    if jeu.selection and jeu.selection.equipe == jeu.tour and jeu.selection.attaque_restantes > 0:
        for u in jeu.unites:
            if (
                u.vivant
                and u.equipe != jeu.selection.equipe
                and jeu.selection.est_a_portee(u)
            ):
                # Dessiner un cercle rouge autour de u
                x, y = hex_to_pixel(jeu, u.pos[0], u.pos[1])
                pygame.draw.circle(jeu.screen, (220, 30, 30), (x, y), jeu.unit_radius+4, 3)

    # panneau info
    if jeu.selection:
        u = jeu.selection
        pygame.draw.rect(jeu.screen, (225,225,225), jeu.info_panel, border_radius=8)
        lignes = [
            f"Nom: {u.nom}",
            f"Faction: {u.faction}",
            f"PV: {u.pv}",
            f"DMG: {u.dmg}",
            f"Portée: {u.portee}",
            f"Attaques restantes: {u.attaque_restantes}/{u.attaque_max}",
            f"PM restants: {u.pm}/{u.mv}",
            f"Equipe: {u.equipe}",
        ]
        if u.comp:
            lignes.append(f"Compétence: {u.comp}")
        for i, l in enumerate(lignes):
            txt = jeu.font_norm.render(l, True, NOIR)
            jeu.screen.blit(txt, (jeu.info_panel.x + 10, jeu.info_panel.y + 10 + i * (txt.get_height() + 4)))

    # bouton fin de tour
    pygame.draw.rect(jeu.screen, (100,100,250), jeu.btn_fin_tour, border_radius=8)
    txt_btn = jeu.font_norm.render("Fin de tour", True, (255,255,255))
    jeu.screen.blit(txt_btn, (jeu.btn_fin_tour.centerx - txt_btn.get_width() // 2,
                               jeu.btn_fin_tour.centery - txt_btn.get_height() // 2))

def dessiner_hex(jeu, q, r, couleur, largeur=1):
    x,y = hex_to_pixel(jeu, q, r)
    pts = []
    for i in range(6):
        ang = math.pi / 3 * i + math.pi / 6
        px = x + jeu.taille_hex * math.cos(ang)
        py = y + jeu.taille_hex * math.sin(ang)
        pts.append((px, py))
    pygame.draw.polygon(jeu.screen, couleur, pts, largeur)
