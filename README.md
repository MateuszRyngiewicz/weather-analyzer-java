# Analizator Danych Pogodowych

Aplikacja webowa do analizy historycznych danych pogodowych dla dunskich miast. Napisana w Pythonie z uzyciem Streamlit i Plotly. Dane pobierane sa z Open-Meteo API i zapisywane lokalnie w SQLite.

W repozytorium jest tez starsza wersja konsolowa napisana w Javie.

## Jak uruchomic

Python (glowna aplikacja):

pip install -r requirements.txt
streamlit run app.py

Aplikacja bedzie dostepna pod http://localhost:8501

Docker:

docker compose up --build

Java (wersja konsolowa):

javac *.java
java Main

## Co robi aplikacja

- pobiera historyczne dane pogodowe z Open-Meteo API dla 5 dunskich miast
- zapisuje pobrane dane w lokalnej bazie SQLite zeby nie pobierac ich za kazdym razem
- filtrowanie po miescie i zakresie dat
- wykrywanie anomalii pogodowych metoda odchylenia standardowego
- wyznaczanie trendu liniowego temperatury
- porownywanie dwoch miast na wykresach
- statystyki miesieczne
- eksport danych do CSV
- fallback na lokalny plik CSV jesli API nie dziala

## Struktura plikow

Python:
- app.py - glowny plik aplikacji, interfejs Streamlit
- weather_api.py - pobieranie danych z Open-Meteo API
- data_loader.py - zarzadzanie danymi (baza SQLite, CSV, API)
- analyzer.py - obliczenia statystyk, wykrywanie anomalii, trend

Java:
- Main.java - punkt wejscia
- WeatherRecord.java - rekord danych pogodowych
- WeatherDataLoader.java - wczytywanie CSV
- WeatherFilter.java - filtrowanie danych
- WeatherStatistics.java - statystyki
- WeatherAnalyzer.java - wykrywanie anomalii
- WeatherReport.java - generowanie raportu

## Technologie

Python, Streamlit, Plotly, Pandas, NumPy, SQLite, Java, Docker

Mateusz Ryngiewicz
