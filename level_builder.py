""" level_builder.py - Interface de création et modification de niveaux"""
import sys
import os
import re
import shutil
import pygame
from niveau_structure import NiveauConfig, TypeRestriction
from niveau_structure import sauvegarder_niveau, obtenir_factions_disponibles
from niveau_structure import charger_niveau
from ui_commons import UIManager
from utils import handle_scroll_events
import unites
from path_utils import get_custom_levels_path, get_campaign_path
from unites_liste import CLASSES_UNITES
from placement import PlacementPhase
from unit_selector import UnitSelector
from const import MAX_CP, MAX_PA
from jeu import Jeu
import ia

# pylint: disable=no-member broad-exception-caught line-too-long

# Constantes


class LevelBuilder:
    """ Interface de création et modification de niveaux """
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

        # Variables pour la préservation des positions
        self._derniere_composition = []
        self._positions_sauvegardees = []

        # Système de scroll pour le menu de sélection d'unités
        self.scroll_offset = 0
        self.scroll_max = 0
        self.items_visible = 0

        self.text_data = {
            "numero": "01",
            "nom": "",
            "description": "",
            "chapitre": "CUSTOM"
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
            self.ui.add_button((center_x-140, h//2-180, 280, 50),
                               "Créer Niveau", self.nouveau_niveau)
            self.ui.add_button((center_x-140, h//2-120, 280, 50),
                               "Modifier Niveau", self.modifier_niveau)
            self.ui.add_button((center_x-140, h//2-60, 280, 50),
                               "Jouer Niveau", self.charger_niveau_custom)
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour)

        elif self.etat == "selection_niveau":
            # Interface de sélection de niveau à modifier
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour_menu)

        elif self.etat == "selection_niveau_custom":
            # Interface de sélection de niveau custom à charger
            self.ui.add_button((20, h-70, 150, 50), "Retour", self.retour_menu)

        elif self.etat == "config_generale":
            # Boutons de navigation
            actions = [
                ("Retour", self.retour_menu),
                ("Suivant: Restrictions", self.config_restrictions)
            ]
            self.ui.add_navigation_buttons(h, actions)

        elif self.etat == "restrictions_config":
            # Bouton pour changer le type de restriction (toujours disponible)
            self.ui.add_button((550, 120, 120, 30), "Changer",
                               self.changer_type_restriction, self.ui.font_small)

            # Boutons pour modifier les valeurs (seulement si les unités ne sont pas imposées)
            if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
                # CP disponible (ligne y=170)
                self.ui.add_increment_buttons(550, 170,
                                              lambda: self.modifier_cp_joueur(
                                                  1),
                                              lambda: self.modifier_cp_joueur(-1))

                # Unités max (ligne y=215)
                self.ui.add_increment_buttons(550, 215,
                                              lambda: self.modifier_max_units(
                                                  1),
                                              lambda: self.modifier_max_units(-1))

            # Calcul dynamique des positions pour les boutons de faction
            base_y = 170  # Position après "Type de restriction"

            if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
                base_y += 90  # CP (45) + Unités max (55) = 100
            else:
                base_y += 25

            # Bouton faction unique (seulement pour FACTION_LIBRE)
            if self.niveau_config.type_restriction == TypeRestriction.FACTION_LIBRE:
                self.ui.add_button((550, base_y, 120, 30), "Toggle",
                                   self.toggle_faction_unique, self.ui.font_small)
                base_y += 45

            # Bouton faction imposée (pour tous sauf UNITES_IMPOSEES)
            if self.niveau_config.type_restriction != TypeRestriction.UNITES_IMPOSEES:
                self.ui.add_button((550, base_y, 120, 30), "Changer",
                                   self.changer_faction_imposee, self.ui.font_small)

            # Navigation
            actions = [
                ("Retour", self.retour_config_general),
                ("Suivant: Ennemis", self.config_ennemis)
            ]
            self.ui.add_navigation_buttons(h, actions)

        elif self.etat == "enemy_selection":
            self.ui.add_button(
                (50, 160, 300, 40), "Sélectionner les Ennemis", self.selectionner_ennemis)

            # Texte du bouton selon le mode
            placement_button_text = "Modifier Placement" if (hasattr(self, 'niveau_selectionne') and
                                                             self.niveau_selectionne and
                                                             self.niveau_config.unites_ennemis) else "Placer Ennemis"

            actions = [
                ("Retour", self.retour_restrictions),
                (placement_button_text, self.placer_ennemis)
            ]
            self.ui.add_navigation_buttons(h, actions)

        elif self.etat == "rewards_config":
            # Boutons pour modifier les CP de récompense
            self.ui.add_increment_buttons(550, 120,
                                          lambda: self.modifier_cp_recompense(
                                              1),
                                          lambda: self.modifier_cp_recompense(-1))

            # Boutons pour modifier les PA de récompense
            self.ui.add_increment_buttons(550, 170,
                                          lambda: self.modifier_pa_recompense(
                                              10),
                                          lambda: self.modifier_pa_recompense(-10))

            # Boutons pour gérer les unités débloquées
            self.ui.add_button((550, 220, 100, 30), "Ajouter",
                               self.ajouter_unite_debloquee, self.ui.font_small)
            self.ui.add_button((660, 220, 100, 30), "Retirer",
                               self.retirer_unite_debloquee, self.ui.font_small)
            self.ui.add_button((770, 220, 100, 30), "Effacer",
                               self.effacer_unites_debloquees, self.ui.font_small)

            # Navigation
            actions = [
                ("Retour", self.retour_placement),
                ("Sauvegarder", self.sauvegarder_niveau),
                ("Tester Niveau", self.tester_niveau)
            ]
            self.ui.add_navigation_buttons(h, actions)

        elif self.etat == "selection_unite_deblocage":
            # Boutons pour chaque unité disponible avec scroll
            if hasattr(self, 'unites_disponibles_pour_selection'):
                y_start = 150
                item_height = 35
                visible_area_height = self.screen.get_height() - 200  # Zone visible
                self.items_visible = visible_area_height // item_height

                total_items = len(self.unites_disponibles_pour_selection)
                self.scroll_max = max(0, total_items - self.items_visible)

                # Limiter le scroll_offset
                self.scroll_offset = max(
                    0, min(self.scroll_offset, self.scroll_max))

                # Afficher seulement les éléments visibles
                start_idx = self.scroll_offset
                end_idx = min(start_idx + self.items_visible, total_items)

                for i in range(start_idx, end_idx):
                    unite = self.unites_disponibles_pour_selection[i]
                    y_pos = y_start + ((i - start_idx) * item_height)

                    # Bouton pour cette unité
                    button_text = f"{unite['nom']} ({unite['faction']}) - T{unite['tier']}"
                    self.ui.add_button((50, y_pos, 600, 30), button_text,
                                       lambda u=unite: self.selectionner_unite_deblocage(
                                           u),
                                       self.ui.font_small)

                # Indicateurs de scroll
                if self.scroll_max > 0:
                    # Flèche haut
                    if self.scroll_offset > 0:
                        self.ui.add_button((660, y_start - 30, 80, 25), "Haut",
                                           self.scroll_up, self.ui.font_small)

                    # Flèche bas
                    if self.scroll_offset < self.scroll_max:
                        bottom_y = y_start + (self.items_visible * item_height)
                        self.ui.add_button((660, bottom_y + 10, 80, 25), "Bas",
                                           self.scroll_down, self.ui.font_small)

                    # Indicateur de position
                    scroll_info = f"{self.scroll_offset + 1}-{min(self.scroll_offset + self.items_visible, total_items)} / {total_items}"
                    text_surface = self.ui.font_small.render(
                        scroll_info, True, (100, 100, 100))
                    info_y = y_start + (self.items_visible * item_height) + 40
                    self.screen.blit(text_surface, (660, info_y))

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

    # ------ Méthodes de scroll ------
    def scroll_up(self):
        """Fait défiler vers le haut"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self.creer_boutons()

    def scroll_down(self):
        """Fait défiler vers le bas"""
        if self.scroll_offset < self.scroll_max:
            self.scroll_offset += 1
            self.creer_boutons()

    def reset_scroll(self):
        """Remet le scroll à zéro"""
        self.scroll_offset = 0

    # ------ Modification de niveau ------
    def modifier_niveau(self):
        """Lance l'interface de sélection de niveau à modifier"""
        self.etat = "selection_niveau"
        # Inclure à la fois les niveaux de campagne et les niveaux custom
        niveaux_campagne = self._charger_liste_niveaux_campagne()
        niveaux_custom = self._charger_liste_niveaux_custom()
        self.niveaux_disponibles = niveaux_campagne + niveaux_custom
        self.niveau_selectionne = None
        self.creer_boutons()

    def charger_niveau_custom(self):
        """Lance l'interface de sélection de niveau custom à jouer"""
        self.etat = "selection_niveau_custom"
        self.niveaux_disponibles = self._charger_liste_niveaux_custom()
        self.niveau_selectionne = None
        self.creer_boutons()

    def _charger_liste_niveaux_campagne(self):
        """Charge la liste des niveaux disponibles dans le dossier Campagne"""
        niveaux = []

        # Utiliser le système de chemins externe/EXE
        campagne_path = get_campaign_path()

        if not campagne_path.exists():
            return niveaux

        # Parcourir les chapitres
        for chapitre_folder in sorted(os.listdir(campagne_path)):
            chapitre_path = campagne_path / chapitre_folder
            if not chapitre_path.is_dir():
                continue

            # Extraire le nom du chapitre
            if "_" in chapitre_folder:
                chapitre_nom = chapitre_folder.split(
                    "_", 1)[1].replace("_", " ")
            else:
                chapitre_nom = chapitre_folder

            # Parcourir les niveaux du chapitre
            for niveau_folder in sorted(os.listdir(chapitre_path)):
                niveau_path = chapitre_path / niveau_folder
                if not niveau_path.is_dir():
                    continue

                niveau_file = niveau_path / "niveau.json"
                if niveau_file.exists():
                    try:
                        config = charger_niveau(niveau_file)
                        if config:
                            niveaux.append({
                                "nom": config.nom or f"Niveau {config.numero}",
                                "chapitre": chapitre_nom,
                                "numero": config.numero,
                                "chemin": niveau_file,
                                "config": config,
                                "type": "campagne"
                            })
                    except Exception as e:
                        print(
                            f"Erreur lors du chargement de {niveau_file}: {e}")

        return niveaux

    def _charger_liste_niveaux_custom(self):
        """Charge la liste des niveaux custom disponibles"""
        niveaux = []

        # Utiliser le système de chemins externe/EXE
        custom_path = get_custom_levels_path()

        if not custom_path.exists():
            custom_path.mkdir(parents=True, exist_ok=True)
            return niveaux

        # Fonction récursive pour parcourir les dossiers
        def parcourir_dossier(dossier_path, chapitre_parent="Niveaux Custom"):
            for item in sorted(os.listdir(dossier_path)):
                item_path = dossier_path / item
                
                # Si c'est un dossier
                if item_path.is_dir():
                    # Chercher niveau.json dans ce dossier
                    niveau_file = item_path / "niveau.json"
                    if niveau_file.exists():
                        try:
                            config = charger_niveau(niveau_file)
                            if config:
                                # Utiliser le chapitre de la config, sinon "CUSTOM", sinon le nom du dossier parent
                                chapitre_config = getattr(config, 'chapitre', None)
                                if chapitre_config and chapitre_config.strip():
                                    chapitre = chapitre_config
                                elif chapitre_parent != "Niveaux Custom":
                                    chapitre = chapitre_parent
                                else:
                                    chapitre = "CUSTOM"
                                niveaux.append({
                                    "nom": config.nom or item,
                                    "chapitre": chapitre,
                                    "numero": getattr(config, 'numero', 0),
                                    "chemin": niveau_file,
                                    "config": config,
                                    "type": "custom"
                                })
                        except Exception as e:
                            print(f"Erreur lors du chargement du niveau custom {niveau_file}: {e}")
                    else:
                        # Pas de niveau.json, peut-être un sous-dossier de chapitre
                        # Parcourir récursivement avec le nom du dossier comme chapitre
                        parcourir_dossier(item_path, item)
                
                # Si c'est un fichier .json directement (compatibilité ancienne)
                elif item.endswith(".json"):
                    try:
                        config = charger_niveau(item_path)
                        if config:
                            # Utiliser le chapitre de la config, sinon "CUSTOM"
                            chapitre_config = getattr(config, 'chapitre', None)
                            if chapitre_config and chapitre_config.strip():
                                chapitre = chapitre_config
                            else:
                                chapitre = "CUSTOM"
                            niveaux.append({
                                "nom": config.nom or item[:-5],
                                "chapitre": chapitre,
                                "numero": getattr(config, 'numero', 0),
                                "chemin": item_path,
                                "config": config,
                                "type": "custom"
                            })
                    except Exception as e:
                        print(f"Erreur lors du chargement du niveau custom {item_path}: {e}")

        # Lancer le parcours
        parcourir_dossier(custom_path)

        return niveaux

    def _charger_liste_niveaux(self):
        """Ancienne fonction - maintenant appelle la version campagne pour compatibilité"""
        return self._charger_liste_niveaux_campagne()

    def charger_niveau_pour_modification(self, niveau_info):
        """Charge un niveau existant pour modification"""
        try:
            config = charger_niveau(niveau_info["chemin"])
            if config:
                self.niveau_config = config
                self.niveau_selectionne = niveau_info
                # Charger les données de texte pour l'interface
                self.text_data = {
                    "numero": f"{config.numero:02d}",
                    "nom": config.nom,
                    "description": config.description,
                    "chapitre": config.chapitre
                }

                # Récupérer les unités ennemies existantes pour la modification
                self.enemy_units_selected = []
                for unit_class, _ in config.unites_ennemis:
                    self.enemy_units_selected.append(unit_class)

                # Initialiser les variables de préservation avec les données existantes
                self._derniere_composition = self.enemy_units_selected[:]
                self._positions_sauvegardees = config.unites_ennemis[:]

                print(f"Niveau '{config.nom}' chargé pour modification")
                print(
                    f"  - {len(config.unites_ennemis)} unités ennemies chargées")
                print(
                    f"  - Types d'unités: {[cls.__name__ for cls, pos in config.unites_ennemis]}")

                # Aller à la configuration générale pour modification
                self.etat = "config_generale"
                self.creer_boutons()
            else:
                print("Erreur lors du chargement du niveau")
        except Exception as e:
            print(f"Erreur: {e}")

    def sauvegarder_niveau_modifie(self):
        """Sauvegarde les modifications sur le niveau existant"""
        if self.niveau_selectionne:
            try:

                # Vérifier si le nom de dossier doit changer
                ancien_chemin = self.niveau_selectionne["chemin"]
                ancien_dossier = os.path.dirname(ancien_chemin)
                dossier_parent = os.path.dirname(ancien_dossier)

                # Calculer le nouveau nom de dossier
                nouveau_nom_dossier = f"{self.niveau_config.numero:02d}_{self.niveau_config.nom.replace(' ', '_')}"
                nouveau_dossier = os.path.join(
                    dossier_parent, nouveau_nom_dossier)
                nouveau_chemin = os.path.join(nouveau_dossier, "niveau.json")

                # Si le dossier a changé, renommer
                if ancien_dossier != nouveau_dossier and os.path.exists(ancien_dossier):
                    if os.path.exists(nouveau_dossier):
                        # Si le nouveau dossier existe déjà, supprimer l'ancien après sauvegarde
                        sauvegarder_niveau(self.niveau_config, nouveau_chemin)
                        shutil.rmtree(ancien_dossier)
                    else:
                        # Renommer le dossier
                        os.rename(ancien_dossier, nouveau_dossier)
                        sauvegarder_niveau(self.niveau_config, nouveau_chemin)
                else:
                    # Utiliser le chemin original si pas de changement
                    sauvegarder_niveau(self.niveau_config, ancien_chemin)

                print(
                    f"Niveau '{self.niveau_config.nom}' mis à jour avec succès!")
                # Retourner au menu principal
                self.etat = "main_menu"
                self.creer_boutons()
            except Exception as e:
                print(f"Erreur lors de la sauvegarde: {e}")
        else:
            # Comportement normal pour nouveau niveau
            self.sauvegarder_niveau()

    # ------ Modificateurs de paramètres ------
    def modifier_max_units(self, delta):
        """Modifie le nombre max d'unités pour le joueur"""
        new_value = self.niveau_config.max_unites + delta
        self.niveau_config.max_unites = max(1, new_value)

    def modifier_cp_joueur(self, delta):
        """Modifie les CP disponibles pour le joueur"""
        new_value = self.niveau_config.cp_disponible + delta
        self.niveau_config.cp_disponible = max(1, min(96, new_value))

    def changer_type_restriction(self):
        """Change le type de restriction cycliquement"""
        types = list(TypeRestriction)
        current_index = types.index(self.niveau_config.type_restriction)
        next_index = (current_index + 1) % len(types)
        self.niveau_config.type_restriction = types[next_index]
        # Recréer les boutons pour refléter le nouveau type de restriction
        self.creer_boutons()

    def modifier_cp_recompense(self, delta):
        """Modifie les CP de récompense"""
        new_value = self.niveau_config.recompense_cp + delta
        self.niveau_config.recompense_cp = max(0, min(MAX_CP, new_value))

    def modifier_pa_recompense(self, delta):
        """Modifie les PA de récompense"""
        new_value = self.niveau_config.recompense_pa + delta
        self.niveau_config.recompense_pa = max(0, min(MAX_PA, new_value))

    def ajouter_unite_debloquee(self):
        """Lance l'interface de sélection d'unité à débloquer"""

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
                    'faction': instance_temp.get_faction(),
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
        self.reset_scroll()  # Remettre le scroll à zéro
        self.creer_boutons()

    def _afficher_prochaine_unite_disponible(self, x, y):
        """Affiche quelle unité sera ajoutée au prochain clic"""

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
                    'faction': instance_temp.get_faction(),
                    'tier': instance_temp.tier
                })

        if not unites_disponibles:
            self.ui.draw_text("Prochaine: (toutes débloquées)", x,
                              y, font=self.ui.font_small, color=(100, 100, 100))
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
            print(
                f"Toutes les unités débloquées ont été retirées ({nb_unites} unités)")
        else:
            print("Aucune unité à effacer")

    def selectionner_unite_deblocage(self, unite_data):
        """Sélectionne une unité spécifique pour déblocage"""
        self.niveau_config.unites_debloquees.append(unite_data['classe'])
        print(
            f"Unité ajoutée: {unite_data['nom']} ({unite_data['faction']}) - Tier {unite_data['tier']}")

        # Retourner à l'état précédent (ou rewards_config par défaut)
        self.etat = getattr(self, 'etat_precedent', 'rewards_config')
        self.creer_boutons()

    def annuler_selection_unite(self):
        """Annule la sélection d'unité et retourne à l'état précédent"""
        self.etat = getattr(self, 'etat_precedent', 'rewards_config')
        self.creer_boutons()

    # ------ Gestion de la préservation des positions ------
    def _compositions_identiques(self, comp1, comp2):
        """Vérifie si deux compositions d'unités sont identiques"""
        if len(comp1) != len(comp2):
            return False

        # Compter les occurrences de chaque classe dans chaque composition
        count1 = {}
        count2 = {}

        for cls in comp1:
            count1[cls] = count1.get(cls, 0) + 1

        for cls in comp2:
            count2[cls] = count2.get(cls, 0) + 1

        return count1 == count2

    def _conserver_positions_communes(self, ancienne_composition, nouvelle_composition):
        """Conserve les positions des unités communes lors d'un changement de composition"""
        if not self.niveau_config.unites_ennemis:
            return

        # Créer des dictionnaires de comptage pour les compositions
        ancien_count = {}
        nouveau_count = {}

        for cls in ancienne_composition:
            ancien_count[cls] = ancien_count.get(cls, 0) + 1

        for cls in nouvelle_composition:
            nouveau_count[cls] = nouveau_count.get(cls, 0) + 1

        # Identifier les unités communes (minimum entre ancien et nouveau count)
        unites_communes = {}
        for cls in ancien_count:
            if cls in nouveau_count:
                unites_communes[cls] = min(
                    ancien_count[cls], nouveau_count[cls])

        if not unites_communes:
            # Aucune unité commune, effacer toutes les positions
            self.niveau_config.unites_ennemis = []
            print("Aucune unité commune, positions effacées")
            return

        # Conserver seulement les positions des unités communes
        nouvelles_positions = []
        unites_conservees = {}

        for unit_class, position in self.niveau_config.unites_ennemis:
            if (unit_class in unites_communes and
                    unites_conservees.get(unit_class, 0) < unites_communes[unit_class]):
                nouvelles_positions.append((unit_class, position))
                unites_conservees[unit_class] = unites_conservees.get(
                    unit_class, 0) + 1

        self.niveau_config.unites_ennemis = nouvelles_positions

        print(
            f"Positions conservées: {len(nouvelles_positions)} unités communes")
        for cls, count in unites_conservees.items():
            print(f"  - {cls.__name__}: {count} position(s) conservée(s)")

    # ------ Actions principales ------
    def nouveau_niveau(self):
        """Commence la création d'un nouveau niveau"""
        self.niveau_config = NiveauConfig()
        self.enemy_units_selected = []

        # Réinitialiser les variables de préservation des positions
        self._derniere_composition = []
        self._positions_sauvegardees = []

        self.text_data = {
            "numero": "01",
            "nom": "",
            "description": "",
            "chapitre": "CUSTOM"
        }
        # Réinitialiser le niveau sélectionné si on était en mode modification
        self.niveau_selectionne = None
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
        # Passer les unités actuellement sélectionnées pour les pré-sélectionner
        selector = UnitSelector(
            self.screen, "builder_enemy", preselected_units=self.enemy_units_selected)
        selected_units = selector.run()

        if selected_units is not None:
            # Conserver les positions existantes pour les unités communes
            old_units = self.enemy_units_selected[:]
            self.enemy_units_selected = selected_units

            # Si on a des unités placées et qu'on change la composition
            if hasattr(self, 'niveau_config') and self.niveau_config.unites_ennemis:
                self._conserver_positions_communes(old_units, selected_units)

            print(
                f"Unités ennemies sélectionnées: {len(self.enemy_units_selected)}")

    def placer_ennemis(self):
        """Lance la phase de placement des ennemis"""
        if not self.enemy_units_selected:
            print("Erreur: Aucune unité ennemie sélectionnée")
            return

        # Préparer les unités existantes si on est en mode modification OU
        # si on a des positions sauvegardées pour cette composition
        existing_units = None

        # Cas 1: Mode modification d'un niveau existant
        if hasattr(self, 'niveau_selectionne') and self.niveau_selectionne and self.niveau_config.unites_ennemis:
            existing_units = []
            for unit_class, position in self.niveau_config.unites_ennemis:
                existing_units.append((unit_class, position))
            print(
                f"Chargement du placement existant (modification): {len(existing_units)} unités")

        # Cas 2: Retour au placement avec la même composition (préservation des positions)
        elif (hasattr(self, '_derniere_composition') and
              hasattr(self, '_positions_sauvegardees') and
              self._compositions_identiques(self._derniere_composition, self.enemy_units_selected)):
            existing_units = self._positions_sauvegardees[:]
            print(
                f"Restauration du placement précédent: {len(existing_units)} unités")

        # Utiliser la phase de placement pour les ennemis (zone rouge)
        placement = PlacementPhase(
            self.screen,
            self.enemy_units_selected,
            titre="Placement des unités ennemies" +
            (" (Modification)" if existing_units else ""),
            player_spawn_zone=[4, 5, 6],  # Zone rouge pour les ennemis
            enemy_spawn_zone=[-1, 0, 1],   # Zone verte (non utilisée ici)
            existing_units=existing_units   # Passer les unités existantes
        )

        enemy_placed = placement.run()

        if enemy_placed is not None:
            self.niveau_config.unites_ennemis = enemy_placed

            # Sauvegarder cette composition et ces positions pour future restauration
            self._derniere_composition = self.enemy_units_selected[:]
            self._positions_sauvegardees = enemy_placed[:]

            print(f"Ennemis placés: {len(enemy_placed)}")
            self.etat = "rewards_config"
            self.creer_boutons()
        else:
            print("Placement annulé")

    def sauvegarder_niveau(self):
        """Sauvegarde le niveau (nouveau ou modifié)"""
        from const import D_CUSTOM_LEVELS_PATH
        
        # Synchroniser les données de configuration avec les champs de texte
        self._synchroniser_config_avec_ui()

        # Si on a un niveau sélectionné, on est en mode modification
        if hasattr(self, 'niveau_selectionne') and self.niveau_selectionne:
            self.sauvegarder_niveau_modifie()
            return

        # Sinon, sauvegarde normale pour nouveau niveau
        # Valider la configuration
        valide, erreurs = self.niveau_config.valider()
        if not valide:
            print("Erreurs de validation:")
            for erreur in erreurs:
                print(f"- {erreur}")
            return

        # TOUJOURS sauvegarder dans custom_levels (jamais dans Campagne)
        chemin_base = D_CUSTOM_LEVELS_PATH
        
        # Si un chapitre est spécifié, créer un sous-dossier dans custom_levels
        if self.niveau_config.chapitre and self.niveau_config.chapitre.strip():
            # Nettoyer le nom du chapitre
            chapitre_nettoye = self.niveau_config.chapitre.strip().replace(' ', '_')
            chemin_dossier = os.path.join(chemin_base, chapitre_nettoye)
        else:
            # Pas de chapitre -> directement dans custom_levels
            chemin_dossier = chemin_base

        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)

        # Structure: dossier/numero_nom/niveau.json
        nom_fichier = f"{self.niveau_config.numero:02d}_{self.niveau_config.nom.replace(' ', '_')}"
        chemin_niveau = os.path.join(chemin_dossier, nom_fichier)
        os.makedirs(chemin_niveau, exist_ok=True)

        chemin_fichier = os.path.join(chemin_niveau, "niveau.json")

        try:
            sauvegarder_niveau(self.niveau_config, chemin_fichier)
            print(f"Niveau custom sauvegardé: {chemin_fichier}")
            print(f"  → Vous pouvez le charger via 'Level Builder > Jouer Niveau'")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def _ensure_text_data_complete(self):
        """S'assure que tous les champs requis sont présents dans text_data"""
        defaults = {
            "numero": "01",
            "nom": "",
            "description": "",
            "chapitre": "CUSTOM"
        }
        for key, default_value in defaults.items():
            if key not in self.text_data:
                self.text_data[key] = default_value

    def _handle_text_input_with_validation(self, event):
        """Gère la saisie de texte avec validation spécifique selon le champ"""
        if not self.ui.champ_actif:
            return

        field_name = self.ui.champ_actif

        if event.key == pygame.K_BACKSPACE:
            if field_name in self.text_data:
                self.text_data[field_name] = self.text_data[field_name][:-1]
        elif event.unicode.isprintable():
            if field_name == "numero":
                # Validation spéciale pour le numéro : seulement des chiffres, max 2 caractères
                if event.unicode.isdigit() and len(self.text_data.get(field_name, "")) < 2:
                    self.text_data[field_name] = self.text_data.get(
                        field_name, "") + event.unicode
            else:
                # Gestion normale pour les autres champs
                max_length = 50 if field_name != "nom" else 30
                if field_name in self.text_data and len(self.text_data[field_name]) < max_length:
                    self.text_data[field_name] += event.unicode

    def _synchroniser_config_avec_ui(self):
        """Met à jour la configuration avec les données de l'interface utilisateur"""
        self.niveau_config.nom = self.text_data.get("nom", "")
        self.niveau_config.description = self.text_data.get("description", "")
        self.niveau_config.chapitre = self.text_data.get("chapitre", "")

        # Traiter le numéro (s'assurer qu'il s'agit d'un entier valide entre 0 et 99)
        try:
            numero_str = self.text_data.get("numero", "01").strip()
            if numero_str:
                numero = int(numero_str)
                self.niveau_config.numero = max(
                    0, min(99, numero))  # Limiter entre 0 et 99
            else:
                self.niveau_config.numero = 1
        except ValueError:
            self.niveau_config.numero = 1

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
        print(
            f"Type de restriction: {self.niveau_config.type_restriction.value}")

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
                print(
                    f"Unités sélectionnées pour le test: {len(unites_selectionnees)}")
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
        else:  # TypeRestriction.UNITES_IMPOSEES
            return "campagne"  # Mode prédéfini pour unités imposées

    def _creer_inventaire_test(self):
        """Crée un inventaire de test avec toutes les unités disponibles"""

        inventaire_test = []
        for classe_unite in CLASSES_UNITES:
            # Ajouter plusieurs exemplaires de chaque unité pour le test
            for _ in range(3):  # 3 exemplaires de chaque
                inventaire_test.append(classe_unite.__name__)

        print(
            f"Inventaire de test créé: {len(inventaire_test)} unités disponibles")
        return inventaire_test

    def _lancer_jeu_test(self, unites_joueur):
        """Lance le jeu de test avec les unités spécifiées"""

        print(
            f"Lancement du jeu de test avec {len(unites_joueur)} unités joueur")

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

    def afficher_selection_niveau(self):
        """Affiche l'interface de sélection de niveau à modifier"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Modifier un Niveau", 50)

        y = 120

        if not hasattr(self, 'niveaux_disponibles') or not self.niveaux_disponibles:
            self.ui.draw_text(
                "Aucun niveau trouvé dans le dossier Campagne/", 50, y, color=(255, 0, 0))
            self.ui.draw_buttons()
            return

        self.ui.draw_text("Sélectionnez un niveau à modifier:", 50, y)
        y += 40

        # Afficher la liste des niveaux
        max_visible = 12  # Nombre maximum de niveaux visibles
        start_index = getattr(self, 'scroll_offset', 0)
        end_index = min(start_index + max_visible,
                        len(self.niveaux_disponibles))

        for i in range(start_index, end_index):
            niveau = self.niveaux_disponibles[i]

            # Couleur alternée pour la lisibilité
            bg_color = (240, 240, 240) if i % 2 == 0 else (255, 255, 255)

            # Rectangle de fond
            niveau_rect = pygame.Rect(50, y, 700, 35)
            pygame.draw.rect(self.screen, bg_color, niveau_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), niveau_rect, 1)

            # Texte du niveau
            text = f"{niveau['chapitre']} - {niveau['nom']} (Niveau {niveau['numero']})"
            self.ui.draw_text(text, 60, y + 8, color=(0, 0, 0))

            # Stocker le rectangle pour la détection de clic
            if not hasattr(self, 'niveau_rects'):
                self.niveau_rects = {}
            self.niveau_rects[i] = niveau_rect

            y += 40

        # Indicateurs de scroll si nécessaire
        if len(self.niveaux_disponibles) > max_visible:
            total_pages = (len(self.niveaux_disponibles) -
                           1) // max_visible + 1
            current_page = start_index // max_visible + 1
            self.ui.draw_text(f"Page {current_page}/{total_pages} - Utilisez la molette pour défiler",
                              50, y + 20, color=(100, 100, 100))

        self.ui.draw_buttons()

    def afficher_selection_niveau_custom(self):
        """Affiche l'interface de sélection de niveau custom à jouer"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Jouer un Niveau Custom", 50)

        y = 120

        if not hasattr(self, 'niveaux_disponibles') or not self.niveaux_disponibles:
            self.ui.draw_text(
                "Aucun niveau custom trouvé dans le dossier custom_levels/", 50, y, color=(255, 0, 0))
            self.ui.draw_text(
                "Créez d'abord des niveaux et sauvegardez-les dans custom_levels/", 50, y + 30, color=(100, 100, 100))
            self.ui.draw_buttons()
            return

        self.ui.draw_text("Sélectionnez un niveau custom à jouer:", 50, y)
        y += 40

        # Afficher la liste des niveaux
        max_visible = 12  # Nombre maximum de niveaux visibles
        start_index = getattr(self, 'scroll_offset', 0)
        end_index = min(start_index + max_visible,
                        len(self.niveaux_disponibles))

        for i in range(start_index, end_index):
            niveau = self.niveaux_disponibles[i]

            # Couleur alternée pour la lisibilité
            bg_color = (240, 255, 240) if i % 2 == 0 else (
                255, 255, 255)  # Teinte verte pour les customs

            # Rectangle de fond
            niveau_rect = pygame.Rect(50, y, 700, 35)
            pygame.draw.rect(self.screen, bg_color, niveau_rect)
            pygame.draw.rect(self.screen, (150, 200, 150),
                             niveau_rect, 1)  # Bordure verte

            # Texte du niveau avec indication custom
            text = f"[CUSTOM] {niveau['nom']}"
            if niveau.get('config') and hasattr(niveau['config'], 'description') and niveau['config'].description:
                text += f" - {niveau['config'].description[:50]}..."

            # Texte vert foncé
            self.ui.draw_text(text, 60, y + 8, color=(0, 100, 0))

            # Stocker le rectangle pour la détection de clic
            if not hasattr(self, 'niveau_rects'):
                self.niveau_rects = {}
            self.niveau_rects[i] = niveau_rect

            y += 40

        # Indicateurs de scroll si nécessaire
        if len(self.niveaux_disponibles) > max_visible:
            total_pages = (len(self.niveaux_disponibles) -
                           1) // max_visible + 1
            current_page = start_index // max_visible + 1
            self.ui.draw_text(f"Page {current_page}/{total_pages} - Utilisez la molette pour défiler",
                              50, y + 20, color=(100, 100, 100))

        self.ui.draw_buttons()

    def _handle_niveau_selection_click(self, pos):
        """Gère les clics sur la liste de niveaux"""
        if hasattr(self, 'niveau_rects'):
            for index, rect in self.niveau_rects.items():
                if rect.collidepoint(pos):
                    niveau_info = self.niveaux_disponibles[index]

                    # Distinguer entre modification et jeu
                    if self.etat == "selection_niveau_custom":
                        # Mode jeu : lancer le niveau directement
                        self.lancer_niveau_custom(niveau_info)
                    else:
                        # Mode modification : charger pour édition
                        self.charger_niveau_pour_modification(niveau_info)
                    break

    def lancer_niveau_custom(self, niveau_info):
        """Lance un niveau custom pour y jouer"""
        try:
            config = niveau_info['config']

            # Pour les niveaux custom, permettre au joueur de choisir ses unités
            # Si des unités sont imposées, les utiliser, sinon lancer la sélection
            if config.unites_imposees:
                # Utiliser les unités imposées (extraire juste les classes)
                unites_joueur = [unite[0] for unite in config.unites_imposees]
                enable_placement = not config.placement_impose
            else:
                # Lancer la sélection d'unités selon le type de restriction
                if config.type_restriction.value == "faction_libre":
                    selector = UnitSelector(self.screen, "campagne_libre",
                                            cp_max=config.cp_disponible,
                                            max_units=config.max_unites,
                                            faction_unique=config.faction_unique_requise,
                                            faction_imposee=config.faction_imposee)
                elif config.type_restriction.value == "faction_unique":
                    selector = UnitSelector(self.screen, "campagne_faction",
                                            cp_max=config.cp_disponible,
                                            max_units=config.max_unites,
                                            faction_unique=True,
                                            faction_imposee=config.faction_imposee)
                else:
                    # Par défaut, sélection libre
                    selector = UnitSelector(self.screen, "campagne_libre",
                                            cp_max=config.cp_disponible,
                                            max_units=config.max_unites)

                unites_joueur = selector.run()

                if unites_joueur is None:  # Annulé
                    print("Sélection d'unités annulée")
                    return

                enable_placement = True

            # Créer le jeu avec la configuration du niveau

            jeu = Jeu(
                ia_strategy=ia.ia_tactique_avancee,
                screen=self.screen,
                initial_player_units=unites_joueur,
                initial_enemy_units=config.unites_ennemis,
                enable_placement=enable_placement,
                niveau_config=config
            )

            # Fermer le level builder et retourner le jeu
            self.running = False
            self.jeu_cree = jeu
            print(f"Lancement du niveau custom: {niveau_info['nom']}")

        except Exception as e:
            print(f"Erreur lors du lancement du niveau custom: {e}")

    def afficher_config_generale(self):
        """Affiche l'interface de configuration générale"""
        self._ensure_text_data_complete()
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Configuration du Niveau", 50)

        y = 120

        # Numéro du niveau (2 chiffres max)
        self.ui.draw_text("Numéro (00-99):", 50, y)
        numero_rect = self.ui.draw_input_field(
            200, y-5, 100, 30, self.text_data.get("numero", "01"), "numero")
        self.field_rects["numero"] = numero_rect
        y += 50

        # Nom du niveau
        self.ui.draw_text("Nom du niveau:", 50, y)
        nom_rect = self.ui.draw_input_field(
            200, y-5, 300, 30, self.text_data["nom"], "nom")
        self.field_rects["nom"] = nom_rect
        y += 50

        # Description
        self.ui.draw_text("Description:", 50, y)
        desc_rect = self.ui.draw_input_field(
            200, y-5, 400, 30, self.text_data["description"], "description")
        self.field_rects["description"] = desc_rect
        y += 50

        # Chapitre
        self.ui.draw_text("Chapitre:", 50, y)
        chapitre_rect = self.ui.draw_input_field(
            200, y-5, 300, 30, self.text_data["chapitre"], "chapitre")
        self.field_rects["chapitre"] = chapitre_rect

        self.ui.draw_buttons()

    def afficher_restrictions_config(self):
        """Affiche l'interface de configuration des restrictions"""
        self.screen.fill((255, 255, 255))
        self.ui.draw_title("Configuration des Restrictions", 50)

        y = 120

        # Type de restriction
        self.ui.draw_text("Type de restriction:", 50, y, color=(50, 50, 150))
        restriction_text = self.niveau_config.type_restriction.value.replace(
            "_", " ").title()
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

        # Faction unique (seulement pour faction libre)
        if self.niveau_config.type_restriction == TypeRestriction.FACTION_LIBRE:
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
        self.ui.draw_text("1. Sélectionnez les unités ennemies",
                          50, 120, color=(100, 100, 100))
        self.ui.draw_text("2. Placez-les sur la carte",
                          50, 140, color=(100, 100, 100))

        # Organiser l'affichage en deux colonnes pour éviter la superposition
        w = self.screen.get_width()
        col1_x = 50  # Colonne gauche : unités sélectionnées
        col2_x = w // 2 + 50  # Colonne droite : placement actuel
        start_y = 220

        # Afficher les unités sélectionnées (colonne gauche)
        if self.enemy_units_selected:
            self.ui.draw_text(
                f"Unités sélectionnées: {len(self.enemy_units_selected)}", col1_x, start_y, color=(0, 150, 0))

            y = start_y + 30
            # Afficher plus d'unités
            for _, cls in enumerate(self.enemy_units_selected[:12]):
                tmp = cls("ennemi", (0, 0))
                unit_text = f"- {tmp.get_nom()} ({tmp.get_faction()})"
                self.ui.draw_text(unit_text, col1_x + 20, y,
                                  font=self.ui.font_small)
                y += 25

            if len(self.enemy_units_selected) > 12:
                self.ui.draw_text(f"... et {len(self.enemy_units_selected) - 12} autres", col1_x + 20, y,
                                  font=self.ui.font_small, color=(100, 100, 100))
        else:
            self.ui.draw_text("Aucune unité sélectionnée",
                              col1_x, start_y, color=(200, 0, 0))

        # Afficher le placement actuel (colonne droite) si on est en mode modification
        if (hasattr(self, 'niveau_selectionne') and self.niveau_selectionne and
                self.niveau_config.unites_ennemis):

            self.ui.draw_text("Placement actuel:", col2_x,
                              start_y, color=(0, 0, 150))
            y_placement = start_y + 30

            # Afficher plus d'unités
            for _, (unit_class, position) in enumerate(self.niveau_config.unites_ennemis[:12]):
                tmp = unit_class("ennemi", position)
                placement_text = f"- {tmp.get_nom()} à {position}"
                self.ui.draw_text(placement_text, col2_x + 20, y_placement,
                                  font=self.ui.font_small, color=(50, 50, 150))
                y_placement += 25

            if len(self.niveau_config.unites_ennemis) > 12:
                self.ui.draw_text(f"... et {len(self.niveau_config.unites_ennemis) - 12} autres", col2_x + 20, y_placement,
                                  font=self.ui.font_small, color=(100, 100, 100))

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
            for _, nom_classe in enumerate(self.niveau_config.unites_debloquees):
                # Créer une instance temporaire pour obtenir le nom d'affichage
                try:
                    classe = next(
                        c for c in CLASSES_UNITES if c.__name__ == nom_classe)
                    instance_temp = classe(equipe=0, pos=(0, 0))
                    self.ui.draw_text(
                        f"• {instance_temp.nom} ({instance_temp.get_faction()})", 70, y, font=self.ui.font_small)
                    y += 25
                except:
                    self.ui.draw_text(
                        f"• {nom_classe} (erreur)", 70, y, font=self.ui.font_small, color=(200, 0, 0))
                    y += 25
        else:
            self.ui.draw_text("Aucune unité débloquée", 70, y,
                              font=self.ui.font_small, color=(100, 100, 100))
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
        self.ui.draw_text(
            "Choisissez l'unité à ajouter aux récompenses:", 50, 120, color=(50, 50, 150))

        # Les unités sont maintenant affichées via les boutons créés dans creer_boutons()
        # avec gestion automatique du scroll

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
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE)
                    self.ui.screen = self.screen
                    self.creer_boutons()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Gestion des boutons
                    if not self.ui.handle_button_events(event):
                        # Gestion des clics sur les champs de texte
                        if self.etat == "config_generale":
                            self.ui.handle_field_click(
                                event.pos, self.field_rects)
                        # Gestion des clics sur la liste de niveaux
                        elif self.etat == "selection_niveau":
                            self._handle_niveau_selection_click(event.pos)
                        elif self.etat == "selection_niveau_custom":
                            self._handle_niveau_selection_click(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if self.etat == "config_generale":
                        self._handle_text_input_with_validation(event)

                elif event.type == pygame.MOUSEWHEEL:
                    if self.etat == "selection_niveau" or self.etat == "selection_niveau_custom":
                        # Direction: 1 = scroll up (vers le haut), -1 = scroll down (vers le bas)
                        max_visible = 12
                        max_offset = max(
                            0, len(self.niveaux_disponibles) - max_visible)
                        self.scroll_offset = handle_scroll_events(
                            [event], self.scroll_offset, 1, max_offset)
                    elif self.etat == "selection_unite_deblocage":
                        if hasattr(self, 'unites_disponibles_pour_selection'):
                            self.scroll_offset = handle_scroll_events(
                                [event], self.scroll_offset, 1, self.scroll_max)

            # Affichage selon l'état
            if self.etat == "main_menu":
                self.afficher_main_menu()
            elif self.etat == "selection_niveau":
                self.afficher_selection_niveau()
            elif self.etat == "selection_niveau_custom":
                self.afficher_selection_niveau_custom()
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

        # Retourner le jeu créé si disponible
        if hasattr(self, 'jeu_cree'):
            return self.jeu_cree
        elif hasattr(self, 'test_game'):
            return self.test_game

        return None

    def toggle_faction_unique(self):
        """Toggle l'option faction unique requise"""
        self.niveau_config.faction_unique_requise = not self.niveau_config.faction_unique_requise

    def changer_faction_imposee(self):
        """Cycle entre les factions disponibles pour l'imposer"""
        factions_options = [""] + \
            self.factions_disponibles  # "" signifie "Aucune"

        if self.niveau_config.faction_imposee in factions_options:
            current_index = factions_options.index(
                self.niveau_config.faction_imposee)
        else:
            current_index = 0

        next_index = (current_index + 1) % len(factions_options)
        self.niveau_config.faction_imposee = factions_options[next_index]
