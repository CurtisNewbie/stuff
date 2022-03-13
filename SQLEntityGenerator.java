import java.io.*;
import java.nio.file.Files;
import java.nio.file.*;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Generator of Java Entity Class based on SQL DDL
 * <p>
 * It takes two arguments, the arg[0] is the path to the SQL DDL file. The SQL file should only contain one 'CREATE
 * TABLE' statement. The arg[1] is the optional flag '--mybatisplus', which indicates the mybatis-plus is used, the
 * generated Java class will then contain annotation, such as @TableField and @TableName.
 * </p>
 * <p>
 * This simple tool requires that each line only contains keywords for a single field. Don't put everything on a single
 * line.
 * </p>
 * <p>
 *
 * </p>
 *
 * <pre>
 * {@code
 *     The Following is a valid example:
 *
 *     CREATE TABLE IF NOT EXISTS book (
 *      id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT "primary key",
 *      name VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'name of the book',
 *      create_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is created',
 *      create_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who created this record',
 *      update_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is updated',
 *      update_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who updated this record',
 *      is_del TINYINT NOT NULL DEFAULT '0' COMMENT '0-normal, 1-deleted'
 *     ) ENGINE=InnoDB COMMENT 'Some nice books';
 * }
 * </pre>
 *
 * <pre>
 *
 *     The generate Java class is as follows:
 *
 *      import java.util.*;
 *      import java.time.*;
 *      import java.math.*;
 *
 *      /** Some nice books *{@literal /}
 *      public class Book {
 *
 *          /** primary key *{@literal /}
 *          private Integer id;
 *
 *          /** name of the book *{@literal /}
 *          private String name;
 *
 *          /** when the record is created *{@literal /}
 *          private LocalDateTime createTime;
 *
 *          /** who created this record *{@literal /}
 *          private String createBy;
 *
 *          /** when the record is updated *{@literal /}
 *          private LocalDateTime updateTime;
 *
 *          /** who updated this record *{@literal /}
 *          private String updateBy;
 *
 *          /** 0-normal, 1-deleted *{@literal /}
 *          private Integer isDel;
 *
 *          // ... and some getter, setter
 *
 *     }
 * </pre>
 *
 * @author yongj.zhuang
 */
public class SQLEntityGenerator {

    /** some of the keywords (lowercase) that we care, may not contain all of them */
    private static final Set<String> keywords = new HashSet<>(Arrays.asList("unsigned"));
    private static final List<String> types = Arrays.asList("varchar", "int", "tinyint", "short", "decimal", "datetime", "timestamp", "bigint");
    private static final String CREATE = "create";
    private static final String COMMENT = "comment";
    private static final String CONSTRAINT = "constraint";

    public static void main(String[] args) throws IOException {

        if (args.length < 1 || args[0].equals("--help") || args[0].equals("-help")) {
            printHelp();
            return;
        }

        final String path = args[0];
        if (path.trim().isEmpty()) {
            System.out.println("Illegal file path, please try again.");
            return;
        }

        final File f = Paths.get(path).toFile();
        if (!f.exists()) {
            System.out.printf("File '%s' not found", path);
            return;
        }
        System.out.printf("Parsing file: '%s'\n", f.getAbsolutePath());

        // read ddl scripts
        final List<String> lines = read(f)
                .stream()
                .filter(l -> !l.trim().isEmpty())
                .collect(Collectors.toList());

        // parse ddl
        final SQLTable table = parse(lines);

        // mybatis-plus feature enabled
        boolean mybatisPlusFeatureEnabled = Arrays.stream(args).anyMatch(ar -> ar.equals("--mybatisplus"));

        // generate java object
        generateJavaClass(table, mybatisPlusFeatureEnabled);
    }

    private static void generateJavaClass(SQLTable table, boolean mybatisPlusFeatureEnabled) throws IOException {
        final String tableCamelCase = toCamelCases(table.tableName);
        final String className = toFirstUppercase(tableCamelCase);
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

            // for mybatis-plus only
            if (mybatisPlusFeatureEnabled) {
                bw.write("import com.baomidou.mybatisplus.annotation.IdType;\n");
                bw.write("import com.baomidou.mybatisplus.annotation.TableField;\n");
                bw.write("import com.baomidou.mybatisplus.annotation.TableId;\n\n");
            }

            // class
            bw.write("/** " + table.tableComment + " */\n");

            // for mybatis-plus only
            if (mybatisPlusFeatureEnabled)
                bw.write(String.format("@TableName(value = \"%s\")\n", table.tableName));

            bw.write("public class " + className + " {\n\n");

            // fields
            for (SQLField field : table.fields) {
                bw.write("    /** " + field.comment + " */\n");

                // for mybatis-plus only
                if (mybatisPlusFeatureEnabled) {
                    if (field.sqlFieldName.equalsIgnoreCase("id"))
                        bw.write("    @TableId(type = IdType.AUTO)\n");
                    else
                        bw.write(String.format("    @TableField(\"%s\")\n", field.sqlFieldName));
                }
                bw.write("    private " + field.javaType + " " + field.javaFieldName + ";\n\n");
            }

            // getter & setter
            for (SQLField field : table.fields) {

                final String us = toFirstUppercase(field.javaFieldName);

                bw.write(String.format("    public %s get%s() {\n", field.javaType, us));
                bw.write(String.format("        return this.%s;\n", field.javaFieldName));
                bw.write("    }\n\n");

                bw.write(String.format("    public void set%s(%s %s) {\n", us, field.javaType, field.javaFieldName));
                bw.write(String.format("        this.%s = %s;\n", field.javaFieldName, field.javaFieldName));
                bw.write("    }\n\n");
            }

            // end
            bw.write("}\n");
        }

