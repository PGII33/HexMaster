# fichier: tuto.py
import ia
from jeu import Jeu

class Tuto:
    def __init__(self, screen):
        self.screen = screen

    def run_flow(self):
        # Ici, le tuto démarre une partie simple contre l’IA.
        return Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen
        )
