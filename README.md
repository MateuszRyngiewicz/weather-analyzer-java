# Analizator Danych Pogodowych

Aplikacja webowa do analizy historycznych danych pogodowych dla dunskich miast. Dane pobierane sa z Open-Meteo Archive API i przechowywane lokalnie w bazie SQLite. Interfejs uzytkownika zbudowany w Streamlit z wykresami Plotly.

Repozytorium zawiera rowniez starsza wersje konsolowa napisana w Javie (folder java/).


## Struktura projektu

```
weather-analyzer/
    app.py                  - glowny plik aplikacji, punkt wejscia
    analyzer.py             - logika analizy danych (statystyki, anomalie, trend)
    data_loader.py          - ladowanie danych z bazy, API i CSV
    weather_api.py          - komunikacja z Open-Meteo API
    weather_data.csv        - lokalny dataset (fallback)
    requirements.txt        - zaleznosci Python
    Dockerfile              - konfiguracja obrazu Docker
    docker-compose.yml      - konfiguracja uruchomienia kontenera
    views/
        tab_overview.py     - widok zakladki Przeglad
        tab_charts.py       - widok zakladki Wykresy
        tab_anomalies.py    - widok zakladki Anomalie
        tab_compare.py      - widok zakladki Porownanie miast
        tab_stats.py        - widok zakladki Statystyki
    java/
        Main.java           - punkt wejscia wersji konsolowej
        WeatherRecord.java  - model danych pogodowych
        WeatherDataLoader.java - wczytywanie danych z CSV
        WeatherFilter.java  - filtrowanie danych
        WeatherStatistics.java - obliczanie statystyk
        WeatherAnalyzer.java - wykrywanie anomalii
        WeatherReport.java  - generowanie raportu tekstowego
```


## Jak uruchomic

### Python

pip install -r requirements.txt
streamlit run app.py

Aplikacja dostepna pod http://localhost:8501

### Docker

docker compose up --build

### Java (wersja konsolowa)

cd java
javac *.java
java Main


## Opis modulow

### app.py

Glowny plik aplikacji. Odpowiada za inicjalizacje strony, panel boczny z ustawieniami (wybor miasta, zakres dat, przelacznik API) oraz orchestracje widokow. Kazda zakladka to osobny modul w folderze views/.

### analyzer.py

Modul odpowiedzialny za analize danych. Wykorzystuje programowanie funkcyjne - funkcje map(), filter() i reduce() do przetwarzania rekordow pogodowych.

compute_statistics(df) - oblicza srednia, min, max, sume opadow, liczbe dni z deszczem. Uzywa map() do wyciagania wartosci z rekordow, filter() do filtrowania dni z opadami, reduce() do sumowania.

detect_anomalies(df, ...) - wykrywa anomalie metoda odchylenia standardowego (srednia +/- 2*std). Uzywa lambd i map() do sprawdzania czy wartosci przekraczaja progi.

compute_monthly_stats(df) - grupuje dane po miesiacach i oblicza agregaty. Wewnatrz kazdej grupy uzywa map() i filter() do przetwarzania rekordow.

compute_trend(df, column) - wyznacza trend liniowy przez regresje liniowa (numpy.polyfit). Zwraca wspolczynnik kierunkowy i wartosci linii trendu.

compare_two_cities(df1, df2) - porownuje statystyki dwoch zbiorow danych.

### data_loader.py

Zarzadza wszystkimi zrodlami danych. Implementuje logike fallback: baza SQLite -> API -> lokalny CSV.

init_db() - tworzy tabele weather_data w SQLite jesli nie istnieje.

save_to_db(df) - zapisuje dane do bazy. Uzywa map() do przeksztalcenia wierszy DataFrame na krotki przed insertem. Duplikaty sa ignorowane (INSERT OR IGNORE).

load_from_db(city, start, end) - pobiera dane z cache dla danego miasta i zakresu dat.

load_data(city, start, end, use_api) - glowna funkcja ladowania. Najpierw sprawdza cache w bazie, jesli brak to odpytuje API i zapisuje wynik, na koncu fallback na lokalny CSV. W CSV uzywa filter() z lambda do filtrowania rekordow po miescie i zakresie dat.

### weather_api.py

Komunikacja z Open-Meteo Archive API. Zawiera slownik CITY_COORDS ze wspolrzednymi geograficznymi dla 5 miast (Copenhagen, Aarhus, Odense, Aalborg, Esbjerg).

fetch_historical_weather(city, start, end) - wysyla zapytanie do API i zwraca DataFrame z danymi dziennymi: srednia/min/max temperatura, suma opadow, predkosc wiatru.

### views/

Kazda zakladka aplikacji to osobny modul z jedna funkcja render(). Taki podzial sprawia ze app.py jest cienki i czytelny, a kazdy widok mozna modyfikowac niezaleznie.

tab_overview.py - metryki (srednia temperatura, opady, wiatr, deszczowe dni) oraz wykres temperatury z linia trendu.

tab_charts.py - wykresy temperatury z zakresem min/max, opadow, wiatru oraz mapa ciepla i srednia miesieczna.

tab_anomalies.py - wykrywanie i wizualizacja anomalii. Mozliwosc recznego ustawienia progow lub automatyczne na podstawie odchylenia standardowego.

tab_compare.py - porownanie dwoch wybranych miast w zadanym zakresie dat. Tabela statystyk i wspolne wykresy.

tab_stats.py - szczegolowe statystyki miesieczne, przeglad surowych danych z filtrowaniem i eksport do CSV.


## Przeplyw danych

1. Uzytkownik wybiera miasto i zakres dat w panelu bocznym
2. data_loader sprawdza czy dane sa juz w bazie SQLite
3. Jesli nie ma w cache - pobiera z Open-Meteo API i zapisuje do bazy
4. Jesli API niedostepne - wczytuje z lokalnego pliku weather_data.csv
5. Dane trafiaja do analyzer.py ktory oblicza statystyki i wykrywa anomalie
6. Wyniki wyswietlane sa w widokach w poszczegolnych zakładkach


## Technologie

Python 3.11, Streamlit, Plotly, Pandas, NumPy, SQLite, Requests, Docker

Java 17 (wersja konsolowa)


## Zrodla danych

Open-Meteo Archive API - https://open-meteo.com
Darmowe API z historycznymi danymi pogodowymi od roku 1940, bez klucza API.

weather_data.csv - lokalny dataset z danymi dla 3 miast z poczatku stycznia 2024. Uzywany jako fallback gdy API jest niedostepne.


Mateusz Ryngiewicz
