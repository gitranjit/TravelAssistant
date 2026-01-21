import requests
import os

API_KEY = "2a346a04abf0b8892ae8d1e182d92f8de1e6a44f46b9deb40bc80f5502c5d765"

params = {
    "engine": "google_flights",
    "api_key": API_KEY,
    "departure_id": "PNQ",
    "arrival_id": "JAI",
    "outbound_date": "2026-03-10",
    "return_date": "2026-03-16",
    "type": 1,  # round trip
    "adults": 1,
    "currency": "INR",
    "country": "in",
    "language": "en",
    "max_results": 5
}

response = requests.get("https://serpapi.com/search", params=params)

print("HTTP status:", response.status_code)
print("Response text (first 500 chars):")
print(response.text[:500])
