import pandas as pd
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
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

def calculate_win_rate(df):
    """Calculate win rate (games where all tiles were closed)."""
    # A game is considered won if all 9 tiles were closed (score = 0)
    df['Win'] = df['Score'] == 0
    return df

def analyze_and_visualize(df):
    """Analyze and visualize the results with enhanced metrics."""
    # Apply strategy names and calculate win rates
    df = apply_strategy_names(df)
    df = calculate_win_rate(df)
    
    # Filter the DataFrame to include only the specified strategies
    df = df[df['Strategy'].isin(strategies)]
    
    # Calculate total games analyzed
    total_games = len(df)
    print(f"\n=== ANALYSIS SUMMARY ===")
    print(f"Total games analyzed: {total_games}")
    
    # Group by strategy name and calculate comprehensive metrics
    grouped = df.groupby(['Strategy', 'Strategy Name']).agg({
        'Game Number': 'count',  # Number of games per strategy
        'Score': ['mean', 'min', 'max', 'std'],  # Score statistics
        'Tiles Closed': ['mean', 'min', 'max'],  # Tiles closed statistics
        'Win': 'sum'  # Number of wins (complete shutdowns)
    }).reset_index()
    
    # Flatten the column hierarchy
    grouped.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in grouped.columns.values]
    
    # Calculate win rate as percentage
    grouped['Win_Rate_%'] = (grouped['Win_sum'] / grouped['Game Number_count'] * 100).round(2)
    
    # Rename columns for clarity
    grouped = grouped.rename(columns={
        'Strategy': 'Strategy_Num',
        'Strategy Name': 'Strategy',
        'Game Number_count': 'Games_Played',
        'Score_mean': 'Avg_Score',
        'Score_min': 'Min_Score',
        'Score_max': 'Max_Score',
        'Score_std': 'Score_StdDev',
        'Tiles Closed_mean': 'Avg_Tiles_Closed',
        'Tiles Closed_min': 'Min_Tiles_Closed',
        'Tiles Closed_max': 'Max_Tiles_Closed',
        'Win_sum': 'Complete_Wins'
    })
    
    # Sort by the most effective strategy (lower score is better)
    grouped = grouped.sort_values(by='Avg_Score', ascending=True)
    
    # Print detailed results table
    print("\n=== STRATEGY PERFORMANCE METRICS ===")
    print("NOTE: Lower score is better (0 is perfect)")
    print("      Complete win = All tiles closed (box shut)")
    
    # Create a display DataFrame with the most important metrics
    display_cols = ['Strategy', 'Games_Played', 'Avg_Score', 'Avg_Tiles_Closed', 
                   'Complete_Wins', 'Win_Rate_%']
    
    print(grouped[display_cols].to_string(index=False))
    
    # Print detailed stats
    print("\n=== DETAILED STATISTICS ===")
    detailed_cols = ['Strategy', 'Min_Score', 'Max_Score', 'Score_StdDev', 
                    'Min_Tiles_Closed', 'Max_Tiles_Closed']
    print(grouped[detailed_cols].to_string(index=False))
    
    # Create a single comprehensive dashboard with all visualizations
    create_unified_dashboard(grouped)

