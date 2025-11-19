import pygame
import sys
from utils import Button, handle_scroll_events, wrap_text
from layout import recalculer_layout, hex_to_pixel, pixel_to_hex
import math

class PlacementPhase:
    def __init__(self, screen, selected_units, titre=None, player_spawn_zone=None, enemy_spawn_zone=None, existing_units=None):
        self.screen = screen
        self.selected_units = selected_units[:]  # copie
        self.font = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 40)
        
        # Configuration personnalisable
        self.titre = titre or "Placement des unités"
        
        # Zones de spawn personnalisables
        if player_spawn_zone:
            self._player_spawn_zone = player_spawn_zone
        else:
            self._player_spawn_zone = [-1, 0, 1]  # Par défaut : 3 lignes du haut
        
        if enemy_spawn_zone:
            self._enemy_spawn_zone = enemy_spawn_zone
        else:
            self._enemy_spawn_zone = [4, 5, 6]  # Par défaut : 3 lignes du bas
        
        self.q_range = range(-1, 7)
        self.r_range = range(-1, 7)
        
        # Unités placées sur le plateau: {(q,r): classe_unite}
        self.placed_units = {}
        
        # Compteurs d'unités disponibles: {classe: nombre}
        self.available_units = {}
        for cls in selected_units:
            self.available_units[cls] = self.available_units.get(cls, 0) + 1
        
        # Charger les unités existantes si fourni (pour modification)
        if existing_units:
            for unit_class, position in existing_units:
                # S'assurer que la position est un tuple (pas une liste)
                if isinstance(position, list):
                    position = tuple(position)
                
                self.placed_units[position] = unit_class
                # Décrémenter le compteur d'unités disponibles
                if unit_class in self.available_units and self.available_units[unit_class] > 0:
                    self.available_units[unit_class] -= 1
        
        # Système clic-clic
        self.selected_unit_to_place = None  # (classe, source_type, source_pos) ou None
        
        # Scroll pour le panneau d'unités
        self.scroll_y = 0
        self.scroll_speed = 40
        
        self.running = True
        self.cancelled = False
        self.validated = False
        
        # Layout
        recalculer_layout(self)
        
        # Boutons
        self._create_buttons()
    
    def _create_buttons(self):
        screen_w, screen_h = self.screen.get_size()
        self.retour_btn = Button(
            (20, screen_h-70, 160, 44),
            "Retour",
            self._cancel,
            self.font
        )
        self.valider_btn = Button(
            (screen_w-180, screen_h-70, 160, 44),
            "Valider",
            self._validate,
            self.font
        )
    
    def _cancel(self):
        self.cancelled = True
        self.running = False
    
    def _validate(self):
        # Vérifier que toutes les unités sont placées
        total_placed = len(self.placed_units)
        total_available = sum(self.available_units.values())
        
        if total_placed == len(self.selected_units) and total_available == 0:
            self.validated = True
            self.running = False
    
    def _is_player_spawn_zone(self, q, r):
        """Vérifie si la case est dans la zone de spawn joueur"""
        return r in self._player_spawn_zone
    
    def _is_enemy_spawn_zone(self, q, r):
        """Vérifie si la case est dans la zone de spawn ennemi"""
        return r in self._enemy_spawn_zone
    
    def _get_hex_color(self, q, r):
        """Retourne la couleur de l'hexagone selon la zone"""
        if self._is_player_spawn_zone(q, r):
            return (50, 200, 50, 100)  # Vert translucide
        elif self._is_enemy_spawn_zone(q, r):
            return (200, 50, 50, 100)  # Rouge translucide
        else:
            return (180, 180, 180)  # Gris neutre
    
    def _draw_hex(self, q, r, color, width=1):
        """Dessine un hexagone"""
        x, y = hex_to_pixel(self, q, r)
        pts = []
        for i in range(6):
            ang = math.pi / 3 * i + math.pi / 6
            px = x + self.taille_hex * math.cos(ang)
            py = y + self.taille_hex * math.sin(ang)
            pts.append((px, py))
        
        if len(color) == 4:  # Couleur avec alpha
            # Créer une surface temporaire pour la transparence
            temp_surf = pygame.Surface((self.taille_hex*2, self.taille_hex*2), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, color, 
                              [(px - x + self.taille_hex, py - y + self.taille_hex) for px, py in pts])
            self.screen.blit(temp_surf, (x - self.taille_hex, y - self.taille_hex))
        else:
            pygame.draw.polygon(self.screen, color, pts, width)
    
    def _get_unit_card_rect(self, index):
        """Retourne le rectangle de la carte d'unité à l'index donné"""
        sidebar_x = self.largeur - self.sidebar_w
        card_w = self.sidebar_w - 20
        card_h = 80
        margin = 10
        
        # Commencer plus bas pour laisser de la place au titre
        start_y = self.top_h + 60  # 60 au lieu de 20
        y = start_y + index * (card_h + margin) - self.scroll_y
        return pygame.Rect(sidebar_x + 10, y, card_w, card_h)
    
    def _calculate_scroll_limits(self):
        """Calcule les limites de scroll pour le panneau d'unités"""
        unique_classes = [cls for cls in set(self.selected_units) if self.available_units.get(cls, 0) > 0]
        if not unique_classes:
            return 0
        
        card_h = 80
        margin = 10
        start_y = self.top_h + 60
        total_height = len(unique_classes) * (card_h + margin)
        visible_height = self.hauteur - start_y - 80  # 80 pour les boutons en bas
        
        return max(0, total_height - visible_height)
    
    def _draw_unit_cards(self):
        """Dessine les cartes d'unités disponibles"""
        sidebar_x = self.largeur - self.sidebar_w
        
        # Fond du panneau
        pygame.draw.rect(self.screen, (240, 240, 240), 
                        pygame.Rect(sidebar_x, self.top_h, self.sidebar_w, self.hauteur - self.top_h))
        
        # Titre
        titre = self.font_big.render("Unités", True, (30, 30, 60))
        self.screen.blit(titre, (sidebar_x + 10, self.top_h + 10))
        
        # Zone de clipping pour les cartes
        clip_rect = pygame.Rect(sidebar_x, self.top_h + 50, self.sidebar_w, self.hauteur - self.top_h - 130)
        self.screen.set_clip(clip_rect)
        
        # Cartes d'unités
        unique_classes = list(set(self.selected_units))
        card_index = 0
        for cls in unique_classes:
            count = self.available_units.get(cls, 0)
            if count == 0:
                continue  # Ne pas afficher les unités épuisées
            
            rect = self._get_unit_card_rect(card_index)
            
            # Ne dessiner que si visible
            if rect.bottom >= self.top_h + 50 and rect.top <= self.hauteur - 130:
                # Vérifier si cette unité est sélectionnée
                is_selected = (self.selected_unit_to_place and 
                             self.selected_unit_to_place[0] == cls and 
                             self.selected_unit_to_place[1] == "list")
                
                # Fond de la carte
                if is_selected:
                    # Couleur de sélection
                    pygame.draw.rect(self.screen, (150, 150, 255), rect, border_radius=8)
                    pygame.draw.rect(self.screen, (0, 0, 255), rect, width=3, border_radius=8)
                else:
                    pygame.draw.rect(self.screen, (220, 220, 220), rect, border_radius=8)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=8)
                
                # Nom de l'unité
                tmp = cls("joueur", (0, 0))
                text_color = (255, 255, 255) if is_selected else (0, 0, 0)
                nom_txt = self.font.render(tmp.get_nom(), True, text_color)
                self.screen.blit(nom_txt, (rect.x + 10, rect.y + 10))
                
                # Compteur
                count_txt = self.font.render(f"x{count}", True, (255, 100, 100) if is_selected else (200, 0, 0))
                self.screen.blit(count_txt, (rect.right - 40, rect.y + 10))
                
                # Stats rapides
                stats_txt = self.font.render(f"PV:{tmp.get_pv()} DMG:{tmp.get_dmg()}", True, (200, 200, 255) if is_selected else (60, 60, 60))
                self.screen.blit(stats_txt, (rect.x + 10, rect.y + 35))
            
            card_index += 1
        
        # Retirer le clipping
        self.screen.set_clip(None)
    
    def _handle_mouse_click(self, pos):
        """Gère le système clic-clic pour sélection et placement"""
        mx, my = pos
        
        # Si aucune unité sélectionnée, essayer de sélectionner une unité
        if not self.selected_unit_to_place:
            # Vérifier si on clique sur une unité placée
            for (q, r), cls in self.placed_units.items():
                x, y = hex_to_pixel(self, q, r)
                if (mx - x)**2 + (my - y)**2 <= self.unit_radius**2:
                    # Sélectionner l'unité du plateau
                    self.selected_unit_to_place = (cls, "board", (q, r))
                    # Retirer temporairement l'unité du plateau
                    del self.placed_units[(q, r)]
                    return
            
            # Vérifier si on clique sur une carte d'unité
            unique_classes = list(set(self.selected_units))
            card_index = 0
            for cls in unique_classes:
                count = self.available_units.get(cls, 0)
                if count == 0:
                    continue
                
                rect = self._get_unit_card_rect(card_index)
                if rect.collidepoint(mx, my):
                    # Sélectionner l'unité de la liste
                    self.selected_unit_to_place = (cls, "list", card_index)
                    self.available_units[cls] -= 1  # Décrémenter immédiatement le compteur
                    return
                
                card_index += 1
        
        else:
            # Une unité est sélectionnée, essayer de la placer
            cls, source_type, source_pos = self.selected_unit_to_place
            
            # Trouver la case hexagonale la plus proche
            best_pos = None
            best_dist = float('inf')
            
            for q in self.q_range:
                for r in self.r_range:
                    x, y = hex_to_pixel(self, q, r)
                    dist = (mx - x)**2 + (my - y)**2
                    if dist < best_dist and dist <= (self.taille_hex * 1.5)**2:
                        best_dist = dist
                        best_pos = (q, r)
            
            # Vérifier si on peut placer l'unité
            can_place = (
                best_pos is not None and
                best_pos not in self.placed_units and
                self._is_player_spawn_zone(*best_pos)  # Seulement en zone joueur
            )
            
            if can_place:
                # Placer l'unité
                self.placed_units[best_pos] = cls
                
                # Si l'unité venait de la liste et qu'il en reste, en resélectionner une automatiquement
                if source_type == "list" and self.available_units.get(cls, 0) > 0:
                    self.selected_unit_to_place = (cls, "list", source_pos)
                    self.available_units[cls] -= 1
                else:
                    self.selected_unit_to_place = None
            else:
                # Clic sur une zone invalide
                # Vérifier si on clique sur une autre unité pour changer la sélection
                clicked_on_unit = False
                
                # Vérifier les unités déjà placées
                for (q, r), other_cls in self.placed_units.items():
                    x, y = hex_to_pixel(self, q, r)
                    if (mx - x)**2 + (my - y)**2 <= self.unit_radius**2:
                        # Remettre l'unité actuelle en arrière si possible
                        if source_type == "board":
                            self.placed_units[source_pos] = cls
                        elif source_type == "list":
                            # Si l'unité venait de la liste, on réincrémente son compteur
                            self.available_units[cls] += 1
                        
                        # Sélectionner la nouvelle unité
                        self.selected_unit_to_place = (other_cls, "board", (q, r))
                        del self.placed_units[(q, r)]
                        clicked_on_unit = True
                        return
                
                # Vérifier les cartes d'unités et la zone de menu
                if not clicked_on_unit:
                    # Vérifier si on est dans la zone du menu (panneau de droite)
                    sidebar_x = self.largeur - self.sidebar_w
                    if mx >= sidebar_x:
                        # Si on clique dans le menu avec une unité du plateau sélectionnée,
                        # on la remet dans la liste au lieu de la remettre sur le plateau
                        if source_type == "board":
                            self.available_units[cls] = self.available_units.get(cls, 0) + 1
                            self.selected_unit_to_place = None
                            return
                    
                    # Gestion normale des clics sur les cartes d'unités
                    unique_classes = list(set(self.selected_units))
                    card_index = 0
                    for other_cls in unique_classes:
                        count = self.available_units.get(other_cls, 0)
                        if count == 0:
                            continue
                        
                        rect = self._get_unit_card_rect(card_index)
                        if rect.collidepoint(mx, my):
                            # Remettre l'unité actuelle si possible
                            if source_type == "board":
                                self.available_units[cls] = self.available_units.get(cls, 0) + 1
                            elif source_type == "list":
                                # Si l'unité venait de la liste, on réincrémente son compteur
                                self.available_units[cls] += 1
                            
                            # Sélectionner la nouvelle unité
                            self.selected_unit_to_place = (other_cls, "list", card_index)
                            self.available_units[other_cls] -= 1
                            clicked_on_unit = True
                            return
                        
                        card_index += 1
                
                    # Si on n'a cliqué sur rien de valide, annuler la sélection
                if not clicked_on_unit:
                    # Remettre l'unité à sa place d'origine
                    if source_type == "board":
                        self.placed_units[source_pos] = cls
                    elif source_type == "list":
                        # Si l'unité venait de la liste, on réincrémente son compteur
                        self.available_units[cls] += 1
                    self.selected_unit_to_place = None
    
    def _handle_right_click(self):
        """Gère le clic droit pour déselectionner l'unité ou la remettre dans la liste"""
        if self.selected_unit_to_place:
            cls, source_type, source_pos = self.selected_unit_to_place
            if source_type == "board":
                # Au lieu de remettre l'unité sur le plateau, on l'ajoute à la liste
                self.available_units[cls] = self.available_units.get(cls, 0) + 1
            elif source_type == "list":
                # Si l'unité venait de la liste, on réincrémente son compteur
                self.available_units[cls] += 1
            self.selected_unit_to_place = None
    
    def run(self):
        """Lance la phase de placement"""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    recalculer_layout(self)
                    self._create_buttons()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        self._handle_mouse_click(event.pos)
                        self.retour_btn.handle_event(event)
                        self.valider_btn.handle_event(event)
                    elif event.button == 3:  # Clic droit
                        self._handle_right_click()
            # Gestion du scroll du panneau d'unités (utilitaire)
            mx, my = pygame.mouse.get_pos()
            sidebar_x = self.largeur - self.sidebar_w
            if mx >= sidebar_x:
                max_scroll = self._calculate_scroll_limits()
                self.scroll_y = handle_scroll_events(events, self.scroll_y, self.scroll_speed, max_scroll)
            
            # Dessin
            self.screen.fill((255, 255, 255))
            
            # Titre principal
            titre_principal = self.font_big.render(self.titre, True, (30, 30, 60))
            self.screen.blit(titre_principal, (20, 20))
            
            # Grille hexagonale
            for q in self.q_range:
                for r in self.r_range:
                    color = self._get_hex_color(q, r)
                    if len(color) == 4:
                        self._draw_hex(q, r, color)
                    else:
                        self._draw_hex(q, r, color, 2)
            
            # Unités placées
            for (q, r), cls in self.placed_units.items():
                x, y = hex_to_pixel(self, q, r)
                
                # Vérifier si cette unité est sélectionnée (mais pas encore re-placée)
                is_selected = (self.selected_unit_to_place and 
                             self.selected_unit_to_place[0] == cls and 
                             self.selected_unit_to_place[1] == "board" and
                             self.selected_unit_to_place[2] == (q, r))
                
                # Cette condition ne devrait jamais être vraie car on retire l'unité du plateau
                # quand on la sélectionne, mais on garde la logique par sécurité
                if not is_selected:
                    pygame.draw.circle(self.screen, (50, 200, 50), (int(x), int(y)), self.unit_radius)
                    
                    # Nom de l'unité
                    tmp = cls("joueur", (0, 0))
                    name_txt = self.font.render(tmp.get_nom(), True, (0, 0, 0))
                    self.screen.blit(name_txt, (x - name_txt.get_width()//2, y - self.unit_radius - 20))
            
            # Panneau latéral
            self._draw_unit_cards()
            
            # Unité sélectionnée pour placement
            if self.selected_unit_to_place:
                mx, my = pygame.mouse.get_pos()
                cls = self.selected_unit_to_place[0]
                
                # Nom de l'unité sélectionnée seulement
                tmp = cls("joueur", (0, 0))
                name_txt = self.font.render(f"Placement: {tmp.get_nom()}", True, (100, 100, 250))
                self.screen.blit(name_txt, (mx - name_txt.get_width()//2, my - 25))
            
            # Boutons
            self.retour_btn.draw(self.screen)
            
            # Bouton valider - actif seulement si toutes les unités sont placées
            total_available = sum(self.available_units.values())
            if total_available == 0:
                self.valider_btn.base_color = (100, 200, 100)
                self.valider_btn.text_color = (255, 255, 255)
            else:
                self.valider_btn.base_color = (150, 150, 150)
                self.valider_btn.text_color = (100, 100, 100)
            self.valider_btn.draw(self.screen)
            
            # Instructions
            if self.selected_unit_to_place:
                cls = self.selected_unit_to_place[0]
                tmp = cls("joueur", (0, 0))
                instruction = self.font.render(f"Cliquez pour placer: {tmp.get_nom()}", True, (0, 0, 200))
                self.screen.blit(instruction, (20, 60))
            elif total_available > 0:
                instruction = self.font.render(f"Cliquez sur une unité, puis sur sa position ({total_available} restantes)", True, (200, 0, 0))
                self.screen.blit(instruction, (20, 60))
            
            pygame.display.flip()
        
        if self.validated:
            return [(cls, pos) for pos, cls in self.placed_units.items()]
        else:
            return None  # Annulé

def auto_place_enemy_units(enemy_classes, q_range=None, r_range=None):
    """Place automatiquement les unités ennemies dans leur zone de spawn"""
    if q_range is None:
        q_range = range(-1, 7)
    if r_range is None:
        r_range = range(-1, 7)
    
    # Positions disponibles en zone ennemie (3 lignes du bas)
    enemy_positions = []
    for r in [4, 5, 6]:
        for q in q_range:
            enemy_positions.append((q, r))
    
    placed_units = []
    for i, cls in enumerate(enemy_classes):
        if i < len(enemy_positions):
            placed_units.append((cls, enemy_positions[i]))
    
    return placed_units