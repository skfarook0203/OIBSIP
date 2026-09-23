"""
Weather Service Module for OASIS Infobyte Weather Application.
Executes OpenWeatherMap Current Weather API requests, validates inputs,
handles network & API exceptions, and parses JSON responses into clean data structures.
"""

import json
from datetime import datetime, timezone
import urllib.request
import urllib.parse
import urllib.error
import socket

from config import (
    CURRENT_WEATHER_URL,
    DEFAULT_TIMEOUT,
    OPENWEATHER_API_KEY,
    deg_to_compass,
)


class WeatherServiceError(Exception):
    """Custom exception class for weather service errors."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _is_coordinates(query: str) -> tuple[float, float] | None:
    """Parses latitude and longitude coordinates if present in query."""
    cleaned = query.strip()
    # Support "lat=17.385,lon=78.4867"
    if "lat=" in cleaned.lower() and "lon=" in cleaned.lower():
        try:
            parts = cleaned.replace(";", "&").split("&") if "&" in cleaned else cleaned.split(",")
            lat, lon = None, None
            for p in parts:
                if "=" in p:
                    k, v = p.split("=", 1)
                    k_str = k.strip().lower()
                    if k_str == "lat":
                        lat = float(v.strip())
                    elif k_str in ("lon", "lng"):
                        lon = float(v.strip())
            if lat is not None and lon is not None and -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                return lat, lon
        except Exception:
            pass

    # Support "17.3850, 78.4867" or "17.3850,78.4867"
    if "," in cleaned:
        parts = [p.strip() for p in cleaned.split(",")]
        if len(parts) == 2:
            try:
                lat = float(parts[0])
                lon = float(parts[1])
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    return lat, lon
            except ValueError:
                pass
    return None


def _build_params(query: str, api_key: str) -> dict:
    """Builds the query parameters distinguishing coordinates, city names, and postal codes."""
    cleaned = query.strip()
    
    # 1. Check if query matches geographic coordinates
    coords = _is_coordinates(cleaned)
    if coords:
        return {"lat": str(coords[0]), "lon": str(coords[1]), "appid": api_key}

    # 2. Check if query matches ZIP code format: e.g. "94016", "94016,US", "500081,IN"
    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    if parts and parts[0].isdigit():
        zip_param = cleaned
        return {"zip": zip_param, "appid": api_key}
    
    # 3. Default to city name query
    return {"q": cleaned, "appid": api_key}


def get_current_weather(query: str, api_key: str | None = None) -> dict:
    """
    Fetches and parses current weather data from OpenWeatherMap.
    Returns a unified dictionary containing metric and imperial measurements.
    
    Raises WeatherServiceError with clear user-facing messages on failure.
    """
    if not query or not query.strip():
        raise WeatherServiceError("Please enter a city name or ZIP/postal code.")

    active_key = (api_key or OPENWEATHER_API_KEY).strip()
    if not active_key:
        raise WeatherServiceError(
            "Weather service API key is missing. Please configure OPENWEATHER_API_KEY in your .env file."
        )

    params = _build_params(query, active_key)
    # Always query in standard metric units and compute imperial conversions locally
    # to allow instant unit toggling without additional network round-trips.
    params["units"] = "metric"

    url = f"{CURRENT_WEATHER_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherApp/2.0"})

    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            status_code = resp.status
            raw_body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8") if exc.fp else ""
        if exc.code == 401:
            raise WeatherServiceError(
                "Invalid API key: Unauthorized access. Please check your OPENWEATHER_API_KEY in .env.\n"
                "(Note: Newly registered keys can take 15–30 minutes to activate).",
                status_code=401,
            )
        elif exc.code == 404:
            raise WeatherServiceError(
                f"Location not found: Unable to locate '{query.strip()}'.\n"
                "Please check the spelling or format (e.g., 'London, UK' or '94016, US').",
                status_code=404,
            )
        elif exc.code == 429:
            raise WeatherServiceError(
                "API rate limit exceeded. You have made too many requests in a short period.\n"
                "Please wait a moment before trying again.",
                status_code=429,
            )
        else:
            try:
                err_data = json.loads(raw_body)
                api_msg = err_data.get("message", "Unknown error")
            except Exception:
                api_msg = raw_body or "Unknown error"
            raise WeatherServiceError(
                f"Weather API Error ({exc.code}): {api_msg.capitalize()}",
                status_code=exc.code,
            )
    except (socket.timeout, urllib.error.URLError) as exc:
        if isinstance(exc, socket.timeout) or (isinstance(exc, urllib.error.URLError) and isinstance(exc.reason, socket.timeout)):
            raise WeatherServiceError(
                "Network timeout: The weather service took too long to respond. "
                "Please check your internet connection."
            )
        raise WeatherServiceError(
            "Network connection failure: Unable to reach weather service. "
            "Please check your network and DNS settings."
        )
    except Exception as exc:
        raise WeatherServiceError(f"Network request error: {str(exc)}")

    # Parse JSON Response
    try:
        data = json.loads(raw_body)
    except (ValueError, json.JSONDecodeError):
        raise WeatherServiceError("Invalid JSON response received from weather service.")

    return _parse_weather_payload(data)


def _parse_weather_payload(data: dict) -> dict:
    """Safely extracts and formats fields from the OpenWeatherMap JSON payload."""
    main = data.get("main", {})
    weather_list = data.get("weather", [{}])
    weather = weather_list[0] if weather_list else {}
    wind = data.get("wind", {})
    sys = data.get("sys", {})

    city_name = data.get("name", "Unknown Location")
    country = sys.get("country", "")
    full_location = f"{city_name}, {country}" if country else city_name

    # Metric Temperatures
    temp_c = float(main.get("temp", 0.0))
    feels_like_c = float(main.get("feels_like", temp_c))
    temp_min_c = float(main.get("temp_min", temp_c))
    temp_max_c = float(main.get("temp_max", temp_c))

    # Imperial Conversions: F = (C * 9/5) + 32
    temp_f = (temp_c * 9.0 / 5.0) + 32.0
    feels_like_f = (feels_like_c * 9.0 / 5.0) + 32.0
    temp_min_f = (temp_min_c * 9.0 / 5.0) + 32.0
    temp_max_f = (temp_max_c * 9.0 / 5.0) + 32.0

    # Wind speed: m/s to mph: 1 m/s = 2.23694 mph
    wind_speed_ms = float(wind.get("speed", 0.0))
    wind_speed_mph = wind_speed_ms * 2.23694
    wind_deg = wind.get("deg", 0)
    wind_dir = deg_to_compass(wind_deg)

    # Visibility: meters to km and miles
    visibility_m = float(data.get("visibility", 10000))
    visibility_km = visibility_m / 1000.0
    visibility_mi = visibility_m * 0.000621371

    # Condition & Description
    condition = weather.get("main", "Clear")
    description = weather.get("description", "clear sky").title()
    icon_code = weather.get("icon", "01d")

    # Humidity & Pressure
    humidity = int(main.get("humidity", 0))
    pressure = int(main.get("pressure", 1013))

    # Timestamp & Celestial Observations
    dt = data.get("dt", 0)
    timezone_offset = data.get("timezone", 0)
    if dt:
        local_dt = datetime.fromtimestamp(dt + timezone_offset, timezone.utc).replace(tzinfo=None)
    else:
        local_dt = datetime.now(timezone.utc).replace(tzinfo=None)

    time_str = local_dt.strftime("%A, %b %d, %Y • %I:%M %p")
    local_time_clock = local_dt.strftime("%I:%M %p")

    # Sunrise and Sunset times
    sunrise_epoch = sys.get("sunrise")
    sunset_epoch = sys.get("sunset")
    sunrise_time = (
        datetime.fromtimestamp(sunrise_epoch + timezone_offset, timezone.utc).strftime("%I:%M %p")
        if sunrise_epoch else "--:--"
    )
    sunset_time = (
        datetime.fromtimestamp(sunset_epoch + timezone_offset, timezone.utc).strftime("%I:%M %p")
        if sunset_epoch else "--:--"
    )

    return {
        "city": city_name,
        "country": country,
        "location_display": full_location,
        "temp_c": round(temp_c, 1),
        "temp_f": round(temp_f, 1),
        "feels_like_c": round(feels_like_c, 1),
        "feels_like_f": round(feels_like_f, 1),
        "temp_min_c": round(temp_min_c, 1),
        "temp_max_c": round(temp_max_c, 1),
        "temp_min_f": round(temp_min_f, 1),
        "temp_max_f": round(temp_max_f, 1),
        "condition": condition,
        "description": description,
        "icon_code": icon_code,
        "humidity": humidity,
        "wind_speed_ms": round(wind_speed_ms, 1),
        "wind_speed_mph": round(wind_speed_mph, 1),
        "wind_deg": wind_deg,
        "wind_dir": wind_dir,
        "visibility_km": round(visibility_km, 1),
        "visibility_mi": round(visibility_mi, 1),
        "pressure": pressure,
        "time_str": time_str,
        "local_time": local_time_clock,
        "sunrise_time": sunrise_time,
        "sunset_time": sunset_time,
        "raw": data,
    }
