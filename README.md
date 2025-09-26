# Lakebase Demo: Smart Inventory Management System

A comprehensive inventory management demonstration built with Databricks, FastAPI, and React. This project showcases modern lakehouse architecture with realistic historical data generation, ML-ready datasets, and intelligent inventory forecasting using Databricks Lakebase.

## 🚀 Key Features

### 📊 **AI-Powered Inventory Analytics**
- **Historical data generation**: 3+ years of realistic transaction patterns
- **ML training datasets**: 134,685+ daily inventory records across 123 time series
- **Demand forecasting**: AI-powered predictions with seasonality and trends
- **Smart reordering**: Intelligent reorder point optimization with urgency levels

### 🏭 **Multi-Warehouse Operations**
- **Three warehouses**: Lyon (France), Hamburg (Germany), Milan (Italy)
- **Real-time tracking**: Live inventory levels across all locations
- **Cross-warehouse analytics**: Comparative performance and capacity utilization
- **Location-specific patterns**: Different demand patterns per warehouse

### 📈 **Comprehensive Data Generation**
- **108,280+ transactions** spanning 1,095 days with realistic patterns
- **41 products** across 8 categories (e-bike components)
- **Balanced inventory**: Lean inventory management with controlled growth
- **Smooth sales patterns**: Granular transaction data for ML training
- **Business events**: Black Friday, seasonal trends, supply disruptions

### 🔄 **Transaction Management**
- **Three transaction types**: Inbound, sales, adjustments
- **Status tracking**: Pending → Confirmed → Processing → Shipped → Delivered
- **Audit trails**: Complete transaction history with timestamps
- **Inventory balancing**: Automatic reorders with cooldown periods

### 📱 **Modern Web Interface**
- **React + TypeScript**: Modern, responsive dashboard
- **Real-time updates**: Live inventory tracking and alerts
- **Auto-generated API client**: Type-safe FastAPI integration
- **Databricks Apps**: Native lakehouse application deployment

## 🛠️ Technology Stack

### Databricks Platform
- **Databricks Lakebase**: PostgreSQL-compatible data lakehouse
- **Databricks Apps**: Native application deployment and hosting
- **Databricks Workflows**: Automated data generation and setup jobs
- **Unity Catalog**: Centralized data governance and management

### Backend
- **FastAPI**: High-performance Python web framework
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM with Lakebase integration
- **Pandas/NumPy**: Data generation and analysis

### Frontend
- **React 18**: Modern component-based UI
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Beautiful component library

### Data & ML
- **Historical datasets**: 3 years of inventory data in Delta tables
- **Time series**: Daily inventory levels for forecasting
- **Feature engineering**: Lag features, rolling statistics
- **Analysis tools**: Comprehensive data validation notebooks

## 📋 Quick Start

### Prerequisites
- **Databricks workspace** with Unity Catalog enabled
- **Lakebase instance** provisioned in your workspace
- **Databricks CLI** installed and configured
- **Python 3.8+** with `databricks-cli` package

### 1. Clone and Configure
```bash
# Clone repository
git clone <repository-url>
cd lakebase-demo

# Configure Databricks CLI
databricks configure

# Verify connection
databricks workspace list
```

### 2. Deploy Bundle to Databricks

1. Create a catalog in Unity Catalog
2. Create a Lakebase instance (1 CU should be sufficient)
3. Modify variables in `databricks.yml` to:
   1. set `catalog_name` and `lakebase_instance_name`.
   2. set the URL of your workspace (`workspace.host_name`)
4. Deploy the bundle

```bash
# Review bundle configuration
cat databricks.yml

# Deploy bundle (creates compute, jobs, and resources)
databricks bundle deploy

# Verify deployment
databricks bundle status
```

### 3. Run Setup Job to Generate Data

Run from Databricks Jobs UI.

### 4. Deploy Databricks App
```bash
# Navigate to app directory
cd app/smart_stock

# Deploy Databricks App
databricks apps deploy smart-stock

# Get app URL
databricks apps list
```
