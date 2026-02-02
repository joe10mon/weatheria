from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)

# Enable CORS to allow frontend to communicate with backend
# Allow all origins for development (restrict in production)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration - Open-Meteo API (FREE, no API key needed!)
OPENMETEO_BASE_URL = 'https://api.open-meteo.com/v1/forecast'
GEOCODING_API_URL = 'https://geocoding-api.open-meteo.com/v1/search'

@app.route('/')
def home():
    """Home endpoint - API information"""
    return jsonify({
        'service': 'Weather Microservice',
        'version': '2.0',
        'api': 'Open-Meteo (Free)',
        'status': 'running',
        'endpoints': {
            '/api/weather': 'GET - Fetch weather data for a city',
            '/api/health': 'GET - Health check endpoint'
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'weather-service',
        'api': 'open-meteo',
        'version': '2.0'
    })

def get_city_coordinates(city_name):
    """
    Convert city name to latitude/longitude using Open-Meteo Geocoding API
    """
    try:
        params = {
            'name': city_name,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        print(f"  → Geocoding: {city_name}")
        response = requests.get(GEOCODING_API_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"  ✗ Geocoding failed with status: {response.status_code}")
            return None
        
        data = response.json()
        
        if 'results' not in data or len(data['results']) == 0:
            print(f"  ✗ City not found in geocoding database")
            return None
        
        location = data['results'][0]
        print(f"  ✓ Found: {location['name']}, {location.get('country', 'Unknown')}")
        print(f"  ✓ Coordinates: {location['latitude']}, {location['longitude']}")
        
        return {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'city': location['name'],
            'country': location.get('country', 'Unknown'),
            'admin1': location.get('admin1', '')
        }
    
    except requests.exceptions.Timeout:
        print(f"  ✗ Geocoding timeout")
        return None
    except Exception as e:
        print(f"  ✗ Geocoding error: {str(e)}")
        return None

@app.route('/api/weather', methods=['GET', 'OPTIONS'])
def get_weather():
    """
    REST API endpoint to fetch weather data
    Query Parameters:
        - city: Name of the city (required)
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get city from query parameters
        city = request.args.get('city')
        
        if not city:
            print("✗ No city parameter provided")
            return jsonify({'error': 'City parameter is required'}), 400
        
        print(f"\n{'='*60}")
        print(f"🌤️  Weather Request for: {city}")
        print(f"{'='*60}")
        
        # Step 1: Convert city name to coordinates
        location = get_city_coordinates(city)
        
        if not location:
            print(f"✗ City '{city}' not found")
            return jsonify({'error': f'City "{city}" not found'}), 404
        
        # Step 2: Fetch weather data from Open-Meteo API
        params = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,pressure_msl',
            'timezone': 'auto'
        }
        
        print(f"  → Fetching weather data...")
        response = requests.get(OPENMETEO_BASE_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"  ✗ Open-Meteo API returned status: {response.status_code}")
            return jsonify({'error': 'Failed to fetch weather data from Open-Meteo API'}), 500
        
        # Parse response from Open-Meteo
        weather_data = response.json()
        current = weather_data.get('current', {})
        
        if not current:
            print(f"  ✗ No current weather data available")
            return jsonify({'error': 'No weather data available'}), 500
        
        # Weather code descriptions (WMO Weather interpretation codes)
        weather_descriptions = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Foggy',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            71: 'Slight snow',
            73: 'Moderate snow',
            75: 'Heavy snow',
            77: 'Snow grains',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            85: 'Slight snow showers',
            86: 'Heavy snow showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail'
        }
        
        weather_code = current.get('weather_code', 0)
        description = weather_descriptions.get(weather_code, 'Unknown')
        
        # Transform data to our API format (matching frontend expectations)
        formatted_data = {
            'city': location['city'],
            'country': location['country'],
            'admin1': location['admin1'],
            'temperature': round(current.get('temperature_2m', 0), 1),
            'feels_like': round(current.get('apparent_temperature', 0), 1),
            'humidity': current.get('relative_humidity_2m', 0),
            'pressure': round(current.get('pressure_msl', 0), 0),
            'wind_speed': round(current.get('wind_speed_10m', 0), 1),
            'precipitation': current.get('precipitation', 0),
            'description': description,
            'weather_code': weather_code,
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"  ✓ Weather data retrieved successfully!")
        print(f"  ✓ Temperature: {formatted_data['temperature']}°C")
        print(f"  ✓ Condition: {formatted_data['description']}")
        print(f"{'='*60}\n")
        
        return jsonify(formatted_data), 200
        
    except requests.exceptions.Timeout:
        print("✗ Request timeout")
        return jsonify({'error': 'Request to weather service timed out'}), 504
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {str(e)}")
        return jsonify({'error': 'Failed to connect to weather service'}), 503
    
    except KeyError as e:
        print(f"✗ Missing data field: {str(e)}")
        return jsonify({'error': 'Invalid data received from weather service'}), 500
    
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Add after_request handler for CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌤️  Weather Microservice Starting...")
    print("=" * 60)
    print("📡 API: Open-Meteo (FREE - No API Key Required!)")
    print("🔧 CORS: Enabled for all origins")
    print("\n📍 Endpoints available:")
    print("   • http://localhost:5000/")
    print("   • http://localhost:5000/api/health")
    print("   • http://localhost:5000/api/weather?city=London")
    print("   • http://localhost:5000/api/weather?city=Mumbai")
    print("   • http://localhost:5000/api/weather?city=Tokyo")
    print("\n💡 Test in browser:")
    print("   http://localhost:5000/api/weather?city=London")
    print("=" * 60 + "\n")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)

# Enable CORS to allow frontend to communicate with backend
# Allow all origins for development (restrict in production)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration - Open-Meteo API (FREE, no API key needed!)
OPENMETEO_BASE_URL = 'https://api.open-meteo.com/v1/forecast'
GEOCODING_API_URL = 'https://geocoding-api.open-meteo.com/v1/search'

@app.route('/')
def home():
    """Home endpoint - API information"""
    return jsonify({
        'service': 'Weather Microservice',
        'version': '2.0',
        'api': 'Open-Meteo (Free)',
        'status': 'running',
        'endpoints': {
            '/api/weather': 'GET - Fetch weather data for a city',
            '/api/health': 'GET - Health check endpoint'
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'weather-service',
        'api': 'open-meteo',
        'version': '2.0'
    })

def get_city_coordinates(city_name):
    """
    Convert city name to latitude/longitude using Open-Meteo Geocoding API
    """
    try:
        params = {
            'name': city_name,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        print(f"  → Geocoding: {city_name}")
        response = requests.get(GEOCODING_API_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"  ✗ Geocoding failed with status: {response.status_code}")
            return None
        
        data = response.json()
        
        if 'results' not in data or len(data['results']) == 0:
            print(f"  ✗ City not found in geocoding database")
            return None
        
        location = data['results'][0]
        print(f"  ✓ Found: {location['name']}, {location.get('country', 'Unknown')}")
        print(f"  ✓ Coordinates: {location['latitude']}, {location['longitude']}")
        
        return {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'city': location['name'],
            'country': location.get('country', 'Unknown'),
            'admin1': location.get('admin1', '')
        }
    
    except requests.exceptions.Timeout:
        print(f"  ✗ Geocoding timeout")
        return None
    except Exception as e:
        print(f"  ✗ Geocoding error: {str(e)}")
        return None

@app.route('/api/weather', methods=['GET', 'OPTIONS'])
def get_weather():
    """
    REST API endpoint to fetch weather data
    Query Parameters:
        - city: Name of the city (required)
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get city from query parameters
        city = request.args.get('city')
        
        if not city:
            print("✗ No city parameter provided")
            return jsonify({'error': 'City parameter is required'}), 400
        
        print(f"\n{'='*60}")
        print(f"🌤️  Weather Request for: {city}")
        print(f"{'='*60}")
        
        # Step 1: Convert city name to coordinates
        location = get_city_coordinates(city)
        
        if not location:
            print(f"✗ City '{city}' not found")
            return jsonify({'error': f'City "{city}" not found'}), 404
        
        # Step 2: Fetch weather data from Open-Meteo API
        params = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,pressure_msl',
            'timezone': 'auto'
        }
        
        print(f"  → Fetching weather data...")
        response = requests.get(OPENMETEO_BASE_URL, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"  ✗ Open-Meteo API returned status: {response.status_code}")
            return jsonify({'error': 'Failed to fetch weather data from Open-Meteo API'}), 500
        
        # Parse response from Open-Meteo
        weather_data = response.json()
        current = weather_data.get('current', {})
        
        if not current:
            print(f"  ✗ No current weather data available")
            return jsonify({'error': 'No weather data available'}), 500
        
        # Weather code descriptions (WMO Weather interpretation codes)
        weather_descriptions = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Foggy',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            71: 'Slight snow',
            73: 'Moderate snow',
            75: 'Heavy snow',
            77: 'Snow grains',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            85: 'Slight snow showers',
            86: 'Heavy snow showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with slight hail',
            99: 'Thunderstorm with heavy hail'
        }
        
        weather_code = current.get('weather_code', 0)
        description = weather_descriptions.get(weather_code, 'Unknown')
        
        # Transform data to our API format (matching frontend expectations)
        formatted_data = {
            'city': location['city'],
            'country': location['country'],
            'admin1': location['admin1'],
            'temperature': round(current.get('temperature_2m', 0), 1),
            'feels_like': round(current.get('apparent_temperature', 0), 1),
            'humidity': current.get('relative_humidity_2m', 0),
            'pressure': round(current.get('pressure_msl', 0), 0),
            'wind_speed': round(current.get('wind_speed_10m', 0), 1),
            'precipitation': current.get('precipitation', 0),
            'description': description,
            'weather_code': weather_code,
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"  ✓ Weather data retrieved successfully!")
        print(f"  ✓ Temperature: {formatted_data['temperature']}°C")
        print(f"  ✓ Condition: {formatted_data['description']}")
        print(f"{'='*60}\n")
        
        return jsonify(formatted_data), 200
        
    except requests.exceptions.Timeout:
        print("✗ Request timeout")
        return jsonify({'error': 'Request to weather service timed out'}), 504
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {str(e)}")
        return jsonify({'error': 'Failed to connect to weather service'}), 503
    
    except KeyError as e:
        print(f"✗ Missing data field: {str(e)}")
        return jsonify({'error': 'Invalid data received from weather service'}), 500
    
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Add after_request handler for CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🌤️  Weather Microservice Starting...")
    print("=" * 60)
    print("📡 API: Open-Meteo (FREE - No API Key Required!)")
    print("🔧 CORS: Enabled for all origins")
    print("\n📍 Endpoints available:")
    print("   • http://localhost:5000/")
    print("   • http://localhost:5000/api/health")
    print("   • http://localhost:5000/api/weather?city=London")
    print("   • http://localhost:5000/api/weather?city=Mumbai")
    print("   • http://localhost:5000/api/weather?city=Tokyo")
    print("\n💡 Test in browser:")
    print("   http://localhost:5000/api/weather?city=London")
    print("=" * 60 + "\n")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)