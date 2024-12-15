import matplotlib.pyplot as plt
import pandas as pd

def plot_smoothness(data):
    """
    Plots the smoothness data over frames.

    Parameters:
    data (DataFrame): DataFrame containing 'Frame' and 'Smoothness' columns.
    """
    plt.figure(figsize=(12, 6))

    # Plot Smoothness values
    plt.plot(data['Frame'], data['Smoothness'], label='Smoothness', color='#1f77b4', marker='o')  # Blue color

    # Adding labels and legend
    plt.title("Smoothness over Frames", fontsize=14)
    plt.xlabel("Frame", fontsize=12)
    plt.ylabel("Smoothness", fontsize=12)
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.tight_layout()
    # plt.show()
    plt.savefig('smoothness_over_frames.png')

def plot_dcr_and_jad(data):
    """
    Plots the comparison of DCR and Coordination Index over frames.

    Parameters:
    data (DataFrame): DataFrame containing 'Frame', 'DCR', and 'Coordination_Index' columns.
    """
    plt.figure(figsize=(12, 6))

    # Plot Coordination Index
    plt.plot(data['Frame'], data['Coordination_Index'], label='Coordination Index', color='#ff7f0e', marker='x')  # Orange color

    # Plot DCR values
    plt.plot(data['Frame'], data['DCR'], label='DCR', color='#2ca02c', marker='o')  # Green color

    # Adding labels and legend
    plt.title("Comparison of Coordination Index and DCR over Frames", fontsize=14)
    plt.xlabel("Frame", fontsize=12)
    plt.ylabel("Values", fontsize=12)
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.tight_layout()
    # plt.show()
    plt.savefig('comparison_dcr_coordination_index.png')

if __name__ == '__main__':
    # Load the data
    smoothness_data = pd.read_csv('./jump/fail/smoothness_values.csv')
    # smoothness_data drop first row
    smoothness_data = smoothness_data.drop(0)
    dcr_data = pd.read_csv('./jump/fail/dcr_values.csv')
    jad_data = pd.read_csv('./jump/fail/jad_values.csv')

    # Merge DCR and JAD data on Frame
    dcr_jad_data = pd.merge(dcr_data, jad_data, on='Frame', how='inner')

    # Plot the smoothness data
    plot_smoothness(smoothness_data)

    # Plot the comparison of DCR and Coordination Index
    plot_dcr_and_jad(dcr_jad_data)