"""
Tests for main.py - Weather Dashboard CLI main module

These tests verify the CLI functionality, argument parsing,
and display functions work correctly.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import (
    create_parser,
    main,
    display_current_weather,
    display_forecast,
    display_favorites,
    interactive_mode,
    show_main_menu,
    show_favorites_menu,
)


class TestArgumentParser:
    """Test cases for the argument parser."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "weather"

    def test_parser_city_argument(self):
        """Test parsing city argument."""
        parser = create_parser()
        args = parser.parse_args(["--city", "London"])
        assert args.city == "London"

    def test_parser_short_city_argument(self):
        """Test parsing short city argument (-c)."""
        parser = create_parser()
        args = parser.parse_args(["-c", "Paris"])
        assert args.city == "Paris"

    def test_parser_forecast_flag(self):
        """Test parsing forecast flag."""
        parser = create_parser()
        args = parser.parse_args(["--city", "Tokyo", "--forecast"])
        assert args.city == "Tokyo"
        assert args.forecast is True

    def test_parser_short_forecast_flag(self):
        """Test parsing short forecast flag (-f)."""
        parser = create_parser()
        args = parser.parse_args(["-c", "Berlin", "-f"])
        assert args.city == "Berlin"
        assert args.forecast is True

    def test_parser_favorites_flag(self):
        """Test parsing favorites flag."""
        parser = create_parser()
        args = parser.parse_args(["--favorites"])
        assert args.favorites is True

    def test_parser_list_favorites_flag(self):
        """Test parsing list-favorites flag."""
        parser = create_parser()
        args = parser.parse_args(["--list-favorites"])
        assert args.list_favorites is True

    def test_parser_add_favorite(self):
        """Test parsing add-favorite argument."""
        parser = create_parser()
        args = parser.parse_args(["--add-favorite", "New York"])
        assert args.add_favorite == "New York"

    def test_parser_remove_favorite(self):
        """Test parsing remove-favorite argument."""
        parser = create_parser()
        args = parser.parse_args(["--remove-favorite", "Chicago"])
        assert args.remove_favorite == "Chicago"

    def test_parser_combined_arguments(self):
        """Test parsing multiple arguments together."""
        parser = create_parser()
        args = parser.parse_args(["-c", "London", "-f"])
        assert args.city == "London"
        assert args.forecast is True


class TestDisplayCurrentWeather:
    """Test cases for display_current_weather function."""

    @patch('main.get_current_weather')
    def test_display_weather_success(self, mock_get_weather):
        """Test successful weather display."""
        mock_get_weather.return_value = {
            "main": {
                "temp": 20.5,
                "feels_like": 19.0,
                "humidity": 65,
            },
            "weather": [{"id": 800, "description": "clear sky"}],
            "wind": {"speed": 3.5},
            "name": "London",
            "sys": {"country": "GB"},
        }
        
        result = display_current_weather("London")
        assert result is True
        mock_get_weather.assert_called_once_with("London")

    @patch('main.get_current_weather')
    def test_display_weather_city_not_found(self, mock_get_weather):
        """Test weather display when city is not found."""
        mock_get_weather.return_value = None
        
        result = display_current_weather("NonExistentCity123")
        assert result is False

    @patch('main.get_current_weather')
    def test_display_weather_with_rain(self, mock_get_weather):
        """Test weather display with rainy conditions."""
        mock_get_weather.return_value = {
            "main": {
                "temp": 15.0,
                "feels_like": 13.5,
                "humidity": 85,
            },
            "weather": [{"id": 501, "description": "moderate rain"}],
            "wind": {"speed": 5.0},
            "name": "Seattle",
            "sys": {"country": "US"},
        }
        
        result = display_current_weather("Seattle")
        assert result is True


