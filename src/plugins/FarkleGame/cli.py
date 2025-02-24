"""Contains the complete CLI version of the Farkle game."""
import random
from enum import Enum
from datetime import datetime
from typing import List, Dict, Set, Tuple

class GameState(Enum):
    WAITING_FOR_PLAYERS = 1
    PLAYER_TURN = 2
    ROLLING_DICE = 3
    SELECTING_DICE = 4
    BANKING_SCORE = 5
    GAME_OVER = 6

class Player:
    def __init__(self, name: str):
        self.name = name
        self.total_score = 0
        self.games_played = 0
        self.average_score = 0.0
        self.wins = 0

    def update_stats(self):
        if self.games_played > 0:
            self.average_score = self.total_score / self.games_played

    def __str__(self):
        return f"{self.name} (Score: {self.total_score}, Parties: {self.games_played}, Victoires: {self.wins})"

class GameHistory:
    def __init__(self, players: List[Player], winner: Player):
        self.players = players
        self.scores = {player.name: player.total_score for player in players}
        self.date = datetime.now()
        self.winner = winner.name

    def __str__(self):
        result = f"Partie du {self.date.strftime('%d/%m/%Y à %H:%M')}\n"
        result += f"Gagnant: {self.winner}\n"
        for name, score in self.scores.items():
            result += f"{name}: {score} points\n"
        return result

