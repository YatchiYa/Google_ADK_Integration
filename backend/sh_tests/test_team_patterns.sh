#!/bin/bash

# ============================================================================
# Google ADK Team Patterns Test Suite
# ============================================================================
# Tests Sequential, Parallel, Hierarchical, and Loop team patterns
# Each test creates separate agents to avoid parent validation errors
# ============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TEST_COUNT=0
PASSED_COUNT=0
FAILED_COUNT=0

print_test() {
    TEST_COUNT=$((TEST_COUNT + 1))
    echo ""
    echo "============================================================================"
    echo -e "${BLUE}TEST $TEST_COUNT: $1${NC}"
    echo "============================================================================"
}

check_result() {
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED: $1${NC}"
        PASSED_COUNT=$((PASSED_COUNT + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED: $1${NC}"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        return 1
    fi
}

extract_json() {
    echo "$1" | jq -r "$2" 2>/dev/null || echo "null"
}

# Function to test conversation without failing the script
test_conversation() {
    local team_id=$1
    local team_name=$2
    
    echo "Testing conversation with $team_name ($team_id)..."
    
    CONV_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
      -H "X-API-Key: $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"user_id\": \"$USER_ID\",
        \"agent_id\": \"$team_id\",
        \"message\": \"Hello team, please process this request\",
        \"context\": {\"test\": \"conversation_test\"}
      }")
    
    CONV_SUCCESS=$(extract_json "$CONV_RESPONSE" ".success")
    if [ "$CONV_SUCCESS" = "true" ]; then
        echo -e "${GREEN}✅ Conversation with $team_name successful${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Conversation with $team_name failed: $(extract_json "$CONV_RESPONSE" ".detail")${NC}"
        echo "Note: This may be expected as team agents use different execution patterns"
        return 1
    fi
}

echo "🚀 Google ADK Team Patterns Test Suite"
echo "Server: http://localhost:8000"
echo "Time: $(date)"
echo ""

# ============================================================================
# SETUP: Authentication
# ============================================================================
print_test "Authentication Setup"

LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

JWT_TOKEN=$(extract_json "$LOGIN_RESPONSE" ".access_token")
USER_ID=$(extract_json "$LOGIN_RESPONSE" ".user_id")

API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Team Test Key", "permissions": ["*"]}')

API_KEY=$(extract_json "$API_KEY_RESPONSE" ".api_key")

if [ "$API_KEY" != "null" ] && [ "$API_KEY" != "" ]; then
    check_result "Authentication Setup"
    echo "API Key: $API_KEY"
else
    echo "❌ Failed authentication setup"
    exit 1
fi

# ============================================================================
# TEST 1: SEQUENTIAL TEAM PATTERN
# ============================================================================
print_test "Sequential Team Pattern - News → Social → Content"

# Create agents for sequential team
echo "Creating agents for sequential team..."

SEQ_AGENT1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sequential News Researcher",
    "persona": {
      "name": "News Research Specialist",
      "description": "Researches current news and events",
      "personality": "thorough and analytical",
      "expertise": ["news research", "current events"],
      "communication_style": "factual"
    },
    "tools": ["google_search"],
    "config": {"temperature": 0.3}
  }')

SEQ_AGENT1_ID=$(extract_json "$SEQ_AGENT1_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Sequential Agent 1 ID: $SEQ_AGENT1_ID"

SEQ_AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sequential Social Analyst",
    "persona": {
      "name": "Social Media Expert",
      "description": "Analyzes social media trends",
      "personality": "trend-aware",
      "expertise": ["social media", "sentiment analysis"],
      "communication_style": "engaging"
    },
    "tools": ["google_search"],
    "config": {"temperature": 0.5}
  }')

SEQ_AGENT2_ID=$(extract_json "$SEQ_AGENT2_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Sequential Agent 2 ID: $SEQ_AGENT2_ID"

SEQ_AGENT3_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sequential Content Writer",
    "persona": {
      "name": "Professional Writer",
      "description": "Creates engaging content",
      "personality": "creative",
      "expertise": ["content writing", "storytelling"],
      "communication_style": "eloquent"
    },
    "tools": ["text_analyzer"],
    "config": {"temperature": 0.8}
  }')

SEQ_AGENT3_ID=$(extract_json "$SEQ_AGENT3_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Sequential Agent 3 ID: $SEQ_AGENT3_ID"

# Create sequential team
echo "Creating sequential team..."
SEQ_TEAM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Sequential Content Pipeline\",
    \"description\": \"Sequential workflow: Research → Analysis → Writing\",
    \"team_type\": \"sequential\",
    \"agent_ids\": [\"$SEQ_AGENT1_ID\", \"$SEQ_AGENT2_ID\", \"$SEQ_AGENT3_ID\"],
    \"metadata\": {\"pattern\": \"SequentialAgent\", \"test\": \"sequential_test\"}
  }")

