import cv2
import mediapipe as mp
import numpy as np
import threading
import tkinter as tk
from tkinter import Label, OptionMenu, StringVar
from PIL import Image, ImageTk

class ColorIdentifierApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Color Identifier")

        self.video_label = Label(window)
        self.video_label.pack()

        self.color_label = Label(window, text="Color: ", font=("Arial", 16))
        self.color_label.pack()

        # Camera selection dropdown
        self.available_cams = self.get_available_cameras()
        self.cam_index = 0
        self.selected_cam = StringVar(value=str(self.cam_index))
        self.cam_menu = OptionMenu(window, self.selected_cam, *map(str, self.available_cams), command=self.change_camera)
        self.cam_menu.pack(pady=5)

        self.running = True
        self.current_color = "#000000"
        self.frame = None
        self.photo = None

        self.thread = threading.Thread(target=self.capture_video)
        self.thread.start()

        self.update_gui()

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def get_available_cameras(self, max_tested=5):
        cams = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cams.append(i)
                cap.release()
        return cams if cams else [0]

    def change_camera(self, value):
        self.cam_index = int(value)
        self.running = False
        self.thread.join()
        self.running = True
        self.thread = threading.Thread(target=self.capture_video)
        self.thread.start()

    def capture_video(self):
        cap = cv2.VideoCapture(self.cam_index)
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, _ = rgb_frame.shape
            center_x, center_y = w // 2, h // 2

            cv2.circle(frame, (center_x, center_y), 5, (255, 255, 255), 2)

            b, g, r = frame[center_y, center_x]
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            self.current_color = hex_color
            self.frame = frame.copy()

        cap.release()

    def update_gui(self):
        if self.frame is not None:
            frame = self.frame.copy()
            b, g, r = frame[frame.shape[0] // 2, frame.shape[1] // 2]
            hex_color = self.current_color

            self.update_color_label(hex_color)

            cv2.rectangle(frame, (10, 10), (100, 60), (int(b), int(g), int(r)), -1)
            cv2.putText(frame, hex_color, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=image)
            self.video_label.configure(image=self.photo)

        self.window.after(30, self.update_gui)

    def update_color_label(self, color):
        self.color_label.config(text=f"Color: {color}", bg=color, fg="white")

    def on_close(self):
        self.running = False
        self.thread.join()
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorIdentifierApp(root)
    root.mainloop()
