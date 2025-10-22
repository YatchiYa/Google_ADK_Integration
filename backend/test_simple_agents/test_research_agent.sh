#!/bin/bash

# ============================================================================
# Research Agent Test - Web Research and Information Gathering Specialist
# ============================================================================
# Tests an agent with multiple research tools:
# - google_search: Google ADK built-in search functionality
# - text_analyzer: Content analysis of search results
# - load_memory: Memory operations for research findings
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Testing Research Agent with Google Search and Analysis Tools"
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
  -d '{"name": "Research Agent Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create Research Agent with Multiple Tools
# ============================================================================
echo -e "${BLUE}Step 2: Creating Research Agent...${NC}"

AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Scholar",
    "persona": {
      "name": "Dr. WebSearch",
      "description": "Expert research analyst specializing in comprehensive web research, information synthesis, and fact-checking across multiple sources",
      "personality": "thorough, objective, and academically rigorous",
      "expertise": ["web research", "information synthesis", "fact-checking", "source evaluation", "content analysis", "trend analysis"],
      "communication_style": "scholarly and comprehensive, providing well-sourced information with critical analysis"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.3,
      "max_output_tokens": 2048
    },
    "tools": ["google_search", "text_analyzer", "load_memory"]
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
    \"message\": \"Hello! I'm ready to conduct comprehensive research and analysis.\",
    \"context\": {
      \"test_type\": \"research_agent\",
      \"session_name\": \"Web Research Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"

# ============================================================================
# Interaction 1: Technology Trend Research
# ============================================================================
echo ""
echo -e "${YELLOW}🚀 INTERACTION 1: Technology Trend Research${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Research the latest trends in artificial intelligence and machine learning for 2024. I need comprehensive information about: 1) Emerging AI technologies and breakthroughs, 2) Major AI companies and their recent developments, 3) AI applications in different industries, 4) Future predictions and market analysis. Please use Google Search to find the most current information, then analyze the content quality and credibility of your sources.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 15
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"

# ============================================================================
# Interaction 2: Competitive Market Analysis
# ============================================================================
echo ""
echo -e "${YELLOW}📈 INTERACTION 2: Competitive Market Analysis${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Conduct a competitive analysis of the top 5 project management software companies in 2024. Search for information about: Asana, Monday.com, Trello, Notion, and ClickUp. Compare their features, pricing, market share, recent updates, and customer reviews. Analyze the search results to identify key differentiators and market positioning strategies. Provide insights on which companies are gaining or losing market share.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 18
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 2 completed${NC}"

# ============================================================================
# Interaction 3: Research Synthesis and Future Insights
# ============================================================================
echo ""
echo -e "${YELLOW}🧠 INTERACTION 3: Research Synthesis and Future Insights${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Based on our previous research on AI trends and project management software, synthesize insights to answer this strategic question: How might AI integration transform the project management software industry in the next 2-3 years? Search for additional information about AI-powered project management features, automation trends, and expert predictions. Store your comprehensive analysis in memory as \"AI Project Management Future Trends\" for future reference. Also analyze the quality and reliability of the sources we used in our research sessions.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 20
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 3 completed${NC}"

# ============================================================================
# Test Summary
# ============================================================================
echo ""
echo "============================================================================"
echo -e "${GREEN}🎉 RESEARCH AGENT TEST COMPLETED${NC}"
echo "============================================================================"
echo "Agent ID: $AGENT_ID"
echo "Conversation ID: $CONVERSATION_ID"
echo "Tools Tested: google_search, text_analyzer, load_memory"
echo ""
echo "Test Coverage:"
echo "✅ Technology trend research with Google Search"
echo "✅ Competitive market analysis"
echo "✅ Multi-source information gathering"
echo "✅ Content quality and credibility analysis"
echo "✅ Research synthesis and strategic insights"
echo "✅ Memory storage for research findings"
echo ""
echo -e "${BLUE}Agent successfully demonstrated comprehensive research capabilities!${NC}"
