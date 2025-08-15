from fastapi import APIRouter

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("")
async def list_products():
    return {"items": [], "total": 0}
