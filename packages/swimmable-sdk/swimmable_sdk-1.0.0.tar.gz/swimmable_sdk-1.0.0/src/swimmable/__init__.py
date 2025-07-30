"""
Swimmable Python SDK

Official Python SDK for the Swimmable API - Real-time swimming conditions and water quality data.

Example:
    Basic usage with no API key required:
    
    >>> from swimmable import SwimmableClient
    >>> client = SwimmableClient()
    >>> conditions = client.get_conditions(lat=34.0522, lon=-118.2437)
    >>> print(f"Water temperature: {conditions.water_temperature}°C")
    
    Enhanced usage with API key:
    
    >>> client = SwimmableClient(api_key="your-api-key-here")
    >>> enhanced = client.get_enhanced_conditions(lat=34.0522, lon=-118.2437)
    >>> print(f"Swimmability score: {enhanced.swimmability_score}/10")
"""

from .client import SwimmableClient, create_client
from .exceptions import SwimmableError, SwimmableAPIError, SwimmableTimeoutError
from .types import (
    BasicConditions,
    EnhancedConditions,
    SpotsResponse,
    SpotInfo,
    Coordinates,
    SwimmableConfig,
    UsageStats,
    ApiKeyInfo,
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    HealthStatus,
)

__version__ = "1.0.0"
__author__ = "Swimmable"
__email__ = "developers@swimmable.app"

__all__ = [
    # Main client
    "SwimmableClient",
    "create_client",
    # Exceptions
    "SwimmableError",
    "SwimmableAPIError", 
    "SwimmableTimeoutError",
    # Types
    "BasicConditions",
    "EnhancedConditions",
    "SpotsResponse",
    "SpotInfo",
    "Coordinates",
    "SwimmableConfig",
    "UsageStats",
    "ApiKeyInfo",
    "CreateApiKeyRequest",
    "CreateApiKeyResponse",
    "HealthStatus",
    # Version
    "__version__",
]