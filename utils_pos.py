""" Geometrical utilities for hexagonal grid positions """
#pylint: disable=line-too-long
from typing import List, Tuple

def hex_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calcule la distance hexagonale entre deux positions"""
    q1, r1 = pos1
    q2, r2 = pos2
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

def est_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """Vérifie si deux positions sont adjacentes"""
    return hex_distance(pos1, pos2) == 1

def est_a_portee(pos_attaquant: Tuple[int, int], pos_cible: Tuple[int, int], portee: int) -> bool:
    """Vérifie si une cible est à portée d'attaque"""
    return hex_distance(pos_attaquant, pos_cible) <= portee

def get_unites_adjacentes(position: Tuple[int, int], unites: List['Unite']) -> List['Unite']:
    """Retourne les unités adjacentes à une position donnée"""
    return [u for u in unites if u.vivant and est_adjacent(position, u.pos)]

def get_unites_a_portee(position: Tuple[int, int], unites: List['Unite'], portee: int) -> List['Unite']:
    """Retourne les unités à portée d'une position donnée"""
    return [u for u in unites if u.vivant and est_a_portee(position, u.pos, portee)]

def get_positions_adjacentes(position: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Retourne les 6 positions hexagonales adjacentes à une position donnée"""
    q, r = position
    # Les 6 directions hexagonales
    directions = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1)
    ]
    return [(q + dq, r + dr) for dq, dr in directions]
