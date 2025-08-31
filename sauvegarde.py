import json
import os

FICHIER_SAVE = "sauvegarde.json"

def charger():
    if os.path.exists(FICHIER_SAVE):
        with open(FICHIER_SAVE, "r") as f:
            return json.load(f)
    # valeurs par défaut
    return {
        "pa": 20,           # Points d'âmes de départ
        "unites": []        # Liste des unités achetées
    }

def sauvegarder(data):
    with open(FICHIER_SAVE, "w") as f:
        json.dump(data, f, indent=2)
