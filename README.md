# Analizator Danych Pogodowych

Aplikacja webowa do analizy historycznych danych pogodowych dla duńskich miast. Napisana w Pythonie z użyciem Streamlit i Plotly. Dane pobierane są z Open-Meteo API i zapisywane lokalnie w SQLite.

W repozytorium jest też starsza wersja konsolowa napisana w Javie.

---

## Jak uruchomić

### Python (główna aplikacja)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aplikacja będzie dostępna pod http://localhost:8501

### Docker

```bash
docker compose up --build
```

### Java (wersja konsolowa)

```bash
javac *.java
java Main
```

---

## Co robi aplikacja

- pobiera historyczne dane pogodowe z Open-Meteo API dla 5 duńskich miast
- zapisuje pobrane dane w lokalnej bazie SQLite żeby nie pobierać ich za każdym razem
- filtrowanie po mieście i zakresie dat
- wykrywanie anomalii pogodowych metodą odchylenia standardowego (2σ)
- wyznaczanie trendu liniowego temperatury
- porównywanie dwóch miast na wykresach
- statystyki miesięczne
- eksport danych do CSV
- fallback na lokalny plik CSV jeśli API nie działa

---

## Struktura plików

**Python:**
- `app.py` - główny plik aplikacji, interfejs Streamlit
- `weather_api.py` - pobieranie danych z Open-Meteo API
- `data_loader.py` - zarządzanie danymi (baza SQLite, CSV, API)
- `analyzer.py` - obliczenia statystyk, wykrywanie anomalii, trend

**Java:**
- `Main.java` - punkt wejścia
- `WeatherRecord.java` - rekord danych pogodowych
- `WeatherDataLoader.java` - wczytywanie CSV
- `WeatherFilter.java` - filtrowanie danych
- `WeatherStatistics.java` - statystyki
- `WeatherAnalyzer.java` - wykrywanie anomalii
- `WeatherReport.java` - generowanie raportu

---

## Technologie

- Python, Streamlit, Plotly, Pandas, NumPy, SQLite
- Java (wersja konsolowa)
- Docker

---

*Mateusz Ryngiewicz*
