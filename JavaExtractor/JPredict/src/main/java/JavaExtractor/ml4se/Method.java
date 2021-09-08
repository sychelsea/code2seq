package JavaExtractor.ml4se;

import java.util.Base64;

public class Method {
    public static final String delim = " @@ ";

    public Method(String encoding) throws Exception {
        String[] data = encoding.split(delim);
        this.name = base64decode(data[0].strip());
        this.comment = base64decode(data[1].strip());
        this.body = base64decode(data[2].strip());
    }

    private String name = null;
    private String body = null;
    private String comment = null;

    public String getName() {
        return this.name;
    }

    public String getBody() {
        return this.body;
    }

    public String getComment() {
        return this.comment;
    }

    private static final Base64.Decoder base64decoder = Base64.getDecoder();
    private static final Base64.Encoder base64encoder = Base64.getEncoder();

    private static String base64encode(String str) {
        String result = base64encoder.encodeToString(str.getBytes());
        return result.strip();
    }

    private static String base64decode(String str) throws Exception {
        byte[] decodedBytes = base64decoder.decode(str);
        String result = new String(decodedBytes);
        return result.strip();
    }
}
