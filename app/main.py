from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.core.database import close_db, engine
from app.api.v1.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)

app.include_router(router)


@app.get("/health", tags=["health"])
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok"}