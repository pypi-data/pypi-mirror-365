"""
Utility functions for the Swimmable Python SDK
"""

import re
import math
from typing import List, Optional, TypeVar, Generic
from datetime import datetime, timedelta

from .types import Coordinates, EnhancedConditions, SpotInfo
from .exceptions import SwimmableValidationError

T = TypeVar('T', bound=SpotInfo)


class LocationUtils:
    """Utilities for working with coordinates and locations"""
    
    @staticmethod
    def validate_coordinates(coordinates: Coordinates) -> bool:
        """
        Validate that coordinates are within valid ranges
        
        Args:
            coordinates: Coordinates to validate
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return (
            -90 <= coordinates.lat <= 90 and 
            -180 <= coordinates.lon <= 180
        )
    
    @staticmethod
    def calculate_distance(coord1: Coordinates, coord2: Coordinates) -> float:
        """
        Calculate the distance between two coordinates using the Haversine formula
        
        Args:
            coord1: First coordinate
            coord2: Second coordinate
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(coord1.lat)
        lat2_rad = math.radians(coord2.lat)
        dlat_rad = math.radians(coord2.lat - coord1.lat)
        dlon_rad = math.radians(coord2.lon - coord1.lon)
        
        a = (
            math.sin(dlat_rad / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon_rad / 2) ** 2
        )
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    @staticmethod
    def find_nearest_spot(target: Coordinates, spots: List[T]) -> Optional[T]:
        """
        Find the nearest spot from a list of coordinates
        
        Args:
            target: Target coordinates
            spots: List of spots with coordinates
            
        Returns:
            The nearest spot, or None if the list is empty
        """
        if not spots:
            return None
        
        nearest = spots[0]
        min_distance = LocationUtils.calculate_distance(
            target, 
            Coordinates(nearest.lat, nearest.lon)
        )
        
        for spot in spots[1:]:
            distance = LocationUtils.calculate_distance(
                target, 
                Coordinates(spot.lat, spot.lon)
            )
            if distance < min_distance:
                min_distance = distance
                nearest = spot
        
        return nearest


class ConditionsUtils:
    """Utilities for working with swimming conditions"""
    
    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert temperature from Celsius to Fahrenheit"""
        return (celsius * 9/5) + 32
    
    @staticmethod  
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Convert temperature from Fahrenheit to Celsius"""
        return (fahrenheit - 32) * 5/9
    
    @staticmethod
    def get_swimmability_description(score: float) -> str:
        """
        Get a human-readable description of the swimmability score
        
        Args:
            score: Swimmability score (1-10)
            
        Returns:
            Human-readable description
        """
        if score >= 9:
            return "Excellent swimming conditions"
        elif score >= 7:
            return "Good swimming conditions"
        elif score >= 5:
            return "Fair swimming conditions"
        elif score >= 3:
            return "Poor swimming conditions"
        else:
            return "Dangerous swimming conditions"
    
    @staticmethod
    def get_swimmability_color(score: float) -> str:
        """
        Get a color code for the swimmability score (useful for UI)
        
        Args:
            score: Swimmability score (1-10)
            
        Returns:
            Hex color code
        """
        if score >= 8:
            return "#10B981"  # Green
        elif score >= 6:
            return "#F59E0B"  # Yellow
        elif score >= 4:
            return "#F97316"  # Orange
        else:
            return "#EF4444"  # Red
    
    @staticmethod
    def is_safe_for_swimming(conditions: EnhancedConditions) -> bool:
        """
        Check if conditions are safe for swimming based on various factors
        
        Args:
            conditions: Enhanced conditions object
            
        Returns:
            True if conditions are considered safe for swimming
        """
        # Basic safety checks
        if conditions.swimmability_score < 5:
            return False
        
        if conditions.warnings:
            return False
        
        # Check water temperature (too cold can be dangerous)
        water_temp = conditions.conditions.water.temperature.value
        if water_temp < 15:  # Below 15°C is generally too cold
            return False
        
        return True


class ApiKeyUtils:
    """Utilities for API key management"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate API key format
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if the API key format is valid
        """
        # Swimmable API keys start with 'swm_' followed by 64 hex characters
        pattern = r'^swm_[a-f0-9]{64}$'
        return bool(re.match(pattern, api_key))
    
    @staticmethod
    def get_key_prefix(api_key: str) -> str:
        """
        Get the prefix of an API key (for display purposes)
        
        Args:
            api_key: Full API key
            
        Returns:
            Truncated key for display
        """
        if len(api_key) < 12:
            return api_key
        return f"{api_key[:12]}..."
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """
        Mask an API key for secure display
        
        Args:
            api_key: API key to mask
            
        Returns:
            Masked API key
        """
        if len(api_key) < 8:
            return "*" * len(api_key)
        
        start = api_key[:4]
        end = api_key[-4:]
        middle = "*" * (len(api_key) - 8)
        return f"{start}{middle}{end}"


class RateLimiter:
    """Rate limiting utilities for client-side throttling"""
    
    def __init__(self, max_requests: int = 100, window_seconds: float = 60.0) -> None:
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[datetime] = []
    
    def can_make_request(self) -> bool:
        """
        Check if a request can be made without exceeding rate limits
        
        Returns:
            True if a request can be made
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Remove requests outside the current window
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]
        
        return len(self.requests) < self.max_requests
    
    def record_request(self) -> None:
        """Record a request (call this after making a successful request)"""
        self.requests.append(datetime.now())
    
    def get_remaining_requests(self) -> int:
        """
        Get the number of requests remaining in the current window
        
        Returns:
            Number of remaining requests
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Remove requests outside the current window
        self.requests = [req_time for req_time in self.requests if req_time > cutoff]
        
        return max(0, self.max_requests - len(self.requests))
    
    def get_reset_time(self) -> float:
        """
        Get the time until the rate limit window resets (in seconds)
        
        Returns:
            Seconds until reset, or 0 if no limit is active
        """
        if not self.requests:
            return 0.0
        
        oldest_request = min(self.requests)
        reset_time = oldest_request + timedelta(seconds=self.window_seconds)
        remaining = (reset_time - datetime.now()).total_seconds()
        
        return max(0.0, remaining)