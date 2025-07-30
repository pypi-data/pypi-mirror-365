"""
Type definitions for the Swimmable Python SDK
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict


@dataclass
class Coordinates:
    """Geographic coordinates (latitude and longitude)"""
    lat: float
    lon: float


@dataclass
class SwimmableConfig:
    """Configuration for the Swimmable client"""
    api_key: Optional[str] = None
    base_url: str = "https://api.swimmable.app"
    timeout: float = 10.0
    headers: Optional[Dict[str, str]] = None


@dataclass
class BasicConditions:
    """Basic swimming conditions for a location"""
    air_temperature: float
    water_temperature: float
    weather_description: str
    uv_index: float
    wind_speed: float
    wave_height: float
    timestamp: str
    demo: Optional[bool] = None
    note: Optional[str] = None


@dataclass
class TemperatureData:
    """Temperature data with value and unit"""
    value: float
    unit: str


@dataclass
class BacteriaData:
    """Bacteria level data"""
    enterococcus: float
    threshold: float
    status: str


@dataclass
class WaterConditions:
    """Water quality conditions"""
    temperature: TemperatureData
    ph: float
    turbidity: str
    bacteria: BacteriaData


@dataclass
class WaveData:
    """Wave data with value and unit"""
    value: float
    unit: str


@dataclass
class CurrentData:
    """Current speed data"""
    value: float
    unit: str


@dataclass
class OceanConditions:
    """Ocean and surf conditions"""
    wave_height: WaveData
    wave_period: WaveData
    current_speed: CurrentData
    rip_risk: str
    tide_status: str


@dataclass
class AirTempData:
    """Air temperature data"""
    value: float
    unit: str


@dataclass
class WindData:
    """Wind speed data"""
    value: float
    unit: str


@dataclass
class VisibilityData:
    """Visibility data"""
    value: float
    unit: str


@dataclass
class WeatherConditions:
    """Weather conditions"""
    air_temp: AirTempData
    wind_speed: WindData
    wind_direction: str
    uv_index: float
    visibility: VisibilityData
    cloud_cover: float
    precipitation: str


@dataclass
class Subscores:
    """Breakdown of swimmability subscores"""
    temperature: float
    water_quality: float
    surf_hazard: float
    meteorology: float


@dataclass
class LocationInfo:
    """Location information"""
    name: str
    lat: float
    lon: float
    timezone: str


@dataclass
class ConditionsData:
    """Container for all condition types"""
    water: WaterConditions
    ocean: OceanConditions
    weather: WeatherConditions


@dataclass
class DataAge:
    """Age of different data sources in minutes"""
    NDBC: float
    EPA: float
    weather: float


@dataclass
class EnhancedConditions:
    """Enhanced swimming conditions with detailed analysis"""
    swimmability_score: float
    location: LocationInfo
    timestamp: str
    subscores: Subscores
    conditions: ConditionsData
    warnings: List[str]
    data_age: DataAge
    demo: Optional[bool] = None
    note: Optional[str] = None


@dataclass
class SpotInfo:
    """Information about a swimming spot"""
    id: int
    name: str
    lat: float
    lon: float
    description: str
    region: str
    nearest_noaa_station: Optional[str] = None


@dataclass
class SpotsResponse:
    """Response containing multiple swimming spots"""
    spots: List[SpotInfo]
    count: int
    note: Optional[str] = None


@dataclass
class HealthStatus:
    """API health status information"""
    status: str
    timestamp: str
    service: str
    version: str
    environment: str
    database: str
    cache: str


@dataclass
class EndpointUsage:
    """Usage statistics for a specific endpoint"""
    endpoint: str
    count: int


@dataclass
class UsageStats:
    """API usage statistics"""
    total_requests: int
    successful_requests: int
    error_requests: int
    avg_response_time: float
    top_endpoints: List[EndpointUsage]


@dataclass
class ApiKeyPermissions:
    """API key permissions"""
    endpoints: List[str]
    rate_limit: int


@dataclass
class ApiKeyInfo:
    """Information about an API key"""
    id: str
    name: str
    key_prefix: str
    description: Optional[str]
    permissions: ApiKeyPermissions
    is_active: bool
    last_used_at: Optional[str]
    expires_at: Optional[str]
    created_at: str


@dataclass
class CreateApiKeyRequest:
    """Request data for creating a new API key"""
    name: str
    description: Optional[str] = None
    permissions: Optional[ApiKeyPermissions] = None
    expires_in_days: Optional[int] = None


@dataclass
class CreateApiKeyResponse:
    """Response data when creating a new API key"""
    api_key: str
    api_key_record: ApiKeyInfo


class ApiErrorDict(TypedDict):
    """Dictionary structure for API errors"""
    error: str
    message: str
    path: Optional[str]
    signup: Optional[str]
    docs: Optional[str]


class RequestOptions(TypedDict, total=False):
    """Options for API requests"""
    timeout: float
    headers: Dict[str, str]