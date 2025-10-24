"""
Database Models for Google ADK Integration
SQLAlchemy models for PostgreSQL persistence
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class AgentDB(Base):
    """Agent database model"""
    __tablename__ = "new_agent"
    
    agent_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, default="default_user")
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_type = Column(String(50), default="regular")  # regular, SequentialAgent, ParallelAgent, TeamAgent, react
    
    # Persona information (stored as JSON)
    persona_name = Column(String(255))
    persona_description = Column(Text)
    persona_personality = Column(Text)
    persona_expertise = Column(JSON)  # List of expertise areas
    persona_communication_style = Column(String(100))
    persona_language = Column(String(10))
    persona_custom_instructions = Column(Text)
    persona_examples = Column(JSON)  # List of example interactions
    
    # Configuration (stored as JSON)
    config = Column(JSON)  # Full config object
    
    # Tools and sub-agents
    tools = Column(JSON)  # List of tool names
    sub_agents = Column(JSON)  # List of sub-agent IDs for team agents
    
    # Planner configuration
    planner = Column(String(50))
    output_key = Column(String(100))
    
    # Metadata
    version = Column(String(20), default="1.0.0")
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    agent_metadata = Column(JSON)  # Additional metadata (renamed from 'metadata')
    
    # Relationships
    conversations = relationship("ConversationDB", back_populates="agent", cascade="all, delete-orphan")


class ConversationDB(Base):
    """Conversation database model"""
    __tablename__ = "new_conversations"
    
    conversation_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, default="default_user")
    agent_id = Column(String(255), ForeignKey("new_agent.agent_id"), nullable=False)
    session_id = Column(String(255))
    title = Column(String(500))
    
    # Conversation metadata
    status = Column(String(50), default="active")  # active, archived, deleted
    message_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime)
    
    # Additional metadata
    conversation_metadata = Column(JSON)
    
    # Relationships
    agent = relationship("AgentDB", back_populates="conversations")
    messages = relationship("MessageDB", back_populates="conversation", cascade="all, delete-orphan")


class MessageDB(Base):
    """Message database model"""
    __tablename__ = "new_messages"
    
    message_id = Column(String(255), primary_key=True)
    user_id = Column(String(255), nullable=False, default="default_user")
    conversation_id = Column(String(255), ForeignKey("new_conversations.conversation_id"), nullable=False)
    
    # Message content
    role = Column(String(50), nullable=False)  # user, assistant, system, tool
    content = Column(Text)
    
    # Message type and metadata
    message_type = Column(String(50))  # text, tool_call, tool_response, thinking, error
    tool_name = Column(String(255))
    tool_args = Column(JSON)
    tool_call_id = Column(String(255))
    
    # Streaming and processing
    is_streaming = Column(Boolean, default=False)
    is_complete = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Additional metadata
    message_metadata = Column(JSON)
    
    # Relationships
    conversation = relationship("ConversationDB", back_populates="messages")
