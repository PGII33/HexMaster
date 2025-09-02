import pygame
import sys
from utils import Button
import unites

class HexArène:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 28)

        self.selected_units = []
        self.max_units = 5  # limite d'unités du joueur
        self.running = True
        self.unit_positions = []  # contiendra (classe, pos) après placement

    # --- Flow principal ---
    def run_flow(self, available_units):
        if not self.selected_units:
            self._select_units_phase(available_units)
        self._placement_phase()
        enemies = self._generate_enemies()
        return self.unit_positions, enemies

    # --- Sélection des unités ---
    def _select_units_phase(self, available_units):
        """
        Écran de sélection des unités avec boutons Retour et Valider.
        """
        self.selected_units = []
        self.running = True
        self.cancelled = False  # pour savoir si on a cliqué sur Retour

        font = pygame.font.SysFont(None, 28)
        screen_w, screen_h = self.screen.get_size()

        retour_btn = Button(
            (20, screen_h-70, 160, 44),
            "Retour",
            lambda: self._quit_selection(cancel=True),
            font
        )
        valider_btn = Button(
            (screen_w-180, screen_h-70, 160, 44),
            "Valider",
            lambda: self._quit_selection(cancel=False),
            font
        )

        margin = 20
        card_w, card_h = 220, 120

        while self.running:
            self.screen.fill((250, 245, 230))
            titre = self.font_big.render("Sélection des unités", True, (30,30,60))
            self.screen.blit(titre, (40, 30))

            # dessiner les cartes
            x, y = margin, 120
            rects = {}
            for cls in available_units:
                rect = pygame.Rect(x, y, card_w, card_h)
                rects[cls] = rect

                pygame.draw.rect(self.screen, (235,235,235), rect, border_radius=12)
                pygame.draw.rect(self.screen, (0,0,0), rect, width=2, border_radius=12)

                # Récupérer le nom depuis une instance temporaire
                tmp_instance = cls("joueur", (0,0))
                unit_name = tmp_instance.get_nom()
                
                txt = self.font_small.render(unit_name, True, (0,0,0))
                self.screen.blit(txt, (x+10, y+10))

                count = self.selected_units.count(cls)
                if count > 0:
                    c_txt = self.font_small.render(f"x{count}", True, (200,0,0))
                    self.screen.blit(c_txt, (x+card_w-40, y+10))

                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(self.screen, (50,150,250), rect, width=3, border_radius=12)

                # avancer en grille
                x += card_w + margin
                if x + card_w > self.screen.get_width() - margin:
                    x = margin
                    y += card_h + margin

            # boutons
            retour_btn.draw(self.screen)
            valider_btn.draw(self.screen)

            # ---------------- EVENTS ----------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    retour_btn.rect.topleft = (20, self.screen.get_height()-70)
                    valider_btn.rect.topleft = (self.screen.get_width()-180, self.screen.get_height()-70)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for cls, rect in rects.items():
                        if rect.collidepoint(event.pos):
                            if len(self.selected_units) < self.max_units:
                                self.selected_units.append(cls)
                    retour_btn.handle_event(event)
                    valider_btn.handle_event(event)

            pygame.display.flip()

    def _quit_selection(self, cancel=False):
        """Ferme l’écran de sélection avec ou sans validation."""
        self.cancelled = cancel
        self.running = False

    # --- Placement automatique des unités ---
    def _placement_phase(self):
        self.unit_positions = []
        start_positions = [(0,0), (1,0), (2,0), (0,1), (1,1)]
        for i, cls in enumerate(self.selected_units[:self.max_units]):
            self.unit_positions.append((cls, start_positions[i]))

    # --- Génération ennemis ---
    def _generate_enemies(self):
        enemies = []
        start_positions = [(5,5), (5,6), (6,5), (6,6), (6,4)]
        for i, _ in enumerate(self.selected_units[:self.max_units]):
            enemies.append((unites.Squelette, start_positions[i]))
        return enemies
