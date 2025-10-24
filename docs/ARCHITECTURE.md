# Database Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Agents  │  │   Chat   │  │  Tools   │  │   Home   │       │
│  │   Page   │  │   Page   │  │   Page   │  │   Page   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │              │              │
└───────┼─────────────┼──────────────┼──────────────┼──────────────┘
        │             │              │              │
        └─────────────┴──────────────┴──────────────┘
                      │
                      ▼ HTTP/SSE
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      API Routers                            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │  Agents  │  │Streaming │  │  Convs   │  │  Memory  │  │ │
│  │  │  Router  │  │  Router  │  │  Router  │  │  Router  │  │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │ │
│  └───────┼─────────────┼─────────────┼─────────────┼─────────┘ │
│          │             │             │             │             │
│          ▼             ▼             ▼             ▼             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Manager Layer                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │    Agent     │  │Conversation  │  │   Memory     │    │ │
│  │  │   Manager    │◄─┤   Manager    │◄─┤   Manager    │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘    │ │
│  │         │                  │                                │ │
│  │         │  ┌───────────────┴────────────────┐              │ │
│  │         │  │                                 │              │ │
│  │         ▼  ▼                                 ▼              │ │
│  │  ┌──────────────┐                   ┌──────────────┐      │ │
│  │  │   Memory     │                   │   Database   │      │ │
│  │  │    Cache     │                   │   Service    │      │ │
│  │  │  (In-RAM)    │                   │  (SQLAlchemy)│      │ │
│  │  └──────────────┘                   └──────┬───────┘      │ │
│  └────────────────────────────────────────────┼──────────────┘ │
└─────────────────────────────────────────────────┼────────────────┘
                                                  │
                                                  ▼ SQL
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  new_agent   │  │new_conversations│ │new_messages │         │
│  │              │  │              │  │              │         │
│  │ - agent_id   │  │ - conv_id    │  │ - msg_id     │         │
│  │ - name       │  │ - agent_id ──┼──┤ - conv_id ───┼─┐       │
│  │ - persona    │  │ - session_id │  │ - role       │ │       │
│  │ - config     │  │ - title      │  │ - content    │ │       │
│  │ - tools      │  │ - status     │  │ - metadata   │ │       │
│  │ - metadata   │  │ - metadata   │  │              │ │       │
│  └──────────────┘  └──────────────┘  └──────────────┘ │       │
│         │                                               │       │
│         └───────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Agent Creation Flow

```
┌─────────┐
│ User    │
│ Creates │
│ Agent   │
└────┬────┘
     │
     ▼ POST /api/v1/agents/
┌─────────────────┐
│ Agents Router   │
└────┬────────────┘
     │
     ▼ create_agent()
┌─────────────────┐
│ Agent Manager   │
│                 │
│ 1. Create       │
│    AgentInfo    │
│ 2. Create       │
│    ADK Agent    │
│ 3. Store in     │
│    Memory       │
└────┬────────────┘
     │
     ▼ _save_agent_to_db()
┌─────────────────┐
│ Database        │
│ Service         │
│                 │
│ save_agent()    │
└────┬────────────┘
     │
     ▼ INSERT INTO new_agent
┌─────────────────┐
│ PostgreSQL      │
│                 │
│ Agent Persisted │
└─────────────────┘
```

### 2. Agent Streaming Flow (On-Demand Loading)

