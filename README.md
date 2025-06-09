# 🖐️ MediaPipe + PyAutoGUI 手動控制滑鼠系統

本專案透過 OpenCV + MediaPipe 傳感辦證手部關鍵點，使用 `pyautogui` 控制滑鼠漸動與點擊操作。提供滑順漸動、抽指點擊、握拳離開等功能，可作為簡易滑鼠替代輸入介面。

## 🎞️ 依賴套件

請先安裝以下 Python 套件：

```bash
pip install opencv-python mediapipe pyautogui numpy
```

## 📋 功能說明

| 功能     | 說明                                                    |
| ------ | ----------------------------------------------------- |
| 漸動滑鼠   | 使用 **食指第二關節 (index\_dip)** 控制滑鼠位置，透過指數移動平均 (EMA) 平滑處理 |
| 點擊操作   | 抽指與食指尖端靠近時觸發點擊事件 (設有冷卻時間)                             |
| 握拳離開   | 當傳感連續握拳數序後，自動退出程式                                     |
| FPS 控制 | 最大顯示平率可調整以減少 CPU/GPU 負擔                               |

## 🎮 操作方式

* 👈 **滑鼠漸動**：將手放在鏡頭前，透過食指第二關節控制漸動位置。
* 🤏 **點擊事件**：將 **食指尖端** 靠近 **抽指尖端**，觸發一次滑鼠點擊。
* 👊 **握拳離開**：持續握拳超過預設序數 (`FIST_FRAMES`) 自動離開程式。
* ⎋ **ESC 鍵**：可隨時按下退出。

## 🔧 可調參數

程式中有多項參數可根據需要進行調整：

```python
EMA_ALPHA           = 0.4   # 漸動平滑系數（值越大越靈敏）
CLICK_THRESHOLD     = 0.05  # 點擊距離關值（抽指與食指）
CLICK_COOLDOWN      = 0.5   # 點擊冷卻時間（秒）
FIST_DIST_THRESHOLD = 0.08  # 握拳判定距離
FIST_FRAMES         = 7     # 判定握拳需要連續序數
TARGET_FPS          = 30    # 顯示畫面最大 FPS
CAM_W, CAM_H        = 480, 270  # 攝影機解析度
```

## 📷 預設攝影機設定

預設使用裝置的 **第一支攝影機**，並設定畫面寬高為 480x270：

```python
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
```

## 🚩 結束程式的方式

* 連續握拳 7 序以上 (可調整)
* 關閉視窗
* 按下 `ESC` 鍵

## 📁 檔案結構

```
hand_mouse_control.py   # 主程式
README.md               # 說明文件
```

## 💡 注意事項

* 建議在光線充足的環境下操作。
* 若滑鼠移動不順或延遲，請嘗試降低解析度或調整 `EMA_ALPHA`。
* 若滑鼠自動移動異常，請確認 `pyautogui.FAILSAFE`是否設為 `False` (程式中已預設關閉)。
