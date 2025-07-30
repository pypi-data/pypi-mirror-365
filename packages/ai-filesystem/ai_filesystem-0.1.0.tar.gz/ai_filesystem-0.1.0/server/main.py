"""Main FastAPI application."""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import db
from .routers import files
from .auth import get_current_user, get_dev_user
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(
    title="AI Filesystem Service",
    version="0.1.0",
    lifespan=lifespan
)

# Override auth dependency in development mode
if settings.dev_mode:
    app.dependency_overrides[get_current_user] = get_dev_user

app.include_router(files.router, prefix="/v1")