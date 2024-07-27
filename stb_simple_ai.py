import random
import logging
import csv
from datetime import datetime
from itertools import combinations

# Game Goal
# Roll the dice, and using the sum of the roll, flip down any combination of tiles totalling that sum
# Flip down all the tiles in the least number of rolls

# Select a strategy for the AI
strategy = 0 # Control - this is randomly choosing tiles to flip down
#strategy = 1 # Goal Based - Always choose the combination that flips down the most tiles
#strategy = 2 # Probability Based - Always choose the combination that has the least chance of recurence

# Configure logging
logging.basicConfig(filename='shut_the_box.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
class ShutTheBox:
    def __init__(self):
        """Initialize the game with tiles numbered 1 to 9 and set the game status to not over."""
        self.tiles = list(range(1, 10))
        self.game_over = False
        self.rolls = []
        self.moves = []

    def roll_dice(self):
        """Simulate rolling two six-sided dice."""
        dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
        return dice1, dice2

    def is_valid_move(self, move, total):
        """Check if the chosen move is valid.

        Args:
            move (list): List of tiles to shut.
            total (int): Total sum of the dice roll.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        return sum(move) == total and all(tile in self.tiles for tile in move)

    def make_move(self, move):
        """Remove the chosen tiles from the list of available tiles.

        Args:
            move (list): List of tiles to shut.
        """
        for tile in move:
            self.tiles.remove(tile)

    def get_possible_moves(self, total):
        """Generate all possible combinations of tiles that sum up to the rolled total.

        Args:
            total (int): Total sum of the dice roll.

        Returns:
            list: List of possible moves (combinations of tiles).
        """
        possible_moves = []
        for i in range(1, len(self.tiles) + 1):
            for combo in combinations(self.tiles, i):
                if sum(combo) == total:
                    possible_moves.append(combo)
        return possible_moves

    def calculate_tile_probabilities(self):
        """Calculate the probability of each tile number being rolled."""
        # Probabilities of sums from 2 to 12 with two six-sided dice
        sum_probabilities = {
            2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36, 6: 5/36,
            7: 6/36, 8: 5/36, 9: 4/36, 10: 3/36, 11: 2/36, 12: 1/36
        }
        
        # Calculate individual tile probabilities based on possible sums
        tile_probabilities = {i: 0 for i in range(1, 10)}
        for total, prob in sum_probabilities.items():
            for i in range(1, 10):
                if i <= total <= 9:
                    tile_probabilities[i] += prob
        
        return tile_probabilities

    def ai_player(self, possible_moves):
        """AI strategy to choose the best move.

        Args:
            possible_moves (list): List of possible moves (combinations of tiles).

        Returns:
            list: The chosen move (combination of tiles).
        """
        if possible_moves:
            if strategy == 0:
                # No Strategy Control: choose the move at random from the possible choices
                chosen_move = random.choice(possible_moves)
            elif strategy == 1:
                # Simple AI Strategy: choose the move that shuts the most tiles
                chosen_move = max(possible_moves, key=len)
            elif strategy == 2:
                # Statistical AI Strategy: choose the move with the lowest probability of recurence
                tile_probabilities = self.calculate_tile_probabilities()
                
                move_probabilities = []
                for move in possible_moves:
                    # Calculate the probability of each move
                    move_probability = sum(tile_probabilities[tile] for tile in move)
                    move_probabilities.append((move, move_probability))
                
                if move_probabilities:
                    # Choose the move with the lowest probability
                    chosen_move = min(move_probabilities, key=lambda x: x[1])[0]
                
            # Provide the selected move from one of the AI strategies back to the game
            return chosen_move           
        return []


    def play_turn(self):
        """Play a single turn of the game, including rolling dice, determining possible moves, and making a move."""
        dice1, dice2 = self.roll_dice()
        total = dice1 + dice2
        self.rolls.append((dice1, dice2))
        logging.debug(f"Rolled: {dice1} + {dice2} = {total}")
        
        possible_moves = self.get_possible_moves(total)
        logging.debug(f"Possible moves: {possible_moves}")
        
        if not possible_moves:
            self.game_over = True
            logging.debug("No possible moves. Game over!")
            return
        
        move = self.ai_player(possible_moves)
        
        if self.is_valid_move(move, total):
            self.make_move(move)
            self.moves.append(move)
            logging.debug(f"AI chose to shut tiles: {move}")
            logging.debug(f"Tiles remaining: {self.tiles}")
        else:
            logging.debug("Invalid move by AI. This should not happen.")
        
        if not self.tiles:
            self.game_over = True
            logging.debug("Congratulations! The AI has shut the box!")

    def play_game(self):
        """Play the game until it is over and return the final score and logs.

        Returns:
            tuple: Final score, number of tiles closed, list of rolls, and list of moves.
        """
        while not self.game_over:
            self.play_turn()
        score = sum(self.tiles)
        logging.debug(f"AI's final score: {score}")
        tiles_closed = 9 - len(self.tiles)
        return score, tiles_closed, self.rolls, self.moves


def simulate_games(num_games):
    """Simulate a specified number of games and log the results.

    Args:
        num_games (int): Number of games to simulate.

    Returns:
        list: List of dictionaries containing game results.
    """
    results = []
    for i in range(num_games):
        logging.debug(f"Starting game {i+1}")
        game = ShutTheBox()
        score, tiles_closed, rolls, moves = game.play_game()
        results.append({
            'game_number': i + 1,
            'score': score,
            'tiles_closed': tiles_closed,
            'rolls': rolls,
            'moves': moves
        })
        logging.debug(f"Game {i+1} ended with score: {score}")
    return results


def save_results_to_csv(results):
    """Save the simulation results to a CSV file with a timestamp.

    Args:
        results (list): List of dictionaries containing game results.
    """
    filename = './results/stb_simple_ai_results_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['Game Number', 'Score', 'Tiles Closed', 'Rolls', 'Moves'])
        # Write result rows
        for result in results:
            writer.writerow([result['game_number'], result['score'], result['tiles_closed'], result['rolls'], result['moves']])
    print(f'Results saved to {filename}') 


if __name__ == '__main__':
    num_games = 10000  # Set the number of games to simulate
    results = simulate_games(num_games)
    save_results_to_csv(results)  
    
    # Calculate and print summary statistics
    avg_score = sum(result['score'] for result in results) / num_games
    avg_tiles_closed = sum(result['tiles_closed'] for result in results) / num_games
    print(f"Average Score: {round(avg_score,2)}, Average Tiles Closed: {round(avg_tiles_closed,1)}")