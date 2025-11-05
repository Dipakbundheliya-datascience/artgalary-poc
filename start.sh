#!/bin/bash

echo "========================================="
echo "Art Gallery Conversational AI Chatbot"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with your GEMINI_API_KEY"
    echo "You can copy .env.example and add your key:"
    echo "  cp .env.example .env"
    exit 1
fi

echo ""
echo "Starting backend server..."
echo "Backend URL: http://localhost:8000"
echo ""
echo "Open frontend/index.html in your browser"
echo "Or run: python -m http.server 3000 --directory frontend"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python app.py
