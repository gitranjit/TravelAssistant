# server to handle events at tourist place at related requests

import os
from typing import List, Dict, Optional, Any
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

EVENT_DIR = "D:\\TravelAssistant\\servers\\event_server"
os.makedirs(EVENT_DIR, exist_ok=True)

mcp = FastMCP("event-server")
def getApiKey():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("cannot fetch api key")
    return api_key

load_dotenv()
mcp = FastMCP("hotel-server")

@mcp.tool()
def search_events(
    query: str,
    location: Optional[str] = None,
    date_filter: Optional[str] = None,
    language: str = "en",
    country: str = "us",
    max_results: int = 20
):
    """
    Docstring to search events at a location
    
    Args: 
        query: Search query for events (e.g., "concerts", "festivals", "art shows",..)
        location: Location to search events in (e.g., "Kerla", "Rajsthan")
        date_filter: date filter (today, tomorrow, week, weekend, next_week, month, next_month)
        language: Language code (default: 'en')
        country: Country code (default: 'us')
        max_results: Maximum number of results to store (default: 20)
    
    Returns:
        Dictionary containing event search results and its metadata
    """

    try:
        api_key = getApiKey()
        search_query = query
        if location:
            search_query+=f" in {location}"
        
        params = {
            "engine": "google-events",
            "api_key" : api_key,
            "q": search_query,
            "hl": language,
            'gl': country
        }

        filters = []
        if date_filter:
            filters.append(f"date:{date_filter}")
        if filters:
            params["htichips"] = ",".join(filters)
        
        print("-----------------------")
        
        # api call to get events information from serpapi
        response = requests.get("https://serpapi.com/search", params=params)
        print(f"response: {response}")
        response.raise_for_status()
        
        event_data = response.json()

        print(event_data)

        # unique search id
        search_id = query.replace(' ','_')
        search_id+=location if location else "global"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_id += f"_{timestamp}"

        events_results = event_data.get("events_results", [])[:max_results]
        print(events_results)
        with open("D:\\TravelAssistant\\servers\\event_server\\events.json",'r') as f:
            json.dump(events_results,indent=2)
            

    except Exception as E:
        return {"error while calling event search event api"}



search_events(
    query="music concerts",
    location="Kerala, India",
    date_filter="today",
    country="in"
)
