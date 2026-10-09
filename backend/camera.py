#!/usr/bin/env python3
"""
Camera module for face capture with quality checks and angle guidance.
"""

import cv2
import numpy as np
import os
from typing import Tuple, Optional, List
import time

class FaceDetector:
    """Face detection using Haar Cascade"""
    
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cascade_path = os.path.join(script_dir, "haarcascade_frontalface_default.xml")
        
        if not os.path.exists(cascade_path):
            raise FileNotFoundError(f"Cascade file not found: {cascade_path}")
        
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame.
        Returns list of (x, y, w, h) for each detected face
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )
        return faces
    
    def get_largest_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Get the largest detected face (assumed to be the main subject)"""
        faces = self.detect_faces(frame)
        if len(faces) == 0:
            return None
        return max(faces, key=lambda f: f[2] * f[3])  # Sort by area


class BlurDetector:
    """Detect if image is too blurry using Laplacian variance"""
    
    @staticmethod
    def is_blurry(frame: np.ndarray, threshold: float = 100.0) -> bool:
        """
        Check if frame is too blurry.
        Returns True if blurry, False if clear.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var < threshold
    
    @staticmethod
    def get_blur_score(frame: np.ndarray) -> float:
        """Get blur score (higher = clearer)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()


class CameraCapture:
    """Handle webcam capture with guided face positioning"""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.face_detector = FaceDetector()
        self.blur_detector = BlurDetector()
        self.instructions = {
            'front': 'Look FRONT - Face the camera directly',
            'left': 'Look LEFT - Turn your head left',
            'right': 'Look RIGHT - Turn your head right',
            'up': 'Look UP - Tilt head upward slightly',
            'down': 'Look DOWN - Tilt head downward slightly',
            'smile': 'SMILE - Show a friendly smile',
            'neutral': 'NEUTRAL - Keep a neutral expression'
        }
    
    def open_camera(self) -> cv2.VideoCapture:
        """Try opening camera with multiple backends"""
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        
        for backend in backends:
            cap = cv2.VideoCapture(self.camera_index, backend)
            if cap.isOpened():
                print(f"✓ Camera opened successfully (backend: {backend})")
                return cap
            cap.release()
        
        raise RuntimeError(
            "Cannot open camera. Ensure:\n"
            "  - Camera is connected\n"
            "  - No other app is using it\n"
            "  - Camera permissions are enabled"
        )
    
    def capture_with_guidance(
        self,
        instruction_type: str = 'front',
        total_captures: int = 50,
        current_count: int = 0,
        blur_threshold: float = 100.0,
        auto_capture: bool = True,
        auto_capture_delay: float = 1.0
    ) -> Optional[np.ndarray]:
        """
        Capture face with guidance and quality checks.
        
        Args:
            instruction_type: Type of pose instruction ('front', 'left', 'right', etc.)
            total_captures: Total captures needed
            current_count: Current capture count
            blur_threshold: Blur detection threshold (higher = stricter)
            auto_capture: Auto-capture when face is properly positioned
            auto_capture_delay: Delay before auto-capture (seconds)
        
        Returns:
            Captured frame or None if cancelled
        """
        cap = self.open_camera()
        last_capture_time = 0
        instruction = self.instructions.get(instruction_type, 'Look at the camera')
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise RuntimeError("Failed to read from camera")
                
                # Flip frame for selfie view
                frame = cv2.flip(frame, 1)
                h, w = frame.shape[:2]
                
                # Detect face
                face = self.face_detector.get_largest_face(frame)
                is_face_detected = face is not None
                
                # Check quality
                is_blurry = self.blur_detector.is_blurry(frame, blur_threshold)
                blur_score = self.blur_detector.get_blur_score(frame)
                
                # Draw guide circle in center
                center_x, center_y = w // 2, h // 2
                radius = min(w, h) // 3
                
                # Draw positioning guide
                if is_face_detected:
                    x, y, fw, fh = face
                    face_center = (x + fw // 2, y + fh // 2)
                    distance = np.sqrt((face_center[0] - center_x)**2 + (face_center[1] - center_y)**2)
                    
                    # Determine if well-positioned
                    is_centered = distance < radius * 0.5
                    face_size_ok = (w * 0.2) < fw < (w * 0.6)
                    is_well_positioned = is_centered and face_size_ok and not is_blurry
                    
                    # Draw face rectangle
                    color = (0, 255, 0) if is_well_positioned else (0, 165, 255)
                    thickness = 3 if is_well_positioned else 2
                    cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, thickness)
                    
                    # Draw status
                    status_texts = []
                    if not is_centered:
                        status_texts.append("Move face to center")
                    if not face_size_ok:
                        status_texts.append("Move closer or further")
                    if is_blurry:
                        status_texts.append(f"Hold steady (blur: {blur_score:.0f})")
                    
                    if is_well_positioned:
                        status_texts = ["✓ Position OK - Ready to capture"]
                
                else:
                    is_well_positioned = False
                    status_texts = ["No face detected - Look at camera"]
                
                # Draw guide circle
                guide_color = (0, 255, 0) if is_face_detected else (0, 0, 255)
                cv2.circle(frame, (center_x, center_y), radius, guide_color, 2)
                
                # Draw instruction
                cv2.putText(
                    frame,
                    instruction,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2
                )
                
                # Draw capture counter
                cv2.putText(
                    frame,
                    f"Captured: {current_count}/{total_captures}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2
                )
                
                # Draw status
                for i, status_text in enumerate(status_texts):
                    cv2.putText(
                        frame,
                        status_text,
                        (20, h - 100 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0) if is_well_positioned else (0, 165, 255),
                        2
                    )
                
                # Draw controls
                cv2.putText(
                    frame,
                    "SPACE: Capture | Q: Quit | SKIP: S",
                    (20, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (200, 200, 200),
                    1
                )
                
                cv2.imshow("Face Registration - Capture", frame)
                
                # Auto-capture if conditions met
                if (auto_capture and is_well_positioned and 
                    time.time() - last_capture_time > auto_capture_delay):
                    cap.release()
                    cv2.destroyAllWindows()
                    return frame
                
                # Manual controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):  # Space to capture
                    if is_face_detected:
                        cap.release()
                        cv2.destroyAllWindows()
                        return frame
                    else:
                        print("⚠ No face detected - cannot capture")
                
                elif key == ord('q'):  # Q to quit
                    cap.release()
                    cv2.destroyAllWindows()
                    return None
                
                elif key == ord('s'):  # S to skip
                    cap.release()
                    cv2.destroyAllWindows()
                    return None
        
        except Exception as e:
            cap.release()
            cv2.destroyAllWindows()
            raise
    
    def crop_face(self, frame: np.ndarray, padding: int = 20) -> Optional[np.ndarray]:
        """
        Crop face region from frame.
        
        Args:
            frame: Input frame
            padding: Padding around face (pixels)
        
        Returns:
            Cropped face image or None if no face detected
        """
        face = self.face_detector.get_largest_face(frame)
        if face is None:
            return None
        
        x, y, w, h = face
        y1 = max(0, y - padding)
        y2 = min(frame.shape[0], y + h + padding)
        x1 = max(0, x - padding)
        x2 = min(frame.shape[1], x + w + padding)
        
        return frame[y1:y2, x1:x2]


def test_camera():
    """Test camera setup"""
    print("\n" + "="*50)
    print("CAMERA TEST")
    print("="*50 + "\n")
    
    try:
        cap_module = CameraCapture()
        print("✓ Camera module initialized")
        
        cap = cap_module.open_camera()
        print("✓ Camera opened")
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print("✓ Successfully captured frame")
            print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
            return True
        else:
            print("✗ Failed to capture frame")
            return False
    
    except Exception as e:
        print(f"✗ Camera error: {e}")
        return False


if __name__ == "__main__":
    test_camera()
