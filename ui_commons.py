"""
Composants UI communs pour éviter la duplication de code
"""

import pygame
from typing import Callable, Optional, List, Tuple, Any
from utils import Button


class UIManager:
    """Gestionnaire d'interface utilisateur réutilisable"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 20)
        self.title_font = pygame.font.SysFont(None, 36)
        
        self.boutons: List[Button] = []
        self.champ_actif: Optional[str] = None
    
    def clear_buttons(self):
        """Efface tous les boutons"""
        self.boutons = []
    
    def add_button(self, rect: Tuple[int, int, int, int], text: str, action: Callable, 
                   font: Optional[pygame.font.Font] = None, color=None, hover_color=None) -> Button:
        """Ajoute un bouton et le retourne"""
        if font is None:
            font = self.font
        
        # Paramètres de couleur optionnels
        kwargs = {}
        if color is not None:
            kwargs['base_color'] = color
        if hover_color is not None:
            kwargs['hover_color'] = hover_color
            
        btn = Button(rect, text, action, font, **kwargs)
        self.boutons.append(btn)
        return btn
    
    def add_navigation_buttons(self, y_bottom: int, actions: List[Tuple[str, Callable]]):
        """Ajoute des boutons de navigation en bas de l'écran"""
        w = self.screen.get_width()
        
        # Bouton retour à gauche
        if len(actions) > 0:
            self.add_button((20, y_bottom - 70, 150, 50), actions[0][0], actions[0][1])
        
        # Autres boutons centrés avec largeur adaptative
        for i, (text, action) in enumerate(actions[1:], 1):
            # Calculer la largeur nécessaire selon la longueur du texte
            text_width = len(text) * 12  # Approximation : 12px par caractère
            button_width = max(200, text_width + 40)  # Minimum 200px, avec padding
            x = w // 2 - button_width // 2  # Centrer le bouton
            y = y_bottom - 150 + (i - 1) * 60
            self.add_button((x, y, button_width, 40), text, action)
    
    def add_increment_buttons(self, x: int, y: int, increment_func: Callable, 
                            decrement_func: Callable) -> Tuple[Button, Button]:
        """Ajoute des boutons +/- pour incrémenter/décrémenter une valeur"""
        btn_minus = self.add_button((x, y, 30, 30), "-", decrement_func, self.font_small)
        btn_plus = self.add_button((x + 40, y, 30, 30), "+", increment_func, self.font_small)
        return btn_minus, btn_plus
    
    def draw_buttons(self):
        """Dessine tous les boutons"""
        for btn in self.boutons:
            btn.draw(self.screen)
    
    def handle_button_events(self, event: pygame.event.Event) -> bool:
        """Gère les événements pour tous les boutons. Retourne True si un bouton a été cliqué"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.boutons:
                if btn.rect.collidepoint(event.pos):
                    if btn.action:
                        btn.action()
                    return True
        return False
    
    def draw_title(self, text: str, y: int = 50, color: Tuple[int, int, int] = (50, 50, 150)):
        """Dessine un titre centré"""
        title = self.font_big.render(text, True, color)
        x = self.screen.get_width() // 2 - title.get_width() // 2
        self.screen.blit(title, (x, y))
    
    def draw_text(self, text: str, x: int, y: int, font: Optional[pygame.font.Font] = None, 
                  color: Tuple[int, int, int] = (0, 0, 0)) -> pygame.Rect:
        """Dessine du texte et retourne le rectangle occupé"""
        if font is None:
            font = self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))
        return pygame.Rect(x, y, surface.get_width(), surface.get_height())
    
    def draw_input_field(self, x: int, y: int, width: int, height: int, 
                        text: str, field_name: str, max_length: int = 50) -> pygame.Rect:
        """Dessine un champ de saisie et retourne son rectangle"""
        rect = pygame.Rect(x, y, width, height)
        
        # Couleur de fond selon si le champ est actif
        color = (255, 255, 200) if self.champ_actif == field_name else (240, 240, 240)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
        
        # Texte
        if text:
            text_surface = self.font.render(text[:max_length], True, (0, 0, 0))
            self.screen.blit(text_surface, (rect.x + 5, rect.y + 5))
        
        return rect
    
    def handle_text_input(self, event: pygame.event.Event, text_data: dict, field_name: str, max_length: int = 50):
        """Gère la saisie de texte pour un champ donné"""
        if self.champ_actif != field_name:
            return
        
        if event.key == pygame.K_BACKSPACE:
            if field_name in text_data:
                text_data[field_name] = text_data[field_name][:-1]
        elif event.unicode.isprintable():
            if field_name in text_data and len(text_data[field_name]) < max_length:
                text_data[field_name] += event.unicode
    
    def handle_field_click(self, pos: Tuple[int, int], field_rects: dict):
        """Gère les clics sur les champs de saisie"""
        self.champ_actif = None
        for field_name, rect in field_rects.items():
            if rect.collidepoint(pos):
                self.champ_actif = field_name
                break


class ScrollableList:
    """Liste scrollable réutilisable"""
    
    def __init__(self, x: int, y: int, width: int, height: int, item_height: int = 30):
        self.rect = pygame.Rect(x, y, width, height)
        self.item_height = item_height
        self.scroll_y = 0
        self.scroll_speed = 30
        self.items: List[Any] = []
        self.selected_items: List[Any] = []
        
    def add_item(self, item: Any):
        """Ajoute un élément à la liste"""
        self.items.append(item)
    
    def clear_items(self):
        """Efface tous les éléments"""
        self.items = []
        self.selected_items = []
    
    def handle_scroll(self, event: pygame.event.Event):
        """Gère le défilement de la liste"""
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll_y = max(0, min(
                self.scroll_y - event.y * self.scroll_speed,
                max(0, len(self.items) * self.item_height - self.rect.height)
            ))
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[Any]:
        """Gère les clics sur les éléments de la liste"""
        if not self.rect.collidepoint(pos):
            return None
        
        local_y = pos[1] - self.rect.y + self.scroll_y
        item_index = local_y // self.item_height
        
        if 0 <= item_index < len(self.items):
            return self.items[item_index]
        return None
    
    def toggle_selection(self, item: Any):
        """Active/désactive la sélection d'un élément"""
        if item in self.selected_items:
            self.selected_items.remove(item)
        else:
            self.selected_items.append(item)
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, 
             render_item_func: Callable[[Any, bool], str]):
        """Dessine la liste avec une fonction de rendu personnalisée"""
        # Fond de la liste
        pygame.draw.rect(surface, (250, 250, 250), self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        # Créer une surface de clipping
        clip_rect = self.rect
        original_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        # Dessiner les éléments visibles
        start_item = max(0, self.scroll_y // self.item_height)
        end_item = min(len(self.items), 
                      start_item + (self.rect.height // self.item_height) + 2)
        
        for i in range(start_item, end_item):
            item = self.items[i]
            y = self.rect.y + i * self.item_height - self.scroll_y
            
            # Fond de l'élément si sélectionné
            item_rect = pygame.Rect(self.rect.x, y, self.rect.width, self.item_height)
            if item in self.selected_items:
                pygame.draw.rect(surface, (200, 255, 200), item_rect)
            
            # Texte de l'élément
            is_selected = item in self.selected_items
            text = render_item_func(item, is_selected)
            text_surface = font.render(text, True, (0, 0, 0))
            surface.blit(text_surface, (self.rect.x + 5, y + 5))
        
        # Restaurer le clipping
        surface.set_clip(original_clip)


class ProgressionManager:
    """Gestionnaire de progression de campagne."""
    
    @staticmethod
    def marquer_niveau_complete(sauvegarde_data: dict, chapitre: str, numero: int):
        """Marque un niveau comme complété dans la sauvegarde."""
        if "campagne_progression" not in sauvegarde_data:
            sauvegarde_data["campagne_progression"] = {}
        
        if chapitre not in sauvegarde_data["campagne_progression"]:
            sauvegarde_data["campagne_progression"][chapitre] = {"niveaux_completes": []}
        
        niveaux_completes = sauvegarde_data["campagne_progression"][chapitre]["niveaux_completes"]
        if numero not in niveaux_completes:
            niveaux_completes.append(numero)
    
    @staticmethod
    def est_niveau_complete(sauvegarde_data: dict, chapitre: str, numero: int) -> bool:
        """Vérifie si un niveau est déjà complété."""
        if "campagne_progression" not in sauvegarde_data:
            return False
        
        if chapitre not in sauvegarde_data["campagne_progression"]:
            return False
        
        return numero in sauvegarde_data["campagne_progression"][chapitre].get("niveaux_completes", [])
    
    @staticmethod
    def appliquer_recompenses(sauvegarde_data: dict, config_niveau) -> bool:
        """Applique les récompenses d'un niveau et retourne True si des récompenses ont été appliquées."""
        if not config_niveau:
            return False
        
        recompenses_appliquees = False
        
        # Appliquer les récompenses CP
        if hasattr(config_niveau, 'recompense_cp') and config_niveau.recompense_cp > 0:
            sauvegarde_data["cp"] = sauvegarde_data.get("cp", 5) + config_niveau.recompense_cp
            recompenses_appliquees = True
        
        # Appliquer les récompenses PA
        if hasattr(config_niveau, 'recompense_pa') and config_niveau.recompense_pa > 0:
            sauvegarde_data["pa"] = sauvegarde_data.get("pa", 100) + config_niveau.recompense_pa
            recompenses_appliquees = True
        
        # Débloquer les unités récompenses
        if hasattr(config_niveau, 'unites_debloquees') and config_niveau.unites_debloquees:
            if "unites" not in sauvegarde_data:
                sauvegarde_data["unites"] = []
            
            for unite_nom in config_niveau.unites_debloquees:
                if unite_nom not in sauvegarde_data["unites"]:
                    sauvegarde_data["unites"].append(unite_nom)
                    recompenses_appliquees = True
        
        return recompenses_appliquees

