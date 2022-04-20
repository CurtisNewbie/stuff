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

    private String tabDelimitedParamPath;

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

    public Map<String, String> getDefaultParams() {
        return defaultParams;
    }

    public JsonBasedCmd setDefaultParams(Map<String, String> defaultParams) {
        this.defaultParams = defaultParams;
        return this;
    }

    public String getTabDelimitedParamPath() {
        return tabDelimitedParamPath;
    }

    public JsonBasedCmd setTabDelimitedParamPath(String tabDelimitedParamPath) {
        this.tabDelimitedParamPath = tabDelimitedParamPath;
        return this;
    }
}
