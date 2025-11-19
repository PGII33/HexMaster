import pygame
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

def dessiner_unite_animee(jeu, unite, x, y, base_color):
    """Dessine une unité avec animation éventuelle"""
    if unite.get_anim() and unite.get_anim().type == "attack" and unite.get_anim().cible:
        cible = unite.get_anim().cible
        cx, cy = hex_to_pixel(jeu, cible.get_pos()[0], cible.get_pos()[1])
        progress = unite.get_anim().progress()
        if progress < 0.5:
            # avancer vers la cible
            f = progress * 2 * 0.2
        else:
            # revenir
            f = (1 - progress) * 2 * 0.2
        x = x + (cx - x) * f
        y = y + (cy - y) * f

    pygame.draw.circle(jeu.screen, base_color, (x,y), jeu.unit_radius)
    return x, y
