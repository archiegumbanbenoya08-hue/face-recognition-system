import requests
import time
import cv2

# Base API URL - the backend will grab frames from its own webcam
API_BASE = "http://127.0.0.1:8000/api/face"
LOCATION = "Main Gate"


def recognize_entry():
    """Trigger recognition for ENTRY event using server's webcam"""
    url = f"{API_BASE}/recognize_local/ENTRY"
    params = {"location": LOCATION}
    return requests.post(url, params=params, timeout=30).json()


def show_camera_preview():
    """Open a webcam preview window until the user presses any key."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("⚠️  Cannot open webcam for preview")
        return
    print("(Press any key in the preview window to continue)")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️  Failed to grab frame from webcam")
            break
        cv2.imshow('Camera Preview', frame)
        # wait 30ms for a key; if any key hit, break
        if cv2.waitKey(30) != -1:
            break
    cap.release()
    cv2.destroyAllWindows()


def recognize_exit():
    """Trigger recognition for EXIT event using server's webcam"""
    url = f"{API_BASE}/recognize_local/EXIT"
    params = {"location": LOCATION}
    return requests.post(url, params=params, timeout=30).json()


def print_result(result):
    """Pretty-print the recognition result"""
    print("\n" + "="*70)
    if result.get("status") == "Recognized":
        print(f"✅ RECOGNIZED - Student Detected!")
        print(f"   Name: {result.get('student')}")
        print(f"   ID: {result.get('student_id')}")
        print(f"   Event: {result.get('event')}")
        print(f"   Parent Email: {result.get('parent_email')}")
        print(f"   📧 Notification sent to parent!")
    else:
        print(f"❌ NOT RECOGNIZED - Unknown person")
    print("="*70 + "\n")


def main():
    print("\n" + "="*70)
    print("🎥 Face Recognition System - Campus Entry/Exit Monitor")
    print("="*70)
    print("Backend uses the connected webcam for capture")
    print("="*70)
    
    while True:
        print("\nOptions:")
        print("  1 - Recognize ENTRY (student entering campus)")
        print("  2 - Recognize EXIT (student leaving campus)")
        print("  3 - Continuous mode (auto-capture every 3 seconds)")
        print("  q - Quit")
        
        choice = input("\nEnter choice: ").strip().lower()
        
        if choice == "q":
            print("\n👋 Exiting system...")
            break
        elif choice == "1":
            try:
                print("\n📸 Showing camera preview...")
                show_camera_preview()
                print("\n📸 Capturing from webcam for ENTRY event...")
                result = recognize_entry()
                print_result(result)
            except requests.exceptions.ConnectionError:
                print("❌ Error: Cannot connect to backend. Is it running?")
                print("   Start it with: python -m uvicorn main:app --reload")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif choice == "2":
            try:
                print("\n📸 Showing camera preview...")
                show_camera_preview()
                print("\n📸 Capturing from webcam for EXIT event...")
                result = recognize_exit()
                print_result(result)
            except requests.exceptions.ConnectionError:
                print("❌ Error: Cannot connect to backend. Is it running?")
                print("   Start it with: python -m uvicorn main:app --reload")
            except Exception as e:
                print(f"❌ Error: {e}")
        elif choice == "3":
            print("\n📸 Continuous recognition mode (press Ctrl+C to stop)...")
            try:
                counter = 0
                while True:
                    try:
                        counter += 1
                        print(f"\n[{counter}] Capturing from webcam... (ENTRY)")
                        result = recognize_entry()
                        print_result(result)
                    except Exception as e:
                        print(f"❌ Error on capture: {e}")
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\n⏹ Stopping continuous mode...")
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or q")


if __name__ == "__main__":
    main()
