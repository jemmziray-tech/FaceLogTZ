import customtkinter as ctk
import cv2
from PIL import Image
import face_recognition
import numpy as np
import os
import csv
from datetime import datetime
import pyttsx3
import threading
import queue
import math

# --- CLOUD COMMUNICATION SETUP ---
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SENDER = os.getenv("TWILIO_WHATSAPP_NUMBER")
TARGET_PHONE = os.getenv("TARGET_PHONE_NUMBER")

if TWILIO_SID and TWILIO_TOKEN:
    twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
else:
    twilio_client = None
    print("⚠️ Warning: Twilio credentials not found in .env file.")

# --- LIVENESS DETECTION MATH ---
def calculate_ear(eye_points):
    """Calculates the Eye Aspect Ratio (EAR) to detect blinks."""
    A = math.dist(eye_points[1], eye_points[5])
    B = math.dist(eye_points[2], eye_points[4])
    C = math.dist(eye_points[0], eye_points[3])
    if C == 0:
        return 0.0
    return (A + B) / (2.0 * C)

# --- SMART PHONEBOOK LOGIC ---
def get_parent_number(student_name):
    try:
        with open("parents.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2 and row[0].strip().upper() == student_name.upper():
                    return row[1].strip()  
    except FileNotFoundError:
        print("⚠️ parents.csv not found!")
    return TARGET_PHONE

def send_whatsapp(name, time_str):
    if twilio_client:
        recipient_number = get_parent_number(name)
        sender_number = TWILIO_SENDER
        if not recipient_number.startswith("whatsapp:"):
            recipient_number = f"whatsapp:{recipient_number}"
        if not sender_number.startswith("whatsapp:"):
            sender_number = f"whatsapp:{sender_number}"
        try:
            message = twilio_client.messages.create(
                from_=sender_number,
                body=f"✅ FaceLogTZ Alert: {name.title()} has safely arrived at class at {time_str}.",
                to=recipient_number,
            )
            print(f"📱 WhatsApp sent! ID: {message.sid}")
        except Exception as e:
            print(f"⚠️ WhatsApp failed to send for {name}: {e}")

# --- AUDIO QUEUE SYSTEM ---
audio_queue = queue.Queue()

def audio_worker():
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)  
    while True:
        message = audio_queue.get()
        engine.say(message)
        engine.runAndWait()
        audio_queue.task_done()

threading.Thread(target=audio_worker, daemon=True).start()

