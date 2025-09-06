# 🚀 Releases Automatiques HexMaster

## Comment ça fonctionne

À chaque push sur la branche `main`, une nouvelle version exécutable de HexMaster est automatiquement créée et mise à disposition.

## 📥 Télécharger la dernière version

1. Allez dans l'onglet **[Releases](../../releases)** de ce repository
2. Téléchargez le fichier `HexMaster.exe` de la dernière release
3. Lancez directement le jeu (aucune installation requise !)

## 🔄 Système de versioning

- **Format des versions :** `vYYYY.MM.DD.HHMM` (ex: `v2025.09.06.1430`)
- **Nettoyage automatique :** Seules les 5 dernières versions sont conservées
- **Release "Latest" :** La version la plus récente est toujours marquée comme "Latest"

## 🛠️ Fichiers de configuration

- `.github/workflows/build.yml` - Version classique avec actions GitHub standard
- `.github/workflows/release.yml` - Version moderne avec GitHub CLI (recommandée)

## 🎮 Avantages

✅ **Accès public :** Tous ceux qui ont accès au repo peuvent télécharger le jeu  
✅ **Pas d'artefacts temporaires :** Les exécutables sont des releases permanentes  
✅ **Historique des versions :** Possibilité de télécharger les versions précédentes  
✅ **Automatisation complète :** Aucune intervention manuelle requise  
✅ **Notifications :** GitHub peut notifier des nouvelles releases  

## 🔧 Pour les développeurs

Pour déclencher manuellement une nouvelle release :
1. Allez dans l'onglet **Actions**
2. Sélectionnez "Build and Release EXE (Modern)"
3. Cliquez sur "Run workflow"

Le processus prend environ 2-3 minutes et créera automatiquement une nouvelle release avec l'exécutable.
