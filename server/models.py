"""Database models for Lakebase inventory management system."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class InventoryStatus(str, Enum):
    """Inventory status enumeration."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    REORDER_NEEDED = "reorder_needed"


# Base Models
class CustomerBase(BaseModel):
    """Base customer model."""
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None


class Customer(CustomerBase):
    """Customer model with ID."""
    customer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product model."""
    name: str
    description: Optional[str] = None
    sku: str
    price: float
    unit: str = "unit"
    category: Optional[str] = None


class Product(ProductBase):
    """Product model with ID."""
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order model."""
    product_id: int
    customer_id: int
    store_id: str
    quantity: int
    requested_by: str
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None


class Order(OrderBase):
    """Order model with ID and timestamps."""
    order_id: int
    order_number: str
    order_date: datetime
    updated_at: datetime
    
    # Joined fields for display
    product_name: Optional[str] = None
    customer_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderCreate(OrderBase):
    """Model for creating a new order."""
    pass


class OrderUpdate(BaseModel):
    """Model for updating an order."""
    status: Optional[OrderStatus] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None


class InventoryHistoryBase(BaseModel):
    """Base inventory history model."""
    product_id: int
    store_id: str
    quantity_change: int
    transaction_type: str  # "IN", "OUT", "ADJUSTMENT"
    reference_id: Optional[str] = None
    notes: Optional[str] = None


class InventoryHistory(InventoryHistoryBase):
    """Inventory history model with ID."""
    history_id: int
    transaction_date: datetime
    balance_after: int
    created_by: str

    class Config:
        from_attributes = True


class InventoryForecastBase(BaseModel):
    """Base inventory forecast model."""
    product_id: int
    store_id: str
    current_stock: int
    forecast_30_days: int
    reorder_point: int
    reorder_quantity: int
    status: InventoryStatus


class InventoryForecast(InventoryForecastBase):
    """Inventory forecast model with metadata."""
    forecast_id: int
    last_updated: datetime
    
    # Joined fields for display
    product_name: Optional[str] = None
    product_sku: Optional[str] = None

    class Config:
        from_attributes = True


class InventoryForecastUpdate(BaseModel):
    """Model for updating inventory forecast."""
    current_stock: Optional[int] = None
    forecast_30_days: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    status: Optional[InventoryStatus] = None


# Response Models for API
class OrderResponse(BaseModel):
    """Response model for order with product details."""
    order_id: int
    order_number: str
    product: str
    quantity: int
    store: str
    requested_by: str
    order_date: datetime
    status: OrderStatus
    
    class Config:
        from_attributes = True


class InventoryForecastResponse(BaseModel):
    """Response model for inventory forecast display."""
    item_id: str
    item_name: str
    stock: int
    forecast_30_days: int
    status: InventoryStatus
    action: str
    
    class Config:
        from_attributes = True


# KPI Models
class OrderManagementKPI(BaseModel):
    """KPI data for order management."""
    total_orders: int
    pending_orders: int
    approved_orders: int
    shipped_orders: int
    average_order_value: float


class StockManagementAlertKPI(BaseModel):
    """KPI data for stock management alerts."""
    low_stock_items: int
    out_of_stock_items: int
    reorder_needed_items: int
    total_alerts: int