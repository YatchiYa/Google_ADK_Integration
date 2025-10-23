# Quick Start Guide - Database Integration

## 🚀 Get Started in 5 Minutes

### Step 1: Verify Database Connection

Your database credentials are already configured:

```
DATABASE_URL=postgresql://de:de@130de9.32:5432/de
```

### Step 2: Test Database Integration

```bash
cd backend
python test_database.py
```

**Expected Output:**

```
✅ Database service initialized successfully
✅ Created agent: agent_xxxxx
✅ Agent found in database
✅ Created conversation: test_conv_001
✅ All tests completed!
```

### Step 3: Start the Backend

```bash
cd backend
python main.py
```

**Look for:**

```
✅ Database service initialized
✅ All managers initialized successfully
Loading X agents from database
```

### Step 4: Create an Agent (Saved to DB Automatically)

```bash
curl -X POST http://localhost:8000/api/v1/agents/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My First Agent",
    "persona": {
      "name": "Assistant",
      "description": "A helpful assistant",
      "personality": "friendly",
      "expertise": ["general"],
      "communication_style": "professional",
      "language": "en",
      "custom_instructions": "",
      "examples": []
    },
    "tools": ["google_search"]
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "Agent 'My First Agent' created successfully with ID: agent_xxxxx"
}
```

### Step 5: Verify Agent in Database

```bash
# List all agents (from database)
curl http://localhost:8000/api/v1/agents/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 6: Test On-Demand Loading

1. **Restart the backend**:

   ```bash
   # Stop with Ctrl+C
   python main.py
   ```

2. **Start a conversation** (agent loads from DB automatically):
   ```bash
   curl -X POST http://localhost:8000/api/v1/streaming/start \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "user_id": "user_123",
       "agent_id": "agent_xxxxx",
       "message": "Hello!"
     }'
   ```

**Backend logs will show:**

```
Loaded agent agent_xxxxx from database on-demand
Created ADK instance for agent agent_xxxxx
```

## ✅ What Just Happened?

1. ✅ **Database tables created** automatically
2. ✅ **Agent saved** to database when created
3. ✅ **Agent loaded** from database on server restart
4. ✅ **Conversation saved** to database when started
5. ✅ **Messages saved** to database as they're sent

## 🎯 Key Features Working

### Automatic Persistence

- All agents saved to `new_agent` table
- All conversations saved to `new_conversations` table
- All messages saved to `new_messages` table

### Lazy Loading

- Agents loaded from DB on first access
- Conversations loaded from DB when requested
- Memory caching for performance

### On-Demand Creation

- Agents created from DB when streaming starts
- No need to pre-load all agents
- Efficient memory usage

## 📊 Check Database Stats

```bash
curl http://localhost:8000/health
```

Or directly query the database:

```sql
-- Connect to database
psql -h 130.211.99.32 -U postgres -d ia-lawyer

-- Check agents
SELECT agent_id, name, created_at FROM new_agent;

-- Check conversations
SELECT conversation_id, agent_id, message_count FROM new_conversations;

-- Check messages
SELECT message_id, role, content FROM new_messages LIMIT 10;
```

## 🔍 Verify Everything Works

### Test 1: Agent Persistence

```bash
# Create agent
curl -X POST http://localhost:8000/api/v1/agents/ ...

# Restart backend
# Ctrl+C, then: python main.py

# List agents (should show agent from DB)
curl http://localhost:8000/api/v1/agents/ ...
```

### Test 2: Conversation Persistence

```bash
# Start conversation
curl -X POST http://localhost:8000/api/v1/streaming/start ...

# Get conversation (from DB)
curl http://localhost:8000/api/v1/conversations/{session_id} ...
```

### Test 3: Message Persistence

```bash
# Send messages in conversation
# Check database:
SELECT * FROM new_messages WHERE conversation_id = 'session_id';
```

## 🐛 Troubleshooting

### Issue: "Database connection failed"

**Solution:**

```bash
# Test database connection
psql -h 130.211.99.32 -U postgres -d ia-lawyer

# If fails, check:
# 1. Database is running
# 2. Credentials are correct
# 3. Network access allowed
```

### Issue: "Agent not found"

**Solution:**

```bash
# Check agent exists in database
psql -h 130.211.99.32 -U postgres -d ia-lawyer
SELECT agent_id, name FROM new_agent;

# Check backend logs
tail -f logs/backend.log | grep -i agent
```

### Issue: "Tables don't exist"

**Solution:**

```bash
# Tables are created automatically on startup
# Check logs for:
✅ Database tables created/verified

# If not created, check database permissions
```

## 📝 Common Tasks

### View All Agents in Database

```sql
SELECT
    agent_id,
    name,
    agent_type,
    tools,
    usage_count,
    created_at
FROM new_agent
WHERE is_active = true;
```

### View All Conversations

```sql
SELECT
    c.conversation_id,
    c.agent_id,
    a.name as agent_name,
    c.message_count,
    c.created_at
FROM new_conversations c
JOIN new_agent a ON c.agent_id = a.agent_id
WHERE c.status = 'active'
ORDER BY c.created_at DESC;
```

### View Conversation Messages

```sql
SELECT
    message_id,
    role,
    content,
    message_type,
    created_at
FROM new_messages
WHERE conversation_id = 'your_session_id'
ORDER BY created_at ASC;
```

## 🎉 Success Indicators

You know it's working when:

✅ Backend logs show: "✅ Database service initialized"
✅ Backend logs show: "Loading X agents from database"
✅ Agents persist across server restarts
✅ Conversations saved to database
✅ Messages appear in database immediately
✅ On-demand agent loading works

## 📚 Next Steps

1. **Read Full Documentation**: `backend/DATABASE_INTEGRATION.md`
2. **Review Implementation**: `IMPLEMENTATION_SUMMARY.md`
3. **Explore Database Schema**: Check table structures
4. **Monitor Performance**: Watch database query logs
5. **Set Up Backups**: Configure automated backups

## 💡 Pro Tips

1. **Monitor Logs**: Always check logs for database operations
2. **Use Test Script**: Run `test_database.py` regularly
3. **Check Stats**: Use `/health` endpoint for quick stats
4. **Database Queries**: Use psql for direct database inspection
5. **Backup Regularly**: Set up automated database backups

## 🆘 Need Help?

1. **Check Logs**: `tail -f logs/backend.log`
2. **Run Tests**: `python test_database.py`
3. **Review Docs**: `backend/DATABASE_INTEGRATION.md`
4. **Check Database**: `psql -h 130.211.99.32 -U postgres -d ia-lawyer`

---

**Ready to go!** Your Google ADK Integration now has full database persistence. 🎉
