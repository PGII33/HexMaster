#!/bin/bash
# Script de build local pour tester avant GitHub Actions

set -e  # Arrêter en cas d'erreur

echo "🚀 === Build Local HexMaster avec Support Données Externes ==="

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "main.py" ] || [ ! -f "main.spec" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le répertoire racine de HexMaster"
    exit 1
fi

echo "📁 Préparation des répertoires de build..."

# Nettoyer les builds précédents
rm -rf dist/ build/ HexMaster_Portable/ HexMaster_Portable_Linux.tar.gz

# S'assurer que les dossiers requis existent
mkdir -p custom_levels
if [ ! -f "custom_levels/.keep" ]; then
    echo "# Dossier pour les niveaux créés par l'utilisateur" > custom_levels/.keep
fi

echo "🔧 Vérification des dépendances..."

# Vérifier PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installation de PyInstaller..."
    pip install pyinstaller
else
    echo "✅ PyInstaller disponible"
fi

echo "🏗️ Construction de l'exécutable..."

# Build avec PyInstaller
pyinstaller --clean --noconfirm main.spec

# Vérifier que l'exécutable a été créé
if [ -f "dist/HexMaster" ]; then
    echo "✅ Exécutable créé avec succès: dist/HexMaster"
    ls -lh dist/HexMaster
else
    echo "❌ Erreur: Exécutable non trouvé"
    ls -la dist/
    exit 1
fi

echo "📦 Création du package portable..."

# Créer la structure portable
PACKAGE_DIR="HexMaster_Portable_Linux"
mkdir -p "$PACKAGE_DIR"

# Copier l'exécutable
cp "dist/HexMaster" "$PACKAGE_DIR/"
chmod +x "$PACKAGE_DIR/HexMaster"

# Créer la structure de données externe
mkdir -p "$PACKAGE_DIR/HexMaster_Data/Campagne"
mkdir -p "$PACKAGE_DIR/HexMaster_Data/custom_levels"

# Copier les niveaux de campagne
cp -r Campagne/* "$PACKAGE_DIR/HexMaster_Data/Campagne/"

# Créer le fichier README
cat > "$PACKAGE_DIR/README.txt" << 'EOF'
# HexMaster - Edition Portable Linux

## 🚀 Démarrage rapide
Ouvrez un terminal dans ce dossier et tapez : ./HexMaster
Ou utilisez le script : ./launch_hexmaster.sh

## 📁 Structure des fichiers
- **HexMaster** : Jeu principal (exécutable Linux)
- **HexMaster_Data/** : Toutes vos données de jeu
  - **Campagne/** : Niveaux de campagne (vous pouvez les modifier !)
  - **custom_levels/** : Vos niveaux créés avec l'éditeur
  - **sauvegarde.json** : Votre progression (créé automatiquement)

## 🎮 Fonctionnalités
- ✅ Campagne complète avec progression
- ✅ Mode HexArène (combat contre IA)
- ✅ Mode Joueur vs Joueur local
- ✅ **Éditeur de niveaux intégré** 
- ✅ **Niveaux créés sauvegardés de façon permanente**
- ✅ Système de points et déblocage d'unités

## 🔧 Créer vos propres niveaux
1. Lancez le jeu : ./HexMaster
2. Menu Principal → Éditeur de Niveaux
3. Créez votre niveau
4. Sauvegardez-le
5. Il apparaîtra dans la liste des niveaux disponibles !

**Les niveaux créés sont sauvegardés dans :** HexMaster_Data/custom_levels/

## 💾 Sauvegarde de progression
Votre progression est automatiquement sauvegardée dans :
**HexMaster_Data/sauvegarde.json**

## 🛠️ Dépannage
- Si le jeu ne se lance pas : 
  chmod +x HexMaster
  ./HexMaster
- Si vos niveaux disparaissent : ils sont dans HexMaster_Data/custom_levels/
- Si la progression est perdue : restaurez sauvegarde.json

## Prérequis système
- Linux (testé sur Ubuntu/Debian)
- Python 3.11+ (inclus dans l'exécutable)
- Bibliothèques graphiques de base (généralement préinstallées)
EOF

# Script de lancement Linux
cat > "$PACKAGE_DIR/launch_hexmaster.sh" << 'EOF'
#!/bin/bash
echo "=================================="
echo "     HexMaster - Lanceur Linux"
echo "=================================="
echo
echo "Vérification des dossiers..."

# Créer les dossiers de données si nécessaire
mkdir -p "HexMaster_Data/custom_levels"

echo "Lancement de HexMaster..."
echo

# Lancer le jeu
./HexMaster

echo
echo "HexMaster fermé."
EOF

chmod +x "$PACKAGE_DIR/launch_hexmaster.sh"

echo "✅ Package portable créé avec support des données externes"

# Lister le contenu
echo "📋 Contenu du package:"
find "$PACKAGE_DIR" -type f | sort

# Créer l'archive
echo "🗜️ Création de l'archive..."
tar -czf "HexMaster_Portable_Linux.tar.gz" "$PACKAGE_DIR"

echo "✅ Archive créée: HexMaster_Portable_Linux.tar.gz"
ls -lh "HexMaster_Portable_Linux.tar.gz"

echo ""
echo "🎉 === Build terminé avec succès ! ==="
echo ""
echo "📦 Fichiers générés:"
echo "   • dist/HexMaster                      (exécutable seul)"
echo "   • HexMaster_Portable_Linux/           (package complet)"
echo "   • HexMaster_Portable_Linux.tar.gz     (archive portable)"
echo ""
echo "🧪 Test recommandé:"
echo "   cd HexMaster_Portable_Linux"
echo "   ./HexMaster"
echo ""
echo "🚀 Prêt pour la distribution !"