class FarkleGame:
    def __init__(self, target_score: int = 4000):
        self.players: List[Player] = []
        self.current_player: Player = None
        self.current_roll: List[int] = []
        self.kept_dice: List[int] = []
        self.turn_score = 0
        self.game_state = GameState.WAITING_FOR_PLAYERS
        self.target_score = target_score
        self.history: List[GameHistory] = []
        self.current_turn_combinations = []
        self.hot_dice = False

    def display_game_state(self):
        """Affiche l'état actuel du jeu"""
        print("\n--- État du jeu ---")
        print(f"Joueur actuel: {self.current_player.name}")
        print(f"Score total: {self.current_player.total_score}")
        print(f"Score du tour: {self.turn_score}")
        print(f"Dés gardés: {self.kept_dice}")
        print(f"Dés lancés: {self.current_roll}")
        
        # Afficher les combinaisons possibles
        if self.game_state == GameState.SELECTING_DICE and self.current_roll:
            possible_combinations = self.find_all_scoring_combinations(self.current_roll)
            if possible_combinations:
                print("\nCombinaisons possibles:")
                for i, (dice_set, score, combo_name) in enumerate(possible_combinations, 1):
                    print(f"{i}. {combo_name}: {dice_set} = {score} points")
        
        print(f"État du jeu: {self.game_state.name}")
        if self.hot_dice:
            print("🔥 DÉS CHAUDS! 🔥 Vous pouvez relancer tous les dés!")
        print("------------------\n")

    def start_game(self, players: List[str]):
        """Démarre une nouvelle partie avec les joueurs spécifiés"""
        self.players = [Player(name.strip()) for name in players if name.strip()]
        if not self.players:
            print("Erreur: Aucun joueur valide n'a été spécifié.")
            return
            
        self.current_player = self.players[0]
        self.game_state = GameState.PLAYER_TURN
        print(f"Partie démarrée avec les joueurs: {', '.join(p.name for p in self.players)}")
        print(f"Objectif: {self.target_score} points")
        self.display_game_state()

    def roll_dice(self):
        """Lance les dés disponibles"""
        if self.game_state != GameState.PLAYER_TURN and not self.hot_dice:
            print("Ce n'est pas le moment de lancer les dés.")
            return
        
        # Si hot dice, on relance tous les dés
        if self.hot_dice:
            num_dice = 6
            self.hot_dice = False
        else:
            num_dice = 6 - len(self.kept_dice)
            
        self.current_roll = [random.randint(1, 6) for _ in range(num_dice)]
        self.game_state = GameState.ROLLING_DICE
        print(f"Dés lancés: {self.current_roll}")
        
        # Vérifier si c'est un Farkle
        if self.is_farkle(self.current_roll):
            print("🎲 FARKLE! 🎲 Vous perdez tous les points de ce tour.")
            self.turn_score = 0
            self.next_player()
        else:
            self.game_state = GameState.SELECTING_DICE
            self.display_game_state()

    def find_all_scoring_combinations(self, dice: List[int]) -> List[Tuple[List[int], int, str]]:
        """Trouve toutes les combinaisons possibles qui marquent des points"""
        result = []
        dice_set = sorted(dice)
        
        # Vérifier la suite complète (1-6)
        if set(dice_set) == {1, 2, 3, 4, 5, 6} and len(dice_set) == 6:
            result.append((dice_set, 1500, "Suite complète (1-6)"))
            return result  # C'est la meilleure combinaison possible
            
        # Vérifier trois paires
        counts = {x: dice_set.count(x) for x in set(dice_set)}
        if len(dice_set) == 6 and len([count for count in counts.values() if count == 2]) == 3:
            result.append((dice_set, 1500, "Trois paires"))
            return result  # C'est aussi une très bonne combinaison
            
        # Vérifier les suites partielles
        if set(dice_set) == {1, 2, 3, 4, 5} and len(dice_set) == 5:
            result.append((dice_set, 500, "Suite partielle (1-5)"))
        if set(dice_set) == {2, 3, 4, 5, 6} and len(dice_set) == 5:
            result.append((dice_set, 750, "Suite partielle (2-6)"))
            
        # Vérifier les suites partielles de 4 dés
        if len(dice_set) >= 4:
            for i in range(len(dice_set) - 3):
                subset = dice_set[i:i+4]
                if subset == [1, 2, 3, 4]:
                    result.append((subset, 250, "Suite partielle (1-4)"))
                elif subset == [2, 3, 4, 5]:
                    result.append((subset, 300, "Suite partielle (2-5)"))
                elif subset == [3, 4, 5, 6]:
                    result.append((subset, 350, "Suite partielle (3-6)"))
                    
        # Vérifier les suites partielles de 3 dés
        if len(dice_set) >= 3:
            for i in range(len(dice_set) - 2):
                subset = dice_set[i:i+3]
                if subset == [1, 2, 3]:
                    result.append((subset, 150, "Suite partielle (1-3)"))
                elif subset == [2, 3, 4]:
                    result.append((subset, 200, "Suite partielle (2-4)"))
                elif subset == [3, 4, 5]:
                    result.append((subset, 250, "Suite partielle (3-5)"))
                elif subset == [4, 5, 6]:
                    result.append((subset, 300, "Suite partielle (4-6)"))
                    
        # Vérifier les multiples (brelans, carrés, etc.)
        for num in set(dice_set):
            count = dice_set.count(num)
            if count >= 3:
                # Brelan
                if count == 3:
                    if num == 1:
                        result.append(([num] * 3, 1000, f"Brelan de 1"))
                    else:
                        result.append(([num] * 3, num * 100, f"Brelan de {num}"))
                # Carré
                elif count == 4:
                    if num == 1:
                        result.append(([num] * 4, 2000, f"Carré de 1"))
                    else:
                        result.append(([num] * 4, num * 200, f"Carré de {num}"))
                # Quinté
                elif count == 5:
                    if num == 1:
                        result.append(([num] * 5, 4000, f"Quinté de 1"))
                    else:
                        result.append(([num] * 5, num * 400, f"Quinté de {num}"))
                # Sixième
                elif count == 6:
                    if num == 1:
                        result.append(([num] * 6, 8000, f"Sixième de 1"))
                    else:
                        result.append(([num] * 6, num * 800, f"Sixième de {num}"))
        
        # Vérifier les 1 et 5 individuels
        ones = [1] * min(dice_set.count(1), 2)  # Limiter à 2 pour éviter de prendre tous les 1 si un brelan est possible
        fives = [5] * min(dice_set.count(5), 2)  # Limiter à 2 pour éviter de prendre tous les 5 si un brelan est possible
        
        if ones:
            for i in range(1, len(ones) + 1):
                result.append((ones[:i], i * 100, f"{i} dé(s) de valeur 1"))
                
        if fives:
            for i in range(1, len(fives) + 1):
                result.append((fives[:i], i * 50, f"{i} dé(s) de valeur 5"))
                
        return result

    def select_dice(self, dice_values: List[int]):
        """Sélectionne des dés du lancer actuel"""
        # Vérifier que les dés sélectionnés sont valides
        if not all(d in self.current_roll for d in dice_values):
            print("Sélection invalide: certains dés ne sont pas dans le lancer actuel.")
            return
            
        # Vérifier que la sélection marque des points
        score = self.calculate_score(dice_values)
        if score == 0:
            print("Cette sélection ne marque aucun point!")
            return
            
        # Ajouter les dés sélectionnés aux dés gardés
        self.kept_dice.extend(dice_values)
        
        # Retirer les dés sélectionnés du lancer actuel
        for die in dice_values:
            self.current_roll.remove(die)
            
        # Mettre à jour le score du tour
        self.turn_score += score
        
        print(f"Dés sélectionnés: {dice_values} = {score} points")
        
        # Vérifier si tous les dés ont été utilisés (hot dice)
        if len(self.kept_dice) == 6:
            print("🔥 DÉS CHAUDS! 🔥 Vous pouvez relancer tous les dés!")
            self.hot_dice = True
            self.kept_dice = []
            
        self.display_game_state()

    def select_combination(self, combination_index: int):
        """Sélectionne une combinaison spécifique parmi les combinaisons possibles"""
        possible_combinations = self.find_all_scoring_combinations(self.current_roll)
        
        if not possible_combinations:
            print("Aucune combinaison disponible!")
            return
            
        if combination_index < 1 or combination_index > len(possible_combinations):
            print(f"Index invalide. Choisissez entre 1 et {len(possible_combinations)}.")
            return
            
        selected_dice, score, combo_name = possible_combinations[combination_index - 1]
        print(f"Combinaison sélectionnée: {combo_name} ({selected_dice}) = {score} points")
        
        # Ajouter les dés sélectionnés aux dés gardés
        self.kept_dice.extend(selected_dice)
        
        # Retirer les dés sélectionnés du lancer actuel
        for die in selected_dice:
            self.current_roll.remove(die)
            
        # Mettre à jour le score du tour
        self.turn_score += score
        
        # Vérifier si tous les dés ont été utilisés (hot dice)
        if len(self.kept_dice) == 6:
            print("🔥 DÉS CHAUDS! 🔥 Vous pouvez relancer tous les dés!")
            self.hot_dice = True
            self.kept_dice = []
            
        self.display_game_state()

    def bank_score(self):
        """Banque le score actuel et passe au joueur suivant"""
        if self.turn_score == 0:
            print("Vous n'avez pas de points à banquer!")
            return
            
        self.current_player.total_score += self.turn_score
        print(f"{self.current_player.name} a banqué {self.turn_score} points!")
        
        # Vérifier si le joueur a gagné
        if self.current_player.total_score >= self.target_score:
            self.end_game()
            return
            
        # Réinitialiser pour le prochain tour
        self.turn_score = 0
        self.kept_dice = []
        self.hot_dice = False
        self.next_player()

    def calculate_score(self, dice_values: List[int]) -> int:
        """Calcule le score pour une combinaison de dés donnée"""
        if not dice_values:
            return 0
            
        score = 0
        dice_set = sorted(dice_values)
        counts = {x: dice_set.count(x) for x in set(dice_set)}
        
        # Suite complète (1-6)
        if set(dice_set) == {1, 2, 3, 4, 5, 6} and len(dice_set) == 6:
            return 1500
        
        # Trois paires
        if len(dice_set) == 6 and len([count for count in counts.values() if count == 2]) == 3:
            return 1500
        
        # Suites partielles
        if set(dice_set) == {1, 2, 3, 4, 5} and len(dice_set) == 5:
            return 500
        if set(dice_set) == {2, 3, 4, 5, 6} and len(dice_set) == 5:
            return 750
        
        # Multiples (brelans, carrés, etc.)
        for num, count in counts.items():
            if count >= 3:
                # Base score for three of a kind
                base_score = 1000 if num == 1 else num * 100
                
                # Multipliers for more than three
                if count == 4:
                    score += base_score * 2
                elif count == 5:
                    score += base_score * 4
                elif count == 6:
                    score += base_score * 8
                else:  # count == 3
                    score += base_score
                    
                # Remove these dice from consideration for individual scoring
                dice_set = [d for d in dice_set if d != num]
        
        # Individual 1s and 5s
        for die in dice_set:
            if die == 1:
                score += 100
            elif die == 5:
                score += 50
                
        return score

    def is_farkle(self, dice_values: List[int]) -> bool:
        """Vérifie si un lancer est un Farkle (aucun point possible)"""
        if not dice_values:
            return False
            
        # Vérifier toutes les combinaisons possibles
        possible_combinations = self.find_all_scoring_combinations(dice_values)
        return len(possible_combinations) == 0

    def next_player(self):
        """Passe au joueur suivant"""
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        self.current_player = self.players[next_index]
        self.turn_score = 0
        self.kept_dice = []
        self.current_roll = []
        self.hot_dice = False
        self.game_state = GameState.PLAYER_TURN
        print(f"C'est maintenant au tour de {self.current_player.name}")
        self.display_game_state()

    def end_game(self):
        """Termine la partie et met à jour les statistiques"""
        winner = max(self.players, key=lambda p: p.total_score)
        
        print("\n🎉 FIN DE LA PARTIE 🎉")
        print(f"Le gagnant est {winner.name} avec {winner.total_score} points!")
        
        # Mettre à jour les statistiques des joueurs
        for player in self.players:
            player.games_played += 1
            if player == winner:
                player.wins += 1
            player.update_stats()
            
        # Enregistrer l'historique
        self.history.append(GameHistory(self.players, winner))
        
        # Afficher le classement final
        self.display_leaderboard()
        
        # Réinitialiser le jeu
        self.game_state = GameState.GAME_OVER

    def display_leaderboard(self):
        """Affiche le classement des joueurs"""
        print("\n--- CLASSEMENT ---")
        sorted_players = sorted(self.players, key=lambda p: p.total_score, reverse=True)
        for i, player in enumerate(sorted_players, 1):
            print(f"{i}. {player.name}: {player.total_score} points")
        print("-----------------\n")

    def display_help(self):
        """Affiche l'aide du jeu"""
        print("\n--- AIDE DU JEU FARKLE ---")
        print("Commandes disponibles:")
        print("  new - Démarrer une nouvelle partie")
        print("  roll - Lancer les dés")
        print("  select <dés> - Sélectionner des dés (ex: select 1 5 5)")
        print("  combo <numéro> - Sélectionner une combinaison par son numéro")
        print("  bank - Banquer les points et passer au joueur suivant")
        print("  score - Afficher le score actuel")
        print("  rules - Afficher les règles du jeu")
        print("  help - Afficher cette aide")
        print("  quit - Quitter le jeu")
        print("\nRègles de base:")
        print("- Le but est d'atteindre 4000 points en premier")
        print("- Vous devez sélectionner au moins un dé qui marque des points à chaque lancer")
        print("- Si vous ne pouvez pas marquer de points, c'est un 'Farkle' et vous perdez tous les points du tour")
        print("- Si vous utilisez tous les dés, vous obtenez des 'dés chauds' et pouvez relancer tous les dés")
        print("---------------------------\n")

    def display_rules(self):
        """Affiche les règles détaillées du jeu"""
        print("\n--- RÈGLES DU FARKLE ---")
        print("Objectif: Être le premier joueur à atteindre 4000 points.")
        
        print("\nDéroulement d'un tour:")
        print("1. Lancez les six dés.")
        print("2. Après chaque lancer, vous devez mettre de côté au moins un dé qui marque des points.")
        print("3. Vous pouvez ensuite choisir de:")
        print("   - Banquer vos points et passer au joueur suivant")
        print("   - Relancer les dés restants pour tenter de marquer plus de points")
        print("4. Si vous ne pouvez pas marquer de points avec un lancer (Farkle), vous perdez tous les points du tour.")
        print("5. Si vous utilisez tous vos dés dans des combinaisons qui marquent, vous obtenez des 'dés chauds'")
        print("   et pouvez relancer les six dés en conservant vos points.")
        
        print("\nCombinaisons qui marquent des points:")
        print("- Chaque 1: 100 points")
        print("- Chaque 5: 50 points")
        print("- Trois 1: 1000 points")
        print("- Trois d'un nombre (sauf 1): nombre × 100 points (ex: trois 4 = 400 points)")
        print("- Quatre d'un nombre: 2× la valeur du brelan")
        print("- Cinq d'un nombre: 4× la valeur du brelan")
        print("- Six d'un nombre: 8× la valeur du brelan")
        print("- Suite complète (1-2-3-4-5-6): 1500 points")
        print("- Trois paires: 1500 points")
        print("- Suite partielle (1-2-3-4-5): 500 points")
        print("- Suite partielle (2-3-4-5-6): 750 points")
        print("---------------------------\n")

