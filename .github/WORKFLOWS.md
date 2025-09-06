# 📋 Documentation Technique - GitHub Actions

## Vue d'ensemble

Ce repository utilise GitHub Actions pour automatiser la création d'exécutables à chaque push sur `main`.

## 🔧 Workflows disponibles

### 1. `release.yml` - Workflow principal (recommandé)
- **Déclencheur :** Push sur `main` + déclenchement manuel
- **Actions :** Utilise GitHub CLI pour créer les releases
- **Avantages :** Plus moderne, gestion automatique du nettoyage
- **Statut :** ✅ Actif

### 2. `build.yml` - Workflow legacy 
- **Déclencheur :** Déclenchement manuel uniquement
- **Actions :** Utilise les actions GitHub classiques
- **Avantages :** Plus stable, moins de dépendances
- **Statut :** ⏸️ Désactivé (disponible en backup)

### 3. `manual-release.yml` - Workflow de fallback
- **Déclencheur :** Déclenchement manuel avec options
- **Actions :** Version simplifiée pour les cas d'urgence
- **Avantages :** Permet de spécifier un suffixe de version
- **Statut :** 🟡 Disponible en cas de problème

## 🏗️ Processus de build

1. **Checkout du code** - Récupération du code source
2. **Setup Python 3.11** - Installation de l'environnement Python
3. **Installation des dépendances** - `pip install -r requirements.txt` + `pyinstaller`
4. **Build de l'exécutable** - `pyinstaller main.spec`
5. **Génération du tag de version** - Format `vYYYY.MM.DD.HHMM`
6. **Création de la release** - Upload de l'exécutable
7. **Nettoyage** - Suppression des anciennes releases (garde les 5 dernières)

## 📋 Configuration requise

### Permissions GitHub
Le repository doit avoir les permissions suivantes pour les GitHub Actions :
- ✅ `contents: write` - Pour créer des releases et tags
- ✅ `GITHUB_TOKEN` - Token automatique (déjà disponible)

### Fichiers requis
- ✅ `main.spec` - Configuration PyInstaller
- ✅ `requirements.txt` - Dépendances Python
- ✅ `main.py` - Point d'entrée de l'application

## 🔄 Versioning

### Format des versions
```
vYYYY.MM.DD.HHMM
```
Exemple : `v2025.09.06.1430` = 6 septembre 2025, 14h30

### Nettoyage automatique
- Garde les **5 dernières releases**
- Supprime automatiquement les anciennes versions
- Évite l'accumulation de fichiers

## 🚨 Dépannage

### Problèmes courants

#### Build échoue
1. Vérifier `requirements.txt`
2. Tester localement avec `test_build.ps1`
3. Vérifier les logs dans l'onglet Actions

#### Release non créée
1. Vérifier les permissions du repository
2. S'assurer que `GITHUB_TOKEN` est disponible
3. Utiliser le workflow de fallback `manual-release.yml`

#### Conflit de versions
1. Supprimer manuellement la release problématique
2. Re-déclencher le workflow

### Tests locaux
Utilisez le script `test_build.ps1` pour tester la build localement :
```powershell
.\test_build.ps1
```

## 📊 Monitoring

### Vérifier le statut
1. Aller dans l'onglet **Actions** du repository
2. Voir les builds récentes et leur statut
3. Consulter les logs en cas d'erreur

### Notifications
GitHub peut envoyer des notifications :
- Par email pour les builds échouées
- Via l'interface web pour les nouvelles releases

## 🔧 Maintenance

### Mise à jour des workflows
1. Modifier les fichiers dans `.github/workflows/`
2. Tester sur une branche de développement
3. Merger sur `main` une fois validé

### Mise à jour des dépendances
Les workflows utilisent :
- `actions/checkout@v4`
- `actions/setup-python@v5`
- `softprops/action-gh-release@v1` (backup)
- GitHub CLI (workflow principal)

## 📝 Logs et debugging

### Accès aux logs
1. Onglet **Actions** → Sélectionner un workflow
2. Cliquer sur un job pour voir les détails
3. Développer chaque étape pour voir les logs

### Variables utiles
- `${{ github.sha }}` - Hash du commit
- `${{ github.ref_name }}` - Nom de la branche
- `${{ steps.version.outputs.VERSION }}` - Version générée
