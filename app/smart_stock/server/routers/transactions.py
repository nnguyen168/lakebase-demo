"""Inventory transactions API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta

from ..models import (
    InventoryTransaction, InventoryTransactionCreate, InventoryTransactionUpdate,
    TransactionResponse, TransactionManagementKPI, TransactionStatus, TransactionType,
    PaginatedResponse, PaginationMeta, BulkStatusUpdateRequest, BulkStatusUpdateResponse,
    BulkDeleteRequest, BulkDeleteResponse
)
# Use database selector
from ..db_selector import db

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=PaginatedResponse[TransactionResponse])
async def get_transactions(
    status: Optional[List[TransactionStatus]] = Query(None, description="Filter by transaction status (multiple values allowed)"),
    warehouse_id: Optional[List[int]] = Query(None, description="Filter by warehouse ID (multiple values allowed)"),
    product_id: Optional[List[int]] = Query(None, description="Filter by product ID (multiple values allowed)"),
    transaction_type: Optional[List[TransactionType]] = Query(None, description="Filter by transaction type (multiple values allowed)"),
    date_from: Optional[datetime] = Query(None, description="Filter transactions from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter transactions until this date"),
    sort_by: Optional[str] = Query("transaction_timestamp", description="Field to sort by (product, warehouse, transaction_timestamp)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip")
):
    """Get list of inventory transactions with optional filters and pagination metadata."""
    try:
        # Debug: Log the incoming filter parameters
        print(f"Filter params - status: {status}, warehouse_id: {warehouse_id}, product_id: {product_id}, "
              f"transaction_type: {transaction_type}, date_from: {date_from}, date_to: {date_to}")

        # Build base query for filtering
        base_query = """
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.product_id
            JOIN warehouses w ON t.warehouse_id = w.warehouse_id
            WHERE 1=1
        """

        params = []

        if status and len(status) > 0:
            placeholders = ', '.join(['%s'] * len(status))
            base_query += f" AND t.status IN ({placeholders})"
            params.extend([s.value for s in status])

        if warehouse_id and len(warehouse_id) > 0:
            placeholders = ', '.join(['%s'] * len(warehouse_id))
            base_query += f" AND t.warehouse_id IN ({placeholders})"
            params.extend(warehouse_id)

        if product_id and len(product_id) > 0:
            placeholders = ', '.join(['%s'] * len(product_id))
            base_query += f" AND t.product_id IN ({placeholders})"
            params.extend(product_id)

        if transaction_type and len(transaction_type) > 0:
            placeholders = ', '.join(['%s'] * len(transaction_type))
            base_query += f" AND t.transaction_type IN ({placeholders})"
            params.extend([t.value for t in transaction_type])

        if date_from:
            base_query += " AND t.transaction_timestamp >= %s"
            params.append(date_from)

        if date_to:
            # Add 23:59:59 to date_to to include the entire day
            base_query += " AND t.transaction_timestamp < %s"
            # Add one day to date_to to include all transactions on that day
            date_to_inclusive = date_to + timedelta(days=1)
            params.append(date_to_inclusive)

        # Get total count
        count_query = "SELECT COUNT(*) as total " + base_query
        print(f"Count query: {count_query}")
        print(f"Query params: {params}")
        count_result = db.execute_query(count_query, tuple(params) if params else None)
        total = count_result[0]['total'] if count_result else 0

        # Map sort fields to actual database columns
        sort_mapping = {
            "product": "p.name",
            "warehouse": "w.name",
            "transaction_timestamp": "t.transaction_timestamp"
        }

        # Validate and apply sorting
        sort_column = sort_mapping.get(sort_by, "t.transaction_timestamp")
        order_direction = "ASC" if sort_order and sort_order.lower() == "asc" else "DESC"

        # Get paginated results
        data_query = """
            SELECT
                t.transaction_id,
                t.transaction_number,
                p.name as product,
                t.quantity_change,
                w.name as warehouse,
                t.transaction_type,
                t.transaction_timestamp,
                t.status,
                t.notes
        """ + base_query + f" ORDER BY {sort_column} {order_direction} LIMIT %s OFFSET %s"

        data_params = params + [limit, offset]
        results = db.execute_query(data_query, tuple(data_params))

        # Create pagination metadata
        pagination = PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )

        return PaginatedResponse(
            items=results,
            pagination=pagination
        )

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
        # Generate transaction number with microseconds for uniqueness
        import time
        timestamp = datetime.now()
        transaction_number = f"TXN-{timestamp.strftime('%Y%m%d')}-{timestamp.strftime('%H%M%S')}-{int(time.time() * 1000) % 1000000}"

        # Get the current max transaction_id and add 1 for a safe new ID
        # This is a workaround for the corrupted sequence
        max_id_query = "SELECT COALESCE(MAX(transaction_id), 0) + 1 FROM inventory_transactions"
        result = db.execute_query(max_id_query)
        new_transaction_id = result[0]['coalesce'] if result else 1

        # Insert with explicit transaction_id to avoid sequence issues
        insert_query = """
            INSERT INTO inventory_transactions (
                transaction_id,
                transaction_number,
                product_id,
                warehouse_id,
                quantity_change,
                transaction_type,
                status,
                notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            new_transaction_id,
            transaction_number,
            transaction.product_id,
            transaction.warehouse_id,
            transaction.quantity_change,
            transaction.transaction_type.value,
            transaction.status.value if transaction.status else 'pending',
            transaction.notes
        )

        # Use execute_update to perform the insert
        rows_affected = db.execute_update(insert_query, params)

        if rows_affected > 0:
            # Now fetch the created record using the unique transaction_number
            select_query = """
                SELECT
                    t.*,
                    p.name as product_name,
                    w.name as warehouse_name
                FROM inventory_transactions t
                JOIN products p ON t.product_id = p.product_id
                JOIN warehouses w ON t.warehouse_id = w.warehouse_id
                WHERE t.transaction_number = %s
            """

            result = db.execute_query(select_query, (transaction_number,))

            if result:
                return result[0]

        raise HTTPException(status_code=500, detail="Failed to create transaction")

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error creating transaction: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create transaction: {str(e)}")


