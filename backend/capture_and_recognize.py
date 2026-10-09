import argparse
import cv2
import requests
import sys
import time
import os
import pickle
import sqlite3
import datetime
import numpy as np

try:
    import face_recognition
except ImportError:
    face_recognition = None

try:
    import mediapipe as mp
except ImportError:
    mp = None

# Endpoint type: change to "EXIT" when needed
API_URL = "http://127.0.0.1:8000/recognize/ENTRY"
# --- Configuration ---
BASE_API_URL = "http://127.0.0.1:8000"
LOCATION = "Main Gate"
APPLICATION_CALLBACK_URL = os.environ.get("APPLICATION_CALLBACK_URL", "")

# Path to the Haar Cascade file for face detection.
# This uses the script directory so you can run the script from any working directory.
# Please download "haarcascade_frontalface_default.xml" from the OpenCV GitHub repo
# and place it next to this script (backend/haarcascade_frontalface_default.xml).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASCADE_PATH = os.path.join(SCRIPT_DIR, "haarcascade_frontalface_default.xml")
RESULT_DISPLAY_TIME_SEC = 5  # How long to show the result on screen
AUTO_CAPTURE_INTERVAL_SEC = 8  # Minimum seconds between automatic captures
LOCAL_HISTORY_DB = os.path.join(SCRIPT_DIR, "capture_history.db")
LAST_CAPTURE_PICKLE = os.path.join(SCRIPT_DIR, "last_capture.pkl")


