import random

class ShutTheBox:
    def __init__(self):
        self.tiles = list(range(1, 10))
        self.game_over = False

    def roll_dice(self):
        return random.randint(1, 6), random.randint(1, 6)

    def is_valid_move(self, move, total):
        return sum(move) == total and all(tile in self.tiles for tile in move)

    def make_move(self, move):
        for tile in move:
            self.tiles.remove(tile)

    def get_possible_moves(self, total):
        from itertools import combinations
        possible_moves = []
        for i in range(1, len(self.tiles) + 1):
            for combo in combinations(self.tiles, i):
                if sum(combo) == total:
                    possible_moves.append(combo)
        return possible_moves

    def play_turn(self):
        dice1, dice2 = self.roll_dice()
        total = dice1 + dice2
        print(f"Rolled: {dice1} + {dice2} = {total}")
        
        possible_moves = self.get_possible_moves(total)
        if not possible_moves:
            self.game_over = True
            print("No possible moves. Game over!")
            return
        
        print(f"Possible moves: {possible_moves}")
        move = input(f"Enter your move (e.g., '1 2' to shut tiles 1 and 2): ").split()
        move = list(map(int, move))
        
        if self.is_valid_move(move, total):
            self.make_move(move)
            print(f"Tiles remaining: {self.tiles}")
        else:
            print("Invalid move. Try again.")
        
        if not self.tiles:
            self.game_over = True
            print("Congratulations! You've shut the box!")

    def play_game(self):
        while not self.game_over:
            self.play_turn()
        score = sum(self.tiles)
        print(f"Your score: {score}")

if __name__ == "__main__":
    game = ShutTheBox()
    game.play_game()