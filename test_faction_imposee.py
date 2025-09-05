#!/usr/bin/env python3
"""
Script pour créer un niveau de test avec faction imposée
"""

import os
import sys

# Ajouter le répertoire racine au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from niveau_structure import NiveauConfig, TypeRestriction, sauvegarder_niveau

def creer_niveau_test_faction_imposee():
    """Crée un niveau de test avec faction imposée"""
    
    # Créer le dossier s'il n'existe pas
    os.makedirs("Campagne/00_Tutoriel/00_Test_Faction", exist_ok=True)
    
    # Configuration du niveau de test
    config = NiveauConfig()
    config.nom = "Test Faction Imposée"
    config.description = "Niveau de test avec faction Religieux imposée"
    config.chapitre = "Tutoriel"
    config.numero = 0
    
    # Configuration des restrictions avec faction imposée
    config.type_restriction = TypeRestriction.FACTION_LIBRE
    config.cp_disponible = 8
    config.max_unites = 10
    config.faction_imposee = "Religieux"  # Force l'utilisation de la faction Religieux
    
    # Ennemis
    config.unites_ennemis = [
        ("Goule", (2, 4)),
        ("Squelette", (3, 5)),
        ("Vampire", (4, 4))
    ]
    
    # Récompenses
    config.recompense_cp = 2
    config.unites_debloquees = []
    
    # Métadonnées
    config.difficulte_ennemis = "facile"
    
    # Sauvegarder le niveau
    fichier_niveau = "Campagne/00_Tutoriel/00_Test_Faction/niveau.json"
    sauvegarder_niveau(config, fichier_niveau)
    
    print(f"✓ Niveau de test créé: {fichier_niveau}")
    print(f"  - Nom: {config.nom}")
    print(f"  - Type: {config.type_restriction.value}")
    print(f"  - Faction imposée: {config.faction_imposee}")
    print(f"  - CP disponible: {config.cp_disponible}")
    print(f"  - Ennemis: {len(config.unites_ennemis)}")

if __name__ == "__main__":
    creer_niveau_test_faction_imposee()
