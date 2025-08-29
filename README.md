Je veux créer un jeu du même type que waven.
Je te définit donc le projet.
Le joueur choisira un élément, une spécialisation et un nom de personnage.
Il y aura un menu Combattre, qui permet de combattre des adversaire, on choisit le nombre de personnage que l'on veut jouer.
La grille de jeu sera hexagonale.
A chaque victoire, un nombre d'exp est attribué au personnage, et un nombre d'or au joueur.
En augementant le niveau du personnage, il pourra débloquer de nouveaux sorts. Il sera limité dans leur utilisation.
Il n'y aura pas de graphismes pour les entités, juste un nom d'affiché.
Quand on survole le nom d'une entité, un menu à droite affiche ses statistiques et ses compétances.

On va tout d'abord créer un combat en 2V2 uniquement avec des entités nommés squelettes. Elles ont 3 PV, et infligent 5 DMG. Les attaques de corps à corps se font uniquement si les entités sont sur 2 héxagones adjascents.

Crée donc ces entitée ainsi qu'un terrain de combat, et tout ce qui va permettre de jouer le combat, comme la sélection de l'entité à jouer, un bouton terminer le tour, quand une unitée est sélectionnée, de l'autre côté de l'affichage pour les ennemies, les statistiques de l'unité apparaitront, une fois sélectionné, si adjascente à un ennemie, l'hexagone autour de celui ci sera rouge, signifiant qu'il est possible de l'attaquer.