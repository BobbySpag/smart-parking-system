"""Smart Parking System – FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import create_tables
from .routes import auth, parking, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown logic."""
    # Startup
    await create_tables()
    yield
    # Shutdown – nothing extra required; engine cleanup is handled by GC


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(parking.router)
    app.include_router(admin.router)

    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


app = create_app()
