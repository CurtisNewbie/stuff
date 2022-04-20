package com.curtisnewbie.generator.sql;

import org.junit.jupiter.api.*;

/**
 * @author yongj.zhuang
 */
public class SqlInsertDmlGeneratorTest {

    public static final String fields = "";
    public static final String dbName = "";
    public static final String tableName = "";
    public static final String jsonDefaultParam = "";
    public static final String tabDelimitedParams = "";

    @Test
    public void generate_insert_template_sql() {
        /*
        {
            "fields" : "",
            "dbName" : "",
            "tableName" : "",
            "defaultParams" : "" ,
            "tabDelimitedParam: ""
        }
         */
        final String insertSql = new SqlInsertDmlGenerator(fields, dbName, tableName)
                .withJsonDefaultParam(jsonDefaultParam)
                .withTabDelimitedParams(tabDelimitedParams, true)
                .generateInsertSql();

        System.out.println(insertSql);
    }

}
