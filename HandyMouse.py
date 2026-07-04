#!/usr/bin/env python
# coding: utf-8

# # Handy Mouse

import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import time
pyautogui.PAUSE = 0.01

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9, max_num_hands=2)

screen_w, screen_h = pyautogui.size()
frame_margin = 0.15

prev_x, prev_y = None, None
clicking = False
dragging = False
screenshot_taken = False
screenshot_cooldown = 2
last_screenshot_time = time.time()
scroll_active = False

cap = cv2.VideoCapture(0)
swipe_start_x = None
swipe_cooldown = 1.0
last_swipe_time = time.time()
swipe_threshold = 0.15  # 15% of frame width movement

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    hand_landmarks_list = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            hand_landmarks_list.append(hand_landmarks)

    if hand_landmarks_list:
        hand_landmarks = hand_landmarks_list[0]
        index_tip = hand_landmarks.landmark[8]

        norm_x = np.interp(index_tip.x, [frame_margin, 1 - frame_margin], [0, 1])
        norm_y = np.interp(index_tip.y, [frame_margin, 1 - frame_margin], [0, 1])
        cursor_x = int(np.clip(norm_x, 0, 1) * screen_w)
        cursor_y = int(np.clip(norm_y, 0, 1) * screen_h)
        cursor_x = max(1, min(screen_w - 2, cursor_x))
        cursor_y = max(1, min(screen_h - 2, cursor_y))

        if prev_x is not None and prev_y is not None:
            cursor_x = int(0.9 * prev_x + 0.1 * cursor_x)
            cursor_y = int(0.9 * prev_y + 0.1 * cursor_y)

        pyautogui.moveTo(cursor_x, cursor_y)
        prev_x, prev_y = cursor_x, cursor_y

    if hand_landmarks_list:
        hand_landmarks = hand_landmarks_list[0]
        index_tip = hand_landmarks.landmark[8]
        index_base = hand_landmarks.landmark[5]
        middle_tip = hand_landmarks.landmark[12]
        thumb_tip = hand_landmarks.landmark[4]

        # Left Click
        if index_tip.y < index_base.y - 0.05 and middle_tip.y > index_base.y:
            if not clicking:
                pyautogui.click()
                clicking = True
        else:
            clicking = False

        # Right Click
        if middle_tip.y < index_base.y and index_tip.y > index_base.y:
            pyautogui.rightClick()

        # Double Click
        if index_tip.y < index_base.y and middle_tip.y < index_base.y:
            pyautogui.doubleClick()

        # Drag and Drop
        pinch_distance = np.linalg.norm(np.array([index_tip.x, index_tip.y]) - np.array([thumb_tip.x, thumb_tip.y]))

        if pinch_distance < 0.025:
            if not dragging:
                pyautogui.mouseDown()
                dragging = True
        else:
            if dragging:
                pyautogui.mouseUp()
                dragging = False

        # Scrolling
        palm_y = hand_landmarks.landmark[0].y
        if palm_y < 0.3:
            pyautogui.scroll(5)
            scroll_active = True
        elif palm_y > 0.7:
            pyautogui.scroll(-5)
            scroll_active = True
        else:
            scroll_active = False

        # Fist Swipe (all fingers curled = fist, move hand left/right)
        wrist = hand_landmarks.landmark[0]
        finger_tips = [hand_landmarks.landmark[i] for i in [8, 12, 16, 20]]
        finger_bases = [hand_landmarks.landmark[i] for i in [5, 9, 13, 17]]

        is_fist = all(tip.y > base.y for tip, base in zip(finger_tips, finger_bases))

        if is_fist:
            current_x = wrist.x
            if swipe_start_x is None:
                swipe_start_x = current_x
            else:
                delta = current_x - swipe_start_x
                current_time = time.time()
                if abs(delta) > swipe_threshold and current_time - last_swipe_time > swipe_cooldown:
                    if delta > 0:
                        pyautogui.hotkey('alt', 'shift', 'tab')
                    else:
                        pyautogui.hotkey('alt', 'tab')
                    last_swipe_time = current_time
                    swipe_start_x = None
        else:
            swipe_start_x = None

    # Zoom In/Out
    if len(hand_landmarks_list) == 2:
        hand1, hand2 = hand_landmarks_list[0], hand_landmarks_list[1]
        index_tip_1 = hand1.landmark[8]
        index_tip_2 = hand2.landmark[8]

        x1, y1 = int(index_tip_1.x * w), int(index_tip_1.y * h)
        x2, y2 = int(index_tip_2.x * w), int(index_tip_2.y * h)

        distance = np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2]))

        if distance > 100:
            pyautogui.hotkey("ctrl", "+")
        elif distance < 50:
            pyautogui.hotkey("ctrl", "-")

        if distance < 30:
            current_time = time.time()
            if not screenshot_taken and current_time - last_screenshot_time > screenshot_cooldown:
                pyautogui.screenshot("screenshot.png")
                print("Screenshot taken!")
                last_screenshot_time = current_time
                screenshot_taken = True
        else:
            screenshot_taken = False

    cv2.putText(frame, "Cursor: Move Hand", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Click: Index Up", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Right Click: Middle Up", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Double Click: 2 Fingers Up", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Drag: Pinch Index+Thumb", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Scroll: Hand Up/Down", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Zoom: 2 Hands Apart/Close", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Screenshot: Cross Index Fingers", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv2.putText(frame, "Swipe: Make Fist + Move L/R", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    cv2.imshow("Gesture-Controlled Mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()