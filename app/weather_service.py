
"""
Weather service for WeatherNow.

Handles communication with the Open-Meteo Geocoding
and Forecast APIs, including validation and error handling.
"""

import requests

from app.weather_codes import get_weather_description, get_weather_icon


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

REQUEST_TIMEOUT = 10


class WeatherServiceError(Exception):
    """Raised when a weather API request fails."""


class CityNotFoundError(WeatherServiceError):
    """Raised when the requested city cannot be found."""


def _get_api_response(url, params, service_name):
    """
    Send an API request and safely return its JSON response.

    Raises:
        WeatherServiceError: If the request fails or the response is invalid.
    """
    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

    except ValueError as error:
        raise WeatherServiceError(
            f"The {service_name} returned an invalid response."
        ) from error

    except requests.RequestException as error:
        raise WeatherServiceError(
            f"Unable to connect to the {service_name}. Please try again."
        ) from error

    if not isinstance(data, dict):
        raise WeatherServiceError(
            f"The {service_name} returned unexpected data."
        )

    if data.get("error"):
        raise WeatherServiceError(
            f"The {service_name} reported an error. Please try again."
        )

    return data


def get_city_coordinates(city):
    """
    Find a city's latitude, longitude, and location details.

    Args:
        city (str): City name.

    Returns:
        dict: City name, country, region, coordinates, and timezone.
    """
    if not isinstance(city, str) or not city.strip():
        raise CityNotFoundError("Please enter a city name.")

    city = city.strip()

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    data = _get_api_response(
        GEOCODING_URL,
        params,
        "location service",
    )

    results = data.get("results")

    if not isinstance(results, list) or not results:
        raise CityNotFoundError(
            f"We couldn't find a city named '{city}'. "
            "Please check the spelling."
        )

    location = results[0]

    if not isinstance(location, dict):
        raise WeatherServiceError(
            "The location service returned invalid location data."
        )

    try:
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])

    except (KeyError, TypeError, ValueError) as error:
        raise WeatherServiceError(
            "The location service returned incomplete coordinates."
        ) from error

    return {
        "name": location.get("name") or city,
        "country": location.get("country") or "",
        "admin1": location.get("admin1") or "",
        "latitude": latitude,
        "longitude": longitude,
        "timezone": location.get("timezone") or "auto",
    }


def get_weather_data(city):
    """
    Retrieve current weather, hourly forecast, and daily forecast.

    Args:
        city (str): Name of the city to search.

    Returns:
        dict: Location and weather information.
    """
    if not isinstance(city, str) or not city.strip():
        raise CityNotFoundError("Please enter a city name.")

    location = get_city_coordinates(city)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "is_day,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation_probability,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "sunrise,"
            "sunset,"
            "uv_index_max"
        ),
        "timezone": location["timezone"],
        "forecast_days": 7,
    }

    data = _get_api_response(
        FORECAST_URL,
        params,
        "weather service",
    )

    current = data.get("current")
    hourly = data.get("hourly")
    daily = data.get("daily")

    if not isinstance(current, dict):
        raise WeatherServiceError(
            "The weather service did not return current conditions."
        )

    if not isinstance(hourly, dict):
        raise WeatherServiceError(
            "The weather service did not return hourly forecasts."
        )

    if not isinstance(daily, dict):
        raise WeatherServiceError(
            "The weather service did not return daily forecasts."
        )

    # Validate the current weather fields required by the application.
    required_current_fields = [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "weather_code",
        "wind_speed_10m",
    ]

    if not all(field in current for field in required_current_fields):
        raise WeatherServiceError(
            "The weather service returned incomplete current conditions."
        )

    # Validate the hourly forecast fields.
    required_hourly_fields = [
        "time",
        "temperature_2m",
        "weather_code",
        "precipitation_probability",
    ]

    if not all(
        isinstance(hourly.get(field), list)
        for field in required_hourly_fields
    ):
        raise WeatherServiceError(
            "The weather service returned incomplete hourly forecasts."
        )

    # Validate the daily forecast fields.
    required_daily_fields = [
        "time",
        "temperature_2m_max",
        "temperature_2m_min",
        "weather_code",
    ]

    if not all(
        isinstance(daily.get(field), list)
        for field in required_daily_fields
    ):
        raise WeatherServiceError(
            "The weather service returned incomplete daily forecasts."
        )

    # Check that forecast arrays contain data.
    if not hourly["time"] or not daily["time"]:
        raise WeatherServiceError(
            "The weather service returned empty forecast data."
        )

    # Add readable weather information.
    weather_code = current["weather_code"]

    current["weather_description"] = get_weather_description(weather_code)
    current["weather_icon"] = get_weather_icon(weather_code)

    return {
        "location": location,
        "current": current,
        "hourly": hourly,
        "daily": daily,
        "timezone": data.get("timezone", location["timezone"]),
        "current_units": data.get("current_units", {}),
        "hourly_units": data.get("hourly_units", {}),
        "daily_units": data.get("daily_units", {}),
    }
