# server to handle flight related requests

# https://serpapi.com/google-flights-api

FLIGHT_DIR = "flight"

import os
import requests
from dotenv import load_dotenv
import json
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
from datetime import datetime
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

@mcp.tool()
def search_flight(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    trip_type: int = 1,
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    travel_class: int = 1,
    currency: str = "INR",
    country: str = "in",
    language: str = "en",
    max_results: int = 10

) -> Dict[str, Any]:
    """searchs available flights for user
    Args:
        "departure_id": departure city. id eg. 'PNQ',
        "arrival_id": arrival city. id eg. 'DEL',
        "outbound_date": date of onboarding.  eg.'2026-03-15',
        "adults": "2", Number of adults. default 1
        "children": "0", Number of children , default 0
        "infants_in_seat":  Number of infants in seat (default: 0)
        "infants_on_lap": Number of infants on lap (default: 0)
        travel_class: Travel class (1=Economy, 2=Premium economy, 3=Business, 4=First)
        country: Country code for search (default: 'ind')
        language: Language code (default: 'en')
        max_results: Maximum number of results to store (default: 10)
        "type": "2", 
        "currency": "INR",
        "sort_by": "Price"
    
        Returns:
        Dictionary containing result of flight search
    """
    try:
        api_key = getApiKey()
        params = {
            "engine": "google_flights",
            "api_key":api_key,
            "departure_id":departure_id,
            "arrival_id":arrival_id,
            "outbound_date":outbound_date,
            "return_date": return_date,
            "type": trip_type,
            "adults": adults,
            "children": children,
            "infants_in_seat": infants_in_seat,
            "infants_on_lap": infants_on_lap,
            "travel_class": travel_class,
            "currency": currency,
            "country": country,
            "language": language,
            "max_results": max_results

        }
        print("couldn't executre search_flight tool")

        if trip_type == 1 and return_date:
            params["return_date"] = return_date
        elif trip_type == 1:
            return {"error: Round trip flight must have return date"}

        try:
            api_result = requests.get('https://serpapi.com/search', params)
            api_result.raise_for_status()

            flight_data = api_result.json()
        except:
            return {"error: Error while requesting API call."}
    
        os.makedirs(FLIGHT_DIR,exist_ok=True)


        search_id = f"{departure_id}_{arrival_id}_{outbound_date}"
        if return_date:
            search_id+=f"_{return_date}"
        search_id+=f"_{datetime.now()}"

        flight_filedata = {
            "search_data": {
                "search_id": search_id,
                "departure_id": departure_id,
                "arrival_id": arrival_id,
                "outbound_date": outbound_date,
                "return_date": return_date,
                "trip_type": "Round Trip" if trip_type==1 else "One Way" if trip_type==2 else "Multi City",
                "adults": adults,
                "children": children,
                "infants_in_seat": infants_in_seat,
                "infants_on_lap": infants_on_lap,
                "currency": currency
            },
            "search_results": {
                "best_flights": flight_data.get("best_flights", [])[:max_results],
                "other_flights": flight_data.get("other_flights", [])[:max_results],
                "price_insights": flight_data.get("price_insights", [])[:max_results]            
            },
        }


        flight_data_file = os.path.json(FLIGHT_DIR,f"{search_flight}.json")

        with open(flight_data_file,"w") as f:
            json.dump(flight_filedata,f,indent=2)

        summary = {
            "route": f"{departure_id} → {arrival_id}",
            "trip_type": "Round Trip" if return_date else "One Way",
            "dates": {
                "outbound": outbound_date,
                "return": return_date
            },
            "passengers": {
                "adults": adults,
                "children": children,
                "infants": infants_in_seat + infants_on_lap
            },
            "results_overview": {
                "best_flights_found": len(flight_data.get("best_flights", [])),
                "other_flights_found": len(flight_data.get("other_flights", []))
            },
            "pricing": {
                "lowest_price": flight_data.get("price_insights", {}).get("lowest_price"),
                "currency": currency,
                "price_level": flight_data.get("price_insights", {}).get("price_level"),
                "typical_range": flight_data.get("price_insights", {}).get("typical_price_range")
            }
        }

        return summary

    except Exception as e:
        return {"error": str(e)}


@mcp_tool()
def get_flight_details(search_id:str) ->str:
    """
    search flight informatio for unique search_id.

    Args:
        search_id: unique id to search flight records from {FLIGHT_DIR/search_id.json}

    Returns:
        Json string with flights information
    """
    file = os.path.join(FLIGHT_DIR,f"{search_id}.json")
    if not os.path.exist(file):
        return f"no flight with search id {search_id} found"
    try:
        with open(file,"r") as f:
            flight_data = json.load(f)
        return json.dumps(flight_data,indent=2)
    except:
        return f"Error while reading file data for search id : {search_id}"



@mpc_tool()
def filter_flights_by_price(search_id:str,min_price:Optional[float] = None,max_price:Optional[float] = None)->str:
    """
    Filters flights that costs between min_price and max_price

    Args:
        search_id: unique id to search flight records from {FLIGHT_DIR/search_id.json}
        min_price: minimum price filter (optional)
        max_price: maximum price filter (optional)

    Returns:
        Json string cotaining filtered list of flight/s
    """

    try:
        flight_path = os.path.join(FLIGHT_DIR,f"{search_id}.json")

        if not os.path.exists(flight_path):
            return "Error: can not find flight path {flight_path}"
        
        with open(flight_path,'r') as f:
            flight_data = json.load(f)

        def price_filter(flight):
            price = flight.get('price',0)

            if min_price is not None and price <min_price:
                return False
            if max_price is not None and price > max_price:
                return False
            return True
        
        filtered_best_flights = []
        filtered_other_flights = []
        for f in flight_data.get('best_flights',[]):
            if price_filter(f) == True:
                filtered_best_flights.append(f)
        
        for f in flight_data.get('other_flights',[]):
            if price_filter(f) == True:
                filtered_best_flights.append(f)
        
        result =  {
            "search_id:":search_id,
            "price_filter":{
                "min_price ": min_price,
                "max_price ": max_price
            },
            "filtered_best_flights":filtered_best_flights,
            "filtered_other_flights":filtered_other_flights,
            "total filtered flights:": len(filtered_best_flights) + len(filtered_other_flights)
        }
    
        return json.dump(result,indent=2)

    except:
        return f"Error in processing flight data for {search_id}"
        

# dump response to file
output_file = "flight_response.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(api_response, f, indent=2, ensure_ascii=False)

