#!/usr/bin/env python3
import argparse
import importlib
import os
import subprocess
import sys
import time


def ensure_insightface_environment():
    try:
        importlib.import_module("insightface.app")
        return
    except ModuleNotFoundError as error:
        venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv_310")
        scripts_dir = "Scripts" if sys.platform.startswith("win") else "bin"
        python_executable = "python.exe" if sys.platform.startswith("win") else "python"
        venv_python = os.path.join(venv_dir, scripts_dir, python_executable)

        current_python = os.path.normcase(os.path.realpath(sys.executable))
        target_python = os.path.normcase(os.path.realpath(venv_python))
        if os.path.isfile(venv_python) and current_python != target_python:
            print(
                f"InsightFace is unavailable in this Python. Restarting with {venv_python}",
                flush=True,
            )
            result = subprocess.run(
                [venv_python, os.path.abspath(__file__), *sys.argv[1:]],
                check=False,
            )
            raise SystemExit(result.returncode)

        raise RuntimeError(
            "Could not import InsightFace. Install backend/requirements.txt in this environment "
            "or use backend/venv_310."
        ) from error

import cv2
import numpy as np

from database import create_parent, get_parent, get_student_by_id, save_student
from camera import configure_camera_window
from face_engine import get_embedding

UPLOAD_FOLDER = "student_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
HAAR_CASCADE_PATH = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
POSES = [
    ("front", "Look straight at the camera."),
    ("left", "Turn your face to the left."),
    ("right", "Turn your face to the right."),
    ("up", "Tilt your head upward."),
    ("down", "Tilt your head downward."),
    ("blink", "Blink your eyes now."),
]
STABLE_FRAMES = 8


def open_camera(camera_index=0):
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera. Check camera connection and try again.")
    return cap


def load_cascades():
    if not os.path.exists(HAAR_CASCADE_PATH):
        raise FileNotFoundError(
            f"Cascade file not found: {HAAR_CASCADE_PATH}. `haarcascade_frontalface_default.xml` is required."
        )
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    return face_cascade, profile_cascade, eye_cascade


def detect_profile_face(gray, frame_w, profile_cascade, flip=False):
    if flip:
        gray = cv2.flip(gray, 1)
    profiles = profile_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(100, 100))
    if len(profiles) == 0:
        return None
    x, y, w, h = max(profiles, key=lambda rect: rect[2] * rect[3])
    if flip:
        x = frame_w - (x + w)
    return x, y, w, h


def pose_is_matched(pose_name, face_center, frame_center, eye_count):
    dx = (face_center[0] - frame_center[0]) / frame_center[0]
    dy = (face_center[1] - frame_center[1]) / frame_center[1]
    if pose_name == "front":
        return abs(dx) < 0.18 and abs(dy) < 0.18
    if pose_name == "left":
        return dx < -0.12
    if pose_name == "right":
        return dx > 0.12
    if pose_name == "up":
        return dy < -0.12
    if pose_name == "down":
        return dy > 0.12
    if pose_name == "blink":
        return eye_count == 0
    return False


def compute_average_embedding(image_paths):
    embeddings = []
    for path in image_paths:
        try:
            embedding = get_embedding(path)
        except Exception as e:
            print(f"Warning: could not embed {path}: {e}")
            continue
        if embedding is not None:
            embeddings.append(np.array(embedding))
    if not embeddings:
        raise RuntimeError("No embeddings were generated from the captured images.")
    return np.mean(np.stack(embeddings), axis=0)


