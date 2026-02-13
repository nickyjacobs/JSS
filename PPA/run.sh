#!/bin/bash

# Password Policy Analyzer - Startup Script

echo "🔒 Starting Password Policy Analyzer..."
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

# Start the application
echo ""
echo "🚀 Starting Flask application..."
echo "📱 Open your browser to: http://localhost:5500"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
