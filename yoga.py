import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path
import math

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# -------------------------------
# Helper Functions
# -------------------------------
def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

def get_pose_vector(landmarks):
    """Return key joint angles to compare between poses"""
    right = mp_pose.PoseLandmark
    l = landmarks
    # Right side
    shoulder = [l[right.RIGHT_SHOULDER.value].x, l[right.RIGHT_SHOULDER.value].y]
    elbow = [l[right.RIGHT_ELBOW.value].x, l[right.RIGHT_ELBOW.value].y]
    wrist = [l[right.RIGHT_WRIST.value].x, l[right.RIGHT_WRIST.value].y]
    hip = [l[right.RIGHT_HIP.value].x, l[right.RIGHT_HIP.value].y]
    knee = [l[right.RIGHT_KNEE.value].x, l[right.RIGHT_KNEE.value].y]
    ankle = [l[right.RIGHT_ANKLE.value].x, l[right.RIGHT_ANKLE.value].y]

    angles = [
        calculate_angle(shoulder, elbow, wrist),
        calculate_angle(hip, knee, ankle),
        calculate_angle(shoulder, hip, knee)
    ]
    return np.array(angles)

def cosine_similarity(a, b):
    """Return cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -------------------------------
# Reference Yoga Pose Angles (approximate templates)
# -------------------------------
POSES = {
    "Cobra Pose": np.array([160, 180, 40]),     # Straight arms, bent back
    "Warrior Pose": np.array([170, 90, 150]),   # One leg bent, arms extended
    "Tree Pose": np.array([160, 45, 110]),      # One leg up, standing tall
}

# -------------------------------
# Main Yoga Detector
# -------------------------------
def main():
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            frame = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                vec = get_pose_vector(lm)

                best_pose, best_score = None, -1
                for pose_name, ref_vec in POSES.items():
                    score = cosine_similarity(vec, ref_vec)
                    if score > best_score:
                        best_score = score
                        best_pose = pose_name

                # Draw landmarks
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                # Show current pose and confidence
                cv2.putText(frame, f'Pose: {best_pose}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 3)
                cv2.putText(frame, f'Confidence: {best_score:.2f}', (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

            cv2.imshow('Yoga Pose Detection', frame)
            if cv2.waitKey(10) & 0xFF == 27:  # ESC to exit
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
