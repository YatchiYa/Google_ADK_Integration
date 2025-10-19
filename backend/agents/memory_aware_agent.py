"""
Memory-Aware Agent for Google ADK
Demonstrates proper cross-session memory management following ADK patterns
"""

from google.adk.agents import LlmAgent
from tools.memory_tools import search_user_memory, get_user_profile, get_session_history


def create_memory_aware_agent():
    """
    Create an agent with memory capabilities following Google ADK patterns.
    
    This agent can:
    1. Remember information within the current session (automatic)
    2. Search across past sessions for relevant information (via tools)
    3. Retrieve user profile information from memory
    4. Access complete session histories
    """
    
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="MemoryAwareAgent",
        
        instruction="""
        You are a memory-aware conversational agent that can remember and recall information across sessions.
        
        MEMORY CAPABILITIES:
        1. CURRENT SESSION: You automatically have access to the current conversation history
        2. CROSS-SESSION: Use tools to search past conversations and user information
        3. USER PROFILE: Use get_user_profile to learn about the user from past interactions
        4. SESSION HISTORY: Use get_session_history to review specific past sessions
        
        WHEN TO USE MEMORY TOOLS:
        - When user asks "Do you remember me?" or similar
        - When user references past conversations
        - When you need context about the user's background, preferences, or history
        - When user asks about previous sessions or topics
        
        MEMORY TOOL USAGE:
        - search_user_memory(query): Search for specific information across all user's sessions
        - get_user_profile(): Get comprehensive user information from memory
        - get_session_history(session_id): Get complete history of a specific session
        
        RESPONSE GUIDELINES:
        - Always acknowledge when you're using memory to recall information
        - Be specific about what you remember and from which context
        - If memory tools return no results, be honest about not having that information
        - Use memory proactively to provide personalized responses
        
        EXAMPLE USAGE:
        User: "Do you remember what I told you about my job?"
        You: Let me search my memory for information about your job... [use search_user_memory]
        
        User: "What do you know about me?"
        You: Let me retrieve your profile from our past conversations... [use get_user_profile]
        """,
        
        tools=[
            search_user_memory,
            get_user_profile,
            get_session_history
        ]
    )
    
    return agent


# Export for use in the application
memory_aware_agent = create_memory_aware_agent()
