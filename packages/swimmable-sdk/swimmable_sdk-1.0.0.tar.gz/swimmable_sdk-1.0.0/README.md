# Swimmable Python SDK

[![PyPI version](https://badge.fury.io/py/swimmable-sdk.svg)](https://pypi.org/project/swimmable-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/swimmable-sdk.svg)](https://pypi.org/project/swimmable-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for the [Swimmable API](https://swimmable.app) - Get real-time swimming conditions, water quality data, and AI-powered safety scores for beaches, lakes, and pools worldwide.

## Features

- 🏊 **Real-time Swimming Conditions** - Water temperature, weather, and safety data
- 🌊 **Enhanced Analysis** - AI-powered swimmability scores and detailed breakdowns  
- 🏖️ **Global Coverage** - 15,000+ beaches, lakes, and swimming spots worldwide
- 🔒 **Type Safe** - Full type hints with comprehensive dataclass definitions
- ⚡ **Modern** - Async/await support and clean Python APIs
- 🚀 **Lightweight** - Minimal dependencies, works with Python 3.7+
- 📱 **Cross-platform** - Works on Windows, macOS, Linux, and cloud platforms

## Installation

```bash
pip install swimmable-sdk
```

```bash
poetry add swimmable-sdk
```

```bash
conda install -c conda-forge swimmable-sdk
```

## Quick Start

### Basic Usage (No API Key Required)

```python
from swimmable import SwimmableClient

client = SwimmableClient()

# Get current swimming conditions for Santa Monica Beach
conditions = client.get_conditions(lat=34.0195, lon=-118.4912)

print(f"Water temperature: {conditions.water_temperature}°C")
print(f"Air temperature: {conditions.air_temperature}°C")
print(f"Weather: {conditions.weather_description}")
```

### Enhanced Conditions with Safety Scores

```python
# Get detailed analysis with swimmability scoring
enhanced = client.get_enhanced_conditions(lat=25.7617, lon=-80.1918)  # Miami Beach

print(f"Swimmability Score: {enhanced.swimmability_score}/10")
print(f"Water Quality Score: {enhanced.subscores.water_quality}/10")
print(f"Safety Rating: {enhanced.subscores.surf_hazard}/10")

# Check for any safety warnings
if enhanced.warnings:
    print("⚠️ Safety Warnings:", enhanced.warnings)
```

### With API Key (For Production Use)

```python
client = SwimmableClient(api_key="your-api-key-here")  # Get one at https://swimmable.app/signup

# Now you can access premium features and higher rate limits
stats = client.get_usage_stats()
print(f"API calls this month: {stats.total_requests}")
```

## API Reference

### Client Configuration

```python
from swimmable import SwimmableClient, SwimmableConfig

# Using configuration object
config = SwimmableConfig(
    api_key="your-api-key",
    base_url="https://api.swimmable.app",  # Default
    timeout=10.0,  # Default timeout in seconds
    headers={"Custom-Header": "value"}
)
client = SwimmableClient(config)

# Or pass parameters directly
client = SwimmableClient(
    api_key="your-api-key",
    timeout=15.0
)
```

### Basic Methods

#### `get_conditions(lat, lon)`

Get basic swimming conditions for a location.

```python
conditions = client.get_conditions(lat=34.0522, lon=-118.2437)

# Returns BasicConditions dataclass
print(f"Air temperature: {conditions.air_temperature}°C")
print(f"Water temperature: {conditions.water_temperature}°C")
print(f"Weather: {conditions.weather_description}")
print(f"UV index: {conditions.uv_index}")
print(f"Wind speed: {conditions.wind_speed} km/h")
print(f"Wave height: {conditions.wave_height}m")
print(f"Timestamp: {conditions.timestamp}")
```

#### `get_enhanced_conditions(lat, lon)`

Get detailed analysis with AI-powered safety scores.

```python
enhanced = client.get_enhanced_conditions(lat=21.2765, lon=-157.8281)  # Waikiki Beach

print(f"Swimmability Score: {enhanced.swimmability_score}/10")
print(f"Location: {enhanced.location.name}")
print(f"Timezone: {enhanced.location.timezone}")

# Detailed subscores
print(f"Temperature Score: {enhanced.subscores.temperature}/10")
print(f"Water Quality Score: {enhanced.subscores.water_quality}/10")
print(f"Surf Hazard Score: {enhanced.subscores.surf_hazard}/10")
print(f"Weather Score: {enhanced.subscores.meteorology}/10")

# Water conditions
water = enhanced.conditions.water
print(f"Water temp: {water.temperature.value}{water.temperature.unit}")
print(f"pH level: {water.ph}")
print(f"Bacteria status: {water.bacteria.status}")

# Ocean conditions
ocean = enhanced.conditions.ocean
print(f"Wave height: {ocean.wave_height.value}{ocean.wave_height.unit}")
print(f"Rip current risk: {ocean.rip_risk}")

# Weather conditions
weather = enhanced.conditions.weather
print(f"Air temp: {weather.air_temp.value}{weather.air_temp.unit}")
print(f"Wind: {weather.wind_speed.value}{weather.wind_speed.unit} {weather.wind_direction}")
```

#### `get_spots()`

Get list of available swimming spots.

```python
spots = client.get_spots()
print(f"Found {spots.count} swimming spots")

for spot in spots.spots:
    print(f"{spot.name} - {spot.region}")
    print(f"  Coordinates: {spot.lat}, {spot.lon}")
    print(f"  Description: {spot.description}")
```

### API Management (Requires API Key)

#### `get_usage_stats(days=30)`

Get your API usage statistics.

```python
stats = client.get_usage_stats(days=30)  # Last 30 days
print(f"Total requests: {stats.total_requests}")
print(f"Successful requests: {stats.successful_requests}")
print(f"Error requests: {stats.error_requests}")
print(f"Average response time: {stats.avg_response_time}ms")

print("Top endpoints:")
for endpoint in stats.top_endpoints:
    print(f"  {endpoint.endpoint}: {endpoint.count} requests")
```

#### `get_api_keys()`

List your API keys.

```python
keys = client.get_api_keys()
for key in keys:
    status = "Active" if key.is_active else "Inactive"
    print(f"{key.name}: {status}")
    print(f"  Prefix: {key.key_prefix}")
    print(f"  Rate limit: {key.permissions.rate_limit}/hour")
    if key.expires_at:
        print(f"  Expires: {key.expires_at}")
```

#### `create_api_key(key_data)`

Create a new API key.

```python
from swimmable import CreateApiKeyRequest

request = CreateApiKeyRequest(
    name="My App Key",
    description="API key for my swimming app",
    expires_in_days=365  # Optional expiration
)

response = client.create_api_key(request)
print(f"New API key: {response.api_key}")
# ⚠️ Save this key securely - you won't see it again!

print(f"Key info: {response.api_key_record.name}")
print(f"Created: {response.api_key_record.created_at}")
```

### Utility Functions

The SDK includes helpful utility functions:

```python
from swimmable.utils import LocationUtils, ConditionsUtils, ApiKeyUtils

# Distance calculation
distance = LocationUtils.calculate_distance(
    Coordinates(lat=34.0522, lon=-118.2437),  # Santa Monica
    Coordinates(lat=25.7617, lon=-80.1918)   # Miami
)
print(f"Distance: {distance:.2f} km")

# Temperature conversion
fahrenheit = ConditionsUtils.celsius_to_fahrenheit(25)
print(f"25°C = {fahrenheit}°F")

# Safety assessment
is_safe = ConditionsUtils.is_safe_for_swimming(enhanced_conditions)
print("✅ Safe to swim" if is_safe else "⚠️ Check conditions carefully")

# API key validation
is_valid = ApiKeyUtils.validate_api_key("swm_1234567890abcdef...")
masked_key = ApiKeyUtils.mask_api_key("swm_1234567890abcdef...")
print(f"Key valid: {is_valid}")
print(f"Masked key: {masked_key}")
```

## Framework Examples

### Django Integration

```python
# views.py
from django.http import JsonResponse
from swimmable import SwimmableClient
from django.conf import settings

client = SwimmableClient(api_key=settings.SWIMMABLE_API_KEY)

def beach_conditions(request, lat, lon):
    try:
        conditions = client.get_conditions(lat=float(lat), lon=float(lon))
        return JsonResponse({
            'water_temperature': conditions.water_temperature,
            'air_temperature': conditions.air_temperature,
            'weather': conditions.weather_description,
            'safe_to_swim': conditions.water_temperature > 18  # Basic safety check
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

### Flask API

```python
from flask import Flask, jsonify, request
from swimmable import SwimmableClient
import os

app = Flask(__name__)
client = SwimmableClient(api_key=os.getenv('SWIMMABLE_API_KEY'))

@app.route('/api/conditions')
def get_conditions():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    
    try:
        conditions = client.get_conditions(lat=lat, lon=lon)
        return jsonify({
            'water_temperature': conditions.water_temperature,
            'air_temperature': conditions.air_temperature,
            'weather_description': conditions.weather_description,
            'uv_index': conditions.uv_index,
            'timestamp': conditions.timestamp
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from swimmable import SwimmableClient, SwimmableError
from pydantic import BaseModel
import os

app = FastAPI()
client = SwimmableClient(api_key=os.getenv('SWIMMABLE_API_KEY'))

class LocationQuery(BaseModel):
    lat: float
    lon: float

@app.get("/conditions")
async def get_swimming_conditions(query: LocationQuery):
    try:
        conditions = client.get_conditions(lat=query.lat, lon=query.lon)
        return {
            "water_temperature": conditions.water_temperature,
            "air_temperature": conditions.air_temperature,
            "weather_description": conditions.weather_description,
            "safe_to_swim": conditions.water_temperature > 18,
            "timestamp": conditions.timestamp
        }
    except SwimmableError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Jupyter Notebook Analysis

```python
import matplotlib.pyplot as plt
import pandas as pd
from swimmable import SwimmableClient

client = SwimmableClient()

# Analyze conditions for multiple beaches
beaches = [
    {"name": "Santa Monica", "lat": 34.0195, "lon": -118.4912},
    {"name": "Miami Beach", "lat": 25.7617, "lon": -80.1918},
    {"name": "Waikiki", "lat": 21.2765, "lon": -157.8281},
]

data = []
for beach in beaches:
    conditions = client.get_conditions(beach["lat"], beach["lon"])
    data.append({
        "Beach": beach["name"],
        "Water Temp": conditions.water_temperature,
        "Air Temp": conditions.air_temperature,
        "Wave Height": conditions.wave_height,
        "UV Index": conditions.uv_index
    })

df = pd.DataFrame(data)
print(df)

# Plot water temperatures
plt.figure(figsize=(10, 6))
plt.bar(df["Beach"], df["Water Temp"])
plt.title("Water Temperatures Across Beaches")
plt.ylabel("Temperature (°C)")
plt.show()
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from swimmable import (
    SwimmableClient, 
    SwimmableError, 
    SwimmableAPIError,
    SwimmableTimeoutError,
    SwimmableAuthenticationError,
    SwimmableRateLimitError
)

client = SwimmableClient(api_key="your-key")

try:
    conditions = client.get_conditions(lat=91, lon=0)  # Invalid latitude
except SwimmableAuthenticationError as e:
    print(f"Authentication failed: {e}")
except SwimmableRateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after}s")
except SwimmableTimeoutError as e:
    print(f"Request timed out after {e.timeout}s")
except SwimmableAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
except SwimmableError as e:
    print(f"General error: {e}")
```

## Rate Limiting

The SDK includes built-in rate limiting utilities:

```python
from swimmable.utils import RateLimiter

limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100 requests per minute

def make_safe_request(lat, lon):
    if not limiter.can_make_request():
        reset_time = limiter.get_reset_time()
        raise Exception(f"Rate limit exceeded. Try again in {reset_time:.1f}s")
    
    conditions = client.get_conditions(lat=lat, lon=lon)
    limiter.record_request()
    
    return conditions
```

## Type Hints and IDE Support

The SDK is fully typed and provides excellent IDE support:

```python
from swimmable import SwimmableClient, BasicConditions, EnhancedConditions

client: SwimmableClient = SwimmableClient(api_key="your-key")

# IDE will provide autocompletion and type checking
conditions: BasicConditions = client.get_conditions(34.0522, -118.2437)
enhanced: EnhancedConditions = client.get_enhanced_conditions(34.0522, -118.2437)

# All dataclass fields are typed
water_temp: float = conditions.water_temperature
score: float = enhanced.swimmability_score
location_name: str = enhanced.location.name
```

## Testing

The SDK is designed to be easily testable:

```python
import pytest
from unittest.mock import Mock, patch
from swimmable import SwimmableClient, BasicConditions

def test_get_conditions():
    client = SwimmableClient()
    
    # Mock the API response
    mock_response = {
        'airTemperature': 22.5,
        'waterTemperature': 20.1,
        'weatherDescription': 'sunny',
        'uvIndex': 6.0,
        'windSpeed': 15.2,
        'waveHeight': 1.2,
        'timestamp': '2024-01-15T10:30:00Z'
    }
    
    with patch.object(client, '_make_request', return_value=mock_response):
        conditions = client.get_conditions(34.0522, -118.2437)
        
        assert isinstance(conditions, BasicConditions)
        assert conditions.water_temperature == 20.1
        assert conditions.weather_description == 'sunny'
```

## API Key Management

1. **Get an API Key**: Sign up at [swimmable.app/signup](https://swimmable.app/signup)
2. **Environment Variables**: Store your API key securely
   ```bash
   export SWIMMABLE_API_KEY=your-api-key-here
   ```
3. **Rate Limits**: Free tier includes generous limits, paid plans available
4. **Security**: Never expose API keys in source code or logs

## Development

To contribute to the SDK:

```bash
# Clone the repository
git clone https://github.com/swimmable/python-sdk
cd python-sdk

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/swimmable

# Format code
black src/ tests/
isort src/ tests/
```

## Changelog

### v1.0.0
- Initial release with full API coverage
- Complete type hints and dataclass support
- Comprehensive error handling
- Rate limiting utilities
- Framework integration examples

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

## Support

- 📧 **Email**: [developers@swimmable.app](mailto:developers@swimmable.app)
- 📖 **Documentation**: [swimmable.app/docs](https://swimmable.app/docs)
- 🐛 **Issues**: [GitHub Issues](https://github.com/swimmable/python-sdk/issues)
- 💬 **Community**: [Discord](https://discord.gg/swimmable)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

Built with ❤️ by the [Swimmable](https://swimmable.app) team. Making water activities safer worldwide! 🏊‍♀️🌊