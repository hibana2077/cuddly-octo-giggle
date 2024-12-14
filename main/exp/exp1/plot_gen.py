import os
import matplotlib.pyplot as plt
import numpy as np

def plot_data(data_folder):
    frames = []
    angles = []
    smoothness = []
    stability = []

    # 遞迴遍歷資料夾
    for root, _, files in os.walk(data_folder):
        for file in files:
            if file.endswith('.txt'):
                frame_id = file.split('_')[-1].split('.')[0]
                txt_path = os.path.join(root, file)

                # 讀取數據
                with open(txt_path, 'r') as f:
                    lines = f.readlines()
                    angle = float(lines[0].split(':')[-1].strip())
                    motion_smoothness = float(lines[1].split(':')[-1].strip())
                    movement_stability_index = float(lines[2].split(':')[-1].strip())

                frames.append(frame_id)
                angles.append(angle)
                smoothness.append(motion_smoothness)
                stability.append(movement_stability_index)

    # 排序frames以確保數據對應
    sorted_indices = np.argsort(frames)
    frames = [frames[i] for i in sorted_indices]
    angles = [angles[i] for i in sorted_indices]
    smoothness = [smoothness[i] for i in sorted_indices]
    stability = [stability[i] for i in sorted_indices]

    # 創建三張圖表
    plt.figure(figsize=(10, 6))

    # 角度圖表
    plt.subplot(3, 1, 1)
    plt.plot(frames, angles, marker='o', label='Angle')
    plt.title('Angles Over Frames')
    plt.xlabel('Frame ID')
    plt.ylabel('Angle')
    plt.grid(True)
    plt.legend()

    # 平滑度圖表
    plt.subplot(3, 1, 2)
    plt.plot(frames, smoothness, marker='o', label='Motion Smoothness', color='orange')
    plt.title('Motion Smoothness Over Frames')
    plt.xlabel('Frame ID')
    plt.ylabel('Motion Smoothness')
    plt.grid(True)
    plt.legend()

    # 穩定性指數圖表
    plt.subplot(3, 1, 3)
    plt.plot(frames, stability, marker='o', label='Stability Index', color='green')
    plt.title('Stability Index Over Frames')
    plt.xlabel('Frame ID')
    plt.ylabel('Stability Index')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    # plt.show()
    plt.savefig('result.png')

# 執行函數
plot_data("./save")