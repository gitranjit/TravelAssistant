# TravelAssistant (MCP)

A modular **AI-powered Travel Assistant** built using **Model Context Protocol (MCP)**.  
It enables structured travel planning through dedicated MCP servers for **Flights, Hotels, Events, and Weather**.

---

## Demo

🎥 **Project Demo**  
[Watch the demo video](demo/TravelAssistant.mp4)

> Note: GitHub opens local videos in a new tab.

---

## What This Project Does

- ✈️ Search and analyze flights with pricing insights
- 🏨 Find hotels with filters (price, rating, amenities)
- 🎉 Discover local events by location and date
- 🌦️ Get travel-friendly weather summaries (past & future)

Each capability is exposed as **MCP tools, resources, and prompts**, making it easy for LLMs to reason and plan trips.

---

## Project Structure

- `servers/`
  - `flight_server.py` – Flight search & analysis
  - `hotel_server.py` – Hotel discovery & filtering
  - `event_server.py` – Event discovery
  - `weather_server.py` – Weather forecast & analysis

---

## Tech Stack

- Python
- Model Context Protocol (MCP)
- SerpAPI (Flights, Hotels, Events)
- Open-Meteo API (Weather & Geocoding)

---
