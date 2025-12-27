""" Module de la boutique """
# pylint: disable=no-name-in-module
# pylint: disable=no-member
import sys
from unites_liste import CLASSES_UNITES
import pygame
from utils import Button, wrap_text, draw_bandeau, get_grid_specs, handle_scroll_events
import sauvegarde
from competences import COMPETENCES
from faction_colors import get_faction_color

class Boutique:
    """ Classe de la boutique où le joueur peut acheter des unités """
    def __init__(self, screen):
        self.screen = screen
        if screen:  # Seulement si on a un écran
            self.font = pygame.font.SysFont(None, 28)
            self.title_font = pygame.font.SysFont(None, 36)
        self.data = sauvegarde.charger()
        self.boutons = []
        self.scroll_y = 0
        self.scroll_speed = 40
        # Système de déblocage secret pour Tier 4
        self.secret_clicks = 0
        self.secret_click_rect = None
        self.running = False

    def est_faction_debloquee(self, faction):
        """Vérifie si le joueur possède au moins une unité de cette faction"""
        unites_possedees = self.data.get("unites", [])

        # Parcourir toutes les unités possédées
        for nom_unite in unites_possedees:
            # Trouver la classe correspondante
            for classe_unite in CLASSES_UNITES:
                tmp = classe_unite("joueur", (0, 0))
                if tmp.get_nom() == nom_unite and tmp.get_faction() == faction:
                    return True
        return False

    def _get_card_height(self, card_w, cls):
        tmp = cls("joueur", (0, 0))
        comp = tmp.get_competence()
        comp_desc = "" if not comp else COMPETENCES.get(comp, "")
        base_lines = [
            f"{tmp.get_nom()}",
            f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
            f"Attaques: {tmp.get_attaque_max()} | Portée: {tmp.get_portee()}",
            f"Faction: {tmp.get_faction()}",
            f"Tier: {tmp.get_tier()}",
            f"Compétence: {'Aucune' if not comp else comp}",
        ]
        desc_lines = wrap_text(comp_desc, self.font, card_w - 20)
        card_h = 20 + len(base_lines) * 30 + len(desc_lines) * 26 + 60
        return card_h

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
        """ Crée les boutons de la boutique """
        self.boutons = []
        self.boutons.append(Button((20, 160, 44), "Retour",
                            self.retour_menu, self.font))

    def acheter_unite(self, prix, nom):
        """Achète une unité si possible"""
        # Vérifier si déjà acheté
        if nom in self.data["unites"]:
            return

        # Vérifier si l'unité est achetable (pas "Bloqué")
        if prix == "Bloqué":
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

    def debloquer_tier4_secret(self):
        """Débloque toutes les unités Tier 4 (système secret)"""

        tier4_units = []
        for classe in CLASSES_UNITES:
            # Créer une instance temporaire pour vérifier le tier
            temp_unit = classe(0, (0, 0))
            if temp_unit.get_tier() == 4 and temp_unit.get_nom() not in self.data["unites"]:
                self.data["unites"].append(temp_unit.get_nom())
                tier4_units.append(temp_unit.get_nom())

        if tier4_units:
            print(
                f"🎉 Déblocage secret ! Unités Tier 4 débloquées: {', '.join(tier4_units)}")
            sauvegarde.sauvegarder(self.data)
            self.creer_boutons()
        else:
            print("🔒 Toutes les unités Tier 4 sont déjà débloquées!")

    def retour_menu(self):
        """ Retourne au menu principal """
        self.running = False

    def wrap_text(self, text, max_width):
        """ Retourne une liste de lignes de texte enveloppées selon la largeur maximale """
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
        """ Affiche la boutique et gère les interactions """
        self.running = True
        self.scroll_y = 0
        bandeau_h = 70  # Hauteur du bandeau
        while self.running:
            self.screen.fill((240, 240, 250))
            screen_w, screen_h, margin, cols, card_w, start_y, card_h = get_grid_specs(
                self.screen,
                CLASSES_UNITES,
                self._get_card_height
            )

            # Recréer les boutons à chaque frame pour éviter l'accumulation
            self.boutons = []

            # Bouton retour (ajouté en premier)
            bouton_retour = Button(
                (20, screen_h - 70, 160, 44), "Retour", self.retour_menu, self.font)
            self.boutons.append(bouton_retour)

            # --- SCROLL LIMITS ---
            total_height = start_y
            x, y, col = margin, start_y, 0
            unites_visibles = []

            for cls in CLASSES_UNITES:
                tmp = cls("joueur", (0, 0))
                if not self.est_faction_debloquee(tmp.get_faction()):
                    continue
                unites_visibles.append(cls)
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

            # Placement des cartes sous le bandeau
            x, y, col = margin, start_y - self.scroll_y, 0
            for cls in unites_visibles:
                tmp = cls("joueur", (0, 0))
                nom = tmp.get_nom()
                prix = tmp.get_prix()
                comp = tmp.get_competence()
                comp_nom = "Aucune" if not comp else comp
                comp_desc = "" if not comp else COMPETENCES.get(comp, "")

                deja_achete = nom in self.data["unites"]

                base_lines = [
                    f"{nom}",
                    f"PV: {tmp.get_pv()} | DMG: {tmp.get_dmg()} | MV: {tmp.get_mv()}",
                    f"Attaques: {tmp.get_attaque_max()} | Portée: {tmp.get_portee()}",
                    f"Faction: {tmp.get_faction()}",
                    f"Tier: {tmp.get_tier()}",
                    f"Compétence: {comp_nom}",
                ]
                desc_lines = wrap_text(comp_desc, self.font, card_w - 20)

                # Couleur de fond selon la faction
                faction_color = get_faction_color(tmp.get_faction())

                rect = pygame.Rect(x, y, card_w, card_h)
                pygame.draw.rect(self.screen, faction_color,
                                 rect, border_radius=12)
                pygame.draw.rect(self.screen, (0, 0, 0), rect,
                                 width=2, border_radius=12)

                for i, l in enumerate(base_lines):
                    txt = self.font.render(l, True, (0, 0, 0))
                    self.screen.blit(txt, (x + 10, y + 12 + i * 30))

                y_text = y + 12 + len(base_lines) * 30 + 6
                for line in desc_lines:
                    txt = self.font.render(line, True, (20, 20, 20))
                    self.screen.blit(txt, (x + 10, y_text))
                    y_text += 26

                # Bouton achat sur la carte
                if deja_achete:
                    couleur = (150, 150, 150)
                    texte = "Déjà acheté"
                elif prix == "Bloqué":
                    couleur = (100, 100, 100)
                    texte = "Non achetable"
                elif self.data["pa"] >= prix:
                    couleur = (100, 200, 100)
                    texte = f"Acheter ({prix} PA)"
                else:
                    couleur = (200, 100, 100)
                    texte = f"Pas assez de PA ({prix})"

                btn_rect = pygame.Rect(
                    x + 10, y + card_h - 50, card_w - 20, 40)
                btn = Button(
                    btn_rect,
                    texte,
                    lambda c=cls, p=prix, n=nom: self.acheter_unite(p, n),
                    self.font,
                    base_color=couleur
                )
                self.boutons.append(btn)
                btn.draw(self.screen)

                x += card_w + margin
                col += 1
                if col >= cols:
                    col = 0
                    x = margin
                    y += card_h + margin

            # Dessiner le bouton retour par-dessus
            bouton_retour.draw(self.screen)

            # --- BANDEAU EN HAUT (toujours dessiné en dernier, donc au 1er plan) ---
            # Utilisation de la fonction utilitaire
            secret_click_rect_container = [None]
            draw_bandeau(
                self.screen,
                screen_w,
                bandeau_h,
                margin,
                self.font,
                self.title_font,
                "Points d'âmes : " + str(self.data["pa"]),
                titre="Boutique",
                secret_click_rect_container=secret_click_rect_container
            )
            self.secret_click_rect = secret_click_rect_container[0]

            # --- GESTION DES EVENEMENTS ---
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    sauvegarde.sauvegarder(self.data)
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE)
                    self.creer_boutons()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Bloquer tout clic dans la zone du bandeau
                    if event.pos[1] < bandeau_h:
                        # Clic dans le bandeau
                        if self.secret_click_rect and self.secret_click_rect.collidepoint(event.pos):
                            self.secret_clicks += 1
                            print(f"🔍 Clic secret {self.secret_clicks}/5")
                            if self.secret_clicks >= 5:
                                self.debloquer_tier4_secret()
                                self.secret_clicks = 0
                        continue  # Empêche tout autre clic dans le bandeau
                    # Gérer les clics normaux sur les boutons avec priorité au bouton retour
                    button_clicked = False
                    if self.boutons and self.boutons[0].rect.collidepoint(event.pos):
                        self.boutons[0].handle_event(event)
                        button_clicked = True
                    if not button_clicked:
                        for i in range(1, len(self.boutons)):
                            if self.boutons[i].rect.collidepoint(event.pos):
                                self.boutons[i].handle_event(event)
                                break
            # Gestion du scroll
            self.scroll_y = handle_scroll_events(
                events, self.scroll_y, self.scroll_speed, max_scroll)

            pygame.display.flip()
