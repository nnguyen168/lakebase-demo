# SmartStock Chatbot Architecture

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                         USER BROWSER                                    │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  SmartStockDashboard (Main App)                                  │ │
│  │                                                                   │ │
│  │  ┌─────────────────────────────────────────────────────────────┐ │ │
│  │  │                                                             │ │ │
│  │  │  FloatingGenie Component                                    │ │ │
│  │  │  - Floating chat button (bottom-right)                      │ │ │
│  │  │  - Minimize/Maximize controls                               │ │ │
│  │  │  - Modal overlay                                            │ │ │
│  │  │                                                             │ │ │
│  │  │  ┌────────────────────────────────────────────────────────┐ │ │ │
│  │  │  │                                                        │ │ │ │
│  │  │  │  AgentChat Component (NEW!)                           │ │ │ │
│  │  │  │                                                        │ │ │ │
│  │  │  │  Features:                                             │ │ │ │
│  │  │  │  • Message history                                     │ │ │ │
│  │  │  │  • Markdown rendering (bold, tables)                   │ │ │ │
│  │  │  │  • User input with Enter key support                   │ │ │ │
│  │  │  │  • Loading states                                      │ │ │ │
│  │  │  │  • Error handling                                      │ │ │ │
│  │  │  │  • Suggested questions                                 │ │ │ │
│  │  │  │  • New chat button                                     │ │ │ │
│  │  │  │                                                        │ │ │ │
│  │  │  └────────────────────────────────────────────────────────┘ │ │ │
│  │  │                                                             │ │ │
│  │  └─────────────────────────────────────────────────────────────┘ │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST
                                    │ /api/agent/send-message
                                    │ Content-Type: application/json
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                   FastAPI BACKEND (Python)                              │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  server/app.py (Main FastAPI App)                                │ │
│  │                                                                   │ │
│  │  • CORS middleware                                               │ │
│  │  • Static file serving                                           │ │
│  │  • Health checks                                                 │ │
│  │  • Router registration                                           │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│                                    │ Includes routers                   │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  server/routers/agent.py (NEW!)                                  │ │
│  │                                                                   │ │
│  │  Routes:                                                         │ │
│  │  • POST /api/agent/send-message                                  │ │
│  │  • GET  /api/agent/health                                        │ │
│  │                                                                   │ │
│  │  Functions:                                                      │ │
│  │  1. Extract conversation history from request                    │ │
│  │  2. Get auth config (host, token, endpoint)                      │ │
│  │  3. Format payload for model serving                             │ │
│  │  4. Make HTTP POST to endpoint                                   │ │
│  │  5. Parse response and extract content                           │ │
│  │  6. Handle errors and timeouts                                   │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST (async with httpx)
                                    │ Authorization: Bearer <token>
                                    │ Content-Type: application/json
                                    │ Timeout: 120s
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│              DATABRICKS MODEL SERVING ENDPOINT                          │
│                                                                         │
│  URL: https://workspace.cloud.databricks.com/serving-endpoints/        │
│       agents_demo_nnguyen-smartstock-assistant/invocations             │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  Agent Runtime                                                    │ │
│  │                                                                   │ │
│  │  1. Receives request with conversation history                   │ │
│  │  2. Processes natural language query                             │ │
│  │  3. Uses MCP tools to interact with Genie                        │ │
│  │  4. Generates and executes SQL                                   │ │
│  │  5. Formats results as markdown                                  │ │
│  │  6. Returns structured response                                  │ │
│  │                                                                   │ │
│  │  ┌─────────────────────────────────────────────────────────────┐ │ │
│  │  │                                                             │ │ │
│  │  │  Managed MCP Server for Genie                               │ │ │
│  │  │                                                             │ │ │
│  │  │  • Natural language understanding                           │ │ │
│  │  │  • SQL generation                                           │ │ │
│  │  │  • Query execution                                          │ │ │
│  │  │  • Result formatting                                        │ │ │
│  │  │                                                             │ │ │
│  │  │  Connected to:                                              │ │ │
│  │  │  ├─ Genie Space (01f0b899...)                               │ │ │
│  │  │  └─ Unity Catalog (smart_stock)                             │ │ │
│  │  │                                                             │ │ │
│  │  └─────────────────────────────────────────────────────────────┘ │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│                                    │ Queries                            │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  Genie Space                                                      │ │
│  │  ID: 01f0b8993ae91634b351d60035aa7c31                            │ │
│  │                                                                   │ │
│  │  • Semantic understanding of SmartStock domain                   │ │
│  │  • Access to inventory database schema                           │ │
│  │  • SQL generation and optimization                               │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                    │                                    │
│                                    │ SQL Queries                        │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                                                                   │ │
│  │  Unity Catalog: smart_stock                                      │ │
│  │                                                                   │ │
│  │  Tables:                                                         │ │
│  │  • products (41 e-bike components)                               │ │
│  │  • inventory (stock levels by warehouse)                         │ │
│  │  • warehouses (Lyon, Hamburg, Milan)                             │ │
│  │  • inventory_transactions (108K+ transactions)                   │ │
│  │  • inventory_forecast (ML predictions)                           │ │
│  │  • sales_history (3 years of weekly sales)                       │ │
│  │                                                                   │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Asks Question
```
User types: "What are my top 5 products by revenue?"
           ↓
AgentChat captures input and adds to message history
```

