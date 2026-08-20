#!/bin/bash
# scripts/setup.sh

echo "🔧 Setting up XYZ AI - Complete Free Setup"
echo "=========================================="

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install AI Engine
echo "Installing AI Engine..."
cd ai-engine
pip install -r requirements.txt
cd ..

# Install Backend
echo "Installing Backend..."
cd backend
pip install -r requirements.txt
cd ..

# Install Frontend
echo "Installing Frontend..."
cd frontend
npm install
npm run build
cd ..

# Download models
echo "Downloading free AI models..."
python scripts/download_models.py

# Setup database
echo "Setting up database..."
python scripts/setup_database.py

# Create admin user
echo "Creating default users..."
python scripts/create_users.py

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  ./scripts/start.sh"