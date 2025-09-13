# 🤖 Système d'Intelligence Artificielle Tactique - HexMaster

## Vue d'ensemble

HexMaster dispose d'un système d'IA sophistiqué capable de gérer des stratégies tactiques complexes, l'utilisation intelligente des compétences actives et passives, et l'adaptation dynamique aux situations de combat.

## Architecture du système IA

### 🎯 Modes d'IA disponibles

#### 1. `cible_faible()` - IA Basique Intelligente
- **Philosophie** : Priorise l'élimination des cibles les plus faibles
- **Utilisation** : IA par défaut pour la plupart des unités
- **Caractéristiques** :
  - Intègre l'utilisation des compétences actives
  - Priorise les cibles avec le moins de PV
  - Optimise le déplacement pour économiser les PM

#### 2. `ia_tactique_avancee()` - IA Stratégique
- **Philosophie** : Analyse tactique complète avec stratégies spécialisées
- **Utilisation** : IA de haut niveau pour les unités importantes
- **Caractéristiques** :
  - Évaluation multicritère des cibles
  - Stratégies défensives et offensives adaptatives
  - Gestion avancée des passifs tactiques

## 🧠 Logique de Prise de Décision

### Phase 1: Analyse des Compétences Actives
L'IA évalue en priorité l'utilisation des compétences actives selon cette hiérarchie :

#### Compétences de Support (Priorité Maximum)
```
1. Soin : Soigner les alliés critiques (≤2 PV = priorité absolue)
2. Bénédiction : Buffer les unités offensives qui peuvent attaquer
3. Commandement : Donner une attaque supplémentaire aux alliés stratégiques
```

#### Compétences d'Attaque Spéciale
```
1. Pluie de flèches : Maximiser les dégâts de zone
2. Tir précis : Éliminer les cibles importantes
3. Explosion sacrée : Sacrifice tactique pour dégâts maximums
```

#### Compétences Passives Automatiques
```
1. Nécromancie/Invocation : Invoquer des renforts
2. Bouclier de la foi : Protéger les alliés adjacents
3. Aura sacrée : Buffer les attaquants adjacents
```

### Phase 2: Évaluation des Cibles

#### Système de Score de Cible (0-100)
L'IA évalue chaque ennemi selon plusieurs critères :

**Facteurs Positifs (augmentent la priorité) :**
- **PV faibles** : Plus l'ennemi a peu de PV, plus il est prioritaire
- **Tier élevé** : Les unités puissantes sont prioritaires
- **Menace directe** : Ennemis pouvant attaquer des alliés importants
- **Position stratégique** : Ennemis mal positionnés ou isolés
- **Kill potential** : Capacité à éliminer la cible en une attaque

**Facteurs Négatifs (diminuent la priorité) :**
- **Distance élevée** : Coût en PM pour atteindre la cible
- **Position défensive** : Cibles protégées par des alliés
- **Résistances** : Armure de pierre, boucliers, etc.

#### Formule de Score Typique
```python
score_base = (100 - cible.pv) + (cible.tier * 10)
score_position = max(0, 50 - distance_hex * 5)
score_menace = evaluation_menace_pour_allies(cible) * 15
score_elimination = 30 if peut_tuer_en_une_attaque(cible) else 0

score_final = score_base + score_position + score_menace + score_elimination
```

### Phase 3: Optimisation de Positionnement

#### Choix de la Position d'Attaque
L'IA sélectionne la meilleure position selon :
1. **Coût minimum** en PM pour atteindre la position
2. **Sécurité** : Éviter les contre-attaques
3. **Flexibilité** : Maintenir des options pour le tour suivant
4. **Support** : Rester proche des alliés si nécessaire

## 🎪 Stratégies Spécialisées

### Gestion des Compétences Passives Tactiques

#### Compétences Défensives
- **Protection** : Placement optimal pour couvrir les alliés fragiles
- **Armure de pierre** : Positionnement en première ligne
- **Enracinement** : Optimisation pour la régénération

#### Compétences Offensives
- **Rage** : Accumulation progressive des stacks d'attaque
- **Sangsue** : Prioriser les cibles qui donnent le plus de PV
- **Lumière vengeresse** : Cibler les Morts-Vivants en priorité

#### Compétences de Contrôle
- **Manipulation** : Cibler les unités faibles pour les retourner
- **Venin incapacitant** : Bloquer les unités mobiles importantes
- **Combustion différée** : Marquer les cibles résistantes

### Stratégies de Groupe

#### Formation Défensive
- Placement des **Gardes royaux** (Protection) devant les unités fragiles
- **Golems** (Armure de pierre) comme tanks principaux
- **Clercs** et **Esprits Saints** en soutien arrière

#### Formation Offensive
- **Archers** avec Pluie de flèches pour le contrôle de zone
- **Centaures** avec Tir précis pour l'élimination ciblée
- **Rois** avec Commandement pour amplifier les attaques

## 🔧 Paramètres de Difficulté

### Seuils de Décision Adaptatifs
L'IA ajuste ses seuils selon la compétence :

```python
# Seuils pour l'utilisation des compétences
SEUILS_COMPETENCES = {
    "soin": 15,           # Seuil bas = utilise souvent
    "benediction": 25,    # Seuil modéré
    "commandement": 30,   # Seuil élevé = utilise sélectivement
    "pluie_de_fleches": 40,  # Doit être très rentable
}
```

### Cooldowns et Limitations
- **Compétences à cooldown** : Utilisées stratégiquement quand disponibles
- **Compétences uniques** : Gardées pour les moments critiques
- **Gestion des ressources** : Équilibre entre attaques et compétences

## 🎲 Gestion des Probabilités

### Compétences à Probabilité
- **Renaissance (80%)** : L'IA compte sur cette résurrection tactique
- **Vol** : Première attaque ignorée prise en compte
- **Manipulation** : Conversion temporaire intégrée dans la stratégie

### Prise de Risque Calculée
L'IA évalue les scénarios optimistes et pessimistes :
- **Scénario optimiste** : Toutes les probabilités favorables
- **Scénario pessimiste** : Toutes les probabilités défavorables  
- **Décision finale** : Basée sur l'espérance mathématique

## 🚀 Optimisations Avancées

### Évaluation Multi-Tours
L'IA peut anticiper les conséquences sur plusieurs tours :
- **Combustion différée** : Planifier les éliminations futures
- **Manipulation** : Prévoir les retournements temporaires
- **Cooldowns** : Planifier l'usage optimal des compétences

### Synergie des Compétences
Reconnaissance et exploitation des combos :
- **Commandement → Attaque buffée** : Séquence optimale
- **Bénédiction → Attaque multiple** : Amplification des dégâts
- **Protection → Positionnement agressif** : Tactique coordonnée

## 📊 Métriques de Performance

### Indicateurs Tactiques
- **Efficacité d'élimination** : Ratio kills/tours
- **Utilisation des compétences** : Pourcentage d'usage optimal
- **Survie des alliés** : Taux de préservation des unités importantes
- **Contrôle territorial** : Domination du terrain de jeu

### Adaptation Dynamique
L'IA ajuste sa stratégie selon :
- **Composition d'équipe** : Adapter aux forces/faiblesses
- **État de la bataille** : Offensive/défensive selon la situation
- **Ressources restantes** : Gestion des PM/attaques disponibles

---

*Cette documentation reflète l'état actuel du système d'IA de HexMaster. Le système continue d'évoluer pour offrir des défis tactiques toujours plus intéressants et réalistes.*