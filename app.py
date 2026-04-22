import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

import data_loader
import analyzer
from weather_api import get_available_cities

# --- konfiguracja strony ---
st.set_page_config(
    page_title="Analizator Pogody",
    page_icon="🌤️",
    layout="wide",
)

st.title("🌤️ Analizator Danych Pogodowych")
st.caption("Historyczne dane dla duńskich miast | Źródło: Open-Meteo Archive API + lokalny dataset")
st.divider()


# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.header("⚙️ Ustawienia")

    cities = get_available_cities()
    city = st.selectbox("🏙️ Wybierz miasto", cities)

    st.subheader("📅 Zakres dat")
    col_a, col_b = st.columns(2)
    start_date = col_a.date_input("Od",  value=date(2023, 1, 1),
                                  min_value=date(2000, 1, 1), max_value=date(2026, 4, 1))
    end_date   = col_b.date_input("Do",  value=date(2023, 12, 31),
                                  min_value=date(2000, 1, 1), max_value=date(2026, 4, 1))

    if start_date > end_date:
        st.error("Data 'od' musi byc wczesniej niz data 'do'!")

    use_api = st.toggle(
        "🌐 Pobierz dane z API",
        value=True,
        help="Pobiera dane z Open-Meteo. Jesli wyłączone, używa tylko lokalnego CSV.",
    )

    st.divider()

    load_btn = st.button("📥 Załaduj dane", type="primary", use_container_width=True)

    if load_btn and start_date <= end_date:
        with st.spinner(f"Pobieranie danych dla {city}..."):
            df = data_loader.load_data(city, start_date, end_date, use_api)

        if df is None or df.empty:
            st.error("Nie udało się pobrać danych. Sprawdź połączenie z internetem lub wybierz inny zakres dat.")
        else:
            st.session_state["df"]         = df
            st.session_state["city"]       = city
            st.session_state["start_date"] = start_date
            st.session_state["end_date"]   = end_date
            st.success(f"✅ Załadowano {len(df)} rekordów!")


# =====================================================================
# BRAK DANYCH - ekran powitalny
# =====================================================================
if "df" not in st.session_state:
    st.info("👈 Wybierz ustawienia i kliknij **Załaduj dane** aby rozpocząć analizę.")

    st.markdown("""
    ### O aplikacji

    Aplikacja analizuje historyczne dane pogodowe dla duńskich miast.

    **Możliwości:**
    - 📊 Przegląd kluczowych wskaźników pogodowych
    - 📈 Interaktywne wykresy temperatur, opadów i wiatru
    - ⚠️ Automatyczne wykrywanie anomalii (metoda odchylenia standardowego)
    - 🔍 Porównywanie dwóch miast obok siebie
    - 📋 Statystyki miesięczne i eksport danych do CSV
    - 🗄️ Lokalne cache w bazie SQLite (szybkie ponowne ładowanie)

    **Źródła danych:**
    - Open-Meteo Archive API (darmowe, bez klucza API)
    - Lokalny plik `weather_data.csv` (fallback)
    """)
    st.stop()


# =====================================================================
# ZAKŁADKI
# =====================================================================
df        = st.session_state["df"]
city_name = st.session_state["city"]

tab_overview, tab_charts, tab_anomalies, tab_compare, tab_stats = st.tabs([
    "📊 Przegląd",
    "📈 Wykresy",
    "⚠️ Anomalie",
    "🔍 Porównanie miast",
    "📋 Statystyki",
])


