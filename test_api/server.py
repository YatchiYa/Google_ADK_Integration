"""
FastAPI Server for Google ADK Agent Testing
Provides endpoints to run the agent and capture events
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import uvicorn

# Import your agent and ADK components
from my_sample_agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = FastAPI(
    title="Google ADK Agent API",
    description="API server for testing Google ADK agents",
    version="1.0.0"
)

# In-memory session storage (use Redis/DB in production)
sessions: Dict[str, Dict[str, Any]] = {}

# ADK Session Service
adk_session_service = InMemorySessionService()


# =====================================================
# Request/Response Models
# =====================================================
class MessagePart(BaseModel):
    text: Optional[str] = None
    inlineData: Optional[Dict[str, Any]] = None


class Message(BaseModel):
    role: str
    parts: List[MessagePart]


class RunRequest(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    new_message: Message
    streaming: bool = False


class SessionState(BaseModel):
    state: Dict[str, Any] = {}


class SessionResponse(BaseModel):
    id: str
    appName: str
    userId: str
    state: Dict[str, Any]
    events: List[Dict[str, Any]]
    lastUpdateTime: float


# =====================================================
# Helper Functions
# =====================================================
def get_session_key(app_name: str, user_id: str, session_id: str) -> str:
    """Generate unique session key"""
    return f"{app_name}:{user_id}:{session_id}"


def get_or_create_session(app_name: str, user_id: str, session_id: str) -> Dict[str, Any]:
    """Get existing session or create new one"""
    key = get_session_key(app_name, user_id, session_id)
    if key not in sessions:
        sessions[key] = {
            "id": session_id,
            "appName": app_name,
            "userId": user_id,
            "state": {},
            "events": [],
            "lastUpdateTime": datetime.now().timestamp()
        }
    return sessions[key]


# =====================================================
# Utility Endpoints
# =====================================================
@app.get("/list-apps")
async def list_apps():
    """List all available agent applications"""
    return ["my_sample_agent"]


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "running",
        "message": "Google ADK Agent API Server",
        "docs": "/docs",
        "available_apps": ["my_sample_agent"]
    }


# =====================================================
# Session Management Endpoints
# =====================================================
@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def create_or_update_session(
    app_name: str,
    user_id: str,
    session_id: str,
    session_state: SessionState
) -> SessionResponse:
    """Create a new session or update existing one"""
    key = get_session_key(app_name, user_id, session_id)
    
    if key in sessions:
        # Update existing session
        sessions[key]["state"] = session_state.state
        sessions[key]["lastUpdateTime"] = datetime.now().timestamp()
    else:
        # Create new session
        sessions[key] = {
            "id": session_id,
            "appName": app_name,
            "userId": user_id,
            "state": session_state.state,
            "events": [],
            "lastUpdateTime": datetime.now().timestamp()
        }
    
    return SessionResponse(**sessions[key])


@app.get("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def get_session(
    app_name: str,
    user_id: str,
    session_id: str
) -> SessionResponse:
    """Get session details"""
    key = get_session_key(app_name, user_id, session_id)
    
    if key not in sessions:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    
    return SessionResponse(**sessions[key])


@app.delete("/apps/{app_name}/users/{user_id}/sessions/{session_id}", status_code=204)
async def delete_session(
    app_name: str,
    user_id: str,
    session_id: str
):
    """Delete a session"""
    key = get_session_key(app_name, user_id, session_id)
    
    if key in sessions:
        del sessions[key]
    
    return None


# =====================================================
# Agent Execution Endpoints
# =====================================================
@app.post("/run")
async def run_agent(request: RunRequest) -> List[Dict[str, Any]]:
    """
    Execute agent and return all events at once
    """
    # Get or create session
    session = get_or_create_session(
        request.app_name,
        request.user_id,
        request.session_id
    )
    
    # Extract user message text
    user_message = ""
    for part in request.new_message.parts:
        if part.text:
            user_message += part.text
    
    # Prepare events list
    events = []
    
    try:
        # Add user message event
        user_event = {
            "content": {
                "parts": [{"text": user_message}],
                "role": "user"
            },
            "invocationId": f"inv-{datetime.now().timestamp()}",
            "author": "user",
            "id": f"msg-{len(session['events'])}",
            "timestamp": datetime.now().timestamp()
        }
        events.append(user_event)
        session["events"].append(user_event)
        
        # Run the agent using ADK Runner
        print(f"\n🚀 Running agent with message: {user_message}\n")
        
        # Create ADK session if not exists
        adk_session_key = f"{request.app_name}:{request.user_id}:{request.session_id}"
        try:
            adk_session = await adk_session_service.get_session(
                app_name=request.app_name,
                user_id=request.user_id,
                session_id=request.session_id
            )
        except:
            adk_session = await adk_session_service.create_session(
                app_name=request.app_name,
                user_id=request.user_id,
                session_id=request.session_id,
                state=session["state"]
            )
        
        # Initialize runner with proper parameters
        runner = Runner(
            agent=root_agent,
            app_name=request.app_name,
            session_service=adk_session_service
        )
        
        # Create content message
        content = types.Content(
            role='user',
            parts=[types.Part(text=user_message)]
        )
        
        # Collect all events from the agent execution
        agent_events = []
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=content
        ):
            # Convert ADK event to our event format
            event_text = ""
            if hasattr(event, 'content') and event.content and event.content.parts:
                event_text = str(event.content.parts[0].text if hasattr(event.content.parts[0], 'text') else event.content.parts[0])
            else:
                event_text = str(event)
            
            event_data = {
                "content": {
                    "parts": [{"text": event_text}],
                    "role": "model"
                },
                "invocationId": f"inv-{datetime.now().timestamp()}",
                "author": event.author if hasattr(event, 'author') else "root_agent",
                "actions": {
                    "stateDelta": {},
                    "artifactDelta": {},
                    "requestedAuthConfigs": {}
                },
                "id": f"evt-{len(agent_events)}",
                "timestamp": datetime.now().timestamp()
            }
            agent_events.append(event_data)
            events.append(event_data)
            session["events"].append(event_data)
        
        # If no events were generated, create a completion event
        if not agent_events:
            response_text = "Agent completed successfully (no events generated)"
        else:
            response_text = "Agent execution completed"
        
        # Add completion event only if no agent events
        if not agent_events:
            response_event = {
                "content": {
                    "parts": [{"text": response_text}],
                    "role": "model"
                },
                "invocationId": f"inv-{datetime.now().timestamp()}",
                "author": "root_agent",
                "actions": {
                    "stateDelta": {},
                    "artifactDelta": {},
                    "requestedAuthConfigs": {}
                },
                "id": f"msg-{len(session['events'])}",
                "timestamp": datetime.now().timestamp()
            }
            events.append(response_event)
            session["events"].append(response_event)
        
        # Update session
        session["lastUpdateTime"] = datetime.now().timestamp()
        
        return events
        
    except Exception as e:
        error_event = {
            "content": {
                "parts": [{"text": f"Error: {str(e)}"}],
                "role": "model"
            },
            "invocationId": f"inv-{datetime.now().timestamp()}",
            "author": "system",
            "error": str(e),
            "id": f"msg-{len(session['events'])}",
            "timestamp": datetime.now().timestamp()
        }
        events.append(error_event)
        session["events"].append(error_event)
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run_sse")
async def run_agent_sse(request: RunRequest):
    """
    Execute agent and stream events as Server-Sent Events
    """
    async def event_generator():
        # Get or create session
        session = get_or_create_session(
            request.app_name,
            request.user_id,
            request.session_id
        )
        
        # Extract user message text
        user_message = ""
        for part in request.new_message.parts:
            if part.text:
                user_message += part.text
        
        try:
            # Send user message event
            user_event = {
                "content": {
                    "parts": [{"text": user_message}],
                    "role": "user"
                },
                "invocationId": f"inv-{datetime.now().timestamp()}",
                "author": "user",
                "id": f"msg-{len(session['events'])}",
                "timestamp": datetime.now().timestamp()
            }
            session["events"].append(user_event)
            yield f"data: {json.dumps(user_event)}\n\n"
            
            # Run the agent using ADK Runner
            print(f"\n🚀 Running agent (streaming) with message: {user_message}\n")
            
            # Create ADK session if not exists
            try:
                adk_session = await adk_session_service.get_session(
                    app_name=request.app_name,
                    user_id=request.user_id,
                    session_id=request.session_id
                )
            except:
                adk_session = await adk_session_service.create_session(
                    app_name=request.app_name,
                    user_id=request.user_id,
                    session_id=request.session_id,
                    state=session["state"]
                )
            
            # Initialize runner with proper parameters
            runner = Runner(
                agent=root_agent,
                app_name=request.app_name,
                session_service=adk_session_service
            )
            
            # Create content message
            content = types.Content(
                role='user',
                parts=[types.Part(text=user_message)]
            )
            
            # Stream events from agent execution
            async for event in runner.run_async(
                user_id=request.user_id,
                session_id=request.session_id,
                new_message=content
            ):
                # Convert ADK event to our event format
                event_text = ""
                if hasattr(event, 'content') and event.content and event.content.parts:
                    event_text = str(event.content.parts[0].text if hasattr(event.content.parts[0], 'text') else event.content.parts[0])
                else:
                    event_text = str(event)
                
                if request.streaming:
                    # Token-level streaming - split content into words
                    words = event_text.split()
                    for i, word in enumerate(words):
                        chunk_event = {
                            "content": {
                                "parts": [{"text": word + " "}],
                                "role": "model"
                            },
                            "invocationId": f"inv-{datetime.now().timestamp()}",
                            "author": event.author if hasattr(event, 'author') else "root_agent",
                            "id": f"chunk-{i}",
                            "timestamp": datetime.now().timestamp()
                        }
                        yield f"data: {json.dumps(chunk_event)}\n\n"
                        await asyncio.sleep(0.05)  # Simulate streaming delay
                else:
                    # Send complete event
                    event_data = {
                        "content": {
                            "parts": [{"text": event_text}],
                            "role": "model"
                        },
                        "invocationId": f"inv-{datetime.now().timestamp()}",
                        "author": event.author if hasattr(event, 'author') else "root_agent",
                        "actions": {
                            "stateDelta": {},
                            "artifactDelta": {},
                            "requestedAuthConfigs": {}
                        },
                        "id": f"evt-{len(session['events'])}",
                        "timestamp": datetime.now().timestamp()
                    }
                    session["events"].append(event_data)
                    yield f"data: {json.dumps(event_data)}\n\n"
            
            # Update session
            session["lastUpdateTime"] = datetime.now().timestamp()
            
        except Exception as e:
            error_event = {
                "content": {
                    "parts": [{"text": f"Error: {str(e)}"}],
                    "role": "model"
                },
                "invocationId": f"inv-{datetime.now().timestamp()}",
                "author": "system",
                "error": str(e),
                "id": f"msg-{len(session['events'])}",
                "timestamp": datetime.now().timestamp()
            }
            session["events"].append(error_event)
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


# =====================================================
# Run Server
# =====================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Google ADK Agent API Server")
    print("="*60)
    print("📚 Interactive Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/")
    print("📋 List Apps: http://localhost:8000/list-apps")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
