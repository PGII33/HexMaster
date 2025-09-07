#!/usr/bin/env python3
"""
Couleurs centralisées pour les factions du jeu.
Ce fichier définit les couleurs utilisées partout dans le jeu pour identifier les factions.
"""

# Couleurs par faction - utilisées dans toute l'interface
FACTION_COLORS = {
    "Morts-Vivants": (220, 210, 220),    # Violet très pâle (doux pour les yeux)
    "Religieux": (255, 245, 200),        # Blanc doré (pur/sacré)
    "Élémentaires": (150, 200, 150),     # Vert nature (naturel/élémentaire)
    "Royaume": (200, 200, 255),          # Bleu royal (noble/royal)
    "Chimères": (255, 180, 150)          # Orange/rouge (sauvage/hybride)
}

def get_faction_color(faction_name):
    """Retourne la couleur RGB pour une faction donnée."""
    return FACTION_COLORS.get(faction_name, (240, 240, 240))  # Gris clair par défaut
