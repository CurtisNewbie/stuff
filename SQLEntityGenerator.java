import java.io.*;
import java.nio.file.Files;
import java.nio.file.*;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.*;
import java.util.stream.Collectors;

public class SQLEntityGenerator {

    private static final List<String> types = Arrays.asList("varchar", "int", "tinyint", "short", "decimal", "datetime", "timestamp", "bigint");
    private static final String CREATE = "create";
    private static final String COMMENT = "comment";
    private static final String CONSTRAINT = "constraint";

    public static void main(String[] args) throws IOException {

        if (args.length < 1) {
            System.out.println("Please specify path to sQL file");
            return;
        }

        final String path = args[0];
        System.out.printf("Will be parsing file: %s\n", path);

        final File f = new File(path);
        if (!f.exists()) {
            System.out.printf("File %s not found", path);
            return;
        }

        // read ddl scripts
        final List<String> lines = read(f).stream()
                .filter(l -> !l.trim().isBlank())
                .collect(Collectors.toList());

        // parse ddl
        final SQLTable table = parse(lines);

        // generate java object
        generateJavaClass(table);
    }

    private static void generateJavaClass(SQLTable table) throws IOException {
        final String tableCamelCase = toCamelCases(table.tableName);
        final String className = tableCamelCase.substring(0, 1).toUpperCase() + tableCamelCase.substring(1, tableCamelCase.length());
        final String fname = className + ".java";
        final Path gp = Paths.get(fname);

        // try to delete it, if there is one
        Files.deleteIfExists(gp);

        // create a new one
        final Path p = Files.createFile(gp);

        try (BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(Files.newOutputStream(p)))) {
            // always import util, time and math
            bw.write("import java.util.*;\n");
            bw.write("import java.time.*;\n");
            bw.write("import java.math.*;\n\n");

            // class
            bw.write("/** " + table.tableComment + " */\n");
            bw.write("public class " + className + " {\n\n");

            // fields
            for (SQLField field : table.fields) {
                bw.write("    /** " + field.comment + " */\n");
                bw.write("    private " + toJavaType(field.type) + " " + toCamelCases(field.fieldName) + ";\n\n");
            }

            // end
            bw.write("}\n");
        }

