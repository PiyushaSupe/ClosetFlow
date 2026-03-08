import requests
import random
import os
import json
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_PATH = os.path.join(BASE_DIR, "data", "users.json")


# ---------------------------------------------------
# Weather API Configuration
# ---------------------------------------------------

# You can replace this with your own API key if needed
OPENWEATHER_API_KEY = "demo"

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


# ---------------------------------------------------
# Load Users
# ---------------------------------------------------

def load_users():

    if not os.path.exists(USERS_PATH):
        return []

    with open(USERS_PATH, "r") as f:
        data = json.load(f)

    return data.get("users", [])


# ---------------------------------------------------
# Get User Location
# ---------------------------------------------------

def get_user_location(user_id):

    users = load_users()

    for user in users:

        if user["user_id"] == user_id:

            profile = user.get("profile", {})

            return profile.get("location", "Pune")

    return "Pune"


# ---------------------------------------------------
# Weather API Call
# ---------------------------------------------------

def fetch_weather(location):

    params = {
        "q": location,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:

        response = requests.get(OPENWEATHER_URL, params=params, timeout=5)

        data = response.json()

        if "main" not in data:
            raise Exception("Invalid weather data")

        return data

    except Exception:

        return None


# ---------------------------------------------------
# Weather Fallback
# ---------------------------------------------------

def fallback_weather():

    # simulate seasonal temperature
    month = datetime.now().month

    if month in [3, 4, 5]:
        return {
            "temperature": random.randint(28, 36),
            "condition": "summer"
        }

    if month in [6, 7, 8]:
        return {
            "temperature": random.randint(24, 30),
            "condition": "rain"
        }

    if month in [9, 10]:
        return {
            "temperature": random.randint(22, 30),
            "condition": "cloudy"
        }

    if month in [11, 12, 1]:
        return {
            "temperature": random.randint(10, 22),
            "condition": "winter"
        }

    return {
        "temperature": 25,
        "condition": "clear"
    }


# ---------------------------------------------------
# Parse Weather API
# ---------------------------------------------------

def parse_weather(data):

    temperature = data["main"]["temp"]

    condition = data["weather"][0]["main"].lower()

    if condition in ["rain", "drizzle"]:
        condition = "rain"

    elif condition in ["clouds"]:
        condition = "cloudy"

    elif condition in ["clear"]:
        condition = "clear"

    else:
        condition = "mixed"

    return {
        "temperature": temperature,
        "condition": condition
    }


# ---------------------------------------------------
# Public Weather Function
# ---------------------------------------------------

def get_weather(user_id=None):

    location = "Pune"

    if user_id:
        location = get_user_location(user_id)

    data = fetch_weather(location)

    if data:

        return parse_weather(data)

    return fallback_weather()


# ---------------------------------------------------
# Temperature Helper
# ---------------------------------------------------

def get_weather_temperature(user_id=None):

    weather = get_weather(user_id)

    return weather["temperature"]


# ---------------------------------------------------
# Weather Condition Helper
# ---------------------------------------------------

def get_weather_condition(user_id=None):

    weather = get_weather(user_id)

    return weather["condition"]


# ---------------------------------------------------
# Clothing Weather Suitability
# ---------------------------------------------------

def is_weather_suitable(clothing_item, temperature):

    temp_range = clothing_item.get("temperature_range", [0, 40])

    min_temp, max_temp = temp_range

    if min_temp <= temperature <= max_temp:
        return True

    return False


# ---------------------------------------------------
# Weather Score For Recommendation
# ---------------------------------------------------

def weather_score(clothing_item, temperature):

    temp_range = clothing_item.get("temperature_range", [0, 40])

    min_temp, max_temp = temp_range

    if min_temp <= temperature <= max_temp:
        return 10

    if temperature < min_temp:
        return -5

    if temperature > max_temp:
        return -5

    return 0