import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.List;

public class WeatherDataLoader {

    public static List<WeatherRecord> loadFromCsv(String fileName) throws IOException {
        return Files.lines(Path.of(fileName))
                .skip(1)
                .map(line -> line.split(","))
                .map(parts -> new WeatherRecord(
                        LocalDate.parse(parts[0].trim()),
                        parts[1].trim(),
                        Double.parseDouble(parts[2].trim()),
                        Double.parseDouble(parts[3].trim()),
                        Double.parseDouble(parts[4].trim()),
                        Double.parseDouble(parts[5].trim()),
                        Double.parseDouble(parts[6].trim())
                ))
                .toList();
    }
}