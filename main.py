# 匯入所需模組
import cv2                     # OpenCV，用於影像處理與攝影機控制
import mediapipe as mp         # MediaPipe，用於手部關鍵點偵測
import pyautogui               # 控制滑鼠
import time                    # 處理時間控制
from collections import deque  # 雙向佇列，用於平滑化滑鼠移動
import numpy as np             # 數學運算工具
import math                    # 提供平方根等基本數學函式

# 判斷是否為握拳（✊）
def is_fist(landmarks):
    # 定義各指尖與對應第二關節的 landmark index
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]
    curled_fingers = 5  # 預設認為全部手指都是彎曲的
    threshold = 0.03    # 閾值：越小代表要求越靠近

    # 比較每根手指尖與第二關節的 y 座標
    for tip, pip in zip(finger_tips, finger_pips):
        tip_y = landmarks[tip].y
        pip_y = landmarks[pip].y
        if tip_y > pip_y:  # 如果指尖比關節還低，表示彎曲
            curled_fingers += 1

    return curled_fingers >= 4  # 至少 4 根彎曲就當作握拳

# 取得螢幕解析度
screen_w, screen_h = pyautogui.size()

# 初始化 MediaPipe Hands 模組
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils  # 用於畫手部骨架

# 建立滑鼠移動軌跡的緩衝區，用於平滑化滑鼠座標
mouse_history = deque(maxlen=5)

# 控制定點擊頻率（冷卻時間），避免重複觸發
click_cooldown = 0.5
last_click_time = time.time() - click_cooldown

# 啟動攝影機
cap = cv2.VideoCapture(0)

# 設定 OpenCV 視窗為全螢幕
cv2.namedWindow("Hand Tracking", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Hand Tracking", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# 主迴圈
while cap.isOpened():
    success, frame = cap.read()  # 讀取攝影機畫面
    if not success:
        continue  # 如果讀取失敗就跳過這幀

    frame = cv2.flip(frame, 1)  # 左右鏡像翻轉，符合自然操作
    h, w, _ = frame.shape       # 取得畫面高度與寬度
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 轉換顏色給 MediaPipe
    result = hands.process(rgb_frame)  # 執行手部偵測

    # 如果有偵測到手
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # 取得 Landmark 4（拇指指尖）與 Landmark 8（食指指尖）
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]

            # 畫出食指指尖的圓圈提示
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)
            cv2.circle(frame, (x, y), 10, (255, 0, 255), -1)

            # 將食指位置轉成螢幕座標
            screen_x = int(index_tip.x * screen_w)
            screen_y = int(index_tip.y * screen_h)
            mouse_history.append((screen_x, screen_y))  # 加入滑鼠歷史紀錄

            # 當滑鼠移動記錄滿時，計算平均座標並移動滑鼠
            if len(mouse_history) == mouse_history.maxlen:
                avg_x = int(np.mean([p[0] for p in mouse_history]))
                avg_y = int(np.mean([p[1] for p in mouse_history]))
                pyautogui.moveTo(avg_x, avg_y)

            # 計算拇指與食指的距離（判斷是否觸碰）
            dx = index_tip.x - thumb_tip.x
            dy = index_tip.y - thumb_tip.y
            dist = math.sqrt(dx * dx + dy * dy)

            # 如果距離很近，並且超過冷卻時間，就觸發滑鼠點擊
            if dist < 0.03 and (time.time() - last_click_time) > click_cooldown:
                pyautogui.click()
                print("🖱️ Clicked!")
                last_click_time = time.time()

            # 如果偵測到握拳，就退出程式
            if is_fist(hand_landmarks.landmark):
                print("👊 偵測到握拳，退出程式！")
                cap.release()
                cv2.destroyAllWindows()
                hands.close()
                exit()

            # 畫出手部骨架與連線
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 顯示畫面
    cv2.imshow("Hand Tracking", frame)

    # 按下 ESC 或點視窗右上角關閉都能退出
    if cv2.waitKey(1) & 0xFF == 27 or cv2.getWindowProperty("Hand Tracking", cv2.WND_PROP_VISIBLE) < 1:
        break

# 資源釋放
cap.release()
cv2.destroyAllWindows()
hands.close()
