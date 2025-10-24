#!/bin/bash

echo "🧪 Quick Test Script for Google ADK Agent API"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Create Session
echo -e "${BLUE}1. Creating session...${NC}"
curl -s -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"visit_count": 1}}' | jq '.'

echo ""
echo -e "${GREEN}✓ Session created${NC}"
echo ""

# Test 2: Run Agent (Streaming)
echo -e "${BLUE}2. Running agent with streaming...${NC}"
echo ""

curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [
        {"text": "Write a short article about AI in healthcare"}
      ]
    },
    "streaming": false
  }'

echo ""
echo ""
echo -e "${GREEN}✓ Test complete${NC}"
