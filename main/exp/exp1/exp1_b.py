import numpy as np
import matplotlib.pyplot as plt

# 假設已經定義好的函式 (用之前的定義)
def motion_smoothness(angles):
    if len(angles) >= 4:
        jerk = np.diff(angles, n=3)  # 三次微分
        return np.mean(np.abs(jerk))  # 計算絕對值平均
    return None

def movement_stability_index(trajectories, center_of_mass):
    if len(trajectories) != len(center_of_mass):
        raise ValueError("Trajectories and center of mass must have the same length.")
    if len(trajectories) < 2:
        return None
    trajectory_var = np.var(trajectories, axis=0).mean()  
    com_deviation = np.linalg.norm(np.diff(center_of_mass, axis=0), axis=1).mean()
    return trajectory_var + com_deviation

# ----------------------#
# 模擬資料
# ----------------------#
num_frames = 300
# 模擬 angles 資料 (假設為0~180度隨機震盪)
angles = np.cumsum(np.random.randn(num_frames)) % 180

# 模擬軌跡資料 (假設有10個關節，座標為(x,y))
num_joints = 10
trajectories = np.cumsum(np.random.randn(num_frames, num_joints, 2), axis=0)
center_of_mass = np.mean(trajectories, axis=1)

# 想要測試的 window_sizes
window_sizes = [5, 10, 20, 30, 50, 80, 100]

smoothness_values = []
msi_values = []

for w_size in window_sizes:
    # 取最後 w_size 個資料
    if w_size <= len(angles):
        angles_win = angles[-w_size:]
    else:
        angles_win = angles  # 若 w_size > 長度, 則全取
    
    if w_size <= len(trajectories):
        trajectories_win = trajectories[-w_size:]
        center_of_mass_win = center_of_mass[-w_size:]
    else:
        trajectories_win = trajectories
        center_of_mass_win = center_of_mass
    
    s_val = motion_smoothness(angles_win)
    m_val = movement_stability_index(trajectories_win, center_of_mass_win)
    
    # 若計算結果為None，設為NaN以便後續處理
    if s_val is None:
        s_val = np.nan
    if m_val is None:
        m_val = np.nan
    
    smoothness_values.append(s_val)
    msi_values.append(m_val)

# 計算 smoothness 和 msi 的最大與最小值
smoothness_max = np.nanmax(smoothness_values)
smoothness_min = np.nanmin(smoothness_values)
msi_max = np.nanmax(msi_values)
msi_min = np.nanmin(msi_values)

# 繪圖
plt.figure(figsize=(10,5))

# 繪製 smoothness 隨 window_size 的變化
plt.subplot(1,2,1)
plt.plot(window_sizes, smoothness_values, marker='o')
plt.title('Motion Smoothness vs Window Size')
plt.xlabel('Window Size')
plt.ylabel('Smoothness')
plt.axhline(smoothness_max, color='r', linestyle='--', label=f'Max: {smoothness_max:.2f}')
plt.axhline(smoothness_min, color='g', linestyle='--', label=f'Min: {smoothness_min:.2f}')
plt.legend()

# 繪製 MSI 隨 window_size 的變化
plt.subplot(1,2,2)
plt.plot(window_sizes, msi_values, marker='o', color='orange')
plt.title('Movement Stability Index vs Window Size')
plt.xlabel('Window Size')
plt.ylabel('MSI')
plt.axhline(msi_max, color='r', linestyle='--', label=f'Max: {msi_max:.2f}')
plt.axhline(msi_min, color='g', linestyle='--', label=f'Min: {msi_min:.2f}')
plt.legend()

plt.tight_layout()
plt.savefig('./result.png')
