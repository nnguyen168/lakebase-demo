# SmartStock: AI-Powered Inventory Management on Databricks

A production-ready inventory management system showcasing **Databricks Lakebase**, **Databricks Apps**, and **AI Agents** with tool-calling capabilities.

![Databricks](https://img.shields.io/badge/Databricks-Platform-orange)
![Lakebase](https://img.shields.io/badge/Lakebase-PostgreSQL-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-green)

## 🎯 What This Demo Shows

| Capability | Databricks Feature |
|------------|-------------------|
| **OLTP Database** | Lakebase (PostgreSQL-compatible) |
| **App Hosting** | Databricks Apps |
| **AI Agent** | Foundation Models + Tool Calling |
| **NL→SQL** | Genie API Integration |
| **Data Governance** | Unity Catalog |
| **ML Pipeline** | Notebooks + Workflows |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABRICKS PLATFORM                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────────────┐  │
│   │  React UI   │────▶│   FastAPI   │────▶│   SmartStock AI Agent   │  │
│   │  (Vite)     │     │   Backend   │     │   (Tool Calling LLM)    │  │
│   └─────────────┘     └──────┬──────┘     └───────────┬─────────────┘  │
│                              │                        │                 │
│                              ▼                        ▼                 │
│   ┌──────────────────────────────────────┐    ┌─────────────────────┐  │
│   │           LAKEBASE (PostgreSQL)      │    │    Genie API        │  │
│   │  • products    • inventory           │    │    (NL → SQL)       │  │
│   │  • warehouses  • transactions        │    └─────────────────────┘  │
│   │  • forecasts   • sales_history       │                              │
│   └──────────────────────────────────────┘                              │
│                              ▲                                          │
│                              │                                          │
│   ┌──────────────────────────┴───────────────────────────────────────┐ │
│   │                    UNITY CATALOG (smart_stock)                    │ │
│   │         silver schema  │  gold schema  │  forecast schema         │ │
│   └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## ✨ Key Features

### 🤖 AI Agent with Actions
The SmartStock AI Agent can **analyze AND take actions**:

```
User: "What's wrong with my inventory?"
  → Agent calls get_critical_inventory_alerts tool
  → Shows items at risk of stockout

User: "What's the financial impact?"
  → Agent calls estimate_stockout_impact tool
  → Shows €XX,XXX potential lost revenue

User: "What are my options?"
  → Agent presents 3 supplier options with pricing

User: "Proceed with Option A"
  → Agent calls resolve_inventory_alert tool (multiple times)
  → Creates actual purchase orders in the database ✅
```

### 📊 Dashboard Features
- **KPI Cards**: Orders, stock health, alerts
- **Multi-warehouse**: Lyon 🇫🇷, Hamburg 🇩🇪, Milan 🇮🇹
- **Inventory Forecast**: 30-day predictions with urgency levels
- **Transaction History**: Full audit trail

### 📈 Data Pipeline
- **108K+ transactions** over 3 years
- **41 products** across 8 categories (e-bike components)
- **ML-ready datasets**: Daily inventory levels for forecasting

## 📁 Project Structure

```
lakebase-demo/
├── databricks.yml              # Asset Bundle config
├── resources/                  # Jobs, schemas, volumes
│
├── src/                        # Data pipelines
│   ├── lakebase_setup/         # Table creation & data generation
│   ├── etl/                    # Bronze → Silver → Gold
│   ├── forecasting_ml/         # ML model training
│   └── dashboard/              # Databricks SQL dashboard
│
└── app/smart_stock/            # Full-stack application
    ├── app.yaml                # Databricks Apps config
    ├── server/                 # FastAPI backend
    │   ├── routers/            # API endpoints
    │   └── services/agent.py   # AI Agent (1100+ lines)
    └── client/                 # React frontend
        └── src/
            ├── pages/          # Dashboard views
            └── components/     # UI components
```

## 🚀 Quick Start

### Prerequisites
- Databricks workspace with **Unity Catalog** enabled
- **Lakebase instance** provisioned
- **Databricks CLI** installed (`pip install databricks-cli`)

### 1. Configure Variables

Edit `databricks.yml`:
```yaml
variables:
  catalog_name: smart_stock        # Your catalog name
  lakebase_instance_name: smart-stock-db

targets:
  dev:
    workspace:
      host: https://your-workspace.cloud.databricks.com/
```

### 2. Deploy Asset Bundle

```bash
# Deploy compute, jobs, schemas
databricks bundle deploy

# Verify
databricks bundle status
```

### 3. Initialize Data

Run the **Full Reset Job** from Databricks Jobs UI to:
- Create tables in Lakebase
- Generate 3 years of sample data
- Train ML models
- Populate forecasts

### 4. Deploy the App

```bash
cd app/smart_stock

# Edit app.yaml with your Lakebase connection details
# Then deploy:
databricks apps deploy smart-stock

# Get the URL:
databricks apps list
```

## 🎮 Demo Flow

1. **Open the app** → Click "Ask your AI" button
2. **Ask**: "Hello SmartStock AI, what's wrong with my inventory?"
3. **Click** quick action buttons to progress through:
   - 💰 Financial impact analysis
   - 📦 Reorder options (A/B/C)
   - ⚡ Execute orders
4. **Watch** the agent create real purchase orders in the database

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind, shadcn/ui |
| **Backend** | FastAPI, Pydantic, uvicorn |
| **Database** | Databricks Lakebase (PostgreSQL) |
| **AI** | Databricks Foundation Models (GPT-OSS-120B) |
| **Analytics** | Genie API, Unity Catalog |
| **Deployment** | Databricks Apps, Asset Bundles |

## 🔧 Local Development

```bash
cd app/smart_stock

# Backend (terminal 1)
uv run python dev_server.py
# → http://localhost:8000/docs

# Frontend (terminal 2)
cd client && bun run dev
# → http://localhost:5173
```

## 📚 Key Files

| File | Purpose |
|------|---------|
| `server/services/agent.py` | AI Agent with tool-calling |
| `server/routers/agent.py` | Agent API endpoint |
| `client/src/components/AgentChat.tsx` | Chat UI with quick actions |
| `src/lakebase_setup/data_generator/` | Sample data generation |
| `src/forecasting_ml/` | ML model training notebooks |

## 📝 License

See [LICENSE.md](app/smart_stock/LICENSE.md)

---

**Built with ❤️ to showcase Databricks Lakebase + AI Agents**
