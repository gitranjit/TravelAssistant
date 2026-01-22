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

        summary = {
            "search_id: ": search_id,
            "place": query,
            "check in date: ": check_in_date,
            "check out date: ": check_out_date,
            "adults: ": adults,
            "hotel_class: ": hotel_class,
            "total hotel results: ": len(hotel_data["properties"])
        }

        return summary

    except Exception as E:
        {"error": str(E)}


