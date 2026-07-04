#!/usr/bin/env python
# coding: utf-8

# # Image Navigator with hand gestures

# In[1]:


import cv2
import mediapipe as mp
import numpy as np
import os

# In[2]:


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# In[3]:


image_folder = "images"
image_files = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
if not image_files:
    raise ValueError("No images found in the specified folder!")

# In[4]:


current_index = 0
scale_factor = 1.0
drag_start = None 
zooming = False

# In[5]:


image = cv2.imread(image_files[current_index])
original_shape = image.shape[:2]

# In[6]:


def zoom_image(image, scale):
    h, w = image.shape[:2]
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    return resized

# In[7]:


cap = cv2.VideoCapture(0)

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

            
            landmarks = hand_landmarks.landmark
            index_tip = (int(landmarks[8].x * w), int(landmarks[8].y * h))
            middle_tip = (int(landmarks[12].x * w), int(landmarks[12].y * h))
            thumb_tip = (int(landmarks[4].x * w), int(landmarks[4].y * h))

            
            dist_thumb_index = np.linalg.norm(np.array(thumb_tip) - np.array(index_tip))

            
            if abs(index_tip[0] - middle_tip[0]) > 100:  
                if index_tip[0] > middle_tip[0]:  
                    current_index = (current_index - 1) % len(image_files)
                else:  
                    current_index = (current_index + 1) % len(image_files)

                
                image = cv2.imread(image_files[current_index])
                scale_factor = 1.0  
                cv2.waitKey(500)  

            
            if dist_thumb_index < 40:  
                scale_factor = min(scale_factor + 0.05, 2.0)
            elif dist_thumb_index > 100:  
                scale_factor = max(scale_factor - 0.05, 0.5)

    
    displayed_image = zoom_image(image, scale_factor)

    
    cv2.imshow("Hand Gesture Image Viewer", displayed_image)
    cv2.imshow("Camera Feed", frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# In[8]:


cap.release()
cv2.destroyAllWindows()

# In[ ]:



