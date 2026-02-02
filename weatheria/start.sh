#!/bin/bash

# Weather App Quick Start Script
# This script helps you set up and run the weather app quickly

echo "================================================"
echo "Weather App - Quick Start Setup"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip"
    exit 1
fi

echo "✅ pip found"
echo ""

# Ask for API key
echo "📝 You need an OpenWeatherMap API key"
echo "Get one free at: https://openweathermap.org/api"
echo ""
read -p "Enter your OpenWeatherMap API key: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ API key cannot be empty"
    exit 1
fi

echo ""
echo "🔧 Setting up backend..."
cd weather-backend

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
OPENWEATHER_API_KEY=$API_KEY
FLASK_ENV=development
FLASK_DEBUG=True
EOF

echo "✅ Backend setup complete!"
echo ""

# Start backend in background
echo "🚀 Starting backend server..."
python3 app.py &
BACKEND_PID=$!

echo "Backend running on PID: $BACKEND_PID"
sleep 3

# Check if backend is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Backend is running successfully!"
else
    echo "⚠️  Backend might not be running properly"
fi

echo ""
echo "🌐 Starting frontend server..."
cd ../weather-frontend

# Start frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "Frontend running on PID: $FRONTEND_PID"
sleep 2

echo ""
echo "================================================"
echo "✅ Weather App is ready!"
echo "================================================"
echo ""
echo "🌐 Open your browser and go to:"
echo "   http://localhost:8080"
echo ""
echo "📡 Backend API is running at:"
echo "   http://localhost:5000"
echo ""
echo "To stop the servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or run: killall python3"
echo ""
echo "================================================"

# Keep script running
echo "Press Ctrl+C to stop all servers..."
wait
