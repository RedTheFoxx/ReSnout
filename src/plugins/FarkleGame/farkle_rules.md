### Key Points

- Farkle est un jeu de dés à deux joueurs où le but est d'atteindre 4 000 points en premier, comme dans *Kingdom Come Deliverance*.
- On utilise six dés à six faces, et chaque tour consiste à rouler les dés, marquer des points avec des combinaisons spécifiques, et choisir entre conserver les points ou relancer pour en marquer plus.

### Objectif et Règles de Base

Le jeu se joue à deux, et l'objectif est d'être le premier à atteindre ou dépasser 4 000 points. Chaque joueur commence son tour en lançant les six dés, puis marque des points en fonction des combinaisons obtenues. Il peut choisir de conserver ses points et passer le tour, ou relancer les dés restants pour tenter de marquer plus, au risque de tout perdre s'il ne marque rien ("farkle").

### Tour et Stratégie

Au début de chaque tour, on lance tous les dés. Ensuite, on doit mettre de côté au moins un dé qui marque des points, basé sur les combinaisons listées. Si tous les dés marquent des points dans un lancer, on peut relancer les six dés pour ajouter aux points ("dés chauds"). Si aucun dé ne marque, c'est un "farkle", et on perd tous les points du tour.

---

### Note Détaillée : Règles Complètes de Farkle dans *Kingdom Come Deliverance*

Cette section fournit une analyse approfondie des règles du jeu de Farkle tel qu'il est implémenté dans *Kingdom Come Deliverance*, avec une structure adaptée pour une implémentation logicielle ou une référence détaillée. Les informations sont tirées de sources fiables, notamment les wikis du jeu et des guides communautaires, pour assurer une précision maximale.

#### Contexte Historique et Gameplay Général

