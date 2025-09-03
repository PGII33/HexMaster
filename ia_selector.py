import random
import unites

class IASelector:
    def __init__(self, mode, **kwargs):
        self.mode = mode
        self.kwargs = kwargs
    
    def select_units(self):
        """Sélectionne automatiquement des unités pour l'IA"""
        if self.mode == "hexarene":
            return self._select_hexarene()
        elif self.mode == "versus":
            return self._select_versus()
        elif self.mode == "mixte":
            return self._select_mixte()
        else:
            return []
    
    def _select_hexarene(self):
        """Sélection pour HexArène : 20% de CP en plus, +1 tier max"""
        player_cp = self.kwargs.get("player_cp", 5)
        player_max_tier = self.kwargs.get("player_max_tier", 1)
        
        ia_cp = int(player_cp * 1.2)  # 20% de plus
        ia_max_tier = min(4, player_max_tier + 1)  # +1 tier, max 4
        
        # Choisir une faction au hasard
        factions = ["Morts-Vivants"]  # Pour l'instant une seule faction
        faction_choisie = random.choice(factions)
        
        # Unités disponibles pour cette faction et tier max
        units_dispo = []
        for cls in unites.CLASSES_UNITES:
            tmp = cls("ennemi", (0,0))
            if tmp.faction == faction_choisie and tmp.tier <= ia_max_tier:
                units_dispo.append(cls)
        
        # Sélection aléatoire avec contrainte de CP
        selected = []
        cp_used = 0
        
        while cp_used < ia_cp and len(selected) < 14:
            available = [cls for cls in units_dispo 
                        if cp_used + cls("ennemi", (0,0)).tier <= ia_cp]
            if not available:
                break
            
            cls = random.choice(available)
            selected.append(cls)
            cp_used += cls("ennemi", (0,0)).tier
        
        return selected
    
    def _select_versus(self):
        """Sélection pour mode Versus (même règles que le joueur)"""
        cp_disponible = self.kwargs.get("cp_disponible", 5)
        
        # Toutes les unités disponibles
        units_dispo = unites.CLASSES_UNITES[:]
        
        selected = []
        cp_used = 0
        
        while cp_used < cp_disponible and len(selected) < 10:
            available = [cls for cls in units_dispo 
                        if cp_used + cls("ennemi", (0,0)).tier <= cp_disponible]
            if not available:
                break
            
            cls = random.choice(available)
            selected.append(cls)
            cp_used += cls("ennemi", (0,0)).tier
        
        return selected
    
    def _select_mixte(self):
        """Sélection pour mode Mixte"""
        cp_disponible = self.kwargs.get("cp_disponible", 5)
        
        # Mélange de toutes les factions
        units_dispo = unites.CLASSES_UNITES[:]
        
        selected = []
        cp_used = 0
        
        while cp_used < cp_disponible and len(selected) < 12:
            available = [cls for cls in units_dispo 
                        if cp_used + cls("ennemi", (0,0)).tier <= cp_disponible]
            if not available:
                break
            
            cls = random.choice(available)
            selected.append(cls)
            cp_used += cls("ennemi", (0,0)).tier
        
        return selected