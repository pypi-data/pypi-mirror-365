# MEMG Integrations

This directory contains example implementations showing how to integrate MEMG (Memory Management System) with various tools and platforms.

## 📋 Available Integrations

### 🤖 ADK (Anthropic Development Kit) Integration
**Location**: `./adk/`

A complete example of integrating MEMG with Claude via the Anthropic API to create a memory-enhanced personal assistant.

**Features**:
- 🧠 **Memory-Enhanced Chat**: Claude remembers your conversations and preferences
- 🔍 **Smart Memory Management**: AI decides when to store vs retrieve memories
- 🎨 **Beautiful Web UI**: Clean, modern interface for natural conversations
- 📦 **One-Command Setup**: Just run `./setup.sh` and start chatting
- 🔧 **Tool Integration**: Memory functions exposed as Claude tools

**Quick Start**:
```bash
pip install memg
cd integrations/adk
./setup.sh
```

## 🎯 Purpose

These integrations serve as:
- **Reference implementations** for developers
- **Working examples** of MEMG capabilities  
- **Starting points** for custom integrations
- **Proof of concepts** for various use cases

## 🛠️ Creating Your Own Integration

Each integration follows this pattern:
1. **Install MEMG**: `pip install memg`
2. **Import memory functions**: Use MEMG's API for memory operations
3. **Expose as tools**: Integrate memory functions into your system
4. **Let AI decide**: Allow the AI to choose when to memorize vs remember

## 📚 Integration Guidelines

- Keep examples **simple and focused**
- Include **complete setup instructions**
- Provide **clear documentation**
- Show **real-world usage patterns**
- Make it **easy to modify** for custom needs

---

*These are example implementations. Modify them to fit your specific needs and use cases.* 