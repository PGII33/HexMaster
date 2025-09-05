#!/usr/bin/env python3
"""
Test rapide du système d'ajout d'unités débloquées
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from niveau_structure import NiveauConfig, TypeRestriction
from level_builder import LevelBuilder
import pygame

def test_ajout_unites_cyclique():
    """Teste l'ajout cyclique d'unités sans freeze"""
    
    print("=== Test ajout d'unités cyclique ===\n")
    
    # Initialiser pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Créer un level builder
    builder = LevelBuilder(screen)
    
    # Initialiser avec un niveau vide
    builder.niveau_config = NiveauConfig()
    builder.niveau_config.nom = "Test Unités"
    
    print(f"État initial:")
    print(f"  Unités débloquées: {builder.niveau_config.unites_debloquees}")
    
    # Tester l'ajout de 5 unités
    print(f"\nAjout de 5 unités...")
    for i in range(5):
        print(f"\nÉtape {i+1}:")
        unites_avant = len(builder.niveau_config.unites_debloquees)
        builder.ajouter_unite_debloquee()
        unites_apres = len(builder.niveau_config.unites_debloquees)
        
        if unites_apres > unites_avant:
            derniere_unite = builder.niveau_config.unites_debloquees[-1]
            print(f"  ✅ Unité ajoutée: {derniere_unite}")
        else:
            print(f"  ❌ Aucune unité ajoutée")
    
    print(f"\nÉtat final:")
    print(f"  Nombre d'unités débloquées: {len(builder.niveau_config.unites_debloquees)}")
    print(f"  Liste: {builder.niveau_config.unites_debloquees}")
    
    # Test de retrait
    print(f"\nTest de retrait...")
    builder.retirer_unite_debloquee()
    print(f"  Après retrait: {len(builder.niveau_config.unites_debloquees)} unités")
    
    # Test d'effacement
    print(f"\nTest d'effacement...")
    builder.effacer_unites_debloquees()
    print(f"  Après effacement: {len(builder.niveau_config.unites_debloquees)} unités")
    
    pygame.quit()
    print(f"\n=== Test terminé avec succès ! ===")

if __name__ == "__main__":
    test_ajout_unites_cyclique()
