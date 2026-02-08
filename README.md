TravelAssistant (MCP-based)

A modular Travel Assistant built using Model Context Protocol (MCP).
It provides structured tools for flights, hotels, events, and weather to support end-to-end travel planning with LLMs.

Features

✈️ Flight Search & Analysis

One-way / round-trip flights

Price insights and filtering

🏨 Hotel Search

Filter by price, rating, amenities

Property-level details

🎉 Event Discovery

Location-based events

Date filtering and comparisons

🌦️ Weather Forecast

Historical + up to 15-day forecast

Travel-friendly summaries

Architecture

Each capability runs as an independent MCP server:

servers/
 ├── flight_server.py
 ├── hotel_server.py
 ├── event_server.py
 └── weather_server.py


All servers expose:

MCP tools

MCP resources

MCP prompts
for easy orchestration by an LLM.

Setup

Clone the repo

Install dependencies

pip install -r requirements.txt


Create a .env file

SERPAPI_KEY=your_api_key_here


Run any server

python flight_server.py

APIs Used

SerpAPI – Flights, Hotels, Events

Open-Meteo – Weather & Geocoding



Notes

No hardcoded location data

Designed for extensibility

Suitable for agent-based travel planners
