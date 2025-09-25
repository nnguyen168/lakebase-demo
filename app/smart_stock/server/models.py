"""Database models for inventory management system."""

from datetime import datetime
from typing import Optional, Generic, TypeVar, List
from decimal import Decimal
from pydantic import BaseModel
from enum import Enum

# Generic type for paginated responses
T = TypeVar('T')


class TransactionStatus(str, Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    INBOUND = "inbound"
    SALE = "sale"
    ADJUSTMENT = "adjustment"


class ForecastStatus(str, Enum):
    """Forecast status enumeration."""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    RESOLVED = "resolved"


class InventoryStatus(str, Enum):
    """Inventory status for UI display."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    REORDER_NEEDED = "reorder_needed"
    RESOLVED = "resolved"


# Product Models
class ProductBase(BaseModel):
    """Base product model."""
    name: str
    description: Optional[str] = None
    sku: str
    price: Decimal
    unit: str = "piece"
    category: Optional[str] = None
    reorder_level: int = 10


class Product(ProductBase):
    """Product model with ID."""
    product_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(ProductBase):
    """Model for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Model for updating a product."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    reorder_level: Optional[int] = None


# Warehouse Models
class WarehouseBase(BaseModel):
    """Base warehouse model."""
    name: str
    location: Optional[str] = None
    manager_id: Optional[int] = None
    timezone: str = "utc"


class Warehouse(WarehouseBase):
    """Warehouse model with ID."""
    warehouse_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WarehouseCreate(WarehouseBase):
    """Model for creating a new warehouse."""
    pass


# Inventory Transaction Models (replacing Order)
class InventoryTransactionBase(BaseModel):
    """Base inventory transaction model."""
    product_id: int
    warehouse_id: int
    quantity_change: int
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    notes: Optional[str] = None


class InventoryTransaction(InventoryTransactionBase):
    """Inventory transaction model with ID."""
    transaction_id: int
    transaction_number: str
    transaction_timestamp: datetime
    updated_at: datetime

    # Joined fields for display
    product_name: Optional[str] = None
    warehouse_name: Optional[str] = None

    class Config:
        from_attributes = True


class InventoryTransactionCreate(BaseModel):
    """Model for creating a new transaction."""
    product_id: int
    warehouse_id: int
    quantity_change: int
    transaction_type: TransactionType
    notes: Optional[str] = None


class InventoryTransactionUpdate(BaseModel):
    """Model for updating a transaction."""
    status: Optional[TransactionStatus] = None
    quantity_change: Optional[int] = None
    notes: Optional[str] = None




# Inventory Forecast Models
class InventoryForecastBase(BaseModel):
    """Base inventory forecast model."""
    product_id: int
    warehouse_id: int
    current_stock: Optional[int] = None
    forecast_30_days: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    confidence_score: Optional[Decimal] = None
    status: ForecastStatus = ForecastStatus.ACTIVE


class InventoryForecast(InventoryForecastBase):
    """Inventory forecast model with metadata."""
    forecast_id: int
    last_updated: datetime

    # Joined fields for display
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    warehouse_name: Optional[str] = None

    class Config:
        from_attributes = True


class InventoryForecastCreate(BaseModel):
    """Model for creating inventory forecast."""
    product_id: int
    warehouse_id: int
    current_stock: int
    forecast_30_days: int
    reorder_point: int
    reorder_quantity: int
    confidence_score: Optional[Decimal] = None


class InventoryForecastUpdate(BaseModel):
    """Model for updating inventory forecast."""
    current_stock: Optional[int] = None
    forecast_30_days: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    confidence_score: Optional[Decimal] = None
    status: Optional[ForecastStatus] = None




# Response Models for API
class TransactionResponse(BaseModel):
    """Response model for transaction with details."""
    transaction_id: int
    transaction_number: str
    product: str
    quantity_change: int
    warehouse: str
    transaction_type: str
    transaction_timestamp: datetime
    status: TransactionStatus

    class Config:
        from_attributes = True


class InventoryForecastResponse(BaseModel):
    """Response model for inventory forecast display."""
    forecast_id: int
    item_id: str
    item_name: str
    stock: int
    forecast_30_days: int
    warehouse_id: int
    warehouse_name: str
    warehouse_location: str
    status: InventoryStatus
    action: str

    class Config:
        from_attributes = True


# Order Models
class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    APPROVED = "approved" 
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class OrderBase(BaseModel):
    """Base order model."""
    product_id: int
    quantity: int
    warehouse_id: int
    requested_by: str
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None
    forecast_id: Optional[int] = None  # Link to forecast recommendation


class Order(OrderBase):
    """Order model with ID."""
    order_id: int
    order_number: str
    created_at: datetime
    updated_at: datetime

    # Joined fields for display
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    unit_price: Optional[Decimal] = None

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Model for creating a new order."""
    product_id: int
    quantity: int
    warehouse_id: int
    requested_by: str
    notes: Optional[str] = None
    forecast_id: Optional[int] = None  # Link to forecast recommendation


class OrderUpdate(BaseModel):
    """Model for updating an order."""
    status: Optional[OrderStatus] = None
    quantity: Optional[int] = None
    notes: Optional[str] = None


# KPI Models
class TransactionManagementKPI(BaseModel):
    """KPI data for transaction management."""
    total_transactions: int
    pending_transactions: int
    confirmed_transactions: int
    processing_transactions: int
    shipped_transactions: int
    delivered_transactions: int
    total_quantity_change: int


class StockManagementAlertKPI(BaseModel):
    """KPI data for stock management alerts."""
    low_stock_items: int
    out_of_stock_items: int
    reorder_needed_items: int
    total_alerts: int


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: List[T]
    pagination: PaginationMeta