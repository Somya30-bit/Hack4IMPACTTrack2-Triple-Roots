import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather_forecast(city):
    if not API_KEY:
        print("Weather error: OPENWEATHER_API_KEY is not set.")
        return None

    city = (city or "").strip()

    if not city:
        print("Weather error: city name is empty.")
        return None

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if "list" in data and len(data["list"]) > 0:
                return data

            print("Weather error: forecast data missing in API response.")
            return None

        print("Weather API error:", response.status_code, response.text)
        return None

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return None