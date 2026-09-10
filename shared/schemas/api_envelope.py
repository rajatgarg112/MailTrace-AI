"""
shared/schemas/api_envelope.py
─────────────────────────────────────────────────────────────────────────────
Standard API response envelope shared by the Backend (Member 2).

All FastAPI endpoints should return ApiEnvelope[T] to ensure consistent
response shapes across the project.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiEnvelope(BaseModel, Generic[T]):
    """
    Standard JSON envelope wrapping all Backend API responses.

    Example:
        {
          "success": true,
          "message": "Email fetched successfully.",
          "data": { ... }
        }
    """

    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
