"""Inventory management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..models import (
    InventoryForecast, InventoryForecastUpdate, InventoryForecastResponse,
    StockManagementAlertKPI, InventoryStatus, InventoryHistory
)
# Use database selector (automatically chooses mock or PostgreSQL)
from ..db_selector import db

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/forecast", response_model=List[InventoryForecastResponse])
async def get_inventory_forecast(
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    status: Optional[InventoryStatus] = Query(None, description="Filter by inventory status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    """Get inventory forecast with optional filters."""
    try:
        query = """
            SELECT 
                p.sku as item_id,
                p.name as item_name,
                f.current_stock as stock,
                f.forecast_30_days,
                f.status,
                CASE 
                    WHEN f.status = 'out_of_stock' THEN 'Urgent Reorder'
                    WHEN f.status = 'reorder_needed' THEN 'Reorder Now'
                    WHEN f.status = 'low_stock' THEN 'Monitor'
                    ELSE 'No Action'
                END as action
            FROM inventory_forecast f
            JOIN products p ON f.product_id = p.product_id
            WHERE 1=1
        """
        
        params = []
        
        if store_id:
            query += " AND f.store_id = %s"
            params.append(store_id)
        
        if status:
            query += " AND f.status = %s"
            params.append(status.value)
        
        query += " ORDER BY f.last_updated DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = db.execute_query(query, params)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory forecast: {str(e)}")


@router.get("/alerts/kpi", response_model=StockManagementAlertKPI)
async def get_stock_alerts_kpi():
    """Get KPI metrics for stock management alerts."""
    try:
        query = """
            SELECT 
                SUM(CASE WHEN status = 'low_stock' THEN 1 ELSE 0 END) as low_stock_items,
                SUM(CASE WHEN status = 'out_of_stock' THEN 1 ELSE 0 END) as out_of_stock_items,
                SUM(CASE WHEN status = 'reorder_needed' THEN 1 ELSE 0 END) as reorder_needed_items,
                SUM(CASE WHEN status IN ('low_stock', 'out_of_stock', 'reorder_needed') THEN 1 ELSE 0 END) as total_alerts
            FROM inventory_forecast
        """
        
        result = db.execute_query(query)
        
        if result:
            return StockManagementAlertKPI(
                low_stock_items=result[0].get("low_stock_items", 0) or 0,
                out_of_stock_items=result[0].get("out_of_stock_items", 0) or 0,
                reorder_needed_items=result[0].get("reorder_needed_items", 0) or 0,
                total_alerts=result[0].get("total_alerts", 0) or 0
            )
        
        return StockManagementAlertKPI(
            low_stock_items=0,
            out_of_stock_items=0,
            reorder_needed_items=0,
            total_alerts=0
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock alerts KPI: {str(e)}")


@router.get("/history", response_model=List[InventoryHistory])
async def get_inventory_history(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip")
):
    """Get inventory transaction history."""
    try:
        query = """
            SELECT * FROM inventory_history
            WHERE 1=1
        """
        
        params = []
        
        if product_id:
            query += " AND product_id = %s"
            params.append(product_id)
        
        if store_id:
            query += " AND store_id = %s"
            params.append(store_id)
        
        if transaction_type:
            query += " AND transaction_type = %s"
            params.append(transaction_type)
        
        query += " ORDER BY transaction_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = db.execute_query(query, params)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory history: {str(e)}")


@router.put("/forecast/{forecast_id}", response_model=InventoryForecast)
async def update_inventory_forecast(forecast_id: int, forecast_update: InventoryForecastUpdate):
    """Update inventory forecast for a specific item."""
    try:
        # Build update query dynamically
        update_fields = []
        params = []
        
        if forecast_update.current_stock is not None:
            update_fields.append("current_stock = %s")
            params.append(forecast_update.current_stock)
        
        if forecast_update.forecast_30_days is not None:
            update_fields.append("forecast_30_days = %s")
            params.append(forecast_update.forecast_30_days)
        
        if forecast_update.reorder_point is not None:
            update_fields.append("reorder_point = %s")
            params.append(forecast_update.reorder_point)
        
        if forecast_update.reorder_quantity is not None:
            update_fields.append("reorder_quantity = %s")
            params.append(forecast_update.reorder_quantity)
        
        if forecast_update.status is not None:
            update_fields.append("status = %s")
            params.append(forecast_update.status.value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("last_updated = CURRENT_TIMESTAMP()")
        params.append(forecast_id)
        
        query = f"""
            UPDATE inventory_forecast 
            SET {', '.join(update_fields)}
            WHERE forecast_id = %s
        """
        
        rows_affected = db.execute_update(query, params)
        
        if rows_affected == 0:
            raise HTTPException(status_code=404, detail="Forecast record not found")
        
        # Return updated forecast
        result = db.execute_query(
            """
            SELECT f.*, p.name as product_name, p.sku as product_sku
            FROM inventory_forecast f
            JOIN products p ON f.product_id = p.product_id
            WHERE f.forecast_id = %s
            """, 
            [forecast_id]
        )
        
        if result:
            return result[0]
        
        raise HTTPException(status_code=500, detail="Failed to retrieve updated forecast")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update forecast: {str(e)}")


@router.post("/history", response_model=InventoryHistory)
async def create_inventory_transaction(transaction: InventoryHistory):
    """Record a new inventory transaction."""
    try:
        # Calculate new balance
        current_balance_query = """
            SELECT current_stock 
            FROM inventory_forecast 
            WHERE product_id = %s AND store_id = %s
        """
        
        current_result = db.execute_query(
            current_balance_query, 
            [transaction.product_id, transaction.store_id]
        )
        
        current_stock = current_result[0]["current_stock"] if current_result else 0
        
        if transaction.transaction_type == "IN":
            new_balance = current_stock + transaction.quantity_change
        elif transaction.transaction_type == "OUT":
            new_balance = current_stock - transaction.quantity_change
        else:  # ADJUSTMENT
            new_balance = transaction.quantity_change
        
        # Insert transaction record
        insert_query = """
            INSERT INTO inventory_history (
                product_id, store_id, quantity_change, transaction_type,
                reference_id, notes, balance_after, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = [
            transaction.product_id,
            transaction.store_id,
            transaction.quantity_change,
            transaction.transaction_type,
            transaction.reference_id,
            transaction.notes,
            new_balance,
            transaction.created_by
        ]
        
        db.execute_update(insert_query, params)
        
        # Update current stock in forecast
        update_forecast_query = """
            UPDATE inventory_forecast 
            SET current_stock = %s, last_updated = CURRENT_TIMESTAMP()
            WHERE product_id = %s AND store_id = %s
        """
        
        db.execute_update(
            update_forecast_query,
            [new_balance, transaction.product_id, transaction.store_id]
        )
        
        # Determine new status based on stock level
        update_status_query = """
            UPDATE inventory_forecast 
            SET status = CASE 
                WHEN current_stock = 0 THEN 'out_of_stock'
                WHEN current_stock < reorder_point THEN 'reorder_needed'
                WHEN current_stock < reorder_point * 1.5 THEN 'low_stock'
                ELSE 'in_stock'
            END
            WHERE product_id = %s AND store_id = %s
        """
        
        db.execute_update(
            update_status_query,
            [transaction.product_id, transaction.store_id]
        )
        
        # Return the created transaction
        result = db.execute_query(
            "SELECT * FROM inventory_history WHERE history_id = LAST_INSERT_ID()",
            []
        )
        
        if result:
            return result[0]
        
        # Fallback: get the most recent transaction
        result = db.execute_query(
            """
            SELECT * FROM inventory_history 
            WHERE product_id = %s AND store_id = %s
            ORDER BY transaction_date DESC
            LIMIT 1
            """,
            [transaction.product_id, transaction.store_id]
        )
        
        if result:
            return result[0]
        
        raise HTTPException(status_code=500, detail="Failed to retrieve created transaction")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create inventory transaction: {str(e)}")