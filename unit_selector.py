import pygame
import sys
from utils import Button, handle_scroll_events, draw_bandeau
import unites
import sauvegarde
from competences import COMPETENCES
from faction_colors import get_faction_color

UNIT_MAX = 24

class UnitSelector:
    def __init__(self, screen, mode, **kwargs):
        self.screen = screen
        self.mode = mode  # "hexarene", "campagne", "versus", "mixte"
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36)
        
        # Charger les données AVANT de configurer le mode
        self.data = sauvegarde.charger()
        
        # Configuration selon le mode
        self.config = self._get_mode_config(**kwargs)
        
        # Initialiser avec les unités pré-sélectionnées si fournies
        preselected_units = kwargs.get('preselected_units', [])
        self.selected_units = preselected_units[:]  # Copie de la liste
        
        # Variables de l'interface
        self.running = True
        self.cancelled = False
        self.scroll_y = 0
        self.scroll_speed = 40
        self.max_scroll = 0
        
        # Pour stocker les boutons dynamiques
        self.unit_buttons = []
        
        # Créer les boutons
        self.creer_boutons()
    
    def _get_mode_config(self, **kwargs):
        """Configure les paramètres selon le mode de jeu"""
        if self.mode == "hexarene":
            return {
                "titre": "HexArène - Sélection des unités",
                "max_units": 14,
                "use_cp": True,
                "cp_disponible": self.data.get("cp", 5),
                "faction_unique": True,
                "unites_disponibles": self._get_owned_units(),
                "background": (250, 245, 230)
            }
        
        elif self.mode == "campagne":
            # Les unités sont prédéfinies en campagne
            return {
                "titre": "Campagne - Unités prédéfinies",
                "max_units": len(kwargs.get("unites_predefinies", [])),
                "use_cp": False,
                "unites_predefinies": kwargs.get("unites_predefinies", []),
                "background": (230, 250, 240)
            }
        
        elif self.mode == "versus":
            joueur = kwargs.get("joueur", 1)
            return {
                "titre": f"Joueur {joueur} - Sélection des unités",
                "max_units": 10,
                "use_cp": True,
                "cp_disponible": self.data.get("cp", 5),
                "faction_unique": False,  # Toutes factions autorisées
                "unites_disponibles": self._get_owned_units(),
                "background": (240, 240, 250)
            }
        
        elif self.mode == "mixte":
            return {
                "titre": "Mode Mixte - Sélection des unités",
                "max_units": 12,
                "use_cp": True,
                "cp_disponible": self.data.get("cp", 5),
                "faction_unique": False,
                "unites_disponibles": self._get_owned_units(),
                "background": (250, 250, 240)
            }
        
        elif self.mode == "builder_enemy":
            return {
                "titre": "Level Builder - Sélection des Ennemis",
                "max_units": UNIT_MAX,  # Limite de UNIT_MAX unités
                "use_cp": False,   # Pas de contrainte CP
                "cp_disponible": 999,
                "faction_unique": False,  # Toutes factions autorisées
                "unites_disponibles": self._get_all_units(),  # Toutes les unités
                "background": (250, 230, 230)  # Rouge clair pour les ennemis
            }
        
        elif self.mode == "campagne_libre":
            return {
                "titre": "Campagne - Sélection Libre",
                "max_units": kwargs.get("max_units", 14),
                "use_cp": True,
                "cp_disponible": kwargs.get("cp_max", 5),
                "faction_unique": False,
                "faction_imposee": kwargs.get("faction_imposee", ""),
                "unites_disponibles": self._get_units_for_faction_imposee(kwargs.get("faction_imposee", "")),
                "background": (230, 250, 240)
            }
        
        elif self.mode == "campagne_faction":
            return {
                "titre": "Campagne - Faction Unique",
                "max_units": kwargs.get("max_units", 14),
                "use_cp": True,
                "cp_disponible": kwargs.get("cp_max", 5),
                "faction_unique": True,
                "faction_imposee": kwargs.get("faction_imposee", ""),
                "unites_disponibles": self._get_units_for_faction_imposee(kwargs.get("faction_imposee", "")),
                "background": (230, 250, 240)
            }
        
        elif self.mode == "campagne_definies":
            return {
                "titre": "Campagne - Factions Définies",
                "max_units": kwargs.get("max_units", 14),
                "use_cp": True,
                "cp_disponible": kwargs.get("cp_max", 5),
                "faction_unique": kwargs.get("faction_unique", False),
                "faction_imposee": kwargs.get("faction_imposee", ""),
                "factions_autorisees": kwargs.get("factions_autorisees", []),
                "unites_disponibles": self._get_units_combined_restrictions(
                    kwargs.get("factions_autorisees", []),
                    kwargs.get("faction_imposee", "")
                ),
                "background": (230, 250, 240)
            }
        
    
    def _get_all_units(self):
        """Retourne toutes les classes d'unités disponibles dans le jeu"""
        # Retourner toutes les unités du jeu, pas seulement celles possédées
        return unites.CLASSES_UNITES
    
    def _get_owned_units(self):
        """Retourne les classes d'unités possédées par le joueur"""
        owned_names = self.data.get("unites", [])
        available_classes = []
        
        for nom in owned_names:
            for classe in unites.CLASSES_UNITES:
                tmp_instance = classe("joueur", (0,0))
                if tmp_instance.get_nom() == nom:
                    available_classes.append(classe)
                    break
        
        return available_classes
    
    def _get_faction_filtered_units(self, factions_autorisees):
        """Retourne les unités possédées filtrées par factions autorisées"""
        if not factions_autorisees:
            return self._get_owned_units()
        
        owned_units = self._get_owned_units()
        filtered_units = []
        
        for cls in owned_units:
            tmp_instance = cls("joueur", (0,0))
            if tmp_instance.faction in factions_autorisees:
                filtered_units.append(cls)
        
        return filtered_units
    
    def _get_units_for_faction_imposee(self, faction_imposee):
        """Retourne les unités selon la faction imposée"""
        if not faction_imposee:
            # Aucune faction imposée, retourner toutes les unités possédées
            return self._get_owned_units()
        
        # Faction imposée, filtrer par cette faction uniquement
        owned_units = self._get_owned_units()
        filtered_units = []
        
        for cls in owned_units:
            tmp_instance = cls("joueur", (0,0))
            if tmp_instance.faction == faction_imposee:
                filtered_units.append(cls)
        
        return filtered_units
    
    def _get_units_combined_restrictions(self, factions_autorisees, faction_imposee):
        """Retourne les unités avec les restrictions combinées (factions autorisées ET faction imposée)"""
        if faction_imposee:
            # Si une faction est imposée, elle prend la priorité
            return self._get_units_for_faction_imposee(faction_imposee)
        
        # Sinon, utiliser les factions autorisées
        return self._get_faction_filtered_units(factions_autorisees)
    
    def _calculate_cp_cost(self, unit_list):
        """Calcule le coût en CP d'une liste d'unités"""
        total = 0
        for cls in unit_list:
            tmp = cls("joueur", (0,0))
            total += tmp.tier
        return total
    
    def _get_faction(self, cls):
        """Retourne la faction d'une classe d'unité"""
        tmp = cls("joueur", (0,0))
        return tmp.faction
    
    def _can_add_unit(self, cls):
        """Vérifie si on peut ajouter cette unité"""
        config = self.config
        
        # Vérifier le nombre max
        if len(self.selected_units) >= config["max_units"]:
            return False
        
        # Vérifier le CP
        if config.get("use_cp", False):
            tmp = cls("joueur", (0,0))
            cost = tmp.tier
            current_cost = self._calculate_cp_cost(self.selected_units)
            if current_cost + cost > config["cp_disponible"]:
                return False
        
        # Vérifier la faction unique
        if config.get("faction_unique", False) and self.selected_units:
            current_faction = self._get_faction(self.selected_units[0])
            if self._get_faction(cls) != current_faction:
                return False
        
        # Vérifier la faction imposée
        faction_imposee = config.get("faction_imposee", "")
        if faction_imposee and self._get_faction(cls) != faction_imposee:
            return False
        
        return True
    
    def creer_boutons(self):
        screen_w, screen_h = self.screen.get_size()
        self.retour_btn = Button(
            (20, screen_h - 70, 160, 44),
            "Retour",
            self.retour,
            self.font
        )
        self.valider_btn = Button(
            (screen_w - 180, screen_h - 70, 160, 44),
            "Valider",
            self.valider,
            self.font
        )
    
    def retour(self):
        self.cancelled = True
        self.running = False
    
    def valider(self):
        if self.mode == "campagne":
            # En campagne, pas de validation nécessaire
            self.running = False
        elif len(self.selected_units) > 0:
            self.running = False
    
    def _grid_specs(self):
        screen_w, screen_h = self.screen.get_size()
        margin = max(20, screen_w // 40)
        cols = 3
        card_w = (screen_w - margin * (cols + 1)) // cols
        if card_w < 260:
            cols = 2
            card_w = (screen_w - margin * (cols + 1)) // cols
        if card_w < 220:
            cols = 1
            card_w = (screen_w - margin * (cols + 1)) // cols
        card_w = max(200, card_w)
        start_y = max(100, int(0.12 * screen_h))
        return screen_w, screen_h, margin, cols, card_w, start_y
    
    def wrap_text(self, text, max_width):
        if not text:
            return [""]
        words = text.split()
        lines, cur = [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if self.font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines or [""]
    
    def _calculer_hauteur_max_carte_predefinie(self, card_w):
        """Calcule la hauteur maximale pour les unités prédéfinies."""
        max_height = 0
        
        for cls, pos in self.config["unites_predefinies"]:
            tmp = cls("joueur", pos)
            comp = tmp.get_competence()
            comp_desc = "" if not comp else COMPETENCES.get(comp, "")
            
            base_lines = [
                f"{tmp.get_nom()}",
                f"{tmp.faction}",
                f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                f"Attaques: {tmp.attaque_max} | Portée: {tmp.portee}",
                f"Tier: {tmp.get_tier()}",
                f"Compétence: {'Aucune' if not comp else comp}",
            ]
            desc_lines = self.wrap_text(comp_desc, card_w - 20)
            card_h = 20 + len(base_lines) * 30 + len(desc_lines) * 26 + 20
            
            max_height = max(max_height, card_h)
        
        return max_height
    
    def _calculer_hauteur_max_carte_disponible(self, card_w):
        """Calcule la hauteur maximale pour les unités disponibles."""
        max_height = 0
        
        for cls in self.config["unites_disponibles"]:
            tmp = cls("joueur", (0,0))
            comp = tmp.get_competence()
            comp_desc = "" if not comp else COMPETENCES.get(comp, "")
            
            base_lines = [
                f"{tmp.get_nom()}",
                f"{tmp.faction}",
                f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                f"Attaques: {tmp.attaque_max} | Portée: {tmp.portee}",
                f"Tier: {tmp.get_tier()} (CP: {tmp.tier})",
                f"Compétence: {'Aucune' if not comp else comp}",
            ]
            desc_lines = self.wrap_text(comp_desc, card_w - 20)
            card_h = 20 + len(base_lines) * 30 + len(desc_lines) * 26 + 60
            
            max_height = max(max_height, card_h)
        
        return max_height
    
    def afficher_campagne(self):
        """Affichage spécial pour le mode campagne (unités prédéfinies)"""
        self.screen.fill(self.config["background"])
        screen_w, screen_h, margin, cols, card_w, start_y = self._grid_specs()
        
        # Calculer la hauteur uniforme pour toutes les cartes
        card_h = self._calculer_hauteur_max_carte_predefinie(card_w)
        
        titre = self.title_font.render(self.config["titre"], True, (30, 30, 60))
        self.screen.blit(titre, (margin, 30))
        
        info = self.font.render("Unités prédéfinies pour ce niveau", True, (100, 100, 100))
        self.screen.blit(info, (margin, 70))
        
        x, y, col = margin, start_y - self.scroll_y, 0
        
        for cls, pos in self.config["unites_predefinies"]:
            tmp = cls("joueur", pos)
            comp = tmp.get_competence()
            comp_desc = "" if not comp else COMPETENCES.get(comp, "")
            
            base_lines = [
                f"{tmp.get_nom()}",
                f"{tmp.faction}",
                f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                f"Attaques: {tmp.attaque_max} | Portée: {tmp.portee}",
                f"Tier: {tmp.get_tier()}",
                f"Compétence: {'Aucune' if not comp else comp}",
            ]
            desc_lines = self.wrap_text(comp_desc, card_w - 20)
            
            rect = pygame.Rect(x, y, card_w, card_h)
            faction_color = get_faction_color(tmp.faction)
            pygame.draw.rect(self.screen, faction_color, rect, border_radius=12)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=12)
            
            for i, l in enumerate(base_lines):
                if i == 0:  # Nom
                    txt = self.font.render(l, True, (20, 20, 120))
                elif i == 1:  # Faction
                    txt = self.font.render(l, True, (120, 20, 20))
                else:
                    txt = self.font.render(l, True, (0, 0, 0))
                self.screen.blit(txt, (x + 10, y + 12 + i * 30))
            
            y_text = y + 12 + len(base_lines) * 30 + 6
            for line in desc_lines:
                txt = self.font.render(line, True, (20, 20, 20))
                self.screen.blit(txt, (x + 10, y_text))
                y_text += 26
            
            x += card_w + margin
            col += 1
            if col >= cols:
                col = 0
                x = margin
                y += card_h + margin
    
    def afficher_selection(self):
        """Affichage pour les modes avec sélection d'unités"""
        self.screen.fill(self.config["background"])
        screen_w, screen_h, margin, cols, card_w, start_y = self._grid_specs()
        
        # Calculer la hauteur uniforme pour toutes les cartes
        card_h = self._calculer_hauteur_max_carte_disponible(card_w)
        
        # Initialiser les variables du bandeau pour plus tard
        bandeau_h = 60
        margin = 20
        pa_text = ""
        
        # Calculer les limites de scroll
        total_height = start_y
        x, y, col = margin, start_y, 0
        for cls in self.config["unites_disponibles"]:
            total_height = max(total_height, y + card_h)
            col += 1
            if col >= cols:
                col = 0
                x = margin
                y += card_h + margin
            else:
                x += card_w + margin
        self.max_scroll = max(0, total_height - (screen_h - start_y - 40))
        
        # Réinitialiser les boutons d'unités
        self.unit_buttons = []
        
        # Affichage des cartes d'unités
        x, y, col = margin, start_y - self.scroll_y, 0
        for cls in self.config["unites_disponibles"]:
            tmp = cls("joueur", (0,0))
            comp = tmp.get_competence()
            comp_nom = "Aucune" if not comp else comp
            comp_desc = "" if not comp else COMPETENCES.get(comp, "")
            
            can_add = self._can_add_unit(cls)
            count_selected = self.selected_units.count(cls)
            
            base_lines = [
                f"{tmp.get_nom()}",
                f"{tmp.faction}",
                f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                f"Attaques: {tmp.attaque_max} | Portée: {tmp.portee}",
                f"Tier: {tmp.get_tier()} (CP: {tmp.tier})",
                f"Compétence: {comp_nom}",
            ]
            desc_lines = self.wrap_text(comp_desc, card_w - 20)
            
            rect = pygame.Rect(x, y, card_w, card_h)
            
            # Couleur de fond selon la disponibilité et la faction
            faction_color = get_faction_color(tmp.faction)
            if can_add or count_selected > 0:
                bg_color = faction_color
            else:
                # Version plus sombre/grisée pour les unités non disponibles
                bg_color = tuple(int(c * 0.7) for c in faction_color)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=12)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=12)
            
            # Affichage du texte
            for i, l in enumerate(base_lines):
                if i == 0:  # Nom
                    txt = self.font.render(l, True, (20, 20, 120))
                elif i == 1:  # Faction
                    txt = self.font.render(l, True, (120, 20, 20))
                else:
                    txt = self.font.render(l, True, (0, 0, 0))
                self.screen.blit(txt, (x + 10, y + 12 + i * 30))
            
            y_text = y + 12 + len(base_lines) * 30 + 6
            for line in desc_lines:
                txt = self.font.render(line, True, (20, 20, 20))
                self.screen.blit(txt, (x + 10, y_text))
                y_text += 26
            
            # Compteur d'unités sélectionnées
            if count_selected > 0:
                count_txt = self.font.render(f"x{count_selected}", True, (200, 0, 0))
                self.screen.blit(count_txt, (rect.right - 40, rect.y + 10))
            
            # Boutons d'ajout/suppression (seulement si visible à l'écran)
            btn_y = y + card_h - 50
            if btn_y >= start_y - 50 and btn_y <= screen_h - 100:  # Vérifier si visible
                
                # Si l'unité est déjà sélectionnée, afficher les deux boutons côte à côte
                if count_selected > 0:
                    # Bouton Retirer (à gauche)
                    btn_retirer_rect = pygame.Rect(x + 10, btn_y, (card_w - 30) // 2, 40)
                    btn_retirer = Button(btn_retirer_rect, "Retirer", lambda c=cls: self.retirer_unite(c), self.font, base_color=(200, 100, 100))
                    self.unit_buttons.append(btn_retirer)
                    btn_retirer.draw(self.screen)
                    
                    # Bouton Ajouter (à droite) - si on peut encore en ajouter
                    if can_add:
                        btn_ajouter_rect = pygame.Rect(x + 10 + (card_w - 30) // 2 + 10, btn_y, (card_w - 30) // 2, 40)
                        btn_ajouter = Button(btn_ajouter_rect, "Ajouter", lambda c=cls: self.ajouter_unite(c), self.font, base_color=(100, 200, 100))
                        self.unit_buttons.append(btn_ajouter)
                        btn_ajouter.draw(self.screen)
                    else:
                        # Bouton grisé avec message d'erreur (à droite)
                        btn_ajouter_rect = pygame.Rect(x + 10 + (card_w - 30) // 2 + 10, btn_y, (card_w - 30) // 2, 40)
                        
                        # Déterminer le message d'erreur approprié
                        if len(self.selected_units) >= self.config["max_units"]:
                            btn_text = "Max atteint"
                        elif self.config.get("use_cp", False):
                            tmp = cls("joueur", (0,0))
                            cost = tmp.tier
                            current_cost = self._calculate_cp_cost(self.selected_units)
                            if current_cost + cost > self.config["cp_disponible"]:
                                btn_text = "CP insuffisant"
                            else:
                                btn_text = "Faction différente"
                        elif self.config.get("faction_unique", False) and self.selected_units:
                            current_faction = self._get_faction(self.selected_units[0])
                            if self._get_faction(cls) != current_faction:
                                btn_text = "Faction différente"
                            else:
                                btn_text = "Non disponible"
                        else:
                            btn_text = "Non disponible"
                        
                        btn_grise = Button(btn_ajouter_rect, btn_text, lambda: None, self.font, base_color=(150, 150, 150))
                        btn_grise.draw(self.screen)
                
                # Si l'unité n'est pas encore sélectionnée
                else:
                    # Bouton d'ajout (pleine largeur)
                    if can_add:
                        btn_rect = pygame.Rect(x + 10, btn_y, card_w - 20, 40)
                        btn_color = (100, 200, 100)
                        btn_text = "Ajouter"
                        # Créer un bouton fonctionnel
                        btn = Button(btn_rect, btn_text, lambda c=cls: self.ajouter_unite(c), self.font, base_color=btn_color)
                        self.unit_buttons.append(btn)
                        btn.draw(self.screen)
                    
                    # Bouton grisé avec message d'erreur (pleine largeur)
                    else:
                        btn_rect = pygame.Rect(x + 10, btn_y, card_w - 20, 40)
                        btn_color = (150, 150, 150)
                        
                        # Déterminer le message d'erreur approprié
                        if len(self.selected_units) >= self.config["max_units"]:
                            btn_text = "Max atteint"
                        elif self.config.get("use_cp", False):
                            tmp = cls("joueur", (0,0))
                            cost = tmp.tier
                            current_cost = self._calculate_cp_cost(self.selected_units)
                            if current_cost + cost > self.config["cp_disponible"]:
                                btn_text = "CP insuffisant"
                            else:
                                btn_text = "Faction différente"
                        elif self.config.get("faction_unique", False) and self.selected_units:
                            current_faction = self._get_faction(self.selected_units[0])
                            if self._get_faction(cls) != current_faction:
                                btn_text = "Faction différente"
                            else:
                                btn_text = "Non disponible"
                        else:
                            btn_text = "Non disponible"
                        
                        # Bouton non-fonctionnel (juste pour l'affichage)
                        btn = Button(btn_rect, btn_text, lambda: None, self.font, base_color=btn_color)
                        btn.draw(self.screen)
            
            x += card_w + margin
            col += 1
            if col >= cols:
                col = 0
                x = margin
                y += card_h + margin
    
    def _get_faction_units(self, faction_requise=None):
        """Retourne les unités d'une faction spécifique ou toutes si aucune faction"""
        if faction_requise is None:
            return self._get_owned_units()
        
        # Filtrer par faction
        owned_units = self._get_owned_units()
        faction_units = []
        
        for cls in owned_units:
            tmp = cls("joueur", (0, 0))
            if tmp.faction == faction_requise:
                faction_units.append(cls)
        
        return faction_units
    
    def ajouter_unite(self, cls):
        """Ajoute une unité à la sélection"""
        if self._can_add_unit(cls):
            self.selected_units.append(cls)
            # Debug supprimé pour éviter le spam dans les logs
    
    def retirer_unite(self, cls):
        """Retire une unité de la sélection"""
        if cls in self.selected_units:
            self.selected_units.remove(cls)
            # Debug supprimé pour éviter le spam dans les logs
    
    def run(self):
        """Lance le sélecteur d'unités"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.creer_boutons()
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.retour_btn.handle_event(event)
                    self.valider_btn.handle_event(event)
                    
                    # GESTION DES BOUTONS D'UNITÉS
                    for btn in self.unit_buttons:
                        btn.handle_event(event)
                
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y = handle_scroll_events([event], self.scroll_y, self.scroll_speed, self.max_scroll)
            
            # Affichage selon le mode
            if self.mode == "campagne":
                self.afficher_campagne()
            else:
                self.afficher_selection()
            
            # Boutons
            self.retour_btn.draw(self.screen)
            
            # Bouton valider selon le mode
            if self.mode == "campagne":
                self.valider_btn.base_color = (100, 200, 100)
                self.valider_btn.text_color = (255, 255, 255)
            elif len(self.selected_units) > 0:
                self.valider_btn.base_color = (100, 200, 100)
                self.valider_btn.text_color = (255, 255, 255)
            else:
                self.valider_btn.base_color = (150, 150, 150)
                self.valider_btn.text_color = (100, 100, 100)
            
            self.valider_btn.draw(self.screen)
            
            # Afficher le bandeau en dernier pour qu'il soit au premier plan
            screen_w = self.screen.get_width()
            bandeau_h = 60
            margin = 20
            pa_text = ""
            
            # Ajouter les informations de CP
            if self.config.get("use_cp", False):
                cp_used = self._calculate_cp_cost(self.selected_units)
                pa_text = f"CP: {cp_used}/{self.config['cp_disponible']}"
            
            # Ajouter le compte d'unités
            if pa_text:
                pa_text += " | "
            pa_text += f"Unités: {len(self.selected_units)}/{self.config['max_units']}"
            
            # Ajouter la restriction si elle existe
            if self.config.get("restriction_type"):
                pa_text += f" | Restriction: {self.config['restriction_type'].name}"
            
            # Dessiner le bandeau en dernier
            draw_bandeau(self.screen, screen_w, bandeau_h, margin, self.font, self.title_font, pa_text, titre=self.config["titre"])
            
            pygame.display.flip()
        
        if self.cancelled:
            return None
        elif self.mode == "campagne":
            return self.config["unites_predefinies"]
        elif self.mode in ["campagne_libre", "campagne_faction", "campagne_definies"]:
            return self.selected_units
        else:
            return self.selected_units