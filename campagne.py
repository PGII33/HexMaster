import pygame
import sys
import os
from niveau_structure import charger_niveau, NiveauConfig, TypeRestriction
from ui_commons import UIManager, ProgressionManager
import sauvegarde
from utils import resource_path

class Campagne:
    def __init__(self, screen):
        self.screen = screen
        if screen is not None:
            self.ui = UIManager(screen)
        
        # État actuel
        self.chapitre_actuel = None
        self.niveau_actuel = None
        self.etat = "selection_chapitre"  # "selection_chapitre", "selection_niveau"
        
        self.running = True
        self.cancelled = False
        
        # Charger la structure de campagne
        self.chapitres = self._load_campaign_structure()
        
        # Créer les boutons seulement si on a un écran
        if screen is not None:
            self.creer_boutons()
    
    def _load_campaign_structure(self):
        """Charge la structure de campagne depuis les dossiers"""
        campaign_path = resource_path("Campagne")
        chapitres = {}
        
        if not os.path.exists(campaign_path):
            print(f"Dossier Campagne non trouvé à {campaign_path}!")
            return {}
        
        # Parcourir les dossiers de chapitres
        for chapter_folder in sorted(os.listdir(campaign_path)):
            chapter_path = os.path.join(campaign_path, chapter_folder)
            if not os.path.isdir(chapter_path):
                continue
            
            # Extraire le nom du chapitre (après le préfixe numérique)
            if "_" in chapter_folder:
                chapter_name = chapter_folder.split("_", 1)[1].replace("_", " ")
            else:
                chapter_name = chapter_folder
            
            chapitres[chapter_name] = {
                "folder": chapter_folder,
                "niveaux": {}
            }
            
            # Parcourir les niveaux du chapitre
            for level_folder in sorted(os.listdir(chapter_path)):
                level_path = os.path.join(chapter_path, level_folder)
                if not os.path.isdir(level_path):
                    continue
                
                niveau_file = os.path.join(level_path, "niveau.json")
                if os.path.exists(niveau_file):
                    config = charger_niveau(niveau_file)
                    if config:
                        # Extraire le numéro de niveau - format plus flexible
                        level_num = None
                        if "_" in level_folder and level_folder.split("_")[0].isdigit():
                            # Format: "01_NomNiveau"
                            level_num = int(level_folder.split("_")[0])
                        elif "niveau" in level_folder.lower():
                            # Format: "Niveau 1" ou "Niveau_1"
                            import re
                            match = re.search(r'niveau[_\s]*(\d+)', level_folder.lower())
                            if match:
                                level_num = int(match.group(1))
                        
                        if level_num is None:
                            # Attribuer un numéro séquentiel
                            level_num = len(chapitres[chapter_name]["niveaux"]) + 1
                        
                        chapitres[chapter_name]["niveaux"][level_num] = config
        
        return chapitres
    
    def creer_boutons(self):
        """Crée les boutons selon l'état actuel"""
        if self.screen is None:
            return
        
        self.ui.clear_buttons()
        w, h = self.screen.get_size()
        
        if self.etat == "selection_chapitre":
            y = 150
            for i, chapitre_nom in enumerate(self.chapitres.keys()):
                self.ui.add_button(
                    (w//2 - 200, y + i * 70, 400, 50),
                    chapitre_nom,
                    lambda nom=chapitre_nom: self.selectionner_chapitre(nom)
                )
            
            # Bouton retour
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour)
        
        elif self.etat == "selection_niveau":
            y = 150
            niveaux = self.chapitres[self.chapitre_actuel]["niveaux"]
            
            for niveau_num in sorted(niveaux.keys()):
                config = niveaux[niveau_num]
                self.ui.add_button(
                    (w//2 - 200, y + (niveau_num - 1) * 70, 400, 50),
                    f"Niveau {niveau_num}: {config.nom}",
                    lambda num=niveau_num: self.selectionner_niveau(num)
                )
            
            # Boutons navigation
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour_chapitres)
    
    def selectionner_chapitre(self, nom):
        """Sélectionne un chapitre"""
        self.chapitre_actuel = nom
        self.etat = "selection_niveau"
        self.creer_boutons()
    
    def selectionner_niveau(self, numero):
        """Sélectionne un niveau"""
        self.niveau_actuel = numero
        self.running = False
    
    def retour(self):
        """Retour au menu principal"""
        self.cancelled = True
        self.running = False
    
    def retour_chapitres(self):
        """Retour à la sélection des chapitres"""
        self.chapitre_actuel = None
        self.etat = "selection_chapitre"
        self.creer_boutons()
    
    def run(self):
        """Lance l'interface de sélection de campagne"""
        if self.screen is None:
            return None
            
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.ui.screen = self.screen
                    self.creer_boutons()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.ui.handle_button_events(event)
            
            self.afficher()
            pygame.display.flip()
        
        if self.cancelled:
            return None
        else:
            return (self.chapitre_actuel, self.niveau_actuel)
    
    def afficher(self):
        """Affiche l'interface"""
        if self.screen is None:
            return
            
        self.screen.fill((255, 255, 255))
        
        if self.etat == "selection_chapitre":
            self.afficher_selection_chapitre()
        elif self.etat == "selection_niveau":
            self.afficher_selection_niveau()
        
        self.ui.draw_buttons()
    
    def afficher_selection_chapitre(self):
        """Affiche la sélection des chapitres"""
        self.ui.draw_title("Campagne - Sélection du Chapitre", 50)
        self.ui.draw_text("Choisissez un chapitre à jouer", 
                         self.screen.get_width()//2 - 120, 100, color=(100, 100, 100))
    
    def afficher_selection_niveau(self):
        """Affiche la sélection des niveaux"""
        self.ui.draw_title(f"Chapitre: {self.chapitre_actuel}", 50)
        self.ui.draw_text("Choisissez un niveau à jouer", 
                         self.screen.get_width()//2 - 120, 100, color=(100, 100, 100))

def get_niveau_data(chapitre: str, numero: int) -> dict:
    """Fonction utilitaire pour récupérer les données d'un niveau au format attendu par le jeu"""
    campaign_path = resource_path("Campagne")
    
    if not os.path.exists(campaign_path):
        return None
    
    # Trouver le dossier du chapitre
    chapter_folder = None
    for folder in os.listdir(campaign_path):
        folder_path = os.path.join(campaign_path, folder)
        if os.path.isdir(folder_path):
            if "_" in folder:
                chapter_name = folder.split("_", 1)[1].replace("_", " ")
            else:
                chapter_name = folder
            
            if chapter_name == chapitre:
                chapter_folder = folder
                break
    
    if not chapter_folder:
        return None
    
    # Trouver le niveau
    chapter_path = os.path.join(campaign_path, chapter_folder)
    for level_folder in os.listdir(chapter_path):
        level_path = os.path.join(chapter_path, level_folder)
        if os.path.isdir(level_path):
            # Extraire le numéro de niveau - format plus flexible
            level_num = None
            if "_" in level_folder and level_folder.split("_")[0].isdigit():
                # Format: "01_NomNiveau"
                level_num = int(level_folder.split("_")[0])
            elif "niveau" in level_folder.lower():
                # Format: "Niveau 1" ou "Niveau_1"
                import re
                match = re.search(r'niveau[_\s]*(\d+)', level_folder.lower())
                if match:
                    level_num = int(match.group(1))
            
            if level_num == numero:
                niveau_file = os.path.join(level_path, "niveau.json")
                if os.path.exists(niveau_file):
                    config = charger_niveau(niveau_file)
                    if config:
                        # Format attendu par le jeu
                        return {
                            "config": config,
                            "unites_joueur": config.unites_imposees if config.type_restriction == TypeRestriction.UNITES_IMPOSEES else [],
                            "unites_ennemis": config.unites_ennemis
                        }
    
    return None


def appliquer_recompenses_niveau(chapitre: str, numero: int):
    """Applique les récompenses d'un niveau complété"""
    # Charger la configuration du niveau
    config = None
    campaign_path = resource_path("Campagne")
    
    if os.path.exists(campaign_path):
        # Trouver le niveau comme dans get_niveau_data
        for folder in os.listdir(campaign_path):
            folder_path = os.path.join(campaign_path, folder)
            if os.path.isdir(folder_path):
                if "_" in folder:
                    chapter_name = folder.split("_", 1)[1].replace("_", " ")
                else:
                    chapter_name = folder
                
                if chapter_name == chapitre:
                    chapter_path = folder_path
                    for level_folder in os.listdir(chapter_path):
                        level_path = os.path.join(chapter_path, level_folder)
                        if os.path.isdir(level_path):
                            # Extraire le numéro de niveau - format plus flexible
                            level_num = None
                            if "_" in level_folder and level_folder.split("_")[0].isdigit():
                                # Format: "01_NomNiveau"
                                level_num = int(level_folder.split("_")[0])
                            elif "niveau" in level_folder.lower():
                                # Format: "Niveau 1" ou "Niveau_1"
                                import re
                                match = re.search(r'niveau[_\s]*(\d+)', level_folder.lower())
                                if match:
                                    level_num = int(match.group(1))
                            
                            if level_num == numero:
                                niveau_file = os.path.join(level_path, "niveau.json")
                                if os.path.exists(niveau_file):
                                    config = charger_niveau(niveau_file)
                                break
                    break
    
    if not config:
        return
    
    # Charger la sauvegarde et appliquer les récompenses
    sauvegarde_data = sauvegarde.charger()
    
    # Vérifier si le niveau n'a pas déjà été complété (pour éviter les récompenses multiples)
    if not config.completable_plusieurs_fois:
        if ProgressionManager.est_niveau_complete(sauvegarde_data, chapitre, numero):
            return  # Niveau déjà complété, pas de récompense
    
    # Marquer comme complété
    ProgressionManager.marquer_niveau_complete(sauvegarde_data, chapitre, numero)
    
    # Appliquer les récompenses
    ProgressionManager.appliquer_recompenses(sauvegarde_data, config)
    
    # Sauvegarder
    sauvegarde.sauvegarder(sauvegarde_data)
    
    print(f"Récompenses appliquées pour {chapitre} niveau {numero}:")
    print(f"- +{config.recompense_cp} CP")
    if config.unites_debloquees:
        print(f"- Unités débloquées: {', '.join(config.unites_debloquees)}")