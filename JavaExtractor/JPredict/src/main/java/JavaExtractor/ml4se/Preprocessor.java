package JavaExtractor.ml4se;

import JavaExtractor.Common.CommandLineValues;
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
        } else {
            System.err.println("Input File not found.");
        }
    }

    private static void collectFeauturefromFile(int threadNum, Path inputFile) {
        List<Method> methods = MethodHelper.readMethodsFromFile(s_CommandLineValues.File.getPath());

        ArrayList<PreprocessTask> extractionTasks = new ArrayList<>();

        for (Method m : methods) {
            if (!m.getBody().isEmpty()) {
                extractionTasks.add(new PreprocessTask(m.getBody(), s_CommandLineValues));
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
}
