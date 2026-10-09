#!/usr/bin/env python3
import mysql.connector

try:
    conn = mysql.connector.connect(host='localhost', user='root', password='')
    cursor = conn.cursor()
    
    # Create database
    cursor.execute('CREATE DATABASE IF NOT EXISTS face_attendance')
    cursor.execute('USE face_attendance')
    
    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        parent_email VARCHAR(100) NOT NULL,
        image_path TEXT,
        embedding LONGTEXT,
        status ENUM("active", "inactive") DEFAULT "active",
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create campus_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS campus_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(50) NOT NULL,
        event_type ENUM("ENTRY","EXIT"),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        location VARCHAR(100) DEFAULT "Main Gate",
        confidence_score FLOAT DEFAULT 0.0,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    ''')
    
    # Create parent_notifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parent_notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(50) NOT NULL,
        parent_email VARCHAR(100) NOT NULL,
        event_type ENUM("ENTRY","EXIT"),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        notification_sent BOOLEAN DEFAULT FALSE,
        sent_at DATETIME
    )
    ''')
    
    # Insert sample students
    cursor.execute('''
    INSERT IGNORE INTO students (student_id, name, parent_email, image_path, status) 
    VALUES 
    ("S001", "Kent", "navarro@gmail.com", "student_images/kent.jpg", "active"),
    ("S002", "Avril", "ilustre@gmail.com", "student_images/avril.jpg", "active"),
    ("S003", "Archie", "benoya@gmail.com", "student_images/archie.jpg", "active")
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database created successfully")
    print("✓ Tables created")
    print("✓ Sample students inserted")
except Exception as e:
    print(f"Error: {e}")
