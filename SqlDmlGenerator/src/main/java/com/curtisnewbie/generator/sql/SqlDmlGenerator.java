package com.curtisnewbie.generator.sql;

import org.apache.commons.text.*;

import java.util.*;

/**
 * @author yongj.zhuang
 */
public class SqlDmlGenerator {

    private static final String pre = "(";
    private static final String after = ")";
    private static final String delimiter = ",";
    private static final String last = ";";

    private final String insertIntoValues;
    private final List<Map<String, String>> params;

    public SqlDmlGenerator(String insertIntoValues, List<Map<String, String>> params) {
        this.insertIntoValues = insertIntoValues;
        this.params = params != null ? params : new ArrayList<>();
    }

    public void generateInsertSql() {
        System.out.println(insertIntoValues);
        final String template = parseTemplate(insertIntoValues);
        for (int i = 0; i < params.size(); i++) {
            final StrSubstitutor sub = new StrSubstitutor(params.get(i));
            String line = pre + sub.replace(template) + after;
            if (i < params.size() - 1)
                line += delimiter;
            else
                line += last;
            System.out.println(line);
        }
    }

    private String parseTemplate(String insertInto) {
        int l, h;
        l = insertInto.indexOf("(");
        h = insertInto.lastIndexOf(")");
        final String[] fields = insertInto.substring(l + 1, h).split(",");
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < fields.length; i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append("${").append(fields[i].trim()).append("}");
        }
        return sb.toString();
    }

}
