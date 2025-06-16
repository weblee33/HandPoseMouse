# ------------------ 套件載入 ------------------
import cv2
import mediapipe as mp
import pyautogui
import time
import numpy as np
import math

# ------------------ 可調參數 ------------------
EMA_ALPHA           = 0.4   # 指數移動平均係數
CLICK_THRESHOLD     = 0.05  # 點擊判斷距離 (拇指-食指)
CLICK_COOLDOWN      = 0.5   # 點擊冷卻秒數
FIST_DIST_THRESHOLD = 0.08  # 拳頭判斷距離
FIST_FRAMES         = 7     # 連續幀數才視為握拳
TARGET_FPS          = 30    # FPS 上限
CAM_W, CAM_H        = 480, 270

# ------------------------------------------------
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()

# -------- MediaPipe Hands 初始化 (輕量模型) -------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1,
                       min_detection_confidence=0.7,
                       model_complexity=0)

# ---------- 狀態變數 ----------
mouse_pos_ema  = None        # EMA 平滑游標
last_click_time = time.time() - CLICK_COOLDOWN
prev_dist       = 1.0        # 前一幀拇指-食指距離
fist_streak     = 0          # 連續握拳幀計數

# ------------ 攝影機 ------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
prev_time = time.time()

# ----------- 函式：判斷握拳 -----------
def is_fist(landmarks):
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]
    curled = sum(landmarks[tip].y > landmarks[pip].y + 0.02
                 for tip, pip in zip(finger_tips, finger_pips))
    dist = math.hypot(landmarks[8].x - landmarks[4].x,
                      landmarks[8].y - landmarks[4].y)
    return dist < FIST_DIST_THRESHOLD and curled >= 3

# ------------------ 主迴圈 ------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        lm = results.multi_hand_landmarks[0]

        # ----------- 取關鍵 Landmark -----------
        thumb_tip  = lm.landmark[4]   # 拇指尖
        index_tip  = lm.landmark[8]   # 食指尖
        index_dip  = lm.landmark[7]   # 食指 DIP（較穩定）

        # ----------- 游標移動 (常態：index_dip) ----------
        target_x = int(index_dip.x * screen_w)
        target_y = int(index_dip.y * screen_h)

        if mouse_pos_ema is None:
            mouse_pos_ema = np.array([target_x, target_y], float)
        mouse_pos_ema = (1-EMA_ALPHA)*mouse_pos_ema + EMA_ALPHA*np.array([target_x, target_y])
        pyautogui.moveTo(int(mouse_pos_ema[0]), int(mouse_pos_ema[1]))

        # ----------- 拇指-食指距離 -----------
        dist = math.hypot(index_tip.x - thumb_tip.x,
                          index_tip.y - thumb_tip.y)

        # 邊緣觸發點擊：上一幀距離>門檻，本幀<=門檻
        if prev_dist > CLICK_THRESHOLD and dist <= CLICK_THRESHOLD and \
           (time.time() - last_click_time) > CLICK_COOLDOWN:

            # 以「拇指-食指中心點」當作真實點擊座標
            center_x = int(((index_tip.x + thumb_tip.x) / 2) * screen_w)
            center_y = int(((index_tip.y + thumb_tip.y) / 2) * screen_h)
            # pyautogui.moveTo(center_x, center_y)  # 撐住游標不偏移
            pyautogui.click()
            print("🖱️ Clicked!")
            last_click_time = time.time()

        prev_dist = dist  # 更新前一幀距離

        # ----------- 握拳判定 -----------
        if is_fist(lm.landmark):
            fist_streak += 1
            if fist_streak >= FIST_FRAMES:
                print("👊 偵測到握拳，退出程式！")
                break
        else:
            fist_streak = 0

    # ---------------- 畫面顯示 ----------------
    cv2.imshow("Hand Tracking", frame)

    # 離開條件
    if cv2.waitKey(1) & 0xFF == 27 or \
       cv2.getWindowProperty("Hand Tracking", cv2.WND_PROP_VISIBLE) < 1:
        break

    # FPS 控制
    elapsed = time.time() - prev_time
    time.sleep(max(0, (1 / TARGET_FPS) - elapsed))
    prev_time = time.time()

# -------- 資源釋放 --------
cap.release()
cv2.destroyAllWindows()
hands.close()
