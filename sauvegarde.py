import json
import os
from const import D_CP, D_PA, D_UNITES
from path_utils import get_save_path

FICHIER_SAVE = str(get_save_path())


def charger():
    """Charge la sauvegarde ou crée une nouvelle si elle n'existe pas."""
    try:
        with open(FICHIER_SAVE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Garantir la structure minimale
            if "cp" not in data:
                data["cp"] = D_CP
            if "pa" not in data:
                data["pa"] = D_PA
            if "unites" not in data:
                data["unites"] = list(D_UNITES)
            if "campagne_progression" not in data:
                data["campagne_progression"] = {}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return creer_sauvegarde_defaut()


def creer_sauvegarde_defaut():
    """Crée une sauvegarde par défaut."""
    return {
        "pa": D_PA,
        "unites": list(D_UNITES),
        "cp": D_CP,
        "campagne_progression": {}
    }


def sauvegarder(data):
    """Sauvegarde les données."""
    try:
        os.makedirs(os.path.dirname(FICHIER_SAVE), exist_ok=True)
        with open(FICHIER_SAVE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")


def marquer_niveau_complete(chapitre_nom, numero_niveau):
    """Marque un niveau comme complété."""
    data = charger()
    if chapitre_nom not in data["campagne_progression"]:
        data["campagne_progression"][chapitre_nom] = {"niveaux_completes": []}
    
    if numero_niveau not in data["campagne_progression"][chapitre_nom]["niveaux_completes"]:
        data["campagne_progression"][chapitre_nom]["niveaux_completes"].append(numero_niveau)
        sauvegarder(data)


def appliquer_recompenses(niveau_config):
    """Applique les récompenses d'un niveau."""
    if not niveau_config:
        return
    
    data = charger()
    
    # Récompenses CP
    if hasattr(niveau_config, 'recompense_cp') and niveau_config.recompense_cp > 0:
        data["cp"] += niveau_config.recompense_cp
        print(f"+{niveau_config.recompense_cp} CP (Total: {data['cp']})")
    
    # Récompenses PA
    if hasattr(niveau_config, 'recompense_pa') and niveau_config.recompense_pa > 0:
        data["pa"] += niveau_config.recompense_pa
        print(f"+{niveau_config.recompense_pa} PA (Total: {data['pa']})")
    
    # Débloquer unités
    if hasattr(niveau_config, 'unites_debloquees') and niveau_config.unites_debloquees:
        for unite_nom in niveau_config.unites_debloquees:
            if unite_nom not in data["unites"]:
                data["unites"].append(unite_nom)
                print(f"Unité débloquée: {unite_nom}")
    
    sauvegarder(data)


def est_niveau_complete(chapitre_nom, numero_niveau):
    """Vérifie si un niveau est complété."""
    data = charger()
    progression = data["campagne_progression"].get(chapitre_nom, {})
    return numero_niveau in progression.get("niveaux_completes", [])


def est_chapitre_disponible(chapitre_nom, chapitres_ordonnes):
    """Vérifie si un chapitre est disponible."""
    # Le premier chapitre est toujours disponible
    if chapitre_nom == chapitres_ordonnes[0]:
        return True
    
    # Trouver le chapitre précédent
    try:
        index = chapitres_ordonnes.index(chapitre_nom)
        if index == 0:
            return True
        chapitre_precedent = chapitres_ordonnes[index - 1]
        
        # Vérifier qu'au moins un niveau du chapitre précédent est complété
        data = charger()
        progression = data["campagne_progression"].get(chapitre_precedent, {})
        return len(progression.get("niveaux_completes", [])) > 0
    except ValueError:
        return False


def est_niveau_disponible(chapitre_nom, numero_niveau, _structure_chapitre=None):
    """Vérifie si un niveau est disponible."""
    # Le niveau 1 est toujours disponible
    if numero_niveau == 1:
        return True
    
    # Vérifier que le niveau précédent est complété
    return est_niveau_complete(chapitre_nom, numero_niveau - 1)


def obtenir_progression_chapitre(chapitre_nom):
    """Retourne la progression d'un chapitre."""
    data = charger()
    return data["campagne_progression"].get(chapitre_nom, {"niveaux_completes": []})
