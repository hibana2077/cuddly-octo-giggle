import numpy as np
from scipy.interpolate import UnivariateSpline
import numpy as np
from scipy.signal import welch
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from scipy.spatial.distance import euclidean
from dtaidistance import dtw

def compute_trajectory_smoothness(keypoints, joint_idx=10, fps=30):
    """
    計算某個關節的軌跡平滑度指標。
    keypoints: numpy array, shape = (num_frames, 17, 2)
               每幀有17個keypoints的(x, y)座標。
    joint_idx: 欲分析的關節索引(0~16)
    fps: 影片幀率 (frames per second)
    """
    # 從keypoints中取出特定關節的x,y序列
    x = keypoints[:, joint_idx, 0]
    y = keypoints[:, joint_idx, 1]
    
    # 時間序列
    num_frames = len(x)
    t = np.arange(num_frames) / fps  # t是秒為單位

    # 計算速度
    # 使用一階差分 approximates v(t_i) = [p(t_{i+1}) - p(t_i)] / Δt
    dt = 1.0 / fps
    vx = np.diff(x) / dt
    vy = np.diff(y) / dt

    # 計算加速度
    ax = np.diff(vx) / dt
    ay = np.diff(vy) / dt

    # 計算 jerk
    jx = np.diff(ax) / dt
    jy = np.diff(ay) / dt

    # 計算 jerk 的平方平均 (MSJ)
    # jerk向量的大小平方： j² = jx² + jy²
    j_mag_sq = jx**2 + jy**2
    MSJ = np.mean(j_mag_sq) if len(j_mag_sq) > 0 else 0.0

    # 計算軌跡的平滑擬合來評估變異量 Var
    # 使用樣條擬合 x(t), y(t) 分別平滑化
    # 試用程度 (s平滑參數) 可依情況調整，這裡先預設為較小值
    s_factor = 1e-3

    spline_x = UnivariateSpline(t, x, s=s_factor)
    spline_y = UnivariateSpline(t, y, s=s_factor)

    x_hat = spline_x(t)
    y_hat = spline_y(t)

    # 計算原軌跡與擬合軌跡的誤差向量
    ex = x - x_hat
    ey = y - y_hat
    e_dist = np.sqrt(ex**2 + ey**2)

    # 計算誤差的變異量 Var
    Var = np.var(e_dist)

    # 將 MSJ 與 Var 結合成平滑度指標
    # 只是範例，可依需要調整權重或公式
    # 平滑度越高，MSJ與Var都應該越小，以下使用簡單形式：
    Smoothness = 1.0 / (1.0 + MSJ * Var)

    return {
        "MSJ": MSJ,
        "Var": Var,
        "Smoothness": Smoothness
    }

# 範例使用：假設 keypoints 是已載入的 (num_frames, 17, 2) numpy 陣列
# 這裡只示意，實際上keypoints需先定義或讀取
#
# keypoints = np.random.rand(100, 17, 2)  # 假設有100幀的虛擬資料
# result = compute_trajectory_smoothness(keypoints, joint_idx=10, fps=30)
# print("MSJ:", result["MSJ"])
# print("Var:", result["Var"])
# print("Smoothness:", result["Smoothness"])

