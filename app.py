from contextlib import asynccontextmanager
from fastapi import FastAPI

from config import validate_config
from sqlite_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_config()
    init_db()

    yield

app = FastAPI(
    title="Internal Knowledge AI Agent",
    version="1.0.1",
    lifespan=lifespan
)

from routers.auth_router import router as auth_router

app.include_router(auth_router)

@app.get(
    "/"
)
def root():
    return {
        "status": "ok",
        "message": "Internal Knowledge AI Agent"
    }

@app.get(
    "/health"
)
def health():
    return {
        "status": "healthy"
    }