# Modification du Placement des Unités - Documentation

## Fonctionnalité Ajoutée

Le Level Builder permet maintenant de modifier le placement des unités ennemies lors de l'édition d'un niveau existant. Les unités déjà placées sont automatiquement chargées et positionnées sur la grille.

## Comment ça fonctionne

### 1. Chargement automatique des unités

Quand vous modifiez un niveau existant :
- ✅ Les types d'unités ennemies sont automatiquement ajoutés à la sélection
- ✅ Les positions existantes sont préservées
- ✅ Le compteur d'unités disponibles est ajusté automatiquement

### 2. Interface améliorée

#### Écran de sélection des ennemis
- **Mode création** : Affiche seulement "Placer Ennemis"
- **Mode modification** : Affiche "Modifier Placement" + liste du placement actuel
- **Informations visibles** : Types d'unités et leurs positions actuelles

#### Phase de placement
- **Unités pré-placées** : Apparaissent déjà sur la grille
- **Titre indicatif** : "(Modification)" ajouté au titre
- **Gestion intelligente** : Les unités placées sont décomptées automatiquement

### 3. Workflow de modification

```
1. Level Builder → "Modifier Niveau"
2. Sélection du niveau dans la liste
3. Navigation : Config générale → Restrictions → Ennemis
4. "Sélectionner les Ennemis" (déjà fait automatiquement)
5. "Modifier Placement" → Interface avec unités déjà placées
6. Modification du placement selon vos besoins
7. Validation et sauvegarde
```

## Modifications techniques

### Level Builder (`level_builder.py`)

#### Méthode `charger_niveau_pour_modification()`
```python
# Récupération automatique des unités ennemies
self.enemy_units_selected = []
for unit_class, position in config.unites_ennemis:
    self.enemy_units_selected.append(unit_class)
```

#### Méthode `placer_ennemis()`
```python
# Préparation des unités existantes pour PlacementPhase
existing_units = None
if hasattr(self, 'niveau_selectionne') and self.niveau_config.unites_ennemis:
    existing_units = []
    for unit_class, position in self.niveau_config.unites_ennemis:
        existing_units.append((unit_class, position))

# Passage à PlacementPhase avec existing_units
placement = PlacementPhase(
    self.screen,
    self.enemy_units_selected,
    existing_units=existing_units  # ← Nouveau paramètre
)
```

#### Interface `enemy_selection`
- Affichage du placement actuel en mode modification
- Bouton adaptatif "Placer Ennemis" / "Modifier Placement"

### PlacementPhase (`placement.py`)

#### Constructeur étendu
```python
def __init__(self, screen, selected_units, titre=None, player_spawn_zone=None, 
             enemy_spawn_zone=None, existing_units=None):  # ← Nouveau
```

#### Chargement des unités existantes
```python
if existing_units:
    for unit_class, position in existing_units:
        # Conversion liste → tuple si nécessaire
        if isinstance(position, list):
            position = tuple(position)
        
        # Placement sur la grille
        self.placed_units[position] = unit_class
        
        # Décompte automatique
        if unit_class in self.available_units:
            self.available_units[unit_class] -= 1
```

## Avantages

### Pour le game design
- ✅ **Modification rapide** : Pas besoin de replacer toutes les unités
- ✅ **Préservation** : Les positions existantes sont conservées
- ✅ **Flexibilité** : Ajout/suppression/déplacement facile d'unités

### Pour l'équilibrage
- ✅ **Itération rapide** : Test → Ajustement → Re-test
- ✅ **Visuel immédiat** : Voir le placement actuel avant modification
- ✅ **Validation** : Même système de validation que la création

### Pour la maintenance
- ✅ **Rétrocompatibilité** : Fonctionne avec tous les niveaux existants
- ✅ **Robustesse** : Gestion des erreurs de format
- ✅ **Intégration** : Utilise les systèmes existants

## Limitations

- Les unités existantes doivent correspondre aux types disponibles
- La modification ne permet pas de changer les types d'unités (utiliser "Sélectionner les Ennemis")
- Les positions invalides sont ignorées silencieusement

## Test et validation

Le système a été testé avec :
- ✅ Niveaux vides (création normale)
- ✅ Niveaux avec unités (modification)
- ✅ Différents types d'unités (Fanatique, Missionnaire, etc.)
- ✅ Différentes positions sur la grille
- ✅ Comptage correct des unités disponibles/placées

## Usage recommandé

1. **Sauvegarde préventive** : Faire une copie des niveaux avant modification importante
2. **Test systématique** : Tester le niveau après chaque modification
3. **Validation** : Vérifier que toutes les unités sont correctement placées
4. **Documentation** : Noter les changements pour le suivi des versions
