# Google ADK Multi-Agent FastAPI Server - Project Overview

## 🎯 Project Summary

This is a comprehensive FastAPI server that provides a complete multi-agent system built on Google's Agent Development Kit (ADK). It supports multi-client usage with robust authentication, real-time streaming conversations, and advanced agent coordination capabilities.

## ✨ Key Features

### 🤖 Agent Management

- **Dynamic Agent Creation**: Create agents with custom personas, configurations, and tools
- **Team Coordination**: Support for Sequential, Parallel, and Hierarchical agent teams
- **Real ADK Integration**: Uses genuine Google ADK classes (LlmAgent, SequentialAgent, ParallelAgent)
- **Tool Integration**: Dynamic tool assignment and management per agent
- **Configuration Management**: Hot-swappable agent configurations and personas

### 🛠️ Tool Management

- **Dynamic Tool Registry**: Runtime tool registration and management
- **Built-in Tools**: Google Search, Calculator, Text Analyzer, Web Scraper, etc.
- **Custom Tool Support**: Easy integration of custom tools
- **Tool Categories**: Organized tool management with categories
- **Usage Analytics**: Track tool usage and performance

### 🧠 Memory Management

- **Conversation Persistence**: SQLite-based memory storage
- **Semantic Search**: Find relevant memories using text matching
- **Importance Weighting**: Prioritize memories by importance scores
- **Context Integration**: Automatic memory integration in conversations
- **User Isolation**: Secure memory separation per user

### 👥 Team Management

- **Sequential Teams**: Agents execute one after another, passing results forward
- **Parallel Teams**: Agents work simultaneously, results are combined
- **Hierarchical Teams**: Coordinator agent manages sub-agents
- **Real ADK Teams**: Uses actual Google ADK team coordination classes
- **Workflow Execution**: Execute complex multi-agent workflows

### 💬 Conversation Management

- **Session Management**: Persistent conversation sessions
- **Message History**: Complete conversation tracking
- **Context Awareness**: Memory-enhanced conversations
- **Multi-format Support**: JSON, streaming, WebSocket
- **Export/Import**: Conversation data portability

### 🌊 Streaming Support

- **Real-time Responses**: 60fps streaming with Server-Sent Events (SSE)
- **WebSocket Support**: Bi-directional real-time communication
- **Optimized Performance**: Batched content delivery and buffering
- **Team Streaming**: Real-time updates from multi-agent teams
- **Event Types**: Start, content, tool calls, thinking, completion, errors

### 🔐 Authentication & Security

- **JWT Tokens**: Secure session-based authentication
- **API Keys**: Long-term API access with permissions
- **Multi-client Support**: Isolated user environments
- **Permission System**: Granular access control
- **Admin Features**: User management and system administration

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│  Routers: agents | tools | memory | teams | conversations  │
│           streaming | auth                                  │
├─────────────────────────────────────────────────────────────┤
│  Managers:                                                  │
│  ├── AgentManager (Google ADK Integration)                 │
│  ├── ToolManager (Dynamic Tool Registry)                   │
│  ├── MemoryManager (SQLite + Search)                       │
│  ├── TeamManager (Multi-agent Coordination)                │
│  ├── ConversationManager (Session Management)              │
│  ├── StreamingHandler (Real-time Responses)                │
│  └── AuthManager (Security & Users)                        │
├─────────────────────────────────────────────────────────────┤
│  Google ADK Layer:                                          │
│  ├── LlmAgent (Individual Agents)                          │
│  ├── SequentialAgent (Team Coordination)                   │
│  ├── ParallelAgent (Team Coordination)                     │
│  ├── Runner (Execution Engine)                             │
│  └── StreamingMode (Real-time Responses)                   │
├─────────────────────────────────────────────────────────────┤
│  Storage Layer:                                             │
│  ├── SQLite (Memory & Conversations)                       │
│  ├── In-Memory (Agents & Tools)                            │
│  └── File System (Configurations)                          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Request Authentication**: JWT/API Key validation
2. **Manager Routing**: Request routed to appropriate manager
3. **Google ADK Integration**: Managers use ADK classes for AI operations
4. **Response Processing**: Results formatted and returned
5. **Streaming Pipeline**: Real-time events streamed to clients

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google API Key (for Gemini models)
- Optional: OpenAI API Key, Anthropic API Key

### Quick Setup

