# Quick Start: Agent Chatbot

Get the new agent-powered chatbot running in 5 minutes.

## Step 1: Add Environment Variable

Create or update `.env.local` in `app/smart_stock/`:

```bash
# Copy the existing .env.local and add this line:
MODEL_SERVING_ENDPOINT=https://fe-vm-nam-nguyen-workspace-classic.cloud.databricks.com/serving-endpoints/agents_demo_nnguyen-smartstock-assistant/invocations
```

Your `.env.local` should have:
```bash
DATABRICKS_HOST=${DATABRICKS_HOST}
DATABRICKS_TOKEN=${DATABRICKS_TOKEN}

# Plus your DB configuration
DB_HOST=...
DB_PORT=5432
# etc...
```

## Step 2: Test the Endpoint

```bash
cd app/smart_stock
uv run python test_agent_endpoint.py
```

✅ Expected output:
```
Testing agent endpoint...
Status Code: 200
✅ Success! Response:
...
ASSISTANT RESPONSE:
================================================================================
**Top 5 Products by Revenue**
...
```

## Step 3: Start the Application

### Terminal 1 - Backend:
```bash
cd app/smart_stock
uv run uvicorn server.app:app --reload
```

### Terminal 2 - Frontend:
```bash
cd app/smart_stock/client
bun run dev
```

## Step 4: Test the Chat

1. Open browser: http://localhost:5173
2. Click the **chat button** (bottom-right corner with sparkle icon)
3. Type: **"What are my top 5 products by revenue?"**
4. Wait 3-10 seconds
5. You should see a nicely formatted table with product data!

## Step 5: Deploy (Optional)

```bash
cd app/smart_stock

# Build frontend
cd client && bun run build && cd ..

# Deploy to Databricks
databricks apps deploy smart-stock

# Check status
./app_status.sh
```

## Troubleshooting

### ❌ "Authentication not configured properly"
**Fix**: Check that `DATABRICKS_HOST` and `DATABRICKS_TOKEN` are set in `.env.local`

### ❌ "Model Serving endpoint not configured"
**Fix**: Check that `MODEL_SERVING_ENDPOINT` is set in `.env.local`

### ❌ Connection timeout
**Fix**: Verify the model serving endpoint URL is correct and accessible

### ❌ "No output received"
**Fix**: Test the endpoint with `test_agent_endpoint.py` - if it works there, restart the backend

## Quick Commands Reference

```bash
# Test endpoint
uv run python test_agent_endpoint.py

# Start backend
uv run uvicorn server.app:app --reload

# Start frontend (in client/)
bun run dev

# Check health
curl http://localhost:8000/api/agent/health

# Test API
curl -X POST http://localhost:8000/api/agent/send-message \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What are my top products?"}]}'

# Build frontend
cd client && bun run build

# Deploy
databricks apps deploy smart-stock

# View logs
uv run python dba_logz.py <app-url>
```

## Example Questions to Try

1. **"What are my top 5 products by revenue?"**
   - Shows formatted table with revenue data

2. **"Show me current critical stock items"**
   - Lists products below reorder point

3. **"What is the inventory turnover rate?"**
   - Calculates and explains turnover metrics

4. **"Which products need restocking in the next 30 days?"**
   - Forecasts demand and suggests reorders

5. **"What's the total value of inventory across all warehouses?"**
   - Aggregates inventory value

## Chat Features

✨ **Markdown Formatting**
- Bold text: **Important**
- Tables with data
- Bullet points

💬 **Conversation Context**
- Remembers last 10 messages
- Can answer follow-up questions
- Example:
  ```
  You: "What are my top products?"
  Bot: [Shows top 5 products]
  
  You: "Show inventory for these"
  Bot: [Shows inventory for the 5 products mentioned above]
  ```

🔄 **New Chat**
- Click "New Chat" to start fresh conversation

## Success! 🎉

Your agent-powered chatbot is now running with:
- Faster responses (3-10s)
- Rich markdown formatting
- Contextual conversations
- Production-ready model serving

For more details, see:
- `AGENT_INTEGRATION.md` - Complete integration guide
- `MIGRATION_SUMMARY.md` - What changed from Genie API

