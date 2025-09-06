# Modificateur de Niveau - Guide d'Utilisation

## Vue d'ensemble

Le modificateur de niveau permet de modifier des niveaux de campagne existants via l'interface Level Builder. Cette fonctionnalité a été intégrée au menu principal du Level Builder.

## Comment utiliser le modificateur

### 1. Accès au modificateur

1. Lancez le jeu avec `python main.py`
2. Allez dans **"Level Builder"** depuis le menu principal
3. Sélectionnez **"Modifier Niveau"** dans le menu du Level Builder

### 2. Sélection du niveau à modifier

- Une liste de tous les niveaux disponibles dans le dossier `Campagne/` s'affiche
- La liste montre le format : `Chapitre - Nom du niveau (Niveau X)`
- Utilisez la molette de la souris pour défiler dans la liste s'il y a beaucoup de niveaux
- Cliquez sur le niveau que vous souhaitez modifier

### 3. Modification du niveau

Une fois un niveau sélectionné, vous accédez aux mêmes interfaces que pour créer un nouveau niveau :

#### Configuration générale
- **Nom du niveau** : Modifiez le nom affiché
- **Description** : Ajoutez ou modifiez la description
- **Chapitre** : Changez le chapitre d'appartenance

#### Configuration des restrictions
- **Type de restriction** : Faction libre, faction unique, etc.
- **CP disponible** : Points de coût pour le joueur
- **Unités maximum** : Limite d'unités pour le joueur
- **Faction unique requise** : Obligation d'utiliser une seule faction
- **Faction imposée** : Force l'utilisation d'une faction spécifique

#### Configuration des ennemis
- **Sélection des unités ennemies** : Choisir les types d'unités
- **Placement des ennemis** : Positionner les unités sur la grille

#### Configuration des récompenses
- **CP de récompense** : Points de coût gagnés à la fin
- **PA de récompense** : Points d'amélioration gagnés
- **Unités débloquées** : Unités débloquées après victoire

### 4. Sauvegarde des modifications

- Cliquez sur **"Sauvegarder"** pour enregistrer vos modifications
- Le niveau sera sauvegardé dans le même fichier que l'original
- Un message de confirmation s'affiche en cas de succès
- Vous retournez automatiquement au menu principal du Level Builder

## Fonctionnalités techniques

### Structure des fichiers
- Les niveaux modifiés gardent leur emplacement d'origine
- Le fichier `niveau.json` est mis à jour avec les nouvelles données
- Aucun nouveau fichier n'est créé lors de la modification

### Validation
- Les mêmes règles de validation s'appliquent que pour la création
- Le système vérifie la cohérence des données avant sauvegarde

### Gestion des erreurs
- Affichage d'un message si aucun niveau n'est trouvé
- Gestion des erreurs de chargement/sauvegarde
- Protection contre les modifications incorrectes

## Cas d'usage

### Équilibrage de niveau
1. Modifier les CP disponibles pour ajuster la difficulté
2. Changer le nombre d'unités autorisées
3. Ajuster les récompenses selon la difficulté

### Correction de bugs
1. Corriger des positions d'ennemis problématiques
2. Modifier des configurations de faction incorrectes
3. Ajuster les types d'unités ennemies

### Amélioration du contenu
1. Ajouter des descriptions manquantes
2. Améliorer les noms de niveau
3. Ajuster les récompenses pour l'équilibrage général

## Limitations actuelles

- Le modificateur charge tous les niveaux en mémoire au démarrage
- La liste n'est pas mise à jour dynamiquement si des niveaux sont ajoutés pendant l'utilisation
- Pas de fonction d'annulation (undo) - les modifications sont définitives lors de la sauvegarde

## Code ajouté

### Nouvelles méthodes dans LevelBuilder
- `modifier_niveau()` : Point d'entrée pour la modification
- `_charger_liste_niveaux()` : Charge tous les niveaux disponibles
- `charger_niveau_pour_modification()` : Charge un niveau spécifique
- `sauvegarder_niveau_modifie()` : Sauvegarde spécialisée pour les modifications
- `afficher_selection_niveau()` : Interface de sélection
- `_handle_niveau_selection_click()` : Gestion des clics sur la liste
- `_handle_scroll()` : Gestion du scroll de la liste
- `_synchroniser_config_avec_ui()` : Synchronisation données/interface

### Modifications des méthodes existantes
- `creer_boutons()` : Ajout du bouton "Modifier Niveau" et gestion du nouvel état
- `run()` : Gestion des événements pour le nouvel état
- `sauvegarder_niveau()` : Détection automatique du mode (création/modification)
- `nouveau_niveau()` : Réinitialisation du niveau sélectionné
