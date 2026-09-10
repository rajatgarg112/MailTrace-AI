from typing import Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, emails, deliveries, quarantine

app = FastAPI(
    title=settings.APP_NAME,
    description="MailTrace AI Backend Foundation API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
# Allowed origins are loaded from configuration (FRONTEND_ORIGIN & ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
)

# Register routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(emails.router, prefix=settings.API_PREFIX)
app.include_router(deliveries.router, prefix=settings.API_PREFIX)
app.include_router(quarantine.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
def root() -> Dict[str, str]:
    """
    Root entrypoint providing basic API info and documentation links.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
    }
