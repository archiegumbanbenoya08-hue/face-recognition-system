# Student Face Registration Module - Setup & Usage Guide

## Overview

This is a comprehensive student face registration system using:
- **Python** for backend processing
- **OpenCV** for camera capture and face detection  
- **face_recognition** library for face encoding
- **TensorFlow/MobileNetV2** for feature extraction
- **MySQL** database for persistent storage

---

## System Architecture

```
registration.py          (Main orchestration)
├── camera.py           (Webcam capture with guidance)
├── encoding.py         (Face encoding generation)
├── database.py         (MySQL operations)
└── face_engine.py      (TensorFlow embeddings)
```

---

## Installation & Setup

### 1. Install Python Dependencies

```bash
pip install opencv-python face-recognition tensorflow numpy mysql-connector-python
```

### 2. Download Haar Cascade File

The face detection cascade file is required:

```bash
# The file should be named: haarcascade_frontalface_default.xml
# It's already included in backend/ directory

# If missing, download from:
# https://github.com/opencv/opencv/tree/master/data/haarcascades
```

### 3. Setup MySQL Database

Using XAMPP or standalone MySQL:

```sql
-- Create database
CREATE DATABASE face_recognition_system;

-- Use the database
USE face_recognition_system;

-- Tables are auto-created by Python on first run
-- But you can manually create them using the schema
```

### 4. Configure Database Connection

Edit [backend/database.py](backend/database.py) - Update connection details if needed:

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",      # MySQL server host
        user="root",           # MySQL username
        password="",           # MySQL password
        database="face_recognition_system"  # Database name
    )
```

---

## Module Documentation

### camera.py - Webcam Capture Module

**Classes:**
- `FaceDetector` - Detects faces using Haar Cascade
- `BlurDetector` - Checks image sharpness
- `CameraCapture` - Main camera interface with guidance

**Key Features:**
- Real-time face detection
- Blur quality checking
- Positioning guidance (on-screen instructions)
- Auto-capture when properly positioned
- Multiple pose guidance (front, left, right, up, down, smile, neutral)

**Example:**
```python
from camera import CameraCapture

camera = CameraCapture()
frame = camera.capture_with_guidance(
    instruction_type='front',
    total_captures=50,
    current_count=0,
    blur_threshold=100.0,
    auto_capture=True,
    auto_capture_delay=1.0
)

# Crop face from frame
cropped_face = camera.crop_face(frame, padding=20)
```

### encoding.py - Face Encoding Module

**Classes:**
- `FaceEncoder` - Generate face embeddings
- `EncodingStorage` - JSON serialization
- `FaceComparison` - Compare face encodings

**Key Features:**
- Dual encoding support (face_recognition + TensorFlow)
- Batch encoding of multiple images
- Euclidean distance comparison
- Cosine similarity matching
- Face database lookup

**Example:**
```python
from encoding import FaceEncoder, FaceComparison

# Encode single face
encoding = FaceEncoder.encode_face("path/to/image.jpg")

# Batch encode
encodings = FaceEncoder.encode_batch([
    "path/to/image1.jpg",
    "path/to/image2.jpg",
])

# Compare faces
match = FaceComparison.compare_faces(encoding1, encoding2, threshold=0.6)
```

### registration.py - Main Registration Workflow

**Classes:**
- `RegistrationForm` - Interactive user input
- `DatasetManager` - Organized image storage
- `StudentRegistration` - Complete registration workflow

**Capture Sequence:**
- 7 different poses × 3 samples each = 21 total captures
- Poses: Front, Left, Right, Up, Down, Smile, Neutral
- Minimum blur checking and quality validation

**Example:**
```python
from registration import StudentRegistration

registration = StudentRegistration()
success = registration.register_student(test_mode=False)
```

### database.py - MySQL Operations

**Key Functions:**
- `create_tables()` - Initialize database schema
- `save_student()` - Save student record with encoding
- `get_student_by_id()` - Retrieve student
- `student_exists()` - Check if student already registered
- `get_parent()` / `create_parent()` - Parent management
- `save_campus_log()` - Record entry/exit events

---

## Usage Guide

### Method 1: Interactive Registration (Recommended)

Run the interactive registration script:

```bash
cd "C:\Users\Admin\Desktop\Face Recognition"
python backend/registration.py
```

**What happens:**
1. Enter student details (ID, name, grade, section, parent email)
2. Camera opens with real-time guidance
3. Automatically captures 21 face samples
4. Generates face encodings
5. Saves to database

**Console Output Example:**
```
============================================================
STUDENT FACE REGISTRATION
============================================================

