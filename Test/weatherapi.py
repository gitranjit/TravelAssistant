import requests

latitude = 28.6139   # Delhi
longitude = 77.2090

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": "2025-02-14",
    "end_date": "2025-02-14",
    "hourly": "precipitation,cloudcover,relativehumidity_2m,windspeed_10m",
    "timezone": "auto"
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

print("API working ✅")
print("\nHourly Weather Data:\n")
print(data["hourly"])
