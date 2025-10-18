# Google ADK Multi-Agent FastAPI Server

A comprehensive FastAPI server with full Google ADK integration supporting multi-client usage, agent management, tool management, memory management, team coordination, and streaming conversations.

## Features

- **Agent Management**: Create, configure, and manage Google ADK agents
- **Tool Management**: Dynamic tool registration and management
- **Memory Management**: Conversation persistence and retrieval
- **Team Management**: Multi-agent coordination (Sequential, Parallel, Hierarchical)
- **Streaming Conversations**: Real-time chat with SSE and WebSocket support
- **Authentication**: JWT tokens and API keys with multi-client support
- **Multi-Client Support**: Secure access control and user management

## Quick Start

### 1. Installation

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### 3. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 4. Access Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

#### Get JWT Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### Create API Key

```bash
curl -X POST "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My API Key", "permissions": ["*"]}'
```

### Agent Management

#### Create Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Assistant Agent",
    "persona": {
      "name": "AI Assistant",
      "description": "A helpful AI assistant",
      "personality": "friendly and professional",
      "expertise": ["general knowledge", "problem solving"],
      "communication_style": "professional"
    },
    "config": {
      "model": "gemini-2.0-flash",
      "temperature": 0.7,
      "max_output_tokens": 2048
    },
    "tools": ["google_search", "custom_calculator"]
  }'
```

#### List Agents

```bash
curl -X GET "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Get Agent

```bash
curl -X GET "http://localhost:8000/api/v1/agents/AGENT_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Tool Management

#### List Tools

```bash
curl -X GET "http://localhost:8000/api/v1/tools/" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Get Tool

```bash
curl -X GET "http://localhost:8000/api/v1/tools/google_search" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Enable/Disable Tool

```bash
# Enable
curl -X POST "http://localhost:8000/api/v1/tools/google_search/enable" \
  -H "X-API-Key: YOUR_API_KEY"

# Disable
curl -X POST "http://localhost:8000/api/v1/tools/google_search/disable" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Memory Management

#### Create Memory

```bash
curl -X POST "http://localhost:8000/api/v1/memory/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "entry": {
      "content": "User prefers detailed explanations",
      "tags": ["preference", "communication"],
      "importance": 0.8
    }
  }'
```

#### Search Memory

```bash
curl -X POST "http://localhost:8000/api/v1/memory/search" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "query": "preferences",
    "limit": 10
  }'
```

### Team Management

#### Create Team

```bash
curl -X POST "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Team",
    "description": "A team for research tasks",
    "team_type": "sequential",
    "agent_ids": ["AGENT_ID_1", "AGENT_ID_2"]
  }'
```

#### List Teams

```bash
curl -X GET "http://localhost:8000/api/v1/teams/" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Conversations

#### Start Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/start" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "agent_id": "AGENT_ID",
    "message": "Hello, how can you help me?"
  }'
```

#### Get Conversation

```bash
curl -X GET "http://localhost:8000/api/v1/conversations/SESSION_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### List User Conversations

```bash
curl -X GET "http://localhost:8000/api/v1/conversations/user/USER_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

### Streaming

#### Send Message with Streaming

```bash
curl -X POST "http://localhost:8000/api/v1/streaming/send?session_id=SESSION_ID" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is artificial intelligence?"
  }' \
  --no-buffer
```

#### Start Streaming Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/streaming/start" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "agent_id": "AGENT_ID",
    "message": "Hello!"
  }' \
  --no-buffer
```

### Statistics

#### Agent Stats

```bash
curl -X GET "http://localhost:8000/api/v1/agents/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Tool Stats

```bash
curl -X GET "http://localhost:8000/api/v1/tools/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Memory Stats

```bash
curl -X GET "http://localhost:8000/api/v1/memory/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

#### Streaming Stats

```bash
curl -X GET "http://localhost:8000/api/v1/streaming/stats/overview" \
  -H "X-API-Key: YOUR_API_KEY"
```

## WebSocket Usage

Connect to WebSocket for real-time conversations:

```javascript
const ws = new WebSocket(
  "ws://localhost:8000/api/v1/streaming/ws/SESSION_ID?api_key=YOUR_API_KEY"
);

ws.onopen = function () {
  console.log("Connected to WebSocket");

  // Send a message
  ws.send(
    JSON.stringify({
      type: "message",
      content: "Hello from WebSocket!",
      metadata: {},
    })
  );
};

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
};
```

## Architecture

```
├── main.py                 # FastAPI application entry point
├── config/
│   └── settings.py        # Application settings
├── managers/              # Core business logic
│   ├── agent_manager.py   # Agent management
│   ├── tool_manager.py    # Tool management
│   ├── memory_manager.py  # Memory management
│   ├── team_manager.py    # Team coordination
│   ├── conversation_manager.py  # Conversation handling
│   └── streaming_handler.py     # Streaming responses
├── routers/               # API endpoints
│   ├── agents.py
│   ├── tools.py
│   ├── memory.py
│   ├── teams.py
│   ├── conversations.py
│   └── streaming.py
├── auth/                  # Authentication
│   ├── auth_manager.py
│   └── dependencies.py
├── models/                # Data models
│   └── api_models.py
├── tools/                 # Custom tools
│   └── google_adk_tools.py
└── utils/                 # Utilities
    └── agent_tool.py
```

## Default Credentials

- **Username**: admin
- **Password**: admin123
- **Default API Key**: Created automatically on first run

## License

MIT License
