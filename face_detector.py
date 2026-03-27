import cv2
import face_recognition

# Connect to the webcam
cap = cv2.VideoCapture(0)

print("Looking for faces... Press 'q' to quit!")

while True:
    # Grab the frame from the camera
    success, frame = cap.read()

    if success:
        # --- THE MAGIC HAPPENS HERE ---

        # 1. OpenCV reads colors in BGR (Blue, Green, Red) format.
        # But our face_recognition brain works in RGB (Red, Green, Blue) format!
        # So, we must convert the image color first before handing it to the brain.
        small_frame = cv2.resize(
            frame, (0, 0), fx=0.25, fy=0.25
        )  # Make it smaller to process faster
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 2. Ask the brain to find all faces in the image.
        # It returns coordinates: (top, right, bottom, left) for every face it sees.
        face_locations = face_recognition.face_locations(rgb_frame)

        # 3. Loop through every face found and draw a box!
        for top, right, bottom, left in face_locations:

            # Since we shrank the image to 1/4 size to make it fast,
            # we have to multiply the coordinates by 4 to draw the box on the original big frame!
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a green rectangle.
            # (0, 255, 0) is the color Green. '2' is the thickness of the line.
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Show the video feed with the boxes drawn on it
        cv2.imshow("My Smart Attendance System", frame)

    # The "Quit" button
    if cv2.waitKey(1) & 0xFF == ord("q"):
        print("Turning off camera...")
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
