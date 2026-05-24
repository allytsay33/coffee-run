"""Google Maps Platform integration helpers.

This module is intentionally isolated from Streamlit UI code. Teammates working
on API behavior can update request parameters or error handling here without
touching page layout files.
"""

import os
import plistlib
from pathlib import Path
from urllib.parse import urlencode

import requests


TAIPEI_CENTER = (25.0330, 121.5654)
IOS_GOOGLE_SERVICE_PLIST = (
    Path.home()
    / "Desktop"
    / "Coffee_Run!!"
    / "Coffee_Run!!"
    / "GoogleService-Info.plist"
)


def get_api_key(override=None):
    """Resolve the Google API key from sidebar input, env var, or iOS plist."""
    if override and override.strip():
        return override.strip()
    env_key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if env_key:
        return env_key
    return get_api_key_from_ios_project()


def get_api_key_from_ios_project():
    """Read the iOS project's GoogleService-Info.plist when available locally."""
    if not IOS_GOOGLE_SERVICE_PLIST.exists():
        return ""
    try:
        data = plistlib.loads(IOS_GOOGLE_SERVICE_PLIST.read_bytes())
    except (OSError, plistlib.InvalidFileException):
        return ""
    return str(data.get("API_KEY", "")).strip()


def search_cafes(keyword, api_key, location=TAIPEI_CENTER, radius=3500):
    """Search Google Places for cafes and normalize results for our database."""
    if not api_key:
        return []

    query = keyword.strip() or "coffee shop"
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"{query} cafe Taipei",
        "location": f"{location[0]},{location[1]}",
        "radius": radius,
        "type": "cafe",
        "language": "zh-TW",
        "key": api_key,
    }
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") not in {"OK", "ZERO_RESULTS"}:
        raise RuntimeError(payload.get("error_message") or payload.get("status"))

    cafes = []
    for item in payload.get("results", []):
        geometry = item.get("geometry", {}).get("location", {})
        open_now = item.get("opening_hours", {}).get("open_now")
        place_id = item.get("place_id")
        if not place_id:
            continue
        cafes.append(
            {
                "cafe_id": f"google-{place_id}",
                "google_place_id": place_id,
                "name": item.get("name", "未命名咖啡廳"),
                "area": infer_area(item.get("formatted_address", "")),
                "address": item.get("formatted_address", ""),
                "distance_meters": 0,
                "lat": geometry.get("lat"),
                "lng": geometry.get("lng"),
                "rating": item.get("rating", 0) or 0,
                "tags": ["Google Places", "待補充"],
                "description": "來自 Google Places 搜尋結果，可由使用者貼文補充細節。",
                "opening_hours": "詳情頁查詢",
                "open_now": int(open_now) if open_now is not None else None,
                "website": "",
                "maps_url": google_maps_url(place_id),
                "source": "google_places",
            }
        )
    return cafes


def fetch_place_details(place_id, api_key):
    """Fetch richer details for one Google Place ID."""
    if not api_key or not place_id:
        return {}

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,geometry,rating,opening_hours,website,url",
        "language": "zh-TW",
        "key": api_key,
    }
    response = requests.get(url, params=params, timeout=12)
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "OK":
        raise RuntimeError(payload.get("error_message") or payload.get("status"))

    result = payload.get("result", {})
    geometry = result.get("geometry", {}).get("location", {})
    opening_hours = result.get("opening_hours", {}).get("weekday_text", [])
    open_now = result.get("opening_hours", {}).get("open_now")
    return {
        "name": result.get("name"),
        "address": result.get("formatted_address"),
        "lat": geometry.get("lat"),
        "lng": geometry.get("lng"),
        "rating": result.get("rating", 0) or 0,
        "opening_hours": "\n".join(opening_hours),
        "open_now": int(open_now) if open_now is not None else None,
        "website": result.get("website", ""),
        "maps_url": result.get("url", google_maps_url(place_id)),
    }


def static_map_url(cafes, api_key, width=430, height=430):
    """Build a Google Static Maps URL with up to 10 cafe markers."""
    if not api_key:
        return ""

    markers = []
    for cafe in cafes:
        if cafe.get("lat") is None or cafe.get("lng") is None:
            continue
        markers.append(f"color:brown|label:C|{cafe['lat']},{cafe['lng']}")
    params = {
        "size": f"{width}x{height}",
        "scale": 2,
        "maptype": "roadmap",
        "key": api_key,
    }
    query = urlencode(params)
    marker_query = "&".join(urlencode({"markers": marker}) for marker in markers[:10])
    return f"https://maps.googleapis.com/maps/api/staticmap?{query}&{marker_query}"


def google_maps_url(place_id):
    """Build a browser link to a Google Maps place."""
    return f"https://www.google.com/maps/search/?api=1&query_place_id={place_id}"


def infer_area(address):
    """Infer a simple Taipei area label from a formatted address."""
    for area in ["大安", "信義", "中山", "中正", "萬華", "松山", "士林", "公館", "師大"]:
        if area in address:
            return area
    return "Google 搜尋"
