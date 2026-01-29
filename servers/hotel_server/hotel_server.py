# server to handle hotel bookings related requests

HOTEL_DIR = "D:\\TravelAssistant\\servers\\hotel_server"
import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP

def getApiKey():
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("cannot fetch api key")
    return api_key

load_dotenv()
mcp = FastMCP("hotel-server")

@mcp.tool()
def search_hotel(
    query,
    check_in_date,
    check_out_date,
    engine = "google_hotels",
    currency = "INR",
    hl = "en",
    adults = 2,
    sort_by = 8,
    hotel_class = 2
):
    """
    Docstring for search_hotel
    
    q: search query for hotels
    check_in_date: hotel check in date
    check_out_date: hotel check out date
    engine: search engine
    currency: currency code (INR for india)
    hl: language code (en for english)
    adults: number of adults (default is 2)
    sort_by: result sort criteria (3-> sort by lowest price, 8-> sort by highest rating, 13 -> sort by most viewed)
    hotel_class: (2,3,4,5) hotel start (2 star,3 star,...)
    """

    try:
        api_key = getApiKey()
        params = {
            "q" : query,
            "check_in_date" : check_in_date,
            "check_out_date" : check_out_date,
            "engine" : engine,
            "currency" : currency,
            "hl": "en",        # language
            "adults": adults,
            "sort_by":sort_by,
            "hotel_class" : hotel_class,
            "api_key" : api_key
        }


        search_id = f"{check_in_date}_{check_out_date}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_id += f"_{timestamp}"

        api_result = requests.get('https://serpapi.com/search', params)
        api_result.raise_for_status()

        hotel_data = api_result.json()
 

        jsonfile = os.path.join(HOTEL_DIR,f"{search_id}.json")
        with open(jsonfile,"w") as f:
            json.dump(hotel_data,f,indent=2)
        
        max_results = hotel_data.get("search_information").get("total_results")

        summary = {
            "search_metadata":{
                "search_id: ": search_id,
                "place": query,
                "check in date: ": check_in_date,
                "check out date: ": check_out_date,
                "adults: ": adults,
                "hotel_class: ": hotel_class,
                "total hotel results: ": len(hotel_data["properties"])
            },
            "properties": hotel_data.get("properties", [])[:max_results],
            
        }

        return summary

    except Exception as E:
        {"error": str(E)}


@mcp.tool()
def filter_hotel_by_price(
search_id,
min_price,
max_price
):
    try:
        jsonpath = os.path.join(HOTEL_DIR,f"{search_id}.json")
        with open(jsonpath,"r") as f:
            hotel_data = json.load(jsonpath)
        
        properties = hotel_data["properties"]
        for property in properties:
            
            def price_filter(property):
                rate = property.get("rate_per_night",None)
                if rate!=None:
                    if rate>=min_price and rate<=max_price:
                        return True
                    else:
                        return False
                return True
            
            filtered_properties = [p for p in hotel_data.get("properties", []) if price_filter(p)]

            result = {
                "search_id": search_id,
                "filters_applied": {
                    "min_price": min_price,
                    "max_price": max_price
                },
                "filtered_properties": filtered_properties,
                "total_filtered": len(filtered_properties)
            }
            
            return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing hotel data for {search_id}: {str(e)}"
    

@mcp.tool()
def filter_hotels_by_rating(
    search_id: str,
    min_rating: float = 3.0
) -> str:
    """
    Filter hotels from a search by minimum rating.
    
    Args:
        search_id: The search ID returned from search_hotels
        min_rating: Minimum overall rating filter (default: 3.0)
        
    Returns:
        JSON string with filtered hotel results
    """
    
    file_path = os.path.join(HOTEL_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        
        def rating_filter(hotel):
            rating = hotel.get("overall_rating", 0)
            return rating >= min_rating
        
        filtered_properties = [h for h in hotel_data.get("properties", []) if rating_filter(h)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "min_rating": min_rating
            },
            "filtered_properties": filtered_properties,
            "total_filtered": len(filtered_properties)
        }
        
        return json.dumps(result, indent=2)
        
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error processing hotel data for {search_id}: {str(e)}"

@mcp.tool()
def get_property_details(
    property_token: str,
    currency: str = "INR",
    country: str = "in",
    language: str = "en"
) -> str:
    """
    Get detailed information about a specific property using its token.
    
    Args:
        property_token: The property token from hotel search results
        currency: Currency for prices (default: 'INR')
        country: Country code for search (default: 'in')
        language: Language code (default: 'en')
        
    Returns:
        JSON string with detailed property information
    """
    
    try:
        api_key = getApiKey()
        
        params = {
            "engine": "google_hotels",
            "api_key": api_key,
            "property_token": property_token,
            "currency": currency,
            "gl": country,
            "hl": language
        }
        
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        
        property_data = response.json()
        return json.dumps(property_data, indent=2)
        
    except Exception as e:
        return f"Unexpected error: {str(e)}"


