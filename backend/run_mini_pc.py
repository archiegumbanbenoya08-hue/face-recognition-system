#!/usr/bin/env python3
"""
MINI PC FACE RECOGNITION SYSTEM
Simple, no-database version for continuous monitoring
"""

import cv2
import numpy as np
import os
from datetime import datetime
from face_engine import get_embedding

class FaceRecognizer:
    def __init__(self):
        self.known_faces = {}
        self.logs = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all known faces from student_images/"""
        image_dir = "student_images"
        print("Loading registered students...")
        
        for filename in sorted(os.listdir(image_dir)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                student_id = os.path.splitext(filename)[0]
                image_path = os.path.join(image_dir, filename)
                
                try:
                    embedding = get_embedding(image_path)
                    self.known_faces[student_id] = embedding
                    print(f"  ✓ {student_id}")
                except Exception as e:
                    print(f"  ✗ {student_id}: {e}")
        
        print(f"Ready: {len(self.known_faces)} students registered\n")
    
    def recognize_embedding(self, embedding, threshold=0.6):
        """Find best match for an embedding"""
        if not self.known_faces:
            return None, None
        
        best_id = None
        best_distance = float('inf')
        
        for student_id, known_emb in self.known_faces.items():
            distance = np.linalg.norm(embedding - known_emb)
            if distance < best_distance:
                best_distance = distance
                best_id = student_id
        
        if best_distance < threshold:
            return best_id, best_distance
        else:
            return None, best_distance
    
    def log_event(self, student_id, event_type="ENTRY"):
        """Log recognition event"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {event_type}: {student_id}\n"
        self.logs.append(entry)
        
        # Also save to file
        with open("recognition_log.txt", "a") as f:
            f.write(entry)
        
        return entry
    
    def run_webcam(self):
        """Run continuous recognition on webcam"""
        print("Starting webcam monitor...")
        print("Controls:")
        print("  SPACE = Log event")
        print("  'e' = Log as EXIT")
        print("  'i' = Log as ENTRY")
        print("  'q' = Quit")
        print()
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot open webcam")
            return
        
        frame_count = 0
        last_result = "Initializing..."
        recognition_interval = 15
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                h, w = frame.shape[:2]
                
                # Recognize periodically
                if frame_count % recognition_interval == 0:
                    try:
                        temp_path = "_temp_recognize.jpg"
                        cv2.imwrite(temp_path, frame)
                        embedding = get_embedding(temp_path)
                        student_id, distance = self.recognize_embedding(embedding)
                        
                        if student_id:
                            last_result = f"RECOGNIZED: {student_id}"
                            color = (0, 255, 0)  # Green
                        else:
                            last_result = f"No match found"
                            color = (0, 0, 255)  # Red
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except:
                        last_result = "Error detecting face"
                        color = (0, 0, 255)
                
                # Display
                cv2.putText(frame, last_result, (10, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "SPACE=Log | e=EXIT | i=ENTRY | q=Quit", 
                           (10, h-15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                           (255, 255, 255), 1)
                
                cv2.imshow("Face Recognition Monitor", frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord(' ') or key == ord('i'):
                    if "RECOGNIZED" in last_result:
                        student_id = last_result.split(": ")[1]
                        log_entry = self.log_event(student_id, "ENTRY")
                        print(f"✓ ENTRY logged: {log_entry.strip()}")
                    else:
                        print("⚠ No student recognized - cannot log")
                elif key == ord('e'):
                    if "RECOGNIZED" in last_result:
                        student_id = last_result.split(": ")[1]
                        log_entry = self.log_event(student_id, "EXIT")
                        print(f"✓ EXIT logged: {log_entry.strip()}")
                    else:
                        print("⚠ No student recognized - cannot log")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Monitor stopped")
            print(f"Total events logged: {len(self.logs)}")

def main():
    print("\n" + "="*60)
    print("MINI PC FACE RECOGNITION SYSTEM")
    print("="*60 + "\n")
    
    recognizer = FaceRecognizer()
    recognizer.run_webcam()

if __name__ == "__main__":
    main()