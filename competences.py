def sangsue(self):
    """Le vampire récupère autant de PV que de dégâts infligés."""
    self.pv += self.dmg

def zombification(self, cible):
    """Transforme l'unite morte en zombie sous le contrôle du joueur de l'attaquant"""
    from unites import Zombie_BASE
    if not cible.vivant and cible.nom != "Zombie":        
        # Transformer la cible en Zombie_BASE
        cible.__class__ = Zombie_BASE
        cible.__init__(self.equipe, cible.pos)
        cible.pm = 0
        cible.a_attaque = True
        cible.comp = "zombification"


def tas_d_os(self):
    from unites import Tas_D_Os
    if not self.vivant:
        self.__class__ = Tas_D_Os
        self.__init__(self.equipe, self.pos)

# Dictionnaire des compétences (nom -> description)
COMPETENCES = {
    "sangsue": "Augmente sa vie du nombre de dégâts infligés.",
    "zombification": "Transforme l'unite ennemie tuée en zombie"
}
