# AI Wellness Tracker
A local Python desktop app (Tkinter + ttkbootstrap) with Mediapipe/OpenCV based exercise pose detection and counters.

## Features included
- Home UI with modern color theme (ttkbootstrap)
- Push-up counter with pose detection (working)
- Placeholders for Pull-up, Sit-up, Skipping (ready to extend)
- SQLite logger (tracker.db) to save workout sessions
- Simple analytics view (Matplotlib) to plot history

## Run (recommended inside a virtualenv)
1. Install requirements:
   pip install -r requirements.txt
2. Run the app:
   python main.py

## Notes
- Requires a webcam for live pose detection.
- Mediapipe may need additional system dependencies on some platforms.
