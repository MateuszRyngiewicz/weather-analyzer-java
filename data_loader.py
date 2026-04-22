import os
import sqlite3
import pandas as pd
from weather_api import fetch_historical_weather

DB_FILE = "weather_history.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            date TEXT,
            city TEXT,
            temperature REAL,
            temperature_max REAL,
            temperature_min REAL,
            precipitation REAL,
            windSpeed REAL,
            PRIMARY KEY (date, city)
        )
    """)
    conn.commit()
    conn.close()


def save_to_db(df):
    conn = sqlite3.connect(DB_FILE)

    df_save = df.copy()
    df_save["date"] = df_save["date"].astype(str)

    for _, row in df_save.iterrows():
        try:
            conn.execute("""
                INSERT OR IGNORE INTO weather_data
                (date, city, temperature, temperature_max, temperature_min, precipitation, windSpeed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["date"], row["city"], row["temperature"],
                row["temperature_max"], row["temperature_min"],
                row["precipitation"], row["windSpeed"]
            ))
        except Exception as e:
            print(f"Blad zapisu do bazy: {e}")

    conn.commit()
    conn.close()


def load_from_db(city, start_date, end_date):
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


def load_from_csv(filepath="weather_data.csv"):
    if not os.path.exists(filepath):
        return pd.DataFrame()

    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])

    if "temperature_max" not in df.columns:
        df["temperature_max"] = df["temperature"]
    if "temperature_min" not in df.columns:
        df["temperature_min"] = df["temperature"]

    return df


def load_data(city, start_date, end_date, use_api=True):
    init_db()

    # najpierw sprawdzamy czy dane sa juz w bazie
    df_cached = load_from_db(city, start_date, end_date)
    if not df_cached.empty:
        print("Dane zaladowane z bazy danych")
        return df_cached

    # jesli nie ma w bazie to pobieramy z API
    if use_api:
        df_api = fetch_historical_weather(city, start_date, end_date)
        if df_api is not None and not df_api.empty:
            save_to_db(df_api)
            return df_api

    # ostateczny fallback - lokalny plik CSV
    print("Ladowanie danych z pliku CSV")
    df_csv = load_from_csv()
    if not df_csv.empty:
        df_filtered = df_csv[df_csv["city"].str.lower() == city.lower()]
        df_filtered = df_filtered[df_filtered["date"] >= pd.Timestamp(start_date)]
        df_filtered = df_filtered[df_filtered["date"] <= pd.Timestamp(end_date)]
        df_filtered = df_filtered.reset_index(drop=True)
        if not df_filtered.empty:
            return df_filtered

    return pd.DataFrame()
