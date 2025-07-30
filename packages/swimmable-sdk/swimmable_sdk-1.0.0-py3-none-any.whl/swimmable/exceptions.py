"""
Exception classes for the Swimmable Python SDK
"""

from typing import Optional


class SwimmableError(Exception):
    """Base exception class for all Swimmable SDK errors"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.endpoint = endpoint

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class SwimmableAPIError(SwimmableError):
    """Exception raised for API-related errors (4xx, 5xx responses)"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int,
        error_code: Optional[str] = None,
        endpoint: Optional[str] = None,
        response_data: Optional[dict] = None
    ) -> None:
        super().__init__(message, status_code, error_code, endpoint)
        self.response_data = response_data


class SwimmableTimeoutError(SwimmableError):
    """Exception raised when a request times out"""
    
    def __init__(self, message: str = "Request timed out", timeout: Optional[float] = None) -> None:
        super().__init__(message)
        self.timeout = timeout

    def __str__(self) -> str:
        if self.timeout:
            return f"{self.message} (timeout: {self.timeout}s)"
        return self.message


class SwimmableValidationError(SwimmableError):
    """Exception raised for client-side validation errors"""
    pass


class SwimmableAuthenticationError(SwimmableAPIError):
    """Exception raised for authentication-related errors (401, 403)"""
    pass


class SwimmableRateLimitError(SwimmableAPIError):
    """Exception raised when rate limits are exceeded (429)"""
    
    def __init__(
        self, 
        message: str, 
        retry_after: Optional[int] = None,
        endpoint: Optional[str] = None
    ) -> None:
        super().__init__(message, 429, "RATE_LIMIT_EXCEEDED", endpoint)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base_message = super().__str__()
        if self.retry_after:
            return f"{base_message} (retry after {self.retry_after}s)"
        return base_message