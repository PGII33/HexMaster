import math
from layout import hex_to_pixel

class Animation:
    def __init__(self, type_, duree, unite, cible=None):
        self.type = type_          # ex: "attack"
        self.timer = duree         # temps restant en ms
        self.duree = duree         # durée totale
        self.unite = unite
        self.cible = cible

    def update(self, dt_ms):
        """Décrémente le timer et retourne True si l'anim est terminée"""
        self.timer -= dt_ms
        return self.timer <= 0

    def progress(self):
        """Retourne une progression 0 → 1"""
        return max(0, min(1, 1 - self.timer / self.duree))

def appliquer_effet(animation):
    """Applique les effets quand une anim se termine"""
    if animation.type == "attack" and animation.cible and animation.cible.vivant:
        animation.cible.pv -= animation.unite.dmg
        if animation.cible.pv <= 0:
            animation.cible.vivant = False

def dessiner_unite_animee(jeu, unite, x, y, base_color):
    """Dessine une unité avec animation éventuelle"""
    if unite.anim and unite.anim.type == "attack" and unite.anim.cible:
        cible = unite.anim.cible
        cx, cy = hex_to_pixel(jeu, cible.pos[0], cible.pos[1])
        progress = unite.anim.progress()
        if progress < 0.5:
            # avancer vers la cible
            f = progress * 2 * 0.2
        else:
            # revenir
            f = (1 - progress) * 2 * 0.2
        x = x + (cx - x) * f
        y = y + (cy - y) * f

    import pygame
    pygame.draw.circle(jeu.screen, base_color, (x,y), jeu.unit_radius)
    return x, y
