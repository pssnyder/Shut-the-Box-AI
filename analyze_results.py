import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from shut_the_box import define_strategy  # Import the define_strategy function

# Select Strategies to compare
# Strategy 0 enables Random Choice - Randomly chooses from all our possible tiles to flip
# Strategy 1 enables Single Tile Priority - Start by choosing only tiles that the dice sum up to, then move to face value of the pips, finally splitting math as a last resort.
# Strategy 2 enables Maximum Immediate Reward Decisions - Always choose the combination that flips down the most tiles
# Strategy 3 enables Probability Based Choices - Always choose the combination that has the least chance of recurence
# Strategy 4 enables Inside Out Logic - Always choose the tile(s) closest to the middle and work outward
# Strategy 5 enables Outside In Logic - Always choose the tile(s) farthest from the middle and work inward
strategies = [0,1,3,4,5] # An array of numbers representing the strategies to analyze this run

def gather_csv_files(directory):
    """Gather all CSV files matching the pattern in the specified directory."""
    return glob.glob(os.path.join(directory, 'stb_simple_ai_results_*.csv'))

def validate_csv_structure(df):
    """Validate the structure of the CSV file."""
    required_columns = ['Strategy', 'Game Number', 'Score', 'Tiles Closed', 'Rolls', 'Moves']
    return all(column in df.columns for column in required_columns)

def load_and_combine_csv_files(file_list):
    """Load and combine all valid CSV files into a single DataFrame."""
    combined_df = pd.DataFrame()
    for file in file_list:
        df = pd.read_csv(file)
        if validate_csv_structure(df):
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        else:
            print(f"Invalid CSV structure in file: {file}")
    return combined_df

def apply_strategy_names(df):
    """Apply user-friendly strategy names to the DataFrame."""
    df['Strategy Name'] = df['Strategy'].apply(define_strategy)
    return df

def analyze_and_visualize(df):
    """Analyze and visualize the results."""
    # Apply strategy names
    df = apply_strategy_names(df)
    
    # Filter the DataFrame to include only the specified strategies
    df = df[df['Strategy'].isin(strategies)]
    
    # Group by strategy name and calculate the average score and average tiles closed
    grouped = df.groupby('Strategy Name').agg({
        'Score': 'mean',
        'Tiles Closed': 'mean'
    }).reset_index()

    # Rename columns for clarity
    grouped.columns = ['Strategy', 'Average Score', 'Average Tiles Closed']

    # Sort by the most effective strategy (e.g., highest average score)
    grouped = grouped.sort_values(by='Average Score', ascending=True)

    # Display the aggregated data
    print(grouped)

    # Plot average score by strategy
    plt.figure(figsize=(10, 5))
    plt.bar(grouped['Strategy'], grouped['Average Score'], color='blue')
    plt.xlabel('Strategy')
    plt.ylabel('Average Score')
    plt.title('Average Score by Strategy')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # Plot average tiles closed by strategy
    plt.figure(figsize=(10, 5))
    plt.bar(grouped['Strategy'], grouped['Average Tiles Closed'], color='green')
    plt.xlabel('Strategy')
    plt.ylabel('Average Tiles Closed')
    plt.title('Average Tiles Closed by Strategy')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    directory = './results/'
    csv_files = gather_csv_files(directory)
    combined_df = load_and_combine_csv_files(csv_files)
    
    if not combined_df.empty:
        analyze_and_visualize(combined_df)
    else:
        print("No valid CSV files found.")