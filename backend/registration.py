#!/usr/bin/env python3
"""
Student Face Registration Module
Complete workflow for registering students with face capture and encoding.
"""

import os
import sys
import re
from typing import Optional, List
import shutil
from pathlib import Path

from camera import CameraCapture
from encoding import FaceEncoder, EncodingStorage
from database import (
    create_tables, get_student_by_id, save_student,
    create_parent, get_parent, student_exists
)


class RegistrationForm:
    """Interactive registration form"""
    
    @staticmethod
    def get_user_input() -> dict:
        """Get registration details from user"""
        print("\n" + "="*60)
        print(" " * 15 + "STUDENT FACE REGISTRATION")
        print("="*60 + "\n")
        
        data = {}
        
        # Student ID
        while True:
            student_id = input("Enter Student ID (e.g., 2025-001): ").strip()
            if not student_id:
                print("⚠ Student ID cannot be empty")
                continue
            
            if student_exists(student_id):
                print(f"⚠ Student ID '{student_id}' already registered!")
                retry = input("Continue anyway? (y/n): ").strip().lower()
                if retry != 'y':
                    continue
            
            data['student_id'] = student_id
            break
        
        # First Name
        while True:
            first_name = input("Enter First Name: ").strip()
            if first_name:
                data['first_name'] = first_name
                break
            print("⚠ First name cannot be empty")
        
        # Last Name
        while True:
            last_name = input("Enter Last Name: ").strip()
            if last_name:
                data['last_name'] = last_name
                break
            print("⚠ Last name cannot be empty")
        
        # Grade Level
        while True:
            grade_level = input("Enter Grade Level (e.g., 1-12): ").strip()
            if grade_level:
                data['grade_level'] = grade_level
                break
            print("⚠ Grade level cannot be empty")
        
        # Section
        while True:
            section = input("Enter Section (e.g., A, B, C): ").strip()
            if section:
                data['section'] = section
                break
            print("⚠ Section cannot be empty")
        
        # Parent Email
        while True:
            parent_email = input("Enter Parent Email: ").strip()
            if RegistrationForm.validate_email(parent_email):
                data['parent_email'] = parent_email
                break
            print("⚠ Invalid email format. Please try again.")
        
        return data
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


class DatasetManager:
    """Manage student face dataset storage"""
    
    BASE_DATASET_DIR = "dataset"
    
    @staticmethod
    def setup_dataset_folder(student_id: str) -> str:
        """
        Create dataset folder for student.
        
        Args:
            student_id: Student ID
        
        Returns:
            Path to dataset folder
        """
        student_folder = os.path.join(
            DatasetManager.BASE_DATASET_DIR,
            student_id
        )
        
        os.makedirs(student_folder, exist_ok=True)
        print(f"✓ Dataset folder: {student_folder}")
        
        return student_folder
    
    @staticmethod
    def get_next_image_number(student_folder: str) -> int:
        """Get next sequential image number"""
        if not os.path.exists(student_folder):
            return 1
        
        existing_files = [
            f for f in os.listdir(student_folder)
            if f.endswith(('.jpg', '.png'))
        ]
        
        return len(existing_files) + 1
    
    @staticmethod
    def save_face_image(
        frame,
        student_folder: str,
        image_number: int
    ) -> str:
        """
        Save captured face image.
        
        Args:
            frame: OpenCV frame
            student_folder: Student dataset folder
            image_number: Sequential image number
        
        Returns:
            Path to saved image
        """
        import cv2
        
        image_path = os.path.join(student_folder, f"{image_number}.jpg")
        cv2.imwrite(image_path, frame)
        print(f"  Saved: {image_path}")
        
        return image_path


