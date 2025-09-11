# 🎮 HexMaster - Système de Données Externes

## 📋 Problème résolu

**Avant :** Les niveaux créés avec l'éditeur dans la version EXE disparaissaient après fermeture car ils étaient créés dans un dossier temporaire PyInstaller.

**Maintenant :** 🎉 **Tous les niveaux créés sont sauvegardés de façon permanente dans un dossier externe accessible !**

## 🏗️ Architecture du nouveau système

### Structure des fichiers (Version EXE)
```
📁 HexMaster_Portable/
├── 🎮 HexMaster.exe                 # Jeu principal
├── 📁 HexMaster_Data/               # Données externes (PERMANENT)
│   ├── 📁 Campagne/                 # Niveaux de campagne (modifiables)
│   │   ├── 📁 01_Religieux/
│   │   │   └── 📁 01_Niveau/
│   │   │       └── 📄 niveau.json
│   │   └── 📁 02_Elementaires/
│   ├── 📁 custom_levels/            # VOS CRÉATIONS (persistent !)
│   │   ├── 📁 MonNiveau1/
│   │   │   └── 📄 niveau.json
│   │   └── 📁 MonNiveau2/
│   └── 💾 sauvegarde.json           # Progression (créé automatiquement)
├── 📄 README.txt                    # Guide d'utilisation
└── 🚀 Lancer_HexMaster.bat          # Script de lancement
```

### Fonctionnement technique

1. **Au premier lancement** de l'EXE :
   - Le dossier `HexMaster_Data/` est créé automatiquement
   - Les niveaux de campagne sont copiés depuis l'EXE vers `HexMaster_Data/Campagne/`
   - Le dossier `custom_levels/` est créé vide

2. **Lors de la création d'un niveau** :
   - L'éditeur sauvegarde dans `HexMaster_Data/custom_levels/NomDuNiveau/`
   - Le niveau reste accessible après redémarrage

3. **Chargement des niveaux** :
   - Le jeu lit d'abord dans `HexMaster_Data/` (externe)
   - Fallback vers les ressources intégrées à l'EXE si nécessaire

## 🛠️ Composants techniques

### `path_utils.py` - Gestionnaire de chemins unifié
```python
# Détection automatique développement vs EXE
def get_exe_dir(): ...           # Dossier de l'EXE
def get_user_data_dir(): ...     # HexMaster_Data/
def get_campaign_path(): ...     # Campagne externe
def get_custom_levels_path(): ... # custom_levels externe
def get_save_path(): ...         # sauvegarde.json externe
```

### Modifications des modules existants
- **`level_builder.py`** : Utilise les nouveaux chemins
- **`sauvegarde.py`** : Sauvegarde externe
- **`main.spec`** : Configuration PyInstaller mise à jour

### Système de build automatisé
- **GitHub Actions** : Build Windows et Linux automatique
- **Package portable** : Structure complète avec documentation
- **Tests de simulation** : Validation avant compilation

## 🚀 Utilisation

### Pour l'utilisateur final
1. **Télécharger** : `HexMaster_Portable_Windows.zip`
2. **Extraire** dans un dossier
3. **Lancer** : `HexMaster.exe`
4. **Créer des niveaux** : Menu → Éditeur de Niveaux
5. **Profiter** : Les niveaux restent disponibles ! 🎉

### Pour le développement
```bash
# Test en mode développement
python3 main.py

# Test de simulation EXE
python3 test_exe_simulation.py

# Build local (Linux)
./build_local.sh

# Build automatique (GitHub Actions)
git push  # Déclenchement automatique
```

## 🎯 Avantages du nouveau système

### ✅ Pour les utilisateurs
- **Persistance garantie** des niveaux créés
- **Modification possible** des niveaux de campagne
- **Sauvegarde externe** facile à sauvegarder
- **Structure claire** et documentée

### ✅ Pour les développeurs
- **Code unifié** développement/EXE
- **Tests automatisés** avant build
- **Build reproductible** via GitHub Actions
- **Architecture modulaire** et extensible

### ✅ Pour la distribution
- **Package complet** avec documentation
- **Installation simple** (extraction + lancement)
- **Compatibilité** Windows et Linux
- **Releases automatiques** avec changelog

## 🔧 Configuration GitHub Actions

Le workflow `build.yml` génère automatiquement :

### Sur push vers `main`
- **Build de test** (artefacts temporaires)
- **Validation** de la compilation

### Sur tag `v*.*.*` ou déclenchement manuel
- **Release complète** avec ZIP portable
- **Documentation** automatique
- **Publication** sur GitHub Releases

### Structure de la release
```
🎯 HexMaster v2024.01.15
├── 📦 HexMaster_Portable_Windows.zip
├── 📦 HexMaster_Portable_Linux.tar.gz
├── 📄 Release notes automatiques
└── 📋 Instructions d'installation
```

## 🐛 Dépannage

### Problème : Niveaux ne se sauvent pas
**Solution :** Vérifier que `HexMaster_Data/custom_levels/` existe et est accessible en écriture.

### Problème : EXE ne se lance pas
**Solutions :**
- Vérifier les permissions d'exécution
- Extraire tous les fichiers du ZIP
- Utiliser le script `Lancer_HexMaster.bat`

### Problème : Niveaux de campagne manquants
**Solution :** 
1. Supprimer le dossier `HexMaster_Data/`
2. Relancer l'EXE pour reconstruction automatique

## 🚀 Roadmap future

### Améliorations possibles
- **Import/Export** de niveaux entre utilisateurs
- **Workshop Steam** (si distribution Steam)
- **Éditeur avancé** avec plus d'options
- **Partage en ligne** de créations
- **Validation automatique** des niveaux

---

**🎉 Résultat final :** L'éditeur de niveaux est maintenant **100% fonctionnel en version EXE** avec **persistance garantie** des créations ! 🏆