def create_unified_dashboard(grouped):
    """Create a unified dashboard with all relevant visualizations in a single window."""
    # Prepare data for multi-metric comparison
    strategies = grouped['Strategy'].tolist()
    
    # Normalize metrics to 0-1 scale for comparison
    win_rate_norm = grouped['Win_Rate_%'] / 100
    avg_score_norm = 1 - (grouped['Avg_Score'] / grouped['Avg_Score'].max())  # Invert so higher is better
    tiles_closed_norm = grouped['Avg_Tiles_Closed'] / 9  # Normalize by maximum possible (9)
    
    # Create a figure with a 2x2 grid layout for all visualizations
    fig = plt.figure(figsize=(20, 18))
    fig.suptitle('Shut The Box AI Strategy Performance Dashboard', fontsize=20, y=0.98)
    
    # Create grid specification for better control of subplot sizes
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2])
    
    # 1. Bar Charts for Main Metrics (top left)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(strategies, grouped['Win_Rate_%'], color='green', alpha=0.7)
    ax1.set_ylabel('Win Rate %', fontsize=12)
    ax1.set_title('Complete Box Shutdown Rate', fontsize=14)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax1.set_ylim(0, max(grouped['Win_Rate_%']) * 1.1)  # Add 10% padding
    
    # 2. Average Score (top right)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.bar(strategies, grouped['Avg_Score'], color='skyblue', alpha=0.7)
    ax2.set_ylabel('Average Score', fontsize=12)
    ax2.set_title('Average Score (Lower is Better)', fontsize=14)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 3. Average Tiles Closed (bottom left)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.bar(strategies, grouped['Avg_Tiles_Closed'], color='orange', alpha=0.7)
    ax3.set_ylabel('Avg Tiles Closed', fontsize=12)
    ax3.set_title('Average Tiles Closed (Higher is Better)', fontsize=14)
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    for i, v in enumerate(grouped['Avg_Tiles_Closed']):
        ax3.text(i, v + 0.1, f"{v:.2f}", ha='center', fontsize=10)
    
    # 4. Radar Chart (bottom right)
    ax4 = fig.add_subplot(gs[1, 1], polar=True)
    
    # Number of metrics for radar chart
    N = 3
    
    # Create theta for radar chart (evenly spaced around circle)
    theta = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    theta += theta[:1]  # Close the loop
    
    # Labels for radar chart axes
    labels = ['Win Rate', 'Score\n(Inverted)', 'Tiles Closed']
    labels += labels[:1]  # Close the loop
    ax4.set_xticks(theta)
    ax4.set_xticklabels(labels, fontsize=12)    # Plot each strategy on the radar chart
    colors = plt.colormaps['tab10'](np.linspace(0, 1, len(strategies)))
    
    for i, strategy in enumerate(strategies):
        # Prepare the values for this strategy
        values = [win_rate_norm.iloc[i], avg_score_norm.iloc[i], tiles_closed_norm.iloc[i]]
        values += values[:1]  # Close the loop
        
        # Plot the strategy on the radar chart
        ax4.plot(theta, values, color=colors[i], label=strategy, linewidth=2)
        ax4.fill(theta, values, color=colors[i], alpha=0.25)
    
    # Customize the radar chart
    ax4.set_ylim(0, 1)
    ax4.set_title('Strategy Comparison: Normalized Metrics', fontsize=14)
    ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    # Add a text box with key observations
    best_strategy = grouped.iloc[0]['Strategy']
    worst_strategy = grouped.iloc[-1]['Strategy']
    highest_win_rate = grouped['Win_Rate_%'].max()
    highest_win_rate_strategy = grouped.loc[grouped['Win_Rate_%'].idxmax(), 'Strategy']
    
    textstr = '\n'.join((
        'Key Observations:',
        f'• Best Overall Strategy: {best_strategy}',
        f'• Highest Win Rate: {highest_win_rate:.2f}% ({highest_win_rate_strategy})',
        f'• Lowest Performance: {worst_strategy}',
        f'• Total Games Analyzed: {grouped["Games_Played"].sum()}'
    ))
    
    # Add text box in the center of the figure
    fig.text(0.5, 0.02, textstr, fontsize=12, 
             bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=1'),
             ha='center')
    
    # Format x-axis labels on all bar charts
    for ax in [ax1, ax2, ax3]:
        ax.set_xticks(range(len(strategies)))
        ax.set_xticklabels(strategies, rotation=45, ha='right')
    
    plt.tight_layout(rect=(0, 0.05, 1, 0.95))  # Adjust layout to make room for the text box
    plt.savefig('./results/unified_dashboard.png', dpi=150, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    directory = './results/'
    csv_files = gather_csv_files(directory)
    combined_df = load_and_combine_csv_files(csv_files)
    
    if not combined_df.empty:
        analyze_and_visualize(combined_df)
    else:
        print("No valid CSV files found.")