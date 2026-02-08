import requests
def get_coordinates(place: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": place, "count": 1}

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    print(f"data: {data}")

    if not data.get("results"):
        raise ValueError(f"Location not found: {place}")

    result = data["results"][0]

    

    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "resolved_name": result.get("name", place),
        "admin1": result.get("admin1", ""),
        "country": result.get("country", "")
    }

get_coordinates("jodhpur")
