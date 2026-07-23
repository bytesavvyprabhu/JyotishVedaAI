import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo



_tf = TimezoneFinder()
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADER = {"User-Agent": "JyotishVedaAI/1.0"}

def geocode_place(place_name):
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1
    }
    response = requests.get(NOMINATIM_URL, params=params, headers=HEADER)
    response.raise_for_status()
    data = response.json()
    
    if not data:
        raise ValueError(f"Place '{place_name}' not found.")
    
    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    
    return lat, lon

def get_tz_offset(lat:float, lon:float, dob:str, tob:str) -> float:
    tz_name = _tf.timezone_at(lat=lat, lng=lon)
    if tz_name is None:
        raise ValueError("Could not determine timezone for the given coordinates.")
    dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    localized = dt.replace(tzinfo=ZoneInfo(tz_name))
    return localized.utcoffset().total_seconds() / 3600


def resolve_birth_Location(place:str, dob:str, tob:str) -> tuple:
    lat, lon = geocode_place(place)
    tz_offset = get_tz_offset(lat, lon, dob, tob)
    return {"latitude": lat, "longitude": lon, "timezone_offset": tz_offset}    


if __name__ == "__main__":
    print(geocode_place("Varanasi, Uttar Pradesh, India"))
    print(resolve_birth_Location("Varanasi, Uttar Pradesh, India", "1997-02-24", "17:05"))