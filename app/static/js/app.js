
// ==========================================
// WEATHER NOW - APPLICATION JAVASCRIPT
// ==========================================


// ==========================================
// DOM ELEMENTS
// ==========================================

const form = document.getElementById("search-form");
const cityInput = document.getElementById("city-input");
const searchButton = document.getElementById("search-button");
const statusEl = document.getElementById("status");
const dashboard = document.getElementById("weather-dashboard");

// Temperature unit controls
const celsiusButton = document.getElementById("celsius-button");
const fahrenheitButton = document.getElementById("fahrenheit-button");
const temperatureUnit = document.getElementById("temperature-unit");

// Location elements
const locationName = document.getElementById("location-name");
const locationDetails = document.getElementById("location-details");

// Current weather elements
const weatherIcon = document.getElementById("weather-icon");
const currentTemperature = document.getElementById("current-temperature");
const weatherDescription = document.getElementById("weather-description");

// Weather detail elements
const feelsLike = document.getElementById("feels-like");
const humidity = document.getElementById("humidity");
const windSpeed = document.getElementById("wind-speed");

// Forecast elements
const hourlyForecast = document.getElementById("hourly-forecast");
const dailyForecast = document.getElementById("daily-forecast");


// ==========================================
// APPLICATION STATE
// ==========================================

let selectedUnit = "C";
let latestWeatherData = null;

// Tracks the currently active weather request.
let activeWeatherRequest = null;

// Identifies the latest search.
let latestRequestId = 0;


// ==========================================
// TEMPERATURE CONVERSION
// ==========================================

function convertTemperature(celsius) {
    if (selectedUnit === "F") {
        return (celsius * 9 / 5) + 32;
    }

    return celsius;
}


function formatTemperature(value) {
    if (
        value === null ||
        value === undefined ||
        !Number.isFinite(Number(value))
    ) {
        return "N/A";
    }

    const convertedValue = convertTemperature(Number(value));

    return `${convertedValue.toFixed(1)} °${selectedUnit}`;
}


// ==========================================
// HTML ELEMENT CREATION
// ==========================================

function createElement(tag, className, text) {
    const element = document.createElement(tag);

    if (className) {
        element.className = className;
    }

    if (text !== undefined) {
        element.textContent = text;
    }

    return element;
}


// ==========================================
// DATE FORMATTING
// ==========================================

function formatDateTime(dateString) {
    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
        return dateString;
    }

    return date.toLocaleString([], {
        weekday: "short",
        hour: "numeric",
        minute: "2-digit"
    });
}


