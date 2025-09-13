# 🎯 Guide de Création de Niveaux Personnalisés - HexMaster

## Vue d'ensemble

HexMaster permet de créer facilement des niveaux personnalisés grâce à un système de fichiers JSON et une structure modulaire. Ce guide vous explique comment créer vos propres défis tactiques.

## 📁 Structure des Dossiers

### Organisation des Niveaux

```
HexMaster_Data/
├── Campagne/                    # Niveaux de campagne officielle
│   ├── 01_Religieux/
│   ├── 02_Elementaires/
│   └── ...
└── custom_levels/               # Vos niveaux personnalisés
    ├── Mon_Chapitre/
    │   ├── 01_Premier_Niveau/
    │   │   └── niveau.json
    │   ├── 02_Deuxieme_Niveau/
    │   │   └── niveau.json
    │   └── meta.json
    └── Autre_Chapitre/
        └── ...
```

### Noms de Dossiers
- **Chapitres** : Nommez avec un préfixe numérique : `01_Nom_Chapitre`, `02_Autre_Chapitre`
- **Niveaux** : Utilisez le même système : `01_Nom_Niveau`, `02_Autre_Niveau`
- **Espaces** : Remplacez les espaces par des underscores `_`

## 🏗️ Création d'un Niveau

### 1. Structure du Fichier `niveau.json`

Créez un fichier `niveau.json` avec cette structure :

```json
{
  "nom": "Mon Premier Niveau",
  "description": "Un niveau pour apprendre les bases du jeu",
  "chapitre": "01_Mon_Chapitre",
  "numero": 1,
  "type_restriction": "faction_libre",
  "unites_imposees": [],
  "placement_impose": false,
  "factions_autorisees": [],
  "faction_unique_requise": false,
  "faction_imposee": "",
  "cp_disponible": 5,
  "max_unites": 8,
  "unites_ennemis": [
    ["Goule", [6, 2]],
    ["Squelette", [7, 1]]
  ],
  "difficulte_ennemis": "normale",
  "recompense_cp": 1,
  "recompense_pa": 50,
  "unites_debloquees": [],
  "recompenses_autres": [],
  "completable_plusieurs_fois": false
}
```

### 2. Explication des Paramètres

#### Informations de Base
- **`nom`** : Nom affiché du niveau
- **`description`** : Description optionnelle du défi
- **`chapitre`** : Identifiant du chapitre parent
- **`numero`** : Numéro du niveau dans le chapitre

#### Types de Restrictions (`type_restriction`)

##### `"faction_libre"` - Liberté Totale
```json
{
  "type_restriction": "faction_libre",
  "cp_disponible": 6,
  "max_unites": 10
}
```
Le joueur peut choisir n'importe quelle combinaison d'unités.

##### `"faction_unique"` - Une Seule Faction
```json
{
  "type_restriction": "faction_unique",
  "faction_unique_requise": true,
  "cp_disponible": 5
}
```
Le joueur doit choisir une faction et s'y tenir.

##### `"factions_definies"` - Factions Limitées
```json
{
  "type_restriction": "factions_definies",
  "factions_autorisees": ["Religieux", "Royaume"],
  "cp_disponible": 6
}
```
Seules certaines factions sont autorisées.

##### `"unites_imposees"` - Unités Prédéfinies
```json
{
  "type_restriction": "unites_imposees",
  "unites_imposees": [
    ["Guerrier", [0, 1]],
    ["Archer", [1, 0]],
    ["Clerc", [0, 2]]
  ],
  "placement_impose": true
}
```
Les unités et leurs positions sont fixes.

#### Configuration Ennemie
```json
{
  "unites_ennemis": [
    ["Goule", [6, 2]],      # [Nom_Unité, [position_q, position_r]]
    ["Vampire", [7, 3]],
    ["Liche", [8, 2]]
  ],
  "difficulte_ennemis": "difficile"  # "facile", "normale", "difficile"
}
```

#### Récompenses
```json
{
  "recompense_cp": 2,                    # Points de Contrainte gagnés
  "recompense_pa": 100,                  # Points d'Âme gagnés
  "unites_debloquees": ["Paladin"],      # Nouvelles unités débloquées
  "completable_plusieurs_fois": false    # Récompense unique ou répétable
}
```

## 🎪 Unités Disponibles

### Liste des Classes d'Unités

#### Morts-Vivants
- `"Tas_D_Os"`, `"Squelette"`, `"Goule"`, `"Spectre"`
- `"Vampire"`, `"Zombie"`, `"Liche"`, `"Archliche"`

#### Religieux  
- `"Missionnaire"`, `"Clerc"`, `"Fanatique"`
- `"Esprit_Saint"`, `"Paladin"`, `"Ange"`, `"ArchAnge"`

#### Élémentaires
- `"Cristal"`, `"Esprit"`, `"Driade"`, `"Gnome"`
- `"Golem"`, `"Ondine"`, `"Ifrit"`, `"Phénix"`

#### Royaume
- `"Cheval"`, `"Guerrier"`, `"Archer"`, `"Cavalier"`
- `"Bouffon"`, `"Garde_Royal"`, `"Roi"`, `"Marionettiste"`

#### Chimères
- `"Harpie"`, `"Centaure"`, `"Griffon"`
- `"Lamia"`, `"Loup_Garou"`, `"Manticore"`, `"Basilic"`

## 🗺️ Système de Coordonnées Hexagonales

### Coordonnées Axiales (q, r)
HexMaster utilise un système de coordonnées hexagonales axiales :

