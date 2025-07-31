# Google Gemini 2.0 Flash Setup

## Required: Add to your .env file

```bash
# Add this line to your .env file:
GOOGLE_API_KEY=your_google_api_key_here
```

## How to get Google API Key:

1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create a new project or select existing
4. Generate API key for Gemini
5. Add to .env file

## Current Setup:
- **Memory**: Google Gemini 2.0 Flash (very fast memory operations)
- **Conversation Processing**: Claude Sonnet 3.5 (high quality insight extraction)

This separation provides:
- ⚡ Fast memory operations with Gemini
- 🧠 High-quality insights with Claude
- No model conflicts between pipelines
