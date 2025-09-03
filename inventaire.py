import pygame
import sys
from utils import Button
import sauvegarde
from unites import CLASSES_UNITES
from competences import COMPETENCES

class Inventaire:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36)
        self.data = sauvegarde.charger()
        self.boutons = []
        self.scroll_y = 0
        self.scroll_speed = 40

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

    def creer_boutons(self):
        self.boutons = []
        screen_w, screen_h, *_ = self._grid_specs()
        self.boutons.append(Button((20, screen_h - 70, 160, 44), "Retour", self.retour_menu, self.font))

    def retour_menu(self):
        self.running = False

    def afficher(self):
        self.creer_boutons()
        self.running = True
        self.scroll_y = 0

        # AJOUTE CETTE LIGNE AVANT LA BOUCLE
        classes_dict = {}
        for classe in CLASSES_UNITES:
            tmp_instance = classe("joueur", (0,0))
            classes_dict[tmp_instance.get_nom()] = classe

        while self.running:
            self.screen.fill((250, 245, 230))
            screen_w, screen_h, margin, cols, card_w, start_y = self._grid_specs()

            # --- SCROLL LIMITS ---
            total_height = start_y
            x, y, col = margin, start_y, 0
            for nom in self.data.get("unites", []):
                cls = classes_dict.get(nom)
                if not cls:
                    continue
                tmp = cls("joueur", (0,0))
                comp = tmp.get_competence()
                comp_desc = "" if not comp else COMPETENCES.get(comp, "")
                base_lines = [
                    f"{nom}",
                    f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                    f"Tier: {tmp.get_tier()}",
                    f"Compétence: {'Aucune' if not comp else comp}",
                ]
                desc_lines = self.wrap_text(comp_desc, card_w - 20)
                card_h = 20 + len(base_lines) * 30 + len(desc_lines) * 26 + 20
                total_height = max(total_height, y + card_h)
                col += 1
                if col >= cols:
                    col = 0
                    x = margin
                    y += card_h + margin
                else:
                    x += card_w + margin
            max_scroll = max(0, total_height - (screen_h - start_y - 40))
            # --- FIN SCROLL LIMITS ---

            titre = self.title_font.render("Inventaire", True, (30, 30, 60))
            self.screen.blit(titre, (margin, 30))

            x, y, col = margin, start_y - self.scroll_y, 0
            for nom in self.data.get("unites", []):
                cls = classes_dict.get(nom)
                if not cls:
                    continue
                tmp = cls("joueur", (0,0))
                comp = tmp.get_competence()
                comp_nom = "Aucune" if not comp else comp
                comp_desc = "" if not comp else COMPETENCES.get(comp, "")

                base_lines = [
                    f"{nom}",
                    f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                    f"Tier: {tmp.get_tier()}",
                    f"Compétence: {comp_nom}",
                ]
                desc_lines = self.wrap_text(comp_desc, card_w - 20)
                card_h = 20 + len(base_lines) * 30 + len(desc_lines) * 26 + 20

                rect = pygame.Rect(x, y, card_w, card_h)
                pygame.draw.rect(self.screen, (235, 235, 235), rect, border_radius=12)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=12)

                for i, l in enumerate(base_lines):
                    txt = self.font.render(l, True, (0, 0, 0))
                    self.screen.blit(txt, (x + 10, y + 12 + i * 30))

                y_text = y + 12 + len(base_lines) * 30 + 6
                for line in desc_lines:
                    txt = self.font.render(line, True, (20, 20, 20))
                    self.screen.blit(txt, (x + 10, y_text))
                    y_text += 26

                col += 1
                if col >= cols:
                    col = 0
                    x = margin
                    y += card_h + margin
                else:
                    x += card_w + margin

            self.boutons[-1].draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.creer_boutons()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for b in self.boutons:
                        b.handle_event(event)
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y -= event.y * self.scroll_speed
                    self.scroll_y = max(0, min(self.scroll_y, max_scroll))

            pygame.display.flip()
