from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    """
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
