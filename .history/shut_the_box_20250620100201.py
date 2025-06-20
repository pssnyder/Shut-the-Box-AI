import os
import random
import logging
import csv
import json
import datetime
from itertools import combinations

# Configuration Section
PLAY_TYPE = 1 # 0 for player control, 1 for AI control
NUM_GAMES = 10  # Set the number of games to simulate
STRATEGIES = [0,1,2,3,4,5]  # An array of numbers representing the strategies to simulate this run

# Ensure the logs and results directories exist
os.makedirs('./logs', exist_ok=True)
os.makedirs('./results', exist_ok=True)

LOG_FILE = './logs/shut_the_box_game_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'
CSV_RESULTS_FILE = './results/stb_simple_ai_results_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.csv'
JSON_RESULTS_FILE = './results/stb_simple_ai_results_' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.json'

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def define_strategy(strategy):
    """Translate the strategy into a user-friendly readable name."""
    if strategy == 0:
        return "Random Choice Strategy"
    elif strategy == 1:
        return "Single Tile"
    elif strategy == 2:
        return "Maximum Immediate Reward"
    elif strategy == 3:
        return "Tiles of Least Probability"
    elif strategy == 4:
        return "Inside Out"
    elif strategy == 5:
        return "Outside In"
    else:
        logging.error(f"Strategy Definition Not Found for Strategy #{strategy}")
        return "Unknown Strategy"

def pad_moves(moves, length=5, pad_value=0):
    """Pad the moves list to a consistent length with a specified pad value."""
    return [list(move) + [pad_value] * (length - len(move)) for move in moves]

