import pygame
import sys
import ia
import unites
from jeu import Jeu
from utils import Button
from boutique import Boutique
from inventaire import Inventaire
from tuto import Tuto
from hexarene import HexArène
from campagne import Campagne, get_niveau_data
from unit_selector import UnitSelector
from ia_selector import IASelector

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
        
        # Menu principal
        self.boutons_menu = [
            Button((center_x-140, h//2-130, 280, 60), "Jouer", self.open_playmenu, self.font_med),
            Button((center_x-140, h//2-50, 280, 60), "Inventaire", self.open_inventaire, self.font_med),
            Button((center_x-140, h//2+30, 280, 60), "Boutique", self.open_boutique, self.font_med),
            Button((center_x-140, h//2+110, 280, 60), "Missions", self.open_missions_placeholder, self.font_med),
            Button((center_x-140, h//2+190, 280, 60), "Quitter", lambda: sys.exit(), self.font_med),
        ]

        # Menu Jouer principal
        self.boutons_playmenu = [
            Button((center_x-140, h//2-100, 280, 50), "Campagne", self.open_campagne_menu, self.font_med),
            Button((center_x-140, h//2-40, 280, 50), "HexArène", self.open_hexarene_menu, self.font_med),
            Button((center_x-140, h//2+20, 280, 50), "JcJ", self.open_jcj_menu, self.font_med),
            Button((20, h-70, 150, 50), "Retour", self.back_to_menu, self.font_med),
        ]

        # Sous-menu Campagne
        self.boutons_campagne_menu = [
            Button((center_x-140, h//2-100, 280, 50), "Tutoriel", self.start_tuto, self.font_med),
            Button((center_x-140, h//2-40, 280, 50), "La grande église", self.start_campagne, self.font_med),
            Button((center_x-140, h//2+20, 280, 50), "Chapitre x", self.start_chapitre_placeholder, self.font_med),
            Button((20, h-70, 150, 50), "Retour", self.back_to_playmenu, self.font_med),
        ]

        # Sous-menu HexArène
        self.boutons_hexarene_menu = [
            Button((center_x-140, h//2-60, 280, 50), "Mode Faction", self.start_hexarene_faction, self.font_med),
            Button((center_x-140, h//2, 280, 50), "Mode Libre", self.start_hexarene_libre, self.font_med),
            Button((20, h-70, 150, 50), "Retour", self.back_to_playmenu, self.font_med),
        ]

        # Sous-menu JcJ
        self.boutons_jcj_menu = [
            Button((center_x-140, h//2-60, 280, 50), "Local", self.start_versus, self.font_med),
            Button((center_x-140, h//2, 280, 50), "En ligne", self.start_en_ligne_placeholder, self.font_med),
            Button((20, h-70, 150, 50), "Retour", self.back_to_playmenu, self.font_med),
        ]

        self.boutons_retour_placeholder = [
            Button((20, h-70, 150, 50), "Retour", self.back_to_menu, self.font_med)
        ]

    # ------ Navigation entre menus ------
    def back_to_menu(self):
        if self.etat == "jeu":
            self.jeu = None
        self.etat = "menu"

    def back_to_playmenu(self):
        self.etat = "playmenu"

    def open_playmenu(self):
        self.etat = "playmenu"

    def open_campagne_menu(self):
        self.etat = "campagne_menu"

    def open_hexarene_menu(self):
        self.etat = "hexarene_menu"

    def open_jcj_menu(self):
        self.etat = "jcj_menu"

    # ------ Actions des boutons ------
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

    def start_chapitre_placeholder(self):
        # Placeholder pour les futurs chapitres
        print("Chapitre x - À implémenter")

    def start_en_ligne_placeholder(self):
        # Placeholder pour le mode en ligne
        print("Mode en ligne - À implémenter")

    def start_tuto(self):
        tuto = Tuto(self.screen)
        self.jeu = tuto.run_flow()
        self.etat = "jeu"

    def start_campagne(self):
        """Lance le mode campagne"""
        campagne = Campagne(self.screen)
        niveau_info = campagne.run()
        
        if niveau_info is None:  # Annulé
            return
        
        chapitre, numero = niveau_info
        niveau_data = get_niveau_data(chapitre, numero)
        
        # Sélection des unités (prédéfinies en campagne)
        selector = UnitSelector(self.screen, "campagne", 
                              unites_predefinies=niveau_data["unites_joueur"])
        player_units = selector.run()
        
        if player_units is None:  # Annulé
            return
        
        self.jeu = Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=player_units,
            initial_enemy_units=niveau_data["unites_ennemis"]
        )
        self.etat = "jeu"

    def start_hexarene_faction(self):
        """Lance le mode HexArène avec contrainte de faction"""
        # Utiliser le mode hexarene existant (qui a déjà la contrainte de faction)
        selector = UnitSelector(self.screen, "hexarene")
        player_units = selector.run()
        
        if player_units is None:  # Annulé
            return
        
        # Calculer le tier max du joueur pour l'IA
        player_max_tier = max([cls("joueur", (0,0)).tier for cls in player_units]) if player_units else 1
        
        # Sélection de l'IA
        import sauvegarde
        data = sauvegarde.charger()
        ia_selector = IASelector("hexarene", 
                                player_cp=data.get("cp", 5),
                                player_max_tier=player_max_tier)
        ia_units = ia_selector.select_units()
        
        self.jeu = Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=player_units,
            initial_enemy_units=ia_units,
            enable_placement=True
        )
        self.etat = "jeu"

    def start_hexarene_libre(self):
        """Lance le mode HexArène sans contrainte de faction (mode mixte)"""
        # Utiliser le mode mixte existant
        selector = UnitSelector(self.screen, "mixte")
        player_units = selector.run()
        
        if player_units is None:  # Annulé
            return
        
        # Sélection de l'IA
        import sauvegarde
        data = sauvegarde.charger()
        ia_selector = IASelector("mixte", cp_disponible=data.get("cp", 5))
        ia_units = ia_selector.select_units()
        
        self.jeu = Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=player_units,
            initial_enemy_units=ia_units,
            enable_placement=True
        )
        self.etat = "jeu"

    def start_versus(self):
        """Lance le mode versus local"""
        # Sélection Joueur 1
        selector1 = UnitSelector(self.screen, "versus", joueur=1)
        player1_units = selector1.run()
        
        if player1_units is None:  # Annulé
            return
        
        # Sélection Joueur 2
        selector2 = UnitSelector(self.screen, "versus", joueur=2)
        player2_units = selector2.run()
        
        if player2_units is None:  # Annulé
            return
        
        # Phase de placement Joueur 1
        from placement import PlacementPhase
        placement1 = PlacementPhase(
            self.screen, 
            player1_units,
            titre="Joueur 1 - Placement des unités",
            player_spawn_zone=[-1, 0, 1],  # Zone verte (haut)
            enemy_spawn_zone=[4, 5, 6]     # Zone rouge (bas)
        )
        player1_placed = placement1.run()
        
        if player1_placed is None:  # Annulé
            return
        
        # Phase de placement Joueur 2
        placement2 = PlacementPhase(
            self.screen, 
            player2_units,
            titre="Joueur 2 - Placement des unités",
            player_spawn_zone=[4, 5, 6],   # Zone rouge devient zone joueur 2
            enemy_spawn_zone=[-1, 0, 1]    # Zone verte devient "ennemie"
        )
        player2_placed = placement2.run()
        
        if player2_placed is None:  # Annulé
            return
        
        # Créer les unités avec leurs positions
        player1_units_with_pos = []
        for cls, pos in player1_placed:
            player1_units_with_pos.append((cls, pos))
        
        player2_units_with_pos = []
        for cls, pos in player2_placed:
            player2_units_with_pos.append((cls, pos))
        
        # Lancement du jeu (pas d'IA, pas de placement automatique)
        self.jeu = Jeu(
            ia_strategy=None,  # Pas d'IA en versus
            screen=self.screen,
            initial_player_units=player1_units_with_pos,
            initial_enemy_units=player2_units_with_pos,
            enable_placement=False,  # Déjà fait
            versus_mode=True  # Nouveau paramètre
        )
        self.etat = "jeu"

    # ------ Méthodes héritées (non modifiées) ------
    def start_hexarene_mode(self):
        """Ancienne méthode - redirige vers mode faction"""
        self.start_hexarene_faction()

    def start_mixte(self):
        """Ancienne méthode - redirige vers mode libre"""
        self.start_hexarene_libre()

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
                elif self.etat == "campagne_menu":
                    for b in self.boutons_campagne_menu: b.handle_event(event)
                elif self.etat == "hexarene_menu":
                    for b in self.boutons_hexarene_menu: b.handle_event(event)
                elif self.etat == "jcj_menu":
                    for b in self.boutons_jcj_menu: b.handle_event(event)
                elif self.etat in ["missions"]:
                    for b in self.boutons_retour_placeholder: b.handle_event(event)
                elif self.etat == "jeu":
                    self.jeu.handle_event(event)

            if self.etat == "menu":
                self.afficher_menu()
            elif self.etat == "playmenu":
                self.afficher_playmenu()
            elif self.etat == "campagne_menu":
                self.afficher_campagne_menu()
            elif self.etat == "hexarene_menu":
                self.afficher_hexarene_menu()
            elif self.etat == "jcj_menu":
                self.afficher_jcj_menu()
            elif self.etat in ["missions"]:
                self.afficher_placeholder()
            elif self.etat == "jeu":
                self.jeu.run_step()

            pygame.display.flip()

    def afficher_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("HexaMaster", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_menu:
            b.draw(self.screen)

    def afficher_playmenu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("Jouer", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_playmenu:
            b.draw(self.screen)

    def afficher_campagne_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("Campagne", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_campagne_menu:
            b.draw(self.screen)

    def afficher_hexarene_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("HexArène", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_hexarene_menu:
            b.draw(self.screen)

    def afficher_jcj_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("Joueur contre Joueur", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_jcj_menu:
            b.draw(self.screen)

    def afficher_placeholder(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("En construction...", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 300))
        for b in self.boutons_retour_placeholder:
            b.draw(self.screen)
