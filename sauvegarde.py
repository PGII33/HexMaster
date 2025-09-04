import json
import os
import sys

def get_save_path():
    """Retourne le chemin correct du fichier de sauvegarde selon l'environnement"""
    if getattr(sys, 'frozen', False):
        # Application compilée avec PyInstaller
        # Le fichier sera dans le même dossier que l'EXE
        application_path = os.path.dirname(sys.executable)
    else:
        # Mode développement
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(application_path, "sauvegarde.json")

FICHIER_SAVE = get_save_path()

def charger():
    try:
        with open(FICHIER_SAVE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ajouter CP si pas présent
            if "cp" not in data:
                data["cp"] = 5  # CP de départ
            if "campagne_progression" not in data:
                data["campagne_progression"] = {
                    "La grande église": {"niveaux_completes": [], "disponible": True}
                }
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "pa": 100,
            "unites": [],
            "cp": 5,  # CP de départ
            "campagne_progression": {
                "La grande église": {"niveaux_completes": [], "disponible": True}
            }
        }

def sauvegarder(data):
    with open(FICHIER_SAVE, "w") as f:
        json.dump(data, f, indent=2)
