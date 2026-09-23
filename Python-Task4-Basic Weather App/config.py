"""
Configuration Module for OASIS Infobyte Weather Application (Task 4 - Advanced Tier).
Handles environment variable loading, API endpoint constants, validation, and GUI themes.
"""

import os

# Safely load variables from .env file using standard library
def _load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.isfile(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

# OpenWeatherMap API Configurations
# The API key should be provided via .env file: OPENWEATHER_API_KEY=your_key
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()

# Base URLs for OpenWeatherMap 2.5 APIs
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL_TEMPLATE = "https://openweathermap.org/img/wn/{icon}@2x.png"

# Location Lookup API (Optional feature)
IPINFO_URL = "https://ipinfo.io/json"

# Network Timeouts (in seconds)
DEFAULT_TIMEOUT = 10
LOCATION_TIMEOUT = 5

# Application Metadata
APP_TITLE = "Weather Dashboard"
APP_SUBTITLE = "Real-time Weather Observations & Multi-day Forecast"
APP_VERSION = "2.0.0"

# Default Geometry
WINDOW_WIDTH = 760
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 700
WINDOW_MIN_HEIGHT = 750

# Visual Styling Palette (Modern Desktop Theme)
THEME = {
    # Base backgrounds
    "bg_dark": "#0f172a",         # Deep slate navy
    "bg_card": "#1e293b",         # Elevated card surface
    "bg_card_inner": "#0f172a",   # Inset elements
    "bg_hover": "#334155",        # Hover state
    
    # Text colors
    "text_primary": "#f8fafc",    # High-contrast white
    "text_secondary": "#94a3b8",  # Muted slate
    "text_muted": "#64748b",      # Dim helper text
    
    # Accent colors
    "accent_blue": "#38bdf8",     # Sky blue highlight
    "accent_blue_hover": "#0284c7",
    "accent_emerald": "#34d399",  # Metric / success green
    "accent_amber": "#fbbf24",    # Warnings / sun
    "accent_red": "#f87171",      # Errors / alerts
    "border": "#334155",          # Clean divider borders
    
    # Status badges
    "status_info_bg": "#1e3a8a",
    "status_info_fg": "#93c5fd",
    "status_error_bg": "#450a0a",
    "status_error_fg": "#fca5a5",
    "status_success_bg": "#064e3b",
    "status_success_fg": "#6ee7b7",
}

# Standard Wind Direction Compass Mapping
COMPASS_DIRECTIONS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
]


def deg_to_compass(degrees: float | int) -> str:
    """Converts wind degree (0-360) into compass heading (e.g. N, ENE)."""
    try:
        val = int((float(degrees) / 22.5) + 0.5)
        return COMPASS_DIRECTIONS[val % 16]
    except Exception:
        return "N/A"


def validate_api_key(api_key: str | None = None) -> tuple[bool, str]:
    """
    Validates the API key format without making network requests.
    Returns (is_valid, message).
    """
    key = api_key if api_key is not None else OPENWEATHER_API_KEY
    if not key:
        return False, (
            "API key not found in .env.\n"
            "Please configure OPENWEATHER_API_KEY in your .env file."
        )
    if len(key) < 20:
        return False, (
            "The configured API key appears to be invalid or incomplete.\n"
            "A 32-character alphanumeric key is required."
        )
    return True, "API Key format is valid."
