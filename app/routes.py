
from flask import Blueprint, render_template, request, jsonify

from app.weather_service import (
    get_weather_data,
    CityNotFoundError,
    WeatherServiceError,
)


main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html", app_name="WeatherNow")


@main.route("/api/weather", methods=["GET"])
def weather():
    """Return weather information for the requested city."""

    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({
            "success": False,
            "error": "Please enter a city name.",
        }), 400

    try:
        weather_data = get_weather_data(city)

        return jsonify({
            "success": True,
            "data": weather_data,
        }), 200

    except CityNotFoundError as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 404

    except WeatherServiceError as error:
        return jsonify({
            "success": False,
            "error": str(error),
        }), 502

    except Exception:
        # Keep unexpected internal errors out of the API response.
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred. Please try again.",
        }), 500