```bash
cd backend
chmod +x start_server.sh
./start_server.sh
```

### Manual Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # Edit with your API keys
python main.py
```

## 📊 API Endpoints Overview

### Authentication (`/auth`)

- `POST /login` - Get JWT token
- `POST /register` - Register new user
- `POST /api-keys` - Create API key
- `GET /api-keys` - List user's API keys

### Agents (`/api/v1/agents`)

- `POST /` - Create agent
- `GET /` - List agents
- `GET /{id}` - Get agent details
- `PUT /{id}` - Update agent
- `DELETE /{id}` - Delete agent
- `GET /search/{query}` - Search agents
- `GET /stats/overview` - Agent statistics

### Tools (`/api/v1/tools`)

- `GET /` - List tools
- `GET /{name}` - Get tool details
- `POST /{name}/enable` - Enable tool
- `POST /{name}/disable` - Disable tool
- `GET /categories/list` - List categories
- `GET /stats/overview` - Tool statistics

### Memory (`/api/v1/memory`)

- `POST /` - Create memory
- `POST /search` - Search memories
- `GET /user/{id}` - List user memories
- `PUT /{id}` - Update memory
- `DELETE /{id}` - Delete memory
- `GET /stats/overview` - Memory statistics

### Teams (`/api/v1/teams`)

- `POST /` - Create team
- `GET /` - List teams
- `GET /{id}` - Get team details
- `PUT /{id}` - Update team
- `POST /{id}/execute` - Execute workflow
- `GET /stats/overview` - Team statistics

### Conversations (`/api/v1/conversations`)

- `POST /start` - Start conversation
- `GET /{id}` - Get conversation
- `GET /user/{id}` - List user conversations
- `POST /{id}/end` - End conversation
- `GET /search/{query}` - Search conversations

### Streaming (`/api/v1/streaming`)

- `POST /send` - Send message (SSE)
- `POST /start` - Start conversation (SSE)
- `WS /ws/{id}` - WebSocket connection
- `GET /sessions/active` - Active sessions
- `GET /stats/overview` - Streaming statistics

## 🔧 Configuration

### Environment Variables

```env
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URL=sqlite:///./google_adk.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### Default Settings

- **Default User**: admin / admin123
- **Database**: SQLite (google_adk.db)
- **Streaming**: 60fps (16ms intervals)
- **Memory**: 10,000 entries max
- **JWT Expiration**: 24 hours

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Authentication Test

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Agent Creation Test

```bash
curl -X POST "http://localhost:8000/api/v1/agents/" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent",
    "persona": {
      "name": "Test Assistant",
      "description": "A test agent",
      "personality": "helpful"
    }
  }'
```

## 📈 Performance Features

### Streaming Optimizations

- **60fps Rendering**: 16ms update intervals
- **Content Batching**: Reduces network overhead
- **Buffer Management**: Smooth content delivery
- **Connection Pooling**: Efficient resource usage

### Memory Optimizations

- **SQLite Indexing**: Fast memory searches
- **Relevance Scoring**: Efficient memory ranking
- **Automatic Cleanup**: Prevents memory bloat
- **Pagination Support**: Large dataset handling

### Caching Strategies

- **Agent Instances**: Cached for reuse
- **Tool Registry**: In-memory tool storage
- **Session Management**: Efficient session tracking
- **Configuration Caching**: Fast setting access

## 🔒 Security Features

### Authentication

- **JWT Tokens**: Secure session management
- **API Keys**: Long-term access control
- **Permission System**: Granular access rights
- **User Isolation**: Secure data separation

### Data Protection

- **Input Validation**: Pydantic model validation
- **SQL Injection Prevention**: Parameterized queries
- **CORS Configuration**: Cross-origin security
- **Rate Limiting**: DDoS protection

## 🚀 Production Deployment

### Docker Support (Future)

```dockerfile
FROM python:3.12
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Environment Setup

- Set strong JWT secrets
- Configure proper CORS origins
- Enable rate limiting
- Set up monitoring and logging
- Use production database (PostgreSQL)

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative docs)
- **CURL Examples**: See CURL_EXAMPLES.md
- **README**: See README.md

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Follow code style guidelines
4. Add tests for new features
5. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues and questions:

1. Check the documentation
2. Review CURL examples
3. Check server logs
4. Create GitHub issue

---

**Built with ❤️ using Google ADK, FastAPI, and modern Python practices**