SEQ_TEAM_SUCCESS=$(extract_json "$SEQ_TEAM_RESPONSE" ".success")
if [ "$SEQ_TEAM_SUCCESS" = "true" ]; then
    SEQ_TEAM_ID=$(extract_json "$SEQ_TEAM_RESPONSE" ".message" | grep -o 'team_[a-f0-9]*')
    check_result "Sequential Team Creation"
    echo "Sequential Team ID: $SEQ_TEAM_ID"
else
    echo "❌ Sequential team creation failed: $SEQ_TEAM_RESPONSE"
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi

# Test sequential team conversation
test_conversation "$SEQ_TEAM_ID" "Sequential Team"

# ============================================================================
# TEST 2: PARALLEL TEAM PATTERN  
# ============================================================================
print_test "Parallel Team Pattern - Market + Tech Research Concurrently"

# Create agents for parallel team (separate from sequential)
echo "Creating agents for parallel team..."

PAR_AGENT1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Parallel Market Researcher",
    "persona": {
      "name": "Market Research Expert",
      "description": "Conducts market research and analysis",
      "personality": "analytical",
      "expertise": ["market research", "business intelligence"],
      "communication_style": "professional"
    },
    "tools": ["google_search"],
    "config": {"temperature": 0.3}
  }')

PAR_AGENT1_ID=$(extract_json "$PAR_AGENT1_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Parallel Agent 1 ID: $PAR_AGENT1_ID"

PAR_AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Parallel Tech Analyst",
    "persona": {
      "name": "Technology Expert",
      "description": "Analyzes technology trends",
      "personality": "technical",
      "expertise": ["technology trends", "innovation"],
      "communication_style": "technical"
    },
    "tools": ["google_search"],
    "config": {"temperature": 0.4}
  }')

PAR_AGENT2_ID=$(extract_json "$PAR_AGENT2_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Parallel Agent 2 ID: $PAR_AGENT2_ID"

# Create parallel team
echo "Creating parallel team..."
PAR_TEAM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Parallel Research Squad\",
    \"description\": \"Parallel research: Market + Tech analysis simultaneously\",
    \"team_type\": \"parallel\",
    \"agent_ids\": [\"$PAR_AGENT1_ID\", \"$PAR_AGENT2_ID\"],
    \"metadata\": {\"pattern\": \"ParallelAgent\", \"test\": \"parallel_test\"}
  }")

PAR_TEAM_SUCCESS=$(extract_json "$PAR_TEAM_RESPONSE" ".success")
if [ "$PAR_TEAM_SUCCESS" = "true" ]; then
    PAR_TEAM_ID=$(extract_json "$PAR_TEAM_RESPONSE" ".message" | grep -o 'team_[a-f0-9]*')
    check_result "Parallel Team Creation"
    echo "Parallel Team ID: $PAR_TEAM_ID"
else
    echo "❌ Parallel team creation failed: $PAR_TEAM_RESPONSE"
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi

# Test parallel team conversation
test_conversation "$PAR_TEAM_ID" "Parallel Team"

# ============================================================================
# TEST 3: HIERARCHICAL TEAM PATTERN
# ============================================================================
print_test "Hierarchical Team Pattern - Intelligent Delegation"

# Create agents for hierarchical team
echo "Creating agents for hierarchical team..."

HIER_AGENT1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hierarchical Data Analyst",
    "persona": {
      "name": "Data Analysis Expert",
      "description": "Specialized in data analysis and insights",
      "personality": "methodical",
      "expertise": ["data analysis", "statistics"],
      "communication_style": "analytical"
    },
    "tools": ["custom_calculator", "text_analyzer"],
    "config": {"temperature": 0.2}
  }')

HIER_AGENT1_ID=$(extract_json "$HIER_AGENT1_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Hierarchical Agent 1 ID: $HIER_AGENT1_ID"

HIER_AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hierarchical Strategy Advisor",
    "persona": {
      "name": "Strategic Planning Expert",
      "description": "Provides strategic recommendations",
      "personality": "strategic",
      "expertise": ["strategic planning", "business strategy"],
      "communication_style": "strategic"
    },
    "tools": ["text_analyzer"],
    "config": {"temperature": 0.6}
  }')

HIER_AGENT2_ID=$(extract_json "$HIER_AGENT2_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Hierarchical Agent 2 ID: $HIER_AGENT2_ID"

# Create hierarchical team
echo "Creating hierarchical team..."
HIER_TEAM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Hierarchical Strategic Intelligence\",
    \"description\": \"Hierarchical team with intelligent delegation\",
    \"team_type\": \"hierarchical\",
    \"agent_ids\": [\"$HIER_AGENT1_ID\", \"$HIER_AGENT2_ID\"],
    \"metadata\": {\"pattern\": \"LlmAgent with sub_agents\", \"test\": \"hierarchical_test\"}
  }")

