import pygame
import sys
import json
import os
from utils import Button
import unites
from placement import PlacementPhase
from unit_selector import UnitSelector

class LevelBuilder:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 20)
        
        # État du level builder
        self.etat = "main_menu"  # main_menu, config_generale, enemy_selection, enemy_placement, rewards_config
        self.running = True
        self.cancelled = False
        
        # Données du niveau en cours de création
        self.level_data = {
            "nom": "",
            "description": "",
            "unites_ennemis": [],  # [(classe, position), ...]
            "contraintes_joueur": {
                "max_units": 14,
                "cp_disponible": 5,
                "faction_unique": True,
                "faction_requise": None
            },
            "recompenses": {
                "cp": 1,
                "unites_debloquees": [],
                "autres": []
            }
        }
        
        # UI temporaire
        self.champ_actif = None
        self.enemy_units_selected = []
        self.scroll_y = 0
        self.scroll_speed = 30
        
        self.creer_boutons()
    
    def creer_boutons(self):
        """Crée les boutons selon l'état actuel"""
        w, h = self.screen.get_size()
        center_x = w // 2
        
        if self.etat == "main_menu":
            self.boutons = [
                Button((center_x-140, h//2-150, 280, 50), "Nouveau Niveau", self.nouveau_niveau, self.font),
                Button((center_x-140, h//2-90, 280, 50), "Charger Niveau", self.charger_niveau, self.font),
                Button((center_x-140, h//2-30, 280, 50), "Gestionnaire Chapitres", self.gestionnaire_chapitres, self.font),
                Button((20, h-70, 150, 50), "Retour", self.retour, self.font),
            ]
        
        elif self.etat == "config_generale":
            self.boutons = [
                # Boutons pour modifier max_units (- puis + et alignés)
                Button((530, 250, 30, 30), "-", lambda: self.modifier_max_units(-1), self.font_small),
                Button((570, 250, 30, 30), "+", lambda: self.modifier_max_units(1), self.font_small),
                
                # Boutons pour modifier CP (- puis + et alignés)
                Button((530, 290, 30, 30), "-", lambda: self.modifier_cp_joueur(-1), self.font_small),
                Button((570, 290, 30, 30), "+", lambda: self.modifier_cp_joueur(1), self.font_small),
                
                # Bouton pour toggle faction unique (aligné)
                Button((530, 330, 120, 30), "Basculer", self.toggle_faction_unique, self.font_small),
                
                # Navigation
                Button((center_x-100, h-150, 200, 40), "Suivant: Ennemis", self.config_ennemis, self.font),
                Button((20, h-70, 150, 50), "Retour", self.retour_menu, self.font),
            ]
        
        elif self.etat == "enemy_selection":
            self.boutons = [
                Button((50, 160, 300, 40), "Sélectionner les Ennemis", self.selectionner_ennemis, self.font),
                Button((center_x-100, h-150, 200, 40), "Placer Ennemis", self.placer_ennemis, self.font),
                Button((20, h-70, 150, 50), "Retour", self.retour_config, self.font),
            ]
        
        elif self.etat == "rewards_config":
            self.boutons = [
                # Boutons pour modifier les CP de récompense (- puis + et alignés)
                Button((360, 115, 30, 30), "-", lambda: self.modifier_cp_recompense(-1), self.font_small),
                Button((400, 115, 30, 30), "+", lambda: self.modifier_cp_recompense(1), self.font_small),
                
                # Navigation
                Button((center_x-100, h-150, 200, 40), "Sauvegarder", self.sauvegarder_niveau, self.font),
                Button((center_x-100, h-100, 200, 40), "Tester Niveau", self.tester_niveau, self.font),
                Button((20, h-70, 150, 50), "Retour", self.retour_placement, self.font),
            ]
    
    # ------ Navigation ------
    def retour(self):
        self.cancelled = True
        self.running = False
    
    def retour_menu(self):
        self.etat = "main_menu"
        self.creer_boutons()
    
    def retour_config(self):
        self.etat = "config_generale"
        self.creer_boutons()
    
    def retour_placement(self):
        self.etat = "enemy_selection"
        self.creer_boutons()
    
    # ------ Modificateurs de paramètres ------
    def modifier_max_units(self, delta):
        """Modifie le nombre max d'unités pour le joueur"""
        new_value = self.level_data["contraintes_joueur"]["max_units"] + delta
        self.level_data["contraintes_joueur"]["max_units"] = max(1, min(20, new_value))
    
    def modifier_cp_joueur(self, delta):
        """Modifie les CP disponibles pour le joueur"""
        new_value = self.level_data["contraintes_joueur"]["cp_disponible"] + delta
        self.level_data["contraintes_joueur"]["cp_disponible"] = max(1, min(20, new_value))
    
    def toggle_faction_unique(self):
        """Active/désactive la contrainte de faction unique"""
        self.level_data["contraintes_joueur"]["faction_unique"] = not self.level_data["contraintes_joueur"]["faction_unique"]
    
    def modifier_cp_recompense(self, delta):
        """Modifie les CP de récompense"""
        new_value = self.level_data["recompenses"]["cp"] + delta
        self.level_data["recompenses"]["cp"] = max(0, min(10, new_value))
    
    # ------ Actions principales ------
    def nouveau_niveau(self):
        """Commence la création d'un nouveau niveau"""
        self.level_data = {
            "nom": "",
            "description": "",
            "unites_ennemis": [],
            "contraintes_joueur": {
                "max_units": 14,
                "cp_disponible": 5,
                "faction_unique": True,
                "faction_requise": None
            },
            "recompenses": {
                "cp": 1,
                "unites_debloquees": [],
                "autres": []
            }
        }
        self.enemy_units_selected = []
        self.etat = "config_generale"
        self.creer_boutons()
    
    def charger_niveau(self):
        """Charge un niveau existant"""
        # TODO: Implémenter le chargement de fichiers
        print("Chargement de niveau - À implémenter")
    
    def gestionnaire_chapitres(self):
        """Ouvre le gestionnaire de chapitres"""
        # TODO: Implémenter le gestionnaire de chapitres
        print("Gestionnaire de chapitres - À implémenter")
    
    def config_ennemis(self):
        """Passe à la sélection des unités ennemies"""
        # Valider qu'on a au moins un nom
        if not self.level_data["nom"].strip():
            self.level_data["nom"] = "Niveau sans nom"
        
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
            self.level_data["unites_ennemis"] = enemy_placed
            print(f"Ennemis placés: {len(enemy_placed)}")
            self.etat = "rewards_config"
            self.creer_boutons()
        else:
            print("Placement annulé")
    
    def sauvegarder_niveau(self):
        """Sauvegarde le niveau créé"""
        if not self.level_data["nom"].strip():
            print("Erreur: Le niveau doit avoir un nom")
            return
        
        if not self.level_data["unites_ennemis"]:
            print("Erreur: Le niveau doit avoir des ennemis")
            return
        
        # Créer le dossier custom_levels s'il n'existe pas
        if not os.path.exists("custom_levels"):
            os.makedirs("custom_levels")
        
        filename = f"custom_levels/{self.level_data['nom'].replace(' ', '_')}.json"
        
        # Convertir les classes d'unités en noms pour la sauvegarde
        level_data_save = self.level_data.copy()
        level_data_save["unites_ennemis"] = [
            (cls.__name__, pos) for cls, pos in self.level_data["unites_ennemis"]
        ]
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(level_data_save, f, indent=2, ensure_ascii=False)
            print(f"Niveau sauvegardé: {filename}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    
    def tester_niveau(self):
        """Lance le niveau pour le tester"""
        if not self.level_data["unites_ennemis"]:
            print("Erreur: Aucun ennemi placé")
            return
        
        from jeu import Jeu
        import ia
        
        # Créer quelques unités de test pour le joueur
        test_player_units = [
            (unites.Squelette, (0, 0)),
            (unites.Goule, (1, 0)),
        ]
        
        # Lancer le jeu
        jeu = Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=test_player_units,
            initial_enemy_units=self.level_data["unites_ennemis"],
            enable_placement=False
        )
        
        # Retourner le jeu pour que le menu principal puisse le lancer
        self.test_game = jeu
        self.running = False
    
    # ------ Affichage ------
    def afficher_main_menu(self):
        """Affiche le menu principal du level builder"""
        self.screen.fill((255, 255, 255))
        
        title = self.font_big.render("Level Builder", True, (50, 50, 150))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
        
        for btn in self.boutons:
            btn.draw(self.screen)
    
    def afficher_config_generale(self):
        """Affiche l'interface de configuration générale"""
        self.screen.fill((255, 255, 255))
        
        title = self.font_big.render("Configuration du Niveau", True, (50, 50, 150))
        self.screen.blit(title, (50, 50))
        
        y = 120
        
        # Nom du niveau
        nom_label = self.font.render("Nom du niveau:", True, (0, 0, 0))
        self.screen.blit(nom_label, (50, y))
        
        # Zone de texte pour le nom
        nom_rect = pygame.Rect(200, y-5, 300, 30)
        color = (255, 255, 200) if self.champ_actif == "nom" else (240, 240, 240)
        pygame.draw.rect(self.screen, color, nom_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), nom_rect, 2)
        
        nom_text = self.font.render(self.level_data["nom"], True, (0, 0, 0))
        self.screen.blit(nom_text, (nom_rect.x + 5, nom_rect.y + 5))
        
        y += 50
        
        # Description
        desc_label = self.font.render("Description:", True, (0, 0, 0))
        self.screen.blit(desc_label, (50, y))
        
        desc_rect = pygame.Rect(200, y-5, 400, 30)
        color = (255, 255, 200) if self.champ_actif == "description" else (240, 240, 240)
        pygame.draw.rect(self.screen, color, desc_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), desc_rect, 2)
        
        desc_text = self.font.render(self.level_data["description"], True, (0, 0, 0))
        self.screen.blit(desc_text, (desc_rect.x + 5, desc_rect.y + 5))
        
        y += 70
        
        # Contraintes joueur
        contraintes_title = self.font.render("Contraintes du joueur:", True, (50, 50, 150))
        self.screen.blit(contraintes_title, (50, y))
        y += 40
        
        # Max unités avec boutons +/- alignés
        max_units_label = self.font.render("Unités max:", True, (0, 0, 0))
        self.screen.blit(max_units_label, (70, y))
        
        max_units_value = self.font.render(str(self.level_data["contraintes_joueur"]["max_units"]), True, (0, 0, 0))
        self.screen.blit(max_units_value, (480, y))
        
        y += 40
        
        # CP disponible avec boutons +/- alignés
        cp_label = self.font.render("CP disponible:", True, (0, 0, 0))
        self.screen.blit(cp_label, (70, y))
        
        cp_value = self.font.render(str(self.level_data["contraintes_joueur"]["cp_disponible"]), True, (0, 0, 0))
        self.screen.blit(cp_value, (480, y))
        
        y += 40
        
        # Faction unique avec bouton toggle aligné
        faction_label = self.font.render("Faction unique:", True, (0, 0, 0))
        self.screen.blit(faction_label, (70, y))
        
        faction_value = "Oui" if self.level_data["contraintes_joueur"]["faction_unique"] else "Non"
        faction_text = self.font.render(faction_value, True, (0, 0, 0))
        self.screen.blit(faction_text, (480, y))
        
        # Dessiner tous les boutons
        for btn in self.boutons:
            btn.draw(self.screen)
    
    def afficher_enemy_selection(self):
        """Affiche l'interface de sélection des ennemis"""
        self.screen.fill((255, 255, 255))
        
        title = self.font_big.render("Sélection des Ennemis", True, (50, 50, 150))
        self.screen.blit(title, (50, 50))
        
        # Instructions
        info_text = self.font.render("1. Sélectionnez les unités ennemies", True, (100, 100, 100))
        self.screen.blit(info_text, (50, 120))
        
        info_text2 = self.font.render("2. Placez-les sur la carte", True, (100, 100, 100))
        self.screen.blit(info_text2, (50, 140))
        
        # Afficher les unités sélectionnées
        if self.enemy_units_selected:
            selected_text = self.font.render(f"Unités sélectionnées: {len(self.enemy_units_selected)}", True, (0, 150, 0))
            self.screen.blit(selected_text, (50, 220))
            
            y = 250
            for i, cls in enumerate(self.enemy_units_selected[:10]):  # Limiter l'affichage
                tmp = cls("ennemi", (0, 0))
                unit_text = self.font_small.render(f"- {tmp.get_nom()} ({tmp.faction})", True, (0, 0, 0))
                self.screen.blit(unit_text, (70, y))
                y += 25
            
            if len(self.enemy_units_selected) > 10:
                more_text = self.font_small.render(f"... et {len(self.enemy_units_selected) - 10} autres", True, (100, 100, 100))
                self.screen.blit(more_text, (70, y))
        else:
            no_selection_text = self.font.render("Aucune unité sélectionnée", True, (200, 0, 0))
            self.screen.blit(no_selection_text, (50, 220))
        
        for btn in self.boutons:
            btn.draw(self.screen)
    
    def afficher_rewards_config(self):
        """Affiche l'interface de configuration des récompenses"""
        self.screen.fill((255, 255, 255))
        
        title = self.font_big.render("Configuration des Récompenses", True, (50, 50, 150))
        self.screen.blit(title, (50, 50))
        
        y = 120
        
        # CP gagnés avec boutons +/- alignés
        cp_label = self.font.render("CP gagnés à la victoire:", True, (0, 0, 0))
        self.screen.blit(cp_label, (50, y))
        
        cp_value = self.font.render(str(self.level_data["recompenses"]["cp"]), True, (0, 0, 0))
        self.screen.blit(cp_value, (310, y))
        
        y += 60
        
        # Résumé du niveau
        resume_title = self.font.render("Résumé du niveau:", True, (50, 50, 150))
        self.screen.blit(resume_title, (50, y))
        y += 40
        
        resume_lines = [
            f"Nom: {self.level_data['nom'] or 'Non défini'}",
            f"Description: {self.level_data['description'] or 'Aucune'}",
            f"Ennemis placés: {len(self.level_data['unites_ennemis'])}",
            f"CP joueur: {self.level_data['contraintes_joueur']['cp_disponible']}",
            f"Unités max: {self.level_data['contraintes_joueur']['max_units']}",
            f"Faction unique: {'Oui' if self.level_data['contraintes_joueur']['faction_unique'] else 'Non'}",
            f"Récompense CP: {self.level_data['recompenses']['cp']}",
        ]
        
        for line in resume_lines:
            text = self.font_small.render(line, True, (0, 0, 0))
            self.screen.blit(text, (70, y))
            y += 25
        
        for btn in self.boutons:
            btn.draw(self.screen)
    
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
                    self.creer_boutons()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in self.boutons:
                        btn.handle_event(event)
                    
                    # Gestion des inputs texte pour la config générale
                    if self.etat == "config_generale":
                        self.gerer_clics_config(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if self.etat == "config_generale":
                        self.gerer_input_texte(event)
            
            # Affichage selon l'état
            if self.etat == "main_menu":
                self.afficher_main_menu()
            elif self.etat == "config_generale":
                self.afficher_config_generale()
            elif self.etat == "enemy_selection":
                self.afficher_enemy_selection()
            elif self.etat == "rewards_config":
                self.afficher_rewards_config()
            
            pygame.display.flip()
        
        # Retourner le jeu de test si créé
        if hasattr(self, 'test_game'):
            return self.test_game
        
        return None
    
    def gerer_clics_config(self, pos):
        """Gère les clics sur les zones de texte en mode config"""
        # Zones de texte pour nom et description
        nom_rect = pygame.Rect(200, 115, 300, 30)
        desc_rect = pygame.Rect(200, 165, 400, 30)
        
        if nom_rect.collidepoint(pos):
            self.champ_actif = "nom"
        elif desc_rect.collidepoint(pos):
            self.champ_actif = "description"
        else:
            self.champ_actif = None
    
    def gerer_input_texte(self, event):
        """Gère la saisie de texte"""
        if self.champ_actif is None:
            return
        
        if event.key == pygame.K_BACKSPACE:
            if self.champ_actif == "nom":
                self.level_data["nom"] = self.level_data["nom"][:-1]
            elif self.champ_actif == "description":
                self.level_data["description"] = self.level_data["description"][:-1]
        
        elif event.unicode.isprintable():
            if self.champ_actif == "nom":
                if len(self.level_data["nom"]) < 30:
                    self.level_data["nom"] += event.unicode
            elif self.champ_actif == "description":
                if len(self.level_data["description"]) < 60:
                    self.level_data["description"] += event.unicode