```
┌─────────┐
│ User    │
│ Starts  │
│ Chat    │
└────┬────┘
     │
     ▼ POST /api/v1/streaming/start
┌─────────────────┐
│ Streaming       │
│ Router          │
└────┬────────────┘
     │
     ▼ ensure_agent_instance()
┌─────────────────┐
│ Agent Manager   │
│                 │
│ Check Memory?   │
│   ├─ Yes ──────┐│
│   └─ No ───────┘│
└────┬────────────┘
     │ Not in memory
     ▼ get_agent()
┌─────────────────┐
│ Database        │
│ Service         │
│                 │
│ Load agent data │
└────┬────────────┘
     │
     ▼ SELECT FROM new_agent
┌─────────────────┐
│ PostgreSQL      │
│                 │
│ Return agent    │
└────┬────────────┘
     │
     ▼ Reconstruct AgentInfo
┌─────────────────┐
│ Agent Manager   │
│                 │
│ 1. Create       │
│    AgentInfo    │
│ 2. Create       │
│    ADK Instance │
│ 3. Cache in     │
│    Memory       │
│ 4. Update usage │
└────┬────────────┘
     │
     ▼ Agent ready
┌─────────────────┐
│ Streaming       │
│ Handler         │
│                 │
│ Stream response │
└─────────────────┘
```

### 3. Conversation & Message Flow

```
┌─────────┐
│ User    │
│ Sends   │
│ Message │
└────┬────┘
     │
     ▼ POST /api/v1/streaming/start
┌─────────────────┐
│ Conversation    │
│ Manager         │
│                 │
│ start_          │
│ conversation()  │
└────┬────────────┘
     │
     ├─────────────────────────┐
     │                         │
     ▼ Save to Memory          ▼ Save to DB
┌─────────────────┐    ┌─────────────────┐
│ Memory Cache    │    │ Database        │
│                 │    │ Service         │
│ Conversation    │    │                 │
│ + Message       │    │ save_           │
│                 │    │ conversation()  │
└─────────────────┘    │ save_message()  │
                       └────┬────────────┘
                            │
                            ▼ INSERT
                       ┌─────────────────┐
                       │ PostgreSQL      │
                       │                 │
                       │ new_            │
                       │ conversations   │
                       │ new_messages    │
                       └─────────────────┘
```

## Component Responsibilities

### Frontend Layer

```
┌────────────────────────────────────────────────────────┐
│                    Frontend Components                  │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Agents Page (/agents)                                 │
│  ├─ Display agents from API                            │
│  ├─ Create new agents                                  │
│  └─ Edit/delete agents                                 │
│                                                         │
│  Chat Page (/chat/[agentId])                           │
│  ├─ Start conversations                                │
│  ├─ Send messages                                      │
│  ├─ Display streaming responses                        │
│  └─ Show conversation history                          │
│                                                         │
│  Tools Page (/tools)                                   │
│  ├─ Display available tools                            │
│  ├─ Attach/detach tools to agents                      │
│  └─ Show tool usage statistics                         │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### Backend Layer

```
┌────────────────────────────────────────────────────────┐
│                    API Routers                          │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Agents Router (/api/v1/agents)                        │
│  ├─ POST /     → Create agent                          │
│  ├─ GET /      → List agents                           │
│  ├─ GET /{id}  → Get agent                             │
│  ├─ PUT /{id}  → Update agent                          │
│  └─ DELETE /{id} → Delete agent                        │
│                                                         │
│  Streaming Router (/api/v1/streaming)                  │
│  ├─ POST /start → Start streaming conversation         │
│  ├─ POST /send  → Send message with streaming          │
│  └─ WS /ws/{id} → WebSocket connection                 │
│                                                         │
│  Conversations Router (/api/v1/conversations)          │
│  ├─ POST /start → Start conversation                   │
│  ├─ GET /{id}   → Get conversation                     │
│  ├─ GET /       → List conversations                   │
│  └─ POST /{id}/message → Add message                   │
│                                                         │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                    Manager Layer                        │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Agent Manager                                          │
│  ├─ Create agents                                      │
│  ├─ Manage agent lifecycle                             │
│  ├─ Load agents from DB (lazy)                         │
│  ├─ Save agents to DB (auto)                           │
│  └─ Ensure agent instances (on-demand)                 │
│                                                         │
│  Conversation Manager                                   │
│  ├─ Start conversations                                │
│  ├─ Add messages                                       │
│  ├─ Load conversations from DB                         │
│  ├─ Save conversations to DB (auto)                    │
│  └─ Save messages to DB (auto)                         │
│                                                         │
│  Tool Manager                                           │
│  ├─ Register tools                                     │
│  ├─ Get tools for agents                               │
│  └─ Manage tool lifecycle                              │
│                                                         │
│  Memory Manager                                         │
│  ├─ Store conversation context                         │
│  ├─ Retrieve relevant memories                         │
│  └─ Manage memory lifecycle                            │
│                                                         │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                    Service Layer                        │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Database Service                                       │
│  ├─ Connection management                              │
│  ├─ Agent CRUD operations                              │
│  ├─ Conversation CRUD operations                       │
│  ├─ Message CRUD operations                            │
│  ├─ Statistics and monitoring                          │
│  └─ Error handling                                     │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### Database Layer

