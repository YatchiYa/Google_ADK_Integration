#!/bin/bash

# ============================================================================
# Simple Sequential Team Test
# ============================================================================
# Tests: Auth -> API Key -> 2 Agents -> Sequential Team -> Conversation -> Streaming
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🚀 Simple Sequential Team Test"
echo "================================"

# Helper function
extract_json() {
    echo "$1" | jq -r "$2" 2>/dev/null || echo "null"
}

# 1. Authentication
echo -e "${BLUE}Step 1: Authentication${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

JWT_TOKEN=$(extract_json "$LOGIN_RESPONSE" ".access_token")
USER_ID=$(extract_json "$LOGIN_RESPONSE" ".user_id")

if [ "$JWT_TOKEN" = "null" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Authentication successful${NC}"

# 2. Create API Key
echo -e "${BLUE}Step 2: Create API Key${NC}"
API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Simple Test Key", "permissions": ["*"]}')

API_KEY=$(extract_json "$API_KEY_RESPONSE" ".api_key")

if [ "$API_KEY" = "null" ]; then
    echo -e "${RED}❌ API Key creation failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ API Key created: $API_KEY${NC}"

# 3. Create Agent 1
echo -e "${BLUE}Step 3: Create Agent 1${NC}"
AGENT1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Agent 1",
    "persona": {
      "name": "First Agent",
      "description": "First agent in the sequence",
      "personality": "helpful",
      "expertise": ["research"],
      "communication_style": "clear"
    },
    "tools": ["google_search"]
  }')

AGENT1_SUCCESS=$(extract_json "$AGENT1_RESPONSE" ".success")
if [ "$AGENT1_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Agent 1 creation failed: $AGENT1_RESPONSE${NC}"
    exit 1
fi

AGENT1_ID=$(extract_json "$AGENT1_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo -e "${GREEN}✅ Agent 1 created: $AGENT1_ID${NC}"

# 4. Create Agent 2
echo -e "${BLUE}Step 4: Create Agent 2${NC}"
AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Agent 2",
    "persona": {
      "name": "Second Agent",
      "description": "Second agent in the sequence",
      "personality": "analytical",
      "expertise": ["analysis"],
      "communication_style": "detailed"
    },
    "tools": ["text_analyzer"]
  }')

AGENT2_SUCCESS=$(extract_json "$AGENT2_RESPONSE" ".success")
if [ "$AGENT2_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Agent 2 creation failed: $AGENT2_RESPONSE${NC}"
    exit 1
fi

AGENT2_ID=$(extract_json "$AGENT2_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo -e "${GREEN}✅ Agent 2 created: $AGENT2_ID${NC}"

# 5. Create Sequential Team
echo -e "${BLUE}Step 5: Create Sequential Team${NC}"
TEAM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Simple Sequential Team\",
    \"description\": \"Simple sequential workflow\",
    \"team_type\": \"sequential\",
    \"agent_ids\": [\"$AGENT1_ID\", \"$AGENT2_ID\"]
  }")

TEAM_SUCCESS=$(extract_json "$TEAM_RESPONSE" ".success")
if [ "$TEAM_SUCCESS" != "true" ]; then
    echo -e "${RED}❌ Team creation failed: $TEAM_RESPONSE${NC}"
    exit 1
fi

TEAM_ID=$(extract_json "$TEAM_RESPONSE" ".message" | grep -o 'team_[a-f0-9]*')
echo -e "${GREEN}✅ Sequential team created: $TEAM_ID${NC}"

# 6. Test Regular Agent Conversation (for comparison)
echo -e "${BLUE}Step 6: Test Regular Agent Conversation${NC}"
REGULAR_CONV_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$AGENT1_ID\",
    \"message\": \"Hello, can you help me?\",
    \"context\": {}
  }")

REGULAR_CONV_SUCCESS=$(extract_json "$REGULAR_CONV_RESPONSE" ".success")
if [ "$REGULAR_CONV_SUCCESS" = "true" ]; then
    echo -e "${GREEN}✅ Regular agent conversation works${NC}"
    REGULAR_SESSION_ID=$(extract_json "$REGULAR_CONV_RESPONSE" ".session_id")
    echo "Session ID: $REGULAR_SESSION_ID"
else
    echo -e "${YELLOW}⚠️ Regular agent conversation failed: $(extract_json "$REGULAR_CONV_RESPONSE" ".detail")${NC}"
fi

# 7. Test Team Conversation
echo -e "${BLUE}Step 7: Test Team Conversation${NC}"
TEAM_CONV_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"agent_id\": \"$TEAM_ID\",
    \"message\": \"Hello team, please process this request sequentially\",
    \"context\": {}
  }")

