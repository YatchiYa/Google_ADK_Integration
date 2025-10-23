"""
Google ADK Multi-Agent FastAPI Application
A comprehensive FastAPI server with full Google ADK integration supporting:
- Agent Management
- Tool Management  
- Memory Management
- Team Management
- Chat Conversation Management with Streaming
- Multi-client support
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger

from managers.agent_manager import AgentManager
from managers.tool_manager import ToolManager
from managers.memory_manager import MemoryManager
from managers.team_manager import TeamManager
from managers.conversation_manager import ConversationManager
from managers.streaming_handler import StreamingHandler
from auth.auth_manager import AuthManager
from models.api_models import *
from config.settings import Settings


# Global managers
managers: Dict[str, Any] = {}

# Global manager instances for router access
agent_manager = None
tool_manager = None
memory_manager = None
team_manager = None
conversation_manager = None
streaming_handler = None
auth_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting Google ADK FastAPI Application")
    
    # Initialize settings
    settings = Settings()
    
    # Initialize managers
    logger.info("Initializing managers...")
    
    # Core managers
    global agent_manager, tool_manager, memory_manager, team_manager
    global conversation_manager, streaming_handler, auth_manager
    
    tool_manager = ToolManager()
    memory_manager = MemoryManager()
    agent_manager = AgentManager(tool_manager, memory_manager)
    team_manager = TeamManager(agent_manager)
    streaming_handler = StreamingHandler(agent_manager=agent_manager)
    conversation_manager = ConversationManager(
        agent_manager=agent_manager,
        memory_manager=memory_manager,
        streaming_handler=streaming_handler
    )
    auth_manager = AuthManager()
    
    # Store in global managers
    managers.update({
        "settings": settings,
        "tool_manager": tool_manager,
        "memory_manager": memory_manager,
        "agent_manager": agent_manager,
        "team_manager": team_manager,
        "streaming_handler": streaming_handler,
        "conversation_manager": conversation_manager,
        "auth_manager": auth_manager
    })
    
    logger.info("✅ All managers initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down application")
    await streaming_handler.shutdown()
    logger.info("✅ Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Google ADK Multi-Agent API",
    description="Comprehensive FastAPI server with Google ADK integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection
def get_agent_manager() -> AgentManager:
    return managers["agent_manager"]

def get_tool_manager() -> ToolManager:
    return managers["tool_manager"]

def get_memory_manager() -> MemoryManager:
    return managers["memory_manager"]

def get_team_manager() -> TeamManager:
    return managers["team_manager"]

def get_conversation_manager() -> ConversationManager:
    return managers["conversation_manager"]

def get_streaming_handler() -> StreamingHandler:
    return managers["streaming_handler"]

def get_auth_manager() -> AuthManager:
    return managers["auth_manager"]


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "managers": {
            "agent_manager": "active",
            "tool_manager": "active", 
            "memory_manager": "active",
            "team_manager": "active",
            "conversation_manager": "active",
            "streaming_handler": "active"
        }
    }


# Include routers
from routers import agents, tools, memory, teams, conversations, streaming, auth, images

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["Tools"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(streaming.router, prefix="/api/v1/streaming", tags=["Streaming"])
app.include_router(images.router, tags=["Images"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Google ADK Multi-Agent FastAPI Server",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "agents": "/api/v1/agents",
            "tools": "/api/v1/tools",
            "memory": "/api/v1/memory", 
            "teams": "/api/v1/teams",
            "conversations": "/api/v1/conversations",
            "streaming": "/api/v1/streaming",
            "images": "/api/v1/images"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
