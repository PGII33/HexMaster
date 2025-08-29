# fichier: jeu.py
import pygame
import sys
import math
import time
import ia
import unites

# --- Paramètres généraux ---
DIM_GRILLE = 7           # dimension "logique" de la grille (q,r vont de -1 à DIM_GRILLE-1)
MARGE = 12               # marge intérieure (px)
SIDE_MIN_W = 260         # largeur mini du panneau latéral (px)
TOP_H_RATIO = 0.07       # hauteur du bandeau (% de la hauteur)
BTN_H_RATIO = 0.06       # hauteur du bouton fin de tour (% de la hauteur)

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (200, 50, 50)
VERT = (50, 200, 50)
GRIS = (180, 180, 180)
BLEU = (50, 150, 250)

# -------------------------
#  Bouton simple
# -------------------------
class Button:
    def __init__(self, rect, text, action, font, base_color=(100,100,250), hover_color=(140,140,250), text_color=BLANC):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

# -------------------------
#  Classe Jeu (ton code, refactorisé pour être piloté depuis l'extérieur)
# -------------------------
class Jeu:
    def __init__(self, ia_strategy=ia.cible_faible, screen=None):
        # Possibilité de recevoir la surface/window depuis l'extérieur
        self.screen = screen if screen is not None else pygame.display.set_mode((1200, 900), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # État du jeu
        self.unites = [
            unites.Squelette("joueur", (0, 0)),
            unites.Cavalier("joueur", (1, 0)),
            unites.Squelette("ennemi", (0, 2)),
            unites.Barbare("ennemi", (1, 2)),
        ]
        self.tour = "joueur"
        self.selection = None
        self.deplacement_possibles = {}  # {(q, r): cout}
        self.ia_strategy = ia_strategy

        self.q_range = range(-1, DIM_GRILLE)
        self.r_range = range(-1, DIM_GRILLE)

        # IA execution state (pour échelonner les actions ennemies)
        self.ia_busy = False
        self.ia_queue = []
        self.ia_index = 0
        self.ia_timer_ms = 0
        self.ia_delay_between_actions = 250  # ms

        # Flag pour indiquer fin de partie
        self.finished = False

        self.recalculer_layout()

    # -----------------------------
    #      Géométrie hexagones
    # -----------------------------
    def axial_to_pixel(self, q, r, size):
        """Layout pointy-topped (axe axial q,r). Sans offset/centrage."""
        x = size * (math.sqrt(3) * q + (math.sqrt(3) / 2) * r)
        y = size * (1.5 * r)
        return x, y

    def recalculer_layout(self):
        """Recalcule dynamiquement tailles, centrage, panneaux, polices, etc."""
        self.largeur, self.hauteur = self.screen.get_size()

        # Panneau latéral (responsive, mais avec largeur mini)
        self.sidebar_w = max(SIDE_MIN_W, int(self.largeur * 0.23))
        self.top_h = max(40, int(self.hauteur * TOP_H_RATIO))

        # Aire disponible pour la grille
        grid_w = self.largeur - self.sidebar_w - 2 * MARGE
        grid_h = self.hauteur - self.top_h - 2 * MARGE
        grid_w = max(100, grid_w)
        grid_h = max(100, grid_h)

        # Calcul de la taille d'hex en fonction de l'enveloppe de la grille (avec size=1 pour normaliser)
        size_probe = 1.0
        centers = []
        for q in self.q_range:
            for r in self.r_range:
                x, y = self.axial_to_pixel(q, r, size_probe)
                centers.append((x, y))
        minx = min(x for x, _ in centers)
        maxx = max(x for x, _ in centers)
        miny = min(y for _, y in centers)
        maxy = max(y for _, y in centers)

        env_w_unit = (maxx - minx) + 2.0
        env_h_unit = (maxy - miny) + 2.0

        sx = grid_w / env_w_unit
        sy = grid_h / env_h_unit
        self.taille_hex = max(8, int(min(sx, sy)))  # éviter des hex trop petits

        # Recalcule l'enveloppe avec la taille finale
        centers_px = []
        for q in self.q_range:
            for r in self.r_range:
                x, y = self.axial_to_pixel(q, r, self.taille_hex)
                centers_px.append((x, y))
        minx_px = min(x for x, _ in centers_px)
        maxx_px = max(x for x, _ in centers_px)
        miny_px = min(y for _, y in centers_px)
        maxy_px = max(y for _, y in centers_px)

        env_w = (maxx_px - minx_px) + 2 * self.taille_hex
        env_h = (maxy_px - miny_px) + 2 * self.taille_hex

        grid_left = MARGE
        grid_top = self.top_h + MARGE
        offset_left = grid_left + (grid_w - env_w) / 2.0 + self.taille_hex
        offset_top = grid_top + (grid_h - env_h) / 2.0 + self.taille_hex

        self.offset_x = offset_left - minx_px
        self.offset_y = offset_top - miny_px

        self.unit_radius = max(12, int(self.taille_hex * 0.45))

        self.font_small = pygame.font.SysFont(None, max(14, int(self.hauteur * 0.022)))
        self.font_norm = pygame.font.SysFont(None, max(18, int(self.hauteur * 0.026)))
        self.font_big = pygame.font.SysFont(None, max(22, int(self.hauteur * 0.03)))

        btn_w = int(self.sidebar_w * 0.8)
        btn_h = max(36, int(self.hauteur * BTN_H_RATIO))
        btn_x = self.largeur - self.sidebar_w + (self.sidebar_w - btn_w) // 2
        btn_y = self.hauteur - btn_h - MARGE
        self.btn_fin_tour = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        self.info_panel = pygame.Rect(self.largeur - self.sidebar_w + MARGE,
                                      self.top_h + MARGE,
                                      self.sidebar_w - 2 * MARGE,
                                      int(self.hauteur * 0.25))

    def hex_to_pixel(self, q, r):
        x, y = self.axial_to_pixel(q, r, self.taille_hex)
        return int(x + self.offset_x), int(y + self.offset_y)

    def dessiner_hex(self, surface, q, r, couleur, largeur=1):
        x, y = self.hex_to_pixel(q, r)
        pts = []
        for i in range(6):
            ang = math.pi / 3 * i + math.pi / 6
            px = x + self.taille_hex * math.cos(ang)
            py = y + self.taille_hex * math.sin(ang)
            pts.append((px, py))
        pygame.draw.polygon(surface, couleur, pts, largeur)

    # -----------------------------
    #             Draw
    # -----------------------------
    def dessiner(self):
        # Dessine tout sur self.screen
        self.screen.fill(BLANC)

        # Bandeau supérieur
        bandeau = pygame.Rect(0, 0, self.largeur, self.top_h)
        pygame.draw.rect(self.screen, (200, 200, 250), bandeau)
        txt_tour = self.font_big.render(f"Tour du {self.tour}", True, NOIR)
        self.screen.blit(txt_tour, (self.largeur // 2 - txt_tour.get_width() // 2,
                                    self.top_h // 2 - txt_tour.get_height() // 2))

        # Séparateur vertical pour le panneau latéral
        pygame.draw.line(self.screen, GRIS,
                         (self.largeur - self.sidebar_w, self.top_h),
                         (self.largeur - self.sidebar_w, self.hauteur), width=2)

        # Dessiner la grille
        for q in self.q_range:
            for r in self.r_range:
                if (q, r) in self.deplacement_possibles:
                    cout = self.deplacement_possibles[(q, r)]
                    intensite = max(70, 250 - cout * 40)
                    couleur = (50, 50, intensite)
                    self.dessiner_hex(self.screen, q, r, couleur, max(2, int(self.taille_hex * 0.08)))
                    # Affiche aussi le coût au centre
                    cx, cy = self.hex_to_pixel(q, r)
                    txtc = self.font_small.render(str(cout), True, BLANC)
                    self.screen.blit(txtc, (cx - txtc.get_width()//2, cy - txtc.get_height()//2))
                else:
                    self.dessiner_hex(self.screen, q, r, GRIS, max(1, int(self.taille_hex * 0.05)))

        # Dessiner les unités
        for u in self.unites:
            if not u.vivant:
                continue
            x, y = self.hex_to_pixel(u.pos[0], u.pos[1])
            color = VERT if u.equipe == "joueur" else ROUGE
            pygame.draw.circle(self.screen, color, (x, y), self.unit_radius)
            name_txt = self.font_small.render(u.nom, True, NOIR)
            self.screen.blit(name_txt, (x - name_txt.get_width() // 2, y - self.unit_radius - name_txt.get_height() - 2))

            # Cercle autour de l'unité sélectionnée
            if self.selection == u:
                pygame.draw.circle(self.screen, color, (x, y), int(self.unit_radius * 1.25), width=max(2, int(self.taille_hex * 0.08)))

        # Panneau d'infos (si sélection)
        if self.selection:
            u = self.selection
            pygame.draw.rect(self.screen, (225, 225, 225), self.info_panel, border_radius=8)
            lignes = [
                f"Nom: {u.nom}",
                f"Equipe: {u.equipe}",
                f"PV: {u.pv}",
                f"DMG: {u.dmg}",
                f"PM restants: {u.pm}/{u.mv}",
                f"Attaque dispo: {'non' if u.a_attaque else 'oui'}",
            ]
            for i, l in enumerate(lignes):
                txt = self.font_norm.render(l, True, NOIR)
                self.screen.blit(txt, (self.info_panel.x + 10, self.info_panel.y + 10 + i * (txt.get_height() + 4)))

            # Surligner les ennemis adjacents si on peut attaquer
            if not u.a_attaque:
                for ennemi in [x for x in self.unites if x.equipe != u.equipe and x.vivant]:
                    if u.est_adjacente(ennemi):
                        ex, ey = self.hex_to_pixel(ennemi.pos[0], ennemi.pos[1])
                        pygame.draw.circle(self.screen, (255, 0, 0), (ex, ey), int(self.unit_radius * 1.1), width=max(2, int(self.taille_hex * 0.08)))

        # Bouton Fin de tour
        pygame.draw.rect(self.screen, (100, 100, 250), self.btn_fin_tour, border_radius=8)
        txt_btn = self.font_norm.render("Fin de tour", True, BLANC)
        self.screen.blit(txt_btn, (self.btn_fin_tour.centerx - txt_btn.get_width() // 2,
                                   self.btn_fin_tour.centery - txt_btn.get_height() // 2))

    # -----------------------------
    #           Helpers
    # -----------------------------
    def reset_actions_tour(self):
        for u in self.unites:
            if u.equipe == self.tour and u.vivant:
                u.reset_actions()

    def handle_click(self, mx, my):
        # Clic sur bouton fin de tour
        if self.btn_fin_tour.collidepoint(mx, my):
            self.tour = "ennemi" if self.tour == "joueur" else "joueur"
            self.selection = None
            self.deplacement_possibles = {}
            self.reset_actions_tour()
            return

        # Clic sur une unité ?
        for u in self.unites:
            if not u.vivant:
                continue
            x, y = self.hex_to_pixel(u.pos[0], u.pos[1])
            if (mx - x) ** 2 + (my - y) ** 2 <= (self.unit_radius) ** 2:
                if u.equipe == self.tour:  # sélection d'une unité alliée
                    if self.selection == u:
                        self.selection = None
                        self.deplacement_possibles = {}
                    else:
                        self.selection = u
                        self.deplacement_possibles = u.cases_accessibles(self.unites)
                else:  # clic sur une unité ennemie
                    if self.selection and not self.selection.a_attaque and self.selection.est_adjacente(u):
                        # attaque si ennemi adjacent
                        self.selection.attaquer(u)
                    else:
                        # sinon, simple sélection (afficher stats de l'ennemi)
                        self.selection = u
                    self.deplacement_possibles = {}
                return  # on a géré un clic sur une unité

        # Clic sur une case vide pour déplacement ?
        if self.selection and self.deplacement_possibles:
            for case, cout in self.deplacement_possibles.items():
                cx, cy = self.hex_to_pixel(case[0], case[1])
                if (mx - cx) ** 2 + (my - cy) ** 2 <= (self.unit_radius) ** 2:
                    occupee = any(u.pos == case and u.vivant for u in self.unites)
                    if not occupee and self.selection.pm >= cout:
                        self.selection.pos = case
                        self.selection.pm -= cout
                    self.deplacement_possibles = {}
                    return

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            # Réassignation de la surface/window
            self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            self.recalculer_layout()
        elif event.type == pygame.MOUSEBUTTONDOWN and self.tour == "joueur":
            mx, my = event.pos
            self.handle_click(mx, my)

    def update(self, dt_ms):
        """dt_ms: ms depuis la dernière frame. Gère le tour IA étape par étape."""
        # Vérifier fin de partie
        joueurs = [u for u in self.unites if u.equipe == "joueur" and u.vivant]
        ennemis = [u for u in self.unites if u.equipe == "ennemi" and u.vivant]
        if not joueurs or not ennemis:
            # fin de la partie
            self.finished = True
            return

        if self.tour == "ennemi":
            # Initialisation de la file si nécessaire
            if not self.ia_busy:
                self.ia_queue = ennemis[:]
                self.ia_index = 0
                self.ia_busy = True
                self.ia_timer_ms = 0

            # Si on a encore des ennemis à jouer
            if self.ia_busy and self.ia_index < len(self.ia_queue):
                self.ia_timer_ms -= dt_ms
                if self.ia_timer_ms <= 0:
                    e = self.ia_queue[self.ia_index]
                    # recalculer joueurs vivants
                    joueurs_courants = [u for u in self.unites if u.equipe == "joueur" and u.vivant]
                    action = self.ia_strategy(e, joueurs_courants, self.unites)
                    # pause avant la prochaine action
                    self.ia_timer_ms = self.ia_delay_between_actions
                    self.ia_index += 1
            else:
                # Fin du tour ennemi
                self.tour = "joueur"
                self.reset_actions_tour()
                self.ia_busy = False
                self.ia_queue = []
                self.ia_index = 0
                self.ia_timer_ms = 0

# -------------------------
#  Gestionnaire global des écrans (menus + jeu)
# -------------------------
class HexaMaster:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 900), pygame.RESIZABLE)
        pygame.display.set_caption("HexaMaster")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont(None, 80)
        self.font_med = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 20)

        self.etat = "menu"
        self.jeu = None

        self.creer_boutons()

    def creer_boutons(self):
        w, h = self.screen.get_size()
        center_x = w // 2
        # Menu principal
        self.boutons_menu = [
            Button((center_x-140, h//2-130, 280, 60), "Jouer", lambda: self.set_etat("playmenu"), self.font_med),
            Button((center_x-140, h//2-50, 280, 60), "Inventaire", lambda: self.set_etat("inventaire"), self.font_med),
            Button((center_x-140, h//2+30, 280, 60), "Boutique", lambda: self.set_etat("boutique"), self.font_med),
            Button((center_x-140, h//2+110, 280, 60), "Missions", lambda: self.set_etat("missions"), self.font_med),
            Button((center_x-140, h//2+190, 280, 60), "Quitter", lambda: sys.exit(), self.font_med),
        ]
        # Play menu
        self.boutons_playmenu = [
            Button((center_x-140, h//2-90, 280, 60), "1 Joueur", lambda: self.start_play_mode(1), self.font_med),
            Button((center_x-140, h//2-10, 280, 60), "2 Joueurs", lambda: self.start_play_mode(2), self.font_med),
            Button((center_x-140, h//2+70, 280, 60), "3 Joueurs", lambda: self.start_play_mode(3), self.font_med),
            Button((20, h-70, 150, 50), "Retour", lambda: self.set_etat("menu"), self.font_med),
        ]
        # Retour pour autres écrans
        self.boutons_retour = [
            Button((20, h-70, 150, 50), "Retour", lambda: self.set_etat("menu"), self.font_med)
        ]

    def set_etat(self, e):
        # Au passage, si on quitte le jeu, nettoyer l'instance
        if self.etat == "jeu" and e != "jeu":
            self.jeu = None
        self.etat = e

    def start_play_mode(self, n_players):
        # Pour l'instant : si 2 joueurs -> on lance la démo (mode jeu)
        if n_players == 2:
            self.jeu = Jeu(ia_strategy=ia.cible_faible, screen=self.screen)
            self.etat = "jeu"
        else:
            # placeholder pour 1 et 3 joueurs
            self.etat = "jeu"
            self.jeu = Jeu(ia_strategy=ia.cible_faible, screen=self.screen)  # démarrage demo aussi (facilement changeable)

    def run(self):
        while True:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.VIDEORESIZE:
                    # Mettre à jour la surface et recalculer layout partout
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.creer_boutons()
                    if self.jeu:
                        self.jeu.screen = self.screen
                        self.jeu.recalculer_layout()

                # Dispatch des événements selon l'état
                if self.etat == "menu":
                    for b in self.boutons_menu:
                        b.handle_event(event)
                elif self.etat == "playmenu":
                    for b in self.boutons_playmenu:
                        b.handle_event(event)
                elif self.etat in ["inventaire", "boutique", "missions"]:
                    for b in self.boutons_retour:
                        b.handle_event(event)
                elif self.etat == "jeu":
                    if self.jeu:
                        self.jeu.handle_event(event)

            # Update + Draw selon l'état
            if self.etat == "menu":
                self.screen.fill(BLANC)
                titre = self.font_big.render("HexaMaster", True, BLEU)
                self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 80))
                for b in self.boutons_menu: b.draw(self.screen)

            elif self.etat == "playmenu":
                self.screen.fill(BLANC)
                titre = self.font_big.render("Mode de jeu", True, BLEU)
                self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 80))
                for b in self.boutons_playmenu: b.draw(self.screen)

            elif self.etat in ["inventaire", "boutique", "missions"]:
                self.screen.fill(BLANC)
                titre = self.font_big.render(self.etat.capitalize(), True, BLEU)
                self.screen.blit(titre, (self.screen.get_width()//2 - titre.get_width()//2, 80))
                for b in self.boutons_retour: b.draw(self.screen)
                # placeholder content
                info = self.font_small.render("Écran en construction — contenu placeholder", True, NOIR)
                self.screen.blit(info, (50, 200))

            elif self.etat == "jeu":
                if self.jeu:
                    self.jeu.update(dt)
                    # si le jeu indique qu'il est fini -> on retourne au menu
                    if self.jeu.finished:
                        # possible afficher un message rapide
                        # ici on revient simplement au menu principal
                        self.jeu = None
                        self.etat = "menu"
                    else:
                        self.jeu.dessiner()

            pygame.display.flip()

if __name__ == "__main__":
    HexaMaster().run()
