#!/usr/bin/env python
# coding: utf-8

# # AirWrite 

# In[7]:


import cv2
import numpy as np
import mediapipe as mp

# In[ ]:


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9, max_num_hands=1)

# In[9]:


whiteboard = np.ones((600, 800, 3), dtype=np.uint8) * 255

# In[10]:


drawing = False
prev_x, prev_y = None, None
selected_color = (0, 0, 255)  
color_selected = False 

colors = {
    'Red': (0, 0, 255),
    'Green': (0, 255, 0),
    'Blue': (255, 0, 0),
    'Black': (0, 0, 0),
    'Eraser': (255, 255, 255)
}

# In[11]:


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

smooth_x, smooth_y = None, None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1) 
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            
            index_tip = hand_landmarks.landmark[8] 
            raw_x, raw_y = int(index_tip.x * w), int(index_tip.y * h)
            if smooth_x is None:
                smooth_x, smooth_y = raw_x, raw_y
            else:
                smooth_x = int(0.7 * smooth_x + 0.3 * raw_x)
                smooth_y = int(0.7 * smooth_y + 0.3 * raw_y)
            index_x, index_y = smooth_x, smooth_y

            
            index_base = hand_landmarks.landmark[5]  
            middle_base = hand_landmarks.landmark[9]  

            
            thumb_tip = hand_landmarks.landmark[4]  
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)

            
            if index_tip.y < index_base.y - 0.08 and index_tip.y < middle_base.y - 0.08:
                color_selected = False  
                if prev_x is not None and prev_y is not None:
                    cv2.line(whiteboard, (prev_x, prev_y), (index_x, index_y), selected_color, 3)
                prev_x, prev_y = index_x, index_y

            else:
                prev_x = None
                prev_y = None

            
            if index_y < 50 and not color_selected:
                if 50 < index_x < 150:
                    selected_color = colors['Red']
                elif 160 < index_x < 260:
                    selected_color = colors['Green']
                elif 270 < index_x < 370:
                    selected_color = colors['Blue']
                elif 380 < index_x < 480:
                    selected_color = colors['Black']
                elif 490 < index_x < 590:
                    selected_color = colors['Eraser']
                color_selected = True

    
    cv2.rectangle(frame, (50, 10), (150, 50), colors['Red'], -1)
    cv2.rectangle(frame, (160, 10), (260, 50), colors['Green'], -1)
    cv2.rectangle(frame, (270, 10), (370, 50), colors['Blue'], -1)
    cv2.rectangle(frame, (380, 10), (480, 50), colors['Black'], -1)
    cv2.rectangle(frame, (490, 10), (590, 50), colors['Eraser'], -1)
    cv2.putText(frame, "Color", (595, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

    
    cv2.imshow("AirWrite - Camera", frame)
    cv2.imshow("AirWrite - Whiteboard", whiteboard)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# In[12]:


cap.release()
cv2.destroyAllWindows()
