package com.curtisnewbie.generator.sql;

import java.util.*;

/**
 * @author yongj.zhuang
 */
public class JsonBasedCmd {

    private String fields;

    private String dbName;

    private String tableName;

    private Map<String, String> defaultParams;

    private String csvFilePath;

    private String excludedCsvFields;

    public String getFields() {
        return fields;
    }

    public void setFields(String fields) {
        this.fields = fields;
    }

    public String getDbName() {
        return dbName;
    }

    public void setDbName(String dbName) {
        this.dbName = dbName;
    }

    public String getTableName() {
        return tableName;
    }

    public void setTableName(String tableName) {
        this.tableName = tableName;
    }

    public Map<String, String> getDefaultParams() {
        return defaultParams;
    }

    public void setDefaultParams(Map<String, String> defaultParams) {
        this.defaultParams = defaultParams;
    }

    public String getCsvFilePath() {
        return csvFilePath;
    }

    public void setCsvFilePath(String csvFilePath) {
        this.csvFilePath = csvFilePath;
    }

    public String getExcludedCsvFields() {
        return excludedCsvFields;
    }

    public void setExcludedCsvFields(String excludedCsvFields) {
        this.excludedCsvFields = excludedCsvFields;
    }
}
