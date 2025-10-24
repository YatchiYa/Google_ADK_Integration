# Google ADK Agent API Server

FastAPI server for testing your Google ADK multi-agent research pipeline.

## 🏗️ Agent Architecture

Your `root_agent` is a **hybrid parallel-sequential pipeline**:

### Phase 1: Parallel Research (3 concurrent pipelines)
```
ParallelAgent
├── News Pipeline (Sequential)
│   ├── news_fetcher (uses google_search)
│   └── news_summarizer
├── Social Pipeline (Sequential)
│   ├── social_monitor (uses google_search)
│   └── sentiment_analyzer
└── Expert Pipeline (Sequential)
    ├── expert_finder (uses google_search)
    └── quote_extractor
```

### Phase 2: Sequential Content Creation
```
SequentialAgent
├── article_writer (synthesizes all research)
├── article_editor (refines content)
└── article_formatter (adds markdown formatting)
```

**Total: 10 sub-agents** orchestrated across 2 phases

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /home/yarab/Bureau/perso/jinxai/Google_ADK_Integration/test_api
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python server.py
```

You should see:
```
🚀 Google ADK Agent API Server
============================================================
📚 Interactive Docs: http://localhost:8000/docs
🔍 Health Check: http://localhost:8000/
📋 List Apps: http://localhost:8000/list-apps
============================================================
```

### 3. Test with cURL

#### Create a Session
```bash
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"state": {"visit_count": 1}}'
```

#### Run Agent (Single Response)
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [
        {"text": "Write an article about artificial intelligence trends in 2024"}
      ]
    }
  }'
```

#### Run Agent (Streaming)
```bash
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
      "role": "user",
      "parts": [
        {"text": "Write an article about quantum computing breakthroughs"}
      ]
    },
    "streaming": true
  }'
```

---

## 📡 API Endpoints

### Utility
- `GET /` - Health check
- `GET /list-apps` - List available agents
- `GET /docs` - Interactive API documentation

### Session Management
- `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}` - Create/update session
- `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}` - Get session
- `DELETE /apps/{app_name}/users/{user_id}/sessions/{session_id}` - Delete session

### Agent Execution
- `POST /run` - Execute agent, return all events at once
- `POST /run_sse` - Execute agent, stream events (Server-Sent Events)

---

## 🧪 Testing Examples

### Example Topics to Test
- "Write an article about artificial intelligence trends"
- "Write an article about quantum computing breakthroughs"
- "Write an article about climate change solutions"
- "Write an article about space exploration updates"
- "Write an article about blockchain technology developments"

### View All Commands
```bash
chmod +x test_commands.sh
./test_commands.sh
```

---

## 📊 Event Capture

Events are captured in the following format:

```json
{
  "content": {
    "parts": [{"text": "response text"}],
    "role": "model"
  },
  "invocationId": "inv-1234567890.123",
  "author": "root_agent",
  "actions": {
    "stateDelta": {},
    "artifactDelta": {},
    "requestedAuthConfigs": {}
  },
  "id": "msg-0",
  "timestamp": 1234567890.123
}
```

---

## 🔍 Interactive API Docs

Visit **http://localhost:8000/docs** for:
- Complete API reference
- Try-it-out functionality
- Request/response schemas
- Live testing interface

---

## 🛠️ How It Works

1. **Session Management**: Sessions store conversation state and event history
2. **Event Capture**: All agent interactions are logged as events
3. **Streaming Support**: Choose between single response or SSE streaming
4. **State Persistence**: Session state is maintained across requests

---

## 📝 Notes

- Sessions are stored in-memory (use Redis/DB for production)
- The agent uses `google_search` tool (requires API credentials)
- Events include user messages, agent responses, and errors
- Token-level streaming simulates word-by-word output

---

## 🐛 Troubleshooting

### Agent Not Running
- Ensure `my_sample_agent` module is importable
- Check that `root_agent` is properly defined in `agent.py`

### Google Search Errors
- Verify Google API credentials are configured
- Check that `google_search` tool is properly initialized

### Session Not Found
- Create a session first using the POST endpoint
- Verify app_name, user_id, and session_id match

---

## 📚 Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/adk)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