        System.out.printf("Java Entity File generated: %s\n", fname);
    }

    private static String toJavaType(String sqlType) {

        if (sqlType.equalsIgnoreCase("varchar"))
            return "String";

        if (sqlType.equalsIgnoreCase("datetime")
                || sqlType.equalsIgnoreCase("timestamp"))
            return "LocalDateTime";

        if (sqlType.equalsIgnoreCase("int")
                || sqlType.equalsIgnoreCase("tinyint")
                || sqlType.equalsIgnoreCase("short"))
            return "Integer";

        if (sqlType.equalsIgnoreCase("bigint"))
            return "Long";

        if (sqlType.equalsIgnoreCase("decimal"))
            return "BigDecimal";

        throw new IllegalArgumentException("Unable to find corresponding java type for " + sqlType);
    }

    private static String toCamelCases(String s) {
        boolean prevIsUnderline = false;
        s = s.toLowerCase();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            if (s.charAt(i) == '_') {
                prevIsUnderline = true;
            } else {
                if (prevIsUnderline) {
                    sb.append((s.charAt(i) + "").toUpperCase());
                    prevIsUnderline = false;
                } else {
                    sb.append(s.charAt(i));
                }
            }
        }

        return sb.toString();
    }

    private static List<String> read(final File f) throws IOException {
        List<String> lines = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(Files.newInputStream(f.toPath(), StandardOpenOption.READ)))) {
            String l;
            while ((l = br.readLine()) != null) {
                lines.add(l);
            }
        }
        return lines;
    }

    private static SQLTable parse(List<String> lines) {
        String tableName = null;
        String tableComment = null;
        List<SQLField> fields = new ArrayList<>();

        for (int i = 0; i < lines.size(); i++) {
            final String trimed = lines.get(i).trim();

            // skip blank lines
            if (trimed.isBlank())
                continue;

            // validate syntax
            if (!endsWithCorrectSymbol(trimed, i, lines.size())) {
                throw new IllegalArgumentException(String.format("Each line must end with either ',' ';' or '(' illegal syntax at line: %d", i + 1));
            }

            // split to tokens
            final String[] tokens = trimed.split(" ");

            // this line starts with create, it must be "CREATE TABLE *", try to extract the table name
            if (tokens[0].equalsIgnoreCase(CREATE)) {
                if (tableName != null)
                    throw new IllegalArgumentException("CREATE keyword is already used, please check your syntax");

                tableName = extractTableName(tokens, i + 1);
            }
            // the last line of the table
            else if (tokens[0].startsWith(")")) {
                tableComment = extractComment(tokens, i + 1);
            }
            // lines for the fields
            else {
                // we don't handle constraints
                if (tokens[0].equalsIgnoreCase(CONSTRAINT))
                    continue;

                fields.add(parseField(tokens, i + 1));
            }
        }

        if (tableName == null)
            throw new IllegalArgumentException("Failed to parse DDL, table name is not found");
        if (fields.isEmpty())
            throw new IllegalArgumentException("Failed to parse DDL, this table doesn't have fields");

        SQLTable sqlTable = new SQLTable();
        sqlTable.tableName = tableName;
        sqlTable.tableComment = tableComment != null ? tableComment : "";
        sqlTable.fields = fields;
        System.out.printf("Table: '%s', comment: '%s'\n", sqlTable.tableName, sqlTable.tableComment);
        return sqlTable;
    }

    private static SQLField parseField(String[] tokens, int lineNo) {
        // the first one is the field name
        final String fieldName = tokens[0];
        if (types.contains(fieldName)) {
            throw new IllegalArgumentException(String.format("Failed to parse DDL, field name %s can't be a keyword, illegal syntax at line %d", fieldName, lineNo));
        }

        String type = null;

        // we look for data type
        for (int i = 1; i < tokens.length; i++) {
            for (String t : types) {
                if (tokens[i].toLowerCase().startsWith(t)) {
                    type = t;
                    break;
                }
            }
        }

        if (type == null)
            throw new IllegalArgumentException(String.format("Failed to parse DDL, unable to identify data type for field '%s', illegal syntax at line %d", fieldName, lineNo));

        SQLField field = new SQLField();
        field.fieldName = fieldName;
        field.type = type;
        field.comment = extractComment(tokens, lineNo);
        System.out.printf("Field: '%s', type: '%s', comment: '%s'\n", fieldName, field.type, field.comment);
        return field;
    }

    private static String extractComment(String[] tokens, int lineNo) {
        // try to find comment, it won't be the first one anyway
        int l = -1, h = -1;
        String pre = "'";
        for (int i = 1; i < tokens.length; i++) {
            if (tokens[i].equalsIgnoreCase(COMMENT)) {

                if (l != -1) // we have already seem COMMENT key word
                    throw new IllegalArgumentException("Failed to parse DDL, multiple COMMENT keyword is found, illegal syntax at line " + lineNo);

                l = i + 1;
                if (!tokens[l].startsWith("'") && !tokens[l].startsWith("\""))
                    throw new IllegalArgumentException("Failed to parse DDL, COMMENT must start with ' or \", illegal syntax at line " + lineNo);

                if (tokens[l].startsWith("\""))
                    pre = "\"";

                // single word comment
                if (tokens[l].endsWith(pre)) {
                    h = l;
                    break;
                }
            } else {

                // we are look for the end of the comment, and we found it
                if (l != -1 && (tokens[i].endsWith(pre) || tokens[i].endsWith(pre + ",")) || tokens[i].endsWith(pre + ";")) {
                    h = i;
                    break;
                }
            }
        }

        // there is no comment
        if (l == -1 || h == -1) {
            return "";
        }

        String joined = String.join(" ", Arrays.copyOfRange(tokens, l, h + 1));
        // ", or "; or "
        int sub = joined.endsWith(",") || joined.endsWith(";") ? 2 : 1;
        return joined.substring(1, joined.length() - sub);
    }

    private static String extractTableName(String[] tokens, int lineNo) {
        // at least 'CREATE TABLE xxxxx (', which is of length 4
        if (tokens.length < 4)
            throw new IllegalArgumentException("Illegal CREATE TABLE statement at line " + lineNo);

        // if length is greater than 3, then it must be 7, 'CREATE TABLE IF NOT EXISTS XXX ('
        if (tokens.length > 3 && tokens.length != 7)
            throw new IllegalArgumentException("Illegal CREATE TABLE statement at line " + lineNo);

        if (!tokens[0].equalsIgnoreCase("create") || !tokens[1].equalsIgnoreCase("table"))
            throw new IllegalArgumentException("Illegal CREATE TABLE statement at line " + lineNo);

        if (tokens.length == 3)
            return tokens[2];

        if (!tokens[2].equalsIgnoreCase("if")
                || !tokens[3].equalsIgnoreCase("not")
                || !tokens[4].equalsIgnoreCase("exists")) {
            throw new IllegalArgumentException("Illegal CREATE TABLE statement at line " + lineNo);
        }

        return tokens[5];
    }

    private static boolean endsWithCorrectSymbol(String line, int i, int len) {
        boolean isLastLine = i == len - 1;
        boolean isFirstLine = i == 0;
        boolean isLineBeforeLastLine = i == len - 2;

        if (isFirstLine)
            return line.endsWith("(");

        // todo, we don't validate them for now
        if (isLastLine || isLineBeforeLastLine) {
            return true;
//            return line.endsWith(")") || line.endsWith(","); // e.g., constraint
//             return line.endsWith(";");
        }

        return line.endsWith(",");
    }

    private static class SQLField {
        private String fieldName;
        private String type;
        private String comment;

        @Override
        public String toString() {
            return "SQLField{" +
                    "fieldName='" + fieldName + '\'' +
                    ", type='" + type + '\'' +
                    ", comment='" + comment + '\'' +
                    '}';
        }
    }

    private static class SQLTable {
        private List<SQLField> fields;
        private String tableName;
        private String tableComment;

        @Override
        public String toString() {
            return "SQLTable{" +
                    "fields=" + fields +
                    ", tableName='" + tableName + '\'' +
                    ", tableComment='" + tableComment + '\'' +
                    '}';
        }
    }

}