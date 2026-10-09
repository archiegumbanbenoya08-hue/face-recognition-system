#!/usr/bin/env python3
"""
Local real-time face recognizer using `trained_faces.pkl` or `encodings.json`.

- Loads known encodings and names
- Captures webcam frames, detects faces with Haar cascade
- Extracts a face ROI, encodes it using `encoding.FaceEncoder.encode_face()` (writes temp file)
- Compares with known encodings (Euclidean distance)
- Draws box + name and overlays name at bottom

Usage:
    python recognize_local.py --threshold 0.6

"""
import os
import time
import argparse
import tempfile
import pickle
import json
import numpy as np
import cv2
from encoding import FaceEncoder

SCRIPT_DIR = os.path.dirname(__file__)
CASCADE_PATH = os.path.join(SCRIPT_DIR, "haarcascade_frontalface_default.xml")
PKL_PATH = os.path.join(SCRIPT_DIR, "trained_faces.pkl")
JSON_PATH = os.path.join(SCRIPT_DIR, "encodings.json")


def load_known_encodings(pkl_path=PKL_PATH, json_path=JSON_PATH):
    encodings = []
    names = []

    if os.path.exists(pkl_path):
        try:
            with open(pkl_path, "rb") as f:
                data = pickle.load(f)
            raw_enc = data.get("encodings")
            raw_names = data.get("names")
            if raw_enc and raw_names and len(raw_enc) == len(raw_names):
                encodings = [np.array(e) for e in raw_enc]
                names = list(raw_names)
                print(f"Loaded {len(encodings)} encodings from {pkl_path}")
                return encodings, names
        except Exception as e:
            print(f"Warning: failed to load pickle: {e}")

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for path, enc in data.items():
                encodings.append(np.array(enc))
                # derive name from path: student_images/<id>.jpg or dataset/<person>/file.jpg
                name = os.path.basename(os.path.dirname(path)) if os.path.dirname(path) and os.path.dirname(path) != '.' else os.path.splitext(os.path.basename(path))[0]
                names.append(name)
            print(f"Loaded {len(encodings)} encodings from {json_path}")
            return encodings, names
        except Exception as e:
            print(f"Warning: failed to load json encodings: {e}")

    print("No known encodings found (trained_faces.pkl or encodings.json missing or invalid).")
    return [], []


def find_best_match(query_enc, known_encodings, known_names, threshold=0.6):
    if len(known_encodings) == 0:
        return None, None
    dists = [np.linalg.norm(k - query_enc) for k in known_encodings]
    best_idx = int(np.argmin(dists))
    best_dist = float(dists[best_idx])
    if best_dist <= threshold:
        return known_names[best_idx], best_dist
    return None, best_dist


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.6, help="Distance threshold for match")
    parser.add_argument("--camera", type=int, default=0, help="Camera index")
    args = parser.parse_args()

    known_encodings, known_names = load_known_encodings()
    if not known_encodings:
        print("No encodings loaded. Run backend/train_embeddings.py first or provide trained_faces.pkl.")

    if not os.path.exists(CASCADE_PATH):
        print(f"Cascade file not found at {CASCADE_PATH}. Download and place 'haarcascade_frontalface_default.xml' next to this script.")
        return

    cascade = cv2.CascadeClassifier(CASCADE_PATH)

    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    print("Starting local recognition. Press 'q' to quit.")

    temp_dir = tempfile.gettempdir()
    last_name = None
    last_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60,60))

        name_to_show = None
        for (x,y,w,h) in faces:
            # Expand box slightly for better encoding
            pad = int(0.2 * max(w,h))
            x0 = max(x - pad, 0)
            y0 = max(y - pad, 0)
            x1 = min(x + w + pad, frame.shape[1])
            y1 = min(y + h + pad, frame.shape[0])

            face_img = frame[y0:y1, x0:x1]

            # Save face crop to temp file and encode using FaceEncoder
            tmp_path = os.path.join(temp_dir, f"_fr_temp_{int(time.time()*1000)}.jpg")
            cv2.imwrite(tmp_path, face_img)
            try:
                query_enc = FaceEncoder.encode_face(tmp_path)
            except Exception as e:
                print(f"Encoding error: {e}")
                query_enc = None
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

            label = "Unknown"
            if query_enc is not None and len(known_encodings) > 0:
                name, dist = find_best_match(query_enc, known_encodings, known_names, threshold=args.threshold)
                if name:
                    label = f"{name} ({dist:.2f})"
                    name_to_show = name
                else:
                    label = f"Unknown ({dist:.2f})"

            # Draw box and label
            color = (0,255,0) if label != "Unknown" else (0,0,255)
            cv2.rectangle(display_frame, (x0,y0), (x1,y1), color, 2)
            cv2.putText(display_frame, label, (x0, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Overlay name at bottom if present
        now = time.time()
        if name_to_show:
            last_name = name_to_show
            last_time = now

        if last_name and (now - last_time) < 5.0:
            text = f"Recognized: {last_name}"
            cv2.putText(display_frame, text, (10, display_frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)

        cv2.imshow("Local Recognizer", display_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
