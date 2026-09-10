"""
PlaceMate AI — Authorization Foundation & Middleware

Provides reusable FastAPI authorization dependencies ensuring students can only
access their own private placement preparation and application tracking data.
"""

from fastapi import Request, HTTPException, status, Depends
from typing import Optional, Dict, Any
from security.core.security.auth import JWTAuth, StudentTokenPayload


def get_bearer_token(request: Request) -> Optional[str]:
    """Extracts Authorization Bearer token from request headers."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_current_student(request: Request) -> StudentTokenPayload:
    """FastAPI Dependency: Authenticates Bearer token and returns StudentTokenPayload."""
    token = get_bearer_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload_dict = JWTAuth.verify_access_token(token)
    if not payload_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication session. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student_id = payload_dict.get("student_id")
    email = payload_dict.get("email")
    name = payload_dict.get("name", "Student")
    role = payload_dict.get("role", "student")

    if not student_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return StudentTokenPayload(
        student_id=student_id,
        email=email,
        name=name,
        role=role,
    )


def verify_student_ownership(
    requested_student_id: str,
    current_student: StudentTokenPayload = Depends(get_current_student),
) -> StudentTokenPayload:
    """FastAPI Dependency: Authorizes access only if current student owns requested resource."""
    if current_student.student_id != requested_student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: You are not authorized to view or modify another student's placement data.",
        )
    return current_student
