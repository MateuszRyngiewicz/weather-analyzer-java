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

    # map - zamiana wierszy dataframe na krotki do insertu
    cols = ["date", "city", "temperature", "temperature_max", "temperature_min", "precipitation", "windSpeed"]
    rows = list(map(
        lambda r: tuple(map(lambda c: r[c], cols)),
        df_save.to_dict("records")
    ))

    for row in rows:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO weather_data
                (date, city, temperature, temperature_max, temperature_min, precipitation, windSpeed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row)
        except Exception as e:
            print(f"Blad zapisu: {e}")

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

    df_cached = load_from_db(city, start_date, end_date)
    if not df_cached.empty:
        return df_cached

    if use_api:
        df_api = fetch_historical_weather(city, start_date, end_date)
        if df_api is not None and not df_api.empty:
            save_to_db(df_api)
            return df_api

    df_csv = load_from_csv()
    if not df_csv.empty:
        # filter - tylko rekordy pasujace do miasta i zakresu dat
        records = df_csv.to_dict("records")
        filtered = list(filter(
            lambda r: r["city"].lower() == city.lower()
                and pd.Timestamp(start_date) <= r["date"] <= pd.Timestamp(end_date),
            records
        ))

        if filtered:
            return pd.DataFrame(filtered).reset_index(drop=True)

    return pd.DataFrame()
