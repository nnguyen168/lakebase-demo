# Generic router module for the Databricks app template
# Add your FastAPI routes here

from fastapi import APIRouter

from .user import router as user_router
from .transactions import router as transactions_router
from .inventory import router as inventory_router
from .products import router as products_router
from .orders import router as orders_router

router = APIRouter()
router.include_router(user_router, prefix='/user', tags=['user'])
router.include_router(transactions_router, tags=['transactions'])
router.include_router(inventory_router, tags=['inventory'])
router.include_router(products_router, tags=['products'])
router.include_router(orders_router, tags=['orders'])
