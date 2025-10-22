#!/bin/bash

# ============================================================================
# Product Discovery Agent Test - Product Hunt and Market Research Specialist
# ============================================================================
# Tests an agent with multiple product discovery tools:
# - product_hunt_search: Product Hunt API for product discovery
# - text_analyzer: Analysis of product descriptions and reviews
# - custom_calculator: Market metrics and scoring calculations
# - load_memory: Memory operations for product insights
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🚀 Testing Product Discovery Agent with Product Hunt and Analysis Tools"
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
  -d '{"name": "Product Agent Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create Product Discovery Agent with Multiple Tools
# ============================================================================
echo -e "${BLUE}Step 2: Creating Product Discovery Agent...${NC}"

AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Hunter Pro",
    "persona": {
      "name": "Innovation Scout",
      "description": "Expert product researcher specializing in discovering trending products, analyzing market opportunities, and evaluating product-market fit across various industries",
      "personality": "curious, trend-aware, and strategically minded",
      "expertise": ["product discovery", "market analysis", "trend identification", "competitive intelligence", "user experience evaluation", "product strategy"],
      "communication_style": "enthusiastic and insightful, providing actionable product intelligence with market context"
    }, 
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.9,
      "max_output_tokens": 2048
    },
    "tools": ["product_hunt_search", "text_analyzer", "custom_calculator"]
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
    \"message\": \"Hello! I'm ready to discover and analyze products and market opportunities.\",
    \"context\": {
      \"test_type\": \"product_agent\",
      \"session_name\": \"Product Discovery Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"

# ============================================================================
# Interaction 1: AI and Productivity Tools Discovery
# ============================================================================
echo ""
echo -e "${YELLOW}🤖 INTERACTION 1: AI and Productivity Tools Discovery${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "I am looking for innovative AI-powered productivity tools that have launched recently. Search Product Hunt for products related to \"AI productivity\", \"artificial intelligence\", and \"automation tools\". I want to discover the top trending AI products, analyze their descriptions for key features and value propositions, and identify market opportunities. Calculate engagement metrics (upvotes, comments) and provide insights on which AI categories are most popular. Focus on products that could help with workflow automation, content creation, or business intelligence.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 15
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"

# # ============================================================================
# # Interaction 2: Mobile App and SaaS Product Analysis
# # ============================================================================
# echo ""
# echo -e "${YELLOW}📱 INTERACTION 2: Mobile App and SaaS Product Analysis${NC}"

# curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
#   -H "X-API-Key: $API_KEY" \
#   -H "Content-Type: application/json" \
#   -H "Accept: text/event-stream" \
#   -d '{
#     "message": "Conduct a comprehensive analysis of trending mobile apps and SaaS products in the productivity and business categories. Search for \"mobile app\", \"SaaS\", \"business tools\", and \"startup\" on Product Hunt. Compare the top products by analyzing their descriptions, user engagement, and market positioning. Calculate success metrics and identify common patterns among highly-voted products. Also analyze this product description for market potential: \"Revolutionary team collaboration platform that combines video conferencing, project management, and AI-powered meeting summaries in one seamless workspace. Features real-time document editing, smart scheduling, and automated task assignment based on conversation analysis.\" Rate its market appeal and suggest improvements.",
#     "stream": true
#   }' \
#   --no-buffer &

# STREAM_PID=$!
# echo "Streaming response (PID: $STREAM_PID)..."
# sleep 18
# kill $STREAM_PID 2>/dev/null || true
# echo -e "${GREEN}✅ Interaction 2 completed${NC}"

# # ============================================================================
# # Interaction 3: Market Opportunity Analysis and Product Strategy
# # ============================================================================
# echo ""
# echo -e "${YELLOW}🎯 INTERACTION 3: Market Opportunity Analysis and Product Strategy${NC}"

# curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
#   -H "X-API-Key: $API_KEY" \
#   -H "Content-Type: application/json" \
#   -H "Accept: text/event-stream" \
#   -d '{
#     "message": "Based on our Product Hunt research of AI productivity tools and SaaS products, synthesize insights to identify the biggest market opportunities for 2024. Search for \"fintech\", \"healthtech\", and \"edtech\" products to expand our market analysis. Calculate market saturation scores for different product categories based on the number of similar products and their engagement levels. Create a comprehensive market opportunity report that includes: 1) Underserved market segments, 2) Emerging product trends, 3) Optimal product positioning strategies, 4) Competitive landscape analysis. Store this analysis in memory as \"Product Market Opportunities 2024\" for future strategic planning. Also provide recommendations for a startup looking to enter the AI productivity space.",
#     "stream": true
#   }' \
#   --no-buffer &

# STREAM_PID=$!
# echo "Streaming response (PID: $STREAM_PID)..."
# sleep 20
# kill $STREAM_PID 2>/dev/null || true
# echo -e "${GREEN}✅ Interaction 3 completed${NC}"

# # ============================================================================
# # Test Summary
# # ============================================================================
# echo ""
# echo "============================================================================"
# echo -e "${GREEN}🎉 PRODUCT DISCOVERY AGENT TEST COMPLETED${NC}"
# echo "============================================================================"
# echo "Agent ID: $AGENT_ID"
# echo "Conversation ID: $CONVERSATION_ID"
# echo "Tools Tested: product_hunt_search, text_analyzer, custom_calculator, load_memory"
# echo ""
# echo "Test Coverage:"
# echo "✅ AI and productivity tools discovery via Product Hunt"
# echo "✅ Mobile app and SaaS product analysis"
# echo "✅ Product description and market potential analysis"
# echo "✅ Engagement metrics and success pattern identification"
# echo "✅ Market opportunity analysis across multiple sectors"
# echo "✅ Competitive landscape assessment"
# echo "✅ Strategic recommendations for product positioning"
# echo "✅ Memory storage for market insights"
# echo ""
# echo -e "${BLUE}Agent successfully demonstrated comprehensive product discovery capabilities!${NC}"
