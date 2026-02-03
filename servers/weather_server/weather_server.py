# server to handle weather information and alerts related requests

WEATHER_DIR = "D:\\TravelAssistant\\flight_server"

import os
import requests
from dotenv import load_dotenv
import json
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
from datetime import datetime

mcp = FastMCP("weather-server")

