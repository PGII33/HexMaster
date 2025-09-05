#!/usr/bin/env python3
"""
Script pour vérifi                if verifier_niveau(niveau_file, chapter_folder, "principal", Q_MIN, Q_MAX, R_MIN, R_MAX, ZONE_JOUEUR, ZONE_ENNEMIE):
                    problemes_trouves += 1r que toutes les positions dans les niveaux de campagne sont valides
"""

import os
import json
import sys

# Ajouter le répertoire racine au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verifier_positions_valides():
    """Vérifie que toutes les positions dans les niveaux sont dans la grille valide (-1 à 6)"""
    
    campaign_path = "Campagne"
    if not os.path.exists(campaign_path):
        print("❌ Dossier Campagne non trouvé!")
        return
    
    # Limites de la grille (comme défini dans jeu.py)
    Q_MIN, Q_MAX = -1, 6
    R_MIN, R_MAX = -1, 6
    
    # Zones spécifiques
    ZONE_JOUEUR = [-1, 0, 1]  # 3 lignes du haut
    ZONE_ENNEMIE = [4, 5, 6]  # 3 lignes du bas
    
    problemes_trouves = 0
    niveaux_verifies = 0
    
    print("=== Vérification des positions dans les niveaux ===\n")
    
    # Parcourir tous les chapitres
    for chapter_folder in sorted(os.listdir(campaign_path)):
        chapter_path = os.path.join(campaign_path, chapter_folder)
        if not os.path.isdir(chapter_path):
            continue
        
        print(f"📁 Chapitre: {chapter_folder}")
        
        # Parcourir tous les niveaux ou fichiers dans le chapitre
        items = os.listdir(chapter_path)
        
        # Vérifier s'il y a un niveau.json directement dans le chapitre
        if "niveau.json" in items:
            niveau_file = os.path.join(chapter_path, "niveau.json")
            if verifier_niveau(niveau_file, chapter_folder, "principal", Q_MIN, Q_MAX, R_MIN, R_MAX, ZONE_JOUEUR, ZONE_ENNEMIE):
                problemes_trouves += 1
            niveaux_verifies += 1
        
        # Vérifier les sous-dossiers de niveaux
        for level_folder in sorted(items):
            level_path = os.path.join(chapter_path, level_folder)
            if os.path.isdir(level_path):
                niveau_file = os.path.join(level_path, "niveau.json")
                if os.path.exists(niveau_file):
                    if verifier_niveau(niveau_file, chapter_folder, level_folder, Q_MIN, Q_MAX, R_MIN, R_MAX, ZONE_JOUEUR, ZONE_ENNEMIE):
                        problemes_trouves += 1
                    niveaux_verifies += 1
    
    print(f"\n=== Résumé ===")
    print(f"✅ Niveaux vérifiés: {niveaux_verifies}")
    if problemes_trouves == 0:
        print("🎉 Aucun problème trouvé! Toutes les positions sont valides.")
    else:
        print(f"⚠️  {problemes_trouves} problème(s) trouvé(s)")

def verifier_niveau(fichier, chapitre, niveau, q_min, q_max, r_min, r_max, zone_joueur, zone_ennemie):
    """Vérifie un niveau spécifique et retourne True s'il y a des problèmes"""
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        problemes = False
        print(f"  📄 {niveau}: {data.get('nom', 'Sans nom')}")
        
        # Vérifier les unités imposées (doivent être en zone joueur)
        if 'unites_imposees' in data and data['unites_imposees']:
            for i, unite_data in enumerate(data['unites_imposees']):
                if len(unite_data) >= 2:
                    nom_unite, position = unite_data[0], unite_data[1]
                    q, r = position[0], position[1]
                    if not (q_min <= q <= q_max and r_min <= r <= r_max):
                        print(f"    ❌ Unité imposée {nom_unite} en position invalide ({q}, {r})")
                        problemes = True
                    elif r not in zone_joueur:
                        print(f"    ⚠️  Unité imposée {nom_unite} hors zone joueur ({q}, {r}) - devrait être en r={zone_joueur}")
                        problemes = True
        
        # Vérifier les unités ennemies (doivent être en zone ennemie)
        if 'unites_ennemis' in data and data['unites_ennemis']:
            for i, unite_data in enumerate(data['unites_ennemis']):
                if len(unite_data) >= 2:
                    nom_unite, position = unite_data[0], unite_data[1]
                    q, r = position[0], position[1]
                    if not (q_min <= q <= q_max and r_min <= r <= r_max):
                        print(f"    ❌ Unité ennemie {nom_unite} en position invalide ({q}, {r})")
                        problemes = True
                    elif r not in zone_ennemie:
                        print(f"    ⚠️  Unité ennemie {nom_unite} hors zone ennemie ({q}, {r}) - devrait être en r={zone_ennemie}")
                        problemes = True
        
        if not problemes:
            print(f"    ✅ Toutes les positions sont valides et dans les bonnes zones")
        
        return problemes
        
    except Exception as e:
        print(f"    ❌ Erreur lors de la lecture: {e}")
        return True

if __name__ == "__main__":
    verifier_positions_valides()
