"""
Database Service for Google ADK Integration
Handles all database operations with PostgreSQL
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from loguru import logger

from models.db_models import Base, AgentDB, ConversationDB, MessageDB


class DatabaseService:
    """Database service for PostgreSQL operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database service
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:NAJOYA959697@130.211.99.32:5432/ia-lawyer"
        )
        
        logger.info(f"Initializing database service with URL: {self.database_url.split('@')[1] if '@' in self.database_url else 'local'}")
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            poolclass=NullPool,  # Disable connection pooling for simplicity
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self._create_tables()
        
        logger.info("Database service initialized successfully")
    
    def _create_tables(self):
        """Create all tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    # ==================== AGENT OPERATIONS ====================
    
    def save_agent(self, agent_data: Dict[str, Any]) -> AgentDB:
        """
        Save or update an agent in the database
        
        Args:
            agent_data: Agent data dictionary
            
        Returns:
            AgentDB: Saved agent model
        """
        session = self.get_session()
        try:
            agent_id = agent_data.get("agent_id")
            
            # Check if agent exists
            existing_agent = session.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
            
            if existing_agent:
                # Update existing agent
                for key, value in agent_data.items():
                    if hasattr(existing_agent, key):
                        setattr(existing_agent, key, value)
                logger.info(f"Updated agent: {agent_id}")
            else:
                # Create new agent
                agent = AgentDB(**agent_data)
                session.add(agent)
                logger.info(f"Created new agent: {agent_id}")
            
            session.commit()
            
            if existing_agent:
                session.refresh(existing_agent)
                return existing_agent
            else:
                session.refresh(agent)
                return agent
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving agent: {e}")
            raise
        finally:
            session.close()
    
    def get_agent(self, agent_id: str) -> Optional[AgentDB]:
        """
        Get an agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Optional[AgentDB]: Agent model or None
        """
        session = self.get_session()
        try:
            agent = session.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
            return agent
        finally:
            session.close()
    
    def get_all_agents(self, include_inactive: bool = False) -> List[AgentDB]:
        """
        Get all agents
        
        Args:
            include_inactive: Include inactive agents
            
        Returns:
            List[AgentDB]: List of agents
        """
        session = self.get_session()
        try:
            query = session.query(AgentDB)
            if not include_inactive:
                query = query.filter(AgentDB.is_active == True)
            agents = query.order_by(AgentDB.created_at.desc()).all()
            return agents
        finally:
            session.close()
    
    def update_agent(self, agent_id: str, updates: dict) -> bool:
        """
        Update agent fields in database
        
        Args:
            agent_id: Agent ID
            updates: Dictionary of fields to update
            
        Returns:
            bool: Success status
        """
        session = self.get_session()
        try:
            agent = session.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
            if not agent:
                logger.warning(f"Agent {agent_id} not found for update")
                return False
            
            # Update allowed fields
            for key, value in updates.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)
                    logger.debug(f"Updated agent {agent_id} field '{key}' to: {value}")
            
            session.commit()
            logger.info(f"Updated agent {agent_id} with fields: {list(updates.keys())}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise
        finally:
            session.close()
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent (soft delete by setting is_active=False)
        
        Args:
            agent_id: Agent ID
            
        Returns:
            bool: Success status
        """
        session = self.get_session()
        try:
            agent = session.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
            if agent:
                agent.is_active = False
                session.commit()
                logger.info(f"Deleted agent: {agent_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting agent: {e}")
            raise
        finally:
            session.close()
    
    def update_agent_usage(self, agent_id: str):
        """
        Update agent usage statistics
        
        Args:
            agent_id: Agent ID
        """
        session = self.get_session()
        try:
            agent = session.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
            if agent:
                agent.usage_count += 1
                agent.last_used = datetime.utcnow()
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating agent usage: {e}")
        finally:
            session.close()
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def save_conversation(self, conversation_data: Dict[str, Any]) -> ConversationDB:
        """
        Save or update a conversation
        
        Args:
            conversation_data: Conversation data dictionary
            
        Returns:
            ConversationDB: Saved conversation model
        """
        session = self.get_session()
        try:
            conversation_id = conversation_data.get("conversation_id")
            
            # Check if conversation exists
            existing_conv = session.query(ConversationDB).filter(
                ConversationDB.conversation_id == conversation_id
            ).first()
            
            if existing_conv:
                # Update existing conversation
                for key, value in conversation_data.items():
                    if hasattr(existing_conv, key):
                        setattr(existing_conv, key, value)
                existing_conv.updated_at = datetime.utcnow()
                logger.debug(f"Updated conversation: {conversation_id}")
            else:
                # Create new conversation
                conversation = ConversationDB(**conversation_data)
                session.add(conversation)
                logger.info(f"Created new conversation: {conversation_id}")
            
            session.commit()
            
            if existing_conv:
                session.refresh(existing_conv)
                return existing_conv
            else:
                session.refresh(conversation)
                return conversation
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving conversation: {e}")
            raise
        finally:
            session.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationDB]:
        """
        Get a conversation by ID
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Optional[ConversationDB]: Conversation model or None
        """
        session = self.get_session()
        try:
            conversation = session.query(ConversationDB).filter(
                ConversationDB.conversation_id == conversation_id
            ).first()
            return conversation
        finally:
            session.close()
    
    def get_agent_conversations(self, agent_id: str, limit: int = 50) -> List[ConversationDB]:
        """
        Get all conversations for an agent
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of conversations to return
            
        Returns:
            List[ConversationDB]: List of conversations
        """
        session = self.get_session()
        try:
            conversations = session.query(ConversationDB).filter(
                ConversationDB.agent_id == agent_id,
                ConversationDB.status == "active"
            ).order_by(ConversationDB.updated_at.desc()).limit(limit).all()
            return conversations
        finally:
            session.close()
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation (soft delete)
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: Success status
        """
        session = self.get_session()
        try:
            conversation = session.query(ConversationDB).filter(
                ConversationDB.conversation_id == conversation_id
            ).first()
            if conversation:
                conversation.status = "deleted"
                session.commit()
                logger.info(f"Deleted conversation: {conversation_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting conversation: {e}")
            raise
        finally:
            session.close()
    
    # ==================== MESSAGE OPERATIONS ====================
    
    def save_message(self, message_data: Dict[str, Any]) -> MessageDB:
        """
        Save a message
        
        Args:
            message_data: Message data dictionary
            
        Returns:
            MessageDB: Saved message model
        """
        session = self.get_session()
        try:
            message = MessageDB(**message_data)
            session.add(message)
            
            # Update conversation message count and timestamp
            conversation = session.query(ConversationDB).filter(
                ConversationDB.conversation_id == message_data["conversation_id"]
            ).first()
            if conversation:
                conversation.message_count += 1
                conversation.last_message_at = datetime.utcnow()
                conversation.updated_at = datetime.utcnow()
            
            session.commit()
            session.refresh(message)
            
            logger.debug(f"Saved message: {message.message_id}")
            return message
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving message: {e}")
            raise
        finally:
            session.close()
    
    def get_conversation_messages(
        self, 
        conversation_id: str, 
        limit: Optional[int] = None
    ) -> List[MessageDB]:
        """
        Get all messages for a conversation
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageDB]: List of messages
        """
        session = self.get_session()
        try:
            query = session.query(MessageDB).filter(
                MessageDB.conversation_id == conversation_id
            ).order_by(MessageDB.created_at.asc())
            
            if limit:
                query = query.limit(limit)
            
            messages = query.all()
            return messages
        finally:
            session.close()
    
    def update_message(self, message_id: str, updates: Dict[str, Any]) -> Optional[MessageDB]:
        """
        Update a message
        
        Args:
            message_id: Message ID
            updates: Dictionary of fields to update
            
        Returns:
            Optional[MessageDB]: Updated message or None
        """
        session = self.get_session()
        try:
            message = session.query(MessageDB).filter(MessageDB.message_id == message_id).first()
            if message:
                for key, value in updates.items():
                    if hasattr(message, key):
                        setattr(message, key, value)
                session.commit()
                session.refresh(message)
                return message
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating message: {e}")
            raise
        finally:
            session.close()
    
    def delete_message(self, message_id: str) -> bool:
        """
        Delete a message
        
        Args:
            message_id: Message ID
            
        Returns:
            bool: Success status
        """
        session = self.get_session()
        try:
            message = session.query(MessageDB).filter(MessageDB.message_id == message_id).first()
            if message:
                # Update conversation message count
                conversation = session.query(ConversationDB).filter(
                    ConversationDB.conversation_id == message.conversation_id
                ).first()
                if conversation and conversation.message_count > 0:
                    conversation.message_count -= 1
                
                session.delete(message)
                session.commit()
                logger.info(f"Deleted message: {message_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting message: {e}")
            raise
        finally:
            session.close()
    
    # ==================== UTILITY OPERATIONS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dict[str, Any]: Statistics dictionary
        """
        session = self.get_session()
        try:
            total_agents = session.query(AgentDB).filter(AgentDB.is_active == True).count()
            total_conversations = session.query(ConversationDB).filter(
                ConversationDB.status == "active"
            ).count()
            total_messages = session.query(MessageDB).count()
            
            return {
                "total_agents": total_agents,
                "total_conversations": total_conversations,
                "total_messages": total_messages
            }
        finally:
            session.close()
