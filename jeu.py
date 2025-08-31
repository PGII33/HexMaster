import pygame
import sys
import math
import ia
import unites
from layout import recalculer_layout, axial_to_pixel, hex_to_pixel
from affichage import dessiner
from input_mod import handle_click
from tour import reset_actions_tour

# Constantes (importées si besoin depuis menu)
BTN_H_RATIO = 0.06

class Jeu:
    def __init__(self, ia_strategy=ia.cible_faible, screen=None,
                 initial_player_units=None, initial_enemy_units=None):
        self.screen = screen if screen is not None else pygame.display.set_mode((1200, 900), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # État du jeu
        self.unites = []

        # si pas d'unités passées, unités par défaut (démo)
        if initial_player_units is None:
            self.unites.extend([
                unites.Squelette("joueur", (0, 0)),
                unites.Vampire("joueur", (1, 0)),
            ])
        else:
            for nom, pos in initial_player_units:
                if nom == "Squelette":
                    self.unites.append(unites.Squelette("joueur", pos))
                elif nom == "Goule":
                    self.unites.append(unites.Goule("joueur", pos))
                elif nom == "Vampire":
                    self.unites.append(unites.Vampire("joueur", pos))

        if initial_enemy_units is None:
            self.unites.extend([
                unites.Squelette("ennemi", (0, 2)),
                unites.Goule("ennemi", (1, 2)),
            ])
        else:
            for nom, pos in initial_enemy_units:
                if nom == "Squelette":
                    self.unites.append(unites.Squelette("ennemi", pos))
                elif nom == "Goule":
                    self.unites.append(unites.Goule("ennemi", pos))
                elif nom == "Vampire":
                    self.unites.append(unites.Vampire("ennemi", pos))

        self.tour = "joueur"
        self.selection = None
        self.deplacement_possibles = {}
        self.ia_strategy = ia_strategy

        self.q_range = range(-1, 7)
        self.r_range = range(-1, 7)

        self.ia_busy = False
        self.ia_queue = []
        self.ia_index = 0
        self.ia_timer_ms = 0
        self.ia_delay_between_actions = 250

        self.finished = False

        recalculer_layout(self)

    def recalculer_layout(self):
        recalculer_layout(self)

    def dessiner(self):
        dessiner(self)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            self.recalculer_layout()
        elif event.type == pygame.MOUSEBUTTONDOWN and self.tour == "joueur":
            mx, my = event.pos
            handle_click(self, mx, my)

    def update(self, dt_ms):
        # Vérifier fin
        joueurs = [u for u in self.unites if u.equipe == "joueur" and u.vivant]
        ennemis = [u for u in self.unites if u.equipe == "ennemi" and u.vivant]
        if not joueurs or not ennemis:
            self.finished = True
            return

        # Tour IA
        if self.tour == "ennemi":
            if not self.ia_busy:
                self.ia_queue = ennemis[:]
                self.ia_index = 0
                self.ia_busy = True
                self.ia_timer_ms = 0

            if self.ia_busy and self.ia_index < len(self.ia_queue):
                self.ia_timer_ms -= dt_ms
                if self.ia_timer_ms <= 0:
                    e = self.ia_queue[self.ia_index]
                    joueurs_courants = [u for u in self.unites if u.equipe == "joueur" and u.vivant]
                    if self.ia_strategy:
                        self.ia_strategy(e, joueurs_courants, self.unites)
                    self.ia_timer_ms = self.ia_delay_between_actions
                    self.ia_index += 1
            else:
                self.tour = "joueur"
                reset_actions_tour(self)
                self.ia_busy = False
                self.ia_queue = []
                self.ia_index = 0
                self.ia_timer_ms = 0