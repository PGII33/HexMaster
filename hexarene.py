# fichier: hexarene.py
import pygame
from utils import Button

class HexArène:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 28)

        self.buttons = []
        self.selected_units = []
        self.max_units = 5  # limite d'unités du joueur
        self.running = True
        self.unit_positions = []  # contiendra (nom, pos) après placement

    # --- Flow principal ---
    def run_flow(self):
        # pour HexArène on prend directement les unités sélectionnées (depuis inventaire)
        if not self.selected_units:
            self._select_units_phase()
        self._placement_phase()
        enemies = self._generate_enemies()
        return self.unit_positions, enemies

    # --- Sélection des unités (optionnel) ---
    def _select_units_phase(self):
        # dans la version actuelle, sélection par clic sur inventaire ou automatique
        # ici on met un flow très simple (démo)
        self.running = False

    # --- Placement automatique des unités ---
    def _placement_phase(self):
        self.unit_positions = []
        start_positions = [(0,0), (1,0), (2,0), (0,1), (1,1)]
        for i, nom in enumerate(self.selected_units[:self.max_units]):
            self.unit_positions.append((nom, start_positions[i]))

    # --- Génération ennemis ---
    def _generate_enemies(self):
        enemies = []
        start_positions = [(5,5), (5,6), (6,5), (6,6), (6,4)]
        for i, nom in enumerate(self.selected_units[:self.max_units]):
            enemies.append(("Squelette", start_positions[i]))
        return enemies
