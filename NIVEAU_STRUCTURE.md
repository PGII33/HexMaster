# Structure de Niveaux HexMaster - Documentation

## Vue d'ensemble

La nouvelle structure de niveaux pour HexMaster permet de créer des niveaux de campagne avec des restrictions flexibles et des récompenses configurables.

## Types de Restrictions

### 1. Unités Imposées (`UNITES_IMPOSEES`)
- Le joueur utilise des unités spécifiques prédéfinies
- Placement optionnellement imposé (positions fixes)
- Utilisé pour des missions avec équipe prédefinie

### 2. Factions Définies (`FACTIONS_DEFINIES`)
- Restriction à un ensemble de factions spécifiques
- Le joueur peut mélanger les factions autorisées (sauf si `faction_unique_requise = True`)
- Permet de créer des scenarios thématiques

### 3. Faction Unique (`FACTION_UNIQUE`)
- Le joueur ne peut utiliser qu'une seule faction
- Pas de mélange autorisé
- Encourage la cohérence d'équipe

### 4. Faction Libre (`FACTION_LIBRE`)
- Aucune restriction de faction
- Le joueur peut utiliser toutes les unités disponibles
- Mode le plus flexible

## Structure des Fichiers

```
Campagne/
├── 00_Tutoriel/
│   ├── 01_Premier_Combat/
│   │   └── niveau.json
│   ├── 02_Armée_Cohérente/
│   │   └── niveau.json
│   └── ...
└── 01_Autre_Chapitre/
    └── ...
```

## Configuration d'un Niveau

Chaque niveau est défini par un fichier `niveau.json` contenant :

```json
{
  "nom": "Nom du niveau",
  "description": "Description du niveau",
  "chapitre": "Nom du chapitre",
  "numero": 1,
  "type_restriction": "faction_libre|faction_unique|factions_definies|unites_imposees",
  "unites_imposees": [],
  "placement_impose": false,
  "factions_autorisees": [],
  "faction_unique_requise": false,
  "cp_disponible": 5,
  "max_unites": 14,
  "unites_ennemis": [["NomClasse", [x, y]]],
  "difficulte_ennemis": "normale",
  "recompense_cp": 1,
  "unites_debloquees": [],
  "recompenses_autres": [],
  "completable_plusieurs_fois": false
}
```

## Outils Disponibles

### 1. Level Builder (`level_builder.py`)
Interface graphique pour créer des niveaux :
- Configuration générale (nom, description, chapitre)
- Définition des restrictions
- Sélection et placement des ennemis
- Configuration des récompenses
- Test du niveau

### 2. Gestionnaire de Campagne (`campagne.py`)
- Chargement automatique de la structure de campagne
- Interface de sélection des chapitres et niveaux
- Gestion des récompenses et progression

### 3. Structure de Données (`niveau_structure.py`)
- Classes `NiveauConfig` et `TypeRestriction`
- Validation des configurations
- Sauvegarde/chargement des niveaux

### 4. UI Commune (`ui_commons.py`)
- Composants d'interface réutilisables
- Gestionnaire de progression
- Évite la duplication de code

## Fonctionnalités

### Validation Automatique
- Vérification de la cohérence des configurations
- Messages d'erreur explicites
- Empêche la création de niveaux invalides

### Système de Récompenses
- CP gagnés à la victoire
- Unités débloquées
- Récompenses personnalisées
- Protection contre les récompenses multiples

### Progression de Campagne
- Suivi des niveaux complétés
- Sauvegarde automatique de la progression
- Compatible avec le système de sauvegarde existant

## Exemples d'Utilisation

### Créer un Niveau Simple
```python
from niveau_structure import NiveauConfig, TypeRestriction, sauvegarder_niveau
import unites

config = NiveauConfig()
config.nom = "Mon Niveau"
config.type_restriction = TypeRestriction.FACTION_LIBRE
config.cp_disponible = 5
config.max_unites = 10
config.unites_ennemis = [(unites.Squelette, (5, 2))]
config.recompense_cp = 1

sauvegarder_niveau(config, "chemin/vers/niveau.json")
```

### Charger et Jouer un Niveau
```python
from campagne import get_niveau_data

# Récupérer les données d'un niveau
data = get_niveau_data("Tutoriel", 1)
if data:
    config = data['config']
    unites_joueur = data['unites_joueur']
    unites_ennemis = data['unites_ennemis']
    
    # Utiliser ces données pour initialiser le jeu
```

## Compatibilité

La nouvelle structure est :
- ✅ Compatible avec le système de sauvegarde existant
- ✅ Compatible avec les unités existantes
- ✅ Extensible pour de nouvelles fonctionnalités
- ✅ Rétrocompatible (via fonctions utilitaires)

## Tests

Le fichier `test_structure.py` contient des tests complets :
- Chargement/sauvegarde des niveaux
- Validation des configurations
- Fonctions utilitaires
- Système de progression

Pour exécuter les tests : `python test_structure.py`
