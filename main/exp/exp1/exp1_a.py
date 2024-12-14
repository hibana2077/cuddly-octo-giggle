from ultralytics import YOLO
import numpy as np
import cv2
import matplotlib.pyplot as plt

# 視訊模式處理
window_size = 30  # 可根據需求調整視窗大小(幀數)

# 載入 YOLO Pose 模型
model = YOLO('yolo11x-pose.pt')

# 設定圖片或視訊路徑
# img_path = '../../test/test2.png'
img_path = './test_video.mp4'
# is_video = False  # 設定是否為視訊模式
is_video = True

# 定義關節連接關係，用於繪製骨架
connections = [
    (5, 7),  # 肩膀到肘部
    (7, 9),  # 肘部到手腕
    # 添加更多連接點根據需求繪製完整骨架
]

# 定義計算關節角度的函數
def calculate_joint_angles(points):
    """計算兩個關節之間的角度"""
    if len(points) >= 3:
        p1, p2, p3 = points[0], points[1], points[2]
        v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
        v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
        angle = np.arccos(
            np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        )
        return np.degrees(angle)
    return None

def motion_smoothness(angles):
    """
    計算運動平滑性 (基於 Jerk Minimization)
    :param angles: 一組關節角度序列
    :return: 運動平滑性 (越小越平滑)
    """
    if len(angles) >= 4:
        jerk = np.diff(angles, n=3)  # 三次微分
        return np.mean(np.abs(jerk))  # 計算絕對值平均
    return None

def movement_stability_index(trajectories, center_of_mass):
    """
    計算動作穩定性指數 (MSI)
    :param trajectories: 關節的軌跡 (形狀: Nx2, 每行為 (x, y))
    :param center_of_mass: 身體質心的軌跡 (形狀: Nx2, 每行為 (x, y))
    :return: 穩定性指數 (越小越穩定)
    """
    if len(trajectories) != len(center_of_mass):
        raise ValueError("Trajectories and center of mass must have the same length.")
    
    # 軌跡方差
    trajectory_var = np.var(trajectories, axis=0).mean()  # x 和 y 方向的平均方差
    
    # 質心偏移量
    com_deviation = np.linalg.norm(np.diff(center_of_mass, axis=0), axis=1).mean()
    
    # 合併為穩定性指數
    return trajectory_var + com_deviation

# 存儲觸發時的數據與圖片
def save_frame_data(frame, frame_index, angle, smoothness, msi):
    filename = f"./save/saved_frame_{frame_index}.png"
    cv2.imwrite(filename, frame)
    with open(f"./save/saved_frame_{frame_index}.txt", "w") as f:
        f.write(f"Angle: {angle}\n")
        f.write(f"Motion Smoothness: {smoothness}\n")
        f.write(f"Movement Stability Index: {msi}\n")
    print(f"Frame data saved: {filename}")

