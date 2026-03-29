# Weather Analyzer

Projekt przedstawia prostą aplikację do analizy danych pogodowych zapisanych w pliku CSV. Program umożliwia przetwarzanie danych, ich filtrowanie oraz wyciąganie podstawowych statystyk.

## Funkcjonalności
- wczytywanie danych z pliku CSV
- filtrowanie danych po mieście
- filtrowanie danych po zakresie dat
- obliczanie statystyk (średnia temperatura, wilgotność, min/max)
- wykrywanie prostych anomalii (temperatura, wiatr, opady)
- generowanie raportu dla wybranego miasta

## Technologie
- Java
- Stream API
- Optional

## Struktura projektu
- `WeatherRecord` – reprezentuje pojedynczy rekord danych pogodowych  
- `WeatherDataLoader` – odpowiada za wczytywanie danych z pliku CSV  
- `WeatherFilter` – zawiera metody do filtrowania danych  
- `WeatherStatistics` – oblicza podstawowe statystyki  
- `WeatherAnalyzer` – wykrywa anomalie w danych  
- `WeatherReport` – generuje raport dla wybranego miasta  
- `Main` – uruchamia program i prezentuje wyniki  

## Uruchomienie
```bash
javac *.java
java Main
