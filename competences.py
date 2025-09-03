def sangsue(self):
    """Le vampire récupère autant de PV que de dégâts infligés."""
    self.pv += self.dmg

def zombification(self, cible):
    """Transforme l'unite morte en zombie sous le contrôle du joueur de l'attaquant"""
    if not cible.vivant and cible.nom != "Zombie":
        from unites import Zombie  # import local pour éviter l'import circulaire
        
        # Transformer directement la cible en zombie
        cible.equipe = self.equipe  # Même équipe que l'attaquant
        cible.nom = "Zombie"
        cible.pv = 8  # Stats du zombie
        cible.dmg = 4
        cible.mv = 1
        cible.pm = 0
        cible.tier = 2
        cible.prix = 10
        cible.comp = "zombification"  # Les zombies peuvent aussi zombifier
        cible.vivant = True
        cible.a_attaque = True

# Dictionnaire des compétences (nom -> description)
COMPETENCES = {
    "sangsue": "Augmente sa vie du nombre de dégâts infligés.",
    "zombification": "Transforme l'unite ennemie morte en zombie"
}
