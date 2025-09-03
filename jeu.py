import pygame
import sys
import math
import ia
import unites
import animations
from layout import recalculer_layout, axial_to_pixel, hex_to_pixel
from affichage import dessiner
from input_mod import handle_click
from tour import reset_actions_tour

# Constantes (importées si besoin depuis menu)
BTN_H_RATIO = 0.06

class Jeu:
    def __init__(self, ia_strategy=ia.cible_faible, screen=None,
                 initial_player_units=None, initial_enemy_units=None, enable_placement=False):
        self.screen = screen if screen is not None else pygame.display.set_mode((1200, 900), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # État du jeu
        self.unites = []
        self.enable_placement = enable_placement
        
        # Traitement des unités selon le mode
        if enable_placement and initial_player_units:
            # Mode avec placement : initial_player_units contient des classes
            from placement import PlacementPhase
            placement = PlacementPhase(screen, initial_player_units)
            placed_units = placement.run()
            
            if placed_units:
                # placed_units contient [(classe, position), ...]
                for cls, pos in placed_units:
                    self.unites.append(cls("joueur", pos))
            else:
                # Placement annulé
                self.finished = True
                return
            
            # Placement automatique des ennemis en zone rouge
            if initial_enemy_units:
                enemy_positions = []
                for r in [4, 5, 6]:  # Zone ennemie
                    for q in range(-1, 7):
                        enemy_positions.append((q, r))
                
                for i, cls in enumerate(initial_enemy_units):
                    if i < len(enemy_positions):
                        self.unites.append(cls("ennemi", enemy_positions[i]))
        
        else:
            # Mode sans placement : initial_player_units contient [(classe, position), ...]
            if initial_player_units:
                for cls, pos in initial_player_units:
                    self.unites.append(cls("joueur", pos))

            if initial_enemy_units:
                for cls, pos in initial_enemy_units:
                    self.unites.append(cls("ennemi", pos))

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

        # Mettre à jour les animations
        for u in self.unites:
            if u.anim:
                if u.anim.update(dt_ms):
                    u.anim = None


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
                self.changer_tour()
                self.ia_busy = False
                self.ia_queue = []
                self.ia_index = 0
                self.ia_timer_ms = 0

    def est_case_vide(self, pos, toutes_unites=None):
        """Renvoie True si aucune unité vivante n'occupe la case pos."""
        if toutes_unites is None:
            toutes_unites = self.unites
        return all(u.pos != pos or not u.vivant for u in toutes_unites)

    def changer_tour(self):
        """Passe au tour suivant et réinitialise les actions/compétences passives."""
        self.tour = "ennemi" if self.tour == "joueur" else "joueur"
        reset_actions_tour(self)
        self.selection = None
        self.deplacement_possibles = {}
