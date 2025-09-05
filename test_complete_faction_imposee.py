#!/usr/bin/env python3
"""
Script de test complet pour la fonctionnalité faction imposée
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from niveau_structure import NiveauConfig, TypeRestriction
from unit_selector import UnitSelector
import pygame

def test_faction_imposee_modes():
    """Teste la faction imposée pour tous les modes de jeu"""
    
    # Configuration de test pour chaque mode
    test_configs = [
        {
            "type": TypeRestriction.FACTION_LIBRE,
            "nom": "Test Faction Libre",
            "faction_imposee": "Morts-Vivants"
        },
        {
            "type": TypeRestriction.FACTION_UNIQUE,
            "nom": "Test Faction Unique", 
            "faction_imposee": "Religieux"
        },
        {
            "type": TypeRestriction.FACTIONS_DEFINIES,
            "nom": "Test Factions Définies",
            "faction_imposee": "Morts-Vivants"
        }
    ]
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    for config in test_configs:
        print(f"\n=== Test {config['nom']} ===")
        
        # Créer la configuration de niveau
        niveau_config = NiveauConfig()
        niveau_config.type_restriction = config["type"]
        niveau_config.nom = config["nom"]
        niveau_config.faction_imposee = config["faction_imposee"]
        niveau_config.cp_disponible = 100
        niveau_config.max_unites = 5
        
        print(f"Type: {niveau_config.type_restriction}")
        print(f"Faction imposée: {niveau_config.faction_imposee}")
        
        # Créer le unit selector
        try:
            unit_selector = UnitSelector(
                screen=screen,
                mode="campagne",
                inventaire_joueur=[],
                type_restriction=niveau_config.type_restriction,
                unites_imposees=niveau_config.unites_imposees,
                factions_definies=niveau_config.factions_autorisees,
                faction_unique_requise=niveau_config.faction_unique_requise,
                cp_disponible=niveau_config.cp_disponible,
                max_unites=niveau_config.max_unites,
                faction_imposee=niveau_config.faction_imposee
            )
            
            # Tester les unités disponibles
            unites_disponibles = unit_selector._get_units_for_faction_imposee(niveau_config.faction_imposee)
            print(f"Unités disponibles: {len(unites_disponibles)}")
            
            # Afficher quelques exemples
            for i, unite_class in enumerate(unites_disponibles[:3]):
                # Créer une instance temporaire pour accéder aux attributs
                instance_temp = unite_class(equipe=0, pos=(0, 0))
                print(f"  - {instance_temp.nom} ({instance_temp.faction})")
            
            print("✅ Test réussi")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    pygame.quit()
    print("\n=== Tests terminés ===")

if __name__ == "__main__":
    test_faction_imposee_modes()
