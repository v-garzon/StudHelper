"""Custom exception classes."""

from typing import Any, Dict, Optional


class StudHelperException(Exception):
    """Base exception for StudHelper."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(StudHelperException):
    """Authentication related errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(StudHelperException):
    """Authorization related errors."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)


class ValidationError(StudHelperException):
    """Validation related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundError(StudHelperException):
    """Resource not found errors."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ProcessingError(StudHelperException):
    """Document processing errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class RateLimitError(StudHelperException):
    """Rate limiting errors."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class ExternalServiceError(StudHelperException):
    """External service errors."""
    
    def __init__(self, message: str, service: str):
        super().__init__(f"{service}: {message}", status_code=502)

