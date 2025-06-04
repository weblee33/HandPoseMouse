# HandPoseMouse 

A Python-based hand gesture mouse controller using **MediaPipe** and **OpenCV**, enabling users to move and click the mouse with just their hand movements—no physical device needed.

---

## Features

-  **Hand Tracking Mouse Movement**  
  Move your cursor using your **index fingertip** in real time.

-  **Pinch to Click**  
  When the **thumb and index finger tips** come close, a mouse click is triggered.

-  **Fist to Exit**  
  Make a fist gesture to immediately exit the program.

-  **Smooth Cursor Movement**  
  Uses a moving average of recent fingertip positions for smooth tracking.

-  **Fullscreen Display**  
  The webcam window runs in fullscreen mode for immersive interaction.

---

##  Requirements

Install the following packages via pip:

```bash
pip install opencv-python mediapipe pyautogui numpy
