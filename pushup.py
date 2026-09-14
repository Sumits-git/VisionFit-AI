# import cv2
# import mediapipe as mp
# import numpy as np
# from pathlib import Path
# import time
# import sqlite3
# from datetime import datetime

# DB = Path(__file__).resolve().parent / 'tracker.db'

# def ensure_db():
#     conn = sqlite3.connect(DB)
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS sessions
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT, exercise TEXT, reps INTEGER, duration REAL, timestamp TEXT)''')
#     conn.commit()
#     conn.close()

# def log_session(exercise, reps, duration):
#     conn = sqlite3.connect(DB)
#     c = conn.cursor()
#     c.execute('INSERT INTO sessions (exercise, reps, duration, timestamp) VALUES (?,?,?,?)',
#               (exercise, reps, duration, datetime.utcnow().isoformat()))
#     conn.commit()
#     conn.close()

# mp_pose = mp.solutions.pose
# mp_drawing = mp.solutions.drawing_utils

# def calculate_angle(a, b, c):
#     a, b, c = np.array(a), np.array(b), np.array(c)
#     radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     angle = np.abs(radians*180.0/np.pi)
#     if angle > 180.0:
#         angle = 360-angle
#     return angle

# def main():
#     ensure_db()
#     cap = cv2.VideoCapture(0)
#     count = 0
#     stage = None
#     start_time = time.time()
#     with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#         while cap.isOpened():
#             ret, frame = cap.read()
#             if not ret:
#                 break
#             frame = cv2.flip(frame, 1)
#             image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = pose.process(image)
#             image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#             if results.pose_landmarks:
#                 lm = results.pose_landmarks.landmark
#                 shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
#                 elbow = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
#                 wrist = [lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

#                 angle = calculate_angle(shoulder, elbow, wrist)
#                 if angle > 150:
#                     stage = 'up'
#                 if angle < 80 and stage == 'up':
#                     stage = 'down'
#                     count += 1

#                 mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#                 cv2.putText(image, f'Push-ups: {count}', (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)
#                 cv2.putText(image, f'Elbow angle: {int(angle)}', (30,90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

#             cv2.imshow('Push-up Counter - Press ESC to stop', image)
#             if cv2.waitKey(10) & 0xFF == 27:
#                 break
#     duration = time.time() - start_time
#     cap.release()
#     cv2.destroyAllWindows()
#     log_session('pushup', count, duration)
#     print(f'Session ended. Reps: {count}, Duration: {duration:.1f}s - logged to tracker.db')

# if __name__ == '__main__':
#     main()


import cv2
import mediapipe as mp
import numpy as np
import time
import sqlite3
import pyttsx3
import threading
from pathlib import Path
import ttkbootstrap as tb
from ttkbootstrap.constants import *

DB_PATH = Path(__file__).resolve().parent / "tracker.db"

# --- Audio Feedback System (Run in background thread to prevent camera lag) ---
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    def _speak():
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            pass
    threading.Thread(target=_speak, daemon=True).start()

# --- Biomechanical Angle Calculator ---
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
    return angle

# --- 8th Sem Feature: Show Beautiful Session Summary Window ---
def show_summary_popup(reps, duration, calories, avg_posture):
    popup = tb.Window(themename="superhero", title="Workout Session Summary")
    popup.geometry("450x350")
    
    tb.Label(popup, text="🎉 Session Completed!", font=("Poppins", 18, "bold"), bootstyle="success").pack(pady=15)
    
    stats_frame = tb.Frame(popup, padding=10)
    stats_frame.pack(fill=BOTH, expand=True)
    
    tb.Label(stats_frame, text=f"Total Reps: {reps}", font=("Poppins", 12)).pack(anchor="w", pady=5)
    tb.Label(stats_frame, text=f"Duration: {int(duration)} seconds", font=("Poppins", 12)).pack(anchor="w", pady=5)
    tb.Label(stats_frame, text=f"Estimated Energy: {calories:.2f} kcal", font=("Poppins", 12)).pack(anchor="w", pady=5)
    tb.Label(stats_frame, text=f"Form Accuracy Score: {int(avg_posture)}%", font=("Poppins", 12)).pack(anchor="w", pady=5)
    
    tb.Button(popup, text="Close & Log Data", bootstyle="success", command=popup.destroy).pack(pady=20)
    popup.mainloop()

# --- Main Tracking Core ---
def start_tracking():
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    
    # State tracking variables
    count = 0
    stage = "up"
    start_time = time.time()
    
    # Advanced Form Evaluation Tracking
    posture_scores = []
    last_voice_time = time.time()

    speak("Push up tracking activated. Keep your spine straight.")

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates for elbow angle (Shoulder-Elbow-Wrist)
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]