# Database Integration Guide

## Overview

This Google ADK Integration system now includes full PostgreSQL persistence for agents, conversations, and messages. The system automatically saves all data to the database and loads it on-demand.

## Database Configuration

### Connection String

Set your PostgreSQL connection in environment variables:

```bash
DATABASE_URL=postgresql://de:de@localhost:5432/de
```

Or it will use the default from the code.

## Database Schema

### Tables

#### 1. `new_agent` - Agent Storage

Stores all agent configurations and metadata:

```sql
- agent_id (PK): Unique agent identifier
- name: Agent name
- description: Agent description
- agent_type: Type (regular, SequentialAgent, ParallelAgent)
- persona_*: Persona configuration fields
- config: JSON configuration object
- tools: JSON array of tool names
- sub_agents: JSON array of sub-agent IDs
- planner: Planner type
- version: Agent version
- is_active: Active status
- usage_count: Usage statistics
- created_at: Creation timestamp
- last_used: Last usage timestamp
- metadata: Additional JSON metadata
```

#### 2. `new_conversations` - Conversation Storage

Stores conversation sessions:

```sql
- conversation_id (PK): Unique conversation identifier
- agent_id (FK): Reference to agent
- session_id: Session identifier
- title: Conversation title
- status: Status (active, archived, deleted)
- message_count: Number of messages
- created_at: Creation timestamp
- updated_at: Last update timestamp
- last_message_at: Last message timestamp
- metadata: Additional JSON metadata
```

#### 3. `new_messages` - Message Storage

Stores all conversation messages:

```sql
- message_id (PK): Unique message identifier
- conversation_id (FK): Reference to conversation
- role: Message role (user, assistant, system, tool)
- content: Message content
- message_type: Type (text, tool_call, tool_response, thinking, error)
- tool_name: Tool name (if tool message)
- tool_args: JSON tool arguments
- tool_call_id: Tool call identifier
- is_streaming: Streaming status
- is_complete: Completion status
- created_at: Creation timestamp
- metadata: Additional JSON metadata
```

## Features

### 1. **Automatic Persistence**

All operations automatically save to database:

- **Agent Creation**: Agents are saved when created
- **Conversation Start**: Conversations are saved when started
- **Message Addition**: Messages are saved when added

### 2. **Lazy Loading**

Agents and conversations are loaded on-demand:

- **Agent Loading**: Agents are loaded from DB when first accessed
- **Conversation Loading**: Conversations are loaded from DB when accessed
- **Memory Caching**: Loaded data is cached in memory for performance

### 3. **On-Demand Agent Creation**

When streaming starts, if an agent is not in memory:

1. System checks database for agent
2. If found, loads agent configuration
3. Creates ADK instance on-demand
4. Proceeds with streaming

## Usage Examples

### Creating an Agent (Auto-saved to DB)

```python
from managers.agent_manager import AgentManager, AgentPersona, AgentConfig
from services.database_service import DatabaseService

# Initialize services
db_service = DatabaseService()
agent_manager = AgentManager(tool_manager, memory_manager, db_service)

# Create agent (automatically saved to DB)
persona = AgentPersona(
    name="Customer Support Agent",
    description="Helps customers with inquiries",
    personality="friendly and helpful",
    expertise=["customer service", "product knowledge"]
)

agent_id = agent_manager.create_agent(
    name="Support Bot",
    persona=persona,
    tools=["google_search", "calculator"]
)
# Agent is now in database!
```

### Starting a Conversation (Auto-saved to DB)

```python
from managers.conversation_manager import ConversationManager

# Initialize with database service
conversation_manager = ConversationManager(
    agent_manager,
    memory_manager,
    streaming_handler,
    database_service=db_service
)

# Start conversation (automatically saved to DB)
session_id = conversation_manager.start_conversation(
    user_id="user_123",
    agent_id=agent_id,
    initial_message="Hello!"
)
# Conversation and message are now in database!
```

### Streaming with On-Demand Agent Loading

```python
# When streaming starts, agent is loaded from DB if not in memory
agent = agent_manager.ensure_agent_instance(agent_id)

# If agent exists in DB but not in memory:
# 1. Loads agent configuration from database
# 2. Creates ADK instance
# 3. Returns ready-to-use agent
# 4. Updates usage statistics
```

### Loading Conversations from Database

```python
# Get conversation (loads from DB if not in memory)
conversation = conversation_manager.get_conversation(session_id)

# Conversation includes:
# - All messages from database
# - Full conversation history
# - Metadata and timestamps
```

## API Integration

### Agent Endpoints

All agent endpoints automatically use database:

```bash
# Create agent (saved to DB)
POST /api/v1/agents/

# List agents (from DB)
GET /api/v1/agents/

# Get agent (from DB)
GET /api/v1/agents/{agent_id}

# Update agent (updates DB)
PUT /api/v1/agents/{agent_id}

# Delete agent (soft delete in DB)
DELETE /api/v1/agents/{agent_id}
```

### Conversation Endpoints

All conversation endpoints use database:

```bash
# Start conversation (saved to DB)
POST /api/v1/conversations/start

# Get conversation (from DB)
GET /api/v1/conversations/{session_id}

# List conversations (from DB)
GET /api/v1/conversations/

# Send message (saved to DB)
POST /api/v1/conversations/{session_id}/message
```

