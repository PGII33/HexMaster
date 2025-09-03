import pygame
import sys
from utils import Button
import sauvegarde
from unites import CLASSES_UNITES
from competences import COMPETENCES

class Boutique:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.title_font = pygame.font.SysFont(None, 36)
        self.data = sauvegarde.charger()
        self.boutons = []
        self.scroll_y = 0
        self.scroll_speed = 40

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

    def acheter_unite(self, classe, prix, nom):
        """Achète une unité si possible"""
        # Vérifier si déjà acheté
        if nom in self.data["unites"]:
            return
        
        # Vérifier si assez de PA
        if self.data["pa"] < prix:
            return
        
        # Effectuer l'achat
        self.data["pa"] -= prix
        self.data["unites"].append(nom)
        
        # Sauvegarder
        sauvegarde.sauvegarder(self.data)
        
        # Recréer les boutons pour mettre à jour l'affichage
        self.creer_boutons()

    def retour_menu(self):
        self.running = False

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

    def afficher(self):
        self.creer_boutons()
        self.running = True
        self.scroll_y = 0
        while self.running:
            self.screen.fill((240,240,250))
            screen_w, screen_h, margin, cols, card_w, start_y = self._grid_specs()

            # --- SCROLL LIMITS ---
            total_height = start_y
            x, y, col = margin, start_y, 0
            for cls in CLASSES_UNITES:
                tmp = cls("joueur", (0,0))
                comp = tmp.get_competence()
                comp_desc = "" if not comp else COMPETENCES.get(comp, "")
                base_lines = [
                    f"{tmp.get_nom()}",
                    f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                    f"Attaques: {tmp.attaque_max}",
                    f"Faction: {tmp.faction}",
                    f"Tier: {tmp.get_tier()}",
                    f"Compétence: {'Aucune' if not comp else comp}",
                ]
                desc_lines = self.wrap_text(comp_desc, card_w - 20)
                card_h = 20 + len(base_lines) * 30 + len(desc_lines) * 26 + 60
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

            titre = self.title_font.render("Boutique", True, (30, 30, 60))
            self.screen.blit(titre, (margin, 30))

            x, y, col = margin, start_y - self.scroll_y, 0
            for cls in CLASSES_UNITES:
                tmp = cls("joueur", (0,0))
                nom = tmp.get_nom()
                prix = tmp.get_prix()
                comp = tmp.get_competence()
                comp_nom = "Aucune" if not comp else comp
                comp_desc = "" if not comp else COMPETENCES.get(comp, "")

                deja_achete = nom in self.data["unites"]

                base_lines = [
                    f"{nom}",
                    f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                    f"Attaques: {tmp.attaque_max}",
                    f"Faction: {tmp.faction}",
                    f"Tier: {tmp.get_tier()}",
                    f"Compétence: {comp_nom}",
                ]
                desc_lines = self.wrap_text(comp_desc, card_w - 20)
                card_h = 20 + len(base_lines) * 30 + len(desc_lines) * 26 + 60

                rect = pygame.Rect(x, y, card_w, card_h)
                pygame.draw.rect(self.screen, (220,220,220), rect, border_radius=12)
                pygame.draw.rect(self.screen, (0,0,0), rect, width=2, border_radius=12)

                for i, l in enumerate(base_lines):
                    txt = self.font.render(l, True, (0,0,0))
                    self.screen.blit(txt, (x + 10, y + 12 + i * 30))

                y_text = y + 12 + len(base_lines) * 30 + 6
                for line in desc_lines:
                    txt = self.font.render(line, True, (20, 20, 20))
                    self.screen.blit(txt, (x + 10, y_text))
                    y_text += 26

                # Bouton achat sur la carte
                if deja_achete:
                    couleur = (150,150,150)
                    texte = "Déjà acheté"
                elif self.data["pa"] >= prix:
                    couleur = (100,200,100)
                    texte = f"Acheter ({prix} PA)"
                else:
                    couleur = (200,100,100)
                    texte = f"Pas assez de PA ({prix})"

                btn_rect = pygame.Rect(x + 10, y + card_h - 50, card_w - 20, 40)
                btn = Button(
                    btn_rect,
                    texte,
                    lambda c=cls, p=prix, n=nom: self.acheter_unite(c, p, n),
                    self.font,
                    base_color=couleur
                )
                btn.draw(self.screen)
                self.boutons.append(btn)

                x += card_w + margin
                col += 1
                if col >= cols:
                    col = 0
                    x = margin
                    y += card_h + margin

            self.boutons[0].draw(self.screen)  # bouton retour

            solde = self.font.render(f"Points d'âmes : {self.data['pa']}", True, (0,0,0))
            self.screen.blit(solde, (self.screen.get_width() - solde.get_width() - 20, 20))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sauvegarde.sauvegarder(self.data)
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
