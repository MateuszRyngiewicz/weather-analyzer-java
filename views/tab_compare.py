import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import data_loader
import analyzer
from weather_api import get_available_cities


def render():
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
            return

        with st.spinner("Pobieranie danych..."):
            df1 = data_loader.load_data(city1, cmp_start, cmp_end, True)
            df2 = data_loader.load_data(city2, cmp_start, cmp_end, True)

        if df1.empty or df2.empty:
            st.error("Nie udalo sie pobrac danych dla jednego z miast.")
            return

        s1, s2 = analyzer.compare_two_cities(df1, df2)

        st.subheader("Zestawienie statystyk")
        tabela = pd.DataFrame({
            "Metryka": [
                "Srednia temperatura", "Maks. temperatura", "Min. temperatura",
                "Suma opadow", "Maks. wiatr", "Dni z deszczem", "Liczba rekordow",
            ],
            city1: [
                f"{s1['avg_temp']:.1f} C", f"{s1['max_temp']:.1f} C", f"{s1['min_temp']:.1f} C",
                f"{s1['total_precipitation']:.1f} mm", f"{s1['max_windspeed']:.1f} km/h",
                s1['rainy_days'], s1['record_count'],
            ],
            city2: [
                f"{s2['avg_temp']:.1f} C", f"{s2['max_temp']:.1f} C", f"{s2['min_temp']:.1f} C",
                f"{s2['total_precipitation']:.1f} mm", f"{s2['max_windspeed']:.1f} km/h",
                s2['rainy_days'], s2['record_count'],
            ],
        })
        st.dataframe(tabela, use_container_width=True, hide_index=True)

        df1["miasto"] = city1
        df2["miasto"] = city2
        df_oba = pd.concat([df1, df2])

        fig_t = px.line(df_oba, x="date", y="temperature", color="miasto",
                        title=f"Temperatura: {city1} vs {city2}",
                        labels={"temperature": "Temperatura (C)", "date": "Data", "miasto": "Miasto"})
        st.plotly_chart(fig_t, use_container_width=True)

        fig_r = px.bar(df_oba, x="date", y="precipitation", color="miasto", barmode="group",
                       title=f"Opady: {city1} vs {city2}",
                       labels={"precipitation": "Opady (mm)", "date": "Data", "miasto": "Miasto"})
        st.plotly_chart(fig_r, use_container_width=True)

        fig_w = px.line(df_oba, x="date", y="windSpeed", color="miasto",
                        title=f"Wiatr: {city1} vs {city2}",
                        labels={"windSpeed": "Wiatr (km/h)", "date": "Data", "miasto": "Miasto"})
        st.plotly_chart(fig_w, use_container_width=True)
