"""Products management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from decimal import Decimal

from ..models import (
    Product, ProductCreate, ProductUpdate,
    PaginatedResponse, PaginationMeta
)
# Use database selector (automatically chooses mock or PostgreSQL)
from ..db_selector import db

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=PaginatedResponse[Product])
async def get_products(
    category: Optional[str] = Query(None, description="Filter by product category"),
    search: Optional[str] = Query(None, description="Search in product name or SKU"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip")
):
    """Get all products with optional filters and pagination metadata."""
    try:
        # Build base query for filtering
        base_query = "FROM products WHERE 1=1"
        params = []
        
        if category:
            base_query += " AND category = %s"
            params.append(category)
            
        if search:
            base_query += " AND (name ILIKE %s OR sku ILIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        # Get total count
        count_query = "SELECT COUNT(*) as total " + base_query
        count_result = db.execute_query(count_query, tuple(params) if params else None)
        total = count_result[0]['total'] if count_result else 0
        
        # Get paginated results
        data_query = """
            SELECT 
                product_id,
                name,
                description,
                sku,
                price,
                unit,
                category,
                reorder_level,
                created_at,
                updated_at
        """ + base_query + " ORDER BY name LIMIT %s OFFSET %s"
        
        data_params = params + [limit, offset]
        products = db.execute_query(data_query, tuple(data_params))
        
        # Convert price to Decimal for proper handling
        for product in products:
            if product.get('price'):
                product['price'] = Decimal(str(product['price']))
        
        # Create pagination metadata
        pagination = PaginationMeta(
            total=total,
            limit=limit,
            offset=offset,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )

        return PaginatedResponse(
            items=products,
            pagination=pagination
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product by ID."""
    try:
        query = """
            SELECT 
                product_id,
                name,
                description,
                sku,
                price,
                unit,
                category,
                reorder_level,
                created_at,
                updated_at
            FROM products
            WHERE product_id = %s
        """
        
        products = db.execute_query(query, (product_id,))
        
        if not products:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        product = products[0]
        if product.get('price'):
            product['price'] = Decimal(str(product['price']))
            
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")


@router.post("/", response_model=Product)
async def create_product(product: ProductCreate):
    """Create a new product."""
    try:
        query = """
            INSERT INTO products (name, description, sku, price, unit, category, reorder_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING product_id, name, description, sku, price, unit, category, reorder_level, created_at, updated_at
        """
        
        params = (
            product.name,
            product.description,
            product.sku,
            float(product.price),
            product.unit,
            product.category,
            product.reorder_level
        )
        
        result = db.execute_query(query, params)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create product")
        
        created_product = result[0]
        if created_product.get('price'):
            created_product['price'] = Decimal(str(created_product['price']))
            
        return created_product
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductUpdate):
    """Update a product."""
    try:
        # First check if product exists
        existing = db.execute_query("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not existing:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        if product.name is not None:
            update_fields.append("name = %s")
            params.append(product.name)
        if product.description is not None:
            update_fields.append("description = %s")
            params.append(product.description)
        if product.price is not None:
            update_fields.append("price = %s")
            params.append(float(product.price))
        if product.unit is not None:
            update_fields.append("unit = %s")
            params.append(product.unit)
        if product.category is not None:
            update_fields.append("category = %s")
            params.append(product.category)
        
        if not update_fields:
            # No fields to update, return current product
            return await get_product(product_id)
        
        query = f"""
            UPDATE products 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE product_id = %s
            RETURNING product_id, name, description, sku, price, unit, category, reorder_level, created_at, updated_at
        """
        params.append(product_id)
        
        result = db.execute_query(query, tuple(params))
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update product")
        
        updated_product = result[0]
        if updated_product.get('price'):
            updated_product['price'] = Decimal(str(updated_product['price']))
            
        return updated_product
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")


@router.delete("/{product_id}")
async def delete_product(product_id: int):
    """Delete a product."""
    try:
        # Check if product exists
        existing = db.execute_query("SELECT product_id FROM products WHERE product_id = %s", (product_id,))
        if not existing:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
        
        # Delete the product
        affected_rows = db.execute_update("DELETE FROM products WHERE product_id = %s", (product_id,))
        
        if affected_rows == 0:
            raise HTTPException(status_code=500, detail="Failed to delete product")
        
        return {"message": f"Product {product_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")
