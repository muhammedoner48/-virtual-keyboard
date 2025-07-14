import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import math
import pygame
import os

pygame.init()
pygame.mixer.init()

sound_files = {key.upper(): f"{key.upper()}.wav" for key in "QWERTYUIOPASDFGHJKLZXCVBNM"}
sound_files["SPACE"] = "SPACE.wav"
sound_files["ENTER"] = "ENTER.wav"
sound_files["BACKSPACE"] = "BACKSPACE.wav"
sound_files["SHIFT"] = "SHIFT.wav"

def play_key_sound(key):
    file_name = 'sounds/'+ sound_files.get(key.upper())
    print(file_name)
    if file_name and os.path.exists(file_name):
        try:
            pygame.mixer.Sound(file_name).play()
        except Exception as e:
            print(f"Ses çalınamadı: {e}")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

rows = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM")
]

key_width, key_height = 60, 60
space_width = 240
func_width = 80
func_height = 30
gap = 10

last_click_time = 0
backspace_hold_start = None
shift_active = False
highlighted_key = None
highlight_start_time = 0
highlight_duration = 0.5
typed_text = ""

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (1280, 720))
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    key_positions = []
    start_y = h - 300

    for row_index, row_keys in enumerate(rows):
        total_row_width = len(row_keys) * key_width + (len(row_keys) - 1) * gap
        start_x = (w - total_row_width) // 2
        for i, key in enumerate(row_keys):
            x = start_x + i * (key_width + gap)
            y = start_y + row_index * (key_height + gap)
            key_positions.append((key, x, y, key_width, key_height))

    # BACKSPACE tuşunu P tuşunun sağına yerleştir
    p_key = next((item for item in key_positions if item[0] == 'P'), None)
    if p_key:
        backspace_x = p_key[1] + key_width + gap
        backspace_y = p_key[2]
    else:
        backspace_x = w - func_width - 30
        backspace_y = start_y - 2 * key_height - gap
    key_positions.append(("BACKSPACE", backspace_x, backspace_y, func_width, func_height))

    # ALT SATIRLAR: SPACE, SHIFT, ENTER
    space_x = (w - space_width) // 2
    space_y = start_y + len(rows) * (key_height + gap)
    key_positions.append(("SPACE", space_x, space_y, space_width, func_height))

    shift_x = space_x - gap - func_width
    key_positions.append(("SHIFT", shift_x, space_y, func_width, func_height))

    enter_x = space_x + space_width + gap
    key_positions.append(("ENTER", enter_x, space_y, func_width, func_height))

    current_time = time.time()

    # Text kutusu
    text_box_height = 40
    text_box_y = start_y - 60
    cv2.rectangle(frame, (40, text_box_y), (w - 40, text_box_y + text_box_height), (50, 50, 50), -1)
    cv2.putText(frame, typed_text, (50, text_box_y + 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    for key, x, y, width, height in key_positions:
        if highlighted_key == key and current_time - highlight_start_time < highlight_duration:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)
        cv2.rectangle(frame, (x, y), (x + width, y + height), color, -1)
        font_scale = 0.6 if len(key) > 1 else 0.7
        text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        cv2.putText(frame, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            index_tip = (int(lm[8].x * w), int(lm[8].y * h))
            thumb_tip = (int(lm[4].x * w), int(lm[4].y * h))

            cv2.circle(frame, index_tip, 10, (0, 255, 0), -1)
            cv2.circle(frame, thumb_tip, 10, (0, 255, 0), -1)

            touching = distance(index_tip, thumb_tip) < 40

            if touching:
                if backspace_hold_start is None:
                    backspace_hold_start = time.time()
                elif time.time() - backspace_hold_start > 3:
                    if len(typed_text) > 0:
                        pyautogui.press("backspace")
                        typed_text = typed_text[:-1]
                    last_click_time = time.time() - 0.9
            else:
                backspace_hold_start = None

            if touching and time.time() - last_click_time > 1:
                for key, x, y, width, height in key_positions:
                    if x < index_tip[0] < x + width and y < index_tip[1] < y + height:
                        if key == "SPACE":
                            pyautogui.write(" ")
                            typed_text += " "
                        elif key == "ENTER":
                            pyautogui.press("enter")
                            typed_text += "\n"
                        elif key == "BACKSPACE":
                            pyautogui.press("backspace")
                            typed_text = typed_text[:-1]
                        elif key == "SHIFT":
                            shift_active = not shift_active
                        else:
                            char = key.upper() if shift_active else key.lower()
                            pyautogui.write(char)
                            typed_text += char
                        play_key_sound(key)
                        last_click_time = time.time()
                        highlighted_key = key
                        highlight_start_time = current_time
                        break

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Sanal Klavye", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
        
cap.release()
cv2.destroyAllWindows()
