# Complete CURL Examples for Google ADK Multi-Agent API

This document provides comprehensive curl examples for testing all endpoints of the Google ADK Multi-Agent FastAPI server.

## Authentication Examples

### 1. Login and Get JWT Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### 2. Register New User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 3. Create API Key
```bash
curl -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key",
    "permissions": ["agents:*", "conversations:*", "memory:*"],
    "expires_days": 90
  }'
```

### 4. List API Keys
```bash
curl -X GET "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Agent Management Examples

### 1. Create Simple Agent
```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "General Assistant",
    "persona": {
      "name": "AI Assistant",
      "description": "A helpful AI assistant for general tasks",
      "personality": "friendly, professional, and helpful",
      "expertise": ["general knowledge", "problem solving", "writing"],
      "communication_style": "professional",
      "language": "en"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.7,
      "max_output_tokens": 2048,
      "top_p": 0.9,
      "top_k": 40
    },
    "tools": ["google_search", "custom_calculator", "text_analyzer"]
  }'
```

### 2. Create Specialized Agent
```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Specialist",
    "persona": {
      "name": "Research Expert",
      "description": "Specialized in research and data analysis",
      "personality": "analytical, thorough, and detail-oriented",
      "expertise": ["research methodology", "data analysis", "academic writing"],
      "communication_style": "academic",
      "custom_instructions": "Always provide sources and citations when possible. Focus on accuracy and thoroughness."
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.3,
      "max_output_tokens": 4096
    },
    "tools": ["google_search", "text_analyzer"],
    "planner": "PlanReActPlanner"
  }'
```

### 3. Create Team Agent (Sequential)
```bash
# First create individual agents, then create team agent
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Team",
    "persona": {
      "name": "Research Team Coordinator",
      "description": "Coordinates research tasks across multiple specialists",
      "personality": "organized and systematic"
    },
    "agent_type": "SequentialAgent",
    "sub_agents": ["RESEARCHER_AGENT_ID", "ANALYST_AGENT_ID", "WRITER_AGENT_ID"]
  }'
```

### 4. List All Agents
```bash
curl -X GET "http://localhost:8000/api/v1/agents/?limit=20&offset=0" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 5. Get Specific Agent
```bash
curl -X GET "http://localhost:8000/api/v1/agents/AGENT_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 6. Update Agent Configuration
```bash
curl -X PUT "http://localhost:8000/api/v1/agents/AGENT_ID" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "temperature": 0.5,
      "max_output_tokens": 3000
    },
    "tools": ["google_search", "custom_calculator", "text_analyzer", "web_scraper"]
  }'
```

### 7. Search Agents
```bash
curl -X GET "http://localhost:8000/api/v1/agents/search/research" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 8. Get Agent Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/agents/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 9. Export Agent Configuration
```bash
curl -X GET "http://localhost:8000/api/v1/agents/AGENT_ID/export" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 10. Deactivate Agent
```bash
curl -X POST "http://localhost:8000/api/v1/agents/AGENT_ID/deactivate" \
  -H "X-API-Key: YOUR_API_KEY"
```

## Tool Management Examples

### 1. List All Tools
```bash
curl -X GET "http://localhost:8000/api/v1/tools/" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 2. Get Specific Tool
```bash
curl -X GET "http://localhost:8000/api/v1/tools/google_search" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 3. Search Tools
```bash
curl -X GET "http://localhost:8000/api/v1/tools/search/calculator" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 4. List Tool Categories
```bash
curl -X GET "http://localhost:8000/api/v1/tools/categories/list" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 5. Enable Tool
```bash
curl -X POST "http://localhost:8000/api/v1/tools/google_search/enable" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 6. Disable Tool
```bash
curl -X POST "http://localhost:8000/api/v1/tools/custom_calculator/disable" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 7. Get Tool Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/tools/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

## Memory Management Examples

### 1. Create Memory Entry
```bash
curl -X POST "http://localhost:8000/api/v1/memory/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "entry": {
      "content": "User prefers detailed technical explanations with examples",
      "tags": ["preference", "communication", "technical"],
      "importance": 0.8,
      "metadata": {
        "category": "user_preference",
        "source": "conversation"
      }
    },
    "session_id": "session_123",
    "agent_id": "AGENT_ID"
  }'
```

### 2. Search Memories
```bash
curl -X POST "http://localhost:8000/api/v1/memory/search" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "query": "technical explanations",
    "limit": 10,
    "min_relevance": 0.5,
    "tags": ["preference"]
  }'
```

### 3. List User Memories
```bash
curl -X GET "http://localhost:8000/api/v1/memory/user/admin?limit=20&offset=0" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 4. Get Specific Memory
```bash
curl -X GET "http://localhost:8000/api/v1/memory/MEMORY_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 5. Update Memory
```bash
curl -X PUT "http://localhost:8000/api/v1/memory/MEMORY_ID" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated: User prefers detailed technical explanations with code examples",
    "importance": 0.9,
    "tags": ["preference", "communication", "technical", "coding"]
  }'
```

### 6. Get Memory Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/memory/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 7. Export User Memories
```bash
curl -X GET "http://localhost:8000/api/v1/memory/export/user/admin" \
  -H "X-API-Key: YOUR_API_KEY"
```

## Team Management Examples

### 1. Create Sequential Team
```bash
curl -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Content Creation Pipeline",
    "description": "Sequential team for content creation: research -> write -> review",
    "team_type": "sequential",
    "agent_ids": ["RESEARCHER_ID", "WRITER_ID", "REVIEWER_ID"],
    "metadata": {
      "use_case": "content_creation",
      "expected_duration": "30_minutes"
    }
  }'
