"""
Structure de données pour les niveaux de campagne et générateur de niveaux.
"""

import json
import os
from typing import Dict, List, Tuple, Optional, Union, Any
from enum import Enum
import unites

DEFAULT_CP = 5
DEFAULT_MAX_UNITES = 5

class TypeRestriction(Enum):
    """Types de restrictions pour la composition de l'équipe joueur"""
    UNITES_IMPOSEES = "unites_imposees"  # Des unités spécifiques sont imposées
    FACTIONS_DEFINIES = "factions_definies"  # Restriction à un ensemble de factions
    FACTION_UNIQUE = "faction_unique"  # Une seule faction autorisée
    FACTION_LIBRE = "faction_libre"  # Aucune restriction de faction


class NiveauConfig:
    """Configuration complète d'un niveau de campagne"""
    
    def __init__(self):
        # Informations générales
        self.nom: str = ""
        self.description: str = ""
        self.chapitre: str = ""
        self.numero: int = 0
        
        # Configuration des unités joueur
        self.type_restriction: TypeRestriction = TypeRestriction.FACTION_LIBRE
        self.unites_imposees: List[Tuple[type, Tuple[int, int]]] = []  # [(classe, position)]
        self.placement_impose: bool = False  # Si True, les positions sont fixes
        self.factions_autorisees: List[str] = []  # Liste des factions autorisées
        self.faction_unique_requise: bool = False  # Pas de mélange de factions
        self.faction_imposee: str = ""  # Faction imposée (force l'utilisation d'une faction spécifique)
        
        # Contraintes générales pour le joueur (si pas d'unités imposées)
        self.cp_disponible: int = DEFAULT_CP
        self.max_unites: int = DEFAULT_MAX_UNITES

        # Configuration des unités ennemies (générées par l'IA)
        self.unites_ennemis: List[Tuple[type, Tuple[int, int]]] = []  # [(classe, position)]
        self.difficulte_ennemis: str = "normale"  # facile, normale, difficile
        
        # Récompenses
        self.recompense_cp: int = 1
        self.recompense_pa: int = 0  # Récompense en PA
        self.unites_debloquees: List[str] = []  # Noms des classes d'unités
        self.recompenses_autres: List[Dict[str, Any]] = []  # Autres récompenses éventuelles
        
        # Métadonnées
        self.completable_plusieurs_fois: bool = False  # Si False, récompense une seule fois
        
    def valider(self) -> Tuple[bool, List[str]]:
        """Valide la configuration du niveau"""
        erreurs = []
        
        if not self.nom.strip():
            erreurs.append("Le niveau doit avoir un nom")
        
        if not self.unites_ennemis:
            erreurs.append("Le niveau doit avoir au moins une unité ennemie")
        
        if self.type_restriction == TypeRestriction.UNITES_IMPOSEES:
            if not self.unites_imposees:
                erreurs.append("Des unités imposées doivent être définies pour ce type de restriction")
        elif self.type_restriction == TypeRestriction.FACTIONS_DEFINIES:
            if not self.factions_autorisees:
                erreurs.append("Au moins une faction doit être autorisée")
        
        if self.cp_disponible <= 0:
            erreurs.append("Le nombre de CP disponibles doit être positif")
        
        if self.max_unites <= 0:
            erreurs.append("Le nombre maximum d'unités doit être positif")
        
        return len(erreurs) == 0, erreurs
    
    def est_faction_autorisee(self, faction: str) -> bool:
        """Vérifie si une faction est autorisée selon les restrictions"""
        if self.type_restriction == TypeRestriction.FACTION_LIBRE:
            return True
        elif self.type_restriction == TypeRestriction.FACTIONS_DEFINIES:
            return faction in self.factions_autorisees
        elif self.type_restriction == TypeRestriction.FACTION_UNIQUE:
            # Pour faction unique, on autorise toutes les factions, 
            # mais on vérifiera la cohérence au moment de la sélection
            return True
        else:  # UNITES_IMPOSEES
            return True  # Pas de restriction puisque les unités sont imposées
    
    def peut_melanger_factions(self) -> bool:
        """Vérifie si le mélange de factions est autorisé"""
        return not (self.faction_unique_requise or 
                   self.type_restriction == TypeRestriction.FACTION_UNIQUE)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire pour sauvegarde"""
        return {
            "nom": self.nom,
            "description": self.description,
            "chapitre": self.chapitre,
            "numero": self.numero,
            "type_restriction": self.type_restriction.value,
            "unites_imposees": [
                (cls.__name__ if hasattr(cls, '__name__') else cls, pos) 
                for cls, pos in self.unites_imposees
            ],
            "placement_impose": self.placement_impose,
            "factions_autorisees": self.factions_autorisees,
            "faction_unique_requise": self.faction_unique_requise,
            "faction_imposee": self.faction_imposee,
            "cp_disponible": self.cp_disponible,
            "max_unites": self.max_unites,
            "unites_ennemis": [
                (cls.__name__ if hasattr(cls, '__name__') else cls, pos) 
                for cls, pos in self.unites_ennemis
            ],
            "difficulte_ennemis": self.difficulte_ennemis,
            "recompense_cp": self.recompense_cp,
            "recompense_pa": self.recompense_pa,
            "unites_debloquees": self.unites_debloquees,
            "recompenses_autres": self.recompenses_autres,
            "completable_plusieurs_fois": self.completable_plusieurs_fois
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NiveauConfig':
        """Crée une configuration depuis un dictionnaire"""
        config = cls()
        
        config.nom = data.get("nom", "")
        config.description = data.get("description", "")
        config.chapitre = data.get("chapitre", "")
        config.numero = data.get("numero", 0)
        
        # Type de restriction
        type_str = data.get("type_restriction", "faction_libre")
        config.type_restriction = TypeRestriction(type_str)
        
        # Unités imposées
        unites_imposees_data = data.get("unites_imposees", [])
        config.unites_imposees = _convert_unit_names_to_classes(unites_imposees_data)
        
        config.placement_impose = data.get("placement_impose", False)
        config.factions_autorisees = data.get("factions_autorisees", [])
        config.faction_unique_requise = data.get("faction_unique_requise", False)
        config.faction_imposee = data.get("faction_imposee", "")
        
        config.cp_disponible = data.get("cp_disponible", 5)
        config.max_unites = data.get("max_unites", 14)
        
        # Unités ennemies
        unites_ennemis_data = data.get("unites_ennemis", [])
        config.unites_ennemis = _convert_unit_names_to_classes(unites_ennemis_data)
        
        config.difficulte_ennemis = data.get("difficulte_ennemis", "normale")
        config.recompense_cp = data.get("recompense_cp", 1)
        config.recompense_pa = data.get("recompense_pa", 0)
        config.unites_debloquees = data.get("unites_debloquees", [])
        config.recompenses_autres = data.get("recompenses_autres", [])
        config.completable_plusieurs_fois = data.get("completable_plusieurs_fois", False)
        
        return config


def _convert_unit_names_to_classes(unit_list: List[Tuple[str, Tuple[int, int]]]) -> List[Tuple[type, Tuple[int, int]]]:
    """Convertit les noms d'unités en classes d'unités"""
    converted = []
    for unit_name, pos in unit_list:
        # Trouver la classe correspondante
        for cls in unites.CLASSES_UNITES:
            if cls.__name__ == unit_name:
                converted.append((cls, pos))
                break
        else:
            print(f"Attention: Unité inconnue '{unit_name}' ignorée")
    return converted


def sauvegarder_niveau(config: NiveauConfig, chemin_fichier: str):
    """Sauvegarde une configuration de niveau"""
    data = config.to_dict()
    
    # Créer le répertoire si nécessaire
    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
    
    with open(chemin_fichier, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def charger_niveau(chemin_fichier: str) -> Optional[NiveauConfig]:
    """Charge une configuration de niveau"""
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return NiveauConfig.from_dict(data)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Erreur lors du chargement de {chemin_fichier}: {e}")
        return None


def obtenir_factions_disponibles() -> List[str]:
    """Retourne la liste des factions disponibles"""
    factions = set()
    for cls in unites.CLASSES_UNITES:
        # Créer une instance temporaire pour obtenir la faction
        instance = cls("temp", (0, 0))
        factions.add(instance.faction)
    return sorted(list(factions))
