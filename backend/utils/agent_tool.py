"""
Agent Tool Utility
Creates tools that allow agents to communicate with other agents
"""

from typing import Any, Dict
from loguru import logger
from google.adk.tools import BaseTool


def create_agent_tool(agent_id: str, agent_manager) -> BaseTool:
    """
    Create a tool that allows communication with another agent
    
    Args:
        agent_id: ID of the target agent
        agent_manager: Agent manager instance
        
    Returns:
        BaseTool: Agent communication tool
    """
    
    class AgentTool(BaseTool):
        """Tool for agent-to-agent communication"""
        
        def __init__(self, target_agent_id: str, manager):
            self.target_agent_id = target_agent_id
            self.agent_manager = manager
            self.name = f"communicate_with_{target_agent_id}"
            self.description = f"Communicate with agent {target_agent_id}"
        
        def __call__(self, message: str) -> str:
            """
            Send message to target agent
            
            Args:
                message: Message to send to the agent
                
            Returns:
                str: Agent's response
            """
            try:
                # Get target agent
                target_agent = self.agent_manager.get_agent(self.target_agent_id)
                if not target_agent:
                    return f"Error: Agent {self.target_agent_id} not found or inactive"
                
                # This is a simplified implementation
                # In a full implementation, you'd use the streaming handler
                logger.info(f"Agent communication: sending message to {self.target_agent_id}")
                
                # For now, return a mock response
                return f"Response from {self.target_agent_id}: Received your message '{message[:50]}...'"
                
            except Exception as e:
                logger.error(f"Error in agent tool communication: {e}")
                return f"Error communicating with agent {self.target_agent_id}: {str(e)}"
    
    return AgentTool(agent_id, agent_manager)
