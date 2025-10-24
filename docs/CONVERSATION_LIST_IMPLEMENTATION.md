# Conversation List Implementation Guide

## Issue: Conversation List Not Loading

The conversation list in the sidebar is currently empty because the API endpoint doesn't exist yet.

## Solution: Implement Conversation Loading

### Step 1: Add Backend Endpoint

Add this to `/backend/routers/conversations.py`:

```python
@router.get("/agent/{agent_id}", response_model=List[ConversationResponse])
async def get_agent_conversations(
    agent_id: str,
    limit: int = Query(50, ge=1, le=100),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for a specific agent"""
    try:
        # Check permissions
        if not require_permission(current_user, "conversations:read"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get conversations from database
        if conversation_manager.db_service:
            db_conversations = conversation_manager.db_service.get_agent_conversations(
                agent_id, 
                limit=limit
            )
            
            conversations = []
            for db_conv in db_conversations:
                # Load messages
                db_messages = conversation_manager.db_service.get_conversation_messages(
                    db_conv.conversation_id,
                    limit=10  # Last 10 messages for preview
                )
                
                messages = []
                for db_msg in db_messages:
                    message_model = MessageModel(
                        role=MessageRole(db_msg.role),
                        content=db_msg.content or "",
                        metadata=db_msg.message_metadata or {},
                        timestamp=db_msg.created_at
                    )
                    messages.append(message_model)
                
                conv_response = ConversationResponse(
                    session_id=db_conv.conversation_id,
                    user_id="default_user",
                    agent_id=db_conv.agent_id,
                    messages=messages,
                    created_at=db_conv.created_at,
                    updated_at=db_conv.updated_at,
                    is_active=db_conv.status == "active",
                    metadata=db_conv.conversation_metadata or {}
                )
                conversations.append(conv_response)
            
            return conversations
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting agent conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 2: Add Frontend Service Method

Add this to `/frontend/src/services/chat.service.ts`:

```typescript
static async getConversations(agentId: string): Promise<ChatSession[]> {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(
      `${API_URL}/conversations/agent/${agentId}`,
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to load conversations");
    }

    const data = await response.json();
    
    // Transform to ChatSession format
    return data.map((conv: any) => ({
      id: conv.session_id,
      agent_id: conv.agent_id,
      user_id: conv.user_id,
      created_at: new Date(conv.created_at),
      updated_at: new Date(conv.updated_at),
      is_active: conv.is_active,
      messages: conv.messages || [],
    }));
  } catch (error) {
    console.error("Error loading conversations:", error);
    return [];
  }
}
```

### Step 3: Update Chat Page

The `loadConversations` function is already in place in `page-enhanced.tsx`:

```typescript
const loadConversations = async () => {
  try {
    const convs = await ChatService.getConversations(agentId);
    setConversations(convs);
  } catch (error) {
    console.error("Failed to load conversations:", error);
  }
};
```

Just uncomment the API call!

### Step 4: Add Conversation Selection

Update the `onConversationSelect` handler in `page-enhanced.tsx`:

```typescript
const handleConversationSelect = async (conversationId: string) => {
  try {
    // Load conversation from API
    const conversation = await ChatService.getConversation(conversationId);
    
    // Set session and messages
    setSession({
      id: conversation.session_id,
      agent_id: conversation.agent_id,
      user_id: conversation.user_id,
      created_at: conversation.created_at,
      updated_at: conversation.updated_at,
      is_active: conversation.is_active,
      messages: [],
    });
    
    // Set messages
    setMessages(conversation.messages);
    
    // Close sidebar
    setSidebarOpen(false);
  } catch (error) {
    console.error("Failed to load conversation:", error);
    setError("Failed to load conversation");
  }
};
```

And update the ChatSidebar call:

```typescript
<ChatSidebar
  agents={availableAgents}
  conversations={conversations}
  currentAgentId={agentId}
  onAgentSelect={handleAgentSelect}
  onNewChat={handleNewChat}
  onConversationSelect={handleConversationSelect}  // Updated
  isOpen={sidebarOpen}
  onClose={() => setSidebarOpen(false)}
/>
```

### Step 5: Add Conversation Title Generation

Optionally, add a title to conversations based on first message:

```typescript
// In backend when creating conversation
const generateConversationTitle = (firstMessage: string): string => {
  // Take first 50 characters of first message
  const title = firstMessage.substring(0, 50);
  return title.length < firstMessage.length ? `${title}...` : title;
};

// When saving conversation
conversation_data = {
  "conversation_id": session_id,
  "agent_id": agent_id,
  "title": generateConversationTitle(initial_message),
  // ... rest of data
}
```

### Step 6: Update ChatSidebar to Show Titles

Update `/frontend/src/components/chat/ChatSidebar.tsx`:

```typescript
{conversations.map((conv) => (
  <button
    key={conv.id}
    onClick={() => onConversationSelect(conv.id)}
    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors text-left"
  >
    <FaComment className="text-sm flex-shrink-0" />
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium truncate">
        {/* Show title if available, otherwise show ID */}
        {conv.messages && conv.messages.length > 0
          ? conv.messages[0].content.substring(0, 30) + "..."
          : conv.id.slice(-8)}
      </p>
      <p className="text-xs text-gray-500 truncate">
        {new Date(conv.created_at).toLocaleDateString()}
      </p>
    </div>
  </button>
))}
```

## Quick Test

### 1. Add Backend Endpoint
```bash
# Edit backend/routers/conversations.py
# Add the get_agent_conversations endpoint
```

### 2. Test Endpoint
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/agent/your_agent_id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Update Frontend
```bash
# Edit frontend/src/services/chat.service.ts
# Add getConversations method
```

### 4. Uncomment in Chat Page
```typescript
// In loadConversations function
const convs = await ChatService.getConversations(agentId);
setConversations(convs);
```

### 5. Test in Browser
- Open chat page
- Check sidebar for conversation list
- Click on a conversation to load it

## Expected Result

After implementation, you should see:
- ✅ List of conversations in sidebar
- ✅ Conversation titles (first message preview)
- ✅ Creation dates
- ✅ Click to load conversation
- ✅ Messages load from database

## Troubleshooting

### No Conversations Showing
1. Check if conversations exist in database:
   ```sql
   SELECT * FROM new_conversations WHERE agent_id = 'your_agent_id';
   ```

2. Check API response:
   ```bash
   curl http://localhost:8000/api/v1/conversations/agent/your_agent_id
   ```

3. Check browser console for errors

### Conversations Not Loading
1. Verify token is valid
2. Check network tab for API call
3. Check backend logs for errors
4. Verify conversation_id format

---

**Status**: Ready to Implement
**Estimated Time**: 15-30 minutes
**Difficulty**: Easy
