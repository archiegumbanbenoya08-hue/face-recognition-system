# 🎓 Campus Face Recognition System - Complete Startup Guide

## Overview
A full-stack face recognition system with Mini PC client, Node.js backend, and React frontend dashboards for monitoring student entry/exit at campus gates.

## 📋 System Architecture

```
┌─────────────────────────────────────┐
│    Mini PC Client (Python)          │
│  - OpenCV + Face Recognition        │
│  - Detects students at gate         │
│  - Sends logs to backend            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Backend API (Node.js/Express)      │
│  - Authentication (JWT)             │
│  - Student management               │
│  - Email notifications              │
│  - Log storage                      │
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌──────────────┐  ┌──────────────┐
│Admin Panel   │  │Parent Portal │
│(React)       │  │ (React)      │
└──────────────┘  └──────────────┘
```

## ⚙️ Step 1: Install Dependencies

### Windows
1. **Node.js** (for backend & frontend)
   - Download: https://nodejs.org/
   - Or: `winget install OpenJS.NodeJS`

2. **Python 3.8+** (for Mini PC client)
   - Download: https://www.python.org/
   - Or: `winget install Python.Python.3.11`

3. **MySQL Server**
   - Download: https://dev.mysql.com/downloads/mysql/
   - Or: `winget install MySQL.MySQL`
   - Create user and remember password

### Linux (Ubuntu/Debian)
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python
sudo apt install -y python3 python3-pip

# Install MySQL
sudo apt install -y mysql-server

# Install face recognition dependencies
sudo apt install -y cmake build-essential libgtk-3-dev libboost-all-dev
```

## 📁 Step 2: Set Up Database

Run the database setup script:
```bash
# Windows
SETUP_DATABASE.bat

# Linux
mysql -u root -p face_recognition_system < backend/database_schema.sql
```

**When prompted:**
- Enter your MySQL root password
- Database will be created automatically
- Default admin: `admin@campus.com` / `admin123`
- Default parents: `navarro@gmail.com` / `parent123`

## 🔧 Step 3: Configure Backend

1. Edit `backend-node/.env`:
```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
JWT_SECRET=change_this_to_random_string
DEVICE_API_KEY=change_this_to_random_string
GMAIL_USER=your_email@gmail.com
GMAIL_PASS=your_app_password
FRONTEND_URL=http://localhost:5173
```

2. **Gmail Setup** (for notifications):
   - Enable 2-Factor Authentication: https://myaccount.google.com/
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Copy the 16-character password to `GMAIL_PASS`

## 🚀 Step 4: Start the System

### Option A: Automated Startup (Windows)
```bash
START_SYSTEM.bat
```
This opens 2 terminals automatically.

### Option B: Manual Startup

**Terminal 1: Backend Server**
```bash
cd backend-node
npm install  # First time only
npm start
# Runs on http://localhost:8000
```

**Terminal 2: Frontend (React)**
```bash
cd frontend
npm install  # First time only
npm run dev
# Opens http://localhost:5173
```

**Terminal 3: Mini PC Client** (on the Mini PC device)
```bash
cd mini_pc_client
pip install face-recognition opencv-python requests numpy
python campus_face_recognition.py
```

## 🔑 Step 5: Access the System

### Admin Dashboard
- **URL:** http://localhost:5173
- **Role:** Admin
- **Email:** admin@campus.com
- **Password:** admin123

**Features:**
- View all registered students
- Register new students with photos
- Edit/delete student records
- View entry/exit logs with filters
- Real-time dashboard overview

### Parent Portal
- **URL:** http://localhost:5173
- **Role:** Parent
- **Email:** navarro@gmail.com
- **Password:** parent123

**Features:**
- View my children's campus status
- Check activity logs
- Track last seen time

## 📸 Step 6: Add Students

### Using Admin Dashboard
1. Go to "Students" section
2. Click "Add Student"
3. Fill in:
   - Student ID (unique)
   - First/Last Name
   - Grade Level
   - Section
   - Parent (select from dropdown)
   - Upload photo
4. Click Save

### Using Registration Script (Optional)
Place student photos in `student_images/` folder and run:
```bash
cd backend
python register_students.py
```

## 👁️ Step 7: Test Face Recognition

### On Mini PC
```bash
python mini_pc_client/campus_face_recognition.py
```

**What happens:**
1. Fetches all student face encodings from backend
2. Captures video from webcam
3. Detects faces in real-time
4. Matches against known students (tolerance: 0.5)
5. Determines ENTRY or EXIT based on last log
6. Sends log to backend
7. Backend sends emails to parent & admin
8. Student name and action appear on screen

### On Admin Dashboard
- Check "Dashboard" to see recent activity
- Go to "Logs" to filter entries/exits
- Monitor students in/out of campus

### On Parent Dashboard
- Go to "My Children" to see current status
- Check "Activity Logs" for detailed history

## 🐛 Troubleshooting

### Connection Issues
```
ERROR: Connection to http://localhost:8000
→ Make sure backend is running: npm start in backend-node
```

### Database Connection
```
ERROR: ER_ACCESS_DENIED_FOR_USER
→ Check DB_USER/DB_PASSWORD in .env matches MySQL setup
```

### Face Recognition Not Working
```
No faces detected
→ Ensure good lighting
→ Position camera at eye level
→ Adjust TOLERANCE in mini_pc_client/campus_face_recognition.py
```

### Emails Not Sending
```
ERROR: Invalid login credentials
→ Verify GMAIL_USER and GMAIL_PASS in .env
→ Use 16-character App Password, not regular password
→ Enable 2FA on Gmail account
```

## 📊 API Documentation

### Authentication
- `POST /api/auth/admin/login` - Admin login
- `POST /api/auth/parent/login` - Parent login

### Students
- `GET /api/students` - List all (admin only)
- `POST /api/students` - Register (admin only)
- `PUT /api/students/:id` - Update (admin only)
- `DELETE /api/students/:id` - Deactivate (admin only)
- `GET /api/students/encodings` - Get face encodings (device key)

### Logs
- `POST /api/logs` - Record entry/exit (device key)
- `GET /api/logs/last/:studentId` - Last event (device key)
- `GET /api/logs/admin` - All logs (admin only)
- `GET /api/logs/parent/:parentId` - Children logs (parent only)

## 🔒 Security Notes

- Change default passwords after first login
- Generate strong JWT_SECRET and DEVICE_API_KEY
- Use HTTPS in production
- Store .env file securely
- Regularly update dependencies

## 📱 File Structure

```
.
├── backend/                 # Original backend (database schema)
├── backend-node/           # Node.js REST API
│   ├── routes/            # API routes
│   ├── middleware/        # Auth middleware
│   ├── server.js          # Main server
│   └── .env               # Configuration
├── frontend/              # React dashboard
│   ├── src/
│   │   ├── components/    # React components
│   │   └── App.jsx        # Main app
│   └── package.json
├── mini_pc_client/        # Face recognition client
│   └── campus_face_recognition.py
├── START_SYSTEM.bat       # Quick start
└── QUICK_START.md         # This file
```

## 🆘 Support

For issues:
1. Check the console output for error messages
2. Review the .env configuration
3. Verify all services are running
4. Check database credentials

Happy monitoring! 🎓✨
