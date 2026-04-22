import requests
import pandas as pd

# wspolrzedne geograficzne dunskich miast
CITY_COORDS = {
    "Copenhagen": (55.6761, 12.5683),
    "Aarhus": (56.1629, 10.2039),
    "Odense": (55.3959, 10.3883),
    "Aalborg": (57.0488, 9.9187),
    "Esbjerg": (55.4765, 8.4594),
}


def get_available_cities():
    return list(CITY_COORDS.keys())


def fetch_historical_weather(city, start_date, end_date):
    if city not in CITY_COORDS:
        print(f"Nieznane miasto: {city}")
        return None

    lat = CITY_COORDS[city][0]
    lon = CITY_COORDS[city][1]

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
    except Exception as e:
        print(f"Blad polaczenia z API: {e}")
        return None

    daily = data.get("daily", {})
    if not daily or not daily.get("time"):
        print("API nie zwrocilo danych")
        return None

    dates = daily["time"]
    temps_mean = daily.get("temperature_2m_mean")
    temps_max = daily.get("temperature_2m_max")
    temps_min = daily.get("temperature_2m_min")
    precipitation = daily.get("precipitation_sum")
    windspeed = daily.get("windspeed_10m_max")

    df = pd.DataFrame({
        "date": pd.to_datetime(dates),
        "city": city,
        "temperature": temps_mean,
        "temperature_max": temps_max,
        "temperature_min": temps_min,
        "precipitation": precipitation,
        "windSpeed": windspeed,
    })

    df = df.dropna(subset=["temperature"])
    df = df.fillna(0)

    return df
