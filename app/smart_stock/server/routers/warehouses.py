"""Warehouses management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from ..models import Warehouse, PaginatedResponse, PaginationMeta
from ..db_selector import db

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("/", response_model=PaginatedResponse[Warehouse])
async def get_warehouses(
    limit: int = Query(100, ge=1, le=500, description="Maximum number of warehouses to return"),
    offset: int = Query(0, ge=0, description="Number of warehouses to skip")
):
    """Get all warehouses with pagination metadata."""
    try:
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM warehouses"
        count_result = db.execute_query(count_query)
        total = count_result[0]['total'] if count_result else 0

        # Get paginated results
        query = """
            SELECT
                warehouse_id,
                name,
                location,
                created_at,
                updated_at
            FROM warehouses
            ORDER BY name
            LIMIT %s OFFSET %s
        """

        warehouses = db.execute_query(query, (limit, offset))

        # Create pagination metadata
        pagination = PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )

        return PaginatedResponse(
            items=warehouses,
            pagination=pagination
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch warehouses: {str(e)}")


@router.get("/{warehouse_id}", response_model=Warehouse)
async def get_warehouse(warehouse_id: int):
    """Get a specific warehouse by ID."""
    try:
        query = """
            SELECT
                warehouse_id,
                name,
                location,
                created_at,
                updated_at
            FROM warehouses
            WHERE warehouse_id = %s
        """

        warehouses = db.execute_query(query, (warehouse_id,))

        if not warehouses:
            raise HTTPException(status_code=404, detail=f"Warehouse with ID {warehouse_id} not found")

        return warehouses[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch warehouse: {str(e)}")