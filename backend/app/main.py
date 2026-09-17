"""
CareFlow AI — Main FastAPI Application Entry Point.

Combines middleware, routing, configuration, and exception handling.
Source of truth: docs/system-architecture.md & docs/api.md.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router


def create_application() -> FastAPI:
    """
    Application factory pattern.
    Configures and returns the FastAPI application instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
        docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
        redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
    )

    # Configure CORS Middleware
    # Disallows wildcard '*' in production according to docs/safety-privacy.md
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Mount API v1 router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Root"], summary="Root endpoint")
    def root():
        """
        Root endpoint providing service information and link to health check.
        """
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "health_check": f"{settings.API_V1_STR}/health",
            "docs": f"{settings.API_V1_STR}/docs",
        }

    if settings.DEBUG:
        @app.get("/docs", include_in_schema=False)
        def docs_redirect():
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

        @app.get("/redoc", include_in_schema=False)
        def redoc_redirect():
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=f"{settings.API_V1_STR}/redoc")

    return app


app = create_application()
