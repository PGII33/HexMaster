import os
import json
from jeu import Jeu
import ia
import unites

class Tuto:
    def __init__(self, screen):
        self.screen = screen
    
    def run_flow(self):
        """Lance le tutoriel en utilisant le niveau de campagne"""
        # Charger le niveau tutoriel depuis la campagne
        tutorial_path = os.path.join("Campagne", "00_Tutoriel", "niveau.json")
        
        if os.path.exists(tutorial_path):
            try:
                with open(tutorial_path, 'r', encoding='utf-8') as f:
                    tutorial_data = json.load(f)
                
                # Convertir les noms d'unités en classes
                unites_joueur = self._convert_unit_names_to_classes(tutorial_data["unites_predefinies"])
                unites_ennemis = self._convert_unit_names_to_classes(tutorial_data["unites_ennemis"])
                
                return Jeu(
                    ia_strategy=ia.cible_faible,
                    screen=self.screen,
                    initial_player_units=unites_joueur,
                    initial_enemy_units=unites_ennemis,
                    enable_placement=False  # Unités prépositionnées
                )
                
            except Exception as e:
                print(f"Erreur lors du chargement du tutoriel: {e}")
        
        # Fallback vers l'ancien système si le fichier n'existe pas
        return self._create_fallback_tutorial()
    
    def _convert_unit_names_to_classes(self, unit_list):
        """Convertit les noms d'unités en classes d'unités"""
        converted = []
        for unit_name, pos in unit_list:
            # Trouver la classe correspondante
            for cls in unites.CLASSES_UNITES:
                if cls.__name__ == unit_name:
                    converted.append((cls, pos))
                    break
            else:
                print(f"Unité inconnue dans le tutoriel: {unit_name}")
        return converted
    
    def _create_fallback_tutorial(self):
        """Crée un tutoriel de secours si le fichier JSON n'existe pas"""
        print("Utilisation du tutoriel de secours")
        
        initial_player_units = [
            (unites.Squelette, (0, 0)),
            (unites.Vampire, (1, 0)),
        ]
        initial_enemy_units = [
            (unites.Squelette, (5, 4)),
            (unites.Goule, (6, 5)),
        ]
        
        return Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=initial_player_units,
            initial_enemy_units=initial_enemy_units,
            enable_placement=False
        )