TEAM_CONV_SUCCESS=$(extract_json "$TEAM_CONV_RESPONSE" ".success")
if [ "$TEAM_CONV_SUCCESS" = "true" ]; then
    echo -e "${GREEN}✅ Team conversation works!${NC}"
    TEAM_SESSION_ID=$(extract_json "$TEAM_CONV_RESPONSE" ".session_id")
    echo "Team Session ID: $TEAM_SESSION_ID"
    
    # 8. Test Streaming with Team (with tool usage)
    echo -e "${BLUE}Step 8: Test Team Streaming with Tool Usage${NC}"
    echo "Starting streaming session with a request that should trigger Google Search..."
    echo "Message: 'Search for the latest AI developments in 2024 and summarize them'"
    echo ""
    
    # Create a temporary file for streaming output
    STREAM_OUTPUT="/tmp/team_streaming_$(date +%s).txt"
    
    # Start streaming and capture complete output
    echo "🔄 Streaming in progress... (will capture complete response)"
    timeout 60s curl -s -N -X POST "http://localhost:8000/api/v1/streaming/start" \
      -H "X-API-Key: $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"user_id\": \"$USER_ID\",
        \"agent_id\": \"$TEAM_ID\",
        \"message\": \"Search for the latest AI developments in 2024 and summarize them\"
      }" > "$STREAM_OUTPUT" 2>&1
    
    if [ -s "$STREAM_OUTPUT" ]; then
        echo -e "${GREEN}✅ Team streaming completed!${NC}"
        echo ""
        echo "=== COMPLETE STREAMING OUTPUT ==="
        
        # Count different event types
        START_EVENTS=$(grep -c '"type": "start"' "$STREAM_OUTPUT" 2>/dev/null | head -1 || echo "0")
        CONTENT_EVENTS=$(grep -c '"type": "content"' "$STREAM_OUTPUT" 2>/dev/null | head -1 || echo "0")
        TOOL_CALL_EVENTS=$(grep -c '"type": "tool_call"' "$STREAM_OUTPUT" 2>/dev/null | head -1 || echo "0")
        TOOL_RESPONSE_EVENTS=$(grep -c '"type": "tool_response"' "$STREAM_OUTPUT" 2>/dev/null | head -1 || echo "0")
        COMPLETE_EVENTS=$(grep -c '"type": "complete"' "$STREAM_OUTPUT" 2>/dev/null | head -1 || echo "0")
        TOTAL_LINES=$(wc -l < "$STREAM_OUTPUT" | head -1)
        
        echo "📊 Event Summary:"
        echo "  - Total streaming lines: $TOTAL_LINES"
        echo "  - Start events: $START_EVENTS"
        echo "  - Content events: $CONTENT_EVENTS"
        echo "  - Tool call events: $TOOL_CALL_EVENTS"
        echo "  - Tool response events: $TOOL_RESPONSE_EVENTS"
        echo "  - Complete events: $COMPLETE_EVENTS"
        echo ""
        
        # Show tool calls if any
        if [ "$TOOL_CALL_EVENTS" -gt 0 ]; then
            echo "🔧 Tool Calls Detected:"
            grep '"type": "tool_call"' "$STREAM_OUTPUT" | head -3 | while read line; do
                TOOL_NAME=$(echo "$line" | jq -r '.metadata.tool_name // "unknown"' 2>/dev/null)
                echo "  - Tool: $TOOL_NAME"
            done
            echo ""
        fi
        
        # Show first few content events
        echo "📝 First Content Events:"
        grep '"type": "content"' "$STREAM_OUTPUT" | head -5 | while read line; do
            CONTENT=$(echo "$line" | jq -r '.content' 2>/dev/null | head -c 100)
            echo "  Content: $CONTENT..."
        done
        echo ""
        
        # Show complete response if available
        if [ "$COMPLETE_EVENTS" -gt 0 ]; then
            echo "✅ Complete Response:"
            grep '"type": "complete"' "$STREAM_OUTPUT" | tail -1 | jq -r '.content // .metadata.final_response // "No final response captured"' 2>/dev/null | head -c 500
            echo "..."
        fi
        
        # Save detailed output for inspection
        echo ""
        echo "💾 Full streaming output saved to: $STREAM_OUTPUT"
        echo "   Use 'cat $STREAM_OUTPUT | jq .' to view formatted JSON"
        
    else
        echo -e "${RED}❌ Team streaming failed - no output captured${NC}"
        echo "Check if the streaming endpoint is working properly"
    fi
    
