"""
Utilitaires pour la gestion des chemins de fichiers,
compatible avec les versions EXE (PyInstaller) et développement.
"""
import os
import sys
import shutil
from pathlib import Path

def get_exe_dir():
    """Retourne le répertoire où se trouve l'exécutable"""
    if getattr(sys, 'frozen', False):
        # Mode EXE (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Mode développement
        return Path(__file__).parent

def get_user_data_dir():
    """Retourne le répertoire pour les données utilisateur (externe à l'EXE)"""
    exe_dir = get_exe_dir()
    return exe_dir / "HexMaster_Data"

def get_resource_path(relative_path):
    """Obtient le chemin vers une ressource, que ce soit en développement ou EXE"""
    if getattr(sys, 'frozen', False):
        # Mode EXE : ressources dans le bundle PyInstaller
        meipass = getattr(sys, '_MEIPASS', Path(sys.executable).parent)
        return Path(meipass) / relative_path
    else:
        # Mode développement : ressources dans le répertoire du script
        return Path(__file__).parent / relative_path

def ensure_user_directories():
    """S'assure que les répertoires utilisateur existent et copie les ressources par défaut"""
    user_data_dir = get_user_data_dir()
    
    # Créer le répertoire principal des données utilisateur
    user_data_dir.mkdir(exist_ok=True)
    
    # Répertoires à créer/copier
    directories_to_setup = [
        ("Campagne", True),  # (nom_dossier, copier_depuis_exe)
        ("custom_levels", False)
    ]
    
    for dir_name, copy_from_exe in directories_to_setup:
        user_dir = user_data_dir / dir_name
        
        # Si le dossier n'existe pas dans les données utilisateur
        if not user_dir.exists():
            if copy_from_exe:
                # Copier depuis les ressources de l'EXE
                resource_dir = get_resource_path(dir_name)
                if resource_dir.exists():
                    print(f"Copie de {dir_name} depuis l'EXE vers les données utilisateur...")
                    shutil.copytree(resource_dir, user_dir)
                    print(f"✅ {dir_name} copié avec succès")
                else:
                    print(f"⚠️ Ressource {dir_name} non trouvée dans l'EXE")
                    user_dir.mkdir(exist_ok=True)
            else:
                # Créer un dossier vide
                user_dir.mkdir(exist_ok=True)
                print(f"✅ Dossier {dir_name} créé")

def get_levels_path(folder_name="custom_levels"):
    """Retourne le chemin vers un dossier de niveaux (toujours externe)"""
    if getattr(sys, 'frozen', False):
        # Mode EXE : utiliser les données utilisateur externes
        return get_user_data_dir() / folder_name
    else:
        # Mode développement : utiliser le dossier local
        return Path(__file__).parent / folder_name

def get_campaign_path():
    """Retourne le chemin vers les niveaux de campagne"""
    return get_levels_path("Campagne")

def get_custom_levels_path():
    """Retourne le chemin vers les niveaux custom"""
    return get_levels_path("custom_levels")

def get_save_path():
    """Retourne le chemin vers le fichier de sauvegarde"""
    if getattr(sys, 'frozen', False):
        # Mode EXE : sauvegarde externe
        return get_user_data_dir() / "sauvegarde.json"
    else:
        # Mode développement : sauvegarde locale
        return Path(__file__).parent / "sauvegarde.json"

# Initialiser les répertoires au chargement du module (seulement en mode EXE)
if __name__ != "__main__" and getattr(sys, 'frozen', False):
    try:
        ensure_user_directories()
    except Exception as e:
        print(f"Erreur lors de l'initialisation des répertoires : {e}")
