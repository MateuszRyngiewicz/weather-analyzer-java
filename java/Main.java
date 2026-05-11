import java.io.IOException;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

public class Main {

    public static void main(String[] args) {
        try {
            List<WeatherRecord> records = WeatherDataLoader.loadFromCsv("weather_data.csv");

            System.out.println("=== ANALIZATOR DANYCH POGODOWYCH ===");
            System.out.println("Liczba wszystkich rekordów: " + records.size());
            System.out.println();

            // Raport dla wybranych miast
            List<WeatherRecord> copenhagenRecords = WeatherFilter.filterByCity(records, "Copenhagen");
            List<WeatherRecord> aarhusRecords = WeatherFilter.filterByCity(records, "Aarhus");

            WeatherReport.printCityReport("Copenhagen", copenhagenRecords);
            System.out.println();
            WeatherReport.printCityReport("Aarhus", aarhusRecords);

            // Średnia temperatura dla wszystkich miast
            System.out.println();
            System.out.println("=== Średnia temperatura dla każdego miasta ===");
            Map<String, Double> avgByCity = WeatherStatistics.averageTemperatureByCity(records);
            avgByCity.forEach((city, avgTemp) ->
                    System.out.println(city + " -> " + avgTemp)
            );

            // Dane dla zakresu dat
            System.out.println();
            System.out.println("=== Dane dla wybranego zakresu dat ===");

            List<WeatherRecord> dateRangeRecords = WeatherFilter.filterByDateRange(
                    records,
                    LocalDate.of(2024, 1, 2),
                    LocalDate.of(2024, 1, 4)
            );

            System.out.println("Liczba rekordów w zakresie dat: " + dateRangeRecords.size());
            dateRangeRecords.forEach(System.out::println);

        } catch (IOException e) {
            System.out.println("Błąd podczas wczytywania pliku: " + e.getMessage());
        }
    }
}