function formatDate(dateString) {
    const date = new Date(`${dateString}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return dateString;
    }

    return date.toLocaleDateString([], {
        weekday: "short",
        day: "numeric",
        month: "short"
    });
}


// ==========================================
// WEATHER ICONS
// ==========================================

function getWeatherIcon(code) {
    const icons = {
        0: "☀️",
        1: "🌤️",
        2: "⛅",
        3: "☁️",
        45: "🌫️",
        48: "🌫️",
        51: "🌦️",
        53: "🌦️",
        55: "🌧️",
        56: "🌧️",
        57: "🌧️",
        61: "🌦️",
        63: "🌧️",
        65: "🌧️",
        66: "🌧️",
        67: "🌧️",
        71: "🌨️",
        73: "🌨️",
        75: "❄️",
        77: "❄️",
        80: "🌦️",
        81: "🌧️",
        82: "⛈️",
        85: "🌨️",
        86: "❄️",
        95: "⛈️",
        96: "⛈️",
        99: "⛈️"
    };

    return icons[code] || "🌡️";
}


// ==========================================
// FORECAST CARD CREATION
// ==========================================

function createForecastCard(title, icon, details) {
    const card = createElement("article", "forecast-card");

    card.appendChild(
        createElement("h3", "", title)
    );

    card.appendChild(
        createElement("p", "forecast-icon", icon)
    );

    details.forEach((detail) => {
        card.appendChild(
            createElement("p", "", detail)
        );
    });

    return card;
}


// ==========================================
// CURRENT WEATHER DISPLAY
// ==========================================

function displayCurrentWeather(data) {
    const location = data.location;
    const current = data.current;

    locationName.textContent = location.name;

    const locationParts = [
        location.admin1,
        location.country
    ].filter(Boolean);

    locationDetails.textContent = locationParts.join(", ");

    weatherIcon.textContent = current.weather_icon;

    currentTemperature.textContent = convertTemperature(
        current.temperature_2m
    ).toFixed(1);

    temperatureUnit.textContent = `°${selectedUnit}`;

    weatherDescription.textContent =
        current.weather_description;

    feelsLike.textContent = formatTemperature(
        current.apparent_temperature
    );

    humidity.textContent =
        `${current.relative_humidity_2m}%`;

    windSpeed.textContent =
        `${current.wind_speed_10m} km/h`;
}


// ==========================================
// HOURLY FORECAST DISPLAY
// ==========================================

function displayHourlyForecast(data) {
    hourlyForecast.replaceChildren();

    const times = data.time || [];
    const temperatures = data.temperature_2m || [];
    const weatherCodes = data.weather_code || [];
    const rainProbabilities = data.precipitation_probability || [];

    const now = Date.now();

    const startIndex = times.findIndex((time) => {
        return new Date(time).getTime() >= now;
    });

    const firstIndex = startIndex === -1 ? 0 : startIndex;

    const endIndex = Math.min(
        firstIndex + 24,
        times.length
    );

    for (let i = firstIndex; i < endIndex; i++) {
        const icon = getWeatherIcon(weatherCodes[i]);

        const card = createForecastCard(
            formatDateTime(times[i]),
            icon,
            [
                `Temperature: ${formatTemperature(temperatures[i])}`,
                `Rain chance: ${rainProbabilities[i] ?? "N/A"}%`
            ]
        );

        hourlyForecast.appendChild(card);
    }
}


// ==========================================
// SEVEN-DAY FORECAST DISPLAY
// ==========================================

function displayDailyForecast(data) {
    dailyForecast.replaceChildren();

    const times = data.time || [];
    const maxTemperatures = data.temperature_2m_max || [];
    const minTemperatures = data.temperature_2m_min || [];
    const weatherCodes = data.weather_code || [];

    for (let i = 0; i < times.length; i++) {
        const icon = getWeatherIcon(weatherCodes[i]);

        const card = createForecastCard(
            formatDate(times[i]),
            icon,
            [
                `High: ${formatTemperature(maxTemperatures[i])}`,
                `Low: ${formatTemperature(minTemperatures[i])}`
            ]
        );

        dailyForecast.appendChild(card);
    }
}


// ==========================================
// RENDER WEATHER DASHBOARD
// ==========================================

function renderWeatherDashboard() {
    if (!latestWeatherData) {
        return;
    }

    displayCurrentWeather(latestWeatherData);

    displayHourlyForecast(
        latestWeatherData.hourly
    );

    displayDailyForecast(
        latestWeatherData.daily
    );
}


// ==========================================
// TEMPERATURE UNIT SWITCHING
// ==========================================

function changeTemperatureUnit(unit) {
    selectedUnit = unit;

    celsiusButton.classList.toggle(
        "active",
        unit === "C"
    );

    fahrenheitButton.classList.toggle(
        "active",
        unit === "F"
    );

    celsiusButton.setAttribute(
        "aria-pressed",
        unit === "C"
    );

    fahrenheitButton.setAttribute(
        "aria-pressed",
        unit === "F"
    );

    renderWeatherDashboard();
}


// ==========================================
// WEATHER API REQUEST
// ==========================================

async function searchWeather(city) {
    // Give every search a unique ID.
    const requestId = ++latestRequestId;

    // Cancel any previous search.
    if (activeWeatherRequest) {
        activeWeatherRequest.abort();
    }

    // Create a controller for this request.
    const controller = new AbortController();
    activeWeatherRequest = controller;

    // Track whether the request timed out.
    let requestTimedOut = false;

    const timeoutId = setTimeout(() => {
        requestTimedOut = true;
        controller.abort();
    }, 15000);

    // Update the interface.
    statusEl.textContent =
        `Searching weather for ${city}...`;

    searchButton.disabled = true;
    searchButton.textContent = "Searching...";

    dashboard.hidden = true;

    try {
        const response = await fetch(
            `/api/weather?city=${encodeURIComponent(city)}`,
            {
                signal: controller.signal
            }
        );

        // Ignore responses from outdated searches.
        if (requestId !== latestRequestId) {
            return;
        }

        // Safely parse the server response.
        let result;

        try {
            result = await response.json();
        } catch {
            throw new Error(
                "The server returned an invalid response. Please try again."
            );
        }

        // Check HTTP and application-level errors.
        if (!response.ok || !result.success) {
            throw new Error(
                result.error ||
                `Weather request failed (HTTP ${response.status}).`
            );
        }

        // Verify that the expected weather data exists.
        if (
            !result.data ||
            !result.data.location ||
            !result.data.current ||
            !result.data.hourly ||
            !result.data.daily
        ) {
            throw new Error(
                "Weather data is incomplete. Please try again."
            );
        }

        // Store the latest successful weather data.
        latestWeatherData = result.data;

        // Display the dashboard.
        renderWeatherDashboard();

        dashboard.hidden = false;

        statusEl.textContent =
            `Weather successfully loaded for ${latestWeatherData.location.name}.`;

    } catch (error) {

        // Ignore errors from outdated searches.
        if (requestId !== latestRequestId) {
            return;
        }

        latestWeatherData = null;
        dashboard.hidden = true;

        if (requestTimedOut) {
            statusEl.textContent =
                "The weather request timed out. Please try again.";

        } else if (error.name === "AbortError") {
            statusEl.textContent =
                "The weather request was cancelled.";

        } else if (error instanceof TypeError) {
            statusEl.textContent =
                "Unable to connect to the server. Check your internet connection and try again.";

        } else {
            statusEl.textContent =
                error.message ||
                "Something went wrong. Please try again.";
        }

    } finally {

        // Clean up the timeout.
        clearTimeout(timeoutId);

        // Only the latest request should update the button.
        if (requestId === latestRequestId) {
            searchButton.disabled = false;
            searchButton.textContent = "Search";

            activeWeatherRequest = null;
        }
    }
}


// ==========================================
// SEARCH FORM EVENT
// ==========================================

form.addEventListener("submit", (event) => {
    event.preventDefault();

    const city = cityInput.value.trim();

    if (!city) {
        statusEl.textContent =
            "Please enter a city name.";

        return;
    }

    searchWeather(city);
});


// ==========================================
// TEMPERATURE BUTTON EVENTS
// ==========================================

celsiusButton.addEventListener("click", () => {
    changeTemperatureUnit("C");
});

fahrenheitButton.addEventListener("click", () => {
    changeTemperatureUnit("F");
});
