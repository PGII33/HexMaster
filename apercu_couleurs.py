#!/usr/bin/env python3

import pygame
pygame.init()

# Test visuel des couleurs de faction
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Test Couleurs Factions")
font = pygame.font.SysFont(None, 24)

faction_colors = {
    "Morts-Vivants": (180, 150, 180),    # Violet pâle
    "Religieux": (255, 245, 200),        # Blanc doré  
    "Élémentaires": (150, 200, 150),     # Vert nature
    "Royaume": (200, 200, 255),          # Bleu royal
    "Chimères": (255, 180, 150)          # Orange/rouge
}

print("=== APERÇU VISUEL DES COULEURS ===")
print("Fenêtre ouverte avec aperçu des couleurs")
print("Fermez la fenêtre pour continuer...")

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((240, 240, 250))
    
    # Titre
    title = font.render("Couleurs des Factions", True, (0, 0, 0))
    screen.blit(title, (10, 10))
    
    # Afficher chaque couleur de faction
    y = 50
    for faction, color in faction_colors.items():
        # Rectangle coloré
        rect = pygame.Rect(20, y, 200, 60)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), rect, width=2, border_radius=8)
        
        # Nom de la faction
        text = font.render(faction, True, (0, 0, 0))
        screen.blit(text, (30, y + 20))
        
        # Code couleur
        color_text = font.render(f"RGB{color}", True, (0, 0, 0))
        screen.blit(color_text, (250, y + 20))
        
        y += 70
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Aperçu terminé.")
