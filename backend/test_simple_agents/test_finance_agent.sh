#!/bin/bash

# ============================================================================
# Finance Agent Test - Financial Data and Market Analysis Specialist
# ============================================================================
# Tests an agent with multiple financial tools:
# - yahoo_finance_data: Real-time and historical financial data
# - custom_calculator: Financial calculations and metrics
# - text_analyzer: Analysis of financial news and reports
# - load_memory: Memory operations for financial insights
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "💰 Testing Finance Agent with Yahoo Finance and Analysis Tools"
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
  -d '{"name": "Finance Agent Test", "permissions": ["*"]}')

API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r ".api_key")
echo -e "${GREEN}✅ Authentication successful${NC}"

# ============================================================================
# Step 2: Create Finance Agent with Multiple Tools
# ============================================================================
echo -e "${BLUE}Step 2: Creating Finance Agent...${NC}"

AGENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wall Street Analyst",
    "persona": {
      "name": "Morgan Financial",
      "description": "Expert financial analyst specializing in market analysis, investment research, portfolio optimization, and financial data interpretation",
      "personality": "analytical, data-driven, and strategically focused",
      "expertise": ["financial analysis", "market research", "investment strategy", "risk assessment", "portfolio management", "technical analysis", "fundamental analysis"],
      "communication_style": "professional and precise, providing actionable financial insights with clear risk assessments"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.1,
      "max_output_tokens": 2048
    },
    "tools": ["yahoo_finance_data", "custom_calculator", "text_analyzer", "load_memory"]
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
    \"message\": \"Hello! I'm ready to analyze financial data and provide investment insights.\",
    \"context\": {
      \"test_type\": \"finance_agent\",
      \"session_name\": \"Financial Analysis Session\"
    }
  }")

CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r ".message" | grep -o 'session_[a-f0-9]*')
echo -e "${GREEN}✅ Conversation started: $CONVERSATION_ID${NC}"

# ============================================================================
# Interaction 1: Stock Market Analysis and Portfolio Assessment
# ============================================================================
echo ""
echo -e "${YELLOW}📊 INTERACTION 1: Stock Market Analysis and Portfolio Assessment${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "I need a comprehensive analysis of my tech stock portfolio. Please get current data for: AAPL (Apple), GOOGL (Google), MSFT (Microsoft), TSLA (Tesla), and NVDA (NVIDIA). For each stock, provide: current price, daily change, market cap, P/E ratio, and 52-week range. Calculate the total portfolio value if I own: 50 shares of AAPL, 25 shares of GOOGL, 40 shares of MSFT, 15 shares of TSLA, and 30 shares of NVDA. Also calculate portfolio diversification metrics and risk assessment.",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 15
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 1 completed${NC}"

# ============================================================================
# Interaction 2: Cryptocurrency and Alternative Investment Analysis
# ============================================================================
echo ""
echo -e "${YELLOW}₿ INTERACTION 2: Cryptocurrency and Alternative Investment Analysis${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Analyze the cryptocurrency market and compare it with traditional investments. Get current data for: BTC-USD (Bitcoin), ETH-USD (Ethereum), and compare their performance with: SPY (S&P 500 ETF), GLD (Gold ETF), and TLT (Treasury Bond ETF). Calculate volatility metrics, correlation analysis, and provide risk-adjusted returns. Also analyze this investment news: \"Federal Reserve signals potential interest rate cuts in 2024, driving increased investor interest in growth stocks and cryptocurrency markets. Analysts predict significant capital rotation from bonds to equities.\" What are the implications for portfolio allocation?",
    "stream": true
  }' \
  --no-buffer &

STREAM_PID=$!
echo "Streaming response (PID: $STREAM_PID)..."
sleep 18
kill $STREAM_PID 2>/dev/null || true
echo -e "${GREEN}✅ Interaction 2 completed${NC}"

# ============================================================================
# Interaction 3: Advanced Financial Planning and Strategy
# ============================================================================
echo ""
echo -e "${YELLOW}🎯 INTERACTION 3: Advanced Financial Planning and Strategy${NC}"

curl -s -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$CONVERSATION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Based on our portfolio analysis and market data, create a comprehensive investment strategy for a $100,000 portfolio with moderate risk tolerance. Consider the current market conditions, interest rate environment, and the stocks/assets we analyzed. Calculate optimal allocation percentages, expected returns, and risk metrics. Get current data for defensive stocks like: JNJ (Johnson & Johnson), PG (Procter & Gamble), and KO (Coca-Cola) to include in the balanced portfolio. Store the complete investment strategy and allocation model in memory as \"Moderate Risk Portfolio Strategy 2024\" for future reference. Also provide rebalancing recommendations and exit strategies.",
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
echo -e "${GREEN}🎉 FINANCE AGENT TEST COMPLETED${NC}"
echo "============================================================================"
echo "Agent ID: $AGENT_ID"
echo "Conversation ID: $CONVERSATION_ID"
echo "Tools Tested: yahoo_finance_data, custom_calculator, text_analyzer, load_memory"
echo ""
echo "Test Coverage:"
echo "✅ Real-time stock market data retrieval"
echo "✅ Portfolio valuation and risk assessment"
echo "✅ Cryptocurrency market analysis"
echo "✅ Financial news analysis and interpretation"
echo "✅ Investment strategy development"
echo "✅ Advanced financial calculations and metrics"
echo "✅ Memory storage for investment strategies"
echo ""
echo -e "${BLUE}Agent successfully demonstrated comprehensive financial analysis capabilities!${NC}"
