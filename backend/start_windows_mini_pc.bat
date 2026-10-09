@echo off
echo Starting Mini PC Face Recognition System...
echo ===========================================
echo.

REM Check if we're in the backend directory
if not exist "main.py" (
    echo Error: Please run this script from the backend directory
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv_310" (
    echo Creating virtual environment...
    python -m venv venv_310
)

REM Activate virtual environment
echo Activating virtual environment...
call venv_310\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check database connection
echo Checking database...
python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='face_attendance'
    )
    conn.close()
    print('Database OK')
except Exception as e:
    print(f'Database error: {e}')
    echo Please ensure XAMPP MySQL is running and database 'face_attendance' exists
    pause
    exit /b 1
"

REM Ensure database tables exist
echo Setting up database tables...
python setup_db.py

REM Start backend in background
echo Starting FastAPI backend...
start /B python -m uvicorn main:app --host 127.0.0.1 --port 8000

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Check if backend is running
curl -s http://127.0.0.1:8000/health > nul 2>&1
if errorlevel 1 (
    echo Backend failed to start
    pause
    exit /b 1
)

echo Backend running on http://127.0.0.1:8000
echo.

REM Start face recognition monitor
echo Starting face recognition monitor...
echo Press Ctrl+C to stop the system
echo.

python mini_pc_monitor.py

REM Cleanup
echo.
echo Shutting down...
taskkill /f /im python.exe > nul 2>&1
echo System stopped