import cv2
import numpy as np
from ultralytics import YOLO

# 定義骨架連接關係 (根據 COCO 格式)
connections = [
    (0, 1), (0, 2),            # 鼻子到雙眼
    (1, 3), (2, 4),            # 左眼到左耳，右眼到右耳
    (0, 5), (0, 6),            # 鼻子到雙肩
    (5, 7), (7, 9),            # 左肩到左手肘，再到左手腕
    (6, 8), (8, 10),           # 右肩到右手肘，再到右手腕
    (5, 11), (6, 12),          # 左肩到左髖，右肩到右髖
    (11, 13), (13, 15),        # 左髖到左膝，再到左腳踝
    (12, 14), (14, 16),        # 右髖到右膝，再到右腳踝
    (11, 12)                   # 左髖到右髖
]


# 載入模型
model = YOLO('yolo11x-pose.pt')

# 讀取圖片並進行預測
img_path = './test2.png'
results = model(img_path)

# 讀取圖片
img = cv2.imread(img_path)

# 轉換顏色 (因為 OpenCV 讀取 BGR 格式)
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# 遍歷每個偵測結果，取得關鍵點並繪製骨架
for result in results:
    keypoints = result.keypoints.xy.cpu().numpy()  # 取得所有關鍵點座標
    print(keypoints.shape)
    
    # 遍歷每個偵測到的物體（例如多個人物）
    for person_keypoints in keypoints:
        
        # 畫點
        for (x, y) in person_keypoints:
            if x > 0 and y > 0:  # 過濾掉無效座標 (0, 0)
                cv2.circle(img, (int(x), int(y)), radius=5, color=(255, 0, 0), thickness=-1)
        
        # 畫線
        for (start, end) in connections:
            if person_keypoints[start][0] > 0 and person_keypoints[start][1] > 0 and \
               person_keypoints[end][0] > 0 and person_keypoints[end][1] > 0:
                pt1 = (int(person_keypoints[start][0]), int(person_keypoints[start][1]))
                pt2 = (int(person_keypoints[end][0]), int(person_keypoints[end][1]))
                cv2.line(img, pt1, pt2, color=(0, 255, 0), thickness=2)

# 顯示結果
cv2.imshow('Image with Skeletons', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 儲存結果
cv2.imwrite('./result.png', img)