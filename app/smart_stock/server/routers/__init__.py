# Generic router module for the Databricks app template
# Add your FastAPI routes here

from fastapi import APIRouter

from .user import router as user_router
from .transactions import router as transactions_router
from .inventory import router as inventory_router
from .products import router as products_router
from .orders import router as orders_router
from .otpr import router as otpr_router
from .inventory_turnover import router as inventory_turnover_router
from .warehouses import router as warehouses_router
from .homepage import router as homepage_router

router = APIRouter()
router.include_router(user_router, prefix='/user', tags=['user'])
router.include_router(transactions_router, tags=['transactions'])
router.include_router(inventory_router, tags=['inventory'])
router.include_router(products_router, tags=['products'])
router.include_router(orders_router, tags=['orders'])
router.include_router(otpr_router, tags=['otpr'])
router.include_router(inventory_turnover_router, tags=['inventory'])
router.include_router(warehouses_router, tags=['warehouses'])
router.include_router(homepage_router, tags=['homepage'])
