import mysql.connector
import json

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="face_recognition_system"
    )

def save_student(student_id, first_name, last_name, grade_level, section, parent_id, parent_email, image_path, embedding):
    """Save student with all required fields matching the new schema"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO student (student_id, first_name, last_name, grade_level, section, parent_id, parent_email, image_path, face_encoding, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """, (student_id, first_name, last_name, grade_level, section, parent_id, parent_email, image_path, json.dumps(embedding.tolist())))
        conn.commit()
    finally:
        conn.close()

def get_students():
    """Get all active students with face encodings"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT student_id, first_name, last_name, grade_level, section, parent_email, face_encoding 
            FROM student 
            WHERE status='active'
        """)
        data = cursor.fetchall()
        return data
    finally:
        conn.close()

def get_student_by_id(student_id):
    """Get student details by student_id"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM student 
            WHERE student_id=%s AND status='active'
        """, (student_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def student_exists(student_id):
    """Check if student ID already exists"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT student_id FROM student 
            WHERE student_id=%s
        """, (student_id,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def get_parent_email(student_id):
    """Get parent email for a student"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT parent_email, first_name, last_name 
            FROM student 
            WHERE student_id=%s
        """, (student_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def save_campus_log(student_id, event_type, location="Main Gate", confidence_score=0.0, student_name=None, admin_id=None):
    """Record entry/exit event to entry_exit_log table"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO entry_exit_log (student_id, admin_id, event_type, location, confidence_score, student_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, admin_id, event_type.upper(), location, confidence_score, student_name))
        conn.commit()
    finally:
        conn.close()

def get_entry_exit_logs(student_id=None, event_type=None, days=None):
    """Get entry/exit logs with optional filtering"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT * FROM entry_exit_log WHERE 1=1"
        params = []
        
        if student_id:
            query += " AND student_id=%s"
            params.append(student_id)
        
        if event_type:
            query += " AND event_type=%s"
            params.append(event_type.upper())
        
        if days:
            query += " AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)"
            params.append(days)
        
        query += " ORDER BY timestamp DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()

def create_parent(email, password):
    """Create a new parent account"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO parent (email, password)
            VALUES (%s, %s)
        """, (email, password))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_parent(email):
    """Get parent by email"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM parent 
            WHERE email=%s
        """, (email,))
        return cursor.fetchone()
    finally:
        conn.close()

def create_admin(email, password):
    """Create a new admin account"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO admin (email, password)
            VALUES (%s, %s)
        """, (email, password))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_admin(email):
    """Get admin by email"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM admin 
            WHERE email=%s
        """, (email,))
        return cursor.fetchone()
    finally:
        conn.close()

def create_tables():
    """Create all tables according to the schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Parent table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parent (
            parent_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        ''')
        
        # Admin table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        ''')
        
        # Student table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            student_id VARCHAR(50) PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            grade_level VARCHAR(50) NOT NULL,
            section VARCHAR(50) NOT NULL,
            parent_id INT NOT NULL,
            parent_email VARCHAR(100) NOT NULL,
            face_encoding LONGTEXT NOT NULL,
            image_path TEXT,
            status ENUM('active', 'inactive') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES parent(parent_id) ON DELETE CASCADE,
            INDEX idx_student_id (student_id),
            INDEX idx_parent_id (parent_id),
            INDEX idx_status (status)
        )
        ''')
        
        # Entry/Exit Log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entry_exit_log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(50) NOT NULL,
            admin_id INT,
            event_type ENUM('ENTRY', 'EXIT') NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            location VARCHAR(100) DEFAULT 'Main Gate',
            confidence_score FLOAT DEFAULT 0.0,
            student_name VARCHAR(200) DEFAULT NULL,
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
            FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL,
            INDEX idx_student_id (student_id),
            INDEX idx_timestamp (timestamp),
            INDEX idx_event_type (event_type),
            INDEX idx_admin_id (admin_id)
        )
        ''')
        cursor.execute("ALTER TABLE entry_exit_log ADD COLUMN IF NOT EXISTS student_name VARCHAR(200) DEFAULT NULL")
        
        conn.commit()
    finally:
        conn.close()
