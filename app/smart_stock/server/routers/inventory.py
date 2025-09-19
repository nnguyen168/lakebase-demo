"""Inventory management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..models import (
    InventoryForecast, InventoryForecastUpdate, InventoryForecastResponse,
    StockManagementAlertKPI, InventoryStatus, ForecastStatus
)
# Use database selector (automatically chooses mock or PostgreSQL)
from ..db_selector import db

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/forecast", response_model=List[InventoryForecastResponse])
async def get_inventory_forecast(
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse ID"),
    status: Optional[ForecastStatus] = Query(None, description="Filter by forecast status"),
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
                CASE
                    WHEN f.current_stock = 0 THEN 'out_of_stock'
                    WHEN f.current_stock < f.reorder_point THEN 'reorder_needed'
                    WHEN f.current_stock < f.reorder_point * 1.5 THEN 'low_stock'
                    ELSE 'in_stock'
                END as status,
                CASE
                    WHEN f.current_stock = 0 THEN 'Urgent Reorder'
                    WHEN f.current_stock < f.reorder_point THEN 'Reorder Now'
                    WHEN f.current_stock < f.reorder_point * 1.5 THEN 'Monitor'
                    ELSE 'No Action'
                END as action
            FROM inventory_forecast f
            JOIN products p ON f.product_id = p.product_id
            WHERE 1=1
        """
        
        params = []
        
        if warehouse_id:
            query += " AND f.warehouse_id = %s"
            params.append(warehouse_id)
        
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
                SUM(CASE WHEN current_stock < reorder_point * 1.5 AND current_stock > reorder_point THEN 1 ELSE 0 END) as low_stock_items,
                SUM(CASE WHEN current_stock = 0 THEN 1 ELSE 0 END) as out_of_stock_items,
                SUM(CASE WHEN current_stock < reorder_point AND current_stock > 0 THEN 1 ELSE 0 END) as reorder_needed_items,
                SUM(CASE WHEN current_stock < reorder_point * 1.5 THEN 1 ELSE 0 END) as total_alerts
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
        
        update_fields.append("last_updated = CURRENT_TIMESTAMP")
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