# =====================================================================
# TAB 1 - PRZEGLĄD
# =====================================================================
with tab_overview:
    st.subheader(f"Przegląd: {city_name}")
    st.caption(f"Okres: {st.session_state['start_date']} – {st.session_state['end_date']}")

    stats = analyzer.compute_statistics(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌡️ Średnia temperatura",  f"{stats['avg_temp']:.1f}°C")
    c2.metric("🌧️ Suma opadów",           f"{stats['total_precipitation']:.1f} mm")
    c3.metric("💨 Maks. prędkość wiatru", f"{stats['max_windspeed']:.1f} km/h")
    c4.metric("☔ Dni z deszczem",        str(stats['rainy_days']))

    st.divider()

    c5, c6 = st.columns(2)
    c5.metric("🔺 Maksymalna temperatura", f"{stats['max_temp']:.1f}°C")
    c5.metric("🔻 Minimalna temperatura",  f"{stats['min_temp']:.1f}°C")
    c6.metric("💧 Średnie opady dzienne",  f"{stats['avg_precipitation']:.1f} mm")
    c6.metric("💨 Średni wiatr",           f"{stats['avg_windspeed']:.1f} km/h")

    st.divider()

    # wykres temperatury z linią trendu
    slope, trend_vals = analyzer.compute_trend(df, "temperature")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["temperature"],
        mode="lines",
        name="Temperatura średnia",
        line=dict(color="royalblue", width=2),
    ))

    if trend_vals is not None:
        direction = "rosnący" if slope > 0 else "malejący"
        fig.add_trace(go.Scatter(
            x=df["date"], y=trend_vals,
            mode="lines",
            name=f"Trend {direction} ({slope:+.4f}°C/dzień)",
            line=dict(color="red", width=1, dash="dash"),
        ))

    fig.update_layout(
        title="Temperatura w czasie z linią trendu",
        xaxis_title="Data",
        yaxis_title="Temperatura (°C)",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# TAB 2 - WYKRESY
# =====================================================================
with tab_charts:
    st.subheader("📈 Wykresy")

    chart_choice = st.radio(
        "Wybierz dane do wyświetlenia:",
        ["Temperatura", "Opady", "Wiatr", "Wszystkie"],
        horizontal=True,
    )

    if chart_choice in ("Temperatura", "Wszystkie"):
        fig_t = go.Figure()

        # zakres min-max jako wypełnienie
        if "temperature_max" in df.columns and "temperature_min" in df.columns:
            fig_t.add_trace(go.Scatter(
                x=pd.concat([df["date"], df["date"][::-1]]),
                y=pd.concat([df["temperature_max"], df["temperature_min"][::-1]]),
                fill="toself",
                fillcolor="rgba(65, 105, 225, 0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Zakres (min–max)",
            ))

        fig_t.add_trace(go.Scatter(
            x=df["date"], y=df["temperature"],
            mode="lines",
            name="Średnia temperatura",
            line=dict(color="royalblue", width=2),
        ))
        fig_t.update_layout(
            title="Temperatura dzienna",
            xaxis_title="Data",
            yaxis_title="Temperatura (°C)",
            hovermode="x unified",
        )
        st.plotly_chart(fig_t, use_container_width=True)

    if chart_choice in ("Opady", "Wszystkie"):
        fig_r = px.bar(
            df, x="date", y="precipitation",
            title="Opady dzienne",
            labels={"precipitation": "Opady (mm)", "date": "Data"},
            color="precipitation",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_r, use_container_width=True)

    if chart_choice in ("Wiatr", "Wszystkie"):
        fig_w = px.line(
            df, x="date", y="windSpeed",
            title="Prędkość wiatru",
            labels={"windSpeed": "Prędkość wiatru (km/h)", "date": "Data"},
        )
        fig_w.update_traces(line_color="seagreen")
        st.plotly_chart(fig_w, use_container_width=True)

    # mapa cieplna - tylko gdy jest wystarczajaco duzo danych
    if len(df) > 30:
        st.divider()
        st.subheader("🗓️ Mapa ciepła temperatur")

        df_heat = df.copy()
        df_heat["month"] = df_heat["date"].dt.month
        df_heat["day"]   = df_heat["date"].dt.day
        pivot = df_heat.pivot_table(values="temperature", index="month", columns="day", aggfunc="mean")

        fig_heat = px.imshow(
            pivot,
            title="Temperatura według miesiąca i dnia",
            labels=dict(x="Dzień miesiąca", y="Miesiąc", color="Temp (°C)"),
            color_continuous_scale="RdBu_r",
            aspect="auto",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # statystyki miesięczne
    st.divider()
    st.subheader("📅 Średnia temperatura miesięczna")
    monthly = analyzer.compute_monthly_stats(df)
    if not monthly.empty:
        fig_m = px.bar(
            monthly, x="month", y="avg_temp",
            title="Średnia temperatura miesięczna",
            labels={"avg_temp": "Temp. (°C)", "month": "Miesiąc"},
            color="avg_temp",
            color_continuous_scale="RdBu_r",
        )
        st.plotly_chart(fig_m, use_container_width=True)


# =====================================================================
# TAB 3 - ANOMALIE
# =====================================================================
with tab_anomalies:
    st.subheader("⚠️ Wykrywanie anomalii pogodowych")
    st.info(
        "Anomalie są wykrywane metodą odchylenia standardowego: wartości odstające "
        "o więcej niż 2σ od średniej są oznaczane jako anomalia. "
        "Możesz też ustawić własne progi."
    )

    use_custom = st.checkbox("Ustaw własne progi ręcznie")

    if use_custom:
        default_th  = df["temperature"].mean()
        default_std = df["temperature"].std()
        c1, c2, c3, c4 = st.columns(4)
        t_high = c1.number_input("Temp. wysoka (°C)", value=round(default_th + 2 * default_std, 1), step=0.5)
        t_low  = c2.number_input("Temp. niska (°C)",  value=round(default_th - 2 * default_std, 1), step=0.5)
        w_thr  = c3.number_input("Wiatr (km/h)",      value=round(df["windSpeed"].mean() + 2 * df["windSpeed"].std(), 1), step=1.0)
        r_thr  = c4.number_input("Opady (mm)",         value=round(df["precipitation"].mean() + 2 * df["precipitation"].std(), 1), step=0.5)
        df_anom = analyzer.detect_anomalies(df, t_high, t_low, w_thr, r_thr)
    else:
        df_anom = analyzer.detect_anomalies(df)

    anomalies = df_anom[df_anom["is_anomaly"]]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Łącznie anomalii",   len(anomalies))
    c2.metric("Wysoka temperatura", int(df_anom["anomaly_high_temp"].sum()))
    c3.metric("Silny wiatr",        int(df_anom["anomaly_wind"].sum()))
    c4.metric("Duże opady",         int(df_anom["anomaly_rain"].sum()))

    st.divider()

    # wykres z zaznaczonymi anomaliami
    normal = df_anom[~df_anom["is_anomaly"]]
    anom   = df_anom[df_anom["is_anomaly"]]

    fig_a = go.Figure()
    fig_a.add_trace(go.Scatter(
        x=normal["date"], y=normal["temperature"],
        mode="lines+markers",
        name="Normalne dni",
        line=dict(color="royalblue"),
        marker=dict(size=3),
    ))
    fig_a.add_trace(go.Scatter(
        x=anom["date"], y=anom["temperature"],
        mode="markers",
        name="Anomalia",
        marker=dict(color="red", size=11, symbol="x"),
    ))
    fig_a.update_layout(
        title="Temperatura – anomalie zaznaczone na czerwono",
        xaxis_title="Data",
        yaxis_title="Temperatura (°C)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_a, use_container_width=True)

    if not anomalies.empty:
        st.subheader("Lista wykrytych anomalii")
        show_cols = [c for c in [
            "date", "temperature", "precipitation", "windSpeed",
            "anomaly_high_temp", "anomaly_low_temp", "anomaly_wind", "anomaly_rain"
        ] if c in anomalies.columns]
        st.dataframe(anomalies[show_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.success("Brak wykrytych anomalii w wybranym zakresie dat.")


# =====================================================================
# TAB 4 - PORÓWNANIE MIAST
# =====================================================================
with tab_compare:
    st.subheader("🔍 Porównanie dwóch miast")

    cities_list = get_available_cities()

    c1, c2 = st.columns(2)
    city1 = c1.selectbox("Miasto 1", cities_list, index=0, key="cmp_city1")
    city2 = c2.selectbox("Miasto 2", cities_list, index=1, key="cmp_city2")

    c3, c4 = st.columns(2)
    cmp_start = c3.date_input("Zakres od", value=date(2023, 1, 1), key="cmp_start")
    cmp_end   = c4.date_input("Zakres do", value=date(2023, 12, 31), key="cmp_end")

    if st.button("🔍 Porównaj miasta", type="primary"):
        if city1 == city2:
            st.warning("Wybierz dwa różne miasta!")
        else:
            with st.spinner("Pobieranie danych..."):
                df1 = data_loader.load_data(city1, cmp_start, cmp_end, True)
                df2 = data_loader.load_data(city2, cmp_start, cmp_end, True)

            if df1.empty or df2.empty:
                st.error("Nie udało się pobrać danych dla jednego z miast.")
            else:
                s1, s2 = analyzer.compare_two_cities(df1, df2)

                # tabela porownawcza
                st.subheader("Zestawienie statystyk")
                compare_table = pd.DataFrame({
                    "Metryka": [
                        "Średnia temperatura", "Maks. temperatura", "Min. temperatura",
                        "Suma opadów", "Maks. wiatr", "Dni z deszczem", "Liczba rekordów",
                    ],
                    city1: [
                        f"{s1['avg_temp']:.1f}°C",
                        f"{s1['max_temp']:.1f}°C",
                        f"{s1['min_temp']:.1f}°C",
                        f"{s1['total_precipitation']:.1f} mm",
                        f"{s1['max_windspeed']:.1f} km/h",
                        s1['rainy_days'],
                        s1['record_count'],
                    ],
                    city2: [
                        f"{s2['avg_temp']:.1f}°C",
                        f"{s2['max_temp']:.1f}°C",
                        f"{s2['min_temp']:.1f}°C",
                        f"{s2['total_precipitation']:.1f} mm",
                        f"{s2['max_windspeed']:.1f} km/h",
                        s2['rainy_days'],
                        s2['record_count'],
                    ],
                })
                st.dataframe(compare_table, use_container_width=True, hide_index=True)

                # wykres temperatury - oba miasta
                df1_plot = df1.copy(); df1_plot["miasto"] = city1
                df2_plot = df2.copy(); df2_plot["miasto"] = city2
                df_both  = pd.concat([df1_plot, df2_plot])

                fig_cmp = px.line(
                    df_both, x="date", y="temperature",
                    color="miasto",
                    title=f"Temperatura: {city1} vs {city2}",
                    labels={"temperature": "Temperatura (°C)", "date": "Data", "miasto": "Miasto"},
                )
                st.plotly_chart(fig_cmp, use_container_width=True)

                # wykres opadow
                fig_rain = px.bar(
                    df_both, x="date", y="precipitation",
                    color="miasto", barmode="group",
                    title=f"Opady: {city1} vs {city2}",
                    labels={"precipitation": "Opady (mm)", "date": "Data", "miasto": "Miasto"},
                )
                st.plotly_chart(fig_rain, use_container_width=True)

                # wykres wiatru
                fig_wind = px.line(
                    df_both, x="date", y="windSpeed",
                    color="miasto",
                    title=f"Prędkość wiatru: {city1} vs {city2}",
                    labels={"windSpeed": "Wiatr (km/h)", "date": "Data", "miasto": "Miasto"},
                )
                st.plotly_chart(fig_wind, use_container_width=True)


# =====================================================================
# TAB 5 - STATYSTYKI
# =====================================================================
with tab_stats:
    st.subheader("📋 Szczegółowe statystyki")

    monthly = analyzer.compute_monthly_stats(df)
    if not monthly.empty:
        st.markdown("#### Agregaty miesięczne")
        st.dataframe(
            monthly.rename(columns={
                "month":      "Miesiąc",
                "avg_temp":   "Śr. temp. (°C)",
                "max_temp":   "Maks. temp. (°C)",
                "min_temp":   "Min. temp. (°C)",
                "total_rain": "Suma opadów (mm)",
                "avg_wind":   "Śr. wiatr (km/h)",
                "rainy_days": "Dni z deszczem",
            }),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("#### Surowe dane")

    search = st.text_input("🔍 Filtruj po dacie (np. 2023-06)")
    df_display = df.copy()
    if search:
        df_display = df_display[df_display["date"].astype(str).str.contains(search)]

    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

    # eksport CSV
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Pobierz dane jako CSV",
        data=csv_bytes,
        file_name=f"pogoda_{city_name}_{st.session_state['start_date']}_{st.session_state['end_date']}.csv",
        mime="text/csv",
    )