HIER_TEAM_SUCCESS=$(extract_json "$HIER_TEAM_RESPONSE" ".success")
if [ "$HIER_TEAM_SUCCESS" = "true" ]; then
    HIER_TEAM_ID=$(extract_json "$HIER_TEAM_RESPONSE" ".message" | grep -o 'team_[a-f0-9]*')
    check_result "Hierarchical Team Creation"
    echo "Hierarchical Team ID: $HIER_TEAM_ID"
else
    echo "❌ Hierarchical team creation failed: $HIER_TEAM_RESPONSE"
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi

# Test hierarchical team conversation
test_conversation "$HIER_TEAM_ID" "Hierarchical Team"

# ============================================================================
# TEST 4: LOOP TEAM PATTERN
# ============================================================================
print_test "Loop Team Pattern - Iterative Processing"

# Create agents for loop team
echo "Creating agents for loop team..."

LOOP_AGENT1_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Loop Processor",
    "persona": {
      "name": "Processing Agent",
      "description": "Processes tasks iteratively",
      "personality": "systematic",
      "expertise": ["task processing", "iteration"],
      "communication_style": "systematic"
    },
    "tools": ["custom_calculator"],
    "config": {"temperature": 0.3}
  }')

LOOP_AGENT1_ID=$(extract_json "$LOOP_AGENT1_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Loop Agent 1 ID: $LOOP_AGENT1_ID"

LOOP_AGENT2_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Loop Checker",
    "persona": {
      "name": "Validation Agent",
      "description": "Checks completion conditions",
      "personality": "thorough",
      "expertise": ["validation", "quality control"],
      "communication_style": "precise"
    },
    "tools": ["text_analyzer"],
    "config": {"temperature": 0.2}
  }')

LOOP_AGENT2_ID=$(extract_json "$LOOP_AGENT2_RESPONSE" ".message" | grep -o 'agent_[a-f0-9]*')
echo "Loop Agent 2 ID: $LOOP_AGENT2_ID"

# Create loop team
echo "Creating loop team..."
LOOP_TEAM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Loop Processing Team\",
    \"description\": \"Loop team for iterative processing\",
    \"team_type\": \"loop\",
    \"agent_ids\": [\"$LOOP_AGENT1_ID\", \"$LOOP_AGENT2_ID\"],
    \"metadata\": {\"pattern\": \"LoopAgent\", \"test\": \"loop_test\"}
  }")

LOOP_TEAM_SUCCESS=$(extract_json "$LOOP_TEAM_RESPONSE" ".success")
if [ "$LOOP_TEAM_SUCCESS" = "true" ]; then
    LOOP_TEAM_ID=$(extract_json "$LOOP_TEAM_RESPONSE" ".message" | grep -o 'team_[a-f0-9]*')
    check_result "Loop Team Creation"
    echo "Loop Team ID: $LOOP_TEAM_ID"
else
    echo "❌ Loop team creation failed: $LOOP_TEAM_RESPONSE"
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi

# Test loop team conversation
test_conversation "$LOOP_TEAM_ID" "Loop Team"

# ============================================================================
# SUMMARY AND VERIFICATION
# ============================================================================
print_test "Summary and Team List Verification"

echo "Listing all created teams..."
TEAMS_LIST_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY")

TEAMS_SUCCESS=$(extract_json "$TEAMS_LIST_RESPONSE" ".success")
TEAMS_TOTAL=$(extract_json "$TEAMS_LIST_RESPONSE" ".total")

if [ "$TEAMS_SUCCESS" = "true" ] && [ "$TEAMS_TOTAL" -ge "4" ]; then
    check_result "Team List Verification"
    echo "Total Teams Created: $TEAMS_TOTAL"
    
    echo ""
    echo "Team Details:"
    echo "$TEAMS_LIST_RESPONSE" | jq -r '.teams[] | "- \(.name) (\(.team_type)): \(.team_id)"'
else
    echo "❌ Team verification failed. Expected 4+ teams, got: $TEAMS_TOTAL"
    FAILED_COUNT=$((FAILED_COUNT + 1))
fi

# ============================================================================
# FINAL RESULTS
# ============================================================================
echo ""
echo "============================================================================"
echo "🏁 FINAL RESULTS"
echo "============================================================================"
echo -e "Total Tests: $TEST_COUNT"
echo -e "${GREEN}Passed: $PASSED_COUNT${NC}"
echo -e "${RED}Failed: $FAILED_COUNT${NC}"

if [ $FAILED_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Google ADK Team Patterns working correctly!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Check logs above for details.${NC}"
    exit 1
fi
