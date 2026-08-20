#!/bin/bash
# scripts/deploy-free.sh

echo "🚀 Deploying XYZ AI with $0 Budget"
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check requirements
echo -e "${YELLOW}Checking requirements...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python 3.x installed${NC}"
else
    echo -e "${RED}❌ Python 3.x not found${NC}"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    echo -e "${GREEN}✅ Node.js installed${NC}"
else
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${YELLOW}⚠️  Docker not found - will use local deployment${NC}"
fi

# Install Python dependencies
echo -e "${YELLOW}Installing AI Engine dependencies...${NC}"
cd ai-engine
pip install -r requirements.txt --quiet
cd ..

# Install Backend dependencies
echo -e "${YELLOW}Installing Backend dependencies...${NC}"
cd backend
pip install -r requirements.txt --quiet
cd ..

# Install Frontend dependencies
echo -e "${YELLOW}Installing Frontend dependencies...${NC}"
cd frontend
npm install --silent
cd ..

# Download Vosk models (free)
echo -e "${YELLOW}Downloading Vosk models...${NC}"
mkdir -p ai-engine/models/vosk

# English model
if [ ! -d "ai-engine/models/vosk/vosk-model-small-en-us-0.15" ]; then
    echo "Downloading English STT model..."
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip -q vosk-model-small-en-us-0.15.zip -d ai-engine/models/vosk/
    rm vosk-model-small-en-us-0.15.zip
fi

# Hindi model
if [ ! -d "ai-engine/models/vosk/vosk-model-small-hi-0.22" ]; then
    echo "Downloading Hindi STT model..."
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip
    unzip -q vosk-model-small-hi-0.22.zip -d ai-engine/models/vosk/
    rm vosk-model-small-hi-0.22.zip
fi

# Setup environment
echo -e "${YELLOW}Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file${NC}"
fi

# Start services
echo -e "${GREEN}Starting XYZ AI services...${NC}"

# Start AI Engine
echo "Starting AI Engine on port 8000..."
cd ai-engine
python src/main.py &
AI_PID=$!
cd ..

# Start Backend
echo "Starting Backend on port 3000..."
cd backend
python src/main.py &
BACKEND_PID=$!
cd ..

# Start Frontend
echo "Starting Frontend on port 8080..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ XYZ AI is running!${NC}"
echo -e "${GREEN}================================${NC}"
echo "AI Engine: http://localhost:8000"
echo "Backend:   http://localhost:3000"
echo "Frontend:  http://localhost:8080"
echo ""
echo "Total Cost: $0"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap for cleanup
trap "kill $AI_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

# Wait for services
wait