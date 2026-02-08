# server to handle weather information and alerts related requests
# support forecast upto 15 days
# API using here: https://geocoding-api.open-meteo.com

WEATHER_DIR = "D:\\TravelAssistant\\servers\\weather_server"

import os
import requests
import json
from datetime import datetime, date
from statistics import mean
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

def get_coordinates(place: str):

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": place, "count": 1}

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    if not data.get("results"):
        raise ValueError(f"Location not found: {place}")

    result = data["results"][0]

    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "resolved_name": result.get("name", place),
        "admin1": result.get("admin1", ""),
        "country": result.get("country", "")
    }


    
def analyze_hourly(hourly: dict, target_date: str):

    rain = hourly.get("rain", [])  
    cloudcover = hourly.get("cloudcover", [])
    humidity = hourly.get("relativehumidity_2m", [])
    wind = hourly.get("windspeed_10m", [])

    rainy_hours = sum(1 for p in rain if p > 0)
    rain_probability = (rainy_hours / 24) * 100 if rain else 0
    total_rain = sum(rain) if rain else 0

    avg_cloud = mean(cloudcover) if cloudcover else 0
    avg_humidity = mean(humidity) if humidity else 0
    max_wind = max(wind) if wind else 0

     # I have decided below values as per google search recommendation 

    thunderstorm = "Low"
    if avg_cloud > 70 and avg_humidity > 60: 
        thunderstorm = "Moderate"
    if avg_humidity > 70 and max_wind > 30:
        thunderstorm = "High"

    return {
        "date": target_date,
        "rain_probability_percent": round(rain_probability, 1),
        "total_rain_mm": round(total_rain, 2),
        "average_cloud_cover_percent": round(avg_cloud, 1),
        "average_humidity_percent": round(avg_humidity, 1),
        "max_wind_speed_kmh": max_wind,
        "thunderstorm_likelihood": thunderstorm
    }


@mcp.tool()
def get_weather(place: str, target_date: str) -> Dict[str, Any]:
    """
    Use this tool whenever user asks about weather
    for a specific place and date.

    - Forecast supported up to 15 days ahead.
    - Historical supported for past dates.
    """

    try:
        geo = get_coordinates(place)

        lat = geo["latitude"]
        lon = geo["longitude"]
        resolved_name = geo["resolved_name"]
        admin1 = geo["admin1"]
        country = geo["country"]

        today = date.today()
        requested_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        if requested_date > today:
            delta = (requested_date - today).days
            if delta > 15:
                return {
                    "error": "Forecast available only up to 15 days ahead."
                }
            url = "https://api.open-meteo.com/v1/forecast"
        else:
            url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": target_date,
            "end_date": target_date,
            "hourly": "rain,cloudcover,relativehumidity_2m,windspeed_10m",
            "timezone": "auto"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        hourly = data.get("hourly", {})

        summary = analyze_hourly(hourly, target_date)

        # Save raw data
        os.makedirs(WEATHER_DIR, exist_ok=True)

        search_id = f"{resolved_name}_{target_date}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_path = os.path.join(WEATHER_DIR, f"{search_id}.json")

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        summary.update({
            "search_id": search_id,
            "location": resolved_name,
            "state_or_region": admin1,
            "country": country,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            }
        })

        return summary

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_weather_details(search_id: str) -> str:

    file_path = os.path.join(WEATHER_DIR, f"{search_id}.json")

    if not os.path.exists(file_path):
        return f"No weather record found for {search_id}"

    with open(file_path, "r") as f:
        return json.dumps(json.load(f), indent=2)



@mcp.resource("weather://searches")
def list_weather_searches() -> str:

    if not os.path.exists(WEATHER_DIR):
        return "No weather searches found."

    files = [f[:-5] for f in os.listdir(WEATHER_DIR) if f.endswith(".json")]

    if not files:
        return "No weather searches found."

    return "Saved Weather Searches:\n\n" + "\n".join(files)


@mcp.prompt()
def weather_analysis_prompt(destination: str, travel_date: str) -> str:

    return f"""
    You must use get_weather tool first.

    Analyze weather for {destination} on {travel_date}.
    Provide:
    - Rain probability
    - Thunderstorm likelihood
    - Wind & humidity comfort
    - Travel advice
    """


if __name__ == "__main__":
    mcp.run(transport="stdio")
