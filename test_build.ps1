#!/usr/bin/env powershell
# Script de test local pour vérifier que la build fonctionne
# Usage: .\test_build.ps1

Write-Host "🔧 Test de build local HexMaster" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Vérifier Python
Write-Host "Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python non trouvé ou non installé" -ForegroundColor Red
    exit 1
}

# Installer les dépendances
Write-Host "Installation des dépendances..." -ForegroundColor Yellow
try {
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller
    Write-Host "✅ Dépendances installées" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de l'installation des dépendances" -ForegroundColor Red
    exit 1
}

# Nettoyer les anciens builds
Write-Host "Nettoyage des anciens builds..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Construire l'exécutable
Write-Host "Construction de l'exécutable..." -ForegroundColor Yellow
try {
    pyinstaller main.spec
    Write-Host "✅ Build terminée" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de la build" -ForegroundColor Red
    exit 1
}

# Vérifier que l'exécutable a été créé
if (Test-Path "dist/HexMaster.exe") {
    $fileSize = (Get-Item "dist/HexMaster.exe").Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
    Write-Host "✅ Exécutable créé: dist/HexMaster.exe ($fileSizeMB MB)" -ForegroundColor Green
    
    # Optionnel: lancer le jeu pour test
    $response = Read-Host "Voulez-vous lancer le jeu pour tester ? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "🎮 Lancement du jeu..." -ForegroundColor Blue
        Start-Process "dist/HexMaster.exe"
    }
} else {
    Write-Host "❌ Erreur: HexMaster.exe non trouvé dans dist/" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Test de build terminé avec succès !" -ForegroundColor Green
