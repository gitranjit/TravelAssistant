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
            "engine": "google_events",
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
        
        processed_results = {
            "search_metadata": {
                "search_id": search_id,
                "query": query,
                "location": location,
                "date_filter": date_filter,
                "language": language,
                "country": country,
                "search_timestamp": datetime.now().isoformat(),
                "total_results": len(events_results)
            },
            "search_parameters": event_data.get("search_parameters", {}),
            "search_information": event_data.get("search_information", {}),
            "events_results": events_results
        }

        event_path = os.path.join(EVENT_DIR,f"{search_id}.json")
        with open(event_path, "w") as f:
            json.dump(processed_results, f, indent=2)


        summary = {
            "search_id": search_id,
            "total_events": len(events_results),
            "query": query,
            "location": location,
            "filters_applied": {
                "date_filter": date_filter,
            },
            "sample_events": [
                {
                    "title": event.get("title", "N/A"),
                    "date": event.get("date", {}).get("when", "N/A"),
                    "venue": event.get("venue", {}).get("name", "N/A") if event.get("venue") else "N/A"
                } for event in events_results[:3]
            ],
            "search_parameters": processed_results["search_metadata"]
        }

        return summary

    except Exception as E:
        return {"error while calling event search event api"}


@mcp.tool()
def get_event_details(search_id: str) -> str:
    """
    Get detailed information about a specific event search.
    
    Args:
        search_id: The search ID to search events for
        
    Returns:
        JSON string with detailed event information
    """
    
    file_path = os.path.join(EVENT_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No event search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            event_data = json.load(f)
        return json.dumps(event_data, indent=2)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading event data for {search_id}: {str(e)}"


@mcp.tool()
def filter_events_by_date(
    search_id: str,
    date_range: Optional[str] = None,
    specific_date: Optional[str] = None
) -> str:
    """
    Filter events from a search by date criteria.
    
    Args:
        search_id: The search ID returned from search_events
        date_range: Date range filter (today, tomorrow, week, weekend, next_week, month)
        specific_date: Filter by specific date (YYYY-MM-DD format)
        
    Returns:
        JSON string with filtered event results
    """
    
    file_path = os.path.join(EVENT_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No event search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            event_data = json.load(f)
        
        events = event_data.get("events_results", [])
        filtered_events = []
        
        for event in events:
            event_date = event.get("date", {})
            if date_range:
                if date_range.lower() in event_date.get("when", "").lower():
                    filtered_events.append(event)
            elif specific_date:
                if specific_date in event_date.get("when", ""):
                    filtered_events.append(event)
            else:
                filtered_events.append(event)
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "date_range": date_range,
                "specific_date": specific_date
            },
            "filtered_events": filtered_events,
            "total_filtered": len(filtered_events)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing event data for {search_id}: {str(e)}"


search_events(
    query="",
    location="Kerala, India",
    date_filter="today",
    country="in"
)
