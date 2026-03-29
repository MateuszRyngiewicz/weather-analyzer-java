import java.time.LocalDate;
import java.util.List;

public class WeatherFilter {

    public static List<WeatherRecord> filterByCity(List<WeatherRecord> records, String city) {
        return records.stream()
                .filter(record -> record.city().equalsIgnoreCase(city))
                .toList();
    }

    public static List<WeatherRecord> filterByDateRange(List<WeatherRecord> records, LocalDate startDate, LocalDate endDate) {
        return records.stream()
                .filter(record -> !record.date().isBefore(startDate) && !record.date().isAfter(endDate))
                .toList();
    }

    public static List<WeatherRecord> filterByCityAndDateRange(List<WeatherRecord> records, String city, LocalDate startDate, LocalDate endDate) {
        return records.stream()
                .filter(record -> record.city().equalsIgnoreCase(city))
                .filter(record -> !record.date().isBefore(startDate) && !record.date().isAfter(endDate))
                .toList();
    }
}