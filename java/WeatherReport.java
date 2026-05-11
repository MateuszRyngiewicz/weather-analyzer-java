import java.util.List;
import java.util.Optional;

public class WeatherReport {

    public static void printCityReport(String city, List<WeatherRecord> records) {
        System.out.println("=== Raport pogodowy dla miasta: " + city + " ===");

        if (records.isEmpty()) {
            System.out.println("Brak danych dla podanego miasta.");
            return;
        }

        System.out.println("Liczba rekordów: " + records.size());
        System.out.println("Średnia temperatura: " + WeatherStatistics.averageTemperature(records));
        System.out.println("Średnia wilgotność: " + WeatherStatistics.averageHumidity(records));
        System.out.println("Liczba dni z opadami: " + WeatherStatistics.countRainyDays(records));

        Optional<WeatherRecord> minTemp = WeatherStatistics.minTemperatureRecord(records);
        Optional<WeatherRecord> maxTemp = WeatherStatistics.maxTemperatureRecord(records);

        minTemp.ifPresent(record ->
                System.out.println("Najniższa temperatura: " + record.temperature() + " (" + record.date() + ")")
        );

        maxTemp.ifPresent(record ->
                System.out.println("Najwyższa temperatura: " + record.temperature() + " (" + record.date() + ")")
        );

        System.out.println();
        System.out.println("Anomalie:");

        List<WeatherRecord> highTempDays = WeatherAnalyzer.findHighTemperatureDays(records, 5.0);
        List<WeatherRecord> lowTempDays = WeatherAnalyzer.findLowTemperatureDays(records, -1.0);
        List<WeatherRecord> strongWindDays = WeatherAnalyzer.findStrongWindDays(records, 24.0);
        List<WeatherRecord> heavyRainDays = WeatherAnalyzer.findHeavyRainDays(records, 6.0);

        System.out.println("Wysoka temperatura: " + highTempDays.size());
        System.out.println("Niska temperatura: " + lowTempDays.size());
        System.out.println("Silny wiatr: " + strongWindDays.size());
        System.out.println("Duże opady: " + heavyRainDays.size());
    }
}