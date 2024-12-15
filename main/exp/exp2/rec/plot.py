import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import get_cmap

# Define the skeleton connections
connections = [
    (0, 1), (0, 2),            # Nose to eyes
    (1, 3), (2, 4),            # Eyes to ears
    (0, 5), (0, 6),            # Nose to shoulders
    (5, 7), (7, 9),            # Left shoulder to elbow to wrist
    (6, 8), (8, 10),           # Right shoulder to elbow to wrist
    (5, 11), (6, 12),          # Shoulders to hips
    (11, 13), (13, 15),        # Left hip to knee to ankle
    (12, 14), (14, 16),        # Right hip to knee to ankle
    (11, 12)                   # Left hip to right hip
]

def plot_skeleton(frame_data, connections, ax=None):
    """
    Plot a single frame's skeleton on a given matplotlib axis.
    
    :param frame_data: DataFrame containing keypoints for a single frame.
    :param connections: List of tuples indicating keypoint connections.
    :param ax: Matplotlib axis to draw the skeleton.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    for kp1, kp2 in connections:
        kp1_data = frame_data[(frame_data['Keypoint_Index'] == kp1) & (frame_data['Keypoint_X'] > 0) & (frame_data['Keypoint_Y'] > 0)]
        kp2_data = frame_data[(frame_data['Keypoint_Index'] == kp2) & (frame_data['Keypoint_X'] > 0) & (frame_data['Keypoint_Y'] > 0)]
        if not kp1_data.empty and not kp2_data.empty:
            x = [kp1_data['Keypoint_X'].values[0], kp2_data['Keypoint_X'].values[0]]
            y = [kp1_data['Keypoint_Y'].values[0], kp2_data['Keypoint_Y'].values[0]]
            ax.plot(x, y, marker='o', markersize=5, color='blue')
    
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title('Skeleton Plot')

def plot_multiple_frames(data, connections, num_frames=5):
    """
    Plot multiple frames' skeletons on a single plot.
    
    :param data: DataFrame containing keypoints for multiple frames.
    :param connections: List of tuples indicating keypoint connections.
    :param num_frames: Number of frames to plot.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = get_cmap('tab10')  # Colormap for different frames

    frames = data['Frame'].unique()
    for i, frame in enumerate(frames[::num_frames]):
        frame_data = data[data['Frame'] == frame]
        color = cmap(i % 10)  # Cycle through colormap
        label_added = False  # Ensure label is added only once per frame
        for kp1, kp2 in connections:
            kp1_data = frame_data[(frame_data['Keypoint_Index'] == kp1) & (frame_data['Keypoint_X'] > 0) & (frame_data['Keypoint_Y'] > 0)]
            kp2_data = frame_data[(frame_data['Keypoint_Index'] == kp2) & (frame_data['Keypoint_X'] > 0) & (frame_data['Keypoint_Y'] > 0)]
            if not kp1_data.empty and not kp2_data.empty:
                x = [kp1_data['Keypoint_X'].values[0], kp2_data['Keypoint_X'].values[0]]
                y = [kp1_data['Keypoint_Y'].values[0], kp2_data['Keypoint_Y'].values[0]]
                ax.plot(x, y, marker='o', markersize=5, color=color, alpha=0.7, label=f'Frame {frame}' if not label_added else "")
                label_added = True  # Label is added once

    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title('Skeletons Across Multiple Frames')
    ax.legend(loc='upper right', fontsize='small')
    # plt.show()
    plt.savefig('skeletons_across_multiple_frames.png')

# Load the keypoints data
def main():
    file_path = './walk/abnormal/keypoints_data.csv'
    keypoints_data = pd.read_csv(file_path)

    # Plot the first frame
    frame_0_person_0 = keypoints_data[(keypoints_data['Frame'] == 0) & (keypoints_data['Person'] == 0)]
    fig, ax = plt.subplots(figsize=(8, 6))
    plot_skeleton(frame_0_person_0, connections, ax=ax)
    plt.show()

    # Plot multiple frames
    plot_multiple_frames(keypoints_data, connections, num_frames=10)

if __name__ == "__main__":
    main()