```
    (0,0) (1,0) (2,0)
  (0,1) (1,1) (2,1) (3,1)
    (0,2) (1,2) (2,2)
```

### Taille du Plateau
- **Largeur** : 0 à 7 (8 colonnes)
- **Hauteur** : 0 à 5 (6 lignes, variables selon la colonne)

### Positionnement Stratégique
```json
{
  "unites_ennemis": [
    ["Archer", [7, 0]],     # Coin supérieur droit
    ["Guerrier", [4, 2]],   # Centre du plateau
    ["Clerc", [0, 5]]       # Coin inférieur gauche
  ]
}
```

## 📋 Fichier de Métadonnées (`meta.json`)

Créez un fichier `meta.json` pour définir votre chapitre :

```json
{
  "nom": "Mon Chapitre Personnalisé",
  "description": "Une série de défis tactiques créés par moi",
  "niveaux": [
    {
      "id": 1,
      "nom": "Premier Défi",
      "requis": []
    },
    {
      "id": 2, 
      "nom": "Défi Avancé",
      "requis": [1]
    },
    {
      "id": 3,
      "nom": "Boss Final",
      "requis": [1, 2]
    }
  ]
}
```

### Dépendances entre Niveaux
- **`requis: []`** : Niveau accessible immédiatement
- **`requis: [1]`** : Nécessite d'avoir terminé le niveau 1
- **`requis: [1, 2]`** : Nécessite les niveaux 1 ET 2

## 🎯 Exemples de Niveaux Types

### Exemple 1 : Niveau d'Initiation
```json
{
  "nom": "Premiers Pas",
  "description": "Apprenez les bases avec des unités simples",
  "type_restriction": "faction_libre",
  "cp_disponible": 3,
  "max_unites": 3,
  "unites_ennemis": [
    ["Goule", [6, 1]],
    ["Squelette", [7, 2]]
  ],
  "recompense_cp": 1,
  "recompense_pa": 25
}
```

### Exemple 2 : Défi Faction Pure
```json
{
  "nom": "Pureté Religieuse",
  "description": "Seule la foi peut triompher",
  "type_restriction": "factions_definies", 
  "factions_autorisees": ["Religieux"],
  "cp_disponible": 5,
  "unites_ennemis": [
    ["Vampire", [6, 1]],
    ["Liche", [7, 2]],
    ["Spectre", [5, 3]]
  ],
  "recompense_cp": 2
}
```

### Exemple 3 : Scenario Imposé
```json
{
  "nom": "Sauvetage Héroïque",
  "description": "Sauvez le clerc avec vos forces limitées",
  "type_restriction": "unites_imposees",
  "unites_imposees": [
    ["Guerrier", [0, 1]],
    ["Guerrier", [1, 1]], 
    ["Clerc", [0, 2]]
  ],
  "placement_impose": true,
  "unites_ennemis": [
    ["Goule", [6, 1]],
    ["Goule", [7, 1]],
    ["Vampire", [6, 3]]
  ]
}
```

### Exemple 4 : Boss Challenge
```json
{
  "nom": "L'Archliche Maudit",
  "description": "Défiez le maître des morts-vivants",
  "type_restriction": "faction_libre",
  "cp_disponible": 8,
  "max_unites": 6,
  "unites_ennemis": [
    ["Archliche", [7, 2]],
    ["Liche", [6, 1]],
    ["Vampire", [6, 3]],
    ["Spectre", [5, 2]]
  ],
  "difficulte_ennemis": "difficile",
  "recompense_cp": 3,
  "recompense_pa": 200,
  "unites_debloquees": ["Necromancien_Special"]
}
```

## 🧪 Tests et Équilibrage

### Conseils d'Équilibrage
1. **Commencez Simple** : Testez avec peu d'unités avant d'ajouter de la complexité
2. **Équilibre CP/Ennemis** : Plus d'ennemis = plus de CP pour le joueur
3. **Progression Logique** : Augmentez progressivement la difficulté
4. **Variété Tactique** : Utilisez différents types d'unités et compétences

### Points de Contrainte Recommandés
- **Niveau Facile** : 3-4 CP, 2-3 ennemis faibles
- **Niveau Normal** : 5-6 CP, 3-5 ennemis mixtes  
- **Niveau Difficile** : 7-8 CP, 4-6 ennemis forts
- **Boss** : 8+ CP, 1 boss + support

### Test de Votre Niveau
1. **Chargez le niveau** via le menu custom du jeu
2. **Testez différentes compositions** d'équipe joueur
3. **Vérifiez l'équilibre** : ni trop facile, ni impossible
4. **Ajustez les récompenses** selon la difficulté réelle

## 🚀 Publication et Partage

### Validation Finale
Avant de partager votre niveau :
- ✅ Le fichier `niveau.json` est syntaxiquement correct
- ✅ Toutes les unités utilisées existent dans le jeu
- ✅ Les positions sont valides sur le plateau hexagonal
- ✅ Les récompenses sont équilibrées
- ✅ Le niveau est jouable et amusant

### Partage Community
1. Zippez votre dossier de chapitre complet
2. Incluez un `meta.json` descriptif
3. Partagez avec d'autres joueurs
4. Collectez les retours pour améliorer vos créations

---

*Amusez-vous bien à créer vos propres défis tactiques dans HexMaster ! N'hésitez pas à expérimenter avec les différentes mécaniques de jeu pour créer des situations uniques et captivantes.*