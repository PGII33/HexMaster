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
                 initial_player_units=None, initial_enemy_units=None, 
                 enable_placement=False, versus_mode=False):
        self.screen = screen if screen is not None else pygame.display.set_mode((1200, 900), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # État du jeu
        self.unites = []
        self.enable_placement = enable_placement
        self.versus_mode = versus_mode  # Nouveau : mode joueur vs joueur
        
        # Variables pour le système de compétences actives
        self.mode_selection_competence = False
        self.competence_en_cours = None
        self.cibles_possibles = []
        self.competence_btn_rect = None
        
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
                    # En mode versus, les "ennemis" sont le joueur 2
                    equipe = "joueur2" if versus_mode else "ennemi"
                    self.unites.append(cls(equipe, pos))

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Permettre les clics pour TOUS les tours (joueur ET joueur2)
            if self.versus_mode or self.tour == "joueur":
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
        
        if self.versus_mode:
            # En mode versus, vérifier joueur2 au lieu d'ennemi
            adversaires = [u for u in self.unites if u.equipe == "joueur2" and u.vivant]
        else:
            adversaires = [u for u in self.unites if u.equipe == "ennemi" and u.vivant]
        
        if not joueurs or not adversaires:
            self.finished = True
            return

        # Tour IA (seulement si pas en mode versus)
        if not self.versus_mode and self.tour == "ennemi":
            if not self.ia_busy:
                adversaires_courants = [u for u in self.unites if u.equipe == "ennemi" and u.vivant]
                self.ia_queue = adversaires_courants[:]
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
        if getattr(self, 'versus_mode', False):
            # En mode versus, alterner entre "joueur" et "joueur2"
            self.tour = "joueur2" if self.tour == "joueur" else "joueur"
        else:
            # Mode normal : alterner entre "joueur" et "ennemi"
            self.tour = "ennemi" if self.tour == "joueur" else "joueur"
        
        reset_actions_tour(self)
        self.selection = None
        self.deplacement_possibles = {}

    # ...reste du code inchangé...
