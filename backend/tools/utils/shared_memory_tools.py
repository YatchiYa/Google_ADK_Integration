"""
Shared Memory Tools for Google ADK
Tools that enable memory sharing between sessions and agents
"""

from typing import Dict, List, Any, Optional
from loguru import logger

# Global storage for memory manager and context
_memory_manager = None
_user_id = None
_agent_id = None

def _set_context(memory_manager, user_id: str, agent_id: str):
    """Set the context for shared memory tools"""
    global _memory_manager, _user_id, _agent_id
    _memory_manager = memory_manager
    _user_id = user_id
    _agent_id = agent_id

def shared_memory(content: str, scope: str = "user", importance: float = 0.8) -> str:
    """
    Create a shared memory entry that persists across sessions
    
    Args:
        content: Memory content to store
        scope: Memory scope ("user", "agent", "global")
        importance: Importance score (0.0-1.0)
        
    Returns:
        Success message with memory ID
    """
    try:
        if not _memory_manager or not _user_id or not _agent_id:
            return "❌ Memory system not properly initialized"
            
        memory_id = _memory_manager.create_shared_memory(
            user_id=_user_id,
            content=content,
            scope=scope,
            scope_id=_agent_id if scope == "agent" else None,
            metadata={
                "created_by_agent": _agent_id,
                "tool": "shared_memory"
            },
            importance=importance
        )
        
        logger.info(f"Created shared memory {memory_id} with scope '{scope}'")
        return f"✅ Created shared memory with ID: {memory_id}. Scope: {scope}. Content stored: {content[:50]}{'...' if len(content) > 50 else ''}"
        
    except Exception as e:
        logger.error(f"Failed to create shared memory: {e}")
        return f"❌ Failed to create shared memory: {str(e)}"

def search_shared_memory(query: str, scope: str = "user", limit: int = 5) -> str:
    """
    Search shared memories
    
    Args:
        query: Search query
        scope: Memory scope to search
        limit: Maximum results
        
    Returns:
        Formatted search results
    """
    try:
        if not _memory_manager or not _user_id:
            return "❌ Memory system not properly initialized"
            
        memories = _memory_manager.search_shared_memories(
            user_id=_user_id,
            query=query,
            scope=scope,
            limit=limit
        )
        
        if not memories:
            return f"🔍 No shared memories found for query '{query}' in scope '{scope}'"
        
        result = f"🧠 Found {len(memories)} shared memories:\n\n"
        for i, memory in enumerate(memories, 1):
            result += f"{i}. **{memory.content[:100]}{'...' if len(memory.content) > 100 else ''}**\n"
            result += f"   - Scope: {memory.metadata.get('scope', 'unknown')}\n"
            result += f"   - Importance: {memory.importance}\n"
            result += f"   - Created: {memory.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to search shared memories: {e}")
        return f"❌ Failed to search shared memories: {str(e)}"


def cross_agent_memory(query: str, limit: int = 10) -> str:
    """
    Search memories from other agents and sessions
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        Formatted memory results from other agents
    """
    try:
        if not _memory_manager or not _user_id:
            return "❌ Memory system not properly initialized"
            
        # Search regular memories from all agents
        regular_memories = _memory_manager.search_memories(
            user_id=_user_id,
            query=query,
            limit=limit//2
        )
        
        # Search shared memories
        shared_memories = _memory_manager.search_shared_memories(
            user_id=_user_id,
            query=query,
            scope="global",
            limit=limit//2
        )
        
        all_memories = regular_memories + shared_memories
        all_memories.sort(key=lambda x: (x.relevance_score or 0, x.importance), reverse=True)
        
        if not all_memories:
            return f"🔍 No cross-agent memories found for query '{query}'"
        
        result = f"🤝 Found {len(all_memories)} memories from other agents:\n\n"
        for i, memory in enumerate(all_memories[:limit], 1):
            memory_type = "Shared" if memory.metadata.get("type") == "shared_memory" else "Session"
            agent_info = f"Agent {memory.agent_id}" if memory.agent_id else "System"
            
            result += f"{i}. **[{memory_type}] {agent_info}**: {memory.content[:70]}{'...' if len(memory.content) > 70 else ''}\n"
            result += f"   - Relevance: {memory.relevance_score or 0:.2f} | Importance: {memory.importance}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get cross-agent memories: {e}")
        return f"❌ Failed to get cross-agent memories: {str(e)}"


def session_memory_bridge(limit: int = 10) -> str:
    """
    Access memories from other sessions with the same agent
    
    Args:
        limit: Maximum results
        
    Returns:
        Formatted session history
    """
    try:
        if not _memory_manager or not _user_id or not _agent_id:
            return "❌ Memory system not properly initialized"
            
        # Get all memories for this agent and user
        memories = _memory_manager.search_memories(
            user_id=_user_id,
            query="",  # Empty query to get all
            agent_id=_agent_id,
            limit=limit * 2  # Get more to filter
        )
        
        # Group by session
        session_groups = {}
        for memory in memories:
            if memory.session_id:
                if memory.session_id not in session_groups:
                    session_groups[memory.session_id] = []
                session_groups[memory.session_id].append(memory)
        
        if not session_groups:
            return f"📝 No previous session history found for agent {_agent_id}"
        
        result = f"📚 Session history for agent {_agent_id}:\n\n"
        
        for session_id, session_memories in list(session_groups.items())[:5]:  # Limit to 5 sessions
            result += f"**Session {session_id}:**\n"
            
            # Show key messages from session
            key_memories = sorted(session_memories, key=lambda x: x.importance, reverse=True)[:3]
            for memory in key_memories:
                role = memory.metadata.get('role', 'unknown')
                content_preview = memory.content[:60] + ('...' if len(memory.content) > 60 else '')
                result += f"  - {role}: {content_preview}\n"
            
            result += f"  - Total messages: {len(session_memories)}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get agent session history: {e}")
        return f"❌ Failed to get session history: {str(e)}"


def create_shared_memory_tools(memory_manager, user_id: str, agent_id: str) -> List:
    """Create all shared memory tools for an agent"""
    # Set the global context
    _set_context(memory_manager, user_id, agent_id)
    
    # Return the function objects
    return [
        shared_memory,
        search_shared_memory,
        cross_agent_memory,
        session_memory_bridge
    ]
