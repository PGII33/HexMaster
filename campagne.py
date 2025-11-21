import pygame
import sys
import os
from niveau_structure import charger_niveau, TypeRestriction
from ui_commons import UIManager
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
        self.etat = "selection_chapitre"

        self.running = True
        self.cancelled = False

        # Charger la structure de campagne
        self.chapitres = self._load_campaign_structure()

        # Créer les boutons seulement si on a un écran
        if screen is not None:
            self.creer_boutons()

    def _load_campaign_structure(self):
        """Charge la structure de campagne depuis les dossiers."""
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
            chapter_name = chapter_folder.split("_", 1)[1].replace("_", " ") if "_" in chapter_folder else chapter_folder

            chapitres[chapter_name] = {"folder": chapter_folder, "niveaux": {}}

            # Parcourir les niveaux du chapitre
            for level_folder in sorted(os.listdir(chapter_path)):
                level_path = os.path.join(chapter_path, level_folder)
                if not os.path.isdir(level_path):
                    continue
                    
                niveau_file = os.path.join(level_path, "niveau.json")
                if not os.path.exists(niveau_file):
                    continue
                    
                config = charger_niveau(niveau_file)
                if not config:
                    continue
                    
                # Extraire le numéro de niveau
                level_num = int(level_folder.split("_")[0]) if "_" in level_folder and level_folder.split("_")[0].isdigit() else len(chapitres[chapter_name]["niveaux"]) + 1
                chapitres[chapter_name]["niveaux"][level_num] = config

        return chapitres

    def creer_boutons(self):
        """Crée les boutons selon l'état actuel."""
        if self.screen is None:
            return

        self.ui.clear_buttons()
        w, h = self.screen.get_size()

        if self.etat == "selection_chapitre":
            y = 150
            chapitres_ordonnes = list(self.chapitres.keys())

            for i, chapitre_nom in enumerate(chapitres_ordonnes):
                disponible = sauvegarde.est_chapitre_disponible(chapitre_nom, chapitres_ordonnes)
                progression = sauvegarde.obtenir_progression_chapitre(chapitre_nom)
                niveaux_completes = len(progression.get("niveaux_completes", []))
                total_niveaux = len(self.chapitres[chapitre_nom]["niveaux"])

                # Texte du bouton avec progression
                texte = f"{chapitre_nom} ({niveaux_completes}/{total_niveaux})" if niveaux_completes > 0 else chapitre_nom

                # Couleur selon la disponibilité
                if disponible:
                    couleur_base = (100, 150, 250)
                    couleur_hover = (140, 190, 250)
                    action = lambda nom=chapitre_nom: self.selectionner_chapitre(nom)
                else:
                    couleur_base = (150, 150, 150)
                    couleur_hover = (170, 170, 170)
                    action = None

                self.ui.add_button(
                    (w//2 - 250, y + i * 70, 500, 50),
                    texte, action,
                    color=couleur_base,
                    hover_color=couleur_hover
                )

            # Bouton retour
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour)

        elif self.etat == "selection_niveau":
            y = 150
            niveaux = self.chapitres[self.chapitre_actuel]["niveaux"]

            for niveau_num in sorted(niveaux.keys()):
                config = niveaux[niveau_num]
                disponible = sauvegarde.est_niveau_disponible(self.chapitre_actuel, niveau_num, niveaux)
                complete = sauvegarde.est_niveau_complete(self.chapitre_actuel, niveau_num)

                # Texte du bouton
                texte = f"Niveau {niveau_num}: {config.nom}"
                if complete:
                    texte += " [Complété]"

                # Couleur selon la disponibilité
                if disponible:
                    if complete:
                        couleur_base = (100, 200, 100)
                        couleur_hover = (140, 240, 140)
                    else:
                        couleur_base = (100, 150, 250)
                        couleur_hover = (140, 190, 250)
                    action = lambda num=niveau_num: self.selectionner_niveau(num)
                else:
                    couleur_base = (150, 150, 150)
                    couleur_hover = (170, 170, 170)
                    action = None

                self.ui.add_button(
                    (w//2 - 250, y + (niveau_num - 1) * 70, 500, 50),
                    texte, action,
                    color=couleur_base,
                    hover_color=couleur_hover
                )

            # Bouton retour
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour_chapitres)

    def selectionner_chapitre(self, nom):
        """Sélectionne un chapitre."""
        self.chapitre_actuel = nom
        self.etat = "selection_niveau"
        self.creer_boutons()

    def selectionner_niveau(self, numero):
        """Sélectionne un niveau."""
        self.niveau_actuel = numero
        self.running = False

    def retour(self):
        """Retour au menu principal."""
        self.cancelled = True
        self.running = False

    def retour_chapitres(self):
        """Retour à la sélection des chapitres."""
        self.chapitre_actuel = None
        self.etat = "selection_chapitre"
        self.creer_boutons()

    def run(self):
        """Lance l'interface de sélection de campagne."""
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
        """Affiche l'interface."""
        if self.screen is None:
            return

        self.screen.fill((255, 255, 255))

        if self.etat == "selection_chapitre":
            self.afficher_selection_chapitre()
        elif self.etat == "selection_niveau":
            self.afficher_selection_niveau()

        self.ui.draw_buttons()

    def afficher_selection_chapitre(self):
        """Affiche la sélection des chapitres."""
        self.ui.draw_title("Campagne - Sélection du Chapitre", 50)
        self.ui.draw_text("Choisissez un chapitre à jouer",
                          self.screen.get_width()//2 - 120, 100, color=(100, 100, 100))

    def afficher_selection_niveau(self):
        """Affiche la sélection des niveaux."""
        self.ui.draw_title(f"Chapitre: {self.chapitre_actuel}", 50)
        self.ui.draw_text("Choisissez un niveau à jouer",
                          self.screen.get_width()//2 - 120, 100, color=(100, 100, 100))


def get_niveau_data(chapitre: str, numero: int) -> dict:
    """Fonction utilitaire pour récupérer les données d'un niveau."""
    campaign_path = resource_path("Campagne")

    if not os.path.exists(campaign_path):
        return None

    # Trouver le dossier du chapitre
    for folder in os.listdir(campaign_path):
        folder_path = os.path.join(campaign_path, folder)
        if not os.path.isdir(folder_path):
            continue
            
        chapter_name = folder.split("_", 1)[1].replace("_", " ") if "_" in folder else folder
        if chapter_name != chapitre:
            continue

        # Trouver le niveau
        for level_folder in os.listdir(folder_path):
            level_path = os.path.join(folder_path, level_folder)
            if not os.path.isdir(level_path):
                continue
                
            # Extraire le numéro de niveau
            level_num = int(level_folder.split("_")[0]) if "_" in level_folder and level_folder.split("_")[0].isdigit() else None
            
            if level_num == numero:
                niveau_file = os.path.join(level_path, "niveau.json")
                if os.path.exists(niveau_file):
                    config = charger_niveau(niveau_file)
                    if config:
                        return {
                            "config": config,
                            "unites_joueur": config.unites_imposees if config.type_restriction == TypeRestriction.UNITES_IMPOSEES else [],
                            "unites_ennemis": config.unites_ennemis
                        }

    return None
