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
| Cristal   | 0    |                   |
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
    
    Aura sacrée : Augmente définitivement l'attaque de +3 pour tous les alliés adjacents tant qu'il vit.
    Armure de pierre : Réduit tous les dégâts reçus de 2 points (minimum 0).
    Bénédiction : Augmente définitivement l'attaque de +2 et donne 1 bouclier à un allié.
    Bouclier de la foi : Donne 1 point de bouclier à tous les alliés adjacents chaque tour.
    Combustion différée : L'unité touchée meurt automatiquement au bout de 3 tours ennemis.
    Commandement : Donne +3 attaque temporaire et +1 attaque supplémentaire à un allié (portée 2). N'utilise pas d'attaque.
    Cristalisation : Crée un cristal de 10PV sur une case adjacente sélectionnée qui se brise au prochain tour.
    Divertissement : Si il reste des attaques en fin de tour, toutes les unités adjacentes perdent 1 attaque au tour suivant.
    Enracinement : Régénère 2 PV en fin de tour si l'unité n'a pas bougé.
    Explosion sacrée : Se sacrifie pour infliger ses PV actuels en dégâts à la cible attaquée uniquement.
    Fantomatique : Traverse les unités gratuitement (0 PM pour traverser, 1 PM par case vide).
    Invocation : Invoque aléatoirement une unité Morts-Vivants (tier 1-2) sur une case adjacente libre chaque tour.
    Lumière vengeresse : Regagne 1 attaque et peut continuer d'agir quand il tue un Mort-Vivant.
    Manipulation : Toutes les unités ennemies avec ≤4 PV rejoignent temporairement votre camp tant qu'elles ont ≤4 PV.
    Monture libéré : Se transforme en Guerrier à une case adjacente libre et crée un Cheval allié à sa position d'origine.
    Nécromancie : Invoque un Squelette sur une case adjacente libre chaque tour.
    Rage : Gagne définitivement +1 attaque après chaque attaque effectuée.
    Regard mortel : Tue instantanément les unités ennemies de tier ≤2 touchées.
    Renaissance : 80% de chance de revenir à la vie avec tous ses PV quand elle meurt.
    Pluie de flèches : Attaque de zone (portée 3) : inflige des dégâts à la cible et toutes les cases adjacentes, y compris aux alliés. Utilisable tous les 2 tours.
    Protection : Subit les dégâts à la place des alliés adjacents (le protecteur le plus résistant prend tous les dégâts).
    Tas d'os : À la mort, se transforme en Tas d'Os de 1 PV.
    Sangsue : Récupère des PV égaux aux dégâts infligés (peut dépasser le maximum).
    Sédition venimeuse : L'unité attaquée est forcée d'attaquer un allié adjacent si possible.
    Soin : Soigne un allié de 5 PV (maximum PV max de la cible).
    Tir précis : Attaque à portée +1 avec dégâts x1.5. Utilisable tous les 2 tours.
    Vague apaisante : Soigne tous les alliés adjacents de 2 PV chaque tour.
    Venin incapacitant : L'unité touchée ne peut pas se déplacer au tour suivant.
    Vol : Ignore complètement la première attaque subie.
    Zombification : Transforme l'unité ennemie tuée en zombie allié.

## Extra

### 

### Idées factions
Kaiju
Dinosaures


### Idées unitée

Paysan
Tour 

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
