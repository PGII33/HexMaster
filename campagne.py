import pygame
import sys
import os
import json
from utils import Button
import unites

class Campagne:
    def __init__(self, screen):
        self.screen = screen
        if screen is not None:
            self.font = pygame.font.SysFont(None, 28)
            self.title_font = pygame.font.SysFont(None, 36)
            self.small_font = pygame.font.SysFont(None, 20)
        
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
        campaign_path = "Campagne"
        chapitres = {}
        
        if not os.path.exists(campaign_path):
            print("Dossier Campagne non trouvé!")
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
                    try:
                        with open(niveau_file, 'r', encoding='utf-8') as f:
                            niveau_data = json.load(f)
                        
                        # Convertir les noms d'unités en classes
                        niveau_data["unites_ennemis"] = self._convert_unit_names_to_classes(niveau_data["unites_ennemis"])
                        if "unites_predefinies" in niveau_data:
                            niveau_data["unites_predefinies"] = self._convert_unit_names_to_classes(niveau_data["unites_predefinies"])
                        
                        # Extraire le numéro de niveau
                        if "_" in level_folder:
                            level_num = int(level_folder.split("_")[0])
                        else:
                            level_num = len(chapitres[chapter_name]["niveaux"]) + 1
                        
                        chapitres[chapter_name]["niveaux"][level_num] = niveau_data
                        
                    except Exception as e:
                        print(f"Erreur lors du chargement de {niveau_file}: {e}")
        
        return chapitres
    
    def _convert_unit_names_to_classes(self, unit_list):
        """Convertit les noms d'unités en classes d'unités"""
        converted = []
        for unit_name, pos in unit_list:
            # Trouver la classe correspondante
            for cls in unites.CLASSES_UNITES:
                if cls.__name__ == unit_name:
                    converted.append((cls, pos))
                    break
            else:
                print(f"Unité inconnue: {unit_name}")
        return converted
    
    def creer_boutons(self):
        """Crée les boutons selon l'état actuel"""
        if self.screen is None:
            return
            
        w, h = self.screen.get_size()
        
        if self.etat == "selection_chapitre":
            self.boutons = []
            y = 150
            for i, chapitre_nom in enumerate(self.chapitres.keys()):
                btn = Button(
                    (w//2 - 200, y + i * 70, 400, 50),
                    chapitre_nom,
                    lambda nom=chapitre_nom: self.selectionner_chapitre(nom),
                    self.font
                )
                self.boutons.append(btn)
            
            # Bouton retour
            self.boutons.append(Button((20, h-70, 150, 50), "Retour", self.retour, self.font))
        
        elif self.etat == "selection_niveau":
            self.boutons = []
            y = 150
            niveaux = self.chapitres[self.chapitre_actuel]["niveaux"]
            
            for niveau_num in sorted(niveaux.keys()):
                niveau = niveaux[niveau_num]
                btn = Button(
                    (w//2 - 200, y + (niveau_num - 1) * 70, 400, 50),
                    f"Niveau {niveau_num}: {niveau['nom']}",
                    lambda num=niveau_num: self.selectionner_niveau(num),
                    self.font
                )
                self.boutons.append(btn)
            
            # Boutons navigation
            self.boutons.append(Button((20, h-70, 150, 50), "Retour", self.retour_chapitres, self.font))
    
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
                    self.creer_boutons()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in self.boutons:
                        btn.handle_event(event)
            
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
        
        for btn in self.boutons:
            btn.draw(self.screen)
    
    def afficher_selection_chapitre(self):
        """Affiche la sélection des chapitres"""
        title = self.title_font.render("Campagne - Sélection du Chapitre", True, (50, 50, 150))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
        
        info = self.font.render("Choisissez un chapitre à jouer", True, (100, 100, 100))
        self.screen.blit(info, (self.screen.get_width()//2 - info.get_width()//2, 100))
    
    def afficher_selection_niveau(self):
        """Affiche la sélection des niveaux"""
        title = self.title_font.render(f"Chapitre: {self.chapitre_actuel}", True, (50, 50, 150))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
        
        info = self.font.render("Choisissez un niveau à jouer", True, (100, 100, 100))
        self.screen.blit(info, (self.screen.get_width()//2 - info.get_width()//2, 100))

def get_niveau_data(chapitre, numero):
    """Fonction utilitaire pour récupérer les données d'un niveau"""
    # Charger directement depuis les fichiers sans créer d'interface
    campaign_path = "Campagne"
    
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
            if "_" in level_folder:
                level_num = int(level_folder.split("_")[0])
            else:
                continue
            
            if level_num == numero:
                niveau_file = os.path.join(level_path, "niveau.json")
                if os.path.exists(niveau_file):
                    try:
                        with open(niveau_file, 'r', encoding='utf-8') as f:
                            niveau_data = json.load(f)
                        
                        # Convertir les noms d'unités en classes
                        def convert_units(unit_list):
                            converted = []
                            for unit_name, pos in unit_list:
                                for cls in unites.CLASSES_UNITES:
                                    if cls.__name__ == unit_name:
                                        converted.append((cls, pos))
                                        break
                            return converted
                        
                        unites_ennemis = convert_units(niveau_data["unites_ennemis"])
                        unites_joueur = []
                        if "unites_predefinies" in niveau_data:
                            unites_joueur = convert_units(niveau_data["unites_predefinies"])
                        
                        # Format attendu par le jeu
                        return {
                            "unites_joueur": unites_joueur,
                            "unites_ennemis": unites_ennemis
                        }
                        
                    except Exception as e:
                        print(f"Erreur lors du chargement du niveau: {e}")
                        return None
    
    return None