else
    echo -e "${RED}❌ Team conversation failed: $(extract_json "$TEAM_CONV_RESPONSE" ".detail")${NC}"
    echo "This indicates the conversation manager cannot find team agents"
fi

# 9. Debug Information
echo -e "${BLUE}Step 9: Debug Information${NC}"
echo "Listing all agents and teams..."

AGENTS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/agents/" -H "X-API-Key: $API_KEY")
AGENTS_TOTAL=$(extract_json "$AGENTS_RESPONSE" ".total")
echo "Total Agents: $AGENTS_TOTAL"

TEAMS_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/teams/" -H "X-API-Key: $API_KEY")
TEAMS_TOTAL=$(extract_json "$TEAMS_RESPONSE" ".total")
echo "Total Teams: $TEAMS_TOTAL"

echo ""
echo "============================================================================"
echo -e "${BLUE}SUMMARY${NC}"
echo "============================================================================"
echo "Agent 1 ID: $AGENT1_ID"
echo "Agent 2 ID: $AGENT2_ID" 
echo "Sequential Team ID: $TEAM_ID"
echo "Regular Agent Conversation: $([ "$REGULAR_CONV_SUCCESS" = "true" ] && echo "✅ Works" || echo "❌ Failed")"
echo "Sequential Team Conversation: $([ "$TEAM_CONV_SUCCESS" = "true" ] && echo "✅ Works" || echo "❌ Failed")"

# 10. Test Hierarchical Team (should support tools better)
echo -e "${BLUE}Step 10: Test Hierarchical Team with Tools${NC}"
HIER_TEAM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Hierarchical Research Team\",
    \"description\": \"Hierarchical team that can delegate to agents with tools\",
    \"team_type\": \"hierarchical\",
    \"agent_ids\": [\"$AGENT1_ID\", \"$AGENT2_ID\"]
  }")

HIER_TEAM_SUCCESS=$(extract_json "$HIER_TEAM_RESPONSE" ".success")
if [ "$HIER_TEAM_SUCCESS" = "true" ]; then
    HIER_TEAM_ID=$(extract_json "$HIER_TEAM_RESPONSE" ".message" | grep -o 'team_[a-f0-9]*')
    echo -e "${GREEN}✅ Hierarchical team created: $HIER_TEAM_ID${NC}"
    
    # Test hierarchical team streaming with tool usage
    echo "Testing hierarchical team streaming..."
    HIER_STREAM_OUTPUT="/tmp/hier_streaming_$(date +%s).txt"
    
    timeout 60s curl -s -N -X POST "http://localhost:8000/api/v1/streaming/start" \
      -H "X-API-Key: $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"user_id\": \"$USER_ID\",
        \"agent_id\": \"$HIER_TEAM_ID\",
        \"message\": \"Use Google Search to find the latest AI news and summarize it\"
      }" > "$HIER_STREAM_OUTPUT" 2>&1
    
    HIER_TOOL_CALLS=$(grep -c '"type": "tool_call"' "$HIER_STREAM_OUTPUT" 2>/dev/null | head -1 || echo "0")
    echo "Hierarchical Team Tool Calls: $HIER_TOOL_CALLS"
    
    if [ "$HIER_TOOL_CALLS" -gt 0 ]; then
        echo -e "${GREEN}✅ Hierarchical team uses tools!${NC}"
        echo "Tool calls detected in hierarchical team"
    else
        echo -e "${YELLOW}⚠️ Hierarchical team didn't use tools${NC}"
    fi
    
    echo "Hierarchical Team ID: $HIER_TEAM_ID"
else
    echo -e "${RED}❌ Hierarchical team creation failed${NC}"
    HIER_TEAM_ID="none"
fi

if [ "$TEAM_CONV_SUCCESS" != "true" ]; then
    echo ""
    echo -e "${YELLOW}ISSUE IDENTIFIED:${NC}"
    echo "Teams are created successfully but conversation manager cannot find them."
    echo "This suggests the conversation manager is not using the updated agent manager properly."
fi

# Cleanup (keep streaming output for inspection)
echo ""
echo "📁 Files preserved for inspection:"
ls -la /tmp/team_streaming_*.txt 2>/dev/null || echo "  No streaming files found"

echo ""
echo "🏁 Test Complete!"
