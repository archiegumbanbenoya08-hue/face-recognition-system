-- Face Recognition Campus Monitoring System Database Schema
-- Based on ERD with STUDENT, PARENT, ENTRY/EXIT LOG, and ADMIN tables

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- Create PARENT table
CREATE TABLE IF NOT EXISTS parent (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create ADMIN table
CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create STUDENT table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create ENTRY/EXIT LOG table
CREATE TABLE IF NOT EXISTS entry_exit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    admin_id INT,
    event_type ENUM('ENTRY', 'EXIT') NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(100) DEFAULT 'Main Gate',
    confidence_score FLOAT DEFAULT 0.0,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL,
    INDEX idx_student_id (student_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_event_type (event_type),
    INDEX idx_admin_id (admin_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample PARENT data
INSERT INTO parent (email, password) VALUES
('navarro@gmail.com', 'parent123'),
('ilustre@gmail.com', 'parent123'),
('benoya@gmail.com', 'parent123');

-- Insert sample ADMIN data
INSERT INTO admin (email, password) VALUES
('admin@campus.com', 'admin123');

-- Insert sample STUDENT data
INSERT INTO student (student_id, first_name, last_name, grade_level, section, parent_id, parent_email, face_encoding, image_path, status) VALUES
('S001', 'Kent', 'Navarro', '10', 'A', 1, 'navarro@gmail.com', '[]', 'student_images/kent.jpg', 'active'),
('S002', 'Avril', 'Ilustre', '10', 'B', 2, 'ilustre@gmail.com', '[]', 'student_images/avril.jpg', 'active'),
('S003', 'Archie', 'Benoya', '9', 'A', 3, 'benoya@gmail.com', '[]', 'student_images/archie.jpg', 'active');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
