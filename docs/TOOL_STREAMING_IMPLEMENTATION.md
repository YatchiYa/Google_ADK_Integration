# Tool Streaming Implementation Guide

## 🎯 Overview

This document explains the implementation of **real-time streaming for tools** in the Google ADK Integration platform. The goal is to allow tools like `call_document_rag_code_civile_algerian` to stream their results chunk-by-chunk as they arrive, providing a better user experience.

---

## 📋 What We've Implemented

### 1. ✅ **Streaming Tool Function**
**File**: `/backend/tools/google_adk_tools.py`

Created a new streaming version of the RAG tool:

```python
def call_document_rag_code_civile_algerian_streaming(query: str, mode: str = "global", user_prompt: str = "expert in laws retrieving"):
    """
    STREAMING VERSION: Yields chunks as they arrive from the API
    """
    # ... setup code ...
    
    for line in response.iter_lines():
        if line:
            json_line = json.loads(line_str)
            
            # Handle references
            if 'references' in json_line:
                yield "__REFERENCES__" + json.dumps(references)
            
            # Handle response chunks - YIELD IMMEDIATELY
            if 'response' in json_line:
                chunk = json_line['response']
                yield chunk  # 🔥 Stream chunk to user
```

**Key Features**:
- ✅ Yields chunks as they arrive (not waiting for full response)
- ✅ Handles references separately
- ✅ Proper error handling
- ✅ Logging for debugging

---

### 2. ✅ **StreamingToolWrapper Class**
**File**: `/backend/tools/google_adk_tools.py`

Created a wrapper class that ADK can use:

```python
class StreamingToolWrapper(BaseTool):
    """
    Wrapper for streaming tools that yield chunks.
    """
    
    def __call__(self, *args, **kwargs) -> Generator[str, None, None]:
        """Execute the streaming tool and yield chunks."""
        for chunk in self.streaming_func(*args, **kwargs):
            yield chunk
```

**Why This Matters**:
- ADK expects tools to be `BaseTool` instances
- This wrapper makes generator functions compatible with ADK
- Allows proper tool registration and discovery

---

### 3. ✅ **Tool Registration**
**File**: `/backend/managers/tool_manager.py`

Registered both versions of the tool:

```python
# Non-streaming (backward compatibility)
self.register_tool(
    name="call_document_rag_code_civile_algerian",
    tool=call_document_rag_code_civile_algerian,
    description="Search Algerian Civil Code using RAG",
    category="document_rag"
)

# STREAMING version
streaming_rag_tool = StreamingToolWrapper(
    streaming_func=call_document_rag_code_civile_algerian_streaming,
    name="call_document_rag_code_civile_algerian_streaming",
    description="[STREAMING] Search Algerian Civil Code with real-time results"
)
self.register_tool(
    name="call_document_rag_code_civile_algerian_streaming",
    tool=streaming_rag_tool,
    description="[STREAMING] Search Algerian Civil Code with real-time results",
    category="document_rag",
    metadata={"streaming": True}
)
```

---

### 4. ✅ **New Event Type**
**File**: `/backend/managers/streaming_handler.py`

Added new event type for tool streaming:

```python
class StreamingEventType(Enum):
    # ... existing types ...
    TOOL_STREAM_CHUNK = "tool_stream_chunk"  # NEW!
```

---

## ⚠️ Current Limitations & Challenges

### **Challenge #1: ADK Tool Execution Model**

**The Problem**:
Google ADK's current architecture executes tools **synchronously** and waits for the complete result before continuing. Even though our tool is a generator that yields chunks, ADK will:

1. Call the tool
2. Collect ALL yielded chunks
3. Wait for the generator to complete
4. Return the full result as a single string
5. Continue with agent processing

**What This Means**:
- The tool DOES stream from the external API ✅
- But ADK doesn't forward those chunks to the user ❌
- User still sees the full result at once ❌

### **Challenge #2: ADK Runner Architecture**

The `Runner.run_async()` method in ADK doesn't currently support:
- Intercepting tool execution mid-stream
- Forwarding tool chunks to the streaming handler
- Partial tool results

### **Challenge #3: Function Response Format**

ADK expects tool responses in a specific format:
```python
FunctionResponse(
    name="tool_name",
    response={"result": "complete_result"}  # Must be complete!
)
```

There's no built-in way to send partial responses.

---

## 🔧 What Needs to Happen Next

### **Option 1: Modify ADK Runner (Complex)**

We would need to:

