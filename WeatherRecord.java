import java.time.LocalDate;

public record WeatherRecord(
        LocalDate date,
        String city,
        double temperature,
        double humidity,
        double pressure,
        double windSpeed,
        double precipitation
) {
}