Enter Student ID (e.g., 2025-001): 2025-001
Enter First Name: Archie
Enter Last Name: Benoya
Enter Grade Level (e.g., 1-12): 6
Enter Section (e.g., A, B, C): A
Enter Parent Email: archiegumbanbenoya08@gmail.com

============================================================
STEP 1: STUDENT INFORMATION
============================================================
✓ Student information validated

============================================================
STEP 2: DATASET SETUP
============================================================
✓ Dataset folder: dataset/2025-001

============================================================
STEP 3: FACE CAPTURE
============================================================
Capture 21 samples for best recognition accuracy.

--- Pose 1/7: Face FRONT - Look directly at camera ---
Press SPACE to capture, or Q to quit
✓ Position OK - Ready to capture
Saved: dataset/2025-001/1.jpg
...
Captured: 21 samples

============================================================
STEP 4: FACE ENCODING
============================================================
Processing 21 images...
✓ Generated 21 encodings

============================================================
STEP 5: DATABASE STORAGE
============================================================
✓ Saved to database: 2025-001

============================================================
✓ REGISTRATION COMPLETE
============================================================

Student: Archie Benoya
ID: 2025-001
Grade: 6
Section: A
Samples: 21
Dataset: dataset/2025-001

Student is ready for face recognition!
```

### Method 2: Command-Line Registration (Quick)

For faster registration without multiple poses:

```bash
python backend/register_student_webcam.py `
  --student-id 2025-002 `
  --first-name John `
  --last-name Doe `
  --grade-level 8 `
  --section B `
  --parent-email john.doe@example.com
```

This captures 1 sample only.

---

## Dataset Organization

After registration, datasets are stored as:

```
dataset/
├── 2025-001/
│   ├── 1.jpg    (Front)
│   ├── 2.jpg    (Front)
│   ├── 3.jpg    (Front)
│   ├── 4.jpg    (Left)
│   ├── 5.jpg    (Left)
│   ├── 6.jpg    (Left)
│   ├── 7.jpg    (Right)
│   ├── 8.jpg    (Right)
│   ├── 9.jpg    (Right)
│   ├── 10.jpg   (Up)
│   ├── 11.jpg   (Up)
│   ├── 12.jpg   (Up)
│   ├── 13.jpg   (Down)
│   ├── 14.jpg   (Down)
│   ├── 15.jpg   (Down)
│   ├── 16.jpg   (Smile)
│   ├── 17.jpg   (Smile)
│   ├── 18.jpg   (Smile)
│   ├── 19.jpg   (Neutral)
│   ├── 20.jpg   (Neutral)
│   └── 21.jpg   (Neutral)
├── 2025-002/
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ...
└── 2025-003/
    └── ...