1. **Fork or extend ADK's Runner class**
2. **Intercept tool execution** before it completes
3. **Stream tool chunks** through the existing streaming pipeline
4. **Handle partial tool responses** in the agent's context

**Pros**:
- True real-time streaming
- Best user experience

**Cons**:
- Requires deep ADK modifications
- May break on ADK updates
- Complex to maintain

---

### **Option 2: Custom Tool Execution Hook (Moderate)**

Create a custom execution layer:

```python
class StreamingToolExecutor:
    """
    Custom executor that intercepts tool calls and streams results
    """
    
    async def execute_tool_with_streaming(self, tool_name, tool_args, session_id):
        # Check if tool supports streaming
        tool_info = tool_manager.get_tool_info(tool_name)
        
        if tool_info.metadata.get("streaming"):
            # Execute streaming version
            streaming_tool = tool_manager.get_tool(f"{tool_name}_streaming")
            
            # Yield chunks as they arrive
            for chunk in streaming_tool(**tool_args):
                yield StreamingEvent(
                    type=StreamingEventType.TOOL_STREAM_CHUNK,
                    content=chunk,
                    session_id=session_id,
                    metadata={"tool_name": tool_name}
                )
            
            # After completion, let ADK continue with full result
            full_result = accumulated_chunks
            return full_result
```

**Pros**:
- Less invasive than Option 1
- Can work alongside ADK
- Easier to maintain

**Cons**:
- Still requires hooking into ADK's execution flow
- May need to modify `streaming_handler.py`

---

### **Option 3: Post-Processing Stream (Simple)**

Simulate streaming by:

1. Tool executes normally (collects all chunks)
2. After tool completes, "replay" the chunks to the user
3. Add artificial delays to simulate streaming

**Pros**:
- Easy to implement
- No ADK modifications needed
- Works with current architecture

**Cons**:
- Not true real-time streaming
- User still waits for full tool execution
- Artificial delays feel fake

---

## 🎯 Recommended Approach

### **Hybrid Solution: Option 2 + Frontend Enhancement**

1. **Backend**: Implement custom tool execution hook
2. **Frontend**: Add visual indicator for streaming tools
3. **User Experience**: Show progress while tool executes

### **Implementation Steps**:

#### **Step 1: Modify Streaming Handler**

```python
# In streaming_handler.py

async def _handle_tool_execution(self, tool_call, session_id, agent_id):
    """
    Custom tool execution with streaming support
    """
    tool_name = tool_call.name
    tool_args = dict(tool_call.args)
    
    # Check if tool supports streaming
    tool_info = self.agent_manager.tool_manager.get_tool_info(tool_name)
    
    if tool_info and tool_info.metadata.get("streaming"):
        # Use streaming version
        streaming_tool_name = f"{tool_name}_streaming"
        streaming_tool = self.agent_manager.tool_manager.get_tool(streaming_tool_name)
        
        if streaming_tool:
            # Yield start event
            yield StreamingEvent(
                type=StreamingEventType.TOOL_CALL,
                content=f"🔧 Starting {tool_name}...",
                session_id=session_id,
                agent_id=agent_id,
                metadata={"tool_name": tool_name, "streaming": True}
            )
            
            # Stream chunks
            accumulated = ""
            for chunk in streaming_tool(**tool_args):
                accumulated += chunk
                yield StreamingEvent(
                    type=StreamingEventType.TOOL_STREAM_CHUNK,
                    content=chunk,
                    session_id=session_id,
                    agent_id=agent_id,
                    metadata={"tool_name": tool_name}
                )
            
            # Yield completion event
            yield StreamingEvent(
                type=StreamingEventType.TOOL_RESPONSE,
                content=f"✅ {tool_name} completed",
                session_id=session_id,
                agent_id=agent_id,
                metadata={"tool_name": tool_name, "result": accumulated}
            )
            
            return accumulated
    
    # Fallback to normal execution
    return None  # Let ADK handle it
```

#### **Step 2: Update Frontend**

```typescript
// In chat page

case 'tool_stream_chunk':
  // Append chunk to current tool response
  setMessages(prev => {
    const updated = [...prev];
    const lastMsg = updated[updated.length - 1];
    
    if (lastMsg && lastMsg.type === 'tool_response') {
      lastMsg.content += event.content;
    } else {
      // Create new tool response message
      updated.push({
        id: `tool-${Date.now()}`,
        type: 'tool_response',
        content: event.content,
        metadata: event.metadata,
        timestamp: new Date()
      });
    }
    
    return updated;
  });
  break;
```

