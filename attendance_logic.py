import cv2
import face_recognition
import os
import pyttsx3
import numpy as np
from datetime import datetime

# --- SETTINGS ---
path = 'known_faces'
# Initialize Voice Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150) # Speed of speech (150 is natural)
images = []
classNames = []

# --- STEP 1: LOAD DATABASE (ORGANIZED BY FOLDERS) ---
if not os.path.exists(path):
    os.makedirs(path)
    print(f"Created '{path}' folder. Please add subfolders with photos!")

myList = os.listdir(path)
print("Loading Database and Encoding Faces...")

for person_name in myList:
    person_path = os.path.join(path, person_name)
    
    if os.path.isdir(person_path):
        for img_name in os.listdir(person_path):
            curImg = cv2.imread(os.path.join(person_path, img_name))
            if curImg is not None:
                images.append(curImg)
                classNames.append(person_name.upper())

# --- STEP 2: FACE ENCODING FUNCTION (FIXED & SYNCED) ---
def findEncodings(images, names):
    encodeList = []
    syncedNames = [] 
    
    for img, name in zip(images, names):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        try:
            encodings = face_recognition.face_encodings(img)
            if len(encodings) > 0: 
                encodeList.append(encodings[0])
                syncedNames.append(name) 
            else:
                print(f"Warning: A photo for {name} was skipped (no clear face).")
        except Exception as e:
            print(f"Error processing a photo for {name}: {e}")
            
    return encodeList, syncedNames

# Generate encodings and perfectly sync the names!
encodeListKnown, classNames = findEncodings(images, classNames)
print(f'Encoding Complete! Found {len(set(classNames))} unique people: {set(classNames)}')

# --- STEP 3: THE ATTENDANCE LOGGER ---
def markAttendance(name):
    if not os.path.exists('Attendance.csv'):
        with open('Attendance.csv', 'w') as f:
            f.writelines('Name,Time,Date')

    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        now = datetime.now()
        dateString = now.strftime('%Y-%m-%d')
        
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        
        if name not in nameList:
            timeString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{timeString},{dateString}')
            print(f"✅ Attendance logged for: {name}")
            
            # THE VOICE ASSISTANT PART:
            engine.say(f"Welcome {name.lower()}. Your attendance has been recorded.")
            engine.runAndWait()

# --- STEP 4: WEBCAM LOOP ---
# Using CAP_DSHOW to prevent Windows from locking the camera!
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame from camera. Is it being used by another app?")
        break

    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        
        if len(faceDis) > 0:
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex]
                markAttendance(name)

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Smart Attendance System', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()