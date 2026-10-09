#!/usr/bin/env python3
"""
Mini PC Face Recognition Monitor
Continuously monitors webcam for faces and recognizes students
"""

import cv2
import requests
import time
import sys
import os
from datetime import datetime

# Configuration
API_BASE = "http://127.0.0.1:8000/api/face"
LOCATION = "Main Gate"
CASCADE_PATH = "haarcascade_frontalface_default.xml"

# Recognition settings
RECOGNITION_INTERVAL = 5  # seconds between recognition attempts
FACE_SIZE_MIN = 100  # minimum face size to consider

def load_cascade():
    """Load Haar cascade for face detection"""
    if not os.path.exists(CASCADE_PATH):
        print(f"Error: Haar cascade file not found: {CASCADE_PATH}")
        print("Please download haarcascade_frontalface_default.xml from OpenCV GitHub")
        sys.exit(1)

    cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if cascade.empty():
        print("Error: Failed to load Haar cascade")
        sys.exit(1)
    return cascade

def detect_faces(frame, cascade):
    """Detect faces in frame"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(FACE_SIZE_MIN, FACE_SIZE_MIN)
    )
    return faces

def recognize_face(frame, event_type="ENTRY"):
    """Send frame to API for recognition"""
    try:
        ret, buf = cv2.imencode('.jpg', frame)
        if not ret:
            return None

        url = f"{API_BASE}/recognize_local/{event_type}"
        files = {"file": ("capture.jpg", buf.tobytes(), "image/jpeg")}
        params = {"location": LOCATION}

        resp = requests.post(url, files=files, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    except Exception as e:
        print(f"Recognition error: {e}")
        return None

def main():
    print("Starting Mini PC Face Recognition Monitor...")
    print(f"Location: {LOCATION}")
    print(f"Recognition interval: {RECOGNITION_INTERVAL} seconds")
    print("="*50)

    # Load face cascade
    cascade = load_cascade()

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        sys.exit(1)

    print("Webcam opened successfully")
    print("Monitoring for faces... (Press Ctrl+C to stop)")

    last_recognition = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame")
                time.sleep(1)
                continue

            current_time = time.time()

            # Detect faces
            faces = detect_faces(frame, cascade)

            if len(faces) > 0:
                # Draw rectangles around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # Attempt recognition if enough time has passed
                if current_time - last_recognition >= RECOGNITION_INTERVAL:
                    print(f"\nDetected {len(faces)} face(s) - attempting recognition...")

                    # Use the largest face for recognition
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    x, y, w, h = largest_face
                    face_roi = frame[y:y+h, x:x+w]

                    result = recognize_face(face_roi)

                    if result:
                        if result.get("status") == "Recognized":
                            print("RECOGNIZED!")
                            print(f"   Student: {result.get('student')}")
                            print(f"   ID: {result.get('student_id')}")
                            print(f"   Event: {result.get('event')}")
                            print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                        else:
                            print("Not recognized")
                    else:
                        print("Recognition failed")

                    last_recognition = current_time

            # Show frame
            cv2.imshow('Mini PC Monitor', frame)

            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping monitor...")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Monitor stopped")

if __name__ == "__main__":
    main()