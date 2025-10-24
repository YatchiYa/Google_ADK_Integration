#!/bin/bash

# =====================================================
# Google ADK Agent Testing Commands
# =====================================================

echo "🧪 Google ADK Agent Testing Commands"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =====================================================
# 1. List Available Apps
# =====================================================
echo -e "${BLUE}1. List Available Apps${NC}"
echo "curl -X GET http://localhost:8000/list-apps"
echo ""

# =====================================================
# 2. Create a Session
# =====================================================
echo -e "${BLUE}2. Create a Session${NC}"
echo 'curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '"'"'{"state": {"visit_count": 1}}'"'"
echo ""

# =====================================================
# 3. Get Session Details
# =====================================================
echo -e "${BLUE}3. Get Session Details${NC}"
echo "curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123"
echo ""

# =====================================================
# 4. Run Agent (Single Response)
# =====================================================
echo -e "${BLUE}4. Run Agent - Single Response${NC}"
echo 'curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [
        {"text": "Write an article about artificial intelligence trends in 2024"}
      ]
    }
  }'"'"
echo ""

# =====================================================
# 5. Run Agent (Streaming - No Token Streaming)
# =====================================================
echo -e "${BLUE}5. Run Agent - Streaming (Event-based)${NC}"
echo 'curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [
        {"text": "Write an article about quantum computing breakthroughs"}
      ]
    },
    "streaming": false
  }'"'"
echo ""

# =====================================================
# 6. Run Agent (Token-level Streaming)
# =====================================================
echo -e "${BLUE}6. Run Agent - Token-level Streaming${NC}"
echo 'curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '"'"'{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [
        {"text": "Write an article about renewable energy innovations"}
      ]
    },
    "streaming": true
  }'"'"
echo ""

# =====================================================
# 7. Delete Session
# =====================================================
echo -e "${BLUE}7. Delete Session${NC}"
echo "curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123"
echo ""

# =====================================================
# Quick Test Examples
# =====================================================
echo -e "${YELLOW}Quick Test Topics:${NC}"
echo "- Artificial Intelligence trends"
echo "- Quantum computing breakthroughs"
echo "- Climate change solutions"
echo "- Space exploration updates"
echo "- Blockchain technology developments"
echo "- Renewable energy innovations"
echo ""

echo -e "${GREEN}✅ Commands ready! Start the server with:${NC}"
echo "python server.py"
echo ""
echo -e "${GREEN}📚 Or view interactive docs at:${NC}"
echo "http://localhost:8000/docs"
