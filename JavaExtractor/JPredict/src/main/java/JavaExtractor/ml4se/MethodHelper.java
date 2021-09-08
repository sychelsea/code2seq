package JavaExtractor.ml4se;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.*;

public final class MethodHelper {

    public static List<Method> readMethodsFromFile(String fileName) {
        List<Method> methods = new ArrayList<Method>();

        try (Stream<String> stream = Files.lines(Paths.get(fileName))) {
            stream.forEach(
                    (String line) -> {
                        try {
                            methods.add(new Method(line));
                        } catch (Exception e) {
                            System.err.println(e);
                            // System.exit(1);
                        }
                    });
        } catch (Exception e) {
            System.err.println(e);
            System.exit(1);
        }

        return methods;
    }
}
