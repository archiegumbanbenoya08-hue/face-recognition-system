@echo off
REM Face Recognition FastAPI Backend Setup and Run Script for Windows

echo.
echo 🚀 Face Recognition Campus Monitoring Backend
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv_310" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv_310
)

REM Activate virtual environment
echo.
echo 🔌 Activating virtual environment...
call venv_310\Scripts\activate.bat

REM Install/upgrade dependencies
echo.
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo.
    echo 📝 Creating .env file...
    copy .env.example .env 2>nul || (
        echo APP_NAME=Face Recognition API > .env
        echo DATABASE_URL=mysql+mysql.connector://root:@localhost:3306/face_attendance >> .env
        echo SECRET_KEY=your-secret-key-change-in-production >> .env
    )
    echo ⚠️  Please update .env with your configuration
)

REM Ensure MySQL and XAMPP are running
echo.
echo ⚠️  Make sure XAMPP (MySQL) is running before starting!
echo.

REM Run the application
echo.
echo 🎉 Starting FastAPI Server...
echo 📍 API URL: http://localhost:8000
echo 📖 Documentation: http://localhost:8000/docs
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
