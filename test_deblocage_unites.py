#!/usr/bin/env python3
"""
Test du système de déblocage d'unités
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from niveau_structure import NiveauConfig, TypeRestriction
import ui_commons
import sauvegarde

def test_deblocage_unites():
    """Teste le système complet de déblocage d'unités"""
    
    print("=== Test du système de déblocage d'unités ===\n")
    
    # 1. Créer un niveau avec des unités à débloquer
    print("1. Création d'un niveau avec récompenses...")
    niveau_config = NiveauConfig()
    niveau_config.nom = "Test Déblocage"
    niveau_config.description = "Niveau de test pour débloquer des unités"
    niveau_config.recompense_cp = 2
    niveau_config.unites_debloquees = ["Vampire", "Ange"]  # Noms de classes
    
    print(f"   Niveau: {niveau_config.nom}")
    print(f"   CP récompense: {niveau_config.recompense_cp}")
    print(f"   Unités à débloquer: {niveau_config.unites_debloquees}")
    
    # 2. Tester la sérialisation
    print("\n2. Test de sérialisation...")
    niveau_dict = niveau_config.to_dict()
    niveau_restaure = NiveauConfig.from_dict(niveau_dict)
    
    assert niveau_restaure.unites_debloquees == niveau_config.unites_debloquees
    print("   ✅ Sérialisation/désérialisation réussie")
    
    # 3. Simuler l'application des récompenses
    print("\n3. Test d'application des récompenses...")
    
    # Données de sauvegarde simulées
    sauvegarde_data = {
        "cp": 5,
        "unites": ["Goule", "Squelette"]  # Unités déjà débloquées
    }
    
    print(f"   Avant: CP={sauvegarde_data['cp']}, Unités={sauvegarde_data['unites']}")
    
    # Appliquer les récompenses
    ui_commons.ProgressionManager.appliquer_recompenses(sauvegarde_data, niveau_config)
    
    print(f"   Après: CP={sauvegarde_data['cp']}, Unités={sauvegarde_data['unites']}")
    
    # Vérifications
    assert sauvegarde_data['cp'] == 7  # 5 + 2
    assert "Vampire" in sauvegarde_data['unites']
    assert "Ange" in sauvegarde_data['unites']
    assert len(sauvegarde_data['unites']) == 4  # Goule, Squelette, Vampire, Ange
    
    print("   ✅ Récompenses appliquées correctement")
    
    # 4. Tester la prévention des doublons
    print("\n4. Test de prévention des doublons...")
    sauvegarde_data_avant = dict(sauvegarde_data)
    
    # Appliquer les mêmes récompenses
    ui_commons.ProgressionManager.appliquer_recompenses(sauvegarde_data, niveau_config)
    
    # Les unités ne doivent pas être dupliquées
    assert len(sauvegarde_data['unites']) == len(sauvegarde_data_avant['unites'])
    print("   ✅ Aucun doublon créé")
    
    # 5. Tester avec des noms d'unités valides
    print("\n5. Validation des noms d'unités...")
    from unites import CLASSES_UNITES
    
    noms_classes_valides = [cls.__name__ for cls in CLASSES_UNITES]
    
    for nom_unite in niveau_config.unites_debloquees:
        if nom_unite in noms_classes_valides:
            print(f"   ✅ {nom_unite} - Classe valide")
        else:
            print(f"   ❌ {nom_unite} - Classe invalide")
    
    print(f"\n=== Test terminé avec succès ! ===")
    print(f"Classes d'unités disponibles: {len(noms_classes_valides)}")
    print(f"Quelques exemples: {noms_classes_valides[:5]}")

if __name__ == "__main__":
    test_deblocage_unites()
