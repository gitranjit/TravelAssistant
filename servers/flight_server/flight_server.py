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

# @mcp.tool()
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


# @mcp.tool()
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



#@mpc.tool()
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
        

@mpc.resource("flights://searches")
def get_flight_searches() -> str:
    """
    This resource provides list of all saved flight searches
    """
    flight_searches = []

    for filename in os.listdir(FLIGHT_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(FLIGHT_DIR,filename)
            search_id = filename[:-5]  #removing .json from filename
            try:
                with open(filepath,'r') as f:
                    flight_data = json.load(f)
                    flight_searches.append(flight_data)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Skipping invalid file {filename}: {e}")
                continue

    
    
    if len(flight_searches) == 0:
        return "Empty Flight Search List"
    content = "List of available flights \n\n"
    
    for search in flight_searches:
        current_flight_info = ""
        dep_airport_name = search.get("best_flights").get("flights").get("departure_airport").get("name")
        dep_airport_time = search.get("best_flights").get("flights").get("departure_airport","").get("time","")
        arr_airport_name = search.get("best_flights").get("flights").get("arrival_airport","").get("name","")
        arr_airport_time = search.get("best_flights").get("flights").get("arrival_airport").get("time")
        price = search.get("best_flights").get("price")
        
        current_flight_info+=f"Departure Airport: {dep_airport_name} \n"
        current_flight_info+=f"Departure date and time: {dep_airport_time} \n"
        
        if search['search_parameters'].get(type) == 1:
            current_flight_info+=f"Arrival Airport: {arr_airport_name} \n"
            current_flight_info+=f"Departure date and time: {arr_airport_time} \n"
        current_flight_info+=f"Flight Price: {price} \n"

        content+=current_flight_info
        content+="\n"
    
    return content

@mcp.resource("flights://{search_id}")
def get_flight_search_details(search_id:str) ->str:
    """
    Gives detailed flight information about perticular flight search

    Args:
        search_id: flight search id to retrive data
    """
    file_path = os.path.join(FLIGHT_DIR,f"{search_id}.json")

    if not os.path.exists(file_path):
        return "No records found for this flight id !"
    
    with open(file_path,'r') as f:
        flight_data = json.load(f)
    
    metadata = flight_data.get("search_metadata","")
    best_flights = flight_data.get("best_flights","")
    other_flights = flight_data.get("other_flights","")
    price_insights = flight_data.get("price_insights","")
    search_parameters = flight_data.get("search_parameters","")
    content = f"Here is detailed information for flight with search_id: {search_id}"
    if len(best_flights)>0:
        content+=""
        for flight in best_flights:
            dep_airport_name = best_flights.get("flights").get("departure_airport").get("name")
            dep_airport_time = best_flights.get("flights").get("departure_airport","").get("time","")
            arr_airport_name = best_flights.get("flights").get("arrival_airport","").get("name","")
            arr_airport_time = best_flights.get("flights").get("arrival_airport").get("time")
            
            price = best_flights.get("price")
            
            current_flight_info+=f"Departure Airport: {dep_airport_name} \n"
            current_flight_info+=f"Departure date and time: {dep_airport_time} \n"
            
            if search_parameters.get(type) == 1:
                current_flight_info+=f"Arrival Airport: {arr_airport_name} \n"
                current_flight_info+=f"Departure date and time: {arr_airport_time} \n"
            current_flight_info+=f"Flight Price: {price} \n"

            content+=current_flight_info
            content+="\n\n"
    
    # will add short summary about other flights
    if len(other_flights)>0:
        content+="information about other flights \nf"

        content += f"Summary of Information of Other Flights\n"
        content += f"Total other options: {len(other_flights)}\n"
        prices = [f.get("price", 0) for f in other_flights]

        content += f"Price range: {min(prices)} - {max(prices)} {metadata.get('currency', 'INR')}\n\n"



    if len(price_insights):
        content+="Flight price insights \n"
        lowest_price = price_insights.get("lowest_price","")
        typical_price_range_L = price_insights.get("typical_price_range")[0]
        typical_price_range_H = price_insights.get("typical_price_range")[1]
        
        content+=f"Lowest Price Available: {lowest_price} \n"
        content+=f"Typical Price Range: {typical_price_range_L} -> {typical_price_range_H} \n"


    return content





if __name__ == "__main__":
    # Basic smoke test
    result = search_flight(
        departure_id="PNQ",
        arrival_id="DEL",
        outbound_date="2026-03-15",
        trip_type=2,
        adults=1
    )

    print(json.dumps(result, indent=2))
