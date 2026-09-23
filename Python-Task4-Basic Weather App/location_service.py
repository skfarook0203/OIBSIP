"""
Location Service Module for Weather Application.
Queries geolocation providers (ipinfo.io with ipapi.co fallback) and OpenWeatherMap
reverse geocoding for pinpoint coordinate resolution.
Uses Python standard library (urllib.request).
"""

from __future__ import annotations

import ipaddress
import json
import urllib.error
import urllib.request
from config import IPINFO_URL, LOCATION_TIMEOUT, OPENWEATHER_API_KEY


def _is_public_ip(ip: str | None) -> bool:
    """Checks whether the given string is a valid public/global IPv4 or IPv6 address."""
    if not ip or not isinstance(ip, str):
        return False
    try:
        obj = ipaddress.ip_address(ip.strip())
        return obj.is_global
    except ValueError:
        return False


def reverse_geocode(lat: float, lon: float, api_key: str | None = None) -> tuple[str | None, str]:
    """
    Reverse geocodes latitude and longitude into an exact city name and country
    using OpenWeatherMap's official Geocoding API.
    Returns:
        (location_query, status_message)
    """
    active_key = (api_key or OPENWEATHER_API_KEY).strip()
    if not active_key:
        return None, "OpenWeatherMap API key is required for reverse geocoding."

    try:
        url = (
            f"http://api.openweathermap.org/geo/1.0/reverse?"
            f"lat={lat:.4f}&lon={lon:.4f}&limit=1&appid={active_key}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "WeatherApp/2.0"})
        with urllib.request.urlopen(req, timeout=LOCATION_TIMEOUT) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data and isinstance(data, list) and len(data) > 0:
                    item = data[0]
                    city = item.get("name", "").strip()
                    country = item.get("country", "").strip()
                    state = item.get("state", "").strip()
                    if city:
                        query_str = f"{city}, {country}" if country else city
                        details = f"{city}, {state}, {country}".replace(", ,", ",").strip(", ")
                        return query_str, f"Detected location from coordinates: {details}"
    except Exception as exc:
        return None, f"Reverse geocoding failed: {str(exc)}"

    return None, f"No location found for coordinates ({lat:.4f}, {lon:.4f})."


def get_approximate_location(client_ip: str | None = None) -> tuple[str | None, str]:
    """
    Attempts to detect approximate location via ipinfo.io, with automatic
    fallback to ipapi.co to reduce variations and handle rate limits.
    
    If client_ip is provided and is a valid public IP, queries that IP specifically.
    Returns:
        (location_query, status_message)
    """
    target_ip = client_ip.strip() if _is_public_ip(client_ip) else None

    # 1. Primary Provider: ipinfo.io
    try:
        url = f"https://ipinfo.io/{target_ip}/json" if target_ip else IPINFO_URL
        req = urllib.request.Request(url, headers={"User-Agent": "WeatherApp/2.0"})
        with urllib.request.urlopen(req, timeout=LOCATION_TIMEOUT) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                city = data.get("city", "").strip()
                region = data.get("region", "").strip()
                country = data.get("country", "").strip()

                if city:
                    query_str = f"{city}, {country}" if country else city
                    details = f"{city}, {region}, {country}".strip(", ")
                    return query_str, f"Detected approximate location: {details}"
    except Exception:
        # Fall through to secondary provider
        pass

    # 2. Secondary Fallback Provider: ipapi.co
    try:
        fallback_url = f"https://ipapi.co/{target_ip}/json/" if target_ip else "https://ipapi.co/json/"
        req = urllib.request.Request(fallback_url, headers={"User-Agent": "WeatherApp/2.0"})
        with urllib.request.urlopen(req, timeout=LOCATION_TIMEOUT) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                city = data.get("city", "").strip()
                region = data.get("region", "").strip()
                country = data.get("country_code", data.get("country", "")).strip()

                if city:
                    query_str = f"{city}, {country}" if country else city
                    details = f"{city}, {region}, {country}".strip(", ")
                    return query_str, f"Detected approximate location: {details}"
    except Exception as exc:
        return None, f"Could not determine location automatically: {str(exc)}"

    return None, "Unable to extract city name from IP geolocation services."