```

---

## Database Schema

### student table
```sql
CREATE TABLE student (
    student_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    grade_level VARCHAR(50) NOT NULL,
    section VARCHAR(50) NOT NULL,
    parent_id INT NOT NULL,
    parent_email VARCHAR(100) NOT NULL,
    face_encoding LONGTEXT NOT NULL,  -- JSON array of encoding values
    image_path TEXT,                   -- Path to dataset folder
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES parent(parent_id)
);
```

### parent table
```sql
CREATE TABLE parent (
    parent_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### entry_exit_log table
```sql
CREATE TABLE entry_exit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    event_type ENUM('ENTRY', 'EXIT') NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(100) DEFAULT 'Main Gate',
    confidence_score FLOAT DEFAULT 0.0,
    student_name VARCHAR(200),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);
```

---

## Camera Controls

During face capture:

| Key | Action |
|-----|--------|
| `SPACE` | Manual capture (if face detected) |
| `Q` | Quit registration |
| `S` | Skip current pose |

**On-Screen Indicators:**
- 🟢 Green rectangle = Face well positioned
- 🟡 Yellow rectangle = Adjust position
- 🔴 Red circle = No face detected

---

## Quality Checks

### Blur Detection
- Measures image sharpness using Laplacian variance
- Threshold: 100.0 (higher = stricter)
- Skips blurry frames automatically

### Face Detection
- Uses Haar Cascade classifier
- Detects frontal faces reliably
- Minimum face size: 50×50 pixels

### Positioning Check
- Face must be centered in capture zone
- Face width should be 20-60% of frame width
- Auto-captures when well-positioned (1 second delay)

---

## Troubleshooting

### "Cannot open camera"
```
Solutions:
1. Close other apps using camera (Zoom, Teams, etc.)
2. Check Windows Camera app permissions
3. Try different USB port (if external camera)
4. Update camera drivers
5. Restart computer
```

### "No face detected"
```
Solutions:
1. Ensure good lighting (natural or bright artificial)
2. Keep face 30-60cm from camera
3. Face should be front-facing or slightly angled
4. Minimize shadows/backlighting
```

### "Duplicate entry error"
```
Solutions:
1. Use a different student ID
2. Or delete existing student record from MySQL:
   DELETE FROM student WHERE student_id='2025-001';
```

### "Database connection failed"
```
Solutions:
1. Verify MySQL server is running
2. Check database credentials in database.py
3. Ensure database exists:
   CREATE DATABASE face_recognition_system;
```

### "TensorFlow warnings/errors"
```
Note: These are normal and can be ignored:
- "TensorFlow GPU support is not available on native Windows"
- "oneDNN custom operations are on"

The system will fall back to CPU processing automatically.
```

---

## Advanced Usage

### Testing Modules Individually

```bash
# Test camera
python backend/camera.py

# Test encoding
python backend/encoding.py

# Test database
python backend/database.py
```

### Manual Face Encoding

```python
from encoding import FaceEncoder, EncodingStorage
import os

# Encode all images in a folder
image_folder = "dataset/2025-001"
images = [os.path.join(image_folder, f) for f in os.listdir(image_folder)]

encodings = FaceEncoder.encode_batch(images)

# Save to file
EncodingStorage.save_encodings_to_file(encodings, "encodings.json")

# Load from file
loaded = EncodingStorage.load_encodings_from_file("encodings.json")
```

### Batch Registration

```python
from registration import StudentRegistration

students = [
    {'student_id': '2025-001', 'first_name': 'Archie', ...},
    {'student_id': '2025-002', 'first_name': 'John', ...},
]

for student_data in students:
    reg = StudentRegistration()
    reg.registration_data = student_data
    reg.register_student()
```

---

## Performance Tips

1. **Good Lighting:** Capture in well-lit environment (min 500 lux)
2. **Face Distance:** Position face 40-60cm from camera
3. **Multiple Angles:** The 21-sample capture provides high accuracy
4. **Clean Lens:** Keep camera lens clean
5. **Batch Processing:** Register multiple students in one session

---

## Security Notes

- Default parent password is "default_password" - change immediately
- Store MySQL passwords securely
- Restrict dataset folder access
- Use HTTPS when deploying web interfaces
- Implement proper authentication for admin functions

---

## Integration with Recognition System

After registration, students can be recognized using:

```bash
# Capture and recognize in real-time
python backend/capture_and_recognize.py ENTRY

# Or with specific location
python backend/capture_and_recognize.py EXIT

# Or from image file
python backend/capture_and_recognize.py ENTRY --image path/to/image.jpg
```

---

## File Summary

| File | Purpose |
|------|---------|
| `camera.py` | Webcam capture with face detection |
| `encoding.py` | Face encoding generation |
| `registration.py` | Main registration workflow |
| `database.py` | MySQL operations |
| `register_student_webcam.py` | Quick single-sample registration |
| `capture_and_recognize.py` | Real-time recognition |
| `face_engine.py` | TensorFlow model loading |

---

## License

Educational use only. Modify as needed for your institution.

---

**Last Updated:** May 2026  
**Version:** 1.0  
**Status:** Production Ready
