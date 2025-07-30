"""
Swimmable API Client
Official Python SDK for the Swimmable API
"""

import json
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
import requests

from .types import (
    SwimmableConfig,
    Coordinates,
    BasicConditions,
    EnhancedConditions,
    SpotsResponse,
    SpotInfo,
    HealthStatus,
    UsageStats,
    ApiKeyInfo,
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    RequestOptions,
    TemperatureData,
    BacteriaData,
    WaterConditions,
    WaveData,
    CurrentData,
    OceanConditions,
    AirTempData,
    WindData,
    VisibilityData,
    WeatherConditions,
    Subscores,
    LocationInfo,
    ConditionsData,
    DataAge,
    EndpointUsage,
    ApiKeyPermissions,
)
from .exceptions import (
    SwimmableError,
    SwimmableAPIError,
    SwimmableTimeoutError,
    SwimmableValidationError,
    SwimmableAuthenticationError,
    SwimmableRateLimitError,
)
from .utils import LocationUtils


class SwimmableClient:
    """
    Official Python client for the Swimmable API
    
    Provides access to real-time swimming conditions, water quality data,
    and AI-powered safety scores for beaches, lakes, and pools worldwide.
    
    Example:
        Basic usage (no API key required):
        
        >>> client = SwimmableClient()
        >>> conditions = client.get_conditions(lat=34.0522, lon=-118.2437)
        >>> print(f"Water temperature: {conditions.water_temperature}°C")
        
        With API key for enhanced features:
        
        >>> client = SwimmableClient(api_key="your-api-key-here")
        >>> enhanced = client.get_enhanced_conditions(lat=34.0522, lon=-118.2437)
        >>> print(f"Swimmability score: {enhanced.swimmability_score}/10")
    """
    
    def __init__(self, config: Optional[SwimmableConfig] = None, **kwargs) -> None:
        """
        Initialize the Swimmable client
        
        Args:
            config: Configuration object
            **kwargs: Individual configuration parameters
        """
        if config is None:
            config = SwimmableConfig()
        
        # Allow kwargs to override config
        self.api_key = kwargs.get('api_key') or config.api_key
        self.base_url = kwargs.get('base_url') or config.base_url
        self.timeout = kwargs.get('timeout') or config.timeout
        self.headers = kwargs.get('headers') or config.headers or {}
        
        # Set up session
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Swimmable-Python-SDK/1.0.0',
            **self.headers
        })
        
        if self.api_key:
            self.session.headers['X-API-Key'] = self.api_key
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        requires_auth: bool = False,
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Swimmable API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body data
            requires_auth: Whether authentication is required
            timeout: Request timeout
            headers: Additional headers
            
        Returns:
            JSON response data
            
        Raises:
            SwimmableError: For various API errors
        """
        if requires_auth and not self.api_key:
            raise SwimmableValidationError(
                "API key is required for this endpoint. "
                "Please provide an api_key when creating the client."
            )
        
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        request_timeout = timeout or self.timeout
        request_headers = headers or {}
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=request_timeout,
                headers=request_headers,
            )
            
            # Parse response
            try:
                data = response.json()
            except json.JSONDecodeError:
                # If not JSON, treat as text
                data = {"message": response.text}
            
            # Handle error responses
            if not response.ok:
                error_message = data.get('message', f'HTTP {response.status_code}: {response.reason}')
                error_code = data.get('error')
                
                if response.status_code == 401:
                    raise SwimmableAuthenticationError(
                        error_message, response.status_code, error_code, endpoint
                    )
                elif response.status_code == 403:
                    raise SwimmableAuthenticationError(
                        error_message, response.status_code, error_code, endpoint
                    )
                elif response.status_code == 429:
                    retry_after = response.headers.get('Retry-After')
                    retry_seconds = int(retry_after) if retry_after else None
                    raise SwimmableRateLimitError(
                        error_message, retry_seconds, endpoint
                    )
                else:
                    raise SwimmableAPIError(
                        error_message, response.status_code, error_code, endpoint, data
                    )
            
            return data
            
        except requests.exceptions.Timeout:
            raise SwimmableTimeoutError(
                f"Request timed out after {request_timeout}s", request_timeout
            )
        except requests.exceptions.RequestException as e:
            raise SwimmableError(f"Request failed: {str(e)}")
    
    def get_conditions(
        self, 
        lat: float, 
        lon: float, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> BasicConditions:
        """
        Get basic swimming conditions for a location
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            Basic conditions data
            
        Example:
            >>> client = SwimmableClient()
            >>> conditions = client.get_conditions(34.0522, -118.2437)
            >>> print(f"Water temp: {conditions.water_temperature}°C")
        """
        coordinates = Coordinates(lat=lat, lon=lon)
        if not LocationUtils.validate_coordinates(coordinates):
            raise SwimmableValidationError(
                f"Invalid coordinates: lat={lat}, lon={lon}. "
                "Latitude must be between -90 and 90, longitude between -180 and 180."
            )
        
        params = {'lat': lat, 'lon': lon}
        data = self._make_request(
            'GET', '/api/public/conditions', params=params,
            timeout=timeout, headers=headers
        )
        
        return BasicConditions(
            air_temperature=data['airTemperature'],
            water_temperature=data['waterTemperature'],
            weather_description=data['weatherDescription'],
            uv_index=data['uvIndex'],
            wind_speed=data['windSpeed'],
            wave_height=data['waveHeight'],
            timestamp=data['timestamp'],
            demo=data.get('_demo'),
            note=data.get('_note'),
        )
    
    def get_enhanced_conditions(
        self, 
        lat: float, 
        lon: float, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> EnhancedConditions:
        """
        Get enhanced swimming conditions with detailed analysis
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            Enhanced conditions with swimmability scores and detailed analysis
            
        Example:
            >>> client = SwimmableClient()
            >>> enhanced = client.get_enhanced_conditions(34.0522, -118.2437)
            >>> print(f"Swimmability score: {enhanced.swimmability_score}/10")
            >>> if enhanced.warnings:
            >>>     print("⚠️ Warnings:", enhanced.warnings)
        """
        coordinates = Coordinates(lat=lat, lon=lon)
        if not LocationUtils.validate_coordinates(coordinates):
            raise SwimmableValidationError(
                f"Invalid coordinates: lat={lat}, lon={lon}. "
                "Latitude must be between -90 and 90, longitude between -180 and 180."
            )
        
        params = {'lat': lat, 'lon': lon}
        data = self._make_request(
            'GET', '/api/public/conditions/enhanced', params=params,
            timeout=timeout, headers=headers
        )
        
        # Parse nested structures
        location = LocationInfo(
            name=data['location']['name'],
            lat=data['location']['lat'],
            lon=data['location']['lon'],
            timezone=data['location']['timezone'],
        )
        
        subscores = Subscores(
            temperature=data['subscores']['temperature'],
            water_quality=data['subscores']['waterQuality'],
            surf_hazard=data['subscores']['surfHazard'],
            meteorology=data['subscores']['meteorology'],
        )
        
        water_conditions = WaterConditions(
            temperature=TemperatureData(
                value=data['conditions']['water']['temperature']['value'],
                unit=data['conditions']['water']['temperature']['unit'],
            ),
            ph=data['conditions']['water']['ph'],
            turbidity=data['conditions']['water']['turbidity'],
            bacteria=BacteriaData(
                enterococcus=data['conditions']['water']['bacteria']['enterococcus'],
                threshold=data['conditions']['water']['bacteria']['threshold'],
                status=data['conditions']['water']['bacteria']['status'],
            ),
        )
        
        ocean_conditions = OceanConditions(
            wave_height=WaveData(
                value=data['conditions']['ocean']['waveHeight']['value'],
                unit=data['conditions']['ocean']['waveHeight']['unit'],
            ),
            wave_period=WaveData(
                value=data['conditions']['ocean']['wavePeriod']['value'],
                unit=data['conditions']['ocean']['wavePeriod']['unit'],
            ),
            current_speed=CurrentData(
                value=data['conditions']['ocean']['currentSpeed']['value'],
                unit=data['conditions']['ocean']['currentSpeed']['unit'],
            ),
            rip_risk=data['conditions']['ocean']['ripRisk'],
            tide_status=data['conditions']['ocean']['tideStatus'],
        )
        
        weather_conditions = WeatherConditions(
            air_temp=AirTempData(
                value=data['conditions']['weather']['airTemp']['value'],
                unit=data['conditions']['weather']['airTemp']['unit'],
            ),
            wind_speed=WindData(
                value=data['conditions']['weather']['windSpeed']['value'],
                unit=data['conditions']['weather']['windSpeed']['unit'],
            ),
            wind_direction=data['conditions']['weather']['windDirection'],
            uv_index=data['conditions']['weather']['uvIndex'],
            visibility=VisibilityData(
                value=data['conditions']['weather']['visibility']['value'],
                unit=data['conditions']['weather']['visibility']['unit'],
            ),
            cloud_cover=data['conditions']['weather']['cloudCover'],
            precipitation=data['conditions']['weather']['precipitation'],
        )
        
        conditions = ConditionsData(
            water=water_conditions,
            ocean=ocean_conditions,
            weather=weather_conditions,
        )
        
        data_age = DataAge(
            NDBC=data['dataAge']['NDBC'],
            EPA=data['dataAge']['EPA'],
            weather=data['dataAge']['weather'],
        )
        
        return EnhancedConditions(
            swimmability_score=data['swimmabilityScore'],
            location=location,
            timestamp=data['timestamp'],
            subscores=subscores,
            conditions=conditions,
            warnings=data['warnings'],
            data_age=data_age,
            demo=data.get('_demo'),
            note=data.get('_note'),
        )
    
    def get_spots(
        self, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> SpotsResponse:
        """
        Get list of available swimming spots
        
        Args:
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            List of swimming spots with metadata
            
        Example:
            >>> client = SwimmableClient()
            >>> spots = client.get_spots()
            >>> print(f"Found {spots.count} swimming spots")
            >>> for spot in spots.spots:
            >>>     print(f"{spot.name} - {spot.region}")
        """
        data = self._make_request(
            'GET', '/api/public/spots',
            timeout=timeout, headers=headers
        )
        
        spots = [
            SpotInfo(
                id=spot['id'],
                name=spot['name'],
                lat=spot['lat'],
                lon=spot['lon'],
                description=spot['description'],
                region=spot['region'],
                nearest_noaa_station=spot.get('nearestNOAAStation'),
            )
            for spot in data['spots']
        ]
        
        return SpotsResponse(
            spots=spots,
            count=data['count'],
            note=data.get('note'),
        )
    
    def get_health(
        self, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> HealthStatus:
        """
        Get API health status
        
        Args:
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            Health status information
        """
        data = self._make_request(
            'GET', '/api/health',
            timeout=timeout, headers=headers
        )
        
        return HealthStatus(
            status=data['status'],
            timestamp=data['timestamp'],
            service=data['service'],
            version=data['version'],
            environment=data['environment'],
            database=data['database'],
            cache=data['cache'],
        )
    
    def get_usage_stats(
        self, 
        days: int = 30, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> UsageStats:
        """
        Get your API usage statistics (requires API key)
        
        Args:
            days: Number of days to look back (default: 30)
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            Usage statistics
            
        Example:
            >>> client = SwimmableClient(api_key="your-key")
            >>> stats = client.get_usage_stats(30)
            >>> print(f"Total requests: {stats.total_requests}")
            >>> success_rate = stats.successful_requests / stats.total_requests * 100
            >>> print(f"Success rate: {success_rate:.1f}%")
        """
        params = {'days': days}
        data = self._make_request(
            'GET', '/api/keys/usage', params=params,
            requires_auth=True, timeout=timeout, headers=headers
        )
        
        top_endpoints = [
            EndpointUsage(endpoint=ep['endpoint'], count=ep['count'])
            for ep in data['top_endpoints']
        ]
        
        return UsageStats(
            total_requests=data['total_requests'],
            successful_requests=data['successful_requests'],
            error_requests=data['error_requests'],
            avg_response_time=data['avg_response_time'],
            top_endpoints=top_endpoints,
        )
    
    def get_api_keys(
        self, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> List[ApiKeyInfo]:
        """
        Get your API keys (requires authentication)
        
        Args:
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            List of API key information
            
        Example:
            >>> client = SwimmableClient(api_key="your-key")
            >>> keys = client.get_api_keys()
            >>> for key in keys:
            >>>     status = "Active" if key.is_active else "Inactive"
            >>>     print(f"{key.name}: {status}")
        """
        data = self._make_request(
            'GET', '/api/keys',
            requires_auth=True, timeout=timeout, headers=headers
        )
        
        return [
            ApiKeyInfo(
                id=key['id'],
                name=key['name'],
                key_prefix=key['key_prefix'],
                description=key.get('description'),
                permissions=ApiKeyPermissions(
                    endpoints=key['permissions']['endpoints'],
                    rate_limit=key['permissions']['rate_limit'],
                ),
                is_active=key['is_active'],
                last_used_at=key.get('last_used_at'),
                expires_at=key.get('expires_at'),
                created_at=key['created_at'],
            )
            for key in data['api_keys']
        ]
    
    def create_api_key(
        self, 
        key_data: CreateApiKeyRequest, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> CreateApiKeyResponse:
        """
        Create a new API key (requires authentication)
        
        Args:
            key_data: API key creation data
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            New API key information
            
        Example:
            >>> client = SwimmableClient(api_key="your-key")
            >>> request = CreateApiKeyRequest(
            >>>     name="My App Key",
            >>>     description="API key for my swimming app"
            >>> )
            >>> response = client.create_api_key(request)
            >>> print(f"New API key: {response.api_key}")
            >>> # ⚠️ Save this key securely - you won't see it again!
        """
        json_data = {
            'name': key_data.name,
        }
        
        if key_data.description:
            json_data['description'] = key_data.description
        
        if key_data.permissions:
            json_data['permissions'] = {
                'endpoints': key_data.permissions.endpoints,
                'rate_limit': key_data.permissions.rate_limit,
            }
        
        if key_data.expires_in_days:
            json_data['expires_in_days'] = key_data.expires_in_days
        
        data = self._make_request(
            'POST', '/api/keys', json_data=json_data,
            requires_auth=True, timeout=timeout, headers=headers
        )
        
        api_key_record = ApiKeyInfo(
            id=data['api_key_record']['id'],
            name=data['api_key_record']['name'],
            key_prefix=data['api_key_record']['key_prefix'],
            description=data['api_key_record'].get('description'),
            permissions=ApiKeyPermissions(
                endpoints=data['api_key_record']['permissions']['endpoints'],
                rate_limit=data['api_key_record']['permissions']['rate_limit'],
            ),
            is_active=data['api_key_record']['is_active'],
            last_used_at=data['api_key_record'].get('last_used_at'),
            expires_at=data['api_key_record'].get('expires_at'),
            created_at=data['api_key_record']['created_at'],
        )
        
        return CreateApiKeyResponse(
            api_key=data['api_key'],
            api_key_record=api_key_record,
        )
    
    def revoke_api_key(
        self, 
        key_id: str, 
        timeout: Optional[float] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Revoke an API key (requires authentication)
        
        Args:
            key_id: ID of the API key to revoke
            timeout: Request timeout in seconds
            headers: Additional headers
            
        Returns:
            True if successful
        """
        data = self._make_request(
            'DELETE', f'/api/keys/{key_id}',
            requires_auth=True, timeout=timeout, headers=headers
        )
        
        return data.get('success', False)
    
    def set_api_key(self, api_key: str) -> None:
        """
        Update the API key for this client
        
        Args:
            api_key: New API key
        """
        self.api_key = api_key
        if api_key:
            self.session.headers['X-API-Key'] = api_key
        elif 'X-API-Key' in self.session.headers:
            del self.session.headers['X-API-Key']
    
    def get_config(self) -> SwimmableConfig:
        """
        Get the current configuration
        
        Returns:
            Current configuration
        """
        return SwimmableConfig(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            headers=dict(self.headers),
        )
    
    def update_config(self, **kwargs) -> None:
        """
        Update client configuration
        
        Args:
            **kwargs: Configuration parameters to update
        """
        if 'api_key' in kwargs:
            self.set_api_key(kwargs['api_key'])
        
        if 'base_url' in kwargs:
            self.base_url = kwargs['base_url']
        
        if 'timeout' in kwargs:
            self.timeout = kwargs['timeout']
        
        if 'headers' in kwargs:
            self.headers.update(kwargs['headers'])
            self.session.headers.update(kwargs['headers'])


def create_client(config: Optional[SwimmableConfig] = None, **kwargs) -> SwimmableClient:
    """
    Create a new Swimmable client instance
    
    Args:
        config: Configuration object
        **kwargs: Individual configuration parameters
        
    Returns:
        New SwimmableClient instance
        
    Example:
        >>> client = create_client(api_key="your-key")
        >>> # or
        >>> config = SwimmableConfig(api_key="your-key", timeout=15.0)
        >>> client = create_client(config)
    """
    return SwimmableClient(config, **kwargs)