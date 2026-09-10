"""
PlaceMate AI — Input Validation & Data Sanitization Strategy

Validates user inputs (Name, Email, Password, Search Queries, Coding Answers,
Aptitude Answers, Company Applications) and strips dangerous script/HTML injection patterns.
"""

from pydantic import BaseModel, EmailStr, Field, validator
import html
import re
from typing import Optional, List, Dict, Any


class InputSanitizer:
    """Sanitizes strings to prevent XSS, HTML Injection, and SQL Injection vectors."""

    DANGEROUS_PATTERNS = [
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"onload\s*=", re.IGNORECASE),
        re.compile(r"onerror\s*=", re.IGNORECASE),
        re.compile(r"onclick\s*=", re.IGNORECASE),
        re.compile(r"<iframe>.*?</iframe>", re.IGNORECASE | re.DOTALL),
    ]

    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    @classmethod
    def sanitize_string(cls, input_str: str) -> str:
        """Strips HTML tags and escapes dangerous special characters."""
        if not input_str:
            return ""

        sanitized = input_str
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = pattern.sub("", sanitized)

        # HTML entity escape
        sanitized = html.escape(sanitized, quote=True)
        return sanitized.strip()

    @classmethod
    def is_valid_email(cls, email: str) -> bool:
        """Validates email format."""
        if not email or len(email) > 254:
            return False
        return bool(cls.EMAIL_REGEX.match(email))


# Pydantic Input Schemas with Automatic Security Sanitization

class StudentRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)

    @validator("name")
    def sanitize_name(cls, v):
        sanitized = InputSanitizer.sanitize_string(v)
        if len(sanitized) < 2:
            raise ValueError("Student name must be at least 2 valid characters.")
        return sanitized

    @validator("email")
    def validate_email_format(cls, v):
        v_clean = v.strip().lower()
        if not InputSanitizer.is_valid_email(v_clean):
            raise ValueError("Invalid email address format.")
        return v_clean


class StudentLoginRequest(BaseModel):
    email: str
    password: str

    @validator("email")
    def clean_email(cls, v):
        return v.strip().lower()


class CompanyApplicationRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    role_title: str = Field(..., min_length=2, max_length=100)
    status: str = Field(default="Applied")
    notes: Optional[str] = Field(default="", max_length=1000)

    @validator("company_name", "role_title", "notes")
    def sanitize_fields(cls, v):
        if v:
            return InputSanitizer.sanitize_string(v)
        return ""


class CodingProgressSubmission(BaseModel):
    problem_id: str
    code_solution: str = Field(..., max_length=10000)
    language: str = Field(..., max_length=20)

    @validator("language")
    def sanitize_lang(cls, v):
        return InputSanitizer.sanitize_string(v)
