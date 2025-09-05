# Architecture des Modes de Jeu HexMaster

## Vue d'ensemble de l'architecture

```
HexaMaster (menu.py)
├── Campagne (campagne.py)
├── HexArène 
│   ├── Mode Faction
│   └── Mode Libre
├── JcJ (Versus)
│   ├── Local
│   └── En ligne
└── Level Builder (level_builder.py)

Tous convergent vers → Jeu (jeu.py)
```

## Flux de Données vers Jeu

### Classe Jeu - Paramètres unifiés
```python
Jeu(
    ia_strategy=function,          # Stratégie IA
    screen=pygame.Surface,         # Écran de jeu
    initial_player_units=list,     # [(classe, position), ...] ou [classe, ...]
    initial_enemy_units=list,      # [(classe, position), ...] ou [classe, ...]
    enable_placement=bool,         # True = phase de placement
    versus_mode=bool              # True = joueur vs joueur
)
```

## Modes de Jeu Détaillés

### 1. Campagne
**Flux**: Menu → Campagne → UnitSelector → Jeu

**Données d'entrée**:
- Configuration de niveau (NiveauConfig)
- Type de restriction (TypeRestriction)

**Logique de sélection d'unités**:
```python
if config.type_restriction == UNITES_IMPOSEES:
    # Unités prédéfinies, pas de sélection
    player_units = config.unites_imposees
    enable_placement = not config.placement_impose
    
elif config.type_restriction == FACTION_LIBRE:
    # Sélection libre avec contraintes CP/max_unites
    selector = UnitSelector(screen, "campagne_libre", config)
    player_units = selector.run()
    enable_placement = True
    
elif config.type_restriction == FACTION_UNIQUE:
    # Sélection avec contrainte faction unique
    selector = UnitSelector(screen, "campagne_faction", config)
    player_units = selector.run()
    enable_placement = True
    
elif config.type_restriction == FACTIONS_DEFINIES:
    # Sélection avec factions limitées
    selector = UnitSelector(screen, "campagne_definies", config)
    player_units = selector.run()
    enable_placement = True
```

**Appel Jeu**:
```python
Jeu(
    ia_strategy=ia.cible_faible,
    screen=screen,
    initial_player_units=player_units,
    initial_enemy_units=config.unites_ennemis,
    enable_placement=enable_placement,
    versus_mode=False
)
```

### 2. HexArène
**Flux**: Menu → HexArène → UnitSelector → IASelector → Jeu

**Mode Faction**:
```python
selector = UnitSelector(screen, "hexarene")  # Contrainte faction
player_units = selector.run()
ia_units = IASelector("hexarene").select_units()

Jeu(
    initial_player_units=player_units,  # [classe, ...]
    initial_enemy_units=ia_units,       # [classe, ...]
    enable_placement=True,
    versus_mode=False
)
```

**Mode Libre**:
```python
selector = UnitSelector(screen, "mixte")  # Pas de contrainte
player_units = selector.run()
ia_units = IASelector("mixte").select_units()

Jeu(
    initial_player_units=player_units,
    initial_enemy_units=ia_units,
    enable_placement=True,
    versus_mode=False
)
```

### 3. Versus (JcJ Local)
**Flux**: Menu → UnitSelector (J1) → UnitSelector (J2) → PlacementPhase (J1) → PlacementPhase (J2) → Jeu

```python
# Sélection J1 et J2
player1_units = UnitSelector(screen, "versus", joueur=1).run()
player2_units = UnitSelector(screen, "versus", joueur=2).run()

# Placement J1 et J2
player1_placed = PlacementPhase(screen, player1_units, zones_j1).run()
player2_placed = PlacementPhase(screen, player2_units, zones_j2).run()

Jeu(
    initial_player_units=player1_placed,    # [(classe, pos), ...]
    initial_enemy_units=player2_placed,     # [(classe, pos), ...]
    enable_placement=False,                 # Déjà placées
    versus_mode=True                        # Mode PvP
)
```

### 4. Level Builder
**Flux**: Level Builder → Test → Jeu

```python
# Test avec unités prédéfinies ou libres selon config
if config.type_restriction == UNITES_IMPOSEES:
    test_units = config.unites_imposees
    enable_placement = not config.placement_impose
else:
    test_units = [unites.Squelette, unites.Goule]  # Unités de test
    enable_placement = True

Jeu(
    initial_player_units=test_units,
    initial_enemy_units=config.unites_ennemis,
    enable_placement=enable_placement,
    versus_mode=False
)
```

## Gestion des Formats dans Jeu

### Format initial_player_units et initial_enemy_units

**Si enable_placement=True**:
- Format d'entrée: `[classe1, classe2, ...]`
- Jeu lance PlacementPhase automatiquement
- Résultat: `[(classe, position), ...]`

**Si enable_placement=False**:
- Format d'entrée: `[(classe, position), ...]`
- Jeu utilise directement les positions

**Logique dans Jeu.__init__**:
```python
if enable_placement and initial_player_units:
    # Lancer placement automatiquement
    placement = PlacementPhase(screen, initial_player_units)
    placed_units = placement.run()
    for cls, pos in placed_units:
        self.unites.append(cls("joueur", pos))
else:
    # Utiliser positions directement
    for cls, pos in initial_player_units:
        self.unites.append(cls("joueur", pos))
```

## Responsabilités

**UnitSelector**: Sélection d'unités selon contraintes
**PlacementPhase**: Placement sur la grille
**Jeu**: Logique de combat et tour par tour
**Menu**: Orchestration et navigation

Cette architecture unifie tous les modes autour de la classe Jeu avec des paramètres clairs.
