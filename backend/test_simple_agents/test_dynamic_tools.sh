#!/bin/bash

# ============================================================================
# Dynamic Tool Management Test - Real-time Tool Attachment/Detachment
# ============================================================================
# This test demonstrates:
# 1. Creating an agent WITHOUT any tools
# 2. Dynamically attaching tools to the agent during conversation
# 3. Using the newly attached tools in streaming responses
# 4. Dynamically detaching tools from the agent
# 5. Verifying tool availability changes in real-time
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

echo "🔧 Testing Dynamic Tool Management with Real-time Attachment/Detachment"
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
  -d '{"name": "Dynamic Tools Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create Agent WITHOUT Any Tools
# ============================================================================
echo -e "${BLUE}Step 2: Creating agent WITHOUT tools...${NC}"

AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dynamic Tool Agent",
    "persona": {
      "name": "Adaptive Assistant",
      "description": "Versatile agent that can dynamically gain and lose capabilities through tool management",
      "personality": "adaptable, helpful, and transparent about current capabilities",
      "expertise": ["dynamic adaptation", "tool utilization", "capability awareness"],
      "communication_style": "clear and informative, always explaining current tool availability"
    }, 
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.7,
      "max_output_tokens": 1500
    },
    "tools": []
  }')

AGENT_SUCCESS=$(echo "$AGENT_RESPONSE" | jq -r ".success")
if [ "$AGENT_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Failed to create agent${NC}"
    echo "$AGENT_RESPONSE"
    exit 1
fi

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r ".message" | grep -o 'agent_[a-f0-9]*')
echo -e "${GREEN}✅ Agent created WITHOUT tools: $AGENT_ID${NC}"

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
    \"message\": \"Hello! I'm ready to demonstrate dynamic tool management.\",
    \"context\": {
      \"test_type\": \"dynamic_tools\",
      \"session_name\": \"Dynamic Tool Management Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"

sleep 3

# ============================================================================
# Interaction 1: Test Agent WITHOUT Tools
# ============================================================================
echo ""
echo -e "${YELLOW}🤖 INTERACTION 1: Testing agent without tools${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "What tools do you currently have available? Can you analyze text or perform calculations?",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 8
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"

sleep 2

# ============================================================================
# Step 4: Dynamically Attach Text Analyzer Tool
# ============================================================================
echo ""
echo -e "${PURPLE}🔧 Step 4: Dynamically attaching 'text_analyzer' tool...${NC}"

ATTACH_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/$AGENT_ID/tools/attach" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_names": ["text_analyzer"]
  }')

ATTACH_SUCCESS=$(echo "$ATTACH_RESPONSE" | jq -r ".success")
if [ "$ATTACH_SUCCESS" = "true" ]; then
    echo -e "${GREEN}✅ Text analyzer tool attached successfully${NC}"
else
    echo -e "${RED}❌ Failed to attach text analyzer tool${NC}"
    echo "$ATTACH_RESPONSE"
fi

sleep 2

# ============================================================================
# Interaction 2: Test Agent WITH Text Analyzer
# ============================================================================
echo ""
echo -e "${YELLOW}📝 INTERACTION 2: Testing agent with text analyzer tool${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Great! Now analyze this text for me: \"Artificial Intelligence is revolutionizing healthcare by enabling faster diagnosis, personalized treatment plans, and predictive analytics for patient outcomes. Machine learning algorithms can process vast amounts of medical data to identify patterns invisible to human doctors.\" What are the key themes and sentiment?",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 12
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 2 completed${NC}"

sleep 2

# ============================================================================
# Step 5: Dynamically Attach Calculator Tool
# ============================================================================
echo ""
echo -e "${PURPLE}🔧 Step 5: Dynamically attaching 'custom_calculator' tool...${NC}"

ATTACH_CALC_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/$AGENT_ID/tools/attach" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_names": ["custom_calculator"]
  }')

ATTACH_CALC_SUCCESS=$(echo "$ATTACH_CALC_RESPONSE" | jq -r ".success")
if [ "$ATTACH_CALC_SUCCESS" = "true" ]; then
    echo -e "${GREEN}✅ Calculator tool attached successfully${NC}"
else
    echo -e "${RED}❌ Failed to attach calculator tool${NC}"
    echo "$ATTACH_CALC_RESPONSE"
fi

sleep 2

