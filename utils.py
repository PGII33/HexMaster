import pygame
import sys
import os

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
        import tempfile
        user_dir = os.path.join(tempfile.gettempdir(), "HexMaster")
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, relative_path)
    else:
        # En développement, utiliser le répertoire courant
        return relative_path

class Button:
    def __init__(self, rect, text, action, font, base_color=(100,100,250), hover_color=(140,140,250), text_color=(255,255,255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()