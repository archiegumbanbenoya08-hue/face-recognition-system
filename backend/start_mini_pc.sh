#!/bin/bash

echo ""
echo "🚀 Mini PC Face Recognition System Startup"
echo "=========================================="
echo ""

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is designed for Linux mini PCs"
    echo "For Windows setup, see QUICK_START_MASTER_GUIDE.md"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Install with: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "✅ Python 3 found:"
python3 --version

# Check if MySQL is running (assuming local MySQL)
if ! pgrep mysqld > /dev/null && ! pgrep mariadbd > /dev/null; then
    echo "⚠️  MySQL/MariaDB not running"
    echo "Start with: sudo systemctl start mysql"
    echo "Or install: sudo apt install mysql-server"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ MySQL/MariaDB is running"
fi

# Go to backend directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv_310" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv_310
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv_310/bin/activate

# Install/upgrade dependencies
echo ""
echo "📥 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Check if database exists
echo ""
echo "🗄️  Checking database..."
python3 -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='face_attendance'
    )
    conn.close()
    print('✅ Database face_attendance exists')
except mysql.connector.Error as e:
    print(f'❌ Database error: {e}')
    print('Create database with: mysql -u root -p -e \"CREATE DATABASE face_attendance;\"')
    print('Then run setup_db.py')
    exit(1)
"

# Create tables if needed
echo ""
echo "📋 Ensuring database tables exist..."
python3 setup_db.py

# Start backend in background
echo ""
echo "🚀 Starting FastAPI backend..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend running on http://localhost:8000"
echo ""

# Start face recognition monitor
echo "📹 Starting face recognition monitor..."
echo "Press Ctrl+C to stop the system"
echo ""

python3 mini_pc_monitor.py

# Cleanup
echo ""
echo "🛑 Shutting down..."
kill $BACKEND_PID 2>/dev/null
echo "✅ System stopped"