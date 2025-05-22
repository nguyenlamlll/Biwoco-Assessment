from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root():
    """
    Root endpoint, serving as a health check endpoint for now.
    """
    return {"status": "ok"}