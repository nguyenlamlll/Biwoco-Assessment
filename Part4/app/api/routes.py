from fastapi import APIRouter
from app.api.endpoints import health, products, orders, sample_products

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

# Add sample endpoint of Part 4 assignment
router.include_router(sample_products.router,
                      tags=['Part4'], 
                      prefix='/api/v1')