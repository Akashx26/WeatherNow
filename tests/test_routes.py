
import pytest

from app import create_app
from app.weather_service import CityNotFoundError, WeatherServiceError


@pytest.fixture
def app():
    """Create a Flask application for testing."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app


@pytest.fixture
def client(app):
    """Create a test client for sending HTTP requests."""
    return app.test_client()


def test_homepage_loads_successfully(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"WeatherNow" in response.data


def test_weather_api_requires_city_name(client):
    response = client.get("/api/weather")

    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["error"] == "Please enter a city name."


def test_weather_api_returns_weather(monkeypatch, client):
    """Test a successful weather API response without calling Open-Meteo."""

    sample_weather = {
        "location": {
            "name": "Bengaluru",
            "country": "India",
        },
        "current": {
            "temperature_2m": 22.1,
            "weather_description": "Overcast",
        },
        "hourly": {},
        "daily": {},
    }

    def mock_get_weather_data(city):
        assert city == "Bengaluru"
        return sample_weather

    monkeypatch.setattr(
        "app.routes.get_weather_data",
        mock_get_weather_data,
    )

    response = client.get("/api/weather?city=Bengaluru")

    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["data"]["current"]["temperature_2m"] == 22.1


def test_weather_api_handles_city_not_found(monkeypatch, client):

    def mock_get_weather_data(city):
        raise CityNotFoundError(
            "We couldn't find a city named 'Unknown'. Please check the spelling."
        )

    monkeypatch.setattr(
        "app.routes.get_weather_data",
        mock_get_weather_data,
    )

    response = client.get("/api/weather?city=Unknown")

    assert response.status_code == 404
    assert response.json["success"] is False
    assert "couldn't find a city" in response.json["error"]


def test_weather_api_handles_service_error(monkeypatch, client):

    def mock_get_weather_data(city):
        raise WeatherServiceError(
            "Unable to retrieve weather information. Please try again."
        )

    monkeypatch.setattr(
        "app.routes.get_weather_data",
        mock_get_weather_data,
    )

    response = client.get("/api/weather?city=Bengaluru")

    assert response.status_code == 502
    assert response.json["success"] is False
    assert "Unable to retrieve weather information" in response.json["error"]
