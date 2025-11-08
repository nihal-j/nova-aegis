#!/bin/bash

# Aegis Development Server Launcher
# Runs both FastAPI backend and Streamlit frontend

set -e

echo "=========================================="
echo "🛡️  AEGIS DEVELOPMENT SERVER"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app/app.py" ]; then
    echo "❌ Error: app/app.py not found. Please run this script from the project root."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo -e "${BLUE}→${NC} Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}→${NC} Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file not found. Creating template..."
    echo "# Aegis Configuration" > .env
    echo "# DEMO_REPO=https://github.com/your-org/your-repo.git" >> .env
    echo "# AEGIS_WEBHOOK_URL=https://your-webhook-url.com" >> .env
    echo -e "${GREEN}✓${NC} .env template created (edit as needed)"
    echo ""
fi

# Kill any existing processes on these ports
echo -e "${BLUE}→${NC} Checking for existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
echo -e "${GREEN}✓${NC} Ports cleared"
echo ""

# Start backend
echo "=========================================="
echo -e "${GREEN}🚀 Starting FastAPI Backend${NC}"
echo "=========================================="
echo "Backend will be available at: http://127.0.0.1:8000"
echo "API docs at: http://127.0.0.1:8000/docs"
echo ""

uvicorn app.app:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "=========================================="
echo -e "${GREEN}🎨 Starting Streamlit Frontend${NC}"
echo "=========================================="
echo "Frontend will be available at: http://127.0.0.1:8501"
echo ""

streamlit run ui/ui.py --server.port 8501 --server.address 127.0.0.1 &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Aegis is running!${NC}"
echo "=========================================="
echo ""
echo -e "${GREEN}📍 Local URLs:${NC}"
echo "   UI:      http://127.0.0.1:8501"
echo "   API:     http://127.0.0.1:8000"
echo "   Docs:    http://127.0.0.1:8000/docs"
echo ""
echo -e "${GREEN}🔧 Quick Commands:${NC}"
echo "   Health:  curl http://127.0.0.1:8000/health"
echo "   Examples: bash scripts/curl-examples.sh"
echo ""
echo -e "${YELLOW}⏹️  To stop: Press Ctrl+C${NC}"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait for processes
wait

