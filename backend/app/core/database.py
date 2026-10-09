import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# For MySQL with PyMySQL
engine = create_engine(
    "mysql+pymysql://root:@localhost/face_recognition_system",
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mysql_connection():
    """Get direct MySQL connection for raw queries"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="face_recognition_system"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
