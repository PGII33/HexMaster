import pygame
import sys
from utils import Button
import sauvegarde

# Catalogue des unités dispo dans la boutique
CATALOGUE = {
    "Squelette": {"prix": 5, "pv": 3, "dmg": 5, "mv": 2, "tier": 1, "comp": ("Aucune", "")},
    "Goule": {"prix": 5, "pv": 10, "dmg": 2, "mv": 1, "tier": 1, "comp": ("Aucune", "")},
    "Vampire": {"prix": 15, "pv": 12, "dmg": 3, "mv": 2, "tier": 2, "comp": ("Sangsue", "Attaque équilibrée, unité rare.")}
}

class Boutique:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 28)
        self.data = sauvegarde.charger()
        self.boutons = []

    def creer_boutons(self):
        """Créer les boutons Acheter et Retour"""
        self.boutons = []
        screen_w, screen_h = self.screen.get_size()
        margin = 40
        card_w = min(300, (screen_w - margin * 2) // 3)
        x, y = margin, 100

        for nom, infos in CATALOGUE.items():
            deja_achete = nom in self.data["unites"]

            def callback(nom_unite=nom, prix=infos["prix"]):
                if self.data["pa"] >= prix and nom_unite not in self.data["unites"]:
                    self.data["pa"] -= prix
                    self.data["unites"].append(nom_unite)
                    sauvegarde.sauvegarder(self.data)
                    self.creer_boutons()

            lignes = [
                f"{nom} - {infos['prix']} PA",
                f"PV: {infos['pv']} | DMG: {infos['dmg']} | MV: {infos['mv']}",
                f"Tier: {infos['tier']}",
                f"Compétence: {infos['comp'][0]}",
                f"{infos['comp'][1]}",
            ]
            card_h = 40 + len(lignes) * 30 + 50

            texte_bouton = "Épuisé" if deja_achete else "Acheter"
            couleur = (150, 150, 150) if deja_achete else (50, 150, 250)

            bouton = Button(
                (x + card_w//2 - 50, y + card_h - 45, 100, 35),
                texte_bouton,
                callback if not deja_achete else (lambda: None),
                self.font,
                base_color=couleur
            )
            self.boutons.append(bouton)

            # responsive placement
            x += card_w + margin
            if x + card_w > screen_w:
                x = margin
                y += card_h + margin

        # bouton retour
        self.boutons.append(Button((20, screen_h - 70, 150, 40), "Retour", self.retour_menu, self.font))

    def retour_menu(self):
        self.running = False

    def afficher(self):
        self.creer_boutons()
        self.running = True
        while self.running:
            self.screen.fill((240,240,250))

            # Afficher solde
            solde = self.font.render(f"Points d'âmes : {self.data['pa']}", True, (0,0,0))
            self.screen.blit(solde, (20, 20))

            screen_w, screen_h = self.screen.get_size()
            margin = 40
            card_w = min(300, (screen_w - margin * 2) // 3)
            x, y = margin, 100
            idx = 0

            for nom, infos in CATALOGUE.items():
                deja_achete = nom in self.data["unites"]

                lignes = [
                    f"{nom} - {infos['prix']} PA",
                    f"PV: {infos['pv']} | DMG: {infos['dmg']} | MV: {infos['mv']}",
                    f"Tier: {infos['tier']}",
                    f"Compétence: {infos['comp'][0]}",
                    f"{infos['comp'][1]}",
                ]
                card_h = 40 + len(lignes) * 30 + 50

                rect = pygame.Rect(x, y, card_w, card_h)
                pygame.draw.rect(self.screen, (220,220,220), rect, border_radius=12)
                pygame.draw.rect(self.screen, (0,0,0), rect, 2, border_radius=12)

                for i, l in enumerate(lignes):
                    txt = self.font.render(l, True, (0,0,0))
                    self.screen.blit(txt, (x+10, y+10+i*30))

                self.boutons[idx].draw(self.screen)
                idx += 1

                x += card_w + margin
                if x + card_w > screen_w:
                    x = margin
                    y += card_h + margin

            # bouton retour
            self.boutons[-1].draw(self.screen)

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

            pygame.display.flip()
