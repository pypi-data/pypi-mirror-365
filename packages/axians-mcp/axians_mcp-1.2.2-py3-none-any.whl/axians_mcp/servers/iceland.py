import json
import logging
import httpx
from typing import Annotated, Any
from fastmcp import Context, FastMCP
from pydantic import Field
from requests.exceptions import HTTPError
from .utils import fetch_iceland_page


logger = logging.getLogger(__name__)

iceland_mcp = FastMCP(
    name="Iceland MCP Service",
    description="Provides tools for interacting with www.iceland-dream.com for Iceland travel information.",
)

REGION_MAP = {
    "nord": "north",
    "south": "south",
    "sud": "south",
    "east": "east",
    "est": "east",
    "west": "west",
    "ouest": "west",
    "north": "north"
}

SEASON_MAP = {
    "spring": "spring",
    "été": "summer",
    "summer": "summer",
    "automne": "autumn",
    "fall": "autumn",
    "autumn": "autumn",
    "winter": "winter",
    "hiver": "winter",
    "printemps": "spring"
}

ACCOMMODATION_MAP = {
    "camping": "camping-iceland",
    "hotel": "hotels-iceland",
    "hostel": "youth-hostels-iceland",
}



@iceland_mcp.tool(tags={"info"})
def get_iceland_info(region: str) -> dict:
    """
    Donne un aperçu touristique d'une région d'Islande.

    Args:
        region: Un point cardinal (north, south, east ou west)
    """
    region_key = REGION_MAP.get(region.lower())
    if not region_key:
        raise ValueError("Région inconnue. Utilisez north, south, east ou west.")
    
    url = f"https://www.iceland-dream.com/guide/{region_key}"
    return fetch_iceland_page(label=region_key, url=url)


@iceland_mcp.tool(tags={"info"})
def get_iceland_season_info(season: str) -> dict:
    """
    Donne des informations sur l'Islande selon la saison.

    Args:
        season: Saison à explorer (spring, summer, autumn, winter)
    """
    season_key = SEASON_MAP.get(season.lower())
    if not season_key:
        raise ValueError("Saison inconnue. Utilisez spring, summer, autumn ou winter.")
    
    url = f"https://www.iceland-dream.com/plan/whentogo/iceland-in-{season_key}"
    return fetch_iceland_page(label=season_key, url=url)

@iceland_mcp.tool(tags={"info", "accommodation"})
def get_iceland_accommodation_info(type: str) -> dict:
    """
    Donne des informations sur un type d'hébergement en Islande.

    Args:
        type: Type d'hébergement (camping, hotel, hostel)
    """
    type_key = ACCOMMODATION_MAP.get(type.lower())
    if not type_key:
        raise ValueError("Type inconnu. Utilisez camping, hotel ou hostel.")

    url = f"https://www.iceland-dream.com/plan/accommodation/{type_key}"
    return fetch_iceland_page(label=type_key, url=url)