### 2. Frontend Sends Request
```javascript
POST /api/agent/send-message
{
  "messages": [
    { "role": "user", "content": "What are my top 5 products by revenue?" }
  ]
}
```

### 3. Backend Processes Request
```python
# server/routers/agent.py

1. Validate authentication (token, host)
2. Get MODEL_SERVING_ENDPOINT from env
3. Format payload:
   {
     "input": [
       {"role": "user", "content": "What are my top 5 products by revenue?"}
     ]
   }
4. POST to model serving endpoint with Bearer token
5. Wait up to 120 seconds
6. Parse response
```

### 4. Model Serving Executes Agent
```
Agent receives request
     ↓
Uses MCP to query Genie
     ↓
Genie generates SQL:
  SELECT 
    product_id,
    product_name,
    SUM(weekly_sales * price) as revenue
  FROM sales_history
  JOIN products USING (product_id)
  GROUP BY product_id, product_name
  ORDER BY revenue DESC
  LIMIT 5
     ↓
Executes on Unity Catalog
     ↓
Formats results as markdown table
     ↓
Returns to backend
```

### 5. Backend Returns to Frontend
```json
{
  "message_id": "chatcmpl_abc123",
  "content": "**Top 5 Products by Revenue**\n\n| Rank | Product | Revenue |\n...",
  "status": "completed",
  "error": null
}
```

### 6. Frontend Renders Response
```
AgentChat receives response
     ↓
Parses markdown content
     ↓
Renders:
  - Bold headings
  - Tables with data
  - Paragraphs
     ↓
Displays in chat bubble
     ↓
Scrolls to bottom
```

## Comparison: Old vs New

### OLD: Genie Conversational API
```
User → Frontend → Backend → Genie API (start conversation)
                              ↓
                         conversation_id
                              ↓
                    Genie API (send message)
                              ↓
                         message_id
                              ↓
                    Poll every 3s (up to 20 times)
                              ↓
                    Check status (PENDING/PROCESSING/COMPLETED)
                              ↓
                    Fetch query results (separate call)
                              ↓
                    Parse and combine data
                              ↓
                    Backend → Frontend → User

Total: 3-20 API calls, 10-60 seconds
```

### NEW: Model Serving Agent
```
User → Frontend → Backend → Model Serving Endpoint
                              ↓
                         Agent processes
                              ↓
                         Returns response
                              ↓
                    Backend → Frontend → User

Total: 1 API call, 3-10 seconds
```

## Component Interactions

