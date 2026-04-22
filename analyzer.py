import numpy as np
import pandas as pd


def compute_statistics(df):
    if df.empty:
        return {}

    avg_temp = round(df["temperature"].mean(), 2)
    total_precipitation = round(df["precipitation"].sum(), 2)
    avg_precipitation = round(df["precipitation"].mean(), 2)
    rainy_days = int((df["precipitation"] > 0).sum())

    if "temperature_max" in df.columns:
        max_temp = round(df["temperature_max"].max(), 2)
    else:
        max_temp = round(df["temperature"].max(), 2)

    if "temperature_min" in df.columns:
        min_temp = round(df["temperature_min"].min(), 2)
    else:
        min_temp = round(df["temperature"].min(), 2)

    max_windspeed = round(df["windSpeed"].max(), 2)
    avg_windspeed = round(df["windSpeed"].mean(), 2)

    stats = {
        "avg_temp": avg_temp,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "total_precipitation": total_precipitation,
        "avg_precipitation": avg_precipitation,
        "max_windspeed": max_windspeed,
        "avg_windspeed": avg_windspeed,
        "rainy_days": rainy_days,
        "record_count": len(df),
    }

    return stats


def detect_anomalies(df, temp_high=None, temp_low=None, wind_thresh=None, rain_thresh=None):
    if df.empty:
        return df.copy()

    result = df.copy()

    # liczymy srednia i odchylenie standardowe dla kazdego parametru
    avg_temp = result["temperature"].mean()
    std_temp = result["temperature"].std()

    avg_wind = result["windSpeed"].mean()
    std_wind = result["windSpeed"].std()

    avg_rain = result["precipitation"].mean()
    std_rain = result["precipitation"].std()

    # jesli uzytkownik nie podal progow to liczymy automatycznie
    if temp_high is None:
        temp_high = avg_temp + 2 * std_temp
    if temp_low is None:
        temp_low = avg_temp - 2 * std_temp
    if wind_thresh is None:
        wind_thresh = avg_wind + 2 * std_wind
    if rain_thresh is None:
        rain_thresh = avg_rain + 2 * std_rain

    result["anomaly_high_temp"] = result["temperature"] > temp_high
    result["anomaly_low_temp"] = result["temperature"] < temp_low
    result["anomaly_wind"] = result["windSpeed"] > wind_thresh
    result["anomaly_rain"] = result["precipitation"] > rain_thresh

    result["is_anomaly"] = (
        result["anomaly_high_temp"] |
        result["anomaly_low_temp"] |
        result["anomaly_wind"] |
        result["anomaly_rain"]
    )

    return result


def compute_monthly_stats(df):
    if df.empty:
        return pd.DataFrame()

    result = df.copy()
    result["month"] = result["date"].dt.to_period("M")

    rows = []
    for month, group in result.groupby("month"):
        avg_temp = round(group["temperature"].mean(), 2)
        max_temp = round(group["temperature"].max(), 2)
        min_temp = round(group["temperature"].min(), 2)
        total_rain = round(group["precipitation"].sum(), 2)
        avg_wind = round(group["windSpeed"].mean(), 2)
        rainy_days = int((group["precipitation"] > 0).sum())

        rows.append({
            "month": str(month),
            "avg_temp": avg_temp,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "total_rain": total_rain,
            "avg_wind": avg_wind,
            "rainy_days": rainy_days,
        })

    return pd.DataFrame(rows)


def compute_trend(df, column="temperature"):
    if df.empty or len(df) < 3:
        return None, None

    x = np.arange(len(df))
    y = df[column].values

    # regresja liniowa - zwraca wspolczynniki wielomianu stopnia 1
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    trend_line = np.polyval(coeffs, x)

    return slope, trend_line


def compare_two_cities(df1, df2):
    stats1 = compute_statistics(df1)
    stats2 = compute_statistics(df2)
    return stats1, stats2
