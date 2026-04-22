import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

import data_loader
import analyzer
from weather_api import get_available_cities


st.set_page_config(page_title="Analizator Pogody", layout="wide")
st.title("Analizator Danych Pogodowych")
st.caption("Historyczne dane dla dunskich miast - Open-Meteo Archive API")
st.divider()


# sidebar z ustawieniami
with st.sidebar:
    st.header("Ustawienia")

    cities = get_available_cities()
    city = st.selectbox("Wybierz miasto", cities)

    st.subheader("Zakres dat")
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Od", value=date(2023, 1, 1), min_value=date(2000, 1, 1), max_value=date(2026, 4, 1))
    end_date = col2.date_input("Do", value=date(2023, 12, 31), min_value=date(2000, 1, 1), max_value=date(2026, 4, 1))

    if start_date > end_date:
        st.error("Data poczatkowa musi byc wczesniejsza niz koncowa!")

    use_api = st.checkbox("Pobierz dane z API", value=True)

    st.divider()

    load_btn = st.button("Zaladuj dane", type="primary", use_container_width=True)

    if load_btn and start_date <= end_date:
        with st.spinner(f"Pobieranie danych dla {city}..."):
            df = data_loader.load_data(city, start_date, end_date, use_api)

        if df is None or df.empty:
            st.error("Nie udalo sie pobrac danych.")
        else:
            st.session_state["df"] = df
            st.session_state["city"] = city
            st.session_state["start_date"] = start_date
            st.session_state["end_date"] = end_date
            st.success(f"Zaladowano {len(df)} rekordow!")


# ekran startowy gdy nie ma danych
if "df" not in st.session_state:
    st.info("Wybierz ustawienia i kliknij Zaladuj dane aby rozpoczac analize.")
    st.markdown("""
    ### O aplikacji

    Aplikacja analizuje historyczne dane pogodowe dla dunskich miast.

    **Mozliwosci:**
    - Przeglad kluczowych wskaznikow pogodowych
    - Interaktywne wykresy temperatur, opadow i wiatru
    - Automatyczne wykrywanie anomalii (metoda odchylenia standardowego)
    - Porownywanie dwoch miast obok siebie
    - Statystyki miesieczne i eksport danych do CSV
    - Cache w bazie SQLite - szybkie ponowne ladowanie

    **Zrodla danych:**
    - Open-Meteo Archive API (darmowe, bez klucza API)
    - Lokalny plik weather_data.csv (fallback gdy brak internetu)
    """)
    st.stop()


df = st.session_state["df"]
city_name = st.session_state["city"]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Przeglad",
    "Wykresy",
    "Anomalie",
    "Porownanie miast",
    "Statystyki",
])


# --- TAB 1: PRZEGLAD ---
with tab1:
    st.subheader(f"Przeglad: {city_name}")
    st.caption(f"Okres: {st.session_state['start_date']} - {st.session_state['end_date']}")

    stats = analyzer.compute_statistics(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Srednia temperatura", f"{stats['avg_temp']:.1f} C")
    col2.metric("Suma opadow", f"{stats['total_precipitation']:.1f} mm")
    col3.metric("Maks. predkosc wiatru", f"{stats['max_windspeed']:.1f} km/h")
    col4.metric("Dni z deszczem", str(stats['rainy_days']))

    st.divider()

    col5, col6 = st.columns(2)
    col5.metric("Maksymalna temperatura", f"{stats['max_temp']:.1f} C")
    col5.metric("Minimalna temperatura", f"{stats['min_temp']:.1f} C")
    col6.metric("Srednie opady dzienne", f"{stats['avg_precipitation']:.1f} mm")
    col6.metric("Sredni wiatr", f"{stats['avg_windspeed']:.1f} km/h")

    st.divider()

    slope, trend_vals = analyzer.compute_trend(df, "temperature")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["temperature"],
        mode="lines",
        name="Temperatura srednia",
        line=dict(color="royalblue", width=2),
    ))

    if trend_vals is not None:
        if slope > 0:
            kierunek = "rosnacy"
        else:
            kierunek = "malejacy"

        fig.add_trace(go.Scatter(
            x=df["date"],
            y=trend_vals,
            mode="lines",
            name=f"Trend {kierunek} ({slope:+.4f} C/dzien)",
            line=dict(color="red", width=1, dash="dash"),
        ))

    fig.update_layout(
        title="Temperatura w czasie z linia trendu",
        xaxis_title="Data",
        yaxis_title="Temperatura (C)",
    )
    st.plotly_chart(fig, use_container_width=True)