### Streaming Endpoints

Streaming automatically loads agents from database:

```bash
# Start streaming (loads agent from DB if needed)
POST /api/v1/streaming/start

# All messages are saved to DB during streaming
```

## Testing

### Run Database Tests

```bash
cd backend
python test_database.py
```

This will test:

- Database connection
- Agent persistence
- Conversation persistence
- Message persistence
- Lazy loading
- On-demand agent creation

### Manual Testing

1. **Create an agent via API**
2. **Restart the backend server**
3. **Start a conversation with that agent**
4. **Agent should load from database automatically**

## Database Service API

### Agent Operations

```python
# Save agent
db_service.save_agent(agent_data)

# Get agent
agent = db_service.get_agent(agent_id)

# List all agents
agents = db_service.get_all_agents(include_inactive=False)

# Delete agent (soft delete)
db_service.delete_agent(agent_id)

# Update usage
db_service.update_agent_usage(agent_id)
```

### Conversation Operations

```python
# Save conversation
db_service.save_conversation(conversation_data)

# Get conversation
conversation = db_service.get_conversation(conversation_id)

# Get agent conversations
conversations = db_service.get_agent_conversations(agent_id, limit=50)

# Delete conversation
db_service.delete_conversation(conversation_id)
```

### Message Operations

```python
# Save message
db_service.save_message(message_data)

# Get conversation messages
messages = db_service.get_conversation_messages(conversation_id, limit=100)

# Update message
db_service.update_message(message_id, updates)

# Delete message
db_service.delete_message(message_id)
```

### Statistics

```python
# Get database statistics
stats = db_service.get_stats()
# Returns: {
#   "total_agents": 10,
#   "total_conversations": 50,
#   "total_messages": 500
# }
```

## Architecture

### Flow Diagram

```
┌─────────────────┐
│   API Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Router Layer   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Manager Layer   │◄────►│ Database Service │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│  Memory Cache   │      │   PostgreSQL DB  │
└─────────────────┘      └──────────────────┘
```

### Key Components

1. **DatabaseService** (`services/database_service.py`)

   - Handles all database operations
   - Uses SQLAlchemy ORM
   - Connection pooling and error handling

2. **Database Models** (`models/db_models.py`)

   - SQLAlchemy models for agents, conversations, messages
   - Relationships and constraints

3. **Agent Manager** (`managers/agent_manager.py`)

   - Loads agents from DB on startup
   - Saves agents to DB on creation
   - Lazy loads agents on-demand

4. **Conversation Manager** (`managers/conversation_manager.py`)
   - Saves conversations and messages to DB
   - Loads conversations from DB on-demand
   - Maintains memory cache

## Performance Considerations

### Caching Strategy

- **Memory First**: Always check memory cache first
- **DB Fallback**: Load from database if not in memory
- **Lazy Loading**: Only create ADK instances when needed
- **Usage Tracking**: Update statistics asynchronously

### Optimization Tips

1. **Connection Pooling**: Adjust pool size based on load
2. **Batch Operations**: Use bulk inserts for multiple messages
3. **Indexing**: Ensure proper indexes on foreign keys
4. **Cleanup**: Periodically archive old conversations

## Error Handling

The system gracefully handles database errors:

```python
# If database is unavailable
try:
    database_service = DatabaseService()
except Exception as e:
    logger.error(f"Database unavailable: {e}")
    database_service = None
    # System continues without persistence
```

## Migration

### From In-Memory to Database

1. **Backup existing data** (if any)
2. **Set DATABASE_URL** environment variable
3. **Restart backend** - tables are created automatically
4. **Verify connection** with test script
5. **Create agents** - they're automatically saved

### Database Migrations

For schema changes, use Alembic:

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
python test_database.py

# Check logs
tail -f logs/backend.log | grep -i database
```

### Data Not Persisting

1. Check DATABASE_URL is set correctly
2. Verify database service initialized
3. Check logs for save errors
4. Ensure tables exist

### Performance Issues

1. Check database connection pool size
2. Monitor query performance
3. Add indexes if needed
4. Consider caching strategies

## Security

### Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for connection strings
3. **Implement proper access control** at database level
4. **Encrypt sensitive data** in metadata fields
5. **Regular backups** of database

### Connection Security

```python
# Use SSL for production
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

## Monitoring

### Health Checks

```bash
# Check database status
GET /health

# Returns database statistics
GET /api/v1/stats
```

### Logging

All database operations are logged:

```python
logger.info("Agent saved to database")
logger.error("Failed to save conversation")
logger.debug("Loaded agent from database")
```

## Future Enhancements

Planned improvements:

1. **Connection Pooling**: Advanced pool management
2. **Read Replicas**: Scale read operations
3. **Caching Layer**: Redis for frequently accessed data
4. **Analytics**: Query performance monitoring
5. **Backup Automation**: Scheduled backups
6. **Data Archival**: Archive old conversations

## Support

For issues or questions:

1. Check logs in `logs/backend.log`
2. Run test script: `python test_database.py`
3. Review this documentation
4. Check database connectivity

---

**Last Updated**: 2025-01-23
**Version**: 1.0.0
