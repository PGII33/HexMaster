import pygame
import sys
from utils import Button
import unites
from placement import PlacementPhase
from unit_selector import UnitSelector

class HexArène:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 28)

        self.selected_units = []
        self.max_units = 14
        self.running = True
        self.unit_positions = []  # contiendra (classe, pos) après placement

    # --- Flow principal ---
    def run_flow(self, available_units):
        # Utiliser le nouveau UnitSelector au lieu de l'ancienne méthode
        selector = UnitSelector(self.screen, "hexarene")
        self.selected_units = selector.run()
        
        if self.selected_units is None:  # Annulé
            return None, None
        
        # Phase de placement
        placement = PlacementPhase(self.screen, self.selected_units)
        unit_positions = placement.run()
        
        if unit_positions is None:  # Annulé
            return None, None
        
        enemies = self._generate_enemies()
        return unit_positions, enemies

    # --- Génération ennemis ---
    def _generate_enemies(self):
        enemies = []
        # Positions de spawn ennemies (zone rouge : r = 4, 5, 6)
        enemy_positions = []
        for r in [4, 5, 6]:
            for q in range(-1, 7):
                enemy_positions.append((q, r))
        
        # Générer autant d'ennemis que le joueur a d'unités placées
        num_enemies = len(self.selected_units)
        
        # Classes d'ennemis disponibles
        enemy_classes = [unites.Squelette, unites.Goule, unites.Spectre, unites.Zombie, unites.Vampire]
        
        import random
        for i in range(min(num_enemies, len(enemy_positions))):
            enemy_class = random.choice(enemy_classes)
            enemies.append((enemy_class, enemy_positions[i]))
        
        return enemies
