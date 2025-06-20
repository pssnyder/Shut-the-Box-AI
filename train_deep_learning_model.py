# train_deep_learning_model.py
"""
Train a deep learning model for the Shut the Box game using PyTorch.
"""
import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import logging
import datetime

# Configuration Section
TRAINING_FILE = './results/stb_simple_ai_results_20240727-191321.json'
MODEL_SAVE_DIR = './models'
EPOCHS = 10
BATCH_SIZE = 32
LOG_FILE = './logs/shut_the_box' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.log'
LEARNING_RATE = 0.001

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def pad_moves(moves, length=5, pad_value=0):
    """Pad the moves list to a consistent length with a specified pad value."""
    return [list(move) + [pad_value] * (length - len(move)) for move in moves]

def load_json_file(file_path):
    """Load the JSON file into a list of dictionaries."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def prepare_data(data, move_length=5, pad_value=0):
    """Prepare data for training."""
    X = []
    y = []

    for entry in data:
        tiles = entry['tiles_closed'] if isinstance(entry['tiles_closed'], list) else [entry['tiles_closed']]
        moves = entry['moves'] if isinstance(entry['moves'], list) else [entry['moves']]

        # Ensure all elements in moves are lists
        moves = [list(move) if isinstance(move, (list, tuple)) else [move] for move in moves]

        # Flatten the tiles and moves lists to avoid jagged arrays
        flat_tiles = [item for sublist in tiles for item in (sublist if isinstance(sublist, list) else [sublist])]
        flat_moves = [item for sublist in moves for item in (sublist if isinstance(sublist, list) else [sublist])]

        X.append([entry['score'], entry['game_number']] + flat_tiles)
        y.extend(flat_moves)  # Flatten the move list and add to y

    # Pad y to have consistent length
    y = pad_moves(y, move_length, pad_value)

    # Convert lists to numpy arrays
    X = np.array(X, dtype=float)
    y = np.array(y, dtype=float).flatten()  # Ensure y is flattened to 1D

    return X, y

class ShutTheBoxModel(nn.Module):
    """Neural network model for Shut the Box."""
    def __init__(self, input_size):
        super(ShutTheBoxModel, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 32)
        self.fc4 = nn.Linear(32, 1)

    def forward(self, x):
        x = self.flatten(x)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return x

def train_model(X, y):
    """Train the model."""
    input_size = X.shape[1]
    model = ShutTheBoxModel(input_size)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32).view(-1, 1)  # Ensure y is a column vector

    for epoch in range(EPOCHS):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_tensor)

        if outputs.shape != y_tensor.shape:
            logging.error(f"Shape mismatch: outputs.shape = {outputs.shape}, y_tensor.shape = {y_tensor.shape}")
            raise RuntimeError(f"Shape mismatch: outputs.shape = {outputs.shape}, y_tensor.shape = {y_tensor.shape}")

        loss = criterion(outputs, y_tensor)
        loss.backward()
        optimizer.step()

        logging.debug(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {loss.item():.4f}")

    # Save the model with a timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    model_save_path = os.path.join(MODEL_SAVE_DIR, f'shut_the_box_model_{timestamp}.pt')
    torch.save(model.state_dict(), model_save_path)

    logging.debug(f"Model training complete and saved as '{model_save_path}'.")

    return model

if __name__ == '__main__':
    logging.debug("#### Begin Training Deep Learning Model ####")
    
    # Load training data
    data = load_json_file(TRAINING_FILE)
    
    if data:
        # Prepare data for training
        X, y = prepare_data(data)
        
        # Train the model
        model = train_model(X, y)
        
        logging.debug("Model training complete.")
    else:
        logging.warning("No valid data found.")