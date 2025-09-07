import pygame
import sys
import math
import ia
import unites
import animations
from layout import recalculer_layout, axial_to_pixel, hex_to_pixel
from affichage import dessiner
from input_mod import handle_click
from tour import reset_actions_tour

def _get_unit_class_by_name(name: str):
    """Convertit un nom de classe d'unité en vraie classe"""
    for cls in unites.CLASSES_UNITES:
        if cls("joueur", (0, 0)).get_nom() == name:
            return cls
    raise ValueError(f"Classe d'unité '{name}' non trouvée")

# Constantes (importées si besoin depuis menu)
BTN_H_RATIO = 0.06

class Jeu:
    def __init__(self, ia_strategy=ia.cible_faible, screen=None,
                 initial_player_units=None, initial_enemy_units=None, 
                 enable_placement=False, versus_mode=False, niveau_config=None, 
                 mode_hexarene=False, hexarene_mode_type=None, faction_hexarene=None,
                 chapitre_nom=None, niveau_nom=None):
        self.screen = screen if screen is not None else pygame.display.set_mode((1200, 900), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        # Mode et configuration
        self.mode_hexarene = mode_hexarene
        self.hexarene_mode_type = hexarene_mode_type  # "faction" ou "libre"
        self.faction_hexarene = faction_hexarene
        self.chapitre_nom = chapitre_nom
        self.niveau_nom = niveau_nom
        self.niveau_config = niveau_config

        # État du jeu et résultats
        self.unites = []
        self.enable_placement = enable_placement
        self.versus_mode = versus_mode  # Nouveau : mode joueur vs joueur
        
        # Menu de fin de combat
        self.show_end_menu = False
        self.end_menu_processed = False  # Nouveau flag pour éviter les re-activations
        self.recompenses = {"pa": 0, "cp": 0, "unites": []}
        
        # Variables pour le système de compétences actives
        self.mode_selection_competence = False
        self.competence_en_cours = None
        self.cibles_possibles = []
        self.competence_btn_rect = None
        
        # Traitement des unités selon le mode
        if enable_placement and initial_player_units:
            # Mode avec placement : initial_player_units contient des classes
            from placement import PlacementPhase
            placement = PlacementPhase(screen, initial_player_units)
            placed_units = placement.run()
            
            if placed_units:
                # placed_units contient [(classe, position), ...]
                for cls, pos in placed_units:
                    self.unites.append(cls("joueur", pos))
            else:
                # Placement annulé
                self.finished = True
                return
            
            # Placement automatique des ennemis selon leurs positions définies
            if initial_enemy_units:
                for i, enemy_data in enumerate(initial_enemy_units):
                    # Gestion des deux formats : classe directe ou (nom_classe, position)
                    if isinstance(enemy_data, tuple) and len(enemy_data) == 2:
                        # Format (nom_classe, position) ou (classe, position)
                        enemy_name_or_class, enemy_position = enemy_data
                        if isinstance(enemy_name_or_class, str):
                            cls = _get_unit_class_by_name(enemy_name_or_class)
                        else:
                            cls = enemy_name_or_class  # C'est déjà une classe
                        
                        # Utiliser la position définie, pas une position automatique
                        # Convertir la liste en tuple si nécessaire (problème JSON)
                        if isinstance(enemy_position, list):
                            enemy_position = tuple(enemy_position)
                        self.unites.append(cls("ennemi", enemy_position))
                    else:
                        # Format classe directe (ancien système) - utiliser position par défaut
                        cls = enemy_data
                        # Fallback: placer en zone rouge si pas de position spécifiée
                        fallback_positions = []
                        for r in [4, 5, 6]:  # Zone ennemie
                            for q in range(-1, 7):
                                fallback_positions.append((q, r))
                        pos = fallback_positions[i] if i < len(fallback_positions) else (5, 5)
                        self.unites.append(cls("ennemi", pos))
        
        else:
            # Mode sans placement : initial_player_units contient [(classe, position), ...]
            if initial_player_units:
                for cls, pos in initial_player_units:
                    # Convertir la liste en tuple si nécessaire (problème JSON)
                    if isinstance(pos, list):
                        pos = tuple(pos)
                    self.unites.append(cls("joueur", pos))

            if initial_enemy_units:
                for enemy_data in initial_enemy_units:
                    # Gestion des deux formats : (classe, position) ou (nom_classe, position)
                    if isinstance(enemy_data, tuple) and len(enemy_data) == 2:
                        cls_or_name, pos = enemy_data
                        if isinstance(cls_or_name, str):
                            cls = _get_unit_class_by_name(cls_or_name)
                        else:
                            cls = cls_or_name  # C'est déjà une classe
                        
                        # Convertir la liste en tuple si nécessaire (problème JSON)
                        if isinstance(pos, list):
                            pos = tuple(pos)
                    else:
                        # Format ancien - cls directe
                        cls = enemy_data
                        pos = (5, 5)  # Position par défaut
                    
                    # En mode versus, les "ennemis" sont le joueur 2
                    equipe = "joueur2" if versus_mode else "ennemi"
                    self.unites.append(cls(equipe, pos))

        self.tour = "joueur"
        self.selection = None
        self.deplacement_possibles = {}
        self.ia_strategy = ia_strategy

        self.q_range = range(-1, 7)
        self.r_range = range(-1, 7)

        self.ia_busy = False
        self.ia_queue = []
        self.ia_index = 0
        self.ia_timer_ms = 0
        self.ia_delay_between_actions = 250

        self.finished = False
        self.player_victory = False  # Nouveau: pour distinguer victoire/défaite
        self.niveau_config = niveau_config  # Nouveau: pour appliquer les récompenses

        # Configuration du callback de kill pour le mode hexarene
        if self.mode_hexarene:
            import unites
            unites.set_kill_callback(self.on_enemy_killed)

        recalculer_layout(self)

    def on_enemy_killed(self, killed_unit):
        """Appelé quand une unité ennemie est tuée. Gère les gains de PA en mode hexarene."""
        if self.mode_hexarene and killed_unit.equipe == "ennemi":
            import sauvegarde
            data = sauvegarde.charger()
            
            # Gagner des PA égaux au tier de l'unité tuée
            pa_gagne = killed_unit.tier
            data["pa"] = data.get("pa", 100) + pa_gagne
            
            sauvegarde.sauvegarder(data)
            print(f"💰 +{pa_gagne} PA pour avoir tué {killed_unit.nom} (Tier {killed_unit.tier})")

    def recalculer_layout(self):
        recalculer_layout(self)

    def dessiner(self):
        dessiner(self)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            self.recalculer_layout()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Permettre les clics pour TOUS les tours (joueur ET joueur2)
            if self.versus_mode or self.tour == "joueur":
                mx, my = event.pos
                handle_click(self, mx, my)

    def abandonner_combat(self):
        """Abandonne le combat en cours - défaite du joueur"""
        self.finished = True
        self.player_victory = False  # Défaite par abandon
        self.activer_menu_fin_combat(False)

    def update(self, dt_ms):
        # Mettre à jour les animations
        for u in self.unites:
            if u.anim:
                if u.anim.update(dt_ms):
                    u.anim = None
                    # Vérifier si c'est une explosion sacrée qui doit mourir après l'animation
                    if hasattr(u, 'explosion_sacree_pending') and u.explosion_sacree_pending:
                        u.explosion_sacree_pending = False
                        u.vivant = False
                        u.pv = 0

        # Vérifier fin
        joueurs = [u for u in self.unites if u.equipe == "joueur" and u.vivant]
        
        if self.versus_mode:
            # En mode versus, vérifier joueur2 au lieu d'ennemi
            adversaires = [u for u in self.unites if u.equipe == "joueur2" and u.vivant]
        else:
            adversaires = [u for u in self.unites if u.equipe == "ennemi" and u.vivant]
        
        if not joueurs or not adversaires:
            self.finished = True
            # Déterminer si c'est une victoire du joueur
            if joueurs and not adversaires:  # Joueur a des unités vivantes, adversaires non
                self.player_victory = True
                self.activer_menu_fin_combat(True)
            else:
                self.player_victory = False
                self.activer_menu_fin_combat(False)
            
            # Nettoyer le callback en mode hexarene
            if self.mode_hexarene:
                import unites
                unites.clear_kill_callback()
            return

        # Tour IA (seulement si pas en mode versus)
        if not self.versus_mode and self.tour == "ennemi":
            if not self.ia_busy:
                adversaires_courants = [u for u in self.unites if u.equipe == "ennemi" and u.vivant]
                self.ia_queue = adversaires_courants[:]
                self.ia_index = 0
                self.ia_busy = True
                self.ia_timer_ms = 0

            if self.ia_busy and self.ia_index < len(self.ia_queue):
                self.ia_timer_ms -= dt_ms
                if self.ia_timer_ms <= 0:
                    e = self.ia_queue[self.ia_index]
                    joueurs_courants = [u for u in self.unites if u.equipe == "joueur" and u.vivant]
                    
                    # Mémoriser l'état avant l'action IA
                    attaques_avant = e.attaque_restantes if hasattr(e, 'attaque_restantes') else 0
                    position_avant = e.pos
                    ennemis_vivants_avant = len([u for u in self.unites if u.equipe != e.equipe and u.vivant])
                    
                    # Protection contre les boucles infinies : compteur de tentatives
                    if not hasattr(e, '_ia_tentatives_tour'):
                        e._ia_tentatives_tour = 0
                    
                    e._ia_tentatives_tour += 1
                    
                    if self.ia_strategy:
                        self.ia_strategy(e, joueurs_courants, self.unites)
                    
                    # Vérifier l'état après l'action IA
                    attaques_apres = e.attaque_restantes if hasattr(e, 'attaque_restantes') else 0
                    position_apres = e.pos
                    ennemis_vivants_apres = len([u for u in self.unites if u.equipe != e.equipe and u.vivant])
                    
                    # Conditions pour continuer :
                    # 1. L'unité a encore des attaques
                    # 2. Elle en avait avant (peut encore agir)
                    # 3. Elle est vivante
                    # 4. Pas trop de tentatives (protection contre boucles infinies)
                    peut_continuer = (attaques_apres > 0 and 
                                    attaques_avant > 0 and 
                                    e.vivant and 
                                    e._ia_tentatives_tour < 10)  # Max 10 actions par tour
                    
                    if peut_continuer:
                        # Détecter si l'IA a fait quelque chose :
                        # 1. A utilisé une attaque (même si regagnée par un passif)
                        # 2. A bougé
                        # 3. A tué un ennemi (important pour lumière vengeresse !)
                        action_effectuee = (attaques_apres < attaques_avant or  # Attaque utilisée nette
                                          position_apres != position_avant or   # A bougé
                                          ennemis_vivants_apres < ennemis_vivants_avant)  # A tué quelqu'un
                        
                        if action_effectuee:
                            # Rester sur la même unité pour qu'elle continue à agir
                            if hasattr(e, '_derniere_position'):
                                e._derniere_position = e.pos  # Mettre à jour la position
                            print(f"IA continue: {type(e).__name__} a {attaques_apres} attaque(s) restante(s)")
                            pass  # Ne pas incrémenter ia_index
                        else:
                            # L'IA n'a rien fait, passer à l'unité suivante pour éviter la boucle
                            print(f"IA bloquée sur {type(e).__name__} - passage à l'unité suivante")
                            e._ia_tentatives_tour = 0  # Reset pour le prochain tour
                            self.ia_index += 1
                    else:
                        # Passer à l'unité suivante
                        e._ia_tentatives_tour = 0  # Reset pour le prochain tour
                        self.ia_index += 1
                    
                    self.ia_timer_ms = self.ia_delay_between_actions
            else:
                self.changer_tour()
                self.ia_busy = False
                self.ia_queue = []
                self.ia_index = 0
                self.ia_timer_ms = 0

    def est_case_vide(self, pos, toutes_unites=None):
        """Renvoie True si aucune unité vivante n'occupe la case pos."""
        if toutes_unites is None:
            toutes_unites = self.unites
        return all(u.pos != pos or not u.vivant for u in toutes_unites)

    def changer_tour(self):
        """Passe au tour suivant et réinitialise les actions/compétences passives."""
        # Appeler fin_tour pour toutes les unités de l'équipe qui termine son tour
        for u in self.unites:
            if u.equipe == self.tour and u.vivant and hasattr(u, 'fin_tour'):
                u.fin_tour()
        
        # Gérer la combustion différée en fin de tour ennemi
        if self.tour == "ennemi":
            for u in self.unites:
                if u.vivant and hasattr(u, 'fin_tour_ennemi'):
                    u.fin_tour_ennemi(self.unites)
        
        if getattr(self, 'versus_mode', False):
            # En mode versus, alterner entre "joueur" et "joueur2"
            self.tour = "joueur2" if self.tour == "joueur" else "joueur"
        else:
            # Mode normal : alterner entre "joueur" et "ennemi"
            self.tour = "ennemi" if self.tour == "joueur" else "joueur"
        
        reset_actions_tour(self)

    def activer_menu_fin_combat(self, victoire):
        """Active le menu de fin de combat avec les récompenses"""
        self.show_end_menu = True
        self.end_menu_processed = True  # Marquer comme traité pour éviter la ré-activation
        self.victoire = victoire
        
        # Calculer les récompenses basées sur la victoire et le mode de jeu
        if victoire:
            self.recompenses = self.calculer_recompenses()
        else:
            # Récompenses minimales en cas de défaite
            self.recompenses = {"pa": 1, "cp": 0, "unites": []}
        
        # Sauvegarder les récompenses
        self.sauvegarder_recompenses()

    def calculer_recompenses(self):
        """Calcule les récompenses basées sur le mode de jeu et la performance"""
        recompenses = {"pa": 0, "cp": 0, "unites": []}
        
        # Base des récompenses selon le mode
        if self.mode_hexarene:
            # HexArène donne plus de PA
            recompenses["pa"] = 5
            recompenses["cp"] = 2
        elif self.versus_mode:
            # Mode versus donne des récompenses équilibrées
            recompenses["pa"] = 3
            recompenses["cp"] = 3
        else:
            # Mode campagne - récompenses selon le niveau
            recompenses["pa"] = 4
            recompenses["cp"] = 1
        
        # Bonus selon les unités survivantes
        joueur_unites = [u for u in self.unites if u.equipe == "joueur" and u.vivant]
        bonus_survie = len(joueur_unites)
        recompenses["pa"] += bonus_survie
        
        # Parfois une nouvelle unité (chance de 30%)
        import random
        if random.random() < 0.3:
            unites_possibles = ["Guerrier", "Archer", "Mage"]
            nouvelle_unite = random.choice(unites_possibles)
            recompenses["unites"].append(nouvelle_unite)
        
        return recompenses

    def sauvegarder_recompenses(self):
        """Sauvegarde les récompenses dans le fichier de sauvegarde"""
        try:
            from sauvegarde import charger, sauvegarder
            progression = charger()
            
            # Ajouter les récompenses à la progression
            progression["pa"] = progression.get("pa", 0) + self.recompenses["pa"]
            progression["cp"] = progression.get("cp", 0) + self.recompenses["cp"]
            
            # Ajouter les nouvelles unités
            if "unites_dispo" not in progression:
                progression["unites_dispo"] = []
            progression["unites_dispo"].extend(self.recompenses["unites"])
            
            sauvegarder(progression)
            print(f"Récompenses sauvegardées: {self.recompenses}")
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des récompenses: {e}")

    def get_titre_fin_combat(self):
        """Retourne le titre approprié pour le menu de fin de combat"""
        statut = "Victoire" if self.victoire else "Défaite"
        
        if self.mode_hexarene:
            # Mode HexArène
            if self.hexarene_mode_type == "faction":
                return f"{statut} - HexArène {self.faction_hexarene}"
            else:
                return f"{statut} - HexArène Libre"
        elif self.versus_mode:
            # Mode Versus
            gagnant = "Joueur 1" if self.victoire else "Joueur 2"
            return f"{statut} - {gagnant}"
        else:
            # Mode Campagne
            if self.chapitre_nom and self.niveau_nom:
                return f"{statut} - {self.chapitre_nom} {self.niveau_nom}"
            else:
                return f"{statut} - Campagne"
        self.selection = None
        self.deplacement_possibles = {}

    # ...reste du code inchangé...
