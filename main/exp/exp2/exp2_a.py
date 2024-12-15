from ultralytics import YOLO
import numpy as np
import cv2
import csv
from metrics import compute_trajectory_smoothness, JointAngleDynamics

# 視訊模式處理
window_size = 30  # 可根據需求調整視窗大小(幀數)

# 載入 YOLO Pose 模型
model = YOLO('../exp1/yolo11x-pose.pt')

# 設定圖片或視訊路徑
img_path = './abnormal_walk.mp4'
is_video = True

# 定義關節連接關係，用於繪製骨架
connections = [
    (5, 7),  # 肩膀到肘部
    (7, 9),  # 肘部到手腕
    # 添加更多連接點根據需求繪製完整骨架
]

# 初始化存儲結構
person_keypoints_sequence = []  # 用於存儲每個人的關鍵點序列
dcr_values = []  # 用於存儲 DCR 指標
smoothness_values = []  # 用於存儲平滑度指標
jad_values = []  # 用於存儲關節角度動態指標

# DCR 計算函數
def calculate_dcr(keypoints):
    if len(keypoints) < 2:
        return 0  # 如果關鍵點不足，返回 0

    limb_sync = []
    for start, end in connections:
        if (keypoints[start][0] > 0 and keypoints[start][1] > 0 and
            keypoints[end][0] > 0 and keypoints[end][1] > 0):
            limb_vector = keypoints[end] - keypoints[start]
            limb_sync.append(np.linalg.norm(limb_vector))

    if len(limb_sync) < 2:
        return 0

    dcr = np.std(limb_sync) / (np.mean(limb_sync) + 1e-5)  # 避免除以 0
    return dcr

# 視訊模式處理
if is_video:
    cap = cv2.VideoCapture(img_path)
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

                # 更新每個人關鍵點的序列
                if len(person_keypoints_sequence) <= frame_index:
                    person_keypoints_sequence.append([])  # 初始化序列列表

                person_keypoints_sequence[frame_index].append(person_keypoints)

                # 計算 DCR 並存儲
                dcr = calculate_dcr(person_keypoints)
                dcr_values.append((frame_index, dcr))

        # 計算平滑度指標
        
        if len(person_keypoints_sequence) > 3:
            keypoints_array = np.array(person_keypoints_sequence[-window_size:])  # 取最近 window_size 幀
            keypoints_array = keypoints_array.squeeze()  # 去除多餘的維度
            smoothness_result = compute_trajectory_smoothness(keypoints_array)
            smoothness_values.append((frame_index, smoothness_result['Smoothness'], smoothness_result['MSJ'], smoothness_result['Var']))

        # 計算關節角度動態指標

        if len(person_keypoints_sequence) > 30:
            keypoints_array = np.array(person_keypoints_sequence[-window_size:])
            # print(keypoints_array.shape)
            keypoints_array = keypoints_array.squeeze()
            jad = JointAngleDynamics(keypoints_array, fps=30)
            features = jad.aggregate_features()
            jad_values.append((frame_index, features['coordination_index']))

        # 顯示結果
        cv2.imshow('Pose Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()

# 將數據保存為 CSV
with open('keypoints_data.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Frame', 'Person', 'Keypoint_Index', 'Keypoint_X', 'Keypoint_Y'])
    for frame_idx, persons in enumerate(person_keypoints_sequence):
        for person_idx, keypoints in enumerate(persons):
            for kp_idx, (x, y) in enumerate(keypoints):
                csvwriter.writerow([frame_idx, person_idx, kp_idx, x, y])

with open('dcr_values.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Frame', 'DCR'])
    for frame_idx, dcr in dcr_values:
        csvwriter.writerow([frame_idx, dcr])

with open('smoothness_values.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Frame', 'Smoothness', 'MSJ', 'Var'])
    for frame_idx, smoothness, msj, var in smoothness_values:
        csvwriter.writerow([frame_idx, smoothness, msj, var])

with open('jad_values.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Frame', 'Coordination_Index'])
    for frame_idx, jad in jad_values:
        csvwriter.writerow([frame_idx, jad])