from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base

class Student(Base):
    __tablename__ = "student"
    
    student_id = Column(String(50), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    grade_level = Column(String(50), nullable=False)
    section = Column(String(50), nullable=False)
    parent_id = Column(Integer, nullable=False, index=True)
    parent_email = Column(String(100), nullable=False)
    face_encoding = Column(Text, nullable=False)  # Store as JSON string
    image_path = Column(String(500), nullable=True)
    status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "grade_level": self.grade_level,
            "section": self.section,
            "parent_id": self.parent_id,
            "parent_email": self.parent_email,
            "image_path": self.image_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Parent(Base):
    __tablename__ = "parent"
    
    parent_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "parent_id": self.parent_id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Admin(Base):
    __tablename__ = "admin"
    
    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "admin_id": self.admin_id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class EntryExitLog(Base):
    __tablename__ = "entry_exit_log"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(50), nullable=False, index=True)
    admin_id = Column(Integer, nullable=True, index=True)
    event_type = Column(String(10), nullable=False, index=True)  # ENTRY or EXIT
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    location = Column(String(100), default="Main Gate")
    confidence_score = Column(String(10), default=0.0)
    
    def to_dict(self):
        return {
            "log_id": self.log_id,
            "student_id": self.student_id,
            "admin_id": self.admin_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "location": self.location,
            "confidence_score": self.confidence_score,
        }