# --- TAB 2: WYKRESY ---
with tab2:
    st.subheader("Wykresy")

    chart_choice = st.radio(
        "Wybierz dane:",
        ["Temperatura", "Opady", "Wiatr", "Wszystkie"],
        horizontal=True,
    )

    if chart_choice == "Temperatura" or chart_choice == "Wszystkie":
        fig_temp = go.Figure()

        if "temperature_max" in df.columns and "temperature_min" in df.columns:
            fig_temp.add_trace(go.Scatter(
                x=pd.concat([df["date"], df["date"][::-1]]),
                y=pd.concat([df["temperature_max"], df["temperature_min"][::-1]]),
                fill="toself",
                fillcolor="rgba(65, 105, 225, 0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                name="Zakres min-max",
            ))

        fig_temp.add_trace(go.Scatter(
            x=df["date"],
            y=df["temperature"],
            mode="lines",
            name="Srednia temperatura",
            line=dict(color="royalblue", width=2),
        ))
        fig_temp.update_layout(title="Temperatura dzienna", xaxis_title="Data", yaxis_title="Temperatura (C)")
        st.plotly_chart(fig_temp, use_container_width=True)

    if chart_choice == "Opady" or chart_choice == "Wszystkie":
        fig_rain = px.bar(
            df, x="date", y="precipitation",
            title="Opady dzienne",
            labels={"precipitation": "Opady (mm)", "date": "Data"},
            color="precipitation",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig_rain, use_container_width=True)

    if chart_choice == "Wiatr" or chart_choice == "Wszystkie":
        fig_wind = px.line(
            df, x="date", y="windSpeed",
            title="Predkosc wiatru",
            labels={"windSpeed": "Predkosc wiatru (km/h)", "date": "Data"},
        )
        fig_wind.update_traces(line_color="seagreen")
        st.plotly_chart(fig_wind, use_container_width=True)

    # mapa cieplna - tylko przy wiekszym zakresie dat
    if len(df) > 30:
        st.divider()
        st.subheader("Mapa ciepla temperatur")

        df_heat = df.copy()
        df_heat["month"] = df_heat["date"].dt.month
        df_heat["day"] = df_heat["date"].dt.day
        pivot = df_heat.pivot_table(values="temperature", index="month", columns="day", aggfunc="mean")

        fig_heat = px.imshow(
            pivot,
            title="Temperatura wedlug miesiaca i dnia",
            labels=dict(x="Dzien miesiaca", y="Miesiac", color="Temp (C)"),
            color_continuous_scale="RdBu_r",
            aspect="auto",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()
    st.subheader("Srednia temperatura miesieczna")
    monthly = analyzer.compute_monthly_stats(df)
    if not monthly.empty:
        fig_monthly = px.bar(
            monthly, x="month", y="avg_temp",
            title="Srednia temperatura miesieczna",
            labels={"avg_temp": "Temp. (C)", "month": "Miesiac"},
            color="avg_temp",
            color_continuous_scale="RdBu_r",
        )
        st.plotly_chart(fig_monthly, use_container_width=True)


# --- TAB 3: ANOMALIE ---
with tab3:
    st.subheader("Wykrywanie anomalii pogodowych")
    st.info("Anomalie sa wykrywane metoda odchylenia standardowego: wartosci odstajace o wiecej niz 2 odchylenia od sredniej.")

    use_custom = st.checkbox("Ustaw wlasne progi")

    if use_custom:
        avg_t = df["temperature"].mean()
        std_t = df["temperature"].std()
        col1, col2, col3, col4 = st.columns(4)
        t_high = col1.number_input("Temp. wysoka (C)", value=round(avg_t + 2 * std_t, 1), step=0.5)
        t_low = col2.number_input("Temp. niska (C)", value=round(avg_t - 2 * std_t, 1), step=0.5)
        w_thr = col3.number_input("Wiatr (km/h)", value=round(df["windSpeed"].mean() + 2 * df["windSpeed"].std(), 1), step=1.0)
        r_thr = col4.number_input("Opady (mm)", value=round(df["precipitation"].mean() + 2 * df["precipitation"].std(), 1), step=0.5)
        df_anom = analyzer.detect_anomalies(df, t_high, t_low, w_thr, r_thr)
    else:
        df_anom = analyzer.detect_anomalies(df)

    anomalies = df_anom[df_anom["is_anomaly"]]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lacznie anomalii", len(anomalies))
    col2.metric("Wysoka temperatura", int(df_anom["anomaly_high_temp"].sum()))
    col3.metric("Silny wiatr", int(df_anom["anomaly_wind"].sum()))
    col4.metric("Duze opady", int(df_anom["anomaly_rain"].sum()))

    st.divider()

    normal_days = df_anom[df_anom["is_anomaly"] == False]
    anomaly_days = df_anom[df_anom["is_anomaly"] == True]

    fig_anom = go.Figure()
    fig_anom.add_trace(go.Scatter(
        x=normal_days["date"],
        y=normal_days["temperature"],
        mode="lines+markers",
        name="Normalne dni",
        line=dict(color="royalblue"),
        marker=dict(size=3),
    ))
    fig_anom.add_trace(go.Scatter(
        x=anomaly_days["date"],
        y=anomaly_days["temperature"],
        mode="markers",
        name="Anomalia",
        marker=dict(color="red", size=10, symbol="x"),
    ))
    fig_anom.update_layout(
        title="Temperatura - anomalie zaznaczone na czerwono",
        xaxis_title="Data",
        yaxis_title="Temperatura (C)",
    )
    st.plotly_chart(fig_anom, use_container_width=True)

    if not anomalies.empty:
        st.subheader("Lista wykrytych anomalii")
        cols_to_show = ["date", "temperature", "precipitation", "windSpeed",
                        "anomaly_high_temp", "anomaly_low_temp", "anomaly_wind", "anomaly_rain"]
        cols_to_show = [c for c in cols_to_show if c in anomalies.columns]
        st.dataframe(anomalies[cols_to_show].reset_index(drop=True), use_container_width=True)
    else:
        st.success("Brak wykrytych anomalii w wybranym zakresie dat.")


# --- TAB 4: POROWNANIE MIAST ---
with tab4:
    st.subheader("Porownanie dwoch miast")

    cities_list = get_available_cities()

    col1, col2 = st.columns(2)
    city1 = col1.selectbox("Miasto 1", cities_list, index=0, key="cmp1")
    city2 = col2.selectbox("Miasto 2", cities_list, index=1, key="cmp2")

    col3, col4 = st.columns(2)
    cmp_start = col3.date_input("Zakres od", value=date(2023, 1, 1), key="cmp_start")
    cmp_end = col4.date_input("Zakres do", value=date(2023, 12, 31), key="cmp_end")

    if st.button("Porownaj miasta", type="primary"):
        if city1 == city2:
            st.warning("Wybierz dwa rozne miasta!")
        else:
            with st.spinner("Pobieranie danych..."):
                df1 = data_loader.load_data(city1, cmp_start, cmp_end, True)
                df2 = data_loader.load_data(city2, cmp_start, cmp_end, True)

            if df1.empty or df2.empty:
                st.error("Nie udalo sie pobrac danych dla jednego z miast.")
            else:
                s1, s2 = analyzer.compare_two_cities(df1, df2)

                st.subheader("Zestawienie statystyk")
                tabela = pd.DataFrame({
                    "Metryka": [
                        "Srednia temperatura", "Maks. temperatura", "Min. temperatura",
                        "Suma opadow", "Maks. wiatr", "Dni z deszczem", "Liczba rekordow",
                    ],
                    city1: [
                        f"{s1['avg_temp']:.1f} C",
                        f"{s1['max_temp']:.1f} C",
                        f"{s1['min_temp']:.1f} C",
                        f"{s1['total_precipitation']:.1f} mm",
                        f"{s1['max_windspeed']:.1f} km/h",
                        s1['rainy_days'],
                        s1['record_count'],
                    ],
                    city2: [
                        f"{s2['avg_temp']:.1f} C",
                        f"{s2['max_temp']:.1f} C",
                        f"{s2['min_temp']:.1f} C",
                        f"{s2['total_precipitation']:.1f} mm",
                        f"{s2['max_windspeed']:.1f} km/h",
                        s2['rainy_days'],
                        s2['record_count'],
                    ],
                })
                st.dataframe(tabela, use_container_width=True, hide_index=True)

                df1["miasto"] = city1
                df2["miasto"] = city2
                df_oba = pd.concat([df1, df2])

                fig_t = px.line(
                    df_oba, x="date", y="temperature", color="miasto",
                    title=f"Temperatura: {city1} vs {city2}",
                    labels={"temperature": "Temperatura (C)", "date": "Data", "miasto": "Miasto"},
                )
                st.plotly_chart(fig_t, use_container_width=True)

                fig_r = px.bar(
                    df_oba, x="date", y="precipitation", color="miasto", barmode="group",
                    title=f"Opady: {city1} vs {city2}",
                    labels={"precipitation": "Opady (mm)", "date": "Data", "miasto": "Miasto"},
                )
                st.plotly_chart(fig_r, use_container_width=True)

                fig_w = px.line(
                    df_oba, x="date", y="windSpeed", color="miasto",
                    title=f"Wiatr: {city1} vs {city2}",
                    labels={"windSpeed": "Wiatr (km/h)", "date": "Data", "miasto": "Miasto"},
                )
                st.plotly_chart(fig_w, use_container_width=True)


# --- TAB 5: STATYSTYKI ---
with tab5:
    st.subheader("Szczegolowe statystyki")

    monthly = analyzer.compute_monthly_stats(df)
    if not monthly.empty:
        st.markdown("#### Agregaty miesieczne")
        st.dataframe(
            monthly.rename(columns={
                "month": "Miesiac",
                "avg_temp": "Sr. temp. (C)",
                "max_temp": "Maks. temp. (C)",
                "min_temp": "Min. temp. (C)",
                "total_rain": "Suma opadow (mm)",
                "avg_wind": "Sr. wiatr (km/h)",
                "rainy_days": "Dni z deszczem",
            }),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.markdown("#### Surowe dane")

    search = st.text_input("Filtruj po dacie (np. 2023-06)")
    df_display = df.copy()
    if search:
        df_display = df_display[df_display["date"].astype(str).str.contains(search)]

    st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Pobierz dane jako CSV",
        data=csv_data,
        file_name=f"pogoda_{city_name}_{st.session_state['start_date']}_{st.session_state['end_date']}.csv",
        mime="text/csv",
    )
