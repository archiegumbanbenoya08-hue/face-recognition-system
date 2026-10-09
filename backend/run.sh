#!/bin/bash

echo ""
echo "🚀 Face Recognition Campus Monitoring Backend"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
fi

echo "✅ Python found:"
python3 --version

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

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        cat > .env << EOF
APP_NAME=Face Recognition API
DATABASE_URL=mysql+mysql.connector://root:@localhost:3306/face_attendance
SECRET_KEY=your-secret-key-change-in-production
EOF
    fi
    echo "⚠️  Please update .env with your configuration"
fi

# Ensure MySQL is running
echo ""
echo "⚠️  Make sure MySQL is running before starting!"
echo ""

# Run the application
echo ""
echo "🎉 Starting FastAPI Server..."
echo "📍 API URL: http://localhost:8000"
echo "📖 Documentation: http://localhost:8000/docs"
echo ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