def main():
    """Main function to run the CLI version of the Farkle game."""
    game = FarkleGame(target_score=4000)  # Score cible de 4000 points selon les règles
    
    print("🎲 Bienvenue au jeu de Farkle! 🎲")
    print("Tapez 'help' pour voir les commandes disponibles.")
    print("Pour commencer une nouvelle partie, tapez 'new'.")

    while True:
        if game.game_state == GameState.GAME_OVER:
            print("Partie terminée! Tapez 'new' pour commencer une nouvelle partie ou 'quit' pour quitter.")
            
        command = input("> ").lower().strip()

        if command == 'new':
            players_input = input("Entrez les noms des joueurs séparés par des virgules: ")
            players = [p.strip() for p in players_input.split(',') if p.strip()]
            if len(players) < 2:
                print("Il faut au moins deux joueurs pour commencer une partie.")
                continue
            game = FarkleGame(target_score=4000)
            game.start_game(players)
            
        elif command == 'roll':
            if game.game_state == GameState.PLAYER_TURN or game.hot_dice:
                game.roll_dice()
            else:
                print("Vous ne pouvez pas lancer les dés maintenant.")
                
        elif command.startswith('select '):
            if game.game_state != GameState.SELECTING_DICE:
                print("Vous ne pouvez pas sélectionner de dés maintenant.")
                continue
                
            try:
                dice = [int(d) for d in command.split()[1:]]
                if not dice:
                    print("Vous devez spécifier au moins un dé.")
                    continue
                game.select_dice(dice)
            except ValueError:
                print("Sélection invalide. Entrez des nombres valides.")
                
        elif command.startswith('combo '):
            if game.game_state != GameState.SELECTING_DICE:
                print("Vous ne pouvez pas sélectionner de combinaison maintenant.")
                continue
                
            try:
                combo_index = int(command.split()[1])
                game.select_combination(combo_index)
            except (ValueError, IndexError):
                print("Index de combinaison invalide.")
                
        elif command == 'bank':
            if game.game_state == GameState.SELECTING_DICE:
                game.bank_score()
            else:
                print("Vous ne pouvez pas banquer de points maintenant.")
                
        elif command == 'score':
            game.display_leaderboard()
            
        elif command == 'help':
            game.display_help()
            
        elif command == 'rules':
            game.display_rules()
            
        elif command == 'quit':
            print("Merci d'avoir joué au Farkle! Au revoir!")
            break
            
        else:
            print("Commande invalide. Tapez 'help' pour voir les commandes disponibles.")

if __name__ == "__main__":
    main()