```

### 2. Create Parallel Team
```bash
curl -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Analysis Team",
    "description": "Parallel analysis from different perspectives",
    "team_type": "parallel",
    "agent_ids": ["TECHNICAL_ANALYST_ID", "BUSINESS_ANALYST_ID", "RISK_ANALYST_ID"]
  }'
```

### 3. Create Hierarchical Team
```bash
curl -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Team",
    "description": "Hierarchical team with coordinator",
    "team_type": "hierarchical",
    "agent_ids": ["SPECIALIST_1_ID", "SPECIALIST_2_ID", "SPECIALIST_3_ID"],
    "coordinator_id": "PROJECT_MANAGER_ID"
  }'
```

### 4. List Teams
```bash
curl -X GET "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 5. Get Team Details
```bash
curl -X GET "http://localhost:8000/api/v1/teams/TEAM_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 6. Add Agent to Team
```bash
curl -X POST "http://localhost:8000/api/v1/teams/TEAM_ID/agents/NEW_AGENT_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 7. Execute Team Workflow
```bash
curl -X POST "http://localhost:8000/api/v1/teams/TEAM_ID/execute" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze market trends for Q1 2024",
    "context": {
      "industry": "technology",
      "focus_areas": ["AI", "cloud computing", "cybersecurity"]
    }
  }'
```

### 8. Get Team Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/teams/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

## Conversation Management Examples

### 1. Start New Conversation
```bash
curl -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "admin",
    "agent_id": "AGENT_ID",
    "message": "Hello! I need help with a Python programming question.",
    "context": {
      "topic": "programming",
      "language": "python",
      "skill_level": "intermediate"
    }
  }'
```

### 2. Get Conversation
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/SESSION_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 3. Get Conversation History
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/SESSION_ID/history?limit=50" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 4. List User Conversations
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/user/admin?limit=20" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 5. Search Conversations
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/search/python?limit=10" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 6. Update Conversation Metadata
```bash
curl -X PUT "http://localhost:8000/api/v1/conversations/SESSION_ID/metadata" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "advanced_python",
    "resolved": true,
    "satisfaction": 5,
    "tags": ["programming", "python", "solved"]
  }'
```

### 7. End Conversation
```bash
curl -X POST "http://localhost:8000/api/v1/conversations/SESSION_ID/end" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 8. Export Conversation
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/SESSION_ID/export" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 9. Get Conversation Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

## Streaming Examples

### 1. Send Message with Streaming Response
```bash
curl -X POST "http://localhost:8000/api/v1/streaming/send?session_id=SESSION_ID" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "Explain quantum computing in simple terms",
    "metadata": {
      "request_type": "explanation",
      "complexity": "beginner"
    }
  }' \
  --no-buffer
```

### 2. Start Streaming Conversation
```bash
curl -X POST "http://localhost:8000/api/v1/streaming/start" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "user_id": "admin",
    "agent_id": "AGENT_ID",
    "message": "I want to learn about machine learning. Where should I start?"
  }' \
  --no-buffer
```

### 3. Get Active Streaming Sessions
```bash
curl -X GET "http://localhost:8000/api/v1/streaming/sessions/active" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 4. Stop Streaming Session
```bash
curl -X POST "http://localhost:8000/api/v1/streaming/sessions/SESSION_ID/stop" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 5. Get Streaming Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/streaming/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 6. Update Streaming Configuration (Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/streaming/config/update" \
  -H "X-API-Key: YOUR_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "update_interval_ms": 20,
    "batch_size": 5,
    "buffer_timeout_ms": 150
  }'
```

## Health Check and System Status

### 1. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### 2. API Root Information
```bash
curl -X GET "http://localhost:8000/"
```

## Complete Workflow Example

Here's a complete workflow demonstrating the full capabilities:

### 1. Authenticate
```bash
# Get API key
RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

JWT_TOKEN=$(echo $RESPONSE | jq -r '.access_token')

# Create API key
API_KEY_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Workflow Key", "permissions": ["*"]}')

API_KEY=$(echo $API_KEY_RESPONSE | jq -r '.api_key')
```

### 2. Create Agents
```bash
# Create research agent
RESEARCHER=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Researcher",
    "persona": {
      "name": "Research Specialist",
      "description": "Expert in research and information gathering",
      "personality": "thorough and analytical"
    },
    "tools": ["google_search", "web_scraper"]
  }')

RESEARCHER_ID=$(echo $RESEARCHER | jq -r '.agent_id')

# Create writer agent
WRITER=$(curl -s -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Writer",
    "persona": {
      "name": "Content Writer",
      "description": "Expert in creating engaging content",
      "personality": "creative and articulate"
    },
    "tools": ["text_analyzer"]
  }')

WRITER_ID=$(echo $WRITER | jq -r '.agent_id')
```

### 3. Create Team
```bash
TEAM=$(curl -s -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Content Team\",
    \"description\": \"Research and writing team\",
    \"team_type\": \"sequential\",
    \"agent_ids\": [\"$RESEARCHER_ID\", \"$WRITER_ID\"]
  }")

TEAM_ID=$(echo $TEAM | jq -r '.team_id')
```

### 4. Start Conversation
```bash
CONVERSATION=$(curl -s -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"admin\",
    \"agent_id\": \"$RESEARCHER_ID\",
    \"message\": \"Research the latest trends in artificial intelligence\"
  }")

SESSION_ID=$(echo $CONVERSATION | jq -r '.session_id')
```

### 5. Send Streaming Message
```bash
curl -X POST "http://localhost:8000/api/v1/streaming/send?session_id=$SESSION_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Focus on machine learning and natural language processing advances in 2024"
  }' \
  --no-buffer
```

This completes a full workflow demonstrating agent creation, team formation, conversation management, and streaming responses.
