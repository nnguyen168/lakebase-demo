"""Inventory management API endpoints."""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..models import (
    InventoryForecast, InventoryForecastUpdate, InventoryForecastResponse,
    StockManagementAlertKPI, InventoryStatus, ForecastStatus,
    PaginatedResponse, PaginationMeta
)
# Use database selector (automatically chooses mock or PostgreSQL)
from ..db_selector import db

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/forecast", response_model=PaginatedResponse[InventoryForecastResponse])
async def get_inventory_forecast(
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse ID"),
    status: Optional[ForecastStatus] = Query(None, description="Filter by forecast status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    sort_by: str = Query('severity', description="Sort key"),
    sort_order: str = Query('asc', description="Sort order: asc or desc")
):
    """Get inventory forecast with optional filters and pagination metadata."""
    try:
        # Validate sort key
        valid_sort_keys = {
            'severity': "severity",
            'stock': "stock",
            'forecast': "forecast_30_days",
            'product': "item_name",
            'last_updated': "f.last_updated"
        }
        if sort_by not in valid_sort_keys:
            sort_by = 'severity'
        sort_order = 'desc' if sort_order.lower() == 'desc' else 'asc'

        # Build base query for filtering
        schema = os.getenv("DB_SCHEMA", "public")
        base_query = f"""
            FROM {schema}.inventory_forecast f
            JOIN {schema}.products p ON f.product_id = p.product_id
            JOIN {schema}.warehouses w ON f.warehouse_id = w.warehouse_id
            WHERE 1=1
        """

        params = []

        if warehouse_id:
            base_query += " AND f.warehouse_id = %s"
            params.append(warehouse_id)

        if status:
            base_query += " AND f.status = %s"
            params.append(status.value)

        # Get total count
        count_query = "SELECT COUNT(*) as total " + base_query
        count_result = db.execute_query(count_query, params)
        total = count_result[0]['total'] if count_result else 0

        # Get paginated results
        data_query = """
            SELECT
                f.forecast_id,
                p.sku as item_id,
                p.name as item_name,
                f.current_stock as stock,
                CAST(f.forecast_30_days AS INTEGER) as forecast_30_days,
                f.warehouse_id,
                w.name as warehouse_name,
                w.location as warehouse_location,
                CASE
                    WHEN f.status = 'resolved' THEN 'resolved'
                    WHEN f.current_stock = 0 THEN 'out_of_stock'
                    WHEN f.current_stock < (f.forecast_30_days * 0.5) THEN 'reorder_needed'  -- Less than 15 days of stock
                    WHEN f.current_stock < f.forecast_30_days THEN 'low_stock'  -- Less than 30 days of stock
                    ELSE 'in_stock'
                END as status,
                CASE
                    WHEN f.status = 'resolved' THEN 'Resolved'
                    WHEN f.current_stock = 0 THEN 'Urgent Reorder'
                    WHEN f.current_stock < (f.forecast_30_days * 0.5) THEN 'Reorder Now'  -- Less than 15 days
                    WHEN f.current_stock < f.forecast_30_days THEN 'Monitor'  -- Less than 30 days
                    ELSE 'No Action'
                END as action,
                CASE
                    WHEN f.status = 'resolved' THEN 4
                    WHEN f.current_stock = 0 THEN 0
                    WHEN f.current_stock < (f.forecast_30_days * 0.5) THEN 1  -- Most urgent
                    WHEN f.current_stock < f.forecast_30_days THEN 2  -- Warning
                    ELSE 3
                END as severity_rank,
                f.last_updated
        """ + base_query

        # Determine order clauses with consistent secondary sorting
        if sort_by == 'severity':
            order_clause = f" ORDER BY severity_rank {sort_order.upper()}, item_name ASC"
        elif sort_by == 'product':
            order_clause = f" ORDER BY item_name {sort_order.upper()}"
        else:
            # Add secondary sort by product name for consistent ordering
            order_clause = f" ORDER BY {valid_sort_keys[sort_by]} {sort_order.upper()}, item_name ASC"
        data_query += order_clause + " LIMIT %s OFFSET %s"

        data_params = params + [limit, offset]
        results = db.execute_query(data_query, data_params)

        # Create pagination metadata
        pagination = PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )

        return PaginatedResponse(
            items=[{k: v for k, v in row.items() if k not in ('severity_rank', 'last_updated')} for row in results],
            pagination=pagination
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory forecast: {str(e)}")


@router.get("/history", response_model=List[dict])
async def get_inventory_history(
    item_id: str = Query(..., description="Product SKU to get history for"),
    warehouse_id: int = Query(..., description="Warehouse ID to get history for"),
    days: int = Query(30, ge=1, le=365, description="Number of days of history to return")
):
    """Get historical inventory levels for a specific product and warehouse."""
    try:
        # Query to get historical inventory levels from the inventory_historical table
        # If that doesn't have data, we can fall back to reconstructing from transactions
        schema = os.getenv('DB_SCHEMA', 'public')
        query = f"""
            SELECT
                ih.snapshot_date as history_date,
                ih.inventory_level as stock_level
            FROM {schema}.inventory_historical ih
            JOIN {schema}.products p ON ih.product_id = p.product_id
            WHERE p.sku = %s
            AND ih.warehouse_id = %s
            AND ih.snapshot_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY ih.snapshot_date ASC
        """
        
        results = db.execute_query(query, (item_id, warehouse_id, days))

        # If no historical data found, try to reconstruct from transactions
        if not results:
            # Fallback query using inventory_transactions to reconstruct daily levels
            fallback_query = f"""
                WITH daily_transactions AS (
                    SELECT
                        DATE(it.transaction_timestamp) as transaction_date,
                        SUM(it.quantity_change) as daily_change
                    FROM {schema}.inventory_transactions it
                    JOIN {schema}.products p ON it.product_id = p.product_id
                    WHERE p.sku = %s
                    AND it.warehouse_id = %s
                    AND it.transaction_timestamp >= CURRENT_DATE - INTERVAL '%s days'
                    AND it.status = 'confirmed'
                    GROUP BY DATE(it.transaction_timestamp)
                    ORDER BY transaction_date ASC
                ),
                running_totals AS (
                    SELECT 
                        transaction_date,
                        SUM(daily_change) OVER (ORDER BY transaction_date) as cumulative_change
                    FROM daily_transactions
                )
                SELECT 
                    transaction_date as history_date,
                    cumulative_change as stock_level
                FROM running_totals
                ORDER BY transaction_date ASC
            """
            
            results = db.execute_query(fallback_query, (item_id, warehouse_id, days))
        
        # Convert to list of dictionaries with date strings
        history_data = []
        for row in results:
            history_data.append({
                'date': row['history_date'].strftime('%Y-%m-%d'),
                'stock_level': row['stock_level']
            })

        return history_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory history: {str(e)}")


@router.get("/alerts/kpi", response_model=StockManagementAlertKPI)
async def get_stock_alerts_kpi():
    """Get KPI metrics for stock management alerts."""
    try:
        schema = os.getenv('DB_SCHEMA', 'public')
        query = f"""
            SELECT
                SUM(CASE WHEN current_stock < forecast_30_days AND current_stock >= (forecast_30_days * 0.5) THEN 1 ELSE 0 END) as low_stock_items,
                SUM(CASE WHEN current_stock = 0 THEN 1 ELSE 0 END) as out_of_stock_items,
                SUM(CASE WHEN current_stock < (forecast_30_days * 0.5) AND current_stock > 0 THEN 1 ELSE 0 END) as reorder_needed_items,
                SUM(CASE WHEN current_stock < forecast_30_days THEN 1 ELSE 0 END) as total_alerts
            FROM {schema}.inventory_forecast
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
        schema = os.getenv('DB_SCHEMA', 'public')
        result = db.execute_query(
            f"""
            SELECT f.*, p.name as product_name, p.sku as product_sku
            FROM {schema}.inventory_forecast f
            JOIN {schema}.products p ON f.product_id = p.product_id
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
