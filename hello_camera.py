import cv2

# 1. Connect to the webcam.
# The number 0 tells the computer to use your default, built-in camera.
cap = cv2.VideoCapture(0)

print("Camera is turning on... Press 'q' to quit!")

# 2. Start a continuous loop to keep grabbing new pictures (frames) from the camera
while True:

    # Read the current frame from the camera
    success, frame = cap.read()

    # If the camera successfully grabbed a frame, let's show it!
    if success:
        # Open a window and display the video feed
        cv2.imshow("My Smart Attendance System", frame)

    # 3. The "Quit" button
    # This checks every 1 millisecond to see if you pressed the 'q' key on your keyboard
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("Turning off camera...")
        break  # This breaks us out of the continuous loop

# 4. Clean up!
# Always be polite and release the camera so other apps (like Zoom) can use it later
cap.release()
cv2.destroyAllWindows()
