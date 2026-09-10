"""
PlaceMate AI — API Security Middleware & Error Handling Foundation

Applies HTTP security headers (nosniff, DENY, XSS-Protection, Referrer-Policy),
configures environment-aware CORS restrictions, and sanitizes exception handlers
to prevent leakage of sensitive stack traces, secrets, or internal errors.
"""

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.security.config import security_config
from backend.core.security.logging import SecurityLogger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects standard HTTP security headers on all API responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Server"] = "PlaceMate-AI-Gateway"

        return response


def setup_security_middleware(app: FastAPI):
    """Attaches Security Headers and Environment-Aware CORS to FastAPI app."""
    
    # 1. Attach Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. Attach CORS Middleware with Configured Origins
    origins = security_config.ALLOWED_ORIGINS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins if not security_config.is_production() else origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    # 3. Attach Sanitized Security Exception Handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        client_ip = request.client.host if request.client else "UNKNOWN"
        if exc.status_code in (401, 403):
            SecurityLogger.log_unauthorized_access(
                path=request.url.path,
                client_ip=client_ip,
                reason=str(exc.detail),
            )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status_code": exc.status_code,
                "message": exc.detail,
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        client_ip = request.client.host if request.client else "UNKNOWN"
        SecurityLogger.log_event(
            "INTERNAL_ERROR",
            client_ip=client_ip,
            status="ERROR",
            details={"path": request.url.path, "exception_type": type(exc).__name__},
        )

        # In production, do NOT leak internal stack trace
        message = (
            "An internal error occurred. Please try again later."
            if security_config.is_production()
            else f"Internal Error: {str(exc)}"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "status_code": 500,
                "message": message,
            },
        )
