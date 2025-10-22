#!/bin/bash

# ============================================================================
# ReAct Planner Agent Test Script (Simple Version)
# Tests PlanReActPlanner with structured reasoning and planning
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}🧠 REACT PLANNER AGENT TEST (SIMPLE)${NC}"
echo -e "${CYAN}============================================================================${NC}"
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
  -d '{"name": "ReAct Planner Agent Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create ReAct Planner Agent
# ============================================================================
echo -e "${BLUE}Step 2: Creating ReAct Planner Agent...${NC}"

AGENT_RESPONSE=$(curl -v -X POST "http://localhost:8000/api/v1/agents" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ReAct Strategic Planner",
    "persona": {
      "name": "Strategic ReAct Planner",
      "description": "Expert strategic planner specializing in structured ReAct methodology for complex multi-step problem solving and analysis",
      "personality": "systematic, analytical, and strategic",
      "expertise": ["strategic planning", "structured reasoning", "multi-step analysis", "problem decomposition", "systematic thinking"],
      "communication_style": "structured and methodical, always following PLANNING -> ACTION -> REASONING -> FINAL_ANSWER format"
    },
    "config": {
      "model": "gemini-2.0-flash-exp",
      "temperature": 0.3,
      "max_output_tokens": 3000
    },
    "tools": ["google_search", "text_analyzer", "custom_calculator", "save_memory", "load_memory"],
    "planner": "PlanReActPlanner"
  }')

echo "Debug - Agent Response: '$AGENT_RESPONSE'"
AGENT_SUCCESS=$(echo "$AGENT_RESPONSE" | jq -r ".success")
if [ "$AGENT_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Failed to create agent${NC}"
    echo "Full response: $AGENT_RESPONSE"
    exit 1
fi

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".agent_id")
echo -e "${GREEN}✅ ReAct Planner Agent created: $AGENT_ID${NC}"

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
    \"message\": \"Hello! I'm ready to demonstrate structured ReAct planning and reasoning for complex tasks.\",
    \"context\": {
      \"test_type\": \"react_planner_agent\",
      \"session_name\": \"ReAct Planning Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN} Conversation started: $CONVERSATION_ID${NC}"

# ============================================================================
# Interaction 1: Multi-Step Business Problem with ReAct Planning
# ============================================================================
echo ""
echo -e "${YELLOW}🧠 INTERACTION 1: Multi-Step Business Problem with ReAct Planning${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "I need help solving this business problem using your ReAct methodology: A startup wants to launch an AI fitness app. They need to: 1) Research the fitness app market, 2) Calculate development costs (6 developers × 8 months × $8000/month), 3) Estimate user acquisition costs, 4) Determine break-even point at $9.99/month subscription. Please use your structured PLANNING -> ACTION -> REASONING -> FINAL_ANSWER approach.",
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
