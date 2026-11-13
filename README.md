

# WeatherNow

A responsive weather forecasting web application built with **Python, Flask, JavaScript, HTML, and CSS**, using the free [Open-Meteo API](https://open-meteo.com/).

WeatherNow allows users to search for cities worldwide and view current weather conditions, hourly forecasts, and a 7-day forecast.

## Features

- Search for weather by city name.
- Display current temperature and weather conditions.
- Show feels-like temperature, humidity, and wind speed.
- Display weather icons and condition descriptions.
- View an hourly weather forecast.
- View a 7-day weather forecast.
- Switch between Celsius (°C) and Fahrenheit (°F).
- Handle invalid city names and API errors.
- Responsive interface for different screen sizes.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework and API routes |
| Requests | HTTP communication with Open-Meteo |
| HTML5 | Page structure |
| CSS3 | Styling and responsive layout |
| JavaScript | Dynamic weather display and interactions |
| Open-Meteo | Geocoding and weather forecast data |
| Pytest | Automated testing |

## Project Structure

```text
WeatherNow/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── weather_service.py
│   ├── weather_codes.py
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── app.js
│   │   └── images/
│   │
│   └── templates/
│       └── index.html
│
├── tests/
│   ├── test_routes.py
│   └── test_weather_service.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd WeatherNow
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python run.py
```

Open the application in your browser at:

```text
http://127.0.0.1:5000/
```

## API Information

WeatherNow uses two public Open-Meteo APIs.

### Geocoding API

Used to convert a city name into geographical coordinates.

```text
https://geocoding-api.open-meteo.com/v1/search
```

### Forecast API

Used to retrieve current weather conditions and forecasts.

```text
https://api.open-meteo.com/v1/forecast
```

No API key is required for the public Open-Meteo endpoints used by this project.

## Application API Endpoint

WeatherNow provides a Flask endpoint:

```http
GET /api/weather?city=Bengaluru
```

A successful response contains location information, current weather, hourly forecasts, and daily forecasts.

Example error response:

```json
{
  "success": false,
  "error": "Please enter a city name."
}
```

## Running Automated Tests

The project uses Pytest.

Run all tests:

```bash
python -m pytest -v
```

The test suite covers:

- Homepage loading.
- Missing city input.
- Successful weather API responses.
- City-not-found errors.
- Weather service failures.
- Geocoding success and error handling.
- Weather data retrieval and validation.

## Error Handling

WeatherNow handles common failures, including:

- Empty city input.
- City names that cannot be found.
- Network connection failures.
- Invalid API responses.
- Unexpected server errors.

## Future Improvements

Potential enhancements include:

- Weather alerts and notifications.
- Search history and favourite cities.
- Sunrise and sunset information.
- UV index display.
- Improved accessibility.
- Deployment to a cloud hosting platform.

## License

This project is intended for educational and personal portfolio purposes.

Weather data is provided by [Open-Meteo](https://open-meteo.com/).

