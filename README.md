# Analizator Danych Pogodowych

Projekt składa się z dwóch części:
- **Aplikacja webowa (Python/Streamlit)** — główna aplikacja z interfejsem użytkownika, wykresami i integracją z API
- **Moduł konsolowy (Java)** — pierwotna wersja analizatora działająca w terminalu

---

## Spis treści

1. [Opis projektu](#opis-projektu)
2. [Architektura systemu](#architektura-systemu)
3. [Wymagania](#wymagania)
4. [Uruchomienie — aplikacja webowa (Python)](#uruchomienie--aplikacja-webowa-python)
5. [Uruchomienie przez Docker](#uruchomienie-przez-docker)
6. [Uruchomienie — moduł konsolowy (Java)](#uruchomienie--moduł-konsolowy-java)
7. [Opis modułów Python](#opis-modułów-python)
8. [Opis modułów Java](#opis-modułów-java)
9. [Funkcjonalności](#funkcjonalności)
10. [Źródła danych](#źródła-danych)
11. [Technologie](#technologie)

---

## Opis projektu

Projekt realizuje pełny system analizy danych pogodowych — od pobrania danych
z zewnętrznego API, przez ich przechowanie w lokalnej bazie danych, aż po
wizualizację i wykrywanie anomalii w przeglądarce internetowej.

Główne cele aplikacji:
- pobranie i buforowanie historycznych danych pogodowych
- filtrowanie danych według lokalizacji i zakresu dat
- wykrywanie trendów i anomalii pogodowych
- porównywanie danych historycznych dla różnych miast
- generowanie statystyk i interaktywnych wykresów

---

## Architektura systemu

```
┌─────────────────────────────────────────────┐
│              Streamlit (app.py)              │  ← interfejs użytkownika
└────────────────────┬────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
   data_loader.py  analyzer.py  weather_api.py
   (ładowanie      (statystyki  (Open-Meteo
    danych)        i anomalie)   API)
         │
    ┌────┴─────┐
    ▼          ▼
SQLite DB   weather_data.csv
(cache)     (lokalny dataset)
```

### Przepływ danych

1. Użytkownik wybiera miasto i zakres dat w panelu bocznym.
2. `data_loader` sprawdza czy dane są już w bazie SQLite (cache).
3. Jeśli nie ma w cache — pobiera dane z Open-Meteo Archive API.
4. Pobrane dane są zapisywane do bazy (przyszłe zapytania są szybsze).
5. Jeśli API jest niedostępne — fallback na lokalny plik `weather_data.csv`.
6. Dane trafiają do `analyzer.py`, który oblicza statystyki i wykrywa anomalie.
7. Wyniki są wyświetlane w postaci wykresów i tabel w przeglądarce.

---

## Wymagania

- Python 3.11 lub nowszy + pip

Lub:
- Docker + Docker Compose (zalecane, bez konfiguracji środowiska)

Dla modułu Java:
- Java 17 lub nowszy (JDK)

---

## Uruchomienie — aplikacja webowa (Python)

### 1. Sklonuj repozytorium

```bash
git clone https://github.com/MateuszRyngiewicz/weather-analyzer-java.git
cd weather-analyzer-java
```

### 2. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### 3. Uruchom aplikację

```bash
streamlit run app.py
```

Aplikacja będzie dostępna pod adresem: [http://localhost:8501](http://localhost:8501)

---

## Uruchomienie przez Docker

Zalecana metoda — nie wymaga instalacji Pythona ani żadnych bibliotek.

### Zbuduj i uruchom

```bash
docker compose up --build
```

Aplikacja będzie dostępna pod: [http://localhost:8501](http://localhost:8501)

### Zatrzymanie

```bash
docker compose down
```

> Baza danych SQLite (`weather_history.db`) jest montowana jako volumen,
> więc pobrane dane są zachowywane między restartami kontenera.

---

## Uruchomienie — moduł konsolowy (Java)

```bash
javac *.java
java Main
```

Program wczytuje plik `weather_data.csv` i wypisuje raporty dla miast Copenhagen, Aarhus i Odense.

---

## Opis modułów Python

### `app.py` — interfejs użytkownika

Główny plik aplikacji. Zawiera cały kod Streamlit odpowiedzialny za układ
strony, panele, zakładki i wykresy. Komunikuje się z pozostałymi modułami.

Zakładki:
- **Przegląd** — metryki, trend temperatury
- **Wykresy** — temperatura z zakresem min/max, opady, wiatr, mapa ciepła
- **Anomalie** — wykryte odchylenia, lista i wizualizacja
- **Porównanie miast** — zestawienie dwóch miast obok siebie
- **Statystyki** — tabela miesięczna, surowe dane, eksport CSV

---

### `weather_api.py` — integracja z API

Odpowiada za komunikację z Open-Meteo Archive API.

Słownik `CITY_COORDS` zawiera współrzędne geograficzne obsługiwanych miast:

| Miasto     | Szerokość | Długość  |
|------------|-----------|----------|
| Copenhagen | 55.6761   | 12.5683  |
| Aarhus     | 56.1629   | 10.2039  |
| Odense     | 55.3959   | 10.3883  |
| Aalborg    | 57.0488   | 9.9187   |
| Esbjerg    | 55.4765   | 8.4594   |

Pobierane zmienne dzienne:
- `temperature_2m_mean` / `temperature_2m_max` / `temperature_2m_min`
- `precipitation_sum`
- `windspeed_10m_max`

---

### `data_loader.py` — ładowanie danych

Zarządza wszystkimi źródłami danych.

**`init_db()`** — tworzy tabelę `weather_data` w SQLite jeśli nie istnieje.

**`save_to_db(df)`** — zapisuje DataFrame do bazy, duplikaty są ignorowane
(`INSERT OR IGNORE`), więc wielokrotne wywołania są bezpieczne.

**`load_from_db(city, start, end)`** — pobiera dane z cache dla danego
miasta i zakresu dat.

**`load_data(city, start, end, use_api)`** — główna funkcja, implementuje
logikę fallback: baza → API → CSV.

---

### `analyzer.py` — analiza danych

**`compute_statistics(df)`** — zwraca słownik ze statystykami:
średnią, min, max, sumą opadów, itp.

**`detect_anomalies(df, ...)`** — wykrywa anomalie metodą odchylenia
standardowego (2σ). Można przekazać własne progi progowe. Dodaje kolumny
boolean do DataFrame (`anomaly_high_temp`, `anomaly_wind`, itd.).

**`compute_monthly_stats(df)`** — agreguje dane po miesiącach,
zwraca DataFrame z agregatami.

**`compute_trend(df, column)`** — wyznacza trend liniowy przy pomocy
`numpy.polyfit`. Zwraca współczynnik kierunkowy i wartości linii trendu.

**`compare_two_cities(df1, df2)`** — pomocnicza funkcja do porównania
dwóch zbiorów danych.

---

## Opis modułów Java

- `WeatherRecord` — reprezentuje pojedynczy rekord danych pogodowych (rekord Java)
- `WeatherDataLoader` — wczytuje dane z pliku CSV
- `WeatherFilter` — filtruje dane po mieście i zakresie dat
- `WeatherStatistics` — oblicza statystyki (średnia, min, max, liczba dni z opadami)
- `WeatherAnalyzer` — wykrywa anomalie (wysoka/niska temperatura, silny wiatr, duże opady)
- `WeatherReport` — generuje raport tekstowy dla wybranego miasta
- `Main` — punkt wejścia, uruchamia analizę i wypisuje wyniki

---

## Funkcjonalności

### Pobieranie danych z API
Aplikacja korzysta z **Open-Meteo Archive API** — darmowego serwisu
bez konieczności rejestracji ani klucza API. Dane historyczne są dostępne
od roku 1940.

### Lokalne cache (SQLite)
Raz pobrane dane są przechowywane w lokalnej bazie SQLite (`weather_history.db`).
Dzięki temu ponowne zapytanie dla tego samego miasta i zakresu dat jest
natychmiastowe i nie wymaga połączenia z internetem.

### Wykrywanie anomalii
Anomalie są wykrywane automatycznie na podstawie odchylenia standardowego:

```
próg_górny = średnia + 2 × std
próg_dolny = średnia − 2 × std
```

Użytkownik może też ręcznie ustawić progi dla każdego parametru oddzielnie.

### Trend liniowy
Na wykresie temperatury rysowana jest linia trendu wyznaczona regresją liniową.
Współczynnik kierunkowy jest wyświetlany w legendzie (w °C/dzień).

### Mapa ciepła
Dla zakresów dłuższych niż 30 dni generowana jest mapa ciepła temperatury
w układzie miesiąc × dzień — pozwala szybko zobaczyć sezonowość danych.

### Porównanie miast
Zakładka "Porównanie miast" umożliwia pobranie danych dla dwóch miast
i wyświetlenie ich na wspólnych wykresach wraz z tabelą porównawczą.

### Eksport danych
Z zakładki "Statystyki" można pobrać wyświetlane dane jako plik CSV.

---

## Źródła danych

- **Open-Meteo Archive API** — https://open-meteo.com/
  Darmowe API z historycznymi danymi pogodowymi bez klucza API.
  Dokumentacja: https://open-meteo.com/en/docs/historical-weather-api

- **weather_data.csv** — lokalny dataset przygotowany ręcznie,
  zawiera dane dla 3 miast z okresu 1–5 stycznia 2024.
  Używany jako fallback gdy API jest niedostępne.

---

## Technologie

| Technologia  | Zastosowanie                        |
|-------------|-------------------------------------|
| Python 3.11 | język programowania (moduł webowy)  |
| Java 17     | język programowania (moduł konsolowy) |
| Streamlit   | interfejs webowy                    |
| Plotly      | interaktywne wykresy                |
| Pandas      | przetwarzanie danych tabelarycznych |
| NumPy       | obliczenia numeryczne (trend)       |
| SQLite      | lokalna baza danych (cache)         |
| Requests    | zapytania HTTP do API               |
| Docker      | konteneryzacja aplikacji            |

---

*Projekt zaliczeniowy — Mateusz Ryngiewicz*
