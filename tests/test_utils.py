"""
Tests for utils.py - Weather Dashboard CLI utility functions

These tests verify the helper functions for API calls, data persistence,
and formatting work correctly.
"""

import pytest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import (
    format_temperature,
    celsius_to_fahrenheit,
    fahrenheit_to_celsius,
    get_weather_emoji,
    validate_city_name,
    load_favorites,
    save_favorites,
    save_favorite,
    remove_favorite,
    get_api_key,
    get_current_weather,
    get_forecast,
)


class TestTemperatureFormatting:
    """Test cases for temperature formatting functions."""

    def test_format_temperature_positive(self):
        """Test formatting positive temperature."""
        result = format_temperature(25.5)
        assert result == "25.5°C"

    def test_format_temperature_negative(self):
        """Test formatting negative temperature."""
        result = format_temperature(-10.3)
        assert result == "-10.3°C"

    def test_format_temperature_zero(self):
        """Test formatting zero temperature."""
        result = format_temperature(0.0)
        assert result == "0.0°C"

    def test_format_temperature_rounding(self):
        """Test that temperature is rounded to 1 decimal place."""
        result = format_temperature(23.456)
        assert result == "23.5°C"


class TestTemperatureConversion:
    """Test cases for temperature conversion functions."""

    def test_celsius_to_fahrenheit_freezing(self):
        """Test conversion at freezing point."""
        result = celsius_to_fahrenheit(0)
        assert result == 32.0

    def test_celsius_to_fahrenheit_boiling(self):
        """Test conversion at boiling point."""
        result = celsius_to_fahrenheit(100)
        assert result == 212.0

    def test_celsius_to_fahrenheit_body_temp(self):
        """Test conversion at body temperature."""
        result = celsius_to_fahrenheit(37)
        assert abs(result - 98.6) < 0.1

    def test_fahrenheit_to_celsius_freezing(self):
        """Test conversion at freezing point."""
        result = fahrenheit_to_celsius(32)
        assert result == 0.0

    def test_fahrenheit_to_celsius_boiling(self):
        """Test conversion at boiling point."""
        result = fahrenheit_to_celsius(212)
        assert result == 100.0

    def test_fahrenheit_to_celsius_negative(self):
        """Test conversion with negative Fahrenheit."""
        result = fahrenheit_to_celsius(-40)
        assert result == -40.0  # -40 is same in both scales

    def test_conversion_round_trip(self):
        """Test that converting back and forth gives same value."""
        original = 25.0
        fahrenheit = celsius_to_fahrenheit(original)
        back_to_celsius = fahrenheit_to_celsius(fahrenheit)
        assert abs(back_to_celsius - original) < 0.01


class TestWeatherEmoji:
    """Test cases for weather emoji function."""

    def test_emoji_thunderstorm(self):
        """Test emoji for thunderstorm conditions."""
        assert get_weather_emoji(200) == "⛈️"
        assert get_weather_emoji(250) == "⛈️"
        assert get_weather_emoji(299) == "⛈️"

    def test_emoji_drizzle(self):
        """Test emoji for drizzle conditions."""
        assert get_weather_emoji(300) == "🌧️"
        assert get_weather_emoji(350) == "🌧️"

    def test_emoji_rain(self):
        """Test emoji for rain conditions."""
        assert get_weather_emoji(500) == "🌧️"
        assert get_weather_emoji(501) == "🌧️"

    def test_emoji_freezing_rain(self):
        """Test emoji for freezing rain."""
        assert get_weather_emoji(511) == "🌨️"

    def test_emoji_snow(self):
        """Test emoji for snow conditions."""
        assert get_weather_emoji(600) == "❄️"
        assert get_weather_emoji(650) == "❄️"

    def test_emoji_fog(self):
        """Test emoji for fog/mist conditions."""
        assert get_weather_emoji(700) == "🌫️"
        assert get_weather_emoji(741) == "🌫️"

    def test_emoji_clear(self):
        """Test emoji for clear sky."""
        assert get_weather_emoji(800) == "☀️"

    def test_emoji_few_clouds(self):
        """Test emoji for few clouds."""
        assert get_weather_emoji(801) == "🌤️"

    def test_emoji_scattered_clouds(self):
        """Test emoji for scattered clouds."""
        assert get_weather_emoji(802) == "⛅"

    def test_emoji_overcast_clouds(self):
        """Test emoji for overcast clouds."""
        assert get_weather_emoji(803) == "☁️"
        assert get_weather_emoji(804) == "☁️"

    def test_emoji_unknown(self):
        """Test emoji for unknown weather code."""
        assert get_weather_emoji(999) == "🌡️"


class TestCityNameValidation:
    """Test cases for city name validation."""

    def test_validate_valid_city(self):
        """Test validation with valid city names."""
        assert validate_city_name("London") is True
        assert validate_city_name("New York") is True
        assert validate_city_name("São Paulo") is True

    def test_validate_empty_string(self):
        """Test validation with empty string."""
        assert validate_city_name("") is False

    def test_validate_whitespace_only(self):
        """Test validation with whitespace only."""
        assert validate_city_name("   ") is False

    def test_validate_single_char(self):
        """Test validation with single character."""
        assert validate_city_name("A") is False

    def test_validate_two_chars(self):
        """Test validation with two characters (minimum)."""
        assert validate_city_name("LA") is True

    def test_validate_too_long(self):
        """Test validation with overly long name."""
        long_name = "A" * 101
        assert validate_city_name(long_name) is False

    def test_validate_with_spaces(self):
        """Test validation with leading/trailing spaces."""
        assert validate_city_name("  London  ") is True


