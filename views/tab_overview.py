import streamlit as st
import plotly.graph_objects as go
import analyzer


def render(df, city_name, start_date, end_date):
    st.subheader(f"Przeglad: {city_name}")
    st.caption(f"Okres: {start_date} - {end_date}")

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
        kierunek = "rosnacy" if slope > 0 else "malejacy"
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
