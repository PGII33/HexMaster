import pygame
import sys
import os
from niveau_structure import NiveauConfig, TypeRestriction, sauvegarder_niveau, obtenir_factions_disponibles
from ui_commons import UIManager, ScrollableList
import unites
from placement import PlacementPhase
from unit_selector import UnitSelector

class LevelBuilder:
    def __init__(self, screen):
        self.screen = screen
        self.ui = UIManager(screen)
        
        # État du level builder
        self.etat = "main_menu"  # main_menu, config_generale, restrictions_config, enemy_selection, enemy_placement, rewards_config
        self.running = True
        self.cancelled = False
        
        # Configuration du niveau en cours de création
        self.niveau_config = NiveauConfig()
        
        # UI temporaire
        self.enemy_units_selected = []
        self.text_data = {
            "nom": "",
            "description": "",
            "chapitre": ""
        }
        self.field_rects = {}
        self.factions_disponibles = obtenir_factions_disponibles()
        
        self.creer_boutons()
    
    def creer_boutons(self):
        """Crée les boutons selon l'état actuel"""
        self.ui.clear_buttons()
        w, h = self.screen.get_size()
        center_x = w // 2
        
        if self.etat == "main_menu":
            self.ui.add_button((center_x-140, h//2-150, 280, 50), "Créer Niveau", self.nouveau_niveau)
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour)
        
        elif self.etat == "config_generale":
            # Boutons de navigation
            actions = [
                ("Retour", self.retour_menu),
                ("Suivant: Restrictions", self.config_restrictions)
            ]
            self.ui.add_navigation_buttons(h, actions)
        
        elif self.etat == "restrictions_config":
            # Boutons pour modifier les valeurs (seulement si applicable)
            if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
                # CP disponible (ligne y=170)
                self.ui.add_increment_buttons(550, 170, 
                                            lambda: self.modifier_cp_joueur(1),
                                            lambda: self.modifier_cp_joueur(-1))
                
                # Unités max (ligne y=215)
                self.ui.add_increment_buttons(550, 215,
                                            lambda: self.modifier_max_units(1),
                                            lambda: self.modifier_max_units(-1))
            
            # Bouton pour changer le type de restriction (ligne y=120)
            self.ui.add_button((550, 120, 120, 30), "Changer", self.changer_type_restriction, self.ui.font_small)
            
            # Boutons pour les options de faction (calcul dynamique basé sur les positions réelles)
            # La position y dépend du type de restriction et des éléments affichés
            base_y = 170  # Position après "Type de restriction"
            
            if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
                base_y += 90  # CP (45) + Unités max (55) = 100
            else:
                base_y += 25
            
            # Bouton faction unique (seulement pour FACTION_LIBRE et FACTIONS_DEFINIES)
            if self.niveau_config.type_restriction in [TypeRestriction.FACTION_LIBRE, TypeRestriction.FACTIONS_DEFINIES]:
                self.ui.add_button((550, base_y, 120, 30), "Toggle", self.toggle_faction_unique, self.ui.font_small)
                base_y += 45
            
            # Bouton faction imposée (pour tous sauf UNITES_IMPOSEES)
            if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
                self.ui.add_button((550, base_y, 120, 30), "Changer", self.changer_faction_imposee, self.ui.font_small)
            
            # Navigation
            actions = [
                ("Retour", self.retour_config_general),
                ("Suivant: Ennemis", self.config_ennemis)
            ]
            self.ui.add_navigation_buttons(h, actions)
        
        elif self.etat == "enemy_selection":
            self.ui.add_button((50, 160, 300, 40), "Sélectionner les Ennemis", self.selectionner_ennemis)
            actions = [
                ("Retour", self.retour_restrictions),
                ("Placer Ennemis", self.placer_ennemis)
            ]
            self.ui.add_navigation_buttons(h, actions)
        
        elif self.etat == "rewards_config":
            # Boutons pour modifier les CP de récompense
            self.ui.add_increment_buttons(360, 115,
                                        lambda: self.modifier_cp_recompense(1),
                                        lambda: self.modifier_cp_recompense(-1))
            
            # Navigation
            actions = [
                ("Retour", self.retour_placement),
                ("Sauvegarder", self.sauvegarder_niveau),
                ("Tester Niveau", self.tester_niveau)
            ]
            self.ui.add_navigation_buttons(h, actions)
    
    # ------ Navigation ------
    def retour(self):
        self.cancelled = True
        self.running = False
    
    def retour_menu(self):
        self.etat = "main_menu"
        self.creer_boutons()
    
    def retour_config_general(self):
        self.etat = "config_generale"
        self.creer_boutons()
    
    def retour_restrictions(self):
        self.etat = "restrictions_config"
        self.creer_boutons()
    
    def retour_placement(self):
        self.etat = "enemy_selection"
        self.creer_boutons()
    
    # ------ Modificateurs de paramètres ------
    def modifier_max_units(self, delta):
        """Modifie le nombre max d'unités pour le joueur"""
        new_value = self.niveau_config.max_unites + delta
        self.niveau_config.max_unites = max(1, min(20, new_value))
    
    def modifier_cp_joueur(self, delta):
        """Modifie les CP disponibles pour le joueur"""
        new_value = self.niveau_config.cp_disponible + delta
        self.niveau_config.cp_disponible = max(1, min(20, new_value))
    
    def changer_type_restriction(self):
        """Change le type de restriction cycliquement"""
        types = list(TypeRestriction)
        current_index = types.index(self.niveau_config.type_restriction)
        next_index = (current_index + 1) % len(types)
        self.niveau_config.type_restriction = types[next_index]
    
    def modifier_cp_recompense(self, delta):
        """Modifie les CP de récompense"""
        new_value = self.niveau_config.recompense_cp + delta
        self.niveau_config.recompense_cp = max(0, min(10, new_value))
    
    # ------ Actions principales ------
    def nouveau_niveau(self):
        """Commence la création d'un nouveau niveau"""
        self.niveau_config = NiveauConfig()
        self.enemy_units_selected = []
        self.text_data = {
            "nom": "",
            "description": "",
            "chapitre": ""
        }
        self.etat = "config_generale"
        self.creer_boutons()
    
    def config_restrictions(self):
        """Passe à la configuration des restrictions"""
        # Valider qu'on a au moins un nom
        if not self.text_data["nom"].strip():
            self.text_data["nom"] = "Niveau sans nom"
        
        # Copier les données texte vers la config
        self.niveau_config.nom = self.text_data["nom"]
        self.niveau_config.description = self.text_data["description"]
        self.niveau_config.chapitre = self.text_data["chapitre"]
        
        self.etat = "restrictions_config"
        self.creer_boutons()
    
    def config_ennemis(self):
        """Passe à la sélection des unités ennemies"""
        self.etat = "enemy_selection"
        self.creer_boutons()
    
    def selectionner_ennemis(self):
        """Ouvre le sélecteur d'unités pour les ennemis"""
        # Utiliser le mode builder_enemy pour aucune contrainte
        selector = UnitSelector(self.screen, "builder_enemy")
        selected_units = selector.run()
        
        if selected_units is not None:
            self.enemy_units_selected = selected_units
            print(f"Unités ennemies sélectionnées: {len(self.enemy_units_selected)}")
    
    def placer_ennemis(self):
        """Lance la phase de placement des ennemis"""
        if not self.enemy_units_selected:
            print("Erreur: Aucune unité ennemie sélectionnée")
            return
        
        # Utiliser la phase de placement pour les ennemis (zone rouge)
        placement = PlacementPhase(
            self.screen,
            self.enemy_units_selected,
            titre="Placement des unités ennemies",
            player_spawn_zone=[4, 5, 6],  # Zone rouge pour les ennemis
            enemy_spawn_zone=[-1, 0, 1]   # Zone verte (non utilisée ici)
        )
        
        enemy_placed = placement.run()
        
        if enemy_placed is not None:
            self.niveau_config.unites_ennemis = enemy_placed
            print(f"Ennemis placés: {len(enemy_placed)}")
            self.etat = "rewards_config"
            self.creer_boutons()
        else:
            print("Placement annulé")
    
    def sauvegarder_niveau(self):
        """Sauvegarde le niveau créé"""
        # Valider la configuration
        valide, erreurs = self.niveau_config.valider()
        if not valide:
            print("Erreurs de validation:")
            for erreur in erreurs:
                print(f"- {erreur}")
            return
        
        # Créer le chemin de sauvegarde
        if self.niveau_config.chapitre:
            chemin_dossier = f"Campagne/{self.niveau_config.chapitre.replace(' ', '_')}"
        else:
            chemin_dossier = "custom_levels"
        
        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)
        
        nom_fichier = f"{self.niveau_config.numero:02d}_{self.niveau_config.nom.replace(' ', '_')}"
        chemin_niveau = os.path.join(chemin_dossier, nom_fichier)
        os.makedirs(chemin_niveau, exist_ok=True)
        
        chemin_fichier = os.path.join(chemin_niveau, "niveau.json")
        
        try:
            sauvegarder_niveau(self.niveau_config, chemin_fichier)
            print(f"Niveau sauvegardé: {chemin_fichier}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def tester_niveau(self):
        """Lance le niveau pour le tester"""
        if not self.niveau_config.unites_ennemis:
            print("Erreur: Aucun ennemi placé")
            return
        
        from jeu import Jeu
        import ia
        
        # Créer quelques unités de test pour le joueur selon le type de restriction
        if self.niveau_config.type_restriction == TypeRestriction.UNITES_IMPOSEES:
            test_player_units = self.niveau_config.unites_imposees
        else:
            test_player_units = [
                (unites.Squelette, (0, 0)),
                (unites.Goule, (1, 0)),
            ]
        
        # Lancer le jeu
        jeu = Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=test_player_units,
            initial_enemy_units=self.niveau_config.unites_ennemis,
            enable_placement=not (self.niveau_config.type_restriction == TypeRestriction.UNITES_IMPOSEES and 
                                 self.niveau_config.placement_impose)
        )
        
        # Retourner le jeu pour que le menu principal puisse le lancer
        self.test_game = jeu
        self.running = False
    
    # ------ Affichage ------
    def afficher_main_menu(self):
        """Affiche le menu principal du level builder"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Level Builder", 100)
        self.ui.draw_buttons()
    
    def afficher_config_generale(self):
        """Affiche l'interface de configuration générale"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Configuration du Niveau", 50)
        
        y = 120
        
        # Nom du niveau
        self.ui.draw_text("Nom du niveau:", 50, y)
        nom_rect = self.ui.draw_input_field(200, y-5, 300, 30, self.text_data["nom"], "nom")
        self.field_rects["nom"] = nom_rect
        y += 50
        
        # Description
        self.ui.draw_text("Description:", 50, y)
        desc_rect = self.ui.draw_input_field(200, y-5, 400, 30, self.text_data["description"], "description")
        self.field_rects["description"] = desc_rect
        y += 50
        
        # Chapitre
        self.ui.draw_text("Chapitre:", 50, y)
        chapitre_rect = self.ui.draw_input_field(200, y-5, 300, 30, self.text_data["chapitre"], "chapitre")
        self.field_rects["chapitre"] = chapitre_rect
        
        self.ui.draw_buttons()
    
    def afficher_restrictions_config(self):
        """Affiche l'interface de configuration des restrictions"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Configuration des Restrictions", 50)
        
        y = 120
        
        # Type de restriction
        self.ui.draw_text("Type de restriction:", 50, y, color=(50, 50, 150))
        restriction_text = self.niveau_config.type_restriction.value.replace("_", " ").title()
        self.ui.draw_text(restriction_text, 350, y)
        y += 50
        
        # Configuration spécifique selon le type
        if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
            # CP disponible
            self.ui.draw_text("CP disponible:", 70, y)
            self.ui.draw_text(str(self.niveau_config.cp_disponible), 350, y)
            y += 45
            
            # Unités max
            self.ui.draw_text("Unités max:", 70, y)
            self.ui.draw_text(str(self.niveau_config.max_unites), 350, y)
            y += 55
        else:
            y += 25
        
        # Faction unique (seulement pour certains types)
        if self.niveau_config.type_restriction in [TypeRestriction.FACTION_LIBRE, TypeRestriction.FACTIONS_DEFINIES]:
            self.ui.draw_text("Faction unique requise:", 70, y)
            faction_text = "Oui" if self.niveau_config.faction_unique_requise else "Non"
            self.ui.draw_text(faction_text, 350, y)
            y += 45
        
        # Faction imposée (pour tous types sauf unités imposées)
        if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
            self.ui.draw_text("Faction imposée:", 70, y)
            faction_imposee_text = self.niveau_config.faction_imposee if self.niveau_config.faction_imposee else "Aucune"
            self.ui.draw_text(faction_imposee_text, 350, y)
            y += 45
        
        self.ui.draw_buttons()
    
    def afficher_enemy_selection(self):
        """Affiche l'interface de sélection des ennemis"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Sélection des Ennemis", 50)
        
        # Instructions
        self.ui.draw_text("1. Sélectionnez les unités ennemies", 50, 120, color=(100, 100, 100))
        self.ui.draw_text("2. Placez-les sur la carte", 50, 140, color=(100, 100, 100))
        
        # Afficher les unités sélectionnées
        if self.enemy_units_selected:
            self.ui.draw_text(f"Unités sélectionnées: {len(self.enemy_units_selected)}", 50, 220, color=(0, 150, 0))
            
            y = 250
            for i, cls in enumerate(self.enemy_units_selected[:10]):  # Limiter l'affichage
                tmp = cls("ennemi", (0, 0))
                unit_text = f"- {tmp.get_nom()} ({tmp.faction})"
                self.ui.draw_text(unit_text, 70, y, font=self.ui.font_small)
                y += 25
            
            if len(self.enemy_units_selected) > 10:
                self.ui.draw_text(f"... et {len(self.enemy_units_selected) - 10} autres", 70, y, 
                                font=self.ui.font_small, color=(100, 100, 100))
        else:
            self.ui.draw_text("Aucune unité sélectionnée", 50, 220, color=(200, 0, 0))
        
        self.ui.draw_buttons()
    
    def afficher_rewards_config(self):
        """Affiche l'interface de configuration des récompenses"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Configuration des Récompenses", 50)
        
        y = 120
        
        # CP gagnés
        self.ui.draw_text("CP gagnés à la victoire:", 50, y)
        self.ui.draw_text(str(self.niveau_config.recompense_cp), 310, y)
        y += 60
        
        # Résumé du niveau
        self.ui.draw_text("Résumé du niveau:", 50, y, color=(50, 50, 150))
        y += 40
        
        resume_lines = [
            f"Nom: {self.niveau_config.nom or 'Non défini'}",
            f"Description: {self.niveau_config.description or 'Aucune'}",
            f"Chapitre: {self.niveau_config.chapitre or 'Aucun'}",
            f"Type: {self.niveau_config.type_restriction.value.replace('_', ' ').title()}",
            f"Ennemis placés: {len(self.niveau_config.unites_ennemis)}",
            f"CP joueur: {self.niveau_config.cp_disponible}",
            f"Unités max: {self.niveau_config.max_unites}",
            f"Récompense CP: {self.niveau_config.recompense_cp}",
        ]
        
        for line in resume_lines:
            self.ui.draw_text(line, 70, y, font=self.ui.font_small)
            y += 25
        
        self.ui.draw_buttons()
    
    # ------ Boucle principale ------
    def run(self):
        """Lance le level builder"""
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
                    # Gestion des boutons
                    if not self.ui.handle_button_events(event):
                        # Gestion des clics sur les champs de texte
                        if self.etat == "config_generale":
                            self.ui.handle_field_click(event.pos, self.field_rects)
                
                elif event.type == pygame.KEYDOWN:
                    if self.etat == "config_generale":
                        self.ui.handle_text_input(event, self.text_data, self.ui.champ_actif)
            
            # Affichage selon l'état
            if self.etat == "main_menu":
                self.afficher_main_menu()
            elif self.etat == "config_generale":
                self.afficher_config_generale()
            elif self.etat == "restrictions_config":
                self.afficher_restrictions_config()
            elif self.etat == "enemy_selection":
                self.afficher_enemy_selection()
            elif self.etat == "rewards_config":
                self.afficher_rewards_config()
            
            pygame.display.flip()
        
        # Retourner le jeu de test si créé
        if hasattr(self, 'test_game'):
            return self.test_game
        
        return None
    
    def toggle_faction_unique(self):
        """Toggle l'option faction unique requise"""
        self.niveau_config.faction_unique_requise = not self.niveau_config.faction_unique_requise
    
    def changer_faction_imposee(self):
        """Cycle entre les factions disponibles pour l'imposer"""
        factions_options = [""] + self.factions_disponibles  # "" signifie "Aucune"
        
        if self.niveau_config.faction_imposee in factions_options:
            current_index = factions_options.index(self.niveau_config.faction_imposee)
        else:
            current_index = 0
        
        next_index = (current_index + 1) % len(factions_options)
        self.niveau_config.faction_imposee = factions_options[next_index]