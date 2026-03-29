import java.util.Comparator;
import java.util.DoubleSummaryStatistics;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class WeatherStatistics {

    public static double averageTemperature(List<WeatherRecord> records) {
        return records.stream()
                .mapToDouble(WeatherRecord::temperature)
                .average()
                .orElse(0.0);
    }

    public static Optional<WeatherRecord> minTemperatureRecord(List<WeatherRecord> records) {
        return records.stream()
                .min(Comparator.comparingDouble(WeatherRecord::temperature));
    }

    public static Optional<WeatherRecord> maxTemperatureRecord(List<WeatherRecord> records) {
        return records.stream()
                .max(Comparator.comparingDouble(WeatherRecord::temperature));
    }

    public static double averageHumidity(List<WeatherRecord> records) {
        return records.stream()
                .mapToDouble(WeatherRecord::humidity)
                .average()
                .orElse(0.0);
    }

    public static long countRainyDays(List<WeatherRecord> records) {
        return records.stream()
                .filter(record -> record.precipitation() > 0)
                .count();
    }

    public static DoubleSummaryStatistics temperatureSummary(List<WeatherRecord> records) {
        return records.stream()
                .collect(Collectors.summarizingDouble(WeatherRecord::temperature));
    }

    public static Map<String, Double> averageTemperatureByCity(List<WeatherRecord> records) {
        return records.stream()
                .collect(Collectors.groupingBy(
                        WeatherRecord::city,
                        Collectors.averagingDouble(WeatherRecord::temperature)
                ));
    }
}