# --- UI & LOGIC ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FaceLogApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FaceLogTZ - Enterprise Dashboard")
        self.geometry("1150x750")

        self.header_label = ctk.CTkLabel(self, text="FaceLogTZ Attendance System", font=ctk.CTkFont(size=28, weight="bold"))
        self.header_label.pack(pady=15)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=10)

        self.left_frame = ctk.CTkFrame(self.container, corner_radius=15)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.video_label = ctk.CTkLabel(self.left_frame, text="Loading Database...", font=ctk.CTkFont(size=20))
        self.video_label.pack(pady=20)

        self.start_button = ctk.CTkButton(self.left_frame, text="Start Camera Stream", font=ctk.CTkFont(size=16, weight="bold"), height=50, command=self.start_camera)
        self.start_button.pack(pady=10)

        self.right_frame = ctk.CTkFrame(self.container, corner_radius=15, width=350)
        self.right_frame.pack(side="right", fill="y")
        self.right_frame.pack_propagate(False)

        self.sidebar_title = ctk.CTkLabel(self.right_frame, text="Live Activity Log", font=ctk.CTkFont(size=18, weight="bold"))
        self.sidebar_title.pack(pady=(20, 10))

        self.activity_log = ctk.CTkTextbox(self.right_frame, font=ctk.CTkFont(size=14), state="disabled", wrap="word")
        self.activity_log.pack(fill="both", expand=True, padx=15, pady=(0, 20))

        self.cap = None

        # Anti-Spoofing & Performance Tuning
        self.frame_counter = 0
        self.frame_skip_rate = 3 
        self.last_face_locations = []
        self.last_face_names = []
        self.last_face_verified = [] 
        
        # Memory Dictionaries
        self.verified_faces_memory = {} 
        self.asked_to_blink = {} 
        self.marked_today = {} # Saves CPU by not reading the CSV endlessly

        self.path = "known_faces"
        self.classNames = []
        self.encodeListKnown = []
        self.load_database()

    def log_activity(self, message):
        now = datetime.now().strftime("%I:%M:%S %p")
        formatted_message = f"[{now}]\n{message}\n\n"
        self.activity_log.configure(state="normal")
        self.activity_log.insert("end", formatted_message)
        self.activity_log.see("end")
        self.activity_log.configure(state="disabled")

    def load_database(self):
        print("Loading Database...")
        self.classNames = []
        self.encodeListKnown = []
        if not os.path.exists(self.path):
            os.makedirs(self.path)

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

            elif os.path.isfile(item_path) and item_path.lower().endswith((".png", ".jpg", ".jpeg")):
                curImg = cv2.imread(item_path)
                if curImg is not None:
                    img_rgb = cv2.cvtColor(curImg, cv2.COLOR_BGR2RGB)
                    encodes = face_recognition.face_encodings(img_rgb)
                    if len(encodes) > 0:
                        self.encodeListKnown.append(encodes[0])
                        self.classNames.append(os.path.splitext(item_name)[0].upper())

        unique_names = set(self.classNames)
        print("Database Loaded! Found:", unique_names)
        self.video_label.configure(text=f"System Ready. {len(unique_names)} students loaded.\nClick Start.")
        self.log_activity(f"⚙️ System Booted.\nLoaded {len(unique_names)} profiles.")

    def markAttendance(self, name):
        if not os.path.isfile("Attendance.csv"):
            with open("Attendance.csv", "w") as f:
                f.writelines("Name,Time,Date")

        with open("Attendance.csv", "r+") as f:
            myDataList = f.readlines()
            now = datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            time_string = now.strftime("%H:%M:%S")

            already_marked_today = False
            for line in myDataList:
                entry = line.strip().split(",")
                if len(entry) >= 3:
                    if entry[0] == name and entry[2] == today_date:
                        already_marked_today = True
                        break

            if not already_marked_today:
                f.writelines(f"\n{name},{time_string},{today_date}")
                print(f"✅ Logged: {name} for {today_date}")
                self.log_activity(f"✅ {name.title()} Arrived.\n📱 WhatsApp Alert Sent.")
                
                audio_queue.put(f"Welcome {name.lower()}.")
                threading.Thread(target=send_whatsapp, args=(name, time_string)).start()

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.video_label.configure(text="ERROR: Camera blocked!", text_color="red")
                self.log_activity("❌ ERROR: Camera blocked by another app.")
                self.cap = None
                return

            self.start_button.configure(text="Camera Running...", state="disabled")
            self.video_label.configure(text="")
            self.log_activity("📹 Live Camera Feed Started.")
            self.update_frame()

    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            success, img = self.cap.read()
            if success:
                img = cv2.flip(img, 1)
                self.frame_counter += 1

                if self.frame_counter % self.frame_skip_rate == 0:
                    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                    imgRGB = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

                    facesCurFrame = face_recognition.face_locations(imgRGB)
                    encodesCurFrame = face_recognition.face_encodings(imgRGB, facesCurFrame)
                    
                    landmarksCurFrame = face_recognition.face_landmarks(imgRGB, facesCurFrame)

                    self.last_face_locations = facesCurFrame
                    self.last_face_names = []
                    self.last_face_verified = []

                    for encodeFace, faceLoc, landmarks in zip(encodesCurFrame, facesCurFrame, landmarksCurFrame):
                        matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                        faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                        
                        name = "UNKNOWN"
                        is_verified = False

                        if len(faceDis) > 0:
                            matchIndex = np.argmin(faceDis)
                            if matches[matchIndex]:
                                name = self.classNames[matchIndex].upper()

                                # 1. Check Memory FIRST
                                is_verified = self.verified_faces_memory.get(name, False)
                                
                                # 2. Only run Blink Math if not verified yet
                                if not is_verified:
                                    left_eye = landmarks.get("left_eye")
                                    right_eye = landmarks.get("right_eye")
                                    
                                    if left_eye and right_eye:
                                        left_ear = calculate_ear(left_eye)
                                        right_ear = calculate_ear(right_eye)
                                        avg_ear = (left_ear + right_ear) / 2.0
                                        
                                        # If EAR < 0.22, Blink Detected!
                                        if avg_ear < 0.22:
                                            self.verified_faces_memory[name] = True
                                            is_verified = True # Update instantly
                                            self.log_activity(f"👁️ Liveness Confirmed: {name.title()}")

                                # 3. Audio Instruction Logic
                                if not is_verified:
                                    if not self.asked_to_blink.get(name, False):
                                        audio_queue.put("Face detected. Please look at the camera and blink.")
                                        self.asked_to_blink[name] = True
                                
                                # 4. Mark Attendance
                                if is_verified:
                                    if not self.marked_today.get(name, False):
                                        self.markAttendance(name)
                                        self.marked_today[name] = True # Locks it out for the rest of the session
                        
                        self.last_face_names.append(name)
                        self.last_face_verified.append(is_verified)

                for (y1, x2, y2, x1), name, verified in zip(self.last_face_locations, self.last_face_names, self.last_face_verified):
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    
                    if name == "UNKNOWN":
                        color = (0, 0, 255) 
                        display_text = "UNKNOWN"
                    elif not verified:
                        color = (0, 255, 255) 
                        display_text = "BLINK TO VERIFY"
                    else:
                        color = (0, 255, 0) 
                        display_text = name

                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
                    cv2.putText(img, display_text, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 2)

                cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(cv2image)
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(750, 560)) 
                self.video_label.configure(image=ctk_image)

            self.after(15, self.update_frame)

if __name__ == "__main__":
    app = FaceLogApp()
    app.mainloop()