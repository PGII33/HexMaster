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
            # Vérifier que la Goule est débloquée par défaut
            if "unites" in data and "Goule" not in data["unites"]:
                data["unites"].append("Goule")
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "pa": 0,
            "unites": ["Goule"],  # Goule débloquée par défaut
            "cp": 5,  # CP de départ
            "campagne_progression": {
                "La grande église": {"niveaux_completes": [], "disponible": True}
            }
        }

def sauvegarder(data):
    with open(FICHIER_SAVE, "w") as f:
        json.dump(data, f, indent=2)


def appliquer_recompenses_niveau(niveau_config, chapitre_nom, numero_niveau):
    """Applique les récompenses d'un niveau et marque sa complétion."""
    if not niveau_config:
        return
    
    data = charger()
    
    # Vérifier si le niveau est déjà complété
    if chapitre_nom not in data["campagne_progression"]:
        data["campagne_progression"][chapitre_nom] = {
            "niveaux_completes": [],
            "disponible": True
        }
    
    niveau_deja_complete = numero_niveau in data["campagne_progression"][chapitre_nom]["niveaux_completes"]
    
    # Si le niveau ne peut pas être complété plusieurs fois et qu'il est déjà complété, pas de récompense
    if hasattr(niveau_config, 'completable_plusieurs_fois') and not niveau_config.completable_plusieurs_fois:
        if niveau_deja_complete:
            print(f"Niveau {chapitre_nom} - {numero_niveau} déjà complété, pas de récompense supplémentaire.")
            return
    
    # Marquer le niveau comme complété (même si déjà complété pour les niveaux répétables)
    if not niveau_deja_complete:
        data["campagne_progression"][chapitre_nom]["niveaux_completes"].append(numero_niveau)
    
    # Appliquer les récompenses CP
    if hasattr(niveau_config, 'recompense_cp') and niveau_config.recompense_cp > 0:
        data["cp"] = data.get("cp", 5) + niveau_config.recompense_cp
        print(f"Récompense: +{niveau_config.recompense_cp} CP (Total: {data['cp']})")
    
    # Appliquer les récompenses PA
    if hasattr(niveau_config, 'recompense_pa') and niveau_config.recompense_pa > 0:
        data["pa"] = data.get("pa", 100) + niveau_config.recompense_pa
        print(f"Récompense: +{niveau_config.recompense_pa} PA (Total: {data['pa']})")
    
    # Débloquer les unités récompenses (seulement si pas déjà complété)
    if hasattr(niveau_config, 'unites_debloquees') and niveau_config.unites_debloquees and not niveau_deja_complete:
        if "unites" not in data:
            data["unites"] = ["Goule"]
        
        nouvelles_unites = []
        for unite_nom in niveau_config.unites_debloquees:
            if unite_nom not in data["unites"]:
                data["unites"].append(unite_nom)
                nouvelles_unites.append(unite_nom)
        
        if nouvelles_unites:
            print(f"Nouvelles unités débloquées: {', '.join(nouvelles_unites)}")
    
    # Sauvegarder les changements
    sauvegarder(data)
    if niveau_deja_complete and hasattr(niveau_config, 'completable_plusieurs_fois') and niveau_config.completable_plusieurs_fois:
        print(f"Niveau {chapitre_nom} - {numero_niveau} complété à nouveau!")
    else:
        print(f"Niveau {chapitre_nom} - {numero_niveau} complété et sauvegardé!")


def niveau_est_complete(chapitre_nom, numero_niveau):
    """Vérifie si un niveau est déjà complété."""
    data = charger()
    
    if chapitre_nom not in data.get("campagne_progression", {}):
        return False
    
    return numero_niveau in data["campagne_progression"][chapitre_nom].get("niveaux_completes", [])


def obtenir_progression_chapitre(chapitre_nom):
    """Retourne la progression d'un chapitre."""
    data = charger()
    return data.get("campagne_progression", {}).get(chapitre_nom, {
        "niveaux_completes": [],
        "disponible": False
    })
