"""Inventory Turnover API endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..db_selector import db

router = APIRouter(prefix="/inventory-turnover", tags=["inventory"])


class InventoryTurnoverMetrics(BaseModel):
    """Inventory turnover metrics from the database view."""
    total_consumption_value: Optional[float] = None
    total_avg_inventory_value: Optional[float] = None
    overall_inventory_turnover: Optional[float] = None
    overall_days_on_hand: Optional[int] = None
    active_products: Optional[int] = None
    total_units_consumed: Optional[int] = None
    total_avg_units: Optional[int] = None


@router.get("/", response_model=InventoryTurnoverMetrics)
async def get_inventory_turnover_metrics():
    """
    Get Inventory Turnover metrics from the inventory_turnover view.

    Returns the overall inventory turnover rate and related metrics.
    This endpoint reads real-time metrics from the database view.
    """
    try:
        # Query the inventory_turnover view directly
        query = "SELECT * FROM public.inventory_turnover"
        result = db.execute_query(query)

        if result and len(result) > 0:
            row = result[0]
            return InventoryTurnoverMetrics(
                total_consumption_value=float(row.get('total_consumption_value')) if row.get('total_consumption_value') is not None else None,
                total_avg_inventory_value=float(row.get('total_avg_inventory_value')) if row.get('total_avg_inventory_value') is not None else None,
                overall_inventory_turnover=float(row.get('overall_inventory_turnover')) if row.get('overall_inventory_turnover') is not None else None,
                overall_days_on_hand=int(row.get('overall_days_on_hand')) if row.get('overall_days_on_hand') is not None else None,
                active_products=int(row.get('active_products')) if row.get('active_products') is not None else None,
                total_units_consumed=int(row.get('total_units_consumed')) if row.get('total_units_consumed') is not None else None,
                total_avg_units=int(row.get('total_avg_units')) if row.get('total_avg_units') is not None else None
            )
        else:
            # Return error if view is empty
            raise HTTPException(status_code=404, detail="No data available in inventory_turnover view")

    except Exception as e:
        # Return error for any database issues
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")