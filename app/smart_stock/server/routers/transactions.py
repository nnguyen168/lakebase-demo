"""Inventory transactions API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from ..models import (
    InventoryTransaction, InventoryTransactionCreate, InventoryTransactionUpdate,
    TransactionResponse, TransactionManagementKPI, TransactionStatus, TransactionType
)
# Use database selector
from ..db_selector import db

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    status: Optional[TransactionStatus] = Query(None, description="Filter by transaction status"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip")
):
    """Get list of inventory transactions with optional filters."""
    try:
        query = """
            SELECT
                t.transaction_id,
                t.transaction_number,
                p.name as product,
                t.quantity_change,
                w.name as warehouse,
                t.transaction_type,
                t.transaction_timestamp,
                t.status
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.product_id
            JOIN warehouses w ON t.warehouse_id = w.warehouse_id
            WHERE 1=1
        """

        params = []

        if status:
            query += " AND t.status = %s"
            params.append(status.value)

        if warehouse_id:
            query += " AND t.warehouse_id = %s"
            params.append(warehouse_id)

        if transaction_type:
            query += " AND t.transaction_type = %s"
            params.append(transaction_type.value)

        query += " ORDER BY t.transaction_timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        results = db.execute_query(query, tuple(params) if params else None)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transactions: {str(e)}")


@router.get("/kpi", response_model=TransactionManagementKPI)
async def get_transaction_kpi():
    """Get KPI metrics for transaction management."""
    try:
        # Get transaction counts by status
        status_query = """
            SELECT
                COUNT(*) as total_transactions,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_transactions,
                SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_transactions,
                SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing_transactions,
                SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) as shipped_transactions,
                SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered_transactions,
                SUM(ABS(quantity_change)) as total_quantity_change
            FROM inventory_transactions
        """

        result = db.execute_query(status_query)

        if result:
            return TransactionManagementKPI(
                total_transactions=result[0].get("total_transactions", 0) or 0,
                pending_transactions=result[0].get("pending_transactions", 0) or 0,
                confirmed_transactions=result[0].get("confirmed_transactions", 0) or 0,
                processing_transactions=result[0].get("processing_transactions", 0) or 0,
                shipped_transactions=result[0].get("shipped_transactions", 0) or 0,
                delivered_transactions=result[0].get("delivered_transactions", 0) or 0,
                total_quantity_change=result[0].get("total_quantity_change", 0) or 0
            )

        return TransactionManagementKPI(
            total_transactions=0,
            pending_transactions=0,
            confirmed_transactions=0,
            processing_transactions=0,
            shipped_transactions=0,
            delivered_transactions=0,
            total_quantity_change=0
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch KPI metrics: {str(e)}")


@router.get("/{transaction_id}", response_model=InventoryTransaction)
async def get_transaction(transaction_id: int):
    """Get a specific transaction by ID."""
    try:
        query = """
            SELECT
                t.*,
                p.name as product_name,
                w.name as warehouse_name
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.product_id
            JOIN warehouses w ON t.warehouse_id = w.warehouse_id
            WHERE t.transaction_id = %s
        """

        results = db.execute_query(query, (transaction_id,))

        if not results:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return results[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transaction: {str(e)}")


@router.post("/", response_model=InventoryTransaction)
async def create_transaction(transaction: InventoryTransactionCreate):
    """Create a new inventory transaction."""
    try:
        # Generate transaction number
        transaction_number = f"TXN-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"

        # Insert the transaction
        query = """
            INSERT INTO inventory_transactions (
                transaction_number,
                product_id,
                warehouse_id,
                quantity_change,
                transaction_type,
                status,
                notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """

        params = (
            transaction_number,
            transaction.product_id,
            transaction.warehouse_id,
            transaction.quantity_change,
            transaction.transaction_type.value,
            'pending',
            transaction.notes
        )

        result = db.execute_query(query, params)

        if result:
            return result[0]

        raise HTTPException(status_code=500, detail="Failed to create transaction")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")


@router.put("/{transaction_id}", response_model=InventoryTransaction)
async def update_transaction(transaction_id: int, transaction_update: InventoryTransactionUpdate):
    """Update an existing transaction."""
    try:
        # Build update query dynamically
        update_fields = []
        params = []

        if transaction_update.status is not None:
            update_fields.append("status = %s")
            params.append(transaction_update.status.value)

        if transaction_update.quantity_change is not None:
            update_fields.append("quantity_change = %s")
            params.append(transaction_update.quantity_change)

        if transaction_update.notes is not None:
            update_fields.append("notes = %s")
            params.append(transaction_update.notes)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(transaction_id)

        query = f"""
            UPDATE inventory_transactions
            SET {', '.join(update_fields)}
            WHERE transaction_id = %s
            RETURNING *
        """

        result = db.execute_query(query, params)

        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return result[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update transaction: {str(e)}")


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """Cancel a transaction."""
    try:
        # Check if transaction exists and can be cancelled
        check_query = """
            SELECT status
            FROM inventory_transactions
            WHERE transaction_id = %s
        """

        result = db.execute_query(check_query, (transaction_id,))

        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if result[0]['status'] in ['delivered', 'cancelled']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel {result[0]['status']} transaction"
            )

        # Update status to cancelled
        update_query = """
            UPDATE inventory_transactions
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE transaction_id = %s
        """

        db.execute_update(update_query, (transaction_id,))

        return {"message": "Transaction cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel transaction: {str(e)}")