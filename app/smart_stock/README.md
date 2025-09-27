# 📦 Smart Stock - Inventory Management System

A modern, AI-powered inventory management application built on Databricks Apps platform, featuring real-time stock tracking, intelligent forecasting, and comprehensive order management.

![Databricks Apps](https://img.shields.io/badge/Databricks-Apps-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Lakebase-blue)

## 🎯 Overview

Smart Stock is a full-stack inventory management solution that helps businesses optimize their stock levels, predict demand, and streamline order processing. Built specifically for the Databricks Apps platform, it leverages modern cloud technologies to deliver real-time insights and automated inventory control.

### Key Features

- **📊 Real-Time Dashboard** - Monitor inventory levels, orders, and KPIs in real-time
- **🔮 AI-Powered Forecasting** - 30-day inventory predictions with ML-based recommendations
- **📦 Order Management** - Complete order lifecycle from creation to delivery
- **🚨 Smart Alerts** - Automatic low stock warnings and reorder point notifications
- **💰 Transaction Tracking** - Full audit trail of all inventory movements
- **📈 Analytics & Reporting** - Comprehensive insights into inventory performance

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** (Databricks Lakebase) - Transactional database
- **Pydantic** - Data validation and serialization
- **uvicorn** - ASGI server

**Frontend:**
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool
- **shadcn/ui** - Beautiful component library
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization

**Infrastructure:**
- **Databricks Apps** - Deployment platform
- **uv** - Python package management
- **bun** - JavaScript runtime & package manager

## 🚀 Getting Started

### Prerequisites

- Databricks workspace with Apps enabled
- Personal Access Token (PAT) or CLI profile
- Node.js 18+ and bun installed
- Python 3.11+ (managed by uv)

### Quick Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd lakebase-demo/app/smart_stock
```

2. **Run the setup script:**
```bash
./setup.sh
```

This will:
- Install all dependencies
- Configure Databricks authentication
- Set up environment variables
- Prepare the application for development

3. **Start development servers:**
```bash
./watch.sh
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📱 Application Features

### Smart Stock Dashboard
The main dashboard provides a comprehensive overview of your inventory system with:
- **Order Statistics**: Total, pending, approved, and shipped orders
- **Stock Health**: Low stock alerts, out-of-stock items, reorder notifications
- **Recent Orders**: Real-time order tracking table
- **Inventory Forecast**: AI-powered 30-day predictions

### Order Management
Complete order lifecycle management:
- Create and track customer orders
- Approval workflow for large orders
- Shipping and delivery tracking
- Order history and analytics

### Inventory Control
Real-time inventory tracking:
- Current stock levels by product
- Automatic reorder point calculations
- Stock movement history
- Location-based inventory tracking

### Transaction History
Comprehensive audit trail:
- All inventory movements (inbound, sales, adjustments)
- User activity tracking
- Transaction search and filtering
- Export capabilities for reporting

## 🗄️ Database Schema

The application uses PostgreSQL (Databricks Lakebase) with the following core tables:

- **products** - Product catalog with SKU, pricing, and specifications
- **inventory** - Current stock levels and locations
- **orders** - Customer orders and status tracking
- **transactions** - Inventory movement history
- **inventory_forecast** - AI-generated predictions and recommendations
- **users** - User management and authentication

## 🔧 Development

### Project Structure
```
smart_stock/
├── server/                    # FastAPI backend
│   ├── app.py                # Main application
│   ├── models.py             # Pydantic models
│   ├── database.py           # Database connections
│   ├── routers/              # API endpoints
│   │   ├── orders.py         # Order management
│   │   ├── inventory.py      # Stock control
│   │   ├── products.py       # Product catalog
│   │   ├── transactions.py   # Transaction history
│   │   └── user.py          # User management
│   └── services/             # Business logic
│
├── client/                    # React frontend
│   ├── src/
│   │   ├── pages/           # Application pages
│   │   │   ├── SmartStockDashboard.tsx
│   │   │   ├── OrderManagement.tsx
│   │   │   ├── InventoryDashboard.tsx
│   │   │   └── TransactionsDashboard.tsx
│   │   ├── components/      # Reusable components
│   │   └── lib/            # Utilities and helpers
│   └── package.json
│
├── scripts/                   # Automation scripts
├── app.yaml                  # Databricks Apps config
└── pyproject.toml           # Python dependencies
```

### API Endpoints

#### Orders
- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Cancel order
- `GET /api/orders/kpi` - Order KPI metrics

#### Inventory
- `GET /api/inventory/` - Current stock levels
- `GET /api/inventory/forecast` - AI predictions
- `PUT /api/inventory/forecast/{id}` - Update forecast
- `GET /api/inventory/alerts/kpi` - Stock alert metrics
- `GET /api/inventory/history` - Movement history

#### Products
- `GET /api/products/` - Product catalog
- `POST /api/products/` - Add new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Remove product

#### Transactions
- `GET /api/transactions/` - Transaction history
- `POST /api/transactions/` - Record transaction
- `GET /api/transactions/summary` - Analytics

### Development Commands

```bash
# Start development servers
./watch.sh

# Format code
./fix.sh

# Deploy to Databricks Apps
./deploy.sh

# Check deployment status
./app_status.sh

# View logs (after deployment)
uv run python dba_logz.py <app-url>
```

## 🚀 Deployment

### Deploy to Databricks Apps

1. **Configure environment:**
```bash
# Edit .env.local with your credentials
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token
DATABRICKS_APP_NAME=smart-stock
```

2. **Deploy the application:**
```bash
./deploy.sh --create  # First deployment
./deploy.sh          # Subsequent updates
```

3. **Monitor deployment:**
```bash
# Check status
./app_status.sh

# View logs
uv run python dba_logz.py <app-url> --duration 60
```

## 🔐 Environment Configuration

Create a `.env.local` file with:

```env
# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
DATABRICKS_APP_NAME=smart-stock

# Database Configuration (auto-configured in app.yaml)
DB_HOST=your-lakebase-host
DB_PORT=5432
DB_NAME=databricks_postgres
DB_USER=lakebase_demo_app
DB_PASSWORD=your-password
```

## 🧪 Testing

### Local Testing
```bash
# Test backend API
uv run python test_db.py

# Test deployed app
uv run python test_deployed_app.py

# API testing
curl http://localhost:8000/api/orders/kpi
```

### Frontend Testing
```bash
cd client
bun test
```

## 📈 Monitoring & Debugging

### View Application Logs
```bash
# Real-time log streaming
uv run python dba_logz.py <app-url> --duration 60

# Search specific patterns
uv run python dba_logz.py <app-url> --search "ERROR" --duration 30

# Browser-based logs (requires authentication)
https://<app-url>/logz
```

### Local Debugging
```bash
# Check development logs
tail -f /tmp/databricks-app-watch.log

# Run with verbose output
./deploy.sh --verbose
./app_status.sh --verbose
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `./fix.sh` to format code
5. Test your changes locally
6. Submit a pull request

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Databricks Apps Guide](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [React Documentation](https://react.dev/)
- [shadcn/ui Components](https://ui.shadcn.com/)

## 📝 License

See [LICENSE.md](LICENSE.md) for details.

## 🆘 Support

For issues or questions:
- Check the [documentation](docs/)
- Review [common issues](#common-issues)
- Open an issue on GitHub

---

**Built with ❤️ for modern inventory management on Databricks Apps**