import os
import shutil
import json
import smtplib
import datetime
from email.mime.text import MIMEText
import numpy as np
import cv2
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from encoding import FaceEncoder, EncodingStorage
from database import (
    save_student, get_students, save_campus_log, create_tables, 
    get_parent_email, create_parent, get_parent, get_entry_exit_logs
)
from event_logger import log_event, read_all_events

try:
    import face_recognition as fr
    FR_AVAILABLE = True
    print("[OK] face_recognition available in main API")
except ImportError:
    FR_AVAILABLE = False
    print("[WARN] face_recognition not installed in main API")


def compare_embedding(known_embedding, query_embedding, distance_threshold=0.6):
    if FR_AVAILABLE:
        try:
            matches = fr.compare_faces([known_embedding], query_embedding, tolerance=distance_threshold)
            distances = fr.face_distance([known_embedding], query_embedding)
            return matches[0], float(distances[0])
        except Exception as e:
            print(f"[WARN] face_recognition compare failed: {e}")
    distance = np.linalg.norm(known_embedding - query_embedding)
    return (distance < distance_threshold), float(distance)


def send_parent_notification(parent_email: str, student_name: str, event_type: str, location: str):
    """Send a simple email alert to the registered parent when a child is detected."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("EMAIL_FROM", smtp_user or "noreply@campus.local")

    if not parent_email:
        print("[INFO] No parent email available for notification.")
        return False

    if not smtp_user or not smtp_password:
        print(f"[INFO] SMTP not configured. Parent email alert skipped for {parent_email}.")
        return False

    subject = f"Campus {event_type.upper()} Alert - {student_name}"
    body = (
        f"Hello,\n\n"
        f"{student_name} was detected at the campus {event_type.upper()} check-in/out.\n"
        f"Location: {location}\n"
        f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "This is an automated campus monitoring notification."
    )

    try:
        message = MIMEText(body)
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = parent_email

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)

        print(f"[OK] Email alert sent to {parent_email} for {student_name}.")
        return True
    except Exception as exc:
        print(f"[WARN] Failed to send email to {parent_email}: {exc}")
        return False


app = FastAPI(
    title="Face Recognition Campus Monitoring",
    version="1.0.0",
    description="API for campus entry/exit monitoring",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "student_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure DB tables exist
try:
    create_tables()
except Exception as e:
    print(f"Warning: Could not create tables: {e}")

@app.get("/")
def read_root():
    """Root endpoint - API documentation"""
    return {
        "app": "Face Recognition Campus Monitoring",
        "version": "1.0.0",
        "docs": "/docs",
        "message": "Welcome to campus entry/exit monitoring system"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Face Recognition Campus Monitoring",
    }

@app.post("/register/")
async def register_student(
    student_id: str = Form(...), 
    first_name: str = Form(...), 
    last_name: str = Form(...),
    grade_level: str = Form(...),
    section: str = Form(...),
    parent_email: str = Form(...), 
    file: UploadFile = File(...)
):
    """Register student with image and all required details"""
    try:
        # Get or create parent
        parent = get_parent(parent_email)
        if not parent:
            # Create parent if doesn't exist (with default password)
            parent_id = create_parent(parent_email, "default_password")
        else:
            parent_id = parent["parent_id"]
        
        # Save student image
        file_path = os.path.join(UPLOAD_FOLDER, f"{student_id}.jpg")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate face encoding using face_recognition if available
        embedding = FaceEncoder.encode_face(file_path)
        if embedding is None:
            raise ValueError("No face found in uploaded image. Please upload a clear face photo.")
        
        # Save student with new schema
        save_student(student_id, first_name, last_name, grade_level, section, parent_id, parent_email, file_path, embedding)
        
        return {
            "message": "Student Registered Successfully", 
            "student_id": student_id,
            "name": f"{first_name} {last_name}",
            "grade_level": grade_level,
            "section": section
        }
    except Exception as e:
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "Error", "detail": str(e)}

@app.post("/recognize/{event_type}")
async def recognize(event_type: str, file: UploadFile = File(...), location: str = "Main Gate"):
    """Campus entry/exit monitoring - records entry/exit only"""
    try:
        temp_path = "temp.jpg"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        new_embedding = FaceEncoder.encode_face(temp_path)
        if new_embedding is None:
            raise ValueError("No face found in captured image. Please try again.")
        print(f"📸 Captured embedding shape: {new_embedding.shape}")
        
        students = get_students()
        print(f"📋 Checking against {len(students)} registered students")
        
        for student in students:
            try:
                saved_embedding = EncodingStorage.deserialize_encoding(student["face_encoding"])
                full_name = f"{student['first_name']} {student['last_name']}"
                print(f"   Comparing with {full_name}: stored embedding shape {saved_embedding.shape}")
                
                # Skip students with invalid/empty embeddings
                if saved_embedding.shape[0] == 0 or len(saved_embedding) == 0:
                    print(f"   Skipping {full_name} - invalid embedding")
                    continue
                
                matched, distance = compare_embedding(saved_embedding, new_embedding)
                print(f"   Distance to {full_name}: {distance:.4f} -> matched={matched}")
                if matched:
                    print(f"✅ Match found: {full_name}")
                    
                    # Save event to JSONL log
                    log_event(
                        event_type=event_type,
                        student_id=student["student_id"],
                        location=location,
                        status="recognized",
                        details={"student_name": full_name}
                    )
                    
                    # Record campus entry/exit
                    save_campus_log(student["student_id"], event_type.upper(), location, student_name=full_name)
                    
                    # Get parent info
                    parent_info = get_parent_email(student["student_id"])
                    parent_email = parent_info["parent_email"] if parent_info else None
                    if parent_email:
                        print(f"📧 Notification: {full_name} ({student['student_id']}) has {event_type} at {location}")
                        print(f"   Parent: {parent_email}")
                        send_parent_notification(parent_email, full_name, event_type, location)
                    
                    return {
                        "status": "Recognized",
                        "student": full_name,
                        "student_id": student["student_id"],
                        "grade_level": student["grade_level"],
                        "section": student["section"],
                        "event": event_type.upper(),
                        "location": location,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "parent_email": parent_email,
                        "email_sent": bool(parent_email)
                    }
            except Exception as e:
                print(f"   Error comparing with {student['first_name']} {student['last_name']}: {e}")
                continue
        
        print(f"❌ No match found")
        log_event(
            event_type=event_type,
            student_id=None,
            location=location,
            status="not_recognized",
            details={"reason": "no matching embedding"}
        )
        return {"status": "Not Recognized"}
    
    except Exception as e:
        print(f"Recognition error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "Error", "detail": str(e)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/entry_exit_logs/")
async def get_logs(student_id: str = None, event_type: str = None, days: int = None):
    """Get entry/exit logs with optional filtering"""
    try:
        logs = get_entry_exit_logs(student_id, event_type, days)
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return {"status": "Error", "detail": str(e)}

@app.get("/students/")
async def get_all_students():
    """Get all active students"""
    try:
        students = get_students()
        return {"students": students, "count": len(students)}
    except Exception as e:
        print(f"Error retrieving students: {e}")
        return {"status": "Error", "detail": str(e)}

@app.get("/events/")
async def get_all_events():
    """Get all logged events from JSONL file"""
    try:
        events = read_all_events()
        return {"events": events, "count": len(events)}
    except Exception as e:
        print(f"Error retrieving events: {e}")
        return {"status": "Error", "detail": str(e)}

@app.post("/api/face/recognize_local/{event_type}")
async def recognize_local(event_type: str, location: str = "Main Gate"):
    """Recognize face using server's webcam for local monitoring"""
    try:
        # Capture frame from webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {"status": "Error", "detail": "Cannot open webcam"}
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {"status": "Error", "detail": "Failed to capture image from webcam"}
        
        # Save temp image
        temp_path = "temp_local.jpg"
        cv2.imwrite(temp_path, frame)
        
        # Generate embedding
        new_embedding = FaceEncoder.encode_face(temp_path)
        if new_embedding is None:
            raise ValueError("No face found in local webcam capture. Please retry.")
        print(f"📸 Local capture embedding shape: {new_embedding.shape}")
        
        students = get_students()
        print(f"📋 Checking against {len(students)} registered students")
        
        for student in students:
            try:
                saved_embedding = EncodingStorage.deserialize_encoding(student["face_encoding"])
                full_name = f"{student['first_name']} {student['last_name']}"
                print(f"   Comparing with {full_name}: stored embedding shape {saved_embedding.shape}")
                
                # Skip students with invalid/empty embeddings
                if saved_embedding.shape[0] == 0 or len(saved_embedding) == 0:
                    print(f"   Skipping {full_name} - invalid embedding")
                    continue
                
                matched, distance = compare_embedding(saved_embedding, new_embedding)
                print(f"   Distance to {full_name}: {distance:.4f} -> matched={matched}")
                if matched:
                    print(f"✅ Match found: {full_name}")

                    log_event(
                        event_type=event_type,
                        student_id=student["student_id"],
                        location=location,
                        status="recognized",
                        details={"student_name": full_name, "source": "local"}
                    )

                    # Record campus entry/exit
                    save_campus_log(student["student_id"], event_type.upper(), location, student_name=full_name)
                    
                    # Get parent info
                    parent_info = get_parent_email(student["student_id"])
                    parent_email = parent_info["parent_email"] if parent_info else None
                    if parent_email:
                        print(f"📧 Notification: {full_name} ({student['student_id']}) has {event_type} at {location}")
                        print(f"   Parent: {parent_email}")
                        send_parent_notification(parent_email, full_name, event_type, location)
                    
                    return {
                        "status": "Recognized",
                        "student": full_name,
                        "student_id": student["student_id"],
                        "grade_level": student["grade_level"],
                        "section": student["section"],
                        "event": event_type.upper(),
                        "location": location,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "parent_email": parent_email,
                        "email_sent": bool(parent_email)
                    }
            except Exception as e:
                print(f"   Error comparing with {student['first_name']} {student['last_name']}: {e}")
                continue
        
        print(f"❌ No match found")
        log_event(
            event_type=event_type,
            student_id=None,
            location=location,
            status="not_recognized",
            details={"reason": "no matching embedding", "source": "local"}
        )
        return {"status": "Not Recognized"}
    
    except Exception as e:
        print(f"Local recognition error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "Error", "detail": str(e)}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
