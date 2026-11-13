
import requests
import pytest

from app.weather_service import (
    get_city_coordinates,
    get_weather_data,
    CityNotFoundError,
    WeatherServiceError,
)


def test_get_city_coordinates_success(monkeypatch):
    """Test successful city lookup."""

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "results": [
                    {
                        "name": "Bengaluru",
                        "country": "India",
                        "admin1": "Karnataka",
                        "latitude": 12.97,
                        "longitude": 77.59,
                        "timezone": "Asia/Kolkata",
                    }
                ]
            }

    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )

    location = get_city_coordinates("Bengaluru")

    assert location["name"] == "Bengaluru"
    assert location["country"] == "India"
    assert location["latitude"] == 12.97
    assert location["longitude"] == 77.59


def test_get_city_coordinates_city_not_found(monkeypatch):
    """Test handling of an unknown city."""

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"results": None}

    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )

    with pytest.raises(CityNotFoundError):
        get_city_coordinates("UnknownCity")


def test_get_city_coordinates_connection_error(monkeypatch):
    """Test handling of a geocoding connection failure."""

    def mock_get(*args, **kwargs):
        raise requests.ConnectionError("Connection failed")

    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(WeatherServiceError):
        get_city_coordinates("Bengaluru")


def test_get_weather_data_success(monkeypatch):
    """Test successful weather forecast retrieval."""

    def mock_get_city_coordinates(city):
        return {
            "name": "Bengaluru",
            "country": "India",
            "admin1": "Karnataka",
            "latitude": 12.97,
            "longitude": 77.59,
            "timezone": "Asia/Kolkata",
        }

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "current": {
                    "temperature_2m": 22.1,
                    "relative_humidity_2m": 79,
                    "apparent_temperature": 22.6,
                    "is_day": 1,
                    "precipitation": 0,
                    "weather_code": 3,
                    "wind_speed_10m": 12.3,
                },
                "hourly": {
                    "time": ["2026-11-13T10:00"],
                    "temperature_2m": [22.1],
                    "relative_humidity_2m": [79],
                    "precipitation_probability": [0],
                    "weather_code": [3],
                    "wind_speed_10m": [12.3],
                },
                "daily": {
                    "time": ["2026-11-13"],
                    "weather_code": [3],
                    "temperature_2m_max": [28.0],
                    "temperature_2m_min": [18.0],
                    "sunrise": ["2026-11-13T06:00"],
                    "sunset": ["2026-11-13T18:00"],
                    "uv_index_max": [8.0],
                },
                "timezone": "Asia/Kolkata",
                "current_units": {},
                "hourly_units": {},
                "daily_units": {},
            }

    monkeypatch.setattr(
        "app.weather_service.get_city_coordinates",
        mock_get_city_coordinates,
    )

    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: MockResponse(),
    )

    weather = get_weather_data("Bengaluru")

    assert weather["location"]["name"] == "Bengaluru"
    assert weather["current"]["temperature_2m"] == 22.1
    assert weather["current"]["relative_humidity_2m"] == 79
    assert weather["current"]["apparent_temperature"] == 22.6
    assert weather["current"]["wind_speed_10m"] == 12.3
    assert weather["current"]["weather_description"]
    assert weather["current"]["weather_icon"]
    assert "hourly" in weather
    assert "daily" in weather


def test_get_weather_data_empty_city():
    """Test handling of an empty city name."""

    with pytest.raises(CityNotFoundError):
        get_weather_data("")


def test_get_weather_data_connection_error(monkeypatch):
    """Test handling of a weather API connection failure."""

    def mock_get_city_coordinates(city):
        return {
            "name": "Bengaluru",
            "country": "India",
            "admin1": "Karnataka",
            "latitude": 12.97,
            "longitude": 77.59,
            "timezone": "Asia/Kolkata",
        }

    def mock_get(*args, **kwargs):
        raise requests.ConnectionError("Connection failed")

    monkeypatch.setattr(
        "app.weather_service.get_city_coordinates",
        mock_get_city_coordinates,
    )

    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(WeatherServiceError):
        get_weather_data("Bengaluru")
