package com.curtisnewbie.generator.sql;

import com.fasterxml.jackson.core.type.*;
import com.fasterxml.jackson.databind.*;
import org.apache.commons.text.*;

import java.io.*;
import java.util.*;
import java.util.stream.*;

/**
 * @author yongj.zhuang
 */
public class SqlInsertDmlGenerator {

    private static final ObjectMapper om = new ObjectMapper();

    private static final String PREFIX = "(";
    private static final String SUFFIX = ")";
    private static final String DELIMITER = ",";
    private static final String STATEMENT_END = ";";

    private final String dbName;
    private final String tableName;
    private final String fields;
    private final List<Map<String, String>> params = new ArrayList<>();
    private final Map<String, String> defaultParam = new HashMap<>();

    /**
     * Construct a SqlDmlGenerator
     *
     * @param fields list of fields delimited by comma
     */
    public SqlInsertDmlGenerator(String fields, String dbName, String tableName) {
        Objects.nonNull(fields);
        this.fields = fields;
        this.dbName = dbName;
        this.tableName = tableName;
    }

    /**
     * Construct a SqlDmlGenerator
     *
     * @param fields list of fields delimited by comma
     */
    public SqlInsertDmlGenerator(String fields, String tableName) {
        Objects.nonNull(fields);
        this.fields = fields;
        this.dbName = null;
        this.tableName = tableName;
    }

    /**
     * Set parameters
     *
     * @param rows        parameters (each represent a row)
     * @param isAllQuoted whether all values are quoted
     */
    public SqlInsertDmlGenerator withMapParams(List<Map<String, String>> rows, final boolean isAllQuoted) {
        Objects.nonNull(rows);
        this.params.addAll(paramMapsPostProcessing(rows, isAllQuoted));
        return this;
    }

    /**
     * Set parameters
     *
     * @param row         map represents a single row
     * @param isAllQuoted whether all values are quoted
     */
    public SqlInsertDmlGenerator withMapParam(Map<String, String> row, final boolean isAllQuoted) {
        Objects.nonNull(row);
        this.params.add(paramMapPostProcessing(row, isAllQuoted));
        return this;
    }

    /**
     * Default parameters
     */
    public SqlInsertDmlGenerator withMapDefaultParam(Map<String, String> defaultParam) {
        return withMapDefaultParam(defaultParam, false);
    }

    /**
     * Default parameters
     *
     * @param isAllQuoted whether all values are quoted
     */
    public SqlInsertDmlGenerator withMapDefaultParam(Map<String, String> defaultParam, final boolean isAllQuoted) {
        this.defaultParam.putAll(paramMapPostProcessing(defaultParam, isAllQuoted));
        return this;
    }

    /**
     * Default parameters
     */
    public SqlInsertDmlGenerator withJsonDefaultParam(String json) {
        return withJsonDefaultParam(json, false);
    }

    /**
     * Default parameters
     *
     * @param isAllQuoted whether all values are quoted
     */
    public SqlInsertDmlGenerator withJsonDefaultParam(String json, final boolean isAllQuoted) {
        this.defaultParam.putAll(paramMapPostProcessing(readAsMap(json), isAllQuoted));
        return this;
    }

    /**
     * Set parameters
     *
     * @param jsonArray   array of json object (each represent a row)
     * @param isAllQuoted whether all values are quoted
     */
    public SqlInsertDmlGenerator withJsonArrayParams(final String jsonArray, final boolean isAllQuoted) {
        Objects.nonNull(jsonArray);

        this.params.addAll(paramMapsPostProcessing(readAsListOfMap(jsonArray), isAllQuoted));
        return this;
    }

    /**
     * Set parameters
     *
     * @param jsonArray array of json object (each represent a row)
     */
    public SqlInsertDmlGenerator withJsonArrayParams(String jsonArray) {
        return withJsonArrayParams(jsonArray, false);
    }

    /**
     * Set parameters
     *
     * @param csv         csv file content (each line represent a row)
     * @param isAllQuoted whether all values are quoted
     */
    public SqlInsertDmlGenerator withCsvParam(final String csv, final boolean isAllQuoted) {
        final String[] lines = csv.split("\n");
        final String[] titles = lines[0].split(",");
        final int tlen = titles.length;

        for (int i = 1; i < lines.length; i++) {
            final String[] columns = lines[i].split(",");
            final int clen = columns.length;
            final ChainedMap chainedMap = new ChainedMap();
            for (int j = 0; j < tlen; j++) {
                if (titles[j].trim().isEmpty())
                    continue;

                if (j >= clen)
                    chainedMap.thenPut(titles[j], "");
                else
                    chainedMap.thenPut(titles[j], columns[j]);
            }
            withMapParam(chainedMap.get(), isAllQuoted);
        }
        return this;
    }

