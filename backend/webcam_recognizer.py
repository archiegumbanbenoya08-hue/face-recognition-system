#!/usr/bin/env python3
"""
Webcam Face Recognition - No Database Required
Simple and straightforward recognition from stored face images
"""

import cv2
import numpy as np
import os
from face_engine import get_embedding, compare_faces

def load_known_faces():
    """Load known faces from student_images directory"""
    known_faces = {}
    image_dir = "student_images"

    if not os.path.exists(image_dir):
        print(f"Error: {image_dir} directory not found")
        return None

    print(f"Loading faces from {image_dir}...")
    for filename in sorted(os.listdir(image_dir)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            student_id = os.path.splitext(filename)[0]
            image_path = os.path.join(image_dir, filename)

            try:
                embedding = get_embedding(image_path)
                known_faces[student_id] = embedding
                print(f"  OK: {student_id}")
            except Exception as e:
                print(f"  SKIP: {student_id} - {e}")

    return known_faces if known_faces else None

def recognize_from_embedding(embedding, known_faces, threshold=0.3):
    """Find best match for an embedding"""
    best_id = None
    best_distance = float('inf')

    for student_id, known_emb in known_faces.items():
        distance = np.linalg.norm(embedding - known_emb)
        if distance < best_distance:
            best_distance = distance
            best_id = student_id

    # Return match only if below threshold
    if best_distance < threshold:
        return best_id, best_distance
    else:
        return None, best_distance

def get_embedding_from_frame(frame):
    """Generate embedding from a video frame"""
    temp_path = "_temp_frame.jpg"
    cv2.imwrite(temp_path, frame)
    try:
        return get_embedding(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    print("\n" + "="*50)
    print("WEBCAM FACE RECOGNITION")
    print("="*50 + "\n")

    # Load faces
    known_faces = load_known_faces()
    if not known_faces:
        print("No valid face images found!")
        return

    print(f"\nLoaded {len(known_faces)} faces")
    print("Starting webcam...")
    print("Press 'q' to quit, space to capture")

    # Try different camera backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Any")
    ]

    cap = None
    for backend, name in backends:
        print(f"Trying {name} backend...")
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ SUCCESS: Using {name} backend")
                break
            else:
                cap.release()
                cap = None
        else:
            print(f"❌ {name} backend failed")

    if cap is None or not cap.isOpened():
        print("\n❌ ERROR: Cannot access camera!")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Close all camera apps (Zoom, Teams, etc.)")
        print("2. Check Windows Camera settings (just opened)")
        print("3. Restart computer")
        print("4. Try different USB port")
        print("5. Update camera drivers")
        return

    frame_count = 0
    recognition_interval = 10  # Recognize every 10 frames

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            h, w = frame.shape[:2]

            # Recognize faces periodically to avoid slowdown
            result_text = "Calculating..."
            result_color = (255, 255, 0)  # Yellow

            if frame_count % recognition_interval == 0:
                try:
                    embedding = get_embedding_from_frame(frame)
                    student_id, distance = recognize_from_embedding(embedding, known_faces)

                    if student_id:
                        result_text = f"FOUND: {student_id} ({distance:.2f})"
                        result_color = (0, 255, 0)  # Green
                    else:
                        result_text = f"Not recognized ({distance:.2f})"
                        result_color = (0, 0, 255)  # Red
                except Exception as e:
                    result_text = f"Error: {str(e)[:30]}"
                    result_color = (0, 0, 255)

            # Display result
            cv2.putText(frame, result_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, result_color, 2)
            cv2.putText(frame, "Press Q to quit", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            cv2.imshow("Face Recognition", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Done!")

if __name__ == "__main__":
    main()