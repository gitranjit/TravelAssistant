# server to handle events at tourist place at related requests

import os
from typing import  Optional
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


@mcp.resource("EVENT_DIR://{search_id}")
def get_event_details(search_id:str) -> str:
    file_path = os.path.join(EVENT_DIR,f"{search_id}.json")

    if not os.path.exists(file_path):
        return f"Event Search not found for search_id {search_id}"
    try:
        with open(file_path,"r") as f:
            event_data = json.load(f)
        
        metadata = event_data.get('search_metadata',{})
        events = event_data.get('events_results',[])
        
        content = f"# Event Search: {search_id}\n\n"
        content += f"## Search Details\n"
        content += f"- **Query**: {metadata.get('query', 'N/A')}\n"
        content += f"- **Location**: {metadata.get('location', 'N/A')}\n"
        content += f"- **Date Filter**: {metadata.get('date_filter', 'None')}\n"
        content += f"- **Language**: {metadata.get('language', 'N/A')}\n"
        content += f"- **Country**: {metadata.get('country', 'N/A')}\n"
        content += f"- **Total Results**: {metadata.get('total_results', 0)}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n\n"

        if events:
            content+=f"Events Found {len(events)}\n\n"
            for i,event in events:
                content+=f"# {i+1}. {event.get('title','NA')}\n"

                date_info = event.get('date',{})
                content += f"- **When**: {date_info.get('when', 'N/A')}\n"
                    
                address = event.get('address', [])
                if address:
                    content += f"- **Address**: {', '.join(address)}\n"
                
                venue = event.get('venue', {})
                if venue:
                    content += f"- **Venue**: {venue.get('name', 'N/A')}"
                    if venue.get('rating'):
                        content += f" (Rating: {venue['rating']}/5, {venue.get('reviews', 0)} reviews)"
                    content += "\n"
                
                description = event.get('description', '')
                if description:
                    content += f"- **Description**: {description[:200]}{'...' if len(description) > 200 else ''}\n"
                
                ticket_info = event.get('ticket_info', [])
                if ticket_info:
                    content += f"- **Tickets Available**: {len(ticket_info)} sources\n"
                    for ticket in ticket_info[:2]:  # Show first 2 ticket sources
                        content += f"  - {ticket.get('source', 'N/A')}: {ticket.get('link_type', 'info')}\n"
                
                content += f"- **Event Link**: {event.get('link', 'N/A')}\n\n"
                content += "---\n\n"
        else:
            content += "No events found for this search.\n"
        
        return content
    
    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted event data for search ID: {search_id}"
    
@mcp.prompt()
def event_discovery_prompt(
    location: str,
    interests: str = "",
    date_preference: str = "",
    event_type: str = "",
    budget: str = ""
) -> str:
    """Generate a structured event search prompt for Claude."""

    prompt = f"""I want to explore interesting events happening in {location}"""

    if interests:
        prompt += f" that match my interests: {interests}"

    if date_preference:
        prompt += f" around {date_preference}"

    if event_type:
        prompt += f", mainly {event_type} events."

    if budget:
        prompt += f" My budget is roughly: {budget}."

    prompt += f"""

Please follow this process while helping me:

1. **Search for Events**:
   Use the search_events tool with:
   - Location: {location}
   - Query: {interests if interests else "events"}"""

    if date_preference:
        prompt += f"""
   - Date filter: {date_preference}"""

    if event_type:
        prompt += f"""
   - Event category: {event_type}"""

    prompt += f"""

2. **Analyze the Results**:
   After retrieving events, provide:
   - A concise summary of the most noteworthy ones
   - Grouping by type (music, festivals, art, sports, etc.)
   - Date and timing insights for easier planning
   - Venue details and accessibility notes
   - Ticket status and pricing observations

3. **Recommendations Based on My Preferences**:
   - Top 5 suggested events with clear reasoning
   - Other relevant options worth considering
   - Lesser-known or unique events
   - Timely or seasonal highlights

4. **Useful Practical Details**:
   For the recommended events, include:
   - Venue information and directions
   - Parking and transport suggestions
   - What to expect and preparation tips
   - Advice on booking tickets

5. **Planning Support**:
   Help me plan if I pick multiple events:
   - Possible mini-itineraries
   - Nearby places to eat or visit
   - Scheduling and timing advice

Start by using the event search tools, then provide detailed analysis and tailored suggestions based on the findings. Focus on events that best align with my interests and preferences.
"""

    return prompt

@mcp.prompt()
def event_comparison_prompt(search_id: str) -> str:
    """Generate a prompt for structured event comparison and analysis."""

    return f"""Review and compare the events associated with search ID: {search_id}

        Please perform a detailed evaluation using the following steps:

        1. **Retrieve Event Data**:
        Use get_event_details('{search_id}') to fetch the complete list of events.

        2. **Categorize the Events**:
        - Organize events by type (concerts, festivals, arts, sports, networking, etc.)
        - Distinguish recurring events from one-time events
        - Separate free events from paid ones

        3. **Side-by-Side Comparison**:
        - Analyze dates and timings (weekday vs weekend, morning/evening)
        - Compare venues (indoor/outdoor, size, accessibility)
        - Evaluate ticket pricing and availability
        - Note event duration and structure

        4. **Assess Quality Signals**:
        - Venue ratings and public feedback
        - Expected popularity and crowd levels
        - Organizer credibility and past event record

        5. **Apply Filtering Tools Where Helpful**:
        - filter_events_by_date for time-based preferences
        - filter_events_by_type for category-focused analysis
        - filter_events_by_venue for location preferences

        6. **Highlight Top Picks**:
        - Best value for money
        - Most distinctive or memorable events
        - Easiest to attend (location, timing, access)
        - Suitable options for different group sizes

        7. **Planning Insights**:
        - Events that can be combined within a day or weekend
        - Need for early booking
        - Weather impact for outdoor venues
        - Transport and parking considerations

        Present the findings in a well-structured format with actionable recommendations for families, couples, solo visitors, and groups.
        """


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