class JointAngleDynamics:
    def __init__(self, keypoints, fps):
        """
        Initialize the class with keypoints in YOLO format and FPS.

        Parameters:
        keypoints (list): List of 17 keypoints (x, y) for each frame.
        fps (float): Frames per second of the data.
        """
        self.keypoints = keypoints
        self.fps = fps
        self.dt = 1 / fps

    def calculate_angle(self, joint_prev, joint_curr, joint_next):
        """
        Compute the joint angle using three connected joints.
        
        Parameters:
        joint_prev, joint_curr, joint_next (tuple): Coordinates of the joints (x, y).

        Returns:
        float: The joint angle in radians.
        """
        vec1 = np.array(joint_prev) - np.array(joint_curr)
        vec2 = np.array(joint_next) - np.array(joint_curr)
        
        cos_theta = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        cos_theta = np.clip(cos_theta, -1.0, 1.0)  # Avoid numerical issues
        return np.arccos(cos_theta)

    def calculate_joint_angles(self):
        """
        Calculate joint angles for each frame.

        Returns:
        dict: Dictionary of joint angles over time for each joint pair.
        """
        joint_pairs = {
            "hip": (11, 12, 13),
            "knee": (12, 13, 14),
            "ankle": (13, 14, 15),
        }
        joint_angles = {joint: [] for joint in joint_pairs}

        for frame in self.keypoints:
            for joint, (p1, p2, p3) in joint_pairs.items():
                joint_prev = frame[p1]
                joint_curr = frame[p2]
                joint_next = frame[p3]
                angle = self.calculate_angle(joint_prev, joint_curr, joint_next)
                joint_angles[joint].append(angle)

        return joint_angles

    def calculate_dynamics(self, angles):
        """
        Calculate dynamic features: angular velocity, acceleration, and jerk.
        
        Parameters:
        angles (list): Time series of joint angles.

        Returns:
        tuple: Angular velocity, acceleration, and jerk.
        """
        angular_velocity = np.diff(angles) / self.dt
        angular_acceleration = np.diff(angular_velocity) / self.dt
        angular_jerk = np.diff(angular_acceleration) / self.dt

        return angular_velocity, angular_acceleration, angular_jerk

    def compute_variability(self, series):
        """
        Compute variability (standard deviation) of a series.
        
        Parameters:
        series (list or np.array): Time series data.

        Returns:
        float: Variability of the series.
        """
        return np.std(series)

    def compute_frequency_features(self, series):
        """
        Compute frequency-domain features using Welch's method.
        
        Parameters:
        series (list or np.array): Time series data.

        Returns:
        float: High-frequency energy ratio.
        """
        f, Pxx = welch(series, fs=self.fps)
        high_freq_energy = np.sum(Pxx[f > 0.5 * np.max(f)])
        total_energy = np.sum(Pxx)

        return high_freq_energy / total_energy

    def compute_pca_coordination(self, joint_angles):
        """
        Compute coordination index using PCA.
        
        Parameters:
        joint_angles (np.array): Matrix of joint angles over time (joints x time).

        Returns:
        float: Coordination index.
        """
        pca = PCA()
        pca.fit(joint_angles.T)
        explained_variance = np.cumsum(pca.explained_variance_ratio_)
        num_components = np.searchsorted(explained_variance, 0.9) + 1
        return 1 / num_components

    def compute_adaptability(self, series1, series2):
        """
        Compute adaptability using Dynamic Time Warping (DTW).
        
        Parameters:
        series1, series2 (list or np.array): Two time series to compare.

        Returns:
        float: DTW distance between the series.
        """
        distance = dtw.distance(series1, series2)
        return distance

    def aggregate_features(self):
        """
        Aggregate features into a Joint Angle Dynamics (JAD) index.

        Returns:
        dict: JAD index and supporting metrics.
        """
        joint_angles = self.calculate_joint_angles()
        results = {}
        for joint, angles in joint_angles.items():
            vel, acc, jerk = self.calculate_dynamics(angles)
            variability = self.compute_variability(angles)
            high_freq_energy_ratio = self.compute_frequency_features(angles)
            results[joint] = {
                "variability": variability,
                "mean_squared_jerk": np.mean(jerk ** 2),
                "high_freq_energy_ratio": high_freq_energy_ratio,
            }

        coordination_index = self.compute_pca_coordination(
            np.array(list(joint_angles.values()))
        )

        return {
            "joint_metrics": results,
            "coordination_index": coordination_index,
        }

# Test Example
if __name__ == "__main__":
    # Sample keypoints in YOLO format: 17 points (x, y) per frame
    sample_keypoints = [
        [(x, y) for x, y in zip(range(17), range(17))],
        [(x + 1, y + 1) for x, y in zip(range(17), range(17))],
        [(x + 2, y + 2) for x, y in zip(range(17), range(17))],
        [(x + 3, y + 3) for x, y in zip(range(17), range(17))],
    ]
    print(f"Shape of sample keypoints: {np.array(sample_keypoints).shape}") # (2, 17, 2)
    jad = JointAngleDynamics(sample_keypoints, fps=30)
    features = jad.aggregate_features()
    print(features)
