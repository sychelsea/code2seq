package JavaExtractor.ml4se;

import JavaExtractor.Common.CommandLineValues;
import JavaExtractor.FeaturesEntities.ProgramFeatures;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadPoolExecutor;
import org.kohsuke.args4j.CmdLineException;

public class Preprocessor {
    // public static int execCnt = 0;
    // public static int printCnt = 0;
    public static int taskNum = 0;
    private static CommandLineValues s_CommandLineValues;

    public static void main(String[] args) {
        try {
            s_CommandLineValues = new CommandLineValues(args);
        } catch (CmdLineException e) {
            e.printStackTrace();
            return;
        }

        if (s_CommandLineValues.File != null) {

            collectFeauturefromFile(
                    s_CommandLineValues.NumThreads, s_CommandLineValues.File.toPath());
            // System.out.println("????");
            printData();

        } else {
            System.err.println("Input File not found.");
        }
    }

    private static void collectFeauturefromFile(int threadNum, Path inputFile) {
        List<Method> methods = MethodHelper.readMethodsFromFile(s_CommandLineValues.File.getPath());

        ArrayList<PreprocessTask> extractionTasks = new ArrayList<>();

        for (Method m : methods) {
            if (!m.getBody().isEmpty()) {
                // System.out.println("i: " + i);
                extractionTasks.add(new PreprocessTask(m, s_CommandLineValues));
            }
        }

        taskNum = extractionTasks.size();
        ThreadPoolExecutor executor = (ThreadPoolExecutor) Executors.newFixedThreadPool(threadNum);
        List<Future<Void>> tasksResults = null;
        try {
            tasksResults = executor.invokeAll(extractionTasks);
            executor.shutdown();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    private static void printData() {
        // try {
        //   Files.writeString(cmdArgs.OutputFile, out);
        // } catch (IOException e) {
        //   e.printStackTrace();
        // }
        // System.out.println("feature size: " + features.size());
        try (BufferedWriter writer = Files.newBufferedWriter(cmdArgs.OutputFile)) {

            for (ProgramFeatures feature : features) {
                String out = featuresToString(feature);
                // System.out.println("[JavaExtractor] " + out);
                writer.write(out + "\n");
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static String featuresToString(ProgramFeatures feature) {
        StringBuilder builder = new StringBuilder();

        String toPrint = feature.toString();
        if (cmdArgs.PrettyPrint) {
            toPrint = toPrint.replace(" ", "\n\t");
        }

        return toPrint;
    }
}
