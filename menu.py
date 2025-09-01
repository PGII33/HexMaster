import pygame
import sys
import ia
from jeu import Jeu
from utils import Button
from boutique import Boutique
from inventaire import Inventaire
from tuto import Tuto
from hexarene import HexArène  # nouveau

BLANC = (255, 255, 255)
BLEU = (50, 150, 250)

class HexaMaster:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 900), pygame.RESIZABLE)
        pygame.display.set_caption("HexaMaster")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont(None, 80)
        self.font_med = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 20)

        self.etat = "menu"
        self.jeu = None

        self.creer_boutons()

    def creer_boutons(self):
        w, h = self.screen.get_size()
        center_x = w // 2
        self.boutons_menu = [
            Button((center_x-140, h//2-130, 280, 60), "Jouer", self.open_playmenu, self.font_med),
            Button((center_x-140, h//2-50, 280, 60), "Inventaire", self.open_inventaire, self.font_med),
            Button((center_x-140, h//2+30, 280, 60), "Boutique", self.open_boutique, self.font_med),
            Button((center_x-140, h//2+110, 280, 60), "Missions", self.open_missions_placeholder, self.font_med),
            Button((center_x-140, h//2+190, 280, 60), "Quitter", lambda: sys.exit(), self.font_med),
        ]

        # Play menu : Demo et HexArène
        self.boutons_playmenu = [
            Button((center_x-140, h//2-50, 280, 60), "Tutoriel", self.start_tuto, self.font_med),
            Button((center_x-140, h//2+50, 280, 60), "HexArène", self.start_hexarene_mode, self.font_med),
            Button((20, h-70, 150, 50), "Retour", self.back_to_menu, self.font_med),
        ]

        self.boutons_retour_placeholder = [
            Button((20, h-70, 150, 50), "Retour", self.back_to_menu, self.font_med)
        ]

    # ------ actions boutons ------
    def back_to_menu(self):
        if self.etat == "jeu":
            self.jeu = None
        self.etat = "menu"

    def open_playmenu(self):
        self.etat = "playmenu"

    def open_inventaire(self):
        inv = Inventaire(self.screen)
        inv.afficher()
        self.creer_boutons()

    def open_boutique(self):
        shop = Boutique(self.screen)
        shop.afficher()
        self.creer_boutons()

    def open_missions_placeholder(self):
        self.etat = "missions"

    def start_tuto(self):
        tuto = Tuto(self.screen)
        self.jeu = tuto.run_flow()
        self.etat = "jeu"


    def start_hexarene_mode(self):
        # Charger inventaire du joueur
        inv_data = Inventaire(self.screen).data
        player_units_names = inv_data.get("unites", [])

        if not player_units_names:
            print("Aucune unité disponible dans l'inventaire !")
            return

        # Lancer HexArène
        hex_arene = HexArène(self.screen)
        # remplacer la sélection automatique par inventaire
        hex_arene.selected_units = player_units_names[:hex_arene.max_units]
        hex_arene._placement_phase()  # placement automatique
        player_units_specs = [(nom, pos) for nom, pos in hex_arene.unit_positions]
        enemy_units_specs = hex_arene._generate_enemies()

        # Lancer le jeu
        self.jeu = Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=player_units_specs,
            initial_enemy_units=enemy_units_specs
        )
        self.etat = "jeu"

    # ------ boucle principale ------
    def run(self):
        while True:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.creer_boutons()
                    if self.jeu:
                        self.jeu.screen = self.screen
                        self.jeu.recalculer_layout()

                if self.etat == "menu":
                    for b in self.boutons_menu: b.handle_event(event)
                elif self.etat == "playmenu":
                    for b in self.boutons_playmenu: b.handle_event(event)
                elif self.etat in ["missions"]:
                    for b in self.boutons_retour_placeholder: b.handle_event(event)
                elif self.etat == "jeu":
                    if self.jeu:
                        self.jeu.handle_event(event)

            # Draw/update
            if self.etat == "menu":
                self.screen.fill(BLANC)
                titre = self.font_big.render("HexaMaster", True, BLEU)
                self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 80))
                for b in self.boutons_menu: b.draw(self.screen)

            elif self.etat == "playmenu":
                self.screen.fill(BLANC)
                titre = self.font_big.render("Mode de jeu", True, BLEU)
                self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 80))
                for b in self.boutons_playmenu: b.draw(self.screen)

            elif self.etat in ["missions"]:
                self.screen.fill(BLANC)
                titre = self.font_big.render("Missions", True, BLEU)
                self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 80))
                for b in self.boutons_retour_placeholder: b.draw(self.screen)
                info = self.font_small.render("Écran en construction — contenu placeholder", True, (0,0,0))
                self.screen.blit(info, (50, 200))

            elif self.etat == "jeu":
                if self.jeu:
                    self.jeu.update(dt)
                    if self.jeu.finished:
                        self.jeu = None
                        self.etat = "menu"
                    else:
                        self.jeu.dessiner()

            pygame.display.flip()
