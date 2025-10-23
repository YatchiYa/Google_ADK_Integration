"""
Test script for database persistence
"""

import os
import sys
from loguru import logger

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from services.database_service import DatabaseService
from managers.agent_manager import AgentManager, AgentPersona, AgentConfig
from managers.tool_manager import ToolManager
from managers.memory_manager import MemoryManager


def test_database_connection():
    """Test database connection and table creation"""
    logger.info("Testing database connection...")
    
    try:
        db_service = DatabaseService()
        logger.info("✅ Database service initialized successfully")
        
        # Get stats
        stats = db_service.get_stats()
        logger.info(f"Database stats: {stats}")
        
        return db_service
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None


def test_agent_persistence(db_service):
    """Test agent persistence"""
    logger.info("\n" + "="*50)
    logger.info("Testing agent persistence...")
    logger.info("="*50)
    
    try:
        # Initialize managers
        tool_manager = ToolManager()
        memory_manager = MemoryManager()
        agent_manager = AgentManager(tool_manager, memory_manager, db_service)
        
        # Create a test agent
        persona = AgentPersona(
            name="Test Agent",
            description="A test agent for database persistence",
            personality="helpful and professional",
            expertise=["testing", "databases"],
            communication_style="professional"
        )
        
        config = AgentConfig(
            model="gemini-2.0-flash",
            temperature=0.7,
            max_output_tokens=2048
        )
        
        agent_id = agent_manager.create_agent(
            name="Test Database Agent",
            persona=persona,
            config=config,
            tools=["google_search", "calculator"]
        )
        
        logger.info(f"✅ Created agent: {agent_id}")
        
        # Verify agent was saved to database
        db_agent = db_service.get_agent(agent_id)
        if db_agent:
            logger.info(f"✅ Agent found in database: {db_agent.name}")
            logger.info(f"   - Tools: {db_agent.tools}")
            logger.info(f"   - Created: {db_agent.created_at}")
        else:
            logger.error(f"❌ Agent not found in database")
        
        # Test agent listing
        all_agents = db_service.get_all_agents()
        logger.info(f"✅ Total agents in database: {len(all_agents)}")
        
        return agent_id
        
    except Exception as e:
        logger.error(f"❌ Agent persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_conversation_persistence(db_service, agent_id):
    """Test conversation persistence"""
    logger.info("\n" + "="*50)
    logger.info("Testing conversation persistence...")
    logger.info("="*50)
    
    try:
        # Create a test conversation
        conversation_data = {
            "conversation_id": "test_conv_001",
            "agent_id": agent_id,
            "session_id": "test_session_001",
            "title": "Test Conversation",
            "status": "active",
            "message_count": 0,
            "metadata": {"test": True}
        }
        
        db_service.save_conversation(conversation_data)
        logger.info(f"✅ Created conversation: test_conv_001")
        
        # Add a test message
        message_data = {
            "message_id": "test_msg_001",
            "conversation_id": "test_conv_001",
            "role": "user",
            "content": "Hello, this is a test message",
            "message_type": "text",
            "metadata": {}
        }
        
        db_service.save_message(message_data)
        logger.info(f"✅ Created message: test_msg_001")
        
        # Verify conversation was saved
        db_conv = db_service.get_conversation("test_conv_001")
        if db_conv:
            logger.info(f"✅ Conversation found in database: {db_conv.title}")
            logger.info(f"   - Agent ID: {db_conv.agent_id}")
            logger.info(f"   - Message count: {db_conv.message_count}")
        else:
            logger.error(f"❌ Conversation not found in database")
        
        # Verify messages
        messages = db_service.get_conversation_messages("test_conv_001")
        logger.info(f"✅ Messages in conversation: {len(messages)}")
        for msg in messages:
            logger.info(f"   - {msg.role}: {msg.content[:50]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Conversation persistence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lazy_loading(db_service):
    """Test lazy loading of agents from database"""
    logger.info("\n" + "="*50)
    logger.info("Testing lazy loading...")
    logger.info("="*50)
    
    try:
        # Initialize fresh managers (simulating server restart)
        tool_manager = ToolManager()
        memory_manager = MemoryManager()
        agent_manager = AgentManager(tool_manager, memory_manager, db_service)
        
        # Get all agents from memory
        agents = agent_manager.list_agents()
        logger.info(f"✅ Agents loaded from database: {len(agents)}")
        
        for agent_info in agents:
            logger.info(f"   - {agent_info['name']} ({agent_info['agent_id']})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Lazy loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("="*70)
    logger.info("DATABASE PERSISTENCE TEST SUITE")
    logger.info("="*70)
    
    # Test 1: Database connection
    db_service = test_database_connection()
    if not db_service:
        logger.error("Database connection failed. Exiting.")
        return
    
    # Test 2: Agent persistence
    agent_id = test_agent_persistence(db_service)
    if not agent_id:
        logger.error("Agent persistence test failed. Exiting.")
        return
    
    # Test 3: Conversation persistence
    conv_success = test_conversation_persistence(db_service, agent_id)
    if not conv_success:
        logger.error("Conversation persistence test failed.")
    
    # Test 4: Lazy loading
    lazy_success = test_lazy_loading(db_service)
    if not lazy_success:
        logger.error("Lazy loading test failed.")
    
    # Final stats
    logger.info("\n" + "="*70)
    logger.info("FINAL DATABASE STATS")
    logger.info("="*70)
    stats = db_service.get_stats()
    logger.info(f"Total Agents: {stats['total_agents']}")
    logger.info(f"Total Conversations: {stats['total_conversations']}")
    logger.info(f"Total Messages: {stats['total_messages']}")
    logger.info("="*70)
    logger.info("✅ All tests completed!")


if __name__ == "__main__":
    main()
