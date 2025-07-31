"""
MEMG + Claude Integration
Simple example showing how to give Claude memory capabilities
"""

import os
from typing import List, Dict, Any
import anthropic
from memg import SyncMemorySystem

class ClaudeWithMemory:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.memory = SyncMemorySystem()
        
        # Define memory tools for Claude
        self.tools = [
            {
                "name": "add_memory",
                "description": "Store information for future reference",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "What to remember"
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "search_memories",
                "description": "Search for relevant memories",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    def add_memory(self, content: str) -> str:
        """Add a memory"""
        try:
            response = self.memory.add(content=content, source="claude_chat")
            return f"✅ Memory stored (ID: {response.memory_id})"
        except Exception as e:
            return f"❌ Failed to store memory: {str(e)}"
    
    def search_memories(self, query: str) -> str:
        """Search memories"""
        try:
            results = self.memory.search(query, limit=3)
            if not results:
                return "No relevant memories found"
            
            memories = []
            for result in results:
                memories.append(f"- {result.get('content', 'No content')}")
            
            return "📚 Relevant memories:\n" + "\n".join(memories)
        except Exception as e:
            return f"❌ Failed to search memories: {str(e)}"
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Chat with Claude, who can use memory tools"""
        
        if conversation_history is None:
            conversation_history = []
        
        # Add user message
        messages = conversation_history + [{"role": "user", "content": message}]
        
        # System prompt
        system_prompt = """You are a helpful assistant with perfect memory. You have access to memory tools:
        
- Use add_memory() to store important information for future reference
- Use search_memories() to recall relevant information from past conversations
- Decide when to store vs retrieve memories based on context
- Be natural - don't mention the tools unless relevant

Remember: You can maintain context across conversations using these memory tools."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=system_prompt,
                messages=messages,
                tools=self.tools
            )
            
            # Handle tool calls
            if response.content[-1].type == "tool_use":
                tool_results = []
                
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        
                        if tool_name == "add_memory":
                            result = self.add_memory(tool_input["content"])
                        elif tool_name == "search_memories":
                            result = self.search_memories(tool_input["query"])
                        else:
                            result = "Unknown tool"
                        
                        tool_results.append({
                            "tool_use_id": content_block.id,
                            "content": result
                        })
                
                # Get final response after tool use
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
                
                final_response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=messages
                )
                
                return final_response.content[0].text
            
            else:
                return response.content[0].text
                
        except Exception as e:
            return f"❌ Error: {str(e)}" 