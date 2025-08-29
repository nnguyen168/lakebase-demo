# Lakebase Inventory Management Application

## Overview
This is a modern inventory management application built with:
- **Backend**: FastAPI with Python, using mock Databricks Lakebase connection
- **Frontend**: React with TypeScript, Vite, and shadcn/ui components
- **Database**: Designed for Databricks Lakebase (currently using mock data)

## Application Features

### Order Management Tab
- **KPI Cards**:
  - Order Management: Shows total orders, pending, approved, shipped counts
  - Stock Management Alert: Shows low stock, out of stock, and reorder alerts
  
- **Order Management Table**: Displays recent orders with:
  - Order number, product, quantity, store, requested by, order date, status
  
- **Inventory Forecast Table**: Shows inventory predictions with:
  - Item ID, item name, current stock, 30-day forecast, status, and recommended action

## Running the Application

### Start Backend Server:
```bash
# Using mock database (no Lakebase connection required)
uv run python dev_server.py
```
Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Start Frontend:
```bash
cd client
bun run dev
```
Frontend runs at: http://localhost:5173

## API Endpoints

### Orders API
- `GET /api/orders/` - Get list of orders
- `GET /api/orders/kpi` - Get order management KPIs
- `GET /api/orders/{order_id}` - Get specific order
- `POST /api/orders/` - Create new order
- `PUT /api/orders/{order_id}` - Update order
- `DELETE /api/orders/{order_id}` - Cancel order

### Inventory API
- `GET /api/inventory/forecast` - Get inventory forecast
- `GET /api/inventory/alerts/kpi` - Get stock alert KPIs
- `GET /api/inventory/history` - Get inventory transaction history
- `PUT /api/inventory/forecast/{forecast_id}` - Update forecast
- `POST /api/inventory/history` - Create inventory transaction

## Database Schema (for Lakebase)

### Tables:
1. **customers** - Customer information
2. **products** - Product catalog
3. **orders** - Order transactions
4. **inventory_history** - Inventory transaction logs
5. **inventory_forecast** - Stock predictions and reorder points

## Configuration

### Environment Variables (.env.local)
```
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com/
DATABRICKS_TOKEN=your-token
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_CATALOG=main
DATABRICKS_SCHEMA=inventory_demo
```

## Development Mode
The application currently runs with mock data for development. To connect to actual Lakebase:
1. Update `.env.local` with your Databricks credentials
2. Use `server/database.py` instead of `server/mock_database.py`
3. Run `uv run python scripts/init_database.py` to create tables and seed data

## Project Structure
```
lakebase-demo/
├── server/                 # Backend FastAPI application
│   ├── app.py             # Main application
│   ├── models.py          # Pydantic models
│   ├── database.py        # Lakebase connection (production)
│   ├── mock_database.py   # Mock database (development)
│   └── routers/           # API endpoints
│       ├── orders.py
│       └── inventory.py
├── client/                 # Frontend React application
│   └── src/
│       ├── pages/
│       │   └── OrderManagement.tsx
│       └── components/
│           └── ui/        # shadcn/ui components
└── scripts/               # Utility scripts
    └── init_database.py   # Database initialization
```

## Key Technologies
- **Databricks Lakebase**: OLTP database for transactional data
- **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- **React + TypeScript**: Type-safe frontend development
- **shadcn/ui**: Modern React component library
- **Tailwind CSS**: Utility-first CSS framework