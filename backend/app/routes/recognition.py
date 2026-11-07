import os
import shutil
import json
import numpy as np
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, Depends
# webcam support
import cv2
from sqlalchemy.orm import Session
from app.core.database import get_db, get_mysql_connection
from app.models.student import Student
from app.schemas.student import (
    StudentRegisterSchema, 
    StudentResponseSchema,
    RecognitionResponseSchema,
)

from face_engine import get_embedding, compare_faces

router = APIRouter(prefix="/api/face", tags=["Face Recognition"])

UPLOAD_FOLDER = "student_images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def _recognize_embedding(embedding, db, event_type, location):
    """Helper: given an embedding array, match a student and return response dict."""
    students = db.query(Student).filter(Student.status == "active").all()
    for student in students:
        try:
            saved_embedding = np.array(json.loads(student.embedding))
            if compare_faces(embedding, saved_embedding):
                return RecognitionResponseSchema(
                    status="Recognized",
                    student=student.name,
                    student_id=student.student_id,
                    event=event_type.upper(),
                    parent_email=student.parent_email,
                )
        except Exception as e:
            print(f"Error comparing face: {e}")
            continue
    return RecognitionResponseSchema(status="Not Recognized")


@router.post("/register/", response_model=dict)
async def register_student(
    student_id: str = Form(...),
    name: str = Form(...),
    parent_email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Register a new student with face image"""
    try:
        # Save uploaded image
        file_path = os.path.join(UPLOAD_FOLDER, f"{student_id}.jpg")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract embedding
        embedding = get_embedding(file_path)
        embedding_json = json.dumps(embedding.tolist())
        
        # Check if student already exists
        existing_student = db.query(Student).filter(Student.student_id == student_id).first()
        if existing_student:
            # Update existing student
            existing_student.name = name
            existing_student.parent_email = parent_email
            existing_student.image_path = file_path
            existing_student.embedding = embedding_json
            existing_student.status = "active"
            db.commit()
            return {
                "status": "success",
                "message": "Student updated successfully",
                "student_id": student_id
            }
        else:
            # Create new student
            student = Student(
                student_id=student_id,
                name=name,
                parent_email=parent_email,
                image_path=file_path,
                embedding=embedding_json,
                status="active"
            )
            db.add(student)
            db.commit()
            
        return {
            "status": "success",
            "message": "Student registered successfully",
            "student_id": student_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@router.post("/recognize/{event_type}", response_model=RecognitionResponseSchema)
async def recognize_face(
    event_type: str,
    file: UploadFile = File(...),
    location: str = "Main Gate",
    db: Session = Depends(get_db)
):
    """Recognize a student from face image"""
    try:
        # Save temp image
        temp_path = "temp.jpg"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get embedding for captured face
        new_embedding = get_embedding(temp_path)
        result = _recognize_embedding(new_embedding, db, event_type, location)
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Recognition failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/recognize_local/{event_type}", response_model=RecognitionResponseSchema)
async def recognize_local(event_type: str,
                           location: str = "Main Gate",
                           db: Session = Depends(get_db)):
    """Capture frame from server webcam and run recognition"""
    # try to open camera 0
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="Cannot open webcam")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise HTTPException(status_code=500, detail="Failed to capture image")

    # write temporary file for embedding
    temp_path = "temp.jpg"
    cv2.imwrite(temp_path, frame)
    try:
        new_embedding = get_embedding(temp_path)
        result = _recognize_embedding(new_embedding, db, event_type, location)
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Recognition failed: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/students/", response_model=list)
async def get_all_students(db: Session = Depends(get_db)):
    """Get all registered students"""
    try:
        students = db.query(Student).filter(Student.status == "active").all()
        return [student.to_dict() for student in students]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get students: {str(e)}")

@router.get("/student/{student_id}", response_model=dict)
async def get_student(student_id: str, db: Session = Depends(get_db)):
    """Get specific student details"""
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get student: {str(e)}")
        ~os.remove(temp_path)

@router.get("/students/", response_model=list[StudentResponseSchema])
async def get_all_students(db: Session = Depends(get_db)):
    """Get all registered active students"""
    try:
        students = db.query(Student).filter(Student.status == "active").all()
        return students
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/campus-logs/", response_model=CampusLogsResponseSchema)
async def get_campus_logs(
    student_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get campus entry/exit logs"""
    try:
        query = db.query(CampusLog)
        
        if student_id:
            query = query.filter(CampusLog.student_id == student_id)
        
        logs = query.order_by(CampusLog.timestamp.desc()).limit(limit).all()
        
        return CampusLogsResponseSchema(
            total=len(logs),
            logs=logs
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/student/{student_id}", response_model=StudentResponseSchema)
async def get_student(student_id: str, db: Session = Depends(get_db)):
    """Get specific student details"""
    try:
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