# 圖片模式處理
if not is_video:
    img = cv2.imread(img_path)
    results = model(img)

    # 遍歷每個偵測結果，取得關鍵點並繪製骨架
    for result in results:
        keypoints = result.keypoints.xy.cpu().numpy()  # 取得所有關鍵點座標
        
        for person_keypoints in keypoints:
            # 繪製點
            for (x, y) in person_keypoints:
                if x > 0 and y > 0:  # 過濾無效座標
                    cv2.circle(img, (int(x), int(y)), radius=5, color=(255, 0, 0), thickness=-1)
            
            # 繪製線條
            for (start, end) in connections:
                if person_keypoints[start][0] > 0 and person_keypoints[start][1] > 0 and \
                   person_keypoints[end][0] > 0 and person_keypoints[end][1] > 0:
                    pt1 = (int(person_keypoints[start][0]), int(person_keypoints[start][1]))
                    pt2 = (int(person_keypoints[end][0]), int(person_keypoints[end][1]))
                    cv2.line(img, pt1, pt2, color=(0, 255, 0), thickness=2)
            
            # 計算關節角度 (假設肩膀-肘部-手腕)
            indices = [5, 7, 9]
            selected_points = [person_keypoints[i] for i in indices]
            angle = calculate_joint_angles(selected_points)
            if angle is not None:
                print(f"Joint Angle (shoulder-elbow-wrist): {angle:.2f} degrees")

    # 顯示結果
    cv2.imshow('Pose Detection', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 視訊模式處
else:
    # 設定冷卻間隔幀數
    cooldown_frames = 30
    last_saved_frame = -cooldown_frames
    cap = cv2.VideoCapture(img_path)
    angles = []  # 用於存儲每幀的角度
    trajectories = []  # 用於存儲關節的軌跡
    center_of_mass = []  # 用於存儲質心的軌跡 (假設質心為關節的平均值)
    saved_frames = []  # 存儲已儲存的幀索引

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for result in results:
            keypoints = result.keypoints.xy.cpu().numpy()  # 取得所有關鍵點座標

            for person_keypoints in keypoints:
                # 繪製點
                for (x, y) in person_keypoints:
                    if x > 0 and y > 0:
                        cv2.circle(frame, (int(x), int(y)), radius=5, color=(255, 0, 0), thickness=-1)

                # 繪製線條
                for (start, end) in connections:
                    if person_keypoints[start][0] > 0 and person_keypoints[start][1] > 0 and \
                       person_keypoints[end][0] > 0 and person_keypoints[end][1] > 0:
                        pt1 = (int(person_keypoints[start][0]), int(person_keypoints[start][1]))
                        pt2 = (int(person_keypoints[end][0]), int(person_keypoints[end][1]))
                        cv2.line(frame, pt1, pt2, color=(0, 255, 0), thickness=2)

                # 計算關節角度 (肩膀-肘部-手腕)
                indices = [5, 7, 9]  # 關鍵點索引，依據實際Model定義
                selected_points = [person_keypoints[i] for i in indices]
                angle = calculate_joint_angles(selected_points)
                if angle is not None:
                    angles.append(angle)
                    # 視窗化：只保留最後 window_size 個資料
                    if len(angles) > window_size:
                        angles = angles[-window_size:]
                    print(f"Joint Angle (shoulder-elbow-wrist): {angle:.2f} degrees")

                # 更新軌跡和質心數據
                trajectories.append(person_keypoints[:, :2])  # 只存儲 x, y
                center_of_mass.append(np.mean(person_keypoints, axis=0))

                # 視窗化：只保留最後 window_size 個資料
                if len(trajectories) > window_size:
                    trajectories = trajectories[-window_size:]
                if len(center_of_mass) > window_size:
                    center_of_mass = center_of_mass[-window_size:]

        # 計算運動平滑性 (Motion Smoothness)
        smoothness = motion_smoothness(angles)
        if smoothness is not None:
            print(f"Motion Smoothness (last {window_size} frames): {smoothness:.2f}")

        # 計算動作穩定性指數 (Movement Stability Index)
        if len(trajectories) > 1 and len(center_of_mass) > 1:
            msi = movement_stability_index(np.array(trajectories), np.array(center_of_mass))
            print(f"Movement Stability Index (last {window_size} frames): {msi:.2f}")

        # 觸發條件檢查
        if smoothness is not None and msi is not None:
            if (smoothness > 5.0 or msi > 10.0) and (frame_index - last_saved_frame >= cooldown_frames):
                save_frame_data(frame, frame_index, angles[-1], smoothness, msi)
                saved_frames.append(frame_index)
                last_saved_frame = frame_index

        # 顯示結果
        cv2.imshow('Pose Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_index += 1

    # 繪製圖表
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(angles)), angles, label="Joint Angles")
    plt.title("Joint Angles Over Time")
    plt.xlabel("Frame Index")
    plt.ylabel("Angle (degrees)")
    plt.legend()
    plt.grid()
    plt.savefig("joint_angles_plot.png")
    plt.show()

    cap.release()
    cv2.destroyAllWindows()
