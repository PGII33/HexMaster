""" Utilitaires divers pour HexaMaster """
import tempfile
import sys
import os
import pygame
# pylint: disable=too-many-arguments disable=too-many-positional-arguments
# pylint: disable=line-too-long


def resource_path(relative_path):
    """Obtient le chemin absolu vers une ressource, fonctionne avec PyInstaller"""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Mode développement normal
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def ensure_writable_path(relative_path):
    """Obtient un chemin accessible en écriture, même dans un exécutable"""
    if hasattr(sys, '_MEIPASS'):
        # Dans un exécutable, utiliser le répertoire utilisateur
        user_dir = os.path.join(tempfile.gettempdir(), "HexMaster")
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, relative_path)
    else:
        # En développement, utiliser le répertoire courant
        return relative_path


class Button:
    """ Classe pour un bouton interactif dans Pygame """

    def __init__(self, rect, text, action, font, base_color=(100, 100, 250), hover_color=(140, 140, 250), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface):
        """ Dessine le bouton sur la surface donnée """
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(
            mouse) else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, (self.rect.centerx - txt.get_width() //
                     2, self.rect.centery - txt.get_height()//2))

    def handle_event(self, event):
        """ Gère les événements de la souris pour le bouton """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False


def draw_bandeau(screen, screen_w, bandeau_h, margin, font, title_font, text, titre="Boutique", secret_click_rect_container=None):
    """
    Dessine le bandeau en haut de l'écran avec le titre et le solde PA.
    Retourne le rect du solde PA (pour gestion du clic secret).
    secret_click_rect_container: si fourni (liste d'un seul élément), le rect sera stocké dedans[0].
    """
    bandeau_rect = pygame.Rect(0, 0, screen_w, bandeau_h)
    pygame.draw.rect(screen, (220, 220, 240), bandeau_rect)
    pygame.draw.line(screen, (120, 120, 160), (0, bandeau_h),
                     (screen_w, bandeau_h), 3)

    titre_surf = title_font.render(titre, True, (30, 30, 60))
    screen.blit(titre_surf, (margin, (bandeau_h - titre_surf.get_height()) // 2))

    solde = font.render(text, True, (0, 0, 0))
    solde_x = screen_w - solde.get_width() - 20
    solde_y = (bandeau_h - solde.get_height()) // 2
    solde_rect = pygame.Rect(
        solde_x, solde_y, solde.get_width(), solde.get_height())
    screen.blit(solde, (solde_x, solde_y))
    if secret_click_rect_container is not None:
        secret_click_rect_container[0] = solde_rect
    return solde_rect


def handle_scroll_events(events, scroll_y, scroll_speed, max_scroll):
    """
    Gère le scroll vertical (MOUSEWHEEL) et bloque le scroll si la souris est sur le bandeau (optionnel).
    Retourne le nouveau scroll_y.
    """
    for event in events:
        if event.type == 1027:  # pygame.MOUSEWHEEL
            scroll_y -= event.y * scroll_speed
            scroll_y = max(0, min(scroll_y, max_scroll))
    return scroll_y


def wrap_text(text, font, max_width):
    """
    Découpe le texte en lignes pour ne pas dépasser max_width (en pixels) avec la police donnée.
    """
    if not text:
        return [""]
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def get_grid_specs(screen, CLASSES_UNITES, get_card_height_func, min_card_w=200, min_margin=20):
    """
    Calcule la grille (largeur, hauteur, margin, colonnes, largeur carte, start_y, hauteur carte)
    en prenant en compte toutes les unités (pour une taille de carte constante).
    get_card_height_func(card_w, cls) doit retourner la hauteur de carte pour une classe donnée et une largeur donnée.
    """
    screen_w, screen_h = screen.get_size()
    margin = max(min_margin, screen_w // 40)
    cols = 3
    card_w = (screen_w - margin * (cols + 1)) // cols
    if card_w < 260:
        cols = 2
        card_w = (screen_w - margin * (cols + 1)) // cols
    if card_w < 220:
        cols = 1
        card_w = (screen_w - margin * (cols + 1)) // cols
    card_w = max(min_card_w, card_w)
    start_y = max(100, int(0.12 * screen_h))

    # Calcul de la hauteur maximale de carte sur toutes les unités
    max_card_h = 0
    for cls in CLASSES_UNITES:
        h = get_card_height_func(card_w, cls)
        max_card_h = max(max_card_h, h)

    return screen_w, screen_h, margin, cols, card_w, start_y, max_card_h


def point_dans_polygone(px, py, pts):
    """ Vérifie si un point (px, py) est à l'intérieur d'un polygone défini par une liste de points pts """
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside
