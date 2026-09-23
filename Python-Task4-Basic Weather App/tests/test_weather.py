"""
Comprehensive Automated Unit Test Suite for OASIS Weather Application.
Tests configuration, input validation, meteorological calculations,
payload parsing, forecast aggregation, and exception handling.
"""

import unittest
from datetime import datetime, timezone

import config
from config import deg_to_compass, validate_api_key
from forecast_service import _process_five_day_outlook, _process_upcoming_hours, get_forecast_data
from location_service import get_approximate_location
from weather_cli import fetch_and_print_weather
from weather_service import WeatherServiceError, _build_params, _parse_weather_payload, get_current_weather


class TestConfig(unittest.TestCase):
    def test_deg_to_compass(self):
        """Tests compass direction conversion from degrees."""
        self.assertEqual(deg_to_compass(0), "N")
        self.assertEqual(deg_to_compass(360), "N")
        self.assertEqual(deg_to_compass(90), "E")
        self.assertEqual(deg_to_compass(180), "S")
        self.assertEqual(deg_to_compass(270), "W")
        self.assertEqual(deg_to_compass(45), "NE")
        self.assertEqual(deg_to_compass(135), "SE")
        self.assertEqual(deg_to_compass(225), "SW")
        self.assertEqual(deg_to_compass(315), "NW")
        # Defensive fallback on invalid types
        self.assertEqual(deg_to_compass("invalid"), "N/A")

    def test_validate_api_key(self):
        """Tests validation of OpenWeatherMap API keys."""
        valid, msg = validate_api_key("")
        self.assertFalse(valid)
        self.assertIn("not found", msg.lower())

        valid, msg = validate_api_key("short_key_123")
        self.assertFalse(valid)
        self.assertIn("invalid or incomplete", msg.lower())

        valid, msg = validate_api_key("1234567890abcdef1234567890abcdef")
        self.assertTrue(valid)
        self.assertIn("valid", msg.lower())


class TestWeatherService(unittest.TestCase):
    def test_build_params_city(self):
        """Tests query parameter building for city names."""
        params = _build_params("Hyderabad, IN", "test_key")
        self.assertEqual(params["q"], "Hyderabad, IN")
        self.assertEqual(params["appid"], "test_key")
        self.assertNotIn("zip", params)

    def test_build_params_zip(self):
        """Tests query parameter building for postal/ZIP codes."""
        params = _build_params("94016", "test_key")
        self.assertEqual(params["zip"], "94016")
        self.assertEqual(params["appid"], "test_key")
        self.assertNotIn("q", params)

        params_in = _build_params("500081, IN", "test_key")
        self.assertEqual(params_in["zip"], "500081, IN")

    def test_build_params_coordinates(self):
        """Tests query parameter building for coordinates."""
        params = _build_params("17.3850, 78.4867", "test_key")
        self.assertEqual(params["lat"], "17.385")
        self.assertEqual(params["lon"], "78.4867")
        self.assertEqual(params["appid"], "test_key")

        params_named = _build_params("lat=51.5074,lon=-0.1278", "test_key")
        self.assertEqual(params_named["lat"], "51.5074")
        self.assertEqual(params_named["lon"], "-0.1278")

    def test_empty_query_raises_service_error(self):
        """Tests that empty or whitespace query raises WeatherServiceError."""
        with self.assertRaises(WeatherServiceError) as ctx:
            get_current_weather("")
        self.assertIn("enter a city", str(ctx.exception).lower())

        with self.assertRaises(WeatherServiceError):
            get_current_weather("   ")

    def test_parse_weather_payload(self):
        """Tests parsing of mock OpenWeatherMap Current Weather response."""
        mock_payload = {
            "name": "Hyderabad",
            "sys": {"country": "IN", "sunrise": 1700000000, "sunset": 1700040000},
            "main": {
                "temp": 25.0,
                "feels_like": 26.0,
                "temp_min": 22.0,
                "temp_max": 28.0,
                "humidity": 65,
                "pressure": 1012,
            },
            "weather": [
                {
                    "main": "Clouds",
                    "description": "scattered clouds",
                    "icon": "03d",
                }
            ],
            "wind": {"speed": 4.0, "deg": 90},
            "visibility": 8000,
            "dt": 1700020000,
            "timezone": 19800,
        }

        parsed = _parse_weather_payload(mock_payload)
        self.assertEqual(parsed["city"], "Hyderabad")
        self.assertEqual(parsed["country"], "IN")
        self.assertEqual(parsed["location_display"], "Hyderabad, IN")
        self.assertEqual(parsed["temp_c"], 25.0)
        self.assertEqual(parsed["temp_f"], 77.0)  # (25 * 9/5) + 32 = 77
        self.assertEqual(parsed["feels_like_c"], 26.0)
        self.assertEqual(parsed["feels_like_f"], 78.8)
        self.assertEqual(parsed["condition"], "Clouds")
        self.assertEqual(parsed["description"], "Scattered Clouds")
        self.assertEqual(parsed["icon_code"], "03d")
        self.assertEqual(parsed["humidity"], 65)
        self.assertEqual(parsed["pressure"], 1012)
        self.assertEqual(parsed["wind_speed_ms"], 4.0)
        self.assertEqual(parsed["wind_dir"], "E")
        self.assertEqual(parsed["visibility_km"], 8.0)
        self.assertIn("sunrise_time", parsed)
        self.assertIn("sunset_time", parsed)
        self.assertIn("local_time", parsed)


class TestForecastService(unittest.TestCase):
    def test_empty_forecast_query_raises(self):
        """Tests that empty query raises WeatherServiceError."""
        with self.assertRaises(WeatherServiceError):
            get_forecast_data("")

    def test_process_upcoming_hours(self):
        """Tests processing of upcoming hourly intervals."""
        mock_items = [
            {
                "dt": 1700020000 + (i * 10800),
                "main": {"temp": 20.0 + i, "humidity": 60 + i},
                "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
                "pop": 0.1 * i,
            }
            for i in range(6)
        ]
        hourly = _process_upcoming_hours(mock_items, 0)
        self.assertLessEqual(len(hourly), 5)
        first = hourly[0]
        self.assertIn("time", first)
        self.assertIn("time_label", first)
        self.assertIn("temp_c", first)
        self.assertIn("temp_f", first)
        self.assertIn("condition", first)
        self.assertIn("pop", first)
        self.assertEqual(first["condition"], "Clear")

    def test_process_five_day_outlook(self):
        """Tests aggregation into 5 daily outlook records."""
        # 40 items across 5 days (8 slots per day)
        mock_items = []
        base_epoch = 1700000000
        for day in range(5):
            for slot in range(8):
                epoch = base_epoch + (day * 86400) + (slot * 10800)
                mock_items.append({
                    "dt": epoch,
                    "main": {"temp": 15.0 + day + slot, "humidity": 50},
                    "weather": [{"main": "Clouds", "description": "few clouds", "icon": "02d"}],
                })

        daily = _process_five_day_outlook(mock_items, 0)
        self.assertEqual(len(daily), 5)
        for day_entry in daily:
            self.assertIn("day_name", day_entry)
            self.assertIn("date_str", day_entry)
            self.assertIn("temp_min_c", day_entry)
            self.assertIn("temp_max_c", day_entry)
            self.assertIn("temp_min_f", day_entry)
            self.assertIn("temp_max_f", day_entry)
            self.assertIn("condition", day_entry)


class TestLocationService(unittest.TestCase):
    def test_location_service_returns_tuple(self):
        """Tests that get_approximate_location returns (query, message) safely."""
        query, message = get_approximate_location()
        self.assertTrue(query is None or isinstance(query, str))
        self.assertIsInstance(message, str)


class TestWeatherCLI(unittest.TestCase):
    def test_empty_input_validation(self):
        """Tests that CLI rejects empty input gracefully returning False."""
        self.assertFalse(fetch_and_print_weather(""))
        self.assertFalse(fetch_and_print_weather("    "))


if __name__ == "__main__":
    unittest.main()
