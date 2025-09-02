def sangsue(self):
    """Le vampire récupère autant de PV que de dégâts infligés."""
    self.pv += self.dmg

# Dictionnaire des compétences (nom -> description)
COMPETENCES = {
    "sangsue": "Augmente sa vie du nombre de dégâts infligés."
}
