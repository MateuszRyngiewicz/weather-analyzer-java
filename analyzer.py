import numpy as np
import pandas as pd
from functools import reduce


def compute_statistics(df):
    if df.empty:
        return {}

    records = df.to_dict("records")

    # map - wyciagamy same temperatury z listy rekordow
    temperatures = list(map(lambda r: r["temperature"], records))
    precipitations = list(map(lambda r: r["precipitation"], records))
    wind_speeds = list(map(lambda r: r["windSpeed"], records))

    # filter - tylko dni z opadami
    rainy = list(filter(lambda r: r["precipitation"] > 0, records))

    # reduce - suma opadow
    total_precipitation = reduce(lambda acc, r: acc + r["precipitation"], records, 0)

    avg_temp = round(sum(temperatures) / len(temperatures), 2)
    avg_precipitation = round(total_precipitation / len(records), 2)
    avg_windspeed = round(sum(wind_speeds) / len(wind_speeds), 2)
    max_windspeed = round(max(wind_speeds), 2)

    if "temperature_max" in df.columns:
        temps_max = list(map(lambda r: r["temperature_max"], records))
        max_temp = round(max(temps_max), 2)
    else:
        max_temp = round(max(temperatures), 2)

    if "temperature_min" in df.columns:
        temps_min = list(map(lambda r: r["temperature_min"], records))
        min_temp = round(min(temps_min), 2)
    else:
        min_temp = round(min(temperatures), 2)

    stats = {
        "avg_temp": avg_temp,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "total_precipitation": round(total_precipitation, 2),
        "avg_precipitation": avg_precipitation,
        "max_windspeed": max_windspeed,
        "avg_windspeed": avg_windspeed,
        "rainy_days": len(rainy),
        "record_count": len(records),
    }

    return stats


def detect_anomalies(df, temp_high=None, temp_low=None, wind_thresh=None, rain_thresh=None):
    if df.empty:
        return df.copy()

    result = df.copy()

    avg_temp = result["temperature"].mean()
    std_temp = result["temperature"].std()
    avg_wind = result["windSpeed"].mean()
    std_wind = result["windSpeed"].std()
    avg_rain = result["precipitation"].mean()
    std_rain = result["precipitation"].std()

    if temp_high is None:
        temp_high = avg_temp + 2 * std_temp
    if temp_low is None:
        temp_low = avg_temp - 2 * std_temp
    if wind_thresh is None:
        wind_thresh = avg_wind + 2 * std_wind
    if rain_thresh is None:
        rain_thresh = avg_rain + 2 * std_rain

    # lambda do sprawdzania czy wartosc przekracza prog
    is_high_temp = lambda t: t > temp_high
    is_low_temp = lambda t: t < temp_low
    is_strong_wind = lambda w: w > wind_thresh
    is_heavy_rain = lambda r: r > rain_thresh

    result["anomaly_high_temp"] = result["temperature"].map(is_high_temp)
    result["anomaly_low_temp"] = result["temperature"].map(is_low_temp)
    result["anomaly_wind"] = result["windSpeed"].map(is_strong_wind)
    result["anomaly_rain"] = result["precipitation"].map(is_heavy_rain)

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

    def stats_for_group(group):
        records = group.to_dict("records")
        temps = list(map(lambda r: r["temperature"], records))
        rains = list(map(lambda r: r["precipitation"], records))
        winds = list(map(lambda r: r["windSpeed"], records))
        rainy = list(filter(lambda r: r["precipitation"] > 0, records))
        total_rain = reduce(lambda acc, r: acc + r["precipitation"], records, 0)

        return {
            "avg_temp": round(sum(temps) / len(temps), 2),
            "max_temp": round(max(temps), 2),
            "min_temp": round(min(temps), 2),
            "total_rain": round(total_rain, 2),
            "avg_wind": round(sum(winds) / len(winds), 2),
            "rainy_days": len(rainy),
        }

    rows = [{"month": str(month), **stats_for_group(group)}
            for month, group in result.groupby("month")]

    return pd.DataFrame(rows)


def compute_trend(df, column="temperature"):
    if df.empty or len(df) < 3:
        return None, None

    x = np.arange(len(df))
    y = df[column].values

    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    trend_line = np.polyval(coeffs, x)

    return slope, trend_line


def compare_two_cities(df1, df2):
    stats1 = compute_statistics(df1)
    stats2 = compute_statistics(df2)
    return stats1, stats2
