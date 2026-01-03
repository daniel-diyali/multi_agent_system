#!/bin/bash

# Multi-Agent System Startup Script
echo "🤖 Starting Multi-Agent Customer Service System"
echo "================================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if OPENAI_API_KEY is set
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  Please set your OPENAI_API_KEY in .env file"
    echo "   Edit .env and replace 'your_openai_api_key_here' with your actual API key"
    exit 1
fi

echo "✅ Environment configured"

# Create data directories if they don't exist
mkdir -p data/chroma
mkdir -p data/sample_data/billing
mkdir -p data/sample_data/account

echo "✅ Data directories ready"

# Run system health check
echo "🔍 Running system health check..."
python3 test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Choose how to run the system:"
    echo "1. Streamlit UI (Interactive Demo)"
    echo "2. FastAPI Server (API Mode)"
    echo "3. Both (Recommended)"
    echo ""
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            echo "🎨 Starting Streamlit UI..."
            streamlit run ui/app.py
            ;;
        2)
            echo "🔧 Starting FastAPI server..."
            python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
            ;;
        3)
            echo "🚀 Starting both services..."
            echo "FastAPI will run on http://localhost:8000"
            echo "Streamlit will run on http://localhost:8501"
            echo ""
            # Start API in background
            python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
            API_PID=$!
            
            # Wait a moment for API to start
            sleep 3
            
            # Start Streamlit
            streamlit run ui/app.py
            
            # Kill API when Streamlit exits
            kill $API_PID 2>/dev/null
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
else
    echo "❌ System health check failed. Please fix issues before running."
    exit 1
fi