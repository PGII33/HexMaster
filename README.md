# HexMaster

## Jouer au jeu

### Télécharger la dernière version
➡️ **[Télécharger HexMaster](../../releases/latest)** ⬅️

1. Cliquez sur le lien ci-dessus
2. Téléchargez le fichier `HexMaster.exe`
3. Lancez le jeu directement (aucune installation requise)

### Versions précédentes
Toutes les versions sont disponibles dans l'onglet [Releases](../../releases).

*Note : Une nouvelle version est automatiquement créée à chaque mise à jour du code.*

## Acronymes

### PA
Les PA (Points d'âme) sont la monaie principale du jeu, elle permet de débloquer des unitées.

### CP
Les CP (Contraintes de Placements) représentent le maximum d'unité plaçables par leurs tier. Tier X = X CP demandés.

### PV
Les PV (Points de vies) représentent la santé d'une unitée. Arrivée à 0 ou moins, l'unitée meurt.

### DMG
Les DMG (domages) représentent les dégats infligeables en une attaque classique.

### MV
Les MV (Mouvements) sont les mouvements maximum d'une unitée en un tour.

## PM
Les PM (Points de mouvements) sont les mouvements restants disponibles d'une unitée sur un tour.

## Mode de jeu

### Campagne
La campagne est constitué d'un chapitre par faction, et en fin de jeu de chapitres bonus.
Un chapitre est composé de plusieurs niveaux, dont au moins un comportant un Boss (tier 4). A l'élimination de ce Boss, on débloque une nouvelle unitée de faction bloqué ainsi que la possibilité de débloquer ses unités dans la boutique.

En complétant la campgane on gagne aussi des PA et des CP pour le mode Hexarène

### Hexarène
Hexarène est un mode infini, on choisit parmi 2 options : "Mode faction" et "Mode Libre". Ces deux modes apportent ou non des contraintes sur les unités jouables du joueur et du bot. Le bot choisit automatiquement ses unités, ce mode permet des niveaux infinis, ou de tester des combinaisons d'unités en dehors de la campagne. A l'élimination d'une unitée dans ce mode, des PA sont gagnés (Tier X = X PA).

Les CP max de ce mode augementent avec le nombre de niveau terminé sur la campagne.

### JcJ (local)
Permet d'affronter un second joueur en local.

## Factions

Les unités du jeu sont séparés en différentes "factions" il s'agit de groupe auquels appartienent ses unités. Sur certains modes de jeux, la faction est imposée, ou le mélange de factions est prohibé. Sur d'autre, la composition d'équipe est indépendante des factions. 

### Morts-Vivants

| Nom       | Tier | Compétences |
|-----------|------|-------------|
| Tas d'os  | 0    |             |
| Squelette | 1    |  Tas d'os   |
| Goule     | 1    |             |
| Spectre   | 1    |Fantomatique |
| Vampire   | 2    |   Sangsue   |
| Zombie    | 2    |Zombification|
| Liche     | 3    | Nécromancie |
| Archliche | 4    | Invocation  |

### Religieux

| Nom              | Tier | Compétences      |
|------------------|------|------------------|
| Missionnaire     | 1    |                  |
| Clerc            | 1    |     Soin         |
| Fanatique        | 1    | Explosion sacrée |
| Esprit Saint     | 2    |Bouclier de la foi|
| Paladin          | 2    | Bénédiction      |
| Ange             | 3    |Lumière Vengeresse|
| ArchAnge         | 4    |   Aura sacrée    |

### Élémentaires

| Nom       | Tier | Compétences       |
|-----------|------|-------------------|
| Cristal   | 0    |Effondrement       |
| Esprit    | 1    |                   |
| Driade    | 1    |Enracinement       |
| Gnome     | 1    |Cristalisation     |
| Golem     | 2    |Armure de pierre   |
| Ondine    | 2    |Vague apaisante    |
| Ifrit     | 3    |Combustion Différée|
| Phénix    | 4    |Renaissance        |

### Royaume

| Nom          | Tier | Compétences    |
|--------------|------|----------------|
| Cheval       | 0    |                |
| Guerrier     | 1    |                |
| Archer       | 1    |Pluie de flèches|
| Cavalier     | 1    |Monture libéré  |
| Bouffon      | 2    |Divertissement  |
| Garde royal  | 2    |Protection      |
| Roi          | 3    |Commandement    |
| Marionettiste| 4    |Manipulation    |


### Chiméres

| Nom       | Tier | Compétences      |
|-----------|------|------------------|
| Harpie    | 1    |                  |
| Centaure  | 1    |Tir Précis        |
| Griffon   | 1    |Vol               |
| Lamia     | 2    |Sédition venimeuse|
| Loup-Garou| 2    |Rage              |
| Manticore | 3    |Venin incapacitant|
| Basilic   | 4    |Regard Mortel     |

## Description des compétences
    
    Aura sacrée : Bonus de dégâts pour tout les alliés adjacents.
    Armure de pierre : Dégats subis moins 2.
    Benediction : Augemente l'attaque et la vie de la cible.
    Bouclier de la foi : 2 Bouclier sur les unités autour de soi.
    Combustion Différée : Toute unité touché meurt au bout de 3 tours.
    Commandement : Une attaque supplémentaire avec des dégats additionnels (dmg) pour la cible.
    Cristallisation : Crée un cristal de 10PV sur une case adjacente sélectionnée qui se brise au prochain tour.
    Divertissement : S'il lui reste une attaque, divertis les ennemis adjacents qui perdent une attaque (fin de tour).
    Effondrement : Meurt à son tour.
    Enracinement : Gagne 2PV si aucun déplacement n'a été fait ce tour ci.
    Explosion sacrée : Se sacrifie pour infliger ses points de vie en dégats.
    Fantomatique : Se déplace au travers des unites gratuitement.
    Invocation : Invoque une unitée de tier 1 ou 2 des Morts-Vivants sur une case adjacente (chaque tour).
    Lumière Vengeresse : Regagne son attaque lorsqu'il tue un Mort-Vivant.
    Manipulation : Toutes les unités avec 4PV ou moins passent dans votre camp (chaque tour, début du tour, pour un tour)
    Monture libéré : Descend de son cheval pour se battre en guerrier (le cheval devient indépendant).
    Nécromancie : Crée un squelette sur une case adjacente (chaque tour).
    Rage : Augemente l'attaque de 1 par attaque.
    Regard mortel : L'ennemie touché est mort s'il est de tier 2 ou moins.
    Renaissance : 80% de chance de revivre après sa mort.
    Pluie de flèches : Inflige ses dégats sur un rayon de 2 cellules juqu'à 3 cases de distances.
    Protection : Si une unité allié est adjacente est attaqué, cette unité subit les dégats à sa place. (si l'unité qui subit les dégats a la même capacité, les dégats sont partagés pour équilibrer les PV)
    Tas d'os : À la mort, un tas d'os d'1PV apparaît sur la cellule.
    Sangsue : Augmente sa vie du nombre de dégâts infligés.
    Sédition venimeuse : La créature attaqué attaque une autre créature ennemie adjacente s'il y en a une.
    Soin : Régénère 5 points de vie.
    Tir Précis : Permet de tirer à porté + 1 en plus de son attaque tout les 2 tours.
    Vague apaisante : Soigne 2 PV aux unités adjacentes.
    Venin incapacitant : Une cible touchée ne peut plus se déplacer pour son prochain tour.
    Vol : Ignore la première attaque subie.
    Zombification : Transforme l'unite ennemie tuée en zombie.

## Extra

### 

### Idées factions
Kaiju
Dinosaures


### Idées unitée
 
Salamandre 

Géants 
Sphinx 
Cyclopes

| Basilic  | 4    |Regard Mortel|
| Dragon   | 4    |             |


| Vincent OP | 4    | Lancé de Claquette |
| Micky   OP | 4    | Réincarnation      |
| Clément OP | 4    | M. ADN             |
| Mathis     | 4    |                    |

### Idées Compétences
    Regard Mortel : ???
    Lancé de Claquette : Tout les 3 tours, peut lancer une claquette n'importe où sur la carte infligeant des dégats.
    M. ADN : Invoque une unité "Dinosaures" sur une case adjacente (chaque tour, tier + 1, max à 4 (tier des boss)).
    Réincarnation : Quand meurt, se réincarne dans le corps d'une unite allié de plus bas rang disponible (max rang 3).

## Mentions

Je remercie Mathis, Vincent et Clément pour m'avoir aidé au niveau inspiration.
