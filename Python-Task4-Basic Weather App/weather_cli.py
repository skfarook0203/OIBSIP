#!/usr/bin/env python3
"""
CLI Weather Application (Beginner Tier)
Fetches and displays real-time weather data for user-specified locations
using the OpenWeatherMap API with graceful error handling and input validation.

Feature Checklist — Beginner Tier:
• Prompt user to enter a city name or ZIP code
• Make an API call to OpenWeatherMap (or equivalent free API) and parse the JSON response
• Display: current temperature (°C and °F), humidity percentage, weather condition description (e.g., 'Partly Cloudy'), wind speed
• Handle API errors gracefully: city not found, network timeout, invalid API key
• Input validation: reject empty city input
"""

import sys
import os

# Import modular services
import config
from weather_service import WeatherServiceError, get_current_weather


def print_banner():
    """Prints a clean CLI application banner."""
    print("=" * 60)
    print("                    WEATHER CLI TOOL")
    print("        Real-Time Meteorological Observations")
    print("=" * 60)


def display_weather_report(data: dict):
    """
    Renders formatted weather telemetry meeting all Beginner Tier requirements:
    - Temperature in both °C and °F
    - Humidity percentage
    - Weather condition description
    - Wind speed
    """
    location = data.get("location_display", data.get("city", "Unknown"))
    temp_c = data.get("temp_c", 0.0)
    temp_f = data.get("temp_f", 0.0)
    feels_c = data.get("feels_like_c", temp_c)
    feels_f = data.get("feels_like_f", temp_f)
    condition = data.get("condition", "N/A")
    description = data.get("description", "N/A")
    humidity = data.get("humidity", 0)
    wind_ms = data.get("wind_speed_ms", 0.0)
    wind_mph = data.get("wind_speed_mph", 0.0)
    wind_dir = data.get("wind_dir", "N/A")
    local_time = data.get("time_str", "N/A")

    print("\n" + "-" * 60)
    print(f"  LOCATION        : {location}")
    print(f"  LOCAL TIME      : {local_time}")
    print("-" * 60)
    print(f"  TEMPERATURE     : {temp_c:.1f}°C  /  {temp_f:.1f}°F")
    print(f"  FEELS LIKE      : {feels_c:.1f}°C  /  {feels_f:.1f}°F")
    print(f"  CONDITION       : {description} ({condition})")
    print(f"  HUMIDITY        : {humidity}%")
    print(f"  WIND SPEED      : {wind_ms:.1f} m/s  ({wind_mph:.1f} mph) {wind_dir}")
    print("-" * 60 + "\n")


def fetch_and_print_weather(query: str) -> bool:
    """
    Validates input, calls API, parses response, and catches errors gracefully.
    Returns True on success, False on error.
    """
    # 1. Input Validation: Reject empty or whitespace-only input
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        print("\n[Input Validation Error] City name or ZIP code cannot be empty.")
        print("Please enter a valid location (e.g. 'Hyderabad', 'London, UK', or '94016').\n")
        return False

    # 2. Make API call and handle errors gracefully
    print(f"\nRetrieving real-time weather observations for '{cleaned_query}'...")
    try:
        data = get_current_weather(cleaned_query)
        display_weather_report(data)
        return True

    except WeatherServiceError as err:
        # Graceful handling for City not found, Network timeout, Invalid API key
        print("\n" + "!" * 60)
        print("  [ERROR] Weather Observation Query Failed")
        print(f"  Details: {err.message}")
        print("!" * 60 + "\n")
        return False

    except Exception as exc:
        print("\n" + "!" * 60)
        print(f"  [ERROR] An unexpected network or data error occurred: {str(exc)}")
        print("!" * 60 + "\n")
        return False


def run_interactive_cli():
    """Runs the CLI tool in interactive prompt loop."""
    print_banner()
    print("Commands: Enter a city or ZIP code. Type 'q' or 'exit' to quit.\n")

    while True:
        try:
            # Prompt user to enter a city name or ZIP code
            user_input = input("Enter city name or ZIP code: ").strip()

            if user_input.lower() in ("q", "quit", "exit"):
                print("\nExiting Weather CLI. Goodbye!")
                break

            # Process input and display weather
            fetch_and_print_weather(user_input)

        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled. Goodbye!")
            break


def main():
    """Entry point for CLI execution."""
    # Filter out flags like --cli or -c if invoked from wrapper
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    # Check if a query argument was provided via command line: e.g. python3 weather_cli.py London
    if args:
        query_arg = " ".join(args).strip()
        print_banner()
        success = fetch_and_print_weather(query_arg)
        sys.exit(0 if success else 1)
    else:
        run_interactive_cli()


if __name__ == "__main__":
    main()
