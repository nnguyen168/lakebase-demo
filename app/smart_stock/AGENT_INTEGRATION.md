# Agent Integration with Model Serving Endpoint

This document describes the new AI agent chatbot integration using Databricks Model Serving with a managed MCP (Model Context Protocol) server for Genie.

## Overview

The chatbot has been upgraded from direct Genie API integration to use a **Databricks Model Serving endpoint** that wraps an agent with a managed MCP server for Genie. This provides:

- **Better performance** - Model serving endpoints are optimized for production workloads
- **Simplified architecture** - Single API call instead of conversation management + polling
- **Enhanced capabilities** - The agent can use tools via MCP to query Genie
- **Better formatting** - Rich markdown responses with tables and formatting
- **Conversation context** - The agent maintains context across the conversation

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          React Frontend                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  FloatingGenie.tsx  →  AgentChat.tsx                           │ │
│  │  - Floating chat button                                         │ │
│  │  - Message history with markdown rendering                      │ │
│  │  - Table support for structured data                            │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
                    POST /api/agent/send-message
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  server/routers/agent.py                                        │ │
│  │  - Message formatting                                           │ │
│  │  - Conversation history management                              │ │
│  │  - Authentication handling                                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
              POST to Model Serving Endpoint with Bearer token
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Databricks Model Serving                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Agent with Managed MCP Server for Genie                       │ │
│  │  - Processes natural language queries                          │ │
│  │  - Uses MCP tools to query Genie                               │ │
│  │  - Generates SQL and executes via Genie                        │ │
│  │  - Formats results with markdown and tables                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
                          Returns structured response
```

## API Format

### Request Format

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What are my top 5 products by revenue?"
    }
  ]
}
```

The backend automatically includes the last 10 messages for conversation context.

### Response Format

```json
{
  "message_id": "chatcmpl_b311ab33-6177-4193-9f0c-38e3c2744dbf",
  "content": "**Top 5 Products by Revenue**\n\n| Rank | Product | Revenue |\n|------|---------|---------|...",
  "status": "completed",
  "error": null
}
```

The content includes markdown formatting with:
- **Bold text** for headings
- Tables for structured data
- Bullet points and lists
- Contextual explanations

## Configuration

### Environment Variables

Add to `.env.local` or `app.yaml`:

```bash
# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com/
DATABRICKS_TOKEN=your-personal-access-token

# Model Serving Endpoint
MODEL_SERVING_ENDPOINT=https://your-workspace.cloud.databricks.com/serving-endpoints/your-agent/invocations
```

### app.yaml Example

```yaml
env:
  - name: DATABRICKS_HOST
    value: "https://fe-vm-nam-nguyen-workspace-classic.cloud.databricks.com/"
  - name: DATABRICKS_TOKEN
    value: "your-token"
  - name: MODEL_SERVING_ENDPOINT
    value: "https://fe-vm-nam-nguyen-workspace-classic.cloud.databricks.com/serving-endpoints/agents_demo_nnguyen-smartstock-assistant/invocations"
```

## Files Changed

### Backend
- **`server/routers/agent.py`** - New router for agent endpoint (replaces genie.py)
- **`server/app.py`** - Added agent router import and registration

### Frontend
- **`client/src/components/AgentChat.tsx`** - New chat component with markdown rendering
- **`client/src/components/FloatingGenie.tsx`** - Updated to use AgentChat instead of GenieChat

### Configuration
- **`app.yaml`** - Added MODEL_SERVING_ENDPOINT environment variable

## Testing

### 1. Test the Model Serving Endpoint Directly

```bash
cd app/smart_stock
uv run python test_agent_endpoint.py
```

This script tests:
- Direct connection to the model serving endpoint
- Response parsing
- Health check endpoint

### 2. Test the Backend API

```bash
# Start the backend server
cd app/smart_stock
uv run uvicorn server.app:app --reload

# In another terminal, test the API
curl -X POST http://localhost:8000/api/agent/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What are my top 5 products by revenue?"
      }
    ]
  }'
```

### 3. Test the Full Stack

```bash
# Start backend
cd app/smart_stock
uv run uvicorn server.app:app --reload

# In another terminal, start frontend
cd app/smart_stock/client
bun run dev

# Open browser to http://localhost:5173
# Click the chat button in the bottom-right corner
# Ask: "What are my top 5 products by revenue?"
```

### 4. Test Health Check

