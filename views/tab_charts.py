import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import analyzer


def render(df):
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
