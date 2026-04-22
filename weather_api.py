import requests
import pandas as pd

# wspolrzedne geograficzne dla duńskich miast
CITY_COORDS = {
    "Copenhagen": (55.6761, 12.5683),
    "Aarhus":     (56.1629, 10.2039),
    "Odense":     (55.3959, 10.3883),
    "Aalborg":    (57.0488, 9.9187),
    "Esbjerg":    (55.4765, 8.4594),
}

def get_available_cities():
    return list(CITY_COORDS.keys())

def fetch_historical_weather(city, start_date, end_date):
    """
    Pobiera historyczne dane pogodowe z Open-Meteo Archive API.
    Zwraca DataFrame albo None jesli wystapi blad.
    """
    if city not in CITY_COORDS:
        print(f"Nieznane miasto: {city}")
        return None

    lat, lon = CITY_COORDS[city]

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "windspeed_10m_max",
        ],
        "timezone": "Europe/Copenhagen",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Blad polaczenia z API: {e}")
        return None

    daily = data.get("daily", {})
    if not daily or not daily.get("time"):
        print("API nie zwrocilo danych")
        return None

    df = pd.DataFrame({
        "date":            pd.to_datetime(daily["time"]),
        "city":            city,
        "temperature":     daily.get("temperature_2m_mean"),
        "temperature_max": daily.get("temperature_2m_max"),
        "temperature_min": daily.get("temperature_2m_min"),
        "precipitation":   daily.get("precipitation_sum"),
        "windSpeed":       daily.get("windspeed_10m_max"),
    })

    # usun wiersze gdzie brakuje glownej temparatury
    df = df.dropna(subset=["temperature"])
    df = df.fillna(0)

    return df
