"""Orders API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta

from ..models import (
    Order, OrderCreate, OrderUpdate, OrderResponse,
    OrderManagementKPI, OrderStatus
)
# Use database selector (automatically chooses mock or PostgreSQL)
from ..db_selector import db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip")
):
    """Get list of orders with optional filters."""
    try:
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Getting orders with status={status}, store_id={store_id}, limit={limit}, offset={offset}")
        query = """
            SELECT 
                o.order_id,
                o.order_number,
                p.name as product,
                o.quantity,
                o.store_id as store,
                o.requested_by,
                o.order_date,
                o.status
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE 1=1
        """
        
        params = []
        
        if status:
            query += " AND o.status = %s"
            params.append(status.value)
        
        if store_id:
            query += " AND o.store_id = %s"
            params.append(store_id)
        
        query += " ORDER BY o.order_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = db.execute_query(query, tuple(params) if params else None)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.get("/kpi", response_model=OrderManagementKPI)
async def get_order_kpi():
    """Get KPI metrics for order management."""
    try:
        # Get order counts by status
        status_query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_orders,
                SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) as shipped_orders
            FROM orders
            WHERE order_date >= CURRENT_DATE - INTERVAL '30' DAY
        """
        
        status_result = db.execute_query(status_query)
        
        # Get average order value
        value_query = """
            SELECT AVG(o.quantity * p.price) as avg_order_value
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.order_date >= CURRENT_DATE - INTERVAL '30' DAY
        """
        
        value_result = db.execute_query(value_query)
        
        if status_result and value_result:
            return OrderManagementKPI(
                total_orders=status_result[0].get("total_orders", 0) or 0,
                pending_orders=status_result[0].get("pending_orders", 0) or 0,
                approved_orders=status_result[0].get("approved_orders", 0) or 0,
                shipped_orders=status_result[0].get("shipped_orders", 0) or 0,
                average_order_value=value_result[0].get("avg_order_value", 0) or 0
            )
        
        return OrderManagementKPI(
            total_orders=0,
            pending_orders=0,
            approved_orders=0,
            shipped_orders=0,
            average_order_value=0
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch KPI metrics: {str(e)}")


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """Get a specific order by ID."""
    try:
        query = """
            SELECT 
                o.*,
                p.name as product_name,
                c.name as customer_name
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s
        """
        
        results = db.execute_query(query, [order_id])
        
        if not results:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return results[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")


@router.post("/", response_model=Order)
async def create_order(order: OrderCreate):
    """Create a new order with inventory transaction."""
    try:
        # Generate order number
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        
        # Execute transaction with inventory update
        result = db.execute_order_transaction(
            "create", 
            order_data={
                "order_number": order_number,
                "product_id": order.product_id,
                "customer_id": order.customer_id,
                "store_id": order.store_id,
                "quantity": order.quantity,
                "requested_by": order.requested_by,
                "status": order.status.value,
                "notes": order.notes
            }
        )
        
        if result:
            return result[0]
        
        raise HTTPException(status_code=500, detail="Failed to retrieve created order")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.put("/{order_id}", response_model=Order)
async def update_order(order_id: int, order_update: OrderUpdate):
    """Update an existing order."""
    try:
        # Build update query dynamically
        update_fields = []
        params = []
        
        if order_update.status is not None:
            update_fields.append("status = %s")
            params.append(order_update.status.value)
        
        if order_update.quantity is not None:
            update_fields.append("quantity = %s")
            params.append(order_update.quantity)
        
        if order_update.notes is not None:
            update_fields.append("notes = %s")
            params.append(order_update.notes)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP()")
        params.append(order_id)
        
        query = f"""
            UPDATE orders 
            SET {', '.join(update_fields)}
            WHERE order_id = %s
        """
        
        rows_affected = db.execute_update(query, params)
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Return updated order
        result = db.execute_query("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        
        if result:
            return result[0]
        
        raise HTTPException(status_code=500, detail="Failed to retrieve updated order")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")


@router.delete("/{order_id}")
async def delete_order(order_id: int):
    """Cancel an order with inventory rollback."""
    try:
        # Get order details first for inventory rollback
        order_query = """
            SELECT o.*, p.name as product_name
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            WHERE o.order_id = %s
        """
        
        order_result = db.execute_query(order_query, [order_id])
        
        if not order_result:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_data = order_result[0]
        
        # Don't allow canceling already cancelled or delivered orders
        if order_data['status'] in ['cancelled', 'delivered']:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel {order_data['status']} order"
            )
        
        # Execute transaction with inventory rollback
        db.execute_order_transaction(
            "cancel", 
            order_data=order_data
        )
        
        return {"message": "Order cancelled successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")