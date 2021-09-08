package JavaExtractor.ml4se;

import JavaExtractor.Common.CommandLineValues;
import JavaExtractor.FeatureExtractor;
import JavaExtractor.FeaturesEntities.ProgramFeatures;
import com.google.gson.Gson;
import java.util.List;
import java.util.concurrent.Callable;

class PreprocessTask implements Callable<Void> {
    private CommandLineValues commandLineValues;
    private String code;

    public PreprocessTask(String methodCode, CommandLineValues commandLineValues) {
        this.code = methodCode;
        this.commandLineValues = commandLineValues;
    }

    @Override
    public Void call() {
        process();
        return null;
    }

    public void process() {

        ProgramFeatures features = getRepresentation();

        if (features == null) return;

        String toPrint = featuresToString(features);
        if (toPrint.length() > 0) {
            System.out.println(toPrint);
        }
    }

    private ProgramFeatures getRepresentation() {
        FeatureExtractor featureExtractor = new FeatureExtractor(this.commandLineValues, null);
        List<ProgramFeatures> features = featureExtractor.extractFeatures(this.code);
        if (features == null || features.isEmpty()) {
            return null;
        }
        return features.get(0);
    }

    private String featuresToString(ProgramFeatures singleMethodFeatures) {
        StringBuilder builder = new StringBuilder();

        String toPrint;
        if (commandLineValues.JsonOutput) {
            toPrint = new Gson().toJson(singleMethodFeatures);
        } else {
            toPrint = singleMethodFeatures.toString();
        }
        if (commandLineValues.PrettyPrint) {
            toPrint = toPrint.replace(" ", "\n\t");
        }
        builder.append(toPrint);

        return builder.toString();
    }
}
