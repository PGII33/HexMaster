#!/usr/bin/env python3
"""
Démonstration complète du menu de fin de combat
"""

import pygame
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from jeu import Jeu
import unites

def demo_menu_fin_combat():
    """Démonstration interactive du menu de fin de combat"""
    pygame.init()
    screen = pygame.display.set_mode((1200, 900))
    pygame.display.set_caption("🎮 Démonstration Menu Fin de Combat")
    
    # Créer un jeu avec des unités
    player_units = [
        (unites.Guerrier, (2, 2)),
        (unites.Archer, (3, 2)),
        (unites.Clerc, (4, 2))
    ]
    
    enemy_units = [
        (unites.Goule, (8, 5)),
        (unites.Squelette, (9, 5))
    ]
    
    # Mode HexArène avec faction
    jeu = Jeu(
        screen=screen,
        initial_player_units=player_units,
        initial_enemy_units=enemy_units,
        enable_placement=False,
        mode_hexarene=True,
        hexarene_mode_type="faction",
        faction_hexarene="Religieux"
    )
    
    print("🎮 Démonstration du Menu de Fin de Combat")
    print("=" * 50)
    print("Instructions:")
    print("- V : Simuler une VICTOIRE")
    print("- D : Simuler une DÉFAITE")
    print("- R : Retour au jeu normal")
    print("- ESC : Quitter")
    print("- Clic sur 'Menu Principal' : Retour au menu")
    print("=" * 50)
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_v:
                    print("🏆 Simulation VICTOIRE")
                    jeu.activer_menu_fin_combat(True)
                elif event.key == pygame.K_d:
                    print("💀 Simulation DÉFAITE")
                    jeu.activer_menu_fin_combat(False)
                elif event.key == pygame.K_r:
                    print("🔄 Retour au jeu")
                    jeu.show_end_menu = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Gestion des clics
                import input_mod
                try:
                    input_mod.handle_click(jeu, event.pos[0], event.pos[1])
                except SystemExit:
                    print("🔄 Retour au menu principal demandé")
                    running = False
        
        # Affichage
        import affichage
        affichage.dessiner(jeu)
        
        # Instructions à l'écran si pas de menu affiché
        if not getattr(jeu, 'show_end_menu', False):
            font = pygame.font.Font(None, 24)
            instructions = [
                "Appuyez sur V pour VICTOIRE, D pour DÉFAITE",
                "R pour revenir au jeu, ESC pour quitter"
            ]
            for i, txt in enumerate(instructions):
                surface = font.render(txt, True, (0, 0, 0))
                screen.blit(surface, (20, 20 + i * 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("🎮 Démonstration terminée")

if __name__ == "__main__":
    demo_menu_fin_combat()
