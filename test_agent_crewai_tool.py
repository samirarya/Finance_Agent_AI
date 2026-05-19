from crewai import Agent
from crewai_tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def mock_tool(input: str):
    """Mock tool description"""
    return "mock"

try:
    agent = Agent(
        role='Test Agent',
        goal='Test',
        backstory='Test',
        llm="gemini/gemini-1.5-flash",
        tools=[mock_tool]
    )
    print("Agent created successfully with crewai_tools @tool!")
except Exception as e:
    print(f"Failed to create agent with crewai_tools @tool: {e}")
