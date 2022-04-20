package com.curtisnewbie.generator.sql;

/**
 * @author yongj.zhuang
 */
public class JsonBasedCmd {

    private String fields;

    private String dbName;

    private String tableName;

    private String defaultParams;

    private String tabDelimitedParam;

    public String getFields() {
        return fields;
    }

    public JsonBasedCmd setFields(String fields) {
        this.fields = fields;
        return this;
    }

    public String getDbName() {
        return dbName;
    }

    public JsonBasedCmd setDbName(String dbName) {
        this.dbName = dbName;
        return this;
    }

    public String getTableName() {
        return tableName;
    }

    public JsonBasedCmd setTableName(String tableName) {
        this.tableName = tableName;
        return this;
    }

    public String getDefaultParams() {
        return defaultParams;
    }

    public JsonBasedCmd setDefaultParams(String defaultParams) {
        this.defaultParams = defaultParams;
        return this;
    }

    public String getTabDelimitedParam() {
        return tabDelimitedParam;
    }

    public JsonBasedCmd setTabDelimitedParam(String tabDelimitedParam) {
        this.tabDelimitedParam = tabDelimitedParam;
        return this;
    }
}
