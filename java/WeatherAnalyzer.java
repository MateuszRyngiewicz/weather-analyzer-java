import java.util.List;

public class WeatherAnalyzer {

    public static List<WeatherRecord> findHighTemperatureDays(List<WeatherRecord> records, double threshold) {
        return records.stream()
                .filter(record -> record.temperature() > threshold)
                .toList();
    }

    public static List<WeatherRecord> findLowTemperatureDays(List<WeatherRecord> records, double threshold) {
        return records.stream()
                .filter(record -> record.temperature() < threshold)
                .toList();
    }

    public static List<WeatherRecord> findStrongWindDays(List<WeatherRecord> records, double threshold) {
        return records.stream()
                .filter(record -> record.windSpeed() > threshold)
                .toList();
    }

    public static List<WeatherRecord> findHeavyRainDays(List<WeatherRecord> records, double threshold) {
        return records.stream()
                .filter(record -> record.precipitation() > threshold)
                .toList();
    }
}