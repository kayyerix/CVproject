import cv2
import time
import os
import threading
import pygame
import mediapipe as mp

# ========================
# Working directory
# ========================
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ========================
# Setup Sound
# ========================
pygame.mixer.init()

def play_sound(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

def play_plek_sequence():
    pygame.mixer.music.load("plek.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.load("jokowi.mp3")
    pygame.mixer.music.play()

# ========================
# Mediapipe setup
# ========================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands_detector = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ========================
# Camera
# ========================
cap = cv2.VideoCapture(0)

# ========================
# State control
# ========================
step = 0
last_trigger_time = 0
cooldown = 2

# ========================
# Detect finger state
# ========================
def get_fingers(hand_landmarks):

    fingers = []

    # Thumb
    if hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    tips = [8, 12, 16, 20]

    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

# ========================
# Main loop
# ========================
while True:

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands_detector.process(rgb)

    current_time = time.time()

    if result.multi_hand_landmarks and current_time - last_trigger_time > cooldown:

        for handLms in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            fingers = get_fingers(handLms)

            # ========================
            # 🤟 STEP 0  → SELAMAT
            # ========================
            if step == 0 and fingers == [1,1,0,0,1]:

                threading.Thread(
                    target=play_sound,
                    args=("selamat.mp3",)
                ).start()

                print("SELAMAT")

                step = 1
                last_trigger_time = current_time

            # ========================
            # ✊ STEP 1 → BERJUANG
            # ========================
            elif step == 1 and fingers == [0,0,0,0,0]:

                threading.Thread(
                    target=play_sound,
                    args=("berjuang.mp3",)
                ).start()

                print("BERJUANG")

                step = 2
                last_trigger_time = current_time

            # ========================
            # 👍 STEP 2 → SUKSES
            # ========================
            elif step == 2 and fingers == [1,0,0,0,0]:

                threading.Thread(
                    target=play_sound,
                    args=("sukses.mp3",)
                ).start()

                print("SUKSES")

                step = 3
                last_trigger_time = current_time

            # ========================
            # 🖐 STEP 3 → PLEK + JOKOWI
            # ========================
            elif step == 3 and fingers == [1,1,1,1,1]:

                threading.Thread(
                    target=play_plek_sequence
                ).start()

                print("PLEK")
                print("ERROR!!!")

                step = 0
                last_trigger_time = current_time

    # ========================
    # UI Text
    # ========================
    cv2.putText(
        frame,
        f"STEP: {step}",
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.imshow("Hand Gesture Sound System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()