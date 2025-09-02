import ia
from jeu import Jeu
import unites

class Tuto:
    def __init__(self, screen):
        self.screen = screen

    def run_flow(self):
        # Ici, le tuto démarre une partie simple contre l'IA.
        initial_player_units = [
            (unites.Squelette, (0, 0)),
            (unites.Vampire, (1, 0)),
        ]
        initial_enemy_units = [
            (unites.Squelette, (0, 2)),
            (unites.Goule, (1, 2)),
        ]
        return Jeu(
            ia_strategy=ia.cible_faible,
            screen=self.screen,
            initial_player_units=initial_player_units,
            initial_enemy_units=initial_enemy_units
        )
