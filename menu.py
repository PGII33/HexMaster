import pygame
import sys
import os
import ia
from jeu import Jeu
from utils import Button, resource_path
from boutique import Boutique
from inventaire import Inventaire
from hexarene import HexArène
from campagne import Campagne, get_niveau_data
from unit_selector import UnitSelector
from ia_selector import IASelector
from sauvegarde import sauvegarder, creer_sauvegarde_defaut
from const import D_DISPLAY_MODE, D_AIDES, BLEU, BLANC

class HexaMaster:
    def __init__(self):
        pygame.init()
        
        # Obtenir la résolution de l'écran
        screen_info = pygame.display.Info()
        self.screen_width = screen_info.current_w
        self.screen_height = screen_info.current_h
        
        # Dimensions par défaut en mode fenêtré (80% de l'écran)
        self.windowed_width = int(self.screen_width * 0.8)
        self.windowed_height = int(self.screen_height * 0.8)
        
        # Démarrer en plein écran
        self.display_mode = D_DISPLAY_MODE
        self.is_fullscreen = True if self.display_mode == "fullscreen" else False  # Pour le VIDEORESIZE event

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                (self.windowed_width, self.windowed_height),
                pygame.RESIZABLE
            )

        pygame.display.set_caption("HexaMaster")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont(None, 80)
        self.font_med = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 20)

        self.etat = "menu"
        self.jeu = None

        self.creer_boutons()

    def set_display_mode(self, mode):
        """Change le mode d'affichage"""
        self.display_mode = mode
        if mode == "fullscreen":
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.windowed_width, self.windowed_height), pygame.RESIZABLE)
        self.creer_boutons()
        if self.jeu:
            self.jeu.screen = self.screen
            self.jeu.recalculer_layout()

    def toggle_display_mode(self):
        if self.display_mode == "windowed":
            self.set_display_mode("fullscreen")
        else:
            self.set_display_mode("windowed")

    def toggle_aide_pv(self):
        D_AIDES["PV"] = not D_AIDES["PV"]
        self.creer_boutons()

    def toggle_aide_dmg(self):
        D_AIDES["DMG"] = not D_AIDES["DMG"]
        self.creer_boutons()

    def toggle_aide_bouclier(self):
        D_AIDES["BOUCLIER"] = not D_AIDES["BOUCLIER"]
        self.creer_boutons()


    def creer_boutons(self):
        w, h = self.screen.get_size()
        center_x = w // 2
        
        # Menu principal - Boutons plus grands avec plus d'espacement
        self.boutons_menu = [
            Button((center_x-160, h//2-200, 320, 70), "Jouer", self.open_playmenu, self.font_med),
            Button((center_x-160, h//2-120, 320, 70), "Inventaire", self.open_inventaire, self.font_med),
            Button((center_x-160, h//2-40, 320, 70), "Boutique", self.open_boutique, self.font_med),
            Button((center_x-160, h//2+40, 320, 70), "Custom", self.open_custom_menu, self.font_med),
            Button((center_x-160, h//2+120, 320, 70), "Quitter", lambda: sys.exit(), self.font_med),
        ]

        # Menu principal des options
        self.boutons_options_main = [
            Button((center_x-200, h//2-100, 400, 70), "Affichage", self.open_option_display, self.font_med, BLEU),
            Button((center_x-200, h//2, 400, 70), "Sauvegarde", self.open_option_save, self.font_med, BLEU),
            Button((center_x-200, h//2+100, 400, 70), "Retour", self.retour_options, self.font_med, BLEU),
        ]

        # Menu des options d'affichage
        self.boutons_options_display = [
            Button((center_x-200, h//2-150, 400, 70),
                   f"Ecran : {self.display_mode}",
                   self.toggle_display_mode, self.font_med, BLEU),
            Button((center_x-200, h//2-50, 400, 70),
                   f"Aide PV : {'ON' if D_AIDES['PV'] else 'OFF'}",
                   self.toggle_aide_pv, self.font_med, BLEU),
            Button((center_x-200, h//2+50, 400, 70),
                   f"Aide DMG : {'ON' if D_AIDES['DMG'] else 'OFF'}",
                   self.toggle_aide_dmg, self.font_med, BLEU),
            Button((center_x-200, h//2+150, 400, 70),
                   f"Aide Bouclier : {'ON' if D_AIDES['BOUCLIER'] else 'OFF'}",
                   self.toggle_aide_bouclier, self.font_med, BLEU),
            Button((center_x-200, h//2+250, 400, 70),
                   "Retour", self.retour_options, self.font_med, BLEU),
        ]

        # Menu des options de sauvegarde
        self.boutons_options_save = [
            Button((center_x-200, h//2, 400, 70), "Réinitialiser Sauvegarde", lambda: sauvegarder(creer_sauvegarde_defaut()), self.font_med, BLEU),
            Button((center_x-200, h//2+100, 400, 70), "Retour", self.retour_options, self.font_med, BLEU),
        ]

        # Bouton Options en haut à droite - présent sur tous les écrans sauf dans les menus d'options
        self.bouton_option = Button((w-140, 20, 120, 50), "Options", self.open_option, self.font_med)

        # Menu Jouer principal
        self.boutons_playmenu = [
            Button((center_x-140, h//2-100, 280, 50), "Campagne", self.start_campagne, self.font_med),
            Button((center_x-140, h//2-40, 280, 50), "HexArène", self.open_hexarene_menu, self.font_med),
            Button((center_x-140, h//2+20, 280, 50), "JcJ", self.open_jcj_menu, self.font_med),
            Button((20, h-70, 150, 50), "Retour", self.back_to_menu, self.font_med),
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

        # Sous-menu Custom
        self.boutons_custom_menu = [
            Button((center_x-140, h//2-60, 280, 50), "Level Builder", self.open_level_builder, self.font_med),
            Button((center_x-140, h//2, 280, 50), "Unite Builder", self.open_unite_builder, self.font_med),
            Button((20, h-70, 150, 50), "Retour", self.back_to_menu, self.font_med),
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

    def open_hexarene_menu(self):
        self.etat = "hexarene_menu"

    def open_jcj_menu(self):
        self.etat = "jcj_menu"

    def open_custom_menu(self):
        self.etat = "custom_menu"

    # ------ Actions des boutons ------
    def open_inventaire(self):
        inv = Inventaire(self.screen)
        inv.afficher()
        self.creer_boutons()

    def open_boutique(self):
        shop = Boutique(self.screen)
        shop.afficher()
        self.creer_boutons()

    def open_option(self):
        """Affiche le menu principal des options"""
        self.etat = "options_main"

    def open_option_display(self):
        """Affiche le menu des options d'affichage"""
        self.etat = "options_display"

    def open_option_save(self):
        """Affiche le menu des options de sauvegarde"""
        self.etat = "options_save"
        
    def retour_options(self):
        """Retourne au menu précédent depuis un menu d'options"""
        if self.etat in ["options_display", "options_save"]:
            self.etat = "options_main"
        else:
            self.etat = "menu"

    def set_display_mode(self, mode):
        """Change le mode d'affichage (windowed ou fullscreen)"""
        self.display_mode = mode
        if mode == "windowed":
            self.screen = pygame.display.set_mode((self.windowed_width, self.windowed_height), pygame.RESIZABLE)
            self.is_fullscreen = False
        else:  # fullscreen
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
            self.is_fullscreen = True
        self.creer_boutons()
        if self.jeu:
            self.jeu.screen = self.screen
            self.jeu.recalculer_layout()

    def open_unite_builder(self):
        """Affiche l'écran du constructeur d'unités (en construction)"""
        self.etat = "unite_builder_construction"

    def open_missions_placeholder(self):
        self.etat = "missions"

    def open_level_builder(self):
        """Lance le level builder"""
        from level_builder import LevelBuilder
        builder = LevelBuilder(self.screen)
        test_game = builder.run()
        
        if test_game:
            # Si un jeu de test a été créé, le lancer
            self.jeu = test_game
            self.etat = "jeu"

    def start_en_ligne_placeholder(self):
        # Placeholder pour le mode en ligne
        print("Mode en ligne - À implémenter")

    def start_campagne(self):
        """Lance le mode campagne"""
        # Vérifier si la structure de campagne existe
        campaign_path = resource_path("Campagne")
        if not os.path.exists(campaign_path):
            print("Aucune campagne trouvée dans le dossier Campagne/")
            print("Veuillez créer manuellement la structure de campagne ou ajouter des niveaux.")
            return
        
        campagne = Campagne(self.screen)
        niveau_info = campagne.run()
        
        if niveau_info is None:  # Annulé
            return
        
        chapitre, numero = niveau_info
        niveau_data = get_niveau_data(chapitre, numero)
        
        if niveau_data is None:
            print("Erreur: Niveau non trouvé")
            return
        
        config = niveau_data["config"]
        player_units = None
        enable_placement = True
        
        # Gestion selon le type de restriction
        if config.type_restriction.value == "unites_imposees":
            # Unités prédéfinies
            player_units = config.unites_imposees
            enable_placement = not config.placement_impose
            
        elif config.type_restriction.value == "faction_libre":
            # Sélection libre avec contraintes CP/max_unités
            selector = UnitSelector(self.screen, "campagne_libre", 
                                  cp_max=config.cp_disponible,
                                  max_units=config.max_unites,
                                  faction_unique=config.faction_unique_requise,
                                  faction_imposee=config.faction_imposee)
            player_units = selector.run()
            
            if player_units is None:  # Annulé
                return
                
        elif config.type_restriction.value == "faction_unique":
            # Sélection avec contrainte faction unique
            selector = UnitSelector(self.screen, "campagne_faction",
                                  cp_max=config.cp_disponible,
                                  max_units=config.max_unites,
                                  faction_unique=True,
                                  faction_imposee=config.faction_imposee)
            player_units = selector.run()
            
            if player_units is None:  # Annulé
                return
        
        if player_units is None:
            print("Erreur: Aucune unité sélectionnée")
            return
        
        # Créer le jeu
        import ia
        self.jeu = Jeu(
            ia_strategy=ia.ia_tactique_avancee,  # IA améliorée pour la campagne
            screen=self.screen,
            initial_player_units=player_units,
            initial_enemy_units=config.unites_ennemis,
            enable_placement=enable_placement,
            versus_mode=False,
            niveau_config=config,  # Passer la configuration du niveau
            chapitre_nom=chapitre,  # Utiliser le nom du chapitre réel
            niveau_nom=config.nom if hasattr(config, 'nom') else f"Niveau {numero}"  # Utiliser le nom du niveau
        )
        self.etat = "jeu"

    def start_hexarene_faction(self):
        """Lance le mode HexArène avec contrainte de faction (joueur et IA sur même faction)"""
        # Utiliser le mode hexarene existant (qui a déjà la contrainte de faction)
        selector = UnitSelector(self.screen, "hexarene")
        player_units = selector.run()
        
        if player_units is None:  # Annulé
            return
        
        # Déterminer la faction du joueur
        player_faction = player_units[0]("joueur", (0,0)).faction if player_units else "Morts-Vivants"
        
        # Sélection de l'IA avec même faction
        import sauvegarde
        data = sauvegarde.charger()
        ia_selector = IASelector("hexarene_faction", 
                                player_cp=data.get("cp", 5),
                                player_faction=player_faction)
        ia_units = ia_selector.select_units()
        
        self.jeu = Jeu(
            ia_strategy=ia.ia_tactique_avancee,  # IA améliorée pour HexArène
            screen=self.screen,
            initial_player_units=player_units,
            initial_enemy_units=ia_units,
            enable_placement=True,
            mode_hexarene=True,  # Activer le mode hexarene
            hexarene_mode_type="faction",
            faction_hexarene=player_faction
        )
        self.etat = "jeu"

    def start_hexarene_libre(self):
        """Lance le mode HexArène libre (joueur et IA peuvent mélanger les factions)"""
        # Utiliser le mode mixte pour le joueur
        selector = UnitSelector(self.screen, "mixte")
        player_units = selector.run()
        
        if player_units is None:  # Annulé
            return
        
        # Sélection de l'IA libre (peut mélanger les factions)
        import sauvegarde
        data = sauvegarde.charger()
        ia_selector = IASelector("hexarene_libre", 
                                player_cp=data.get("cp", 5))
        ia_units = ia_selector.select_units()
        
        self.jeu = Jeu(
            ia_strategy=ia.ia_tactique_avancee,  # IA améliorée pour le mode libre
            screen=self.screen,
            initial_player_units=player_units,
            initial_enemy_units=ia_units,
            enable_placement=True,
            mode_hexarene=True,  # Activer le mode hexarene
            hexarene_mode_type="libre"
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

                if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    # Limiter la taille minimale et maximale de la fenêtre
                    w = max(800, min(event.w, self.screen_width))
                    h = max(600, min(event.h, self.screen_height))
                    self.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                    self.creer_boutons()
                    if self.jeu:
                        self.jeu.screen = self.screen
                        self.jeu.recalculer_layout()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT):
                        self.toggle_fullscreen()

                if self.etat == "menu":
                    for b in self.boutons_menu: b.handle_event(event)
                    self.bouton_option.handle_event(event)
                elif self.etat == "options_main":
                    for b in self.boutons_options_main: b.handle_event(event)
                elif self.etat == "options_display":
                    for b in self.boutons_options_display: b.handle_event(event)
                elif self.etat == "options_save":
                    for b in self.boutons_options_save: b.handle_event(event)
                elif self.etat == "playmenu":
                    for b in self.boutons_playmenu: b.handle_event(event)
                    self.bouton_option.handle_event(event)
                elif self.etat == "campagne_menu":
                    for b in self.boutons_campagne_menu: b.handle_event(event)
                    self.bouton_option.handle_event(event)
                elif self.etat == "hexarene_menu":
                    for b in self.boutons_hexarene_menu: b.handle_event(event)
                    self.bouton_option.handle_event(event)
                elif self.etat == "jcj_menu":
                    for b in self.boutons_jcj_menu: b.handle_event(event)
                    self.bouton_option.handle_event(event)
                elif self.etat == "custom_menu":
                    for b in self.boutons_custom_menu: b.handle_event(event)
                    self.bouton_option.handle_event(event)
                elif self.etat in ["missions", "unite_builder_construction"]:
                    for b in self.boutons_retour_placeholder: b.handle_event(event)
                elif self.etat == "jeu":
                    if self.jeu:
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
            elif self.etat == "custom_menu":
                self.afficher_custom_menu()
            elif self.etat in ["missions", "unite_builder_construction"]:
                self.afficher_placeholder()
            elif self.etat == "options_main":
                self.screen.fill(BLANC)
                title = self.font_big.render("Options", True, (30, 30, 60))
                self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
                for b in self.boutons_options_main: b.draw(self.screen)
                pygame.display.flip()  # Ajout du flip() ici
            elif self.etat == "options_display":
                self.screen.fill(BLANC)
                title = self.font_big.render("Options d'Affichage", True, (30,30,60))
                self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
                for b in self.boutons_options_display: b.draw(self.screen)
                pygame.display.flip()  # Ajout du flip() ici
            elif self.etat == "options_save":
                self.screen.fill(BLANC)
                title = self.font_big.render("Options de Sauvegarde", True, (30, 30, 60))
                self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
                for b in self.boutons_options_save: b.draw(self.screen)
                pygame.display.flip()  # Ajout du flip() ici
            elif self.etat == "jeu":
                if self.jeu:
                    # Vérifier si le jeu est terminé
                    if hasattr(self.jeu, 'finished') and self.jeu.finished:
                        # Si le menu de fin de combat n'est pas encore affiché ET pas encore traité, l'activer
                        if (not getattr(self.jeu, 'show_end_menu', False) and 
                            not getattr(self.jeu, 'end_menu_processed', False)):
                            # Activer le menu de fin de combat avec le bon résultat
                            victoire = getattr(self.jeu, 'player_victory', False)
                            self.jeu.activer_menu_fin_combat(victoire)
                        
                        # Si le menu de fin de combat est affiché, continuer à dessiner le jeu
                        if getattr(self.jeu, 'show_end_menu', False):
                            self.jeu.update(dt)
                            self.jeu.dessiner()
                        else:
                            # Le menu a été fermé ET déjà traité, retourner au menu principal
                            if getattr(self.jeu, 'end_menu_processed', False):
                                # Si c'est une victoire en campagne, appliquer récompenses 
                                if (hasattr(self.jeu, 'player_victory') and self.jeu.player_victory and
                                    hasattr(self.jeu, 'niveau_config') and self.jeu.niveau_config):
                                    # Appliquer les récompenses du niveau (campagne)
                                    niveau_config = self.jeu.niveau_config
                                    if hasattr(niveau_config, 'chapitre') and hasattr(niveau_config, 'numero'):
                                        from sauvegarde import marquer_niveau_complete, appliquer_recompenses
                                        
                                        # Convertir le nom de chapitre si nécessaire
                                        chapitre_display = niveau_config.chapitre
                                        if "_" in chapitre_display:
                                            chapitre_display = chapitre_display.split("_", 1)[1].replace("_", " ")
                                        
                                        # Marquer comme complété et appliquer récompenses
                                        marquer_niveau_complete(chapitre_display, niveau_config.numero)
                                        appliquer_recompenses(niveau_config)
                                
                                self.etat = "menu"
                                self.jeu = None
                    else:
                        self.jeu.update(dt)
                        self.jeu.dessiner()

            pygame.display.flip()

    def afficher_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("HexaMaster", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_menu:
            b.draw(self.screen)
        self.bouton_option.draw(self.screen)

    def afficher_playmenu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("Jouer", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_playmenu:
            b.draw(self.screen)
        self.bouton_option.draw(self.screen)

    def afficher_campagne_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("Campagne", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_campagne_menu:
            b.draw(self.screen)
        self.bouton_option.draw(self.screen)

    def afficher_hexarene_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("HexArène", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_hexarene_menu:
            b.draw(self.screen)
        self.bouton_option.draw(self.screen)

    def afficher_jcj_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("Joueur contre Joueur", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_jcj_menu:
            b.draw(self.screen)
        self.bouton_option.draw(self.screen)

    def afficher_custom_menu(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("Custom", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        for b in self.boutons_custom_menu:
            b.draw(self.screen)
        self.bouton_option.draw(self.screen)

    def afficher_placeholder(self):
        self.screen.fill(BLANC)
        title = self.font_big.render("En construction...", True, BLEU)
        subtitle = None
            
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 250))
        if subtitle:
            self.screen.blit(subtitle, (self.screen.get_width()//2 - subtitle.get_width()//2, 320))
        for b in self.boutons_retour_placeholder:
            b.draw(self.screen)

    def afficher_options(self):
        """Affiche le menu d'options avec debug de sauvegarde"""
        self.screen.fill(BLANC)
        
        # Titre
        title = self.font_big.render("Options", True, BLEU)
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 50))
        
        # Boutons
        for b in self.boutons_options:
            b.draw(self.screen)
