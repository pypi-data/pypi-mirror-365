#!/usr/bin/env python3
"""
Simple CLI chat with memory-enhanced Claude
"""

import os
from dotenv import load_dotenv
from claude_memory import ClaudeWithMemory

def main():
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        print("   Please run ./setup.sh first")
        return
    
    print("🤖 Memory-Enhanced Claude Chat")
    print("   Type 'quit' to exit")
    print("   Claude will remember your conversations!")
    print("-" * 50)
    
    # Initialize Claude with memory
    try:
        claude = ClaudeWithMemory()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Get Claude's response
            print("🤖 Claude: ", end="", flush=True)
            response = claude.chat(user_input, conversation_history)
            print(response)
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Keep history manageable
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main() 