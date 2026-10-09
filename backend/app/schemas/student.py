from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class StudentRegisterSchema(BaseModel):
    student_id: str
    name: str
    parent_email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "S001",
                "name": "John Doe",
                "parent_email": "parent@example.com"
            }
        }

class StudentResponseSchema(BaseModel):
    student_id: str
    name: str
    parent_email: str
    status: str
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RecognitionRequestSchema(BaseModel):
    event_type: str  # ENTRY or EXIT
    location: Optional[str] = "Main Gate"

class RecognitionResponseSchema(BaseModel):
    status: str  # "Recognized" or "Not Recognized"
    student: Optional[str] = None
    student_id: Optional[str] = None
    event: Optional[str] = None
    parent_email: Optional[str] = None
    timestamp: Optional[datetime] = None

class CampusLogSchema(BaseModel):
    id: int
    student_id: str
    event_type: str
    location: str
    timestamp: datetime

    class Config:
        from_attributes = True

class CampusLogsResponseSchema(BaseModel):
    total: int
    logs: List[CampusLogSchema]