```
┌────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                  │
├────────────────────────────────────────────────────────┤
│                                                         │
│  new_agent                                             │
│  ├─ Stores agent configurations                        │
│  ├─ Persona information                                │
│  ├─ Tool assignments                                   │
│  ├─ Usage statistics                                   │
│  └─ Metadata                                           │
│                                                         │
│  new_conversations                                     │
│  ├─ Stores conversation sessions                       │
│  ├─ Links to agents                                    │
│  ├─ Message counts                                     │
│  ├─ Status tracking                                    │
│  └─ Timestamps                                         │
│                                                         │
│  new_messages                                          │
│  ├─ Stores all messages                                │
│  ├─ Links to conversations                             │
│  ├─ Role and content                                   │
│  ├─ Tool call metadata                                 │
│  └─ Timestamps                                         │
│                                                         │
└────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Repository Pattern

```
Manager Layer (Business Logic)
        ↓
Database Service (Data Access)
        ↓
SQLAlchemy ORM (Object Mapping)
        ↓
PostgreSQL (Data Storage)
```

### 2. Lazy Loading Pattern

```
Request for Agent
    ↓
Check Memory Cache
    ├─ Found → Return
    └─ Not Found
        ↓
    Load from Database
        ↓
    Create Instance
        ↓
    Cache in Memory
        ↓
    Return
```

### 3. Write-Through Cache Pattern

```
Create/Update Operation
    ↓
Write to Memory Cache
    ↓
Write to Database
    ↓
Return Success
```

## Performance Optimizations

### Caching Strategy

```
┌─────────────────────────────────────────┐
│           Request Flow                   │
└─────────────────────────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Check Memory │ ◄─── Fast (μs)
         │    Cache     │
         └──────┬───────┘
                │
         ┌──────┴───────┐
         │              │
    Found│              │Not Found
         │              │
         ▼              ▼
    ┌────────┐   ┌──────────────┐
    │ Return │   │ Query        │ ◄─── Slower (ms)
    │ Cached │   │ Database     │
    └────────┘   └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Cache Result │
                 │ Return Data  │
                 └──────────────┘
```

### Database Connection Pooling

```
┌─────────────────────────────────────────┐
│        Connection Pool                   │
│                                          │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐   │
│  │Conn│ │Conn│ │Conn│ │Conn│ │Conn│   │
│  │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │   │
│  └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘   │
└────┼──────┼──────┼──────┼──────┼────────┘
     │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼
   Req1   Req2   Req3   Req4   Req5
```

## Scalability Considerations

### Horizontal Scaling

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Backend  │  │ Backend  │  │ Backend  │
│Instance 1│  │Instance 2│  │Instance 3│
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   PostgreSQL    │
         │   (Shared DB)   │
         └─────────────────┘
```

### Read Replicas (Future)

```
┌──────────┐
│ Primary  │ ◄─── Writes
│   DB     │
└────┬─────┘
     │ Replication
     ├──────────┬──────────┐
     ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐
│Replica 1││Replica 2││Replica 3│ ◄─── Reads
└─────────┘└─────────┘└─────────┘
```

---

**Architecture Version**: 1.0.0
**Last Updated**: January 23, 2025
