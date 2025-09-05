# IA Enrichie - Documentation

## Améliorations de l'IA

### 1. IA Classique (`cible_faible`) - Améliorée
- **Avant** : Attaquait seulement les ennemis
- **Maintenant** : 
  - ✅ Utilise les compétences immédiates (explosion sacrée, bouclier de la foi, etc.)
  - ✅ Utilise les compétences actives sur cibles (soin, bénédiction)
  - ✅ Puis procède à l'attaque classique

### 2. Nouvelle IA Tactique (`ia_tactique_avancee`)
Une IA beaucoup plus intelligente avec :

#### Phase 1 : Analyse Situationnelle
- Identifie les alliés et ennemis
- Évalue l'état général du combat

#### Phase 2 : Support Prioritaire
- **Soin d'urgence** : Soigne en priorité les alliés à ≤2 PV
- **Bénédiction tactique** : Buff l'allié le plus offensif qui peut attaquer

#### Phase 3 : Compétences Immédiates
- **Explosion sacrée** : Si ≥2 ennemis adjacents et rentable
- **Bouclier de la foi** : Si alliés adjacents vulnérables
- **Aura sacrée** : Si alliés adjacents peuvent attaquer
- **Nécromancie/Invocation** : Invoque sur positions stratégiques

#### Phase 4 : Attaque Adaptative
- **Évaluation multi-critères** des cibles :
  - PV ennemis (priorité aux faibles)
  - Danger ennemi (dégâts, tier)
  - Distance à la cible
  - Menace sur alliés
  - Compétences dangereuses

- **Positionnement tactique** :
  - Évite les positions dangereuses
  - Reste près des alliés pour le soutien
  - Optimise le coût en PM

## Compétences Gérées Intelligemment

### Compétences de Support
- **Soin** : Priorité aux alliés critiques, puis aux plus blessés
- **Bénédiction** : Priorité aux unités offensives qui peuvent attaquer

### Compétences Offensives
- **Explosion sacrée** : Calcul coût/bénéfice avant sacrifice
- **Attaques normales** : Évaluation multi-critères des cibles

### Compétences de Zone
- **Bouclier de la foi** : Active si alliés adjacents vulnérables
- **Aura sacrée** : Active si alliés adjacents offensifs
- **Nécromancie/Invocation** : Positionnement stratégique

## Intégration dans le Jeu

### Modes utilisant l'IA Avancée
- ✅ **Campagne** : `ia_tactique_avancee`
- ✅ **HexArène** : `ia_tactique_avancee`
- ✅ **Mode Mixte** : `ia_tactique_avancee`
- ✅ **Level Builder (Test)** : `ia_tactique_avancee`

### Compatibilité
- ✅ Fonctionne avec tous les types d'unités
- ✅ Compatible avec toutes les compétences existantes
- ✅ Extensible pour nouvelles compétences

## Avantages pour le Joueur

1. **Défis Plus Intéressants** : L'IA utilise ses compétences de manière intelligente
2. **Réalisme Tactique** : L'IA soigne ses alliés, utilise des buffs, etc.
3. **Variété** : Chaque combat est plus imprévisible et stratégique
4. **Apprentissage** : Le joueur apprend en voyant l'IA utiliser les compétences

## Performance

- **Optimisé** : Évaluation efficace avec scores pondérés
- **Robuste** : Gestion d'erreurs et fallbacks
- **Maintenable** : Code modulaire et bien documenté
