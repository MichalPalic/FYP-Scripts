import matplotlib.pyplot as plt

def create_double_line_graph(x, y1, y2, width=10, height=5):
    # Create a figure and a set of subplots with specified size
    fig, ax1 = plt.subplots(figsize=(width, height))

    # Create the first line (orange) on the left axis
    ax1.plot(x, y1, color='orange', label='Line 1 (left axis)', marker='X', markersize=20)  # Added marker
    ax1.set_xlabel('X values')
    ax1.set_ylabel('Y1 values', color='orange')
    ax1.tick_params(axis='y', labelcolor='orange')

    # Create the second axis (ax2) using the same x-axis (ax1) but different y-axis
    ax2 = ax1.twinx()  
    ax2.plot(x, y2, color='blue', label='Line 2 (right axis)', marker='X', markersize=20)  # Added marker
    ax2.set_ylabel('Y2 values', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')

    # Add legends and show the plot
    fig.tight_layout()
    fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
    plt.show()

# Sample data
x = range(1, 11)  # Common x-axis values from 1 to 10
y1 = [10, 13, 8, 15, 18, 15, 22, 25, 30, 27]  # Data for the first line
y2 = [1, 4, 6, 8, 10, 12, 14, 16, 18, 20]  # Data for the second line

# Example usage of the function
create_double_line_graph(x, y1, y2, width=12, height=6)
