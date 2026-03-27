# FaceLogTZ: Smart Attendance System

![Python Version](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)

An offline-first, locally hosted Computer Vision system that automates classroom attendance using advanced facial recognition.

## The Vision
Traditional attendance tracking in schools is manual, slow, and prone to errors. FaceLogTZ modernizes classroom management by using AI to identify students in real-time and automatically log their presence. 

Designed specifically with local African environments in mind, this system operates entirely **offline** to bypass unreliable internet connectivity. It utilizes a **dynamic folder-based database architecture**, allowing multiple reference photos per student. This ensures the AI remains highly accurate across different skin tones and under drastically changing classroom lighting conditions throughout the school day.

## Key Features
- **100% Offline Capability:** Runs completely locally on the host machine; no external cloud APIs or continuous internet connection required.
- **Robust Recognition Engine:** Utilizes dynamic folder-scanning to learn multiple angles and lighting conditions for a single identity, increasing match accuracy.
- **Interactive Voice Assistant:** Integrated `pyttsx3` offline Text-to-Speech engine to provide real-time audio confirmation and student greetings, enhancing the user experience.
- **Automated Logging:** Automatically generates a time-stamped `.csv` database containing Student Name, Time of Arrival, and Date.
- **Hardware Optimized:** Incorporates dynamic frame resizing (processing frames at 25% scale) to run smoothly even on older, low-resource school computers.

## Technology Stack
- **Python 3.9** - Core runtime environment.
- **OpenCV (`cv2`)** - For video stream handling and GUI rendering.
- **`face_recognition` (dlib)** - Deep learning models for generating 128-dimension facial encodings.
- **`pyttsx3`** - Cross-platform, offline Text-to-Speech engine.
- **NumPy** - For mathematical array comparisons and distance calculations.

## Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/jemmziray-tech/FaceLogTZ.git](https://github.com/jemmziray-tech/FaceLogTZ.git)
cd FaceLogTZ