class StudentRegistration:
    """Main registration workflow"""
    
    # Capture sequence for variety
    CAPTURE_SEQUENCE = [
        ('front', 'Face FRONT - Look directly at camera'),
        ('left', 'Face LEFT - Turn head 30° left'),
        ('right', 'Face RIGHT - Turn head 30° right'),
        ('up', 'Face UP - Tilt head upward'),
        ('down', 'Face DOWN - Tilt head downward'),
        ('front', 'SMILE - Show a friendly smile'),
        ('front', 'NEUTRAL - Return to neutral expression'),
    ]
    
    SAMPLES_PER_POSE = 3  # Capture this many for each pose
    TOTAL_SAMPLES = len(CAPTURE_SEQUENCE) * SAMPLES_PER_POSE
    
    def __init__(self):
        self.registration_data = {}
        self.captured_images = []
        self.face_encodings = {}
    
    def register_student(self, test_mode: bool = False) -> bool:
        """
        Complete registration workflow.
        
        Args:
            test_mode: Skip camera for testing
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Step 1: Get student information
            print("\n" + "="*60)
            print("STEP 1: STUDENT INFORMATION")
            print("="*60)
            self.registration_data = RegistrationForm.get_user_input()
            
            # Step 2: Setup dataset folder
            print("\n" + "="*60)
            print("STEP 2: DATASET SETUP")
            print("="*60)
            student_id = self.registration_data['student_id']
            dataset_folder = DatasetManager.setup_dataset_folder(student_id)
            
            # Step 3: Face capture
            if not test_mode:
                print("\n" + "="*60)
                print("STEP 3: FACE CAPTURE")
                print("="*60)
                print(f"\nCapture {self.TOTAL_SAMPLES} samples for best recognition accuracy.\n")
                
                if not self._capture_faces(dataset_folder):
                    print("\n⚠ Registration cancelled")
                    return False
            
            # Step 4: Generate encodings
            print("\n" + "="*60)
            print("STEP 4: FACE ENCODING")
            print("="*60)
            print("\nGenerating face encodings...")
            
            if not self._generate_encodings(dataset_folder):
                print("\n⚠ Failed to generate encodings")
                return False
            
            # Step 5: Save to database
            print("\n" + "="*60)
            print("STEP 5: DATABASE STORAGE")
            print("="*60)
            print("\nSaving to database...")
            
            if not self._save_to_database(dataset_folder):
                print("\n⚠ Failed to save to database")
                return False
            
            # Success
            print("\n" + "="*60)
            print("✓ REGISTRATION COMPLETE")
            print("="*60)
            print(f"\nStudent: {self.registration_data['first_name']} {self.registration_data['last_name']}")
            print(f"ID: {self.registration_data['student_id']}")
            print(f"Grade: {self.registration_data['grade_level']}")
            print(f"Section: {self.registration_data['section']}")
            print(f"Samples: {len(self.captured_images)}")
            print(f"Dataset: {dataset_folder}")
            print("\nStudent is ready for face recognition!\n")
            
            return True
        
        except KeyboardInterrupt:
            print("\n\n⚠ Registration cancelled by user")
            return False
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _capture_faces(self, dataset_folder: str) -> bool:
        """Capture face samples with guidance"""
        try:
            camera = CameraCapture()
            total_captured = 0
            
            for pose_idx, (pose, instruction) in enumerate(self.CAPTURE_SEQUENCE):
                print(f"\n--- Pose {pose_idx + 1}/{len(self.CAPTURE_SEQUENCE)}: {instruction} ---")
                
                for sample in range(self.SAMPLES_PER_POSE):
                    current_count = total_captured
                    
                    frame = camera.capture_with_guidance(
                        instruction_type=pose,
                        total_captures=self.TOTAL_SAMPLES,
                        current_count=current_count,
                        blur_threshold=100.0,
                        auto_capture=True,
                        auto_capture_delay=0.5
                    )
                    
                    if frame is None:
                        print("\n⚠ Capture cancelled")
                        return False
                    
                    # Crop face and save
                    cropped_face = camera.crop_face(frame, padding=20)
                    if cropped_face is not None:
                        image_number = DatasetManager.get_next_image_number(dataset_folder)
                        image_path = DatasetManager.save_face_image(
                            cropped_face,
                            dataset_folder,
                            image_number
                        )
                        self.captured_images.append(image_path)
                        total_captured += 1
                    else:
                        print("  ⚠ Failed to crop face - skipping")
                        sample -= 1  # Retry this sample
            
            print(f"\n✓ Captured {total_captured} samples")
            return True
        
        except Exception as e:
            print(f"✗ Capture error: {e}")
            return False
    
    def _generate_encodings(self, dataset_folder: str) -> bool:
        """Generate face encodings"""
        try:
            # Get all images
            image_files = [
                os.path.join(dataset_folder, f)
                for f in sorted(os.listdir(dataset_folder))
                if f.endswith(('.jpg', '.png'))
            ]
            
            if not image_files:
                print("✗ No images found")
                return False
            
            print(f"\nProcessing {len(image_files)} images...")
            
            # Generate encodings
            encodings = FaceEncoder.encode_batch(image_files)
            
            if not encodings:
                print("✗ Failed to generate any encodings")
                return False
            
            # Average encodings for final stored encoding
            encoding_arrays = list(encodings.values())
            average_encoding = sum(encoding_arrays) / len(encoding_arrays)
            
            self.face_encodings['average'] = average_encoding
            self.face_encodings['all'] = encoding_arrays
            
            print(f"✓ Generated {len(encodings)} encodings")
            print(f"  Average encoding shape: {average_encoding.shape}")
            
            return True
        
        except Exception as e:
            print(f"✗ Encoding error: {e}")
            return False
    
    def _save_to_database(self, dataset_folder: str) -> bool:
        """Save student and encodings to database"""
        try:
            # Ensure tables exist
            create_tables()
            
            student_id = self.registration_data['student_id']
            first_name = self.registration_data['first_name']
            last_name = self.registration_data['last_name']
            grade_level = self.registration_data['grade_level']
            section = self.registration_data['section']
            parent_email = self.registration_data['parent_email']
            
            # Get or create parent
            parent = get_parent(parent_email)
            if not parent:
                parent_id = create_parent(parent_email, "default_password")
                print(f"✓ Created parent: {parent_email}")
            else:
                parent_id = parent['parent_id']
                print(f"✓ Using existing parent: {parent_email}")
            
            # Save average encoding
            average_encoding = self.face_encodings['average']
            
            # Save student
            save_student(
                student_id,
                first_name,
                last_name,
                grade_level,
                section,
                parent_id,
                parent_email,
                dataset_folder,
                average_encoding
            )
            
            print(f"✓ Saved to database: {student_id}")
            return True
        
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("Student Face Registration System")
    print("="*60)
    
    # Create database if needed
    try:
        create_tables()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)
    
    # Run registration
    registration = StudentRegistration()
    
    if registration.register_student():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
