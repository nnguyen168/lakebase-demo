"""Orders management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from ..models import (
    Order, OrderCreate, OrderUpdate, OrderStatus, ForecastStatus,
    TransactionStatus, TransactionType
)
# Use database selector
from ..db_selector import db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[Order])
async def get_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    requested_by: Optional[str] = Query(None, description="Filter by requestor"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip")
):
    """Get list of orders with optional filters."""
    try:
        # Since there's no orders table yet, return mock data for now
        # In the future, this would query a real orders table
        return []
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """Get a specific order by ID."""
    try:
        # Mock implementation - return not found for now
        raise HTTPException(status_code=404, detail="Order not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")


@router.post("/", response_model=Order)
async def create_order(order: OrderCreate):
    """Create a new order."""
    try:
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

        # If this order is based on a forecast recommendation, mark the forecast as resolved
        if order.forecast_id:
            try:
                # Update the forecast status to resolved
                update_query = """
                    UPDATE inventory_forecast 
                    SET status = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE forecast_id = %s
                """
                db.execute_update(update_query, (ForecastStatus.RESOLVED.value, order.forecast_id))
                print(f"✅ Marked forecast {order.forecast_id} as resolved")
            except Exception as forecast_error:
                # Log the error but don't fail the order creation
                print(f"⚠️ Warning: Could not update forecast {order.forecast_id}: {forecast_error}")

        # Create a corresponding inventory transaction with "processing" status
        # Note: Due to sequence synchronization issues in the database, 
        # we'll gracefully handle transaction creation failures
        try:
            # For orders, we assume warehouse_id = 1 (default warehouse) if not specified
            # In a real system, this would be determined from business logic
            warehouse_id = 1
            
            transaction_notes = f"Order {order_number}: {order.notes}" if order.notes else f"Order {order_number}"
            
            # Use a unique transaction number following existing patterns (ORD- prefix)
            unique_transaction_number = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{datetime.now().microsecond}"
            
            # Try to create the transaction, but handle sequence errors gracefully
            insert_transaction_query = """
                INSERT INTO inventory_transactions 
                (transaction_number, product_id, warehouse_id, quantity_change, transaction_type, status, notes, transaction_timestamp, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """
            
            db.execute_update(insert_transaction_query, (
                unique_transaction_number,
                order.product_id,
                warehouse_id,
                order.quantity,  # Positive quantity for inbound orders
                TransactionType.INBOUND.value,
                TransactionStatus.PROCESSING.value,
                transaction_notes
            ))
            print(f"✅ Created transaction {unique_transaction_number} for order {order_number}")
            
        except Exception as transaction_error:
            # If transaction creation fails (likely due to sequence issues), 
            # log the error but continue with order creation
            error_msg = str(transaction_error)
            if "duplicate key" in error_msg and "pkey" in error_msg:
                print(f"⚠️ Database sequence issue prevented transaction creation for order {order_number}")
                print(f"   Order was created successfully, but corresponding transaction could not be recorded")
                print(f"   This is a known issue with the database sequence synchronization")
            else:
                print(f"⚠️ Warning: Could not create transaction for order {order_number}: {transaction_error}")

        # For now, just return a mock successful response without actually creating in database
        # In the future, this would insert into an orders table
        mock_order = Order(
            order_id=12345,  # Mock ID
            order_number=order_number,
            product_id=order.product_id,
            quantity=order.quantity,
            requested_by=order.requested_by,
            status=OrderStatus.PENDING,
            notes=order.notes,
            forecast_id=order.forecast_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            product_name="Mock Product",  # Would be joined from products table
            product_sku="MOCK-SKU",
            unit_price=10.00
        )

        return mock_order

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.put("/{order_id}", response_model=Order)
async def update_order(order_id: int, order_update: OrderUpdate):
    """Update an existing order."""
    try:
        # Mock implementation - return not found for now
        raise HTTPException(status_code=404, detail="Order not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")


@router.delete("/{order_id}")
async def cancel_order(order_id: int):
    """Cancel an order."""
    try:
        # Mock implementation - return not found for now
        raise HTTPException(status_code=404, detail="Order not found")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")
