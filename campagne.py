import pygame
import sys
from utils import Button
import unites

# Configuration des chapitres et niveaux
CHAPITRES = {
    "La grande église": {
        "faction_requise": "Morts-Vivants",
        "description": "Les morts-vivants envahissent la grande église...",
        "niveaux": {
            1: {
                "nom": "Les cryptes",
                "description": "Explorez les cryptes abandonnées",
                "unites_joueur": [(unites.Squelette, (0,0)), (unites.Goule, (1,0))],
                "unites_ennemis": [(unites.Goule, (5,5)), (unites.Goule, (6,5))],
                "cp_gagne": 1
            },
            2: {
                "nom": "Le sanctuaire",
                "description": "Pénétrez dans le sanctuaire",
                "unites_joueur": [(unites.Squelette, (0,0)), (unites.Goule, (1,0)), (unites.Spectre, (0,1))],
                "unites_ennemis": [(unites.Vampire, (5,5)), (unites.Goule, (6,5)), (unites.Spectre, (5,6))],
                "cp_gagne": 1
            },
            3: {
                "nom": "L'autel maudit",
                "description": "Confrontez-vous au mal ancien",
                "unites_joueur": [(unites.Vampire, (0,0)), (unites.Zombie, (1,0)), (unites.Liche, (0,1))],
                "unites_ennemis": [(unites.Archliche, (5,5)), (unites.Vampire, (6,5)), (unites.Liche, (5,6))],
                "cp_gagne": 1
            }
        }
    }
}

class Campagne:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # État actuel
        self.chapitre_actuel = None
        self.niveau_actuel = None
        self.etat = "selection_chapitre"  # "selection_chapitre", "selection_niveau"
        
        self.running = True
        self.cancelled = False
        self.niveau_selectionne = None
        
        # Données de progression (à charger depuis sauvegarde plus tard)
        self.progression = {
            "La grande église": {"niveaux_completes": [], "disponible": True}
        }
        
        self.creer_boutons()
    
    def creer_boutons(self):
        screen_w, screen_h = self.screen.get_size()
        self.retour_btn = Button(
            (20, screen_h - 70, 160, 44),
            "Retour",
            self.retour,
            self.font
        )
    
    def retour(self):
        if self.etat == "selection_niveau":
            self.etat = "selection_chapitre"
            self.chapitre_actuel = None
        else:
            self.cancelled = True
            self.running = False
    
    def selectionner_chapitre(self, nom_chapitre):
        self.chapitre_actuel = nom_chapitre
        self.etat = "selection_niveau"
    
    def selectionner_niveau(self, numero_niveau):
        self.niveau_selectionne = (self.chapitre_actuel, numero_niveau)
        self.running = False
    
    def afficher_selection_chapitre(self):
        self.screen.fill((250, 240, 230))
        
        # Titre
        titre = self.title_font.render("Campagne - Sélection du chapitre", True, (30, 30, 60))
        self.screen.blit(titre, (40, 30))
        
        y = 120
        for nom_chapitre, info in CHAPITRES.items():
            disponible = self.progression[nom_chapitre]["disponible"]
            
            # Rectangle du chapitre
            rect = pygame.Rect(40, y, self.screen.get_width() - 80, 100)
            color = (220, 220, 220) if disponible else (180, 180, 180)
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=12)
            
            # Nom du chapitre
            nom_txt = self.font.render(nom_chapitre, True, (0, 0, 0))
            self.screen.blit(nom_txt, (rect.x + 20, rect.y + 10))
            
            # Description
            desc_txt = self.small_font.render(info["description"], True, (60, 60, 60))
            self.screen.blit(desc_txt, (rect.x + 20, rect.y + 40))
            
            # Faction requise
            faction_txt = self.small_font.render(f"Faction: {info['faction_requise']}", True, (100, 100, 100))
            self.screen.blit(faction_txt, (rect.x + 20, rect.y + 65))
            
            # Gestion du clic
            if disponible and rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (50, 150, 250), rect, width=3, border_radius=12)
            
            y += 120
    
    def afficher_selection_niveau(self):
        self.screen.fill((230, 250, 240))
        
        chapitre_info = CHAPITRES[self.chapitre_actuel]
        
        # Titre
        titre = self.title_font.render(f"Campagne - {self.chapitre_actuel}", True, (30, 30, 60))
        self.screen.blit(titre, (40, 30))
        
        # Description du chapitre
        desc_txt = self.font.render(chapitre_info["description"], True, (60, 60, 60))
        self.screen.blit(desc_txt, (40, 70))
        
        y = 120
        for numero, niveau_info in chapitre_info["niveaux"].items():
            # Vérifier si le niveau est disponible
            niveaux_completes = self.progression[self.chapitre_actuel]["niveaux_completes"]
            disponible = numero == 1 or (numero - 1) in niveaux_completes
            
            # Rectangle du niveau
            rect = pygame.Rect(40, y, self.screen.get_width() - 80, 80)
            color = (220, 240, 220) if disponible else (180, 180, 180)
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=12)
            
            # Nom du niveau
            nom_txt = self.font.render(f"Niveau {numero}: {niveau_info['nom']}", True, (0, 0, 0))
            self.screen.blit(nom_txt, (rect.x + 20, rect.y + 10))
            
            # Description
            desc_txt = self.small_font.render(niveau_info["description"], True, (60, 60, 60))
            self.screen.blit(desc_txt, (rect.x + 20, rect.y + 40))
            
            # Statut
            if numero in niveaux_completes:
                statut_txt = self.small_font.render("✓ Terminé", True, (0, 150, 0))
                self.screen.blit(statut_txt, (rect.right - 100, rect.y + 10))
            
            # Gestion du clic
            if disponible and rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(self.screen, (50, 150, 250), rect, width=3, border_radius=12)
            
            y += 100
    
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.creer_boutons()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.etat == "selection_chapitre":
                        y = 120
                        for nom_chapitre, info in CHAPITRES.items():
                            rect = pygame.Rect(40, y, self.screen.get_width() - 80, 100)
                            if rect.collidepoint(event.pos) and self.progression[nom_chapitre]["disponible"]:
                                self.selectionner_chapitre(nom_chapitre)
                                break
                            y += 120
                    
                    elif self.etat == "selection_niveau":
                        chapitre_info = CHAPITRES[self.chapitre_actuel]
                        y = 120
                        for numero, niveau_info in chapitre_info["niveaux"].items():
                            rect = pygame.Rect(40, y, self.screen.get_width() - 80, 80)
                            niveaux_completes = self.progression[self.chapitre_actuel]["niveaux_completes"]
                            disponible = numero == 1 or (numero - 1) in niveaux_completes
                            
                            if rect.collidepoint(event.pos) and disponible:
                                self.selectionner_niveau(numero)
                                break
                            y += 100
                    
                    self.retour_btn.handle_event(event)
            
            # Affichage
            if self.etat == "selection_chapitre":
                self.afficher_selection_chapitre()
            elif self.etat == "selection_niveau":
                self.afficher_selection_niveau()
            
            self.retour_btn.draw(self.screen)
            pygame.display.flip()
        
        if self.cancelled:
            return None
        else:
            return self.niveau_selectionne

def get_niveau_data(chapitre, numero):
    """Retourne les données d'un niveau spécifique"""
    return CHAPITRES[chapitre]["niveaux"][numero]