Farkle, également appelé "dice" dans le jeu, est une activité secondaire jouable dans les tavernes de *Kingdom Come Deliverance*. Il s'agit d'un jeu de dés à deux joueurs, où le premier à atteindre un score cible gagne. Dans le premier jeu, le score cible est généralement de 4 000 points, bien que des sources suggèrent 10 000 points pour *Kingdom Come Deliverance II*, nécessitant une vérification supplémentaire. Pour cette documentation, nous adoptons 4 000 points comme standard, basé sur les informations du wiki officiel ([Dice (Kingdom Come: Deliverance)](https://kingdom-come-deliverance.fandom.com/wiki/Dice_%28Kingdom_Come:_Deliverance%29)).

Le jeu met l'accent sur la stratégie et le risque, avec des décisions sur le moment de conserver les points ou de relancer pour en marquer plus, tout en risquant un "farkle" (perte totale des points du tour si aucun dé ne marque).

#### Matériel et Préparation

- **Nombre de joueurs** : Deux.
- **Équipement** : Six dés à six faces standard.

#### Structure d'un Tour

1. **Lancer initial** : À chaque tour, le joueur lance les six dés.
2. **Identification des dés marquant des points** : Après le lancer, le joueur identifie les combinaisons de dés qui marquent des points (voir section sur les combinaisons). Il doit mettre de côté au moins un dé marquant des points.
3. **Options après chaque lancer** :
   - **Conserver les points** : Le joueur peut choisir de conserver les points accumulés avec les dés mis de côté et passer le tour.
   - **Relancer les dés restants** : Le joueur peut relancer les dés non mis de côté, en essayant de marquer plus de points. Cette décision implique un risque, car un lancer sans dés marquant des points entraîne un "farkle".
4. **Dés chauds ("Hot Dice")** : Si le joueur met de côté tous les six dés dans un seul lancer (c'est-à-dire que tous les dés font partie d'une combinaison marquant des points), il bénéficie d'un lancer supplémentaire avec les six dés, ajoutant aux points accumulés. Il n'y a pas de limite au nombre de lancers "dés chauds" possibles dans un tour.
5. **Farkle** : Si un lancer ne produit aucun dé marquant des points, le joueur "farkle" et perd tous les points accumulés pendant ce tour. Le tour passe alors au joueur suivant.

#### Combinaisons de Score

Les combinaisons de score sont cruciales pour l'implémentation. Le joueur peut choisir comment partitionner les dés en combinaisons non chevauchantes pour maximiser les points. Voici les combinaisons possibles, avec des exemples pour clarification :

| **Combinaison**       | **Points**     | **Exemple**                     |
| --------------------------- | -------------------- | ------------------------------------- |
| 1 seul                      | 100 points par dé   | Un 1 = 100 points                     |
| 5 seul                      | 50 points par dé    | Un 5 = 50 points                      |
| Brelan (pas de 1)           | Nombre × 100 points | Trois 4 = 400 points                  |
| Trois 1                     | 1 000 points         | Trois 1 = 1 000 points                |
| Carré (quatre d'une sorte) | Nombre × 200 points | Quatre 4 = 800 points                 |
| Quinté (cinq d'une sorte)  | Nombre × 400 points | Cinq 4 = 1 600 points                 |
| Sixième (six d'une sorte)  | Nombre × 800 points | Six 4 = 3 200 points                  |
| Suite complète (1-6)       | 1 500 points         | 1,2,3,4,5,6 = 1 500 points            |
| Trois paires                | 1 500 points         | Deux 1, deux 2, deux 3 = 1 500 points |
| Suite partielle (1-5)       | 500 points           | 1,2,3,4,5 = 500 points                |
| Suite partielle (2-6)       | 750 points           | 2,3,4,5,6 = 750 points                |

**Notes sur le score** :

- Chaque dé ne peut faire partie que d'une seule combinaison. Par exemple, avec 1,2,3,4,5,6, on peut marquer 1 500 points comme suite complète, mais pas aussi marquer des points individuels pour les 1 et 5.
- Le joueur choisit la combinaison ou la combinaison de combinaisons qui maximise les points, tant que les ensembles de dés sont disjoints.

#### Considérations pour l'Implémentation

Pour implémenter ce jeu, voici quelques points clés :

- **Simulation des lancers** : Générer des résultats aléatoires pour six dés, chacun avec des faces de 1 à 6.
- **Détection des combinaisons** : Développer une logique pour identifier toutes les combinaisons possibles (brelans, suites, paires, etc.), en tenant compte des dés spéciaux.
- **Décisions du joueur** : Permettre au joueur de choisir quels dés mettre de côté et quelle combinaison utiliser, avec une interface pour sélectionner les options.
- **Gestion des points** : Suivre les points accumulés par tour et le score total, avec des règles pour les "dés chauds" et les "farkles".
- **Interface utilisateur** : Afficher clairement les dés lancés, les combinaisons possibles, et les points potentiels pour chaque choix.

#### Sources et Vérifications

Les règles ont été dérivées de plusieurs sources, notamment :

- Le wiki officiel du jeu, qui détaille les combinaisons et les mécaniques ([Dice (Kingdom Come: Deliverance)](https://kingdom-come-deliverance.fandom.com/wiki/Dice_%28Kingdom_Come:_Deliverance%29)).
- Des guides communautaires sur Steam, qui confirment les scores et les stratégies ([Farkle Dice Compendium](https://steamcommunity.com/sharedfiles/filedetails/?id=1304651631)).
- Des articles de jeu comme GameSpot, qui mentionnent les scores cibles et les mécaniques ([Kingdom Come: Deliverance 2 - How To Win Dice Games (Farkle Guide)](https://www.gamespot.com/gallery/kingdom-come-deliverance-2-dice-game-farkle-tips-guide/2900-6189/)).

Ces sources ont été croisées pour assurer la cohérence, bien que certaines variations (comme le score cible dans le second jeu) nécessitent une vérification supplémentaire dans le contexte du jeu.

#### Conclusion

Cette documentation fournit une base solide pour implémenter Farkle tel qu'il est joué dans *Kingdom Come Deliverance*, avec des règles claires pour les combinaisons, les tours, et les dés spéciaux. Elle est conçue pour être utilisée comme référence technique, avec des exemples et des considérations pour une implémentation logicielle.

### Key Citations

- [Dice (Kingdom Come: Deliverance) Wiki Page](https://kingdom-come-deliverance.fandom.com/wiki/Dice_%28Kingdom_Come:_Deliverance%29)
- [Farkle Dice Compendium Steam Guide](https://steamcommunity.com/sharedfiles/filedetails/?id=1304651631)
- [Kingdom Come: Deliverance 2 Dice Game Guide GameSpot](https://www.gamespot.com/gallery/kingdom-come-deliverance-2-dice-game-farkle-tips-guide/2900-6189/)
