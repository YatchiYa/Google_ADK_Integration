"""
Conversation Management System for Google ADK
Handles chat conversations, message history, and session management
"""

import uuid
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from loguru import logger


class MessageRole(Enum):
    """Message roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Chat message data structure"""
    message_id: str
    role: MessageRole
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """Conversation data structure"""
    session_id: str
    user_id: str
    agent_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationManager:
    """
    Conversation management system
    Handles chat sessions, message history, and conversation persistence
    """
    
    def __init__(self, agent_manager, memory_manager, streaming_handler):
        """
        Initialize conversation manager
        
        Args:
            agent_manager: Agent manager instance
            memory_manager: Memory manager instance
            streaming_handler: Streaming handler instance
        """
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager
        self.streaming_handler = streaming_handler
        
        self._conversations: Dict[str, Conversation] = {}
        self._lock = Lock()
        
        logger.info("Conversation manager initialized")
    
    def start_conversation(self,
                          user_id: str,
                          agent_id: str,
                          initial_message: Optional[str] = None,
                          session_id: Optional[str] = None,
                          context: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new conversation
        
        Args:
            user_id: User identifier
            agent_id: Agent identifier
            initial_message: Optional initial message
            session_id: Optional custom session ID
            context: Optional conversation context
            
        Returns:
            str: Session ID
        """
        try:
            # Validate agent exists
            if not self.agent_manager.get_agent_info(agent_id):
                raise ValueError(f"Agent {agent_id} not found")
            
            # Generate session ID if not provided
            if not session_id:
                session_id = f"session_{uuid.uuid4().hex[:12]}"
            
            # Create conversation
            conversation = Conversation(
                session_id=session_id,
                user_id=user_id,
                agent_id=agent_id,
                metadata=context or {}
            )
            
            # Add initial message if provided
            if initial_message:
                message = Message(
                    message_id=str(uuid.uuid4()),
                    role=MessageRole.USER,
                    content=initial_message,
                    metadata={"is_initial": True}
                )
                conversation.messages.append(message)
            
            # Store conversation
            with self._lock:
                self._conversations[session_id] = conversation
            
            # Store in memory for context
            if initial_message:
                self.memory_manager.create_memory(
                    user_id=user_id,
                    content=f"Started conversation with {agent_id}: {initial_message}",
                    session_id=session_id,
                    agent_id=agent_id,
                    metadata={"type": "conversation_start"},
                    importance=0.8
                )
            
            logger.info(f"Started conversation {session_id} between user {user_id} and agent {agent_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise
    
    def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID"""
        with self._lock:
            return self._conversations.get(session_id)
    
    def add_message(self,
                   session_id: str,
                   role: MessageRole,
                   content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a message to conversation
        
        Args:
            session_id: Session identifier
            role: Message role
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            str: Message ID
        """
        try:
            with self._lock:
                conversation = self._conversations.get(session_id)
                if not conversation:
                    raise ValueError(f"Conversation {session_id} not found")
                
                # Create message
                message = Message(
                    message_id=str(uuid.uuid4()),
                    role=role,
                    content=content,
                    metadata=metadata or {}
                )
                
                # Add to conversation
                conversation.messages.append(message)
                conversation.updated_at = datetime.now()
                
                # Store in memory for context
                self.memory_manager.create_memory(
                    user_id=conversation.user_id,
                    content=f"{role.value}: {content}",
                    session_id=session_id,
                    agent_id=conversation.agent_id,
                    metadata={
                        "type": "conversation_message",
                        "role": role.value,
                        "message_id": message.message_id
                    },
                    importance=0.7 if role == MessageRole.USER else 0.6
                )
                
                logger.debug(f"Added {role.value} message to conversation {session_id}")
                return message.message_id
                
        except Exception as e:
            logger.error(f"Failed to add message to conversation: {e}")
            raise
    
    async def send_message(self,
                          session_id: str,
                          message: str,
                          metadata: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message and get streaming response
        
        Args:
            session_id: Session identifier
            message: User message
            metadata: Optional message metadata
            
        Yields:
            Dict containing streaming response data
        """
        try:
            conversation = self.get_conversation(session_id)
            if not conversation:
                raise ValueError(f"Conversation {session_id} not found")
            
            # Add user message
            user_message_id = self.add_message(
                session_id=session_id,
                role=MessageRole.USER,
                content=message,
                metadata=metadata
            )
            
            # Store user message in memory immediately
            try:
                memory_id = self.memory_manager.add_message_to_memory(
                    user_id=conversation.user_id,
                    session_id=session_id,
                    agent_id=conversation.agent_id,
                    role="user",
                    content=message,
                    metadata=metadata
                )
                logger.info(f"Stored user message in memory: {memory_id}")
            except Exception as e:
                logger.error(f"Failed to store user message in memory: {e}")
            
            # Get agent with updated tools for this user context
            agent = self.agent_manager.get_agent(conversation.agent_id)
            if not agent:
                raise ValueError(f"Agent {conversation.agent_id} not found")
            
            # Create agent with updated tools for this user context
            agent_info = self.agent_manager._agents.get(conversation.agent_id)
            if agent_info and agent_info.tools:
                # Get tools with proper user context for shared memory
                updated_tools = self.agent_manager.tool_manager.get_tools_for_agent(
                    tool_names=agent_info.tools,
                    agent_manager=self.agent_manager,
                    memory_manager=self.memory_manager,
                    user_id=conversation.user_id,
                    agent_id=conversation.agent_id
                )
                
                # Create a new agent instance with updated tools
                from google.adk.agents import LlmAgent
                from google.genai import types
                try:
                    from google.genai.models import LiteLlm
                except ImportError:
                    # Fallback for different ADK versions
                    LiteLlm = None
                
                # Build instruction
                instruction = self.agent_manager._build_instruction(agent_info.persona)
                
                # Create generate content config
                generate_config = types.GenerateContentConfig(
                    temperature=agent_info.config.temperature,
                    max_output_tokens=agent_info.config.max_output_tokens,
                    top_p=agent_info.config.top_p,
                    top_k=agent_info.config.top_k,
                    safety_settings=agent_info.config.safety_settings or []
                )
                
                # Create model
                if agent_info.config.model.startswith(("openai/", "anthropic/", "ollama/")) and LiteLlm:
                    model = LiteLlm(model=agent_info.config.model)
                else:
                    model = agent_info.config.model
                
                # Create new agent instance with updated tools
                agent = LlmAgent(
                    model=model,
                    name=conversation.agent_id,
                    description=agent_info.persona.description,
                    instruction=instruction,
                    tools=updated_tools,
                    generate_content_config=generate_config,
                    output_key=f"{conversation.agent_id}_response"
                )
                
                logger.info(f"Created agent instance with {len(updated_tools)} tools for conversation")
            
            # Get session context (conversation history from memory)
            session_context = self.memory_manager.get_session_context(
                user_id=conversation.user_id,
                session_id=session_id,
                agent_id=conversation.agent_id,
                limit=15
            )
            
            logger.info(f"Retrieved {len(session_context)} memory entries for session {session_id}")
            
            # Build context from session memory
            context_messages = []
            if session_context:
                for memory in session_context[-10:]:  # Last 10 messages
                    role = memory.metadata.get('role', 'unknown')
                    context_messages.append(f"{role}: {memory.content}")
                logger.info(f"Built context with {len(context_messages)} messages")
            
            # Build enhanced message with session context
            enhanced_message = message
            if context_messages:
                conversation_history = "\n".join(context_messages)
                enhanced_message = f"Previous conversation in this session:\n{conversation_history}\n\nCurrent message: {message}"
                logger.info(f"Enhanced message with context: {len(enhanced_message)} chars")
            else:
                logger.info("No session context found, using original message")
            
            # Start streaming response
            assistant_content = ""
            
            async for event in self.streaming_handler.start_streaming_session(
                session_id=session_id,
                agent_id=conversation.agent_id,
                user_id=conversation.user_id,
                agent=agent,
                message=enhanced_message
            ):
                # Collect assistant content
                if event.type.value == "content" and event.content:
                    assistant_content += event.content
                
                # Yield streaming event
                yield {
                    "type": event.type.value,
                    "content": event.content,
                    "metadata": event.metadata,
                    "timestamp": event.timestamp,
                    "session_id": session_id,
                    "message_id": user_message_id
                }
            
            # Add assistant response to conversation and memory
            if assistant_content.strip():
                assistant_message_id = self.add_message(
                    session_id=session_id,
                    role=MessageRole.ASSISTANT,
                    content=assistant_content.strip(),
                    metadata={"response_to": user_message_id}
                )
                
                # Store assistant response in memory immediately
                try:
                    memory_id = self.memory_manager.add_message_to_memory(
                        user_id=conversation.user_id,
                        session_id=session_id,
                        agent_id=conversation.agent_id,
                        role="assistant",
                        content=assistant_content.strip(),
                        metadata={"response_to": user_message_id}
                    )
                    logger.info(f"Stored assistant response in memory: {memory_id}")
                except Exception as e:
                    logger.error(f"Failed to store assistant response in memory: {e}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            yield {
                "type": "error",
                "content": f"Error: {str(e)}",
                "metadata": {"error_type": type(e).__name__},
                "timestamp": datetime.now().timestamp(),
                "session_id": session_id
            }
    
    def get_conversation_history(self,
                               session_id: str,
                               limit: Optional[int] = None,
                               offset: int = 0) -> List[Message]:
        """Get conversation message history"""
        conversation = self.get_conversation(session_id)
        if not conversation:
            return []
        
        messages = conversation.messages[offset:]
        if limit:
            messages = messages[:limit]
        
        return messages
    
    def list_conversations(self,
                         user_id: str,
                         agent_id: Optional[str] = None,
                         active_only: bool = True,
                         limit: int = 50,
                         offset: int = 0) -> List[Conversation]:
        """List conversations for a user"""
        with self._lock:
            conversations = []
            
            for conversation in self._conversations.values():
                # Filter by user
                if conversation.user_id != user_id:
                    continue
                
                # Filter by agent if specified
                if agent_id and conversation.agent_id != agent_id:
                    continue
                
                # Filter by active status
                if active_only and not conversation.is_active:
                    continue
                
                conversations.append(conversation)
            
            # Sort by updated time (most recent first)
            conversations.sort(key=lambda x: x.updated_at, reverse=True)
            
            # Apply pagination
            return conversations[offset:offset + limit]
    
    def search_conversations(self,
                           user_id: str,
                           query: str,
                           agent_id: Optional[str] = None,
                           limit: int = 20) -> List[Conversation]:
        """Search conversations by content"""
        query_lower = query.lower()
        matches = []
        
        with self._lock:
            for conversation in self._conversations.values():
                # Filter by user
                if conversation.user_id != user_id:
                    continue
                
                # Filter by agent if specified
                if agent_id and conversation.agent_id != agent_id:
                    continue
                
                # Search in messages
                for message in conversation.messages:
                    if query_lower in message.content.lower():
                        matches.append(conversation)
                        break
        
        # Sort by relevance (number of matching messages) and recency
        def relevance_score(conv):
            match_count = sum(1 for msg in conv.messages if query_lower in msg.content.lower())
            recency_score = conv.updated_at.timestamp()
            return (match_count, recency_score)
        
        matches.sort(key=relevance_score, reverse=True)
        return matches[:limit]
    
    def update_conversation_metadata(self,
                                   session_id: str,
                                   metadata: Dict[str, Any]) -> bool:
        """Update conversation metadata"""
        try:
            with self._lock:
                conversation = self._conversations.get(session_id)
                if not conversation:
                    return False
                
                conversation.metadata.update(metadata)
                conversation.updated_at = datetime.now()
                
                logger.debug(f"Updated metadata for conversation {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update conversation metadata: {e}")
            return False
    
    def end_conversation(self, session_id: str) -> bool:
        """End a conversation"""
        try:
            with self._lock:
                conversation = self._conversations.get(session_id)
                if not conversation:
                    return False
                
                conversation.is_active = False
                conversation.updated_at = datetime.now()
                
                # Store conversation summary in memory
                if conversation.messages:
                    message_count = len(conversation.messages)
                    last_message = conversation.messages[-1].content[:100] if conversation.messages else ""
                    
                    self.memory_manager.create_memory(
                        user_id=conversation.user_id,
                        content=f"Ended conversation with {conversation.agent_id}. {message_count} messages exchanged. Last: {last_message}",
                        session_id=session_id,
                        agent_id=conversation.agent_id,
                        metadata={
                            "type": "conversation_end",
                            "message_count": message_count,
                            "duration_minutes": (conversation.updated_at - conversation.created_at).total_seconds() / 60
                        },
                        importance=0.6
                    )
                
                logger.info(f"Ended conversation {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to end conversation: {e}")
            return False
    
    def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation permanently"""
        try:
            with self._lock:
                if session_id in self._conversations:
                    del self._conversations[session_id]
                    logger.info(f"Deleted conversation {session_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")
            return False
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        with self._lock:
            total_conversations = len(self._conversations)
            active_conversations = sum(1 for c in self._conversations.values() if c.is_active)
            
            # Message statistics
            total_messages = sum(len(c.messages) for c in self._conversations.values())
            
            # User statistics
            user_stats = {}
            for conversation in self._conversations.values():
                user_id = conversation.user_id
                user_stats[user_id] = user_stats.get(user_id, 0) + 1
            
            # Agent statistics
            agent_stats = {}
            for conversation in self._conversations.values():
                agent_id = conversation.agent_id
                agent_stats[agent_id] = agent_stats.get(agent_id, 0) + 1
            
            # Average conversation length
            conversation_lengths = [len(c.messages) for c in self._conversations.values()]
            avg_length = sum(conversation_lengths) / len(conversation_lengths) if conversation_lengths else 0
            
            return {
                "total_conversations": total_conversations,
                "active_conversations": active_conversations,
                "inactive_conversations": total_conversations - active_conversations,
                "total_messages": total_messages,
                "average_conversation_length": round(avg_length, 1),
                "conversations_by_user": dict(sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
                "conversations_by_agent": dict(sorted(agent_stats.items(), key=lambda x: x[1], reverse=True)[:10])
            }
    
    def export_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export conversation data"""
        conversation = self.get_conversation(session_id)
        if not conversation:
            return None
        
        return {
            "session_id": conversation.session_id,
            "user_id": conversation.user_id,
            "agent_id": conversation.agent_id,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "is_active": conversation.is_active,
            "metadata": conversation.metadata,
            "messages": [
                {
                    "message_id": msg.message_id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "metadata": msg.metadata,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in conversation.messages
            ],
            "exported_at": datetime.now().isoformat()
        }
    
    def import_conversation(self, conversation_data: Dict[str, Any]) -> Optional[str]:
        """Import conversation from data"""
        try:
            session_id = conversation_data["session_id"]
            
            # Create conversation
            conversation = Conversation(
                session_id=session_id,
                user_id=conversation_data["user_id"],
                agent_id=conversation_data["agent_id"],
                created_at=datetime.fromisoformat(conversation_data["created_at"]),
                updated_at=datetime.fromisoformat(conversation_data["updated_at"]),
                is_active=conversation_data.get("is_active", True),
                metadata=conversation_data.get("metadata", {})
            )
            
            # Import messages
            for msg_data in conversation_data.get("messages", []):
                message = Message(
                    message_id=msg_data["message_id"],
                    role=MessageRole(msg_data["role"]),
                    content=msg_data["content"],
                    metadata=msg_data.get("metadata", {}),
                    timestamp=datetime.fromisoformat(msg_data["timestamp"])
                )
                conversation.messages.append(message)
            
            # Store conversation
            with self._lock:
                self._conversations[session_id] = conversation
            
            logger.info(f"Imported conversation {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to import conversation: {e}")
            return None
    
    def cleanup_old_conversations(self, days: int = 30, keep_active: bool = True) -> int:
        """Clean up old conversations"""
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            with self._lock:
                sessions_to_delete = []
                
                for session_id, conversation in self._conversations.items():
                    # Skip active conversations if requested
                    if keep_active and conversation.is_active:
                        continue
                    
                    # Delete if older than cutoff
                    if conversation.updated_at < cutoff_date:
                        sessions_to_delete.append(session_id)
                
                # Delete conversations
                for session_id in sessions_to_delete:
                    del self._conversations[session_id]
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old conversations")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old conversations: {e}")
            return 0