class ShutTheBox:
    def __init__(self):
        """Initialize the game with tiles numbered 1 to 9 and set the game status to not over."""
        self.tiles = list(range(1, 10))
        self.game_over = False
        self.invalid_move = False
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

    def ai_player(self, possible_moves, dice1, dice2, total):
        """AI strategy to choose the best move.

        Args:
            possible_moves (list): List of possible moves (combinations of tiles).
            dice1 (int): The value of the first die.
            dice2 (int): The value of the second die.
            total (int): The sum of the dice roll.

        Returns:
            list: The chosen move (combination of tiles).
        """
        if possible_moves:
            if strategy == 0:
                # Random Choice Strategy
                chosen_move = random.choice(possible_moves)
            elif strategy == 1:
                # Single Tile Priority Strategy
                # Step 1: Choose tiles that match the total sum of the dice
                single_tile_move = [total] if [total] in possible_moves else []
                if single_tile_move:
                    chosen_move = single_tile_move
                else:
                    # Step 2: Choose tiles that match the individual dice values
                    individual_moves = [move for move in possible_moves if set(move) == {dice1, dice2}]
                    if individual_moves:
                        chosen_move = individual_moves[0]
                    else:
                        # Step 3: Resort to other combinations and pick one at random
                        chosen_move = random.choice(possible_moves)
            elif strategy == 2:
                # Maximum Immediate Reward Decisions
                chosen_move = max(possible_moves, key=len)
            elif strategy == 3:
                # Probability Based Choices
                tile_probabilities = self.calculate_tile_probabilities()
                move_probabilities = []
                for move in possible_moves:
                    # Calculate the probability of each move
                    move_probability = sum(tile_probabilities[tile] for tile in move)
                    move_probabilities.append((move, move_probability))
                if move_probabilities:
                    # Choose the move with the lowest probability
                    chosen_move = min(move_probabilities, key=lambda x: x[1])[0]
            elif strategy == 4:
                # Inside Out Logic: Always choose the tile(s) closest to the middle and work outward
                middle = 5
                possible_moves.sort(key=lambda move: min(abs(tile - middle) for tile in move))
                chosen_move = possible_moves[0]
            elif strategy == 5:
                # Outside In Logic: Always choose the tile(s) farthest from the middle and work inward
                middle = 5
                possible_moves.sort(key=lambda move: -min(abs(tile - middle) for tile in move))
                chosen_move = possible_moves[0]

            logging.debug(f"Chosen Move: {chosen_move}")
            return list(chosen_move)
        return []

    def play_turn(self):
        """Play a single turn of the game, including rolling dice, determining possible moves, and making a move."""
        
        # Start by showing the remaining tiles
        if PLAY_TYPE == 0:
            print(f"Tiles remaining: {self.tiles}")
        logging.debug(f"Tiles remaining: {self.tiles}")
                
        dice1, dice2 = self.roll_dice()
        total = dice1 + dice2
        self.rolls.append((dice1, dice2))
        
        # Set up a loop so we don't re-roll if we made an invalid move
        self.invalid_move = True # Prepare the loop 
        while self.invalid_move:
            
            if PLAY_TYPE == 0:
                print(f"Rolled: {dice1} + {dice2} = {total}")
            logging.debug(f"Rolled: {dice1} + {dice2} = {total}")            
            possible_moves = self.get_possible_moves(total)
            if PLAY_TYPE == 0:
                print(f"Possible moves: {possible_moves}")
            logging.debug(f"Possible moves: {possible_moves}")

            if not possible_moves:
                self.game_over = True
                self.rolls.pop() # Remove the last dice roll since no moves could be made
                if PLAY_TYPE == 0:
                    print("No possible moves. Game over!")
                logging.debug("No possible moves. Game over!")
                break

            if PLAY_TYPE == 0:        
                move = input(f"Enter your move (e.g., '1 2' to shut tiles 1 and 2): ").split()
                move = list(map(int, move))
            else:
                move = self.ai_player(possible_moves, dice1, dice2, total)

            if self.is_valid_move(move, total):
                self.invalid_move = False
                self.make_move(move)
                self.moves.append(move)
            else:
                self.invalid_move = True
                if PLAY_TYPE == 0:
                    print("Invalid move. Try again.")
                    logging.debug("Invalid move by player. Re-prompting")
                else:
                    logging.error("Invalid move by AI. This should not happen.")

            if not self.tiles:
                self.game_over = True
                if PLAY_TYPE == 0:
                    print("Congratulations! You've shut the box!")
                logging.debug("Congratulations! The box has been shut!")

    def play_game(self):
        """Play the game until it is over and return the final score and logs.

        Returns:
            tuple: Final score, number of tiles closed, list of rolls, and list of moves.
        """
        while not self.game_over:
            self.play_turn()
        score = sum(self.tiles)
        tiles_closed = 9 - len(self.tiles)
        if PLAY_TYPE == 0:
            print(f"Your final score: {score} with {tiles_closed} tiles closed")
        logging.debug(f"AI's final score: {score} with {tiles_closed} tiles closed")
        
        # Pad moves array to a consistent length
        padded_moves = pad_moves(self.moves)
        
        return strategy, score, tiles_closed, self.rolls, padded_moves
    
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
        strategy, score, tiles_closed, rolls, moves = game.play_game()
        results.append({
            'game_number': i + 1,
            'strategy': strategy,
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
    if not os.path.exists(CSV_RESULTS_FILE):
        with open(CSV_RESULTS_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write headers
            writer.writerow(['Strategy', 'Game Number', 'Score', 'Tiles Closed', 'Rolls', 'Moves'])
    
    with open(CSV_RESULTS_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write result rows
        for result in results:
            writer.writerow([result['strategy'], result['game_number'], result['score'], result['tiles_closed'], result['rolls'], result['moves']])
    logging.debug(f'Results appended to {CSV_RESULTS_FILE}')

def save_results_to_json(results):
    """Save the simulation results to a JSON file.

    Args:
        results (list): List of dictionaries containing game results.
    """
    if os.path.exists(JSON_RESULTS_FILE):
        with open(JSON_RESULTS_FILE, 'r') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.extend(results)

    with open(JSON_RESULTS_FILE, 'w') as file:
        json.dump(results, file, indent=4)

    logging.debug(f'Results saved to {JSON_RESULTS_FILE}')

if __name__ == '__main__':
    logging.debug(f"#### Beginning {len(STRATEGIES)} Strategy Testing ####")
    print("#### Beginning", len(STRATEGIES), "Strategy Tests ####")
    for strategy in STRATEGIES:
        logging.debug(f"## ## Simulation beginning for {NUM_GAMES} games using strategy #{strategy} ## ##")
        results = simulate_games(NUM_GAMES)
        save_results_to_csv(results)
        save_results_to_json(results)
        # Calculate and print summary statistics
        avg_score = sum(result['score'] for result in results) / NUM_GAMES
        avg_tiles_closed = sum(result['tiles_closed'] for result in results) / NUM_GAMES
        logging.debug(f"## ## Simulation ended for {NUM_GAMES} games using strategy #{define_strategy(strategy)} ## ##")
        print(f"Strategy Deployed: {define_strategy(strategy)}, Games Simulated: {NUM_GAMES}, Average Score: {round(avg_score, 2)}, Average Tiles Closed: {round(avg_tiles_closed, 1)}")
    print("#### All Simulations Have Ended ####")
    logging.debug(f"#### #### All Simulations Have Ended #### ####")