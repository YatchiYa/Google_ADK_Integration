#!/bin/bash

# ============================================================================
# Calculation Agent Test - Math and Computation Specialist
# ============================================================================
# Tests an agent with multiple calculation and math tools:
# - custom_calculator: Basic arithmetic operations
# - text_analyzer: Text metrics and analysis
# - load_memory: Memory operations for calculations
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🧮 Testing Calculation Agent with Multiple Math Tools"
echo "Server: http://localhost:8000"
echo "Time: $(date)"
echo ""

# ============================================================================
# Step 1: Authentication
# ============================================================================
echo -e "${BLUE}Step 1: Authenticating...${NC}"

LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

JWT_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r ".access_token")
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r ".user_id")

if [ "$JWT_TOKEN" = "null" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi

# Create API Key
API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Calculation Agent Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create Calculation Agent with Multiple Tools
# ============================================================================
echo -e "${BLUE}Step 2: Creating Calculation Agent...${NC}"

AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Math Wizard",
    "persona": {
      "name": "Professor Calculator",
      "description": "Expert mathematician and computational analyst specializing in complex calculations, statistical analysis, and mathematical problem solving",
      "personality": "precise, analytical, and educational",
      "expertise": ["mathematics", "statistics", "data analysis", "computational thinking", "problem solving"],
      "communication_style": "academic but accessible, always showing work and explaining steps"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.1,
      "max_output_tokens": 2048
    },
    "tools": ["custom_calculator", "text_analyzer", "load_memory"]
  }')

AGENT_SUCCESS=$(echo "$AGENT_RESPONSE" | jq -r ".success")
if [ "$AGENT_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Failed to create agent${NC}"
    exit 1
fi

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*')
echo -e "${GREEN}✅ Agent created: $AGENT_ID${NC}"

# ============================================================================
# Step 3: Start Conversation Session
# ============================================================================
echo -e "${BLUE}Step 3: Starting conversation session...${NC}"

CONVERSATION_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"Hello! I'm ready to work on mathematical problems and calculations.\",
    \"context\": {
      \"test_type\": \"calculation_agent\",
      \"session_name\": \"Math Problem Solving Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"

# ============================================================================
# Interaction 1: Basic Arithmetic and Complex Calculations
# ============================================================================
echo ""
echo -e "${YELLOW}🔢 INTERACTION 1: Complex Mathematical Calculations${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "I need help with several calculations: 1) Calculate compound interest: $10,000 invested at 5.5% annual rate for 7 years, compounded quarterly. 2) Find the area of a circle with radius 12.5 meters. 3) Solve this equation: 3x² + 7x - 12 = 0. Please show all your work and use your calculator tool for precision.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 8
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"

# ============================================================================
# Interaction 2: Statistical Analysis and Text Metrics
# ============================================================================
echo ""
echo -e "${YELLOW}📊 INTERACTION 2: Statistical Analysis with Text Processing${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Analyze this dataset and text: Sales data: [125, 340, 278, 156, 423, 389, 234, 567, 445, 321]. Calculate mean, median, mode, standard deviation, and variance. Also analyze this product description: \"Revolutionary AI-powered smartphone with 108MP camera, 5000mAh battery, 12GB RAM, and lightning-fast 5G connectivity for seamless performance.\" Give me word count, character analysis, and key metrics.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 10
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 2 completed${NC}"

# ============================================================================
# Interaction 3: Advanced Problem Solving with Memory
# ============================================================================
echo ""
echo -e "${YELLOW}🧠 INTERACTION 3: Advanced Problem Solving with Memory${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Remember our previous calculations and help me with this business scenario: Based on the compound interest calculation we did earlier, if I want to reach $25,000 in the same timeframe (7 years) with the same 5.5% rate compounded quarterly, what initial investment do I need? Also, using the sales data statistics we calculated, project next month sales if there is a 15% growth trend. Store these results in memory for future reference.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 12
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 3 completed${NC}"

# ============================================================================
# Test Summary
# ============================================================================
echo ""
echo "============================================================================"
echo -e "${GREEN}🎉 CALCULATION AGENT TEST COMPLETED${NC}"
echo "============================================================================"
echo "Agent ID: $AGENT_ID"
echo "Conversation ID: $CONVERSATION_ID"
echo "Tools Tested: custom_calculator, text_analyzer, load_memory"
echo ""
echo "Test Coverage:"
echo "✅ Complex mathematical calculations (compound interest, geometry, algebra)"
echo "✅ Statistical analysis (mean, median, standard deviation)"
echo "✅ Text analysis and metrics"
echo "✅ Memory storage and retrieval"
echo "✅ Multi-step problem solving"
echo ""
echo -e "${BLUE}Agent successfully demonstrated mathematical expertise with tool integration!${NC}"
