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
public class SqlDmlGenerator {

    private static final ObjectMapper om = new ObjectMapper();

    private static final String PREFIX = "(";
    private static final String SUFFIX = ")";
    private static final String DELIMITER = ",";
    private static final String STATEMENT_END = ";";

    private final String dbName;
    private final String tableName;
    private final String fields;
    private final List<Map<String, String>> params = new ArrayList<>();
    private Map<String, String> defaultParam = new HashMap<>();

    /**
     * Construct a SqlDmlGenerator
     *
     * @param fields list of fields delimited by comma
     */
    public SqlDmlGenerator(String fields, String dbName, String tableName) {
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
    public SqlDmlGenerator(String fields, String tableName) {
        Objects.nonNull(fields);
        this.fields = fields;
        this.dbName = null;
        this.tableName = tableName;
    }

    /**
     * Set parameters
     *
     * @param params parameters (each represent a row)
     */
    public SqlDmlGenerator withMapParams(List<Map<String, String>> params) {
        Objects.nonNull(params);
        this.params.addAll(params);
        return this;
    }

    /**
     * Default parameters
     */
    public SqlDmlGenerator withMapDefaultParam(Map<String, String> defaultParam) {
        this.defaultParam.putAll(defaultParam);
        return this;
    }

    /**
     * Default parameters
     */
    public SqlDmlGenerator withJsonDefaultParam(String json) {
        this.defaultParam.putAll(readAsMap(json));
        return this;
    }

    /**
     * Set parameters
     *
     * @param jsonArray array of json object (each represent a row)
     */
    public SqlDmlGenerator withJsonArrayParams(String jsonArray) {
        Objects.nonNull(jsonArray);

        this.params.addAll(readAsListOfMap(jsonArray));
        return this;
    }

    /**
     * Set parameters
     *
     * @param jsons list of json object (each represent a row)
     */
    public SqlDmlGenerator withJsonParams(List<String> jsons) {
        Objects.nonNull(jsons);
        this.params.addAll(jsons.stream()
                .map(SqlDmlGenerator::readAsMap)
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

            sb.append(line);
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

}
