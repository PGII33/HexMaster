import json
import os

FICHIER_SAVE = "sauvegarde.json"

def charger():
    try:
        with open("sauvegarde.json", "r", encoding="utf-8") as f:
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
