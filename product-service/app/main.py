from fastapi import FastAPI
from app.api.routes_products import router as products_router
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": settings.APP_NAME}

app.include_router(products_router)