    /**
     * Set parameters
     *
     * @param tabDelimitedParams tab delimited data (each line represent a row)
     * @param isAllQuoted        whether all values are quoted
     */
    public SqlInsertDmlGenerator withTabDelimitedParams(final String tabDelimitedParams, final boolean isAllQuoted) {
        final String[] lines = tabDelimitedParams.split("\n");
        final String[] titles = lines[0].split("\\t");
        final int tlen = titles.length;

        for (int i = 1; i < lines.length; i++) {
            final String[] columns = lines[i].split("\\t");
            final int clen = columns.length;
            final ChainedMap chainedMap = new ChainedMap();
            for (int j = 0; j < tlen; j++) {
                if (j >= clen)
                    chainedMap.thenPut(titles[j], "");
                else
                    chainedMap.thenPut(titles[j], columns[j]);
            }
            withMapParam(chainedMap.get(), isAllQuoted);
        }
        return this;
    }

    /**
     * Set parameters
     *
     * @param tabDelimitedParams tab delimited data (each line represent a row)
     */
    public SqlInsertDmlGenerator withTabDelimitedParams(final String tabDelimitedParams) {
        return withTabDelimitedParams(tabDelimitedParams, false);
    }

    /**
     * Set parameters
     *
     * @param jsonObjects list of json object (each represent a row)
     */
    public SqlInsertDmlGenerator withJsonParams(List<String> jsonObjects) {
        Objects.nonNull(jsonObjects);
        this.params.addAll(jsonObjects.stream()
                .map(SqlInsertDmlGenerator::readAsMap)
                .collect(Collectors.toList()));
        return this;
    }

    /**
     * Generate (batch) insert SQL
     */
    public String generateInsertSql() {
        final String dbNTable = dbName != null ? dbName + "." + tableName : tableName;
        StringBuilder sb = new StringBuilder(String.format("INSERT INTO %s (%s) VALUES \n", dbNTable, fields));

        final String template = genStrInterpolationTemplate(fields);
        for (int i = 0; i < params.size(); i++) {
            Map<String, String> m = new HashMap<>(defaultParam);
            m.putAll(params.get(i));
            final StrSubstitutor sub = new StrSubstitutor(m);
            String line = PREFIX + sub.replace(template) + SUFFIX;
            if (i < params.size() - 1)
                line += DELIMITER;
            else
                line += STATEMENT_END;

            sb.append(line).append("\n");
        }

        return sb.toString();
    }

    // ---------------------------------------------- helper methods -----------------------------------------

    private static Map<String, String> readAsMap(String json) {
        try {
            return om.readValue(json, new TypeReference<Map<String, String>>() {
            });
        } catch (IOException e) {
            throw new IllegalArgumentException(e);
        }
    }

    private static List<Map<String, String>> readAsListOfMap(String jsonArray) {
        try {
            return om.readValue(jsonArray, new TypeReference<List<Map<String, String>>>() {
            });
        } catch (IOException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Generate a string interpolation template
     * <p>
     * Parse a list of fields delimited by ',' e.g., 'fieldA,fieldB,fieldC' into a string interpolation template: '${fieldA},${fieldB},${fieldC}'
     * </p>
     */
    private static String genStrInterpolationTemplate(final String fields) {
        final String[] fieldsArr = fields.split(",");
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < fieldsArr.length; i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append("${").append(fieldsArr[i].trim()).append("}");
        }
        return sb.toString();
    }

    private static Map<String, String> paramMapPostProcessing(Map<String, String> m, boolean isAllQuoted) {
        if (isAllQuoted) {
            m.forEach((k, v) -> m.put(k, quote(v)));
        }
        return m;
    }

    private static List<Map<String, String>> paramMapsPostProcessing(List<Map<String, String>> l, boolean isAllQuoted) {
        l.forEach(m -> paramMapPostProcessing(m, isAllQuoted));
        return l;
    }

    private static final String quote(String v) {
        return "'" + v + "'";
    }

}
