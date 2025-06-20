import os
import random
import logging
import csv
import json
import datetime
import time
import sys
from itertools import combinations

# Configuration Section
PLAY_TYPE = 1 # 0 for player control, 1 for AI control
NUM_GAMES = 100  # Set the number of games to simulate
STRATEGIES = [0,1,2,3,4,5]  # An array of numbers representing the strategies to simulate this run
PROGRESS_UPDATE_INTERVAL = 100  # Update progress every X games (adjust based on your simulation size)

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

def update_simulation_dashboard(iteration, total, strategy, running_score_sum, running_tiles_closed_sum, start_time, refresh=False):
    """
    Update the simulation dashboard with current progress and stats
    
    Args:
        iteration (int): Current iteration
        total (int): Total iterations
        strategy (int): Current strategy being simulated
        running_score_sum (float): Sum of scores so far
        running_tiles_closed_sum (float): Sum of tiles closed so far
        start_time (float): Start time of the simulation
        refresh (bool): Whether to refresh the entire dashboard
    """
    strategy_name = define_strategy(strategy)
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    elapsed_time = time.time() - start_time
    games_per_second = iteration / elapsed_time if elapsed_time > 0 else 0
    
    # Estimate remaining time
    if games_per_second > 0:
        remaining_games = total - iteration
        est_time_remaining = remaining_games / games_per_second
        if est_time_remaining > 60:
            time_remaining = f"{est_time_remaining/60:.1f} minutes"
        else:
            time_remaining = f"{est_time_remaining:.1f} seconds"
    else:
        time_remaining = "calculating..."
    
    # Calculate averages
    avg_score = running_score_sum / iteration if iteration > 0 else 0
    avg_tiles_closed = running_tiles_closed_sum / iteration if iteration > 0 else 0
    
    # Progress bar
    bar_length = 30
    filled_length = int(bar_length * iteration // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Clear previous output if refreshing the dashboard
    if refresh:
        # Move cursor up 8 lines (height of the dashboard)
        sys.stdout.write("\033[F\033[F\033[F\033[F\033[F\033[F\033[F\033[F")
    
    # Dashboard display
    dashboard = [
        "╔═══════════════════════════════════════════════════════════════════════════╗",
        f"║ SIMULATION DASHBOARD - Strategy {strategy} ({strategy_name})".ljust(71) + "║",
        "╠═══════════════════════════════════════════════════════════════════════════╣",
        f"║ Progress: |{bar}| {percent}%".ljust(71) + "║",
        f"║ Games: {iteration}/{total}".ljust(71) + "║",
        f"║ Current Stats: Avg Score: {avg_score:.2f} | Avg Tiles Closed: {avg_tiles_closed:.1f}".ljust(71) + "║",
        f"║ Performance: {games_per_second:.1f} games/sec | Est. remaining: {time_remaining}".ljust(71) + "║",
        "╚═══════════════════════════════════════════════════════════════════════════╝"
    ]
    
    # Print dashboard
    print("\n".join(dashboard), flush=True)

class ShutTheBox:
    def __init__(self, current_strategy=None):
        """Initialize the game with tiles numbered 1 to 9 and set the game status to not over."""
        self.tiles = list(range(1, 10))
        self.game_over = False
        self.invalid_move = False
        self.rolls = []
        self.moves = []
        self.strategy = current_strategy

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
        tile_probabilities = {i: 0.0 for i in range(1, 10)}  # Changed from 0 to 0.0
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
            if self.strategy == 0:
                # Random Choice Strategy
                chosen_move = random.choice(possible_moves)
            elif self.strategy == 1:
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
            elif self.strategy == 2:
                # Maximum Immediate Reward Decisions
                chosen_move = max(possible_moves, key=len)
            elif self.strategy == 3:
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
            elif self.strategy == 4:
                # Inside Out Logic: Always choose the tile(s) closest to the middle and work outward
                middle = 5
                possible_moves.sort(key=lambda move: min(abs(tile - middle) for tile in move))
                chosen_move = possible_moves[0]
            elif self.strategy == 5:
                # Outside In Logic: Always choose the tile(s) farthest from the middle and work inward
                middle = 5
                possible_moves.sort(key=lambda move: -min(abs(tile - middle) for tile in move))
                chosen_move = possible_moves[0]
            else:
                # Default to random if strategy is not defined
                chosen_move = random.choice(possible_moves)

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
        
        return self.strategy, score, tiles_closed, self.rolls, padded_moves
    
def simulate_games(num_games, strategy):
    """Simulate a specified number of games and log the results.

    Args:
        num_games (int): Number of games to simulate.
        strategy (int): The strategy to use for the simulation.

    Returns:
        list: List of dictionaries containing game results.
    """
    results = []
    start_time = time.time()
    running_score_sum = 0
    running_tiles_closed_sum = 0
    
    # Print initial dashboard
    update_simulation_dashboard(0, num_games, strategy, 0, 0, start_time)
    
    for i in range(num_games):
        logging.debug(f"Starting game {i+1}")
        game = ShutTheBox(strategy)
        game_strategy, score, tiles_closed, rolls, moves = game.play_game()
        results.append({
            'game_number': i + 1,
            'strategy': game_strategy,
            'score': score,
            'tiles_closed': tiles_closed,
            'rolls': rolls,
            'moves': moves
        })
        
        running_score_sum += score
        running_tiles_closed_sum += tiles_closed
        
        # Update dashboard periodically
        if (i + 1) % PROGRESS_UPDATE_INTERVAL == 0 or i + 1 == num_games:
            update_simulation_dashboard(i + 1, num_games, strategy, running_score_sum, running_tiles_closed_sum, start_time, refresh=(i+1 > PROGRESS_UPDATE_INTERVAL))
        
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
    
    total_start_time = time.time()
    strategy_count = len(STRATEGIES)
    
    for idx, strategy in enumerate(STRATEGIES):
        strategy_name = define_strategy(strategy)
        print(f"\n[{idx+1}/{strategy_count}] Starting simulation for strategy: {strategy_name}")
        
        # Add extra newlines to make room for the dashboard
        print("\n\n\n\n\n\n\n\n")
        
        strategy_start_time = time.time()
        logging.debug(f"## ## Simulation beginning for {NUM_GAMES} games using strategy #{strategy} ## ##")
        
        results = simulate_games(NUM_GAMES, strategy)
        save_results_to_csv(results)
        save_results_to_json(results)
        
        # Calculate and print summary statistics
        avg_score = sum(result['score'] for result in results) / NUM_GAMES
        avg_tiles_closed = sum(result['tiles_closed'] for result in results) / NUM_GAMES
        
        strategy_time = time.time() - strategy_start_time
        
        logging.debug(f"## ## Simulation ended for {NUM_GAMES} games using strategy #{define_strategy(strategy)} ## ##")
        
        print(f"\nResults for Strategy {strategy} ({strategy_name}):")
        print(f"  Games Simulated: {NUM_GAMES}")
        print(f"  Average Score: {round(avg_score, 2)}")
        print(f"  Average Tiles Closed: {round(avg_tiles_closed, 1)}")
        print(f"  Time Taken: {round(strategy_time, 1)} seconds ({round(NUM_GAMES/strategy_time, 1)} games/second)")
        print(f"  Results saved to {CSV_RESULTS_FILE} and {JSON_RESULTS_FILE}")
        
        if idx < strategy_count - 1:
            remaining_strategies = strategy_count - idx - 1
            print(f"\n{remaining_strategies} strategies remaining to test...")
    
    total_time = time.time() - total_start_time
    print("\n#### All Simulations Have Ended ####")
    print(f"Total time taken: {round(total_time/60, 2)} minutes")
    logging.debug(f"#### #### All Simulations Have Ended #### ####")
    logging.debug(f"Total time taken: {round(total_time/60, 2)} minutes")
