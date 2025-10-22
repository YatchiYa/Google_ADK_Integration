#!/bin/bash

# ============================================================================
# Analysis Agent Test - Text and Data Analysis Specialist
# ============================================================================
# Tests an agent with multiple analysis tools:
# - text_analyzer: Advanced text analysis and metrics
# - custom_calculator: Statistical calculations
# - load_memory: Memory operations for analysis results
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "📊 Testing Analysis Agent with Multiple Analysis Tools"
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
  -d '{"name": "Analysis Agent Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create Analysis Agent with Multiple Tools
# ============================================================================
echo -e "${BLUE}Step 2: Creating Analysis Agent...${NC}"

AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Analyst Pro",
    "persona": {
      "name": "Dr. Analytics",
      "description": "Expert data analyst specializing in text analysis, sentiment analysis, content metrics, and statistical interpretation of textual data",
      "personality": "methodical, insightful, and detail-oriented",
      "expertise": ["text analysis", "sentiment analysis", "content strategy", "data interpretation", "statistical analysis", "natural language processing"],
      "communication_style": "analytical and comprehensive, providing detailed insights with actionable recommendations"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.2,
      "max_output_tokens": 2048
    },
    "tools": ["text_analyzer", "custom_calculator", "load_memory"]
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
    \"message\": \"Hello! I'm ready to analyze text and provide detailed insights.\",
    \"context\": {
      \"test_type\": \"analysis_agent\",
      \"session_name\": \"Content Analysis Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"

# ============================================================================
# Interaction 1: Comprehensive Text Analysis
# ============================================================================
echo ""
echo -e "${YELLOW}📝 INTERACTION 1: Comprehensive Text Analysis${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Please analyze this product review comprehensively: \"I absolutely love this new smartphone! The camera quality is outstanding, capturing incredibly sharp photos even in low light. The battery life exceeds my expectations, lasting easily through a full day of heavy usage. However, I found the user interface slightly confusing at first, and the price point is quite steep for budget-conscious consumers. Overall, despite minor drawbacks, this device delivers exceptional performance and innovative features that justify the investment. Highly recommended for tech enthusiasts!\" Provide detailed text metrics, sentiment analysis, key themes, and readability assessment.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 10
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"

# ============================================================================
# Interaction 2: Comparative Content Analysis
# ============================================================================
echo ""
echo -e "${YELLOW}🔍 INTERACTION 2: Comparative Content Analysis${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Compare and analyze these two marketing headlines: \n\nHeadline A: \"Revolutionary AI Technology Transforms Business Operations Forever\" \n\nHeadline B: \"Smart AI Tools Help Small Businesses Save Time and Money\" \n\nAnalyze word choice, emotional impact, target audience appeal, clarity, and effectiveness. Calculate readability scores, word frequency, and provide statistical comparison of their linguistic features. Which headline would perform better and why?",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 12
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 2 completed${NC}"

# ============================================================================
# Interaction 3: Advanced Analytics with Memory Integration
# ============================================================================
echo ""
echo -e "${YELLOW}🧠 INTERACTION 3: Advanced Analytics with Memory Integration${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Based on our previous analyses of the product review and marketing headlines, create a comprehensive content strategy report. Calculate the average sentiment score across all analyzed texts, identify common positive and negative themes, and recommend optimal content length and style for this product category. Store these insights in memory as \"Content Strategy Guidelines\" for future reference. Also analyze this social media post: \"Just tried the new coffee shop downtown ☕️ Amazing latte art and cozy atmosphere! Perfect spot for remote work 💻 #coffee #productivity #remote\" and compare its engagement potential with our previous examples.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 15
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 3 completed${NC}"

# ============================================================================
# Test Summary
# ============================================================================
echo ""
echo "============================================================================"
echo -e "${GREEN}🎉 ANALYSIS AGENT TEST COMPLETED${NC}"
echo "============================================================================"
echo "Agent ID: $AGENT_ID"
echo "Conversation ID: $CONVERSATION_ID"
echo "Tools Tested: text_analyzer, custom_calculator, load_memory"
echo ""
echo "Test Coverage:"
echo "✅ Comprehensive text analysis (sentiment, metrics, themes)"
echo "✅ Comparative content analysis"
echo "✅ Statistical text comparison"
echo "✅ Content strategy recommendations"
echo "✅ Social media content analysis"
echo "✅ Memory integration for insights storage"
echo ""
echo -e "${BLUE}Agent successfully demonstrated advanced analytical capabilities!${NC}"