class TestFavoritesManagement:
    """Test cases for favorites file management."""

    @pytest.fixture
    def temp_favorites_file(self, tmp_path):
        """Create a temporary favorites file for testing."""
        favorites_file = tmp_path / "favorites.json"
        return favorites_file

    def test_load_favorites_empty_file(self, tmp_path, monkeypatch):
        """Test loading favorites from non-existent file."""
        fake_path = tmp_path / "nonexistent.json"
        monkeypatch.setattr('utils.FAVORITES_FILE', fake_path)
        
        result = load_favorites()
        assert result == []

    def test_load_favorites_with_data(self, tmp_path, monkeypatch):
        """Test loading favorites with existing data."""
        favorites_file = tmp_path / "favorites.json"
        favorites_file.write_text('{"favorites": ["London", "Paris"]}')
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = load_favorites()
        assert result == ["London", "Paris"]

    def test_load_favorites_invalid_json(self, tmp_path, monkeypatch):
        """Test loading favorites from corrupted file."""
        favorites_file = tmp_path / "favorites.json"
        favorites_file.write_text('not valid json')
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = load_favorites()
        assert result == []

    def test_save_favorites(self, tmp_path, monkeypatch):
        """Test saving favorites to file."""
        favorites_file = tmp_path / "favorites.json"
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = save_favorites(["Tokyo", "Berlin"])
        assert result is True
        
        # Verify file contents
        data = json.loads(favorites_file.read_text())
        assert data["favorites"] == ["Tokyo", "Berlin"]

    def test_save_favorite_new_city(self, tmp_path, monkeypatch):
        """Test adding a new favorite city."""
        favorites_file = tmp_path / "favorites.json"
        favorites_file.write_text('{"favorites": ["London"]}')
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = save_favorite("Paris")
        assert result is True
        
        # Verify file contents
        data = json.loads(favorites_file.read_text())
        assert "Paris" in data["favorites"]
        assert "London" in data["favorites"]

    def test_save_favorite_duplicate(self, tmp_path, monkeypatch):
        """Test adding a duplicate favorite city."""
        favorites_file = tmp_path / "favorites.json"
        favorites_file.write_text('{"favorites": ["London"]}')
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = save_favorite("London")
        assert result is False

    def test_save_favorite_case_insensitive(self, tmp_path, monkeypatch):
        """Test that duplicate check is case-insensitive."""
        favorites_file = tmp_path / "favorites.json"
        favorites_file.write_text('{"favorites": ["London"]}')
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = save_favorite("LONDON")
        assert result is False

    def test_remove_favorite_existing(self, tmp_path, monkeypatch):
        """Test removing an existing favorite city."""
        favorites_file = tmp_path / "favorites.json"
        favorites_file.write_text('{"favorites": ["London", "Paris"]}')
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = remove_favorite("London")
        assert result is True
        
        # Verify file contents
        data = json.loads(favorites_file.read_text())
        assert "London" not in data["favorites"]
        assert "Paris" in data["favorites"]

    def test_remove_favorite_not_found(self, tmp_path, monkeypatch):
        """Test removing a non-existent favorite city."""
        favorites_file = tmp_path / "favorites.json"
        favorites_file.write_text('{"favorites": ["London"]}')
        monkeypatch.setattr('utils.FAVORITES_FILE', favorites_file)
        
        result = remove_favorite("Tokyo")
        assert result is False


class TestApiKey:
    """Test cases for API key handling."""

    def test_get_api_key_not_set(self, monkeypatch):
        """Test getting API key when not set."""
        monkeypatch.setattr('utils.API_KEY', '')
        
        with pytest.raises(ValueError) as exc_info:
            get_api_key()
        
        assert "API key not found" in str(exc_info.value)

    def test_get_api_key_set(self, monkeypatch):
        """Test getting API key when properly set."""
        monkeypatch.setattr('utils.API_KEY', 'test_api_key_123')
        
        result = get_api_key()
        assert result == 'test_api_key_123'


class TestApiCalls:
    """Test cases for API call functions."""

    @patch('utils.requests.get')
    def test_get_current_weather_success(self, mock_get, monkeypatch):
        """Test successful weather API call."""
        monkeypatch.setattr('utils.API_KEY', 'test_key')
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"main": {"temp": 20}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = get_current_weather("London")
        assert result == {"main": {"temp": 20}}

    @patch('utils.requests.get')
    def test_get_current_weather_no_api_key(self, mock_get, monkeypatch):
        """Test weather API call without API key."""
        monkeypatch.setattr('utils.API_KEY', '')
        
        result = get_current_weather("London")
        assert result is None
        mock_get.assert_not_called()

    @patch('utils.requests.get')
    def test_get_forecast_success(self, mock_get, monkeypatch):
        """Test successful forecast API call."""
        monkeypatch.setattr('utils.API_KEY', 'test_key')
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"city": {"name": "London"}, "list": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = get_forecast("London")
        assert result["city"]["name"] == "London"

    @patch('utils.requests.get')
    def test_get_weather_connection_error(self, mock_get, monkeypatch):
        """Test weather API call with connection error."""
        monkeypatch.setattr('utils.API_KEY', 'test_key')
        
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = get_current_weather("London")
        assert result is None

    @patch('utils.requests.get')
    def test_get_weather_timeout(self, mock_get, monkeypatch):
        """Test weather API call with timeout."""
        monkeypatch.setattr('utils.API_KEY', 'test_key')
        
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = get_current_weather("London")
        assert result is None