def capture_pose_images(student_id, camera_index=0):
    face_cascade, profile_cascade, eye_cascade = load_cascades()
    cap = open_camera(camera_index)
    captured_paths = []
    window_name = "Register Student - Pose Capture"
    configure_camera_window(window_name)
    try:
        for pose_name, pose_label in POSES:
            stable_count = 0
            pose_captured = False
            print(f"Prepare for pose: {pose_name.upper()} - {pose_label}")
            while not pose_captured:
                ret, frame = cap.read()
                if not ret:
                    raise RuntimeError("Failed to read from camera.")
                frame_h, frame_w = frame.shape[:2]
                frame_center = (frame_w / 2.0, frame_h / 2.0)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_box = None
                eye_count = 0
                if pose_name in ("left", "right"):
                    flip = pose_name == "left"
                    profile = detect_profile_face(gray, frame_w, profile_cascade, flip=flip)
                    if profile is not None:
                        face_box = profile
                if face_box is None:
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(120, 120))
                    if len(faces) > 0:
                        face_box = max(faces, key=lambda rect: rect[2] * rect[3])
                label = "No face detected"
                color = (0, 0, 255)
                if face_box is not None:
                    x, y, w, h = face_box
                    face_center = (x + w / 2.0, y + h / 2.0)
                    face_gray = gray[y : y + h, x : x + w]
                    eyes = eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
                    eye_count = len(eyes)
                    pose_match = pose_is_matched(pose_name, face_center, frame_center, eye_count)
                    label = f"Pose: {pose_name.upper()} ({stable_count}/{STABLE_FRAMES})"
                    if pose_match:
                        stable_count += 1
                        color = (0, 255, 0)
                    else:
                        stable_count = 0
                        color = (0, 0, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    if pose_name == "blink":
                        cv2.putText(frame, f"Eyes detected: {eye_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                else:
                    stable_count = 0
                    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                cv2.putText(frame, pose_label, (10, frame_h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, "Press C to capture manually when pose is correct.", (10, frame_h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.imshow(window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    raise SystemExit("Capture cancelled by user.")
                if key == ord("c") and face_box is not None:
                    stable_count = STABLE_FRAMES
                if stable_count >= STABLE_FRAMES:
                    file_name = f"{student_id}.jpg" if pose_name == "front" else f"{student_id}_{pose_name}.jpg"
                    file_path = os.path.join(UPLOAD_FOLDER, file_name)
                    cv2.imwrite(file_path, frame)
                    captured_paths.append(file_path)
                    print(f"Captured {pose_name} pose: {file_path}")
                    pose_captured = True
                    time.sleep(0.4)
                cv2.putText(frame, "Press q to cancel.", (10, frame_h - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            time.sleep(0.4)
        return captured_paths
    finally:
        cap.release()
        cv2.destroyAllWindows()


def prompt_or_value(prompt_text, value=None, validator=None, empty_message=None):
    if value is not None:
        value = value.strip()
        if validator is not None and not validator(value):
            raise ValueError(f"Invalid value for {prompt_text.lower()}.")
        return value
    while True:
        user_value = input(prompt_text).strip()
        if not user_value:
            if empty_message:
                print(empty_message)
            continue
        if validator is not None and not validator(user_value):
            print(f"Invalid value. Please try again.")
            continue
        return user_value


def collect_registration_data(args):
    student_id = args.student_id.strip() if args.student_id else None
    first_name = args.first_name.strip() if args.first_name else None
    last_name = args.last_name.strip() if args.last_name else None
    grade_level = args.grade_level.strip() if args.grade_level else None
    section = args.section.strip() if args.section else None
    parent_email = args.parent_email.strip() if args.parent_email else None

    if not student_id:
        student_id = prompt_or_value("Enter student ID: ", empty_message="Student ID cannot be empty.")
    if get_student_by_id(student_id):
        raise ValueError(
            f"Student ID '{student_id}' already exists. "
            "Use a different ID or remove the existing student record before registering again."
        )

    if not first_name:
        first_name = prompt_or_value("Enter FIRST NAME: ", empty_message="First name cannot be empty.")
    if not last_name:
        last_name = prompt_or_value("Enter LAST NAME: ", empty_message="Last name cannot be empty.")
    if not grade_level:
        grade_level = prompt_or_value("Enter GRADE LEVEL: ", empty_message="Grade level cannot be empty.")
    if not section:
        section = prompt_or_value("Enter SECTION: ", empty_message="Section cannot be empty.")
    if not parent_email:
        parent_email = prompt_or_value(
            "Enter PARENT EMAIL: ",
            validator=lambda value: "@" in value and "." in value,
            empty_message="Parent email cannot be empty.",
        )

    return {
        "student_id": student_id,
        "first_name": first_name,
        "last_name": last_name,
        "grade_level": grade_level,
        "section": section,
        "parent_email": parent_email,
    }


def register_student(args):
    registration = collect_registration_data(args)
    student_id = registration["student_id"]
    first_name = registration["first_name"]
    last_name = registration["last_name"]
    grade_level = registration["grade_level"]
    section = registration["section"]
    parent_email = registration["parent_email"]
    if args.image:
        if not os.path.exists(args.image):
            raise FileNotFoundError(f"Image file not found: {args.image}")
        image_path = os.path.join(UPLOAD_FOLDER, f"{student_id}.jpg")
        if os.path.abspath(args.image) != os.path.abspath(image_path):
            os.replace(args.image, image_path)
        image_paths = [image_path]
        print(f"Copied image to {image_path}")
    else:
        print("\nFollow the on-screen camera instructions to capture the student's face.")
        image_paths = capture_pose_images(student_id, camera_index=args.camera_index)
        if not image_paths:
            raise RuntimeError("No images were captured for the student.")
        image_path = os.path.join(UPLOAD_FOLDER, f"{student_id}.jpg")
    parent = get_parent(parent_email)
    if not parent:
        parent_id = create_parent(parent_email, "default_password")
        print(f"Created new parent record for {parent_email}")
    else:
        parent_id = parent["parent_id"]
        print(f"Using existing parent record for {parent_email}")
    embedding = compute_average_embedding(image_paths)
    save_student(student_id, first_name, last_name, grade_level, section, parent_id, parent_email, image_path, embedding)
    print("\nStudent registered successfully:")
    print(f"  ID: {student_id}")
    print(f"  Name: {first_name} {last_name}")
    print(f"  Grade: {grade_level}")
    print(f"  Section: {section}")
    print(f"  Parent: {parent_email}")
    print(f"  Photo: {image_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Register a student via webcam or image file.")
    parser.add_argument("--student-id", help="Unique student ID")
    parser.add_argument("--first-name", help="Student first name")
    parser.add_argument("--last-name", help="Student last name")
    parser.add_argument("--grade-level", help="Student grade level")
    parser.add_argument("--section", help="Student section")
    parser.add_argument("--parent-email", help="Parent email address")
    parser.add_argument("--image", help="Optional existing image file to use instead of webcam capture")
    parser.add_argument("--camera-index", type=int, default=0, help="Camera index to use for capture")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        ensure_insightface_environment()
        args = parse_args()
        register_student(args)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
