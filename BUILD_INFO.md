# HexMaster - Informations de Build

## Configuration de compilation

Ce projet utilise **PyInstaller** en mode `onedir` pour créer des exécutables optimisés pour la sécurité et la compatibilité.

### Commande de build
```bash
pyinstaller --clean --noconfirm main.spec
```

### Configuration (main.spec)
- **Mode**: `onedir` (dossier de distribution)
- **UPX**: Désactivé (pour éviter les faux positifs antivirus)
- **Console**: Désactivée (application graphique)
- **Optimisations**: Minimales pour la transparence

### Structure de sortie
```
dist/HexMaster/
├── HexMaster.exe          # Exécutable principal
└── _internal/             # Dépendances et données
    ├── Campagne/          # Données de campagne
    ├── custom_levels/     # Niveaux personnalisés
    └── [bibliothèques]    # Python runtime, pygame, etc.
```

## Vérification de sécurité

### Reproduction du build
1. Cloner le dépôt à la révision exacte
2. Installer Python 3.11 et les dépendances (`pip install -r requirements.txt`)
3. Exécuter `pyinstaller --clean --noconfirm main.spec`
4. Comparer les hashs SHA256

### Antivirus
Cette configuration minimise les faux positifs :
- ✅ Mode `onedir` (vs `onefile`)  
- ✅ UPX désactivé
- ✅ Build `--clean` systématique
- ✅ PyInstaller récent

### Hash SHA256
Chaque release inclut le hash SHA256 de l'archive pour vérification d'intégrité.

## Alternatives de sécurité

Si votre antivirus signale encore des problèmes :
1. **Build manuelle** : Clonez et compilez vous-même
2. **Whitelist** : Ajoutez le dossier à l'exclusion antivirus
3. **Version source** : Exécutez directement `python main.py`

## Contact sécurité

Pour signaler un faux positif d'antivirus ou une préoccupation de sécurité :
- Ouvrir une issue GitHub avec le détail de la détection
- Inclure le nom de l'antivirus et la version
- Mentionner le hash SHA256 du fichier concerné