import streamlit as st
import analyzer


def render(df, city_name, start_date, end_date):
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
        file_name=f"pogoda_{city_name}_{start_date}_{end_date}.csv",
        mime="text/csv",
    )
