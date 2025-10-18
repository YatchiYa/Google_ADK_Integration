#!/bin/bash

# Google ADK Multi-Agent FastAPI Server Startup Script

echo "🚀 Starting Google ADK Multi-Agent FastAPI Server..."

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
# Google ADK Configuration
GOOGLE_API_KEY=your_google_api_key_here

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration (optional)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database Configuration
DATABASE_URL=sqlite:///./google_adk.db

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging Configuration
LOG_LEVEL=INFO

# CORS Configuration
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_ENABLED=true
EOF
    echo "📝 Created .env file. Please update it with your API keys!"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Check if Google API key is set
if grep -q "your_google_api_key_here" .env; then
    echo "⚠️  WARNING: Please set your GOOGLE_API_KEY in the .env file!"
    echo "   You can get one from: https://console.cloud.google.com/"
fi

# Start the server
echo "🌟 Starting FastAPI server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📖 ReDoc Documentation: http://localhost:8000/redoc"
echo ""
echo "🔑 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

# Run the server with auto-reload
python main.py

echo "👋 Server stopped. Goodbye!"