### Frontend Components
```
App.tsx
  └─ SmartStockDashboard.tsx (Main dashboard)
       ├─ Homepage (KPIs, charts)
       ├─ Inventory Transactions
       ├─ Inventory Analytics
       ├─ Inventory Forecast
       └─ FloatingGenie.tsx (Always visible)
            └─ AgentChat.tsx (Modal overlay)
                 ├─ Message list
                 ├─ Markdown renderer
                 ├─ Input box
                 └─ Send button
```

### Backend Routers
```
server/app.py (Main FastAPI app)
  ├─ /api/orders → orders.py
  ├─ /api/inventory → inventory.py
  ├─ /api/products → products.py
  ├─ /api/transactions → transactions.py
  ├─ /api/warehouses → warehouses.py
  ├─ /api/agent → agent.py (NEW!)
  └─ /api/genie → genie.py (OLD - kept for compatibility)
```

## Configuration Flow

### Development (.env.local)
```
Developer sets:
  DATABRICKS_HOST=...
  DATABRICKS_TOKEN=...
  MODEL_SERVING_ENDPOINT=...
       ↓
server/app.py loads .env.local
       ↓
Environment variables available to agent.py
       ↓
agent.py uses for authentication and endpoint URL
```

### Production (app.yaml)
```
app.yaml defines:
  env:
    - name: DATABRICKS_HOST
      value: ...
    - name: DATABRICKS_TOKEN
      value: ...
    - name: MODEL_SERVING_ENDPOINT
      value: ...
       ↓
Databricks Apps injects as environment variables
       ↓
agent.py reads from os.getenv()
```

## Error Handling Flow

```
User sends message
     ↓
Frontend validation
  └─ Error: Empty message → Show inline error
     ↓
Backend receives request
     ↓
Authentication check
  └─ Error: Missing token → HTTP 500 "Authentication not configured"
     ↓
Model serving request
  ├─ Timeout (120s) → HTTP 504 "Request timed out"
  ├─ Network error → HTTP 503 "Failed to connect"
  └─ Server error (500) → HTTP 500 "Failed to communicate with agent"
     ↓
Response parsing
  └─ Error: Invalid format → HTTP 500 "No output received"
     ↓
Frontend receives response
  └─ Error: status !== 200 → Display error message in chat
     ↓
User sees error message with option to retry
```

## Security Architecture

```
Frontend (Browser)
  ↓ HTTPS only
Backend (FastAPI)
  ↓ Bearer token (from env)
Model Serving Endpoint
  ↓ Databricks authentication
Genie Space
  ↓ Unity Catalog permissions
Unity Catalog
  ↓ RBAC
Data Tables
```

All secrets stored in:
- Development: `.env.local` (gitignored)
- Production: `app.yaml` or Databricks Secrets

## Monitoring & Observability

```
Frontend Logs
  • Browser console (errors, network calls)
  • React DevTools (component state)
     ↓
Backend Logs
  • uvicorn access logs
  • Python logger (agent.py)
  • FastAPI /docs for API testing
     ↓
Databricks Logs
  • Model serving endpoint metrics
  • Request/response logs
  • Error traces
     ↓
Genie Logs
  • Query execution logs
  • SQL generated
  • Performance metrics
```

## Deployment Architecture

### Local Development
```
Developer Machine
  ├─ Terminal 1: Backend (uvicorn)
  │    └─ Port 8000
  ├─ Terminal 2: Frontend (Vite)
  │    └─ Port 5173
  └─ Browser: http://localhost:5173
       └─ Proxies API to localhost:8000
```

### Production (Databricks Apps)
```
Databricks Apps Platform
  ├─ Frontend (React build)
  │    └─ Served from /build
  ├─ Backend (FastAPI)
  │    └─ Port 8000 (internal)
  └─ Single URL
       ├─ / → Frontend (index.html)
       └─ /api/* → Backend routes
```

---

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Simple request/response flow
- ✅ Easy to debug and monitor
- ✅ Production-ready scalability
- ✅ Secure authentication

