# Face Recognition Backend Integration with Flutter

## Backend Setup Complete ✅

Your FastAPI backend is now structured and running on `http://localhost:8000` (or `http://192.168.x.x:8000` from your network)

### Backend Architecture

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py        # Configuration & settings
│   │   └── database.py      # Database connection & setup
│   ├── models/
│   │   └── student.py       # SQLAlchemy ORM models
│   ├── routes/
│   │   └── recognition.py   # Face recognition endpoints
│   └── schemas/
│       └── student.py       # Pydantic request/response models
├── main.py                  # FastAPI app initialization
├── requirements.txt         # Python dependencies
└── .env                     # Configuration file
```

## API Endpoints

### 1. Register Student
```
POST /api/face/register/
```
**Form Data:**
- `student_id` (string): Unique student ID (e.g., "S001")
- `name` (string): Student name
- `parent_email` (string): Parent email for notifications
- `file` (image): Student face image

**Response:**
```json
{
  "status": "success",
  "message": "Student registered successfully",
  "student_id": "S001"
}
```

### 2. Recognize Face (Entry/Exit)
```
POST /api/face/recognize/{event_type}?location=Main%20Gate
```
**Parameters:**
- `event_type`: "ENTRY" or "EXIT"
- `location` (optional): Location name (default: "Main Gate")

**Form Data:**
- `file` (image): Captured face image

**Response:**
```json
{
  "status": "Recognized",
  "student": "John Doe",
  "student_id": "S001",
  "event": "ENTRY",
  "parent_email": "parent@example.com",
  "timestamp": "2026-03-05T10:30:00"
}
```

### 3. Get All Students
```
GET /api/face/students/
```

**Response:**
```json
[
  {
    "student_id": "S001",
    "name": "John Doe",
    "parent_email": "parent@example.com",
    "status": "active",
    "image_path": "student_images/S001.jpg",
    "created_at": "2026-03-05T10:00:00"
  }
]
```

### 4. Get Campus Logs
```
GET /api/face/campus-logs/?student_id=S001&limit=50
```

**Query Parameters:**
- `student_id` (optional): Filter by student
- `limit` (optional): Number of logs (default: 50, max: 1000)

**Response:**
```json
{
  "total": 5,
  "logs": [
    {
      "id": 1,
      "student_id": "S001",
      "event_type": "ENTRY",
      "location": "Main Gate",
      "timestamp": "2026-03-05T09:00:00"
    }
  ]
}
```

### 5. Get Specific Student
```
GET /api/face/student/{student_id}
```

**Response:**
```json
{
  "student_id": "S001",
  "name": "John Doe",
  "parent_email": "parent@example.com",
  "status": "active",
  "image_path": "student_images/S001.jpg",
  "created_at": "2026-03-05T10:00:00"
}
```

### 6. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "app": "Face Recognition Campus Monitoring API",
  "version": "1.0.0"
}
```

### 7. Root
```
GET /
```

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Setting Up Your Flutter App

### 1. Update API Service

Replace your `lib/services/api_service.dart` with the provided `face_recognition_api_service.dart`

### 2. Configure Backend URL

In your Flutter app, update the base URL to point to your backend:

```dart
// For local development
static const String baseUrl = 'http://localhost:8000';

// For network access (replace with your Mini PC IP)
static const String baseUrl = 'http://192.168.1.100:8000';
```

### 3. Use in Your Flutter Screens

```dart
final apiService = FaceRecognitionApiService();

// Register a student
final result = await apiService.registerStudent(
  studentId: 'S001',
  name: 'John Doe',
  parentEmail: 'parent@example.com',
  imageFile: imageFile,
);

// Recognize a face
final recognition = await apiService.recognizeFace(
  imageFile: imageFile,
  eventType: 'ENTRY',
  location: 'Main Gate',
);

// Get all students
final students = await apiService.getAllStudents();

// Get campus logs
final logs = await apiService.getCampusLogs(studentId: 'S001');
```

## Running the Backend

### Windows (PowerShell)
```powershell
cd backend
.\run.bat
```

### Linux/Mac
```bash
cd backend
chmod +x run.sh
./run.sh
```

### Manual Start
```bash
cd backend
python -m venv venv_310
source venv_310/bin/activate  # On Windows: venv_310\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Database Setup

1. Ensure MySQL/XAMPP is running
2. Create database `face_attendance`:
   ```sql
   CREATE DATABASE face_attendance;
   ```
3. The tables will be created automatically on first run

## Important Configuration

### CORS Settings
The backend allows requests from:
- localhost:8000
- localhost:3000
- 127.0.0.1:3000
- 127.0.0.1:8000
- 192.168.1.100:8000 (Update with your Mini PC IP)
- All origins (*) - for development

### Update ALLOWED_ORIGINS
In `backend/app/core/config.py`:
```python
allowed_origins: List[str] = [
    "http://localhost:8000",
    "http://192.168.x.x:8000",  # Your Mini PC IP
    "*",
]
```

## Troubleshooting

### Database Connection Error
- Ensure MySQL is running
- Check database credentials in `.env`
- Verify database `face_attendance` exists

### TensorFlow Warning
- This is normal - the system uses mock embeddings for demonstration
- In production, configure TensorFlow properly

### Port 8000 Already in Use
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Next Steps

1. ✅ Backend is running
2. ✅ Database is configured
3. 📱 Integrate Flutter API service
4. 🎯 Update Flutter screens to use the new endpoints
5. 🚀 Deploy to Mini PC for network access
