import customtkinter as ctk
import cv2
from PIL import Image
import face_recognition
import numpy as np
import os
from datetime import datetime
import pyttsx3
import threading
import queue

# --- CLOUD COMMUNICATION SETUP ---
from dotenv import load_dotenv
from twilio.rest import Client

# Load secret keys from your .env vault
load_dotenv()
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SENDER = os.getenv("TWILIO_WHATSAPP_NUMBER")
TARGET_PHONE = os.getenv("TARGET_PHONE_NUMBER")

# Initialize Twilio Client
if TWILIO_SID and TWILIO_TOKEN:
    twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
else:
    twilio_client = None
    print("⚠️ Warning: Twilio credentials not found in .env file.")


def send_whatsapp(name, time_str):
    if twilio_client:
        try:
            message = twilio_client.messages.create(
                from_=TWILIO_SENDER,
                body=f"✅ FaceLogTZ Alert: {name.title()} has safely arrived at class at {time_str}.",
                to=TARGET_PHONE,
            )
            print(f"📱 WhatsApp successfully sent! ID: {message.sid}")
        except Exception as e:
            print(f"⚠️ WhatsApp failed to send: {e}")


# --- AUDIO QUEUE SYSTEM ---
audio_queue = queue.Queue()


def audio_worker():
    """A dedicated background worker that speaks names one by one."""
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)  # Make it speak a little faster!

    while True:
        # Wait for a name to enter the queue
        name = audio_queue.get()
        # Speak the name
        engine.say(f"Welcome {name.lower()}.")
        engine.runAndWait()
        # Tell the queue we finished this name
        audio_queue.task_done()


# Start the audio worker in the background immediately
threading.Thread(target=audio_worker, daemon=True).start()


# --- UI & LOGIC ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class FaceLogApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FaceLogTZ - Enterprise Dashboard")
        self.geometry("900x750")

        self.header_label = ctk.CTkLabel(
            self,
            text="FaceLogTZ Attendance System",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.header_label.pack(pady=20)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=10, padx=40, fill="both", expand=True)

        self.video_label = ctk.CTkLabel(
            self.main_frame, text="Loading Database...", font=ctk.CTkFont(size=20)
        )
        self.video_label.pack(pady=20)

        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Start Camera Stream",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            command=self.start_camera,
        )
        self.start_button.pack(pady=10)

        self.cap = None

        # --- AI BRAIN SETUP ---
        self.path = "known_faces"
        self.classNames = []
        self.encodeListKnown = []
        self.load_database()

    def load_database(self):
        print("Loading Database...")
        self.classNames = []
        self.encodeListKnown = []

        for item_name in os.listdir(self.path):
            item_path = os.path.join(self.path, item_name)

            if os.path.isdir(item_path):
                for img_name in os.listdir(item_path):
                    img_path = os.path.join(item_path, img_name)
                    curImg = cv2.imread(img_path)

                    if curImg is not None:
                        img_rgb = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
                        encodes = face_recognition.face_encodings(img_rgb)
                        if len(encodes) > 0:
                            self.encodeListKnown.append(encodes[0])
                            self.classNames.append(item_name.upper())

            elif os.path.isfile(item_path) and item_path.lower().endswith(
                (".png", ".jpg", ".jpeg")
            ):
                curImg = cv2.imread(item_path)
                if curImg is not None:
                    img_rgb = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
                    encodes = face_recognition.face_encodings(img_rgb)
                    if len(encodes) > 0:
                        self.encodeListKnown.append(encodes[0])
                        self.classNames.append(os.path.splitext(item_name)[0].upper())

        unique_names = set(self.classNames)
        print("Database Loaded! Found:", unique_names)
        self.video_label.configure(
            text=f"System Ready. {len(unique_names)} students loaded.\nClick Start."
        )

    def markAttendance(self, name):
        """Logs attendance only if the person hasn't been logged TODAY."""
        if not os.path.isfile("Attendance.csv"):
            with open("Attendance.csv", "w") as f:
                f.writelines("Name,Time,Date")

        with open("Attendance.csv", "r+") as f:
            myDataList = f.readlines()

            now = datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            time_string = now.strftime("%H:%M:%S")

            # Check if this person was already marked TODAY specifically
            already_marked_today = False

            for line in myDataList:
                entry = line.strip().split(",")
                # Make sure the line has enough columns (Name, Time, Date)
                if len(entry) >= 3:
                    recorded_name = entry[0]
                    recorded_date = entry[2]

                    # If the name AND today's date match, they are already logged!
                    if recorded_name == name and recorded_date == today_date:
                        already_marked_today = True
                        break

            # If they haven't been marked today, write the new entry
            if not already_marked_today:
                f.writelines(f"\n{name},{time_string},{today_date}")
                print(f"✅ Logged: {name} for {today_date}")

                # --- MULTITHREADING WITH QUEUE ---
                # 1. Put the name in the audio queue (No overlapping voices)
                audio_queue.put(name)
                # 2. Text the parent globally
                threading.Thread(target=send_whatsapp, args=(name, time_string)).start()

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.video_label.configure(
                    text="ERROR: Camera is blocked by another app!", text_color="red"
                )
                self.cap = None
                return

            self.start_button.configure(text="Camera Running...", state="disabled")
            self.video_label.configure(text="")
            self.update_frame()

    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            success, img = self.cap.read()
            if success:
                img = cv2.flip(img, 1)

                imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                facesCurFrame = face_recognition.face_locations(imgS)
                encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

                for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                    matches = face_recognition.compare_faces(
                        self.encodeListKnown, encodeFace
                    )
                    faceDis = face_recognition.face_distance(
                        self.encodeListKnown, encodeFace
                    )
                    matchIndex = np.argmin(faceDis)

                    if matches[matchIndex]:
                        name = self.classNames[matchIndex].upper()

                        y1, x2, y2, x1 = faceLoc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.rectangle(
                            img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED
                        )
                        cv2.putText(
                            img,
                            name,
                            (x1 + 6, y2 - 6),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1,
                            (255, 255, 255),
                            2,
                        )

                        self.markAttendance(name)

                cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(cv2image)
                ctk_image = ctk.CTkImage(
                    light_image=pil_image, dark_image=pil_image, size=(640, 480)
                )
                self.video_label.configure(image=ctk_image)

            self.after(15, self.update_frame)


if __name__ == "__main__":
    app = FaceLogApp()
    app.mainloop()