#### **Step 3: Visual Indicator**

```tsx
{/* In StreamingEvent component */}
{metadata.streaming && (
  <div className="flex items-center space-x-2 text-blue-600">
    <div className="animate-pulse">⚡</div>
    <span className="text-xs">Streaming results...</span>
  </div>
)}
```

---

## 🚀 Testing the Implementation

### **Test 1: Verify Tool Registration**

```bash
# Check if streaming tool is registered
curl http://localhost:8000/api/v1/tools | jq '.[] | select(.name | contains("streaming"))'
```

Expected output:
```json
{
  "name": "call_document_rag_code_civile_algerian_streaming",
  "description": "[STREAMING] Search Algerian Civil Code...",
  "category": "document_rag",
  "metadata": {
    "streaming": true
  }
}
```

### **Test 2: Direct Tool Execution**

```python
# Test the streaming function directly
from tools.google_adk_tools import call_document_rag_code_civile_algerian_streaming

for chunk in call_document_rag_code_civile_algerian_streaming(
    query="What are the property rights in Algerian law?"
):
    print(chunk, end='', flush=True)
```

Expected: Chunks appear one by one (not all at once)

### **Test 3: Agent with Streaming Tool**

1. Create agent with streaming tool attached
2. Send query that triggers the tool
3. Monitor backend logs for `[STREAMING]` messages
4. Check if chunks are being yielded

---

## 📊 Current Status

### ✅ **Completed**
1. Streaming tool function created
2. StreamingToolWrapper class implemented
3. Tool registered in tool manager
4. New event type added
5. Documentation created

### ⏳ **In Progress**
1. Streaming handler modifications
2. Frontend chunk handling
3. Visual indicators

### ❌ **Blocked**
1. ADK Runner integration (requires deep modifications)
2. True real-time streaming (ADK limitation)

---

## 🎯 Next Steps

### **Immediate (Today)**
1. ✅ Complete tool registration
2. ⏳ Test direct tool execution
3. ⏳ Verify chunks are being generated

### **Short Term (This Week)**
1. ⏳ Implement custom tool execution hook
2. ⏳ Update frontend to handle tool chunks
3. ⏳ Add visual streaming indicators
4. ⏳ Test end-to-end streaming

### **Long Term (Next Week)**
1. ⏳ Research ADK Runner modifications
2. ⏳ Consider contributing to ADK for native streaming support
3. ⏳ Implement streaming for other tools

---

## 💡 Alternative: Server-Sent Events (SSE)

If ADK modifications prove too complex, we can:

1. **Bypass ADK for streaming tools**
2. **Use direct SSE connection** for tool execution
3. **Merge results** back into ADK flow

```python
@router.post("/api/v1/tools/{tool_name}/stream")
async def stream_tool_execution(tool_name: str, args: dict):
    """
    Direct SSE endpoint for streaming tools
    """
    async def event_generator():
        tool = tool_manager.get_tool(f"{tool_name}_streaming")
        
        for chunk in tool(**args):
            yield {
                "event": "chunk",
                "data": json.dumps({"content": chunk})
            }
        
        yield {
            "event": "complete",
            "data": json.dumps({"status": "done"})
        }
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

## 📝 Summary

### **What Works**
- ✅ Tool streams from external API
- ✅ Chunks are generated in real-time
- ✅ Tool is properly registered
- ✅ Wrapper class is functional

### **What Doesn't Work (Yet)**
- ❌ ADK doesn't forward chunks to user
- ❌ User sees full result at once
- ❌ No visual streaming indicator

### **The Core Issue**
Google ADK's architecture doesn't natively support streaming tool results. We need to either:
1. Modify ADK's Runner (complex)
2. Create custom execution layer (moderate)
3. Use SSE bypass (simple but hacky)

---

## 🔗 Related Files

- `/backend/tools/google_adk_tools.py` - Tool implementations
- `/backend/managers/tool_manager.py` - Tool registration
- `/backend/managers/streaming_handler.py` - Streaming logic
- `/backend/managers/agent_manager.py` - Agent execution
- `/frontend/src/app/chat/[agentId]/page.tsx` - Chat interface
- `/frontend/src/components/chat/StreamingEvent.tsx` - Event display

---

**Status**: 🟡 Partially Implemented - Tool streaming works, but ADK integration pending

**Next Action**: Implement custom tool execution hook in streaming handler

**Estimated Time**: 4-6 hours for full implementation

---

**Date**: October 23, 2025
**Version**: 1.0
