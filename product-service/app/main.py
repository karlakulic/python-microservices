from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes_products import router as products_router
from app.config import settings

from app.db.session import Base, engine   
from app import models
from app.messaging.consumer import start_consumer_in_thread

async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_consumer_in_thread()
    yield

app = FastAPI(title=settings.APP_NAME, lifespan = lifespan)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": settings.APP_NAME}

app.include_router(products_router)