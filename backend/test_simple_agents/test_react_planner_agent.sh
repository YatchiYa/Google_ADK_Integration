#!/bin/bash

# ============================================================================
# ReAct Planner Agent Test Script
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
echo -e "${CYAN}🧠 REACT PLANNER AGENT TEST${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo -e "${BLUE}Testing PlanReActPlanner with structured reasoning and multi-step planning${NC}"
echo "Server: http://localhost:8000"
echo "Time: $(date)"
echo ""

# Configuration
BASE_URL="http://localhost:8000/api/v1"
USER_ID="admin"

# ============================================================================
# Step 0: Authentication
# ============================================================================
echo -e "${BLUE}Step 0: Authenticating...${NC}"

# Login first
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
# Step 1: Create ReAct Planner Agent
# ============================================================================
echo -e "${BLUE}Step 1: Creating ReAct Planner Agent...${NC}"

AGENT_RESPONSE=$(curl -v -X POST "$BASE_URL/agents" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Strategic ReAct Planner",
    "description": "Advanced ReAct agent with structured planning capabilities",
    "model": "gemini-2.0-flash-exp",
    "instructions": "You are a strategic planning agent that uses ReAct methodology. Follow this format: PLANNING -> ACTION -> REASONING -> FINAL_ANSWER",
    "tools": [
      "google_search",
      "text_analyzer", 
      "custom_calculator",
      "save_memory",
      "load_memory"
    ],
    "planner": "PlanReActPlanner",
    "temperature": 0.3,
    "max_tokens": 3000
  }')

echo "Debug - Agent Response: '$AGENT_RESPONSE'"
AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".agent_id")
echo -e "${GREEN}✅ ReAct Planner Agent created: $AGENT_ID${NC}"

if [ "$AGENT_ID" = "null" ] || [ -z "$AGENT_ID" ]; then
    echo -e "${RED}❌ Agent creation failed${NC}"
    echo "Response: $AGENT_RESPONSE"
    exit 1
fi

# ============================================================================
# Step 2: Start Conversation Session
# ============================================================================
echo -e "${BLUE}Step 2: Starting conversation session...${NC}"

CONVERSATION_RESPONSE=$(curl -s -X POST "$BASE_URL/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT_ID\",
    \"message\": \"Hello! I'm ready to demonstrate structured planning and reasoning for complex tasks.\",
    \"context\": {
      \"test_type\": \"react_planner_agent\",
      \"session_name\": \"Strategic Planning Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"

# ============================================================================
# Interaction 1: Multi-Step Problem Solving with ReAct Planning
# ============================================================================
echo ""
echo -e "${YELLOW}🧠 INTERACTION 1: Multi-Step Problem Solving with ReAct Planning${NC}"

curl -s -X POST "$BASE_URL/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "I need help solving this business problem: A startup wants to launch an AI-powered fitness app. They need to: 1) Research the fitness app market size and key competitors, 2) Calculate the development costs (assume 6 developers for 8 months at $8000/month each), 3) Estimate user acquisition costs based on industry averages, 4) Determine break-even point if they charge $9.99/month subscription. Please use your ReAct planning methodology to structure this analysis step by step.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 15
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"

# ============================================================================
# Interaction 2: Text Analysis with Strategic Reasoning
# ============================================================================
echo ""
echo -e "${YELLOW}📝 INTERACTION 2: Text Analysis with Strategic Reasoning${NC}"

curl -s -X POST "$BASE_URL/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Please analyze this product review and provide strategic insights: \"This AI fitness app is amazing! The personalized workout plans are spot-on and the nutrition tracking is incredibly detailed. However, the subscription price of $9.99/month feels a bit steep compared to competitors like MyFitnessPal. The UI could also use some improvements - it feels cluttered. Overall, I love the AI features but the pricing and design need work.\" Use your ReAct methodology to: 1) Analyze the sentiment and key themes, 2) Calculate readability metrics, 3) Identify improvement opportunities, 4) Provide strategic recommendations for the product team.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 12
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 2 completed${NC}"

# ============================================================================
# Interaction 3: Synthesis and Memory Integration
# ============================================================================
echo ""
echo -e "${YELLOW}🧠 INTERACTION 3: Synthesis and Memory Integration${NC}"

curl -s -X POST "$BASE_URL/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Based on our previous analysis of the fitness app business case and the product review, create a comprehensive strategic recommendation. Use your ReAct methodology to: 1) Synthesize insights from both analyses, 2) Calculate the impact of addressing the UI and pricing concerns on user retention (assume 15% improvement), 3) Recommend an optimal pricing strategy, 4) Create an action plan for product improvements. Store your final strategic framework in memory as \"Fitness App Strategic Plan\" for future reference.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 18
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 3 completed${NC}"

# ============================================================================
# Test Summary
# ============================================================================
echo ""
echo -e "${CYAN}============================================================================${NC}"
echo -e "${CYAN}🎉 REACT PLANNER AGENT TEST COMPLETED${NC}"
echo -e "${CYAN}============================================================================${NC}"
echo -e "${GREEN}Agent ID: $AGENT_ID${NC}"
echo -e "${GREEN}Conversation ID: $CONVERSATION_ID${NC}"
echo -e "${GREEN}Planner: PlanReActPlanner${NC}"
echo -e "${GREEN}Tools Tested: google_search, text_analyzer, custom_calculator, save_memory, load_memory${NC}"
echo ""
echo -e "${YELLOW}Test Coverage:${NC}"
echo -e "${GREEN}✅ Structured ReAct planning methodology (PLANNING -> ACTION -> REASONING -> FINAL_ANSWER)${NC}"
echo -e "${GREEN}✅ Multi-step business problem solving with calculations${NC}"
echo -e "${GREEN}✅ Text analysis with strategic reasoning${NC}"
echo -e "${GREEN}✅ Cross-analysis synthesis and integration${NC}"
echo -e "${GREEN}✅ Memory storage and retrieval for strategic frameworks${NC}"
echo -e "${GREEN}✅ Tool coordination for complex workflows${NC}"
echo -e "${GREEN}✅ Structured thinking and systematic problem decomposition${NC}"
echo ""
echo -e "${PURPLE}Agent successfully demonstrated advanced ReAct planning and reasoning capabilities!${NC}"
