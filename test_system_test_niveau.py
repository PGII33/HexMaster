#!/usr/bin/env python3
"""
Test du système de test de niveau
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from niveau_structure import NiveauConfig, TypeRestriction
from level_builder import LevelBuilder
import pygame
import unites

def test_system_test_niveau():
    """Teste le système de test de niveau avec contraintes"""
    
    print("=== Test du système de test de niveau ===\n")
    
    # Initialiser pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Créer un level builder
    builder = LevelBuilder(screen)
    
    # Test 1: Niveau avec unités imposées
    print("1. Test avec unités imposées...")
    builder.niveau_config = NiveauConfig()
    builder.niveau_config.nom = "Test Unités Imposées"
    builder.niveau_config.type_restriction = TypeRestriction.UNITES_IMPOSEES
    builder.niveau_config.unites_imposees = [
        (unites.Vampire, (0, 0)),
        (unites.Ange, (1, 0))
    ]
    builder.niveau_config.unites_ennemis = [
        (unites.Goule, (4, 4)),
        (unites.Clerc, (5, 4))
    ]
    
    # Tester la création d'inventaire
    inventaire = builder._creer_inventaire_test()
    print(f"   Inventaire créé: {len(inventaire)} unités")
    print(f"   Types uniques: {len(set(inventaire))}")
    
    # Test 2: Niveau avec faction imposée
    print(f"\n2. Test avec faction imposée...")
    builder.niveau_config = NiveauConfig()
    builder.niveau_config.nom = "Test Faction Imposée"
    builder.niveau_config.type_restriction = TypeRestriction.FACTION_LIBRE
    builder.niveau_config.faction_imposee = "Morts-Vivants"
    builder.niveau_config.cp_disponible = 8
    builder.niveau_config.max_unites = 4
    builder.niveau_config.unites_ennemis = [
        (unites.Ange, (4, 4)),
        (unites.Paladin, (5, 4))
    ]
    
    # Valider la configuration
    valide, erreurs = builder.niveau_config.valider()
    print(f"   Configuration valide: {valide}")
    if not valide:
        for erreur in erreurs:
            print(f"     - {erreur}")
    
    # Test 3: Niveau avec faction unique
    print(f"\n3. Test avec faction unique...")
    builder.niveau_config = NiveauConfig()
    builder.niveau_config.nom = "Test Faction Unique"
    builder.niveau_config.type_restriction = TypeRestriction.FACTION_UNIQUE
    builder.niveau_config.faction_unique_requise = True
    builder.niveau_config.cp_disponible = 10
    builder.niveau_config.max_unites = 5
    builder.niveau_config.unites_ennemis = [
        (unites.Vampire, (4, 4)),
        (unites.Liche, (5, 4)),
        (unites.Zombie, (4, 5))
    ]
    
    valide, erreurs = builder.niveau_config.valider()
    print(f"   Configuration valide: {valide}")
    
    # Test 4: Validation des contraintes
    print(f"\n4. Test de validation...")
    configs_test = [
        {
            "nom": "Niveau sans nom",
            "setup": lambda cfg: setattr(cfg, 'nom', ''),
            "devrait_echouer": True
        },
        {
            "nom": "CP négatifs",
            "setup": lambda cfg: setattr(cfg, 'cp_disponible', -1),
            "devrait_echouer": True
        },
        {
            "nom": "Configuration valide",
            "setup": lambda cfg: None,
            "devrait_echouer": False
        }
    ]
    
    for test_config in configs_test:
        print(f"   Test: {test_config['nom']}")
        test_niveau = NiveauConfig()
        test_niveau.nom = "Test Validation"
        test_niveau.unites_ennemis = [(unites.Goule, (4, 4))]
        
        test_config["setup"](test_niveau)
        
        valide, erreurs = test_niveau.valider()
        if test_config["devrait_echouer"]:
            if not valide:
                print(f"     ✅ Échec attendu détecté: {erreurs[0] if erreurs else 'Erreur'}")
            else:
                print(f"     ❌ Devrait échouer mais réussit")
        else:
            if valide:
                print(f"     ✅ Validation réussie")
            else:
                print(f"     ❌ Validation échoue: {erreurs}")
    
    print(f"\n=== Test terminé ===")
    print(f"Le système de test de niveau est prêt à fonctionner !")
    print(f"Utilisation: Créer un niveau complet → Cliquer 'Tester Niveau'")
    
    pygame.quit()

if __name__ == "__main__":
    test_system_test_niveau()
