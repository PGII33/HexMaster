import pygame
import sys
from jeu import Jeu
from utils import Button

BLANC = (255,255,255)
BLEU = (50,150,250)

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
            Button((center_x-140, h//2-130, 280, 60), "Jouer", lambda: self.set_etat("playmenu"), self.font_med),
            Button((center_x-140, h//2-50, 280, 60), "Inventaire", lambda: self.set_etat("inventaire"), self.font_med),
            Button((center_x-140, h//2+30, 280, 60), "Boutique", lambda: self.set_etat("boutique"), self.font_med),
            Button((center_x-140, h//2+110, 280, 60), "Missions", lambda: self.set_etat("missions"), self.font_med),
            Button((center_x-140, h//2+190, 280, 60), "Quitter", lambda: sys.exit(), self.font_med),
        ]

        self.boutons_playmenu = [
            Button((center_x-140, h//2-90, 280, 60), "1 personnage", lambda: self.start_play_mode(1), self.font_med),
            Button((center_x-140, h//2-10, 280, 60), "2 personnages", lambda: self.start_play_mode(2), self.font_med),
            Button((center_x-140, h//2+70, 280, 60), "3 personnages", lambda: self.start_play_mode(3), self.font_med),
            Button((20, h-70, 150, 50), "Retour", lambda: self.set_etat("menu"), self.font_med),
        ]

        self.boutons_retour = [
            Button((20, h-70, 150, 50), "Retour", lambda: self.set_etat("menu"), self.font_med)
        ]

    def set_etat(self, e):
        if self.etat == "jeu" and e != "jeu":
            self.jeu = None
        self.etat = e

    def start_play_mode(self, n_players):
        # Pour l'instant: lancer la démo pour 2 (ou autres), tu peux adapter plus tard
        if n_players >= 1:
            self.jeu = Jeu(ia_strategy=None, screen=self.screen)  # ia_strategy None ou défaut
            self.etat = "jeu"

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
                elif self.etat in ["inventaire", "boutique", "missions"]:
                    for b in self.boutons_retour: b.handle_event(event)
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

            elif self.etat in ["inventaire", "boutique", "missions"]:
                self.screen.fill(BLANC)
                titre = self.font_big.render(self.etat.capitalize(), True, BLEU)
                self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 80))
                for b in self.boutons_retour: b.draw(self.screen)
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