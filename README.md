# Student Campus Entry/Exit Monitoring System

A complete face recognition system for monitoring student entry and exit at campus gates using a Mini PC, with web dashboards for administrators and parents.

## System Overview

- **Mini PC Client**: Python script running face recognition at the campus gate
- **Backend API**: Node.js REST API with authentication and email notifications
- **Frontend**: React web application with Admin and Parent dashboards
- **Database**: MySQL with proper relationships

## Features

- Real-time face recognition using face_recognition library
- Automatic entry/exit detection based on last log
- Email notifications to parents and admins
- Role-based access control (Admin/Parent)
- Comprehensive logging and reporting
- Responsive web dashboards

## Setup Instructions

### 1. Database Setup

1. Install MySQL and create database:
```bash
mysql -u root -p
CREATE DATABASE face_recognition_system;
exit;
```

2. Run the schema:
```bash
mysql -u root face_recognition_system < backend-node/database_schema.sql
```

### 2. Backend Setup

1. Navigate to backend directory:
```bash
cd backend-node
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables in `.env`:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=face_recognition_system
JWT_SECRET=your_jwt_secret_key_here
DEVICE_API_KEY=your_device_api_key_here
GMAIL_USER=your_gmail@gmail.com
GMAIL_PASS=your_app_password
FRONTEND_URL=http://localhost:3000
```

4. Start the backend:
```bash
npm start
```

### 3. Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

### 4. Mini PC Client Setup

1. Install Python dependencies on your Mini PC:
```bash
pip install face-recognition opencv-python requests numpy
```

2. Install system dependencies (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y cmake build-essential libgtk-3-dev libboost-all-dev
```

3. For dlib compilation (may take time):
```bash
pip install dlib
```

4. Update the script configuration:
   - Change `BACKEND_URL` to your backend server URL
   - Set `DEVICE_API_KEY` to match your backend `.env`

5. Run the client:
```bash
python campus_face_recognition.py
```

### 5. Gmail Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
3. Use the App Password in `GMAIL_PASS` (not your regular password)

### 6. Seed Initial Data

1. Hash the admin password:
```bash
node -e "const bcrypt = require('bcrypt'); bcrypt.hash('admin123', 10).then(h => console.log(h));"
```

2. Update the database with hashed password:
```sql
UPDATE admin SET password = 'hashed_password_here' WHERE email = 'admin@campus.com';
UPDATE parent SET password = 'hashed_password_here' WHERE email = 'navarro@gmail.com';
-- Repeat for other parents
```

3. Register student face encodings by running the registration script from the existing Python backend.

## Usage

1. **Admin Login**: Use `admin@campus.com` / `admin123`
2. **Parent Login**: Use parent emails like `navarro@gmail.com` / `parent123`
3. **Mini PC**: Run the Python script to start face recognition
4. **Access Web App**: Open http://localhost:3000

## API Endpoints

### Authentication
- `POST /api/auth/admin/login` - Admin login
- `POST /api/auth/parent/login` - Parent login

### Students (Admin only)
- `GET /api/students` - Get all students with status
- `POST /api/students` - Register new student
- `PUT /api/students/:id` - Update student
- `DELETE /api/students/:id` - Deactivate student
- `GET /api/students/encodings` - Get face encodings (device key required)

### Logs
- `POST /api/logs` - Record entry/exit (device key required)
- `GET /api/logs/last/:studentId` - Get last log (device key required)
- `GET /api/logs/admin` - Get all logs (admin only)
- `GET /api/logs/parent/:parentId` - Get parent's children logs (parent only)

## Troubleshooting

### Face Recognition Issues
- Ensure good lighting at the camera location
- Position camera at eye level
- Adjust `TOLERANCE` value if needed (lower = stricter matching)

### Email Not Sending
- Verify Gmail App Password is correct
- Check Gmail account security settings
- Ensure "Less secure app access" is enabled if not using App Password

### Database Connection
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database and tables exist

### Camera Issues
- Test camera with `cv2.VideoCapture(0)`
- Check camera permissions on Mini PC
- Try different camera index if multiple cameras

## Security Notes

- Change default passwords after setup
- Use HTTPS in production
- Store JWT secrets securely
- Limit device API key access
- Regularly update dependencies

## License

This project is for educational purposes.