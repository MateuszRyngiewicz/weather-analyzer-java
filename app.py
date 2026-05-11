import streamlit as st
from datetime import date

import data_loader
from weather_api import get_available_cities
from views import tab_overview, tab_charts, tab_anomalies, tab_compare, tab_stats


st.set_page_config(page_title="Analizator Pogody", layout="wide")
st.title("Analizator Danych Pogodowych")
st.caption("Historyczne dane dla dunskich miast - Open-Meteo Archive API")
st.divider()


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


if "df" not in st.session_state:
    st.info("Wybierz ustawienia i kliknij Zaladuj dane aby rozpoczac analize.")
    st.markdown("""
    ### O aplikacji

    Aplikacja analizuje historyczne dane pogodowe dla dunskich miast.

    Mozliwosci:
    - Przeglad kluczowych wskaznikow pogodowych
    - Interaktywne wykresy temperatur, opadow i wiatru
    - Automatyczne wykrywanie anomalii metoda odchylenia standardowego
    - Porownywanie dwoch miast obok siebie
    - Statystyki miesieczne i eksport danych do CSV
    - Cache w bazie SQLite - szybkie ponowne ladowanie

    Zrodla danych:
    - Open-Meteo Archive API (darmowe, bez klucza API)
    - Lokalny plik weather_data.csv (fallback gdy brak internetu)
    """)
    st.stop()


df = st.session_state["df"]
city_name = st.session_state["city"]
start = st.session_state["start_date"]
end = st.session_state["end_date"]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Przeglad",
    "Wykresy",
    "Anomalie",
    "Porownanie miast",
    "Statystyki",
])

with tab1:
    tab_overview.render(df, city_name, start, end)

with tab2:
    tab_charts.render(df)

with tab3:
    tab_anomalies.render(df)

with tab4:
    tab_compare.render()

with tab5:
    tab_stats.render(df, city_name, start, end)
