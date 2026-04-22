import numpy as np
import pandas as pd


def compute_statistics(df):
    """Oblicza podstawowe statystyki dla zbioru rekordow pogodowych"""
    if df.empty:
        return {}

    max_col = "temperature_max" if "temperature_max" in df.columns else "temperature"
    min_col = "temperature_min" if "temperature_min" in df.columns else "temperature"

    stats = {
        "avg_temp":           round(df["temperature"].mean(), 2),
        "max_temp":           round(df[max_col].max(), 2),
        "min_temp":           round(df[min_col].min(), 2),
        "total_precipitation": round(df["precipitation"].sum(), 2),
        "avg_precipitation":  round(df["precipitation"].mean(), 2),
        "max_windspeed":      round(df["windSpeed"].max(), 2),
        "avg_windspeed":      round(df["windSpeed"].mean(), 2),
        "rainy_days":         int((df["precipitation"] > 0).sum()),
        "record_count":       len(df),
    }
    return stats


def detect_anomalies(df, temp_high=None, temp_low=None, wind_thresh=None, rain_thresh=None):
    """
    Wykrywa anomalie pogodowe.
    Jesli progi nie sa podane, oblicza je automatycznie na podstawie
    sredniej ± 2 odchylenia standardowego.
    """
    if df.empty:
        return df.copy()

    result = df.copy()

    mean_t  = result["temperature"].mean()
    std_t   = result["temperature"].std()
    mean_w  = result["windSpeed"].mean()
    std_w   = result["windSpeed"].std()
    mean_r  = result["precipitation"].mean()
    std_r   = result["precipitation"].std()

    if temp_high is None:
        temp_high = mean_t + 2 * std_t
    if temp_low is None:
        temp_low = mean_t - 2 * std_t
    if wind_thresh is None:
        wind_thresh = mean_w + 2 * std_w
    if rain_thresh is None:
        rain_thresh = mean_r + 2 * std_r

    result["anomaly_high_temp"] = result["temperature"] > temp_high
    result["anomaly_low_temp"]  = result["temperature"] < temp_low
    result["anomaly_wind"]      = result["windSpeed"] > wind_thresh
    result["anomaly_rain"]      = result["precipitation"] > rain_thresh
    result["is_anomaly"] = (
        result["anomaly_high_temp"] |
        result["anomaly_low_temp"]  |
        result["anomaly_wind"]      |
        result["anomaly_rain"]
    )

    return result


def compute_monthly_stats(df):
    """Grupuje dane po miesiacach i oblicza agregaty"""
    if df.empty:
        return pd.DataFrame()

    tmp = df.copy()
    tmp["month"] = tmp["date"].dt.to_period("M")

    monthly = tmp.groupby("month").agg(
        avg_temp    = ("temperature",   "mean"),
        max_temp    = ("temperature",   "max"),
        min_temp    = ("temperature",   "min"),
        total_rain  = ("precipitation", "sum"),
        avg_wind    = ("windSpeed",     "mean"),
        rainy_days  = ("precipitation", lambda x: int((x > 0).sum())),
    ).reset_index()

    monthly["month"] = monthly["month"].astype(str)
    monthly = monthly.round(2)
    return monthly


def compute_trend(df, column="temperature"):
    """
    Oblicza trend liniowy dla wybranej kolumny.
    Zwraca wspolczynnik kierunkowy i wartosci linii trendu.
    """
    if df.empty or len(df) < 3:
        return None, None

    x = np.arange(len(df))
    y = df[column].values

    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    trend_line = np.polyval(coeffs, x)

    return slope, trend_line


def compare_two_cities(df1, df2):
    """Porownuje statystki dwoch zbiorow danych (dwa rozne miasta)"""
    return compute_statistics(df1), compute_statistics(df2)
