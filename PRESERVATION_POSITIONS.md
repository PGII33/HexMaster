# Préservation des Positions d'Unités - Level Builder

## Vue d'ensemble

Le système de création de niveaux a été amélioré pour préserver intelligemment les positions des unités lors des modifications de composition, évitant ainsi de perdre le travail de placement effectué.

## Nouvelles fonctionnalités

### 1. Conservation des positions lors du retour à la sélection

**Problème résolu :** Quand on revient de la phase de placement vers la sélection d'unités, toutes les positions étaient perdues.

**Solution :** Le système mémorise automatiquement :
- La dernière composition d'unités sélectionnées
- Leurs positions sur la carte
- Restaure automatiquement ces positions si la composition n'a pas changé

### 2. Préservation partielle lors du changement de composition

**Problème résolu :** Changer la composition d'ennemis effaçait toutes les positions existantes.

**Solution :** Le système conserve intelligemment :
- Les positions des unités communes entre l'ancienne et la nouvelle composition
- Retire seulement les positions des unités qui ne sont plus présentes
- Préserve l'ordre et la distribution des unités conservées

## Comportements détaillés

### Scénario 1 : Retour à la sélection sans changement

```
1. Sélection : [Squelette, Goule, Squelette]
2. Placement sur la carte aux positions (1,4), (2,4), (3,4)
3. Retour à la sélection → Positions mémorisées
4. Retour au placement → Positions restaurées automatiquement
```

### Scénario 2 : Modification partielle de composition

```
Composition initiale : [Squelette, Goule, Squelette, Zombie]
Positions : Squelette(1,4), Goule(2,4), Squelette(3,4), Zombie(1,5)

Nouvelle composition : [Squelette, Liche, Squelette, Goule]
Résultat : Squelette(1,4), Squelette(3,4), Goule(2,4) conservés
           Zombie(1,5) retiré, Liche pas encore placée
```

### Scénario 3 : Changement complet de composition

```
Ancienne : [Squelette, Goule]
Nouvelle : [Zombie, Liche]
Résultat : Toutes les positions effacées (aucune unité commune)
```

## Variables de mémorisation

Le system utilise deux variables internes :

- **`_derniere_composition`** : Liste des classes d'unités de la dernière sélection
- **`_positions_sauvegardees`** : Positions correspondantes sur la carte

Ces variables sont automatiquement :
- Initialisées lors de la création d'un nouveau niveau
- Mises à jour après chaque placement validé
- Utilisées pour la restauration lors du retour au placement

## Algorithmes utilisés

### Comparaison de compositions

```python
def _compositions_identiques(self, comp1, comp2):
    # Compare les occurrences de chaque classe d'unité
    # [Squelette, Goule, Squelette] == [Squelette, Squelette, Goule] : True
    # [Squelette, Goule] == [Squelette, Squelette, Goule] : False
```

### Conservation des positions communes

```python
def _conserver_positions_communes(self, ancienne, nouvelle):
    # 1. Calculer les unités communes (min des occurrences)
    # 2. Conserver seulement les positions des unités communes
    # 3. Respecter les limites de quantité pour chaque type
```

## Intégration avec PlacementPhase

Le système `PlacementPhase` a été étendu pour accepter des unités pré-placées :

```python
placement = PlacementPhase(
    screen,
    selected_units,
    existing_units=existing_units  # Unités avec positions existantes
)
```

## Impact utilisateur

### Amélioration de l'expérience

1. **Pas de perte de travail** : Les positions sont conservées lors des allers-retours
2. **Modification intelligente** : Les changements partiels ne perdent que le nécessaire
3. **Workflow naturel** : L'utilisateur peut itérer librement sur la composition

### Messages informatifs

Le système affiche des messages pour informer l'utilisateur :

```
"Chargement du placement existant (modification): 3 unités"
"Restauration du placement précédent: 3 unités"
"Positions conservées: 2 unités communes"
"  - Squelette: 2 position(s) conservée(s)"
```

## Tests de validation

Les fonctionnalités ont été validées par :

1. **Tests unitaires** : Validation des algorithmes de comparaison et conservation
2. **Tests d'intégration** : Validation du workflow complet
3. **Tests interactifs** : Validation de l'expérience utilisateur

## Compatibilité

Les améliorations sont **rétrocompatibles** :
- Les niveaux existants continuent de fonctionner normalement
- Aucun changement nécessaire dans les fichiers de configuration
- L'interface reste identique, seul le comportement est amélioré

## Cas d'usage typiques

### Création itérative
1. Sélectionner des unités
2. Les placer grossièrement
3. Retourner affiner la sélection
4. → Les positions sont conservées

### Ajustement fin
1. Avoir une composition complète placée
2. Vouloir remplacer une unité par une autre
3. → Seule l'unité remplacée perd sa position

### Modification de niveau existant
1. Charger un niveau pour modification
2. Ajuster la composition d'ennemis
3. → Les positions communes sont préservées
