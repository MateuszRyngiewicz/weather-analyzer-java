import os
import sqlite3
import pandas as pd
from weather_api import fetch_historical_weather

DB_FILE = "weather_history.db"

# --- baza danych SQLite ---

def init_db():
    """Tworzy tabele w bazie jesli jeszcze nie istnieja"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            date             TEXT,
            city             TEXT,
            temperature      REAL,
            temperature_max  REAL,
            temperature_min  REAL,
            precipitation    REAL,
            windSpeed        REAL,
            PRIMARY KEY (date, city)
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(df):
    """Zapisuje rekordy do bazy, duplikaty sa ignorowane"""
    conn = sqlite3.connect(DB_FILE)
    cols = ["date", "city", "temperature", "temperature_max", "temperature_min", "precipitation", "windSpeed"]
    df_save = df[cols].copy()
    df_save["date"] = df_save["date"].astype(str)

    rows = [tuple(row) for row in df_save.itertuples(index=False)]
    conn.executemany("""
        INSERT OR IGNORE INTO weather_data
        (date, city, temperature, temperature_max, temperature_min, precipitation, windSpeed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()

def load_from_db(city, start_date, end_date):
    """Wczytuje dane z lokalnej bazy SQLite"""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()

    conn = sqlite3.connect(DB_FILE)
    query = """
        SELECT * FROM weather_data
        WHERE city = ? AND date >= ? AND date <= ?
        ORDER BY date
    """
    df = pd.read_sql_query(query, conn, params=(city, str(start_date), str(end_date)))
    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

# --- pliki CSV ---

def load_from_csv(filepath="weather_data.csv"):
    """Wczytuje dane z pliku CSV (lokalny dataset)"""
    if not os.path.exists(filepath):
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])

    # dodaj kolumny max/min jesli brakuje (stary format pliku)
    if "temperature_max" not in df.columns:
        df["temperature_max"] = df["temperature"]
    if "temperature_min" not in df.columns:
        df["temperature_min"] = df["temperature"]

    return df

# --- glowna funkcja ---

def load_data(city, start_date, end_date, use_api=True):
    """
    Laduje dane pogodowe.
    Kolejnosc: baza danych (cache) -> API -> lokalny CSV.
    """
    init_db()

    # sprawdz czy mamy juz dane w bazie
    df_cached = load_from_db(city, start_date, end_date)
    if not df_cached.empty:
        return df_cached

    # pobierz z API
    if use_api:
        df_api = fetch_historical_weather(city, start_date, end_date)
        if df_api is not None and not df_api.empty:
            save_to_db(df_api)
            return df_api

    # fallback na lokalny CSV
    df_csv = load_from_csv()
    if not df_csv.empty:
        mask = (
            (df_csv["city"].str.lower() == city.lower()) &
            (df_csv["date"] >= pd.Timestamp(start_date)) &
            (df_csv["date"] <= pd.Timestamp(end_date))
        )
        result = df_csv[mask].reset_index(drop=True)
        if not result.empty:
            return result

    return pd.DataFrame()
