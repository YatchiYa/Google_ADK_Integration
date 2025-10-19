"""
Memory Tools for Google ADK
Provides tools for agents to search and retrieve cross-session memories
Following Google ADK patterns for memory management
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
from loguru import logger


@dataclass
class MemorySearchResult:
    """Result from memory search operation"""
    content: str
    session_id: str
    agent_id: str
    relevance_score: float
    created_at: str
    metadata: Dict[str, Any]
    tags: List[str]


def search_user_memory(
    query: str,
    limit: int = 5,
    min_relevance: float = 0.2,
    memory_manager=None,
    user_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search user's cross-session memory for relevant information.
    
    This tool allows agents to retrieve information from past conversations
    with the same user, following Google ADK memory patterns.
    
    Args:
        query: Search query to find relevant memories
        limit: Maximum number of results to return
        min_relevance: Minimum relevance score (0.0 to 1.0)
        memory_manager: Memory manager instance (injected by framework)
        user_id: User ID (injected by framework)
        
    Returns:
        Dict containing search results and metadata
    """
    try:
        if not memory_manager:
            return {
                "success": False,
                "error": "Memory manager not available",
                "memories": []
            }
        
        if not user_id:
            return {
                "success": False,
                "error": "User ID not available",
                "memories": []
            }
        
        # Search memories for this user
        memories = memory_manager.search_memories(
            user_id=user_id,
            query=query,
            limit=limit,
            min_relevance=min_relevance
        )
        
        # Convert to search results
        results = []
        for memory in memories:
            result = MemorySearchResult(
                content=memory.content,
                session_id=memory.session_id or "unknown",
                agent_id=memory.agent_id or "unknown",
                relevance_score=memory.relevance_score or 0.0,
                created_at=memory.created_at.isoformat() if memory.created_at else "",
                metadata=memory.metadata,
                tags=memory.tags
            )
            results.append(result)
        
        # Format results for agent consumption
        formatted_memories = []
        for result in results:
            # Determine the role from tags or metadata
            role = "unknown"
            if "user" in result.tags:
                role = "user"
            elif "assistant" in result.tags:
                role = "assistant"
            elif result.metadata.get("role"):
                role = result.metadata["role"]
            
            formatted_memories.append({
                "content": result.content,
                "role": role,
                "session": result.session_id,
                "relevance": result.relevance_score,
                "date": result.created_at
            })
        
        logger.info(f"Memory search for '{query}' returned {len(formatted_memories)} results")
        
        return {
            "success": True,
            "query": query,
            "total_results": len(formatted_memories),
            "memories": formatted_memories,
            "message": f"Found {len(formatted_memories)} relevant memories for query: {query}"
        }
        
    except Exception as e:
        logger.error(f"Error searching user memory: {e}")
        return {
            "success": False,
            "error": str(e),
            "memories": []
        }


def get_user_profile(
    memory_manager=None,
    user_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve user profile information from memory.
    
    This tool searches for user information across all sessions to build
    a profile of the user based on what they've shared.
    
    Args:
        memory_manager: Memory manager instance (injected by framework)
        user_id: User ID (injected by framework)
        
    Returns:
        Dict containing user profile information
    """
    try:
        if not memory_manager or not user_id:
            return {
                "success": False,
                "error": "Memory manager or user ID not available",
                "profile": {}
            }
        
        # Search for user information using common patterns
        user_info_queries = [
            "my name",
            "I am",
            "I work",
            "I specialize",
            "my job",
            "my background"
        ]
        
        all_user_info = []
        for query in user_info_queries:
            memories = memory_manager.search_memories(
                user_id=user_id,
                query=query,
                limit=10,
                min_relevance=0.1
            )
            
            # Filter for user messages containing personal information
            for memory in memories:
                if ("user" in memory.tags and 
                    any(keyword in memory.content.lower() for keyword in 
                        ['my name', 'i am', 'i work', 'i specialize', 'my job', 'my background'])):
                    all_user_info.append({
                        "content": memory.content,
                        "session": memory.session_id,
                        "date": memory.created_at.isoformat() if memory.created_at else ""
                    })
        
        # Remove duplicates and sort by date
        unique_info = []
        seen_content = set()
        for info in all_user_info:
            if info["content"] not in seen_content:
                unique_info.append(info)
                seen_content.add(info["content"])
        
        # Sort by date (most recent first)
        unique_info.sort(key=lambda x: x["date"], reverse=True)
        
        logger.info(f"Retrieved user profile with {len(unique_info)} pieces of information")
        
        return {
            "success": True,
            "user_id": user_id,
            "profile_entries": unique_info[:5],  # Top 5 most recent
            "total_entries": len(unique_info),
            "message": f"Found {len(unique_info)} pieces of user information"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user profile: {e}")
        return {
            "success": False,
            "error": str(e),
            "profile": {}
        }


def get_session_history(
    session_id: str = None,
    memory_manager=None,
    user_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve complete history for a specific session.
    
    Args:
        session_id: Session ID to retrieve history for
        memory_manager: Memory manager instance (injected by framework)
        user_id: User ID (injected by framework)
        
    Returns:
        Dict containing session history
    """
    try:
        if not memory_manager or not user_id:
            return {
                "success": False,
                "error": "Memory manager or user ID not available",
                "history": []
            }
        
        if not session_id:
            return {
                "success": False,
                "error": "Session ID is required",
                "history": []
            }
        
        # Get all memories for this session
        memories = memory_manager.search_memories(
            user_id=user_id,
            query="",  # Empty query to get all
            session_id=session_id,
            limit=100,
            min_relevance=0.0
        )
        
        # Sort by creation time
        memories.sort(key=lambda x: x.created_at if x.created_at else "")
        
        # Format history
        history = []
        for memory in memories:
            role = "unknown"
            if "user" in memory.tags:
                role = "user"
            elif "assistant" in memory.tags:
                role = "assistant"
            elif memory.metadata.get("role"):
                role = memory.metadata["role"]
            
            history.append({
                "role": role,
                "content": memory.content,
                "timestamp": memory.created_at.isoformat() if memory.created_at else "",
                "metadata": memory.metadata
            })
        
        logger.info(f"Retrieved session history for {session_id} with {len(history)} entries")
        
        return {
            "success": True,
            "session_id": session_id,
            "history": history,
            "total_entries": len(history),
            "message": f"Retrieved {len(history)} entries from session {session_id}"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving session history: {e}")
        return {
            "success": False,
            "error": str(e),
            "history": []
        }
