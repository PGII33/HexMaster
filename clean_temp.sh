#!/bin/bash
# Script de nettoyage des fichiers temporaires avant commit

echo "🧹 Nettoyage des fichiers temporaires..."

# Supprimer les caches Python
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Supprimer les dossiers de build temporaires
rm -rf build/ dist/ HexMaster_Portable*/ *.tar.gz *.zip

# Supprimer le dossier de données de test
rm -rf HexMaster_Data/

# Supprimer les logs temporaires
rm -f *.log test_output.log build.log

# Supprimer les fichiers de test temporaires (sauf ceux commençant par test_ qui sont dans .gitignore)
rm -f temp_* 

echo "✅ Nettoyage terminé !"
echo ""
echo "📋 Fichiers à commiter :"
git status --porcelain | grep -v "^??" | head -20
