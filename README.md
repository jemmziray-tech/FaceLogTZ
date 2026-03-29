# 📸 FaceLogTZ: Enterprise Smart Attendance System

[![Made in Tanzania](https://img.shields.io/badge/made%20in-tanzania-008751.svg?style=for-the-badge)](https://github.com/Tanzania-Developers-Community/made-in-tanzania)
![Python Version](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv&logoColor=white)
![Twilio](https://img.shields.io/badge/Twilio-Cloud%20Messaging-F22F46?style=for-the-badge&logo=twilio&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)

A modern, multithreaded Computer Vision system that automates classroom attendance using advanced facial recognition, real-time audio queues, and instant WhatsApp cloud notifications.

## 📱 The Vision
Traditional attendance tracking in schools is manual, slow, and prone to errors. FaceLogTZ modernizes classroom management by using AI to identify students in real-time and automatically log their presence. 

Designed specifically with local African environments in mind, this system operates on a **Hybrid Edge-to-Cloud architecture**. Heavy video processing and facial recognition happen entirely locally on the host machine to save bandwidth, while lightweight data is pushed securely to the cloud (Twilio) to instantly notify parents and stakeholders via WhatsApp.

## 🚀 Key Features
- **Modern Enterprise Dashboard:** Built with `customtkinter` for a sleek, responsive, dark-mode user interface.
- **Real-Time Cloud Notifications:** Integrates with the Twilio API to automatically send WhatsApp delivery receipts to parents or managers the second a face is recognized.
- **Smart Daily Validation:** Date-aware logic ensures students are only logged once per day, preventing duplicate entries in the database.
- **Asynchronous Audio Engine:** A custom threading queue (`pyttsx3`) greets users by name one-by-one, preventing overlapping robotic voices or UI crashes during high-traffic moments.
- **Robust Recognition Engine:** Utilizes dynamic folder-scanning to learn multiple angles and lighting conditions for a single identity, increasing match accuracy across different skin tones.
- **Hardware Optimized:** Incorporates dynamic frame resizing (processing frames at 25% scale) to run smoothly even on older, low-resource school computers.

## 🛠️ Technology Stack
- **Core:** Python 3.9+
- **Computer Vision:** OpenCV (`cv2`), `face_recognition` (128-dimension facial encodings)
- **GUI:** `customtkinter`, `Pillow`
- **Cloud API:** `twilio` (WhatsApp integration)
- **Utilities:** `pyttsx3` (Text-to-Speech), `python-dotenv` (Security), `threading`, `queue`, `NumPy`

## 📁 Project Structure
```text
Smart_Attendance_Project/
│
├── known_faces/          
├── .env                 
├── app_ui.py             
├── Attendance.csv        
└── README.md
           
## ⚙️ Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/jemmziray-tech/FaceLogTZ.git](https://github.com/jemmziray-tech/FaceLogTZ.git)
cd FaceLogTZ
**2. Install Dependencies**
pip install opencv-python face_recognition customtkinter twilio python-dotenv pyttsx3 Pillow numpy

