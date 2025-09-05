# Système de Bouclier - Documentation

## Changements Effectués

### 1. Renommage "Shield" → "Bouclier"
- ✅ **competences.py** : Toutes les références à `shield` renommées en `bouclier`
- ✅ **affichage.py** : Interface utilisateur mise à jour
- ✅ **ia.py** : Logique de l'IA adaptée
- ✅ **README.md** : Documentation mise à jour

### 2. Système de Bouclier comme PV Additionnels

#### Nouvelle Méthode `subir_degats()`
```python
def subir_degats(self, degats):
    """Subit des dégâts en tenant compte du bouclier."""
    # Le bouclier absorbe d'abord les dégâts
    # Les dégâts en excès vont aux PV
```

#### Fonctionnement
1. **Absorption** : Le bouclier absorbe les dégâts en premier
2. **Débordement** : Si les dégâts dépassent le bouclier, l'excès va aux PV
3. **Non-soignable** : Le bouclier ne peut pas être restauré par les soins

### 3. Intégration Complète

#### Attaques
- ✅ Attaques normales utilisent `subir_degats()`
- ✅ Explosion sacrée utilise `subir_degats()`
- ✅ Toutes les sources de dégâts respectent le bouclier

#### Compétences qui donnent du bouclier
- ✅ **Bouclier de la foi** : +2 bouclier aux alliés adjacents
- ✅ **Bénédiction** : +1 bouclier à la cible

#### Affichage
- ✅ Cercle bleu autour des unités avec bouclier
- ✅ Nombre de points de bouclier affiché
- ✅ Info-bulle mise à jour

### 4. IA Intelligente
- ✅ L'IA priorise les alliés sans bouclier pour "Bouclier de la foi"
- ✅ Évaluation tactique prenant en compte le bouclier

## Avantages du Système

### 1. Stratégique
- **Protection temporaire** : Absorbe les dégâts sans affecter les PV
- **Non-cumulatif avec soin** : Le bouclier et les soins sont complémentaires
- **Planification tactique** : Anticiper les dégâts avec du bouclier

### 2. Visuel
- **Feedback clair** : Cercle bleu visible et compteur
- **Immédiat** : On voit l'effet du bouclier instantanément

### 3. Équilibré
- **Temporaire** : Le bouclier se consomme
- **Stratégique** : Doit être utilisé au bon moment
- **Complémentaire** : Ne remplace pas les soins

## Tests Validés

✅ **Test 1** : Absorption complète (2 dégâts sur 3 boucliers)
✅ **Test 2** : Débordement (3 dégâts sur 1 bouclier)  
✅ **Test 3** : Attaque avec bouclier partiel
✅ **Test 4** : Affichage en jeu
✅ **Test 5** : IA utilisant les compétences de bouclier

Le système de bouclier est maintenant pleinement fonctionnel et intégré !
