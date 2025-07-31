#!/usr/bin/env python3
"""
MEMG + Google ADK Integration

A simple demonstration of how to use MEMG memory system with Google ADK.
Run with: python main.py
"""
import asyncio
from datetime import datetime, timedelta
from typing import cast

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk.sessions.session import Session
from google.genai import types

from agent import root_agent
from agents.tools import MemgMemoryService

# Load environment variables
load_dotenv()


async def main():
    """Main demo function showing MEMG + ADK integration"""
    app_name = 'memg_adk_demo'
    user_id = 'demo_user'
    
    # Create runner with our custom MEMG memory service
    runner = InMemoryRunner(
        app_name=app_name,
        agent=root_agent
    )
    # Set our custom memory service
    runner.memory_service = MemgMemoryService()
    
    async def chat(session: Session, message: str) -> Session:
        """Send a message and get response"""
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text=message)]
        )
        
        print(f'\n🧑 User: {message}')
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
        ):
            if not event.content or not event.content.parts:
                continue
                
            if event.content.parts[0].text:
                print(f'🤖 {event.author}: {event.content.parts[0].text}')
            elif event.content.parts[0].function_call:
                func_call = event.content.parts[0].function_call
                print(f'🔧 {event.author}: Calling {func_call.name}({func_call.args})')
            elif event.content.parts[0].function_response:
                func_resp = event.content.parts[0].function_response
                print(f'📋 {event.author}: {func_resp.name} → {func_resp.response}')
        
        # Return updated session
        return cast(
            Session,
            await runner.session_service.get_session(
                app_name=app_name, 
                user_id=user_id, 
                session_id=session.id
            ),
        )
    
    print("🚀 MEMG + Google ADK Demo")
    print("=" * 50)
    
    # Session 1: Build up some memory
    print("\n📝 Session 1: Building Memory")
    session_1 = await runner.session_service.create_session(
        app_name=app_name, 
        user_id=user_id
    )
    
    session_1 = await chat(session_1, "Hi! My name is Alex.")
    session_1 = await chat(session_1, "I'm a software engineer working on AI projects.")
    session_1 = await chat(session_1, "I love Python and I'm learning about agent frameworks.")
    session_1 = await chat(session_1, f"Today is {datetime.now().strftime('%Y-%m-%d')} and I had a great meeting about our new product.")
    
    print("\n💾 Saving session to MEMG memory...")
    if runner.memory_service:
        await runner.memory_service.add_session_to_memory(session_1)
    print("✅ Memory saved!")
    
    # Session 2: Test memory recall
    print("\n🧠 Session 2: Testing Memory Recall")
    session_2 = await runner.session_service.create_session(
        app_name=app_name, 
        user_id=user_id
    )
    
    session_2 = await chat(session_2, "Hi again!")
    session_2 = await chat(session_2, "What do you remember about me?")
    session_2 = await chat(session_2, "What's my profession?")
    session_2 = await chat(session_2, "What programming language do I like?")
    session_2 = await chat(session_2, "What happened in my meeting today?")
    
    print("\n🎉 Demo complete!")
    print("\nThis demonstrates how MEMG integrates with Google ADK to provide")
    print("persistent memory across different conversation sessions.")


if __name__ == '__main__':
    asyncio.run(main()) 