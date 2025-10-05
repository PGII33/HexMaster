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
>Aura sacrée (Passif) : Augmente définitivement les DMG de +3 pour tous les alliés adjacents tant que l'unité est en vie.
(Non stackable)

>Armure de pierre (Passif) : Réduit tous les dégâts reçus de 2 points (minimum 0).

> Bénédiction (Actif) : Augmente définitivement l'attaque de +2 et donne 1 bouclier à un allié.
(Non stackable, portée : 3).

> Bouclier de la foi (Passif) : Donne 1 point de bouclier à tous les alliés adjacents.
(Chaque tour)

> Combustion différée (Passif) : L'unité touchée meurt automatiquement au bout de 3 tours ennemis.

> Commandement (Actif) : Donne +3 DMG temporaire et +1 attaque supplémentaire temporaire à un allié.
(Non stackable, Portée : 2)

> Cristalisation (Actif) : Crée un cristal de 10PV sur une case adjacente sélectionnée.

> Divertissement (Passif) : S'il reste au moins une attaque en fin de tour à l'unité, toutes les unités adjacentes perdent une attaque au tour suivant.

> Enracinement (Passif) : Régénère 2 PV en fin de tour si l'unité n'a pas bougé.

> Explosion sacrée (Passif) : Se sacrifie pour infliger ses PV actuels en dégâts à la cible attaquée.

> Fantomatique (Passif) : Permet de passer au travers des unités (ne coûte pas de PM).

> Invocation (Passif) : Invoque aléatoirement deux unité Morts-Vivants (tier 1-2) sur une case adjacente libre chaque tour.

> Lumière vengeresse (Passif) : L'unité regagne 1 attaque quand elle tue une unité de la faction Mort-Vivant.

> Manipulation (Passif) : Toutes les unités ennemies avec 4 PV ou moins rejoignent votre équipe tant qu'elles ont 3 PV ou moins.

> Monture libéré (Actif) : L'unité se transforme en Guerrier sur une case adjacente libre et crée un Cheval allié sur sa position d'origine.

> Nécromancie (Passif) : Invoque un Squelette sur une case adjacente libre chaque tour.

> Rage (Passif) : L'unité gagne +1 DMG après chaque attaque effectuée.
(Stackable)

> Regard mortel (Passif) : Tue instantanément les unités ennemies de tier 2 ou moins touchées.

> Renaissance (Passif) : L'unité a 80% de chance de revenir à la vie avec tous ses PV quand elle meurt.

> Pluie de flèches (Actif) : L'unité inflige des dégâts à la cible et toutes les unités adjacentes. 
(Portée : 3, Rechargement : 1 tour)

> Protection (Passif) : Les unités subissent les dégâts à la place des alliés adjacents les dégats s'équilibrent pour que chaque protecteur aient le même nombre de poits de vie.

> Tas d'os (Passif) : À la mort de l'unité, se transforme en Tas d'Os.

> Sangsue (Passif) : L'unité gagné des PV égaux aux dégâts infligés (peut dépasser le maximum).

> Sédition venimeuse (Passif) : L'unité attaquée est forcée d'attaquer un allié adjacent si possible.

> Soin (Actif) : Soigne un allié de 5 PV.
(Portée : 2)

> Tir précis (Actif) : L'unité attaque à portée +1 avec dmg x1.5.
(Rechargement : 1 tour)

> Vague apaisante (Passif) : Soigne tous les alliés adjacents de 2 PV chaque tour.

> Venin incapacitant (Passif) : L'unité touchée ne peut pas se déplacer au tour suivant.

> Vol (Passif) : Ignore complètement la première attaque subie.

> Zombification (Passif) : Transforme l'unité ennemie tuée en zombie allié (de).

## Extra

### 

### Idées factions
Bonus : Faction obtenable après avoir terminé le jeu, contient des unités sans cohérence nécessaire.
Kaiju ??
Dinosaures ??

### Idée Ajouts

#### Bâtiments
Tour : Augemente de 1 la portée des unités adjacentes
Mur : Bloque le passage 
Cache : Réduit de 1 (min 1) la portée atteignant les unités adjacentes à la cache
Fleuve sacré


### Idées unitée

| Unité          | Tier | Compétences    | Faction|
|------------|------|--------------------|--------|
| Paysan     | 1    | ?                  | Humain |
| Salamandre | 4    | ?              |Elementaires| 
| Basilic    |   4  |Regard Mortel         | ?    |
| Dragon     | 4    | ?                    | ?    |
| Goblin     | ? | ? | ? |
| Elfes     | ? | ? | ? |
| Elfes noir     | ? | ? | ? |  
| Orc     | ? | ? | ? |
| Géants     | ?    | ?                    |    ? |
| Cyclopes   | ?    |                  ?   |    ? |
| Dracula    | 4    |      ?        |Morts-Vivants|
| Vincent    | 4    | Lancé de Claquette   | Bonus|
| Micky      | 4    | Réincarnation        | Bonus|
| Clément    | 4    | M. ADN               | Bonus|
| Mathis     | ?    | Vague de guérison                 |     ?|

### Idées Compétences
    Lancé de Claquette : Tout les Z tours, peut lancer une claquette à portée X infligeant Y dégats.
    M. ADN : Invoque une unité "Dinosaures" sur une case adjacente (chaque tour, tier + 1, max à 4 (tier des boss)).
    Réincarnation : Quand meurt, se réincarne dans le corps d'une unite allié de plus bas rang disponible (max rang 3).
    Vague de guérison : Retire tout les debuff et soigne de X (portée à determiner)

## Mentions

Je remercie **Mathis**, **Vincent** et **Clément** pour m'avoir aidé au niveau inspiration.
