from fastapi import APIRouter
from app.api.endpoints import health, products, orders

router = APIRouter()

router.include_router(health.router,
                      tags=['Health'], 
                      prefix='/api/v1')
router.include_router(products.router,
                      tags=['Products'], 
                      prefix='/api/v1')
router.include_router(orders.router,
                      tags=['Orders'], 
                      prefix='/api/v1')