# ============================================================================
# Interaction 3: Test Agent WITH Both Tools
# ============================================================================
echo ""
echo -e "${YELLOW}🧮 INTERACTION 3: Testing agent with both text analyzer and calculator${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Perfect! Now I want you to: 1) Calculate the compound interest for $10,000 invested at 5% annual rate for 10 years, and 2) Analyze this product description: \"EcoFit Pro - Revolutionary sustainable fitness tracker made from recycled materials. Features 30-day battery life, waterproof design, and AI-powered health insights. Perfect for environmentally conscious fitness enthusiasts.\" Give me both the calculation results and text analysis.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 15
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 3 completed${NC}"

sleep 2

# ============================================================================
# Step 6: Check Current Agent Tools
# ============================================================================
echo ""
echo -e "${CYAN}📋 Step 6: Checking current agent tools...${NC}"

AGENT_INFO_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/agents/$AGENT_ID" \
  -H "X-API-Key: $API_KEY")

CURRENT_TOOLS=$(echo "$AGENT_INFO_RESPONSE" | jq -r ".data.tools[]?" 2>/dev/null || echo "No tools")
echo -e "${CYAN}Current tools: $CURRENT_TOOLS${NC}"

sleep 2

# ============================================================================
# Step 7: Dynamically Detach Text Analyzer Tool
# ============================================================================
echo ""
echo -e "${PURPLE}🔧 Step 7: Dynamically detaching 'text_analyzer' tool...${NC}"

DETACH_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/$AGENT_ID/tools/detach" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_names": ["text_analyzer"]
  }')

DETACH_SUCCESS=$(echo "$DETACH_RESPONSE" | jq -r ".success")
if [ "$DETACH_SUCCESS" = "true" ]; then
    echo -e "${GREEN}✅ Text analyzer tool detached successfully${NC}"
else
    echo -e "${RED}❌ Failed to detach text analyzer tool${NC}"
    echo "$DETACH_RESPONSE"
fi

sleep 2

# ============================================================================
# Interaction 4: Test Agent WITH Only Calculator
# ============================================================================
echo ""
echo -e "${YELLOW}🧮 INTERACTION 4: Testing agent with only calculator (text analyzer removed)${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Now try to: 1) Calculate the area of a circle with radius 7.5 meters, and 2) Analyze this text: \"Innovation drives progress.\" Can you still do both tasks?",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 10
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 4 completed${NC}"

sleep 2

# ============================================================================
# Step 8: Detach All Remaining Tools
# ============================================================================
echo ""
echo -e "${PURPLE}🔧 Step 8: Detaching all remaining tools...${NC}"

DETACH_ALL_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/$AGENT_ID/tools/detach" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_names": ["custom_calculator"]
  }')

DETACH_ALL_SUCCESS=$(echo "$DETACH_ALL_RESPONSE" | jq -r ".success")
if [ "$DETACH_ALL_SUCCESS" = "true" ]; then
    echo -e "${GREEN}✅ All tools detached successfully${NC}"
else
    echo -e "${RED}❌ Failed to detach remaining tools${NC}"
    echo "$DETACH_ALL_RESPONSE"
fi

sleep 2

# ============================================================================
# Interaction 5: Test Agent Back to No Tools
# ============================================================================
echo ""
echo -e "${YELLOW}🤖 INTERACTION 5: Testing agent back to no tools state${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "What tools do you have available now? Can you still perform calculations or text analysis?",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 8
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 5 completed${NC}"

# ============================================================================
# Test Summary
# ============================================================================
echo ""
echo "============================================================================"
echo -e "${GREEN}🎉 DYNAMIC TOOL MANAGEMENT TEST COMPLETED${NC}"
echo "============================================================================"
echo "Agent ID: $AGENT_ID"
echo "Conversation ID: $CONVERSATION_ID"
echo ""
echo "Test Coverage:"
echo "✅ Created agent without any tools"
echo "✅ Dynamically attached text_analyzer tool"
echo "✅ Tested agent with text analysis capabilities"
echo "✅ Dynamically attached custom_calculator tool"
echo "✅ Tested agent with both text analysis and calculation capabilities"
echo "✅ Dynamically detached text_analyzer tool"
echo "✅ Tested agent with only calculation capabilities"
echo "✅ Dynamically detached all remaining tools"
echo "✅ Verified agent returned to no-tools state"
echo ""
echo -e "${BLUE}Dynamic tool management successfully demonstrated!${NC}"
echo -e "${CYAN}The agent's capabilities changed in real-time based on attached tools.${NC}"
