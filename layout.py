import math
import pygame
from collections import deque

DIM_GRILLE = 7
MARGE = 12
SIDE_MIN_W = 260
TOP_H_RATIO = 0.07
BTN_H_RATIO = 0.06

# conversion axial -> pixel (pointy-topped)
def axial_to_pixel(q, r, size):
    x = size * (math.sqrt(3) * q + (math.sqrt(3) / 2) * r)
    y = size * (1.5 * r)
    return x, y

# wrapper qui utilise les attributs de l'instance jeu
def hex_to_pixel(jeu, q, r):
    x, y = axial_to_pixel(q, r, jeu.taille_hex)
    return int(x + jeu.offset_x), int(y + jeu.offset_y)

# recalcul du layout (mutates l'objet jeu)
def recalculer_layout(jeu):
    jeu.largeur, jeu.hauteur = jeu.screen.get_size()

    jeu.sidebar_w = max(SIDE_MIN_W, int(jeu.largeur * 0.23))
    jeu.top_h = max(40, int(jeu.hauteur * TOP_H_RATIO))

    grid_w = jeu.largeur - jeu.sidebar_w - 2 * MARGE
    grid_h = jeu.hauteur - jeu.top_h - 2 * MARGE
    grid_w = max(100, grid_w)
    grid_h = max(100, grid_h)

    # Vérifier que l'objet jeu a les attributs nécessaires
    if not hasattr(jeu, 'q_range') or not hasattr(jeu, 'r_range'):
        print("Warning: Objet Jeu incomplet, utilisation de valeurs par défaut")
        jeu.q_range = range(-1, 7)
        jeu.r_range = range(-1, 7)
    
    # taille d'hex (probe)
    size_probe = 1.0
    centers = []
    for q in jeu.q_range:
        for r in jeu.r_range:
            x,y = axial_to_pixel(q, r, size_probe)
            centers.append((x,y))
    minx = min(x for x,_ in centers)
    maxx = max(x for x,_ in centers)
    miny = min(y for _,y in centers)
    maxy = max(y for _,y in centers)

    env_w_unit = (maxx - minx) + 2.0
    env_h_unit = (maxy - miny) + 2.0

    sx = grid_w / env_w_unit
    sy = grid_h / env_h_unit
    jeu.taille_hex = max(8, int(min(sx, sy)))

    centers_px = []
    for q in jeu.q_range:
        for r in jeu.r_range:
            x,y = axial_to_pixel(q, r, jeu.taille_hex)
            centers_px.append((x,y))
    minx_px = min(x for x,_ in centers_px)
    maxx_px = max(x for x,_ in centers_px)
    miny_px = min(y for _,y in centers_px)
    maxy_px = max(y for _,y in centers_px)

    env_w = (maxx_px - minx_px) + 2 * jeu.taille_hex
    env_h = (maxy_px - miny_px) + 2 * jeu.taille_hex

    grid_left = MARGE
    grid_top = jeu.top_h + MARGE
    offset_left = grid_left + (grid_w - env_w) / 2.0 + jeu.taille_hex
    offset_top = grid_top + (grid_h - env_h) / 2.0 + jeu.taille_hex

    jeu.offset_x = offset_left - minx_px
    jeu.offset_y = offset_top - miny_px

    jeu.unit_radius = max(12, int(jeu.taille_hex * 0.45))

    jeu.font_small = pygame.font.SysFont(None, max(14, int(jeu.hauteur * 0.022)))
    jeu.font_norm = pygame.font.SysFont(None, max(18, int(jeu.hauteur * 0.026)))
    jeu.font_big = pygame.font.SysFont(None, max(22, int(jeu.hauteur * 0.03)))

    btn_w = int(jeu.sidebar_w * 0.8)
    btn_h = max(36, int(jeu.hauteur * BTN_H_RATIO))
    btn_x = jeu.largeur - jeu.sidebar_w + (jeu.sidebar_w - btn_w) // 2
    btn_y = jeu.hauteur - btn_h - MARGE
    jeu.btn_fin_tour = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    # Bouton Abandonner au-dessus du bouton Fin de tour
    btn_y_abandon = btn_y - btn_h - 10  # 10 pixels d'espacement
    jeu.btn_abandonner = pygame.Rect(btn_x, btn_y_abandon, btn_w, btn_h)

    jeu.info_panel = pygame.Rect(jeu.largeur - jeu.sidebar_w + MARGE,
                                  jeu.top_h + MARGE,
                                  jeu.sidebar_w - 2 * MARGE,
                                  int(jeu.hauteur * 0.25))

def pixel_to_hex(jeu, x, y):
    """Convertit des coordonnées pixel en coordonnées hexagonales"""
    # Inverse de hex_to_pixel
    grid_x = jeu.largeur - jeu.sidebar_w
    grid_y = jeu.hauteur - jeu.top_h
    
    center_x = grid_x // 2
    center_y = jeu.top_h + grid_y // 2
    
    # Conversion approximative - peut nécessiter des ajustements
    rel_x = x - center_x
    rel_y = y - center_y
    
    # Formules de conversion hexagonale inverse
    q = (2./3 * rel_x) / jeu.taille_hex
    r = (-1./3 * rel_x + math.sqrt(3)/3 * rel_y) / jeu.taille_hex
    
    return round(q), round(r)