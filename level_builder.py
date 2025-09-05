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
        self.etat = "main_menu"  # main_menu, config_generale, restrictions_config, enemy_selection, enemy_placement, rewards_config, selection_unite_deblocage
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
            self.ui.add_increment_buttons(550, 120,
                                        lambda: self.modifier_cp_recompense(1),
                                        lambda: self.modifier_cp_recompense(-1))
            
            # Boutons pour modifier les PA de récompense
            self.ui.add_increment_buttons(550, 170,
                                        lambda: self.modifier_pa_recompense(10),
                                        lambda: self.modifier_pa_recompense(-10))
            
            # Boutons pour gérer les unités débloquées
            self.ui.add_button((550, 220, 100, 30), "Ajouter", self.ajouter_unite_debloquee, self.ui.font_small)
            self.ui.add_button((660, 220, 100, 30), "Retirer", self.retirer_unite_debloquee, self.ui.font_small)
            self.ui.add_button((770, 220, 100, 30), "Effacer", self.effacer_unites_debloquees, self.ui.font_small)
            
            # Navigation
            actions = [
                ("Retour", self.retour_placement),
                ("Sauvegarder", self.sauvegarder_niveau),
                ("Tester Niveau", self.tester_niveau)
            ]
            self.ui.add_navigation_buttons(h, actions)
        
        elif self.etat == "selection_unite_deblocage":
            # Boutons pour chaque unité disponible
            if hasattr(self, 'unites_disponibles_pour_selection'):
                y_start = 150
                for i, unite in enumerate(self.unites_disponibles_pour_selection):
                    y_pos = y_start + (i * 35)
                    # Limiter l'affichage pour éviter de sortir de l'écran
                    if y_pos > self.screen.get_height() - 100:
                        break
                    
                    # Bouton pour cette unité
                    button_text = f"{unite['nom']} ({unite['faction']}) - T{unite['tier']}"
                    self.ui.add_button((50, y_pos, 600, 30), button_text, 
                                     lambda u=unite: self.selectionner_unite_deblocage(u), 
                                     self.ui.font_small)
            
            # Navigation
            actions = [
                ("Annuler", self.annuler_selection_unite)
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
    
    def modifier_pa_recompense(self, delta):
        """Modifie les PA de récompense"""
        new_value = self.niveau_config.recompense_pa + delta
        self.niveau_config.recompense_pa = max(0, min(500, new_value))  # Max 500 PA
    
    def ajouter_unite_debloquee(self):
        """Lance l'interface de sélection d'unité à débloquer"""
        from unites import CLASSES_UNITES
        
        # Obtenir les unités déjà débloquées
        unites_deja_debloquees = set(self.niveau_config.unites_debloquees)
        
        # Créer la liste des unités disponibles
        unites_disponibles = []
        for classe_unite in CLASSES_UNITES:
            nom_classe = classe_unite.__name__
            if nom_classe not in unites_deja_debloquees:
                instance_temp = classe_unite(equipe=0, pos=(0, 0))
                unites_disponibles.append({
                    'classe': nom_classe,
                    'nom': instance_temp.nom,
                    'faction': instance_temp.faction,
                    'tier': instance_temp.tier,
                    'prix': instance_temp.prix if hasattr(instance_temp, 'prix') else 0
                })
        
        if not unites_disponibles:
            print("Toutes les unités sont déjà dans les récompenses")
            return
        
        # Trier par faction puis par tier
        unites_disponibles.sort(key=lambda x: (x['faction'], x['tier']))
        
        # Passer en mode sélection d'unité
        self.unites_disponibles_pour_selection = unites_disponibles
        self.etat_precedent = self.etat
        self.etat = "selection_unite_deblocage"
        self.creer_boutons()
    def _afficher_prochaine_unite_disponible(self, x, y):
        """Affiche quelle unité sera ajoutée au prochain clic"""
        from unites import CLASSES_UNITES
        
        # Obtenir les unités déjà débloquées
        unites_deja_debloquees = set(self.niveau_config.unites_debloquees)
        
        # Créer la liste des unités disponibles
        unites_disponibles = []
        for classe_unite in CLASSES_UNITES:
            nom_classe = classe_unite.__name__
            if nom_classe not in unites_deja_debloquees:
                instance_temp = classe_unite(equipe=0, pos=(0, 0))
                unites_disponibles.append({
                    'classe': nom_classe,
                    'nom': instance_temp.nom,
                    'faction': instance_temp.faction,
                    'tier': instance_temp.tier
                })
        
        if not unites_disponibles:
            self.ui.draw_text("Prochaine: (toutes débloquées)", x, y, font=self.ui.font_small, color=(100, 100, 100))
            return
        
        # Trier par faction puis par tier
        unites_disponibles.sort(key=lambda x: (x['faction'], x['tier']))
        
        # Obtenir l'index actuel
        if not hasattr(self, '_index_unite_selection'):
            self._index_unite_selection = 0
        
    def retirer_unite_debloquee(self):
        """Retire la dernière unité des récompenses de déblocage"""
        if self.niveau_config.unites_debloquees:
            unite_retiree = self.niveau_config.unites_debloquees.pop()
            print(f"Unité retirée des récompenses: {unite_retiree}")
        else:
            print("Aucune unité à retirer")
    
    def effacer_unites_debloquees(self):
        """Efface toutes les unités des récompenses de déblocage"""
        if self.niveau_config.unites_debloquees:
            nb_unites = len(self.niveau_config.unites_debloquees)
            self.niveau_config.unites_debloquees.clear()
            print(f"Toutes les unités débloquées ont été retirées ({nb_unites} unités)")
        else:
            print("Aucune unité à effacer")
    
    def selectionner_unite_deblocage(self, unite_data):
        """Sélectionne une unité spécifique pour déblocage"""
        self.niveau_config.unites_debloquees.append(unite_data['classe'])
        print(f"Unité ajoutée: {unite_data['nom']} ({unite_data['faction']}) - Tier {unite_data['tier']}")
        
        # Retourner à l'état précédent (ou rewards_config par défaut)
        self.etat = getattr(self, 'etat_precedent', 'rewards_config')
        self.creer_boutons()
    
    def annuler_selection_unite(self):
        """Annule la sélection d'unité et retourne à l'état précédent"""
        self.etat = getattr(self, 'etat_precedent', 'rewards_config')
        self.creer_boutons()
    
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
        """Lance le niveau pour le tester avec toutes les contraintes"""
        # Valider le niveau avant le test
        valide, erreurs = self.niveau_config.valider()
        if not valide:
            print("Erreur: Le niveau n'est pas valide:")
            for erreur in erreurs:
                print(f"- {erreur}")
            return
        
        if not self.niveau_config.unites_ennemis:
            print("Erreur: Aucun ennemi placé")
            return
        
        print(f"Lancement du test du niveau: {self.niveau_config.nom}")
        print(f"Type de restriction: {self.niveau_config.type_restriction.value}")
        
        # Si le type de restriction impose des unités spécifiques, les utiliser directement
        if self.niveau_config.type_restriction == TypeRestriction.UNITES_IMPOSEES:
            if not self.niveau_config.unites_imposees:
                print("Erreur: Aucune unité imposée définie")
                return
            
            # Lancer directement le jeu avec les unités imposées
            self._lancer_jeu_test(self.niveau_config.unites_imposees)
            
        else:
            # Utiliser le sélecteur d'unités avec toutes les contraintes
            self._lancer_selecteur_test()
    
    def _lancer_selecteur_test(self):
        """Lance le sélecteur d'unités pour le test avec les contraintes du niveau"""
        
        print("Ouverture du sélecteur d'unités pour le test...")
        print(f"Contraintes actives:")
        print(f"  - Type: {self.niveau_config.type_restriction.value}")
        print(f"  - CP disponible: {self.niveau_config.cp_disponible}")
        print(f"  - Unités max: {self.niveau_config.max_unites}")
        if self.niveau_config.faction_imposee:
            print(f"  - Faction imposée: {self.niveau_config.faction_imposee}")
        if self.niveau_config.faction_unique_requise:
            print(f"  - Faction unique requise: Oui")
        
        # Créer un inventaire de test (toutes les unités disponibles)
        inventaire_test = self._creer_inventaire_test()
        
        # Déterminer le mode selon le type de restriction
        mode_selector = self._get_mode_for_restriction()
        
        try:
            # Lancer le sélecteur avec les contraintes du niveau
            unit_selector = UnitSelector(
                screen=self.screen,
                mode=mode_selector,
                inventaire_joueur=inventaire_test,
                type_restriction=self.niveau_config.type_restriction,
                unites_imposees=self.niveau_config.unites_imposees,
                factions_definies=self.niveau_config.factions_autorisees,
                faction_unique_requise=self.niveau_config.faction_unique_requise,
                cp_disponible=self.niveau_config.cp_disponible,
                max_unites=self.niveau_config.max_unites,
                faction_imposee=self.niveau_config.faction_imposee,
                # Paramètres spécifiques selon le mode
                max_units=self.niveau_config.max_unites,
                cp_max=self.niveau_config.cp_disponible,
                faction_unique=self.niveau_config.faction_unique_requise
            )
            
            # Lancer la sélection
            unites_selectionnees = unit_selector.run()
            
            if unites_selectionnees and not unit_selector.cancelled:
                print(f"Unités sélectionnées pour le test: {len(unites_selectionnees)}")
                self._lancer_jeu_test(unites_selectionnees)
            else:
                print("Test annulé: Aucune unité sélectionnée")
                
        except Exception as e:
            print(f"Erreur lors du lancement du sélecteur: {e}")
            print("Utilisation d'unités par défaut pour le test...")
            # Fallback avec des unités par défaut (juste les classes)
            unites_defaut = [
                unites.Squelette,
                unites.Goule
            ]
            self._lancer_jeu_test(unites_defaut)
    
    def _get_mode_for_restriction(self):
        """Retourne le mode de sélecteur approprié selon le type de restriction"""
        if self.niveau_config.type_restriction == TypeRestriction.FACTION_LIBRE:
            return "campagne_libre"
        elif self.niveau_config.type_restriction == TypeRestriction.FACTION_UNIQUE:
            return "campagne_faction"
        elif self.niveau_config.type_restriction == TypeRestriction.FACTIONS_DEFINIES:
            return "campagne_definies"
        else:  # TypeRestriction.UNITES_IMPOSEES
            return "campagne"  # Mode prédéfini pour unités imposées
    
    def _creer_inventaire_test(self):
        """Crée un inventaire de test avec toutes les unités disponibles"""
        from unites import CLASSES_UNITES
        
        inventaire_test = []
        for classe_unite in CLASSES_UNITES:
            # Ajouter plusieurs exemplaires de chaque unité pour le test
            for _ in range(3):  # 3 exemplaires de chaque
                inventaire_test.append(classe_unite.__name__)
        
        print(f"Inventaire de test créé: {len(inventaire_test)} unités disponibles")
        return inventaire_test
    
    def _lancer_jeu_test(self, unites_joueur):
        """Lance le jeu de test avec les unités spécifiées"""
        from jeu import Jeu
        import ia
        
        print(f"Lancement du jeu de test avec {len(unites_joueur)} unités joueur")
        
        # Afficher les unités du joueur
        print("Unités du joueur:")
        for classe in unites_joueur:
            if hasattr(classe, '__name__'):
                nom_classe = classe.__name__
            else:
                nom_classe = str(classe)
            print(f"  - {nom_classe}")
        
        # Lancer le jeu avec IA tactique avancée pour les tests
        jeu = Jeu(
            ia_strategy=ia.ia_tactique_avancee,  # Utiliser l'IA améliorée pour les tests
            screen=self.screen,
            initial_player_units=unites_joueur,
            initial_enemy_units=self.niveau_config.unites_ennemis,
            enable_placement=not (self.niveau_config.type_restriction == TypeRestriction.UNITES_IMPOSEES and 
                                 self.niveau_config.placement_impose),
            niveau_config=self.niveau_config  # Passer la config pour tests
        )
        
        # Stocker le jeu pour que le menu principal puisse le lancer
        self.test_game = jeu
        self.running = False
        print("Jeu de test préparé - fermeture du level builder")
    
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
        self.ui.draw_text(str(self.niveau_config.recompense_cp), 350, y)
        y += 50
        
        # PA gagnés
        self.ui.draw_text("PA gagnés à la victoire:", 50, y)
        self.ui.draw_text(str(self.niveau_config.recompense_pa), 350, y)
        y += 50
        
        # Unités débloquées
        self.ui.draw_text("Unités débloquées:", 50, y, color=(50, 50, 150))
        y += 30
        
        if self.niveau_config.unites_debloquees:
            for i, nom_classe in enumerate(self.niveau_config.unites_debloquees):
                # Créer une instance temporaire pour obtenir le nom d'affichage
                try:
                    from unites import CLASSES_UNITES
                    classe = next(c for c in CLASSES_UNITES if c.__name__ == nom_classe)
                    instance_temp = classe(equipe=0, pos=(0, 0))
                    self.ui.draw_text(f"• {instance_temp.nom} ({instance_temp.faction})", 70, y, font=self.ui.font_small)
                    y += 25
                except:
                    self.ui.draw_text(f"• {nom_classe} (erreur)", 70, y, font=self.ui.font_small, color=(200, 0, 0))
                    y += 25
        else:
            self.ui.draw_text("Aucune unité débloquée", 70, y, font=self.ui.font_small, color=(100, 100, 100))
            y += 25
        
        # Afficher la prochaine unité qui sera ajoutée
        y += 20
        
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
            f"Récompense PA: {self.niveau_config.recompense_pa}",
            f"Unités débloquées: {len(self.niveau_config.unites_debloquees)}",
        ]
        
        for line in resume_lines:
            self.ui.draw_text(line, 70, y, font=self.ui.font_small)
            y += 25
        
        self.ui.draw_buttons()
    
    def afficher_selection_unite_deblocage(self):
        """Affiche l'interface de sélection d'unité pour déblocage"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Sélection d'Unité à Débloquer", 50)
        
        # Instructions
        self.ui.draw_text("Choisissez l'unité à ajouter aux récompenses:", 50, 120, color=(50, 50, 150))
        
        # Afficher les unités disponibles
        if hasattr(self, 'unites_disponibles_pour_selection'):
            y = 150
            faction_actuelle = None
            
            for unite in self.unites_disponibles_pour_selection:
                # Afficher un séparateur de faction
                if unite['faction'] != faction_actuelle:
                    if faction_actuelle is not None:
                        y += 10  # Espacement entre factions
                    self.ui.draw_text(f"--- {unite['faction']} ---", 70, y, color=(100, 100, 100))
                    faction_actuelle = unite['faction']
                    y += 30
                
                # Les boutons sont créés dans creer_boutons(), ici on fait juste l'espacement
                y += 35
                
                # Limiter l'affichage
                if y > self.screen.get_height() - 100:
                    nb_restantes = len([u for u in self.unites_disponibles_pour_selection 
                                      if self.unites_disponibles_pour_selection.index(u) > 
                                      self.unites_disponibles_pour_selection.index(unite)])
                    if nb_restantes > 0:
                        self.ui.draw_text(f"... et {nb_restantes} autres unités", 70, y, 
                                        color=(100, 100, 100), font=self.ui.font_small)
                    break
        
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
            elif self.etat == "selection_unite_deblocage":
                self.afficher_selection_unite_deblocage()
            
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