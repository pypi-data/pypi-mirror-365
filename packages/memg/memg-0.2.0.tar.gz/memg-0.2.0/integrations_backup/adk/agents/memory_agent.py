"""
Memory-enhanced agent using Google ADK with MEMG integration
"""
from datetime import datetime
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.load_memory_tool import load_memory_tool
from google.adk.tools.preload_memory_tool import preload_memory_tool


def update_current_time(callback_context: CallbackContext):
    """Update current time in agent state"""
    callback_context.state['_time'] = datetime.now().isoformat()


# Memory-enhanced agent with MEMG integration
memory_agent = Agent(
    model='gemini-2.0-flash-001',
    name='memg_memory_agent',
    description='AI assistant with persistent memory using MEMG system',
    before_agent_callback=update_current_time,
    instruction="""You are a helpful AI assistant with access to persistent memory.

Current time: {_time}

You can remember information from past conversations and retrieve it when needed.
Use the memory tools to:
- Load relevant memories when answering questions
- Preload context for better responses

Always be helpful and use your memory capabilities to provide personalized assistance.
""",
    tools=[
        load_memory_tool,
        preload_memory_tool,
    ],
) 