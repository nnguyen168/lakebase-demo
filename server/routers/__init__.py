# Generic router module for the Databricks app template
# Add your FastAPI routes here

from fastapi import APIRouter

from .user import router as user_router
from .orders import router as orders_router
from .inventory import router as inventory_router

router = APIRouter()
router.include_router(user_router, prefix='/user', tags=['user'])
router.include_router(orders_router, tags=['orders'])
router.include_router(inventory_router, tags=['inventory'])
