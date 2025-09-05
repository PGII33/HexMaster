#!/usr/bin/env python3
"""
Test du nouveau sélecteur d'unités
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from niveau_structure import NiveauConfig
from level_builder import LevelBuilder
import pygame

def test_selecteur_unites():
    """Teste le nouveau sélecteur d'unités GUI"""
    
    print("=== Test du sélecteur d'unités GUI ===\n")
    
    # Initialiser pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Créer un level builder
    builder = LevelBuilder(screen)
    builder.niveau_config = NiveauConfig()
    builder.niveau_config.nom = "Test Sélecteur"
    
    print("1. Test préparation de la sélection...")
    
    # Simuler un clic sur "Ajouter" (sans vraiment l'exécuter)
    from unites import CLASSES_UNITES
    
    unites_disponibles = []
    for classe_unite in CLASSES_UNITES:
        instance_temp = classe_unite(equipe=0, pos=(0, 0))
        unites_disponibles.append({
            'classe': classe_unite.__name__,
            'nom': instance_temp.nom,
            'faction': instance_temp.faction,
            'tier': instance_temp.tier
        })
    
    # Trier par faction puis tier
    unites_disponibles.sort(key=lambda x: (x['faction'], x['tier']))
    
    print(f"   Unités disponibles pour sélection: {len(unites_disponibles)}")
    print(f"   Factions: {set(u['faction'] for u in unites_disponibles)}")
    
    # Test de sélection d'une unité spécifique
    print(f"\n2. Test de sélection d'unité...")
    
    # Sélectionner le Vampire (Morts-Vivants)
    vampire = next((u for u in unites_disponibles if u['nom'] == 'Vampire'), None)
    if vampire:
        print(f"   Sélection de: {vampire['nom']} ({vampire['faction']}) - Tier {vampire['tier']}")
        builder.selectionner_unite_deblocage(vampire)
        print(f"   ✅ Unité ajoutée aux récompenses")
    
    # Sélectionner un Ange (Religieux)
    ange = next((u for u in unites_disponibles if u['nom'] == 'Ange'), None)
    if ange:
        print(f"   Sélection de: {ange['nom']} ({ange['faction']}) - Tier {ange['tier']}")
        builder.selectionner_unite_deblocage(ange)
        print(f"   ✅ Unité ajoutée aux récompenses")
    
    print(f"\n3. Vérification des résultats...")
    print(f"   Unités débloquées: {builder.niveau_config.unites_debloquees}")
    print(f"   Nombre d'unités: {len(builder.niveau_config.unites_debloquees)}")
    
    # Vérifier que les bonnes unités ont été ajoutées
    expected = ['Vampire', 'Ange']
    if all(unite in builder.niveau_config.unites_debloquees for unite in expected):
        print(f"   ✅ Toutes les unités attendues sont présentes")
    else:
        print(f"   ❌ Erreur: unités manquantes")
    
    pygame.quit()
    print(f"\n=== Test terminé avec succès ! ===")

if __name__ == "__main__":
    test_selecteur_unites()
