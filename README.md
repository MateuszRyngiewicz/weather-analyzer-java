# Weather Analyzer

Aplikacja do analizy danych pogodowych zapisanych w pliku CSV.

## Funkcjonalności
- wczytywanie danych z pliku CSV
- filtrowanie danych (miasto, zakres dat)
- obliczanie statystyk (średnia, min, max)
- wykrywanie prostych anomalii (temperatura, wiatr, opady)
- generowanie raportu dla wybranego miasta

## Technologie
- Java
- Stream API
- Optional

## Struktura projektu
- `WeatherRecord` – pojedynczy rekord danych
- `WeatherDataLoader` – wczytywanie danych z pliku
- `WeatherFilter` – filtrowanie danych
- `WeatherStatistics` – obliczenia statystyczne
- `WeatherAnalyzer` – wykrywanie anomalii
- `WeatherReport` – generowanie raportu
- `Main` – uruchomienie programu

## Uruchomienie
```bash
javac *.java
java Main
