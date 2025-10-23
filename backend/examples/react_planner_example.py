#!/usr/bin/env python3
"""
ReAct Planner Example for Google ADK
Demonstrates PlanReActPlanner with structured reasoning and planning
"""

import asyncio
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.planners import PlanReActPlanner, BuiltInPlanner
from google.genai.types import ThinkingConfig

# Configuration
APP_NAME = "react_planner_demo"
USER_ID = "demo_user"
SESSION_ID = "react_session_001"

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the weather report.
        
    Returns:
        dict: status and result or error msg.
    """
    weather_data = {
        "new york": "Sunny, 25°C (77°F), light breeze from the west",
        "london": "Cloudy, 18°C (64°F), chance of rain in the afternoon", 
        "tokyo": "Partly cloudy, 22°C (72°F), humid conditions",
        "paris": "Overcast, 16°C (61°F), light drizzle expected",
        "sydney": "Clear skies, 28°C (82°F), perfect beach weather"
    }
    
    city_lower = city.lower()
    if city_lower in weather_data:
        return {
            "status": "success",
            "report": f"Weather in {city}: {weather_data[city_lower]}"
        }
    else:
        return {
            "status": "error", 
            "error_message": f"Weather information for '{city}' is not available."
        }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the current time.
        
    Returns:
        dict: status and result or error msg.
    """
    timezone_map = {
        "new york": "America/New_York",
        "london": "Europe/London", 
        "tokyo": "Asia/Tokyo",
        "paris": "Europe/Paris",
        "sydney": "Australia/Sydney"
    }
    
    city_lower = city.lower()
    if city_lower in timezone_map:
        tz_identifier = timezone_map[city_lower]
        tz = ZoneInfo(tz_identifier)
        now = datetime.now(tz)
        report = f'Current time in {city}: {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        return {"status": "success", "report": report}
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}."
        }

def calculate_travel_time(from_city: str, to_city: str, transport: str = "flight") -> dict:
    """Calculate estimated travel time between cities.
    
    Args:
        from_city (str): Origin city
        to_city (str): Destination city  
        transport (str): Mode of transport (flight, train, car)
        
    Returns:
        dict: status and travel time estimate
    """
    # Simplified travel time matrix (in hours)
    travel_times = {
        ("new york", "london"): {"flight": 7, "train": None, "car": None},
        ("new york", "tokyo"): {"flight": 14, "train": None, "car": None},
        ("london", "paris"): {"flight": 1.5, "train": 2.5, "car": 6},
        ("tokyo", "sydney"): {"flight": 9, "train": None, "car": None},
        ("paris", "london"): {"flight": 1.5, "train": 2.5, "car": 6}
    }
    
    from_lower = from_city.lower()
    to_lower = to_city.lower()
    
    # Check both directions
    route = (from_lower, to_lower)
    reverse_route = (to_lower, from_lower)
    
    if route in travel_times:
        time_data = travel_times[route]
    elif reverse_route in travel_times:
        time_data = travel_times[reverse_route]
    else:
        return {
            "status": "error",
            "error_message": f"No travel data available for route {from_city} to {to_city}"
        }
    
    if transport.lower() not in time_data or time_data[transport.lower()] is None:
        return {
            "status": "error", 
            "error_message": f"{transport} travel not available for this route"
        }
    
    travel_time = time_data[transport.lower()]
    return {
        "status": "success",
        "report": f"Travel time from {from_city} to {to_city} by {transport}: {travel_time} hours"
    }

async def demo_plan_react_planner():
    """Demonstrate PlanReActPlanner with structured reasoning"""
    
    print("🧠 ReAct Planner Demo - PlanReActPlanner")
    print("=" * 60)
    
    # Create PlanReActPlanner
    planner = PlanReActPlanner()
    print("✅ PlanReActPlanner created")
    
    # Create agent with planner
    agent = LlmAgent(
        model="gemini-2.0-flash-exp",
        name="travel_planning_agent", 
        instruction="""You are a travel planning assistant that uses structured ReAct methodology.
        
        Follow this format:
        /*PLANNING*/
        Create a detailed step-by-step plan
        
        /*ACTION*/  
        Execute the planned actions using available tools
        
        /*REASONING*/
        Explain your reasoning and observations
        
        /*FINAL_ANSWER*/
        Provide the final comprehensive answer
        """,
        planner=planner,
        tools=[get_weather, get_current_time, calculate_travel_time]
    )
    
    # Session and Runner
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID
    )
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    
    # Test query requiring planning and multiple tool calls
    query = """I'm planning a business trip from New York to London, then to Paris. 
    I need to know:
    1. Current weather in all three cities
    2. Current time in each city  
    3. Travel times between the cities
    4. Best recommendations for scheduling meetings
    
    Please create a comprehensive travel plan with detailed reasoning."""
    
    print(f"\n🎯 Query: {query}")
    print("\n📋 Agent Response:")
    print("-" * 60)
    
    # Execute with structured planning
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id, 
        new_message=content
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end='', flush=True)
    
    print("\n" + "=" * 60)
    print("✅ ReAct Planning Demo Complete!")

async def demo_builtin_planner():
    """Demonstrate BuiltInPlanner with thinking capabilities"""
    
    print("\n\n🤔 Built-in Planner Demo - BuiltInPlanner with Thinking")
    print("=" * 60)
    
    # Create ThinkingConfig
    thinking_config = ThinkingConfig(
        include_thoughts=True,   # Include model's internal reasoning
        thinking_budget=512      # Limit thinking tokens
    )
    
    # Create BuiltInPlanner
    planner = BuiltInPlanner(thinking_config=thinking_config)
    print("✅ BuiltInPlanner with ThinkingConfig created")
    
    # Create agent with thinking planner
    agent = LlmAgent(
        model="gemini-2.5-flash-exp",
        name="analytical_agent",
        instruction="You are an analytical assistant that shows your thinking process clearly.",
        planner=planner,
        tools=[get_weather, get_current_time, calculate_travel_time]
    )
    
    # Session and Runner  
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME + "_thinking",
        user_id=USER_ID
    )
    runner = Runner(agent=agent, app_name=APP_NAME + "_thinking", session_service=session_service)
    
    # Complex analytical query
    query = """If I need to attend meetings in Tokyo at 9 AM local time, and then fly to Sydney for a 2 PM meeting the same day, is this feasible? Consider time zones, flight duration, and provide a detailed analysis."""
    
    print(f"\n🎯 Query: {query}")
    print("\n🤔 Agent Response (with thinking):")
    print("-" * 60)
    
    # Execute with thinking
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=content
    ):
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end='', flush=True)
    
    print("\n" + "=" * 60)
    print("✅ Built-in Planner Demo Complete!")

async def main():
    """Run both planner demonstrations"""
    try:
        # Demo PlanReActPlanner
        await demo_plan_react_planner()
        
        # Demo BuiltInPlanner  
        await demo_builtin_planner()
        
        print("\n🎉 All planner demonstrations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Google ADK Planner Demonstrations")
    asyncio.run(main())
