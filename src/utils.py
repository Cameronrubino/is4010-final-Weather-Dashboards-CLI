"""
Weather Dashboard CLI - Utility Functions

This module contains helper functions for API calls, data persistence,
and formatting for the Weather Dashboard CLI.
"""

import os
import json
from typing import Optional
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"
FAVORITES_FILE = Path(__file__).parent.parent / "favorites.json"


def get_api_key() -> str:
    """
    Get the OpenWeatherMap API key from environment variables.
    
    Returns:
        The API key string
        
    Raises:
        ValueError: If API key is not set
    """
    if not API_KEY:
        raise ValueError(
            "OpenWeatherMap API key not found. "
            "Please set OPENWEATHERMAP_API_KEY in your .env file."
        )
    return API_KEY


def get_current_weather(city: str) -> Optional[dict]:
    """
    Fetch current weather data for a city from OpenWeatherMap API.
    
    Args:
        city: Name of the city (e.g., "London" or "New York,US")
        
    Returns:
        Dictionary containing weather data, or None if request failed
    """
    try:
        api_key = get_api_key()
    except ValueError:
        return None
    
    url = f"{BASE_URL}/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial",  # Use Fahrenheit for US users
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return None  # City not found
        print(f"HTTP Error: {e}")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not reach the weather service.")
        return None
    except requests.exceptions.Timeout:
        print("Timeout: The weather service took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


def get_forecast(city: str) -> Optional[dict]:
    """
    Fetch 5-day weather forecast for a city from OpenWeatherMap API.
    
    Args:
        city: Name of the city (e.g., "London" or "New York,US")
        
    Returns:
        Dictionary containing forecast data, or None if request failed
    """
    try:
        api_key = get_api_key()
    except ValueError:
        return None
    
    url = f"{BASE_URL}/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "imperial",  # Use Fahrenheit for US users
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not reach the weather service.")
        return None
    except requests.exceptions.Timeout:
        print("Timeout: The weather service took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None


def load_favorites() -> list:
    """
    Load favorite cities from the JSON file.
    
    Returns:
        List of favorite city names
    """
    if not FAVORITES_FILE.exists():
        return []
    
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("favorites", [])
    except (json.JSONDecodeError, IOError):
        return []


def save_favorites(favorites: list) -> bool:
    """
    Save favorite cities to the JSON file.
    
    Args:
        favorites: List of city names to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump({"favorites": favorites}, f, indent=2)
        return True
    except IOError:
        return False


def save_favorite(city: str) -> bool:
    """
    Add a city to the favorites list.
    
    Args:
        city: Name of the city to add
        
    Returns:
        True if city was added, False if already exists
    """
    favorites = load_favorites()
    
    # Normalize city name for comparison
    city_normalized = city.strip().title()
    
    # Check if already in favorites (case-insensitive)
    if any(fav.lower() == city_normalized.lower() for fav in favorites):
        return False
    
    favorites.append(city_normalized)
    save_favorites(favorites)
    return True


def remove_favorite(city: str) -> bool:
    """
    Remove a city from the favorites list.
    
    Args:
        city: Name of the city to remove
        
    Returns:
        True if city was removed, False if not found
    """
    favorites = load_favorites()
    city_lower = city.strip().lower()
    
    # Find and remove (case-insensitive)
    for i, fav in enumerate(favorites):
        if fav.lower() == city_lower:
            favorites.pop(i)
            save_favorites(favorites)
            return True
    
    return False


def format_temperature(temp: float) -> str:
    """
    Format temperature value for display.
    
    Args:
        temp: Temperature in Fahrenheit
        
    Returns:
        Formatted temperature string with unit
    """
    return f"{temp:.1f}°F"


def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit.
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Temperature in Fahrenheit
    """
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Convert Fahrenheit to Celsius.
    
    Args:
        fahrenheit: Temperature in Fahrenheit
        
    Returns:
        Temperature in Celsius
    """
    return (fahrenheit - 32) * 5 / 9


def get_weather_emoji(weather_id: int) -> str:
    """
    Get an appropriate emoji for a weather condition ID.
    
    Weather condition codes: https://openweathermap.org/weather-conditions
    
    Args:
        weather_id: OpenWeatherMap weather condition ID
        
    Returns:
        Emoji string representing the weather condition
    """
    # Thunderstorm (2xx)
    if 200 <= weather_id < 300:
        return "⛈️"
    # Drizzle (3xx)
    elif 300 <= weather_id < 400:
        return "🌧️"
    # Rain (5xx)
    elif 500 <= weather_id < 600:
        if weather_id == 511:  # Freezing rain
            return "🌨️"
        return "🌧️"
    # Snow (6xx)
    elif 600 <= weather_id < 700:
        return "❄️"
    # Atmosphere (7xx) - fog, mist, etc.
    elif 700 <= weather_id < 800:
        return "🌫️"
    # Clear (800)
    elif weather_id == 800:
        return "☀️"
    # Clouds (80x)
    elif 801 <= weather_id < 810:
        if weather_id == 801:  # Few clouds
            return "🌤️"
        elif weather_id == 802:  # Scattered clouds
            return "⛅"
        else:  # Broken/overcast clouds
            return "☁️"
    else:
        return "🌡️"


def validate_city_name(city: str) -> bool:
    """
    Validate that a city name is reasonable.
    
    Args:
        city: City name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not city or not city.strip():
        return False
    
    # City name should be at least 2 characters
    if len(city.strip()) < 2:
        return False
    
    # City name shouldn't be too long
    if len(city.strip()) > 100:
        return False
    
    return True