def ensure_capture_db():
    conn = sqlite3.connect(LOCAL_HISTORY_DB)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                status TEXT,
                student TEXT,
                grade_level TEXT,
                section TEXT,
                location TEXT,
                timestamp TEXT,
                raw_result BLOB
            )
        ''')
        conn.commit()
    finally:
        conn.close()


def log_capture_result(event_type, result):
    ensure_capture_db()
    raw_data = pickle.dumps(result)
    conn = sqlite3.connect(LOCAL_HISTORY_DB)
    try:
        conn.execute(
            "INSERT INTO captures (event_type, status, student, grade_level, section, location, timestamp, raw_result) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                event_type,
                result.get("status"),
                result.get("student"),
                result.get("grade_level"),
                result.get("section"),
                result.get("location"),
                datetime.datetime.now().isoformat(),
                raw_data,
            )
        )
        conn.commit()
    finally:
        conn.close()
    try:
        with open(LAST_CAPTURE_PICKLE, "wb") as f:
            pickle.dump(result, f)
    except Exception:
        pass


def has_face(frame):
    if face_recognition is None:
        return True
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb, model="hog")
    return len(boxes) > 0


def capture_frame():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError("Failed to capture image")
    return frame


def recognize_from_image(image_path: str, api_url: str):
    """Load an image from disk and send it for recognition."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    frame = cv2.imread(image_path)
    if frame is None:
        raise RuntimeError(f"Failed to load image: {image_path}")
    return recognize(frame, api_url)

def get_api_url(event_type):
    """Constructs the API URL based on the event type."""
    # Based on your main.py, the endpoint is at the root.
    # Based on the main.py, the endpoint is at the root.
    return f"{BASE_API_URL}/recognize/{event_type.upper()}"

def send_result_to_application(result):
    """Send the recognized student data to an external application callback."""
    if not APPLICATION_CALLBACK_URL:
        return
    if result.get("status") != "Recognized":
        return

    payload = {
        "student_id": result.get("student_id"),
        "name": result.get("student"),
        "grade_level": result.get("grade_level"),
        "section": result.get("section"),
        "event": result.get("event"),
        "location": result.get("location"),
        "timestamp": result.get("timestamp")
    }

    try:
        app_resp = requests.post(APPLICATION_CALLBACK_URL, json=payload, timeout=10)
        app_resp.raise_for_status()
        print(f"[INFO] Sent recognized student data to application: {APPLICATION_CALLBACK_URL}")
    except requests.RequestException as e:
        print(f"[WARN] Failed to send data to application: {e}")


def recognize(frame, api_url):
    """Encodes a frame and sends it to the backend for recognition."""
    ret, buf = cv2.imencode('.jpg', frame)
    if not ret:
        raise RuntimeError("Failed to encode image")

    files = {"file": ("capture.jpg", buf.tobytes(), "image/jpeg")}
    params = {"location": LOCATION}

    try:
        resp = requests.post(api_url, files=files, params=params, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        event_type = api_url.rstrip("/").split("/")[-1]
        log_capture_result(event_type, result)
        send_result_to_application(result)
        return result
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
        error_result = {"status": "Error", "detail": str(e), "response": getattr(e.response, 'text', None)}
        log_capture_result(api_url.rstrip("/").split("/")[-1], error_result)
        return error_result
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return {"status": "Error", "detail": str(e)}


def auto_select_event_type():
    """Auto-pick ENTRY for morning and EXIT for afternoon/evening."""
    now = datetime.datetime.now()
    return "ENTRY" if now.hour < 12 else "EXIT"


def print_instructions(event_type):
    """Prints clear instructions for the user."""
    print("\n" + "="*50)
    print(" " * 15 + "WEBCAM MONITOR")
    print("="*50)
    print(f" MODE:         {event_type.upper()}")
    print(" DESCRIPTION:  Automatically detects and recognizes faces in real time.")
    print("\n CONTROLS:")
    print("   'q' - Quit the application.")
    print("\n CAPTURE GUIDANCE:")
    print("   1. Keep your face visible on the screen.")
    print("   2. Any face angle is accepted; no circle alignment is required.")
    print("   3. The system auto-captures when a face is found.")
    print("\n AUTOMATION:")
    print("   Any detected face is checked automatically.")
    print("   Mode is chosen based on local time: AM = ENTRY, PM = EXIT.")
    print("\n VISUAL FEEDBACK:")
    print("   Green Box: Face detected and being recognized.")
    print("   Red Box: No match or student is not registered yet.")
    print("="*50 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capture a face and recognize it via the backend API")
    parser.add_argument("mode", nargs="?", default="AUTO", help="ENTRY/EXIT/AUTO")
    parser.add_argument("--image", "-i", help="Path to an image file to use instead of webcam")
    args = parser.parse_args()

    # Determine event type
    if args.mode.upper() == "AUTO":
        event_type = auto_select_event_type()
        print(f"Auto-selected mode based on time ({datetime.datetime.now().strftime('%H:%M')}): {event_type}")
    elif args.mode.upper() in ["ENTRY", "EXIT"]:
        event_type = args.mode.upper()
    else:
        print("Usage: python capture_and_recognize.py [ENTRY|EXIT|AUTO] [--image path]")
        sys.exit(1)

    api_url = get_api_url(event_type)

    if args.image:
        print(f"Recognizing using image: {args.image}")
        try:
            result = recognize_from_image(args.image, api_url)
            print("Result:", result)
        except Exception as e:
            print(f"Error: {e}")
        sys.exit(0)

    print("Capturing from webcam...")

    # 2. Load Face Detector
    if not os.path.exists(CASCADE_PATH):
        print(f"Error: Cascade file not found at '{CASCADE_PATH}'")
        print("Please download 'haarcascade_frontalface_default.xml' from the OpenCV repository")
        print("and place it in the same directory as this script.")
        sys.exit(1)
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

    # 3. Initialize Camera
    def open_camera(index=0):
        """Try opening the camera using a few different backends known to work on Windows."""
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for api in backends:
            cap = cv2.VideoCapture(index, api)
            if cap.isOpened():
                print(f"[INFO] Camera opened using backend {api}")
                return cap
            cap.release()
        return None

    cap = open_camera(0)
    if not cap or not cap.isOpened():
        print("Error: Cannot open camera. Make sure no other app is using it and that the camera is enabled.")
        sys.exit(1)

    # 4. State variables for display
    last_result = None
    last_result_time = 0
    last_capture_time = 0

    print_instructions(event_type)

    # 5. Main Loop
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break

        # --- Face Detection and Display Logic ---
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

        # Clear result after timeout
        if time.time() - last_result_time > RESULT_DISPLAY_TIME_SEC:
            last_result = None

        frame_h, frame_w = frame.shape[:2]

        # Draw rectangles for whichever faces are visible; no alignment circle restriction.
        for (x, y, w, h) in faces:
            color = (0, 255, 0)
            text = "Recognizing..."
            if last_result:
                if last_result.get("status") == "Recognized":
                    color = (0, 255, 0)
                    text = last_result.get("student", "Recognized")
                else:
                    color = (0, 0, 255)
                    text = "Not recognized"
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        if last_result:
            result_status = last_result.get("status", "")
            result_label = last_result.get("student") if result_status == "Recognized" else "Not recognized"
            if result_status == "Recognized":
                overlay_text = f"{result_label} - Grade {last_result.get('grade_level')} Section {last_result.get('section')}"
            else:
                overlay_text = "Face not registered. Please register this student first."
            cv2.putText(frame, overlay_text, (10, frame_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow(f"Campus Monitor - {event_type.upper()}", frame)

        # --- Automatic capture whenever any face is visible and enough time passed ---
        if len(faces) > 0 and (time.time() - last_capture_time) > AUTO_CAPTURE_INTERVAL_SEC:
            print(f"[{time.strftime('%H:%M:%S')}] Auto capturing frame for {event_type}...")
            result = recognize(frame, api_url)
            print("Result:", result)
            if result.get("status") == "Not Recognized":
                print("[INFO] Student is not yet registered. Please register the student first.")
            last_result = result
            last_result_time = time.time()
            last_capture_time = time.time()

        # --- Key Handling ---
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # 6. Cleanup
    cap.release()
    cv2.destroyAllWindows()
