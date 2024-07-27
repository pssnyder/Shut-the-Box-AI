import numpy as np
import random

class QLearningAI:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.99):
        self.q_table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay

    def get_state_key(self, tiles):
        return tuple(sorted(tiles))

    def choose_action(self, state, possible_moves):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(possible_moves)
        state_key = self.get_state_key(state)
        if state_key not in self.q_table:
            return random.choice(possible_moves)
        return max(possible_moves, key=lambda move: self.q_table[state_key].get(move, 0))

    def update_q_table(self, state, action, reward, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {}
        old_value = self.q_table[state_key].get(action, 0)
        future_rewards = max(self.q_table[next_state_key].values(), default=0)
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * future_rewards - old_value)
        self.q_table[state_key][action] = new_value

    def decay_exploration(self):
        self.exploration_rate *= self.exploration_decay

# Integrate QLearningAI into the game