@router.put("/bulk-status", response_model=BulkStatusUpdateResponse)
async def bulk_update_status(request: BulkStatusUpdateRequest):
    """Update status for multiple transactions at once."""
    try:
        if not request.transaction_ids:
            raise HTTPException(status_code=400, detail="No transaction IDs provided")

        # Validate transactions exist and can be updated
        placeholders = ', '.join(['%s'] * len(request.transaction_ids))
        check_query = f"""
            SELECT transaction_id, status
            FROM inventory_transactions
            WHERE transaction_id IN ({placeholders})
        """

        existing_transactions = db.execute_query(check_query, tuple(request.transaction_ids))

        if not existing_transactions:
            raise HTTPException(status_code=404, detail="No valid transactions found")

        found_ids = {t['transaction_id'] for t in existing_transactions}
        missing_ids = set(request.transaction_ids) - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Transactions not found: {list(missing_ids)}"
            )

        # Check if any transactions are in a final state that can't be changed
        final_states = ['delivered', 'cancelled']
        locked_transactions = [
            t['transaction_id'] for t in existing_transactions
            if t['status'] in final_states and request.status.value not in final_states
        ]

        if locked_transactions:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot update transactions in final state: {locked_transactions}"
            )

        # Perform bulk update
        update_query = f"""
            UPDATE inventory_transactions
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE transaction_id IN ({placeholders})
        """

        params = [request.status.value] + request.transaction_ids
        affected_rows = db.execute_update(update_query, tuple(params))

        return BulkStatusUpdateResponse(
            updated_count=affected_rows,
            message=f"Successfully updated {affected_rows} transaction(s) to status '{request.status.value}'"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update transaction status: {str(e)}")


@router.delete("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_transactions(request: BulkDeleteRequest):
    """Delete multiple transactions at once."""
    try:
        if not request.transaction_ids:
            raise HTTPException(status_code=400, detail="No transaction IDs provided")

        # Check which transactions exist
        placeholders = ', '.join(['%s'] * len(request.transaction_ids))
        check_query = f"""
            SELECT transaction_id
            FROM inventory_transactions
            WHERE transaction_id IN ({placeholders})
        """

        existing_transactions = db.execute_query(check_query, tuple(request.transaction_ids))

        if not existing_transactions:
            raise HTTPException(status_code=404, detail="No valid transactions found to delete")

        found_ids = [t['transaction_id'] for t in existing_transactions]
        missing_ids = set(request.transaction_ids) - set(found_ids)

        # Delete the transactions
        delete_query = f"""
            DELETE FROM inventory_transactions
            WHERE transaction_id IN ({placeholders})
        """

        deleted_count = db.execute_update(delete_query, tuple(request.transaction_ids))

        # Prepare response message
        message = f"Successfully deleted {deleted_count} transaction(s)"
        if missing_ids:
            message += f" (IDs not found: {list(missing_ids)})"

        return BulkDeleteResponse(
            deleted_count=deleted_count,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete transactions: {str(e)}")


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


