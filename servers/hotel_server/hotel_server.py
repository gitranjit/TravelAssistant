# server to handle hotel bookings related requests

HOTEL_DIR = "D:\\TravelAssistant\\servers\\hotel_server"
import requests
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from typing import List

mcp = FastMCP("hotel-server")
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
            "hl": hl,        # language
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
            "search_id": search_id,
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
min_price: int,
max_price: int
):
    file_path = os.path.join(HOTEL_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        
        def price_filter(hotel):
            rate = hotel.get("rate_per_night", {})
            price = rate.get("extracted_lowest", 0)
            if min_price is not None and price < min_price:
                return False
            if max_price is not None and price > max_price:
                return False
            return True
        
        filtered_properties = [h for h in hotel_data.get("properties", []) if price_filter(h)]
        
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
        min_rating: Minimum overall rating filter value (default: 3.0)
        
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
        
        filtered_properties = []
        for hotel in hotel_data.get("properties",[]):
            if rating_filter(hotel):
                filtered_properties.append(hotel)

        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "min_rating": min_rating
            },
            "filtered_properties": filtered_properties,
            "total_filtered": len(filtered_properties)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error processing hotel data for {search_id}: {str(e)}"

@mcp.tool()
def filter_hotels_by_amenities(
    search_id: str,
    required_amenities: List[str]
) -> str:
    """
    Filter hotels from a search by required amenities.
    
    Args:
        search_id: The search ID returned from search_hotels
        required_amenities: List of required amenity names (e.g., ['Free Wi-Fi', 'Pool', 'Spa'])
        
    Returns:
        JSON string with filtered hotel results
    """
    
    file_path = os.path.join(HOTEL_DIR, f"{search_id}.json")
    
    if not os.path.exists(file_path):
        return f"No hotel search found with ID: {search_id}"
    
    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)
        
        def amenity_filter(hotel):
            hotel_amenities = hotel.get("amenities", [])
            hotel_amenities_lower = [a.lower() for a in hotel_amenities]
            return all(req.lower() in hotel_amenities_lower for req in required_amenities)
        
        filtered_properties = [h for h in hotel_data.get("properties", []) if amenity_filter(h)]
        
        result = {
            "search_id": search_id,
            "filters_applied": {
                "required_amenities": required_amenities
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

@mcp.resource("hotel_server://{search_id}")
def get_hotel_search_details(search_id: str) -> str:
    """
    Retrieve full details for a given hotel search ID.

    Args:
        search_id: Identifier of the hotel search
    """
    file_path = os.path.join(HOTEL_DIR, f"{search_id}.json")

    if not os.path.isfile(file_path):
        return f"# Hotel Search Not Found: {search_id}\n\nNo hotel search found with this ID."

    try:
        with open(file_path, "r") as f:
            hotel_data = json.load(f)

        metadata = hotel_data.get("search_metadata", {})
        properties = hotel_data.get("properties", [])
        brands = hotel_data.get("brands", [])

        content = f"# Hotel Search: {search_id}\n\n"

        # -------------------- Search Details --------------------
        content += "## Search Details\n"
        content += f"- **Location**: {metadata.get('location', 'N/A')}\n"
        content += f"- **Check-in**: {metadata.get('check_in_date', 'N/A')}\n"
        content += f"- **Check-out**: {metadata.get('check_out_date', 'N/A')}\n"

        guests = metadata.get("guests", {})
        adults = guests.get("adults", 0)
        children = guests.get("children", 0)

        content += f"- **Guests**: {adults} adults"
        if children > 0:
            content += f", {children} children"
        content += "\n"

        content += f"- **Search Type**: {metadata.get('search_type', 'hotels').title()}\n"
        content += f"- **Currency**: {metadata.get('currency', 'INR')}\n"
        content += f"- **Search Time**: {metadata.get('search_timestamp', 'N/A')}\n\n"

        # -------------------- Filters --------------------
        filters = metadata.get("filters", {})
        if any(filters.values()):
            content += "## Applied Filters\n"
            sort_map = {3: "Lowest price", 8: "Highest rating", 13: "Most reviewed"}

            if filters.get("sort_by"):
                content += f"- **Sort By**: {sort_map.get(filters['sort_by'], 'Custom')}\n"
            if filters.get("hotel_class"):
                classes = ", ".join(f"{c}-star" for c in filters["hotel_class"])
                content += f"- **Hotel Class**: {classes}\n"
            if filters.get("free_cancellation"):
                content += "- **Free Cancellation**: Yes\n"
            if filters.get("special_offers"):
                content += "- **Special Offers**: Yes\n"
            if filters.get("bedrooms"):
                content += f"- **Min Bedrooms**: {filters['bedrooms']}\n"
            content += "\n"

        # -------------------- Properties --------------------
        if properties:
            content += f"## Properties Found ({len(properties)})\n\n"

            prices, ratings = [], []

            for prop in properties[:10]:
                rate_info = prop.get("rate_per_night", {})
                lowest = rate_info.get("extracted_lowest")
                if lowest:
                    prices.append(lowest)

                rating = prop.get("overall_rating")
                if rating:
                    ratings.append(rating)

            if prices:
                content += f"**Price Range**: ${min(prices)} - ${max(prices)} per night\n"
            if ratings:
                content += f"**Rating Range**: {min(ratings):.1f} - {max(ratings):.1f} stars\n"
            content += "\n"

            for idx, prop in enumerate(properties[:5]):
                content += f"### {idx + 1}. {prop.get('name', 'N/A')}\n"
                content += f"- **Type**: {prop.get('type', 'N/A').title()}\n"

                if prop.get("hotel_class"):
                    content += f"- **Class**: {prop['hotel_class']}\n"

                rate_info = prop.get("rate_per_night", {})
                if rate_info.get("lowest"):
                    content += f"- **Rate**: {rate_info['lowest']} per night"
                    if rate_info.get("before_taxes_fees"):
                        content += f" (${rate_info['before_taxes_fees']} before taxes/fees)"
                    content += "\n"

                if prop.get("overall_rating"):
                    content += f"- **Rating**: {prop['overall_rating']:.1f}/5"
                    if prop.get("reviews"):
                        content += f" ({prop['reviews']} reviews)"
                    content += "\n"

                if prop.get("location_rating"):
                    content += f"- **Location Rating**: {prop['location_rating']:.1f}/5\n"

                amenities = prop.get("amenities", [])
                if amenities:
                    content += f"- **Amenities**: {', '.join(amenities[:5])}"
                    if len(amenities) > 5:
                        content += f" (and {len(amenities) - 5} more)"
                    content += "\n"

                if prop.get("deal"):
                    content += f"- **Deal**: {prop['deal']}\n"
                if prop.get("eco_certified"):
                    content += "- **Eco Certified**: Yes\n"
                if prop.get("sponsored"):
                    content += "- **Sponsored**: Yes\n"

                content += "\n"

       
        return content

    except json.JSONDecodeError:
        return f"# Error\n\nCorrupted hotel data for search ID: {search_id}"

@mcp.prompt()
def hotel_planning_prompt(
    destination: str,
    check_in_date: str,
    check_out_date: str,
    guests: int = 2,
    budget: str = "",
    preferences: str = "",
    hotel_type: str = "hotels"
) -> str:
    """Create a structured hotel planning prompt for Claude."""

    prompt = (
        f"Plan accommodation for a trip to {destination} "
        f"from {check_in_date} to {check_out_date} "
        f"for {guests} guest{'s' if guests != 1 else ''}."
    )

    if budget:
        prompt += f" Budget preference: {budget}."

    if preferences:
        prompt += f" Accommodation preferences: {preferences}."

    prompt += f"""

        Please assist with the following hotel planning steps:

        1. **Hotel Search**: Use the search_hotels tool to identify suitable stays:
        - Location: {destination}
        - Check-in: {check_in_date}
        - Check-out: {check_out_date}
        - Guests: {guests}
        - Type: {hotel_type}
        - Review results and highlight strong options

        2. **Hotel Evaluation**: After retrieving hotels, provide:
        - Overview of the top 5-10 properties with advantages and drawbacks
        - Pricing comparison and value insights
        - Location benefits and distance to key attractions
        - Amenities comparison
        - Rating and review observations
        - Room and stay details

        3. **Filtering and Shortlisting**: Apply appropriate filters:
        - Use filter_hotels_by_price to search hotels within specified budget
        - Use filter_hotels_by_rating to search hotels within specified rating

        4. **Property Deep Dive**: For shortlisted options:
        - Use get_property_details for in-depth data
        - Include photos, amenities, policies, and reviews
        - Note nearby attractions and transport access

        5. **Stay Recommendations**: Based on destination and preferences:
        - Suggested neighborhoods
        - Transport considerations
        - Nearby attractions and accessibility
        - Dining and entertainment around the area

        6. **Budget Guidance**: If budget is provided:
        - Cost analysis within budget
        - Suggestions for better deals
        - Alternate date advice if pricing is high
        - Additional expenses to account for (parking, resort fees)

        Present the output in a well-structured format with actionable recommendations. Start with hotel search tools, then provide analysis and final suggestions based on the findings.
        """

    return prompt

@mcp.prompt()
def hotel_comparison_prompt(search_id: str) -> str:
    """Create a prompt for in-depth hotel comparison and evaluation."""

    return f"""Analyze and compare the hotel options for search ID: {search_id}

        Provide a thorough comparison with the following steps:

        1. **Hotel Overview**:
        - Use get_hotel_details('{search_id}') to fetch the full hotel dataset

        2. **Top Recommendations**:
        - Highlight 5-8 leading hotels with detailed insights
        - Evaluate price-to-value balance
        - Compare location convenience
        - Review amenities and service quality

        3. **Comparison Table**:
        - Nightly price and total stay cost
        - Star rating and guest review scores
        - Important amenities and facilities
        - Location ratings and nearby points of interest
        - Available room types and sizes

        4. **Filtering Guidance**:
        - Use filter_hotels_by_price for economical choices
        - Use filter_hotels_by_rating for quality-focused options

        5. **Final Recommendations**:
        - Best overall value stay
        - Premium/luxury choice
        - Budget-friendly option
        - Best location advantage
        - Best amenities offering

        6. **Booking Factors**:
        - Cancellation terms and flexibility
        - Taxes and additional charges
        - Check-in and check-out timings
        - Special deals or packages
        - Seasonal pricing patterns

        7. **Neighborhood Insights**:
        - Safety and walkability
        - Distance to attractions, dining, and transport
        - Local vibe and surroundings
        - Shopping and entertainment availability

        Structure the output clearly with targeted suggestions for different traveler needs such as budget travelers, luxury seekers, families, and business travelers.
        """

if __name__ == "__main__":
    mcp.run(transport = "stdio")

