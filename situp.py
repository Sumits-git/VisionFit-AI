import cv2, mediapipe as mp, numpy as np, time, sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parent / 'tracker.db'
mp_pose, mp_drawing = mp.solutions.pose, mp.solutions.drawing_utils

def calculate_angle(a,b,c):
    a,b,c = np.array(a),np.array(b),np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360-angle if angle>180 else angle

def ensure_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS sessions(id INTEGER PRIMARY KEY, exercise TEXT, reps INT, duration REAL, timestamp TEXT)')
    conn.commit(); conn.close()

def log_session(exercise,reps,duration):
    conn = sqlite3.connect(DB)
    conn.execute('INSERT INTO sessions(exercise,reps,duration,timestamp) VALUES (?,?,?,?)',(exercise,reps,duration,datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def main():
    ensure_db()
    cap = cv2.VideoCapture(0)
    counter, stage = 0, None
    start = time.time()
    with mp_pose.Pose() as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame = cv2.flip(frame,1)
            results = pose.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                hip = [lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x, lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                shoulder = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                knee = [lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                angle = calculate_angle(shoulder, hip, knee)
                if angle > 130: stage = "down"
                if angle < 100 and stage == "down":
                    stage = "up"; counter += 1
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                cv2.putText(frame, f'Sit-ups: {counter}', (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0,255,0), 3)
            cv2.imshow('Sit-up Counter', frame)
            if cv2.waitKey(10)&0xFF==27: break
    cap.release(); cv2.destroyAllWindows()
    log_session('situp',counter,time.time()-start)
    print("Sit-ups:", counter)

if __name__=="__main__":
    main()
