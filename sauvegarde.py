import json
import os
from const import D_CP, D_PA, D_UNITES

# Utiliser le nouveau système de chemins unifié
from path_utils import get_save_path
FICHIER_SAVE = str(get_save_path())

def charger():
    try:
        with open(FICHIER_SAVE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ajouter CP si pas présent
            if "cp" not in data:
                data["cp"] = D_CP  # CP de départ
            if "campagne_progression" not in data:
                data["campagne_progression"] = {
                    "Religieux": {"niveaux_completes": [], "disponible": True}
                }
            # S'assurer que le premier chapitre (Religieux) est toujours disponible
            if "Religieux" not in data["campagne_progression"]:
                data["campagne_progression"]["Religieux"] = {"niveaux_completes": [], "disponible": True}

            return data
    except FileNotFoundError:
        return creer_sauvegarde_defaut()
    except json.JSONDecodeError as e:
        print(f"Erreur de lecture JSON: {e}")
        return creer_sauvegarde_defaut()
    except Exception as e:
        print(f"Erreur inattendue lors du chargement: {e}")
        return creer_sauvegarde_defaut()

def creer_sauvegarde_defaut():
    """Crée une sauvegarde par défaut"""
    data = {
        "pa": D_PA,  # Points d'âmes de départ
        "unites": [unite for unite in D_UNITES],  # Goule débloquée par défaut
        "cp": D_CP,  # CP de départ
        "campagne_progression": {
            "Religieux": {"niveaux_completes": [], "disponible": True}
        }
    }
    return data

def sauvegarder(data):
    try:
        print(f"[DEBUG] Tentative de sauvegarde vers: {FICHIER_SAVE}")
        
        # S'assurer que le dossier parent existe
        os.makedirs(os.path.dirname(FICHIER_SAVE), exist_ok=True)
        
        # Tenter d'écrire le fichier
        with open(FICHIER_SAVE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[DEBUG] Sauvegarde réussie: {len(data)} éléments sauvés")
        
        # Vérifier que le fichier a bien été créé et contient des données
        if os.path.exists(FICHIER_SAVE):
            size = os.path.getsize(FICHIER_SAVE)
            print(f"[DEBUG] Fichier créé: {size} octets")
        else:
            print(f"[DEBUG] ERREUR: Le fichier n'a pas été créé!")
            
    except PermissionError as e:
        print(f"[ERREUR] Pas de permission d'écriture: {e}")
        print(f"[ERREUR] Chemin tentative: {FICHIER_SAVE}")
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la sauvegarde: {e}")
        print(f"[ERREUR] Chemin tentative: {FICHIER_SAVE}")

def obtenir_chemin_sauvegarde():
    """Retourne le chemin du fichier de sauvegarde pour debug"""
    return FICHIER_SAVE


def appliquer_recompenses_niveau(niveau_config, chapitre_nom, numero_niveau):
    """Applique les récompenses d'un niveau et marque sa complétion."""
    if not niveau_config:
        return
    
    # Convertir le nom de dossier en nom de chapitre affiché
    # Ex: "01_Religieux" -> "Religieux"
    if "_" in chapitre_nom:
        chapitre_display = chapitre_nom.split("_", 1)[1].replace("_", " ")
    else:
        chapitre_display = chapitre_nom
    
    data = charger()
    
    # Vérifier si le niveau est déjà complété
    if chapitre_display not in data["campagne_progression"]:
        data["campagne_progression"][chapitre_display] = {
            "niveaux_completes": [],
            "disponible": True
        }
    
    niveau_deja_complete = numero_niveau in data["campagne_progression"][chapitre_display]["niveaux_completes"]
    
    # Si le niveau ne peut pas être complété plusieurs fois et qu'il est déjà complété, pas de récompense
    if hasattr(niveau_config, 'completable_plusieurs_fois') and not niveau_config.completable_plusieurs_fois:
        if niveau_deja_complete:
            print(f"Niveau {chapitre_display} - {numero_niveau} déjà complété, pas de récompense supplémentaire.")
            return
    
    # Marquer le niveau comme complété (même si déjà complété pour les niveaux répétables)
    if not niveau_deja_complete:
        data["campagne_progression"][chapitre_display]["niveaux_completes"].append(numero_niveau)
    
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
        print(f"Niveau {chapitre_display} - {numero_niveau} complété à nouveau!")
    else:
        print(f"Niveau {chapitre_display} - {numero_niveau} complété et sauvegardé!")


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


def est_chapitre_disponible(chapitre_nom, chapitres_ordonnes):
    """Vérifie si un chapitre est disponible selon la progression."""
    # Migration automatique au premier accès
    migrer_progression_chapitre()
    
    data = charger()
    progression = data.get("campagne_progression", {})
    
    # Le premier chapitre est toujours disponible
    if chapitre_nom == chapitres_ordonnes[0]:
        return True
    
    # Trouver l'index du chapitre actuel
    try:
        index_actuel = chapitres_ordonnes.index(chapitre_nom)
    except ValueError:
        return False
    
    # Vérifier que le chapitre précédent est complété
    chapitre_precedent = chapitres_ordonnes[index_actuel - 1]
    progression_precedent = progression.get(chapitre_precedent, {})
    
    # Le chapitre précédent doit avoir au moins un niveau complété (ou être complètement terminé)
    niveaux_completes = progression_precedent.get("niveaux_completes", [])
    return len(niveaux_completes) > 0


def est_niveau_disponible(chapitre_nom, numero_niveau, structure_chapitre):
    """Vérifie si un niveau est disponible selon la progression."""
    data = charger()
    progression = data.get("campagne_progression", {}).get(chapitre_nom, {})
    niveaux_completes = progression.get("niveaux_completes", [])
    
    # Le niveau 1 est toujours disponible si le chapitre l'est
    if numero_niveau == 1:
        return True
    
    # Pour les autres niveaux, vérifier que le niveau précédent est complété
    return (numero_niveau - 1) in niveaux_completes


def est_niveau_complete(chapitre_nom, numero_niveau):
    """Vérifie si un niveau est complété."""
    data = charger()
    progression = data.get("campagne_progression", {}).get(chapitre_nom, {})
    return numero_niveau in progression.get("niveaux_completes", [])


def migrer_progression_chapitre():
    """Migre les données de progression pour utiliser des noms de chapitre cohérents."""
    data = charger()
    
    if "campagne_progression" not in data:
        return
    
    progression = data["campagne_progression"]
    cles_a_supprimer = []
    
    for cle in list(progression.keys()):
        # Si c'est un nom de dossier (contient un underscore), convertir
        if "_" in cle:
            nom_affiche = cle.split("_", 1)[1].replace("_", " ")
            
            # Si la version affichée existe déjà, fusionner
            if nom_affiche in progression:
                # Fusionner les niveaux complétés
                niveaux_existants = set(progression[nom_affiche].get("niveaux_completes", []))
                niveaux_dossier = set(progression[cle].get("niveaux_completes", []))
                niveaux_fusionnes = sorted(list(niveaux_existants | niveaux_dossier))
                
                progression[nom_affiche]["niveaux_completes"] = niveaux_fusionnes
                print(f"Fusion des progressions {cle} -> {nom_affiche}: niveaux {niveaux_fusionnes}")
            else:
                # Renommer la clé
                progression[nom_affiche] = progression[cle]
                print(f"Migration de {cle} -> {nom_affiche}")
            
            # Marquer l'ancienne clé pour suppression
            cles_a_supprimer.append(cle)
    
    # Supprimer les anciennes clés
    for cle in cles_a_supprimer:
        del progression[cle]
    
    if cles_a_supprimer:
        sauvegarder(data)
        print(f"Migration terminée: {len(cles_a_supprimer)} entrées migrées")
