import requests
from datetime import date, datetime
import json
import os

# --- Zodiac Mapping (used only if not using API) ---
ZODIAC_SIGNS = [
    ("Capricorn", (date(2000, 12, 22), date(2001, 1, 19))),
    ("Aquarius", (date(2000, 1, 20), date(2000, 2, 18))),
    ("Pisces", (date(2000, 2, 19), date(2000, 3, 20))),
    ("Aries", (date(2000, 3, 21), date(2000, 4, 19))),
    ("Taurus", (date(2000, 4, 20), date(2000, 5, 20))),
    ("Gemini", (date(2000, 5, 21), date(2000, 6, 20))),
    ("Cancer", (date(2000, 6, 21), date(2000, 7, 22))),
    ("Leo", (date(2000, 7, 23), date(2000, 8, 22))),
    ("Virgo", (date(2000, 8, 23), date(2000, 9, 22))),
    ("Libra", (date(2000, 9, 23), date(2000, 10, 22))),
    ("Scorpio", (date(2000, 10, 23), date(2000, 11, 21))),
    ("Sagittarius", (date(2000, 11, 22), date(2000, 12, 21))),
]

def get_sun_sign(dob):
    dob_2000 = dob.replace(year=2000)
    for sign, (start, end) in ZODIAC_SIGNS:
        if start <= dob_2000 <= end:
            return sign
    return "Capricorn"

# --- API Token Fetch ---
def get_prokerala_token(client_id, client_secret):
    response = requests.post("https://api.prokerala.com/token", data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    })
    response.raise_for_status()
    return response.json()["access_token"]

# --- Daily Horoscope via Sun Sign ---
def get_horoscope_api(sign):
    if not sign:
        return {
            "description": "Sun sign not found.",
            "sign": "Unknown",
            "date": "N/A",
            "source": "Fallback"
        }

    creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credit.json"))
    with open(creds_path) as f:
        creds = json.load(f)

    try:
        token = get_prokerala_token(creds["client_id"], creds["client_secret"])
    except Exception as e:
        print("⚠️ Token fetch error:", e)
        return {"error": "Unable to authenticate with Prokerala API."}

    url = "https://api.prokerala.com/v1/astrology/sun-sign-prediction"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"sign": sign.lower()}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        return {
            "description": data["data"]["prediction"],
            "sign": sign,
            "date": data["meta"]["date"],
            "source": "Prokerala Sun Sign Prediction"
        }

    except Exception as e:
        print("⚠️ Horoscope fetch error:", e)
        return {
            "description": "Could not retrieve horoscope.",
            "sign": sign,
            "date": "N/A",
            "source": "Fallback"
        }


# --- Geolocation (Place to Coordinates) ---
def get_coordinates(place):
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": "MythicPersona/1.0"})
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError("Place not found")
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print("🌍 Location error:", e)
        return None, None

# --- Full Astrological Profile (Sun, Moon, Lagna, Nakshatra) ---
def get_birth_profile(dob, tob, place, timezone="+05:30"):
    creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credit.json"))
    with open(creds_path) as f:
        creds = json.load(f)

    try:
        token = get_prokerala_token(creds["client_id"], creds["client_secret"])
    except Exception as e:
        print("⚠️ Token error:", e)
        return {"error": "Token generation failed."}

    lat, lon = get_coordinates(place)
    if not lat or not lon:
        return {"error": "Invalid location. Coordinates not found."}

    dt = datetime.combine(dob, tob).strftime("%Y-%m-%dT%H:%M:%S")
    url = "https://api.prokerala.com/v2/astrology/birth-details"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {
    "datetime": f"{dt}{timezone}",
    "coordinates": f"{lat:.2f},{lon:.2f}",
    "ayanamsa": 1
}


    try:
        response = requests.get(url, headers=headers, params=params)
        print("✅ API Response Status:", response.status_code)
        print("✅ Raw JSON:", response.text)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})  # ✅ Only return the inner data dictionary

    except Exception as e:
        print("⚠️ Profile fetch error:", e)
        return {"error": "Failed to get astrological profile."}