class TestDisplayForecast:
    """Test cases for display_forecast function."""

    @patch('main.get_forecast')
    def test_display_forecast_success(self, mock_get_forecast):
        """Test successful forecast display."""
        mock_get_forecast.return_value = {
            "city": {"name": "London", "country": "GB"},
            "list": [
                {
                    "dt_txt": "2024-01-01 12:00:00",
                    "main": {"temp": 10.0, "feels_like": 8.5, "humidity": 70},
                    "weather": [{"id": 802, "description": "scattered clouds"}],
                    "wind": {"speed": 4.0},
                }
                for _ in range(40)  # Simulate 5 days of 3-hourly data
            ],
        }
        
        result = display_forecast("London")
        assert result is True
        mock_get_forecast.assert_called_once_with("London")

    @patch('main.get_forecast')
    def test_display_forecast_city_not_found(self, mock_get_forecast):
        """Test forecast display when city is not found."""
        mock_get_forecast.return_value = None
        
        result = display_forecast("FakeCity999")
        assert result is False


class TestDisplayFavorites:
    """Test cases for display_favorites function."""

    @patch('main.load_favorites')
    def test_display_favorites_empty(self, mock_load):
        """Test displaying empty favorites list."""
        mock_load.return_value = []
        # Should complete without error
        display_favorites()
        mock_load.assert_called_once()

    @patch('main.load_favorites')
    def test_display_favorites_with_cities(self, mock_load):
        """Test displaying favorites with cities."""
        mock_load.return_value = ["London", "Paris", "Tokyo"]
        # Should complete without error
        display_favorites()
        mock_load.assert_called_once()


class TestMainFunction:
    """Test cases for the main entry point."""

    @patch('sys.argv', ['main.py'])
    @patch('main.interactive_mode')
    def test_main_no_arguments(self, mock_interactive):
        """Test main function with no arguments runs interactive mode."""
        mock_interactive.return_value = 0
        result = main()
        assert result == 0
        mock_interactive.assert_called_once()

    @patch('sys.argv', ['main.py', '--list-favorites'])
    @patch('main.display_favorites')
    def test_main_list_favorites(self, mock_display):
        """Test main function with --list-favorites."""
        result = main()
        assert result == 0
        mock_display.assert_called_once()

    @patch('sys.argv', ['main.py', '--add-favorite', 'London'])
    @patch('main.save_favorite')
    def test_main_add_favorite(self, mock_save):
        """Test main function with --add-favorite."""
        mock_save.return_value = True
        result = main()
        assert result == 0
        mock_save.assert_called_once_with('London')

    @patch('sys.argv', ['main.py', '--remove-favorite', 'London'])
    @patch('main.remove_favorite')
    def test_main_remove_favorite(self, mock_remove):
        """Test main function with --remove-favorite."""
        mock_remove.return_value = True
        result = main()
        assert result == 0
        mock_remove.assert_called_once_with('London')

    @patch('sys.argv', ['main.py', '-c', 'London'])
    @patch('main.display_current_weather')
    def test_main_get_weather(self, mock_display):
        """Test main function with city argument."""
        mock_display.return_value = True
        result = main()
        assert result == 0
        mock_display.assert_called_once_with('London')

    @patch('sys.argv', ['main.py', '-c', 'London', '-f'])
    @patch('main.display_forecast')
    def test_main_get_forecast(self, mock_display):
        """Test main function with city and forecast arguments."""
        mock_display.return_value = True
        result = main()
        assert result == 0
        mock_display.assert_called_once_with('London')

    @patch('sys.argv', ['main.py', '--favorites'])
    @patch('main.weather_for_favorites')
    def test_main_weather_for_favorites(self, mock_weather):
        """Test main function with --favorites."""
        result = main()
        assert result == 0
        mock_weather.assert_called_once()


class TestInteractiveMode:
    """Test cases for interactive mode functions."""

    def test_show_main_menu_function_exists(self):
        """Test that show_main_menu function exists."""
        assert callable(show_main_menu)

    def test_show_favorites_menu_function_exists(self):
        """Test that show_favorites_menu function exists."""
        assert callable(show_favorites_menu)

    def test_interactive_mode_function_exists(self):
        """Test that interactive_mode function exists."""
        assert callable(interactive_mode)
