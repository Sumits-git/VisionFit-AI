import os
import sys
import subprocess
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import PhotoImage
from PIL import Image, ImageTk
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"

def run_module(module_name):
    python = sys.executable
    module_path = BASE / f"{module_name}.py"
    if not module_path.exists():
        tb.dialogs.Messagebox.show_error(f"Module {module_name} not found.")
        return
    subprocess.Popen([python, str(module_path)])

# ---------------- MAIN WINDOW ----------------
app = tb.Window(themename="superhero")
app.title("VisionFit AI: Pose & Rep Assistant")
app.geometry("980x620")

# ---------- BACKGROUND IMAGE ----------
bg_path = ASSETS / "bg_main.jpg"
if bg_path.exists():
    try:
        bg_img = Image.open(bg_path).resize((980, 620))
        bg_photo = ImageTk.PhotoImage(bg_img)
        bg_label = tb.Label(app, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print("Failed to load background:", e)

# ---------------- TOP BAR ----------------
top = tb.Frame(app, padding=10)
top.pack(fill=X)

# Change the Top Bar Label
tb.Label(
    top, text='🏋️ VisionFit AI', 
    font=('Poppins', 20, 'bold'), 
    bootstyle='default'
).pack(side=LEFT, padx=10)

# ---------------- LEFT PANEL ----------------
left = tb.Frame(app, padding=12, bootstyle="dark")
left.place(x=20, y=80, width=260, height=460)

profile_title = tb.Label(left, text='Profile', font=('Poppins', 14, 'bold'))
profile_title.pack(pady=(0,10))

# Load avatar icon
avatar_icon = ASSETS / "avatar.png"
if avatar_icon.exists():
    img = Image.open(avatar_icon).resize((64, 64))
    avatar_photo = ImageTk.PhotoImage(img)
else:
    avatar_photo = PhotoImage(width=1, height=1)

avatar = tb.Label(
    left, 
    image=avatar_photo, 
    text=' Hello, User! \nReady for your workout?', 
    compound=LEFT, 
    font=('Poppins', 10),
    anchor='w'
)
avatar.image = avatar_photo
avatar.pack(fill=X, pady=6)

# Stats
stats_frame = tb.Frame(left, padding=8)
stats_frame.pack(pady=12, fill=X)
tb.Label(stats_frame, text='Total Sessions: 0', font=('Poppins', 10)).pack(anchor='w')
tb.Label(stats_frame, text='Total Reps (all): 0', font=('Poppins', 10)).pack(anchor='w')

tb.Button(
    left, 
    text='📊 Open Analytics', 
    bootstyle='info-outline', 
    command=lambda: run_module('analytics')
).pack(fill=X, pady=(20,0))

# ---------------- CENTER GRID ----------------
center = tb.Frame(app, padding=12)
center.place(x=310, y=80, width=640, height=460)

cards = [
    ('Push-up', 'Start push-up counter with pose guidance', 'pushup', 'success', 'push-up.png'),
    ('Pull-up', 'Track your pull-ups with AI', 'pullup', 'primary', 'pull-up.png'),
    ('Sit-up', 'Analyze your sit-up form', 'situp', 'warning', 'sit-up.png'),
    ('Squat', 'Improve your squat posture', 'squat', 'secondary', 'squat.png'),
    ('Skipping', 'Detect jump-rope repetitions', 'skipping', 'danger', 'skipping-rope.png'),
    ('Yoga', 'Detect yoga poses with AI', 'yoga', 'info', 'lotus.png'),
]

r = 0; c = 0
for name, desc, module, style, icon_file in cards:
    card = tb.Frame(center, padding=12, bootstyle="dark")
    card.grid(row=r, column=c, padx=12, pady=12, sticky='nsew')

    # Load icon if exists
    icon_path = ASSETS / icon_file
    if icon_path.exists():
        icon_img = Image.open(icon_path).resize((48, 48))
        icon_photo = ImageTk.PhotoImage(icon_img)
        lbl_icon = tb.Label(card, image=icon_photo)
        lbl_icon.image = icon_photo
        lbl_icon.pack(pady=(0,8))

    tb.Label(card, text=name, font=('Poppins', 14, 'bold')).pack()
    tb.Label(card, text=desc, wraplength=220, font=('Poppins', 9)).pack(pady=(6,12))
    tb.Button(
        card, text='▶ Start', 
        bootstyle=f"{style}-outline", 
        command=lambda m=module: run_module(m)
    ).pack(side=BOTTOM, fill=X)
    
    c += 1
    if c > 2:
        c = 0
        r += 1

for i in range(3):
    center.grid_columnconfigure(i, weight=1)
for i in range(3):
    center.grid_rowconfigure(i, weight=1)

# Lift all widgets above background
top.lift()
left.lift()
center.lift()

# ---------------- FOOTER ----------------
footer = tb.Label(
    app, 
    text='Built with ❤️ using Mediapipe • OpenCV • Tkinter • ttkbootstrap', 
    anchor='center',
    font=('Poppins', 9)
)
footer.pack(side=BOTTOM, pady=8)

# ---------------- MAINLOOP ----------------
if __name__ == '__main__':
    app.mainloop()
