import os

def getApiKey():
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        raise ValueError("cannot fetch api key")
    return api_key

