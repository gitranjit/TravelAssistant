# server to handle flight related requests

# https://serpapi.com/google-flights-api

import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
# from utils import getApiKey
def getApiKey():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("cannot fetch api key")
    return api_key


api_key = getApiKey()
params = {
  'api_key': api_key,
  "engine": "google_flights",
    "departure_id": 'PNQ',
    "arrival_id": 'DEL',
    "outbound_date": '2026-03-15',
    "adults": "2",
    "children": "0",
    "type": "2",
    "currency": "INR",
    "sort_by": "Price"  # default Top flights
}

api_result = requests.get('https://serpapi.com/search', params)

api_response = api_result.json()

# dump response to file
output_file = "flight_response.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(api_response, f, indent=2, ensure_ascii=False)

