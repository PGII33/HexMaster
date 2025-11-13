""" Module des unités du jeu HexaMaster """
#pylint: disable=line-too-long
from collections import deque
import animations
import competences as co
from utils_pos import est_a_portee

# Callback global pour gérer les kills (sera défini par le jeu si besoin)
_kill_callback = None


def set_kill_callback(callback):
    """Définit le callback à appeler quand une unité est tuée."""
    global _kill_callback
    _kill_callback = callback


def clear_kill_callback():
    """Supprime le callback de kill."""
    global _kill_callback
    _kill_callback = None


class Unite:
    """ Class to define a unite """
    def __init__(self, equipe, pos, pv, dmg, mv, tier, nom, faction, prix=None, comp=None, portee=1, pv_max=None, attaque_max=1):
        self.equipe = equipe
        self.pos = pos
        self.pv = pv
        self.pv_max = pv_max if pv_max is not None else pv
        self.dmg = dmg
        self.mv = mv
        self.pm = self.mv
        self.tier = tier
        self.nom = nom
        self.faction = faction
        self.portee = portee
        self.attaque_max = attaque_max
        self.attaque_restantes = attaque_max
        self.bouclier = 0
        # prix selon le nouveau système : Tier 1=20, Tier 2=80, Tier 3=200, Tier 4=non achetable
        if prix is not None:
            self.prix = prix
        else:
            if tier == 1:
                self.prix = 20
            elif tier == 2:
                self.prix = 80
            elif tier == 3:
                self.prix = 200
            elif tier == 4:
                self.prix = -1  # Non achetable (bloqué)
            else:
                self.prix = tier * 5  # Fallback pour autres tiers
        # comp doit être le nom de la compétence (string) ou None/""
        self.comp = comp or ""

        # Système de cooldown pour les compétences actives
        self.cooldown_actuel = 0  # Tours restants avant de pouvoir réutiliser la compétence
        # Cooldown maximum de la compétence
        self.cooldown_max = self.get_cooldown_competence()

        self.set_vivant(True)
        self.anim = None

    # ---------- Getters ----------
    def get_nom(self):
        """ get attribute nom """
        return self.nom

    def get_pv(self):
        """ get attribute pv """
        return self.pv

    def get_dmg(self):
        """ get attribute dmg """
        return self.dmg

    def get_mv(self):
        """ get attribute mv """
        return self.mv

    def get_pm(self):
        """ get attribute pm """
        return self.pm

    def get_bouclier(self):
        """ get attribute bouclier """
        return self.bouclier

    def get_attaque_max(self):
        """ get attribute attaque_max, it is the maximum number of attacks per turn """
        return self.attaque_max

    def get_attaque_restantes(self):
        """ get attribute attaque_restantes, it is the number of attacks left this turn """
        return self.attaque_restantes

    def get_tier(self):
        """ get attribute tier """
        return self.tier

    def get_prix(self):
        """ get attribute prix or "Bloqué" if prix < 0 """
        return "Bloqué" if self.prix < 0 else self.prix

    def get_faction(self):
        """ get attribute faction """
        return self.faction

    def get_equipe(self):
        """ get attribute equipe """
        return self.equipe

    def is_vivant(self):
        """ get attribute vivant """
        return self.vivant

    def has_competence(self):
        """ get True if the unit has a competence, False otherwise """
        return bool(self.comp)

    def get_cooldown_competence(self):
        """ get the cooldown max of the competence """
        if not self.comp:
            return 0
        return co.get_cooldown(self.comp)

    def get_competence(self):
        """ get attribute comp """
        return self.comp

    def get_portee(self):
        """ get attribute portee """
        return self.portee

    def get_pv_max(self):
        """ get attribute pv_max """
        return self.pv_max

    def get_attaque_totale(self):
        """Calcule l'attaque totale incluant les boosts temporaires."""
        attaque_base = self.dmg

        # Ajouter les boosts attaque (ba)
        ba_benediction = getattr(self, 'ba_benediction', 0)
        ba_commandement = getattr(self, 'ba_commandement', 0)
        ba_aura_sacree = getattr(self, 'ba_aura_sacree', 0)
        ba_rage = getattr(self, 'ba_rage', 0)

        return attaque_base + ba_benediction + ba_commandement + ba_aura_sacree + ba_rage

    def get_buff(self, nom_buff):
        """ Retourne 1 si le buff est appliqué à l'unité, 0 sinon. Lève une erreur si le buff est inconnu."""
        return co.get_buff(nom_buff)

    def set_vivant(self, etat):
        """ set attribute vivant to etat """
        self.vivant = etat

    # ---------- Logique ----------
    def reset_actions(self):
        """Réinitialise les PM et attaques restantes au début du tour."""
        self.attaque_restantes = max(self.attaque_max, self.attaque_restantes)
        self.pm = self.mv

        # Appliquer l'effet venin incapacitant si l'unité a été empoisonnée
        if hasattr(self, 'venin_incapacite'):
            self.pm = 0  # L'unité ne peut plus se déplacer
            # TODO:
            print(
                f"🐍 {self.nom} est incapacité par le venin ! Aucun mouvement possible ce tour.")

        # Appliquer l'effet divertissement si l'unité a été divertie
        if hasattr(self, 'diverti'):
            self.attaque_restantes = max(0, self.attaque_restantes - 1)
            print(f"{self.nom} est diverti et perd 1 attaque!")

    def cases_accessibles(self, toutes_unites, q_range=None, r_range=None):
        """ Retourne un dictionnaire des cases accessibles avec leur coût en PM."""
        if self.pm <= 0:
            return {}

        # Limites par défaut si non spécifiées
        if q_range is None:
            q_range = range(-1, 7)
        if r_range is None:
            r_range = range(-1, 7)

        if self.comp == "fantomatique":
            return co.cases_fantomatiques(self, toutes_unites, q_range, r_range)

        accessibles = {}
        file = deque([(self.pos, 0)])
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
        occupees = {u.pos for u in toutes_unites if u.is_vivant()
                    and u != self}

        while file:
            (q, r), cout = file.popleft()
            if cout >= self.pm:
                continue
            for dq, dr in directions:
                new_pos = (q+dq, r+dr)
                new_q, new_r = new_pos

                # VÉRIFIER QUE LA NOUVELLE POSITION EST DANS LA GRILLE
                if new_q not in q_range or new_r not in r_range:
                    continue

                new_cout = cout + 1
                if new_pos in occupees:
                    continue
                if new_pos == self.pos:
                    continue
                if new_pos not in accessibles or new_cout < accessibles[new_pos]:
                    accessibles[new_pos] = new_cout
                    file.append((new_pos, new_cout))
        return accessibles

    # ---------- Combat ----------
    def subir_degats(self, degats):
        """Subit des dégâts en tenant compte du vol, bouclier et de l'armure de pierre."""

        # Appliquer vol si l'unité a cette compétence (avant tout le reste)
        if self.comp == "vol":
            degats = co.vol(self, degats)

        # Appliquer l'armure de pierre si l'unité a cette compétence
        if self.comp == "armure de pierre":
            degats = co.armure_de_pierre(degats)

        # Le bouclier absorbe d'abord les dégâts (après armure de pierre)
        if self.bouclier > 0:
            if degats <= self.bouclier:
                # Le bouclier absorbe tous les dégâts
                self.bouclier -= degats
                # Retourner les dégâts réellement subis (après armure)
                return degats
            else:
                # Le bouclier absorbe une partie, le reste va aux PV
                degats_aux_pv = degats - self.bouclier
                self.bouclier = 0
                # Les dégâts restants vont aux PV
                self.pv -= degats_aux_pv
        else:
            # Les dégâts vont directement aux PV
            self.pv -= degats
        return degats  # Retourner les dégâts réellement subis (après armure)

    def appliquer_degats_avec_protection(self, cible, degats, toutes_unites):  # TODO
        """Applique les dégâts en tenant compte de la protection."""
        # La fonction protection gère maintenant tout le processus
        return co.protection(cible, degats, toutes_unites)

    def attaquer(self, autre, toutes_unites=None):
        """Applique l'animation et les dégâts séparément."""
        if toutes_unites is None:
            toutes_unites = []

        if self.attaque_restantes > 0 and est_a_portee(self.pos, autre.pos, self.get_portee()) and autre.is_vivant():
            self.attaque_restantes -= 1

            # Animation
            self.anim = animations.Animation("attack", 250, self, cible=autre)

            # Gestion spéciale pour explosion sacrée
            if self.comp == "explosion sacrée":
                # Le Fanatique inflige ses PV en dégâts et se sacrifie après l'animation
                co.explosion_sacrée(self, toutes_unites, autre)
            else:
                # Attaque normale - calculer les dégâts avec boosts
                degats_totaux = self.get_attaque_totale()
                if hasattr(self, 'ba_commandement'):
                    self.ba_commandement = 0  # Réinitialiser après utilisation

                # Appliquer la protection si applicable
                degats_infliges = self.appliquer_degats_avec_protection(
                    autre, degats_totaux, toutes_unites)

                # Compétence sangsue après l'attaque (avec les vrais dégâts)
                if self.comp == "sangsue":
                    co.sangsue(self, degats_infliges)

                # Combustion différée : marquer la cible
                if self.comp == "combustion différée" and autre.is_vivant():
                    co.combustion_differee(self, autre)

            # Vérification de mort commune pour tous les types d'attaque
            cible_tuée = False
            if autre.pv <= 0:
                # Passer la liste complète des unités
                result = autre.mourir(toutes_unites)
                cible_tuée = result  # True si l'unité était vivante et est maintenant morte

            # Compétences après l'attaque (quand on sait si la cible est tuée)
            if self.comp == "lumière vengeresse" and cible_tuée:
                co.lumière_vengeresse(self, autre)

            if self.comp == "zombification" and cible_tuée:
                co.zombification(self, autre)

            # Rage : augmente l'attaque après chaque attaque
            if self.comp == "rage":
                co.rage(self)

            # Venin incapacitant : empêche la cible de se déplacer au prochain tour
            if self.comp == "venin incapacitant" and autre.is_vivant():
                co.venin_incapacitant(self, autre)

            # Sédition venimeuse : la cible attaque un ennemi adjacent
            if self.comp == "sédition venimeuse" and autre.is_vivant():
                co.sedition_venimeuse(self, autre, toutes_unites)

    def mourir(self, toutes_unites=None):
        """Gère la mort de l'unité et les compétences déclenchées.
        Retourne True si l'unité était vivante et est maintenant morte."""
        if self.is_vivant():
            # Si l'unité est sélectionnée dans le jeu, la désélectionner
            for jeu in [u for u in toutes_unites if hasattr(u, 'selection')]:
                if jeu.selection == self:
                    jeu.selection = None
                    jeu.deplacement_possibles = {}

            # Compétence de renaissance : tentative de résurrection avant la mort
            if self.comp == "renaissance":
                if co.renaissance(self, toutes_unites):
                    return False  # L'unité a été ressuscitée, elle n'est pas morte

            self.set_vivant(False)

            # Appeler le callback de kill si défini (pour le mode hexarene)
            global _kill_callback
            if _kill_callback:
                _kill_callback(self)

            # Compétences déclenchées à la mort (sauf explosion sacrée qui est gérée dans attaquer)
            if self.comp == "tas d'os":
                co.tas_d_os(self)
            # Si c'est un marionettiste qui meurt, libérer toutes ses unités manipulées
            elif self.comp == "manipulation":
                co.liberer_toutes_unites_manipulees_par(self, toutes_unites)

            return True  # Unité effectivement tuée
        return False  # Unité déjà morte

    def debut_tour(self, toutes_unites, plateau, q_range=None, r_range=None):
        """À appeler au début du tour de l'unité pour déclencher les compétences passives."""

        # Réduction du cooldown des compétences actives
        if self.cooldown_actuel > 0:
            self.cooldown_actuel -= 1

        # Compétences passives
        if self.comp == "nécromancie":
            co.nécromancie(self, toutes_unites, plateau, q_range, r_range)
        elif self.comp == "invocation":
            co.invocation(self, toutes_unites, plateau, q_range, r_range)
        elif self.comp == "bouclier de la foi":
            co.bouclier_de_la_foi(self, toutes_unites)
        elif self.comp == "aura sacrée":
            co.aura_sacrée(self, toutes_unites)
        elif self.comp == "vague apaisante":
            co.vague_apaisante(self, toutes_unites)
        # La manipulation se déclenche en fin de tour, pas au début
        # Ajoute ici d'autres compétences passives si besoin

    def fin_tour(self, toutes_unites):
        """À appeler en fin de tour de l'unité pour déclencher les compétences de fin de tour."""
        # Compétence d'enracinement : régénère si l'unité n'a pas bougé
        if self.comp == "enracinement":
            co.enracinement(self)
        # Compétence de divertissement : réduit les attaques des ennemis adjacents
        elif self.comp == "divertissement":
            co.divertissement(self, toutes_unites)
        # Compétence de manipulation : contrôle les unités avec ≤4 PV
        elif self.comp == "manipulation":
            co.manipulation(self, toutes_unites)

    def fin_tour_ennemi(self, toutes_unites):
        """À appeler en fin de tour ennemi pour gérer la combustion différée."""
        # Gérer la combustion différée (compte à rebours en fin de tour ennemi)
        if hasattr(self, 'combustion_tours_restants'):
            co.gerer_combustion_differee(self, toutes_unites)

    def a_competence_active(self):
        """Retourne True si l'unité a une compétence active utilisable (pas en cooldown)."""
        if not self.comp:
            return False
        if not co.est_competence_active(self.comp):
            return False
        return self.cooldown_actuel <= 0  # Utilisable seulement si pas en cooldown

    def possede_competence_active(self):
        """Retourne True si l'unité possède une compétence active (indépendamment du cooldown)."""
        if not self.comp:
            return False
        return co.est_competence_active(self.comp)

    def get_cooldown_info(self):
        """Retourne des informations sur le cooldown de la compétence."""
        if not self.comp or not co.est_competence_active(self.comp):
            return None
        return {
            "actuel": self.cooldown_actuel,
            "max": self.cooldown_max,
            "disponible": self.cooldown_actuel <= 0
        }

    def get_competence_status(self):
        """Retourne le statut de la compétence pour l'affichage."""
        if not self.comp:
            return "Aucune compétence"

        if not co.est_competence_active(self.comp):
            return f"{self.comp} (passive)"

        if self.cooldown_actuel <= 0:
            return f"{self.comp} (prêt)"
        else:
            return f"{self.comp} ({self.cooldown_actuel} tours)"

    def utiliser_competence(self, cible=None, toutes_unites=None):
        """Utilise la compétence active de l'unité."""
        # Vérifier les conditions d'utilisation
        attaque_necessaire = co.comp_attaque

        if (self.a_competence_active() and
            (not attaque_necessaire or self.attaque_restantes > 0) and
                self.cooldown_actuel <= 0):

            success = co.utiliser_competence_active(
                self, self.comp, cible, toutes_unites)
            if success:
                # Activer le cooldown et marquer comme utilisée ce tour
                self.cooldown_actuel = self.cooldown_max

                # Seules certaines compétences ne consomment pas d'attaque
                if self.comp in co.comp_attaque:
                    self.attaque_restantes -= 1
            return success
        return False