```bash
curl http://localhost:8000/api/agent/health
```

Expected response:
```json
{
  "status": "healthy",
  "configured": true,
  "endpoint": "https://...",
  "host": "https://..."
}
```

## Features

### Markdown Rendering

The frontend now supports:
- **Bold text** using `**text**`
- Tables with headers and rows
- Automatic table formatting from markdown
- Line breaks and paragraphs

Example agent response:
```markdown
**Top 5 Products by Revenue**

| Rank | Product ID | Product Name | Revenue (USD) |
|------|------------|--------------|---------------|
| 1    | 29         | Carbon Frame MTB | $6,932,400 |
| 2    | 35         | E-Motor 750W | $4,138,480 |

**What this means for you**
- Revenue drivers...
- Stock focus...
```

### Conversation Context

The backend automatically includes the last 10 messages in each request, allowing the agent to:
- Remember previous questions
- Provide contextual follow-ups
- Reference earlier parts of the conversation

Example conversation:
```
User: "What are my top products?"
Agent: [Shows top 5 products]

User: "Show me inventory levels for these"
Agent: [Uses context to show inventory for the previously mentioned products]
```

### Error Handling

The system handles:
- **Network errors** - Connection failures to model serving
- **Timeout errors** - Long-running queries (120s timeout)
- **Authentication errors** - Invalid tokens or credentials
- **API errors** - Malformed responses or server errors

Errors are displayed in the chat with:
- User-friendly error messages
- Technical details for debugging
- Retry capability

## Migration from Genie API

### What Changed

1. **Backend endpoint**: `/api/genie/send-message` → `/api/agent/send-message`
2. **Request format**: 
   - Before: `{message: string, conversation_id?: string}`
   - After: `{messages: [{role, content}]}`
3. **No polling**: Single request/response instead of create + poll
4. **No conversation ID**: History managed by sending message array
5. **Richer responses**: Markdown formatted with tables

### What Stayed the Same

- Frontend chat UI (FloatingGenie wrapper)
- Chat button appearance
- Message history display
- Suggested questions
- User experience

### Old Genie Integration (Deprecated)

The old Genie integration is still available in:
- `server/routers/genie.py`
- `client/src/components/GenieChat.tsx`

To switch back, update `FloatingGenie.tsx`:
```typescript
import GenieChat from './GenieChat';  // Instead of AgentChat
```

## Troubleshooting

### "Authentication not configured properly"

**Cause**: Missing DATABRICKS_HOST or DATABRICKS_TOKEN

**Solution**: 
```bash
# Add to .env.local
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com/
DATABRICKS_TOKEN=your-token
```

### "Model Serving endpoint not configured"

**Cause**: Missing MODEL_SERVING_ENDPOINT environment variable

**Solution**:
```bash
# Add to .env.local
MODEL_SERVING_ENDPOINT=https://your-workspace.cloud.databricks.com/serving-endpoints/your-agent/invocations
```

### Request timeout (504 error)

**Cause**: Agent taking longer than 120 seconds to respond

**Solutions**:
- Increase timeout in `agent.py` (line 40): `httpx.AsyncClient(timeout=180.0)`
- Optimize your queries in the agent
- Check Genie space performance

### "No output received from model serving endpoint"

**Cause**: Model serving response format changed

**Solution**: Check the response structure matches the expected format in `agent.py` lines 89-109

### Tables not rendering correctly

**Cause**: Markdown table format not recognized

**Solution**: The agent should output tables in this format:
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Value 1  | Value 2  |
```

Ensure separator row with dashes is included.

## Performance

- **Response time**: ~3-10 seconds (depends on query complexity)
- **Timeout**: 120 seconds
- **Concurrent users**: Limited by model serving endpoint capacity
- **Rate limits**: Depends on Databricks workspace limits

## Next Steps

1. **Add streaming responses** - Use SSE for real-time message updates
2. **Add message feedback** - Thumbs up/down for quality tracking
3. **Add conversation export** - Download chat history
4. **Add voice input** - Speech-to-text for queries
5. **Add suggested follow-ups** - Agent-generated next questions
6. **Add visualization** - Charts and graphs in chat responses

## Resources

- [Databricks Model Serving Documentation](https://docs.databricks.com/en/machine-learning/model-serving/index.html)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [Databricks Genie](https://docs.databricks.com/en/genie/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Markdown Libraries](https://github.com/remarkjs/react-markdown)