        System.out.printf("Java class file generated: %s\n", p.toAbsolutePath());
    }

    private static String toJavaType(Set<String> keywords, String sqlType) {

        if (sqlType.equalsIgnoreCase("varchar"))
            return "String";

        if (sqlType.equalsIgnoreCase("datetime")
                || sqlType.equalsIgnoreCase("timestamp"))
            return "LocalDateTime";

        if (sqlType.equalsIgnoreCase("int")) {
            if (keywords.contains("unsigned"))
                return "Long";

            return "Integer";
        }

        if (sqlType.equalsIgnoreCase("tinyint")
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
            if (trimed.isEmpty())
                continue;

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
        sqlTable.log();
        return sqlTable;
    }

    private static SQLField parseField(String[] tokens, int lineNo) {
        // the first one is the field name
        final String fieldName = tokens[0];
        if (types.contains(fieldName)) {
            throw new IllegalArgumentException(String.format("Failed to parse DDL, field name %s can't be a keyword, illegal syntax at line %d", fieldName, lineNo));
        }

        String type = null;
        Set<String> kw = new HashSet<>();

        // we look for data type, as well as other keywords, e.g., unsigned
        for (int i = 1; i < tokens.length; i++) {
            for (String t : types) {
                if (type == null && tokens[i].toLowerCase().startsWith(t)) {
                    type = t;
                }
            }

            // keywords
            final String lowerCaseToken = tokens[i].toLowerCase();
            if (keywords.contains(lowerCaseToken))
                kw.add(lowerCaseToken);
        }

        if (type == null)
            throw new IllegalArgumentException(String.format("Failed to parse DDL, unable to identify data type for field '%s', illegal syntax at line %d", fieldName, lineNo));

        final SQLField field = new SQLField(fieldName, kw, type, extractComment(tokens, lineNo));
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

        final String joined = String.join(" ", Arrays.copyOfRange(tokens, l, h + 1));

        // ( ", or "; or " ) we only want the part before {@code pre}
        return joined.substring(1, joined.lastIndexOf(pre));
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

    private static void printHelp() {
        System.out.println("\n  SQLEntityGenerator by yongj.zhuang\n");
        System.out.println("  Help:\n");
        System.out.println("    arg[0] - Path to the SQL DDL file");
        System.out.println("    arg[1] - (Optional) '--mybatisplus' to enable mybatis-plus feature, e.g., @TableField, @TableName, etc\n");
        System.out.println("  For exmaple:\n");
        System.out.println("    java SQLEntityGenerator book.sql --mybatisplus\n");
        System.out.println("    java SQLEntityGenerator book.sql\n\n");
        System.out.println("  This tool parse a SQL DDL script file, and then generate a ");
        System.out.println("  simple Java Class for this 'table'. The SQL file should ");
        System.out.println("  only contain one 'CREATE TABLE' statement.\n");
        System.out.println("  Each line should only contain key words for a single field,");
        System.out.println("  so don't put everything in one line.\n");
        System.out.println("  For example:\n");
        System.out.println("  CREATE TABLE IF NOT EXISTS book (");
        System.out.println("    id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT COMMENT \"primary key\",");
        System.out.println("    name VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'name of the book',");
        System.out.println("    create_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is created',");
        System.out.println("    create_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who created this record',");
        System.out.println("    update_time DATETIME NOT NULL DEFAULT NOW() COMMENT 'when the record is updated',");
        System.out.println("    update_by VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'who updated this record',");
        System.out.println("    is_del TINYINT NOT NULL DEFAULT '0' COMMENT '0-normal, 1-deleted'");
        System.out.println(" ) ENGINE=InnoDB COMMENT 'Some nice books';\n\n");
    }

    private static String toFirstUppercase(String str) {
        return str.substring(0, 1).toUpperCase() + str.substring(1, str.length());
    }

    private static class SQLField {
        private final String sqlFieldName;
        private final String sqlType;
        private final String comment;
        private final String javaType;
        private final String javaFieldName;

        public SQLField(String sqlFieldName, Set<String> keywords, String sqlType, String comment) {
            this.sqlFieldName = sqlFieldName;
            this.sqlType = sqlType;
            this.comment = comment;
            this.javaType = toJavaType(keywords, sqlType);
            this.javaFieldName = toCamelCases(sqlFieldName);
        }

        public void log(){
            System.out.printf("Field: '%s' ('%s'), type: '%s' ('%s'), comment: '%s'\n", sqlFieldName, javaFieldName, sqlType, javaType, comment);
        }
    }

    private static class SQLTable {
        private List<SQLField> fields;
        private String tableName;
        private String tableComment;

        public void log() {
            System.out.printf("Table: '%s', comment: '%s'\n", tableName, tableComment);
            fields.forEach(SQLField::log);
        }
    }

}