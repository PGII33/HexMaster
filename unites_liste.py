""" Fichier définissant toutes les unités. Ce fichier est voué à être remplacé """
# pylint: disable=missing-class-docstring disable=invalid-name
from unites import Unite

# Morts-Vivants

class Tas_D_Os(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Tas d'Os", pv=1, dmg=0,
                         mv=0, tier=0, faction="Morts-Vivants", attaque_max=0)


class Goule(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Goule", pv=16,
                         dmg=2, mv=1, tier=1, faction="Morts-Vivants")


class Squelette(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Squelette", pv=3, dmg=5,
                         mv=2, tier=1, comp="tas d'os", faction="Morts-Vivants")


class Spectre(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Spectre", pv=5, dmg=3, mv=1,
                         tier=1, comp="fantomatique", faction="Morts-Vivants")


class Zombie(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Zombie", pv=10, dmg=2, mv=2,
                         tier=2, comp="zombification", faction="Morts-Vivants")


class Vampire(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Vampire", pv=8, dmg=3,
                         mv=2, tier=2, comp="sangsue", faction="Morts-Vivants")


class Liche(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Liche", pv=9, dmg=1, mv=2,
                         tier=3, comp="nécromancie", faction="Morts-Vivants", portee=2)


class Archliche(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Archliche", pv=18, dmg=1, mv=2,
                         tier=4, comp="invocation", faction="Morts-Vivants", portee=3)


# Religieux

class Missionnaire(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Missionnaire",
                         pv=12, dmg=2, mv=3, tier=1, faction="Religieux")


class Clerc(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Clerc", pv=5, dmg=0, mv=1,
                         tier=1, faction="Religieux", comp="soin", attaque_max=0)


class Fanatique(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Fanatique", pv=10, dmg=0,
                         mv=3, tier=1, faction="Religieux", comp="explosion sacrée")


class Esprit_Saint(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Esprit Saint", pv=7, dmg=1,
                         mv=2, tier=2, faction="Religieux", comp="bouclier de la foi")


class Paladin(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Paladin", pv=13, dmg=3,
                         mv=2, tier=2, faction="Religieux", comp="bénédiction")


class Ange(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Ange", pv=12, dmg=6, mv=2, tier=3,
                         faction="Religieux", comp="lumière vengeresse", portee=2)


class ArchAnge(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="ArchAnge", pv=20, dmg=13, mv=3,
                         tier=4, faction="Religieux", comp="aura sacrée", portee=2)


# Élémentaires

class Cristal(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Cristal", pv=10, dmg=0,
                         mv=0, tier=0, faction="Élémentaires", attaque_max=0)


class Esprit(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Esprit", pv=6,
                         dmg=3, mv=3, tier=1, faction="Élémentaires")


class Driade(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Driade", pv=10, dmg=2, mv=1,
                         tier=1, faction="Élémentaires", comp="enracinement")


class Gnome(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Gnome", pv=5, dmg=2, mv=2,
                         tier=1, faction="Élémentaires", comp="cristalisation")


class Golem(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Golem", pv=12, dmg=4, mv=1,
                         tier=2, faction="Élémentaires", comp="armure de pierre")


class Ondine(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Ondine", pv=7, dmg=2, mv=2,
                         tier=2, faction="Élémentaires", comp="vague apaisante")


class Ifrit(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Ifrit", pv=25, dmg=3, mv=2,
                         tier=3, faction="Élémentaires", comp="combustion différée")


class Phenix(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Phénix", pv=15, dmg=6,
                         mv=3, tier=4, faction="Élémentaires", comp="renaissance")


# Royaume

class Cheval(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Cheval", pv=1, dmg=0,
                         mv=3, tier=0, faction="Royaume", attaque_max=0)


class Guerrier(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Guerrier",
                         pv=10, dmg=4, mv=2, tier=1, faction="Royaume")


class Archer(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Archer", pv=6, dmg=2, mv=1,
                         tier=1, faction="Royaume", comp="pluie de flèches", portee=2)


class Cavalier(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Cavalier", pv=8, dmg=3,
                         mv=3, tier=1, faction="Royaume", comp="monture libéré")


class Bouffon(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Bouffon", pv=9, dmg=1,
                         mv=2, tier=2, faction="Royaume", comp="divertissement")


class Garde_Royal(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Garde royal", pv=15, dmg=3,
                         mv=1, tier=2, faction="Royaume", comp="protection")


class Roi(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Roi", pv=12, dmg=4,
                         mv=2, tier=3, faction="Royaume", comp="commandement")


class Marionettiste(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Marionettiste", pv=14, dmg=3,
                         mv=2, tier=4, faction="Royaume", comp="manipulation")


# Chimères

class Harpie(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Harpie", pv=7,
                         dmg=3, mv=3, tier=1, faction="Chimères")


class Centaure(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Centaure", pv=6, dmg=2, mv=2,
                         tier=1, faction="Chimères", comp="tir précis", portee=2)


class Griffon(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Griffon", pv=8, dmg=4,
                         mv=3, tier=1, faction="Chimères", comp="vol")


class Lamia(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Lamia", pv=11, dmg=3, mv=2,
                         tier=2, faction="Chimères", comp="sédition venimeuse")


class Loup_Garou(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Loup-Garou", pv=12,
                         dmg=4, mv=2, tier=2, faction="Chimères", comp="rage")


class Manticore(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Manticore", pv=13, dmg=5,
                         mv=2, tier=3, faction="Chimères", comp="venin incapacitant")


class Basilic(Unite):
    def __init__(self, equipe, pos):
        super().__init__(equipe, pos, nom="Basilic", pv=16, dmg=7,
                         mv=2, tier=4, faction="Chimères", comp="regard mortel")


# Liste des classes utilisables
CLASSES_UNITES = [
    # Morts-Vivants
    Goule, Squelette, Spectre, Vampire, Zombie, Liche, Archliche,
    # Religieux
    Missionnaire, Clerc, Fanatique, Esprit_Saint, Paladin, Ange, ArchAnge,
    # Élémentaires
    Esprit, Driade, Gnome, Golem, Ondine, Ifrit, Phenix,
    # Royaume
    Guerrier, Archer, Cavalier, Bouffon, Garde_Royal, Roi, Marionettiste,
    # Chimères
    Harpie, Centaure, Griffon, Lamia, Loup_Garou, Manticore, Basilic
]
