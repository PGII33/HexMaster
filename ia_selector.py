import random
from unites_liste import CLASSES_UNITES


class IASelector:
    def __init__(self, mode, **kwargs):
        self.mode = mode
        self.kwargs = kwargs

    def select_units(self):
        """Sélectionne automatiquement des unités pour l'IA"""
        if self.mode == "hexarene":
            return self._select_hexarene()
        elif self.mode == "hexarene_faction":
            return self._select_hexarene_faction()
        elif self.mode == "hexarene_libre":
            return self._select_hexarene_libre()
        elif self.mode == "versus":
            return self._select_versus()
        elif self.mode == "mixte":
            return self._select_mixte()
        else:
            return []

    def _select_hexarene_faction(self):
        """Sélection pour HexArène Mode Faction : même faction que le joueur, seulement tier 3-4, variété maximale"""
        player_cp = self.kwargs.get("player_cp", 5)
        player_faction = self.kwargs.get("player_faction", "Morts-Vivants")

        # L'IA a un budget généreux pour prendre que du haut tier
        ia_cp = player_cp * 2  # Budget doublé pour permettre plus d'unités tier 3-4
        # Limite par les cellules disponibles, minimum tier 3
        max_units = min(24, ia_cp // 3)

        # Unités de tier 3-4 uniquement pour la faction du joueur
        units_tier3_4 = []
        for cls in CLASSES_UNITES:
            tmp = cls("ennemi", (0, 0))
            if tmp.get_faction() == player_faction and tmp.get_tier() >= 3:
                units_tier3_4.append(cls)

        if not units_tier3_4:
            # Fallback si pas d'unités tier 3-4 dans cette faction
            return self._select_hexarene_faction_fallback(player_faction, ia_cp)

        # Sélection pour maximiser la variété tout en restant dans les tiers élevés
        selected = []
        cp_used = 0
        units_available = units_tier3_4[:]

        # Prioriser la variété : prendre une de chaque type d'abord
        for cls in units_available:
            if cp_used + cls("ennemi", (0, 0)).get_tier() <= ia_cp and len(selected) < max_units:
                selected.append(cls)
                cp_used += cls("ennemi", (0, 0)).get_tier()
                units_available.remove(cls)

        # Compléter avec des doublons si nécessaire et si budget/espace le permet
        while units_available and cp_used < ia_cp and len(selected) < max_units:
            cls = self._choose_smart_unit(units_available, ia_cp - cp_used)
            if cp_used + cls("ennemi", (0, 0)).get_tier() <= ia_cp:
                selected.append(cls)
                cp_used += cls("ennemi", (0, 0)).get_tier()
            else:
                break

        return selected

    def _select_hexarene_faction_fallback(self, player_faction, ia_cp):
        """Fallback si pas d'unités tier 3-4 dans la faction"""
        units_faction = []
        for cls in CLASSES_UNITES:
            tmp = cls("ennemi", (0, 0))
            if tmp.get_faction() == player_faction:
                units_faction.append(cls)

        # Prendre les meilleures unités disponibles
        selected = []
        cp_used = 0
        max_units = min(24, ia_cp // 2)  # Plus flexible sur le tier

        # Trier par tier décroissant
        units_faction.sort(key=lambda cls: cls(
            "ennemi", (0, 0)).get_tier(), reverse=True)

        for cls in units_faction:
            if cp_used + cls("ennemi", (0, 0)).get_tier() <= ia_cp and len(selected) < max_units:
                selected.append(cls)
                cp_used += cls("ennemi", (0, 0)).get_tier()

        return selected

    def _select_hexarene_libre(self):
        """Sélection pour HexArène Mode Libre : toutes factions, seulement tier 3-4, variété maximale"""
        player_cp = self.kwargs.get("player_cp", 5)

        # Budget généreux pour l'IA
        ia_cp = player_cp * 2  # Budget doublé
        max_units = min(24, ia_cp // 3)  # Limite par les cellules disponibles

        # Toutes les unités tier 3-4 de toutes factions
        units_tier3_4 = []
        factions_dict = {}

        for cls in CLASSES_UNITES:
            tmp = cls("ennemi", (0, 0))
            if tmp.get_tier() >= 3:
                units_tier3_4.append(cls)
                if tmp.get_faction() not in factions_dict:
                    factions_dict[tmp.get_faction()] = []
                factions_dict[tmp.get_faction()].append(cls)

        if not units_tier3_4:
            # Fallback : prendre les meilleures unités disponibles
            return self._select_hexarene_libre_fallback(ia_cp)

        selected = []
        cp_used = 0

        # Stratégie : prendre au moins une unité de chaque faction si possible
        factions = list(factions_dict.keys())

        # Tour 1 : Une unité de chaque faction
        for faction in factions:
            if cp_used >= ia_cp or len(selected) >= max_units:
                break
            faction_units = factions_dict[faction]
            # Prioriser tier 4, puis tier 3
            faction_units.sort(key=lambda cls: cls(
                "ennemi", (0, 0)).get_tier(), reverse=True)

            for cls in faction_units:
                if cp_used + cls("ennemi", (0, 0)).get_tier() <= ia_cp:
                    selected.append(cls)
                    cp_used += cls("ennemi", (0, 0)).get_tier()
                    break

        # Tour 2 : Compléter avec les meilleures unités restantes
        remaining_units = [cls for cls in units_tier3_4 if cls not in selected]
        while remaining_units and cp_used < ia_cp and len(selected) < max_units:
            cls = self._choose_smart_unit(remaining_units, ia_cp - cp_used)
            if cp_used + cls("ennemi", (0, 0)).get_tier() <= ia_cp:
                selected.append(cls)
                cp_used += cls("ennemi", (0, 0)).get_tier()
                remaining_units.remove(cls)
            else:
                break

        return selected

    def _select_hexarene_libre_fallback(self, ia_cp):
        """Fallback pour mode libre si pas d'unités tier 3-4"""
        all_units = CLASSES_UNITES[:]
        all_units.sort(key=lambda cls: cls(
            "ennemi", (0, 0)).get_tier(), reverse=True)

        selected = []
        cp_used = 0
        max_units = min(24, ia_cp // 2)

        for cls in all_units:
            if cp_used + cls("ennemi", (0, 0)).get_tier() <= ia_cp and len(selected) < max_units:
                selected.append(cls)
                cp_used += cls("ennemi", (0, 0)).get_tier()

        return selected

    def _choose_smart_unit(self, available_units, remaining_cp):
        """Choisit intelligemment une unité selon l'espace CP restant"""
        # Prioriser les unités qui utilisent bien l'espace restant
        tier_weights = {}
        for cls in available_units:
            tier = cls("ennemi", (0, 0)).get_tier()
            # Plus le tier est élevé, plus il a de poids (mais sans dépasser le CP)
            if tier <= remaining_cp:
                weight = tier * 2  # Favoriser les tiers élevés
                if tier == 4:  # Bonus pour les tier 4 (boss)
                    weight *= 1.5
                elif tier == 3:  # Bonus pour les tier 3
                    weight *= 1.3
                tier_weights[cls] = weight

        if not tier_weights:
            return random.choice(available_units)

        # Sélection pondérée
        total_weight = sum(tier_weights.values())
        rand = random.uniform(0, total_weight)
        current = 0

        for cls, weight in tier_weights.items():
            current += weight
            if rand <= current:
                return cls

        return random.choice(list(tier_weights.keys()))

    def _select_hexarene(self):
        """Sélection pour HexArène (ancienne méthode, conservée pour compatibilité)"""
        return self._select_hexarene_faction()

    def _select_versus(self):
        """Sélection pour mode Versus (même règles que le joueur)"""
        cp_disponible = self.kwargs.get("cp_disponible", 5)

        # Toutes les unités disponibles
        units_dispo = CLASSES_UNITES[:]

        selected = []
        cp_used = 0

        while cp_used < cp_disponible and len(selected) < 10:
            available = [cls for cls in units_dispo
                         if cp_used + cls("ennemi", (0, 0)).get_tier() <= cp_disponible]
            if not available:
                break

            cls = random.choice(available)
            selected.append(cls)
            cp_used += cls("ennemi", (0, 0)).get_tier()

        return selected

    def _select_mixte(self):
        """Sélection pour mode Mixte"""
        cp_disponible = self.kwargs.get("cp_disponible", 5)

        # Mélange de toutes les factions
        units_dispo = CLASSES_UNITES[:]

        selected = []
        cp_used = 0

        while cp_used < cp_disponible and len(selected) < 12:
            available = [cls for cls in units_dispo
                         if cp_used + cls("ennemi", (0, 0)).get_tier() <= cp_disponible]
            if not available:
                break

            cls = random.choice(available)
            selected.append(cls)
            cp_used += cls("ennemi", (0, 0)).get_tier()

        return selected

    def _select_versus(self):
        """Sélection pour mode Versus (même règles que le joueur)"""
        cp_disponible = self.kwargs.get("cp_disponible", 5)

        # Toutes les unités disponibles
        units_dispo = CLASSES_UNITES[:]

        selected = []
        cp_used = 0

        while cp_used < cp_disponible and len(selected) < 10:
            available = [cls for cls in units_dispo
                         if cp_used + cls("ennemi", (0, 0)).get_tier() <= cp_disponible]
            if not available:
                break

            cls = random.choice(available)
            selected.append(cls)
            cp_used += cls("ennemi", (0, 0)).get_tier()

        return selected

    def _select_mixte(self):
        """Sélection pour mode Mixte"""
        cp_disponible = self.kwargs.get("cp_disponible", 5)

        # Mélange de toutes les factions
        units_dispo = CLASSES_UNITES[:]

        selected = []
        cp_used = 0

        while cp_used < cp_disponible and len(selected) < 12:
            available = [cls for cls in units_dispo
                         if cp_used + cls("ennemi", (0, 0)).get_tier() <= cp_disponible]
            if not available:
                break

            cls = random.choice(available)
            selected.append(cls)
            cp_used += cls("ennemi", (0, 0)).get_tier()

        return selected
