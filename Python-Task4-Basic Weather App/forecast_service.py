"""
Forecast Service Module for OASIS Infobyte Weather Application.
Queries the OpenWeatherMap 5-day / 3-hour forecast API and processes
both the Next 6-to-12-Hour timeline and the 5-Day Daily Outlook.
"""

from collections import defaultdict
from datetime import datetime, timezone
import json
import socket
import urllib.request
import urllib.parse
import urllib.error

from config import DEFAULT_TIMEOUT, FORECAST_URL, OPENWEATHER_API_KEY
from weather_service import WeatherServiceError, _build_params


def get_forecast_data(query: str, api_key: str | None = None) -> dict:
    """
    Fetches the 5-day / 3-hour forecast payload and processes:
    1. 'hourly': The next upcoming intervals (covering 6 to 12 hours)
    2. 'daily': The 5-day outlook with daily high/low temperatures & conditions.
    """
    if not query or not query.strip():
        raise WeatherServiceError("Please enter a location for forecast data.")

    active_key = (api_key or OPENWEATHER_API_KEY).strip()
    if not active_key:
        raise WeatherServiceError(
            "API key is missing. Please configure OPENWEATHER_API_KEY in your .env file."
        )

    params = _build_params(query, active_key)
    params["units"] = "metric"

    url = f"{FORECAST_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherApp/2.0"})

    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            status_code = resp.status
            raw_body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8") if exc.fp else ""
        if exc.code == 401:
            raise WeatherServiceError(
                "Invalid API key when requesting forecast data.",
                status_code=401,
            )
        elif exc.code == 404:
            raise WeatherServiceError(
                f"Forecast not found for '{query.strip()}'.",
                status_code=404,
            )
        else:
            raise WeatherServiceError(
                f"Forecast API error ({exc.code})",
                status_code=exc.code,
            )
    except (socket.timeout, urllib.error.URLError) as exc:
        if isinstance(exc, socket.timeout) or (isinstance(exc, urllib.error.URLError) and isinstance(exc.reason, socket.timeout)):
            raise WeatherServiceError(
                "Forecast request timed out. Please check your network connection."
            )
        raise WeatherServiceError(
            "Unable to connect to forecast service. Please check your internet connection."
        )
    except Exception as exc:
        raise WeatherServiceError(f"Forecast network error: {str(exc)}")

    try:
        payload = json.loads(raw_body)
    except (ValueError, json.JSONDecodeError):
        raise WeatherServiceError("Invalid JSON received from forecast service.")

    forecast_items = payload.get("list", [])
    if not forecast_items:
        raise WeatherServiceError("No forecast intervals returned for this location.")

    timezone_offset = payload.get("city", {}).get("timezone", 0)

    return {
        "hourly": _process_upcoming_hours(forecast_items, timezone_offset),
        "daily": _process_five_day_outlook(forecast_items, timezone_offset),
    }


def _process_upcoming_hours(items: list[dict], timezone_offset: int) -> list[dict]:
    """
    Extracts the immediate upcoming forecast intervals.
    Provides the next 4-5 intervals (covering the next 6 to 12 hours in 3h steps).
    """
    hourly_results = []
    # Take up to the first 5 entries
    for item in items[:5]:
        dt = item.get("dt", 0)
        if dt:
            local_dt = datetime.fromtimestamp(dt + timezone_offset, timezone.utc).replace(tzinfo=None)
        else:
            local_dt = datetime.now(timezone.utc).replace(tzinfo=None)

        time_label = local_dt.strftime("%I %p").lstrip("0")
        if not time_label:
            time_label = local_dt.strftime("%I %p")

        main = item.get("main", {})
        temp_c = float(main.get("temp", 0.0))
        temp_f = (temp_c * 9.0 / 5.0) + 32.0

        weather_list = item.get("weather", [{}])
        weather = weather_list[0] if weather_list else {}
        condition = weather.get("main", "Clear")
        description = weather.get("description", "").title()
        icon_code = weather.get("icon", "01d")
        pop = float(item.get("pop", 0.0))

        hourly_results.append({
            "time": time_label,
            "time_label": time_label,
            "datetime_str": local_dt.strftime("%b %d, %I:%M %p"),
            "temp_c": round(temp_c, 1),
            "temp_f": round(temp_f, 1),
            "condition": condition,
            "description": description,
            "icon_code": icon_code,
            "humidity": int(main.get("humidity", 0)),
            "pop": pop,
        })

    return hourly_results


def _process_five_day_outlook(items: list[dict], timezone_offset: int) -> list[dict]:
    """
    Aggregates the 40 three-hour forecast points into 5 calendar days,
    calculating daily high, daily low, and representative weather conditions.
    """
    days_dict = defaultdict(list)

    for item in items:
        dt = item.get("dt", 0)
        if dt:
            local_dt = datetime.fromtimestamp(dt + timezone_offset, timezone.utc).replace(tzinfo=None)
        else:
            local_dt = datetime.now(timezone.utc).replace(tzinfo=None)

        date_key = local_dt.date()
        days_dict[date_key].append((local_dt, item))

    daily_results = []
    # Sort by date
    sorted_dates = sorted(days_dict.keys())

    # We want up to 5 days
    for date_key in sorted_dates[:5]:
        group = days_dict[date_key]
        temps_c = [float(it[1].get("main", {}).get("temp", 0.0)) for it in group]
        min_c = min(temps_c) if temps_c else 0.0
        max_c = max(temps_c) if temps_c else 0.0

        min_f = (min_c * 9.0 / 5.0) + 32.0
        max_f = (max_c * 9.0 / 5.0) + 32.0

        # Pick representative reading: prefer midday ~12:00-15:00, or center of day
        midday_item = None
        for local_dt, item in group:
            if 11 <= local_dt.hour <= 15:
                midday_item = item
                break
        if not midday_item:
            midday_item = group[len(group) // 2][1]

        weather_list = midday_item.get("weather", [{}])
        weather = weather_list[0] if weather_list else {}
        condition = weather.get("main", "Clear")
        description = weather.get("description", "").title()
        icon_code = weather.get("icon", "01d")

        # Format day: "Mon, Sep 23"
        first_dt = group[0][0]
        day_name = first_dt.strftime("%a")
        date_str = first_dt.strftime("%b %d")

        daily_results.append({
            "day_name": day_name,
            "date_str": date_str,
            "display_date": f"{day_name}, {date_str}",
            "temp_min_c": round(min_c, 1),
            "temp_max_c": round(max_c, 1),
            "temp_min_f": round(min_f, 1),
            "temp_max_f": round(max_f, 1),
            "condition": condition,
            "description": description,
            "icon_code": icon_code,
        })

    return daily_results
