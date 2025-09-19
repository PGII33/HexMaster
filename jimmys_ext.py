from random import *
from unites import *
import unites

class TADOS1(unites.Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="TADOS", pv=1, dmg=0, mv=0, tier=0, comp="nécromancie", faction="Morts-Vivants", attaque_max=0)

class Jimmy1(unites.Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Friendly Jimmy", pv=3, dmg=5, mv=2, tier=2, comp="boneful TADOS", faction="Morts-Vivants")

class TADOS2(unites.Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="méchant TADOS", pv=1, dmg=1, mv=0, tier=0, faction="Morts-Vivants")

class Jimmy2(unites.Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Angry Jimmy", pv=3, dmg=5, mv=2, tier=1, comp="angry TADOS", faction="Morts-Vivants")

class TADOS3(unites.Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Jimmy's TADOS", pv=1, dmg=1, mv=0, tier=0, comp="Jimmy's tas d'os", faction="Morts-Vivants")

class Jimmy3(unites.Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Jimmy's Jimmy", pv=3, dmg=5, mv=2, tier=1, comp="Jimmy's TADOS", faction="Morts-Vivants")

class Jimmy(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Jimmy", pv=3, dmg=5, mv=2, tier=0, comp="tas d'os", faction="Morts-Vivants")

class Jimmy4(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Better Jimmy", pv=3, dmg=5, mv=2, tier=2, comp="Jimmiest", faction="Morts-Vivants")

def liche_tados(self):
    """Transforme l'unité morte en tas d'os."""
    # Transformation en tas d'os : c'est une nouvelle unité vivante
    self.__class__ = TADOS1
    self.__init__(self.equipe, self.pos)

def mechant_tados(self):
    """Transforme l'unité morte en tas d'os."""
    # Transformation en tas d'os : c'est une nouvelle unité vivante
    self.__class__ = TADOS2
    self.__init__(self.equipe, self.pos)
    self.combustion_tours_restants = 2

def jimmy_tados(self):
    """Transforme l'unité morte en tas d'os."""
    # Transformation en tas d'os : c'est une nouvelle unité vivante
    self.__class__ = TADOS3
    self.__init__(self.equipe, self.pos)

def jimmyfication(self, cible):
    """Transforme l'unite morte en zombie sous le contrôle du joueur de l'attaquant"""
    from unites import Zombie_BASE
    if cible.nom == "Squelette":
        # Transformer la cible en Jimmy
        cible.__class__ = Jimmy
        cible.__init__(self.equipe, cible.pos)

def superjimmy(cible):
    jimmys = [Jimmy1, Jimmy2, Jimmy3]
    shuffle(jimmys)
    cible.__class__ = jimmys[0]
    cible.__init__(cible.equipe, cible.pos)
    return True

def jimmys_everywhere(self, toutes_unites):
    """Soigne les unités alliées adjacentes de 2 PV (comme bouclier de la foi mais avec soin)."""
    directions = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    q, r = self.pos

    for unite in toutes_unites:
        if unite.equipe == self.equipe and unite != self:
            unite_q, unite_r = unite.pos
            for dq, dr in directions:
                if (q + dq, r + dr) == (unite_q, unite_r):
                    # Soigner l'unité adjacente
                    jimmyfication(self, unite)

CLASSES_UNITES = [
    # Morts-Vivants
    Goule, Squelette, Spectre, Vampire, Zombie, Liche, Archliche, Jimmy1, Jimmy2, Jimmy3,
    # Religieux
    Missionnaire, Clerc, Fanatique, Esprit_Saint, Paladin, Ange, ArchAnge,
    # Élémentaires
    Esprit, Driade, Gnome, Golem, Ondine, Ifrit, Phénix,
    # Royaume
    Guerrier, Archer, Cavalier, Bouffon, Garde_Royal, Roi, Marionettiste,
    # Chimères
    Harpie, Centaure, Griffon, Lamia, Loup_Garou, Manticore, Basilic
]