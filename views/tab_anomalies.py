import streamlit as st
import plotly.graph_objects as go
import analyzer


def render(df):
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
